# Décision 00 — SEC-01 R1-RD01 — Livraison technique C03-R05 pour recette indépendante

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `e4af004c87ef69d7c06dad11b4c0927b40fdb517`  
**Chantier prioritaire unique :** réception indépendante de la comparaison fonctionnelle et de la caractérisation temporelle N/W/C03, C03-R05.

## Sources vérifiées

- Mandat 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R05-NEUTRALITE-20261025.md`.
- Protocole préalable : `b65-http/SEC01-RD01-C03-R05-PROTOCOLE-20261025.md`, commit `816556e2b54e3cc4c87523d5028b1b5320a9c431`, **antérieur aux ajouts du banc et du test**.
- Rapport 01 : `b65-http/SEC01-RD01-C03-R05-NEUTRALITE-PREUVES-20261025.md`.
- GitHub compare `ed4a40e19e633ad32cc28ae6580990693b00cb81..e4af004c87ef69d7c06dad11b4c0927b40fdb517` : **quatre fichiers uniquement** : protocole et rapport ajoutés, `b65-http/c03_r05_compare.py` et `b65-http/test_c03_r05.py` ajoutés ; aucune modification des wrappers C, application, moteur SQLite ou workflow.
- Commit testé exact `d5248e4510c1c3502138a5bf62f1213ba858e8fd`.
- CI n°186 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40234530686 : `completed/success`, sur le commit testé ; logs : **116/116 JavaScript, 11/11 SQLite, 126/126 HTTP/identité/banc = 253 exécutions réussies**, pas nécessairement 253 scénarios distincts.
- Test `test_three_vfs_functional_parity_and_descriptive_measurements` : réussi. Appel à `campaign()`, assertions sur la parité, 18 mesures, six échauffements, trois valeurs par configuration et scénario.
- Protocole : trois modes N native, W wrapper de référence, C03 prototype ; **COMMIT et ROLLBACK**, `SQLITE_BUSY=5`, libération normale des verrous et réessai, deux bases fictives, `journal_mode=DELETE`, `synchronous=FULL`, `integrity_check=ok/ok`, absence de journaux résiduels, sous-processus et répertoires temporaires isolés, `perf_counter_ns()`.
- **Échantillon mesuré** : un échauffement par couple scénario/mode = 6 ; trois mesures par couple = 18. Ordre fixe alterné des modes. La durée comprend l'initialisation des bases, la contention et les contrôles ; exclut compilation, démarrage du sous-processus et enregistrement VFS.
- Médianes issues du rapport 01 : COMMIT N=12,882795 ms, W=13,613391 ms, C03=12,865131 ms ; ROLLBACK N=10,139528 ms, W=10,768111 ms, C03=10,535503 ms. **Valeurs descriptives, pas verdict de performance.** Le rapport conserve aussi chacune des 18 valeurs brutes.
- CI n°186 conserve le certificat fictif C03-3 `RECONSTRUIT_BANC_FICTIF` et les tests antérieurs C03-R01/R02/R03 ; absence d'échec dans cette campagne ne vaut pas qualification générale.
- **Tests locaux du commit exact : non exécutés selon le rapport 01** ; le chat 00 n'a lancé aucun test supplémentaire.

## Décision du 00

**LIVRAISON TECHNIQUE C03-R05 ACCEPTÉE POUR RECETTE INDÉPENDANTE PAR LE CHAT 03, SANS CLÔTURE DE C03-R05.**

La comparaison N/W/C03 apporte une preuve candidate de **parité fonctionnelle observée** dans le seul profil fictif testé de contention SQLite COMMIT/ROLLBACK. Elle caractérise descriptivement les durées sans budget temporel approuvé ni démonstration de neutralité temporelle absolue ou générale.

### Mandat unique au chat 03 — Recette indépendante

1. Vérifier que le protocole a été versionné **avant** les mesures, distinguer les commits `816556e2`, `aa26055e` (précision du protocole), `d5248e45` et HEAD documentaire ; vérifier absence de seuil de surcharge fabriqué après résultats.
2. Inspecter `c03_r05_compare.py` et `test_c03_r05.py` au commit testé : identité SQLite et bibliothèque effectivement utilisée, isolation des sous-processus, réutilisation du scénario N/W, présence effective de C03, assertions bloquantes de `SQLITE_BUSY`, COMMIT/ROLLBACK, état final, intégrité, DELETE/FULL, absence de journaux résiduels et absence d'overflow C03.
3. Vérifier les logs CI n°186 au **commit exact**, résultats 116/11/126, présence des mesures brutes, six échauffements non mesurés, 18 mesures mesurées, trois valeurs par groupe, calcul des médianes et dispersions, exécution des tests anciens C03-R01/R02/R03 et du certificat fictif C03-3.
4. Qualifier précisément le périmètre temporel mesuré : initialisation + contention + vérifications ; exclusions du chronomètre ; bruit du runner partagé, répétitions réduites, absence de seuil de performance, chronologies natives non comparables.
5. Confirmer le périmètre de quatre fichiers et le maintien des wrappers C, moteur SQLite, métier et workflow inchangés.
6. Émettre un **PV indépendant** : GO/NO-GO de réception de la parité fonctionnelle bornée et de la **caractérisation descriptive** des durées, recommandations précises sur le maintien ouvert ou l'éventuelle clôture **ciblée et partielle** de C03-R05. Ne pas assimiler trois répétitions à la neutralité temporelle.
7. Remonter le PV au 00, qui seul pourra arbitrer le statut de C03-R05. Aucun développement ou nouveau test par 03 au titre de ce mandat.

**Interdictions :** aucune instrumentation causale `BEFORE_DELEGATE`, SIGKILL, injection de panne, G04, modifications wrappers, `_persistent_journey()`, fusion main, fournisseur réel, site public ou production.

## Statuts maintenus

**C03-R05 OUVERTE — livraison en attente de PV 03** ; C03-R04 et R06 OUVERTES ; C03-R01, R02 et R03 CLÔTURÉES uniquement dans leur périmètre expérimental fictif ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS ; G04 NO-GO ; G05 partiel ; R1-C01 partiel ; B6.5 en recette ; B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 03 le protocole, le rapport 01, le commit testé et les journaux de la CI n°186 pour une recette indépendante strictement limitée à C03-R05.
