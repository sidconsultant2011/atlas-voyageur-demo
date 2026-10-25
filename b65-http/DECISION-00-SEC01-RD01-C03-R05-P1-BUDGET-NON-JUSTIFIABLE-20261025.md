# Décision 00 — SEC-01 R1-RD01 — Budget B non justifiable, suspension quantitative C03-R05

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `8b2b3aee63d37f448268909c596cb9891bd6eaeb`  
**Autorité :** 00 — Pilotage et gouvernance.

## Vérifications et références

- Décision 00 antérieure : `b65-http/DECISION-00-SEC01-RD01-C03-R05-P1-METHODE-RECEPTION-20261025.md`.
- Contrat G03-R01 : `b65-http/SEC01-RD01-G03-R01-CONTRAT-ATTESTATION-CAUSALE-20261025.md`, consulté sur la branche autorisée. Il exige une relation causale `BEFORE_DELEGATE`/`AFTER_RETURN`, des retours natifs préservés, une observation non réentrante, sûre en concurrence, à mémoire et délai bornés, et la préservation d'invariants fonctionnels. **Aucun budget de surcharge temporelle chiffré ni SLA de COMMIT n'y est établi.**
- Conception VFS : `b65-http/SEC01-RD01-CONCEPTION-TECHNIQUE-VFS-20261025.md`, consultée. Elle évoque les effets possibles de la collecte sur ordonnancement, latence, IPC et contention ; aucun budget maximal chiffré n'est attesté.
- Avis indépendant 02 daté du 25 octobre 2026, transmis sous le titre `Fondement du budget C03-R05-P1` : conclusion **« Budget B non justifiable à ce stade »** ; aucun nouveau test, aucune modification de dépôt.
- Campagne N/W/C03 antérieure : GitHub Actions n°186 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40234530686, `completed/success` au commit `d5248e4510c1c3502138a5bf62f1213ba858e8fd` ; 253 exécutions réussies selon réception précédente. Les 18 mesures sont descriptives, non un fondement indépendant pour fixer B.
- Le chat 00 n'a exécuté aucun test local ni nouvelle CI.

## Décision explicite du 00

**CONCLUSION DOCUMENTAIRE VALIDÉE : BUDGET B NON JUSTIFIABLE À CE STADE.**

**C03-R05 DEMEURE OUVERTE ; SA QUALIFICATION QUANTITATIVE EST SUSPENDUE.**

Aucun taux de surcharge (5 %, 10 %, 20 % ou autre) ne sera inventé ou déduit des observations passées. La durée globale du scénario COMMIT/ROLLBACK et contention ne mesure pas spécifiquement la perturbation locale du callback `xDelete` important pour G03-R01. La proximité des médianes ne démontre ni neutralité temporelle, ni représentativité causale générale.

**Acquis inchangés :** parité fonctionnelle expérimentale N/W/C03 pour les scénarios fictifs testés et caractérisation descriptive des durées, réceptionnées indépendamment. Le contrat G03-R01 conserve ses exigences de neutralité fonctionnelle, absence de réentrance et préservation des comportements transactionnels, sans que ces exigences soient converties artificiellement en pourcentage.

**Condition de réouverture des mesures quantitatives C03-R05 :** apparition et approbation par le 00 d'un besoin externe au lot de mesures passées, établissant un critère temporel falsifiable pertinent pour le point causal et un plan de mesure adapté ; toute nouvelle instrumentation nécessiterait une autorisation distincte. Ne pas confondre acceptabilité des durées et preuve causale `BEFORE_DELEGATE`.

## Gouvernance et statuts

- **C03-R05 : OUVERTE, campagne quantitative suspendue, acquis bornés maintenus.**
- **C03-R04 et C03-R06 : OUVERTES** ; **C03-R01 à R03 : CLÔTURÉES** dans leurs seuls périmètres fictifs.
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 : OUVERTS.**
- **B6.5 EN RECETTE ; G04, B6.3 et production NO-GO** ; G05 global PARTIEL, R1-C01 PARTIEL.
- Pas de nouveau développement autorisé par cette décision, pas de modification wrapper C/moteur/code métier, pas de `BEFORE_DELEGATE`, SIGKILL, panne, G04, donnée réelle, fournisseur, fusion vers main, site public ou déploiement.
- Le document est un **arbitrage de gouvernance**, pas un résultat de test ni une qualification de production.

## Prochaine action unique

Demander au chat 02 une priorisation documentaire entre les seules réserves encore actives et non suspendues **C03-R04 et C03-R06**, sans rouvrir C03-R05 ni lancer d'autres chantiers.
