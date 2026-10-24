import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createCreditLedger} from './credit-ledger.mjs';
test('two simultaneous reservations cannot exceed capacity',async()=>{
 const l=createCreditLedger({limit:3});
 const results=await Promise.all(['a','b'].map(key=>Promise.resolve().then(()=>l.reserve({cost:2,key}))));
 assert.equal(results.filter(x=>x.ok).length,1);
 assert.equal(l.snapshot().reserved,2);
 assert.equal(l.snapshot().available,1);
});
test('100 parallel attempts never overdraw',async()=>{
 const l=createCreditLedger({limit:20});
 const r=await Promise.all(Array.from({length:100},(_,i)=>Promise.resolve().then(()=>l.reserve({key:'req-'+i,cost:2}))));
 assert.equal(r.filter(x=>x.ok).length,10);
 assert.equal(l.snapshot().available,0);assert.equal(l.snapshot().reserved,20);
});
test('idempotency replay does not charge again',()=>{
 const l=createCreditLedger({limit:5});
 const a=l.reserve({key:'same',cost:2}),b=l.reserve({key:'same',cost:2});
 assert.equal(a.reservationId,b.reservationId);
 assert.equal(l.snapshot().available,3);
});
test('same idempotency key different cost fails',()=>{
 const l=createCreditLedger({limit:5});l.reserve({key:'same',cost:2});
 assert.equal(l.reserve({key:'same',cost:3}).reason,'IDEMPOTENCY_CONFLICT');
});
test('success commits exactly once',()=>{
 const l=createCreditLedger({limit:4});l.reserve({key:'a',cost:2});
 assert.equal(l.settle('a',{charged:true}).ok,true);
 assert.equal(l.settle('a',{charged:true}).reason,'ALREADY_SETTLED');
 assert.deepEqual([l.snapshot().reserved,l.snapshot().committed,l.snapshot().available],[0,2,2]);
});
test('failure refunds only once',()=>{
 const l=createCreditLedger({limit:4});l.reserve({key:'a',cost:2});
 assert.equal(l.settle('a',{charged:false}).ok,true);
 assert.equal(l.settle('a',{charged:false}).reason,'ALREADY_SETTLED');
 assert.deepEqual([l.snapshot().reserved,l.snapshot().committed,l.snapshot().available],[0,0,4]);
});
test('unknown claim never refunds',()=>{
 const l=createCreditLedger({limit:4});
 assert.equal(l.settle('missing').reason,'UNKNOWN_RESERVATION');
});
test('invalid costs and keys rejected',()=>{
 const l=createCreditLedger({limit:4});
 assert.throws(()=>l.reserve({cost:-1,key:'a'}),RangeError);
 assert.throws(()=>l.reserve({cost:1,key:''}),TypeError);
});
test('previously refunded idempotency claim requires a new key',()=>{
 const l=createCreditLedger({limit:4});l.reserve({key:'a',cost:2});l.settle('a',{charged:false});
 assert.equal(l.reserve({key:'a',cost:2}).ok,false);
 assert.equal(l.reserve({key:'b',cost:2}).ok,true);
});
