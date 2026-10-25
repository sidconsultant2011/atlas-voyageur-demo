"""C03-R05 : exécution répétée N/W/C03 sur banc fictif, sans panne."""
import json
import unittest
from c03_r05_compare import campaign

class C03R05Neutrality(unittest.TestCase):
    def test_three_vfs_functional_parity_and_descriptive_measurements(self):
        proof = campaign()
        self.assertTrue(proof["functional_parity"])
        self.assertEqual(proof["measured_samples"], 18)
        self.assertEqual(proof["warmups"], 6)
        for resolution in ("COMMIT", "ROLLBACK"):
            for mode in ("N", "W", "C03"):
                with self.subTest(resolution=resolution, mode=mode):
                    sample = proof["summary"][resolution][mode]
                    self.assertEqual(len(sample["samples_ms"]), 3)
                    self.assertTrue(all(x >= 0 for x in sample["samples_ms"]))
        print("RD01 C03-R05 N/W/C03 PARITY AND TIMINGS " +
              json.dumps(proof, ensure_ascii=False, sort_keys=True), flush=True)

if __name__ == "__main__":
    unittest.main()
