# ATLAS VOYAGEUR — B6.5 — PV DE RECETTE ERGONOMIQUE ET CRITÈRES PARCOURS INTÉGRÉ
Date : 22 octobre 2026
Statut : **RECETTE ERGONOMIQUE CIBLÉE CLÔTURÉE (périmètre observé) — PAS DE GO PRODUCTION**.
Branche : `feature/b6-5-cartographie-interactive`.

## 1. Périmètre et preuves observées sur iPhone
- Adresse de départ librement saisie, recherchée, choisie puis confirmée (« Adresse reconnue ») : **PASS observation iPhone**.
- Bouton « Rechercher mon adresse » pleine largeur sur iPhone : **PASS observation iPhone**.
- Routage géocodé Geoapify vers Paris-Orly, parcours réellement modifié selon l’adresse choisie : **PASS observation iPhone** (exemple Rozay-en-Brie → Orly, 65,1 km, environ 45 min hors trafic).
- Carte vectorielle, marqueurs et cadrage : **PASS observation iPhone**. Le zoom partiel signalé était volontaire et non une anomalie de recadrage.
- Réglages de test et compteurs dans des sections repliables : **PASS observation iPhone**.
- Point d'arrivée : **point de référence géographique vers Orly**, pas accès terminal/parking validé.
- Limites connues : écran de recette avec contenu technique, champ Safari autofill jaune possible ; trafic réel non présent ; pas de garantie de durée ou de temps de sortie passager.
- Aucun PASS de bout en bout « vol réel → trajet → heure de départ » à ce stade.

## 2. Référence économique et vigilance
Dernier relevé Geoapify observé sur 22 septembre–22 octobre 2026 (UTC) : **244 demandes / 71 crédits**, dont **231 demandes de tuiles / 58 crédits**, **7 géocodages / 7 crédits**, **6 routages / 6 crédits**. Référence précédente : 142 / 38, dont 139 tuiles / 35 crédits.
Les différences agrègent plusieurs manipulations, **ne constituent pas un coût unitaire par accueil**. Les relevés fournisseur peuvent être décalés ; le compteur local de tuiles ne mesure pas toute la facturation. B6.4 : banc de 20 parcours et droits commerciaux encore à finaliser.

## 3. Contrat fonctionnel cible (non encore livré)
Une personne vient accueillir un voyageur : identifier son vol avec ou sans numéro, confirmer son état (décollé, en vol, atterri, retardé, annulé ou inconnu), choisir **son propre point de départ**, calculer le trajet routier vers le bon lieu d'accueil, déterminer **quand partir** en fonction de l'ETA du vol et de la marge de sortie, et réévaluer si les données changent.
Aucune clé, endpoint, quota ou outil de développement dans l'interface publique ; les fonctions de recette restent isolées.

## 4. Critères de validation — parcours vol + trajet + départ
| ID | Critère observable | Condition de réussite | État |
|---|---|---|---|
| P01 | Recherche avec numéro | Résultat exact, date et aéroports cohérents ; erreur contrôlée si absent/homonyme | À tester réel |
| P02 | Recherche sans numéro | Aéroport + date + plage horaire permettent de sélectionner le bon vol, ou limitation explicite | À tester réel |
| P03 | Statut de vol | Décollage confirmé **uniquement si donnée disponible** ; états et horodatage source visibles ; pas de faux « en temps réel » | À tester réel |
| P04 | Actualisations | Rafraîchissements maîtrisés, dernière vérification indiquée, limites API et erreurs respectées | À tester réel |
| P05 | Adresse libre | Recherche, choix, correction et changement d'adresse sans origine imposée | PASS ciblé B6.5 |
| P06 | Trajet recalculé | Carte, distance et durée changent selon adresse ; défaut API n'affiche pas ancien tracé comme nouveau trajet | PASS ciblé B6.5, erreurs à étendre |
| P07 | Destination accueil | Terminal / lieu de rendez-vous justifié quand disponible ; sinon indiquer point aéroport indicatif | Non réalisé |
| P08 | Heure de départ | Formule traçable : arrivée estimée + délai sortie/bagages − route estimée − marge éventuelle ; fuseaux Europe/Paris et ceux du vol corrects | À intégrer |
| P09 | Incertitude | Données manquantes, vol non décollé, retard, absence de trafic et estimations de sortie clairement distingués des faits | À tester |
| P10 | Modification en cours de suivi | Retard / nouveau ETA / nouvelle adresse => nouveau calcul sans confusion ; contrôle des appels et de la durée de suivi | À tester |
| P11 | UX iPhone | Champs accessibles, boutons lisibles, carte et résultat directement disponibles, sans donnée technique visible | PASS ciblé B6.5 ; à retester intégré |
| P12 | Langues | FR/EN/RU : libellés, erreurs, textes longs russes et formats horaires, langue conservée | À tester intégré |
| P13 | Résilience | Erreur 400/429/5xx, timeout, hors réseau, vol ambigu : état clair et aucune indication trompeuse | À tester |
| P14 | Coût et licence | 20 parcours B6.4 documentés : endpoint, unités facturées, rafraîchissements, durée ; droits commerciaux AeroDataBox/Geoapify vérifiés | NO-GO |
| P15 | Sécurité | Clés et quotas côté serveur ou infrastructure appropriée ; aucune clé technique demandée au public | À concevoir |
| P16 | Recette complète | Au moins un scénario nominal et un scénario de retard/échec filmés ou capturés sur iPhone, plus revue PC, données et coûts tracés | À réaliser |

## 5. Jeux d'essai requis
1. Vol connu, décollage confirmé, adresse choisie et route calculée.
2. Vol non encore décollé et ETA incertain ; ne pas inventer une confirmation.
3. Vol retardé, heure conseillée recalculée et justification affichée.
4. Vol introuvable / plusieurs vols similaires sans numéro ; sélection explicite.
5. Changement d'adresse et d'aéroport / terminal ; comparaison du trajet et de l'horaire.
6. Erreurs API, dépassement de quotas, mode réseau interrompu ; message compréhensible, pas de valeur obsolète donnée comme fraîche.
7. Variantes FR/EN/RU sur iPhone avec textes longs, heures et dates locales.

## 6. Critères GO / NO-GO
**GO recette intégrée** seulement si P01–P13, P16 sont contrôlés avec preuves, anomalies bloquantes corrigées, mesures fournisseurs rapprochées et coûts documentés.
**GO commercial/production** requiert en plus P14/P15, droits de redistribution, tarification, politique de confidentialité et validation explicite du responsable projet. Aucune approbation n'est implicitement accordée par ce PV.

## 7. Gouvernance immuable
B6.5 reste une branche de recette ; **B6.3 NO-GO**. Pas d'achat, pas de fusion sur `main`, pas de modification du site public `voyageur.atlascore.eu`. Les outils GitHub, Cloudflare, Geoapify et RapidAPI/AeroDataBox restent réservés aux essais.

ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.
