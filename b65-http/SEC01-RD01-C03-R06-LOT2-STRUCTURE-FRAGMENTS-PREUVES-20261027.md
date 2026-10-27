# SEC-01 R1-RD01 — C03-R06 lot 2 — Intégrité structurelle des fragments — Rapport de preuves

**Date du rapport :** 27 octobre 2026. **Mandat 00 :** décision datée du 26 octobre 2026, `b65-http/DECISION-00-SEC01-RD01-C03-R06-LOT2-STRUCTURE-FRAGMENTS-20261026.md`.

**Branche autorisée :** `feature/b6-5-cartographie-interactive`. **HEAD initial vérifié :** `504ebe3020ff8ef194688e85495fc9adad82f18a`.

## Résultat technique du lot

Le changement est limité au validateur Python `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`.

La fonction partagée `validate_fragment_structure(entry)` exige :
1. un dictionnaire d'entrée et des champs `data` et `mask` présents, de type exact `bytes` ; aucun cast implicite ;
2. `len(data) == len(mask)` ;
3. exclusivement des marqueurs `0x00` et `0x01`.

Une fonction partagée `_observed_slice(data,mask,start,end)` exige `0 <= start < end <= len(data)` et que chaque octet requis du masque soit exactement `1`. Les deux points d'entrée `reciprocal_certificate()` et `_pointer_offsets()` contrôlent les couples binaires avant leur interprétation. Les lectures de pointeurs et les références S→A/B utilisent la vérification bornée. Les erreurs structurelles sont levées par `AssertionError` contrôlée avant la construction du certificat positif.

**Interdictions tenues :** aucune modification de `c03_vfs.c`, du wrapper de référence, du moteur SQLite, du code métier ou du workflow. Aucune nouvelle mesure C03-R05, instrumentation `BEFORE_DELEGATE`, injection, SIGKILL ou G04.

## Commits et fichiers modifiés

- **`71c82fbf9b6a4ebf4103321a5375c859493c91f1`** : correctif Python `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`.
- **`14df892f2d75b79f1c065794778e656a0091ac62`** : huit tests ciblés dans le nouveau fichier `b65-http/test_c03_r06_fragments.py`. **Commit exact vérifié par GitHub Actions n°212.**
- Présent rapport : uniquement documentaire.

Les fixtures historiques de `test_c03_passive.py`, les tests C03-R01 à R04 et ceux du lot 1 C03-R06 n'ont pas été modifiés.

## Matrice de tests du lot 2

| Test exécuté | Preuve ou rejet requis | CI n°212 |
|---|---|---|
| `test_valid_S_A_B_control` | trois fichiers fictifs valides et références croisées acceptées | PASS |
| `test_truncated_S_mask_even_all_remaining_one` | masque S plus court bien que tous ses marqueurs valent 1 : rejet | PASS |
| `test_truncated_A_mask_in_pointer_region` | masque du journal A tronqué au niveau du pointeur : rejet | PASS |
| `test_oversized_B_mask` | masque B plus long que les données : rejet | PASS |
| `test_nonbinary_0x02_marker` | marqueur 2 injecté tour à tour dans S, A et B : rejet | PASS |
| `test_incompatible_data_and_mask_types` | texte, liste, `bytearray`, `None` : rejet contrôlé | PASS |
| `test_direct_pointer_decoder_rejects_invalid_pair` | décodeur de pointeurs appelé avec une structure incohérente : rejet | PASS |
| `test_empty_or_out_of_bounds_slice_never_qualifies` | tranche vide, début négatif, dépassement et trou de présence : rejet | PASS |

Les tests synthétiques utilisent `fictional_entries()` et la véritable fonction de certification Python. Ils ne falsifient ni les retours SQLite ni des fichiers sur disque. Le défaut antérieur était attesté par lecture du code (absence de contrôle systématique des longueurs et des marqueurs), **pas par observation d'un faux certificat positif réel**. Aucun faux certificat antérieur n'est revendiqué.

## GitHub Actions et non-régression

**CI n°212 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40476861479  
**Commit testé :** `14df892f2d75b79f1c065794778e656a0091ac62` ; **résultat : `completed/success`**.

- JavaScript : **116/116**.
- SQLite : **11/11**.
- HTTP/identité/banc : **147/147**, dont huit tests C03-R06 lot 2.
- **274 exécutions réussies** au total, non assimilables à 274 scénarios distincts.

Les suites préexistantes C03-R01, R02, R03, R04, le lot 1 C03-R06 et le scénario réel fictif `RECONSTRUIT_BANC_FICTIF` sont inclus dans la CI réussie. Celle-ci conserve la reconstruction S→{A,B}, A→S et B→S, les six événements de suppression attribués sans anomalie, les contrôles SQLite `integrity_check=ok/ok`, `journal_mode=DELETE` et `synchronous=FULL`. Ceci ne constitue pas une extension de leur portée de validation.

**Tests locaux du commit exact : non exécutés.** La vérification des tests effectuée ici résulte de la CI GitHub et de ses journaux, pas d'une campagne locale. La CI n°211 était déjà réussie sur le commit Python seul, mais ne contenait pas les huit nouveaux tests ; la référence complète est **n°212**.

## Limites et conclusion

**Conclusion technique :** validation structurelle des fragments renforcée et tests ciblés réussis sur le profil fictif testé. Le correctif ne réinterprète pas les contenus internes des pointeurs ni les générations, ne démontre pas la résistance à toutes les corruptions ni une neutralité temporelle, et ne change aucune garantie de production.

**C03-R06 reste ouverte** ; le lot 2 est proposé à la recette indépendante du chat 03 uniquement. Les familles « contenu du pointeur altéré » et « métadonnées contradictoires » restent hors de ce lot, à arbitrer par le 00.

**Statuts :** C03-R01 à R04 clôturées dans leur périmètre expérimental ; C03-R05 ouverte, campagne quantitative suspendue ; C03-R06 et C03-3 globale ouvertes ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 ouverts ; G04, B6.3 et production NO-GO ; B6.5 en recette.

**Prochaine action unique :** remettre ce rapport, le commit `14df892f` et la CI n°212 au chat 03 pour réception indépendante du seul lot 2 C03-R06.
