#!/usr/bin/env python3
"""Find real PersonOS cases by exact ID, project text, and pending status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from append_case import DEFAULT_ROOT, TYPE_CONFIG, CaseError, load_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--id", dest="case_id")
    parser.add_argument("--project")
    parser.add_argument("--pending", action="store_true")
    return parser.parse_args()


def summary(case_type: str, record: dict[str, Any]) -> dict[str, Any]:
    return {
        "编号": record.get("编号"),
        "类型": case_type,
        "状态": record.get("状态"),
        "发生日期": record.get("发生日期", "待确认"),
        "项目": record.get("项目", "未标注"),
        "结果": record.get("结果")
        or record.get("成功表现")
        or record.get("失败表现")
        or record.get("最终选择"),
        "待验证项": record.get("待验证项", []),
        "关联案例": record.get("关联案例", []),
    }


def main() -> int:
    args = parse_args()
    found: list[dict[str, Any]] = []
    for case_type, (filename, _) in TYPE_CONFIG.items():
        records = load_jsonl(args.root / "04_cases" / filename)
        for record in records:
            if not str(record.get("状态", "")).startswith("真实/"):
                continue
            if args.case_id and record.get("编号") != args.case_id:
                continue
            if args.project and args.project.casefold() not in str(record.get("项目", "")).casefold():
                continue
            if args.pending and not record.get("待验证项"):
                continue
            found.append(summary(case_type, record))
    print(json.dumps(found, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CaseError as exc:
        raise SystemExit(f"错误：{exc}") from exc

