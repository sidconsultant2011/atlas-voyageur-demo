# B6.5 — P0-01 — Limitation de débit persistante des sessions
Date : 25 octobre 2026 — QA HTTP locale, aucun fournisseur.

## Livraison
- `b65-http/persistent_sessions.py` : table SQLite `request_events` indexée par hash de session et date ; fenêtre glissante configurable (défaut 60 s), plafond par session (défaut 8).
- Une transaction `BEGIN IMMEDIATE` sérialise la vérification de session, le contrôle CSRF, le nettoyage des événements expirés, le comptage et l'insertion du nouvel événement. Une demande au-delà du plafond retourne `429 RATE_LIMITED`.
- `b65-http/test_persistent_rate_limit.py` : huit tests portant sur redémarrage, fenêtre glissante, isolation des sessions, 30 accès concurrents, CSRF invalide, révocation, expiration et configuration.
- La suite existante `python3 -m unittest discover -s b65-http -p 'test_*.py' -v` est exécutée par GitHub Actions sur chaque modification du dossier.

## Preuve
GitHub Actions n°54, commit `f1a22ed96815734dbafbe68ea2300d29297c1908` : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40171521151 — succès.
Dans le test concurrent à plafond 5 : 5 admissions, 25 refus pour 30 tentatives avec connexions distinctes au même fichier local.

## Limites P0-01
Le compteur est durable sur disque et transactionnel **sur un seul fichier SQLite accessible localement** ; il n'est ni distribué entre hôtes ni accompagné d'un quota par IP, compte, origine et budget fournisseur global. Le test utilise plusieurs connexions et threads sur une seule machine, pas plusieurs centres de données. Une authentification utilisateur réelle, HTTPS, cookies Secure, une politique de purge globale et une revue de sécurité indépendante restent nécessaires. Les données de l'ancienne façade mémoire n'ont pas été migrées. Les sessions QA ne constituent pas un mécanisme de compte utilisateur commercial.

**P0-01 reste OPEN ; aucune autorisation de raccordement à atlascore.eu.** Ce raccordement demeure une étape prévue seulement après les validations nécessaires et un GO explicite.

B6.5 en recette — B6.3 NO-GO — aucun achat — aucune fusion sur main — site public inchangé — aucun test iPhone nécessaire.
