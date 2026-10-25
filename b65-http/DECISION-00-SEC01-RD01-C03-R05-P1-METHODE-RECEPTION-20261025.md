# Décision 00 — SEC-01 R1-RD01 — Réception documentaire de la méthode C03-R05-P1

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `92db144f0c1f188e997790c2d0cc4ea1e1c69324`  
**Autorité :** 00 — Pilotage et gouvernance.  
**Chantier unique :** C03-R05-P1 — examen documentaire du contrat temporel, sans expérimentation.

## Sources et état réel

- Décision 00 initiale : `b65-http/DECISION-00-SEC01-RD01-C03-R05-P1-BUDGET-20261025.md`.
- Protocole de comparaison déjà exécuté : `b65-http/SEC01-RD01-C03-R05-PROTOCOLE-20261025.md`.
- Rapport expérimental : `b65-http/SEC01-RD01-C03-R05-NEUTRALITE-PREUVES-20261025.md`.
- CI n°186 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40234530686, `completed/success`, commit `d5248e4510c1c3502138a5bf62f1213ba858e8fd`. Bilan de référence antérieurement vérifié : 253 exécutions réussies et 18 durées descriptives. Ces données **ne définissent ni budget admissible ni neutralité générale**.
- Note `C03-R05-P1 — Proposition de budget et protocole de décision` remise au 00 par le chat 02 le 25 octobre 2026 sous forme de texte, **non enregistrée par 02 dans GitHub** ; le présent document est une décision du 00, pas une validation expérimentale ou statistique de cette note.
- Aucun nouveau test, résultat de mesure ni développement n'est revendiqué au titre de l'avis 02 ou de cette décision.

## Arbitrage du 00

**GO DE RÉCEPTION DOCUMENTAIRE DU CADRE MÉTHODOLOGIQUE, AVEC RÉSERVES.**

Le 00 accepte comme **base de travail, non comme protocole final approuvé**, les principes suivants :
1. Profil borné : Linux/runner documenté, SQLite effective identique, deux bases fictives ATTACH, DELETE/FULL, scénarios COMMIT et ROLLBACK avec contention ; N comme référence, W comme témoin, C03 comme instrument étudié.
2. Définir **avant** une future campagne un budget de perturbation admissible `B` **justifié par les besoins du banc de preuve G03-R01** ; ne pas déduire `B` des 18 observations existantes.
3. Comparer des durées positives sur une échelle relative, avec plan bloqué et ordre équilibré, en analysant séparément COMMIT et ROLLBACK.
4. Prévoir une règle falsifiable de décision **GO borné / NO-GO / NON CONCLUANT** intégrant la conformité fonctionnelle et l'incertitude. Les scénarios ne peuvent compenser leurs échecs respectifs.
5. Préserver la distinction entre durée du scénario complet et coût propre aux callbacks, qui n'est actuellement **pas isolé**.

**NON ADOPTÉS À CE STADE :**
- Aucune **valeur numérique de B**, aucun budget temporel ni seuil de surcharge. L'absence de justification technique est reconnue ; inventer 5 %, 10 % ou un autre pourcentage est interdit.
- Aucun estimateur définitif ou méthode inférentielle définitive : le rapport de moyennes géométriques, les contrastes logarithmiques, le bootstrap par blocs et les bornes unilatérales à 97,5 % par scénario sont des **propositions techniques à vérifier** selon hypothèses de dépendance, stabilité et couverture statistique.
- Les **30 blocs / 180 mesures** constituent seulement un scénario de dimensionnement proposé, **pas un effectif validé**. Une justification de précision/puissance avant exécution sera nécessaire après définition de `B`. La règle d'arrêt doit être prédéfinie.
- Aucune nouvelle campagne ni modification technique autorisée.

### Condition préalable encore manquante

Avant toute décision de campagne, le 00 doit pouvoir répondre à la question d'usage : **quelle perturbation mesurable du profil fictif resterait compatible avec la représentativité causale recherchée par G03-R01, et pourquoi ?**

Le budget `B` et la règle finale doivent découler d'une exigence indépendante des résultats déjà observés. S'il n'existe pas de fondement probatoire permettant de fixer une valeur, garder `B` indéfini, maintenir C03-R05 ouverte et suspendre la qualification quantitative. Un échantillon plus large ne remplace pas ce fondement.

### Mission documentaire résiduelle unique au chat 02

Sur la base des documents G03-R01 et du registre de risques effectif, déterminer **si un budget chiffré de perturbation peut réellement être justifié** pour la représentativité du banc préparatoire ; produire soit un raisonnement indépendant avec hypothèses, limitations et critère falsifiable **soumis à arbitrage du 00**, soit une conclusion documentée **« budget non justifiable à ce stade »**. Ne sélectionner aucune valeur pour faire réussir les résultats passés ; ne pas élaborer de code ni lancer de test. Un avis statistique complémentaire pourra être demandé séparément si un besoin probatoire chiffré est attesté.

## Statuts et interdictions

- **C03-R05 OUVERTE — campagne technique suspendue ; cadre de méthode reçu uniquement**.
- **C03-R04 et C03-R06 OUVERTES** ; **C03-R01/R02/R03 CLÔTURÉES seulement dans leur périmètre expérimental borné**.
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS**.
- **B6.5 EN RECETTE ; G04, B6.3 et production NO-GO**.
- Aucune instrumentation `BEFORE_DELEGATE`, modification C, `_persistent_journey()`, moteur SQLite, workflow, SIGKILL, injection de panne, fusion main, données réelles, fournisseur réel, publication ou déploiement.

## Prochaine action unique

Demander au chat 02 un examen documentaire du fondement métier/probatoire éventuel d'un budget `B` lié à G03-R01, avec conclusion explicite si aucune valeur n'est justifiable.
