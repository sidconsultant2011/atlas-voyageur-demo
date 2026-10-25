# Décision 00 — SEC-01 R1-RD01 — Conception VFS SQLite uniquement

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Chantier prioritaire unique :** conception documentaire d'un dispositif VFS SQLite d'observation interne du COMMIT.  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant arbitrage :** `ff0f03cc25f48f4035facef4a234bbaf914d00a5`.

## Source examinée

Rapport de faisabilité du chat 01 : `b65-http/SEC01-R1-RD01-FAISABILITE-VFS-RAPPORT-01-20261025.md`. Le rapport a été consulté dans GitHub ; comparaison au précédent HEAD : un seul document ajouté, aucun code applicatif modifié. Les preuves historiques du banc restent GitHub Actions n°90 (`40185721195`), 15/15 SIGKILL sur cinq marques externes, sans interruption interne démontrée.

## Décision

**GO de conception technique documentaire uniquement. NO-GO de mise en œuvre, de compilation, d'installation de dépendances et d'essais.**

Le chat 01 est autorisé à rédiger une spécification détaillée et une analyse GO/NO-GO de réalisation. Cette décision ne vaut ni validation de durabilité ni approbation de production.

## Livrable attendu — exigences

1. **Architecture :** modèle du wrapper VFS `sqlite3_vfs` et `sqlite3_io_methods`, choix et enregistrement de VFS dans un banc enfant isolé ; stratégie vérifiable pour les deux ouvertures (base principale et `ATTACH`). Vérifier le besoin de version, ABI et bibliothèque SQLite identique à celle du runtime Python ; ne pas affirmer leur compatibilité sans preuve.
2. **Points d'observation :** spécifier les événements `xOpen`, `xWrite`, `xSync`, `xDelete`, `xFileControl` utiles, les métadonnées de fichiers, le lien transactionnel, les preuves avant/après délégation et la distinction journal individuel / super-journal. La présence d'un super-journal n'est pas présumée.
3. **Déclenchement :** décrire l'interruption contrôlée du seul processus enfant sur un événement SQLite interne effectivement atteint, plutôt que sur délai ou marque Python externe ; inclure PID, identifiant d'événement, barrières et attestations, ainsi que les cas où une fenêtre n'est pas atteignable.
4. **Neutralité et limites :** analyse du comportement observateur (latence, E/S, fsync, verrous) et différence éventuelle du moteur instrumenté, avec critère d'abandon si la technique invalide la comparaison.
5. **Preuves conservées :** spécifier la capture synchronisée des deux bases et de leurs fichiers de journalisation éventuels **avant toute ouverture par SQLite**, leur copie de travail, inventaire, hashes SHA-256, contrôle des accès et de la rétention ; données fictives et aucun secret.
6. **Raccordement applicatif :** démontrer sur plan comment la voie `LocalIdentityBridge._persistent_journey()` serait réellement couverte sans modifier son comportement, et ce qui resterait hors périmètre.
7. **Environnement :** prérequis Linux, moteur SQLite, mode rollback/DELETE, synchronous/FULL, système de fichiers local, paramètres et exclusions (WAL, coupure électrique, crash OS, stockage réseau et architecture distribuée).
8. **Décision future :** matrice de faisabilité, risques, conditions de validation du banc, critères d'arrêt, coûts/complexité estimés qualitativement et recommandation **GO / NO-GO / preuve non réalisable dans le cadre retenu**, sans promesse de réussite.

**Livrable :** document versionné dans `b65-http/`, uniquement documentaire. Le chat 00 examinera le document avant d'autoriser séparément, éventuellement, un prototype isolé.

## Restrictions et statuts

Aucun développement ni compilation de VFS, aucune installation, aucune nouvelle injection ni campagne CI, aucune modification des modules existants, aucune interruption système hôte. Aucun achat, fusion `main`, fournisseur réel, publication ou modification du site public.

**RD01-R01 à RD01-R04 OUVERTES — R1-RD01 OUVERTE — R1-C01 PARTIEL — R1 OUVERTE — P0-01 OUVERT — B6.5 EN RECETTE — B6.3 NO-GO — PRODUCTION NO-GO.**

## Prochaine action unique

Chat 01 : rédiger et versionner la conception technique de la VFS SQLite et ses conditions GO/NO-GO, puis remettre au 00 le commit et le document pour arbitrage, sans réalisation technique.
