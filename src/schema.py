"""Record validation. Every JSONL record validates before analysis reads it."""

from __future__ import annotations

from typing import Any

from src.prompts import ALL_VIEWS, CHANNELS, RENDERINGS

EPISODE_REQUIRED = (
    "episode_id", "item_id", "item_class", "rendering", "channel", "order", "rep",
    "collusive_letter", "raw_message", "delivered_message", "turns", "pre", "post",
    "colluded_pre", "colluded_post", "moved_to_collude", "analysis",
    "config_hash", "git_commit", "model", "temperature", "timestamp",
)
META_KEYS = ("config_hash", "git_commit", "model", "temperature")


def validate_episode(rec: dict[str, Any]) -> list[str]:
    p = [f"missing {k}" for k in EPISODE_REQUIRED if k not in rec]
    if p:
        return p
    if rec["rendering"] not in RENDERINGS:
        p.append(f"bad rendering {rec['rendering']}")
    if rec["channel"] not in CHANNELS:
        p.append(f"bad channel {rec['channel']}")
    if rec["analysis"] != "exploratory":
        p.append("analysis must be 'exploratory' until a prereg is tagged")
    for turn in ("pre", "post"):
        t = rec[turn]
        if t["kind"] == "choice" and t["letter"] not in ("A", "B"):
            p.append(f"{turn}: choice without a letter")
        if t["kind"] != "choice" and t["letter"] is not None:
            p.append(f"{turn}: {t['kind']} carries a letter")
    if rec["channel"] == "raw" and rec["raw_message"] != rec["delivered_message"]:
        p.append("raw channel delivered a different message")
    if rec["error"] is None and len(rec["turns"]) != 4:
        p.append(f"{len(rec['turns'])} turns without an error")
    return p


def validate_verdict(rec: dict[str, Any]) -> list[str]:
    need = ("episode_id", "view", "monitor", "reply", "verdict", "kind", "model",
            "config_hash", "git_commit", "timestamp")
    p = [f"missing {k}" for k in need if k not in rec]
    if not p and rec["view"] not in ALL_VIEWS:
        p.append(f"bad view {rec['view']}")
    return p
