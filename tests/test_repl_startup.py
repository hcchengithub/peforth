import subprocess
import sys
import unittest


class ReplStartupTests(unittest.TestCase):
    def test_noninteractive_import_defers_prompt_toolkit_ui(self):
        probe = (
            "import sys; import peforth.repl as repl; "
            "print(repl.PromptSession is None, "
            "any(name == 'prompt_toolkit' or name.startswith('prompt_toolkit.') "
            "for name in sys.modules))"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "True False")


if __name__ == "__main__":
    unittest.main()
