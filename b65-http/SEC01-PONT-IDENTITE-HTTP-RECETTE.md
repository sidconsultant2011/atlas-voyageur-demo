# B6.5 — SEC-01 — Pont identité fictive ↔ HTTP local — recette
**25 octobre 2026 — uniquement loopback 127.0.0.1, aucun fournisseur, aucune connexion publique**

## Objet
Relier `fictional_identities.py` aux opérations HTTP QA déjà présentes sans transformer les identités de test en un authentificateur accessible au navigateur.

## Livrables
- `b65-http/local_identity_bridge.py` : objet injecté côté serveur, reliant un cookie de session QA préexistant à un **jeton d'identité fictive créé et attribué uniquement par le harnais de tests**. La correspondance est maintenue en mémoire, non sérialisée ; les jetons bruts ne sont jamais exposés par l'API.
- `b65-http/local_http_facade.py` : paramètre optionnel `identity_bridge`. Lorsqu'il est défini, toutes les opérations HTTP QA sur les parcours (création, lecture, changement de libellé, suppression) consultent les autorisations de la base d'identités. Sans pont, les anciens tests de sessions QA restent fonctionnels.
- `b65-http/test_local_identity_bridge.py` : six scénarios HTTP loopback : identité autorisée, cookie non lié, IDOR lecture/écriture/suppression, opérations du propriétaire, désactivation de l'identité, refus CSRF/session forgée.

## Frontières et limites
Aucun endpoint de login ou d'enregistrement d'identité n'a été créé. `bind_fixture` est une méthode Python interne accessible au banc d'essai **seulement** : elle ne valide pas une identité humaine, ne vérifie pas actuellement qu'un cookie QA fourni est actif et ne doit jamais être utilisée comme point d'entrée en production. Le pont fonctionne dans une instance locale : il perd ses associations après redémarrage et n'est pas distribué. Les appels de révocation QA cookie restent séparés des révocations de jetons d'identité fictive.

Les succès de ces tests démontrent un contrôle d'autorisation sur données fictives et requêtes loopback, **pas** une authentification, un TLS, une architecture de sessions commerciales ou une protection d'un service Internet.

## Décision
**SEC-01 : étape d'intégration QA seulement ; P0-01 reste OPEN.** Les autres risques P0 restent OPEN. La connexion à `atlascore.eu` / `voyageur.atlascore.eu` est différée et exigera sa propre décision explicite de GO.

**Gouvernance : B6.5 recette — B6.3 NO-GO — aucun achat — aucune fusion main — site public inchangé — aucun test iPhone.**

*ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.*
