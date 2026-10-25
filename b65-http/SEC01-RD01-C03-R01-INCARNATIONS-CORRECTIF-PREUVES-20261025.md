# SEC-01 R1-RD01 — C03-R01 — Sélection des incarnations rollback — Rapport de preuves

**Date :** 25 octobre 2026. **Chantier unique :** C03-R01, validateur Python expérimental, banc SQLite fictif isolé.  
**Décision officielle :** `b65-http/DECISION-00-SEC01-RD01-C03-R01-INCARNATIONS-20261025.md`.  
**Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD initial vérifié :** `f44e45ce9fb572d7226bbb1615f2544b6c55c52b`.

## 1. Changement effectif
- `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`, commit `a38e1c4395f1644a95a69e1872b583da43eef959` : remplacement de `max(generation)` par vérification des références S→A/B et A/B→S depuis les buffers capturés et masques déjà disponibles.
- Pour chacun des deux chemins attendus, vérifier l'unicité de son occurrence complète dans S, rechercher les pointeurs vers S par identité de fichier, offsets, numéro de page, longueur, somme de contrôle et magie. **Une seule incarnation portant exactement un pointeur valide est admissible.** Zéro ou plusieurs : erreur bloquante.
- L'incarnation sélectionnée doit être fermée, marquée supprimée par le canal probatoire C03-R02 et antérieure à l'ouverture de S. Une incarnation postérieure du même chemin est rejetée comme remplacement sans continuité démontrable. La présence d'une incarnation historique complète et terminée **sans** pointeur vers S est tolérée. Aucune génération maximale n'est utilisée pour choisir un candidat.
- `b65-http/test_c03_passive.py`, commits `1f7ff049acc5290017cbb21192c0660579506fda` puis correctif de fixture `5bd4a0aec3c24a4ed2690d22af8885a63d72762d` : sept tests ciblés C03-R01 supplémentaires.
- **Aucun changement** aux fichiers `c03_vfs.c`, `atlas_rd01_vfs.c`, au moteur SQLite, à `_persistent_journey()`, au code métier ou au workflow.

## 2. Critères et tests bloquants
| Test ajouté | Attestation ou rejet attendu | CI n°170 |
|---|---|---|
| `test_r01_one_compatible_incarnation` | une seule A et une seule B admissibles | PASS |
| `test_r01_historical_incarnation_discriminated_by_references` | ancienne incarnation distincte du journal de la transaction, sans pointeur S, non sélectionnée | PASS |
| `test_r01_indistinguishable_compatible_incarnations_rejected` | deux incarnations référant S, rejet explicite | PASS |
| `test_r01_missing_participant_rejected` | journal absent, rejet | PASS |
| `test_r01_incompatible_reciprocal_reference_rejected` | lien A→S ou S→A altéré, rejet | PASS |
| `test_r01_recreated_or_replaced_without_continuity_rejected` | ouverture plus récente du même chemin sans preuve de continuité, rejet | PASS |
| `test_r01_incomplete_incarnation_rejected` | masque d'observation lacunaire sur le pointeur, rejet | PASS |

Les tests synthétiques sollicitent **la même fonction Python `reciprocal_certificate` que le scénario réel**. Les incarnations synthétiques ne sont pas des transactions natives concurrentes et ne prouvent pas l'identité physique des inodes.

## 3. Contrôles GitHub Actions et historique exact

**CI n°168** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231186623, commit `a38e1c4395f1644a95a69e1872b583da43eef959` : succès du validateur avec anciens tests. **Ne contient pas la nouvelle couverture ciblée.**

**CI n°169** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231220751, commit `1f7ff049acc5290017cbb21192c0660579506fda` : `completed/failure`. Les six autres scénarios C03-R01 ont passé ; `test_r01_incomplete_incarnation_rejected` a échoué parce que la fixture ajoutait les caractères littéraux `\\x00` au masque au lieu d'octets nuls. C'était une erreur de fixture, pas une preuve de réussite.

**CI n°170** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231306358, commit testé `5bd4a0aec3c24a4ed2690d22af8885a63d72762d` : `completed/success`.
- JavaScript : **116/116**.
- SQLite hors ligne : **11/11**.
- HTTP/identité/banc : **120/120**.
- **247 exécutions réussies**, sans assimiler ce total à 247 scénarios distincts.
- Les **sept tests C03-R01** ont tous réussi.
- Non-régression C03-3 réelle : `verdict=RECONSTRUIT_BANC_FICTIF` ; `S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true`, `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`, SQLite runner 3.45.1.
- Non-régression C03-R02 : `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}` ; les tests de rejet `no_match`, ambiguïté et erreurs C restent dans la suite.
- **Tests locaux du commit exact : non exécutés dans cette conversation.** Aucune exécution CI ne doit être présentée comme essai local.

## 4. Limites explicites
La VFS expérimentale expose déjà les chemins, incarnations ordinales, fermetures, suppressions et octets reçus au passage des journaux. La sélection Python peut établir une unicité **dans cet inventaire**, pas un identifiant natif de transaction SQLite ni une identité physique universelle.

Le test positif réel utilise un seul COMMIT final dans un banc isolé. La règle de rejet des incarnations nouvelles après le candidat est volontairement conservatrice : elle peut empêcher une validation plutôt que créer une attribution infondée. Elle n'établit pas une preuve générale de concurrence, de reconstruction après panne, de neutralité de l'observateur ni d'interception causale.

C03-R02 demeure **clôturée dans son périmètre expérimental** selon la décision 00 transmise ; ce changement ne rouvre pas cette réserve. Les autres réserves C03-R03 à C03-R06 ne sont pas traitées.

## 5. Verdict soumis au chat 03

**Correctif C03-R01 fonctionnel dans le banc fictif ciblé, avec sept vérifications bloquantes et non-régression positive sur la CI n°170. Proposition : réception indépendante favorable dans cette portée, sans clôture automatique de C03-R01.**

G03-R01, VFS-R01, R1-RD01, R1, P0-01 restent ouverts ; G04, B6.3 et production NO-GO ; B6.5 en recette.

**Prochaine action unique :** soumettre le commit `5bd4a0ae`, la CI n°170 et ce rapport au chat 03 pour recette indépendante sur C03-R01 uniquement.
