"""C03-R02 : preuves ciblées d'attribution xDelete, banc fictif seulement.
Le retour SQLite fourni est conservé ; seuls les marqueurs probatoires changent.
"""
import ctypes
import ctypes.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent / "rd01-vfs-step1" / "c03-passive" / "c03_vfs.c"

class C03R02DeletionAttribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="atlas-c03-r02-")
        so = str(Path(cls.temp.name) / "c03.so")
        proc = subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra",
                               "-o", so, str(SOURCE), "-lsqlite3"],
                              capture_output=True, text=True)
        if proc.returncode:
            raise AssertionError("C03-R02 compiler: " + proc.stderr)
        cls.lib = ctypes.CDLL(so)
        cls.lib.c03_test_reset.argtypes = []
        cls.lib.c03_test_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        cls.lib.c03_test_open.restype = ctypes.c_int
        cls.lib.c03_test_delete.argtypes = [ctypes.c_char_p, ctypes.c_int]
        cls.lib.c03_test_delete.restype = ctypes.c_int
        cls.lib.c03_info.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int] + [
            ctypes.POINTER(ctypes.c_int)] * 7
        cls.lib.c03_info.restype = ctypes.c_int
        cls.lib.c03_delete_stats.argtypes = [ctypes.POINTER(ctypes.c_int)] * 6
        cls.lib.c03_delete_stats.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.lib.c03_test_reset()
        cls.temp.cleanup()

    def setUp(self):
        self.lib.c03_test_reset()
        self.path = b"/fictional/c03/identities.sqlite-journal"

    def opened(self, path=None, closed=True):
        index = self.lib.c03_test_open(path or self.path, 1, int(closed))
        self.assertGreaterEqual(index, 0)
        return index

    def deleted(self, index):
        name = ctypes.create_string_buffer(1024)
        values = [ctypes.c_int() for _ in range(7)]
        self.assertGreaterEqual(self.lib.c03_info(index, name, 1024,
                                *[ctypes.byref(v) for v in values]), 0)
        return values[3].value

    def stats(self):
        values = [ctypes.c_int() for _ in range(6)]
        self.assertEqual(self.lib.c03_delete_stats(*[ctypes.byref(v) for v in values]), 0)
        return tuple(v.value for v in values)  # events, attributed, ambiguous, unknown, native_error, unclosed

    def test_active_unique_closed_incarnation(self):
        first = self.opened()
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        self.assertEqual(self.deleted(first), 1)
        self.assertEqual(self.stats(), (1, 1, 0, 0, 0, 0))

    def test_reused_path_distinct_proven_lifecycle(self):
        first = self.opened()
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        second = self.opened()
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        self.assertEqual((self.deleted(first), self.deleted(second)), (1, 1))
        self.assertEqual(self.stats(), (2, 2, 0, 0, 0, 0))

    def test_multiple_compatible_incarnations_must_remain_unattributed(self):
        a, b = self.opened(), self.opened()
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)  # real native rc kept
        self.assertEqual((self.deleted(a), self.deleted(b)), (0, 0))
        self.assertEqual(self.stats(), (1, 0, 1, 0, 0, 0))

    def test_native_delete_error_never_marks_deleted(self):
        first = self.opened()
        self.assertEqual(self.lib.c03_test_delete(self.path, 10), 10)  # SQLITE_IOERR
        self.assertEqual(self.deleted(first), 0)
        self.assertEqual(self.stats(), (1, 0, 0, 0, 1, 0))

    def test_delete_without_open_is_non_attributable(self):
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        self.assertEqual(self.stats(), (1, 0, 0, 1, 0, 0))

    def test_recreation_after_proven_deletion(self):
        first = self.opened()
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        fresh = self.opened()
        self.assertEqual((self.deleted(first), self.deleted(fresh)), (1, 0))
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        self.assertEqual((self.deleted(first), self.deleted(fresh)), (1, 1))
        self.assertEqual(self.stats(), (2, 2, 0, 0, 0, 0))

    def test_open_incarnation_not_claimed_proven(self):
        first = self.opened(closed=False)
        self.assertEqual(self.lib.c03_test_delete(self.path, 0), 0)
        self.assertEqual(self.deleted(first), 0)
        self.assertEqual(self.stats(), (1, 0, 0, 0, 0, 1))

if __name__ == "__main__":
    unittest.main()
