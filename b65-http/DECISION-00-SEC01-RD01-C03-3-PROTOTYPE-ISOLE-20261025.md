# Décision 00 — SEC-01 R1-RD01 — Prototype isolé de collecte passive C03-3

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `6255ab4fb97a9a320df26b57a31cd986b976bc2e`  
**Chantier prioritaire unique :** qualification d'un prototype isolé de reconstruction passive S↔A/B pendant COMMIT normal, sans panne.

## Sources et vérifications

- Mandat documentaire : `b65-http/DECISION-00-SEC01-RD01-C03-3-COLLECTE-PASSIVE-20261025.md`.
- Dernier rapport 01, vérifié dans GitHub : `b65-http/SEC01-RD01-C03-3-COLLECTE-PASSIVE-FAISABILITE-20261025.md`.
- Diff GitHub `eb33cd89d8a0593c7041b10a399053ed4803285b..6255ab4fb97a9a320df26b57a31cd986b976bc2e` : **un seul document ajouté** ; aucun code modifié et aucun test nouveau.
- Wrapper de référence : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`, **à préserver inchangé**.
- CI historique n°135 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980, sur `fc6eded13fa15b8776b12dd0cd494349d0a2e906`. Référence de parité N/W, **pas** preuve C03-3.
- Le rapport conclut à la faisabilité documentaire conditionnelle : les références croisées S→A/B et A/B→S sont décrites par SQLite, mais leur reconstruction à travers les buffers, tailles et offsets `xWrite` n'est pas démontrée dans le wrapper courant.

## Arbitrage du 00

**GO TECHNIQUE CONDITIONNEL, STRICTEMENT LIMITÉ À UN PROTOTYPE ISOLÉ C03-3** pour un COMMIT normal sur deux bases SQLite fictives attachées, rollback-DELETE, `synchronous=FULL`, dans le même profil Linux/SQLite que la référence N/W. L'objectif unique est la preuve réciproque et sans ambiguïté des références **S→{A,B}, A→S, B→S** à partir des flux d'écriture VFS validés et du cycle de vie des fichiers.

**Ce GO n'autorise pas** l'instrumentation pré-délégation `BEFORE_DELEGATE` de `xDelete`, une intervention causale dans COMMIT, G04, une injection, un SIGKILL ou une conclusion de durabilité physique. Il n'autorise pas de modification de `atlas_rd01_vfs.c` existant ni du code applicatif.

### Mandat ciblé au chat 01

1. **Préserver le wrapper reçu** : développer une copie expérimentale distincte, explicitement nommée, dans le seul sous-répertoire de banc C03-3. Conserver le moteur SQLite Python du banc et la VFS de référence inchangés. Avant toute édition lire les instructions de dépôt pertinentes.
2. **Limiter la capture aux journaux fictifs** : relever uniquement dans le prototype les buffers `xWrite`, `iAmt`, `iOfst`, code retour, rôle/identité de handle et incarnation du fichier ; tenir compte de `xOpen`, `xTruncate`, `xClose`, `xDelete` dans la reconstitution logique. Ne pas copier les pages applicatives ni publier les octets bruts des journaux ; conserver en sortie uniquement un certificat synthétique avec identités fictives et preuves dérivées non sensibles.
3. **Gérer les cas rejetés** : trous d'écriture, écritures échouées, réécritures, fragmentation, fichier supprimé/recréé, chemins homonymes, super-journal manquant, références discordantes et plusieurs candidats possibles doivent donner un verdict explicite **NON DÉMONTRÉ/REJETÉ**. Ne pas fabriquer d'identifiant transactionnel natif.
4. **Interdire tout accès intrusif** aux fichiers vivants et toute réentrance SQLite depuis les callbacks. Pas de blocage artificiel ni de fsync/attente ajoutés aux callbacks ; contrôle des allocations et de la volumétrie pour que le dispositif reste borné. Si la méthode ne peut pas être réalisée sans modifier invalidement le comportement SQLite, **arrêter le prototype et remonter un NO-GO**.
5. **Comparer au témoin reçu** les caractéristiques nécessaires du scénario : même moteur et PRAGMA, COMMIT normal, deux mutations, résultats SQL, intégrité, journaux résiduels et absence d'erreur supplémentaire. La comparaison historique N/W ne prouve pas la neutralité de ce nouveau prototype.
6. **Tests autorisés uniquement dans ce périmètre** : tests locaux du banc fictif et GitHub Actions non destructifs si utiles. Rapporter distinctement exécutions locales et CI, avec leurs commits précis et traces. Une CI réussie n'équivaut pas à une réception indépendante.
7. **Livrable** : rapport de preuve versionné comprenant les trois références décodées, leurs provenances de buffers/offsets et identités de fichier, la relation au contexte des deux mutations, verdict falsifiable, cas de rejet, effets observateurs observables, limites et soumission au chat 03 pour recette indépendante avant décision du 00.

### Conditions de sécurité permanentes

Aucun fournisseur réel, identité réelle, clé, jeton, secret ni données personnelles dans les sources, traces ou certificats. Pas de modification du site public, aucune fusion `main`, aucun achat ni publication. Aucun essai de panne, aucun SIGKILL, aucune interruption du COMMIT, aucune activation `BEFORE_DELEGATE` sur `xDelete`, aucun G04 ni appel métier `_persistent_journey()`.

## Critère de sortie

**RECEVABLE uniquement si** le certificat démontre S→{A,B}, A→S et B→S avec identités de fichiers et incarnations sans ambiguïté, capture logique des écritures effectivement acceptées, et invariants SQL/SQLite préservés dans l'environnement ciblé.

**NO-GO motivé** si la reconstitution nécessite une lecture invasive, une réentrance SQLite, une altération des garanties nécessaires au COMMIT normal, ou si un lien demeure non observé ou équivoque. Une sortie partielle doit être **NON DÉMONTRÉ**, jamais convertie en succès par analogie documentaire.

Cette preuve, même reçue, **ne prouverait pas** `BEFORE_DELEGATE`, l'identité événementielle de la VFS native, une récupération post-panne, la durabilité physique ou la conformité métier.

## Statuts inchangés

**C03-3, G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 OUVERTS ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

## Prochaine action unique

Transmettre au chat 01 le mandat d'un prototype **distinct et isolé** de collecte passive C03-3 pour COMMIT normal fictif ; remettre preuves et code versionné à une recette indépendante du chat 03 avant tout nouvel arbitrage.
