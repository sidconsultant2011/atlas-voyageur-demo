# SEC-01 R1 — Complément de qualification du chat 01 — 25 octobre 2026

## Périmètre et gouvernance
Décision 00 : `b65-http/DECISION-00-SEC01-R1-CRITERES-20261025.md`.
PV indépendant source : `b65-http/PV-03-SEC01-R1-20261025.md`.
HEAD de départ contrôlé identique à `98d5593ff9080e898258b20a9c717c894d155f3c`.
Branche autorisée uniquement : `feature/b6-5-cartographie-interactive`.
Aucune modification des modules applicatifs au titre de ce complément : **nouveaux tests uniquement**.

## Versions
- `634c4135d0f45d7ea9c9af72fb6d387de8a15be0` : création des tests complémentaires.
- `1f77985303e6c955462b5f49ad505bd5c4a5d399` : horloge simulée identique dans le processus fils ; évite un faux positif par expiration.
- `6886eff86ea5479f68a88a2893bc4fdbaa2608f5` : preuve explicite du verrou SQLite `BEGIN IMMEDIATE` bloqué dans le processus fils.

Fichier de tests : `b65-http/test_sec01_r1_complements.py`.

## Exécutions attestées
GitHub Actions [n°83](https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40184360880) : `completed/success`, HEAD testé `6886eff86ea5479f68a88a2893bc4fdbaa2608f5`.
- JavaScript : 116/116 réussis.
- SQLite : 11/11 réussis.
- HTTP et identité : 94/94 exécutions réussies.
- Total : 221 exécutions, 0 échec ; le total ne signifie pas 221 scénarios distincts.
- Les 4 méthodes de test du complément apparaissent dans la découverte HTTP/identité.
Tests exécutés directement dans le conteneur de conversation : **aucun** ; preuves issues des journaux GitHub Actions.

## Couverture obtenue et portée exacte
- **R1-C01** : test des paramètres effectifs `PRAGMA journal_mode=DELETE` et `synchronous=FULL (2)` sur les deux bases de la fixture CI ; simulation de rollback d'une transaction sur deux bases avant COMMIT ; point d'effet opérationnel défini comme COMMIT. Cela ne simule pas un crash OS pendant le COMMIT et ne certifie pas la durabilité crash-safe.
- **R1-C02** : création, modification et suppression du pont forcées avec un `_authorize` bloqué **après acquisition de BEGIN IMMEDIATE**, puis révocation concurrente. Les mutations validées avant la révocation sont observées en SQL ; les requêtes suivantes sont refusées. L'observation `assertNotIn` de révocation avant déblocage est complémentaire, pas une preuve indépendante d'acquisition de verrou par le révocateur.
- **R1-C04** : relecture de `identity_journeys` pour les effets create/update/delete. Les contrôles de propriété et IDOR antérieurs demeurent couverts par les suites B6.5.
- **R1-C05** : révocation réelle via endpoint HTTP local (200), lecture SQL `sessions.revoked=1`, puis tests HTTP de GET, POST création, POST modification et DELETE refusés 401 ; relecture SQL de l'absence de modification métier.
- **R1-C06** : processus enfant créé en mode `spawn` ; le parent tient effectivement `BEGIN IMMEDIATE`, le fils teste un autre `BEGIN IMMEDIATE` avec timeout zéro et constate `database is locked` ; le parent valide ensuite `revoked=1` avant COMMIT ; l'opération métier du fils après déblocage est refusée et l'état SQL inchangé. Cette preuve concerne plusieurs processus partageant **un même fichier SQLite local**.

## Paramètres SQLite et limites de durabilité
Les fixtures exécutées sous GitHub Actions ont observé `journal_mode=DELETE` et `synchronous=FULL` dans les bases principale et attachée. La sérialisation est assurée par les verrous SQLite sur une même base de sessions partagée entre toutes les connexions du prototype.

Pour l'atomicité du COMMIT sur fichiers attachés, SQLite documente des restrictions : la base principale ne doit pas être en mémoire, `journal_mode` ne doit pas être WAL ; les bases doivent se trouver sur un stockage local cohérent. Le super-journal en mode rollback vise l'atomicité multi-bases selon ces conditions. Ce dossier **ne démontre pas** la résistance effective à une coupure de courant, crash noyau, défaillance matérielle ou stockage réseau, ni le maintien de `FULL/DELETE` sur toute plateforme future. Aucun protocole d'injection de panne au milieu du COMMIT n'a été exécuté. Les résultats sont ceux de l'environnement Linux GitHub Actions, non une garantie production.

Les limites distinctes du `LocalState` en mémoire, des bases SQLite indépendantes hébergées sur plusieurs machines et des fournisseurs d'identité réels ne sont pas levées.

## Demande au chat 03
Effectuer une réception indépendante de R1-C01, C02, C04, C05 et C06 au regard des preuves ci-dessus ; distinguer qualification expérimentale locale et garanties de durabilité en cas de panne. Ne lever aucune réserve automatiquement.

**Statut non modifié : R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; production NO-GO.**
