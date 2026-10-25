"""B6.5 IDOR cross-session protections over real loopback HTTP, offline only."""
import json
import unittest
from test_local_http_facade import LocalHTTPTests
from local_http_facade import ALLOWED_ORIGIN

class JourneyIsolationTests(LocalHTTPTests):
    def request_owner(self,method,path,cookie,csrf=None,body=None):
        h={"Origin":ALLOWED_ORIGIN,"Cookie":cookie}
        if csrf:h["X-CSRF-Token"]=csrf
        if body is not None:
            h["Content-Type"]="application/json"
            body=json.dumps(body)
        return self.request(method,path,body=body,headers=h)
    def create(self,cookie,csrf):
        st,_,d=self.request_owner("POST","/api/v1/qa/journeys",cookie,csrf,{})
        self.assertEqual(st,201)
        return d["journeyId"]
    def test_cross_session_read_denied(self):
        a,ac=self.session();b,bc=self.session()
        jid=self.create(a,ac)
        self.assertEqual(self.request_owner("GET",f"/api/v1/qa/journeys/{jid}",b)[0],404)
        self.assertEqual(self.request_owner("GET",f"/api/v1/qa/journeys/{jid}",a)[0],200)
    def test_cross_session_update_denied_without_mutation(self):
        a,ac=self.session();b,bc=self.session();jid=self.create(a,ac)
        url=f"/api/v1/qa/journeys/{jid}/label"
        self.assertEqual(self.request_owner("POST",url,b,bc,{"message":"intrusion"})[0],404)
        self.assertEqual(self.request_owner("GET",f"/api/v1/qa/journeys/{jid}",a)[2]["data"]["label"],"Parcours fictif")
    def test_cross_session_delete_denied(self):
        a,ac=self.session();b,bc=self.session();jid=self.create(a,ac)
        url=f"/api/v1/qa/journeys/{jid}"
        self.assertEqual(self.request_owner("DELETE",url,b,bc)[0],404)
        self.assertEqual(self.request_owner("GET",url,a)[0],200)
    def test_owner_can_update_and_delete(self):
        a,ac=self.session();jid=self.create(a,ac);url=f"/api/v1/qa/journeys/{jid}"
        self.assertEqual(self.request_owner("POST",url+"/label",a,ac,{"message":"nouveau"})[0],200)
        self.assertEqual(self.request_owner("GET",url,a)[2]["data"]["label"],"nouveau")
        self.assertEqual(self.request_owner("DELETE",url,a,ac)[0],200)
        self.assertEqual(self.request_owner("GET",url,a)[0],404)
    def test_missing_csrf_denies_owner_write(self):
        a,ac=self.session();jid=self.create(a,ac)
        self.assertEqual(self.request_owner("DELETE",f"/api/v1/qa/journeys/{jid}",a)[0],403)
    def test_forged_identifier_and_missing_cookie(self):
        a,ac=self.session();jid=self.create(a,ac)
        self.assertEqual(self.request_owner("GET","/api/v1/qa/journeys/unknown",a)[0],404)
        self.assertEqual(self.request("GET",f"/api/v1/qa/journeys/{jid}")[0],401)
    def test_cross_session_csrf_not_sufficient(self):
        a,ac=self.session();b,bc=self.session();jid=self.create(a,ac)
        self.assertEqual(self.request_owner("POST",f"/api/v1/qa/journeys/{jid}/label",b,ac,{"message":"bad"})[0],403)

if __name__=="__main__":unittest.main()
