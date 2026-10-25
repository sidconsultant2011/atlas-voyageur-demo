# SEC-01 R1-RD01 — C03-R02 — Correctif final de validation no_match

**Date :** 25 octobre 2026. **Mandat du 00 :** `b65-http/DECISION-00-SEC01-RD01-C03-R02-NO-MATCH-20261025.md`.  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`.  
**HEAD initial vérifié :** `6c6aac6b92cc73f4941f52650ecbba5702dc76fa`.

## Périmètre réalisé
- Commit **`6112e56060d0a83db54e5d3c61fce6b07145be3b`**, seul fichier `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : extraction de la validation réelle en fonction `validate_deletion_attribution(deletion)` et appel depuis `run()`, à la place de l'ancienne condition. La validation rejette tout compteur strictement positif parmi `ambiguous`, **`no_match`**, `native_errors` et `not_closed` en levant `AssertionError`, avant la construction et l'émission du certificat positif.
- Commit **`40f7bf89b54dbee4cc167663d279c4d99d6a8b3c`**, seul fichier `b65-http/test_c03_passive.py` : trois tests ajoutés appelant la **même fonction Python** que le `run()` réel. `test_certificate_rejects_no_match_one_and_many` vérifie les valeurs 1 et 2 en exception bloquante ; `test_certificate_all_zero_is_accepted` accepte quatre anomalies nulles ; `test_certificate_keeps_other_rejections` vérifie indépendamment les trois autres anomalies.
- **Aucun changement** dans `c03_vfs.c`, `attribute_delete()`, `atlas_rd01_vfs.c`, code applicatif, moteur SQLite ou workflow. Aucun `BEFORE_DELEGATE`, G04, SIGKILL ni injection.

## Condition de preuve
Le contrôle Python réel appelle désormais :
```python
validate_deletion_attribution(deletion)
```
et la fonction rejette :
```python
if any(deletion[name] > 0 for name in
       ("ambiguous", "no_match", "native_errors", "not_closed")):
    raise AssertionError(...)
```
Le comptage `no_match` provient toujours du helper C expérimental déjà réceptionné ; aucun code de retour natif SQLite n'a été modifié. Les tests de validation utilisent des dictionnaires fictifs synthétiques : ils attestent le **chemin Python** de validation, non une suppression OS sans correspondance effectivement provoquée.

## GitHub Actions exécutée et résultats
**CI n°163 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40227116667  
**Commit testé :** `40f7bf89b54dbee4cc167663d279c4d99d6a8b3c`.  
**GitHub :** `completed / success`.
- JavaScript : **116/116**.
- SQLite : **11/11**.
- HTTP/identité et banc : **113/113**, comprenant les trois nouveaux tests et les sept tests C03-R02 déjà présents.
- **240 exécutions réussies** au total ; ce chiffre n'est pas le nombre de scénarios uniques.
- `RD01 C03-3 PASSIVE CERTIFICATE` : `no_match=0`, `ambiguous=0`, `native_errors=0`, `not_closed=0`, six événements attribués sur six ; liens S→A/B, A→S et B→S rétablis ; `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`, SQLite **3.45.1** du runner.
- Tests locaux de ce commit : **non exécutés dans cette conversation**. CI et tests locaux doivent rester distincts.

## Risques résiduels, décision
**La lacune ciblée no_match est corrigée et ses rejets bloquants sont vérifiés sur CI.** Cela n'établit ni identité physique universelle de fichier, ni neutralité générale du prototype, ni preuve après panne. Le résultat est à présenter au chat 03 pour réception indépendante ; **C03-R02 reste OUVERTE** tant que le 00 n'a pas pris de décision après cette recette.

Autres réserves C03-R01 et C03-R03 à R06, G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 ouvertes ; G04, B6.3 et production NO-GO ; B6.5 en recette.

**Prochaine action unique :** soumettre le correctif `40f7bf89`, la CI n°163 et ce rapport au chat 03 pour la réception indépendante du rejet `no_match` uniquement.
