/** B6.5 OFFLINE ledger. Atomic synchronous reservation before any awaited operation.
 * Single-process simulation only; distributed implementation must use a database transaction.
 */
export function createCreditLedger({limit=10}={}){
 if(!Number.isSafeInteger(limit)||limit<0)throw new RangeError('Invalid limit');
 let available=limit,reserved=0,committed=0,counter=0;
 const claims=new Map();
 const snapshot=()=>Object.freeze({limit,available,reserved,committed,activeReservations:[...claims.values()].filter(x=>x.state==='reserved').length});
 return Object.freeze({
  snapshot,
  reserve({cost,key}={}){
   if(!Number.isSafeInteger(cost)||cost<=0)throw new RangeError('Invalid cost');
   if(typeof key!=='string'||!key.trim())throw new TypeError('Idempotency key required');
   if(claims.has(key)){
    const v=claims.get(key);
    if(v.cost!==cost)return {ok:false,reason:'IDEMPOTENCY_CONFLICT'};
    return {ok:v.state!=='refunded',reason:'REPLAY',reservationId:v.id,state:v.state};
   }
   if(available<cost)return {ok:false,reason:'BUDGET_EXHAUSTED'};
   // No await before these mutations: atomic in this event loop.
   available-=cost;reserved+=cost;
   const v={id:'reservation-'+(++counter),key,cost,state:'reserved'};
   claims.set(key,v);return {ok:true,reservationId:v.id,state:v.state};
  },
  settle(key,{charged=true}={}){
   const v=claims.get(key);
   if(!v)return {ok:false,reason:'UNKNOWN_RESERVATION'};
   if(v.state!=='reserved')return {ok:false,reason:'ALREADY_SETTLED',state:v.state};
   reserved-=v.cost;
   if(charged){committed+=v.cost;v.state='committed'}
   else{available+=v.cost;v.state='refunded'}
   return {ok:true,state:v.state};
  }
 });
}
