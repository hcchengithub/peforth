import subprocess
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from typing import cast

from peforth import ai_bridge, repl


class ReplStartupTests(unittest.TestCase):
    def test_launch_context_records_mode_and_caps_utf8_command_line(self):
        context = repl._make_launch_context(
            ["f", "-c", "繁體中文" * 500], one_shot=True, repl_mode="chat"
        )

        self.assertTrue(context["initial_one_shot"])
        self.assertEqual(context["initial_repl_mode"], "chat")
        self.assertTrue(context["command_line_truncated"])
        self.assertLessEqual(len(context["command_line"].encode("utf-8")), 1024)
        self.assertTrue(context["command_line"].endswith("…"))

    def test_runtime_mode_helpers_log_only_actual_transitions(self):
        class RecordingLogger:
            def __init__(self):
                self.events = []

            def append_event(self, runtime_id, turn_id, event_type, **kwargs):
                self.events.append((runtime_id, turn_id, event_type, kwargs["payload"]))

        logger = RecordingLogger()
        vm = SimpleNamespace(host={
            "diagnostic_log": logger,
            "diagnostic_runtime_id": "runtime-1",
            "one_shot": True,
            "repl_mode": "forth",
        })

        ai_bridge.set_one_shot(vm, False, reason="enter_repl")
        ai_bridge.set_one_shot(vm, False, reason="enter_repl")
        ai_bridge.set_repl_mode(vm, "chat", reason="forth_word")
        ai_bridge.set_repl_mode(vm, "chat", reason="forth_word")

        self.assertEqual([event[2] for event in logger.events], [
            "one_shot_changed", "repl_input_mode_changed",
        ])
        self.assertEqual(logger.events[0][3], {
            "previous": True, "current": False, "reason": "enter_repl",
        })
        self.assertEqual(logger.events[1][3], {
            "previous": "forth", "current": "chat", "reason": "forth_word",
        })

    def test_create_vm_persists_launch_context_and_logs_repl_mode_changes(self):
        class RecordingLogger:
            instances = []

            def __init__(self, *_args, **_kwargs):
                self.events = []
                self.metadata = None
                self.instances.append(self)

            def start_runtime(self, **kwargs):
                self.metadata = kwargs["metadata"]
                return "runtime-1"

            def append_event(self, _runtime_id, _turn_id, event_type, **kwargs):
                self.events.append((event_type, kwargs.get("payload")))

            def finish_runtime(self, *_args, **_kwargs):
                pass

            def close(self):
                pass

        context = repl._make_launch_context(
            ["f", "-i", "-e", "chat"], one_shot=True, repl_mode="forth"
        )
        with patch.dict("os.environ", {"PEFORTH_AI_LOG_MODE": "normal"}), \
                patch.object(repl, "DiagnosticLog", RecordingLogger):
            vm = repl.create_vm(launch_context=context)
            vm.dictate("chat")
            vm.dictate("forth")

        logger = RecordingLogger.instances[-1]
        self.assertEqual(logger.metadata["initial_one_shot"], True)
        self.assertEqual(logger.metadata["initial_repl_mode"], "forth")
        self.assertTrue(vm.host["one_shot"])  # Entry into REPL is a caller transition.
        self.assertEqual([kind for kind, _ in logger.events], [
            "one_shot_state", "repl_input_mode_state",
            "repl_input_mode_changed", "repl_input_mode_changed",
        ])

    def test_tick_heartbeat_forth_word_only_logs_and_consumes_message(self):
        class RecordingLogger:
            def __init__(self):
                self.event: dict[str, object] = {}

            def append_event(self, runtime_id, turn_id, event_type, **kwargs):
                self.event = {
                    "runtime_id": runtime_id, "turn_id": turn_id,
                    "event_type": event_type, **kwargs,
                }

        with patch.dict("os.environ", {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()
        logger = RecordingLogger()
        vm.host["_ai_heartbeat_context"] = {
            "logger": logger,
            "runtime_id": "runtime-1",
            "turn_id": "local-turn-1",
            "session_id": "session-1",
            "remote_turn_id": "server-turn-1",
            "call_id": "call-1",
        }
        message = ': do-not-execute 999 ;'
        original_stack = list(vm.stack)
        vm.push(message)
        task = vm.dictate("tickHeartbeat")

        self.assertEqual(task.status, "done")
        self.assertEqual(vm.stack, original_stack)
        self.assertNotIn("do-not-execute", vm.words)
        self.assertEqual((logger.event["runtime_id"], logger.event["turn_id"], logger.event["event_type"]), (
            "runtime-1", "local-turn-1", "ai_heartbeat",
        ))
        self.assertEqual(logger.event["remote_turn_id"], "server-turn-1")
        self.assertEqual(logger.event["call_id"], "call-1")
        self.assertEqual(logger.event["payload"], {"message": message})

    def test_execute_then_interactive_records_one_shot_transition(self):
        class RecordingLogger:
            def __init__(self):
                self.events = []

            def append_event(self, _runtime_id, _turn_id, event_type, **kwargs):
                self.events.append((event_type, kwargs["payload"]))

        logger = RecordingLogger()
        class FakeVM:
            def __init__(self):
                self.host = {
                    "diagnostic_log": logger,
                    "diagnostic_runtime_id": "runtime-1",
                    "repl_mode": "forth",
                    "one_shot": True,
                }

            def dictate(self, _source):
                return None

        vm = FakeVM()
        with patch.object(repl, "create_vm", return_value=vm) as create_vm, \
                patch.object(repl, "repl"):
            self.assertEqual(repl.main(["-i", "-e", "1 2 +"]), 0)

        launch = create_vm.call_args.kwargs["launch_context"]
        self.assertTrue(launch["initial_one_shot"])
        self.assertEqual(launch["initial_repl_mode"], "forth")
        self.assertFalse(vm.host["one_shot"])
        self.assertIn(("one_shot_changed", {
            "previous": True, "current": False, "reason": "enter_repl",
        }), logger.events)

    def test_interactive_chat_one_shot_changes_only_when_prompting_after_task(self):
        class RecordingLogger:
            def __init__(self):
                self.events = []

            def append_event(self, _runtime_id, _turn_id, event_type, **kwargs):
                self.events.append((event_type, kwargs["payload"]))

        class PromptSession:
            def __init__(self, **_kwargs):
                pass

            def prompt(self, _prompt):
                raise EOFError

        logger = RecordingLogger()
        vm = SimpleNamespace(host={
            "diagnostic_log": logger,
            "diagnostic_runtime_id": "runtime-1",
            "one_shot": True,
            "repl_mode": "chat",
        }, compiling=False)
        with patch.object(repl, "_load_prompt_toolkit"), \
                patch.object(repl, "PromptSession", PromptSession), \
                patch.object(repl, "CompleteStyle", SimpleNamespace(MULTI_COLUMN="multi")), \
                patch.object(repl, "ForthWordCompleter", return_value=None), \
                patch.object(repl, "_make_repl_key_bindings", return_value=None), \
                patch.object(repl, "_farewell"):
            repl.repl(cast(repl.VM, vm), initial_task=SimpleNamespace(status="done"), show_greeting=False)

        self.assertFalse(vm.host["one_shot"])
        self.assertIn(("one_shot_changed", {
            "previous": True, "current": False, "reason": "enter_repl",
        }), logger.events)

    def test_noninteractive_import_defers_prompt_toolkit_ui(self):
        probe = (
            "import sys; import peforth.repl as repl; "
            "print(repl.PromptSession is None, "
            "any(name == 'prompt_toolkit' or name.startswith('prompt_toolkit.') "
            "for name in sys.modules))"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "True False")


if __name__ == "__main__":
    unittest.main()
