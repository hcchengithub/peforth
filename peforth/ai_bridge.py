"""Small Python transport and host helpers used by the Forth AI words."""
from __future__ import annotations

from datetime import datetime, timezone
import io
import json
import math
import os
import re
import socket
import sys
import time
import uuid
from contextlib import redirect_stderr, redirect_stdout
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .session_store import (
    SessionStore,
    build_session_description,
    extract_first_sentence,
    extract_first_user_message_text,
    format_description_time,
)

RUNTIME_ROOT = Path(__file__).resolve().parent.parent
USER_HOME = Path.home() / ".peforth"
API = "https://api.openai.com/v1/agents"


def _configured_seconds(name, default):
    raw = os.environ.get(name)
    try:
        seconds = float(raw) if raw is not None else float(default)
    except (TypeError, ValueError):
        raise RuntimeError(f"{name} must be a positive number of seconds.") from None
    if not math.isfinite(seconds) or seconds <= 0:
        raise RuntimeError(f"{name} must be a positive number of seconds.")
    return seconds


def _request_timeout():
    return _configured_seconds("PEFORTH_AI_REQUEST_TIMEOUT", 120)


def _stream_timeout():
    return _configured_seconds("PEFORTH_AI_STREAM_TIMEOUT", 300)


def _poll_interval():
    return _configured_seconds("PEFORTH_AI_POLL_INTERVAL", 0.5)


def _sse_open_grace():
    return _configured_seconds("PEFORTH_AI_SSE_OPEN_GRACE", 5.0)


def _runtime_config_path():
    configured = os.environ.get("PEFORTH_CONFIG_DIR")
    if configured:
        path = Path(configured).expanduser()
        return path if path.is_absolute() else (Path.cwd() / path).resolve()
    return USER_HOME


def _session_db_path():
    """Return the path to the local SQLite session mirror database."""
    return _runtime_config_path() / "sessions" / "sessions.sqlite3"


def _open_session_store():
    return SessionStore(_session_db_path())


def _source_skills_dir():
    configured = os.environ.get("PEFORTH_SKILLS_DIR")
    return Path(configured).expanduser() if configured else RUNTIME_ROOT / "skills"


def _load_all_skills_text():
    """Collect the markdown text of every skill bundle under ``skills_root``.

    Each skill directory is expected to contain a ``SKILL.md`` file. The
    function returns a tuple ``(skill_names, combined_text)`` where
    ``skill_names`` is a list of discovered skill directory names and
    ``combined_text`` is the concatenated markdown of all skill files with a
    simple header separating them.
    """
    skills_root = _source_skills_dir()
    if not skills_root.is_absolute():
        skills_root = (RUNTIME_ROOT / skills_root).resolve()

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
        # Strip the leading YAML‑style block (--- ... ---) which is used for metadata.
        text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
        parts.append(f"## Skill: {entry.name}\n\n{text}\n")
    combined = "\n".join(parts)
    return skill_names, combined


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
        if not os.environ.get(key, "").strip():
            os.environ[key] = value


def _diagnostic_event(context, event_type, *, payload=None, remote_turn_id=None,
                      call_id=None, content_id=None, http_method=None, url=None,
                      http_status=None, local_request_id=None,
                      provider_request_id=None, elapsed_ms=None, error=None):
    if not context:
        return False
    logger = context.get("logger")
    runtime_id = context.get("runtime_id")
    if logger is None or runtime_id is None:
        return False
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
        return True
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)
        return False


def log_heartbeat(vm, message):
    if not isinstance(message, str):
        raise TypeError("tickHeartbeat expects a message string.")
    context = vm.host.get("_ai_heartbeat_context")
    if context is None:
        logger = vm.host.get("diagnostic_log")
        runtime_id = vm.host.get("diagnostic_runtime_id")
        context = ({
            "logger": logger,
            "runtime_id": runtime_id,
            "turn_id": None,
            "session_id": vm.host.get("ai_active_session_id"),
        } if logger is not None and runtime_id is not None else None)
    if context is None:
        return False
    logged = _diagnostic_event(
        context, "ai_heartbeat", payload={"message": message},
        remote_turn_id=context.get("remote_turn_id"),
        call_id=context.get("call_id"),
    )
    if isinstance(context, dict):
        context["_logged"] = logged
    return logged


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


def _diagnostic_runtime_event(vm, event_type, *, payload=None):
    logger = vm.host.get("diagnostic_log")
    runtime_id = vm.host.get("diagnostic_runtime_id")
    if logger is None or runtime_id is None:
        return
    try:
        logger.append_event(
            runtime_id, None, event_type,
            session_id=vm.host.get("ai_active_session_id"),
            payload=payload,
        )
    except Exception as exc:
        print(f"AI diagnostic write failed: {exc}", file=sys.stderr)


def set_one_shot(vm, value, *, reason):
    value = bool(value)
    previous = vm.host.get("one_shot")
    vm.host["one_shot"] = value
    if previous is None or bool(previous) == value:
        return
    _diagnostic_runtime_event(
        vm, "one_shot_changed",
        payload={"previous": bool(previous), "current": value, "reason": str(reason)},
    )


def set_repl_mode(vm, mode, *, reason):
    if mode not in {"chat", "forth"}:
        raise ValueError("REPL mode must be 'chat' or 'forth'.")
    previous = vm.host.get("repl_mode")
    vm.host["repl_mode"] = mode
    if previous == mode:
        return
    if previous is None:
        _diagnostic_runtime_event(
            vm, "repl_input_mode_started",
            payload={"current": mode, "reason": str(reason)},
        )
    else:
        _diagnostic_runtime_event(
            vm, "repl_input_mode_changed",
            payload={"previous": previous, "current": mode, "reason": str(reason)},
        )


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


def _response_socket(response):
    candidates = [
        getattr(response, "_sock", None),
        getattr(getattr(response, "fp", None), "_sock", None),
        getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None),
    ]
    return next((candidate for candidate in candidates
                 if callable(getattr(candidate, "settimeout", None))), None)


def _bounded_body_read(response, size, timeout, *, method, path):
    """Read one HTTP response body under its own request-sized time budget."""
    unlimited = size is None or size < 0
    target = None if unlimited else size
    chunks = []
    total = 0
    deadline = time.monotonic() + timeout
    reader = getattr(response, "read1", None)
    if not callable(reader):
        reader = getattr(getattr(response, "fp", None), "read1", None)
    while target is None or total < target:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            exc = TimeoutError("response body read exceeded its timeout")
            outcome = ("; POST outcome may be unknown; check the session before retrying"
                       if method == "POST" else "")
            raise RuntimeError(
                f"Agents API response body timed out after {timeout:g}s: "
                f"{method} {path}{outcome}"
            ) from exc
        remaining_size = 64 * 1024 if target is None else min(64 * 1024, target - total)
        sock = _response_socket(response)
        if sock is not None:
            sock.settimeout(remaining)
        try:
            chunk = reader(remaining_size) if callable(reader) else response.read(size)
        except (TimeoutError, socket.timeout) as exc:
            outcome = ("; POST outcome may be unknown; check the session before retrying"
                       if method == "POST" else "")
            raise RuntimeError(
                f"Agents API response body timed out after {timeout:g}s: "
                f"{method} {path}{outcome}"
            ) from exc
        if time.monotonic() >= deadline:
            outcome = ("; POST outcome may be unknown; check the session before retrying"
                       if method == "POST" else "")
            raise RuntimeError(
                f"Agents API response body timed out after {timeout:g}s: "
                f"{method} {path}{outcome}"
            )
        if not isinstance(chunk, (bytes, str)):
            raise TypeError("HTTP response body must be bytes or text")
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if not callable(reader):
            break
    if chunks and isinstance(chunks[0], str):
        return "".join(chunks)
    return b"".join(chunks)


class _LoggedResponse:
    def __init__(self, response, diagnostic, *, method, path, operation,
                 started_ns, request_id, provider_request_id, status, stream,
                 body_timeout):
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
        self._body_timeout = body_timeout
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
        value = _bounded_body_read(
            self._response, size, self._body_timeout,
            method=self._method, path=self._path,
        )
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


def _redact_image_urls(value):
    if isinstance(value, dict):
        return {
            key: "[redacted image URL]"
            if key == "image_url" and value.get("type") == "input_image"
            else _redact_image_urls(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_image_urls(item) for item in value]
    return value

def _request(method, path, payload=None, stream=False, *, diagnostic=None,
             operation=None, timeout=None, headers=None):
    load_dotenv()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in ~/.peforth/.env or the process environment to use AI.")
    timeout = _request_timeout() if timeout is None else _configured_seconds(
        "request timeout", timeout
    )
    method = method.upper()
    operation = operation or path.split("?", 1)[0].strip("/") or "request"
    request_id = str(uuid.uuid4())
    started_ns = time.monotonic_ns()
    request_text = None if payload is None else json.dumps(payload, ensure_ascii=False)
    body = request_text.encode() if request_text is not None else None
    request_headers = {
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "OpenAI-Beta": "agents=v1",
        "Accept": "text/event-stream" if stream else "application/json"}
    if headers:
        request_headers.update({str(name): str(value) for name, value in headers.items()})
    request = urllib.request.Request(
        API + path, data=body, method=method, headers=request_headers
    )
    context = dict(diagnostic or {})
    context["operation"] = operation
    verbose = context.get("mode") == "verbose"
    request_details: dict[str, object] = {"stream": bool(stream)}
    request_payload_content_id = None
    if verbose:
        if request_text is not None:
            diagnostic_request_text = json.dumps(
                _redact_image_urls(payload), ensure_ascii=False
            )
            request_payload_content_id = _diagnostic_store_content(
                context, "http_request_payload", diagnostic_request_text
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
        response = urllib.request.urlopen(request, timeout=timeout)
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
        detail_read_error = None
        try:
            detail_bytes = _bounded_body_read(
                exc, 4096, _request_timeout(), method=method, path=path
            )
        except Exception as body_error:
            detail_bytes = b""
            detail_read_error = body_error
        detail = (detail_bytes.decode("utf-8", "replace")
                  if isinstance(detail_bytes, bytes) else str(detail_bytes))
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
        error = detail_read_error or RuntimeError(f"Agents API HTTP {exc.code}: {detail}")
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
    except (TimeoutError, socket.timeout) as exc:
        elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
        outcome = (" (request outcome may be unknown; check session state before retrying)"
                   if method == "POST" else "")
        error = RuntimeError(
            f"Agents API request timed out after {timeout:g}s: {method} {path}{outcome}"
        )
        _diagnostic_event(
            context, "http_request_failed", payload={"stream": bool(stream)},
            http_method=method, url=path, local_request_id=request_id,
            elapsed_ms=elapsed_ms, error=error,
        )
        raise error from exc
    except urllib.error.URLError as exc:
        elapsed_ms = (time.monotonic_ns() - started_ns) / 1_000_000
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            outcome = (" (request outcome may be unknown; check session state before retrying)"
                       if method == "POST" else "")
            error = RuntimeError(
                f"Agents API request timed out after {timeout:g}s: {method} {path}{outcome}"
            )
        else:
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
        stream_socket = _response_socket(response)
        if stream_socket is not None:
            stream_socket.settimeout(_stream_timeout())
    return _LoggedResponse(
        response, context, method=method, path=path, operation=operation,
        started_ns=started_ns, request_id=request_id,
        provider_request_id=provider_request_id, status=status, stream=stream,
        body_timeout=_request_timeout(),
    )


def _api_get(path, *, diagnostic=None, operation=None):
    with _request(
            "GET", path, diagnostic=diagnostic, operation=operation) as response:
        return json.load(response)


def _api_delete(path, *, diagnostic=None, operation=None):
    with _request("DELETE", path, diagnostic=diagnostic, operation=operation) as response:
        return json.load(response)


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


def _fetch_session_items(session_id, *, diagnostic=None):
    """Fetch all remote items for a session in ascending sequence order."""
    encoded_id = urllib.parse.quote(session_id, safe="")
    items = []
    after = None
    while True:
        query = {"limit": 100, "order": "asc"}
        if after:
            query["after"] = after
        page = _api_get(
            f"/sessions/{encoded_id}/items?{urllib.parse.urlencode(query)}",
            diagnostic=diagnostic, operation="list_session_items",
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


_NUM_RE = r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)'
_REGION4_RE = rf'{_NUM_RE}\s+{_NUM_RE}\s+{_NUM_RE}\s+{_NUM_RE}'
_STR_RE = r's"\s[^"]*"'
_BOOL_RE = r'(?:true|false)'
_TRAIL_RE = r'(?:\s+(?:\.|cr|drop))*'

_READONLY_AI_SEARCH_LINE_RE = re.compile(
    rf'^(?:'
    rf'{_STR_RE}\s+ai-search'
    rf'|ai-search(?:\s+\S.*)?'
    rf'|\(ai-sessions-list\)'
    rf'|desktop-capture{_TRAIL_RE}'
    rf'|{_REGION4_RE}\s+desktop-capture-region{_TRAIL_RE}'
    rf'|{_STR_RE}(?:\s+{_BOOL_RE})?\s+ai-screen{_TRAIL_RE}'
    rf'|{_STR_RE}\s+{_REGION4_RE}(?:\s+{_BOOL_RE})?\s+ai-screen-region{_TRAIL_RE}'
    rf'|{_STR_RE}\s+desktop-capture\s+{_BOOL_RE}\s+ai-image-file{_TRAIL_RE}'
    rf'|{_STR_RE}\s+{_REGION4_RE}\s+desktop-capture-region\s+{_BOOL_RE}\s+ai-image-file{_TRAIL_RE}'
    rf'|{_STR_RE}\s+{_STR_RE}\s+{_BOOL_RE}\s+ai-image-file{_TRAIL_RE}'
    rf')$'
)


def _is_readonly_session_search_forth(source):
    """Return True if Forth source only runs read-only session searches or desktop screen inspection."""
    if not isinstance(source, str):
        return False
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    if not lines:
        return False
    return all(bool(_READONLY_AI_SEARCH_LINE_RE.match(line)) for line in lines)


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
                    "remote_deleted": session.get("remote_deleted", 0),
                },
                "messages": messages,
            }
        if isinstance(query, str) and query.strip():
            matches = store.search_sessions(query.strip(), include_deleted=include_deleted)
            return {
                "sessions": [
                    {
                        "session_id": row["session_id"],
                        "description": row.get("description") or "",
                        "created_at": row.get("created_at"),
                        "last_active_at": row.get("last_active_at"),
                        "remote_deleted": row.get("remote_deleted", 0),
                        "matches": row.get("matches") or [],
                    }
                    for row in matches[:limit]
                ]
            }
        recent = store.list_sessions(include_deleted=include_deleted)
        return {
            "sessions": [
                {
                    "session_id": row["session_id"],
                    "description": row.get("description") or "",
                    "created_at": row.get("created_at"),
                    "last_active_at": row.get("last_active_at"),
                    "status": row.get("status"),
                    "model": row.get("model"),
                    "remote_deleted": row.get("remote_deleted", 0),
                }
                for row in recent[:limit]
            ]
        }


def _agent_instructions():
    skill_names, combined_text = _load_all_skills_text()
    # Optional: include reference documentation for core peforth-forth skill
    skills_root = _source_skills_dir()
    if not skills_root.is_absolute():
        skills_root = (RUNTIME_ROOT / skills_root).resolve()
    reference_path = skills_root / 'peforth-forth' / 'references' / 'forth-reference.md'
    reference_text = reference_path.read_text(encoding="utf-8") if reference_path.is_file() else ""
    intro = (
        "You assist with peforth Forth. Use the live dictionary tool before relying on unfamiliar words. "
        "To recall or search past conversations from the local SQLite session mirror, use the read-only peforth_search_sessions tool (or ai-search), which runs without user approval. "
        "For local shell commands, use the host default_shell from the Runtime capability inventory unless the user explicitly requests another shell or the task requires another shell's syntax. Windows defaults to pwsh; WSL/Linux defaults to bash. The shells entries list available executors and do not override default_shell. "
        "Only the local Forth tool can execute code. Use peforth_tick_heartbeat only for meaningful milestones, not periodic or repeated status messages; it records a diagnostic message and cannot execute Forth. Approval scopes: Yes (allow_once) approves one proposal; Trust this AI task applies only for later proposals in the same AI Task and expires when that Task completes, fails, or is cancelled; Runtime Trust must be explicitly enabled with ai-trust-runtime and lasts in this Forth process until ai-confirm or process exit. ai-confirm revokes Runtime Trust and any active Task Trust. Never infer Trust from a prior Yes or from a different AI Task.\n\n"
    )
    instructions = intro + combined_text
    if reference_text:
        instructions += "\n\nForth reference:\n" + reference_text
    if len(instructions.encode("utf-8")) > 100_000:
        raise RuntimeError("Combined skill texts are too large to include in agent instructions.")
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


def _latest_turn(session_id, *, diagnostic=None):
    encoded_id = urllib.parse.quote(session_id, safe="")
    query = urllib.parse.urlencode({"limit": 1, "order": "desc"})
    page = _api_get(
        f"/sessions/{encoded_id}/turns?{query}", diagnostic=diagnostic,
        operation="list_session_turns",
    )
    rows = page.get("data") or []
    return rows[0] if rows and isinstance(rows[0], dict) else None


def _session_turn_output_text(session_id, turn_id, *, diagnostic=None):
    items = _fetch_session_items(session_id, diagnostic=diagnostic)

    messages = []
    for item in items:
        if (not isinstance(item, dict) or item.get("turn_id") != turn_id
                or item.get("type") != "message" or item.get("role") != "assistant"):
            continue
        text = "".join(
            part.get("text", "") for part in item.get("content", [])
            if isinstance(part, dict) and part.get("type") == "output_text"
            and isinstance(part.get("text"), str)
        )
        if text:
            messages.append((item.get("phase"), text))
    final_messages = [text for phase, text in messages if phase == "final_answer"]
    return "".join(final_messages or [text for _, text in messages])


def _poll_session_events(session_id, previous_turn_id=None, *, diagnostic=None):
    """Poll saved session state/items until the remote turn resolves."""
    encoded_id = urllib.parse.quote(session_id, safe="")
    context = dict(diagnostic or {})
    context["session_id"] = session_id
    interval = _poll_interval()
    target_turn_id = None
    action_signature = None

    while True:
        session = _api_get(
            f"/sessions/{encoded_id}", diagnostic=context,
            operation="poll_session_state",
        )
        latest = _latest_turn(session_id, diagnostic=context)
        if (latest and isinstance(latest.get("id"), str)
                and latest["id"] != previous_turn_id):
            target_turn_id = latest["id"]

        status = session.get("status")
        if status == "requires_action":
            actions = session.get("required_actions") or []
            signature = tuple(sorted(
                tuple(str(action.get(key) or "")
                      for key in ("type", "call_id", "request_id"))
                for action in actions if isinstance(action, dict)
            ))
            if signature != action_signature:
                if target_turn_id is None:
                    target_turn_id = next((
                        action.get("turn_id") for action in actions
                        if isinstance(action, dict) and action.get("turn_id")
                    ), None)
                yield {"type": "agent.session.requires_action", "session": session}
                action_signature = signature
        else:
            action_signature = None

        if status == "failed":
            error = session.get("error") or "The session failed."
            raise RuntimeError(f"Agents API session failed: {error}")

        if latest and latest.get("id") == target_turn_id:
            turn_status = latest.get("status")
            if turn_status == "completed":
                output = _session_turn_output_text(
                    session_id, target_turn_id, diagnostic=context
                )
                if output:
                    yield {"type": "agent.session.turn.output_text.delta", "delta": output}
                yield {"type": "agent.session.turn.output_text.done", "text": output}
                yield {
                    "type": "agent.session.turn.completed", "session_id": session_id,
                    "turn_id": target_turn_id, "turn": latest,
                }
                return
            if turn_status in {"failed", "cancelled", "incomplete"}:
                kind = ("agent.session.turn.cancelled" if turn_status == "cancelled"
                        else "agent.session.turn.failed")
                yield {"type": kind, "session_id": session_id,
                       "turn_id": target_turn_id, "turn": latest}
                return

        time.sleep(interval)


def _create_session(payload, *, diagnostic=None, stream=True):
    request_payload = {**payload, "stream": bool(stream)}
    if stream:
        response = _request(
            "POST", "/sessions", request_payload, stream=True,
            diagnostic=diagnostic, operation="create_session", timeout=_stream_timeout(),
        )
        yield from _event_stream(
            response, diagnostic=diagnostic, operation="create_session",
            timeout=_stream_timeout(),
        )
        return

    with _request(
            "POST", "/sessions", request_payload, diagnostic=diagnostic,
            operation="create_session", timeout=_request_timeout(),
            ) as response:
        session = json.load(response)
    session_id = session.get("id") if isinstance(session, dict) else None
    if not isinstance(session_id, str) or not session_id:
        raise RuntimeError("Agents API created a session without returning its ID.")
    context = dict(diagnostic or {})
    context["session_id"] = session_id
    yield {"type": "agent.session.created", "session": session}
    yield from _poll_session_events(session_id, diagnostic=context)


def _event_stream(response, *, diagnostic=None, operation=None, timeout=None):
    timeout = _stream_timeout() if timeout is None else _configured_seconds(
        "stream timeout", timeout
    )
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
    except (TimeoutError, socket.timeout) as exc:
        error = RuntimeError(
            f"Agents API SSE stream timed out after {timeout:g}s without data."
        )
        _sse_diagnostic_event(
            context, response, "sse_stream_failed",
            payload={"elapsed_ms": (time.monotonic_ns() - stream_started_ns) / 1_000_000},
            error=error,
        )
        raise error from exc
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


def _raise_session_event_error(session_id, exc):
    message = str(exc)
    if "Agents API HTTP 500" in message and session_id not in message:
        raise RuntimeError(
            f"{message}\n"
            f"Remote session {session_id} returned an internal server error on /events "
            "and appears corrupted on OpenAI's server. "
            "Use ai-use to switch to another session, ai-new to start a new session, "
            "or ai-cleanup to delete this broken session."
        ) from exc
    raise exc


def _drain_failed_sse_stream(response, *, diagnostic=None, operation=None):
    sock = _response_socket(response)
    if sock is None or response.closed:
        return
    try:
        sock.settimeout(0.2)
        for _ in _event_stream(
                response, diagnostic=diagnostic, operation=operation, timeout=0.2):
            pass
    except Exception:
        pass


def _sse_open_fallback_error(error):
    if isinstance(error, urllib.error.HTTPError):
        return False
    if isinstance(error, (TimeoutError, socket.timeout, ConnectionError)):
        return True
    message = str(error)
    return isinstance(error, RuntimeError) and message.startswith((
        "Agents API request timed out after", "Agents API connection failed:"
    ))


def _stream(session_id, event, *, diagnostic=None, stream=True):
    encoded_id = urllib.parse.quote(session_id, safe="")
    operation = "continue_session"
    if not stream:
        previous_turn = _latest_turn(session_id, diagnostic=diagnostic)
        previous_turn_id = previous_turn.get("id") if previous_turn else None
        try:
            with _request(
                    "POST", f"/sessions/{encoded_id}/events", {"events": [event]},
                    diagnostic=diagnostic, operation="submit_session_event",
                    timeout=_request_timeout(), headers={"Idempotency-Key": str(uuid.uuid4())}) as accepted:
                accepted.read()
        except RuntimeError as exc:
            _raise_session_event_error(session_id, exc)
        context = dict(diagnostic or {})
        context["session_id"] = session_id
        yield from _poll_session_events(
            session_id, previous_turn_id, diagnostic=context
        )
        return

    submitted = False

    def submit_event():
        nonlocal submitted
        if submitted:
            return
        submitted = True
        with _request(
                "POST", f"/sessions/{encoded_id}/events", {"events": [event]},
                diagnostic=diagnostic, operation="submit_session_event") as accepted:
            accepted.read()

    try:
        response = _request(
            "GET", f"/sessions/{encoded_id}/events?stream=true", stream=True,
            diagnostic=diagnostic, operation=operation, timeout=_sse_open_grace(),
        )
    except Exception as exc:
        if not _sse_open_fallback_error(exc):
            raise
        context = dict(diagnostic or {})
        context["session_id"] = session_id
        _diagnostic_event(
            context, "sse_open_fallback_to_poll",
            payload={"fallback": "post_then_poll", "error_type": type(exc).__name__},
            error=exc,
        )
        yield from _stream(session_id, event, diagnostic=diagnostic, stream=False)
        return

    try:
        try:
            submit_event()
        except RuntimeError as exc:
            _drain_failed_sse_stream(
                response, diagnostic=diagnostic, operation=operation
            )
            _raise_session_event_error(session_id, exc)
        yield from _event_stream(
            response, diagnostic=diagnostic, operation=operation,
            timeout=_stream_timeout(),
        )
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


def _tool_result(session_id, action, success, output="", error="", *, diagnostic=None,
                 persist_result=True):
    result_text = output if success else error
    result_content_id = (
        _diagnostic_store_content(diagnostic, "tool_result", result_text)
        if persist_result else None
    )
    event = {"type": "agent.session.input.tool_result", "turn_id": action["turn_id"],
             "call_id": action["call_id"], "success": success}
    event["output" if success else "error"] = result_text
    encoded_id = urllib.parse.quote(session_id, safe="")
    started_ns = time.monotonic_ns()
    request_diagnostic = diagnostic
    if not persist_result and isinstance(diagnostic, dict):
        request_diagnostic = dict(diagnostic)
        request_diagnostic["mode"] = "standard"
    try:
        with _request(
                "POST", f"/sessions/{encoded_id}/events", {"events": [event]},
                diagnostic=request_diagnostic, operation="submit_tool_result") as response:
            response.read()
    except Exception as exc:
        _diagnostic_action_event(
            diagnostic, "tool_result_submit_failed", action,
            content_id=result_content_id, error=exc,
            elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
            payload={"success": success, "result_persisted": persist_result},
        )
        raise
    _diagnostic_action_event(
        diagnostic, "tool_result_submitted", action, content_id=result_content_id,
        elapsed_ms=(time.monotonic_ns() - started_ns) / 1_000_000,
        payload={"success": success, "result_persisted": persist_result},
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


def _wait_for_current_actions(session_id, *, diagnostic=None, attempts=3):
    """Retry an event-triggered state read while the session is transitioning."""
    attempts = max(1, int(attempts))
    status, actions = None, []
    for attempt in range(attempts):
        status, actions = _current_actions(session_id, diagnostic=diagnostic)
        if status == "requires_action" and actions:
            return status, actions
        if status not in {"in_progress", "requires_action"}:
            return status, actions
        if attempt + 1 < attempts:
            time.sleep(_poll_interval())
    return status, actions


def _reconcile_stream_turn(session_id, turn_id, *, diagnostic=None, attempts=3):
    """Read the current turn status and saved answer for an SSE reconciliation."""
    if not isinstance(turn_id, str) or not turn_id:
        return None, None
    attempts = max(1, int(attempts))
    matched = None
    for attempt in range(attempts):
        latest = _latest_turn(session_id, diagnostic=diagnostic)
        if isinstance(latest, dict) and latest.get("id") == turn_id:
            matched = latest
            if latest.get("status") != "in_progress":
                break
        if attempt + 1 < attempts:
            time.sleep(_poll_interval())
    if matched is None:
        return None, None
    status = matched.get("status")
    output = (
        _session_turn_output_text(session_id, turn_id, diagnostic=diagnostic)
        if status == "completed" else None
    )
    return status, output


def _normalize_surrogates(text):
    """Convert UTF-16 surrogate code points to valid Unicode scalars."""
    normalized = []
    index = 0
    while index < len(text):
        codepoint = ord(text[index])
        if 0xD800 <= codepoint <= 0xDBFF:
            if index + 1 < len(text):
                low = ord(text[index + 1])
                if 0xDC00 <= low <= 0xDFFF:
                    normalized.append(chr(0x10000 + ((codepoint - 0xD800) << 10) + (low - 0xDC00)))
                    index += 2
                    continue
            normalized.append("\uFFFD")
        elif 0xDC00 <= codepoint <= 0xDFFF:
            normalized.append("\uFFFD")
        else:
            normalized.append(text[index])
        index += 1
    return "".join(normalized)


def _run(vm, source):
    stdout, stderr = io.StringIO(), io.StringIO()
    previous_execution_depth = vm.host.get("_ai_forth_execution", 0)
    vm.host["_ai_forth_execution"] = previous_execution_depth + 1
    try:
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                task = vm.dictate(source)
        finally:
            if previous_execution_depth:
                vm.host["_ai_forth_execution"] = previous_execution_depth
            else:
                vm.host.pop("_ai_forth_execution", None)
        if task.status == "paused":
            task.cancel()
            return json.dumps({"status": "error", "error": "Async pause is not supported in AI execution"})
        result = {"status": task.status, "stack": repr(vm.stack),
                  "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}
    except Exception as exc:
        result = {"status": "error", "error": str(exc), "stack": repr(vm.stack),
                  "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}
    result = {
        key: _normalize_surrogates(value) if isinstance(value, str) else value
        for key, value in result.items()
    }
    return json.dumps(result, ensure_ascii=False)


def _session_id_from_event(event):
    session = event.get("session") or event.get("data") or {}
    if isinstance(session, dict):
        return session.get("id") or session.get("session_id") or event.get("session_id")
    return event.get("session_id")


def _saved_session(vm):
    return vm.host.get("ai_active_session_id") or ""


def _diagnostic_start_turn(vm, prompt, *, instructions=None, session_id=None,
                           terminal_output_stream=True, api_transport_stream=True):
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
            payload={
                "one_shot": bool(vm.host.get("one_shot", False)),
                "repl_mode": vm.host.get("repl_mode"),
                "terminal_output_stream": bool(terminal_output_stream),
                "api_transport_stream": bool(api_transport_stream),
            },
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
