"""B6.5 SEC-01: offline identity prototype, NEVER production authentication.
Fictional test accounts only; no passwords, external identity provider or network.
"""
import hashlib, secrets, sqlite3, time
from pathlib import Path
from sqlite_ac08 import open_qa_database

class FictionalIdentityStore:
    def __init__(self,path,clock=None,ttl=900):
        self.path=str(Path(path));self.clock=clock or time.time;self.ttl=ttl
        if ttl<=0:raise ValueError("Invalid TTL")
        self._initializing=True
        with self._db() as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("CREATE TABLE IF NOT EXISTS identities (id TEXT PRIMARY KEY, enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)))")
            db.execute("CREATE TABLE IF NOT EXISTS identity_sessions (token_hash TEXT PRIMARY KEY, identity_id TEXT NOT NULL REFERENCES identities(id), expires REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0)")
            db.execute("CREATE TABLE IF NOT EXISTS identity_journeys (id TEXT PRIMARY KEY, identity_id TEXT NOT NULL REFERENCES identities(id), label TEXT NOT NULL)")
        self._initializing=False
    def _db(self):
        db=open_qa_database(self.path, initialize=getattr(self,"_initializing",False), foreign_keys=True)
        return db
    @staticmethod
    def _hash(token):
        return hashlib.sha256(token.encode()).hexdigest() if isinstance(token,str) else ""
    def add_fixture_identity(self,identity_id):
        if identity_id not in ("qa-alice","qa-bob"):raise ValueError("Only fictional approved identities")
        with self._db() as db:db.execute("INSERT OR IGNORE INTO identities(id) VALUES(?)",(identity_id,))
    def open_session(self,identity_id):
        # trusted test harness only: caller cannot be an anonymous HTTP request
        if identity_id not in ("qa-alice","qa-bob"):raise ValueError("Invalid fixture identity")
        token=secrets.token_urlsafe(32)
        with self._db() as db:
            row=db.execute("SELECT enabled FROM identities WHERE id=?",(identity_id,)).fetchone()
            if not row or not row[0]:raise PermissionError("Identity not enabled")
            db.execute("INSERT INTO identity_sessions VALUES(?,?,?,0)",(self._hash(token),identity_id,self.clock()+self.ttl))
        return token
    def whoami(self,token):
        with self._db() as db:
            row=db.execute("""SELECT s.identity_id FROM identity_sessions s JOIN identities i ON i.id=s.identity_id
              WHERE s.token_hash=? AND s.revoked=0 AND i.enabled=1 AND s.expires>?""",(self._hash(token),self.clock())).fetchone()
            return row[0] if row else None
    def revoke(self,token):
        with self._db() as db:
            return db.execute("UPDATE identity_sessions SET revoked=1 WHERE token_hash=? AND revoked=0",(self._hash(token),)).rowcount==1
    def disable_identity(self,identity_id):
        with self._db() as db:
            db.execute("UPDATE identities SET enabled=0 WHERE id=?",(identity_id,))
            db.execute("UPDATE identity_sessions SET revoked=1 WHERE identity_id=?",(identity_id,))
    def create_journey(self,token):
        identity_id=self.whoami(token)
        if not identity_id:raise PermissionError("AUTH_REQUIRED")
        journey_id=secrets.token_urlsafe(24)
        with self._db() as db:db.execute("INSERT INTO identity_journeys VALUES(?,?,?)",(journey_id,identity_id,"Parcours fictif"))
        return journey_id
    def get_journey(self,token,journey_id):
        identity_id=self.whoami(token)
        if not identity_id:return None
        with self._db() as db:
            row=db.execute("SELECT label FROM identity_journeys WHERE id=? AND identity_id=?",(journey_id,identity_id)).fetchone()
            return {"label":row[0]} if row else None
    def set_label(self,token,journey_id,label):
        identity_id=self.whoami(token)
        if not identity_id or not isinstance(label,str) or len(label)>80:return False
        with self._db() as db:
            return db.execute("UPDATE identity_journeys SET label=? WHERE id=? AND identity_id=?",(label,journey_id,identity_id)).rowcount==1
    def delete_journey(self,token,journey_id):
        identity_id=self.whoami(token)
        if not identity_id:return False
        with self._db() as db:
            return db.execute("DELETE FROM identity_journeys WHERE id=? AND identity_id=?",(journey_id,identity_id)).rowcount==1
