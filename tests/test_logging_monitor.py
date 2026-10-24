import io
import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.peforth_logging_monitor import (
    _start_message_box,
    format_event,
    iter_new_events,
    list_runtime_ids,
    render_events,
    main,
    parser,
)


class LoggingMonitorTests(unittest.TestCase):
    def test_format_event_includes_timestamp_emoji_and_short_description(self):
        row = {
            "recorded_at": "2026-10-21T08:00:00+00:00",
            "event_type": "sse_event_received",
            "operation": "stream_response",
            "http_status": None,
            "error_type": None,
            "error_message": None,
            "payload_json": json.dumps({"event_type": "agent.session.turn.in_progress"}),
            "runtime_id": "123456789abcdef",
            "turn_id": "turn-123456789",
        }
        rendered = format_event(row)
        self.assertIn("16:00:00", rendered)
        self.assertIn("12345678 ", rendered)
        self.assertIn("📨", rendered)
        self.assertIn("SSE event received", rendered)
        self.assertNotIn("123456789abcdef", rendered)

    def test_list_runtime_ids_returns_eight_character_prefixes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ai-diagnostics.sqlite3"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE runtimes (runtime_id TEXT, started_at TEXT)")
            connection.executemany(
                "INSERT INTO runtimes VALUES (?, ?)",
                [("abcdef123456", "2026-01-01"), ("0123456789ab", "2026-01-02")],
            )
            connection.commit()
            self.assertEqual(
                list_runtime_ids(connection),
                [("abcdef12", "abcdef123456"), ("01234567", "0123456789ab")],
            )
            connection.close()

    def test_iter_new_events_returns_only_events_after_event_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ai-diagnostics.sqlite3"
            connection = sqlite3.connect(path)
            connection.executescript("""
                CREATE TABLE timeline (
                    event_id INTEGER PRIMARY KEY, runtime_id TEXT, turn_id TEXT,
                    recorded_at TEXT, event_type TEXT, operation TEXT,
                    http_status INTEGER, error_type TEXT, error_message TEXT,
                    payload_json TEXT
                );
                INSERT INTO timeline VALUES
                    (1, 'r', NULL, '2026-01-01T00:00:00+00:00', 'runtime_started', NULL, NULL, NULL, NULL, NULL),
                    (2, 'r', NULL, '2026-01-01T00:00:01+00:00', 'http_request_started', 'x', NULL, NULL, NULL, '{}');
            """)
            connection.commit()
            rows = iter_new_events(connection, 1)
            self.assertEqual([row["event_id"] for row in rows], [2])
            connection.close()

    def test_help_is_available(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("Monitor peforth SQLite diagnostic logging", output.getvalue())
        self.assertIn("--database", output.getvalue())

    def test_main_loads_dotenv_before_resolving_database_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text(
                "LINE_CHANNEL_ACCESS_TOKEN=test-token\nLINE_USER_ID=test-user\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with patch.dict(os.environ, {
                    "PEFORTH_CONFIG_DIR": tmp,
                    "LINE_CHANNEL_ACCESS_TOKEN": "",
                    "LINE_USER_ID": "",
            }), redirect_stdout(output):
                with self.assertRaises(SystemExit) as raised:
                    main(["--help"])
                self.assertEqual(os.environ["LINE_CHANNEL_ACCESS_TOKEN"], "test-token")
                self.assertEqual(os.environ["LINE_USER_ID"], "test-user")

            self.assertEqual(raised.exception.code, 0)
            help_text = "".join(output.getvalue().split())
            self.assertIn(str(Path(tmp) / "ai-diagnostics.sqlite3"), help_text)

    def test_runtime_map_command_prints_short_and_full_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ai-diagnostics.sqlite3"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE runtimes (runtime_id TEXT, started_at TEXT)")
            connection.execute("INSERT INTO runtimes VALUES ('abcdef123456', '2026-01-01')")
            connection.commit()
            connection.close()
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--database", str(path), "--runtime-map"]), 0)
            self.assertIn("abcdef12  abcdef123456", output.getvalue())

    def test_watchdog_options_accept_large_finite_lookback_and_reject_invalid_values(self):
        args = parser().parse_args(["--watchdog", "--orphan-lookback-hours", "1000"])
        self.assertTrue(args.watchdog)
        self.assertEqual(args.orphan_lookback_hours, 1000)
        for value in ("0", "-1", "inf", "nan"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                parser().parse_args(["--orphan-lookback-hours", value])

    def test_message_box_is_launched_as_a_waiting_child_process(self):
        issue = {"title": "title", "message": "message"}
        with patch("tools.peforth_logging_monitor.subprocess.Popen") as popen:
            child = _start_message_box(issue)
        command = popen.call_args.args[0]
        self.assertIn("--notify", command)
        self.assertIn("--wait", command)
        self.assertEqual(command[-4:], ["--title", "title", "--message", "message"])
        self.assertIs(child, popen.return_value)

    def test_notifier_child_calls_windows_adapter_only_in_wait_mode(self):
        with patch("tools.peforth_logging_monitor._show_message_box") as show:
            self.assertEqual(main(["--notify", "--wait", "--title", "title",
                                   "--message", "message"]), 0)
        show.assert_called_once_with("title", "message")

    def test_render_events_collapses_adjacent_identical_events_with_count(self):
        rows = [{
            "event_id": index,
            "recorded_at": "2026-10-21T08:00:00+00:00",
            "event_type": "sse_event_received",
            "operation": "continue_session",
            "http_status": 200,
            "error_type": None,
            "error_message": None,
            "payload_json": json.dumps({"event_type": "agent.session.turn.output_text.delta"}),
            "runtime_id": "123456789abcdef",
        } for index in range(1, 12)]
        rendered = render_events(rows)
        self.assertEqual(len(rendered), 1)
        self.assertIn("×11", rendered[0])


if __name__ == "__main__":
    unittest.main()
