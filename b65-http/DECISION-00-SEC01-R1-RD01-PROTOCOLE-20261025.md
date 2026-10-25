# Décision 00 — SEC-01 R1-RD01 — Protocole expérimental de durabilité

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Chantier unique :** SEC-01 R1-RD01 — durabilité atomique SQLite multi-fichiers  
**Source de proposition :** chat 02 — Sécurité P0, « R1-RD01-PROTOCOLE-01 » transmis au 00.  
**HEAD vérifié avant décision :** `6d6582bcc620f225e0a51b64bd711dc0e74da77f`.  
**Référence :** `b65-http/PV-03-SEC01-R1-COMPLEMENT-20261025.md`.

## Décision et autorisation

Le 00 **approuve les quatre phases, les huit critères d'acceptation RD01-C01 à RD01-C08 et la matrice de six fenêtres d'injection proposées par le chat 02**, comme plan de qualification, **sans préjuger leur faisabilité ni leur réussite**.

**GO expérimental strictement limité :** autoriser au chat 01 un banc de test isolé, des fixtures entièrement fictives et une instrumentation de qualification ciblée pour l'**arrêt brutal d'un processus enfant**, sur deux fichiers SQLite locaux liés par une transaction `ATTACH DATABASE` et `BEGIN IMMEDIATE`.

- La mise au point des scripts de test et de l'instrumentation doit rester distincte du code métier préexistant. Ne pas modifier les modules applicatifs sans découverte d'une anomalie concrète et nouvel arbitrage.
- Ne jamais viser des bases utilisateurs, un service réel, le système d'exploitation hôte ou une infrastructure publique. Les essais de type coupure électrique, crash noyau, stockage réseau ou multi-hôtes ne sont **pas autorisés**.
- Ne pas appeler « interruption pendant COMMIT » un simple `kill` après temporisation ; conserver une preuve instrumentée de l'étape atteinte. Si cette preuve manque, déclarer le cas **non démontré**.
- La journalisation et l'instrumentation ne doivent pas modifier silencieusement le mécanisme de persistance étudié. Consigner tout impact du banc sur le comportement testé.
- Les validations ne porteront que sur le moteur, la plateforme, le stockage et le type de panne réellement examinés.

## Phases du protocole approuvées

**A — Préqualification :** relever OS, version et compilation SQLite, type de fichiers physiques principal et attaché, `PRAGMA journal_mode` (rollback, hors WAL), `PRAGMA synchronous` (objectif FULL sur les deux bases), localisation des fichiers et journaux, même système de fichiers local, hypothèses de cache et de synchronisation. **Arrêt de qualification** si précondition nécessaire absente.

**B — Témoins :** deux bases uniquement fictives, identifiant de transaction partagé, état initial documenté ; mutation jointe dans une transaction multi-fichiers. Exemple de fixture (ne présume pas du métier réel) : session A `revoked=0 → 1`, parcours B absent → présent.

**C — Interruption et récupération :** processus enfant isolé ; transaction et point d'injection contrôlés ; arrêt brutal **sans rollback applicatif** ; préservation des deux bases et des journaux ; réouverture depuis un autre processus ; intégrité et invariants vérifiés.

**D — Matrice d'injection :** avant COMMIT, début COMMIT, journalisation, synchronisation, finalisation COMMIT, après COMMIT confirmé. Ne déclarer « testé » que ce qui est effectivement atteint et prouvé ; toute fenêtre non accessible demeure non qualifiée. Définir avant l'exécution la répétition de chaque cas réalisable.

## Invariant d'état

| État récupéré | Session A | Parcours B | Verdict |
|---|---|---|---|
| AVANT | `revoked=0` | absent | conforme |
| APRÈS | `revoked=1` | présent | conforme |
| PARTIEL A | `revoked=1` | absent | non conforme |
| PARTIEL B | `revoked=0` | présent | non conforme |

Toute autre altération ou corruption doit être consignée séparément, puis analysée sans attribution automatique à SQLite.

## Critères d'acceptation approuvés

| ID | Critère | Preuve |
|---|---|---|
| RD01-C01 | Environnement connu | Versions, stockage, journaux, paramètres |
| RD01-C02 | Transaction effectivement multi-fichiers | Mutation liée dans un COMMIT |
| RD01-C03 | Interruption reproductible | Type de panne et point atteint attestés |
| RD01-C04 | Récupération cohérente | État complet AVANT ou APRÈS, jamais partiel |
| RD01-C05 | Intégrité SQLite | `PRAGMA integrity_check` par base et invariants métier |
| RD01-C06 | Reproductibilité | Résultats cohérents sur la campagne définie, aucune anomalie inexpliquée |
| RD01-C07 | Traçabilité | Commit, scripts, configurations, journaux et états SQL |
| RD01-C08 | Limites explicites | Conclusion circonscrite aux pannes et environnements réellement testés |

**Réception exigée :** contrôle indépendant du chat 03 après dépôt des preuves. Tout critère applicable non prouvé bloque le verdict « pleinement reçu » pour le périmètre défini. La réussite d'arrêts de processus ne qualifie ni coupure électrique, ni crash OS, ni panne de matériel.

## Statuts et restrictions

**R1-RD01 NON LEVÉE — R1-C01 PARTIEL — R1 OUVERTE — P0-01 OUVERT — B6.5 EN RECETTE — B6.3 NO-GO — production NO-GO.** Les réserves R2 à R4 restent inchangées.

Aucun achat, aucune fusion vers `main`, aucun fournisseur réel, aucune modification ou publication du site public, aucun test de production ou d'iPhone revendiqué.

## Prochaine action unique

Chat 01 — réaliser le banc de qualification limité à l'arrêt brutal de processus selon ce protocole ; produire un dossier versionné contenant environnement, scripts, preuves des phases atteintes, états SQL et limites pour réception indépendante par le chat 03, sans étendre le périmètre.
