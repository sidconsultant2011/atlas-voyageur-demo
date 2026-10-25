"""B6.5 SEC-01 identity binding end-to-end over localhost only."""
import http.client,json,tempfile,threading,unittest
from pathlib import Path
from fictional_identities import FictionalIdentityStore
from local_identity_bridge import LocalIdentityBridge
from local_http_facade import create_server,ALLOWED_ORIGIN

class IdentityBridgeHTTPTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.identities=FictionalIdentityStore(str(Path(self.temp.name)/"identity.sqlite"))
  for name in ("qa-alice","qa-bob"):self.identities.add_fixture_identity(name)
  self.bridge=LocalIdentityBridge(self.identities)
  self.server=create_server(identity_bridge=self.bridge)
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join(timeout=5);self.temp.cleanup()
 def req(self,method,path,cookie=None,csrf=None,payload=None):
  h={"Origin":ALLOWED_ORIGIN}
  if cookie:h["Cookie"]=cookie
  if csrf:h["X-CSRF-Token"]=csrf
  if payload is not None:
   h["Content-Type"]="application/json"
   payload=json.dumps(payload)
  if method=="POST" and payload is None:payload=""
  conn=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=4)
  conn.request(method,path,body=payload,headers=h)
  r=conn.getresponse();headers=dict(r.getheaders());raw=r.read();conn.close()
  return r.status,headers,json.loads(raw or b"{}")
 def session(self,identity=None):
  status,h,d=self.req("POST","/api/v1/qa/session")
  self.assertEqual(status,201)
  cookie=h["Set-Cookie"].split(";",1)[0];csrf=d["csrfToken"]
  if identity:self.bridge.bind_fixture(cookie.split("=",1)[1],self.identities.open_session(identity))
  return cookie,csrf
 def create(self,cookie,csrf):
  return self.req("POST","/api/v1/qa/journeys",cookie,csrf,{})
 def test_bound_identity_creates_and_accesses_own_journey(self):
  cookie,csrf=self.session("qa-alice")
  status,_,data=self.create(cookie,csrf);self.assertEqual(status,201)
  jid=data["journeyId"]
  self.assertEqual(self.req("GET","/api/v1/qa/journeys/"+jid,cookie)[0],200)
 def test_unbound_cookie_cannot_create_or_read(self):
  bound,csrf=self.session("qa-alice");jid=self.create(bound,csrf)[2]["journeyId"]
  unbound,uc=self.session()
  self.assertEqual(self.create(unbound,uc)[0],401)
  self.assertEqual(self.req("GET","/api/v1/qa/journeys/"+jid,unbound)[0],404)
 def test_cross_identity_read_update_delete_denied(self):
  a,ac=self.session("qa-alice");b,bc=self.session("qa-bob")
  jid=self.create(a,ac)[2]["journeyId"];url="/api/v1/qa/journeys/"+jid
  self.assertEqual(self.req("GET",url,b)[0],404)
  self.assertEqual(self.req("POST",url+"/label",b,bc,{"message":"stolen"})[0],404)
  self.assertEqual(self.req("DELETE",url,b,bc)[0],404)
  self.assertEqual(self.req("GET",url,a)[2]["data"]["label"],"Parcours fictif")
 def test_owner_edit_delete_allowed(self):
  a,ac=self.session("qa-alice");jid=self.create(a,ac)[2]["journeyId"];url="/api/v1/qa/journeys/"+jid
  self.assertEqual(self.req("POST",url+"/label",a,ac,{"message":"changed"})[0],200)
  self.assertEqual(self.req("GET",url,a)[2]["data"]["label"],"changed")
  self.assertEqual(self.req("DELETE",url,a,ac)[0],200)
  self.assertEqual(self.req("GET",url,a)[0],404)
 def test_identity_revocation_closes_journey_access(self):
  a,ac=self.session("qa-alice");jid=self.create(a,ac)[2]["journeyId"]
  self.identities.disable_identity("qa-alice")
  self.assertEqual(self.req("GET","/api/v1/qa/journeys/"+jid,a)[0],404)
  self.assertEqual(self.create(a,ac)[0],401)
 def test_origin_csrf_and_fake_session_fail_closed(self):
  a,ac=self.session("qa-alice")
  self.assertEqual(self.req("POST","/api/v1/qa/journeys",a,payload={})[0],403)
  self.assertEqual(self.req("GET","/api/v1/qa/journeys/fake","atlas_qa=bogus")[0],401)
  with self.assertRaises(PermissionError):self.bridge.bind_fixture("not-real","invalid-token")
if __name__=="__main__":unittest.main()
