/** B6.5 OFFLINE ONLY — AeroDataBox V2 to existing journey controller bridge. */
import {selectAeroDataBoxFlightV2} from './aerodatabox-v2.mjs';
const validUtc=s=>typeof s==='string'&&Number.isFinite(Date.parse(s))?Date.parse(s):null;
export function applyAeroDataBoxV2Offline(controller,records,{
 number=null,originIata=null,destinationIata=null,
 nowUtc='2027-05-15T14:05:00Z',maxAgeMinutes=30,maxFutureSkewMinutes=2,
 requestVersion=null
}={}){
 if(!controller||typeof controller.setFlight!=='function'||typeof controller.getState!=='function')throw new TypeError('Journey controller required');
 const now=validUtc(nowUtc);
 if(now===null||!Number.isFinite(maxAgeMinutes)||maxAgeMinutes<=0||!Number.isFinite(maxFutureSkewMinutes)||maxFutureSkewMinutes<0)throw new RangeError('Invalid clock or freshness policy');
 const selection=selectAeroDataBoxFlightV2(records,{number,originIata,destinationIata});
 if(selection.status!=='selected')return {accepted:false,reason:selection.status.toUpperCase(),candidates:selection.candidates,state:controller.getState()};
 const f=selection.flight,updated=validUtc(f.lastUpdatedUtc);
 const freshness=updated===null?'unknown':updated>now+maxFutureSkewMinutes*60000?'future':now-updated>maxAgeMinutes*60000?'stale':'fresh';
 // A possible runway event must NEVER be passed as a confirmed event.
 // The mock adapter used by the controller has a separate explicit confirmation field.
 const raw={
  number:f.flightNumber,status:f.status==='uncertain'?'unknown':f.status,
  stale:freshness!=='fresh'||f.status==='uncertain'||f.status==='unknown',
  departure:{airport:{iata:f.originIata}},
  arrival:{airport:{iata:f.destinationIata},
   scheduledTime:f.scheduledArrivalUtc?{utc:f.scheduledArrivalUtc}:undefined,
   revisedTime:f.revisedArrivalUtc?{utc:f.revisedArrivalUtc}:undefined}
 };
 // If a provider record is missing IATA destination, do not reuse a previous route.
 if(!f.destinationIata||!f.flightNumber)raw.stale=true;
 const result=controller.setFlight(raw,{
  observedAtUtc:updated===null?null:f.lastUpdatedUtc,
  requestVersion
 });
 return {...result,source:'AERODATABOX_V2_OFFLINE',freshness,
  confidence:freshness==='fresh'&&!raw.stale?'indicative':'unavailable',
  evidence:{possibleArrivalRunwayUtc:f.possibleArrivalRunwayUtc,
   possibleTakeoffUtc:f.possibleTakeoffUtc,
   actualArrivalRunwayUtc:null,uncertainty:[...f.uncertainty]}};
}
