"""SQLite-backed diagnostic logging for peforth runtimes."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS contents (
    content_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL,
    content_type TEXT NOT NULL,
    content_text TEXT NOT NULL,
    content_size INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(content_type, content_hash)
);
CREATE TABLE IF NOT EXISTS runtimes (
    runtime_id TEXT PRIMARY KEY,
    process_id INTEGER NOT NULL,
    parent_process_id INTEGER,
    environment TEXT NOT NULL,
    os_name TEXT NOT NULL,
    hostname TEXT,
    username TEXT,
    working_directory TEXT,
    source_path TEXT,
    runtime_path TEXT,
    runtime_version TEXT,
    git_revision TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    exit_status TEXT,
    metadata_json TEXT
);
CREATE TABLE IF NOT EXISTS turns (
    turn_id TEXT PRIMARY KEY,
    runtime_id TEXT NOT NULL,
    remote_session_id TEXT,
    remote_turn_id TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    prompt_content_id INTEGER,
    instructions_content_id INTEGER,
    output_content_id INTEGER,
    output_status TEXT,
    status TEXT,
    error_type TEXT,
    error_message TEXT,
    metadata_json TEXT,
    FOREIGN KEY (runtime_id) REFERENCES runtimes(runtime_id),
    FOREIGN KEY (prompt_content_id) REFERENCES contents(content_id),
    FOREIGN KEY (instructions_content_id) REFERENCES contents(content_id),
    FOREIGN KEY (output_content_id) REFERENCES contents(content_id)
);
CREATE TABLE IF NOT EXISTS timeline (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    runtime_id TEXT NOT NULL,
    turn_id TEXT,
    recorded_at TEXT NOT NULL,
    monotonic_ns INTEGER NOT NULL,
    sequence_no INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    session_id TEXT,
    remote_turn_id TEXT,
    call_id TEXT,
    operation TEXT,
    http_method TEXT,
    url TEXT,
    http_status INTEGER,
    local_request_id TEXT,
    provider_request_id TEXT,
    elapsed_ms REAL,
    content_id INTEGER,
    payload_json TEXT,
    error_type TEXT,
    error_message TEXT,
    FOREIGN KEY (runtime_id) REFERENCES runtimes(runtime_id),
    FOREIGN KEY (turn_id) REFERENCES turns(turn_id),
    FOREIGN KEY (content_id) REFERENCES contents(content_id)
);
CREATE INDEX IF NOT EXISTS idx_turns_runtime_time ON turns(runtime_id, started_at, turn_id);
CREATE INDEX IF NOT EXISTS idx_turns_session_time ON turns(remote_session_id, started_at, turn_id);
CREATE INDEX IF NOT EXISTS idx_timeline_runtime_time ON timeline(runtime_id, recorded_at, event_id);
CREATE INDEX IF NOT EXISTS idx_timeline_turn_time ON timeline(turn_id, recorded_at, event_id);
CREATE INDEX IF NOT EXISTS idx_timeline_session_time ON timeline(session_id, recorded_at, event_id);
CREATE INDEX IF NOT EXISTS idx_timeline_type_time ON timeline(event_type, recorded_at, event_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DiagnosticLog:
    """Small per-runtime writer for a shared environment SQLite database."""

    def __init__(self, path: str | os.PathLike[str], *, environment: str,
                 busy_timeout_ms: int = 250, write_deadline_ms: int = 500):
        if environment not in {"windows", "wsl"}:
            raise ValueError("environment must be 'windows' or 'wsl'")
        if busy_timeout_ms < 0:
            raise ValueError("busy_timeout_ms must not be negative")
        if write_deadline_ms <= 0:
            raise ValueError("write_deadline_ms must be positive")
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.environment = environment
        self.busy_timeout_ms = busy_timeout_ms
        self.write_deadline_ms = write_deadline_ms
        self.connection = sqlite3.connect(str(self.path), timeout=busy_timeout_ms / 1000)
        self.connection.row_factory = sqlite3.Row
        try:
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute(f"PRAGMA busy_timeout = {int(busy_timeout_ms)}")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._migrate_schema()
        except Exception:
            self.connection.close()
            raise
        self._sequence = 0

    def _migrate_schema(self) -> None:
        version = int(self.connection.execute("PRAGMA user_version").fetchone()[0])
        if version > SCHEMA_VERSION:
            raise RuntimeError(
                f"database schema version {version} is newer schema version {SCHEMA_VERSION}"
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
            self.connection.rollback()
            raise

    def _set_busy_timeout_for_deadline(self, deadline_ns: int) -> None:
        remaining_ns = deadline_ns - time.monotonic_ns()
        if remaining_ns <= 0:
            raise TimeoutError("diagnostic log write exceeded its deadline")
        remaining_ms = max(1, (remaining_ns + 999_999) // 1_000_000)
        timeout_ms = min(self.busy_timeout_ms, remaining_ms)
        self.connection.execute(f"PRAGMA busy_timeout = {timeout_ms}")

    @contextmanager
    def _write_transaction(self):
        deadline_ns = time.monotonic_ns() + self.write_deadline_ms * 1_000_000
        try:
            self._set_busy_timeout_for_deadline(deadline_ns)
            try:
                self.connection.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as exc:
                if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                    raise TimeoutError("diagnostic log write exceeded its deadline") from exc
                raise
            yield deadline_ns
            self._commit(deadline_ns)
        except Exception:
            if self.connection.in_transaction:
                self.connection.rollback()
            raise
        finally:
            if not self.connection.in_transaction:
                self.connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")

    def _commit(self, deadline_ns: int) -> None:
        self._set_busy_timeout_for_deadline(deadline_ns)
        try:
            self.connection.commit()
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                raise TimeoutError("diagnostic log write exceeded its deadline") from exc
            raise

    def start_runtime(self, *, process_id: int | None = None, runtime_id: str | None = None,
                      source_path: str | None = None, runtime_path: str | None = None,
                      runtime_version: str | None = None, git_revision: str | None = None,
                      metadata: dict | None = None) -> str:
        runtime_id = runtime_id or str(uuid.uuid4())
        with self._write_transaction():
            self.connection.execute(
                """INSERT INTO runtimes
                (runtime_id, process_id, parent_process_id, environment, os_name,
                 hostname, username, working_directory, source_path, runtime_path,
                 runtime_version, git_revision, started_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (runtime_id, process_id if process_id is not None else os.getpid(),
                 os.getppid(), self.environment, os.name, os.uname().nodename if hasattr(os, "uname") else None,
                 os.environ.get("USERNAME") or os.environ.get("USER"), str(Path.cwd()),
                 source_path, runtime_path, runtime_version, git_revision, _now(),
                 json.dumps(metadata or {}, ensure_ascii=False)),
            )
        self.append_event(runtime_id, None, "runtime_started")
        return runtime_id

    def finish_runtime(self, runtime_id: str, *, exit_status: str | None = None) -> None:
        sequence_no = self._sequence + 1
        with self._write_transaction():
            cursor = self.connection.execute(
                "UPDATE runtimes SET finished_at = ?, exit_status = ? WHERE runtime_id = ?",
                (_now(), exit_status, runtime_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"unknown runtime_id: {runtime_id!r}")
            self.connection.execute(
                """INSERT INTO timeline
                (runtime_id, recorded_at, monotonic_ns, sequence_no, event_type)
                VALUES (?, ?, ?, ?, ?)""",
                (runtime_id, _now(), time.monotonic_ns(), sequence_no, "runtime_finished"),
            )
        self._sequence = sequence_no

    def _store_content_in_transaction(self, content_type: str, text: str) -> int:
        if not isinstance(text, str):
            raise TypeError("content text must be a string")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        self.connection.execute(
            "INSERT OR IGNORE INTO contents(content_hash, content_type, content_text, content_size, created_at) VALUES (?, ?, ?, ?, ?)",
            (digest, content_type, text, len(text.encode("utf-8")), _now()),
        )
        row = self.connection.execute(
            "SELECT content_id FROM contents WHERE content_type = ? AND content_hash = ?",
            (content_type, digest),
        ).fetchone()
        return int(row[0])

    def store_content(self, content_type: str, text: str) -> int:
        with self._write_transaction():
            content_id = self._store_content_in_transaction(content_type, text)
        return content_id

    def set_turn_session(self, turn_id: str, session_id: str) -> None:
        with self._write_transaction():
            cursor = self.connection.execute(
                "UPDATE turns SET remote_session_id = ? WHERE turn_id = ?",
                (session_id, turn_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"unknown turn_id: {turn_id!r}")

    def finish_turn(self, turn_id: str, *, output_text: str | None,
                    output_status: str, status: str, error_type: str | None = None,
                    error_message: str | None = None) -> None:
        valid_output_statuses = {"complete", "partial", "empty", "failed_before_output"}
        valid_statuses = {"completed", "failed", "partial", "cancelled"}
        if output_status not in valid_output_statuses:
            raise ValueError(f"invalid output_status: {output_status!r}")
        if status not in valid_statuses:
            raise ValueError(f"invalid turn status: {status!r}")
        if output_text is not None and not isinstance(output_text, str):
            raise TypeError("output_text must be a string or None")
        if output_status in {"complete", "partial"} and output_text is None:
            raise ValueError(f"output_text is required for {output_status!r} output")

        with self._write_transaction():
            content_type = {"complete": "output", "partial": "partial_output",
                            "empty": "output", "failed_before_output": None}[output_status]
            output_content_id = (
                self._store_content_in_transaction(content_type, output_text)
                if output_text is not None and content_type is not None else None
            )
            cursor = self.connection.execute(
                """UPDATE turns
                SET ended_at = ?, output_content_id = ?, output_status = ?, status = ?,
                    error_type = ?, error_message = ?
                WHERE turn_id = ?""",
                (_now(), output_content_id, output_status, status, error_type, error_message, turn_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"unknown turn_id: {turn_id!r}")

    def start_turn(self, runtime_id: str, *, prompt_content_id: int | None = None,
                   instructions_content_id: int | None = None, remote_session_id: str | None = None,
                   remote_turn_id: str | None = None, turn_id: str | None = None) -> str:
        turn_id = turn_id or str(uuid.uuid4())
        with self._write_transaction():
            self.connection.execute(
                """INSERT INTO turns
                (turn_id, runtime_id, remote_session_id, remote_turn_id, started_at,
                 prompt_content_id, instructions_content_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (turn_id, runtime_id, remote_session_id, remote_turn_id, _now(),
                 prompt_content_id, instructions_content_id),
            )
        return turn_id

    def append_event(self, runtime_id: str, turn_id: str | None, event_type: str,
                     *, payload: dict | None = None, session_id: str | None = None,
                     remote_turn_id: str | None = None, call_id: str | None = None,
                     operation: str | None = None, http_method: str | None = None,
                     url: str | None = None, http_status: int | None = None,
                     local_request_id: str | None = None,
                     provider_request_id: str | None = None, elapsed_ms: float | None = None,
                     content_id: int | None = None, error_type: str | None = None,
                     error_message: str | None = None) -> int:
        sequence_no = self._sequence + 1
        with self._write_transaction():
            cursor = self.connection.execute(
                """INSERT INTO timeline
                (runtime_id, turn_id, recorded_at, monotonic_ns, sequence_no,
                 event_type, session_id, remote_turn_id, call_id, operation, http_method, url,
                 http_status, local_request_id, provider_request_id, elapsed_ms,
                 content_id, payload_json, error_type, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (runtime_id, turn_id, _now(), time.monotonic_ns(), sequence_no,
                 event_type, session_id, remote_turn_id, call_id, operation, http_method, url,
                 http_status, local_request_id, provider_request_id, elapsed_ms,
                 content_id,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True) if payload is not None else None,
                 error_type, error_message),
            )
            event_id = cursor.lastrowid
        self._sequence = sequence_no
        return int(event_id)

    def close(self) -> None:
        self.connection.close()


__all__ = ["DiagnosticLog", "SCHEMA_VERSION"]
