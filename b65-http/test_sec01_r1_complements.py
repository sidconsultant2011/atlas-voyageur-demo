"""SEC-01 R1 complément : entrelacements reproductibles, HTTP et SQLite.
Les événements signalent l'entrée effective dans la transaction (après BEGIN IMMEDIATE).
Aucun service ni identité réelle.
"""
import http.client
import json
import multiprocessing as mp
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from persistent_sessions import PersistentSessionState
from fictional_identities import FictionalIdentityStore
from local_identity_bridge import LocalIdentityBridge
from local_http_facade import create_server, ALLOWED_ORIGIN


def child_during_open_transaction(path, sid, jid, started, begin, result):
    state = PersistentSessionState(path, clock=lambda: 1000.0, rate_limit=1000)
    started.set()                 # child is alive, but not yet authorized
    begin.wait(10)
    result.put(("begun", True))
    result.put(("mutation", state.update_journey(sid, jid, "child-too-late")))


class R1Complements(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "sessions.sqlite")
        self.identity_path = str(Path(self.temp.name) / "identities.sqlite")
        self.now = [1000.0]
        self.state = PersistentSessionState(self.path, clock=lambda: self.now[0], rate_limit=1000)
        self.sid, self.csrf = self.state.create()
        self.identities = FictionalIdentityStore(self.identity_path, clock=lambda: self.now[0])
        self.identities.add_fixture_identity("qa-alice")
        self.bridge = LocalIdentityBridge(self.identities)
        self.bridge.bind_state(self.state)
        self.token = self.identities.open_session("qa-alice")
        self.bridge.bind_fixture(self.sid, self.token)

    def tearDown(self):
        self.temp.cleanup()

    def read_sql(self, filename, statement, args=()):
        with sqlite3.connect(filename) as db:
            return db.execute(statement, args).fetchall()

    def test_create_update_delete_forced_precommit_order(self):
        # The mutator has already acquired BEGIN IMMEDIATE before the revoke starts.
        for operation in ("create", "update", "delete"):
            with self.subTest(operation=operation):
                sid, csrf = self.state.create()
                self.bridge.bind_fixture(sid, self.identities.open_session("qa-alice"))
                jid = self.bridge.create(sid)
                entered, release = threading.Event(), threading.Event()
                class HeldState(PersistentSessionState):
                    def _authorize(inner, connection, cookie, csrf=None, write=False):
                        status = super()._authorize(connection, cookie, csrf, write)
                        if (cookie == sid and threading.current_thread().name == "held-writer"):
                            entered.set()
                            if not release.wait(8):
                                raise TimeoutError("Held writer not released")
                        return status
                held = HeldState(self.path, clock=lambda: self.now[0], rate_limit=1000)
                writer_bridge = LocalIdentityBridge(self.identities)
                writer_bridge.bind_state(held)
                # The fixture binding also checks the cookie but does not enter _authorize.
                writer_bridge.bind_fixture(sid, self.identities.open_session("qa-alice"))
                outcomes = {}
                def mutate():
                    if operation == "create":
                        outcomes["mutation"] = writer_bridge.create(sid)
                    elif operation == "update":
                        outcomes["mutation"] = writer_bridge.update(sid, jid, "authorized")
                    else:
                        outcomes["mutation"] = writer_bridge.delete(sid, jid)
                def revoke():
                    outcomes["revoke"] = self.state.revoke(sid, csrf)
                writer = threading.Thread(target=mutate, name="held-writer")
                revoker = threading.Thread(target=revoke)
                try:
                    writer.start()
                    self.assertTrue(entered.wait(8), "Writer did not reach locked transaction")
                    revoker.start()
                    # Revoker cannot complete while the mutation owns the SQLite write lock.
                    self.assertNotIn("revoke", outcomes)
                finally:
                    release.set()
                    writer.join(12)
                    if revoker.ident is not None:
                        revoker.join(12)
                self.assertFalse(writer.is_alive())
                self.assertFalse(revoker.is_alive())
                self.assertEqual(outcomes["revoke"][0], 200)
                self.assertEqual(self.read_sql(self.path, "SELECT revoked FROM sessions WHERE id_hash=?",
                                               (self.state.digest(sid),)), [(1,)])
                if operation == "create":
                    self.assertIsNotNone(outcomes["mutation"])
                    created = outcomes["mutation"]
                    self.assertEqual(len(self.read_sql(self.identity_path,
                                      "SELECT id FROM identity_journeys WHERE id=?", (created,))), 1)
                elif operation == "update":
                    self.assertTrue(outcomes["mutation"])
                    self.assertEqual(self.read_sql(self.identity_path,
                                     "SELECT label FROM identity_journeys WHERE id=?", (jid,)),
                                     [("authorized",)])
                else:
                    self.assertTrue(outcomes["mutation"])
                    self.assertEqual(self.read_sql(self.identity_path,
                                     "SELECT id FROM identity_journeys WHERE id=?", (jid,)), [])
                self.assertIsNone(writer_bridge.create(sid))
                self.assertFalse(writer_bridge.update(sid, jid, "late"))
                self.assertFalse(writer_bridge.delete(sid, jid))

    def test_other_process_blocked_by_real_open_transaction(self):
        ctx = mp.get_context("spawn")
        started, begin = ctx.Event(), ctx.Event()
        result = ctx.Queue()
        jid = self.state.create_journey(self.sid)
        # Hold a real SQLite write transaction while the child begins.
        parent = sqlite3.connect(self.path, timeout=10)
        process = ctx.Process(target=child_during_open_transaction,
                              args=(self.path, self.sid, jid, started, begin, result))
        try:
            parent.execute("BEGIN IMMEDIATE")
            self.assertEqual(parent.execute("SELECT revoked FROM sessions WHERE id_hash=?",
                                           (self.state.digest(self.sid),)).fetchone(), (0,))
            process.start()
            self.assertTrue(started.wait(10))
            begin.set()
            self.assertEqual(result.get(timeout=10), ("begun", True))
            # Revocation takes effect while the child is waiting for the DB lock.
            parent.execute("UPDATE sessions SET revoked=1 WHERE id_hash=?",
                           (self.state.digest(self.sid),))
            parent.commit()
            self.assertEqual(result.get(timeout=12), ("mutation", None))
            process.join(10)
            self.assertEqual(process.exitcode, 0)
            self.assertEqual(self.read_sql(self.path,"SELECT label FROM journeys WHERE id=?",(jid,)),
                             [("Parcours fictif",)])
        finally:
            begin.set()
            parent.close()
            if process.is_alive():
                process.terminate()
                process.join(5)

    def test_http_refuses_every_mutation_after_revocation_with_sql_proof(self):
        server = create_server(state=self.state, identity_bridge=self.bridge)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def request(method, route, body=None):
            headers = {"Origin": ALLOWED_ORIGIN, "Cookie": "atlas_qa=" + self.sid,
                       "X-CSRF-Token": self.csrf}
            if body is not None:
                headers["Content-Type"] = "application/json"
                body = json.dumps(body)
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            try:
                conn.request(method, route, body=body, headers=headers)
                response = conn.getresponse()
                response.read()
                return response.status
            finally:
                conn.close()
        try:
            jid = self.bridge.create(self.sid)
            route = "/api/v1/qa/journeys/" + jid
            self.assertEqual(request("POST", "/api/v1/qa/session/revoke"), 200)
            self.assertEqual(self.read_sql(self.path,
                "SELECT revoked FROM sessions WHERE id_hash=?", (self.state.digest(self.sid),)), [(1,)])
            self.assertEqual(request("POST", "/api/v1/qa/journeys", {}), 401)
            self.assertEqual(request("POST", route + "/label", {"message": "late"}), 401)
            self.assertEqual(request("DELETE", route), 401)
            self.assertEqual(request("GET", route), 401)
            self.assertEqual(self.read_sql(self.identity_path,
                "SELECT label FROM identity_journeys WHERE id=?", (jid,)), [("Parcours fictif",)])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)

    def test_journal_settings_and_rollback_for_attached_databases(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute("PRAGMA journal_mode").fetchone()
            self.assertEqual(rows[0].lower(), "delete")
            db.execute("ATTACH DATABASE ? AS idb", (self.identity_path,))
            self.assertEqual(db.execute("PRAGMA idb.journal_mode").fetchone()[0].lower(), "delete")
            # SQLite synchronous=FULL (2) is the default used by the fixture.
            self.assertEqual(db.execute("PRAGMA main.synchronous").fetchone()[0], 2)
            self.assertEqual(db.execute("PRAGMA idb.synchronous").fetchone()[0], 2)
            before = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            initial = db.execute("SELECT COUNT(*) FROM idb.identity_journeys").fetchone()[0]
            try:
                db.execute("BEGIN IMMEDIATE")
                db.execute("UPDATE sessions SET revoked=1 WHERE id_hash=?", (self.state.digest(self.sid),))
                db.execute("INSERT INTO idb.identity_journeys(id,identity_id,label) VALUES(?,?,?)",
                           ("rollback-probe", "qa-alice", "temporary"))
                raise RuntimeError("simulated failure before commit")
            except RuntimeError:
                db.rollback()
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], before)
            self.assertEqual(db.execute("SELECT revoked FROM sessions WHERE id_hash=?",
                                        (self.state.digest(self.sid),)).fetchone(), (0,))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM idb.identity_journeys").fetchone()[0], initial)


if __name__ == "__main__":
    unittest.main()
