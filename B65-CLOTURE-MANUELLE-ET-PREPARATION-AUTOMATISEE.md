# ATLAS VOYAGEUR — B6.5 — Clôture de recette manuelle et préparation automatique
Date : 22 octobre 2026
Statut : **recette manuelle clôturée pour les cas observés uniquement**. Pas de GO global, pas de validation des données live.

## Preuves iPhone retenues
- Adresse libre, géocodage de recette et trajet vers Orly : test iPhone positif.
- Interface mobile : bouton de recherche pleine largeur, confirmation d'adresse, carte lisible, réglages de test repliables : test iPhone positif.
- Simulation fictive « vol retardé — arrivée révisée » : arrivée 17 h 50, sortie 40 min, route 45 min, marges 20 min ; départ conseillé **17 h 25** : cohérent.
- Simulation fictive « vol annulé » : aucun départ conseillé et mention « Conseil suspendu » : conforme.
- Toutes autres variantes (fuseaux rares, reprise réseau, ambiguïtés et transitions rapides) : **non validées manuellement**, couvertures automatisées à compléter.

## Contrôles techniques automatiques
Un workflow GitHub Actions sur cette branche exécute les tests unitaires du calculateur à chaque modification du dossier `b65-calculateur`, sans clé ni appel AeroDataBox / Geoapify. La réussite du workflow n'est **pas affirmée tant que GitHub n'a pas exécuté et rapporté ses résultats**.
Commande locale : `node --test b65-calculateur/atlas-depart-engine.test.mjs`.

## Prochain contrat d'adaptateurs (sans appels externes)
- `FlightAdapter` : sélection du vol, normalisation UTC, statut, fraîcheur, incertitudes, terminal optionnel.
- `RouteAdapter` : origine choisie, destination justifiée, durée en secondes, distance et fraîcheur, absence de trafic certifié.
- `DeparturePlanner` : `planDeparture()` pur et reproductible.
- Fournir des fixtures JSON immuables simulant normal, retardé, annulé, données vieillies et erreur de routage.
- Les adaptateurs **mock** devront être remplaçables par AeroDataBox/Geoapify, mais ne devront contenir ni secrets ni trafic réseau.
- Garde-fous : ne jamais annoncer un décollage sur simple heure planifiée, invalider un résultat quand le trajet ou le vol est modifié, afficher la cause si aucune heure conseillée.

## Conditions avant toute intégration live
Valider la correspondance des champs fournisseurs et les coûts par endpoint en environnement contrôlé, fixer stratégie de rafraîchissement et backend de protection des clés, les zones horaires et les règles de disponibilité, puis seulement décider explicitement d'activer des appels.

## Gouvernance
**B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion main ; site public voyageur.atlascore.eu inchangé.**
Les visuels avion/train/bus constituent un chantier distinct et non bloquant, sans intégration dans cette étape.
