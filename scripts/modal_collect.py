"""Collect episodes on Modal. Nothing calls a model on the laptop.

    .venv/bin/modal run scripts/modal_collect.py --dry-run
    .venv/bin/modal run scripts/modal_collect.py --smoke 20
    .venv/bin/modal run --detach scripts/modal_collect.py --confirm

The laptop asserts the controls, prices the run and writes the stream to
data/episodes/. Each container also appends to the `vi-paraphrase-episodes`
volume, so a dropped stream costs the terminal, not the run.
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

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("requests>=2.31", "openai>=1.40", "python-dotenv>=1.0", "pyyaml>=6.0")
    .add_local_dir(ROOT / "src", f"{REMOTE}/src", ignore=["**/__pycache__"])
    .add_local_dir(ROOT / "configs", f"{REMOTE}/configs")
    .add_local_dir(ROOT / "data" / "items", f"{REMOTE}/data/items")
    .add_local_dir(ROOT / "data" / "stimuli", f"{REMOTE}/data/stimuli")
    .add_local_dir(ROOT / "data" / "stimuli_workflow", f"{REMOTE}/data/stimuli_workflow")
    .add_local_dir(ROOT / "data" / "stimuli_ext", f"{REMOTE}/data/stimuli_ext")
)
# Language arm (2026-10-28, proposed): mounted once its stimuli are frozen.
for _d in ("stimuli_en", "stimuli_zh"):
    if (ROOT / "data" / _d).exists():
        image = image.add_local_dir(ROOT / "data" / _d, f"{REMOTE}/data/{_d}")
vol = modal.Volume.from_name("vi-paraphrase-episodes", create_if_missing=True)
app = modal.App("vi-paraphrase-collect")
_STATE: dict[str, Any] = {}


@app.function(image=image, secrets=[modal.Secret.from_name("collusion-keys"),
                                    modal.Secret.from_name("vllm-key")],
              volumes={"/episodes": vol}, cpu=0.5, memory=1024, timeout=60 * 15,
              max_containers=CONTAINERS, retries=0)
@modal.concurrent(max_inputs=PER_CONTAINER)
def run_one(job: dict, *, cfg: dict, agent: str, base_url: str | None, meta: dict,
            run_id: str, item_set: str = "market") -> dict:
    sys.path.insert(0, REMOTE)
    from src import prompts as P
    from src.clients import get_client
    from src.episode import load_items, load_stimuli, run_episode
    from src.schema import validate_episode

    if "items" not in _STATE:
        items, stimuli = load_items(item_set), load_stimuli(item_set)
        P.assert_prompt_controls(items, stimuli)  # again, inside the container
        a = cfg["agents"][agent]
        if a["client"] == "vllm":
            from src.clients import VLLMClient
            client = VLLMClient(model=a["model"], base_url=base_url, max_tokens=a["max_tokens"])
        else:
            client = get_client(a["client"], model=a["model"])
        if not client.supports_reasoning_control:
            raise SystemExit("control 1: agent client has no per-call reasoning switch")
        _STATE.update(items=items, stimuli=stimuli, client=client, tag=uuid.uuid4().hex[:10])
    item = _STATE["items"][job["item_index"]]
    rec = run_episode(_STATE["client"], item, job, _STATE["stimuli"], cfg, meta)
    problems = validate_episode(rec)
    if problems:
        raise RuntimeError(f"schema failure on {rec['episode_id']}: {problems}")
    d = Path("/episodes") / run_id
    d.mkdir(parents=True, exist_ok=True)
    with (d / f"{_STATE['tag']}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    vol.commit()
    return rec


@app.local_entrypoint()
def main(agent: str = "gemini", smoke: int = 0, confirm: bool = False, dry_run: bool = False,
         resume: bool = False, items: str = "market", channels: str = "") -> None:
    """--channels limits the run to those channels and writes to its own file
    (`summary_episodes_*` for the summary channels), so earlier files stay as reported."""
    from src import prompts as P
    from src.episode import build_jobs, episode_id, load_items, load_stimuli
    from src.run_meta import config_hash, estimate_episode_cost, git_commit, load_cfg
    from src.schema import validate_episode

    item_set = items
    cfg = load_cfg()
    items, stimuli = load_items(item_set), load_stimuli(item_set)
    if stimuli is None:
        raise SystemExit("no data/stimuli/stimuli.jsonl: run scripts/modal_stimuli.py first")
    report = P.assert_prompt_controls(items, stimuli)
    jobs = build_jobs(items, cfg["k"], smoke)
    if channels:
        keep = set(P.SUMMARIES) if channels == "summaries" else set(channels.split(","))
        jobs = [j for j in jobs if j["channel"] in keep]
    acfg = cfg["agents"][agent]
    prefix = "" if item_set == "market" else f"{item_set}_"
    if channels:
        prefix = ("summary_" if channels == "summaries" else "channels_") + prefix
    out = ROOT / "data" / "episodes" / (f"{prefix}smoke_{len(jobs)}_{agent}.jsonl" if smoke
                                        else f"{prefix}episodes_{agent}.jsonl")
    done: set[str] = set()
    if resume and out.exists():
        for line in out.read_text().splitlines():
            rec = json.loads(line)
            if "_meta" not in rec and rec.get("error") is None:
                done.add(rec["episode_id"])
        jobs = [j for j in jobs if episode_id(items[j["item_index"]], j) not in done]

    chash, commit = config_hash(cfg), git_commit()
    cost, billed = estimate_episode_cost(cfg, agent, len(jobs))
    base_url = None
    if acfg["client"] == "vllm":
        base_url = modal.Function.from_name(acfg["app"], "serve").get_web_url().rstrip("/") + "/v1"
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    meta = {"config_hash": chash, "git_commit": commit, "agent": agent, "model": acfg["model"],
            "item_set": item_set,
            "temperature": cfg["temperature"], "run_id": run_id}

    print(f"agent         {agent} ({acfg['model']})  reasoning={cfg['reasoning']}  T={cfg['temperature']}")
    print(f"item set      {item_set}")
    print(f"items         {len(items)}   episodes {len(jobs)}" + (f"  (resume: {len(done)} done)" if resume else ""))
    print(f"CONTROLS      {report}")
    print(f"config_hash   {chash}   git {commit}")
    print(f"ESTIMATED COST  ${cost:,.2f}  ({billed}; Modal CPU containers on top)")
    print(f"output        {out}")
    if commit.endswith("-dirty") or commit == "no-commit":
        print("WARNING: src/scripts/configs not committed; records will say so.")
    if dry_run:
        print("--dry-run: no call made.")
        return
    if len(jobs) > 20 and not confirm:
        raise SystemExit("more than 20 episodes: re-run with --confirm (cost guard)")

    out.parent.mkdir(parents=True, exist_ok=True)
    n, failed = 0, []
    with out.open("a" if resume else "w") as fh:
        fh.write(json.dumps({"_meta": {**meta, "n_jobs": len(jobs), "est_cost": cost,
                                       "controls": report}}) + "\n")
        for res in run_one.map(jobs, order_outputs=False, return_exceptions=True,
                               kwargs={"cfg": cfg, "agent": agent, "base_url": base_url,
                                       "meta": meta, "run_id": run_id, "item_set": item_set}):
            if isinstance(res, Exception):
                failed.append(repr(res)[:200])
                continue
            assert not validate_episode(res)
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            fh.flush()
            n += 1
    print(f"\nwrote {n} episodes to {out}; {len(failed)} inputs failed (gaps, use --resume)")
    for f in failed[:5]:
        print("  ", f)
    print("COMMIT data/episodes/ NOW.")
