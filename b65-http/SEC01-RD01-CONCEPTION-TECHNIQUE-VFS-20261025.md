# ATLAS VOYAGEUR — SEC-01 R1-RD01 — Conception technique VFS SQLite
**Version :** 1.0 — 25 octobre 2026  
**Nature :** spécification documentaire, **non implémentée, non compilée, non testée**.  
**Mandat :** `b65-http/DECISION-00-SEC01-RD01-CONCEPTION-VFS-20261025.md`.  
**Base GitHub examinée :** `b3770927cb0c08c7f6e807dcbbf6ec5520419e95`, branche `feature/b6-5-cartographie-interactive`.

## 1. Objet, périmètre et résultats existants

Concevoir, sans le réaliser, un banc VFS capable d'attribuer de façon causale une interruption **du seul processus enfant fictif** à une opération interne observable de SQLite pendant une transaction à deux bases attachées. L'instrumentation ne doit toucher ni les modules métier ni le site public. Le banc actuel `rd01_crash_bench.py` a démontré 15/15 récupérations cohérentes sur cinq marqueurs **externes** (CI n°90), pas une interruption interne au COMMIT. Les réserves RD01-R01 à RD01-R04 demeurent ouvertes.

**Frontière explicite :** VFS est une interface des appels entre SQLite et son environnement système, pas un point d'observation universel de toutes les fonctions internes du pager. Un appel VFS entrant n'atteste pas à lui seul l'achèvement de l'opération déléguée, sa durabilité physique ni le franchissement du point de COMMIT.

## 2. Architecture logique proposée — aucune réalisation

```text
Hôte de contrôle (aucune connexion SQLite avant archivage)
  ├─ Orchestrateur des scénarios et des préconditions
  ├─ Récepteur d'attestations hors SQLite + contrôleur PID
  ├─ Contrôle d'arrêt du seul processus enfant et attente de sa disparition
  ├─ Gardien « accès interdit » des données brutes jusqu'à la copie
  ├─ Inventaire, copie OS des bases et journaux, SHA-256, manifeste
  └─ Récupérateur sur COPIE DE TRAVAIL séparée, puis intégrité et invariants
           │ canal d'événements avec numéro séquentiel et acquittement
  Enfant fictif isolé
    ├─ Python / runtime SQLite à version et liaison attestées
    ├─ Connexion principale + ATTACH de la base d'identité fictive
    ├─ VFS d'observation enregistrée uniquement dans l'enfant
    │    ├─ enveloppe sqlite3_vfs (xOpen / xDelete / métadonnées)
    │    ├─ enveloppe sqlite3_file + sqlite3_io_methods
    │    │    ├─ xWrite / xSync / xFileControl / xTruncate
    │    │    └─ xLock / xUnlock / xClose et opérations auxiliaires
    │    └─ délégation vers VFS native, sans changement de résultat
    └─ transaction témoin OU chemin identités QA explicitement choisi
```

Les journaux d'attestation doivent être **hors de l'ensemble des fichiers SQLite étudiés** et ne doivent jamais contenir de cookies, CSRF, jetons ni identité réelle. La VFS n'est pas enregistrée globalement dans l'application existante ni destinée au public.

### 2.1 Interfaces et contrats envisagés

| Interface conceptuelle | Entrées | Sorties et obligation | Risque / condition d'arrêt |
|---|---|---|---|
| `VFSRegistration` | bibliothèque SQLite liée, nom VFS parent, nom de la VFS observatrice | identifiants/versions de la même instance SQLite ; résolution du VFS actif | NO-GO si double bibliothèque/ABI ambiguë |
| `FileRegistry` | `xOpen`, `flags`, chemin éventuellement absent, identifiant handle | rôle du fichier : main, base ATTACH, journal rollback, super-journal candidat, autre | NO-GO pour un déclenchement « super-journal » sans typage vérifiable |
| `EventObserver` | pré/post `xWrite/xSync/xDelete/xFileControl`, handle, offsets, taille, flags, codes retour | flux ordonné, non secret, numéros séquentiels, PID/TID | journalisation qui modifie le comportement ou provoque réentrance |
| `GateController` | scénario, événement sélectionné, phase `BEFORE_DELEGATE` ou `AFTER_RETURN` | attestation, acquittement du parent, enfant en attente ; le parent seul peut déclencher SIGKILL | échec si événement absent, horodatage seul ou absence d'acquittement |
| `EvidenceCustodian` | PID mort, répertoire isolé, inventaire des chemins | image brute **avant ouverture SQLite**, manifeste haché | NO-GO si fichier omis ou connexion active |
| `RecoveryVerifier` | copie de travail isolée | état AVANT/APRÈS/PARTIEL, integrity_check de chaque base, SQL métier | l'image brute demeure intacte |

**Exigences d'implémentation éventuelle, non autorisées ici :** conserver les versions, `szOsFile`, durée de vie des structures, `pMethods`, pointeurs de fichier internes, indicateurs `iVersion`, erreurs et options `xFileControl` ; transmettre fidèlement toutes les méthodes supportées vers le VFS parent (y compris méthodes de mémoire partagée si présentes). Ne pas supposer que toutes les méthodes de contrôle de fichier sont émises dans ce scénario. La sécurité des callbacks et la gestion des situations de concurrence doivent être spécifiées avant codage.

### 2.2 Compatibilité et choix des connexions

**Constat du dépôt :** `PersistentSessionState.connect()` utilise le `sqlite3.connect(self.path)` standard ; `LocalIdentityBridge._persistent_journey()` ouvre la base de sessions puis exécute `ATTACH DATABASE ? AS identity_db`, `BEGIN IMMEDIATE` et des opérations sur la base attachée.

**Question bloquante :** démontrer que la VFS de banc est enregistrée **dans l'instance SQLite réellement utilisée par le module `sqlite3` de Python**. Les pistes sont une enveloppe native chargée dans un processus enfant isolé utilisant la bibliothèque SQLite du module ou un runtime de banc distinct explicitement reconnu comme non équivalent. Aucun recours supposé à une API d'enregistrement VFS de haut niveau dans `sqlite3` standard. Une simple URI `vfs=` non vérifiée ne prouve pas la prise en charge de la base attachée.

**Critère de preuve d'activation future :** avant tout essai de panne, obtenir un inventaire exhaustif des fichiers ouverts montrant les opérations de la base principale, de la base `identity_db` et leurs journaux par la VFS observatrice, relier les ouvertures aux connexions et vérifier la version/ABI de la bibliothèque native. Sinon **NO-GO d'injection métier**. La reproduction avec un runtime SQL différent sera étiquetée « banc transactionnel » et ne pourra pas valider `_persistent_journey()`.

## 3. Événements observables et preuve causale

| Événement | Intérêt pendant transaction multi-fichiers | Attestation attendue | Ce qu'il ne prouve pas |
|---|---|---|---|
| `xOpen` | ouverture des bases, journaux, candidat super-journal | flags, nom, identité handle, type proposé puis confirmé | la participation au COMMIT |
| `xWrite` | écriture journal ou base | pré-délégation et retour, offset/taille/code | fsync ou durabilité |
| `xSync` | demande de synchronisation journal/base | flags, entrée et retour | flush matériel effectif |
| `xDelete` | suppression journal individuel ou éventuel super-journal | type exact du fichier, chemin, pré/post et résultat | « point de COMMIT » si c'est seulement un journal individuel |
| `xFileControl` | signaux auxiliaires selon SQLite et VFS | opcode, résultat et contexte | présence garantie ni équivalence avec xDelete |
| `xLock/xUnlock/xTruncate/xClose` | ordonnancement, finalisation et contexte | handle, transition, code retour | état de validation à eux seuls |

**Point important :** pour le schéma rollback multi-bases décrit par SQLite, la suppression du *super-journal* est le point logique déterminant du COMMIT. Le rôle d'un `xDelete` doit être prouvé par l'historique `xOpen`, les noms de fichiers et la transaction concernée ; **la simple observation d'un `xDelete` ne suffit pas**. Le super-journal n'est pas garanti dans tous les scénarios. Si son rôle ne peut être établi, verdict de cette fenêtre : **NON ATTEINTE / NON PROUVÉE**.

### 3.1 Contrôle d'arrêt futur — protocole conceptuel

1. Le parent établit un scénario unique et enregistre une identité de processus attendue ; le banc préqualifie le moteur, les PRAGMA et le stockage.
2. L'enfant ouvre les deux bases **via la VFS vérifiée** ; des marqueurs d'entrée/sortie VFS sont émis, avec séquence monotone et identifiants de handle. Le parent confirme que le marqueur provient du PID attendu et concerne le type de fichier ciblé.
3. La VFS suspend l'enfant **à l'intérieur du callback sélectionné**, à un endroit défini par `BEFORE_DELEGATE` ou `AFTER_RETURN`. L'attestation contient la phase et sa relation à l'appel natif. Le parent l'acquitte, puis seul le parent provoque l'arrêt **de cet enfant** ; le PID mort et le code de sortie sont consignés.
4. Si le marqueur sélectionné ne peut être atteint, si la suspension s'effectue après une séquence non déterministe ou si l'attestation n'est pas suffisamment discriminante, ne pas réinterpréter un timeout comme interruption interne.
5. L'événement « entrée dans `xDelete` avant délégation » est distinct de « `xDelete` terminé ». Une coupure après le retour peut avoir dépassé le point logique. La démonstration ne prétendra pas créer arbitrairement un état « au milieu de l'appel natif » si cet instant n'est pas observable.

**Causalité requise** : attestation complète du callback interne et de sa phase + suspension confirmée + correspondance PID/transaction + ordre de séquence + signal d'arrêt du parent et disparition de l'enfant. La mesure du seul temps écoulé ne satisfait pas cette exigence.

## 4. Neutralité de l'instrumentation et échec possible

Le wrapper ajouterait des callbacks, allocations, chemins d'erreur, verrous, concurrence, latence, IPC et éventuellement des écritures ou fsync du canal de preuve ; il peut transformer l'ordre des opérations et la surface de panne. Le protocole futur devra comparer l'empreinte des ouvertures, flags, `journal_mode`, `synchronous`, SQL et codes de retour **avec et sans instrumentation**, et documenter explicitement les écarts. Aucun essai comparatif n'est autorisé dans la phase actuelle.

Si une VFS requiert une SQLite de version différente, un changement en WAL, une modification du SQL métier ou le masquage d'une opération critique, le banc peut rester utile pour l'étude générale mais devient **NO-GO pour une conclusion sur le moteur Python actuel**.

## 5. Archivage brut avant récupération — RD01-R03

**Deux répertoires immuablement séparés :** `capture_brute/` et `recuperation_travail/`. Le parent doit confirmer la disparition de tous les écrivains, bloquer les ouvertures SQLite, inventorier les fichiers **par l'OS**, puis copier le groupe cohérent de la base principale, de la base attachée, des journaux rollback, de l'éventuel super-journal, des fichiers connexes éventuels (`-wal/-shm` conservés comme indice de déviation), des marques VFS et de la configuration.

| Artefact conceptuel | Champs exigés |
|---|---|
| `manifest-before.json` | ID essai, décision/commit, OS, Python, SQLite et compilation, VFS, PRAGMA, chemins relatifs, PID, événement, phase pré/post, heure, version protocole, SHA-256 et taille par fichier |
| `vfs-events.jsonl` | séquence, PID/TID, connexion/handle, type fichier, événement, offset/flags, phase, code retour, événement de barrière et accusé de réception |
| `manifest-raw.json` | fichiers bruts, emplacement et empreintes SHA-256, statut « aucune ouverture SQLite préalable », notes sur fichiers manquants |
| `manifest-recovery.json` | empreintes de copie de travail, méthode de copie, invariants AVANT/APRÈS/PARTIEL, PRAGMA integrity_check sur chaque base, journaux de récupération |
| `environment.json` | kernel/OS, système de fichiers/montage, même périphérique, versions et options SQLite, modes journaux, sync, limite du stockage et des garanties physiques |

**Ordre obligatoire :** mort confirmée de l'enfant → aucun accès SQLite → copie brute cohérente des bases et de tous journaux → SHA-256 et manifeste → duplication pour récupération → ouverture SQLite **uniquement de la copie** → état et intégrité. Ne pas modifier, nettoyer, checkpoint ni rejouer les journaux avant leur copie. Préserver noms relatifs et relations de fichiers du super-journal. Une liste de fichiers partielle doit invalider la conclusion « récupération qualifiée ».

La conservation versionnée ou comme artefact GitHub Actions est une **proposition future**, non déployée. Durée de rétention, confidentialité, contrôles d'accès, vérification d'empreintes après téléchargement et absence de secrets sont des prérequis. Le banc actuel supprime ses répertoires temporaires après ouverture/inspection SQLite et ne remplit donc pas encore ce contrat.

## 6. Deux scénarios distincts à ne pas confondre

| Scénario | Transactions | Valeur de preuve | Limite |
|---|---|---|---|
| **T — Témoin contrôlé** | `BEGIN IMMEDIATE`, mutation session A + insertion parcours B fictif, `COMMIT` | observer super-journal et récupérer un état AVANT/APRÈS associé à deux écritures | pas le chemin métier existant |
| **M — Chemin applicatif** | `LocalIdentityBridge._persistent_journey()` : validation de session sur base principale, validation de l'identité dans base attachée, modification `identity_journeys`, quota éventuel dans base principale | vérifier que les deux bases sont effectivement impliquées, avec événements VFS sur les deux | `LocalState` en mémoire et fournisseur réel exclus ; ne pas modifier la méthode |

**Point à prouver pour M :** l'appel `state._authorize()` peut écrire dans `request_events` et la mutation d'identité peut écrire dans `identity_db.identity_journeys`. La qualification devra prouver l'existence des deux écritures dans la *même* transaction et la couverture VFS complète. En cas de quota bloquant, de session expirée ou d'opération refusée, ne pas attribuer l'absence de super-journal à un défaut de SQLite : le scénario pourrait n'avoir écrit qu'une base ou aucune. Le choix de fixtures devra garantir l'opération métier autorisée sans inclure de données réelles.

## 7. Préqualification d'environnement et dépendances (non installées)

- Linux dans processus enfant sur répertoire temporaire contrôlé, même système de fichiers local cohérent pour les deux bases ; vérifier montage/type de FS, `st_dev`, règles de verrouillage, VFS mère et présence des fichiers réels.
- Python et bibliothèque SQLite effectives attestées (`sqlite3.sqlite_version`, chemin et ABI de la bibliothèque, compilation, `PRAGMA compile_options`, `PRAGMA database_list`). La disponibilité des interfaces natives pour enregistrer une VFS depuis le même runtime est **INCONNUE** à cette date ; toute bibliothèque alternative nécessiterait une décision.
- `journal_mode=DELETE` et `synchronous=FULL` constatés pour **les deux bases**, base principale sur disque, ATTACH effectif. WAL/MEMORY/OFF, stockage distant, chiffrement tiers et plusieurs hôtes hors du cadre de démonstration.
- Les appels de synchronisation vers l'OS ne garantissent pas la persistance physique ; crash OS, panne noyau, perte de courant, matériel défaillant ou caches trompeurs sont exclus.

## 8. Matrice de décision GO / NO-GO pour un futur prototype

| Porte | Condition nécessaire avant réalisation | Échec / décision |
|---|---|---|
| G01 — Même moteur | bibliothèque SQLite effective et ABI VFS du Python cible identifiables, sans substitution silencieuse | NO-GO ciblage applicatif |
| G02 — Couverture des deux bases | toutes les ouvertures/journaux observables par la même VFS ; preuve propre aux connexions principale et ATTACH | NO-GO pour M |
| G03 — COMMIT interne | appel interne distingué du délai externe, super-journal typé ou alternative clairement justifiée | NON DÉMONTRABLE si aucun point exploitable |
| G04 — Arrêt causal | attestation interne, suspension confirmée, PID et phase, arrêt du seul enfant contrôlé | NO-GO d'injection |
| G05 — Conservation | fichiers bruts complets et hachables avant ouverture par SQLite ; journaux préservés | NO-GO récupération qualifiée |
| G06 — Neutralité | journalisation, sync, codes retour et SQL non altérés de manière invalidante | NO-GO d'équivalence |
| G07 — Sécurité et responsabilité | sandbox locale fictive, aucune donnée réelle, aucun secret, aucun droit hôte destructeur | NO-GO expérimental |
| G08 — Réception | critères documentés, preuves reproductibles et contrôle indépendant 03 | aucun GO sécurité sans 03 puis 00 |

**Coûts/complexité qualitatifs :** wrapper VFS C et gestion des versions/ABI : élevés ; instrumentation et preuve causale : élevées ; archivage des journaux et récupération sans altération : moyens à élevés ; maintenance multi-environnements : élevée ; seul traçage OS plus simple mais force probatoire moindre. Aucun prix, délai ni charge chiffrée ne sont établis.

**Recommandation technique : GO conditionnel vers un prototype isolé uniquement si les portes G01, G02 et G05 peuvent être vérifiées à faible intrusion et si le 00 juge la valeur probatoire suffisante ; sinon NO-GO.** Une première autorisation d'implémentation, une éventuelle campagne d'injection et une réception du chat 03 constitueraient des décisions **distinctes**. Aucune autorisation n'est présumée.

## 9. Sources et vérifications

**Constaté dans GitHub au départ :** HEAD `b3770927cb0c08c7f6e807dcbbf6ec5520419e95`, décision officielle, rapport de faisabilité, `local_identity_bridge.py`, `persistent_sessions.py`.  
**Sources SQLite officielles pour l'architecture proposée :**
- https://www.sqlite.org/vfs.html
- https://www.sqlite.org/c3ref/vfs.html
- https://www.sqlite.org/c3ref/io_methods.html
- https://www.sqlite.org/atomiccommit.html
- https://www.sqlite.org/tempfiles.html

Les interfaces VFS et le déroulement théorique du COMMIT sont documentés par SQLite ; leur présence, ordre et interception dans **le runtime du projet** ne sont pas expérimentalement vérifiés. Ce document ne constitue aucune validation de prototype.

## 10. Continuité et statuts

**Aucune modification applicative, aucune VFS développée/compilée, aucune dépendance installée, aucun test ou SIGKILL exécuté pour cette conception.** La CI n°90 et les 15 essais antérieurs ne sont pas rejoués ni attribués à ce document.

**RD01-R01 à R04 ouvertes ; R1-RD01 ouverte ; R1-C01 partiel ; R1 ouverte ; P0-01 ouvert ; B6.5 en recette ; B6.3 NO-GO ; production NO-GO.**

**Prochaine action unique :** soumettre ce dossier au chat 00 pour arbitrage explicite du GO/NO-GO d'un éventuel prototype VFS isolé, sans autorisation implicite d'essais.
