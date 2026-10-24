# B6.5 — Recette horloge accélérée — 24 octobre 2026

**Statut : implémentée sur branche de recette, CI finale à confirmer.**

## Chaîne testée
`accelerated-journey.mjs` assemble :
1. un contrôleur `createJourneyController` avec horloge injectée et règle fictive d'expiration à 30 min ;
2. un tableau fictif `FlightContract` AeroDataBox V2 traité par `applyAeroDataBoxV2Offline` ;
3. une route Geoapify fictive de 45 min ;
4. un calcul indicatif de départ.

## Scénario de référence
- Heure initiale 14:05 UTC ; dernière observation fictive à 14:00 UTC.
- Initial : `indicative`, heure conseillée 17h25 Paris (15:25Z).
- +26 minutes simulées (14:31Z) : âge de donnée 31 min => `expired`, heure `null`, `unavailable`.
- Nouvelle observation fictive horodatée 14:31Z : `fresh`, conseil à nouveau disponible.
- Si l'estimation d'arrivée change à 16:05Z, nouvel horaire de départ conseillé à 17h40 Paris (15:40Z).
- Aucun événement `runwayTime` n'est promu au statut de piste confirmée.

## Vérification
`node --test b65-calculateur/*.test.mjs` dans GitHub Actions, sans appel fournisseur ni attente de 30 minutes.
6 tests ajoutés dans `accelerated-journey.test.mjs`.
Page QA indépendante : `RECETTE-B65-HORLOGE-ACCELEREE.html` (boutons +26 min, réception fictive, reset). Aucun test iPhone requis.

## Limites
La page simule le temps lors d'une action utilisateur ; **pas de minuterie active en arrière-plan**. Le contrôleur vérifie sa fraîcheur à chaque lecture. Aucun poll, aucune authentification, aucune connexion réseau fournisseur. Ce n'est pas un délai de rafraîchissement réel validé.
**B6.5 en recette ; B6.3 NO-GO ; aucun achat ; aucune fusion sur main ; site public inchangé.**
