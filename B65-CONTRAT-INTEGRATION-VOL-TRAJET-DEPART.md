# ATLAS VOYAGEUR — B6.5 — CONTRAT D’INTÉGRATION V1
**AeroDataBox → Geoapify → calculateur de départ**
Date : 22 octobre 2026 · Statut : **SPÉCIFICATION DE RECETTE, NON DÉPLOYÉE**.
Branche : `feature/b6-5-cartographie-interactive`. B6.3 NO-GO, aucune fusion `main`, aucun achat, aucun changement site public.

## 1. Objectif et frontières
Rendre à la personne qui accueille un voyageur : **le bon vol, le trajet depuis son adresse choisie et l'heure indicative à laquelle partir**.
Trois modules strictement séparés :
- **Vol** (adaptateur AeroDataBox via RapidAPI) : horaires, aéroports, statut, provenance des dates, date d'observation.
- **Trajet** (adaptateur Geoapify) : géocodage du point de départ libre et itinéraire voiture vers un point routable justifié à l'aéroport.
- **Planification** (moteur local métier) : calcule estimation du rendez-vous et heure de départ avec hypothèses explicites.
Pas de logique de facturation fournisseur ni de clé API dans l'UI publique. Le prototype B6.5 garde ses accès de recette séparés.

## 2. Contrat d'entrée / sortie commun
Chaque donnée externe suit :
`{ value, unit?, source, observedAtUtc, validForSeconds?, confidence: 'observed'|'estimated'|'user'|'unknown', error? }`.
Horaires **stockés comme instants ISO 8601 avec offset ou UTC**, jamais comme simple `HH:mm` pour les opérations.
`null` signifie *inconnu*, pas zéro. Les valeurs déduites ne sont pas des observations.

### FlightRecord normalisé
| Champ | Source / transformation | Obligatoire ? | Défaut/absence |
|---|---|---|---|
| `flightNumber`, `flightDateLocal` | Recherche AeroDataBox ; date locale du vol et aéroport correspondant | oui pour suivi identifié | demander sélection / ne pas créer de vol |
| `originIata`, `destinationIata` | `departure.airport.iata`, `arrival.airport.iata` | oui | désambiguïser, bloquer planification |
| `originTimezone`, `destinationTimezone` | zones IANA retournées avec les aéroports | oui pour horaires locaux fiables | UTC affiché en secours avec avertissement |
| `scheduledArrivalUtc` | `arrival.scheduledTime.utc` | souhaité | planification conditionnelle, pas de fausse précision |
| `revisedArrivalUtc` | `arrival.revisedTime.utc`, si présent | optionnel | utiliser horaire prévu, marqué provisoire |
| `actualArrivalRunwayUtc` | `arrival.runwayTime.utc` **si valide et correspondant au statut** | optionnel | aucune affirmation d'atterrissage |
| `scheduledDepartureUtc`, `revisedDepartureUtc` | `departure.scheduledTime.utc`, `departure.revisedTime.utc` | optionnel | non disponible |
| `actualTakeoffUtc` | `departure.runwayTime.utc` **seulement si qualité, cohérence et statut corroborent le décollage** | optionnel | afficher « Décollage non confirmé » |
| `status`, `lastUpdatedUtc`, `quality` | AeroDataBox : `status`, `lastUpdatedUtc`, `departure/arrival.quality` | oui pour suivi dynamique | état inconnu et dernière date disponible |
| `terminal`, `gate`, `baggageBelt` | AeroDataBox arrival (si disponibles) | non | « Non communiqué » ; ne pas inventer parking |

**Important :** `lastUpdatedUtc` décrit la fraîcheur de la source, pas une garantie de suivi temps réel. Un `runwayTime` présent et incohérent (par exemple date d'un segment différent) ne suffit pas à prouver le décollage. Les codeshares et vols multisegments doivent être désambiguïsés avec les aéroports et dates.
Les exemples antérieurs AeroDataBox comportent `scheduledTime`, `revisedTime`, `runwayTime`, `quality`, `status`, `lastUpdatedUtc`. La correspondance des champs aux endpoints et forfaits doit être testée avant consommation répétée.

### Geoapify / route
| Champ | Source | Condition et indisponibilité |
|---|---|---|
| `departureAddressText` | saisie utilisateur | jamais imposée ; ne pas persister sans consentement |
| `departureCoordinatesLonLat` | résultat sélectionné Geoapify Geocoding | sélection explicite ; l'absence bloque la route |
| `airportMeetPointLonLat`, `meetPointLabel` | référentiel interne contrôlé terminal/zone accessible | utiliser « point aéroport indicatif » tant qu'aucun lieu exact validé |
| `routeGeometry` | `features[0].geometry` Geoapify Routing | absent => pas de tracé nouveau ; pas de maintien trompeur de l'ancienne route |
| `routeDistanceMeters` | `features[0].properties.distance` | null si absence/erreur |
| `routeDurationSeconds` | `features[0].properties.time` | estimation hors trafic réel, null si indisponible |
| `routeCalculatedAtUtc` | horodatage de la réponse dans notre système | nécessaire pour affichage de fraîcheur |
| `trafficModel` | paramètre demandé + fournisseur | `none`, `approximated`, `verifiedLive`; jamais `verifiedLive` sans preuve |

**Geoapify :** `waypoints=lat,lon|lat,lon`, `mode=drive`. En GeoJSON, la géométrie est fréquemment `MultiLineString` et la durée `properties.time` (secondes), distance `properties.distance` (mètres). Certaines options de détail augmentent les crédits. Pas de trafic temps réel prétendu avec le seul routage.

## 3. Fuseaux horaires et dates
- Stocker heures opérationnelles en instants UTC ISO (`2027-05-15T15:35:00Z`) et zone IANA connue (`Europe/Paris`, `America/Los_Angeles`, etc.). Convertir via bibliothèque temporelle / Intl, jamais décaler manuellement de ±1/±2 h.
- Les dates locales du départ et de l'arrivée peuvent être différentes. Chercher le vol en respectant la date locale interprétée par l'endpoint AeroDataBox (`dateLocalRole` à documenter pour le plan choisi).
- Heure de rendez-vous et départ affichées dans la **zone de la ville de départ routier** (pour Orly : `Europe/Paris`), avec date complète si changement de jour.
- En DST (heures manquantes ou doublées), ne pas parser une heure locale sans date, offset et zone ; tester fin mars / fin octobre.
- Les `local` du fournisseur sont **pour l'affichage et le contrôle**, `utc` est la référence de calcul quand il existe.

## 4. Formule de planification et règles
Variables :
- `arrivalBasisUtc` = atterrissage confirmé si disponible **pour un rendez-vous après atterrissage** ; sinon arrivée révisée, sinon arrivée planifiée (étiquetée comme telle).
- `exitDelayMinutes` = durée de sortie + bagages / formalités **choisie par l'utilisateur ou hypothèse paramétrable**, affichée.
- `meetingMarginMinutes` = réserve choisie avant rendez-vous (si utilisée).
- `roadMinutes` = `routeDurationSeconds/60` issue de Geoapify, arrondi en entier supérieur.
- `trafficBufferMinutes` = marge circulation paramétrée ; **pas** une mesure temps réel.
- `otherTravelBufferMinutes` = marge de sécurité supplémentaire, si choisie.
Formules :
`expectedMeetingUtc = arrivalBasisUtc + exitDelayMinutes`
`recommendedDepartureUtc = expectedMeetingUtc - roadMinutes - trafficBufferMinutes - otherTravelBufferMinutes - meetingMarginMinutes`.
**Point à vérifier en recette :** la marge de rendez-vous doit être interprétée de façon cohérente : partir en avance d'autant, jamais double-compter sortie du passager, trafic ou marges.
Ne proposer d'heure de départ déterministe que si `arrivalBasisUtc`, adresse choisie, point cible, route et hypothèses sont disponibles. Sinon expliquer quelle pièce manque et proposer un calcul provisoire **clairement signalé**, si données suffisantes.
Date/heure de prochaine actualisation et incertitude affichées ; jamais promettre ponctualité exacte.

## 5. Mise à jour et gestion d'états
- `scheduled` / pas encore décollé : départ non confirmé, horaire indicatif.
- `airborne` / décollage confirmé : ETA révisée si fournie, sinon programmé ; fiabilité explicitée.
- `arrived` : comparer heure runway / atterrissage effective quand connue ; **sortie du passager non observable directement**.
- `delayed` : recalculer seulement si ETA crédible et plus récente, expliquer changement de départ.
- `cancelled`, `diverted` : suspendre conseil de départ et afficher motif.
- `unknown`, données vieillies, erreurs 400/401/403/429/5xx, timeout, vol ambigu : indicateurs « non confirmé » / « indisponible », aucun faux statut « live » ; pas de récupération en boucle qui dépense des quotas.
- Modification de l'adresse : invalidation immédiate du trajet et de l'heure conseillée précédents.
- Réponse obsolète ou désordonnée : ignorer l'ancienne mise à jour si `lastUpdatedUtc` plus ancien, sauvegarder sa provenance pour audit.

## 6. Consommation, rythme et autorisations
Journal de chaque appel pour B6.4 : `sessionId` pseudonyme, `provider`, `endpoint`, `requestAtUtc`, `httpStatus`, `unitsEstimated`, `unitsBilledOfficial` (si relevé), `cacheHit`, `followDurationSeconds`, `reason` (initial, refresh, user, error retry), sans clé ni adresse personnelle dans les journaux. Agréger par parcours sur 20 cas.
Le rythme de rafraîchissement des vols est **à fixer après quota et conditions contractuelles**, pas de valeur arbitraire intégrée maintenant.
Les droits de **réaffichage, cache, redistribution et usage commercial** AeroDataBox via RapidAPI et Geoapify sont une condition préalable au GO commercial, non réputés acquis avec les offres gratuites.

## 7. Tests d'acceptation du contrat
| ID | Test | Réussite attendue |
|---|---|---|
| I01 | Vol avec numéro, date locale et aéroports | identification non ambiguë, horaires UTC normalisés |
| I02 | Vol sans numéro via FIDS | sélection explicite, coût et plage horaire mesurés |
| I03 | Décollage réel / données contradictoires | confirmé seulement si cohérent, sinon non confirmé |
| I04 | Retard et nouvelle ETA | heure de départ recalculée, justification et source |
| I05 | Arrivée et sortie inconnue | différence entre atterrissage et sortie clairement visible |
| I06 | Adresse libre FR et hors Paris | géocodage et route de cette adresse, anciens résultats invalidés |
| I07 | Zone/terminal absent | point d'aéroport indicatif indiqué, jamais « bon terminal » inventé |
| I08 | DST et changement de jour | heures/dates correctes en zones IANA |
| I09 | Route échoue ou API 429 | pas d'ancien tracé présenté comme nouveau, coût et erreur tracés |
| I10 | Calcul avec marges | formule reproductible, pas de double comptage, unités cohérentes |
| I11 | FR/EN/RU et iPhone | aucune clé technique publique ; texte RU lisible ; heures compréhensibles |
| I12 | 20 parcours B6.4 | coût officiel et actualisations mesurés, licence vérifiée avant commercialisation |

## 8. Points non résolus et décision
- **Non livré :** adaptateur AeroDataBox connecté au trajet, actualisation réelle, moteur d'heure de départ intégré, terminal/parking exact, stockage sécurité serveur.
- **Non prouvé :** droit commercial complet, temps réel du trafic, coût unitaire moyen par parcours.
- Prochaine réalisation recommandée : **moteur de calcul et adaptateurs simulés sur données d'essai contrôlées**, puis tests fournisseurs selon quota/contrat. Pas d'appels live initiés par ce document.

B6.3 = **NO-GO**. B6.5 = **RECETTE / SPÉCIFICATION**. Aucun achat ; aucune fusion sur `main` ; `voyageur.atlascore.eu` inchangé.

ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.
