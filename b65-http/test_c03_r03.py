"""SEC01 C03-R03 — xClose synthetic native returns; no filesystem fault injection."""
import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent / "rd01-vfs-step1" / "c03-passive"))
from c03_run import validate_close_evidence, reciprocal_certificate
from test_c03_passive import fictional_entries, MAIN, ATTACHED

SOURCE=Path(__file__).resolve().parent/"rd01-vfs-step1"/"c03-passive"/"c03_vfs.c"

class C03R03CloseEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="atlas-c03-r03-")
        so=str(Path(cls.temp.name)/"c03.so")
        result=subprocess.run(["cc","-std=c11","-shared","-fPIC","-Wall","-Wextra",
                               "-o",so,str(SOURCE),"-lsqlite3"],capture_output=True,text=True)
        if result.returncode:
            raise AssertionError("C03-R03 compilation: "+result.stderr)
        cls.lib=ctypes.CDLL(so)
        cls.lib.c03_test_reset.argtypes=[]
        cls.lib.c03_test_open.argtypes=[ctypes.c_char_p,ctypes.c_int,ctypes.c_int]
        cls.lib.c03_test_open.restype=ctypes.c_int
        cls.lib.c03_test_close.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int]
        cls.lib.c03_test_close.restype=ctypes.c_int
        cls.lib.c03_close_info.argtypes=[ctypes.c_int]+[ctypes.POINTER(ctypes.c_int)]*3
        cls.lib.c03_close_info.restype=ctypes.c_int
        cls.lib.c03_info.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int]+[ctypes.POINTER(ctypes.c_int)]*7
        cls.lib.c03_info.restype=ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.lib.c03_test_reset()
        cls.temp.cleanup()

    def setUp(self):
        self.lib.c03_test_reset()

    def record(self, native_rc, known):
        index=self.lib.c03_test_open(b"/fictional/closing-journal",1,0)
        self.assertGreaterEqual(index,0)
        self.assertEqual(self.lib.c03_test_close(index,native_rc,int(known)),native_rc)
        path=ctypes.create_string_buffer(1024)
        state=[ctypes.c_int() for _ in range(7)]
        self.assertGreaterEqual(self.lib.c03_info(index,path,1024,*[ctypes.byref(v) for v in state]),0)
        close=[ctypes.c_int() for _ in range(3)]
        self.assertEqual(self.lib.c03_close_info(index,*[ctypes.byref(v) for v in close]),0)
        return {"closed":state[2].value,"error":state[4].value,
                "close_called":close[0].value,"close_known":close[1].value,
                "close_rc":close[2].value}

    def test_successful_close_native_ok(self):
        row=self.record(0,True)
        self.assertEqual(row,{"closed":1,"error":0,"close_called":1,"close_known":1,"close_rc":0})
        validate_close_evidence(row)

    def test_failed_close_native_result_preserved(self):
        row=self.record(10,True)  # synthetic SQLITE_IOERR; no OS failure induced
        self.assertEqual((row["closed"],row["error"],row["close_rc"]),(0,1,10))
        with self.assertRaises(AssertionError):validate_close_evidence(row)

    def test_unknown_close_result_rejected(self):
        row=self.record(0,False)
        self.assertEqual((row["closed"],row["close_called"],row["close_known"]),(0,1,0))
        with self.assertRaises(AssertionError):validate_close_evidence(row)

    def test_uninvoked_close_not_positive(self):
        row={"closed":0,"error":0,"close_called":0,"close_known":0,"close_rc":0}
        with self.assertRaises(AssertionError):validate_close_evidence(row)

    def test_failed_close_on_A_B_S_blocks_certificate(self):
        for index,role in ((1,"A"),(2,"B"),(0,"S")):
            with self.subTest(role=role):
                entries=fictional_entries()
                evidence=self.record(10,True)
                entries[index].update(evidence)
                with self.assertRaisesRegex(AssertionError,"C03-R03"):
                    reciprocal_certificate(entries,MAIN,ATTACHED,4096)

if __name__=="__main__":
    unittest.main()
