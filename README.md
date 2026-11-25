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

## Conclusion pour Bold

Pas d'intégration en l'état : le sport vient déjà sans erreur de Strava, Hevy et Garmin, et c'est un
modèle Python de près de 1 Go alors que Bold tourne en Next.js sur Vercel. Piste non testée :
l'apprentissage à partir de réponses confirmées (`laya.Learner`), par exemple pour repérer une
blessure dans des notes libres.
