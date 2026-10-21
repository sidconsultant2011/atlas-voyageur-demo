# ATLAS VOYAGEUR — Prévisualisation PC isolée B6.3

**Statut : version de développement, non validée, non publiée.**

La branche `feature/b6-3-international` n'est pas fusionnée dans `main` et n'est pas servie par `voyageur.atlascore.eu`.

## Essai local sous Windows

1. Dans GitHub, ouvrir la branche `feature/b6-3-international` de `sidconsultant2011/atlas-voyageur-demo`.
2. Choisir **Code → Download ZIP** afin d'obtenir l'intégralité des fichiers de cette branche (y compris `index.html`, `i18n.js`, `intro.js`, `sw.js`, le manifeste et `icons/`).
3. Extraire les fichiers dans un dossier **distinct** des versions B6.2 et d'ATLAS FLIGHT.
4. Dans ce dossier extrait, ouvrir un terminal Windows et exécuter `python -m http.server 8893 --bind 127.0.0.1`.
5. Visiter **http://127.0.0.1:8893/** depuis le PC. Ce port réservé aux essais ne touche ni à `voyageur.atlascore.eu`, ni aux services locaux 8877 et 8880.
6. Tester FR / EN / RU, puis l'écran signature. Pour masquer et réactiver la signature, utiliser le bouton « Afficher la signature à l'ouverture » dans l'en-tête (texte adapté à la langue).

**Avertissement :** GitHub Pages ne sert pas cette branche. Ne pas confondre téléchargement de code et déploiement. Ne pas installer cette version sur l'iPhone de démonstration.

## Contrôles prioritaires

- Vérifier la signature au premier lancement : « ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment. », puis traductions EN/RU.
- Vérifier que le choix d'afficher la signature et la langue restent mémorisés après fermeture/réouverture.
- Rechercher `DEMO001` avec numéro, puis rechercher le 15/05/2027 à 18h30 ±1h sans numéro.
- Vérifier la date fictive dans la fiche du vol et le passage à « Accueillir ».
- Vérifier le calcul avec 20 puis 35 minutes, l'enregistrement/restauration et la navigation sticky.
- Passer hors connexion **uniquement après une première visite locale connectée**, puis vérifier les trois langues et le parcours.
- Consigner les anomalies linguistiques, notamment les phrases résiduelles en français, les dates et l'affichage cyrillique.

**Aucun test complet sur PC ou iPhone n'est encore attesté.** Les résultats de syntaxe ne valent pas validation fonctionnelle.
