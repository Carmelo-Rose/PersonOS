#!/usr/bin/env python3
"""Validate and atomically replace one confirmed PersonOS case by exact ID."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from append_case import (
    DEFAULT_ROOT,
    TYPE_CONFIG,
    CaseError,
    apply_decision_lifecycle,
    atomic_append,
    load_json_object,
    load_jsonl,
    validate_case,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, dest="case_id")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matches: list[tuple[str, Path, list[dict], int]] = []
    for case_type, (filename, _) in TYPE_CONFIG.items():
        destination = args.root / "04_cases" / filename
        records = load_jsonl(destination)
        for index, record in enumerate(records):
            if record.get("编号") == args.case_id:
                matches.append((case_type, destination, records, index))
    if not matches:
        raise CaseError(f"未找到案例：{args.case_id}")
    if len(matches) != 1:
        raise CaseError(f"案例编号不唯一，拒绝更新：{args.case_id}")

    case_type, destination, records, index = matches[0]
    if not str(records[index].get("状态", "")).startswith("真实/"):
        raise CaseError("只允许更新真实案例")
    replacement = load_json_object(args.input)
    validate_case(case_type, replacement)
    if case_type == "decision":
        # 更新决策时保留生命周期字段；若替换对象省略，则沿用原记录的值
        old = records[index]
        replacement.setdefault("决策状态", old.get("决策状态", "现行"))
        replacement.setdefault("取代", old.get("取代", ""))
        replacement.setdefault("被取代", old.get("被取代", ""))
        replacement = apply_decision_lifecycle(replacement)
    replacement = {"编号": args.case_id, **replacement}
    records[index] = replacement
    result = {"编号": args.case_id, "操作": "更新", "目标文件": str(destination)}
    if args.dry_run:
        result["dry_run"] = True
    else:
        atomic_append(destination, records[:-1], records[-1])
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CaseError as exc:
        raise SystemExit(f"错误：{exc}") from exc
