# Décision 00 — SEC-01 R1-RD01 — Réception indépendante du correctif d'assertions G03

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `867c0edbc6c94c77cc90f3afd4115b39650bf62b`  
**Chantier prioritaire unique :** réception indépendante du correctif de couverture G03.

## Mandat et preuves contrôlés par le 00

- Décision préalable : `b65-http/PV-03-SEC01-RD01-G03-PREPARATION-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-G03-CORRECTIF-ASSERTIONS-PREUVES-20261025.md`.
- GitHub Actions n°120 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40208301806 ; `completed / success` sur le commit `03986691d23f0044c5fcbe9c1ac2a169f0c938c6`.
- **116/116 JavaScript, 11/11 SQLite, 96/96 HTTP/identité et banc, soit 223 exécutions réussies** ; pas nécessairement autant de scénarios uniques.
- Comparaison depuis `514774d5de54e0c06f047ab190bf47f6537b709a` jusqu'au HEAD documentaire : uniquement `b65-http/test_rd01_vfs_step1.py` modifié et rapport de preuves ajouté. Aucun changement au wrapper C ni aux modules applicatifs.
- Le test `test_g01_g02_g05_prequalification` contient désormais deux assertions bloquantes explicites :
  `self.assertTrue(proof["G03"]["observations"]["candidate_open_observed"])` et `self.assertTrue(proof["G03"]["observations"]["candidate_delete_observed"])`.
- Les assertions `commit_internal_phase_proven=false` et `durability_proven=false` sont conservées. Aucun nom fixe du super-journal.
- Ligne de preuve `RD01 G03 NORMAL COMMIT TRACE` dans la CI n°120 : les deux observations sont `true`, candidat `sessions.sqlite-mj8DEF5F9A7` ouvert à la séquence 80 puis `xDelete` (retour 0) à la séquence 116 ; 128 événements observés. Correspondance toujours par basename et ordre, émission post-délégation.
- **Tests locaux du commit final : non exécutés par le chat 01.** Aucun nouveau test négatif artificiel, aucune injection ou SIGKILL.

## Arbitrage du 00

**Accepter la livraison technique du correctif de non-régression G03 pour transmission au chat 03 — Recette indépendante.**

L'ajout des deux assertions fait désormais échouer le test en cas de retour booléen faux pour une ouverture ou suppression de candidat super-journal, sous réserve de la sémantique réelle du code de production de la preuve. La CI réussie atteste le scénario positif, et non un essai négatif d'efficacité des assertions.

**Mission du chat 03 :** examiner le diff et les deux assertions, vérifier qu'elles sont bien bloquantes et que le banc émet les valeurs contrôlées, confronter la CI n°120 et son commit, signaler l'absence de scénario négatif artificiel et émettre un avis de réception limité à la couverture automatisée G03. Ne pas extrapoler à l'identité complète des fichiers, à la neutralité VFS ou à la durabilité.

**Aucune autorisation nouvelle pour modification du wrapper, instrumentation avant délégation, suspension, injection G04, arrêt pendant COMMIT, ajout de dépendance ou modification applicative.**

## Statuts et réserves

**G03 : préparation reçue avec réserves, contrôle d'assertions en recette 03 ; G04 NO-GO.** G01 recevable sur CI ciblée ; G02 recevable sur banc fictif ; G05 archivage de fichiers propres reçu, G05 global PARTIEL. **G03-R01 à R07, VFS-R01 à R05, RD01-R01 à R04 ouverts. R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

## Prochaine action unique

Transmettre au chat 03 le commit testé `03986691d23f0044c5fcbe9c1ac2a169f0c938c6`, le rapport et les journaux CI n°120 pour procès-verbal indépendant du seul correctif d'assertions G03.
