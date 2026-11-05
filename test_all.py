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
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
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

    def test_skills_loading_and_list_skills_word(self):
        import ai
        names, text = ai.load_all_skills(HERE / "skills")
        self.assertIn("herdr", names)
        self.assertIn("peforth-forth", names)
        self.assertIn("windows-screen-capture", names)
        self.assertIn("windows-msgbox", names)
        self.assertIn("ai-diagnostics-log-inspector", names)
        self.assertIn("line-notify", names)

        # Prompt includes skills and reference
        prompt = ai.get_system_prompt(self.vm)
        self.assertIn("## Skill: herdr", prompt)
        self.assertIn("## Skill: peforth-forth", prompt)
        self.assertIn("Forth Reference", prompt)
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



if __name__ == "__main__":
    print("=" * 60)
    print(" Running peforth Architectural & Self-Test Suite")
    print("=" * 60)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
