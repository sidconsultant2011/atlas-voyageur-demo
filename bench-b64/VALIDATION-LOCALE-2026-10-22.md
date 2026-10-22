# B6.4 — Validation initiale locale et contrôle des offres — 22 octobre 2026

## Résultat d'exécution

Un exemplaire local reconstitué de `measure.py`, avec 20 dossiers synthétiques, a exécuté les commandes `check`, `report` et `add` avec succès. Un appel AeroDataBox fictif (2 unités et preuve nommée SYNTHETIC) et une réponse Geoapify HTTP 429 fictive ont été journalisés. Le rapport a affiché 2 appels, 1 échec, 2 unités aériennes et 1 consommation Geoapify inconnue. **Ceci n'est pas un usage réel fournisseur.** Le fichier `bench-b64/events.csv` du dépôt reste vide. Aucune clé API ni aucun appel réseau réel.

## Vérification documentaire publique (et non quotas du compte utilisateur)

- AeroDataBox : documentation officielle https://aerodatabox.com/pricing ; Basic annonce 400 unités/mois (essai 7 jours) ; Pro 5 000 unités/mois à partir de 7,50 USD/mois dans le comparatif fournisseur ; Tier 1/2/3 = 1/2/6 unités, à vérifier sur l'endpoint exact. **Le plan et la consommation de l'utilisateur dans RapidAPI ne sont pas lus ni vérifiés**.
- AeroDataBox API via RapidAPI : https://doc.aerodatabox.com/rapidapi.html ; vérifier le marquage Tier de chaque endpoint réellement choisi ; ne jamais exposer les clés API.
- Geoapify : https://www.geoapify.com/pricing/ : Free 3 000 crédits/jour ; API 10 10 000 crédits/jour pour 59 USD/mois ; l'offre gratuite peut être utilisée commercialement avec attribution et dans les limites. Usage effectif du compte non consulté.
- Geoapify Routing : https://apidocs.geoapify.com/docs/routing/ : calcul des crédits par paires de points et options (éviter routes, itinéraire détaillé, longue distance).
- Ces montants sont des tarifs publics et non des factures ni des données propres au compte.

## Blocages avant première mesure réelle

1. Lire le plan réel et les unités/quota restant de RapidAPI (avec capture expurgée de tout secret).
2. Identifier dans la documentation AeroDataBox les endpoints précis pour recherche par numéro et par aéroport/date/heure ; noter leur Tier.
3. Lire le compteur/quota effectif Geoapify et préciser endpoints de géocodage, routage et éventuels fonds de carte.
4. Vérifier les licences d'utilisation commerciale et de réaffichage des données, y compris limites de cache et conditions de redistribution.
5. Obtenir l'autorisation de réaliser un premier parcours sans abonnement ni dépassement ; ensuite seulement remplir `events.csv` avec des mesures observées.

**NO-GO sur usage facturable et publication.** B6.3, `main`, DNS et production publique inchangés.
