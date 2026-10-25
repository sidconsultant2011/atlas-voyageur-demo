# Décision 00 — SEC-01 R1-RD01 — Livraison du prototype C03-3 à la recette indépendante

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD GitHub vérifié avant décision :** `b87314acb29b1cff3292f73ba769475961d958d6`  
**Chantier prioritaire unique :** réception indépendante du prototype isolé de collecte passive C03-3.

## Périmètre et sources contrôlés

- Mandat 00 : `b65-http/DECISION-00-SEC01-RD01-C03-3-PROTOTYPE-ISOLE-20261025.md`.
- Rapport 01 : `b65-http/SEC01-RD01-C03-3-PROTOTYPE-PREUVES-20261025.md`.
- Fichiers nouveaux : `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c`, `c03_run.py` et `b65-http/test_c03_passive.py`.
- Comparaison GitHub `cdd802cfec8419472716983be401b0ece57c54c6..b87314acb29b1cff3292f73ba769475961d958d6` : **quatre fichiers ajoutés seulement**, sans modification du wrapper de référence C, du code métier ni du workflow.
- GitHub Actions n°150 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40218478132 ; **completed / success**, commit testé `3a1c004257f292c6b5cc2c12321a80228a4e8720`.
- CI : **116/116 JavaScript, 11/11 SQLite, 103/103 HTTP/identité/banc, soit 230 exécutions** (pas nécessairement 230 scénarios distincts).
- Journal CI `RD01 C03-3 PASSIVE CERTIFICATE` : `verdict=RECONSTRUIT_BANC_FICTIF`, `links.S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true`, `same_sqlite_symbol=true`, moteur SQLite **3.45.1**, `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`.
- Provenance CI : super-journal génération 6, 2 écritures, suppression attestée après COMMIT normal ; A génération 4, 13 écritures et pointeur offset 9216 ; B génération 5, 16 écritures et pointeur offset 13312 ; offsets des noms de journaux dans S : 0 et 56 ; 6 incarnations de journaux observées.
- Cinq tests C03-3 réussis : `test_normal_commit_real_sqlite`, `test_accept_complete_synthetic_fragments`, `test_reject_missing_reference`, `test_reject_incomplete_fragment`, `test_reject_ambiguous_super`.
- Contrôle local de préparation mentionné par 01 : Linux SQLite **3.46.1** ; ce contrôle **ne correspond pas au commit final**. Résultats du commit final appuyés par la CI SQLite 3.45.1.

## Décision du 00

**LIVRAISON TECHNIQUE ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03.** Le résultat expérimental est recevable comme **preuve candidate**, non comme validation définitive ni clôture C03-3.

Le certificat indique la reconstruction des références réciproques **S→{A,B}, A→S, B→S** sur un COMMIT normal, deux bases fictives attachées, wrapper expérimental distinct et runtime Linux CI. Les erreurs sur références absentes, fragments incomplets et super-journaux concurrents sont rejetées dans les tests synthétiques. Les cas négatifs ne sont pas exhaustifs.

Le certificat signale `raw_buffers_published=false`, sans prouver une purge systématique de la mémoire brute ; le rapport précise que la mémoire C n'est pas explicitement nettoyée.

**LIMITES** : pas de mesure comparative de neutralité temporelle N/W/prototype, pas de parité événementielle de la VFS native, pas de `BEFORE_DELEGATE`, pas d'arrêt causal, pas de panne, pas de durabilité physique, pas de qualification `_persistent_journey()`, pas de couverture générale des collisions/incarnations concurrentes.

## Mandat de réception indépendante au chat 03

Vérifier :
1. Le code du wrapper expérimental `c03_vfs.c` et le décodeur `c03_run.py` sur le commit testé ; isolation du wrapper d'origine, couverture des seuls journaux fictifs, limites mémoire, gestion des identités, appels VFS délégués, états de `xWrite`, `xTruncate`, `xClose`, `xDelete`.
2. Les assertions de `test_c03_passive.py`, leur caractère bloquant et leur correspondance aux **cinq** tests de la CI n°150, y compris cas négatifs.
3. La preuve effective du décodage réciproque des quatre liens, les incarnations, les offsets, le contexte des deux mutations, et les critères de rejet des cas ambigus.
4. La cohérence des résultats SQL, de l'intégrité, des paramètres DELETE/FULL, du moteur et de la séparation des preuves locales et CI.
5. Les limites de neutralité, de mémoire C non purgée, de couverture négative et de traçabilité ; ne pas convertir `raw_buffers_published=false` en garantie générale de confidentialité.
6. Rendre un **PV indépendant avec verdict limité, preuves, réserves et avis à soumettre au 00**, sans test ou modification exigés.

**Aucune modification C/Python/métier, aucune instrumentation `BEFORE_DELEGATE`, aucune panne, aucun SIGKILL et aucun G04 autorisés par le présent mandat.**

## Statuts maintenus

**C03-3, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS** ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.

## Prochaine action unique

Transmettre au chat 03 le code, les preuves et la CI n°150 pour réception indépendante du prototype C03-3 avant nouvel arbitrage.
