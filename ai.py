"""peforth - AI Extension Module (v2.1.0)

Implements:
- Security Guard Decorator for vm.call (Task-level approval scope)
- Tools: peforth_search_words, peforth_run_forth
- (ai) cooperative turn generator with OpenAI-compatible SSE streaming
"""

import _thread
import atexit
import contextlib
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import platform
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from projectk import KernelError
from session_store import (
    SCHEMA_VERSION,
    SessionStore,
    build_session_description,
    extract_first_sentence,
    extract_first_user_message_text,
    extract_item_text,
    format_description_time,
    is_complete_description,
)


_OUTPUT_LIMIT = 64 * 1024

_ANSI_RESET = "\x1b[0m"
_ANSI_GREEN_BOLD = "\x1b[1;38;2;135;215;135m"
_ANSI_GREEN = "\x1b[38;2;135;215;135m"
_ANSI_DEEP_GREEN = "\x1b[38;2;0;100;0m"
_ANSI_DIM = "\x1b[2;37m"


class TaskInterruptMonitor:
    """Monitor keyboard input during task execution so pressing standalone Esc interrupts the task."""

    def __init__(self, vm=None, *, interrupt_callback=None):
        self.vm = vm
        self._interrupt_callback = interrupt_callback or _thread.interrupt_main
        self._stop_event = threading.Event()
        self._thread = None

    def _trigger_interrupt(self):
        if self.vm is not None and hasattr(self.vm, "host"):
            self.vm.host["esc_interrupted"] = True
        self._interrupt_callback()

    def _in_interactive_prompt(self) -> bool:
        if self.vm is not None and hasattr(self.vm, "host"):
            return bool(self.vm.host.get("in_approval"))
        return False

    def process_key_stream(self, kbhit_fn, getch_fn, wait_fn=None) -> bool:
        """Inspect buffered console keys; return True and trigger interrupt if standalone Esc is pressed."""
        wait = wait_fn or self._stop_event.wait
        if not kbhit_fn():
            return False
        ch = getch_fn()
        if ch in ("\x00", "\xe0", b"\x00", b"\xe0"):
            if kbhit_fn():
                getch_fn()
            return False
        if ch in ("\x1b", b"\x1b"):
            wait(0.02)
            if kbhit_fn():
                while kbhit_fn():
                    getch_fn()
                return False
            self._trigger_interrupt()
            return True
        if ch in ("\x03", b"\x03"):
            self._trigger_interrupt()
            return True
        return False

    def _watch_windows(self):
        try:
            import msvcrt
        except ImportError:
            return
        while not self._stop_event.is_set():
            if self._in_interactive_prompt():
                self._stop_event.wait(0.025)
                continue
            try:
                if self.process_key_stream(msvcrt.kbhit, msvcrt.getwch):
                    break
            except Exception:
                break
            self._stop_event.wait(0.025)

    def _watch_posix(self):
        try:
            import select
            import termios
            import tty
            fd = sys.stdin.fileno()
            orig_attrs = termios.tcgetattr(fd)
        except Exception:
            return

        cbreak_active = False

        def _enable_cbreak():
            nonlocal cbreak_active
            if not cbreak_active:
                try:
                    tty.setcbreak(fd, termios.TCSANOW)
                    cbreak_active = True
                except Exception:
                    pass

        def _restore_attrs():
            nonlocal cbreak_active
            if cbreak_active:
                try:
                    termios.tcsetattr(fd, termios.TCSANOW, orig_attrs)
                except Exception:
                    pass
                cbreak_active = False

        def _kbhit():
            r, _, _ = select.select([fd], [], [], 0)
            return bool(r)

        def _getch():
            return os.read(fd, 1)

        try:
            _enable_cbreak()
            while not self._stop_event.is_set():
                if self._in_interactive_prompt():
                    _restore_attrs()
                    self._stop_event.wait(0.025)
                    continue
                _enable_cbreak()
                try:
                    if self.process_key_stream(_kbhit, _getch):
                        break
                except Exception:
                    break
                self._stop_event.wait(0.025)
        finally:
            _restore_attrs()

    def __enter__(self):
        if self.vm is not None and hasattr(self.vm, "host"):
            self.vm.host.pop("esc_interrupted", None)
        if sys.stdin is not None and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
            target = self._watch_windows if os.name == "nt" else self._watch_posix
            self._thread = threading.Thread(target=target, name="peforth-esc-monitor", daemon=True)
            self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=0.1)
        return False


def _urlopen_interruptible(req, timeout=60):
    """Open URL with 50ms main-thread signal checks on interactive TTY so Esc / Ctrl+C wake immediately."""
    if not (sys.stdin is not None and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        return urllib.request.urlopen(req, timeout=timeout)
    result = []
    error = []
    done = threading.Event()

    def _worker():
        try:
            result.append(urllib.request.urlopen(req, timeout=timeout))
        except BaseException as exc:
            error.append(exc)
        finally:
            done.set()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    try:
        while not done.wait(timeout=0.05):
            pass
    except BaseException:
        if result:
            try:
                result[0].close()
            except Exception:
                pass
        raise
    if error:
        raise error[0]
    return result[0]


def _iter_response_lines(response):
    """Iterate over response lines while allowing KeyboardInterrupt / Esc to wake within 50ms on Windows."""
    if not (sys.stdin is not None and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()) or isinstance(response, (list, tuple)):
        for line in response:
            yield line
        return
    q = queue.Queue()
    _EOF = object()

    def _reader():
        try:
            for line in response:
                q.put((True, line))
        except BaseException as exc:
            q.put((False, exc))
        finally:
            q.put((True, _EOF))

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    try:
        while True:
            try:
                ok, item = q.get(timeout=0.05)
            except queue.Empty:
                continue
            if not ok:
                raise item
            if item is _EOF:
                break
            yield item
    finally:
        try:
            response.close()
        except Exception:
            pass


def _clip(value, limit=_OUTPUT_LIMIT):
    value = value or ""
    return value[:limit], len(value) > limit


def _run_process(argv, input_text=None, timeout=60):
    try:
        if not (sys.stdin is not None and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
            completed = subprocess.run(
                argv,
                input=input_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
        else:
            proc = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            out_box = []
            err_box = []
            done = threading.Event()

            def _comm():
                try:
                    out_box.append(proc.communicate(input=input_text))
                except BaseException as e:
                    err_box.append(e)
                finally:
                    done.set()

            t = threading.Thread(target=_comm, daemon=True)
            t.start()
            deadline = time.monotonic() + timeout if timeout else None
            try:
                while not done.wait(timeout=0.05):
                    if deadline is not None and time.monotonic() >= deadline:
                        proc.kill()
                        done.wait(timeout=1.0)
                        stdout_raw, stderr_raw = out_box[0] if out_box else ("", "")
                        raise subprocess.TimeoutExpired(argv, timeout, output=stdout_raw, stderr=stderr_raw)
            except BaseException:
                try:
                    if proc.poll() is None:
                        proc.kill()
                except Exception:
                    pass
                raise
            if err_box:
                raise err_box[0]
            stdout_str, stderr_str = out_box[0]
            completed = subprocess.CompletedProcess(argv, proc.returncode, stdout_str, stderr_str)
    except subprocess.TimeoutExpired as exc:
        stdout_raw = exc.stdout or ""
        stderr_raw = exc.stderr or ""
        stdout, out_trunc = _clip(stdout_raw)
        stderr, err_trunc = _clip(stderr_raw)
        return {
            "exit_code": None,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": True,
            "truncated": out_trunc or err_trunc,
            "error": f"Process exceeded the {timeout}-second time limit.",
        }
    except OSError as exc:
        return {
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "timed_out": False,
            "truncated": False,
            "error": str(exc),
        }

    stdout, out_trunc = _clip(completed.stdout)
    stderr, err_trunc = _clip(completed.stderr)
    return {
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": False,
        "truncated": out_trunc or err_trunc,
    }


def _http_result(status, headers, response_or_body):
    if hasattr(response_or_body, "read"):
        raw = response_or_body.read()
    else:
        raw = response_or_body or b""
    if isinstance(raw, str):
        body, truncated = _clip(raw)
    else:
        body, truncated = _clip(raw.decode("utf-8", errors="replace"))
    header_dict = dict(headers.items()) if hasattr(headers, "items") else dict(headers or {})
    return {
        "status_code": status,
        "headers": header_dict,
        "body": body,
        "truncated": truncated,
    }


def _http_request(url, method="GET", headers=None, body=None, timeout=30):
    data = body.encode("utf-8") if isinstance(body, str) else body
    req_headers = dict(headers or {})
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method.upper())
    try:
        with _urlopen_interruptible(req, timeout=timeout) as resp:
            return _http_result(resp.status, resp.headers, resp)
    except urllib.error.HTTPError as exc:
        try:
            return _http_result(exc.code, exc.headers, exc)
        finally:
            exc.close()
    except Exception as exc:
        return {"error": str(exc)}


_SCREENSHOT_MAX_BYTES = 750_000
_SCREENSHOT_MAX_DIMENSION = 1920
_IMAGE_DATA_URI_MAX_LEN = 1_048_576


def _powershell_executable(vm=None):
    if os.name == "nt":
        if vm is not None:
            info = vm.host.get("system_info")
            if isinstance(info, dict):
                pwsh = (info.get("shells") or {}).get("pwsh") or {}
                if pwsh.get("available") and pwsh.get("path"):
                    return str(pwsh["path"])
        for candidate in ("pwsh", "powershell", "pwsh.exe", "powershell.exe"):
            found = shutil.which(candidate)
            if found:
                return found
        raise RuntimeError("PowerShell is not available for Windows desktop capture.")
    else:
        wsl_fallback = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
        if os.path.isfile(wsl_fallback):
            return wsl_fallback
        raise RuntimeError("Windows desktop capture is only supported on Windows or WSL.")


def _windows_to_local_path(win_path):
    if not isinstance(win_path, str) or not win_path:
        return win_path
    if os.name == "nt":
        return win_path
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", win_path)
    if match:
        drive = match.group(1).lower()
        rest = match.group(2).replace("\\", "/")
        return f"/mnt/{drive}/{rest}"
    return win_path


def _local_to_windows_path(local_path):
    if not isinstance(local_path, str) or not local_path or os.name == "nt":
        return local_path
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", local_path)
    if match:
        drive = match.group(1).upper()
        rest = match.group(2).replace("/", "\\")
        return f"{drive}:\\{rest}"
    return local_path


def _run_powershell_encoded(script, vm=None, timeout=60):
    import base64

    executable = _powershell_executable(vm=vm)
    preamble = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"
        "$ErrorActionPreference = 'Stop'\n"
    )
    encoded = base64.b64encode((preamble + script).encode("utf-16le")).decode("ascii")
    result = _run_process(
        [
            executable,
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-OutputFormat",
            "Text",
            "-EncodedCommand",
            encoded,
        ],
        timeout=timeout,
    )
    if result.get("timed_out"):
        raise RuntimeError(result.get("error") or "PowerShell desktop capture timed out.")
    if result.get("error"):
        raise RuntimeError(f"Could not run PowerShell: {result['error']}")
    if result.get("exit_code") != 0:
        detail = result.get("stderr", "").strip() or result.get("stdout", "").strip()
        raise RuntimeError(f"PowerShell capture error ({result.get('exit_code')}): {detail}")
    return result


def capture_desktop(
    region=None,
    max_dimension=_SCREENSHOT_MAX_DIMENSION,
    quality=82,
    max_bytes=_SCREENSHOT_MAX_BYTES,
    vm=None,
):
    """Capture a DPI-aware live Windows desktop screenshot sized for AI inspection."""
    if isinstance(max_dimension, bool) or not isinstance(max_dimension, int) or max_dimension < 64:
        raise ValueError("max_dimension must be an integer >= 64.")
    if isinstance(quality, bool) or not isinstance(quality, int) or not (10 <= quality <= 100):
        raise ValueError("quality must be an integer between 10 and 100.")
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 10_000:
        raise ValueError("max_bytes must be an integer >= 10000.")

    has_region = region is not None
    rx = ry = rw = rh = 0.0
    normalized_region = False
    if has_region:
        if not isinstance(region, (list, tuple)) or len(region) != 4:
            raise ValueError("region must be a 4-item (x, y, width, height) sequence.")
        for item in region:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise ValueError("region coordinates must be numbers.")
        rx, ry, rw, rh = (float(region[0]), float(region[1]), float(region[2]), float(region[3]))
        if rw <= 0 or rh <= 0:
            raise ValueError("region width and height must be positive.")
        if (
            0.0 <= rx <= 1.0
            and 0.0 <= ry <= 1.0
            and 0.0 < rw <= 1.0
            and 0.0 < rh <= 1.0
            and (any(isinstance(v, float) for v in region) or (rw <= 1.0 and rh <= 1.0))
        ):
            normalized_region = True

    script = f"""
Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public static class PeForthDpi {{ [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); }}'
[void][PeForthDpi]::SetProcessDPIAware()
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

try {{
    Get-ChildItem -Path $env:TEMP -Filter 'desktop-live-*' -ErrorAction SilentlyContinue |
        Where-Object {{ $_.LastWriteTimeUtc -lt (Get-Date).ToUniversalTime().AddHours(-1) }} |
        Remove-Item -Force -ErrorAction SilentlyContinue
}} catch {{}}

$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
$hasRegion = {'$true' if has_region else '$false'}
$normalized = {'$true' if normalized_region else '$false'}
if ($hasRegion) {{
    if ($normalized) {{
        $capX = $bounds.Left + [int][Math]::Round({rx!r} * $bounds.Width)
        $capY = $bounds.Top + [int][Math]::Round({ry!r} * $bounds.Height)
        $capW = [Math]::Max(1, [int][Math]::Round({rw!r} * $bounds.Width))
        $capH = [Math]::Max(1, [int][Math]::Round({rh!r} * $bounds.Height))
    }} else {{
        $capX = [int][Math]::Round({rx!r})
        $capY = [int][Math]::Round({ry!r})
        $capW = [Math]::Max(1, [int][Math]::Round({rw!r}))
        $capH = [Math]::Max(1, [int][Math]::Round({rh!r}))
    }}
    $right = [Math]::Min($bounds.Right, $capX + $capW)
    $bottom = [Math]::Min($bounds.Bottom, $capY + $capH)
    $capX = [Math]::Max($bounds.Left, [Math]::Min($capX, $bounds.Right - 1))
    $capY = [Math]::Max($bounds.Top, [Math]::Min($capY, $bounds.Bottom - 1))
    $capW = [Math]::Max(1, $right - $capX)
    $capH = [Math]::Max(1, $bottom - $capY)
}} else {{
    $capX = $bounds.Left
    $capY = $bounds.Top
    $capW = $bounds.Width
    $capH = $bounds.Height
}}

$origBmp = [System.Drawing.Bitmap]::new($capW, $capH)
$g = [System.Drawing.Graphics]::FromImage($origBmp)
try {{
    $sourcePt = [System.Drawing.Point]::new($capX, $capY)
    $g.CopyFromScreen($sourcePt, [System.Drawing.Point]::Empty, [System.Drawing.Size]::new($capW, $capH))

    $maxDim = {int(max_dimension)}
    $maxBytes = {int(max_bytes)}
    $qual = {int(quality)}
    $scale = 1.0
    if ($capW -gt $maxDim -or $capH -gt $maxDim) {{
        $scale = [Math]::Min($maxDim / $capW, $maxDim / $capH)
    }}

    $encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
        Where-Object {{ $_.MimeType -eq 'image/jpeg' }} | Select-Object -First 1

    $jpegBytes = $null
    $tw = [Math]::Max(1, [int][Math]::Round($capW * $scale))
    $th = [Math]::Max(1, [int][Math]::Round($capH * $scale))

    for ($attempt = 0; $attempt -lt 6; $attempt++) {{
        $tw = [Math]::Max(1, [int][Math]::Round($capW * $scale))
        $th = [Math]::Max(1, [int][Math]::Round($capH * $scale))
        $targetBmp = [System.Drawing.Bitmap]::new($tw, $th)
        $tg = [System.Drawing.Graphics]::FromImage($targetBmp)
        $ms = [System.IO.MemoryStream]::new()
        try {{
            $tg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $tg.DrawImage($origBmp, 0, 0, $tw, $th)
            $encParams = [System.Drawing.Imaging.EncoderParameters]::new(1)
            $encParams.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new(
                [System.Drawing.Imaging.Encoder]::Quality, [long]$qual
            )
            $targetBmp.Save($ms, $encoder, $encParams)
            $jpegBytes = $ms.ToArray()
        }} finally {{
            $ms.Dispose()
            $tg.Dispose()
            $targetBmp.Dispose()
        }}
        if ($jpegBytes.Length -le $maxBytes) {{
            break
        }}
        if ($qual -gt 55) {{
            $qual = [Math]::Max(50, $qual - 15)
        }} else {{
            $scale = $scale * 0.75
        }}
    }}

    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $id = [guid]::NewGuid().ToString('N').Substring(0, 8)
    $outPath = Join-Path $env:TEMP ('desktop-live-' + $stamp + '-' + $id + '.jpg')
    [System.IO.File]::WriteAllBytes($outPath, $jpegBytes)
    $info = Get-Item -LiteralPath $outPath
    [PSCustomObject]@{{
        path = $info.FullName
        size = $info.Length
        width = $tw
        height = $th
        orig_width = $capW
        orig_height = $capH
        screen_width = $bounds.Width
        screen_height = $bounds.Height
        region = [PSCustomObject]@{{ x = $capX; y = $capY; width = $capW; height = $capH }}
        captured_at = $info.LastWriteTimeUtc.ToString('o')
    }} | ConvertTo-Json -Compress
}} finally {{
    $g.Dispose()
    $origBmp.Dispose()
}}
"""
    try:
        result = _run_powershell_encoded(script, vm=vm)
    except RuntimeError as exc:
        msg = str(exc)
        if "CopyFromScreen" in msg and any(indicator in msg for indicator in ("代碼無效", "handle is invalid", "Win32Exception (6)")):
            raise RuntimeError(
                "Windows desktop capture failed: display handle is invalid. "
                "The screen may be locked, asleep, or running without an active rendered desktop session."
            ) from exc
        raise

    lines = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Desktop capture produced no metadata output.")
    try:
        meta = json.loads(lines[-1])
    except ValueError as exc:
        raise RuntimeError(f"Desktop capture returned invalid JSON: {lines[-1]!r}") from exc
    local_path = _windows_to_local_path(meta.get("path", ""))
    if not local_path or not os.path.isfile(local_path) or os.path.getsize(local_path) <= 0:
        raise RuntimeError(f"Captured screenshot file is missing or empty: {local_path!r}")
    meta["path"] = local_path
    return meta


def _compress_image_file_for_ai(
    abs_path,
    max_dimension=_SCREENSHOT_MAX_DIMENSION,
    quality=82,
    max_bytes=_SCREENSHOT_MAX_BYTES,
    vm=None,
):
    """Downscale and JPEG-compress an existing image file so it fits inside max_bytes."""
    import base64

    win_path = _local_to_windows_path(abs_path)
    escaped_path = win_path.replace("'", "''")
    script = f"""
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile('{escaped_path}')
try {{
    $ow = $src.Width
    $oh = $src.Height
    $maxDim = {int(max_dimension)}
    $maxBytes = {int(max_bytes)}
    $qual = {int(quality)}
    $scale = 1.0
    if ($ow -gt $maxDim -or $oh -gt $maxDim) {{
        $scale = [Math]::Min($maxDim / $ow, $maxDim / $oh)
    }}
    $encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
        Where-Object {{ $_.MimeType -eq 'image/jpeg' }} | Select-Object -First 1
    $jpegBytes = $null
    for ($attempt = 0; $attempt -lt 6; $attempt++) {{
        $tw = [Math]::Max(1, [int][Math]::Round($ow * $scale))
        $th = [Math]::Max(1, [int][Math]::Round($oh * $scale))
        $targetBmp = [System.Drawing.Bitmap]::new($tw, $th)
        $tg = [System.Drawing.Graphics]::FromImage($targetBmp)
        $ms = [System.IO.MemoryStream]::new()
        try {{
            $tg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $tg.DrawImage($src, 0, 0, $tw, $th)
            $encParams = [System.Drawing.Imaging.EncoderParameters]::new(1)
            $encParams.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new(
                [System.Drawing.Imaging.Encoder]::Quality, [long]$qual
            )
            $targetBmp.Save($ms, $encoder, $encParams)
            $jpegBytes = $ms.ToArray()
        }} finally {{
            $ms.Dispose()
            $tg.Dispose()
            $targetBmp.Dispose()
        }}
        if ($jpegBytes.Length -le $maxBytes) {{
            break
        }}
        if ($qual -gt 55) {{
            $qual = [Math]::Max(50, $qual - 15)
        }} else {{
            $scale = $scale * 0.75
        }}
    }}
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $id = [guid]::NewGuid().ToString('N').Substring(0, 8)
    $outPath = Join-Path $env:TEMP ('desktop-scaled-' + $stamp + '-' + $id + '.jpg')
    [System.IO.File]::WriteAllBytes($outPath, $jpegBytes)
    Write-Output $outPath
}} finally {{
    $src.Dispose()
}}
"""
    result = _run_powershell_encoded(script, vm=vm)
    lines = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Image compression produced no output path.")
    temp_local_path = _windows_to_local_path(lines[-1])
    try:
        with open(temp_local_path, "rb") as f:
            data = f.read()
    finally:
        try:
            os.remove(temp_local_path)
        except OSError:
            pass
    return "image/jpeg", base64.b64encode(data).decode("ascii")


def encode_image_file_data_uri(file_path, max_data_uri_len=_IMAGE_DATA_URI_MAX_LEN, vm=None):
    """Read a local image file and return a data:image/...;base64,... URI."""
    import base64
    import mimetypes

    if not isinstance(file_path, str) or not file_path.strip():
        raise RuntimeError("ai-image-file expects a valid file path.")
    abs_path = os.path.abspath(os.path.expanduser(file_path.strip()))
    if not os.path.isfile(abs_path):
        raise RuntimeError(f"File not found: {abs_path}")
    mime_type, _ = mimetypes.guess_type(abs_path)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"
    file_size = os.path.getsize(abs_path)
    max_raw_bytes = min(_SCREENSHOT_MAX_BYTES, ((max_data_uri_len - 32) // 4) * 3)
    if file_size <= max_raw_bytes and mime_type in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        with open(abs_path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("ascii")
        data_uri = f"data:{mime_type};base64,{b64_str}"
        if len(data_uri) <= max_data_uri_len:
            return data_uri
    mime_type, b64_str = _compress_image_file_for_ai(abs_path, vm=vm)
    return f"data:{mime_type};base64,{b64_str}"


def _expand_env_vars(value: str) -> str:
    """Expand ~, $VAR, and %VAR% placeholders in path configuration strings."""
    if not value:
        return ""
    expanded = os.path.expanduser(os.path.expandvars(value.strip()))
    return re.sub(
        r"%([^%]+)%",
        lambda match: os.environ.get(match.group(1), match.group(0)),
        expanded,
    )


def _reported_source_path(runtime_path: Path) -> str:
    """Return the source checkout path separately from the active runtime path."""
    configured = os.environ.get("PEFORTH_SOURCE_PATH", "").strip()
    if configured:
        return _expand_env_vars(configured)
    return str(runtime_path)


def _latest_runtime_file_info(runtime_path: Path) -> dict | None:
    """Return the newest .f/.py file under the runtime directory."""
    try:
        root = Path(runtime_path).resolve()
    except OSError:
        return None
    newest = None
    try:
        for candidate in root.rglob("*"):
            if candidate.suffix.casefold() not in {".f", ".py"}:
                continue
            parts = {p.casefold() for p in candidate.parts}
            if ".venv" in parts or "venvs" in parts or "__pycache__" in parts or ".git" in parts:
                continue
            try:
                if not candidate.is_file():
                    continue
                modified = candidate.stat().st_mtime
            except OSError:
                continue
            relative = candidate.relative_to(root).as_posix()
            if (newest is None or modified > newest[0]
                    or (modified == newest[0] and relative < newest[1])):
                newest = (modified, relative)
    except OSError:
        return None
    if newest is None:
        return None
    modified, relative = newest
    return {
        "file": relative,
        "modified": datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S"),
    }


def _safe_home_dir() -> Path:
    try:
        return Path.home()
    except Exception:
        env_home = os.environ.get("USERPROFILE") or os.environ.get("HOME")
        if env_home:
            return Path(env_home)
        return Path(tempfile.gettempdir())


def detect_system_info(vm=None) -> dict:
    load_dotenv()
    is_windows = os.name == "nt"
    is_wsl = bool(os.environ.get("WSL_DISTRO_NAME")) or "microsoft" in platform.release().casefold()
    environment = "wsl" if is_wsl else ("windows" if is_windows else "linux")
    os_name = "Windows" if is_windows else ("WSL" if is_wsl else "Linux")

    # Detect active shell
    if is_wsl:
        active_shell = "bash"
    elif is_windows:
        if "PSModulePath" in os.environ:
            active_shell = "pwsh"
        elif "PROMPT" in os.environ:
            active_shell = "cmd"
        else:
            active_shell = "pwsh"
    else:
        active_shell = os.path.basename(os.environ.get("SHELL", "bash"))

    default_shell = "pwsh" if is_windows else "bash"

    pwsh_candidates = ("pwsh", "powershell", "pwsh.exe", "powershell.exe") if is_windows else ("pwsh", "powershell")
    pwsh_path = os.environ.get("PEFORTH_PWSH_PATH", "").strip()
    if pwsh_path:
        pwsh_path = _expand_env_vars(pwsh_path)
        if not os.path.isfile(pwsh_path):
            pwsh_path = shutil.which(pwsh_path)
    if not pwsh_path:
        for c in pwsh_candidates:
            pwsh_path = shutil.which(c)
            if pwsh_path:
                break

    curl_path = shutil.which("curl.exe" if is_windows else "curl")
    bash_path = shutil.which("bash.exe" if is_windows else "bash")

    wsl_info = {"active": is_wsl, "available": False, "path": None, "distro": None}
    if is_windows:
        wsl_bin = shutil.which("wsl") or shutil.which("wsl.exe")
        if wsl_bin:
            wsl_info["available"] = True
            wsl_info["path"] = wsl_bin
            configured_distro = os.environ.get("PEFORTH_WSL_DISTRO", "").strip()
            try:
                proc = subprocess.run([wsl_bin, "-l", "-q"], capture_output=True, timeout=5)
                raw = proc.stdout
                text = raw.decode("utf-16-le", errors="ignore") if b"\x00" in raw else raw.decode("utf-8", errors="ignore")
                distros = [line.strip() for line in text.splitlines() if line.strip()]
                wsl_info["distros"] = distros
                if configured_distro:
                    wsl_info["distro"] = configured_distro
                elif distros:
                    wsl_info["distro"] = distros[0]
            except Exception:
                wsl_info["distro"] = configured_distro or "Ubuntu"
    elif is_wsl:
        wsl_info["available"] = True
        wsl_info["distro"] = os.environ.get("WSL_DISTRO_NAME") or os.environ.get("PEFORTH_WSL_DISTRO")

    file_dir = vm.host.get("__file__dir__") if (vm is not None and hasattr(vm, "host")) else None
    runtime_dir = Path(file_dir).resolve() if file_dir else Path(__file__).resolve().parent
    runtime_path = str(runtime_dir)
    source_path = _reported_source_path(runtime_dir)

    prefix = os.path.normcase(os.path.abspath(sys.prefix))
    base_prefix = os.path.normcase(os.path.abspath(sys.base_prefix))
    venv_active = prefix != base_prefix

    config_dir_raw = os.environ.get("PEFORTH_CONFIG_DIR", "").strip()
    resolved_config_dir = str(Path(_expand_env_vars(config_dir_raw)).resolve()) if config_dir_raw else str((_safe_home_dir() / ".peforth").resolve())
    skills_dir_raw = (os.environ.get("PEFORTH_SKILLS_DIR", "") or os.environ.get("PEFORTH_AI_SKILLS_DIR", "")).strip()

    config_snapshot = {
        "PEFORTH_SOURCE_PATH": os.environ.get("PEFORTH_SOURCE_PATH", ""),
        "PEFORTH_CONFIG_DIR": config_dir_raw or resolved_config_dir,
        "PEFORTH_SKILLS_DIR": skills_dir_raw or str(get_skills_dir(vm)),
        "PEFORTH_AI_MODEL": os.environ.get("PEFORTH_AI_MODEL", ""),
        "PEFORTH_AI_LOG_MODE": os.environ.get("PEFORTH_AI_LOG_MODE", "normal"),
        "PEFORTH_PWSH_PATH": os.environ.get("PEFORTH_PWSH_PATH", ""),
        "PEFORTH_WSL_DISTRO": os.environ.get("PEFORTH_WSL_DISTRO", ""),
        "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL", ""),
        "OPENAI_MODEL": os.environ.get("OPENAI_MODEL", ""),
        "OPENAI_REASONING_EFFORT": os.environ.get("OPENAI_REASONING_EFFORT", ""),
        "OPENAI_API_KEY_SET": bool(os.environ.get("OPENAI_API_KEY", "").strip()),
        "HERDR_ENV": os.environ.get("HERDR_ENV", ""),
        "HERDR_WORKSPACE_ID": os.environ.get("HERDR_WORKSPACE_ID", ""),
        "HERDR_TAB_ID": os.environ.get("HERDR_TAB_ID", ""),
        "HERDR_PANE_ID": os.environ.get("HERDR_PANE_ID", ""),
        "LINE_USER_ID_SET": bool(os.environ.get("LINE_USER_ID", "").strip()),
        "LINE_CHANNEL_ACCESS_TOKEN_SET": bool(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()),
    }

    return {
        "os": os_name,
        "platform": sys.platform,
        "environment": environment,
        "active_shell": active_shell,
        "default_shell": default_shell,
        "cwd": os.getcwd(),
        "source_path": source_path,
        "runtime_path": runtime_path,
        "runtime_latest": _latest_runtime_file_info(runtime_dir),
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        "venv": {
            "active": venv_active,
            "path": sys.prefix if venv_active else None,
        },
        "shells": {
            "pwsh": {"available": bool(pwsh_path), "path": pwsh_path},
            "curl": {"available": bool(curl_path), "path": curl_path},
            "bash": {"available": bool(bash_path), "path": bash_path},
        },
        "wsl": wsl_info,
        "config": config_snapshot,
    }


def load_dotenv(env_path=None):
    """Load environment variables from .env file using only standard library."""
    if env_path is None:
        candidates = [
            Path.cwd() / ".env",
            Path(__file__).resolve().parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
            _safe_home_dir() / ".peforth" / ".env",
        ]
        for c in candidates:
            if c.exists():
                env_path = c
                break
    if env_path and os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key, val)


DEFAULT_PROVIDERS_CONFIG = {
    "stateful": {
        "provider": "OpenAI",
        "endpoint": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "stateless": {
        "default_profile": "openai-gpt-4o-mini",
        "profiles": {
            "openai-gpt-4o-mini": {
                "provider": "OpenAI",
                "endpoint": "https://api.openai.com/v1",
                "model": "gpt-4o-mini",
                "reasoning": "none",
                "api_key_env": "OPENAI_API_KEY",
                "aliases": ["gpt-4o-mini", "4o-mini", "openai"],
            },
            "openai-o3-mini": {
                "provider": "OpenAI",
                "endpoint": "https://api.openai.com/v1",
                "model": "o3-mini",
                "reasoning": "medium",
                "api_key_env": "OPENAI_API_KEY",
                "aliases": ["o3-mini", "o3"],
            },
            "google-gemini-3.8-flash": {
                "provider": "Google",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "model": "gemini-3.8-flash",
                "reasoning": "Medium",
                "api_key_env": "GEMINI_API_KEY",
                "aliases": ["Gemini 3.8 Flash", "gemini-flash", "gemini", "google"],
            },
            "groq-llama-3.3-70b": {
                "provider": "Groq",
                "endpoint": "https://api.groq.com/openai/v1",
                "model": "llama-3.3-70b-versatile",
                "reasoning": "none",
                "api_key_env": "GROQ_API_KEY",
                "aliases": ["groq", "llama-3.3"],
            },
            "ollama-local": {
                "provider": "Ollama",
                "endpoint": "http://localhost:11434/v1",
                "model": "llama3",
                "reasoning": "none",
                "api_key_env": "OLLAMA_API_KEY",
                "aliases": ["ollama", "local"],
            },
        },
    },
}


def get_providers_yaml_path(vm=None) -> Path | None:
    file_dir = vm.host.get("__file__dir__") if (vm is not None and hasattr(vm, "host")) else None
    candidates = [
        Path.cwd() / "providers.yaml",
        Path.cwd() / "providers.yml",
        Path(file_dir).resolve() / "providers.yaml" if file_dir else None,
        Path(__file__).resolve().parent / "providers.yaml",
        _safe_home_dir() / ".peforth" / "providers.yaml",
        Path.cwd() / "providers.yaml.example",
        Path(file_dir).resolve() / "providers.yaml.example" if file_dir else None,
        Path(__file__).resolve().parent / "providers.yaml.example",
        _safe_home_dir() / ".peforth" / "providers.yaml.example",
    ]
    for c in candidates:
        if c and c.exists():
            return c
    return None


def _parse_simple_yaml(text: str) -> dict:
    """Parse a basic subset of YAML without external dependencies (supporting dicts, inline lists, block lists, strings)."""
    cleaned_lines = []
    for line in text.splitlines():
        s = line.rstrip()
        if not s.strip() or s.strip().startswith("#"):
            continue
        cleaned_lines.append(s)

    root = {}
    stack = [(-1, root)]

    list_item_re = re.compile(r"^(\s*)-\s*(.*)$")
    key_val_re = re.compile(r"^(\s*)([A-Za-z0-9_\-\.]+)\s*:\s*(.*)$")

    def parse_scalar(val: str):
        val = val.strip()
        if not val:
            return None
        if val.startswith("[") and val.endswith("]"):
            try:
                return json.loads(val)
            except Exception:
                inner = val[1:-1].strip()
                if not inner:
                    return []
                parts = [p.strip().strip("'\"") for p in inner.split(",")]
                return [p for p in parts if p]
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            return val[1:-1]
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        if val.lower() in ("null", "none", "~"):
            return None
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    for line in cleaned_lines:
        indent = len(line) - len(line.lstrip(" "))
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        current_parent = stack[-1][1]

        m_list = list_item_re.match(line)
        if m_list:
            item_val = parse_scalar(m_list.group(2))
            if isinstance(current_parent, list):
                current_parent.append(item_val)
            continue

        m_kv = key_val_re.match(line)
        if m_kv:
            key = m_kv.group(2).strip()
            rest = m_kv.group(3).strip()
            if " #" in rest:
                rest = rest.split(" #", 1)[0].strip()

            if not rest:
                new_dict = {}
                if isinstance(current_parent, dict):
                    current_parent[key] = new_dict
                stack.append((indent, new_dict))
            else:
                parsed_val = parse_scalar(rest)
                if isinstance(current_parent, dict):
                    current_parent[key] = parsed_val

    return root


def load_providers_config(vm=None) -> dict:
    load_dotenv()
    config = json.loads(json.dumps(DEFAULT_PROVIDERS_CONFIG))
    yaml_path = get_providers_yaml_path(vm)
    if yaml_path and yaml_path.exists():
        loaded = None
        try:
            import yaml
            with open(yaml_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
        except Exception:
            pass
        if not isinstance(loaded, dict):
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    loaded = _parse_simple_yaml(f.read())
            except Exception:
                pass
        if isinstance(loaded, dict):
            if "stateful" in loaded and isinstance(loaded["stateful"], dict):
                config["stateful"].update(loaded["stateful"])
            if "stateless" in loaded and isinstance(loaded["stateless"], dict):
                st = loaded["stateless"]
                if "default_profile" in st:
                    config["stateless"]["default_profile"] = st["default_profile"]
                if "profiles" in st and isinstance(st["profiles"], dict) and st["profiles"]:
                    config["stateless"]["profiles"] = st["profiles"]
    return config


def get_stateful_config(vm=None) -> dict:
    cfg = load_providers_config(vm)
    return cfg.get("stateful", DEFAULT_PROVIDERS_CONFIG["stateful"])


def list_stateless_profiles(vm=None) -> list[str]:
    cfg = load_providers_config(vm)
    return list(cfg.get("stateless", {}).get("profiles", {}).keys())


def get_active_stateless_profile(vm=None) -> dict:
    if vm is not None and hasattr(vm, "host") and vm.host.get("ai_stateless_profile"):
        return dict(vm.host["ai_stateless_profile"])
    cfg = load_providers_config(vm)
    stateless = cfg.get("stateless", {})
    profiles = stateless.get("profiles", {})
    default_name = stateless.get("default_profile", "openai-gpt-4o-mini")
    profile = profiles.get(default_name)
    if not profile and profiles:
        profile = next(iter(profiles.values()))
    if not profile:
        profile = DEFAULT_PROVIDERS_CONFIG["stateless"]["profiles"]["openai-gpt-4o-mini"]
    profile_copy = dict(profile)
    env_model = os.environ.get("OPENAI_MODEL")
    if env_model:
        profile_copy["model"] = env_model
    if vm is not None and hasattr(vm, "host"):
        vm.host["ai_stateless_profile"] = profile_copy
    return profile_copy


def get_active_provider_info(vm=None) -> dict:
    if vm is not None and hasattr(vm, "host") and vm.host.get("ai_active_session_id"):
        st = get_stateful_config(vm)
        model = vm.host.get("ai_stateful_model") or st.get("model", "gpt-6-luna")
        reasoning = vm.host.get("ai_stateful_reasoning") or st.get("reasoning") or "none"
        return {
            "provider": st.get("provider", "OpenAI"),
            "model": str(model),
            "reasoning": str(reasoning),
        }
    prof = get_active_stateless_profile(vm)
    model = prof.get("model", "gpt-4o-mini")
    reasoning = prof.get("reasoning", os.environ.get("OPENAI_REASONING_EFFORT", "none"))
    return {
        "provider": prof.get("provider", "OpenAI"),
        "model": str(model),
        "reasoning": str(reasoning),
    }


def has_valid_api_key(vm=None) -> bool:
    load_dotenv()
    prof = get_active_stateless_profile(vm)
    api_key_env = prof.get("api_key_env", "OPENAI_API_KEY")
    if api_key_env == "OLLAMA_API_KEY":
        return True
    return bool(os.environ.get(api_key_env, "").strip())


def select_startup_stateless_profile(vm=None) -> tuple[bool, str | None]:
    """Keep the active profile when usable; otherwise select first configured profile with credentials."""
    load_dotenv()
    if has_valid_api_key(vm):
        return True, None

    profiles = load_providers_config(vm).get("stateless", {}).get("profiles", {})
    for name, profile in profiles.items():
        api_key_env = profile.get("api_key_env", "OPENAI_API_KEY")
        if api_key_env == "OLLAMA_API_KEY" or os.environ.get(api_key_env, "").strip():
            ok, _message = apply_stateless_provider(vm, name)
            if ok:
                return True, name
    return False, None


def _normalize_base_endpoint(url: str | None) -> str:
    return (url or "").strip().rstrip("/").lower()


def _is_stateful_compatible_profile(vm, profile: dict | None) -> bool:
    """Return True if profile's provider and endpoint match the configured Stateful endpoint."""
    if not isinstance(profile, dict):
        return False
    st_cfg = get_stateful_config(vm)
    st_provider = (st_cfg.get("provider") or "OpenAI").strip().lower()
    st_endpoint = _normalize_base_endpoint(st_cfg.get("endpoint") or "https://api.openai.com/v1")
    prof_provider = (profile.get("provider") or "").strip().lower()
    prof_endpoint = _normalize_base_endpoint(profile.get("endpoint") or "https://api.openai.com/v1")
    return prof_provider == st_provider and prof_endpoint == st_endpoint


def _update_stateful_session_model(vm, session_id: str, model: str, reasoning: str = None) -> tuple[bool, str]:
    """Update the active Stateful remote session's model/reasoning in-place via POST /sessions/{id}."""
    st_cfg = get_stateful_config(vm)
    st_provider = st_cfg.get("provider", "OpenAI")
    agent_patch = {"model": model}
    norm_reasoning = None
    if reasoning is not None and str(reasoning).strip():
        norm_reasoning = str(reasoning).strip().lower()
        agent_patch["reasoning"] = {"effort": norm_reasoning}

    encoded_id = urllib.parse.quote(session_id, safe="")
    try:
        with _api_request(
            "POST",
            f"/sessions/{encoded_id}",
            payload={"agent": agent_patch},
            timeout=30,
            vm=vm,
            operation="update stateful session model",
        ) as resp:
            raw = resp.read().decode("utf-8", errors="replace").strip()
            data = json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = str(e)
        err_msg = err_body
        try:
            err_json = json.loads(err_body)
            if isinstance(err_json, dict):
                err_obj = err_json.get("error")
                if isinstance(err_obj, dict) and err_obj.get("message"):
                    err_msg = err_obj["message"]
                elif err_json.get("message"):
                    err_msg = err_json["message"]
        except Exception:
            pass
        return False, (
            f"[Provider Refused] Failed to update Stateful session '{session_id}' to model '{model}' "
            f"(HTTP {e.code}): {err_msg}\n"
            f"Guidance:\n"
            f"  1. Active Stateful session '{session_id}' was kept intact.\n"
            f"  2. Choose a supported {st_provider} Agents API model (e.g. '/provider {st_provider} gpt-6.1-terra').\n"
            f"  3. Or run '/ai-new' to exit Stateful mode before switching to a Stateless model."
        )
    except Exception as e:
        return False, f"[Provider Error] Failed to update Stateful session '{session_id}' to model '{model}': {e}"

    agent_resp = data.get("agent") if isinstance(data, dict) and isinstance(data.get("agent"), dict) else {}
    updated_model = str(agent_resp.get("model") or model)
    updated_reasoning = norm_reasoning
    if updated_reasoning is None and isinstance(agent_resp.get("reasoning"), dict):
        eff = agent_resp["reasoning"].get("effort")
        if eff:
            updated_reasoning = str(eff).strip().lower()

    if vm is not None and hasattr(vm, "host"):
        vm.host["ai_stateful_model"] = updated_model
        if updated_reasoning is not None:
            vm.host["ai_stateful_reasoning"] = updated_reasoning

    eff_disp = updated_reasoning or (vm.host.get("ai_stateful_reasoning") if vm is not None and hasattr(vm, "host") else None) or "none"
    reasoning_str = f" (Reasoning: {eff_disp})" if eff_disp and str(eff_disp).lower() != "none" else ""
    return True, f"[AI] Updated Stateful session '{session_id}' to {st_provider} | {updated_model}{reasoning_str}."


def apply_stateless_provider(vm, spec: str, reasoning: str = None) -> tuple[bool, str]:
    load_dotenv()
    spec = (spec or "").strip()
    if not spec:
        return False, "[Provider Error] Provider or model specification cannot be empty."

    if reasoning is None:
        parts = re.split(r"[,，]", spec, maxsplit=1)
        if len(parts) == 2:
            cand_target, cand_reasoning = parts[0].strip(), parts[1].strip()
            if cand_reasoning.lower() in ("none", "low", "medium", "high"):
                spec = cand_target
                reasoning = cand_reasoning.capitalize()
        else:
            m = re.search(r"\bwith\s+(low|medium|high|none)\s+(?:reasoning|effort)\b", spec, re.I)
            if m:
                reasoning = m.group(1).capitalize()
                spec = spec[:m.start()].strip()

    cfg = load_providers_config(vm)
    profiles = cfg.get("stateless", {}).get("profiles", {})
    spec_clean = spec.strip().lower()
    spec_tokens = set(re.findall(r"[a-z0-9]+", spec_clean))

    def _score_profile(k: str, p: dict) -> int:
        k_lower = k.lower()
        if k_lower == spec_clean:
            return 1000
        if p.get("model", "").lower() == spec_clean:
            return 500
        for a in p.get("aliases", []):
            if a.lower() == spec_clean:
                return 400
        if p.get("provider", "").lower() == spec_clean:
            return 300

        score = 0
        provider = p.get("provider", "").lower()
        model = p.get("model", "").lower()
        model_tokens = set(re.findall(r"[a-z0-9]+", model))
        key_tokens = set(re.findall(r"[a-z0-9]+", k_lower))

        if provider and provider in spec_tokens:
            score += 50
        elif provider and not (provider in spec_tokens):
            all_known_providers = {prof.get("provider", "").lower() for prof in profiles.values()} - {""}
            if any(kp in spec_tokens for kp in all_known_providers):
                score -= 100

        if model_tokens and model_tokens.issubset(spec_tokens):
            score += 40
        elif any(t in spec_tokens for t in model_tokens):
            score += 20

        for a in p.get("aliases", []):
            a_tokens = set(re.findall(r"[a-z0-9]+", a.lower()))
            if a_tokens and a_tokens.issubset(spec_tokens):
                score += 30
                break

        if key_tokens and key_tokens.issubset(spec_tokens):
            score += 30

        return score

    best_match = None
    best_key = None
    best_score = 0

    for k, p in profiles.items():
        s = _score_profile(k, p)
        if s > best_score:
            best_score = s
            best_key, best_match = k, p

    active_session_id = vm.host.get("ai_active_session_id") if (vm is not None and hasattr(vm, "host")) else None
    st_cfg = get_stateful_config(vm)
    st_provider_lower = (st_cfg.get("provider") or "OpenAI").strip().lower()

    if active_session_id:
        non_stateful_providers = {
            (p.get("provider") or "").strip().lower()
            for p in profiles.values()
            if not _is_stateful_compatible_profile(vm, p)
        } - {""}
        has_non_stateful_provider_token = any(np in spec_tokens for np in non_stateful_providers)

        if not best_match or (not _is_stateful_compatible_profile(vm, best_match) and best_score < 50 and not has_non_stateful_provider_token):
            if not has_non_stateful_provider_token:
                target_model = re.sub(rf"^{re.escape(st_provider_lower)}\s+", "", spec.strip(), flags=re.I).strip()
                if target_model and target_model.lower() != st_provider_lower:
                    return _update_stateful_session_model(vm, active_session_id, target_model, reasoning=reasoning)
            available = ", ".join(list_stateless_profiles(vm))
            return False, f"[Provider Error] Unknown provider or model '{spec}'. Available profiles: {available}"

    if not best_match:
        available = ", ".join(list_stateless_profiles(vm))
        return False, f"[Provider Error] Unknown provider or model '{spec}'. Available profiles: {available}"

    matched_key, matched_profile = best_key, best_match

    if active_session_id:
        if not _is_stateful_compatible_profile(vm, matched_profile):
            cur_info = get_active_provider_info(vm)
            cur_provider = cur_info.get("provider", st_cfg.get("provider", "OpenAI"))
            cur_model = cur_info.get("model", st_cfg.get("model", "gpt-6-luna"))
            req_provider = matched_profile.get("provider", "Stateless")
            req_model = matched_profile.get("model", matched_key)
            refusal_msg = (
                f"[Provider Refused] Cannot switch to Stateless provider '{req_provider} | {req_model}' "
                f"while in Stateful mode (active remote session: {active_session_id}, provider: {cur_provider} | {cur_model}).\n"
                f"Guidance:\n"
                f"  1. To switch models within this Stateful session, choose an {cur_provider} Agents API compatible model (e.g. '/provider {cur_provider} gpt-6.1-terra').\n"
                f"  2. For a one-shot task using '{req_provider} | {req_model}' without leaving Stateful mode, use:\n"
                f"     /with-model {matched_key} subagent: <prompt>\n"
                f"  3. To exit Stateful mode and return to local Stateless mode first, run:\n"
                f"     /ai-new\n"
                f"     and then switch provider again."
            )
            return False, refusal_msg

        exact_aliases = [a.lower() for a in matched_profile.get("aliases", [])]
        is_exact = (
            matched_key.lower() == spec_clean
            or matched_profile.get("model", "").lower() == spec_clean
            or spec_clean in exact_aliases
        )
        if is_exact:
            target_model = matched_profile.get("model") or spec.strip()
        else:
            stripped = re.sub(rf"^{re.escape(st_provider_lower)}\s+", "", spec.strip(), flags=re.I).strip()
            target_model = stripped if (stripped and stripped.lower() != st_provider_lower) else (matched_profile.get("model") or spec.strip())
        target_reasoning = reasoning if reasoning is not None else (matched_profile.get("reasoning") if is_exact else None)
        return _update_stateful_session_model(vm, active_session_id, target_model, reasoning=target_reasoning)

    active = dict(matched_profile)
    api_key_env = active.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(api_key_env, "").strip()

    if not api_key and api_key_env != "OLLAMA_API_KEY":
        return False, f"[Provider Error] API key '{api_key_env}' is not set in environment or .env."

    if reasoning is not None:
        active["reasoning"] = reasoning.capitalize() if reasoning.lower() in ("low", "medium", "high") else reasoning

    if vm is not None and hasattr(vm, "host"):
        vm.host["ai_stateless_profile"] = active

    if active.get("reasoning"):
        os.environ["OPENAI_REASONING_EFFORT"] = active["reasoning"]

    reasoning_disp = active.get("reasoning", "")
    reasoning_str = f" (Reasoning: {reasoning_disp})" if reasoning_disp and reasoning_disp.lower() != "none" else ""
    return True, f"[AI] Switched Stateless provider to {active.get('provider')} | {active.get('model')}{reasoning_str}."


class TeeOutput(io.StringIO):
    """Mirror stdout to both the original stream and an internal buffer."""
    def __init__(self, target):
        super().__init__()
        self.target = target

    def write(self, s):
        try:
            self.target.write(s)
            self.target.flush()
        except Exception:
            pass
        return super().write(s)


def init_diagnostics(vm, *, database_path=None, force=False):
    """Initialize SQLite-backed diagnostic logging for the peforth runtime."""
    if not force and getattr(vm, "_diagnostics_initialized", False):
        return vm.host.get("diagnostic_log")
    vm._diagnostics_initialized = True

    load_dotenv()
    log_mode = os.environ.get("PEFORTH_AI_LOG_MODE", "normal").strip().lower()
    vm.host["diagnostic_log_mode"] = log_mode
    if log_mode == "disabled":
        return None

    try:
        from diagnostic_log import DiagnosticLog
    except ImportError:
        try:
            from peforth.diagnostic_log import DiagnosticLog
        except ImportError:
            return None

    try:
        env = "windows" if os.name == "nt" else "wsl"
        if database_path is None:
            config_dir = os.environ.get("PEFORTH_CONFIG_DIR")
            db_dir = Path(config_dir).expanduser() if config_dir else _safe_home_dir() / ".peforth"
            database_path = db_dir / "ai-diagnostics.sqlite3"

        logger = DiagnosticLog(database_path, environment=env)
        file_dir = vm.host.get("__file__dir__") if (vm is not None and hasattr(vm, "host")) else None
        runtime_dir = Path(file_dir).resolve() if file_dir else Path(__file__).resolve().parent
        metadata = {
            "argv": sys.argv,
            "version": "2.1.0",
        }
        runtime_id = logger.start_runtime(
            source_path=_reported_source_path(runtime_dir),
            runtime_path=str(runtime_dir),
            runtime_version=sys.version.split()[0],
            metadata=metadata,
        )
        vm.host["diagnostic_log"] = logger
        vm.host["diagnostic_runtime_id"] = runtime_id

        def _cleanup():
            try:
                logger.finish_runtime(runtime_id)
            except Exception:
                pass
            try:
                logger.close()
            except Exception:
                pass
        atexit.register(_cleanup)
        return logger
    except Exception:
        return None


def _ensure_local_session_id(vm) -> str:
    """Return or generate the current local Stateless session ID (local_<16-hex>)."""
    local_id = vm.host.get("ai_local_session_id")
    if not local_id:
        local_id = f"local_{uuid.uuid4().hex[:16]}"
        vm.host["ai_local_session_id"] = local_id
    return local_id


def _current_diagnostic_session_id(vm) -> str | None:
    """Return the active remote session ID (sess_...) or local Stateless session ID (local_...)."""
    return vm.host.get("ai_active_session_id") or vm.host.get("ai_local_session_id")


def _log_event(vm, event_type, turn_id=None, *, payload=None, call_id=None,
               operation=None, http_method=None, url=None, http_status=None,
               elapsed_ms=None, error=None, session_id=None):
    """Append a diagnostic event to the timeline table if logging is enabled."""
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None:
        return None
    try:
        return logger.append_event(
            runtime_id, turn_id, event_type,
            session_id=session_id if session_id is not None else _current_diagnostic_session_id(vm),
            call_id=call_id,
            operation=operation,
            http_method=http_method,
            url=url,
            http_status=http_status,
            elapsed_ms=elapsed_ms,
            payload=payload,
            error_type=type(error).__name__ if error is not None else None,
            error_message=str(error) if error is not None else None,
        )
    except Exception:
        return None


def _finish_turn(vm, turn_id, *, output_text=None, output_status="complete", status="completed", error=None):
    """Mark a turn finished and append the completion/failure event in the timeline."""
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None or turn_id is None:
        return
    try:
        logger.finish_turn(
            turn_id,
            output_text=output_text,
            output_status=output_status,
            status=status,
            error_type=type(error).__name__ if error is not None else None,
            error_message=str(error) if error is not None else None,
        )
        event_type = {
            "completed": "ai_turn_completed",
            "cancelled": "ai_turn_cancel_requested",
        }.get(status, "ai_turn_failed")
        logger.append_event(
            runtime_id, turn_id, event_type,
            session_id=_current_diagnostic_session_id(vm),
            error_type=type(error).__name__ if error is not None else None,
            error_message=str(error) if error is not None else None,
        )
    except Exception:
        pass


def log_heartbeat(vm, message="heartbeat"):
    """Record an AI heartbeat in the diagnostic log for watchdog progress tracking."""
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None:
        return False
    try:
        logger.append_event(
            runtime_id, vm.host.get("ai_current_turn_id"), "ai_heartbeat",
            payload={"message": str(message)}
        )
        return True
    except Exception:
        return False


def install_security_guard(vm):
    """Install security decorator on vm.call to protect against unsafe AI execution."""
    init_diagnostics(vm)
    if getattr(vm, "_security_guard_installed", False):
        return
    vm._security_guard_installed = True

    original_call = vm.call

    def security_aware_call(operation):
        task = vm.task
        in_ai_task = vm.host.get("in_ai_task")

        # Security check applies only when running inside an AI Task context
        if in_ai_task is not None and task is in_ai_task:
            if vm.host.get("in_approval"):
                yield from original_call(operation)
                return

            resolved = vm._resolve(operation)

            # Containers (tuples of colon steps) and Literals are internal execution constructs;
            # their contained steps or values are dispatched individually through vm.call.
            import projectk
            if isinstance(resolved, (tuple, list, projectk.Literal)):
                yield from original_call(operation)
                return

            # Inherited Frame Safety:
            # If the current execution is within a Frame whose word is marked safe=True,
            # internal helper operations (like unannotated python closures) within this
            # parent frame inherit safety and execute freely.
            # Frames below ai_task_base_frame_depth belong to the outer orchestrator
            # (such as ai: or (ai)) and must never leak safety to untrusted AI code.
            base_depth = vm.host.get("ai_task_base_frame_depth", 0)
            frames = getattr(task, "frames", [])
            relevant_frames = frames[base_depth:] if base_depth < len(frames) else []

            def _is_safe_word(w):
                if getattr(w, "safe", False) is True:
                    return True
                if hasattr(w, "properties") and isinstance(w.properties, dict) and w.properties.get("safe") is True:
                    return True
                if callable(w) and getattr(w, "_safe", False) is True:
                    return True
                return False

            def _is_explicitly_unsafe_word(w):
                if getattr(w, "safe", None) is False:
                    return True
                if hasattr(w, "properties") and isinstance(w.properties, dict) and w.properties.get("safe") is False:
                    return True
                return False

            if any(_is_safe_word(getattr(f, "word", None)) for f in relevant_frames):
                # An explicitly unsafe word (safe=False) must NEVER inherit safety
                if not _is_explicitly_unsafe_word(resolved):
                    yield from original_call(operation)
                    return

            trusted_tasks = vm.host.setdefault("trusted_ai_tasks", set())
            if task not in trusted_tasks:
                if not _is_safe_word(resolved):
                    source_text = getattr(resolved, "source", None)
                    name = getattr(resolved, "name", None)
                    if not name and callable(resolved):
                        import inspect
                        try:
                            fn_src = inspect.getsource(resolved).strip()
                            if fn_src:
                                source_text = source_text or fn_src
                                name = fn_src.splitlines()[0]
                        except Exception:
                            pass
                        if not name:
                            fn_name = getattr(resolved, "__name__", "")
                            if fn_name and fn_name != "<lambda>":
                                name = fn_name
                    if not name:
                        name = source_text if source_text else repr(resolved)
                    if not source_text:
                        source_text = name

                    turn_id = vm.host.get("ai_current_turn_id")

                    # In interactive mode (not headless), prompt for approval directly
                    if not vm.host.get("headless", False):
                        proposal = {
                            "word": name,
                            "source": source_text,
                        }
                        _log_event(vm, "approval_requested", turn_id=turn_id,
                                   operation=name, payload=proposal)

                        nokia_word = vm.tick("nokia")
                        if nokia_word:
                            yield from vm.call(nokia_word)

                        vm.host["in_approval"] = True
                        try:
                            choice = read_numbered_choice(
                                "Choose 1-4: ",
                                default="1",
                                labels={
                                    "1": "Allow Once",
                                    "2": "Trust this AI task",
                                    "3": "Deny this proposal",
                                    "4": "Cancel this AI task",
                                },
                                styles={"1": _ANSI_GREEN, "2": _ANSI_GREEN, "3": _ANSI_DIM, "4": _ANSI_DIM},
                                proposal=proposal,
                            )
                        finally:
                            vm.host["in_approval"] = False

                        decision = {
                            "1": "allow_once",
                            "2": "trust_task",
                            "3": "deny",
                            "4": "cancel",
                        }.get(choice, "allow_once")

                        _log_event(vm, "approval_received", turn_id=turn_id,
                                   operation=name, payload={"decision": decision})

                        if decision == "trust_task":
                            trusted_tasks.add(task)
                        elif decision == "deny":
                            raise KernelError(f"Security: Execution of word '{name}' was denied.")
                        elif decision == "cancel":
                            task.cancel()
                            raise KernelError("Security: AI task was cancelled.")
                        # "allow_once": execute this call once without adding to trusted_tasks
                        vm.host["in_approval"] = True
                        try:
                            yield from original_call(operation)
                        finally:
                            vm.host["in_approval"] = False
                        return

                    # Fallback for headless / non-interactive test mode: pause task
                    sys.__stdout__.write(f"\n[Security] Word '{name}' is not marked as safe.\n")
                    sys.__stdout__.write("Task paused for review. Type 'resume' for single step, 'trust-task resume' to trust this task.\n")
                    sys.__stdout__.flush()

                    vm.host["pending_ai_task"] = task
                    yield vm.pause()

        yield from original_call(operation)

    vm.call = security_aware_call


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "peforth_search_words",
            "description": "Search the current Forth dictionary (words, category, help, comments, source). Pure read-only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword to search in word names, help strings, or comments."
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "peforth_search_sessions",
            "description": "Search or read past AI conversations in the local SQLite session mirror (sessions.sqlite3). Read-only. Pass query to search across all sessions, or session_id to read messages from a specific session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search terms to match against session descriptions and conversation items.",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID (or unambiguous suffix) to read conversation messages from.",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 20,
                        "description": "Maximum number of matching sessions or messages to return.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "peforth_read_skill",
            "description": (
                "Read full documentation or companion files for an available skill. "
                "Call without file_path to read the main SKILL.md and discover companion files (references, scripts). "
                "Call with file_path (relative to the skill directory) to read a specific reference or script."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "The logical name of the skill (e.g. 'peforth-forth', 'line-notify').",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional relative path inside the skill directory (e.g. 'references/forth-reference.md', 'scripts/send_msgbox.ps1'). Defaults to 'SKILL.md'.",
                    },
                },
                "required": ["skill_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "peforth_run_forth",
            "description": (
                "Execute Forth source code in the user's local VM. "
                "ONLY use this tool when you genuinely need to run Forth/Python code, define words, inspect Forth state, or perform computations in Forth. "
                "NEVER use this tool for conversational responses, greetings, explanations, or telling jokes — reply directly in text instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Forth source code to evaluate in the VM."
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Clear explanation of why this Forth code is being executed."
                    }
                },
                "required": ["source", "purpose"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_provider",
            "description": "Switch the active AI provider, model, and reasoning effort when requested by the user in natural language (e.g. '切換到 Gemini 3.8 Flash，Medium', 'switch to o3-mini').",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_or_model": {
                        "type": "string",
                        "description": "Target provider or model name (e.g. 'Gemini 3.8 Flash', 'Google', 'o3-mini', 'gpt-4o-mini', 'Groq').",
                    },
                    "reasoning": {
                        "type": "string",
                        "enum": ["none", "low", "medium", "high", "None", "Low", "Medium", "High"],
                        "description": "Optional reasoning effort level.",
                    },
                },
                "required": ["provider_or_model"],
                "additionalProperties": False,
            },
        },
    },
]


def tool_search_words(vm, query):
    """Search words in vm.words matching query (supports multi-token relevance scoring)."""
    tokens = [t.strip().lower() for t in query.split() if t.strip()]
    if not tokens:
        tokens = [query.strip().lower()]

    scored = []
    for name, word in vm.words.items():
        score = 0
        name_lower = name.lower()
        help_text = getattr(word, "help", "") or ""
        help_lower = help_text.lower()
        comment = getattr(word, "comment", "") or ""
        comment_lower = comment.lower()
        source = getattr(word, "source", "") or ""
        source_lower = source.lower()

        for tok in tokens:
            if tok == name_lower:
                score += 100
            elif tok in name_lower:
                score += 30
            if tok in help_lower:
                score += 20
            if tok in comment_lower:
                score += 10
            if tok in source_lower:
                score += 5

        if score > 0:
            scored.append((score, {
                "name": name,
                "category": getattr(word, "category", "host"),
                "help": help_text,
                "comment": comment,
                "source": source,
                "safe": word.properties.get("safe", False) if hasattr(word, "properties") else False
            }))

    scored.sort(key=lambda item: item[0], reverse=True)
    matches = [item[1] for item in scored[:30]]
    return {"query": query, "count": len(matches), "words": matches}


# --- Session Store & Local SQLite Mirror Helpers ---

def _runtime_config_path() -> Path:
    configured = os.environ.get("PEFORTH_CONFIG_DIR")
    if configured:
        path = Path(configured).expanduser()
        return path if path.is_absolute() else (Path.cwd() / path).resolve()
    return _safe_home_dir() / ".peforth"


def _session_db_path() -> Path:
    """Return the path to the local SQLite session mirror database."""
    return _runtime_config_path() / "sessions" / "sessions.sqlite3"


def _open_session_store() -> SessionStore:
    return SessionStore(_session_db_path())


def _short_id(session_id):
    return str(session_id or "")[-8:]


def _resolve_session_selector(rows, selector):
    """Return (1-based index, row) for a numeric index or exact session ID."""
    if isinstance(selector, int) and not isinstance(selector, bool):
        if 1 <= selector <= len(rows):
            return selector, rows[selector - 1]
        raise RuntimeError(f"No session number {selector}; the current list has {len(rows)} entries.")
    if isinstance(selector, str) and selector:
        matches = [(index, row) for index, row in enumerate(rows, 1)
                   if (row.get("id") or row.get("session_id")) == selector]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise RuntimeError(f"No session ID matches {selector!r} in the current list.")
        raise RuntimeError(f"Session ID {selector!r} is duplicated in the current list.")
    raise RuntimeError("Expected a session number or full session ID.")


def _session_title(session_id):
    """Return the session description from the local SQLite mirror if present."""
    if not isinstance(session_id, str) or not session_id:
        return ""
    db_path = _session_db_path()
    if not db_path.is_file():
        return ""
    with _open_session_store() as store:
        return store.get_description(session_id)


def _format_time(value):
    if not value:
        return "unknown"
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except (ValueError, TypeError, OSError, OverflowError):
        return str(value)


def _saved_session(vm):
    return vm.host.get("ai_active_session_id") or ""


_current_sync_vm = None


@contextlib.contextmanager
def _sync_context(vm):
    global _current_sync_vm
    prev = _current_sync_vm
    _current_sync_vm = vm
    try:
        yield
    finally:
        _current_sync_vm = prev


def _api_request(method, path, payload=None, stream=False, timeout=30, *, vm=None, operation=None):
    load_dotenv()
    effective_vm = vm if vm is not None else _current_sync_vm
    st_cfg = get_stateful_config(effective_vm)
    key_env = st_cfg.get("api_key_env", "OPENAI_API_KEY")
    key = os.environ.get(key_env, "").strip()
    if not key:
        raise RuntimeError(f"Set {key_env} in ~/.peforth/.env or the process environment to use AI.")
    base_url = st_cfg.get("endpoint", "https://api.openai.com/v1").strip().rstrip("/")
    if not base_url.endswith("/agents"):
        base_url = f"{base_url}/agents"
    url = f"{base_url}{path}" if path.startswith("/") else f"{base_url}/{path}"
    request_text = None if payload is None else json.dumps(payload, ensure_ascii=False)
    body = request_text.encode("utf-8") if request_text is not None else None
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "agents=v1",
        "Accept": "text/event-stream" if stream else "application/json",
    }
    req = urllib.request.Request(url, data=body, method=method.upper(), headers=headers)
    t0 = time.monotonic()
    effective_vm = vm if vm is not None else _current_sync_vm
    if effective_vm is not None:
        _log_event(
            effective_vm,
            "http_request_started",
            http_method=method.upper(),
            url=url,
            operation=operation or path,
            payload={"path": path} if payload is None else payload,
        )
    try:
        response = _urlopen_interruptible(req, timeout=timeout)
        if effective_vm is not None:
            elapsed_ms = (time.monotonic() - t0) * 1000.0
            http_status = getattr(response, "status", getattr(response, "code", 200))
            _log_event(
                effective_vm,
                "http_response_received",
                http_method=method.upper(),
                url=url,
                http_status=http_status,
                elapsed_ms=elapsed_ms,
                operation=operation or path,
            )
        return response
    except urllib.error.HTTPError as e:
        if effective_vm is not None:
            elapsed_ms = (time.monotonic() - t0) * 1000.0
            _log_event(
                effective_vm,
                "http_request_failed",
                http_method=method.upper(),
                url=url,
                http_status=e.code,
                elapsed_ms=elapsed_ms,
                operation=operation or path,
                error=e,
            )
        raise
    except Exception as e:
        if effective_vm is not None:
            elapsed_ms = (time.monotonic() - t0) * 1000.0
            _log_event(
                effective_vm,
                "http_request_failed",
                http_method=method.upper(),
                url=url,
                elapsed_ms=elapsed_ms,
                operation=operation or path,
                error=e,
            )
        raise


def _api_get(path, timeout=30, *, vm=None, operation=None):
    with _api_request("GET", path, timeout=timeout, vm=vm, operation=operation) as response:
        return json.load(response)


def _api_delete(path, timeout=30, *, vm=None, operation=None):
    with _api_request("DELETE", path, timeout=timeout, vm=vm, operation=operation) as response:
        return json.load(response)


def _list_remote_sessions():
    """Fetch remote session records using the API's cursor pagination."""
    sessions = []
    after = ""
    page = 1
    while True:
        query = urllib.parse.urlencode({"limit": 100, "order": "desc", **({"after": after} if after else {})})
        op = f"/sessions (page {page})"
        data = _api_get(f"/sessions?{query}", operation=op)
        sessions.extend(data.get("data") or [])
        if not data.get("has_more") or not data.get("last_id") or data["last_id"] == after:
            return sessions
        after = data["last_id"]
        page += 1


def _fetch_session_items(session_id):
    """Fetch all remote items for a session in ascending sequence order."""
    encoded_id = urllib.parse.quote(session_id, safe="")
    short_sid = _short_id(session_id)
    items = []
    after = None
    page = 1
    while True:
        query = {"limit": 100, "order": "asc"}
        if after:
            query["after"] = after
        op = f"/sessions/{short_sid}/items (page {page})"
        data = _api_get(
            f"/sessions/{encoded_id}/items?{urllib.parse.urlencode(query)}",
            operation=op,
        )
        items.extend(data.get("data") or [])
        last_id = data.get("last_id")
        if not data.get("has_more") or not last_id or last_id == after:
            break
        after = last_id
        page += 1
    return items


def sync_sessions(vm=None):
    """Incrementally sync remote sessions and items into the local SQLite mirror."""
    with _sync_context(vm):
        t_start = time.monotonic()
        if vm is not None:
            _log_event(vm, "session_sync_started", operation="fetching remote sessions")
        remote_sessions = _list_remote_sessions()
        synced = 0
        skipped = 0
        remote_ids = []
        if vm is not None:
            _log_event(
                vm,
                "session_sync_remote_listed",
                operation=f"found {len(remote_sessions)} remote sessions",
                payload={"total_remote": len(remote_sessions)},
            )
        with _open_session_store() as store:
            for remote in remote_sessions:
                if not isinstance(remote, dict):
                    continue
                session_id = remote.get("id") or remote.get("session_id")
                if not isinstance(session_id, str) or not session_id:
                    continue
                remote_ids.append(session_id)
                if store.needs_item_sync(remote):
                    short_sid = _short_id(session_id)
                    if vm is not None:
                        _log_event(
                            vm,
                            "session_items_sync_started",
                            session_id=session_id,
                            operation=f"syncing items for {short_sid}",
                        )
                    items = _fetch_session_items(session_id)
                    store.sync_session(remote, items)
                    synced += 1
                    if vm is not None:
                        _log_event(
                            vm,
                            "session_items_sync_completed",
                            session_id=session_id,
                            operation=f"synced {len(items)} items for {short_sid}",
                            payload={"count": len(items)},
                        )
                else:
                    store.update_session_metadata(remote)
                    skipped += 1
            deleted = store.mark_missing_remote_deleted(remote_ids)
            local_by_id = {
                row["id"]: row for row in store.list_sessions(include_deleted=False)
            }
            rows = [local_by_id[sid] for sid in remote_ids if sid in local_by_id]
        if vm is not None:
            vm.host["ai_session_rows"] = rows
            elapsed_total = (time.monotonic() - t_start) * 1000.0
            _log_event(
                vm,
                "session_sync_completed",
                elapsed_ms=elapsed_total,
                operation=f"synced={synced} skipped={skipped} deleted={deleted}",
                payload={"total": len(remote_ids), "synced": synced, "skipped": skipped, "deleted": deleted},
            )
        return {
            "total": len(remote_ids),
            "synced": synced,
            "skipped": skipped,
            "deleted": deleted,
            "rows": rows,
        }


def list_local_sessions(vm=None, *, include_deleted=False):
    """Read sessions from the local SQLite mirror."""
    db_path = _session_db_path()
    if not db_path.is_file():
        rows = []
    else:
        with _open_session_store() as store:
            rows = store.list_sessions(include_deleted=include_deleted)
    if vm is not None:
        vm.host["ai_session_rows"] = rows
    return rows


def export_session_json(selector, output_path=None, *, vm=None):
    """Export a session's items from the local SQLite mirror to a JSON array file."""
    with _open_session_store() as store:
        rows = (vm.host.get("ai_session_rows") if vm is not None else None)
        if rows is None:
            rows = store.list_sessions(include_deleted=True)
        if isinstance(selector, int) and not isinstance(selector, bool):
            _, row = _resolve_session_selector(rows, selector)
            session_id = row.get("id") or row.get("session_id")
        elif isinstance(selector, str) and selector:
            all_local = store.list_sessions(include_deleted=True)
            candidates = rows or all_local
            exact = [
                r for r in candidates
                if (r.get("id") or r.get("session_id")) == selector
            ]
            if len(exact) == 1:
                session_id = exact[0].get("id") or exact[0].get("session_id")
            elif store.get_session(selector) is not None:
                session_id = selector
            else:
                suffix = [
                    r for r in candidates
                    if _short_id(r.get("id") or r.get("session_id")) == selector
                ]
                if len(suffix) == 1:
                    session_id = suffix[0].get("id") or suffix[0].get("session_id")
                elif len(suffix) > 1:
                    raise RuntimeError(f"Session ID suffix {selector!r} is ambiguous; use the full ID.")
                else:
                    session_id = selector
        else:
            raise RuntimeError("Expected a session number or session ID.")

        local = store.get_session(session_id)
        if local is None or not local.get("synced_at"):
            items = _fetch_session_items(session_id)
            store.sync_session({"id": session_id}, items)

        if output_path is None or (isinstance(output_path, str) and not output_path.strip()):
            stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
            output_path = f"ai-session-full-{stamp}.json"
        return store.export_session_json(session_id, output_path)


def search_local_sessions(query, *, include_deleted=True):
    """Search descriptions and item contents in the local SQLite mirror."""
    db_path = _session_db_path()
    if not db_path.is_file():
        return []
    with _open_session_store() as store:
        return store.search_sessions(str(query or ""), include_deleted=include_deleted)


def query_local_sessions(*, query=None, session_id=None, limit=20, include_deleted=True):
    """Read-only search or message inspection against the local SQLite session mirror."""
    db_path = _session_db_path()
    if not db_path.is_file():
        return {"sessions": [], "messages": []}
    limit = max(1, min(int(limit or 20), 100))
    with _open_session_store() as store:
        if isinstance(session_id, str) and session_id.strip():
            target_id = session_id.strip()
            session = store.get_session(target_id)
            if session is None:
                all_sessions = store.list_sessions(include_deleted=include_deleted)
                suffix_matches = [
                    row for row in all_sessions
                    if _short_id(row.get("session_id")) == target_id
                ]
                if len(suffix_matches) == 1:
                    target_id = suffix_matches[0]["session_id"]
                    session = suffix_matches[0]
                elif len(suffix_matches) > 1:
                    raise ValueError(f"Session ID suffix {target_id!r} is ambiguous; use the full ID.")
                else:
                    return {"session": None, "messages": []}
            messages = store.get_session_messages(target_id, limit=limit)
            if isinstance(query, str) and query.strip():
                terms = [t.casefold() for t in query.split() if t.strip()]
                messages = [
                    msg for msg in messages
                    if any(term in msg["text"].casefold() for term in terms)
                ][:limit]
            return {
                "session": {
                    "session_id": session["session_id"],
                    "description": session.get("description") or "",
                    "created_at": session.get("created_at"),
                    "last_active_at": session.get("last_active_at"),
                    "status": session.get("status"),
                    "model": session.get("model"),
                    "remote_deleted": session.get("remote_deleted"),
                },
                "messages": messages,
            }
        results = store.search_sessions(str(query or ""), include_deleted=include_deleted)
        return {
            "sessions": [
                {
                    "session_id": row["session_id"],
                    "description": row.get("description") or "",
                    "created_at": row.get("created_at"),
                    "last_active_at": row.get("last_active_at"),
                    "status": row.get("status"),
                    "model": row.get("model"),
                    "remote_deleted": row.get("remote_deleted"),
                    "matches": row.get("matches") or [],
                }
                for row in results[:limit]
            ],
            "messages": [],
        }


def get_ai_context(vm) -> dict:
    """Return the context dictionary for the currently active AI session.

    In Stateful mode (when vm.host['ai_active_session_id'] is set):
      - Checks local session mirror freshness against remote metadata.
      - If stale or missing, fetches remote items and updates the local mirror.
      - Returns a dict with mode="stateful", session_id, and the ordered raw items.

    In Stateless mode (default in-memory conversation):
      - Dumps the active conversation from vm.host['ai_messages'].
      - Returns a dict with mode="stateless", session_id (local session ID),
        and the list of message dicts (user, assistant, tool calls, tool results).
    """
    import copy
    import urllib.parse

    active_id = vm.host.get("ai_active_session_id")
    if active_id:
        items = []
        with _sync_context(vm), _open_session_store() as store:
            remote_session = None
            try:
                encoded_id = urllib.parse.quote(active_id, safe="")
                remote_session = _api_get(
                    f"/sessions/{encoded_id}",
                    operation=f"get session {_short_id(active_id)}",
                )
            except Exception:
                remote_session = None

            if remote_session and isinstance(remote_session, dict):
                if store.needs_item_sync(remote_session):
                    items = _fetch_session_items(active_id)
                    store.sync_session(remote_session, items)
                else:
                    store.update_session_metadata(remote_session)

            items = store.get_session_items(active_id)

        return {
            "mode": "stateful",
            "session_id": active_id,
            "items": items,
        }
    else:
        local_id = vm.host.get("ai_local_session_id") or _ensure_local_session_id(vm)
        raw_messages = vm.host.get("ai_messages") or []
        return {
            "mode": "stateless",
            "session_id": local_id,
            "items": copy.deepcopy(raw_messages),
        }


def normalize_forth_source(source: str) -> str:
    """Normalize Forth source code submitted by AI:
    1. Replaces invalid opening tag <pyV> with <py>.
    2. Ensures opening tag <py> is separated from surrounding code by whitespace.
    """
    if not source:
        return ""
    text = source
    # 1. Opening <pyV> is invalid -> convert to <py>
    text = re.sub(r"<pyV>", "<py>", text)
    # 2. Ensure whitespace after opening <py>: <py>import -> <py> import
    text = re.sub(r"<py>(?!\s|$)", "<py> ", text)
    # 3. Ensure whitespace before opening <py>: foo<py> -> foo <py>
    text = re.sub(r"(\S)<py>", r"\1 <py>", text)
    return text


SYSTEM_PROMPT = """You are an intelligent AI pair programmer embedded inside the peforth Forth environment.
peforth is an AI-first Forth environment hosted by Python. It seamlessly bridges Forth with Python: you can run native Forth, write Python host definitions, and execute Python code directly inside Forth!

=== The Two Pillars of peforth: Skills & Forth Words ===
1. SKILLS (Knowledge & SOPs): You do not need to memorize every procedure or domain upfront. When you need guidelines, workflows, or specialized knowledge, inspect === Available Skills === and use `peforth_read_skill` to retrieve detailed instructions just-in-time.
2. FORTH WORDS (Capabilities & Execution): When you need to inspect or act upon the system, search the live dictionary using `peforth_search_words` and execute clean Forth code via `peforth_run_forth`.

=== When to Respond Directly vs. When to Use Tools ===
- CONVERSATION & Q&A: For general conversation, greetings, questions, explanations, discussions, or telling jokes, respond DIRECTLY with natural language text! Your text reply is streamed immediately to the user's terminal.
  DO NOT use peforth_run_forth or print statements (e.g. s" ..." . cr) just to speak to the user or tell a joke!
- CODE EXECUTION: ONLY call peforth_run_forth when you genuinely need to execute Forth code, define new words, test behavior in the VM, perform calculations, or run Python interop requested by the user.
- AVOID DUPLICATE OUTPUT: When you use peforth_run_forth to execute code that produces output in the terminal, DO NOT repeat or echo that entire stdout in your final assistant reply; just briefly explain the result if necessary.
- SUBAGENT DELEGATION: If a Forth task requires isolated one-shot AI inference, formatting, or analysis without polluting the main conversation history, use `(subagent)` or `subagent:` (with optional `with-model`, `with-tools`, `with-instruction`, `with-reasoning` prefixes). Do NOT invoke recursive mainstream `ai:` from within a tool task.

=== Full Source Code Access & Self-Understanding ===
- You have full access to your own live Forth dictionary and underlying Python source code!
- Through `peforth_search_words`, you can inspect any word's help description, extended comments, and full implementation source code (both Forth colon definitions and host Python code).
- Because you have complete visibility into your own source code and architecture, you are fully equipped and encouraged to answer ANY questions the user asks about peforth itself, its internal mechanisms, word semantics, Forth stack effects, and Python bridge capabilities.
- When the user asks how peforth works or how to use a specific feature, consult your dictionary/skills to give accurate, authoritative, and helpful answers.

=== Forth & Python Bridge Syntax Guide ===
- WHITESPACE DELIMITATION: In Forth, all words and tokens MUST be separated by whitespace (spaces or newlines).
- PYTHON BLOCKS: Use `<py> ... </py>` for inline Python execution. To return values to the Forth data stack, call `vm.push(...)` inside Python.
  *IMPORTANT*: The opening `<py>` tag MUST be followed by whitespace before Python code!
  - Example: `<py> import os; print('hello') </py>`
  - Example: `<py> x = 123 + 456; vm.push(x) </py>`
  - WRONG: `<py>import os...</py>` (Fails as unknown word `<py>import`)

=== Important Rules ===
- When executing code, always explain your purpose and propose clean Forth source code.
- If your proposed code executes non-safe words (such as <py>, file operations, or system commands), the VM task-level security guard will pause and ask the user for approval. This is normal and expected.
- GOAL-DRIVEN & SELF-CORRECTION (使命必達): When a tool execution results in an error (e.g. syntax typo, missing quote, parameter error, command failure), DO NOT simply stop, apologize, or ask the user for permission to retry. Immediately analyze the error output, fix your Forth code, and call peforth_run_forth again in the same turn to accomplish the user's objective. Continue until the task is successfully completed or genuinely blocked.
- Be concise, accurate, and helpful.
"""


def get_skills_dir(vm=None) -> Path:
    """Resolve the active skills directory from environment, VM, or package location."""
    configured = os.environ.get("PEFORTH_SKILLS_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    if vm is not None:
        file_dir = vm.host.get("__file__dir__")
        if file_dir:
            candidate = Path(file_dir) / "skills"
            if candidate.is_dir():
                return candidate.resolve()
    candidate = Path(__file__).resolve().parent / "skills"
    if candidate.is_dir():
        return candidate.resolve()
    runtime_skills = _safe_home_dir() / ".peforth" / "skills"
    if runtime_skills.is_dir():
        return runtime_skills.resolve()
    return candidate


def parse_skill_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter key-value pairs (e.g. name, description) from SKILL.md."""
    meta = {}
    stripped_text = text.lstrip()
    if not stripped_text.startswith("---"):
        return meta
    parts = stripped_text.split("---", 2)
    if len(parts) < 3:
        return meta
    current_key = None
    multiline_buf = []

    def flush():
        nonlocal current_key, multiline_buf
        if current_key:
            val = " ".join(multiline_buf).strip()
            if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
                val = val[1:-1].strip()
            meta[current_key] = val
            multiline_buf = []
            current_key = None

    for line in parts[1].strip().splitlines():
        s = line.strip()
        if not s:
            continue
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            flush()
            key, sep, rest = line.partition(":")
            current_key = key.strip()
            rest = rest.strip()
            if rest in (">-", ">", "|", "|-"):
                multiline_buf = []
            elif rest:
                multiline_buf.append(rest)
        elif current_key:
            multiline_buf.append(s)
    flush()
    return meta


def load_skills_manifest(skills_root=None) -> tuple[list[str], str]:
    """Build a lightweight manifest of available skills without exposing local absolute paths."""
    if skills_root is None:
        skills_root = get_skills_dir()
    if not isinstance(skills_root, Path):
        skills_root = Path(skills_root)
    if not skills_root.is_dir():
        return [], ""

    skill_names = []
    lines = []
    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue
        skill_names.append(entry.name)
        meta = parse_skill_frontmatter(skill_file.read_text(encoding="utf-8"))
        desc = meta.get("description", "").strip()
        if not desc:
            desc = f"Skill {entry.name}"

        # Find companion files (excluding SKILL.md)
        companion_files = []
        for f in sorted(entry.rglob("*")):
            if f.is_file() and f.name != "SKILL.md":
                rel = str(f.relative_to(entry)).replace("\\", "/")
                companion_files.append(rel)

        companion_str = f" [companion: {', '.join(companion_files)}]" if companion_files else ""
        lines.append(f"- {entry.name}: {desc}{companion_str}")

    return skill_names, "\n".join(lines)


def load_all_skills(skills_root=None) -> tuple[list[str], str]:
    """Collect the markdown text of every skill bundle under skills_root."""
    if skills_root is None:
        skills_root = get_skills_dir()
    if not isinstance(skills_root, Path):
        skills_root = Path(skills_root)
    if not skills_root.is_dir():
        return [], ""

    skill_names = []
    parts = []
    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue
        skill_names.append(entry.name)
        text = skill_file.read_text(encoding="utf-8")
        # Strip leading YAML frontmatter (--- ... ---)
        text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
        parts.append(f"## Skill: {entry.name}\n\n{text}\n")
    return skill_names, "\n".join(parts)


def tool_read_skill(vm, skill_name: str, file_path: str = None) -> dict:
    """Read a skill's SKILL.md or companion reference/script file safely."""
    if not isinstance(skill_name, str) or not skill_name.strip():
        return {"error": "skill_name must be a non-empty string."}
    skill_name = skill_name.strip()
    if "/" in skill_name or "\\" in skill_name or Path(skill_name).name != skill_name:
        return {"error": f"Invalid skill name '{skill_name}'."}

    skills_root = get_skills_dir(vm).resolve()
    target_skill_dir = (skills_root / skill_name).resolve()

    try:
        target_skill_dir.relative_to(skills_root)
    except ValueError:
        return {"error": "Access denied: skill directory escapes skills root."}

    if not target_skill_dir.is_dir():
        return {"error": f"Skill '{skill_name}' not found."}

    companion_files = []
    for f in sorted(target_skill_dir.rglob("*")):
        if f.is_file() and f.name != "SKILL.md":
            rel = str(f.relative_to(target_skill_dir)).replace("\\", "/")
            companion_files.append(rel)

    subpath = (file_path or "SKILL.md").strip()
    target_file = (target_skill_dir / subpath).resolve()

    try:
        target_file.relative_to(target_skill_dir)
    except ValueError:
        return {"error": "Access denied: file_path escapes skill directory."}

    if not target_file.is_file():
        return {
            "error": f"File '{subpath}' not found in skill '{skill_name}'.",
            "available_companion_files": companion_files,
        }

    try:
        content = target_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

    res_file = str(target_file.relative_to(target_skill_dir)).replace("\\", "/")
    res = {
        "skill": skill_name,
        "file": res_file,
        "content": content,
    }
    if res_file == "SKILL.md":
        res["companion_files"] = companion_files
    return res


def get_system_prompt(vm=None) -> str:
    """Build full agent system prompt dynamically composed with loaded skills manifest."""
    skills_root = get_skills_dir(vm)
    skill_names, manifest_text = load_skills_manifest(skills_root)

    sys_info = detect_system_info(vm)
    shell_label = "pwsh (PowerShell 7)" if sys_info.get("active_shell") == "pwsh" else sys_info.get("active_shell", "unknown")
    os_label = sys_info.get("os", "unknown").lower()

    env_section = (
        f"\n\n=== System Environment ===\n"
        f"- OS: {os_label}\n"
        f"- Active Shell: {shell_label}\n"
    )

    instructions = SYSTEM_PROMPT + env_section
    if manifest_text:
        instructions += "\n\n=== Available Skills ===\n" + manifest_text

    if len(instructions.encode("utf-8")) > 50_000:
        raise RuntimeError("Agent instructions unexpectedly exceed maximum allowed size.")
    return instructions



def _sanitize_messages(messages):
    """Ensure every assistant message with tool_calls is properly closed by tool messages."""
    sanitized = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        sanitized.append(msg)
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            expected_ids = {tc["id"] for tc in msg["tool_calls"] if "id" in tc}
            j = i + 1
            tool_msgs = []
            while j < len(messages) and messages[j].get("role") == "tool":
                tool_msgs.append(messages[j])
                j += 1
            responded_ids = {tm.get("tool_call_id") for tm in tool_msgs}
            missing_ids = expected_ids - responded_ids
            for mid in missing_ids:
                tool_msgs.append({
                    "role": "tool",
                    "tool_call_id": mid,
                    "content": json.dumps({"error": "Tool execution was not completed."}, ensure_ascii=False)
                })
            sanitized.extend(tool_msgs)
            i = j
        else:
            i += 1
    return sanitized


def read_numbered_choice(
    prompt: str = "Choose 1-4: ",
    choices: tuple = ("1", "2", "3", "4"),
    default: str = "1",
    *,
    labels: dict = None,
    styles: dict = None,
    proposal: dict = None,
) -> str:
    """Read a single-key or numbered choice with prompt_toolkit, falling back to input()."""
    labels = labels or {
        "1": "Allow Once",
        "2": "Trust this AI task",
        "3": "Deny this proposal",
        "4": "Cancel this AI task",
    }
    styles = styles or {}

    if not sys.stdin.isatty():
        return default

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.keys import Keys
        from prompt_toolkit.formatted_text import ANSI
        import asyncio

        selected_index = [choices.index(default) if default in choices else 0]
        bindings = KeyBindings()

        def _confirm(event):
            event.current_buffer.text = choices[selected_index[0]]
            event.current_buffer.validate_and_handle()

        @bindings.add("c-m", eager=True)
        def _enter(event):
            _confirm(event)

        @bindings.add(" ", eager=True)
        def _space(event):
            _confirm(event)

        def _move_selection(event, step):
            selected_index[0] = (selected_index[0] + step) % len(choices)
            event.app.invalidate()

        @bindings.add(Keys.Up, eager=True)
        def _prev(event):
            _move_selection(event, -1)

        @bindings.add(Keys.Down, eager=True)
        def _next(event):
            _move_selection(event, 1)

        @bindings.add("escape")
        def _escape_cancel(event):
            cancel_choice = "4" if "4" in choices else ("2" if "2" in choices else choices[-1])
            selected_index[0] = choices.index(cancel_choice)
            event.current_buffer.text = cancel_choice
            event.app.invalidate()
            event.current_buffer.validate_and_handle()

        def _confirm_selected_choice(app, buffer):
            async def confirm_after_render():
                await asyncio.sleep(0.05)
                buffer.validate_and_handle()
            app.create_background_task(confirm_after_render())

        for choice in choices:
            def _select(event, selected=choice):
                selected_index[0] = choices.index(selected)
                event.current_buffer.text = selected
                event.app.invalidate()
                _confirm_selected_choice(event.app, event.current_buffer)
            bindings.add(choice, eager=True)(_select)

        def choice_prompt():
            selected = choices[selected_index[0]]
            selected_style = "\x1b[1;48;2;255;255;255;38;2;0;100;0m"
            reset = "\x1b[0m"
            rows = []
            for choice in choices:
                style = selected_style if choice == selected else styles.get(choice, "")
                suffix = reset if style else ""
                rows.append(f"{style}{choice}. {labels.get(choice, choice)}{suffix}")
            rows.extend(("", prompt))
            return ANSI("\n".join(rows))

        session = PromptSession(multiline=False, key_bindings=bindings)
        result = session.prompt(choice_prompt)
        return result.strip() if result and result.strip() in choices else default
    except KeyboardInterrupt:
        raise
    except Exception:
        for choice in choices:
            print(f"{choice}. {labels.get(choice, choice)}")
        try:
            val = input(prompt).strip()
            return val if val in choices else default
        except KeyboardInterrupt:
            raise
        except Exception:
            return default


def _resolve_tools_list(base_tools: list, tools_spec) -> list:
    """Resolve tools specification into a filtered list of tool schemas."""
    if tools_spec is None:
        return list(base_tools)
    if isinstance(tools_spec, str):
        clean = tools_spec.strip().lower()
        if clean in ("none", "off", "false", "0", "empty", "[]"):
            return []
        if clean in ("all", "default", "*"):
            return list(base_tools)
        wanted = {t.strip() for t in tools_spec.split(",") if t.strip()}
        return [
            t for t in base_tools
            if (t.get("name") or t.get("function", {}).get("name")) in wanted
        ]
    if isinstance(tools_spec, (list, tuple, set)):
        if not tools_spec:
            return []
        first = next(iter(tools_spec))
        if isinstance(first, dict):
            return list(tools_spec)
        wanted = {str(x).strip() for x in tools_spec if str(x).strip()}
        if wanted <= {"none", "off", "false", "0", "empty", "[]"}:
            return []
        if "all" in wanted or "*" in wanted:
            return list(base_tools)
        return [
            t for t in base_tools
            if (t.get("name") or t.get("function", {}).get("name")) in wanted
        ]
    return list(base_tools)


def resolve_profile_override(vm, base_profile: dict, model_spec: str = None, reasoning_spec: str = None) -> dict:
    """Return a profile dict incorporating optional model/provider and reasoning overrides without mutating global state."""
    prof = dict(base_profile)
    if model_spec:
        spec = str(model_spec).strip()
        cfg = load_providers_config(vm)
        profiles = cfg.get("stateless", {}).get("profiles", {})
        spec_clean = spec.lower()
        spec_tokens = set(re.findall(r"[a-z0-9]+", spec_clean))

        best_match = None
        best_score = 0
        for k, p in profiles.items():
            k_lower = k.lower()
            score = 0
            if k_lower == spec_clean:
                score = 1000
            elif p.get("model", "").lower() == spec_clean:
                score = 500
            elif any(a.lower() == spec_clean for a in p.get("aliases", [])):
                score = 400
            elif p.get("provider", "").lower() == spec_clean:
                score = 300
            else:
                model_tokens = set(re.findall(r"[a-z0-9]+", p.get("model", "").lower()))
                if model_tokens and model_tokens.issubset(spec_tokens):
                    score += 40
            if score > best_score:
                best_score = score
                best_match = p

        if best_match is not None:
            prof = dict(best_match)
        else:
            prof["model"] = spec

    if reasoning_spec is not None:
        r_clean = str(reasoning_spec).strip()
        prof["reasoning"] = r_clean.capitalize() if r_clean.lower() in ("low", "medium", "high") else r_clean

    return prof


_WITH_FOLLOWERS = {
    "ai:", "AI:", "subagent:", "SUBAGENT:", "(ai)", "(subagent)",
    "with-model", "with-reasoning", "with-instruction", "with-tools",
}


def set_pending_turn_option(vm, key: str) -> None:
    """Parse and store a temporary turn option from TIB or data stack for with-* words."""
    rem = (vm.input.remaining if getattr(vm, "input", None) else "").lstrip()
    next_tok = rem.split(None, 1)[0] if rem else ""
    if (not next_tok or next_tok in _WITH_FOLLOWERS) and vm.dstack:
        val = vm.pop()
    elif next_tok:
        val = (vm.input.read() or "").strip()
    elif vm.dstack:
        val = vm.pop()
    else:
        raise RuntimeError(f"with-{key} expects a value in input or on the stack")

    if isinstance(val, str):
        val = val.strip()
    opts = vm.host.setdefault("ai_pending_turn_options", {})
    opts[key] = val


def _http_chat_stream(base_url, api_key, model, messages, tools, reasoning_effort=None):
    """Send streaming Chat Completion request to OpenAI-compatible endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if tools:
        payload["tools"] = tools

    # Automatically set reasoning_effort to "none" for reasoning models when using tools
    if reasoning_effort is None:
        reasoning_effort = os.environ.get("OPENAI_REASONING_EFFORT")
    if reasoning_effort is None:
        if any(prefix in model.lower() for prefix in ("o1", "o3", "gpt-6")):
            reasoning_effort = "none"
    if reasoning_effort:
        payload["reasoning_effort"] = (
            reasoning_effort.lower()
            if str(reasoning_effort).lower() in ("none", "low", "medium", "high")
            else reasoning_effort
        )

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        return _urlopen_interruptible(req, timeout=60)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        if "reasoning_effort" in err_body:
            if "Unrecognized request argument" in err_body:
                payload.pop("reasoning_effort", None)
            else:
                payload["reasoning_effort"] = "none"
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            return _urlopen_interruptible(req, timeout=60)
        raise


AGENTS_TOOLS_DEFINITION = [
    {
        "type": "function",
        "name": tc["function"]["name"],
        "description": tc["function"]["description"],
        "parameters": tc["function"]["parameters"],
    }
    for tc in TOOLS_DEFINITION
]

_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_APPROVAL_MENU_RE = re.compile(
    r"(?:Purpose:\s*Execution of unsafe word[^\n]*\n+Forth action:\n.*?)?"
    r"1\.\s*Allow Once\n2\.\s*Trust this AI task\n3\.\s*Deny this proposal\n4\.\s*Cancel this AI task\n+"
    r"(?:Choose 1-4:\s*\d*\s*)?",
    flags=re.S,
)


def _clean_tool_stdout(stdout_text: str) -> str:
    """Strip ANSI escape codes and interactive security approval menu noise from tool stdout."""
    if not isinstance(stdout_text, str) or not stdout_text:
        return ""
    cleaned = _ANSI_ESCAPE_RE.sub("", stdout_text)
    cleaned = _APPROVAL_MENU_RE.sub("", cleaned)
    return cleaned.strip()


def distill_messages_for_promotion(messages: list) -> dict:
    """Clean and distill local in-memory messages for promotion to a remote Agents API session.

    Removes:
    - system prompt (sent separately via agent.instructions)
    - dictionary/session lookup dumps (peforth_search_words, peforth_search_sessions)
    - failed peforth_run_forth attempts and approval menu ANSI noise
    - base64 image data URIs
    """
    messages = messages or []
    raw_chars = len(json.dumps(messages, ensure_ascii=False))

    tool_results_by_id = {}
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "tool" and msg.get("tool_call_id"):
            tool_results_by_id[msg["tool_call_id"]] = msg.get("content", "")

    entries = []
    user_turns = 0
    assistant_replies = 0
    kept_tool_calls = 0
    removed_noise_items = 0

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if role == "system":
            removed_noise_items += 1
            continue
        if role == "tool":
            # Handled alongside assistant tool_calls
            continue
        if role == "user":
            content = msg.get("content")
            if isinstance(content, str):
                text = content.strip()
            elif isinstance(content, list):
                parts = []
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text" and part.get("text"):
                            parts.append(str(part["text"]).strip())
                        elif part.get("type") == "image_url":
                            parts.append("[Image attached]")
                            removed_noise_items += 1
                text = " ".join(p for p in parts if p)
            else:
                text = str(content or "").strip()
            if text:
                entries.append(f"User: {text}")
                user_turns += 1
        elif role == "assistant":
            tool_calls = msg.get("tool_calls") or []
            for tc in tool_calls:
                if not isinstance(tc, dict):
                    continue
                call_id = tc.get("id", "")
                fn = tc.get("function") or {}
                fn_name = fn.get("name", "")
                args_str = fn.get("arguments", "{}")
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else (args_str or {})
                except Exception:
                    args = {}

                if fn_name in ("peforth_search_words", "peforth_search_sessions", "peforth_read_skill"):
                    removed_noise_items += 1
                    continue

                if fn_name == "peforth_run_forth":
                    raw_res = tool_results_by_id.get(call_id, "{}")
                    try:
                        res_obj = json.loads(raw_res) if isinstance(raw_res, str) else (raw_res or {})
                    except Exception:
                        res_obj = {}
                    if not isinstance(res_obj, dict) or res_obj.get("error"):
                        removed_noise_items += 1
                        continue
                    purpose = str(args.get("purpose") or "").strip()
                    source = str(args.get("source") or "").strip()
                    cleaned_out = _clean_tool_stdout(str(res_obj.get("stdout") or ""))
                    action_line = f"[Executed Forth ({purpose})]:\n{source}" if purpose else f"[Executed Forth]:\n{source}"
                    if cleaned_out:
                        if len(cleaned_out) > 600:
                            cleaned_out = cleaned_out[:600] + "... (truncated)"
                        action_line += f"\nOutput: {cleaned_out}"
                    entries.append(action_line)
                    kept_tool_calls += 1
                else:
                    removed_noise_items += 1

            content = msg.get("content")
            if isinstance(content, str) and content.strip():
                entries.append(f"Assistant: {content.strip()}")
                assistant_replies += 1

    preview_text = "\n\n".join(entries)
    promoted_input = (
        "Below is the distilled conversation context from our current local peforth session:\n\n"
        f"{preview_text}\n\n"
        "Please briefly acknowledge that you have received this prior context and are ready to continue."
    ) if preview_text else ""

    return {
        "user_turns": user_turns,
        "assistant_replies": assistant_replies,
        "kept_tool_calls": kept_tool_calls,
        "removed_noise_items": removed_noise_items,
        "raw_chars": raw_chars,
        "distilled_chars": len(preview_text),
        "preview_text": preview_text,
        "promoted_input": promoted_input,
    }


def _session_id_from_event(event: dict) -> str | None:
    if not isinstance(event, dict):
        return None
    session = event.get("session") or event.get("data") or {}
    if isinstance(session, dict):
        sid = session.get("id") or session.get("session_id")
        if sid:
            return str(sid)
    sid = event.get("session_id")
    return str(sid) if sid else None


def _agents_event_stream(response):
    """Yield decoded JSON events from an OpenAI Agents API SSE response."""
    data_lines = []
    event_name = None
    try:
        for raw in _iter_response_lines(response):
            raw_bytes = raw if isinstance(raw, bytes) else str(raw).encode("utf-8")
            line = raw_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
            if line.startswith(":"):
                continue
            elif line.startswith("event:"):
                event_name = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
            elif not line:
                if data_lines:
                    joined = "\n".join(data_lines)
                    data_lines.clear()
                    if joined == "[DONE]":
                        event_name = None
                        break
                    try:
                        event = json.loads(joined)
                        if isinstance(event, dict) and event_name and "type" not in event:
                            event["type"] = event_name
                        yield event
                    except json.JSONDecodeError:
                        pass
                event_name = None
        if data_lines:
            joined = "\n".join(data_lines)
            if joined != "[DONE]":
                try:
                    event = json.loads(joined)
                    if isinstance(event, dict) and event_name and "type" not in event:
                        event["type"] = event_name
                    yield event
                except json.JSONDecodeError:
                    pass
    finally:
        try:
            response.close()
        except Exception:
            pass


def _wait_for_current_actions(session_id: str, attempts: int = 3):
    """Fetch current session status and required_actions from Agents API."""
    encoded_id = urllib.parse.quote(session_id, safe="")
    status, actions = None, []
    for attempt in range(max(1, attempts)):
        session = _api_get(f"/sessions/{encoded_id}")
        status = session.get("status")
        actions = session.get("required_actions") or []
        if status == "requires_action" and actions:
            return status, actions
        if status not in {"in_progress", "requires_action"}:
            return status, actions
        if attempt + 1 < attempts:
            time.sleep(0.5)
    return status, actions


def _submit_agents_tool_result(session_id: str, turn_id: str, call_id: str, success: bool, result_text: str):
    """Submit a tool execution result back to an active Agents API session."""
    encoded_id = urllib.parse.quote(session_id, safe="")
    event = {
        "type": "agent.session.input.tool_result",
        "turn_id": turn_id,
        "call_id": call_id,
        "success": bool(success),
    }
    event["output" if success else "error"] = result_text
    with _api_request("POST", f"/sessions/{encoded_id}/events", payload={"events": [event]}, timeout=60) as resp:
        resp.read()


def _chat_turn_width() -> int:
    return max(24, min(shutil.get_terminal_size((80, 24)).columns, 100))


def _chat_turn_header(role: str, provider_info: dict = None) -> str:
    try:
        from wcwidth import wcswidth
    except ImportError:
        def wcswidth(s):
            return len(s)

    width = _chat_turn_width()
    if role == "user":
        title = chr(0x1F44B) + " user"
        prefix = "╭─ " + title + " "
        suffix = "──╮"
        dashes = max(1, width - wcswidth(prefix) - wcswidth(suffix))
        return prefix + "─" * dashes + suffix
    elif role in ("assistant", "subagent"):
        title = (chr(0x1FA84) + " Subagent") if role == "subagent" else (chr(0x1FA84) + " peforth")
        prefix = "╭─ " + title + " "
        if provider_info:
            p_name = provider_info.get("provider", "OpenAI")
            m_name = provider_info.get("model", "")
            r_level = provider_info.get("reasoning", "")
            parts = [str(p_name)]
            if m_name:
                parts.append(str(m_name))
            if r_level and str(r_level).lower() != "none":
                parts.append(str(r_level).capitalize() if str(r_level).lower() in ("low", "medium", "high") else str(r_level))
            meta_str = " │ ".join(parts)
            suffix = f" {meta_str} ──╮"
        else:
            suffix = "──╮"
        dashes = max(1, width - wcswidth(prefix) - wcswidth(suffix))
        return prefix + "─" * dashes + suffix
    else:
        raise ValueError("role must be user, assistant, or subagent")


def _chat_turn_bottom(timestamp: str = None) -> str:
    try:
        from wcwidth import wcswidth
    except ImportError:
        def wcswidth(s):
            return len(s)

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    width = _chat_turn_width()
    prefix = "╰"
    suffix = f" {timestamp} ──╯"
    dashes = max(1, width - wcswidth(prefix) - wcswidth(suffix))
    return prefix + "─" * dashes + suffix


def _print_chat_turn(role: str, text: str, provider_info: dict = None) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    sys.stdout.write(_chat_turn_header(role, provider_info) + "\n")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for line in normalized.split("\n"):
        sys.stdout.write("  " + line + "\n")
    sys.stdout.write(_chat_turn_bottom() + "\n")
    sys.stdout.flush()


class ChatBoxStreamer:
    """Manages styled chat turn output frames for terminal interactions."""

    def __init__(self, stream_response: bool = True, provider_info: dict = None, role: str = "assistant"):
        self.stream_response = stream_response
        self.provider_info = provider_info or {}
        self.role = role
        self.box_open = False
        self.line_start = True
        if self.stream_response and hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    def print_user_turn(self, prompt: str) -> None:
        if not self.stream_response or not prompt or not prompt.strip():
            return
        _print_chat_turn("user", prompt.strip())

    def write_chunk(self, chunk: str) -> None:
        if not self.stream_response or not chunk:
            return
        if not self.box_open:
            sys.stdout.write("\n" + _chat_turn_header(self.role, self.provider_info) + "\n")
            self.box_open = True
            self.line_start = True

        for part in chunk.splitlines(keepends=True):
            if self.line_start:
                sys.stdout.write("  ")
            sys.stdout.write(part)
            self.line_start = part.endswith("\n") or part.endswith("\r")
        sys.stdout.flush()

    def close_box(self) -> None:
        if not self.stream_response or not self.box_open:
            return
        if not self.line_start:
            sys.stdout.write("\n")
        sys.stdout.write(_chat_turn_bottom() + "\n")
        sys.stdout.flush()
        self.box_open = False
        self.line_start = True


def ai_turn_stateful(vm, prompt, stream_response, *, session_id=None, create_new=False, image_url=None, isolated_session=False, options=None):
    """Cooperative generator for one Stateful AI turn via the OpenAI Agents API (/v1/agents/sessions)."""
    init_diagnostics(vm)
    load_dotenv()
    opts = dict(options or {})
    stateful_cfg = get_stateful_config(vm)
    key_env = stateful_cfg.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(key_env, "").strip()
    model = (opts.get("model") or vm.host.get("ai_stateful_model") or stateful_cfg.get("model") or os.environ.get("OPENAI_MODEL", "gpt-6-luna")).strip()
    reasoning_effort = opts.get("reasoning") or vm.host.get("ai_stateful_reasoning") or "none"

    if not api_key:
        msg = (
            f"\n[AI] {key_env} is not set.\n"
            f"Please configure {key_env} in your environment or in a .env file.\n"
        )
        if stream_response:
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            vm.push(msg)
        return

    system_instructions = str(opts["instruction"]) if opts.get("instruction") else get_system_prompt(vm)
    active_tools = [] if isolated_session else _resolve_tools_list(AGENTS_TOOLS_DEFINITION, opts.get("tools"))
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    turn_id = None
    if logger is not None and runtime_id is not None:
        try:
            prompt_cid = logger.store_content("prompt", prompt)
            instr_cid = logger.store_content("agent_instructions", system_instructions)
            turn_id = logger.start_turn(
                runtime_id,
                prompt_content_id=prompt_cid,
                instructions_content_id=instr_cid,
                remote_session_id=session_id,
            )
            vm.host["ai_current_turn_id"] = turn_id
            logger.append_event(
                runtime_id, turn_id, "ai_turn_started",
                session_id=session_id,
                payload={"model": model, "stream_response": bool(stream_response), "mode": "stateful"},
            )
        except Exception:
            turn_id = None

    user_content = [{"type": "input_text", "text": prompt}]
    if image_url is not None:
        user_content.append({"type": "input_image", "image_url": image_url})

    accumulated_full_text = []
    remote_turn_id = None
    stateful_cfg = get_stateful_config(vm)
    provider_info = {
        "provider": stateful_cfg.get("provider", "OpenAI"),
        "model": model,
        "reasoning": reasoning_effort,
    }
    streamer = ChatBoxStreamer(stream_response, provider_info=provider_info)
    streamer.print_user_turn(prompt)

    try:
        if create_new or not session_id:
            payload = {
                "agent": {
                    "model": model,
                    "tools": active_tools,
                    "instructions": system_instructions,
                },
                "environment": {"type": "none"},
                "input": [{"role": "user", "content": user_content}] if image_url is not None else prompt,
                "stream": True,
            }
            _log_event(vm, "http_request_started", turn_id=turn_id,
                       http_method="POST", url="/agents/sessions", payload={"model": model})
            response = _api_request("POST", "/sessions", payload=payload, stream=True, timeout=300)
        else:
            encoded_id = urllib.parse.quote(session_id, safe="")
            message_event = {
                "type": "agent.session.input.message",
                "input": [{"role": "user", "content": user_content}],
            }
            _log_event(vm, "http_request_started", turn_id=turn_id,
                       http_method="POST", url=f"/agents/sessions/{encoded_id}/events",
                       payload={"model": model, "session_id": session_id})
            with _api_request("POST", f"/sessions/{encoded_id}/events", payload={"events": [message_event]}, timeout=60) as post_resp:
                post_resp.read()
            _log_event(vm, "http_request_started", turn_id=turn_id,
                       http_method="GET", url=f"/agents/sessions/{encoded_id}/events?stream=true",
                       payload={"model": model, "session_id": session_id})
            response = _api_request("GET", f"/sessions/{encoded_id}/events?stream=true", stream=True, timeout=300)

        _log_event(vm, "sse_stream_opened", turn_id=turn_id)
        for event in _agents_event_stream(response):
            if not isinstance(event, dict):
                continue
            ev_turn_id = event.get("turn_id")
            if not ev_turn_id and isinstance(event.get("turn"), dict):
                ev_turn_id = event["turn"].get("id")
            if isinstance(ev_turn_id, str) and ev_turn_id:
                remote_turn_id = ev_turn_id

            if not session_id:
                discovered_id = _session_id_from_event(event)
                if discovered_id:
                    session_id = discovered_id
                    if not isolated_session:
                        vm.host["ai_active_session_id"] = session_id
                    if logger is not None and turn_id is not None:
                        try:
                            logger.set_turn_session(turn_id, session_id)
                        except Exception:
                            pass

            kind = event.get("type", "")
            if kind == "agent.session.turn.output_text.delta":
                delta_text = event.get("delta", "")
                if delta_text:
                    accumulated_full_text.append(delta_text)
                    streamer.write_chunk(delta_text)
            elif kind == "agent.session.turn.output_text.done":
                done_text = event.get("text", "")
                if done_text and not accumulated_full_text:
                    accumulated_full_text.append(done_text)
                    streamer.write_chunk(done_text)
            elif kind == "agent.session.requires_action":
                streamer.close_box()
                if not session_id:
                    continue
                status, actions = _wait_for_current_actions(session_id)
                if status != "requires_action" or not actions:
                    continue
                for action in actions:
                    if not isinstance(action, dict):
                        continue
                    act_turn_id = action.get("turn_id") or remote_turn_id or ""
                    call_id = action.get("call_id") or ""
                    fn_name = action.get("name") or ""
                    raw_args = action.get("arguments", "{}")
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                    except Exception:
                        args = {}

                    _log_event(vm, "tool_call_started", turn_id=turn_id,
                               call_id=call_id, operation=fn_name,
                               payload={"arguments": raw_args})

                    if fn_name == "peforth_search_words":
                        query = args.get("query", "")
                        if stream_response:
                            sys.stdout.write(f"\n[AI Tool] Searching dictionary for: {query!r}...\n")
                            sys.stdout.flush()
                        result_data = tool_search_words(vm, query)
                        _submit_agents_tool_result(
                            session_id, act_turn_id, call_id, True,
                            json.dumps(result_data, ensure_ascii=False),
                        )
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "switch_provider":
                        target = args.get("provider_or_model", "")
                        r_level = args.get("reasoning")
                        ok, msg = apply_stateless_provider(vm, target, reasoning=r_level)
                        if ok:
                            streamer.provider_info = get_active_provider_info(vm)
                        if stream_response:
                            sys.stdout.write(f"\n{msg}\n")
                            sys.stdout.flush()
                        _submit_agents_tool_result(
                            session_id, act_turn_id, call_id, ok,
                            json.dumps({"success": ok, "message": msg}, ensure_ascii=False),
                        )
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "peforth_search_sessions":
                        session_query = args.get("query")
                        target_session_id = args.get("session_id")
                        result_limit = args.get("limit", 20)
                        try:
                            exec_result = query_local_sessions(
                                query=session_query,
                                session_id=target_session_id,
                                limit=result_limit,
                            )
                            _submit_agents_tool_result(
                                session_id, act_turn_id, call_id, True,
                                json.dumps(exec_result, ensure_ascii=False),
                            )
                        except Exception as e:
                            _submit_agents_tool_result(
                                session_id, act_turn_id, call_id, False,
                                f"{type(e).__name__}: {e}",
                            )
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "peforth_read_skill":
                        skill_name = args.get("skill_name", "")
                        file_path = args.get("file_path")
                        if stream_response:
                            target_disp = f"{skill_name}/{file_path}" if file_path else skill_name
                            sys.stdout.write(f"\n[AI Tool] Reading skill: {target_disp}...\n")
                            sys.stdout.flush()
                        result_data = tool_read_skill(vm, skill_name, file_path)
                        _submit_agents_tool_result(
                            session_id, act_turn_id, call_id, True,
                            json.dumps(result_data, ensure_ascii=False),
                        )
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "peforth_run_forth":
                        source = normalize_forth_source(args.get("source", ""))
                        purpose = args.get("purpose", "")
                        if stream_response:
                            sys.stdout.write(
                                f"\n{_ANSI_GREEN_BOLD}[AI Proposes Forth Code]{_ANSI_RESET}\n"
                                f"{_ANSI_DEEP_GREEN}Purpose: {purpose}\n"
                                f"Source:\n"
                                f"{source.strip()}{_ANSI_RESET}\n\n"
                            )
                            sys.stdout.flush()

                        prev_ai_task = vm.host.get("in_ai_task")
                        prev_base_depth = vm.host.get("ai_task_base_frame_depth")
                        vm.host["in_ai_task"] = vm.task
                        vm.host["ai_task_base_frame_depth"] = len(getattr(vm.task, "frames", []))

                        tee = TeeOutput(sys.stdout)
                        old_stdout = sys.stdout
                        error_msg = None
                        _log_event(vm, "forth_execution_started", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name,
                                   payload={"purpose": purpose, "source": source})
                        try:
                            sys.stdout = tee
                            yield from vm.evaluate(source)
                        except Exception as e:
                            error_msg = f"{type(e).__name__}: {e}"
                            sys.__stdout__.write(f"\n[Execution Error] {error_msg}\n")
                            sys.__stdout__.flush()
                        finally:
                            sys.stdout = old_stdout
                            vm.host["in_ai_task"] = prev_ai_task
                            if prev_base_depth is None:
                                vm.host.pop("ai_task_base_frame_depth", None)
                            else:
                                vm.host["ai_task_base_frame_depth"] = prev_base_depth
                            _log_event(vm, "forth_execution_finished", turn_id=turn_id,
                                       call_id=call_id, operation=fn_name,
                                       payload={"stdout": tee.getvalue(), "error": error_msg})

                        exec_result = {
                            "stdout": tee.getvalue(),
                            "dstack": [repr(x) for x in vm.dstack],
                            "error": error_msg,
                        }
                        _submit_agents_tool_result(
                            session_id, act_turn_id, call_id, True,
                            json.dumps(exec_result, ensure_ascii=False),
                        )
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)
                    else:
                        _submit_agents_tool_result(
                            session_id, act_turn_id, call_id, False,
                            f"Unknown tool: {fn_name}",
                        )
            elif kind in ("error", "agent.session.failed", "agent.session.turn.failed", "agent.session.turn.cancelled"):
                detail = event.get("error") or event.get("turn", {}).get("error") or event
                raise RuntimeError(f"Agents API {kind}: {detail}")
            elif kind == "agent.session.turn.completed":
                break

        _log_event(vm, "sse_stream_completed", turn_id=turn_id)
    except KeyboardInterrupt as e:
        streamer.close_box()
        trusted_tasks = vm.host.get("trusted_ai_tasks")
        if trusted_tasks and vm.task in trusted_tasks:
            trusted_tasks.remove(vm.task)
        vm.host["pending_ai_task"] = None
        _finish_turn(
            vm, turn_id,
            output_text="".join(accumulated_full_text) if accumulated_full_text else None,
            output_status="partial" if accumulated_full_text else "empty",
            status="cancelled", error=e,
        )
        vm.host["ai_current_turn_id"] = None
        raise
    except Exception as e:
        _log_event(vm, "sse_stream_failed", turn_id=turn_id, error=e)
        _finish_turn(
            vm, turn_id,
            output_text="".join(accumulated_full_text) if accumulated_full_text else None,
            output_status="partial" if accumulated_full_text else "failed_before_output",
            status="failed", error=e,
        )
        vm.host["ai_current_turn_id"] = None
        err_msg = f"\n[AI Error] Agents API request failed: {e}\n"
        if stream_response:
            sys.stdout.write(err_msg)
            sys.stdout.flush()
        else:
            vm.push(err_msg)
        return

    trusted_tasks = vm.host.get("trusted_ai_tasks")
    if trusted_tasks and vm.task in trusted_tasks:
        trusted_tasks.remove(vm.task)
    vm.host["pending_ai_task"] = None

    full_output = "".join(accumulated_full_text)
    streamer.close_box()
    _finish_turn(
        vm, turn_id,
        output_text=full_output if full_output else None,
        output_status="complete" if full_output else "empty",
        status="completed",
    )
    vm.host["ai_current_turn_id"] = None

    if not stream_response:
        vm.push(full_output)


def promote_local_session(vm):
    """Distill current local in-memory messages, ask user for approval, and promote to a new remote Agents API session."""
    active_id = vm.host.get("ai_active_session_id")
    messages = vm.host.get("ai_messages") or []
    user_turns = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]

    if active_id and not user_turns:
        print(f"Already in Stateful mode with remote session: {active_id}")
        return

    if not user_turns:
        print("No local conversation context to promote. Start chatting with ai: first.")
        return

    distilled = distill_messages_for_promotion(messages)
    print("\n=== Distilled Context for Remote Promotion ===")
    print(
        f"Turns: {distilled['user_turns']} user turn(s), "
        f"{distilled['assistant_replies']} assistant reply(ies), "
        f"{distilled['kept_tool_calls']} executed Forth action(s)"
    )
    print(
        f"Removed noise: {distilled['removed_noise_items']} item(s) "
        f"({distilled['raw_chars']} raw chars -> {distilled['distilled_chars']} distilled chars)"
    )
    print("-" * 46)
    print(distilled["preview_text"])
    print("-" * 46)

    choice = read_numbered_choice(
        "Choose 1-2: ",
        choices=("1", "2"),
        default="1",
        labels={
            "1": "Promote to new remote Agents API session",
            "2": "Cancel (keep local Stateless conversation)",
        },
    )
    if choice != "1":
        print("Promotion cancelled. Remaining in local Stateless mode.")
        return

    old_local_id = vm.host.get("ai_local_session_id") or _ensure_local_session_id(vm)
    print("\nPromoting context to a new remote Agents API session...")
    yield from ai_turn_stateful(
        vm,
        distilled["promoted_input"],
        stream_response=True,
        create_new=True,
    )
    new_session_id = vm.host.get("ai_active_session_id")
    if new_session_id:
        vm.host.pop("ai_messages", None)
        vm.host.pop("ai_local_session_id", None)
        _log_event(
            vm,
            "ai_session_promoted",
            session_id=new_session_id,
            payload={
                "from_local_session_id": old_local_id,
                "to_remote_session_id": new_session_id,
            },
        )
        print(f"Promoted local conversation to remote session: {new_session_id}")



def ai_subagent_turn(vm, prompt, stream_response, *, options=None):
    """Execute an isolated, one-shot Sub-agent turn.

    Sub-agents run with an independent context, leaving the mainstream conversation
    history (ai_messages / ai_active_session_id) completely untouched.
    """
    pending_opts = vm.host.pop("ai_pending_turn_options", None) or {}
    merged_opts = dict(pending_opts)
    if isinstance(options, dict):
        merged_opts.update(options)
    yield from _stateless_turn_loop(
        vm,
        prompt,
        stream_response,
        options=merged_opts,
        is_subagent=True,
    )


def ai_turn(vm, prompt, stream_response):
    """Cooperative generator for one AI conversation turn.

    Routes to Stateful OpenAI Agents API mode if vm.host['ai_active_session_id']
    is set (unless ai_isolated_session_once is set), or defaults to Stateless
    /chat/completions mode using vm.host['ai_messages'].
    Automatically routes re-entrant calls inside an AI tool task (in_ai_task)
    to ai_subagent_turn to prevent deadlocks and HTTP 409 Conflicts.
    """
    if vm.host.get("in_ai_task"):
        pending_opts = vm.host.pop("ai_pending_turn_options", None)
        yield from ai_subagent_turn(vm, prompt, stream_response, options=pending_opts)
        return

    pending_opts = vm.host.pop("ai_pending_turn_options", None) or {}
    active_session_id = vm.host.get("ai_active_session_id")
    if active_session_id and not vm.host.get("ai_isolated_session_once", False):
        if pending_opts.get("model"):
            cand_prof = resolve_profile_override(
                vm, get_active_stateless_profile(vm), model_spec=pending_opts["model"]
            )
            if not _is_stateful_compatible_profile(vm, cand_prof):
                cur_info = get_active_provider_info(vm)
                refusal = (
                    f"\n[Provider Refused] Cannot run a mainstream 'ai:' turn on Stateless-only provider "
                    f"'{cand_prof.get('provider')} | {cand_prof.get('model')}' while in Stateful mode "
                    f"(active remote session: {active_session_id}, provider: {cur_info.get('provider')} | {cur_info.get('model')}).\n"
                    f"Guidance:\n"
                    f"  1. For a one-shot task using '{cand_prof.get('provider')} | {cand_prof.get('model')}' without leaving Stateful mode, use:\n"
                    f"     with-model {pending_opts['model']} subagent: <prompt>\n"
                    f"  2. To exit Stateful mode and return to local Stateless mode first, run:\n"
                    f"     ai-new\n"
                )
                if stream_response:
                    sys.stdout.write(refusal)
                    sys.stdout.flush()
                else:
                    vm.push(refusal.strip())
                return

        image_url = vm.host.pop("ai_image_url_once", None)
        isolated_session = vm.host.pop("ai_isolated_session_once", False)
        stateful_kwargs = {
            "session_id": active_session_id,
            "image_url": image_url,
            "isolated_session": isolated_session,
        }
        if pending_opts:
            stateful_kwargs["options"] = pending_opts
        yield from ai_turn_stateful(
            vm,
            prompt,
            stream_response,
            **stateful_kwargs,
        )
        return

    yield from _stateless_turn_loop(
        vm,
        prompt,
        stream_response,
        options=pending_opts,
        is_subagent=False,
    )


def _stateless_turn_loop(vm, prompt, stream_response, *, options=None, is_subagent=False):
    """Core Stateless /chat/completions turn engine supporting both Mainstream and Sub-agent turns."""
    init_diagnostics(vm)
    load_dotenv()
    opts = dict(options or {})
    base_prof = get_active_stateless_profile(vm)
    prof = resolve_profile_override(
        vm,
        base_prof,
        model_spec=opts.get("model"),
        reasoning_spec=opts.get("reasoning"),
    )
    p_name = prof.get("provider", "OpenAI")
    base_url = prof.get("endpoint", "https://api.openai.com/v1").strip()
    model = (prof.get("model") or "gpt-4o-mini").strip()
    reasoning_effort = prof.get("reasoning")
    api_key_env = prof.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(api_key_env, "").strip()

    if not api_key and api_key_env != "OLLAMA_API_KEY":
        msg = (f"\n[AI] API key '{api_key_env}' is not set for provider '{p_name}'.\n"
               f"Please configure {api_key_env} in your environment or in a .env file.\n"
               f"Example: export {api_key_env}=\"sk-...\"\n")
        if stream_response:
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            vm.push(msg)
        return

    image_url = opts.get("image_url") or vm.host.pop("ai_image_url_once", None)
    isolated_session = is_subagent or bool(opts.get("isolated_session")) or vm.host.pop("ai_isolated_session_once", False)
    if is_subagent:
        diag_session_id = f"subagent_{uuid.uuid4().hex[:16]}"
    elif isolated_session:
        diag_session_id = f"isolated_{uuid.uuid4().hex[:16]}"
    else:
        diag_session_id = _ensure_local_session_id(vm)

    # Start diagnostic turn tracking if enabled
    system_instructions = str(opts["instruction"]) if opts.get("instruction") else get_system_prompt(vm)
    active_tools = _resolve_tools_list(TOOLS_DEFINITION, opts.get("tools"))
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    parent_turn_id = vm.host.get("ai_current_turn_id")
    turn_id = None
    if logger is not None and runtime_id is not None:
        try:
            prompt_cid = logger.store_content("prompt", prompt)
            instr_cid = logger.store_content("agent_instructions", system_instructions)
            if is_subagent:
                turn_meta = {
                    "kind": "subagent",
                    "parent_turn_id": parent_turn_id,
                    "model": model,
                    "provider": p_name,
                }
                if opts.get("tools") is not None:
                    turn_meta["tools"] = [t.get("function", {}).get("name") for t in active_tools]
                meta_json = json.dumps(turn_meta, ensure_ascii=False)
            elif opts:
                meta_json = json.dumps(
                    {"kind": "mainstream", "model": model, "provider": p_name},
                    ensure_ascii=False,
                )
            else:
                meta_json = None

            turn_id = logger.start_turn(
                runtime_id,
                prompt_content_id=prompt_cid,
                instructions_content_id=instr_cid,
                remote_session_id=diag_session_id,
                metadata_json=meta_json,
            )
            vm.host["ai_current_turn_id"] = turn_id
            if is_subagent:
                if parent_turn_id is not None:
                    logger.append_event(
                        runtime_id, parent_turn_id, "subagent_invoked",
                        session_id=_current_diagnostic_session_id(vm),
                        payload={
                            "subagent_turn_id": turn_id,
                            "model": model,
                            "provider": p_name,
                            "prompt": prompt[:200],
                        },
                    )
                logger.append_event(
                    runtime_id, turn_id, "subagent_turn_started",
                    session_id=diag_session_id,
                    payload={
                        "parent_turn_id": parent_turn_id,
                        "model": model,
                        "provider": p_name,
                        "stream_response": bool(stream_response),
                        "mode": "subagent",
                    },
                )
            else:
                logger.append_event(
                    runtime_id, turn_id, "ai_turn_started",
                    session_id=diag_session_id,
                    payload={"model": model, "stream_response": bool(stream_response)},
                )
        except Exception:
            turn_id = None

    if image_url is not None:
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
    else:
        user_content = prompt

    if isolated_session:
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_content},
        ]
    else:
        messages = vm.host.setdefault("ai_messages", [
            {"role": "system", "content": system_instructions}
        ])
        messages = _sanitize_messages(messages)
        messages.append({"role": "user", "content": user_content})
        vm.host["ai_messages"] = messages

    accumulated_full_text = []
    if opts.get("model") or opts.get("reasoning") or is_subagent:
        provider_info = {
            "provider": p_name,
            "model": model,
            "reasoning": reasoning_effort or "none",
        }
    else:
        provider_info = get_active_provider_info(vm)
    streamer = ChatBoxStreamer(
        stream_response,
        provider_info=provider_info,
        role="subagent" if is_subagent else "assistant",
    )
    streamer.print_user_turn(prompt)

    def _restore_turn_id():
        vm.host["ai_current_turn_id"] = parent_turn_id if is_subagent else None

    def _log_subagent_end(failed_error=None):
        if not is_subagent or logger is None or runtime_id is None or turn_id is None:
            return
        try:
            if failed_error is not None:
                logger.append_event(
                    runtime_id, turn_id, "subagent_turn_failed",
                    session_id=diag_session_id,
                    payload={"parent_turn_id": parent_turn_id, "model": model},
                    error_type=type(failed_error).__name__,
                    error_message=str(failed_error),
                )
            else:
                logger.append_event(
                    runtime_id, turn_id, "subagent_turn_completed",
                    session_id=diag_session_id,
                    payload={"parent_turn_id": parent_turn_id, "model": model},
                )
            if parent_turn_id is not None:
                logger.append_event(
                    runtime_id, parent_turn_id, "subagent_completed",
                    session_id=_current_diagnostic_session_id(vm),
                    payload={
                        "subagent_turn_id": turn_id,
                        "model": model,
                        "status": "failed" if failed_error is not None else "completed",
                    },
                )
        except Exception:
            pass

    # Outer loop for handling multi-turn tool calling
    assistant_content = ""
    try:
        while True:
            t0 = time.monotonic()
            req_url = f"{base_url.rstrip('/')}/chat/completions"
            _log_event(vm, "http_request_started", turn_id=turn_id,
                       http_method="POST", url=req_url, payload={"model": model})
            try:
                if opts.get("reasoning") is not None:
                    try:
                        response = _http_chat_stream(
                            base_url, api_key, model, messages, active_tools,
                            reasoning_effort=reasoning_effort,
                        )
                    except TypeError:
                        response = _http_chat_stream(base_url, api_key, model, messages, active_tools)
                else:
                    response = _http_chat_stream(base_url, api_key, model, messages, active_tools)
                elapsed_ms = (time.monotonic() - t0) * 1000.0
                http_status = getattr(response, "status", 200)
                _log_event(vm, "http_response_received", turn_id=turn_id,
                           http_status=http_status, elapsed_ms=elapsed_ms)
            except urllib.error.HTTPError as e:
                elapsed_ms = (time.monotonic() - t0) * 1000.0
                _log_event(vm, "http_request_failed", turn_id=turn_id,
                           http_status=e.code, elapsed_ms=elapsed_ms, error=e)
                _log_subagent_end(failed_error=e)
                _finish_turn(vm, turn_id,
                             output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                             output_status="partial" if accumulated_full_text else "failed_before_output",
                             status="failed", error=e)
                _restore_turn_id()
                err_body = e.read().decode("utf-8", errors="replace")
                err_msg = f"\n[AI Error] HTTP {e.code}: {err_body}\n"
                if stream_response:
                    sys.stdout.write(err_msg)
                    sys.stdout.flush()
                else:
                    vm.push(err_msg)
                return
            except Exception as e:
                elapsed_ms = (time.monotonic() - t0) * 1000.0
                _log_event(vm, "http_request_failed", turn_id=turn_id,
                           elapsed_ms=elapsed_ms, error=e)
                _log_subagent_end(failed_error=e)
                _finish_turn(vm, turn_id,
                             output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                             output_status="partial" if accumulated_full_text else "failed_before_output",
                             status="failed", error=e)
                _restore_turn_id()
                err_msg = f"\n[AI Error] Network request failed: {e}\n"
                if stream_response:
                    sys.stdout.write(err_msg)
                    sys.stdout.flush()
                else:
                    vm.push(err_msg)
                return

            assistant_content = ""
            tool_calls_map = {}  # index -> {id, name, arguments}

            _log_event(vm, "sse_stream_opened", turn_id=turn_id)
            first_chunk_logged = False
            try:
                with response:
                    for raw_line in _iter_response_lines(response):
                        line = raw_line.decode("utf-8").strip()
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        if not first_chunk_logged:
                            _log_event(vm, "sse_event_received", turn_id=turn_id)
                            first_chunk_logged = True

                        choices = chunk.get("choices", [])
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {})

                        # Text streaming
                        content_chunk = delta.get("content")
                        if content_chunk:
                            assistant_content += content_chunk
                            streamer.write_chunk(content_chunk)

                        # Tool calls streaming
                        if "tool_calls" in delta:
                            for tc in delta["tool_calls"]:
                                idx = tc.get("index", 0)
                                if idx not in tool_calls_map:
                                    tool_calls_map[idx] = {
                                        "id": "",
                                        "name": "",
                                        "arguments": ""
                                    }
                                if tc.get("id"):
                                    tool_calls_map[idx]["id"] += tc["id"]
                                fn = tc.get("function", {})
                                if fn.get("name"):
                                    tool_calls_map[idx]["name"] += fn["name"]
                                if fn.get("arguments"):
                                    tool_calls_map[idx]["arguments"] += fn["arguments"]
                _log_event(vm, "sse_stream_completed", turn_id=turn_id)
            except Exception as e:
                _log_event(vm, "sse_stream_failed", turn_id=turn_id, error=e)
                _log_subagent_end(failed_error=e)
                _finish_turn(vm, turn_id,
                             output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                             output_status="partial" if accumulated_full_text else "failed_before_output",
                             status="failed", error=e)
                _restore_turn_id()
                raise

            if assistant_content:
                accumulated_full_text.append(assistant_content)

            # Build assistant message object
            assistant_msg = {"role": "assistant"}
            if assistant_content:
                assistant_msg["content"] = assistant_content
            else:
                assistant_msg["content"] = None
            assistant_content = ""

            if tool_calls_map:
                streamer.close_box()
                formatted_tool_calls = []
                for idx in sorted(tool_calls_map.keys()):
                    entry = tool_calls_map[idx]
                    formatted_tool_calls.append({
                        "id": entry["id"] or f"call_{idx}",
                        "type": "function",
                        "function": {
                            "name": entry["name"],
                            "arguments": entry["arguments"],
                        }
                    })
                assistant_msg["tool_calls"] = formatted_tool_calls
                messages.append(assistant_msg)

                # Execute each tool call
                for tc in formatted_tool_calls:
                    call_id = tc["id"]
                    fn_name = tc["function"]["name"]
                    args_str = tc["function"]["arguments"]
                    try:
                        args = json.loads(args_str) if args_str else {}
                    except json.JSONDecodeError:
                        args = {}

                    _log_event(vm, "tool_call_started", turn_id=turn_id,
                               call_id=call_id, operation=fn_name,
                               payload={"arguments": args_str})

                    if fn_name == "peforth_search_words":
                        query = args.get("query", "")
                        if stream_response:
                            sys.stdout.write(f"\n[AI Tool] Searching dictionary for: {query!r}...\n")
                            sys.stdout.flush()
                        result_data = tool_search_words(vm, query)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps(result_data, ensure_ascii=False)
                        })
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "switch_provider":
                        target = args.get("provider_or_model", "")
                        r_level = args.get("reasoning")
                        ok, msg = apply_stateless_provider(vm, target, reasoning=r_level)
                        if ok and not is_subagent:
                            prof = get_active_stateless_profile(vm)
                            p_name = prof.get("provider", "OpenAI")
                            base_url = prof.get("endpoint", "https://api.openai.com/v1").strip()
                            model = (prof.get("model") or "gpt-4o-mini").strip()
                            reasoning_effort = prof.get("reasoning")
                            api_key_env = prof.get("api_key_env", "OPENAI_API_KEY")
                            api_key = os.environ.get(api_key_env, "").strip()
                            streamer.provider_info = get_active_provider_info(vm)
                        if stream_response:
                            sys.stdout.write(f"\n{msg}\n")
                            sys.stdout.flush()
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps({"success": ok, "message": msg}, ensure_ascii=False),
                        })
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "peforth_search_sessions":
                        allowed_arguments = {"query", "session_id", "limit"}
                        if not set(args.keys()).issubset(allowed_arguments):
                            exec_result = {"error": "peforth_search_sessions accepts only query, session_id, and limit."}
                        else:
                            session_query = args.get("query")
                            target_session_id = args.get("session_id")
                            result_limit = args.get("limit", 20)
                            try:
                                if session_query is not None and not isinstance(session_query, str):
                                    raise TypeError("query must be a string")
                                if target_session_id is not None and not isinstance(target_session_id, str):
                                    raise TypeError("session_id must be a string")
                                if isinstance(result_limit, bool) or not isinstance(result_limit, int) or result_limit < 1:
                                    raise ValueError("limit must be a positive integer")
                                exec_result = query_local_sessions(
                                    query=session_query,
                                    session_id=target_session_id,
                                    limit=result_limit,
                                )
                            except Exception as e:
                                exec_result = {"error": f"{type(e).__name__}: {e}"}
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps(exec_result, ensure_ascii=False)
                        })
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "peforth_read_skill":
                        skill_name = args.get("skill_name", "")
                        file_path = args.get("file_path")
                        if stream_response:
                            target_disp = f"{skill_name}/{file_path}" if file_path else skill_name
                            sys.stdout.write(f"\n[AI Tool] Reading skill: {target_disp}...\n")
                            sys.stdout.flush()
                        result_data = tool_read_skill(vm, skill_name, file_path)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps(result_data, ensure_ascii=False)
                        })
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)

                    elif fn_name == "peforth_run_forth":
                        source = normalize_forth_source(args.get("source", ""))
                        purpose = args.get("purpose", "")

                        if stream_response:
                            sys.stdout.write(
                                f"\n{_ANSI_GREEN_BOLD}[AI Proposes Forth Code]{_ANSI_RESET}\n"
                                f"{_ANSI_DEEP_GREEN}Purpose: {purpose}\n"
                                f"Source:\n"
                                f"{source.strip()}{_ANSI_RESET}\n\n"
                            )
                            sys.stdout.flush()

                        # Execute Forth code under AI task context.
                        # Individual words are verified against safe=True in security_aware_call.
                        prev_ai_task = vm.host.get("in_ai_task")
                        prev_base_depth = vm.host.get("ai_task_base_frame_depth")
                        vm.host["in_ai_task"] = vm.task
                        vm.host["ai_task_base_frame_depth"] = len(getattr(vm.task, "frames", []))

                        tee = TeeOutput(sys.stdout)
                        old_stdout = sys.stdout
                        error_msg = None
                        _log_event(vm, "forth_execution_started", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name,
                                   payload={"purpose": purpose, "source": source})
                        try:
                            sys.stdout = tee
                            yield from vm.evaluate(source)
                        except Exception as e:
                            error_msg = f"{type(e).__name__}: {e}"
                            sys.__stdout__.write(f"\n[Execution Error] {error_msg}\n")
                            sys.__stdout__.flush()
                        finally:
                            sys.stdout = old_stdout
                            vm.host["in_ai_task"] = prev_ai_task
                            if prev_base_depth is None:
                                vm.host.pop("ai_task_base_frame_depth", None)
                            else:
                                vm.host["ai_task_base_frame_depth"] = prev_base_depth
                            _log_event(vm, "forth_execution_finished", turn_id=turn_id,
                                       call_id=call_id, operation=fn_name,
                                       payload={"stdout": tee.getvalue(), "error": error_msg})

                        exec_result = {
                            "stdout": tee.getvalue(),
                            "dstack": [repr(x) for x in vm.dstack],
                            "error": error_msg
                        }
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps(exec_result, ensure_ascii=False)
                        })
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps({"error": f"Unknown tool: {fn_name}"})
                        })
                        _log_event(vm, "tool_result_submitted", turn_id=turn_id,
                                   call_id=call_id, operation=fn_name)
                # Continue loop to stream the assistant's follow-up
                continue
            else:
                # No tool calls; turn is complete
                messages.append(assistant_msg)
                break
    except KeyboardInterrupt as e:
        if assistant_content:
            accumulated_full_text.append(assistant_content)
        streamer.close_box()
        trusted_tasks = vm.host.get("trusted_ai_tasks")
        if trusted_tasks and vm.task in trusted_tasks:
            trusted_tasks.remove(vm.task)
        vm.host["pending_ai_task"] = None
        _log_subagent_end(failed_error=e)
        _finish_turn(
            vm, turn_id,
            output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
            output_status="partial" if accumulated_full_text else "empty",
            status="cancelled", error=e,
        )
        _restore_turn_id()
        raise

    # Clean up trusted task status once turn is done
    trusted_tasks = vm.host.get("trusted_ai_tasks")
    if trusted_tasks and vm.task in trusted_tasks:
        trusted_tasks.remove(vm.task)
    vm.host["pending_ai_task"] = None

    streamer.close_box()
    _log_subagent_end()
    _finish_turn(vm, turn_id,
                 output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                 output_status="complete" if accumulated_full_text else "empty",
                 status="completed")
    _restore_turn_id()

    if not stream_response:
        vm.push("\n".join(accumulated_full_text))
