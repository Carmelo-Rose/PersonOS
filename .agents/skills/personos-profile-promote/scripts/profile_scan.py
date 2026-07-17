#!/usr/bin/env python3
"""Read-only PersonOS profile-promotion scan.

Profile is the stable self-model layer. It must never be written from a single session:
a trait only earns a profile entry when MULTIPLE real cases support it. This scan feeds
that decision. It reports:

  - existing profile entries (anti-pattern headings, preference rows) and every case id
    already cited across 00_profile, so promotion decides new / strengthen without guessing
  - the per-case signal text (复盘 / 经验 / 可复用经验 / 选择理由 / 根因 / 预防方式 …) that
    a trait would be distilled from
  - tag clusters with their PROJECT distribution, so a trait supported by many cases from one
    single project is not mistaken for a cross-project stable trait
  - which real cases are not yet cited anywhere in profile (unused evidence)

Never writes. The agent reads this, forms candidate traits semantically, and only proposes
those whose support crosses the threshold.
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

# Fields that carry a distilled preference / anti-pattern / working-style signal.
SIGNAL_FIELDS = [
    "复盘", "经验", "可复用经验", "成功因素", "关键动作",
    "根因", "预防方式", "修正措施", "选择理由", "预警信号",
]


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


def load_cases(root: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for ctype, fname in CASE_FILES.items():
        for rec in load_jsonl(root / "04_cases" / fname):
            if not is_real(rec):
                continue
            signals: list[str] = []
            for key in SIGNAL_FIELDS:
                val = rec.get(key)
                if isinstance(val, str) and val.strip():
                    signals.append(f"{key}: {val.strip()}")
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and item.strip():
                            signals.append(f"{key}: {item.strip()}")
            cases.append(
                {
                    "编号": rec.get("编号"),
                    "类型": ctype,
                    "项目": rec.get("项目", "未标注"),
                    "标签": rec.get("标签", []) or [],
                    "信号": signals,
                }
            )
    return cases


def scan_profile(root: Path) -> dict[str, Any]:
    base = root / "00_profile"
    anti_headings: list[str] = []
    pref_rows: list[str] = []
    cited: set[str] = set()
    per_file_cases: dict[str, list[str]] = {}

    if base.is_dir():
        for md in sorted(base.glob("*.md")):
            text = md.read_text(encoding="utf-8", errors="replace")
            ids = sorted(set(CASE_ID_RE.findall(text)))
            per_file_cases[md.name] = ids
            cited.update(ids)
            if md.name == "anti_patterns.md":
                anti_headings = [h.strip() for h in re.findall(r"^###\s+(.+)$", text, re.MULTILINE)]
            if md.name == "preference.md":
                # first column (场景) of the 决策偏好 markdown table
                in_pref = False
                for line in text.splitlines():
                    if line.startswith("## 决策偏好"):
                        in_pref = True
                        continue
                    if in_pref and line.startswith("## "):
                        break
                    if in_pref and line.strip().startswith("|"):
                        cells = [c.strip() for c in line.strip().strip("|").split("|")]
                        if cells and cells[0] not in ("场景", "---", "") and set(cells[0]) != {"-"}:
                            pref_rows.append(cells[0])
    return {
        "反模式标题": anti_headings,
        "决策偏好场景": pref_rows,
        "已引用案例": sorted(cited),
        "各文件引用案例": per_file_cases,
    }


def build_clusters(cases: list[dict[str, Any]]) -> dict[str, Any]:
    by_tag: dict[str, list[str]] = defaultdict(list)
    tag_projects: dict[str, set[str]] = defaultdict(set)
    for c in cases:
        for tag in c["标签"]:
            by_tag[str(tag)].append(c["编号"])
            tag_projects[str(tag)].add(str(c["项目"]))
    clusters = {}
    for tag, ids in by_tag.items():
        if len(ids) >= 2:
            clusters[tag] = {
                "案例": ids,
                "项目数": len(tag_projects[tag]),
                "项目": sorted(tag_projects[tag]),
                "跨项目": len(tag_projects[tag]) >= 2,
            }
    # cross-project clusters first (stronger evidence), then by support size
    return dict(sorted(clusters.items(), key=lambda kv: (-kv[1]["项目数"], -len(kv[1]["案例"]))))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_root(args.root)
    cases = load_cases(root)
    profile = scan_profile(root)

    all_ids = {c["编号"] for c in cases}
    uncited = sorted(all_ids - set(profile["已引用案例"]))

    report = {
        "root": str(root),
        "计数": {
            "真实案例": len(cases),
            "profile已引用案例": len(profile["已引用案例"]),
            "profile未引用案例": len(uncited),
            "反模式条目": len(profile["反模式标题"]),
            "决策偏好条目": len(profile["决策偏好场景"]),
        },
        "现有profile": profile,
        "未被profile引用的案例": uncited,
        "信号语料": cases,
        "聚类线索_跨项目优先": build_clusters(cases),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
