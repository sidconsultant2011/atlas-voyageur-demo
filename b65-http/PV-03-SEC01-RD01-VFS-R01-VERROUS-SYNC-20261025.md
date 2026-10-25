# PV-03-SEC01-RD01-VFS-R01-VERROUS-SYNC-20261025 — Réception indépendante et arbitrage du 00

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Source de recette :** chat 03 — Recette et GitHub Actions  
**Arbitrage et dépôt du PV :** chat 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant enregistrement :** `0749c16a2a0b1a2972c4261529ec21436f480737`.

## Références et preuves

- Décision 00 : `b65-http/DECISION-00-SEC01-RD01-VFS-R01-VERROUS-SYNC-RECEPTION-20261025.md`.
- Rapport 01 : `b65-http/SEC01-RD01-VFS-R01-VERROUS-SYNC-PREUVES-20261025.md`.
- Banc versionné : `b65-http/rd01-vfs-step1/vfs_r01_contention.py`.
- Test versionné : `b65-http/test_vfs_r01_contention.py`.
- Commit effectivement testé : `fc6eded13fa15b8776b12dd0cd494349d0a2e906`.
- GitHub Actions n°135 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980 — `completed / success`, 116/116 tests JavaScript, 11/11 SQLite, 98/98 HTTP/identité/banc : **225 exécutions réussies** (non nécessairement 225 scénarios distincts).
- Le chat 03 a examiné le code et les journaux de CI sans lancer de nouveaux tests locaux ou CI ni modifier le dépôt. Le chat 00 a revérifié le HEAD, le code du banc et le test.

## Contrôle des scénarios de contention

Le protocole utilise N (VFS native) et W (wrapper existant), chacun sur deux bases SQLite fictives attachées dans des répertoires distincts, avec **deux connexions et deux threads du même processus**, des événements Python hors SQLite bornés à huit secondes, `busy_timeout=0`, `BEGIN IMMEDIATE`, `journal_mode=DELETE`, `synchronous=FULL`.

Pour les scénarios **COMMIT** et **ROLLBACK** normaux du premier écrivain :
- La tentative incompatible du second écrivain reçoit `SQLITE_BUSY=5` dans N et W.
- Après libération normale, le second écrivain peut acquérir sa transaction et la valider.
- Les états intermédiaires sont identiques N/W : COMMIT donne session=1 / parcours=holder ; ROLLBACK conserve session=0 / parcours=initial.
- Les états finaux sont identiques : session=2 / parcours=contender.
- `integrity_check=ok/ok`, DELETE/DELETE et FULL(2)/FULL(2), aucun journal résiduel après fermeture normale.
- Assertions bloquantes présentes dans `test_vfs_r01_contention.py`.
- Le journal W signale **45 retours `xSync` avec code 0** ; le témoin N n'est pas instrumenté de manière équivalente.

**VERDICT DE RECETTE INDÉPENDANTE : FAVORABLE AVEC RÉSERVES** pour la parité opérationnelle des effets d'exclusion, libération, visibilité et annulation des transactions dans les deux scénarios déterministes exécutés.

## Limites et réserves

- **VFS-R01 / G03-R06 ouvertes** : absence de parité événementielle `xSync/xLock/xUnlock` démontrée et de neutralité temporelle générale.
- Les 45 retours `xSync` de W ne prouvent ni synchronisation physique durable ni séquence native N identique.
- La contention interprocessus, WAL, mmap, VFS V2/V3, les anomalies sous charge, le chemin métier `_persistent_journey()`, l'atomicité sous panne et la récupération après crash restent **non qualifiés**.
- Les barrières Python et fermetures nominales sont bornées ; un `join(TIMEOUT)` sur thread bloqué permet d'identifier un échec du banc sans garantir universellement sa terminaison.
- Aucune panne simulée, aucun SIGKILL ni expérimentation G04 ; aucun changement du wrapper C ou du code métier.

## Décision du 00

**ACCEPTER la réception indépendante des effets transactionnels N/W sur COMMIT et ROLLBACK normaux. CLÔTURER uniquement le sous-chantier de qualification de contention observable.** Les résultats et le PV deviennent une référence expérimentale limitée au profil testé. Aucune clôture automatique de VFS-R01, G03-R06, R1-RD01, R1 ou P0-01.

**G03 : préparation reçue avec réserves ; G04 : NO-GO ; G05 global : PARTIEL ; VFS-R01, G03-R06 et autres réserves documentées : OUVERTES ; R1-RD01 : OUVERTE ; R1-C01 : PARTIEL ; R1 : OUVERTE ; P0-01 : OUVERT ; B6.5 : EN RECETTE ; B6.3 : NO-GO ; PRODUCTION : NO-GO.**

**Aucune nouvelle instrumentation, correction du wrapper, injection, SIGKILL, modification applicative, fusion main, publication ou activation fournisseur autorisée par le présent PV.**

## Suite de gouvernance

La réception termine la campagne de contention, sans démontrer une neutralité intégrale. Avant une prochaine expérimentation, le chat 02 doit préciser si les preuves du profil rollback-DELETE sont suffisantes pour la phase préparatoire courante, ou définir **une condition probatoire résiduelle unique et falsifiable** justifiant une étude distincte. Cette analyse est documentaire uniquement et n'autorise aucun développement ni G04.

## Prochaine action unique

Transmettre ce PV au chat 02 et solliciter un avis documentaire sur une seule condition de preuve résiduelle, avant tout nouveau GO technique.
