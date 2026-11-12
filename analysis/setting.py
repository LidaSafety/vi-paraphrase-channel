"""Workplace versus market tasks (Track 2.1): harmful items, raw channel, all task episodes pooled.

Rates and the workplace-minus-market difference carry 95% intervals from a bootstrap that resamples
items within each setting (10,000 resamples, fixed seed). Also the Spearman rank agreement between the
two agents' per-family message-induced rates.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKPLACE = {"no_poach", "review_ring", "budget_padding"}
FILES = ("episodes_{a}", "workflow_episodes_{a}", "ext_episodes_{a}")


def _episodes(agent: str) -> list[dict]:
    out = []
    for f in FILES:
        p = ROOT / "data" / "episodes" / (f.format(a=agent) + ".jsonl")
        out += [json.loads(l) for l in p.read_text().splitlines()[1:] if l.strip()]
    return out


def stats(items: dict[str, dict], B: int = 10000, seed: int = 20261026) -> dict:
    rng = random.Random(seed)
    res: dict = {}
    fam_moved: dict = {}
    for a in ("gemini", "qwen"):
        by = defaultdict(list)
        for r in _episodes(a):
            if r["channel"] == "raw" and r["item_class"] == "harmful":
                by[r["item_id"]].append(r)
        wi = [k for k in by if items[k]["family"] in WORKPLACE]
        mi = [k for k in by if items[k]["family"] not in WORKPLACE]
        res[a] = {}
        for key in ("moved_to_collude", "colluded_post"):
            def rate(ks):
                return sum(sum(bool(r[key]) for r in by[k]) for k in ks) / sum(len(by[k]) for k in ks)
            w, m = rate(wi), rate(mi)
            ws, ms, ds = [], [], []
            for _ in range(B):
                bw = [rng.choice(wi) for _ in wi]
                bm = [rng.choice(mi) for _ in mi]
                ws.append(rate(bw)); ms.append(rate(bm)); ds.append(ws[-1] - ms[-1])
            q = lambda xs: (sorted(xs)[int(.025 * B)], sorted(xs)[int(.975 * B)])  # noqa: E731
            res[a][key] = {"workplace": {"est": w, "lo": q(ws)[0], "hi": q(ws)[1]},
                           "market": {"est": m, "lo": q(ms)[0], "hi": q(ms)[1]},
                           "diff": {"est": w - m, "lo": q(ds)[0], "hi": q(ds)[1]}}
        fam = defaultdict(list)
        for k, v in by.items():
            fam[items[k]["family"]] += v
        fam_moved[a] = {f: sum(bool(r["moved_to_collude"]) for r in v) / len(v) for f, v in fam.items()}
    fs = sorted(fam_moved["gemini"])
    rk = {a: {f: i for i, f in enumerate(sorted(fs, key=lambda f: fam_moved[a][f]))} for a in fam_moved}
    n = len(fs)
    res["spearman_moved"] = 1 - 6 * sum((rk["gemini"][f] - rk["qwen"][f]) ** 2 for f in fs) / (n * (n * n - 1))
    return res
