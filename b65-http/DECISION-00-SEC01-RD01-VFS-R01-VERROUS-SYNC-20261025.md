# Décision 00 — SEC-01 R1-RD01 — Qualification ciblée des effets de verrouillage et de synchronisation VFS N/W

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD vérifié avant décision :** `7b67d412721e62e5c55b192c52d4e97a41627ba0`  
**Chantier prioritaire unique :** effets transactionnels observables des verrous et synchronisations dans le profil rollback-DELETE multi-bases.

## Sources vérifiées

- PV indépendant 03 : `b65-http/PV-03-SEC01-RD01-VFS-R01-NW-20261025.md` (réception favorable de la comparaison fonctionnelle, avec réserves).
- Banc : `b65-http/rd01-vfs-step1/vfs_r01_compare.py`.
- Wrapper : `b65-http/rd01-vfs-step1/atlas_rd01_vfs.c`.
- CI historique n°129 : https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40210414951 — `completed/success`, commit testé `88de630acae24f8d960c6d4089dd8f21d7d3a630`, **224 exécutions réussies**, non nécessairement 224 scénarios distincts.
- Avis du chat 02 du 25 octobre 2026 : GO conditionnel ciblé sur préservation des effets de verrouillage/synchronisation, sans neutralité générale ni G04.

## Décision du 00

**GO CONDITIONNEL POUR UNE SEULE QUALIFICATION COMPLÉMENTAIRE : parité des effets transactionnels observables de verrouillage et synchronisation entre VFS native N et wrapper W existant**, sur un banc local fictif en rollback-DELETE, deux bases SQLite, `ATTACH`, `BEGIN IMMEDIATE`, `synchronous=FULL`.

La comparaison fonctionnelle N/W préexistante **demeure reçue et clôturée** ; pas de duplication de son scénario normal comme nouveau chantier.

### Travaux limités autorisés au chat 01

1. Concevoir avant exécution un **protocole falsifiable et borné** : mêmes moteurs/versions, mêmes fichiers fictifs indépendants pour N et W, mêmes SQL, paramètres et contrôle de concurrence (deux connexions et, si utile, processus enfants terminés proprement).
2. Choisir des entrelacements déterministes avec **barrières au niveau du banc Python, hors callbacks SQLite/VFS** pour démontrer qu'une transaction active exclut une écriture concurrente incompatible, puis que l'opération redevient possible après `COMMIT` ou `ROLLBACK` normal. Borner strictement les attentes et éviter tout blocage durable de runner.
3. Vérifier des retours et états comparables : succès ou `SQLITE_BUSY` attendu selon le scénario, état final des deux bases, invariants, `integrity_check`, maintien de `journal_mode=DELETE` et `synchronous=FULL`, absence de journaux résiduels après fermeture propre. Toute différence N/W inexpliquée sur l'exclusion, les résultats ou codes d'erreur rend la parité **NON QUALIFIÉE**.
4. Caractériser exactement les informations de synchronisation que la méthode permet d'attester : `xSync` visible uniquement côté W, délégation présente dans le code, mais **aucune comparaison événementielle native N** ni preuve de persistance physique sans mesure indépendante. Une propriété non mesurée reste `NON DÉMONTRÉE`.
5. Analyser l'effet observateur, la concurrence et les limites sans inventer une égalité temporelle. Les différences de durée doivent être rapportées avec contexte ; seules, elles ne démontrent pas une violation de verrou ou de synchronisation.
6. Modifier si nécessaire **uniquement le banc fictif et les tests associés**, plus documentation probatoire. Tests locaux et CI non destructifs autorisés dans ce périmètre, à rattacher aux SHA précis et à rapporter séparément. Si le protocole n'est pas fiable, interrompre cette qualification avec un NO-GO motivé, plutôt que multiplier des essais.
7. Livrer un rapport GitHub avec matrice `recevable / divergence / non mesuré`, critères falsifiables, résultats attribués à N et W, limites, recommandation GO/NO-GO et transmission en recette indépendante au chat 03 avant nouvel arbitrage du 00.

### Interdictions

- **Wrapper C `atlas_rd01_vfs.c` inchangé** ; pas d'extension VFS V2/V3, pas de nouvelle instrumentation de callback ni synchronisation ajoutée dans les callbacks.
- Aucun `SIGKILL`, aucun crash, injection de panne, corruption volontaire, coupure, arrêt forcé au milieu du COMMIT, aucune expérimentation G04.
- Aucun changement ni exécution de `LocalIdentityBridge._persistent_journey()` dans ce mandat, aucun changement applicatif ni de moteur SQLite, aucune nouvelle dépendance externe non approuvée.
- Pas de fusion `main`, activation fournisseur, données réelles, secret, achat, publication ou modification du site public.

## Limite des décisions de sûreté

L'expérience peut qualifier **les effets opérationnels observables des verrous** en COMMIT normal et les exigences de configuration/synchronisation visibles ; elle **ne peut pas à elle seule prouver** : la parité événementielle des I/O native/wrapper, l'équivalence générale du wrapper, le timing absolu, la durabilité physique en cas de panne, l'atomicité d'un arrêt causal, ni l'équivalence du chemin métier.

**VFS-R01 et G03-R06 restent OUVERTES** jusqu'à avis indépendant puis nouvelle décision, même si le scénario de contention réussit. **G03 préparation reçue avec réserves ; G04 NO-GO ; G05 global PARTIEL ; R1-RD01 et P0-01 OUVERTS ; R1-C01 PARTIEL ; R1 OUVERTE ; B6.5 EN RECETTE ; B6.3 et PRODUCTION NO-GO.**

## Prochaine action unique

Transmettre au chat 01 cette autorisation limitée de comparaison des effets transactionnels N/W sur banc fictif, avec protocole borné, puis demander une réception indépendante par 03 avant toute autre décision technique.
