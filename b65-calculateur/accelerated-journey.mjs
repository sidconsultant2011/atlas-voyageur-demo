/** B6.5 — accelerated clock, offline flight V2 + mock route + departure calculation.
 * No timers or network. All transitions are deterministic and driven by advanceMinutes().
 */
import {createJourneyController} from './journey-controller.mjs';
import {applyAeroDataBoxV2Offline} from './aerodatabox-v2-controller.mjs';
const min=60000;
const asUtc=t=>new Date(t).toISOString();
export function createAcceleratedJourney({
 startUtc='2027-05-15T14:05:00Z',sourceAtUtc='2027-05-15T14:00:00Z',
 maxAgeMinutes=30
}={}){
 let now=Date.parse(startUtc);
 if(!Number.isFinite(now)||!Number.isFinite(maxAgeMinutes)||maxAgeMinutes<=0)throw new RangeError('Invalid simulated clock');
 const controller=createJourneyController({now:()=>now,freshnessPolicy:{maxAgeMinutes,maxFutureSkewMinutes:2}});
 const makeFlight=(observedAtUtc, revised='2027-05-15T15:50:00Z')=>({
  number:'AV103',status:'Delayed',lastUpdatedUtc:observedAtUtc,
  departure:{airport:{iata:'CDG'}},
  arrival:{airport:{iata:'ORY'},scheduledTime:{utc:'2027-05-15T15:35:00Z'},
   revisedTime:{utc:revised},runwayTime:{utc:'2027-05-15T15:42:00Z'}}
 });
 const observation=(stamp,revised)=>applyAeroDataBoxV2Offline(controller,[makeFlight(stamp,revised)],{
  nowUtc:asUtc(now),maxAgeMinutes});
 controller.selectRouteFixture('rozay');
 const initial=observation(sourceAtUtc);
 const state=()=>({
  nowUtc:asUtc(now),
  ...controller.getState()
 });
 const advanceMinutes=n=>{
  if(!Number.isFinite(n)||n<0)throw new RangeError('Advance must be nonnegative');
  now+=n*min;return state();
 };
 const receiveFreshObservation=(revised)=>observation(asUtc(now),revised);
 return Object.freeze({state,advanceMinutes,receiveFreshObservation,initial});
}
