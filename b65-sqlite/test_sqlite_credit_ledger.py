"""B6.5 real on-disk SQLite tests, including independent process concurrency."""
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from sqlite_credit_ledger import SQLiteCreditLedger

def worker(path, budget, start, index, output):
    start.wait()
    output.put(SQLiteCreditLedger(path,budget).reserve("req-"+str(index),2))

class SQLiteLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=str(Path(self.temp.name)/"ledger.sqlite")
        self.db=SQLiteCreditLedger(self.path,20)
    def tearDown(self):
        self.temp.cleanup()
    def test_persists_across_reopening(self):
        self.assertTrue(self.db.reserve("a",3)["ok"])
        del self.db
        other=SQLiteCreditLedger(self.path,20)
        self.assertEqual(other.snapshot()["reserved"],3)
        self.assertEqual(other.reserve("a",3)["reason"],"REPLAY")
    def test_multiprocess_no_overspend(self):
        ctx=multiprocessing.get_context("spawn")
        start=ctx.Event()
        output=ctx.Queue()
        workers=[ctx.Process(target=worker,args=(self.path,20,start,i,output)) for i in range(16)]
        for p in workers:p.start()
        start.set()
        results=[output.get(timeout=40) for _ in workers]
        for p in workers:
            p.join(timeout=40)
            self.assertEqual(p.exitcode,0)
        self.assertEqual(sum(r["ok"] for r in results),10)
        self.assertEqual(self.db.snapshot()["available"],0)
        self.assertEqual(self.db.snapshot()["reserved"],20)
    def test_settlement_exactly_once(self):
        self.db.reserve("a",5)
        self.assertTrue(self.db.settle("a",charged=True)["ok"])
        self.assertEqual(SQLiteCreditLedger(self.path,20).settle("a",charged=True)["reason"],"ALREADY_SETTLED")
        self.assertEqual(self.db.snapshot()["committed"],5)
    def test_refund_exactly_once(self):
        self.db.reserve("a",5)
        self.db.settle("a",charged=False)
        self.assertEqual(self.db.snapshot()["available"],20)
        self.assertEqual(self.db.settle("a",charged=False)["reason"],"ALREADY_SETTLED")
    def test_crash_and_reconciliation(self):
        now=[1000]
        db=SQLiteCreditLedger(self.path,20,clock=lambda:now[0])
        db.reserve("a",4,ttl_ms=100)
        now[0]=1200
        resumed=SQLiteCreditLedger(self.path,20,clock=lambda:now[0])
        self.assertEqual(resumed.recover_expired(),1)
        self.assertEqual(resumed.snapshot()["reserved"],4)
        self.assertEqual(resumed.reserve("a",4)["state"],"reconciliation_required")
        self.assertEqual(resumed.settle("a")["reason"],"CHARGE_STATUS_UNKNOWN")
        self.assertTrue(resumed.settle("a",charged=True)["ok"])
    def test_key_conflict_and_invariants(self):
        self.db.reserve("same",2)
        self.assertEqual(self.db.reserve("same",3)["reason"],"IDEMPOTENCY_CONFLICT")
        x=self.db.snapshot()
        self.assertEqual(x["budget"],x["available"]+x["reserved"]+x["committed"])
    def test_existing_db_budget_mismatch(self):
        with self.assertRaises(ValueError):SQLiteCreditLedger(self.path,999)

if __name__=="__main__":
    unittest.main()
