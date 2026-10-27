# 00 — Réception technique pour recette indépendante — C03-R06 lot 2

**Date :** 27 octobre 2026  
**Dépôt :** `sidconsultant2011/atlas-voyageur-demo`  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `9b22d2e7ff41667b45153e73ab05fbc086a2a661`

## Objet et sources

Réception technique du seul lot 2 C03-R06, contrôle structurel des couples fictifs `data`/`mask`, pour transmission au chat 03 en vue de recette indépendante. Cette décision ne clôture aucun risque global.

- Mandat du 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R06-LOT2-STRUCTURE-FRAGMENTS-20261026.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-C03-R06-LOT2-STRUCTURE-FRAGMENTS-PREUVES-20261027.md`.
- Commit de code et tests **exécuté** en CI : `14df892f2d75b79f1c065794778e656a0091ac62`.
- CI **n°212**, ID `40476861479` : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40476861479 ; **completed/success**. Journaux CI lus par 00 : 116/116 JavaScript, 11/11 SQLite, 147/147 HTTP/identité/banc, soit 274 **exécutions de tests** réussies, pas nécessairement 274 scénarios distincts.
- Huit cas `test_c03_r06_fragments.py` individuels lus dans les journaux CI : chacun `ok`.
- Diff contrôlé entre le HEAD de mandat `504ebe3020ff8ef194688e85495fc9adad82f18a` et le HEAD documentaire `9b22d2e7ff41667b45153e73ab05fbc086a2a661` : seulement 3 fichiers : `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`, `b65-http/test_c03_r06_fragments.py` et rapport de preuves.
- Lecture du code au commit testé : `validate_fragment_structure(entry)` impose dictionnaire avec `data` et `mask` de type exact `bytes`, égalité de longueurs et marqueurs exclusivement 0 ou 1. `_observed_slice()` refuse les tranches vides, hors limites ou dont tous les marqueurs ne sont pas 1. `reciprocal_certificate()` et `_pointer_offsets()` utilisent ces contrôles.
- Certificat fictif normal observé dans la CI n°212 : six événements `xDelete`, six attributions, anomalie nulle, liens S↔A/B, intégrité `ok/ok`, DELETE/FULL ; les tests antérieurs restent réussis dans la suite.
- Tests locaux du commit exact : **non exécutés** selon le rapport 01. Le 00 n'a effectué aucun nouveau test ni modification de code.

## Décision formelle du 00

**GO DE RÉCEPTION TECHNIQUE DU LOT 2 C03-R06 POUR RECETTE INDÉPENDANTE 03**, exclusivement sur le profil expérimental fictif et le mécanisme de contrôle structurel des fragments. **C03-R06 reste OUVERTE.**

Ne pas assimiler la prévention de masques invalides à une preuve générale de fiabilité, d'absence de corruption de pointeurs, de neutralité temporelle, de durabilité ni de résistance aux pannes. La preuve d'un ancien certificat positif erroné n'a pas été apportée ; les défauts sont ceux des validations auparavant insuffisamment explicites.

### Mandat de recette indépendante au chat 03, et à lui seul

1. Relever le HEAD et vérifier le commit testé `14df892f2d75b79f1c065794778e656a0091ac62`, le rapport et le diff exact de trois fichiers.
2. Examiner `validate_fragment_structure()` : refus des types incompatibles, du manque d'un champ, des longueurs inégales et d'un marqueur autre que 0/1. Contrôler `_observed_slice()` et son appel effectif dans les chemins de reconstruction S↔A/B, y compris `_pointer_offsets()`.
3. Vérifier la portée et les assertions bloquantes des huit cas ciblés : témoin S/A/B, masque S tronqué, masque A tronqué, masque B surdimensionné, marqueur 0x02, mauvais type, appel direct au décodeur, tranche vide/hors limites/partiellement absente.
4. Lire la CI n°212 au commit exact et vérifier 116/11/147, huit réussites ciblées, certificat fictif normal et non-régression C03-R01 à R04 ainsi que C03-R06 lot 1.
5. Constater que le moteur SQLite, la VFS C, le wrapper de référence, le métier et le workflow sont inchangés.
6. Distinguer explicitement tests et assertions synthétiques, analyse statique, CI exécutée et absence de contrôle local. Émettre un **PV indépendant** avec réserves et avis sur réception **bornée au lot 2**, sans clôture globale.

**Interdictions :** pas de développement supplémentaire, CI nouvelle non requise, lot 3 non autorisé, aucune mesure C03-R05, aucune instrumentation `BEFORE_DELEGATE`, aucune injection, SIGKILL ou G04, et aucun usage de données réelles.

## Gouvernance, statuts et condition stratégique

- C03-R01 à R04 : clôturées seulement dans les périmètres expérimentaux fictifs reçus.
- C03-R05 : ouverte ; qualification quantitative suspendue car budget B non justifiable.
- C03-R06 : **ouverte**, lot 1 reçu, lot 2 soumis à recette 03.
- C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 : ouverts.
- B6.5 : en recette ; G04, B6.3 et production : NO-GO.

Après cette recette unique, **pas de poursuite mécanique des lots expérimentaux**. Une future campagne devra d'abord être justifiée par rapport à la finalité d'ATLAS VOYAGEUR et à l'exigence de sécurité P0-01, sous arbitrage explicite du 00. Les acquis techniques restent conservés.

## Prochaine action unique

Transmettre le rapport, le commit testé et la CI n°212 au chat 03 pour une **recette indépendante strictement limitée au lot 2 C03-R06**.
