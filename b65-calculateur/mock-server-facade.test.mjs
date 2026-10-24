import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createMockFacade} from './mock-server-facade.mjs';
const start=Date.parse('2027-05-15T14:05:00Z');
const open=(f,token='opaque-owner-123456')=>{
 const created=f.createSession({ownerToken:token});
 assert.equal(created.httpStatus,201);
 const {journeyId,sessionToken}=created.data;
 return (op,body={})=>f.call(op,{journeyId,sessionToken,body});
};
test('full in-process flow: flight address route advice',()=>{
 const f=createMockFacade({now:()=>start}),call=open(f);
 assert.equal(call('flight.search',{number:'AV103'}).data.candidates.length,1);
 call('flight.select',{candidateId:'fixture-delayed'});
 call('origin.geocode',{text:'adresse fictive à Rozay'});
 const origin=call('origin.select',{originId:'mock-rozay'});
 const route=call('route.calculate',{originVersion:origin.data.originVersion});
 assert.equal(route.data.durationSeconds,2700);
 assert.match(call('recommendation').data.recommendation.recommendedDepartureLocal,/17:25/);
 assert.equal(f.metrics().spent,4);
});
test('unauthorized session and token isolation',()=>{
 const f=createMockFacade({now:()=>start});
 const a=f.createSession({ownerToken:'owner-111111111'}).data,b=f.createSession({ownerToken:'owner-222222222'}).data;
 assert.equal(f.call('recommendation',{journeyId:a.journeyId,sessionToken:b.sessionToken}).httpStatus,404);
 assert.equal(f.call('recommendation',{journeyId:'random',sessionToken:a.sessionToken}).httpStatus,404);
});
test('missing owner token denied',()=>assert.equal(createMockFacade().createSession({ownerToken:'x'}).httpStatus,401));
test('invalid inputs are blocked before credits',()=>{
 const f=createMockFacade({now:()=>start}),call=open(f);
 assert.equal(call('flight.search',{number:'<script>'}).httpStatus,400);
 assert.equal(call('origin.geocode',{text:'a'}).httpStatus,400);
 assert.equal(f.metrics().spent,0);
});
test('identical flight search uses cache',()=>{
 const f=createMockFacade({now:()=>start}),call=open(f);
 call('flight.search',{number:'AV103'});call('flight.search',{number:'AV103'});
 assert.equal(f.metrics().spent,2);
});
test('cache expires and consumes again',()=>{
 let t=start;const f=createMockFacade({now:()=>t,cacheMs:1000}),call=open(f);
 call('flight.search',{number:'AV103'});t+=1001;call('flight.search',{number:'AV103'});
 assert.equal(f.metrics().spent,4);
});
test('budget hard stops supplier mock operation',()=>{
 const f=createMockFacade({now:()=>start,budget:1}),call=open(f);
 assert.equal(call('flight.search',{number:'AV103'}).errors[0].code,'BUDGET_EXHAUSTED');
 assert.equal(f.metrics().spent,0);
});
test('session rate limit blocks distinct requests',()=>{
 const f=createMockFacade({now:()=>start,maxCallsPerSession:1}),call=open(f);
 call('origin.geocode',{text:'adresse fictive 1'});
 assert.equal(call('origin.geocode',{text:'adresse fictive 2'}).errors[0].code,'RATE_LIMITED');
});
test('stale origin version cannot calculate route',()=>{
 const f=createMockFacade({now:()=>start}),call=open(f);
 call('flight.select',{candidateId:'fixture-delayed'});
 const x=call('origin.select',{originId:'mock-rozay'});
 assert.equal(call('route.calculate',{originVersion:x.data.originVersion-1}).errors[0].code,'STALE_STATE_VERSION');
});
test('offline refresh is explicitly disabled',()=>{
 const f=createMockFacade({now:()=>start}),call=open(f);
 assert.equal(call('flight.refresh').errors[0].code,'RATE_LIMITED');
 assert.equal(f.metrics().spent,0);
});
test('expired session is denied',()=>{
 let t=start;const f=createMockFacade({now:()=>t}),session=f.createSession({ownerToken:'owner-123456789'}).data;
 t+=3600001;
 assert.equal(f.call('recommendation',{journeyId:session.journeyId,sessionToken:session.sessionToken}).httpStatus,404);
});
test('unknown operation fails closed',()=>{
 const f=createMockFacade({now:()=>start}),call=open(f);
 assert.equal(call('proxy.external',{url:'https://example.org'}).httpStatus,404);
});
