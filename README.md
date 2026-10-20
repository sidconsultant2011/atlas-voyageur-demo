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

## Projet

Prototype de démonstration publique distinct des versions de développement et d'ATLAS FLIGHT. Aucun secret API ni base de données privée n'est fourni dans ce dépôt.

Tous droits réservés sur le code et les contenus originaux, sauf les droits propres aux fournisseurs et aux données tierces indiqués ci-dessus.
