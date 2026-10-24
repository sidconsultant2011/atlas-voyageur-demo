import {planDeparture} from './atlas-depart-engine.mjs';
import {mockFlights,mockRoutes,adaptAeroDataBoxFixture,adaptGeoapifyFixture} from './mock-adapters.mjs';
export const DEFAULT_ASSUMPTIONS=Object.freeze({exitDelayMinutes:40,trafficBufferMinutes:15,otherTravelBufferMinutes:5,meetingMarginMinutes:0});
export function simulatePickup({flightScenario='delayed',routeScenario='rozay',assumptions=DEFAULT_ASSUMPTIONS}={}){
 if(!Object.hasOwn(mockFlights,flightScenario)||!Object.hasOwn(mockRoutes,routeScenario))throw new RangeError('Unknown fixture name');
 const flight=adaptAeroDataBoxFixture(mockFlights[flightScenario]);
 const road=adaptGeoapifyFixture(mockRoutes[routeScenario]);
 const recommendation=planDeparture({flight,road,assumptions});
 return {flight,road,recommendation,mode:'MOCK_ONLY'};
}
