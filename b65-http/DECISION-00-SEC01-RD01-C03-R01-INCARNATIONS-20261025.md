# Décision 00 — SEC-01 R1-RD01 — Traitement expérimental ciblé C03-R01

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `48eef5139980fd071be249230226e2bddc75f67f`  
**Chantier prioritaire unique :** sélection et validation univoques des incarnations A/B des journaux rollback du prototype C03-3.

## Sources vérifiées et état de départ

- Décision 00 de clôture ciblée C03-R02 : `b65-http/DECISION-00-SEC01-RD01-C03-R02-CLOTURE-CIBLEE-20261025.md`.
- Décodeur expérimental `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` : `reciprocal_certificate()` retient actuellement `journals = [max(matches, key=lambda r: r["generation"]) for matches in journal_sets]`. Le numéro de génération correspond à un enregistrement du banc, **pas** à un identifiant natif de transaction.
- CI historique de référence n°163 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40227116667 ; `completed/success` sur `40f7bf89b54dbee4cc167663d279c4d99d6a8b3c`, 240 exécutions réussies. Cette CI **ne démontre pas** une sélection univoque en cas d'incarnations concurrentes ou de cycles de vie ambiguës.
- Avis indépendant du chat 02 du 25 octobre 2026 : priorité unique **C03-R01**, GO conditionnel recommandé sur un traitement expérimental de sélection et de rejet des identités ambiguës, sans G04 ni attestation causale.

## Décision du 00

**GO TECHNIQUE CONDITIONNEL, STRICTEMENT LIMITÉ À C03-R01** sur le banc expérimental fictif C03-3, pour remplacer la sélection automatique par génération maximale par une décision probatoire univoque ou un **rejet bloquant**.

Le mandat ne porte **ni** sur un identifiant de transaction SQLite natif ni sur l'identité matérielle universelle des fichiers. L'objectif est de démontrer, au moyen des références S↔A/B et des informations de cycle de vie déjà disponibles, qu'un seul journal A et un seul journal B peuvent être attribués à S ; sinon, le certificat ne doit pas être émis.

### Mandat unique au chat 01

1. Lire les instructions applicables et contrôler le HEAD avant édition. Délimiter la modification au sélecteur/validateur d'incarnations de `b65-http/rd01-vfs-step1/c03-passive/c03_run.py` et aux tests ciblés nécessaires, sans toucher au wrapper C expérimental ni au wrapper principal. Si une instrumentation supplémentaire du cycle de vie s'avère nécessaire, **arrêter et demander un nouvel arbitrage**, plutôt que l'implémenter.
2. **Supprimer la dépendance probatoire au seul `max(generation)`.** Une incarnation est recevable seulement si les références réciproques sont compatibles, les écritures/masques et le cycle de vie observé sont cohérents, et qu'une seule incarnation candidate demeure par journal participant.
3. Préserver la distinction entre incarnation historique prouvée achevée et incarnation actuellement compatible ; ne pas rejeter arbitrairement un COMMIT normal du banc simplement parce que le registre comporte des entrées historiques. Ne pas convertir une génération plus élevée, un chemin, un nom, un timestamp ou un identifiant d'essai en preuve transactionnelle.
4. Cas falsifiables minimaux : (a) une seule incarnation A/B compatible → certificat possible sous autres contrôles ; (b) deux incarnations historiques discriminées par des preuves réciproques et du cycle de vie → seule incarnation effectivement prouvée recevable ; (c) deux incarnations indiscernables compatibles → rejet ; (d) journal A/B absent → rejet ; (e) liens S→A/B ou A/B→S incompatibles → rejet ; (f) incarnation remplacée, recréée ou incomplète sans continuité probante → rejet. Les cas synthétiques doivent solliciter la même validation Python que le chemin de production du certificat, avec assertions bloquantes.
5. Conserver sans régression les acquis C03-R02 : unicité des suppressions dans le registre, préservation des codes retour natifs et rejet Python de `no_match>0`, `ambiguous>0`, `native_errors>0` et `not_closed>0`.
6. Vérifier le COMMIT normal fictif S↔A/B, intégrité des deux bases, DELETE/FULL et les tests préexistants. Si l'identité unique ne peut être attestée avec les données disponibles, rendre **NON DÉMONTRÉ/NO-GO motivé**, sans assouplir le critère.
7. Rapporter le diff, tests locaux réellement exécutés et preuves GitHub Actions au **commit testé exact** ; produire un rapport de preuves versionné et soumettre le livrable au chat 03 pour recette indépendante avant toute décision de clôture C03-R01.

### Interdictions

Aucune modification de `b65-http/rd01-vfs-step1/c03-passive/c03_vfs.c`, `atlas_rd01_vfs.c`, des callbacks VFS, du moteur SQLite, du code métier, de `_persistent_journey()` ou du workflow. Aucune lecture intrusive de fichiers à chaud, aucune instrumentation `BEFORE_DELEGATE`, interruption, SIGKILL, injection de panne ni G04. Aucun traitement parallèle de C03-R03 à R06, fusion main, fournisseur réel, achat ou déploiement.

## Portée des résultats et statuts

**C03-R01 OUVERTE — traitement expérimental seulement autorisé**. C03-R02 demeure **clôturée dans son périmètre expérimental**. C03-3 global OUVERT ; C03-R03 à R06 OUVERTES ; G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS ; G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; R1-C01 PARTIEL ; B6.5 EN RECETTE ; B6.3 NO-GO ; production NO-GO.

Aucune nouvelle preuve technique ni test ne découle de cette autorisation documentaire seule.

## Prochaine action unique

Transmettre au chat 01 le mandat expérimental isolé C03-R01, avec rejet obligatoire des associations ambiguës, puis faire réceptionner indépendamment le résultat par le chat 03 avant tout nouvel arbitrage du 00.
