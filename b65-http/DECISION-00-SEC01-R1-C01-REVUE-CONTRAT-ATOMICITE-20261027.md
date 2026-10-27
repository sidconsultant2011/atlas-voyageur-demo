# 00 — SEC-01 R1-C01 — GO documentaire : contrat d'atomicité et de récupération

**Date :** 27 octobre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `655834548d04cab275fbae76a7b5343db551898a`

## Contexte et sources vérifiées

Le chat 02 a remis le 27 octobre 2026 son avis indépendant sur le risque résiduel R1-C01. Sa recommandation unique est de vérifier d'abord **documentairement** le contrat de persistance et de récupération du pont d'identité, sans nouvelle instrumentation VFS ni essai de panne.

Sources du dépôt relues directement par le 00 :
- `b65-http/DECISION-00-SEC01-R1-CRITERES-20261025.md` : R1-C01 définit la prise d'effet de la révocation ; une mutation commitée avant cet instant peut être légitime, une mutation non validée ne doit pas créer d'effet postérieur illégitime.
- `b65-http/DECISION-00-SEC01-R1-RD01-PROTOCOLE-20261025.md` : protocole expérimental historiquement approuvé, sans préjuger de l'obtention d'une garantie générale.
- `b65-http/SEC01-R1-RD01-RAPPORT-EXPERIMENTAL-01-20261025.md` : essais historiques sur un banc isolé avec deux SQLite, `ATTACH`, `DELETE`, `FULL` et arrêt d'un enfant ; pas d'essai de panne OS ou matérielle.
- `b65-http/DECISION-00-SEC01-R1-HTTP-REVOCATION-CONCURRENTE-RECETTE-20261027.md` : complément HTTP concurrent officiellement réceptionné avec réserves ; **R1-C01 demeure PARTIEL**, R1-RD01, R1 et P0-01 restent ouverts.
- Décision de proportionnalité `b65-http/DECISION-00-SEC01-RD01-G03-R01-NECESSITE-PROPORTIONNALITE-20261027.md` : l'utilité obligatoire de la sonde VFS interne n'est pas démontrée.

L'avis 02 signale un risque conditionnel de récupération d'états partiels après interruption du COMMIT multi-bases, ou de disparition d'une révocation après confirmation HTTP. **Aucun état partiel réel n'est attesté comme observé.** La transaction témoin RD01 est une fixture, non une démonstration que toutes les opérations métier couplent session et identité de la même manière. L'avis 02 a effectué zéro nouveau test et aucune modification du code.

## Décision formelle

**GO DOCUMENTAIRE UNIQUEMENT — R1-C01 : REVUE DU CONTRAT D'ATOMICITÉ ET DE RÉCUPÉRATION DU PROTOTYPE LOCAL FICTIF.**

**Chantier prioritaire unique confié au chat 02 — Sécurité P0** : produire un dossier de qualification des exigences et preuves, en examinant les chemins de code applicables avant toute proposition de nouvel essai.

### Contrôles attendus, avec preuves ou qualification manquante

1. **Périmètre réel** : identifier chaque opération de révocation et mutation métier concernée, les fichiers SQLite effectivement touchés, les limites de la fixture RD01 et les relations d'atomicité réellement nécessaires pour l'autorisation.
2. **Invariants AVANT/APRÈS** : décrire pour chaque opération les états admissibles avant et après COMMIT, les états partiels interdits et le risque pour les droits. Ne pas qualifier « interdit » un état sans contrat métier pertinent.
3. **Préconditions SQLite** : déterminer, à partir des sources et paramètres vérifiables, les exigences de fichier principal sur disque, transactions `ATTACH`, modes de journalisation, exclusions WAL applicables à l'atomicité entre fichiers, `synchronous`, système de fichiers, périphériques, topologie et environnement. Distinguer configuration observée au banc et celle d'une future exploitation.
4. **COMMIT et HTTP** : vérifier par lecture du code si une réponse HTTP 200 de révocation peut précéder la réussite du COMMIT et comment sont traités les erreurs et rollbacks. Séparer ordre logique et preuve de durabilité après panne.
5. **Récupération** : préciser comment les bases sont rouvertes, comment l'état d'autorisation est recalculé et comment sont évitées les réassociations implicites.
6. **Défaut sécurisé** : formuler comme **exigence à qualifier**, et non comme acquis, le refus des opérations protégées lorsqu'une incohérence de sécurité est détectée ; déterminer si le code en fournit déjà une preuve.
7. **Matrice probatoire** : pour chaque propriété, indiquer source exacte, état `DEMONTRÉ DANS LE PÉRIMÈTRE`, `PARTIEL`, `NON DÉMONTRÉ` ou `NON APPLICABLE JUSTIFIÉ`, hypothèses et conséquences produit.
8. **Conclusion documentaire** : `GO DOCUMENTAIRE` si contrat et préconditions cohérents sans contradiction majeure, `NO-GO DOCUMENTAIRE` si contradiction critique attestée, `NON CONCLUANT` si informations ou preuves essentielles manquent. Formuler **une seule proposition de prochaine vérification proportionnée**, si elle demeure nécessaire, sans l'exécuter.

### Restrictions

Aucun changement de code ni d'architecture, migration SQLite, nouvelle campagne CI, test de panne, SIGKILL, G04, `BEFORE_DELEGATE`, instrumentation VFS ou extension C03. Aucun fournisseur réel, donnée réelle, achat, publication, fusion main ou déploiement. Le chat 02 peut consulter le code et les documents GitHub, mais ne doit pas prétendre qu'une lecture statique démontre un comportement après panne.

## Statuts préservés

- R1-C01 : **PARTIEL** ; R1-RD01, R1, P0-01 : **OUVERTS**.
- R1-C02 à C07 : recevables dans les périmètres fictifs locaux historiquement reçus.
- C03-R01 à R04 : clôturés uniquement dans leurs périmètres expérimentaux fictifs.
- C03-R05 : ouverte, campagne quantitative suspendue ; C03-R06 : ouverte, lots 1 et 2 reçus.
- C03-3 global, G03-R01, VFS-R01, G03-R06 : ouverts.
- B6.5 : en recette ; G04, B6.3 et production : NO-GO.

**Aucun GO expérimental ni GO de production ne découle du présent mandat.**

## Prochaine action unique

Transmettre au chat 02 le mandat documentaire R1-C01 pour une matrice du contrat d'atomicité et de récupération, avec critères vérifiables et une seule recommandation au 00.
