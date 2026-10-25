# SEC-01 R1-RD01 — G03-R01-C03-3 — Verdict final documentaire : collecte passive des références croisées

**Date :** 25 octobre 2026  
**Type :** dernière étude documentaire ciblée, sans mise en œuvre ni nouvel essai  
**Mandat du 00 :** `b65-http/DECISION-00-SEC01-RD01-C03-3-COLLECTE-PASSIVE-20261025.md`  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD initial vérifié :** `eb33cd89d8a0593c7041b10a399053ed4803285b`

## 1. Verdict final exploitable

**GO CONDITIONNEL DE FAISABILITÉ, limité à la possibilité technique d'une future collecte passive dans un banc isolé ; NO-GO DE RÉALISATION IMMÉDIATE.**

**Pourquoi ce verdict ?** Dans le profil rollback multi-fichiers documenté par SQLite, les références sont réciproques : le super-journal **S** liste les journaux rollback participants **A et B**, tandis que chaque journal **A/B** porte une référence à **S**. La VFS reçoit, dans `sqlite3_io_methods.xWrite`, les octets à écrire, leur longueur et leur offset. En principe, un observateur *non réentrant* placé sur ce passage pourrait assembler les **écritures logiques autorisées**, même fragmentées, et rechercher les références documentées **sans ouvrir à chaud les fichiers**.

Ce n'est **pas** une possibilité déjà démontrée dans le projet. Le wrapper existant ne conserve que `xWrite` + taille + code retour après délégation : il ne conserve ni les octets de `pBuf`, ni `iOfst`, ni l'identifiant stable du fichier ; ses traces sont insuffisantes pour reconstituer S↔A/B. Un `xOpen` avec `SQLITE_OPEN_MASTER_JOURNAL` aide à classifier S, mais un `xDelete(zName,...)` n'a pas d'identifiant SQL de transaction ni de handle fichier en argument.

**Conclusion impérative :** la collecte passive est **plausible sous prérequis falsifiables**, non acquise et non générale ; la neutralité et la complétude des observations demeurent à établir. Un GO éventuel devrait porter uniquement sur un **prototype de capture/validation d'écritures lors de COMMIT normaux**, distinct d'une éventuelle autorisation de callback pré-délégation ou de G04.

## 2. Documents et code réutilisés, sans refaire les études N/W

- Décision 00 actuelle, le rapport `SEC01-RD01-G03-R01-C03-ETUDE-FAISABILITE-20261025.md`, le contrat `SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md`.
- `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c` : `op()` typage `SQLITE_OPEN_MASTER_JOURNAL` ; `wr()` délègue `xWrite(inner,b,n,o)` puis journalise `n`, mais pas `b` ou `o` ; `de()` journalise après `parent->xDelete` en n'ayant que `zName` et `syncDir` ; `emit()` conserve le basename, pas l'identité canonique ni les handles.
- `b65-http/rd01-vfs-step1/g03_trace_analysis.py` : rapproche `xOpen(S)` et `xDelete(S)` par basename et ordre ; recevable pour préparation G03 mais **insuffisant pour C03-3**.
- CI historique n°135, commit `fc6eded13fa15b8776b12dd0cd494349d0a2e906` : référence N/W de fonctionnalités et verrous **seulement**, non une preuve des références croisées.
- Aucune compilation ni CI n'a été exécutée ici ; les analyses portent sur des contrats, des sources et le code déjà versionné.

## 3. Formats, ordre et disponibilité documentaire des références

| Élément | Mécanisme documenté par SQLite | Données accessibles conceptuellement via la VFS | Limite à vérifier sur SQLite Python 3.45.1 |
|---|---|---|---|
| S→A/B | S contient des noms de journaux rollback participants ; il ne contient pas les anciennes pages de base | ouvertures typées `SQLITE_OPEN_MASTER_JOURNAL`, flux `xWrite(S,buf,n,offset)` | encodage exact, terminaisons et découpage d'écriture du moteur concret non vérifiés par le banc |
| A→S et B→S | un enregistrement de pointeur vers le super-journal est ajouté à chaque journal rollback participant | `xWrite(A/B,buf,n,offset)` sur les handles de journaux ; éventuels `xSync` | présence, emplacement, alignement, longueur et écriture possiblement fragmentée doivent être corroborés |
| Identité des fichiers | S reçoit le flag de rôle lors de `xOpen`; A/B sont journaux propres à deux bases modifiées | `xOpen` + flags et chemin complet ; handle du journal pour chaque `xWrite` | aucun identifiant de transaction SQL n'est fourni par la VFS |
| Suppression S | un `xDelete` cible un chemin; sous les conditions rollback multi-bases, la suppression de S est le point logique de COMMIT | `xDelete(vfs,zName,syncDir)`, éventuellement typable via un registre externe déjà construit | aucun handle transmis à `xDelete` ; chemins réutilisés et collisions à exclure |
| Ordre des références | SQLite crée/remplit S et inscrit sa référence dans les journaux participants avant de le supprimer lors d'un COMMIT normal | enchaînement possible `xOpen/xWrite/xSync/xDelete` | séquence exacte des callbacks, buffers, retours et écritures du runtime cible **non attestée** |

**Format du pointeur A/B→S :** la spécification SQLite *File IO Specification* décrit un enregistrement optionnel de fin de journal comportant un numéro spécial de page verrou, un nom UTF-8, sa longueur, une somme de contrôle du nom et des octets magiques ; positionnement à un offset aligné sur la taille de secteur. Son décodage nécessite le contexte exact du journal. Ce document technique SQLite doit être traité comme une description de conception, **pas** comme preuve expérimentale que la version liée à Python émet exactement cette séquence d'appels VFS.

**Format S→A/B :** la documentation publique SQLite `lockingv3.html` et `tempfiles.html` établit une liste de noms de journaux participants dans S ; elle ne constitue pas, à elle seule, une preuve du **découpage en `xWrite`**, des frontières des chaînes ou des octets exacts générés par SQLite 3.45.1 sur le runner. Un décodeur devra être étalonné sur le format effectivement émis avant qu'une association soit recevable. Ne pas inventer l'existence d'un unique `xWrite` complet par fichier.

## 4. Possibilité et contraintes d'une reconstruction passive — proposition NON implémentée

**Entrée conceptuelle :** pour chaque handle de journal typé par `xOpen`, observer `xWrite(handle,pBuf,iAmt,iOfst)` **sans changer les buffers ni les arguments**, puis son code retour. Une séquence d'écritures validées peut être reconstruite en tant qu'image *logique observée*, indexée par **identité de handle + incarnation du fichier + offset**. Elle doit gérer :

1. **Fragments :** une référence peut se répartir sur plusieurs appels, secteurs ou offsets ; un parseur qui ne voit que le contenu d'un appel ne suffit pas. Les plages manquantes rendent la référence **INCOMPLÈTE**.
2. **Réécritures :** plusieurs appels à la même plage peuvent écraser des octets précédents. Appliquer les seules écritures dont le retour est conforme ; une erreur ou un retour ambigu rend l'état du contenu **INCONNU**, pas « écrit avec certitude ».
3. **Troncature et cycle de vie :** `xTruncate`, `xClose`, `xDelete`, nouvelle ouverture, génération/identité OS doivent être intégrés au modèle si leur absence rend la reconstruction fausse. Le wrapper actuel ne trace pas `xTruncate` ; une capture de `xWrite` seule ne garantit donc pas la reconstitution complète.
4. **Offsets et trous :** ne pas traiter des octets jamais observés comme des zéros attestés. `iOfst` et `iAmt` sont nécessaires pour reconnaître la structure aux bons offsets.
5. **Ordre et concurrence :** associer chaque appel à son handle/instance, avec ordre garanti dans la portée étudiée ; `serial` actuel global non protégé n'est pas une preuve générale multi-thread. Deux fichiers portant le même basename ne doivent jamais être fusionnés.
6. **Classification :** `SQLITE_OPEN_MASTER_JOURNAL` donne un rôle de création plus précis que la forme du nom. Exiger également le lien de chaque journal à sa base et une relation réciproque avec les références décodées.
7. **Données sensibles :** ne pas publier les buffers `xWrite` des pages applicatives. Une capture future devra être restreinte aux **journaux fictifs strictement nécessaires**, avec quota, contrôle d'accès, purge, suppression des données brutes après création de preuves vérifiables, sans clé ni identité réelle.
8. **Durabilité :** retour `SQLITE_OK` de `xWrite` atteste le résultat rapporté par la VFS, pas un `fsync` matériel. Une reconstruction en mémoire prouve au mieux les octets vus/reçus au passage ; elle ne garantit ni la persistance ni l'état après crash.

**Risques d'intrusion :** copie mémoire des buffers, allocations, checksum, synchronisation du canal probatoire et verrous du registre ajoutent latence et effets observateurs, y compris en mode COMMIT normal. Les contrôles de parité N/W reçus sont nécessaires mais non suffisants : une future instrumentation doit être comparée à la référence **sans altérer les règles de verrouillage, les codes d'erreur, `journal_mode=DELETE`, `synchronous=FULL` ou les invariants**. Aucune lecture des fichiers pendant COMMIT, aucun appel SQL réentrant et aucune modification des pointeurs fournis à `xWrite` ne seraient admissibles.

## 5. Unicité transactionnelle et preuve réciproque

Un fichier S est admissible si les éléments suivants sont simultanément établis :

- une seule incarnation typée **S** liée à un `xOpen` réussi `SQLITE_OPEN_MASTER_JOURNAL` ; identité de fichier/chemin complet et cycle de vie sans réutilisation ambiguë ;
- deux journaux rollback distincts **A et B**, chacun identifié par son `xOpen`, son appartenance à la base `main` ou `ATTACH`, et les deux modifications SQL dans la même transaction contrôlée du banc ;
- l'image logique observée de **S** permet de décoder **A** et **B** comme participants ;
- l'image logique observée de **A** permet de décoder **S**, et celle de **B** permet de décoder **le même S**, avec longueurs/checksums/format et offsets cohérents dans le profil choisi ;
- au moment de `xDelete`, le chemin complet correspond à cette **incarnation** de S **et à aucune autre** candidate ; l'identité ne repose ni uniquement sur `basename`, ni sur `run_id`, ni sur la proximité temporelle ;
- tout cas de noms dupliqués, fichiers recréés, écriture incomplète, erreur de journal, super-journal absent ou liens incompatibles aboutit à **AMBIGU / REJETÉ**, jamais à une validation implicite.

La VFS **n'expose pas de `transaction_id` SQL natif** dans `xWrite` ou `xDelete`. La portée probatoire resterait donc un banc borné ayant une seule transaction multi-bases active, où la corrélation SQL est appuyée par les deux mutations, les références réciproques et le cycle de vie. La transposition à plusieurs transactions concurrentes ou à `_persistent_journey()` exigerait des preuves supplémentaires et une décision distincte.

**Important :** une future trace `BEFORE_DELEGATE` de `xDelete` est une **autre exigence**. La collecte croisée à elle seule ne prouve pas la phase d'entrée du callback ni la capacité d'arrêter l'enfant dans ce callback. Aucune réalisation G04 n'est envisageable sur la seule base de cette étude.

## 6. Matrice de suffisance probatoire C03-3

| Liaison | Documenté par SQLite | Déjà démontré dans le banc | Requiert instrumentation ultérieure | Cas bloquant |
|---|---|---|---|---|
| S→A/B | Oui, liste des journaux dans S | **Non** | capture passive des octets `xWrite(S)`, identité/offsets, décodage | liste absente, partielle ou ambiguë |
| A→S | Oui, pointeur vers S dans A | **Non** | `xWrite(A)`, parseur de fin de journal, vérification de structure | pointeur absent ou checksum invalide |
| B→S | Oui, pointeur vers S dans B | **Non** | `xWrite(B)`, même contrôle | cible différente ou pointeur absent |
| Fichier S typé | `SQLITE_OPEN_MASTER_JOURNAL` | **Candidat identifié** par traces historiques | identité de handle/incarnation, chemin complet et durée de vie | seule ressemblance de nom |
| Journaux A et B rattachés aux bases | nom, mode et journaux rollback documentés | **Ouvertures observées** sur le banc | rôle de fichiers, génération/handle, double mutation vérifiée | journal étranger ou une base non modifiée |
| `xDelete`→incarnation de S | opération par chemin, sans handle natif | **Corrélation basename post-retour seulement** | registre d'incarnations et chemin complet ; phase avant délégation séparée | plusieurs incarnations compatibles ou fichier réutilisé |
| Neutralité | aucune garantie de neutralité d'un observateur | référence fonctionnelle N/W limitée au profil CI | qualification comparative après instrumentation, conservation des retours/ordres pertinents | perturbation transactionnelle inexpliquée |
| Durabilité physique | hypothèses propres à SQLite et au stockage | **Non** | hors de C03-3 ; nécessite protocole séparé | aucune déduction d'un simple `xWrite` |

## 7. Décision finale proposée au 00

**GO CONDITIONNEL pour envisager un jour un prototype de collecte passive de références croisées en COMMIT normal**, à condition d'obtenir une autorisation expresse nouvelle, sur le wrapper isolé et le moteur SQLite fixé. Ce GO documentaire ne constitue **aucun GO d'implémentation**.

Le prototype ultérieur, s'il est autorisé, aurait un **seul objectif de réception** : produire un certificat montrant **S→{A,B}, A→S, B→S**, avec identités de fichiers complètes, gestion des écritures fragmentées/réécrites et absence d'association concurrente, **sans ouvrir les journaux à chaud**. Toute ambiguïté ou omission est un échec bloquant ; un COMMIT normal réussi ne suffit pas.

**Condition technique bloquante unique : démontrer la reconstruction fiable et réciproque des trois références S→A/B, A→S et B→S exclusivement à partir des écritures VFS validées et des identités/cycles de vie des fichiers, sans modifier la transaction ni dégrader les acquis N/W.**

Si les références ne sont pas observables de manière complète à ce niveau, ou si leur reconstruction exige une intrusion invalidante, le verdict devient **NO-GO motivé** pour cette méthode, sans multiplier les études générales.

## 8. Provenance, limites et statuts

**Sources du dépôt GitHub (contrôlées dans ce mandat) :**
- `b65-http/DECISION-00-SEC01-RD01-C03-3-COLLECTE-PASSIVE-20261025.md`
- `b65-http/SEC01-RD01-G03-R01-C03-ETUDE-FAISABILITE-20261025.md`
- `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`
- `b65-http/rd01-vfs-step1/g03_trace_analysis.py`.

**Documentation externe SQLite consultée :**
- https://www.sqlite.org/lockingv3.html — relations réciproques entre super-journal et journaux rollback.
- https://www.sqlite.org/atomiccommit.html — mécanisme COMMIT multi-bases.
- https://www.sqlite.org/tempfiles.html — création, contenu et conditions du super-journal.
- https://www2.sqlite.org/fileio.html — description de pointeur de super-journal et des structures de journal ; **la correspondance exacte avec les appels de SQLite 3.45.1 reste non testée**.
- https://www.sqlite.org/c3ref/io_methods.html — interface `xWrite` (buffer, taille, offset).

**Contrôles nouveaux :** aucun test local, aucune CI, aucune compilation et aucune modification C/Python. Les références CI n°135 sont historiques et **ne démontrent pas C03-3**.

**Statuts inchangés :** C03-3, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global partiel ; B6.5 en recette ; B6.3 et production NO-GO.

**Prochaine action unique :** soumettre cette décision de faisabilité au chat 00 pour arbitrage explicite d'un éventuel prototype isolé de collecte passive, sans mise en œuvre implicite.
