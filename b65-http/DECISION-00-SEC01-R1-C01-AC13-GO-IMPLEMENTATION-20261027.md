# 00 — SEC-01 R1-C01 — GO d'implémentation ciblée AC-13

**Décision du 00 — 1er novembre 2026**  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `24cc77d1b9721ad76c20b07ceb15c81ae381ea47`

## Sources vérifiées

- Note de cadrage 01 : `b65-http/SEC01-R1-C01-AC13-CADRAGE-TECHNIQUE-20261027.md`, versionnée sur la branche au commit `24cc77d1b9721ad76c20b07ceb15c81ae381ea47`. Ce commit ajoute uniquement le document ; aucune implémentation ni test AC-13 avant cette décision.
- Mandat précédent : `b65-http/DECISION-00-SEC01-R1-C01-AC13-CADRAGE-20261027.md`.
- Contrat R1-C01 V1.1 : `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md`.
- AC-08 réceptionné dans le fictif local avec réserves : `b65-http/DECISION-00-SEC01-R1-C01-AC08-RECETTE-INDEPENDANTE-20261027.md`.

## Arbitrage

**GO — IMPLÉMENTATION ET TESTS CIBLÉS AC-13**, en unique chantier technique actif sur la branche autorisée.

**Contrat de réponse approuvé :**
- Exception `SQLitePreconditionError` -> **HTTP 503** avec `{"status":"unavailable","errors":[{"code":"STORAGE_PRECONDITION_FAILED"}]}`.
- Exception `sqlite3.Error` -> **HTTP 503** avec `{"status":"unavailable","errors":[{"code":"STORAGE_UNAVAILABLE"}]}`.
- Aucun chemin, SQL, cookie, jeton, CSRF, information personnelle ou `str(exc)` dans la réponse, les en-têtes ou les journaux.
- En cas d'erreur sur mutation ou COMMIT, ne pas retourner 200/201, `revoked:true`, `deleted:true`, `journeyId`, cookie de confirmation ou assertion de rollback/COMMIT. **L'issue transactionnelle peut rester inconnue.**
- Aucune autorisation accordée lorsque `state.check()` ou un contrôle d'identité échoue ; aucune mutation déléguée après exception d'autorisation.
- Aucun réessai automatique des mutations non idempotentes. Conserver 401/403/404/429, contrôles de requête, `Cache-Control:no-store`, CSP, CORS et comportement du `LocalState` en mémoire.

## Périmètre de réalisation

Seuls `b65-http/local_http_facade.py` et un fichier de tests dédié `b65-http/test_sec01_ac13_http_errors.py` sont autorisés. Implémenter **une frontière commune** ciblée pour `SQLitePreconditionError` et `sqlite3.Error` autour des méthodes `do_POST`, `do_GET`, `do_DELETE`, qui réutilise `fail()` ou `send_json()`, uniquement si une réponse n'a pas encore commencé. Ne pas intercepter `BaseException` ni camoufler les exceptions de programmation. Les erreurs de transmission après début de réponse ne doivent pas entraîner une deuxième réponse HTTP.

L'initialisation défaillante d'un état persistant reste une erreur de démarrage empêchant le service d'admettre du trafic ; ne pas simuler de réponse si le serveur n'écoute pas.

## Critères de tests falsifiables

- AC-08 refusé : 503 stable et sans fuite pour les routes persistantes, aucune opération protégée poursuivie.
- `sqlite3.OperationalError` à la vérification de session : aucun accès, aucune mutation, aucun succès métier, y compris GET et echo.
- Exception de révocation : aucun succès ou cookie de confirmation ; issue COMMIT non prétendue connue.
- Erreur simulée de mutation / sortie transactionnelle : pas de 200/201 ni de preuve de rollback inventée ; ne pas assimiler injection Python à panne native.
- `database is locked` ou I/O synthétique : 503 et zéro retry automatique.
- Conservation des refus 401/403/404/429, JSON et origines, des réponses normales, des en-têtes de protection et du mode mémoire.
- Non-régression des tests AC-08, R1, identité et B6.5 ; vérifier les résultats du workflow `.github/workflows/b65-calculateur-tests.yml` sur le **commit technique exact**.

Le chat 01 devra rapporter commandes et résultats locaux séparément des résultats CI, inclure l'éventuel historique d'échec/correction et les réserves d'exhaustivité. Un résultat d'CI historique n'est pas une preuve AC-13. La recette indépendante 03 suivra séparément toute réception technique.

## Interdictions

Aucun changement de `persistent_sessions.py`, `fictional_identities.py`, `local_identity_bridge.py`, `sqlite_ac08.py`, moteurs ou transaction SQLite, code C, VFS, workflow, C03, G04, `main`, site public, fournisseurs réels ni production. Pas d'injection de panne OS, SIGKILL, `BEFORE_DELEGATE`, test de durabilité physique, migration ou architecture distribuée. Tout élargissement doit revenir au 00.

## Statuts

- AC-13 : **GO d'implémentation ; non encore développé, testé ni validé par cette décision**.
- AC-08 : réceptionné avec réserves, inchangé.
- R1-C01 : PARTIEL ; R1-RD01, R1 et P0-01 : OUVERTS.
- B6.5 : EN RECETTE ; B6.3, G04 et production : NO-GO.

## Prochaine action unique

Transmettre au chat 01 le mandat de réalisation et tests ciblés AC-13, puis attendre le rapport de preuve sur commit exact pour réception technique par le 00.
