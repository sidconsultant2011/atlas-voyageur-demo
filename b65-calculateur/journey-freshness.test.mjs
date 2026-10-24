import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createJourneyController} from './journey-controller.mjs';
const T=Date.parse('2027-05-15T14:05:00Z');
const policy={maxAgeMinutes:30,maxFutureSkewMinutes:2};
function ready(nowValue=T){
 let clock=nowValue;
 const c=createJourneyController({freshnessPolicy:policy,now:()=>clock});
 c.selectFlightFixture('delayed',{observedAtUtc:'2027-05-15T14:00:00Z'});
 c.selectRouteFixture('rozay');
 return {c,setTime:t=>{clock=t}};
}
test('fresh flight yields normal indicative departure',()=>{
 const {c}=ready();assert.equal(c.getState().recommendation.status,'indicative');
 assert.equal(c.getState().flightFreshness.status,'fresh');
 assert.match(c.getState().recommendation.recommendedDepartureLocal,/17:25/);
});
test('flight expires even without new provider response',()=>{
 const {c,setTime}=ready();
 setTime(T+26*60000);
 const s=c.getState();assert.equal(s.flightFreshness.status,'expired');
 assert.equal(s.recommendation.status,'unavailable');
 assert.equal(s.recommendation.recommendedDepartureUtc,null);
 assert.ok(s.recommendation.errors.includes('FLIGHT_STALE'));
});
test('boundary valid at 30min, expires immediately after',()=>{
 const {c,setTime}=ready();setTime(T+25*60000);
 assert.equal(c.getState().flightFreshness.status,'fresh');
 setTime(T+25*60000+1);assert.equal(c.getState().flightFreshness.status,'expired');
});
test('future observation beyond skew blocks',()=>{
 const {c}=ready(T-8*60000);
 assert.equal(c.getState().flightFreshness.status,'future');
 assert.equal(c.getState().recommendation.status,'unavailable');
});
test('missing observation time blocks when policy enabled',()=>{
 const c=createJourneyController({freshnessPolicy:policy,now:()=>T});
 c.selectFlightFixture('delayed');c.selectRouteFixture('rozay');
 assert.equal(c.getState().flightFreshness.status,'unknown');
 assert.equal(c.getState().recommendation.status,'unavailable');
});
test('new observation restores advice after expiry',()=>{
 const {c,setTime}=ready();setTime(T+26*60000);
 assert.equal(c.getState().recommendation.status,'unavailable');
 c.selectFlightFixture('delayed',{observedAtUtc:'2027-05-15T14:32:00Z'});
 assert.equal(c.getState().flightFreshness.status,'fresh');
 assert.equal(c.getState().recommendation.status,'indicative');
});
test('expired flight cannot be revived by changing route',()=>{
 const {c,setTime}=ready();setTime(T+26*60000);
 c.selectRouteFixture('paris');
 assert.equal(c.getState().recommendation.status,'unavailable');
});
test('expired flight cannot be revived by changing margins',()=>{
 const {c,setTime}=ready();setTime(T+26*60000);
 c.setAssumptions({exitDelayMinutes:40,trafficBufferMinutes:10,otherTravelBufferMinutes:5,meetingMarginMinutes:0});
 assert.equal(c.getState().recommendation.status,'unavailable');
});
test('existing mock UI behavior stays unchanged without policy',()=>{
 const c=createJourneyController();c.selectFlightFixture('delayed');c.selectRouteFixture('rozay');
 assert.equal(c.getState().flightFreshness.status,'not_enforced');
 assert.match(c.getState().recommendation.recommendedDepartureLocal,/17:25/);
});
test('invalid freshness configuration is rejected',()=>{
 assert.throws(()=>createJourneyController({freshnessPolicy:{maxAgeMinutes:0}}),RangeError);
});
