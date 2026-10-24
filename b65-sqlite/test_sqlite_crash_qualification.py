"""B6.5 SQLite crash/durability QA. All crashes affect isolated child processes and temp DBs."""
import multiprocessing as mp
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from sqlite_credit_ledger import SQLiteCreditLedger

def killed_during_transaction(path, ready):
    con=sqlite3.connect(path,timeout=10,isolation_level=None)
    con.execute("BEGIN IMMEDIATE")
    con.execute("UPDATE accounts SET available=available-5,reserved=reserved+5 WHERE id=1")
    con.execute("INSERT INTO reservations(key,cost,state,expires_at) VALUES('interrupted',5,'reserved',9999999999999)")
    ready.set()
    os._exit(73)  # no COMMIT: SQLite must roll back

def committed_then_killed(path, ready):
    ledger=SQLiteCreditLedger(path,20)
    ledger.reserve("durable",4)
    ready.set()
    os._exit(74)  # committed transaction must remain on disk

class SQLiteCrashQualification(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=str(Path(self.temp.name)/"crash.sqlite")
        self.db=SQLiteCreditLedger(self.path,20)
        self.ctx=mp.get_context("spawn")
    def tearDown(self):
        self.temp.cleanup()
    def launch(self,target):
        ready=self.ctx.Event()
        child=self.ctx.Process(target=target,args=(self.path,ready))
        child.start()
        self.assertTrue(ready.wait(20),"child did not reach crash point")
        child.join(20)
        self.assertFalse(child.is_alive(),"child still running")
        self.assertNotEqual(child.exitcode,0)
    def validate(self):
        with sqlite3.connect(self.path) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(),[])
            row=con.execute("SELECT budget,available,reserved,committed FROM accounts WHERE id=1").fetchone()
            self.assertEqual(row[0],sum(row[1:]))
            totals=con.execute("SELECT COALESCE(SUM(cost),0) FROM reservations WHERE state IN ('reserved','reconciliation_required')").fetchone()[0]
            self.assertEqual(row[2],totals)
            committed=con.execute("SELECT COALESCE(SUM(cost),0) FROM reservations WHERE state='committed'").fetchone()[0]
            self.assertEqual(row[3],committed)
    def test_kill_before_commit_rolls_back_atomically(self):
        self.launch(killed_during_transaction)
        self.validate()
        self.assertEqual(SQLiteCreditLedger(self.path,20).snapshot()["available"],20)
        with sqlite3.connect(self.path) as con:
            self.assertIsNone(con.execute("SELECT key FROM reservations WHERE key='interrupted'").fetchone())
    def test_kill_after_commit_preserves_reservation(self):
        self.launch(committed_then_killed)
        self.validate()
        reopened=SQLiteCreditLedger(self.path,20)
        self.assertEqual(reopened.snapshot()["reserved"],4)
        self.assertEqual(reopened.reserve("durable",4)["reason"],"REPLAY")
    def test_expired_inflight_after_restart_requires_reconciliation(self):
        now=[1000]
        db=SQLiteCreditLedger(self.path,20,clock=lambda:now[0])
        db.reserve("pending",6,ttl_ms=100)
        now[0]=1200
        restarted=SQLiteCreditLedger(self.path,20,clock=lambda:now[0])
        self.assertEqual(restarted.recover_expired(),1)
        self.assertEqual(restarted.snapshot()["reserved"],6)
        self.assertEqual(restarted.settle("pending")["reason"],"CHARGE_STATUS_UNKNOWN")
        self.validate()
        self.assertTrue(restarted.settle("pending",charged=False)["ok"])
        self.validate()
        self.assertEqual(restarted.snapshot()["available"],20)
    def test_integrity_detects_modified_accounting(self):
        self.db.reserve("pending",5)
        self.validate()
        with sqlite3.connect(self.path) as con:
            con.execute("UPDATE accounts SET committed=5,reserved=0,available=15 WHERE id=1")
        with self.assertRaises(AssertionError):
            self.validate()  # physical integrity_check alone would still say ok

if __name__=="__main__":
    unittest.main()
