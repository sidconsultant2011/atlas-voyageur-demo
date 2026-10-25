# B6.5 — P0-01 — Isolation des parcours et IDOR HTTP local
Date : 25 octobre 2026. **Recette hors ligne, bouclage IPv4 127.0.0.1, aucun fournisseur.**

## Changement
`b65-http/local_http_facade.py` possède désormais un registre de parcours fictifs dont chacun conserve une clé `owner` liée à la session créatrice. Les identifiants de parcours sont aléatoires. Toute lecture, écriture ou suppression impose une session valide et la correspondance du propriétaire ; l'accès croisé retourne **404** (pas d'information sur l'existence du parcours). Le client n'est jamais autorisé à choisir son propriétaire.

Opérations QA supplémentaires :
- `POST /api/v1/qa/journeys` — crée un parcours fictif propre à la session avec contrôle CSRF.
- `GET /api/v1/qa/journeys/{id}` — lit seulement le parcours détenu.
- `POST /api/v1/qa/journeys/{id}/label` — change le libellé propriétaire, avec contrôle CSRF.
- `DELETE /api/v1/qa/journeys/{id}` — supprime seulement le parcours détenu, avec contrôle CSRF.

## Tests ajoutés
`b65-http/test_journey_isolation.py` contient 7 scénarios (lecture, modification, suppression inter-sessions refusées ; opérations propriétaires permises ; CSRF manquant ; identifiant inconnu et session absente ; tentative avec jeton CSRF d'un autre utilisateur). Ils passent par une véritable connexion HTTP à la boucle locale, sans fournisseur. Le fichier de test importe la classe de base HTTP existante : les tests de base peuvent donc être exécutés deux fois par découverte unittest, sans étendre le périmètre fonctionnel.

## Critère P0-01
Le contrôle IDOR des parcours fictifs est couvert **dans ce seul modèle local en mémoire**. P0-01 **reste OPEN** : identité utilisateur réelle, persistance des sessions, HTTPS/cookie Secure, gestion des expirations et de la suppression, contrôle métier complet, protections d'exploitation et revue indépendante restent absents. Ces tests ne prouvent pas une résistance à des attaques sur un service Internet.

Gouvernance : B6.5 recette, B6.3 NO-GO ; aucun achat ; aucun merge `main` ; site public inchangé ; aucun test iPhone.
