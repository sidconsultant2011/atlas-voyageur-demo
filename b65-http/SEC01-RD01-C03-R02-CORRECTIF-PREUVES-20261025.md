# SEC-01 R1-RD01 — C03-R02 — Correctif d'attribution univoque xDelete — Preuves

**Date :** 25 octobre 2026. **Chantier unique :** C03-R02 ; prototype C03-3 fictif isolé.  
**Branche :** `feature/b6-5-cartographie-interactive`.  
**Décision officielle :** `b65-http/DECISION-00-SEC01-RD01-C03-R02-CORRECTIF-20261025.md`.  
**HEAD de départ vérifié :** `ea4525e5606e40f3e30d6896e5a32230127d03da`.

## 1. Modifications bornées et commits

- `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c`, commit `de5bd4ec96e3e46d0c54cc7b7e094ee4393dda61` : suppression du marquage de **toutes** les incarnations par chemin ; ajout de `attribute_delete()` après le retour de la VFS mère. Retour SQLite préservé sans transformation. Comptages distincts des événements attribués, ambigus, sans correspondance, échoués et incarnations non fermées. Un candidat non supprimé, de chemin identique, fermé et unique peut être marqué ; en cas de zéro ou plusieurs candidats, **aucun marquage**. Le chemin et la génération ne sont pas présentés comme un identifiant physique universel.
- `b65-http/test_c03_r02.py`, commit `6b703db64abbac978bf2a2f23a1932eef53b3b22` : sept tests unitaires sur les véritables fonctions C d'attribution à l'aide de cas fictifs, sans suppression OS réelle. Le seam de test partage `attribute_delete()` avec le callback après délégation.
- `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`, commit `3bdc4a7bf06cc3fccbc75e3809fb2fcf41e24742` : lecture des compteurs d'attribution dans le scénario de COMMIT normal ; échec si ambiguïté, erreur native ou incarnation encore ouverte ; ajout du bilan au certificat synthétique.
- **Inchangés :** `atlas_rd01_vfs.c`, moteur SQLite, code métier, `_persistent_journey()`, workflow et autres réserves C03.

## 2. Règle probatoire et portée

`parent->xDelete()` s'exécute normalement, et son code retour est restitué tel quel. **Après** ce retour seulement, `attribute_delete()` détermine si exactement une incarnation déjà ouverte, non marquée supprimée et fermée est compatible avec le chemin. Dans le cas unique, et exclusivement lorsque le retour natif est `SQLITE_OK`, cette incarnation est marquée supprimée ; sinon, aucune ne l'est. Une ancienne incarnation du même chemin **non prouvée supprimée** reste compatible même si elle est fermée : la suppression est alors ambiguë et aucune incarnation n'est revendiquée.

Les cas `no_match`, `ambiguous`, `native_errors` et `not_closed` sont discriminés dans le canal de preuve. **Aucun de ces états ne remplace le code SQLite retourné par le parent.** Le journal d'observation et le helper de test n'introduisent pas de phase `BEFORE_DELEGATE`. Aucun arrêt, SIGKILL ou essai de panne.

**Limite importante :** la règle démontre l'unicité **parmi les incarnations observées par ce registre en mémoire** ; elle ne démontre pas l'identité matérielle du fichier supprimé, ni l'exhaustivité des ouvertures hors VFS, des changements de chemin, des opérations concurrentes non maîtrisées ou des réutilisations non observées. Une identité de chemin + génération ne suffit pas à garantir une identité d'inode. Ce sont des réserves résiduelles, pas des validations.

## 3. Tests ciblés exécutés dans CI n°157

| Test | Attente falsifiable | Résultat CI |
|---|---|---|
| `test_active_unique_closed_incarnation` | une attribution pour un candidat unique, code `SQLITE_OK` conservé | **PASS** |
| `test_reused_path_distinct_proven_lifecycle` | deux suppressions successives, chacune sur sa propre incarnation attestée, pas d'attribution croisée | **PASS** |
| `test_multiple_compatible_incarnations_must_remain_unattributed` | un `xDelete` réussi ne marque aucune des deux incarnations compatibles | **PASS** |
| `test_native_delete_error_never_marks_deleted` | `SQLITE_IOERR=10` retourné tel quel et aucune incarnation supprimée | **PASS** |
| `test_delete_without_open_is_non_attributable` | suppression native réussie, preuve sans correspondance, aucune attribution | **PASS** |
| `test_recreation_after_proven_deletion` | une nouvelle incarnation du même chemin n'hérite pas du marquage précédent ; nouvelle suppression distincte | **PASS** |
| `test_open_incarnation_not_claimed_proven` | une incarnation encore ouverte n'est pas attribuée par le système de preuve | **PASS** |

Les scénarios unitaires exploitent le seam de test C et simulent le code retour fourni à `attribute_delete`. Ils **ne simulent pas de panne** et ne sont pas des tests d'erreur OS réelle. Les chemins utilisés sont exclusivement fictifs.

## 4. Non-régression réelle C03-3

La même CI n°157 exécute le COMMIT normal du prototype original. Dans le certificat `RD01 C03-3 PASSIVE CERTIFICATE` :
- `verdict=RECONSTRUIT_BANC_FICTIF` ;
- `S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true` ;
- `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}` ;
- `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`, `mutations=[1,fake]` ;
- `same_sqlite_symbol=true`, moteur SQLite **3.45.1**, Linux ;
- `before_delegate_demonstrated=false`, `crash_recovery_demonstrated=false`, `physical_durability_demonstrated=false`.

L'unicité 6/6 vaut **pour cette exécution normale** et ne prétend pas démontrer toutes les conditions de concurrence et de réutilisation.

## 5. Résultats et références vérifiées

**GitHub Actions n°157**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40224448242  
**Commit testé :** `3bdc4a7bf06cc3fccbc75e3809fb2fcf41e24742`.  
**Statut :** `completed`, conclusion `success`.
- 116/116 JavaScript ;
- 11/11 SQLite ;
- 110/110 HTTP, identité et banc ;
- **237 exécutions de tests réussies**, pas nécessairement autant de scénarios distincts.

**Tests locaux du commit GitHub exact : NON EXÉCUTÉS.** Le conteneur local n'a pas pu résoudre `github.com` pour cloner le dépôt (`Could not resolve host: github.com`). Aucun résultat CI n'est comptabilisé comme test local. Les essais de synthèse C utilisent des retours natifs *fournis au helper*, ce que les noms de tests indiquent.

## 6. Verdict pour le chat 03

**Correctif C03-R02 réalisé et contrôlé sur CI dans le périmètre fictif isolé ; proposition de réception indépendante favorable avec réserves.**

La nouvelle règle interdit l'attribution de plusieurs incarnations par une seule suppression observée, protège contre le cas ambigu et conserve le code retour SQLite. Elle n'établit pas une identité OS universelle ni une garantie de neutralité, et la couverture n'est pas exhaustive en situation concurrente réelle.

**C03-R02 reste OUVERTE jusqu'à nouvelle décision du 00 après recette du chat 03.** C03-R01, C03-R03 à R06, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 restent ouvertes ; G04, B6.3 et production NO-GO ; B6.5 en recette. Aucune fusion `main`, aucune publication ni modification métier.

**Prochaine action unique :** remettre ce rapport, les trois commits et les journaux CI n°157 au chat 03 pour réception indépendante de C03-R02 seulement.
