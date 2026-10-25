# Décision 00 — SEC-01 R1-RD01 — Clôture ciblée C03-R03

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `a53f15ef47761f8ee72189dc0a232e3940991542`  
**Autorité :** 00 — Pilotage et gouvernance.

## Sources et preuves

- Décision de transmission à la recette : `b65-http/DECISION-00-SEC01-RD01-C03-R03-RECEPTION-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-C03-R03-XCLOSE-CORRECTIF-PREUVES-20261025.md`.
- Procès-verbal indépendant du chat 03 **`PV-03-SEC01-RD01-C03-R03-20261025`**, remis au 00 en texte le 25 octobre 2026 : verdict **réception favorable avec réserves**, recommandation de clôture ciblée. La présence de ce PV comme fichier autonome GitHub n'est pas attestée.
- Code examiné au commit testé `63664ba669964c1427d5032cbf274d34b1b7a3dc` : `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` appelle `parent xClose`, enregistre son retour via `record_close_result()`, puis retourne le code natif sans transformation. `closed=1` si, et seulement si, le code connu vaut `SQLITE_OK`; erreur ou résultat inconnu ne donnent aucune fermeture positivement attestée.
- `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` collecte les informations `c03_close_info()` dans le chemin réel du banc et appelle `validate_close_evidence()` avant certificat. Les anciennes fixtures synthétiques dépourvues des nouveaux champs utilisent un contrôle de compatibilité `closed/error` ; cela ne prétend pas attester un retour natif pour ces anciennes fixtures.
- CI n°178 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232772919 : `completed / success` sur `63664ba669964c1427d5032cbf274d34b1b7a3dc` ; **116/116 JavaScript, 11/11 SQLite, 125/125 HTTP/identité/banc**, soit **252 exécutions réussies**, qui ne sont pas nécessairement 252 scénarios distincts.
- Cinq tests ciblés : `SQLITE_OK`, erreur native `SQLITE_IOERR` fournie au helper, retour indéterminé, fermeture non invoquée et échec A/B/S dans trois sous-cas. Tous réussis dans la CI n°178. Les erreurs sont **synthétiques**, pas des fautes OS provoquées.
- Non-régression : `RECONSTRUIT_BANC_FICTIF`, S→A/B, A/B→S, six suppressions attribuées sur six, anomalies d'attribution nulles, intégrité SQLite `ok/ok`, DELETE/DELETE, FULL/FULL, SQLite CI 3.45.1. Les tests C03-R01 et C03-R02 restent inclus.
- CI n°177 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232703728 : `completed / failure` au commit `cd2a8ddc874f95c931d683cd6b1afd79530f10ad`. Le PV attribue l'échec à la lecture de `deleted` (index 3) à la place de `closed` (index 2) dans le test. Corrigé au commit testé n°178. **Cet échec historique reste conservé.**
- Aucun nouveau test local ou CI lancé par les chats 03 et 00 ; aucun test local sur le commit exact revendiqué par le chat 01.

## Décision explicite du 00

**GO — CLÔTURE CIBLÉE DE C03-R03**, limitée à la preuve logicielle du succès du callback `xClose` dans le registre expérimental fictif et les scénarios reçus.

Le défaut initial consistant à marquer `closed=1` indépendamment du résultat natif est corrigé. Dans ce périmètre, le certificat positif exige des fermetures connues et réussies ; le code retour SQLite n'est pas modifié par l'observateur.

**Cette clôture ne constitue pas une qualification de l'identité physique des fichiers, de la concurrence multi-transaction, de la neutralité temporelle, de la sécurité des buffers mémoire, de la durabilité physique ni de la récupération après panne.** Les retours négatifs des tests ont été simulés.

## Statuts préservés

- **C03-R01, C03-R02, C03-R03 : CLÔTURÉES exclusivement dans leurs périmètres expérimentaux bornés.**
- **C03-R04, C03-R05 et C03-R06 : OUVERTES.**
- **C03-3 global : OUVERT**, prototype reçu avec réserves.
- **G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 : OUVERTS** ; G03 préparatoire avec réserves.
- **G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE.**
- **G04, B6.3 et production : NO-GO.**

Aucun code, moteur SQLite, workflow, wrapper principal ou site public modifié au titre de cette décision. Aucun nouveau chantier technique, G04, `BEFORE_DELEGATE`, SIGKILL, injection de panne, fusion vers main, fournisseur réel ni déploiement autorisé.

## Prochaine action unique

Demander au chat 02 un avis documentaire sur la **prochaine et unique priorité parmi C03-R04, R05 et R06**, puis revenir au 00 pour arbitrage avant tout développement.
