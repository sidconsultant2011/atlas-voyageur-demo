# Décision 00 — SEC-01 R1-RD01 — Porte documentaire C03-R05-P1

**Date :** 25 octobre 2026  
**Branche autorisée :** `feature/b6-5-cartographie-interactive`  
**HEAD contrôlé avant décision :** `f864aa51c86db0ca6254e401cb23ce4327b13355`  
**Chantier prioritaire unique :** C03-R05-P1 — définition **préalable** des critères de perturbation admissible et de décision.

## Références et état vérifiés

- Arbitrage du 00 : `b65-http/DECISION-00-SEC01-RD01-C03-R05-ARBITRAGE-20261025.md` : **parité fonctionnelle N/W/C03 bornée et caractérisation descriptive reçues ; C03-R05 maintenue ouverte**.
- Protocole expérimental : `b65-http/SEC01-RD01-C03-R05-PROTOCOLE-20261025.md` : aucun seuil chiffré adopté.
- CI n°186 https://github.com/sidconsultant2011/atlas-voyageur-demo/actions/runs/40234530686 : `completed/success` sur `d5248e4510c1c3502138a5bf62f1213ba858e8fd` ; 253 exécutions selon les preuves précédemment réceptionnées ; 18 durées sur 6 couples scénario/mode ; cette CI ne démontre **pas** une neutralité temporelle générale.
- Avis documentaire du chat 02 reçu le 25 octobre 2026 : **suspendre les campagnes de mesure C03-R05 jusqu'à définition et validation préalable par le 00 d'une borne de perturbation, d'un estimateur et d'une règle de décision prenant en compte l'incertitude**. Aucun nouveau test ou changement de code n'est attesté dans cet avis.

## Décision explicite du 00

**GO DOCUMENTAIRE C03-R05-P1** pour élaborer une proposition de **contrat de qualification temporelle borné**.

**NO-GO À TOUTE NOUVELLE CAMPAGNE DE MESURE, MODIFICATION DE CODE OU INSTRUMENTATION** tant que le 00 n'a pas arrêté les critères nécessaires. Les mesures existantes restent des observations descriptives ; elles ne servent pas à choisir a posteriori un seuil qui les ferait réussir.

### Mandat documentaire unique au chat 02 — Sécurité P0

Préparer une proposition autonome de porte C03-R05-P1, destinée à l'arbitrage 00, contenant :

1. **Profil précis :** Linux et bibliothèque SQLite identifiés, deux bases fictives ATTACH, DELETE/FULL, scénarios COMMIT/ROLLBACK et contention ; limites de comparabilité des configurations N (native), W (témoin), C03 (expérimentale).
2. **Budget proposé, à justifier :** préciser quel niveau de perturbation temporelle serait admissible **pour la représentativité du banc fictif**, et selon quel fondement technique. Si aucune valeur numérique n'est justifiable, formuler ce manque explicitement et proposer la voie de décision 00 ; **ne pas inventer un seuil**.
3. **Estimateur et unité :** définir à l'avance comment comparer C03 à N sur chacun des scénarios, notamment `delta=(T_C03-T_N)/T_N`, la statistique retenue et la prise en compte de W comme témoin secondaire.
4. **Incertitude et décision :** proposer méthode d'échantillonnage, taille et plan de répétition justifiés, environnement/ordre/contrôle du bruit, règle GO / NO-GO / NON CONCLUANT établie avant exécution, et traitement conservateur des dépassements ou divergences fonctionnelles. Ne pas confondre une estimation centrale avec une borne supérieure de surcoût.
5. **Périmètre d'observation :** identifier ce que mesure réellement le chronomètre existant (scénario complet) et ce qu'il exclut, sans prétendre isoler les callbacks `xWrite`, `xSync`, `xClose`. Toute instrumentation nouvelle exige un arbitrage 00 distinct, avant exécution.
6. **Traçabilité :** sources du dépôt, hypothèses, critères non définis, risques et limites, et décision 00 encore nécessaire avant nouvelle campagne.

**Livrable attendu :** note documentaire `C03-R05-P1 — proposition de budget et protocole de décision` avec recommandation de GO/NO-GO pour passer ultérieurement à des mesures ; ne pas présenter cette note comme un budget approuvé.

### Statuts et restrictions

- **C03-R05 OUVERTE — campagne technique suspendue, travail documentaire P1 seul autorisé**.
- **C03-R04 et C03-R06 OUVERTES** ; **C03-R01 à R03 CLÔTURÉES uniquement dans le périmètre expérimental fictif**.
- **C03-3 global, G03-R01, VFS-R01, G03-R06, R1-RD01, R1 et P0-01 OUVERTS** ; G05 global et R1-C01 PARTIELS ; B6.5 EN RECETTE ; **G04, B6.3 et production NO-GO**.
- **Interdits :** nouvelle CI de mesure, modification des wrappers C, du moteur SQLite, du code métier ou du workflow, instrumentation `BEFORE_DELEGATE`, SIGKILL, injection de panne, données personnelles réelles, fournisseur réel, fusion main, publication et déploiement.

## Prochaine action unique

Transmettre au chat 02 la décision C03-R05-P1 et lui demander de formaliser le contrat de qualification temporelle sans produire de nouvelles mesures ni fixer de seuil arbitraire.
