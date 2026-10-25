# Décision 00 — SEC-01 R1-RD01 — Livraison technique C03-R01 pour recette indépendante

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `1185c93b33460dd130a3d613866c24737a7b71f3`  
**Chantier prioritaire unique :** réception indépendante de la sélection des incarnations C03-R01.

## Contrôles et preuves

- Mandat officiel du 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R01-INCARNATIONS-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-C03-R01-INCARNATIONS-CORRECTIF-PREUVES-20261025.md`.
- Comparaison GitHub `f44e45ce9fb572d7226bbb1615f2544b6c55c52b..1185c93b33460dd130a3d613866c24737a7b71f3` : trois fichiers dans le périmètre, `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` modifié, `b65-http/test_c03_passive.py` modifié et rapport ajouté. Aucun changement au code C expérimental, au wrapper de référence, à l'application ni au workflow.
- Commit testé `5bd4a0aec3c24a4ed2690d22af8885a63d72762d`.
- CI n°170 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231306358 : `completed/success`, sur le commit testé, **116/116 JavaScript, 11/11 SQLite, 120/120 HTTP/identité/banc, 247 exécutions réussies**, non nécessairement 247 scénarios distincts.
- Sept tests C03-R01 explicitement `ok` dans les logs : `test_r01_one_compatible_incarnation`, `test_r01_historical_incarnation_discriminated_by_references`, `test_r01_indistinguishable_compatible_incarnations_rejected`, `test_r01_missing_participant_rejected`, `test_r01_incompatible_reciprocal_reference_rejected`, `test_r01_recreated_or_replaced_without_continuity_rejected`, `test_r01_incomplete_incarnation_rejected`.
- Code inspecté : `reciprocal_certificate()` n'utilise plus `max(matches,key=generation)`. Il exige un pointeur valide vers S dans exactement une incarnation par journal participant, interdit les candidats multiples, les remplacements ultérieurs du chemin et les cycles incohérents.
- Certificat CI C03-3 `RECONSTRUIT_BANC_FICTIF` ; liens S→A/B et A/B→S, incarnations A4/B5/S6, `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}`, `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`, SQLite runner 3.45.1.
- **CI n°169** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231220751 : `completed/failure`, commit `1f7ff049acc5290017cbb21192c0660579506fda`. D'après le rapport 01, la fixture du test de masque incomplet employait des caractères littéraux incorrects ; correction au commit 5bd4a0ae, vérifiée par la CI n°170. L'échec historique n'est ni masqué ni requalifié en succès.
- Tests locaux du commit exact par le chat 01 : **non exécutés**. Le chat 00 n'a exécuté aucun test local ni CI.

## Décision du 00

**LIVRAISON TECHNIQUE C03-R01 ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03**, sans validation générale ni clôture anticipée.

La sélection probatoire d'incarnations est désormais fondée sur la cohérence des références réciproques et le cycle de vie déjà observé dans le banc fictif. Les scénarios négatifs prévus sont représentés par des jeux synthétiques de la même fonction Python que le COMMIT normal. Les preuves appuient la correction dans ce cadre seulement : pas de qualification de concurrence multi-transaction, d'identité inode, de neutralité temporelle ou de durabilité physique.

### Mandat unique au chat 03

1. Inspecter le diff du validateur `reciprocal_certificate()` au commit testé et vérifier que `max(generation)` ne joue plus de rôle de sélection, que zéro ou plusieurs incarnations compatibles sont rejetées et qu'une incarnation historique distincte est traitée correctement.
2. Contrôler les **sept tests C03-R01**, leurs assertions bloquantes, les fixtures de masques et leur raccord à la même fonction Python que le scénario réel ; distinguer cas synthétiques et exécutions SQLite.
3. Vérifier les journaux CI n°170 sur le commit exact, les 247 exécutions, les sept tests ciblés et les invariants C03-3/C03-R02 (références croisées, suppressions, `no_match`, intégrité, DELETE/FULL).
4. Examiner l'incident historique de CI n°169 et le correctif de fixture ; conserver explicitement son échec.
5. Préciser la portée de l'unicité des incarnations **dans le registre observé**, le caractère conservateur des rejets, les limites de concurrence et d'identité matérielle, et les réserves C03-R03 à R06 toujours ouvertes.
6. Produire un **PV indépendant** avec verdict GO/NO-GO limité à C03-R01, preuves, réserves et recommandation de clôture ciblée ou de maintien ouvert au 00. Aucune décision P0 ne découle automatiquement des tests.

**Interdictions :** le présent mandat est documentaire uniquement : aucune modification C/Python, aucun test nouveau, aucune instrumentation `BEFORE_DELEGATE`, aucune injection, SIGKILL, panne, G04, fusion main, changement du site public ni production.

## Statuts inchangés

**C03-R01 OUVERTE, livraison en attente de PV 03**. **C03-R02 clôturée dans son périmètre expérimental limité** ; C03-3 global ouvert, reçu avec réserves ; C03-R03 à R06 ouvertes ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G04 NO-GO ; G05 partiel ; R1-C01 partiel ; B6.5 en recette ; B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 03 ce mandat, le commit testé, le rapport du chat 01 et les journaux CI n°169/170 pour réception indépendante ciblée C03-R01.
