# B6.5 — Modèle de transactions multi-instances simulé
Date : 24 octobre 2026. **Prototype hors ligne, pas une base de données réellement persistante.**

## Architecture
`createTransactionStore()` représente une base transactionnelle partagée, conservée en mémoire pendant la vie du processus de test. Plusieurs instances `createTransactionalCreditService({store})` partagent ce même état. Une file de transactions sérialise les mutations et empêche de dépasser le budget sous `Promise.all`.

**Distinction cruciale :** le partage entre objets simulant des serveurs n'est pas une vraie persistance disque ni une atomicité inter-processus. Un redémarrage du processus effacerait le stockage. Les tests de « redémarrage » ne recréent que l'instance de service et conservent volontairement le store.

## Cycle financier
- `reserve(key,cost)` : réserver avant l'appel; refus si budget insuffisant ; clé d'idempotence unique.
- `settle(key,{charged:true})` : débiter définitivement, exactement une fois.
- `settle(key,{charged:false})` : libérer uniquement lorsque l'absence de facturation est établie.
- `recover()` : les réservations expirées passent en `reconciliation_required`, **sans restitution automatique**, pour éviter un sous-comptage si le fournisseur a déjà facturé.
- Un traitement de réconciliation manuelle/automatique avec données officielles du fournisseur est encore à concevoir avant réseau.

## Tests
9 tests : 100 réservations sur 4 instances simulées, doubles réservations même clé, collisions de clés, commit concurrent, remboursement unique, simulation de panne/reprise, état facturation inconnu, file après rejet, invariant de conservation des crédits.

Commande CI existante : `node --test b65-calculateur/*.test.mjs`.

## Prérequis production (non implémentés)
1. Stockage réellement durable (SQL transactionnel avec isolation et contraintes ou mécanisme équivalent).
2. Écritures conditionnelles atomiques entre processus et régions, résistantes aux coupures.
3. Idempotence durable avec contraintes uniques, statut `pending/settled/needs_reconciliation` et verrou de réconciliation.
4. Rapprochement facturation externe (unités consommées malgré timeout ou 5xx).
5. Expiration et maintenance des réservations orphelines, journaux d'audit, alertes et budgets plafond.
6. Tests d'intégration avec vrais processus et crashs de base, mais **sans fournisseur** avant un nouveau GO.

**B6.5 recette — B6.3 NO-GO — aucun achat — aucune fusion sur main — site public inchangé.**
