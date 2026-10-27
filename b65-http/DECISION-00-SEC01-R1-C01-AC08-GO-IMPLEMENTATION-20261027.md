# 00 — SEC-01 R1-C01 — GO implémentation ciblée AC-08

**Date :** 27 octobre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `1fde81199cb1ff5f700e7f5e4021df4c6592ccbb`.

## Sources et constat

- Cadrage 01 reçu et relu : `b65-http/SEC01-R1-C01-AC08-CADRAGE-TECHNIQUE-20261027.md`. Commit `1fde81199cb1ff5f700e7f5e4021df4c6592ccbb` : **un document ajouté, aucun code modifié**.
- Décision de priorité : `b65-http/DECISION-00-SEC01-R1-C01-AUDIT-STATIQUE-AC08-20261027.md`.
- Contrat cible version 1.1 : `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md`.
- Modules concernés : `b65-http/persistent_sessions.py`, `b65-http/fictional_identities.py`, `b65-http/local_identity_bridge.py`.
- AC-08 : l'imposition et la vérification systématiques des paramètres de journalisation, synchronisation et certaines préconditions de stockage ne sont pas démontrées dans le code applicatif actuel. Aucun incident de corruption ni de perte de révocation n'est attesté.

## Décision

**GO — DÉVELOPPEMENT ET TESTS CIBLÉS AC-08 SUR LA BRANCHE AUTORISÉE.** Le chat 01 est autorisé à implémenter la **préparation contrôlée puis la vérification avec refus en cas de non-conformité** des paramètres `journal_mode=DELETE` et `synchronous=FULL` pour les bases fictives sessions et identités et le chemin `ATTACH`. Aucun autre chantier technique n'est ouvert.

### Exigences impératives

1. **Périmètre de code réduit** : `persistent_sessions.py`, `fictional_identities.py`, `local_identity_bridge.py` et éventuellement un petit utilitaire SQLite commun seulement si le gain de cohérence justifie l'ajout. Aucun changement de fonctionnalité métier.
2. **Initialisation des nouvelles fixtures fictives** : établir la configuration hors transaction, avant admission de requêtes et sans concurrence ; vérifier les réponses effectives des PRAGMA, ne jamais présumer leur succès.
3. **Bases préexistantes** : inspecter avant toute écriture de reconfiguration ; si mode journal ou topologie incompatible, **refuser** la connexion protégée/admission, ne pas migrer automatiquement, ne pas convertir WAL silencieusement. Préserver les données préexistantes.
4. **Connexions** : sur chaque connexion protégée, vérifier `journal_mode`, établir et vérifier `synchronous=FULL` comme propriété de connexion si admissible ; conserver `busy_timeout` et `foreign_keys=ON`.
5. **Pont attaché** : après `ATTACH`, avant `BEGIN IMMEDIATE`, contrôler aliases et chemins, modes journal et niveaux de synchronisation effectifs de `main` et `identity_db`. Aucune mutation sur configuration non conforme.
6. **Préconditions de stockage** : exclure `:memory:` pour la propriété multi-fichiers revendiquée ; identifier les limites de vérification des chemins, périphériques, support de stockage et système de fichiers, sans confondre `st_dev` et garantie physique. Ne pas promettre une durabilité générale ou un support inter-hôtes.
7. **Défaillance de configuration** : mode d'échec explicite au démarrage ou à l'admission, sans mutation protégée et sans faux succès. Préserver les diagnostics sans secrets ; ne pas introduire un traitement HTTP général des exceptions SQLite relevant d'AC-13.
8. **Préservation** : maintenir les comportements fictifs existants et les frontières transactionnelles R1. Éviter les changements de journaux pendant une transaction ou un trafic concurrent. Les bases historiques non conformes restent bloquées, sans action intrusive.
9. **Contrôles** : mettre en place les tests ciblés de conformité et d'échec sécurisé AC-08, puis exécuter les suites de non-régression pertinentes. Distinguer résultats **locaux** et **GitHub Actions**, avec commit exact, commandes et preuve. Vérifier la conclusion réelle du workflow `.github/workflows/b65-calculateur-tests.yml` avant toute déclaration de succès. Documenter les fixtures, changements et limites.
10. **Livraison** : rapport technique borné au chat 00 avec diff, commits, tests et régressions éventuelles. **Aucun GO de recette indépendante ou de production n'est automatique** après un résultat technique favorable.

### Interdictions

Aucune modification de `main`, fusion, publication, site public, fournisseur réel, achat, donnée personnelle réelle ni secret. Aucun correctif AC-13, migration automatique de bases préexistantes, changement d'architecture, SIGKILL, injection de panne, instrumentation VFS/`BEFORE_DELEGATE`, extension C03 ni G04. Toute anomalie nécessitant un élargissement du périmètre doit être remontée au 00 avant correction.

## Statuts conservés

- AC-08 : **GO d'implémentation, non encore implémenté ni validé** au moment de la décision.
- AC-13 : écart contractuel attesté, hors chantier actif.
- R1-C01 : **PARTIEL** ; R1-RD01, R1 et P0-01 **OUVERTS**.
- B6.5 **EN RECETTE** ; B6.3, G04 et production **NO-GO**.
- C03-R05 ouverte et suspendue ; C03-R06 ouverte ; aucun GO sur les extensions C03.

## Prochaine action unique

Faire exécuter par le chat 01 le correctif AC-08 et les tests ciblés autorisés sur la branche, puis remettre au 00 le résultat technique sourcé sans ouvrir AC-13.
