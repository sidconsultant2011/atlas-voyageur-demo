# B6.5 — Réservations atomiques de crédits et concurrence — recette hors ligne

Date : 24 octobre 2026. **Spécification et code de simulation seulement. Aucun fournisseur connecté.**

## Livrables
- `credit-ledger.mjs` : compteur en mémoire, réservation synchrone avant toute opération asynchrone, validation du coût entier, clé d'idempotence, commit, remboursement unique et arrêt dur si capacité insuffisante.
- `credit-ledger.test.mjs` : 9 tests ; doubles réservations simultanées, 100 demandes concurrentes, idempotence, conflits, validation coûts, commit unique, remboursement unique, inconnus.
- Le workflow GitHub Actions B6.5 existant inclut automatiquement `b65-calculateur/*.test.mjs`.

## Invariants
`available + reserved + committed === limit`, et les trois quantités sont positives ou nulles.
Une réservation est effectuée **avant tout await**, donc atomique uniquement dans un même event loop JavaScript.
Aucune opération ne dépasse le plafond ; les mêmes clés ne déboursent pas deux fois.
Un échec non facturé restitue le crédit une seule fois. En cas de facturation incertaine, **ne pas rembourser sans rapprochement fournisseur**.

## Limites avant réseau
**Ce code ne garantit PAS l'atomicité entre plusieurs processus, instances serverless ou redémarrages.** Pour une vraie façade : persistance transactionnelle (SQL avec contrainte de solde et ligne de réservation verrouillée / mise à jour conditionnelle, ou Redis avec script atomique correctement configuré), clés d'idempotence persistantes, expiration/compensation des réservations orphelines, budget global et par session, tolérance aux crashes, audit comptable, rapprochement des unités réellement facturées et retries encadrés.

Les appels facturés malgré des erreurs HTTP ne peuvent pas être automatiquement « remboursés » ; le statut doit être résolu via fournisseur. Les tarifs peuvent varier par endpoint/tier et une réservation doit couvrir le coût maximal prévu avant exécution.

## Garde-fous
Pas de clé API, pas de fetch, pas de serveur HTTP, pas de déploiement, pas de changement de UI ni branche principale.

**B6.5 en recette — B6.3 NO-GO — aucun achat — aucune fusion main — site public inchangé.**
