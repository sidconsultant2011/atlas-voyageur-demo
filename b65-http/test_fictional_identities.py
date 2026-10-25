"""B6.5 SEC-01: offline identity management and IDOR proof."""
import tempfile,unittest
from pathlib import Path
from fictional_identities import FictionalIdentityStore

class IdentityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=str(Path(self.tmp.name)/"identities.sqlite");self.time=[100.]
  self.db=FictionalIdentityStore(self.path,clock=lambda:self.time[0],ttl=30)
  for x in ("qa-alice","qa-bob"):self.db.add_fixture_identity(x)
 def tearDown(self):self.tmp.cleanup()
 def reopen(self):return FictionalIdentityStore(self.path,clock=lambda:self.time[0],ttl=30)
 def test_two_identities_cannot_read_cross_journeys(self):
  a=self.db.open_session("qa-alice");b=self.db.open_session("qa-bob");j=self.db.create_journey(a)
  self.assertIsNone(self.db.get_journey(b,j))
  self.assertEqual(self.db.get_journey(a,j)["label"],"Parcours fictif")
 def test_cross_identity_update_delete_rejected(self):
  a=self.db.open_session("qa-alice");b=self.db.open_session("qa-bob");j=self.db.create_journey(a)
  self.assertFalse(self.db.set_label(b,j,"pirate"));self.assertFalse(self.db.delete_journey(b,j))
  self.assertEqual(self.db.get_journey(a,j)["label"],"Parcours fictif")
 def test_owner_can_modify_and_delete(self):
  a=self.db.open_session("qa-alice");j=self.db.create_journey(a)
  self.assertTrue(self.db.set_label(a,j,"voyage"))
  self.assertEqual(self.db.get_journey(a,j)["label"],"voyage")
  self.assertTrue(self.db.delete_journey(a,j));self.assertIsNone(self.db.get_journey(a,j))
 def test_persistence_and_reopen(self):
  a=self.db.open_session("qa-alice");j=self.db.create_journey(a)
  self.assertEqual(self.reopen().whoami(a),"qa-alice")
  self.assertIsNotNone(self.reopen().get_journey(a,j))
 def test_session_expiry(self):
  a=self.db.open_session("qa-alice");j=self.db.create_journey(a);self.time[0]+=31
  self.assertIsNone(self.reopen().whoami(a));self.assertIsNone(self.reopen().get_journey(a,j))
 def test_revoke_persistent(self):
  a=self.db.open_session("qa-alice")
  self.assertTrue(self.db.revoke(a));self.assertFalse(self.db.revoke(a))
  self.assertIsNone(self.reopen().whoami(a))
 def test_disable_identity_revokes_all_sessions(self):
  a=self.db.open_session("qa-alice");b=self.db.open_session("qa-alice")
  self.db.disable_identity("qa-alice")
  self.assertIsNone(self.reopen().whoami(a));self.assertIsNone(self.reopen().whoami(b))
  with self.assertRaises(PermissionError):self.db.open_session("qa-alice")
 def test_no_unapproved_accounts(self):
  with self.assertRaises(ValueError):self.db.add_fixture_identity("administrator")
 def test_unknown_token_rejected(self):
  self.assertIsNone(self.db.whoami("fake"))
  with self.assertRaises(PermissionError):self.db.create_journey("fake")
 def test_tokens_not_persisted_as_plaintext(self):
  a=self.db.open_session("qa-alice");self.assertNotIn(a.encode(),Path(self.path).read_bytes())
if __name__=="__main__":unittest.main()
