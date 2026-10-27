# 00 — SEC-01 R1-C01 — Réception de l'audit statique et priorité AC-08

**Date :** 27 octobre 2026  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `31e43238c9cc4b0f58637e8ffd609a2b503f9c53`  
**Autorité :** 00 — Pilotage et gouvernance.

## Pièces et contrôles

- Compte rendu du chat 02 remis au 00 le 27 octobre 2026 : audit statique R1-C01, matrice AC-01 à AC-14, préconisation **AC-08** prioritaire. Le compte rendu existe en conversation ; son enregistrement autonome dans GitHub n'est pas affirmé.
- Contrat documentaire V1.1 : `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md` ; réception : `b65-http/DECISION-00-SEC01-R1-C01-CONTRAT-V11-RECEPTION-20261027.md`.
- Mandat de l'audit statique : `b65-http/DECISION-00-SEC01-R1-C01-CONTRAT-V1-RECEPTION-20261027.md`.
- GitHub consulté directement au HEAD indiqué. `b65-http/persistent_sessions.py:19-22` : `sqlite3.connect(self.path,timeout=10)` et `PRAGMA busy_timeout=10000`, sans imposition explicite de `journal_mode` ou `synchronous`.
- `b65-http/fictional_identities.py:17-18` : connexion SQLite et `PRAGMA foreign_keys=ON` ; pas d'imposition explicite des préconditions AC-08.
- `b65-http/local_identity_bridge.py:74-76` : `ATTACH DATABASE` puis `BEGIN IMMEDIATE` pour le pont persistant.
- `b65-http/local_http_facade.py:110-115` : appel `state.revoke()` puis réponse HTTP ; aucune gestion spécifique des erreurs SQLite/COMMIT dans ce segment.
- Les tests historiques de CI n°218 et RD01 n°90 sont des preuves **datées et bornées**, non rejouées pendant cet audit. Aucun test local/CI nouveau ni modification applicative dans ce chantier.

## Décision 00 — Réception de l'audit

**RÉCEPTION DOCUMENTAIRE FAVORABLE DE L'AUDIT STATIQUE ; R1-C01 RESTE PARTIEL.**

La conformité logique AC-01 à AC-07 demeure limitée à ses preuves précédemment réceptionnées. Écarts au contrat cible attestés : **AC-08**, préconditions de journalisation/synchronisation/stockage non systématiquement imposées ou vérifiées par le code ; **AC-13**, absence de traitement explicite et uniforme des erreurs SQLite/COMMIT aux chemins HTTP examinés. AC-09 à AC-11 demeurent partiels ; AC-12 non démontré ; AC-14 hors topologie locale actuelle, sans garantie distribuée future.

Les écarts n'attestent **ni panne réelle, ni corruption, ni perte de révocation observée**. La récupération après interruption interne d'un COMMIT multi-bases n'est pas qualifiée.

## Arbitrage AC-08 — Une seule priorité active

**GO DE CADRAGE TECHNIQUE AC-08 UNIQUEMENT**, confié au chat 01 — Développement et intégrations, **sans autorisation de modifier le code ou de lancer des tests**.

Objet de la note de cadrage :
1. Vérifier HEAD et règles applicables, puis inventorier les connexions SQLite du vrai chemin persistant, par base, distinguer mono-base et `ATTACH`, ainsi que toute couverture existante.
2. Énoncer les propriétés SQLite et hypothèses documentées nécessaires au prototype local : mode rollback approprié, compatibilité du mode WAL avec l'atomicité inter-fichiers revendiquée, `synchronous`, base principale sur disque, fichiers et topologie de stockage. Ne pas fixer de paramètres à l'aveugle ni promettre la durabilité matérielle.
3. Proposer la **modification minimale**, avec compatibilité et stratégie de refus d'une configuration incompatible, traitement des connexions déjà ouvertes, impacts sur fixtures/tests, et maîtrise des régressions ; privilégier une proposition sans changement d'architecture.
4. Définir les vérifications falsifiables qui seraient nécessaires en cas de GO technique ultérieur, avec distinction des tests locaux et CI et de leur commit exact. **Ne pas les exécuter à ce stade.**
5. Livrer au 00 une seule proposition de réalisation AC-08, avec fichiers, risques, limites et coût de complexité.

**AC-13 n'est pas un second chantier autorisé.** Le traitement des erreurs reste un écart connu à prioriser séparément ultérieurement par le 00.

### Exclusions

Aucun développement, changement SQLite, migration, correctif HTTP, test, GitHub Actions, injection de panne, SIGKILL, instrumentation VFS/`BEFORE_DELEGATE`, extension C03, G04, fournisseur réel, fusion main, publication ou déploiement n'est autorisé par la présente décision.

## Statuts

- AC-08 : écart de conformité contractuelle attesté, cadrage autorisé, **non corrigé et non validé**.
- AC-13 : écart de conformité contractuelle attesté, hors chantier actif.
- R1-C01 : **PARTIEL** ; R1-RD01, R1, P0-01 : **OUVERTS**.
- C03-R01 à R04 : clôtures fictives ciblées ; C03-R05 ouverte/suspendue ; C03-R06 ouverte (lots 1 et 2 reçus).
- C03-3 global, G03-R01, VFS-R01, G03-R06 : ouverts.
- B6.5 : en recette ; B6.3, G04, production : **NO-GO**.

## Prochaine action unique

Transmettre au chat 01 le mandat de **cadrage AC-08 sans implémentation**, puis soumettre au 00 sa proposition technique avant tout GO de correction.
