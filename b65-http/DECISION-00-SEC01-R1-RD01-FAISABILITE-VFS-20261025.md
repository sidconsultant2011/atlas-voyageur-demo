# Décision 00 — SEC-01 R1-RD01 — Étude de faisabilité VFS SQLite

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Chantier prioritaire unique :** étude de faisabilité de l'instrumentation interne du COMMIT multi-fichiers SQLite.  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `d3b8411e22b4905ac00413899e2b559ef395d356`.

## Sources et acquis

- Rapport du chat 02 — « Analyse de faisabilité R1-RD01 » reçu au 00 le 25 octobre 2026.
- PV : `b65-http/PV-03-SEC01-R1-RD01-20261025.md`.
- Banc existant : `b65-http/rd01_crash_bench.py`.
- CI n°90 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40185721195.
- Les **15 essais SIGKILL conformes aux cinq points externes** sont acquis, sans preuve d'interruption interne du COMMIT. Aucun test nouveau exécuté par le 02 lors de son analyse.

## Décision de pilotage

**GO limité à l'étude de faisabilité technique**, confiée au chat 01. **Aucun GO d'implémentation ou de nouvelle expérimentation.**

L'étude doit :
1. Comparer les pistes de traçage système, VFS instrumentée SQLite et moteur d'essai instrumenté ; exclure le SIGKILL chronométré comme preuve suffisante à lui seul.
2. Identifier les événements internes `xWrite`, `xSync`, `xDelete` ou autres effectivement pertinents au COMMIT multi-fichiers et vérifier leur accessibilité pratique dans l'environnement du dépôt ; ne pas supposer la présence du super-journal.
3. Décrire la méthode de preuve d'atteinte du point interne, ses risques de perturbation de la journalisation et la différence avec le moteur SQLite non instrumenté.
4. Examiner la possibilité de sauvegarder **avant toute récupération** les deux bases, journaux et éventuel super-journal ; proposer un manifeste, SHA-256, conservation et diffusion sans données réelles ni secrets.
5. Identifier les données d'environnement réellement accessibles (versions, options SQLite, montage, type de système de fichiers, modes journaux, `synchronous`) et les limites de `fsync` / stockage physique.
6. Établir la faisabilité d'un scénario relié au chemin applicatif `local_identity_bridge.py::_persistent_journey()`, distinct de la seule transaction témoin.
7. Présenter les prérequis, dépendances, modifications envisagées **sans les réaliser**, risques, critères de décision et alternative « non démontrable avec le banc retenu ».

Le livrable attendu est **un rapport de faisabilité versionné dans GitHub**, avec sources, périmètre et recommandation au 00. Aucun succès expérimental n'est présumé.

## Restrictions

Pas de développement ou installation de VFS, aucune instrumentation nouvelle, aucun crash expérimental, aucun changement du code applicatif, aucun lancement de campagne identique, aucune interruption de l'OS ou du matériel. Aucun achat, activation d'un fournisseur réel, fusion sur `main`, publication ou modification du site public. Les tests sur bases réelles sont exclus.

## Statuts inchangés

**RD01-R01 à RD01-R04 OUVERTES — RD01-C01/C03/C07 PARTIELS — R1-RD01 OUVERTE — R1-C01 PARTIEL — R1 OUVERTE — P0-01 OUVERT — B6.5 EN RECETTE — B6.3 NO-GO — PRODUCTION NO-GO.**

Les 15 essais et la CI n°90 conservent leur portée limitée au SIGKILL d'un processus enfant aux marques externes instrumentées.

## Prochaine action unique

Transmettre au chat 01 cette décision pour **produire uniquement le rapport de faisabilité VFS**, sans modifier le code ni exécuter de nouveaux tests, puis remettre au 00 sa recommandation pour arbitrage.
