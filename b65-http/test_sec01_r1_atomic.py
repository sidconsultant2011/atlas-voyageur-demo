"""SEC-01 R1: deterministic SQLite lock ordering, HTTP-after-revoke and cross-process QA.
No public services, real credentials or external network.
"""
import multiprocessing
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from persistent_sessions import PersistentSessionState


def _child_mutation(path, sid, jid, begin, output):
    state = PersistentSessionState(path, rate_limit=1000)
    begin.wait()
    output.put(state.update_journey(sid, jid, "child"))


class R1AtomicSQLiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "r1.sqlite")
        self.now = [1000.0]
        self.state = PersistentSessionState(self.path, clock=lambda: self.now[0], rate_limit=1000)
        self.sid, self.csrf = self.state.create()
        self.jid = self.state.create_journey(self.sid)

    def tearDown(self):
        self.temp.cleanup()

    def sql(self, query, args=()):
        with sqlite3.connect(self.path) as db:
            return db.execute(query, args).fetchall()

    def test_revocation_commit_blocks_all_subsequent_mutations(self):
        self.assertEqual(self.state.revoke(self.sid, self.csrf)[0], 200)
        self.assertEqual(self.sql("SELECT revoked FROM sessions WHERE id_hash=?",
                                  (self.state.digest(self.sid),)), [(1,)])
        before = self.sql("SELECT id,label,version FROM journeys")
        self.assertIsNone(self.state.create_journey(self.sid))
        self.assertIsNone(self.state.update_journey(self.sid, self.jid, "forbidden"))
        self.assertFalse(self.state.remove_journey(self.sid, self.jid))
        self.assertEqual(before, self.sql("SELECT id,label,version FROM journeys"))

    def test_cross_owner_write_cannot_bypass_ownership(self):
        other, other_csrf = self.state.create()
        self.assertIsNone(self.state.update_journey(other, self.jid, "hijack"))
        self.assertFalse(self.state.remove_journey(other, self.jid))
        self.assertEqual(self.state.journey(self.sid, self.jid)["label"], "Parcours fictif")

    def test_mutation_transaction_finishes_before_revoke_commit(self):
        entered = threading.Event()
        release = threading.Event()
        class PausedState(PersistentSessionState):
            def _authorize(inner, conn, sid, csrf=None, write=False):
                result = super()._authorize(conn, sid, csrf, write)
                if result[0] == 200 and threading.current_thread().name == "mutation":
                    entered.set()
                    if not release.wait(5):
                        raise TimeoutError("Synchronization failure")
                return result

        state = PausedState(self.path, clock=lambda: self.now[0], rate_limit=1000)
        outcomes = {}
        def mutate():
            outcomes["mutation"] = state.update_journey(self.sid, self.jid, "before-revoke")
        def revoke():
            outcomes["revoke"] = self.state.revoke(self.sid, self.csrf)
        writer = threading.Thread(target=mutate, name="mutation")
        writer.start()
        self.assertTrue(entered.wait(5))
        revoker = threading.Thread(target=revoke, name="revoker")
        revoker.start()
        self.assertNotIn("revoke", outcomes)
        release.set()
        writer.join(8)
        revoker.join(8)
        self.assertFalse(writer.is_alive())
        self.assertFalse(revoker.is_alive())
        self.assertEqual(outcomes["mutation"]["label"], "before-revoke")
        self.assertEqual(outcomes["revoke"][0], 200)
        self.assertEqual(self.sql("SELECT label FROM journeys WHERE id=?", (self.jid,)),
                         [("before-revoke",)])
        self.assertIsNone(state.update_journey(self.sid, self.jid, "too-late"))

    def test_revoker_serializes_before_second_connection_mutation(self):
        self.assertEqual(self.state.revoke(self.sid, self.csrf)[0], 200)
        reopened = PersistentSessionState(self.path, clock=lambda: self.now[0], rate_limit=1000)
        self.assertIsNone(reopened.update_journey(self.sid, self.jid, "too-late"))
        self.assertFalse(reopened.remove_journey(self.sid, self.jid))

    def test_other_process_cannot_mutate_after_committed_revocation(self):
        context = multiprocessing.get_context("spawn")
        gate = context.Event()
        output = context.Queue()
        process = context.Process(target=_child_mutation, args=(self.path, self.sid, self.jid, gate, output))
        process.start()
        try:
            self.assertEqual(self.state.revoke(self.sid, self.csrf)[0], 200)
            gate.set()
            self.assertIsNone(output.get(timeout=12))
            process.join(12)
            self.assertEqual(process.exitcode, 0)
            self.assertEqual(self.sql("SELECT label FROM journeys WHERE id=?", (self.jid,)),
                             [("Parcours fictif",)])
        finally:
            gate.set()
            if process.is_alive():
                process.terminate()
                process.join(5)


if __name__ == "__main__":
    unittest.main()
