/** B6.5 local-only accelerated display driver: injectable timers, no I/O. */
export function createLocalDisplayTicker({onTick,intervalMs=1000,setIntervalFn=setInterval,clearIntervalFn=clearInterval}={}){
 if(typeof onTick!=='function'||!Number.isFinite(intervalMs)||intervalMs<100)throw new TypeError('Valid onTick and intervalMs >=100 required');
 let handle=null;
 return Object.freeze({
  start(){if(handle!==null)return false;handle=setIntervalFn(onTick,intervalMs);return true},
  stop(){if(handle===null)return false;clearIntervalFn(handle);handle=null;return true},
  isRunning(){return handle!==null}
 });
}
