import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createAcceleratedJourney} from './accelerated-journey.mjs';
test('full mock chain: available -> expired -> restored',()=>{
 const sim=createAcceleratedJourney();
 assert.equal(sim.initial.accepted,true);
 assert.equal(sim.state().recommendation.status,'indicative');
 assert.equal(sim.state().recommendation.recommendedDepartureUtc,'2027-05-15T15:25:00.000Z');
 assert.equal(sim.advanceMinutes(26).recommendation.status,'unavailable');
 assert.equal(sim.state().flightFreshness.status,'expired');
 assert.equal(sim.state().recommendation.recommendedDepartureUtc,null);
 const update=sim.receiveFreshObservation();
 assert.equal(update.accepted,true);
 assert.equal(sim.state().flightFreshness.status,'fresh');
 assert.equal(sim.state().recommendation.recommendedDepartureUtc,'2027-05-15T15:25:00.000Z');
});
test('new ETA after expiry produces new departure',()=>{
 const sim=createAcceleratedJourney();
 sim.advanceMinutes(26);
 sim.receiveFreshObservation('2027-05-15T16:05:00Z');
 assert.equal(sim.state().recommendation.recommendedDepartureUtc,'2027-05-15T15:40:00.000Z');
});
test('advance without network leaves versions unchanged',()=>{
 const sim=createAcceleratedJourney();const before=sim.state();
 sim.advanceMinutes(26);const after=sim.state();
 assert.equal(after.flightVersion,before.flightVersion);
 assert.equal(after.routeVersion,before.routeVersion);
});
test('at expiry boundary remains fresh; after 1 ms expires',()=>{
 const sim=createAcceleratedJourney({startUtc:'2027-05-15T14:00:00Z'});
 assert.equal(sim.advanceMinutes(30).flightFreshness.status,'fresh');
 assert.equal(sim.advanceMinutes(.00002).flightFreshness.status,'expired');
});
test('no fabricated landing from runwayTime',()=>{
 const sim=createAcceleratedJourney();
 assert.equal(sim.initial.evidence.actualArrivalRunwayUtc,null);
 assert.equal(sim.state().recommendation.arrivalKind,'estimated');
});
test('cannot advance backwards',()=>{
 const sim=createAcceleratedJourney();
 assert.throws(()=>sim.advanceMinutes(-1),RangeError);
});
