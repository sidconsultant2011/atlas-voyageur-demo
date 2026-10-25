# Décision 00 — SEC-01 R1-RD01 — Qualification expérimentale C03-R05

**Date :** 25 octobre 2026
**Branche autorisée :** `feature/b6-5-cartographie-interactive`
**HEAD vérifié avant décision :** `8b242d6d58788a3fc8f997db3867b5e6fa0a83c3`
**Chantier prioritaire unique :** C03-R05, préservation des propriétés fonctionnelles et caractérisation temporelle du prototype VFS C03.

## Sources contrôlées

- Clôture ciblée C03-R03 : `b65-http/DECISION-00-SEC01-RD01-C03-R03-CLOTURE-CIBLEE-20261025.md`.
- Code C expérimental : `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` ; interception d'appels VFS, copie de buffers et registre en mémoire. Risque d'effet observateur, sans mesure de neutralité déjà démontrée.
- Comparaison N/W existante : `b65-http/DECISION-00-SEC01-RD01-VFS-R01-COMPARAISON-RECEPTION-20261025.md`, CI n°129 ; équivalence fonctionnelle reçue dans un scénario COMMIT fictif borné, pas de comparaison des chronologies fines.
- Banc de contention N/W : `b65-http/DECISION-00-SEC01-RD01-VFS-R01-VERROUS-SYNC-RECEPTION-20261025.md`, CI n°135 ; effets observables COMMIT/ROLLBACK, SQLITE_BUSY et libération vérifiés pour N/W, sans qualification temporelle C03.
- CI de référence C03 n°178 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232772919 ; `completed/success` sur `63664ba669964c1427d5032cbf274d34b1b7a3dc`, 252 exécutions réussies. **Ne qualifie pas C03-R05.**
- Avis du chat 02 reçu le 25 octobre 2026 : priorité unique recommandée C03-R05 parmi R04/R05/R06 ; aucun code ou test produit par cette recommandation.

## Décision 00

**GO TECHNIQUE CONDITIONNEL, STRICTEMENT EXPÉRIMENTAL ET BORNÉ À C03-R05.**

Le seul chantier autorisé est l'étude comparative de préservation des propriétés transactionnelles du profil fictif SQLite rollback-DELETE multi-bases et la caractérisation des effets temporels de l'observateur C03 par rapport aux témoins N (native) et W (wrapper de référence existant). Aucune équivalence N/W/C03 n'est présumée.

### Mandat au chat 01

1. Lire les instructions applicables et inspecter l'état du dépôt. Réutiliser les bancs N/W existants et le prototype C03, sans redévelopper ni modifier ce qui est déjà validé.
2. **Protocole avant résultats** : documenter les trois configurations, la bibliothèque SQLite effectivement chargée, les paramètres SQL/PRAGMA, les machines/runners, l'environnement, l'ordre des campagnes, les répétitions, la mesure monotone adaptée, les périodes mesurées, l'échauffement éventuel et les conditions de contention. Éviter de calibrer un seuil a posteriori. Si un budget chiffré de surcharge est indispensable pour un GO/NO-GO, le proposer au 00 pour décision **avant** la campagne de qualification ; sans budget validé, ne prétendre qu'à une caractérisation descriptive.
3. Comparer les propriétés observables à scénario et configuration comparables : COMMIT et ROLLBACK normaux, états finaux et invariants, `SQLITE_BUSY` et libération des verrous, intégrité `ok/ok` sur les deux bases, DELETE/DELETE, FULL/FULL, absence de journaux résiduels en fin d'exécution normale, codes retour et erreurs. Documenter explicitement tout écart de couverture avec N/W.
4. Produire des mesures temporelles répétables et brutes autant que possible, avec distributions ou médianes et dispersion, et distinguer bruit d'environnement d'une surcharge potentielle. Les différences de durée sont à décrire ; **aucun résultat chiffré ni neutralité n'est anticipé**.
5. Confirmer que le certificat C03-3 demeure recevable pour COMMIT normal fictif et que C03-R01, C03-R02, C03-R03 ne régressent pas. Ne pas considérer les tests N/W passés comme des tests de C03.
6. **Limites techniques du mandat :** privilégier de nouveaux bancs/tests/documents expérimentaux séparés. **Ne modifier aucun wrapper C** (ni `c03_vfs.c` ni `atlas_rd01_vfs.c`), ni moteur SQLite, code métier, `_persistent_journey()`, workflow ou configuration de production. Si des fonctionnalités VFS nécessaires au profil manquent, ou si une nouvelle instrumentation est indispensable, arrêter ce périmètre et demander arbitrage au 00.
7. Exécuter les contrôles adaptés et consigner clairement les tests locaux effectivement réalisés versus GitHub Actions sur le commit exact, les anomalies et échecs intermédiaires, et les limites du runner. Préparer un rapport de preuves versionné, puis réception indépendante par le chat 03. Une absence de divergence sur un banc borné ne vaut pas neutralité générale.
8. En cas de modification transactionnelle inexpliquée, `SQLITE_BUSY` non préservé, certificat positif malgré erreur d'observation, ou mesure non reproductible, rendre un **NO-GO motivé** plutôt que transformer l'essai en preuve.

### Interdictions

Aucune instrumentation causale `BEFORE_DELEGATE`, SIGKILL, injection de panne ou reprise post-panne, G04, fournisseur réel, données personnelles, fusion main, publication ni déploiement. Aucun chantier C03-R04 ou C03-R06 engagé en parallèle.

### Statuts maintenus

**C03-R05 OUVERTE — qualification seulement autorisée** ; C03-R04 et R06 OUVERTES ; C03-R01 à R03 CLÔTURÉES dans leurs seuls périmètres expérimentaux ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 OUVERTS ; G04 NO-GO ; G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE ; B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 01 ce mandat de qualification expérimentale C03-R05 pour définir le protocole avant mesures, conduire la comparaison bornée sans modifier les wrappers, puis soumettre les preuves au chat 03 pour recette indépendante.
