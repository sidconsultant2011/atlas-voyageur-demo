# 00 — B6.5 — GO de cadrage du parcours fonctionnel intégré fictif

**Date :** 1er novembre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `08c6c1ba6d745cec49b66246f9328eeae2f62455`

## Sources de décision

- Bilan indépendant remis par le chat 03 en conversation : `BILAN-03-B65-RECETTE-GLOBALE-20261101`. Le bilan est reçu en conversation ; un dépôt GitHub autonome n'est pas attesté.
- `B65-PV-ERGONOMIE-ET-CRITERES-PARCOURS.md` : recette ergonomique ciblée du 22 octobre 2026 et critères P01 à P16.
- `B65-CONTRAT-INTEGRATION-VOL-TRAJET-DEPART.md` : spécification du parcours vol / itinéraire / départ, non déployée.
- `B65-RAPPORT-MAITRE-RECETTE-TECHNIQUE-2026-10-25.md` : rapport technique historique hors ligne ; état daté distinct du HEAD.
- Pages présentes dans le dépôt : `index.html`, `RECETTE-B65-VECTORIELLE.html`, `RECETTE-B65-PARCOURS-COMPLET.html`. Modules `b65-calculateur/` présents.
- `b65-http/DECISION-00-SEC01-R1-C01-GEL-TECHNIQUE-20261101.md` : gel R1-C01 maintenu.
- GitHub contrôlé par le 00 avant décision : HEAD `08c6c1ba6d745cec49b66246f9328eeae2f62455`. Aucune nouvelle campagne de tests exécutée pour le bilan.

## Constat et frontières de preuve

Le dépôt possède déjà des éléments de simulation de vol, calcul du départ, contrôle de fraîcheur, gestion de retards/annulations, cartographie vectorielle, recherche d'adresse et routage de recette. Les essais manuels iPhone précédents prouvent certains comportements ciblés vers Orly (P05/P06/P11), non une expérience internationale intégrée. La CI n°247 sur le commit AC-13 `8ddd7678c0d23ae7c8e53af4104d0c139042397d` est une preuve de non-régression sur son périmètre, non une validation de l'expérience unifiée au HEAD documentaire actuel.

Aucun vol réel, lieu d'accueil terminal/parking vérifié, contrat commercial fournisseur, ni parcours international complet validé n'est attesté. Ne pas réouvrir le problème de cadrage/zoom iPhone sans nouvel élément.

## Décision du 00

**GO — RÉCEPTION DU BILAN DOCUMENTAIRE 03.**

**GO — CADRAGE FONCTIONNEL ET TECHNIQUE B6.5 UNIQUEMENT, SUR DONNÉES AÉRIENNES ENTIÈREMENT FICTIVES.** La priorité active suivante est la consolidation d'un parcours mobile vol fictif → adresse de départ → destination d'aéroport clairement qualifiée → trajet de recette → heure indicative de départ.

Le chat 01 est chargé de réaliser l'inventaire d'intégration **sans changement de code à ce stade** et de remettre une proposition unique de réalisation. Il doit d'abord examiner les pages de recette et modules existants et vérifier s'il existe déjà une réalisation équivalente, pour ne pas refaire le calculateur, les adaptateurs, la carte ou les acquis iPhone.

### Critères du cadrage

1. Décrire les modules et pages existants réutilisables, le parcours actuel de chaque page et ce qui manque réellement pour une interface unique. Distinguer les données de vol fictives des appels éventuels à la recette Geoapify nécessitant clé/Internet : **aucune activation supplémentaire de fournisseur réel autorisée**.
2. Proposer une expérience mobile sobre noir / or champagne, rassurante, compatible international par conception, indiquant explicitement provenance, fraîcheur des données, hypothèses et caractère fictif.
3. Maintenir horaires stockés avec date/offset ou UTC, puis affichages locaux identifiés ; prendre en compte fuseaux, changement de jour, retards, annulation, informations manquantes et erreur réseau **sans inventer de données observées**.
4. Ne pas présenter la destination actuelle Orly comme un terminal, parking ou point de prise en charge confirmé. Prévoir un libellé « point indicatif » lorsque le lieu précis n'est pas établi.
5. Utiliser la matrice P01 à P16 : identifier les critères vérifiables en mode simulé, ceux nécessitant des données réelles (notamment P01–P04 selon le PV historique), les cas déjà reçus (P05/P06/P11 ciblés) et les preuves de recette intégrée futures. Ne jamais transformer une recette fictive en GO fournisseur ou production.
6. Proposer les fichiers strictement nécessaires, les risques de régression, des tests ciblés et la revue iPhone/PC ultérieure **à exécuter seulement après GO séparé**. Proposer un seul premier lot fonctionnel minimal et ses critères de sortie.
7. Ne pas inclure de clés, jetons, données personnelles réelles ou secrets ; préserver toutes les fonctionnalités et acquis déjà validés.

### Interdictions

Aucun nouveau développement ni test n'est autorisé par cette décision. Aucun achat, crédit fournisseur, nouveau raccordement API réel, modification de `main`, du site public ou déploiement. Aucune reprise de R1-C01, C03, VFS, SIGKILL, G04 ou modification de l'architecture de sécurité. Tout besoin nouveau de service réel doit être soumis au 00 avant exécution.

## Statuts

- B6.5 : **EN RECETTE**, intégration fonctionnelle complète non réceptionnée.
- AC-08 et AC-13 : **RÉCEPTIONNÉS AVEC RÉSERVES** dans le prototype fictif local.
- R1-C01 : **PARTIEL, GEL TECHNIQUE MAINTENU** ; R1-RD01, R1 et P0-01 : **OUVERTS**.
- B6.3, G04 et production : **NO-GO**.

## Prochaine action unique

Transmettre au chat 01 le mandat de cadrage d'intégration B6.5 fictive, sans code ni essais ; soumettre ensuite une proposition unique de développement au 00.
