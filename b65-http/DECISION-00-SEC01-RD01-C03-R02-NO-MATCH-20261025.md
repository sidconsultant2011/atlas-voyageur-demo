# Décision 00 — SEC-01 R1-RD01 — Complément bloquant no_match C03-R02

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `3cc5fb59089f731f7af28985e9e5e2c57727b1f6`  
**Chantier prioritaire unique :** refus d'un certificat C03-R02 contenant `no_match>0`.

## Sources vérifiées

- PV indépendant : `b65-http/PV-03-SEC01-RD01-C03-R02-20261025.md`.
- Code courant : `b65-http/rd01-vfs-step1/c03-passive/c03_run.py`. La condition d'échec du certificat contient `ambiguous`, `native_errors`, `not_closed`, mais **pas `no_match`** ; le compteur est néanmoins collecté.
- Helper C expérimental `attribute_delete()` : le rejet probatoire `no_match` est déjà comptabilisé, avec conservation du retour natif SQLite.
- CI n°157 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40224448242, `completed/success` sur `3bdc4a7bf06cc3fccbc75e3809fb2fcf41e24742` ; 116 JavaScript, 11 SQLite, 110 HTTP/identité/banc = 237 exécutions, dont sept tests C03-R02. La CI positive a `no_match=0` et ne valide pas le rejet d'un `no_match>0`.
- Avis documentaire indépendant du chat 02 reçu le 25 octobre 2026 : **NO-GO de clôture ciblée**, GO conditionnel recommandé pour ce seul complément.

## Décision du 00

**NO-GO DE CLÔTURE C03-R02 À CE STADE.** La correction du marquage multiple est conservée comme acquise dans le périmètre testé.

**GO TECHNIQUE LIMITÉ** à la vérification bloquante `no_match>0` au niveau du certificat Python et à ses tests associés, sur données fictives.

### Mandat unique au chat 01

1. Avant toute édition, consulter les instructions applicables du dépôt et vérifier le HEAD, le code actuel et les tests existants pour éviter tout doublon.
2. Limiter le correctif à `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` et à un test Python ciblé existant ou nouveau si nécessaire. Éviter toute refonte et préserver le reste du certificat.
3. Le certificat doit être **rejeté**, et non simplement annoté, si `no_match>0`. Les rejets actuels `ambiguous>0`, `native_errors>0` et `not_closed>0` doivent rester opérants.
4. Test négatif **bloquant**, directement sur la validation Python réellement utilisée par le certificat, avec `no_match=1` et éventuellement plusieurs suppressions non attribuables ; vérifier le comportement inverse lorsque tous les compteurs sont nuls. Ne pas prétendre qu'un test de helper C démontre ce contrôle Python.
5. Préserver le scénario C03-3 du COMMIT normal fictif, les relations S↔A/B, DELETE/FULL, intégrité SQL et les résultats existants. Tester la non-régression et rattacher précisément le code testé au commit et à la CI.
6. Rapporter séparément les tests locaux réellement exécutés et ceux de GitHub Actions, avec détails des assertions, résultat et limites. Si le test ne peut être raccordé au chemin effectif de validation, remonter un **NO-GO motivé** plutôt que simuler une réussite.
7. Remettre un rapport de preuves et soumettre le résultat au chat 03 pour recette indépendante avant toute décision de clôture ciblée du 00.

### Interdictions

Aucune modification du C `c03_vfs.c`, de `attribute_delete()`, du wrapper de référence `atlas_rd01_vfs.c`, du moteur, du code métier, de `_persistent_journey()`, des paramètres SQLite ou du workflow. Aucun `BEFORE_DELEGATE`, SIGKILL, injection de panne, G04, fusion `main`, fournisseur réel, secret, publication ou production.

## Critère de réception falsifiable

- `no_match=0` et autres anomalies nulles : certificat potentiellement valide sous les autres assertions existantes.
- `no_match=1` ou `no_match>1` : **échec bloquant du certificat**.
- `ambiguous>0`, `native_errors>0` ou `not_closed>0` : rejets préservés.
- Aucun changement des retours de la VFS native et aucun faux succès dû à un simple champ JSON.

## Statuts conservés

**C03-R02 OUVERTE** en attente de complément et de recette 03 ; C03-3 expérimental reçu avec réserves et globalement ouvert ; C03-R01 et C03-R03 à R06 ouvertes ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global partiel ; R1-C01 partiel ; B6.5 en recette ; B6.3 et production NO-GO.

## Prochaine action unique

Transmettre au chat 01 le mandat de correction minimale du certificat Python `no_match`, avec test négatif bloquant et recette indépendante 03 exigée avant clôture.
