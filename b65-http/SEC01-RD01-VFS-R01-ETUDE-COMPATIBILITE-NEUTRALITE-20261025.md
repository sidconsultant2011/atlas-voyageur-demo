# SEC-01 R1-RD01 — Étude documentaire VFS-R01 et G03-R06
**Date :** 25 octobre 2026  
**Nature :** lecture du code GitHub et de la documentation officielle SQLite ; **aucune compilation, aucun test nouveau, aucune modification C/Python ou applicative**.  
**Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD initial vérifié :** `779650a0b638a5631d06b750f434e7773d5521ea`.  
**Décision :** `b65-http/DECISION-00-SEC01-RD01-VFS-R01-ETUDE-20261025.md`.

## 1. Verdict exécutif

**GO CONDITIONNEL pour examiner ultérieurement un correctif isolé**, mais **NO-GO actuel pour toute implémentation, comparaison expérimentale, injection et G04**.

La déclaration `sqlite3_io_methods io={1,...}` et `sqlite3_vfs.iVersion=2` concerne deux objets différents et **ne constitue pas en soi un défaut ABI** : l'interface fichier V1 comporte `xClose`, `xRead`, `xWrite`, `xTruncate`, `xSync`, `xFileSize`, `xLock`, `xUnlock`, `xCheckReservedLock`, `xFileControl`, `xSectorSize` et `xDeviceCharacteristics`. La VFS V2 ajoute essentiellement `xCurrentTimeInt64` à ses méthodes V1. Les méthodes fichiers SHM sont ajoutées en V2 et les méthodes `xFetch/xUnfetch` en V3 **de l'interface fichier**, et non de la VFS elle-même.

Le risque **réel et circonscrit** est que chaque fichier ouvert par le wrapper expose une table V1 même si le fichier natif proposait une table V2 ou V3. Cette réduction des capacités ne démontre pas un échec en rollback-DELETE, mais rend toute prétention de neutralité générale injustifiée. Les autres risques sont la perturbation de l'ordre et du timing par la trace post-délégation, la qualité de remontée des erreurs, et la préservation des verrouillages et synchronisations.

**Une seule condition technique prioritaire pour la suite :** disposer, avant toute réalisation, d'un contrat de parité **des méthodes et des effets** du chemin rollback-DELETE multi-bases entre VFS native et wrapper, associé à un protocole de comparaison indépendant et falsifiable. Si la parité ne peut pas être démontrée sur le moteur Python ciblé, **NO-GO pour attribuer au chemin applicatif les conclusions du banc**.

## 2. Sources et portée de vérification

**Dépôt GitHub lu sur la branche :**
- `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c` (wrapper étudié).
- `b65-http/rd01-vfs-step1/rd01_vfs_step1.py` (scénario SQLite ATTACH et paramètres).
- `b65-http/SEC01-RD01-G03-PREPARATION-PREUVES-20261025.md` (résultats précédents et limites).
- Décision officielle `DECISION-00-SEC01-RD01-VFS-R01-ETUDE-20261025.md`.

**Références normatives externes consultées :**
- https://www.sqlite.org/c3ref/io_methods.html — structure et versions des méthodes d'un fichier.
- https://www.sqlite.org/c3ref/vfs.html — structure et versions de `sqlite3_vfs`.
- https://www.sqlite.org/vfs.html — couche VFS, sélection par connexion et par base attachée.
- https://www.sqlite.org/atomiccommit.html — fonctionnement et hypothèses du COMMIT rollback multi-fichiers.

Les lignes C et Python sont **constatées** ; les comportements des méthodes natives effectivement appelées au runtime non instrumenté ne sont **pas directement mesurés dans cette étude**. GitHub Actions n°120 est une preuve historique déjà reçue, non une nouvelle exécution : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40208301806 (commit `03986691d23f0044c5fcbe9c1ac2a169f0c938c6`).

## 3. Inventaire précis des interfaces du wrapper

### 3.1 Interface `sqlite3_vfs`

Dans `atlas_rd01_register()` :
- `parent=sqlite3_vfs_find(0)` ; puis `wrapper=*parent` (copie de la structure du VFS natif) ; `wrapper.zName="atlas_rd01_observer"` ; `wrapper.szOsFile=sizeof(Obs)` ; `wrapper.iVersion=2`.
- Méthodes remplacées par des adaptateurs : `xOpen`, `xDelete`, `xAccess`, `xFullPathname`, `xDlOpen`, `xDlError`, `xDlSym`, `xDlClose`, `xRandomness`, `xSleep`, `xCurrentTime`, `xGetLastError`, `xCurrentTimeInt64`.
- Toutes ces adaptations délèguent au parent ; seules `xOpen` et `xDelete` ajoutent une trace d'événement. `xGetLastError` et `xCurrentTimeInt64` disposent de retours de repli dans le code, sans preuve de leur équivalence en situation de défaut.
- Les méthodes VFS V3 `xSetSystemCall`, `xGetSystemCall`, `xNextSystemCall` ne sont pas annoncées puisque `wrapper.iVersion=2`, même si la copie `wrapper=*parent` a pu en conserver les pointeurs : elles ne font pas partie du contrat déclaré.

### 3.2 Interface `sqlite3_io_methods`

Dans `op()`, le wrapper alloue `w->inner` avec `parent->szOsFile` et appelle `parent->xOpen()`. En cas de succès, il expose systématiquement `w->base.pMethods=&io`, où `io.iVersion=1`.

| Catégorie | Méthodes | État constaté dans le wrapper | Impact susceptible d'apparaître |
|---|---|---|---|
| Fichier V1 : lecture et dimensions | `xClose/xRead/xTruncate/xFileSize` | Déléguées à `w->inner->pMethods` ; `xClose` trace après retour | Pas de perte de capacité V1 attendue ; erreur et durée de vie du handle à comparer |
| Fichier V1 : écriture et synchronisation | `xWrite/xSync` | Déléguées ; émission post-retour `write()` avec taille ou flags | Latence, ordre relatif observable, code retour et séquencement fsync potentiellement perturbés |
| Fichier V1 : verrouillage | `xLock/xUnlock/xCheckReservedLock` | Déléguées sans trace propre | Parité de verrous probable par structure mais **non mesurée**, spécialement entre deux connexions/processus |
| Fichier V1 : commandes et propriétés | `xFileControl/xSectorSize/xDeviceCharacteristics` | Déléguées ; `xFileControl` trace opcode/retour | Des propriétés déclarées par la VFS mère peuvent affecter les chemins optimisés et les garanties physiques |
| Fichier V2 | `xShmMap/xShmLock/xShmBarrier/xShmUnmap` | **Non exposées** dans `io.iVersion=1` | Incompatibilité ou chemins différents en cas de WAL / shared-memory ; **hors scénario DELETE actuel** |
| Fichier V3 | `xFetch/xUnfetch` | **Non exposées** dans `io.iVersion=1` | Optimisation mmap absente ; différence possible de `xRead`, temps et appels observables, même hors WAL |
| VFS V3 | `xSetSystemCall/xGetSystemCall/xNextSystemCall` | Non annoncées par `wrapper.iVersion=2` | Fonctionnalités d'introspection/substitution des syscalls indisponibles ; non prouvé comme défaut dans le scénario courant |

**Point de vérification impératif :** la valeur effective de `parent->iVersion` et de `w->inner->pMethods->iVersion` n'est **pas enregistrée** dans les preuves antérieures. Il ne faut donc pas inventer que la VFS native CI exposait précisément toutes les méthodes V2 ou V3 ; la perte est **potentielle** au regard des API, pas une observation comparative instrumentée.

**Précaution `xOpen` :** SQLite précise qu'un `xClose` peut être appelé après un `xOpen` en échec si `pMethods` a été laissé non nul. Le wrapper fait `memset(w,0)` et ne définit `w->base.pMethods` qu'en cas de succès : propriété cohérente par lecture, sans simulation de défaut réalisée.

## 4. Scénario strict analysé

Le banc Python `rd01_vfs_step1.py` construit, depuis le Python du banc et son SQLite déjà préqualifié :
1. une base `sessions.sqlite` ouverte par URI `?vfs=atlas_rd01_observer` ;
2. `PRAGMA main.journal_mode=DELETE`, `PRAGMA main.synchronous=FULL` ; création et écriture de fixture ;
3. `ATTACH DATABASE` de `identities.sqlite`, PRAGMA `idb.journal_mode=DELETE` et `idb.synchronous=FULL`, création de fixture ;
4. `BEGIN IMMEDIATE`, mise à jour d'une session et insertion d'un parcours fictif dans la base attachée ; `COMMIT` réussi ; contrôle des bases sur copie.

**Confirmé précédemment par CI** : les deux bases et journaux ont généré des traces `xOpen`, et un `xDelete` corrélé au candidat super-journal a été observé au retour de la VFS mère. Ce résultat ne mesure pas l'ordonnancement du même scénario sans VFS.

La documentation SQLite autorise des VFS différentes entre bases d'une même connexion. Le fait d'attacher une base ne garantit donc **pas abstraitement** qu'elle utilise la même VFS ; il faut le prouver dans chaque environnement. Le banc l'a montré pour les ouvertures observées sous CI ciblée.

**Dans ce scénario**, les opérations de fichiers V1 (ouverture, lectures/écritures, synchronisations, verrous, delete et contrôle de fichiers) sont les capacités pertinentes ; SHM V2 ne constitue pas une exigence fonctionnelle systématique en rollback-DELETE. En revanche, le rôle de V3 fetch et l'effet de sa suppression doivent être mesurés plutôt que déclarés inexistants.

## 5. Matrice des écarts — niveaux de preuve

| Question | Constaté | Susceptible d'influencer | Non démontré |
|---|---|---|---|
| `sqlite3_vfs.iVersion=2` et `sqlite3_io_methods.iVersion=1` | Oui ; deux interfaces distinctes | Compatibilité fonctionnelle d'extensions de méthodes | Erreur intrinsèque de version : **non** |
| Méthodes fichiers V1 du wrapper | Délégation par code | Ordre, latence, comportement en erreur | Parité native vs wrapper sous mêmes conditions |
| `xLock/xUnlock` | Délégués | Contentions et timings interprocessus | Même ordre/durée/verdict sous concurrence |
| `xWrite/xSync/xDelete` | Délégués ; trace après retour | Effet observateur, séquence et latence ; suppressions du super-journal | Parité temporelle / durabilité / absence de pertes d'attestation |
| `xFileControl` | Délégué, opcode tracé | Chemins selon options VFS, erreurs, hints | Parité opcode/retour et effets sur COMMIT |
| Fonctions SHM V2 | Non exposées | WAL et accès mémoire partagée | Défaut en rollback-DELETE ; non démontré et hors cible |
| Fonctions V3 fetch/unfetch | Non exposées | mmap / optimisation et distribution des appels de lecture | Influence exacte sous paramètres CI |
| Fonctionnalités VFS V3 | Non annoncées | Introspection / fonctions syscall | Exigence pour le COMMIT DELETE testé |
| `serial` global et `emit()` vers trace | Compteur sans verrou ; `write()` après délégation ; basename | Émission en concurrence, interférence I/O, collisions de chemin | Ordre garanti sur plusieurs threads, trace durable en cas de panne |
| Couverture ATTACH | Observée sur banc fictif antérieur | VFS spécifique par base ; chemins de journaux | Couverture de `_persistent_journey()` et du runtime non instrumenté |

## 6. Comparaison native / wrapper : contrat technique futur (non exécuté)

La future comparaison doit être conduite **sur une même version SQLite, un même environnement local et des fixtures fictives indépendantes**, en gardant identiques SQL, paramètres, schéma, modes, stockage et absence de panne. Aucune modification applicative n'est exigée pour ce protocole de banc.

**Témoin N — VFS native :** exécuter la transaction témoin avec moteur Python de référence, enregistrer les PRAGMA et identifiants de fichiers, les résultats SQL, les états des deux bases après COMMIT, verrous observables et erreurs éventuelles ; si l'ordre des I/O doit être comparé, utiliser un traçage externe clairement identifié comme observateur lui aussi, sans lui attribuer une neutralité parfaite.

**Témoin W — wrapper :** exécuter la même transaction avec VFS d'observation ; enregistrer `parent->iVersion`, `inner->pMethods->iVersion`, méthodes accessibles par type de fichier, `xFileControl` (opcodes/retours), `xWrite/xSync` (taille, flags, résultats), `xDelete` (rôle et retour), classes de verrou, durée et nombre d'événements, ainsi que les fichiers de journalisation. Les traces devront distinguer les méthodes **effectivement appelées** des méthodes **simplement exposées**.

| Critère | Différence tolérable sous justification | Écart invalidant |
|---|---|---|
| Schémas et résultats métier | Aucune différence | État final différent, session ou parcours incohérent |
| `integrity_check` et invariants | Aucun échec toléré | Corruption, incohérence ou état partiel après COMMIT normal |
| Codes de résultat SQLite, erreurs, quotas et verrous | Variabilité temporelle documentée seulement, sans changement de sémantique | Un succès transformé en erreur, perte de verrou, deadlock, erreur masquée |
| Journal mode / synchronous | Aucune différence | WAL/OFF/MEMORY à la place de DELETE ou `synchronous` dégradé |
| Écritures, journaux, synchronisations et suppression super-journal | Différences expliquées par l'observateur/optimisation **sans perte de mécanisme requis** | Événement essentiel absent inexpliqué, xSync omis ou erreur nouvelle |
| Comptages I/O / durée | Variations mesurées acceptables si mécanisme identique | Déviation systématique rendant le COMMIT ou les attestations ininterprétables |
| Méthodes d'API disponibles | Limitation strictement justifiée au profil DELETE sans conséquence observée | Fonction native requise par le scénario et non relayée, ou remplacement silencieux de moteur |
| Reproductibilité | Variations de noms aléatoires et latences possibles | Dépendance non contrôlée empêchant d'associer résultats et fichiers |

La comparaison de nombre d'appels, timings et verrous exige des **répétitions planifiées**, sans qu'aucune quantité de répétitions ni seuil chiffré ne puisse être considéré validé par la présente étude. L'identification du super-journal ne doit jamais se reposer sur un basename fixe.

La CI historique 116/11/96 teste la non-régression fonctionnelle avec wrapper ; elle **ne constitue pas une comparaison avec la VFS native**.

## 7. Raccordement ultérieur à `_persistent_journey()`

La voie métier utilise les sessions dans la base principale et les identités dans une base `ATTACH`, `BEGIN IMMEDIATE`, `state._authorize()` avec accès à `request_events`, puis une opération de parcours dans la base d'identité. **Cette voie n'a pas été exécutée dans la présente étude.**

Une comparaison transposable au métier exigerait d'attester : même moteur Python, même bibliothèque native et ABI, deux écritures effectives dans la transaction, VFS effectivement sélectionnée pour chaque fichier, mêmes mécanismes de journaux et verrous et conservation des données fictives. Une simulation témoin SQL analogue ne remplace pas l'exécution de cette voie. Toute utilisation du code applicatif, même pour qualification, demanderait l'autorisation correspondante du 00.

## 8. Risques résiduels et décision future

**Priorité technique unique : contrat de parité native/wrapper dans le profil rollback-DELETE multi-bases** (interfaces, résultats, journalisation, verrouillage, synchronisation et intégrité).

Risques à conserver explicitement : réduction de `io_methods` V2/V3 vers V1 ; version VFS2 non équivalente à VFS3 ; fenêtre temporelle ajoutée par `emit()`, séquences non sûres en multithread, absence de fsync individuel du journal de preuves ; rôle du super-journal prouvé seulement par une corrélation VFS post-retour ; neutralité et durabilité physique non démontrées.

**Proposition de GO conditionnel ultérieur :** étude suivie, sur décision distincte du 00, d'un correctif **uniquement de banc** qui préserve les capacités effectivement disponibles dans la VFS mère et permet de mesurer la parité avec un témoin natif. Les interfaces étendues ne doivent pas être activées aveuglément : la version annoncée du wrapper doit refléter les fonctions réellement implémentées et sécurisées.

**NO-GO motivé** si identité moteur/ABI non démontrée, si les méthodes nécessaires à DELETE/FULL sont perdues, si les verrous ou synchronisations diffèrent de façon invalidante, ou si la comparaison ne distingue pas les effets observateurs des propriétés essentielles. Aucun SIGKILL, crash, G04 ni conclusion générale de durabilité ne seraient permis par un simple correctif d'interface.

## 9. Preuves et gouvernance

Aucun test local ni GitHub Actions lancé pour cette étude. Les derniers résultats de CI mentionnés sont **antérieurs** et rattachés à leur commit propre ; aucun résultat neuf n'est revendiqué. Aucun wrapper C ni module applicatif modifié.

**VFS-R01 OUVERTE ; G03-R06 OUVERTE ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; RD01-R01 à RD01-R04, R1-RD01, R1, P0-01 ouverts ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.**

**Prochaine action unique :** soumettre ce rapport au chat 00 pour décision explicite d'ouvrir ou non, ultérieurement, une qualification comparée du wrapper contre la VFS native, sans mise en œuvre implicite.
