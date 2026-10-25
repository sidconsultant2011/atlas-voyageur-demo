# Décision 00 — SEC-01 R1-RD01 — Clôture ciblée C03-R04

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `c797a218f054b5f096adcd01013d6694bbea6868`  
**Autorité :** 00 — Pilotage et gouvernance.

## Sources et preuves

- Mandat technique : `b65-http/DECISION-00-SEC01-RD01-C03-R04-PURGE-MEMOIRE-20261025.md`.
- Décision de soumission en recette : `b65-http/DECISION-00-SEC01-RD01-C03-R04-RECEPTION-20261025.md`.
- Rapport de preuves 01 : `b65-http/SEC01-RD01-C03-R04-PURGE-MEMOIRE-CORRECTIF-PREUVES-20261025.md`.
- PV de recette indépendante 03, remis au 00 sous le titre `PV-03-SEC01-RD01-C03-R04-20261025` le 25 octobre 2026 : **réception favorable avec réserves**, recommandation de clôture ciblée. Sa présence comme fichier autonome du dépôt n'a pas été vérifiée.
- GitHub Actions n°199 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40238011587 ; `completed / success` au commit exact **`2e3f8f09eccc857b5a4980e1d14eb9a6224d2360`**.
- Logs CI contrôlés : **116/116 JavaScript**, **11/11 SQLite**, **131/131 HTTP/identité/banc**, soit **258 exécutions réussies** (ne signifient pas 258 scénarios distincts). Les cinq tests C03-R04 sont individuellement réussis.
- Inspection au commit testé : `c03_vfs.c` utilise `secure_wipe` à travers des écritures `volatile unsigned char*`, `destroy_pair` vérifie les octets avant chaque `free`, invalide les pointeurs et la taille ; `c03_cleanup` nettoie le registre ; le seam simule les allocations partielles. Les données non nulles dans le test de purge évitent de confondre `calloc` avec l'effacement.
- `c03_run.py` appelle le nettoyage C dans `finally`, après la certification ou son rejet, et vérifie les compteurs de purge. Remplacer les références Python par `b""` **n'est pas une preuve d'effacement physique** de leurs anciennes allocations.
- Certificat C03-3 fictif : `RECONSTRUIT_BANC_FICTIF`, liens S↔A/B, six suppressions attribuées sur six, intégrité `ok/ok`, DELETE/FULL ; les tests C03-R01, R02, R03 restent réussis.
- Le périmètre de développement comprend quatre fichiers : `c03_vfs.c`, `c03_run.py`, `test_c03_r04.py`, rapport de preuves ; wrapper de référence, application et workflow inchangés.
- Aucun nouveau test local du commit exact revendiqué par 01 ou 03 ; le 00 n'a pas exécuté de tests locaux ou CI.

## Décision explicite du 00

**GO — CLÔTURE CIBLÉE DE C03-R04.**

Le 00 accepte la réception indépendante favorable avec réserves. **La seule propriété clôturée** est le cycle de vie de purge et de libération des copies brutes `data` et `present` **suivies par le prototype expérimental C03** sur les chemins effectivement testés, y compris allocations partielles synthétiques, succès, rejet et nettoyage répété.

La technique `volatile` a été inspectée et testée dans l'environnement Linux C11 du runner ; **aucune garantie multi-plateforme universelle** ou contre toute optimisation/duplication mémoire n'est inférée.

### Réserves explicites

- Les tests de faute d'allocation sont **synthétiques** ; ils ne provoquent aucun échec matériel réel.
- La vérification de lecture après destruction démontre un rejet, mais ne distingue pas toujours la garde sur pointeur nul du refus d'index déjà invalidé.
- La réaffectation des références Python ne purge pas leurs anciennes copies ; les buffers `ctypes`, SQLite, CPU, mémoire allocateur, swap, caches et dumps demeurent hors périmètre.
- Un crash avant `finally`, la récupération après panne et l'effacement physique définitif ne sont pas qualifiés.
- Cette clôture ne rend pas admissibles les données personnelles réelles et ne constitue **ni clôture P0-01, ni GO G04 ou production**.

## Statuts après décision

- **C03-R01, C03-R02, C03-R03 et C03-R04 : CLÔTURÉES exclusivement dans leurs périmètres expérimentaux fictifs et bornés.**
- **C03-R05 : OUVERTE**, qualification quantitative et campagnes de mesures suspendues — budget B non justifiable à ce stade.
- **C03-R06 : OUVERTE**.
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 : OUVERTS.**
- **B6.5 : EN RECETTE ; G04, B6.3 et production : NO-GO.** G05 global et R1-C01 demeurent partiels selon les décisions antérieures.

Aucun changement technique, fournisseur réel, fusion main, mise en ligne ou déploiement autorisé par cette décision.

## Prochaine action unique

Demander au chat 02 un avis documentaire sur le périmètre et les critères falsifiables de **C03-R06**, seule réserve active non suspendue, avant tout nouveau mandat technique.
