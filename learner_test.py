"""Apprentissage continu de laya (laya.Learner) sur des notes de séance en français.

36 notes gardées de côté pour mesurer, 72 données comme « réponses confirmées » par paquets de 24.
On mesure l'exactitude sur les 36 avant tout apprentissage, puis après 24, 48 et 72 réponses.
"""

import json
import random
import sys
import time

from laya import Learner

from data import NOTES, QUESTIONS, labels

SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 0
random.seed(SEED)
notes = NOTES[:]
random.shuffle(notes)
test, pool = notes[:36], notes[36:]
STEPS = [0, 24, 48, 72]


def evaluate(learner):
    ok = {q: 0 for q in QUESTIONS}
    readout = {}
    fp = fn = 0
    t0 = time.time()
    for note in test:
        out = learner.decide(note[0])["answers"]
        want = labels(note)
        for q in QUESTIONS:
            ok[q] += out[q]["answer"] == want[q]
            readout[q] = out[q]["readout"]
        if out["douleur"]["answer"] and not want["douleur"]:
            fp += 1
        if not out["douleur"]["answer"] and want["douleur"]:
            fn += 1
    return {
        "exactitude": {q: round(ok[q] / len(test), 3) for q in QUESTIONS},
        "lecture": readout,
        "douleur_fausses_alertes": fp,
        "douleur_ratees": fn,
        "ms_par_note": round(1000 * (time.time() - t0) / len(test)),
    }


t0 = time.time()
learner = Learner(QUESTIONS, auto=False)
print(f"chargé en {time.time() - t0:.0f} s", flush=True)
print(f"test : {len(test)} notes, dont {sum(n[2] for n in test)} avec douleur", flush=True)

results = []
fed = 0
for step in STEPS:
    for note in pool[fed:step]:
        learner.feedback(note[0], labels(note))
    fed = step
    t1 = time.time()
    if step:
        learner.step(min_rows=1)
    learn_s = round(time.time() - t1, 1)
    r = {"graine": SEED, "reponses_confirmees": step, "apprentissage_s": learn_s, **evaluate(learner)}
    st = learner.status()["questions"]
    r["validation_croisee"] = {q: st[q]["cross_validated_accuracy"] for q in QUESTIONS}
    results.append(r)
    print(json.dumps(r, ensure_ascii=False), flush=True)

json.dump(results, open(sys.argv[1] if len(sys.argv) > 1 else "results_learner.json", "w"),
          ensure_ascii=False, indent=2)
