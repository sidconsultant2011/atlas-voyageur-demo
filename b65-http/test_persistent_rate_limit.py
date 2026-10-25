"""B6.5 SQLite session quota persists across service restart and competing instances."""
import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from persistent_sessions import PersistentSessionState

class PersistentQuotaTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.path=str(Path(self.tmp.name)/"quota.sqlite")
  self.now=[1000.0]
 def tearDown(self):self.tmp.cleanup()
 def state(self,limit=3):
  return PersistentSessionState(self.path,clock=lambda:self.now[0],rate_limit=limit,window_seconds=60)
 def test_restart_does_not_reset_quota(self):
  a=self.state();sid,csrf=a.create()
  self.assertEqual([a.check(sid)[0] for _ in range(3)],[200]*3)
  self.assertEqual(self.state().check(sid)[0],429)
 def test_window_expires_then_accepts(self):
  s=self.state();sid,_=s.create()
  for _ in range(3):self.assertEqual(s.check(sid)[0],200)
  self.now[0]+=61
  self.assertEqual(self.state().check(sid)[0],200)
 def test_independent_sessions_have_separate_quota(self):
  s=self.state();a,_=s.create();b,_=s.create()
  for _ in range(3):self.assertEqual(s.check(a)[0],200)
  self.assertEqual(s.check(a)[0],429)
  self.assertEqual(s.check(b)[0],200)
 def test_parallel_connections_do_not_exceed_quota(self):
  s=self.state(limit=5);sid,_=s.create()
  def check(_):return self.state(limit=5).check(sid)[0]
  with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
   codes=list(pool.map(check,range(30)))
  self.assertEqual(codes.count(200),5)
  self.assertEqual(codes.count(429),25)
 def test_invalid_csrf_does_not_consume_budget(self):
  s=self.state(limit=1);sid,_=s.create()
  self.assertEqual(s.check(sid,csrf="wrong",write=True)[0],403)
  self.assertEqual(s.check(sid)[0],200)
  self.assertEqual(s.check(sid)[0],429)
 def test_revoked_session_stays_denied(self):
  s=self.state(limit=4);sid,csrf=s.create()
  self.assertEqual(s.revoke(sid,csrf)[0],200)
  self.assertEqual(self.state(limit=4).check(sid)[0],401)
 def test_expired_session_stays_denied(self):
  s=self.state();sid,_=s.create()
  self.now[0]+=901
  self.assertEqual(self.state().check(sid)[0],401)
 def test_reject_invalid_policy(self):
  with self.assertRaises(ValueError):PersistentSessionState(self.path,rate_limit=0)

if __name__=="__main__":unittest.main()
