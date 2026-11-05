"""peforth - AI Extension Module (v2.1.0)

Implements:
- Security Guard Decorator for vm.call (Task-level approval scope)
- Tools: peforth_search_words, peforth_run_forth
- (ai) cooperative turn generator with OpenAI-compatible SSE streaming
"""

import atexit
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
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


def _clip(value, limit=_OUTPUT_LIMIT):
    value = value or ""
    return value[:limit], len(value) > limit


def _run_process(argv, input_text=None, timeout=60):
    try:
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
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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
    wsl_fallback = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    if os.path.isfile(wsl_fallback):
        return wsl_fallback
    raise RuntimeError("PowerShell is not available for Windows desktop capture.")


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


def detect_system_info(vm=None) -> dict:
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
    pwsh_path = None
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
            try:
                proc = subprocess.run([wsl_bin, "-l", "-q"], capture_output=True, timeout=5)
                raw = proc.stdout
                text = raw.decode("utf-16-le", errors="ignore") if b"\x00" in raw else raw.decode("utf-8", errors="ignore")
                distros = [line.strip() for line in text.splitlines() if line.strip()]
                if distros:
                    wsl_info["distro"] = distros[0]
            except Exception:
                wsl_info["distro"] = "Ubuntu"
    elif is_wsl:
        wsl_info["available"] = True
        wsl_info["distro"] = os.environ.get("WSL_DISTRO_NAME")

    return {
        "os": os_name,
        "environment": environment,
        "active_shell": active_shell,
        "default_shell": default_shell,
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        "shells": {
            "pwsh": {"available": bool(pwsh_path), "path": pwsh_path},
            "curl": {"available": bool(curl_path), "path": curl_path},
            "bash": {"available": bool(bash_path), "path": bash_path},
        },
        "wsl": wsl_info,
    }



def load_dotenv(env_path=None):
    """Load environment variables from .env file using only standard library."""
    if env_path is None:
        candidates = [
            Path.cwd() / ".env",
            Path(__file__).resolve().parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
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
            db_dir = Path(config_dir).expanduser() if config_dir else Path.home() / ".peforth"
            database_path = db_dir / "ai-diagnostics.sqlite3"

        logger = DiagnosticLog(database_path, environment=env)
        metadata = {
            "argv": sys.argv,
            "version": "2.1.0",
        }
        runtime_id = logger.start_runtime(
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


def _log_event(vm, event_type, turn_id=None, *, payload=None, call_id=None,
               operation=None, http_method=None, url=None, http_status=None,
               elapsed_ms=None, error=None):
    """Append a diagnostic event to the timeline table if logging is enabled."""
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None:
        return None
    try:
        return logger.append_event(
            runtime_id, turn_id, event_type,
            session_id=vm.host.get("ai_active_session_id"),
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
            session_id=vm.host.get("ai_active_session_id"),
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

            # Inherited Frame Safety:
            # If the current execution is within a Frame whose word is marked safe=True,
            # internal helper operations (like unannotated python closures) within this
            # parent frame inherit safety and execute freely.
            # Frames below ai_task_base_frame_depth belong to the outer orchestrator
            # (such as ai: or (ai)) and must never leak safety to untrusted AI code.
            base_depth = vm.host.get("ai_task_base_frame_depth", 0)
            frames = getattr(task, "frames", [])
            relevant_frames = frames[base_depth:] if base_depth < len(frames) else []
            if any(getattr(getattr(f, "word", None), "properties", {}).get("safe")
                   for f in relevant_frames):
                resolved = vm._resolve(operation)
                # An explicitly unsafe word (safe=False) must NEVER inherit safety
                if not (hasattr(resolved, "properties") and resolved.properties.get("safe") is False):
                    yield from original_call(operation)
                    return

            trusted_tasks = vm.host.setdefault("trusted_ai_tasks", set())
            if task not in trusted_tasks:
                resolved = vm._resolve(operation)
                is_safe = False
                if hasattr(resolved, "properties") and resolved.properties.get("safe"):
                    is_safe = True
                elif callable(resolved) and getattr(resolved, "_safe", False):
                    is_safe = True

                if not is_safe:
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

                    # In interactive mode (not headless), use ai-approve UI
                    if not vm.host.get("headless", False):
                        approval_word = vm.tick("ai-approve")
                        if approval_word:
                            proposal = {
                                "purpose": f"Execution of unsafe word '{name}'",
                                "source": source_text,
                            }
                            stack_depth = len(vm.dstack)
                            vm.push(proposal)
                            _log_event(vm, "approval_requested", turn_id=turn_id,
                                       operation=name, payload=proposal)
                            vm.host["in_approval"] = True
                            try:
                                yield from vm.call(approval_word)
                            finally:
                                vm.host["in_approval"] = False
                            decision = vm.pop() if len(vm.dstack) > stack_depth else "deny"
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
    return Path.home() / ".peforth"


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


def _api_request(method, path, payload=None, stream=False, timeout=30):
    load_dotenv()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in ~/.peforth/.env or the process environment to use AI.")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
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
    return urllib.request.urlopen(req, timeout=timeout)


def _api_get(path, timeout=30):
    with _api_request("GET", path, timeout=timeout) as response:
        return json.load(response)


def _api_delete(path, timeout=30):
    with _api_request("DELETE", path, timeout=timeout) as response:
        return json.load(response)


def _list_remote_sessions():
    """Fetch remote session records using the API's cursor pagination."""
    sessions = []
    after = ""
    while True:
        query = urllib.parse.urlencode({"limit": 100, "order": "desc", **({"after": after} if after else {})})
        page = _api_get(f"/sessions?{query}")
        sessions.extend(page.get("data") or [])
        if not page.get("has_more") or not page.get("last_id") or page["last_id"] == after:
            return sessions
        after = page["last_id"]


def _fetch_session_items(session_id):
    """Fetch all remote items for a session in ascending sequence order."""
    encoded_id = urllib.parse.quote(session_id, safe="")
    items = []
    after = None
    while True:
        query = {"limit": 100, "order": "asc"}
        if after:
            query["after"] = after
        page = _api_get(
            f"/sessions/{encoded_id}/items?{urllib.parse.urlencode(query)}"
        )
        items.extend(page.get("data") or [])
        last_id = page.get("last_id")
        if not page.get("has_more") or not last_id or last_id == after:
            break
        after = last_id
    return items


def sync_sessions(vm=None):
    """Incrementally sync remote sessions and items into the local SQLite mirror."""
    remote_sessions = _list_remote_sessions()
    synced = 0
    skipped = 0
    remote_ids = []
    with _open_session_store() as store:
        for remote in remote_sessions:
            if not isinstance(remote, dict):
                continue
            session_id = remote.get("id") or remote.get("session_id")
            if not isinstance(session_id, str) or not session_id:
                continue
            remote_ids.append(session_id)
            if store.needs_item_sync(remote):
                items = _fetch_session_items(session_id)
                store.sync_session(remote, items)
                synced += 1
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


SYSTEM_PROMPT = """You are an intelligent AI pair programmer embedded inside the peforth Forth environment.
peforth is an AI-first Forth environment hosted by Python. It seamlessly bridges Forth with Python: you can run native Forth, write Python host definitions, and execute Python code directly inside Forth!

=== When to Respond Directly vs. When to Use Tools ===
- CONVERSATION & Q&A: For general conversation, greetings, questions, explanations, discussions, or telling jokes, respond DIRECTLY with natural language text! Your text reply is streamed immediately to the user's terminal.
  DO NOT use peforth_run_forth or print statements (e.g. s" ..." . cr) just to speak to the user or tell a joke!
- CODE EXECUTION: ONLY call peforth_run_forth when you genuinely need to execute Forth code, define new words, test behavior in the VM, perform calculations, or run Python interop requested by the user.
- AVOID DUPLICATE OUTPUT: When you use peforth_run_forth to execute code that produces output in the terminal, DO NOT repeat or echo that entire stdout in your final assistant reply; just briefly explain the result if necessary.
- DICTIONARY SEARCH: Use peforth_search_words when you need to look up available Forth words, syntax, or documentation before proposing code.

You have access to tools:
1. peforth_search_words: search available Forth vocabulary, words, help strings, comments, and implementation source. Pure read-only.
   *IMPORTANT*: peforth is a rich, evolving environment. When unsure whether a word exists or how it interacts with the VM, ALWAYS search the dictionary first to inspect its documentation and source!
2. peforth_search_sessions: Search or read past AI conversations from the local SQLite session mirror (sessions.sqlite3). Read-only; runs without user approval. Pass query to search across all sessions, or session_id to read messages from a specific session.
3. peforth_run_forth: propose and execute Forth source code in the user's local VM.

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
    runtime_skills = Path.home() / ".peforth" / "skills"
    if runtime_skills.is_dir():
        return runtime_skills.resolve()
    return candidate


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


def get_system_prompt(vm=None) -> str:
    """Build full agent system prompt dynamically composed with loaded skills."""
    skills_root = get_skills_dir(vm)
    skill_names, combined_skills = load_all_skills(skills_root)
    reference_path = skills_root / "peforth-forth" / "references" / "forth-reference.md"
    reference_text = reference_path.read_text(encoding="utf-8") if reference_path.is_file() else ""

    sys_info = detect_system_info(vm)
    shell_label = "pwsh (PowerShell 7)" if sys_info.get("active_shell") == "pwsh" else sys_info.get("active_shell", "unknown")
    os_label = sys_info.get("os", "unknown").lower()

    env_section = (
        f"\n\n=== System Environment ===\n"
        f"- OS: {os_label}\n"
        f"- Active Shell: {shell_label}\n"
    )

    instructions = SYSTEM_PROMPT + env_section
    if combined_skills:
        instructions += "\n\n=== Available Skills ===\n\n" + combined_skills
    if reference_text:
        instructions += "\n\n=== Forth Reference ===\n\n" + reference_text

    if len(instructions.encode("utf-8")) > 100_000:
        raise RuntimeError("Combined skill texts are too large to include in agent instructions.")
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
    except Exception:
        for choice in choices:
            print(f"{choice}. {labels.get(choice, choice)}")
        try:
            val = input(prompt).strip()
            return val if val in choices else default
        except Exception:
            return default


def _http_chat_stream(base_url, api_key, model, messages, tools):
    """Send streaming Chat Completion request to OpenAI-compatible endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "stream": True,
    }

    # Automatically set reasoning_effort to "none" for reasoning models when using tools
    reasoning_effort = os.environ.get("OPENAI_REASONING_EFFORT")
    if reasoning_effort is None:
        if any(prefix in model.lower() for prefix in ("o1", "o3", "gpt-6")):
            reasoning_effort = "none"
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        if "reasoning_effort" in err_body:
            if "Unrecognized request argument" in err_body:
                payload.pop("reasoning_effort", None)
            else:
                payload["reasoning_effort"] = "none"
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            return urllib.request.urlopen(req, timeout=60)
        raise


def ai_turn(vm, prompt, stream_response):
    """Cooperative generator for one AI conversation turn."""
    init_diagnostics(vm)
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        msg = ("\n[AI] OPENAI_API_KEY is not set.\n"
               "Please configure OPENAI_API_KEY in your environment or in a .env file.\n"
               "Example: export OPENAI_API_KEY=\"sk-...\"\n")
        if stream_response:
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            vm.push(msg)
        return

    # Start diagnostic turn tracking if enabled
    system_instructions = get_system_prompt(vm)
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
                remote_session_id=vm.host.get("ai_active_session_id"),
            )
            vm.host["ai_current_turn_id"] = turn_id
            logger.append_event(
                runtime_id, turn_id, "ai_turn_started",
                payload={"model": model, "stream_response": bool(stream_response)},
            )
        except Exception:
            turn_id = None

    image_url = vm.host.pop("ai_image_url_once", None)
    isolated_session = vm.host.pop("ai_isolated_session_once", False)

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

    # Outer loop for handling multi-turn tool calling
    while True:
        t0 = time.monotonic()
        req_url = f"{base_url.rstrip('/')}/chat/completions"
        _log_event(vm, "http_request_started", turn_id=turn_id,
                   http_method="POST", url=req_url, payload={"model": model})
        try:
            response = _http_chat_stream(base_url, api_key, model, messages, TOOLS_DEFINITION)
            elapsed_ms = (time.monotonic() - t0) * 1000.0
            http_status = getattr(response, "status", 200)
            _log_event(vm, "http_response_received", turn_id=turn_id,
                       http_status=http_status, elapsed_ms=elapsed_ms)
        except urllib.error.HTTPError as e:
            elapsed_ms = (time.monotonic() - t0) * 1000.0
            _log_event(vm, "http_request_failed", turn_id=turn_id,
                       http_status=e.code, elapsed_ms=elapsed_ms, error=e)
            _finish_turn(vm, turn_id,
                         output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                         output_status="partial" if accumulated_full_text else "failed_before_output",
                         status="failed", error=e)
            vm.host["ai_current_turn_id"] = None
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
            _finish_turn(vm, turn_id,
                         output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                         output_status="partial" if accumulated_full_text else "failed_before_output",
                         status="failed", error=e)
            vm.host["ai_current_turn_id"] = None
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
                for raw_line in response:
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
                        if stream_response:
                            sys.stdout.write(content_chunk)
                            sys.stdout.flush()

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
            _finish_turn(vm, turn_id,
                         output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                         output_status="partial" if accumulated_full_text else "failed_before_output",
                         status="failed", error=e)
            vm.host["ai_current_turn_id"] = None
            raise

        if assistant_content:
            accumulated_full_text.append(assistant_content)

        # Build assistant message object
        assistant_msg = {"role": "assistant"}
        if assistant_content:
            assistant_msg["content"] = assistant_content
        else:
            assistant_msg["content"] = None

        if tool_calls_map:
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

                elif fn_name == "peforth_run_forth":
                    source = args.get("source", "")
                    purpose = args.get("purpose", "")

                    if stream_response:
                        sys.stdout.write(f"\n[AI Proposes Forth Code]\nPurpose: {purpose}\nSource:\n{source.strip()}\n---\n")
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

    # Clean up trusted task status once turn is done
    trusted_tasks = vm.host.get("trusted_ai_tasks")
    if trusted_tasks and vm.task in trusted_tasks:
        trusted_tasks.remove(vm.task)
    vm.host["pending_ai_task"] = None

    _finish_turn(vm, turn_id,
                 output_text="\n".join(accumulated_full_text) if accumulated_full_text else None,
                 output_status="complete" if accumulated_full_text else "empty",
                 status="completed")
    vm.host["ai_current_turn_id"] = None

    if stream_response:
        sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        vm.push("\n".join(accumulated_full_text))
