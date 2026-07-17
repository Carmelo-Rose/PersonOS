---
name: personos-profile-promote
description: Promote stable self-model traits into 00_profile only after multiple real cases support them. Use when the user wants to 升格 profile, 提炼稳定偏好, 补 00_profile, turn accumulated cases into preferences / anti-patterns / working-style traits, or strengthen existing profile entries with new evidence. Read-only scan first, count support across cases and projects, propose a candidate board that shows支撑案例数 and 跨项目分布, take one confirmation, then write only selected traits that cross the support threshold. Never write from a single case, never write before confirmation.
---

# PersonOS Profile Promote

Profile is the stable self-model layer — who the user is, what they prefer, what they avoid. A
trait belongs here only after **multiple real cases** confirm it is stable, not a one-off. This
skill is the promotion pass that turns accumulated `04_cases` into `00_profile` entries, and it is
deliberately stricter than the other distillation skills.

This is the third layer of the harvest, alongside case→organ/eval distillation. `04_cases`
accumulate freely; this skill promotes only what has crossed the stability threshold.

Default PersonOS root: `/Users/zhuanzmima0000/Documents/PersonOS`
(scripts auto-detect root by walking up for `04_cases` + `00_profile`, or honor `PERSONOS_ROOT` /
`--root`.)

## Core Rule

One case is evidence, not proof. A profile trait must be supported by at least the support
threshold (default 2, prefer 3) of DISTINCT real cases. Prefer cross-project support: three cases
from one project is weaker than three across projects. Never invent a trait the cases do not
repeatedly show. The user is always the subject.

## Guardrails

- Read-only until confirmation. Only `write_profile.py` writes, only selected items.
- Threshold enforced by the writer: a new anti-pattern or preference row needs ≥ `--min-support`
  distinct real case 编号. Do not try to bypass it.
- Never write `person_profile.md` (identity/goals) or `04_cases`/`00_profile` outside the three
  supported operations. Identity edits are proposed as text for the user to apply manually.
- Prefer cross-project evidence. If a candidate's support is concentrated in one project, say so
  and lower confidence or defer — this directly addresses the profile's own noted risk of
  single-project over-representation.
- Deduplicate against existing anti-pattern headings and decision-preference scenarios before
  proposing. When a trait already exists, prefer `strengthen` (add new cases) over a new entry.
- Distinguish a stable trait from a single strong opinion. If it appears once, it is not profile
  material yet — leave it as a case.
- Do not batch-write. Present the board, take one confirmation, write the frozen manifest, stop.

## Workflow

### 1. Scan (read-only)

```bash
python3 scripts/profile_scan.py --root "<PersonOS root>"
```

Returns: existing profile entries (anti-pattern headings, decision-preference scenarios) and
every case id already cited in profile; the per-case signal text (复盘 / 经验 / 可复用经验 /
选择理由 / 根因 …); tag clusters with their **project distribution** (cross-project first); and the
cases not yet cited anywhere in profile.

### 2. Form candidate traits and count support

Read the signal corpus. Group signals into candidate traits and, for each, collect the DISTINCT
supporting case ids and how many projects they span. Keep only traits at or near the threshold.
Route each to a kind:

- **`anti_pattern`** — a recurring harmful pattern to avoid (fills the anti-pattern template).
- **`preference_row`** — a recurring decision preference (a row in the 决策偏好 table).
- **`strengthen`** — new cases that reinforce an EXISTING anti-pattern; adds evidence instead of a
  duplicate entry. Prefer this whenever the trait already exists.

An ability-map or identity (`person_profile.md`) update is proposed as plain text for the user to
apply by hand — do not write it with the script.

### 3. Present the candidate board

One Chinese board, grouped by kind. For each: kind, 目标文件, 拟定标题/场景, **支撑案例编号**,
**项目数(跨项目?)**, 置信度, 一句话简述. Mark anything below threshold as `暂缓(证据不足)` and
anything single-project as `证据集中，建议再等跨项目案例`. Then offer exactly:
`确认写入 <编号>`、`修改`、`不保存`.

### 4. Freeze the manifest

Build a JSON array of the selected items using `references/profile-schema.md`. Write to a temp
file. Do not change payloads after confirmation.

### 5. Write

```bash
python3 scripts/write_profile.py --input /tmp/pmanifest.json --root "<PersonOS root>" --dry-run
python3 scripts/write_profile.py --input /tmp/pmanifest.json --root "<PersonOS root>"
```

Raise `--min-support` (e.g. 3) for a stricter bar. The writer validates all items first, rejects
under-supported traits and duplicates, and appends entries with today's review date.

### 6. Report

Summarize which traits were promoted, with which supporting cases, and note any deferred
candidates (below threshold or single-project) so a later run can revisit once more cases arrive.

## Output Boundary

This skill reads `04_cases` and writes only the three supported operations in `00_profile`, only
after confirmation, and only for traits that cross the support threshold. It never writes identity
facts, never promotes from a single case, and never treats its own proposal as confirmed.
