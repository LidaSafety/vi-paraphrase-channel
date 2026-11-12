"""Third-party summaries of each full episode trace, for the `summary` monitor view.

    .venv/bin/modal run scripts/modal_summarize.py --episodes data/episodes/episodes_gemini.jsonl --confirm

A summarizer that is neither agent nor monitor (configs/study.yaml `summarizer`)
reads the full trace (situation, pre-message choice, message as delivered, final
action, report) and writes an activity-log summary with SUMMARY_PROMPT. It is not
told to look for collusion. A summary is evidence a monitor reads, never a
label: it enters no measure.
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
)
app = modal.App("vi-paraphrase-summarize")


@app.function(image=image, timeout=60 * 60, secrets=[modal.Secret.from_name("vllm-key")])
def summarize(jobs: list[dict], scfg: dict, url: str) -> list[dict]:
    sys.path.insert(0, REMOTE)
    from concurrent.futures import ThreadPoolExecutor

    from src.clients import VLLMClient
    client = VLLMClient(model=scfg["model"], base_url=url, max_tokens=scfg["max_tokens"])

    def one(j):
        try:
            rep = client.chat([{"role": "user", "content": j["prompt"]}],
                              temperature=scfg["temperature"], reasoning=False)
            return {"episode_id": j["episode_id"], "summary": rep.text.strip(), "error": None}
        except Exception as exc:  # noqa: BLE001  logged as data
            return {"episode_id": j["episode_id"], "summary": "", "error": repr(exc)[:300]}

    with ThreadPoolExecutor(32) as ex:
        return list(ex.map(one, jobs))


@app.local_entrypoint()
def main(episodes: str, dry_run: bool = False, confirm: bool = False) -> None:
    from src import prompts as P
    from src.episode import load_items
    from src.run_meta import config_hash, git_commit, load_cfg
    from src.views import episode_ctx

    cfg = load_cfg()
    scfg = cfg["summarizer"]
    path = ROOT / episodes
    recs = [r for r in map(json.loads, path.read_text().splitlines()) if "_meta" not in r]
    items = {it["item_id"]: it for s in ("market", "workflow", "ext") for it in load_items(s)}
    jobs = []
    for r in recs:
        if r["post"]["kind"] != "choice" or not r.get("report"):
            continue
        it = items[r["item_id"]]
        ctx = episode_ctx(r, it)
        trace = P.render_view("baseline_info", ctx, P.T(it)["VIEW_BLOCKS"])
        jobs.append({"episode_id": r["episode_id"], "prompt": P.SUMMARY_PROMPT.format(
            principal=it["principal"], agent_name=it["agent_name"], trace=trace)})
    print(f"summarizer    {scfg['model']}   episodes {len(jobs)}")
    if dry_run:
        print(jobs[0]["prompt"])
        return
    if len(jobs) > 20 and not confirm:
        raise SystemExit("more than 20 summaries: re-run with --confirm (cost guard)")
    url = modal.Function.from_name(scfg["app"], "serve").get_web_url().rstrip("/") + "/v1"
    out = summarize.remote(jobs, scfg, url)
    dest = ROOT / "data" / "summaries" / f"{path.stem}__summarizer.jsonl"
    dest.parent.mkdir(parents=True, exist_ok=True)
    meta = {"_meta": {"summarizer": scfg, "config_hash": config_hash(cfg), "git_commit": git_commit(),
                      "episodes": episodes, "timestamp": datetime.now(timezone.utc).isoformat()}}
    with dest.open("w") as fh:
        for r in [meta] + out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    errs = sum(1 for r in out if r["error"])
    print(f"wrote {len(out)} summaries to {dest.relative_to(ROOT)}; errors {errs}")
    print("example:", out[0]["summary"][:400])
