# Décision 00 — SEC-01 R1-RD01 — Référence préparatoire N/W et étude documentaire G03-R01

**Date :** 25 octobre 2026  
**Projet :** ATLAS VOYAGEUR — B6.5  
**Branche :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `117a65ad88fbe9fd0127271f08b60a5ae745d591`  
**Chantier prioritaire unique suivant :** étude documentaire du contrat d'attestation causale G03-R01.

## Sources et état attesté

- Avis du chat 02 — « Avis après qualification des verrous N/W », daté du 25 octobre 2026.
- PV indépendant reçu : `b65-http/PV-03-SEC01-RD01-VFS-R01-VERROUS-SYNC-20261025.md`.
- CI n°135 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40212661980 ; `completed/success`, commit testé `fc6eded13fa15b8776b12dd0cd494349d0a2e906`, **225 exécutions réussies**, non nécessairement 225 scénarios distincts.
- Wrapper C existant consulté : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`.
- Les tests N/W antérieurs montrent des résultats équivalents dans le profil Linux SQLite 3.45.1, bases fictives `ATTACH`, rollback-DELETE, FULL, `BEGIN IMMEDIATE`, COMMIT et ROLLBACK normaux, contention contrôlée entre deux connexions dans un même processus.
- Ces preuves ne mesurent pas une identité des appels I/O internes natifs, une neutralité temporelle absolue ou la durabilité après panne.

## Arbitrage du 00

**GO : conserver le banc VFS N/W comme référence expérimentale préparatoire LIMITÉE au profil testé.** La comparaison fonctionnelle et la qualification de contention déjà réceptionnées restent clôturées dans leur sous-périmètre ; pas de répétition sans besoin probatoire nouveau.

**GO DOCUMENTAIRE UNIQUEMENT : G03-R01, contrat d'attestation causale interne au COMMIT multi-fichiers.** Cette décision n'autorise aucune implémentation, aucun changement de code et aucune nouvelle expérimentation.

### Mission documentaire unique au chat 01

Rédiger un dossier de conception **sans réalisation** décrivant :

1. **Cible causale exacte** : distinguer la suppression du super-journal comme point logique documenté du COMMIT et les garanties réellement accessibles au niveau `xDelete`, avec hypothèses et limites.
2. **Association non ambiguë** : définir les éléments nécessaires à relier événement, transaction multi-bases, fichier super-journal, chemin canonique, handle et rôle SQLite. Séparer les propriétés présentes dans le wrapper des champs manquants ; ne pas prétendre qu'un identifiant de transaction est déjà attesté.
3. **Entrée versus retour du callback** : contrat d'événements `BEFORE_DELEGATE` et `AFTER_RETURN`, ordre, codes, opérations et identités requises. Le traçage actuellement post-délégation ne constitue pas une attestation d'entrée.
4. **Chaîne de preuve falsifiable** : conditions d'acceptation et d'échec, provenance, corrélation événementielle, conservation de la preuve et limites de sa synchronisation. Identifier les moyens potentiels de prouver un point interne sans temporisation ni simple marque externe Python.
5. **Neutralité et effets observateurs** : risques d'ordonnancement, latence, contention, nouvelles écritures ou synchronisations de trace, perte de méthode/garantie native, conséquences sur COMMIT, et garde-fous pour conserver les acquis N/W.
6. **Matrice d'arbitrage ultérieur** : faits établis, exigences non implémentées, non démontrés, critères GO/NO-GO d'une éventuelle instrumentation isolée, sans concevoir un GO automatique pour G04 ni valider une reprise après panne.

Confronter ce contrat au code et aux documents GitHub existants, notamment aux rapports G03 et à la conception VFS déjà présente, afin de **réutiliser sans dupliquer** leurs acquis. Distinguer une exigence, une proposition, un changement futur hypothétique et une preuve acquise.

**Livrable :** note documentaire GitHub versionnée sur la branche B6.5 avec références précises et une seule condition bloquante prioritaire à remonter au 00, pour avis de sécurité 02 et arbitrage explicite ultérieur.

### Interdictions

- Aucune modification du wrapper `atlas_rd01_vfs.c`, du banc, de ses tests, du code métier ou du workflow.
- Aucune compilation, aucun nouveau test local ou GitHub Actions demandé par ce mandat.
- Aucun `SIGKILL`, arrêt causal, panne simulée, barrière callback, expérimentation G04 ou manipulation de journaux chauds.
- Aucune activation fournisseur réel, fusion vers main, donnée personnelle réelle, achat, publication ou modification du site public.

## Statuts conservés

**G03 préparation reçue avec réserves ; G03-R01 OUVERTE ; VFS-R01 et G03-R06 OUVERTES ; G04 NO-GO ; G05 global PARTIEL ; R1-RD01 OUVERTE ; R1-C01 PARTIEL ; R1 OUVERTE ; P0-01 OUVERT ; B6.5 EN RECETTE ; B6.3 NO-GO ; PRODUCTION NO-GO.**

Les résultats N/W préparatoires ne qualifient ni `_persistent_journey()`, ni l'atomicité après panne, ni la synchronisation physique du stockage.

## Prochaine action unique

Transmettre au chat 01 le mandat d'étude documentaire G03-R01 et lui faire remettre un contrat d'attestation causale à arbitrer, sans développement ni injection.
