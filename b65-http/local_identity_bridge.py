"""SEC-01 QA-only identity bridge: fail closed on session revocation, expiry, restart.
The binding exists in process memory only and is never a public login endpoint.
"""
import hashlib, threading
from sqlite_ac08 import require_existing_disk, verify_attached

class LocalIdentityBridge:
    def __init__(self, identity_store):
        self.identities=identity_store
        self._bindings={}
        self._lock=threading.RLock()
        self._session_state=None

    def bind_state(self, state):
        if not callable(getattr(state,"is_active_session",None)):
            raise TypeError("Session state must support read-only validation")
        with self._lock:
            if self._session_state is not None and self._session_state is not state:
                raise RuntimeError("Bridge already attached to another state")
            self._session_state=state

    def _active(self, cookie):
        return (isinstance(cookie,str) and bool(cookie) and
                self._session_state is not None and
                self._session_state.is_active_session(cookie))

    @staticmethod
    def _key(cookie):
        return hashlib.sha256(cookie.encode()).hexdigest()

    def bind_fixture(self,session_cookie,identity_token):
        if not self._active(session_cookie) or not self.identities.whoami(identity_token):
            raise PermissionError("Identity or HTTP session invalid")
        with self._lock:
            if not self._active(session_cookie):
                raise PermissionError("HTTP session no longer valid")
            self._bindings[self._key(session_cookie)]=identity_token

    def owner_token(self,session_cookie):
        if not self._active(session_cookie):return None
        key=self._key(session_cookie)
        with self._lock:
            token=self._bindings.get(key)
            if not token:return None
            if not self._active(session_cookie) or not self.identities.whoami(token):
                self._bindings.pop(key,None)
                return None
            return token

    def revoke_binding(self,session_cookie):
        if not isinstance(session_cookie,str):return
        with self._lock:self._bindings.pop(self._key(session_cookie),None)


    def _persistent_journey(self,session_cookie,operation,jid=None,label=None):
        """One SQLite transaction locks session and identity databases together.

        Returns (handled, result). Only the supported local SQLite fixtures use
        this path; in-memory LocalState keeps its historical test behavior.
        """
        from persistent_sessions import PersistentSessionState
        from fictional_identities import FictionalIdentityStore
        state=self._session_state
        if not isinstance(state,PersistentSessionState) or not isinstance(self.identities,FictionalIdentityStore):
            return False,None
        if not isinstance(session_cookie,str) or not session_cookie:
            return True,(False if operation in ("update","delete") else None)
        key=self._key(session_cookie)
        with self._lock:
            token=self._bindings.get(key)
            if token is None:return True,(False if operation in ("update","delete") else None)
            # On-disk SQLite databases share BEGIN IMMEDIATE serialization.
            # Both databases use their default rollback-journal mode, allowing
            # atomic multi-file COMMIT on the same local filesystem.
            with state.connect() as c:
                require_existing_disk(self.identities.path)
                c.execute("ATTACH DATABASE ? AS identity_db",(self.identities.path,))
                verify_attached(c,state.path,self.identities.path)
                c.execute("BEGIN IMMEDIATE")
                status,_=state._authorize(c,session_cookie)
                if status!=200:
                    self._bindings.pop(key,None)
                    return True,(False if operation in ("update","delete") else None)
                row=c.execute("""SELECT s.identity_id FROM identity_db.identity_sessions s
                     JOIN identity_db.identities i ON i.id=s.identity_id
                     WHERE s.token_hash=? AND s.revoked=0 AND i.enabled=1 AND s.expires>?""",
                     (self.identities._hash(token),self.identities.clock())).fetchone()
                if not row:
                    self._bindings.pop(key,None)
                    return True,(False if operation in ("update","delete") else None)
                owner=row[0]
                if operation=="create":
                    import secrets
                    created=secrets.token_urlsafe(24)
                    c.execute("INSERT INTO identity_db.identity_journeys(id,identity_id,label) VALUES(?,?,?)",
                              (created,owner,"Parcours fictif"))
                    return True,created
                if operation=="read":
                    found=c.execute("SELECT label FROM identity_db.identity_journeys WHERE id=? AND identity_id=?",
                                    (jid,owner)).fetchone()
                    return True,({"label":found[0]} if found else None)
                if operation=="update":
                    if not isinstance(label,str) or len(label)>80:return True,False
                    changed=c.execute("UPDATE identity_db.identity_journeys SET label=? WHERE id=? AND identity_id=?",
                                      (label,jid,owner)).rowcount
                    return True,bool(changed)
                if operation=="delete":
                    changed=c.execute("DELETE FROM identity_db.identity_journeys WHERE id=? AND identity_id=?",
                                      (jid,owner)).rowcount
                    return True,bool(changed)
                raise ValueError("Unsupported identity journey operation")

    def create(self,session_cookie):
        handled,result=self._persistent_journey(session_cookie,"create")
        if handled:return result
        token=self.owner_token(session_cookie)
        return self.identities.create_journey(token) if token else None
    def read(self,session_cookie,jid):
        handled,result=self._persistent_journey(session_cookie,"read",jid)
        if handled:return result
        token=self.owner_token(session_cookie)
        return self.identities.get_journey(token,jid) if token else None
    def update(self,session_cookie,jid,label):
        handled,result=self._persistent_journey(session_cookie,"update",jid,label)
        if handled:return result
        token=self.owner_token(session_cookie)
        return self.identities.set_label(token,jid,label) if token else False
    def delete(self,session_cookie,jid):
        handled,result=self._persistent_journey(session_cookie,"delete",jid)
        if handled:return result
        token=self.owner_token(session_cookie)
        return self.identities.delete_journey(token,jid) if token else False
