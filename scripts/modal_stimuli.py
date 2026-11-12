"""Render, relay and gate every rival message, once, before any episode.

    .venv/bin/modal run scripts/modal_stimuli.py --dry-run
    .venv/bin/modal run scripts/modal_stimuli.py

Three stages, all in one container, all model calls on Modal:
  1. RENDER  Gemini writes each item's message in each of the four renderings.
             A message with a banned phrase or bad JSON is re-rendered, up to
             three attempts; every attempt is logged.
  2. RELAY   Qwen3-8B (vllm-qwen3-8b-ep) rewrites every raw message twice:
             `paraphrased` (new words, same tone) and `neutralized` (platform
             notice, social context removed). Thinking off, temperature 0.
  3. GATE    Gemini reads each text beside the two options, without being told
             which is the arrangement, and says which way it pushes (A/B/KHÔNG).
             A manipulation check on the stimulus, never an episode measure.

Writes data/stimuli/stimuli.jsonl and data/stimuli/gate.jsonl. Commit both.
Never regenerate mid-study.
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

app = modal.App("vi-paraphrase-stimuli")


@app.function(image=image, timeout=60 * 45, cpu=1.0, memory=2048,
              secrets=[modal.Secret.from_name("collusion-keys"),
                       modal.Secret.from_name("vllm-key")])
def build(items: list[dict], cfg: dict, qwen_url: str) -> dict:
    sys.path.insert(0, REMOTE)
    import re
    from concurrent.futures import ThreadPoolExecutor

    from src import prompts as P
    from src.clients import GeminiClient, VLLMClient
    from src.episode import options
    from src.scoring import classify

    rc, pc, gc = cfg["renderer"], cfg["paraphraser"], cfg["gate"]
    gem_render = GeminiClient(model=rc["model"])
    gem_gate = GeminiClient(model=gc["model"])
    qwen = VLLMClient(model=pc["model"], base_url=qwen_url, max_tokens=pc["max_tokens"])

    def render(job):
        it, r = job
        tpl = P.T(it)
        prompt = tpl["RENDER_PROMPT"].format(**it, style=tpl.get("RENDER_STYLES", P.RENDER_STYLES)[r])
        attempts = []
        for _ in range(3):
            try:
                rep = gem_render.chat([{"role": "user", "content": prompt}],
                                      temperature=rc["temperature"], reasoning=rc["reasoning"])
                m = re.search(r"\{.*\}", rep.text, re.S)
                text = json.loads(m.group(0))["message"].strip() if m else ""
                err = None if text else "no JSON message"
            except Exception as exc:  # noqa: BLE001
                text, err = "", repr(exc)[:300]
            hits = P.banned_hits(text, P.lang(it))
            attempts.append({"text": text, "error": err, "banned_hits": hits})
            if text and not hits:
                break
        return {"key": P.stimulus_key(it["item_id"], r, "raw"), "item_id": it["item_id"],
                "rendering": r, "channel": "raw", "text": attempts[-1]["text"],
                "attempts": attempts, "model": rc["model"]}

    def relay(job):
        raw, ch = job
        msgs = [{"role": "system", "content": P.RELAY_SYSTEM[ch]},
                {"role": "user", "content": P.RELAY_USER.format(message=raw["text"])}]
        try:
            rep = qwen.chat(msgs, temperature=pc["temperature"], reasoning=pc["reasoning"])
            text, err = rep.text.strip().strip("“”\"").strip(), None
            obs = rep.raw.get("thinking_observed")
        except Exception as exc:  # noqa: BLE001
            text, err, obs = "", repr(exc)[:300], None
        return {"key": P.stimulus_key(raw["item_id"], raw["rendering"], ch),
                "item_id": raw["item_id"], "rendering": raw["rendering"], "channel": ch,
                "text": text, "source_message": raw["text"], "error": err,
                "thinking_observed": obs, "model": pc["model"]}

    by_id = {it["item_id"]: it for it in items}

    def gate(s):
        it = by_id[s["item_id"]]
        opt_a, opt_b, coll = options(it, 0)
        prompt = P.T(it)["GATE_PROMPT"].format(**it, opt_a=opt_a, opt_b=opt_b, text=s["text"])
        try:
            rep = gem_gate.chat([{"role": "user", "content": prompt}],
                                temperature=gc["temperature"], reasoning=gc["reasoning"])
            reply = rep.text
            letter, kind = classify(reply)
            # KHÔNG in the Vietnamese gate, NEITHER in the English one (language arm)
            if kind != "choice" and re.match(r"^\W*(kh[oô]ng|neither|都不)", reply.strip(), re.I):
                kind = "neither"
            err = None
        except Exception as exc:  # noqa: BLE001
            reply, letter, kind, err = "", None, "unparsed", repr(exc)[:300]
        pushes = (letter == coll) if kind == "choice" else (False if kind == "neither" else None)
        return {"key": s["key"], "reply": reply, "letter": letter, "kind": kind,
                "pushes_collusive": pushes, "error": err, "model": gc["model"]}

    with ThreadPoolExecutor(16) as ex:
        raws = list(ex.map(render, [(it, r) for it in items for r in P.RENDERINGS]))
        ok = [r for r in raws if r["text"]]
        relays = list(ex.map(relay, [(r, ch) for r in ok for ch in P.RELAYED
                                     if ch in P.channels(by_id[r["item_id"]])]))
        stim = raws + relays
        gates = list(ex.map(gate, [s for s in stim if s["text"]]))
    return {"stimuli": stim, "gates": gates}


@app.function(image=image, timeout=60 * 30, cpu=1.0, memory=2048,
              secrets=[modal.Secret.from_name("collusion-keys")])
def regate(stim: list[dict], items: list[dict], cfg: dict, prompt_name: str) -> list[dict]:
    """Gate only, on frozen stimuli: nothing is rendered or relayed again."""
    sys.path.insert(0, REMOTE)
    import re
    from concurrent.futures import ThreadPoolExecutor

    from src import prompts as P
    from src.clients import GeminiClient
    from src.episode import options
    from src.scoring import classify

    gc = cfg["gate"]
    gem = GeminiClient(model=gc["model"])
    by_id = {it["item_id"]: it for it in items}
    template = getattr(P, prompt_name)

    def gate(s):
        it = by_id[s["item_id"]]
        opt_a, opt_b, coll = options(it, 0)
        try:
            reply = gem.chat([{"role": "user", "content": template.format(**it, opt_a=opt_a, opt_b=opt_b,
                                                                           text=s["text"])}],
                             temperature=gc["temperature"], reasoning=gc["reasoning"]).text
            letter, kind = classify(reply)
            if kind != "choice" and re.match(r"^\W*(kh[oô]ng|neither|都不)", reply.strip(), re.I):
                kind = "neither"
            err = None
        except Exception as exc:  # noqa: BLE001
            reply, letter, kind, err = "", None, "unparsed", repr(exc)[:300]
        pushes = (letter == coll) if kind == "choice" else (False if kind == "neither" else None)
        return {"key": s["key"], "reply": reply, "letter": letter, "kind": kind,
                "pushes_collusive": pushes, "error": err, "model": gc["model"], "prompt": prompt_name}

    with ThreadPoolExecutor(16) as ex:
        return list(ex.map(gate, stim))


@app.local_entrypoint()
def main(dry_run: bool = False, items: str = "market", regate_with: str = "") -> None:
    """--regate-with GATE_PROMPT_EN_V2 reruns only the gate on the frozen stimuli of --items and
    writes gate_v2.jsonl beside gate.jsonl, which is kept."""
    import difflib

    from src import prompts as P
    from src.episode import load_items
    from src.run_meta import config_hash, git_commit, load_cfg

    from src.episode import stimuli_dir
    item_set = items
    cfg = load_cfg()
    items = load_items(item_set)
    P.assert_prompt_controls(items, None)
    if regate_with:
        from src.episode import load_stimuli
        frozen = load_stimuli(item_set)
        P.assert_prompt_controls(items, frozen)
        dest = stimuli_dir(item_set) / "gate_v2.jsonl"
        print(f"regate        {len(frozen)} frozen stimuli of {item_set} with {regate_with} -> {dest}")
        if dry_run or dest.exists():
            print("--dry-run or gate_v2.jsonl exists: no call made.")
            return
        out = regate.remote(list(frozen.values()), items, cfg, regate_with)
        meta = {"_meta": {"config_hash": config_hash(cfg), "git_commit": git_commit(), "gate": cfg["gate"],
                          "prompt": regate_with, "timestamp": datetime.now(timezone.utc).isoformat()}}
        with dest.open("w") as fh:
            fh.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for r in out:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        kinds: dict[str, int] = {}
        for r in out:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        print(f"wrote {len(out)} gate answers to {dest}   kinds {kinds}")
        return
    n_raw = len(items) * len(P.RENDERINGS)
    n_relay = sum(len([c for c in P.channels(it) if c in P.RELAYED]) for it in items) * len(P.RENDERINGS)
    qwen_url = modal.Function.from_name(cfg["paraphraser"]["app"], "serve").get_web_url()
    print(f"item set      {item_set}")
    print(f"items         {len(items)}  raw messages {n_raw}  relays {n_relay}")
    print(f"renderer      {cfg['renderer']['model']}   relay {cfg['paraphraser']['model']} at {qwen_url}")
    print(f"gate calls    {n_raw + n_relay} on {cfg['gate']['model']}")
    print(f"config_hash   {config_hash(cfg)}   git {git_commit()}")
    if dry_run:
        print("--dry-run: controls asserted, no call made.")
        return

    out = build.remote(items, cfg, qwen_url.rstrip("/") + "/v1")
    meta = {"_meta": {"config_hash": config_hash(cfg), "git_commit": git_commit(),
                      "renderer": cfg["renderer"], "paraphraser": cfg["paraphraser"],
                      "gate": cfg["gate"], "timestamp": datetime.now(timezone.utc).isoformat()}}
    d = stimuli_dir(item_set)
    d.mkdir(parents=True, exist_ok=True)
    for name, rows in (("stimuli.jsonl", out["stimuli"]), ("gate.jsonl", out["gates"])):
        with (d / name).open("w") as fh:
            fh.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    stim = {s["key"]: s for s in out["stimuli"]}
    gates = {g["key"]: g for g in out["gates"]}
    print(f"\nwrote {len(stim)} stimuli, {len(gates)} gate answers to {d}")
    print("\nrelay vs raw: identical / mean similarity")
    for ch in P.RELAYED:
        for r in P.RENDERINGS:
            rows = [s for s in stim.values() if s["channel"] == ch and s["rendering"] == r]
            if not rows:
                continue
            same = sum(1 for s in rows if s["text"].strip() == s["source_message"].strip())
            sim = sum(difflib.SequenceMatcher(None, s["source_message"], s["text"]).ratio()
                      for s in rows) / max(1, len(rows))
            print(f"  {ch:11s} {r:12s} {same:3d}/{len(rows)}  {sim:.3f}")
    print("\ngate: share pushing toward the collusive option")
    for cls in ("harmful", "mutual_gains"):
        for ch in P.CHANNELS:
            row = []
            for r in P.RENDERINGS:
                g = [gates[k] for k, s in stim.items() if k in gates and s["channel"] == ch
                     and s["rendering"] == r and k.split("|")[0].endswith("_h" if cls == "harmful" else "_m")]
                row.append(f"{r}={sum(1 for x in g if x['pushes_collusive'])}/{len(g)}")
            print(f"  {cls:12s} {ch:11s} " + "  ".join(row))
    try:
        P.assert_prompt_controls(items, stim)
        print("\nCONTROLS PASS on the frozen stimuli.")
    except SystemExit as exc:
        print(f"\n{exc}")
    print("COMMIT data/stimuli/ NOW.")
