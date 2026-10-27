# 00 — SEC-01 R1-C01 — Réception du contrat documentaire V1.0

**Date :** 27 octobre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `c4165531d17983782388e129a03a198b9bb1c03f`

## Références vérifiées

- Contrat livré par le chat 04 : `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md`, version 1.0, **14 868 caractères**, vérifié sur GitHub au commit `c4165531d17983782388e129a03a198b9bb1c03f`.
- Le commit documentaire ajoute **un fichier** ; aucune modification applicative n'est attestée dans ce commit.
- Mandat 00 : `b65-http/DECISION-00-SEC01-R1-C01-REVUE-RESULTAT-20261027.md` et réception matrice `b65-http/DECISION-00-SEC01-R1-C01-MATRICE-RECEPTION-20261027.md`.
- Contrôles préexistants : réception HTTP concurrente CI n°218 et rapport historique RD01 CI n°90, **sans nouvelle exécution** au titre du présent contrat.

## Examen du contrat

Le document sépare la révocation HTTP **mono-base** `sessions.sqlite` ; le pont de mutations persistantes utilisant `ATTACH` des bases `sessions.sqlite` / `identities.sqlite` ; l'association mémoire `_bindings` ; et la **fixture** expérimentale RD01 qui associe deux écritures explicites. Il décrit les opérations, fichiers lus et modifiés, points de validation logique, invariants AVANT/APRÈS et cas partiels réellement interdits.

Il distingue le comportement observé ou établi par lecture de code des exigences **encore proposées** : préconditions obligatoires de journalisation et de stockage, garantie de récupération après panne, gestion maîtrisée des exceptions SQLite/COMMIT, refus sécurisé en cas d'incohérence. Le code de connexion ne garantit pas explicitement partout `DELETE`/`FULL` ni le rejet d'un mode incompatible comme WAL pour l'atomicité inter-fichiers recherchée. Ces lacunes probatoires ne sont pas érigées en défaillances effectivement reproduites.

Le contrat propose un **unique contrôle ultérieur** : audit statique non destructif des préconditions de connexion SQLite et du traitement des exceptions COMMIT sur les chemins réellement exposés par HTTP.

## Décision officielle du 00

**GO — RÉCEPTION DOCUMENTAIRE DU CONTRAT R1-C01 V1.0, AVEC RÉSERVES.** La livraison du chat 04 est achevée dans son périmètre autorisé.

**Verdict global R1-C01 : NON CONCLUANT ; critère R1-C01 : PARTIEL.** R1-RD01, R1 et P0-01 demeurent ouverts. Le contrat ne constitue ni une certification d'atomicité durable après panne ni une validation de production.

**GO — AUDIT STATIQUE CIBLÉ**, en priorité unique suivante, confiée au **chat 02 — Sécurité P0**, exclusivement pour comparer le code réel aux préconditions SQLite et aux exigences de traitement des erreurs COMMIT déjà identifiées. Le chat 02 doit commencer par vérifier HEAD et rechercher un audit équivalent existant avant toute nouvelle production documentaire.

### Objet et critères de l'audit documentaire statique

1. Lister les chemins HTTP persistants effectivement exposés, `connect()`, `ATTACH`, `BEGIN IMMEDIATE`, création/révocation et mutations d'identité ; distinguer lecture et écriture, mono-base et multi-bases.
2. Pour chaque connexion pertinente, documenter ce qui est explicitement imposé par le code, seulement observé dans un test historique, hérité d'un défaut SQLite ou dépendant du déploiement : `journal_mode`, `synchronous`, WAL, stockage, chemins et topologie.
3. Tracer les erreurs de COMMIT/rollback/SQLite, depuis la connexion jusqu'à la réponse HTTP et à l'état d'autorisation ; indiquer le comportement effectivement codé, pas celui attendu du contrat.
4. Confronter chaque point à AC-01..AC-14 et livrer une matrice `CONFORME DANS LE PÉRIMÈTRE` / `ÉCART ATTESTÉ` / `NON DÉMONTRÉ` / `NON APPLICABLE JUSTIFIÉ`, avec fichier, fonctions et lignes vérifiables.
5. Conclure avec **une seule recommandation** proportionnée au risque produit : aucune action si les preuves sont suffisantes, ou proposition ciblée distincte à arbitrer au 00 ; **aucun correctif implicitement autorisé**.

**Exclusions impératives :** aucune modification code ou architecture, aucun test local ou CI, aucune injection de panne, SIGKILL, instrumentation VFS/`BEFORE_DELEGATE`, campagne C03, expérimentation G04, fournisseur réel, fusion main, publication ou production. Les futures contraintes d'hébergement devront être clairement indiquées comme non qualifiées.

## Statuts conservés

- R1-C01 : **PARTIEL**, qualification globale de récupération **NON CONCLUANTE**.
- R1-RD01, R1, P0-01 : **OUVERTS**.
- C03-R01 à R04 : clôtures ciblées dans le fictif ; C03-R05 ouverte, suspendue ; C03-R06 ouverte, lots 1 et 2 reçus.
- C03-3 global, G03-R01, G03-R06, VFS-R01 : ouverts.
- B6.5 : en recette ; B6.3, G04 et production : NO-GO.

## Prochaine action unique

Transmettre au chat 02 l'audit statique ciblé des paramètres SQLite et du chemin de traitement des erreurs COMMIT, sans essai ni correctif.
