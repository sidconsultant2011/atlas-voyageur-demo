# B6.5 — Expiration temporelle automatique des informations aériennes
Date : 24 octobre 2026 · **recette hors ligne**.

## Modification
`createJourneyController({freshnessPolicy,now})` prend une politique optionnelle `{maxAgeMinutes,maxFutureSkewMinutes}` et une horloge injectable renvoyant un instant Unix en millisecondes (`Date.now` par défaut).

À chaque appel à `getState()`, le contrôleur recontrôle `latestFlightAt` par rapport à `now()`. En cas de donnée expirée, future anormale ou non horodatée, le conseil est suspendu et `FLIGHT_STALE` apparaît. L'ancien horaire ne peut pas réapparaître à la faveur d'un changement de route ou de marges. Une nouvelle observation fraîche peut rétablir le calcul.

## Compatibilité
La politique est **opt-in** pour ne pas casser les simulations historiques, dont les données fictives ne disposent pas de date d'observation. Le raccordement AeroDataBox V2 peut injecter l'horloge fictive et la politique de 30 minutes pendant la recette. Le plafond de 30 minutes est un **paramètre de test**, pas une recommandation d'intervalle de rafraîchissement fournisseur.

## Limite fondamentale
Il n'y a **aucun timer réseau ou tâche de fond**. L'expiration est réévaluée quand `getState()` est consulté : un futur écran pourra planifier une simple mise à jour locale à l'instant d'expiration (sans appel API). La page actuelle B6.5 n'utilise pas cette politique optionnelle et n'a pas été modifiée.
La donnée expirée reste présente comme preuve dans l'état, mais l'heure de départ est **null** et le statut du conseil **unavailable**.

## Tests
`journey-freshness.test.mjs` : 10 tests (fraîcheur, expiration sans réponse, seuil strict, horodatage futur, absent, rétablissement, modifications route/marges, compatibilité historique, configuration invalide).
GitHub Actions exécute `node --test b65-calculateur/*.test.mjs`. Ne pas déclarer PASS CI avant observation de la dernière exécution.

## Gouvernance
B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur main ; site public inchangé.
