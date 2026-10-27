# 00 — SEC-01 R1-C01 — Réception indépendante ciblée AC-08

**Date :** 27 octobre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `de62d1ebd942ac83b5deb46cd38a524e95ba0e82`

## Références et vérification

- PV indépendant du chat 03 remis au 00 : `PV-03-SEC01-R1-C01-AC08-20261027`, verdict **RÉCEPTION FAVORABLE AVEC RÉSERVES**. Le PV existe dans la conversation ; son dépôt comme fichier autonome dans GitHub n'est pas attesté.
- Réception technique initiale 00 : `b65-http/DECISION-00-SEC01-R1-C01-AC08-RECEPTION-TECHNIQUE-20261027.md`.
- Rapport de réalisation 01 : `b65-http/SEC01-R1-C01-AC08-CORRECTIF-PREUVES-20261027.md`.
- Commit technique testé : `eb97c24eb969b2a28f4276b1c489d7eb46a6c6a4`.
- CI n°238 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587946581 ; contrôle direct GitHub par le 00 : `completed/success` avec `head_sha` correspondant exactement au commit technique.
- Journaux de la CI n°238 vérifiés lors de la réception technique : 116/116 tests JavaScript, 11/11 SQLite, 161/161 tests HTTP/identité/sécurité, dont huit tests AC-08 individuels réussis ; 288 **exécutions** au total, sans assimiler ce chiffre à 288 scénarios distincts.
- Échec historique CI n°236 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587789860 : recréation implicite de la base d'identités disparue après initialisation lors de `ATTACH`. Le même scénario passe en CI n°238 après contrôle d'existence préalable. L'échec n'est pas effacé.
- Aucun nouveau test ni changement GitHub par le chat 03. Tests locaux du dépôt complet au commit technique exact non exécutés selon le PV.

## Décision du 00

**GO — RÉCEPTION INDÉPENDANTE CIBLÉE DU CORRECTIF AC-08, AVEC RÉSERVES.**

Dans le périmètre **local, fictif, expérimental** reçu, les huit tests AC-08 attestent la préparation et vérification `journal_mode=DELETE` / `synchronous=FULL` des connexions gérées, le refus d'un mode WAL préexistant sans conversion automatique, la vérification de deux fichiers après `ATTACH` et avant `BEGIN IMMEDIATE`, le refus de bases manquantes sans recréation implicite, et la préservation des paramètres existants `busy_timeout` et `foreign_keys`.

**AC-08 peut être classé « réceptionné avec réserves dans le périmètre testé »**, mais **pas « garanti en toutes configurations »**. Cette décision ne clôture pas R1-C01 ni le risque parent P0-01.

### Réserves indépendantes conservées

1. `Path.resolve()` précédant `is_symlink()` ne démontre pas le rejet de tous les chemins d'entrée symboliques.
2. La vérification préalable `require_existing_disk()` ne supprime pas la fenêtre de remplacement concurrent de fichier avant `ATTACH` ; les contrôles post-attachement ne prouvent pas une protection exhaustive.
3. Les modifications de modes ou l'accès par des clients SQLite externes ne sont pas globalement qualifiés.
4. **AC-13** : aucune traduction HTTP uniforme, maîtrisée, des exceptions SQLite/COMMIT n'a été implémentée ; aucune réponse 503 spécifique n'est attestée.
5. `DELETE/FULL`, les chemins et `st_dev` ne démontrent ni durabilité physique après panne, ni récupération au cœur du COMMIT, ni atomicité inter-hôtes.
6. Les journaux de la CI réussie comportent des `ResourceWarning` sur des connexions de tests antérieurs : pas d'échec de CI, mais pas de prétention à une campagne sans avertissements.

## Frontière de décision

Le chantier technique AC-08 est **terminé et reçu uniquement dans les conditions testées**. **Pas de lot AC-08 supplémentaire automatiquement ouvert.** Les réserves ne deviennent pas des anomalies effectivement reproduites hors les cas établis.

- **R1-C01 : PARTIEL**, contrat de récupération après panne NON CONCLUANT.
- **R1-RD01, R1, P0-01 : OUVERTS**.
- AC-13 : écart documentaire antérieurement attesté, non corrigé et non autorisé dans cette décision.
- C03-R05 : ouvert et suspendu ; C03-R06 : ouvert, lots 1 et 2 reçus ; autres réserves C03/G03/VFS inchangées.
- B6.5 : EN RECETTE ; B6.3, G04 et production : NO-GO.

Aucun nouveau développement, test de panne, CI, extension C03, instrumentation VFS, correctif AC-13, déploiement, fournisseur réel, fusion main ou publication n'est autorisé par cette réception.

## Prochaine action unique

Soumettre au chat 02 — Sécurité P0 une **évaluation documentaire de proportionnalité** des réserves indépendantes AC-08 et d'AC-13 pour déterminer **une seule priorité éventuelle** avant nouveau GO technique, sans lancer de code ni de tests.
