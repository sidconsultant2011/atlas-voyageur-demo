"""SEC-01 AC-13 — HTTP SQLite error boundary on fictional localhost only.

Injected Python exceptions are not filesystem faults or native COMMIT failures.
"""
import http.client
import json
import sqlite3
import threading
import unittest

from local_http_facade import ALLOWED_ORIGIN, LocalState, create_server
from sqlite_ac08 import SQLitePreconditionError


class FakeState(LocalState):
    def __init__(self):
        super().__init__(clock=lambda: 1000.0)
        self.inject = None
        self.calls = []
        self.sid, self.csrf = self.create()

    def _fault(self, method):
        self.calls.append(method)
        if self.inject == method:
            raise sqlite3.OperationalError("secret-SQL-/private/path-cookie=hidden")
        if self.inject == method + ":precondition":
            raise SQLitePreconditionError("secret-AC08-/private/path")
        if self.inject == method + ":commit":
            # Only a synthetic exception at the application return boundary.
            # No assertion of persistence, rollback or native COMMIT result.
            raise sqlite3.DatabaseError("COMMIT outcome unknown /private/path")

    def create(self):
        self._fault("create") if hasattr(self, "calls") else None
        return super().create()

    def check(self, sid, csrf=None, write=False):
        self._fault("check")
        return super().check(sid, csrf, write)

    def revoke(self, sid, csrf):
        self._fault("revoke")
        return super().revoke(sid, csrf)

    def create_journey(self, sid):
        self._fault("create_journey")
        return super().create_journey(sid)

    def journey(self, sid, jid):
        self._fault("journey")
        return super().journey(sid, jid)

    def update_journey(self, sid, jid, label):
        self._fault("update_journey")
        return {"version": 2}

    def remove_journey(self, sid, jid):
        self._fault("remove_journey")
        return super().remove_journey(sid, jid)


class FakeBridge:
    def __init__(self):
        self.calls = []
        self.inject = None

    def bind_state(self, state):
        self.state = state

    def _apply(self, name, *args):
        self.calls.append(name)
        if self.inject == name:
            raise sqlite3.OperationalError("SQL secret-token")
        if self.inject == name + ":precondition":
            raise SQLitePreconditionError("secret-AC08")
        if self.inject == name + ":commit":
            raise sqlite3.DatabaseError("COMMIT uncertain secret")
        if name == "create":
            return "fictional-journey"
        if name == "read":
            return {"label": "fictif", "version": 1}
        return True

    def create(self, *args): return self._apply("create", *args)
    def read(self, *args): return self._apply("read", *args)
    def update(self, *args): return self._apply("update", *args)
    def delete(self, *args): return self._apply("delete", *args)
    def revoke_binding(self, *args): return self._apply("revoke_binding", *args)


class AC13HTTPErrorBoundary(unittest.TestCase):
    def setUp(self):
        self.state = FakeState()
        self.bridge = FakeBridge()
        self.server = create_server(state=self.state, identity_bridge=self.bridge)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)

    def request(self, method, route, body=None, csrf=True, origin=ALLOWED_ORIGIN):
        headers = {"Origin": origin, "Cookie": "atlas_qa=" + self.state.sid}
        if csrf:
            headers["X-CSRF-Token"] = self.state.csrf
        if body is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(body, separators=(",", ":"))
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            conn.request(method, route, body=body, headers=headers)
            response = conn.getresponse()
            status = response.status
            hdr = dict(response.getheaders())
            raw = response.read()
            return status, hdr, json.loads(raw) if raw else None, raw.decode()
        finally:
            conn.close()

    def assert_503(self, result, code):
        status, headers, body, raw = result
        self.assertEqual(status, 503)
        self.assertEqual(body, {"status": "unavailable", "errors": [{"code": code}]})
        for secret in ("/private/path", "secret", "COMMIT", "rolled_back", "revoked", "journeyId"):
            self.assertNotIn(secret, raw)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("frame-ancestors", headers["Content-Security-Policy"])
        self.assertNotIn("Set-Cookie", headers)

    def test_precondition_rejections_across_all_http_verbs(self):
        cases = [
            ("create", "POST", "/api/v1/qa/session", None),
            ("revoke", "POST", "/api/v1/qa/session/revoke", None),
            ("check", "GET", "/api/v1/qa/state", None),
            ("check", "POST", "/api/v1/qa/echo", {"message": "ok"}),
            ("check", "DELETE", "/api/v1/qa/journeys/id", None),
            ("create_journey", "POST", "/api/v1/qa/journeys", {}),
        ]
        for operation, method, route, body in cases:
            with self.subTest(operation=operation, method=method):
                self.state.inject = operation + ":precondition"
                self.assert_503(self.request(method, route, body), "STORAGE_PRECONDITION_FAILED")
                self.state.inject = None

    def test_sqlite_errors_on_all_protected_routes(self):
        cases = [
            ("create", "POST", "/api/v1/qa/session", None),
            ("revoke", "POST", "/api/v1/qa/session/revoke", None),
            ("check", "GET", "/api/v1/qa/state", None),
            ("check", "POST", "/api/v1/qa/echo", {"message": "ok"}),
            ("check", "DELETE", "/api/v1/qa/journeys/id", None),
            ("create_journey", "POST", "/api/v1/qa/journeys", {}),
        ]
        for operation, method, route, body in cases:
            with self.subTest(operation=operation):
                self.state.inject = operation
                self.assert_503(self.request(method, route, body), "STORAGE_UNAVAILABLE")
                self.state.inject = None

    def test_check_failure_prevents_bridge_delegation(self):
        self.state.inject = "check"
        self.assert_503(self.request("POST", "/api/v1/qa/journeys", {}),
                        "STORAGE_UNAVAILABLE")
        self.assert_503(self.request("GET", "/api/v1/qa/journeys/id"),
                        "STORAGE_UNAVAILABLE")
        self.assert_503(self.request("DELETE", "/api/v1/qa/journeys/id"),
                        "STORAGE_UNAVAILABLE")
        self.assertEqual(self.bridge.calls, [])

    def test_bridge_errors_on_mutation_and_read(self):
        for action, method, route, body in (
            ("create", "POST", "/api/v1/qa/journeys", {}),
            ("read", "GET", "/api/v1/qa/journeys/id", None),
            ("read", "POST", "/api/v1/qa/journeys/id/label", {"message": "x"}),
            ("update", "POST", "/api/v1/qa/journeys/id/label", {"message": "x"}),
            ("delete", "DELETE", "/api/v1/qa/journeys/id", None),
        ):
            with self.subTest(action=action, method=method):
                self.bridge.inject = action
                self.assert_503(self.request(method, route, body), "STORAGE_UNAVAILABLE")
                self.bridge.inject = None

    def test_commit_outcome_not_asserted_and_no_automatic_retry(self):
        for op, route, body in (
            ("create", "/api/v1/qa/session", None),
            ("revoke", "/api/v1/qa/session/revoke", None),
            ("create_journey", "/api/v1/qa/journeys", {}),
        ):
            with self.subTest(op=op):
                self.state.inject = op + ":commit"
                before = len(self.state.calls)
                self.assert_503(self.request("POST", route, body), "STORAGE_UNAVAILABLE")
                self.assertEqual(self.state.calls[before:].count(op), 1)
                self.state.inject = None

    def test_business_refusals_preserved(self):
        result = self.request("POST", "/api/v1/qa/session/revoke", csrf=False)
        self.assertEqual(result[0], 403)
        result = self.request("GET", "/api/v1/qa/state", origin="http://evil.invalid")
        self.assertEqual(result[0], 403)
        result = self.request("GET", "/api/v1/qa/no-such-route")
        self.assertEqual(result[0], 404)
        result = self.request("POST", "/api/v1/qa/journeys", {"bad": "payload"})
        self.assertEqual(result[0], 400)
        self.assertEqual(self.request("GET", "/api/v1/qa/state")[0], 200)

    def test_memory_state_still_works_without_bridge(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)
        self.server = create_server()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        status, headers, data, _ = self.request("POST", "/api/v1/qa/session")
        self.assertEqual(status, 201)
        self.assertIn("Set-Cookie", headers)
        self.assertIn("csrfToken", data)


if __name__ == "__main__":
    unittest.main()
