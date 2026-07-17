#!/usr/bin/env python3
"""Validate and atomically append one confirmed real case to PersonOS."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


def resolve_default_root() -> Path:
    env_root = os.environ.get("PERSONOS_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()
    windows_root = Path(r"D:\workspace\PersonOS")
    if os.name == "nt" and windows_root.exists():
        return windows_root
    return Path.home() / "Documents" / "PersonOS"


DEFAULT_ROOT = resolve_default_root()
TYPE_CONFIG = {
    "decision": (
        "decision_cases.jsonl",
        ["决策背景", "候选方案", "最终选择", "选择理由", "结果", "复盘"],
    ),
    "failure": (
        "failure_cases.jsonl",
        ["背景", "失败表现", "根因", "预警信号", "修正措施", "预防方式"],
    ),
    "success": (
        "success_cases.jsonl",
        ["背景", "成功表现", "关键动作", "成功因素", "可复用经验"],
    ),
    "project": (
        "project_cases.jsonl",
        ["背景", "目标", "行动", "结果", "经验"],
    ),
}
COMMON_REQUIRED = ["状态", "发生日期", "项目", "证据来源", "待验证项", "标签"]
ALLOWED_STATUSES = {"真实/已验证", "真实/待验证"}
# 决策生命周期轴（与可信度轴“状态”正交）
ALLOWED_DECISION_STATES = {"现行", "已取代", "已废弃", "提议中"}
DECISION_LIFECYCLE_FIELDS = ("决策状态", "取代", "被取代")


def apply_decision_lifecycle(record: dict[str, Any]) -> dict[str, Any]:
    """确保 decision 记录带有生命周期字段，并置于“状态”之后。缺省 决策状态=现行、指针为空串。"""
    state = record.get("决策状态", "现行")
    supersedes = str(record.get("取代", "") or "").strip()
    superseded_by = str(record.get("被取代", "") or "").strip()
    rebuilt: dict[str, Any] = {}
    for key, value in record.items():
        if key in DECISION_LIFECYCLE_FIELDS:
            continue
        rebuilt[key] = value
        if key == "状态":
            rebuilt["决策状态"] = state
            rebuilt["取代"] = supersedes
            rebuilt["被取代"] = superseded_by
    if "决策状态" not in rebuilt:
        rebuilt["决策状态"] = state
        rebuilt["取代"] = supersedes
        rebuilt["被取代"] = superseded_by
    return rebuilt


class CaseError(ValueError):
    """Raised when a case or destination fails validation."""


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CaseError(f"无法读取合法 JSON 输入：{exc}") from exc
    if not isinstance(value, dict):
        raise CaseError("输入必须是单个 JSON 对象")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise CaseError(f"目标文件不存在：{path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise CaseError(f"目标 JSONL 第 {line_number} 行为空")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CaseError(f"目标 JSONL 第 {line_number} 行非法：{exc}") from exc
        if not isinstance(record, dict):
            raise CaseError(f"目标 JSONL 第 {line_number} 行不是 JSON 对象")
        records.append(record)
    ids = [record.get("编号") for record in records if record.get("编号") is not None]
    if len(ids) != len(set(ids)):
        raise CaseError("目标 JSONL 存在重复编号")
    return records


def validate_case(case_type: str, record: dict[str, Any]) -> None:
    if "编号" in record:
        raise CaseError("输入不得包含“编号”；编号由脚本生成")
    required = COMMON_REQUIRED + TYPE_CONFIG[case_type][1]
    missing = [field for field in required if field not in record]
    if missing:
        raise CaseError(f"缺少必填字段：{', '.join(missing)}")
    if record["状态"] not in ALLOWED_STATUSES:
        raise CaseError("状态必须是“真实/已验证”或“真实/待验证”")
    for field in ("证据来源", "待验证项", "标签"):
        if not isinstance(record[field], list):
            raise CaseError(f"“{field}”必须是数组")
    if "关联案例" in record and not isinstance(record["关联案例"], list):
        raise CaseError("“关联案例”必须是数组")
    if "示例" in record["标签"]:
        raise CaseError("真实案例标签不得包含“示例”")
    if record["状态"] == "真实/已验证" and record["待验证项"]:
        raise CaseError("“真实/已验证”案例的“待验证项”必须为空")
    if case_type == "decision":
        state = record.get("决策状态", "现行")
        if state not in ALLOWED_DECISION_STATES:
            raise CaseError("决策状态必须是：现行 / 已取代 / 已废弃 / 提议中")
        for field in ("取代", "被取代"):
            if field in record and not isinstance(record[field], str):
                raise CaseError(f"“{field}”必须是字符串（决策编号或空串）")


def next_id(case_type: str, records: list[dict[str, Any]], id_date: str) -> str:
    pattern = re.compile(rf"^{re.escape(case_type)}_{re.escape(id_date)}_(\d{{3}})$")
    sequence = max(
        (
            int(match.group(1))
            for record in records
            if isinstance(record.get("编号"), str)
            and (match := pattern.match(record["编号"]))
        ),
        default=0,
    )
    candidate = f"{case_type}_{id_date}_{sequence + 1:03d}"
    if any(record.get("编号") == candidate for record in records):
        raise CaseError(f"生成的编号重复：{candidate}")
    return candidate


def atomic_append(path: Path, records: list[dict[str, Any]], record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for item in [*records, record]:
                handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=TYPE_CONFIG, required=True, dest="case_type")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--id-date",
        default=date.today().strftime("%Y%m%d"),
        help="ID date in YYYYMMDD format; defaults to today",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"\d{8}", args.id_date):
        raise CaseError("--id-date 必须使用 YYYYMMDD 格式")
    filename = TYPE_CONFIG[args.case_type][0]
    destination = args.root / "04_cases" / filename
    record = load_json_object(args.input)
    validate_case(args.case_type, record)
    records = load_jsonl(destination)
    new_id = next_id(args.case_type, records, args.id_date)
    result = {"编号": new_id, "目标文件": str(destination)}
    if args.case_type == "decision":
        record = apply_decision_lifecycle(record)
        supersedes = record["取代"].strip()
        if supersedes:
            targets = [r for r in records if r.get("编号") == supersedes]
            if not targets:
                raise CaseError(f"“取代”指向的决策不存在：{supersedes}")
            target = targets[0]
            record["取代"] = supersedes
            target["决策状态"] = "已取代"
            target["被取代"] = new_id
            result["取代"] = supersedes
            result["旧决策已标记"] = "已取代"
    record = {"编号": new_id, **record}
    if args.dry_run:
        result["dry_run"] = True
    else:
        atomic_append(destination, records, record)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CaseError as exc:
        raise SystemExit(f"错误：{exc}") from exc
