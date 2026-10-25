# SEC-01 R1-RD01 — VFS-R01 / G03-R06 — Qualification des verrous et synchronisations N/W
**Date :** 25 octobre 2026. **Périmètre :** banc SQLite fictif isolé, contention contrôlée, sans panne.
**Décision 00 :** `b65-http/DECISION-00-SEC01-RD01-VFS-R01-VERROUS-SYNC-20261025.md`.
**Branche :** `feature/b6-5-cartographie-interactive`. **HEAD initial vérifié :** `91080739686072bafdd212b29e63bfef047776bf`.

## Protocole falsifiable (réalisé)
Deux témoins indépendants, N (VFS SQLite native) et W (wrapper C existant non modifié), utilisent le **même moteur SQLite 3.45.1** dans le runner Linux et des bases fictives dans des répertoires distincts. Pour chacun des modes de résolution COMMIT et ROLLBACK, deux connexions ouvertes dans deux threads distincts exécutent :
1. Préparer deux bases via `ATTACH DATABASE`, `journal_mode=DELETE` et `synchronous=FULL (2)` sur chacune ; insertion d'une session et d'un parcours fictifs.
2. Le premier écrivain acquiert `BEGIN IMMEDIATE`, met à jour **les deux bases**, puis attend sur une barrière Python `threading.Event` (hors SQLite).
3. Le second ouvre une connexion indépendante avec `busy_timeout=0` et tente `BEGIN IMMEDIATE`. **Attendu obligatoirement : `SQLITE_BUSY=5`**. Tout succès anticipé échoue au test.
4. Le premier écrivain termine par COMMIT normal ou ROLLBACK normal selon le scénario. Le parent relit les deux bases et exige l'état intermédiaire attendu ; ensuite seulement le second écrivain reçoit l'autorisation de réessayer.
5. Le second écrivain acquiert `BEGIN IMMEDIATE`, écrit sur les deux bases, COMMIT normalement. Vérifier l'état final, `integrity_check=ok` des deux bases, DELETE/FULL et absence de journaux résiduels après fermeture.
6. Toutes les barrières sont bornées à **8 secondes** ; libération des événements dans `finally`, fermeture des connexions et `join` des threads. Aucun `SIGKILL`, arrêt brutal, faute injectée, G04, ni callback VFS modifié.

**Critères invalidants** : absence de refus SQLITE_BUSY pendant exclusion, code SQLite inattendu, impossibilité de réessayer après COMMIT/ROLLBACK, états N/W différents, divergence de PRAGMA, corruption, journaux résiduels ou threads non terminés. Une simple variation de délai n'est pas un critère d'échec.

## Développement ciblé
- Ajout `b65-http/rd01-vfs-step1/vfs_r01_contention.py`, commit `f84403f019b145ed6b645a5b786d9dfba6e29db7`.
- Ajout `b65-http/test_vfs_r01_contention.py`, commit `fc6eded13fa15b8776b12dd0cd494349d0a2e906`.
- Aucun changement à `atlas_rd01_vfs.c`, `local_identity_bridge.py`, `persistent_sessions.py`, `vfs_r01_compare.py` (comparaison normale préexistante), ni au workflow.
- Compilation temporaire du **wrapper inchangé** avec `cc` et `libsqlite3` déjà disponibles sur le runner ; aucune installation de dépendance.

## Résultat et preuve CI
**GitHub Actions n°135 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980
**Commit testé :** `fc6eded13fa15b8776b12dd0cd494349d0a2e906`.
**Conclusion :** `completed / success`.
- JavaScript : 116/116.
- SQLite hors ligne : 11/11.
- HTTP/identité/banc : 98/98.
- **225 exécutions réussies** ; pas nécessairement 225 scénarios distincts.
- Les journaux contiennent la trace structurée `RD01 VFS R01 LOCK SYNC PARITY`.
- **Tests locaux de ce commit dans la conversation : non exécutés.** Ne pas confondre la CI et un contrôle local.

## Matrice N/W observée
| Critère | N | W | Résultat |
|---|---|---|---|
| Moteur | SQLite Python 3.45.1 | Même version, symbole natif identique | Recevable sur runner CI |
| Deux bases et transaction | ATTACH, BEGIN IMMEDIATE | Idem | Recevable |
| Écriture incompatible sous verrou | `SQLITE_BUSY=5` | `SQLITE_BUSY=5` | **Parité du refus** |
| Après COMMIT holder | Valeurs intermédiaires session=1, label=holder | Identiques | **Parité de visibilité** |
| Après ROLLBACK holder | Valeurs initiales session=0, label=initial | Identiques | **Parité d'annulation** |
| Réessai après libération | COMMIT accepté, session=2, label=contender | Identique | **Parité du déblocage** |
| Intégrité des deux bases | `ok,ok` | `ok,ok` | Recevable |
| Journalisation | DELETE, DELETE | DELETE, DELETE | Identique |
| Synchronisation configurée | FULL(2), FULL(2) | FULL(2), FULL(2) | Identique |
| Journaux restant après fermeture | Aucun | Aucun | Identique |
| `xSync` | Non tracé par N | **45 retours `xSync` avec code 0** dans W | **NON COMPARABLE événement par événement** |
| xLock, xUnlock, ordre I/O, timing précis | Non instrumentés | Wrapper délègue les méthodes selon lecture C | **NON MESURÉ comparativement** |
| Effet physique de fsync, durabilité crash | Non évalués | Non évalués | **NON DÉMONTRÉ** |

Les résultats de la comparaison fonctionnelle précédente (CI n°129) sont **conservés**, sans être présentés comme une nouvelle étude dans ce chantier. Les seuls nouveaux scénarios de la CI n°135 sont les contentions COMMIT et ROLLBACK.

## Limites et risques résiduels
L'expérience compare des **effets transactionnels**, pas une identité temporelle de comportement. L'instrumentation W ajoute un fichier de trace et une surcharge et n'offre toujours que `sqlite3_io_methods.iVersion=1`. Le témoin N ne fournit pas de trace `xSync` interne : **45 retours synchronisés W ne signifient pas 45 synchronisations physiques durables, ni parité native**. Aucune validation d'une panne OS, coupure électrique, stockage réseau, WAL, moteur multiplateforme, contention interprocessus ou du chemin applicatif `_persistent_journey()`.

Le protocole emploie deux **threads**, deux **connexions** et une base de sessions partagée par paire, sans processus enfant ; les connexions sont fermées normalement. `busy_timeout=0` élimine l'attente SQLite implicite, tandis que les barrières Python gardent l'entrelacement contrôlé.

**Proposition de réception indépendante 03 :** recevoir la parité des effets d'exclusion et de déblocage dans les **deux scénarios testés**, sans considérer VFS-R01 / G03-R06 complètement soldées. La limite physique et la couverture native des méthodes restent ouvertes. Aucun GO G04 ni production.

**Statuts inchangés :** VFS-R01 et G03-R06 ouvertes ; G03 reçu avec réserves ; G04 NO-GO ; G05 global partiel ; R1-RD01, R1 et P0-01 ouverts ; B6.5 en recette ; B6.3 et production NO-GO.

**Prochaine action unique :** soumettre le présent rapport, le commit `fc6eded1` et les journaux GitHub Actions n°135 au chat 03 pour réception indépendante de la seule qualification des verrous et synchronisations.
