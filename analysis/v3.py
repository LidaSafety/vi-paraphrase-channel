"""Figures and macros for the version 3 paper (paper/main_v3.tex).

    .venv/bin/python -m analysis.v3

Reads results/language_{agent}/stats.json, results/targets/stats.json and results/red_language/stats.json.
Writes paper/figures/v3_*.pdf and paper/v3_numbers.tex. Terms follow docs/execution-plan.md, "Version 3":
B = proposal-consistent harmful action, C = observed switch, hard negative = harmful item, declined.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np

from analysis.extend import (AGENTS, BG, CELLS, INK, INK2, LABEL, LANGS, LCOL, LNAME, MCOL, PAPER, ROOT, SMONS,
                             _bars, _cell_label, _heat, cell, fig_red, macro_name, num)

RENDER = ("direct", "euphemism", "relationship", "omission")
TCOL = {"B": "#52514e", "C": "#c9c8c3"}


def _load(p):
    p = ROOT / p
    return json.loads(p.read_text()) if p.exists() else None


def fig_stages(S, path):
    keys = ("colluded_pre", "colluded_post", "twin_cooperate")
    short = {"colluded_pre": "Pre-proposal\nharmful choice", "colluded_post": "Proposal-consistent\nharmful action (B)",
             "twin_cooperate": "Twin cooperation\n(positive control)"}
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.6), sharey=True)
    for ax, agent in zip(axes, AGENTS):
        st = S.get(agent) or {}
        _bars(ax, keys, LANGS, lambda k, l: st.get("episodes", {}).get(k, {}).get("pooled", {}).get(l), LCOL, ymax=110)
        ax.set_xticklabels([short[k] for k in keys], fontsize=7)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
    axes[0].set_ylabel("% of episodes", fontsize=7.5, color=INK2)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    handles = [plt.Rectangle((0, 0), 1, 1, color=LCOL[l], label=LNAME[l]) for l in LANGS]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.06), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_switch(T, path):
    """Diverging bars: switch toward the proposal (right) and away from it (left), conditional on T1."""
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.4), sharey=True)
    for ax, agent in zip(axes, AGENTS):
        sw = T[agent]["switch"]
        ax.set_facecolor(BG)
        ax.xaxis.grid(True, color="#e9e8e4", linewidth=0.7)
        ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        for i, l in enumerate(LANGS):
            y = len(LANGS) - 1 - i
            for side, key, alpha in ((1, "toward", 1.0), (-1, "away", 0.45)):
                d = sw[key][l]
                v = 100 * d["est"]
                ax.barh(y, side * v, 0.62, color=LCOL[l], alpha=alpha, edgecolor=BG)
                ax.plot([side * 100 * d["lo"], side * 100 * d["hi"]], [y, y], color=INK, lw=0.7)
                ax.text(side * (100 * d["hi"] + 1.5), y, f"{v:.0f}", va="center", ha="left" if side > 0 else "right",
                        fontsize=6.5, color=INK2)
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_yticks(range(len(LANGS)))
        ax.set_yticklabels([LNAME[l] for l in reversed(LANGS)], fontsize=7.5)
        ax.set_xlim(-62, 62)
        ax.set_xticks([-50, -25, 0, 25, 50])
        ax.set_xticklabels(["50", "25", "0", "25", "50"], fontsize=7)
        ax.set_ylim(-0.6, 2.9)
        ax.tick_params(length=0)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
        ax.text(-3, 2.55, "← away from the proposal", fontsize=6.5, color=INK2, ha="right")
        ax.text(3, 2.55, "toward the proposal →", fontsize=6.5, color=INK2, ha="left")
    fig.supxlabel("Conditional switch rate, % of harmful episodes (away: of agents harmful at T1; toward: of agents not harmful at T1)",
                  fontsize=7, color=INK2, y=-0.02)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_targets(T, path):
    """AUC of the suspicion score for target B (vs hard negatives) and target C (vs unchanged harmful
    choices), Vietnamese episodes, Vietnamese prompt. Dashed line: chance."""
    mons = list(SMONS)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.5), sharey=True)
    for ax, agent in zip(axes, AGENTS):
        res = T[agent]["scores"]

        def get(mon, t):
            d = (res.get(mon) or {}).get("vi_msg_vi_frame") or {}
            k = {"B": "auc_B_vs_hard", "C": "auc_C_vs_unchanged"}[t]
            return d.get(k)
        _bars(ax, mons, ("B", "C"), get, TCOL, ymax=115, label_fmt="{:.0f}", fontsize=6)
        for txt in ax.texts:  # show AUC on the 0-1 scale
            txt.set_text(f"{float(txt.get_text()) / 100:.2f}")
        ax.axhline(50, color=INK, lw=0.8, ls=(0, (3, 2)))
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(["0", ".25", ".50", ".75", "1"], fontsize=7)
        ax.set_xticklabels([SMONS[m].replace("Claude ", "").replace(" Small 3.1", "") for m in mons], fontsize=7)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
    axes[0].set_ylabel("AUC of the suspicion score", fontsize=7.5, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=TCOL["B"], label="B: harmful action vs hard negatives"),
               plt.Rectangle((0, 0), 1, 1, color=TCOL["C"], label="C: switched vs unchanged harmful choice"),
               plt.Line2D([], [], color=INK, lw=0.8, ls=(0, (3, 2)), label="chance")]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.07), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_scores(S, path):
    """Heatmaps: AUC of B against hard negatives, and false positive rate on hard negatives at the
    Vietnamese-set threshold. Rows: agent x message language x prompt; columns: monitors."""
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
                A[i, j], F[i, j] = d["auc_hard"]["est"], 100 * d["fa_hard"]["est"]
    labels = [f"{LABEL[a].split()[0]} · {_cell_label(m, f)}" for a, m, f in rows]
    short = [SMONS[m].replace("Claude ", "").replace("Mistral Small 3.1", "Mistral").replace(" 27B", "") for m in mons]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.6), gridspec_kw={"wspace": 0.05})
    _heat(axes[0], A, labels, short, blue, 0.6, 1.0, "{:.2f}")
    _heat(axes[1], F, [""] * len(rows), short, orange, 0, 70, "{:.0f}")
    axes[1].set_yticklabels([])
    for ax in axes:
        ax.axhline(len(CELLS) - 0.5, color=INK, lw=0.8)
    axes[0].set_xlabel("AUC, B vs hard negatives (higher is better)", fontsize=7.5, color=INK2)
    axes[1].set_xlabel("False positive rate on hard negatives, %\n(threshold set on Vietnamese; lower is better)",
                       fontsize=7.5, color=INK2)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_renderings(T, path):
    """Conditional switch toward the proposal by rendering and language."""
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.5), sharey=True)
    for ax, agent in zip(axes, AGENTS):
        tb = T[agent]["switch"]["toward_by_rendering"]
        _bars(ax, RENDER, LANGS, lambda rd, l: tb[rd][l], LCOL, ymax=70)
        ax.set_xticklabels(RENDER, fontsize=7.5)
        ax.set_title(LABEL[agent], color=INK, loc="left", fontsize=9)
    axes[0].set_ylabel("Switch toward the proposal, %\n(of agents not harmful at T1)", fontsize=7.5, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=LCOL[l], label=LNAME[l]) for l in LANGS]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.07), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def table_language(T, S, path):
    """Main-text table for the AAAI version: every language-arm rate, estimate [95% interval], per agent."""
    rows = [("Pre-proposal harmful choice (T1)", lambda st, a, l: st["episodes"]["colluded_pre"]["pooled"].get(l)),
            ("Proposal-consistent harmful action (B)", lambda st, a, l: st["episodes"]["colluded_post"]["pooled"].get(l)),
            ("Switch toward (C), of not harmful at T1", lambda st, a, l: T[a]["switch"]["toward"].get(l)),
            ("Switch away, of harmful at T1", lambda st, a, l: T[a]["switch"]["away"].get(l)),
            ("Twin cooperation (positive control)", lambda st, a, l: st["episodes"]["twin_cooperate"]["pooled"].get(l))]
    mons = ("sonnet", "haiku", "mistral", "gemma")
    out = ["\\begin{tabular}{@{}llccc@{}}", "\\toprule",
           "Agent & Measure (\\%) & Vietnamese & English & Chinese \\\\", "\\midrule"]
    for a in AGENTS:
        st = S[a]
        for i, (name, get) in enumerate(rows):
            lead = LABEL[a] if i == 0 else ""
            out.append(f"{lead} & {name} & " + " & ".join(cell(get(st, a, l)) for l in LANGS) + " \\\\")
        out.append("\\addlinespace")
        for j, m in enumerate(mons):
            sc = st["scores"].get(m) or {}
            vals = [cell((sc.get(f"{l}_msg_{l}_frame") or {}).get("fa_hard")) for l in LANGS]
            name = SMONS[m].replace("Claude ", "") + ", false positives on hard negatives"
            out.append(f" & {name} & " + " & ".join(vals) + " \\\\")
        out.append("\\midrule" if a != AGENTS[-1] else "\\bottomrule")
    out.append("\\end{tabular}")
    path.write_text("% Generated by analysis/v3.py. Do not edit.\n" + "\n".join(out) + "\n")


def numbers(T, S):
    M = {}
    strong = [d["auc_hard"]["est"] for a in AGENTS for mon in ("sonnet", "haiku")
              for k, d in (((S.get(a) or {}).get("scores") or {}).get(mon) or {}).items() if k.endswith("_frame")]
    M["TgMinStrongAucB"] = f"{min(strong):.2f}"
    for agent, st in T.items():
        A = agent.capitalize()
        for key in ("toward", "away"):
            for k, d in st["switch"][key].items():
                diff = "minus" in k
                M[macro_name("Tg", A, key, k)] = (num(d["est"], diff) + ("" if diff else "\\%")) if d.get("est") is not None else "n/a"
                M[macro_name("Tg", A, key, k, "ci")] = cell(d, diff)
        for rd, res in st["switch"]["toward_by_rendering"].items():
            for k, d in res.items():
                diff = "minus" in k
                M[macro_name("Tg", A, "toward", rd, k)] = (num(d["est"], diff) + ("" if diff else "\\%")) if d.get("est") is not None else "n/a"
                M[macro_name("Tg", A, "toward", rd, k, "ci")] = cell(d, diff)
        for mon, res in st["scores"].items():
            for ck, d in res.items():
                for t in ("auc_B_vs_hard", "auc_C_vs_unchanged"):
                    v = d[t]
                    tag = "AucB" if "B" in t.split("_")[1] else "AucC"
                    M[macro_name("Tg", A, mon, ck, tag)] = f"{v['est']:.2f}"
                    M[macro_name("Tg", A, mon, ck, tag, "ci")] = f"{v['est']:.2f} [{v['lo']:.2f}, {v['hi']:.2f}]"
                for m, v in d.get("split", {}).items():
                    if m != "threshold":
                        M[macro_name("Tg", A, mon, ck, "split", m)] = num(v["mean"]) + "\\%"
    return M


def main() -> None:
    S = {a: _load(f"results/language_{a}/stats.json") for a in AGENTS}
    T = _load("results/targets/stats.json")
    R = _load("results/red_language/stats.json")
    if not (all(S.values()) and T):
        raise SystemExit("run analysis.language and analysis.targets first")
    F = PAPER / "figures"
    fig_stages(S, F / "v3_stages.pdf")
    fig_switch(T, F / "v3_switch.pdf")
    fig_targets(T, F / "v3_targets.pdf")
    fig_scores(S, F / "v3_scores.pdf")
    fig_renderings(T, F / "v3_renderings.pdf")
    if R:
        fig_red(R, F / "v3_red.pdf", what="uncaught B")
        fig_red(R, F / "v3_red_english.pdf", pol="english", what="uncaught B")
    table_language(T, S, PAPER / "tables" / "v3_language.tex")
    M = numbers(T, S)
    (PAPER / "v3_numbers.tex").write_text("% Generated by analysis/v3.py. Do not edit.\n"
                                          + "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in sorted(M.items())))
    print(f"wrote {len(M)} macros, 7 figures")


if __name__ == "__main__":
    main()
