# SEC-01 R1-RD01 — G03-R01-C03 — Faisabilité de l'association transaction, super-journal et xDelete

**Date :** 25 octobre 2026  
**Nature :** étude documentaire uniquement ; aucune instrumentation, compilation, modification de code ou exécution de test.  
**Décision 00 :** `b65-http/DECISION-00-SEC01-RD01-G03-R01-C03-ETUDE-FAISABILITE-20261025.md`  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant rédaction :** `2e20a33dbfddf47d44f8d241b0a61b0ec505f4b6`.

## 1. Verdict motivé

**FAISABILITÉ DE CONCEPTION CONDITIONNELLE pour un banc SQLite isolé, à périmètre borné ; démontrabilité réelle NON ACQUISE.** L'association transaction multi-bases → super-journal → `xDelete` n'est **pas nativement fournie par une seule méthode VFS**. Un registre de correspondances hors SQLite pourrait permettre de la reconstituer en combinant :
1. un scénario attestant deux mutations effectivement réalisées sous une transaction `ATTACH` unique ;
2. l'ouverture positive d'un fichier de rôle super-journal, signalée par `SQLITE_OPEN_MASTER_JOURNAL`, avec identité de fichier complète ;
3. des indices **indépendants du seul nom** établissant la participation des deux journaux rollback et leur relation au super-journal ;
4. l'identité du chemin que recevrait le même `sqlite3_vfs.xDelete` lors de son invocation ;
5. une future attestation `BEFORE_DELEGATE`, émise avant l'appel à la VFS mère, **non implémentée et non autorisée dans ce mandat**.

Le simple appariement `xOpen` / `xDelete` par basename ne satisfait pas C03. Un identifiant de scénario ne devient pas automatiquement un identifiant natif de transaction SQLite. La conception n'est qualifiable comme **vérifiable** que si elle exclut explicitement les associations concurrentes, les homonymes et les fichiers temporaires réutilisés. À défaut : **NO-GO pour l'instrumentation causale**, même si l'essai courant fonctionne.

## 2. Fondement exact et frontières de l'API

Sources du dépôt consultées :
- `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c` ;
- `b65-http/rd01-vfs-step1/g03_trace_analysis.py` ;
- `b65-http/SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md` ;
- décision de gouvernance citée en tête.

**Constat dans le wrapper actuel :**
- `op()` reçoit `zName` et `flags` ; `role()` classe `SQLITE_OPEN_MASTER_JOURNAL` comme `super-journal-candidate`. Il logue après `parent->xOpen`.
- `de()` reçoit un `zName` et `syncDir`, transmet à `parent->xDelete` puis émet `xDelete` après le retour. Son `role(z,0)` **ne peut pas** reconstruire le drapeau `SQLITE_OPEN_MASTER_JOURNAL` qui était présent lors d'un `xOpen`.
- `emit()` tronque chaque chemin au **basename**, écrit séquence, PID, nom d'événement, rôle, code de retour et flags. Il n'enregistre pas le chemin canonique, l'identité de fichier persistante, le handle, la connexion, le TID ni la transaction.
- `g03_trace_analysis.py` recherche l'ouverture candidate et une suppression ultérieure sur le **même basename**. Cette méthode permet une corrélation de trace, pas l'association C03 non ambiguë.
- Aucun identifiant SQL de transaction n'est transmis par `sqlite3_vfs.xDelete(sqlite3_vfs*, const char *zName, int syncDir)`. Contrairement à certaines méthodes `sqlite3_io_methods`, `xDelete` ne reçoit **pas** `sqlite3_file*` ; il n'existe donc aucun handle à inférer directement de cet appel.

**Fondement SQLite officiel :** `https://www.sqlite.org/c3ref/vfs.html` ; `https://www.sqlite.org/atomiccommit.html` ; `https://www.sqlite.org/tempfiles.html`. En rollback multi-fichiers utilisant réellement un super-journal, sa suppression est décrite comme le point logique du COMMIT ; la réalisation physique de cette opération et le fonctionnement des systèmes de fichiers ont des hypothèses distinctes. Les détails de fichiers temporaires peuvent évoluer avec SQLite : **le profil doit rester fixé à la version et au moteur testés**.

## 3. Matrice des identités et preuves attendues

| Objet | Identifiant nécessaire | Origine / possibilité | Preuve indépendante ou limite |
|---|---|---|---|
| Exécution fictive | `run_id`, version moteur, PID, manifest de configuration | Contrôle du banc seulement | Prouve l'environnement, **pas** l'identité transactionnelle |
| Transaction SQL | identifiant corrélé à la connexion, bornes transactionnelles, deux mutations et résultat COMMIT | À reconstruire par contrôle du banc et événements ; aucun champ SQL transaction dans `xDelete` | Invalide si deux transactions candidates peuvent correspondre |
| Bases principales et ATTACH | chemins canoniques, alias, URI/VFS réellement choisie, identifiants de fichiers | Connexion/ATTACH du banc et ouvertures `xOpen` | Même version/ABI et couverture VFS des deux bases indispensables |
| Journaux rollback participants | identité, chemin complet, liens aux bases, cycle de vie | `xOpen`, rôle/flags et corroboration du contenu/métadonnées de journal sous protocole non intrusif futur | Distinguer les journaux de cette transaction des journaux d'autres transactions |
| Super-journal | `SQLITE_OPEN_MASTER_JOURNAL`, nom complet normalisé, répertoire, identité de création, correspondance aux journaux participants | `xOpen` VFS ; modèle SQLite des super-journaux et de leurs références | Le flag est plus probant qu'un suffixe, **mais ne porte pas seul l'identité de la transaction** |
| Suppression ciblée | chemin complet normalisé, identité de l'opération, rôle prouvé par registre, `syncDir` | `xDelete` ; pas de handle en argument | Nécessite une correspondance univoque à un super-journal préalablement enregistré |
| Attestation avant délégation | numéro d'invocation, `BEFORE_DELEGATE`, événement reçu avec provenance et statut de conservation | **Proposition future non implémentée** | Une trace post-retour ne prouve pas l'entrée préalable au point de suppression |

**Attention aux identités OS :** le chemin canonique permet une comparaison plus précise que le basename mais n'établit pas seul l'identité inode/fichier : renommage, suppression/recréation et réutilisation sont possibles. Une identité OS (périphérique/inode) pourrait corroborer l'objet **tant qu'il existe**, sans devenir une identité éternelle. La correspondance doit reposer sur plusieurs éléments, notamment rôle VFS, cycle de vie, contexte transactionnel et références aux journaux, avec incertitude explicitement signalée.

## 4. Faisabilité des corroborations supplémentaires

### A. Drapeau de création

**Exigence :** constater `xOpen` réussi portant `SQLITE_OPEN_MASTER_JOURNAL`, avec nom complet et identifiant d'ouverture. Son rôle initial est établi plus précisément qu'avec le basename. **Limite :** le seul drapeau indique un type de fichier demandé par SQLite, sans lier formellement les deux bases participantes.

### B. Références entre journaux

**Piste de corroboration issue de la documentation SQLite :** lors du COMMIT multi-fichiers en rollback, les journaux individuels et le super-journal ont des références destinées à permettre la récupération atomique. Une future procédure documentaire/technique de vérification pourrait croiser, quand elles sont accessibles, les références au super-journal depuis les journaux rollback et la liste de journaux associée au super-journal. Leur format exact, leur visibilité avant suppression et leur stabilité dans la version SQLite cible ne sont **pas validés ici**.

**Risque d'effet observateur :** accéder à ces fichiers pendant une transaction pourrait influer sur verrous, concurrence, durée et I/O ; aucune lecture live supplémentaire ou copie à chaud n'est autorisée. Une approche par informations passivement collectées dans le chemin d'I/O autorisé serait à étudier sous **nouveau mandat** et sous contrôle des limites de neutralité ; pas de lecture réentrante de SQLite depuis la VFS.

### C. Contexte d'unicité du banc

Un répertoire isolé, un seul processus et une seule transaction multi-bases active réduisent les ambiguïtés, sans remplacer la corroboration des fichiers. La preuve doit être explicitement limitée à ces préconditions. Un cas comportant plusieurs transactions ou fichiers homonymes, y compris sur répertoires distincts, ne peut être déclaré équivalent sans identité supplémentaire.

### D. Suppression exacte et absence de handle

Le `xDelete` ne recevant que `zName` et `syncDir`, la corrélation doit consulter conceptuellement le registre des fichiers déjà typés. Pour une invocation future, l'association recevable requiert exactement **un** super-journal actif compatible par chemin, cycle de vie et lien aux participants. Si zéro ou plusieurs candidats sont compatibles : **NON DÉMONTRÉ / NO-GO**. Ne pas inférer à partir de `syncDir` qu'il s'agit d'un super-journal.

### E. Phase future BEFORE_DELEGATE

L'émission éventuelle de `BEFORE_DELEGATE` aurait à se produire **dans** le callback `xDelete`, avant l'appel natif, avec identifiant d'invocation et preuve de réception. Cette position permettrait seulement d'attester l'arrivée dans le callback ; elle ne prouverait ni le succès de la suppression, ni le franchissement du point logique COMMIT, ni une persistance physique. Elle ne doit pas être remplacée par un message Python émis avant `commit()` ou une temporisation. **Aucune réalisation de ce mécanisme n'est autorisée dans la présente étude.**

## 5. Protocole futur falsifiable — non exécuté

| Porte C03 | Preuve exigée dans un futur banc autorisé | Rejet falsifiable |
|---|---|---|
| C03-1 — Participants | deux bases **effectivement modifiées** par la même transaction, journaux attribués aux bases | une seule base écrite ou transaction incertaine |
| C03-2 — Rôle fichier | `xOpen` réussi avec `SQLITE_OPEN_MASTER_JOURNAL`, identité du fichier et cycle de vie complets | simple suffixe `-mj`, basename ou ouverture en échec |
| C03-3 — Lien indépendant | références du super-journal et des **deux** journaux rollback compatibles et vérifiables sans modifier la transaction | noms seulement, référence manquante ou incompatible |
| C03-4 — Unicité | un unique super-journal compatible, malgré essais conceptuels de collision/concurrence | zéro ou plusieurs candidats plausibles |
| C03-5 — Cible `xDelete` | même fichier identifié par le registre, et non par ordre temporel arbitraire | chemin ambigu, suppression d'un journal individuel ou fichier recréé |
| C03-6 — Phase | `BEFORE_DELEGATE` distinct de `AFTER_RETURN`, associé à la même invocation, sans marqueur externe substitué | seul post-retour disponible |
| C03-7 — Neutralité | acquis N/W (DELETE/FULL, verrous, codes, SQL et intégrité) préservés sous contrôle indépendant | divergence inexpliquée ou réentrance |
| C03-8 — Fiabilité | ordre, origine et état d'archivage prouvés, sans prétendre à une durabilité physique | séquence ambiguë ou trace émise assimilée à preuve persistée |

Ces critères sont **des exigences proposées pour un éventuel protocole ultérieur**, non des tests passés ou une validation des portes C01–C08 antérieures.

**Règle d'arrêt :** dès qu'une identité reste multivaluée, que le drapeau n'est pas observé ou que le lien aux deux journaux n'est pas démontrable avec une neutralité acceptable, déclarer **C03 NON QUALIFIÉE**. Ne pas compenser par temporisation, multiplications d'essais ou inférence de COMMIT à partir du seul retour `SQLITE_OK`.

## 6. Neutralité et risques de conception

- **Réentrance :** le callback ne doit pas appeler SQLite pour demander quel SQL ou quelle transaction est active ; cela pourrait introduire une réentrance et modifier les verrous.
- **Concurrence :** le `serial` global actuel n'est pas protégé ; le futur registre devrait avoir une discipline de concurrence sans créer de nouveau blocage sur le chemin de COMMIT.
- **Timing et latence :** journaux supplémentaires, IPC, calcul de chemin canonique ou lecture du contenu des journaux à chaud peuvent perturber l'ordonnancement ; aucune « neutralité parfaite » présumée.
- **Verrous et synchronisations :** rester au même moteur SQLite, préserver délégations, codes d'erreur, `journal_mode=DELETE`, `synchronous=FULL`, effets `SQLITE_BUSY` et états N/W déjà réceptionnés. La version V1 des méthodes I/O reste une limite déclarée du wrapper.
- **Persistance de la preuve :** distinguer émission, réception, accusé, sauvegarde et synchronisation de la trace. SHA-256 prouve une intégrité de copie sous conditions, pas la durabilité d'un crash.
- **Sécurité :** identités et bases fictives exclusivement ; traces hors journaux SQLite et sans secrets ; aucune extension à `_persistent_journey()` dans ce mandat.

## 7. Conclusion, arbitrage et condition unique

**Verdict : GO documentaire de faisabilité conditionnelle ; NO-GO de réalisation immédiate.** Une conception vérifiable semble possible dans le profil isolé si la correspondance du fichier et de ses deux journaux peut être corroborée et si une future invocation `xDelete` peut retrouver **un seul** candidat correctement qualifié. Le code présent ne démontre pas ces préconditions.

**Condition bloquante prioritaire unique : démontrer par des références indépendantes et non ambiguës que le super-journal identifié avec `SQLITE_OPEN_MASTER_JOURNAL` appartient exactement aux deux journaux rollback de la transaction fictive, de sorte que le `xDelete` sur son chemin complet ne puisse cibler qu'un seul fichier de cette transaction.**

La future preuve `BEFORE_DELEGATE` reste une exigence séparée, non implémentée. Une première vérification du lien journaux/super-journal serait nécessaire **avant** tout arbitrage de développement de callback.

**Pas de nouvelle preuve expérimentale** acquise ici. VFS-R01, G03-R01, G03-R06, R1-RD01, R1, P0-01 ouverts ; G03 avec réserves, G04 NO-GO, G05 global partiel ; B6.5 en recette, B6.3 et production NO-GO.

## 8. Sources

- Décision officielle 00 : `DECISION-00-SEC01-RD01-G03-R01-C03-ETUDE-FAISABILITE-20261025.md`.
- Contrat G03-R01 : `SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md`.
- Sources du banc : `rd01-vfs-step1/atlas_rd01_vfs.c`, `rd01-vfs-step1/g03_trace_analysis.py`.
- SQLite officiel : https://www.sqlite.org/atomiccommit.html ; https://www.sqlite.org/tempfiles.html ; https://www.sqlite.org/c3ref/vfs.html.
- Résultats CI historiques préexistants et non rejoués : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980 (n°135, commit `fc6eded13fa15b8776b12dd0cd494349d0a2e906`).

**Prochaine action unique :** transmettre ce verdict au chat 00 pour arbitrage éventuel d'une méthode de corroboration journaux/super-journal, sans développement ni essais dans la présente phase.
