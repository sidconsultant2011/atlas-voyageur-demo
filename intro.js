/* B6.3 — Écran signature et préférence utilisateur (uniquement branche de développement). */
(()=>{'use strict';
const pref='atlas-voyageur-show-intro';
const strings={
 fr:{open:"Le bon vol. Le bon trajet. Le bon moment.",continue:"Accéder à l'application",toggle:"Afficher la signature à l'ouverture",hint:"Vous pourrez modifier ce choix à tout moment."},
 en:{open:"The right flight. The right route. The right time.",continue:"Enter the app",toggle:"Show opening message",hint:"You can change this setting at any time."},
 ru:{open:"Нужный рейс. Правильный маршрут. Точное время.",continue:"Перейти в приложение",toggle:"Показывать приветствие при запуске",hint:"Этот выбор можно изменить в любое время."}
};
let showIntro=true;try{showIntro=localStorage.getItem(pref)!=='false'}catch(_){}
const style=document.createElement('style');style.textContent=`
#atlas-opening{position:fixed;inset:0;z-index:1000;background:#09131f;color:#f5f3ef;display:flex;align-items:center;justify-content:center;padding:calc(24px + env(safe-area-inset-top,0px)) 20px calc(24px + env(safe-area-inset-bottom,0px));text-align:center}
#atlas-opening[hidden]{display:none!important}
#atlas-opening .intro-inner{max-width:520px;width:100%}
#atlas-opening h2{font-size:clamp(26px,6vw,40px);line-height:1.2;color:#bccad5;margin:20px 0 30px}
#atlas-opening button{background:#bccad5;color:#09131f;border:0;border-radius:10px;padding:14px 20px;min-height:48px;font-weight:800;width:100%;max-width:380px}
#atlas-opening p{color:#b3c1d1;font-size:13px}
#atlas-opening .intro-brand{letter-spacing:2px;font-size:17px;font-weight:850}
#atlas-intro-setting{font-size:12px;border:1px solid #34475d;border-radius:9px;background:#1c2d42;color:#f5f3ef;padding:8px 10px;cursor:pointer}
`;document.head.appendChild(style);
const overlay=document.createElement('section');overlay.id='atlas-opening';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-labelledby','atlas-intro-message');overlay.innerHTML='<div class="intro-inner"><div class="intro-brand">ATLAS VOYAGEUR</div><h2 id="atlas-intro-message"></h2><button id="atlas-intro-go" type="button"></button><p id="atlas-intro-hint"></p></div>';
document.body.appendChild(overlay);
const toggle=document.createElement('button');toggle.id='atlas-intro-setting';toggle.type='button';document.querySelector('.app > header')?.append(toggle);
const currentLang=()=>window.ATLAS_I18N?.getLanguage?.()||'fr';
function paint(){const v=strings[currentLang()]||strings.fr;document.getElementById('atlas-intro-message').textContent=v.open;document.getElementById('atlas-intro-go').textContent=v.continue;document.getElementById('atlas-intro-hint').textContent=v.hint;toggle.textContent=(showIntro?'☑ ':'☐ ')+v.toggle;toggle.setAttribute('aria-pressed',String(showIntro));}
function close(){overlay.hidden=true;document.body.style.overflow='';toggle.focus();}
function open(){paint();overlay.hidden=false;document.body.style.overflow='hidden';document.getElementById('atlas-intro-go').focus();}
document.getElementById('atlas-intro-go').addEventListener('click',close);
toggle.addEventListener('click',()=>{showIntro=!showIntro;try{localStorage.setItem(pref,String(showIntro))}catch(_){}paint();if(showIntro)open()});
window.addEventListener('atlas-language-change',paint);
paint();if(showIntro)open();else overlay.hidden=true;
})();
