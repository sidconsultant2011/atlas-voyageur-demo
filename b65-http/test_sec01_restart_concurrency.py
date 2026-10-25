"""SEC-01 complementary QA: integrated SQLite restart and revocation concurrency.
Offline localhost only. No production atomicity claim.
"""
import concurrent.futures
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from fictional_identities import FictionalIdentityStore
from local_identity_bridge import LocalIdentityBridge
from local_http_facade import ALLOWED_ORIGIN, create_server
from persistent_sessions import PersistentSessionState


class RestartAndRevocationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = [1000.0]
        self.session_path = self.root / "sessions.sqlite"
        self.identity_path = self.root / "identities.sqlite"
        self.identities = FictionalIdentityStore(str(self.identity_path), clock=lambda: self.now[0])
        self.identities.add_fixture_identity("qa-alice")
        self.state = PersistentSessionState(str(self.session_path), clock=lambda: self.now[0], rate_limit=1000)
        self.bridge = LocalIdentityBridge(self.identities)
        self.start(self.state, self.bridge)

    def start(self, state, bridge):
        self.server = create_server(state=state, identity_bridge=bridge)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=5)
        self.assertFalse(self.worker.is_alive())

    def tearDown(self):
        self.stop()
        self.tmp.cleanup()

    def request(self, method, path, sid=None, csrf=None, payload=None):
        headers = {"Origin": ALLOWED_ORIGIN}
        if sid:
            headers["Cookie"] = "atlas_qa=" + sid
        if csrf:
            headers["X-CSRF-Token"] = csrf
        if payload is not None:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(payload)
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=8)
        try:
            conn.request(method, path, body=payload, headers=headers)
            response = conn.getresponse()
            data = json.loads(response.read() or b"{}")
            return response.status, data
        finally:
            conn.close()

    def bound_session(self):
        sid, csrf = self.state.create()
        token = self.identities.open_session("qa-alice")
        self.bridge.bind_fixture(sid, token)
        return sid, csrf, token

    def restart(self):
        self.stop()
        self.state = PersistentSessionState(str(self.session_path), clock=lambda: self.now[0], rate_limit=1000)
        self.identities = FictionalIdentityStore(str(self.identity_path), clock=lambda: self.now[0])
        self.bridge = LocalIdentityBridge(self.identities)
        self.start(self.state, self.bridge)

    def test_integrated_restart_requires_explicit_rebinding(self):
        sid, csrf, token = self.bound_session()
        status, result = self.request("POST", "/api/v1/qa/journeys", sid, csrf, {})
        self.assertEqual(status, 201)
        jid = result["journeyId"]
        self.restart()
        self.assertTrue(self.state.is_active_session(sid))
        self.assertEqual(self.request("GET", "/api/v1/qa/journeys/" + jid, sid)[0], 404)
        self.assertEqual(self.request("POST", "/api/v1/qa/journeys", sid, csrf, {})[0], 401)
        self.bridge.bind_fixture(sid, token)
        self.assertEqual(self.request("GET", "/api/v1/qa/journeys/" + jid, sid)[0], 200)

    def test_integrated_revocation_survives_restart(self):
        sid, csrf, token = self.bound_session()
        self.assertEqual(self.request("POST", "/api/v1/qa/session/revoke", sid, csrf)[0], 200)
        self.restart()
        self.assertFalse(self.state.is_active_session(sid))
        self.assertEqual(self.request("POST", "/api/v1/qa/journeys", sid, csrf, {})[0], 401)
        with self.assertRaises(PermissionError):
            self.bridge.bind_fixture(sid, token)

    def test_integrated_expiry_survives_restart(self):
        sid, csrf, token = self.bound_session()
        self.now[0] += 901
        self.restart()
        self.assertFalse(self.state.is_active_session(sid))
        self.assertEqual(self.request("POST", "/api/v1/qa/journeys", sid, csrf, {})[0], 401)
        with self.assertRaises(PermissionError):
            self.bridge.bind_fixture(sid, token)

    def test_parallel_revocation_and_protected_requests_fail_closed_after_completion(self):
        sid, csrf, _ = self.bound_session()
        status, data = self.request("POST", "/api/v1/qa/journeys", sid, csrf, {})
        self.assertEqual(status, 201)
        jid = data["journeyId"]
        path = "/api/v1/qa/journeys/" + jid
        gate = threading.Event()

        def protected_worker(i):
            gate.wait(timeout=5)
            if i % 2:
                return self.request("POST", path + "/label", sid, csrf, {"message": "race"})[0]
            return self.request("GET", path, sid)[0]

        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            requests = [pool.submit(protected_worker, i) for i in range(20)]
            gate.set()
            revocation = self.request("POST", "/api/v1/qa/session/revoke", sid, csrf)[0]
            statuses = [future.result(timeout=10) for future in requests]
        self.assertEqual(revocation, 200)
        self.assertTrue(all(s in (200, 401, 404) for s in statuses), statuses)
        # Assertions concern requests initiated AFTER revoke returned, not
        # operations already in flight at the revocation linearization point.
        for _ in range(5):
            self.assertEqual(self.request("GET", path, sid)[0], 401)
            self.assertEqual(self.request("POST", path + "/label", sid, csrf, {"message": "blocked"})[0], 401)
            self.assertEqual(self.request("DELETE", path, sid, csrf)[0], 401)
            self.assertEqual(self.request("POST", "/api/v1/qa/journeys", sid, csrf, {})[0], 401)


if __name__ == "__main__":
    unittest.main()
