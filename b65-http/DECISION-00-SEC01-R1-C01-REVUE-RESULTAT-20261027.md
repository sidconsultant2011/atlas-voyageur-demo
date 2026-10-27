# 00 — SEC-01 R1-C01 — Réception de la revue documentaire et arbitrage

**Date :** 27 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `29fe36ba4ebbb366da25f1bf8694264e0f7ccd7e`  
**Autorité :** 00 — Pilotage et gouvernance.

## Sources examinées

- Revue indépendante 02 reçue dans le chat 00 le 27 octobre 2026, titre `02 — SÉCURITÉ P0 — Revue indépendante du contrat R1-C01`, verdict **NON CONCLUANT**. Ce rapport est reçu en conversation ; sa présence comme fichier autonome dans le dépôt n'est pas attestée.
- Mandat précédent : `b65-http/DECISION-00-SEC01-R1-C01-REVUE-CONTRAT-ATOMICITE-20261027.md`.
- Examen direct du code sur la branche, notamment `b65-http/persistent_sessions.py`, `b65-http/local_identity_bridge.py` et `b65-http/local_http_facade.py`.
- Preuves antérieures : `b65-http/DECISION-00-SEC01-R1-HTTP-REVOCATION-CONCURRENTE-RECETTE-20261027.md`, `b65-http/DECISION-00-SEC01-R1-CRITERES-20261025.md`, `b65-http/DECISION-00-SEC01-R1-RD01-PROTOCOLE-20261025.md`, `b65-http/SEC01-R1-RD01-RAPPORT-EXPERIMENTAL-01-20261025.md`.

## Faits établis dans leur périmètre

1. `PersistentSessionState.revoke()` dans `persistent_sessions.py` exécute `BEGIN IMMEDIATE` puis `UPDATE sessions SET revoked=1` dans `sessions.sqlite`. Le `return 200` normal est situé après sortie du contexte transactionnel : le chemin ne combine **pas** automatiquement cette révocation HTTP avec une mutation de `identities.sqlite`.
2. `LocalIdentityBridge._persistent_journey()` attache `identities.sqlite` à la connexion de `sessions.sqlite` et ouvre `BEGIN IMMEDIATE`. L'autorisation et l'opération métier du pont persistant sont coordonnées dans cette transaction. Une opération de ce pont ne modifie pas nécessairement les deux bases ; la présence d'`ATTACH` n'en fait pas à elle seule une mise à jour simultanée.
3. La fixture RD01 associe explicitement une modification de révocation en base sessions et une insertion métier en base identités. Elle **n'est pas une reproduction exacte de chaque révocation HTTP**.
4. Le code de connexion consulté `PersistentSessionState.connect()` applique un `busy_timeout`, mais n'impose pas explicitement `journal_mode=DELETE`, `synchronous=FULL`, interdiction WAL, ni préconditions complètes de stockage à toutes les connexions. Ces paramètres étaient observés dans des bancs particuliers ; leur application future n'est pas qualifiée.
5. La logique de COMMIT avant HTTP 200 dans le chemin `revoke()` est étayée par l'inspection du code ; la traduction HTTP maîtrisée de toute erreur SQLite ne l'est pas. Le refus après révocation en état sain est réceptionné localement, mais la détection d'une récupération incohérente suivie d'un refus par défaut n'est pas démontrée de manière générale.
6. Les quinze résultats historiques du banc RD01 sont favorables dans leurs cinq fenêtres externes, pas dans toutes les sous-étapes internes du COMMIT, ni lors de pannes OS/matérielles. Aucun état partiel réel observé n'est attesté par les sources.

## Décision officielle du 00

**RÉCEPTION DU RAPPORT DOCUMENTAIRE 02 — VERDICT : NON CONCLUANT pour la qualification globale de récupération R1-C01.**

Il ne s'agit ni d'un constat d'échec applicatif ni d'un GO de sécurité. La distinction entre révocation mono-base et opérations du pont utilisant `ATTACH` est reconnue et doit éviter tout approfondissement expérimental mal ciblé.

**R1-C01 reste PARTIEL ; R1-RD01, R1 et P0-01 restent OUVERTS.**

### Chantier prioritaire unique suivant — documentation du contrat applicable

**GO DOCUMENTAIRE CIBLÉ POUR LE CHAT 04 — DOCUMENTATION TECHNIQUE**, uniquement pour formaliser un **contrat opposable de configuration SQLite et de reprise en sécurité du prototype fictif persistant**, à partir de la revue 02 et de sources GitHub réelles. Ce contrat ne doit pas se présenter comme une propriété déjà implémentée ou validée.

Livrable : un document versionné identifiant, **opération par opération**, les bases lues et modifiées, le point logique de validation, les invariants AVANT/APRÈS, les états interdits et les attentes de récupération. Distinguer impérativement révocation HTTP mono-base, parcours du pont `ATTACH`, suppression d'association mémoire et transaction témoin RD01. Associer à chaque exigence sa preuve du code/tests, son statut vérifié/non démontré, les préconditions d'hébergement et de stockage (disque, systèmes de fichiers, journalisation/WAL, synchronisation, topologie) ainsi que la conduite attendue en cas d'incohérence (refus sécurisé comme **exigence proposée**, non résultat testé). Prévoir les erreurs de COMMIT et leur traduction HTTP sans inventer une implémentation. Contenir une seule proposition de vérification future, soumise à une autorisation séparée du 00.

**Exclusions :** aucune modification de code, migration SQLite, exécution de tests, nouvelle CI, panne simulée, SIGKILL, instrumentation VFS/`BEFORE_DELEGATE`, extension C03, G04, fournisseur réel, achat, fusion main ou production. La documentation ne lève pas R1-C01.

### Statuts

- R1-C01 : **PARTIEL** ; R1-RD01, R1, P0-01 : **OUVERTS**.
- R1-C02 à C07 : recevables seulement dans les périmètres fictifs historiquement qualifiés.
- C03-R01 à R04 : clôtures expérimentales ciblées ; C03-R05 ouverte/suspendue ; C03-R06 ouverte, lots 1 et 2 reçus.
- C03-3 global, G03-R01, VFS-R01, G03-R06 : **OUVERTS**.
- B6.5 : en recette ; B6.3, G04, production : **NO-GO**.

## Prochaine action unique

Transmettre au chat 04 la mission documentaire bornée de rédaction du contrat R1-C01, sans développement ni nouveau test.
