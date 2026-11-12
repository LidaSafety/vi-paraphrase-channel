"""English glosses of the Vietnamese texts, for DISPLAY ONLY.

    .venv/bin/python scripts/translate.py --local-env /Users/coherenteyes/agent-collusion-bench/.env

Machine translation by Claude Opus 5.5, keyed by the sha256 of the exact
Vietnamese text, appended to data/translations/en.jsonl (already translated
texts are skipped). Nothing here enters an episode, a gate, a monitor or a
reported rate: agents, relays and monitors only ever saw the Vietnamese.
The key is read from the given .env into this process and never printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/translations/en.jsonl"
MODEL = "claude-opus-5-5"
PROMPT = (
    "Translate this Vietnamese text into natural English. It comes from a fictional "
    "online marketplace study. Translate faithfully and keep the grammatical form: an "
    "instruction or decision option stays an imperative (\"Cut the price of X to Y.\"), a "
    "fragment stays a fragment, a statement stays a statement. Keep every number, price "
    "(đ) and shop name exactly. "
    "Keep the tone visible: if the Vietnamese is indirect, euphemistic or appeals to a "
    "relationship (for example \"anh em\"), the English should be too. Do not explain "
    "or add anything. Output only the translation.\n\n{text}"
)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_cache() -> dict[str, str]:
    if not OUT.exists():
        return {}
    return {r["sha"]: r["en"] for r in map(json.loads, OUT.read_text().splitlines()) if r.get("en")}


def texts_to_translate() -> list[tuple[str, str]]:
    from src.episode import load_items, load_stimuli
    out: list[tuple[str, str]] = []
    for it in load_items():
        for f in ("situation", "option_collude", "option_compete", "proposal"):
            out.append((f"item.{f}", it[f]))
    for s in load_stimuli().values():
        out.append((f"stimulus.{s['channel']}", s["text"]))
    # The agent report quoted in the generated report's example episode.
    from analysis.example import example_episode
    ex = example_episode()
    out.append(("episode.report", ex["report"]))
    seen, uniq = set(), []
    for kind, t in out:
        if t and sha(t) not in seen:
            seen.add(sha(t))
            uniq.append((kind, t))
    return uniq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local-env", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--share", action="store_true",
                    help="only the example texts quoted in share/ (results page and collaborator doc)")
    a = ap.parse_args()
    from dotenv import dotenv_values
    os.environ.update({k: v for k, v in dotenv_values(a.local_env).items()
                       if k == "ANTHROPIC_API_KEY" and v})
    from src.anthropic_client import AnthropicClient

    cache = load_cache()
    if a.share:
        from analysis.share_page import example_texts
        A, B = example_texts()
        pool = [(f"share.{k}", t) for k, t in A + B]
    else:
        pool = texts_to_translate()
    todo = [(k, t) for k, t in pool if sha(t) not in cache]
    if a.limit:
        todo = todo[:a.limit]
    print(f"to translate: {len(todo)} (already cached: {len(cache)})")
    client = AnthropicClient(model=MODEL, effort="low", max_tokens=4000)

    def one(kt):
        kind, text = kt
        try:
            r = client.chat([{"role": "user", "content": PROMPT.format(text=text)}])
            return {"sha": sha(text), "kind": kind, "vi": text, "en": r.text.strip(), "model": MODEL,
                    "stop_reason": r.raw.get("stop_reason"), "usage": r.raw.get("usage"), "error": None}
        except Exception as exc:  # noqa: BLE001
            return {"sha": sha(text), "kind": kind, "vi": text, "en": "", "model": MODEL,
                    "error": repr(exc)[:300]}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    n_err, cost = 0, 0.0
    with ThreadPoolExecutor(16) as ex, OUT.open("a") as fh:
        for rec in ex.map(one, todo):
            rec["timestamp"] = datetime.now(timezone.utc).isoformat()
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_err += bool(rec["error"] or not rec["en"])
            u = rec.get("usage") or {}
            cost += u.get("input_tokens", 0) * 4e-6 + u.get("output_tokens", 0) * 20e-6
    print(f"wrote {len(todo)} translations, {n_err} failed, cost ${cost:.2f} -> {OUT}")


if __name__ == "__main__":
    main()
