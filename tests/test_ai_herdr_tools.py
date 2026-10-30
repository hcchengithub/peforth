import json
import unittest
from unittest.mock import patch

from peforth import ai_tools


class HerdrSessionAndPaneTests(unittest.TestCase):
    def test_herdr_cli_omits_session_selector_for_forth_default(self):
        completed = {
            "exit_code": 0,
            "stdout": "{}",
            "stderr": "",
            "timed_out": False,
            "truncated": False,
        }
        with patch.object(ai_tools.shutil, "which", return_value="herdr.exe"), \
                patch.object(ai_tools, "_run_process", return_value=completed) as run:
            ai_tools._herdr_process(["pane", "list"])
        self.assertEqual(run.call_args.args[0], ["herdr.exe", "pane", "list"])

    def test_explicit_tool_session_is_selected(self):
        completed = {
            "exit_code": 0,
            "stdout": "{}",
            "stderr": "",
            "timed_out": False,
            "truncated": False,
        }
        with patch.object(ai_tools.shutil, "which", return_value="herdr.exe"), \
                patch.object(ai_tools, "_run_process", return_value=completed) as run:
            ai_tools._herdr_process(["pane", "list"], session="qa-session")
        self.assertEqual(
            run.call_args.args[0],
            ["herdr.exe", "--session", "qa-session", "pane", "list"],
        )

    def test_pane_validation_uses_workspace_from_full_pane_id(self):
        listing = {"panes": [{"pane_id": "wp:pA"}]}
        with patch.object(ai_tools, "_herdr_json", return_value=listing) as herdr_json:
            self.assertEqual(ai_tools._herdr_validate_pane("wp:pA"), "wp:pA")
        herdr_json.assert_called_once_with(
            ["pane", "list", "--workspace", "wp"], session=None
        )

    def test_read_clamps_actual_lines_but_reports_original_request(self):
        response = {
            "exit_code": 0,
            "stdout": json.dumps({"text": "visible output"}),
            "stderr": "",
            "truncated": False,
        }
        with patch.object(ai_tools, "_herdr_validate_pane", return_value="w1:p2"), \
                patch.object(ai_tools, "_herdr_process", return_value=response) as process:
            snapshot = ai_tools._herdr_screen_read("w1:p2", line_count=1001)
        self.assertEqual(
            process.call_args.args[0],
            ["pane", "read", "w1:p2", "--source", "visible", "--lines", "1000"],
        )
        self.assertIsNone(process.call_args.kwargs["session"])
        self.assertEqual(snapshot["lines_requested"], 1001)
        self.assertTrue(snapshot["truncated"])

    def test_ai_generated_forth_operation_uses_shared_approval(self):
        class FakeVM:
            def __init__(self):
                self.host = {"_ai_forth_execution": True}

            def pause(self):
                return "approval-pause"

        vm = FakeVM()
        result = {"exit_code": 0, "response": {}, "stderr": "", "truncated": False}
        with patch.object(ai_tools, "_herdr_validate_pane", return_value="w1:p2"), \
                patch.object(ai_tools, "_herdr_operation_response", return_value=result) as operate:
            task = ai_tools._herdr_forth_operation(vm, "run", "w1:p2", "git status")
            self.assertEqual(next(task), "approval-pause")
            proposal = vm.host["ai_pending_approval"]
            self.assertEqual(proposal["kind"], "computer_use")
            self.assertIn("in session default", proposal["purpose"])
            self.assertEqual(json.loads(proposal["source"])["session"], "default")
            vm.host["ai_approval_result"] = True
            with self.assertRaises(StopIteration) as completed:
                next(task)
        self.assertNotIn("session", completed.exception.value)
        operate.assert_called_once_with(["pane", "run", "w1:p2", "git status"], session=None)


if __name__ == "__main__":
    unittest.main()
