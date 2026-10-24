import {test} from 'node:test';import assert from 'node:assert/strict';
import {createLocalDisplayTicker} from './local-display-ticker.mjs';
import {createAcceleratedJourney} from './accelerated-journey.mjs';
test('local clock tick: available -> expired -> refreshed without API',()=>{
 const simulation=createAcceleratedJourney();let tick;
 const ticker=createLocalDisplayTicker({onTick:()=>simulation.advanceMinutes(1),setIntervalFn:fn=>{tick=fn;return 1},clearIntervalFn:()=>{tick=null}});
 assert.equal(ticker.start(),true);assert.equal(ticker.start(),false);
 assert.equal(simulation.state().recommendation.status,'indicative');
 for(let i=0;i<25;i++)tick();
 assert.equal(simulation.state().recommendation.status,'indicative');
 tick();assert.equal(simulation.state().flightFreshness.status,'expired');
 assert.equal(simulation.state().recommendation.status,'unavailable');
 simulation.receiveFreshObservation();assert.equal(simulation.state().recommendation.status,'indicative');
 assert.equal(ticker.stop(),true);assert.equal(ticker.isRunning(),false);
});
test('stopping local ticker prevents further scheduled ticks',()=>{
 let count=0,fn,cleared=false;
 const ticker=createLocalDisplayTicker({onTick:()=>count++,setIntervalFn:cb=>{fn=cb;return 123},clearIntervalFn:id=>{assert.equal(id,123);cleared=true}});
 ticker.start();fn();assert.equal(count,1);ticker.stop();assert.equal(cleared,true);assert.equal(ticker.stop(),false);
});
