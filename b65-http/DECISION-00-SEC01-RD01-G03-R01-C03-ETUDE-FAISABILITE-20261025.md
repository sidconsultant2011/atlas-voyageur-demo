# Décision 00 — SEC-01 R1-RD01 — Faisabilité documentaire de l'association causale G03-R01-C03

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `8b21bf7d6fa0409a7872f0abc98372bd40395abd`  
**Priorité unique :** démontrabilité de l'association transaction multi-bases → super-journal → invocation `xDelete`.

## Sources contrôlées

- Contrat 01 : `b65-http/SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md`.
- Réception du contrat par le 00 : `b65-http/DECISION-00-SEC01-RD01-G03-R01-CONTRAT-RECEPTION-20261025.md`.
- Wrapper existant : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`.
- Avis indépendant du chat 02 daté du 25 octobre 2026 : cohérence documentaire de C01–C08, C03 bloquante, **GO documentaire conditionnel**, **NO-GO de réalisation immédiate**.
- Référence expérimentale historique : CI n°135 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980, sur `fc6eded13fa15b8776b12dd0cd494349d0a2e906`. Ses succès ne valident pas le contrat causal.

## Décision du 00

**GO DOCUMENTAIRE STRICTEMENT LIMITÉ À G03-R01-C03.** Le contrat existant est retenu comme base de conception, pas comme preuve d'une instrumentation fonctionnelle.

**NO-GO pour toute modification du wrapper C, du banc, des tests, de l'application ou du workflow ; aucun nouveau test, compilation, CI, callback pré-délégation, barrière, SIGKILL, injection, G04 ou publication n'est autorisé.**

### Livrable demandé au chat 01

Produire une **note de faisabilité documentaire** portant exclusivement sur la capacité de relier de façon vérifiable :
1. la transaction SQLite fictive ayant modifié deux bases attachées et leurs journaux ;
2. l'ouverture avec drapeau `SQLITE_OPEN_MASTER_JOURNAL` et l'identité du super-journal, en distinguant chemin canonique, fichier, handle ouvert et rôle ;
3. la suppression `sqlite3_vfs.xDelete` ciblant exactement ce fichier, malgré l'absence native d'un identifiant de transaction SQL, de connexion et de handle dans cet appel ;
4. une future attestation `BEFORE_DELEGATE`, clairement distincte du succès post-retour, **sans réaliser cette attestation** ;
5. les conditions de non-ambiguïté dans le banc isolé, les cas de collision/concurrence, les indices corroborants et les limites qui empêchent une extrapolation ;
6. les risques d'effet observateur, de réentrance et de modification des garanties de verrouillage et synchronisation ;
7. un protocole futur **non exécuté**, falsifiable, avec les preuves exigées, critères de rejet et une **seule condition bloquante**.

Ne pas inventer un `transaction_id` natif absent de la VFS ni assimiler l'identifiant d'essai à l'identité transactionnelle démontrée. Le rapprochement sur basename seul n'est pas recevable. Privilégier la réutilisation du contrat, des études G03 et du banc N/W existants, sans duplication.

### Critères de décision future

**GO conditionnel à examiner plus tard** seulement si une association transaction/fichiers/super-journal/`xDelete` est démontrable dans le périmètre annoncé, que les ambiguïtés sont falsifiables et que la future observation avant délégation peut être étudiée sans dégrader les acquis N/W.

**NO-GO** si l'identification repose exclusivement sur un nom ressemblant au super-journal, sur un ID d'essai non corroboré, sur une coïncidence temporelle, ou si plusieurs associations compatibles subsistent. Le simple `xDelete` réussi post-délégation ne prouve pas une causalité avant la suppression.

## Statuts inchangés

G03-R01, VFS-R01 et G03-R06 **OUVERTES** ; G03 préparation reçue avec réserves ; G04 **NO-GO** ; G05 global **PARTIEL** ; R1-RD01 et R1 et P0-01 **OUVERTS** ; R1-C01 **PARTIEL** ; B6.5 **EN RECETTE** ; B6.3 **NO-GO** ; production **NO-GO**.

Aucune nouvelle preuve causale, de neutralité VFS ou de durabilité physique n'est déduite de cette décision.

## Prochaine action unique

Transmettre au chat 01 ce mandat d'analyse documentaire G03-R01-C03 et demander un rapport de faisabilité versionné, avant tout nouvel arbitrage du 00.
