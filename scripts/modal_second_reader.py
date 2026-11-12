"""LLM re-readers of the stimulus gate. NOT human validation.

    .venv/bin/modal run scripts/modal_second_reader.py --reader gpt
    .venv/bin/modal run scripts/modal_second_reader.py --reader gemma

The same GATE_PROMPT the Gemini gate answered, put to an OpenAI model, on every
frozen stimulus (720 texts). Raw replies go to data/stimuli/reader_<name>.jsonl;
`scripts/score_gate.py` scores both readers in code and reports agreement.
Decided by the human on 2026-10-25 in place of a human sample (CLAUDE.md, 9).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REMOTE = "/root/repo"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("requests>=2.31", "openai>=1.40", "python-dotenv>=1.0", "pyyaml>=6.0",
                 "anthropic>=1.0")
    .add_local_dir(ROOT / "src", f"{REMOTE}/src", ignore=["**/__pycache__"])
)
app = modal.App("vi-paraphrase-second-reader")

# The Anthropic key lives in its own secret, created by the human. It is mounted
# only when asked for (VIPC_ANTHROPIC=1), so the gpt and gemma readers still run
# on a workspace that does not have it.
SECRETS = [modal.Secret.from_name("collusion-keys"), modal.Secret.from_name("vllm-key")]
if os.environ.get("VIPC_ANTHROPIC") == "1":
    SECRETS.append(modal.Secret.from_name("anthropic-key"))


@app.function(image=image, timeout=60 * 60, secrets=SECRETS)
def read(jobs: list[dict], rc: dict, base_url: str | None) -> list[dict]:
    sys.path.insert(0, REMOTE)
    return _read(jobs, rc, base_url)


def _read(jobs: list[dict], rc: dict, base_url: str | None) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor

    from src.clients import get_client

    if rc["client"] == "vllm":
        from src.clients import VLLMClient
        client = VLLMClient(model=rc["model"], base_url=base_url, max_tokens=rc["max_tokens"])
    elif rc["client"] == "anthropic":
        from src.anthropic_client import AnthropicClient
        client = AnthropicClient(model=rc["model"], effort=rc["effort"])
    else:
        client = get_client(rc["client"], model=rc["model"])

    def one(j):
        try:
            rep = client.chat([{"role": "user", "content": j["prompt"]}],
                              temperature=rc["temperature"], reasoning=rc.get("reasoning", False))
            return {"key": j["key"], "reply": rep.text, "error": None,
                    "stop_reason": (rep.raw or {}).get("stop_reason"),
                    "usage": (rep.raw or {}).get("usage")}
        except Exception as exc:  # noqa: BLE001
            return {"key": j["key"], "reply": "", "error": repr(exc)[:300]}

    with ThreadPoolExecutor(16) as ex:
        return list(ex.map(one, jobs))


@app.local_entrypoint()
def main(reader: str = "gpt", harmful_only: bool = False, limit: int = 0,
         local_env: str = "", append: bool = False) -> None:
    """--append reads only stimuli not yet in reader_<name>.jsonl and appends to it
    (used when new channels were added after the reader first ran)."""
    from src import prompts as P
    from src.episode import load_items, load_stimuli, options
    from src.run_meta import config_hash, git_commit, load_cfg

    cfg = load_cfg()
    rc = cfg["readers"][reader]
    items = {it["item_id"]: it for it in load_items()}
    stim = load_stimuli()
    jobs = []
    for key, s in stim.items():
        it = items[s["item_id"]]
        if harmful_only and it["item_class"] != "harmful":
            continue
        opt_a, opt_b, _ = options(it, 0)
        jobs.append({"key": key, "prompt": P.GATE_PROMPT.format(**it, opt_a=opt_a, opt_b=opt_b,
                                                                 text=s["text"])})
    dest = ROOT / (f"data/stimuli/reader_{reader}.jsonl" if not limit
                   else f"data/stimuli/smoke_reader_{reader}_{limit}.jsonl")
    if append:
        have = {json.loads(l).get("key") for l in dest.read_text().splitlines()}
        jobs = [j for j in jobs if j["key"] not in have]
    if limit:
        jobs = jobs[:limit]
    print(f"second reader {rc['model']} on {len(jobs)} stimuli")
    base_url = None
    if rc["client"] == "vllm":
        base_url = modal.Function.from_name(rc["app"], "serve").get_web_url().rstrip("/") + "/v1"
    if local_env:
        # API-only reader run from the laptop: the key is read from the given .env
        # into this process's environment, never printed and never written out.
        from dotenv import dotenv_values
        os.environ.update({k: v for k, v in dotenv_values(local_env).items()
                           if k.endswith("_API_KEY") and v})
        out = _read(jobs, rc, base_url)
    else:
        out = read.remote(jobs, rc, base_url)
    meta = {"_meta": {"reader": rc, "config_hash": config_hash(cfg), "git_commit": git_commit(),
                      "timestamp": datetime.now(timezone.utc).isoformat(),
                      "note": "LLM second reader, not human validation"
                              + ("; appended for new channels" if append else "")}}
    with dest.open("a" if append else "w") as fh:
        if not append:
            fh.write(json.dumps(meta) + "\n")
        for o in out:
            fh.write(json.dumps({**o, "model": rc["model"]}, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)} replies, {sum(1 for o in out if o['error'])} errors -> {dest}")
