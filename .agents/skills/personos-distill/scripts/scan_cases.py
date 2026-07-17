#!/usr/bin/env python3
"""Read-only PersonOS distillation scan.

Inventories real 04_cases, existing 02_organs rules/eval, and 06_eval system evals,
then reports the cross-reference gaps distillation should close:

  - organ rules whose 用户动作/判断来源 cites no real case 编号
  - decision cases not yet referenced by any 06_eval 来源案例 / 关联案例
  - tag and project clusters (>=2 real cases) that may support a new or updated rule

This script never writes. It is the eyes of personos-distill; the agent reads its
JSON output, does the semantic clustering, and proposes candidates for confirmation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

CASE_ID_RE = re.compile(r"\b(?:decision|failure|success|project)_\d{8}_\d{3}\b")

CASE_FILES = {
    "decision": "decision_cases.jsonl",
    "failure": "failure_cases.jsonl",
    "success": "success_cases.jsonl",
    "project": "project_cases.jsonl",
}


def resolve_root(explicit: Path | None) -> Path:
    if explicit:
        return explicit.expanduser().resolve()
    env_root = os.environ.get("PERSONOS_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    # Auto-detect: walk up from cwd looking for the PersonOS layout.
    for base in [Path.cwd(), *Path.cwd().parents]:
        if (base / "04_cases").is_dir() and (base / "02_organs").is_dir():
            return base.resolve()
    return (Path.home() / "Documents" / "PersonOS").resolve()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def is_real(rec: dict[str, Any]) -> bool:
    return str(rec.get("状态", "")).startswith("真实/")


def one_line(rec: dict[str, Any]) -> str:
    for key in ("最终选择", "成功表现", "失败表现", "结果", "目标", "决策背景", "背景"):
        val = rec.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()[:80]
    return ""


def load_cases(root: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for ctype, fname in CASE_FILES.items():
        for rec in load_jsonl(root / "04_cases" / fname):
            if not is_real(rec):
                continue
            cases.append(
                {
                    "编号": rec.get("编号"),
                    "类型": ctype,
                    "项目": rec.get("项目", "未标注"),
                    "发生日期": rec.get("发生日期", "待确认"),
                    "标签": rec.get("标签", []) or [],
                    "摘要": one_line(rec),
                    "待验证项": rec.get("待验证项", []) or [],
                }
            )
    return cases


SECTION_RE = re.compile(r"(?ms)^### (?P<heading>.+?)\n(?P<body>.*?)(?=^### |\Z)")


def field_from_body(body: str, label: str) -> str:
    m = re.search(rf"^- {re.escape(label)}[:：](.*)$", body, re.MULTILINE)
    return m.group(1).strip() if m else ""


def load_organ_rules(root: Path) -> list[dict[str, Any]]:
    base = root / "02_organs"
    rules: list[dict[str, Any]] = []
    if not base.is_dir():
        return rules
    for organ_dir in sorted(d for d in base.iterdir() if d.is_dir()):
        for md in sorted(organ_dir.glob("*.md")):
            if md.name == "README.md":
                continue
            text = md.read_text(encoding="utf-8", errors="replace")
            for m in SECTION_RE.finditer(text):
                heading = m.group("heading").strip()
                body = m.group("body")
                source = field_from_body(body, "用户动作/判断来源")
                cited = sorted(set(CASE_ID_RE.findall(body)))
                rules.append(
                    {
                        "organ": organ_dir.name,
                        "path": str(md.relative_to(root)),
                        "heading": heading,
                        "状态": field_from_body(body, "状态"),
                        "适用场景": field_from_body(body, "适用场景")[:120],
                        "标签": field_from_body(body, "标签"),
                        "来源文本": source[:160],
                        "已引用案例": cited,
                        "未打通": len(cited) == 0,
                    }
                )
    return rules


def load_eval_case_refs(root: Path) -> dict[str, list[str]]:
    """Return {source_file: [case ids referenced]} across organ eval + 06_eval."""
    refs: dict[str, list[str]] = {}
    # organ eval_cases.jsonl
    base = root / "02_organs"
    if base.is_dir():
        for jl in base.rglob("eval_cases.jsonl"):
            ids: list[str] = []
            for rec in load_jsonl(jl):
                ids += CASE_ID_RE.findall(json.dumps(rec, ensure_ascii=False))
            refs[str(jl.relative_to(root))] = sorted(set(ids))
    # 06_eval/*.jsonl
    ev = root / "06_eval"
    if ev.is_dir():
        for jl in sorted(ev.glob("*.jsonl")):
            ids = []
            real = False
            for rec in load_jsonl(jl):
                if str(rec.get("状态", "")).startswith("真实/"):
                    real = True
                ids += CASE_ID_RE.findall(json.dumps(rec, ensure_ascii=False))
                for cid in rec.get("来源案例", []) or []:
                    if isinstance(cid, str):
                        ids.append(cid)
            refs[str(jl.relative_to(root))] = sorted(set(ids))
            refs.setdefault("_meta", [])
    return refs


def build_clusters(cases: list[dict[str, Any]]) -> dict[str, Any]:
    by_project: dict[str, list[str]] = defaultdict(list)
    by_tag: dict[str, list[str]] = defaultdict(list)
    for c in cases:
        by_project[str(c["项目"])].append(c["编号"])
        for tag in c["标签"]:
            by_tag[str(tag)].append(c["编号"])
    return {
        "by_project": {k: v for k, v in sorted(by_project.items()) if len(v) >= 2},
        "by_tag": {k: v for k, v in sorted(by_tag.items(), key=lambda kv: -len(kv[1])) if len(v) >= 2},
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=None)
    p.add_argument("--json", action="store_true", help="Print full JSON (default)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_root(args.root)

    cases = load_cases(root)
    rules = load_organ_rules(root)
    eval_refs = load_eval_case_refs(root)

    referenced_ids: set[str] = set()
    for ids in eval_refs.values():
        referenced_ids.update(ids)
    for r in rules:
        referenced_ids.update(r["已引用案例"])

    decision_ids = [c["编号"] for c in cases if c["类型"] == "decision"]
    decisions_without_eval = [cid for cid in decision_ids if cid not in referenced_ids]

    report = {
        "root": str(root),
        "计数": {
            "真实案例": len(cases),
            "按类型": {t: sum(1 for c in cases if c["类型"] == t) for t in CASE_FILES},
            "器官规则": len(rules),
            "未打通规则": sum(1 for r in rules if r["未打通"]),
        },
        "案例": cases,
        "器官规则": rules,
        "缺口": {
            "未引用任何案例的规则": [
                {"organ": r["organ"], "heading": r["heading"], "path": r["path"]}
                for r in rules
                if r["未打通"]
            ],
            "尚无eval的决策案例": decisions_without_eval,
        },
        "聚类线索": build_clusters(cases),
        "现有eval引用": eval_refs,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
