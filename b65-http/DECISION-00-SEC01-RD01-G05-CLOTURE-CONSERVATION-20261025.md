# Décision 00 — SEC-01 R1-RD01 — Clôture du seul chantier documentaire de conservation G05

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD GitHub vérifié avant décision :** `f2077c8695cc39e8c88e2065e12240ce015eec0b`.

## Sources de décision

- PV 03 et arbitrage précédent : `b65-http/PV-03-SEC01-RD01-G05-ARCHIVE-20261025.md`.
- GitHub Actions n°108 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40205084577
- Commit testé : `1071fbe3ce35ba5556e53c437acf928c730d9e0b`.
- Artefact source : `atlas-rd01-g05-40205084577`, ID `12602679040`.
- Expiration indiquée de l'artefact GitHub : **2026-11-08T15:03:22Z**.
- Empreinte SHA-256 publiée dans les journaux CI : `08e4847a3963e25e3533d306188f87bfc5649994e19823e743c5b1e46f02b5f5`.

## Copie documentaire indépendante — Google Drive

**Archive ZIP :**
- Nom : `ATLAS-VOYAGEUR-G05-PREUVES-CI108-20261025.zip`
- ID : `1Fo7mrKPJtBMzVDXCBg3wmRuBnIhbt3s6`
- URL : https://drive.google.com/file/d/1Fo7mrKPJtBMzVDXCBg3wmRuBnIhbt3s6/view
- Taille relue dans les métadonnées Drive : **6610 octets**.
- Accès : fichier non partagé selon métadonnées consultées le 25 octobre 2026.

**Fiche de conservation :**
- Nom : `ATLAS-VOYAGEUR-G05-FICHE-CONSERVATION-20261025.md`
- ID : `19Y6CykkO5-xMHw5x2rJvXFJa_0FdUwvF`
- URL : https://drive.google.com/file/d/19Y6CykkO5-xMHw5x2rJvXFJa_0FdUwvF/view
- Taille relue : **2456 octets**.
- Accès : fichier non partagé selon métadonnées consultées.

Le chat 04 rapporte avoir téléchargé le ZIP d'origine depuis GitHub, vérifié le SHA-256, copié le ZIP dans Google Drive, retéléchargé la copie et obtenu une **comparaison binaire identique (cmp, code 0)**. La fiche de conservation décrit ce contrôle et les références exactes. Le 00 a **vérifié directement l'existence, la taille et les permissions rapportées par Drive, ainsi que le contenu textuel de la fiche** ; il n'a pas, dans ce contrôle, recalculé lui-même l'empreinte SHA-256 de la copie binaire Drive.

## Décision du 00

**MISSION 04 — CONSERVATION DOCUMENTAIRE DES PREUVES G05 : CLÔTURÉE**, sous réserve des règles de disponibilité et de rétention du compte Google Drive. La copie indépendante existe et sa traçabilité est documentée. Cela ne garantit pas une conservation éternelle ni une sauvegarde redondante.

**Périmètre de réception :** fichiers SQLite fictifs fermés normalement ; archive ZIP, manifestes, traces et intégrité contrôlés précédemment par 03. Aucune nouvelle preuve de récupération après panne produite par cette conservation.

**G05 GLOBAL : PARTIEL.** Le sous-périmètre archivage de fichiers propres est reçu. Les journaux chauds après panne, la récupération post-crash et l'interruption interne au COMMIT ne sont pas démontrés.

**G03/G04 NON AUTORISÉES.** Réserves VFS-R01 à R05 et RD01-R01 à R04 ouvertes. **R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

Aucune fusion vers main, activation de fournisseur réel, publication ou modification du site public, aucun achat. Aucune modification applicative ou nouvelle campagne de tests lors de cette décision.

## Suite soumise au pilotage

La clôture documentaire permet de revenir au chantier prioritaire SEC-01 sans perdre les preuves. Avant tout essai G03/G04, le 00 devra arbitrer séparément les réserves techniques (équivalence du wrapper VFS, chemin métier, preuve causale et récupération de journaux chauds) et le niveau de preuve réellement recherché. Aucun GO expérimental n'est déduit de ce document.

## Prochaine action unique

Confier au chat 02 — Sécurité P0 une **proposition de décision GO/NO-GO pour une éventuelle étape technique G03/G04**, fondée sur les réserves restantes et les preuves archivées, sans développement ni essai supplémentaire.
