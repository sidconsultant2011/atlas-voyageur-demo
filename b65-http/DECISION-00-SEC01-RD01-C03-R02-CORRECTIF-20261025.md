# Décision 00 — SEC-01 R1-RD01 — Correctif expérimental ciblé C03-R02

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `0cdcc8989c36d8a3dd81fb1e7fa8b9558908a9dd`  
**Chantier prioritaire unique :** attribution univoque d'une suppression `xDelete` à une incarnation de fichier dans le prototype fictif C03-3.

## Vérifications et fondement

- PV reçu : `b65-http/PV-03-SEC01-RD01-C03-3-20261025.md`.
- Prototype `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` : la fonction `de()` délègue actuellement `parent->xDelete(parent,z,n)`, puis si `SQLITE_OK` marque `deleted=1` pour **toutes** les entrées non supprimées dont le chemin égale `z`. Cette logique ne démontre pas l'incarnation supprimée en cas de réutilisation de chemin.
- `b65-http/test_c03_passive.py` : cinq tests préexistants.
- CI n°150 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40218478132 ; `completed/success` sur `3a1c004257f292c6b5cc2c12321a80228a4e8720`, 230 exécutions (pas nécessairement 230 scénarios uniques). **Aucun de ces résultats ne valide par avance C03-R02.**
- Avis indépendant 02 transmis le 25 octobre 2026 : C03-R02 est la priorité de sécurité parmi les six réserves de C03-3.

## Décision du 00

**GO TECHNIQUE CONDITIONNEL pour un seul correctif expérimental C03-R02**, strictement dans la copie isolée `c03-passive` et les tests correspondants, sur données fictives, COMMIT normal, sans panne ni arrêt causal. Ce GO ne constitue pas une preuve de correction, une clôture de réserve ou une autorisation de production.

### Exigence unique

Associer chaque événement `xDelete` réussi à **une incarnation unique démontrée** du fichier supprimé, ou classer cet événement **NON ATTRIBUABLE / REJETÉ**. Ne jamais marquer plusieurs incarnations supprimées par le même retour réussi ; ne jamais transformer un doute probatoire en `SQLITE_OK` instrumenté ni modifier le code retour natif.

### Protocole et critères falsifiables

1. Inventorier avant édition les règles de création, ouverture, fermeture, réutilisation de chemin et suppression réellement disponibles dans le prototype et leurs limites. Ne pas inventer une identité OS/SQLite qui ne serait pas attestée.
2. Cas à qualifier au minimum : (a) incarnation active unique, (b) deux incarnations historiques de même chemin avec cycle de vie discriminant, (c) plusieurs incarnations compatibles indiscernables, (d) `xDelete` natif en erreur, (e) suppression sans ouverture correspondante, (f) recréation après suppression. Pour chaque cas, attribuer de manière vérifiable **exactement un objet ou zéro** et signaler les ambiguïtés.
3. Distinguer **le retour SQLite de l'opération** de **la validité de son attribution probatoire**. L'absence d'attribution ne doit jamais masquer, altérer ou inventer un résultat de suppression. Ne pas considérer qu'une comparaison de chemins ou un numéro de génération seul prouve l'identité de l'objet système.
4. Garder le prototype non réentrant, sans lecture de fichiers vivants, modification des paramètres SQLite, blocage artificiel, mécanisme de preuve post-panne ni nouvelle collecte hors périmètre.
5. Conserver les comportements déjà reçus : liens S→{A,B}, A→S, B→S, COMMIT normal fictif, DELETE/FULL, codes d'erreur, invariants SQL, intégrité et absence de journaux résiduels.
6. Ajouter des tests locaux ciblés et les faire vérifier par GitHub Actions dans le workflow existant sans l'altérer, en rapportant séparément les résultats locaux et CI avec les SHA précis. En cas de preuve d'identité inatteignable sans intervention invalidante, **arrêter et documenter NO-GO motivé**, sans artificiellement réussir un scénario.
7. Remettre rapport de preuves, diff exact, résultats, limites et réserves C03-R01 et R03–R06 toujours ouvertes ; demander **recette indépendante du chat 03** avant toute nouvelle décision de clôture au 00.

### Interdictions

Ne pas modifier `atlas_rd01_vfs.c` (wrapper de référence), le code métier, `_persistent_journey()`, ni le moteur SQLite. Aucun `BEFORE_DELEGATE`, SIGKILL, injection de panne, G04, traitement parallèle de C03-R01/R03–R06, fusion `main`, fournisseur réel, achat, secret ou publication.

## Statuts après autorisation

**C03-R02 : OUVERTE, correctif expérimental autorisé et non encore réalisé.** C03-3 reçu avec réserves, globalement OUVERT ; C03-R01 et C03-R03 à R06 OUVERTES ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS ; G03 préparation avec réserves ; G04 NO-GO ; G05 partiel ; R1-C01 partiel ; B6.5 en recette ; B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 01 le mandat de correctif isolé C03-R02 avec cas de rejet obligatoires, puis faire réceptionner le résultat indépendamment par 03 avant nouvel arbitrage du 00.
