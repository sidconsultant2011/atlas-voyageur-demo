# ATLAS VOYAGEUR — B6.5 — CONTRAT FAÇADE SERVEUR SÉCURISÉE V1
Date : 24 octobre 2026. **SPÉCIFICATION UNIQUEMENT, AUCUN CODE RÉSEAU NI DÉPLOIEMENT.**
Statut : DRAFT / NO-GO fournisseurs réels.

## 1. Mission et frontières
Façade privée entre l'interface ATLAS VOYAGEUR et AeroDataBox (RapidAPI), Geoapify geocoding/routing, et éventuellement tuiles.
Ne jamais exposer de secret fournisseur, d'unités facturées ou de panneau développeur dans l'interface publique.
La façade ne modifie pas le contrôleur métier B6.5 : elle normalise les données, contrôle identité/session, coûts et fraîcheur, et transmet des résultats contractuels.
Ne pas exposer un proxy universel d'URL ; seuls les endpoints explicitement autorisés sont admis.

## 2. Routes internes proposées (versionnées)
Toutes préfixées `/api/v1`. Toutes les routes ci-dessous restent **NON IMPLÉMENTÉES**.

| Méthode / route | Entrée validée | Sortie attendue | Budget et limites |
|---|---|---|---|
| `POST /journeys` | consentement opérationnel, langue `fr/en/ru`, mode `flight` | `journeyId` opaque, expiration de session | 1 création par intention ; anti-abus |
| `POST /journeys/{id}/flights/search` | numéro/date locale/aéroports OU destination/date/plage ; liste blanche | candidats avec provenance, statut et fraîcheur | recherche explicite, dédoublonnée ; pas de recherche sur chaque frappe |
| `POST /journeys/{id}/flights/select` | identifiant opaque d'un candidat appartenant à la session | vol normalisé + `flightVersion` | pas d'appel fournisseur si candidat déjà en cache valable |
| `GET /journeys/{id}/flight` | `If-None-Match` facultatif | état vol connu, `observedAtUtc`, `expiresAtUtc`, `quality`, `version` | lecture locale cache avant toute actualisation fournisseur |
| `POST /journeys/{id}/flight/refresh` | demande explicite et jeton de version | nouvelle observation ou `nextAllowedAtUtc` | rate limit + budget mensuel + cooldown + cache |
| `POST /journeys/{id}/origin/geocode` | texte adresse, longueur bornée, session autorisée | au plus 5 résultats sélectionnables, pas de choix silencieux | anti-rebond côté UI + plafond par session |
| `PUT /journeys/{id}/origin` | identifiant résultat géocodage / coordonnées contrôlées | origine validée + `originVersion` ; invalide route/conseil | aucun appel fournisseur |
| `POST /journeys/{id}/route` | `originVersion`, aéroport/lieu cible autorisé, mode `drive` | distance m, durée sec, géométrie optionnelle, `routeVersion` | cache par points normalisés, plafond appels |
| `GET /journeys/{id}/recommendation` | option d'affichage IANA | conseil indicatif ou suspendu + raisons et horodatages | calcul serveur/local pur : **0 appel fournisseur** |

Proposition : les chemins externes ne sont jamais acceptés depuis la requête publique ; l'implémentation choisit les endpoints fournisseurs fixes à partir des opérations validées.

## 3. Enveloppe de réponse
```json
{
  "schemaVersion": "1",
  "journeyId": "opaque-id",
  "requestId": "opaque-trace-id",
  "stateVersion": 3,
  "status": "ok|partial|unavailable",
  "data": {},
  "source": {"provider": "aerodatabox|geoapify|atlas", "observedAtUtc": null, "expiresAtUtc": null, "confidence": "observed|estimated|unknown"},
  "errors": [],
  "limits": {"nextAllowedAtUtc": null}
}
```
La réponse `recommendation` inclut `recommendedDepartureUtc` **ou null**, `arrivalKind`, `roadDurationSeconds`, `assumptions`, `freshness`, `reasons`. Ne jamais renvoyer `actualArrivalRunwayUtc` sans corroboration de source indépendante et règle qualifiée.
Date UTC ISO-8601 stricte, fuseau IANA uniquement pour affichage ; unités explicites ; absent = null.

## 4. Authentification et protection des sessions
- Session signée ou jeton éphémère opaque, non prédictible, expiration et rotation ; cookie `Secure; HttpOnly; SameSite=Lax/Strict` pour web, et CSRF si auth cookie.
- Authentification utilisateur/payante future séparée du contrôle d'accès aux sessions ; empêcher consultation ou écriture inter-sessions (IDOR).
- CORS en liste blanche pour les origines QA autorisées ; jamais `*` avec credentials ; HTTPS strict, CSP, validation Origin/Referer en défense supplémentaire (pas une authentification).
- Validation de toutes les entrées, limites de longueur et cardinalité, aéroports IATA/ICAO autorisés, horaires et plages bornés, type MIME JSON, limite taille requête.
- Rate limits par session, utilisateur, IP/anomalie et budget global fournisseur ; sécurité anti-bot adaptée avant exposition.
- Aucun endpoint permettant de choisir arbitrairement hôte, URL, port ou protocole fournisseur (SSRF).
- Secrets `RAPIDAPI_KEY`, `GEOAPIFY_SERVER_KEY` dans coffre/variables chiffrées serveur seulement ; séparation QA/prod, rotation, révocation, jamais dans JS, HTML, URL d'analytics ou journaux.
- Map tiles : une clé client **est publique** si visible dans le navigateur ; restreindre domaine, quotas et clés distinctes ou utiliser un proxy spécifique budgété. Vérifier attribution et licence.

## 5. Quotas, consommation et cache : politique initiale à valider
**Valeurs ci-dessous : hypothèses de conception, pas limites fournisseur ni autorisation d'achat.**
- Séparer deux compteurs : `requestCount` et `apiUnitsUsed` chez AeroDataBox, `geoapifyCreditsUsed` chez Geoapify. Incrémenter d'après endpoint/tier, rapprocher avec relevés fournisseurs.
- Pré-budgétiser chaque appel et réserver des unités de manière atomique avant la requête ; refuser si plafond atteint. Réconcilier après facturation réelle.
- Exemple de garde-fous QA candidats : au maximum 2 recherches vol/min/session, 5 géocodages/10 min/session, 3 routages/10 min/session, 1 actualisation vol/5 min/session, uniquement si budget disponible. **À ne pas implémenter sans arbitrage.**
- Cache partagé avec clé incluant provider, endpoint, paramètres normalisés, date locale, segment et scope légal ; TTL différenciés selon état du vol et conditions contractuelles. Aucun TTL arbitraire pour un vol en cours tant que couverture et droits fournisseur non validés.
- Distinguer `observedAtUtc` (fraîcheur source), `retrievedAtUtc` (notre lecture), `expiresAtUtc` (notre politique) ; le cache ne doit pas prolonger artificiellement une donnée périmée.
- Cache/déduplication d'appels concurrents (singleflight), `ETag` pour lecture interne, versioning `flightVersion` et `routeVersion` pour écarter réponses hors ordre.
- Geoapify : tuiles 0,25 crédit/tuile en contexte de base ; Geocoding ~1 crédit, Routing simple ~1 crédit (selon options et limites). AeroDataBox : tiers 1/2/3 = 1/2/6 unités, **vérifier le tier de chaque endpoint effectivement utilisé**.
- Plafond financier fournisseur global = `HARD_STOP`; empêcher que des retries ou un écran laissé ouvert engendrent une dette.

## 6. Politiques d'erreurs et résilience
| Cas | HTTP interne | Comportement |
|---|---:|---|
| Entrée invalide / plage date excessive | 400 | code stable `INVALID_INPUT`, aucun appel fournisseur |
| Session absente | 401 | `AUTH_REQUIRED` |
| Session d'autrui / fonction interdite | 403 ou 404 | `ACCESS_DENIED` sans fuite de détails |
| Vol introuvable | 404 | `FLIGHT_NOT_FOUND`, distinguer indisponibilité données |
| Plusieurs vols | 409 | `AMBIGUOUS_FLIGHT`, candidats filtrés |
| Version obsolète | 409 | `STALE_STATE_VERSION`, invalider ancien résultat |
| Budget dépassé | 429 | `BUDGET_EXHAUSTED`, arrêt des appels |
| Rythme dépassé | 429 | `RATE_LIMITED`, `Retry-After` calculé localement |
| Fournisseur inaccessible/timeout | 502/503/504 | `PROVIDER_UNAVAILABLE`, ne pas présenter cache périmé comme nouveau |
| Résultat partiel | 200 `partial` ou 503 selon endpoint | indiquer champs inconnus, désactiver conseil si critique |

Retry borné sur erreurs transitoires uniquement, backoff/jitter, jamais sur 400/401/403, pas de boucle illimitée et aucun secret dans les messages. Circuit-breaker sur échecs répétés.

## 7. Confidentialité, observabilité et audit
- Adresse privée = donnée personnelle : minimiser, durée de rétention courte à définir, suppression explicite, RGPD et politique de confidentialité avant usage public.
- Traces par identifiant de parcours pseudonyme et `requestId`, sans texte d'adresse, clé, numéro de téléphone ou identité du voyageur.
- Métriques : endpoints, cache-hit, statut fournisseur, latence, consommations estimées/officielles, actualisations, taux 429, suspension sur données périmées, nombre de trajets.
- Journal de sécurité séparé, accès limités, conservation documentée, purge automatique.
- Aucun composant de débogage/facturation exposé dans UI end-user.

## 8. Critères de validation avant développement réseau
1. Sign-off sur schémas de requête/réponse, gestion sessions, versionnage et codes erreurs ; tests mocks contractuels.
2. Vérification des droits commerciaux AeroDataBox/RapidAPI et Geoapify (stockage, réaffichage, licences tuiles, attribution).
3. Matrice coûts par endpoint et budgets tests — B6.4 20 parcours, incluant rafraîchissements.
4. Choix plateforme et architecture de coffre des secrets, pas de clé client RapidAPI.
5. Tests adversariaux : cache périmé, IDOR, quotas, SSRF, CSRF, injection, race conditions, collisions, appels répétés, vol ambigu.
6. Approbation explicite d'activation réseau distincte d'une validation QA.

## 9. État et décision
**Contrat proposé, non implémenté.** Aucun serveur, endpoint réseau, clé, quota ou cache effectivement déployé.
B6.5 reste une branche de recette ; B6.3 NO-GO ; pas d'achat, pas de fusion sur `main`, site public `voyageur.atlascore.eu` inchangé.

ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.
