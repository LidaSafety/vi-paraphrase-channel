"""Re-relay ONLY the relayed stimuli that came back identical to their raw message.

    .venv/bin/modal run scripts/modal_fix_relays.py

Rule (docs/execution-plan.md, Changes): a relay identical to its source carries
no manipulation and blocks the run (control 11). Those records, and only
those, are relayed again with the same prompt at temperature 0.7, up to three
attempts. The first non-identical, banned-phrase-free text is kept; every
attempt, including the original verbatim one, is stored on the record. Raw
messages and all other relays are untouched. The gate is then run on the new
texts and appended to gate.jsonl.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REMOTE = "/root/repo"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("requests>=2.31", "openai>=1.40", "python-dotenv>=1.0", "pyyaml>=6.0")
    .add_local_dir(ROOT / "src", f"{REMOTE}/src", ignore=["**/__pycache__"])
    .add_local_dir(ROOT / "configs", f"{REMOTE}/configs")
    .add_local_dir(ROOT / "data" / "items", f"{REMOTE}/data/items")
)
app = modal.App("vi-paraphrase-fix-relays")
RETRY_TEMPERATURE = 0.7


@app.function(image=image, timeout=60 * 20, secrets=[modal.Secret.from_name("collusion-keys"),
                                                      modal.Secret.from_name("vllm-key")])
def fix(recs: list[dict], items: list[dict], cfg: dict, qwen_url: str) -> list[dict]:
    sys.path.insert(0, REMOTE)
    from src import prompts as P
    from src.clients import GeminiClient, VLLMClient
    from src.episode import options

    pc, gc = cfg["paraphraser"], cfg["gate"]
    qwen = VLLMClient(model=pc["model"], base_url=qwen_url, max_tokens=pc["max_tokens"])
    gem = GeminiClient(model=gc["model"])
    by_id = {it["item_id"]: it for it in items}
    out = []
    for s in recs:
        attempts = [{"text": s["text"], "temperature": pc["temperature"], "identical": True}]
        for _ in range(3):
            msgs = [{"role": "system", "content": P.RELAY_SYSTEM[s["channel"]]},
                    {"role": "user", "content": P.RELAY_USER.format(message=s["source_message"])}]
            rep = qwen.chat(msgs, temperature=RETRY_TEMPERATURE, reasoning=pc["reasoning"])
            text = rep.text.strip().strip("“”\"").strip()
            same = text == s["source_message"].strip()
            attempts.append({"text": text, "temperature": RETRY_TEMPERATURE, "identical": same,
                             "banned_hits": P.banned_hits(text)})
            if text and not same and not P.banned_hits(text):
                break
        new = {**s, "text": attempts[-1]["text"], "relay_attempts": attempts,
               "relay_retry_rule": "identical-to-source, T=0.7, max 3"}
        it = by_id[s["item_id"]]
        opt_a, opt_b, _ = options(it, 0)
        g = gem.chat([{"role": "user", "content": P.GATE_PROMPT.format(
            **it, opt_a=opt_a, opt_b=opt_b, text=new["text"])}],
            temperature=gc["temperature"], reasoning=gc["reasoning"])
        out.append({"stimulus": new, "gate": {"key": s["key"], "reply": g.text, "error": None,
                                              "model": gc["model"], "rerun": True}})
    return out


@app.local_entrypoint()
def main() -> None:
    from src.episode import load_items
    from src.run_meta import load_cfg

    cfg = load_cfg()
    path = ROOT / "data/stimuli/stimuli.jsonl"
    lines = [json.loads(l) for l in path.read_text().splitlines()]
    targets = [r for r in lines[1:] if r["channel"] != "raw"
               and r["text"].strip() == r["source_message"].strip()]
    print(f"identical relays: {len(targets)}  {[t['key'] for t in targets]}")
    if not targets:
        return
    url = modal.Function.from_name(cfg["paraphraser"]["app"], "serve").get_web_url().rstrip("/") + "/v1"
    res = fix.remote(targets, load_items(), cfg, url)
    fixed = {r["stimulus"]["key"]: r["stimulus"] for r in res}
    lines[0]["_meta"].setdefault("fixes", []).append(
        {"script": "scripts/modal_fix_relays.py", "keys": sorted(fixed),
         "timestamp": datetime.now(timezone.utc).isoformat()})
    with path.open("w") as fh:
        for r in lines:
            r = fixed.get(r.get("key"), r)
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (ROOT / "data/stimuli/gate.jsonl").open("a") as fh:
        for r in res:
            fh.write(json.dumps(r["gate"], ensure_ascii=False) + "\n")
    for k, s in fixed.items():
        print(f"{k}: {len(s['relay_attempts']) - 1} retries -> {s['text'][:90]}")
