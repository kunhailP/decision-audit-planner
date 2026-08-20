#!/usr/bin/env python3
"""Inspect the inherited shift-study artifacts without modifying them."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


DEFAULT_SOURCE = Path(
    "/Users/baggeon-u/Documents/Codex/2026-08-20/new-chat/work/shift-study"
)


def csv_profile(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return {
            "exists": True,
            "path": str(path),
            "rows": len(rows),
            "columns": reader.fieldnames or [],
            "has_query_id": bool({"qid", "query_id"} & set(reader.fieldnames or [])),
            "has_repeat_id": bool({"repeat", "repeat_id"} & set(reader.fieldnames or [])),
        }


def git_commit(source: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build_inventory(source: Path) -> dict:
    candidate_dir = source / "runs" / "candidates"
    block1 = csv_profile(source / "runs" / "block1_confirm" / "per_query.csv")
    pilot = csv_profile(source / "runs" / "pilot" / "per_query_v7.csv")
    mechanism = csv_profile(source / "runs" / "h1_mechanism" / "per_query.csv")
    return {
        "source": str(source),
        "git_commit": git_commit(source),
        "candidate_dir": {
            "path": str(candidate_dir),
            "exists": candidate_dir.exists(),
            "csv_files": len(list(candidate_dir.glob("*.csv")))
            if candidate_dir.exists()
            else 0,
        },
        "artifacts": {
            "block1_confirm_per_query": block1,
            "pilot_per_query_v7": pilot,
            "h1_mechanism_per_query": mechanism,
        },
        "budget_curve_ready": bool(
            candidate_dir.exists()
            and block1.get("has_query_id")
            and block1.get("has_repeat_id")
        ),
        "notes": [
            "block1_confirm/per_query.csv is expected to be dataset-level despite its name",
            "candidate-level inputs are required to rerun the probe protocol for new k values",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    inventory = build_inventory(args.source.resolve())
    rendered = json.dumps(inventory, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
