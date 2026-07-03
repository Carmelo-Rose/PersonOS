#!/usr/bin/env python3
"""Apply a confirmed PersonOS capture manifest deterministically.

This is the batch write path for session-capture. After the user confirms the
candidate board, the confirmed items are frozen into a manifest. This script
reads that frozen manifest and dispatches each item to the matching specialist
write script (append_case / update_case / write_knowledge / write_prompt /
write_organ). The model never re-derives content at write time, which is what
removes capture drift.

The specialist write scripts remain the single source of schema validation,
atomic writes, ID generation, and duplicate/path rejection. This script only
routes frozen items to them and reports results.

Manifest shape (JSON):

{
  "schema_version": "1",
  "root": "/Users/zhuanzmima0000/Documents/PersonOS",   # optional; --root wins
  "items": [
    {
      "id": "item-1",                 # optional label for reporting
      "group": "cases|knowledge|prompt|organ",
      "operation": "create|update",
      "title": "...",                 # optional label for reporting
      "case_type": "decision|failure|success|project",  # cases only
      "target_id": "decision_20260616_001",             # cases update only
      "path": "03_knowledge/<domain>/<slug>.md",        # knowledge/prompt update
      "allow_new_domain": false,      # knowledge create into a new domain
      "allow_new_category": false,    # prompt create into a new category
      "allow_new_organ": false,       # organ create into a new organ
      "payload": { ...exact specialist write-script JSON... }
    }
  ]
}

For organ items, new-vs-update is decided by the specialist script from whether
`heading` is present in the payload; `operation` is informational there.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("/Users/zhuanzmima0000/Documents/PersonOS")
SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
GROUPS = {"cases", "knowledge", "prompt", "organ"}
OPERATIONS = {"create", "update"}

SCRIPTS = {
    "cases_create": SKILLS_DIR / "personos-cases-capture" / "scripts" / "append_case.py",
    "cases_update": SKILLS_DIR / "personos-cases-capture" / "scripts" / "update_case.py",
    "knowledge": SKILLS_DIR / "personos-knowledge-capture" / "scripts" / "write_knowledge.py",
    "prompt": SKILLS_DIR / "personos-prompt-capture" / "scripts" / "write_prompt.py",
    "organ": SKILLS_DIR / "personos-organ-capture" / "scripts" / "write_organ.py",
}

# All specialist write scripts support --dry-run.
DRY_RUN_GROUPS = {"cases", "knowledge", "prompt", "organ"}


class ManifestError(ValueError):
    """Raised when the manifest is structurally invalid."""


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"无法读取合法 JSON manifest：{exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError("manifest 必须是单个 JSON 对象")
    items = value.get("items")
    if not isinstance(items, list) or not items:
        raise ManifestError("manifest.items 必须是非空数组")
    return value


def validate_item(item: dict[str, Any], index: int) -> None:
    label = f"items[{index}]"
    if not isinstance(item, dict):
        raise ManifestError(f"{label} 必须是 JSON 对象")
    group = item.get("group")
    if group not in GROUPS:
        raise ManifestError(f"{label}.group 必须是：{', '.join(sorted(GROUPS))}")
    operation = item.get("operation")
    if operation not in OPERATIONS:
        raise ManifestError(f"{label}.operation 必须是：{', '.join(sorted(OPERATIONS))}")
    if not isinstance(item.get("payload"), dict):
        raise ManifestError(f"{label}.payload 必须是 JSON 对象")

    if group == "cases":
        if operation == "create":
            valid = {"decision", "failure", "success", "project"}
            if item.get("case_type") not in valid:
                raise ManifestError(f"{label}.case_type 必须是：{', '.join(sorted(valid))}")
        else:
            if not isinstance(item.get("target_id"), str) or not item["target_id"].strip():
                raise ManifestError(f"{label}.target_id 在 cases 更新时必填")
    elif group in {"knowledge", "prompt"}:
        if operation == "update":
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                raise ManifestError(f"{label}.path 在 {group} 更新时必填")

    script = SCRIPTS["cases_create" if group == "cases" and operation == "create"
                     else "cases_update" if group == "cases"
                     else group]
    if not script.is_file():
        raise ManifestError(f"{label} 找不到写入脚本：{script}")


def build_argv(item: dict[str, Any], payload_file: Path, root: Path, dry_run: bool) -> list[str]:
    group = item["group"]
    operation = item["operation"]
    if group == "cases" and operation == "create":
        argv = [str(SCRIPTS["cases_create"]), "--type", item["case_type"],
                "--input", str(payload_file), "--root", str(root)]
    elif group == "cases":
        argv = [str(SCRIPTS["cases_update"]), "--id", item["target_id"],
                "--input", str(payload_file), "--root", str(root)]
    else:
        argv = [str(SCRIPTS[group]), "--input", str(payload_file), "--root", str(root)]
        if group in {"knowledge", "prompt"} and operation == "update":
            argv += ["--path", item["path"]]
        if group == "knowledge" and item.get("allow_new_domain"):
            argv.append("--allow-new-domain")
        if group == "prompt" and item.get("allow_new_category"):
            argv.append("--allow-new-category")
        if group == "organ" and item.get("allow_new_organ"):
            argv.append("--allow-new-organ")
    if dry_run:
        argv.append("--dry-run")
    return [sys.executable, *argv]


def run_item(item: dict[str, Any], root: Path, dry_run: bool) -> dict[str, Any]:
    group = item["group"]
    label = {"id": item.get("id"), "group": group, "operation": item["operation"],
             "title": item.get("title")}
    if dry_run and group not in DRY_RUN_GROUPS:
        return {**label, "status": "skipped", "detail": f"{group} 写脚本不支持 dry-run，跳过"}

    fd, temp_name = tempfile.mkstemp(prefix="personos-manifest-item-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(item["payload"], handle, ensure_ascii=False)
        proc = subprocess.run(
            build_argv(item, Path(temp_name), root, dry_run),
            capture_output=True, text=True,
        )
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass

    if proc.returncode == 0:
        try:
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            result = proc.stdout.strip()
        return {**label, "status": "applied", "result": result}
    return {**label, "status": "failed",
            "detail": (proc.stderr.strip() or proc.stdout.strip() or f"退出码 {proc.returncode}")}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a confirmed PersonOS capture manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, help="Override manifest root")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate routing and dry-run groups that support it")
    parser.add_argument("--continue-on-error", action="store_true",
                        help="Keep applying remaining items after a failure")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    items = manifest["items"]
    for index, item in enumerate(items):
        validate_item(item, index)  # all-or-nothing on routing before any write

    root = (args.root or Path(manifest.get("root", DEFAULT_ROOT))).resolve()
    results: list[dict[str, Any]] = []
    aborted = False
    for item in items:
        outcome = run_item(item, root, args.dry_run)
        results.append(outcome)
        if outcome["status"] == "failed" and not args.continue_on_error:
            aborted = True
            break

    summary = {
        "root": str(root),
        "dry_run": args.dry_run,
        "total": len(items),
        "applied": sum(r["status"] == "applied" for r in results),
        "failed": sum(r["status"] == "failed" for r in results),
        "skipped": sum(r["status"] == "skipped" for r in results),
        "aborted": aborted,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ManifestError as exc:
        raise SystemExit(f"错误：{exc}")
