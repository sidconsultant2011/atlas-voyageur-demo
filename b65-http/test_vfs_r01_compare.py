"""VFS-R01 : témoin natif N vs wrapper inchangé W, COMMIT normal uniquement."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / "rd01-vfs-step1"))
from vfs_r01_compare import compare


class VFSR01Parity(unittest.TestCase):
    def test_native_wrapper_normal_commit(self):
        proof = compare()
        self.assertTrue(proof["environment"]["same_library_symbol"])
        self.assertEqual(proof["differences"], [])
        self.assertEqual(proof["N"]["integrity"], ["ok", "ok"])
        self.assertEqual(proof["W"]["integrity"], ["ok", "ok"])
        self.assertGreater(proof["W_observations"]["xSync"], 0)
        self.assertEqual(proof["N"]["remaining_journals"], [])
        self.assertEqual(proof["W"]["remaining_journals"], [])
        print("RD01 VFS R01 NATIVE WRAPPER COMPARISON " +
              json.dumps(proof, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    unittest.main()
