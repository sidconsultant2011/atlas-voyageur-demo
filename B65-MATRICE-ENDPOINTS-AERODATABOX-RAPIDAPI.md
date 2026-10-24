# ATLAS VOYAGEUR — B6.5 — MATRICE ENDPOINTS AERODATABOX RAPIDAPI V1
Date : 24 octobre 2026 · **DOC SEULEMENT — NO-GO API LIVE**.

## Sources de vérité
- Spécification OpenAPI officielle RapidAPI : https://doc.aerodatabox.com/docs/openapi-rapidapi-v1.json (consultée, version exposée v1.15.1.0 ; le portail HTML peut présenter une version différente, à revérifier avant intégration).
- Pricing RapidAPI Basic : https://rapidapi.com/aedbx-aedbx/api/aerodatabox/pricing
- Portail RapidAPI : https://rapidapi.com/aedbx-aedbx/api/aerodatabox
Aucun appel endpoint réel, aucun secret consulté ni achat.

## Matrice des endpoints utiles (GET)
| Priorité | Besoin | Chemin de la spécification | Tier | Basic unités/appel | Champs / structure de réponse documentés | Statut |
|---|---|---|---|---:|---|---|
| P0 | Recherche par numéro sur date locale | `/flights/{searchBy}/{searchParam}/{dateLocal}` (`searchBy=number`) | 2 | 2 | tableau `FlightContract[]` : `number`, `status`, `lastUpdatedUtc`, `departure`, `arrival`, `codeshareStatus` | Confirmé par OpenAPI, données à valider par aérodrome |
| P0 | Recherche du vol à date la plus proche (repli limité) | `/flights/{searchBy}/{searchParam}` | 2 | 2 | même tableau `FlightContract[]`, vol à date proche et risque d'ambiguïté | Confirmé ; ne pas substituer à date explicite |
| P0 | Sans numéro — tableau arrivées par plage locale | `/flights/airports/{codeType}/{code}/{fromLocal}/{toLocal}` | 2 | 2 | `AirportFidsContract` : horaires/statuts potentiels ; `direction=Arrival`, filtres `withCancelled`, `withCodeshared`, `withLeg` | Confirmé ; plage Basic max 12h |
| P1 | Sans numéro — tableau horaire relatif | `/flights/airports/{codeType}/{code}` | 2 | 2 | `AirportFidsContract` ; `offsetMinutes`, `durationMinutes`, filtres | Confirmé ; utile uniquement pour fenêtre proche du moment |
| P1 | Autocomplétion numéro de vol | `/flights/search/term` (`q`, `limit`) | 2 | 2 | liste de `FlightSearchItemContract` avec `number` | Confirmé ; jamais appeler à chaque frappe sans anti-rebond |
| P1 | Métadonnées d'aéroport | `/airports/{codeType}/{code}` | 1 | 1 | `AirportContract`, codes IATA/ICAO, nom, lieu, métadonnées | Confirmé ; cache à durée autorisée |
| P0 QA | Vérifier couverture des actualisations d'un aéroport | `/health/services/airports/{icao}/feeds` | Free Tier | 0* | `FeedServiceStatusContract`, `service` + `status` | Confirmé ; *vérifier note Free Tier et quota de requêtes |
| P2 | Historique d'un vol sur intervalle | `/flights/{searchBy}/{searchParam}/{dateFromLocal}/{dateToLocal}` | 3 | 6 | liste d'enregistrements de vol | Hors MVP |
| P2 | Recherche de dates d'exploitation | Famille `/flights/{searchBy}/{searchParam}/dates...` (chemins à vérifier avant codage) | 2 d'après section spécification | 2 | listes de dates locales | Hors MVP, chemin volontairement non figé |
| P2 | Alertes PUSH webhooks | Flight Alert API ; souscriptions | coût distinct | à qualifier | notifications `FlightNotificationItemContract` | Hors MVP ; souscription séparée du quota ordinaire |

**Précision :** pas de Tier 1 supposé pour « Flight Status » : la spécification le classe **Tier 2 = 2 API units**. La voie FIDS est aussi Tier 2. Les données d'arrivée ou de décollage en direct dépendent de la couverture locale : un champ présent dans le schéma n'est pas nécessairement renseigné.

## Champs exacts FlightContract et types
- Racine : `number`, `status`, `codeshareStatus`, `lastUpdatedUtc`, `departure`, `arrival`, `isCargo`. Optionnel : `callSign`, `aircraft`, `airline`, `location`, `flightPlan`.
- `departure` / `arrival` = `FlightAirportMovementContract` : `airport`, `quality`, `scheduledTime`, `revisedTime`, `predictedTime` (expérimental selon endpoint), `runwayTime`, `terminal`, plus données opérationnelles optionnelles.
- Les horaires sont objets `DateTimeContract` (UTC et local selon disponibilité). Toujours baser l'arithmétique sur `utc` présent et valide ; défaut `null` si absent.
- `revisedTime` peut désigner estimation/réel à la porte ou à la piste. **Ne pas coder équivalence automatique « revisedTime = heure de piste ».**
- `runwayTime` peut être réel **ou estimé** : la seule présence ne prouve pas un atterrissage/décollage. Il faut croiser `status`, `quality` et les autres dates. Le champ `confirmed` des mocks B6.5 **n'existe pas comme preuve contractuelle officielle**.
- `lastUpdatedUtc` date la dernière mise à jour des données du vol, **hors position**. Indiquer la fraîcheur et résister aux réponses hors ordre.
- `airport` est un objet aéroport, pas nécessairement un simple champ `iata` à la racine. Codeshare, date locale, aéroports doivent être rapprochés avant sélection.
- Terminal, gate et bagages sont optionnels, ne jamais inventer un point de parking.

## Tarification du forfait Basic (RapidAPI, état affiché au 24/10/2026)
- 400 **API Units / mois**, plafond dur ; 1 600 **Requests / mois**, plafond dur ; **1 000 requêtes/heure**.
- Tier 1 : 1 unité ; Tier 2 : 2 unités ; Tier 3 : 6 unités ; Free Tier : 0 unité (sous note fournisseur).
- FIDS / airport departures-arrivals : fenêtre de **12 heures** par page en Basic.
- Récupérer les flight plans avec un Flight Status peut **multiplier x2 les unités** ; ne pas demander les flight plans.
- Attribution **obligatoire** sur Basic ; cache/rétention standard **7 jours**.
- Les cases de permission d'usage commercial / sous-licence B2B et les restrictions de réaffichage doivent être confirmées dans les termes complets ; ne pas considérer l'abonnement gratuit comme une licence de commercialisation.
- Hypothèse mathématique indicative : **une recherche numéro = 2 unités**, une FIDS = 2 ; 400 unités permettraient au maximum 200 de ces appels si aucune autre consommation. En vrai, rafraîchissements, autres endpoints, limites, éventuelles facturations supplémentaires réduisent ce plafond. Aucun modèle de pack vendu ne doit en être déduit.
- Pas de planning de polling fixé : imposer stratégie de budget et règles des conditions fournisseur avant activation.

## Conditions de sécurité et d'usage
- Clé RapidAPI **uniquement côté serveur**, headers `X-RapidAPI-Key` et `X-RapidAPI-Host: aerodatabox.p.rapidapi.com` ; jamais exposée au navigateur.
- Mettre une façade serveur avec quotas de session, cache contrôlé, anti-rebond sur FIDS et autocomplétion, alertes quotas, protection contre requêtes abusives, backoff raisonnable et pas de boucle infinie.
- Ne pas loguer clés ni données personnelles identifiantes ; journaliser les unités imputables et le motif de chaque appel.
- Rendre visibles les états `scheduled-only`, `live-updated`, `coverage unknown`, `stale`; ne pas écrire « live » par défaut.
- En cas de résultat multiple, ne jamais en choisir un sans confirmation explicite.
- Les alertes PUSH ont **leur propre facturation/crédits** ; pas de décision d'usage maintenant.

## Points encore ouverts et GO
- Vérification directe d'échantillons de **réponses réelles** en QA (avec budget autorisé) indispensable avant de figer l'adaptateur : champs facultatifs, statut, qualité, heures piste/porte, terminal, position.
- Préciser schema complet `AirportFidsContract` et `FlightStatus` enum au moment du mapping de production.
- Contrôler conditions commerciales et couverture réelle des aéroports visés avant déploiement.
- Aucun lancement API, aucune modification des fixtures mocks, du site public ou de `main`.

**Gouvernance : B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion main ; voyageur.atlascore.eu inchangé.**
ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.
