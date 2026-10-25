# ATLAS VOYAGEUR — B6.5 — SEC-01 — Cycle de vie du pont d'identité
Date : 25 octobre 2026. **QA uniquement ; boucle locale 127.0.0.1 ; aucune API fournisseur.**

## Correctif
- `local_identity_bridge.py` n'autorise plus une association sur simple présence d'une chaîne cookie et d'un jeton d'identité valide : `bind_fixture` exige une session HTTP active, contrôlée côté état serveur, puis revérifiée avant stockage de l'association.
- Chaque opération propriétaire (`create/read/update/delete`) vérifie à nouveau que la session HTTP est active ET que le jeton d'identité fictive est toujours valide. Toute association périmée est inutilisable.
- `local_http_facade.py` expose une validation sans consommation de quota (`LocalState.is_active_session`), ajoute une révocation effective en mémoire `LocalState.revoke`, supprime l'association du pont après révocation et injecte la validation de session dans le pont.
- `persistent_sessions.py` fournit la validation read-only de l'état SQLite, y compris expiration/révocation.
- Les associations du pont restent **exclusivement en mémoire** : un nouveau pont créé après redémarrage ne retrouve aucune autorisation préalable, même si la session QA persiste sur disque. Aucune liaison automatique sans nouvelle validation explicite du banc d'essai.

## Réception
`test_local_identity_bridge.py` ajoute les scénarios : cookie forgé avec vrai jeton d'identité, révocation HTTP, expiration via horloge fictive, nouveau pont après redémarrage sans autorisations héritées. Les tests historiques d'IDOR, cookie CSRF et propriété demeurent dans le workflow B6.5.

## Limites
La validation read-only et l'opération métier peuvent être séparées dans le temps ; ce mock ne constitue pas un verrouillage distribué et ne garantit pas une révocation atomique inter-hôtes. Aucun login humain, aucun TLS, aucune identité commerciale, aucun fournisseur réel. Les sessions QA sont des données fictives. **P0-01 et les autres risques P0 demeurent ouverts.**

## Continuité
Le raccordement futur de `atlascore.eu` et `voyageur.atlascore.eu` reste planifié **sans changement actuel**. Le dossier technique exhaustif de A à Z pour toute éventuelle commercialisation reste une exigence documentaire future, distincte du travail de recette.

**B6.5 recette — B6.3 NO-GO — aucun achat — aucune fusion main — site public inchangé — aucun test iPhone.**
