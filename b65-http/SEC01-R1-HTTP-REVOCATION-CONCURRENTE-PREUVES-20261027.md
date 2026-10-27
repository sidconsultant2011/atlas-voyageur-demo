# SEC-01 R1 — Qualification HTTP concurrente avec révocation — Preuves

**Date :** 27 octobre 2026. **Chantier unique :** concurrence HTTP/revocation dans le prototype fictif SQLite local.  
**Décision 00 :** `b65-http/DECISION-00-SEC01-R1-HTTP-REVOCATION-CONCURRENTE-20261027.md`.  
**Branche :** `feature/b6-5-cartographie-interactive`. **HEAD initial contrôlé :** `1e706e081093b04d56c010af6626723ed7aa80b2`.

## 1. Analyse de couverture et périmètre ajouté

Les tests existants `b65-http/test_sec01_r1_complements.py` étaient déjà présents et ont été lus : entrelacements directs SQL de création/mise à jour/suppression sous `BEGIN IMMEDIATE`, contention interprocessus, refus HTTP de toutes les mutations après révocation et rollback des bases attachées. Aucun de ces tests historiques n'a été refait sous un autre nom.

**Ajout unique :** `b65-http/test_sec01_r1_http_concurrent.py` au commit `880c7f9cbf324ea54cff85dbdaaeb02c50a0b460`. Deux tests HTTP de complément et un témoin de verrou SQLite indépendant. Aucun changement au métier, au wrapper C, au moteur SQLite, aux workflows, à C03 ou à G04.

Les tests réutilisent les fixtures de `R1Complements`, `PersistentSessionState`, `LocalIdentityBridge` et `create_server`. `BarrierState` est une **sous-classe réservée aux tests** : elle signale et retient temporairement les requêtes *après* acquisition de `BEGIN IMMEDIATE` par les méthodes existantes. Elle ne réécrit pas les commandes SQL, le `COMMIT` ni les codes retour. Son compteur signale l'entrée dans `state.check` pour les deux requêtes HTTP concurrentes. Cette observation supplémentaire limite l'inférence au banc de test : elle n'atteste pas que le serveur non instrumenté expose les mêmes barrières.

## 2. Scénario A — mutation HTTP engagée avant révocation

1. Un `POST /api/v1/qa/journeys` entre dans la transaction protégée `_persistent_journey` ; `_authorize` signale son passage après `BEGIN IMMEDIATE`.
2. Une autre connexion SQLite avec `timeout=0` tente `BEGIN IMMEDIATE` et reçoit effectivement `database is locked`. La session reste lisible comme `revoked=0`.
3. Un `POST /api/v1/qa/session/revoke` concurrent est initié ; il ne peut pas prendre le verrou d'écriture tant que la mutation le détient.
4. La barrière de la mutation est libérée. Le gestionnaire de contexte effectue son COMMIT, puis la révocation obtient son propre verrou et finit par son COMMIT.
5. Réponses finales : **mutation HTTP 201**, **révocation HTTP 200**. Relecture indépendante : `sessions.revoked=1` et ligne attendue de `identity_journeys` présente avec label fictif initial. Nouvelle création HTTP après révocation : **401**.

**Lecture probatoire :** l'ordre des COMMIT découle de l'exclusion réelle des écrivains et du programme transactionnel inspecté ; la CI n'enregistre **pas** d'événement natif autonome `COMMIT` avec horodatage à chaque fichier SQLite. Le test ne prétend pas prouver quel HTTP 201/200 est arrivé en premier au client, ce qui n'est pas la condition de sécurité.

## 3. Scénario B — révocation engagée avant deux mutations HTTP

1. Le `POST` de révocation atteint `_authorize` sous `BEGIN IMMEDIATE` ; le témoin SQLite indépendant confirme `database is locked`.
2. La relecture indépendante voit `revoked=0` et photographie l'état SQL de `identity_journeys`.
3. Deux connexions HTTP distinctes initient des `POST /api/v1/qa/journeys`. Le compteur de test signale qu'elles ont toutes deux atteint `state.check` avant la libération de la transaction de révocation. Le témoin SQLite confirme que le verrou est toujours détenu, et la relecture SQL ne montre aucune mutation nouvelle.
4. La barrière de révocation est libérée : **HTTP 200** puis deux résultats de mutations **HTTP 401**, sans nouvelle ligne `identity_journeys`.
5. Une nouvelle connexion HTTP tente une mutation après la confirmation de révocation : **HTTP 401**. La relecture finale conserve `revoked=1` et une base `identities` inchangée.

**Limite :** les signaux du compteur sont émis à l'entrée de `state.check` avant le `BEGIN IMMEDIATE` de chaque requête. Ils attestent les deux entrées HTTP dans la fonction protégée alors que la révocation tient effectivement le verrou, et non la date précise d'arrivée du paquet réseau. Les refus 401 sont, eux, des réponses HTTP réelles du banc.

## 4. Exécution et preuves

**GitHub Actions n°218 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40479880801  
**Commit testé exact :** `880c7f9cbf324ea54cff85dbdaaeb02c50a0b460`.  
**Conclusion :** `completed / success`.

- JavaScript : **116/116**.
- SQLite : **11/11**.
- HTTP/identité/sécurité : **153/153**, comprenant **deux nouveaux tests R1 HTTP concurrent**.
- **280 exécutions de tests réussies**, sans postuler 280 scénarios uniques.
- Tests locaux du commit exact : **non exécutés** ; seules les preuves de GitHub Actions sont revendiquées dans ce rapport.
- Aucun échec intermédiaire connu pour le commit de cet ajout.

## 5. Portée et conclusion

**Qualification HTTP concurrente ciblée favorable sur le banc fictif SQLite local testé.** Les deux nouveaux tests lient acquisition effective du verrou, HTTP, COMMIT déduit du modèle transactionnel inspecté et relecture indépendante des bases. L'état final ne révèle aucune mutation illégitime après la révocation dans ces entrelacements.

**Non démontré :** horodatage/sonde native des COMMIT, crash avant/après COMMIT, durabilité physique, atomicité de récupération inter-bases après panne, concurrence multi-hôtes ayant des bases indépendantes, réplication et production. Aucune clôture de R1-C01, R1, R1-RD01 ni P0-01 ne découle de cette CI.

**Statuts :** R1-C01 PARTIEL ; R1, R1-RD01 et P0-01 ouverts ; C03 extensions suspendues ; B6.5 en recette ; G04, B6.3 et production NO-GO.

**Prochaine action unique :** soumettre ce rapport, le commit testé et les journaux CI n°218 au chat 03 pour réception indépendante de la qualification R1 HTTP concurrente.
