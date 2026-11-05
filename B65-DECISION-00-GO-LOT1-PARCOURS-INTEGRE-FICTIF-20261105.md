# 00 — B6.5 — GO du premier lot intégré fictif hors réseau

**Date :** 5 novembre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `22d889fbc0aafcafc57b4c6b5fbaff17808e5c6e`

## Sources vérifiées

- `B65-CADRAGE-01-PARCOURS-INTEGRE-FICTIF-20261101.md`, commit `22d889fbc0aafcafc57b4c6b5fbaff17808e5c6e` : proposition du chat 01, sans réalisation.
- `B65-DECISION-00-CADRAGE-PARCOURS-INTEGRE-FICTIF-20261101.md`.
- `B65-PV-ERGONOMIE-ET-CRITERES-PARCOURS.md` : référentiel P01–P16 et acquis ciblés historiques.
- `B65-CONTRAT-INTEGRATION-VOL-TRAJET-DEPART.md` : contrat d'intégration existant, non déployé.
- Le dépôt contient déjà `RECETTE-B65-PARCOURS-COMPLET.html`, `RECETTE-B65-VECTORIELLE.html`, `b65-calculateur/journey-controller.mjs`, `atlas-depart-engine.mjs` et des fixtures mock. Le parcours utilisateur unifié final n'est pas validé.
- La branche `main` demeure séparée. Le code public B6.2 doit rester inchangé.

## Décision

**GO — DÉVELOPPEMENT ET TESTS DU LOT 1 B6.5, ENTIÈREMENT FICTIF, SANS NOUVEL APPEL FOURNISSEUR.**

**Objectif unique :** dans la page QA existante `RECETTE-B65-PARCOURS-COMPLET.html`, permettre une sélection explicite d'un vol fictif AV103, le choix d'une origine fictive Paris ou Rozay, une représentation schématique honnêtement étiquetée du trajet vers le point indicatif Paris-Orly, et l'heure de départ estimée issue du contrôleur et du calculateur existants.

### Périmètre de réalisation

1. **Réutilisation prioritaire** : ne pas réécrire le moteur, la gestion des versions/invalidation, la simulation aérienne ou la cartographie historique.
2. **Vols** : réutiliser les fixtures AV103 (prévu, retard, atterri, annulé, absent/périmé) ; afficher les identifiants, statuts, horaires et sources fictifs, sans inventer de provenance, fuseau ou horodatage fournisseur non renseigné. Tout complément de métadonnées fictives doit être explicite et validé par des tests.
3. **Origines** : sélection/réinitialisation de Paris et Rozay comme **origines de simulation**, jamais comme géocodage libre. Préserver P05/P06/P11 déjà reçus sur la page vectorielle distincte sans déclarer leur validation dans la page unifiée.
4. **Trajet** : afficher un schéma indicatif ou une géométrie réellement liée à la fixture choisie ; aucune reprise trompeuse d'un tracé Paris–Orly pour Rozay. Destination : « Paris-Orly — point d'aéroport indicatif », ni terminal, ni parking, ni rendez-vous vérifié.
5. **Heure** : obtenir le calcul exclusivement de `journey-controller.mjs` / `atlas-depart-engine.mjs`, sans formule concurrente ; afficher dates locales complètes avec zone `Europe/Paris` clairement identifiée et référence UTC, date/heure de simulation et marges/hypothèses. Conserver la conception UTC/offset et ne pas revendiquer une validation internationale complète.
6. **États bloquants** : annulation, absence d'heure, origine non sélectionnée, itinéraire indisponible, scénario réseau indisponible sans appel réseau -> suspendre le conseil et retirer tout itinéraire obsolète. Retard et changement d'origine -> invalider puis recalculer, sans réutiliser des réponses périmées.
7. **UX** : page QA mobile sobre noir/or champagne, libellés fiables et accessibles ; ne pas considérer FR/EN/RU intégralement qualifiées ni la revue iPhone effectuée avant leur preuve.
8. **Fichiers autorisés** : `RECETTE-B65-PARCOURS-COMPLET.html` ; si indispensable, enrichissement strictement **fictif** de `b65-calculateur/mock-adapters.mjs` ; un fichier de tests B6.5 ciblés. Aucune modification du contrôleur ou du calculateur sans revenir au 00 pour arbitrage motivé.
9. **Contrôles** : tests ciblés du lot (nominal, retard, annulation, absence, itinéraire, invalidation, réseau simulé, date locale/UTC, absence d'appel externe) ; non-régression des suites existantes ; vérifier l'état et les journaux du workflow GitHub Actions sur commit technique exact. Distinguer tests locaux, CI et revue manuelle iPhone/PC. **Ne pas revendiquer de test iPhone ou PC sans exécution attestée**.
10. **Livraison** : rapport technique, commit exact, diff, résultats et limites au 00, puis recette indépendante chat 03 décidée par le 00. Ce GO n'est pas un GO de publication ou production.

### Exclusions absolues

Aucun appel nouveau à Geoapify, AeroDataBox/RapidAPI, MapLibre CDN ou autre fournisseur ; aucun achat, clé API, consommation de crédits, changement `index.html`, `i18n.js`, `RECETTE-B65-VECTORIELLE.html`, `RECETTE-B65-CARTOGRAPHIE.html`, `main`, CNAME, domaine public, site public ou déploiement. Aucune reprise des expérimentations SQLite R1-C01, C03, VFS, SIGKILL ou G04.

## États conservés

- B6.5 : **EN RECETTE**, parcours lot 1 à développer puis à qualifier.
- AC-08 et AC-13 : réceptionnés avec réserves.
- R1-C01 : PARTIEL, **gel technique maintenu** ; R1-RD01, R1 et P0-01 ouverts.
- B6.3, G04 et production : NO-GO.
- B6.2-PUBLIC sur main : **inchangée** par la présente décision.

## Prochaine action unique

Transmettre au chat 01 le GO du lot 1 B6.5 fictif hors réseau et demander le code, les tests et les preuves sur commit exact, sans publication.
