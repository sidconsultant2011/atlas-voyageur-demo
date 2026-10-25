# SEC-01 R1-RD01 — C03-R06 lot 1 — Cohérence comptable xDelete — Rapport de preuves

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**Décision autorisant le lot :** `b65-http/DECISION-00-SEC01-RD01-C03-R06-COHERENCE-XDELETE-20261025.md`  
**HEAD initial vérifié :** `60de0fd4dd57bb79c4be0bcb62c5680e1cac2095`.

## 1. Périmètre strict exécuté

**Unique changement de logique :** `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`, fonction `validate_deletion_attribution()`.

Le contrôle exige des champs `events`, `attributed`, `ambiguous`, `no_match`, `native_errors`, `not_closed`, chacun de type Python `int` exact et supérieur ou égal à zéro, en refusant `bool`, `float`, `str`, `None`, listes et autres types. Les champs obligatoires absents provoquent une `AssertionError` contrôlée, pas une exception brute `KeyError` ou `TypeError`.

Le contrôle établit obligatoirement :
```text
events == attributed + ambiguous + no_match + native_errors + not_closed
```

Une fois les champs et l'équation vérifiés, il conserve le rejet de tout compteur d'anomalie strictement positif et de `attributed != events`. Les six compteurs proviennent du collecteur C antérieur **inchangé**. L'appel existant `run() -> validate_deletion_attribution(deletion)` se situe toujours **avant** la création et l'émission du certificat positif. Aucun code de retour SQLite n'est transformé.

**Fichiers du lot :**
1. `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : validation renforcée.
2. `b65-http/test_c03_passive.py` : adaptation strictement nécessaire des anciennes fixtures C03-R02 à six champs.
3. `b65-http/test_c03_r06_accounting.py` : huit tests ciblés de cette première famille.
4. Le présent rapport documentaire.

**Hors périmètre et inchangés :** `c03_vfs.c`, `atlas_rd01_vfs.c`, SQLite, code métier, workflow, C03-R05, instrumentation causale, SIGKILL, G04, production. Aucun test de panne.

## 2. Traçabilité des commits

- **`c4e36eb52732dc38f7bf432c8adbb145fd44b990`** : introduction de la validation comptable stricte dans `c03_run.py`.
- **`033a3a711c81ee373223c6001bc8fd8de622b34f`** : adaptation des fixtures historiques à la comptabilité à six champs.
- **`262d79a8d16cab9831e11253617d7c564a4a46cd`** : huit tests unitaires ciblés C03-R06 ; **commit exact testé par la CI n°206**.

## 3. Critères falsifiables vérifiés

| Test | Attente | CI n°206 |
|---|---|---|
| `test_balanced_positive_certificate` | `events=attributed=6`, anomalies nulles : validateur accepte | PASS |
| `test_unattributed_event_with_zero_anomalies_rejected` | `events=6`, `attributed=5`, anomalies nulles : rejet | PASS |
| `test_overcount_rejected` | `attributed=7` avec `events=6` : rejet | PASS |
| `test_negative_counter_rejected` | valeur négative dans chacun des six champs : rejet | PASS |
| `test_missing_required_field_rejected_without_keyerror` | absence de chacun des six champs : rejet contrôlé | PASS |
| `test_invalid_type_rejected_without_typeerror` | `str`, `float`, `None`, `bool`, listes, dictionnaires et objet non-dictionnaire : rejet contrôlé | PASS |
| `test_accounted_positive_anomaly_still_blocks_certificate` | anomalie positive comptablement équilibrée dans chaque catégorie : rejet maintenu | PASS |
| `test_balanced_zero_event_empty_record` | tous compteurs à zéro : cohérence comptable seule acceptée | PASS |

**Limite du cas zéro événement :** le validateur contrôle uniquement les comptes ; une éventuelle obligation d'un événement positif ou d'une transaction avérée ne relève pas de cette correction. Le certificat global dispose de ses autres contrôles préexistants ; le présent test ne prétend pas les qualifier à nouveau.

## 4. Résultats GitHub Actions

**CI n°206 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40241390833  
**Commit testé :** `262d79a8d16cab9831e11253617d7c564a4a46cd`.  
**Résultat vérifié :** `completed / success`.

- JavaScript : **116/116**.
- SQLite : **11/11**.
- HTTP / identité / banc : **139/139**, comprenant huit nouveaux tests C03-R06.
- **266 exécutions de tests réussies**, certaines découvertes `unittest` pouvant compter les mêmes classes ; ne pas les présenter comme 266 scénarios uniques.

**CI intermédiaire n°204**, commit `c4e36eb52732dc38f7bf432c8adbb145fd44b990` : `completed/failure` avant adaptation des anciennes fixtures C03-R02 initialement dépourvues de `events` et `attributed`. Ce résultat n'est pas présenté comme un succès ; le correctif des fixtures figure dans le commit `033a3a71`.

**Tests locaux du commit exact : non exécutés dans cette conversation.** Les preuves d'exécution publiées sont celles des journaux GitHub Actions n°206, non des contrôles locaux.

## 5. Non-régression et portée exacte

Le certificat positif C03-3 du runner Linux SQLite **3.45.1** indique :
- `verdict=RECONSTRUIT_BANC_FICTIF` ;
- `S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true` ;
- `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}` ;
- `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]` ;
- `before_delegate_demonstrated=false`, `crash_recovery_demonstrated=false`, `physical_durability_demonstrated=false`.

La CI n°206 a aussi exécuté les tests antérieurs C03-R01, R02, R03 et R04 sans échec. Elle **ne qualifie pas** l'identité universelle des fichiers, la neutralité temporelle, la durabilité ni la concurrence générale.

**Réserves C03-R06 non traitées :** fragments mal formés, pointeurs corrompus, métadonnées de cycle de vie contradictoires. Une réussite de ce premier lot comptable ne permet aucune clôture globale de C03-R06 ou C03-3.

## 6. Verdict proposé à la recette indépendante 03

**Premier lot C03-R06 réalisé, test positif et rejets comptables vérifiés par CI ; proposition de réception ciblée favorable dans le périmètre fictif limité, sans clôture automatique.** La décision appartient au chat 00 après PV indépendant du chat 03.

**Statuts maintenus :** C03-R01 à R04 clôturées dans leurs périmètres fictifs ; C03-R05 ouverte, campagne quantitative suspendue ; C03-R06 ouverte ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G04, B6.3 et production NO-GO ; B6.5 en recette.

**Prochaine action unique :** soumettre au chat 03 ce rapport, le commit testé `262d79a8` et la CI n°206 pour réception indépendante du seul premier lot C03-R06.
