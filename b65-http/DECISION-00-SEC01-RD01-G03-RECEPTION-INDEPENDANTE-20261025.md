# Décision 00 — SEC-01 R1-RD01 — Transmission en recette indépendante G03

**Date :** 25 octobre 2026
**Projet :** ATLAS VOYAGEUR — B6.5
**Branche de travail :** `feature/b6-5-cartographie-interactive`
**HEAD vérifié avant décision :** `aa55c249f977a1c4b7612977cd8c434d5f7ea126`
**Chantier prioritaire unique :** réception indépendante de la préparation probatoire G03.

## Sources et constats directement vérifiés par le 00

- Mandat : `b65-http/DECISION-00-SEC01-RD01-G03-PREPARATION-20261025.md`.
- Rapport du chat 01 : `b65-http/SEC01-RD01-G03-PREPARATION-PREUVES-20261025.md`.
- GitHub Actions n°116 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40207400841 ; **completed / success**.
- Commit effectivement testé : `86de3e07621c68b4e24e80e94f12982e2cd7c621`.
- CI : **116/116 JavaScript, 11/11 SQLite, 96/96 HTTP/identité**, soit 223 exécutions réussies, pas nécessairement des scénarios distincts.
- Diff comparé depuis `76e7dbc3c7541852ab9c9ab6282f13ef4f5a4d44` : quatre fichiers changés, `b65-http/rd01-vfs-step1/g03_trace_analysis.py` (ajout), `b65-http/rd01-vfs-step1/rd01_vfs_step1.py`, `b65-http/test_rd01_vfs_step1.py` (modifiés), rapport G03 ajouté. **Wrapper C et code applicatif inchangés**.
- Ligne de journal CI `RD01 G03 NORMAL COMMIT TRACE` : 128 événements ; candidat super-journal `sessions.sqlite-mj0E9BEA920` ouvert à la séquence 80 et `xDelete` sur même basename à la séquence 116 avec code retour 0 ; les deux bases fictives observées.
- Le rapprochement est **par nom tronqué et ordre dans une même trace**, non par identité complète de handle et de transaction. La trace `xDelete` est émise **après** retour de la VFS native.
- Limites déclarées dans la preuve : `before_after_delegate_proven=false`, `commit_internal_phase_proven=false`, `transaction_id_proven=false`, `durability_proven=false`.
- **Aucun essai SIGKILL, interruption, suspension ou injection ; aucun nouveau test local du commit final n'est rapporté par le chat 01.** Seule la CI a été vérifiée pour le commit final.

## Décision du 00

**Livraison technique de la préparation G03 : ACCEPTÉE POUR RECETTE INDÉPENDANTE DU CHAT 03.**

L'observation d'un `xOpen` candidat super-journal puis d'un `xDelete` réussi sur le même nom pendant un COMMIT normal est acquise comme **preuve de corrélation technique sur le banc fictif**, sous réserve de l'avis indépendant du 03.

**Aucun GO pour une nouvelle instrumentation probatoire** (émission pré-délégation, identifiant transactionnel, synchronisation des traces, modification du wrapper) avant recette 03 puis arbitrage séparé du 00.

**G04 NO-GO** : aucun SIGKILL, crash, suspension dans callback VFS, arrêt causal, interruption interne de COMMIT, panne OS ou panne physique autorisés par cette décision.

## Mandat au chat 03 — Recette indépendante

1. Lire `g03_trace_analysis.py`, le banc et les assertions de `test_rd01_vfs_step1.py` au commit testé ; confronter leurs mécanismes aux traces CI n°116.
2. Qualifier précisément la preuve séquence 80 / 116 : ouverture avec flag super-journal candidat, suppression sur même basename, retour 0 ; distinguer corrélation et preuve du point logique de validation.
3. Vérifier que les limites sont réellement représentées par les assertions, notamment post-délégation, nom tronqué, absence d'ID transactionnel, ordre séquentiel mono-processus non protégé, trace non synchronisée, surface VFS V1 et effet observateur.
4. Vérifier que le code applicatif est inchangé et que les suites CI sont bien rattachées au commit `86de3e07`, et non au commit documentaire final.
5. Rendre un **PV indépendant G03 préparation** : acquis recevables, preuves et réserves, conditions bloquantes pour envisager une instrumentation future ; signaler tout résultat non attesté. Aucune nouvelle campagne de panne ni modification demandée.

## Statuts maintenus

G01 recevable pour le runtime CI, G02 recevable pour le banc fictif, G05 archivage de fichiers propres reçu et conservé, **G05 global partiel**. **G03 en préparation, non qualifiée pour l'arrêt interne ; G04 NO-GO.** VFS-R01 à R05 et RD01-R01 à R04 ouvertes ; **R1-RD01 OUVERTE, R1-C01 PARTIEL, R1 OUVERTE, P0-01 OUVERT, B6.5 EN RECETTE, B6.3 NO-GO, PRODUCTION NO-GO**.

## Prochaine action unique

Transmettre au chat 03 ce mandat et le rapport G03 rattaché aux journaux de GitHub Actions n°116, pour procès-verbal indépendant avant tout nouvel arbitrage technique.
