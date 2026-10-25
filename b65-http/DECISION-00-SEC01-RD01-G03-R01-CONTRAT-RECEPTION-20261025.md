# Décision 00 — SEC-01 R1-RD01 — Réception documentaire du contrat G03-R01

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `188a9dfed3c6cb4d500f1a6f14e679e7ee262462`  
**Chantier unique suivant :** avis indépendant de sécurité 02 sur la faisabilité du contrat G03-R01.

## Sources et contrôles

- Mandat du 00 : `b65-http/DECISION-00-SEC01-RD01-G03-R01-ETUDE-CAUSALE-20261025.md`.
- Contrat remis par le chat 01 : `b65-http/SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md`.
- GitHub : comparaison depuis `3114d83daf4004dd866eca916fbf4f74eda0d6a5` jusqu'à `188a9dfed3c6cb4d500f1a6f14e679e7ee262462` ; **un seul document ajouté**, sans modification C, Python, métier ou workflow.
- Aucune nouvelle exécution de tests locaux ni GitHub Actions pour ce document. CI n°135 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980, référence expérimentale **antérieure** sur le commit `fc6eded13fa15b8776b12dd0cd494349d0a2e906`, sans validation du contrat causal.

## Réception et portée du document

**RÉCEPTION DOCUMENTAIRE FAVORABLE DU LIVRABLE 01**, limitée à la complétude du contrat de conception remis au regard du mandat.

Le document définit :
- le point logique de suppression du super-journal en COMMIT rollback multi-bases **lorsqu'un super-journal est effectivement utilisé**, sans l'assimiler à une preuve de durabilité physique ;
- les identités nécessaires pour associer transaction, participants, fichiers, super-journal, invocation `xDelete` et provenance ;
- des couples d'événements `BEFORE_DELEGATE` / `AFTER_RETURN` avec `invocation_id`, retour natif et conservation qualifiée ;
- les risques d'effet observateur, de non-réentrance, de concurrence, de latence et de réduction des capacités de la VFS ;
- huit critères falsifiables C01 à C08 pour une **éventuelle** réalisation distinctement autorisée ;
- la **condition bloquante unique** : liaison non ambiguë `transaction multi-bases → super-journal identifié → invocation xDelete` avec phase `BEFORE_DELEGATE` vérifiable sans dégrader la sémantique ni les acquis N/W.

Les exigences non réalisées ne doivent pas être présentées comme des preuves : le wrapper courant reste post-délégation et ne fournit pas d'identifiant transactionnel attesté, d'identité complète des fichiers ou de couples entrée/sortie opérationnels.

## Arbitrage du 00

**GO pour avis indépendant de sécurité documentaire au chat 02, sur le contrat G03-R01 uniquement.** Ce GO ne préjuge pas de l'approbation du contrat ni de la faisabilité de son implémentation.

Le chat 02 devra :
1. examiner la faisabilité et la cohérence des exigences C01–C08 avec l'API VFS réellement disponible, notamment le fait que `sqlite3_vfs.xDelete` porte sur un chemin sans handle ni identifiant SQL de transaction ;
2. distinguer les corrélations démontrables des identifiants seulement proposés, la cardinalité des participants et l'origine du rôle super-journal ;
3. évaluer si un mécanisme de preuve avant délégation pourrait être conçu **sans modifier les garanties nécessaires au scénario rollback-DELETE reçu**, sans réentrance SQLite et sans masquer les réserves VFS-R01 / G03-R06 ;
4. qualifier la conservation réelle des traces : émission, réception, acquittement, synchronisation et persistance restent des états différents ;
5. rendre un verdict motivé **GO documentaire conditionnel / NO-GO** sur la faisabilité future, avec **une condition falsifiable prioritaire**, risques résiduels et pièces de preuve à exiger avant un éventuel mandat au chat 01.

**Aucune modification du wrapper, du banc, des tests, du code métier ou du workflow. Aucun test ou CI nouveau autorisé par cet arbitrage.** Aucun arrêt causal, SIGKILL, panne, G04, fournisseur réel, fusion `main` ou publication.

## Statuts maintenus

Contrat G03-R01 : **reçu documentairement, en attente de l'avis de sécurité 02**. G03-R01 : **OUVERTE** ; G03 préparatoire : reçu avec réserves ; VFS-R01 et G03-R06 : **OUVERTES** ; G04 : **NO-GO** ; G05 global : **PARTIEL** ; R1-RD01, R1 et P0-01 : **OUVERTS** ; R1-C01 : **PARTIEL** ; B6.5 : **EN RECETTE** ; B6.3 : **NO-GO** ; production : **NO-GO**.

## Prochaine action unique

Transmettre au chat 02 le contrat et la présente décision pour un avis indépendant de faisabilité documentaire sur G03-R01, sans développement ni expérimentation.
