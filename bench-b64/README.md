# B6.4 — ÉCONOMIE ET CONNECTEURS — Banc de mesure 20 parcours

**Statut : banc prêt, aucune mesure réelle exécutée, aucun achat autorisé.**
**Branche isolée : `feature/b6-4-economie-connecteurs`**. Le projet B6.3 (référence PLATINE CHAMPAGNE) et `main` demeurent inchangés.

## Objet

Mesurer le coût facturé d'un **dossier d'accueil de voyageur**, de la recherche initiale à la fin du suivi. Distinguer les factures fournisseurs, les appels réseau, les rafraîchissements internes et les coûts non API. Ne jamais vendre des « appels API » à l'utilisateur final.

## Contenu du banc

- `cases.csv` : **20 parcours numérotés**, incluant vols ponctuels, retardés, annulés, vols sans numéro, ambiguïtés, erreurs et déconnexions.
- `events.csv` : journal immuable des observations de consommation et d'incidents ; vide au départ.
- `measure.py` : commandes standard Python pour initialiser le journal, y ajouter des mesures et calculer une synthèse.
- `PRICING-ASSUMPTIONS.md` : coûts à confirmer et conditions de licence.

## Sécurité et garde-fous

1. **Aucun accès API automatique** dans le banc ; aucune clé RapidAPI/Geoapify, aucune requête réseau et aucun paiement. Les événements sont saisis à partir des réponses/logs/quota fournisseurs réellement observés.
2. Ne jamais enregistrer de clé API, email de passager, nom, PNR ni adresse personnelle. Utiliser uniquement des aéroports, catégories et identifiants de tests non sensibles.
3. `api_units_reported` et `geo_credits_reported` : uniquement des consommations **rapportées ou déduites d'une grille tarifaire vérifiée pour l'endpoint exact**. En cas d'absence de preuve : champ vide ; ne jamais saisir une estimation comme mesure.
4. Une erreur HTTP 429/5xx est journalisée au même titre qu'un succès. Les relances consommatrices et la mise en cache sont explicites.
5. `planned_refreshes` est un objectif de scénario et non un appel réellement exécuté. Les coûts ne sont calculés qu'à partir des événements constatés.
6. Ne pas tester 20 vrais vols sans avoir préalablement vérifié les quotas et règles des fournisseurs. Autorisation humaine préalable à toute dépense ou test réel.
7. Ne pas interpréter l'affichage d'un vol comme un droit de redistribution commerciale : validation contractuelle fournisseur obligatoire.

## Utilisation locale

Dans le dossier `bench-b64`, exécuter :

```bash
python measure.py check
python measure.py add 01 AeroDataBox "/flights/..." 200 --units 2 --evidence "quota-dashboard-2026-10-22" --duration 300
python measure.py add 01 Geoapify "/v1/routing" 200 --credits 1 --evidence "geo-dashboard-2026-10-22"
python measure.py report
```

**Ces commandes sont des exemples de saisie, pas des consommations déjà mesurées.** Les valeurs doivent être remplacées par celles réellement observées. Le script refuse les cas inconnus et n'envoie aucun appel réseau.

Le journal génère une synthèse par dossier : appels, réussites/erreurs, unités AeroDataBox et crédits Geoapify **connus**, valeurs inconnues, durée réelle du suivi entre premier et dernier événement, et latence cumulée. Un rapport global ne peut pas être qualifié de « coût réel » si les valeurs facturées manquent.

## Recette/GO B6.4

- 20/20 dossiers renseignés avec résultats (y compris scénarios sans résultat) ;
- endpoints détaillés ; preuves de facturation exploitables, cas d'échecs tracés ;
- grille de facturation contractuelle confirmée et devise/taxes documentées ;
- droits d'usage commercial, cache, redistribution, attribution et notifications validés ;
- p50/p90/coût max par dossier, moyenne avec et sans échecs ; coûts Stripe et infrastructures séparés ;
- grille des packs seulement **après** rapprochement des coûts et validation juridique.

**Ne jamais fusionner B6.4 ni B6.3 vers `main` sans décision explicite.**
