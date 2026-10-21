/* ATLAS VOYAGEUR B6.3 — FR / EN / RU. Branche de développement. */
(() => {
'use strict';
const messages = {
"J'accueille un voyageur.":["I'm welcoming a traveler.","Я встречаю путешественника."],
"Le bon vol. Le bon trajet. Le bon moment.":["The right flight. The right route. The right time.","Нужный рейс. Правильный маршрут. Точное время."],
"Découvrir ATLAS VOYAGEUR":["Discover ATLAS VOYAGEUR","Об ATLAS VOYAGEUR"],
"1. Trouver":["1. Find","1. Найти"],
"2. Choisir":["2. Choose","2. Выбрать"],
"3. Accueillir":["3. Meet","3. Встретить"],
"Retrouver son vol":["Find the flight","Найти рейс"],
"Sans numéro":["Without flight number","Без номера рейса"],
"Avec numéro":["With flight number","По номеру рейса"],
"Aéroport d'arrivée":["Arrival airport","Аэропорт прибытия"],
"Date d'arrivée":["Arrival date","Дата прибытия"],
"Heure approximative":["Approximate time","Примерное время"],
"Plage de recherche":["Search window","Интервал поиска"],
"Numéro du vol":["Flight number","Номер рейса"],
"Trouver le vol":["Find flight","Найти рейс"],
"Choisir son vol":["Choose the flight","Выбрать рейс"],
"Sélectionner ce vol →":["Select this flight →","Выбрать этот рейс →"],
"Préparer mon accueil":["Plan the pickup","Спланировать встречу"],
"Compagnie fictive ATLAS":["Fictional ATLAS airline","Вымышленная авиакомпания ATLAS"],
"Fictif":["Fictional","Вымышленный"],
"Simulation":["Simulation","Симуляция"],
"Terminal":["Terminal","Терминал"],
"Porte":["Gate","Выход"],
"Bagages":["Baggage","Багаж"],
"Non communiquée":["Not provided","Не указан"],
"Non communiqués":["Not provided","Не указана информация"],
"Mon trajet vers Orly":["My route to Orly","Мой маршрут в Орли"],
"Distance":["Distance","Расстояние"],
"Trajet retenu pour le calcul":["Travel time used","Время в пути для расчёта"],
"Référence cartographique : 20 min":["Map reference: 20 min","По карте: 20 мин"],
"Durée de référence cartographique":["Map reference time","Время по карте"],
"Modifier mes hypothèses":["Adjust my estimates","Изменить параметры"],
"Route (min)":["Travel time (min)","Время в пути (мин)"],
"Sortie du voyageur (min)":["Time to exit airport (min)","Время выхода пассажира (мин)"],
"Marge circulation (min)":["Traffic buffer (min)","Запас на пробки (мин)"],
"Avance au rendez-vous (min)":["Arrival buffer (min)","Запас до встречи (мин)"],
"Enregistrer ce scénario sur mon appareil":["Save this scenario on my device","Сохранить сценарий на устройстве"],
"Restaurer le scénario enregistré":["Restore saved scenario","Восстановить сценарий"],
"Rencontre estimée :":["Estimated meeting:","Ожидаемая встреча:"],
"Calcul suspendu":["Calculation paused","Расчёт приостановлен"],
"Durée de trajet à vérifier":["Check travel time","Проверьте время в пути"],
"Hors API":["No API","Без API"],
"DEMONSTRATION PROFESSIONNELLE · B6.2-PUBLIC":["PROFESSIONAL DEMO · B6.3-DEV","ПРОФЕССИОНАЛЬНАЯ ДЕМО · B6.3-DEV"],
"DÉMONSTRATION PROFESSIONNELLE · B6.2-PUBLIC":["PROFESSIONAL DEMO · B6.3-DEV","ПРОФЕССИОНАЛЬНАЯ ДЕМО · B6.3-DEV"],
"Paris-Orly (ORY)":["Paris-Orly (ORY)","Париж-Орли (ORY)"],
"Porto":["Porto","Порту"],
"Paris-Orly":["Paris-Orly","Париж-Орли"],
"Paris centre → Paris-Orly":["Central Paris → Paris-Orly","Центр Парижа → Париж-Орли"],
"Conception et développement — Joseph Vincent":["Design and development — Joseph Vincent","Концепция и разработка — Joseph Vincent"],
"Un projet ATLAS CORE":["An ATLAS CORE project","Проект ATLAS CORE"],
"© 2026 Joseph Vincent — Tous droits réservés.":["© 2026 Joseph Vincent — All rights reserved.","© 2026 Joseph Vincent — Все права защищены."],
"Scénario fictif disponible : Porto → Orly.":["Fictional scenario available: Porto → Orly.","Доступен вымышленный сценарий: Порту → Орли."],
"1 vol fictif disponible · aucune requête réseau":["1 fictional flight available · no network request","1 вымышленный рейс · без сетевых запросов"],
"*Scénario inventé uniquement pour démonstration.":["*This scenario is fictional and intended only for demonstration.","*Этот сценарий вымышлен и предназначен только для демонстрации."],
"DÉMONSTRATION PUBLIQUE — VOL FICTIF.":["PUBLIC DEMO — FICTIONAL FLIGHT.","ПУБЛИЧНАЯ ДЕМО — ВЫМЫШЛЕННЫЙ РЕЙС."],
"Toutes les informations aériennes sont inventées, sans valeur opérationnelle.":["All flight details are fictional and must not be used for travel.","Все данные о рейсе вымышлены и не предназначены для поездок."],
"VOL ENTIÈREMENT FICTIF — aucune information de vol réelle. Ne pas utiliser pour un déplacement.":["ENTIRELY FICTIONAL FLIGHT — no real flight information. Do not use for actual travel.","ПОЛНОСТЬЮ ВЫМЫШЛЕННЫЙ РЕЙС — нет реальных данных. Не используйте для поездок."],
"Compagnie fictive ATLAS · appareil fictif":["Fictional ATLAS airline · fictional aircraft","Вымышленная авиакомпания ATLAS · вымышленный самолёт"],
"Paris centre → Paris-Orly · itinéraire calcul Geoapify enregistré. Pas de trafic en direct.":["Central Paris → Paris-Orly · saved Geoapify route. No live traffic.","Центр Парижа → Париж-Орли · сохранённый маршрут Geoapify. Нет данных о пробках."],
"Estimation hors trafic réel.":["Estimate without live traffic.","Оценка без учёта пробок в реальном времени."],
"contributeurs OpenStreetMap":["OpenStreetMap contributors","участники OpenStreetMap"],
"Tracé de référence : calcul":["Reference route: calculated by","Исходный маршрут: расчёт"],
"· données géographiques ©":["· geographic data ©","· геоданные ©"],
"DÉPART INDICATIF · EUROPE/PARIS":["ESTIMATED DEPARTURE · EUROPE/PARIS","ПРИМЕРНОЕ ВРЕМЯ ВЫЕЗДА · EUROPE/PARIS"],
"15 mai 2027 · données fictives":["15 May 2027 · fictional data","15 мая 2027 г. · вымышленные данные"],
"Référence : 20 min (itinéraire Geoapify enregistré). Valeur modifiable.":["Reference: 20 min (saved Geoapify route). Editable.","По карте: 20 мин (маршрут Geoapify). Можно изменить."],
"Reprendre la durée de référence — 20 min":["Reset to reference time — 20 min","Вернуть время по карте — 20 мин"],
"Les horaires de rencontre et de départ sont des calculs indicatifs, pas des observations.":["Meeting and departure times are estimates, not live observations.","Время встречи и выезда рассчитано приблизительно, а не получено в реальном времени."],
"Vous accueillez quelqu'un à l'aéroport ? Avec":["Meeting someone at the airport? With","Встречаете кого-то в аэропорту? С"],
"ou sans numéro de vol":["or without a flight number","номером рейса или без него"],
"depuis votre propre adresse de départ":["from your own starting address","от вашего адреса отправления"],
"jusqu'à l'aéroport.":["to the airport.","до аэропорта."],
"Il vise à estimer quand partir, avec des marges pour la circulation et la sortie du voyageur. Le projet est pensé pour une utilisation internationale.":["It aims to estimate when to leave, factoring in traffic buffers and time for the traveler to exit the airport. Designed for international use.","Приложение помогает определить время выезда с запасом на пробки и выход пассажира из аэропорта. Проект рассчитан на международное использование."],
"Cette version publique est une":["This public version is a","Эта публичная версия —"],
"démonstration fictive":["fictional demonstration","демонстрация с вымышленными данными"],
": un vol simulé, un trajet Paris → Orly préenregistré et un calculateur local. Pas de vols réels, pas de recherche libre d'adresse, aucun appel API et aucune information en direct.":[": one simulated flight, a saved Paris → Orly route and a local calculator. No real flights, free-form address search, API calls or live updates.",": один смоделированный рейс, сохранённый маршрут Париж → Орли и локальный калькулятор. Нет реальных рейсов, свободного поиска адреса, API и данных в реальном времени."],
"ATLAS VOYAGEUR · Démonstration publique fictive · Aucun suivi de vol réel · Aucun appel API. Le tracé routier de référence est préenregistré.":["ATLAS VOYAGEUR · Fictional public demo · No real flight tracking · No API calls. The reference route is saved.","ATLAS VOYAGEUR · Публичная демонстрация с вымышленными данными · Без отслеживания реальных рейсов и API. Маршрут сохранён."],
"Tracé historique Paris centre vers Paris-Orly":["Historical route, central Paris to Paris-Orly","Исторический маршрут: центр Парижа — Париж-Орли"],
"± 30 min":["± 30 min","± 30 мин"],
"± 1 heure":["± 1 hour","± 1 час"],
"± 2 heures":["± 2 hours","± 2 часа"]
};
const patterns=[
[/^(\d+) min$/,(m,n,l)=>l==='en'?n+' min':n+' мин'],
[/^Rencontre estimée : (.+)$/,(m,time,l)=>l==='en'?'Estimated meeting: '+time:'Ожидаемая встреча: '+time],
[/^Personnalisé · référence cartographique : 20 min$/,(m,l)=>l==='en'?'Custom · map reference: 20 min':'Изменено · по карте: 20 мин'],
[/^Durée personnalisée : (\d+) min · référence cartographique : 20 min\.$/,(m,n,l)=>l==='en'? 'Custom duration: '+n+' min · map reference: 20 min.':'Выбрано: '+n+' мин · по карте: 20 мин.'],
[/^Scénario restauré : trajet (\d+) min · départ (.+)\.$/,(m,n,time,l)=>l==='en'?'Scenario restored: '+n+' min drive · departure '+time+'.':'Сценарий восстановлен: дорога '+n+' мин · выезд '+time+'.'],
[/^Enregistré et vérifié : (\d+) min · départ (.+)\.$/,(m,n,time,l)=>l==='en'?'Saved and verified: '+n+' min · departure '+time+'.':'Сохранено и проверено: '+n+' мин · выезд '+time+'.']
];
const originalNodes=new WeakMap();
const originAttrs=new WeakMap();
const idx={en:0,ru:1};
let language='fr', running=false;
function translate(value,lang){
 if(lang==='fr')return value;
 const clean=value.trim();
 const direct=messages[clean];
 if(direct)return value.replace(clean,direct[idx[lang]]);
 for(const [re,fn] of patterns){const match=clean.match(re);if(match){const r=fn(...match,lang);return value.replace(clean,r);}}
 return value;
}
function syncText(node){
 const live=node.nodeValue||'';
 const saved=originalNodes.get(node);
 if(saved===undefined || live!==saved.rendered){ originalNodes.set(node,{source:live,rendered:live});}
 const item=originalNodes.get(node);
 const converted=translate(item.source,language);
 if(node.nodeValue!==converted){item.rendered=converted;node.nodeValue=converted;}
 else item.rendered=converted;
}
function sync(){
 if(running)return;
 running=true;
 try{
 document.documentElement.lang=language;
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 let node;
 while((node=walker.nextNode())){if(node.parentElement && !['SCRIPT','STYLE'].includes(node.parentElement.tagName))syncText(node);}
 document.querySelectorAll('[aria-label]').forEach(el=>{
   let prev=originAttrs.get(el),live=el.getAttribute('aria-label');
   if(!prev||live!==prev.rendered){prev={source:live,rendered:live};originAttrs.set(el,prev)}
   const next=translate(prev.source,language);if(next!==live)el.setAttribute('aria-label',next);prev.rendered=next;
 });
 document.querySelectorAll('[data-lang]').forEach(button=>{
   const on=button.dataset.lang===language;
   button.setAttribute('aria-pressed',String(on));
   button.style.borderColor=on?'var(--gold)':'var(--line)';
   button.style.background=on?'#35495a':'var(--card)';
 });
 }finally{running=false}
}
function select(lang){
 if(!Object.hasOwn(idx,lang)&&lang!=='fr')return;
 language=lang;
 try{localStorage.setItem('atlas-voyageur-language',lang)}catch(_){}
 sync();
}
const header=document.querySelector('.app > header');
if(header){
 const chooser=document.createElement('div');
 chooser.className='lang-switch';
 chooser.setAttribute('role','group');
 chooser.setAttribute('aria-label','Language / Langue / Язык');
 chooser.style.cssText='display:flex;gap:4px;justify-content:flex-end;flex-wrap:wrap;';
 for(const lang of ['fr','en','ru']){
   const b=document.createElement('button');
   b.type='button';b.dataset.lang=lang;b.textContent=lang.toUpperCase();
   b.setAttribute('aria-label',{fr:'Français',en:'English',ru:'Русский'}[lang]);
   b.style.cssText='font-size:12px;min-height:38px;min-width:39px;padding:5px;border-radius:8px;color:var(--text);border:1px solid var(--line);background:var(--card)';
   b.addEventListener('click',()=>select(lang));chooser.appendChild(b);
 }
 header.appendChild(chooser);
}
let stored='fr';
try{stored=localStorage.getItem('atlas-voyageur-language')||'fr'}catch(_){}
select(['fr','en','ru'].includes(stored)?stored:'fr');
new MutationObserver(()=>{if(!running)sync()}).observe(document.body,{subtree:true,childList:true,characterData:true});
window.ATLAS_I18N={getLanguage:()=>language,setLanguage:select};
})();