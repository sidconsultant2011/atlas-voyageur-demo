# SEC-01 R1-RD01 — G03-R01 — Contrat documentaire d'attestation causale
**Date :** 25 octobre 2026. **Nature :** exigences et conception sans réalisation.  
**Mandat :** `b65-http/DECISION-00-SEC01-RD01-G03-R01-ETUDE-CAUSALE-20261025.md`.  
**Référence de départ vérifiée sur GitHub :** `3114d83daf4004dd866eca916fbf4f74eda0d6a5`, branche `feature/b6-5-cartographie-interactive`.  
**Restrictions respectées :** aucun changement C/Python/applicatif ou workflow, aucun test, aucune compilation, aucun SIGKILL, aucun G04.

## 1. Objectif et limite de preuve

**Exigence G03-R01 :** définir une attestation *causale*, vérifiable par un tiers, du passage d'une transaction SQLite `ATTACH` multi-fichiers par un appel VFS qui participe à la validation du COMMIT. Cette définition ne présume ni l'existence, ni l'atteignabilité, ni l'innocuité d'un éventuel futur point d'interception.

La documentation SQLite décrit, **dans le profil rollback multi-fichiers où un super-journal est effectivement utilisé**, la **suppression du super-journal** comme point logique de COMMIT. Il faut distinguer :
- l'entrée dans `sqlite3_vfs.xDelete` avant toute délégation ;
- le retour de `xDelete` de la VFS mère avec résultat `SQLITE_OK` ;
- l'achèvement logique du mécanisme SQLite, lequel repose sur ses hypothèses de système de fichiers ;
- la durabilité physique, **non déductible** du seul retour `xDelete`, `xSync`, ni de journaux applicatifs.

Un `xDelete` sur un journal de base individuelle n'est pas une preuve du point logique multi-fichiers. Un nom de fichier semblable au super-journal n'en prouve pas à lui seul l'identité. En cas d'absence de super-journal ou d'ambiguïté, le contrat rend le résultat **NON ATTEINT / NON DÉMONTRÉ**, sans substitution de temporisation ou de marque Python.

## 2. Acquis réellement constatés et manques

Sources consultées : `atlas_rd01_vfs.c`, `g03_trace_analysis.py`, `SEC01-RD01-CONCEPTION-TECHNIQUE-VFS-20261025.md`, `SEC01-RD01-G03-PREPARATION-PREUVES-20261025.md` et décision 00 actuelle.

| Élément | Fait acquis | Absence de preuve / limite |
|---|---|---|
| Environnement banc N/W | Linux CI et SQLite Python 3.45.1 ; scénario ATTACH/DELETE/FULL avec COMMIT/ROLLBACK normal, contention contrôlée, reçu dans sa portée (CI n°135 au commit `fc6eded13fa15b8776b12dd0cd494349d0a2e906`) | pas une équivalence générale ni une exécution de `_persistent_journey()` |
| Fichier candidat super-journal | `role()` détecte le drapeau `SQLITE_OPEN_MASTER_JOURNAL` dans `xOpen` | aucun registre fiable de chemins canoniques, handles et transaction |
| Suppression corrélée | exemple CI n°116 : `xOpen` séquence 80, `xDelete` réussi séquence 116, rapprochés sur basename | ce rapprochement est post-délégation et peut être ambigu ; la version exacte d'une trace n'est pas une identité transactionnelle |
| Chaîne d'événements | `emit()` écrit séquence globale, PID, événement, rôle, rc, flags, basename dans un TSV | pas de marque d'ENTRÉE, TID, ID de transaction, chemin canonique ni identifiant de handle ; `serial` global non protégé |
| Conservation | archives G05 propres et SHA-256 ont déjà été publiées lors de la CI n°108 | pas d'attestation individuelle synchronisée ni d'archive après incident avec journaux chauds |
| Neutralité | délégation V1 présente ; effets fonctionnels N/W déjà comparés | `sqlite3_io_methods` V1 réduit l'interface native potentielle ; ordre/latence/I/O native non prouvés |

**Ne pas refaire** la qualification normale N/W : elle est la référence préparatoire, non l'objet du présent contrat.

## 3. Identités : contrat d'association sans ambiguïté

Un futur enregistrement de preuve **devrait** transporter les champs suivants. Ils sont des **exigences non implémentées**, pas des propriétés du TSV actuel.

| Champ obligatoire proposé | Fonction / condition de vérification |
|---|---|
| `protocol_version`, `run_id`, `case_id` | rattacher chaque preuve à une exécution fictive, au commit et à la configuration, sans collision |
| `engine_id`, `vfs_parent_id`, `vfs_wrapper_id` | prouver le même moteur / ABI et la couverture de la VFS réellement utilisée |
| `pid`, `tid`, `connection_id` et `transaction_id` | relier un callback à **une transaction** et à un participant sans utiliser un timestamp comme substitut |
| `db_alias`, `file_id`, `file_role`, `open_flags`, `canonical_path` | typer la base principale, la base ATTACH, leurs journaux et le super-journal ; conserver l'identité même après fermeture |
| `event_seq`, `callback_name`, `invocation_id` | assurer la relation un-à-un entre entrée et sortie d'un même appel, et l'ordre observé |
| `phase` | valeurs `BEFORE_DELEGATE` / `AFTER_RETURN` distinctes, explicitement enregistrées |
| `arguments`, `parent_return_code`, `result_class` | enregistrer flags et retours pertinents sans données personnelles ou secrets |
| `record_receipt_id`, `proof_channel_state` | établir ce qui a été effectivement reçu et conservé hors des bases SQLite |
| `configuration_hash`, `evidence_sha256` | détecter divergence de paramètres et altération des archives après collecte |

**Difficulté structurante :** l'API VFS ne transmet pas d'identifiant SQL de transaction à chaque `xDelete`. `xDelete` est une méthode `sqlite3_vfs` portant sur un chemin, sans `sqlite3_file` associé. Le lien entre une suppression et le handle/transaction doit donc être **démontré par une table d'identité contrôlée** (ou mécanisme équivalent prouvé) sans réentrance dans SQLite. Un ID « ajouté au hasard » ou inféré par nom seul n'est pas recevable. Les adresses de pointeurs ne sont pas des identifiants durables entre exécutions.

**Exigence de cardinalité :** une attestation candidate doit montrer exactement un ensemble de bases participantes, leurs journaux, l'association explicite au super-journal et **une** opération de suppression ciblée ; les transactions concurrentes et les homonymes doivent être discriminés. Les chemins canoniques sont à conserver sans fuite de répertoires sensibles : uniquement le banc fictif isolé.

## 4. Modèle proposé de cycle d'attestation

Schéma logique seulement, **aucun callback nouveau n'est créé** :

```text
Transaction fictive identifiée, deux bases réellement modifiées
        |
Registre de fichiers vérifié : DB A / DB B / journaux / super-journal
        |
xDelete(super-journal) : BEFORE_DELEGATE [invocation_id=K]
        |     `entrée prouvée` ≠ `suppression effectuée`
Délégation à la VFS native (sans changer ses arguments)
        |
xDelete(super-journal) : AFTER_RETURN [même invocation_id=K, résultat]
        |     succès VFS ≠ durabilité physique
Réception vérifiable de la trace hors SQLite et archive avec SHA-256
```

Le contrat interdit d'appeler « avant COMMIT » une marque Python située avant `db.commit()`, et d'appeler « dans COMMIT » une simple trace émise après retour de la fonction SQL. Un événement interne recevable est un **callback effectivement entré** avec phase et provenance prouvées. Une marque `AFTER_RETURN` seule reste une preuve de retour, pas d'entrée opposable à une future interruption.

Une **preuve de causalité d'arrêt G04** requerrait en plus un protocole distinct de barrière et arrêt borné. Elle n'est **ni spécifiée comme implémentation ni autorisée** ici. La valeur du contrat G03 est uniquement de dire si l'appel interne cible peut être identifié et attesté sans ambiguïté.

## 5. Chaîne de conservation proposée

1. Avant scénario : figer manifeste de versions Python / SQLite / VFS native et observatrice, PRAGMA des deux bases, mode rollback-DELETE, support, commit, fixture et identités de fichiers.
2. Pendant un COMMIT **normal futur seulement si autorisé** : produire le journal probatoire dans un canal distinct, avec numéros de séquence, couples `BEFORE_DELEGATE` et `AFTER_RETURN`, identifiant d'appel, retour et références aux fichiers.
3. Distinguer **émis**, **reçu**, **acquitté**, **stocké** et **synchronisé**. Le succès de `write()` n'est pas une garantie de persistance ; un `fsync()` réussi ne prouve pas le matériel. Un acquittement ne doit affirmer que le niveau réellement atteint.
4. Préserver les artefacts et empreintes SHA-256, vérifier les archives après téléchargement. Garder `capture_brute` séparé de `recuperation_travail` ; éviter tout accès SQLite aux fichiers bruts avant leur copie **si un protocole d'arrêt est ultérieurement autorisé**.
5. Exiger que les traces de preuve ne soient pas dans les bases ni dans leurs journaux et qu'elles ne contiennent aucune clé, jeton, identité réelle ni donnée sensible.

Aucun journal chaud n'est produit au titre de cette étude, et aucune garantie de survie à une panne n'est acquise.

## 6. Neutralité : garde-fous sur la référence N/W

- Ne pas remplacer la bibliothèque SQLite du Python cible ; contrôler version effective, symbole et ABI avant toute conclusion.
- Ne pas masquer les fonctions natives nécessaires à rollback-DELETE ni changer les valeurs `journal_mode=DELETE`, `synchronous=FULL`, les verrous, les codes de retour et les SQL.
- Les méthodes I/O du wrapper sont V1 ; la disponibilité et la compatibilité V2/V3 ne sont **pas** démontrées, comme déjà noté sous VFS-R01 / G03-R06.
- Toute émission avant délégation allonge le chemin critique et peut affecter ordonnancement, contention ou erreurs. L'ajout d'un `fsync` de preuve peut modifier les coûts de synchronisation sans améliorer la sûreté SQLite. Une mesure de parité limitée et falsifiable serait nécessaire **après autorisation distincte**.
- Les traces doivent être non réentrantes, sûres en concurrence, à mémoire et délai bornés, avec politique d'échec explicitée. Si l'observateur bloque ou provoque une erreur SQLite, l'exécution ne peut pas être présentée comme « neutre ».
- Respecter l'état de référence reçu : COMMIT/ROLLBACK normaux et `SQLITE_BUSY` sous contention ; aucune prétention de neutralité temporelle ou physique.

## 7. Matrice de recevabilité future — falsifiable

| Porte | Critère GO d'une future réalisation **isolée** | Critère NO-GO / non démontré |
|---|---|---|
| C01 — Moteur | même instance de bibliothèque / ABI et VFS activée sur les deux bases | bibliothèque différente ou méthode essentielle manquante |
| C02 — Participants | lien prouvé entre transaction, deux mutations, fichiers et journaux | une base non modifiée ou participant non identifié |
| C03 — Super-journal | rôle et identité du super-journal prouvés indépendamment du seul basename | `xDelete` générique, ambiguïté ou super-journal absent |
| C04 — Phase du callback | paires entrée/sortie vérifiables par `invocation_id` et retour de la VFS native | uniquement trace après délégation ou timestamps |
| C05 — Ordre et provenance | séquences sans doublon, PID/TID, identifiant transactionnel non ambigu, concurrence maîtrisée | corrélation reconstituée sans preuve ou collision |
| C06 — Conservation | état reçu/synchronisé honnêtement qualifié, archive vérifiable et non altérée | marque émise assimilée abusivement à marque persistée |
| C07 — Neutralité | résultats SQL, règles de verrou, journalisation et synchronisation configurée préservés sous contrôle comparatif autorisé | divergence inexpliquée ou surface VFS dégradée pertinente |
| C08 — Limites | absence d'arrêt/panne et portée du moteur inscrites dans la conclusion | COMMIT normal présenté comme garantie de reprise ou de production |

**Verdict documentaire proposé :** le contrat d'attestation est **définissable**, mais sa satisfaisabilité dans le wrapper actuel n'est **pas démontrée**. En particulier les champs `transaction_id`, chemins canoniques, identifiants de fichiers, couples pré/post et preuve de réception durable n'existent pas dans le journal actuel. Ces manques ne sont pas des échecs de tests : ils n'ont pas été implémentés ni qualifiés.

### Condition bloquante prioritaire unique à arbitrer au 00

**Prouver la liaison non ambiguë `transaction multi-bases → super-journal identifié → invocation xDelete` avec la phase `BEFORE_DELEGATE` vérifiable, sans changer la sémantique de la transaction ni dégrader les acquis N/W.**

Sans cette liaison démontrable, toute instrumentation causale serait **NO-GO**, même en présence de marqueurs temporels, d'une suppression de fichier réussie ou d'une trace post-retour. Si une étude ultérieure juge ce lien impossible dans la VFS sans altérer SQLite, recommander un NO-GO motivé plutôt qu'une multiplication d'essais.

## 8. Références, limites et gouvernance

- Décision 00 : `b65-http/DECISION-00-SEC01-RD01-G03-R01-ETUDE-CAUSALE-20261025.md`.
- Conception VFS : `b65-http/SEC01-RD01-CONCEPTION-TECHNIQUE-VFS-20261025.md` (proposition antérieure, à ne pas confondre avec implémentation).
- Préparation G03 : `b65-http/SEC01-RD01-G03-PREPARATION-PREUVES-20261025.md` et `b65-http/rd01-vfs-step1/g03_trace_analysis.py`.
- Code source wrapper : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`.
- Base de qualification N/W reçue : CI n°135 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980, sur `fc6eded13fa15b8776b12dd0cd494349d0a2e906`. **Aucune nouvelle CI n'est revendiquée.**
- SQLite : https://www.sqlite.org/atomiccommit.html ; https://www.sqlite.org/c3ref/io_methods.html ; https://www.sqlite.org/c3ref/vfs.html.

**Statuts inchangés :** G03-R01 OUVERTE ; G03 préparatoire reçu avec réserves ; VFS-R01 et G03-R06 OUVERTE ; G04 NO-GO ; G05 global PARTIEL ; R1-RD01, R1 et P0-01 OUVERTS ; B6.5 EN RECETTE ; B6.3 NO-GO ; production NO-GO.

**Prochaine action unique :** soumettre le contrat documentaire au chat 00 pour avis du chat 02 et arbitrage explicite de la faisabilité d'une éventuelle instrumentation probatoire isolée, sans autorisation implicite de développement.
