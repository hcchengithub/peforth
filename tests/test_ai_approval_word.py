import contextlib
import io
import unittest
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
        self.assertIn("2. Trust throughout this AI response (this task)", display.getvalue())
        self.assertIn("\x1b[0m", display.getvalue())
        self.assertTrue(prompts[0].startswith("\x1b[96m"))
        self.assertTrue(prompts[0].endswith("\x1b[0m"))


if __name__ == "__main__":
    unittest.main()
