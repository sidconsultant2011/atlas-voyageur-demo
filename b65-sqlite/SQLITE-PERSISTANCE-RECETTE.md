# B6.5 — SQLite durable hors ligne — recette

Date : 24 octobre 2026. **Prototype réel sur disque, aucun fournisseur ni serveur HTTP.**

## Réalisation
- `b65-sqlite/sqlite_credit_ledger.py` : SQLite standard Python, fichier persistant local. `BEGIN IMMEDIATE` protège lecture et mutation d'un budget global, `UPDATE ... WHERE available>=cost` évite le dépassement. Clés d'idempotence uniques, confirmation/remboursement unique, `CHECK` comptable.
- `b65-sqlite/test_sqlite_credit_ledger.py` : tests de réouverture de base, concurrence sur **16 processus séparés** avec budget de 20 crédits et demandes de 2 crédits, règlement unique, restitution unique, reprise des réservations expirées sans remboursement arbitraire, collisions de clés, budget incohérent.
- Le workflow GitHub Actions déclenche maintenant `python3 -m unittest discover -s b65-sqlite -p 'test_*.py' -v` et conserve les tests Node B6.5 existants. Aucune dépendance pip et aucun appel réseau.

## Limites
- « Multi-processus » correspond à plusieurs processus sur **la même machine et le même fichier SQLite**. Ce n'est PAS une base partagée entre plusieurs instances serverless ou hôtes distants ; SQLite local ne peut pas devenir à lui seul une base transactionnelle multi-région.
- Les transactions et données persistent lors du redémarrage d'un processus si le fichier disque reste accessible.
- Les interruptions après appel à un fournisseur mais avant confirmation exigeraient un mécanisme de rapprochement avec sa facturation. Une réservation expirée passe en `reconciliation_required` et demeure provisionnée.
- Le débit, les verrouillages, l'idempotence temporelle, la rotation du stockage, sauvegardes, crash-consistency/PRAGMA et les erreurs I/O disque n'ont pas encore de qualification pour exploitation commerciale.
- Test actuellement limité aux opérations comptables : aucun service HTTP, aucune connexion à Geoapify ou AeroDataBox.

## Politique
B6.5 recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur main ; site public inchangé ; aucun test iPhone.
