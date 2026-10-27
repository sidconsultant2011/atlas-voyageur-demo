# 00 — SEC-01 R1-C01 — Réception de l'avis 02 et GO de cadrage AC-13

**Date :** 27 octobre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `aa2bdcf364647385bf1896845471d2aaa9c098ee`.

## Éléments reçus et vérifiés

Avis indépendant du chat 02 remis au 00 le 27 octobre 2026, intitulé `02 — SÉCURITÉ P0 — Évaluation des réserves AC-08 et AC-13`. Sa conclusion recommande **AC-13** comme priorité unique, en maintenant AC-08 comme réceptionné avec réserves. Cet avis est présent dans la conversation ; aucune livraison autonome dans le dépôt n'est présumée.

Sources directes GitHub vérifiées au HEAD : décision `b65-http/DECISION-00-SEC01-R1-C01-AC08-RECETTE-INDEPENDANTE-20261027.md`, `b65-http/local_http_facade.py`, `b65-http/sqlite_ac08.py`.

- `local_http_facade.py` possède `fail()` et `send_json()`, mais `do_POST` appelle directement `state.revoke()` (ligne 112) sans conversion explicite locale des exceptions SQLite et `SQLitePreconditionError` en réponse HTTP structurée.
- Les autres chemins HTTP persistants utilisent les connexions pour sessions et parcours ; une analyse exhaustive des frontières de gestion des exceptions fait précisément partie du cadrage.
- `sqlite_ac08.py` peut lever `SQLitePreconditionError` avec codes stables pour des préconditions incompatibles. Le refus de poursuivre la mutation est intentionnel ; la traduction HTTP stable n'est pas qualifiée.
- AC-08 a été réceptionné favorablement avec réserves sur le prototype fictif local. La CI n°238 a été reçue avec 288 exécutions réussies sur le commit `eb97c24eb969b2a28f4276b1c489d7eb46a6c6a4`. Aucun nouveau test n'a été réalisé pour le présent avis.

Les erreurs d'interface ne prouvent **ni** un contournement effectif de l'autorisation **ni** une corruption SQLite constatée ; le risque concerne une réponse ambiguë, une indisponibilité non maîtrisée ou une erreur potentiellement sensible exposée.

## Décision officielle

**GO — RÉCEPTION DE L'AVIS DE PROPORTIONNALITÉ 02.**

**AC-13 devient le seul chantier prioritaire actif : GO DE CADRAGE TECHNIQUE UNIQUEMENT, SANS DÉVELOPPEMENT NI TEST.** Le chat 01 est chargé de remettre une seule proposition technique bornée, après vérification du code GitHub et des acquis existants.

### Périmètre du cadrage AC-13

1. Inventorier tous les points d'entrée HTTP persistants pour création, contrôle, révocation de sessions et lecture/mutation de parcours, y compris via le pont d'identité fictif ; identifier les appels pouvant lever `SQLitePreconditionError`, `sqlite3.OperationalError` et les erreurs de connexion, de transaction et de COMMIT.
2. Identifier le comportement actuellement codé, les éventuels traitements d'exception déjà présents, les chemins de réponse HTTP et les points où un succès 200/201 pourrait être trompeur. Ne pas inventer d'état de COMMIT.
3. Définir une proposition unique de traitement HTTP borné : échec de précondition AC-08, indisponibilité/occupation SQLite, refus de toute autorisation impossible à vérifier, absence de fuite de secrets ou chemins locaux, réponse structurée sans annoncer la réussite ou l'annulation lorsque l'issue du COMMIT est incertaine.
4. Examiner un éventuel statut HTTP d'indisponibilité (503 ou autre) et un code d'erreur stable, **sans le déclarer validé**. Vérifier les interactions avec cookies, réponses et réessais, ainsi que les limites d'un traitement synchrone.
5. Fournir un périmètre de fichiers minimal, des critères falsifiables de tests ciblés et de non-régression R1/B6.5/AC-08, et les risques résiduels. Une seule proposition de réalisation pour arbitrage ultérieur du 00.

### Exclusions et réserves

**Aucun GO d'implémentation n'est donné à ce stade.** Aucun code, tests locaux, CI, injection de panne, SIGKILL, VFS/`BEFORE_DELEGATE`, C03, G04, migration SQLite, modification d'architecture, fournisseurs réels, données personnelles réelles, fusion `main`, publication ou production. AC-08 ne doit pas être rouvert. La qualification d'atomicité récupérée après panne interne du COMMIT, durabilité physique, sécurité multi-hôtes, accès de clients SQLite externes, liens symboliques et remplacement concurrent restent distincts.

## États de gouvernance conservés

- AC-08 : **RÉCEPTIONNÉ AVEC RÉSERVES** dans le périmètre expérimental.
- AC-13 : **OUVERT**, cadrage autorisé, non réalisé et non qualifié.
- R1-C01 : **PARTIEL** ; R1-RD01, R1, P0-01 : **OUVERTS**.
- B6.5 : **EN RECETTE** ; B6.3, G04, production : **NO-GO**.
- C03-R05 suspendu ; C03-R06 ouvert ; extensions C03 et G03 non autorisées.

## Prochaine action unique

Transmettre au chat 01 le mandat de cadrage AC-13, sans toucher au code ni exécuter de tests, pour obtenir une proposition technique unique et ses critères de qualification.
