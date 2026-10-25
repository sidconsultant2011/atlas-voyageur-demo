# Décision 00 — SEC-01 R1-RD01 — Livraison technique C03-R03 pour recette indépendante

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `7fed4e79c591c2e6780e398012892de683f93f33`  
**Chantier prioritaire unique :** réception indépendante du suivi du résultat de `xClose` dans C03-R03.

## Contrôles et preuves

- Mandat 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R03-XCLOSE-20261025.md`.
- Rapport 01 : `b65-http/SEC01-RD01-C03-R03-XCLOSE-CORRECTIF-PREUVES-20261025.md`.
- Diff GitHub `eecd19fe20de899ba747fab3aab4bbfcb2ab310a..7fed4e79c591c2e6780e398012892de683f93f33` : **quatre fichiers** dans le périmètre, `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` et `c03_run.py` modifiés, `b65-http/test_c03_r03.py` et le rapport ajoutés. Le wrapper C de référence, l'application et le workflow restent inchangés.
- CI n°178 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232772919 ; `completed/success` sur le **commit testé `63664ba669964c1427d5032cbf274d34b1b7a3dc`** ; 116/116 JavaScript, 11/11 SQLite, 125/125 HTTP/identité/banc : **252 exécutions réussies**, non nécessairement autant de scénarios distincts.
- C expérimental inspecté au commit testé : `cl()` appelle `xClose` natif, passe le retour exact à `record_close_result(slot,r,1)`, libère le handle interne puis retourne `r`. Le helper distingue `close_called`, `close_known`, `close_rc` et `closed` ; `closed=1` seulement si résultat connu `SQLITE_OK`, sinon `error=1` et absence de preuve positive.
- Python inspecté : `run()` collecte `c03_close_info` pour les entrées C03 du banc et `reciprocal_certificate()` invoque `validate_close_evidence(entry)` ; la certification refuse fermeture absente, indéterminée ou en échec. Les anciennes fixtures synthétiques sans champs additionnels sont conservées sous le contrôle `closed/error` : ce n'est **pas** une preuve d'un retour natif pour ces anciennes fixtures.
- Cinq tests C03-R03 `ok` dans le journal CI n°178 : succès `SQLITE_OK`, échec retour natif fourni au helper, retour indéterminé, fermeture non invoquée, échecs sur journaux A/B et super-journal S.
- Certificat normal CI : `RECONSTRUIT_BANC_FICTIF`, S→A/B et A/B→S, six suppressions attribuées sur six, `ambiguous=0`, `no_match=0`, `native_errors=0`, `not_closed=0`, deux intégrités `ok/ok`, DELETE/DELETE, FULL/FULL, SQLite Linux 3.45.1.
- CI n°177 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40232703728 ; `completed/failure` sur `cd2a8ddc874f95c931d683cd6b1afd79530f10ad` ; erreur de fixture signalée par 01 : lecture de l'index `deleted` à la place de `closed`. Correction au commit testé n°178. **L'échec de n°177 reste conservé.**
- Tests locaux du commit exact : **non exécutés selon le rapport 01**. Le chat 00 n'a lancé aucun test.

## Décision du 00

**LIVRAISON TECHNIQUE C03-R03 ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03**, sans clôture anticipée.

Le suivi expérimental distingue désormais invocation, disponibilité du résultat natif et réussite de fermeture. La logique et les cinq tests apportent une preuve candidate dans le banc fictif isolé ; aucun test n'a provoqué de véritable erreur de fermeture du système de fichiers.

### Mandat unique au chat 03

1. Vérifier le code `cl()` et `record_close_result()` au commit testé : résultat natif `xClose` inchangé, `closed` positif si et seulement si retour connu `SQLITE_OK`, erreur ou indétermination rejetée.
2. Contrôler l'export `c03_close_info`, sa collecte dans `run()` et son contrôle par `validate_close_evidence()` avant certification. Examiner l'exception de compatibilité des anciennes fixtures sans métadonnées C03-R03 pour ne pas la confondre avec le chemin réel.
3. Examiner les cinq tests ciblés et leurs assertions effectives : `SQLITE_OK`, `SQLITE_IOERR` synthétique, résultat inconnu, absence d'invocation, échec ciblé A/B/S ; distinguer les valeurs simulées de véritables retours OS.
4. Vérifier le rattachement exact de la CI n°178 au commit `63664ba`, les cinq tests individuels, 116/11/125 exécutions et non-régression S↔A/B, DELETE/FULL, `integrity_check=ok/ok`, C03-R01 et C03-R02.
5. Contrôler l'échec historique CI n°177 et la correction de fixture sans requalifier l'échec comme réussite.
6. Remettre **un PV de recette indépendant** avec verdict, réserves et avis sur une **clôture ciblée** C03-R03 dans le seul périmètre du banc fictif. Aucune clôture automatique par 03 ni autorisation G04/P0.

**Restrictions :** examen documentaire et de code seulement ; aucune modification, nouveaux tests exigés, injection, SIGKILL, `BEFORE_DELEGATE`, G04, fusion main ni production.

## Statuts maintenus

**C03-R03 OUVERTE, livraison en attente de PV 03** ; C03-R01 et C03-R02 clôturées uniquement dans leur périmètre expérimental ; C03-R04 à R06 ouvertes ; C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 ouverts ; G04 NO-GO ; B6.5 en recette ; B6.3 et production NO-GO. G05 global et R1-C01 demeurent partiels selon le référentiel précédent.

## Prochaine action unique

Transmettre au chat 03 le rapport, le commit testé et les journaux CI n°177/178 pour une recette indépendante exclusivement C03-R03.
