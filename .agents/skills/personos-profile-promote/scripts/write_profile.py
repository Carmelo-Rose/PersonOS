#!/usr/bin/env python3
"""Write one confirmed PersonOS profile-promotion manifest.

Profile is the stable self-model layer, so this writer is deliberately strict:

  kind = "anti_pattern"    新增 00_profile/anti_patterns.md 一条反模式
  kind = "preference_row"  新增 00_profile/preference.md 决策偏好表一行
  kind = "strengthen"      给一条既有反模式补挂新的来源案例

A NEW trait (anti_pattern / preference_row) must be supported by at least --min-support
distinct real case 编号 (default 2). This enforces "多案例支撑后再提炼，避免过早固化未验证抽象".
The writer never touches person_profile.md or 04_cases, and rejects duplicates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

CASE_ID_RE = re.compile(r"\b(?:decision|failure|success|project)_\d{8}_\d{3}\b")
ANTI_REQUIRED = {
    "applicable_scenario", "typical_manifestation", "why_harmful",
    "early_signal", "alternative", "exceptions",
}
PREF_REQUIRED = {"scenario", "preference", "priority", "reason", "exception"}
DEFAULT_MIN_SUPPORT = 2


class ProfileError(ValueError):
    pass


def resolve_root(explicit: Path | None) -> Path:
    if explicit:
        return explicit.expanduser().resolve()
    env_root = os.environ.get("PERSONOS_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    for base in [Path.cwd(), *Path.cwd().parents]:
        if (base / "04_cases").is_dir() and (base / "00_profile").is_dir():
            return base.resolve()
    return (Path.home() / "Documents" / "PersonOS").resolve()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as h:
            h.write(text)
            h.flush()
            os.fsync(h.fileno())
        os.replace(temp, path)
    except Exception:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
        raise


def distinct_case_ids(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    ids: list[str] = []
    for v in values:
        for cid in CASE_ID_RE.findall(str(v)):
            if cid not in ids:
                ids.append(cid)
    return ids


def require_support(source_cases: Any, min_support: int, field: str) -> list[str]:
    ids = distinct_case_ids(source_cases)
    if len(ids) < min_support:
        raise ProfileError(
            f"{field} 仅有 {len(ids)} 个真实案例支撑，未达阈值 {min_support}；"
            f"profile 需多案例支撑后再提炼，避免过早固化"
        )
    return ids


def validate_common(item: dict[str, Any]) -> None:
    if not isinstance(item.get("title"), str) or not item["title"].strip():
        raise ProfileError("title 必须是非空字符串")


# ---------- anti_pattern ----------

def anti_heading(title: str) -> str:
    return f"反模式名称：{title}"


def section_pattern(heading: str) -> re.Pattern[str]:
    return re.compile(rf"(?ms)^### {re.escape(heading)}\n.*?(?=^### |^## |\Z)")


def render_anti(item: dict[str, Any], heading: str, ids: list[str]) -> str:
    return "\n".join(
        [
            f"### {heading}",
            "",
            f"- 适用场景：{item['applicable_scenario']}",
            f"- 典型表现：{item['typical_manifestation']}",
            f"- 为什么有害：{item['why_harmful']}",
            f"- 早期信号：{item['early_signal']}",
            f"- 替代做法：{item['alternative']}",
            f"- 允许例外：{item['exceptions']}",
            f"- 来源案例：{'、'.join(ids)}",
            f"- 最后复核日期：{date.today().isoformat()}",
            "",
        ]
    )


def insert_before_marker(text: str, marker: str, block: str) -> str:
    idx = text.find(marker)
    if idx == -1:
        return text.rstrip() + "\n\n" + block
    head = text[:idx].rstrip()
    return head + "\n\n" + block.rstrip() + "\n\n" + text[idx:]


def write_anti_pattern(root: Path, item: dict[str, Any], min_support: int, dry: bool) -> dict[str, Any]:
    validate_common(item)
    missing = sorted(ANTI_REQUIRED - item.keys())
    if missing:
        raise ProfileError(f"anti_pattern 缺少必填字段：{', '.join(missing)}")
    for k in ANTI_REQUIRED:
        if not isinstance(item[k], str) or not item[k].strip():
            raise ProfileError(f"{k} 必须是非空字符串")
    ids = require_support(item.get("source_cases"), min_support, "source_cases")

    dest = root / "00_profile" / "anti_patterns.md"
    if not dest.exists():
        raise ProfileError(f"文件不存在：{dest}")
    text = dest.read_text(encoding="utf-8")
    heading = anti_heading(item["title"])
    if list(section_pattern(heading).finditer(text)):
        raise ProfileError(f"反模式已存在，拒绝重复新增：### {heading}")
    block = render_anti(item, heading, ids)
    new_text = insert_before_marker(text, "## 待补充清单", block)
    if not dry:
        atomic_write(dest, new_text)
    return {"操作": "新增反模式", "目标文件": "00_profile/anti_patterns.md", "标题": f"### {heading}", "支撑案例": ids}


# ---------- preference_row ----------

def write_preference_row(root: Path, item: dict[str, Any], min_support: int, dry: bool) -> dict[str, Any]:
    validate_common(item)
    missing = sorted(PREF_REQUIRED - item.keys())
    if missing:
        raise ProfileError(f"preference_row 缺少必填字段：{', '.join(missing)}")
    for k in PREF_REQUIRED:
        if not isinstance(item[k], str) or not item[k].strip():
            raise ProfileError(f"{k} 必须是非空字符串")
    ids = require_support(item.get("source_cases"), min_support, "source_cases")

    dest = root / "00_profile" / "preference.md"
    if not dest.exists():
        raise ProfileError(f"文件不存在：{dest}")
    lines = dest.read_text(encoding="utf-8").splitlines()

    # locate 决策偏好 table block
    start = next((i for i, l in enumerate(lines) if l.startswith("## 决策偏好")), None)
    if start is None:
        raise ProfileError("preference.md 缺少『## 决策偏好』小节")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    table_rows = [i for i in range(start, end) if lines[i].strip().startswith("|")]
    if not table_rows:
        raise ProfileError("未找到决策偏好表")
    # duplicate check on 场景 (first column)
    for i in table_rows:
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if cells and cells[0] == item["scenario"].strip():
            raise ProfileError(f"决策偏好场景已存在，拒绝重复新增：{item['scenario']}")

    reason = item["reason"].strip()
    if not CASE_ID_RE.search(reason):
        reason = f"{reason}（{'、'.join(ids)}）"
    row = f"| {item['scenario'].strip()} | {item['preference'].strip()} | {item['priority'].strip()} | {reason} | {item['exception'].strip()} |"
    insert_at = table_rows[-1] + 1
    new_lines = lines[:insert_at] + [row] + lines[insert_at:]
    if not dry:
        atomic_write(dest, "\n".join(new_lines) + "\n")
    return {"操作": "新增决策偏好行", "目标文件": "00_profile/preference.md", "场景": item["scenario"], "支撑案例": ids}


# ---------- strengthen an existing anti-pattern ----------

def write_strengthen(root: Path, item: dict[str, Any], min_support: int, dry: bool) -> dict[str, Any]:
    heading = str(item.get("heading", "")).strip()
    add = distinct_case_ids(item.get("add_source_cases"))
    if not heading:
        raise ProfileError("strengthen 需要 heading（既有反模式标题，不含 ###）")
    if not add:
        raise ProfileError("add_source_cases 必须含真实案例编号")
    dest = root / "00_profile" / "anti_patterns.md"
    text = dest.read_text(encoding="utf-8")
    m = list(section_pattern(heading).finditer(text))
    if len(m) != 1:
        raise ProfileError(f"需要找到唯一反模式标题：### {heading}（找到 {len(m)} 个）")
    section = m[0].group(0)
    src = re.search(r"^- 来源案例：(.*)$", section, re.MULTILINE)
    if not src:
        raise ProfileError("该反模式缺少『来源案例』行")
    already = set(CASE_ID_RE.findall(src.group(1)))
    to_add = [c for c in add if c not in already]
    if not to_add:
        return {"操作": "补挂来源案例", "目标文件": "00_profile/anti_patterns.md", "标题": f"### {heading}", "结果": "案例已存在，无改动"}
    new_src_line = f"- 来源案例：{src.group(1).rstrip()}、{'、'.join(to_add)}"
    new_section = section.replace(src.group(0), new_src_line)
    new_section = re.sub(r"^- 最后复核日期：.*$", f"- 最后复核日期：{date.today().isoformat()}", new_section, count=1, flags=re.MULTILINE)
    new_text = text[: m[0].start()] + new_section + text[m[0].end():]
    if not dry:
        atomic_write(dest, new_text)
    return {"操作": "补挂来源案例", "目标文件": "00_profile/anti_patterns.md", "标题": f"### {heading}", "新增案例": to_add}


WRITERS = {
    "anti_pattern": write_anti_pattern,
    "preference_row": write_preference_row,
    "strengthen": write_strengthen,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--root", type=Path, default=None)
    p.add_argument("--min-support", type=int, default=DEFAULT_MIN_SUPPORT)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_root(args.root)
    try:
        manifest = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"无法读取 manifest：{exc}") from exc
    if not isinstance(manifest, list) or not manifest:
        raise ProfileError("manifest 必须是非空 JSON 数组")

    for i, item in enumerate(manifest):
        if not isinstance(item, dict):
            raise ProfileError(f"第 {i} 项不是对象")
        if item.get("kind") not in WRITERS:
            raise ProfileError(f"第 {i} 项 kind 非法：{item.get('kind')}；允许：{', '.join(WRITERS)}")
        WRITERS[item["kind"]](root, item, args.min_support, dry=True)

    results = [WRITERS[item["kind"]](root, item, args.min_support, dry=args.dry_run) for item in manifest]
    print(json.dumps({"root": str(root), "min_support": args.min_support, "dry_run": args.dry_run, "结果": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProfileError as exc:
        raise SystemExit(f"错误：{exc}")
