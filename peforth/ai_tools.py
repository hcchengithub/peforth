"""Python-only host operations used by the AI Forth words in ai.f."""
from __future__ import annotations

import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

_OUTPUT_LIMIT = 64 * 1024
_PROCESS_TIMEOUT = 60
_HTTP_TIMEOUT = 30


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


def _program_info(name, version_args):
    path = shutil.which(name)
    if not path:
        return {"available": False, "path": None, "version": None}
    result = _run_process([path, *version_args], timeout=8)
    version_text = result.get("stdout", "").strip() or result.get("stderr", "").strip()
    version = next((line.strip() for line in version_text.splitlines() if line.strip()), None)
    return {"available": True, "path": path, "version": version}


def _windows_wsl_info():
    wsl_path = shutil.which("wsl.exe") or shutil.which("wsl")
    if not wsl_path:
        return {"available": False, "path": None, "distro": None, "distros": []}

    listed = _run_process([wsl_path, "--list", "--quiet"], timeout=10)
    raw = (listed.get("stdout") or "").replace("\x00", "").replace("\ufeff", "")
    distros = [line.strip() for line in raw.splitlines() if line.strip()]
    configured = os.environ.get("PEFORTH_WSL_DISTRO", "Ubuntu")
    distro = next((item for item in distros if item.casefold() == configured.casefold()), None)
    if distro is None and configured.casefold() == "ubuntu":
        distro = next((item for item in distros if item.casefold().startswith("ubuntu")), None)
    info = {"available": bool(distro), "path": wsl_path, "distro": distro, "distros": distros}
    if listed.get("exit_code") not in (0, None):
        info["error"] = listed.get("stderr") or "Could not list WSL distributions."
    return info


def _detect_system_info():
    """Detect host capabilities used by the Forth-defined system_info word."""
    is_windows = os.name == "nt"
    release = platform.release()
    is_wsl = bool(os.environ.get("WSL_DISTRO_NAME")) or "microsoft" in release.casefold()
    wsl_distro = os.environ.get("WSL_DISTRO_NAME") if is_wsl else None

    prefix = os.path.normcase(os.path.abspath(sys.prefix))
    base_prefix = os.path.normcase(os.path.abspath(sys.base_prefix))
    venv_active = prefix != base_prefix

    pwsh_name = "pwsh.exe" if is_windows else "pwsh"
    pwsh = _program_info(
        pwsh_name,
        ["-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"],
    )

    if is_windows:
        wsl = _windows_wsl_info()
        if wsl.get("available"):
            bash_probe = _run_process([
                wsl["path"], "-d", wsl["distro"], "--exec", "bash", "--version"
            ], timeout=10)
            version_text = bash_probe.get("stdout", "").strip() or bash_probe.get("stderr", "").strip()
            bash = {
                "available": bash_probe.get("exit_code") == 0,
                "path": wsl["path"],
                "distro": wsl["distro"],
                "version": next((line.strip() for line in version_text.splitlines() if line.strip()), None),
            }
        else:
            bash = {"available": False, "path": None, "distro": None, "version": None}
    else:
        wsl = {"available": is_wsl, "path": None, "distro": wsl_distro, "distros": []}
        bash = _program_info("bash", ["--version"])

    curl_name = "curl.exe" if is_windows else "curl"
    curl = _program_info(curl_name, ["--version"])
    if is_windows and not curl["available"]:
        curl = _program_info("curl", ["--version"])

    return {
        "os": platform.system(),
        "platform": sys.platform,
        "source_path": str(Path(__file__).resolve().parent.parent),
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "venv": {"active": venv_active, "path": sys.prefix if venv_active else None},
        "wsl": {
            "active": is_wsl,
            "available": wsl.get("available", False),
            "distro": wsl.get("distro") or wsl_distro,
            "path": wsl.get("path"),
            "distros": wsl.get("distros", []),
        },
        "shells": {"pwsh": pwsh, "bash": bash, "curl": curl},
    }


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
