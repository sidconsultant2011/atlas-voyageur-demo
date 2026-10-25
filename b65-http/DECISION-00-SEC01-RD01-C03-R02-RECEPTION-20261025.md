# Décision 00 — SEC-01 R1-RD01 — Livraison technique C03-R02 à la recette indépendante

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `c819219d8c81d59eedf597a72ab06106f460d0d1`  
**Chantier prioritaire unique :** réception indépendante du correctif expérimental d'attribution `xDelete` C03-R02.

## Preuves directement contrôlées

- Mandat du 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R02-CORRECTIF-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-C03-R02-CORRECTIF-PREUVES-20261025.md`.
- Comparaison GitHub `ea4525e5606e40f3e30d6896e5a32230127d03da..c819219d8c81d59eedf597a72ab06106f460d0d1` : quatre fichiers, dans le périmètre autorisé : `c03_vfs.c` et `c03_run.py` modifiés, `test_c03_r02.py` et le rapport ajoutés. Aucun changement au wrapper de référence `atlas_rd01_vfs.c`, au code métier ou au workflow.
- GitHub Actions **n°157**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40224448242 : `completed / success`, sur le **commit testé `3bdc4a7bf06cc3fccbc75e3809fb2fcf41e24742`**.
- **116/116** JavaScript, **11/11** SQLite, **110/110** HTTP/identité/banc : **237 exécutions réussies**, non nécessairement 237 scénarios distincts.
- Sept tests C03-R02 nommés dans les journaux : incarnation unique fermée, chemin réutilisé à cycles discriminés, plusieurs candidats compatibles rejetés, erreur native de suppression non masquée, suppression sans ouverture, recréation après suppression, incarnation encore ouverte non attribuée. Tous `ok`.
- Certificat CI de non-régression : `RECONSTRUIT_BANC_FICTIF`, liens `S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true`, `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}` ; intégrité `ok/ok`, DELETE/DELETE et FULL/FULL, SQLite CI 3.45.1.
- Tests locaux **sur le commit exact** : **non exécutés** ; les exécutions CI ne doivent pas être présentées comme tests locaux.

## Décision du 00

**LIVRAISON TECHNIQUE ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03**, sans clôture anticipée de C03-R02.

Le nouveau mécanisme de preuve distingue la suppression réelle déléguée à la VFS mère et l'attribution probatoire à une incarnation observée. En cas d'ambiguïté, le mécanisme ne doit marquer aucune incarnation tout en conservant le code retour SQLite. Les observations positives de CI sont limitées au banc fictif, aux identités surveillées et au scénario COMMIT normal.

### Mandat unique au chat 03

1. Contrôler au commit testé le diff C du callback `xDelete` et du helper `attribute_delete()` : jamais plusieurs incarnations marquées par un seul `xDelete`, `SQLITE_OK` natif conservé, événements `no_match`, `ambiguous`, `native_errors` et `not_closed` distingués sans changer les retours.
2. Examiner les sept tests de `b65-http/test_c03_r02.py`, leurs assertions et leur raccord réel à la fonction utilisée par le callback, en distinguant les codes retour injectés dans les tests du fonctionnement réel du système de fichiers.
3. Vérifier les preuves CI n°157 sur `3bdc4a7b`, les sept résultats individuels, le certificat de non-régression C03-3 et la séparation des tests locaux non exécutés.
4. Qualifier la portée de l'unicité : incarnation prouvée **parmi les entrées du registre**, sans identité universelle de l'objet OS ni couverture exhaustive des changements de chemin et de concurrence.
5. Conserver C03-R01 et C03-R03 à R06 comme réserves ouvertes, notamment fermeture, mémoire et neutralité, sans les traiter au titre du présent PV.
6. Remettre un **PV 03 indépendant** (recevable / réserves / NO-GO motivé) avec preuves, anomalies, risques résiduels et recommandation de décision au 00. Aucun nouveau développement ni essai demandé à 03.

**Interdits :** aucune modification C/Python, métier, wrapper de référence ou workflow par ce mandat ; aucune injection, panne, SIGKILL, `BEFORE_DELEGATE`, G04, fusion main ni publication.

## Statuts maintenus

**C03-R02 OUVERTE — livraison technique en attente de recette indépendante** ; C03-3 prototype reçu avec réserves et globalement ouvert ; C03-R01 et R03 à R06 ouvertes ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 ouverts ; G03 préparation avec réserves ; G04 NO-GO ; G05 partiel ; R1-C01 partiel ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.

## Prochaine action unique

Transmettre le présent mandat, le rapport du chat 01, le commit testé et les journaux CI n°157 au chat 03 pour réception indépendante limitée à C03-R02.
