# 01 — B6.5 — Cadrage du parcours intégré fictif

**Date :** 1er novembre 2026. **Nature :** étude et proposition, aucun code modifié, aucun test exécuté.  
**Dépôt :** `sidconsultant2011/atlas-voyageur-demo`. **Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD contrôlé avant étude :** `dc04f18331d946fc7ba75d3c36af24a7169fd6b2`.  
**GO de cadrage :** `B65-DECISION-00-CADRAGE-PARCOURS-INTEGRE-FICTIF-20261101.md`.  
**Référentiels :** `B65-PV-ERGONOMIE-ET-CRITERES-PARCOURS.md` (P01–P16), `B65-CONTRAT-INTEGRATION-VOL-TRAJET-DEPART.md` (I01–I12).  
**Restriction :** ni tests nouveaux ni modification applicative ; aucun branchement réel aux fournisseurs.

## 1. Constat du dépôt — réutiliser plutôt que recommencer

| Composant existant au HEAD cité | Acquis observé dans le code | Frontière ou manque à combler |
|---|---|---|
| `index.html` et `i18n.js` | Parcours public préexistant « retrouver / choisir / accueillir », recherche du vol fictif `DEMO001`, trois langues FR/EN/RU et écran de calcul autonome | Page **publique** et calcul simplifié non câblés au contrôleur B6.5 ; **ne pas modifier** cette page ni le site dans ce lot |
| `RECETTE-B65-PARCOURS-COMPLET.html` | Page QA mobile **déjà intégrée** aux modules `createJourneyController` et `formatLocal`, scènes retard, atterrissage, prévu, annulé, manquant, périmé ; route schématique et hypothèses utilisateur | Origine choisie par liste « Rozay / Paris » et **pas de saisie/recherche libre**, pas de carte routière, pas de sélection vol avec critères de provenance/destination clairement exposés, pas de borne réseau dans ce même parcours |
| `b65-calculateur/journey-controller.mjs` | `setFlight`, `setRoute`, sélection de fixtures, invalidation de route, versions de requêtes, rejet d'observation plus ancienne, politique de fraîcheur **optionnelle** et gestion des hypothèses | Les écrans doivent lui transmettre les événements de sélection, invalidation, erreurs et fraîcheur ; ne pas le réécrire. La politique de fraîcheur n'est **pas** imposée par la page actuelle |
| `b65-calculateur/atlas-depart-engine.mjs` | Moteur pur `planDeparture`, UTC ISO avec offset obligatoire, `Intl.DateTimeFormat`, bases horaire prévue/révisée/observée, marges séparées, annulation et états incomplets | `displayZone` défaut `Europe/Paris` ; fournir zone locale du point de départ et informations aériennes cohérentes, sans convertir les heures par arithmétique locale |
| `b65-calculateur/mock-adapters.mjs`, `mock-integration.mjs` | Vols **AV103** fictifs (retardé, atterri, annulé, périmé, manquant, non confirmé) ; routes mock Paris / Rozay (20/45 min), sans réseau ; provenance déclarée `AeroDataBox MOCK` et `Geoapify MOCK` ; 4 marges distinctes | L'adaptateur vol ne restitue aujourd'hui dans sa sortie que `flightNumber`, `destinationIata`, état, horaires et `source` : **provenance d'aéroport**, date locale, zones IANA et date d'observation aérienne structurée ne sont pas toutes dans le modèle mock normalisé ; **ne pas inventer** ces valeurs |
| `RECETTE-B65-VECTORIELLE.html` | UI de recherche d'adresse libre, sélection explicite du résultat, routage vers le point géographique **indicatif** d'Orly, MapLibre, rendu géométrique, ajustement carte, compteur QA | Géocodage, routage et fond de carte déclenchent des appels **Geoapify réels** après saisie locale d'une clé ; MapLibre est chargé via CDN ; aucun de ces appels ne peut devenir automatique dans le premier lot entièrement fictif |
| `RECETTE-B65-CARTOGRAPHIE.html` | Carte QA et géométrie de référence préenregistrée, marqueurs et rendu, **sans trajet dynamique** | Fond de carte chargé depuis fournisseur avec clé ; le tracé témoin Paris→Orly n'est pas la route effective d'une adresse arbitraire |
| `b65-calculateur/*.test.mjs`, `simulation-ui.test.mjs` | Tests unitaires de moteur, adaptateurs, contrôleur, fraîcheur, UI de simulation présents | Leur présence ne prouve pas le parcours iPhone/PC intégré ; aucune exécution nouvelle dans ce cadrage |

**Conclusion vérifiée :** le simulateur intégré calculateur + vol + trajet **existe déjà**. L'écart est l'UX unifiée incluant **sélection de vol explicitée, adresse choisie et visualisation cartographique de recette** en cohérence avec ce contrôleur, non la réalisation d'un nouveau moteur.

**Point d'attention :** le PV historique du 22 octobre constate des PASS ciblés iPhone pour la recherche d'adresse et le routage Geoapify vers Orly (P05/P06/P11), **pas** une validation du parcours unifié sans fournisseur. Il signale que le point Orly n'est ni terminal ni parking validé. Le code actuel de la page vectorielle affiche en cas d'erreur de routage une *ancienne ligne de démonstration* ; cela ne doit jamais être présenté comme un nouveau trajet. Les relevés de crédits du PV sont historiques et non un coût actuel démontré.

## 2. Proposition UNIQUE de premier lot fonctionnel — raccordement de recette 100 % fictive hors réseau

**Choix :** faire évoluer **uniquement la page de recette** `RECETTE-B65-PARCOURS-COMPLET.html` comme écran d'accueil de l'intégration et lui relier les composants existants, avec **deux jeux d'adresses / trajets fictifs contrôlés**. Conserver séparément `RECETTE-B65-VECTORIELLE.html` comme atelier historique avec clé fournie localement en recette, **sans l'importer ni l'activer** dans ce premier lot. On évite ainsi de créer une consommation Geoapify ou une dépendance à un réseau, tout en préservant l'acquis P05/P06 et la carte existante.

### Parcours et contrat de présentation du lot 1
1. **Vol fictif identifié et sélectionné :** proposer un seul ensemble cohérent de scénarios `AV103` et une sélection explicite parmi les variantes déjà définies (prévu, retard, atterri, annulé, information absente/périmée). Afficher **numéro, provenance/destination, statut, horaires de simulation et source**. Toute donnée de provenance non présente dans les fixtures doit être ajoutée seulement **après validation** comme métadonnée **inventée et étiquetée fictive** ; sinon afficher « Non renseignée ». Ne jamais qualifier un décollage réel ou une fraîcheur « live ».
2. **Choix d'adresse et trajet :** commencer par les **deux adresses de recette** représentant Paris et Rozay, avec **sélection explicite, correction/changement et réinitialisation** ; afficher un libellé clair « Adresse fictive prédéfinie, **pas** une recherche géocodée ». Le champ de recherche libre réel demeure sur la page vectorielle de recette, non connecté dans ce lot. La géométrie de trajet cartographique ne doit être affichée que si une fixture géométrique cohérente est attestée par le dépôt et liée à la même origine : sinon **schéma de trajet existant**, avec indication « itinéraire indicatif simulé, aucune route réelle calculée ». Ne pas reprendre le tracé Paris→Orly pour Rozay.
3. **Destination :** « Paris-Orly — **point d'aéroport indicatif** » ; ne pas prétendre identifier terminal, parking, hall, zone d'attente ou lieu de rencontre réel. **Ne pas réutiliser** des coordonnées Orly comme si elles étaient un lieu routier vérifié à l'international.
4. **Départ conseillé :** afficher la sortie de `createJourneyController().getState().recommendation`, calculée par `planDeparture` seulement si vol, adresse simulée, temps de route fictif et marges existent ; aucune formule parallèle dans la page. Rendre visibles valeur de référence prévue/révisée/atterrie fictive, durée de route, sortie passager, trafic **non observé**, marges, formule, date complète, heure locale de départ **Europe/Paris** et UTC de référence ; changement de jour identifié. `null` = inconnu. Aucune garantie de trafic, sortie bagages ou ponctualité.
5. **Provenance/fraîcheur :** badges textuels sobres « Vol simulé — AeroDataBox MOCK », « Trajet simulé — Geoapify MOCK », horodatage **de la simulation ou horodatage source fictif explicitement déclaré** s'il existe ; pas de date d'observation présentée comme celle du fournisseur. Ne pas utiliser un horodatage fictif de mai 2027 comme « actualisé aujourd'hui ». Une limite de fraîcheur ne doit pas rendre périmé de facto un scénario daté dans le futur : prévoir une horloge de recette explicite et contrôlée ou une mention « horloge de simulation », puis tester l'expiration via `freshnessPolicy`.
6. **États de sécurité UX :** retard crédible fictif → recalcul ; annulé/détourné → suspendu ; vol sans horaire, adresse non choisie, destination inconnue, trajet indisponible ou simulation réseau indisponible → **pas d'heure** ni d'ancien tracé reconduit. Changement de sélection ou d'adresse → `invalidateRoute` **avant** tout nouvel état ; `flightVersion` / `routeVersion` pour ignorer une réponse plus ancienne. La panne réseau doit pouvoir être **simulée sans requête** dans ce lot, distincte d'un test fournisseur.
7. **Mobile premium :** conserver la structure de la page QA, palette sombre / champagne et contrôles accessibles ; traductions FR/EN/RU **à examiner** sans modifier `i18n.js` ou le site public au premier lot. Si langues complètes non disponibles, afficher explicitement « traduction intégrée non réceptionnée » plutôt que présumer P12 validé.

### Fichiers à envisager après GO distinct
- **Indispensable :** `RECETTE-B65-PARCOURS-COMPLET.html` (interface d'assemblage existante, sans API fournisseur).
- **Si nécessaire et avec justification préalable :** `b65-calculateur/mock-adapters.mjs` pour enrichir les **fixtures** de champs `originIata`, zones IANA, horaires observés au titre de la simulation ; ne pas étendre l'adaptateur à une API réelle. `b65-calculateur/journey-controller.mjs` doit de préférence rester **inchangé** ; toute modification nécessiterait une justification explicite et des tests de non-régression.
- **Tests futurs :** un fichier de tests d'interface B6.5 dédié, en réutilisant les tests existants de moteur/contrôleur ; ne pas dupliquer les scénarios unitaires.
- **Inchangés dans le premier lot :** `index.html`, `i18n.js`, `RECETTE-B65-VECTORIELLE.html`, `RECETTE-B65-CARTOGRAPHIE.html`, `atlas-depart-engine.mjs`, services HTTP, modules identité/sécurité, workflows, `main`, site public.

**Arbitrage explicite nécessaire du 00 :** le premier lot **ne réalise pas encore une recherche libre géocodée ni un routage Geoapify au sein de la page unifiée**. Il offre un choix d'origines fictives, une visualisation schématique cohérente et l'heure calculée ; le raccordement du champ d'adresse réel et de la cartographie interactive sera étudié comme lot ultérieur distinct **si** validation fonctionnelle du premier lot. Cela respecte la priorité de ne pas activer de fournisseur réel, mais ne suffit pas à réceptionner P05/P06 dans la nouvelle page intégrée.

## 3. Horaires et règles internationales de conception

- **Base de calcul :** instants ISO 8601 UTC/offset, pas de `HH:mm` isolé pour des opérations. Afficher « heure locale de la personne qui part » avec zone IANA `Europe/Paris` pour les fixtures Orly, date complète et UTC explicite dans les détails.
- **International cible :** provenance et destination IATA, zones IANA distinctes `originTimezone`, `destinationTimezone`, zone du départ routier, dates locales potentiellement différentes, franchissement de minuit et changements d'heure. Le lot 1 mono-aéroport ORY **n'établit pas** la conformité internationale complète.
- **Heures de référence :** `actualArrivalRunwayUtc` uniquement si statut corroboré ; sinon ETA révisée ; sinon horaire planifié. Vol encore programmé : départ **non confirmé**. Retard sans ETA actualisée crédible : ne pas le convertir en décollage réel.
- **Formule contractuelle :** `expectedMeetingUtc = arrivalBasisUtc + exitDelayMinutes` ; `recommendedDepartureUtc = expectedMeetingUtc - ceil(routeDurationSeconds/60) - trafficBufferMinutes - otherTravelBufferMinutes - meetingMarginMinutes` (soustractions en minutes). Les marges sont des hypothèses utilisateurs, non des mesures de trafic.
- **Affichage de fraîcheur :** distinguer heure du scénario, heure de réception/observation de recette, durée de validité si paramétrée et absence de source réelle. Les observations reçues dans un ordre inversé doivent être rejetées par le contrôleur lorsqu'elles sont datées et plus anciennes.

## 4. Critères P01–P16 : portée du premier lot

| Critère | Cible du lot de simulation et méthode de qualification future | Limite restant hors lot |
|---|---|---|
| P01 | Choix explicite d'un vol fictif identifié avec numéro/date/aéroports, refus d'inconnu | Recherche AeroDataBox réelle non testée |
| P02 | Simuler « sans numéro » en choix contrôlé si fixture disponible ; sinon marquer NON COUVERT | FIDS et désambiguïsation réelle non testées |
| P03 | Statuts fictifs, libellés « non confirmé », source et nature de l'horaire | Décollage réel non attesté |
| P04 | Horloge/horodatage simulés, rejet de réponses périmées | Rafraîchissements fournisseurs/quota non testés |
| P05 | Changement d'origine parmi deux fixtures | Recherche d'adresse libre déjà reçue sur **autre page**, non reçue intégrée |
| P06 | Réinitialisation du temps/ligne et recalcul des deux routes fictives | Réseau Geoapify et géométrie de route réelle non reçus intégrés |
| P07 | Afficher « point d'aéroport indicatif » | Terminal/parking réel absent |
| P08 | Heure calculée via moteur existant, UTC/date locale, marges traçables | Changement de fuseau international à étendre |
| P09 | Null/inconnu, retard, données périmées, trafic et sortie passager hypothétiques | Incertitude fournisseur réelle non mesurée |
| P10 | Retard + changement origine → invalidation et recalcul sans données périmées | Suivi temps réel réel et fréquence non testés |
| P11 | Revue mobile iPhone et PC **à exécuter après GO** | PASS historiques ciblés non transférables automatiquement |
| P12 | Cadrer FR/EN/RU et longueur RU ; vérifier langues disponibles | Traduction intégrale de ce nouvel écran non promise |
| P13 | Simuler erreurs/absence réseau, pas d'ancien résultat tenu pour nouveau | 400/429/5xx/timeout réels non testés |
| P14 | Aucun appel ni crédit fournisseur dans le lot ; le bilan historique de crédits demeure une référence datée | 20 parcours B6.4, tarification et licences NO-GO |
| P15 | Zéro clé ni quota ni endpoint public dans la nouvelle page de simulation | Architecture serveur/sécurité production hors lot |
| P16 | Captures d'un nominal et d'un retard/échec sur iPhone, revue PC et traces de CI après GO | GO intégré réel non obtenu par le seul lot mock |

**Règle de réception :** ne pas déclarer P01–P04 « réels » validés par leur analogue mock ; P05/P06/P11 historiques sont des preuves ciblées sur la page cartographique, non le résultat de cette nouvelle intégration. Une recette globale P01–P16 requiert les étapes et services non autorisés ici.

## 5. Tests à autoriser après un éventuel GO de réalisation

- Flux nominal fictif : choisir le vol AV103, son origine/destination clairement étiquetées, choisir Paris ou Rozay, afficher source des hypothèses, résultat UTC/local et calcul reproductible.
- Retard/arrivée prévue/atterri, annulation et absence d'heure : état et calcul/suspension cohérents, aucune confirmation de décollage fictif déguisée en donnée réelle.
- Changer d'adresse, revenir à « inconnue », changer de vol ou destination : invalidation immédiate de la route et de l'heure ; pas de résultat antérieur réutilisé après échec.
- Simulation « réseau indisponible » **sans appel** : état compréhensible, carte/route conservée seulement si explicitement témoin historique, jamais présentée comme nouvelle.
- Tester UTC et Europe/Paris avec date complète, changement de jour et passage à l'heure d'été/hiver via `Intl` ; tests de provenance et d'horloge de simulation non trompeuse.
- Vérifier accessibilité tactile, textes longs et variantes FR/EN/RU effectivement prises en charge ; capture iPhone d'un cas nominal et d'un cas retard/échec, et revue PC, **sans déclarer que ces essais ont eu lieu**.
- Non-régression des suites `b65-calculateur/*.test.mjs`, de la cartographie historique et des acquis B6.5, en différenciant résultats locaux, CI et recette manuelle ; qualifier les dépendances CDN/fournisseur **sans déclencher de requête** au stade du lot fictif.

**Critères de sortie proposés :** aucune nouvelle dépendance externe, aucun code métier/calculateur réécrit, source fictive et hypothèses toujours visibles, absence de conseil en cas de donnée bloquante, cohérence d'invalidation, tests ciblés puis CI réussis sur commit exact **et** réception indépendante chat 03. Aucune qualification iPhone/PC n'est acquise avant sa réalisation.

## 6. Risques et limites résiduels

1. **Confusion de sources :** fixtures `AeroDataBox MOCK` et `Geoapify MOCK` ne sont pas des données fournisseur ; ne pas les étiqueter « observées ».
2. **Fausse carte :** la route géométrique de la page vectorielle est liée à un point Orly et ne peut pas figurer indistinctement un trajet Rozay ; carte et routage Geoapify sont séparés du lot sans réseau.
3. **Dépendance internet et crédits :** la page vectorielle utilise CDN MapLibre et appels directs Geoapify avec clé locale ; ne pas la charger automatiquement depuis la simulation ni ajouter de nouvelle clé. Le PV économique n'est pas une mesure du lot.
4. **Fuseaux :** la page actuelle force `Europe/Paris` et affiche une arrivée partielle `HH:mm` ; ne pas généraliser ce comportement à tout aéroport international.
5. **Périmètre produit :** deux origines fictives et un schéma ne constituent **pas** le choix d'adresse arbitraire et la carte interactive du produit final. L'absence de recherche libre intégrée est à déclarer, non à masquer.
6. **Sécurité et publication :** R1-C01 reste gelé ; P0 ouvert ; `index.html` et site public inchangés. Aucune permission de fournisseur ou de déploiement.

## 7. Arbitrage demandé au 00

**Proposition unique — GO/NO-GO pour un premier lot « page QA B6.5 unifiée entièrement fictive, hors réseau » :** assembler dans `RECETTE-B65-PARCOURS-COMPLET.html` la sélection explicite AV103, le choix contrôlé d'origine, la représentation indicative de trajet, l'affichage sourcé et horodaté du calcul existant et les états de suspension/invalidation ; enrichir au strict nécessaire les fixtures mock, sans nouveau moteur, sans Geoapify, sans MapLibre CDN et sans modification du site public. Prévoir tests ciblés, CI, puis recette indépendante 03.

**Différé et non autorisé :** saisie/recherche libre géocodée dans la page unifiée, routage réel, carte interactive alimentée par réseau, vols AeroDataBox réels, licences/coûts, lancement production.

**Statuts inchangés :** B6.5 EN RECETTE, parcours unifié non réceptionné ; AC-08/AC-13 réceptionnés avec réserves dans leur périmètre ; R1-C01 PARTIEL et gelé ; R1-RD01/R1/P0-01 OUVERTS ; G04/B6.3/production NO-GO.

**Prochaine action unique :** soumettre ce cadrage au chat 00 pour GO/NO-GO du premier lot fonctionnel fictif, sans ouvrir d'autre chantier.
