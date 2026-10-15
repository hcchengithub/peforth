import multiprocessing
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from peforth.diagnostic_log import DiagnosticLog


class DiagnosticLogTests(unittest.TestCase):
    def test_same_content_is_stored_once_and_turns_keep_occurrences(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=101)

            first = log.store_content("prompt", "same prompt")
            second = log.store_content("prompt", "same prompt")
            turn_a = log.start_turn(runtime_id, prompt_content_id=first)
            turn_b = log.start_turn(runtime_id, prompt_content_id=second)

            self.assertEqual(first, second)
            self.assertNotEqual(turn_a, turn_b)
            self.assertEqual(log.connection.execute("SELECT COUNT(*) FROM contents").fetchone()[0], 1)
            self.assertEqual(log.connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0], 2)
            log.close()

    def test_connection_enables_foreign_keys_and_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="windows")
            self.assertEqual(log.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertGreater(log.connection.execute("PRAGMA user_version").fetchone()[0], 0)
            log.close()

    def test_turn_remote_session_can_be_recorded_after_session_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=305)
            turn_id = log.start_turn(runtime_id)

            log.set_turn_session(turn_id, "sess-created")

            self.assertEqual(log.connection.execute(
                "SELECT remote_session_id FROM turns WHERE turn_id = ?", (turn_id,)
            ).fetchone()[0], "sess-created")
            log.close()

    def test_finishing_runtime_records_end_time_and_lifecycle_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=304)

            log.finish_runtime(runtime_id, exit_status="0")

            runtime = log.connection.execute(
                "SELECT finished_at, exit_status FROM runtimes WHERE runtime_id = ?", (runtime_id,)
            ).fetchone()
            event = log.connection.execute(
                "SELECT event_type FROM timeline WHERE runtime_id = ? ORDER BY event_id DESC LIMIT 1",
                (runtime_id,),
            ).fetchone()
            self.assertIsNotNone(runtime[0])
            self.assertEqual(runtime[1], "0")
            self.assertEqual(event[0], "runtime_finished")
            log.close()

    def test_runtime_stores_source_and_runtime_identity_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(
                process_id=303, source_path="/checkout", runtime_path="/package",
                runtime_version="3.14.0", git_revision="abc123"
            )
            row = log.connection.execute(
                "SELECT source_path, runtime_path, runtime_version, git_revision "
                "FROM runtimes WHERE runtime_id = ?", (runtime_id,)
            ).fetchone()
            self.assertEqual(tuple(row), ("/checkout", "/package", "3.14.0", "abc123"))
            log.close()

    def test_runtime_can_append_timeline_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=202)
            turn_id = log.start_turn(runtime_id)
            event_id = log.append_event(runtime_id, turn_id, "test_event", payload={"ok": True})
            row = log.connection.execute(
                "SELECT event_type, payload_json FROM timeline WHERE event_id = ?", (event_id,)
            ).fetchone()
            self.assertEqual(tuple(row), ("test_event", '{"ok": true}'))
            log.close()

    def test_timeline_event_stores_http_and_request_timing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=203)
            event_id = log.append_event(
                runtime_id, None, "http_response_received",
                operation="create_session", http_method="POST", url="/sessions",
                http_status=201, local_request_id="req-local",
                provider_request_id="req-provider", elapsed_ms=12.5,
                remote_turn_id="turn-remote", call_id="call-1",
            )

            row = log.connection.execute(
                "SELECT operation, http_method, url, http_status, local_request_id, "
                "provider_request_id, elapsed_ms, remote_turn_id, call_id "
                "FROM timeline WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            self.assertEqual(tuple(row), (
                "create_session", "POST", "/sessions", 201,
                "req-local", "req-provider", 12.5, "turn-remote", "call-1",
            ))
            log.close()

    def test_write_deadline_bounds_wait_for_database_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagnostics.sqlite3"
            log = DiagnosticLog(path, environment="wsl", busy_timeout_ms=5000, write_deadline_ms=40)
            blocker = sqlite3.connect(path)
            blocker.execute("BEGIN IMMEDIATE")
            started = time.monotonic()

            try:
                with self.assertRaises(TimeoutError):
                    log.start_runtime(process_id=303)
                self.assertLess(time.monotonic() - started, 0.5)
                self.assertEqual(log.connection.execute("SELECT COUNT(*) FROM runtimes").fetchone()[0], 0)
            finally:
                blocker.rollback()
                blocker.close()
                log.close()

    def test_schema_migration_is_atomic_when_existing_schema_is_incompatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagnostics.sqlite3"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE turns (turn_id TEXT PRIMARY KEY)")
            connection.commit()
            connection.close()

            with self.assertRaises(sqlite3.OperationalError):
                DiagnosticLog(path, environment="wsl")

            connection = sqlite3.connect(path)
            try:
                self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 0)
                tables = {row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )}
                self.assertNotIn("runtimes", tables)
                self.assertNotIn("contents", tables)
            finally:
                connection.close()

    def test_finishing_turn_stores_deduplicated_output_and_occurrence_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=404)
            first_turn = log.start_turn(runtime_id)
            second_turn = log.start_turn(runtime_id)

            log.finish_turn(first_turn, output_text="answer", output_status="complete",
                            status="completed")
            log.finish_turn(second_turn, output_text="answer", output_status="complete",
                            status="completed")

            rows = log.connection.execute(
                "SELECT output_content_id, output_status, status, ended_at "
                "FROM turns ORDER BY started_at, turn_id"
            ).fetchall()
            self.assertEqual(rows[0][0], rows[1][0])
            self.assertEqual((rows[0][1], rows[0][2]), ("complete", "completed"))
            self.assertIsNotNone(rows[0][3])
            self.assertEqual(log.connection.execute("SELECT COUNT(*) FROM contents").fetchone()[0], 1)
            self.assertEqual(log.connection.execute("SELECT content_text FROM contents").fetchone()[0], "answer")
            log.close()

    def test_finishing_turn_without_output_records_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DiagnosticLog(Path(tmp) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = log.start_runtime(process_id=405)
            turn_id = log.start_turn(runtime_id)

            log.finish_turn(turn_id, output_text=None, output_status="failed_before_output",
                            status="failed", error_type="TimeoutError", error_message="timed out")

            row = log.connection.execute(
                "SELECT output_content_id, output_status, status, error_type, error_message "
                "FROM turns WHERE turn_id = ?", (turn_id,)
            ).fetchone()
            self.assertEqual(tuple(row), (None, "failed_before_output", "failed", "TimeoutError", "timed out"))
            log.close()

    def test_new_database_runs_current_schema_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagnostics.sqlite3"
            log = DiagnosticLog(path, environment="wsl")
            try:
                tables = {row[0] for row in log.connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )}
                self.assertTrue({"contents", "runtimes", "turns", "timeline"}.issubset(tables))
                self.assertEqual(log.connection.execute("PRAGMA user_version").fetchone()[0], 1)
            finally:
                log.close()

    def test_database_from_newer_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagnostics.sqlite3"
            connection = sqlite3.connect(path)
            connection.execute("PRAGMA user_version = 99")
            connection.commit()
            connection.close()

            with self.assertRaisesRegex(RuntimeError, "newer schema"):
                DiagnosticLog(path, environment="wsl")


if __name__ == "__main__":
    unittest.main()
