# Décision 00 — SEC-01 R1-RD01 — Qualification comparative VFS native / wrapper existant

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `1dce0004b4541506b6bedb5751cc28542c9baf51`  
**Chantier prioritaire unique :** comparaison expérimentale non destructive du banc fictif sous VFS native et sous wrapper VFS existant.

## Sources vérifiées

- Décision documentaire : `b65-http/DECISION-00-SEC01-RD01-VFS-R01-ETUDE-20261025.md`.
- Rapport 01 : `b65-http/SEC01-RD01-VFS-R01-ETUDE-COMPATIBILITE-NEUTRALITE-20261025.md`.
- Wrapper : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`.
- Banc : `b65-http/rd01-vfs-step1/rd01_vfs_step1.py`.
- Rapport G03 : `b65-http/SEC01-RD01-G03-PREPARATION-PREUVES-20261025.md`.
- CI historique n°120 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40208301806, sur `03986691d23f0044c5fcbe9c1ac2a169f0c938c6`, 223 exécutions réussies. **Ce n'est pas une preuve de comparaison native/wrapper.**
- Comparaison depuis `779650a0b638a5631d06b750f434e7773d5521ea` jusqu'au HEAD documentaire : **un seul fichier ajouté** ; aucun module applicatif ni wrapper modifié.

## Décision du 00

**GO CONDITIONNEL POUR LA COMPARAISON EXPÉRIMENTALE NON DESTRUCTIVE sur le banc fictif, avec deux exécutions témoins N (native) et W (wrapper existant).** L'objectif strict est d'objectiver VFS-R01 / G03-R06 sur le scénario SQLite rollback-DELETE, ATTACH de deux bases, BEGIN IMMEDIATE et synchronous=FULL, sans panne.

**Le présent GO n'autorise PAS un correctif du wrapper C, l'ajout des méthodes V2/V3, la qualification de l'atomicité pendant une panne ou G04.** Toute suite sera arbitré après les preuves et l'avis indépendant du chat 03.

### Périmètre autorisé au chat 01

1. Examiner l'environnement exact et vérifier sur chaque témoin la version et l'identité du moteur SQLite. Utiliser le même runtime Python, même système, même support de fichiers, fixtures fictives et SQL, sans changer les paramètres transactionnels pour améliorer artificiellement un résultat.
2. Exécuter indépendamment le **témoin N** sur VFS native et le **témoin W** sur le wrapper inchangé. Éviter les collisions entre les fichiers des deux témoins et conserver le nom et la provenance de chaque jeu.
3. Vérifier et consigner : `PRAGMA journal_mode` par base, `synchronous` par base, attachement effectif des deux bases, étapes de transaction normales, codes d'erreur et résultats SQL, invariants, `integrity_check`, présence/absence des journaux à la fermeture et conservation des preuves. Distinguer les valeurs observées des hypothèses de neutralité.
4. Qualifier ce que l'on peut réellement comparer sur les verrouillages, synchronisations et I/O sans trace invasive sur le témoin N. Ne **pas** inventer une parité événement par événement si les outils d'observation diffèrent ; classifier « même résultat », « différence observée », ou « non mesuré ».
5. Définir à l'avance les différences invalidantes : moteur SQLite distinct ou ABI incertaine ; modes de journalisation/synchronisation modifiés ; divergences SQL/invariants ; erreurs ou verrouillages incohérents ; absence inexpliquée d'une propriété requise au COMMIT normal. Ne pas attribuer automatiquement toute variation de durée, compteurs ou noms de fichiers à une anomalie.
6. Autoriser uniquement les changements **minimaux du banc fictif, de ses tests et de la documentation de preuves**, nécessaires à ces deux témoins. Aucune nouvelle dépendance externe sans arbitrage ; pas de compilation globale ni substitution de moteur. Des essais locaux/CI **non destructifs** de COMMIT normal sont autorisés si nécessaires et doivent être consignés par commit exact, séparément.
7. Préparer un rapport de comparaison versionné : paramètres complets N/W, matrice par critère, observations, différences, non-mesurés, limites de l'effet observateur, verdict de faisabilité pour le scénario testé et proposition motivée de GO/NO-GO pour une étape ultérieure. Soumettre ensuite au **chat 03 pour recette indépendante** avant arbitrage du 00.

### Interdictions

- **Ne pas modifier `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`** dans cette étape.
- Aucune instrumentation avant délégation, ni nouvelle barrière dans les callbacks, aucun SIGKILL, crash, arrêt de processus ciblé, simulation de panne ou G04.
- Ne pas modifier ni exécuter `LocalIdentityBridge._persistent_journey()` dans cette étape ; aucune mutation du code applicatif.
- Aucun fournisseur réel, donnée personnelle réelle, secret, achat, fusion vers `main`, publication ou modification du site public.
- Aucune conclusion de neutralité générale VFS ou de durabilité physique à partir de COMMIT normaux.

## Critère de sortie et statuts

**Livrable attendu :** preuve comparable, falsifiable et versionnée du scénario N/W ; classification explicite de chaque critère (recevable pour cette portée / divergence / non démontré), accompagnée des limites. Sans résultat observable, déclarer **NON DÉMONTRÉ**, pas « conforme ».

VFS-R01 et G03-R06 **OUVERTES** jusqu'à examen indépendant ; G03 préparation reçue avec réserves ; G04 **NO-GO** ; G05 global **PARTIEL**. Réserves VFS-R02 à R05, G03-R01 à R07, RD01-R01 à R04 inchangées ; R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.

## Prochaine action unique

Transmettre au chat 01 le mandat de comparer sur banc fictif la VFS native et le wrapper **inchangé**, avec COMMIT normal uniquement, puis présenter les preuves au chat 03 sans lancer G04.
