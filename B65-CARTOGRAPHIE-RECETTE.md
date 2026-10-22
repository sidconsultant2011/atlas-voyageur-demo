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


## Variante CARTE NETTE — 22 octobre 2026
Le prototype offre un sélecteur entre fond de référence raster `dark-matter` standard et nouvelle variante raster Geoapify `dark-matter-brown` en `@2x` pour les écrans HiDPI. Chaque changement arrête la carte et remet le compteur local à zéro. L'itinéraire GeoJSON et les marqueurs sont conservés. Comparer à écran équivalent, sans zoom ni déplacement supplémentaire : référence observée 36 demandes de tuiles, 9 crédits *estimés*, zéro crédit tuiles encore enregistré dans le tableau de bord Geoapify. Les deux sessions sont des essais distincts; ne pas affirmer que l'une coûte davantage tant que les relevés fournisseur ne sont pas disponibles. Le mode @2x est une meilleure résolution raster, pas une promesse de textes vectoriels redimensionnables. Aucun chargement automatique.

## Variante VECTORIELLE LISIBLE — 22 octobre 2026
Page distincte : `RECETTE-B65-VECTORIELLE.html`. Le sélecteur permet de comparer Geoapify MapLibre vectoriel (style JSON `dark-matter-brown`) avec le raster standard. Libellés des couches `symbol` renforcés à au moins 14–16px, halo et couleur platine. Même tracé Paris centre → Orly, pas de géocodage / routage supplémentaire.
Compteur local des requêtes `Tile` (Geoapify) et estimation théorique à 0,25 crédit / demande. Il ne reflète pas directement la facture, car le cache et la comptabilisation provider peuvent diverger.
**Point de référence officiel Geoapify avant nouvel essai :** 63 demandes API, 18 crédits au total, dont 60 demandes de tuiles de carte / 15 crédits. Relever de nouveau après session : incréments de tuiles et crédits d'abord, puis inspecter lisibilité FR/EN/RU, zoom et affichage mobile. Test non encore réalisé. Aucune nouvelle clé stockée; carte inactive par défaut. Branche uniquement et aucun GO production.
