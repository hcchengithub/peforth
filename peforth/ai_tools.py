"""Python-only host operations used by the AI Forth words in ai.f."""
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


def _herdr_process(args):
    """Run one bounded Herdr CLI request and require a successful exit."""
    executable = shutil.which("herdr")
    if not executable:
        raise RuntimeError("Herdr CLI is not available on this process PATH.")
    result = _run_process([executable, *args], timeout=_HERDR_TIMEOUT)
    if result["timed_out"]:
        raise RuntimeError("Herdr CLI request timed out; inspect pane state before retrying.")
    if result.get("error"):
        raise RuntimeError(f"Could not run Herdr CLI: {result['error']}")
    if result["exit_code"] != 0:
        detail = result["stderr"].strip() or result["stdout"].strip()
        raise RuntimeError(f"Herdr CLI returned exit code {result['exit_code']}: {detail}")
    return result


def _herdr_json(args):
    result = _herdr_process(args)
    if result["truncated"]:
        raise RuntimeError("Herdr CLI JSON response exceeded the output limit.")
    try:
        return json.loads(result["stdout"])
    except (TypeError, ValueError):
        raise RuntimeError("Herdr CLI response was not valid JSON.") from None


def _herdr_operation_response(args):
    result = _herdr_process(args)
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


def _herdr_validate_pane(pane_id):
    pane_id = _herdr_pane_id(pane_id)
    _herdr_context()
    workspace_id = pane_id.split(":", 1)[0]
    listing = _herdr_json(["pane", "list", "--workspace", workspace_id])
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


def _herdr_screen_read(pane_id, source="visible", line_count=80):
    pane_id = _herdr_validate_pane(pane_id)
    if source not in {"visible", "recent", "recent-unwrapped"}:
        raise ValueError("source must be visible, recent, or recent-unwrapped.")
    if isinstance(line_count, bool) or not isinstance(line_count, int) or line_count < 1:
        raise ValueError("line_count must be a positive integer.")
    requested_line_count = line_count
    line_count = min(line_count, _HERDR_MAX_SCREEN_LINES)
    response = _herdr_process([
        "pane", "read", pane_id, "--source", source, "--lines", str(line_count),
    ])
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
    return {
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


def _herdr_activate_permit(vm, operation, pane_id, arguments):
    token = secrets.token_bytes(32)
    _ACTIVE_HERDR_PERMITS.add(token)
    vm.host["_herdr_computer_use_permit"] = {
        "token": token,
        "operation": operation,
        "pane_id": pane_id,
        "arguments": arguments,
        "used": False,
    }
    return token


def _herdr_deactivate_permit(vm, token):
    _ACTIVE_HERDR_PERMITS.discard(token)
    permit = vm.host.get("_herdr_computer_use_permit")
    if isinstance(permit, dict) and permit.get("token") is token:
        vm.host.pop("_herdr_computer_use_permit", None)


def _herdr_forth_operation(vm, operation, pane_id, arguments):
    _herdr_validate_operation_arguments(operation, arguments)
    pane_id = _herdr_validate_pane(pane_id)
    permit = vm.host.get("_herdr_computer_use_permit")
    if permit is None:
        if vm.host.get("_ai_forth_execution"):
            raise RuntimeError(
                "Computer Use from peforth_run_forth is blocked; use computer_operate "
                "so the dedicated ai-approve prompt can authorize this operation."
            )
        includes_enter = (
            operation == "run"
            or (
                operation == "send_keys"
                and any("enter" in key.casefold() or "return" in key.casefold()
                        for key in arguments)
            )
        )
        proposal = {
            "kind": "computer_use",
            "purpose": f"Computer Use: {operation} on pane {pane_id}",
            "source": json.dumps(
                {
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
          or permit.get("arguments") != arguments):
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
        result = _herdr_operation_response(argv)
    except Exception as exc:
        raise RuntimeError(
            f"Herdr operation result is unconfirmed; inspect pane {pane_id} before retrying. {exc}"
        ) from None
    argument_name = {
        'send_text': 'text',
        'send_keys': 'keys',
        'run': 'command',
    }[operation]
    return {
        'pane_id': pane_id,
        'operation': operation,
        argument_name: arguments,
        'success': True,
        'result': result,
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
