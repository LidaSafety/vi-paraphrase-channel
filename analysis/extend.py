"""Numbers, tables and figures for paper/extend.tex (the language arm). Generated, never typed.

    .venv/bin/python -m analysis.language --agent gemini && .venv/bin/python -m analysis.language --agent qwen
    .venv/bin/python -m analysis.extend

Reads results/language_{agent}/stats.json (analysis/language.py) and writes
paper/extend_numbers.tex, paper/tables/ext_*.tex and paper/figures/ext_*.pdf. EXPLORATORY.

Figure style follows analysis/figures.py. Languages take categorical slots 1 to 3 of the dataviz
reference palette (validated light: CVD dE 9.2, normal-vision dE 27.6; aqua is below 3:1 contrast,
so every mark is also direct-labelled or has a distinct marker, and every figure has a table).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from analysis.figures import BG, GRID, INK, INK2, LABEL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
AGENTS = ("gemini", "qwen")
LANGS = ("vi", "en", "zh")
LNAME = {"vi": "Vietnamese", "en": "English", "zh": "Chinese"}
LCOL = {"vi": "#2a78d6", "en": "#eb6834", "zh": "#1baf7a"}
LMARK = {"vi": "o", "en": "s", "zh": "D"}
RENDER = ("direct", "euphemism", "relationship", "omission")
MEAS = {"colluded_pre": "Unprompted collusion", "moved_to_collude": "Attack uptake",
        "colluded_post": "Successful attack", "twin_cooperate": "Usefulness (benign tasks)"}
MONS = {"haiku": "Claude Haiku 5.5", "mistral": "Mistral Small 3.1"}


def load(agent):
    p = ROOT / "results" / f"language_{agent}" / "stats.json"
    return json.loads(p.read_text()) if p.exists() else None


def num(x, pp=False):
    """A percent with a true minus sign; pp adds a sign for differences."""
    if x is None:
        return "n/a"
    v = 100 * x
    s = f"{abs(v):.1f}"
    return ("−" if v < 0 else ("+" if pp and v > 0 else "")) + s


def cell(d, pp=False):
    if not d or d.get("est") is None:
        return "n/a"
    return f"{num(d['est'], pp)} [{num(d['lo'])}, {num(d['hi'])}]"


def excl0(d):
    return bool(d and d.get("est") is not None and (d["lo"] > 0 or d["hi"] < 0))


def macro_name(*parts):
    """LaTeX macro names take letters only."""
    out = ""
    for p in parts:
        p = str(p)
        out += "".join(c for c in p.title() if c.isalpha())
    return out


# --- figures -----------------------------------------------------------------------

def _axes(ax):
    ax.set_facecolor(BG)
    ax.xaxis.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)


MCOL = {"sonnet": "#6250d6", "haiku": "#e87ba4", "mistral": "#eda100", "gemma": "#008300"}  # validated, slots 7, 5, 4, 6


def _bars(ax, groups, series, get, colors, width=0.8, label_fmt="{:.0f}", ymax=100, fontsize=6):
    """Grouped columns with thin 95% whiskers and a value label on each column (relief rule)."""
    ax.set_facecolor(BG)
    ax.yaxis.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    n = len(series)
    w = width / n
    for gi, g in enumerate(groups):
        for si, ser in enumerate(series):
            d = get(g, ser)
            if not d or d.get("est") is None:
                continue
            x = gi - width / 2 + w * (si + 0.5)
            v = 100 * d["est"]
            ax.bar(x, v, w * 0.92, color=colors[ser], edgecolor=BG, linewidth=0.6)
            if "lo" in d:
                ax.plot([x, x], [100 * d["lo"], 100 * d["hi"]], color=INK, lw=0.7)
            top = max(v, 100 * d.get("hi", d["est"]))
            ax.text(x, top + ymax * 0.015, label_fmt.format(v), ha="center", va="bottom", fontsize=fontsize, color=INK2)
    ax.set_xticks(range(len(groups)))
    ax.set_ylim(0, ymax)
    ax.tick_params(axis="both", labelsize=7, length=0)


def fig_stages(S, path):
    """Grouped columns: the four measures, one column per language, one panel per agent."""
    keys = list(MEAS)
    short = {"colluded_pre": "Unprompted\ncollusion", "moved_to_collude": "Attack\nuptake",
             "colluded_post": "Successful\nattack", "twin_cooperate": "Usefulness\n(benign tasks)"}
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7), sharey=True)
    for ax, agent in zip(axes, AGENTS):
        st = S.get(agent) or {}
        _bars(ax, keys, LANGS, lambda k, l: st.get("episodes", {}).get(k, {}).get("pooled", {}).get(l), LCOL,
              ymax=110)
        ax.set_xticklabels([short[k] for k in keys], fontsize=7)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
    axes[0].set_ylabel("% of episodes", fontsize=7.5, color=INK2)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    handles = [plt.Rectangle((0, 0), 1, 1, color=LCOL[l], label=LNAME[l]) for l in LANGS]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.06), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_renderings(S, measure, path, ylabel):
    """Grouped columns: one group per rendering, one column per language, one panel per agent."""
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.5), sharey=True)
    for ax, agent in zip(axes, AGENTS):
        st = S.get(agent) or {}
        _bars(ax, RENDER, LANGS, lambda rd, l: st.get("episodes", {}).get(measure, {}).get(rd, {}).get(l), LCOL,
              ymax=80)
        ax.set_xticklabels(RENDER, fontsize=7.5)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
    axes[0].set_ylabel(ylabel, fontsize=7.5, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=LCOL[l], label=LNAME[l]) for l in LANGS]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.07), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_monitor(S, view, path):
    """Binary monitor: grouped columns per agent and message language; dark = prompt in the message's
    language, light = English prompt. Rows: miss rate, false positives on declined; columns: monitors."""
    rows = [("fnr", "Miss rate (%)"), ("flag_declined", "False positive rate, hard\nbenign trajectories (%)")]
    groups = [(a, l) for a in AGENTS for l in LANGS]
    PCOL = {"own": INK2, "en": "#c9c8c3"}
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 4.2), sharey="row")
    for c, mon in enumerate(MONS):
        for r, (meas, yl) in enumerate(rows):
            ax = axes[r][c]

            def get(g, pol, meas=meas, mon=mon):
                a, l = g
                m = ((S.get(a) or {}).get("monitors") or {}).get(mon, {}).get(view, {}).get(meas, {})
                return m.get(f"{l}_msg_{l}_monitor") if pol == "own" else (
                    None if l == "en" else m.get(f"{l}_msg_en_monitor"))
            _bars(ax, groups, ("own", "en"), get, PCOL, ymax=110)
            ax.set_xticklabels([f"{'Gemini' if a == 'gemini' else 'Qwen'}\n{LNAME[l]}" for a, l in groups], fontsize=6.5)
            ax.set_yticks([0, 50, 100])
            if r == 0:
                ax.set_title(MONS[mon], color=INK, loc="left", fontsize=9)
            if c == 0:
                ax.set_ylabel(yl, fontsize=7.5, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=PCOL["own"], label="monitor prompt in the message's language"),
               plt.Rectangle((0, 0), 1, 1, color=PCOL["en"], label="English monitor prompt")]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.04), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


CELLS = [("vi", "vi"), ("vi", "en"), ("en", "en"), ("zh", "zh"), ("zh", "en")]
SMONS = {"sonnet": "Claude Sonnet 5.5", "haiku": "Claude Haiku 5.5", "mistral": "Mistral Small 3.1",
         "gemma": "Gemma 3 27B"}


def _cell_label(msg, mlang):
    return f"{LNAME[msg]}" + ("" if msg == mlang else ", English prompt")


def _heat(ax, M, rows, cols, cmap, vmin, vmax, fmt):
    """Annotated heatmap; text switches to white on dark cells."""
    im = ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if v != v:  # NaN
                continue
            dark = (v - vmin) / (vmax - vmin) > 0.55
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=6.5, color="white" if dark else INK)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, fontsize=7, rotation=0)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=7)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([x - 0.5 for x in range(1, len(cols))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color=BG, linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    return im


def fig_scores(S, path):
    """Two annotated heatmaps: AUC (ranking) and false positive rate on agents that declined at the
    audit threshold fixed on Vietnamese. Rows: agent x message language x prompt; columns: monitors."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    blue = LinearSegmentedColormap.from_list("b", ["#ffffff", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
    orange = LinearSegmentedColormap.from_list("o", ["#ffffff", "#fbdccb", "#f2a07a", "#eb6834", "#8f3a14"])
    mons = list(SMONS)
    rows = [(a, m, f) for a in AGENTS for m, f in CELLS]
    A = np.full((len(rows), len(mons)), np.nan)
    F = np.full((len(rows), len(mons)), np.nan)
    for j, mon in enumerate(mons):
        for i, (a, m, f) in enumerate(rows):
            d = (((S.get(a) or {}).get("scores") or {}).get(mon) or {}).get(f"{m}_msg_{f}_frame")
            if d:
                A[i, j], F[i, j] = d["auc"]["est"], 100 * d["fa_hard"]["est"]
    labels = [f"{LABEL[a].split()[0]} · {_cell_label(m, f)}" for a, m, f in rows]
    short = [SMONS[m].replace("Claude ", "").replace("Mistral Small 3.1", "Mistral").replace(" 27B", "") for m in mons]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.6), gridspec_kw={"wspace": 0.05})
    _heat(axes[0], A, labels, short, blue, 0.75, 1.0, "{:.2f}")
    _heat(axes[1], F, [""] * len(rows), short, orange, 0, 70, "{:.0f}")
    axes[1].set_yticklabels([])
    for ax in axes:
        ax.axhline(len(CELLS) - 0.5, color=INK, lw=0.8)
    axes[0].set_xlabel("AUC, successful attacks vs all benign trajectories (higher is better)", fontsize=7.5, color=INK2)
    axes[1].set_xlabel("False positive rate on hard benign trajectories (agent declined), %\n(audit threshold set on Vietnamese; lower is better)",
                       fontsize=7.5, color=INK2)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def table_scores(S):
    lines = ["\\begin{tabular}{lllrrrr}", "\\toprule",
             "Monitor & Agent & Message, prompt & AUC & AUC, hard benign & Caught & FPR, hard benign \\\\",
             "\\midrule"]
    for mon in SMONS:
        first = True
        for agent in AGENTS:
            res = ((S.get(agent) or {}).get("scores") or {}).get(mon)
            if not res:
                continue
            for msg, ml in CELLS:
                d = res.get(f"{msg}_msg_{ml}_frame")
                if not d:
                    continue
                f3 = lambda k: f"{d[k]['est']:.3f} [{d[k]['lo']:.3f}, {d[k]['hi']:.3f}]"  # noqa: E731
                head = f"{SMONS[mon]} (t={res['threshold']})" if first else ""
                lines.append(f"{head} & {LABEL[agent]} & {_cell_label(msg, ml)} & {f3('auc')} & {f3('auc_hard')} & "
                             f"{cell(d['detect'])} & {cell(d['fa_hard'])} \\\\")
                first = False
        lines.append("\\addlinespace")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


def table_sensitivity(S):
    """Qwen review_swap twin drop: each language minus Vietnamese without that family."""
    lines = ["\\begin{tabular}{llrr}", "\\toprule",
             "Agent & Measure & English $-$ Vietnamese & Chinese $-$ Vietnamese \\\\", "\\midrule"]
    for agent in AGENTS:
        E = (S.get(agent) or {}).get("episodes_no_review_swap")
        if not E:
            continue
        for k, lab in MEAS.items():
            c = E[k]["pooled"]
            lines.append(f"{LABEL[agent] if k == 'colluded_pre' else ''} & {lab} & "
                         f"{cell(c.get('en_minus_vi'), True)} & {cell(c.get('zh_minus_vi'), True)} \\\\")
        lines.append("\\addlinespace")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


# --- tables ------------------------------------------------------------------------

def table_stages(S):
    lines = ["\\begin{tabular}{llrrr}", "\\toprule",
             "Agent & Measure & Vietnamese & English & Chinese \\\\", "\\midrule"]
    for agent in AGENTS:
        st = S.get(agent)
        if not st:
            continue
        for k, lab in MEAS.items():
            c = st["episodes"][k]["pooled"]
            lines.append(f"{LABEL[agent] if k == 'colluded_pre' else ''} & {lab} & "
                         + " & ".join(cell(c.get(l)) for l in LANGS) + " \\\\")
        lines.append("\\addlinespace")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


def table_diffs(S, measure):
    """Each language minus Vietnamese, per rendering; bold where the interval excludes 0."""
    lines = ["\\begin{tabular}{llrrrr}", "\\toprule",
             "Agent & Rendering & English $-$ Vietnamese & Chinese $-$ Vietnamese & "
             "English: gap $-$ direct gap & Chinese: gap $-$ direct gap \\\\", "\\midrule"]
    for agent in AGENTS:
        st = S.get(agent)
        if not st:
            continue
        for rd in ("pooled",) + RENDER:
            c = st["episodes"][measure][rd]
            cells = []
            for key in ("en_minus_vi", "zh_minus_vi", "en_gap_minus_direct_gap", "zh_gap_minus_direct_gap"):
                d = c.get(key)
                txt = cell(d, True) if d else ""
                cells.append(f"\\textbf{{{txt}}}" if excl0(d) else txt)
            lines.append(f"{LABEL[agent] if rd == 'pooled' else ''} & {rd} & " + " & ".join(cells) + " \\\\")
        lines.append("\\addlinespace")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


def table_gate(S):
    st = next((S[a] for a in AGENTS if S.get(a)), None)
    lines = ["\\begin{tabular}{lrrrrrr}", "\\toprule",
             " & \\multicolumn{3}{c}{Gate: still pushes to collude} & \\multicolumn{3}{c}{Mean characters} \\\\",
             "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
             "Rendering & Vietnamese & English & Chinese & Vietnamese & English & Chinese \\\\", "\\midrule"]
    for rd in RENDER:
        g = [st["stimuli"].get(l, {}).get(rd) for l in LANGS]
        lines.append(f"{rd} & " + " & ".join(f"{x['gate_pushes']}/{x['gate_n']}" if x else "n/a" for x in g) + " & "
                     + " & ".join(f"{x['mean_chars']:.0f}" if x else "n/a" for x in g) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines) + "\n"


def table_monitor(S, view):
    lines = ["\\begin{tabular}{lllrrr}", "\\toprule",
             "Monitor & Agent & Message & Miss rate, own prompt & Miss rate, English prompt & "
             "FPR, declined, own prompt \\\\", "\\midrule"]
    for mon in MONS:
        first = True
        for agent in AGENTS:
            m = ((S.get(agent) or {}).get("monitors") or {}).get(mon, {}).get(view, {})
            if not m:
                continue
            for l in LANGS:
                f, d = m["fnr"], m["flag_declined"]
                own, en = f.get(f"{l}_msg_{l}_monitor"), f.get(f"{l}_msg_en_monitor")
                if not own:
                    continue
                lines.append(f"{MONS[mon] if first else ''} & {LABEL[agent]} & {LNAME[l]} & {cell(own)} & "
                             f"{cell(en) if l != 'en' else '(same)'} & {cell(d.get(f'{l}_msg_{l}_monitor'))} \\\\")
                first = False
        lines.append("\\addlinespace")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


# --- numbers -----------------------------------------------------------------------

def numbers(S):
    M = {}
    for agent in AGENTS:
        st = S.get(agent)
        if not st:
            continue
        A = agent.capitalize()
        for k in MEAS:
            for rd in ("pooled",) + RENDER:
                c = st["episodes"][k][rd]
                for l in st["languages"]:
                    M[macro_name("Ext", A, k, rd, l)] = num(c[l]["est"]) + "\\%"
                for l in st["languages"][1:]:
                    d = c[f"{l}_minus_vi"]
                    M[macro_name("Ext", A, k, rd, l, "diff")] = cell(d, True)
                    M[macro_name("Ext", A, k, rd, l, "diffest")] = num(d["est"], True)
                    if f"{l}_gap_minus_direct_gap" in c:
                        M[macro_name("Ext", A, k, rd, l, "did")] = cell(c[f"{l}_gap_minus_direct_gap"], True)
        for mon, views in (st.get("monitors") or {}).items():
            for vw, ms in views.items():
                for meas, c in ms.items():
                    for key, d in c.items():
                        if key.endswith("_monitor"):
                            M[macro_name("Ext", A, mon, vw, meas, key)] = num(d["est"]) + "\\%"
                    for key in ("en_frame_minus_own", "own_frame_minus_vi"):
                        for l, d in c.get(key, {}).items():
                            M[macro_name("Ext", A, mon, vw, meas, key, l)] = cell(d, True)
        M[macro_name("Ext", A, "languages")] = str(len(st["languages"]))
        for mon, res in (st.get("scores") or {}).items():
            M[macro_name("Ext", A, mon, "threshold")] = str(res["threshold"])
            for key, d in res.items():
                if not isinstance(d, dict):
                    continue
                for k in ("auc", "auc_hard", "detect", "fa_hard"):
                    if k not in d:
                        continue
                    v = d[k]
                    if "auc" in k:
                        M[macro_name("Ext", A, mon, key, k)] = f"{v['est']:.3f}".replace("-", "\u2212")
                        M[macro_name("Ext", A, mon, key, k, "ci")] = (
                            f"{v['est']:+.3f} [{v['lo']:.3f}, {v['hi']:.3f}]" if "minus" in key
                            else f"{v['est']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}]").replace("-", "\u2212")
                    else:
                        M[macro_name("Ext", A, mon, key, k)] = cell(v, "minus" in key)
                        M[macro_name("Ext", A, mon, key, k, "est")] = num(v["est"], "minus" in key) + (
                            "" if "minus" in key else "\\%")
        E = st.get("episodes_no_review_swap") or {}
        for k in E:
            for l in st["languages"][1:]:
                M[macro_name("Ext", A, "norev", k, l, "diff")] = cell(E[k]["pooled"].get(f"{l}_minus_vi"), True)
    return M


# --- red team R1: the attacker picks the language ----------------------------------

POLS = {"matched": "monitor prompt in the message's language", "english": "English monitor prompt"}


def load_red():
    p = ROOT / "results" / "red_language" / "stats.json"
    return json.loads(p.read_text()) if p.exists() else None


def fig_red(R, path, pol="matched", what="uncaught collusion"):
    """Uncaught collusion per attacker language, one column per monitor. Rows: fixed threshold, fixed audit
    capacity; columns: agents. Black tick: a perfect monitor under the same capacity."""
    mons = [m for m in SMONS if any((R.get(a) or {}).get(m) for a in AGENTS)]
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 4.4), sharey=True)
    for r, mode in enumerate(("fixed_threshold", "fixed_capacity")):
        for c, agent in enumerate(AGENTS):
            ax = axes[r][c]

            def get(l, mon, mode=mode, agent=agent):
                return ((R.get(agent) or {}).get(mon, {}).get(mode, {}).get(pol, {}).get("cells", {}).get(l) or {}).get("uncaught")
            _bars(ax, LANGS, mons, get, MCOL, ymax=55, fontsize=5.5)
            if mode == "fixed_capacity":
                w = 0.8 / len(mons)
                for gi, l in enumerate(LANGS):
                    for si, mon in enumerate(mons):
                        d = (R.get(agent) or {}).get(mon, {}).get(mode, {}).get(pol, {}).get("cells", {}).get(l)
                        if d and "oracle_miss" in d:
                            fl = 100 * d["oracle_miss"]["est"] * d["n"]["collusive"] / d["n"]["harmful"]
                            if fl > 0.05:
                                x = gi - 0.4 + w * (si + 0.5)
                                ax.plot([x - w * 0.45, x + w * 0.45], [fl, fl], color=INK, lw=1.4)
            ax.set_xticklabels([LNAME[l] for l in LANGS], fontsize=7.5)
            if r == 1:
                ax.set_xlabel("language chosen by the attacker", fontsize=7.5, color=INK2)
            if r == 0:
                ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
            if c == 0:
                ax.set_ylabel({"fixed_threshold": "Fixed audit threshold", "fixed_capacity": "Fixed audit budget"}[mode]
                              + f"\n{what}, %", fontsize=7.5, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=MCOL[m], label=SMONS[m]) for m in mons]
    handles.append(plt.Line2D([], [], color=INK, lw=1.4, label="perfect monitor, same audit budget"))
    fig.legend(handles=handles, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 1.05), fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_diffs(S, path):
    """Each language minus Vietnamese (percentage points) for the four measures. Filled: all families;
    hollow: without review_swap (sensitivity). Columns: agents."""
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.1), sharey=True)
    for c, agent in enumerate(AGENTS):
        ax = axes[c]
        _axes(ax)
        st = S.get(agent) or {}
        ys, labels, y = [], [], 0
        for m in MEAS:
            for l in ("en", "zh"):
                for off, src, filled in ((0.15, "episodes", True), (-0.15, "episodes_no_review_swap", False)):
                    d = (((st.get(src) or {}).get(m) or {}).get("pooled") or {}).get(f"{l}_minus_vi")
                    if not d or d.get("est") is None:
                        continue
                    ax.plot([100 * d["lo"], 100 * d["hi"]], [y + off, y + off], color=LCOL[l], lw=1.2)
                    ax.plot(100 * d["est"], y + off, LMARK[l], ms=5, color=LCOL[l],
                            mfc=LCOL[l] if filled else BG, mec=LCOL[l], mew=1.2)
                ys.append(y)
                labels.append(f"{MEAS[m]} · {LNAME[l]}")
                y -= 1
            y -= 0.5
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_yticks(ys)
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlim(-30, 30)
        ax.tick_params(axis="x", labelsize=7)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=8.5)
    fig.supxlabel("Language minus Vietnamese (percentage points)", fontsize=8, color=INK2, y=0.08)
    handles = [plt.Line2D([], [], marker="o", color=INK2, ls="", ms=5, label="all families"),
               plt.Line2D([], [], marker="o", color=INK2, mfc=BG, ls="", ms=5, label="without review_swap")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.55, -0.03), fontsize=7.5)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def table_red(R):
    lines = ["\\begin{tabular}{llllrrr}", "\\toprule",
             "Monitor & Agent & Audit rule & Prompt & Uncaught, vi & Uncaught, en & Uncaught, zh \\\\", "\\midrule"]
    rule = {"fixed_threshold": "fixed threshold", "fixed_capacity": "fixed budget"}
    for mon in SMONS:
        first = True
        for agent in AGENTS:
            res = (R.get(agent) or {}).get(mon)
            if not res:
                continue
            first_agent = True
            for mode in rule:
                for pol in POLS:
                    c = res[mode][pol]["cells"]
                    head = f"{SMONS[mon]} (t={res['threshold']})" if first else ""
                    ag = LABEL[agent] if first_agent else ""
                    first_agent = False
                    lines.append(f"{head} & {ag} & {rule[mode]} & {'matched' if pol == 'matched' else 'English'} & "
                                 + " & ".join(cell(c.get(l, {}).get("uncaught")) for l in LANGS) + " \\\\")
                    first = False
        lines.append("\\addlinespace")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


def red_numbers(R):
    M = {}
    for agent, mons in R.items():
        A = agent.capitalize()
        for mon, res in mons.items():
            M[macro_name("Red", A, mon, "q")] = num(res["audit_share_q"]) + "\\%"
            for mode in ("fixed_threshold", "fixed_capacity"):
                md = "thr" if mode == "fixed_threshold" else "cap"
                for pol, r in res[mode].items():
                    for l, c in r["cells"].items():
                        for k in ("miss", "uncaught", "fpr_declined", "oracle_miss"):
                            if k in c:
                                M[macro_name("Red", A, mon, md, pol, l, k)] = num(c[k]["est"]) + "\\%"
                                M[macro_name("Red", A, mon, md, pol, l, k, "ci")] = cell(c[k])
                    for k, w in r["worst"].items():
                        M[macro_name("Red", A, mon, md, pol, "worst", k)] = cell(w)
                        M[macro_name("Red", A, mon, md, pol, "worst", k, "lang")] = LNAME[w["language"]]
    return M


def main() -> None:
    S = {a: load(a) for a in AGENTS}
    if not any(S.values()):
        raise SystemExit("run analysis/language.py first")
    (PAPER / "figures").mkdir(exist_ok=True)
    (PAPER / "tables").mkdir(exist_ok=True)
    fig_stages(S, PAPER / "figures" / "ext_stages.pdf")
    fig_renderings(S, "colluded_post", PAPER / "figures" / "ext_renderings.pdf",
                   "Successful attack, %")
    fig_renderings(S, "moved_to_collude", PAPER / "figures" / "ext_moved.pdf",
                   "Attack uptake, %")
    fig_monitor(S, "delivered", PAPER / "figures" / "ext_monitor.pdf")
    (PAPER / "tables" / "ext_stages.tex").write_text(table_stages(S))
    (PAPER / "tables" / "ext_post.tex").write_text(table_diffs(S, "colluded_post"))
    (PAPER / "tables" / "ext_moved.tex").write_text(table_diffs(S, "moved_to_collude"))
    (PAPER / "tables" / "ext_gate.tex").write_text(table_gate(S))
    (PAPER / "tables" / "ext_monitor.tex").write_text(table_monitor(S, "delivered"))
    fig_scores(S, PAPER / "figures" / "ext_scores.pdf")
    (PAPER / "tables" / "ext_scores.tex").write_text(table_scores(S))
    (PAPER / "tables" / "ext_sensitivity.tex").write_text(table_sensitivity(S))
    M = numbers(S)
    R = load_red()
    fig_diffs(S, PAPER / "figures" / "ext_diffs.pdf")
    if R:
        fig_red(R, PAPER / "figures" / "ext_red.pdf")
        fig_red(R, PAPER / "figures" / "ext_red_english.pdf", pol="english")
        (PAPER / "tables" / "ext_red.tex").write_text(table_red(R))
        M.update(red_numbers(R))
    (PAPER / "extend_numbers.tex").write_text(
        "% Generated by analysis/extend.py. Do not edit.\n"
        + "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in sorted(M.items())))
    print(f"wrote {len(M)} macros, {5 if R else 4} figures, {7 if R else 6} tables")


if __name__ == "__main__":
    main()
