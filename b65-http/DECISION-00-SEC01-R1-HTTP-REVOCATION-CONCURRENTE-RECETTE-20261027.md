# 00 — SEC-01 R1 — Réception indépendante ciblée de la révocation HTTP concurrente

**Date :** 27 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `8ea2b7b9713cced84c2b9702d7937772fa075010`  
**Décideur :** 00 — Pilotage et gouvernance.

## Sources et preuves

- PV indépendant du chat 03 remis au 00 le 27 octobre 2026 : `PV-03-SEC01-R1-HTTP-CONCURRENT-20261027`, verdict **réception favorable avec réserves**. Le présent dépôt n'est pas présenté comme hébergeant un PV autonome du chat 03.
- Mandat de qualification : `b65-http/DECISION-00-SEC01-R1-HTTP-REVOCATION-CONCURRENTE-20261027.md`.
- Rapport du chat 01 : `b65-http/SEC01-R1-HTTP-REVOCATION-CONCURRENTE-PREUVES-20261027.md`.
- Réception technique préalable : `b65-http/DECISION-00-SEC01-R1-HTTP-REVOCATION-CONCURRENTE-RECEPTION-20261027.md`.
- Code de test exact : `b65-http/test_sec01_r1_http_concurrent.py` au commit `880c7f9cbf324ea54cff85dbdaaeb02c50a0b460`.
- CI n°218 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40479880801 ; `completed/success` sur ce même commit.
- Contrôle direct des journaux GitHub Actions par le 00 : 116/116 tests JavaScript, 11/11 SQLite, 153/153 HTTP, identité et sécurité ; les deux tests de `test_sec01_r1_http_concurrent.py` sont présents dans la suite réussie. Soit 280 **exécutions** réussies, non 280 scénarios distincts.
- Diff déjà vérifié à la réception technique : ajout de deux fichiers (tests et rapport), aucun changement applicatif, VFS C, C03, moteur SQLite ni workflow.
- **Tests locaux du commit exact non exécutés** selon le rapport 01 ; aucun nouveau test local ni CI exécuté par 03 ou 00.

## Résultat indépendant reçu

**Scénario A.** La mutation HTTP protégée détient `BEGIN IMMEDIATE` avant la révocation ; un second écrivain SQLite reçoit `database is locked` ; après libération, HTTP mutation **201**, révocation **200**, la base `sessions` est marquée révoquée et la mutation métier légitime figure dans `identities`. Mutation supplémentaire après révocation : **401**.

**Scénario B.** La révocation détient `BEGIN IMMEDIATE` ; deux mutations entrent dans le contrôle `state.check` pendant la retenue transactionnelle, mais n'ont pas acquis leurs propres verrous. Après la révocation HTTP **200**, les deux mutations répondent **401**, sans nouvelle ligne métier. Nouvelle connexion : **401**. Les bases sont relues indépendamment.

**Réserves probatoires.** `BarrierState` n'est qu'une sous-classe de test. Le témoin SQLite confirme la contention, mais les COMMIT individuels ne sont pas enregistrés par des sondes natives ; l'ordre est inféré du verrouillage et du code. Les événements de `state.check` ne mesurent pas les arrivées réseau. Cette recette limitée ne qualifie pas tous les entrelacements, les écritures physiques, la durabilité, la récupération après panne ou les hôtes indépendants.

## Décision officielle du 00

**GO — RÉCEPTION INDÉPENDANTE CIBLÉE DE LA QUALIFICATION HTTP CONCURRENTE R1, AVEC RÉSERVES.**

Cet acquis confirme le comportement attendu dans **deux scénarios déterministes du prototype fictif SQLite local**. Il complète les preuves R1-C02, R1-C05 et R1-C06 dans ce périmètre, sans constituer une nouvelle réception globale de R1.

**R1-C01 demeure PARTIEL ; R1-RD01, R1 et P0-01 restent OUVERTS.** Les six autres critères R1-C02 à R1-C07 conservent leur réception historique locale, non élargie.

La suspension des nouvelles extensions C03/G03-R01 reste applicable. Pas de nouvelle campagne C03, `BEFORE_DELEGATE`, test de panne, SIGKILL ou G04 sans nouvel arbitrage. Aucune fusion main, publication, activation réelle, déploiement ni production autorisée.

## Gouvernance et prochaine priorité

- C03-R01 à R04 : clôturées dans leurs seuls périmètres expérimentaux fictifs.
- C03-R05 : ouverte, qualification temporelle suspendue.
- C03-R06 : ouverte, lots 1 et 2 reçus.
- C03-3 global, G03-R01, VFS-R01, G03-R06 : ouverts.
- B6.5 en recette ; B6.3, G04, production : NO-GO.

Le contrôle concurrent HTTP est **réceptionné et terminé**. Pour éviter une prolongation technique automatique, le prochain travail doit d'abord être **documentaire** : définir, à partir des besoins produit, une stratégie de qualification du risque résiduel R1-C01 relatif à la reprise et à la cohérence lors d'une panne du COMMIT multi-bases. Comparer les options sans préjuger de la nécessité de VFS ou autoriser une campagne de panne. Clarifier le risque effectivement bloquant pour P0-01.

## Prochaine action unique

Demander au chat 02 un avis documentaire sur le risque R1-C01 encore partiel et sur les moyens proportionnés de le qualifier, sans code ni tests nouveaux avant arbitrage du 00.
