# Décision 00 — SEC-01 R1-RD01 — C03-R06 : cohérence comptable xDelete

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `57488c0c84265f6bf22c4c33770dc87f9b388280`  
**Autorité :** 00 — Pilotage et gouvernance  
**Chantier prioritaire unique :** C03-R06, première classe négative des compteurs de suppression du prototype fictif.

## Sources consultées et constat

- Avis documentaire du chat 02 transmis au 00 le 25 octobre 2026 : réutiliser la couverture négative antérieure C03-R01 à R04 ; proposer quatre classes complémentaires, en priorité incohérence `xDelete`.
- Code `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` vérifié sur le HEAD de départ : `validate_deletion_attribution(deletion)` rejette les compteurs positifs `ambiguous`, `no_match`, `native_errors` et `not_closed`, mais **ne vérifie pas explicitement** `events = attributed + ambiguous + no_match + native_errors + not_closed`, non-négativité et typage des champs. Un exemple purement synthétique `events=6, attributed=5`, autres compteurs à zéro, ne suffit pas à provoquer son rejet isolément. Cela n'établit **pas** qu'un certificat complet erroné a été observé.
- Code `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c` : `attribute_delete()` incrémente `deletion_events` puis classe chaque événement natif selon attribution, erreur, absence de correspondance, ambiguïté ou fermeture non attestée. Les retours natifs sont conservés.
- Tests existants inspectés : `test_c03_passive.py`, `test_c03_r02.py`, `test_c03_r03.py`, `test_c03_r04.py`. Couvrent notamment incarnations, ambiguïtés, erreurs `xDelete`, retours `xClose` et nettoyage des buffers. Ne pas recopier ces cas.
- Dernier jalon de référence : clôture ciblée C03-R04 `b65-http/DECISION-00-SEC01-RD01-C03-R04-CLOTURE-CIBLEE-20261025.md`, HEAD de départ `57488c0c84265f6bf22c4c33770dc87f9b388280`; CI n°199 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40238011587 au commit `2e3f8f09eccc857b5a4980e1d14eb9a6224d2360` : `completed/success`, 258 exécutions réussies (pas 258 scénarios distincts).
- Aucun nouveau test ni nouveau résultat CI exécuté par le 00 à l'occasion de cet arbitrage.

## Décision du 00

**GO TECHNIQUE CONDITIONNEL POUR UN PREMIER LOT C03-R06 STRICTEMENT LIMITÉ AUX COMPTEURS xDelete.** C03-R06 **reste ouverte** et sa clôture n'est pas autorisée a priori.

### Contrat falsifiable du lot

Pour des champs entiers non négatifs, exiger explicitement :

```
events == attributed + ambiguous + no_match + native_errors + not_closed
```

Un certificat positif ne peut être délivré si `attributed != events` ou si l'une des catégories d'anomalie est non nulle ; refuser de manière contrôlée les champs obligatoires absents, types incompatibles, compteurs négatifs, déséquilibres et éventuellement valeurs incohérentes dépassant le total.

Ne pas présumer de la validité d'une entrée à partir du seul fait que ses quatre compteurs d'anomalie sont nuls. Une entrée mal formée doit être rejetée comme donnée probatoire invalide, sans `KeyError` ou `TypeError` non traité dans la validation ciblée.

### Mandat unique au chat 01

1. Inspecter instructions et HEAD, code actuel et tests existants avant modification ; confirmer l'appel de ce validateur sur le chemin réel menant à la certification et identifier l'endroit où un résultat positif pourrait autrement être émis.
2. Ajouter des tests synthétiques ciblés qui exercent le validateur réel avec : cas cohérent positif, déficit d'attributions à anomalies nulles, surcomptage, négatifs, valeur manquante, valeur de type invalide, anomalie positive cohérente, et vérification du refus contrôlé.
3. Faire la **plus petite correction Python nécessaire** à la cohérence comptable et au rejet explicite, sans réécrire le certificat, le décodeur, les méthodes VFS ou les mécanismes C03-R01 à R04.
4. Maintenir les invariants du banc fictif COMMIT normal : certificat `RECONSTRUIT_BANC_FICTIF`, références S↔A/B, six suppressions attribuées sur six, intégrité `ok/ok`, DELETE/FULL et régression C03-R01 à R04. Aucun résultat natif SQLite ne doit être transformé par l'observation.
5. Fournir rapport versionné, diff limité, tests locaux réellement exécutés, CI sur commit exact, éventuels échecs intermédiaires et limites probatoires. En cas d'impossibilité d'effectuer le contrôle sans élargir le périmètre, arrêter et remonter un NO-GO motivé.
6. Préparer la réception indépendante par le chat 03 avant tout arbitrage de clôture.

**Autres classes C03-R06 (fragments mal formés, pointeurs corrompus, cycle de vie contradictoire) : hors de ce premier lot.** Aucune clôture globale C03-R06 ne pourra découler automatiquement d'une seule correction comptable.

## Restrictions et statuts

- **C03-R01 à R04 : clôturées dans leurs seuls périmètres expérimentaux fictifs.**
- **C03-R05 : ouverte, campagne quantitative suspendue faute de budget B justifiable.**
- **C03-R06 : ouverte, premier lot comptable autorisé.**
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1, P0-01 : ouverts**.
- **B6.5 en recette ; G04, B6.3 et production NO-GO.**
- Aucune modification wrapper C, SQLite, workflow ou métier ; aucune instrumentation `BEFORE_DELEGATE`, injection de panne, SIGKILL, G04, données réelles, fournisseur réel, fusion main, publication ni déploiement.

## Prochaine action unique

Transmettre au chat 01 ce mandat de correction comptable `xDelete` C03-R06, puis préparer les preuves pour réception indépendante par le chat 03.
