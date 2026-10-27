# 00 — SEC-01 — Mandat ciblé de qualification HTTP concurrente avec révocation

**Date :** 27 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `a33f1687d67c3f3c9eaa8f96771b23835e933a12`  
**Autorité :** 00 — Pilotage et gouvernance

## Justification fondée sur les exigences produit

Avis documentaire du chat 02 remis au 00 le 27 octobre 2026 : priorité unique à une preuve déterministe du comportement HTTP et des états SQLite lorsqu'une opération métier protégée concurrence une révocation. Aucun développement ni test exécuté par 02.

Sources GitHub revérifiées :
- `b65-http/DECISION-00-SEC01-R1-CRITERES-20261025.md` : critères approuvés R1-C01 à R1-C07 et distinction entre mutation commitée avant révocation, qui peut répondre ultérieurement, et mutation non validée devant être refusée après le point de prise d'effet.
- `b65-http/PV-03-SEC01-R1-COMPLEMENT-20261025.md` : R1-C02 à R1-C07 **recevables dans le seul périmètre local testé**, R1-C01 **PARTIEL** (atomicité/durabilité en panne COMMIT multi-bases non démontrées). CI historique n°83 au commit `6886eff86ea5479f68a88a2893bc4fdbaa2608f5`, 221 exécutions selon PV : non rejouée par 00 ici.
- `b65-http/test_sec01_r1_complements.py` : les tests existants couvrent création/mise à jour/suppression avec `BEGIN IMMEDIATE` et entrelacements forcés, contention entre processus partageant une base SQLite locale, refus HTTP des mutations après révocation et rollback des bases attachées. Éviter les doublons.
- `b65-http/DECISION-00-SEC01-RD01-G03-R01-NECESSITE-PROPORTIONNALITE-20261027.md` : ne pas imposer l'instrumentation causale C03/G03-R01 comme condition universelle sans nécessité de preuve démontrée ; extensions C03 suspendues.
- `b65-http/DECISION-00-SEC01-RD01-C03-R06-LOT2-RECETTE-20261027.md` : lot 2 reçu avec réserves ; C03-R06 globale ouverte.

Le risque qualifié est une **lacune probatoire ciblée**, pas une vulnérabilité constatée : il n'existe pas encore de preuve HTTP déterministe distincte couvrant la requête déjà engagée pendant la révocation et corrélant l'ordre des COMMIT avec l'état SQL.

## Décision 00

**GO — QUALIFICATION CIBLÉE R1 HTTP + SQLITE CONCURRENTE AVEC RÉVOCATION.**

Un seul chantier prioritaire actif : produire une preuve HTTP et SQL traçable avec données fictives locales. **Mandat de tests et de preuves uniquement ; aucun correctif de code métier n'est autorisé à ce stade.** Si un défaut est découvert, consigner ses effets, arrêter l'extension et demander un arbitrage 00 spécifique.

### Contrat de recette minimal falsifiable

1. Avant toute modification, vérifier HEAD, instructions applicables, contrôle HTTP, transactions R1 et tests existants. Réutiliser `test_sec01_r1_complements.py`, les fixtures et le mécanisme `BEGIN IMMEDIATE`.
2. Construire le **plus petit ajout de test déterministe** nécessaire aux entrelacements HTTP réellement non couverts, avec barrières de synchronisation après acquisition du verrou SQL prouvée et chronologie cohérente des COMMIT. Ne pas utiliser un `sleep` probabiliste comme preuve d'ordonnancement.
3. Montrer une mutation autorisée commitée **avant** le COMMIT de révocation, même si la réponse HTTP de mutation survient après ; ne pas compter ce cas comme violation.
4. Montrer qu'une mutation encore non validée au moment où la révocation prend effet ne persiste pas illégitimement après. Si l'ordre des transactions permet à la mutation d'être validée avant révocation, documenter l'ordre plutôt que de conclure abusivement à une défaillance.
5. Rejeter avec HTTP 401 et sans effet SQL une requête protégée initiée après HTTP 200 de révocation ; vérifier également deux requêtes concurrentes sur une même session et une connexion réouverte après révocation **dans la mesure où ces sous-cas sont réellement manquants des tests existants**.
6. Corréler requêtes/résultats HTTP, point de prise d'effet et relectures indépendantes des bases `sessions` et `identities`, au moyen d'éléments probatoires non sensibles. Critère NO-GO : une session révoquée produit une nouvelle mutation protégée ou une mutation non autorisée se trouve persistée après l'effet de révocation.
7. Préserver les acquis R1, C03-R01 à R04, C03-R06 lots 1 et 2, les fonctionnalités B6.5 et les retours SQLite. Fournir références de fichiers et commits, tests locaux réellement exécutés, CI GitHub sur **commit exact**, logs, échecs intermédiaires, limites et éventuel PV 03 indépendant.
8. Si une preuve directe du verrou SQL ou de l'ordre du COMMIT exige un changement applicatif, un seam de test susceptible d'altérer les invariants ou une instrumentation interdite, ne pas l'entreprendre implicitement ; présenter d'abord au 00 la limite et une solution minimale à autoriser séparément.

**Exclusions :** développement métier, fournisseur réel, données personnelles, activation production, fusion main, publication, G04, injection de panne, SIGKILL, instrumentation `BEFORE_DELEGATE`, extension C03, campagne quantitative C03-R05. Aucune qualification distribuée entre hôtes indépendants ni durabilité physique promise.

## Statuts conservés

- R1-C02 à R1-C07 : recevables **localement** suivant PV 03 historique ; R1-C01 : **PARTIEL**.
- R1, R1-RD01 et P0-01 : **OUVERTS**.
- C03-R01 à R04 : clôturées dans les seuls périmètres expérimentaux fictifs ; C03-R05 ouverte et suspendue ; C03-R06 ouverte, lots 1 et 2 reçus.
- C03-3 global, G03-R01, VFS-R01 et G03-R06 : **OUVERTS**.
- B6.5 en recette ; G04, B6.3 et production : **NO-GO**.

## Prochaine action unique

Transmettre au chat 01 le mandat de qualification HTTP concurrente avec révocation, limité aux tests et preuves manquants, pour exécution contrôlée sans nouveau chantier C03.
