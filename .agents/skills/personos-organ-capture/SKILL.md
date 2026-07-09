---
name: personos-organ-capture
description: Capture stable PersonOS judgment assets into 02_organs, including decision rules, scoring rubric updates, and eval or boundary cases. Use when the user wants to preserve a stable classifier, rule, scoring standard, positive or negative example, edge case, visual judgment, coding judgment, ecommerce judgment, or product MVP judgment. Inspect existing organs, avoid duplicates, interview with low effort, show a readable draft, and write only after explicit confirmation.
---

# PersonOS Organ Capture

Capture one judgment asset at a time into `02_organs/<organ>/`.

Default PersonOS root:
`PERSONOS_ROOT` if set; otherwise use a platform-aware local default:
`D:\workspace\PersonOS` on Windows when that directory exists, else `~/Documents/PersonOS`

Read [references/organ-schema.md](references/organ-schema.md) before drafting or writing.

## Boundaries

- The user is always the source subject of a PersonOS organ record. Record which user cases, judgments, corrections, or calibration moments produced the rule, rubric, or eval case.
- Use this skill for stable judgment rules, scoring standards, classifiers, evaluation cases, and boundary examples.
- `02_organs` is not a place to invent abstract rules. Preserve the user evidence behind each judgment asset and the calibration path that made it stable enough to save.
- Use `personos-knowledge-capture` for general methods or tool usage.
- Use `personos-prompt-capture` for prompt text and invocation wording.
- Use `personos-cases-capture` for concrete project events and results.
- Never modify `00_profile/` or `04_cases/`.
- Never promote one conversation directly into a stable profile, preference, or anti-pattern.
- Never write before the user explicitly chooses `确认写入`.
- Capture at most one primary organ asset per invocation.
- Exclude secrets, credentials, `.env` contents, private keys, tokens, unrelated private data, caches, dependency trees, and generated artifacts.
- Every draft must contain `用户动作/判断来源`. If deleting the user's actions and judgments leaves an abstract rule or rubric detached from evidence, rewrite before presenting the draft.

## Workflow

### 1. Locate Existing Context

Inspect current conversation or supplied artifact first. Then inspect a small relevant subset of
`02_organs/`, especially organ README files and likely related rules, rubrics, and eval cases.

Default organs:

- `coding_judgement`
- `ecommerce_judgement`
- `ml_aesthetic`
- `product_mvp_judgement`

Create a new organ only after the user confirms it. Otherwise choose the closest existing
organ and record boundary uncertainty in the draft.

### 2. Choose Asset Kind

Choose exactly one:

- **Rule**: a stable criterion, classifier, boundary, or should/avoid rule.
- **Rubric**: a scoring standard or rubric section update.
- **Eval case**: a positive, negative, or boundary sample with expected judgment.

For `ml_aesthetic`, prefer existing destinations:

- rules: `visual_rules.md`
- rubric: `scoring_rubric.md`
- eval cases: `eval_cases.jsonl`

For other organs, use `rules.md` and `eval_cases.jsonl`, creating them only when first needed.

### 3. Decide New Or Update

Recommend:

- **Update** when the existing rule/rubric already covers the same judgment and the new material changes boundary, confidence, examples, or calibration.
- **New** when the judgment asset is distinct.
- **Do not save** when the judgment is speculative, one-off, or not stable enough for an organ.

Use exact destination path or heading for updates. Never silently merge ambiguous matches.

### 4. Interview With Low Effort

Ask one question at a time only when a required field or important boundary is unclear.
Prefer concrete options grounded in evidence.

Useful question patterns:

- `这条判断更适合做规则、评分量表，还是边界评测样本？`
- `它应该归到 coding_judgement、product_mvp_judgement，还是另一个器官？`
- `用户是从哪些案例、判断或纠偏中提炼出它的？`
- `这个规则的允许例外是什么？`

### 5. Present A Readable Draft

Show a concise Chinese draft containing:

- organ, asset kind, status, destination
- rule/rubric/case title
- 用户动作/判断来源
- applicable scenario and boundary
- positive requirement and avoid condition, when relevant
- evidence and examples
- confidence or expected score/classification
- unresolved items
- operation: `新增`, `更新 <path#heading>`, or `追加 eval case`

Before showing the draft, check that `source`, `judgment_basis`, `examples`,
`change_reason`, or `judgment_reason` connect the asset to user cases, judgments, corrections,
or calibration moments.

Then offer exactly: `确认写入`, `修改`, `不保存`.

If the user chooses `修改`, revise and present the readable draft again. If the user chooses
`不保存`, stop without writing.

### 6. Write After Confirmation

Create a temporary JSON object with the confirmed fields. Run:

```bash
python3 ~/.codex/skills/personos-organ-capture/scripts/write_organ.py \
  --input <confirmed-object.json> \
  --root <your PersonOS root>
```

If this skill is installed in another Agent, use that Agent's local
`personos-organ-capture/scripts/write_organ.py` path instead of assuming the current working
directory is the PersonOS repository.

Use `--allow-new-organ` only after the user confirms a new organ. Use `--dry-run` before
writing when the destination is uncertain. Remove temporary input files after success or
failure. Report the destination path and whether the asset was added or updated.
