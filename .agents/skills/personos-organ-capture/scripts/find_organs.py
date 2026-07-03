#!/usr/bin/env python3
"""List existing PersonOS organ assets so a capture can decide new vs update.

Read-only. Lists rule/rubric headings (### ...) in organ Markdown files and the
titled samples in eval_cases JSONL. Used during session-capture extraction to
surface likely duplicates before anything is written. Never modifies the repo.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("/Users/zhuanzmima0000/Documents/PersonOS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--organ", help="Restrict to one organ folder")
    parser.add_argument("--query", help="Case-insensitive substring over heading and path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base = args.root / "02_organs"
    found: list[dict[str, Any]] = []
    if base.is_dir():
        for organ_dir in sorted(d for d in base.iterdir() if d.is_dir()):
            if args.organ and organ_dir.name != args.organ:
                continue
            for md in sorted(organ_dir.glob("*.md")):
                if md.name == "README.md":
                    continue
                text = md.read_text(encoding="utf-8", errors="replace")
                rel = md.relative_to(args.root)
                for heading in re.findall(r"^###\s+(.+)$", text, re.MULTILINE):
                    found.append(
                        {
                            "organ": organ_dir.name,
                            "kind": "rule_or_rubric",
                            "heading": heading.strip(),
                            "path": str(rel),
                        }
                    )
            for jsonl in sorted(organ_dir.glob("*.jsonl")):
                rel = jsonl.relative_to(args.root)
                for line in jsonl.read_text(encoding="utf-8", errors="replace").splitlines():
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(record, dict):
                        continue
                    found.append(
                        {
                            "organ": organ_dir.name,
                            "kind": "eval_case",
                            "heading": record.get("标题") or record.get("编号"),
                            "path": str(rel),
                        }
                    )
    if args.query:
        needle = args.query.casefold()
        found = [
            row
            for row in found
            if needle in f"{row.get('heading', '')} {row.get('path', '')}".casefold()
        ]
    print(json.dumps(found, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
