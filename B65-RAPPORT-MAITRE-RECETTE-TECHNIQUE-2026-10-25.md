# ATLAS VOYAGEUR — RAPPORT MAÎTRE DE RECETTE TECHNIQUE B6.5
**Édition : 25 octobre 2026** — Version 1.0 — Statut : **PASS QA HORS LIGNE / NO-GO CONNEXION FOURNISSEURS ET PRODUCTION**

## 1. Périmètre, décision et sources
Dépôt : `sidconsultant2011/atlas-voyageur-demo`. Branche de recette : `feature/b6-5-cartographie-interactive`.
Référence contrôlée : commit `f6a9d26e5e17486a92542fced474f5472018b968` ; exécution GitHub Actions **n°42, successful**, https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40135072884 (24/10/2026, 21:37 UTC).
**Décision : les tests automatisés B6.5 actuellement couverts sont verts.** Ceci ne constitue ni une homologation sécurité, ni une approbation d'API réelle, ni un GO B6.3.

Sources CI additionnelles :
- n°41 — test interruption SQLite : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40135038922 — success. Journal consulté : Node **116 tests, 116 pass, 0 fail** ; Python SQLite **11 tests, OK**.
- n°39 — persistance SQLite initiale : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40134655525 — success. Journal consulté : Node **116 pass**, Python SQLite **7 tests, OK**.
- n°34 — réservations atomiques en mémoire : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40134003869 — success.
- n°32 — façade simulée : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40133273965 — success ; journal contrôlé précédemment : 98 pass, 0 fail.
La n°42 porte sur un commit documentaire après la n°41 : elle valide le pipeline sur l'état référencé sans apporter à elle seule un test de sécurité nouveau.

## 2. Inventaire des livrables et garanties démontrées
| Domaine | Pièces maîtresses | Preuve/état |
|---|---|---|
| Calcul de départ / gestion des fuseaux horaires et marges | `b65-calculateur/atlas-depart-engine.mjs`, tests associés | Tests Node CI verts ; résultats indicatifs uniquement |
| Adaptateurs AeroDataBox V2 **offline** et Geoapify fictif | `b65-calculateur/aerodatabox-v2.mjs`, `aerodatabox-v2-controller.mjs`, `mock-adapters.mjs` | Contrôles de normalisation, données inconnues, fraîcheur ; pas d'API réelle |
| Contrôleur, cohérence et versions | `journey-controller.mjs` + tests | Invalidation de route, refus d'observation ancienne, expiration à la lecture |
| Horloge accélérée / affichage QA | `accelerated-journey.mjs`, `local-display-ticker.mjs`, `RECETTE-B65-HORLOGE-ACCELEREE.html` | Passage disponible → expiré → restauré sur horloge fictive ; aucun poll fournisseur |
| Contrat façade serveur | `B65-CONTRAT-FACADE-SERVEUR-SECURISEE-V1.md` | Spécification V1 ; endpoints non implémentés |
| Façade simulée en mémoire | `mock-server-facade.mjs`, `mock-server-facade.test.mjs` | Isolation des sessions fictives, budget, cache, entrées invalides, gestion des erreurs ; **pas de serveur HTTP** |
| Crédits mono-processus | `credit-ledger.mjs`, `credit-ledger.test.mjs` | Débits et remboursements idempotents ; `Promise.all` sur un processus |
| Multi-instances fictives | `transactional-credit-store.mjs`, `transactional-credit-store.test.mjs` | Instances JS partageant un store en mémoire ; **pas de persistance disque** |
| SQLite sur disque | `b65-sqlite/sqlite_credit_ledger.py`, `test_sqlite_credit_ledger.py` | `BEGIN IMMEDIATE`, intégrité des soldes, concurrence **16 processus** sur un fichier local, réouverture |
| Robustesse après arrêt de processus | `b65-sqlite/test_sqlite_crash_qualification.py` | Rollback avant commit, durabilité après commit, contrôle physique et métier, réservations à réconcilier |

**Important :** le contrôle du plafond et la persistance sont qualifiés dans les environnements de test visés, pas dans une architecture multi-hôtes réelle ; l'intégration en bout-en-bout `HTTP → auth réelle → base → API fournisseur` reste absente.

## 3. Preuves d'essai — niveau de confiance
- GitHub Actions utilise Node.js 22 et `node --test b65-calculateur/*.test.mjs`; Python exécute `python3 -m unittest discover -s b65-sqlite -p 'test_*.py' -v` sans service payant.
- Au commit n°41 : **127 tests au total sur deux runners de tests dans un même job** (116 Node + 11 Python). Les journaux rapportent zéro échec pour Node et `OK` pour Python.
- Arrêt de processus enfants via `os._exit` ; *ne constitue pas un test de coupure électrique ou de crash du système d'exploitation*.
- Vérification comptable : `available + reserved + committed = budget`, protection des réservations ambiguës par état `reconciliation_required`; impossibilité de se reposer sur `PRAGMA integrity_check` seul pour détecter des incohérences métiers.
- CI verte ne garantit pas la sécurité en production, les licences fournisseurs, la précision des vols réels ou la robustesse d'un réseau.

## 4. Risques ouverts / critères bloquants avant toute connexion fournisseur
| Priorité | Bloqueur | Critère de levée |
|---|---|---|
| P0 | Authentification serveur, contrôles d'accès aux parcours (IDOR), CSRF/CORS et anti-abus non livrés | Tests d'intégration et sécurité sur une façade HTTP non publique |
| P0 | Secrets, rotation, séparation environnements et exposition potentielle des clés de carte | Architecture serveur sécurisée et contrôle des secrets/URLs/logs |
| P0 | Budget fournisseur réel, tarif par endpoint, plafonds de frais, retries, concurrence inter-instances distantes | Matrice tarifaire vérifiée, hard stop transactionnel partagé, rapprochement facture |
| P0 | API réelles non connectées ; qualité, horodatage, statut observé/estimé non qualifiés | Contrats fixtures adversariaux, conformité aux schémas actuels et preuve sur données autorisées |
| P0 | Traçabilité après panne et débit incertain | Journal durable et rapprochement officiel avant toute libération des crédits |
| P1 | SQLite local non adapté au multi-hôtes serverless sans service de données partagé | Choix d'infrastructure transactionnelle et qualification inter-hôtes |
| P1 | Conformité, licence, attribution cartographique, conservation et vie privée | Revue licences, RGPD, retention/purge, informations utilisateur |
| P1 | Fiabilité UI réelle/veille en arrière-plan/mobilité | Recette multi-navigateurs dédiée, sans obligation immédiate de test iPhone |
| P1 | Déploiement, observabilité, supervision coût, sauvegardes et reprise | Environnement isolé, métriques et alertes, scénario de restauration |
| P2 | Avertissements techniques des GitHub Actions | Maintenance des dépendances/actions sans affecter la recette fonctionnelle |

## 5. Décision et prochaines conditions
**B6.5 — PASS TECHNIQUE RESTREINT AUX TESTS HORS LIGNE.** Les preuves ci-dessus suffisent à poursuivre la conception et les tests fictifs. **NO-GO vers les APIs fournisseurs, les achats, les opérations commerciales et la production.**
La prochaine phase peut être une matrice de levée des P0 avec responsables, tests de réception et preuves minimales. Tout accès aux fournisseurs réels nécessite une décision GO explicite distincte et une vérification préalable des coûts/licences. Aucun test iPhone nouveau imposé.

**Règles de gouvernance non modifiées : B6.5 en recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur `main` ; site `voyageur.atlascore.eu` inchangé.**

ATLAS VOYAGEUR — *Le bon vol. Le bon trajet. Le bon moment.*
