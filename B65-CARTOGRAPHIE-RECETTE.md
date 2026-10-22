# ATLAS VOYAGEUR — B6.5 CARTOGRAPHIE INTERACTIVE

Statut : **prototype isolé, NO-GO production**. Branche `feature/b6-5-cartographie-interactive` issue de `feature/b6-3-platine`.

## Fichier de recette
`RECETTE-B65-CARTOGRAPHIE.html`

- Palette bleu nuit, platine champagne et turquoise.
- Carte routière réelle fondée sur tuiles Geoapify et MapLibre GL JS (bibliothèque CDN), uniquement si l'utilisateur clique **Charger la carte** après avoir saisi sa propre clé.
- Route Paris centre → Paris-Orly : **437 coordonnées issues de la géométrie de référence préenregistrée dans B6.3**. Aucun nouveau géocodage ni routage, et aucune donnée de trafic.
- Marqueurs départ / arrivée, zoom et déplacement.
- Compteur local des **demandes de tuiles déclenchées** depuis la page et estimation indicative à **0,25 crédit / tuile**. Ni relevé fournisseur ni preuve de facturation.
- La clé est gardée exclusivement en mémoire de l'onglet, non persistée ; elle est envoyée à Geoapify pour les tuiles. Ne pas publier de clé en dur dans le dépôt.
- Aucun appel avant clic explicite ; ensuite des requêtes réseau et consommation potentielle de crédits sont **attendues**. Dépend d'Internet, pas un mode hors ligne.
- Code client statique, sans aucun achat ni configuration DNS.

## Validation nécessaire
1. Comparer compteur Geoapify officiel avant/après session iPhone pour déterminer le débit réel.
2. Comparer iPhone Safari, iPhone PWA, PC et comportement hors ligne.
3. Contrôler attribution et conditions de cache/licence.
4. Test de quota / limite et gestion des erreurs d'authentification.
5. Vérifier lisibilité, contraste, contrôles tactiles et scroll.
6. Décider si chargement de tuiles au besoin est assez rassurant et rapide.
7. Aucune fusion ni adoption commerciale sans GO explicite.

## Métriques fournisseur préalables observées
Geoapify, fenêtre 22 septembre–22 octobre 2026 : 3 demandes, 3 crédits, soit géocodage 2/2, routage 1/1 et tuiles 0/0. Plafond gratuit 3 000 crédits quotidiens.

B6.4 conserve son banc de mesure indépendant. B6.3 et `main` restent inchangés. L'URL publique `voyageur.atlascore.eu` reste sur B6.2.
