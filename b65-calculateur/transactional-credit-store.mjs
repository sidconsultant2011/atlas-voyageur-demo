/** B6.5 offline multi-instance transaction model.
 * Shared durable-state simulator, serialized transactions, no network or external DB.
 * Real implementation must replace store.transaction() by a durable ACID transaction.
 */
export function createTransactionStore({limit=20,now=()=>Date.now()}={}){
 if(!Number.isSafeInteger(limit)||limit<0)throw new RangeError('Invalid limit');
 const data={limit,available:limit,reserved:0,committed:0,claims:new Map()};
 let queue=Promise.resolve();
 return Object.freeze({
  transaction(fn){
   const next=queue.then(()=>fn(data));
   queue=next.then(()=>undefined,()=>undefined);
   return next;
  },
  snapshot:()=>({limit:data.limit,available:data.available,reserved:data.reserved,committed:data.committed,claims:[...data.claims.values()].map(x=>({...x}))}),
  now
 });
}
export function createTransactionalCreditService({store,instanceId='instance'}={}){
 if(!store||typeof store.transaction!=='function')throw new TypeError('Shared store required');
 const reserve=({key,cost,ttlMs=60000}={})=>store.transaction(db=>{
  if(typeof key!=='string'||!key.trim()||!Number.isSafeInteger(cost)||cost<=0||!Number.isSafeInteger(ttlMs)||ttlMs<=0)throw new RangeError('Invalid reservation');
  const existing=db.claims.get(key);
  if(existing)return existing.cost!==cost?{ok:false,reason:'IDEMPOTENCY_CONFLICT'}:{ok:existing.state!=='released',reason:'REPLAY',state:existing.state,key};
  if(db.available<cost)return {ok:false,reason:'BUDGET_EXHAUSTED'};
  const claim={key,cost,state:'reserved',createdAt:store.now(),expiresAt:store.now()+ttlMs,owner:instanceId};
  db.available-=cost;db.reserved+=cost;db.claims.set(key,claim);
  return {ok:true,key,state:'reserved'};
 });
 const settle=(key,{charged}={})=>store.transaction(db=>{
  const x=db.claims.get(key);
  if(!x)return {ok:false,reason:'UNKNOWN_RESERVATION'};
  if(x.state!=='reserved')return {ok:false,reason:'ALREADY_SETTLED',state:x.state};
  if(typeof charged!=='boolean')return {ok:false,reason:'CHARGE_STATUS_UNKNOWN'};
  db.reserved-=x.cost;
  if(charged){db.committed+=x.cost;x.state='committed'}else{db.available+=x.cost;x.state='released'}
  return {ok:true,state:x.state};
 });
 // Expired reservations become 'reconciliation_required' instead of being refunded:
 // provider may have billed even if application crashed.
 const recover=()=>store.transaction(db=>{
  let changed=0;
  for(const x of db.claims.values()){
   if(x.state==='reserved'&&x.expiresAt<=store.now()){x.state='reconciliation_required';changed++}
  }
  return {reconciliationRequired:changed};
 });
 return Object.freeze({reserve,settle,recover,snapshot:store.snapshot});
}
