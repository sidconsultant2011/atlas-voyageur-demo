/** B6.5 controlled fixtures only. No network, no provider credentials. */
export const mockFlights=Object.freeze({
 delayed:Object.freeze({number:'AV103',status:'airborne',arrival:{scheduledTime:{utc:'2027-05-15T15:35:00Z'},revisedTime:{utc:'2027-05-15T15:50:00Z'}},destination:{iata:'ORY'}}),
 landed:Object.freeze({number:'AV103',status:'arrived',arrival:{scheduledTime:{utc:'2027-05-15T15:35:00Z'},runwayTime:{utc:'2027-05-15T15:40:00Z',confirmed:true}},destination:{iata:'ORY'}}),
 cancelled:Object.freeze({number:'AV103',status:'cancelled',arrival:{scheduledTime:{utc:'2027-05-15T15:35:00Z'}},destination:{iata:'ORY'}}),
 stale:Object.freeze({number:'AV103',status:'airborne',stale:true,arrival:{scheduledTime:{utc:'2027-05-15T15:35:00Z'}},destination:{iata:'ORY'}}),
 missing:Object.freeze({number:'AV103',status:'unknown',arrival:{},destination:{iata:'ORY'}}),
 unconfirmed:Object.freeze({number:'AV103',status:'scheduled',arrival:{scheduledTime:{utc:'2027-05-15T15:35:00Z'},runwayTime:{utc:'2027-05-15T15:40:00Z',confirmed:false}},destination:{iata:'ORY'}})
});
export const mockRoutes=Object.freeze({
 rozay:Object.freeze({originSelected:true,destinationVerified:true,features:[{properties:{time:2700,distance:65100}}]}),
 paris:Object.freeze({originSelected:true,destinationVerified:true,features:[{properties:{time:1200,distance:19000}}]}),
 unavailable:Object.freeze({originSelected:true,destinationVerified:true,features:[]}),
 noOrigin:Object.freeze({originSelected:false,destinationVerified:true,features:[]}),
 noDestination:Object.freeze({originSelected:true,destinationVerified:false,features:[]})
});
const utc=s=>typeof s==='string'&&/(?:Z|[+-]\d\d:\d\d)$/.test(s)&&Number.isFinite(Date.parse(s))?new Date(s).toISOString():null;
export function adaptAeroDataBoxFixture(raw){
 if(!raw||typeof raw!=='object')throw new TypeError('Invalid flight fixture');
 const scheduledArrivalUtc=utc(raw.arrival?.scheduledTime?.utc);
 const revisedArrivalUtc=utc(raw.arrival?.revisedTime?.utc);
 // Never infer a landing from the presence of runwayTime alone.
 const actualArrivalRunwayUtc=raw.status==='arrived'&&raw.arrival?.runwayTime?.confirmed===true?utc(raw.arrival.runwayTime.utc):null;
 return {flightNumber:raw.number??null,destinationIata:raw.destination?.iata??null,status:raw.status??'unknown',stale:raw.stale===true,scheduledArrivalUtc,revisedArrivalUtc,actualArrivalRunwayUtc,source:'AeroDataBox MOCK'};
}
export function adaptGeoapifyFixture(raw){
 if(!raw||typeof raw!=='object')throw new TypeError('Invalid route fixture');
 const p=raw.features?.[0]?.properties;
 const durationSeconds=Number.isFinite(p?.time)&&p.time>=0?p.time:null;
 const distanceMeters=Number.isFinite(p?.distance)&&p.distance>=0?p.distance:null;
 return {originSelected:raw.originSelected===true,destinationVerified:raw.destinationVerified===true,durationSeconds,distanceMeters,trafficModel:'none',source:'Geoapify MOCK'};
}
