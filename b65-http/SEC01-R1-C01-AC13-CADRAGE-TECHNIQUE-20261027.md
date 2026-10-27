# SEC-01 R1-C01 — AC-13 — Cadrage technique des erreurs SQLite vers HTTP

**Date :** 27 octobre 2026. **Nature :** cadrage documentaire seul ; aucune implémentation, aucun test.  
**Dépôt :** `sidconsultant2011/atlas-voyageur-demo`. **Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD de départ vérifié :** `2f1ec5041fb8ab46dbb140135dc2d55644ddfc4c`.  
**Décision du 00 :** `b65-http/DECISION-00-SEC01-R1-C01-AC13-CADRAGE-20261027.md`.  
**Contrat cible :** `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md`, version 1.1.

## 1. Constat attesté sur le code courant

`b65-http/local_http_facade.py` définit déjà `Handler.send_json(status,payload,extra)` et `Handler.fail(code,error)`. Les réponses de cette méthode portent `Cache-Control:no-store`, `nosniff`, `Referrer-Policy:no-referrer`, une politique CSP et une autorisation d'origine restreinte. `do_POST`, `do_GET` et `do_DELETE` n'ont cependant pas de frontière générale de traduction des exceptions `sqlite3.Error` ou `SQLitePreconditionError` en JSON de service indisponible. Les `try/except` existants dans `do_POST` ne concernent que la syntaxe/validation du corps JSON.

`b65-http/sqlite_ac08.py` fournit `SQLitePreconditionError` pour les refus de mode DELETE, synchronisation FULL, chemins/alias/fichiers de bases et topologie : ces codes internes n'ont pas de traduction HTTP uniforme qualifiée. `PersistentSessionState.connect()`, `FictionalIdentityStore._db()` et `LocalIdentityBridge._persistent_journey()` exécutent des opérations SQLite susceptibles de lever des erreurs de connexion, verrouillage, lecture, écriture ou COMMIT. La sortie normale du `with sqlite3.Connection` précède le retour de succès métier, mais une exception durant cette sortie ne suffit pas à déterminer l'état persistant final.

L'absence de traitement HTTP explicite constitue un écart au **contrat cible** ; aucune fuite observée, violation d'autorisation ou perte de révocation n'est déduite de ce constat statique. **AC-08 est reçu avec réserves** et n'est pas rouvert.

## 2. Inventaire exhaustif des routes HTTP du prototype

| Route / méthode | Points d'appel SQLite possibles | Risque sur exception |
|---|---|---|
| `POST /api/v1/qa/session` | `state.create()` → `PersistentSessionState.create` | INSERT de session et COMMIT ; ne pas délivrer cookie/CSRF comme succès si sortie transactionnelle échoue |
| `POST /api/v1/qa/session/revoke` | `state.revoke()` → `PersistentSessionState.revoke` ; puis `identity_bridge.revoke_binding()` si 200 | COMMIT de révocation ambigu ; ne pas délivrer 200 ni annoncer révocation ou absence de révocation sur erreur |
| `POST /api/v1/qa/journeys` | `state.check(...,write=True)` ; `identity_bridge.create()` → pont `ATTACH` ou `state.create_journey()` | Autorisation inconnue ou création/COMMIT du parcours non confirmé ; jamais de 201 sur erreur |
| `POST /api/v1/qa/journeys/{id}/label` | `state.check(...,write=True)`, `identity_bridge.read/update()` ou `state.journey/update_journey()` | Lecture puis mutation/COMMIT incertains ; ne pas retourner de version ou 200 non confirmé |
| `POST /api/v1/qa/echo` | `state.check(...,write=True)` | Précondition d'autorisation / écriture de quota non confirmée : interdire l'accès à la réponse fonctionnelle |
| `GET /api/v1/qa/state` | `state.check()` | Autorisation impossible à vérifier ; ne pas retourner 200 |
| `GET /api/v1/qa/journeys/{id}` | `state.check()`, puis `identity_bridge.read()` ou `state.journey()` | Ne pas exposer de parcours lorsque l'autorisation ne peut être confirmée |
| `DELETE /api/v1/qa/journeys/{id}` | `state.check(...,write=True)`, puis `identity_bridge.delete()` ou `state.remove_journey()` | Suppression/COMMIT non confirmé ; ne pas annoncer `deleted:true` |

La méthode `OPTIONS` et les rejets d'origine, de longueur et de schéma de JSON ne nécessitent pas de connexion SQLite : conserver leurs comportements et statuts existants. Le chemin `LocalState` entièrement en mémoire doit également conserver sa sémantique actuelle ; le traitement AC-13 est réservé aux exceptions SQLite constatées, non une transformation des refus métier 401/403/404/429.

Au-delà des routes, **l'initialisation** `PersistentSessionState.__init__` et `FictionalIdentityStore.__init__` intervient avant le traitement HTTP : une exception AC-08 ou SQLite au démarrage doit empêcher la mise en service du serveur persistant. Il ne faut pas fabriquer une réponse HTTP lorsque l'écoute n'a pas été créée.

## 3. Un seul changement minimal proposé pour futur GO

**Créer dans `b65-http/local_http_facade.py` une frontière HTTP commune, contrôlée et ciblée**, autour de l'exécution de chaque méthode `do_POST`, `do_GET`, `do_DELETE` : réutiliser les réponses existantes `fail()` / `send_json()`, intercepter exclusivement `SQLitePreconditionError` et `sqlite3.Error` (incluant connexions, `OperationalError`, verrouillage, erreurs d'écriture et COMMIT). Ajouter les imports nécessaires et factoriser au lieu de répéter des blocs disparates.

Le futur correctif ne devra pas intercepter `BaseException`, `KeyboardInterrupt`, ni masquer arbitrairement les erreurs de programmation ; il doit conserver les refus métier normaux et les erreurs JSON déjà gérées. Les dépendances `state` et `identity_bridge` doivent pouvoir remonter leurs exceptions SQLite **inchangées** jusqu'à la frontière HTTP. Aucun changement SQL, des transactions, de `sqlite_ac08.py`, de `PersistentSessionState` ou de la VFS n'est proposé.

**Proposition de contrat HTTP à faire valider avant codage** :
- Réponse de défaillance SQLite commune, **HTTP 503** (*proposé, non validé*) : `{"status":"unavailable","errors":[{"code":"STORAGE_UNAVAILABLE"}]}`. Ce code ne dit **rien** de l'issue d'une mutation, même si une exception a été levée au COMMIT.
- Le refus `SQLitePreconditionError` lié à AC-08 peut utiliser un code public distinct `STORAGE_PRECONDITION_FAILED`, toujours avec le même statut 503 proposé, sans reprendre le détail interne de chemin, configuration, exception ou SQL.
- Pour toute mutation avec erreur SQLite, y compris un éventuel COMMIT, **aucun accusé fonctionnel 200/201**, aucun `journeyId`, `deleted:true`, `revoked:true` ni version « confirmée ». **Pas de mention `rolled_back`, `committed` ou `revoked=false`** : l'état peut être inconnu.
- Ne pas émettre de nouveau cookie de session après échec de création, ni de cookie d'expiration supposant une révocation effectuée si le COMMIT a échoué ou reste ambigu. Il peut être pertinent de supprimer prudemment un cookie côté client, mais cette mesure ne prouverait jamais la révocation persistante et n'est **pas** proposée par défaut.
- Ne pas réessayer automatiquement une mutation depuis le serveur, ni prescrire au client un retry automatique sur HTTP 503 ; **l'idempotence n'est pas assurée**. Les lectures/états ultérieurs peuvent nécessiter une réouverture indépendante, un diagnostic et une décision opérateur.
- Ne pas exposer `str(exc)`, trace SQL, chemin local, cookie, CSRF, jeton de pont, identité ou valeurs de base dans le JSON, les en-têtes ou les journaux. La façade existante neutralise `log_message` ; ne pas ajouter d'impression de secrets. Conserver `Cache-Control:no-store` et les protections d'origine.
- La frontière doit envoyer **une seule réponse** ; elle n'est applicable qu'aux exceptions levées **avant le début effectif de `send_json`**. Une exception réseau après envoi des en-têtes ou pendant la transmission ne peut pas être rattrapée en envoyant un second 503 ; documenter ce cas séparément.

**Limite intrinsèque :** une réponse HTTP 503 pour un COMMIT ambigu indique uniquement l'impossibilité de confirmer le résultat. Une requête de lecture après reconnexion ne suffit pas toujours à établir la durabilité en cas de panne physique future. Le contrat ne revendique donc ni compensation automatique ni exactement-une-fois.

## 4. Conditions d'autorisation et point transactionnel

- `state.check` peut lui-même ouvrir `BEGIN IMMEDIATE` et écrire `request_events` ; si ce contrôle échoue, **aucune mutation ni lecture protégée** ne doit être déléguée. Un 401 ne doit pas être inventé pour une erreur SQLite : il représente un refus d'authentification, pas un système de stockage indisponible.
- Le pont `_persistent_journey` reprend l'autorisation **dans la transaction avec `ATTACH`**, après son contrôle AC-08. La frontière HTTP ne doit pas l'éluder ; elle traduit uniquement une exception SQL.
- `state.revoke` modifie la base sessions et quitte le contexte SQLite pour COMMIT avant de renvoyer le statut de succès normal. En cas d'exception, `revoke_binding` ne doit pas devenir une preuve de révocation persistante ; le JSON ne doit pas présenter le résultat comme certain. L'association mémoire peut nécessiter un traitement conservateur futur, mais ce cadrage ne revoit pas sa durée de vie ni AC-08.
- Une anomalie SQL dans l'enregistrement de quota (même sur une route de lecture) doit être traitée comme indisponibilité de vérification, et non comme autorisation implicite.

## 5. Fichiers, risques de régression et tests futurs falsifiables

**Périmètre de code unique recommandé :** `b65-http/local_http_facade.py`, plus un fichier de tests `b65-http/test_sec01_ac13_http_errors.py`. Aucun changement à la façade de démonstration publique, aux modules SQLite ou au contrat AC-08.

**Tests proposés mais NON exécutés** (fixtures factices isolées, exceptions injectées dans les points d'appel Python, **sans** injection de panne OS, VFS ou SIGKILL) :

1. Refus AC-08 sur session creation, check, revoke, create/read/update/delete : 503 JSON structuré proposé, pas de 200/201, pas de mutation ultérieure ni divulgation du code interne/chemin.
2. Erreur `sqlite3.OperationalError` sur `state.check` : aucun appel au pont / aucune réponse protégée positive pour GET, POST, DELETE, y compris `echo`.
3. Erreur SQLite sur `state.revoke` : aucun `revoked:true`, aucun cookie d'expiration de succès et aucune suppression du pont revendiquée comme preuve SQL ; état transactionnel public **inconnu**.
4. Erreur SQLite synthétique sur retour du contexte transactionnel / COMMIT de création ou modification : HTTP 503 proposé, sans `journeyId`, `version` ou statut certain, avec relecture SQLite indépendante du banc lorsque l'injection contrôlée permet de déterminer l'état réel. **Ne jamais inventer que l'injection reproduit une vraie panne COMMIT native**.
5. Contention `database is locked` et erreur d'I/O synthétique : même comportement de refus protégé, sans message SQL exposé, ni retry automatique.
6. Non-régression de 401/403/404/429, JSON invalide, origine, CORS, cookies, CSP, `Cache-Control:no-store`, fonctionnement inchangé du `LocalState` mémoire.
7. Non-régression des scénarios R1 HTTP concurrents, de la suite AC-08 (DELETE/FULL, WAL refusé, ATTACH), de l'intégrité du pont et de B6.5 ; tests locaux et CI rapportés séparément sur le **même commit**.

**Risque majeur résiduel :** des erreurs de réponse réseau après écriture du statut HTTP ne peuvent pas être converties en nouveau JSON ; des clients peuvent ne pas recevoir une réponse, même si le COMMIT a réussi. Une frontière HTTP ne rend pas une mutation idempotente. Le problème de récupération des erreurs COMMIT persistantes et de crash reste ouvert au contrat R1-C01.

## 6. Niveaux de preuve et arbitrage demandé

**Preuves directes GitHub :** décision de cadrage, contrat R1-C01, `local_http_facade.py`, `sqlite_ac08.py`, `persistent_sessions.py`, `local_identity_bridge.py` au HEAD initial cité. La stratégie HTTP décrite ci-dessus est **une proposition** issue de cette inspection, pas un comportement implémenté, testé, ni reçu.

**Aucun nouveau test local ou GitHub Actions n'a été lancé pour AC-13.** Les résultats antérieurs AC-08 (CI n°238) et R1 concurrente (CI n°218) servent uniquement de référence de non-régression ; ils ne sont pas des preuves d'AC-13.

**Décision unique attendue du 00 :** GO ou NO-GO d'implémentation de la frontière HTTP ciblée `SQLitePreconditionError` + `sqlite3.Error`, avec **HTTP 503** et codes publics stables proposés, en conservant l'incertitude du COMMIT et sans replay/retry automatique ni modification transactionnelle.

**Statuts inchangés :** AC-08 réceptionné avec réserves ; AC-13 ouvert et seulement cadré ; R1-C01 PARTIEL ; R1-RD01, R1 et P0-01 OUVERTS ; B6.5 en recette ; B6.3, G04 et production NO-GO ; C03-R05 suspendu ; C03-R06 ouvert.

**Prochaine action unique :** transmettre cette note de cadrage au 00 pour arbitrage explicite GO/NO-GO d'implémentation AC-13.
