import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from peforth.diagnostic_log import DiagnosticLog
from tools import ai_diagnostics


class AiDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "diagnostics.sqlite3"
        self.writer = DiagnosticLog(self.path, environment="wsl")
        self.runtime_id = self.writer.start_runtime(process_id=8801)
        prompt_id = self.writer.store_content("prompt", "reproduce timeout")
        self.turn_id = self.writer.start_turn(
            self.runtime_id, prompt_content_id=prompt_id,
            remote_session_id="session-query", remote_turn_id="remote-turn-query",
        )
        self.writer.append_event(
            self.runtime_id, self.turn_id, "sse_event_received",
            session_id="session-query", remote_turn_id="remote-turn-query",
            call_id="call-query", payload={"event_type": "agent.session.requires_action"},
        )
        self.writer.append_event(
            self.runtime_id, self.turn_id, "current_actions_response_received",
            session_id="session-query", remote_turn_id="remote-turn-query",
            call_id="call-query", operation="get_current_actions",
            payload={"status": "in_progress", "required_action_count": 1},
        )
        self.writer.append_event(
            self.runtime_id, self.turn_id, "sse_stream_failed",
            session_id="session-query", error_type="TimeoutError",
            error_message="read timeout waiting for SSE data",
        )
        self.writer.finish_turn(
            self.turn_id, output_text="partial answer", output_status="partial",
            status="partial", error_type="TimeoutError", error_message="read timeout",
        )

    def tearDown(self):
        self.writer.close()
        self.tmp.cleanup()

    def test_read_only_connection_blocks_writes_and_reads_live_database(self):
        connection = ai_diagnostics.connect_readonly(self.path)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0], 1)
            with self.assertRaises(Exception):
                connection.execute("DELETE FROM turns")
        finally:
            connection.close()
        self.assertEqual(self.writer.connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0], 1)

    def test_runtime_turn_session_and_failure_queries(self):
        with contextlib.closing(ai_diagnostics.connect_readonly(self.path)) as connection:
            self.assertEqual(ai_diagnostics.list_runtimes(connection)[0]["runtime_id"], self.runtime_id)
            self.assertEqual(len(ai_diagnostics.timeline_for_runtime(connection, self.runtime_id)), 4)
            self.assertEqual(len(ai_diagnostics.timeline_for_turn(connection, self.turn_id)), 3)
            self.assertEqual(len(ai_diagnostics.timeline_for_session(connection, "session-query")), 3)
            self.assertEqual(len(ai_diagnostics.find_failed_streams(connection)), 1)
            self.assertEqual(len(ai_diagnostics.find_read_timeouts(connection)), 1)
            pairs = ai_diagnostics.find_requires_action_in_progress(connection)
            self.assertEqual(len(pairs), 1)
            self.assertEqual(pairs[0]["call_id"], "call-query")

    def test_turn_content_and_export_restore_prompt_partial_output_and_timeline(self):
        with contextlib.closing(ai_diagnostics.connect_readonly(self.path)) as connection:
            content = ai_diagnostics.turn_contents(connection, self.turn_id)
            self.assertEqual(content["prompt"], "reproduce timeout")
            self.assertEqual(content["output"], "partial answer")
            self.assertEqual(content["output_status"], "partial")
            exported = ai_diagnostics.export_turn(connection, self.turn_id)
            self.assertEqual(exported["turn"]["turn_id"], self.turn_id)
            self.assertEqual(len(exported["timeline"]), 3)
            self.assertEqual(exported["contents"]["prompt"], "reproduce timeout")

    def test_cli_emits_json_and_uses_read_only_database(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = ai_diagnostics.main([str(self.path), "show-turn", self.turn_id])
        self.assertEqual(result, 0)
        rendered = json.loads(output.getvalue())
        self.assertEqual(rendered["turn"]["turn_id"], self.turn_id)
        connection = ai_diagnostics.connect_readonly(self.path)
        try:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("CREATE TABLE forbidden (x)")
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
