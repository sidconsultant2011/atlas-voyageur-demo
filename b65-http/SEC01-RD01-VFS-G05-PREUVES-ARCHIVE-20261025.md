# SEC-01 R1-RD01 — Complément G05 — Rapport de preuves du chat 01
Date : 25 octobre 2026. Branche : `feature/b6-5-cartographie-interactive`.

## Référence de décision
Décision 00 et PV indépendant : `b65-http/PV-03-SEC01-RD01-VFS-ETAPE1-20261025.md`.
HEAD initial vérifié : `120245f7f93889e76ac02a5b7b1b2ac8310a461d`.
Mission unique : conservation durable de fichiers fictifs propres. Aucun SIGKILL, aucun essai de panne, aucune instrumentation G03/G04, aucune modification du code métier.

## Modifications
- `b65-http/rd01-vfs-step1/rd01_vfs_step1.py` : sortie contrôlée par variable `ATLAS_RD01_G05_OUTPUT` ; copie `capture_brute/` et `recuperation_travail/` hors répertoire temporaire, `manifest.json` (source GitHub, tailles, SHA-256, paramètres d'environnement et marqueurs explicites « sans panne »), `proof.json`, vérification à nouveau des empreintes.
- `.github/workflows/b65-calculateur-tests.yml` : variable pour répertoire de preuves du runner, publication via `actions/upload-artifact@v4`, nom lié au run, `retention-days: 14`, `if-no-files-found: error`.
- Commits : `27c94478ce9d60efc623e5b26c56b9cd75f02eb5` (premier ajout), `a4ebc131e42889ba82b985544f42a89f393396aa` (formatage), `89963ff1d28c57ccee55633a69b8f30659f62fb6` (workflow), `1071fbe3ce35ba5556e53c437acf928c730d9e0b` (correction de syntaxe du banc).
- CI n°107 : **échec** dû à une erreur de syntaxe dans la préparation de l'archive ; aucun artefact produit. Cette anomalie du banc est corrigée dans `1071fbe3` ; elle ne concerne pas le métier.

## Preuve CI finale
- GitHub Actions n°108 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40205084577
- Commit testé : `1071fbe3ce35ba5556e53c437acf928c730d9e0b`.
- Statut : `completed` ; conclusion : `success`.
- JavaScript : 116/116.
- SQLite : 11/11.
- HTTP et identité, comprenant le scénario VFS : 96/96.
- Total : 223 **exécutions** réussies, pas 223 scénarios uniques.
- Artefact : `atlas-rd01-g05-40205084577`, ID `12602679040`, 6 610 octets, archive ZIP téléchargeable : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40205084577/artifacts/12602679040
- SHA-256 du ZIP : `08e4847a3963e25e3533d306188f87bfc5649994e19823e743c5b1e46f02b5f5`. Valeur indiquée par l'action upload et retrouvée après téléchargement.
- Conservation CI paramétrée : 14 jours ; disponibilité ultérieure soumise à la politique de rétention GitHub.

## Contenu réellement récupéré et contre-expertisé
Le ZIP a été téléchargé après la réussite de la CI et ouvert **hors du runner**. Il contient exactement huit chemins :
```text
capture_brute/identities.sqlite
capture_brute/sessions.sqlite
capture_brute/vfs.tsv
recuperation_travail/identities.sqlite
recuperation_travail/sessions.sqlite
recuperation_travail/vfs.tsv
manifest.json
proof.json
```
Les six fichiers des deux arborescences ont été vérifiés individuellement en taille et SHA-256 par comparaison avec `manifest.json`. Six concordances sur six. Contrôle CRC du ZIP : aucune erreur.
Le manifeste contient les identifiants du commit et du run GitHub, les PRAGMA, les versions, les tailles et SHA-256 ainsi que `no_hot_journals=true` et `no_crash_recovery=true`.
Les bases sont exclusivement fictives. Aucun cookie, jeton réel, clé API ou donnée personnelle réelle n'est introduit.

## Portée exacte et réserves
**G05 — conservation de fichiers fictifs propres et artefact téléchargeable : démontrée pour cette CI et ce banc. G05 globale : PARTIELLE.**
- Aucun journal rollback chaud ou super-journal actif au moment de l'archivage (la transaction est commitée normalement).
- Aucun arrêt brutal, aucune récupération post-crash et aucun artefact pré-récupération *après panne*.
- Les traces VFS sont celles du banc fictif, pas une preuve d'instrumentation directe de `_persistent_journey()`.
- Le wrapper natif n'est pas certifié équivalent à la VFS standard (VFS-R01), et la trace n'est pas individuellement synchronisée (VFS-R03).
- Une politique de rétention de 14 jours ne constitue pas un archivage pérenne ; exporter sous gouvernance documentaire si une conservation plus longue est exigée.
- Le contrôle indépendant du chat 03 et la décision 00 demeurent requis.

## Décision proposée
Recevoir le **complément archivage G05** dans sa portée : publication, téléchargement, manifestes et intégrité reproductible d'un jeu de bases propres. **Ne pas lever G05 entièrement**, ni RD01-R01 à R04, ni VFS-R01 à R05, ni R1-RD01, R1 ou P0-01. B6.5 reste en recette, B6.3 NO-GO, production NO-GO.

**Prochaine action unique :** soumettre ce rapport et l'artefact CI n°108 au chat 03 pour réception indépendante de la conservation G05.
