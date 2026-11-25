# Laya testing

Test du modèle [convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya) (Apache 2.0) :
un modèle qui répond à des questions fermées (choix, échelle, oui/non) sur un texte, avec des
probabilités, sans générer de texte.

## Lancer

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python test.py
```

Pour l'apprentissage continu : `.venv/bin/python learner_test.py results/learner_seed0.json 0`
(le dernier nombre choisit le découpage test / apprentissage).

Le premier lancement télécharge le modèle multilingue (environ 840 Mo). Hôtes à autoriser si le
réseau est filtré : `huggingface.co` et `us.aws.cdn.hf.co` (CDN des poids).

## Résultats (24/11/2026, CPU 4 cœurs, sans GPU, laya 0.5.3)

5 descriptions de séance en français, 3 questions (sport, effort, douleur). Texte français envoyé
automatiquement au modèle `multilingual`.

| Texte | Sport (proba) | Effort | Douleur (proba oui) |
|---|---|---|---|
| Footing 8 km, jambes légères | **vélo** 0,74, faux | modéré | 0,00, juste |
| Développé couché 4x8, « cramé » | muscu 0,99 | très dur, de peu | **0,82, fausse alerte** |
| Fractionné 10x400, mal au genou | **muscu** 0,43, faux (course 0,32) | modéré | 0,71, juste |
| 40 longueurs piscine | natation 0,90 | modéré | 0,00, juste |
| Vélo 60 km, « cuisses ont brûlé » | vélo 0,999 | modéré | **0,96, fausse alerte** |

- Sport : 3 sur 5. Les erreurs ont une probabilité plus basse, mais pas toujours (footing classé vélo à 0,74).
- Effort : « modéré » presque partout, peu utile.
- Douleur : confond fatigue normale (« cramé », « ça brûle ») et blessure.
- Vitesse : environ 250 ms par texte une fois chargé ; 100 s pour la première requête (téléchargement et chargement).

## Apprentissage continu avec `laya.Learner` (25/11/2026)

`laya.Learner` ne passe pas par l'encodeur testé plus haut : il réutilise le lecteur de vegaml (un
petit LLM de 0,8B, figé) et ajoute par question un petit classifieur, réentraîné à partir des réponses
confirmées. Ce classifieur ne remplace la réponse d'origine que s'il fait mieux en validation croisée.

Protocole (`learner_test.py`, données dans `data.py`) : 108 notes de séance écrites à la main pour
ce test, avec mes étiquettes (sport, douleur à surveiller oui / non, effort facile / modéré / très dur).
36 notes restent de côté pour mesurer, les 72 autres sont données comme réponses confirmées par paquets
de 24. Trois découpages différents (graines 0, 1, 2), moyennes ci-dessous.

| Exactitude sur 36 notes | départ | après 24 | après 48 | après 72 |
|---|---|---|---|---|
| Douleur (oui / non) | 67 % | 93 % | 93 % | **94 %** |
| Sport (4 choix) | 56 % | 58 % | 62 % | **82 %** |
| Effort (3 niveaux) | 42 % | 40 % | 55 % | **60 %** |

- **Douleur :** au départ il répond « non » à tout (les 36 notes avec douleur ratées sur les 3 essais).
  Après seulement 24 réponses, il fait la différence entre fatigue et douleur. Après 72 réponses,
  sur les 3 essais : 1 fausse alerte en tout, et 6 douleurs ratées sur 36 (83 % repérées).
- **Sport :** au départ le lecteur 0,8B fait moins bien que l'encodeur multilingue (56 % contre 3 sur 5).
  Il lui faut environ 72 réponses pour dépasser 80 %, et ça varie selon le découpage (69 à 89 %).
- **Effort :** reste moyen et instable (47 à 67 %). Mes propres étiquettes sont discutables sur cette
  question, et le texte ne dit souvent pas grand-chose de l'intensité.
- **Coût :** sans GPU (4 cœurs), chargement 5 s une fois le modèle en cache (82 s la toute première fois),
  environ 0,4 s par note, 50 à 70 s par réentraînement. Le réentraînement relit les notes avec le
  lecteur ; il tourne en arrière-plan en usage normal (`auto=True`, tous les 50 retours par défaut).

Limites : petit test (36 notes), notes et étiquettes écrites par moi, donc plus régulières que de
vraies notes. À refaire sur de vraies notes de séance avant d'en tirer une conclusion ferme.

Résultats bruts : `results/learner_seed*.json`.

## Conclusion pour Bold

Pas d'intégration en l'état pour le sport : il vient déjà sans erreur de Strava, Hevy et Garmin, et c'est un
modèle Python de près de 1 Go alors que Bold tourne en Next.js sur Vercel.

Piste intéressante : repérer une douleur dans les notes libres pour le Coach. Avec `laya.Learner`,
quelques dizaines de réponses confirmées suffisent ici. Il faudrait un petit service Python à part
(serveur avec au moins 2 à 4 Go de RAM, pas Vercel) et de vraies notes pour valider.
