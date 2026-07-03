#!/usr/bin/env python3
"""Validate and write one confirmed PersonOS organ judgment asset."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("/Users/zhuanzmima0000/Documents/PersonOS")
KINDS = {"rule", "rubric", "eval_case"}
STATUSES = {"已验证", "待验证", "实验中", "弃用"}
CONFIDENCE = {"高", "中", "低"}
COMMON_REQUIRED = {"kind", "organ", "status", "title", "source", "tags", "last_updated"}
RULE_REQUIRED = {
    "applicable_scenario",
    "positive_requirement",
    "avoid",
    "judgment_basis",
    "examples",
    "exceptions",
    "confidence",
}
RUBRIC_REQUIRED = {"rubric_content", "applicable_scenario", "change_reason"}
EVAL_REQUIRED = {"sample", "expected_classification", "expected_score", "judgment_reason"}


class OrganError(ValueError):
    """Raised when organ input or destination is invalid."""


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OrganError(f"无法读取合法 JSON 输入：{exc}") from exc
    if not isinstance(value, dict):
        raise OrganError("输入必须是单个 JSON 对象")
    return value


def validate_date(value: Any, field: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise OrganError(f"{field} 必须使用 YYYY-MM-DD")


def validate_rel_filename(value: str, suffix: str) -> str:
    raw = value.strip()
    rel = Path(raw)
    if rel.is_absolute() or ".." in rel.parts or len(rel.parts) != 1:
        raise OrganError("destination 必须是器官目录下的单个文件名")
    if rel.suffix != suffix:
        raise OrganError(f"destination 必须以 {suffix} 结尾")
    return rel.name


def validate_record(record: dict[str, Any]) -> None:
    missing = sorted(COMMON_REQUIRED - record.keys())
    if missing:
        raise OrganError(f"缺少必填字段：{', '.join(missing)}")
    for key in ("kind", "organ", "status", "title", "last_updated"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise OrganError(f"{key} 必须是非空字符串")
    if record["kind"] not in KINDS:
        raise OrganError(f"kind 必须是：{', '.join(sorted(KINDS))}")
    if record["status"] not in STATUSES:
        raise OrganError(f"status 必须是：{', '.join(sorted(STATUSES))}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_/-]*", record["organ"]):
        raise OrganError("organ 只能包含小写字母、数字、下划线、连字符或斜杠")
    validate_date(record["last_updated"], "last_updated")
    for field in ("source", "tags"):
        if not isinstance(record[field], list):
            raise OrganError(f"{field} 必须是数组")
    if not record["source"]:
        raise OrganError("source 必须包含至少一条用户动作/判断来源")
    if not all(isinstance(item, str) and item.strip() for item in record["source"]):
        raise OrganError("source 每一项都必须是非空字符串，描述具体用户动作/判断来源")
    if "unresolved" in record and not isinstance(record["unresolved"], list):
        raise OrganError("unresolved 必须是数组")

    if record["kind"] == "rule":
        missing = sorted(RULE_REQUIRED - record.keys())
        if missing:
            raise OrganError(f"rule 缺少必填字段：{', '.join(missing)}")
        for key in RULE_REQUIRED - {"examples"}:
            if not isinstance(record[key], str) or not record[key].strip():
                raise OrganError(f"{key} 必须是非空字符串")
        if record["confidence"] not in CONFIDENCE:
            raise OrganError("confidence 必须是：高、中、低")
        if not isinstance(record["examples"], list):
            raise OrganError("examples 必须是数组")
    elif record["kind"] == "rubric":
        missing = sorted(RUBRIC_REQUIRED - record.keys())
        if missing:
            raise OrganError(f"rubric 缺少必填字段：{', '.join(missing)}")
        for key in RUBRIC_REQUIRED:
            if not isinstance(record[key], str) or not record[key].strip():
                raise OrganError(f"{key} 必须是非空字符串")
    else:
        missing = sorted(EVAL_REQUIRED - record.keys())
        if missing:
            raise OrganError(f"eval_case 缺少必填字段：{', '.join(missing)}")
        if not isinstance(record["judgment_reason"], list):
            raise OrganError("judgment_reason 必须是数组")


def organ_dir(root: Path, record: dict[str, Any], allow_new_organ: bool) -> Path:
    destination = root / "02_organs" / record["organ"]
    if not destination.exists():
        if not allow_new_organ:
            raise OrganError(f"器官不存在，需先确认新器官：{record['organ']}")
        destination.mkdir(parents=True, exist_ok=True)
        readme = destination / "README.md"
        if not readme.exists():
            readme.write_text(f"# {record['organ']}\n\n待补充。\n", encoding="utf-8")
    if not destination.is_dir():
        raise OrganError(f"器官路径不是目录：{destination}")
    return destination


def default_rule_file(record: dict[str, Any]) -> str:
    if "destination" in record:
        return validate_rel_filename(str(record["destination"]), ".md")
    return "visual_rules.md" if record["organ"] == "ml_aesthetic" else "rules.md"


def default_rubric_file(record: dict[str, Any]) -> str:
    if "destination" in record:
        return validate_rel_filename(str(record["destination"]), ".md")
    return "scoring_rubric.md"


def default_eval_file(record: dict[str, Any]) -> str:
    if "destination" in record:
        return validate_rel_filename(str(record["destination"]), ".jsonl")
    return "eval_cases.jsonl"


def markdown_list(items: list[Any]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def section_pattern(heading: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?ms)^### {re.escape(heading)}\n.*?(?=^### |\Z)",
    )


def replace_or_append_section(path: Path, heading: str, section: str, update: bool) -> str:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    pattern = section_pattern(heading)
    matches = list(pattern.finditer(original))
    if update:
        if len(matches) != 1:
            raise OrganError(f"更新需要找到唯一标题：### {heading}")
        return original[: matches[0].start()] + section + original[matches[0].end() :]
    if matches:
        raise OrganError(f"目标标题已存在，拒绝重复新增：### {heading}")
    prefix = original.rstrip() + "\n\n" if original.strip() else ""
    return prefix + section


def render_rule(record: dict[str, Any], heading: str) -> str:
    unresolved = record.get("unresolved", [])
    rule_id = record.get("rule_id", "待生成或待填写")
    return "\n".join(
        [
            f"### {heading}",
            "",
            f"- 规则编号：{rule_id}",
            f"- 状态：{record['status']}",
            f"- 适用场景：{record['applicable_scenario']}",
            f"- 正向要求：{record['positive_requirement']}",
            f"- 应避免：{record['avoid']}",
            f"- 判断依据：{record['judgment_basis']}",
            "- 示例：",
            markdown_list(record["examples"]),
            f"- 允许例外：{record['exceptions']}",
            f"- 置信度：{record['confidence']}",
            f"- 用户动作/判断来源：{', '.join(map(str, record['source']))}",
            f"- 标签：{', '.join(map(str, record['tags'])) if record['tags'] else '无'}",
            f"- 待确认或待验证：{', '.join(map(str, unresolved)) if unresolved else '无'}",
            f"- 最后更新日期：{record['last_updated']}",
            "",
        ]
    )


def render_rubric(record: dict[str, Any], heading: str) -> str:
    unresolved = record.get("unresolved", [])
    return "\n".join(
        [
            f"### {heading}",
            "",
            f"- 状态：{record['status']}",
            f"- 适用场景：{record['applicable_scenario']}",
            f"- 变更原因：{record['change_reason']}",
            f"- 用户动作/判断来源：{', '.join(map(str, record['source']))}",
            f"- 标签：{', '.join(map(str, record['tags'])) if record['tags'] else '无'}",
            f"- 待确认或待验证：{', '.join(map(str, unresolved)) if unresolved else '无'}",
            f"- 最后更新日期：{record['last_updated']}",
            "",
            record["rubric_content"].strip(),
            "",
        ]
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise OrganError(f"目标 JSONL 第 {line_number} 行为空")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise OrganError(f"目标 JSONL 第 {line_number} 行非法：{exc}") from exc
        if not isinstance(record, dict):
            raise OrganError(f"目标 JSONL 第 {line_number} 行不是 JSON 对象")
        records.append(record)
    ids = [item.get("编号") for item in records if item.get("编号") is not None]
    if len(ids) != len(set(ids)):
        raise OrganError("目标 JSONL 存在重复编号")
    return records


def next_eval_id(organ: str, records: list[dict[str, Any]]) -> str:
    id_date = date.today().strftime("%Y%m%d")
    prefix = re.sub(r"[^a-z0-9]+", "_", organ.lower()).strip("_") or "organ"
    pattern = re.compile(rf"^{re.escape(prefix)}_{id_date}_(\d{{3}})$")
    sequence = max(
        (
            int(match.group(1))
            for record in records
            if isinstance(record.get("编号"), str)
            and (match := pattern.match(record["编号"]))
        ),
        default=0,
    )
    return f"{prefix}_{id_date}_{sequence + 1:03d}"


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in records)
    atomic_write(path, text)


def append_eval_case(path: Path, record: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    records = load_jsonl(path)
    item = {
        "编号": next_eval_id(record["organ"], records),
        "状态": record["status"],
        "标题": record["title"],
        "样本": record["sample"],
        "预期分类": record["expected_classification"],
        "预期分数": record["expected_score"],
        "判断理由": record["judgment_reason"],
        "用户动作/判断来源": record["source"],
        "标签": record["tags"],
        "备注": record.get("notes", ""),
        "最后更新日期": record["last_updated"],
    }
    if not dry_run:
        atomic_write_jsonl(path, [*records, item])
    return item


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--allow-new-organ", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    record = load_json_object(args.input)
    validate_record(record)
    base = organ_dir(root, record, args.allow_new_organ)

    if record["kind"] == "rule":
        destination = base / default_rule_file(record)
        heading = str(record.get("heading") or f"规则名称：{record['title']}")
        update = "heading" in record
        text = replace_or_append_section(destination, heading, render_rule(record, heading), update)
        operation = "更新" if update else "新增"
        result = {"操作": operation, "目标文件": str(destination), "标题": f"### {heading}"}
        if not args.dry_run:
            atomic_write(destination, text)
    elif record["kind"] == "rubric":
        destination = base / default_rubric_file(record)
        heading = str(record.get("heading") or record["title"])
        update = "heading" in record
        text = replace_or_append_section(destination, heading, render_rubric(record, heading), update)
        operation = "更新" if update else "新增"
        result = {"操作": operation, "目标文件": str(destination), "标题": f"### {heading}"}
        if not args.dry_run:
            atomic_write(destination, text)
    else:
        destination = base / default_eval_file(record)
        item = append_eval_case(destination, record, args.dry_run)
        result = {"操作": "追加 eval case", "目标文件": str(destination), "编号": item["编号"]}

    if args.dry_run:
        result["dry_run"] = True
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OrganError as exc:
        raise SystemExit(f"错误：{exc}") from exc
