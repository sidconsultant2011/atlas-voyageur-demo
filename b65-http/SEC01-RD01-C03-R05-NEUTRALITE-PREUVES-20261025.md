# SEC-01 R1-RD01 — C03-R05 — Qualification fonctionnelle et caractérisation temporelle N/W/C03

**Date :** 25 octobre 2026. **Branche :** `feature/b6-5-cartographie-interactive`. **Mandat 00 :** `b65-http/DECISION-00-SEC01-RD01-C03-R05-NEUTRALITE-20261025.md`. **Départ vérifié :** `ed4a40e19e633ad32cc28ae6580990693b00cb81`.

## 1. Ordre effectif et commits

1. **`816556e2b54e3cc4c87523d5028b1b5320a9c431`** : protocole de mesure versionné **avant ajout du banc comparatif** : `b65-http/SEC01-RD01-C03-R05-PROTOCOLE-20261025.md`.
2. **`287b5a0d2498a3bbe61c1398329e1976bf34950c`** : nouveau banc isolé `b65-http/c03_r05_compare.py`, réutilisant `vfs_r01_contention._scenario`, VFS N native, W référence et C03 expérimentale existantes, sans toucher aux sources C.
3. **`aa26055edeb363d4ff44f3c83010a016787a250e`** : précision du **périmètre temporel mesuré**, avant toute CI contenant le test de campagne : démarrage du chronomètre juste avant `_scenario`, comprenant création et initialisation des bases, contention, fermeture, vérification d'intégrité et absence de journaux.
4. **`d5248e4510c1c3502138a5bf62f1213ba858e8fd`** : ajout du test bloquant `b65-http/test_c03_r05.py`, comprenant six échauffements hors statistiques, 18 mesures et assertions de parité N/W/C03.

**Inchangés :** `atlas_rd01_vfs.c`, `c03_vfs.c`, moteur SQLite, workflow, code métier et `_persistent_journey()`. Aucun callback causal, aucune lecture de journaux à chaud, aucune panne provoquée, aucun SIGKILL ni G04.

## 2. Environnement, échantillonnage et mode de comparaison

**CI n°186** : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40234530686.  
**Commit exact testé :** `d5248e4510c1c3502138a5bf62f1213ba858e8fd`.  
**Conclusion :** `completed / success`.

- Linux `6.17.0-1022-azure-x86_64`, glibc `2.39`, Python `3.12.3`, SQLite **3.45.1**.
- Les wrappers C de référence et expérimental sont compilés **temporairement** par le sous-processus, puis enregistrés dans la même bibliothèque SQLite. Le banc vérifie égalité version/symbole avant d'autoriser W ou C03.
- Chaque couple scénario / VFS est isolé dans son propre **processus et répertoire temporaires**, ce qui évite de confondre les registres C03 successifs. Les processus se terminent normalement.
- Deux scénarios : `COMMIT` et `ROLLBACK` du premier écrivain ; chaque scénario vérifie `SQLITE_BUSY=5` du second écrivain sous `BEGIN IMMEDIATE`, libération normale, état intermédiaire et réessai concluant par COMMIT.
- `journal_mode=DELETE` et `synchronous=FULL` sur les deux bases, `integrity_check=[ok,ok]`, absence de fichiers journaux résiduels, comparaison exacte des états SQLite retournés.
- **6 échauffements** non inclus dans les statistiques, **3 répétitions mesurées pour chacun des six couples** = 18 mesures. Ordres des modes dans les trois tours : N/W/C03, W/C03/N, C03/N/W. L'ordre des scénarios est COMMIT puis ROLLBACK.
- Horloge monotone `perf_counter_ns()` du sous-processus. Durée depuis avant `_scenario` jusqu'après validation des résultats, **y compris initialisation des bases**, à l'exclusion de la compilation, du démarrage du processus et de l'enregistrement VFS. La mesure comprend les barrières Python et le bruit d'ordonnancement.
- **Aucun seuil de performance ou budget de surcharge validé**. Il est interdit de déduire une neutralité temporelle de ces observations.

## 3. Matrice fonctionnelle — CI n°186

| Critère | N | W | C03 | Qualification |
|---|---|---|---|---|
| Bibliothèque SQLite | 3.45.1 | version/symbole identiques | version/symbole identiques | Même moteur runner, vérifié |
| Journaux deux bases | DELETE | DELETE | DELETE | Conforme |
| Synchronisation configurée | FULL (2) | FULL (2) | FULL (2) | Conforme |
| Exclusion du second écrivain | `SQLITE_BUSY=5` | `SQLITE_BUSY=5` | `SQLITE_BUSY=5` | Même effet fonctionnel |
| Premier écrivain COMMIT | valeur intermédiaire modifiée | identique | identique | Conforme |
| Premier écrivain ROLLBACK | état antérieur conservé | identique | identique | Conforme |
| Libération et réessai | second COMMIT réussi | identique | identique | Conforme |
| Intégrité des deux bases | `ok/ok` | `ok/ok` | `ok/ok` | Conforme |
| Journaux résiduels fin normale | aucun | aucun | aucun | Conforme |
| Divergence des résultats | aucune | aucune | aucune | **Parité fonctionnelle dans le banc** |
| Chronologie fine des callbacks natifs | non instrumentée | trace W | C03 capture en mémoire | **Non comparable** |
| Durabilité physique / coupure / G04 | non testée | non testée | non testée | **Non démontrée** |

**Critère bloquant** : tout résultat différent, refus `SQLITE_BUSY` absent, erreur d'observation `c03_overflow`, défaut de configuration ou journal résiduel échoue immédiatement au test. Aucun de ces échecs n'a été relevé en CI n°186.

La campagne de contention ne recertifie pas à elle seule le décodeur de super-journal, mais le même workflow exécute les tests C03-R01, R02 et R03 et le certificat COMMIT normal fictif préexistants. Leur absence d'échec dans CI n°186 confirme leur non-régression dans cette exécution, sans extension de périmètre.

## 4. Durées brutes et dispersion en millisecondes

| Scénario | Mode | 3 durées brutes (ms) | Médiane (ms) | Min–max (ms) | Amplitude (ms) |
|---|---|---|---:|---|---:|
| COMMIT | N | 13.017985 ; 12.882795 ; 12.172797 | **12.882795** | 12.172797–13.017985 | 0.845188 |
| COMMIT | W | 13.384279 ; 13.655016 ; 13.613391 | **13.613391** | 13.384279–13.655016 | 0.270737 |
| COMMIT | C03 | 12.702871 ; 12.865131 ; 13.330057 | **12.865131** | 12.702871–13.330057 | 0.627186 |
| ROLLBACK | N | 9.853501 ; 11.551296 ; 10.139528 | **10.139528** | 9.853501–11.551296 | 1.697795 |
| ROLLBACK | W | 11.052217 ; 10.768111 ; 10.682174 | **10.768111** | 10.682174–11.052217 | 0.370043 |
| ROLLBACK | C03 | 12.886411 ; 10.535503 ; 10.462907 | **10.535503** | 10.462907–12.886411 | 2.423504 |

**Lecture :** la médiane C03 est proche de N sur COMMIT et légèrement supérieure sur ROLLBACK dans ce lot. Les amplitudes et l'environnement partagé empêchent d'attribuer cette différence à l'instrumentation plutôt qu'au bruit/à la variabilité d'I/O et d'ordonnancement. Les valeurs mesurent un **parcours de scénario complet**, et non le coût isolé d'un `xWrite` ou `xClose`. Trois échantillons par groupe ne fournissent aucune borne robuste de latence maximale ou de régression rare.

Il n'y a **pas de seuil chiffré**, donc **pas de verdict de performance GO/NO-GO**. Le résultat est une **caractérisation descriptive** seulement. Aucun calcul a posteriori ne fait office de seuil accepté.

## 5. Tests GitHub Actions et tests locaux : distincts

- CI n°186, commit `d5248e4510c1c3502138a5bf62f1213ba858e8fd` : **116/116 JavaScript ; 11/11 SQLite ; 126/126 HTTP/identité/banc** ; soit **253 exécutions réussies**. Ce total peut compter des découvertes `unittest` redondantes ; ce n'est pas 253 scénarios distincts.
- **Tests locaux du commit exact : non exécutés.** Les seules nouvelles mesures quantitatives invoquées viennent de cette CI.
- Les CI antérieures n°129, 135 et 178 restent des références de continuité, **pas** des résultats de la nouvelle campagne triple.

## 6. Verdict et limites résiduelles

**Neutralité fonctionnelle sur les scénarios COMMIT/ROLLBACK et contention N/W/C03 du banc fictif : démontrée dans le profil CI observé.** La parité n'est ni globale à SQLite ni garantie sur un autre OS/moteur, un chemin métier, d'autres contraintes de charge ou des défaillances.

**Surcharge temporelle : caractérisée descriptivement, sans verdict de neutralité temporelle.** Non démontrés : latence sous charges variées, comportement en concurrence interprocessus, appels internes de synchronisation VFS N, persistance physique, interception `BEFORE_DELEGATE`, COMMIT interrompu et G04.

**À soumettre au chat 03** pour réception indépendante du périmètre fonctionnel, de la traçabilité des durées et de la portée des conclusions. C03-R05 reste **OUVERTE** jusqu'à décision du 00.

**Statuts sans clôture implicite :** C03-R01 à R03 clôturées dans le périmètre fictif ; C03-R04, R05 et R06 ouvertes ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G04 NO-GO, B6.5 en recette, B6.3 et production NO-GO.

**Prochaine action unique :** transmettre au chat 03 le commit testé `d5248e45`, la CI n°186, le protocole préalable et le présent rapport pour recette indépendante de C03-R05.
