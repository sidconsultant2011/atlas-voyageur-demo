# SEC-01 R1-C01 — AC-08 — Note de cadrage technique des préconditions SQLite

**Date :** 27 octobre 2026. **Nature :** étude technique sans réalisation ni test.  
**Branche :** `feature/b6-5-cartographie-interactive`.  
**HEAD vérifié avant cadrage :** `5949d1d77b6625ecc3aae16b345f7550afa8768e`.  
**Décision du 00 :** `b65-http/DECISION-00-SEC01-R1-C01-AUDIT-STATIQUE-AC08-20261027.md`.  
**Contrat :** `b65-http/CONTRAT-04-SEC01-R1-C01-PERSISTANCE-REPRISE-20261027.md`, version 1.1.

## 1. Verdict de cadrage

**Un correctif AC-08 limité à la vérification et à l'établissement contrôlé des préconditions des connexions SQLite est faisable, sans changer l'architecture. GO DE CADRAGE seulement ; GO D'IMPLÉMENTATION À DÉCIDER PAR LE 00.**

Le code actuel ne fixe ni ne vérifie systématiquement `journal_mode=DELETE` et `synchronous=FULL`. Aucune violation effective, perte de révocation ou corruption n'a été observée. Une valeur par défaut de SQLite ou une configuration observée sur un banc ne prouve pas la conformité de toutes les connexions. Pas de correction introduite par cette note.

## 2. Inventaire réel des connexions et fonctions

| Fichier et point d'entrée | Connexions et opérations | Limite observée |
|---|---|---|
| `b65-http/persistent_sessions.py:PersistentSessionState.connect` | `sqlite3.connect(self.path,timeout=10)`; `PRAGMA busy_timeout=10000` ; utilisé par initialisation, création session, `check`, `revoke`, `journey`, et create/update/delete directs | Ni mode de journal, ni synchronisation, ni chemin disque qualifiés |
| `b65-http/fictional_identities.py:FictionalIdentityStore._db` | `sqlite3.connect(self.path,timeout=10)` ; `PRAGMA foreign_keys=ON` ; initialisation, ouverture/révocation identité, parcours directs | Même absence de mode et synchronisation imposés ; foreign_keys est déjà activé et doit rester actif |
| `b65-http/local_identity_bridge.py:LocalIdentityBridge._persistent_journey` | `state.connect()` sur base sessions principale ; `ATTACH DATABASE ? AS identity_db` ; `BEGIN IMMEDIATE` ; session et identité vérifiées, opérations parcours en base attachée | Il faut contrôler **main et identity_db sur cette même connexion après ATTACH et avant BEGIN**, en plus des politiques établies pour chaque fichier |
| `b65-http/local_http_facade.py` | Appels HTTP aux fonctions persistantes ci-dessus | Aucun changement HTTP autorisé au titre d'AC-08 ; AC-13 traité séparément |

Le pont avec `ATTACH` peut modifier les événements de débit de `sessions.sqlite` et `identity_journeys` de `identities.sqlite` dans un seul COMMIT. Le `POST .../session/revoke` ne modifie normalement que la base sessions ; **ne pas** assimiler toutes les révocations HTTP à une transaction bi-base.

## 3. Contrat exécutable proposé, sous réserve d'un GO technique du 00

**Politique minimale unique proposée : `journal_mode=DELETE`, `synchronous=FULL` pour les deux fichiers fictifs locaux, sur toutes les connexions concernées ; base `main` réellement sur disque ; mode identique explicitement vérifié après ATTACH.** Ce choix suit le contrat documentaire actuel, sans substituer a posteriori `EXTRA` à `FULL`. SQLite indique que `EXTRA` apporte un renforcement distinct, en particulier à la suppression du rollback-journal ; il n'est pas inclus dans cette proposition minimale et la durabilité après perte d'alimentation reste non démontrée.

Séquence de mise en œuvre proposée :
1. **Initialisation contrôlée, avant admission des requêtes :** déterminer les chemins canoniques attendus des deux bases, rejeter `:memory:`, URI non autorisées, chemins inattendus, fichier absent lorsqu'il devrait déjà exister et topologie de stockage non qualifiée. Distinguer explicitement création initiale de fixture fictive et ouverture d'une base existante. Les autorisations et la disponibilité du répertoire de journaux devront être contrôlées ; la correspondance de `st_dev` peut être un signal local, jamais une preuve matérielle exhaustive.
2. **Configuration séquencée hors transaction et avant trafic concurrent :** pour une nouvelle fixture, établir `PRAGMA main.journal_mode=DELETE`, puis lire son résultat ; fixer `PRAGMA main.synchronous=FULL`, puis lire sa valeur. Même procédure indépendante pour le fichier identités, sans perturber `foreign_keys=ON`. Les résultats doivent être comparés à `delete` et à l'entier `2`. Ne pas supposer qu'un `PRAGMA` a réussi du seul fait qu'il n'a pas levé d'exception. Un mode incompatible sur une base **existante** (notamment WAL) doit **bloquer l'admission** : pas de conversion silencieuse ou migration automatique.
3. **Contrôle à chaque connexion protégée :** lire `PRAGMA main.journal_mode` et `PRAGMA main.synchronous` avant `BEGIN IMMEDIATE`; refus contrôlé si le mode diffère. Le niveau `synchronous` étant propre à la connexion, il doit être posé et vérifié sur chaque connexion SQLite nouvellement ouverte, puis contrôlé après. Préserver `busy_timeout` et `foreign_keys=ON`.
4. **Pont bi-base :** immédiatement après `ATTACH` et avant le `BEGIN IMMEDIATE`, lire `PRAGMA database_list`, confirmer fichiers et alias attendus, lire `PRAGMA main.journal_mode`, `PRAGMA identity_db.journal_mode`; établir et contrôler `PRAGMA main.synchronous=FULL` et `PRAGMA identity_db.synchronous=FULL` sur **cette connexion**. Refuser si un journal est en WAL, MEMORY, OFF ou autrement incompatible ; aucun début de mutation.
5. **Défaut sécurisé et nettoyage :** une configuration incompatible, lecture de PRAGMA invalide, fichier imprévu ou erreur SQL au démarrage / contrôle AC-08 rend l'instance **non admissible aux mutations protégées**, sans réponse 200 revendiquant une réussite. Fermer les connexions et produire un diagnostic sans secrets. Le statut HTTP exact et la politique des exceptions sont du ressort d'AC-13 ; AC-08 ne doit pas les implémenter sous ce mandat. Le mode d'échec de l'initialisation est à convenir avant réalisation pour éviter des exceptions non traitées dans le serveur HTTP.
6. **Connexions déjà ouvertes :** aucune garantie rétroactive. Le futur GO devra prescrire une fenêtre de démarrage/quiescence, fermer les connexions antérieures à la configuration, puis recréer des connexions conformes. Ne pas changer `journal_mode` pendant une transaction ni en pleine concurrence. Ne pas migrer des fixtures historiques implicitement.

Ces prescriptions sont une **proposition**, pas une description du code existant.

## 4. Pourquoi ce périmètre est minimal

Une seule politique centralisée, utilisée par les deux fabriques de connexion et vérifiée au pont `ATTACH`, évite une réécriture des opérations métier et conserve la sérialisation `BEGIN IMMEDIATE` et l'API publique des sessions. L'initialisation séquentielle est nécessaire car `journal_mode` est un état du fichier pouvant impliquer des changements incompatibles avec des connexions concurrentes, tandis que `synchronous` doit être vérifié sur chaque connexion.

**Fichiers à modifier uniquement sous un futur GO :** `persistent_sessions.py`, `fictional_identities.py`, `local_identity_bridge.py` et éventuellement un module utilitaire SQLite partagé, si cela réduit les duplications. Aucune modification de `local_http_facade.py` n'est proposée dans AC-08 ; ses anomalies d'erreur/COMMIT relèvent d'AC-13.

## 5. Risques et compatibilité à accepter avant GO

| Risque | Mesure proposée | Limite |
|---|---|---|
| Base existante en WAL ou configuration non conforme | Refus d'ouverture protégée ; migration seulement sur autorisation séparée et sauvegarde qualifiée | Peut empêcher de démarrer certaines fixtures existantes |
| Journaux de deux fichiers sur support non qualifié / réseau | Contrôler chemins, nature locale attendue, hypothèses de VFS et support ; rejeter topologie non reconnue | Aucun détecteur logiciel ne prouve à lui seul les propriétés physiques de `fsync` |
| Connexion attachée avec PRAGMA différents | Vérifier chaque schéma après `ATTACH`, avant transaction | Dépend de la version de SQLite et du mode effectif de chaque base |
| Verrouillage lors du changement de mode | Configurer avant trafic, sans auto-conversion en période concurrente | Démarrage et fixtures de test à adapter |
| Ouverture de nombreuses connexions | Vérification stricte à chaque connexion ; préserver timeout et étrangeté des clés | Surcoût à mesurer dans une recette future, sans seuil inventé |
| Exceptions SQL et retour HTTP ambigu | Bloquer l'admission de la configuration ; documenter AC-13 comme risque indépendant | AC-13 non implémentée |
| Rupture du scénario fictif ou régression R1 | Recette R1 et B6.5 inchangée, vérifications comparatives | À prouver par tests futurs uniquement |

## 6. Matrice des tests à demander ultérieurement, NON exécutés

- Connexions mono-base sessions et identités : vérifier `DELETE`, `FULL=2`, conservation de `foreign_keys=ON` et de `busy_timeout` ; reproduire sur chaque nouvelle connexion.
- Connexion avec `ATTACH` : vérifier les deux fichiers présents sur disque, alias exacts, deux journaux DELETE, deux synchronisations FULL, puis `BEGIN IMMEDIATE` et COMMIT normaux sur bases fictives.
- Fixture préconfigurée volontairement WAL ou modes incompatibles : refus contrôlé **avant mutation**, sans conversion silencieuse ; état SQL inchangé, diagnostic sans secrets.
- Fichier principal `:memory:`, base attachée absente / chemin incompatible / topologie non admissible : échec sécurisé ; ne pas créer silencieusement une base manquante si la configuration exige un fichier existant.
- Deux connexions successives puis concurrentes : aucune connexion non vérifiée admise, contention et `SQLITE_BUSY` conservés, absence de changement `journal_mode` au cours d'une transaction.
- Scénarios de référence R1-C01 à R1-C07, mutations HTTP/révocation, propriétés SQL et identité fictive, et suite B6.5, exécutés sur un commit précis ; mesurer tout surcoût séparément, sans seuil postérieur aux résultats.
- Relecture indépendante des états persistants et tests de défaillance de configuration (sans SIGKILL/G04 dans le mandat AC-08). Tests d'atomicité au cœur du COMMIT, durabilité électrique et multi-hôtes restent hors qualification de cette étape.

**Traces attendues après éventuel GO :** version SQLite et OS, profils des bases (sans chemins sensibles dans les logs), noms de PRAGMA et valeurs effectives, verdict de contrôle, commit exact, commandes locales et exécution GitHub Actions précise. Un statut CI vide ne serait pas une preuve.

## 7. Références et décision attendue

**Sources GitHub vérifiées au HEAD cité :** `persistent_sessions.py`, `fictional_identities.py`, `local_identity_bridge.py`, contrat V1.1 et décision AC-08.  
**Documentation SQLite officielle consultée :**
- https://sqlite.org/lang_attach.html — conditions d'atomicité avec `ATTACH`, base `main` non en mémoire et mode non-WAL.
- https://www.sqlite.org/pragma.html — modes `journal_mode` et `synchronous`, résultats effectifs des PRAGMA, `FULL` et `EXTRA`.
- https://sqlite.org/wal.html — limitation d'atomicité inter-fichiers en WAL.

**Résultat de ce mandat :** note technique préparée, aucun code modifié, aucun test local ni GitHub Actions lancé. La publication de la présente note n'est **pas** une autorisation de réalisation. La traçabilité GitHub de cette note doit être contrôlée après dépôt.

**Proposition unique à soumettre au 00 :** autoriser ultérieurement un correctif AC-08 **« préparation contrôlée puis vérification fail-closed de DELETE/FULL pour sessions et identités, y compris au pont ATTACH »**, exclusivement sur les fichiers ci-dessus, accompagné des tests de conformité et de non-régression ; sans migration automatique de bases préexistantes et sans ouvrir AC-13.

**Statuts inchangés :** AC-08 écart ouvert, AC-13 hors chantier ; R1-C01 PARTIEL ; R1-RD01, R1, P0-01 ouverts ; B6.5 en recette ; G04, B6.3 et production NO-GO.

**Prochaine action unique :** transmettre ce cadrage au chat 00 pour décision explicite GO/NO-GO d'implémentation AC-08.
