# B6.5 — Contrôleur de parcours fictif : recette

Statut : contrôleur et 17 tests de régression créés ; exécution GitHub Actions à confirmer.

## Fonction
`journey-controller.mjs` coordonne les adaptateurs AeroDataBox et Geoapify **fictifs** avec `planDeparture()`. Il conserve l'état courant d'un parcours sans réseau, stockage ou secret.

## Sécurité de cohérence
- Pas d'heure conseillée tant que vol et route ne sont pas présents.
- Une modification d'adresse appelle `invalidateRoute()` : ancien trajet et ancienne heure immédiatement annulés.
- Une nouvelle réponse route ou vol dispose d'un `requestVersion` pour ignorer la réponse d'une requête remplacée.
- Un `observedAtUtc` plus ancien que la dernière observation acceptée est ignoré pour le fournisseur concerné.
- Un changement de vol ou d'aéroport de destination invalide le trajet précédent.
- Modification des hypothèses => recalcul sans requête réseau.
- Un vol annulé, des données périmées, un trajet absent ou une hypothèse obligatoire absente suspendent le conseil.
- `getState()` renvoie des copies et ne permet pas de muter l'état interne.
- Une source ayant le même horodatage peut actuellement remplacer la précédente : arbitrage d'égalité à spécifier avant données réelles.

## Contrat d'utilisation
```js
import {createJourneyController} from './journey-controller.mjs';
const controller=createJourneyController();
controller.selectFlightFixture('delayed');
controller.selectRouteFixture('rozay');
console.log(controller.getState().recommendation.recommendedDepartureLocal);
// 15/05/2027 17:25 (selon le format local)
const oldToken=controller.getRequestVersions().routeVersion;
controller.invalidateRoute(); // conseil suspendu immédiatement
controller.selectRouteFixture('paris',{requestVersion:oldToken}); // ignoré
```

## Périmètre et limites
Les adaptateurs utilisent uniquement des fixtures. Aucun appel API n'est intégré, les prix et licences commerciaux ne sont pas validés, le réel suivi du vol n'est pas opérationnel. Les identités aériennes et les versions sont des mécanismes de recette à adapter à une session réseau future. Le même horaire fournisseur ne garantit pas la fraîcheur absolue. La preuve de réussite des tests individuels doit provenir des journaux Actions, pas seulement de l'existence des tests.

Commande automatique déjà couverte par le workflow B6.5 :
`node --test b65-calculateur/*.test.mjs`

## Gouvernance
B6.5 = recette ; B6.3 = NO-GO ; aucun achat, aucune fusion sur `main`, aucun changement du site public.
