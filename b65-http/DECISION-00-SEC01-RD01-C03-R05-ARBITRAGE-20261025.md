# Décision 00 — SEC-01 R1-RD01 — Réception expérimentale C03-R05 et maintien ouvert

**Date :** 25 octobre 2026
**Branche :** `feature/b6-5-cartographie-interactive`
**HEAD vérifié avant décision :** `209d21a83f4c5f4b3a885003aefb22d27e40ec90`
**Autorité :** 00 — Pilotage et gouvernance.
**Chantier prioritaire unique :** qualification probatoire C03-R05 ; aucune nouvelle réalisation technique autorisée par ce document.

## Sources et preuves contrôlées

- Mandat 00 initial : `b65-http/DECISION-00-SEC01-RD01-C03-R05-NEUTRALITE-20261025.md`.
- Réception du livrable pour recette : `b65-http/DECISION-00-SEC01-RD01-C03-R05-RECEPTION-20261025.md`.
- Protocole `b65-http/SEC01-RD01-C03-R05-PROTOCOLE-20261025.md`, première version `816556e2b54e3cc4c87523d5028b1b5320a9c431`, version précisant le chronomètre `aa26055e`, toutes deux antérieures à la CI mesurée.
- Rapport de preuves `b65-http/SEC01-RD01-C03-R05-NEUTRALITE-PREUVES-20261025.md`.
- PV indépendant du chat 03 transmis au 00 le 25 octobre 2026 sous le titre `PV-03-SEC01-RD01-C03-R05-20261025` : réception favorable avec réserves, **recommandation explicite de maintenir C03-R05 ouverte**. La présence du PV comme fichier GitHub indépendant n'a pas été établie.
- GitHub Actions n°186 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40234530686 — `completed / success`, **commit exact `d5248e4510c1c3502138a5bf62f1213ba858e8fd`**. Journaux consultés : 116/116 JavaScript, 11/11 SQLite, 126/126 HTTP/identité/banc = **253 exécutions réussies** (pas nécessairement 253 scénarios uniques).
- Le test `test_three_vfs_functional_parity_and_descriptive_measurements` est `ok`, et la trace `RD01 C03-R05 N/W/C03 PARITY AND TIMINGS` indique `functional_parity=true`, `measured_samples=18`. Six échauffements exécutés par le parcours de la campagne, sans journal individuel des temps d'échauffement.
- Aucun wrapper C, moteur SQLite, module métier ou workflow modifié dans le périmètre livré.
- Tests locaux du commit exact : **non exécutés** selon le rapport 01 ; aucun nouveau test déclenché par les chats 03 ou 00.

## Décision du 00

**GO DE RÉCEPTION EXPÉRIMENTALE LIMITÉE :**
1. **Parité fonctionnelle bornée N/W/C03 reçue** pour les scénarios fictifs COMMIT et ROLLBACK avec contention testée : `SQLITE_BUSY=5`, libération et réessai, cohérence des états, DELETE/FULL, intégrité `ok/ok`, absence de journaux résiduels et dépassements C03 sur les essais.
2. **Caractérisation temporelle descriptive reçue** : six échauffements, 18 durées, trois mesures par couple scénario/VFS, statistiques vérifiées.

**NO-GO À LA CLÔTURE DE C03-R05 : RÉSERVE MAINTENUE OUVERTE.**

Les mesures couvrent tout le scénario depuis `_scenario` jusqu'à son retour : initialisation, contention, SQL et contrôles, **mais pas** compilation, démarrage du processus, enregistrement VFS ni vérification finale `c03_overflow()`. Elles ne caractérisent pas séparément les callbacks et ne démontrent pas la neutralité temporelle générale. Trois mesures par groupe sur un runner partagé et l'absence de budget temporel validé interdisent tout verdict de surcharge acceptable ou neutralité absolue.

Médianes du rapport, en millisecondes : COMMIT N=12,882795, W=13,613391, C03=12,865131 ; ROLLBACK N=10,139528, W=10,768111, C03=10,535503. **Aucun seuil de performance n'est adopté a posteriori.**

## Limites, statuts et restrictions

- **C03-R05 OUVERTE** ; **C03-R04 et C03-R06 OUVERTES**.
- **C03-R01, C03-R02 et C03-R03 CLÔTURÉES uniquement dans leur périmètre fictif borné**.
- **C03-3 global OUVERT**, ainsi que G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01.
- G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE ; **G04, B6.3 et production NO-GO**.
- La parité fonctionnelle observée ne prouve pas une identité physique universelle, une équivalence des séquences VFS natives, une concurrence interprocessus générale, `BEFORE_DELEGATE`, une récupération après panne ou une durabilité physique.
- Aucun nouveau développement, instrumentation, panne, SIGKILL, injection, G04, activation réelle, fusion main, publication ou déploiement autorisé par cette décision.

## Prochaine action unique

Demander au chat 02 un avis **strictement documentaire** sur le critère de preuve encore manquant pour C03-R05 et la pertinence d'un complément limité, avant tout nouveau mandat technique du 00.
