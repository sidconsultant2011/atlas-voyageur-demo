# ATLAS VOYAGEUR — B6.5 — FAÇADE SERVEUR FICTIVE V1 — RECETTE
Date : 24 octobre 2026. **IN-PROCESS MOCK UNIQUEMENT — aucun serveur HTTP, aucune API externe, aucun secret fournisseur, aucun déploiement.**

## Livrables
- `mock-server-facade.mjs` : simulateur d'opérations métier côté serveur (sessions, recherche de vol, sélection, recherche/choix d'origine, route, recommandation).
- `mock-server-facade.test.mjs` : 12 tests sur parcours nominal, isolation session, entrées invalides, budget, plafonds, cache, expiration du cache et de la session, version obsolète, refus de refresh et fermeture des opérations inconnues.
- Commande couverte par GitHub Actions : `node --test b65-calculateur/*.test.mjs`.

## Équivalents proposés, non déployés
| Opération interne mock | Futur endpoint contractuel |
|---|---|
| `createSession` | `POST /api/v1/journeys` |
| `flight.search`, `flight.select` | `/api/v1/journeys/{id}/flights/search`, `/flights/select` |
| `origin.geocode`, `origin.select` | `/api/v1/journeys/{id}/origin/geocode`, `PUT /origin` |
| `route.calculate` | `POST /api/v1/journeys/{id}/route` |
| `recommendation` | `GET /api/v1/journeys/{id}/recommendation` |
| `flight.refresh` | Rejeté 429 par construction, aucun polling réseau |

## Vérifications
- Secret de session opaque via `node:crypto randomUUID`, distinct d'un jeton propriétaire externe ; un autre token ne peut pas agir sur cette session.
- Cache de réponses fictives avec TTL : les hits ne dépensent pas de crédits simulés.
- Budget de crédits simulés : recherche AeroDataBox = 2 unités, geocoding Geoapify = 1, itinéraire Geoapify = 1. Plafond global stoppe les dépenses ; compteur de sessions limite le nombre d'appels.
- Aucun proxy d'URL, aucune permission de choisir des hôtes fournisseurs, aucun flux HTTP.
- Codes d'erreur stables : `INVALID_INPUT`, `ACCESS_DENIED`, `RATE_LIMITED`, `BUDGET_EXHAUSTED`, `STALE_STATE_VERSION`, etc.

## Limites importantes — à traiter avant prototype réseau
Ceci **n'est pas une façade sécurisée prête pour la production**. La création de session accepte encore un jeton propriétaire purement fictif : pas d'authentification serveur, de cookies HttpOnly, de CSRF ni de gestion de consentement implémentés. La signature/session, la synchronisation des compteurs, la protection concurrente de réservation des unités, le cache réparti, la limitation IP globale, la gestion des erreurs fournisseurs réelles, les TTL légaux, la suppression RGPD, le contrôle terminal et l'antifraude restent ouverts. Le cache est partagé globalement au mock et doit être revu par périmètre et type de données avant usage réel. Pas de garantie de sécurité contre un attaquant en environnement public.

Les seuls tests passés dans une exécution hors ligne de la logique du module couvrent **12 scénarios**, avant consolidation finale des identifiants de session. La réussite de la suite GitHub Actions **après le dernier commit** reste à confirmer.

## Gouvernance
**B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur main ; voyageur.atlascore.eu inchangé.** Aucun test iPhone.
