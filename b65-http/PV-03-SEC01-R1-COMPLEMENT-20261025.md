# PV-03-SEC01-R1-COMPLEMENT-20261025 — Réception indépendante et arbitrage 00

**Projet :** ATLAS VOYAGEUR — B6.5  
**Date :** 25 octobre 2026  
**Origine du PV :** 03 — Recette et GitHub Actions  
**Enregistrement et décision :** 00 — Pilotage et gouvernance  
**Nature :** transcription fidèle des conclusions de recette remises au 00, complétée de l'arbitrage sur la réserve R1-RD01. Aucun nouveau test exécuté pendant cet enregistrement.

## Versions et preuves

- Dépôt : `sidconsultant2011/atlas-voyageur-demo`
- Branche : `feature/b6-5-cartographie-interactive`
- HEAD contrôlé avant enregistrement : `b1788a0131bad754a1e31fa08b1764f1ce3de51a`
- Commit des tests : `6886eff86ea5479f68a88a2893bc4fdbaa2608f5`
- Commit du dossier complémentaire : `b1788a0131bad754a1e31fa08b1764f1ce3de51a`
- Workflow : `.github/workflows/b65-calculateur-tests.yml`
- GitHub Actions n°83 : `40184360880`, job `121141892112`, `completed / success` sur `6886eff8`
- Test : `b65-http/test_sec01_r1_complements.py`
- Dossier source : `b65-http/SEC01-R1-COMPLEMENT-PREUVES-01-20261025.md`
- CI : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40184360880

## Résultat automatisé

- 116 exécutions JavaScript réussies ;
- 11 exécutions SQLite réussies ;
- 94 exécutions HTTP et identité réussies ;
- **221 exécutions réussies, zéro échec** ; ce nombre ne constitue pas 221 scénarios distincts.
- Quatre nouveaux tests R1 identifiés comme réussis dans les journaux.
- Aucun nouveau test local exécuté par le chat 03.

## Réception indépendante par le chat 03

| Critère | Verdict 03 | Portée |
|---|---|---|
| R1-C01 — Point unique de prise d'effet | **PARTIEL** | COMMIT défini, paramètres observés ; durabilité atomique lors d'une panne pendant COMMIT non démontrée |
| R1-C02 — Absence d'effets post-révocation | **RECEVABLE** | Entrelacements forcés et effets SQL dans le pont persistant local |
| R1-C03 — Sérialisation SQLite | **RECEVABLE** | `BEGIN IMMEDIATE` et sérialisation examinée |
| R1-C04 — Isolation et mutations | **RECEVABLE** | Création, modification, suppression et propriété contrôlées |
| R1-C05 — Refus HTTP après révocation | **RECEVABLE** | Requêtes commencées après confirmation refusées 401, avec vérification SQL ; pas de preuve d'entrelacement HTTP forcé en cours de révocation |
| R1-C06 — Concurrence multiprocessus | **RECEVABLE** | Verrou effectivement constaté dans un processus fils partageant la même base locale |
| R1-C07 — Non-régression | **RECEVABLE** | Suites B6.5 réussies dans leur périmètre automatisé |

**Bilan 03 : six critères recevables localement ; R1-C01 partiel ; réception favorable avec réserve résiduelle.**

Le test de synchronisation utilisant `assertNotIn("revoke", outcomes)` ne prouve pas isolément que le révocateur a tenté le verrou ; les conclusions reposent sur l'ensemble des mécanismes et observations. Le test de rollback avant COMMIT ne simule pas une interruption brutale pendant le COMMIT.

## Réserve R1-RD01 — Durabilité atomique multi-fichiers

**Non levée.** Les fixtures CI ont observé `journal_mode=DELETE` et `synchronous=FULL` sur les deux bases attachées et un rollback explicite avant COMMIT. Il manque une preuve contrôlée de cohérence de récupération après interruption brutale au cours d'un COMMIT multi-bases, ainsi que la qualification des préconditions et limites de stockage.

Cette réserve constitue une **insuffisance de preuve**, sans démonstration de corruption.

## Décision du 00

1. **Accepter** le procès-verbal indépendant et la réception des six critères dans le périmètre SQLite local testé.
2. **Maintenir R1-C01 partiel et R1-RD01 ouverte et bloquante** pour une clôture complète de R1 ; ne pas extrapoler la sérialisation à une garantie de durabilité face aux pannes.
3. **Maintenir R1 OUVERTE, P0-01 OUVERT, B6.5 EN RECETTE, B6.3 NO-GO et production NO-GO.** R2 à R4 inchangées.
4. **Ne pas modifier le code** avant définition d'un protocole ciblé. La prochaine étape porte exclusivement sur le cadrage de la preuve R1-RD01 : configuration SQLite effective, conditions de stockage local et de journalisation, test d'interruption contrôlée au COMMIT et contrôle des deux bases après récupération, conditions d'acceptation et limites explicites. Aucun résultat n'est présumé.
5. Aucun achat, fusion vers `main`, activation de fournisseur réel ni publication ou modification du site public n'est autorisé.

## Prochaine action unique

**Chat 02 — Sécurité P0 :** établir le protocole reproductible et les critères d'acceptation de la qualification R1-RD01 sur le prototype SQLite local, sans nouvelle modification de code et avant arbitrage d'exécution du 00.
