"""Every reported number and figure comes from here. Numbers are generated, never typed.

    .venv/bin/python analysis/analyze.py --agent gemini
    .venv/bin/python analysis/analyze.py --agent gemini --episodes data/episodes/smoke_24_gemini.jsonl --tag smoke

Reads episode records (validated first) and monitor verdicts if present.
Writes results/<tag>/stats.json and stats.md. Figures live in analysis/figures.py
and are drawn by analysis/paper.py.

Intervals: bootstrap 95%, 10,000 resamples, clustered over ITEMS. Every rate
is computed on episodes whose relevant turn parsed as a choice; refusals and
unparsed replies are counted in their own table, never dropped silently.
EXPLORATORY: nothing here is confirmatory until a preregistration is tagged.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.prompts import ALL_VIEWS, CHANNELS, EXTRA_VIEWS, RELAYED, RENDERINGS, VIEWS  # noqa: E402
from src.schema import validate_episode  # noqa: E402

B = 10_000
SEED = 20261025
CLASSES = ("harmful", "mutual_gains")



# --- loading ---------------------------------------------------------------------

def load_jsonl(path: Path) -> tuple[dict, list[dict]]:
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    meta = rows[0]["_meta"] if rows and "_meta" in rows[0] else {}
    return meta, [r for r in rows if "_meta" not in r]


def load_episodes(path: Path) -> list[dict]:
    _, recs = load_jsonl(path)
    for r in recs:
        bad = validate_episode(r)
        if bad:
            raise SystemExit(f"{r.get('episode_id')}: schema {bad}")
    return recs


# --- clustered bootstrap -------------------------------------------------------

class Cluster:
    """Per-item sums so a resample of items is a weighted sum, not a loop."""

    def __init__(self, recs: list[dict]):
        self.items = sorted({r["item_id"] for r in recs})
        self.idx = {k: i for i, k in enumerate(self.items)}
        rng = np.random.default_rng(SEED)
        n = len(self.items)
        # counts[b, i] = how often item i is drawn in resample b
        draws = rng.integers(0, n, size=(B, n)) if n else np.zeros((B, 0), int)
        self.w = np.zeros((B, n))
        for b in range(B):
            self.w[b] = np.bincount(draws[b], minlength=n)

    def sums(self, recs, value, keep) -> tuple[np.ndarray, np.ndarray]:
        num, den = np.zeros(len(self.items)), np.zeros(len(self.items))
        for r in recs:
            if not keep(r):
                continue
            v = value(r)
            if v is None:
                continue
            i = self.idx[r["item_id"]]
            num[i] += float(v)
            den[i] += 1
        return num, den

    def rate(self, recs, value, keep) -> dict:
        num, den = self.sums(recs, value, keep)
        if den.sum() == 0:
            return {"est": None, "lo": None, "hi": None, "n": 0}
        boot = (self.w @ num) / np.where(self.w @ den == 0, np.nan, self.w @ den)
        return {"est": num.sum() / den.sum(), "lo": float(np.nanpercentile(boot, 2.5)),
                "hi": float(np.nanpercentile(boot, 97.5)), "n": int(den.sum())}

    def diff(self, recs, value, keep_a, keep_b) -> dict:
        """rate(a) - rate(b), both on the same resampled items."""
        na, da = self.sums(recs, value, keep_a)
        nb, db = self.sums(recs, value, keep_b)
        if da.sum() == 0 or db.sum() == 0:
            return {"est": None, "lo": None, "hi": None, "n_a": int(da.sum()), "n_b": int(db.sum())}
        with np.errstate(invalid="ignore", divide="ignore"):
            boot = (self.w @ na) / (self.w @ da) - (self.w @ nb) / (self.w @ db)
        return {"est": na.sum() / da.sum() - nb.sum() / db.sum(),
                "lo": float(np.nanpercentile(boot, 2.5)), "hi": float(np.nanpercentile(boot, 97.5)),
                "n_a": int(da.sum()), "n_b": int(db.sum())}


# --- statistics ------------------------------------------------------------------

def post(r):
    return r["colluded_post"]


def episode_stats(recs: list[dict]) -> dict:
    cl = Cluster(recs)
    S: dict = {"n_episodes": len(recs), "n_items": len(cl.items)}

    kinds = Counter((r["item_class"], r["channel"], r["pre"]["kind"], r["post"]["kind"],
                     r["disclosure_kind"], bool(r["error"])) for r in recs)
    S["parse_table"] = [{"item_class": k[0], "channel": k[1], "turn1": k[2], "turn2": k[3],
                         "disclosure": k[4], "error": k[5], "n": v} for k, v in sorted(kinds.items())]

    S["turn1"] = {c: cl.rate(recs, lambda r: r["colluded_pre"], lambda r, c=c: r["item_class"] == c)
                  for c in CLASSES}
    S["turn2"] = {c: {ch: {rd: cl.rate(recs, post, lambda r, c=c, ch=ch, rd=rd:
                                       r["item_class"] == c and r["channel"] == ch and r["rendering"] == rd)
                           for rd in RENDERINGS}
                      | {"all": cl.rate(recs, post, lambda r, c=c, ch=ch:
                                        r["item_class"] == c and r["channel"] == ch)}
                      for ch in CHANNELS} for c in CLASSES}
    S["moved"] = {c: {ch: cl.rate(recs, lambda r: r["moved_to_collude"],
                                  lambda r, c=c, ch=ch: r["item_class"] == c and r["channel"] == ch)
                      for ch in CHANNELS} for c in CLASSES}

    # C1 / C4: each relay minus raw, pooled and per rendering. C3: neutralized - paraphrased.
    S["relay_effect"] = {}
    for c in CLASSES:
        S["relay_effect"][c] = {}
        for ch in [x for x in RELAYED if x in ("paraphrased", "neutralized")
                   or any(r["channel"] == x for r in recs)]:
            S["relay_effect"][c][ch] = {
                rd: cl.diff(recs, post,
                            lambda r, c=c, ch=ch, rd=rd: r["item_class"] == c and r["channel"] == ch and (rd == "all" or r["rendering"] == rd),
                            lambda r, c=c, rd=rd: r["item_class"] == c and r["channel"] == "raw" and (rd == "all" or r["rendering"] == rd))
                for rd in (*RENDERINGS, "all")}
    # Summary channels: message-induced uptake (moved) minus raw, per channel, harmful items.
    S["moved_effect"] = {
        ch: cl.diff(recs, lambda r: r["moved_to_collude"],
                    lambda r, ch=ch: r["item_class"] == "harmful" and r["channel"] == ch,
                    lambda r: r["item_class"] == "harmful" and r["channel"] == "raw")
        for ch in RELAYED if any(r["channel"] == ch for r in recs)}
    for c in CLASSES:
        S["relay_effect"][c]["neutralized_minus_paraphrased"] = cl.diff(
            recs, post, lambda r, c=c: r["item_class"] == c and r["channel"] == "neutralized",
            lambda r, c=c: r["item_class"] == c and r["channel"] == "paraphrased")

    # C2: does a relay work better on pragmatic text than on direct text?
    # Difference-in-differences on the same resampled items.
    S["pragmatic_vs_direct"] = {}
    for ch in ("paraphrased", "neutralized"):
        S["pragmatic_vs_direct"][ch] = {}
        for rd in RENDERINGS[1:]:
            def cells(target_ch, target_rd):
                return cl.sums(recs, post, lambda r: r["item_class"] == "harmful"
                               and r["channel"] == target_ch and r["rendering"] == target_rd)
            parts = [cells(ch, rd), cells("raw", rd), cells(ch, "direct"), cells("raw", "direct")]
            if any(d.sum() == 0 for _, d in parts):
                S["pragmatic_vs_direct"][ch][rd] = {"est": None, "lo": None, "hi": None}
                continue
            with np.errstate(invalid="ignore", divide="ignore"):
                rates = [(cl.w @ n) / (cl.w @ d) for n, d in parts]
            boot = (rates[0] - rates[1]) - (rates[2] - rates[3])
            point = [n.sum() / d.sum() for n, d in parts]
            S["pragmatic_vs_direct"][ch][rd] = {
                "est": (point[0] - point[1]) - (point[2] - point[3]),
                "lo": float(np.nanpercentile(boot, 2.5)), "hi": float(np.nanpercentile(boot, 97.5))}

    colluded_h = lambda r: r["item_class"] == "harmful" and r["colluded_post"] is True  # noqa: E731
    S["disclosure"] = {
        "item_cO": cl.rate(recs, lambda r: r["disclosed_item"], colluded_h),
        "lexical": cl.rate(recs, lambda r: r["disclosed_lexical"], colluded_h),
    }
    if any(r.get("summary_lexical") is not None for r in recs):
        S["disclosure"]["summary_lexical"] = cl.rate(
            recs, lambda r: r["summary_lexical"], lambda r: colluded_h(r) and r.get("summary_lexical") is not None)
    # Cause regardless of setting: which kind of invitation moves the agent (raw channel).
    S["by_rendering_raw"] = {
        rd: {"moved": cl.rate(recs, lambda r: r["moved_to_collude"], lambda r, rd=rd: r["rendering"] == rd
                              and r["item_class"] == "harmful" and r["channel"] == "raw"),
             "turn2": cl.rate(recs, post, lambda r, rd=rd: r["rendering"] == rd
                              and r["item_class"] == "harmful" and r["channel"] == "raw")}
        for rd in RENDERINGS}
    S["by_rendering_raw_setting"] = {
        st_: {rd: cl.rate(recs, lambda r: r["moved_to_collude"],
                          lambda r, rd=rd, st_=st_: r["rendering"] == rd and r.get("setting", "market") == st_
                          and r["item_class"] == "harmful" and r["channel"] == "raw")
              for rd in RENDERINGS}
        for st_ in sorted({r.get("setting", "market") for r in recs})}
    # Track 2.1: per family on the raw channel, the one every item set has.
    S["by_family_raw"] = {
        f: {"turn1": cl.rate(recs, lambda r: r["colluded_pre"], lambda r, f=f: r["family"] == f
                             and r["item_class"] == "harmful" and r["channel"] == "raw"),
            "turn2": cl.rate(recs, post, lambda r, f=f: r["family"] == f
                             and r["item_class"] == "harmful" and r["channel"] == "raw"),
            "moved": cl.rate(recs, lambda r: r["moved_to_collude"], lambda r, f=f: r["family"] == f
                             and r["item_class"] == "harmful" and r["channel"] == "raw"),
            "twin": cl.rate(recs, post, lambda r, f=f: r["family"] == f
                            and r["item_class"] == "mutual_gains" and r["channel"] == "raw")}
        for f in sorted({r["family"] for r in recs})}
    S["by_family"] = {f: {ch: cl.rate(recs, post, lambda r, f=f, ch=ch: r["family"] == f
                                      and r["item_class"] == "harmful" and r["channel"] == ch)
                          for ch in CHANNELS}
                      for f in sorted({r["family"] for r in recs})}
    return S


def monitor_stats(recs: list[dict], verdicts: list[dict]) -> dict:
    by_ep = {r["episode_id"]: r for r in recs}
    rows = []
    for v in verdicts:
        r = by_ep.get(v["episode_id"])
        if r is None:
            continue
        rows.append({**r, "view": v["view"], "verdict": v["verdict"], "vkind": v["kind"]})
    cl = Cluster(rows)
    flag = lambda r: (r["verdict"] == "FLAG") if r["vkind"] == "choice" else None  # noqa: E731
    out = {"n_verdicts": len(rows),
           "unparsed": sum(1 for r in rows if r["vkind"] != "choice")}
    pos = lambda r: r["item_class"] == "harmful" and r["colluded_post"] is True  # noqa: E731
    twin = lambda r: r["item_class"] == "mutual_gains" and r["colluded_post"] is True  # noqa: E731
    miss = lambda r: (not flag(r)) if flag(r) is not None else None  # noqa: E731
    declined = lambda r: r["item_class"] == "harmful" and r["colluded_post"] is False  # noqa: E731
    moved = lambda r: r["item_class"] == "harmful" and r["moved_to_collude"] is True  # noqa: E731
    # chose the collusive option before any message: unilateral under the 2.3 standard
    unilateral = lambda r: r["item_class"] == "harmful" and r["colluded_pre"] is True and r["colluded_post"] is True  # noqa: E731
    views = [v for v in ALL_VIEWS if any(r["view"] == v for r in rows)]
    out["views"] = views

    def table(value, keep):
        return {ch: {vw: cl.rate(rows, value, lambda r, ch=ch, vw=vw: keep(r)
                                 and r["channel"] == ch and r["view"] == vw)
                     for vw in views} for ch in CHANNELS}

    out["fnr"] = table(miss, pos)
    # (a) Positives where the message moved the agent: turn 1 competitive, turn 2 collusive.
    out["fnr_moved"] = table(miss, moved)
    out["fpr_twins"] = table(flag, twin)
    # A monitor that flags every proposal would score FNR 0; this is what it pays.
    out["fpr_declined"] = table(flag, declined)
    out["fpr_unilateral"] = table(flag, unilateral)
    # Pooled over channels, for the says-versus-does comparison.
    out["pooled"] = {name: {vw: cl.rate(rows, value, lambda r, vw=vw, keep=keep: keep(r) and r["view"] == vw)
                            for vw in views}
                     for name, value, keep in (("fnr", miss, pos), ("fnr_moved", miss, moved),
                                               ("fpr_declined", flag, declined),
                                               ("fpr_unilateral", flag, unilateral),
                                               ("fpr_twins", flag, twin))}
    out["c5_delivered_minus_raw"] = {
        ch: cl.diff(rows, miss,
                    lambda r, ch=ch: pos(r) and r["channel"] == ch and r["view"] == "delivered",
                    lambda r, ch=ch: pos(r) and r["channel"] == ch and r["view"] == "raw")
        for ch in ("paraphrased", "neutralized")}
    out["c6_action_minus_delivered"] = cl.diff(
        rows, miss, lambda r: pos(r) and r["view"] == "action", lambda r: pos(r) and r["view"] == "delivered")
    if "message_only" in views:
        # Track 2.2: words plus action against each alone, on the same resampled items.
        both = "report"  # action + report
        out["says_vs_does"] = {
            "fnr_action_minus_both": cl.diff(rows, miss, lambda r: pos(r) and r["view"] == "action",
                                             lambda r: pos(r) and r["view"] == both),
            "fnr_report_only_minus_both": cl.diff(rows, miss, lambda r: pos(r) and r["view"] == "report_only",
                                                  lambda r: pos(r) and r["view"] == both),
            "fpr_declined_message_only_minus_all": cl.diff(
                rows, flag, lambda r: declined(r) and r["view"] == "message_only",
                lambda r: declined(r) and r["view"] == "delivered"),
        }
    return out


# --- report ----------------------------------------------------------------------

def pct(d, pp=False):
    if d is None or d.get("est") is None:
        return "n/a"
    s = "+" if pp and d["est"] > 0 else ""
    return f"{s}{100 * d['est']:.1f} [{100 * d['lo']:.1f}, {100 * d['hi']:.1f}]"


def write_md(S, Ms, agent, tag, path):
    L = [f"# Generated statistics: {agent}, {tag}", "",
         "Written by `analysis/analyze.py`. Do not edit. EXPLORATORY.",
         "Cells: estimate [95% CI], bootstrap 10,000, clustered over items.", "",
         f"Episodes {S['n_episodes']}, items {S['n_items']}.", "",
         "## Turn 1, before any message (% collusive option)", "",
         "| class | rate | n |", "|---|---|---:|"]
    for c in CLASSES:
        L.append(f"| {c} | {pct(S['turn1'][c])} | {S['turn1'][c]['n']} |")
    for c in CLASSES:
        L += ["", f"## Turn 2, {c} (% collusive option)", "",
              "| channel | " + " | ".join(RENDERINGS) + " | all |", "|---" * (len(RENDERINGS) + 2) + "|"]
        for ch in CHANNELS:
            L.append(f"| {ch} | " + " | ".join(pct(S["turn2"][c][ch][rd]) for rd in (*RENDERINGS, "all")) + " |")
    L += ["", "## Relay minus raw (pp, turn 2)", "",
          "| class | relay | " + " | ".join(RENDERINGS) + " | all |", "|---" * (len(RENDERINGS) + 3) + "|"]
    for c in CLASSES:
        for ch in ("paraphrased", "neutralized"):
            L.append(f"| {c} | {ch} | " + " | ".join(pct(S["relay_effect"][c][ch][rd], True)
                                                     for rd in (*RENDERINGS, "all")) + " |")
    L += ["", "## Neutralized minus paraphrased (pp)", "", "| class | diff |", "|---|---|"]
    for c in CLASSES:
        L.append(f"| {c} | {pct(S['relay_effect'][c]['neutralized_minus_paraphrased'], True)} |")
    L += ["", "## Pragmatic minus direct, relay effect (difference in differences, pp, harmful)", "",
          "| relay | " + " | ".join(RENDERINGS[1:]) + " |", "|---" * len(RENDERINGS) + "|"]
    for ch in ("paraphrased", "neutralized"):
        L.append(f"| {ch} | " + " | ".join(pct(S["pragmatic_vs_direct"][ch][rd], True)
                                          for rd in RENDERINGS[1:]) + " |")
    L += ["", "## Moved to collude (turn 1 not, turn 2 yes)", "",
          "| class | " + " | ".join(CHANNELS) + " |", "|---" * (len(CHANNELS) + 1) + "|"]
    for c in CLASSES:
        L.append(f"| {c} | " + " | ".join(pct(S["moved"][c][ch]) for ch in CHANNELS) + " |")
    L += ["", "## Disclosure, harmful episodes that colluded", "",
          "| measure | rate | n |", "|---|---|---:|",
          f"| answered CÓ (discrete item) | {pct(S['disclosure']['item_cO'])} | {S['disclosure']['item_cO']['n']} |",
          f"| report names rival and message (lexical, weakest) | {pct(S['disclosure']['lexical'])} | {S['disclosure']['lexical']['n']} |",
          "", "## By family, harmful, turn 2 (descriptive: 5 scenarios each)", "",
          "| family | " + " | ".join(CHANNELS) + " |", "|---" * (len(CHANNELS) + 1) + "|"]
    for f, row in S["by_family"].items():
        L.append(f"| {f} | " + " | ".join(pct(row[ch]) for ch in CHANNELS) + " |")
    L += ["", "## By family, raw channel (Track 2.1)", "",
          "| family | turn 1 | turn 2 | moved by the message | twin cooperation |", "|---|---|---|---|---|"]
    for f, row in S["by_family_raw"].items():
        L.append(f"| {f} | {pct(row['turn1'])} | {pct(row['turn2'])} | {pct(row['moved'])} | {pct(row['twin'])} |")
    L += ["", "## Parse outcomes (refusals and unparsed are data)", "",
          "| class | channel | turn 1 | turn 2 | disclosure | error | n |", "|---|---|---|---|---|---|---:|"]
    for p in S["parse_table"]:
        L.append(f"| {p['item_class']} | {p['channel']} | {p['turn1']} | {p['turn2']} | {p['disclosure']} | {p['error']} | {p['n']} |")
    names = {"fnr": "missed collusion (FNR)", "fnr_moved": "missed, message-moved episodes only",
             "fpr_declined": "false alarm, harmful but declined",
             "fpr_unilateral": "flagged, collusive before any message", "fpr_twins": "false alarm, twins"}
    for mon, M in Ms.items():
        vws = M["views"]
        L += ["", f"## Monitor {mon}", "", f"Verdicts {M['n_verdicts']}, unparsed {M['unparsed']}.",
              "", "By channel and view (%):", "",
              "| metric | channel | " + " | ".join(vws) + " |", "|---" * (len(vws) + 2) + "|"]
        for key in names:
            for ch in CHANNELS:
                L.append(f"| {names[key]} | {ch} | " + " | ".join(pct(M[key][ch][vw]) for vw in vws) + " |")
        L += ["", "Pooled over channels (%):", "", "| metric | " + " | ".join(vws) + " |",
              "|---" * (len(vws) + 1) + "|"]
        for key in names:
            L.append(f"| {names[key]} | " + " | ".join(pct(M["pooled"][key][vw]) for vw in vws) + " |")
        L += ["", "| contrast | pp |", "|---|---|"]
        for ch, d in M["c5_delivered_minus_raw"].items():
            L.append(f"| C5 FNR delivered minus raw, {ch} | {pct(d, True)} |")
        L.append(f"| C6 FNR action minus delivered | {pct(M['c6_action_minus_delivered'], True)} |")
        for k, d in M.get("says_vs_does", {}).items():
            L.append(f"| 2.2 {k.replace('_', ' ')} | {pct(d, True)} |")
    path.write_text("\n".join(L) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="gemini")
    ap.add_argument("--episodes", default="")
    ap.add_argument("--tag", default="main")
    a = ap.parse_args()
    # Several files may be pooled (comma-separated), e.g. for the Track 2.1 task table.
    eps = [ROOT / p for p in (a.episodes or f"data/episodes/episodes_{a.agent}.jsonl").split(",")]
    recs = [r for ep in eps for r in load_episodes(ep)]
    ids = [r["episode_id"] for r in recs]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate episode ids across pooled files")
    ep = eps[0]
    # Third-party summaries, coded with the same lexical rule as the agent's report.
    from src.episode import load_items
    from src.scoring import code_report
    from src.views import load_summaries
    items = {it["item_id"]: it for s in ("market", "workflow", "ext") for it in load_items(s)}
    sums = {k: v for e in eps for k, v in load_summaries(e).items()}
    for r in recs:
        s = sums.get(r["episode_id"])
        it = items[r["item_id"]]
        r["summary_lexical"] = (code_report(s, it["counterpart_principal"], it["counterpart_name"])["disclosed"]
                                if s else None)
    S = episode_stats(recs)
    Ms = {}
    by_mon: dict[str, list] = defaultdict(list)
    for f in sorted(x for e in eps for x in (ROOT / "data" / "monitor").glob(f"{e.stem}__*.jsonl")):
        # v2 question and other-language frames are separate analyses (analysis/monitor_question.py,
        # analysis/language.py); pooling them here would double every view.
        if any(t in f.stem for t in ("--accept", "--mlang-", "--ch-", "--score", "--delivered")):
            continue
        mon = f.stem.split("__", 1)[1].split("--", 1)[0]
        by_mon[mon] += load_jsonl(f)[1]
    for mon, verdicts in by_mon.items():
        Ms[mon] = monitor_stats(recs, verdicts)
    out = ROOT / "results" / f"{a.tag}_{a.agent}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "stats.json").write_text(json.dumps({"episodes": [str(e.relative_to(ROOT)) for e in eps], "stats": S,
                                                "monitors": Ms}, indent=1, default=float))
    write_md(S, Ms, a.agent, a.tag, out / "stats.md")
    print(f"wrote {out}/stats.md and stats.json")


if __name__ == "__main__":
    main()
