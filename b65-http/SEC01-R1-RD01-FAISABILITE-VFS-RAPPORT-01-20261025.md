# ATLAS VOYAGEUR — SEC-01 R1-RD01 — Étude de faisabilité VFS SQLite
Date : 25 octobre 2026. Auteur fonctionnel : chat 01 — Développement et intégrations.
Nature : **analyse documentaire et lecture du dépôt uniquement** ; aucune VFS développée, aucune nouvelle injection, aucun test exécuté, aucune modification applicative.

## 1. Mandat, référence et base vérifiée
- Décision 00 : `b65-http/DECISION-00-SEC01-R1-RD01-FAISABILITE-VFS-20261025.md`.
- Branche : `feature/b6-5-cartographie-interactive`.
- HEAD constaté avant étude : `ff626b32981b091fedf6d8da28174c3aef1211de` (comparaison GitHub : identique).
- Sources du dépôt examinées : `b65-http/local_identity_bridge.py`, `b65-http/rd01_crash_bench.py`, `b65-http/SEC01-R1-RD01-RAPPORT-EXPERIMENTAL-01-20261025.md`.
- Acquis inchangé : 15/15 interruptions SIGKILL conformes aux cinq marques externes de CI n°90 ; aucune interruption interne au COMMIT démontrée.
- Réserves RD01-R01 à RD01-R04 ouvertes ; nouvelle expérimentation interdite sans arbitrage du 00.

## 2. Conclusion synthétique
**FAISABILITÉ CONDITIONNELLE ; GO recommandé uniquement pour une conception instrumentée isolée ultérieure, pas pour un développement immédiat.**
Une VFS enveloppant la VFS native permettrait théoriquement d'observer des appels SQLite pendant COMMIT, de produire une preuve d'entrée dans la couche VFS et de suspendre **un processus enfant de banc** au point demandé. Cela ne prouverait ni l'état des écritures dans un cache matériel ni une coupure d'alimentation. **Un SIGKILL sur temporisation n'est pas une preuve d'interruption interne.**

Le point de bascule d'une transaction multi-bases en mode rollback dépend notamment du **super-journal** : SQLite documente la suppression de ce fichier comme point de COMMIT multi-fichiers dans cette configuration. Sa création effective doit être observée, jamais présumée. L'ordre exact et l'existence des opérations dépendent de la version, de la VFS, des PRAGMA et des fichiers réellement modifiés.

## 3. Options comparées

| Option | Visibilité possible | Dépendances / impact | Force probatoire | Avis |
|---|---|---|---|---|
| A. Traçage OS externe (strace, tracepoints, eBPF selon droits) | appels système open/write/fsync/unlink du processus ; PID, fd, chemins rapprochés | outils et permissions de l'hôte, surcharge, traces possiblement incomplètes, association chemin-fd | bonne observation externe ; pas de point d'arrêt déterministe garanti entre événement SQLite et effet système ; fsync appelé ≠ persistance physique prouvée | utile pour recoupement, insuffisant seul |
| B. VFS « wrapper/shim » contrôlée | `xOpen`, type de fichier, `xWrite`, `xSync`, `xDelete`, `xFileControl`, verrous ; avant/après délégation | implémentation native C, gestion sqlite3_vfs/sqlite3_file/sqlite3_io_methods, enregistrement par processus, sécurité ABI et VFS parent ; instrumentation modifie l'ordonnancement | meilleure voie pour prouver l'entrée d'un appel VFS durant un COMMIT ; arrêt ciblé du processus enfant possible après preuve causale | **option prioritaire conditionnelle** |
| C. Moteur SQLite de test instrumenté (sources de même version, assertions/hooks internes) | étapes du moteur plus fines que les seules opérations OS | compilation particulière, déviation du SQLite embarqué dans Python, maintenance et justification d'équivalence | plus précis pour le point de contrôle interne, mais portabilité vers moteur non instrumenté à démontrer | alternative si B impossible ou insuffisante |

Une bibliothèque Python offrant une VFS personnalisable (ex. APSW) ne peut être retenue qu'après vérification des versions, licences, disponibilité et surtout de l'équivalence avec `sqlite3` du runtime. Pas de dépendance approuvée ni installée au titre de cette étude.

## 4. Événements internes ciblés et preuve d'atteinte
- `sqlite3_vfs.xOpen` : discriminer fichiers principaux, journaux rollback, fichiers temporaires et potentiels super-journaux ; capturer type/nom/handle quand disponibles.
- `sqlite3_io_methods.xWrite` : enregistrer entrée/sortie, cible, offset, taille, résultat ; une écriture peut concerner un journal ou une base et n'est pas synonyme de COMMIT.
- `xSync` : consigner entrée/sortie et indicateurs ; la réussite d'appel ne prouve pas la durabilité matérielle réelle.
- `sqlite3_vfs.xDelete` : événement critique potentiel pour la suppression du **super-journal**. Distinguer journal individuel et super-journal ; preuve du type et du chemin de fichier obligatoire.
- `xFileControl`, notamment `SQLITE_FCNTL_SYNC` et `SQLITE_FCNTL_COMMIT_PHASETWO` : signaux utiles selon VFS/version, **pas garantis présents dans tous les chemins** et non substituables à la suppression effective du super-journal.
- `xLock/xUnlock`, `xTruncate`, `xClose` : traces de contexte, récupération et finalisation.

**Proposition de preuve future, non exécutée :** chaque événement serait corrélé à un identifiant de transaction fictive, PID/TID, horloge monotone et numéro séquentiel ; preuve du type de fichier et résultat de l'appel ; marque écrite dans un canal indépendant des bases SQLite ; accusé de réception de la marque par un parent contrôleur ; suspension à barrière sur le *chemin VFS sélectionné* avant ou après délégation vers la VFS native ; seul le parent pourrait tuer **son propre enfant** et vérifier le statut de sortie. La preuve devrait distinguer « entrée dans xDelete » de « retour réussi de xDelete » : arrêter avant délégation ne teste pas la suppression elle-même ; tuer après retour de xDelete n'est plus un arrêt avant le point de validation. Il faudra accepter qu'une fenêtre interne puisse rester impraticable.

**Effet observateur :** temporisation, barrières, fsync des traces, changements du cache, allocation et verrous peuvent influer sur le comportement. Ne jamais écrire une trace de preuve dans les bases ni leurs journaux ; mesurer/documenter cette perturbation dans un protocole futur. Toute promesse d'équivalence avec le moteur natif doit être validée, pas simplement affirmée.

## 5. Durabilité : conditions et exclusions
Préqualifications nécessaires sur la future plateforme (non toutes vérifiées actuellement) :
- `sqlite3.sqlite_version`, `sqlite3.version`, `PRAGMA compile_options`, `PRAGMA database_list`, `PRAGMA journal_mode` et `PRAGMA synchronous` pour **chaque** base, version SQLite native liée à la VFS et version du Python test.
- Base principale stockée sur disque ; deux bases effectivement modifiées dans une seule transaction `ATTACH` ; modes rollback compatibles (pas WAL, MEMORY, OFF), synchronisation non désactivée et idéalement FULL ; même stockage local pertinent, identification du type de montage et du système de fichiers (pas seulement égalité de st_dev).
- Type du VFS hôte, comportement des appels sync et de répertoires ; fichiers temporaires et permissions ; pas de VFS « nolock » ou transformation cachée.
- Garanties réelles du matériel, cache de stockage et effet physique de `fsync` : **inconnues et non testées**. Ne pas extrapoler un SIGKILL à un crash noyau, à une coupure de courant ni à un autre hôte.
- SQLite indique qu'en transaction attachée un super-journal nécessite des conditions précises ; l'absence de super-journal doit être qualifiée comme arrêt de cette voie probatoire, pas comme preuve de fonctionnement.

## 6. Préservation des artefacts avant récupération (RD01-R03)
Méthode proposée pour un **banc futur uniquement**, non mise en œuvre :
1. Chaque essai dans un répertoire temporaire unique à données fictives ; manifeste préalable contenant commits GitHub, versions, paramètres, identifiants de scénario, type de panne, PID et séquence événementielle ; aucun secret.
2. Après la disparition **confirmée** du processus enfant, bloquer toute connexion SQLite, y compris les PRAGMA et l'inspection du banc, pour empêcher une récupération anticipée.
3. Inventorier puis conserver ensemble, de façon cohérente, **tous** les fichiers potentiellement pertinents : les deux `.sqlite`, leurs `-journal`, éventuel super-journal, et pour diagnostic les éventuels `-wal`/`-shm` (dont la présence signalerait une déviation à analyser), ainsi que traces VFS et marques.
4. Produire deux jeux : **instantané brut pré-récupération**, en lecture/copie de fichiers au niveau OS sans ouvrir SQLite, puis **copie de travail** isolée où seule la récupération est déclenchée. Exiger que toute copie respecte l'arrêt des écrivains et que journaux et bases conservent exactement leurs chemins relatifs nécessaires à SQLite.
5. Hacher chaque fichier avec SHA-256, taille, noms, identifiant de scénario ; conserver un manifeste avant et un manifeste après récupération, résultats de `PRAGMA integrity_check` par base et lectures métier AVANT/APRÈS/PARTIEL.
6. Publier uniquement des artefacts fictifs et nettoyés ; conserver les octets nécessaires au diagnostic et leur empreinte, jamais jetons, clés ni données personnelles ; contrôler les droits de diffusion et la durée de rétention GitHub Actions.

Le banc `rd01_crash_bench.py` actuel réouvre les bases par `inspect()` avant archivage, puis détruit les fichiers temporaires : ce comportement documenté est **insuffisant** pour RD01-R03 sans un autre protocole futur.

## 7. Faisabilité applicative : `LocalIdentityBridge._persistent_journey()` (RD01-R04)
**Constat vérifié dans GitHub :** la méthode utilise `state.connect()`, `ATTACH DATABASE ? AS identity_db`, `BEGIN IMMEDIATE`, contrôle `state._authorize()`, contrôle de jeton en base attachée, puis INSERT/SELECT/UPDATE/DELETE de `identity_db.identity_journeys`. La base principale est celle des sessions, la base attachée celle des identités. Le pont conserve son association fictive en mémoire ; le comportement de `LocalState` est un autre chemin.

**Raccordement envisagé seulement :** au lieu de modifier `_persistent_journey()`, exécuter une copie de banc du même parcours derrière une VFS enregistrée dans le processus enfant, et s'assurer que **les deux** ouvertures SQLite (principale et ATTACH) passent par ce VFS. Avec `sqlite3` Python standard, la sélection/registration de VFS native n'est pas directement exposée par une API de haut niveau : étude d'un petit wrapper natif ou runtime SQLite isolé nécessaire ; un changement d'URI `vfs=` doit être considéré comme une modification de banc à qualifier et ne suffit pas à établir son adoption par toutes les connexions. Vérifier également l'usage de la même bibliothèque SQLite entre composant VFS et module `sqlite3`, et le passage effectif des I/O attendues.

La vraie méthode existante ne fait pas simultanément `revoke()` et une mutation dans une seule transaction : le banc métier doit provoquer une opération `_persistent_journey()` sur identité fictive et qualifier son effet, **sans appeler cet essai une transaction identique à la transaction témoin**. La route HTTP et les créations/revalidations de sessions ne sont pas dans le périmètre de l'instrumentation future sans nouveau mandat. Aucun fichier applicatif modifié dans cette étude.

## 8. Conditions de GO/NO-GO ultérieur
**GO de conception instrumentée isolée seulement si :**
1. le 00 approuve séparément un design non intrusif, avec version SQLite et ABI connues ;
2. un point **pendant** une opération VFS correspondant au chemin COMMIT est ciblé de manière non ambiguë (type de fichier, événement d'entrée/sortie et lien transaction), et l'échec à atteindre une fenêtre est consigné ;
3. les deux bases et leurs journaux peuvent être préservés avant toute récupération ;
4. le protocole définit la preuve de l'événement interne, le contrôle de l'arrêt du seul enfant, les invariants et l'intégrité à comparer, et la gestion d'une absence de super-journal ;
5. l'impact de la VFS sur le moteur, les dépendances, l'environnement, les coûts de maintenance et les limites physiques sont acceptés.

**NO-GO / « non démontrable avec le banc retenu »** si le même moteur SQLite ne peut être utilisé, si les fichiers/journaux ne sont pas capturables, si le point interne n'est pas observablement relié au COMMIT, si l'interception altère le mode de journalisation, ou si une simple temporisation SIGKILL constitue l'unique preuve.

**Recommandation au 00 :** ne pas lancer d'instrumentation maintenant. Si le bénéfice d'une réduction de RD01-R01/R03 est jugé prioritaire, autoriser dans un second arbitrage une **phase de conception limitée** d'une VFS d'observation en processus enfant et du protocole d'archivage pré-récupération ; reporter toute campagne d'injection et toute intégration réelle à une autorisation distincte. Une VFS ne peut pas, par construction, qualifier les pannes physiques exclues.

## 9. Sources et niveau de vérification
**Dépôt consulté** : décision `DECISION-00-SEC01-R1-RD01-FAISABILITE-VFS-20261025.md`, `local_identity_bridge.py`, `rd01_crash_bench.py`, rapport de CI n°90. HEAD contrôlé sur GitHub. Aucun test nouveau exécuté.

**Documentation officielle SQLite consultée :**
- https://www.sqlite.org/vfs.html — VFS, registration et choix de VFS, interfaces.
- https://sqlite.org/c3ref/io_methods.html — appels `xWrite`, `xSync`, `xFileControl`.
- https://www.sqlite.org/c3ref/vfs.html — `xDelete`, `xOpen`.
- https://www.sqlite.org/atomiccommit.html — multi-fichiers, super-journal et point de COMMIT.
- https://www.sqlite.org/tempfiles.html — conditions de création du super-journal.
- https://www.sqlite.org/c3ref/c_fcntl_begin_atomic_write.html — signaux `SQLITE_FCNTL_SYNC`, `COMMIT_PHASETWO`.
- https://www.sqlite.org/testing.html — pratiques des bancs VFS de simulation de crash.

**Incertitudes vérifiables uniquement lors d'une autorisation ultérieure** : bibliothèque SQLite effectivement liée, compilation et ABI, choix VFS pour ATTACH, événements et noms de fichiers effectivement observés, possibilités de suspension d'un appel `xDelete`, identité du système de fichiers et performance d'archivage. Les capacités observables décrites sont des possibilités documentées, pas des observations instrumentées du dépôt.

**Statuts inchangés :** RD01-R01/R02/R03/R04 ouvertes, R1-RD01 ouverte, R1 et P0-01 ouverts, B6.5 en recette, B6.3 NO-GO, production NO-GO.

**Prochaine action unique proposée :** décision du 00 sur l'ouverture ou non d'une phase distincte de conception VFS et préservation des artefacts.
