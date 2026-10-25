# SEC-01 R1-RD01 — C03-R04 — Purge des buffers mémoire C — Rapport de preuves
**Date :** 25 octobre 2026. **Branche :** `feature/b6-5-cartographie-interactive`.  
**Mandat :** `b65-http/DECISION-00-SEC01-RD01-C03-R04-PURGE-MEMOIRE-20261025.md`.  
**HEAD initial vérifié :** `0a74d57a0b1e39f921b1a7a6397eb6869b51ff76`.

## Périmètre du correctif

- `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` : ajout d'un effacement explicite byte à byte à travers un pointeur `volatile unsigned char*`, et d'une fonction `destroy_pair` qui efface jusqu'à la taille allouée de **1 Mio** par buffer, constate l'état nul **avant** `free`, remet les pointeurs à `NULL` puis invalide la taille. `c03_cleanup` libère les registres complets et est idempotent. `c03_test_reset` réutilise cette fonction. Le code d'allocation libère immédiatement le buffer survivant d'un échec partiel et conserve les marqueurs d'erreur et d'overflow. `c03_copy` refuse les buffers déjà détruits. Compteurs synthétiques de purge exposés sans publier de contenu brut.
- `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : `try/finally` englobant les opérations SQLite fictives, récupération et vérification du certificat ; nettoyage C systématique après la dernière utilisation des buffers et contrôle du bilan de purge. Sur rejet synthétique après copie, nettoyage également exécuté avant remontée de l'erreur. La destruction C intervient **après** `reciprocal_certificate`, et jamais dans `xClose`. Les champs `data` et `mask` du tableau Python sont remplacés par des chaînes d'octets vides avant retour ou exception.
- `b65-http/test_c03_r04.py` : cinq tests ciblés. L'essai complet remplit préalablement les deux buffers par des **octets non nuls** pour éviter de qualifier à tort un simple `calloc`. Les allocations partielles sont simulées exclusivement par un seam C de test, sans faute réelle du système d'exploitation.

**Commits techniques :** `d8d2773a0a1319f929b112016bc05941ad692bc7`, `e0be176d043d98a9ffdbee4089b1429c4885f918`, `046816ab635cbdd5e3ab0493f28102cbcfeffbce`, `7d556bf015753a6abc9f4b4e65b0ea22502e2766`, `76f140486b50b762244cb3da24145eb3df9141dd`, `2e3f8f09eccc857b5a4980e1d14eb9a6224d2360`.

**Exclusions tenues :** aucun changement du wrapper `atlas_rd01_vfs.c`, du moteur SQLite, des modules métier, de `_persistent_journey()`, du workflow, de G04 ou des callbacks causaux. Aucune nouvelle campagne C03-R05 ni opération de production.

## Validation fonctionnelle et mémoire

| Contrôle | Résultat CI n°199 | Limite |
|---|---|---|
| Deux allocations complètes, buffers fictifs remplis d'octets non nuls | PASS | Vérification dans le même processus avant `free` |
| Purge et vérification avant chaque `free` | PASS | Accès `volatile` qualifié pour le compilateur Linux utilisé, non preuve multi-plateforme |
| Allocation partielle, échec de `data` | PASS | Défaillance simulée, non défaut réel de `calloc` |
| Allocation partielle, échec de `present` | PASS | Même limite |
| Nettoyage après certificat COMMIT normal | PASS | Le certificat positif ne contient pas de buffers bruts |
| Nettoyage après rejet fictif après copie | PASS | Exception synthétique, chemin réel Python `finally` |
| Appel de nettoyage répété | PASS | Compteurs de libération inchangés au second nettoyage |
| Reset des enregistrements | PASS | Etat de registre vide |
| Copie depuis une entrée détruite | Refus vérifié | Pas de déréférencement d'une mémoire libérée |
| C03-R01, R02, R03 et certificat S↔A/B | Non-régression CI PASS | Profil fictif Linux SQLite 3.45.1 seulement |

**Mécanisme de purge :** les écritures via un pointeur `volatile` rendent leur omission par optimisation inappropriée sous le compilateur C11 du runner ; le code compare ensuite les octets à zéro avant `free` et maintient un compteur `wipe_failed`. Cela ne constitue ni une preuve matérielle universelle ni une attestation d'effacement de toutes les copies en mémoire.

**Portée des erreurs :** `record_open` conserve le défaut d'observation comme `overflow` ; une allocation partielle est détruite sans exposer un certificat positif. Le `finally` remet à zéro le registre expérimental même lorsqu'une vérification ou un décodeur échoue. En présence d'une erreur de nettoyage, le certificat est bloqué par l'exception Python.

**Limites restant ouvertes :** les buffers temporaires `ctypes` et les objets `bytes` Python restent susceptibles d'avoir des copies hors registre C, y compris après suppression de leurs références. La VFS native SQLite, les registres CPU, les dumps, le swap et les mécanismes d'allocateur ne sont pas purgés par ce correctif. Une vérification avant `free` ne garantit pas que le contenu ne puisse être récupéré d'aucun emplacement physique. Un crash avant le `finally` est hors mandat et non testé.

## CI et tests locaux

- **CI n°199** : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40238011587, sur le **commit exact testé** `2e3f8f09eccc857b5a4980e1d14eb9a6224d2360` ; `completed / success`.
- **116/116 JavaScript ; 11/11 SQLite ; 131/131 HTTP/identité/banc**, soit **258 exécutions réussies** ; ce nombre ne vaut pas 258 scénarios uniques.
- CI antérieures n°194 à 197 ont également été vertes sur leurs commits respectifs, mais n°199 est la référence intégrant le test des octets non nuls.
- **Tests locaux du commit exact : non exécutés dans cette conversation.** Ne pas assimiler les logs du runner GitHub à des contrôles locaux.

## Décision proposée à la recette

**Correctif C03-R04 réalisé sur le prototype C uniquement, non-régression constatée, réception indépendante chat 03 nécessaire.** La portée est la purge explicite et la libération sans double libération des allocations suivies. La confidentialité totale de la mémoire d'un processus ou la durabilité du stockage n'est **pas démontrée**.

C03-R04 **OUVERTE** dans l'attente de la décision 00 après PV 03 ; C03-R05 **OUVERTE**, campagne quantitative suspendue ; C03-R06 **OUVERTE** ; C03-R01 à R03 clôturées dans leur portée fictive ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G04, B6.3 et production NO-GO ; B6.5 en recette.

**Prochaine action unique :** remettre au chat 03 ce rapport et les journaux de la CI n°199 pour réception indépendante C03-R04.
