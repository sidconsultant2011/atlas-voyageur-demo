# Décision 00 — SEC-01 R1-RD01 — Réception technique du complément no_match pour recette indépendante

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `4a202997ca575da1e7fbf7349b596c361d1854a4`  
**Chantier prioritaire unique :** recette indépendante 03 du correctif de validation du certificat `no_match`.

## Sources et preuves contrôlées

- Mandat 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R02-NO-MATCH-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-C03-R02-NO-MATCH-CORRECTIF-PREUVES-20261025.md`.
- Comparaison GitHub `6c6aac6b92cc73f4941f52650ecbba5702dc76fa..4a202997ca575da1e7fbf7349b596c361d1854a4` : trois fichiers concernés : `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` modifié, `b65-http/test_c03_passive.py` modifié, rapport de preuves ajouté. Aucun changement C, wrapper de référence, métier ou workflow.
- Commit testé : `40f7bf89b54dbee4cc167663d279c4d99d6a8b3c`.
- CI n°163 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40227116667 — **completed / success**, sur le commit testé.
- Journal CI : **116/116 JavaScript, 11/11 SQLite, 113/113 HTTP/identité/banc**, soit **240 exécutions de tests réussies**, sans assimiler ce total à 240 scénarios uniques.
- Les trois tests ajoutés au commit testé sont `test_certificate_rejects_no_match_one_and_many` (`no_match=1` et `2` rejetés), `test_certificate_all_zero_is_accepted`, `test_certificate_keeps_other_rejections`. Tous `ok` dans la CI.
- `validate_deletion_attribution(deletion)` est appelé depuis `run()` avant émission du certificat et rejette toute valeur strictement positive parmi `ambiguous`, `no_match`, `native_errors`, `not_closed`.
- Le scénario fictif de COMMIT normal émet toujours `RECONSTRUIT_BANC_FICTIF`, quatre relations S↔A/B, `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}`, intégrité `ok/ok`, DELETE/DELETE, FULL/FULL, SQLite 3.45.1.
- Aucun test local du **commit complet testé** n'est déclaré. La preuve d'exécution du code de ce commit provient de la CI, non du contrôle local.

## Décision du 00

**RÉCEPTION TECHNIQUE DU LIVRABLE POUR RECETTE INDÉPENDANTE PAR LE CHAT 03**, sans clôture anticipée de C03-R02.

Le défaut ciblé de validation `no_match` a été corrigé dans le code inspecté et sur les cas synthétiques testés. Les rejets préexistants sont maintenus et le COMMIT normal fictif reste conforme. Le résultat est une **preuve candidate** destinée à la réception indépendante.

### Mandat unique de recette au chat 03

1. Contrôler au commit `40f7bf89b54dbee4cc167663d279c4d99d6a8b3c` le validateur `validate_deletion_attribution` et son appel dans `run()` avant émission du certificat.
2. Examiner les trois tests nouveaux et leurs assertions bloquantes : `no_match=1` et `2`, zéro anomalie, maintien de `ambiguous`, `native_errors`, `not_closed` ; distinguer injection d'un dictionnaire fictif et suppression OS réelle.
3. Vérifier dans les journaux CI n°163 le commit, les résultats 116/11/113, les trois tests individuels, la reconstruction S↔A/B, les six attributions, les PRAGMA DELETE/FULL et l'intégrité `ok/ok`.
4. Vérifier qu'aucun C, wrapper de référence, code métier ou workflow n'a été modifié et que les résultats CI ne sont pas déclarés comme tests locaux.
5. Prononcer un **PV indépendant, limité à la correction de la lacune `no_match`**, avec verdict GO/NO-GO, réserves résiduelles et avis sur la **clôture ciblée** de C03-R02 dans le seul périmètre du registre fictif. Une clôture ciblée ne vaudrait pas qualification générale d'identité physique, concurrence ou neutralité.
6. Remonter le PV au 00 pour décision ; le chat 03 n'autorise pas à lui seul la clôture P0 ni la mise en œuvre d'une autre réserve.

Aucune nouvelle modification ou exécution de tests par le 00. Aucune instrumentation `BEFORE_DELEGATE`, injection, SIGKILL, G04, modification du moteur, fusion main ni publication autorisée par cette décision.

## Statuts maintenus

**C03-R02 OUVERTE — correction livrée, en attente de PV 03**. C03-3 prototype reçu avec réserves, globalement ouvert ; C03-R01 et C03-R03 à R06 ouvertes ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global partiel ; R1-C01 partiel ; B6.5 en recette ; B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 03 le correctif, le rapport et la CI n°163 pour réception indépendante ciblée `no_match`, avant tout arbitrage du 00 sur C03-R02.
