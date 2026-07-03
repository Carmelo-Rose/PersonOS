#!/usr/bin/env python3
"""Validate and write one confirmed PersonOS prompt entry."""

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
STATUSES = {"已验证", "待验证", "实验中", "弃用"}
REQUIRED = {
    "title",
    "status",
    "category",
    "source",
    "tool_or_scenario",
    "version",
    "prompt_body",
    "input_requirements",
    "output_format",
    "success_criteria",
    "validation_result",
    "applicable_boundary",
    "change_reason",
    "tags",
    "last_updated",
}
ARRAY_FIELDS = {"source", "input_requirements", "success_criteria", "applicable_boundary", "tags"}


class PromptError(ValueError):
    """Raised when prompt input or destination is invalid."""


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromptError(f"无法读取合法 JSON 输入：{exc}") from exc
    if not isinstance(value, dict):
        raise PromptError("输入必须是单个 JSON 对象")
    return value


def validate_date(value: Any, field: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise PromptError(f"{field} 必须使用 YYYY-MM-DD")


def validate_slug(value: str) -> str:
    slug = value.strip().lower()
    if slug.endswith(".md"):
        slug = slug[:-3]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", slug):
        raise PromptError("slug 必须是 1-80 位小写字母、数字或连字符，且以字母或数字开头")
    return slug


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        slug = f"prompt-{date.today().strftime('%Y%m%d')}"
    return slug[:80].strip("-") or "prompt"


def validate_record(record: dict[str, Any]) -> None:
    missing = sorted(REQUIRED - record.keys())
    if missing:
        raise PromptError(f"缺少必填字段：{', '.join(missing)}")
    for key in (
        "title",
        "status",
        "category",
        "tool_or_scenario",
        "version",
        "prompt_body",
        "validation_result",
        "change_reason",
        "last_updated",
    ):
        if not isinstance(record[key], str) or not record[key].strip():
            raise PromptError(f"{key} 必须是非空字符串")
    if record["status"] not in STATUSES:
        raise PromptError(f"status 必须是：{', '.join(sorted(STATUSES))}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_/-]*", record["category"]):
        raise PromptError("category 只能包含小写字母、数字、下划线、连字符或斜杠")
    validate_date(record["last_updated"], "last_updated")
    for field in ARRAY_FIELDS:
        if not isinstance(record[field], list):
            raise PromptError(f"{field} 必须是数组")
    if not record["source"]:
        raise PromptError("source 必须包含至少一条用户动作/判断来源")
    if not all(isinstance(item, str) and item.strip() for item in record["source"]):
        raise PromptError("source 每一项都必须是非空字符串，描述具体用户动作/判断来源")
    if not isinstance(record["output_format"], (str, list)):
        raise PromptError("output_format 必须是字符串或数组")
    if "unresolved" in record and not isinstance(record["unresolved"], list):
        raise PromptError("unresolved 必须是数组")
    if "history" in record and not isinstance(record["history"], list):
        raise PromptError("history 必须是数组")
    if "```" in record["prompt_body"]:
        raise PromptError("prompt_body 不能包含三反引号，避免破坏 fenced block")
    if "slug" in record:
        validate_slug(str(record["slug"]))


def resolve_update_path(root: Path, raw_path: str) -> Path:
    rel = Path(raw_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise PromptError("--path 必须是仓库内相对路径")
    if len(rel.parts) < 3 or rel.parts[0] != "05_prompts" or rel.suffix != ".md":
        raise PromptError("--path 必须形如 05_prompts/<category>/<slug>.md")
    return root / rel


def default_destination(root: Path, record: dict[str, Any], allow_new_category: bool) -> Path:
    category_dir = root / "05_prompts" / record["category"]
    if not category_dir.exists():
        if not allow_new_category:
            raise PromptError(f"分类不存在，需先确认新分类：{record['category']}")
        category_dir.mkdir(parents=True, exist_ok=True)
        readme = category_dir / "README.md"
        if not readme.exists():
            readme.write_text(f"# {record['category']}\n\n待补充。\n", encoding="utf-8")
    if not category_dir.is_dir():
        raise PromptError(f"分类路径不是目录：{category_dir}")
    slug = validate_slug(str(record.get("slug") or slugify(record["title"])))
    return category_dir / f"{slug}.md"


def markdown_list(items: list[Any]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def content_block(value: str | list[Any]) -> str:
    if isinstance(value, list):
        return markdown_list(value)
    return value.strip()


def render_markdown(record: dict[str, Any]) -> str:
    unresolved = record.get("unresolved", [])
    history = record.get("history", [])
    return "\n".join(
        [
            f"# {record['title']}",
            "",
            "## 元数据",
            "",
            f"- 状态：{record['status']}",
            f"- 分类：{record['category']}",
            f"- 工具或场景：{record['tool_or_scenario']}",
            f"- 版本：{record['version']}",
            f"- 最后更新：{record['last_updated']}",
            f"- 标签：{', '.join(map(str, record['tags'])) if record['tags'] else '无'}",
            "",
            "## 用户动作/判断来源",
            "",
            markdown_list(record["source"]),
            "",
            "## 输入要求",
            "",
            markdown_list(record["input_requirements"]),
            "",
            "## 提示词正文",
            "",
            "```text",
            record["prompt_body"].strip(),
            "```",
            "",
            "## 输出格式",
            "",
            content_block(record["output_format"]),
            "",
            "## 成功标准",
            "",
            markdown_list(record["success_criteria"]),
            "",
            "## 验证结果",
            "",
            record["validation_result"].strip(),
            "",
            "## 适用边界",
            "",
            markdown_list(record["applicable_boundary"]),
            "",
            "## 变更原因",
            "",
            record["change_reason"].strip(),
            "",
            "## 版本历史",
            "",
            markdown_list(history),
            "",
            "## 待确认或待验证",
            "",
            markdown_list(unresolved),
            "",
        ]
    )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--path", help="Exact existing repo-relative path for updates")
    parser.add_argument("--allow-new-category", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    record = load_json_object(args.input)
    validate_record(record)

    if args.path:
        destination = resolve_update_path(root, args.path)
        operation = "更新"
        if not destination.is_file():
            raise PromptError(f"更新目标不存在：{destination}")
    else:
        destination = default_destination(root, record, args.allow_new_category)
        operation = "新增"
        if destination.exists():
            raise PromptError(f"目标已存在，拒绝重复新增：{destination}")

    result = {"操作": operation, "目标文件": str(destination)}
    if args.dry_run:
        result["dry_run"] = True
        print(json.dumps(result, ensure_ascii=False))
        return 0

    atomic_write(destination, render_markdown(record))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PromptError as exc:
        raise SystemExit(f"错误：{exc}") from exc
