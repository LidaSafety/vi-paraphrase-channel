"""Stimulus-level robustness for the summary styles. Never used in an episode.

    .venv/bin/modal run scripts/modal_summary_robust.py --source resample   # Qwen3-8B again, T=0.7
    .venv/bin/modal run scripts/modal_summary_robust.py --source gemma      # Gemma-3-27B, T=0

For every harmful raw message, each summary style is written once more, either a
second sample from the same relay model or by a different, larger model, and
gated with the same Gemini gate. The question is whether a style's loss of the
invitation (gate verdict) repeats across samples and summarizers. Output:
data/stimuli/robust_summaries_<source>.jsonl.
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
)
app = modal.App("vi-paraphrase-summary-robust")
SOURCES = {"resample": ("paraphraser", 0.7), "gemma": ("summarizer", 0.0)}


@app.function(image=image, timeout=60 * 40, secrets=[modal.Secret.from_name("collusion-keys"),
                                                      modal.Secret.from_name("vllm-key")])
def run(jobs: list[dict], model: str, url: str, temperature: float, max_tokens: int, gc: dict) -> list[dict]:
    sys.path.insert(0, REMOTE)
    from src import prompts as P
    from src.clients import GeminiClient, VLLMClient
    llm = VLLMClient(model=model, base_url=url, max_tokens=max_tokens)
    gem = GeminiClient(model=gc["model"])

    def one(j):
        try:
            text = llm.chat([{"role": "system", "content": P.RELAY_SYSTEM[j["channel"]]},
                             {"role": "user", "content": P.RELAY_USER.format(message=j["source"])}],
                            temperature=temperature, reasoning=False).text.strip().strip("“”\"").strip()
            err = None
        except Exception as exc:  # noqa: BLE001
            text, err = "", repr(exc)[:300]
        reply, gerr = "", None
        if text:
            for wait in (0, 10, 30, 60, 120):
                time.sleep(wait)
                try:
                    reply = gem.chat([{"role": "user", "content": j["gate_prompt"].replace("<<TEXT>>", text)}],
                                     temperature=gc["temperature"], reasoning=gc["reasoning"]).text
                    gerr = None
                    break
                except Exception as exc:  # noqa: BLE001
                    gerr = repr(exc)[:300]
        return {**{k: j[k] for k in ("key", "item_id", "rendering", "channel")}, "text": text,
                "identical": text == j["source"].strip(), "error": err, "gate_reply": reply, "gate_error": gerr}

    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(one, jobs))


@app.local_entrypoint()
def main(source: str = "resample") -> None:
    from src import prompts as P
    from src.episode import load_items, load_stimuli, options
    from src.run_meta import git_commit, load_cfg

    cfg = load_cfg()
    role, temp = SOURCES[source]
    mc = cfg[role]
    items = {it["item_id"]: it for it in load_items()}
    jobs = []
    for s in load_stimuli().values():
        it = items[s["item_id"]]
        if s["channel"] != "raw" or it["item_class"] != "harmful":
            continue
        opt_a, opt_b, _ = options(it, 0)
        for ch in P.SUMMARIES:
            jobs.append({"key": P.stimulus_key(s["item_id"], s["rendering"], ch), "item_id": s["item_id"],
                         "rendering": s["rendering"], "channel": ch, "source": s["text"],
                         "gate_prompt": P.GATE_PROMPT.format(**it, opt_a=opt_a, opt_b=opt_b, text="<<TEXT>>")})
    print(f"{source}: {mc['model']} T={temp}  {len(jobs)} summaries")
    url = modal.Function.from_name(mc["app"], "serve").get_web_url().rstrip("/") + "/v1"
    out = run.remote(jobs, mc["model"], url, temp, mc.get("max_tokens", 400), cfg["gate"])
    dest = ROOT / "data" / "stimuli" / f"robust_summaries_{source}.jsonl"
    with dest.open("w") as fh:
        fh.write(json.dumps({"_meta": {"source": source, "model": mc["model"], "temperature": temp,
                                       "gate": cfg["gate"], "git_commit": git_commit(),
                                       "timestamp": datetime.now(timezone.utc).isoformat()}}) + "\n")
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)}; errors {sum(1 for o in out if o['error'] or o['gate_error'])}; "
          f"identical {sum(o['identical'] for o in out)}")
