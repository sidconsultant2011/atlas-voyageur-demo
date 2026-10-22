/* ATLAS VOYAGEUR B6.2-PUBLIC — actualisation en ligne, secours hors-ligne sans API */
const CACHE = 'atlas-voyageur-dev-b63-champagne-v4';
const ASSETS = ['./index.html','./manifest.webmanifest','./i18n.js','./intro.js','./icons/icon-192.png','./icons/icon-512.png','./icons/icon-180.png'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>(k.startsWith('atlas-voyageur-public-')||k.startsWith('atlas-voyageur-dev-'))&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith(new URL(self.registration.scope).pathname)) return;
  if (/\/api\//.test(url.pathname)) { event.respondWith(new Response('API indisponible dans cette demonstration',{status:403}));return; }
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req, {cache:'no-store'})
        .then(response => {
          if (response.ok) {
            const copy = response.clone();
            event.waitUntil(caches.open(CACHE).then(cache=>cache.put('./index.html',copy)));
          }
          return response;
        })
        .catch(()=>caches.match('./index.html').then(r=>r||new Response('Installation hors ligne incomplete',{status:503})))
    );
    return;
  }
  event.respondWith(caches.match(req,{ignoreSearch:true}).then(r=>r||fetch(req)));
});
