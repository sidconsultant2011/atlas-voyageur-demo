"""C03-R04 — purge C expérimental, allocations fictives, certificat normal et rejet."""
import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / "rd01-vfs-step1" / "c03-passive"))
from c03_run import run

SOURCE = Path(__file__).resolve().parent / "rd01-vfs-step1" / "c03-passive" / "c03_vfs.c"


class C03R04Wipe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="atlas-c03-r04-")
        so = str(Path(cls.tmp.name) / "libc03.so")
        proc = subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra",
                               "-o", so, str(SOURCE), "-lsqlite3"],
                              text=True, capture_output=True)
        if proc.returncode:
            raise AssertionError(proc.stderr)
        cls.lib = ctypes.CDLL(so)
        cls.lib.c03_test_reset.argtypes = []
        cls.lib.c03_test_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        cls.lib.c03_test_open.restype = ctypes.c_int
        cls.lib.c03_test_allocation_fault.argtypes = [ctypes.c_int]
        cls.lib.c03_cleanup.argtypes = []
        cls.lib.c03_count.restype = ctypes.c_int
        cls.lib.c03_overflow.restype = ctypes.c_int
        cls.lib.c03_wipe_stats.argtypes = [ctypes.POINTER(ctypes.c_int)] * 4
        cls.lib.c03_wipe_stats.restype = ctypes.c_int
        cls.lib.c03_copy.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        cls.lib.c03_copy.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.lib.c03_test_reset()
        cls.tmp.cleanup()

    def setUp(self):
        self.lib.c03_test_reset()

    def stats(self):
        x = [ctypes.c_int() for _ in range(4)]
        self.assertEqual(self.lib.c03_wipe_stats(*[ctypes.byref(v) for v in x]), 0)
        return tuple(v.value for v in x)  # verified, failures, freed, records remaining

    def test_full_allocation_then_wipe_before_free(self):
        idx = self.lib.c03_test_open(b"/fictional/a-journal", 1, 1)
        self.assertEqual(idx, 0)
        self.lib.c03_cleanup()
        self.assertEqual(self.stats(), (2, 0, 2, 0))
        self.assertEqual(self.lib.c03_copy(0, None, None, 0), -1)

    def test_both_partial_allocation_failures_are_cleaned(self):
        for mode in (1, 2):
            with self.subTest(partial=mode):
                self.lib.c03_test_reset()
                self.lib.c03_test_allocation_fault(mode)
                self.assertEqual(self.lib.c03_test_open(b"/fictional/partial-journal", 1, 1), -1)
                self.assertEqual(self.lib.c03_overflow(), 1)
                self.assertEqual(self.stats()[:3], (1, 0, 1))
                self.lib.c03_cleanup()
                self.assertEqual(self.stats(), (1, 0, 1, 0))
                self.lib.c03_test_allocation_fault(0)

    def test_reset_idempotent(self):
        self.assertEqual(self.lib.c03_test_open(b"/fictional/reset-journal", 1, 1), 0)
        self.lib.c03_cleanup()
        first = self.stats()
        self.lib.c03_cleanup()
        self.assertEqual(first, self.stats())
        self.lib.c03_test_reset()
        self.assertEqual(self.stats(), (0, 0, 0, 0))

    def test_successful_certificate_then_cleanup(self):
        certificate = run()
        self.assertEqual(certificate["verdict"], "RECONSTRUIT_BANC_FICTIF")
        self.assertEqual(certificate["links"],
                         {"S_to_journals": ["A", "B"], "A_to_S": True, "B_to_S": True})
        self.assertEqual(certificate["integrity_check"], ["ok", "ok"])
        self.assertEqual(certificate["journal_mode"], ["delete", "delete"])
        self.assertEqual(certificate["synchronous"], [2, 2])
        self.assertEqual(certificate["deletion_attribution"]["attributed"], 6)

    def test_rejected_certificate_then_cleanup(self):
        with self.assertRaisesRegex(AssertionError, "rejet fictif après copie"):
            run(reject_after_copy=True)


if __name__ == "__main__":
    unittest.main()
