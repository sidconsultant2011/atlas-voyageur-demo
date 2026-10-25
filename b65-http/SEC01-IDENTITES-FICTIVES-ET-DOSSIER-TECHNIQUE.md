# ATLAS VOYAGEUR — B6.5 — SEC-01 : identité fictive locale et autorisations
**25 octobre 2026 — Prototype SEC-01 de laboratoire, aucune identité réelle ni connexion fournisseur.**

## Réalisé
- `b65-http/fictional_identities.py` : registre SQLite **de deux identités de test explicites** (`qa-alice`, `qa-bob`), sessions aléatoires, hash des jetons stockés, durée de vie absolue, révocation, désactivation d'identité, et parcours associés à l'identité.
- Les opérations lire, modifier et supprimer un parcours sont filtrées en base par `identity_id`; une identité différente ne peut pas accéder à ce parcours. Le stockage persiste entre réouvertures de SQLite.
- `b65-http/test_fictional_identities.py` : 10 tests de séparation, révocation, expiration, persistance, accès illégitime et absence du jeton brut dans le fichier.
- Les tests sont automatiquement récupérés par la commande CI Python existante `python3 -m unittest discover -s b65-http -p 'test_*.py' -v`.

## Avertissement de sécurité
L'opération `open_session(identity_id)` est **réservée au harnais de tests local**. Elle n'authentifie pas un être humain : connaître `qa-alice` suffit à obtenir une session. Le module n'est **pas relié à la façade HTTP publique** et ne doit jamais être exposé comme endpoint de connexion. Son objectif est de vérifier les frontières d'autorisation *une fois l'identité supposée établie*. Pour P0-01, il reste à concevoir une authentification réelle, l'émission sûre de session, TLS, contrôle des risques d'abus, autorisation complète et revue indépendante.

**P0-01 reste OPEN.** Aucun GO fournisseur ou site public.

## Trajectoire documentaire intégrale (commercialisation éventuelle — différée)
Lorsqu'une mise en vente sera envisagée, produire et tenir à jour un **dossier technique exhaustif de bout en bout** : architecture et ADR, composants et versions, dépendances/licences, schémas de données et migrations, contrats API, gestion identité/sessions, sécurité et modèle de menaces, clés/secrets, confidentialité/RGPD, opérations CI/CD, supervision/alertes, quotas et facturation, plans de reprise/rollback, essais et preuves, performance, accessibilité, UX, procédures d'exploitation, procédures de support, maintenance, coûts, conformité et documentation d'installation/usage.

La documentation doit être versionnée, réconciliée avec l'état du code et accompagnée d'un manifeste de preuves et de continuité avant toute revue commerciale. **Ce registre ne lance pas une commercialisation** : priorité actuelle à terminer ATLAS VOYAGEUR en recette.

## Gouvernance
B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion `main` ; aucun changement de `atlascore.eu` ni de `voyageur.atlascore.eu` ; aucun test iPhone requis.

*ATLAS VOYAGEUR — Le bon vol. Le bon trajet. Le bon moment.*
