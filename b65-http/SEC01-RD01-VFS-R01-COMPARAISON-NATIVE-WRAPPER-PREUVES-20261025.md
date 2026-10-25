# SEC-01 R1-RD01 — Comparaison expérimentale VFS native N / wrapper W
**Date :** 25 octobre 2026. **Périmètre :** prototype fictif isolé, COMMIT normal uniquement.  
**Mandat 00 :** `b65-http/DECISION-00-SEC01-RD01-VFS-R01-COMPARAISON-20261025.md`.  
**HEAD initial contrôlé :** `a2e451751179e74f6f59e3a1c9357f63fd6cd948`.  
**Branche :** `feature/b6-5-cartographie-interactive`.

## 1. Réalisation exacte
- Banc ajouté : `b65-http/rd01-vfs-step1/vfs_r01_compare.py`, commits `69b492b7f5558e1842144501cf689575b66e7c0b`, correction du type des assertions `be6c7384cd5f2734503fe036acf17e088ac98178`.
- Test bloquant ajouté : `b65-http/test_vfs_r01_compare.py`, commit `88de630acae24f8d960c6d4089dd8f21d7d3a630`.
- **Aucun changement** à `atlas_rd01_vfs.c`, `local_identity_bridge.py`, `persistent_sessions.py`, paramètres applicatifs ou workflow. Le wrapper existant est seulement compilé temporairement par le banc avec `cc` et `libsqlite3` du runner, sans installation de dépendance.
- Chaque témoin possède son répertoire `N/` ou `W/` et ses deux fichiers propres `sessions.sqlite` et `identities.sqlite`. La connexion N est ouverte par la VFS native ; W par `?vfs=atlas_rd01_observer`.
- Mêmes instructions DDL, DML et COMMIT normal : création session fictive, `ATTACH` de la base identités, création de parcours, puis `BEGIN IMMEDIATE`, mise à jour session et insertion du parcours dans une transaction commune. Même Python et même bibliothèque SQLite attestés (égalité du symbole et de version).
- Le banc compare les deux résultats SQL, listes des bases attachées, modes `journal_mode`, `synchronous`, phase COMMIT, `integrity_check` et fichiers journaux résiduels. Des assertions bloquantes rejettent toute divergence.

## 2. CI réellement exécutée
**GitHub Actions n°129 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40210414951  
**Commit testé :** `88de630acae24f8d960c6d4089dd8f21d7d3a630`.  
Conclusion : **completed / success**.
- JavaScript : **116/116**.
- SQLite : **11/11**.
- HTTP/identité, incluant le nouveau test comparatif : **97/97**.
- Total : **224 exécutions réussies** (ne veut pas dire 224 scénarios uniques).
- **Tests locaux de ce commit : non exécutés** dans cette conversation. Les preuves de réussite du code versionné viennent de la CI n°129.

## 3. Matrice de parité et de limites
| Critère | N — natif | W — wrapper inchangé | Qualification |
|---|---|---|---|
| Moteur SQLite | 3.45.1 | 3.45.1 | **Identité de version et symbole constatée dans le processus du runner** |
| Bibliothèques, ABI complète | Non inventoriées exhaustivement | Wrapper chargé sur même moteur | **Partiel : équivalence ABI complète non certifiée** |
| `database_list` | idb/identities.sqlite, main/sessions.sqlite | identique | **Même résultat** |
| `journal_mode` | delete, delete | delete, delete | **Même résultat** |
| `synchronous` | 2, 2 | 2, 2 | **Même résultat** |
| Transaction | BEGIN IMMEDIATE puis COMMIT | idem | **Même résultat** |
| Résultats SQL | session révoquée ; parcours fictif inséré | identiques | **Même résultat** |
| Intégrité | ok, ok | ok, ok | **Même résultat** |
| Journaux restant après fermeture | aucun | aucun | **Même résultat** |
| Codes d'erreur | aucune erreur de scénario relevée | aucune erreur de scénario relevée | **Parité du succès normal seulement** |
| `xSync`, `xLock`, séquence I/O par appel | non instrumentés | xSync=16 ; xWrite=60 ; xDelete=6 ; xOpen=8 ; xFileControl=34 | **NON MESURÉ de façon comparative** |
| Latences et contention | non mesurées | non mesurées | **NON MESURÉ** |
| Présence temporaire du super-journal | non tracée côté natif | wrapper observe des événements sur COMMIT normal | **Non comparable événement par événement** |
| Équivalence SHM V2, fetch V3 et WAL | hors cible | wrapper io_methods V1 | **NON DÉMONTRÉ** |
| Durabilité panne / arrêt interne COMMIT | aucune panne | aucune panne | **NON DÉMONTRÉ** |
| `_persistent_journey()` | non appelé | non appelé | **Hors périmètre** |

**Aucune divergence sur les propriétés fonctionnelles explicitement mesurées dans la CI n°129.** Cela ne prouve ni égalité d'ordonnancement, ni neutralité physique du wrapper. Une trace du seul W ne permet pas de reconstituer par supposition les appels internes de N.

## 4. Vérification des critères invalidants
- Pas de changement de version du moteur Python SQLite rapportée ni de symbole SQLite observé ; G01 demeure limité au runner.
- Pas de changement observé de modes DELETE/FULL.
- Pas de divergence SQL ou d'intégrité.
- Pas de fichier journal résiduel après fermeture normale.
- Aucune erreur sur le chemin normal.
- **Non contrôlé** : l'ordre/temps des verrous, les syncs effectivement exécutés côté natif, les codes d'erreur sous contention, les éventuelles différences de mmap et les fonctions V2/V3 absentes du wrapper.
- Ne pas qualifier les 16 `xSync` du W de « parité avec N ».

## 5. Verdict et précautions
**Parité fonctionnelle de scénario normal RECEVABLE techniquement dans le banc fictif et runner CI visé**, à soumettre à réception indépendante 03.  
**Neutralité complète du wrapper NON DÉMONTRÉE : VFS-R01 et G03-R06 demeurent ouvertes.**  
Aucune modification autorisée du wrapper n'a été engagée. La qualification de COMMIT normal ne démontre pas de reprise après panne, d'atomicité sous crash ou de durabilité physique. Aucune injection, aucun SIGKILL, aucun test G04.

**Recommandation au 00 après recette 03 :** considérer ce témoin comme une référence fonctionnelle préliminaire. N'envisager une correction d'interface native que si un écart réellement pertinent est identifié ou si la preuve des capacités nécessaires au scénario ne peut être obtenue avec l'instrument actuel. Nouvelle décision préalable obligatoire.

## 6. Continuité
VFS-R01 et G03-R06 ouvertes ; G03 préparatoire avec réserves, G04 NO-GO, G05 global partiel ; R1-RD01, R1, P0-01 ouverts ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.

**Prochaine action unique :** réception indépendante du chat 03 du commit `88de630a`, des journaux CI n°129 et du présent rapport, avant tout arbitrage supplémentaire du 00.
