# Décision 00 — SEC-01 R1-RD01 — Dernière étude documentaire C03-3 : disponibilité des références croisées et collecte passive

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `5a882a79851fe64bfaddfaba622021d4cc35dd22`  
**Priorité technique unique :** décider de la faisabilité d'une preuve réciproque S↔A/B au moyen d'une collecte passive, sans implémenter celle-ci.

## Sources vérifiées et provenance

- Rapport 01 : `b65-http/SEC01-RD01-G03-R01-C03-ETUDE-FAISABILITE-20261025.md`.
- Réception 00 : `b65-http/DECISION-00-SEC01-RD01-G03-R01-C03-RECEPTION-20261025.md`.
- Wrapper : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`, avec `xOpen`, `xWrite` et `xDelete` existants.
- Avis indépendant du chat 02, 25 octobre 2026 : **GO documentaire conditionnel, NO-GO réalisation immédiate** ; recommandation d'examiner la disponibilité des références croisées entre super-journal S et deux journaux rollback A/B et leur collecte passive dans le profil SQLite ciblé.
- CI n°135, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980, commit `fc6eded13fa15b8776b12dd0cd494349d0a2e906`, référence N/W préexistante ; **ne démontre pas C03-3**.
- Documentation SQLite citée par l'étude : `https://www.sqlite.org/atomiccommit.html` et `https://www.sqlite.org/c3ref/vfs.html`. Les hypothèses de format et d'accessibilité dans la version ciblée doivent rester à qualifier.

## Décision du 00

**GO DOCUMENTAIRE UNIQUEMENT POUR UNE DERNIÈRE ÉTUDE CIBLÉE C03-3.**

Une méthode serait conceptuellement probante si S référençait précisément A et B, que A et B référençaient ce même S, et qu'un cycle de vie non ambigu permettait ensuite de lier `xDelete(S)` à la bonne incarnation du fichier. **Aucune de ces preuves croisées n'a encore été extraite du banc.**

### Mission documentaire du chat 01

1. Déterminer, à partir du code et des documents officiels SQLite, le **format et les moments de disponibilité** des références S→A/B et A/B→S dans le profil Python SQLite 3.45.1 rollback-DELETE, `ATTACH`, deux bases modifiées, `synchronous=FULL` ; séparer les garanties documentées des suppositions propres à la version.
2. Étudier **sans l'exécuter** la possibilité de collecter les références de manière passive depuis les buffers déjà passés à `xWrite` et les identités `xOpen`/cycle de vie ; documenter offsets, écritures partielles, écrasements, ordres, codes de retour, type de fichier et limites de réception, sans supposer qu'un buffer écrit est physiquement durable.
3. Préciser comment associer S à **une incarnation unique** de A et B, puis à la cible `xDelete`, sans se fier seulement aux chemins, basenames, timestamps ou `run_id`, sans supposer un `transaction_id` transmis par SQLite.
4. Évaluer les risques : mémorisation des fragments, concurrence, durée de vie, latence et allocation, lecture à chaud, réentrance, sécurité des traces, effet observateur et conséquences sur les acquis N/W.
5. Produire une **matrice de suffisance probatoire** indiquant pour chaque lien ce qui est documenté, ce qui serait techniquement observable, ce qui exige une nouvelle instrumentation et ce qui demeure non démontrable sans autre source.
6. Conclure par un **GO conditionnel de faisabilité** assorti de prérequis falsifiables, ou par un **NO-GO motivé**, sur une condition unique. Éviter une simple recommandation de nouvelle étude générale ; remonter une décision exploitable au 00.

**Livrable unique :** rapport documentaire versionné sur la branche B6.5, avec sources, limites, critères de rejet et proposition pour un éventuel mandat expérimental minimal distinct.

### Interdictions

Aucune modification C/Python, du wrapper, du banc, du code métier, des tests ou du workflow. Aucune compilation, aucun nouveau test local ou CI ; aucune lecture intrusive de journaux à chaud, aucun registre instrumenté, aucun callback pré-délégation, aucune réentrance SQLite. Aucun SIGKILL, arrêt causal, panne, G04, publication, fournisseur réel ou fusion `main`.

## Portée et statuts

**G03-R01, C03-3, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS**. G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE ; B6.3 et production NO-GO.

Une réussite documentaire ne prouve pas la capacité réelle de collecte, ni `BEFORE_DELEGATE`, ni la neutralité ni la durabilité physique.

## Prochaine action unique

Transmettre au chat 01 le mandat de dernière étude documentaire de collecte passive C03-3, avec verdict de faisabilité obligatoire avant nouvel arbitrage du 00.
