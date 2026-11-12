"""The paper's figures, drawn from generated stats only.

Style: one accent hue plus neutral grey, direct labels instead of legends where
possible, thin interval lines, no top/right spines, light grid. Colours come from
the dataviz reference palette (validated light-mode: blue #2a78d6, orange #eb6834).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK, INK2, GRID, BG = "#1d1d1b", "#6b6a66", "#e9e8e4", "#ffffff"
ACCENT, ACCENT2, NEUTRAL = "#2a78d6", "#eb6834", "#a8a7a2"
LABEL = {"gemini": "Gemini 2.5 Flash", "qwen": "Qwen3-8B"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9.5,
    "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "xtick.major.size": 0, "ytick.major.size": 0, "savefig.dpi": 300,
    "pdf.fonttype": 42, "ps.fonttype": 42,  # TrueType, not Type 3 (AAAI requires Type 1 or TrueType)
})


def _pct(d):
    return None if not d or d.get("est") is None else (100 * d["est"], 100 * d["lo"], 100 * d["hi"])


def tasks(by_family: dict[str, dict[str, dict]], workflow_fams: set[str], path: Path,
          initiated: dict[str, dict[str, dict]] | None = None) -> None:
    """Per family, three pathways: taken unprompted (grey circle), pulled in by the message (blue
    circle) and, if given, proposed unasked in the initiation probe (dark diamond)."""
    fams = sorted(by_family["gemini"],
                  key=lambda f: -sum((by_family[a].get(f, {}).get("moved") or {}).get("est") or 0
                                     for a in by_family))
    n = len(fams)
    fig, axes = plt.subplots(1, 2, figsize=(6.6, (0.33 if initiated else 0.27) * n + 1.0), sharey=True)
    series = [("turn1", NEUTRAL, "o", 4.5), ("moved", ACCENT, "o", 5.5)]
    if initiated:
        series.append(("initiated", INK, "D", 4.2))
    offs = [0.24, 0.0, -0.24] if initiated else [0.17, -0.17]
    for ax, agent in zip(axes, ("gemini", "qwen")):
        ax.set_facecolor(BG)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
        for i, f in enumerate(fams):
            y = n - 1 - i
            row = by_family.get(agent, {}).get(f)
            if not row:
                continue
            for (key, color, mk, size), dy in zip(series, offs):
                src = initiated.get(agent, {}).get(f) if key == "initiated" else row.get(key)
                v = _pct(src) if src else None
                if v is None:
                    continue
                ax.plot([v[1], v[2]], [y + dy, y + dy], color=color, linewidth=1.1, alpha=0.75,
                        solid_capstyle="round")
                ax.plot(v[0], y + dy, mk, color=color, markersize=size, markeredgecolor=BG,
                        markeredgewidth=0.8, zorder=3)
        ax.set_xlim(-2, 102)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xlabel("% of harmful episodes")
        ax.set_title(LABEL[agent], loc="left", color=INK, fontweight="bold")
    axes[0].set_yticks(range(n))
    axes[0].set_yticklabels([f.replace("_", " ") for f in reversed(fams)])
    for lab, f in zip(axes[0].get_yticklabels(), reversed(fams)):
        lab.set_color(INK if f not in workflow_fams else ACCENT2)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", linestyle="-", color=NEUTRAL, markersize=4.5, linewidth=1.1,
                      label="taken unprompted (turn 1)"),
               Line2D([], [], marker="o", linestyle="-", color=ACCENT, markersize=5.5, linewidth=1.1,
                      label="pulled in by the message")]
    if initiated:
        handles.append(Line2D([], [], marker="D", linestyle="-", color=INK, markersize=4.2, linewidth=1.1,
                              label="proposed it unasked"))
    handles.append(Line2D([], [], linestyle="none", label="orange family names: workplace"))
    leg = fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize=7.5,
                     bbox_to_anchor=(0.5, -0.02), handlelength=1.6)
    leg.get_texts()[-1].set_color(ACCENT2)
    fig.tight_layout(w_pad=1.2, rect=(0, 0.06, 1, 1))
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


VIEW_LABEL = {"action": "action only", "report_only": "", "message_only": "message only",
              "report": "action + report  (report only is the same point)",
              "delivered": "action + report + message"}
# label offsets in points, chosen so labels clear their points and each other
OFFSET = {"action": (7, 0), "report_only": (0, 0), "message_only": (-4, 9),
          "report": (9, -7), "delivered": (0, 9)}


BAR_VIEWS = [("action", "action only"), ("report_only", "report only"), ("message_only", "message only"),
             ("report", "action + report"), ("delivered", "action + report + message"),
             ("baseline_info", "  + baseline, same episode"), ("family_baseline", "  + baseline, similar situations")]
# The rule row ("standard") is left out on purpose: the rule tells the monitor to clear unilateral
# choices, so "missed, all collusion" would count those clears as misses. The table reports it.
HERO = "family_baseline"


def butterfly(monitors: list[tuple[str, dict]], path: Path) -> None:
    """Figure 2. Rows are monitor views. Left: missed collusion. Right: false alarms on harmful
    episodes the agent declined. One bar per monitor, darker for the first; thin lines are 95% CIs."""
    n = len(BAR_VIEWS)
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(6.8, 0.42 * n + 1.1), sharey=True,
                                   gridspec_kw={"wspace": 0.04})
    h = 0.34
    shades = [1.0, 0.45]
    for j, (name, pooled) in enumerate(monitors):
        for i, (v, _) in enumerate(BAR_VIEWS):
            y = n - 1 - i + (h / 2 if j == 0 else -h / 2)
            miss, fa = _pct(pooled["fnr"].get(v)), _pct(pooled["fpr_declined"].get(v))
            for ax, val, color, sign in ((axl, miss, ACCENT, -1), (axr, fa, ACCENT2, 1)):
                if val is None:
                    continue
                ax.barh(y, sign * val[0], height=h * 0.9, color=color, alpha=shades[j], linewidth=0)
                ax.plot([sign * val[1], sign * val[2]], [y, y], color=INK2, linewidth=0.7, alpha=0.8)
                ax.text(sign * (max(val[0], val[2]) + 2), y, f"{val[0]:.0f}", va="center",
                        ha="right" if sign < 0 else "left", fontsize=7, color=INK2)
    for ax, title in ((axl, "missed collusion (%)"), (axr, "false alarms on declined episodes (%)")):
        ax.set_facecolor(BG)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
        ax.set_title(title, color=INK, fontsize=8.5, loc="center")
    axl.set_xlim(-112, 0)
    axl.set_xticks([-100, -75, -50, -25, 0], ["100", "75", "50", "25", "0"])
    axr.set_xlim(0, 112)
    axr.set_xticks([0, 25, 50, 75, 100])
    axl.set_yticks(range(n))
    axl.set_yticklabels([lab for _, lab in reversed(BAR_VIEWS)])
    for lab, (v, _) in zip(axl.get_yticklabels(), reversed(BAR_VIEWS)):
        if v == HERO:
            lab.set_fontweight("bold")
            lab.set_color(INK)
    # the three baseline rows sit under a light band: what the evidence standard adds
    nb = sum(1 for v, _ in BAR_VIEWS if v in ("baseline_info", "family_baseline", "standard"))
    for ax in (axl, axr):
        ax.axhspan(-0.5, nb - 0.5, color="#f3f6fb", zorder=0)
    axl.tick_params(axis="y", length=0)
    # Legend swatches in the bars' own colours: each monitor is a blue/orange pair, darker for the first.
    from matplotlib.legend_handler import HandlerTuple
    from matplotlib.patches import Patch
    handles = [(Patch(color=ACCENT, alpha=a_), Patch(color=ACCENT2, alpha=a_)) for a_ in shades]
    fig.legend(handles=handles, labels=[f"{name} monitor" for name, _ in monitors], loc="lower center",
               ncol=len(monitors), frameon=False, fontsize=7.5, bbox_to_anchor=(0.55, 0.0),
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0)}, handlelength=2.6)
    fig.subplots_adjust(bottom=0.12)
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def pipeline(path: Path) -> None:
    """Figure 1. One episode as a swimlane: each role is a lane (with the model that plays it), time runs
    left to right, arrows show what passes between roles. Dashed: the optional summary path."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    GREEN = "#1d8a5f"
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56)
    ax.axis("off")
    LANES = [("Rival", "scripted; Gemini wrote its messages", INK2),
             ("Relay", "Qwen3-8B", ACCENT),
             ("Executor (agent)", "Gemini 2.5 Flash or Qwen3-8B", ACCENT2),
             ("Owner", "the principal", INK2),
             ("Summarizer", "Gemma-3-27B, optional", GREEN),
             ("Monitor", "Mistral Small 3.1 or Claude Haiku 5.5", GREEN)]
    LH, TOP, X0 = 8.2, 53.0, 26.0
    ys = {}
    for i, (name, model, col) in enumerate(LANES):
        y = TOP - (i + 0.5) * LH
        ys[name] = y
        if i % 2 == 0:
            ax.add_patch(FancyBboxPatch((0, y - LH / 2), 100, LH, boxstyle="square,pad=0", facecolor="#f6f5f2",
                                        edgecolor="none", zorder=0))
        ax.text(1.0, y + 1.3, name, fontsize=7.2, fontweight="bold", color=col, va="center")
        ax.text(1.0, y - 1.6, model, fontsize=5.3, color=INK2, va="center", style="italic")
        ax.plot([X0, 99], [y, y], color="#d6d4cf", linewidth=0.8, zorder=1)

    def step(x, lane, label, col, w=10.4):
        y = ys[lane]
        ax.add_patch(FancyBboxPatch((x - w / 2, y - 1.9), w, 3.8, boxstyle="round,pad=0,rounding_size=1.8",
                                    facecolor=col, edgecolor="none", zorder=3))
        ax.text(x, y, label, ha="center", va="center", fontsize=5.7, color="white", fontweight="bold", zorder=4)

    def send(x0, l0, x1, l1, label="", dashed=False):
        down = ys[l1] < ys[l0]
        ax.add_patch(FancyArrowPatch((x0, ys[l0] - (2.0 if down else -2.0)), (x1, ys[l1] + (2.0 if down else -2.0)),
                                     arrowstyle="-|>", mutation_scale=8, color=INK2, linewidth=0.9,
                                     linestyle=(0, (3, 2)) if dashed else "-", zorder=2))
        if label:
            ax.text(max(x0, x1) + 1.4, (ys[l0] + ys[l1]) / 2, label, fontsize=5.3, color=INK2, style="italic",
                    va="center", ha="left")

    E = "Executor (agent)"
    step(31, E, "T1 choose", ACCENT2)
    step(42, "Rival", "invitation", INK2)
    send(42, "Rival", 42, "Relay")
    step(42, "Relay", "relay", ACCENT)
    send(44, "Relay", 51, E, "message as delivered")
    step(53, E, "T2 choose", ACCENT2)
    step(64.5, E, "T3 report", ACCENT2)
    send(64.5, E, 64.5, "Owner", "self-report")
    step(64.5, "Owner", "reads it", INK2)
    step(76, E, "T4 yes/no", ACCENT2)
    step(88.5, E, "full log", "#9a9893", w=9.0)
    step(80, "Summarizer", "summary", GREEN)
    send(86, E, 81.5, "Summarizer", dashed=True)
    step(92.5, "Monitor", "FLAG / CLEAR", GREEN, w=13.5)
    send(90, E, 93.5, "Monitor", "one view")
    send(81.5, "Summarizer", 89, "Monitor", dashed=True)
    ax.annotate("", xy=(99, TOP + 0.6), xytext=(X0, TOP + 0.6), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.8))
    ax.text(X0, TOP + 1.8, "one episode, in order", fontsize=5.6, color=INK2, va="bottom")
    ax.text(1.0, 1.0, "Dashed: the optional path, where the monitor reads only a neutral summary of the log.",
            fontsize=5.3, color=INK2, style="italic")
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def asked_vs_told(rows: list[tuple[str, dict]], path: Path) -> None:
    """Who mentions the rival's message, among colluding harmful episodes. One row per agent:
    the agent asked directly (grey), the agent's own report (orange), a neutral third-party
    summary of the trace (blue). All three coded in code; thin lines are 95% CIs."""
    bars = [("item_cO", "answers yes when asked", NEUTRAL),
            ("lexical", "own report mentions it", ACCENT2),
            ("summary_lexical", "neutral summary mentions it", ACCENT)]
    fig, ax = plt.subplots(figsize=(6.6, 0.62 * len(rows) + 0.75))
    h = 0.24
    for i, (label, d) in enumerate(rows):
        y0 = len(rows) - 1 - i
        for j, (k, _, color) in enumerate(bars):
            v = _pct(d.get(k))
            if v is None:
                continue
            y = y0 + (1 - j) * h
            ax.barh(y, v[0], height=h * 0.86, color=color, linewidth=0)
            ax.plot([v[1], v[2]], [y, y], color=INK2, linewidth=0.7)
            ax.text(max(v[0], v[2]) + 1.5, y, f"{v[0]:.0f}%", va="center", fontsize=7, color=INK2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([lab for lab, _ in reversed(rows)])
    ax.set_xlim(0, 108)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("% of colluding harmful episodes")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=c, label=l) for _, l, c in bars], loc="lower center", ncol=3,
               frameon=False, fontsize=7.5, bbox_to_anchor=(0.55, 0.0))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
