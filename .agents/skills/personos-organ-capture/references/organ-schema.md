# PersonOS Organ Schema

## Destination

Write judgment assets under:

`02_organs/<organ>/`

Known organs are the existing subdirectories under `02_organs/`. Create a new organ only when
the user explicitly confirms it.

## Asset Kinds

Confirmed JSON input for `write_organ.py` must contain `kind` with one of:

- `rule`
- `rubric`
- `eval_case`

Common required fields:

- `organ`: destination organ folder name.
- `status`: `已验证`, `待验证`, `实验中`, or `弃用`.
- `title`: human-readable asset title.
- `source`: non-empty array naming the user cases, judgments, corrections, artifacts, or
  calibration moments behind this asset.
- `tags`: array.
- `last_updated`: `YYYY-MM-DD`.

## Rule Fields

Required for `kind: rule`:

- `applicable_scenario`: string.
- `positive_requirement`: string.
- `avoid`: string.
- `judgment_basis`: string.
- `examples`: array, preferably user-confirmed positive, negative, or boundary examples.
- `exceptions`: string.
- `confidence`: `高`, `中`, or `低`.

Optional:

- `rule_id`: explicit ID.
- `destination`: explicit Markdown filename, relative to the organ directory.
- `heading`: exact heading to update.

Default destination is `visual_rules.md` for `ml_aesthetic`, otherwise `rules.md`.

## Rubric Fields

Required for `kind: rubric`:

- `rubric_content`: string.
- `applicable_scenario`: string.
- `change_reason`: string.

Optional:

- `destination`: explicit Markdown filename, relative to the organ directory.
- `heading`: exact heading to update.

Default destination is `scoring_rubric.md`.

## Eval Case Fields

Required for `kind: eval_case`:

- `sample`: string or object.
- `expected_classification`: string.
- `expected_score`: number or string.
- `judgment_reason`: array.

Optional:

- `notes`: string.
- `destination`: explicit JSONL filename, relative to the organ directory.

Default destination is `eval_cases.jsonl`.

## New Versus Update

- New rule or rubric: omit `heading`; the script appends a new heading and rejects duplicates.
- Update rule or rubric: pass exact `heading`; the script replaces only that heading section.
- Eval cases are append-only and receive generated IDs.

## Readable Draft

Before writing, show:

- 器官 / 资产类型 / 状态 / 目标路径
- 标题
- 用户动作/判断来源
- 适用场景和边界
- 规则、评分标准或样本
- 预期分类与评分
- 依据、例外、置信度
- 标签
- 待确认或待验证
- 操作

If removing the user's actions and judgments leaves an abstract rule, rubric, or test case
detached from evidence, rewrite the draft before asking for confirmation.

Then offer exactly: `确认写入`, `修改`, `不保存`.
