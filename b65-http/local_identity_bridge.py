"""SEC-01 QA-only identity binding. A trusted local test harness binds a fictional identity
to a cookie session; never exposed as HTTP registration/login."""
import hashlib, threading

class LocalIdentityBridge:
    def __init__(self,identity_store):
        self.identities=identity_store
        self._bindings={}
        self._lock=threading.RLock()
    def bind_fixture(self,session_cookie,identity_token):
        if not isinstance(session_cookie,str) or not session_cookie or not self.identities.whoami(identity_token):
            raise PermissionError("Identity or session invalid")
        key=hashlib.sha256(session_cookie.encode()).hexdigest()
        with self._lock:self._bindings[key]=identity_token
    def owner_token(self,session_cookie):
        if not isinstance(session_cookie,str):return None
        key=hashlib.sha256(session_cookie.encode()).hexdigest()
        with self._lock:token=self._bindings.get(key)
        return token if token and self.identities.whoami(token) else None
    def create(self,session_cookie):
        token=self.owner_token(session_cookie)
        return self.identities.create_journey(token) if token else None
    def read(self,session_cookie,jid):
        token=self.owner_token(session_cookie)
        return self.identities.get_journey(token,jid) if token else None
    def update(self,session_cookie,jid,label):
        token=self.owner_token(session_cookie)
        return self.identities.set_label(token,jid,label) if token else False
    def delete(self,session_cookie,jid):
        token=self.owner_token(session_cookie)
        return self.identities.delete_journey(token,jid) if token else False
