# Décision 00 — SEC-01 R1-RD01 — Réception indépendante de la comparaison VFS native / wrapper

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `0e1331a794fa51e6200c1803bd968bb0c5ed0439`  
**Chantier prioritaire unique :** réception indépendante 03 de la comparaison VFS native N / wrapper W en COMMIT normal.

## Sources et contrôles directement vérifiés par le 00

- Mandat : `b65-http/DECISION-00-SEC01-RD01-VFS-R01-COMPARAISON-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-VFS-R01-COMPARAISON-NATIVE-WRAPPER-PREUVES-20261025.md`.
- GitHub Actions n°129 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40210414951 — `completed / success`, commit testé `88de630acae24f8d960c6d4089dd8f21d7d3a630`.
- Tests CI : **116/116 JavaScript, 11/11 SQLite, 97/97 HTTP/identité et banc**, total **224 exécutions réussies** (pas nécessairement 224 scénarios différents). Le chat 01 ne rapporte aucun test local du commit final.
- Diff GitHub depuis `a2e451751179e74f6f59e3a1c9357f63fd6cd948` jusqu'au HEAD : trois fichiers **ajoutés** : `b65-http/rd01-vfs-step1/vfs_r01_compare.py`, `b65-http/test_vfs_r01_compare.py`, rapport de preuves. **Aucun wrapper C ni module applicatif modifié.**
- La trace de CI `RD01 VFS R01 NATIVE WRAPPER COMPARISON` présente deux jeux N/W : version SQLite 3.45.1, mêmes symboles de bibliothèque attestés dans le runtime, `database_list` sur deux bases, `journal_mode=delete/delete`, `synchronous=2/2`, `BEGIN IMMEDIATE` puis `COMMIT`, état final identique (session `fixture-session` révoquée, parcours `fixture-journey` libellé `fake`), `integrity_check=ok/ok`, et aucun journal résiduel après fermeture normale. `differences=[]` pour les critères testés.
- La trace du seul témoin W montre `xSync=16`, `xWrite=60`, `xDelete=6`, `xOpen=8`, `xFileControl=34` ; le témoin N n'a pas de trace d'I/O native comparable.

## Décision du 00

**LIVRAISON TECHNIQUE DE LA COMPARAISON N/W ACCEPTÉE POUR RECETTE INDÉPENDANTE PAR LE CHAT 03.**

La comparaison constitue un témoin expérimental **fonctionnel** encourageant, **strictement limité au scénario fictif rollback-DELETE avec deux bases et COMMIT normal sur le runner ciblé**.

**Aucune preuve de neutralité complète** : absence de comparaison fine des appels natifs `xSync/xLock`, ordre temporel, latences et contention non mesurés, ABI non inventoriée exhaustivement, méthodes V2/V3 et WAL non qualifiées, absence de qualification directe de `_persistent_journey()`. Aucune preuve d'atomicité/durabilité post-panne ni d'interruption interne du COMMIT.

**VFS-R01 et G03-R06 restent OUVERTES** jusqu'à nouvel arbitrage ; aucune clôture automatique sur la base du succès CI.

## Mandat au chat 03 — Recette indépendante ciblée

1. Inspecter au commit testé `88de630a` le nouveau banc `vfs_r01_compare.py`, le test `test_vfs_r01_compare.py` et les assertions bloquantes, sans supposer l'égalité de paramètres non effectivement vérifiés.
2. Confronter le code et les rapports aux journaux CI n°129, en rattachant les **224 exécutions** au bon commit et en distinguant résultats locaux non exécutés, CI exécutée et documentation finale.
3. Vérifier l'indépendance des répertoires N/W, l'égalité des SQL, des PRAGMA et des invariants, et que `differences=[]` porte exclusivement sur les critères comparés.
4. Qualifier les limites de l'observabilité native : aucune parité des I/O élémentaires, verrouillages, temps, concurrence ou garanties de synchronisation physique ne peut être déduite de la seule trace W.
5. Confirmer l'absence de modification du wrapper C, des modules applicatifs et d'injection de panne. Émettre un **PV 03 de réception limitée**, réserves et conseil de GO/NO-GO au 00 sans autoriser un chantier nouveau.

**Pas de nouveau développement, changement du wrapper, G03 pré-délégation, SIGKILL, injection, suspension, G04, ou modification du chemin métier.** Aucune fusion sur `main`, activation de fournisseur réel ni publication.

## Statuts inchangés

**VFS-R01 OUVERTE ; G03-R06 OUVERTE ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; VFS-R02 à R05, G03-R01 à R07 et RD01-R01 à R04 ouvertes. R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

## Prochaine action unique

Transmettre au chat 03 le rapport N/W au HEAD documentaire `0e1331a7`, le commit testé `88de630a` et les journaux CI n°129 pour réception indépendante, sans nouvelle expérimentation.
