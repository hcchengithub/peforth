import contextlib
from datetime import datetime
import importlib.machinery
import os
import importlib.util
import io
import math
import pathlib
import tempfile
import json
import sqlite3
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.data_structures import Size
from prompt_toolkit.document import Document
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.output.vt100 import Vt100_Output
from prompt_toolkit.shortcuts import CompleteStyle

from peforth.diagnostic_log import DiagnosticLog
from peforth.projectk import VM, Input, ForthError, DEMO
from peforth import repl as _f_mod
Constant = _f_mod.Constant
Value = _f_mod.Value


class KernelTests(unittest.TestCase):
    def setUp(self):
        self._diagnostics_patch = patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"})
        self._diagnostics_patch.start()
        self.addCleanup(self._diagnostics_patch.stop)

    def boot(self):
        vm = VM(host={'ForthError': ForthError})
        with contextlib.redirect_stdout(io.StringIO()):
            vm.dictate(DEMO).resume()
        return vm

    def test_seed_and_independent_instances(self):
        a, b = VM(), VM()
        self.assertEqual(set(a.words), {'code', 'end-code'})
        a.push(1)
        self.assertEqual(b.stack, [])

    def test_tick_and_callable_constant(self):
        vm = self.boot()
        self.assertIsNone(vm.tick('missing'))
        ten = vm.tick('ten')
        self.assertEqual(ten.value, 10)
        vm.dictate('ten')
        self.assertEqual(vm.pop(), 10)

    def test_exact_integers_and_literals(self):
        vm = VM()
        vm.dictate('9007199254740993 -0x10 2.5 0b11')
        self.assertEqual(vm.stack, [9007199254740993, -16, 2.5, 3])

    def test_host_objects(self):
        resource = {'name': 'resource'}
        vm = VM(host={'resource': resource})
        vm.dictate('code resource\n    vm.push(resource)\nend-code\nresource')
        self.assertIs(vm.pop(), resource)

    def test_input_regions(self):
        source = Input(' name first line\nseveral\nlines| tail')
        self.assertEqual(source.read(), 'name')
        self.assertEqual(source.read(until='\n'), ' first line')
        self.assertEqual(source.read(until='|'), 'several\nlines')
        self.assertEqual(source.read(), 'tail')
        self.assertIsNone(source.read())

    def test_input_uses_one_string_and_character_offset(self):
        source = Input(": square dup * ; 5 square")
        original_tib = source.tib
        self.assertIsInstance(source.tib, str)
        self.assertEqual(source.itib, 0)

        self.assertEqual(source.read(), ":")
        self.assertEqual(source.tib, original_tib)
        self.assertEqual(source.itib, 1)
        self.assertEqual(source.read(), "square")
        self.assertGreater(source.itib, 1)

    def test_input_append_at_tail_is_read_after_existing_text(self):
        source = Input("1 2")
        self.assertEqual(source.read(), "1")
        source.append(" 3 4")

        self.assertEqual([source.read(), source.read(), source.read()], ["2", "3", "4"])
        self.assertIsNone(source.read())

    def test_paused_task_can_append_input_and_resume(self):
        vm = VM()
        vm.define("pause", lambda v: v.pause())
        task = vm.dictate("1 pause 2")
        self.assertEqual(task.status, "paused")

        task.append_input(" 3")
        self.assertEqual(task.resume().status, "done")
        self.assertEqual(vm.stack, [1, 2, 3])

    def test_t_stack_words_are_task_private(self):
        vm = _f_mod.create_vm()
        first = vm.dictate("11 >t t@ t>")
        self.assertEqual(vm.stack, [11, 11])
        self.assertEqual(first.tstack, [])

        vm.define("pause", lambda v: v.pause())
        paused = vm.dictate("22 >t pause")
        self.assertEqual(paused.status, "paused")
        self.assertEqual(paused.tstack, [22])

        other = vm.dictate("33 >t")
        self.assertEqual(other.tstack, [33])
        self.assertEqual(paused.tstack, [22])

    def test_t_stack_words_report_underflow(self):
        vm = _f_mod.create_vm()
        with self.assertRaisesRegex(ForthError, "T-stack underflow"):
            vm.dictate("t@")
        with self.assertRaisesRegex(ForthError, "T-stack underflow"):
            vm.dictate("t>")

    def test_tib_append_word_adds_source_during_execution(self):
        vm = _f_mod.create_vm()

        task = vm.dictate('s" 42" tib.append 7')
        self.assertEqual(task.status, "done")
        self.assertEqual(vm.stack, [7, 42])
        self.assertEqual(task.inputs, [])

    def test_task_append_after_end_of_input_does_not_revive_done_task(self):
        vm = VM()
        task = vm.dictate("1")
        self.assertEqual(task.status, "done")
        with self.assertRaisesRegex(ForthError, "Cannot append input to a done task"):
            task.append_input(" 2")
        self.assertEqual(vm.stack, [1])

    def test_composition_and_capture(self):
        vm = self.boot()
        vm.dictate(': old 6 square ;')
        vm.define('square', lambda v: v.push(99))
        vm.dictate('old square')
        self.assertEqual(vm.stack, [36, 99])

    def test_immediate_string_and_null_literal(self):
        vm = self.boot()
        vm.dictate(': message s" hello\nworld" ; message')
        self.assertEqual(vm.pop(), 'hello\nworld')
        vm.begin('nothing'); vm.literal(None); vm.finish()
        vm.execute('nothing')
        self.assertIsNone(vm.pop())

    def test_comma(self):
        vm = self.boot()
        vm.begin('calc')
        vm.literal(10)
        vm.comma(vm.tick('*'))
        vm.comma(vm.tick('square'))
        vm.finish()
        calc = vm.tick('calc')
        self.assertEqual(len(calc.action), 3)

        # Outside compiling raises error
        with self.assertRaisesRegex(ForthError, 'No definition is being built'):
            vm.comma(vm.tick('*'))

    def test_pause_inside_composition_and_source(self):
        vm = self.boot()
        vm.dictate(': step 1 pause 2 ;')
        task = vm.dictate('step 3')
        self.assertEqual((task.status, vm.stack), ('paused', [1]))
        self.assertEqual(task.resume().status, 'done')
        self.assertEqual(vm.stack, [1, 2, 3])
        self.assertFalse(task.inputs)

    def test_nested_resumable_work(self):
        vm = self.boot()
        def nested(v):
            yield from v.evaluate('5 pause 6')
            v.push(7)
        vm.define('nested', nested)
        task = vm.dictate('nested 8')
        self.assertEqual(vm.stack, [5])
        task.resume()
        self.assertEqual(vm.stack, [5, 6, 7, 8])

    def test_host_reentry(self):
        vm = VM()
        vm.define('nested', lambda v: v.dictate('20'))
        vm.dictate('10 nested 30')
        self.assertEqual(vm.stack, [10, 20, 30])

    def test_generator_continuation(self):
        vm = VM()
        def word(v):
            v.push('before')
            yield v.pause()
            v.push('after')
        vm.define('work', word)
        task = vm.execute('work')
        self.assertEqual(vm.stack, ['before'])
        task.resume()
        self.assertEqual(vm.stack, ['before', 'after'])

    def test_definition_across_inputs(self):
        vm = self.boot()
        vm.dictate(': twice dup')
        self.assertTrue(vm.compiling)
        vm.dictate('* ; 7 twice')
        self.assertEqual(vm.stack, [49])

    def test_bad_definition_preserves_old_word(self):
        vm = VM()
        vm.define('keep', lambda v: v.push(1))
        with self.assertRaises(ForthError):
            vm.dictate('code keep\n    this is invalid syntax!\nend-code')
        vm.dictate('keep')
        self.assertEqual(vm.pop(), 1)

    def test_definition_errors_recover(self):
        vm = self.boot()
        with self.assertRaises(ForthError):
            vm.dictate(': broken missing ;')
        self.assertFalse(vm.compiling)
        self.assertNotIn('broken', vm.words)
        vm.dictate('8 square')
        self.assertEqual(vm.pop(), 64)

    def test_abort_and_cancel(self):
        vm = self.boot()
        vm.define('abort', lambda v: v.abort())
        self.assertEqual(vm.dictate('1 abort 2').status, 'aborted')
        self.assertEqual(vm.stack, [1])
        task = vm.dictate('3 pause 4')
        task.cancel()
        self.assertEqual(task.status, 'aborted')
        self.assertFalse(task.inputs)
        vm.dictate('5')
        self.assertEqual(vm.stack, [1, 3, 5])

    def test_string_terminator_is_data(self):
        vm = VM()
        vm.dictate('code message\n    vm.push("""hello\nend-code\nworld""")\nend-code\nmessage 7')
        self.assertEqual(vm.stack, ['hello\nend-code\nworld', 7])

    def test_code_single_line_and_inline_end_code(self):
        vm = VM()
        vm.dictate("code inc vm.push(vm.pop() + 1) end-code 5 inc")
        self.assertEqual(vm.stack, [6])
        vm.dictate("code double vm.push(vm.pop() * 2) end-code 7 double")
        self.assertEqual(vm.stack, [6, 14])
        vm.dictate("code triple\n    x = vm.pop()\n    vm.push(x * 3) end-code\n10 triple")
        self.assertEqual(vm.stack, [6, 14, 30])
        vm.dictate("code with_comment\n    # end-code in comment\n    vm.push(99) end-code\nwith_comment")
        self.assertEqual(vm.stack, [6, 14, 30, 99])


    def test_diagnostics_and_retry(self):
        vm = VM()
        with self.assertRaisesRegex(ForthError, 'empty'):
            vm.pop()
        for text in ['unknown', 'end-code', 'code', 'code broken\n vm.push(1)']:
            with self.assertRaises(ForthError):
                vm.dictate(text)
            vm.dictate('42')
            self.assertEqual(vm.pop(), 42)
        self.assertFalse(vm._active)

    def test_failure_after_pause(self):
        vm = VM()
        def bad(v):
            yield v.pause()
            raise ValueError('oops')
        vm.define('bad', bad)
        task = vm.dictate('bad 9')
        with self.assertRaisesRegex(ForthError, 'oops'):
            task.resume()
        self.assertEqual(task.status, 'failed')
        self.assertFalse(task.inputs)
        vm.dictate('10')
        self.assertEqual(vm.pop(), 10)

    def test_invalid_yield_closes_continuation(self):
        vm = VM()
        def bad(v):
            yield 'unexpected'
        vm.define('bad', bad)
        with self.assertRaises(ForthError):
            vm.dictate('bad 9')
        self.assertFalse(vm._active)
        vm.dictate('10')
        self.assertEqual(vm.pop(), 10)

    def test_pop_with_depth(self):
        vm = VM()
        vm.push(10, 20, 30)
        self.assertEqual(vm.pop(0), 30)
        self.assertEqual(vm.pop(1), 10)
        self.assertEqual(vm.pop(), 20)
        with self.assertRaisesRegex(ForthError, 'empty'):
            vm.pop()
        vm.push(10)
        with self.assertRaisesRegex(ForthError, 'depth'):
            vm.pop(1)

    def test_word_help_and_comment_fields(self):
        vm = VM()
        word = vm.define('greet', lambda v: None, help='say hello', comment='\tnote\n')
        self.assertEqual(word.help, 'say hello')
        self.assertEqual(word.comment, '\tnote\n')
        word2 = vm.define('bye', lambda v: None)
        self.assertEqual(word2.help, '')
        self.assertEqual(word2.comment, '')

    def test_value_class_and_property(self):
        vm = VM()
        word = vm.define('total', Value(10), type='value')
        self.assertEqual(word.value, 10)
        word.value = 25
        self.assertEqual(word.value, 25)
        self.assertEqual(word.action.value, 25)
        vm.execute('total')
        self.assertEqual(vm.pop(), 25)

        const_word = vm.define('limit', Constant(100), type='constant')
        self.assertEqual(const_word.value, 100)


class ReplCompletionTests(unittest.TestCase):
    def run_prompt(self, chunks, vm, output=None):
        with create_pipe_input() as prompt_input:
            session = PromptSession(
                multiline=True,
                completer=_f_mod.ForthWordCompleter(vm),
                key_bindings=_f_mod._make_repl_key_bindings(vm),
                complete_style=CompleteStyle.MULTI_COLUMN,
                complete_while_typing=False,
                input=prompt_input,
                output=output or DummyOutput(),
            )

            def feed_input():
                for chunk in chunks:
                    prompt_input.send_text(chunk)
                    time.sleep(0.08)

            feeder = threading.Thread(target=feed_input)
            feeder.start()
            try:
                return session.prompt()
            finally:
                feeder.join()

    def test_forth_completer_matches_case_insensitive_prefix_and_keeps_original_names(self):
        vm = SimpleNamespace(
            words={"dup": object(), "DUPLICATE": object(), "drop": object()},
            host={"repl_mode": "forth"},
        )
        completer = _f_mod.ForthWordCompleter(vm)

        actual = list(completer.get_completions(
            Document("dUp"), CompleteEvent(completion_requested=True)))

        self.assertEqual([completion.text for completion in actual], ["dup", "DUPLICATE"])

    def test_completer_uses_current_token_and_preserves_text_after_cursor(self):
        vm = SimpleNamespace(
            words={"dup": object(), "DUPLICATE": object(), "foo": object()},
            host={"repl_mode": "forth"},
        )
        completer = _f_mod.ForthWordCompleter(vm)
        document = Document("foo dUpTAIL", cursor_position=len("foo dUp"))

        actual = list(completer.get_completions(
            document, CompleteEvent(completion_requested=True)))

        self.assertEqual([completion.text for completion in actual], ["dup", "DUPLICATE"])
        self.assertEqual([completion.start_position for completion in actual], [-3, -3])

    def test_completer_reads_live_dictionary_and_suppresses_empty_or_chat_prefix(self):
        vm = SimpleNamespace(words={"drop": object()}, host={"repl_mode": "forth"})
        completer = _f_mod.ForthWordCompleter(vm)
        event = CompleteEvent(completion_requested=True)

        vm.words["dynamic"] = object()
        self.assertEqual(
            [c.text for c in completer.get_completions(Document("dyn"), event)],
            ["dynamic"],
        )
        self.assertEqual(list(completer.get_completions(Document(""), event)), [])
        self.assertEqual(list(completer.get_completions(Document(" "), event)), [])
        vm.host["repl_mode"] = "chat"
        self.assertEqual(list(completer.get_completions(Document("dyn"), event)), [])

    def test_completer_accepts_forth_word_names_with_special_characters(self):
        names = [".", ".s", "[if]", "ai:", "py:"]
        vm = SimpleNamespace(words={name: object() for name in names}, host={})
        completer = _f_mod.ForthWordCompleter(vm)
        event = CompleteEvent(completion_requested=True)

        for name in names:
            with self.subTest(name=name):
                self.assertIn(
                    name,
                    [c.text for c in completer.get_completions(Document(name[:1]), event)],
                )

    def test_arrows_select_and_space_accepts_candidate_with_trailing_space(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", "\t", "\x1b[C", " ", "\r"], vm)

        self.assertEqual(actual, "duplicate ")

    def test_right_arrow_moves_horizontally_to_next_column(self):
        names = [f"w{index:02}" for index in range(30)]
        vm = SimpleNamespace(
            words={name: object() for name in names},
            host={"repl_mode": "forth"},
        )
        transcript = io.StringIO()
        output = Vt100_Output(
            transcript, lambda: Size(rows=12, columns=80),
            term="xterm-256color", enable_cpr=False,
        )

        actual = self.run_prompt(["w", chr(9), "\x1b[C", " ", chr(13)], vm, output=output)

        self.assertEqual(actual, "w02 ")

    def test_down_at_bottom_of_column_does_not_jump_to_next_column(self):
        names = [f"w{index:02}" for index in range(30)]
        vm = SimpleNamespace(
            words={name: object() for name in names},
            host={"repl_mode": "forth"},
        )
        output = Vt100_Output(
            io.StringIO(), lambda: Size(rows=12, columns=80),
            term="xterm-256color", enable_cpr=False,
        )

        actual = self.run_prompt(
            ["w", chr(9), "\x1b[B", "\x1b[B", "\x1b[B", " ", chr(13)],
            vm, output=output,
        )

        self.assertEqual(actual, "w01 ")

    def test_left_arrow_moves_horizontally_to_previous_column(self):
        names = [f"w{index:02}" for index in range(12)]
        vm = SimpleNamespace(
            words={name: object() for name in names},
            host={"repl_mode": "forth"},
        )
        output = Vt100_Output(
            io.StringIO(), lambda: Size(rows=12, columns=80),
            term="xterm-256color", enable_cpr=False,
        )

        actual = self.run_prompt(
            ["w", chr(9), "\x1b[C", "\x1b[D", " ", chr(13)],
            vm, output=output,
        )

        self.assertEqual(actual, "w00 ")

    def test_up_at_top_of_column_does_not_deselect_or_change_column(self):
        names = [f"w{index:02}" for index in range(12)]
        vm = SimpleNamespace(
            words={name: object() for name in names},
            host={"repl_mode": "forth"},
        )
        output = Vt100_Output(
            io.StringIO(), lambda: Size(rows=12, columns=80),
            term="xterm-256color", enable_cpr=False,
        )

        actual = self.run_prompt(["w", chr(9), "\x1b[A", " ", chr(13)], vm, output=output)

        self.assertEqual(actual, "w00 ")

    def test_completion_items_show_arrow_navigation_hint(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )
        completions = list(_f_mod.ForthWordCompleter(vm).get_completions(
            Document(text="du"), CompleteEvent(completion_requested=True)))

        self.assertEqual(len(completions), 2)
        expected_hint = "\u2191 \u2193 \u2190 \u2192 move | Space selects | Esc cancels"
        self.assertEqual(
            {completion.display_meta_text for completion in completions},
            {expected_hint},
        )

    def test_space_confirms_a_single_candidate(self):
        vm = SimpleNamespace(words={"dup": object()}, host={"repl_mode": "forth"})

        actual = self.run_prompt(["du", "\t", " ", "\r"], vm)

        self.assertEqual(actual, "dup ")

    def test_tab_renders_all_matches_in_a_multicolumn_menu(self):
        vm = SimpleNamespace(
            words={"duplicate": object(), "duplex": object(), "dupe": object()},
            host={"repl_mode": "forth"},
        )
        transcript = io.StringIO()
        output = Vt100_Output(
            transcript, lambda: Size(rows=20, columns=80),
            term="xterm-256color", enable_cpr=False,
        )

        self.run_prompt(["du", "\t", "\x1b", "x", "\r"], vm, output=output)

        rendered = transcript.getvalue()
        for candidate in vm.words:
            with self.subTest(candidate=candidate):
                self.assertIn(candidate, rendered)

    def test_escape_cancels_preview_and_restores_the_original_token(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", "\t", "\x1b[B", "\x1b", "x", "\r"], vm)

        self.assertEqual(actual, "dux")

    def test_enter_does_not_commit_an_unconfirmed_completion(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", chr(9), chr(13)], vm)

        self.assertEqual(actual, "du")

    def test_typing_while_menu_open_discards_preview_before_inserting(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", chr(9), "x", chr(13)], vm)

        self.assertEqual(actual, "dux")

    def test_backspace_while_menu_open_edits_the_original_token(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", chr(9), chr(127), chr(13)], vm)

        self.assertEqual(actual, "d")

    def test_delete_while_menu_open_edits_the_original_token(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", "\x1b[D", chr(9), chr(4), chr(13)], vm)

        self.assertEqual(actual, "d")

    def test_multiline_newline_does_not_commit_completion_preview(self):
        vm = SimpleNamespace(
            words={"dup": object(), "duplicate": object()},
            host={"repl_mode": "forth"},
        )

        actual = self.run_prompt(["du", chr(9), chr(10), "x", chr(13)], vm)

        self.assertEqual(actual, "du\nx")

    def test_tab_with_no_candidate_keeps_the_input_unchanged(self):
        vm = SimpleNamespace(words={"dup": object()}, host={"repl_mode": "forth"})

        actual = self.run_prompt(["zzz", chr(9), chr(13)], vm)

        self.assertEqual(actual, "zzz")

    def test_control_c_still_interrupts_with_completion_menu_open(self):
        vm = SimpleNamespace(words={"dup": object()}, host={"repl_mode": "forth"})

        with self.assertRaises(KeyboardInterrupt):
            self.run_prompt(["du", chr(9), chr(3), chr(13)], vm)

    def test_space_without_menu_remains_an_ordinary_input_character(self):
        vm = SimpleNamespace(words={"dup": object()}, host={"repl_mode": "forth"})

        actual = self.run_prompt(["x", " ", "y", "\r"], vm)

        self.assertEqual(actual, "x y")


class ReplBootstrapTests(unittest.TestCase):
    def setUp(self):
        self._diagnostics_patch = patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"})
        self._diagnostics_patch.start()
        self.addCleanup(self._diagnostics_patch.stop)
        self.vm = _f_mod.create_vm()

    def test_diagnostic_log_mode_defaults_to_normal_and_accepts_verbose(self):
        with patch.dict(os.environ):
            os.environ.pop("PEFORTH_AI_LOG_MODE", None)
            self.assertEqual(_f_mod._diagnostic_log_mode(), "normal")
            os.environ["PEFORTH_AI_LOG_MODE"] = "verbose"
            self.assertEqual(_f_mod._diagnostic_log_mode(), "verbose")

    def test_create_vm_starts_diagnostic_runtime_in_normal_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {
                    "PEFORTH_AI_LOG_MODE": "normal",
                    "PEFORTH_CONFIG_DIR": directory,
            }), patch.object(_f_mod.ai_bridge, "load_dotenv"), \
                    patch.object(_f_mod, "_detect_system_info", return_value={"config": {"PEFORTH_AI_MODEL": ""}, "wsl": {"active": True}}), \
                    patch.object(_f_mod.atexit, "register") as register_exit:
                vm = _f_mod.create_vm()

            logger = vm.host["diagnostic_log"]
            runtime_id = vm.host["diagnostic_runtime_id"]
            self.assertEqual(vm.host["diagnostic_log_mode"], "normal")
            self.assertIsInstance(logger, DiagnosticLog)
            self.assertEqual(logger.connection.execute(
                "SELECT environment FROM runtimes WHERE runtime_id = ?", (runtime_id,)
            ).fetchone()[0], "windows" if os.name == "nt" else "wsl")
            self.assertEqual(vm.host["system_info"]["config"]["PEFORTH_AI_LOG_MODE"], "normal")
            register_exit.assert_called_once_with(_f_mod._close_diagnostic_log, logger, runtime_id)
            _f_mod._close_diagnostic_log(logger, runtime_id)
            connection = sqlite3.connect(pathlib.Path(directory) / "ai-diagnostics.sqlite3")
            try:
                self.assertIsNotNone(connection.execute(
                    "SELECT finished_at FROM runtimes WHERE runtime_id = ?", (runtime_id,)
                ).fetchone()[0])
            finally:
                connection.close()

    def test_create_vm_disables_diagnostics_without_creating_database(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {
                    "PEFORTH_AI_LOG_MODE": "disabled",
                    "PEFORTH_CONFIG_DIR": directory,
            }), patch.object(_f_mod.ai_bridge, "load_dotenv"), \
                    patch.object(_f_mod, "_detect_system_info", return_value={"config": {"PEFORTH_AI_MODEL": ""}, "wsl": {"active": True}}):
                vm = _f_mod.create_vm()

            self.assertEqual(vm.host["diagnostic_log_mode"], "disabled")
            self.assertNotIn("diagnostic_log", vm.host)
            self.assertFalse((pathlib.Path(directory) / "ai-diagnostics.sqlite3").exists())

    def test_forth_sources_are_loaded_from_f_package(self):
        self.assertEqual(_f_mod.FORTH_SOURCE_ROOT.name, "f")
        self.assertEqual(_f_mod.BASE_F_PATH.name, "base.f")
        self.assertEqual(_f_mod.AI_F_PATH.name, "ai.f")
        self.assertEqual(_f_mod.AUXILIARY_F_PATH.name, "auxiliary.f")
        package_dir = pathlib.Path(_f_mod.__file__).resolve().parent
        self.assertFalse((package_dir / "base.f").exists())
        self.assertFalse((package_dir / "ai.f").exists())
        self.assertFalse((package_dir / "auxiliary.f").exists())

    def test_question_dup_is_loaded_from_bootstrap(self):
        self.vm.dictate("0 ?dup 1 ?dup")
        self.assertEqual(self.vm.stack, [0, 1, 1])

    def test_auxiliary_stringify_is_defined_directly_in_forth_source(self):
        stringify = self.vm.tick("stringify")
        self.assertIsNotNone(stringify)
        self.assertIn("json.dumps", stringify.source)

        self.vm.push({"answer": [42]})
        self.vm.dictate("stringify")
        self.assertEqual(self.vm.pop(), '{\n  "answer": [\n    42\n  ]\n}')

        self.vm.push("{'answer': 42}")
        self.vm.dictate("stringify")
        self.assertEqual(self.vm.pop(), '{\n  "answer": 42\n}')

    def test_cls_is_defined_directly_in_forth_source_and_clears_terminal(self):
        cls = self.vm.tick("cls")
        self.assertIn("print(\"\\x1b[2J\\x1b[H\"", cls.source)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.vm.dictate("cls")
        self.assertEqual(output.getvalue(), "\x1b[2J\x1b[H")

    def test_bracket_conditionals_select_arms_and_handle_nested_skips(self):
        self.vm.dictate("1 [if] 11 [else] 22 [then]")
        self.vm.dictate("0 [if] 33 [else] 44 [then]")
        self.assertEqual(self.vm.stack, [11, 44])

        # The skipped outer arm contains a nested conditional; its [else] must
        # not be mistaken for the outer [else].
        self.vm.dictate("0 [if] 1 [if] 55 [else] 66 [then] [else] 77 [then]")
        self.assertEqual(self.vm.pop(), 77)

    def test_bracket_conditional_skip_ignores_markers_in_strings_and_comments(self):
        source = ('0 [if] s" [else] [then]" // [else] [then]'
                  + chr(10) + '42 [else] 99 [then]')
        self.vm.dictate(source)
        # [else] belongs to the skipped outer arm; the comment consumes the
        # remainder of that physical line, including the following [then].
        self.assertEqual(self.vm.stack, [99])

    def test_bracket_conditionals_report_unmatched_groups(self):
        with self.assertRaisesRegex(ForthError, "Unmatched conditional"):
            self.vm.dictate("0 [if] 1")

    def test_bracket_until_and_again_rewind_interpretation_input(self):
        self.vm.dictate("0 [begin] 1+ dup 3 >= [until]")
        self.assertEqual(self.vm.stack, [3])

        self.vm.dictate("0 [begin] 1+ dup 3 < [if] [again] [then]")
        self.assertEqual(self.vm.stack, [3, 3])

    def test_bracket_for_next_counts_nested_and_zero_iteration_case(self):
        self.vm.dictate("0 3 [for] 1+ [next]")
        self.vm.dictate("0 0 [for] 1+ [next]")
        self.vm.dictate("0 2 [for] 2 [for] 1+ [next] [next]")
        self.assertEqual(self.vm.stack, [3, 1, 4])

    def test_bracket_interpretation_loops_reject_compilation_mode(self):
        for source in (": bad-begin [begin] ;", ": bad-until [until] ;",
                       ": bad-for [for] ;", ": bad-next [next] ;"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ForthError, "only be used while interpreting"):
                    self.vm.dictate(source)

        # Each failed dictate task cleans up its own interpretation T-stack.
        self.vm.dictate("1 [if] 2 [then]")
        self.assertEqual(self.vm.stack, [2])

    def test_ai_local_control_words_are_defined_and_work_from_ai_f(self):
        for name in ("ai-new", "ai-status", "ai-confirm", "ai-trust-runtime"):
            self.assertIsNotNone(self.vm.tick(name))
            self.assertTrue(self.vm.tick(name).source.strip())
        self.assertIn('pop("ai_active_session_id"', self.vm.tick("ai-new").source)
        self.assertIn("ai_active_session_id", self.vm.tick("ai-status").source)
        self.assertIn('pop("ai_trusted"', self.vm.tick("ai-confirm").source)

        bridge = _f_mod.ai_bridge
        other_vm = _f_mod.create_vm()
        self.vm.host["ai_active_session_id"] = "sess_current_12345678"
        other_vm.host["ai_active_session_id"] = "sess_other_abcdefgh"
        detail = {"id": "sess_current_12345678", "created_at": 1791466592,
                  "last_active_at": 1791470192, "status": "idle",
                  "agent": {"model": "gpt-test"},
                  "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}}
        with patch.object(bridge, "_session_titles", return_value={"sess_current_12345678": "peforth"}):
            with patch.object(bridge, "_api_get", return_value=detail) as api_get:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.vm.dictate("ai-status")
                self.assertIn("Session current: peforth [sess_current_12345678]", output.getvalue())
                self.assertIn("Status: idle", output.getvalue())
                self.assertIn("Model: gpt-test", output.getvalue())
                self.assertIn("Usage: input=1 output=2 total=3 tokens", output.getvalue())
                api_get.assert_called_once_with("/sessions/sess_current_12345678")

            with contextlib.redirect_stdout(io.StringIO()):
                self.vm.dictate("ai-new")
            self.assertNotIn("ai_active_session_id", self.vm.host)
            self.assertEqual(other_vm.host["ai_active_session_id"], "sess_other_abcdefgh")

            self.vm.host["ai_session_rows"] = [{"id": "sess_selected_87654321"}]
            with patch.object(bridge, "_api_get", return_value={}), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.vm.dictate("1 ai-use")
            self.assertEqual(self.vm.host["ai_active_session_id"], "sess_selected_87654321")
            self.assertEqual(other_vm.host["ai_active_session_id"], "sess_other_abcdefgh")

        remote = [{"id": "sess_selected_abcdefgh"}]
        with patch.object(bridge, "_list_remote_sessions", return_value=remote), \
                patch.object(bridge, "_api_get", return_value={}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.vm.dictate('s" abcdefgh" ai-use')
        self.assertEqual(self.vm.host["ai_active_session_id"], "sess_selected_abcdefgh")

    def test_ai_use_prints_full_session_id(self):
        bridge = _f_mod.ai_bridge
        session_id = "sess_selected_abcdefgh"
        output = io.StringIO()
        with patch.object(bridge, "_list_remote_sessions", return_value=[{"id": session_id}]), \
                patch.object(bridge, "_api_get", return_value={}), \
                contextlib.redirect_stdout(output):
            self.vm.push(session_id)
            self.vm.execute(self.vm.tick("ai-use"))
        self.assertEqual(self.vm.host["ai_active_session_id"], session_id)
        self.assertIn(f"[{session_id}]", output.getvalue())

    def test_ai_session_and_cleanup_still_accept_session_numbers(self):
        bridge = _f_mod.ai_bridge
        session_id = "sess_number_12345678"
        self.vm.host["ai_session_rows"] = [{"id": session_id}]
        detail = {"id": session_id, "created_at": 1791466592,
                  "last_active_at": 1791470192, "status": "idle",
                  "agent": {"model": "gpt-test"}, "usage": {}}
        with patch.object(bridge, "_api_get", return_value=detail) as api_get:
            self.vm.push(1)
            self.vm.execute(self.vm.tick("ai-session"))
        api_get.assert_called_once_with("/sessions/sess_number_12345678")

        self.vm.host["ai_session_rows"] = [{"id": session_id}]
        with patch.object(bridge, "_api_delete", return_value={"deleted": True}) as api_delete:
            self.vm.push(1)
            self.vm.execute(self.vm.tick("ai-cleanup"))
        api_delete.assert_called_once_with("/sessions/sess_number_12345678")

    def test_ai_session_and_cleanup_accept_full_session_ids(self):
        bridge = _f_mod.ai_bridge
        session_id = "sess_full_12345678"
        self.vm.host.pop("ai_session_rows", None)
        detail = {"id": session_id, "created_at": 1791466592,
                  "last_active_at": 1791470192, "status": "idle",
                  "agent": {"model": "gpt-test"}, "usage": {}}
        output = io.StringIO()
        with patch.object(bridge, "_list_remote_sessions", return_value=[{"id": session_id}]) as list_sessions:
            with patch.object(bridge, "_sync_session_index", return_value={session_id: "Design"}):
                with patch.object(bridge, "_api_get", return_value=detail) as api_get:
                    with contextlib.redirect_stdout(output):
                        self.vm.push(session_id)
                        self.vm.execute(self.vm.tick("ai-session"))
        list_sessions.assert_called_once_with()
        api_get.assert_called_once_with("/sessions/sess_full_12345678")
        self.assertIn("[sess_full_12345678]", output.getvalue())

        self.vm.host["ai_session_rows"] = [{"id": session_id}]
        self.vm.host["ai_session_titles"] = {session_id: "Design"}
        output = io.StringIO()
        with patch.object(bridge, "_api_delete", return_value={"deleted": True}) as api_delete:
            with contextlib.redirect_stdout(output):
                self.vm.push(session_id)
                self.vm.execute(self.vm.tick("ai-cleanup"))
        api_delete.assert_called_once_with("/sessions/sess_full_12345678")
        self.assertIn("sess_full_12345678", output.getvalue())
        self.assertNotIn("ai_session_rows", self.vm.host)

    def test_bye_refreshes_session_index_and_prints_resume_command(self):
        bridge = _f_mod.ai_bridge
        self.vm.host["ai_active_session_id"] = "sess_current_12345678"
        output = io.StringIO()
        with patch.object(bridge, "refresh_session_index") as refresh, \
                patch.object(bridge, "_session_title", return_value="peforth"), \
                contextlib.redirect_stdout(output):
            _f_mod._farewell(self.vm)
        refresh.assert_called_once_with(self.vm)
        self.assertIn('To resume it in a future Forth run, enter: s" sess_current_12345678" ai-use', output.getvalue())

        self.vm.host["ai_trusted"] = True
        with contextlib.redirect_stdout(io.StringIO()):
            self.vm.dictate("ai-confirm")
        self.assertNotIn("ai_trusted", self.vm.host)

    def test_session_files_follow_config_dir(self):
        bridge = _f_mod.ai_bridge
        with tempfile.TemporaryDirectory() as directory:
            config_dir = pathlib.Path(directory) / "user config"
            with patch.dict("os.environ", {"PEFORTH_CONFIG_DIR": str(config_dir)}), \
                patch.object(bridge, "SESSION_FILE", config_dir / ".ai_session.json"):
                bridge._write_session_index([{"id": "sess_config", "title": "Local"}])
                self.assertEqual(
                    json.loads((config_dir / ".ai_session.json").read_text(encoding="utf-8")),
                    {"sessions": [{"id": "sess_config", "title": "Local"}]},
                )
                self.assertEqual(bridge._session_titles(), {"sess_config": "Local"})

    def test_session_title_reader_ignores_legacy_fields(self):
        bridge = _f_mod.ai_bridge
        original = '{"active_session_id":"legacy","sessions":[{"id":"sess_1","title":"Design","last_used_at":"old"}]}'

        class ReadOnlyFile:
            name = ".ai_session.json"

            def read_text(self, encoding=None):
                return original

        session_file = ReadOnlyFile()
        with patch.object(bridge, "SESSION_FILE", session_file):
            self.assertEqual(bridge._session_titles(), {"sess_1": "Design"})
            self.assertEqual(session_file.read_text(encoding="utf-8"), original)

    def test_ai_sessions_display_title_cloud_times_and_full_id(self):
        bridge = _f_mod.ai_bridge
        remote = [{"id": "sess_full_12345678", "created_at": 1791466592,
                   "last_active_at": 1791470192, "status": "idle",
                   "agent": {"model": "gpt-test"}, "environment": {"type": "none"}}]
        saved = []
        with patch.object(bridge, "_list_remote_sessions", return_value=remote), \
                patch.object(bridge, "_session_titles", return_value={"sess_full_12345678": "Design chat"}), \
                patch.object(bridge, "_write_session_index", side_effect=lambda rows: saved.extend(rows)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.vm.dictate("ai-sessions")
        rendered = output.getvalue()
        self.assertIn("Design chat [sess_full_12345678]", rendered)
        self.assertIn("Started:", rendered)
        self.assertIn("Last active:", rendered)
        self.assertEqual(saved, [{"id": "sess_full_12345678", "title": "Design chat"}])

    def test_agent_tool_names_are_peforth_branded_and_package_skill_is_found(self):
        import json
        from peforth import ai_bridge

        vm = _f_mod.create_vm()
        captured = {}

        def create_session(payload, *, diagnostic=None):
            captured.update(payload)
            return iter([
                {"type": "agent.session.created", "session": {"id": "sess_new_12345678"}},
                {"type": "agent.session.turn.output_text.done", "text": "ok"},
                {"type": "agent.session.turn.completed"},
            ])

        with patch.object(ai_bridge, "_create_session", side_effect=create_session), \
                patch.object(ai_bridge, "_saved_session", return_value=None), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.dict("os.environ", {"OPENAI_API_KEY": "test-only"}):
            vm.push("hello")
            vm.push(False)
            vm.execute(vm.tick("(ai)"))

        functions = captured["agent"]["tools"]
        self.assertEqual([tool["name"] for tool in functions],
                         ["peforth_search_words", "peforth_tick_heartbeat", "peforth_run_forth"])
        instructions = captured["agent"]["instructions"]
        self.assertIn("peforth Forth", instructions)
        self.assertNotIn("Project K", instructions)
        self.assertIn("Trust this AI task", instructions)
        self.assertIn("ai-trust-runtime", instructions)
        inventory_text = instructions.split("## Runtime capability inventory\n", 1)[1]
        inventory = json.loads(inventory_text)
        self.assertEqual(
            inventory["host"]["runtime_latest"],
            _f_mod._latest_runtime_file_info(pathlib.Path(_f_mod.__file__).resolve().parent),
        )
        self.assertEqual(inventory["host"]["runtime_path"], str(pathlib.Path(_f_mod.__file__).resolve().parent))
        self.assertNotIn("source_latest", inventory["host"])
        self.assertNotIn("runtime_source_path", inventory["host"])
        self.assertEqual(captured["environment"], {"type": "none"})
        self.assertTrue(captured["stream"])

    def test_ai_words_have_visible_source_and_help(self):
        ai_line = self.vm.tick("ai:")
        self.assertIsNotNone(ai_line)
        self.assertIsInstance(ai_line.action, tuple)
        self.assertTrue(any(getattr(word, "name", None) == "word" for word in ai_line.action))
        self.assertIn("remaining input", ai_line.help)
        self.assertIn("Trust", ai_line.comment)
        self.assertIsNone(self.vm.tick("(ai-line)"))

        ai_stack = self.vm.tick("(ai)")
        self.assertIn("prompt-string stream?", ai_stack.help)
        self.assertIn("Trust/Yes/No/Cancel approval flow", ai_stack.comment)

    def test_ai_workflow_words_are_defined_in_ai_f(self):
        for name in ("ai-sessions", "ai-session", "ai-use", "ai-cleanup",
                     "ai-cancel", "(ai)",
                     "(ai-context)", "system_info", "run_pwsh", "run_bash",
                     "run_curl", "run_http"):
            word = self.vm.tick(name)
            self.assertIsNotNone(word, name)
            self.assertTrue(
                word.source.strip()
                or isinstance(word.action, tuple),
                name,
            )

    def test_latest_runtime_file_info_uses_newest_f_or_py_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            older = root / "projectk.py"
            newest = root / "f" / "auxiliary.f"
            ignored = root / "notes.txt"
            newest.parent.mkdir()
            older.write_text("# old", encoding="utf-8")
            newest.write_text("\\ newest", encoding="utf-8")
            ignored.write_text("ignore", encoding="utf-8")
            os.utime(older, (100, 100))
            os.utime(newest, (200, 200))

            info = _f_mod._latest_runtime_file_info(root)

        self.assertEqual(info["file"], "f/auxiliary.f")
        self.assertEqual(info["modified"], datetime.fromtimestamp(200).strftime("%Y-%m-%d %H:%M:%S"))

    def test_latest_runtime_file_info_is_unavailable_when_no_runtime_files_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            info = _f_mod._latest_runtime_file_info(pathlib.Path(directory))
        self.assertIsNone(info)

    def test_repl_greeting_fragments_include_runtime_and_command_hints(self):
        info = {"runtime_latest": {"file": "f/auxiliary.f", "modified": "2026-10-12 23:37:29"}}
        fragments = _f_mod._greeting_fragments(info)
        self.assertEqual(
            "".join(text for _style, text in fragments),
            "\np e f o r t h   v 2\nForth REPL · Runtime modified: 2026-10-12 23:37:29"
            "\n\nEnter submits / Ctrl+J or Esc then Enter adds a line.\n"
            "chat  AI chat / forth  Forth mode / bye or Ctrl-D  Exit",
        )
        self.assertEqual(fragments[0][0], "class:greeting.title")
        self.assertEqual(_f_mod._greeting_fragments({})[0][1], "\np e f o r t h   v 2")

    def test_reported_source_path_expands_windows_userprofile_placeholder(self):
        configured = r"%USERPROFILE%\OneDrive\Documents\GitHub\peforth"
        userprofile = r"C:\Users\TestUser"
        with patch.dict("os.environ", {
            "PEFORTH_SOURCE_PATH": configured,
            "USERPROFILE": userprofile,
        }):
            self.assertEqual(
                _f_mod._reported_source_path(),
                userprofile + r"\OneDrive\Documents\GitHub\peforth",
            )

    def test_detect_system_info_includes_runtime_metadata(self):
        latest = {"file": "f/auxiliary.f", "modified": "2026-10-12 23:37:29"}
        repo_path = r"C:\Users\8304018\OneDrive\Documents\GitHub\peforth"
        with patch.dict("os.environ", {"PEFORTH_SOURCE_PATH": repo_path, "PEFORTH_CACHE_TTL": "0"}):
            with patch.object(_f_mod, "_latest_runtime_file_info", return_value=latest):
                with patch.object(_f_mod, "_program_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        detected = _f_mod._detect_system_info()
        self.assertEqual(detected["source_path"], repo_path)
        self.assertEqual(detected["config"]["PEFORTH_SOURCE_PATH"], repo_path)
        self.assertEqual(detected["runtime_latest"], latest)
        self.assertEqual(detected["runtime_path"], str(pathlib.Path(_f_mod.__file__).resolve().parent))
        self.assertNotIn("source_latest", detected)
        self.assertNotIn("runtime_source_path", detected)

    def _detect_wsl_system_info(self, env, program_info):
        fake_os = SimpleNamespace(name="posix", environ=os.environ, path=os.path)
        with patch.dict(os.environ, {"WSL_DISTRO_NAME": "Ubuntu", "PEFORTH_CACHE_TTL": "0", **env}):
            with patch.object(_f_mod, "os", fake_os):
                with patch.object(_f_mod, "_program_info", side_effect=program_info):
                    return _f_mod._detect_system_info()

    def test_wsl_system_info_prefers_detected_windows_pwsh_exe(self):
        detected_path = "/mnt/c/Program Files/PowerShell/7/pwsh.exe"
        configured_path = "/custom/pwsh.exe"
        calls = []

        def program_info(name, _version_args):
            calls.append(name)
            if name == "pwsh.exe":
                return {"available": True, "path": detected_path, "version": "7.6.7"}
            return {"available": False, "path": None, "version": None}

        detected = self._detect_wsl_system_info(
            {"PEFORTH_PWSH_PATH": configured_path}, program_info)
        pwsh = detected["shells"]["pwsh"]

        self.assertEqual(pwsh, {
            "available": True,
            "path": detected_path,
            "version": "7.6.7",
            "execution_host": "windows",
            "source": "path",
        })
        self.assertEqual(detected["config"]["PEFORTH_PWSH_PATH"], configured_path)
        self.assertIn("pwsh.exe", calls)
        self.assertNotIn("pwsh", calls)

    def test_wsl_system_info_uses_env_pwsh_path_when_detection_fails(self):
        configured_path = "/custom/pwsh.exe"
        calls = []

        def program_info(name, _version_args):
            calls.append(name)
            if name == configured_path:
                return {"available": True, "path": configured_path, "version": "7.6.7"}
            return {"available": False, "path": None, "version": None}

        detected = self._detect_wsl_system_info(
            {"PEFORTH_PWSH_PATH": configured_path}, program_info)
        pwsh = detected["shells"]["pwsh"]

        self.assertEqual(pwsh, {
            "available": True,
            "path": configured_path,
            "version": "7.6.7",
            "execution_host": "windows",
            "source": "env",
        })
        self.assertEqual(calls[:2], ["pwsh.exe", configured_path])
        self.assertEqual(detected["config"]["PEFORTH_PWSH_PATH"], configured_path)

    def test_system_info_word_uses_runtime_binding_and_host_commands(self):
        from peforth import ai_tools

        info = {
            "os": "Windows",
            "shells": {
                "pwsh": {"available": True, "path": "pwsh.exe"},
                "bash": {"available": True, "path": "bash"},
                "curl": {"available": True, "path": "curl.exe"},
            },
            "wsl": {"available": True, "path": "wsl.exe", "distro": "Ubuntu"},
        }
        result = {"exit_code": 0, "stdout": "ok", "stderr": "", "timed_out": False, "truncated": False}
        self.vm.host["system_info"] = info
        with patch.object(ai_tools, "_run_process", return_value=result) as run_process:
            self.vm.dictate("system_info system_info")
            self.assertIs(self.vm.pop(), info)
            self.assertIs(self.vm.pop(), info)

            self.vm.push("Write-Output ok")
            self.vm.dictate("run_pwsh")
            self.assertEqual(self.vm.pop(), result)
            run_process.assert_called_with(
                ["pwsh.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "-"],
                input_text="Write-Output ok")

            self.vm.push("echo ok")
            self.vm.dictate("run_bash")
            self.assertEqual(self.vm.pop(), result)
            run_process.assert_called_with(
                ["wsl.exe", "-d", "Ubuntu", "--exec", "bash", "--noprofile", "--norc", "-s"],
                input_text="echo ok")

            self.vm.push(["-sS", "https://example.test"])
            self.vm.dictate("run_curl")
            self.assertEqual(self.vm.pop(), result)
            run_process.assert_called_with(["curl.exe", "-sS", "https://example.test"])

    def test_ai_model_value_is_initialized_from_system_info_and_can_change(self):
        info = {"config": {"PEFORTH_AI_MODEL": "gpt-6-luna"}}
        with patch.object(_f_mod.ai_bridge, "load_dotenv"):
            with patch.object(_f_mod, "_detect_system_info", return_value=info) as detect:
                vm = _f_mod.create_vm()
        detect.assert_called_once_with()
        vm.dictate("aiModel")
        self.assertEqual(vm.pop(), "gpt-6-luna")
        vm.dictate('s" gpt-6-mini" to aiModel aiModel')
        self.assertEqual(vm.pop(), "gpt-6-mini")

    def test_ai_model_uses_luna_when_config_is_empty(self):
        with patch.object(_f_mod.ai_bridge, "load_dotenv"):
            with patch.object(_f_mod, "_detect_system_info", return_value={"config": {"PEFORTH_AI_MODEL": ""}}):
                vm = _f_mod.create_vm()
        vm.dictate("aiModel")
        self.assertEqual(vm.pop(), "gpt-6-luna")

    def test_run_http_word_validates_in_forth_and_uses_python_transport(self):
        from peforth import ai_tools

        response = {"status_code": 200, "headers": {}, "body": "ok", "truncated": False}
        with patch.object(ai_tools, "_http_request", return_value=response) as request:
            self.vm.push({"url": "https://example.test", "method": "post",
                          "headers": {"Content-Type": "text/plain"}, "body": "hello"})
            self.vm.dictate("run_http")
            self.assertEqual(self.vm.pop(), response)
            request.assert_called_once_with("https://example.test", "POST",
                                            {"Content-Type": "text/plain"}, "hello")

            self.vm.push({"url": "file:///etc/passwd"})
            self.vm.dictate("run_http")
            self.assertIn("only supports absolute http:// or https://",
                          self.vm.pop()["error"])
            request.assert_called_once()

    def test_ai_context_returns_chat_or_complete_items(self):
        bridge = _f_mod.ai_bridge
        context_word = self.vm.tick("ai-context")
        self.assertIsInstance(context_word.action, tuple)
        action_names = [getattr(operation, "name", None) for operation in context_word.action]
        self.assertIn("BL", action_names)
        self.assertIn("int", action_names)
        self.vm.host["ai_session_rows"] = [{"id": "sess_1"}]
        items = [
            {"id": "item_1", "type": "message", "role": "user",
             "content": [{"type": "input_text", "text": "Hello"}]},
            {"id": "item_2", "type": "function_call", "name": "peforth_words"},
            {"id": "item_3", "type": "message", "role": "assistant",
             "content": [{"type": "output_text", "text": "Hi there."}]},
        ]
        api_page = {"data": list(reversed(items)), "has_more": False, "last_id": "item_1"}
        with patch.object(bridge, "_api_get", return_value=api_page):
            self.vm.dictate("ai-context 1 5")
            self.assertEqual(self.vm.pop(), [
                {"role": "user", "text": "Hello"},
                {"role": "assistant", "text": "Hi there."},
            ])

            self.vm.dictate("ai-context 1 5 chat")
            self.assertEqual(self.vm.pop(), [
                {"role": "user", "text": "Hello"},
                {"role": "assistant", "text": "Hi there."},
            ])

            self.vm.dictate("ai-context 1 5 json")
            self.assertEqual(self.vm.pop(), items)

        self.assertIsNone(self.vm.tick("ai-transcript"))
        self.assertIsNone(self.vm.tick("ai-items"))

    def test_ai_context_fetches_only_recent_turn_pages(self):
        bridge = _f_mod.ai_bridge
        pages = [
            {"data": [
                {"id": "a3", "type": "message", "role": "assistant"},
                {"id": "u3", "type": "message", "role": "user"},
                {"id": "tool3", "type": "function_call"},
                {"id": "a2", "type": "message", "role": "assistant"},
            ], "has_more": True, "last_id": "a2"},
            {"data": [
                {"id": "u2", "type": "message", "role": "user"},
                {"id": "a1", "type": "message", "role": "assistant"},
                {"id": "u1", "type": "message", "role": "user"},
            ], "has_more": False, "last_id": "u1"},
        ]
        requests = []

        def api_get(path):
            requests.append(path)
            return pages.pop(0)

        self.vm.host["ai_session_rows"] = [{"id": "sess_1"}]
        with patch.object(bridge, "_api_get", side_effect=api_get):
            self.vm.dictate("ai-context 1 2 json")
            recent = self.vm.pop()

        self.assertEqual([item["id"] for item in recent], ["u2", "a2", "tool3", "u3", "a3"])
        self.assertEqual(len(requests), 2)
        self.assertIn("order=desc", requests[0])
        self.assertIn("limit=4", requests[0])

    def test_word_uses_falsy_delimiters_for_all_remaining_input(self):
        for delimiter in (None, "", False, 0):
            self.vm.push(delimiter)
            self.vm.dictate("word remaining\nlines")
            self.assertEqual(self.vm.pop(), " remaining\nlines")

        self.vm.dictate("BL word first")
        self.assertEqual(self.vm.pop(), "first")

    def test_int_and_float_convert_values_on_the_stack(self):
        self.vm.push("42")
        self.vm.dictate("int")
        self.assertEqual(self.vm.pop(), 42)

        self.vm.push("3.125")
        self.vm.dictate("float")
        self.assertEqual(self.vm.pop(), 3.125)

    def test_python_value_words_and_peforth_aliases(self):
        self.vm.dictate("none None")
        self.assertIsNone(self.vm.pop())
        self.assertIsNone(self.vm.pop())

        self.vm.dictate("true True false False")
        self.assertIs(self.vm.pop(), False)
        self.assertIs(self.vm.pop(), False)
        self.assertIs(self.vm.pop(), True)
        self.assertIs(self.vm.pop(), True)

        self.vm.dictate('""')
        self.assertEqual(self.vm.pop(), "")

        self.vm.dictate("inf infinity -inf -infinity nan")
        self.assertTrue(math.isnan(self.vm.pop()))
        self.assertEqual(self.vm.pop(), float("-inf"))
        self.assertEqual(self.vm.pop(), float("-inf"))
        self.assertEqual(self.vm.pop(), float("inf"))
        self.assertEqual(self.vm.pop(), float("inf"))

    def test_alias_defines_an_alias_for_a_colon_word(self):
        self.vm.dictate(": original 17 ; ' original alias original-alias original-alias")
        self.assertEqual(self.vm.pop(), 17)
        self.assertEqual(self.vm.tick("original-alias").type, "alias")

    def test_multiline_editor_submission_runs_as_one_forth_buffer(self):
        state = {"in_code_block": False, "code_buffer": [], "ai_task": None}
        with contextlib.redirect_stdout(io.StringIO()):
            _f_mod._process_one_line(self.vm, ": square\n dup *\n;\n5 square", state)
        self.assertEqual(self.vm.pop(), 25)

    def test_multiline_ai_prompt_is_preserved_as_one_message(self):
        self.vm.host["repl_mode"] = "chat"
        state = {"in_code_block": False, "code_buffer": [], "ai_task": None}
        received = []

        def fake_create(payload, *, diagnostic=None):
            received.append(payload["input"])
            yield {"type": "agent.session.created", "session": {"id": "sess_new"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "First line.\nSecond line."}
            yield {"type": "agent.session.turn.output_text.done", "text": "First line.\nSecond line."}
            yield {"type": "agent.session.turn.completed"}

        with patch.object(_f_mod.ai_bridge, "_create_session", side_effect=fake_create):
            with contextlib.redirect_stdout(io.StringIO()):
                _f_mod._process_repl_input(self.vm, "First line.\nSecond line.", state)

        self.assertEqual(received, ["First line.\nSecond line."])

    def test_repl_mode_commands_switch_between_chat_and_forth(self):
        state = {"in_code_block": False, "code_buffer": [], "ai_task": None}
        self.assertIsNotNone(self.vm.tick("chat"))
        self.assertIsNotNone(self.vm.tick("forth"))
        with contextlib.redirect_stdout(io.StringIO()):
            _f_mod._process_repl_input(self.vm, "chat", state)
        self.assertEqual(self.vm.host["repl_mode"], "chat")
        with contextlib.redirect_stdout(io.StringIO()):
            _f_mod._process_repl_input(self.vm, "forth", state)
        self.assertEqual(self.vm.host["repl_mode"], "forth")

    def test_cli_execute_joins_every_remaining_argument_as_tib(self):
        class RecordingVM:
            def __init__(self):
                self.sources = []

            def dictate(self, source):
                self.sources.append(source)

        vm = RecordingVM()
        with patch.object(_f_mod, "create_vm", return_value=vm), \
                patch.object(_f_mod, "repl") as interactive_repl:
            result = _f_mod.main(["-e", "1", "2", "+", ".", "-i"])
        self.assertEqual(result, 0)
        self.assertEqual(vm.sources, ["1 2 + . -i"])
        interactive_repl.assert_not_called()

    def test_cli_repeated_load_options_run_files_in_order_before_execute(self):
        with tempfile.TemporaryDirectory() as directory:
            first = pathlib.Path(directory) / "first.f"
            second = pathlib.Path(directory) / "second.f"
            first.write_text(": loaded-first 40 ;", encoding="utf-8")
            second.write_text(": loaded-second loaded-first 2 + ;", encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = _f_mod.main([
                    "-l", str(first), "--load", str(second),
                    "-e", "loaded-second", ".",
                ])

        self.assertEqual(result, 0)
        self.assertIn("42", output.getvalue())

    def test_cli_interactive_option_runs_after_execute(self):
        class RecordingVM:
            def __init__(self):
                self.sources = []
                self.host = {"one_shot": True}

            def dictate(self, source):
                self.sources.append(source)

        vm = RecordingVM()
        with patch.object(_f_mod, "create_vm", return_value=vm), \
                patch.object(_f_mod, "repl") as interactive_repl:
            result = _f_mod.main(["-i", "-e", "1", "2", "+", "."])
        self.assertEqual(result, 0)
        self.assertEqual(vm.sources, ["1 2 + ."])
        interactive_repl.assert_called_once_with(vm)

    def test_cli_chat_defaults_to_new_session_and_returns_id_on_stderr(self):
        class RecordingVM:
            def __init__(self):
                self.host = {}
                self.stack = []
                self.task = object()
                self.executed = None

            def push(self, value):
                self.stack.append(value)

            def tick(self, name):
                return name

            def execute(self, word):
                self.executed = (word, self.stack[:])
                self.stack.clear()
                self.host["ai_active_session_id"] = "sess_created_here"
                return self.task

        vm = RecordingVM()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(_f_mod, "create_vm", return_value=vm), \
                patch.object(_f_mod.ai_bridge, "_list_remote_sessions") as list_sessions, \
                patch.object(_f_mod, "repl") as interactive_repl, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = _f_mod.main(["--chat", "Hello", "from", "CLI"])
        self.assertEqual(result, 0)
        self.assertEqual(vm.executed, ("(ai)", ["Hello from CLI", True]))
        self.assertEqual(vm.host["repl_mode"], "chat")
        self.assertFalse(vm.host["ai_transport_stream_once"])
        list_sessions.assert_not_called()
        self.assertNotIn("SESSION_ID=", stdout.getvalue())
        self.assertIn("SESSION_ID=sess_created_here", stderr.getvalue())
        interactive_repl.assert_called_once_with(
            vm, initial_task=vm.task, exit_when_idle=True, show_greeting=False)

    def test_cli_chat_with_id_continues_only_the_explicit_session(self):
        class RecordingVM:
            def __init__(self):
                self.host = {}
                self.stack = []
                self.task = object()
                self.executed = None

            def push(self, value):
                self.stack.append(value)

            def tick(self, name):
                return name

            def execute(self, word):
                self.executed = (word, self.stack[:])
                self.stack.clear()
                return self.task

        vm = RecordingVM()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(_f_mod, "create_vm", return_value=vm), \
                patch.object(_f_mod.ai_bridge, "_list_remote_sessions") as list_sessions, \
                patch.object(_f_mod, "repl") as interactive_repl, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = _f_mod.main(["-c", "Hello", "from", "CLI", "-id", "sess_explicit"])
        self.assertEqual(result, 0)
        self.assertEqual(vm.executed, ("(ai)", ["Hello from CLI", True]))
        self.assertEqual(vm.host["ai_active_session_id"], "sess_explicit")
        self.assertFalse(vm.host["ai_transport_stream_once"])
        list_sessions.assert_not_called()
        self.assertNotIn("SESSION_ID=", stdout.getvalue())
        self.assertIn("SESSION_ID=sess_explicit", stderr.getvalue())
        interactive_repl.assert_called_once_with(
            vm, initial_task=vm.task, exit_when_idle=True, show_greeting=False)

    def test_cli_id_requires_value_and_can_select_repl_without_chat(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = _f_mod.main(["-id"])
        self.assertEqual(result, 2)
        self.assertIn("-id requires a session ID", stderr.getvalue())

        vm = SimpleNamespace(host={})
        with patch.object(_f_mod, "create_vm", return_value=vm):
            with patch.object(_f_mod, "repl") as interactive_repl:
                result = _f_mod.main(["-id", "sess_explicit"])
        self.assertEqual(result, 0)
        self.assertEqual(vm.host["ai_active_session_id"], "sess_explicit")
        interactive_repl.assert_called_once_with(vm)

    def test_cli_new_option_is_removed(self):
        stderr = io.StringIO()
        with patch.object(_f_mod, "create_vm") as create_vm, \
                patch.object(_f_mod, "repl"), contextlib.redirect_stderr(stderr):
            result = _f_mod.main(["-new", "-c", "Hello"])
        self.assertEqual(result, 2)
        self.assertIn("Unknown option: -new", stderr.getvalue())
        create_vm.assert_not_called()


    def test_cli_chat_interactive_flag_must_precede_prompt(self):
        class RecordingVM:
            def __init__(self):
                self.host = {}
                self.stack = []
                self.task = object()
                self.executed = None

            def push(self, value):
                self.stack.append(value)

            def tick(self, name):
                return name

            def execute(self, word):
                self.executed = (word, self.stack[:])
                self.stack.clear()
                return self.task

        vm = RecordingVM()
        with patch.object(_f_mod, "create_vm", return_value=vm), \
                patch.object(_f_mod.ai_bridge, "_list_remote_sessions", return_value=[]), \
                patch.object(_f_mod, "repl") as interactive_repl:
            result = _f_mod.main(["-i", "-c", "Hello", "there"])
        self.assertEqual(result, 0)
        self.assertEqual(vm.executed, ("(ai)", ["Hello there", True]))
        interactive_repl.assert_called_once_with(
            vm, initial_task=vm.task, exit_when_idle=False, show_greeting=False)

    def test_cli_chat_without_id_skips_session_lookup(self):
        class RecordingVM:
            def __init__(self):
                self.host = {}
                self.stack = []
                self.task = object()

            def push(self, value):
                self.stack.append(value)

            def tick(self, name):
                return name

            def execute(self, word):
                self.executed = (word, self.stack[:])
                self.stack.clear()
                return self.task

        vm = RecordingVM()
        with patch.object(_f_mod, "create_vm", return_value=vm), \
                patch.object(_f_mod.ai_bridge, "_list_remote_sessions") as list_sessions, \
                patch.object(_f_mod, "repl") as interactive_repl:
            result = _f_mod.main(["-c", "A", "fresh", "chat"])
        self.assertEqual(result, 0)
        self.assertEqual(vm.executed, ("(ai)", ["A fresh chat", True]))
        self.assertNotIn("ai_active_session_id", vm.host)
        list_sessions.assert_not_called()
        interactive_repl.assert_called_once_with(
            vm, initial_task=vm.task, exit_when_idle=True, show_greeting=False)

    def test_one_shot_chat_exits_without_repl_greeting_or_farewell(self):
        session_options = {}

        class QuietPromptSession:
            def __init__(self, **kwargs):
                session_options.update(kwargs)

        class CompletedTask:
            status = "done"

        output = io.StringIO()
        _f_mod._load_prompt_toolkit()
        with patch.object(_f_mod, "PromptSession", QuietPromptSession), \
                patch.object(_f_mod, "_make_multiline_key_bindings", return_value=None), \
                patch.object(_f_mod.ai_bridge, "refresh_session_index") as refresh, \
                patch.object(_f_mod, "_farewell") as farewell, \
                contextlib.redirect_stdout(output):
            _f_mod.repl(self.vm, initial_task=CompletedTask(), exit_when_idle=True,
                        show_greeting=False)
        self.assertEqual(output.getvalue(), "")
        self.assertIsInstance(session_options["completer"], _f_mod.ForthWordCompleter)
        self.assertFalse(session_options["complete_while_typing"])
        self.assertIs(session_options["complete_style"], CompleteStyle.MULTI_COLUMN)
        self.assertIsNotNone(session_options["key_bindings"])
        refresh.assert_called_once_with(self.vm)
        farewell.assert_not_called()

    def test_cli_help_is_available(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = _f_mod.main(["-h"])
        self.assertEqual(result, 0)
        self.assertIn("-e <Forth tokens...>", output.getvalue())
        self.assertIn("-i, --interactive", output.getvalue())
        self.assertIn("-id <session-id>", output.getvalue())
        self.assertIn("Continue the conversation in this session", output.getvalue())
        self.assertIn("-l, --load <path>", output.getvalue())
        self.assertIn("may be repeated; before -e or -c", output.getvalue())
        self.assertNotIn("may appear anywhere", output.getvalue())
        self.assertIn("SESSION_ID=<session-id>", output.getvalue())
        self.assertNotIn("-new", output.getvalue())

    def test_http_request_records_lifecycle_timing_and_request_ids(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=508)
            turn_id = logger.start_turn(runtime_id)
            diagnostic = {
                "logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                "mode": "normal",
            }

            class FakeResponse:
                status = 201
                headers = {"x-request-id": "provider-123"}
                closed = False

                def close(self):
                    self.closed = True

            response = FakeResponse()
            with patch.object(ai_bridge, "load_dotenv"), \
                    patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), \
                    patch.object(ai_bridge.urllib.request, "urlopen", return_value=response):
                result = ai_bridge._request(
                    "POST", "/sessions", {"input": "hello"}, stream=True,
                    diagnostic=diagnostic, operation="create_session",
                )
                result.close()

            rows = logger.connection.execute(
                "SELECT event_type, operation, http_method, url, http_status, "
                "local_request_id, provider_request_id, elapsed_ms "
                "FROM timeline WHERE turn_id = ? ORDER BY event_id", (turn_id,),
            ).fetchall()
            self.assertEqual([row[0] for row in rows], [
                "http_request_started", "sse_open_started", "http_response_received",
                "sse_opened", "http_request_closed",
            ])
            self.assertTrue(all(row[1] == "create_session" for row in rows))
            self.assertTrue(all(row[2] == "POST" and row[3] == "/sessions" for row in rows))
            self.assertEqual(rows[2][4:7], (201, rows[0][5], "provider-123"))
            self.assertGreaterEqual(rows[-1][7], 0)
            self.assertTrue(response.closed)
            logger.close()

    def test_http_error_records_response_payload_and_closure(self):
        from email.message import Message
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=509)
            turn_id = logger.start_turn(runtime_id)
            diagnostic = {
                "logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                "mode": "verbose",
            }
            headers = Message()
            headers["x-request-id"] = "provider-error-1"
            headers["Set-Cookie"] = "secret-cookie"
            http_error = ai_bridge.urllib.error.HTTPError(
                "https://api.example/sessions", 400, "Bad Request",
                headers,
                io.BytesIO(b'{"error":"bad request"}'),
            )
            with patch.object(ai_bridge, "load_dotenv"), \
                    patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), \
                    patch.object(ai_bridge.urllib.request, "urlopen", side_effect=http_error):
                with self.assertRaisesRegex(RuntimeError, "Agents API HTTP 400"):
                    ai_bridge._request(
                        "POST", "/sessions", {"input": "hello"},
                        diagnostic=diagnostic, operation="create_session",
                    )

            rows = logger.connection.execute(
                "SELECT event_type, content_id, payload_json, http_status, "
                "provider_request_id FROM timeline WHERE turn_id = ? ORDER BY event_id",
                (turn_id,),
            ).fetchall()
            self.assertEqual([row[0] for row in rows], [
                "http_request_started", "http_response_received", "http_response_payload",
                "http_request_failed", "http_request_closed",
            ])
            self.assertEqual(rows[1][3:], (400, "provider-error-1"))
            self.assertEqual(rows[4][3:], (400, "provider-error-1"))
            self.assertEqual(logger.connection.execute(
                "SELECT content_text FROM contents WHERE content_id = ?",
                (rows[2][1],),
            ).fetchone()[0], '{"error":"bad request"}')
            response_headers = json.loads(rows[1][2])["response_headers"]
            self.assertEqual(response_headers["Set-Cookie"], "[REDACTED]")
            logger.close()

    def test_verbose_http_request_persists_payloads_with_secret_redaction(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=505)
            turn_id = logger.start_turn(runtime_id)
            diagnostic = {
                "logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                "mode": "verbose",
            }

            class FakeResponse:
                status = 200
                headers = {"x-request-id": "provider-read-1"}
                closed = False

                def read(self, size=-1):
                    return b'{"result":"ok"}'

                def close(self):
                    self.closed = True

            response = FakeResponse()
            with patch.object(ai_bridge, "load_dotenv"), \
                    patch.dict(os.environ, {"OPENAI_API_KEY": "do-not-log"}), \
                    patch.object(ai_bridge.urllib.request, "urlopen", return_value=response):
                logged = ai_bridge._request(
                    "POST", "/inspect", {"prompt": "hello"},
                    diagnostic=diagnostic, operation="inspect",
                )
                self.assertEqual(logged.read(), b'{"result":"ok"}')
                logged.close()

            rows = logger.connection.execute(
                "SELECT event_type, content_id, payload_json FROM timeline "
                "WHERE turn_id = ? ORDER BY event_id", (turn_id,),
            ).fetchall()
            request_event = next(row for row in rows if row[0] == "http_request_started")
            started = json.loads(request_event[2])
            self.assertEqual(started["request_payload_content_id"], request_event[1])
            self.assertEqual(logger.connection.execute(
                "SELECT content_text FROM contents WHERE content_id = ?",
                (request_event[1],),
            ).fetchone()[0], '{"prompt": "hello"}')
            self.assertEqual(started["request_headers"]["Authorization"], "[REDACTED]")
            body_event = next(row for row in rows if row[0] == "http_response_payload")
            self.assertEqual(logger.connection.execute(
                "SELECT content_text FROM contents WHERE content_id = ?", (body_event[1],)
            ).fetchone()[0], '{"result":"ok"}')
            self.assertNotIn("do-not-log", repr([row[2] for row in rows]))
            logger.close()

    def test_sse_stream_records_timing_and_respects_logging_mode(self):
        from peforth import ai_bridge

        raw_lines = [
            b'data: {"type":"agent.session.turn.output_text.delta","delta":"Hi"}\n',
            b"\n", b": keepalive\n", b"\n", b"data: [DONE]\n", b"\n",
        ]

        class FakeResponse:
            def __init__(self):
                self.closed = False

            def __iter__(self):
                return iter(raw_lines)

            def close(self):
                self.closed = True

        for mode in ("normal", "verbose"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
                runtime_id = logger.start_runtime(process_id=507)
                turn_id = logger.start_turn(runtime_id)
                diagnostic = {
                    "logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                    "mode": mode,
                }
                response = FakeResponse()
                events = list(ai_bridge._event_stream(
                    response, diagnostic=diagnostic, operation="create_session",
                ))

                self.assertEqual(events, [{"type": "agent.session.turn.output_text.delta", "delta": "Hi"}])
                rows = logger.connection.execute(
                    "SELECT event_type, content_id, payload_json FROM timeline "
                    "WHERE turn_id = ? ORDER BY event_id", (turn_id,),
                ).fetchall()
                event_types = [row[0] for row in rows]
                self.assertIn("sse_event_received", event_types)
                self.assertIn("sse_heartbeat_received", event_types)
                self.assertIn("sse_done_received", event_types)
                self.assertIn("sse_stream_ended", event_types)
                self.assertIn("sse_stream_closed", event_types)
                delta = next(json.loads(row[2]) for row in rows
                             if row[0] == "sse_event_received")
                self.assertEqual((delta["delta_length"], delta["output_length"]), (2, 2))
                self.assertEqual("delta" in delta, mode == "verbose")
                line_rows = [row for row in rows if row[0] == "sse_line_received"]
                self.assertEqual(bool(line_rows), mode == "verbose")
                if line_rows:
                    self.assertIsNotNone(line_rows[0][1])
                    raw_line = logger.connection.execute(
                        "SELECT content_text FROM contents WHERE content_id = ?",
                        (line_rows[0][1],),
                    ).fetchone()[0]
                    self.assertIn('"delta":"Hi"', raw_line)
                self.assertTrue(response.closed)
                logger.close()

    def test_live_ai_turn_wires_http_and_sse_diagnostics(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=506)
            self.vm.host["diagnostic_log"] = logger
            self.vm.host["diagnostic_runtime_id"] = runtime_id
            self.vm.host["diagnostic_log_mode"] = "normal"
            stream_events = [
                {"type": "agent.session.created", "session": {"id": "sess_live"}},
                {"type": "agent.session.turn.output_text.delta", "delta": "Hello"},
                {"type": "agent.session.turn.output_text.done", "text": "Hello"},
                {"type": "agent.session.turn.completed"},
            ]
            raw_lines = []
            for event in stream_events:
                raw_lines.extend((b"data: " + json.dumps(event).encode() + b"\n", b"\n"))

            class FakeResponse:
                status = 201
                headers = {"x-request-id": "live-provider-req"}

                def __init__(self):
                    self.closed = False

                def __iter__(self):
                    return iter(raw_lines)

                def close(self):
                    self.closed = True

            response = FakeResponse()
            with patch.object(ai_bridge, "load_dotenv"), \
                    patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                    patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), \
                    patch.object(ai_bridge.urllib.request, "urlopen", return_value=response), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.vm.push("Say hello")
                self.vm.push(False)
                self.vm.dictate("(ai)")

            turn = logger.connection.execute(
                "SELECT turn_id, remote_session_id, status FROM turns"
            ).fetchone()
            self.assertEqual(tuple(turn[1:]), ("sess_live", "completed"))
            rows = logger.connection.execute(
                "SELECT event_type, session_id, http_method, url, http_status, "
                "provider_request_id, payload_json FROM timeline WHERE turn_id = ? ORDER BY event_id",
                (turn[0],),
            ).fetchall()
            event_types = [row[0] for row in rows]
            self.assertIn("http_request_started", event_types)
            self.assertIn("sse_opened", event_types)
            self.assertIn("sse_event_received", event_types)
            self.assertIn("sse_stream_closed", event_types)
            self.assertEqual(next(row[5] for row in rows if row[0] == "http_response_received"),
                             "live-provider-req")
            session_event = next(row for row in rows if row[0] == "sse_event_received")
            self.assertEqual(session_event[1], "sess_live")
            http_closed = next(row for row in rows if row[0] == "http_request_closed")
            self.assertEqual(http_closed[1], "sess_live")
            self.assertFalse(any(row[0] == "sse_line_received" for row in rows))
            self.assertTrue(response.closed)
            logger.close()

    def test_current_actions_response_and_payload_are_recorded(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=507)
            turn_id = logger.start_turn(runtime_id, remote_session_id="sess_actions")
            diagnostic = {"logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                          "session_id": "sess_actions", "mode": "normal"}
            response = {"status": "in_progress", "required_actions": [
                {"turn_id": "remote-actions", "call_id": "call-actions",
                 "name": "peforth_run_forth", "arguments": {"source": "42 ."}}
            ]}
            with patch.object(ai_bridge, "_api_get", return_value=response):
                status, actions = ai_bridge._current_actions("sess_actions", diagnostic=diagnostic)

            self.assertEqual(status, "in_progress")
            self.assertEqual(actions[0]["call_id"], "call-actions")
            rows = logger.connection.execute(
                "SELECT event_type, operation, payload_json, content_id FROM timeline "
                "WHERE turn_id = ? ORDER BY event_id", (turn_id,)
            ).fetchall()
            self.assertEqual([row[0] for row in rows], [
                "current_actions_request_started", "current_actions_response_received",
                "current_actions_payload",
            ])
            self.assertEqual(json.loads(rows[1][2])["status"], "in_progress")
            self.assertEqual(rows[2][1], "get_current_actions")
            self.assertIn("call-actions", logger.connection.execute(
                "SELECT content_text FROM contents WHERE content_id = ?", (rows[2][3],)
            ).fetchone()[0])
            logger.close()

    def test_tool_result_submission_failure_is_recorded_without_masking_error(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=508)
            turn_id = logger.start_turn(runtime_id)
            diagnostic = {"logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                          "session_id": "sess_failure", "mode": "normal"}
            action = {"turn_id": "remote-tool-fail", "call_id": "call-fail",
                      "name": "peforth_search_words"}
            with patch.object(ai_bridge, "_request", side_effect=OSError("network down")):
                with self.assertRaisesRegex(OSError, "network down"):
                    ai_bridge._tool_result(
                        "sess_failure", action, True, "tool output", diagnostic=diagnostic
                    )
            event = logger.connection.execute(
                "SELECT event_type, call_id, error_type, error_message, content_id "
                "FROM timeline WHERE turn_id = ?", (turn_id,)
            ).fetchone()
            self.assertEqual(tuple(event[:4]), (
                "tool_result_submit_failed", "call-fail", "OSError", "network down"
            ))
            self.assertEqual(logger.connection.execute(
                "SELECT content_type, content_text FROM contents WHERE content_id = ?",
                (event[4],),
            ).fetchone()[1], "tool output")
            logger.close()

    def test_ai_tool_call_records_arguments_execution_and_result(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=509)
            self.vm.host["diagnostic_log"] = logger
            self.vm.host["diagnostic_runtime_id"] = runtime_id
            action = {
                "turn_id": "remote-turn-tool",
                "call_id": "call-search-1",
                "name": "peforth_search_words",
                "arguments": {"query": "dup"},
            }

            class FakeResponse:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def read(self):
                    return b"{}"

            def fake_create(payload, *, diagnostic=None):
                yield {"type": "agent.session.created", "session": {"id": "sess_tool"}}
                yield {"type": "agent.session.requires_action", "call_id": "call-search-1",
                       "turn_id": "remote-turn-tool"}
                yield {"type": "agent.session.turn.output_text.delta", "delta": "Done"}
                yield {"type": "agent.session.turn.output_text.done", "text": "Done"}
                yield {"type": "agent.session.turn.completed"}

            with (patch.object(ai_bridge, "_create_session", side_effect=fake_create),
                  patch.object(ai_bridge, "_current_actions", return_value=("requires_action", [action])),
                  patch.object(ai_bridge, "_request", return_value=FakeResponse()),
                  patch.object(ai_bridge, "_agent_instructions", return_value="instructions"),
                  patch.object(ai_bridge, "load_dotenv"),
                  contextlib.redirect_stdout(io.StringIO())):
                self.vm.push("Search dup")
                self.vm.push(False)
                self.vm.dictate("(ai)")

            turn_id = logger.connection.execute("SELECT turn_id FROM turns").fetchone()[0]
            rows = logger.connection.execute(
                "SELECT event_type, call_id, content_id, payload_json FROM timeline "
                "WHERE turn_id = ? ORDER BY event_id", (turn_id,)
            ).fetchall()
            by_type = {row[0]: row for row in rows}
            for event_type in ("tool_call_received", "tool_call_arguments_parsed",
                               "tool_call_started", "tool_call_completed", "tool_result_submitted"):
                self.assertIn(event_type, by_type)
                self.assertEqual(by_type[event_type][1], "call-search-1")
            arguments_id = by_type["tool_call_arguments_parsed"][2]
            arguments = logger.connection.execute(
                "SELECT content_type, content_text FROM contents WHERE content_id = ?",
                (arguments_id,),
            ).fetchone()
            self.assertEqual(tuple(arguments), ("tool_arguments", '{"query": "dup"}'))
            result_id = by_type["tool_result_submitted"][2]
            result = logger.connection.execute(
                "SELECT content_type, content_text FROM contents WHERE content_id = ?",
                (result_id,),
            ).fetchone()
            self.assertEqual(result[0], "tool_result")
            self.assertIn('"name": "dup"', result[1])
            logger.close()

    def test_forth_execution_result_normalizes_surrogate_pairs(self):
        from peforth import ai_bridge

        surrogate_pair = "\ud83d\ude00"

        class SurrogateRepr:
            def __repr__(self):
                return "stack:" + ("x" * 16774) + surrogate_pair

        class FakeVM:
            def __init__(self):
                self.stack = [SurrogateRepr()]

            def dictate(self, _source):
                print(("x" * 73) + surrogate_pair)
                return SimpleNamespace(status="done")

        execution = ai_bridge._run(FakeVM(), "ignored")
        result = json.loads(execution)

        result["stdout"].encode("utf-8")
        result["stack"].encode("utf-8")
        execution.encode("utf-8")
        self.assertEqual(result["stdout"], ("x" * 73) + "😀\n")
        self.assertIn("😀", result["stack"])
        self.assertEqual(ai_bridge._normalize_surrogates("left\ud800right\udc00"), "left�right�")
        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            logger.store_content("forth_stdout", result["stdout"])
            logger.store_content("forth_stack", result["stack"])
            logger.close()


    def test_ai_approval_and_local_forth_execution_are_logged(self):
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=510)
            self.vm.host["diagnostic_log"] = logger
            self.vm.host["diagnostic_runtime_id"] = runtime_id
            action = {
                "turn_id": "remote-turn-forth",
                "call_id": "call-forth-1",
                "name": "peforth_run_forth",
                "arguments": {"source": "42 . cr", "purpose": "print a test value"},
            }

            class FakeResponse:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def read(self):
                    return b"{}"

            def fake_create(payload, *, diagnostic=None):
                yield {"type": "agent.session.created", "session": {"id": "sess_approval"}}
                yield {"type": "agent.session.requires_action", "call_id": "call-forth-1",
                       "turn_id": "remote-turn-forth"}
                yield {"type": "agent.session.turn.output_text.delta", "delta": "Done"}
                yield {"type": "agent.session.turn.output_text.done", "text": "Done"}
                yield {"type": "agent.session.turn.completed"}

            with (patch.object(ai_bridge, "_create_session", side_effect=fake_create),
                  patch.object(ai_bridge, "_current_actions", side_effect=[
                      ("requires_action", [action]), ("requires_action", [action])
                  ]),
                  patch.object(ai_bridge, "_request", return_value=FakeResponse()),
                  patch.object(ai_bridge, "_agent_instructions", return_value="instructions"),
                  patch.object(ai_bridge, "load_dotenv"),
                  contextlib.redirect_stdout(io.StringIO())):
                self.vm.push("Run local code")
                self.vm.push(False)
                task = self.vm.dictate("(ai)")
                self.assertEqual(task.status, "paused")
                self.vm.host.pop("ai_pending_approval")
                self.vm.host["ai_approval_result"] = True
                task.resume()
                self.assertEqual(task.status, "done")

            turn_id = logger.connection.execute("SELECT turn_id FROM turns").fetchone()[0]
            rows = logger.connection.execute(
                "SELECT event_type, call_id, content_id, elapsed_ms, payload_json "
                "FROM timeline WHERE turn_id = ? ORDER BY event_id", (turn_id,)
            ).fetchall()
            by_type = {row[0]: row for row in rows}
            for event_type in ("approval_requested", "approval_wait_started",
                               "approval_decision_received", "approval_wait_ended",
                               "forth_execution_started", "forth_execution_completed"):
                self.assertIn(event_type, by_type)
                self.assertEqual(by_type[event_type][1], "call-forth-1")
            self.assertIsNotNone(by_type["approval_wait_ended"][3])
            source = logger.connection.execute(
                "SELECT content_type, content_text FROM contents WHERE content_id = ?",
                (by_type["forth_execution_started"][2],),
            ).fetchone()
            self.assertEqual(tuple(source), ("forth_source", "42 . cr"))
            stdout_id = json.loads(by_type["forth_execution_completed"][4])["stdout_content_id"]
            stdout = logger.connection.execute(
                "SELECT content_type, content_text FROM contents WHERE content_id = ?",
                (stdout_id,),
            ).fetchone()
            self.assertEqual(tuple(stdout), ("forth_stdout", "42\n"))
            logger.close()

    def test_ai_approval_cancel_records_event_and_wait_duration(self):
        import time
        from peforth import ai_bridge

        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=511)
            turn_id = logger.start_turn(runtime_id)
            context = {"logger": logger, "runtime_id": runtime_id, "turn_id": turn_id,
                       "session_id": "sess_cancel", "mode": "normal"}
            action = {"turn_id": "remote-cancel", "call_id": "call-cancel",
                      "name": "peforth_run_forth"}
            pending = {"action": action, "diagnostic_context": context,
                       "approval_started_ns": time.monotonic_ns() - 2_000_000,
                       "source_content_id": logger.store_content("forth_source", "42 .")}

            ai_bridge._diagnostic_cancel_approval(pending, reason="user_cancel")

            events = logger.connection.execute(
                "SELECT event_type, elapsed_ms, payload_json FROM timeline "
                "WHERE turn_id = ? ORDER BY event_id", (turn_id,)
            ).fetchall()
            self.assertEqual([row[0] for row in events],
                             ["approval_cancelled", "approval_wait_ended"])
            self.assertGreaterEqual(events[1][1], 0)
            self.assertIn('"decision": "cancelled"', events[1][2])
            logger.close()

    def test_ai_turn_renders_same_cards_in_forth_and_chat_modes(self):
        def fake_create(payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess_ui"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Hello"}
            yield {"type": "agent.session.turn.output_text.done", "text": "Hello"}
            yield {"type": "agent.session.turn.completed"}

        for mode in ("forth", "chat"):
            with self.subTest(mode=mode):
                vm = _f_mod.create_vm()
                vm.host["repl_mode"] = mode
                output = io.StringIO()
                with patch.object(_f_mod.ai_bridge, "_create_session", side_effect=fake_create), \
                        patch.object(_f_mod.ai_bridge, "_agent_instructions", return_value="instructions"), \
                        patch.object(_f_mod.ai_bridge, "load_dotenv"), \
                        contextlib.redirect_stdout(output):
                    vm.push("Say hello")
                    vm.push(True)
                    vm.dictate("(ai)")

                rendered = output.getvalue()
                self.assertIn(chr(0x1F44B) + " user", rendered)
                self.assertIn(chr(0x1FA84) + " peforth", rendered)
                self.assertIn("  Hello", rendered)
                self.assertNotIn(chr(0x1F916), rendered)
                self.assertLess(rendered.index(chr(0x1F44B)), rendered.index(chr(0x1FA84)))

    def test_ai_turn_records_prompt_and_completed_output(self):
        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=509)
            self.vm.host["diagnostic_log"] = logger
            self.vm.host["diagnostic_runtime_id"] = runtime_id
            self.vm.host["ai_transport_stream_once"] = False
            captured = {}

            def fake_create(payload, *, diagnostic=None, stream=True):
                captured.update(payload=payload, stream=stream)
                yield {"type": "agent.session.created", "session": {"id": "sess_diag"}}
                yield {"type": "agent.session.turn.output_text.delta", "delta": "Hello"}
                yield {"type": "agent.session.turn.output_text.done", "text": "Hello"}
                yield {"type": "agent.session.turn.completed"}

            with patch.object(_f_mod.ai_bridge, "_create_session", side_effect=fake_create), \
                    patch.object(_f_mod.ai_bridge, "_agent_instructions", return_value="instructions"), \
                    patch.object(_f_mod.ai_bridge, "load_dotenv"), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.vm.push("Say hello")
                self.vm.push(False)
                self.vm.dictate("(ai)")

            turn = logger.connection.execute(
                "SELECT turn_id, prompt_content_id, instructions_content_id, output_content_id, "
                "remote_session_id, status, output_status FROM turns"
            ).fetchone()
            self.assertEqual((turn[4], turn[5], turn[6]), ("sess_diag", "completed", "complete"))
            self.assertEqual(self.vm.host["ai_active_session_id"], "sess_diag")
            self.assertFalse(captured["payload"]["stream"])
            self.assertFalse(captured["stream"])
            started_payload = logger.connection.execute(
                "SELECT payload_json FROM timeline WHERE turn_id = ? AND event_type = ?",
                (turn[0], "ai_turn_started"),
            ).fetchone()[0]
            self.assertEqual(json.loads(started_payload), {
                "one_shot": False,
                "repl_mode": "forth",
                "terminal_output_stream": False,
                "api_transport_stream": False,
            })
            expected_content = ((turn[1], "Say hello"), (turn[2], "instructions"), (turn[3], "Hello"))
            for content_id, expected_text in expected_content:
                actual_text = logger.connection.execute(
                    "SELECT content_text FROM contents WHERE content_id = ?", (content_id,)
                ).fetchone()[0]
                if expected_text == "instructions":
                    self.assertTrue(actual_text.startswith("instructions\n\n## Runtime capability inventory"))
                else:
                    self.assertEqual(actual_text, expected_text)
            event_types = [row[0] for row in logger.connection.execute(
                "SELECT event_type FROM timeline WHERE turn_id = ? ORDER BY event_id", (turn[0],)
            )]
            self.assertIn("ai_turn_started", event_types)
            self.assertIn("ai_session_created", event_types)
            self.assertIn("ai_turn_completed", event_types)
            logger.close()

    def test_ai_turn_failure_preserves_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            logger = DiagnosticLog(pathlib.Path(directory) / "diagnostics.sqlite3", environment="wsl")
            runtime_id = logger.start_runtime(process_id=510)
            self.vm.host["diagnostic_log"] = logger
            self.vm.host["diagnostic_runtime_id"] = runtime_id

            def fake_create(payload, *, diagnostic=None):
                yield {"type": "agent.session.created", "session": {"id": "sess_partial"}}
                yield {"type": "agent.session.turn.output_text.delta", "delta": "Part"}
                raise RuntimeError("stream broke")

            with patch.object(_f_mod.ai_bridge, "_create_session", side_effect=fake_create), \
                    patch.object(_f_mod.ai_bridge, "_agent_instructions", return_value="instructions"), \
                    patch.object(_f_mod.ai_bridge, "load_dotenv"), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.vm.push("Say something")
                self.vm.push(False)
                with self.assertRaisesRegex(ForthError, "stream broke"):
                    self.vm.dictate("(ai)")

            turn = logger.connection.execute(
                "SELECT output_content_id, status, output_status, error_type "
                "FROM turns"
            ).fetchone()
            self.assertEqual(tuple(turn[1:]), ("failed", "partial", "RuntimeError"))
            self.assertEqual(logger.connection.execute(
                "SELECT content_text FROM contents WHERE content_id = ?", (turn[0],)
            ).fetchone()[0], "Part")
            logger.close()

    def test_diagnostic_failure_does_not_replace_ai_error(self):
        class FailingDiagnosticLog:
            def store_content(self, *args, **kwargs):
                raise OSError("disk full")

        self.vm.host["diagnostic_log"] = FailingDiagnosticLog()
        self.vm.host["diagnostic_runtime_id"] = "runtime-test"

        def fake_create(payload, *, diagnostic=None):
            yield {"type": "agent.session.created", "session": {"id": "sess_error"}}
            raise RuntimeError("Agents API failed")

        with patch.object(_f_mod.ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(_f_mod.ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(_f_mod.ai_bridge, "load_dotenv"), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.vm.push("Say hello")
            self.vm.push(False)
            with self.assertRaisesRegex(ForthError, "Agents API failed"):
                self.vm.dictate("(ai)")

    def test_stack_ai_word_returns_assistant_text(self):
        def fake_create(payload, *, diagnostic=None):
            yield {"type": "agent.session.created", "session": {"id": "sess_stack"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Hello"}
            yield {"type": "agent.session.turn.output_text.done", "text": "Hello"}
            yield {"type": "agent.session.turn.completed"}

        with patch.object(_f_mod.ai_bridge, "_create_session", side_effect=fake_create), \
                contextlib.redirect_stdout(io.StringIO()):
            self.vm.push("Say hello")
            self.vm.push(False)
            self.vm.dictate("(ai)")
        self.assertEqual(self.vm.pop(), "Hello")

    def test_multiline_key_bindings_submit_and_insert_newlines(self):
        class RecordingBindings:
            def __init__(self):
                self.handlers = {}

            def add(self, *keys):
                def register(handler):
                    self.handlers[keys] = handler
                    return handler
                return register

        bindings = _f_mod._make_multiline_key_bindings(RecordingBindings)

        class Buffer:
            def __init__(self):
                self.inserted = []
                self.submitted = False

            def insert_text(self, text):
                self.inserted.append(text)

            def validate_and_handle(self):
                self.submitted = True

        class Event:
            def __init__(self):
                self.current_buffer = Buffer()

        enter = Event()
        bindings.handlers[("c-m",)](enter)
        self.assertTrue(enter.current_buffer.submitted)

        for keys in (("c-j",), ("escape", "c-m")):
            event = Event()
            bindings.handlers[keys](event)
            self.assertEqual(event.current_buffer.inserted, ["\n"])

    def test_modified_enter_sequences_map_to_newline(self):
        sequences = {}
        _f_mod._map_extended_enter_sequences(sequences, "c-j")
        self.assertEqual(sequences["\x1b[27;2;13~"], "c-j")
        self.assertEqual(sequences["\x1b[13;2u"], "c-j")

    def test_help_and_comment(self):
        self.vm.dictate(': hi s" Hello!" . ; // ( -- ) Greeting\n/// Line 1\n/// Line 2\n')
        word = self.vm.tick('hi')
        self.assertEqual(word.help, '( -- ) Greeting')
        self.assertEqual(word.comment, 'Line 1\nLine 2\n')

    def test_help_and_comment_inside_colon_definition(self):
        prev_word = self.vm.last()
        self.vm.dictate(': greeting // a greeting\n/// Note 1\ns" hello world!" . ;\n')
        word = self.vm.tick('greeting')
        self.assertEqual(word.help, 'a greeting')
        self.assertEqual(word.comment, 'Note 1\n')
        self.assertNotEqual(prev_word.help, 'a greeting')

    def test_last_word(self):
        self.vm.dictate(': sample 42 . ; last')
        w = self.vm.pop()
        self.assertEqual(w.name, 'sample')

    def test_last_execute_runs_the_most_recent_definition(self):
        self.vm.dictate(': sample 41 1 + ; last execute')
        self.assertEqual(self.vm.pop(), 42)

    def test_colon_colon_and_colon_greater(self):
        self.vm.dictate(": hi s\" Hello!\" . ; s\" Custom\" ' hi :: help=pop(1)")
        word = self.vm.tick('hi')
        self.assertEqual(word.help, 'Custom')
        self.vm.dictate("' hi :> help")
        self.assertEqual(self.vm.pop(), 'Custom')
        self.vm.dictate("' hi :> help.upper()")
        self.assertEqual(self.vm.pop(), 'CUSTOM')

    def test_colon_colon_and_colon_greater_in_colon_word(self):
        self.vm.dictate(": hi s\" Hello!\" . ;")
        self.vm.dictate(": set-h s\" GodHelps\" ' hi :: help=pop(1) ;")
        self.vm.dictate(": get-h ' hi :> help ;")
        self.vm.dictate("set-h get-h")
        self.assertEqual(self.vm.pop(), 'GodHelps')

    def test_dot_output(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate("123 . 456 .")
        self.assertEqual(buf.getvalue(), "123456")

    def test_see_output(self):
        self.vm.dictate(': hi s" Hello!" . ; // A greeting\n/// Note 1\n')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see hi')
        output = buf.getvalue()
        self.assertIn('hi A greeting', output)
        self.assertIn('    Note 1', output)
        self.assertIn("'name': 'hi'", output)
        self.assertIn("'type': 'colon'", output)
        self.assertIn(': hi', output)

    def test_value_and_to(self):
        # Definition & interpret usage
        self.vm.dictate('10 value total total')
        self.assertEqual(self.vm.pop(), 10)
        self.vm.dictate('20 to total total')
        self.assertEqual(self.vm.pop(), 20)

        # Python reading & writing
        word = self.vm.tick('total')
        self.assertEqual(word.value, 20)
        word.value = 99
        self.vm.dictate('total')
        self.assertEqual(self.vm.pop(), 99)

        # In colon definitions
        self.vm.dictate(': inc total 1 + to total ; inc total')
        self.assertEqual(self.vm.pop(), 100)

        # see output
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see total')
        self.assertIn('100 value total', buf.getvalue())

        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see inc')
        self.assertIn(': inc total 1 + to total ;', buf.getvalue())

        # Error when assigning to constant or non-existent
        self.vm.dictate('50 constant limit')
        with self.assertRaisesRegex(ForthError, 'not a value'):
            self.vm.dictate('60 to limit')
        with self.assertRaisesRegex(ForthError, 'Unknown word'):
            self.vm.dictate('60 to nonexistent')

    def test_forth_comma(self):
        # Define meta-compiling macro using comma
        self.vm.dictate(': compile-add [\'] + , ; immediate')
        self.vm.dictate(': calc 10 20 compile-add ; calc')
        self.assertEqual(self.vm.pop(), 30)

        # In interpret mode, comma raises ForthError
        with self.assertRaisesRegex(ForthError, 'No definition is being built'):
            self.vm.dictate("[\'] + ,")

    def test_return_stack(self):
        self.vm.dictate('10 >r 20 >r r@ r> r>')
        self.assertEqual(self.vm.pop(), 10)
        self.assertEqual(self.vm.pop(), 20)
        self.assertEqual(self.vm.pop(), 20)
        # A new task has its own empty return stack; r> must underflow
        with self.assertRaisesRegex(ForthError, 'Return stack underflow'):
            self.vm.dictate('r>')

    def test_return_stack_task_private_isolation(self):
        # Task 1 pushes to return stack and pauses
        task1 = self.vm.dictate('10 >r 20 >r pause r> r>')
        self.assertEqual(task1.status, 'paused')
        self.assertEqual(task1.rstack, [10, 20])

        # Task 2 runs independently with its own return stack
        self.vm.dictate('999 >r r@ r>')
        self.assertEqual(self.vm.pop(), 999)
        self.assertEqual(self.vm.pop(), 999)

        # Task 1's rstack was not touched by Task 2
        self.assertEqual(task1.rstack, [10, 20])

        # Resume Task 1 and verify it pops its own values
        task1.resume()
        self.assertEqual(task1.status, 'done')
        self.assertEqual(self.vm.pop(), 10)
        self.assertEqual(self.vm.pop(), 20)

    def test_for_next_task_isolation(self):
        # Task 1 pauses inside for...next loop
        task1 = self.vm.dictate(': pause-loop 2 for r@ pause next ; pause-loop')
        self.assertEqual(task1.status, 'paused')
        self.assertEqual(task1.rstack, [2])

        # Task 2 runs its own for...next loop to completion while Task 1 is paused
        self.vm.dictate(': other-loop 0 3 for r@ + next ; other-loop')
        self.assertEqual(self.vm.pop(), 6)  # 3+2+1 = 6

        # Task 1's loop counter is completely unharmed
        self.assertEqual(task1.rstack, [2])
        task1.resume()
        self.assertEqual(task1.status, 'paused')
        self.assertEqual(task1.rstack, [1])
        task1.resume()
        self.assertEqual(task1.status, 'done')

    def test_if_else_then(self):
        self.vm.dictate(': check-gt 10 > if 100 else 200 then ;')
        self.vm.dictate('15 check-gt')
        self.assertEqual(self.vm.pop(), 100)
        self.vm.dictate('5 check-gt')
        self.assertEqual(self.vm.pop(), 200)

        # Single if then
        self.vm.dictate(': check-pos dup 0 > if 1+ then ;')
        self.vm.dictate('5 check-pos')
        self.assertEqual(self.vm.pop(), 6)
        self.vm.dictate('-5 check-pos')
        self.assertEqual(self.vm.pop(), -5)

        # Nested if else then
        self.vm.dictate('''
        : nested-if
            dup 0 > if
                dup 10 > if
                    100
                else
                    50
                then
            else
                0
            then nip ;
        ''')
        self.vm.dictate('20 nested-if')
        self.assertEqual(self.vm.pop(), 100)
        self.vm.dictate('5 nested-if')
        self.assertEqual(self.vm.pop(), 50)
        self.vm.dictate('-3 nested-if')
        self.assertEqual(self.vm.pop(), 0)

        # Pause inside if
        self.vm.dictate(': pause-if 1 if 42 pause 99 then ;')
        task = self.vm.dictate('pause-if')
        self.assertEqual(task.status, 'paused')
        self.assertEqual(self.vm.stack, [42])
        task.resume()
        self.assertEqual(task.status, 'done')
        self.assertEqual(self.vm.stack, [42, 99])
        self.vm.stack.clear()

    def test_for_next(self):
        self.vm.dictate(': countdown 0 5 for r@ + next ; countdown')
        # 0 + 5 + 4 + 3 + 2 + 1 = 15
        self.assertEqual(self.vm.pop(), 15)

        # Early exit using return stack modification
        self.vm.dictate(': early-exit 0 10 for r@ + r@ 5 = if r> drop 0 >r then next ; early-exit')
        # 0 + 10 + 9 + 8 + 7 + 6 + 5 = 45
        self.assertEqual(self.vm.pop(), 45)

        # Nested for next
        self.vm.dictate(': nested-loop 0 3 for 2 for 1+ next next ; nested-loop')
        # 3 * 2 = 6
        self.assertEqual(self.vm.pop(), 6)

        # Pause inside for-next
        self.vm.dictate(': pause-for 2 for r@ pause next ;')
        task = self.vm.dictate('pause-for')
        self.assertEqual(task.status, 'paused')
        self.assertEqual(self.vm.stack, [2])
        task.resume()
        self.assertEqual(task.status, 'paused')
        self.assertEqual(self.vm.stack, [2, 1])
        task.resume()
        self.assertEqual(task.status, 'done')
        self.assertEqual(self.vm.stack, [2, 1])
        self.vm.stack.clear()

    def test_begin_loops(self):
        # begin ... until
        self.vm.dictate(': sum-until 0 1 begin swap over + swap 1+ dup 10 > until drop ; sum-until')
        self.assertEqual(self.vm.pop(), 55)

        # begin ... while ... repeat
        self.vm.dictate(': sum-while 0 1 begin dup 10 <= while swap over + swap 1+ repeat drop ; sum-while')
        self.assertEqual(self.vm.pop(), 55)

        # begin ... while ... until ... then
        self.vm.dictate(': sum-while-until 0 1 begin dup 20 <= while swap over + swap 1+ dup 10 > until then drop ; sum-while-until')
        self.assertEqual(self.vm.pop(), 55)

    def test_control_errors(self):
        with self.assertRaisesRegex(ForthError, 'No definition is being built'):
            self.vm.dictate('if')
        with self.assertRaisesRegex(ForthError, 'No definition is being built'):
            self.vm.dictate('for')
        with self.assertRaisesRegex(ForthError, 'Data stack is empty'):
            self.vm.dictate(': bad-then then ;')
        with self.assertRaisesRegex(ForthError, 'Data stack is empty'):
            self.vm.dictate(': bad-next next ;')
        with self.assertRaisesRegex(ForthError, 'Data stack is empty'):
            self.vm.dictate(': bad-repeat repeat ;')

    def test_words_command(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('words')
        all_words_output = buf.getvalue().strip().split()
        self.assertEqual(set(all_words_output), set(self.vm.words.keys()))

        # Single pattern
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('words drop')
        self.assertEqual(buf.getvalue().strip(), 'drop dropall rdrop 2drop')

        # Case-insensitive
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('words DROP')
        self.assertEqual(buf.getvalue().strip(), 'drop dropall rdrop 2drop')

        # Multiple patterns (AND logic)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('words py :')
        self.assertEqual(buf.getvalue().strip(), 'py: py::')

        # Non-matching pattern
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('words no_such_word')
        self.assertEqual(buf.getvalue().strip(), '')

    def test_help_command(self):
        # A specific name matches exactly, not words containing that name.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('help dup')
        expected_dup = (
            "dup ( x -- x x ) Duplicate the top item on the data stack.\n"
            "    Push a duplicate of TOS (top-of-stack) onto the data stack."
        )
        self.assertEqual(buf.getvalue().strip(), expected_dup)

        # Word lookup is case-insensitive.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('help DuP')
        self.assertEqual(buf.getvalue().strip(), expected_dup)

        # Help with custom word and multi-line comments
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate(': demo-fn ; // ( a -- b ) Custom demo\n/// Line 1\n/// Line 2\nhelp demo-fn')
        demo_output = buf.getvalue().strip()
        expected_demo = (
            "demo-fn ( a -- b ) Custom demo\n"
            "    Line 1\n"
            "    Line 2"
        )
        self.assertEqual(demo_output, expected_demo)

        # The name must match exactly; help text and multiple terms are not searched.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('help Custom demo')
        self.assertEqual(buf.getvalue().strip(), "No word named 'Custom demo'.")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('help for loop')
        self.assertEqual(buf.getvalue().strip(), "No word named 'for loop'.")

        # Help with no patterns outputs entire dictionary manual
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('help')
        all_help = buf.getvalue().strip()
        self.assertIn('code ( <name> -- )', all_help)
        self.assertIn('dup ( x -- x x )', all_help)
        self.assertIn('if ( flag -- )', all_help)

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
        self.vm.dictate(': greet s" Welcome!" ; greet')
        self.assertEqual(self.vm.pop(), 'Welcome!')

    def test_dot_string_words_print_in_interpret_and_compiled_modes(self):
        for source, expected in [
                ('." double quote output"', "double quote output"),
                (".' single quote output'", "single quote output"),
                (".` backtick output`", "backtick output")]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.vm.dictate(source)
            self.assertEqual(output.getvalue(), expected)

        self.vm.dictate(': say-double ." compiled double" ;')
        self.vm.dictate(": say-single .' compiled single' ;")
        self.vm.dictate(': say-backtick .` compiled backtick` ;')
        for source, expected in [
                ("say-double", "compiled double"),
                ("say-single", "compiled single"),
                ("say-backtick", "compiled backtick")]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.vm.dictate(source)
            self.assertEqual(output.getvalue(), expected)

    def test_char_token(self):
        # Single char
        self.vm.dictate('char "')
        self.assertEqual(self.vm.pop(), '"')

        # Multi-character non-whitespace string token (enhanced char)
        self.vm.dictate('char hello')
        self.assertEqual(self.vm.pop(), 'hello')
        self.vm.dictate('char token_123')
        self.assertEqual(self.vm.pop(), 'token_123')

        # Compilation mode inside colon definition
        self.vm.dictate(': get-tag char <my-tag> ; get-tag')
        self.assertEqual(self.vm.pop(), '<my-tag>')

        # Missing token raises ForthError
        with self.assertRaisesRegex(ForthError, 'char expects a token'):
            self.vm.dictate('char')

    def test_create_does(self):
        # Custom defining word via create ... does>
        self.vm.dictate(': mk-adder create , does> @ + ;')
        self.vm.dictate('10 mk-adder add10')
        self.assertEqual(self.vm.tick('add10').type, 'mk-adder')

        self.vm.dictate('5 add10')
        self.assertEqual(self.vm.pop(), 15)
        self.vm.dictate('100 add10')
        self.assertEqual(self.vm.pop(), 110)

        # Another custom defining word: constant factory defined by user
        self.vm.dictate(': my-const create , does> @ ;')
        self.vm.dictate('999 my-const k999')
        self.vm.dictate('k999')
        self.assertEqual(self.vm.pop(), 999)

    def test_variable_and_store_fetch(self):
        self.vm.dictate('variable counter')
        # Initial value is 0
        self.vm.dictate('counter @')
        self.assertEqual(self.vm.pop(), 0)

        # Store new value
        self.vm.dictate('42 counter !')
        self.vm.dictate('counter @')
        self.assertEqual(self.vm.pop(), 42)

        # Modify inside colon definition
        self.vm.dictate(': inc counter @ 1 + counter ! ; inc inc counter @')
        self.assertEqual(self.vm.pop(), 44)

    def test_see_defining_words(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see constant')
        self.assertIn(': constant create , does> @ ;', buf.getvalue())

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see value')
        self.assertIn(': value create , does> @ ;', buf.getvalue())

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see variable')
        self.assertIn(': variable create 0 , ;', buf.getvalue())

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see string-quote')
        self.assertIn(': string-quote create , immediate does> @ (s) ;', buf.getvalue())

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see s"')
        self.assertIn('char \'"\' string-quote s"', buf.getvalue())
        self.assertIn('Friends: s" s\' s` s| s^ s/', buf.getvalue())

    def test_see_code_and_created_words(self):
        # 1. see on code word (e.g. create)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see create')
        out_create = buf.getvalue()
        self.assertIn('create ( <name> -- )', out_create)
        self.assertIn("'name': 'create'", out_create)
        self.assertIn("'type': 'code'", out_create)
        self.assertIn("'help': '...'", out_create)
        self.assertIn("'comment': '...'", out_create)
        self.assertIn("'source': '...'", out_create)
        self.assertIn('code create', out_create)
        self.assertIn('end-code', out_create)

        # 2. see on created word with body (e.g. xx)
        self.vm.dictate('create xx 123 , 456 ,')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate('see xx')
        out_xx = buf.getvalue()
        self.assertIn("'name': 'xx'", out_xx)
        self.assertIn("'type': 'created'", out_xx)
        self.assertIn("'body': [123, 456]", out_xx)
        self.assertIn('created xx (body: [123, 456])', out_xx)

        # 3. ' create . prints native dataclass _Word(...) representation
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.vm.dictate("' create .")
        out_tick = buf.getvalue()
        self.assertTrue(out_tick.startswith("_Word(name='create'"))
        self.assertIn("help='( <name> -- )", out_tick)


if __name__ == '__main__':
    unittest.main()
