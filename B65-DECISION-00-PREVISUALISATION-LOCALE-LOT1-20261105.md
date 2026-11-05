# 00 — B6.5 lot 1 — Autorisation de prévisualisation locale privée

**Date :** 5 novembre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche documentaire :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `ebd0dcecb5298039a213523dd8afd657338df501`  
**Commit applicatif à visualiser exclusivement :** `373844940d49ab65061ae659e48e6e72eeeac038`

## Origine de l'arbitrage

Le chat 03 a remis le PV `PV-03-B65-LOT1-VISUEL-20261105` : contrôle préparatoire GitHub PASS mais **recette navigateur PC NON EXÉCUTÉE** et **recette Safari iPhone NON EXÉCUTÉE**, faute d'accès à une prévisualisation exécutable et à un iPhone.

La couverture automatisée avait été réceptionnée avec réserves par `B65-DECISION-00-RECEPTION-LOT1-FICTIF-20261105.md` ; CI n°253 réussie sur le commit applicatif exact.

Contrôle GitHub direct du 00 avant décision : la page `RECETTE-B65-PARCOURS-COMPLET.html` du commit applicatif importe localement `./b65-calculateur/atlas-depart-engine.mjs` et `./b65-calculateur/journey-controller.mjs`. Aucun appel fournisseur explicite n'a été trouvé dans cette page lors de l'inspection statique. Cela **ne constitue pas** une preuve d'absence de toute requête réseau au moment de l'exécution ; la recette doit le constater.

## Décision officielle

**GO — PRÉVISUALISATION PRIVÉE LOCALE ET RECETTE MANUELLE PC/IPHONE DU LOT 1, SOUS CONDITIONS.**

Ceci autorise un moyen technique de consultation **temporaire**, pas une nouvelle livraison publique ni le déploiement d'une application accessible depuis Internet.

1. Récupérer une **copie locale isolée** du dépôt sur le **commit exact** `373844940d49ab65061ae659e48e6e72eeeac038`, sans travailler sur `main`, sans modifier le dépôt distant et sans `git push`. Vérifier `git rev-parse HEAD` et la présence des fichiers relatifs.
2. Pour PC : servir les fichiers avec un simple serveur HTTP statique local, par exemple `python -m http.server 8765 --bind 127.0.0.1` depuis la copie figée ; ouvrir `http://127.0.0.1:8765/RECETTE-B65-PARCOURS-COMPLET.html` dans Chromium. Le choix du port 8765 est indicatif. Ne pas utiliser un lien `file://` si les modules ES sont bloqués par l'origine.
3. Pour iPhone Safari seulement si le PC et l'iPhone sont sur le **même réseau privé de confiance** : arrêter le serveur localhost puis redémarrer un serveur HTTP statique lié **uniquement à l'adresse IPv4 privée du PC**, pas à toutes les interfaces Internet ; utiliser `http://<IP_PRIVEE_PC>:8765/RECETTE-B65-PARCOURS-COMPLET.html`. Restreindre l'accès via le pare-feu Windows au profil privé et, si possible, à l'IP privée de l'iPhone ; désactiver l'accès dès la fin des essais. Ne pas créer de règle globale exposant le port. Ne jamais employer tunnel public, transfert de port routeur, DNS public ou proxy public sans arbitrage distinct.
4. Vérifier dans les outils réseau du navigateur l'absence de requêtes à AeroDataBox, Geoapify et autres fournisseurs réels, ainsi que l'absence de clé et de données personnelles dans les échanges ; arrêter et remonter au 00 si constat contraire.
5. Suivre les scénarios de recette déjà mandatés : AV103, Paris/Rozay, horaires/UTC, retard, annulation, données périmées, réseau fictif indisponible, schéma CSS effectivement masqué ; vérifier la lisibilité PC et les commandes tactiles iPhone. Capturer les preuves utiles avec URL de prévisualisation privée expurgée si nécessaire, SHA exact, environnement, navigateur, date et verdict PASS/FAIL/NON EXÉCUTÉ.
6. Le chat 03 ne peut revendiquer un PASS iPhone sans observation matérielle ni captures attestées. Si le dispositif LAN privé est impraticable, statut **NON EXÉCUTÉ** et retour au 00, sans publication de la branche pour contourner le blocage.

## Frontières et interdictions

Aucun changement de code, de workflow, de branche `main`, de `index.html`, de `CNAME`, de DNS, du site `voyageur.atlascore.eu`, de l'hébergement public ou de la configuration du site. Aucun fournisseur ou abonnement réel activé, aucune donnée personnelle réelle, aucun déploiement cloud, aucun nouveau chantier R1-C01, C03 ou VFS. Aucun essai d'interface n'est attesté par cette décision elle-même.

Statuts : lot 1 réception automatisée favorable avec réserves ; recette visuelle PC/iPhone **NON EXÉCUTÉE** à date ; B6.5 **EN RECETTE** ; R1-C01 **PARTIEL / gel technique** ; P0-01 ouvert ; B6.3, G04 et production **NO-GO**.

## Prochaine action unique

Mettre à disposition du chat 03 une copie locale exécutable du commit exact pour réaliser en premier la recette visuelle PC, puis la recette iPhone seulement dans le cadre LAN privé autorisé et avec preuves distinctes.
