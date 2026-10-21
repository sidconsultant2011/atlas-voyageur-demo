# ATLAS VOYAGEUR

**Le bon vol. Le bon trajet. Le bon moment.**

ATLAS VOYAGEUR est un projet d'assistant d'accueil à l'aéroport, pensé pour aider une personne à retrouver un voyageur et à organiser son départ depuis **sa propre adresse** (domicile, bureau ou autre lieu) vers l'aéroport d'arrivée.

## Le concept

- **Avec un numéro de vol :** identifier directement le vol et consulter les informations d'arrivée disponibles.
- **Sans numéro de vol :** rechercher à partir de l'aéroport, de la provenance, de la date et d'une heure approximative, puis choisir le bon vol parmi les correspondances.
- **Depuis son adresse de départ :** préparer le trajet vers l'aéroport et estimer l'heure à laquelle partir, avec des marges ajustables pour la circulation et la sortie du voyageur.
- **International :** concevoir le parcours pour plusieurs pays et fuseaux horaires, selon la disponibilité des données.

L'objectif est simple : **savoir où aller, quand partir et quelles informations vérifier pour accueillir sereinement un proche.**

## Cette démonstration publique

Cette version est **une simulation, pas un suivi en direct**. Elle propose :

- un **vol entièrement fictif**, DÉMO-001, pour illustrer la recherche avec ou sans numéro ;
- un seul scénario d'arrivée prédéfini à Paris-Orly ;
- un tracé Paris centre → Paris-Orly **préenregistré**, calculé avec Geoapify, utilisant des données géographiques © contributeurs OpenStreetMap ;
- un calculateur local d'heure de départ avec durées et marges modifiables ;
- une sauvegarde locale et un cache PWA pour un usage hors connexion, après installation et sous réserve des limites du navigateur.

**Limites :** cette démonstration ne recherche pas des vols réels, ne géocode pas librement une adresse et ne calcule pas de nouvel itinéraire. Aucun appel à AeroDataBox ou Geoapify n'est effectué. Les horaires du vol, le terminal et le scénario sont fictifs. **Ne pas utiliser pour organiser un vrai déplacement.**

## Essayer

Après activation de GitHub Pages, la démonstration pourra être accessible à :

https://sidconsultant2011.github.io/atlas-voyageur-demo/

*Ce lien est prévu ; sa disponibilité dépend de l'activation de GitHub Pages.*

## Attributions

Itinéraire de référence : [Geoapify](https://www.geoapify.com/) — données géographiques © [contributeurs OpenStreetMap](https://www.openstreetmap.org/copyright).

## Feuille de route — priorité B6.3 INTERNATIONAL

**Décision du 21 octobre 2026 : la prochaine version a pour priorité absolue l'intégration complète des langues FR / EN / RU, avant toute nouvelle fonctionnalité.**

- **Français (FR)** : conserver la version de référence.
- **English (EN)** : traduire intégralement le parcours et les messages.
- **Русский (RU)** : traduire intégralement le parcours en alphabet cyrillique.
- Afficher un sélecteur FR / EN / RU accessible à toutes les étapes.
- Mémoriser le choix de langue sur l'appareil, y compris hors connexion.
- Adapter les formats de date et la présentation des horaires à la langue, sans confondre les fuseaux horaires et les heures locales.
- Traduire les avertissements « données fictives », la rubrique « Découvrir ATLAS VOYAGEUR », les actions, les aides et les messages d'erreur.
- Préserver le parcours, le calcul de départ, la navigation mobile fixe, les sauvegardes et le fonctionnement hors connexion.
- Valider les trois langues sur ordinateur et sur iPhone avant toute publication.

**État de diffusion :** la démonstration actuellement accessible à https://voyageur.atlascore.eu/ est en français uniquement. Les versions EN et RU sont prévues, **non encore disponibles**. La B6.2-PUBLIC reste la référence stable pour le retour arrière.

### Amélioration continue — « Votre avis nous intéresse »

**Décision validée le 21 octobre 2026 :** intégrer un dispositif de collecte de retours utilisateurs à ATLAS VOYAGEUR, en priorité dans le chantier B6.3, sans retarder l'internationalisation FR / EN / RU.

- Un accès discret « Votre avis nous intéresse » depuis l'application.
- Trois catégories : **suggestion**, **problème rencontré**, **retour d'expérience**.
- Commentaires **privés**, non publiés automatiquement ; aucun compte requis.
- Adresse de contact facultative pour réponse éventuelle.
- Interface intégralement **FR / EN / RU**, accessible sur mobile et adaptée au fonctionnement PWA.
- Réception effective via un service de formulaire sécurisé compatible avec GitHub Pages ; **aucune collecte annoncée comme active avant tests de transmission**.
- Mesures anti-spam, information claire sur les données personnelles, limitation des données collectées et modalités de conservation à définir avant activation.
- Centralisation des retours pour suivre les anomalies, regrouper les suggestions et prioriser les corrections dans la feuille de route.
- Validation préalable de la confidentialité, de la réception des messages et du traitement des données avant mise en production.

**Statut : exigence adoptée, non développée et non disponible dans la démonstration publique actuelle.**

## Projet

Prototype de démonstration publique distinct des versions de développement et d'ATLAS FLIGHT. Aucun secret API ni base de données privée n'est fourni dans ce dépôt.

**ATLAS VOYAGEUR**  
Conception et développement — **Joseph Vincent**  
Un projet **ATLAS CORE**  
© 2026 Joseph Vincent — Tous droits réservés sur les créations originales, sous réserve des droits des fournisseurs et contributeurs tiers indiqués ci-dessus.
