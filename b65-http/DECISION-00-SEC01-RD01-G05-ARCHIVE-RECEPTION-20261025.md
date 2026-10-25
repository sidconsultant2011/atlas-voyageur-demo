# Décision 00 — SEC-01 R1-RD01 — Complément archivage G05

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Chantier prioritaire unique :** réception indépendante du complément de conservation G05.  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant cette décision :** `6a9db1fd2563e7f356548bd3cbb100354b249f6b`.

## Sources et preuves vérifiées

- Rapport du chat 01 : `b65-http/SEC01-RD01-VFS-G05-PREUVES-ARCHIVE-20261025.md`.
- CI n°108 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40205084577.
- Commit testé : `1071fbe3ce35ba5556e53c437acf928c730d9e0b`.
- CI `completed / success` : 116 exécutions JS, 11 SQLite, 96 HTTP/identité, soit **223 exécutions réussies** (pas 223 scénarios nécessairement distincts).
- La CI précédente n°107 avait échoué sur une erreur de syntaxe du banc, corrigée pour la CI n°108.
- Artefact visible sur GitHub : `atlas-rd01-g05-40205084577`, ID `12602679040`, 6 610 octets, non expiré au moment de la vérification ; date d'expiration indiquée **8 novembre 2026**.
- Journaux du job : étape `Publier preuves G05 fictives` réussie et SHA-256 du ZIP publié `08e4847a3963e25e3533d306188f87bfc5649994e19823e743c5b1e46f02b5f5`.
- Trace de test `RD01 VFS STEP1 PROOF` : `persisted_files_verified=6`, `recovery_after_crash=NON_TESTEE`.
- Comparaison depuis `120245f7f93889e76ac02a5b7b1b2ac8310a461d` : trois fichiers changés, dont workflow et banc, **aucun module applicatif existant modifié**.

Le chat 01 rapporte avoir téléchargé le ZIP et vérifié huit fichiers, six empreintes et son CRC. Ces contrôles hors runner sont **une déclaration appuyée par le rapport du 01** et doivent être corroborés indépendamment par le chat 03. Le 00 a directement confirmé l'existence de l'artefact, sa métadonnée et les journaux de publication, mais n'a pas lui-même contre-expertisé les octets de l'archive.

## Décision

**Accepter la livraison technique du complément G05 pour passage au chat 03 — Recette indépendante**, sans modifier la qualification globale.

Le chat 03 doit vérifier l'archive réellement téléchargée (inventaire, tailles, CRC, SHA-256 du ZIP et de chaque fichier prévu au manifeste), la provenance du commit/CI, les versions et PRAGMA, les limitations d'accès et de rétention, l'absence de données réelles ou de secrets, et la distinction fondamentale entre archives de fichiers propres et archives de journaux chauds après crash.

**Portée acquise sous réserve de réception 03 :** publication et copie hors runner de bases fictives propres, traces, manifeste et rapport. **G05 global reste PARTIEL :** pas de journal chaud, pas de récupération post-panne, pas d'interruption interne du COMMIT.

**Aucune autorisation G03/G04**, aucune nouvelle injection ou SIGKILL, aucun changement de code applicatif, aucune nouvelle dépendance, aucune fusion vers main, fournisseur réel, achat, publication ni modification du site public.

## Statuts

**G01 RECEVABLE sur le runtime CI ; G02 RECEVABLE sur banc fictif ; G05 PARTIEL ; VFS-R01 à R05 OUVERTES ; RD01-R01 à R04 OUVERTES ; R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

La rétention GitHub étant limitée à 14 jours, le chat 03 doit signaler la date d'expiration et recommander au 00 une stratégie documentaire si les octets doivent être conservés au-delà de la fenêtre prévue.

## Prochaine action unique

Transmettre au chat 03 le rapport du commit documentaire `6a9db1fd`, les journaux CI n°108 et l'artefact `12602679040` pour contre-expertise indépendante G05 sans essai de panne.
