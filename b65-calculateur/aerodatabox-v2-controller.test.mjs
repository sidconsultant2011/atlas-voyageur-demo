import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createJourneyController} from './journey-controller.mjs';
import {applyAeroDataBoxV2Offline} from './aerodatabox-v2-controller.mjs';
const dt=s=>({utc:s});
const source=(status='Delayed',updated='2027-05-15T14:00:00Z')=>({
 number:'AV103',status,lastUpdatedUtc:updated,
 departure:{airport:{iata:'CDG'},runwayTime:dt('2027-05-15T12:10:00Z')},
 arrival:{airport:{iata:'ORY'},scheduledTime:dt('2027-05-15T15:35:00Z'),revisedTime:dt('2027-05-15T15:50:00Z'),runwayTime:dt('2027-05-15T15:42:00Z')}
});
const cWithRoad=()=>{const c=createJourneyController();c.selectRouteFixture('rozay');return c};
test('V2 offline normal flight makes indicative 17:25, not runway',()=>{
 const c=cWithRoad(),res=applyAeroDataBoxV2Offline(c,[source()],{number:'AV103'});
 assert.equal(res.accepted,true);assert.equal(res.freshness,'fresh');assert.equal(res.evidence.actualArrivalRunwayUtc,null);
 assert.equal(c.getState().recommendation.recommendedDepartureUtc,'2027-05-15T15:25:00.000Z');
 assert.equal(c.getState().recommendation.arrivalKind,'estimated');
});
test('runway time on Arrived is not confirmation',()=>{
 const c=cWithRoad(),res=applyAeroDataBoxV2Offline(c,[source('Arrived')]);
 assert.equal(res.evidence.possibleArrivalRunwayUtc,'2027-05-15T15:42:00.000Z');
 assert.equal(c.getState().recommendation.arrivalKind,'estimated');
});
test('expired update suspends previous advice',()=>{
 const c=cWithRoad();applyAeroDataBoxV2Offline(c,[source()]);
 const r=applyAeroDataBoxV2Offline(c,[source('Delayed','2027-05-15T14:20:00Z')],{nowUtc:'2027-05-15T15:10:00Z'});
 assert.equal(r.freshness,'stale');assert.ok(c.getState().recommendation.errors.includes('FLIGHT_STALE'));
});
test('missing provider timestamp is unknown and unsafe',()=>{
 const c=cWithRoad();const r=applyAeroDataBoxV2Offline(c,[source('Delayed',null)]);
 assert.equal(r.freshness,'unknown');assert.equal(c.getState().recommendation.status,'unavailable');
});
test('future source update beyond tolerance is unsafe',()=>{
 const c=cWithRoad(),r=applyAeroDataBoxV2Offline(c,[source('Delayed','2027-05-15T14:20:00Z')]);
 assert.equal(r.freshness,'future');assert.equal(c.getState().recommendation.status,'unavailable');
});
test('cancelled provider status suspends',()=>{
 const c=cWithRoad();applyAeroDataBoxV2Offline(c,[source('Canceled')]);
 assert.ok(c.getState().recommendation.errors.includes('FLIGHT_NOT_SERVICEABLE'));
});
test('uncertain provider status suspends',()=>{
 const c=cWithRoad();applyAeroDataBoxV2Offline(c,[source('CanceledUncertain')]);
 assert.equal(c.getState().recommendation.status,'unavailable');
});
test('ambiguous results never replace current flight',()=>{
 const c=cWithRoad();applyAeroDataBoxV2Offline(c,[source()]);
 const r=applyAeroDataBoxV2Offline(c,[source(),{...source(),number:'AV104'}]);
 assert.equal(r.reason,'AMBIGUOUS');assert.equal(r.accepted,false);
 assert.equal(c.getState().flight.flightNumber,'AV103');
});
test('empty selection does not invent a flight',()=>{
 const c=cWithRoad(),r=applyAeroDataBoxV2Offline(c,[]);
 assert.equal(r.reason,'NOT_FOUND');assert.equal(c.getState().recommendation.status,'unavailable');
});
test('older source data cannot overwrite latest accepted record',()=>{
 const c=cWithRoad();applyAeroDataBoxV2Offline(c,[source('Delayed','2027-05-15T14:04:00Z')]);
 const r=applyAeroDataBoxV2Offline(c,[source('Expected','2027-05-15T14:00:00Z')]);
 assert.equal(r.accepted,false);assert.equal(r.reason,'OLDER_OBSERVATION');
});
test('superseded request is ignored',()=>{
 const c=cWithRoad(),version=c.getRequestVersions().flightVersion;
 applyAeroDataBoxV2Offline(c,[source()]);
 const r=applyAeroDataBoxV2Offline(c,[source()],{requestVersion:version});
 assert.equal(r.reason,'SUPERSEDED_REQUEST');
});
test('changed destination invalidates previous route',()=>{
 const c=cWithRoad();applyAeroDataBoxV2Offline(c,[source()]);
 const changed={...source('Delayed','2027-05-15T14:02:00Z'),arrival:{...source().arrival,airport:{iata:'CDG'}}};
 applyAeroDataBoxV2Offline(c,[changed]);
 assert.equal(c.getState().road,null);
 assert.equal(c.getState().recommendation.status,'unavailable');
});
test('missing destination prevents advice',()=>{
 const c=cWithRoad();const f=source();f.arrival={...f.arrival,airport:{}};
 applyAeroDataBoxV2Offline(c,[f]);
 assert.equal(c.getState().recommendation.status,'unavailable');
});
