#!/usr/bin/env python3
"""List existing PersonOS knowledge entries so a capture can decide new vs update.

Read-only. Used during session-capture extraction to surface likely duplicates
before anything is written. Never modifies the repository.
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
    parser.add_argument("--domain", help="Restrict to one domain folder")
    parser.add_argument("--query", help="Case-insensitive substring over title and path")
    return parser.parse_args()


def first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else None


def main() -> int:
    args = parse_args()
    base = args.root / "03_knowledge"
    found: list[dict[str, Any]] = []
    if base.is_dir():
        for path in sorted(base.rglob("*.md")):
            if path.name == "README.md":
                continue
            if args.domain and path.parent.name != args.domain:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            title = first_match(text, r"^#\s+(.+)$") or path.stem
            rel = path.relative_to(args.root)
            if args.query and args.query.casefold() not in f"{title} {rel}".casefold():
                continue
            found.append(
                {
                    "title": title,
                    "domain": path.parent.name,
                    "status": first_match(text, r"^-\s*状态[：:]\s*(.+)$"),
                    "tags": first_match(text, r"^-\s*标签[：:]\s*(.+)$"),
                    "path": str(rel),
                }
            )
    print(json.dumps(found, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
