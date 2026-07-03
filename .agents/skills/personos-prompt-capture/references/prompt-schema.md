# PersonOS Prompt Schema

## Destination

Write one Markdown file per prompt asset:

`05_prompts/<category>/<slug>.md`

Known categories are the existing subdirectories under `05_prompts/`. Create a new category
only when the user explicitly confirms it.

## Required Fields

Confirmed JSON input for `write_prompt.py` must contain:

- `title`: human-readable prompt name.
- `status`: `已验证`, `待验证`, `实验中`, or `弃用`.
- `category`: destination category folder name.
- `source`: non-empty array describing why the user accepted, corrected, reused, or validated
  this prompt or usage pattern.
- `tool_or_scenario`: target tool, agent, workflow, or use scenario.
- `version`: version string such as `v1`.
- `prompt_body`: reusable prompt text.
- `input_requirements`: array.
- `output_format`: string or array.
- `success_criteria`: array.
- `validation_result`: string describing observed outcome or what remains unverified.
- `applicable_boundary`: array describing where the user's approval applies and where it does not.
- `change_reason`: string explaining why this prompt version deserves to be saved.
- `tags`: array.
- `last_updated`: `YYYY-MM-DD`.

Optional fields:

- `unresolved`: array.
- `slug`: explicit filename slug without `.md`.
- `history`: array of version notes.

## Status Policy

- `已验证`: observed to work or confirmed by the user with a result.
- `待验证`: reusable but not yet tested.
- `实验中`: actively being tried; expect changes.
- `弃用`: retained for history and comparison, not recommended.

## New Versus Update

- New prompt: no `--path`; script writes to a slug under the selected category and rejects an
  existing destination.
- Update: pass exact `--path`; script replaces that exact Markdown file after validation.
- Preserve useful version history in `history` or `change_reason`; do not overwrite provenance
  silently.

## Prompt Body

The script writes `prompt_body` inside a fenced `text` block. Do not put secrets or private
runtime values in the prompt body.
Do not save a prompt body without its user judgment provenance.

## Readable Draft

Before writing, show:

- 标题 / 状态 / 分类 / 目标工具或场景
- 用户动作/判断来源
- 版本与变更原因
- 输入要求
- 输出格式
- 成功标准与验证结果
- 适用边界
- 提示词正文摘要或全文
- 标签
- 待确认或待验证
- 操作与目标路径

If removing the user's actions and judgments leaves a generic prompt-library entry, rewrite
the draft before asking for confirmation.

Then offer exactly: `确认写入`, `修改`, `不保存`.
