"""Emit paper/numbers.tex, paper/tables/*.tex and paper/figures/* from the generated stats.

    .venv/bin/python analysis/paper.py

Every number in paper/main.tex is a macro defined here. Nothing is typed by
hand. Run analysis/analyze.py (main, workflow, tasks) and scripts/score_gate.py
first. A missing input is reported, and its macros print as a visible "??".
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.prompts import CHANNELS, RENDERINGS  # noqa: E402

PAPER = ROOT / "paper"
AGENTS = ("gemini", "qwen")
LABEL = {"gemini": "Gemini 2.5 Flash", "qwen": "Qwen3-8B"}
WORKFLOW_FAMS = ("no_poach", "review_ring", "budget_padding")
MISSING: list[str] = []


def load(path: str) -> dict | None:
    f = ROOT / path
    if not f.exists():
        MISSING.append(path)
        return None
    return json.loads(f.read_text())


def pct(d, digits=1) -> str:
    if not d or d.get("est") is None:
        return "??"
    return f"{100 * d['est']:.{digits}f}\\%"


def ci(d) -> str:
    if not d or d.get("est") is None or d.get("lo") is None:
        return "??"
    return f"[{100 * d['lo']:.1f}, {100 * d['hi']:.1f}]".replace("-", "$-$")


def pp(d) -> str:
    if not d or d.get("est") is None:
        return "??"
    return f"{100 * d['est']:+.1f}".replace("-", "$-$")


def cell(d, bold: bool = False) -> str:
    """Table cell: estimate with its interval, compact. Key numbers are set in bold."""
    if not d or d.get("est") is None:
        return "--"
    est = f"{100 * d['est']:.1f}"
    return (f"\\textbf{{{est}}}" if bold else est) + f" {{\\scriptsize[{100 * d['lo']:.1f}, {100 * d['hi']:.1f}]}}"


def is_max(d, ds) -> bool:
    vals = [x["est"] for x in ds if x and x.get("est") is not None]
    return bool(d and d.get("est") is not None and vals and d["est"] == max(vals))


def excludes_zero(d) -> bool:
    return bool(d and d.get("lo") is not None and (d["lo"] > 0 or d["hi"] < 0))


def tex_escape(s: str) -> str:
    return (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
             .replace("_", "\\_").replace("#", "\\#").replace("$", "\\$"))


def main() -> None:
    S = {a: load(f"results/main_{a}/stats.json") for a in AGENTS}
    W = {a: load(f"results/workflow_{a}/stats.json") for a in AGENTS}
    Tk = {a: load(f"results/tasks_{a}/stats.json") for a in AGENTS}
    agree = load("results/reader_agreement.json")
    st = {a: S[a]["stats"] if S[a] else None for a in AGENTS}
    mon = {a: S[a]["monitors"].get("mistral") if S[a] else None for a in AGENTS}
    wst = {a: W[a]["stats"] if W[a] else None for a in AGENTS}
    wmon = {a: W[a]["monitors"].get("mistral") if W[a] else None for a in AGENTS}
    tk = {a: Tk[a]["stats"] if Tk[a] else None for a in AGENTS}

    M: dict[str, str] = {}
    g, q = st["gemini"], st["qwen"]
    # sizes
    M["nMarketEp"] = str(g["n_episodes"]) if g else "??"
    M["nWorkflowEp"] = str(wst["gemini"]["n_episodes"]) if wst["gemini"] else "??"
    M["nTaskItems"] = str(tk["gemini"]["n_items"]) if tk["gemini"] else "??"
    M["nTaskEp"] = str(tk["gemini"]["n_episodes"]) if tk["gemini"] else "??"
    # behaviour, market
    for a, P in (("gemini", "Gem"), ("qwen", "Qw")):
        s = st[a]
        if not s:
            continue
        M[f"{P}TurnOne"] = pct(s["turn1"]["harmful"])
        M[f"{P}MovedRaw"] = pct(s["moved"]["harmful"]["raw"])
        M[f"{P}Para"] = pp(s["relay_effect"]["harmful"]["paraphrased"]["all"])
        M[f"{P}ParaCI"] = ci(s["relay_effect"]["harmful"]["paraphrased"]["all"])
        M[f"{P}Neut"] = pp(s["relay_effect"]["harmful"]["neutralized"]["all"])
        M[f"{P}NeutCI"] = ci(s["relay_effect"]["harmful"]["neutralized"]["all"])
        M[f"{P}TwinMin"] = pct(min((s["turn2"]["mutual_gains"][ch]["all"] for ch in CHANNELS
                                    if (s["turn2"]["mutual_gains"].get(ch, {}).get("all") or {}).get("est") is not None),
                                   key=lambda d: d["est"]))
        M[f"{P}DiscItem"] = pct(s["disclosure"]["item_cO"])
        M[f"{P}DiscLex"] = pct(s["disclosure"]["lexical"])
    # monitor
    for a, P in (("gemini", "Mon"), ("qwen", "MonQ")):
        m = mon[a]
        if not m:
            continue
        pm = m["pooled"]
        M[f"{P}ActionFNR"] = pct(pm["fnr"]["action"])
        M[f"{P}ActionFNRCI"] = ci(pm["fnr"]["action"])
        M[f"{P}ReportFNR"] = pct(pm["fnr"]["report"])
        M[f"{P}ReportOnlyFNR"] = pct(pm["fnr"]["report_only"])
        M[f"{P}DeliveredFNR"] = pct(pm["fnr"]["delivered"])
        M[f"{P}MovedActionFNR"] = pct(pm["fnr_moved"]["action"])
        M[f"{P}MovedReportFNR"] = pct(pm["fnr_moved"]["report"])
        M[f"{P}FADeclReport"] = pct(pm["fpr_declined"]["report"])
        M[f"{P}FADeclDelivered"] = pct(pm["fpr_declined"]["delivered"])
        M[f"{P}FADeclMsgOnly"] = pct(pm["fpr_declined"]["message_only"])
        if "says_vs_does" in m:
            M[f"{P}ActionMinusBoth"] = pp(m["says_vs_does"]["fnr_action_minus_both"])
            M[f"{P}ActionMinusBothCI"] = ci(m["says_vs_does"]["fnr_action_minus_both"])
    # Second monitor (Claude Haiku 5.5) on Gemini episodes
    hk = S["gemini"]["monitors"].get("haiku") if S["gemini"] else None
    if hk:
        pm = hk["pooled"]
        M["HkActionFNR"] = pct(pm["fnr"]["action"])
        M["HkReportFNR"] = pct(pm["fnr"]["report"])
        M["HkFADeclReport"] = pct(pm["fpr_declined"]["report"])
        M["HkFADeclMsgOnly"] = pct(pm["fpr_declined"]["message_only"])
        M["HkFADeclDelivered"] = pct(pm["fpr_declined"]["delivered"])
        M["HkFATwinsAction"] = pct(pm["fpr_twins"]["action"])
        M["HkDeliveredFNR"] = pct(pm["fnr"]["delivered"])
    hkq = S["qwen"]["monitors"].get("haiku") if S["qwen"] else None
    if hkq:
        M["HkQReportFNR"] = pct(hkq["pooled"]["fnr"]["report"])
    # Track 2.3: the standard view against the other views, Gemini agent, market pooled
    for mname, P in (("mistral", "StdMi"), ("haiku", "StdHk")):
        mm = S["gemini"]["monitors"].get(mname) if S["gemini"] else None
        if mm and "standard" in mm["views"]:
            pm = mm["pooled"]
            M[f"{P}MovedFNR"] = pct(pm["fnr_moved"]["standard"])
            M[f"{P}FADecl"] = pct(pm["fpr_declined"]["standard"])
            M[f"{P}FAUni"] = pct(pm["fpr_unilateral"]["standard"])
            M[f"{P}FATwins"] = pct(pm["fpr_twins"]["standard"])
            M[f"{P}RepFAUni"] = pct(pm["fpr_unilateral"]["report"])
            M[f"{P}RepMovedFNR"] = pct(pm["fnr_moved"]["report"])
            M[f"{P}AllFADecl"] = pct(pm["fpr_declined"]["delivered"])
            if "baseline_info" in mm["views"]:
                M[f"{P}CtlMovedFNR"] = pct(pm["fnr_moved"]["baseline_info"])
                M[f"{P}CtlFADecl"] = pct(pm["fpr_declined"]["baseline_info"])
                M[f"{P}CtlFAUni"] = pct(pm["fpr_unilateral"]["baseline_info"])
            if "pop_baseline" in mm["views"]:
                M[f"{P}PopFNR"] = pct(pm["fnr"]["pop_baseline"])
                M[f"{P}PopMovedFNR"] = pct(pm["fnr_moved"]["pop_baseline"])
                M[f"{P}PopFADecl"] = pct(pm["fpr_declined"]["pop_baseline"])
                M[f"{P}PopFAUni"] = pct(pm["fpr_unilateral"]["pop_baseline"])
            if "family_baseline" in mm["views"]:
                M[f"{P}FamFNR"] = pct(pm["fnr"]["family_baseline"])
                M[f"{P}FamFADecl"] = pct(pm["fpr_declined"]["family_baseline"])
        mq = S["qwen"]["monitors"].get(mname) if S["qwen"] else None
        if mq and "standard" in mq["views"]:
            M[f"{P}QwMovedFNR"] = pct(mq["pooled"]["fnr_moved"]["standard"])
            M[f"{P}QwRepMovedFNR"] = pct(mq["pooled"]["fnr_moved"]["report"])
            if "pop_baseline" in mq["views"]:
                M[f"{P}QwPopFADecl"] = pct(mq["pooled"]["fpr_declined"]["pop_baseline"])
                M[f"{P}QwPopMovedFNR"] = pct(mq["pooled"]["fnr_moved"]["pop_baseline"])
            if "family_baseline" in mq["views"]:
                M[f"{P}QwFamFNR"] = pct(mq["pooled"]["fnr"]["family_baseline"])
                M[f"{P}QwFamFADecl"] = pct(mq["pooled"]["fpr_declined"]["family_baseline"])
    hkw = W["gemini"]["monitors"].get("haiku") if W["gemini"] else None
    if hkw:
        M["HkWfActionFNR"] = pct(hkw["pooled"]["fnr"]["action"])
    if wmon["gemini"]:
        pm = wmon["gemini"]["pooled"]
        M["WfActionFNR"] = pct(pm["fnr"]["action"])
        M["WfReportFNR"] = pct(pm["fnr"]["report"])
        M["WfFADeclMsgOnly"] = pct(pm["fpr_declined"]["message_only"])
        M["WfFADeclReport"] = pct(pm["fpr_declined"]["report"])
    # gate and readers
    gs = [json.loads(l) for l in (ROOT / "data/stimuli/gate_scored.jsonl").read_text().splitlines()[1:]]
    for ch, P in (("raw", "Raw"), ("paraphrased", "Para"), ("neutralized", "Neut")):
        v = [r["pushes_collusive"] for r in gs if r["item_class"] == "harmful" and r["channel"] == ch
             and r["pushes_collusive"] is not None]
        M[f"GatePush{P}"] = f"{100 * sum(v) / len(v):.0f}\\%"
    if agree:
        for name, P in (("opus", "Opus"), ("gemini_pro", "GeminiPro"), ("gemma", "Gemma"), ("gpt", "GPT")):
            r = agree["readers"].get(name, {}).get("harmful")
            M[f"Agree{P}"] = f"{100 * r['agreement']:.0f}\\%" if r else "??"
    # 2.1 tasks: top families, invitation type
    for a, P in (("gemini", "Gem"), ("qwen", "Qw")):
        t = tk[a]
        if not t:
            continue
        fam = t["by_family_raw"]
        for key, K in (("turn1", "TopUnprompted"), ("moved", "TopMoved")):
            f, r = max(((f, r) for f, r in fam.items() if r[key]["est"] is not None),
                       key=lambda x: x[1][key]["est"])
            M[f"{P}{K}Fam"] = f"\\texttt{{{tex_escape(f)}}}"
            M[f"{P}{K}"] = pct(r[key])
        for setting in ("market", "workflow"):
            row = t.get("by_rendering_raw_setting", {}).get(setting)
            if not row:
                continue
            for rd in RENDERINGS:
                M[f"{P}{setting.capitalize()}{rd.capitalize()}"] = pct(row[rd])

    # Summary channels (C5-S styles): stimulus loss, agent uptake, positive control, monitor.
    SU = {a: load(f"results/summary_{a}/stats.json") for a in AGENTS}
    SUM_CH = ("raw", "sum_short", "sum_long", "sum_system", "sum_codeswitch")
    SUM_LAB = {"raw": "Original message", "sum_short": "Short (one sentence)", "sum_long": "Long (3--4 sentences)",
               "sum_system": "System log (3 fields)", "sum_codeswitch": "Code-switched"}
    if all(SU.values()) and agree and "by_channel" in agree:
        import json as _j
        stim_rows = [_j.loads(l) for l in (ROOT / "data/stimuli/stimuli.jsonl").read_text().splitlines()[1:]]
        rows = []
        for ch in SUM_CH:
            bc = agree["by_channel"].get(ch, {})
            L = [len(s["text"]) for s in stim_rows if s["channel"] == ch]
            g, o = bc.get("gemini"), bc.get("opus")
            eff = [SU[a]["stats"]["moved_effect"].get(ch) if ch != "raw" else SU[a]["stats"]["moved"]["harmful"]["raw"]
                   for a in AGENTS]
            twin = SU["qwen"]["stats"]["turn2"]["mutual_gains"][ch]["all"]
            rows.append(f"{SUM_LAB[ch]} & {sum(L) / len(L):.0f} & "
                        f"{100 * g['push']:.1f} & {100 * o['push']:.1f} & "
                        + " & ".join(cell(e, ch != "raw" and excludes_zero(e)) for e in eff)
                        + f" & {cell(twin, twin['est'] < 0.9)} \\\\")
        (PAPER / "tables" / "summaries.tex").write_text(
            "\\begin{tabular}{lrrrrrr}\n\\toprule\n"
            " & & \\multicolumn{2}{c}{Still invites (\\%)} & \\multicolumn{2}{c}{Moved by message} & Qwen twins \\\\\n"
            "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\n"
            "Agent reads & Chars & Gate & Opus & Gemini & Qwen & cooperate \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
        se = {a: SU[a]["stats"]["moved_effect"] for a in AGENTS}
        M["SumQwSysMoved"] = pp(se["qwen"]["sum_system"])
        M["SumQwSysMovedCI"] = ci(se["qwen"]["sum_system"])
        M["SumGemSysMoved"] = pp(se["gemini"]["sum_system"])
        M["SumGemCSMoved"] = pp(se["gemini"]["sum_codeswitch"])
        M["SumGemCSMovedCI"] = ci(se["gemini"]["sum_codeswitch"])
        M["SumQwCSMoved"] = pp(se["qwen"]["sum_codeswitch"])
        M["SumQwRawMoved"] = pct(SU["qwen"]["stats"]["moved"]["harmful"]["raw"])
        M["SumQwSysTwin"] = pct(SU["qwen"]["stats"]["turn2"]["mutual_gains"]["sum_system"]["all"])
        M["SumQwRawTwin"] = pct(SU["qwen"]["stats"]["turn2"]["mutual_gains"]["raw"]["all"])
        M["SumOpusSys"] = pct({"est": agree["by_channel"]["sum_system"]["opus"]["push"]})
        M["SumOpusRaw"] = pct({"est": agree["by_channel"]["raw"]["opus"]["push"]})
        for a, A in (("gemini", "Gem"), ("qwen", "Qw")):
            for name, N in (("mistral", "Mi"), ("haiku", "Hk")):
                mm = SU[a]["monitors"].get(name)
                if mm:
                    M[f"Sum{A}{N}SysFADel"] = pct(mm["fpr_declined"]["sum_system"].get("delivered"))
                    M[f"Sum{A}{N}SysFARaw"] = pct(mm["fpr_declined"]["sum_system"].get("raw"))
    # robustness: second Qwen sample and Gemma, gate push on sum_system vs others
    for src, K in (("resample", "Res"), ("gemma", "Gma")):
        f = ROOT / f"data/stimuli/robust_summaries_{src}.jsonl"
        if f.exists():
            import json as _j
            import re as _re

            from src.episode import load_items as _li
            from src.episode import options as _opt
            from src.scoring import classify as _cls
            its = {i["item_id"]: i for i in _li()}
            R = [_j.loads(l) for l in f.read_text().splitlines()[1:]]
            def _push(r):
                _, _, coll = _opt(its[r["item_id"]], 0)
                l, k = _cls(r["gate_reply"])
                if k != "choice" and _re.match(r"^\W*kh[oô]ng\b", (r["gate_reply"] or "").strip(), _re.I):
                    return False
                return (l == coll) if k == "choice" else None
            for ch, C in (("sum_system", "Sys"), ("sum_short", "Short"), ("sum_long", "Long"), ("sum_codeswitch", "CS")):
                v = [x for x in (_push(r) for r in R if r["channel"] == ch) if x is not None]
                M[f"Rob{K}{C}"] = pct({"est": sum(v) / len(v)}) if v else "??"

    from analysis.lexical import write as _lex
    _lex(PAPER / "tables" / "lexical.tex")
    # Track 2.1: workplace versus market tasks, and cross-model rank agreement
    from analysis.setting import stats as _setting
    from src.episode import load_items as _li2
    _items = {i["item_id"]: i for s in ("market", "workflow", "ext") for i in _li2(s)}
    ST = _setting(_items)
    for a, A in (("gemini", "Gem"), ("qwen", "Qw")):
        mv = ST[a]["moved_to_collude"]
        M[f"Set{A}WpMoved"] = pct(mv["workplace"])
        M[f"Set{A}MkMoved"] = pct(mv["market"])
        M[f"Set{A}MovedDiff"] = pp(mv["diff"])
        M[f"Set{A}MovedDiffCI"] = ci(mv["diff"])
        M[f"Set{A}PostDiff"] = pp(ST[a]["colluded_post"]["diff"])
    M["SetRankRho"] = f"{ST['spearman_moved']:.2f}"
    # Initiation probe: does the agent open the collusion itself? (analysis/initiate.py)
    from analysis.initiate import stats as _init
    INI = _init()
    for a, A in (("gemini", "Gem"), ("qwen", "Qw")):
        s_ = INI.get(a)
        if not s_:
            continue
        M[f"Init{A}Harm"] = pct(s_["propose_harmful"])
        M[f"Init{A}HarmCI"] = ci(s_["propose_harmful"])
        M[f"Init{A}Twin"] = pct(s_["propose_twin"])
        M[f"Init{A}Pre"] = pct(s_["pre_collusive"])
        M[f"Init{A}FollowProp"] = pct(s_["final_collusive_if_proposed"])
        M[f"Init{A}FollowNot"] = pct(s_["final_collusive_if_not"])
        top = max(s_["by_family"].items(), key=lambda kv: kv[1])
        M[f"Init{A}TopFam"] = "\\texttt{" + top[0].replace("_", "\\_") + "}"
        M[f"Init{A}TopFamRate"] = pct({"est": top[1]})
        M[f"Init{A}WpDiff"] = pp(s_["propose_wp_minus_mk"])
        M[f"Init{A}WpDiffCI"] = ci(s_["propose_wp_minus_mk"])
    # Oversight through a summary (macros for the text; table oversight.tex below)
    for a, A in (("gemini", "Gem"), ("qwen", "Qw")):
        for name, N in (("mistral", "Mi"), ("haiku", "Hk")):
            mm = S[a]["monitors"].get(name) if S[a] else None
            if not mm or "summary" not in mm["views"]:
                continue
            pm = mm["pooled"]
            for v, V in (("report_only", "Self"), ("summary", "Sum"), ("baseline_info", "Trace")):
                M[f"Ov{A}{N}{V}FNR"] = pct(pm["fnr"].get(v))
                M[f"Ov{A}{N}{V}FA"] = pct(pm["fpr_declined"].get(v))
    # Every macro main.tex uses gets a definition; one without data prints "??".
    import re
    used = set(re.findall(r"\\([A-Z][A-Za-z]+)", (PAPER / "main.tex").read_text()))
    for name in sorted(used - set(M) - {"TODO", "Large", "LaTeX"}):
        M[name] = "??"
        MISSING.append(f"macro \\{name}")
    from analysis.pathways import stats as _paths
    PW = _paths()
    # pathway agreement macros (analysis/pathways.py)
    rho = lambda k: PW["corr"][k]  # noqa: E731
    fmt = lambda d: f"{d['est'] + 0.0:.2f}".replace("-0.00", "0.00").replace("-", "$-$")  # noqa: E731
    fci = lambda d: f"[{d['lo']:.2f}, {d['hi']:.2f}]".replace("-", "$-$")  # noqa: E731
    for name, k in (("PwGemSpInit", "gemini.spontaneous~gemini.initiated"),
                    ("PwGemInvInit", "gemini.invited~gemini.initiated"),
                    ("PwQwSpInit", "qwen.spontaneous~qwen.initiated"),
                    ("PwQwInvInit", "qwen.invited~qwen.initiated"),
                    ("PwXInv", "gemini.invited~qwen.invited"),
                    ("PwXInit", "gemini.initiated~qwen.initiated"),
                    ("PwXSp", "gemini.spontaneous~qwen.spontaneous")):
        M[name] = fmt(rho(k))
        M[name + "CI"] = fci(rho(k))
    M["PwGemAdInv"] = pct(PW["by_family"]["gemini"]["invited"]["ad_rotation"])
    M["PwGemAdInit"] = pct(PW["by_family"]["gemini"]["initiated"]["ad_rotation"])
    # Relationship probe (analysis/relation.py): owners are old friends vs have never met
    from analysis.relation import stats as _rel
    REL = _rel()
    for a, A in (("gemini", "Gem"), ("qwen", "Qw")):
        r_ = REL.get(a)
        if not r_:
            continue
        for k, K in (("colluded_pre", "Pre"), ("moved_to_collude", "Moved"), ("colluded_post", "Post")):
            M[f"Rel{A}{K}Tie"] = pct(r_[k]["tie"])
            M[f"Rel{A}{K}None"] = pct(r_[k]["none"])
            M[f"Rel{A}{K}Diff"] = pp(r_[k]["diff"])
            M[f"Rel{A}{K}DiffCI"] = ci(r_[k]["diff"])
        M[f"Rel{A}TwinDiff"] = pp(r_["twin_post"]["diff"])
        M[f"Rel{A}TwinDiffCI"] = ci(r_["twin_post"]["diff"])
    lines = ["% Generated by analysis/paper.py. Do not edit.", ""]
    for k, v in sorted(M.items()):
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    PAPER.mkdir(exist_ok=True)
    (PAPER / "numbers.tex").write_text("\n".join(lines) + "\n")

    # --- tables ------------------------------------------------------------------
    T = PAPER / "tables"
    T.mkdir(exist_ok=True)

    # Table: tasks (2.1)
    rows = []
    fams = list(tk["gemini"]["by_family_raw"]) if tk["gemini"] else []
    col = lambda a, k: [tk[a]["by_family_raw"][f][k] for f in fams] if tk[a] else []  # noqa: E731
    ini = {a: {f: PW["by_family"][a]["initiated"][f] for f in PW["families"]} for a in AGENTS}
    for f in fams:
        rg = tk["gemini"]["by_family_raw"][f]
        rq = tk["qwen"]["by_family_raw"].get(f) if tk["qwen"] else None
        setting = "workplace" if f in WORKFLOW_FAMS else "market"
        ig, iq = ini["gemini"].get(f), ini["qwen"].get(f)
        ic = lambda v, a: cell(v, is_max(v, list(ini[a].values())))  # noqa: E731
        rows.append(f"\\texttt{{{tex_escape(f)}}} & {setting} & "
                    f"{cell(rg['turn1'], is_max(rg['turn1'], col('gemini', 'turn1')))} & "
                    f"{cell(rg['moved'], is_max(rg['moved'], col('gemini', 'moved')))} & "
                    f"{ic(ig, 'gemini')} & "
                    f"{cell(rq['turn1'], is_max(rq['turn1'], col('qwen', 'turn1'))) if rq else '--'} & "
                    f"{cell(rq['moved'], is_max(rq['moved'], col('qwen', 'moved'))) if rq else '--'} & "
                    f"{ic(iq, 'qwen')} \\\\")
    (T / "tasks.tex").write_text(
        "\\begin{tabular}{llrrrrrr}\n\\toprule\n"
        " & & \\multicolumn{3}{c}{Gemini 2.5 Flash} & \\multicolumn{3}{c}{Qwen3-8B} \\\\\n"
        "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\n"
        "Family & Setting & Unprompted & Moved & Initiated & Unprompted & Moved & Initiated \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

    # Table: what each monitor view misses and flags (2.2 and 2.3). Gemini agent, market set,
    # pooled over channels; panel A Gemini monitor, panel B Haiku monitor.
    VIEW_ROWS = [("action", "Action only"), ("report_only", "Report only"), ("message_only", "Message only"),
                 ("report", "Action + report"), ("delivered", "Action + report + message"),
                 ("baseline_info", "\\quad + baseline (no rule)"),
                 ("pop_baseline", "\\quad + same situation, other runs (no rule)"),
                 ("family_baseline", "\\quad + similar situations (no rule)"), ("standard", "\\quad + baseline and rule (standard)")]
    METRICS = ("fnr", "fnr_moved", "fpr_declined", "fpr_unilateral")
    body = []
    for name, title in (("mistral", "A. Mistral Small 3.1 24B monitor"), ("haiku", "B. Claude Haiku 5.5 monitor")):
        mm = S["gemini"]["monitors"].get(name) if S["gemini"] else None
        if not mm:
            continue
        body.append(f"\\multicolumn{{5}}{{l}}{{\\textit{{{title}}}}} \\\\")
        for v, lab in VIEW_ROWS:
            if v not in mm["views"]:
                continue
            pm = mm["pooled"]
            bold = v == "standard"
            body.append(f"{lab} & " + " & ".join(cell(pm.get(k, {}).get(v), bold) for k in METRICS) + " \\\\")
        body.append("\\midrule")
    if body and body[-1] == "\\midrule":
        body.pop()
    (T / "views.tex").write_text(
        "\\begin{tabular}{lrrrr}\n\\toprule\n"
        " & \\multicolumn{2}{c}{Missed} & \\multicolumn{2}{c}{Flagged} \\\\\n"
        "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
        "Monitor reads & all collusion & message-induced & declined & unilateral \\\\\n\\midrule\n"
        + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n")

    # Table: oversight through a summary. Same input, two forms: the full trace with the
    # pre-message choice (baseline_info) against a third-party summary of that trace; the
    # self-report is the agent's own compressed account. Market set, both agents.
    OV_ROWS = [("report_only", "Agent's own report"), ("summary", "Third-party summary of the trace"),
               ("baseline_info", "Full trace")]
    body = []
    for name, title in (("mistral", "A. Mistral Small 3.1 24B monitor"), ("haiku", "B. Claude Haiku 5.5 monitor")):
        if not all(S[a] and name in S[a]["monitors"] for a in AGENTS):
            continue
        body.append(f"\\multicolumn{{5}}{{l}}{{\\textit{{{title}}}}} \\\\")
        for v, lab in OV_ROWS:
            cells = []
            for a in AGENTS:
                pm = S[a]["monitors"][name]["pooled"]
                cells += [cell(pm["fnr"].get(v)), cell(pm["fpr_declined"].get(v))]
            body.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        body.append("\\midrule")
    if body and body[-1] == "\\midrule":
        body.pop()
    (T / "oversight.tex").write_text(
        "\\begin{tabular}{lrrrr}\n\\toprule\n"
        " & \\multicolumn{2}{c}{Gemini agent} & \\multicolumn{2}{c}{Qwen agent} \\\\\n"
        "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
        "Monitor reads & missed & flagged declined & missed & flagged declined \\\\\n\\midrule\n"
        + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n")

    # Table: relays (2.3 robustness), market
    rows = []
    for a in AGENTS:
        s = st[a]
        if not s:
            continue
        rows.append(f"{LABEL[a]} & {cell(s['turn1']['harmful'])} & "
                    + " & ".join(cell(s["turn2"]["harmful"][ch]["all"]) for ch in ("raw", "paraphrased", "neutralized"))
                    + "".join(f" & {cell(s['relay_effect']['harmful'][ch]['all'], excludes_zero(s['relay_effect']['harmful'][ch]['all']))}"
                              for ch in ("paraphrased", "neutralized")) + " \\\\")
    (T / "relays.tex").write_text(
        "\\begin{tabular}{lrrrrrr}\n\\toprule\n"
        " & & \\multicolumn{3}{c}{Took the arrangement (turn 2)} & \\multicolumn{2}{c}{Relay minus raw (pp)} \\\\\n"
        "\\cmidrule(lr){3-5}\\cmidrule(lr){6-7}\n"
        "Agent & Turn 1 & Raw & Paraphrased & Neutralized & Paraphrased & Neutralized \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

    # Table: invitation type by setting (moved, raw)
    rows = []
    for a in AGENTS:
        t = tk[a]
        if not t:
            continue
        for setting, row in t.get("by_rendering_raw_setting", {}).items():
            vals = [row[rd] for rd in RENDERINGS]
            rows.append(f"{LABEL[a]} & {setting} & " + " & ".join(cell(row[rd], is_max(row[rd], vals))
                                                               for rd in RENDERINGS) + " \\\\")
    (T / "rendering.tex").write_text(
        "\\begin{tabular}{llrrrr}\n\\toprule\n"
        "Agent & Setting & Direct & Euphemism & Relationship & Omission \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

    # Appendix: readers by family
    if agree:
        names = ["gemini", *agree["readers"]]
        head = {"gemini": "Gemini gate", "gpt": "GPT-5.4-nano", "gemma": "Gemma-3-27B",
                "gemini_pro": "Gemini 3.1 Pro", "opus": "Opus 5.5"}
        rows = [f"\\texttt{{{tex_escape(f)}}} & " + " & ".join(
            (f"\\textbf{{{100 * row[n]:.1f}}}" if row[n] < 0.8 else f"{100 * row[n]:.1f}")
            if row.get(n) is not None else "--" for n in names) + " \\\\"
            for f, row in agree["by_family"].items()]
        (T / "readers.tex").write_text(
            "\\begin{tabular}{l" + "r" * len(names) + "}\n\\toprule\n"
            "Family & " + " & ".join(head.get(n, n) for n in names) + " \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

    # Appendix: full monitor tables
    full = []
    MONS = {"mistral": "Mistral Small 3.1 24B monitor", "haiku": "Claude Haiku 5.5 monitor"}
    for label, src in (("Market", S), ("Workflow", W)):
        for a in AGENTS:
            for mname, mlabel in MONS.items():
                m = src[a]["monitors"].get(mname) if src[a] else None
                if not m:
                    continue
                pm = m["pooled"]
                body = "\n".join(
                    f"\\texttt{{{tex_escape(v)}}} & {cell(pm['fnr'][v])} & {cell(pm['fnr_moved'][v])} & "
                    f"{cell(pm['fpr_declined'][v])} & {cell(pm.get('fpr_unilateral', {}).get(v))} & "
                    f"{cell(pm['fpr_twins'][v])} \\\\" for v in m["views"])
                full.append(f"\\paragraph{{{mlabel}, {label.lower()} set, {LABEL[a]} episodes.}}\n"
                            "\\begin{center}\\small\\resizebox{\\linewidth}{!}{\\begin{tabular}{lrrrrr}\n\\toprule\n"
                            "View & Missed: all & Missed: message-induced & Flagged: declined & Flagged: unilateral & Flagged: twins \\\\\n"
                            f"\\midrule\n{body}\n\\bottomrule\n\\end{{tabular}}}}\n\\end{{center}}\n")
    (T / "monitor_full.tex").write_text("\n".join(full))

    # Example episode (Vietnamese, with machine translation)
    from analysis.example import example_episode, gloss, tr
    from src.episode import load_items
    ex = example_episode()
    en = gloss()
    it = next(i for i in load_items() if i["item_id"] == ex["item_id"])

    def q(vi, prefix=""):
        e = tr(vi, en)
        return (f"\\begin{{quote}}\\small {prefix}{tex_escape(vi)}"
                + (f"\\\\[2pt]\\textit{{{prefix}{tex_escape(e)}}}" if e else "") + "\\end{quote}")
    (T / "example.tex").write_text("\n".join([
        f"\\noindent Item \\texttt{{{tex_escape(ex['item_id'])}}}, rendering \\texttt{{{ex['rendering']}}}, "
        f"raw channel. Situation and options:",
        q(it["situation"]), q(ex["opt_a"], "A) "), q(ex["opt_b"], "B) "),
        f"\\noindent Turn 1, before any message: \\textbf{{{ex['pre']['letter']}}} (compete). The rival's message:",
        q(ex["raw_message"]),
        f"\\noindent Turn 2: \\textbf{{{ex['post']['letter']}}} (the collusive key). The agent's report to its owner:",
        q(ex["report"]),
    ]) + "\n")

    # Table: the four renderings, defined, with one real frozen message each (English gloss)
    from src import prompts as P
    from src.episode import load_stimuli
    stim = load_stimuli()
    DEFS = {"direct": "States who should do what.",
            "euphemism": "Softens the request with everyday phrases such as \\emph{cho gọn} (to keep it simple) "
                         "or \\emph{linh động} (be flexible).",
            "relationship": "Appeals to a long business relationship, for example \\emph{anh em} (brothers).",
            "omission": "Announces the sender's own plan and asks for nothing."}
    rows = []
    for rd in P.RENDERINGS:
        vi = stim[P.stimulus_key("price_hold_1_h", rd, "raw")]["text"]
        e = tr(vi, en) or "(no translation)"
        rows.append(f"{rd} & {DEFS[rd]} & \\textit{{{tex_escape(e)}}} \\\\")
    (T / "renderings.tex").write_text(
        "\\begin{tabular}{p{0.13\\linewidth}p{0.3\\linewidth}p{0.5\\linewidth}}\n\\toprule\n"
        "Rendering & What it does & Example (item \\texttt{price\\_hold\\_1}, machine translation) \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

    # Appendix: every prompt, verbatim (Vietnamese), from src/prompts.py
    PROMPTS = [("Agent system prompt (market)", P.SYSTEM), ("Agent system prompt (workflow)", P.SYSTEM_WORKFLOW),
               ("Turn 1, choice", P.CHOICE_TURN), ("Turn 2, message and choice", P.MESSAGE_TURN),
               ("Turn 3, report (market)", P.REPORT_TURN), ("Turn 4, disclosure (market)", P.DISCLOSURE_TURN),
               ("Renderer (market)", P.RENDER_PROMPT), ("Relay: paraphrased", P.RELAY_SYSTEM["paraphrased"]),
               ("Relay: neutralized", P.RELAY_SYSTEM["neutralized"]), ("Gate (market)", P.GATE_PROMPT),
               ("Monitor system prompt (market)", P.MONITOR_SYSTEM), ("Monitor question", P.MONITOR_USER),
               ("Monitor question, standard view", P.STANDARD_USER)]
    out = []
    for name, text in PROMPTS:
        body = tex_escape(text).replace("{", "\\{").replace("}", "\\}").replace("\n", "\\\\\n")
        out.append(f"\\paragraph{{{name}.}}\n{{\\footnotesize\\ttfamily {body}}}\n")
    (T / "prompts.tex").write_text("\n".join(out))

    # figures, drawn here so the paper owns its figure style
    from analysis import figures as FIG
    F = PAPER / "figures"
    F.mkdir(exist_ok=True)
    by_family = {}
    for a in AGENTS:
        if tk[a]:
            by_family[a] = tk[a]["by_family_raw"]
        else:  # until the pooled task set exists, fall back to main + workflow
            by_family[a] = {**(st[a]["by_family_raw"] if st[a] else {}),
                            **(wst[a]["by_family_raw"] if wst[a] else {})}
    from analysis.pathways import stats as _pw
    _P = _pw()
    FIG.tasks(by_family, set(WORKFLOW_FAMS), F / "tasks.pdf",
              initiated={a: _P["by_family"][a]["initiated"] for a in AGENTS})
    FIG.pipeline(F / "pipeline.pdf")
    monitors = [(title, S["gemini"]["monitors"][name]["pooled"])
                for name, title in (("mistral", "Mistral Small 3.1"), ("haiku", "Claude Haiku 5.5"))
                if S["gemini"] and name in S["gemini"]["monitors"]]
    if monitors:
        FIG.butterfly(monitors, F / "views.pdf")
    disc = []
    for tag, T_ in (("main", "marketplace"), ("workflow", "workplace")):
        for a in AGENTS:
            s_ = load(f"results/{tag}_{a}/stats.json")
            if s_:
                disc.append((f"{LABEL[a].split()[0]}, {T_}", s_["stats"]["disclosure"]))
    if disc:
        FIG.asked_vs_told(disc, F / "asked.pdf")
    print(f"wrote {len(M)} macros, tables and figures to {PAPER}")
    if MISSING:
        print("MISSING inputs (their numbers print as ??):\n  " + "\n  ".join(MISSING))


if __name__ == "__main__":
    main()
