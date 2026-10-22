# ATLAS VOYAGEUR — B6.3 PLATINE — Recette finale avant promotion

**Décision utilisateur :** PLATINE est l'identité principale retenue pour B6.3. Harmonisation réalisée uniquement sur `feature/b6-3-platine`. **NO-GO production.**

## Design retenu

- Fond bleu nuit conservé `#09131F`.
- Accent platine `#BCCAD5` pour signature, commandes principales, état sélectionné et contours/focus.
- Avertissements harmonisés en bleu acier et texte gris clair, sans ancien or.
- Turquoise conservé sur le panneau de calcul et les informations opérationnelles.
- Indicateur de focus visible : pas de suppression du focus clavier.

## Contrôles techniques effectués

- `index.html` (script intégré), `intro.js`, `i18n.js`, `sw.js` : syntaxe JavaScript vérifiée, aucune erreur détectée.
- Présence vérifiée du code des trois étapes sticky, du calcul routier et de la sauvegarde locale.
- Ancienne couleur d'accent `#DFB374` absente de `index.html`; identifiants et données de démo préservés.
- Cache PWA distinct `atlas-voyageur-dev-b63-platine-v2`.

## Recette finale restant à confirmer sur le déploiement HTTPS Cloudflare

1. Vérifier le dernier build de `feature/b6-3-platine` dans Cloudflare Pages, récupérer son URL de prévisualisation réellement publiée. Les anciennes URL de déploiement sont des captures figées.
2. Sur iPhone Safari : valider signature d'ouverture et activation/désactivation du réglage dans FR / EN / RU.
3. Vérifier les trois étapes, l'état sélectionné et les messages d'erreur sans ancien or ou couleur illisible.
4. En FR / EN / RU : lecture des titres, heures et annotations du trajet, aucune coupure russe.
5. Calcul 20 min → 17:30, puis 35 min → 17:15, rencontre à 18:15, sur les mêmes données fictives.
6. Sauvegarde et restauration à 35 min, persistance de langue et du réglage après relancement.
7. Tester iPhone PWA autonome : barre sticky sous l'encoche, sans régression.
8. Tester hors connexion après chargement initial, navigation et calcul, sauvegarde/restauration.
9. Vérifier le rendu sur PC et un retour sur l'affichage platine — décision graphique explicitement approuvée, recette visuelle complète encore requise.
10. Vérifier indépendamment que `https://voyageur.atlascore.eu/` reste sur B6.2 ; ne pas modifier DNS OVH, `main` ni la production du projet Cloudflare de test.

## Gouvernance

- Ne pas fusionner dans `main` sans validation finale explicite.
- Ne pas modifier le domaine public sans instruction explicite.
- L'espace « Votre avis nous intéresse » est postérieur à cette recette.
