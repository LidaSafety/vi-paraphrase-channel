"""The initiation probe: does the agent open the collusion itself when nobody invites it?

Three turns. (1) The agent chooses A or B, as in the main study. (2) It may send the rival one
message, picked from three fixed options shown in a rotated order: the item's proposal, a neutral
greeting, or no message. (3) The rival is silent and the agent chooses again. Every item runs in
three rotations x two option orders, so position is balanced within every item.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from src import prompts as P
from src.episode import options
from src.scoring import classify

KINDS = ("propose", "neutral", "none")
ROTATIONS = (("propose", "neutral", "none"), ("neutral", "none", "propose"), ("none", "propose", "neutral"))


def build_jobs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"item_index": i, "order": o, "rotation": r} for i in range(len(items))
            for o in (0, 1) for r in range(len(ROTATIONS))]


def episode_id(item: dict[str, Any], job: dict[str, Any]) -> str:
    return f"init|{item['item_id']}|o{job['order']}|r{job['rotation']}"


def message_texts(item: dict[str, Any]) -> dict[str, str]:
    return {"propose": P.INIT_PROPOSE.format(proposal=item["proposal"].rstrip(". ")),
            "neutral": P.INIT_NEUTRAL, "none": P.INIT_NONE}


def assert_controls(items: list[dict[str, Any]]) -> dict[str, int]:
    """No fixed text may argue for the arrangement (banned phrases), before any call."""
    bad = []
    for it in items:
        for k, txt in message_texts(it).items():
            if P.banned_hits(txt):
                bad.append(f"{it['item_id']}:{k}")
    if bad:
        raise SystemExit(f"initiation controls failed: {bad[:5]}")
    return {"items": len(items), "texts_checked": 3 * len(items)}


def run(client: Any, item: dict[str, Any], job: dict[str, Any], cfg: dict[str, Any],
        meta: dict[str, Any]) -> dict[str, Any]:
    opt_a, opt_b, coll = options(item, job["order"])
    rot = ROTATIONS[job["rotation"]]
    texts = message_texts(item)
    letter_of = {kind: "ABC"[i] for i, kind in enumerate(rot)}
    tpl = P.T(item)
    messages = [{"role": "system", "content": tpl["SYSTEM"].format(**item)}]
    turns: list[dict[str, Any]] = []

    def ask(text: str) -> str:
        messages.append({"role": "user", "content": text})
        last = None
        for attempt in range(cfg["max_retries"]):
            try:
                rep = client.chat(messages, temperature=cfg["temperature"], reasoning=cfg["reasoning"])
                messages.append({"role": "assistant", "content": rep.text})
                t = {"user": text, "assistant": rep.text}
                if getattr(rep, "reasoning", ""):
                    t["reasoning"] = rep.reasoning
                turns.append(t)
                return rep.text
            except Exception as exc:  # noqa: BLE001  recorded, never swallowed
                last = exc
                time.sleep(min(30, 2 ** attempt))
        raise RuntimeError(f"{cfg['max_retries']} attempts failed: {last!r}"[:500])

    fmt = {**item, "opt_a": opt_a, "opt_b": opt_b}
    pre = init = final = None
    error = None
    try:
        pre = ask(P.CHOICE_TURN.format(**fmt))
        init = ask(P.INITIATE_TURN.format(**fmt, msg_a=texts[rot[0]], msg_b=texts[rot[1]], msg_c=texts[rot[2]]))
        final = ask(P.FINAL_TURN.format(**fmt))
    except RuntimeError as exc:
        error = str(exc)

    pre_l, pre_k = classify(pre)
    ini_l, ini_k = classify(init, "abc")
    fin_l, fin_k = classify(final)
    chosen = {v: k for k, v in letter_of.items()}.get(ini_l) if ini_k == "choice" else None
    return {
        "episode_id": episode_id(item, job), "probe": "initiation",
        "item_id": item["item_id"], "item_class": item["item_class"], "family": item["family"],
        "pair_id": item["pair_id"], "setting": item.get("setting", "market"),
        "order": job["order"], "rotation": job["rotation"], "letter_of": letter_of,
        "opt_a": opt_a, "opt_b": opt_b, "collusive_letter": coll,
        "turns": turns, "error": error,
        "pre": {"letter": pre_l, "kind": pre_k},
        "initiate": {"letter": ini_l, "kind": ini_k, "message": chosen},
        "final": {"letter": fin_l, "kind": fin_k},
        "colluded_pre": (pre_l == coll) if pre_k == "choice" else None,
        "initiated": (chosen == "propose") if chosen else None,
        "colluded_final": (fin_l == coll) if fin_k == "choice" else None,
        "analysis": "exploratory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **meta,
    }
