# B6.5 — P0-01 — Façade HTTP locale — recette

Date : 25 octobre 2026. Statut : **prototype QA local uniquement ; P0-01 encore OPEN.**

## Périmètre livré
- `b65-http/local_http_facade.py` : petit serveur HTTP Python standard library ; création possible uniquement avec `host='127.0.0.1'`, port de test aléatoire.
- `b65-http/test_local_http_facade.py` : vérifications réelles via HTTP de loopback ; aucun appel externe.
- `/api/v1/qa/session` : création de session fictive et jeton CSRF ; cookie `HttpOnly; SameSite=Strict`. Pas de `Secure` dans le test HTTP local **non HTTPS** ; ce mécanisme ne peut donc pas être repris tel quel en production.
- `GET /api/v1/qa/state` : accès uniquement avec cookie de session valide.
- `POST /api/v1/qa/echo` : payload borné, content-type JSON, session, jeton CSRF, contrôle Origin ; renvoie uniquement un écho fictif.
- CORS : seule origine `http://127.0.0.1:8765` en liste blanche ; aucune autorisation au reste du réseau.
- Limite : 8 requêtes vérifiées par minute par session, état en mémoire, sans persistance.
- En-têtes de protection : CSP restrictive, no-store, nosniff, no-referrer.
- Aucun accès à AeroDataBox/Geoapify, aucune clé, aucun routage de fournisseurs, aucun déploiement.

## Contrôles de réception simulés
Lancement : `python3 -m unittest discover -s b65-http -p 'test_*.py' -v`. Le workflow B6.5 exécute aussi les suites Node et SQLite précédentes.

Scénarios : bind non-loopback refusé, authentification absente refusée, origine non admise refusée, attributs cookie, CSRF absent et erroné, deux sessions indépendantes et cookie forgé, écriture autorisée avec CSRF valide, limitation 429, preflight CORS, endpoint inconnu refusé et type de contenu incorrect.

## LIMITES / conditions de levée P0-01
La façade est **volontairement incomplète** : pas de TLS, pas d'authentification réelle d'utilisateur, pas de liaison forte session-parcours métier, pas de protections anti-abus par IP sur un déploiement, pas de stockage durable des sessions, pas de garantie d'isolation multi-instance, pas d'audit ou de test de sécurité indépendant. Le jeton CSRF est délivré au client qui a initié la session locale ; pas de modèle d'identité à compte utilisateur. Les clés/cookies en production nécessiteront `Secure`, TLS et durcissement supplémentaires.

**P0-01 reste OPEN** jusqu'aux preuves sur la façade complète locale, avec IDOR sur vrais parcours, contrôles session durable et revue de sécurité. Le succès CI signifie que les scénarios QA listés sont passés, pas une homologation réseau ou sécurité.

**Gouvernance : B6.5 en recette — B6.3 NO-GO — aucun achat — aucune fusion `main` — site public inchangé — aucun test iPhone.**
