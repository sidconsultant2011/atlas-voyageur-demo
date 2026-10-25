# SEC-01 R1-RD01 — Correctif ciblé de couverture G03 — 25 octobre 2026

## Mandat
Décision 00 et PV indépendant : `b65-http/PV-03-SEC01-RD01-G03-PREPARATION-20261025.md`.
Branche : `feature/b6-5-cartographie-interactive`.
HEAD initial vérifié : `514774d5de54e0c06f047ab190bf47f6537b709a`.

## Correctif réel
Commit `03986691d23f0044c5fcbe9c1ac2a169f0c938c6` : modification **du seul fichier** `b65-http/test_rd01_vfs_step1.py`, ajout de deux assertions bloquantes :
```python
self.assertTrue(proof["G03"]["observations"]["candidate_open_observed"])
self.assertTrue(proof["G03"]["observations"]["candidate_delete_observed"])
```
Un booléen faux pour l'une ou l'autre observation fait échouer le test principal. Le nom du super-journal est dynamique, et aucune chaîne de nom fixe n'a été introduite. Les assertions `two_databases=true`, `commit_internal_phase_proven=false` et `durability_proven=false` sont conservées. Aucun changement au wrapper C, à l'analyseur G03, aux modules applicatifs, à la journalisation ou au workflow. Aucun test négatif artificiel supplémentaire ajouté (optionnel dans le mandat).

## Contrôles exécutés et preuves
**Tests locaux du commit : non exécutés** dans la présente conversation, absence d'exécution locale du dépôt identique au commit.

**GitHub Actions n°120 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40208301806
- Commit testé : `03986691d23f0044c5fcbe9c1ac2a169f0c938c6`.
- Statut `completed`, conclusion `success`.
- Tests JavaScript : 116/116 ; SQLite : 11/11 ; HTTP/identité et banc : 96/96 ; soit 223 **exécutions de tests** réussies, pas 223 scénarios uniques.
- Trace COMMIT normal fictif : `candidate_open_observed=true`, `candidate_delete_observed=true`, candidat ouvert en séquence 80, suppression corrélée `xDelete` (retour 0) en séquence 116. Basename variable `sessions.sqlite-mj8DEF5F9A7` pour **cette** exécution seulement.
- `commit_internal_phase_proven=false`, `durability_proven=false` restent attestés comme limites d'observation.

## Limites et réception
Les deux assertions bloquantes lèvent **uniquement la lacune de couverture** explicitement signalée par 03 : un retour `false` devient un échec de la CI. Il n'y a pas eu d'exécution instrumentée d'un scénario négatif supprimant artificiellement les événements ; le comportement d'échec découle du code d'assertion ajouté et reste disponible pour inspection indépendante.

Les signaux proviennent toujours d'un COMMIT normal, enregistrés post-délégation, avec corrélation par basename. Ne démontrent pas une interruption interne, un point d'arrêt causal, une atomicité en cas de crash ou une durabilité physique. G03-R01 à R07 et autres réserves conservées. Aucun SIGKILL, crash, injection, G04, fusion main, fournisseur réel ni publication.

**Statuts :** G03 préparation reçue avec réserves ; G04 NO-GO ; R1-RD01, R1 et P0-01 ouverts ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.

## Suite unique
Soumettre le commit `03986691`, ce rapport et les journaux GitHub Actions n°120 au chat 03 pour réception indépendante de **la correction de couverture uniquement**.
