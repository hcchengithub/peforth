"""Python-only host operations used by the AI Forth words in ai.f."""
from __future__ import annotations

import subprocess
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
