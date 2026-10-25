# Décision 00 — SEC-01 R1-RD01 — Clôture ciblée C03-R01

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `20b5be4cf7602f3e4bca693e78bbde7c7179c7e9`  
**Autorité :** 00 — Pilotage et gouvernance.

## Sources vérifiées

- Décision de transmission à la recette : `b65-http/DECISION-00-SEC01-RD01-C03-R01-RECEPTION-20261025.md`.
- Rapport technique 01 : `b65-http/SEC01-RD01-C03-R01-INCARNATIONS-CORRECTIF-PREUVES-20261025.md`.
- Procès-verbal indépendant **`PV-03-SEC01-RD01-C03-R01-20261025`** transmis au 00 le 25 octobre 2026 ; verdict **réception favorable avec réserves, recommandation de clôture ciblée**. Le PV est reçu comme texte transmis ; sa présence en tant que fichier GitHub autonome n'a pas été attestée.
- Commit de code testé : `5bd4a0aec3c24a4ed2690d22af8885a63d72762d`.
- CI n°170 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231306358 : `completed / success` au commit testé ; **116/116 JavaScript, 11/11 SQLite, 120/120 HTTP/identité/banc, 247 exécutions réussies** (pas nécessairement autant de scénarios distincts).
- Code Python `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` contrôlé au commit testé : `reciprocal_certificate()` n'utilise plus `max(matches, key=lambda r: r["generation"])` comme sélecteur ; références S↔A/B, présence des octets et masques, format des pointeurs et états observés du cycle de vie sont exigés ; **zéro ou plusieurs incarnations compatibles provoquent un rejet**. Une incarnation postérieure du même chemin est refusée conservatoirement.
- Sept tests C03-R01 présents et `ok` dans les logs : incarnation unique ; historique discriminé ; plusieurs compatibles ; participant absent ; références incompatibles ; recréation sans continuité ; incarnation incomplète. Les essais négatifs sont synthétiques et utilisent `reciprocal_certificate()`.
- Certificat positif CI : `RECONSTRUIT_BANC_FICTIF`, `S_to_journals=[A,B]`, `A_to_S=true`, `B_to_S=true`, `deletion_attribution={events:6,attributed:6,ambiguous:0,no_match:0,native_errors:0,not_closed:0}`, intégrité `ok/ok`, DELETE/DELETE, FULL/FULL, SQLite CI 3.45.1.
- Incident historique **CI n°169** https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40231220751 : `completed / failure` sur `1f7ff049acc5290017cbb21192c0660579506fda`. Le PV indépendant attribue l'échec à la fixture du masque incomplet, corrigée avant n°170. **L'échec n°169 reste une preuve historique et n'est pas requalifié.**
- Aucun test local du commit final par le chat 03 ou le 00.

## Décision explicite du 00

**GO DE CLÔTURE CIBLÉE C03-R01**, limité aux incarnations de journaux observées dans le **registre du banc fictif** et aux scénarios de validation réceptionnés.

Le défaut ciblé consistant à **choisir arbitrairement une incarnation de journal par `max(generation)`** est corrigé. La sélection n'est probatoirement recevable que si une incarnation unique pour chaque journal participant correspond aux références réciproques observées et aux règles de cycle de vie du prototype ; les situations ambiguës ou insuffisamment corroborées entraînent le refus du certificat.

**C03-R02 demeure clôturée uniquement dans son périmètre expérimental**, selon la décision `b65-http/DECISION-00-SEC01-RD01-C03-R02-CLOTURE-CIBLEE-20261025.md`. Aucune réouverture automatique.

## Limites conservées

Cette clôture **n'établit pas** d'identité physique universelle des fichiers ni d'identification transactionnelle native SQLite, d'exhaustivité des événements VFS, de couverture générale des fichiers recréés/renommés, de comportement concurrent multi-transaction, de neutralité de l'instrumentation, de confidentialité complète de la mémoire, de durabilité physique, de récupération après panne, ou d'attestation causale `BEFORE_DELEGATE`.

**Statuts après arbitrage :**
- **C03-R01 : CLÔTURÉE — périmètre expérimental borné**.
- **C03-R02 : CLÔTURÉE — périmètre expérimental borné**.
- **C03-R03, C03-R04, C03-R05 et C03-R06 : OUVERTES**.
- **C03-3 global : OUVERT**, prototype reçu avec réserves.
- **G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 : OUVERTS** ; G03 préparation reçue avec réserves ; G05 global PARTIEL ; R1-C01 PARTIEL.
- **B6.5 : EN RECETTE ; G04, B6.3 et production : NO-GO**.

Aucun achat, fusion vers main, activation fournisseur, modification du site public ou autre chantier technique autorisé par la présente décision documentaire.

## Prochaine action unique

Confier au chat 02 une **priorisation documentaire d'une seule réserve parmi C03-R03 à R06**, avant tout nouveau GO de développement par le 00.
