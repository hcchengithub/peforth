#!/usr/bin/env python3
"""peforth Comprehensive Architectural Contract & Self-Test Suite.

Run locally:
    python test_all.py
    or: pytest test_all.py

Zero external dependencies required (uses standard library unittest).
Protects against regressions, accidental architectural deviations, and safe-property drift.
"""

import ast
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from projectk import VM, KernelError, Word


class TestKernelPurity(unittest.TestCase):
    """Guarantees that projectk.py remains a pure, minimal, dependency-free micro-kernel."""

    def test_no_third_party_imports_in_kernel(self):
        kernel_path = HERE / "projectk.py"
        source = kernel_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        allowed_modules = {
            "dataclasses", "inspect", "io", "re", "tokenize", "sys", "os"
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_pkg = alias.name.split(".")[0]
                    self.assertIn(
                        top_pkg,
                        allowed_modules,
                        f"projectk.py must not import external or non-standard package: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_pkg = node.module.split(".")[0]
                    self.assertIn(
                        top_pkg,
                        allowed_modules,
                        f"projectk.py must not import from external package: {node.module}"
                    )

    def test_fresh_vm_contains_only_two_seed_words(self):
        vm = VM()
        self.assertEqual(
            set(vm.words.keys()),
            {"code", "end-code"},
            "A newly constructed VM must contain ONLY the two seed words: 'code' and 'end-code'."
        )

    def test_kernel_has_no_ui_or_prompt_toolkit_baggage(self):
        kernel_text = (HERE / "projectk.py").read_text(encoding="utf-8")
        forbidden_imports = ["prompt_toolkit", "colorama", "readline", "getpass"]
        for term in forbidden_imports:
            self.assertNotIn(
                f"import {term}",
                kernel_text,
                f"Kernel projectk.py must remain UI-agnostic; forbidden import found: {term}"
            )
            self.assertNotIn(
                f"from {term}",
                kernel_text,
                f"Kernel projectk.py must remain UI-agnostic; forbidden from-import found: {term}"
            )

        tree = ast.parse(kernel_text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotEqual(
                    node.func.id,
                    "input",
                    "Kernel projectk.py must not call Python builtin input() function."
                )


class TestArchitecturalContracts(unittest.TestCase):
    """Guarantees that Forth drives Forth and Python does not overstep into command dispatch."""

    def test_main_py_is_minimal_bootstrapper(self):
        main_path = HERE / "main.py"
        lines = [l for l in main_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertLessEqual(
            len(lines),
            20,
            "main.py must remain a tiny bootstrap shim (< 20 lines)."
        )
        content = main_path.read_text(encoding="utf-8")
        self.assertNotIn("while True:", content, "main.py must not implement REPL loop in Python host.")
        self.assertNotIn("input(", content, "main.py must not implement interactive input.")
        self.assertIn("init.f", content, "main.py must dictate init.f.")

    def test_init_f_ends_with_include_peforth(self):
        init_lines = (HERE / "init.f").read_text(encoding="utf-8").strip().splitlines()
        last_non_empty = [l.strip() for l in init_lines if l.strip() and not l.strip().startswith("\\")][-1]
        self.assertEqual(
            last_non_empty,
            "include peforth.f",
            "init.f must culminate in 'include peforth.f'."
        )

    def test_peforth_f_orchestrates_extensions_and_repl(self):
        peforth_f = (HERE / "peforth.f").read_text(encoding="utf-8")
        self.assertIn("include base.f", peforth_f)
        self.assertIn("include auxiliary.f", peforth_f)
        self.assertIn("include herdr.f", peforth_f)
        self.assertIn("include ai.f", peforth_f)
        self.assertIn("include repl.f", peforth_f)
        self.assertIn("repl", peforth_f)


class TestSafePropertyAudit(unittest.TestCase):
    """Audits dictionary words to verify task-level security metadata integrity."""

    @classmethod
    def setUpClass(cls):
        # Boot VM up to base.f without starting REPL
        cls.vm = VM({"headless": True, "__file__dir__": str(HERE)})
        cls.vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

    def test_pure_words_have_safe_true(self):
        # Pure stack, arithmetic, logic, and comparison words MUST be safe
        pure_words = [
            "pick", "roll", "dup", "drop", "dropall", "swap", "over", "rot",
            "-rot", "nip", "2dup", "2drop", "depth", "slice",
            ">r", "r>", "r@", "rdrop", ">t", "t@", "t>",
            "+", "-", "*", "/", "mod", "1+", "1-", "2+", "2-",
            "abs", "negate", "max", "min",
            "=", "<>", "!=", "==", "<", ">", "<=", ">=", "0=", "0<",
            "not", "and", "or", "AND", "OR", "NOT", "XOR", "<<", ">>", "within",
            "BL", "CR", "none", '""', "inf", "-inf", "nan",
            "int", "float", "bool", "str", "list", "dict", "set", "tuple", "type",
            "{}", "[]", "count", "trim",
            ".", ".s", "cr", "space", "words", "see", 's"', '."', "char",
            "branch", "0branch", "doNext", "here", ",", "!", "@", "[']", "[compile]",
            "begin", "until", "again", "if", "ahead", "then", "else", "?dup",
            "while", "repeat", "aft", "for", "next",
            "create", "does>", "constant", "variable", "value", "to",
            "case", "of", "endof", "endcase"
        ]
        missing_safe = []
        for name in pure_words:
            word = self.vm.tick(name)
            self.assertIsNotNone(word, f"Expected word {name!r} to exist in dictionary.")
            if not word.properties.get("safe", False):
                missing_safe.append(name)

        self.assertEqual(
            missing_safe,
            [],
            f"Pure words must have safe=True! Missing safe=True on: {missing_safe}"
        )

    def test_dangerous_or_host_eval_words_are_not_safe(self):
        # Arbitrary Python evaluation or state destruction must NOT be safe=True
        unsafe_words = ["<py>", "</py>", "</pyV>", "tib.append", "forget"]
        for name in unsafe_words:
            word = self.vm.tick(name)
            if word is not None:
                self.assertFalse(
                    word.properties.get("safe", False),
                    f"Dangerous word {name!r} must NOT be marked safe=True!"
                )

    def test_tokenized_word_search_finds_python_interop_words(self):
        import ai
        res = ai.tool_search_words(self.vm, "python execute eval")
        matched_names = [w["name"] for w in res["words"]]
        self.assertIn("execute", matched_names)
        self.assertTrue(any("py" in name for name in matched_names))

    def test_chat_and_forth_mode_switching(self):
        self.vm.dictate("chat")
        self.assertEqual(self.vm.host.get("repl_mode"), "chat")
        self.vm.dictate("forth")
        self.assertEqual(self.vm.host.get("repl_mode"), "forth")

    def test_nokia_chime_words_exist_and_are_safe(self):
        for name in ("nokia", "nokia2"):
            word = self.vm.tick(name)
            self.assertIsNotNone(word, f"Word '{name}' should be in dictionary")
            self.assertTrue(word.properties.get("safe"), f"Word '{name}' should be safe")

    def test_ai_approve_and_nokia2_property_types(self):
        # Verify ai-approve is defined and marked safe
        approve_word = self.vm.tick("ai-approve")
        self.assertIsNotNone(approve_word, "ai-approve word must exist")
        self.assertTrue(approve_word.properties.get("safe"), "ai-approve must be marked safe")

        # Verify nokia2_after_seconds is parsed as an int (not str)
        ai_word = self.vm.tick("ai:")
        self.assertIsNotNone(ai_word)
        self.assertIsInstance(ai_word.properties.get("nokia2_after_seconds"), int)
        self.assertEqual(ai_word.properties.get("nokia2_after_seconds"), 30)

    def test_sanitize_messages_heals_incomplete_tool_calls(self):
        import ai
        broken_messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_123", "type": "function", "function": {"name": "peforth_run_forth", "arguments": "{}"}}
            ]},
            {"role": "user", "content": "next turn"}
        ]
        sanitized = ai._sanitize_messages(broken_messages)
        # Should contain tool response between assistant and next user turn
        roles = [m["role"] for m in sanitized]
        self.assertEqual(roles, ["user", "assistant", "tool", "user"])
        self.assertEqual(sanitized[2]["tool_call_id"], "call_123")

    def test_words_have_documentation(self):
        words_to_check = [
            "begin", "until", "again", "if", "ahead", "then", "else", "?dup",
            "while", "repeat", "aft", "for", "next",
            "constant", "variable", "value",
            "py:", "py>", "py::", "py>>", ":>",
            "?repl", "(ai-monotonic-time)"
        ]
        for name in words_to_check:
            word = self.vm.tick(name)
            self.assertIsNotNone(word, f"Word '{name}' must exist in dictionary")
            help_text = getattr(word, "help", "") or ""
            self.assertTrue(bool(help_text.strip()), f"Word '{name}' must have help documentation")

        # (setup-ai) must no longer exist
        self.assertNotIn("(setup-ai)", self.vm.words, "(setup-ai) should not exist in dictionary")

    def test_words_and_help_pattern_filtering(self):
        import io
        from contextlib import redirect_stdout

        # Test words pattern filtering
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("words py >>")
        output = buf.getvalue().strip()
        self.assertIn("py>>", output)
        self.assertNotIn("dup", output)
        self.assertNotIn("swap", output)

        # Test help exact match
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("help dup")
        output = buf.getvalue()
        self.assertIn("dup ( x -- x x )", output)

        # Test help substring filtering
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("help py:")
        output = buf.getvalue()
        self.assertIn("py:", output)

        # Test help non-matching
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("help non_existent_word_xyz")
        output = buf.getvalue()
        self.assertIn("No word matching 'non_existent_word_xyz'.", output)


class TestSecurityTaskApproval(unittest.TestCase):
    """Verifies that the task security guard halts on non-safe words and resumes on trust-task."""

    def setUp(self):
        self.vm = VM({"headless": True, "__file__dir__": str(HERE)})
        self.vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

    def test_safe_words_execute_without_security_pause(self):
        # A task executing safe words should complete directly without pausing for approval
        task = self.vm.dictate("10 20 +")
        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.dstack, [30])

    def test_unsafe_words_pause_untrusted_task(self):
        from projectk import Task
        # An unsafe word executed inside an untrusted AI task must pause for security review
        self.vm.define("dangerous_action", lambda v: v.push("dangerous_executed"), properties={"safe": False})
        task = Task(self.vm, self.vm.evaluate("dangerous_action"))
        self.vm.host["in_ai_task"] = task
        task.resume()
        self.assertEqual(task.status, "paused")
        self.assertNotIn("dangerous_executed", self.vm.dstack)

        # After trusting the task, resuming it executes the action
        self.vm.dictate("trust-task")
        task.resume()
        self.assertEqual(task.status, "done")
        self.assertIn("dangerous_executed", self.vm.dstack)


class TestForthSelfTestExecution(unittest.TestCase):
    """Executes selftest.f inside the VM and verifies 100% assertions pass."""

    def test_selftest_f_runs_and_passes(self):
        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

        task = vm.dictate("include selftest.f")
        self.assertEqual(task.status, "done", f"selftest.f failed with status {task.status}")


class TestCLISmoke(unittest.TestCase):
    """End-to-end smoke test launching main.py via subprocess."""

    def test_cli_pipe_execution(self):
        cmd = [sys.executable, str(HERE / "main.py")]
        input_script = '1 2 + . cr s" smoke test passed" count . cr bye\n'
        proc = subprocess.run(
            cmd,
            input=input_script,
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0, f"main.py exited with non-zero: {proc.stderr}")
        self.assertIn("peforth 2.1.0 (with AI support)", proc.stdout)
        self.assertIn("3", proc.stdout)
        self.assertIn("17", proc.stdout)  # len of "smoke test passed"


if __name__ == "__main__":
    print("=" * 60)
    print(" Running peforth Architectural & Self-Test Suite")
    print("=" * 60)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
