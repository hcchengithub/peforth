"""Small Python transport and host helpers used by the Forth AI words."""
from __future__ import annotations

from datetime import datetime, timezone
import io
import json
import os
import re
import tempfile
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


def _request(method, path, payload=None, stream=False):
    load_dotenv()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in ~/.peforth/.env or the process environment to use AI.")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
    request = urllib.request.Request(API + path, data=body, method=method, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "OpenAI-Beta": "agents=v1",
        "Accept": "text/event-stream" if stream else "application/json"})
    try:
        return urllib.request.urlopen(request, timeout=300)
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", "replace")
        raise RuntimeError(f"Agents API HTTP {exc.code}: {detail}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Agents API connection failed: {exc.reason}") from None


def _api_get(path):
    with _request("GET", path) as response:
        return json.load(response)


def _api_delete(path):
    with _request("DELETE", path) as response:
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


def _create_session(payload):
    return _event_stream(_request("POST", "/sessions", payload, stream=True))


def _event_stream(response):
    try:
        data = []
        for raw in response:
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            if line.startswith("data:"):
                data.append(line[5:].lstrip())
            elif not line and data:
                joined = "\n".join(data)
                data.clear()
                if joined != "[DONE]":
                    try:
                        yield json.loads(joined)
                    except json.JSONDecodeError:
                        pass
        if data and "\n".join(data) != "[DONE]":
            yield json.loads("\n".join(data))
    finally:
        response.close()


def _stream(session_id, event):
    encoded_id = urllib.parse.quote(session_id, safe="")
    response = _request("GET", f"/sessions/{encoded_id}/events?stream=true", stream=True)
    try:
        with _request("POST", f"/sessions/{encoded_id}/events", {"events": [event]}) as accepted:
            accepted.read()
        yield from _event_stream(response)
    finally:
        if not response.closed:
            response.close()


def _tool_result(session_id, action, success, output="", error=""):
    event = {"type": "agent.session.input.tool_result", "turn_id": action["turn_id"],
             "call_id": action["call_id"], "success": success}
    event["output" if success else "error"] = output if success else error
    encoded_id = urllib.parse.quote(session_id, safe="")
    with _request("POST", f"/sessions/{encoded_id}/events", {"events": [event]}) as response:
        response.read()


def _current_actions(session_id):
    session = _api_get(f"/sessions/{urllib.parse.quote(session_id, safe='')}")
    return session.get("status"), session.get("required_actions") or []


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


def cancel_turn(vm):
    session_id = _saved_session(vm)
    if session_id:
        with _request("POST", f"/sessions/{urllib.parse.quote(session_id, safe='')}/events", {
                "events": [{"type": "agent.session.input.cancel"}]}) as response:
            response.read()
