# SEC-01 R1-C01 — AC-08 — Correctif SQLite DELETE/FULL — Preuves d'implémentation

**Date :** 27 octobre 2026. **Chantier prioritaire unique :** AC-08, prototype SQLite fictif local.  
**Autorité :** décision `b65-http/DECISION-00-SEC01-R1-C01-AC08-GO-IMPLEMENTATION-20261027.md`.  
**Cadrage accepté :** `b65-http/SEC01-R1-C01-AC08-CADRAGE-TECHNIQUE-20261027.md`.  
**Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD initial vérifié :** `029793f7101e5fd3b9c458050d25e4a7d9ef1d4d`.

## 1. Changement borné effectivement réalisé

- `b65-http/sqlite_ac08.py` (**nouveau**) : définit `SQLitePreconditionError` et les contrôles communs. Une fixture nouvelle est créée en `mode=rwc`, puis `PRAGMA main.journal_mode=DELETE` est exécuté et sa réponse relue ; `PRAGMA main.synchronous=FULL` est établi et relu (`2`). Une base **existante** est ouverte en `mode=rw`, son `journal_mode` est **lu avant toute conversion** ; si la valeur n'est pas `delete`, l'ouverture protégée est refusée. Chaque connexion vérifie `synchronous=FULL` après configuration. `foreign_keys=ON` reste activé et vérifié pour les identités. Le chemin `:memory:` ou de forme URI `file:` passé comme argument applicatif est rejeté.
- `b65-http/persistent_sessions.py` : route les connexions vers l'utilitaire commun ; autorise la création de la fixture seulement lors de l'initialisation ; conserve `busy_timeout=10000`, les tables et méthodes existantes. Aucune modification du comportement métier ni de `BEGIN IMMEDIATE`.
- `b65-http/fictional_identities.py` : route `_db()` vers la même politique, avec contrôle explicite de `foreign_keys=ON`. La création de fixture est réservée à l'initialisation.
- `b65-http/local_identity_bridge.py` : exige l'existence du fichier d'identités **avant `ATTACH`** pour éviter sa création implicite ; après attachement et **avant `BEGIN IMMEDIATE`**, vérifie l'alias `identity_db`, les chemins principaux réels, les modes `DELETE` et les deux synchronisations `FULL`. Vérifie aussi, à titre d'indice local, l'égalité `st_dev` des fichiers ; cela ne garantit pas la durabilité physique ni un même système de stockage réel.

**Défaut sécurisé AC-08 :** une configuration non conforme lève `SQLitePreconditionError` avec un code stable ne contenant aucun jeton, cookie ni nom de personne. La mutation protégée n'est pas exécutée et aucun résultat métier de succès n'est retourné par ces chemins. Le comportement de sérialisation SQLite normal reste inchangé. **Le mappage HTTP des exceptions SQL n'a pas été modifié ; AC-13 demeure un autre chantier.**

**Exclusions respectées :** pas de code C/VFS/C03, de workflow, de moteur SQLite, de modification de `local_http_facade.py`, d'application métier, de `main`, de migration automatique, de fournisseur réel, de SIGKILL ou de G04.

## 2. Commits techniques

| Commit | Modification |
|---|---|
| `1cb8eedd8fd6ef118872ed3a1336ee9148911629` | utilitaire SQLite AC-08 |
| `6897a58502aa3d02db0b560d0bc8c453386e123a` | ouverture des sessions |
| `b105581df486582f9416131d8c12a5e729c5198e` | ouverture des identités |
| `68b6d0d9092ac0d6330d4644bd0010283cdb83b2` | vérification `ATTACH` |
| `79d325447e5ed759fa5f02a4dcf15375014f8a72` | ajout de huit tests AC-08 |
| `e9b4aed60c60b39a86793b69387cb7f79fa31258` | vérification préalable d'existence |
| **`eb97c24eb969b2a28f4276b1c489d7eb46a6c6a4`** | refus de l'attachement implicite ; **commit final testé** |

## 3. Tests ciblés AC-08 — résultats observés

| Cas | Résultat CI n°238 |
|---|---|
| Deux fichiers nouveaux DELETE/FULL sur chaque nouvelle connexion, `foreign_keys`, `busy_timeout` | PASS |
| `ATTACH` existant et deux bases DELETE/FULL avant `BEGIN IMMEDIATE` | PASS |
| Base sessions existante en WAL : refus, aucune conversion, état `revoked` inchangé | PASS |
| Base identités existante en WAL : refus, aucun nouveau parcours, WAL inchangé | PASS |
| Fichier identités supprimé après initialisation : refus avant `ATTACH`, pas de recréation | PASS |
| Chemins `:memory:` et `file:` : refus | PASS |
| Alias d'attachement incorrect : rejet | PASS |
| Réouverture des deux fichiers compatibles ; opérations d'identité et révocation préservées | PASS |

Les tests manipulent exclusivement des données locales fictives. Le refus WAL n'est **pas** une migration ; le contenu existant et le mode WAL restent inchangés dans les cas testés.

## 4. Historique GitHub Actions, erreurs et séparation local/CI

- **CI n°236**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587789860, commit `79d325447e5ed759fa5f02a4dcf15375014f8a72` : `completed / failure`. Le test `test_missing_fixture_after_creation_never_recreated` démontrait qu'avec `ATTACH DATABASE ?`, SQLite recréait une base absente avant le contrôle post-attachement, jusqu'à l'échec SQL `no such table`. Ce défaut a donné lieu aux commits `e9b4aed6` et `eb97c24e`. L'échec n'est pas masqué.
- **CI n°238**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587946581, commit **`eb97c24eb969b2a28f4276b1c489d7eb46a6c6a4`** : **`completed / success`** ; **116/116 JavaScript**, **11/11 SQLite** et **161/161 HTTP/identité/sécurité**, soit **288 exécutions réussies**, pas nécessairement 288 scénarios uniques. Huit tests AC-08 explicitement `ok`, suites R1 et B6.5 incluses.
- **Tests locaux du commit complet : non exécutés.** Une tentative de `git ls-remote` depuis l'environnement local a échoué : `Could not resolve host: github.com`. Les logs GitHub Actions ne sont pas des tests locaux. Aucun succès local n'est revendiqué.

## 5. Limites probatoires et risques résiduels

AC-08 constitue une **politique d'admission et de vérification SQLite locale**, pas la qualification de la récupération physique :
- `DELETE/FULL` est imposé/vérifié dans les chemins pris en charge ; cela ne garantit pas l'intégrité d'un disque, le comportement `fsync` d'un matériel ou la persistance après coupure.
- Les tests ne simulent ni crash interne COMMIT, ni coupure de courant, ni concurrence inter-hôtes. `st_dev` est un indice de topologie, pas une preuve de support local fiable ; une inspection des montages, supports réseau et chemins symboliques est à approfondir avant tout autre niveau de garantie.
- La vérification des PRAGMA est faite sur les connexions gérées ; elle ne contrôle pas un client SQLite indépendant altérant ultérieurement les fichiers. Les connexions déjà ouvertes hors de ce code ne sont pas rétroactivement qualifiées.
- Le refus lors des contrôles de configuration peut produire une exception Python non convertie en réponse HTTP normalisée : **AC-13** est **hors chantier** et reste à arbitrer séparément. Aucune réponse HTTP 503 n'est revendiquée.
- Une base préexistante incompatible demeure indisponible pour les mutations protégées ; aucune migration automatique n'est prévue.
- **Aucune validation de recette indépendante chat 03 réalisée ici.**

## 6. Verdict technique et décision attendue

**Correctif AC-08 implémenté et non-régression CI n°238 réussie dans le périmètre local fictif.** La réception indépendante du chat 03 et l'arbitrage 00 restent requis ; ce résultat ne clôt pas R1-C01, R1, R1-RD01 ni P0-01.

**Statuts :** AC-08 implémenté sur la branche et testé par CI, **non réceptionné indépendamment** ; AC-13 ouvert hors périmètre ; R1-C01 PARTIEL ; R1-RD01/R1/P0-01 OUVERTS ; B6.5 en recette ; G04, B6.3 et production NO-GO.

**Prochaine action unique :** présenter au chat 03 le commit technique `eb97c24e`, la CI n°238 et ce rapport pour recette indépendante AC-08.
