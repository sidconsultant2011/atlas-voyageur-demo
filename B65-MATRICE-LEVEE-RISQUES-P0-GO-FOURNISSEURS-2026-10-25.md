# ATLAS VOYAGEUR — B6.5 — MATRICE DE LEVÉE DES RISQUES P0
**Édition 25 octobre 2026 — V1.0 — DÉCISION GO FOURNISSEURS : NO-GO**

## 1. Objet et règle de décision
Référence source : `B65-RAPPORT-MAITRE-RECETTE-TECHNIQUE-2026-10-25.md`. La validation de 127 tests hors ligne (116 Node + 11 SQLite, exécution GitHub Actions n°41) **n'équivaut pas** à une homologation d'une façade HTTP ni à une autorisation de connexion réelle.

**Aucun GO fournisseur** tant qu'un seul des cinq critères P0 ci-dessous reste OPEN/BLOCKED. Le statut DONE exige cumulativement : correctif réalisé, tests automatiques PASS, preuve archivée et validation explicite de la gouvernance. Le GO doit être donné séparément et explicitement ; aucun succès CI ne le déclenche automatiquement.

## 2. Matrice opposable
| ID | Risque P0 / impact | Correctif attendu (sans réseau fournisseur) | Test de réception et résultat exigé | Preuve minimale / pièce de clôture | Responsable fonctionnel proposé* | Statut initial |
|---|---|---|---|---|---|---|
| P0-01 | Sessions HTTP, IDOR, CSRF, CORS et abus → exposition des parcours et du budget | Adapter le contrat en **façade HTTP locale non publique** avec authentification réelle testable, sessions éphémères, vérification d'appartenance à chaque opération, protection CSRF si cookie, CORS liste blanche, quotas session et globaux | Requêtes non authentifiées 401 ; accès inter-sessions 403/404 ; CSRF incorrect rejeté ; Origin interdit rejeté ; burst bloqué 429 ; entrées malformées 400 ; toutes voies échouent de manière fermée | Rapport d'exécution automatisée (cas positifs/négatifs), code de protection, configuration effective et revue de menace signée | Sécurité applicative + développeur façade | **OPEN** |
| P0-02 | Secrets / séparation environnements / fuite côté client → usage non autorisé et coût | Coffre de secrets serveur, droits minimaux, rotation/révocation, environnement QA isolé, CSP/log redaction ; pour cartes, clé publique restreinte ou proxy contrôlé | Analyse statique dépôt/build et traces : zéro secret ; clés QA impossibles sur origines non autorisées ; rotation simulée et accès refusé après révocation ; aucun paramètre client ne peut choisir une URL fournisseur | Rapport scan secrets + procédure de rotation testée + configuration masquée vérifiée + validation sécurité | DevSecOps + sécurité | **OPEN** |
| P0-03 | Quotas/tarification/retries/cache/concurrence multi-hôtes → dépassement financier | Matrice **tarifs/licences par endpoint** vérifiée au moment du GO ; registre d'unités persistantes partagé entre instances réelles ; réservation atomique avec plafond dur ; retries et circuit-breaker bornés ; cache avec TTL légaux ; arrêt des demandes en cas de budget insuffisant | Sous charge concurrente inter-processus **et inter-hôtes** : budget jamais dépassé, retries et crashs inclus ; simulations 429/5xx ; aucun appel supplémentaire après hard-stop ; déduplication facturation et cache ; rapprochement comptable | Table tarifaire horodatée et sourcée, journal de campagne charge, états du registre avant/après, captures alertes hard-stop, validation coût = 0 jusqu'au GO | Architecture backend + contrôle coût | **OPEN** |
| P0-04 | Données fournisseurs non qualifiées : identité du vol, horodatage, statut réel/estimé, cache périmé → conseil de départ trompeur | Contrats d'adaptateurs AeroDataBox V2/Geoapify figés, horodatage `observedAtUtc/retrievedAtUtc/expiresAtUtc` distinct, validation stricte schémas, sélection vol ambiguë, refus d'événement piste non confirmé ; catalogue de fixtures autorisées avec schéma et provenance | Fixtures adversariales : vols multiples, changement destination, fuseaux/DST, annulé/unknown, estimation sans réel, réponse plus ancienne, expiration sans réponse, géocodage ambigu, routage indisponible ; conseil suspendu dès qu'une donnée critique manque | Jeu de fixtures versionné, matrice champ→source, rapports de tests, décision de non-promotion des événements non prouvés, revue qualité datée | Responsable données vols + QA | **OPEN** |
| P0-05 | Panne entre réponse fournisseur et facturation : réservation orpheline, double débit ou remboursement indu | Journal d'opérations durable et idempotent `reserved/committed/reconciliation_required/released`, identifiants de requête, reprise contrôlée, absence de remboursement sur coût inconnu, procédure de rapprochement auprès de source officielle lorsque légalement disponible | Crash avant/après commit et à chaque transition ; redémarrage sur disque ; deux nœuds tentant la même clé ; état inconnu ne libère aucun crédit ; rapprochement manuel/simulé une fois, invariant comptable respecté | Logs anonymisés, état SQLite/registre, rapport de tests de crash, procédure de réconciliation et approbation comptable | Backend + contrôle coût | **OPEN** |

*Les rôles sont proposés, **aucune personne n'est nommément désignée** et aucune approbation n'est présumée.

## 3. Preuves existantes réutilisables — ne ferment pas les P0
- GitHub Actions **n°41** : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40135038922 — Node 116/116 ; SQLite 11/11 ; permet de justifier les contrôles métier simulés, pas l'HTTP réel.
- **n°42** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40135072884 — exécution du même pipeline, succès.
- `b65-calculateur/mock-server-facade.mjs` — sessions et limites fictives **in-process**, sans auth serveur ni CSRF effectif.
- `b65-calculateur/credit-ledger.mjs`, `transactional-credit-store.mjs` — budgets simulés mono-processus/multi-instance fictive.
- `b65-sqlite/sqlite_credit_ledger.py`, `test_sqlite_credit_ledger.py`, `test_sqlite_crash_qualification.py` — SQLite local sur disque, concurrence plusieurs processus, rollback/durabilité face à interruption de processus ; **pas de crash machine ou d'écriture multi-hôtes**.
- `b65-calculateur/aerodatabox-v2.mjs`, `aerodatabox-v2-controller.mjs`, `journey-controller.mjs` — règles de fraîcheur sur fixtures ; aucune garantie de disponibilité commerciale du fournisseur.

## 4. Registre de preuves de levée (à remplir lors des étapes futures)
| P0 | Commit correctif | Exécution CI / résultat | Rapport sécurité/qualité | Revue indépendante | Validation gouvernance | Décision |
|---|---|---|---|---|---|---|
| P0-01 | — | — | — | — | — | OPEN |
| P0-02 | — | — | — | — | — | OPEN |
| P0-03 | — | — | — | — | — | OPEN |
| P0-04 | — | — | — | — | — | OPEN |
| P0-05 | — | — | — | — | — | OPEN |

Tout statut de clôture doit renvoyer à un artefact accessible, versionné et daté. On ne remplace pas une preuve manquante par un succès de tests sur un autre domaine.

## 5. Contrôles transverses de GO, indépendants de P0
Avant tout GO réel, vérifier également licences et coûts réels, confidentialité/RGPD et durées de conservation, attribution cartographique, supervision des dépenses, sauvegardes, et les risques P1/P2 qui deviendraient bloquants selon l'architecture effectivement retenue.

**Décision du présent document : 5/5 P0 ouverts, donc NO-GO fournisseur.** Réexamen uniquement sur preuves et décision explicite. Aucun déploiement, achat, clé réelle, appel AeroDataBox/Geoapify, fusion `main` ou changement du site public autorisé.

**Gouvernance : B6.5 en recette — B6.3 NO-GO — aucun achat — aucune fusion sur `main` — `voyageur.atlascore.eu` inchangé — aucun test iPhone nécessaire.**

*ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.*
