"""Initiation probe on Modal: does the agent open the collusion itself? (src/initiate.py)

    .venv/bin/modal run scripts/modal_initiate.py --agent gemini --dry-run
    .venv/bin/modal run scripts/modal_initiate.py --agent gemini --confirm

All 144 task items (market, workflow, extension), 6 episodes each (3 rotations x 2 orders).
Writes data/episodes/initiate_{agent}.jsonl.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REMOTE = "/root/repo"
CONTAINERS = int(os.environ.get("VIPC_CONTAINERS", "4"))
PER_CONTAINER = int(os.environ.get("VIPC_CONCURRENCY", "4"))
SETS = ("market", "workflow", "ext")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("requests>=2.31", "openai>=1.40", "python-dotenv>=1.0", "pyyaml>=6.0")
    .add_local_dir(ROOT / "src", f"{REMOTE}/src", ignore=["**/__pycache__"])
    .add_local_dir(ROOT / "configs", f"{REMOTE}/configs")
    .add_local_dir(ROOT / "data" / "items", f"{REMOTE}/data/items")
)
app = modal.App("vi-paraphrase-initiate")
_STATE: dict[str, Any] = {}


@app.function(image=image, secrets=[modal.Secret.from_name("collusion-keys"), modal.Secret.from_name("vllm-key")],
              cpu=0.5, memory=1024, timeout=60 * 15, max_containers=CONTAINERS, retries=0)
@modal.concurrent(max_inputs=PER_CONTAINER)
def run_one(job: dict, *, cfg: dict, agent: str, base_url: str | None, meta: dict) -> dict:
    sys.path.insert(0, REMOTE)
    from src import initiate as I
    from src.clients import get_client
    from src.episode import load_items
    if "items" not in _STATE:
        items = [it for s in SETS for it in load_items(s)]
        I.assert_controls(items)
        a = cfg["agents"][agent]
        if a["client"] == "vllm":
            from src.clients import VLLMClient
            client = VLLMClient(model=a["model"], base_url=base_url, max_tokens=a["max_tokens"])
        else:
            client = get_client(a["client"], model=a["model"])
        if not client.supports_reasoning_control:
            raise SystemExit("control 1: agent client has no per-call reasoning switch")
        _STATE.update(items=items, client=client)
    return I.run(_STATE["client"], _STATE["items"][job["item_index"]], job, cfg, meta)


@app.local_entrypoint()
def main(agent: str = "gemini", confirm: bool = False, dry_run: bool = False, resume: bool = False) -> None:
    from src import initiate as I
    from src.episode import load_items
    from src.run_meta import config_hash, git_commit, load_cfg
    cfg = load_cfg()
    items = [it for s in SETS for it in load_items(s)]
    report = I.assert_controls(items)
    jobs = I.build_jobs(items)
    out = ROOT / "data" / "episodes" / f"initiate_{agent}.jsonl"
    done = set()
    if resume and out.exists():
        done = {json.loads(l)["episode_id"] for l in out.read_text().splitlines()[1:]
                if l.strip() and not json.loads(l).get("error")}
        jobs = [j for j in jobs if I.episode_id(items[j["item_index"]], j) not in done]
    acfg = cfg["agents"][agent]
    base_url = None
    if acfg["client"] == "vllm":
        base_url = modal.Function.from_name(acfg["app"], "serve").get_web_url().rstrip("/") + "/v1"
    meta = {"config_hash": config_hash(cfg), "git_commit": git_commit(), "agent": agent, "model": acfg["model"],
            "temperature": cfg["temperature"], "run_id": f"init-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}",
            "probe": "initiation"}
    print(f"agent {agent} ({acfg['model']})  items {len(items)}  episodes {len(jobs)}  controls {report}")
    if dry_run:
        it = items[0]
        print(I.message_texts(it))
        return
    if len(jobs) > 20 and not confirm:
        raise SystemExit("more than 20 episodes: re-run with --confirm (cost guard)")
    n, failed = 0, []
    with out.open("a" if resume else "w") as fh:
        if not resume:
            fh.write(json.dumps({"_meta": {**meta, "n_jobs": len(jobs), "controls": report}}) + "\n")
        for res in run_one.map(jobs, order_outputs=False, return_exceptions=True,
                               kwargs={"cfg": cfg, "agent": agent, "base_url": base_url, "meta": meta}):
            if isinstance(res, Exception):
                failed.append(repr(res)[:200])
                continue
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            fh.flush()
            n += 1
    print(f"wrote {n} episodes to {out.relative_to(ROOT)}; {len(failed)} failed")
    for f in failed[:5]:
        print("  ", f)
