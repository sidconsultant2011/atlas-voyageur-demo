# SEC-01 R1 — Rapport technique partiel pour recette 03

Date : 25 octobre 2026. Environnement : prototype fictif local SQLite, sans fournisseur externe.

## Références
- Décision 00 : `b65-http/DECISION-00-SEC01-R1-CRITERES-20261025.md`
- Base avant changements : `1f2d7c5a44a05ee73ef8806773b66e6ef754f181`
- Correctif `persistent_sessions.py` : `975b94df1c87e6724c2bae1fa43789dc0d0ec298`
- Tests ajoutés `test_sec01_r1_atomic.py` : `36c7e1a77d4ee1bd42dd261b35873ab18e39c30f`
- Correctif du pont d'identité sur deux bases SQLite attachées : `03215f0fe5ffe4dd6329975be7b191a910cca6b2`
- Tests déterministes supplémentaires du pont : `70375c234032337493dc7addc9f23e1e4e0674f8`
- CI initiale : [GitHub Actions n°75](https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40179663703), commit `36c7e1a77d4ee1bd42dd261b35873ab18e39c30f`, completed / success.
- CI avec pont transactionnel et tests complémentaires : [GitHub Actions n°78](https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40179873955), commit `70375c234032337493dc7addc9f23e1e4e0674f8`, completed / success.

## Mécanisme
Le chemin persistant du pont d'identité utilise également `ATTACH DATABASE` avant `BEGIN IMMEDIATE` : les écritures `identity_journeys` et le contrôle de la session dans `sessions` participent à une même transaction SQLite locale. Cela suppose des bases sur le même système de fichiers local et un journal SQLite compatible avec les transactions multi-bases ; aucune garantie distribuée n'est revendiquée.

Le prototype `PersistentSessionState` utilise désormais `BEGIN IMMEDIATE` pour la validation de session et les effets SQL des mutations create/update/delete ; `revoke` effectue la validation CSRF et l'UPDATE du drapeau `revoked` dans la même transaction. Le point de prise d'effet est le COMMIT de la révocation. Une mutation engagée et commitée avant ce point peut renvoyer sa réponse plus tard. Une mutation commencée après ce COMMIT est refusée. Les verrous SQLite opèrent entre connexions et processus d'une même base locale.

Les contrôles de quota, expiration, CSRF et propriété sont maintenus dans les méthodes concernées. Le contrôle de quota demeure transactionnel. L'API et le protocole HTTP existants ne sont pas modifiés.

## Tests réellement observés
GitHub Actions n°78 :
- JavaScript : 116/116 réussis.
- SQLite (suite distincte) : 11/11 réussis.
- HTTP/identité via découverte unittest : 90 exécutions réussies, incluant 7 nouveaux tests R1.
- Total de 217 exécutions de tests ; les classes découvertes/importées peuvent être répétées : ce chiffre ne désigne pas 217 scénarios uniques.
- Tests locaux depuis l'environnement ChatGPT : **non exécutés**, accès Git distant du conteneur indisponible.

Nouveaux tests R1 : deux tests supplémentaires couvrent le pont SQLite attaché, les mutations d'identité avant et après révocation, et le verrouillage déterministe pendant une écriture. En outre : interdiction de créer/modifier/supprimer après révocation ; propriété croisée ; transaction de modification tenue avant COMMIT de révocation via Events ; connexion SQLite réouverte ; processus séparé après révocation, lecture SQL des effets.

## État par critère et réserves
- R1-C01 : contrat de point de COMMIT décrit pour `PersistentSessionState`, **partiel**.
- R1-C02 : mutation bloquée/sérialisée vérifiée dans la voie persistante, **partiel**.
- R1-C03 : validation et mutation dans `BEGIN IMMEDIATE` sur SQLite persistant, y compris pont utilisant deux bases attachées, **démontré par code et CI sur ce périmètre**.
- R1-C04 : assertions de propriété et des trois mutations, dont le pont d'identité ; entrelacement forcé sur update, **couverture concurrente create/delete encore incomplète**.
- R1-C05 : refus post-révocation dans la voie persistante ; HTTP testé par régression, **preuve d'entrelacement HTTP déterministe R1 encore incomplète**.
- R1-C06 : test multiprocessing après COMMIT ; manque encore d'entrelacement forcé interprocessus **avant** COMMIT.
- R1-C07 : non-régression CI réussie, aucune réassociation implicite testée dans suite historique ; absence de preuve d'atomicité inter-bases.

### Limites restantes
Le chemin pont d'identité SQLite attaché fournit désormais la sérialisation transactionnelle locale des mutations ; le pont utilisant `LocalState` en mémoire reste volontairement distinct et hors de ce contrat persistant. Les tests ne couvrent pas encore l'ensemble des entrelacements forcés create/delete, ni la coordination interprocessus pendant une transaction d'identité en cours. Pas de preuve de résistance aux pannes pendant le COMMIT multi-fichiers, ni de garantie si WAL est activé ou si les bases résident sur des systèmes de fichiers différents. Ne pas présenter R1 comme clôturée ni extrapoler les garanties SQLite à plusieurs hôtes, TLS ou production.

## Gouvernance
**R1 OUVERTE — P0-01 OUVERT — B6.5 en recette — production NO-GO.** Aucune fusion vers main ni publication. La réception indépendante du chat 03 reste requise, ainsi que la qualification indépendante du chemin d'identité et la couverture déterministe complémentaire.
