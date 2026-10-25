# SEC-01 R1-RD01 — Rapport expérimental du chat 01 — 25 octobre 2026

## Décision, périmètre et versions
Décision 00 : `b65-http/DECISION-00-SEC01-R1-RD01-PROTOCOLE-20261025.md`, base GitHub `6183c5884f9830f904d66b1f97dd46fb96858934` ; branche `feature/b6-5-cartographie-interactive`.

Banc isolé ajouté sous `b65-http/rd01_crash_bench.py` (commit `22f6ee9dc9d1146ee0e97edf300cd6c07a54ebac`) et test `b65-http/test_rd01_crash_bench.py` (commit `0eef698b6643037f204f5111308ac7c1ba46ded3`). Corrections du banc : fermeture de canal stderr enfant `f73a00fa8794c788e6be622027de329dd16d0c7d` et trace détaillée de chaque cas en CI `5fdb7c2ce69b2aa3e5b9cb95d309d9d083aed7f4`.

**Aucun module applicatif existant modifié**. Aucune base réelle, aucun fournisseur, aucune panne OS, aucune coupure électrique. Seul le processus enfant créé par le banc reçoit SIGKILL.

## Préqualification
Plateforme GitHub Actions n°90 : Linux `6.17.0-1022-azure`, Python `3.12.3`, SQLite `3.45.1`. Deux fichiers temporaires SQLite sur le même périphérique (`st_dev` comparé), base principale sur disque, `journal_mode=DELETE` et `synchronous=FULL (2)` observés sur les deux bases. Version et options de compilation SQLite accessibles dans le rapport JSON du script. Le système de fichiers sous-jacent, les garanties matérielles de fsync et la résistance aux pannes OS ne sont **pas qualifiés**.

## Transaction témoin
Un enfant ouvre les deux bases avec `ATTACH DATABASE` puis exécute `BEGIN IMMEDIATE`, `UPDATE sessions SET revoked=1` dans la base principale et `INSERT INTO aux.journeys` dans la base attachée, suivis de `COMMIT`. Une marque de preuve, sur fichier séparé et synchronisée par fsync, est émise à chaque point *accessible depuis Python*. Le parent vérifie PID et marque, envoie `SIGKILL`, attend le code `-9`, puis réouvre les deux bases et vérifie `PRAGMA integrity_check` et les deux invariants métier.

L'instrumentation de preuve ajoute des opérations I/O et modifie l'ordonnancement ; elle ne prétend jamais sonder les sous-étapes internes SQLite COMMIT.

## Résultats CI attestés
**GitHub Actions n°90**, commit `5fdb7c2ce69b2aa3e5b9cb95d309d9d083aed7f4` : [journaux et étapes](https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40185721195), `completed/success`.

- JavaScript : 116/116.
- SQLite : 11/11.
- HTTP/identité : 95/95 exécutions dont le test `test_process_kill_attached_sqlite_recovery`.
- Total : 222 exécutions réussies (pas 222 scénarios uniques).
- Campagne expérimentale : 5 points instrumentés × 3 répétitions = **15 cas conformes / 15** ; traces individuelles `RD01 CASE` dans le journal n°90.

| Marque atteinte avant SIGKILL | Répétitions | État des deux fichiers après récupération |
|---|---:|---|
| `before_begin` | 3 | AVANT |
| `after_begin` | 3 | AVANT |
| `after_first_update` | 3 | AVANT |
| `after_second_update` | 3 | AVANT |
| `after_commit` | 3 | APRÈS |

Dans tous les cas, `integrity_check=['ok','ok']`, `journal_mode=['delete','delete']`, `synchronous=[2,2]`. Aucun état PARTIEL observé **dans cette campagne**.

Environnement local de développement distinct : Linux 6.18.55, SQLite 3.46.1 ; le prototype local du banc a donné 15/15, mais la version finale exacte publiée est vérifiée principalement par la CI n°90. Ne pas confondre les deux environnements.

## Matrice RD01-C01 à C08 : état technique, pas réception
- **C01** : OS, Python, SQLite, modes journal et synchronisation tracés ; système de fichiers et fsync physique non attestés.
- **C02** : transaction multi-fichiers explicitement dans le code du banc.
- **C03** : marque PID/phase synchronisée et SIGKILL confirmé sur 5 points *hors sous-étapes internes COMMIT* ; début/journalisation/synchronisation/finalisation internes non prouvés.
- **C04** : quinze états cohérents AVANT ou APRÈS, aucun partiel observé.
- **C05** : deux `integrity_check=ok` par cas, invariants SQL relus.
- **C06** : trois répétitions par point instrumenté, résultats identiques.
- **C07** : commits, scripts, référence CI et traces individuelles disponibles.
- **C08** : limites explicites ci-dessous.

## Réserves techniques, décision
Le protocole référence six fenêtres d'injection ; le banc teste cinq *marques externes* et ne saurait les assimiler toutes aux fenêtres internes demandées. **Interruption pendant COMMIT NON DÉMONTRÉE**. Pas de preuve de reprise après coupure électrique, crash OS, panne de stockage, stockage réseau ni WAL. Les fichiers temporaires ne sont pas conservés comme artefacts GitHub ; seuls les résultats structurés imprimés dans les logs CI et les scripts versionnés sont disponibles. Le banc ne qualifie pas toutes les implémentations et tous les dispositifs de stockage SQLite.

**R1-RD01 OUVERTE — R1 OUVERTE — P0-01 OUVERT — B6.5 EN RECETTE — production NO-GO.**

## Réception demandée au chat 03
Examiner le périmètre exact des cinq points, la preuve de SIGKILL et de récupération, les journaux de la CI n°90 et les limites d'instrumentation. Ne pas prononcer de clôture sans nouvel arbitrage du 00.
