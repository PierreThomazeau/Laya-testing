import time, json
from laya import Router

router = Router()
questions = {
    "sport": {"type": "choice", "instructions": "Quel sport décrit cette séance ?",
              "criteria": {"course": "course à pied, footing, fractionné, trail",
                           "muscu": "musculation, haltères, développé couché, squat",
                           "velo": "vélo, cyclisme, home trainer",
                           "natation": "natation, piscine, longueurs"}},
    "effort": {"type": "score", "instructions": "Quelle intensité ressentie ?",
               "criteria": ["facile", "modéré", "très dur"]},
    "douleur": {"type": "noul", "instructions": "La personne signale-t-elle une douleur ou une blessure ?"},
}
textes = [
    "Footing tranquille de 8 km au bord du canal, jambes légères.",
    "Séance pecs-triceps, développé couché 4x8 à 80 kg, j'étais cramé à la fin.",
    "Fractionné 10x400 m, gros mal au genou droit sur les dernières répétitions.",
    "40 longueurs à la piscine, rien de spécial.",
    "Sortie vélo de 60 km avec du dénivelé, les cuisses ont brûlé dans la dernière côte.",
]
for t in textes:
    t0 = time.time()
    r = router.predict(t, questions)
    ms = (time.time() - t0) * 1000
    a = r["answers"]
    print(f"\n{t}\n  modèle={r['routing']['model']}  {ms:.0f} ms")
    print("  " + json.dumps(a, ensure_ascii=False, default=str)[:600])
