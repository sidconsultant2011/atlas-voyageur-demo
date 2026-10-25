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
        self.journeys={}
    def create(self):
        with self.lock:
            sid=secrets.token_urlsafe(32)
            csrf=secrets.token_urlsafe(32)
            self.sessions[sid]={"csrf":csrf,"expires":self.clock()+900,"hits":[]}
            return sid,csrf
    def create_journey(self,sid):
        with self.lock:
            jid=secrets.token_urlsafe(24)
            self.journeys[jid]={"owner":sid,"label":"Parcours fictif","version":1}
            return jid
    def journey(self,sid,jid):
        with self.lock:
            item=self.journeys.get(jid)
            if item is None or not secrets.compare_digest(item["owner"],sid):return None
            return item
    def remove_journey(self,sid,jid):
        with self.lock:
            if self.journey(sid,jid) is None:return False
            del self.journeys[jid]
            return True
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
            if self.headers.get("Origin")!=ALLOWED_ORIGIN or self.headers.get("Access-Control-Request-Method") not in ("POST","GET","DELETE"):
                return self.fail(403,"ORIGIN_DENIED")
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin",ALLOWED_ORIGIN)
            self.send_header("Access-Control-Allow-Methods","GET, POST, DELETE")
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
            if self.path=="/api/v1/qa/session/revoke":
                if not hasattr(state,"revoke"):return self.fail(404,"NOT_FOUND")
                status,detail=state.revoke(self.cookies(),self.headers.get("X-CSRF-Token"))
                if status!=200:return self.fail(status,detail)
                return self.send_json(200,{"status":"ok","data":detail},{"Set-Cookie":"atlas_qa=; HttpOnly; SameSite=Strict; Path=/api/v1/qa; Max-Age=0"})
            is_create=self.path=="/api/v1/qa/journeys"
            is_update=self.path.startswith("/api/v1/qa/journeys/") and self.path.endswith("/label")
            if not (is_create or is_update or self.path=="/api/v1/qa/echo"):return self.fail(404,"NOT_FOUND")
            size=self.headers.get("Content-Length")
            if not size or not size.isdecimal() or int(size)>MAX_BODY:return self.fail(413,"INVALID_LENGTH")
            if self.headers.get("Content-Type")!="application/json":return self.fail(415,"INVALID_CONTENT_TYPE")
            status,detail=state.check(self.cookies(),self.headers.get("X-CSRF-Token"),write=True)
            if status!=200:return self.fail(status,detail)
            if is_create:
                if int(size)!=2 or self.rfile.read(2)!=b"{}":return self.fail(400,"INVALID_INPUT")
                jid=state.create_journey(self.cookies())
                if jid is None:return self.fail(401,"AUTH_REQUIRED")
                return self.send_json(201,{"journeyId":jid,"source":"MOCK_ONLY"})
            if is_update:
                jid=self.path.split("/")[-2]
                if state.journey(self.cookies(),jid) is None:return self.fail(404,"NOT_FOUND")
            try:
                data=json.loads(self.rfile.read(int(size)))
                if not isinstance(data,dict) or set(data)!={"message"} or not isinstance(data["message"],str) or len(data["message"])>80:
                    raise ValueError()
            except (ValueError,UnicodeDecodeError):return self.fail(400,"INVALID_INPUT")
            if is_update:
                if hasattr(state,"update_journey"):
                    journey=state.update_journey(self.cookies(),jid,data["message"])
                else:
                    with state.lock:
                        journey=state.journey(self.cookies(),jid)
                        if journey is not None:
                            journey["label"]=data["message"];journey["version"]+=1
                if journey is None:return self.fail(404,"NOT_FOUND")
                return self.send_json(200,{"status":"ok","data":{"version":journey["version"]}})
            return self.send_json(200,{"status":"ok","data":{"message":data["message"],"source":"MOCK_ONLY"}})
        def do_GET(self):
            if not self.origin_ok():return self.fail(403,"ORIGIN_DENIED")
            is_journey=self.path.startswith("/api/v1/qa/journeys/") and len(self.path.split("/"))==6
            if not (self.path=="/api/v1/qa/state" or is_journey):return self.fail(404,"NOT_FOUND")
            status,detail=state.check(self.cookies())
            if status!=200:return self.fail(status,detail)
            if is_journey:
                item=state.journey(self.cookies(),self.path.rsplit("/",1)[-1])
                if item is None:return self.fail(404,"NOT_FOUND")
                return self.send_json(200,{"status":"ok","data":{"label":item["label"],"version":item["version"],"source":"MOCK_ONLY"}})
            return self.send_json(200,{"status":"ok","data":{"source":"MOCK_ONLY"}})
        def do_DELETE(self):
            if not self.origin_ok():return self.fail(403,"ORIGIN_DENIED")
            if not (self.path.startswith("/api/v1/qa/journeys/") and len(self.path.split("/"))==6):return self.fail(404,"NOT_FOUND")
            status,detail=state.check(self.cookies(),self.headers.get("X-CSRF-Token"),write=True)
            if status!=200:return self.fail(status,detail)
            if not state.remove_journey(self.cookies(),self.path.rsplit("/",1)[-1]):return self.fail(404,"NOT_FOUND")
            return self.send_json(200,{"status":"ok","data":{"deleted":True}})
    return ThreadingHTTPServer((host,port),Handler)

if __name__=="__main__":
    raise SystemExit("QA-only module; instantiate create_server() in local tests, no public listener.")
