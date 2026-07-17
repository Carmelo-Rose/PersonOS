# PersonOS Distill Manifest Schema

`write_manifest.py --input <file>` takes a **JSON array** of items. Each item has a `kind`.
Every item must trace to at least one real case 编号 (形如 `decision_20260614_001`); the writer
rejects any asset without case linkage. All items are validated before anything is written.

Statuses for organ assets (`rule`, `eval_case`): `已验证` / `待验证` / `实验中` / `弃用`.
Confidence for rules: `高` / `中` / `低`. `最后更新日期` is filled by the script (today).

## kind: rule  → new rule in 02_organs/<organ>/rules.md (visual_rules.md for ml_aesthetic)

Byte-compatible with personos-organ-capture output. Rejects a duplicate heading.

```json
{
  "kind": "rule",
  "organ": "ecommerce_judgement",
  "status": "待验证",
  "title": "自动化采集先评估风控再落脚本",
  "applicable_scenario": "...",
  "positive_requirement": "...",
  "avoid": "...",
  "judgment_basis": "...",
  "examples": ["正例：...", "反例：..."],
  "exceptions": "...",
  "confidence": "中",
  "source": ["decision_20260704_001", "decision_20260708_001", "success_20260716_001"],
  "tags": ["电商自动化", "风控"],
  "unresolved": [],
  "rule_id": "（可选）",
  "destination": "（可选，器官目录下单个 .md 文件名）"
}
```

`source` **must** contain at least one real case 编号.

## kind: link_source  → back-link an EXISTING rule to its cases (minimal, safe)

Appends case 编号 to the rule's `用户动作/判断来源` line and refreshes `最后更新日期`. Use this to
close the "organ 未与 case 打通" gap without rewriting the rule.

```json
{
  "kind": "link_source",
  "organ": "coding_judgement",
  "heading": "规则名称：无基础前端动效：分步构建优先",
  "add_source_cases": ["success_20260621_001", "success_20260624_001", "failure_20260619_001"],
  "destination": "（可选）"
}
```

`heading` must match the existing `### ...` heading exactly. `add_source_cases` must contain real
case 编号. Already-present ids are skipped (idempotent).

## kind: eval_case  → append to 02_organs/<organ>/eval_cases.jsonl (per-organ calibration)

```json
{
  "kind": "eval_case",
  "organ": "ml_aesthetic",
  "status": "待验证",
  "title": "...",
  "sample": "路径或对象",
  "expected_classification": "good",
  "expected_score": 8,
  "judgment_reason": ["..."],
  "source": ["success_20260624_001"],
  "tags": ["正例"],
  "notes": "（可选）"
}
```

## kind: system_eval  → append to 06_eval/<target> (system-level evaluation)

`target` ∈ `project_decision_eval.jsonl` / `person_answer_eval.jsonl` / `visual_eval.jsonl`.
`content` holds the eval-specific题面 fields; the script injects 编号 / 来源案例 / 关联规则 /
最后更新日期. `source_cases` must be non-empty real case ids.

```json
{
  "kind": "system_eval",
  "target": "project_decision_eval.jsonl",
  "status": "待验证",
  "title": "未验证需求时先人工流程还是先完整开发",
  "content": {
    "项目情境": "...",
    "约束": ["两周", "一人"],
    "候选方案": ["完整开发", "人工流程验证"],
    "期望决策": "人工流程验证",
    "期望理由": ["先降低需求不确定性"],
    "评测标准": ["选择符合约束", "说明验证目标"]
  },
  "source_cases": ["decision_20260614_001"],
  "linked_rules": ["规则名称：..."],
  "tags": ["产品决策", "MVP"]
}
```

## Notes

- `status` for `system_eval` is a free non-empty string; prefer `待验证` for freshly distilled
  items and reserve `已验证` for tests you have confirmed reflect your judgment.
- Prefer `link_source` before minting new rules — it closes the existing gap at lowest risk.
- Do not hard-code the outcome of a decision case into a `system_eval` beyond what a fair test
  needs; the eval should test judgment, not memory.
