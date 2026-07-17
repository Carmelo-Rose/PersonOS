#!/usr/bin/env python3
"""Write one confirmed PersonOS distillation manifest.

A manifest is a JSON array of items, each with a `kind`. Distillation only ever
writes assets that trace back to real cases, so every item must carry case linkage:

  kind = "rule"         新增 02_organs 规则；source 必须至少含一个真实案例编号
  kind = "link_source"  给一条既有 02_organs 规则补挂案例编号（打通存量，最小改动）
  kind = "eval_case"    追加 02_organs/<organ>/eval_cases.jsonl；source 必须含案例编号
  kind = "system_eval"  追加 06_eval/<file>.jsonl；来源案例 必须非空

Rule rendering is byte-compatible with personos-organ-capture's write_organ.py.
All writes are atomic. Use --dry-run to preview without touching the repo.
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
STATUSES = {"已验证", "待验证", "实验中", "弃用"}
CONFIDENCE = {"高", "中", "低"}
RULE_REQUIRED = {
    "applicable_scenario",
    "positive_requirement",
    "avoid",
    "judgment_basis",
    "examples",
    "exceptions",
    "confidence",
}
EVAL_REQUIRED = {"sample", "expected_classification", "expected_score", "judgment_reason"}
ALLOWED_SYSTEM_EVAL = {
    "project_decision_eval.jsonl",
    "person_answer_eval.jsonl",
    "visual_eval.jsonl",
}


class DistillError(ValueError):
    """Raised when manifest input or destination is invalid."""


def resolve_root(explicit: Path | None) -> Path:
    if explicit:
        return explicit.expanduser().resolve()
    env_root = os.environ.get("PERSONOS_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    for base in [Path.cwd(), *Path.cwd().parents]:
        if (base / "04_cases").is_dir() and (base / "02_organs").is_dir():
            return base.resolve()
    return (Path.home() / "Documents" / "PersonOS").resolve()


# ---------- io helpers ----------

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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise DistillError(f"目标 JSONL 第 {n} 行为空：{path}")
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DistillError(f"目标 JSONL 第 {n} 行非法：{exc}") from exc
        if not isinstance(rec, dict):
            raise DistillError(f"目标 JSONL 第 {n} 行不是对象：{path}")
        records.append(rec)
    return records


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    text = "".join(
        json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records
    )
    atomic_write(path, text)


def next_id(prefix: str, records: list[dict[str, Any]]) -> str:
    stem = re.sub(r"[^a-z0-9]+", "_", prefix.lower()).strip("_") or "item"
    day = date.today().strftime("%Y%m%d")
    pat = re.compile(rf"^{re.escape(stem)}_{day}_(\d{{3}})$")
    seq = max(
        (
            int(m.group(1))
            for r in records
            if isinstance(r.get("编号"), str) and (m := pat.match(r["编号"]))
        ),
        default=0,
    )
    return f"{stem}_{day}_{seq + 1:03d}"


def markdown_list(items: list[Any]) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "- 无"


# ---------- validation ----------

def require_case_source(source: list[Any], field: str) -> None:
    if not isinstance(source, list) or not source:
        raise DistillError(f"{field} 必须是非空数组，至少引用一个真实案例编号")
    joined = " ".join(str(s) for s in source)
    if not CASE_ID_RE.search(joined):
        raise DistillError(
            f"{field} 未包含任何真实案例编号（形如 decision_20260614_001）；"
            f"蒸馏产物必须可溯源到 04_cases"
        )


def validate_common(item: dict[str, Any]) -> None:
    for key in ("status", "title"):
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise DistillError(f"{key} 必须是非空字符串")
    if not isinstance(item.get("tags", []), list):
        raise DistillError("tags 必须是数组")


# ---------- rule (new) ----------

def render_rule(item: dict[str, Any], heading: str) -> str:
    unresolved = item.get("unresolved", [])
    return "\n".join(
        [
            f"### {heading}",
            "",
            f"- 规则编号：{item.get('rule_id', '待生成或待填写')}",
            f"- 状态：{item['status']}",
            f"- 适用场景：{item['applicable_scenario']}",
            f"- 正向要求：{item['positive_requirement']}",
            f"- 应避免：{item['avoid']}",
            f"- 判断依据：{item['judgment_basis']}",
            "- 示例：",
            markdown_list(item["examples"]),
            f"- 允许例外：{item['exceptions']}",
            f"- 置信度：{item['confidence']}",
            f"- 用户动作/判断来源：{', '.join(map(str, item['source']))}",
            f"- 标签：{', '.join(map(str, item['tags'])) if item.get('tags') else '无'}",
            f"- 待确认或待验证：{', '.join(map(str, unresolved)) if unresolved else '无'}",
            f"- 最后更新日期：{date.today().isoformat()}",
            "",
        ]
    )


def rule_file(root: Path, organ: str, item: dict[str, Any]) -> Path:
    if item.get("destination"):
        name = Path(str(item["destination"])).name
    else:
        name = "visual_rules.md" if organ == "ml_aesthetic" else "rules.md"
    return root / "02_organs" / organ / name


def section_pattern(heading: str) -> re.Pattern[str]:
    return re.compile(rf"(?ms)^### {re.escape(heading)}\n.*?(?=^### |\Z)")


def write_rule(root: Path, item: dict[str, Any], dry: bool) -> dict[str, Any]:
    validate_common(item)
    organ = str(item.get("organ", "")).strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_/-]*", organ):
        raise DistillError("organ 只能包含小写字母、数字、下划线、连字符或斜杠")
    if item["status"] not in STATUSES:
        raise DistillError(f"status 必须是：{', '.join(sorted(STATUSES))}")
    missing = sorted(RULE_REQUIRED - item.keys())
    if missing:
        raise DistillError(f"rule 缺少必填字段：{', '.join(missing)}")
    if item["confidence"] not in CONFIDENCE:
        raise DistillError("confidence 必须是：高、中、低")
    if not isinstance(item["examples"], list):
        raise DistillError("examples 必须是数组")
    require_case_source(item.get("source", []), "source")

    dest = rule_file(root, organ, item)
    if not dest.parent.is_dir():
        raise DistillError(f"器官不存在，请先在 02_organs 下创建：{organ}")
    heading = f"规则名称：{item['title']}"
    original = dest.read_text(encoding="utf-8") if dest.exists() else ""
    if list(section_pattern(heading).finditer(original)):
        raise DistillError(f"目标标题已存在，拒绝重复新增：### {heading}")
    prefix = original.rstrip() + "\n\n" if original.strip() else ""
    if not dry:
        atomic_write(dest, prefix + render_rule(item, heading))
    return {"操作": "新增规则", "目标文件": str(dest.relative_to(root)), "标题": f"### {heading}"}


# ---------- link_source (retro-link existing rule) ----------

def write_link_source(root: Path, item: dict[str, Any], dry: bool) -> dict[str, Any]:
    organ = str(item.get("organ", "")).strip()
    heading = str(item.get("heading", "")).strip()
    add = item.get("add_source_cases", [])
    if not organ or not heading:
        raise DistillError("link_source 需要 organ 与 heading")
    require_case_source(add, "add_source_cases")
    if item.get("destination"):
        dest = root / "02_organs" / organ / Path(str(item["destination"])).name
    else:
        dest = root / "02_organs" / organ / ("visual_rules.md" if organ == "ml_aesthetic" else "rules.md")
    if not dest.exists():
        raise DistillError(f"规则文件不存在：{dest}")
    text = dest.read_text(encoding="utf-8")
    matches = list(section_pattern(heading).finditer(text))
    if len(matches) != 1:
        raise DistillError(f"需要找到唯一标题：### {heading}（找到 {len(matches)} 个）")
    section = matches[0].group(0)

    src_line = re.search(r"^- 用户动作/判断来源：(.*)$", section, re.MULTILINE)
    if not src_line:
        raise DistillError("该规则缺少『用户动作/判断来源』行，无法补挂")
    existing = src_line.group(1)
    already = set(CASE_ID_RE.findall(existing))
    to_add = [c for c in add if c not in already]
    if not to_add:
        return {"操作": "补挂案例", "目标文件": str(dest.relative_to(root)), "标题": f"### {heading}", "结果": "案例已存在，无改动"}
    new_src = existing.rstrip()
    sep = "；证据案例：" if "证据案例" not in existing else "、"
    new_src = f"{new_src}{sep}{'、'.join(to_add)}"
    new_section = section.replace(src_line.group(0), f"- 用户动作/判断来源：{new_src}")
    new_section = re.sub(
        r"^- 最后更新日期：.*$",
        f"- 最后更新日期：{date.today().isoformat()}",
        new_section,
        count=1,
        flags=re.MULTILINE,
    )
    new_text = text[: matches[0].start()] + new_section + text[matches[0].end():]
    if not dry:
        atomic_write(dest, new_text)
    return {"操作": "补挂案例", "目标文件": str(dest.relative_to(root)), "标题": f"### {heading}", "新增案例": to_add}


# ---------- organ eval_case ----------

def write_eval_case(root: Path, item: dict[str, Any], dry: bool) -> dict[str, Any]:
    validate_common(item)
    organ = str(item.get("organ", "")).strip()
    if not organ:
        raise DistillError("eval_case 需要 organ")
    if item["status"] not in STATUSES:
        raise DistillError(f"status 必须是：{', '.join(sorted(STATUSES))}")
    missing = sorted(EVAL_REQUIRED - item.keys())
    if missing:
        raise DistillError(f"eval_case 缺少必填字段：{', '.join(missing)}")
    if not isinstance(item["judgment_reason"], list):
        raise DistillError("judgment_reason 必须是数组")
    require_case_source(item.get("source", []), "source")

    dest = root / "02_organs" / organ / "eval_cases.jsonl"
    if not dest.parent.is_dir():
        raise DistillError(f"器官不存在：{organ}")
    records = load_jsonl(dest)
    rec = {
        "编号": next_id(organ, records),
        "状态": item["status"],
        "标题": item["title"],
        "样本": item["sample"],
        "预期分类": item["expected_classification"],
        "预期分数": item["expected_score"],
        "判断理由": item["judgment_reason"],
        "用户动作/判断来源": item["source"],
        "标签": item.get("tags", []),
        "备注": item.get("notes", ""),
        "最后更新日期": date.today().isoformat(),
    }
    if not dry:
        atomic_write_jsonl(dest, [*records, rec])
    return {"操作": "追加器官eval", "目标文件": str(dest.relative_to(root)), "编号": rec["编号"]}


# ---------- system eval (06_eval) ----------

def write_system_eval(root: Path, item: dict[str, Any], dry: bool) -> dict[str, Any]:
    validate_common(item)
    target = str(item.get("target", "")).strip()
    if target not in ALLOWED_SYSTEM_EVAL:
        raise DistillError(f"target 必须是：{', '.join(sorted(ALLOWED_SYSTEM_EVAL))}")
    content = item.get("content", {})
    if not isinstance(content, dict) or not content:
        raise DistillError("content 必须是非空对象（该 eval 的题面字段）")
    source_cases = item.get("source_cases", [])
    require_case_source(source_cases, "source_cases")

    dest = root / "06_eval" / target
    records = load_jsonl(dest)
    rec = {
        "编号": next_id(Path(target).stem, records),
        "状态": item["status"],
        "标题": item["title"],
        **content,
        "来源案例": source_cases,
        "关联规则": item.get("linked_rules", []),
        "标签": item.get("tags", []),
        "最后更新日期": date.today().isoformat(),
    }
    if not dry:
        atomic_write_jsonl(dest, [*records, rec])
    return {"操作": "追加系统eval", "目标文件": str(dest.relative_to(root)), "编号": rec["编号"]}


WRITERS = {
    "rule": write_rule,
    "link_source": write_link_source,
    "eval_case": write_eval_case,
    "system_eval": write_system_eval,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True, help="Manifest JSON (array of items)")
    p.add_argument("--root", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_root(args.root)
    try:
        manifest = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistillError(f"无法读取 manifest：{exc}") from exc
    if not isinstance(manifest, list) or not manifest:
        raise DistillError("manifest 必须是非空 JSON 数组")

    # Validate every item BEFORE writing anything (all-or-nothing on validation).
    for i, item in enumerate(manifest):
        if not isinstance(item, dict):
            raise DistillError(f"第 {i} 项不是对象")
        kind = item.get("kind")
        if kind not in WRITERS:
            raise DistillError(f"第 {i} 项 kind 非法：{kind}；允许：{', '.join(WRITERS)}")
        WRITERS[kind](root, item, dry=True)

    results = [WRITERS[item["kind"]](root, item, dry=args.dry_run) for item in manifest]
    print(json.dumps({"root": str(root), "dry_run": args.dry_run, "结果": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DistillError as exc:
        raise SystemExit(f"错误：{exc}")
