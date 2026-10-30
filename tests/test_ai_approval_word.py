import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from prompt_toolkit.data_structures import Size
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.output.vt100 import Vt100_Output

from peforth import repl


def _strip_vt100_sequences(text):
    visible = []
    index = 0
    while index < len(text):
        if text[index] == chr(27) and index + 1 < len(text) and text[index + 1] == "[":
            index += 2
            while index < len(text) and not ("@" <= text[index] <= "~"):
                index += 1
            index += 1
        else:
            visible.append(text[index])
            index += 1
    return "".join(visible)


def _create_vm_with_silent_nokia():
    vm = repl.create_vm()
    vm.define('nokia', lambda _: None)
    vm.define('nokia2', lambda _: None)
    return vm


class NumberedChoiceTests(unittest.TestCase):
    def test_digit_returns_and_echoes_choice_inline(self):
        display = io.StringIO()
        output = Vt100_Output(
            stdout=display, get_size=lambda: Size(rows=24, columns=80),
            term="xterm", enable_cpr=False)
        with create_pipe_input() as input_stream:
            input_stream.send_text("2")
            result = repl.read_numbered_choice(
                "Choose 1-4: ", input=input_stream, output=output)
        visible = _strip_vt100_sequences(display.getvalue())
        self.assertEqual(result, "2")
        self.assertIn("Choose 1-4: 2" + chr(13) + chr(10), visible)

    def test_down_arrow_moves_highlight_and_enter_confirms_current_choice(self):
        display = io.StringIO()
        output = Vt100_Output(
            stdout=display, get_size=lambda: Size(rows=24, columns=80),
            term="xterm", enable_cpr=False)
        labels = {
            "1": "Allow Once",
            "2": "Trust this AI task",
            "3": "Deny this proposal",
            "4": "Cancel this AI task",
        }
        with create_pipe_input() as input_stream:
            input_stream.send_text("\x1b[B" + chr(13))
            result = repl.read_numbered_choice(
                "Choose 1-4: ", input=input_stream, output=output, labels=labels)
        rendered = display.getvalue()
        visible = _strip_vt100_sequences(rendered)
        self.assertEqual(result, "2")
        self.assertIn("2. Trust this AI task", visible)
        self.assertIn(
            "\x1b[0;38;5;22;48;5;231;1m2. Trust this AI task",
            rendered,
        )
        self.assertNotIn("Selected:", visible)
        self.assertIn("Choose 1-4: 2" + chr(13) + chr(10), visible)

    def test_space_confirms_the_currently_highlighted_choice(self):
        with create_pipe_input() as input_stream:
            input_stream.send_text("\x1b[B ")
            result = repl.read_numbered_choice(
                "Choose 1-4: ",
                labels={"1": "Allow Once", "2": "Trust this AI task"},
                output=DummyOutput(),
                input=input_stream,
            )
        self.assertEqual(result, "2")

    def test_enter_confirms_initially_highlighted_first_choice(self):
        with create_pipe_input() as input_stream:
            input_stream.send_text(chr(13))
            result = repl.read_numbered_choice(
                "Choose 1-4: ", input=input_stream, output=DummyOutput())
        self.assertEqual(result, "1")

    def test_ai_approve_maps_choices_without_executing_proposal(self):
        vm = _create_vm_with_silent_nokia()
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

    def test_ai_approve_computer_use_uses_shared_trust_choices(self):
        vm = _create_vm_with_silent_nokia()
        proposal = {
            "kind": "computer_use",
            "purpose": "Computer Use: run on pane w2:p4 in session default",
            "source": '{"session":"default","pane_id":"w2:p4","command":"git status","operation":"run"}',
        }
        vm.push(proposal)
        display = io.StringIO()
        with patch.object(repl, "read_numbered_choice", return_value="2") as reader:
            with contextlib.redirect_stdout(display):
                task = vm.dictate("ai-approve")
        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "trust_task")
        visible = _strip_vt100_sequences(display.getvalue())
        self.assertIn("Purpose: Computer Use: run on pane w2:p4 in session default", visible)
        self.assertIn("Computer Use operation and complete parameters:", visible)
        self.assertIn('"session":"default"', visible)
        self.assertIn(chr(27) + "[1;38;2;135;215;135mPurpose: Computer Use: run on pane w2:p4 in session default" + chr(27) + "[0m", display.getvalue())
        self.assertEqual(reader.call_args.args[0], "Choose 1-4: ")
        self.assertEqual(reader.call_args.kwargs.get("choices", ("1", "2", "3", "4")), ("1", "2", "3", "4"))
        self.assertEqual(
            reader.call_args.kwargs["labels"],
            {
                "1": "Allow Once",
                "2": "Trust this AI task",
                "3": "Deny this proposal",
                "4": "Cancel this AI task",
            },
        )

    def test_ai_approve_word_accepts_one_key_without_enter(self):
        vm = _create_vm_with_silent_nokia()
        vm.push({"purpose": "one-key test", "source": "not executed"})
        reader = repl.read_numbered_choice
        prompts = []
        reader_options = []
        display = io.StringIO()
        with create_pipe_input() as input_stream:
            input_stream.send_text("3")

            def read_choice(prompt, **kwargs):
                prompts.append(prompt)
                reader_options.append(kwargs)
                return reader(prompt, input=input_stream, output=DummyOutput(), **kwargs)

            with patch.object(repl, "read_numbered_choice", side_effect=read_choice), \
                    contextlib.redirect_stdout(display):
                task = vm.dictate("ai-approve")
        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "deny")
        self.assertNotIn("ai_trusted", vm.host)
        visible = _strip_vt100_sequences(display.getvalue())
        self.assertIn('Purpose: one-key test', visible)
        self.assertNotIn('AI permission requested', visible)
        self.assertIn(chr(27) + '[1;38;2;135;215;135mPurpose: one-key test' + chr(27) + '[0m', display.getvalue())
        self.assertLess(visible.index("Purpose:"), visible.index("Forth action:"))
        self.assertNotIn("---", visible)
        self.assertNotIn("Choose 1-4:", visible)
        self.assertIn("\x1b[0m", display.getvalue())
        self.assertEqual(prompts, ["Choose 1-4: "])
        self.assertEqual(
            reader_options[0]["labels"],
            {
                "1": "Allow Once",
                "2": "Trust this AI task",
                "3": "Deny this proposal",
                "4": "Cancel this AI task",
            },
        )
        self.assertEqual(set(reader_options[0]["styles"]), {"1", "2", "3", "4"})


class ApprovalScopeTests(unittest.TestCase):
    def test_task_trust_applies_only_to_same_task_and_expires(self):
        vm = _create_vm_with_silent_nokia()
        state = {"trusted_ai_task": None}
        task = SimpleNamespace(status="paused")
        proposal = {
            "kind": "computer_use",
            "purpose": "trust one AI task pane operation",
            "source": '{"session":"default","pane_id":"w2:p4","operation":"run","command":"git status"}',
        }

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
        vm = _create_vm_with_silent_nokia()
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
        vm = _create_vm_with_silent_nokia()
        task = SimpleNamespace(status="paused")
        state = {"trusted_ai_task": task}
        vm.host["ai_clear_task_trust"] = lambda: state.__setitem__("trusted_ai_task", None)

        vm.dictate("ai-trust-runtime")
        self.assertTrue(vm.host["ai_trusted"])
        self.assertIs(state["trusted_ai_task"], task)
        proposal = {
            "kind": "computer_use",
            "purpose": "trusted pane operation",
            "source": '{"session":"default","pane_id":"w2:p4","operation":"run","command":"git status"}',
        }
        with patch.object(repl, "read_numbered_choice", side_effect=AssertionError("Runtime Trust should approve")):
            self.assertEqual(
                repl._resolve_ai_approval_decision(vm, state, task, proposal),
                "allow_once",
            )

        vm.dictate("ai-confirm")
        self.assertNotIn("ai_trusted", vm.host)
        self.assertIsNone(state["trusted_ai_task"])


if __name__ == "__main__":
    unittest.main()
