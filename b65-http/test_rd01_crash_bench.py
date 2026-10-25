"""RD01: invoke isolated SIGKILL harness in the existing B6.5 offline CI."""
import unittest
from rd01_crash_bench import experiment, PHASES, REPEATS


class RD01CrashQualification(unittest.TestCase):
    def test_process_kill_attached_sqlite_recovery(self):
        report = experiment()
        self.assertEqual(report["total"], len(PHASES) * REPEATS)
        self.assertEqual(report["passed"], report["total"])
        print("RD01 ENV:", report["environment"], flush=True)
        for case in report["cases"]:
            print("RD01 CASE:", case["phase"], case["repetition"], case["etat"],
                  case["integrity_check"], case["journal_mode"],
                  case["synchronous"], "SIGKILL", flush=True)
        for case in report["cases"]:
            with self.subTest(phase=case["phase"], repetition=case["repetition"]):
                self.assertTrue(case["compliant"])
                self.assertEqual(case["integrity_check"], ["ok", "ok"])
                self.assertEqual(case["etat"], case["expected"])


if __name__ == "__main__":
    unittest.main()
