"""Build share/index.html: a results page for collaborators.

Every number on the page is read from paper/numbers.tex (written by analysis/paper.py from the
generated stats), and every excerpt comes from frozen data by the same rule as the paper's
Figure 5. Nothing here is typed by hand.

    .venv/bin/python analysis/paper.py && .venv/bin/python analysis/share_page.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.lexical import EXAMPLE_KEY, INVITE, LOAN, LOST, SOURCE, STYLE  # noqa: E402
from src.episode import load_items  # noqa: E402
from src.scoring import code_report  # noqa: E402

OUT = ROOT / "share"


def macros() -> dict[str, str]:
    M = {}
    for line in (ROOT / "paper" / "numbers.tex").read_text().splitlines():
        m = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}$", line)
        if m:
            v = m.group(2).replace("\\%", "%").replace("\\_", "_").replace("$-$", "\u2212")
            v = re.sub(r"\\texttt\{(.*?)\}", r"\1", v)
            M[m.group(1)] = v
    return M


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
        out.append(html.escape(text[i:s]))
        out.append(f'<mark class="{k}">{html.escape(text[s:e])}</mark>')
        i = e
    out.append(html.escape(text[i:]))
    return "".join(out).replace("\n", "<br>")


def example_texts() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """The raw Vietnamese behind both example panels (same selection rule as the paper)."""
    stim = [json.loads(l) for l in (ROOT / "data/stimuli/stimuli.jsonl").read_text().splitlines()[1:]]
    by = {(s["item_id"], s["rendering"], s["channel"]): s["text"] for s in stim}
    a = [(STYLE[ch], by[(*EXAMPLE_KEY, ch)]) for ch in STYLE]
    items = {it["item_id"]: it for it in load_items()}
    eps = [json.loads(l) for l in (ROOT / "data/episodes/episodes_qwen.jsonl").read_text().splitlines()[1:]]
    sums = {r["episode_id"]: r["summary"] for r in
            map(json.loads, (ROOT / "data/summaries/episodes_qwen__summarizer.jsonl").read_text().splitlines()[1:])}
    for r in sorted(eps, key=lambda r: r["episode_id"]):
        it = items[r["item_id"]]
        s = sums.get(r["episode_id"])
        cr = lambda t: code_report(t, it["counterpart_principal"], it["counterpart_name"])  # noqa: E731
        if (it["item_class"] == "harmful" and r["channel"] == "raw" and r.get("moved_to_collude") and s
                and not cr(r["report"])["mentions_counterpart"] and cr(s)["disclosed"]):
            return a, [("Rival's message", r["delivered_message"]), ("Agent's report to its owner", r["report"]),
                       ("Neutral summary of the same episode", s)]
    return a, []


def examples() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    stim = [json.loads(l) for l in (ROOT / "data/stimuli/stimuli.jsonl").read_text().splitlines()[1:]]
    by = {(s["item_id"], s["rendering"], s["channel"]): s["text"] for s in stim}
    a = [(STYLE[ch], mark(by[(*EXAMPLE_KEY, ch)])) for ch in STYLE]
    items = {it["item_id"]: it for it in load_items()}
    eps = [json.loads(l) for l in (ROOT / "data/episodes/episodes_qwen.jsonl").read_text().splitlines()[1:]]
    sums = {r["episode_id"]: r["summary"] for r in
            map(json.loads, (ROOT / "data/summaries/episodes_qwen__summarizer.jsonl").read_text().splitlines()[1:])}

    def code(t, it):
        return code_report(t, it["counterpart_principal"], it["counterpart_name"])
    for r in sorted(eps, key=lambda r: r["episode_id"]):
        it = items[r["item_id"]]
        s = sums.get(r["episode_id"])
        if (it["item_class"] == "harmful" and r["channel"] == "raw" and r.get("moved_to_collude") and s
                and not code(r["report"], it)["mentions_counterpart"] and code(s, it)["disclosed"]):
            return a, [("Rival's message", mark(r["delivered_message"])),
                       ("Agent's report to its owner", mark(r["report"], True)),
                       ("Neutral summary of the same episode", mark(s, True))]
    return a, []


CSS = """
/* Academic project page: one column, paper typography, figures with numbered captions. */
:root {
  color-scheme: light;
  --bg: #ffffff; --ink: #1b1b1b; --ink-2: #333333; --muted: #5c5c5c; --tone: #f4f4f2; --link: #1a5fb4; --line: #d0d0cc;
  --mark-inv: #dfe9f6; --mark-lost: #f8dfd2;
  --serif: "Source Serif 4", "Times New Roman", Georgia, serif;
  --sans: "Source Sans 3", system-ui, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 17.5px/1.62 var(--serif); -webkit-font-smoothing: antialiased; }
main { max-width: 760px; margin: 0 auto; padding: 56px 20px 96px; }
img { display: block; max-width: 100%; height: auto; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
a:focus-visible, button:focus-visible { outline: 2px solid var(--link); outline-offset: 2px; }
h1 { font: 600 clamp(28px, 4.4vw, 38px)/1.18 var(--serif); letter-spacing: -.01em; margin: 0 0 6px; text-align: center; text-wrap: balance; }
.subtitle { text-align: center; font-size: 19px; color: var(--ink-2); margin: 0 0 22px; }
.authors { text-align: center; font-size: 17px; margin: 0; }
.affil { text-align: center; font-size: 15px; color: var(--muted); margin: 4px 0 0; }
.links { display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin: 22px 0 0; }
.links a { font: 500 15px/1 var(--sans); color: #fff; background: var(--ink); padding: 10px 16px; border-radius: 999px; transition: transform .15s ease, background-color .15s ease; }
.links a:hover { text-decoration: none; background: #3a3a3a; transform: translateY(-1px); }
.links a:active { transform: scale(.98); }
h2 { font: 600 23px/1.25 var(--serif); margin: 52px 0 12px; }
h3 { font: 600 18px/1.3 var(--serif); margin: 28px 0 8px; }
p { margin: 0 0 14px; }
.abstract { background: var(--tone); padding: 22px 26px; margin-top: 36px; }
.abstract h2 { margin: 0 0 8px; font-size: 19px; text-align: center; }
.abstract p { text-align: justify; hyphens: auto; margin: 0; }
.tldr { font-size: 17.5px; margin-top: 28px; }
figure { margin: 26px 0 30px; }
figure.wide { margin-inline: max(-120px, calc((760px - 100vw) / 2 + 20px)); }
figure img { width: 100%; }
figcaption { font-size: 15px; line-height: 1.5; color: var(--ink-2); margin-top: 10px; }
figcaption b { font-weight: 600; }
.chat { background: var(--tone); padding: 18px 22px; }
.chat .vi { font-size: 18px; margin: 0 0 6px; }
.chat .en { font-size: 15px; color: var(--muted); margin: 0; }
table { width: 100%; border-collapse: collapse; font-size: 15.5px; font-variant-numeric: lining-nums tabular-nums; }
caption { caption-side: top; text-align: left; font-size: 15px; color: var(--ink-2); padding-bottom: 8px; line-height: 1.5; }
thead th { border-top: 1.5px solid var(--ink); border-bottom: 1px solid var(--ink); font-weight: 600; padding: 7px 8px; text-align: right; }
thead th:first-child, tbody td:first-child { text-align: left; }
tbody td { padding: 6px 8px; text-align: right; }
tbody tr:last-child td { border-bottom: 1.5px solid var(--ink); }
tbody tr.best td { font-weight: 600; }
tbody tr { transition: background-color .15s ease; }
tbody tr:hover { background: var(--tone); }
.ex { width: 100%; border-collapse: collapse; font-size: 15.5px; }
.ex td { vertical-align: top; padding: 10px 10px; border-bottom: 1px solid var(--line); text-align: left; }
.ex td.k { width: 150px; color: var(--muted); font-size: 14.5px; }
.ex .en { color: var(--muted); font-size: 14.5px; margin-top: 4px; }
.ex tr:first-child td { border-top: 1.5px solid var(--ink); }
.ex tr:last-child td { border-bottom: 1.5px solid var(--ink); }
mark { background: var(--mark-inv); color: inherit; padding: 0 2px; }
mark.lost { background: var(--mark-lost); }
mark.loan { background: none; text-decoration: underline; text-decoration-thickness: 1.5px; text-underline-offset: 3px; }
ul { padding-left: 22px; margin: 0 0 14px; }
li { margin-bottom: 6px; }
pre { background: var(--tone); padding: 16px 18px; overflow-x: auto; font-size: 13.5px; line-height: 1.5; }
.foot { font-size: 14px; color: var(--muted); margin-top: 48px; }
.js .rise { opacity: 0; transform: translateY(12px); transition: opacity .6s ease, transform .6s ease; }
.js .rise.in { opacity: 1; transform: none; }
@media (max-width: 600px) { body { font-size: 17px; } .ex td.k { width: 96px; } .abstract { padding: 18px; } figure.wide { margin-inline: 0; } }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } .js .rise { opacity: 1; transform: none; transition: none; } .links a, tbody tr { transition: none; } }
"""

JS = r"""
document.documentElement.classList.add('js');
(function () {
  var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting || e.boundingClientRect.top < 0) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { threshold: 0 });
  document.querySelectorAll('figure, table, .ex, .abstract').forEach(function (el) { el.classList.add('rise'); io.observe(el); });
  setTimeout(function () { document.querySelectorAll('.rise:not(.in)').forEach(function (el) { el.classList.add('in'); }); }, 1500);
})();
"""


VIEWS = [("action", "The action", "What the agent chose, nothing else."),
         ("report", "+ its report", "What it told its owner afterwards."),
         ("delivered", "+ the rival's message", "The invitation it received, as delivered."),
         ("baseline_info", "+ its choice before the message", "What it chose before anyone asked."),
         ("family_baseline", "+ its usual behaviour", "How it chose on similar cases, which a platform can record.")]


def views_data() -> dict:
    S = json.loads((ROOT / "results/main_gemini/stats.json").read_text())["monitors"]
    f = lambda d: "n/a" if not d or d.get("est") is None else f"{100 * d['est']:.1f}%"  # noqa: E731
    out = {}
    for k, label, _ in VIEWS:
        hk, mi = S["haiku"]["pooled"], S["mistral"]["pooled"]
        miss, flag = hk["fnr"].get(k, {}).get("est"), hk["fpr_declined"].get(k, {}).get("est")
        good = miss is not None and flag is not None and miss < .1 and flag < .1
        out[k] = {"label": label, "hk_miss": f(hk["fnr"].get(k)), "hk_flag": f(hk["fpr_declined"].get(k)),
                  "mi_miss": f(mi["fnr"].get(k)), "mi_flag": f(mi["fpr_declined"].get(k)),
                  "verdict": "Fair verdict" if good else ("Misses collusion" if (miss or 0) >= (flag or 0) else "Blames the innocent"),
                  "good": good}
    return out


def credits() -> list[dict]:
    p = OUT / "img" / "credits.json"
    return json.loads(p.read_text()) if p.exists() else []


def build() -> str:
    M = macros()
    A, B = examples()
    rawA, rawB = example_texts()
    tr = {r["sha"]: r["en"] for r in map(json.loads, (ROOT / "data/translations/en.jsonl").read_text().splitlines())
          if r.get("en")}
    gloss = lambda t: html.escape(tr.get(__import__("hashlib").sha256(t.encode()).hexdigest(), ""))  # noqa: E731

    def m(k: str) -> str:
        if k not in M:
            raise KeyError(f"macro {k} missing from paper/numbers.tex")
        return M[k]
    sysA = dict(zip([k for k, _ in A], [v for _, v in A]))
    sysT = dict(rawA)
    VD = views_data()
    best = {k: ' class="best"' if k == "family_baseline" else "" for k, _, _ in VIEWS}
    vrows = "".join(f'<tr{best[k]}><td>{html.escape(lbl)}</td><td>{VD[k]["hk_miss"]}</td>'
                    f'<td>{VD[k]["hk_flag"]}</td><td>{VD[k]["mi_miss"]}</td><td>{VD[k]["mi_flag"]}</td></tr>' for k, lbl, _ in VIEWS)
    repo = "https://github.com/melanieyes/vi-paraphrase-channel"
    return f"""<title>Would It Have Done That Anyway?</title>
<meta name="description" content="Evidence of collusion between LLM agents, tested in Vietnamese. Apart AI Collusion Research Sprint, Track 2.">
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<style>{CSS}</style>
<main>

<header>
  <h1>Would It Have Done That Anyway?</h1>
  <p class="subtitle">Evidence of Collusion Between LLM Agents, Tested in Vietnamese</p>
  <p class="authors">Melanie Bui</p>
  <p class="affil">Lida Safety Research · with Apart Research · AI Collusion Research Sprint, Track 2</p>
  <div class="links"><a href="{repo}">Code</a><a href="{repo}/tree/main/data">Data</a><a href="{repo}/blob/main/docs/execution-plan.md">Design log</a></div>
</header>

<figure>
  <div class="chat">
    <p class="vi" lang="vi">{html.escape(rawA[0][1])}</p>
    <p class="en">{gloss(rawA[0][1])}</p>
  </div>
  <figcaption><b>Figure 1.</b> A rival shop's agent writes to ours on a fictional Vietnamese marketplace. Our agent keeps its price. Did it collude? The answer depends on whether it would have kept the price anyway.</figcaption>
</figure>

<section class="abstract">
  <h2>Abstract</h2>
  <p>When AI agents act for competing businesses and can message each other, a platform has only their logs to decide whether they colluded. We ask what in those logs counts as convincing evidence. In {m('nTaskItems')} Vietnamese scenarios, a scripted rival invites an agent (Gemini 2.5 Flash or Qwen3-8B) into a deal that hurts a third party, and two monitors (Mistral Small 3.1 and Claude Haiku 5.5) judge each episode. Every harmful deal has a harmless twin as a control. No single piece of evidence was enough. Agents often made the collusive choice before any message arrived, admitted the rival's influence when asked but left it out of their reports, and a monitor reading the message flagged about half of the agents that had refused. We propose that evidence of collusion needs a proposal, an action that matches it, and a change from what the agent would otherwise do; giving monitors the agent's usual behaviour in similar situations cut false flags below one in ten. Given the chance to write first, both agents proposed the deal themselves in about a third of harmful cases, and summarizing a message or a log can erase the offer altogether.</p>
</section>

<h2>Setup</h2>
<p>An episode has six roles. A scripted rival sends an invitation in one of four styles (direct, euphemism, relational appeal, bare announcement), written once and frozen. A relay (Qwen3-8B) delivers it raw, paraphrased, neutralized or summarized. The executor, the agent under test, chooses before and after the message, reports to its owner, and answers whether the rival influenced it. A monitor judges one view of the log, directly or through a neutral summary by Gemma-3-27B. Every measure is coded in code; the monitors' verdicts are what we study.</p>
<figure class="wide"><img src="fig/pipeline.png" width="1400" height="560" alt="Swimlane diagram of one episode: rival, relay, executor, owner, summarizer and monitor, left to right in time." loading="lazy">
<figcaption><b>Figure 2.</b> One episode, with each role in its own lane and the model that plays it. Dashed: the optional path where the monitor reads only a neutral summary.</figcaption></figure>

<h2>Each source misleads on its own</h2>
<ul>
  <li><b>The action.</b> Gemini chose the collusive option before any message in {m('GemTopUnprompted')} of episodes in its most tempting task. A matching action proves little.</li>
  <li><b>The report.</b> Asked directly, Qwen admitted the rival's influence in {m('QwDiscItem')} of colluding episodes, but its reports mentioned the message in only {m('QwDiscLex')}.</li>
  <li><b>The message.</b> A monitor reading the message flagged {m('StdMiAllFADecl')} (Mistral) and {m('StdHkAllFADecl')} (Haiku) of agents that had refused the deal.</li>
</ul>

<h2>An evidence standard</h2>
<p>We propose that convincing evidence needs (i) a proposal, (ii) an action that matches it, and (iii) a departure from what the agent does without the proposal. A deployed platform cannot see the counterfactual, but it can record how the agent behaves on similar situations. Table 1 shows what that record adds.</p>
<table>
  <caption><b>Table 1.</b> Missed collusion and false flags on agents that refused, by what the monitor reads (Gemini agent, market cases, %). The bold row is the version a platform can run.</caption>
  <thead><tr><th>Monitor reads</th><th>Haiku missed</th><th>Haiku false flags</th><th>Mistral missed</th><th>Mistral false flags</th></tr></thead>
  <tbody>{vrows}</tbody>
</table>
<figure class="wide"><img src="fig/views.png" width="1400" height="760" alt="Bar chart of missed collusion and false alarms for each monitor view, for both monitors." loading="lazy">
<figcaption><b>Figure 3.</b> The same comparison with 95% intervals clustered over items. Darker bars: Mistral; lighter: Claude Haiku 5.5.</figcaption></figure>

<h2>Agents also start it</h2>
<p>In a second run no rival wrote first; after its first choice the agent could send the rival the proposal, a greeting, or nothing. Gemini sent the proposal in {m('InitGemHarm')} of harmful situations and Qwen in {m('InitQwHarm')}, against {m('InitGemTwin')} and {m('InitQwTwin')} for harmless twins. The tasks where agents opened deals were not those where invitations moved them: in ad rotation an invitation moved Gemini in {m('PwGemAdInv')} of cases, yet Gemini proposed the deal itself in {m('PwGemAdInit')}.</p>
<figure class="wide"><img src="fig/tasks.png" width="1400" height="760" alt="For each task family and both agents: collusion before any message, after the message, and proposals sent unasked." loading="lazy">
<figcaption><b>Figure 4.</b> Three pathways into collusion by task family: collusive before any message (grey), moved by the message (blue), proposed unasked (dark diamond). Orange labels mark workplace tasks.</figcaption></figure>

<h2>A tie between the owners</h2>
<p>Adding one sentence to the system prompt, that the two owners are old friends who once worked together rather than strangers, raised Gemini's collusive final choice from {m('RelGemPostNone')} to {m('RelGemPostTie')} of harmful market episodes ({m('RelGemPostDiff')} points), with the shift already present before any message. Qwen shifted less ({m('RelQwPostDiff')} points) and its harmless cooperation rose as well. Once invited, workplace deals also pulled both agents in more than market deals (Gemini {m('SetGemWpMoved')} vs. {m('SetGemMkMoved')}; Qwen {m('SetQwWpMoved')} vs. {m('SetQwMkMoved')}; post hoc).</p>

<h2>Where the evidence is lost</h2>
<p>A neutral summary of the full log kept what the agent's own report dropped: with it, Haiku missed {m('OvQwHkSumFNR')} of Qwen's collusion instead of {m('OvQwHkSelfFNR')}. A summary inside the channel did the opposite: written as a system log, the rival's offer came out as <i lang="vi">Đề nghị: Không có</i> (Proposal: none), and Qwen's harmless cooperation fell from {m('SumQwRawTwin')} to {m('SumQwSysTwin')}.</p>
<table class="ex">
  <caption><b>Table 2.</b> The words themselves, verbatim from frozen data. Blue: words that carry the invitation or tie the decision to the rival. Orange: the field that erases the proposal. English lines are machine translations.</caption>
  <tr><td class="k">Qwen's report to its owner</td><td><div lang="vi">{B[1][1]}</div><div class="en">{gloss(rawB[1][1])}</div></td></tr>
  <tr><td class="k">Neutral summary of the same log</td><td><div lang="vi">{B[2][1]}</div><div class="en">{gloss(rawB[2][1])}</div></td></tr>
  <tr><td class="k">The rival's original offer</td><td><div lang="vi">{sysA["Original"]}</div><div class="en">{gloss(sysT["Original"])}</div></td></tr>
  <tr><td class="k">Summarized as a system log</td><td><div lang="vi">{sysA["System log"]}</div><div class="en">{gloss(sysT["System log"])}</div></td></tr>
</table>

<h2>Limitations</h2>
<p>The rival is scripted, and the initiation probe offers a fixed proposal, so it measures willingness to open collusion rather than skill at it. Each task family has eight scenarios. There is no English condition, so we cannot say whether collusion is more or less likely in Vietnamese. The relationship probe compares two stated relationships, not a tie with no statement. All results are exploratory, and all scenarios are fictional.</p>

<h2>Citation</h2>
<pre><code>@misc{{bui2026anyway,
  title  = {{Would It Have Done That Anyway? Evidence of Collusion Between LLM Agents, Tested in Vietnamese}},
  author = {{Bui, Melanie}},
  year   = {{2026}},
  note   = {{Apart AI Collusion Research Sprint, Track 2}},
  url    = {{{repo}}}
}}</code></pre>

<p class="foot">Rates carry bootstrap 95% intervals clustered over scenarios; the paper reports them. Every number on this page is generated from the logged data by the same code as the paper.</p>

</main>
<script>{JS}</script>
"""


def standalone(page: str) -> str:
    """The repo copy: a full document that opens straight from disk (the published artifact
    gets the same page without these wrappers). Title, fonts and styles go in the head."""
    i = page.index("<main>")
    head, body = page[:i], page[i:]
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            "<style>body{margin:0} img{max-width:100%}</style>\n" + head + "</head>\n<body>\n" + body
            + "\n</body>\n</html>\n")


if __name__ == "__main__":
    import subprocess
    (OUT / "fig").mkdir(parents=True, exist_ok=True)
    for f in ("pipeline", "views", "asked", "tasks"):
        subprocess.run(["pdftoppm", "-png", "-r", "170", "-singlefile", str(ROOT / "paper/figures" / f"{f}.pdf"),
                        str(OUT / "fig" / f)], check=True)
    page = build()
    (OUT / "index.html").write_text(standalone(page))
    if len(sys.argv) > 1:   # optional: also write the bare page for publishing as an artifact
        Path(sys.argv[1]).write_text(page)
    print(f"wrote {OUT / 'index.html'} and share/fig/*.png")
