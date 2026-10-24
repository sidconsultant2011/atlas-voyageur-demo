"""B6.5 SQLite offline credit ledger. No HTTP and no provider secrets."""
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
 id INTEGER PRIMARY KEY CHECK(id=1),
 budget INTEGER NOT NULL CHECK(budget>=0),
 available INTEGER NOT NULL CHECK(available>=0),
 reserved INTEGER NOT NULL CHECK(reserved>=0),
 committed INTEGER NOT NULL CHECK(committed>=0),
 CHECK(available+reserved+committed=budget)
);
CREATE TABLE IF NOT EXISTS reservations (
 key TEXT PRIMARY KEY,
 cost INTEGER NOT NULL CHECK(cost>0),
 state TEXT NOT NULL CHECK(state IN ('reserved','committed','released','reconciliation_required')),
 expires_at INTEGER NOT NULL
);
"""

class SQLiteCreditLedger:
    def __init__(self, database_path, budget, clock=None):
        if type(budget) is not int or budget < 0:
            raise ValueError("invalid budget")
        self.path = str(Path(database_path))
        self.clock = clock or (lambda: int(time.time() * 1000))
        with self._connect() as con:
            con.executescript(SCHEMA)
            con.execute("INSERT OR IGNORE INTO accounts(id,budget,available,reserved,committed) VALUES (1,?,?,0,0)", (budget,budget))
            existing = con.execute("SELECT budget FROM accounts WHERE id=1").fetchone()[0]
            if existing != budget:
                raise ValueError("budget mismatch for existing database")

    def _connect(self):
        con = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        con.execute("PRAGMA busy_timeout=10000")
        return con

    def _transaction(self, operation):
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            result = operation(con)
            con.commit()
            return result
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def reserve(self, key, cost, ttl_ms=60000):
        if not isinstance(key,str) or not key.strip() or type(cost) is not int or cost<=0 or type(ttl_ms) is not int or ttl_ms<=0:
            raise ValueError("invalid reservation")
        def op(con):
            row = con.execute("SELECT cost,state FROM reservations WHERE key=?", (key,)).fetchone()
            if row:
                if row[0]!=cost: return {"ok":False,"reason":"IDEMPOTENCY_CONFLICT"}
                return {"ok":row[1]!="released","reason":"REPLAY","state":row[1]}
            updated = con.execute("UPDATE accounts SET available=available-?, reserved=reserved+? WHERE id=1 AND available>=?",(cost,cost,cost)).rowcount
            if not updated: return {"ok":False,"reason":"BUDGET_EXHAUSTED"}
            con.execute("INSERT INTO reservations(key,cost,state,expires_at) VALUES(?,?,'reserved',?)",(key,cost,int(self.clock())+ttl_ms))
            return {"ok":True,"state":"reserved"}
        return self._transaction(op)

    def settle(self, key, charged=None):
        def op(con):
            row=con.execute("SELECT cost,state FROM reservations WHERE key=?",(key,)).fetchone()
            if not row:return {"ok":False,"reason":"UNKNOWN_RESERVATION"}
            cost,state=row
            if state not in ("reserved","reconciliation_required"):return {"ok":False,"reason":"ALREADY_SETTLED"}
            if type(charged) is not bool:return {"ok":False,"reason":"CHARGE_STATUS_UNKNOWN"}
            con.execute("UPDATE accounts SET reserved=reserved-?, committed=committed+? , available=available+? WHERE id=1",(cost,cost if charged else 0,0 if charged else cost))
            con.execute("UPDATE reservations SET state=? WHERE key=?",("committed" if charged else "released",key))
            return {"ok":True,"state":"committed" if charged else "released"}
        return self._transaction(op)

    def recover_expired(self):
        def op(con):
            return con.execute("UPDATE reservations SET state='reconciliation_required' WHERE state='reserved' AND expires_at<=?",(int(self.clock()),)).rowcount
        return self._transaction(op)

    def snapshot(self):
        with self._connect() as con:
            row=con.execute("SELECT budget,available,reserved,committed FROM accounts WHERE id=1").fetchone()
            return dict(zip(("budget","available","reserved","committed"),row))
