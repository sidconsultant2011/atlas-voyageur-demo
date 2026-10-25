# Décision 00 — SEC-01 R1-RD01 — Clôture ciblée C03-R02

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `47db7dc55fc11889295a1cac3df2071a8e808afb`  
**Autorité :** 00 — Pilotage et gouvernance.

## Sources vérifiées

- Mandat et réception technique précédents : `b65-http/DECISION-00-SEC01-RD01-C03-R02-NO-MATCH-RECEPTION-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-C03-R02-NO-MATCH-CORRECTIF-PREUVES-20261025.md`.
- Avis indépendant 03 reçu le 25 octobre 2026, intitulé `PV-03-SEC01-RD01-C03-R02-NO-MATCH-20261025` : GO de recette ciblée, recommandation de clôture limitée au registre fictif expérimental ; **cet avis a été transmis au 00 et n'était pas un fichier PV présent sur GitHub au moment de l'examen**.
- Commit testé GitHub : `40f7bf89b54dbee4cc167663d279c4d99d6a8b3c`.
- CI n°163 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40227116667 ; **completed/success**, sur le commit testé ; logs contrôlés : 116/116 JavaScript, 11/11 SQLite, 113/113 HTTP/identité/banc = **240 exécutions réussies**, pas nécessairement 240 scénarios distincts.
- Trois tests ciblés `test_certificate_rejects_no_match_one_and_many`, `test_certificate_all_zero_is_accepted`, `test_certificate_keeps_other_rejections` : tous réussis sur CI.
- `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : le `run()` réel appelle `validate_deletion_attribution(deletion)` ; la fonction lève `AssertionError` pour un compteur strictement positif parmi `ambiguous`, `no_match`, `native_errors`, `not_closed`, avant l'émission du certificat.
- Certificat CI : `RECONSTRUIT_BANC_FICTIF`, S→A/B et A/B→S, `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}` ; deux bases fictives intègres `ok/ok`, DELETE/DELETE, FULL/FULL, SQLite 3.45.1.
- Les tests négatifs du validateur Python sont **synthétiques** : ils n'injectent pas de suppressions OS sans correspondance. Pas de test local du commit exact rapporté.

## Décision du 00

**CLÔTURE CIBLÉE DE C03-R02 : GO, STRICTEMENT POUR LE REGISTRE FICTIF ET LES SCÉNARIOS EXPÉRIMENTAUX REÇUS.**

L'anomalie initiale — attribuer plusieurs incarnations suivies à un seul `xDelete` réussi — est corrigée par le mécanisme `attribute_delete()` réceptionné indépendamment dans le précédent PV, sans altérer le retour natif de SQLite. Le contrôle Python `no_match>0` est désormais bloquant, avec préservation des autres rejets et non-régression du COMMIT normal fictif.

**Portée exacte de la clôture :** une suppression est associée à au plus une incarnation parmi celles suivies par le registre expérimental ; les cas d'ambiguïté et d'absence de correspondance couverts sont rejetés probatoirement. Ce n'est **pas** une preuve d'identité physique universelle, de couverture des événements non observés, de concurrence multi-transaction, de neutralité temporelle ou de durabilité.

## Réserves maintenues et absence d'autorisations implicites

- **C03-3 global OUVERT**, prototype reçu avec réserves.
- **C03-R01 et C03-R03 à R06 OUVERTES** : incarnations et concurrence, fermeture, mémoire C, neutralité temporelle, couverture négative.
- **G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS** ; G03 préparation reçue avec réserves ; G05 global PARTIEL ; R1-C01 PARTIEL.
- **G04 NO-GO, B6.3 NO-GO, production NO-GO ; B6.5 EN RECETTE.**
- Aucune preuve `BEFORE_DELEGATE`, aucune interruption causale, récupération post-panne ou durabilité physique.
- Aucune modification C/Python, aucun nouveau test, aucune fusion main, aucun fournisseur réel ni déploiement autorisés par cette décision documentaire.

## Prochaine action unique

Confier au chat 02 un avis **documentaire uniquement** pour proposer une seule priorité parmi les réserves encore ouvertes de C03-3, sans ouvrir de réalisation technique avant nouvel arbitrage du 00.
