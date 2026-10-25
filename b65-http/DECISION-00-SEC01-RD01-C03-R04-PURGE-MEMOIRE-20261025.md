# Décision 00 — SEC-01 R1-RD01 — Mandat expérimental C03-R04 : buffers C

**Date :** 25 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `f5ae1aeeb51faef264673de6f63fe80a0c2c6c46`  
**Priorité technique unique :** C03-R04 — cycle de vie, purge et libération des copies brutes observées dans la VFS expérimentale C03-3.

## Sources et anomalie attestée

- Avis indépendant du chat 02 transmis le 25 octobre 2026 : priorité C03-R04 sur C03-R06, GO conditionnel pour un correctif borné.
- Code vérifié : `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` : `MAX_FILES=16`, `MAX_BYTES=1024*1024`; `record_open()` alloue `data` et `present` par `calloc`; `wr()` copie les buffers de `xWrite`; `c03_test_reset()` libère les deux zones par `free()` sans effacement explicite préalable. `record_open()` marque une défaillance d'allocation mais ne nettoie pas immédiatement sa paire partiellement allouée.
- Les données du prototype et tests actuels sont fictives. Aucune fuite de mémoire, lecture adversaire ou présence de données personnelles réelles n'est démontrée ; **l'absence d'une garantie de purge est le constat**.
- Clôtures ciblées antérieures de C03-R01 (incarnations), C03-R02 (suppressions), C03-R03 (`xClose`) : toutes limitées au registre expérimental.
- C03-R05 est **ouverte avec mesures quantitatives suspendues** conformément à `b65-http/DECISION-00-SEC01-RD01-C03-R05-P1-BUDGET-NON-JUSTIFIABLE-20261025.md`.

## Décision 00

**GO TECHNIQUE CONDITIONNEL — CORRECTION STRICTEMENT EXPÉRIMENTALE C03-R04.**

### Mandat unique au chat 01

1. Vérifier HEAD, instructions du dépôt, code C03 et chemin Python actuel de certification avant toute modification. Ne pas refaire un mécanisme déjà qualifié.
2. Inventorier précisément les chemins d'allocation des buffers de `Record`, les allocations partielles, leur durée de conservation nécessaire à `reciprocal_certificate()`, les branches de sortie normale et de rejet, ainsi que le mécanisme actuel de reset. Identifier les propriétés effectivement testables en mémoire avant et après purge.
3. Modifier **uniquement le prototype C03-3**, ses interfaces de nettoyage/lecture Python strictement nécessaires, des tests ciblés et un rapport de preuve. Ne pas modifier `atlas_rd01_vfs.c`, le moteur SQLite, le workflow ni l'application.
4. Définir un **effacement explicite non optimisable** pour le contexte du runner et du prototype, utilisé avant chaque libération des buffers `data` et `present`. Ne pas présenter un simple `memset` optimisable comme preuve suffisante. Documenter portabilité, optimisations et limites du mécanisme retenu.
5. Garantir un nettoyage idempotent avec gestion des allocations partiellement réussies, des erreurs d'observation, des échecs de certificat et du reset, sans `double free`, accès après libération ou preuve faussement positive. Le nettoyage doit intervenir **après la dernière utilisation légitime** du contenu permettant d'identifier S, A et B ; une purge au callback `xClose` sans validation de la durée de vie serait prématurée.
6. En fin du chemin normal fictif, déclencher ou exiger explicitement la destruction des buffers avant sortie du processus en tenant compte de l'accès Python aux octets et au registre. Vérifier la même obligation sur chemin d'erreur. Ne pas assimiler destruction d'un registre C à effacement universel des copies Python/SQLite ou du swap.
7. Définir des tests synthétiques bloquants couvrant au moins : allocation complète, allocation partielle simulée, reset, certification normale puis destruction, certification rejetée puis destruction, tentative répétée de nettoyage, et impossibilité d'exploiter des buffers nettoyés. Vérifier les invariants C03-R01/R02/R03, les six suppressions correctement attribuées, intégrité `ok/ok`, S↔A/B et DELETE/FULL. Ne pas provoquer de panne OS ni utiliser de données réelles.
8. Rapporter les contrôles locaux effectivement exécutés, les CI sur commits exacts, les incidents intermédiaires, la portée de la vérification d'effacement, les éventuelles limitations du compilateur, la liste des fichiers modifiés et la non-régression. Si un nettoyage fiable exige une modification de périmètre interdite ou casse le certificat, **NO-GO motivé** et retour au 00 sans contournement.
9. Préparer la livraison pour **recette indépendante du chat 03**. La correction et la réussite CI n'entraînent aucune clôture automatique de C03-R04.

### Limitations et exclusions

Le correctif ne démontrera pas l'effacement des copies dans SQLite, Python, caches, dumps ou swap, ni la sûreté générale face à un attaquant pouvant lire la mémoire. La mémoire du processus demeure fictive/isolée ; aucune qualification de données réelles ou production.

**Interdits :** nouveau chantier C03-R06 ; nouvelle campagne ou budget C03-R05 ; `BEFORE_DELEGATE` ; SIGKILL ; injection de panne ; G04 ; modification des wrappers de référence ; fournisseur réel ; fusion vers main ; site public ; déploiement.

## Statuts après décision

- **C03-R04 : OUVERTE — traitement expérimental autorisé.**
- **C03-R05 : OUVERTE — qualification temporelle suspendue ; acquis fonctionnels précédents conservés.**
- **C03-R06 : OUVERTE.**
- **C03-R01, R02 et R03 : clôturées strictement dans leurs périmètres fictifs bornés.**
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 : OUVERTS.**
- **B6.5 : EN RECETTE ; G04, B6.3 et production : NO-GO.**

## Prochaine action unique

Transmettre ce mandat au chat 01 pour corriger exclusivement la purge et le cycle de vie des buffers C03, puis préparer les preuves pour réception indépendante par le chat 03.
