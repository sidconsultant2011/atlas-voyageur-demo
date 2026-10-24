# B6.5 — Rafraîchissement visuel local de l'expiration

Date : 24 octobre 2026. **QA B6.5 exclusivement — pas d'appels fournisseurs.**

## Changement
La page isolée `RECETTE-B65-HORLOGE-ACCELEREE.html` démarre un minuteur local qui avance l'horloge fictive d'une minute toutes les secondes réelles. Elle relit `simulation.state()` puis rafraîchit les champs du DOM. L'expiration est donc visible sans cliquer et sans lancer de requête AeroDataBox ou Geoapify.

Un bouton permet de mettre l'horloge en pause/reprise. Les actions +26 min, nouvelle observation fictive et réinitialisation restent disponibles. Tous les calculs s'appuient sur les modules B6.5 déjà présents.

La politique de 30 minutes reste une valeur **de test**. Le pilote local n'effectue ni polling réseau, ni géocodage, ni appel fournisseur, ni écriture persistante, ni abonnement. L'horloge accélérée est une fonction du laboratoire QA, **pas** un mécanisme à reprendre tel quel en production.

## Non-régression
`local-display-ticker.mjs` injecte setInterval et clearInterval, facilitant les tests.
`local-display-ticker.test.mjs` valide sans attendre : passage calcul disponible -> expiré -> restauré sur nouvelle observation ; démarrage idempotent et arrêt.
Le workflow existant exécute `node --test b65-calculateur/*.test.mjs` ; la réussite de cette modification CI doit encore être constatée.

## Limites
L'animation s'arrête si le navigateur suspend les minuteries d'un onglet inactif. À la reprise, le pilote ne compense pas le temps réel écoulé : c'est un **simulateur**, pas l'horloge de sécurité d'un service réel. La source de vérité reste le calculateur et son contrôle des timestamps. Si le simulateur est laissé actif longtemps, il avance sa propre horloge fictive.

## Gouvernance
B6.5 recette, B6.3 NO-GO ; aucun achat, aucune fusion sur main, site public inchangé. Aucun test iPhone requis.
