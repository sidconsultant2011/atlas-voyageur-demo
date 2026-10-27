# Décision 00 — SEC-01 — Nécessité et proportionnalité G03-R01 / C03

**Date :** 27 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `e240bb01a48c27511072e9d63f9b9993518b7476`  
**Autorité :** 00 — Pilotage et gouvernance.

## Objet et vérifications

Le chat 02 a remis le 27 octobre 2026 un avis documentaire indépendant intitulé `Nécessité et proportionnalité de G03-R01 et du dispositif C03`, sans nouveau test ni modification du dépôt. Il conclut que la sécurité P0-01 est indispensable, mais que l'instrumentation causale interne de COMMIT SQLite via G03-R01 / C03 n'est **pas démontrée indispensable** à la satisfaction des exigences R1.

Sources GitHub revérifiées directement par 00 :
- `b65-http/DECISION-00-SEC01-R1-CRITERES-20261025.md`, approbation des sept exigences R1-C01 à C07 : prise d'effet de la révocation, absence de mutation illégitime ultérieure, sérialisation SQLite, contrôle des propriétaires, refus HTTP après révocation, cohérence entre connexions/processus, réassociation et IDOR.
- `b65-http/SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md` : G03-R01 recherche une liaison transaction multi-bases / super-journal / invocation VFS `xDelete` et `BEFORE_DELEGATE`, avec absence de modification de la sémantique SQLite et sans confondre COMMIT logique et durabilité physique.
- `b65-http/DECISION-00-SEC01-RD01-C03-R06-LOT2-RECEPTION-20261027.md` : C03-R06 lot 2 techniquement reçu pour recette indépendante 03, non clôturé.
- Dernier HEAD contrôlé au moment de la présente décision : `e240bb01a48c27511072e9d63f9b9993518b7476`.

**Constat documentaire :** aucune des exigences R1-C01 à R1-C07 ne prescrit explicitement une observation causale `xDelete` ou `BEFORE_DELEGATE`. Les garanties métier requièrent d'abord des preuves transactionnelles SQL, des rejets HTTP, des contrôles de concurrence et de propriété et des états persistants. Les essais de reprise sur panne ont une finalité distincte. Cela ne démontre ni la suffisance actuelle des alternatives ni l'inutilité générale de G03-R01.

## Arbitrage formel du 00

**GO DOCUMENTAIRE : avis de proportionnalité retenu.**

**SUSPENSION DE TOUTE NOUVELLE EXTENSION TECHNIQUE C03/G03-R01 APRÈS LE LOT 2 C03-R06 DÉJÀ ENGAGÉ**, tant qu'une nécessité probatoire complémentaire n'est pas démontrée. Aucun lot 3, nouvelle instrumentation `BEFORE_DELEGATE`, campagne quantitative C03-R05, SIGKILL, injection de panne ou G04 n'est autorisé.

### Critère de réouverture en quatre conditions cumulatives

1. **Risque produit explicite :** définir un scénario de défaillance pertinent pour la révocation, l'identité ou une mutation non autorisée, dont les conséquences réelles justifient l'effort.
2. **Nécessité de la preuve interne :** démontrer que la couverture du scénario exige de connaître le passage d'un point causal interne identifié du COMMIT multi-bases, plutôt qu'une simple observation de l'état observable.
3. **Insuffisance des autres moyens :** documenter pourquoi les tests SQL, HTTP, de sérialisation, de concurrence, de récupération et de cohérence persistante ne suffisent pas à l'assurance attendue.
4. **Faisabilité et proportionnalité :** démontrer que l'instrumentation peut obtenir une preuve recevable sans dégrader les invariants pertinents, pour un coût et un risque justifiés ; la neutralité temporelle C03-R05 reste non qualifiée.

Si l'une de ces conditions manque, **la nécessité de G03-R01 demeure non démontrée** et aucune poursuite automatique de C03 n'est décidée. Ne pas transformer la suspension du moyen expérimental en clôture de l'exigence de sécurité.

## Maintien des travaux en cours et des statuts

**Chantier prioritaire actif unique : recette indépendante C03-R06 lot 2 par le chat 03**, conformément à la décision déjà enregistrée. Cette décision stratégique n'ouvre pas de second chantier technique et ne remplace pas le PV indépendant attendu.

- C03-R01 à R04 : clôturées seulement dans leurs périmètres fictifs expérimentaux.
- C03-R05 : ouverte, qualification quantitative suspendue faute de budget B justifiable.
- C03-R06 : ouverte, lot 1 reçu, lot 2 en attente de recette indépendante.
- C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 : ouverts.
- B6.5 : en recette ; G04, B6.3 et production : NO-GO.
- L'avis ne valide pas une architecture de remplacement, n'atteste pas un audit exhaustif du code courant, et ne clôture aucun P0.
- Aucun changement du code, nouveau test, fournisseur réel, fusion main, publication, déploiement ou achat autorisé.

## Prochaine action unique

Obtenir du chat 03 le procès-verbal indépendant **C03-R06 lot 2** déjà mandaté, avant de réexaminer au 00 l'ordre des chantiers au regard des besoins de sécurité et du produit.
