#!/usr/bin/env python3
"""peforth Comprehensive Architectural Contract & Self-Test Suite.

Run locally:
    python test_all.py
    or: pytest test_all.py

Zero external dependencies required (uses standard library unittest).
Protects against regressions, accidental architectural deviations, and safe-property drift.
"""

import ast
import contextlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

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
        self.assertIn("include ai.f", peforth_f)
        self.assertIn("include herdr.f", peforth_f)
        self.assertIn("include repl.f", peforth_f)
        self.assertIn("repl", peforth_f)
        # ai.f must be included before herdr.f because herdr.f depends on ai.f
        self.assertLess(
            peforth_f.index("include ai.f"),
            peforth_f.index("include herdr.f"),
            "ai.f must be included before herdr.f in peforth.f"
        )


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
            ".", ".s", "cr", "space", "words", "see", 's"', "s'", 's`', "s|", "s^", "s/", '."', ".'", '.`', ".|", ".^", "./", "char",
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
        for item in res["words"]:
            self.assertIn("source", item, "search results must include the word source")


    def test_alias_and_standard_aliases(self):
        # Verify 2.0.0 aliases True, False, None, infinity, -infinity exist and work
        self.vm.dictate("none None")
        self.assertIsNone(self.vm.pop())
        self.assertIsNone(self.vm.pop())

        self.vm.dictate("true True false False")
        self.assertIs(self.vm.pop(), False)
        self.assertIs(self.vm.pop(), False)
        self.assertIs(self.vm.pop(), True)
        self.assertIs(self.vm.pop(), True)

        self.vm.dictate("infinity -infinity")
        self.assertEqual(self.vm.pop(), float("-inf"))
        self.assertEqual(self.vm.pop(), float("inf"))

        # Verify alias signature ' word alias Name
        self.vm.dictate(": original 17 ; ' original alias original-alias original-alias")
        self.assertEqual(self.vm.pop(), 17)
        alias_word = self.vm.tick("original-alias")
        self.assertEqual(alias_word.category, "alias")
        self.assertEqual(getattr(alias_word, "type", "alias"), "alias")

    def test_chat_and_forth_mode_switching(self):
        self.vm.dictate("chat")
        self.assertEqual(self.vm.host.get("repl_mode"), "chat")
        self.vm.dictate("forth")
        self.assertEqual(self.vm.host.get("repl_mode"), "forth")

    def test_chat_mode_slash_leading_forth_tib(self):
        import projectk
        import unittest.mock

        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))
        vm.dictate((HERE / "repl.f").read_text(encoding="utf-8"))

        dispatched = []
        orig_dictate = vm.dictate

        def empty_gen():
            if False:
                yield

        def spy_dictate(tib):
            dispatched.append(tib)
            if tib.startswith("ai:"):
                # Avoid network requests in unit tests
                return projectk.Task(vm, empty_gen()).resume()
            return orig_dictate(tib)

        vm.dictate = spy_dictate
        try:
            inputs = [
                "chat",
                "/10 20 +",
                "hello world",
                "forth is a language",
                "bye everyone",
                "/forth",
                "bye",
            ]
            with unittest.mock.patch("sys.stdin.isatty", return_value=False), \
                 unittest.mock.patch("builtins.input", side_effect=inputs):
                orig_dictate("repl")

            # Check that / leading inputs had slash stripped and ran as Forth statements
            self.assertEqual(vm.pop(), 30)
            self.assertIn("10 20 +", dispatched)
            self.assertIn("forth", dispatched)

            # Check that non-slash inputs were dispatched to chatting (ai:)
            self.assertIn("ai: hello world", dispatched)
            self.assertIn("ai: forth is a language", dispatched)
            self.assertIn("ai: bye everyone", dispatched)
            self.assertEqual(vm.host.get("repl_mode"), "forth")
            self.assertTrue(vm.host.get("exit_requested"))
        finally:
            vm.dictate = orig_dictate

    def test_cls_clears_screen_and_scrollback(self):
        import io
        from contextlib import redirect_stdout

        word = self.vm.tick("cls")
        self.assertIsNotNone(word, "cls word must exist")
        self.assertTrue(word.properties.get("safe"), "cls must have safe=True")

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("cls")
        self.assertIn("\033[2J\033[3J\033[H", buf.getvalue())

    def test_bracket_flow_control_conditionals_and_loops(self):
        # 1. [if] [else] [then]
        self.vm.dictate("1 [if] 11 [else] 22 [then]")
        self.assertEqual(self.vm.pop(), 11)
        self.vm.dictate("0 [if] 33 [else] 44 [then]")
        self.assertEqual(self.vm.pop(), 44)
        self.vm.dictate("0 [if] 1 [if] 55 [else] 66 [then] [else] 77 [then]")
        self.assertEqual(self.vm.pop(), 77)

        # 2. [begin] [until] and [again]
        self.vm.dictate("dropall 0 [begin] 1+ dup 3 >= [until]")
        self.assertEqual(self.vm.pop(), 3)

        # 3. [for] [next]
        self.vm.dictate("dropall 0 3 [for] 1+ [next]")
        self.assertEqual(self.vm.pop(), 3)
        self.vm.dictate("dropall 0 0 [for] 1+ [next]")
        self.assertEqual(self.vm.pop(), 1)
        self.vm.dictate("dropall 0 2 [for] 2 [for] 1+ [next] [next]")
        self.assertEqual(self.vm.pop(), 4)

    def test_inherited_200_auxiliary_words(self):
        # 1. dir, keys, dict>keys
        self.vm.dictate("<py> {'a': 1, 'b': 2} </pyV> dict>keys")
        self.assertEqual(sorted(self.vm.pop()), ["a", "b"])

        self.vm.dictate("<py> {'x': 10} </pyV> keys")
        self.assertEqual(self.vm.pop(), ["x"])

        # 2. <text> and </text>
        self.vm.dictate("<text> hello from 2.0 </text>")
        self.assertEqual(self.vm.pop(), "hello from 2.0 ")

        # 3. <comment> and </comment>
        self.vm.dictate("10 <comment> ignored text </comment> 20 +")
        self.assertEqual(self.vm.pop(), 30)

        # 4. (space) and (')
        self.vm.dictate("(space)")
        self.assertEqual(self.vm.pop(), " ")

        self.vm.dictate("s' dup' (')")
        word = self.vm.pop()
        self.assertEqual(word.name, "dup")

        # 5. sleep and greeting
        self.vm.dictate("1 sleep")
        self.vm.dictate("greeting")

        # 6. aiModel and initial-ai-model
        self.vm.dictate("aiModel")
        val = self.vm.pop()
        self.assertIsInstance(val, str)
        self.vm.dictate('s" test-custom-model" to aiModel aiModel')
        self.assertEqual(self.vm.pop(), "test-custom-model")

    def test_inherited_shell_and_debug_words_are_unsafe(self):
        unsafe_inherited = ["*debug*", "bash", "(bash)", "pwsh", "(pwsh)", "sudo", "(sudo)"]
        for name in unsafe_inherited:
            word = self.vm.tick(name)
            self.assertIsNotNone(word, f"Word {name!r} must be defined in dictionary")
            self.assertFalse(word.properties.get("safe", False), f"Word {name!r} must be marked safe=False")

    def test_nokia_chime_words_exist_and_are_safe(self):
        for name in ("nokia", "nokia2", "nokia-full"):
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

    def test_word_falsy_delimiter_and_ai_colon_prompt_preservation(self):
        # 1. word with empty string delimiter consumes entire remaining TIB without stripping
        self.vm.dictate('"" word   def foo():\n        return 42   ')
        raw_result = self.vm.pop()
        self.assertEqual(raw_result, "   def foo():\n        return 42   ")

        # 2. Mock (ai) action to capture the exact prompt passed by ai:
        captured = []
        def mock_ai(v):
            stream_flag = v.pop()
            prompt = v.pop()
            captured.append((prompt, stream_flag))
        self.vm.words["(ai)"].action = mock_ai

        self.vm.dictate("ai:   code indented prompt\n  second line  ")
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][0], "   code indented prompt\n  second line  ")
        self.assertTrue(captured[0][1])

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

    def test_system_prompt_includes_environment(self):
        import ai
        prompt = ai.get_system_prompt(self.vm)
        self.assertIn("=== System Environment ===", prompt)
        self.assertIn("- OS:", prompt)
        self.assertIn("- Active Shell:", prompt)

    def test_vision_words_exist_and_are_safe(self):
        vision_words = [
            "desktop-capture",
            "desktop-capture-region",
            "ai-image-url",
            "ai-image-file",
            "ai-screen",
            "ai-screen-region",
        ]
        for name in vision_words:
            word = self.vm.tick(name)
            self.assertIsNotNone(word, f"Word '{name}' must exist in dictionary")
            self.assertTrue(word.properties.get("safe", False), f"Word '{name}' must be safe=True")
            help_text = getattr(word, "help", "") or ""
            self.assertTrue(bool(help_text.strip()), f"Word '{name}' must have help documentation")

    def test_session_words_exist_and_safe_properties(self):
        safe_session_words = [
            "(ai-sessions)",
            "(ai-sessions-list)",
            "ai-sessions",
            "ai-sync",
            "(ai-session-details)",
            "ai-session",
            "ai-use",
            "ai-new",
            "ai-status",
            "ai-export-session",
            "ai-search",
            "ai-cancel",
            "(ai-context)",
            "ai-context",
        ]
        for name in safe_session_words:
            word = self.vm.tick(name)
            self.assertIsNotNone(word, f"Word '{name}' must exist in dictionary")
            self.assertTrue(word.properties.get("safe", False), f"Word '{name}' must be safe=True")
            help_text = getattr(word, "help", "") or ""
            self.assertTrue(bool(help_text.strip()), f"Word '{name}' must have help documentation")

        cleanup_word = self.vm.tick("ai-cleanup")
        self.assertIsNotNone(cleanup_word, "Word 'ai-cleanup' must exist in dictionary")
        self.assertFalse(cleanup_word.properties.get("safe", False), "Word 'ai-cleanup' must be safe=False")
        self.assertTrue(bool(getattr(cleanup_word, "help", "").strip()), "Word 'ai-cleanup' must have help documentation")

        promote_word = self.vm.tick("ai-promote")
        self.assertIsNotNone(promote_word, "Word 'ai-promote' must exist in dictionary")
        self.assertFalse(promote_word.properties.get("safe", False), "Word 'ai-promote' must be safe=False")
        self.assertTrue(bool(getattr(promote_word, "help", "").strip()), "Word 'ai-promote' must have help documentation")


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

    def test_see_decompiles_colon_words_and_source(self):
        import io
        from contextlib import redirect_stdout

        # 1. Test see on colon word with python expression (nokia)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("see nokia")
        output = buf.getvalue()
        self.assertIn(": nokia py> [[659,120],[587,120],[370,240],[415,240]] (play-notes) ;", output)
        self.assertNotIn("<function", output, "see nokia should not show raw function object address")

        # 2. Test see on immediate colon word (bye)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("see bye")
        output = buf.getvalue()
        self.assertIn(": bye (bye) abort ; immediate", output)

        # 3. Test see on code word (play-notes)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate("see (play-notes)")
        output = buf.getvalue()
        self.assertIn("code (play-notes)", output)
        self.assertIn("end-code", output)

        # 4. Test see on string-quote word (s") and print-string-quote word (.")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate('see s"')
        self.assertIn("char '\"' string-quote s\"", buf.getvalue())

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.vm.dictate('see ."')
        self.assertIn("char '\"' print-string-quote .\"", buf.getvalue())

    def test_string_delimiters(self):
        # 1. Double quote s"
        self.vm.dictate('s" this is a book"')
        self.assertEqual(self.vm.pop(), "this is a book")

        # 2. Single quote s' (can embed double quotes)
        self.vm.dictate('s\' he said "hello"\'')
        self.assertEqual(self.vm.pop(), 'he said "hello"')

        # 3. Backtick s`
        self.vm.dictate('s` markdown code`')
        self.assertEqual(self.vm.pop(), 'markdown code')

        # 4. Pipe s|
        self.vm.dictate('s| path/to/file|')
        self.assertEqual(self.vm.pop(), 'path/to/file')

        # 5. Caret s^
        self.vm.dictate('s^ [0-9]+^')
        self.assertEqual(self.vm.pop(), '[0-9]+')

        # 6. Slash s/
        self.vm.dictate('s/ hello world from slash/')
        self.assertEqual(self.vm.pop(), 'hello world from slash')

        # Leading whitespace preservation: only the first separator space is stripped
        self.vm.dictate('s"   two leading spaces"')
        self.assertEqual(self.vm.pop(), '  two leading spaces')

        # Multi-line string
        self.vm.dictate('s" line 1\nline 2"')
        self.assertEqual(self.vm.pop(), 'line 1\nline 2')

        # Compilation mode inside colon definition
        self.vm.dictate(': greet-s s\' Welcome to "Project K"!\' ; greet-s')
        self.assertEqual(self.vm.pop(), 'Welcome to "Project K"!')

    def test_dot_string_delimiters(self):
        import io
        from contextlib import redirect_stdout

        for source, expected in [
            ('." double quote output"', "double quote output"),
            (".' single quote output'", "single quote output"),
            (".` backtick output`", "backtick output"),
            (".| pipe output|", "pipe output"),
            (".^ caret output^", "caret output"),
            ("./ slash output/", "slash output"),
        ]:
            output = io.StringIO()
            with redirect_stdout(output):
                self.vm.dictate(source)
            self.assertEqual(output.getvalue(), expected)

        # Compilation mode inside colon definitions
        self.vm.dictate(': say-d ." compiled double" ;')
        self.vm.dictate(": say-s .' compiled single' ;")
        self.vm.dictate(': say-b .` compiled backtick` ;')
        self.vm.dictate(': say-p .| compiled pipe| ;')
        self.vm.dictate(': say-c .^ compiled caret^ ;')
        self.vm.dictate(': say-sl ./ compiled slash/ ;')

        for word_call, expected in [
            ("say-d", "compiled double"),
            ("say-s", "compiled single"),
            ("say-b", "compiled backtick"),
            ("say-p", "compiled pipe"),
            ("say-c", "compiled caret"),
            ("say-sl", "compiled slash"),
        ]:
            output = io.StringIO()
            with redirect_stdout(output):
                self.vm.dictate(word_call)
            self.assertEqual(output.getvalue(), expected)

    def test_forth_word_completer_matches_dictionary_in_all_modes(self):
        try:
            from prompt_toolkit.document import Document
        except ImportError:
            self.skipTest("prompt_toolkit is not installed in this environment")

        completer_cls = self.vm.host.get("ForthWordCompleter")
        if completer_cls is None:
            self.skipTest("prompt_toolkit is not installed in this environment")

        completer = completer_cls(self.vm)


        # 1. Test in Forth mode
        self.vm.host["repl_mode"] = "forth"
        doc = Document("nok", 3)
        completions = [c.text for c in completer.get_completions(doc, None)]
        self.assertIn("nokia", completions)
        self.assertIn("nokia2", completions)
        self.assertIn("nokia-full", completions)

        # 2. Test in Chat mode (Unified completion applies to all modes)
        self.vm.host["repl_mode"] = "chat"
        doc_chat = Document("ai-app", 6)
        completions_chat = [c.text for c in completer.get_completions(doc_chat, None)]
        self.assertIn("ai-approve", completions_chat)


        # 3. Test run-monitor completion
        doc_mon = Document("run-mon", 7)
        completions_mon = [c.text for c in completer.get_completions(doc_mon, None)]
        self.assertIn("run-monitor", completions_mon)

        # 4. Trailing space should not trigger completion
        doc_space = Document("nokia ", 6)
        completions_space = list(completer.get_completions(doc_space, None))
        self.assertEqual(len(completions_space), 0)

        # 5. Test completion with leading slash (e.g., in Chat mode /<word>)
        doc_slash = Document("/ai-app", 7)
        slash_completions = list(completer.get_completions(doc_slash, None))
        slash_texts = [c.text for c in slash_completions]
        self.assertIn("ai-approve", slash_texts)
        for c in slash_completions:
            if c.text == "ai-approve":
                self.assertEqual(c.start_position, -6)

    def test_skills_loading_and_list_skills_word(self):
        import ai
        names, text = ai.load_all_skills(HERE / "skills")
        self.assertIn("herdr", names)
        self.assertIn("peforth-forth", names)
        self.assertIn("windows-screen-capture", names)
        self.assertIn("windows-msgbox", names)
        self.assertIn("ai-diagnostics-log-inspector", names)
        self.assertIn("line-notify", names)

        # Prompt includes skills without duplicating references/forth-reference.md
        prompt = ai.get_system_prompt(self.vm)
        self.assertIn("## Skill: herdr", prompt)
        self.assertIn("## Skill: peforth-forth", prompt)
        self.assertNotIn("=== Forth Reference ===", prompt)
        self.assertLessEqual(len(prompt.encode("utf-8")), 100_000)

        # list-skills word in Forth
        task = self.vm.dictate("list-skills")
        self.assertEqual(task.status, "done")
        skills_str = self.vm.pop()
        self.assertIn("herdr", skills_str)
        self.assertIn("peforth-forth", skills_str)

    def test_herdr_words_and_security_annotations(self):
        safe_words = [
            "herdr-current-pane", "herdr-screen-read", "herdr-screen-tail",
            "herdr-show-pane-id", "herdr-clear-pane-id", "stringify"
        ]
        unsafe_words = [
            "herdr-screen-send-text", "herdr-screen-send-keys", "herdr-screen-run"
        ]

        for name in safe_words:
            w = self.vm.tick(name)
            self.assertIsNotNone(w, f"Word '{name}' must exist in dictionary")
            self.assertTrue(w.properties.get("safe"), f"Word '{name}' must have safe=True")

        for name in unsafe_words:
            w = self.vm.tick(name)
            self.assertIsNotNone(w, f"Word '{name}' must exist in dictionary")
            self.assertFalse(w.properties.get("safe", False), f"Word '{name}' must NOT have safe=True")

    def test_shell_and_system_info_words_and_security_annotations(self):
        # Read-only system reflection words are safe=True
        for name in ("system_info", "(ai-tool-error)"):
            w = self.vm.tick(name)
            self.assertIsNotNone(w, f"Word '{name}' must exist in dictionary")
            self.assertTrue(w.properties.get("safe"), f"Word '{name}' must have safe=True")

        # System/network executing words are unsafe (safe=False)
        for name in ("run_pwsh", "run_bash", "run_curl", "run_http"):
            w = self.vm.tick(name)
            self.assertIsNotNone(w, f"Word '{name}' must exist in dictionary")
            self.assertFalse(w.properties.get("safe", False), f"Word '{name}' must NOT have safe=True")

        # Test system_info execution and structure
        task = self.vm.dictate("system_info")
        self.assertEqual(task.status, "done")
        info = self.vm.pop()
        self.assertIsInstance(info, dict)
        self.assertIn("os", info)
        self.assertIn("environment", info)
        self.assertIn("active_shell", info)
        self.assertIn("default_shell", info)
        self.assertIn("shells", info)
        self.assertIn("pwsh", info["shells"])
        self.assertIn("curl", info["shells"])
        self.assertIn("bash", info["shells"])
        self.assertIn("wsl", info)
        self.assertIn("active", info["wsl"])




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

    def test_interactive_ai_approve_for_unsafe_words(self):
        from projectk import Task
        # In non-headless mode, unsafe words trigger ai-approve
        self.vm.host["headless"] = False
        self.vm.define("risky_cmd", lambda v: v.push("risky_done"), properties={"safe": False})

        # Mock ai-approve returning 'allow_once'
        approval_calls = []
        def mock_approve(v):
            proposal = v.pop()
            approval_calls.append(proposal)
            v.push("allow_once")
        self.vm.define("ai-approve", mock_approve, properties={"safe": True})

        task = Task(self.vm, self.vm.evaluate("risky_cmd"))
        self.vm.host["in_ai_task"] = task
        task.resume()

        self.assertEqual(task.status, "done")
        self.assertIn("risky_done", self.vm.dstack)
        self.assertEqual(len(approval_calls), 1)
        self.assertIn("risky_cmd", approval_calls[0]["purpose"])

        # Safe words must NEVER trigger ai-approve
        approval_calls.clear()
        task2 = Task(self.vm, self.vm.evaluate("10 20 +"))
        self.vm.host["in_ai_task"] = task2
        task2.resume()
        self.assertEqual(task2.status, "done")
        self.assertEqual(len(approval_calls), 0)

    def test_interactive_ai_approve_reentrancy_protection(self):
        from projectk import Task
        self.vm.host["headless"] = False
        self.vm.define("risky_outer", lambda v: v.push("outer_done"), properties={"safe": False})
        self.vm.define("risky_inner", lambda v: v.push("inner_done"), properties={"safe": False})

        # ai-approve calls another unsafe word inside itself
        approval_calls = []
        def approve_with_side_effect(v):
            proposal = v.pop()
            approval_calls.append(proposal)
            # Invoke risky_inner directly during approval
            yield from v.call(v.tick("risky_inner"))
            v.push("allow_once")

        self.vm.define("ai-approve", approve_with_side_effect, properties={"safe": True})
        task = Task(self.vm, self.vm.evaluate("risky_outer"))
        self.vm.host["in_ai_task"] = task
        task.resume()

        self.assertEqual(task.status, "done")
        self.assertIn("inner_done", self.vm.dstack)
        self.assertIn("outer_done", self.vm.dstack)
        # Approval must be requested exactly ONCE for outer; inner must NOT trigger recursion
        self.assertEqual(len(approval_calls), 1)
        self.assertIn("risky_outer", approval_calls[0]["purpose"])

    def test_parent_frame_safety_inheritance(self):
        from projectk import Task
        # When a parent word is safe, internal Python expressions (like py>)
        # inherit safety within that frame and do not pause an untrusted AI task
        self.vm.dictate(": safe_wrapper py> 21*2 ; ' safe_wrapper :: safe=True")
        task = Task(self.vm, self.vm.evaluate("safe_wrapper"))
        self.vm.host["in_ai_task"] = task
        task.resume()

        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), 42)

        # nokia is a safe colon word using py> internally; it must complete without pausing
        task_nokia = Task(self.vm, self.vm.evaluate("nokia"))
        self.vm.host["in_ai_task"] = task_nokia
        task_nokia.resume()
        self.assertEqual(task_nokia.status, "done")

    def test_unsafe_compiled_closure_shows_source_code(self):
        from projectk import Task
        self.vm.host["headless"] = False
        # When an unsafe compiled closure triggers approval, proposal['source'] must be the Python source
        self.vm.dictate(": unsafe_wrapper py> 99*2 ;")
        approval_calls = []
        def mock_approve(v):
            proposal = v.pop()
            approval_calls.append(proposal)
            v.push("allow_once")
        self.vm.define("ai-approve", mock_approve, properties={"safe": True})

        task = Task(self.vm, self.vm.evaluate("unsafe_wrapper"))
        self.vm.host["in_ai_task"] = task
        task.resume()

        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), 198)
        self.assertEqual(len(approval_calls), 1)
        # Verify it displays the actual source code rather than '<function ...>'
        self.assertEqual(approval_calls[0]["source"], "unsafe_wrapper")

    def test_ai_task_base_frame_depth_prevents_outer_frame_leak(self):
        from projectk import Task, Frame
        # Define an unsafe action
        self.vm.define("dangerous_action", lambda v: v.push("dangerous_executed"), properties={"safe": False})
        # Define an outer harness word with safe=True (simulating ai: or (ai))
        self.vm.dictate(": outer_ai_word ; ' outer_ai_word :: safe=True")
        outer_word = self.vm.words["outer_ai_word"]

        task = Task(self.vm, self.vm.evaluate("dangerous_action"))
        # Push outer safe frame
        task.frames.append(Frame(outer_word, iter([])))
        self.vm.host["in_ai_task"] = task
        # Set base frame depth to 1 (outer frame belongs to orchestrator)
        self.vm.host["ai_task_base_frame_depth"] = 1
        task.resume()

        # Must pause for review and NOT inherit safe=True from outer_ai_word
        self.assertEqual(task.status, "paused")

    def test_safe_parent_cannot_inherit_explicit_unsafe_word(self):
        from projectk import Task
        # Define an unsafe action with safe=False
        self.vm.define("unsafe_leaf", lambda v: v.push("ran_unsafe"), properties={"safe": False})
        # Define a parent word with safe=True calling the unsafe leaf
        self.vm.dictate(": safe_parent unsafe_leaf ; ' safe_parent :: safe=True")
        task = Task(self.vm, self.vm.evaluate("safe_parent"))
        self.vm.host["in_ai_task"] = task
        self.vm.host["ai_task_base_frame_depth"] = 0
        task.resume()

        # Explicitly unsafe words (safe=False) must NEVER inherit safety even if called from safe_parent
        self.assertEqual(task.status, "paused")

    def test_does_words_like_s_quote_do_not_trigger_security_pause(self):
        from projectk import Task
        # s" is defined via create ... does> and executes an internal tuple of steps (@, (s))
        # It must complete cleanly in an AI task without triggering a false security pause on the tuple
        task = Task(self.vm, self.vm.evaluate('s" hello from test"'))
        self.vm.host["in_ai_task"] = task
        self.vm.host["ai_task_base_frame_depth"] = 0
        task.resume()

        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), "hello from test")


class TestDiagnosticLoggingAndMonitoring(unittest.TestCase):
    """Verifies SQLite diagnostic logging, monitoring renderer, and watchdog supervision."""

    def test_diagnostic_log_schema_and_lifecycle(self):
        from diagnostic_log import DiagnosticLog
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_diag.sqlite3"
            env = "windows" if os.name == "nt" else "wsl"
            logger = DiagnosticLog(db_path, environment=env)

            runtime_id = logger.start_runtime(runtime_version="test-2.1.0")
            self.assertTrue(runtime_id)

            prompt_cid = logger.store_content("prompt", "Calculate 2+2 in Forth")
            instr_cid = logger.store_content("agent_instructions", "You are an assistant.")
            self.assertIsInstance(prompt_cid, int)
            self.assertIsInstance(instr_cid, int)

            turn_id = logger.start_turn(runtime_id, prompt_content_id=prompt_cid, instructions_content_id=instr_cid)
            self.assertTrue(turn_id)

            ev1 = logger.append_event(runtime_id, turn_id, "ai_turn_started")
            ev2 = logger.append_event(runtime_id, turn_id, "tool_call_started", operation="peforth_run_forth", call_id="c1")
            ev3 = logger.append_event(runtime_id, turn_id, "tool_result_submitted", operation="peforth_run_forth", call_id="c1")
            self.assertGreater(ev3, ev2)

            logger.finish_turn(turn_id, output_text="The answer is 4.", output_status="complete", status="completed")
            logger.finish_runtime(runtime_id)
            logger.close()

            # Query database directly
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            runtime_row = conn.execute("SELECT * FROM runtimes WHERE runtime_id = ?", (runtime_id,)).fetchone()
            self.assertIsNotNone(runtime_row)
            self.assertIsNotNone(runtime_row["finished_at"])

            turn_row = conn.execute("SELECT * FROM turns WHERE turn_id = ?", (turn_id,)).fetchone()
            self.assertIsNotNone(turn_row)
            self.assertEqual(turn_row["status"], "completed")

            events = conn.execute("SELECT event_type FROM timeline WHERE runtime_id = ? ORDER BY event_id", (runtime_id,)).fetchall()
            event_types = [e["event_type"] for e in events]
            self.assertIn("runtime_started", event_types)
            self.assertIn("ai_turn_started", event_types)
            self.assertIn("tool_call_started", event_types)
            self.assertIn("tool_result_submitted", event_types)
            self.assertIn("runtime_finished", event_types)
            conn.close()
            logger.close()


    def test_ai_py_init_diagnostics_and_heartbeat(self):
        import ai
        vm = VM()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "diag.sqlite3"
            logger = ai.init_diagnostics(vm, database_path=db_path, force=True)
            self.assertIsNotNone(logger)
            self.assertIn("diagnostic_log", vm.host)
            self.assertIn("diagnostic_runtime_id", vm.host)

            runtime_id = vm.host["diagnostic_runtime_id"]
            turn_id = logger.start_turn(runtime_id)
            vm.host["ai_current_turn_id"] = turn_id
            logged = ai.log_heartbeat(vm, "compiling word")
            self.assertTrue(logged)

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM timeline WHERE event_type = 'ai_heartbeat'").fetchall()
            self.assertEqual(len(rows), 1)
            payload = json.loads(rows[0]["payload_json"])
            self.assertEqual(payload.get("message"), "compiling word")
            conn.close()
            logger.close()


    def test_peforth_logging_monitor_render_events(self):
        from tools.peforth_logging_monitor import render_events

        test_events = [
            {"runtime_id": "12345678-abcd", "event_type": "runtime_started", "recorded_at": "2026-11-05T06:00:00Z"},
            {"runtime_id": "12345678-abcd", "event_type": "http_request_started", "recorded_at": "2026-11-05T06:00:01Z"},
            {"runtime_id": "12345678-abcd", "event_type": "sse_event_received", "recorded_at": "2026-11-05T06:00:02Z"},
            {"runtime_id": "12345678-abcd", "event_type": "sse_event_received", "recorded_at": "2026-11-05T06:00:03Z"},
            {"runtime_id": "12345678-abcd", "event_type": "tool_call_started", "operation": "peforth_run_forth", "recorded_at": "2026-11-05T06:00:04Z"},
        ]
        rendered = render_events(test_events)
        self.assertEqual(len(rendered), 4)  # 2 sse_event_received are collapsed into 1 with ×2
        self.assertIn("🚀", rendered[0])
        self.assertIn("🌐", rendered[1])
        self.assertIn("📨", rendered[2])
        self.assertIn("×2", rendered[2])
        self.assertIn("🛠️", rendered[3])
        self.assertIn("peforth_run_forth", rendered[3])

    def test_ai_diagnostics_query_tool(self):
        from diagnostic_log import DiagnosticLog
        import tools.ai_diagnostics as diag_tool

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "diag.sqlite3"
            env = "windows" if os.name == "nt" else "wsl"
            logger = DiagnosticLog(db_path, environment=env)
            rid = logger.start_runtime(runtime_version="2.1.0")
            logger.close()

            conn = diag_tool.connect_readonly(db_path)
            runtimes = diag_tool.list_runtimes(conn)
            self.assertEqual(len(runtimes), 1)
            self.assertEqual(runtimes[0]["runtime_id"], rid)
            conn.close()


    def test_peforth_watchdog_issue_tracking(self):
        from diagnostic_log import DiagnosticLog
        from tools.peforth_watchdog import Watchdog

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "watchdog.sqlite3"
            env = "windows" if os.name == "nt" else "wsl"
            logger = DiagnosticLog(db_path, environment=env)
            rid = logger.start_runtime(runtime_version="2.1.0")

            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            watchdog = Watchdog(conn, orphan_lookback_hours=0)
            high_water = watchdog.initialize()
            self.assertGreaterEqual(high_water, 0)

            # Polling new events with no active turn should report no issues
            new_events = watchdog.poll()
            issues = watchdog.current_issues()
            self.assertEqual(len(issues), 0)

            conn.close()
            logger.finish_runtime(rid)
            logger.close()



class TestForthSelfTestExecution(unittest.TestCase):
    """Executes selftest.f inside the VM and verifies 100% assertions pass."""

    def test_selftest_f_runs_and_passes(self):
        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

        task = vm.dictate("include selftest.f")
        self.assertEqual(task.status, "done", f"selftest.f failed with status {task.status}")


class TestVisionAndDesktopCapture(unittest.TestCase):
    """Verifies desktop screenshot capture, region cropping, image compression, and vision Forth words."""

    @classmethod
    def setUpClass(cls):
        cls.vm = VM({"headless": True, "__file__dir__": str(HERE)})
        cls.vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

    def test_capture_desktop_live(self):
        import ai
        try:
            meta = ai.capture_desktop(vm=self.vm)
        except RuntimeError as e:
            if "display handle is invalid" in str(e) or "PowerShell is not available" in str(e):
                self.skipTest(f"Desktop capture skipped: {e}")
            raise
        self.assertIsInstance(meta, dict)
        for key in ("path", "width", "height", "orig_width", "orig_height", "size", "captured_at"):
            self.assertIn(key, meta)
        self.assertTrue(os.path.isfile(meta["path"]))
        self.assertGreater(meta["size"], 0)
        self.assertLessEqual(meta["size"], ai._SCREENSHOT_MAX_BYTES)
        try:
            os.remove(meta["path"])
        except OSError:
            pass

    def test_capture_desktop_region_normalized(self):
        import ai
        try:
            meta = ai.capture_desktop(region=(0.0, 0.0, 0.25, 0.25), vm=self.vm)
        except RuntimeError as e:
            if "display handle is invalid" in str(e) or "PowerShell is not available" in str(e):
                self.skipTest(f"Desktop capture skipped: {e}")
            raise
        self.assertTrue(os.path.isfile(meta["path"]))
        self.assertGreater(meta["width"], 0)
        self.assertGreater(meta["height"], 0)
        try:
            os.remove(meta["path"])
        except OSError:
            pass

    def test_capture_desktop_invalid_args(self):
        import ai
        with self.assertRaises(ValueError):
            ai.capture_desktop(max_dimension=32)
        with self.assertRaises(ValueError):
            ai.capture_desktop(quality=5)
        with self.assertRaises(ValueError):
            ai.capture_desktop(region=[1, 2, 3])
        with self.assertRaises(ValueError):
            ai.capture_desktop(region=[0, 0, -10, 100])

    def test_encode_image_file_data_uri(self):
        import ai
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(
                b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"
                b"\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f"
                b"\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b"
                b"\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01"
                b"\x01\x00\x00?\x00\xbf\x00\xff\xd9"
            )
            temp_path = f.name
        try:
            uri = ai.encode_image_file_data_uri(temp_path, vm=self.vm)
            self.assertTrue(uri.startswith("data:image/jpeg;base64,"))
            self.assertLessEqual(len(uri), ai._IMAGE_DATA_URI_MAX_LEN)
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

    def test_desktop_capture_forth_execution(self):
        output = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = output
            self.vm.dictate("desktop-capture")
        except KernelError as e:
            if "display handle is invalid" in str(e) or "PowerShell is not available" in str(e):
                self.skipTest(f"Desktop capture skipped: {e}")
            raise
        finally:
            sys.stdout = old_stdout

        self.assertGreater(len(self.vm.dstack), 0)
        path = self.vm.pop()
        self.assertIsInstance(path, str)
        self.assertTrue(os.path.isfile(path))
        try:
            os.remove(path)
        except OSError:
            pass


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

    def test_cli_help_flag(self):
        cmd = [sys.executable, str(HERE / "main.py"), "-h"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Usage: f", proc.stdout)
        self.assertIn("-h, --help", proc.stdout)
        self.assertIn("-l, --load", proc.stdout)
        self.assertIn("-e <tokens...>", proc.stdout)
        self.assertIn("run-monitor", proc.stdout)

    def test_cli_execute_option(self):
        cmd = [sys.executable, str(HERE / "main.py"), "-e", "10", "20", "+", ".", "cr"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("30", proc.stdout)

    def test_cli_load_files_in_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            first = Path(tmpdir) / "first.f"
            second = Path(tmpdir) / "second.f"
            first.write_text(": loaded-first 40 ;\n", encoding="utf-8")
            second.write_text(": loaded-second loaded-first 2 + ;\n", encoding="utf-8")

            cmd = [
                sys.executable,
                str(HERE / "main.py"),
                "-l", str(first),
                "--load", str(second),
                "-e", "loaded-second . cr",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
            self.assertIn("42", proc.stdout)

    def test_cli_unknown_option_exits_2(self):
        cmd = [sys.executable, str(HERE / "main.py"), "--bad-flag"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Unknown option", proc.stderr)

    def test_run_monitor_word_defined(self):
        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))
        self.assertIn("run-monitor", vm.words)
        word = vm.words["run-monitor"]
        self.assertIn("diagnostic logging monitor", getattr(word, "help", ""))


class TestSessionDescriptionRules(unittest.TestCase):
    def test_format_description_time_uses_local_timezone_static_text(self):
        from datetime import datetime, timedelta, timezone
        from session_store import format_description_time
        tz_plus_8 = timezone(timedelta(hours=8))
        ts = int(datetime(2026, 4, 19, 6, 58, 26, tzinfo=tz_plus_8).timestamp())
        self.assertEqual(
            format_description_time(ts, tz=tz_plus_8),
            "2026-04-19 06:58:26",
        )

    def test_extract_first_sentence_breaks_on_newline_and_chinese_or_english_punctuation(self):
        from session_store import extract_first_sentence
        self.assertEqual(
            extract_first_sentence("第一行內容\n第二行內容。"),
            "第一行內容",
        )
        self.assertEqual(
            extract_first_sentence("請幫我檢查 ai.f 的設定。接著跑測試！"),
            "請幫我檢查 ai.f 的設定",
        )
        self.assertEqual(
            extract_first_sentence("為什麼 3.14 會出現錯誤？請看第 2 行"),
            "為什麼 3.14 會出現錯誤",
        )
        self.assertEqual(
            extract_first_sentence("Check version 3.14 in ai.f. Then run tests!"),
            "Check version 3.14 in ai.f",
        )
        self.assertEqual(
            extract_first_sentence("What is inside peforth/ai.py? Let me know."),
            "What is inside peforth/ai.py",
        )

    def test_extract_first_sentence_truncates_at_80_unicode_chars_with_ellipsis(self):
        from session_store import extract_first_sentence
        long_clause = "甲" * 80
        self.assertEqual(extract_first_sentence(long_clause + "。後續"), long_clause)

        over_80 = "乙" * 81
        self.assertEqual(
            extract_first_sentence(over_80 + "。後續"),
            ("乙" * 80) + "...",
        )

    def test_extract_first_user_message_skips_non_user_items(self):
        from session_store import extract_first_user_message_text
        items = [
            {"id": "item_0", "type": "reasoning", "summary": [{"text": "thinking"}]},
            {
                "id": "item_1",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Assistant greeting."}],
            },
            {
                "id": "item_2",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "使用者的第一句話。第二句話。"}],
            },
            {
                "id": "item_3",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "第二則使用者訊息。"}],
            },
        ]
        self.assertEqual(
            extract_first_user_message_text(items),
            "使用者的第一句話。第二句話。",
        )

    def test_build_session_description_placeholder_and_overwrite_protection(self):
        from datetime import datetime, timedelta, timezone
        from session_store import build_session_description, is_complete_description
        tz_plus_8 = timezone(timedelta(hours=8))
        ts = int(datetime(2026, 4, 19, 6, 58, 26, tzinfo=tz_plus_8).timestamp())

        # No user message yet -> save only the time prefix
        placeholder = build_session_description(ts, [], existing_description=None, tz=tz_plus_8)
        self.assertEqual(placeholder, "2026-04-19 06:58:26")
        self.assertFalse(is_complete_description(placeholder))

        # Later sync brings a user message -> completes the description
        items = [
            {
                "id": "msg_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "請實作 AI session 本地副本。"}],
            }
        ]
        completed = build_session_description(ts, items, existing_description=placeholder, tz=tz_plus_8)
        self.assertEqual(completed, "2026-04-19 06:58:26 | 請實作 AI session 本地副本")
        self.assertTrue(is_complete_description(completed))

        # Subsequent syncs or user modifications are never overwritten
        other_items = [
            {
                "id": "msg_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "完全不同的訊息。"}],
            }
        ]
        self.assertEqual(
            build_session_description(ts, other_items, existing_description=completed, tz=tz_plus_8),
            completed,
        )
        custom_desc = "手動標記的重要重點 Session"
        self.assertEqual(
            build_session_description(ts, other_items, existing_description=custom_desc, tz=tz_plus_8),
            custom_desc,
        )


class TestSessionStoreAndSync(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.env_patch = patch.dict(
            "os.environ",
            {
                "PEFORTH_CONFIG_DIR": str(self.config_dir),
                "PEFORTH_AI_LOG_MODE": "disabled",
            },
        )
        self.env_patch.start()
        self.vm = VM({"headless": True, "__file__dir__": str(HERE)})
        self.vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

    def tearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def test_schema_creation_and_role_null_for_non_message_items(self):
        import ai
        from session_store import SessionStore, SCHEMA_VERSION
        db_path = ai._session_db_path()
        self.assertEqual(db_path, self.config_dir / "sessions" / "sessions.sqlite3")
        with SessionStore(db_path) as store:
            version = store.connection.execute("PRAGMA user_version").fetchone()[0]
            self.assertEqual(version, SCHEMA_VERSION)
            items = [
                {
                    "id": "item_msg_1",
                    "turn_id": "turn_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Hello SQLite mirror!"}],
                },
                {
                    "id": "item_call_1",
                    "turn_id": "turn_1",
                    "type": "function_call",
                    "role": "ignored_for_non_message",
                    "name": "forth_eval",
                    "arguments": '{"code": "words"}',
                },
            ]
            store.sync_session(
                {
                    "id": "sess_schema_1",
                    "created_at": 1700000000,
                    "last_active_at": 1700000100,
                    "status": "idle",
                    "agent": {"model": "gpt-4o-mini"},
                },
                items,
            )
            rows = store.connection.execute(
                "SELECT id, seq, turn_id, type, role, raw_json FROM session_items "
                "WHERE session_id = ? ORDER BY seq ASC",
                ("sess_schema_1",),
            ).fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["id"], "item_msg_1")
            self.assertEqual(rows[0]["seq"], 0)
            self.assertEqual(rows[0]["role"], "user")
            self.assertEqual(rows[1]["id"], "item_call_1")
            self.assertEqual(rows[1]["seq"], 1)
            self.assertIsNone(rows[1]["role"])

    def test_differential_sync_skips_unchanged_and_marks_remote_deleted(self):
        import ai
        remote_v1 = [
            {
                "id": "sess_a",
                "created_at": 1700000200,
                "last_active_at": 1700000250,
                "status": "idle",
                "agent": {"model": "gpt-4o-mini"},
            },
            {
                "id": "sess_b",
                "created_at": 1700000100,
                "last_active_at": 1700000150,
                "status": "idle",
                "agent": {"model": "gpt-4o-mini"},
            },
        ]
        items_by_session = {
            "sess_a": [
                {
                    "id": "a_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Session A first prompt."}],
                }
            ],
            "sess_b": [
                {
                    "id": "b_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Session B first prompt."}],
                }
            ],
        }

        with patch.object(ai, "_list_remote_sessions", return_value=remote_v1), \
                patch.object(ai, "_fetch_session_items", side_effect=lambda sid: items_by_session[sid]) as fetch_mock:
            stats1 = ai.sync_sessions(self.vm)
            self.assertEqual(stats1["synced"], 2)
            self.assertEqual(stats1["skipped"], 0)
            self.assertEqual(stats1["deleted"], 0)
            self.assertEqual(fetch_mock.call_count, 2)

            # Second sync with identical last_active_at makes zero item requests
            fetch_mock.reset_mock()
            stats2 = ai.sync_sessions(self.vm)
            self.assertEqual(stats2["synced"], 0)
            self.assertEqual(stats2["skipped"], 2)
            self.assertEqual(stats2["deleted"], 0)
            fetch_mock.assert_not_called()

        # Third sync: sess_a has newer last_active_at, sess_b disappeared remotely
        remote_v2 = [
            {
                "id": "sess_a",
                "created_at": 1700000200,
                "last_active_at": 1700000300,
                "status": "idle",
                "agent": {"model": "gpt-4o-mini"},
            }
        ]
        items_by_session["sess_a"] = [
            {
                "id": "a_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Changed text should not overwrite description."}],
            },
            {
                "id": "a_2",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Second item added."}],
            },
        ]
        with patch.object(ai, "_list_remote_sessions", return_value=remote_v2), \
                patch.object(ai, "_fetch_session_items", side_effect=lambda sid: items_by_session[sid]) as fetch_mock:
            stats3 = ai.sync_sessions(self.vm)
            self.assertEqual(stats3["synced"], 1)
            self.assertEqual(stats3["skipped"], 0)
            self.assertEqual(stats3["deleted"], 1)
            fetch_mock.assert_called_once_with("sess_a")

        with ai._open_session_store() as store:
            sess_a = store.get_session("sess_a")
            sess_b = store.get_session("sess_b")
            self.assertIsNotNone(sess_a)
            self.assertIsNotNone(sess_b)
            self.assertIn("Session A first prompt", sess_a["description"])
            self.assertEqual(sess_a["remote_deleted"], 0)
            self.assertEqual(len(store.get_session_items("sess_a")), 2)
            # sess_b is marked remote_deleted = 1 but its local data and items are preserved
            self.assertEqual(sess_b["remote_deleted"], 1)
            self.assertEqual(len(store.get_session_items("sess_b")), 1)
            self.assertEqual([r["id"] for r in store.list_sessions(include_deleted=False)], ["sess_a"])
            self.assertEqual(len(store.list_sessions(include_deleted=True)), 2)

    def test_failed_session_sync_is_atomic_and_retried_next_time(self):
        import ai
        remote = [
            {"id": "sess_ok", "created_at": 1700000200, "last_active_at": 1700000250},
            {"id": "sess_fail", "created_at": 1700000100, "last_active_at": 1700000150},
        ]

        def flaky_fetch(sid):
            if sid == "sess_fail":
                raise RuntimeError("Simulated network failure")
            return [
                {
                    "id": "ok_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "OK session."}],
                }
            ]

        with patch.object(ai, "_list_remote_sessions", return_value=remote), \
                patch.object(ai, "_fetch_session_items", side_effect=flaky_fetch):
            with self.assertRaises(RuntimeError):
                ai.sync_sessions(self.vm)

        with ai._open_session_store() as store:
            self.assertIsNotNone(store.get_session("sess_ok"))
            self.assertIsNone(store.get_session("sess_fail"))

        # Next sync succeeds and only needs to fetch sess_fail
        with patch.object(ai, "_list_remote_sessions", return_value=remote), \
                patch.object(
                    ai,
                    "_fetch_session_items",
                    return_value=[
                        {
                            "id": "fail_recovered_1",
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Recovered session."}],
                        }
                    ],
                ) as fetch_mock:
            stats = ai.sync_sessions(self.vm)
            self.assertEqual(stats["synced"], 1)
            self.assertEqual(stats["skipped"], 1)
            fetch_mock.assert_called_once_with("sess_fail")

    def test_forth_words_ai_sync_ai_export_session_and_ai_search(self):
        import ai
        remote = [
            {
                "id": "sess_export_12345678",
                "created_at": 1700000500,
                "last_active_at": 1700000550,
                "status": "idle",
                "agent": {"model": "gpt-4o-mini"},
            }
        ]
        raw_items = [
            {
                "id": "item_u1",
                "turn_id": "turn_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "請備份這個特別標籤。還有更多細節。"}],
            },
            {
                "id": "item_a1",
                "turn_id": "turn_1",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "好，已經同步到本地 SQLite 資料庫。"}],
            },
        ]

        with patch.object(ai, "_list_remote_sessions", return_value=remote), \
                patch.object(ai, "_fetch_session_items", return_value=raw_items):
            sync_out = io.StringIO()
            with contextlib.redirect_stdout(sync_out):
                self.vm.dictate("ai-sync")
            self.assertIn("Synced AI sessions: 1 updated, 0 unchanged", sync_out.getvalue())

        export_file = self.config_dir / "exported-session.json"
        export_out = io.StringIO()
        with contextlib.redirect_stdout(export_out):
            self.vm.push(1)
            self.vm.push(str(export_file))
            self.vm.execute(self.vm.tick("ai-export-session"))
        self.assertTrue(export_file.is_file())
        exported_data = json.loads(export_file.read_text(encoding="utf-8"))
        self.assertEqual(exported_data, raw_items)

        search_out = io.StringIO()
        with contextlib.redirect_stdout(search_out):
            self.vm.dictate("ai-search 特別標籤")
        rendered_search = search_out.getvalue()
        self.assertIn("Matched 1 local session(s)", rendered_search)
        self.assertIn("sess_export_12345678", rendered_search)
        self.assertIn("請備份這個特別標籤", rendered_search)

    def test_peforth_search_sessions_direct_tool_runs_without_approval(self):
        import ai
        with ai._open_session_store() as store:
            store.sync_session(
                {
                    "id": "sess_direct_12345678",
                    "created_at": 1700000100,
                    "last_active_at": 1700000150,
                    "status": "idle",
                    "agent": {"model": "gpt-4o-mini"},
                },
                [
                    {
                        "id": "u1",
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "調整螢幕亮度到 50%。"}],
                    },
                    {
                        "id": "a1",
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "已將螢幕亮度調到 50%。"}],
                    },
                ],
            )

        res = ai.query_local_sessions(query="螢幕亮度")
        self.assertEqual(len(res["sessions"]), 1)
        self.assertEqual(res["sessions"][0]["session_id"], "sess_direct_12345678")

    def test_ai_status_and_ai_use_lifecycle(self):
        """Test ai-status displays local in-memory session, remote session, and none correctly."""
        import ai
        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

        # 1. Fresh state: no remote session, no local messages
        out_fresh = io.StringIO()
        with contextlib.redirect_stdout(out_fresh):
            vm.dictate("ai-status")
        self.assertIn("Active AI session: none", out_fresh.getvalue())
        self.assertIn("fresh local conversation", out_fresh.getvalue())

        # 2. Local in-memory session with turns
        vm.host["ai_messages"] = [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "測試對話主題。第一句在此。"},
            {"role": "assistant", "content": "收到測試。"},
            {"role": "user", "content": "第二輪對話"},
        ]
        out_local = io.StringIO()
        with contextlib.redirect_stdout(out_local):
            vm.dictate("ai-status")
        val = out_local.getvalue()
        self.assertIn("Active AI session: local (in-memory)", val)
        first_local_id = vm.host.get("ai_local_session_id")
        self.assertTrue(first_local_id and first_local_id.startswith("local_"))
        self.assertIn(f"[{first_local_id}]", val)
        self.assertIn("Topic: 測試對話主題", val)
        self.assertIn("Turns: 2 user turn(s)", val)

        # 3. Remote session active (via ai_active_session_id)
        detail = {
            "id": "sess_remote_9999",
            "created_at": 1700000000,
            "last_active_at": 1700000050,
            "status": "idle",
            "agent": {"model": "gpt-remote-model"},
            "usage": {"input_tokens": 12, "output_tokens": 34, "total_tokens": 46},
        }
        with patch.object(ai, "_api_get", return_value=detail), \
             patch.object(ai, "_session_title", return_value="Remote Session Title"):
            vm.host["ai_active_session_id"] = "sess_remote_9999"
            out_remote = io.StringIO()
            with contextlib.redirect_stdout(out_remote):
                vm.dictate("ai-status")
            val_remote = out_remote.getvalue()
            self.assertIn("Session current: Remote Session Title [sess_remote_9999]", val_remote)
            self.assertIn("Model: gpt-remote-model", val_remote)
            self.assertIn("Local turns: 2 user turn(s) active in memory", val_remote)

        # 4. ai-new clears remote session, local session ID, and local messages
        with contextlib.redirect_stdout(io.StringIO()):
            vm.dictate("ai-new")
        self.assertNotIn("ai_active_session_id", vm.host)
        self.assertNotIn("ai_local_session_id", vm.host)
        self.assertNotIn("ai_messages", vm.host)
        out_after_new = io.StringIO()
        with contextlib.redirect_stdout(out_after_new):
            vm.dictate("ai-status")
        self.assertIn("Active AI session: none", out_after_new.getvalue())

        # 5. Starting a new local conversation after ai-new gets a distinct local_session_id
        second_local_id = ai._ensure_local_session_id(vm)
        self.assertTrue(second_local_id.startswith("local_"))
        self.assertNotEqual(first_local_id, second_local_id)

    def test_distill_messages_for_promotion(self):
        import json
        import ai

        messages = [
            {"role": "system", "content": "Huge system prompt with skills"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Define a word to triple a number and test it on 7."},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="}},
                ],
            },
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_lookup_1",
                        "type": "function",
                        "function": {"name": "peforth_search_words", "arguments": json.dumps({"query": "triple"})},
                    },
                    {
                        "id": "call_fail_1",
                        "type": "function",
                        "function": {"name": "peforth_run_forth", "arguments": json.dumps({"source": ": triple 3 * ;", "purpose": "define triple"})},
                    },
                    {
                        "id": "call_ok_1",
                        "type": "function",
                        "function": {"name": "peforth_run_forth", "arguments": json.dumps({"source": ": triple 3 * ; 7 triple", "purpose": "define and test triple"})},
                    },
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_lookup_1",
                "content": json.dumps({"matches": [{"name": "*", "help": "multiply"}]}),
            },
            {
                "role": "tool",
                "tool_call_id": "call_fail_1",
                "content": json.dumps({"approved": False, "status": "denied", "error": "User denied execution"}),
            },
            {
                "role": "tool",
                "tool_call_id": "call_ok_1",
                "content": json.dumps({
                    "approved": True,
                    "status": "completed",
                    "error": None,
                    "stdout": (
                        "\x1b[33mPurpose: Execution of unsafe word 'triple'\x1b[0m\n"
                        "Forth action:\n: triple 3 * ;\n"
                        "1. Allow Once\n2. Trust this AI task\n3. Deny this proposal\n4. Cancel this AI task\n"
                        "Choose 1-4: 1\nResult OK\n"
                    ),
                    "dstack": ["21"],
                }),
            },
            {
                "role": "assistant",
                "content": "I have defined `triple` and verified `7 triple` leaves `21` on the stack.",
            },
        ]

        distilled = ai.distill_messages_for_promotion(messages)
        self.assertEqual(distilled["user_turns"], 1)
        self.assertEqual(distilled["assistant_replies"], 1)
        self.assertEqual(distilled["kept_tool_calls"], 1)
        self.assertGreaterEqual(distilled["removed_noise_items"], 2)

        promoted = distilled["promoted_input"]
        self.assertNotIn("Huge system prompt", promoted)
        self.assertNotIn("iVBORw0KGgo", promoted)
        self.assertIn("[Image attached]", promoted)
        self.assertIn("Define a word to triple a number", promoted)
        self.assertIn(": triple 3 * ; 7 triple", promoted)
        self.assertIn("Result OK", promoted)
        self.assertNotIn("Choose 1-4:", promoted)
        self.assertIn("I have defined `triple`", promoted)

    def test_ai_promote_and_dual_mode_routing(self):
        import io
        import contextlib
        from unittest.mock import patch
        import ai

        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))
        vm.host["ai_messages"] = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "Hello local world."},
            {"role": "assistant", "content": "Hi there!"},
        ]

        # 1. Cancel ai-promote (choice "2") -> stays in local Stateless mode
        out_cancel = io.StringIO()
        with patch.object(ai, "read_numbered_choice", return_value="2"), \
             contextlib.redirect_stdout(out_cancel):
            vm.dictate("ai-promote")
        self.assertIn("Promotion cancelled", out_cancel.getvalue())
        self.assertIsNone(vm.host.get("ai_active_session_id"))
        self.assertEqual(len(vm.host.get("ai_messages", [])), 3)

        # 2. Approve ai-promote (choice "1") -> creates remote session and clears ai_messages
        def fake_stateful_promote(vm_arg, prompt, stream_response, session_id=None, create_new=False, **kwargs):
            if False:
                yield None
            self.assertTrue(create_new)
            self.assertIn("Hello local world.", prompt)
            vm_arg.host["ai_active_session_id"] = "sess_promoted_777"

        out_promote = io.StringIO()
        with patch.object(ai, "read_numbered_choice", return_value="1"), \
             patch.object(ai, "ai_turn_stateful", side_effect=fake_stateful_promote), \
             contextlib.redirect_stdout(out_promote):
            vm.dictate("ai-promote")
        self.assertEqual(vm.host.get("ai_active_session_id"), "sess_promoted_777")
        self.assertNotIn("ai_messages", vm.host)
        self.assertIn("Promoted local conversation to remote session: sess_promoted_777", out_promote.getvalue())

        # 3. When ai_active_session_id is set, ai_turn routes to ai_turn_stateful
        routed_calls = []

        def fake_stateful_turn(vm_arg, prompt, stream_response, session_id=None, **kwargs):
            if False:
                yield None
            routed_calls.append((session_id, prompt, stream_response))

        with patch.object(ai, "ai_turn_stateful", side_effect=fake_stateful_turn):
            vm.dictate('s" Follow-up in remote session" false (ai)')
        self.assertEqual(routed_calls, [("sess_promoted_777", "Follow-up in remote session", False)])

        # 4. ai-use switches to remote session and clears ai_messages (no 50-message preload)
        vm.host["ai_messages"] = [{"role": "user", "content": "leftover"}]
        with patch.object(ai, "_list_remote_sessions", return_value=[{"id": "sess_other_888"}]), \
             patch.object(ai, "_api_get", return_value={"id": "sess_other_888"}), \
             patch.object(ai, "_session_title", return_value="Other Session"), \
             contextlib.redirect_stdout(io.StringIO()):
            vm.dictate('s" sess_other_888" ai-use')
        self.assertEqual(vm.host.get("ai_active_session_id"), "sess_other_888")
        self.assertNotIn("ai_messages", vm.host)

    def test_ai_context_dual_mode(self):
        import io
        import contextlib
        from unittest.mock import patch, MagicMock
        import ai

        vm = VM({"headless": True, "__file__dir__": str(HERE)})
        vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))

        # --- 1. Stateless mode ---
        vm.host.pop("ai_active_session_id", None)
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Hi there"},
            {"role": "assistant", "content": "Hello!"},
        ]
        vm.host["ai_messages"] = list(messages)

        # Call via Forth word ai-context
        vm.dictate("ai-context")
        self.assertEqual(len(vm.dstack), 1)
        ctx = vm.pop()
        self.assertIsInstance(ctx, dict)
        self.assertEqual(ctx["mode"], "stateless")
        self.assertTrue(ctx["session_id"].startswith("local_"))
        self.assertEqual(len(ctx["items"]), 3)
        self.assertEqual(ctx["items"][1]["content"], "Hi there")

        # Mutating returned ctx does not alter vm.host["ai_messages"]
        ctx["items"].append({"role": "user", "content": "Extra"})
        self.assertEqual(len(vm.host["ai_messages"]), 3)

        # Test ai-status in Stateless mode
        out_stateless = io.StringIO()
        with contextlib.redirect_stdout(out_stateless):
            vm.dictate("ai-status")
        status_val = out_stateless.getvalue()
        self.assertIn("Mode: Stateless", status_val)
        self.assertIn("Turns: 1 user turn(s) (3 messages in context)", status_val)

        # --- 2. Stateful mode ---
        vm.host["ai_active_session_id"] = "sess_stateful_test"
        remote_metadata = {
            "id": "sess_stateful_test",
            "last_active_at": 1700000000,
            "status": "completed",
        }
        raw_remote_items = [
            {"id": "item_1", "type": "message", "role": "user", "content": [{"type": "text", "text": "Remote prompt"}]},
            {"id": "item_2", "type": "message", "role": "assistant", "content": [{"type": "text", "text": "Remote answer"}]},
        ]

        # Case A: needs_item_sync is True -> fetches remote items and syncs mirror
        mock_store = MagicMock()
        mock_store.needs_item_sync.return_value = True
        mock_store.get_session_items.return_value = raw_remote_items

        with patch.object(ai, "_open_session_store") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_store
            with patch.object(ai, "_api_get", return_value=remote_metadata) as mock_get:
                with patch.object(ai, "_fetch_session_items", return_value=raw_remote_items) as mock_fetch:
                    vm.dictate("ai-context")
                    self.assertEqual(len(vm.dstack), 1)
                    st_ctx = vm.pop()
                    self.assertEqual(st_ctx["mode"], "stateful")
                    self.assertEqual(st_ctx["session_id"], "sess_stateful_test")
                    self.assertEqual(st_ctx["items"], raw_remote_items)
                    mock_fetch.assert_called_once_with("sess_stateful_test")
                    mock_store.sync_session.assert_called_once_with(remote_metadata, raw_remote_items)

        # Case B: needs_item_sync is False -> fast path: uses local mirror without fetching items
        mock_store_fresh = MagicMock()
        mock_store_fresh.needs_item_sync.return_value = False
        mock_store_fresh.get_session_items.return_value = raw_remote_items

        with patch.object(ai, "_open_session_store") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_store_fresh
            with patch.object(ai, "_api_get", return_value=remote_metadata):
                with patch.object(ai, "_fetch_session_items") as mock_fetch_never:
                    st_ctx2 = ai.get_ai_context(vm)
                    self.assertEqual(st_ctx2["mode"], "stateful")
                    self.assertEqual(st_ctx2["items"], raw_remote_items)
                    mock_fetch_never.assert_not_called()
                    mock_store_fresh.update_session_metadata.assert_called_once_with(remote_metadata)

        # Chat turn count can be derived directly from items
        user_turns = [
            it for it in st_ctx2["items"]
            if (it.get("role") == "user" or (it.get("type") == "message" and it.get("role") == "user"))
        ]
        self.assertEqual(len(user_turns), 1)




if __name__ == "__main__":
    print("=" * 60)
    print(" Running peforth Architectural & Self-Test Suite")
    print("=" * 60)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
