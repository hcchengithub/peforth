import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from peforth.diagnostic_log import DiagnosticLog
from tools.peforth_logging_monitor import connect_readonly
from tools.peforth_watchdog import (
    NO_PROGRESS_SECONDS,
    REMINDER_SECONDS,
    ReminderManager,
    Watchdog,
    process_matches_runtime,
    validate_lookback_hours,
)


class FakeChild:
    def __init__(self):
        self.returncode = None

    def poll(self):
        return self.returncode


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ai-diagnostics.sqlite3"
        self.writer = DiagnosticLog(self.path, environment="wsl")
        self.now = datetime.now(timezone.utc)
        self.alive = {}
        self.runtime_ids = {}
        self.connections = []

    def tearDown(self):
        for connection in self.connections:
            connection.close()
        self.writer.close()
        self.tmp.cleanup()

    def add_runtime(self, name, *, alive=True, last_activity=None, open_turn=True,
                    prompt="Watch the long task"):
        runtime_id = self.writer.start_runtime(process_id=5000 + len(self.runtime_ids))
        self.runtime_ids[name] = runtime_id
        self.alive[runtime_id] = alive
        start = last_activity or (self.now - timedelta(minutes=10))
        self.writer.connection.execute(
            "UPDATE runtimes SET started_at = ? WHERE runtime_id = ?",
            (start.isoformat(), runtime_id),
        )
        self.writer.connection.commit()
        event_id = self.writer.connection.execute(
            "SELECT event_id FROM timeline WHERE runtime_id = ? ORDER BY event_id LIMIT 1",
            (runtime_id,),
        ).fetchone()[0]
        self.set_event_time(event_id, start)
        turn_id = ""
        if open_turn:
            prompt_id = self.writer.store_content("prompt", prompt)
            turn_id = self.writer.start_turn(runtime_id, prompt_content_id=prompt_id)
            self.writer.connection.execute(
                "UPDATE turns SET started_at = ? WHERE turn_id = ?",
                (start.isoformat(), turn_id),
            )
            self.writer.connection.commit()
            self.add_event(runtime_id, turn_id, "ai_turn_started", when=start)
        return runtime_id, turn_id

    def set_event_time(self, event_id, when):
        self.writer.connection.execute(
            "UPDATE timeline SET recorded_at = ? WHERE event_id = ?",
            (when.isoformat(), event_id),
        )
        self.writer.connection.commit()

    def add_event(self, runtime_id, turn_id, kind, *, payload=None, call_id=None,
                  remote_turn_id=None, when=None):
        event_id = self.writer.append_event(
            runtime_id, turn_id, kind, payload=payload, call_id=call_id,
            remote_turn_id=remote_turn_id,
        )
        self.set_event_time(event_id, when or self.now)
        return event_id

    def watchdog(self, *, lookback: float = 0):
        connection = connect_readonly(self.path)
        self.connections.append(connection)
        watchdog = Watchdog(
            connection, orphan_lookback_hours=lookback,
            process_checker=lambda row: self.alive.get(row["runtime_id"]),
            now=lambda: self.now,
        )
        watchdog.initialize()
        return watchdog

    def test_no_progress_is_objective_only_and_heartbeat_and_polling_do_not_reset_clock(self):
        runtime_id, turn_id = self.add_runtime("live")
        first_remote_state = self.now - timedelta(minutes=8)
        self.add_event(runtime_id, turn_id, "sse_event_received",
                       payload={"event_type": "agent.session.turn.in_progress"},
                       remote_turn_id="remote-turn", when=first_remote_state)
        self.add_event(runtime_id, turn_id, "sse_event_received",
                       payload={"event_type": "agent.session.heartbeat"},
                       when=self.now - timedelta(minutes=1))
        self.add_event(runtime_id, turn_id, "ai_heartbeat",
                       payload={"message": "still working on it"},
                       when=self.now - timedelta(seconds=30))
        watchdog = self.watchdog()
        issue = watchdog.current_issues()[f"no-progress:{turn_id}"]
        self.assertEqual(issue["last_progress_at"], first_remote_state)
        self.assertIn("still working on it", issue["message"])

    def test_no_progress_threshold_is_inclusive_at_five_minutes(self):
        runtime_id, turn_id = self.add_runtime(
            "boundary", last_activity=self.now - timedelta(seconds=NO_PROGRESS_SECONDS),
        )
        watchdog = self.watchdog()
        self.assertIn(f"no-progress:{turn_id}", watchdog.current_issues())

        self.writer.connection.execute(
            "UPDATE turns SET started_at = ? WHERE turn_id = ?",
            ((self.now - timedelta(seconds=NO_PROGRESS_SECONDS - 1)).isoformat(), turn_id),
        )
        self.writer.connection.commit()
        watchdog.turns[turn_id]["started_at"] = (
            self.now - timedelta(seconds=NO_PROGRESS_SECONDS - 1)
        ).isoformat()
        watchdog.turns[turn_id]["last_progress_at"] = watchdog.turns[turn_id]["started_at"]
        self.assertNotIn(f"no-progress:{turn_id}", watchdog.current_issues())

    def test_state_change_call_id_accepted_result_and_output_growth_are_progress(self):
        runtime_id, turn_id = self.add_runtime("live")
        watchdog = self.watchdog()
        start_progress = watchdog.turns[turn_id]["last_progress_at"]

        transition_time = self.now - timedelta(minutes=4)
        self.add_event(runtime_id, turn_id, "sse_event_received",
                       payload={"event_type": "agent.session.turn.in_progress"},
                       remote_turn_id="remote-1", when=transition_time)
        watchdog.poll()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], transition_time.isoformat())

        repeated_time = self.now - timedelta(minutes=3)
        self.add_event(runtime_id, turn_id, "sse_event_received",
                       payload={"event_type": "agent.session.turn.in_progress"},
                       remote_turn_id="remote-1", when=repeated_time)
        watchdog.poll()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], transition_time.isoformat())

        call_time = self.now - timedelta(minutes=2)
        self.add_event(runtime_id, turn_id, "tool_call_started", call_id="call-1", when=call_time)
        watchdog.poll()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], call_time.isoformat())

        accepted_time = self.now - timedelta(minutes=1)
        self.add_event(runtime_id, turn_id, "tool_result_submitted", call_id="call-1", when=accepted_time)
        watchdog.poll()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], accepted_time.isoformat())

        output_time = self.now
        self.add_event(runtime_id, turn_id, "sse_event_received",
                       payload={"event_type": "agent.session.turn.output_text.delta",
                                "delta_length": 5, "output_length": 5},
                       remote_turn_id="remote-1", when=output_time)
        watchdog.poll()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], output_time.isoformat())
        self.assertNotIn(f"no-progress:{turn_id}", watchdog.current_issues())
        self.assertLess(start_progress, watchdog.turns[turn_id]["last_progress_at"])

    def test_startup_high_water_snapshot_does_not_replay_later_event(self):
        runtime_id, turn_id = self.add_runtime("live")
        watchdog = self.watchdog()
        high_water = watchdog.cursor
        event_id = self.add_event(runtime_id, turn_id, "tool_call_started", call_id="new-call")
        self.assertGreater(event_id, high_water)
        events = watchdog.poll()
        self.assertEqual([event["event_id"] for event in events], [event_id])
        self.assertEqual(watchdog.cursor, event_id)

    def test_orphan_cutoff_is_inclusive_and_large_lookback_is_allowed(self):
        cutoff = self.now - timedelta(hours=24)
        runtime_id, _ = self.add_runtime("boundary", alive=False, last_activity=cutoff)
        old_id, _ = self.add_runtime("old", alive=False,
                                     last_activity=cutoff - timedelta(seconds=1))
        watchdog = self.watchdog(lookback=24)
        issues = watchdog.current_issues()
        self.assertIn(f"orphan:{runtime_id}", issues)
        self.assertNotIn(f"orphan:{old_id}", issues)
        self.assertEqual(validate_lookback_hours(0), 0)
        self.assertEqual(validate_lookback_hours(1000), 1000)
        self.assertEqual(validate_lookback_hours(1e300), 1e300)
        self.assertEqual(validate_lookback_hours(0.001), 0.001)
        for invalid in (-1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                validate_lookback_hours(invalid)

        huge_watchdog = self.watchdog(lookback=1e300)
        self.assertIn(f"orphan:{runtime_id}", huge_watchdog.current_issues())

    def test_default_zero_lookback_skips_preexisting_orphan(self):
        runtime_id, _ = self.add_runtime("old-orphan", alive=False)
        watchdog = self.watchdog()
        self.assertNotIn(f"orphan:{runtime_id}", watchdog.current_issues())

    def test_repeated_polled_action_snapshot_does_not_advance_progress(self):
        runtime_id, turn_id = self.add_runtime("live")
        first_seen = self.now - timedelta(minutes=8)
        self.add_event(runtime_id, turn_id, "current_actions_response_received",
                       payload={"status": "requires_action", "required_action_count": 1},
                       call_id="action-call", when=first_seen)
        watchdog = self.watchdog()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], first_seen.isoformat())

        self.add_event(runtime_id, turn_id, "current_actions_response_received",
                       payload={"status": "requires_action", "required_action_count": 1},
                       call_id="action-call", when=self.now - timedelta(seconds=30))
        watchdog.poll()
        self.assertEqual(watchdog.turns[turn_id]["last_progress_at"], first_seen.isoformat())

    def test_cleanly_finished_runtime_is_not_an_orphan(self):
        runtime_id, _ = self.add_runtime("finished", alive=False)
        self.writer.finish_runtime(runtime_id, exit_status="0")
        watchdog = self.watchdog()
        self.assertFalse(any(issue["kind"] == "orphan"
                             for issue in watchdog.current_issues().values()))

    def test_runtime_becoming_orphan_is_detected_without_history_rescan(self):
        runtime_id, turn_id = self.add_runtime("live", alive=True)
        watchdog = self.watchdog()
        self.alive[runtime_id] = False
        self.add_event(runtime_id, turn_id, "ai_heartbeat",
                       payload={"message": "working"}, when=self.now - timedelta(seconds=1))
        events = watchdog.poll()
        self.assertEqual(len(events), 1)
        issue = watchdog.current_issues()[f"orphan:{runtime_id}"]
        self.assertEqual(issue["turn_id"], turn_id)
        self.assertEqual(issue["last_activity_at"], self.now - timedelta(seconds=1))

    def test_orphan_summary_contains_short_preview_without_full_prompt(self):
        prompt = "secret " + "very long task " * 20
        runtime_id, turn_id = self.add_runtime("dead", alive=False, prompt=prompt)
        watchdog = self.watchdog(lookback=24)
        issue = watchdog.current_issues()[f"orphan:{runtime_id}"]
        self.assertEqual(issue["turn_id"], turn_id)
        message = issue["message"]
        self.assertIn("Open turn:", message)
        self.assertIn("Prompt:", message)
        self.assertNotIn(prompt, message)
        preview = message.split("Prompt: ", 1)[1]
        self.assertLessEqual(len(preview), 61)

    def test_pid_reuse_is_not_treated_as_same_runtime(self):
        started = self.now - timedelta(minutes=1)
        runtime = {"environment": "wsl", "process_id": 123, "started_at": started.isoformat()}
        with patch("tools.peforth_watchdog._current_environment", return_value="wsl"), \
                patch("tools.peforth_watchdog._process_creation_time", return_value=started.timestamp() - 60):
            self.assertTrue(process_matches_runtime(runtime))
        with patch("tools.peforth_watchdog._current_environment", return_value="wsl"), \
                patch("tools.peforth_watchdog._process_creation_time", return_value=started.timestamp() - 1):
            self.assertTrue(process_matches_runtime(runtime))
        with patch("tools.peforth_watchdog._current_environment", return_value="wsl"):
            with patch("tools.peforth_watchdog._process_creation_time", return_value=started.timestamp() + 60):
                self.assertFalse(process_matches_runtime(runtime))

    def test_reminder_manager_waits_for_dismissal_and_repeats_five_minutes_later(self):
        clock = [0.0]
        children = []
        def start(issue):
            child = FakeChild()
            children.append((issue["key"], child))
            return child
        manager = ReminderManager(start, now=lambda: clock[0], log=lambda _: None)
        issue = {"key": "no-progress:t", "title": "title", "message": "message"}
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 1)
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 1)
        children[0][1].returncode = 0
        clock[0] = 10
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 1)
        clock[0] = 10 + REMINDER_SECONDS - 1
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 1)
        clock[0] += 1
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 2)

    def test_orphan_alert_is_not_repeated_after_dismissal(self):
        clock = [0.0]
        children = []
        manager = ReminderManager(
            lambda issue: children.append(FakeChild()) or children[-1],
            now=lambda: clock[0], log=lambda _: None,
        )
        issue = {"key": "orphan:r", "kind": "orphan", "title": "title", "message": "message"}
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 1)

        children[0].returncode = 0
        clock[0] = REMINDER_SECONDS * 2
        manager.update({issue["key"]: issue})
        manager.update({issue["key"]: issue})
        self.assertEqual(len(children), 1)
        self.assertIn(issue["key"], manager.dismissed_orphans)

    def test_recovery_stops_future_reminders_without_closing_open_child(self):
        clock = [0.0]
        children = []
        manager = ReminderManager(lambda issue: children.append(FakeChild()) or children[-1],
                                  now=lambda: clock[0], log=lambda _: None)
        issue = {"key": "orphan:r", "title": "title", "message": "message"}
        manager.update({issue["key"]: issue})
        child = children[0]
        manager.update({})
        self.assertIsNone(child.returncode)
        child.returncode = 0
        clock[0] = REMINDER_SECONDS * 2
        manager.update({})
        self.assertEqual(len(children), 1)
        self.assertNotIn(issue["key"], manager.states)

    def test_multiple_alerts_are_queued_without_overlapping_windows(self):
        clock = [0.0]
        children = []
        shown = []
        def start(issue):
            child = FakeChild()
            children.append(child)
            shown.append(issue["key"])
            return child
        manager = ReminderManager(start, now=lambda: clock[0], log=lambda _: None)
        first = {"key": "orphan:a", "title": "a", "message": "a"}
        second = {"key": "orphan:b", "title": "b", "message": "b"}
        manager.update({first["key"]: first, second["key"]: second})
        manager.update({first["key"]: first, second["key"]: second})
        self.assertEqual(len(children), 1)
        children[0].returncode = 0
        clock[0] += 1
        manager.update({first["key"]: first, second["key"]: second})
        self.assertEqual(len(children), 2)
        self.assertNotEqual(shown[0], shown[1])

    def test_notifier_failure_is_logged_and_does_not_raise(self):
        clock = [0.0]
        messages = []
        issue = {"key": "orphan:r", "title": "title", "message": "message"}
        manager = ReminderManager(
            lambda _: (_ for _ in ()).throw(OSError("no Windows desktop")),
            now=lambda: clock[0], log=messages.append,
        )
        manager.update({issue["key"]: issue})
        self.assertTrue(any("notification failed" in message for message in messages))
        clock[0] = REMINDER_SECONDS
        manager.update({issue["key"]: issue})
        self.assertEqual(sum("notification failed" in message for message in messages), 2)

    def test_readonly_database_and_fixed_no_progress_threshold(self):
        runtime_id, _ = self.add_runtime("live")
        connection = connect_readonly(self.path)
        try:
            self.assertEqual(connection.execute("PRAGMA query_only").fetchone()[0], 1)
            with self.assertRaises(Exception):
                connection.execute("UPDATE runtimes SET exit_status = 'x'")
        finally:
            connection.close()
        self.assertEqual(NO_PROGRESS_SECONDS, 300)


if __name__ == "__main__":
    unittest.main()
