# B6.5 — Calculateur autonome : protocole de recette

Moteur `atlas-depart-engine.mjs` + tests `atlas-depart-engine.test.mjs`. **Pure JS, aucune requête réseau, aucune clé et aucun connecteur live**.

## Exécution locale
`node --test b65-calculateur/atlas-depart-engine.test.mjs`

12 scénarios de test rédigés : horaires révisés et confirmés, trajectoire absente, vol annulé, adresse non choisie, marges absentes, données périmées, changement heure été/hiver, fuseau Europe/Paris, datetime UTC invalide et arrondi à la minute supérieure.

## Règles métier V1
`rendezVous = arrivée de référence + sortie passager estimée`;
`départ conseillé = rendezVous - trajet voiture arrondi à la minute supérieure - marge trafic - autre marge - marge de rendez-vous`.
Les marges sont des hypothèses paramétrées. Valeurs absentes => pas de conseil de départ. La priorité des horaires est arrivée piste confirmée, arrivée révisée, arrivée programmée. La présence d'un champ ne prouve PAS à elle seule l'état réel du vol : **la normalisation AeroDataBox devra certifier l'arrivée piste avant d'alimenter `actualArrivalRunwayUtc`**.
Une proposition d'heure est **indicative**, jamais prédictive à elle seule. Délais de sortie, congestion et destination précise ne sont pas encore connus en réel.

## Exemple fictif
Arrivée révisée `2027-05-15T15:50:00Z` (17h50 Paris), sortie 40 min, trajet 35 min, marge circulation 15 min, autre marge 5 min, rendez-vous +40 min = 18h30 Paris ; départ 17h35 Paris.

## Hors périmètre de cette livraison
Pas de rendu UI public, pas de connecteurs, pas de trafic temps réel, pas de frais commerciaux ni vente, pas de fusion production.
Requis avant intégration : définition ferme de la marge rendez-vous (risque de double comptage), validation d'horodatage qualité, DST et timezone de chaque aéroport, expiration des estimations et statut source, tests FR/EN/RU.

**Gouvernance : B6.3 NO-GO ; B6.5 recette ; aucun achat ; main et voyageur.atlascore.eu inchangés.**
