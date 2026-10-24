# B6.5 — Adaptateurs fictifs — recette automatique

Statut : **mocks créés**, exécution GitHub Actions post-commit **à confirmer**. Aucune requête fournisseur.

## Fichiers
- `mock-adapters.mjs` : données fictives AeroDataBox et Geoapify, normalisations et garde-fous.
- `mock-integration.mjs` : composition des deux adaptateurs avec `planDeparture()`, sans I/O.
- `mock-integration.test.mjs` : 13 scénarios contrôlés.
- `atlas-depart-engine.test.mjs` : 12 scénarios unitaires historiques.

## Contrat et limites
- Vol fictif `AV103` ; arrivée prévue, révisée, atterrissage confirmé, annulé, données périmées, arrivée absente et horodatage non confirmé.
- Itinéraires simulés : Rozay-en-Brie 45 min / Paris centre 20 min ; aucun géocodage ni carte réelle.
- Paramètres par défaut : sortie 40 min, marge circulation 15 min, autre marge 5 min et avance 0.
- Attendu nominal retardé : 17h25, le 15 mai 2027 heure de Paris.
- Valeurs fournisseur absentes/invalides deviennent `null` et déclenchent suspension de calcul.
- Le `runwayTime` n'est considéré « confirmé » **que dans la fixture** s'il est explicitement marqué confirmé et que le statut correspond. Ce champ `confirmed` est propre aux mocks : il ne doit jamais être présenté comme champ réel certifié AeroDataBox.
- Invariant : aucun `fetch`, aucun secret, aucune API, aucune dépense fournisseur ; `mock-adapters.mjs` ne doit pas être interprété comme un mapping de champs officiellement validé par AeroDataBox.
- Les tests définis (12 + 13) vérifient la logique ; le résultat de leur exécution sur GitHub reste à vérifier.

## Commande de recette
```bash
node --test b65-calculateur/*.test.mjs
```
Le workflow GitHub Actions B6.5 exécute désormais les deux fichiers de tests. En cas d'échec, examiner le job avant toute nouvelle modification.

## Gouvernance
B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion main ; site public inchangé.
