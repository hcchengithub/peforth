import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from peforth import ai_bridge
from peforth import repl as _f_mod


class AISkillsTests(unittest.TestCase):
    def setUp(self):
        self._diagnostics_patch = patch.dict(
            os.environ, {'PEFORTH_AI_LOG_MODE': 'disabled'}
        )
        self._diagnostics_patch.start()
        self.addCleanup(self._diagnostics_patch.stop)

    def _write_skill(self, root, name, contents):
        skill_dir = root / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / 'SKILL.md').write_text(contents, encoding='utf-8')
        return skill_dir

    def test_loads_skill_directories_in_order_and_strips_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self._write_skill(
                root, 'zeta',
                '---\nname: zeta\ndescription: metadata\n---\n# Zeta skill\n',
            )
            self._write_skill(root, 'alpha', '# Alpha skill\n')
            (root / 'ignored').mkdir()
            (root / 'README.md').write_text('not a skill', encoding='utf-8')

            with patch.dict(os.environ, {'PEFORTH_SKILLS_DIR': str(root)}):
                names, combined = ai_bridge._load_all_skills_text()

        self.assertEqual(names, ['alpha', 'zeta'])
        self.assertIn('## Skill: alpha', combined)
        self.assertIn('# Alpha skill', combined)
        self.assertIn('## Skill: zeta', combined)
        self.assertIn('# Zeta skill', combined)
        self.assertNotIn('description: metadata', combined)

    def test_agent_instructions_include_all_skills_and_forth_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self._write_skill(root, 'peforth-forth', '# Core Forth skill\n')
            self._write_skill(root, 'extra', '# Extra skill\n')
            reference = (
                root / 'peforth-forth' / 'references' / 'forth-reference.md'
            )
            reference.parent.mkdir()
            reference.write_text('# Forth reference body\n', encoding='utf-8')

            with patch.dict(os.environ, {'PEFORTH_SKILLS_DIR': str(root)}):
                instructions = ai_bridge._agent_instructions()

        self.assertIn('## Skill: extra', instructions)
        self.assertIn('# Extra skill', instructions)
        self.assertIn('## Skill: peforth-forth', instructions)
        self.assertIn('Forth reference:', instructions)
        self.assertIn('# Forth reference body', instructions)
        self.assertLessEqual(len(instructions.encode('utf-8')), 100_000)

    def test_agent_instructions_resolve_relative_skills_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime_root = pathlib.Path(directory)
            skills_root = runtime_root / 'configured-skills'
            self._write_skill(skills_root, 'peforth-forth', '# Core Forth skill\n')
            reference = (
                skills_root / 'peforth-forth' / 'references' / 'forth-reference.md'
            )
            reference.parent.mkdir()
            reference.write_text('# Relative Forth reference\n', encoding='utf-8')
            with patch.object(ai_bridge, 'RUNTIME_ROOT', runtime_root):
                with patch.dict(os.environ, {'PEFORTH_SKILLS_DIR': 'configured-skills'}):
                    instructions = ai_bridge._agent_instructions()
        self.assertIn('# Relative Forth reference', instructions)
    def test_agent_instructions_reject_more_than_100kb(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self._write_skill(root, 'large', '\u4f60' * 34_000)

            with patch.dict(os.environ, {'PEFORTH_SKILLS_DIR': str(root)}):
                with self.assertRaisesRegex(RuntimeError, 'too large'):
                    ai_bridge._agent_instructions()

    def test_list_skills_pushes_sorted_names_on_forth_stack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self._write_skill(root, 'zeta', '# Zeta\n')
            self._write_skill(root, 'alpha', '# Alpha\n')

            with patch.dict(os.environ, {'PEFORTH_SKILLS_DIR': str(root)}):
                vm = _f_mod.create_vm()
                vm.dictate('list-skills')

        self.assertEqual(vm.pop(), 'alpha zeta')
        self.assertEqual(vm.stack, [])


if __name__ == '__main__':
    unittest.main()
