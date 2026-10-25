"""B6.5 QA disk sessions: restart, expiry, revocation, IDOR and local HTTP."""
import tempfile, unittest, sqlite3
from pathlib import Path
from persistent_sessions import PersistentSessionState
from local_http_facade import create_server

class PersistentSessionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=str(Path(self.tmp.name)/"sessions.db");self.now=[1000]
  self.state=PersistentSessionState(self.path,clock=lambda:self.now[0],ttl_seconds=60)
 def tearDown(self):self.tmp.cleanup()
 def restart(self):return PersistentSessionState(self.path,clock=lambda:self.now[0],ttl_seconds=60)
 def test_survives_service_restart(self):
  sid,csrf=self.state.create();jid=self.state.create_journey(sid)
  other=self.restart()
  self.assertEqual(other.check(sid)[0],200)
  self.assertEqual(other.journey(sid,jid)["label"],"Parcours fictif")
 def test_expiration_denies_journeys(self):
  sid,csrf=self.state.create();jid=self.state.create_journey(sid)
  self.now[0]+=61
  self.assertEqual(self.restart().check(sid)[0],401)
  self.assertIsNone(self.restart().journey(sid,jid))
 def test_revocation_survives_restart(self):
  sid,csrf=self.state.create()
  self.assertEqual(self.state.revoke(sid,csrf)[0],200)
  self.assertEqual(self.restart().check(sid)[0],401)
 def test_wrong_csrf_cannot_revoke(self):
  sid,csrf=self.state.create()
  self.assertEqual(self.state.revoke(sid,"bad")[0],403)
  self.assertEqual(self.state.check(sid)[0],200)
 def test_cross_owner_denied_after_restart(self):
  a,ca=self.state.create();b,cb=self.state.create();jid=self.state.create_journey(a)
  other=self.restart()
  self.assertIsNone(other.journey(b,jid))
  self.assertFalse(other.remove_journey(b,jid))
  self.assertIsNone(other.update_journey(b,jid,"hack"))
  self.assertEqual(other.journey(a,jid)["label"],"Parcours fictif")
 def test_tokens_not_stored_in_plaintext(self):
  sid,csrf=self.state.create()
  raw=Path(self.path).read_bytes()
  self.assertNotIn(sid.encode(),raw)
  self.assertNotIn(csrf.encode(),raw)
 def test_persistent_state_supported_by_local_server(self):
  server=create_server(state=self.state)
  self.assertEqual(server.server_address[0],"127.0.0.1")
  server.server_close()
if __name__=="__main__":unittest.main()
