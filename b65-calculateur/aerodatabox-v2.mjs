/** AeroDataBox RapidAPI FlightContract normalization V2 — offline only.
 * Schema: https://doc.aerodatabox.com/docs/openapi-rapidapi-v1.json (1.15.1.0)
 * Not a network client, not a claim of live confirmation.
 */
const STATUS={
 Unknown:'unknown',Expected:'scheduled',EnRoute:'airborne',CheckIn:'scheduled',
 Boarding:'scheduled',GateClosed:'scheduled',Departed:'airborne',
 Delayed:'delayed',Approaching:'airborne',Arrived:'arrived',
 Canceled:'cancelled',Diverted:'diverted',CanceledUncertain:'uncertain'
};
const absoluteUtc=v=>typeof v==='string'&&/(?:Z|[+-]\d\d:\d\d)$/.test(v)&&Number.isFinite(Date.parse(v))?new Date(v).toISOString():null;
const fromDateTime=v=>absoluteUtc(v?.utc);
const code=v=>typeof v==='string'&&v.trim()?v.trim().toUpperCase():null;
const quality=v=>typeof v==='string'?v:null;
function movement(raw){
 const v=raw&&typeof raw==='object'?raw:{};
 return {
  airportIata:code(v.airport?.iata),
  airportIcao:code(v.airport?.icao),
  airportTimeZone:typeof v.airport?.timeZone==='string'?v.airport.timeZone:null,
  scheduledUtc:fromDateTime(v.scheduledTime),
  revisedUtc:fromDateTime(v.revisedTime),
  predictedUtc:fromDateTime(v.predictedTime),
  runwayUtc:fromDateTime(v.runwayTime),
  terminal:typeof v.terminal==='string'&&v.terminal.trim()?v.terminal.trim():null,
  quality:quality(v.quality)
 };
}
export function normalizeAeroDataBoxV2(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new TypeError('FlightContract object required');
 const statusRaw=typeof raw.status==='string'?raw.status:'Unknown';
 const status=STATUS[statusRaw]??'unknown';
 const arrival=movement(raw.arrival),departure=movement(raw.departure);
 const uncertainty=[];
 if(!(statusRaw in STATUS))uncertainty.push('UNKNOWN_PROVIDER_STATUS');
 if(!arrival.airportIata&&!arrival.airportIcao)uncertainty.push('ARRIVAL_AIRPORT_UNKNOWN');
 if(!arrival.revisedUtc&&!arrival.scheduledUtc)uncertainty.push('ARRIVAL_TIME_UNKNOWN');
 if(arrival.runwayUtc)uncertainty.push('RUNWAY_TIME_NOT_INDEPENDENTLY_CONFIRMED');
 if(departure.runwayUtc)uncertainty.push('TAKEOFF_TIME_NOT_INDEPENDENTLY_CONFIRMED');
 const observedAtUtc=absoluteUtc(raw.lastUpdatedUtc);
 if(!observedAtUtc)uncertainty.push('SOURCE_UPDATE_TIME_UNKNOWN');
 // IMPORTANT: flight status + runwayTime alone cannot establish observed runway event.
 // Keep runway timestamps in evidence; never forward them as actualArrivalRunwayUtc.
 return {
  flightNumber:code(raw.number),status,statusRaw,source:'AeroDataBox OpenAPI 1.15.1.0 — OFFLINE',
  codeshareStatus:typeof raw.codeshareStatus==='string'?raw.codeshareStatus:null,
  lastUpdatedUtc:observedAtUtc,
  originIata:departure.airportIata,destinationIata:arrival.airportIata,
  departure,arrival,scheduledArrivalUtc:arrival.scheduledUtc,
  revisedArrivalUtc:arrival.revisedUtc,
  predictedArrivalUtc:arrival.predictedUtc,
  actualArrivalRunwayUtc:null,
  actualTakeoffUtc:null,
  possibleArrivalRunwayUtc:arrival.runwayUtc,
  possibleTakeoffUtc:departure.runwayUtc,
  arrivalTerminal:arrival.terminal,uncertainty,
  stale:false
 };
}
export function selectAeroDataBoxFlightV2(items,{number=null,originIata=null,destinationIata=null}={}){
 if(!Array.isArray(items))throw new TypeError('Flight Status endpoint returns an array');
 let flights=items.map(normalizeAeroDataBoxV2);
 if(number)flights=flights.filter(x=>x.flightNumber===code(number));
 if(originIata)flights=flights.filter(x=>x.originIata===code(originIata));
 if(destinationIata)flights=flights.filter(x=>x.destinationIata===code(destinationIata));
 return flights.length===1?{status:'selected',flight:flights[0],candidates:1}:
 {status:flights.length?'ambiguous':'not_found',flight:null,candidates:flights.length};
}
