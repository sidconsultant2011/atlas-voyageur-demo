# SEC-01 R1-RD01 — C03-3 — Prototype isolé de collecte passive — Rapport de preuves
**Date :** 25 octobre 2026. **Périmètre :** journaux SQLite fictifs, COMMIT normal, sans panne.  
**Décision 00 :** `b65-http/DECISION-00-SEC01-RD01-C03-3-PROTOTYPE-ISOLE-20261025.md`.  
**HEAD initial contrôlé :** `cdd802cfec8419472716983be401b0ece57c54c6`.  
**Branche :** `feature/b6-5-cartographie-interactive`.

## 1. Livrables techniques et séparation
- `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` : **copie expérimentale distincte**, VFS `atlas_c03_passive`, commit `5062ddaf04396910cb4a74cdd7ace418c3a45676`.
- `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : décodeur mémoire et certificat synthétique, commit `3feb650f080a60fbce122179bf035ce6196c9996`.
- `b65-http/test_c03_passive.py` : scénario SQLite réel fictif et quatre cas synthétiques, commit testé `3a1c004257f292c6b5cc2c12321a80228a4e8720`.
- Le wrapper de référence **`atlas_rd01_vfs.c` inchangé** ; aucun fichier applicatif ni workflow modifié ; aucune nouvelle dépendance externe installée.

## 2. Contrat d'observation effectivement implémenté
1. La VFS expérimentale relaie les méthodes V1 vers la VFS mère et n'active pas de modification de `xDelete` avant délégation. Aucun arrêt ni temporisation dans un callback.
2. La capture est limitée aux handles ouverts avec `SQLITE_OPEN_MAIN_JOURNAL` ou `SQLITE_OPEN_MASTER_JOURNAL`. **Aucun buffer des écritures des fichiers de base** n'est conservé. Les copies temporaires de buffers de journal restent uniquement en mémoire du processus et ne sont ni écrites dans un fichier ni imprimées.
3. Le prototype enregistre l'identité de chemin, un ordinal d'incarnation, un tableau d'octets et de présence par offset, écritures acceptées `SQLITE_OK`, écrasements successifs, troncatures réussies, fermetures et suppressions réussies.
4. Garde-fous : au plus 16 incarnations de journaux et 1 Mio par incarnation ; dépassement, erreur de `xWrite` ou `xTruncate`, manque d'octets observés et identification multiple entraînent un échec.
5. Décodage après **COMMIT normal**, et non depuis le callback : les données logiques du super-journal contiennent deux noms de journaux rollback ; les deux journaux contiennent chacun une structure de pointeur vers le même S, vérifiée avec numéro de page de verrou, longueur, somme des octets du nom et magie SQLite. Seuls noms de rôle, générations, offsets et résultats sont émis dans le certificat.
6. Le code ne présente pas l'ordinal d'incarnation comme identifiant transactionnel natif. Le certificat est limité au contexte du banc isolé, mono-transaction finale et deux bases effectivement écrites.
7. La mémoire C n'est pas explicitement purgée avant la fin du processus : la garantie est **absence de publication et de persistance volontaire de buffers bruts**, non confidentialité mémoire formellement démontrée.

## 3. Résultats CI finalisés
**GitHub Actions n°150** : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40218478132  
**Commit testé :** `3a1c004257f292c6b5cc2c12321a80228a4e8720`.  
**État :** `completed / success`.

- 116 tests JavaScript sur 116 réussis.
- 11 tests SQLite sur 11 réussis.
- 103 exécutions HTTP/identité/banc sur 103 réussies, dont les **5 tests C03-3**.
- **230 exécutions au total**, certaines découvertes unittest pouvant répéter des classes ; ne pas interpréter comme 230 scénarios uniques.
- CI n°148 (source C seule) et n°149 (code Python ajouté) ont également conclu `success` ; seule la n°150 couvre les **cinq tests de rejet et de succès ajoutés**.

**Tests locaux :** essai du banc prototype isolé exécuté dans le conteneur de préparation, Linux, Python lié à SQLite **3.46.1**, résultat `RECONSTRUIT_BANC_FICTIF` pour S↔A/B. Ce contrôle de préparation locale ne représente **pas** l'exécution du commit GitHub final. La preuve intégrée au commit exact est la CI n°150 sur SQLite **3.45.1**.

## 4. Certificat synthétique CI n°150
D'après la ligne `RD01 C03-3 PASSIVE CERTIFICATE` des journaux :
- `verdict=RECONSTRUIT_BANC_FICTIF` ; `same_sqlite_symbol=true`.
- `links.S_to_journals=[A,B]` ; `links.A_to_S=true` ; `links.B_to_S=true`.
- Fichier S ouvert comme `SQLITE_OPEN_MASTER_JOURNAL`, génération interne **6**, **2 écritures**, suppression réussie après COMMIT normal.
- Journal A : génération **4**, **13 écritures**, pointeur A→S à l'offset **9216**, référence S→A à l'offset **0**.
- Journal B : génération **5**, **16 écritures**, pointeur B→S à l'offset **13312**, référence S→B à l'offset **56**.
- `observed_journal_incarnations=6` ; les incarnations précédentes correspondent aux transactions de préparation fictives et ne doivent pas être confondues avec la transaction finale.
- `mutations=[1,fake]`, `integrity_check=[ok,ok]`, `journal_mode=[delete,delete]`, `synchronous=[2,2]`, taille page **4096**, moteur CI SQLite **3.45.1**.
- `raw_buffers_published=false`, `before_delegate_demonstrated=false`, `crash_recovery_demonstrated=false`, `physical_durability_demonstrated=false`.

Les noms complets des journaux et les octets de leurs pages ne sont **pas publiés**. Les offsets constituent une provenance d'observation, pas un pointeur durable hors de la transaction.

## 5. Cas négatifs réellement exécutés
- `test_reject_missing_reference` : référence corrompue dans le journal B → rejet attendu, test réussi.
- `test_reject_incomplete_fragment` : masque de couverture amputé → rejet attendu, test réussi.
- `test_reject_ambiguous_super` : deux super-journaux compatibles → rejet attendu, test réussi.
- `test_accept_complete_synthetic_fragments` : certificat synthétique cohérent → reçu, test réussi.
- `test_normal_commit_real_sqlite` : deux bases et références réellement émises via VFS → certificat reçu, test réussi.

**Limites de couverture négative :** pas de scénarios automatiques ciblant chaque type d'erreur I/O, toutes les fragmentations possibles, les collisions de chemins vivants, la réutilisation d'incarnation ou la concurrence multi-transaction. Les contrôles de structures existent mais cette campagne n'en établit pas l'exhaustivité. Les deux bases restent entièrement fictives.

## 6. Parité, effet observateur et verdict à soumettre au chat 03

| Propriété | Observation | Limite |
|---|---|---|
| Liens S→{A,B} | **Reconstitués** | Dans le banc, version SQLite et format capturés |
| A→S et B→S | **Reconstitués et contrôlés** | Pas de démonstration généralisable à d'autres versions/formats |
| Identité de fichier / incarnation | Chemin complet de banc + génération, lien typé `xOpen` | Ce n'est pas un ID SQL natif ; concurrence/renommage non exhaustivement éprouvés |
| Troncatures / écritures | Traitement logique des retours, offsets et présence | Capture mémoire limitée ; absence de panne et erreurs de stockage simulées |
| COMMIT et intégrité | Deux écritures, COMMIT normal, deux `integrity_check=ok` | Pas de preuve d'atomicité en crash |
| Neutralité VFS | Résultats fonctionnels sans erreur en scénario positif | **Aucune mesure comparative N/W/P de latence ni d'ordre I/O par appel** ; non démontrée |
| G04 / `BEFORE_DELEGATE` | Aucune instrumentation de causalité | **NO-GO** |
| Durabilité physique | Non testée | **NON DÉMONTRÉE** |

**Proposition technique : C03-3 recevable dans la stricte limite de la reconstitution réciproque sur banc Linux SQLite 3.45.1 ; réception indépendante du chat 03 requise.** Ne pas clôturer G03-R01, VFS-R01, G03-R06, R1-RD01, R1 ni P0-01. Aucun GO d'instrumentation `BEFORE_DELEGATE`, G04, production ou fournisseur réel.

## 7. Provenance et références
- Décision autorisant le prototype : `DECISION-00-SEC01-RD01-C03-3-PROTOTYPE-ISOLE-20261025.md`.
- Rapport de faisabilité antérieur : `SEC01-RD01-C03-3-COLLECTE-PASSIVE-FAISABILITE-20261025.md`.
- Source SQLite : https://sqlite.org/draft/fileio.html (structure de pointeur en journal), https://www.sqlite.org/lockingv3.html (super-journal), https://www.sqlite.org/c3ref/io_methods.html (buffers et offsets).
- Preuve CI n°150 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40218478132.

**Prochaine action unique :** réception indépendante du chat 03 sur le commit testé `3a1c0042`, les journaux CI n°150 et le présent rapport, sans autorisation implicite de G04.
