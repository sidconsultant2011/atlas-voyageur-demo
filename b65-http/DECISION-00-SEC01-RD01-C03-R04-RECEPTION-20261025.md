# Décision 00 — SEC-01 R1-RD01 — Livraison technique C03-R04 pour recette indépendante

**Date :** 25 octobre 2026
**Branche autorisée :** `feature/b6-5-cartographie-interactive`
**HEAD vérifié avant décision :** `367f77c9d418452622403c2cbb303b15e0712c09`
**Chantier prioritaire unique :** recette indépendante de la purge des buffers C dans le prototype C03-3.

## Sources et vérifications GitHub

- Mandat 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R04-PURGE-MEMOIRE-20261025.md`.
- Rapport de développement : `b65-http/SEC01-RD01-C03-R04-PURGE-MEMOIRE-CORRECTIF-PREUVES-20261025.md`.
- GitHub compare `0a74d57a0b1e39f921b1a7a6397eb6869b51ff76..367f77c9d418452622403c2cbb303b15e0712c09` : **quatre fichiers** seulement ; `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` et `c03_run.py` modifiés ; `b65-http/test_c03_r04.py` et rapport ajoutés. Wrapper principal `atlas_rd01_vfs.c`, moteur SQLite, code métier et workflow inchangés.
- CI GitHub Actions n°199 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40238011587 ; `completed / success`, commit **testé exact `2e3f8f09eccc857b5a4980e1d14eb9a6224d2360`**.
- Journaux CI n°199 contrôlés : **116/116 JavaScript**, **11/11 SQLite**, **131/131 HTTP/identité/banc** = **258 exécutions réussies**, pas nécessairement 258 scénarios uniques.
- Les cinq tests `test_c03_r04` sont `ok` dans les journaux : allocation partielle des deux côtés, allocation complète suivie d'effacement d'octets non nuls, `reset` idempotent, certification positive puis purge, rejet puis purge.
- Code C au commit testé : `secure_wipe` écrit via `volatile unsigned char*`, `destroy_pair` vérifie zéro avant `free`, remet `data` et `present` à NULL, expose des compteurs de vérification et libération ; `c03_cleanup` est appelé depuis `c03_test_reset`. Les ressources en allocation partielle sont nettoyées, et `c03_copy` refuse un enregistrement détruit.
- Code Python au commit testé : `try/finally` autour de la certification réelle, effacement logique des références `data`/`mask` avant appel `c03_cleanup` et contrôle du bilan de purge. Cette réaffectation des objets Python n'atteste **pas** la destruction de leurs anciennes copies d'octets.
- Le certificat fictif normal de CI n°199 indique `RECONSTRUIT_BANC_FICTIF`, liens S↔A/B, six suppressions attribuées sur six, intégrité `ok/ok`, configuration DELETE/FULL, sans preuve de durabilité physique.
- Tests locaux du commit exact : **non exécutés selon le rapport 01**. Le chat 00 n'a pas lancé de test supplémentaire.

## Décision du 00

**LIVRAISON TECHNIQUE C03-R04 ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03. C03-R04 RESTE OUVERTE.**

La présence d'un mécanisme de purge mémoire C explicite et sa mise en oeuvre dans les chemins de certification sont corroborées par le code et la CI. La réussite de l'instrumentation de test ne prouve pas l'effacement universel de la mémoire et n'autorise aucun usage de données réelles.

### Mandat unique de recette indépendante au chat 03

1. Vérifier au commit exact la fonction `secure_wipe`, `destroy_pair` et `c03_cleanup`, leur ordre purge-vérification-`free`, les garanties réellement soutenues par `volatile` sur le compilateur de CI et les limites de portabilité/optimisation.
2. Vérifier les allocations complètes et les deux allocations partielles, la préservation des indicateurs d'échec, l'idempotence du cleanup, le refus de copie d'une entrée détruite, l'absence de double libération et la portée des compteurs `wipe_verified`, `wipe_failed`, `buffers_freed`.
3. Vérifier le `try/finally` Python et l'ordre entre extraction des copies, reconstruction du certificat, nettoyage après succès et nettoyage après rejet. Contrôler si tous les chemins pertinents déclenchent effectivement `c03_cleanup` et refusent une preuve positive en cas d'échec de purge.
4. Contrôler les cinq tests et leurs assertions bloquantes sur **des données non nulles** et les allocations partielles **simulées**, sans les présenter comme de vraies fautes d'allocation système.
5. Confronter les journaux CI n°199 au commit `2e3f8f09eccc857b5a4980e1d14eb9a6224d2360`, les totaux 116/11/131, et vérifier la non-régression C03-R01/R02/R03 ainsi que le certificat positif S↔A/B, DELETE/FULL et intégrité `ok/ok`.
6. Vérifier le périmètre du diff et les exclusions tenues ; **ne pas déduire de la remise à `b""` des objets Python une destruction physique de leurs anciennes allocations**, ni une protection des caches, swap, dumps, copies SQLite ou crash avant `finally`.
7. Produire **un procès-verbal indépendant** concluant sur la réception ou non de la purge ciblée et recommandant au 00 une éventuelle **clôture bornée** C03-R04. Aucune clôture automatique.

**Restrictions :** examen indépendant sans nouvelle modification ni test imposé ; aucun nouveau chantier C03-R06 ou C03-R05, pas de `BEFORE_DELEGATE`, SIGKILL, panne, G04, fusion main, fournisseur réel ni production.

## Statuts maintenus

**C03-R04 OUVERTE**, livraison en attente de PV 03 ; **C03-R05 OUVERTE, campagne quantitative suspendue** ; **C03-R06 OUVERTE** ; C03-R01/R02/R03 clôturées dans leurs seuls périmètres fictifs ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; B6.5 en recette ; G04, B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 03 le code/test au commit `2e3f8f09`, le rapport de preuves et les logs CI n°199 pour une recette indépendante exclusivement C03-R04.
