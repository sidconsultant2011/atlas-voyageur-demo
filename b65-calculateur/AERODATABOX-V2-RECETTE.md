# ATLAS VOYAGEUR — AeroDataBox V2 hors ligne — contrat et tests

Date : 24 octobre 2026. Branche : `feature/b6-5-cartographie-interactive`.
**Statut : normalisation OpenAPI V2 écrite ; validation CI de cette version non encore confirmée.** Aucun appel AeroDataBox / RapidAPI.

## Source
Schéma officiel AeroDataBox RapidAPI OpenAPI v1.15.1.0 :
https://doc.aerodatabox.com/docs/openapi-rapidapi-v1.json
Schémas : `FlightContract`, `FlightAirportMovementContract`, `DateTimeContract`, `FlightStatus`.
Le endpoint Flight Status (single day) renvoie **un tableau de FlightContract**, pas obligatoirement un vol unique.

## Entrée
- `normalizeAeroDataBoxV2(raw)` accepte un objet FlightContract conforme dans ses grandes lignes.
- `selectAeroDataBoxFlightV2(array,{number,originIata,destinationIata})` filtre des réponses ; si 0 résultat => `not_found`, si plusieurs => `ambiguous`, jamais choix arbitraire.
- L'adaptateur ne fait pas de requête HTTP, ne lit pas de clé, ne stocke rien.

## Champs
- Identité : `number`, `codeshareStatus`, `status`, `lastUpdatedUtc`, `departure.airport.iata`, `arrival.airport.iata`.
- Horaires : `arrival.scheduledTime.utc`, `revisedTime.utc`, `predictedTime.utc` et `runwayTime.utc`; idem côté départ pour conservation de preuve.
- Terminal facultatif, qualité brute conservée quand de type chaîne. Si source fournit un autre objet/enum qualité, le mapping sera spécifié après qualification.
- Les heures UTC sont converties en ISO 8601 normalisé. Les heures `local` ne sont **jamais** interprétées seules comme UTC.
- Une donnée absente/invalide est `null`, avec motifs `uncertainty`. Aucun horaire 00:00 fictif.

## Distinguer preuve et estimation
La spécification décrit `runwayTime` comme heure **réelle ou estimée**.
L'adaptateur expose `possibleArrivalRunwayUtc` et `possibleTakeoffUtc` comme indices, mais **`actualArrivalRunwayUtc = null` et `actualTakeoffUtc = null`** tant que les règles de corroboration ne sont pas établies. Même lorsque `status=Arrived`, aucun faux « piste confirmée » n'est déduit.
Le mapping vers le moteur `planDeparture()` sera une étape ultérieure, après définition des règles de confiance. Pour l'instant, V2 est **isolé des mocks et de la page iPhone**.

## Statuts OpenAPI mappés
`Unknown`→unknown ; `Expected`/`CheckIn`/`Boarding`/`GateClosed`→scheduled ; `EnRoute`/`Departed`/`Approaching`→airborne ; `Delayed`→delayed ; `Arrived`→arrived ; `Canceled`→cancelled ; `Diverted`→diverted ; `CanceledUncertain`→uncertain.
Statut non reconnu => unknown, sans interprétation optimiste.

## Tests
`aerodatabox-v2.test.mjs` : **12 tests définis** couvrant tous les états, heures UTC, local sans UTC, absence de champs, incertitude runway, mise à jour invalide, résultat multiple ou manquant.
Le workflow déjà présent exécute tous les tests `b65-calculateur/*.test.mjs` sur push de cette branche. **Vérifier le PASS GitHub Actions avant de déclarer le lot validé.**

## GO / NO-GO
Pas de client HTTP, pas de clé, pas d'intégration live, pas de coût supplémentaire.
**B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur main ; site voyageur.atlascore.eu inchangé.**
