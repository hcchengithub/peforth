"""SQLite-backed local read-only mirror for peforth AI sessions."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    description TEXT,
    created_at INTEGER,
    last_active_at INTEGER,
    synced_at TEXT,
    status TEXT,
    model TEXT,
    remote_deleted INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS session_items (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    turn_id TEXT,
    type TEXT,
    role TEXT,
    raw_json TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC, session_id);
CREATE INDEX IF NOT EXISTS idx_session_items_session_seq ON session_items(session_id, seq ASC);
"""

_TIME_ONLY_DESCRIPTION_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
_CHINESE_SENTENCE_PUNCT = frozenset("。？！；")
_ENGLISH_SENTENCE_PUNCT = frozenset("?!")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_description_time(created_at, *, tz=None) -> str:
    """Format a remote created_at timestamp into static local YYYY-MM-DD HH:mm:ss text."""
    if created_at is None or created_at == "":
        now = datetime.now(timezone.utc)
        local_dt = now.astimezone(tz) if tz is not None else now.astimezone()
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    try:
        dt = datetime.fromtimestamp(int(created_at), timezone.utc)
        local_dt = dt.astimezone(tz) if tz is not None else dt.astimezone()
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OSError, OverflowError):
        if isinstance(created_at, str):
            text = created_at.strip()
            if _TIME_ONLY_DESCRIPTION_RE.match(text):
                return text
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                local_dt = dt.astimezone(tz) if tz is not None else dt.astimezone()
                return local_dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        return str(created_at)


def extract_item_text(item: dict) -> str:
    """Extract concatenated text from a session item dictionary."""
    if not isinstance(item, dict):
        return ""
    content = item.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    output = item.get("output")
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        parts = []
        for part in output:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return ""


def extract_first_user_message_text(items: list[dict] | None) -> str:
    """Return the text of the first user message in the given items list."""
    for item in items or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message" or item.get("role") != "user":
            continue
        text = extract_item_text(item).strip()
        if text:
            return text
    return ""


def extract_first_sentence(text: str, *, max_chars: int = 80) -> str:
    """Extract the first sentence according to SPEC boundary and 80-char rules.

    Sentence break priority (earliest occurrence in the normalized text):
    1. Newline ``\\n``
    2. Chinese terminal punctuation: ``。``, ``？``, ``！``, ``；``
    3. English terminal punctuation: ``?``, ``!``, or ``. `` (period followed by whitespace)

    If the extracted clause exceeds ``max_chars`` Unicode characters, truncate to
    the first ``max_chars`` characters and append ``...``.
    """
    if not isinstance(text, str):
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").lstrip()
    if not normalized:
        return ""

    cut_index = len(normalized)
    length = len(normalized)
    for idx, ch in enumerate(normalized):
        if ch == "\n":
            cut_index = idx
            break
        if ch in _CHINESE_SENTENCE_PUNCT or ch in _ENGLISH_SENTENCE_PUNCT:
            cut_index = idx
            break
        if ch == "." and (idx + 1 < length and normalized[idx + 1].isspace()):
            cut_index = idx
            break

    clause = normalized[:cut_index].strip()
    if len(clause) > max_chars:
        return clause[:max_chars] + "..."
    return clause


def is_complete_description(description: str | None) -> bool:
    """Return True if description already has a complete summary or user customization."""
    if not isinstance(description, str):
        return False
    stripped = description.strip()
    if not stripped:
        return False
    return not bool(_TIME_ONLY_DESCRIPTION_RE.match(stripped))


def build_session_description(
    created_at,
    items: list[dict] | None = None,
    existing_description: str | None = None,
    *,
    tz=None,
) -> str:
    """Generate or preserve a session description according to SPEC rules."""
    if is_complete_description(existing_description):
        return existing_description  # type: ignore[return-value]

    if isinstance(existing_description, str) and _TIME_ONLY_DESCRIPTION_RE.match(existing_description.strip()):
        time_prefix = existing_description.strip()
    else:
        time_prefix = format_description_time(created_at, tz=tz)

    first_user_text = extract_first_user_message_text(items)
    first_sentence = extract_first_sentence(first_user_text)
    if first_sentence:
        return f"{time_prefix} | {first_sentence}" if time_prefix else first_sentence
    return time_prefix


def _normalize_timestamp(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        try:
            return int(stripped)
        except ValueError:
            return stripped
    return str(value)


def _session_model(remote_session: dict) -> str | None:
    if not isinstance(remote_session, dict):
        return None
    model = remote_session.get("model")
    if isinstance(model, str) and model:
        return model
    agent = remote_session.get("agent")
    if isinstance(agent, dict):
        agent_model = agent.get("model")
        if isinstance(agent_model, str) and agent_model:
            return agent_model
    return None


def _row_to_session_dict(row: sqlite3.Row | dict) -> dict:
    data = dict(row)
    session_id = data.get("session_id") or data.get("id") or ""
    model = data.get("model")
    return {
        "id": session_id,
        "session_id": session_id,
        "description": data.get("description") or "",
        "created_at": data.get("created_at"),
        "last_active_at": data.get("last_active_at"),
        "synced_at": data.get("synced_at"),
        "status": data.get("status"),
        "model": model,
        "agent": {"model": model} if model else {},
        "remote_deleted": int(data.get("remote_deleted") or 0),
    }


class SessionStore:
    """SQLite read-only mirror store for remote OpenAI Agents API sessions."""

    def __init__(self, path: str | os.PathLike[str], *, busy_timeout_ms: int = 5000):
        if busy_timeout_ms < 0:
            raise ValueError("busy_timeout_ms must not be negative")
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.busy_timeout_ms = int(busy_timeout_ms)
        self.connection = sqlite3.connect(str(self.path), timeout=max(0.1, self.busy_timeout_ms / 1000))
        self.connection.row_factory = sqlite3.Row
        try:
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._migrate_schema()
        except Exception:
            self.connection.close()
            raise

    def __enter__(self) -> SessionStore:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    def _migrate_schema(self) -> None:
        version = int(self.connection.execute("PRAGMA user_version").fetchone()[0])
        if version > SCHEMA_VERSION:
            raise RuntimeError(
                f"sessions database schema version {version} is newer than supported version {SCHEMA_VERSION}"
            )
        if version == SCHEMA_VERSION:
            return

        migrations = {1: _SCHEMA}
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            while version < SCHEMA_VERSION:
                next_version = version + 1
                script = migrations.get(next_version)
                if script is None:
                    raise RuntimeError(f"no migration available for schema version {next_version}")
                for statement in script.split(";"):
                    if statement.strip():
                        self.connection.execute(statement)
                self.connection.execute(f"PRAGMA user_version = {next_version}")
                version = next_version
            self.connection.commit()
        except Exception:
            if self.connection.in_transaction:
                self.connection.rollback()
            raise

    @contextmanager
    def _transaction(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.commit()
        except Exception:
            if self.connection.in_transaction:
                self.connection.rollback()
            raise

    def get_session(self, session_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return _row_to_session_dict(row) if row is not None else None

    def get_description(self, session_id: str) -> str:
        row = self.connection.execute(
            "SELECT description FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None or not row["description"]:
            return ""
        return str(row["description"])

    def set_description(self, session_id: str, description: str) -> None:
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id must be a non-empty string")
        with self._transaction():
            existing = self.connection.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if existing is None:
                self.connection.execute(
                    "INSERT INTO sessions (session_id, description, remote_deleted) VALUES (?, ?, 0)",
                    (session_id, description),
                )
            else:
                self.connection.execute(
                    "UPDATE sessions SET description = ? WHERE session_id = ?",
                    (description, session_id),
                )

    def needs_item_sync(self, remote_session: dict) -> bool:
        """Return True if a remote session is missing locally, unsynced, or has newer last_active_at."""
        session_id = remote_session.get("id") or remote_session.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return False
        local = self.get_session(session_id)
        if local is None:
            return True
        if not local.get("synced_at"):
            return True
        remote_active = _normalize_timestamp(remote_session.get("last_active_at"))
        local_active = _normalize_timestamp(local.get("last_active_at"))
        if remote_active is None:
            return False
        if local_active is None:
            return True
        if isinstance(remote_active, int) and isinstance(local_active, int):
            return remote_active > local_active
        return str(remote_active) != str(local_active)

    def sync_session(
        self,
        remote_session: dict,
        items: list[dict],
        *,
        synced_at: str | None = None,
        tz=None,
    ) -> dict:
        """Write one session's metadata and items atomically in a single short transaction."""
        session_id = remote_session.get("id") or remote_session.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("remote_session must contain a non-empty 'id'")
        created_at = _normalize_timestamp(remote_session.get("created_at"))
        last_active_at = _normalize_timestamp(remote_session.get("last_active_at"))
        status = remote_session.get("status")
        model = _session_model(remote_session)
        synced_timestamp = synced_at if synced_at is not None else _now_iso()

        with self._transaction():
            existing = self.connection.execute(
                "SELECT description, created_at, model, status FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            existing_desc = existing["description"] if existing is not None else None
            effective_created_at = (
                created_at
                if created_at is not None
                else (existing["created_at"] if existing is not None else None)
            )
            effective_model = model or (existing["model"] if existing is not None else None)
            effective_status = status or (existing["status"] if existing is not None else None)
            description = build_session_description(
                effective_created_at,
                items,
                existing_description=existing_desc,
                tz=tz,
            )

            self.connection.execute(
                """INSERT INTO sessions (
                    session_id, description, created_at, last_active_at,
                    synced_at, status, model, remote_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(session_id) DO UPDATE SET
                    description = excluded.description,
                    created_at = COALESCE(excluded.created_at, sessions.created_at),
                    last_active_at = excluded.last_active_at,
                    synced_at = excluded.synced_at,
                    status = COALESCE(excluded.status, sessions.status),
                    model = COALESCE(excluded.model, sessions.model),
                    remote_deleted = 0
                """,
                (
                    session_id,
                    description,
                    effective_created_at,
                    last_active_at,
                    synced_timestamp,
                    effective_status,
                    effective_model,
                ),
            )

            for seq, item in enumerate(items or []):
                if not isinstance(item, dict):
                    raise TypeError("Each session item must be a dictionary")
                item_id = item.get("id")
                if not isinstance(item_id, str) or not item_id:
                    item_id = f"{session_id}:seq:{seq}"
                turn_id = item.get("turn_id")
                item_type = item.get("type")
                role = item.get("role") if item_type == "message" else None
                raw_json = json.dumps(item, ensure_ascii=False)
                self.connection.execute(
                    """INSERT OR REPLACE INTO session_items (
                        id, session_id, seq, turn_id, type, role, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (item_id, session_id, seq, turn_id, item_type, role, raw_json),
                )

        return self.get_session(session_id)  # type: ignore[return-value]

    def update_session_metadata(self, remote_session: dict) -> None:
        """Update lightweight metadata for an unchanged session without touching items or description."""
        session_id = remote_session.get("id") or remote_session.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return
        created_at = _normalize_timestamp(remote_session.get("created_at"))
        last_active_at = _normalize_timestamp(remote_session.get("last_active_at"))
        status = remote_session.get("status")
        model = _session_model(remote_session)
        with self._transaction():
            self.connection.execute(
                """UPDATE sessions
                SET created_at = COALESCE(?, created_at),
                    last_active_at = COALESCE(?, last_active_at),
                    status = COALESCE(?, status),
                    model = COALESCE(?, model),
                    remote_deleted = 0
                WHERE session_id = ?""",
                (created_at, last_active_at, status, model, session_id),
            )

    def mark_remote_deleted(self, session_id: str, deleted: bool = True) -> None:
        with self._transaction():
            self.connection.execute(
                "UPDATE sessions SET remote_deleted = ? WHERE session_id = ?",
                (1 if deleted else 0, session_id),
            )

    def mark_missing_remote_deleted(self, active_remote_ids: set[str] | list[str] | tuple[str, ...]) -> int:
        active_set = {sid for sid in active_remote_ids if isinstance(sid, str) and sid}
        with self._transaction():
            if not active_set:
                cursor = self.connection.execute(
                    "UPDATE sessions SET remote_deleted = 1 WHERE remote_deleted = 0"
                )
                return int(cursor.rowcount)
            placeholders = ", ".join("?" for _ in active_set)
            cursor = self.connection.execute(
                f"UPDATE sessions SET remote_deleted = 1 "
                f"WHERE remote_deleted = 0 AND session_id NOT IN ({placeholders})",
                tuple(active_set),
            )
            return int(cursor.rowcount)

    def list_sessions(self, *, include_deleted: bool = False) -> list[dict]:
        if include_deleted:
            rows = self.connection.execute(
                "SELECT * FROM sessions ORDER BY COALESCE(created_at, 0) DESC, rowid DESC"
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT * FROM sessions WHERE remote_deleted = 0 "
                "ORDER BY COALESCE(created_at, 0) DESC, rowid DESC"
            ).fetchall()
        return [_row_to_session_dict(row) for row in rows]

    def get_session_items(self, session_id: str) -> list[dict]:
        rows = self.connection.execute(
            "SELECT raw_json FROM session_items WHERE session_id = ? ORDER BY seq ASC",
            (session_id,),
        ).fetchall()
        return [json.loads(row["raw_json"]) for row in rows]

    def export_session_json(self, session_id: str, output_path: str | os.PathLike[str]) -> Path:
        items = self.get_session_items(session_id)
        target = Path(output_path).expanduser()
        if not target.is_absolute():
            target = (Path.cwd() / target).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload_text = json.dumps(items, ensure_ascii=False, indent=2) + "\n"
        target.write_text(payload_text, encoding="utf-8", newline="\n")
        return target

    def get_session_messages(self, session_id: str, *, limit: int = 50) -> list[dict]:
        rows = self.connection.execute(
            "SELECT seq, type, role, raw_json FROM session_items WHERE session_id = ? ORDER BY seq ASC",
            (session_id,),
        ).fetchall()
        messages = []
        for row in rows:
            if row["type"] != "message" or row["role"] not in ("user", "assistant"):
                continue
            try:
                parsed = json.loads(row["raw_json"] or "{}")
            except json.JSONDecodeError:
                parsed = {}
            text = extract_item_text(parsed).strip()
            if text:
                messages.append({
                    "seq": row["seq"],
                    "role": row["role"],
                    "text": text,
                })
        if limit and limit > 0:
            return messages[-limit:]
        return messages

    def search_sessions(self, query: str, *, include_deleted: bool = True) -> list[dict]:
        terms = [term.casefold() for term in (query or "").split() if term.strip()]
        if not terms:
            return []
        sessions = self.list_sessions(include_deleted=include_deleted)
        primary_results = []
        secondary_results = []
        for session in sessions:
            session_id = session["session_id"]
            description = session.get("description") or ""
            item_rows = self.connection.execute(
                "SELECT seq, type, role, raw_json FROM session_items WHERE session_id = ? ORDER BY seq ASC",
                (session_id,),
            ).fetchall()
            message_snippets = []
            other_snippets = []
            searchable_parts = [session_id.casefold(), description.casefold()]
            message_parts = [session_id.casefold(), description.casefold()]
            for item_row in item_rows:
                raw_json = item_row["raw_json"] or ""
                searchable_parts.append(raw_json.casefold())
                try:
                    parsed = json.loads(raw_json)
                except json.JSONDecodeError:
                    parsed = {}
                text = extract_item_text(parsed) or raw_json
                folded_text = text.casefold()
                is_message = item_row["type"] == "message" and item_row["role"] in ("user", "assistant")
                if is_message:
                    message_parts.append(folded_text)
                if any(term in folded_text for term in terms):
                    snippet = " ".join(text.split())
                    if len(snippet) > 160:
                        snippet = snippet[:160] + "..."
                    role_label = item_row["role"] or item_row["type"] or "item"
                    formatted = f"[{role_label}] {snippet}"
                    if is_message:
                        message_snippets.append(formatted)
                    else:
                        other_snippets.append(formatted)

            combined = "\n".join(searchable_parts)
            if all(term in combined for term in terms):
                matched_snippets = (message_snippets + other_snippets)[:5]
                entry = {
                    **session,
                    "matches": matched_snippets,
                }
                if all(term in "\n".join(message_parts) for term in terms):
                    primary_results.append(entry)
                else:
                    secondary_results.append(entry)
        return primary_results + secondary_results


__all__ = [
    "SCHEMA_VERSION",
    "SessionStore",
    "build_session_description",
    "extract_first_sentence",
    "extract_first_user_message_text",
    "extract_item_text",
    "format_description_time",
    "is_complete_description",
]
