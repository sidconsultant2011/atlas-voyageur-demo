# 04 — SEC-01 R1-C01 — Contrat documentaire de persistance SQLite et de reprise sécurisée

**Version :** 1.0 — 27 octobre 2026  
**Nature :** contrat cible et constat de code, **non** validation d'implémentation ni qualification après panne.  
**Mandat :** `DECISION-00-SEC01-R1-C01-REVUE-RESULTAT-20261027.md`.  
**Base de lecture :** commit `c4225283d741266e8f7ca7ef5f11b83838b9b967`, branche `feature/b6-5-cartographie-interactive`.  
**Périmètre :** prototype QA local, identités et données fictives exclusivement. Aucune production autorisée.

## 1. Sources et niveaux de preuve

- Code : `persistent_sessions.py`, `fictional_identities.py`, `local_identity_bridge.py`, `local_http_facade.py` sous `b65-http/`, lus au commit ci-dessus.
- Décisions : `DECISION-00-SEC01-R1-CRITERES-20261025.md`, `DECISION-00-SEC01-R1-C01-REVUE-CONTRAT-ATOMICITE-20261027.md`, `DECISION-00-SEC01-R1-C01-REVUE-RESULTAT-20261027.md`.
- Réception concurrente : `DECISION-00-SEC01-R1-HTTP-REVOCATION-CONCURRENTE-RECETTE-20261027.md`, CI n°218 (commit `880c7f9cbf324ea54cff85dbdaaeb02c50a0b460`), deux scénarios déterministes uniquement.
- Expérimentation : `SEC01-R1-RD01-RAPPORT-EXPERIMENTAL-01-20261025.md`, CI n°90 (commit `5fdb7c2ce69b2aa3e5b9cb95d309d9d083aed7f4`), 15 exécutions en 5 fenêtres *externes*.
- L'avis indépendant du chat 02 est reçu par le 00 en conversation ; son dépôt comme fichier autonome n'est pas attesté. **Verdict R1-C01 global : NON CONCLUANT**, statut du critère : PARTIEL.

Échelle de preuve : **DÉMONTRÉ DANS LE PÉRIMÈTRE** = lecture directe de code ou résultat reçu explicitement borné ; **PARTIEL** = chemin identifié mais limites de qualification ; **NON DÉMONTRÉ** = preuve manquante ; **NON APPLICABLE JUSTIFIÉ** = propriété hors opération et hors contrat.

## 2. Frontières transactionnelles et opérations réelles

| Opération et point d'entrée | Fichiers lus | Fichiers modifiés | Point logique et effet |
|---|---|---|---|
| Création session QA, `PersistentSessionState.create` | sessions | `sessions.sqlite` : session | INSERT puis sortie du contexte SQLite (COMMIT normal) ; cookie transmis ensuite par façade |
| Vérification session, `check` | sessions | `sessions.sqlite` : `request_events` pour contrôle de débit | `BEGIN IMMEDIATE`, lecture d'autorisation, entretien des événements, sortie du contexte |
| Révocation HTTP, `POST /api/v1/qa/session/revoke` → `PersistentSessionState.revoke` | sessions | `sessions.sqlite` : `request_events`, `sessions.revoked=1` | `BEGIN IMMEDIATE`, `_authorize`, UPDATE, COMMIT à la sortie de `with`; retour métier 200 ensuite. **Ne modifie pas `identities.sqlite`** |
| Retrait du pont mémoire, `revoke_binding` | dictionnaire mémoire | dictionnaire mémoire `_bindings` | Après `state.revoke` ayant rendu 200 et avant émission HTTP 200 ; non persistant, non lié atomiquement au COMMIT SQLite |
| Association fictive, `bind_fixture` | session et identité (lectures séparées) | `_bindings` mémoire | Validation de deux identifiants fictifs, seconde vérification session ; aucun COMMIT multi-base |
| Création/lecture/mise à jour/suppression parcours via `_persistent_journey` | `sessions.sqlite` : session et débit ; `identities.sqlite` : identité, session identité, parcours | `sessions.sqlite` : `request_events` si autorisé ; `identities.sqlite` : `identity_journeys` pour create/update/delete ; lecture sans écriture métier | `ATTACH identity_db` sur connexion sessions, `BEGIN IMMEDIATE`, `_authorize`, vérification du jeton fictif, mutation ciblée puis COMMIT à la sortie du contexte ; la présence d'ATTACH **n'implique pas deux modifications pour toute opération** |
| `FictionalIdentityStore.revoke` / `disable_identity` | identités | `identities.sqlite` : `identity_sessions`, éventuellement `identities` | Transactions propres à la base identité ; différentes de la révocation HTTP |
| Parcours direct `PersistentSessionState.create_journey/journey/update_journey/remove_journey` | sessions | `sessions.sqlite` : événements et table `journeys` selon opération | `BEGIN IMMEDIATE`, autorisation puis lecture/mutation mono-base |
| Chemin mémoire `LocalState` | mémoire | mémoire | Aucun contrat de durabilité SQLite ; **NON APPLICABLE JUSTIFIÉ** |
| **Fixture RD01** `rd01_crash_bench.py` | deux bases du banc | `sessions.sqlite` : révocation + seconde base : insertion témoin | Transaction `ATTACH` délibérément bi-base pour tester 5 marqueurs externes ; **ne reproduit pas une révocation HTTP réelle** |

**Attention au chemin HTTP métier :** `local_http_facade.py` invoque `state.check` avant de déléguer à `identity_bridge.create/read/update/delete`. Le pont persistant renouvelle sa vérification dans la transaction avec `ATTACH`. Les deux vérifications ne sont pas une seule transaction HTTP de bout en bout ; les accès mémoire du pont ne sont pas durables. Ne pas déduire de la simple lecture une gestion transactionnelle universelle pour les échecs en retour de `state.check`.

## 3. Invariants AVANT, APRÈS, états partiels interdits

**Règle R1-C01 :** le point de prise d'effet de la révocation HTTP est le COMMIT effectif de `sessions.revoked=1`. Une mutation métier validée avant ce point peut devenir visible ou répondre plus tard. Aucune mutation non validée avant le point ne doit acquérir un droit et être commitée après lui sur cette même base locale sérialisée.

| Opération | AVANT admissible | APRÈS succès et COMMIT | États partiels interdits au contrat cible |
|---|---|---|---|
| Révocation HTTP mono-base | Session active, `revoked=0` | `revoked=1` ; requêtes futures refusées ; pont mémoire retiré si exécution HTTP suit son chemin normal | HTTP 200 de révocation alors que l'état révoqué n'a pas été validé et résiste insuffisamment à une reprise conforme aux hypothèses ; acceptation d'un nouvel effet métier après révocation commitée |
| Révocation rejetée (401/403/429) | Autorisation invalide ou quota épuisé | Aucun changement de droit de révocation revendiqué ; les éventuels effets de contrôle de débit doivent être distingués | Retour signalant succès de révocation sans transition `revoked=1` |
| Pont métier CREATE/UPDATE/DELETE | Cookie, association mémoire, session et identité valides ; propriété du parcours requise | Mutation `identity_journeys` pour le propriétaire autorisé, précédée de la décision d'autorisation dans la transaction | Mutation sans propriétaire valide ; mutation nouvelle après révocation sérialisée déjà committée ; effet métier durable alors que transaction supposée annulée |
| Pont READ | Identité et session valides et propriétaire correct | Lecture du parcours appartenant à l'identité, sans mutation métier | Exposition d'un parcours tiers ou à une session refusée |
| Suppression association mémoire | Association présente ou absente | Association absente dans ce processus | Réassociation automatique au redémarrage ou persistance non autorisée de l'association ; **pas de contrat atomique multi-base pour cette simple suppression mémoire** |
| Fixture RD01 | Deux témoins dans l'état AVANT | Deux témoins APRÈS, dans le banc | État mixte AVANT/APRÈS pour les deux modifications de la fixture ; ce contrat de fixture n'est **pas** une exigence de synchroniser la révocation HTTP avec chaque identité |

L'invariant de **durabilité** après panne OS, perte d'alimentation ou COMMIT interrompu est une exigence à qualifier, pas un résultat acquis. Sur erreur COMMIT, ne pas inférer succès ou absence d'effet sans réouverture et vérification appropriées.

## 4. Préconditions SQLite : code, banc, contrat cible

| Propriété | Constat au commit source | Contrat cible et lacune |
|---|---|---|
| Chemins et stockage | `sqlite3.connect(path, timeout=10)` ; `busy_timeout=10000` sur connexion sessions ; `foreign_keys=ON` dans connexions `FictionalIdentityStore._db` | Imposer et vérifier explicitement chemins persistants, droits, intégrité et stockage local adapté ; **non imposé exhaustivement par code** |
| Transaction | `BEGIN IMMEDIATE` dans révocation et pont ; `ATTACH` avant BEGIN du pont | Conserver sérialisation des écrivains et contrôler résultat COMMIT avant accusé métier ; partiellement identifié par lecture |
| Journalisation | Pas de `PRAGMA journal_mode=DELETE` explicite dans `PersistentSessionState.connect` ou `_persistent_journey` | Pour revendiquer l'atomicité inter-fichiers avec `ATTACH`, imposer mode rollback-journal compatible pour toutes les bases pertinentes ; **ne pas autoriser WAL comme preuve d'atomicité multi-fichier** |
| Synchronisation | Pas de `PRAGMA synchronous=FULL` explicitement imposé dans ces connexions | Paramétrer et vérifier une politique de synchronisation appropriée ; `FULL` observé uniquement dans banc Linux RD01 ; garantie physique non déduite du paramètre |
| Base principale | Sessions utilisée comme connexion principale, identités attachée | Fichier principal effectivement sur disque, pas `:memory:`, et absence de WAL pour la garantie inter-fichiers visée ; configuration effective à contrôler |
| Dispositifs et topologie | Banc RD01 : deux bases sur même `st_dev`, Linux, SQLite 3.45.1, `DELETE`, `FULL` | Valider support local, même environnement de verrouillage et hypothèses du système de fichiers, stockage, journalisation et `fsync`. Aucun contrat prouvé sur réseau, multi-hôtes, OS crash ou matériel |
| Erreurs SQL | La façade ne présente pas de gestion généralisée `sqlite3.Error` sur les chemins inspectés | Refuser toute réponse de succès en cas d'exception COMMIT/IO, sans présumer que les HTTP 5xx sont déjà formatés ni que l'état persistant est connu |

Ces exigences représentent un **contrat à rendre exécutable et qualifiable ultérieurement**, non une description d'une configuration garantie par le prototype actuel.

## 5. Chronologie COMMIT → HTTP et reprises

### Révocation HTTP mono-base (lecture du code)

1. Contrôle HTTP d'origine et extraction cookie/CSRF.
2. `state.revoke` ouvre `BEGIN IMMEDIATE`, vérifie la session et écrit `sessions.revoked=1`.
3. Sortie normale de `with self.connect()` : commit transactionnel SQLite effectué avant `return 200` de `revoke`.
4. La façade supprime l'association mémoire du pont, puis émet HTTP 200 et cookie expiré.

**DÉMONTRÉ DANS LE PÉRIMÈTRE (structure du code) :** le chemin normal ne répond pas 200 avant la sortie du contexte transactionnel. **NON DÉMONTRÉ :** durabilité physique de l'écriture après panne ; réponse HTTP maîtrisée pour chaque exception SQLite et ambiguïté COMMIT ; suppression mémoire si exception avant la réponse.

### Pont métier `ATTACH`

Le COMMIT du `with state.connect()` précède le retour d'une opération réussie du pont ; il peut porter sur les événements de débit dans sessions et la mutation de parcours dans identités. Il reste distinct du `check` HTTP préalable. Le verrou `BEGIN IMMEDIATE` et la vérification à l'intérieur du pont étayent la sérialisation locale, **pas** une transaction distribuée, inter-hôtes, ou une preuve générale d'intégrité post-panne.

### Exigences proposées de reprise et de défaut sécurisé — NON IMPLÉMENTATION CERTIFIÉE

- Au redémarrage : ouvrir les fichiers sous préconditions vérifiées, laisser SQLite traiter les journaux selon son protocole, vérifier l'intégrité/cohérence utile (sessions révoquées, identités actives, ownership, liens) avant d'accepter une mutation protégée.
- Ne jamais recréer une association `_bindings` en mémoire à partir des seules tables SQLite ; une nouvelle association explicite sur identifiants fictifs valides est nécessaire.
- Si base manquante, journal incohérent, récupération impossible, paramètres requis absents, réponse COMMIT ambiguë ou divergence critique des droits : **refuser par défaut** les opérations protégées, tracer un diagnostic sans secrets, et exiger résolution opérateur documentée. Ne pas renvoyer 200 comme si la révocation était définitivement acquise si le COMMIT n'est pas connu.
- La sémantique HTTP exacte (503 ou autre statut, identifiant d'erreur stable), les politiques de reprise et leur mise en œuvre **restent à définir et à tester**. Aucun comportement automatique fail-closed après corruption n'est validé par ce document.

## 6. Matrice probatoire

| Propriété | Appui | Statut |
|---|---|---|
| Révocation HTTP mono-base, commit logique avant retour 200 normal | `persistent_sessions.py:revoke`, `local_http_facade.py:do_POST` | **DÉMONTRÉ DANS LE PÉRIMÈTRE** (lecture statique) |
| `ATTACH` et autorisation dans `BEGIN IMMEDIATE` du pont persistant | `local_identity_bridge.py:_persistent_journey` | **DÉMONTRÉ DANS LE PÉRIMÈTRE** (lecture statique) |
| Révocation concurrente et mutations refusées après | décision réception CI 218, deux scénarios | **PARTIEL** (banc fictif déterministe) |
| Fixture RD01 : 15 états AVANT/APRÈS aux cinq marqueurs externes | rapport RD01, CI 90 | **PARTIEL** (pas d'interruption au cœur du COMMIT) |
| `DELETE`/`FULL` imposés à toute connexion du prototype | code des connexions | **NON DÉMONTRÉ** |
| Atomicité durable inter-fichiers sur panne interne COMMIT | absence d'essais internes, OS, stockage | **NON DÉMONTRÉ** |
| Reprise cohérente et refus sécurisé sur incohérence | pas de chemin exhaustif identifié | **NON DÉMONTRÉ** (exigence proposée) |
| Garantie inter-hôtes | architecture locale SQLite | **NON APPLICABLE JUSTIFIÉ** au prototype ; aucune revendication possible |
| Atomicité multi-bases pour simple retrait du pont mémoire | `revoke_binding` modifie dict seulement | **NON APPLICABLE JUSTIFIÉ** |

## 7. Conclusion documentaire et vérification future unique

**Contrat formalisé et traçable — verdict sur la qualification de récupération : NON CONCLUANT.** Le point de validation logique de révocation HTTP et la distinction avec le pont `ATTACH` sont identifiés. Les garanties de configuration, de durabilité physique, de reprise en panne et de refus sécurisé **ne sont pas démontrées**.

**Une seule proposition de vérification ultérieure, soumise au 00 et non autorisée ici :** un audit de conformité **statique et non destructif** des préconditions de connexion SQLite et du traitement des exceptions COMMIT sur les chemins réellement exposés par HTTP, débouchant sur une matrice code/exigences et une décision sur le besoin (ou non) de qualification dynamique. Ce contrôle n'est pas réalisé dans ce chantier.

**Statuts inchangés :** R1-C01 **PARTIEL** ; R1-RD01, R1, P0-01 **OUVERTS** ; B6.5 **EN RECETTE** ; B6.3, G04, production **NO-GO**. Pas de code, test, CI, VFS, SIGKILL ni déploiement dans cette livraison.

## Résultat à remonter au 00

Chantier : contrat documentaire R1-C01, à partir du commit source `c4225283`. Résultat : matrice et invariants formalisés ; aucune qualification de panne supplémentaire. Décision attendue : réception du présent contrat et arbitrage éventuel, distinct, de l'unique audit statique proposé. **Prochaine action : réception documentaire par le chat 00.**
