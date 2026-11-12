"""Score collected episodes with the platform monitors, at four nested views.

    .venv/bin/modal run scripts/modal_monitor.py --episodes data/episodes/smoke_24.jsonl --dry-run
    .venv/bin/modal run scripts/modal_monitor.py --episodes data/episodes/episodes.jsonl --confirm

Offline: the agent's decisions are already fixed, so the views only change
what the monitor reads. `raw` is scored only on relayed channels; on the raw
channel it would repeat `delivered` byte for byte.

Episodes with an unparsed or refused final choice are not scored (there is no
action to show) and are counted in the header.

Proposed 2026-10-28 (docs/execution-plan.md), nothing run yet:
    --question accept    the v2 question (one actor, one act), views with the action only
    --monitor-lang en    score with the English monitor frame (language arm); `match` (default)
                         uses each episode's own language, so Vietnamese runs are unchanged
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
app = modal.App("vi-paraphrase-monitor")


@app.function(image=image, timeout=60 * 60, cpu=1.0, memory=2048,
              secrets=[modal.Secret.from_name("collusion-keys"),
                       modal.Secret.from_name("vllm-key")])
def score(jobs: list[dict], mcfg: dict, qwen_url: str | None) -> list[dict]:
    sys.path.insert(0, REMOTE)
    return _score(jobs, mcfg, qwen_url)


def _score(jobs: list[dict], mcfg: dict, qwen_url: str | None) -> list[dict]:
    # each job carries its own system prompt: market and workflow monitors differ
    from concurrent.futures import ThreadPoolExecutor

    from src import prompts as P
    from src.clients import GeminiClient, VLLMClient
    from src.scoring import parse_score, parse_verdict

    if mcfg.get("app"):
        client = VLLMClient(model=mcfg["model"], base_url=qwen_url, max_tokens=mcfg["max_tokens"],
                            template_kwargs=mcfg.get("chat_template_kwargs", True))
    elif mcfg.get("client") == "anthropic":
        from src.anthropic_client import AnthropicClient
        client = AnthropicClient(model=mcfg["model"], effort=mcfg["effort"], max_tokens=mcfg["max_tokens"])
    else:
        client = GeminiClient(model=mcfg["model"])

    def one(j):
        # the user turn is built locally (question version and monitor language), see main()
        msgs = [{"role": "system", "content": j.get("system", P.MONITOR_SYSTEM)},
                {"role": "user", "content": j["user"]}]
        try:
            rep = client.chat(msgs, temperature=mcfg["temperature"], reasoning=mcfg["reasoning"])
            reply, err = rep.text, None
            if (rep.raw or {}).get("stop_reason") == "refusal":
                err = "refusal"
        except Exception as exc:  # noqa: BLE001
            reply, err = "", repr(exc)[:300]
        if j.get("question") == "score":
            score, kind = parse_score(reply)
            return {**{k: j[k] for k in ("episode_id", "view")}, "reply": reply,
                    "verdict": None, "score": score, "kind": kind, "error": err}
        v, kind = parse_verdict(reply)
        return {**{k: j[k] for k in ("episode_id", "view")}, "reply": reply,
                "verdict": v, "kind": kind, "error": err}

    with ThreadPoolExecutor(48 if mcfg.get("app") else 16) as ex:
        return list(ex.map(one, jobs))


@app.local_entrypoint()
def main(episodes: str, monitor: str = "gemini", views: str = "nested", dry_run: bool = False,
         confirm: bool = False, local_env: str = "", max_tokens: int = 0,
         question: str = "original", monitor_lang: str = "match", channels: str = "") -> None:
    from src import prompts as P
    from src.run_meta import config_hash, git_commit, load_cfg
    from src.schema import validate_episode, validate_verdict

    if question not in ("original", "accept", "score") or monitor_lang not in ("match", "vi", "en", "zh"):
        raise SystemExit("--question original|accept|score, --monitor-lang match|vi|en|zh")
    if question in ("accept", "score") and views in ("extra", "standard", "summary"):
        raise SystemExit(f"--question accept: '{views}' cannot take it ('standard' keeps its own rule; "
                         "'extra' and 'summary' do not show the action)")
    cfg = load_cfg()
    mcfg = dict(cfg["monitors"][monitor])
    if max_tokens:
        # Logged override (docs/execution-plan.md): Aya opens the standard view with reasoning and a
        # 16-token cap cut it before the verdict. Temperature 0, so a longer cap only lets it finish.
        mcfg["max_tokens"] = max_tokens
    path = ROOT / episodes
    recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    recs = [r for r in recs if "_meta" not in r]
    for r in recs:
        bad = validate_episode(r)
        if bad:
            raise SystemExit(f"{r.get('episode_id')}: {bad}")
    from src.episode import load_items
    from src.episode import items_path
    sets = ("market", "workflow", "ext") + tuple(s for s in ("market_en", "market_zh") if items_path(s).exists())
    items = {it["item_id"]: it for s in sets for it in load_items(s)}
    scorable = [r for r in recs if r["post"]["kind"] == "choice" and r.get("report")]
    if channels:  # e.g. "raw" for the language arm's Vietnamese comparison
        scorable = [r for r in scorable if r["channel"] in channels.split(",")]
    from src.views import episode_ctx, load_summaries, turn1_by_family, turn1_by_item
    turn1, summaries = turn1_by_item(recs), load_summaries(path)
    fam = turn1_by_family(recs, items)
    if views == "summary" and not summaries:
        raise SystemExit(f"no summaries for {path.name}: run scripts/modal_summarize.py first")
    jobs = []
    for r in scorable:
        it = items[r["item_id"]]
        mlang = P.lang(it) if monitor_lang == "match" else monitor_lang
        if mlang == P.lang(it):
            tpl = P.T(it)
        elif it.get("setting", "market") in ("market", "market_en", "market_zh"):
            # the other language's frame; the item text stays in the episode's own language
            tpl = P.SETTINGS[P.MARKET_BY_LANG[mlang]]
        else:
            raise SystemExit(f"{r['episode_id']}: no {mlang} monitor frame for setting {it.get('setting')}")
        ctx = episode_ctx(r, it, turn1, summaries, fam, lang=mlang)
        if views == "summary" and not ctx["summary"]:
            continue
        chosen = {"nested": P.VIEWS, "extra": ("report_only", "message_only"),
                  "all": P.VIEWS + ("report_only", "message_only"), "standard": ("standard",),
                  "baseline_info": ("baseline_info",), "pop_baseline": ("pop_baseline",),
                  "summary": ("summary",), "family_baseline": ("family_baseline",),
                  "channel": ("delivered", "raw"), "delivered": ("delivered",)}[views]
        if question in ("accept", "score"):
            chosen = tuple(v for v in chosen if v in P.ACCEPT_VIEWS)
        for v in chosen:
            if v == "raw" and r["channel"] == "raw":
                continue
            view_text = P.render_view(v, ctx, tpl["VIEW_BLOCKS"])
            if v == "standard":
                if mlang != "vi":
                    raise SystemExit("the standard view has no English rule yet")
                user = P.STANDARD_USER.format(view=view_text)
            else:
                user = P.MONITOR_QUESTIONS[(mlang, question)].format(
                    view=view_text, agent_name=it["agent_name"], counterpart_name=it["counterpart_name"])
            jobs.append({"episode_id": r["episode_id"], "view": v, "system": tpl["MONITOR_SYSTEM"],
                         "view_text": view_text, "user": user, "question": question})
    print(f"monitor       {monitor} ({mcfg['model']})")
    print(f"episodes      {len(recs)}   scorable {len(scorable)}   not scorable {len(recs) - len(scorable)}")
    print(f"question      {question}   monitor language {monitor_lang}")
    print(f"calls         {len(jobs)}")
    if dry_run:
        print("--dry-run: no call made. First view:\n")
        print((jobs[0]["system"] + "\n\n" + jobs[0]["user"]) if jobs else "(none)")
        return
    if len(jobs) > 200 and not confirm:
        raise SystemExit("more than 200 monitor calls: re-run with --confirm (cost guard)")
    qwen_url = None
    if mcfg.get("app"):
        qwen_url = modal.Function.from_name(mcfg["app"], "serve").get_web_url().rstrip("/") + "/v1"
    if local_env:
        # API-only monitor run from the laptop (the Claude key is not a Modal secret):
        # the key is read from the given .env into this process, never printed.
        import os

        from dotenv import dotenv_values
        os.environ.update({k: v for k, v in dotenv_values(local_env).items() if k.endswith("_API_KEY") and v})
        out = _score(jobs, mcfg, qwen_url)
    else:
        out = score.remote(jobs, mcfg, qwen_url)
    stamp = {"monitor": monitor, "model": mcfg["model"], "max_tokens": mcfg.get("max_tokens"), "config_hash": config_hash(cfg),
             "question": question, "monitor_lang": monitor_lang,
             "git_commit": git_commit(), "timestamp": datetime.now(timezone.utc).isoformat()}
    suffix = {"nested": "", "extra": "--extra", "all": "", "standard": "--standard",
              "baseline_info": "--baseline_info", "pop_baseline": "--pop_baseline",
              "summary": "--summary", "family_baseline": "--family_baseline", "channel": "",
              "delivered": "--delivered"}[views]
    suffix += {"accept": "--accept", "score": "--score"}.get(question, "") + (
        f"--mlang-{monitor_lang}" if monitor_lang != "match" else "") + (
        f"--ch-{channels.replace(',', '-')}" if channels else "")
    dest = ROOT / "data" / "monitor" / f"{path.stem}__{monitor}{suffix}.jsonl"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w") as fh:
        fh.write(json.dumps({"_meta": {**stamp, "source": episodes}}) + "\n")
        for o in out:
            rec = {**o, **stamp}
            assert not validate_verdict(rec), validate_verdict(rec)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    kinds = {}
    for o in out:
        kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
    print(f"wrote {len(out)} verdicts to {dest}   kinds {kinds}")
    print("COMMIT data/monitor/ NOW.")
