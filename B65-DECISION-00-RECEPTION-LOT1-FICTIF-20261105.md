# 00 — B6.5 — Réception indépendante ciblée du lot 1 fictif

**Date :** 5 novembre 2026  
**Autorité :** 00 — Pilotage et gouvernance  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD avant décision, vérifié :** `373844940d49ab65061ae659e48e6e72eeeac038`

## Fondements de la décision

Le chat 03 a remis en conversation le PV `PV-03-B65-LOT1-FONCTIONNEL-FICTIF-20261105` avec verdict **FAVORABLE AVEC RÉSERVES**, sur revue du dépôt et des journaux GitHub. Aucun fichier PV autonome dans GitHub n'est présumé.

Contrôles du 00 réalisés directement dans GitHub :
- Comparaison du commit d'autorisation `0423321bb252d8c568a159e1c80c7bc3229fb08f` au commit livré `373844940d49ab65061ae659e48e6e72eeeac038` : **trois commits, deux fichiers seulement**, `RECETTE-B65-PARCOURS-COMPLET.html` et `b65-calculateur/simulation-ui.test.mjs`.
- CI n°253 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/42007178917, **completed/success** sur le SHA livré exact. Journaux du job `test` contrôlés : **116/116 JavaScript**, **11/11 SQLite**, **168/168 HTTP/identité/sécurité**, soit **295 exécutions**, pas nécessairement 295 scénarios distincts.
- CI n°251 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/42007013193, `completed/failure`. Incident antérieur de banc DOM `route-mode` documenté par le PV, sans effacement de l'échec.
- CI n°252 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/42007080269, `completed/success`.
- `RECETTE-B65-PARCOURS-COMPLET.html` au SHA technique : règle `.route[hidden]{display:none}` présente.
- `simulation-ui.test.mjs` au SHA technique : assertions de simulation incluant les identifiants et horaires observées dans le PV. Le DOM simulé ne rend pas le CSS réel.
- Aucun test manuel iPhone ni PC au commit final n'est attesté. Aucun nouveau test local, CI ou navigateur n'a été lancé par le 00.

## Décision du 00

**GO — RÉCEPTION CIBLÉE AVEC RÉSERVES DU LOT 1 B6.5, POUR SA COUVERTURE FONCTIONNELLE AUTOMATISÉE.**

Le lot fictif assemble dans la page QA existante la sélection AV103, l'origine simulée Paris/Rozay, le trajet schématique vers Orly, la recommandation du contrôleur et les états de retard, annulation, atterrissage, indisponibilité et données périmées. Les mentions de données MOCK, de provenance non renseignée et de date/heure de simulation évitent d'en faire une information aérienne réelle. Les tests automatisés couvrent aussi la suppression d'un conseil en cas de données ou de trajet indisponibles.

**La recette visuelle PC et iPhone du lot final reste à réaliser.** La présence d'une propriété DOM `hidden` et de CSS adapté ne prouvent pas le rendu dans Safari ou un autre moteur navigateur. Le lot ne comporte ni recherche libre d'adresse ni itinéraire géocodé, ni terminal/parking qualifié, ni couverture internationale complète, ni fournisseur réel.

La réception ne constitue **ni la clôture B6.5 globale**, ni un GO fournisseur, ni un GO de production, ni une autorisation de publication sur `voyageur.atlascore.eu`.

## Mandat unique au chat 03 : recette visuelle bornée du lot reçu

**GO de recette manuelle ciblée PC/iPhone, sans changement de code ni publication.**

1. Ouvrir localement ou dans un environnement de prévisualisation **non public, sans fournisseur réel** la page `RECETTE-B65-PARCOURS-COMPLET.html` au commit technique `373844940d49ab65061ae659e48e6e72eeeac038`, et constater les dépendances réseau réelles de ce mode de prévisualisation avant emploi.
2. Vérifier en navigateur PC la sélection AV103, origine Paris/Rozay, changement d'origine et de scénario, état de retard, annulation, données périmées, trajet ou réseau simulé indisponible. Contrôler que le schéma est réellement masqué, qu'aucun ancien conseil/UTC n'apparaît, et que les étiquettes fictives et hypothèses restent visibles.
3. Réaliser les mêmes observations sur **iPhone Safari** avec contrôles tactiles et lisibilité mobile. Captures horodatées du nominal, du retard et d'une suspension si possibles, avec références du commit effectivement servi.
4. Rapporter séparément chaque environnement, appareil, version navigateur si connue, mode de prévisualisation, étapes, résultats, captures, anomalies et limites. **Ne pas annoncer PASS iPhone avant observation réellement attestée**.
5. Ne pas relancer de CI par défaut, ne pas reprendre AC-08/AC-13/R1-C01, ne pas activer Geoapify ni AeroDataBox, ne pas modifier `main`, le DNS, le site public ou le workflow.
6. Si l'accès iPhone à une prévisualisation locale non publique n'est pas possible sans nouveau déploiement, **documenter le blocage et demander arbitrage du 00** ; ne pas créer de nouveau site ni exposer la branche sans autorisation.

## Statuts après décision

- **Lot 1 B6.5 : RÉCEPTION FONCTIONNELLE AUTOMATISÉE FAVORABLE AVEC RÉSERVES**.
- **Recette visuelle PC/iPhone du lot : À EFFECTUER**.
- **B6.5 global : EN RECETTE**, intégration réelle et internationale non qualifiée.
- AC-08, AC-13 : réceptionnés avec réserves dans le local fictif.
- R1-C01 : PARTIEL, **gel technique maintenu** ; R1-RD01/R1/P0-01 ouverts.
- B6.3, G04, production : **NO-GO**. B6.2-PUBLIC sur `main` inchangée.

## Prochaine action unique

Remettre au chat 03 le mandat de recette visuelle PC/iPhone du lot 1 au commit exact, sans publication.
