"""Read-only queries for peforth's SQLite AI diagnostic databases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
from urllib.parse import quote


def connect_readonly(path: str | Path) -> sqlite3.Connection:
    """Open an existing diagnostics database without permitting writes."""
    resolved = str(Path(path).expanduser().resolve())
    uri = f"file:{quote(resolved, safe='/:')}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _dict_rows(cursor) -> list[dict]:
    return [dict(row) for row in cursor.fetchall()]


def list_runtimes(connection: sqlite3.Connection, *, limit: int = 100) -> list[dict]:
    if limit < 1:
        raise ValueError("limit must be positive")
    return _dict_rows(connection.execute(
        "SELECT * FROM runtimes ORDER BY started_at DESC, runtime_id LIMIT ?", (limit,)
    ))


def timeline_for_runtime(connection: sqlite3.Connection, runtime_id: str) -> list[dict]:
    return _dict_rows(connection.execute(
        "SELECT * FROM timeline WHERE runtime_id = ? ORDER BY event_id", (runtime_id,)
    ))


def timeline_for_turn(connection: sqlite3.Connection, turn_id: str) -> list[dict]:
    return _dict_rows(connection.execute(
        "SELECT * FROM timeline WHERE turn_id = ? ORDER BY event_id", (turn_id,)
    ))


def timeline_for_session(connection: sqlite3.Connection, session_id: str) -> list[dict]:
    return _dict_rows(connection.execute(
        """SELECT DISTINCT timeline.* FROM timeline
        LEFT JOIN turns ON turns.turn_id = timeline.turn_id
        WHERE timeline.session_id = ? OR turns.remote_session_id = ?
        ORDER BY timeline.event_id""",
        (session_id, session_id),
    ))


def find_failed_streams(connection: sqlite3.Connection) -> list[dict]:
    return _dict_rows(connection.execute(
        """SELECT * FROM timeline
        WHERE event_type IN ('sse_stream_failed', 'sse_parse_failed', 'http_request_failed')
        ORDER BY event_id DESC"""
    ))


def find_read_timeouts(connection: sqlite3.Connection) -> list[dict]:
    rows = _dict_rows(connection.execute(
        """SELECT * FROM timeline
        WHERE event_type IN ('sse_stream_failed', 'http_request_failed', 'sse_read_failed')
        ORDER BY event_id DESC"""
    ))
    return [row for row in rows if "timeout" in (
        str(row.get("error_type") or "") + " " + str(row.get("error_message") or "")
    ).casefold()]


def _event_payload(row: dict) -> dict:
    try:
        value = json.loads(row.get("payload_json") or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def find_requires_action_in_progress(connection: sqlite3.Connection) -> list[dict]:
    rows = _dict_rows(connection.execute(
        """SELECT * FROM timeline WHERE turn_id IS NOT NULL
        AND event_type IN ('sse_event_received', 'current_actions_response_received')
        ORDER BY event_id"""
    ))
    by_turn: dict[str, list[dict]] = {}
    for row in rows:
        by_turn.setdefault(row["turn_id"], []).append(row)
    pairs = []
    for turn_rows in by_turn.values():
        for index, required in enumerate(turn_rows):
            required_payload = _event_payload(required)
            if (required["event_type"] != "sse_event_received"
                    or required_payload.get("event_type") != "agent.session.requires_action"):
                continue
            required_call = required.get("call_id") or required_payload.get("call_id")
            for progress in turn_rows[index + 1:]:
                progress_payload = _event_payload(progress)
                is_status_response = (
                    progress["event_type"] == "current_actions_response_received"
                    and str(progress_payload.get("status", "")).casefold() == "in_progress"
                )
                is_sse_progress = (
                    progress["event_type"] == "sse_event_received"
                    and progress_payload.get("event_type") == "agent.session.turn.in_progress"
                )
                if not (is_status_response or is_sse_progress):
                    continue
                progress_call = progress.get("call_id") or progress_payload.get("call_id")
                if required_call and progress_call and required_call != progress_call:
                    continue
                if (required.get("session_id") and progress.get("session_id")
                        and required["session_id"] != progress["session_id"]):
                    continue
                pairs.append({
                    "turn_id": required["turn_id"],
                    "runtime_id": required["runtime_id"],
                    "session_id": required.get("session_id") or progress.get("session_id"),
                    "call_id": required_call or progress_call,
                    "requires_action": required,
                    "in_progress": progress,
                })
                break
    return pairs


def turn_contents(connection: sqlite3.Connection, turn_id: str) -> dict:
    row = connection.execute(
        """SELECT t.*, prompt.content_text AS prompt_text,
                  instructions.content_text AS instructions_text,
                  output.content_text AS output_text
        FROM turns AS t
        LEFT JOIN contents AS prompt ON prompt.content_id = t.prompt_content_id
        LEFT JOIN contents AS instructions ON instructions.content_id = t.instructions_content_id
        LEFT JOIN contents AS output ON output.content_id = t.output_content_id
        WHERE t.turn_id = ?""", (turn_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"unknown turn_id: {turn_id!r}")
    turn = dict(row)
    return {
        "turn": turn,
        "prompt": turn.pop("prompt_text"),
        "instructions": turn.pop("instructions_text"),
        "output": turn.pop("output_text"),
        "output_status": turn.get("output_status"),
        "status": turn.get("status"),
    }


def export_turn(connection: sqlite3.Connection, turn_id: str) -> dict:
    contents = turn_contents(connection, turn_id)
    return {
        "turn": contents["turn"],
        "contents": {
            "prompt": contents["prompt"],
            "instructions": contents["instructions"],
            "output": contents["output"],
            "output_status": contents["output_status"],
        },
        "timeline": timeline_for_turn(connection, turn_id),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="SQLite diagnostics database (opened read-only)")
    commands = parser.add_subparsers(dest="command", required=True)
    runtimes = commands.add_parser("list-runtimes")
    runtimes.add_argument("--limit", type=int, default=100)
    runtime_timeline = commands.add_parser("runtime-timeline")
    runtime_timeline.add_argument("runtime_id")
    turn_timeline = commands.add_parser("turn-timeline")
    turn_timeline.add_argument("turn_id")
    session_timeline = commands.add_parser("session-timeline")
    session_timeline.add_argument("session_id")
    commands.add_parser("failed-streams")
    commands.add_parser("read-timeouts")
    commands.add_parser("requires-action-in-progress")
    show_turn = commands.add_parser("show-turn")
    show_turn.add_argument("turn_id")
    export = commands.add_parser("export-turn")
    export.add_argument("turn_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    queries = {
        "list-runtimes": lambda db: list_runtimes(db, limit=args.limit),
        "runtime-timeline": lambda db: timeline_for_runtime(db, args.runtime_id),
        "turn-timeline": lambda db: timeline_for_turn(db, args.turn_id),
        "session-timeline": lambda db: timeline_for_session(db, args.session_id),
        "failed-streams": find_failed_streams,
        "read-timeouts": find_read_timeouts,
        "requires-action-in-progress": find_requires_action_in_progress,
        "show-turn": lambda db: turn_contents(db, args.turn_id),
        "export-turn": lambda db: export_turn(db, args.turn_id),
    }
    try:
        connection = connect_readonly(args.database)
        try:
            result = queries[args.command](connection)
        finally:
            connection.close()
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f"ai_diagnostics: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
