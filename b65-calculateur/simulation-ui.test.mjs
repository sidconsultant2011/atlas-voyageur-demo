/** Offline smoke test: executes the actual B6.5 HTML module with a minimal DOM stand-in.
 * No browser, downloads, keys, live APIs, Playwright or npm dependencies.
 */
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {resolve,dirname} from 'node:path';

test('B6.5 simulation page: events and result remain coherent',async()=>{
 const base=resolve(dirname(fileURLToPath(import.meta.url)),'..');
 const html=readFileSync(resolve(base,'RECETTE-B65-PARCOURS-COMPLET.html'),'utf8');
 assert.match(html,/<script type="module">/);
 assert.doesNotMatch(html,/fetch\s*\(|https?:\/\/api\.geoapify\.com|rapidapi\.com/i);
 const match=html.match(/<script type="module">([\s\S]*?)<\/script>/);
 assert.ok(match,'Inline UI module not found');
 const ids=['scenario','origin','route-mode','exit','traffic','buffer','margin','calculate','from','basis','arrival','departure','date','departure-utc','explanation','details','flight-number','flight-origin','flight-destination','flight-status','flight-source','freshness','route-source','route-diagram'];
 const defaults={scenario:'revised',origin:'rozay','route-mode':'available',exit:'40',traffic:'15',buffer:'5',margin:'0'};
 const elements=Object.fromEntries(ids.map(id=>[id,{
  value:defaults[id]??'',textContent:'',
  events:{},addEventListener(name,fn){this.events[name]=fn},
  fire(name){assert.equal(typeof this.events[name],'function',id+' missing '+name);this.events[name]()}
 }]));
 const previous=globalThis.document;
 globalThis.document={getElementById(id){assert.ok(Object.hasOwn(elements,id),'Unknown DOM ID '+id);return elements[id]}};
 try{
  let js=match[1];
  js=js.replaceAll("'./b65-calculateur/atlas-depart-engine.mjs'","'"+pathToFileURL(resolve(base,'b65-calculateur/atlas-depart-engine.mjs')).href+"'");
  js=js.replaceAll("'./b65-calculateur/journey-controller.mjs'","'"+pathToFileURL(resolve(base,'b65-calculateur/journey-controller.mjs')).href+"'");
  await import('data:text/javascript;base64,'+Buffer.from(js,'utf8').toString('base64'));
  const val=id=>elements[id].textContent;
  assert.equal(val('departure'),'17:25');
  assert.match(val('basis'),/révisée/i);
  assert.equal(val('flight-number'),'AV 103');
  assert.equal(val('flight-origin'),'Non renseignée (fixture)');
  assert.equal(val('flight-destination'),'ORY');
  assert.match(val('flight-source'),/AeroDataBox MOCK/);
  assert.match(val('route-source'),/Geoapify MOCK/);
  assert.match(val('freshness'),/aucune actualisation fournisseur/);
  assert.equal(val('departure-utc'),'UTC : 2027-05-15T15:25:00.000Z');
  assert.match(val('date'),/Europe\/Paris/);
  assert.equal(elements['route-diagram'].hidden,false);
  elements.scenario.value='cancelled';elements.scenario.fire('change');
  assert.equal(val('departure'),'—');
  assert.equal(val('date'),'Conseil suspendu');
  assert.match(val('explanation'),/annulé/);
  elements.scenario.value='revised';elements.scenario.fire('change');
  assert.equal(val('departure'),'17:25');
  elements.origin.value='paris';elements.origin.fire('change');
  assert.equal(val('departure'),'17:50');
  elements.origin.value='unknown';elements.origin.fire('change');
  assert.equal(elements['route-diagram'].hidden,true);
  assert.equal(val('departure'),'—');
  assert.match(val('explanation'),/Adresse non choisie/);
  elements.origin.value='rozay';elements.origin.fire('change');
  assert.equal(val('departure'),'17:25');
  elements['route-mode'].value='offline';elements['route-mode'].fire('change');
  assert.equal(val('departure'),'—');
  assert.equal(val('departure-utc'),'UTC : —');
  assert.equal(elements['route-diagram'].hidden,true);
  assert.match(val('route-source'),/aucun appel externe/);
  elements['route-mode'].value='unavailable';elements['route-mode'].fire('change');
  assert.equal(val('departure'),'—');
  elements['route-mode'].value='available';elements['route-mode'].fire('change');
  assert.equal(val('departure'),'17:25');
  assert.equal(elements['route-diagram'].hidden,false);
  elements.traffic.value='25';elements.traffic.fire('change');
  assert.equal(val('departure'),'17:15');
  elements.scenario.value='stale';elements.scenario.fire('change');
  assert.equal(val('departure'),'—');
  assert.match(val('explanation'),/périmées/);
  elements.scenario.value='missing';elements.scenario.fire('change');
  assert.equal(val('departure'),'—');
  assert.match(val('explanation'),/Arrivée inconnue/);
  elements.scenario.value='actual';elements.scenario.fire('change');
  assert.equal(val('departure'),'17:05');
  assert.match(val('flight-status'),/Atterri.*simulation/);
  elements.exit.value='';elements.exit.fire('change');
  assert.equal(val('departure'),'—');
  assert.match(val('explanation'),/Paramètre manquant/);
 }finally{globalThis.document=previous}
});
