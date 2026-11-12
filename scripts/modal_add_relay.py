"""Add one new relayed channel to the frozen market stimuli, then gate it.

    .venv/bin/modal run scripts/modal_add_relay.py --channel summarized

Raw messages and existing relays are untouched. Each raw message is relayed
once with RELAY_SYSTEM[channel] at the paraphraser's settings; a reply identical
to its source or with a banned phrase is retried at T=0.7, up to three times,
as in scripts/modal_fix_relays.py. New records are appended to stimuli.jsonl
and their gate replies to gate.jsonl.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
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
app = modal.App("vi-paraphrase-add-relay")
RETRY_TEMPERATURE = 0.7


@app.function(image=image, timeout=60 * 40, secrets=[modal.Secret.from_name("collusion-keys"),
                                                      modal.Secret.from_name("vllm-key")])
def add(raws: list[dict], items: list[dict], cfg: dict, qwen_url: str, channel: str) -> list[dict]:
    sys.path.insert(0, REMOTE)
    from src import prompts as P
    from src.clients import GeminiClient, VLLMClient
    from src.episode import options

    pc, gc = cfg["paraphraser"], cfg["gate"]
    qwen = VLLMClient(model=pc["model"], base_url=qwen_url, max_tokens=pc["max_tokens"])
    gem = GeminiClient(model=gc["model"])
    by_id = {it["item_id"]: it for it in items}

    def one(raw):
        msgs = [{"role": "system", "content": P.RELAY_SYSTEM[channel]},
                {"role": "user", "content": P.RELAY_USER.format(message=raw["text"])}]
        attempts, obs = [], None
        for temp in (pc["temperature"], RETRY_TEMPERATURE, RETRY_TEMPERATURE, RETRY_TEMPERATURE):
            rep = qwen.chat(msgs, temperature=temp, reasoning=pc["reasoning"])
            text, obs = rep.text.strip().strip("“”\"").strip(), rep.raw.get("thinking_observed")
            same = text == raw["text"].strip()
            attempts.append({"text": text, "temperature": temp, "identical": same,
                             "banned_hits": P.banned_hits(text)})
            if text and not same and not P.banned_hits(text):
                break
        stim = {"item_id": raw["item_id"], "rendering": raw["rendering"], "channel": channel,
                "key": P.stimulus_key(raw["item_id"], raw["rendering"], channel),
                "text": attempts[-1]["text"], "source_message": raw["text"],
                "error": None, "thinking_observed": obs, "model": pc["model"],
                "relay_attempts": attempts}
        it = by_id[raw["item_id"]]
        opt_a, opt_b, _ = options(it, 0)
        reply, err = "", None
        for wait in (0, 10, 30, 60, 120):
            time.sleep(wait)
            try:
                reply = gem.chat([{"role": "user", "content": P.GATE_PROMPT.format(
                    **it, opt_a=opt_a, opt_b=opt_b, text=stim["text"])}],
                    temperature=gc["temperature"], reasoning=gc["reasoning"]).text
                err = None
                break
            except Exception as exc:  # noqa: BLE001  logged as data, never dropped
                err = repr(exc)[:300]
        return {"stimulus": stim, "gate": {"key": stim["key"], "reply": reply, "error": err,
                                           "model": gc["model"]}}

    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(one, raws))


@app.local_entrypoint()
def main(channel: str = "sum_short") -> None:
    """--channel takes a comma-separated list; the channels run in parallel on Modal."""
    from src import prompts as P
    from src.episode import load_items
    from src.run_meta import load_cfg

    chans = channel.split(",")
    assert all(c in P.RELAY_SYSTEM for c in chans), chans
    cfg = load_cfg()
    path = ROOT / "data/stimuli/stimuli.jsonl"
    lines = [json.loads(l) for l in path.read_text().splitlines()]
    have = {r["key"] for r in lines[1:]}
    todo = {c: [r for r in lines[1:] if r["channel"] == "raw"
                and P.stimulus_key(r["item_id"], r["rendering"], c) not in have] for c in chans}
    for c in chans:
        print(f"channel {c}: {len(todo[c])} raw messages to relay")
    url = modal.Function.from_name(cfg["paraphraser"]["app"], "serve").get_web_url().rstrip("/") + "/v1"
    items = load_items()
    outs = list(add.starmap([(todo[c], items, cfg, url, c) for c in chans if todo[c]]))
    res = [x for o in outs for x in o]
    lines[0]["_meta"].setdefault("added_channels", []).append(
        {"script": "scripts/modal_add_relay.py", "channels": chans, "n": len(res),
         "timestamp": datetime.now(timezone.utc).isoformat()})
    with path.open("w") as fh:
        for r in lines + [x["stimulus"] for x in res]:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (ROOT / "data/stimuli/gate.jsonl").open("a") as fh:
        for r in res:
            fh.write(json.dumps(r["gate"], ensure_ascii=False) + "\n")
    for c in chans:
        rc = [x["stimulus"] for x in res if x["stimulus"]["channel"] == c]
        bad = [s["key"] for s in rc if s["relay_attempts"][-1]["identical"] or s["relay_attempts"][-1]["banned_hits"]]
        print(f"{c}: added {len(rc)}; still identical or banned: {bad}")
