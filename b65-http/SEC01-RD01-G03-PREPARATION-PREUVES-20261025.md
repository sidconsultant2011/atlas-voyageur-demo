# SEC-01 R1-RD01 — Dossier probatoire de préparation G03 — chat 01
**Date :** 25 octobre 2026. **Statut :** préparation G03 seulement, sans interruption.
**Décision 00 :** `b65-http/DECISION-00-SEC01-RD01-G03-PREPARATION-20261025.md`.  
**Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD initial vérifié :** `76e7dbc3c7541852ab9c9ab6282f13ef4f5a4d44`.

## 1. Modifications, portée et interdictions respectées
- Ajout de `b65-http/rd01-vfs-step1/g03_trace_analysis.py` (commit `66ed0e23fee9c01bd4f3d023764e49ba83c69283`) : vérification des champs TSV, de la monotonie des numéros de séquence, identification des fichiers `xOpen` marqués `super-journal-candidate` par le flag SQLite, puis rapprochement avec `xDelete` de même basename dans une séquence ultérieure et son code retour.
- Adaptation **du banc seul** `rd01_vfs_step1.py` (commit `74db8717c8928e109e774e8911acc5746b28241c`) : exécution de l'analyse sur la trace d'une transaction multi-bases fictive **COMMIT normal**, inclusion de la preuve dans `proof.json` conservé par G05.
- Adaptation du test existant (commit `86de3e07621c68b4e24e80e94f12982e2cd7c621`) : contrôle de la présence des deux ouvertures, exclusion explicite des assertions de durabilité et de phase interne ; impression du résultat `RD01 G03 NORMAL COMMIT TRACE` dans le journal CI.
- **Aucun changement au wrapper C `atlas_rd01_vfs.c`** : risque d'observateur non aggravé par les callbacks natifs existants. Aucun changement à `local_identity_bridge.py`, `persistent_sessions.py`, au workflow ni à l'application.
- Aucun SIGKILL, arrêt causal, suspension, faute injectée, essai de crash ou substitution moteur ; aucune nouvelle dépendance.

## 2. Exécution vérifiée
- **CI n°116 :** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40207400841
- Commit testé : `86de3e07621c68b4e24e80e94f12982e2cd7c621`. Conclusion GitHub : `completed / success`.
- JavaScript : **116/116** ; SQLite hors ligne : **11/11** ; HTTP/identité et banc : **96/96** ; soit **223 exécutions réussies**, pas nécessairement 223 scénarios différents.
- Test ajouté sur ce chantier : **analyse du COMMIT normal** intégrée au test existant, pas de campagne de panne.
- **Tests locaux du commit final : non exécutés ici.** Les résultats du commit final proviennent des journaux CI.

### 2.1 Attestation extraite du journal de CI n°116
- PID distincts observés dans cette trace : **1**.
- Événements enregistrés : **128** ; `xOpen=8`, `xWrite=60`, `xSync=16`, `xDelete=6`, `xFileControl=31`, `xClose=6`, `registered=1`.
- Un `xOpen` portant le rôle `super-journal-candidate` et code 0 à la séquence **80**, pour `sessions.sqlite-mj0E9BEA920`.
- Un `xDelete` de même basename, avec code de retour **0**, à la séquence **116**.
- Les ouvertures des bases fictives `sessions.sqlite` et `identities.sqlite` sont observées.
- `observations.candidate_open_observed=true` ; `candidate_delete_observed=true` ; `two_databases=true`.
- `commit_internal_phase_proven=false` ; `before_after_delegate_proven=false` ; `transaction_id_proven=false` ; `durability_proven=false`.

**Lecture correcte :** cette exécution fournit une corrélation de nom/ordre et un retour réussi d'une opération VFS du COMMIT normal. Elle ne constitue pas l'attestation causale complète attendue avant une expérimentation G04. Le nom de super-journal est aléatoire et changera aux autres exécutions. La suppression réussie est enregistrée **après délégation** au parent VFS.

## 3. Audit de neutralité et de compatibilité G06
Lecture du wrapper C présent sur la branche :
- `sqlite3_io_methods io={1,...}` expose uniquement **la version 1** ; fonctions de mémoire partagée `xShmMap/xShmLock/xShmBarrier/xShmUnmap` (V2) et `xFetch/xUnfetch` (V3) ne sont pas déléguées. Le wrapper `sqlite3_vfs` déclare `iVersion=2`. Ce décalage n'est **pas en soi une défaillance** dans le banc rollback-DELETE, mais **empêche d'affirmer une équivalence générale** avec la VFS native.
- `emit()` s'exécute **après** la délégation `xWrite`, `xSync`, `xDelete`, `xFileControl` et `xOpen`. L'ordre de trace représente un ordre de retours enregistrés, non la preuve des moments d'entrée dans les appels natifs.
- La trace utilise `write()` dans un descripteur distinct, **sans `fsync` individuel**, et conserve le **basename**, pas le chemin canonique ou l'identité du handle. Une collision de nom ou une perte de données après crash reste concevable ; non testée.
- `serial` est global sans protection de concurrence ; il est vérifié monotone dans cette campagne mono-processus, pas garanti de façon générale multi-thread.
- `xFileControl` est transmis au parent et son opcode enregistré ; le rapport actuel ne prouve pas que les opcodes correspondent précisément à une phase donnée du COMMIT.
- Le traçage I/O, la VFS V1 et le chargement natif peuvent modifier la latence, la surface de fonctionnalités et le planning du moteur ; aucune comparaison exhaustive avec et sans VFS n'a été exécutée.
**Verdict G06 : réserve de neutralité OUVERTE.** Aucun argument ne permet de conclure à une équivalence complète ni de généraliser au mécanisme WAL ou au moteur d'autres plateformes.

## 4. Matrice G03 — valeurs probatoires exactes
| Élément | Statut technique | Motif |
|---|---|---|
| Ouverture réelle des deux bases fictives | **ATTEINT** | événements `xOpen`, noms distincts |
| `xOpen` super-journal candidat | **ATTEINT** | flag d'ouverture + code 0 |
| `xDelete` sur même basename plus tard | **ATTEINT** | séquences 80 et 116, retour 0 |
| Suppression assimilable au point logique COMMIT sous conditions SQLite | **OBSERVABLE SOUS CONDITIONS** | documentation SQLite pour rollback multi-bases ; identité exacte du super-journal à relier sans ambiguïté |
| Identification complète pré/post-délégation et rôle exact des fichiers | **NON DÉMONTRÉ** | callbacks enregistrés uniquement au retour, noms tronqués |
| Identifiant explicite de transaction et horodatage causal | **NON DÉMONTRÉ** | aucun ID de transaction dans les événements |
| Archivage d'attestation synchronisée individuellement | **NON DÉMONTRÉ** | pas de `fsync` par événement ; G05 conserve néanmoins la trace d'un COMMIT normal |
| Arrêt causal pendant COMMIT / G04 | **NON EXPLOITABLE DANS CE MANDAT** | interdit, aucune suspension ni panne |
| Durabilité et reprise après coupure | **NON DÉMONTRÉ** | aucune panne ; aucune preuve physique |

### Schéma de preuve future proposé, **non réalisé**
Émettre un événement lié à un **chemin canonique + identifiant de handle + ID de transaction fictive**, codes SQLite et flags, séquence validée, PID/TID, `BEFORE_DELEGATE` et `AFTER_RETURN`, dans un canal séparé des bases, avec propriété d'acquittement vérifiable ; conserver ces preuves via le mécanisme G05 avant toute récupération. La définition d'une barrière causale et d'un arrêt par le parent reste un **document de conception exclusivement**, requérant nouvelle décision 00.

## 5. Raccordement futur au chemin métier — documentaire seulement
Dans le code vérifié, `LocalIdentityBridge._persistent_journey()` obtient `state.connect()` sur la base sessions, exécute `ATTACH DATABASE ? AS identity_db`, puis `BEGIN IMMEDIATE`. Elle appelle `state._authorize()` susceptible de modifier `request_events` dans la base principale, puis des mutations `identity_db.identity_journeys` dans la base attachée si les droits l'autorisent.

Pour une preuve ultérieure, il faudrait attester que **les deux bases sont réellement écrites** sous la même transaction, que les opérations et journaux sont visibles par le wrapper et que le moteur reste identique. Une session expirée, un refus de quota ou un accès refusé peut supprimer une partie des écritures. **Aucun appel à cette méthode métier n'a été effectué pour G03** ; aucune inférence d'équivalence depuis le banc ne suffit.

## 6. Recommandation au 00 et limites de reprise
**GO de préparation probatoire obtenu ; NO-GO de G04 dans l'état.** Il est techniquement pertinent de définir un instrument futur permettant typage exact des fichiers, émission pré/post, identifiant transactionnel et neutralité VFS mesurée **avant** toute expérimentation causale. Faute de tels signaux, il serait incorrect de confondre un marqueur Python ou un `xDelete` post-retour avec un arrêt « au milieu du COMMIT ».

Aucune réserve P0 automatiquement levée. G01 recevable sur CI ciblée ; G02 recevable sur banc fictif ; conservation documentaire G05 clôturée par 00, **G05 globale partielle** pour la récupération post-panne. G03 préparatoire non qualifiée comme preuve d'arrêt ; G04 NON AUTORISÉE. VFS-R01 à R05 et RD01-R01 à R04 restent ouvertes ; R1-RD01, R1, P0-01 ouverts ; B6.5 en recette, B6.3 NO-GO, production NO-GO.

### Références
- Décision 00 : `DECISION-00-SEC01-RD01-G03-PREPARATION-20261025.md`.
- SQLite : https://www.sqlite.org/atomiccommit.html (super-journal et suppression logique), https://www.sqlite.org/tempfiles.html (rôle du super-journal), https://www.sqlite.org/c3ref/io_methods.html (versions V1/V2/V3).
- GitHub Actions n°116 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40207400841

**Prochaine action unique proposée :** soumettre le présent rapport au chat 00 pour l'arbitrage de la prochaine étape technique ; ne pas engager G04.
