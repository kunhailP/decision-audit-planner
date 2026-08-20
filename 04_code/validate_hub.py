#!/usr/bin/env python3
"""Validate the research hub's required control documents."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "PROJECT.yaml",
    "00_admin/DECISIONS.md",
    "00_admin/STATUS.md",
    "00_admin/ROADMAP.md",
    "00_admin/QUALITY_GATES.md",
    "00_admin/SUBMISSION_STRATEGY.md",
    "01_design/METHOD_SPEC_v0.2.md",
    "01_design/CLAIM_EVIDENCE_MATRIX.md",
    "02_literature/RELATED_WORK_MATRIX.md",
    "03_data/DATA_REGISTRY.yaml",
    "04_code/CONTRACTS.md",
    "04_code/configs/research_v0.2.yaml",
    "09_artifact/README.md",
    "10_research_program/README.md",
]


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    empty = [
        path
        for path in REQUIRED
        if (ROOT / path).is_file() and (ROOT / path).stat().st_size == 0
    ]
    report = {
        "hub": str(ROOT),
        "required_files": len(REQUIRED),
        "missing": missing,
        "empty": empty,
        "valid": not missing and not empty,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
