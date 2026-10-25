# ATLAS VOYAGEUR — B6.5 — P0-01 — PLAN DE TESTS DE PRÉPRODUCTION
**Version 1.0 — 25/10/2026 — PLAN PROPOSÉ, NON EXÉCUTÉ — P0-01 OPEN**

## 1. Préconditions
Environnement de préproduction **privé**, jamais sur `main` ni sur le domaine public, fournisseurs AeroDataBox et Geoapify remplacés par des mocks, identités de test seulement, horloge contrôlable, bases temporaires et suppression à la fin. Aucune clé fournisseur réelle. Ces essais ne requièrent ni iPhone ni dépense.

La préproduction doit être techniquement isolée et soumise à une approbation dédiée avant toute mise en service ; le présent plan n'autorise ni déploiement ni ouverture réseau.

## 2. Jeu de scénarios et critères
| Test | Préparation / attaque fictive | Attendu obligatoire | Preuve attendue | Décision |
|---|---|---|---|---|
| PRE-01 | Accès sans authentification aux routes d'un parcours | 401 ou 404 sans données | Requête/réponse expurgées, test CI | NON EXÉCUTÉ |
| PRE-02 | Identité A accède au parcours B en GET/POST/PUT/DELETE, avec jeton A | 403/404, aucune mutation ni révélation d'existence | Tests d'IDOR, états avant/après | NON EXÉCUTÉ |
| PRE-03 | Token et session expirés/révoqués, y compris deux instances et redémarrage | 401, aucun accès conservé, suppression/rotation conformes | Journal tests multi-instances et extrait base pseudonymisé | NON EXÉCUTÉ |
| PRE-04 | POST sans CSRF, CSRF faux, CSRF d'une autre session, attaque cross-origin | 403, aucune modification | Tests de navigateur/HTTP isolé | NON EXÉCUTÉ |
| PRE-05 | Origines interdites, preflight sauvage, méthodes non prévues | CORS fermé, 403/405, aucun effet | Matrice méthodes/origines et traces | NON EXÉCUTÉ |
| PRE-06 | Connexion HTTP simple, TLS invalide, inspection cookies | HTTPS requis sur futur environnement privé, cookies Secure/HttpOnly/SameSite, HSTS selon politique | Configuration TLS et tests automatisés | NON EXÉCUTÉ |
| PRE-07 | 30 requêtes concurrentes + multiples sessions et IP simulées | 429 au-delà du plafond, quota conservé après redémarrage, pas de réinitialisation malveillante | Métriques avant/après, trace 429 et invariants | NON EXÉCUTÉ |
| PRE-08 | Corps trop volumineux, JSON malformé, content-type erroné, ID inattendu, injection | 400/413/415 selon cas, pas de crash ni réponse contenant secret | Fuzzing ciblé et tableau 4xx | NON EXÉCUTÉ |
| PRE-09 | Redémarrage brutal pendant mutation/revocation de session | Opération atomique ou rollback, jamais session à moitié révoquée | Tests de reprise, integrity_check, état sessions | NON EXÉCUTÉ |
| PRE-10 | Inspection build/logs, cookies, traces, erreurs | Aucun cookie/CSRF/secret/adresse complète journalisé, politique de rétention vérifiée | Scan secrets et logs anonymisés | NON EXÉCUTÉ |
| PRE-11 | Tentative de sortie vers fournisseur ou hôte arbitraire depuis le mock | Aucune requête sortante, egress interdit | Capture réseau de labo et règles egress | NON EXÉCUTÉ |
| PRE-12 | Coupure simulée, supervision indisponible, restauration sauvegarde de préproduction | Fonctionnement en refus sécurisé, rollback documenté | Rapport exercice, validation opérateur | NON EXÉCUTÉ |

## 3. Protocole d'exécution
1. Figer commit, environnement, scénarios, jeux de données fictifs, références de configuration (sans secrets).
2. Lancer suites unitaires préexistantes, puis tests d'intégration HTTP et tests de concurrence/attaques listés.
3. Enregistrer pour chaque cas : identifiant test, commit Git, date UTC, environnement, commandes, résultat exact, état avant/après, lien Actions ou artefact, éventuelle anomalie.
4. Interdire clôture si anomalie critique/haute ouverte, preuve manquante, fuite de données ou échec d'une exigence P0-01.
5. Revue indépendante sécurité, puis décision écrite du responsable de pilotage : `P0-01 PASS_EVIDENCE` ou `NO-GO`. **Ne pas extrapoler à P0-02–05.**

## 4. Séparation des preuves
Les réussites existantes — https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40170181025 (IDOR QA), https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40171152709 (sessions QA), https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40171571510 (rate limit QA) — sont de **l'antériorité technique**, pas des PASS sur ce nouveau plan de préproduction.

## 5. Raccordement futur atlascore.eu
Le raccordement `atlascore.eu` / `voyageur.atlascore.eu` n'est **ni réalisé ni autorisé**. Au moment approprié : planifier revue DNS/TLS et sécurité de domaine, architecture de routage/rollback, tests de non-régression et décision explicite avant tout changement. Ne pas confondre connexion au domaine et accès fournisseur : deux portes GO distinctes.

**Gouvernance : B6.5 recette, B6.3 NO-GO, aucun achat, aucune fusion `main`, site public inchangé, aucun nouveau test iPhone.**

*ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.*
