# B6.5 — Qualification SQLite : interruptions brutales et intégrité

**Date : 24 octobre 2026. Périmètre : uniquement tests hors ligne sur fichiers SQLite temporaires.**

## Scénarios automatisés
Le fichier `b65-sqlite/test_sqlite_crash_qualification.py` ajoute quatre contrôles à la suite SQLite déjà branchée sur GitHub Actions :

1. Un processus enfant ouvre `BEGIN IMMEDIATE`, modifie le budget et insère une réservation, puis s'arrête brutalement via `os._exit(73)` **sans commit**. Après réouverture, les écritures doivent avoir été annulées : budget entier et réservation absente.
2. Un processus enfant valide une réservation, puis s'arrête brutalement via `os._exit(74)`. La réservation doit demeurer sur disque et une nouvelle ouverture doit reconnaître la même clé d'idempotence.
3. Une réservation laissée en attente expire après redémarrage logique. `recover_expired()` passe en `reconciliation_required` sans restituer le budget tant que la facturation ne peut pas être déterminée. La résolution explicite « non facturé » libère les crédits.
4. Une modification comptable incohérente mais respectant les contraintes SQLite est volontairement injectée. Le contrôle métier doit la détecter, même si `PRAGMA integrity_check` ne détecte aucune anomalie physique.

Chaque scénario vérifie `PRAGMA integrity_check`, `PRAGMA foreign_key_check`, la conservation du budget et la concordance entre les sommes comptables et les réservations. Les enfants sont isolés des autres processus et les données restent dans le dossier temporaire du test.

## Limites
Cela ne simule pas une coupure électrique de la machine, un crash noyau, une corruption physique du système de fichiers ni des stockages distants. `os._exit` termine un processus utilisateur, pas l'ordinateur ; la durabilité des écritures face à une panne d'alimentation nécessite tests matériels et réglages de synchronisation disque dédiés.

Il n'existe encore aucun service HTTP, aucun appel AeroDataBox/Geoapify, aucune authentification opérationnelle ni API réelle. Les réservations « à réconcilier » exigeraient ultérieurement un rapprochement officiel des débits fournisseurs et un journal d'audit dédié.

**B6.5 en recette — B6.3 NO-GO — aucun achat — aucune fusion main — site public inchangé — aucun test iPhone.**
