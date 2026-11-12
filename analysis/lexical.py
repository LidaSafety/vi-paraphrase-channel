"""Figure: the words themselves. Panel A, one frozen invitation and its four frozen summaries.
Panel B, an agent report that leaves the message out beside a neutral summary of the same
episode. Every excerpt is selected by a fixed rule in code and highlighted by fixed patterns;
nothing is chosen or edited by hand."""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.episode import load_items
from src.scoring import code_report

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_KEY = ("price_hold_1_h", "relationship")      # same message as the renderings table
# blue: words that carry the invitation; orange: the field that drops it; underline: loanwords
INVITE = [r"[Aa]nh em", r"giữ giá", r"[Đđ]ề nghị(?!: )", r"[Đđ]ề xuất", r"\bmong\b", r"luân phiên"]
# Panel B only: words that tie the decision to the rival
SOURCE = [r"đối thủ cạnh tranh", r"Gia Dụng Minh Tâm", r"thông báo từ", r"theo đề nghị"]
LOST = [r"Đề nghị: [Kk]hông có"]
LOAN = [r"\bdeal\b", r"\bok\b", r"\bsale\b"]
STYLE = {"raw": "Original", "sum_short": "Short", "sum_long": "Long", "sum_system": "System log",
         "sum_codeswitch": "Code-switched"}


def esc(s: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}")):
        s = s.replace(a, b)
    return s


def mark(text: str, source: bool = False) -> str:
    text = re.sub(r"\*\*", "", text).strip()
    text = re.sub(r"[ \t]*\n\s*", "\n", text)
    spans = []
    for kind, pats in (("lost", LOST), ("inv", INVITE + (SOURCE if source else [])), ("loan", LOAN)):
        for p in pats:
            for m in re.finditer(p, text, flags=re.I if kind == "loan" else 0):
                if not any(m.start() < e and s < m.end() for s, e, _ in spans):
                    spans.append((m.start(), m.end(), kind))
    out, i = [], 0
    for s, e, k in sorted(spans):
        out.append(esc(text[i:s]))
        w = esc(text[s:e])
        out.append({"lost": r"\colorbox{lexlost}{" + w + "}", "inv": r"\colorbox{lexinv}{" + w + "}",
                    "loan": r"\underline{" + w + "}"}[k])
        i = e
    out.append(esc(text[i:]))
    return "".join(out).replace("\n", r" \newline ")


def write(path: Path) -> None:
    stim = [json.loads(l) for l in (ROOT / "data/stimuli/stimuli.jsonl").read_text().splitlines()[1:]]
    by = {(s["item_id"], s["rendering"], s["channel"]): s["text"] for s in stim}
    rows = [f"{STYLE[ch]} & {mark(by[(*EXAMPLE_KEY, ch)])} \\\\" for ch in STYLE]

    # Panel B rule: first Qwen episode by id, harmful, raw channel, moved by the message, whose
    # report names neither the rival nor the arrangement, while the neutral summary does both.
    items = {it["item_id"]: it for it in load_items()}
    eps = [json.loads(l) for l in (ROOT / "data/episodes/episodes_qwen.jsonl").read_text().splitlines()[1:]]
    sums = {r["episode_id"]: r["summary"] for r in
            map(json.loads, (ROOT / "data/summaries/episodes_qwen__summarizer.jsonl").read_text().splitlines()[1:])}
    def code(t, it):
        return code_report(t, it["counterpart_principal"], it["counterpart_name"])
    pick = None
    for r in sorted(eps, key=lambda r: r["episode_id"]):
        it = items[r["item_id"]]
        s = sums.get(r["episode_id"])
        if (it["item_class"] == "harmful" and r["channel"] == "raw" and r.get("moved_to_collude") and s
                and not code(r["report"], it)["mentions_counterpart"] and code(s, it)["disclosed"]):
            pick = (r, s)
            break
    b = []
    if pick:
        r, s = pick
        b = [f"Message & {mark(r['delivered_message'])} \\\\",
             f"Agent's report & {mark(r['report'], True)} \\\\",
             f"Neutral summary & {mark(s, True)} \\\\"]
    # A key above the table, in the figure's own swatches, so the colours read without the caption.
    key = ("{\\raggedright\\footnotesize\\textbf{How to read the highlights}\\par\\smallskip\n"
           "\\begin{tabular}{@{}p{0.40\\linewidth}p{0.33\\linewidth}p{0.21\\linewidth}@{}}\n"
           "\\raggedright\\colorbox{lexinv}{\\strut\\ blue\\ }\\enspace words that carry the invitation or tie the decision "
           "to the rival: \\emph{anh em} (brothers), \\emph{gi\u1eef gi\u00e1} (hold the price), "
           "\\emph{\u0111\u1ec1 ngh\u1ecb} (propose) & "
           "\\raggedright\\colorbox{lexlost}{\\strut\\ orange\\ }\\enspace the field that erases the proposal: "
           "\\emph{\u0110\u1ec1 ngh\u1ecb: Kh\u00f4ng c\u00f3} (Proposal: none) & "
           "\\raggedright\\underline{underlined}\\enspace an English loanword (\\emph{deal})\\tabularnewline\n"
           "\\end{tabular}\\par}\\medskip\n")
    path.write_text(key +
        "\\begin{tabular}{@{}p{0.15\\linewidth}p{0.81\\linewidth}@{}}\n\\toprule\n"
        "\\multicolumn{2}{@{}l}{\\textit{A. One invitation and four summaries of it (agent sees one)}} \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\midrule\n"
        "\\multicolumn{2}{@{}l}{\\textit{B. A Qwen episode: what the agent told its owner, and what a neutral summarizer wrote}} \\\\\n\\midrule\n"
        + "\n".join(b) + "\n\\bottomrule\n\\end{tabular}\n")
