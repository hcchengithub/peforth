import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from peforth import repl


class IncludeTests(unittest.TestCase):
    def setUp(self):
        self._environment = patch.dict(os.environ, {'PEFORTH_AI_LOG_MODE': 'disabled'})
        self._environment.start()
        self.addCleanup(self._environment.stop)

    def make_vm(self, runtime_path):
        vm = repl.create_vm()
        vm.host['system_info']['runtime_path'] = str(runtime_path)
        return vm

    def test_include_words_have_help_and_comments(self):
        with tempfile.TemporaryDirectory() as runtime:
            vm = self.make_vm(runtime)
            for name in ("include", "(include)"):
                word = vm.tick(name)
                self.assertTrue(word.help, name)
                self.assertTrue(word.comment, name)

    def test_include_prefers_current_working_directory(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as runtime:
            cwd_path = Path(cwd)
            runtime_f = Path(runtime) / 'f'
            runtime_f.mkdir()
            (cwd_path / 'module.f').write_text('111', encoding='utf-8')
            (runtime_f / 'module.f').write_text('222', encoding='utf-8')
            vm = self.make_vm(runtime)
            with patch('pathlib.Path.cwd', return_value=cwd_path):
                task = vm.dictate('include module.f')
            self.assertEqual(task.status, 'done')
            self.assertEqual(vm.pop(), 111)

    def test_include_falls_back_to_runtime_f_directory(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as runtime:
            cwd_path = Path(cwd)
            runtime_f = Path(runtime) / 'f'
            runtime_f.mkdir()
            (runtime_f / 'module.f').write_text('222', encoding='utf-8')
            vm = self.make_vm(runtime)
            with patch('pathlib.Path.cwd', return_value=cwd_path):
                task = vm.dictate('include module.f')
            self.assertEqual(task.status, 'done')
            self.assertEqual(vm.pop(), 222)

    def test_parenthesized_include_accepts_path_with_spaces_from_stack(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as runtime:
            cwd_path = Path(cwd)
            source_path = cwd_path / 'module with spaces.f'
            source_path.write_text('333', encoding='utf-8')
            vm = self.make_vm(runtime)
            with patch('pathlib.Path.cwd', return_value=cwd_path):
                vm.push(str(source_path))
                task = vm.dictate('(include)')
            self.assertEqual(task.status, 'done')
            self.assertEqual(vm.pop(), 333)


if __name__ == '__main__':
    unittest.main()
