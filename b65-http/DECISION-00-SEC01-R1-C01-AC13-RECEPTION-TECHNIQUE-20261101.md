# 00 — SEC-01 R1-C01 — AC-13 — Réception technique pour recette indépendante

**Date :** 1er novembre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `8ddd7678c0d23ae7c8e53af4104d0c139042397d`

## Sources et contrôles effectués

- Décision autorisant AC-13 : `b65-http/DECISION-00-SEC01-R1-C01-AC13-GO-IMPLEMENTATION-20261027.md`.
- Cadrage : `b65-http/SEC01-R1-C01-AC13-CADRAGE-TECHNIQUE-20261027.md`.
- Comparaison entre le GO `2263214b0fff41adbc07d1e5dfb0f5aa0b39707d` et le commit testé `8ddd7678c0d23ae7c8e53af4104d0c139042397d` : **deux seuls fichiers** du périmètre, `b65-http/local_http_facade.py` modifié et `b65-http/test_sec01_ac13_http_errors.py` ajouté.
- `local_http_facade.py` : la frontière `protect_sqlite_http` intercepte `SQLitePreconditionError` et `sqlite3.Error` autour des méthodes `do_POST`, `do_GET`, `do_DELETE`. Elle s'abstient d'envoyer une seconde réponse lorsque la réponse initiale est déjà commencée.
- `test_sec01_ac13_http_errors.py` : sept fonctions de tests ciblés.
- **GitHub Actions n°247** : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/41342824300 ; vérifiée sur le SHA technique exact : `completed / success`, job `test` : `success`. Journaux consultés par le 00 : 116/116 JavaScript ; 11/11 SQLite ; 168/168 HTTP/identité/sécurité, dont 7 tests AC-13 individualisés et `ok`. **295 exécutions réussies**, sans assimiler 295 exécutions à 295 scénarios distincts.
- **CI n°246** : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/41342745930 ; conclusion GitHub `failure` confirmée. Le chat 01 attribue trois échecs de tests au mauvais point d'injection des exceptions de création ; le contrôle direct effectué ici confirme l'échec et la réussite ultérieure, sans prétendre avoir reproduit localement la cause.
- Les tests locaux du dépôt complet **n'ont pas été exécutés** au commit exact selon le rapport 01 ; aucun test local exécuté par le 00.
- Aucun changement de modules de transaction SQLite, pont, AC-08, workflow, C03 ou VFS n'est présent dans la comparaison.

## Résultat technique reçu

Dans les scénarios fictifs locaux testés, la façade traduit des exceptions SQLite en réponses HTTP 503 structurées :
- `SQLitePreconditionError` : code public `STORAGE_PRECONDITION_FAILED` ;
- `sqlite3.Error` : code public `STORAGE_UNAVAILABLE`.

Les tests couvrent les routes protégées, le refus de délégation lorsque l'autorisation échoue, la conservation des statuts métier normaux, le fonctionnement du mode mémoire, le traitement d'erreurs métier du pont et l'absence de réessai automatique dans les scénarios synthétiques. La gestion évite une nouvelle réponse si une réponse a déjà commencé.

En cas d'exception au moment de la mutation ou du COMMIT, la réponse d'indisponibilité **ne certifie ni réussite ni rollback**. La simulation d'exception Python n'est ni une panne SQLite native ni une preuve de durabilité matérielle ou de récupération après panne.

## Décision officielle du 00

**GO — RÉCEPTION TECHNIQUE CIBLÉE AC-13 POUR PASSAGE EN RECETTE INDÉPENDANTE AU CHAT 03.**

Le 00 constate le périmètre borné et les preuves de CI. **AC-13 reste non réceptionné indépendamment** ; aucune clôture du critère global R1-C01 ou de P0-01.

### Mandat de recette indépendante 03

1. Contrôler le HEAD et le commit testé `8ddd7678c0d23ae7c8e53af4104d0c139042397d`, ainsi que les deux fichiers modifiés au regard du GO.
2. Examiner le code de la frontière HTTP : classes d'exception attrapées, codes publics/statu 503, absence de détails sensibles, en-têtes existants, maintien des refus métier, prévention d'une seconde réponse.
3. Vérifier les sept tests AC-13 et les lignes correspondantes des journaux CI n°247, y compris le comportement sur exception de mutation/COMMIT synthétique, refus d'autorisation et absence de retry.
4. Contrôler l'historique de la CI n°246 en échec et la correction de tests, sans effacer l'incident.
5. Émettre un PV **favorable, favorable avec réserves ou défavorable**, avec limites et résultat propre à la recette. **Ne pas relancer automatiquement des tests ou une nouvelle CI** ; escalader toute anomalie nécessitant un changement de code ou un nouveau test.

### Limitations conservées

Aucune garantie d'atomicité récupérée en panne native, de durabilité physique, de résultat connu après COMMIT incertain, de réponse si une déconnexion intervient après envoi des en-têtes, ni de sûreté multi-hôtes. AC-08 demeure réceptionné avec réserves ; ses réserves sur les chemins et la concurrence avec `ATTACH` restent ouvertes. Les erreurs de programmation hors SQLite ne sont pas couvertes par AC-13.

## Statuts

- AC-13 : **implémenté, CI reçue, réception technique favorable pour recette 03 ; réception indépendante en attente**.
- AC-08 : **réceptionné avec réserves**.
- R1-C01 : **PARTIEL** ; R1-RD01, R1, P0-01 : **OUVERTS**.
- B6.5 : **EN RECETTE** ; B6.3, G04 et production : **NO-GO**.
- Aucun changement `main`, migration, publication, achat, déploiement, fournisseur réel, instrumentation VFS, SIGKILL, extension C03 ou nouveau chantier technique n'est autorisé.

## Prochaine action unique

Transmettre au chat 03 le présent mandat et les journaux CI n°247 pour la recette indépendante AC-13, sans nouveau développement ni campagne de panne.
