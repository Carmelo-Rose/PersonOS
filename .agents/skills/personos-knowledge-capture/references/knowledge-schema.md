# PersonOS Knowledge Schema

## Destination

Write one Markdown file per knowledge asset:

`03_knowledge/<domain>/<slug>.md`

Known domains are the existing subdirectories under `03_knowledge/`. Create a new domain only
when the user explicitly confirms it.

## Required Fields

Confirmed JSON input for `write_knowledge.py` must contain:

- `title`: human-readable title.
- `status`: `已验证`, `待验证`, or `过时`.
- `type`: concise type such as `方法`, `原则`, `工具用法`, `术语`, `架构判断`, or `最佳实践`.
- `domain`: destination domain folder name.
- `source`: non-empty array describing the user actions, judgments, corrections, or artifacts
  that produced this knowledge.
- `applicable_conditions`: array describing when the user should reuse this knowledge.
- `staleness_risk`: string.
- `core_content`: string or array preserving the reusable content and how it affects later
  user judgment or action.
- `boundaries`: array of limits, exceptions, or situations where the user's judgment should
  change.
- `related`: array; use `[]` when none.
- `tags`: array.
- `last_updated`: `YYYY-MM-DD`.

Optional fields:

- `unresolved`: array.
- `slug`: explicit filename slug without `.md`.

## Status Policy

- `已验证`: supported by user confirmation, observed use, or cited artifact.
- `待验证`: useful but not yet validated or missing an important result.
- `过时`: preserved for history but not recommended for current use.

## New Versus Update

- New entry: no `--path`; script writes to a slug under the selected domain and rejects an
  existing destination.
- Update: pass exact `--path`; script replaces that exact Markdown file after validation.
- Do not update by title search. If multiple related entries exist, ask the user which exact
  path to update.

## Readable Draft

Before writing, show:

- 标题 / 状态 / 类型 / 领域
- 用户动作/判断来源
- 适用条件
- 核心内容
- 边界与例外
- 失效风险
- 关联项
- 标签
- 待确认或待验证
- 操作与目标路径

If removing the user's actions and judgments leaves a generic encyclopedia entry, rewrite the
draft before asking for confirmation.

Then offer exactly: `确认写入`, `修改`, `不保存`.
