# Décision 00 — SEC-01 R1-RD01 — Prototype VFS préqualification étape 1

Date : 25 octobre 2026.
Chantier prioritaire unique : préqualification de la VFS SQLite.
Branche de travail : `feature/b6-5-cartographie-interactive`.
HEAD vérifié avant arbitrage : `ae53e20dce65f81eac30e76bc218d5cd07eb1c21`.

## Sources vérifiées

Conception technique : `b65-http/SEC01-RD01-CONCEPTION-TECHNIQUE-VFS-20261025.md`. Rapport de faisabilité : `b65-http/SEC01-R1-RD01-FAISABILITE-VFS-RAPPORT-01-20261025.md`. La comparaison `b3770927...ae53e20d` ne comporte qu'un document de conception ajouté. La campagne antérieure GitHub Actions n°90 concerne le banc SIGKILL externe ; elle n'est pas une preuve VFS interne.

## Décision

**GO limité pour la réalisation et la vérification expérimentale d'un prototype VFS isolé de préqualification des portes G01, G02 et G05 exclusivement.**

**G01 — Même moteur :** vérifier la version, l'emplacement, la liaison effective et l'ABI SQLite utilisés par `sqlite3` dans le processus enfant Python. Le banc doit prouver quelle instance du moteur est effectivement instrumentée ; une bibliothèque substituée ne valide pas automatiquement le chemin applicatif.

**G02 — Couverture des deux bases :** observer, sans mutation du code métier existant, les ouvertures et les accès de la base principale, de la base attachée `ATTACH` et des fichiers annexes réellement présents. Inventorier les rôles de fichiers, références de connexions, codes retour et limites. Ne pas présumer un super-journal si son existence n'est pas observée.

**G05 — Conservation :** sur des fichiers purement fictifs, démontrer un inventaire et une copie brute cohérente des deux bases et des journaux associés avant toute réouverture SQLite, ainsi que manifestes SHA-256, copie de travail séparée et absence de secrets. La méthode devra pouvoir être examinée indépendamment.

## Étendue de l'autorisation

Sont autorisés uniquement : ajout de code de banc isolé, éventuel wrapper VFS minimal d'observation, essais de compatibilité et traçabilité sur bases fictives, résultats documentés, contrôles de non-régression adaptés au périmètre si nécessaires. Préserver strictement les fichiers applicatifs existants et la branche autorisée.

**Interdictions :** aucune injection SIGKILL ou autre panne, aucune suspension au sein du COMMIT, aucun mécanisme expérimental d'interruption G03/G04, aucune compilation ou installation globale affectant l'environnement métier, aucune activation de fournisseur réel, aucune publication, aucune fusion vers `main`, aucune modification du site public. Toute dépendance externe nouvelle ou moteur non équivalent doit être signalé et soumis à arbitrage avant introduction.

## Conditions de sortie

Pour chacune des portes G01/G02/G05 : distinguer **démontrée**, **partielle** ou **non démontrée**, avec preuves attachées à un commit exact, scripts et journaux, conditions d'exécution et limites. Relever tout effet observateur et divergence avec SQLite natif ; fournir un dossier pour réception indépendante par le chat 03.

**Ne pas considérer un succès des trois portes comme autorisation automatique d'injection.** Toute étape G03/G04 nécessite décision nouvelle du 00.

## Statuts inchangés

RD01-R01 à RD01-R04 ouvertes ; R1-RD01 ouverte ; R1-C01 partiel ; R1 et P0-01 ouverts ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO. Les 15 essais du banc antérieur restent reçus uniquement pour leurs cinq marqueurs externes.

## Prochaine action unique

Confier au chat 01 le prototype isolé limité aux portes G01, G02 et G05 ; lui demander le dossier de preuves versionné pour réception par le chat 03, sans injection ni modification applicative.
