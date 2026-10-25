# SEC-01 R1-RD01 — C03-R03 — Fiabilisation de xClose — Rapport de preuves
**Date :** 25 octobre 2026. **Branche :** `feature/b6-5-cartographie-interactive`.  
**Mandat :** `b65-http/DECISION-00-SEC01-RD01-C03-R03-XCLOSE-20261025.md`.  
**HEAD avant modification vérifié :** `eecd19fe20de899ba747fab3aab4bbfcb2ab310a`.

## Modification ciblée
- **`b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c`** — commit `5f7f3994e84783b660617bb636e4cdc79f7e6be3`. `cl()` appelle `xClose` natif, transmet le résultat exact à `record_close_result(slot,rc,known=1)`, puis libère le handle interne et restitue le même `rc`. Chaque entrée du registre distingue `close_called`, `close_known`, `close_rc`, `closed`. `closed=1` uniquement lorsque le résultat est connu et égal à `SQLITE_OK` ; sinon `closed=0` et `error=1`. Le helper `c03_test_close()` permet de fournir des retours synthétiques au **même** mécanisme, sans injection d'erreur OS.
- **`b65-http/rd01-vfs-step1/c03-passive/c03_run.py`** — commit `7cf392fce82ebdd36388e8b59e88da27d1b015e6`. Pour chaque entrée C03 réelle, collecte explicite `c03_close_info` avant certification. `validate_close_evidence` impose un succès connu et attesté ; toute entrée avec `closed=0`, `error=1`, `close_called!=1`, `close_known!=1` ou `close_rc!=SQLITE_OK` est rejetée. Les anciennes fixtures synthétiques sans métadonnées C03-R03 gardent leur contrôle `closed/error` pour préserver les tests antérieurs ; le chemin réel `run()` fournit systématiquement les nouveaux champs.
- **`b65-http/test_c03_r03.py`** — commit `cd2a8ddc874f95c931d683cd6b1afd79530f10ad`, puis correction de lecture du champ `closed` au bon index `c03_info` au commit **`63664ba669964c1427d5032cbf274d34b1b7a3dc`**. Cinq tests unitaires C03-R03 (dont trois sous-cas A, B et S).
- Aucun changement à `atlas_rd01_vfs.c`, au moteur SQLite, au code métier, à `_persistent_journey()` ou au workflow. Aucun `BEFORE_DELEGATE`, SIGKILL, injection, G04 ni essai de panne.

## Matrice de tests sur la logique réellement appelée
| Situation | Attendu | CI n°178 |
|---|---|---|
| `SQLITE_OK=0` transmis au helper natif | `closed=1`, `close_known=1`, résultat 0 | PASS |
| `SQLITE_IOERR=10` fictif fourni au helper | code 10 conservé, `closed=0`, `error=1` | PASS |
| retour inconnu fictif | `close_known=0`, `closed=0`, rejet | PASS |
| invocation absente | attestation positive refusée | PASS |
| échec sur journal A | rejet de `reciprocal_certificate()` | PASS |
| échec sur journal B | rejet de `reciprocal_certificate()` | PASS |
| échec sur super-journal S | rejet de `reciprocal_certificate()` | PASS |

**Ces tests contrôlent la logique C utilisée après le callback réel, avec des codes simulés. Ils ne constituent pas la preuve d'une erreur de fermeture OS réelle.** Le test de certificat A/B/S emploie des fixtures fictives et le même validateur Python que le COMMIT normal.

## GitHub Actions — historique exact
- **CI n°177**, commit `cd2a8ddc874f95c931d683cd6b1afd79530f10ad`, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232703728 : **completed/failure**. Défaut de fixture : le test lisait l'index 3 (`deleted`) au lieu de l'index 2 (`closed`) dans `c03_info`. Les rejets C03-R03 et la reconstruction normale avaient réussi.
- **CI n°178**, commit testé exact **`63664ba669964c1427d5032cbf274d34b1b7a3dc`**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232772919 : **completed/success**.
- JavaScript : **116/116** ; SQLite : **11/11** ; HTTP/identité/banc : **125/125**, dont les cinq tests ciblés C03-R03 ; **252 exécutions réussies** au total, sans inférer autant de scénarios distincts.
- Le certificat normal issu de la CI n°178 indique `verdict=RECONSTRUIT_BANC_FICTIF`, `S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true`, `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`, `same_sqlite_symbol=true`, SQLite runner **3.45.1**. Les compteurs C03-R02 sont `events=6`, `attributed=6`, autres anomalies à zéro.
- **Tests locaux du commit exact : non exécutés dans cette conversation.** Aucun résultat local ne se déduit de la CI.

## Limites et statuts
La preuve consiste en un suivi plus fiable du code retour `xClose` rapporté par la VFS native. `SQLITE_OK` ne prouve ni persistance physique, ni identité inode universelle, ni neutralité temporelle. Les tests d'échec s'appuient sur un seam fictif et non une faute matérielle. L'expérimentation ne couvre pas la récupération après panne.

**Proposition à la recette 03 : recevoir le correctif C03-R03 dans le périmètre expérimental testé**, sans clôture automatique par le chat 01.

**C03-R03 ouverte**, C03-R01 et C03-R02 clôturées dans leur périmètre expérimental ; C03-R04 à R06 ouvertes ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 ouverts ; G04 NO-GO, B6.5 en recette, B6.3 et production NO-GO.

**Prochaine action unique :** soumettre ce rapport et le commit testé `63664ba` avec la CI n°178 au chat 03 pour réception indépendante C03-R03.
