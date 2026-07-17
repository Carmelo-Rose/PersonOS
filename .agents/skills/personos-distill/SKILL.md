---
name: personos-distill
description: Distill accumulated 04_cases into 02_organs judgment rules and 06_eval evaluation cases, and back-link existing organ rules to the real cases behind them. Use when the user wants to 蒸馏案例, 从案例提炼规则, 整理已有案例, 打通 organs 与 cases, 补齐 06_eval, 生成评测题, or periodically harvest scattered cases into stable judgment assets. Read-only scan first, propose a candidate board grouped by gap, take one confirmation, then write only the selected items with enforced case traceability. Never write directly, never write before confirmation.
---

# PersonOS Distill

The five capture skills push single sessions *down* into PersonOS (one case, one note at a
time). This skill pulls the accumulated cases *up*: it reads the whole `04_cases` pile, finds
repeated patterns and cross-reference gaps, and proposes stable `02_organs` rules and `06_eval`
evaluation cases — each traceable back to the real cases that justify it.

Distillation is the aggregation layer. It exists because a rule or an eval set is distilled
*across many cases*, which a single-session intake skill structurally cannot produce.

Default PersonOS root: `/Users/zhuanzmima0000/Documents/PersonOS`
(scripts auto-detect the root by walking up for a folder containing `04_cases` and `02_organs`,
or honor `PERSONOS_ROOT` / `--root`.)

## Core Rule

The user is always the subject. A distilled rule or eval case must encode *the user's* repeated
judgment, correction, or decision — never a generic best practice. Every asset must cite the real
case 编号 it came from. If removing the case citations leaves an abstract rule with no evidence,
do not propose it.

## Guardrails

- Read-only until confirmation. Only `write_manifest.py` writes, and only the items the user
  selected.
- Never modify `04_cases/` or `00_profile/`. Distillation reads cases; it does not edit them.
- Every proposed rule / eval case must trace to at least one real case 编号. The writer rejects
  any asset without case linkage — do not try to bypass it.
- Propose from evidence, not ambition. A rule needs either repeated cases (≥2 supporting) or one
  strong, explicit user correction. Mark confidence accordingly (`高`/`中`/`低`).
- Never invent a judgment, motive, or lesson the cases do not show.
- Deduplicate against existing organ headings and existing eval before proposing.
- Do not batch-write. Present the board, take one selection, write the frozen manifest, stop.

## Workflow

### 1. Scan (read-only)

Run the scan and read its JSON:

```bash
python3 scripts/scan_cases.py --root "<PersonOS root>"
```

It returns: all real cases (id / type / project / tags / one-line), every organ rule with the
cases it already cites, and the gaps — `未引用任何案例的规则` and `尚无eval的决策案例` — plus
tag/project clusters (≥2 cases) as clustering seeds.

### 2. Cluster and identify candidates

Read the cases and the clusters. Look for:

- **Repeated pattern → new rule.** Two or more cases where the user made the same kind of
  judgment or correction (e.g. several 前端动效 successes/failures around 分步构建). Propose a
  `rule` in the most fitting existing organ, `source` = those case 编号.
- **Existing rule missing its evidence → `link_source`.** A rule in `未引用任何案例的规则` whose
  real supporting cases now exist. Propose a `link_source` to back-link it. This is the cheapest,
  highest-value move for the current top-heavy state — do it first.
- **Real decision with no eval → `system_eval`.** A decision case in `尚无eval的决策案例` that
  encodes a judgment worth testing. Rewrite it as a `project_decision_eval` item (情境 / 约束 /
  候选方案 / 期望决策 / 期望理由 / 评测标准), `source_cases` = that case id. Do not leak the
  original outcome as a hint beyond what a fair test needs.
- **Per-organ calibration sample → `eval_case`.** A case that makes a good positive/negative/
  boundary sample for a specific organ (e.g. `ml_aesthetic`).

Keep proposals grounded: prefer `link_source` and a small number of high-confidence rules over a
long speculative list. Default to at most ~6 candidates per run unless the user asks for more.

### 3. Present the candidate board

Show one readable Chinese board, grouped by kind, e.g.:

```text
【补挂案例 link_source】(打通存量，最低风险)
  1. coding_judgement/rules.md「分步构建优先」← success_20260621_001, success_20260624_001, failure_20260619_001

【新增规则 rule】
  2. ecommerce_judgement「自动化采集先评估风控再落脚本」
     依据案例: decision_20260704_001, decision_20260708_001, success_20260716_001  置信度: 中

【系统评测 system_eval → 06_eval/project_decision_eval.jsonl】
  3. 「未验证需求时先人工流程还是先完整开发」← decision_20260614_001
```

For each item show: kind, 目标器官/文件, 标题, 依据案例编号, 置信度（规则）, 简述. Then offer
exactly: `确认写入 <编号列表>`、`修改`、`不保存`.

### 4. Take one confirmation and freeze the manifest

Only the items the user names get written. Build a frozen manifest JSON array from the selected
items using the field contract in `references/distill-schema.md`. Write it to a temp file.

### 5. Write

Dry-run first, then write:

```bash
python3 scripts/write_manifest.py --input /tmp/manifest.json --root "<PersonOS root>" --dry-run
python3 scripts/write_manifest.py --input /tmp/manifest.json --root "<PersonOS root>"
```

The writer validates every item before writing anything, renders rules byte-compatible with the
organ-capture format, appends eval cases with generated IDs, and refuses any asset without case
linkage.

### 6. Report

Summarize what was written and the new cross-links created (which rules now cite which cases,
which eval cases were added and from which decision). Note any candidates the user deferred so a
later run can pick them up.

## Output Boundary

This skill reads `04_cases` and writes only `02_organs` and `06_eval`, only after explicit
confirmation, and only with case traceability. It never edits cases or profile, and never treats
its own proposal as confirmed.
