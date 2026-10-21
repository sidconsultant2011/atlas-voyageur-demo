# ATLAS VOYAGEUR — Audit B6.3 INTERNATIONAL (21 octobre 2026)

**Branche auditée :** `feature/b6-3-international`  
**Production :** `main` / https://voyageur.atlascore.eu/ — inchangée  
**Décision : NON AUTORISÉ POUR PRODUCTION (NO-GO)**

## Méthode et limites

Relecture directe, dans GitHub, des versions de `index.html`, `i18n.js`, `sw.js` et `manifest.webmanifest`. Contrôles statiques de structure, des flux FR/EN/RU, des messages dynamiques, du calcul, du stockage et du cache. **Aucun test d'exécution dans un navigateur réel, aucune installation iPhone et aucun test hors connexion réel ne sont revendiqués.** Les contrôles de comportement restent à effectuer sur une version de prévisualisation isolée.

## Constatations

| ID | Gravité | Résultat | Décision |
|---|---|---|---|
| I18N-01 | Bloquant | Traductions incomplètes : messages dynamiques de recherche, d'erreur, d'enregistrement et de restauration sans traduction dans le catalogue ou les motifs. | Compléter le catalogue et tester chaque flux |
| I18N-02 | Bloquant | Date de fiche `Arrivée : 15 mai 2027 à 17 h 35...` non entièrement traduite ; formats et fuseaux présentés en français dans plusieurs endroits. | Localisation explicite des dates et heures par langue |
| I18N-03 | Majeur | Certaines phrases HTML mêlent des éléments gras et du texte ordinaire ; la traduction par **nœud texte exact** laisse des fragments en français, sans garantie de phrase naturelle en EN/RU. | Remplacer les fragments par des unités traduisibles cohérentes, revoir par locuteur |
| I18N-04 | Majeur | Le contenu de `manifest.webmanifest` est encore en français (`name`, `description`, `lang`) et son identifiant `release=b62public` désigne la version publique stable. | Politique de métadonnées multilingues et identité PWA à définir sans multiplier les installations |
| I18N-05 | Majeur | Libellés/attributs accessibilité (`aria-label`, textes injectés dans le tracé SVG, notifications temporaires) partiellement traduits ou non couverts. | Auditer contenus visibles, lisibles par lecteur d'écran et modifiés par JavaScript |
| I18N-06 | Majeur | Affichage EN/RU non vérifié sur largeurs iPhone, texte cyrillique, retour à FR et ouverture après redémarrage. | Matrice de tests visuels FR/EN/RU sur PC et iPhone |
| PWA-01 | Majeur | `sw.js` nettoie seulement les caches préfixés `atlas-voyageur-public-` ; le cache de développement `atlas-voyageur-dev-` n'est pas inclus dans ce nettoyage. | Corriger la stratégie de nettoyage / éviter la concurrence des caches |
| PWA-02 | Majeur | Présence de mécanismes d'actualisation Service Worker, mais aucun essai réel du démarrage, de la mise à jour, du mode avion ou du basculement de langue hors connexion. | Tests offline et mise à jour sur iPhone installé |
| REG-01 | À vérifier | Le calcul du départ (route + marge circulation + avance), le stockage `atlas-voyageur-public-b62-v1` et les contrôles de durée sont encore présents ; **présence du code ≠ test fonctionnel réussi**. | Rejouer les calculs 20/35 min et vérifier les heures attendues |
| REG-02 | À vérifier | Barre `.steps` sticky conservée sur PC et safe area iOS conservée ; absence de test réel du défilement en FR/EN/RU. | Tester les 3 boutons sur PC et iPhone (Safari + PWA installée) |
| REG-03 | À vérifier | Recherche avec/sans numéro et sélection du vol encore codées ; absence de test de bout en bout en EN et RU. | Parcours complet dans chaque langue |
| PROD-01 | Conforme | B6.3 existe sur une **branche indépendante** ; le fichier `i18n.js` n'est pas référencé dans le `index.html` de `main`. | Ne pas fusionner avant levée des blocages |

## Matrice minimale de recette avant fusion

1. FR, EN, RU : démarrer, changer de langue, parcourir les trois écrans, revenir au français ; aucune phrase française résiduelle en EN/RU (hors marques, références et noms propres).
2. Recherche **avec numéro** (`DEMO001`) et **sans numéro** (15/05/2027 à 18:30 ± 1 h) ; tester aussi une recherche sans résultat.
3. Fiche vol : date, heure locale, aéroports, avertissement fictif et sélection en trois langues.
4. Calcul : paramètres route 20 puis 35 min, marges de circulation/sortie/avance ; heure de départ cohérente, saisies invalides correctement signalées.
5. Sauvegarder, fermer, rouvrir, restaurer ; vérifier que changer de langue ne modifie pas le scénario enregistré.
6. PC : barre sticky et affichage lisible ; iPhone Safari et icône PWA : barre entièrement visible sous la zone système, pas de débordement en russe.
7. Réseau coupé après première visite : navigation et traductions fonctionnelles ; retour en ligne : version actualisée et sauvegarde préservée.
8. Manifest, accessibilité clavier/lecteur d'écran, sécurité des fichiers statiques et absence d'appels API réels.

## Conditions de sortie

- Corriger les écarts bloquants/majeurs documentés.
- Exécuter et consigner les résultats des tests PC, Safari iPhone et PWA iPhone, y compris hors connexion.
- Procéder à une revue de traduction russe et anglaise orientée usage (pas seulement présence de chaînes).
- Obtenir validation explicite avant fusion sur `main` et publication sur `voyageur.atlascore.eu`.

**Le formulaire « Votre avis nous intéresse » reste hors périmètre de cette première recette : il vient ensuite.**

## Recette technique intermédiaire — 21 octobre 2026 (après correctifs)

**Correctifs enregistrés sur la branche uniquement :** enrichissement du catalogue `i18n.js` (dates, recherche sans résultat, erreurs, sauvegarde et restauration), complément des motifs dynamiques ; nettoyage des anciens caches `atlas-voyageur-dev-` dans `sw.js`.

**Contrôles statiques réalisés :** analyse de syntaxe JavaScript pour `i18n.js`, `sw.js` et le script embarqué de `index.html` — **aucune erreur de syntaxe détectée** ; présence de `./i18n.js` dans le cache hors connexion ; présence de la navigation sticky et de la logique de calcul d'origine. Le catalogue contient plus de 100 entrées, mais le nombre d'entrées **ne garantit pas** la qualité ni la couverture intégrale.

**Écarts restants :** la localisation repose sur une traduction de nœuds texte et non encore sur une architecture complète par identifiants de messages. Les phrases HTML fragmentées, les chaînes mixtes et des annotations SVG peuvent toujours échapper à la traduction. Le manifeste de PWA demeure principalement en français. Les tests d'exécution avec interactions, la vérification réelle des trois langues, l'affichage mobile, la restauration persistante et le mode hors connexion ne sont pas encore réalisés.

**Décision maintenue : NO-GO.** Ne pas fusionner sur `main`, ne pas annoncer EN/RU comme disponibles, ne pas installer la branche de développement sur l'iPhone utilisé pour la démonstration publique. Prévoir une prévisualisation isolée et une recette automatisée + visuelle avant toute promotion.

## Correctifs linguistiques complémentaires — 21 octobre 2026

- Ajout des traductions **EN/RU** pour les annotations résiduelles du trajet, notamment « Estimation hors trafic réel. » et la ligne d'itinéraire Porto (OPO) → Paris-Orly (ORY).
- Compléments pour messages de sauvegarde/restauration, notamment le toast « Scénario restauré : 35 min », constaté encore en français pendant la recette russe.
- `show()` et `storageNote()` traduisent les messages au moment où ils sont affichés ; les notifications dynamiques ne dépendent plus exclusivement du passage de l'observateur de mutations.
- Nouvelle version du cache `atlas-voyageur-dev-b63-l10n-v4` pour embarquer les changements hors connexion.
- Vérification statique de la syntaxe `index.html` (JavaScript intégré), `i18n.js`, `intro.js` et `sw.js` : aucune erreur détectée.

**Recette restant à faire :** télécharger à nouveau le ZIP de la branche B6.3, actualiser le serveur local PC et vérifier réellement les notifications EN/RU, les textes mixtes de l'itinéraire et le fonctionnement hors connexion après mise à jour. Les tests iPhone demeurent non réalisés. **NO-GO maintenu**, `main` et la démonstration publique restent inchangés.
