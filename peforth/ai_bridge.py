"""Small Python transport and host helpers used by the Forth AI words."""
from __future__ import annotations

from datetime import datetime, timezone
import io
import json
import os
import re
import sys
import tempfile
import time
import uuid
from contextlib import redirect_stderr, redirect_stdout
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parent.parent
USER_HOME = Path.home() / ".peforth"
API = "https://api.openai.com/v1/agents"


def _runtime_config_path():
    configured = os.environ.get("PEFORTH_CONFIG_DIR")
    if configured:
        path = Path(configured).expanduser()
        return path if path.is_absolute() else (Path.cwd() / path).resolve()
    return USER_HOME


SESSION_FILE = USER_HOME / ".ai_session.json"


def _session_file():
    """Resolve the configured session index, honoring explicit test overrides."""
    default_path = USER_HOME / ".ai_session.json"
    if "SESSION_FILE" in globals() and SESSION_FILE != default_path:
        return SESSION_FILE
    return _runtime_config_path() / ".ai_session.json"


def _source_skills_dir():
    configured = os.environ.get("PEFORTH_SKILLS_DIR")
    return Path(configured).expanduser() if configured else RUNTIME_ROOT / "skills"


def load_dotenv():
    try:
        lines = (_runtime_config_path() / ".env").read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _diagnostic_event(context, event_type, *, payload=None, remote_turn_id=None,
                      call_id=None, content_id=None, http_method=None, url=None,
                      http_status=None, local_request_id=None,
                      provider_request_id=None, elapsed_ms=None, error=None):
    if not context:
        return
    logger = context.get("logger")
    runtime_id = context.get("runtime_id")
    if logger is None or runtime_id is None:
        return
    try:
        logger.append_event(
            runtime_id, context.get("turn_id"), event_type,
            session_id=context.get("session_id"), remote_turn_id=remote_turn_id,
            call_id=call_id, operation=context.get("operation"),
            http_method=http_method, url=url, http_status=http_status,
            local_request_id=local_request_id,
            provider_request_id=provider_request_id, elapsed_ms=elapsed_ms,
            content_id=content_id if content_id is not None else context.get("content_id"),
            payload=payload,
            error_type=type(error).__name__ if error is not None else None,
            error_message=str(error) if error is not None else None,
        )
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)


def _diagnostic_context(vm, turn_id):
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None or turn_id is None:
        return None
    return {
        "logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
        "session_id": vm.host.get("ai_active_session_id"),
        "mode": vm.host.get("diagnostic_log_mode", "normal"),
    }


def _header_value(headers, *names):
    for name in names:
        value = headers.get(name) if hasattr(headers, "get") else None
        if value:
            return str(value)
    return None


def _safe_headers(headers):
    if not hasattr(headers, "items"):
        return {}
    sensitive = {"authorization", "cookie", "set-cookie", "x-api-key", "api-key"}
    return {str(name): ("[REDACTED]" if str(name).casefold() in sensitive else str(value))
            for name, value in headers.items()}


class _LoggedResponse:
    def __init__(self, response, diagnostic, *, method, path, operation,
                 started_ns, request_id, provider_request_id, status, stream):
        self._response = response
        self._diagnostic = diagnostic
        self._method = method
        self._path = path
        self._operation = operation
        self._started_ns = started_ns
        self._request_id = request_id
        self._provider_request_id = provider_request_id
        self._status = status
        self._stream = stream
        self._verbose = diagnostic.get("mode") == "verbose"
        self._response_payload = bytearray()
        self._closed = False

    def __getattr__(self, name):
        return getattr(self._response, name)

    @property
    def closed(self):
        return self._closed or bool(getattr(self._response, "closed", False))

    def __iter__(self):
        return iter(self._response)

    def read(self, size=-1):
        value = self._response.read(size)
        if self._verbose and not self._stream and value:
            self._response_payload.extend(
                value.encode("utf-8") if isinstance(value, str) else value
            )
        return value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self._closed:
            return
        try:
            self._response.close()
        finally:
            self._closed = True
            elapsed_ms = (time.monotonic_ns() - self._started_ns) / 1_000_000
            if self._response_payload:
                content_text = self._response_payload.decode("utf-8", "replace")
                content_id = _diagnostic_store_content(
                    self._diagnostic, "http_response_payload", content_text
                )
                _diagnostic_event(
                    self._diagnostic, "http_response_payload",
                    content_id=content_id,
                    payload={"content_length": len(self._response_payload)},
                    http_method=self._method, url=self._path,
                    http_status=self._status, local_request_id=self._request_id,
                    provider_request_id=self._provider_request_id,
                    elapsed_ms=elapsed_ms,
                )
            _diagnostic_event(
                self._diagnostic, "http_request_closed", http_method=self._method,
                url=self._path, http_status=self._status,
                local_request_id=self._request_id,
                provider_request_id=self._provider_request_id, elapsed_ms=elapsed_ms,
            )


def _request(method, path, payload=None, stream=False, *, diagnostic=None, operation=None):
    load_dotenv()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in ~/.peforth/.env or the process environment to use AI.")
    method = method.upper()
    operation = operation or path.split("?", 1)[0].strip("/") or "request"
    request_id = str(uuid.uuid4())
    started_ns = time.monotonic_ns()
    request_text = None if payload is None else json.dumps(payload, ensure_ascii=False)
    body = request_text.encode() if request_text is not None else None
    request = urllib.request.Request(API + path, data=body, method=method, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "OpenAI-Beta": "agents=v1",
        "Accept": "text/event-stream" if stream else "application/json"})
    context = dict(diagnostic or {})
    context["operation"] = operation
    verbose = context.get("mode") == "verbose"
    request_details: dict[str, object] = {"stream": bool(stream)}
    request_payload_content_id = None
    if verbose:
        if request_text is not None:
            request_payload_content_id = _diagnostic_store_content(
                context, "http_request_payload", request_text
            )
            request_details["request_payload_content_id"] = request_payload_content_id
        request_details["request_headers"] = _safe_headers(dict(request.header_items()))
    _diagnostic_event(
        context, "http_request_started", payload=request_details,
        content_id=request_payload_content_id,
        http_method=method, url=path, local_request_id=request_id,
    )
    if stream:
        _diagnostic_event(
            context, "sse_open_started", payload={"stream": True},
            http_method=method, url=path, local_request_id=request_id,
        )
    try:
        response = urllib.request.urlopen(request, timeout=300)
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
        provider_request_id = _header_value(exc.headers, "x-request-id", "request-id", "openai-request-id")
        response_details: dict[str, object] = {"stream": bool(stream)}
        if verbose:
            response_details["response_headers"] = _safe_headers(exc.headers)
        _diagnostic_event(
            context, "http_response_received", payload=response_details,
            http_method=method, url=path, http_status=exc.code,
            local_request_id=request_id, provider_request_id=provider_request_id,
            elapsed_ms=elapsed_ms,
        )
        detail_bytes = exc.read(4096)
        detail = detail_bytes.decode("utf-8", "replace")
        if verbose and detail_bytes:
            content_id = _diagnostic_store_content(
                context, "http_response_payload", detail
            )
            _diagnostic_event(
                context, "http_response_payload", content_id=content_id,
                payload={"content_length": len(detail_bytes)},
                http_method=method, url=path, http_status=exc.code,
                local_request_id=request_id, provider_request_id=provider_request_id,
                elapsed_ms=elapsed_ms,
            )
        error = RuntimeError(f"Agents API HTTP {exc.code}: {detail}")
        _diagnostic_event(
            context, "http_request_failed", payload={"stream": bool(stream)},
            http_method=method, url=path, http_status=exc.code,
            local_request_id=request_id, provider_request_id=provider_request_id,
            elapsed_ms=elapsed_ms, error=error,
        )
        try:
            exc.close()
        except Exception as close_error:
            _diagnostic_event(
                context, "http_response_close_failed", payload={"stream": bool(stream)},
                http_method=method, url=path, http_status=exc.code,
                local_request_id=request_id, provider_request_id=provider_request_id,
                elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
                error=close_error,
            )
        finally:
            _diagnostic_event(
                context, "http_request_closed", http_method=method, url=path,
                http_status=exc.code, local_request_id=request_id,
                provider_request_id=provider_request_id,
                elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
            )
        raise error from None
    except urllib.error.URLError as exc:
        elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
        error = RuntimeError(f"Agents API connection failed: {exc.reason}")
        _diagnostic_event(
            context, "http_request_failed", payload={"stream": bool(stream)},
            http_method=method, url=path, local_request_id=request_id,
            elapsed_ms=elapsed_ms, error=error,
        )
        raise error from None
    except Exception as exc:
        elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
        _diagnostic_event(
            context, "http_request_failed", payload={"stream": bool(stream)},
            http_method=method, url=path, local_request_id=request_id,
            elapsed_ms=elapsed_ms, error=exc,
        )
        raise

    status = getattr(response, "status", None)
    if status is None and hasattr(response, "getcode"):
        status = response.getcode()
    headers = getattr(response, "headers", {})
    provider_request_id = _header_value(headers, "x-request-id", "request-id", "openai-request-id")
    response_details: dict[str, object] = {"stream": bool(stream)}
    if verbose:
        response_details["response_headers"] = _safe_headers(headers)
    elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
    _diagnostic_event(
        context, "http_response_received", payload=response_details,
        http_method=method, url=path, http_status=status,
        local_request_id=request_id, provider_request_id=provider_request_id,
        elapsed_ms=elapsed_ms,
    )
    if stream:
        _diagnostic_event(
            context, "sse_opened", payload={"stream": True, "http_status": status},
            http_method=method, url=path, http_status=status,
            local_request_id=request_id, provider_request_id=provider_request_id,
            elapsed_ms=elapsed_ms,
        )
    return _LoggedResponse(
        response, context, method=method, path=path, operation=operation,
        started_ns=started_ns, request_id=request_id,
        provider_request_id=provider_request_id, status=status, stream=stream,
    )


def _api_get(path, *, diagnostic=None, operation=None):
    with _request("GET", path, diagnostic=diagnostic, operation=operation) as response:
        return json.load(response)


def _api_delete(path, *, diagnostic=None, operation=None):
    with _request("DELETE", path, diagnostic=diagnostic, operation=operation) as response:
        return json.load(response)


def _session_titles():
    """Read user-maintained titles from the shared session index."""
    session_file = _session_file()
    try:
        value = json.loads(session_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid session title JSON in {session_file.name} at line {exc.lineno}, column {exc.colno}."
        ) from None
    except OSError as exc:
        raise RuntimeError(f"Cannot read {session_file.name}: {exc}") from None
    if not isinstance(value, dict):
        raise RuntimeError(f"{session_file.name} must contain a JSON object.")
    rows = value.get("sessions", [])
    if not isinstance(rows, list):
        raise RuntimeError(f"The 'sessions' field in {session_file.name} must be a list.")
    return {row["id"]: row["title"] for row in rows
            if isinstance(row, dict) and isinstance(row.get("id"), str)
            and isinstance(row.get("title"), str) and row["title"].strip()}


def _write_session_index(rows):
    """Atomically replace the local index so readers never see partial JSON."""
    session_file = _session_file()
    session_file.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=session_file.name + ".", suffix=".tmp",
                                     dir=str(session_file.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump({"sessions": rows}, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, session_file)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _sync_session_index(remote_sessions):
    titles = _session_titles()
    rows = []
    for session in remote_sessions:
        session_id = session.get("id")
        if isinstance(session_id, str) and session_id:
            rows.append({"id": session_id, "title": titles.get(session_id, "")})
    try:
        _write_session_index(rows)
    except OSError as exc:
        raise RuntimeError(f"Cannot update {_session_file().name}: {exc}") from None
    return {row["id"]: row["title"] for row in rows if row["title"].strip()}


def _short_id(session_id):
    return str(session_id or "")[-8:]


def _session_title(session_id, titles=None):
    titles = _session_titles() if titles is None else titles
    return titles.get(session_id, "")


def _format_time(value):
    if not value:
        return "unknown"
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except (ValueError, TypeError, OSError, OverflowError):
        return str(value)


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


def refresh_session_index(vm=None):
    rows = _list_remote_sessions()
    _sync_session_index(rows)
    if vm is not None:
        vm.host["ai_session_rows"] = rows
    return rows


def _agent_instructions():
    skills_root = _source_skills_dir()
    if not skills_root.is_absolute():
        skills_root = (RUNTIME_ROOT / skills_root).resolve()
    skill = skills_root / "peforth-forth"
    skill_file = skill / "SKILL.md"
    if not skill_file.is_file():
        raise RuntimeError(f"peforth Forth skill not found: {skill_file}")
    skill_text = skill_file.read_text(encoding="utf-8")
    reference_path = skill / "references" / "forth-reference.md"
    reference_text = reference_path.read_text(encoding="utf-8") if reference_path.is_file() else ""
    skill_text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", skill_text, count=1, flags=re.S)
    instructions = (
        "You assist with peforth Forth. Use the live dictionary tool before relying on unfamiliar words. "
        "Only the local Forth tool can execute code. Approval scopes: Yes (allow_once) approves one proposal; Trust this AI task applies only to later proposals in the same AI Task and expires when that Task completes, fails, or is cancelled; Runtime Trust must be explicitly enabled with ai-trust-runtime and lasts in this Forth process until ai-confirm or process exit. ai-confirm revokes Runtime Trust and any active Task Trust. Never infer Trust from a prior Yes or from a different AI Task.\n\n"
        + skill_text + ("\n\nForth reference:\n" + reference_text if reference_text else "")
    )
    if len(instructions.encode("utf-8")) > 100_000:
        raise RuntimeError("peforth Forth skill text is too large to include in agent instructions.")
    return instructions


def _sse_diagnostic_event(context, response, event_type, *, payload=None,
                          content_id=None, remote_turn_id=None, call_id=None,
                          error=None, elapsed_ms=None):
    context = dict(context or {})
    if content_id is not None:
        context["content_id"] = content_id
    _diagnostic_event(
        context, event_type, payload=payload, remote_turn_id=remote_turn_id,
        call_id=call_id,
        http_method=getattr(response, "_method", None),
        url=getattr(response, "_path", None),
        http_status=getattr(response, "_status", None),
        local_request_id=getattr(response, "_request_id", None),
        provider_request_id=getattr(response, "_provider_request_id", None),
        elapsed_ms=elapsed_ms, error=error,
    )


def _diagnostic_store_content(context, content_type, text):
    if not context:
        return None
    logger = context.get("logger")
    if logger is None:
        return None
    try:
        return logger.store_content(content_type, text)
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)
        return None


def _create_session(payload, *, diagnostic=None):
    response = _request(
        "POST", "/sessions", payload, stream=True, diagnostic=diagnostic,
        operation="create_session",
    )
    return _event_stream(response, diagnostic=diagnostic, operation="create_session")


def _event_stream(response, *, diagnostic=None, operation=None):
    context = diagnostic if isinstance(diagnostic, dict) else dict(diagnostic or {})
    if operation is not None:
        context["operation"] = operation
    verbose = context.get("mode") == "verbose"
    stream_started_ns = time.monotonic_ns()
    last_read_ns = None
    last_event_ns = None
    output_length = 0
    data = []
    event_name = None

    def timing(now_ns):
        return {
            "elapsed_ms": (now_ns - stream_started_ns) / 1_000_000,
            "since_last_read_ms": ((now_ns - last_read_ns) / 1_000_000
                                   if last_read_ns is not None else None),
            "since_last_event_ms": ((now_ns - last_event_ns) / 1_000_000
                                    if last_event_ns is not None else None),
        }

    def decode_event(joined, now_ns):
        nonlocal output_length, last_event_ns
        if joined == "[DONE]":
            _sse_diagnostic_event(context, response, "sse_done_received",
                                  payload=timing(now_ns))
            last_event_ns = now_ns
            return None
        try:
            event = json.loads(joined)
        except json.JSONDecodeError as exc:
            _sse_diagnostic_event(
                context, response, "sse_parse_failed",
                payload={**timing(now_ns), "data_length": len(joined)}, error=exc,
            )
            raise
        if not isinstance(event, dict):
            event_type = event_name or "unknown"
            payload = {**timing(now_ns), "event_type": event_type,
                       "data_length": len(joined)}
            if verbose:
                payload["data"] = event
            _sse_diagnostic_event(context, response, "sse_event_received", payload=payload)
            last_event_ns = now_ns
            return event

        kind = event.get("type") or event_name or "unknown"
        session_id = _session_id_from_event(event)
        if session_id:
            context["session_id"] = session_id
            response_context = getattr(response, "_diagnostic", None)
            if isinstance(response_context, dict):
                response_context["session_id"] = session_id
        remote_turn = event.get("turn_id")
        if not remote_turn and isinstance(event.get("turn"), dict):
            remote_turn = event["turn"].get("id")
        call_id = event.get("call_id")
        event_context = dict(context)
        delta = event.get("delta") if kind.endswith("output_text.delta") else None
        if isinstance(delta, str):
            output_length += len(delta)
        payload = {
            **timing(now_ns), "event_type": kind,
            "data_length": len(joined),
        }
        if session_id:
            payload["session_id"] = session_id
        if remote_turn:
            payload["remote_turn_id"] = remote_turn
        if call_id:
            payload["call_id"] = call_id
        if isinstance(delta, str):
            payload["delta_length"] = len(delta)
            payload["output_length"] = output_length
            if verbose:
                payload["delta"] = delta
        elif verbose:
            payload["data"] = event
        else:
            for key in ("status", "sequence_number"):
                if key in event:
                    payload[key] = event[key]
        _sse_diagnostic_event(
            event_context, response, "sse_event_received", payload=payload,
            remote_turn_id=remote_turn, call_id=call_id,
        )
        last_event_ns = now_ns
        return event

    try:
        for raw in response:
            now_ns = time.monotonic_ns()
            raw_bytes = raw if isinstance(raw, bytes) else str(raw).encode("utf-8")
            line = raw_bytes.decode("utf-8", "replace").rstrip(chr(13) + chr(10))
            line_timing = timing(now_ns)
            if verbose:
                content_id = _diagnostic_store_content(context, "sse_raw_line", line)
                _sse_diagnostic_event(
                    context, response, "sse_line_received",
                    payload={**line_timing, "line_length": len(raw_bytes)},
                    content_id=content_id, elapsed_ms=line_timing["elapsed_ms"],
                )
            last_read_ns = now_ns

            if line.startswith(":"):
                _sse_diagnostic_event(
                    context, response, "sse_heartbeat_received",
                    payload={**line_timing, "line_length": len(raw_bytes)},
                )
            elif line.startswith("event:"):
                event_name = line[6:].strip()
            elif line.startswith("data:"):
                data.append(line[5:].lstrip())
            elif not line:
                if data:
                    joined = "\n".join(data)
                    data.clear()
                    try:
                        event = decode_event(joined, now_ns)
                    except json.JSONDecodeError:
                        # Match the existing parser contract: malformed delimited
                        # records are skipped, but remain visible in diagnostics.
                        event_name = None
                        continue
                    event_name = None
                    if event is not None:
                        yield event
                else:
                    event_name = None
        if data:
            joined = "\n".join(data)
            event = decode_event(joined, time.monotonic_ns())
            if event is not None:
                yield event
        _sse_diagnostic_event(
            context, response, "sse_stream_ended",
            payload={"elapsed_ms": (time.monotonic_ns() - stream_started_ns) / 1_000_000},
        )
    except Exception as exc:
        _sse_diagnostic_event(
            context, response, "sse_stream_failed",
            payload={"elapsed_ms": (time.monotonic_ns() - stream_started_ns) / 1_000_000},
            error=exc,
        )
        raise
    finally:
        try:
            response.close()
        finally:
            _sse_diagnostic_event(
                context, response, "sse_stream_closed",
                payload={"elapsed_ms": (time.monotonic_ns() - stream_started_ns) / 1_000_000},
            )


def _stream(session_id, event, *, diagnostic=None):
    encoded_id = urllib.parse.quote(session_id, safe="")
    operation = "continue_session"
    response = _request(
        "GET", f"/sessions/{encoded_id}/events?stream=true", stream=True,
        diagnostic=diagnostic, operation=operation,
    )
    try:
        with _request(
                "POST", f"/sessions/{encoded_id}/events", {"events": [event]},
                diagnostic=diagnostic, operation="submit_session_event") as accepted:
            accepted.read()
        yield from _event_stream(response, diagnostic=diagnostic, operation=operation)
    finally:
        if not response.closed:
            response.close()


def _diagnostic_action_event(context, event_type, action, *, payload=None,
                             content_id=None, error=None, elapsed_ms=None):
    payload = {"tool_name": action.get("name"), **(payload or {})}
    _diagnostic_event(
        context, event_type, payload=payload,
        remote_turn_id=action.get("turn_id"), call_id=action.get("call_id"),
        content_id=content_id, elapsed_ms=elapsed_ms, error=error,
    )


def _diagnostic_cancel_approval(pending, *, reason):
    action = pending.get("action") or {}
    diagnostic = pending.get("diagnostic_context")
    content_id = pending.get("source_content_id")
    _diagnostic_action_event(
        diagnostic, "approval_cancelled", action,
        content_id=content_id, payload={"reason": reason},
    )
    started_ns = pending.get("approval_started_ns")
    elapsed_ms = (
        (time.monotonic_ns() - started_ns) / 1_000_000
        if isinstance(started_ns, int) else None
    )
    _diagnostic_action_event(
        diagnostic, "approval_wait_ended", action,
        content_id=content_id, elapsed_ms=elapsed_ms,
        payload={"decision": "cancelled", "reason": reason},
    )


def _tool_result(session_id, action, success, output="", error="", *, diagnostic=None):
    result_text = output if success else error
    result_content_id = _diagnostic_store_content(diagnostic, "tool_result", result_text)
    event = {"type": "agent.session.input.tool_result", "turn_id": action["turn_id"],
             "call_id": action["call_id"], "success": success}
    event["output" if success else "error"] = result_text
    encoded_id = urllib.parse.quote(session_id, safe="")
    started_ns = time.monotonic_ns()
    try:
        with _request(
                "POST", f"/sessions/{encoded_id}/events", {"events": [event]},
                diagnostic=diagnostic, operation="submit_tool_result") as response:
            response.read()
    except Exception as exc:
        _diagnostic_action_event(
            diagnostic, "tool_result_submit_failed", action,
            content_id=result_content_id, error=exc,
            elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
            payload={"success": success},
        )
        raise
    _diagnostic_action_event(
        diagnostic, "tool_result_submitted", action, content_id=result_content_id,
        elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
        payload={"success": success},
    )


def _current_actions(session_id, *, diagnostic=None):
    event_context = dict(diagnostic or {})
    event_context["session_id"] = session_id
    event_context["operation"] = "get_current_actions"
    started_ns = time.monotonic_ns()
    _diagnostic_event(
        event_context, "current_actions_request_started",
        payload={"operation": "get_current_actions"},
    )
    try:
        session = _api_get(
            f"/sessions/{urllib.parse.quote(session_id, safe='')}",
            diagnostic=diagnostic, operation="get_current_actions",
        )
        status = session.get("status")
        actions = session.get("required_actions") or []
    except Exception as exc:
        _diagnostic_event(
            event_context, "current_actions_request_failed",
            elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
            error=exc,
        )
        raise

    payload_text = json.dumps(session, ensure_ascii=False, sort_keys=True, default=str)
    payload_content_id = _diagnostic_store_content(
        event_context, "current_actions_payload", payload_text
    )
    first_action = actions[0] if actions else {}
    elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
    _diagnostic_event(
        event_context, "current_actions_response_received",
        remote_turn_id=first_action.get("turn_id"),
        call_id=first_action.get("call_id"), elapsed_ms=elapsed_ms,
        payload={"status": status, "required_action_count": len(actions)},
    )
    _diagnostic_event(
        event_context, "current_actions_payload",
        remote_turn_id=first_action.get("turn_id"),
        call_id=first_action.get("call_id"), content_id=payload_content_id,
        elapsed_ms=elapsed_ms, payload={"status": status},
    )
    return status, actions


def _run(vm, source):
    stdout, stderr = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            task = vm.dictate(source)
        if task.status == "paused":
            task.cancel()
            return json.dumps({"status": "error", "error": "Async pause is not supported in AI execution"})
        result = {"status": task.status, "stack": repr(vm.stack),
                  "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}
    except Exception as exc:
        result = {"status": "error", "error": str(exc), "stack": repr(vm.stack),
                  "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}
    return json.dumps(result, ensure_ascii=False)


def _session_id_from_event(event):
    session = event.get("session") or event.get("data") or {}
    if isinstance(session, dict):
        return session.get("id") or session.get("session_id") or event.get("session_id")
    return event.get("session_id")


def _saved_session(vm):
    return vm.host.get("ai_active_session_id") or ""


def _diagnostic_start_turn(vm, prompt, *, instructions=None, session_id=None):
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None:
        return None
    try:
        prompt_content_id = logger.store_content("prompt", prompt)
        instructions_content_id = (
            logger.store_content("agent_instructions", instructions)
            if instructions is not None else None
        )
        turn_id = str(uuid.uuid4())
        logger.start_turn(
            runtime_id, prompt_content_id=prompt_content_id,
            instructions_content_id=instructions_content_id,
            remote_session_id=session_id, turn_id=turn_id,
        )
        logger.append_event(
            runtime_id, turn_id, "ai_turn_started", session_id=session_id,
            payload={"stream": True},
        )
        return turn_id
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)
        return None


def _diagnostic_update_session(vm, turn_id, session_id, *, created=False):
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None or turn_id is None:
        return
    try:
        logger.set_turn_session(turn_id, session_id)
        logger.append_event(
            runtime_id, turn_id,
            "ai_session_created" if created else "ai_session_selected",
            session_id=session_id,
        )
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)


def _diagnostic_finish_turn(vm, turn_id, output_text, *, output_status, status, error=None):
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None or turn_id is None:
        return
    try:
        logger.finish_turn(
            turn_id, output_text=output_text, output_status=output_status,
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
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)


def cancel_turn(vm):
    session_id = _saved_session(vm)
    if session_id:
        with _request("POST", f"/sessions/{urllib.parse.quote(session_id, safe='')}/events", {
                "events": [{"type": "agent.session.input.cancel"}]}) as response:
            response.read()
