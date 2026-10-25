# ATLAS VOYAGEUR — B6.5 — P0-01 — CHECKLIST DE DURCISSEMENT PRÉPRODUCTION
**Version 1.0 — 25/10/2026 — P0-01 OPEN / raccordement atlascore.eu NO-GO**

**Sources internes** : `B65-MATRICE-LEVEE-RISQUES-P0-GO-FOURNISSEURS-2026-10-25.md`, `b65-http/P001-FACADE-HTTP-LOCALE-RECETTE.md`, `b65-http/P001-ISOLATION-PARCOURS-IDOR-RECETTE.md`, `b65-http/P001-SESSIONS-PERSISTANTES-RECETTE.md`, `b65-http/P001-RATE-LIMIT-PERSISTANT-RECETTE.md`.

## 1. Règle d'usage
Chaque item requiert **correction + test PASS + preuve horodatée + revue indépendante**. « Testé en loopback » n'est pas « homologué pour Internet ». Le présent document **prépare** le durcissement ; il ne le déclare pas réalisé. Statuts autorisés : `OPEN`, `IN_PROGRESS`, `PASS_EVIDENCE`, `BLOCKED`. La clôture P0-01 nécessite approbation humaine explicite du pilotage.

## 2. Checklist de sécurité
| ID | Exigence/contrôle | État actuel constaté | Critère de sortie | Preuve requise | État |
|---|---|---|---|---|---|
| SEC-01 | Identité du demandeur et ouverture de session | Jetons aléatoires **QA sans comptes réels** | Auth réelle ou mécanisme d'identité approuvé ; refus des comptes non autorisés ; durée, rotation et invalidation définies | Schéma d'identité, test auth négatif, revue sécurité | OPEN |
| SEC-02 | Confidentialité HTTP | Loopback en HTTP ; cookie QA sans `Secure` | TLS valide, HSTS après qualification, cookie `Secure; HttpOnly; SameSite` adapté, aucune fuite via HTTP | Configuration TLS redigée, tests HTTPS/cookie et redirection | OPEN |
| SEC-03 | Autorisation objet / IDOR | Parcours fictifs liés à la session, tests croisés PASS | Tous endpoints et verbes soumis à politique propriétaire ; session expirée/révoquée impossible ; contrôle d'accès avec identité approuvée | Matrice route×action×rôle, tests IDOR croisés et revus | IN_PROGRESS |
| SEC-04 | CSRF et Origines | CSRF, CORS origine QA, validation `Origin` en boucle locale | Vérifier navigateur réel sur environnement isolé avec cookies ; origines par environnement ; aucun wildcard ; preflight et méthodes maîtrisés | Captures HTTP, tests CSRF cross-origin et prévol ; configuration | IN_PROGRESS |
| SEC-05 | Sessions persistantes | SQLite local, token/CSRF hachés, expiration/révocation testées | Stockage partagé selon topologie choisie, purge, limite absolue/inactivité, révocation immédiate sur toutes instances, rotation | Tests redémarrage, révocation simultanée, dossier rétention et purge | IN_PROGRESS |
| SEC-06 | Limites et anti-abus | 8/min/session, SQLite sur machine unique | Quota IP et identité, plafond global, contrôle création de sessions, coûts des requêtes en échec, stratégie multi-nœuds et `Retry-After` | Charge adversariale multi-sessions/instances ; preuve 429/hard stop | IN_PROGRESS |
| SEC-07 | Validation entrées/erreurs | Corps JSON borné et routes allowlist sur mock | Validation stricte chemin, IDs, méthode, JSON, longueur, média ; aucune stack trace ni secret | Fuzzing borné, tests 4xx, revue des réponses | IN_PROGRESS |
| SEC-08 | Journalisation et protection données | Logs serveur QA limités ; aucun registre d'audit qualifié | Journaux minimisés, pseudonymisés, suppression/retention, détection incidents, masquage de cookie/CSRF/adresse | Exemple de traces anonymisées, contrôle fuite et politique RGPD | OPEN |
| SEC-09 | Sécurité des secrets, dépendances, chaîne CI | Pas de clé fournisseur dans prototype ; revue P0-02 distincte | CI non exposée, secrets hors frontend, scans SAST/secret, dépendances et privilèges minimaux | Rapports scans, paramétrage d'environnement, revue P0-02 | OPEN |
| SEC-10 | Défense réseau, exploitation, restauration | Serveur strictement `127.0.0.1`; aucun déploiement | Environnement de préproduction privé et isolé, règles ingress/egress, monitoring, sauvegarde/restauration, kill switch | Architecture réseau validée et tests d'accès non autorisé | OPEN |
| SEC-11 | Gestion des incidents et décision | SQLite crédit réconciliation simulée ; pas de runbook exploitation complet | Procédure rollback/révocation d'urgence, alertes, responsabilités et traçabilité | Runbook testé, validation sécurité + pilotage | OPEN |

## 3. Ordre des portes
1. **Porte A (conception)** : architecture identités, réseau, TLS, sessions/stockage, quotas ; étude de menaces signée.
2. **Porte B (implémentation privée)** : contrôles ci-dessus sur une préproduction non exposée, mocks uniquement.
3. **Porte C (recette)** : plan `B65-P001-PLAN-TESTS-PREPRODUCTION-2026-10-25.md` entièrement PASS avec preuves et absence de faille critique/haute non traitée.
4. **Porte D (décision)** : P0-01 potentiellement clôturable après revue indépendante. **P0-02 à P0-05 et obligations légales restent bloquantes** pour tout GO fournisseur. Un GO de raccordement web réclame une décision distincte.

## 4. Traçabilité
Pièces existantes : GitHub Actions n°47 (isolation parcours) https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40170181025 ; n°52 (sessions persistantes) https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40171152709 ; n°55 (quota persistant) https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40171571510. Preuves limitées au périmètre de tests décrit.

**Aucun achat, aucun fournisseur réel, aucun déploiement, aucune fusion `main`, aucun changement `atlascore.eu` ou `voyageur.atlascore.eu`, aucun test iPhone demandé.**

*ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.*
