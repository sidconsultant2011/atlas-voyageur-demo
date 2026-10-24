# ATLAS VOYAGEUR — B6.5 — AUDIT DE PRÉ-INTÉGRATION FOURNISSEURS
Date : 24 octobre 2026. Statut : **audit documentaire, sans activation API**.

## Périmètre
Adaptateur AeroDataBox via RapidAPI, adaptateur Geoapify Geocoding/Routing/Map Tiles et API intermédiaire sécurisée. Aucune clé inspectée, aucun appel fournisseur, aucun achat. Les adaptateurs mocks existants restent seuls actifs.

## Matrice des champs
| Donnée normalisée | Source candidate | Traitement | Qualification |
|---|---|---|---|
| flightNumber, date/segment, origin/destination IATA | AeroDataBox flight status/FIDS | contrôler codeshare et date locale | endpoint et noms exacts à confirmer |
| scheduledArrivalUtc | AeroDataBox arrival scheduledTime.utc | convertir/valider instant | candidat, à prouver pour endpoint choisi |
| revisedArrivalUtc | AeroDataBox arrival revisedTime.utc | ne pas confondre estimation et observation | candidat, à prouver |
| actualArrivalRunwayUtc | AeroDataBox arrival runwayTime.utc | exiger cohérence statut + qualité ; ne pas inférer une sortie passager | candidat, à prouver |
| actualTakeoffUtc | AeroDataBox departure runwayTime.utc | corroboration statut et provenance | candidat, à prouver |
| status, lastUpdatedUtc, quality | AeroDataBox | gérer stale, unknown, cancelled, diverted ; horodatage UTC | disponibilité par endpoint à prouver |
| arrivalTerminal, baggageBelt | AeroDataBox si disponibles | null sinon, pas de parking inventé | à prouver |
| selectedDeparture | Utilisateur + Geoapify Geocoding | adresse choisie explicitement, lat/lon et provenance | format API documenté |
| routeDurationSeconds | Geoapify Routing GeoJSON features[0].properties.time | en secondes, >=0 | documenté |
| routeDistanceMeters | Geoapify Routing GeoJSON features[0].properties.distance | mètres, >=0 | documenté |
| routeGeometry | Geoapify GeoJSON features[0].geometry | généralement MultiLineString, order GeoJSON [lon,lat] | documenté |
| trafficModel | Geoapify traffic: free_flow / approximated | jamais « trafic en direct » | documenté |
| adviceUtc | Moteur ATLAS | rencontre = arrivée + délai sortie ; départ = rencontre − route − marges | mocks déjà implémentés |

## Coûts documentés
### Geoapify
- Offre Free : 3 000 crédits/jour, conditions d'attribution à respecter.
- Geocoding : 1 crédit/requête.
- Routing : 1 crédit par segment entre deux waypoints de base, options et longue distance (>500 km) peuvent accroître le coût.
- Map tiles : 0,25 crédit/demande.
- Exemple théorique (non une mesure) : 1 recherche + 1 route + 20 tuiles = **7 crédits**.
- Usage fournisseur historiquement relevé sur essais multiples : 244 demandes / 71 crédits, dont 231 demandes tuiles / 58 crédits. **Ce n'est pas un coût unitaire par voyageur.**

### AeroDataBox via RapidAPI
- Basic affiché : 400 API Units/mois et 1 600 requests/mois, hard limits.
- Tier 1 = 1 unité/requête ; Tier 2 = 2 ; Tier 3 = 6. Options spéciales (flight plans) peuvent multiplier les unités.
- **Bloquant :** fixer la liste réelle des endpoints (status vol exact, FIDS sans numéro, rafraîchissement) et leur tier, puis confirmer conditions de cache/retention/affichage et usage commercial.
- Ne pas extrapoler un tarif moyen pour un accueil tant que le nombre d'actualisations n'est pas défini.

## Architecture et protections obligatoires
1. Façade côté serveur pour AeroDataBox avec secret RapidAPI uniquement dans variables serveur, jamais HTML/JS public ni logs.
2. Pour Geoapify geocoding/routing : façade serveur, cache contrôlé, minimisation de l'adresse personnelle, durée de conservation à définir.
3. Pour tuiles MapLibre : clé séparée et restreinte aux origines autorisées, ou proxy avec contrôle des charges. Une clé embarquée navigateur **n'est pas secrète**.
4. Contrôle des coûts : quotas par session/utilisateur, rate limiting, backoff encadré sur 429/5xx, aucune boucle de polling infinie ; budget plafond avant tout GO.
5. Réponses horodatées en UTC, timezone IANA pour affichage, indication « données reçues à… », état périmé et refus de conseil trompeur.
6. Versioning requête/état du contrôleur : ignorer anciens résultats et invalider trajet lors de changement d'adresse, vol ou destination.
7. Attribution : Geoapify + OpenStreetMap / OpenMapTiles selon affichage, et termes AeroDataBox/RapidAPI avant redistribution.
8. Tests sécurité : aucune clé dans console, source HTML, bundles, URLs partagées, traces analytics, messages d'erreur, artefacts ou GitHub. Les requêtes Geoapify navigateur avec clé dans URL requièrent contrôle spécifique.
9. Architecture QA/test entièrement séparée de main et site public. Ne pas brancher les fournisseurs sans nouveau GO.

## Décisions NO-GO et critères de sortie
- **NON QUALIFIÉ :** schéma exact et tiers des endpoints AeroDataBox nécessaires ; coût par parcours réel y compris refresh ; conditions de conservation/redistribution ; volume réel tuiles/session ; conception backend et garde-fous clés.
- Passer en réalisation seulement après matrice endpoints et champs validée, banc de 20 parcours à budget encadré, revue sécurité, et accord explicite du pilotage.
- Les fixtures mock et CI sont une preuve de cohérence logique, **pas** une preuve de comportement des API réelles.

## Sources officielles consultées
- https://aerodatabox.com/api-spec
- https://doc.aerodatabox.com/rapidapi.html
- https://rapidapi.com/aedbx-aedbx/api/aerodatabox/pricing
- https://apidocs.geoapify.com/docs/geocoding/
- https://apidocs.geoapify.com/docs/routing/
- https://apidocs.geoapify.com/docs/maps
- https://www.geoapify.com/pricing/

## Gouvernance
**B6.5 en recette — B6.3 NO-GO — aucun achat — aucune fusion sur main — site public voyageur.atlascore.eu inchangé.**
ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.
