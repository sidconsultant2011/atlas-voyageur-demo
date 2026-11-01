# 00 — SEC-01 R1-C01 — Décision de maintien du gel technique

**Date :** 1er novembre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `68100568cfdec850affeef104e5031c7d71bdd2e`

## Pièces reçues et vérifications

Le chat 02 a remis en conversation sa synthèse indépendante intitulée **« 02 — SÉCURITÉ P0 — Consolidation des risques résiduels R1-C01 »**, datée du 1er novembre 2026. L'avis propose de **maintenir le gel des expérimentations R1-C01**. Cette synthèse n'est pas présentée comme un fichier autonome déjà publié dans GitHub.

Décisions officielles vérifiées directement dans GitHub :
- `b65-http/DECISION-00-SEC01-R1-C01-AC08-RECETTE-INDEPENDANTE-20261027.md` : AC-08 réceptionné dans le prototype local fictif, avec réserves.
- `b65-http/DECISION-00-SEC01-R1-C01-AC13-RECETTE-INDEPENDANTE-20261101.md` : AC-13 réceptionné dans le prototype local fictif, avec réserves.
- `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md` : contrat documentaire R1-C01 V1.1.

Preuves techniques déjà réceptionnées, **non réexécutées dans cette consolidation** :
- AC-08 : CI n°238, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40587946581 ; commit `eb97c24eb969b2a28f4276b1c489d7eb46a6c6a4`, 288 exécutions dont 8 tests ciblés.
- AC-13 : CI n°247, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/41342824300 ; commit `8ddd7678c0d23ae7c8e53af4104d0c139042397d`, 295 exécutions dont 7 tests ciblés.
- Les échecs intermédiaires CI n°236 et n°246 restent dans l'historique. Aucun nouvel essai local, test CI, campagne de panne ou modification du code n'a été réalisé pour la synthèse du chat 02.

## Constat de sécurité

Les acquis expérimentaux réceptionnés couvrent, dans le périmètre testé :
1. La révocation logique transactionnelle, le contrôle d'autorisation et les refus après révocation dans les scénarios R1 réceptionnés.
2. La configuration contrôlée des bases fictives en `journal_mode=DELETE` et `synchronous=FULL`, le refus de configurations incompatibles et le contrôle préalable des fichiers avant `ATTACH` (AC-08, avec réserves).
3. Les réponses HTTP 503 structurées pour `SQLitePreconditionError` et `sqlite3.Error`, sans divulgation de détails SQLite, sans succès métier trompeur et sans réessai automatique dans les cas synthétiques (AC-13, avec réserves).

Garanties **non démontrées** :
- Récupération d'une transaction lors d'une interruption interne du COMMIT SQLite, notamment lorsqu'une atomicité entre effets multi-bases est réellement exigée.
- Durabilité physique après panne OS, disque, perte d'alimentation et conservation garantie d'une révocation déjà confirmée.
- État final de la mutation lorsque l'issue du COMMIT est ambiguë, ou résultat réellement reçu par le client en cas de rupture réseau.
- Stratégie générale de détection/quarantaine/récupération d'un état persistant incohérent.
- Protection exhaustive des chemins symboliques, résistance au remplacement concurrent du fichier avant `ATTACH`, maîtrise des clients SQLite externes et coordination inter-hôtes.

Les réserves sont des **risques et limites de preuve**, et ne sont pas assimilées à des incidents effectivement observés ou à une démonstration de corruption.

## Décision officielle du 00

**GO — RÉCEPTION DE LA SYNTHÈSE DOCUMENTAIRE DE SÉCURITÉ DU CHAT 02.**

**MAINTIEN DU GEL TECHNIQUE R1-C01 : AUCUN NOUVEAU CHANTIER EXPÉRIMENTAL IMMÉDIAT.**

AC-08 et AC-13 restent **réceptionnés avec réserves, pour le prototype fictif local uniquement**. Les travaux ciblés sont terminés et ne doivent pas être recommencés.

La reprise d'une qualification de récupération ou toute extension de sécurité devra être arbitrée **séparément** par le 00, sur la base d'une architecture d'exploitation cible, d'une nécessité produit explicite, d'hypothèses de stockage/topologie vérifiables et d'une comparaison avec les alternatives les plus simples. **Aucun GO implicite** n'est accordé pour étude d'architecture, nouveau code, essais supplémentaires, instrumentation VFS, SIGKILL, campagne C03 ou G04.

Le gel du développement R1-C01 **ne constitue pas** une acceptation des risques pour de vraies identités, sessions ou données personnelles, ni une autorisation de commercialisation ou de production.

## Statuts inchangés

- AC-08 : **réceptionné avec réserves**, périmètre local fictif.
- AC-13 : **réceptionné avec réserves**, périmètre local fictif.
- R1-C01 : **PARTIEL**, qualification globale après panne **NON CONCLUANTE**, gel technique maintenu.
- R1-RD01, R1 et P0-01 : **OUVERTS**.
- C03-R05 : **OUVERT, suspendu** ; C03-R06 : **OUVERT** (lots 1 et 2 reçus) ; autres réserves C03/G03/VFS non levées.
- B6.5 : **EN RECETTE** ; B6.3, G04 et production : **NO-GO**.

Aucune fusion vers `main`, modification du site public, activation de fournisseur réel, achat, migration ni déploiement n'est autorisé.

## Prochaine action unique

Conserver cette décision comme référence de gouvernance du 00, **sans ouvrir de nouveau chantier technique R1-C01** tant que l'architecture cible et les critères de nécessité n'ont pas fait l'objet d'un arbitrage distinct.
