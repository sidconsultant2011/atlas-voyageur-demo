# B6.5 — Contrôle automatique de la page de simulation

Date : 24 octobre 2026.

## Couverture ajoutée
`b65-calculateur/simulation-ui.test.mjs` extrait et exécute le module JavaScript de `RECETTE-B65-PARCOURS-COMPLET.html` dans un faux DOM minimal, avec le véritable contrôleur `journey-controller.mjs`. Il ne contacte aucun service externe et ne nécessite aucune dépendance npm.

Il exerce les événements : arrivée révisée (17h25), vol annulé (suspension), retour à l'état nominal, changement de trajet (17h50 pour Paris dans la fixture), absence d'adresse (suspension), augmentation marge trafic (17h15), données périmées (suspension), atterrissage confirmé fictif (17h05 avec marge modifiée), et sortie passager vide (suspension).

## Déclenchement
Le workflow `.github/workflows/b65-calculateur-tests.yml` déclenche `node --test b65-calculateur/*.test.mjs` pour toutes modifications du dossier de calcul ou de la page de simulation.

## Limites
- C'est un test d'intégration JavaScript **sans rendu réel** : il ne prouve pas l'affichage visuel, Safari iPhone, les tailles tactiles ou l'accessibilité complète.
- Les scénarios aérien et routier sont **entièrement fictifs**.
- La réussite GitHub Actions du nouveau test doit être consultée sur le workflow après son dernier commit. Ne pas déduire le PASS du seul enregistrement du fichier.
- Éviter de renouveler des tests iPhone sans anomalie détectée.

## Gouvernance
B6.5 recette, B6.3 NO-GO ; aucun achat, aucune fusion sur `main`, site public inchangé.
