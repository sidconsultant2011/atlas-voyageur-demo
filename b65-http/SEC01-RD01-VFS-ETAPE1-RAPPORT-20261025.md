# SEC-01 R1-RD01 — Préqualification VFS, étape 1 — Rapport au chat 03
**Date :** 25 octobre 2026  
**Mission du 00 :** `b65-http/DECISION-00-SEC01-RD01-PROTOTYPE-VFS-ETAPE1-20261025.md`  
**Branche :** `feature/b6-5-cartographie-interactive`  
**Base vérifiée avant travail :** `e57ff544cacf7fc3a18c2086ff446c9bebba269d`  
**Aucune modification applicative, aucune injection de panne, aucun SIGKILL, aucune installation globale.**

## 1. Modifications autorisées et preuves
- `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c` : wrapper VFS natif d'observation, construit localement et chargé **dans le processus Python du banc** ; commit `0c81a2a6a54a66bf359608b0bd99464b13e7acd0`.
- `b65-http/rd01-vfs-step1/rd01_vfs_step1.py` : compile le wrapper avec le compilateur et `libsqlite3` système existants, vérifie l'identité de symboles, ouvre deux bases fictives via `ATTACH`, collecte les traces puis archive les fichiers après fermeture normale ; commit `c52dd144d67f88efad3f6247a70a429cfc2f52fb`.
- `b65-http/test_rd01_vfs_step1.py` : scénario intégré aux tests B6.5, commit `f59c66b896bb8a5f0c6f42d09e6f0fd74dd702ce`.
- Correctif ciblé de portabilité du banc : `6179d7d869a9ec5718097656a6b052768fc4b387`. L'exécution précédente n°100 avait échoué au **stade de compilation du banc**, sans erreur applicative. Diagnostic du compilateur désormais restitué, et suppression de `-Werror`, sans désactivation des avertissements.

**GitHub Actions n°101 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40203935190  
**Commit exécuté :** `6179d7d869a9ec5718097656a6b052768fc4b387`.  
**Résultat :** completed / success.
- JavaScript : 116/116.
- SQLite existant : 11/11.
- HTTP et identité, dont 1 test de préqualification VFS : 96/96.
- Total : 223 exécutions de tests réussies, non nécessairement 223 scénarios uniques.
- Tests locaux de préparation exécutés dans le conteneur de conversation : prototype fonctionnel sous Linux 6.18.55 / Python 3.13.5 / SQLite 3.46.1 ; **la preuve d'intégration versionnée finale est la CI n°101**, pas la préparation locale.

## 2. Environnement CI attesté
- Linux `6.17.0-1022-azure-x86_64-with-glibc2.39`.
- Python `3.12.3`, moteur SQLite rapporté par le module Python `3.45.1`.
- Bibliothèque `libsqlite3.so.0`, version appelée via le wrapper `3.45.1`.
- Adresse du symbole `sqlite3_vfs_find` fournie par le wrapper identique à l'adresse obtenue via `libsqlite3.so.0` dans **ce processus**.
- Fichiers sur même `st_dev` ; deux `journal_mode=DELETE`, deux `synchronous=FULL (2)`.
- Compilation avec `cc`, `-shared -fPIC`, et `-lsqlite3`, **temporaire uniquement**. Aucun nouveau paquet ni bibliothèque externe introduits.

Cette combinaison fournit une **forte preuve opérationnelle G01 dans le runner ciblé**. Elle ne constitue pas une certification ABI multi-plateforme ni une preuve d'équivalence de toutes les méthodes VFS au runtime non instrumenté ; le chemin métier `_persistent_journey()` n'a pas été directement invoqué dans ce test.

## 3. Matrice de réception technique

| Porte | Verdict proposé au 03 | Preuves et limites |
|---|---|---|
| **G01 — Même moteur** | **DÉMONTRÉ SUR LE RUNNER CIBLÉ, réserve d'ABI et de chemin métier** | versions 3.45.1 concordantes, même adresse du symbole SQLite natif, absence d'autre moteur volontairement installé, même processus Python ; pas de validation ABI sur d'autres plateformes |
| **G02 — Deux bases** | **DÉMONTRÉ POUR LE BANC FICTIF ; PAS POUR `_persistent_journey()`** | événements `xOpen` des fichiers `sessions.sqlite` et `identities.sqlite`, journaux observés, candidat super-journal observé ; pas de trace sur la méthode métier originale |
| **G05 — Préservation** | **PARTIEL** | trois fichiers conservés en lecture brute avant ouverture SQLite de la copie ; taille et SHA-256 vérifiés ; invariants SQL et `integrity_check=ok` sur copie ; pas de journal chaud à capturer après crash, pas d'artefact brut persistant en CI |

### 3.1 Compteurs de traces (CI n°101)
- `xOpen` : 8.
- `xWrite` : 60.
- `xSync` : 16.
- `xDelete` : 6.
- `xFileControl` : 31.
- Fichiers de bases observés : `sessions.sqlite`, `identities.sqlite`.
- Journaux et candidat super-journal : `sessions.sqlite-journal`, `identities.sqlite-journal`, `sessions.sqlite-mj9A68A5901`.
- Un fichier identifié par le flag SQLite `SQLITE_OPEN_MASTER_JOURNAL` est **candidat super-journal** ; son rôle causal dans une interruption interne n'a pas été testé.

Le journal CI `RD01 VFS STEP1 PROOF` détaille ces compteurs ainsi que les SHA-256 et tailles des fichiers copiés. Les noms du candidat super-journal sont dynamiques et non des identifiants pérennes.

### 3.2 Archives G05 de ce témoin *sans panne*
`manifest_raw` issu de CI n°101 :
- `sessions.sqlite` : 12 288 octets, SHA-256 `06c7754b8e08eb99a5c6c2fb87f601dd9eb265fd9d060c0cb06ec472eeea4f54`.
- `identities.sqlite` : 12 288 octets, SHA-256 `ec92c9e566d0c146e4a087aa7c44d31b3644d6f07efc690f88d79f6f0b7d1d4a`.
- `vfs.tsv` : 4 837 octets, SHA-256 `0a96444451f4cbc9d2c1706bcacecda0dc8f8ad705f7b5471d7120185e9dd128`.

Les copies brutes et de récupération restent **temporaires**, supprimées en fin de test. Aucun journal rollback « chaud » n'existe après ce COMMIT normal et sa fermeture. Les SHA des journaux *pendant* la transaction ne peuvent donc pas être revendiqués. Les empreintes sont ici des résultats du runner CI n°101 et ne doivent pas être présumées constantes ailleurs.

## 4. Limites d'observation, neutralité et sécurité
1. Le wrapper expose des méthodes I/O version 1 à son client et ne relaie pas les extensions de version 2/3 (SHM, `xFetch`, `xUnfetch`). Le VFS enregistré utilise une version 2 pour accéder à `xCurrentTimeInt64` ; ce choix **modifie la surface d'optimisation** par rapport au VFS hôte. Il est acceptable pour observer des accès du banc en rollback-DELETE, mais **pas preuve d'équivalence VFS complète** pour production ou étapes G03/G04. Une future évolution nécessiterait un nouvel arbitrage.
2. Traçage `write()` non synchrone et noms de fichiers réduits au basename ; instrumenter `xWrite/xSync/xDelete` affecte l'ordonnancement. L'étiquette `main-db` est celle du type d'ouverture SQLite et **pas** la garantie que seule la base principale de la connexion globale est concernée : vérifier le nom réel.
3. La transaction fictive teste deux écritures avec `ATTACH`, mais ne réexécute pas directement `_persistent_journey()`. Toute extrapolation à cette voie et à `LocalState` est interdite.
4. La conservation de deux fichiers propres et d'une trace avant leur ouverture sur copie satisfait uniquement une preuve de **méthode de copie**. Aucun journal chaud, recovery post-crash ou archive GitHub Actions téléchargeable n'est démontré.
5. Aucun SIGKILL, arrêt de processus pendant COMMIT, fault injection, crash OS, panne électrique, WAL, multi-hôtes ou test fournisseur réel.
6. La liaison native VFS est limitée au banc enfant / processus Python de test. Aucun composant global n'est modifié, aucune clé/API incluse.

## 5. Décision attendue et continuité
**Proposition au 03 : G01 démontré sur plateforme CI, G02 démontré dans le banc, G05 partiel.** La preuve couvre des ouvertures et une capture propre, pas un arrêt interne ni la conservation des journaux avant récupération d'une panne. Une validation ou un changement de statut doit être décidé séparément par 03 puis 00.

**RD01-R01 à RD01-R04 ouvertes ; R1-RD01 ouverte ; R1 et P0-01 ouverts ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.**

**Prochaine action unique :** réception indépendante par le chat 03 du commit `6179d7d`, des journaux CI n°101 et du présent rapport, sans autorisation implicite de G03/G04.
