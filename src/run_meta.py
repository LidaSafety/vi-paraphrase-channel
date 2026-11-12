"""Config hash, git commit, cost estimate. Read on the laptop, stamped on every record."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_cfg() -> dict[str, Any]:
    return yaml.safe_load((ROOT / "configs" / "study.yaml").read_text())


def config_hash(cfg: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]


def git_commit() -> str:
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                      text=True, stderr=subprocess.DEVNULL).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "src", "scripts", "configs"],
                                        cwd=ROOT, text=True).strip()
        return sha + ("-dirty" if dirty else "")
    except Exception:  # noqa: BLE001
        return "no-commit"


def estimate_episode_cost(cfg: dict[str, Any], agent: str, n: int) -> tuple[float, str]:
    """(USD, what is billed). API agents bill tokens; Modal agents bill GPU time."""
    c, a = cfg["cost"], cfg["agents"][agent]
    if a["client"] == "vllm":
        out = c["est_output_tokens_per_episode_by_model"][a["model"]] * n
        hours = out / c["est_gpu_tok_per_s"] / 3600
        return hours * c["gpu_hourly"]["L40S"], f"Modal L40S, ~{hours:.2f} GPU-hours"
    pin, pout = c["prices_per_mtok"][a["model"]]
    usd = (c["est_input_tokens_per_episode"] * pin
           + c["est_output_tokens_per_episode"] * pout) * n / 1e6
    return usd, f"{a['model']} tokens"
