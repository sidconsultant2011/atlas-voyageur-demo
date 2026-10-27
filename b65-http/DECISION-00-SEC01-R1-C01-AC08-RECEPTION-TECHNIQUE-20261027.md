# 00 — SEC-01 R1-C01 — AC-08 — Réception technique pour recette indépendante

**Date :** 27 octobre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `612cc4b2422371b945f593ade84bc9a19eeccdbc`

## Références contrôlées directement

- GO technique antérieur : `b65-http/DECISION-00-SEC01-R1-C01-AC08-GO-IMPLEMENTATION-20261027.md`.
- Rapport de réalisation : `b65-http/SEC01-R1-C01-AC08-CORRECTIF-PREUVES-20261027.md`, présent sur la branche au HEAD indiqué.
- Commit technique testé : `eb97c24eb969b2a28f4276b1c489d7eb46a6c6a4`.
- CI n°238 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587946581 ; état **completed**, conclusion **success**, head SHA identique au commit technique testé.
- Journaux de l'unique job `test` lus directement par le 00 : **116/116 JavaScript**, **11/11 SQLite**, **161/161 HTTP/identité/sécurité** dont **8/8 tests ciblés AC-08** tous `ok` ; total de **288 exécutions réussies**, pas nécessairement 288 scénarios distincts.
- CI n°236 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587789860, échec antérieur documenté pour recréation implicite de `identities.sqlite` absente au moment de l'`ATTACH`. Le test `test_missing_fixture_after_creation_never_recreated` réussit dans la CI n°238 après correction.
- Comparaison GitHub du HEAD initial de mandat `029793f7101e5fd3b9c458050d25e4a7d9ef1d4d` au HEAD documentaire `612cc4b2422371b945f593ade84bc9a19eeccdbc` : six fichiers changés — `sqlite_ac08.py` (ajout), `persistent_sessions.py`, `fictional_identities.py`, `local_identity_bridge.py`, `test_sec01_ac08.py` (ajout), et rapport (ajout).
- Les modules métier, la façade `local_http_facade.py`, les wrappers C, le workflow GitHub Actions, C03 et VFS ne font pas partie du diff indiqué. Les tests locaux du dépôt complet **n'ont pas été exécutés** au commit testé ; ne pas les annoncer comme réussis.

## Résultat technique borné

Le code AC-08 livré vise la préparation et la vérification de `journal_mode=DELETE` et `synchronous=FULL` sur les connexions SQLite des sessions et identités fictives, avec contrôle des deux bases attachées **avant `BEGIN IMMEDIATE`**, conservation des paramètres existants `busy_timeout` et `foreign_keys`.

Les tests rapportés et leur présence dans les journaux CI confirment sur des fixtures fictives locales : création conforme, réouverture compatible, refus de WAL préexistant sans conversion automatique, refus des chemins `:memory:` / URI non admissibles, contrôle des deux bases à `ATTACH`, et absence de recréation du fichier d'identités supprimé après initialisation.

## Décision 00

**GO — RÉCEPTION TECHNIQUE CIBLÉE AC-08 POUR RECETTE INDÉPENDANTE 03.**

Cette décision constate la livraison et ses preuves de CI. Elle **n'est pas** une réception indépendante, une clôture d'AC-08, une levée de R1-C01, ni une autorisation de production.

### Mandat à 03 — Recette indépendante sans campagne automatique

Le chat 03 est chargé de :
1. Vérifier branche/HEAD et rattachement de la CI n°238 au commit exact `eb97c24e`.
2. Examiner le diff AC-08 et vérifier que les six fichiers correspondent au mandat ; code métier/HTTP/C03/workflow inchangés.
3. Examiner le comportement de l'utilitaire SQLite : distinction base neuve/existante, absence de conversion silencieuse WAL, contrôle `DELETE/FULL` sur chaque connexion, conservation `foreign_keys`/`busy_timeout`, erreurs et absence de mutation sur configuration refusée.
4. Vérifier particulièrement le correctif de la recréation implicite à `ATTACH` qui avait provoqué l'échec de la CI n°236, puis le scénario réussi en CI n°238.
5. Contrôler les 8 assertions/tests AC-08 et les non-régressions existantes 116/11/161 sur les journaux ; distinguer les tests locaux non exécutés.
6. Émettre un PV indépendant, verdict favorable, favorable avec réserves ou défavorable, en bornant précisément ses preuves et limites. **Ne pas lancer de nouvelle CI ou campagne locale par défaut**, sauf anomalie concrète nécessitant nouvel arbitrage.

### Réserves maintenues

AC-13, gestion HTTP des exceptions SQLite/COMMIT : non traitée. La configuration `DELETE/FULL` n'établit pas une garantie de durabilité physique, récupération de panne interne du COMMIT, coupure OS/matérielle ni sécurité multi-hôtes. Les vérifications basées sur chemins/`st_dev` ne prouvent pas les propriétés matérielles du support.

**R1-C01 demeure PARTIEL ; R1-RD01, R1, P0-01 restent OUVERTS. B6.5 demeure EN RECETTE ; B6.3, G04 et production restent NO-GO.** Aucun GO de fusion main, site public, déploiement, fournisseur réel ou injection de panne n'est donné.

## Prochaine action unique

Transmettre au chat 03 les preuves AC-08 et le présent mandat pour obtenir le PV indépendant, sans relancer automatiquement les tests.
