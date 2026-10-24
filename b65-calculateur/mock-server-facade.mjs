/** B6.5 server facade MOCK ONLY. In-process contract; no HTTP listeners, fetch, or secrets. */
import {createJourneyController} from './journey-controller.mjs';
import {mockFlights,mockRoutes} from './mock-adapters.mjs';
export function createMockFacade({now=()=>Date.now(),budget=20,cacheMs=300000,maxCallsPerSession=5}={}){
 if(!Number.isFinite(budget)||budget<0||!Number.isFinite(cacheMs)||cacheMs<0||!Number.isFinite(maxCallsPerSession)||maxCallsPerSession<1)throw new RangeError('Invalid limits');
 const sessions=new Map(),cache=new Map();let spent=0,seq=0;
 const response=(status,data=null,error=null)=>({httpStatus:status,status:status<400?'ok':'unavailable',data,errors:error?[error]:[]});
 const error=(status,code)=>response(status,null,{code});
 const access=(id,token)=>{
  const s=sessions.get(id);
  if(!s||s.token!==token)return null;
  if(now()>s.expiresAt){sessions.delete(id);return null}
  return s;
 };
 const charge=(s,key,cost,provider)=>{
  const existing=cache.get(key);
  if(existing&&now()<existing.expiresAt)return {cached:true,result:structuredClone(existing.result)};
  if(s.calls>=maxCallsPerSession)return {error:error(429,'RATE_LIMITED')};
  if(spent+cost>budget)return {error:error(429,'BUDGET_EXHAUSTED')};
  s.calls++;spent+=cost;
  return {cached:false,store:result=>{cache.set(key,{expiresAt:now()+cacheMs,result:structuredClone(result)});return result},provider};
 };
 // caller supplies opaque identifiers (fixture-only simulation); never attach this to an HTTP server.
 const createSession=({ownerToken,locale='fr'}={})=>{
  if(typeof ownerToken!=='string'||ownerToken.length<12)return error(401,'AUTH_REQUIRED');
  if(!['fr','en','ru'].includes(locale))return error(400,'INVALID_INPUT');
  const id='mock-journey-'+(++seq),token='mock-session-'+seq+'-'+ownerToken;
  sessions.set(id,{token,controller:createJourneyController(),expiresAt:now()+3600000,calls:0,selected:null});
  return response(201,{journeyId:id,sessionToken:token,expiresAtUtc:new Date(now()+3600000).toISOString()});
 };
 const call=(operation,{journeyId,sessionToken,body={}}={})=>{
  const s=access(journeyId,sessionToken);
  if(!s)return error(404,'ACCESS_DENIED');
  if(!body||typeof body!=='object'||Array.isArray(body))return error(400,'INVALID_INPUT');
  if(operation==='flight.search'){
   const number=body.number;
   if(typeof number!=='string'||!/^[A-Za-z]{1,3}\d{1,4}$/.test(number))return error(400,'INVALID_INPUT');
   const key='flight:'+number.toUpperCase(),q=charge(s,key,2,'aerodatabox');
   if(q.error)return q.error;
   if(q.cached)return response(200,q.result);
   const candidates=number.toUpperCase()==='AV103'?[{candidateId:'fixture-delayed',number:'AV103',destination:'ORY'}]:[];
   return response(200,q.store({candidates,source:'MOCK_ONLY'}));
  }
  if(operation==='flight.select'){
   if(body.candidateId!=='fixture-delayed')return error(404,'FLIGHT_NOT_FOUND');
   s.selected=body.candidateId;s.controller.selectFlightFixture('delayed');
   return response(200,{flightVersion:s.controller.getState().flightVersion});
  }
  if(operation==='origin.geocode'){
   if(typeof body.text!=='string'||body.text.trim().length<6||body.text.length>150)return error(400,'INVALID_INPUT');
   const key='geo:'+body.text.trim().toLowerCase(),q=charge(s,key,1,'geoapify');
   if(q.error)return q.error;
   if(q.cached)return response(200,q.result);
   return response(200,q.store({candidates:[{originId:'mock-rozay',label:'Adresse fictive de recette'}],source:'MOCK_ONLY'}));
  }
  if(operation==='origin.select'){
   if(body.originId!=='mock-rozay')return error(400,'INVALID_INPUT');
   s.controller.invalidateRoute();s.origin='mock-rozay';
   return response(200,{originVersion:s.controller.getState().routeVersion});
  }
  if(operation==='route.calculate'){
   if(s.origin!=='mock-rozay'||!s.selected)return error(409,'PREREQUISITES_MISSING');
   const v=s.controller.getState().routeVersion;
   if(body.originVersion!==v)return error(409,'STALE_STATE_VERSION');
   const q=charge(s,'route:'+journeyId+':'+v,1,'geoapify');
   if(q.error)return q.error;
   s.controller.selectRouteFixture('rozay');
   return response(200,{routeVersion:s.controller.getState().routeVersion,distanceMeters:65100,durationSeconds:2700,source:'MOCK_ONLY'});
  }
  if(operation==='recommendation'){
   return response(200,{recommendation:s.controller.getState().recommendation,source:'MOCK_ONLY'});
  }
  if(operation==='flight.refresh')return error(429,'RATE_LIMITED'); // explicitly blocked in offline prototype
  return error(404,'UNKNOWN_OPERATION');
 };
 return Object.freeze({createSession,call,metrics:()=>({spent,budget,sessions:sessions.size,cacheEntries:cache.size})});
}
