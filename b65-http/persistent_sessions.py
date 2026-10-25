"""B6.5 persistent QA sessions. SQLite locally, hashed cookie tokens, wall clock TTL.
Offline-only model; not production authentication.
"""
import hashlib, secrets, sqlite3, threading, time
from pathlib import Path

class PersistentSessionState:
    def __init__(self,path,clock=None,ttl_seconds=900,rate_limit=8,window_seconds=60):
        self.path=str(Path(path));self.clock=clock or time.time;self.ttl=ttl_seconds
        self.lock=threading.RLock()
        if type(rate_limit) is not int or rate_limit<1 or window_seconds<=0:raise ValueError('Invalid rate policy')
        self.rate_limit=rate_limit;self.window_seconds=window_seconds
        if ttl_seconds<=0:raise ValueError("Invalid TTL")
        with self.connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS sessions (id_hash TEXT PRIMARY KEY, csrf_hash TEXT NOT NULL, expires REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, CHECK(revoked IN (0,1)))")
            c.execute("CREATE TABLE IF NOT EXISTS request_events (id_hash TEXT NOT NULL, timestamp REAL NOT NULL)")
            c.execute("CREATE INDEX IF NOT EXISTS request_events_session_time ON request_events(id_hash,timestamp)")
            c.execute("CREATE TABLE IF NOT EXISTS journeys (id TEXT PRIMARY KEY, owner_hash TEXT NOT NULL, label TEXT NOT NULL, version INTEGER NOT NULL)")
    def connect(self):
        c=sqlite3.connect(self.path,timeout=10)
        c.execute("PRAGMA busy_timeout=10000")
        return c
    @staticmethod
    def digest(value):
        return hashlib.sha256(value.encode()).hexdigest() if isinstance(value,str) else ""
    def create(self):
        sid=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
        with self.connect() as c:
            c.execute("INSERT INTO sessions(id_hash,csrf_hash,expires) VALUES(?,?,?)",(self.digest(sid),self.digest(csrf),self.clock()+self.ttl))
        return sid,csrf
    def is_active_session(self,sid):
        with self.connect() as c:
            row=c.execute("SELECT expires,revoked FROM sessions WHERE id_hash=?",(self.digest(sid),)).fetchone()
        return bool(row and not row[1] and self.clock()<row[0])
    def check(self,sid,csrf=None,write=False):
        # BEGIN IMMEDIATE serializes checks across connections and processes.
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            identity=self.digest(sid)
            row=c.execute("SELECT csrf_hash,expires,revoked FROM sessions WHERE id_hash=?",(identity,)).fetchone()
            now=self.clock()
            if row is None or row[2] or now>=row[1]:return 401,"AUTH_REQUIRED"
            if write and (not isinstance(csrf,str) or not secrets.compare_digest(self.digest(csrf),row[0])):
                return 403,"CSRF_INVALID"
            c.execute("DELETE FROM request_events WHERE id_hash=? AND timestamp<=?",(identity,now-self.window_seconds))
            count=c.execute("SELECT COUNT(*) FROM request_events WHERE id_hash=?",(identity,)).fetchone()[0]
            if count>=self.rate_limit:return 429,"RATE_LIMITED"
            c.execute("INSERT INTO request_events(id_hash,timestamp) VALUES(?,?)",(identity,now))
            return 200,{"valid":True}
    def revoke(self,sid,csrf):
        status,detail=self.check(sid,csrf,write=True)
        if status!=200:return status,detail
        with self.connect() as c:
            c.execute("UPDATE sessions SET revoked=1 WHERE id_hash=?",(self.digest(sid),))
        return 200,{"revoked":True}
    def create_journey(self,sid):
        if self.check(sid)[0]!=200:return None
        jid=secrets.token_urlsafe(24)
        with self.connect() as c:
            c.execute("INSERT INTO journeys(id,owner_hash,label,version) VALUES(?,?,?,1)",(jid,self.digest(sid),"Parcours fictif"))
        return jid
    def journey(self,sid,jid):
        if self.check(sid)[0]!=200:return None
        with self.connect() as c:
            row=c.execute("SELECT label,version FROM journeys WHERE id=? AND owner_hash=?",(jid,self.digest(sid))).fetchone()
        return {"label":row[0],"version":row[1]} if row else None
    def remove_journey(self,sid,jid):
        if self.check(sid)[0]!=200:return False
        with self.connect() as c:
            return bool(c.execute("DELETE FROM journeys WHERE id=? AND owner_hash=?",(jid,self.digest(sid))).rowcount)
    def update_journey(self,sid,jid,label):
        if self.check(sid)[0]!=200:return None
        with self.connect() as c:
            count=c.execute("UPDATE journeys SET label=?,version=version+1 WHERE id=? AND owner_hash=?",(label,jid,self.digest(sid))).rowcount
        return self.journey(sid,jid) if count else None
