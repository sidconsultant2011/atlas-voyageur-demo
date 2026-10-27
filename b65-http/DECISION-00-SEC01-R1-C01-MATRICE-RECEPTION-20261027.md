# 00 — SEC-01 R1-C01 — Réception ciblée de la matrice de conformité

**Date :** 27 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant cette décision :** `c4225283d741266e8f7ca7ef5f11b83838b9b967`  
**Autorité :** 00 — Pilotage et gouvernance

## Livrable remis et vérification de périmètre

Le chat 02 a remis au 00 le 27 octobre 2026 sa **Matrice détaillée de conformité R1-C01** (AC-01 à AC-14), en complément de la revue de sécurité et du mandat `b65-http/DECISION-00-SEC01-R1-C01-REVUE-CONTRAT-ATOMICITE-20261027.md`. Le document intégral a été reçu en conversation ; il n'est pas affirmé qu'un fichier autonome identique existe déjà sur GitHub.

Les chemins de code `b65-http/persistent_sessions.py` et `b65-http/local_identity_bridge.py` ont été vérifiés directement par le 00 lors de la réception de la revue précédente : `revoke()` met à jour `sessions.sqlite` avec `BEGIN IMMEDIATE` et renvoie 200 après sortie du contexte transactionnel ; `_persistent_journey()` utilise `ATTACH` de `identities.sqlite` et le contrôle d'autorisation dans la transaction. Les sources historiques R1, RD01 et la CI n°218 sont déjà référencées dans `b65-http/DECISION-00-SEC01-R1-C01-REVUE-RESULTAT-20261027.md`. Aucun test nouveau n'a été exécuté lors de la présente réception.

## Matrice reçue — synthèse opposable

| ID | Propriété | Statut documentaire reçu |
|---|---|---|
| AC-01 | Point logique unique de prise d'effet de révocation | Démontré — logique locale ; durabilité non prouvée |
| AC-02 | HTTP 200 après COMMIT normal | Démontré — ordre du code ; durabilité physique non prouvée |
| AC-03 | Autorisation et mutation sous sérialisation | Démontré — chemins locaux inspectés |
| AC-04 | Vérification session et identité dans transaction `ATTACH` | Démontré — structure de code ; récupération non prouvée |
| AC-05 | Refus après révocation confirmée | Démontré — scénarios reçus, non exhaustifs |
| AC-06 | Mutation légitime validée avant révocation | Démontré — scénario reçu, ordre de COMMIT inféré |
| AC-07 | Absence de réassociation automatique du pont après redémarrage | Démontré — prototype fictif local |
| AC-08 | Journalisation compatible multi-bases | Partiel — `DELETE/FULL` observés dans banc, non imposés partout |
| AC-09 | Compatibilité de stockage et d'environnement | Partiel — banc caractérisé, futur hébergement non qualifié |
| AC-10 | Reprise tout-AVANT ou tout-APRÈS après interruption | Partiel — 15 cas historiques / 5 marqueurs externes |
| AC-11 | Conservation de révocation confirmée après incident | Partiel — fonctionnement normal testé, panne non qualifiée |
| AC-12 | Refus sécurisé après incohérence détectée | Non démontré au niveau général |
| AC-13 | Gestion maîtrisée des erreurs SQLite à l'interface HTTP | Partiel — pas de retour 200 normal si exception, HTTP d'erreur non qualifié |
| AC-14 | Cohérence multi-hôtes indépendants | Non démontré ; hors périmètre local actuel, dépend d'un choix de topologie futur |

### Invariants utiles au contrat

- **Révocation HTTP mono-base** : après confirmation HTTP 200, la révocation doit rester opposable, notamment après redémarrage ; toute nouvelle opération protégée doit être refusée. La perte ultérieure de cette révocation est un état interdit.
- **Opérations du pont persistant avec `ATTACH`** : l'autorisation et la mutation se trouvent dans la même transaction ; un état n'est « partiel » que si des effets **effectivement liés par le contrat métier** ont été séparés. Une lecture en base sessions et une seule écriture en base identités ne constituent pas deux écritures contractuellement atomiques.
- **Fixture expérimentale RD01** : met explicitement à jour une révocation dans sessions et insère un parcours dans identities au sein d'une transaction témoin ; ne représente pas la révocation HTTP applicative.
- **Conditions SQLite** : l'utilisation d'`ATTACH` ne suffit pas à attester l'atomicité inter-fichiers ; fichiers, journal rollback/WAL, paramètres `synchronous`, stockage et topologie devront être vérifiés pour le déploiement envisagé.
- **Incohérence** : refuser par défaut les mutations protégées, sans divulgation et avec traitement maîtrisé des erreurs, est une **exigence à qualifier**, non une propriété actuellement certifiée.

## Arbitrage du 00

**GO — RÉCEPTION DOCUMENTAIRE DE LA MATRICE AC-01 À AC-14, avec verdict global R1-C01 : NON CONCLUANT.**

Cette réception reconnaît un livrable utile, **sans clôturer R1-C01, R1-RD01, R1 ou P0-01**, ni transformer une qualification statique ou locale en garantie générale après panne.

**Aucune nouvelle analyse générale de sécurité n'est demandée au chat 02. Aucun nouveau test ni changement de code n'est autorisé par cette décision.**

Le **seul chantier prioritaire déjà ouvert** demeure celui du chat **04 — Documentation**, chargé par `b65-http/DECISION-00-SEC01-R1-C01-REVUE-RESULTAT-20261027.md` de produire le contrat technique de configuration SQLite, d'atomicité et de reprise. Il doit **réutiliser** la matrice AC-01 à AC-14 reçue et le présent inventaire, sans répéter l'étude ni prétendre à une validation de préproduction. La rédaction complète du contrat reste une livraison distincte de la matrice de conformité.

## Statuts

- R1-C01 : **PARTIEL**, revue documentaire **NON CONCLUANTE**.
- R1-RD01, R1 et P0-01 : **OUVERTS**.
- C03-R01 à R04 : clôtures bornées au fictif expérimental ; C03-R05 ouverte et suspendue ; C03-R06 ouverte, lots 1 et 2 reçus.
- C03-3 global, G03-R01, VFS-R01 et G03-R06 : **OUVERTS**.
- B6.5 en recette ; G04, B6.3 et production : **NO-GO**.

## Prochaine action unique

Remettre au chat 04 la matrice AC-01 à AC-14 reçue afin qu'il produise le contrat documentaire de configuration SQLite et de reprise sécurisé déjà mandaté, sans nouveau test ni modification du code.
