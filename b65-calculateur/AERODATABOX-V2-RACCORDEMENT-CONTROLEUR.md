# B6.5 — Raccordement AeroDataBox V2 au contrôleur — hors ligne
Date : 24 octobre 2026. Statut : **code + 13 tests ajoutés, CI à confirmer**.

## Raccordement
`aerodatabox-v2-controller.mjs` reçoit un tableau de `FlightContract` fictifs sous structure OpenAPI V2. Il sélectionne un vol sans ambiguïté et transmet un objet réduit au contrôleur de parcours existant, via l'adaptateur simulé. Aucun `fetch`, aucun token, aucun appel RapidAPI, aucune interface iPhone modifiée.

## Politique de fraîcheur de recette
- Horloge **injectée** : `nowUtc`; valeur fictive par défaut 15 mai 2027 à 14:05Z.
- Fraîcheur maximum paramétrable : **30 minutes** (valeur de test, non cadence fournisseur/production).
- Horodatage absent => `unknown`, conseil suspendu ; horodatage futur de > 2 min => `future`, conseil suspendu ; ancien => `stale`, conseil suspendu.
- Comparaison des observations par le contrôleur : réponses hors ordre et requêtes supplantées ne remplacent pas les dernières données admises.
- Ambiguïté (plusieurs vols) ou aucun résultat : refus de sélectionner arbitrairement.

## Séparation preuves / hypothèses
- Les `runwayTime` ne sont jamais passés à `actualArrivalRunwayUtc` ou `actualTakeoffUtc`.
- Ils restent seulement dans `evidence.possibleArrivalRunwayUtc` / `possibleTakeoffUtc`.
- Même avec statut `Arrived`, la date runway n'est pas « confirmée » sans règle métier supplémentaire de corroboration.
- Le calculateur peut fournir une heure **indicative** à partir de `revisedTime` ou `scheduledTime` quand la source est assez fraîche, mais ne la présente pas comme atterrissage réellement observé.
- `Canceled` et `Diverted` suspendent le conseil via le contrôleur. `CanceledUncertain` et statut inconnu sont traités comme incertains et suspendus.

## Limites
Cette politique est un banc d'essai, pas une validation de qualité réelle d'AeroDataBox. Contrôle plus poussé requis : statuts en production, qualité, fuseaux, sens « runway », date locale, codeshares, cache et licences. Le contrôleur actuel retient la dernière heure d'observation sans politique globale d'expiration tant qu'une nouvelle évaluation n'est pas demandée ; la fraîcheur **n'est pas réévaluée automatiquement à chaque seconde**. À durcir avant mode réel.

## Test et gouvernance
13 tests dédiés plus tests existants, dans `node --test b65-calculateur/*.test.mjs`.
**B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur main ; site public inchangé.**
