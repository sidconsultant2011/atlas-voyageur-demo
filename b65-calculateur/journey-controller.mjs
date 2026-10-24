/** B6.5 — Offline journey controller. No network, persistence or provider secrets. */
import {planDeparture} from './atlas-depart-engine.mjs';
import {adaptAeroDataBoxFixture,adaptGeoapifyFixture,mockFlights,mockRoutes} from './mock-adapters.mjs';
import {DEFAULT_ASSUMPTIONS} from './mock-integration.mjs';
const clone=x=>structuredClone(x);
const timestamp=x=>typeof x==='string'&&Number.isFinite(Date.parse(x))?Date.parse(x):null;
export function createJourneyController({assumptions=DEFAULT_ASSUMPTIONS, freshnessPolicy=null, now=()=>Date.now()}={}){
 if(typeof now!=='function')throw new TypeError('Clock function required');
 if(freshnessPolicy!==null&&(!Number.isFinite(freshnessPolicy.maxAgeMinutes)||freshnessPolicy.maxAgeMinutes<=0||!Number.isFinite(freshnessPolicy.maxFutureSkewMinutes??2)||freshnessPolicy.maxFutureSkewMinutes<0))throw new RangeError('Invalid freshness policy');
 let flight=null,road=null,flightVersion=0,routeVersion=0;
 let latestFlightAt=null,latestRouteAt=null;
 let lastReason='AWAITING_FLIGHT_AND_ROUTE';
 let settings=clone(assumptions);
 const flightFreshness=()=>{
   if(!flight||freshnessPolicy===null)return {status:'not_enforced'};
   const current=now();
   if(!Number.isFinite(current))throw new RangeError('Invalid clock value');
   if(latestFlightAt===null)return {status:'unknown'};
   const ageMs=current-latestFlightAt;
   if(ageMs<-(freshnessPolicy.maxFutureSkewMinutes??2)*60000)return {status:'future',ageMinutes:ageMs/60000};
   if(ageMs>freshnessPolicy.maxAgeMinutes*60000)return {status:'expired',ageMinutes:ageMs/60000};
   return {status:'fresh',ageMinutes:ageMs/60000};
 };
 const calculation=()=>{
   if(!flight||!road)return null;
   const freshness=flightFreshness();
   const input=freshnessPolicy!==null&&freshness.status!=='fresh'?{...flight,stale:true}:flight;
   return planDeparture({flight:input,road,assumptions:settings});
 };
 const snapshot=()=>{
   const r=calculation();
   return {mode:'MOCK_ONLY',flight:clone(flight),road:clone(road),
     recommendation:r??{status:'unavailable',recommendedDepartureUtc:null,errors:[!flight?'FLIGHT_UNAVAILABLE':'ROUTE_UNAVAILABLE']},
     flightVersion,routeVersion,latestFlightAt,latestRouteAt,flightFreshness:flightFreshness(),lastReason};
 };
 const accept=(kind,raw,{observedAtUtc=null,requestVersion=null}={})=>{
   const isFlight=kind==='flight',current=isFlight?flightVersion:routeVersion;
   if(requestVersion!==null&&requestVersion!==current)return {accepted:false,reason:'SUPERSEDED_REQUEST',state:snapshot()};
   const date=observedAtUtc===null?null:timestamp(observedAtUtc);
   if(observedAtUtc!==null&&date===null)throw new RangeError('Invalid observedAtUtc');
   const old=isFlight?latestFlightAt:latestRouteAt;
   if(date!==null&&old!==null&&date<old)return {accepted:false,reason:'OLDER_OBSERVATION',state:snapshot()};
   const normalized=isFlight?adaptAeroDataBoxFixture(raw):adaptGeoapifyFixture(raw);
   if(isFlight){
     const flightChanged=flight&&(flight.flightNumber!==normalized.flightNumber||flight.destinationIata!==normalized.destinationIata);
     flight=normalized;flightVersion++;
     if(date!==null)latestFlightAt=date;
     if(flightChanged){road=null;routeVersion++;latestRouteAt=null;lastReason='FLIGHT_CHANGED_ROUTE_INVALIDATED'}
     else lastReason='FLIGHT_UPDATED';
   }else{road=normalized;routeVersion++;if(date!==null)latestRouteAt=date;lastReason='ROUTE_UPDATED'}
   return {accepted:true,reason:lastReason,state:snapshot()};
 };
 return Object.freeze({
   getState:snapshot,
   getRequestVersions:()=>({flightVersion,routeVersion}),
   setFlight:(raw,opts)=>accept('flight',raw,opts),
   setRoute:(raw,opts)=>accept('route',raw,opts),
   selectFlightFixture:(name,opts)=>{if(!Object.hasOwn(mockFlights,name))throw new RangeError('Unknown flight fixture');return accept('flight',mockFlights[name],opts)},
   selectRouteFixture:(name,opts)=>{if(!Object.hasOwn(mockRoutes,name))throw new RangeError('Unknown route fixture');return accept('route',mockRoutes[name],opts)},
   setAssumptions:next=>{settings=clone(next);lastReason='ASSUMPTIONS_UPDATED';return snapshot()},
   invalidateRoute:()=>{road=null;routeVersion++;latestRouteAt=null;lastReason='ROUTE_INVALIDATED';return snapshot()},
   reset:()=>{flight=null;road=null;flightVersion++;routeVersion++;latestFlightAt=null;latestRouteAt=null;lastReason='RESET';return snapshot()}
 });
}
