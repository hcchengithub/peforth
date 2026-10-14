import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from peforth import repl


class NumberedChoiceTests(unittest.TestCase):
    def test_digit_returns_without_waiting_for_enter(self):
        with create_pipe_input() as input_stream:
            input_stream.send_text("2")
            result = repl.read_numbered_choice(
                "Choose: ", input=input_stream, output=DummyOutput())
        self.assertEqual(result, "2")

    def test_enter_returns_default_choice(self):
        with create_pipe_input() as input_stream:
            input_stream.send_text("\r")
            result = repl.read_numbered_choice(
                "Choose: ", default="1", input=input_stream, output=DummyOutput())
        self.assertEqual(result, "1")

    def test_ai_approve_maps_choices_without_executing_proposal(self):
        vm = repl.create_vm()
        proposal = {
            "purpose": "unit test approval only",
            "source": "This source must never be executed.",
        }
        expected = {
            "1": "allow_once",
            "2": "trust_task",
            "3": "deny",
            "4": "cancel",
        }
        for choice, decision in expected.items():
            with self.subTest(choice=choice):
                vm.push(proposal)
                with patch.object(repl, "read_numbered_choice", return_value=choice), \
                        contextlib.redirect_stdout(io.StringIO()):
                    task = vm.dictate("ai-approve")
                self.assertEqual(task.status, "done")
                self.assertEqual(vm.pop(), decision)
                self.assertNotIn("ai_trusted", vm.host)

    def test_ai_approve_word_accepts_one_key_without_enter(self):
        vm = repl.create_vm()
        vm.push({"purpose": "one-key test", "source": "not executed"})
        reader = repl.read_numbered_choice
        prompts = []
        display = io.StringIO()
        with create_pipe_input() as input_stream:
            input_stream.send_text("3")

            def read_choice(prompt, **kwargs):
                prompts.append(prompt)
                return reader(prompt, input=input_stream, output=DummyOutput(), **kwargs)

            with patch.object(repl, "read_numbered_choice", side_effect=read_choice), \
                    contextlib.redirect_stdout(display):
                task = vm.dictate("ai-approve")
        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "deny")
        self.assertNotIn("ai_trusted", vm.host)
        self.assertTrue(display.getvalue().startswith("\n\x1b[96m"))
        self.assertIn("2. Trust this AI task only", display.getvalue())
        self.assertIn("\x1b[0m", display.getvalue())
        self.assertTrue(prompts[0].startswith("\x1b[96m"))
        self.assertTrue(prompts[0].endswith("\x1b[0m"))


class ApprovalScopeTests(unittest.TestCase):
    def test_task_trust_applies_only_to_same_task_and_expires(self):
        vm = repl.create_vm()
        state = {"trusted_ai_task": None}
        task = SimpleNamespace(status="paused")
        proposal = {"purpose": "trust one AI task", "source": "1 2 +"}

        with patch.object(repl, "read_numbered_choice", return_value="2"), \
                contextlib.redirect_stdout(io.StringIO()):
            decision = repl._resolve_ai_approval_decision(vm, state, task, proposal)
        self.assertEqual(decision, "trust_task")
        self.assertIs(state["trusted_ai_task"], task)
        self.assertNotIn("ai_trusted", vm.host)

        with patch.object(repl, "read_numbered_choice", side_effect=AssertionError("same task should trust")):
            self.assertEqual(repl._resolve_ai_approval_decision(vm, state, task, proposal), "allow_once")

        next_task = SimpleNamespace(status="paused")
        with patch.object(repl, "read_numbered_choice", return_value="1"), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(repl._resolve_ai_approval_decision(vm, state, next_task, proposal), "allow_once")
        self.assertIs(state["trusted_ai_task"], task)

        task.status = "done"
        repl._expire_ai_task_trust(state)
        self.assertIsNone(state["trusted_ai_task"])

    def test_task_trust_and_approval_word_preserve_paused_task_continuation(self):
        vm = repl.create_vm()
        vm.define("pause-once", lambda current_vm: current_vm.pause())
        vm.dictate(": parent pause-once ;")
        parent_task = vm.dictate("parent")
        self.assertEqual(parent_task.status, "paused")

        state = {"trusted_ai_task": None}
        proposal = {"purpose": "same task continuation", "source": "1 2 +"}
        with patch.object(repl, "read_numbered_choice", return_value="2"):
            with contextlib.redirect_stdout(io.StringIO()):
                decision = repl._resolve_ai_approval_decision(vm, state, parent_task, proposal)
        self.assertEqual(decision, "trust_task")
        self.assertIs(state["trusted_ai_task"], parent_task)

        vm.host["ai_approval_result"] = True
        self.assertEqual(parent_task.resume().status, "done")
        repl._expire_ai_task_trust(state)
        self.assertIsNone(state["trusted_ai_task"])

    def test_runtime_trust_is_explicit_and_ai_confirm_clears_both_scopes(self):
        vm = repl.create_vm()
        task = object()
        state = {"trusted_ai_task": task}
        vm.host["ai_clear_task_trust"] = lambda: state.__setitem__("trusted_ai_task", None)

        vm.dictate("ai-trust-runtime")
        self.assertTrue(vm.host["ai_trusted"])
        self.assertIs(state["trusted_ai_task"], task)

        vm.dictate("ai-confirm")
        self.assertNotIn("ai_trusted", vm.host)
        self.assertIsNone(state["trusted_ai_task"])


if __name__ == "__main__":
    unittest.main()
