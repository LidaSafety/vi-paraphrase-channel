"""Initiation probe statistics (src/initiate.py). Rates over harmful items unless stated; 95%
intervals from a bootstrap that resamples items (10,000 resamples, fixed seed).

    .venv/bin/python analysis/initiate.py     # prints a summary; paper.py imports stats()
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKPLACE = {"no_poach", "review_ring", "budget_padding"}


def load(agent: str) -> list[dict]:
    p = ROOT / "data" / "episodes" / f"initiate_{agent}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines()[1:] if l.strip()]


def _rate(by: dict, ids: list, key: str, cond=None) -> float | None:
    num = den = 0
    for k in ids:
        for r in by[k]:
            if r[key] is None or (cond and not cond(r)):
                continue
            den += 1
            num += bool(r[key])
    return num / den if den else None


def _boot(by, ids_a, key, ids_b=None, cond=None, B=10000, seed=20261026):
    rng = random.Random(seed)
    est_a = _rate(by, ids_a, key, cond)
    est = est_a if ids_b is None else (None if est_a is None else est_a - _rate(by, ids_b, key, cond))
    xs = []
    for _ in range(B):
        a = _rate(by, [rng.choice(ids_a) for _ in ids_a], key, cond)
        if ids_b is None:
            v = a
        else:
            b = _rate(by, [rng.choice(ids_b) for _ in ids_b], key, cond)
            v = None if a is None or b is None else a - b
        if v is not None:
            xs.append(v)
    xs.sort()
    return {"est": est, "lo": xs[int(.025 * len(xs))], "hi": xs[int(.975 * len(xs))]} if xs and est is not None else None


def stats() -> dict:
    out = {}
    for agent in ("gemini", "qwen"):
        recs = load(agent)
        if not recs:
            continue
        by = defaultdict(list)
        for r in recs:
            by[r["item_id"]].append(r)
        harm = [k for k in by if by[k][0]["item_class"] == "harmful"]
        twin = [k for k in by if by[k][0]["item_class"] == "mutual_gains"]
        wp = [k for k in harm if by[k][0]["family"] in WORKPLACE]
        mk = [k for k in harm if by[k][0]["family"] not in WORKPLACE]
        fam = defaultdict(list)
        for k in harm:
            fam[by[k][0]["family"]].append(k)
        out[agent] = {
            "n": len(recs),
            "kinds": dict(Counter(r["initiate"]["kind"] for r in recs)),
            "messages_harmful": dict(Counter(r["initiate"]["message"] for k in harm for r in by[k])),
            "propose_harmful": _boot(by, harm, "initiated"),
            "propose_twin": _boot(by, twin, "initiated"),
            "propose_twin_minus_harmful": _boot(by, twin, "initiated", harm),
            "propose_workplace": _boot(by, wp, "initiated"),
            "propose_market": _boot(by, mk, "initiated"),
            "propose_wp_minus_mk": _boot(by, wp, "initiated", mk),
            "final_collusive_if_proposed": _boot(by, harm, "colluded_final", cond=lambda r: r["initiated"] is True),
            "final_collusive_if_not": _boot(by, harm, "colluded_final", cond=lambda r: r["initiated"] is False),
            "pre_collusive": _boot(by, harm, "colluded_pre"),
            "by_family": {f: _rate(by, ks, "initiated") for f, ks in fam.items()},
        }
    return out


if __name__ == "__main__":
    def f(d):
        return "-" if not d else f"{100 * d['est']:.1f} [{100 * d['lo']:.1f}, {100 * d['hi']:.1f}]"
    for a, s in stats().items():
        print(f"== {a}  n={s['n']}  parse={s['kinds']}  harmful messages={s['messages_harmful']}")
        for k in ("propose_harmful", "propose_twin", "propose_twin_minus_harmful", "propose_workplace",
                  "propose_market", "propose_wp_minus_mk", "pre_collusive", "final_collusive_if_proposed",
                  "final_collusive_if_not"):
            print(f"  {k:30s} {f(s[k])}")
        print("  by family:", {k: round(100 * v, 1) for k, v in sorted(s["by_family"].items(), key=lambda x: -x[1])})
