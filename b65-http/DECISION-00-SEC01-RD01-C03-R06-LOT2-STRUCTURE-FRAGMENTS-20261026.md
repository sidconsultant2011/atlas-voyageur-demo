# Décision 00 — SEC-01 R1-RD01 — C03-R06 lot 2 : intégrité structurelle des fragments

**Date :** 26 octobre 2026  
**Branche de travail autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `1e0120e398da60158dc6b950409ef32002d39362`  
**Priorité technique unique :** C03-R06 lot 2 — structure des couples `data` et `mask` du prototype fictif.

## Références consultées et constat

- Décision de réception du lot 1 : `b65-http/DECISION-00-SEC01-RD01-C03-R06-LOT1-RECETTE-20261026.md` : lot de comptabilité `xDelete` reçu, **C03-R06 globale ouverte**.
- Avis documentaire du chat 02, daté du 26 octobre 2026 : priorité exclusive recommandée aux masques des fragments de preuve ; aucune modification ni nouveau test exécuté par 02.
- Code sur HEAD : `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`. `reciprocal_certificate()` contrôle `all(s["mask"])` sans validation préalable de `len(data)==len(mask)` ; `_pointer_offsets()` utilise `all(mask[start:end])` sans vérifier préalablement les longueurs et le domaine binaire des valeurs. Une valeur `0x02` est non nulle pour `all()`. Ceci est une lacune de validation explicite, **pas une preuve d'un certificat faux positif effectivement observé**.
- Tests examinés : `b65-http/test_c03_passive.py` avec `test_reject_incomplete_fragment` et `test_r01_incomplete_incarnation_rejected` couvrant des absences de présence via zéros de masque. Ces tests ne prouvent pas le rejet systématique des longueurs incompatibles ni des valeurs non binaires.
- Dernière CI réceptionnée : n°206 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40241390833 au commit `262d79a8d16cab9831e11253617d7c564a4a46cd` ; 266 exécutions réussies, dont huit tests comptables lot 1. Ces résultats ne valent pas nouvelle recette du lot 2.

## Décision du 00

**GO TECHNIQUE CONDITIONNEL — C03-R06 LOT 2, SEULEMENT VALIDATION STRUCTURELLE DES FRAGMENTS.**

Le lot 2 doit imposer, avant toute interprétation des références S↔A/B :
1. Des entrées `data` et `mask` de types binaires compatibles et explicitement vérifiés, sans conversion implicite silencieuse.
2. `len(data) == len(mask)` pour tout fragment utilisé comme preuve.
3. Chaque octet de `mask` appartient strictement à `{0,1}`.
4. Pour toute référence examinée, bornes et longueurs de sous-tranches suffisantes ; la présence complète exige le marqueur `1` sur chacun des octets requis.
5. Rejet `AssertionError` contrôlé des structures incompatibles, sans certificat `RECONSTRUIT_BANC_FICTIF` positif ni changement des retours natifs SQLite.

### Mandat technique unique au chat 01

- Recontrôler HEAD, instructions du dépôt, `reciprocal_certificate()`, `_pointer_offsets()`, `fictional_entries()` et les tests déjà présents avant modification.
- Construire les fixtures synthétiques de validation structurelle : témoin normal S/A/B accepté ; masque S tronqué (même si tous les octets restants valent 1) ; masque A tronqué dans une zone nécessaire au pointeur ; masque B surdimensionné ; masque contenant `0x02` ; `data` ou `mask` de type incompatible. Distinguer dans le rapport tests existants réutilisés et nouveaux cas ajoutés.
- Identifier et démontrer d'abord les cas précis dont l'ancienne validation est insuffisante ; ne pas annoncer de faux certificat positif sans test observé.
- Apporter la correction Python **minimale** des contrôles d'entrée, en privilégiant une validation partagée, sans refonte du décodeur ou de la reconstruction des références.
- Les anomalies doivent échouer de manière déterministe et maîtrisée, pas par `IndexError`/`TypeError` accidentels. Les échecs de fixture doivent être bloquants.
- Préserver le certificat fictif `RECONSTRUIT_BANC_FICTIF`, S↔A/B, six suppressions attribuées, intégrité `ok/ok`, DELETE/FULL ainsi que les tests et acquis C03-R01/R02/R03/R04 et C03-R06 lot 1.
- Rapporter liste des fichiers et commits, résultats locaux exécutés ou absence de tests locaux, CI et journaux sur **commit exact**, échecs intermédiaires, limites et non-régression. Soumettre ensuite le lot à une recette indépendante du chat 03.
- **C03-R06 reste ouverte** ; la réception éventuelle du lot 2 n'équivaudra pas à sa clôture globale.

### Exclusions

Hors lot 2 : altération du contenu interne des pointeurs, checksum, marqueurs, générations et métadonnées contradictoires non structurelles ; concurrence générale ; modifications de `c03_vfs.c` ou `atlas_rd01_vfs.c` ; moteur SQLite, code métier, workflow, performance C03-R05, `BEFORE_DELEGATE`, SIGKILL, injection de panne, G04, fournisseurs réels, fusion main, publication et production.

## Statuts

- **C03-R01 à R04 : clôturées** seulement dans leurs périmètres expérimentaux fictifs.
- **C03-R05 : ouverte, qualification quantitative suspendue** (budget B non justifiable).
- **C03-R06 : ouverte, lot 1 reçu, lot 2 autorisé mais non encore qualifié**.
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 : ouverts**.
- **B6.5 en recette ; G04, B6.3 et production NO-GO**.

## Prochaine action unique

Transmettre ce mandat au chat 01 pour les seuls contrôles structurels `data`/`mask` de C03-R06 lot 2 et la préparation des preuves destinées à la recette indépendante 03.
