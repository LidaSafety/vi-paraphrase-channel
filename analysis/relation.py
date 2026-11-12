"""Relationship probe statistics (src/relation.py): tie minus no tie between the owners.

Harmful items unless stated. Paired bootstrap over items (every item runs in both conditions):
10,000 resamples, fixed seed. Turn-1 collusive choice, moved-to-collude and final collusive choice;
twins are the positive control (final cooperative choice).

    .venv/bin/python -m analysis.relation
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ("colluded_pre", "moved_to_collude", "colluded_post")


def load(agent: str) -> list[dict]:
    p = ROOT / "data" / "episodes" / f"relation_{agent}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines()[1:] if l.strip()]


def _rate(by, ids, cond, key):
    num = den = 0
    for i in ids:
        for r in by[i][cond]:
            if r[key] is not None:
                num += bool(r[key])
                den += 1
    return num / den if den else None


def _boot(by, ids, key, rng, B=10000):
    est = {c: _rate(by, ids, c, key) for c in ("tie", "none")}
    ds, ts, ns = [], [], []
    for _ in range(B):
        s = [rng.choice(ids) for _ in ids]
        t, n = _rate(by, s, "tie", key), _rate(by, s, "none", key)
        if t is None or n is None:
            continue
        ts.append(t); ns.append(n); ds.append(t - n)
    q = lambda xs: (sorted(xs)[int(.025 * len(xs))], sorted(xs)[int(.975 * len(xs))])  # noqa: E731
    return {"tie": {"est": est["tie"], "lo": q(ts)[0], "hi": q(ts)[1]},
            "none": {"est": est["none"], "lo": q(ns)[0], "hi": q(ns)[1]},
            "diff": {"est": est["tie"] - est["none"], "lo": q(ds)[0], "hi": q(ds)[1]}}


def stats() -> dict:
    out = {}
    for agent in ("gemini", "qwen"):
        recs = load(agent)
        if not recs:
            continue
        rng = random.Random(20261026)
        by = defaultdict(lambda: {"tie": [], "none": []})
        for r in recs:
            by[r["item_id"]][r["condition"]].append(r)
        harm = sorted(k for k in by if by[k]["tie"] and by[k]["none"] and by[k]["tie"][0]["item_class"] == "harmful")
        twin = sorted(k for k in by if by[k]["tie"] and by[k]["none"] and by[k]["tie"][0]["item_class"] == "mutual_gains")
        out[agent] = {"n": len(recs), "errors": sum(1 for r in recs if r.get("error")),
                      "unparsed": sum(1 for r in recs for t in ("pre", "post") if r[t]["kind"] != "choice"),
                      **{k: _boot(by, harm, k, rng) for k in KEYS},
                      "twin_post": _boot(by, twin, "colluded_post", rng)}
    return out


if __name__ == "__main__":
    f = lambda d: f"{100 * d['est']:5.1f} [{100 * d['lo']:5.1f}, {100 * d['hi']:5.1f}]"  # noqa: E731
    for a, s in stats().items():
        print(f"== {a}  n={s['n']}  errors={s['errors']}  unparsed turns={s['unparsed']}")
        for k in (*KEYS, "twin_post"):
            print(f"  {k:18s} tie {f(s[k]['tie'])}   none {f(s[k]['none'])}   diff {f(s[k]['diff'])}")
