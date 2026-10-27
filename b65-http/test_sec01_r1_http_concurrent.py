"""SEC-01 R1 : ordre déterministe HTTP/SQLite sur deux bases fictives.

Complète les entrelacements SQL de test_sec01_r1_complements.py :
- mutation HTTP déjà sous BEGIN IMMEDIATE avant révocation ;
- révocation HTTP déjà sous BEGIN IMMEDIATE avant deux mutations HTTP.
Aucune modification du code applicatif, de C03, du moteur ou du workflow.
"""
import http.client
import json
import sqlite3
import threading
import unittest

from test_sec01_r1_complements import R1Complements
from persistent_sessions import PersistentSessionState
from local_identity_bridge import LocalIdentityBridge
from local_http_facade import create_server, ALLOWED_ORIGIN


class BarrierState(PersistentSessionState):
    """Observation de l'entrée effective sous BEGIN IMMEDIATE via _authorize.

    Signalisation de test uniquement : aucune transaction ouverte ou validée
    en dehors des méthodes de référence, aucun changement de retour SQL.
    """
    def __init__(self, *args, **kwargs):
        self.hold_kind = None
        self.entered = threading.Event()
        self.release = threading.Event()
        self.check_arrivals = threading.Condition()
        self.check_count = 0
        self.context = threading.local()
        super().__init__(*args, **kwargs)

    def check(self, sid, csrf=None, write=False):
        if write:
            with self.check_arrivals:
                self.check_count += 1
                self.check_arrivals.notify_all()
        return super().check(sid, csrf, write)

    def revoke(self, sid, csrf):
        self.context.revoke = True
        try:
            return super().revoke(sid, csrf)
        finally:
            self.context.revoke = False

    def _authorize(self, c, sid, csrf=None, write=False):
        response = super()._authorize(c, sid, csrf, write)
        kind = "revoke" if getattr(self.context, "revoke", False) else (
            "mutation" if not write and threading.current_thread() is not threading.main_thread() else None)
        if response[0] == 200 and kind == self.hold_kind:
            # BEGIN IMMEDIATE est déjà acquis et _authorize a lu la session.
            self.entered.set()
            if not self.release.wait(10):
                raise AssertionError("Barrière SQL non libérée")
        return response

    def wait_for_checks(self, count):
        with self.check_arrivals:
            return self.check_arrivals.wait_for(lambda: self.check_count >= count, timeout=10)


class R1HTTPRevocationConcurrency(R1Complements):
    """Hérite des fixtures locales, sans réexécuter ses tests historiques."""
    __test__ = False

    def setUp(self):
        super().setUp()
        # Base sessions et pont restent identiques ; remplacer seulement
        # l'objet de contrôle par une sous-classe sans modification SQL.
        self.state = BarrierState(self.path, clock=lambda: self.now[0], rate_limit=1000)
        self.bridge = LocalIdentityBridge(self.identities)
        self.bridge.bind_state(self.state)
        self.bridge.bind_fixture(self.sid, self.identities.open_session("qa-alice"))
        self.server = create_server(state=self.state, identity_bridge=self.bridge)
        self.serving = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.serving.start()

    def tearDown(self):
        self.state.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.serving.join(5)
        super().tearDown()

    def http(self, method, route, body=None):
        headers = {"Origin": ALLOWED_ORIGIN,
                   "Cookie": "atlas_qa=" + self.sid,
                   "X-CSRF-Token": self.csrf}
        raw = None
        if body is not None:
            raw = json.dumps(body)
            headers["Content-Type"] = "application/json"
        c = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=12)
        try:
            c.request(method, route, body=raw, headers=headers)
            r = c.getresponse()
            payload = json.loads(r.read())
            return r.status, payload
        finally:
            c.close()

    def snapshot(self):
        sessions = self.read_sql(self.path,
            "SELECT revoked FROM sessions WHERE id_hash=?", (self.state.digest(self.sid),))
        identities = self.read_sql(self.identity_path,
            "SELECT id,label FROM identity_journeys ORDER BY id")
        return sessions, identities

    def assert_writer_locked(self):
        with sqlite3.connect(self.path, timeout=0) as probe:
            with self.assertRaises(sqlite3.OperationalError) as error:
                probe.execute("BEGIN IMMEDIATE")
            self.assertIn("locked", str(error.exception).lower())

    def launch(self, name, method, route, body, out):
        def worker():
            try:
                out[name] = self.http(method, route, body)
            except Exception as exc:
                out[name] = exc
        t = threading.Thread(target=worker, name=name)
        t.start()
        return t

    def assert_responses(self, threads, out):
        for thread in threads:
            thread.join(12)
            self.assertFalse(thread.is_alive(), "Requête HTTP encore active")
        for response in out.values():
            if isinstance(response, Exception):
                raise response

    def test_http_mutation_locked_before_revocation_commit(self):
        """Mutation engagée sous verrou : preuve SQL avant COMMIT révocation."""
        self.state.hold_kind = "mutation"
        out = {}
        writer = self.launch("writer", "POST", "/api/v1/qa/journeys", {}, out)
        revoker = None
        try:
            self.assertTrue(self.state.entered.wait(10),
                            "Mutation non entrée sous BEGIN IMMEDIATE")
            self.assert_writer_locked()
            revoker = self.launch("revoker", "POST",
                                  "/api/v1/qa/session/revoke", None, out)
            # Le révocateur n'a pas encore le verrou ; état visible non révoqué.
            self.assertEqual(self.snapshot()[0], [(0,)])
        finally:
            self.state.release.set()
            threads = [writer] + ([revoker] if revoker else [])
            self.assert_responses(threads, out)
        self.assertEqual(out["writer"][0], 201)
        self.assertEqual(out["revoker"][0], 200)
        jid = out["writer"][1]["journeyId"]
        self.assertEqual(self.snapshot()[0], [(1,)])
        self.assertEqual(self.read_sql(self.identity_path,
             "SELECT label FROM identity_journeys WHERE id=?", (jid,)),
             [("Parcours fictif",)])
        self.assertEqual(self.http("POST", "/api/v1/qa/journeys", {})[0], 401)

    def test_http_revoke_locked_before_two_mutations_and_new_connection(self):
        """Deux demandes HTTP arrivées alors que le COMMIT révocation est bloqué."""
        self.state.hold_kind = "revoke"
        out = {}
        revoker = self.launch("revoker", "POST",
                              "/api/v1/qa/session/revoke", None, out)
        writers = []
        try:
            self.assertTrue(self.state.entered.wait(10),
                            "Révocation non entrée sous BEGIN IMMEDIATE")
            self.assert_writer_locked()
            before = self.snapshot()
            self.assertEqual(before[0], [(0,)])
            writers = [
                self.launch("writer-1", "POST", "/api/v1/qa/journeys", {}, out),
                self.launch("writer-2", "POST", "/api/v1/qa/journeys", {}, out)]
            self.assertTrue(self.state.wait_for_checks(2),
                            "Les deux requêtes n'ont pas atteint state.check")
            # Le verrou exclusif de révocation est toujours détenu.
            self.assert_writer_locked()
            self.assertEqual(self.snapshot(), before)
        finally:
            self.state.release.set()
            self.assert_responses([revoker] + writers, out)
        self.assertEqual(out["revoker"][0], 200)
        self.assertEqual(out["writer-1"][0], 401)
        self.assertEqual(out["writer-2"][0], 401)
        self.assertEqual(self.snapshot(), ([(1,)], before[1]))
        # http() construit une connexion HTTP distincte à chaque appel.
        self.assertEqual(self.http("POST", "/api/v1/qa/journeys", {})[0], 401)
        self.assertEqual(self.snapshot(), ([(1,)], before[1]))


# unittest charge les méthodes test_* de la classe héritée ; neutraliser
# les cas historiques déjà découverts dans test_sec01_r1_complements.py.
for _name in list(vars(R1Complements)):
    if _name.startswith("test_"):
        setattr(R1HTTPRevocationConcurrency, _name, None)


if __name__ == "__main__":
    unittest.main()
