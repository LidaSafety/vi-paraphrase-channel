"""The example episode quoted in the paper, and the display-only English glosses."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def example_episode() -> dict:
    """One real harmful episode where the message moved a Gemini agent."""
    rows = [json.loads(l) for l in (ROOT / "data/episodes/episodes_gemini.jsonl").read_text().splitlines()[1:]]
    return next(r for r in rows if r["item_class"] == "harmful" and r["moved_to_collude"]
                and r["channel"] == "raw" and r["rendering"] == "euphemism")


def gloss() -> dict[str, str]:
    """Machine-translated English for display, keyed by sha256 of the Vietnamese."""
    path = ROOT / "data/translations/en.jsonl"
    if not path.exists():
        return {}
    return {r["sha"]: r["en"] for r in map(json.loads, path.read_text().splitlines()) if r.get("en")}


def tr(text: str, en: dict[str, str]) -> str | None:
    return en.get(hashlib.sha256(text.encode()).hexdigest())
