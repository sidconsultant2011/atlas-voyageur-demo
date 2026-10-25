# Décision 00 — SEC-01 R1-RD01 — Soumission en recette indépendante de la qualification des verrous N/W

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `33ffae7b7369684a51f23a0b3a59cb0149423083`  
**Chantier unique :** réception indépendante de la qualification des effets de verrouillage et synchronisation observables N/W.

## Sources et preuves vérifiées par le 00

- Mandat du 00 : `b65-http/DECISION-00-SEC01-RD01-VFS-R01-VERROUS-SYNC-20261025.md`.
- Rapport chat 01 : `b65-http/SEC01-RD01-VFS-R01-VERROUS-SYNC-PREUVES-20261025.md`.
- GitHub Actions **n°135**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980 : **completed / success**, commit testé **`fc6eded13fa15b8776b12dd0cd494349d0a2e906`**.
- **116/116 JavaScript, 11/11 SQLite, 98/98 HTTP/identité/banc** : total **225 exécutions réussies**, pas nécessairement 225 scénarios distincts.
- Diff depuis `91080739686072bafdd212b29e63bfef047776bf` jusqu'au HEAD documentaire : trois fichiers **ajoutés** : `b65-http/rd01-vfs-step1/vfs_r01_contention.py`, `b65-http/test_vfs_r01_contention.py`, et le rapport de preuves. **Wrapper C et modules applicatifs inchangés.**
- Ligne `RD01 VFS R01 LOCK SYNC PARITY` : **COMMIT** et **ROLLBACK** produisent chacun `SQLITE_BUSY=5` lors d'une tentative incompatible du second écrivain, puis un réessai réussi après libération normale, avec résultats intermédiaires et finaux égaux N/W, intégrité `ok/ok`, DELETE/DELETE, FULL(2)/FULL(2), aucun journal résiduel.
- **45 retours `xSync` réussis enregistrés côté W seulement**, sans trace native N comparable. La persistance physique, l'ordre événementiel et la neutralité temporelle ne sont pas mesurés.
- **Aucun test local exécuté dans la conversation du chat 01** sur le commit final ; preuve d'exécution rattachée à la CI n°135.
- Aucun SIGKILL, aucune injection de panne ni essai G04.

## Décision du 00

**LIVRAISON TECHNIQUE ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03.** Cette décision ne vaut **pas encore clôture de la qualification de contention**, ni clôture VFS-R01 ou G03-R06.

L'absence de divergence est établie seulement sur les **effets transactionnels observables** des deux scénarios déterministes, dans le runtime CI ciblé. Les compteurs `xSync` côté W ne peuvent pas être attribués à N, ni assimilés à des synchronisations physiquement durables.

### Mandat unique de recette indépendante au chat 03

1. Lire les fichiers `vfs_r01_contention.py` et `test_vfs_r01_contention.py` au commit **`fc6eded1`** ; contrôler les deux connexions, les deux threads, le `busy_timeout=0`, la barrière Python hors callback, les attentes bornées à 8 secondes, la libération `finally` et les états exigés.
2. Vérifier la correspondance stricte entre scénarios N/W, les deux variantes COMMIT/ROLLBACK, l'exclusion `SQLITE_BUSY=5`, les réessais, les résultats SQL, l'intégrité, les paramètres DELETE/FULL et l'absence de journaux résiduels.
3. Confronter les assertions bloquantes à la trace de la CI n°135, vérifier commit et totaux, et distinguer les tests CI des tests locaux non exécutés par le chat 01.
4. Qualifier les réserves : **pas de comparaison des `xSync/xLock` élémentaires N/W**, pas de preuve de persistance après panne, de neutralité temporelle, de couverture de `_persistent_journey()`, de contention interprocessus ou d'équivalence générale VFS V2/V3.
5. Émettre un **PV 03 indépendant** avec verdict limité, preuves, risques résiduels et recommandation au 00. Aucun développement ni nouvel essai ne sont demandés par ce mandat.

### Interdictions et statuts

**Aucun GO pour modification du wrapper C, instrumentation causale G03, interruption, SIGKILL, injection, G04 ou exécution du chemin métier.** Aucune fusion `main`, donnée réelle, fournisseur réel ni publication.

**VFS-R01 OUVERTE ; G03-R06 OUVERTE ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; R1-RD01 et P0-01 OUVERTS ; R1-C01 PARTIEL ; R1 OUVERTE ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

## Prochaine action unique

Transmettre au chat 03 ce mandat, le rapport du chat 01 et les journaux CI n°135 pour réception indépendante des effets transactionnels N/W, sans développement nouveau.
