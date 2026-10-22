/** ATLAS VOYAGEUR B6.5 - Pure calculation engine. No HTTP, API keys or storage. */
const minute=60000;
const validNumber=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
const parseInstant=v=>typeof v==='string'&&/(?:Z|[+-]\d\d:\d\d)$/.test(v)&&Number.isFinite(Date.parse(v))?Date.parse(v):null;
const iso=t=>new Date(t).toISOString();
export function formatLocal(utc,zone='Europe/Paris',locale='fr-FR'){
 if(parseInstant(utc)===null)return null;
 try{return new Intl.DateTimeFormat(locale,{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date(utc));}catch{return null}
}
export function planDeparture({flight={},road={},assumptions={},displayZone='Europe/Paris',locale='fr-FR'}={}){
 const options=[['actualArrivalRunwayUtc','observed'],['revisedArrivalUtc','estimated'],['scheduledArrivalUtc','scheduled']];
 let arrival=null,arrivalKind='unknown';
 for(const [key,kind] of options){const t=parseInstant(flight[key]);if(t!==null){arrival=t;arrivalKind=kind;break}}
 const errors=[];
 if(arrival===null)errors.push('ARRIVAL_UNAVAILABLE');
 if(['cancelled','diverted'].includes(flight.status))errors.push('FLIGHT_NOT_SERVICEABLE');
 if(flight.stale===true)errors.push('FLIGHT_STALE');
 if(!road.originSelected)errors.push('ORIGIN_NOT_SELECTED');
 if(!road.destinationVerified)errors.push('DESTINATION_NOT_VERIFIED');
 if(!validNumber(road.durationSeconds))errors.push('ROUTE_UNAVAILABLE');
 const fields=['exitDelayMinutes','trafficBufferMinutes','otherTravelBufferMinutes','meetingMarginMinutes'];
 for(const k of fields)if(!validNumber(assumptions[k]))errors.push('MISSING_'+k);
 if(errors.length)return {status:'unavailable',errors:[...new Set(errors)],arrivalKind,recommendedDepartureUtc:null};
 const roadMinutes=Math.ceil(road.durationSeconds/60);
 const expectedMeeting=arrival+assumptions.exitDelayMinutes*minute;
 const buffersMinutes=assumptions.trafficBufferMinutes+assumptions.otherTravelBufferMinutes+assumptions.meetingMarginMinutes;
 const recommended=expectedMeeting-(roadMinutes+buffersMinutes)*minute;
 return {status:'indicative',arrivalKind,arrivalBasisUtc:iso(arrival),expectedMeetingUtc:iso(expectedMeeting),recommendedDepartureUtc:iso(recommended),recommendedDepartureLocal:formatLocal(iso(recommended),displayZone,locale),expectedMeetingLocal:formatLocal(iso(expectedMeeting),displayZone,locale),roadMinutes,buffersMinutes,exitDelayMinutes:assumptions.exitDelayMinutes,assumptions:{...assumptions},notes:['Road estimate excludes verified live traffic','Passenger exit duration is assumed','No provider call made']};
}