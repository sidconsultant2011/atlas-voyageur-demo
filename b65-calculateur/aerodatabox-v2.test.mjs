import {test} from 'node:test';
import assert from 'node:assert/strict';
import {normalizeAeroDataBoxV2,selectAeroDataBoxFlightV2} from './aerodatabox-v2.mjs';
const d=s=>({utc:s,local:'2027-05-15 17:35+02:00'});
const valid={
 number:'AV103',status:'Delayed',codeshareStatus:'IsOperator',lastUpdatedUtc:'2027-05-15T14:00:00Z',
 departure:{airport:{iata:'CDG',icao:'LFPG'},quality:['Basic'],scheduledTime:d('2027-05-15T12:00:00Z')},
 arrival:{airport:{iata:'ORY',icao:'LFPO'},quality:['Basic'],
 scheduledTime:d('2027-05-15T15:35:00Z'),revisedTime:d('2027-05-15T15:50:00Z'),
 terminal:' 1 '}
};
test('normalizes revised, scheduled and IATA codes',()=>{
 const x=normalizeAeroDataBoxV2(valid);
 assert.equal(x.status,'delayed');assert.equal(x.revisedArrivalUtc,'2027-05-15T15:50:00.000Z');
 assert.equal(x.scheduledArrivalUtc,'2027-05-15T15:35:00.000Z');assert.equal(x.destinationIata,'ORY');
 assert.equal(x.arrivalTerminal,'1');assert.equal(x.actualArrivalRunwayUtc,null);
});
test('ISO local-only time is never used as UTC',()=>{
 const x=normalizeAeroDataBoxV2({...valid,arrival:{...valid.arrival,revisedTime:{local:'2027-05-15 17:50'}}});
 assert.equal(x.revisedArrivalUtc,null);
});
test('absence of arrival fields remains null',()=>{
 const x=normalizeAeroDataBoxV2({...valid,arrival:{airport:{iata:'ORY'}}});
 assert.equal(x.scheduledArrivalUtc,null);assert.equal(x.revisedArrivalUtc,null);assert.ok(x.uncertainty.includes('ARRIVAL_TIME_UNKNOWN'));
});
test('status enums preserve distinctions',()=>{
 const pairs={Unknown:'unknown',Expected:'scheduled',EnRoute:'airborne',CheckIn:'scheduled',Boarding:'scheduled',GateClosed:'scheduled',Departed:'airborne',Delayed:'delayed',Approaching:'airborne',Arrived:'arrived',Canceled:'cancelled',Diverted:'diverted',CanceledUncertain:'uncertain'};
 for(const [raw,want] of Object.entries(pairs))assert.equal(normalizeAeroDataBoxV2({...valid,status:raw}).status,want,raw);
});
test('unknown future status fails safe',()=>{
 const x=normalizeAeroDataBoxV2({...valid,status:'Taxiing'});
 assert.equal(x.status,'unknown');assert.ok(x.uncertainty.includes('UNKNOWN_PROVIDER_STATUS'));
});
test('a runway timestamp is not independently verified',()=>{
 const x=normalizeAeroDataBoxV2({...valid,status:'Arrived',arrival:{...valid.arrival,runwayTime:d('2027-05-15T15:42:00Z')}});
 assert.equal(x.status,'arrived');assert.equal(x.actualArrivalRunwayUtc,null);
 assert.equal(x.possibleArrivalRunwayUtc,'2027-05-15T15:42:00.000Z');
 assert.ok(x.uncertainty.includes('RUNWAY_TIME_NOT_INDEPENDENTLY_CONFIRMED'));
});
test('departure runway is not treated as confirmed takeoff',()=>{
 const x=normalizeAeroDataBoxV2({...valid,departure:{...valid.departure,runwayTime:d('2027-05-15T12:23:00Z')}});
 assert.equal(x.actualTakeoffUtc,null);
 assert.equal(x.possibleTakeoffRunwayUtc,undefined);
 assert.equal(x.possibleTakeoffUtc,'2027-05-15T12:23:00.000Z');
});
test('null or malformed update time flagged',()=>{
 const x=normalizeAeroDataBoxV2({...valid,lastUpdatedUtc:'today'});
 assert.equal(x.lastUpdatedUtc,null);assert.ok(x.uncertainty.includes('SOURCE_UPDATE_TIME_UNKNOWN'));
});
test('unparseable UTC and missing airport handled',()=>{
 const x=normalizeAeroDataBoxV2({...valid,arrival:{scheduledTime:{utc:'nonsense'}}});
 assert.equal(x.scheduledArrivalUtc,null);assert.equal(x.destinationIata,null);
});
test('Flight Status multiple matches never auto-select',()=>{
 const x=selectAeroDataBoxFlightV2([valid,{...valid,number:'AV104'}]);
 assert.equal(x.status,'ambiguous');assert.equal(x.flight,null);
});
test('user filters disambiguate flight numbers',()=>{
 const x=selectAeroDataBoxFlightV2([valid,{...valid,number:'AV104'}],{number:'av103',destinationIata:'ORY'});
 assert.equal(x.status,'selected');assert.equal(x.flight.flightNumber,'AV103');
});
test('no results and invalid payload handled',()=>{
 assert.equal(selectAeroDataBoxFlightV2([]).status,'not_found');
 assert.throws(()=>selectAeroDataBoxFlightV2({}),TypeError);
 assert.throws(()=>normalizeAeroDataBoxV2(null),TypeError);
});
