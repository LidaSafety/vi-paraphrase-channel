"""Three pathways into collusion, per task family (Track 2.1). Harmful items only, no new data.

    spontaneous  main study, turn 1: the collusive option chosen before any message (raw channel)
    invited      main study: moved to the collusive option by the rival's message (raw channel)
    initiated    initiation probe: the agent sent the proposal itself

Per-family rates carry 95% intervals from a bootstrap over items in the family. Pathway agreement is
the Spearman correlation of item-level rates (72 harmful items), within an agent and between agents,
with a bootstrap over items. 10,000 resamples, fixed seed.

    .venv/bin/python analysis/pathways.py
"""

from __future__ import annotations

import random
from collections import defaultdict

from analysis.initiate import load as load_init
from analysis.setting import _episodes

PATHS = ("spontaneous", "invited", "initiated")
AGENTS = ("gemini", "qwen")
B = 10000
SEED = 20261026


def item_counts() -> dict:
    """agent -> path -> item_id -> (hits, n); and item_id -> family."""
    out: dict = {}
    fam: dict = {}
    for a in AGENTS:
        c = {p: defaultdict(lambda: [0, 0]) for p in PATHS}
        for r in _episodes(a):
            if r["channel"] != "raw" or r["item_class"] != "harmful":
                continue
            fam[r["item_id"]] = r["family"]
            for p, key in (("spontaneous", "colluded_pre"), ("invited", "moved_to_collude")):
                if r[key] is not None:
                    c[p][r["item_id"]][0] += bool(r[key])
                    c[p][r["item_id"]][1] += 1
        for r in load_init(a):
            if r["item_class"] == "harmful" and r["initiated"] is not None:
                c["initiated"][r["item_id"]][0] += r["initiated"]
                c["initiated"][r["item_id"]][1] += 1
        out[a] = c
    return out, fam


def _rank(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x: list[float], y: list[float]) -> float | None:
    rx, ry = _rank(x), _rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = sum((a - mx) ** 2 for a in rx) ** .5
    sy = sum((b - my) ** 2 for b in ry) ** .5
    return sxy / (sx * sy) if sx and sy else None


def _ci(est, xs):
    xs = sorted(v for v in xs if v is not None)
    return {"est": est, "lo": xs[int(.025 * len(xs))], "hi": xs[int(.975 * len(xs))]}


def stats() -> dict:
    C, fam = item_counts()
    rng = random.Random(SEED)
    ids = sorted(set.intersection(*(set(C[a][p]) for a in AGENTS for p in PATHS)))
    rate = {a: {p: {i: C[a][p][i][0] / C[a][p][i][1] for i in ids} for p in PATHS} for a in AGENTS}

    fams = sorted({fam[i] for i in ids})
    by_fam = {}
    for a in AGENTS:
        by_fam[a] = {}
        for p in PATHS:
            by_fam[a][p] = {}
            for f in fams:
                ks = [i for i in ids if fam[i] == f]
                agg = lambda s: sum(C[a][p][i][0] for i in s) / sum(C[a][p][i][1] for i in s)  # noqa: E731
                by_fam[a][p][f] = _ci(agg(ks), [agg([rng.choice(ks) for _ in ks]) for _ in range(B)])

    pairs = [(a, p, a, q) for a in AGENTS for i, p in enumerate(PATHS) for q in PATHS[i + 1:]]
    pairs += [("gemini", p, "qwen", p) for p in PATHS]
    corr = {}
    for a1, p1, a2, p2 in pairs:
        f = lambda s: spearman([rate[a1][p1][i] for i in s], [rate[a2][p2][i] for i in s])  # noqa: E731
        corr[f"{a1}.{p1}~{a2}.{p2}"] = _ci(f(ids), [f([rng.choice(ids) for _ in ids]) for _ in range(B)])
    return {"n_items": len(ids), "families": fams, "by_family": by_fam, "corr": corr}


if __name__ == "__main__":
    s = stats()
    print("harmful items", s["n_items"])
    for a in AGENTS:
        print(f"== {a}")
        for f in s["families"]:
            print(f"  {f:15s}", "  ".join(f"{p[:5]} {100 * s['by_family'][a][p][f]['est']:5.1f}" for p in PATHS))
    for k, v in s["corr"].items():
        print(f"  {k:40s} {v['est']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}]")
