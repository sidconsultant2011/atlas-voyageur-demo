"""AC-08 — contrats DELETE/FULL et échec sécurisé sur fixtures fictives."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fictional_identities import FictionalIdentityStore
from persistent_sessions import PersistentSessionState
from local_identity_bridge import LocalIdentityBridge
from sqlite_ac08 import SQLitePreconditionError, open_qa_database, verify_attached


class AC08SQLitePreconditions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="atlas-ac08-")
        root = Path(self.tmp.name)
        self.sessions = root / "sessions.sqlite"
        self.identities = root / "identities.sqlite"

    def tearDown(self):
        self.tmp.cleanup()

    def initial(self):
        state = PersistentSessionState(self.sessions, rate_limit=1000, clock=lambda: 1000.)
        identities = FictionalIdentityStore(self.identities, clock=lambda: 1000.)
        identities.add_fixture_identity("qa-alice")
        bridge = LocalIdentityBridge(identities)
        bridge.bind_state(state)
        sid, csrf = state.create()
        bridge.bind_fixture(sid, identities.open_session("qa-alice"))
        return state, identities, bridge, sid, csrf

    def test_new_fixtures_and_each_connection_delete_full(self):
        state, identities, bridge, sid, _ = self.initial()
        for connect, foreign_keys in ((state.connect, False), (identities._db, True)):
            for _ in range(2):
                c = connect()
                try:
                    self.assertEqual(c.execute("PRAGMA main.journal_mode").fetchone(), ("delete",))
                    self.assertEqual(c.execute("PRAGMA main.synchronous").fetchone(), (2,))
                    if foreign_keys:
                        self.assertEqual(c.execute("PRAGMA foreign_keys").fetchone(), (1,))
                    else:
                        self.assertEqual(c.execute("PRAGMA busy_timeout").fetchone(), (10000,))
                finally:
                    c.close()
        self.assertIsNotNone(bridge.create(sid))

    def test_attach_two_files_prior_to_begin_immediate(self):
        state, identities, bridge, sid, _ = self.initial()
        with state.connect() as c:
            c.execute("ATTACH DATABASE ? AS identity_db", (str(self.identities),))
            verify_attached(c, self.sessions, self.identities)
            for schema in ("main", "identity_db"):
                self.assertEqual(c.execute("PRAGMA "+schema+".journal_mode").fetchone(), ("delete",))
                self.assertEqual(c.execute("PRAGMA "+schema+".synchronous").fetchone(), (2,))
            c.execute("BEGIN IMMEDIATE")
            c.rollback()
        self.assertIsNotNone(bridge.create(sid))

    def test_existing_wal_sessions_refused_without_conversion(self):
        state, identities, bridge, sid, _ = self.initial()
        with sqlite3.connect(self.sessions) as c:
            self.assertEqual(c.execute("PRAGMA journal_mode=WAL").fetchone(), ("wal",))
        with self.assertRaisesRegex(SQLitePreconditionError, "JOURNAL_INCOMPATIBLE"):
            state.connect()
        with self.assertRaisesRegex(SQLitePreconditionError, "JOURNAL_INCOMPATIBLE"):
            state.revoke(sid, "fictional")
        with sqlite3.connect(self.sessions) as c:
            self.assertEqual(c.execute("PRAGMA journal_mode").fetchone(), ("wal",))
            self.assertEqual(c.execute("SELECT revoked FROM sessions WHERE id_hash=?",
                                       (state.digest(sid),)).fetchone(), (0,))

    def test_existing_wal_identities_refused_and_no_business_mutation(self):
        state, identities, bridge, sid, _ = self.initial()
        with sqlite3.connect(self.identities) as c:
            self.assertEqual(c.execute("PRAGMA journal_mode=WAL").fetchone(), ("wal",))
        with self.assertRaisesRegex(SQLitePreconditionError, "JOURNAL_INCOMPATIBLE"):
            identities._db()
        with self.assertRaisesRegex(SQLitePreconditionError, "JOURNAL_INCOMPATIBLE"):
            bridge.create(sid)
        with sqlite3.connect(self.identities) as c:
            self.assertEqual(c.execute("PRAGMA journal_mode").fetchone(), ("wal",))
            self.assertEqual(c.execute("SELECT COUNT(*) FROM identity_journeys").fetchone(), (0,))

    def test_missing_fixture_after_creation_never_recreated(self):
        state, identities, bridge, sid, _ = self.initial()
        self.identities.unlink()
        with self.assertRaisesRegex(SQLitePreconditionError, "DATABASE_MISSING"):
            identities._db()
        with self.assertRaisesRegex(SQLitePreconditionError, "DATABASE_MISSING"):
            bridge.create(sid)
        self.assertFalse(self.identities.exists())

    def test_invalid_memory_and_uri_rejected(self):
        for value in (":memory:", "file:fixture.sqlite?mode=memory"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(SQLitePreconditionError, "INVALID_DISK_PATH"):
                    open_qa_database(value, initialize=True)

    def test_attachment_wrong_alias_or_missing_file_rejected(self):
        state, identities, bridge, sid, _ = self.initial()
        with state.connect() as c:
            c.execute("ATTACH DATABASE ? AS other", (str(self.identities),))
            with self.assertRaisesRegex(SQLitePreconditionError, "ATTACHMENT_MISMATCH"):
                verify_attached(c, self.sessions, self.identities)
        self.assertEqual(bridge.read(sid, "missing"), None)

    def test_reopen_existing_compatible_fixture(self):
        state, identities, bridge, sid, csrf = self.initial()
        state2 = PersistentSessionState(self.sessions, clock=lambda: 1000., rate_limit=1000)
        identities2 = FictionalIdentityStore(self.identities, clock=lambda: 1000.)
        self.assertTrue(state2.is_active_session(sid))
        self.assertEqual(identities2.whoami(identities.open_session("qa-alice")), "qa-alice")
        self.assertEqual(state2.revoke(sid, csrf)[0], 200)


if __name__ == "__main__":
    unittest.main()
