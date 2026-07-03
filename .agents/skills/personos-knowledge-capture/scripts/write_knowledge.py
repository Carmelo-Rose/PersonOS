#!/usr/bin/env python3
"""Validate and write one confirmed PersonOS knowledge entry."""

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
STATUSES = {"已验证", "待验证", "过时"}
REQUIRED = {
    "title",
    "status",
    "type",
    "domain",
    "source",
    "applicable_conditions",
    "staleness_risk",
    "core_content",
    "boundaries",
    "related",
    "tags",
    "last_updated",
}
ARRAY_FIELDS = {"source", "applicable_conditions", "boundaries", "related", "tags"}


class KnowledgeError(ValueError):
    """Raised when knowledge input or destination is invalid."""


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeError(f"无法读取合法 JSON 输入：{exc}") from exc
    if not isinstance(value, dict):
        raise KnowledgeError("输入必须是单个 JSON 对象")
    return value


def validate_date(value: Any, field: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise KnowledgeError(f"{field} 必须使用 YYYY-MM-DD")


def validate_slug(value: str) -> str:
    slug = value.strip().lower()
    if slug.endswith(".md"):
        slug = slug[:-3]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", slug):
        raise KnowledgeError("slug 必须是 1-80 位小写字母、数字或连字符，且以字母或数字开头")
    return slug


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        slug = f"knowledge-{date.today().strftime('%Y%m%d')}"
    return slug[:80].strip("-") or "knowledge"


def validate_record(record: dict[str, Any]) -> None:
    missing = sorted(REQUIRED - record.keys())
    if missing:
        raise KnowledgeError(f"缺少必填字段：{', '.join(missing)}")
    for key in ("title", "status", "type", "domain", "staleness_risk", "last_updated"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise KnowledgeError(f"{key} 必须是非空字符串")
    if record["status"] not in STATUSES:
        raise KnowledgeError(f"status 必须是：{', '.join(sorted(STATUSES))}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_/-]*", record["domain"]):
        raise KnowledgeError("domain 只能包含小写字母、数字、下划线、连字符或斜杠")
    validate_date(record["last_updated"], "last_updated")
    for field in ARRAY_FIELDS:
        if not isinstance(record[field], list):
            raise KnowledgeError(f"{field} 必须是数组")
    if not record["source"]:
        raise KnowledgeError("source 必须包含至少一条用户动作/判断来源")
    if not all(isinstance(item, str) and item.strip() for item in record["source"]):
        raise KnowledgeError("source 每一项都必须是非空字符串，描述具体用户动作/判断来源")
    if "unresolved" in record and not isinstance(record["unresolved"], list):
        raise KnowledgeError("unresolved 必须是数组")
    content = record["core_content"]
    if not isinstance(content, (str, list)) or (isinstance(content, str) and not content.strip()):
        raise KnowledgeError("core_content 必须是非空字符串或数组")
    if isinstance(content, list) and not content:
        raise KnowledgeError("core_content 数组不能为空")
    if "slug" in record:
        validate_slug(str(record["slug"]))


def resolve_update_path(root: Path, raw_path: str) -> Path:
    rel = Path(raw_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise KnowledgeError("--path 必须是仓库内相对路径")
    if len(rel.parts) < 3 or rel.parts[0] != "03_knowledge" or rel.suffix != ".md":
        raise KnowledgeError("--path 必须形如 03_knowledge/<domain>/<slug>.md")
    return root / rel


def default_destination(root: Path, record: dict[str, Any], allow_new_domain: bool) -> Path:
    domain_dir = root / "03_knowledge" / record["domain"]
    if not domain_dir.exists():
        if not allow_new_domain:
            raise KnowledgeError(f"领域不存在，需先确认新领域：{record['domain']}")
        domain_dir.mkdir(parents=True, exist_ok=True)
        readme = domain_dir / "README.md"
        if not readme.exists():
            readme.write_text(f"# {record['domain']}\n\n待补充。\n", encoding="utf-8")
    if not domain_dir.is_dir():
        raise KnowledgeError(f"领域路径不是目录：{domain_dir}")
    slug = validate_slug(str(record.get("slug") or slugify(record["title"])))
    return domain_dir / f"{slug}.md"


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
    return "\n".join(
        [
            f"# {record['title']}",
            "",
            "## 元数据",
            "",
            f"- 状态：{record['status']}",
            f"- 类型：{record['type']}",
            f"- 领域：{record['domain']}",
            f"- 最后更新：{record['last_updated']}",
            f"- 标签：{', '.join(map(str, record['tags'])) if record['tags'] else '无'}",
            "",
            "## 用户动作/判断来源",
            "",
            markdown_list(record["source"]),
            "",
            "## 适用条件",
            "",
            markdown_list(record["applicable_conditions"]),
            "",
            "## 核心内容",
            "",
            content_block(record["core_content"]),
            "",
            "## 边界与例外",
            "",
            markdown_list(record["boundaries"]),
            "",
            "## 失效风险",
            "",
            record["staleness_risk"].strip(),
            "",
            "## 关联项",
            "",
            markdown_list(record["related"]),
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
    parser.add_argument("--allow-new-domain", action="store_true")
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
            raise KnowledgeError(f"更新目标不存在：{destination}")
    else:
        destination = default_destination(root, record, args.allow_new_domain)
        operation = "新增"
        if destination.exists():
            raise KnowledgeError(f"目标已存在，拒绝重复新增：{destination}")

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
    except KnowledgeError as exc:
        raise SystemExit(f"错误：{exc}") from exc
