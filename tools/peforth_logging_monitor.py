"""Live terminal monitor for peforth SQLite diagnostic logging."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from urllib.parse import quote


EMOJI = {
    "runtime_started": "🚀",
    "runtime_finished": "🏁",
    "http_request_started": "🌐",
    "http_response_received": "✅",
    "http_request_failed": "❌",
    "http_response_payload": "📦",
    "http_response_closed": "🔒",
    "sse_stream_opened": "📡",
    "sse_event_received": "📨",
    "sse_heartbeat": "💓",
    "sse_stream_completed": "✅",
    "sse_stream_failed": "❌",
    "sse_stream_closed": "🔌",
    "tool_call_started": "🛠️",
    "tool_result_submitted": "📤",
    "approval_requested": "🙋",
    "approval_received": "👍",
    "forth_execution_started": "▶️",
    "forth_execution_finished": "⏹️",
}


def default_database() -> Path:
    configured = os.environ.get("PEFORTH_CONFIG_DIR")
    directory = Path(configured).expanduser() if configured else Path.home() / ".peforth"
    return directory / "ai-diagnostics.sqlite3"


def connect_readonly(path: Path) -> sqlite3.Connection:
    resolved = str(path.expanduser().resolve())
    uri = f"file:{quote(resolved, safe='/:')}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def iter_new_events(connection: sqlite3.Connection, last_event_id: int) -> list[dict]:
    cursor = connection.execute(
        "SELECT * FROM timeline WHERE event_id > ? ORDER BY event_id", (last_event_id,)
    )
    rows = cursor.fetchall()
    if cursor.description and rows and not isinstance(rows[0], sqlite3.Row):
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in rows]
    return [dict(row) for row in rows]


def list_runtime_ids(connection: sqlite3.Connection) -> list[tuple[str, str]]:
    """Return stable four-character labels and their full runtime UUIDs."""
    rows = connection.execute(
        "SELECT runtime_id FROM runtimes ORDER BY started_at, runtime_id"
    ).fetchall()
    runtime_ids = [row[0] for row in rows]
    labels = [runtime_id[:4] for runtime_id in runtime_ids]
    if len(labels) != len(set(labels)):
        raise ValueError("runtime ID prefix collision; use the full UUID to disambiguate")
    return list(zip(labels, runtime_ids))


def _payload(row: dict) -> dict:
    try:
        value = json.loads(row.get("payload_json") or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def _time(value: str | None) -> str:
    if not value:
        return "??:??:??"
    try:
        return datetime.fromisoformat(value).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def _description(row: dict) -> str:
    event_type = row.get("event_type") or "unknown event"
    descriptions = {
        "runtime_started": "runtime started",
        "runtime_finished": "runtime finished",
        "http_request_started": "HTTP request started",
        "http_response_received": "HTTP response received",
        "http_request_failed": "HTTP request failed",
        "sse_stream_opened": "SSE stream opened",
        "sse_event_received": "SSE event received",
        "sse_heartbeat": "SSE heartbeat",
        "sse_stream_completed": "SSE stream completed",
        "sse_stream_failed": "SSE stream failed",
        "sse_stream_closed": "SSE stream closed",
        "tool_call_started": "tool call started",
        "tool_result_submitted": "tool result submitted",
        "approval_requested": "approval requested",
        "approval_received": "approval received",
        "forth_execution_started": "Forth execution started",
        "forth_execution_finished": "Forth execution finished",
    }
    description = descriptions.get(event_type, event_type.replace("_", " "))
    operation = row.get("operation")
    if operation:
        description += f" ({operation})"
    event_name = _payload(row).get("event_type")
    if event_name and event_name != event_type:
        description += f" [{event_name}]"
    if row.get("http_status") is not None:
        description += f" status={row['http_status']}"
    if row.get("elapsed_ms") is not None:
        description += f" elapsed={row['elapsed_ms']:.0f}ms"
    if row.get("error_message"):
        description += f": {row['error_message']}"
    return description


def format_event(row: dict) -> str:
    event_type = row.get("event_type") or ""
    runtime_label = str(row.get("runtime_id") or "????")[:4].ljust(4, "?")
    return f"[{runtime_label}] {_time(row.get('recorded_at'))} {EMOJI.get(event_type, '🔎')} {_description(row)}"


def _event_key(row: dict) -> tuple:
    """Identify display-equivalent adjacent events without using event_id/time."""
    return (
        str(row.get("runtime_id") or ""), row.get("event_type"), row.get("operation"),
        row.get("http_status"), row.get("error_type"), row.get("error_message"),
        _payload(row).get("event_type"),
    )


def render_events(rows: list[dict]) -> list[str]:
    """Render events, collapsing consecutive display-equivalent events."""
    rendered: list[str] = []
    previous_key = None
    repeat_count = 0
    for row in rows:
        key = _event_key(row)
        if key == previous_key:
            repeat_count += 1
            continue
        if rendered and repeat_count > 1:
            rendered[-1] += f" ×{repeat_count}"
        rendered.append(format_event(row))
        previous_key = key
        repeat_count = 1
    if rendered and repeat_count > 1:
        rendered[-1] += f" ×{repeat_count}"
    return rendered


def monitor(database: Path, interval: float) -> None:
    if interval <= 0:
        raise ValueError("interval must be positive")
    connection = connect_readonly(database)
    last_event_id = 0
    print(f"👀 peforth logging monitor | {database}", flush=True)
    print("   waiting for activity; press Ctrl-C to stop", flush=True)
    try:
        while True:
            events = iter_new_events(connection, last_event_id)
            for line in render_events(events):
                print(line, flush=True)
            if events:
                for row in events:
                    last_event_id = max(last_event_id, int(row["event_id"]))
            time.sleep(interval)
            connection.close()
            connection = connect_readonly(database)
    finally:
        connection.close()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Monitor peforth SQLite diagnostic logging and show live activity."
    )
    result.add_argument(
        "-d", "--database", type=Path, default=default_database(),
        help="SQLite database to monitor (default: %(default)s)",
    )
    result.add_argument(
        "-i", "--interval", type=float, default=0.5,
        help="polling interval in seconds (default: %(default)s)",
    )
    result.add_argument(
        "--runtime-map", action="store_true",
        help="print four-character runtime IDs and full UUIDs, then exit",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.runtime_map:
            connection = connect_readonly(args.database)
            try:
                for short_id, runtime_id in list_runtime_ids(connection):
                    print(f"{short_id}  {runtime_id}")
            finally:
                connection.close()
            return 0
        monitor(args.database, args.interval)
    except KeyboardInterrupt:
        print("\n👋 logging monitor stopped", flush=True)
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f"peforth_logging_monitor: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
