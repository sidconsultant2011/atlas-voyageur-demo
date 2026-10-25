"""B6.5 QA-only loopback HTTP facade. Standard library, no outbound requests."""
import json, secrets, threading, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from urllib.parse import urlsplit

ALLOWED_ORIGIN = "http://127.0.0.1:8765"
MAX_BODY = 4096

class LocalState:
    def __init__(self,clock=None):
        self.clock=clock or time.monotonic
        self.lock=threading.RLock()
        self.sessions={}
    def create(self):
        with self.lock:
            sid=secrets.token_urlsafe(32)
            csrf=secrets.token_urlsafe(32)
            self.sessions[sid]={"csrf":csrf,"expires":self.clock()+900,"hits":[]}
            return sid,csrf
    def check(self,sid,csrf=None,write=False):
        with self.lock:
            session=self.sessions.get(sid)
            if not session or self.clock()>=session["expires"]:return 401,"AUTH_REQUIRED"
            now=self.clock()
            session["hits"]=[t for t in session["hits"] if now-t<60]
            if len(session["hits"])>=8:return 429,"RATE_LIMITED"
            if write and (not csrf or not secrets.compare_digest(csrf,session["csrf"])):
                return 403,"CSRF_INVALID"
            session["hits"].append(now)
            return 200,session

def create_server(*,port=0,host="127.0.0.1",state=None):
    if host!="127.0.0.1":raise ValueError("Only IPv4 loopback is allowed")
    state=state or LocalState()
    class Handler(BaseHTTPRequestHandler):
        server_version="AtlasQA/1"
        sys_version=""
        def log_message(self,*args):pass
        def send_json(self,status,payload,extra=None):
            raw=json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Content-Length",str(len(raw)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Referrer-Policy","no-referrer")
            self.send_header("Content-Security-Policy","default-src 'none'; frame-ancestors 'none'")
            if self.headers.get("Origin")==ALLOWED_ORIGIN:
                self.send_header("Access-Control-Allow-Origin",ALLOWED_ORIGIN)
                self.send_header("Vary","Origin")
            for k,v in (extra or {}).items():self.send_header(k,v)
            self.end_headers();self.wfile.write(raw)
        def fail(self,code,error):
            self.send_json(code,{"status":"unavailable","errors":[{"code":error}]})
        def origin_ok(self):
            origin=self.headers.get("Origin")
            return origin in (None,ALLOWED_ORIGIN)
        def cookies(self):
            c=SimpleCookie()
            try:c.load(self.headers.get("Cookie",""))
            except Exception:return None
            return c["atlas_qa"].value if "atlas_qa" in c else None
        def do_OPTIONS(self):
            if self.headers.get("Origin")!=ALLOWED_ORIGIN or self.headers.get("Access-Control-Request-Method") not in ("POST","GET"):
                return self.fail(403,"ORIGIN_DENIED")
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin",ALLOWED_ORIGIN)
            self.send_header("Access-Control-Allow-Methods","GET, POST")
            self.send_header("Access-Control-Allow-Headers","Content-Type, X-CSRF-Token")
            self.send_header("Access-Control-Max-Age","60")
            self.send_header("Vary","Origin")
            self.end_headers()
        def do_POST(self):
            if not self.origin_ok():return self.fail(403,"ORIGIN_DENIED")
            if self.path=="/api/v1/qa/session":
                if self.headers.get("Origin")!=ALLOWED_ORIGIN:return self.fail(403,"ORIGIN_REQUIRED")
                if self.headers.get("Content-Length") not in ("0",None):return self.fail(400,"INVALID_INPUT")
                sid,csrf=state.create()
                return self.send_json(201,{"csrfToken":csrf,"expiresInSeconds":900},
                    {"Set-Cookie":f"atlas_qa={sid}; HttpOnly; SameSite=Strict; Path=/api/v1/qa"})
            if self.path!="/api/v1/qa/echo":return self.fail(404,"NOT_FOUND")
            size=self.headers.get("Content-Length")
            if not size or not size.isdecimal() or int(size)>MAX_BODY:return self.fail(413,"INVALID_LENGTH")
            if self.headers.get("Content-Type")!="application/json":return self.fail(415,"INVALID_CONTENT_TYPE")
            status,detail=state.check(self.cookies(),self.headers.get("X-CSRF-Token"),write=True)
            if status!=200:return self.fail(status,detail)
            try:
                data=json.loads(self.rfile.read(int(size)))
                if not isinstance(data,dict) or set(data)!={"message"} or not isinstance(data["message"],str) or len(data["message"])>80:
                    raise ValueError()
            except (ValueError,UnicodeDecodeError):return self.fail(400,"INVALID_INPUT")
            return self.send_json(200,{"status":"ok","data":{"message":data["message"],"source":"MOCK_ONLY"}})
        def do_GET(self):
            if not self.origin_ok():return self.fail(403,"ORIGIN_DENIED")
            if self.path!="/api/v1/qa/state":return self.fail(404,"NOT_FOUND")
            status,detail=state.check(self.cookies())
            if status!=200:return self.fail(status,detail)
            return self.send_json(200,{"status":"ok","data":{"source":"MOCK_ONLY"}})
    return ThreadingHTTPServer((host,port),Handler)

if __name__=="__main__":
    raise SystemExit("QA-only module; instantiate create_server() in local tests, no public listener.")
