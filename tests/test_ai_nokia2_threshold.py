import os, unittest
from unittest.mock import patch
from peforth import repl

class Nokia2ThresholdTests(unittest.TestCase):
    def setUp(self):
        p=patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE":"disabled"})
        p.start()
        self.addCleanup(p.stop)

    def test_default_and_user_setting(self):
        vm=repl.create_vm()
        word=vm.tick("ai:")
        self.assertEqual(word.nokia2_after_seconds,30)
        vm.dictate("' ai: :: nokia2_after_seconds=45")
        self.assertEqual(word.nokia2_after_seconds,45)

    def test_strict_threshold_controls_chime(self):
        for limit,elapsed,expected in ((30,30,False),(30,30.01,True),(45,45,False),(45,45.01,True)):
            vm=repl.create_vm()
            if limit != 30: vm.dictate(f"' ai: :: nokia2_after_seconds={limit}")
            clock=iter((100,100+elapsed))
            played=[]
            def fake_ai(vm):
                vm.pop()
                vm.pop()
            vm.tick("(ai-monotonic-time)").action=lambda vm: vm.push(next(clock))
            vm.tick("(ai)").action=fake_ai
            vm.tick("nokia2").action=lambda vm: played.append(True)
            task=vm.dictate("ai: hello")
            self.assertEqual(task.status,"done")
            self.assertEqual(played,[True] if expected else [])
            self.assertEqual(vm.stack,[])

if __name__ == "__main__":
    unittest.main()
