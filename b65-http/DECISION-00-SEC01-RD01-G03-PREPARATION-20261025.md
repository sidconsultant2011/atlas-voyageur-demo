# Décision 00 — SEC-01 R1-RD01 — Préparation probatoire G03

**Date :** 25 octobre 2026
**Projet :** ATLAS VOYAGEUR — B6.5
**Branche autorisée :** `feature/b6-5-cartographie-interactive`
**HEAD vérifié avant arbitrage :** `4d780f8501f73d7aa7015580487a3f7ada713acb`
**Chantier prioritaire unique :** préparation de la preuve d'observation d'un événement VFS lié au COMMIT multi-fichiers, sans injection de panne.

## Sources vérifiées et acquis

- Décision de clôture de conservation G05 : `b65-http/DECISION-00-SEC01-RD01-G05-CLOTURE-CONSERVATION-20261025.md`.
- Conception VFS : `b65-http/SEC01-RD01-CONCEPTION-TECHNIQUE-VFS-20261025.md`.
- Rapport du prototype VFS : `b65-http/SEC01-RD01-VFS-ETAPE1-RAPPORT-20261025.md`.
- Avis du chat 02 remis au 00 le 25 octobre 2026 : « 02 — SÉCURITÉ P0 — Arbitrage G03/G04 », **GO conditionnel de préparation G03 / NO-GO expérimental G04**.
- CI n°108 (déjà reçue) : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40205084577, commit `1071fbe3ce35ba5556e53c437acf928c730d9e0b`, 223 exécutions réussies.
- Copies documentaires privées G05 : Drive `1Fo7mrKPJtBMzVDXCBg3wmRuBnIhbt3s6` (ZIP) et `19Y6CykkO5-xMHw5x2rJvXFJa_0FdUwvF` (fiche), archivage documentaire 04 clôturé, sans qualifier la durabilité.

## Arbitrage du 00

**GO CONDITIONNEL — PRÉPARATION PROBATOIRE DE G03 UNIQUEMENT.** **NO-GO pour les injections G03/G04 et pour l'arrêt causal G04.**

Le chat 01 est autorisé à travailler uniquement dans le banc fictif isolé et sa documentation, à partir de l'existant, afin d'établir si un événement VFS effectivement émis pendant un COMMIT multi-fichiers peut être identifié, lié à la transaction et consigné sans changer matériellement les garanties évaluées.

### Travaux autorisés

1. Vérifier l'identité du moteur/ABI SQLite déjà constatée sous CI et analyser la couverture exacte du wrapper `sqlite3_io_methods` version 1 par rapport au VFS natif ; préciser le risque d'altération d'ordonnancement, de journaux, de `xFileControl` et de synchronisation (porte G06). **Ne pas déclarer le wrapper équivalent par principe.**
2. Construire la **spécification probatoire** des événements (types et chemins réels des fichiers, `xWrite`, `xSync`, `xDelete`, `xFileControl`, pré/post-délégation, codes retour, séquence, PID, phase, transaction, candidat super-journal). Distinguer événement réellement observé et interprétation du point logique de COMMIT.
3. Décrire un mécanisme fiable de traçabilité et de synchronisation de preuves hors bases SQLite, avec effets observateurs documentés ; concevoir sa future conservation avec G05 déjà acquis.
4. Documenter la relation future à `LocalIdentityBridge._persistent_journey()` : conditions exigeant deux bases effectivement mutées et instrumentées, sans changer ni appeler le code métier dans cette phase.
5. Si nécessaire et **uniquement pour vérifier la disponibilité et l'identification des événements G03 lors d'un COMMIT qui se termine normalement**, réaliser des ajustements ciblés au code de banc fictif/trace et des contrôles **non destructifs**, sans attente en callback ni arrêt de processus. Ne pas installer de nouvelle dépendance externe, remplacer silencieusement le moteur SQLite ou changer le code applicatif. Toute modification de banc et tout test exécuté devront être liés à un commit et rapportés séparément entre local et CI.
6. Livrer une matrice **atteint / observable sous conditions / non démontré / non exploitable** et une recommandation de **GO/NO-GO pour une future expérimentation**, avec conditions d'arrêt. Un point non atteint n'est pas une panne observée ni un défaut de SQLite.

### Interdictions explicites

- **Aucun SIGKILL**, aucun crash, aucune injection de faute, aucune suspension ou barrière bloquante dans un callback VFS, aucun essai G04.
- Aucun changement dans `local_identity_bridge.py`, `persistent_sessions.py` ou autre module applicatif existant.
- Aucune substitution du moteur SQL, dépendance ajoutée sans nouvel arbitrage, panne système, stockage réel, donnée personnelle, secret, activation fournisseur ou déploiement.
- Aucune fusion sur `main`, publication ou modification du site public.
- Ne pas rejouer à l'identique les anciennes campagnes sans justification.

## Conditions pour une décision expérimentale future, non accordée ici

Le 00 exigera un examen du dossier par le chat 02 puis une nouvelle décision explicite avant tout arrêt causal G04. La préparation doit éclairer notamment :
- G03 : preuve discriminante du type réel de fichier et de l'événement du COMMIT effectivement atteint.
- G06 : effets et limitations du wrapper, comparaison pertinente avec VFS native.
- G05 : méthode de préservation des journaux potentiellement chauds **avant** réouverture lors d'une éventuelle panne ultérieure, non qualifiée actuellement.
- G04 : design de barrière et accusé de réception sous PID vérifié **uniquement comme proposition documentaire**, sans réalisation.
- G08 : programme de réception indépendante du 03 après une expérimentation future autorisée.

## État inchangé

**G01 recevable (runtime CI ciblé), G02 recevable (banc fictif), G05 global partiel** (archivage fichiers propres reçu, conservation Drive clôturée). **G03 non encore qualifiée ; G04 non autorisée.**

**VFS-R01 à R05 et RD01-R01 à R04 ouvertes ; R1-RD01 ouverte ; R1-C01 partiel ; R1 ouverte ; P0-01 ouvert ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.**

Aucune preuve nouvelle de durabilité ne découle du présent arbitrage.

## Prochaine action unique

Transmettre au chat 01 cette décision pour préparer uniquement le dossier G03 de preuve d'événement interne et de neutralité, sans injection de panne, puis présenter ses constats au 00 pour nouvel arbitrage.
