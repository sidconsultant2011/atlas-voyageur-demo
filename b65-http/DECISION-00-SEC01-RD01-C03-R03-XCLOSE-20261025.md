# Décision 00 — SEC-01 R1-RD01 — Qualification expérimentale xClose C03-R03

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `a5296f8dc9ced3248a4274a1263ee7806472ff6b`  
**Chantier prioritaire unique :** C03-R03 — distinguer l'invocation de `xClose` et sa réussite native sur le prototype fictif C03-3.

## Sources vérifiées

- Clôture ciblée C03-R01 : `b65-http/DECISION-00-SEC01-RD01-C03-R01-CLOTURE-CIBLEE-20261025.md`.
- Code expérimental `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` : actuellement, `cl()` appelle `xClose` parent, puis positionne `rec[w->slot].closed=1` **sans condition sur le code retour**, avant de retourner `r`. Le résultat natif est conservé mais la preuve de cycle de vie peut être inexacte.
- Décodeur `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : `reciprocal_certificate()` exige `closed` pour les participants et vérifie les erreurs, mais le flag actuel ne prouve pas le succès de `xClose`.
- CI n°170 antérieure : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231306358 ; `completed/success` sur `5bd4a0aec3c24a4ed2690d22af8885a63d72762d`, 247 exécutions. **Cette CI n'est pas une preuve de C03-R03.**
- Avis documentaire du chat 02 transmis le 25 octobre 2026 : priorité unique **C03-R03**, avec recommandation de GO conditionnel et critères falsifiables.

## Décision du 00

**GO TECHNIQUE CONDITIONNEL — CORRECTIF EXPÉRIMENTAL LIMITÉ À C03-R03.**

Objectif : empêcher qu'une fermeture native échouée, absente ou non qualifiable contribue à un certificat positif de cycle de vie. Ne modifier ni le résultat natif ni le fonctionnement de SQLite pour produire une preuve favorable.

### Mandat unique au chat 01

1. Avant modification, contrôler HEAD, instructions applicables du dépôt et code existant, sans refaire les acquis.
2. Limiter le code à la **copie expérimentale** `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c`, aux éventuelles vérifications strictement nécessaires dans `c03_run.py` et aux tests ciblés. Ne pas modifier le wrapper de référence.
3. Distinguer dans le canal probatoire une invocation `xClose` d'une fermeture réussie, et conserver la valeur exacte du retour natif. `closed=1` ne doit signifier succès que si `r==SQLITE_OK`. Sur retour en erreur, conserver un indicateur fiable d'échec ou d'état non démontré **avant libération du handle**, sans faire dépendre la preuve d'une lecture ultérieure du handle libéré.
4. Faire **échouer bloquamment** la certification positive lorsqu'une fermeture échouée ou indéterminée porte sur un journal participant A/B ou le super-journal S, ainsi que sur toute entrée observée dont l'état erroné aurait été faussement accepté par la preuve. Ne jamais interpréter l'absence de flag de succès comme une réussite.
5. Couvrir par des **tests synthétiques de la logique réellement appelée** : succès `SQLITE_OK`, erreur native préservée, retour non qualifiable, échec de A, de B et de S. Vérifier qu'un test échoue si l'observateur marque une fermeture échouée comme réussie. Distinguer explicitement code retour simulé dans un seam et erreur OS réelle ; aucune injection de panne système.
6. Préserver le COMMIT normal fictif et ses relations S↔A/B, les contrôles DELETE/FULL, `integrity_check=ok/ok`, les rejets C03-R01, et tous les acquis C03-R02, y compris `no_match>0` et les retours `xDelete`. Aucun nouveau comportement de verrouillage, attente, `fsync` ou lecture intrusive de journal actif.
7. Exécuter les tests locaux adaptés si réalisables, reporter séparément les résultats GitHub Actions sur le commit exact, les erreurs rencontrées, la version SQLite, les preuves de non-régression, le diff et les limites. Si la preuve ne peut pas être obtenue dans ce périmètre sans instrumentation additionnelle, **arrêter et rendre NO-GO motivé**, sans contourner les exigences.
8. Remettre un rapport de preuves versionné puis solliciter la **recette indépendante du chat 03** avant tout arbitrage de clôture C03-R03 par le 00.

### Restrictions et risques résiduels

- Aucun changement au wrapper de référence `atlas_rd01_vfs.c`, au code métier, à `_persistent_journey()`, au moteur SQLite, au workflow, à la configuration ou aux fournisseurs.
- Aucun `BEFORE_DELEGATE`, G04, SIGKILL, injection de panne, test de récupération post-panne, changement du site, fusion main ou déploiement.
- Les tests synthétiques n'établissent pas un échec réel `xClose` du système de fichiers ; `SQLITE_OK` n'établit pas l'identité inode ni une garantie de durabilité.
- **C03-R04, R05 et R06 demeurent ouvertes** : mémoire C, neutralité temporelle, couverture négative.
- **C03-R01 et C03-R02 demeurent clôturées dans leur périmètre expérimental** sans extension implicite.
- **C03-R03 OUVERTE — réalisation seulement autorisée** ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS ; G04 et production NO-GO ; B6.5 EN RECETTE ; B6.3 NO-GO.

## Prochaine action unique

Transmettre ce mandat au chat 01 pour traiter exclusivement C03-R03, avec vérification du retour de `xClose` et tests ciblés, avant recette indépendante 03.
