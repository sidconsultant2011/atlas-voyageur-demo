# Décision 00 — SEC-01 R1-RD01 — Étude documentaire VFS-R01 et G03-R06

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `7a589d961da62ac97ba15fac3abba7c505dd00f2`  
**Priorité unique :** compatibilité et neutralité du wrapper VFS, sans modification de code.

## Sources et constats

- Avis du chat 02 « Priorisation des réserves G03 » reçu le 25 octobre 2026 : **VFS-R01 / G03-R06 condition bloquante prioritaire**.
- PV G03 : `b65-http/PV-03-SEC01-RD01-G03-ASSERTIONS-20261025.md` ; correctif d'assertions reçu.
- Wrapper observé dans GitHub : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`. `sqlite3_io_methods` initialisé en version 1 et `sqlite3_vfs` exposé en version 2 ; la comparaison exhaustive à la VFS native et la neutralité restent **non démontrées**.
- CI n°120 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40208301806, `completed / success`, commit `03986691d23f0044c5fcbe9c1ac2a169f0c938c6`, **223 exécutions réussies** (116 JavaScript, 11 SQLite, 96 HTTP/identité/banc), non nécessairement 223 scénarios distincts.
- G05 : sous-périmètre d'archivage de fichiers propres reçu et conservé, G05 global **PARTIEL**.

## Décision du 00

**GO DOCUMENTAIRE LIMITÉ À VFS-R01 ET G03-R06.** Aucune autre réserve n'est ouverte comme chantier parallèle.

L'étude du chat 01 devra :
1. Inventorier précisément les méthodes `sqlite3_vfs` et `sqlite3_io_methods` exposées par le wrapper, les délégations présentes et les méthodes de la VFS native du runtime SQLite ciblé, en séparant faits confirmés et hypothèses.
2. Évaluer les effets possibles de l'interface I/O V1 et des fonctions non relayées (notamment SHM et fetch) sur le scénario exact : deux bases fictives avec `ATTACH`, `BEGIN IMMEDIATE`, rollback-DELETE et `synchronous=FULL`. Ne pas exiger ni prétendre démontrer une équivalence générale WAL ou multiplateforme.
3. Caractériser les écarts possibles en opérations de fichiers, verrouillages, ordre, latence, retour d'erreurs, synchronisation, comportement multi-thread et chemins transactionnels, y compris l'effet observateur de `write()` après délégation.
4. Établir les conditions d'une comparaison probante VFS native / VFS instrumentée, sans l'exécuter dans ce mandat : invariants mesurables, scénario témoin, critères de différence tolérable et invalidante, besoins de preuves.
5. Préciser les conséquences pour le raccordement futur à `LocalIdentityBridge._persistent_journey()`, sans exécuter ni modifier la voie applicative.
6. Proposer **un verdict GO conditionnel ou NO-GO pour un éventuel correctif isolé**, les prérequis, les limites de preuve et les contrôles indépendants 03 qui seraient nécessaires. Un GO d'implémentation requerra une **nouvelle décision explicite du 00**.

## Interdictions

**Documentation seulement :** aucune compilation/test nouveau, aucun changement du wrapper C ou du banc, aucune instrumentation pré-délégation, aucune barrière, aucun SIGKILL, aucune injection de panne, aucun essai G04, aucun changement du code applicatif, aucune nouvelle dépendance ni substitution de moteur SQLite.

Aucune fusion vers `main`, achat, fournisseur réel, publication ou modification du site public.

## Critère de sortie

Rapport documentaire versionné sur la branche B6.5 avec matrice « constaté / susceptible d'influencer / non démontré », liens précis vers code et références SQLite officielles, différence entre modes VFS et scénario exact, risques résiduels, recommandation motivée et **une seule condition technique prioritaire** pour un éventuel travail ultérieur. Pas de GO expérimental automatique.

## Statuts inchangés

Correctif d'assertions G03 : reçu et clôturé. G03 préparation : reçue avec réserves ; **G04 NO-GO** ; G05 global PARTIEL. **VFS-R01 et G03-R06 OUVERTES**, autres réserves G03-R01 à R07, VFS-R02 à R05 et RD01-R01 à R04 également ouvertes.

**R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

## Prochaine action unique

Confier au chat 01 la seule étude documentaire VFS-R01 / G03-R06, avec rapport de faisabilité à remonter au 00 avant toute nouvelle modification.
