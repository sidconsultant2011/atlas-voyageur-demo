# Décision 00 — SEC-01 — Critères R1

Date : 25 octobre 2026.
Périmètre : ATLAS VOYAGEUR B6.5, prototype fictif local SQLite.
Base vérifiée avant décision : `6c0746df8d15f3134cbcad293f9303f0da5a8965`.
Référence recette : `b65-http/PV-03-SEC01-20261025.md`.

## Décision

Le pilotage 00 **approuve comme exigences de qualification** R1-C01 à R1-C07 proposées par le chat 02, et **autorise le chat 01 à développer, tester et corriger exclusivement R1** sur `feature/b6-5-cartographie-interactive`. Cette approbation **ne signifie pas que R1 est levée**.

| ID | Critère approuvé | Preuve attendue |
|---|---|---|
| R1-C01 | Point unique et observable de prise d'effet de la révocation | Contrat de cohérence documenté |
| R1-C02 | Aucun nouvel effet métier après ce point, sauf mutation validée atomiquement avant | Test d'entrelacement déterministe |
| R1-C03 | Validation de session et mutation dans une même unité de sérialisation SQLite | Analyse des transactions et verrouillages |
| R1-C04 | Pas de contournement des contrôles de propriété lors des créations, modifications ou suppressions concurrentes | Tests ciblés des trois mutations |
| R1-C05 | Toute requête protégée commencée après confirmation de la révocation est refusée | Tests HTTP et état SQL |
| R1-C06 | Cohérence sur plusieurs connexions et processus d'une même base SQLite locale | Tests multiprocessus reproductibles |
| R1-C07 | Aucune réassociation implicite, IDOR ni régression fonctionnelle | Non-régression B6.5 |

## Contrat de vérification

Une mutation validée et atomiquement enregistrée **avant** le point de prise d'effet de la révocation peut répondre plus tard, sans être un défaut. Une mutation **non validée** à cet instant ne doit pas produire d'effet métier postérieur. La réponse HTTP 200 de révocation doit intervenir après enregistrement durable de son état. Les tests doivent forcer les entrelacements par synchronisation et relire la base, pas seulement vérifier des statuts HTTP.

## Limites et garde-fous

R1 reste **OUVERTE** jusqu'à développement, exécution, preuves GitHub Actions et réception indépendante par le chat 03. R2, R3, R4 et P0-01 restent ouverts ; B6.5 reste en recette ; production NO-GO. Le résultat local SQLite ne démontre pas une garantie inter-hôtes avec bases indépendantes. Aucun achat, fournisseur réel, fusion vers `main`, publication, modification du site public ou test iPhone supplémentaire autorisé. Le chat 01 doit contrôler le HEAD avant toute mutation et fournir commits, résultats et limites. Aucun transfert automatique entre chats n'est présumé.

## Prochaine action unique

Chat 01 : implémenter et qualifier le correctif ciblé R1 selon R1-C01 à R1-C07, puis préparer le dossier de preuves pour réception par le chat 03.
