"""Python-only host operations used by AI and Herdr Forth words."""
from __future__ import annotations

import subprocess
import os
import re
import secrets
import shutil
import json
from datetime import datetime, timezone
import urllib.error
import urllib.request

_OUTPUT_LIMIT = 64 * 1024
_HERDR_MAX_SCREEN_LINES = 1000
_PROCESS_TIMEOUT = 60
_HTTP_TIMEOUT = 30
_HERDR_TIMEOUT = 10
_ACTIVE_HERDR_PERMITS = set()


def _clip(value):
    value = value or ""
    return value[:_OUTPUT_LIMIT], len(value) > _OUTPUT_LIMIT


def _decode_partial(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def _run_process(argv, input_text=None, timeout=_PROCESS_TIMEOUT):
    """Run a process without a shell and return bounded text output."""
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
        stdout, out_truncated = _clip(_decode_partial(exc.stdout))
        stderr, err_truncated = _clip(_decode_partial(exc.stderr))
        return {
            "exit_code": None,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": True,
            "truncated": out_truncated or err_truncated,
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

    stdout, out_truncated = _clip(completed.stdout)
    stderr, err_truncated = _clip(completed.stderr)
    return {
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": False,
        "truncated": out_truncated or err_truncated,
    }


def _herdr_session_name(value):
    if (not isinstance(value, str) or not value or value != value.strip()
            or value.startswith("-") or len(value) > 256
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise ValueError("session must be a non-empty Herdr session name.")
    return value


def _herdr_process(args, session=None):
    """Run one bounded Herdr CLI request in an optional named session."""
    executable = shutil.which("herdr")
    if not executable:
        raise RuntimeError("Herdr CLI is not available on this process PATH.")
    argv = [executable]
    if session is not None:
        argv.extend(["--session", _herdr_session_name(session)])
    argv.extend(args)
    result = _run_process(argv, timeout=_HERDR_TIMEOUT)
    if result["timed_out"]:
        raise RuntimeError("Herdr CLI request timed out; inspect pane state before retrying.")
    if result.get("error"):
        raise RuntimeError(f"Could not run Herdr CLI: {result['error']}")
    if result["exit_code"] != 0:
        detail = result["stderr"].strip() or result["stdout"].strip()
        raise RuntimeError(f"Herdr CLI returned exit code {result['exit_code']}: {detail}")
    return result


def _herdr_json(args, session=None):
    result = _herdr_process(args, session=session)
    if result["truncated"]:
        raise RuntimeError("Herdr CLI JSON response exceeded the output limit.")
    try:
        return json.loads(result["stdout"])
    except (TypeError, ValueError):
        raise RuntimeError("Herdr CLI response was not valid JSON.") from None


def _herdr_operation_response(args, session=None):
    result = _herdr_process(args, session=session)
    raw_stdout = result['stdout']
    try:
        response = json.loads(raw_stdout)
    except (TypeError, ValueError):
        response = raw_stdout
    return {
        'exit_code': result['exit_code'],
        'response': response,
        'stderr': result['stderr'],
        'truncated': result['truncated'],
    }


def _herdr_walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _herdr_walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _herdr_walk(item)


def _herdr_pane_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"w[0-9A-Za-z]+:p[0-9A-Za-z]+", value):
        raise ValueError("pane_id must be a Herdr pane ID such as w1:p2.")
    return value


def _herdr_context():
    """Require a live Herdr-managed caller and verify its inherited pane context."""
    if os.environ.get("HERDR_ENV") != "1":
        raise RuntimeError("This process is not running inside a Herdr-managed pane.")
    inherited_pane = os.environ.get("HERDR_PANE_ID")
    if not inherited_pane:
        raise RuntimeError("Herdr did not provide a caller pane ID.")
    inherited_pane = _herdr_pane_id(inherited_pane)
    current = _herdr_json(["pane", "current", "--current"])
    live_pane = next(
        (item.get("pane_id") for item in _herdr_walk(current)
         if isinstance(item.get("pane_id"), str)),
        None,
    )
    if live_pane != inherited_pane:
        raise RuntimeError("The inherited Herdr pane ID is stale or no longer current.")
    return inherited_pane


def _herdr_validate_pane(pane_id, session=None):
    pane_id = _herdr_pane_id(pane_id)
    if session is not None:
        session = _herdr_session_name(session)
    workspace_id = pane_id.split(":", 1)[0]
    listing = _herdr_json(["pane", "list", "--workspace", workspace_id], session=session)
    if not any(item.get("pane_id") == pane_id for item in _herdr_walk(listing)):
        raise RuntimeError(f"Herdr pane {pane_id} is not present in its workspace.")
    return pane_id


def _herdr_current_pane():
    return _herdr_context()


def _herdr_text_value(value):
    preferred = ("text", "snapshot", "content", "output", "recent_text")
    for item in _herdr_walk(value):
        for key in preferred:
            candidate = item.get(key)
            if isinstance(candidate, str):
                return candidate
    return ""


def _herdr_screen_read(pane_id, source="visible", line_count=80, session=None):
    if session is not None:
        session = _herdr_session_name(session)
    pane_id = _herdr_validate_pane(pane_id, session=session)
    if source not in {"visible", "recent", "recent-unwrapped"}:
        raise ValueError("source must be visible, recent, or recent-unwrapped.")
    if isinstance(line_count, bool) or not isinstance(line_count, int) or line_count < 1:
        raise ValueError("line_count must be a positive integer.")
    requested_line_count = line_count
    line_count = min(line_count, _HERDR_MAX_SCREEN_LINES)
    response = _herdr_process([
        "pane", "read", pane_id, "--source", source, "--lines", str(line_count),
    ], session=session)
    raw_text = response["stdout"]
    parsed = None
    try:
        parsed = json.loads(raw_text)
    except (TypeError, ValueError):
        pass
    if isinstance(parsed, str):
        text = parsed
    elif parsed is not None:
        text = _herdr_text_value(parsed)
    else:
        text = raw_text
    if not text and raw_text:
        text = raw_text
    truncation = response["truncated"]
    if parsed is not None and not isinstance(parsed, str):
        truncation = truncation or any(
            item.get("truncated") is True for item in _herdr_walk(parsed)
        )
    snapshot = {
        "pane_id": pane_id,
        "source": source,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "line_count": len(text.splitlines()),
        "lines_requested": requested_line_count,
        "truncated": truncation or requested_line_count > line_count,
        "result": {
            "exit_code": response["exit_code"],
            "stderr": response["stderr"],
            "truncated": response["truncated"],
        },
    }
    if session is not None:
        snapshot["session"] = session
    return snapshot


def _herdr_validate_operation_arguments(operation, arguments):
    if operation == "send_text":
        if not isinstance(arguments, str) or not arguments or len(arguments) > 10000:
            raise ValueError("text must contain 1 to 10000 characters.")
    elif operation == "send_keys":
        if (not isinstance(arguments, list) or not arguments or len(arguments) > 32
                or any(not isinstance(key, str) or not key or len(key) > 32 for key in arguments)):
            raise ValueError("keys must be a list of 1 to 32 non-empty key names.")
    elif operation == "run":
        if not isinstance(arguments, str) or not arguments or len(arguments) > 10000:
            raise ValueError("command must contain 1 to 10000 characters.")
    else:
        raise ValueError("Unsupported Herdr operation.")
    return arguments


def _herdr_activate_permit(vm, operation, pane_id, arguments, session=None):
    token = secrets.token_bytes(32)
    _ACTIVE_HERDR_PERMITS.add(token)
    vm.host["_herdr_computer_use_permit"] = {
        "token": token,
        "operation": operation,
        "pane_id": pane_id,
        "arguments": arguments,
        "session": session,
        "used": False,
    }
    return token


def _herdr_deactivate_permit(vm, token):
    _ACTIVE_HERDR_PERMITS.discard(token)
    permit = vm.host.get("_herdr_computer_use_permit")
    if isinstance(permit, dict) and permit.get("token") is token:
        vm.host.pop("_herdr_computer_use_permit", None)


def _herdr_forth_operation(vm, operation, pane_id, arguments, session=None):
    _herdr_validate_operation_arguments(operation, arguments)
    permit = vm.host.get("_herdr_computer_use_permit")
    if permit is not None:
        session = permit.get("session", session)
    if session is not None:
        session = _herdr_session_name(session)
    pane_id = _herdr_validate_pane(pane_id, session=session)
    if permit is None:
        includes_enter = (
            operation == "run"
            or (
                operation == "send_keys"
                and any("enter" in key.casefold() or "return" in key.casefold()
                        for key in arguments)
            )
        )
        approval_session = session if session is not None else "default"
        proposal = {
            "kind": "computer_use",
            "purpose": f"Computer Use: {operation} on pane {pane_id} in session {approval_session}",
            "source": json.dumps(
                {
                    "session": approval_session,
                    "pane_id": pane_id,
                    "operation": operation,
                    "includes_enter": includes_enter,
                    "arguments": arguments,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        vm.host["ai_pending_approval"] = proposal
        yield vm.pause()
        approved = bool(vm.host.pop("ai_approval_result", False))
        if not approved:
            raise PermissionError("Computer Use was not approved; the pane operation was not run.")
    elif (not isinstance(permit, dict)
          or permit.get("token") not in _ACTIVE_HERDR_PERMITS
          or permit.get("used")
          or permit.get("operation") != operation
          or permit.get("pane_id") != pane_id
          or permit.get("arguments") != arguments
          or permit.get("session") != session):
        raise RuntimeError("The pending Computer Use approval does not match this operation.")
    else:
        permit["used"] = True
        _ACTIVE_HERDR_PERMITS.discard(permit["token"])
    if operation == "send_text":
        argv = ["pane", "send-text", pane_id, arguments]
    elif operation == "send_keys":
        argv = ["pane", "send-keys", pane_id, *arguments]
    else:
        argv = ["pane", "run", pane_id, arguments]
    try:
        result = _herdr_operation_response(argv, session=session)
    except Exception as exc:
        raise RuntimeError(
            f"Herdr operation result is unconfirmed; inspect pane {pane_id} before retrying. {exc}"
        ) from None
    argument_name = {
        'send_text': 'text',
        'send_keys': 'keys',
        'run': 'command',
    }[operation]
    response = {
        'pane_id': pane_id,
        'operation': operation,
        argument_name: arguments,
        'success': True,
        'result': result,
    }
    if session is not None:
        response["session"] = session
    return response


def _http_body_text(raw, headers):
    try:
        charset = headers.get_content_charset()
    except AttributeError:
        charset = None
    try:
        return raw.decode(charset or "utf-8", "replace")
    except LookupError:
        return raw.decode("utf-8", "replace")


def _http_result(status, headers, body):
    raw = body.read(_OUTPUT_LIMIT + 1)
    truncated = len(raw) > _OUTPUT_LIMIT
    raw = raw[:_OUTPUT_LIMIT]
    return {
        "status_code": status,
        "headers": {str(key): str(value) for key, value in headers.items()},
        "body": _http_body_text(raw, headers),
        "truncated": truncated,
    }


def _http_request(url, method, headers, body):
    """Send an already-validated request and normalize its response."""
    data = body.encode("utf-8") if body is not None else None
    try:
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT) as response:
            return _http_result(response.status, response.headers, response)
    except urllib.error.HTTPError as exc:
        try:
            return _http_result(exc.code, exc.headers, exc)
        finally:
            exc.close()
    except Exception as exc:
        return {"error": str(exc)}


_IMAGE_DATA_URI_MAX_LEN = 1_048_576
_SCREENSHOT_MAX_BYTES = 750_000
_SCREENSHOT_MAX_DIMENSION = 1920


def _powershell_executable(vm=None):
    """Locate a PowerShell executable capable of running Windows System.Drawing."""
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
    """Convert a Windows path to a local filesystem path when running under WSL."""
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
    """Convert a WSL /mnt/<drive>/... path to a Windows path when needed."""
    if not isinstance(local_path, str) or not local_path or os.name == "nt":
        return local_path
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", local_path)
    if match:
        drive = match.group(1).upper()
        rest = match.group(2).replace("/", "\\")
        return f"{drive}:\\{rest}"
    return local_path


def _run_powershell_encoded(script, vm=None, timeout=_PROCESS_TIMEOUT):
    """Execute a multi-line PowerShell script safely via UTF-16LE -EncodedCommand."""
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
    if result["timed_out"]:
        raise RuntimeError(result.get("error") or "PowerShell desktop capture timed out.")
    if result.get("error"):
        raise RuntimeError(f"Could not run PowerShell: {result['error']}")
    if result["exit_code"] != 0:
        detail = result["stderr"].strip() or result["stdout"].strip()
        raise RuntimeError(f"PowerShell failed (exit code {result['exit_code']}): {detail}")
    return result


def capture_desktop(
    region=None,
    max_dimension=_SCREENSHOT_MAX_DIMENSION,
    quality=82,
    max_bytes=_SCREENSHOT_MAX_BYTES,
    vm=None,
):
    """Capture a DPI-aware live Windows desktop screenshot sized for AI inspection.

    If ``region`` is provided as ``(x, y, width, height)``, values may be either
    normalized floats in ``0.0..1.0`` (fractions of VirtualScreen) or pixel
    coordinates. The captured image is saved to a unique timestamped JPEG in
    ``TEMP`` guaranteed not to exceed ``max_bytes`` so that its Base64 data URI
    always fits within the Agents API ``1,048,576``-character limit.
    """
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
    result = _run_powershell_encoded(script, vm=vm)
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
    """Read a local image file and return a ``data:image/...;base64,...`` URI.

    If the raw file's Base64 Data URI exceeds ``max_data_uri_len`` (1,048,576 chars
    on the OpenAI Agents API), the image is automatically downscaled and compressed
    to a JPEG that fits within the limit.
    """
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
    with open(abs_path, "rb") as f:
        raw_bytes = f.read()
    prefix = f"data:{mime_type};base64,"
    encoded_len = ((len(raw_bytes) + 2) // 3) * 4
    if len(prefix) + encoded_len <= max_data_uri_len:
        encoded = base64.b64encode(raw_bytes).decode("ascii")
        return prefix + encoded
    max_raw_bytes = min(_SCREENSHOT_MAX_BYTES, ((max_data_uri_len - 32) // 4) * 3)
    compressed_mime, encoded = _compress_image_file_for_ai(
        abs_path, max_bytes=max_raw_bytes, vm=vm
    )
    data_uri = f"data:{compressed_mime};base64,{encoded}"
    if len(data_uri) > max_data_uri_len:
        raise RuntimeError(
            f"Compressed image Data URI ({len(data_uri)} chars) still exceeds the "
            f"{max_data_uri_len}-character limit."
        )
    return data_uri
