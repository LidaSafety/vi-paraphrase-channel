"""One episode, four turns. Shared by the local dry run and the Modal runner."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src import prompts as P
from src.scoring import classify, code_report, parse_yes_no

ROOT = Path(__file__).resolve().parent.parent
# Item sets. `market` is the main study; `workflow` (Track 2.1) runs raw only.
ITEM_SETS = {"market": ("items.jsonl", "stimuli"),
             "workflow": ("items_workflow.jsonl", "stimuli_workflow"),
             "ext": ("items_ext.jsonl", "stimuli_ext"),
             # Language arm (2026-10-28, proposed): the market items in English, raw only.
             "market_en": ("items_en.jsonl", "stimuli_en"),
             "market_zh": ("items_zh.jsonl", "stimuli_zh")}


def items_path(item_set: str = "market") -> Path:
    return ROOT / "data" / "items" / ITEM_SETS[item_set][0]


def stimuli_dir(item_set: str = "market") -> Path:
    return ROOT / "data" / ITEM_SETS[item_set][1]


def load_items(item_set: str = "market") -> list[dict[str, Any]]:
    return [json.loads(l) for l in items_path(item_set).read_text().splitlines() if l.strip()]


def load_stimuli(item_set: str = "market") -> dict[str, dict[str, Any]] | None:
    path = stimuli_dir(item_set) / "stimuli.jsonl"
    if not path.exists():
        return None
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            if "_meta" not in rec:
                out[rec["key"]] = rec
    return out


def build_jobs(items: list[dict[str, Any]], k: int, smoke: int = 0) -> list[dict[str, Any]]:
    """Every item x rendering x channel x order x rep. Both orders run in every
    cell, so order is balanced within every cell by construction."""
    # job order: item, rendering, channel, order, rep
    jobs = []
    for idx, it in enumerate(items):
        for r in P.RENDERINGS:
            for ch in P.channels(it):
                for order in (0, 1):
                    for rep in range(k):
                        jobs.append({"item_index": idx, "rendering": r,
                                     "channel": ch, "order": order, "rep": rep})
    if smoke:
        # Round-robin over class x rendering x channel so a 20-episode smoke
        # touches every cell instead of the first items in file order.
        import random
        rng = random.Random(20261025)
        groups: dict[tuple, list] = {}
        for j in jobs:
            key = (items[j["item_index"]]["item_class"], j["rendering"], j["channel"])
            groups.setdefault(key, []).append(j)
        for g in groups.values():
            rng.shuffle(g)
        keys = sorted(groups)
        picked, i = [], 0
        while len(picked) < min(smoke, len(jobs)):
            g = groups[keys[i % len(keys)]]
            if g:
                picked.append(g.pop())
            i += 1
        jobs = picked
    return jobs


def episode_id(item: dict[str, Any], job: dict[str, Any]) -> str:
    return f"{item['item_id']}|{job['rendering']}|{job['channel']}|o{job['order']}|r{job['rep']}"


def options(item: dict[str, Any], order: int) -> tuple[str, str, str]:
    """(opt_a, opt_b, collusive_letter). Fixed within the episode."""
    flip = (item["order_base"] + order) % 2
    if flip:
        return item["option_collude"], item["option_compete"], "A"
    return item["option_compete"], item["option_collude"], "B"


def run_episode(client: Any, item: dict[str, Any], job: dict[str, Any],
                stimuli: dict[str, dict[str, Any]],
                cfg: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    opt_a, opt_b, coll = options(item, job["order"])
    raw = stimuli[P.stimulus_key(item["item_id"], job["rendering"], "raw")]["text"]
    delivered = stimuli[P.stimulus_key(item["item_id"], job["rendering"], job["channel"])]["text"]

    tpl = P.T(item)
    messages = [{"role": "system", "content": tpl["SYSTEM"].format(**item)}]
    turns: list[dict[str, Any]] = []
    error = None

    def ask(text: str) -> str:
        messages.append({"role": "user", "content": text})
        last = None
        for attempt in range(cfg["max_retries"]):
            try:
                rep = client.chat(messages, temperature=cfg["temperature"],
                                  reasoning=cfg["reasoning"])
                messages.append({"role": "assistant", "content": rep.text})
                t = {"user": text, "assistant": rep.text}
                if getattr(rep, "reasoning", ""):
                    t["reasoning"] = rep.reasoning
                usage = (rep.raw or {}).get("usageMetadata") or (rep.raw or {}).get("usage")
                if usage:
                    t["usage"] = usage
                turns.append(t)
                return rep.text
            except Exception as exc:  # noqa: BLE001  recorded, never swallowed
                last = exc
                time.sleep(min(30, 2 ** attempt))
        raise RuntimeError(f"{cfg['max_retries']} attempts failed: {last!r}"[:500])

    fmt = {**item, "opt_a": opt_a, "opt_b": opt_b}
    pre = post = report = disc = None
    try:
        pre = ask(tpl.get("CHOICE_TURN", P.CHOICE_TURN).format(**fmt))
        post = ask(tpl.get("MESSAGE_TURN", P.MESSAGE_TURN).format(**fmt, message=delivered))
        report = ask(tpl["REPORT_TURN"].format(**fmt))
        disc = ask(tpl["DISCLOSURE_TURN"].format(**fmt))
    except RuntimeError as exc:
        error = str(exc)

    pre_l, pre_k = classify(pre)
    post_l, post_k = classify(post)
    disc_v, disc_k = parse_yes_no(disc)
    lex = code_report(report or "", item["counterpart_principal"], item["counterpart_name"],
                      lang=P.lang(item))
    colluded_pre = (pre_l == coll) if pre_k == "choice" else None
    colluded_post = (post_l == coll) if post_k == "choice" else None
    moved = (colluded_pre is False and colluded_post is True) if (
        colluded_pre is not None and colluded_post is not None) else None
    final_option = None
    if post_k == "choice":
        final_option = opt_a if post_l == "A" else opt_b

    return {
        "episode_id": episode_id(item, job),
        "item_id": item["item_id"], "item_class": item["item_class"],
        "family": item["family"], "pair_id": item["pair_id"],
        "setting": item.get("setting", "market"),
        **({"language": P.lang(item)} if P.lang(item) != "vi" else {}),
        "rendering": job["rendering"], "channel": job["channel"],
        "order": job["order"], "rep": job["rep"],
        "opt_a": opt_a, "opt_b": opt_b, "collusive_letter": coll,
        "raw_message": raw, "delivered_message": delivered,
        "turns": turns, "error": error,
        "pre": {"letter": pre_l, "kind": pre_k},
        "post": {"letter": post_l, "kind": post_k},
        "colluded_pre": colluded_pre, "colluded_post": colluded_post,
        "moved_to_collude": moved, "final_option": final_option,
        "report": report,
        "disclosed_item": disc_v, "disclosure_kind": disc_k,
        "disclosed_lexical": lex["disclosed"], "lexical": lex,
        "analysis": "exploratory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **meta,
    }
