import os
import unittest
from unittest.mock import patch

from peforth import repl


class MergedBaseWordsTests(unittest.TestCase):
    def setUp(self):
        self._environment = patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"})
        self._environment.start()
        self.addCleanup(self._environment.stop)
        self.vm = repl.create_vm()

    def test_last_literal_sets_property_on_word_being_defined(self):
        task = self.vm.dictate(
            ": test [ last literal ] :> nokia2_after_seconds ;"
        )
        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.stack, [])

        task = self.vm.dictate("' test :: nokia2_after_seconds=30")
        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.stack, [])

        task = self.vm.dictate("test")
        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), 30)

    def test_auxiliary_migrated_key_words_return_lists(self):
        self.vm.push({"alpha": 1})
        task = self.vm.dictate("dict>keys")
        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), ["alpha"])

        self.vm.push({"beta": 2})
        task = self.vm.dictate("keys")
        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), ["beta"])


if __name__ == "__main__":
    unittest.main()
