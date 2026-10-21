# Prévisualisation HTTPS iPhone — B6.3 INTERNATIONAL

**STATUT : CONFIGURATION PRÉPARÉE, DÉPLOIEMENT NON EFFECTUÉ. AUCUNE VALIDATION DE PRODUCTION.**

## Objectif

Tester B6.3 sur iPhone via un site HTTPS séparé, en conservant intégralement la B6.2 sur `https://voyageur.atlascore.eu/`. La branche `main` ne doit jamais être fusionnée ni modifiée pour cet essai.

## Solution recommandée : projet Cloudflare Pages indépendant

L'utilisateur doit posséder un compte Cloudflare et autoriser la liaison GitHub. Aucun identifiant ou clé API ne doit être transmis dans la conversation.

1. Aller dans le tableau de bord Cloudflare, **Workers & Pages** et créer **un nouveau projet Pages**, lié à GitHub.
2. Sélectionner uniquement `sidconsultant2011/atlas-voyageur-demo`.
3. Nommer le projet, par exemple `atlas-voyageur-b63-qa` **si ce nom est disponible**. Ne pas ajouter `voyageur.atlascore.eu` ou un autre domaine personnalisé.
4. Choisir comme **branche de production de ce nouveau projet Pages uniquement** : `feature/b6-3-international` ; cette notion concerne ce nouveau projet de prévisualisation, **pas la production réelle ATLAS VOYAGEUR**.
5. Framework : **None** ; commande build : vide ; répertoire de sortie : `/` (racine, fichiers statiques). Adapter si l'interface Cloudflare demande `.`.
6. Valider le déploiement, puis relever l'**URL HTTPS réellement créée** depuis les détails de déploiement. L'adresse `https://atlas-voyageur-b63-qa.pages.dev` est illustrative et ne doit pas être présentée comme réelle avant confirmation.
7. Vérifier qu'une ouverture de `https://voyageur.atlascore.eu/` affiche toujours B6.2. La présence de `CNAME` dans le dépôt GitHub n'est pas une instruction de changer le DNS Cloudflare ; **ne modifier aucun paramètre OVH**.
8. Le fichier `_headers` propre à la branche interdit l'indexation par les moteurs ; la consigne ne garantit **pas** un accès privé. Si confidentialité souhaitée, configurer l'accès protégé (Cloudflare Access) et vérifier l'accès depuis l'iPhone avant toute diffusion.

### Recette iPhone

- Safari normal : page HTTPS, intro activée / désactivée, fermeture et réouverture.
- FR / EN / RU : navigation, encodage cyrillique, absence de débordement, textes lisibles.
- Démonstration fictive : rechercher `DEMO001` ou la date/heure de test, sélectionner, consulter l'étape Accueillir.
- Trajet 20 puis 35 minutes : départ 17h30 puis 17h15, heure de rencontre 18h15.
- Sauvegarde/restauration, langue mémorisée, légendes EN/RU et notifications.
- Ajout à l'écran d'accueil de l'iPhone **uniquement en veillant à distinguer l'app QA de l'app publique existante** ; vérifier la non-interférence des caches et données stockées sur des origines différentes.
- Mode avion **après une première visite avec le SW installé** : vérifier ouverture, parcours, langue, calculs et restauration.
- **Aucune fusion** tant que ces contrôles ne sont pas validés.

## Après validation

L'environnement de prévisualisation pourra être désactivé ou supprimé. Conserver la démonstration publique B6.2 tant que le responsable du projet n'a pas autorisé explicitement la publication de B6.3.
