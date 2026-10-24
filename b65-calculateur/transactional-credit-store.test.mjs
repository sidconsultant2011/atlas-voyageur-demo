import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createTransactionStore,createTransactionalCreditService} from './transactional-credit-store.mjs';
test('100 requests across 4 instances never exceed shared budget',async()=>{
 const store=createTransactionStore({limit:20});
 const nodes=Array.from({length:4},(_,i)=>createTransactionalCreditService({store,instanceId:'node'+i}));
 const result=await Promise.all(Array.from({length:100},(_,i)=>nodes[i%4].reserve({key:'req'+i,cost:2})));
 assert.equal(result.filter(x=>x.ok).length,10);
 assert.equal(store.snapshot().reserved,20);
 assert.equal(store.snapshot().available,0);
});
test('two instances share idempotency reservation',async()=>{
 const store=createTransactionStore({limit:4}),a=createTransactionalCreditService({store}),b=createTransactionalCreditService({store});
 const [x,y]=await Promise.all([a.reserve({key:'same',cost:3}),b.reserve({key:'same',cost:3})]);
 assert.equal(x.ok,true);assert.equal(y.reason==='REPLAY'||x.reason==='REPLAY',true);
 assert.equal(store.snapshot().reserved,3);
});
test('conflicting reuse of key is rejected',async()=>{
 const store=createTransactionStore(),s=createTransactionalCreditService({store});
 await s.reserve({key:'a',cost:2});assert.equal((await s.reserve({key:'a',cost:3})).reason,'IDEMPOTENCY_CONFLICT');
});
test('commit is exactly once from competing nodes',async()=>{
 const store=createTransactionStore({limit:5}),a=createTransactionalCreditService({store}),b=createTransactionalCreditService({store});
 await a.reserve({key:'a',cost:3});
 const settled=await Promise.all([a.settle('a',{charged:true}),b.settle('a',{charged:true})]);
 assert.equal(settled.filter(x=>x.ok).length,1);
 assert.equal(store.snapshot().committed,3);
});
test('unbilled failed operation refunds once',async()=>{
 const store=createTransactionStore({limit:5}),a=createTransactionalCreditService({store});
 await a.reserve({key:'a',cost:3});await a.settle('a',{charged:false});
 assert.equal(store.snapshot().available,5);
 assert.equal((await a.settle('a',{charged:false})).reason,'ALREADY_SETTLED');
});
test('crash/timeout reservation does not silently refund',async()=>{
 let clock=1000;const store=createTransactionStore({limit:5,now:()=>clock}),a=createTransactionalCreditService({store,instanceId:'crashed'});
 await a.reserve({key:'a',cost:3,ttlMs:100});
 clock=1200;
 const resumed=createTransactionalCreditService({store,instanceId:'restarted'});
 assert.equal((await resumed.recover()).reconciliationRequired,1);
 assert.equal(store.snapshot().available,2);
 assert.equal(store.snapshot().reserved,3);
 assert.equal((await resumed.reserve({key:'a',cost:3})).state,'reconciliation_required');
});
test('unknown charge outcome blocks settlement',async()=>{
 const store=createTransactionStore(),a=createTransactionalCreditService({store});
 await a.reserve({key:'a',cost:2});
 assert.equal((await a.settle('a',{})).reason,'CHARGE_STATUS_UNKNOWN');
});
test('transaction queue survives rejected validation',async()=>{
 const store=createTransactionStore(),a=createTransactionalCreditService({store});
 await assert.rejects(a.reserve({key:'bad',cost:-1}),RangeError);
 assert.equal((await a.reserve({key:'good',cost:1})).ok,true);
});
test('accounting invariant after mixed outcomes',async()=>{
 const store=createTransactionStore({limit:10}),a=createTransactionalCreditService({store});
 await a.reserve({key:'a',cost:2});await a.reserve({key:'b',cost:3});
 await a.settle('a',{charged:true});await a.settle('b',{charged:false});
 const x=store.snapshot();assert.equal(x.available+x.reserved+x.committed,x.limit);
});
