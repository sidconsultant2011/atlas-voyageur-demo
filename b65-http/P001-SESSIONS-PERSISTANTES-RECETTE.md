# B6.5 — P0-01 — Persistance locale des sessions, expiration et révocation
Date : 25 octobre 2026. **QA hors ligne uniquement. P0-01 reste ouvert.**

## Livraison
- `b65-http/persistent_sessions.py` : stockage local SQLite réel, sessions et parcours sur disque, identifiants de session et jetons CSRF aléatoires ; seuls leurs hash SHA-256 sont stockés. Vérification d'expiration basée sur une horloge murale injectable (`time.time`, et non `time.monotonic` qui ne survit pas au redémarrage).
- `b65-http/local_http_facade.py` : accepte le stockage persistant comme adaptateur ; `POST /api/v1/qa/session/revoke` exige le cookie valide et un jeton CSRF valide, révoque côté stockage et expire le cookie QA.
- `b65-http/test_persistent_sessions.py` : création de session, réouverture de base, parcours conservé, expiration et révocation, absence de token brut sur disque, accès croisé refusé, et parcours HTTP inaccessible après révocation.
- CI existante : tests Python HTTP, SQLite et Node. Aucun appel fournisseur.

## Invariants
Une session révoquée ou expirée n'autorise plus lecture, modification ou suppression de parcours après ouverture d'une nouvelle instance de stockage. La session est propriétaire des parcours qu'elle crée, même après réouverture. La valeur brute d'un jeton n'est pas enregistrée en base.

## Limites bloquantes
Le serveur est réservé au loopback `127.0.0.1`, sur HTTP non chiffré ; cookie QA **sans Secure**, donc impropre à une publication Internet. Il n'existe aucune identité utilisateur réelle, aucun coffre de secrets, aucune protection de la base disque au repos, aucune purge des sessions expirées, aucune protection distribuée des quotas. **Important** : le compteur rate-limit en mémoire de l'ancien état n'est pas implémenté dans l'adaptateur persistant ; sa mise en conformité est à traiter avant levée de P0-01. Il manque les scénarios de suppression/renouvellement de session, test multi-processus de révocation et revue sécurité indépendante.

La validation des tests ne signifie pas homologation de sécurité. Aucun domaine `atlascore.eu` ou `voyageur.atlascore.eu` n'a été raccordé ni modifié. Le **raccordement du site est différé**, après levée documentée des risques prioritaires, décision GO de déploiement distincte et validation explicite de l'utilisateur.

**Gouvernance inchangée : B6.5 recette — B6.3 NO-GO — aucun achat — aucune fusion `main` — site public inchangé — aucun test iPhone.**
