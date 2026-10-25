"""SEC-01 VFS-R01 : contention bornée N/W sans panne."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / "rd01-vfs-step1"))
from vfs_r01_contention import compare_contention


class VFSR01LockParity(unittest.TestCase):
    def test_busy_and_recovery_after_normal_release(self):
        proof = compare_contention()
        self.assertTrue(proof["environment"]["same_library_symbol"])
        for resolution in ("COMMIT", "ROLLBACK"):
            with self.subTest(resolution=resolution):
                case = proof["cases"][resolution]
                self.assertTrue(case["functional_parity"])
                self.assertEqual(case["N"], case["W"])
                self.assertEqual(case["N"]["busy_code"], 5)  # SQLITE_BUSY
                self.assertEqual(case["N"]["busy_name"], "SQLITE_BUSY")
                self.assertEqual(case["N"]["retry"], "COMMIT")
                self.assertEqual(case["N"]["final"]["integrity"], ["ok", "ok"])
                self.assertEqual(case["N"]["remaining_journals"], [])
                self.assertEqual(case["N"]["journal_mode"], ["delete", "delete"])
                self.assertEqual(case["N"]["synchronous"], [2, 2])
        self.assertGreater(proof["W_successful_xSync_logged"], 0)
        print("RD01 VFS R01 LOCK SYNC PARITY " +
              json.dumps(proof, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    unittest.main()
