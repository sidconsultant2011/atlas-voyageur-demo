"""Loopback HTTP security checks: no outside network or providers."""
import http.client, json, threading, unittest
from http.cookies import SimpleCookie
from local_http_facade import create_server, ALLOWED_ORIGIN

class LocalHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=create_server()
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
        cls.port=cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join(timeout=5)
    def request(self,method,path,body=None,headers=None):
        con=http.client.HTTPConnection("127.0.0.1",self.port,timeout=5)
        con.request(method,path,body=body,headers=headers or {})
        r=con.getresponse()
        result=(r.status,dict(r.getheaders()),json.loads(r.read() or b"{}"))
        con.close();return result
    def session(self):
        status,headers,data=self.request("POST","/api/v1/qa/session",headers={"Origin":ALLOWED_ORIGIN,"Content-Length":"0"})
        self.assertEqual(status,201)
        cookie=headers["Set-Cookie"].split(";",1)[0]
        return cookie,data["csrfToken"]
    def test_only_loopback_bind(self):
        with self.assertRaises(ValueError):create_server(host="0.0.0.0")
    def test_missing_auth_denied(self):
        self.assertEqual(self.request("GET","/api/v1/qa/state")[0],401)
    def test_origin_denied(self):
        self.assertEqual(self.request("POST","/api/v1/qa/session",headers={"Origin":"https://attacker.example","Content-Length":"0"})[0],403)
    def test_session_cookie_flags(self):
        _,h,_=self.request("POST","/api/v1/qa/session",headers={"Origin":ALLOWED_ORIGIN,"Content-Length":"0"})
        self.assertIn("HttpOnly",h["Set-Cookie"]);self.assertIn("SameSite=Strict",h["Set-Cookie"])
    def test_csrf_missing_rejected(self):
        cookie,_=self.session()
        st,_,_=self.request("POST","/api/v1/qa/echo",body='{"message":"a"}',headers={"Origin":ALLOWED_ORIGIN,"Cookie":cookie,"Content-Type":"application/json"})
        self.assertEqual(st,403)
    def test_csrf_invalid_rejected(self):
        cookie,_=self.session()
        st,_,_=self.request("POST","/api/v1/qa/echo",body='{"message":"a"}',headers={"Cookie":cookie,"X-CSRF-Token":"invalid","Content-Type":"application/json"})
        self.assertEqual(st,403)
    def test_session_isolation(self):
        a,_=self.session();b,_=self.session()
        # A session cookie cannot be guessed or substituted with a fake one.
        self.assertEqual(self.request("GET","/api/v1/qa/state",headers={"Cookie":"atlas_qa=forged"})[0],401)
        self.assertEqual(self.request("GET","/api/v1/qa/state",headers={"Cookie":a})[0],200)
        self.assertEqual(self.request("GET","/api/v1/qa/state",headers={"Cookie":b})[0],200)
    def test_allowed_write(self):
        cookie,csrf=self.session()
        st,_,data=self.request("POST","/api/v1/qa/echo",body='{"message":"ok"}',headers={"Origin":ALLOWED_ORIGIN,"Cookie":cookie,"X-CSRF-Token":csrf,"Content-Type":"application/json"})
        self.assertEqual(st,200);self.assertEqual(data["data"]["message"],"ok")
    def test_rate_limit(self):
        cookie,_=self.session()
        headers={"Cookie":cookie}
        statuses=[self.request("GET","/api/v1/qa/state",headers=headers)[0] for _ in range(10)]
        self.assertIn(429,statuses);self.assertEqual(statuses[:8],[200]*8)
    def test_cors_preflight(self):
        st,h,_=self.request("OPTIONS","/api/v1/qa/echo",headers={"Origin":ALLOWED_ORIGIN,"Access-Control-Request-Method":"POST"})
        self.assertEqual(st,204);self.assertEqual(h["Access-Control-Allow-Origin"],ALLOWED_ORIGIN)
    def test_unknown_route_denied(self):
        self.assertEqual(self.request("GET","/api/v1/qa/external")[0],404)
    def test_reject_invalid_content_type(self):
        cookie,csrf=self.session()
        self.assertEqual(self.request("POST","/api/v1/qa/echo",body="{}",headers={"Cookie":cookie,"X-CSRF-Token":csrf,"Content-Type":"text/plain"})[0],415)

if __name__=="__main__":unittest.main()
