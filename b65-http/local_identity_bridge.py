"""SEC-01 QA-only identity bridge: fail closed on session revocation, expiry, restart.
The binding exists in process memory only and is never a public login endpoint.
"""
import hashlib, threading

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
