---
name: personos-knowledge-capture
description: Capture reusable PersonOS knowledge into 03_knowledge from conversations, artifacts, project work, or explicit notes. Use when the user wants to preserve methods, principles, tool usage, terminology, architecture judgment, best practices, or other reusable knowledge that is not primarily a concrete event, prompt, or organ rule. Inspect existing knowledge, avoid duplicates, interview with low effort, show a readable draft, and write only after explicit confirmation.
---

# PersonOS Knowledge Capture

Capture one reusable knowledge asset at a time into `03_knowledge/<domain>/<slug>.md`.

Default PersonOS root:
`PERSONOS_ROOT` if set; otherwise use a platform-aware local default:
`D:\workspace\PersonOS` on Windows when that directory exists, else `~/Documents/PersonOS`

Read [references/knowledge-schema.md](references/knowledge-schema.md) before drafting or writing.

## Boundaries

- The user is always the source subject of a PersonOS knowledge record. Record what the user confirmed, corrected, used, rejected, or decided, not just the resulting fact.
- Use this skill for reusable methods, principles, tool usage, terminology, architecture judgment, and best practices.
- `03_knowledge` is not an encyclopedia. Preserve the context where the user confirmed the knowledge and how it should affect later user judgment or action.
- Use `personos-cases-capture` instead when the subject is a concrete event, result, or follow-up.
- Use `personos-prompt-capture` when the durable artifact is a prompt.
- Use `personos-organ-capture` when the durable artifact is a stable judgment rule, scoring standard, or eval/boundary case.
- Never modify `00_profile/` or `04_cases/`.
- Never promote one conversation directly into a stable profile, preference, or anti-pattern.
- Never write before the user explicitly chooses `确认写入`.
- Capture at most one primary knowledge asset per invocation.
- Exclude secrets, credentials, `.env` contents, private keys, tokens, unrelated private data, caches, dependency trees, and generated artifacts.
- Every draft must contain `用户动作/判断来源`. If deleting the user's actions and judgments leaves a generic article, rewrite before presenting the draft.

## Workflow

### 1. Locate Existing Context

Inspect current conversation or supplied artifact first. Then inspect a small relevant subset of
`03_knowledge/`, especially existing domain README files and likely related entries.

Default domains:

- `ai_agent`
- `automation`
- `backend`
- `frontend`
- `ecommerce`
- `video_content`

Create a new domain only after the user confirms it. Otherwise choose the closest existing
domain and record boundary uncertainty in the draft.

### 2. Decide New Or Update

Recommend:

- **Update** when the existing entry already covers the same reusable knowledge and the new material clarifies status, source, boundary, validation, or stale risk.
- **New** when the knowledge has a distinct title, use case, or reusable lesson.
- **Do not save** when the material is only a transient task note or unsupported guess.

Use exact destination path for updates. Never silently merge ambiguous matches.

### 3. Interview With Low Effort

Ask one question at a time only when a required field or important boundary is unclear.
Prefer concrete options grounded in evidence.

Useful question patterns:

- `这条知识主要应该归到 ai_agent、automation，还是另一个领域？`
- `它现在更像已验证方法、待验证判断，还是可能会过时的规则？`
- `用户是在什么上下文中确认、纠偏或使用了这条知识？`
- `最重要的适用边界是哪一个？`

### 4. Present A Readable Draft

Show a concise Chinese draft containing:

- title, status, type, domain, destination
- 用户动作/判断来源
- applicable conditions
- core content
- boundaries and exceptions
- failure or staleness risk
- related cases or prompts
- tags and unresolved items
- operation: `新增` or `更新 <path>`

Before showing the draft, check that `source`, `core_content`, `applicable_conditions`, and
`boundaries` preserve why this knowledge matters to the user's later judgment or action.

Then offer exactly: `确认写入`, `修改`, `不保存`.

If the user chooses `修改`, revise and present the readable draft again. If the user chooses
`不保存`, stop without writing.

### 5. Write After Confirmation

Create a temporary JSON object with the confirmed fields. For new entries:

```bash
python3 ~/.codex/skills/personos-knowledge-capture/scripts/write_knowledge.py \
  --input <confirmed-object.json> \
  --root <your PersonOS root>
```

For updates, pass the exact destination:

```bash
python3 ~/.codex/skills/personos-knowledge-capture/scripts/write_knowledge.py \
  --input <confirmed-object.json> \
  --path 03_knowledge/<domain>/<slug>.md \
  --root <your PersonOS root>
```

If this skill is installed in another Agent, use that Agent's local
`personos-knowledge-capture/scripts/write_knowledge.py` path instead of assuming the current
working directory is the PersonOS repository.

Use `--allow-new-domain` only after the user confirms a new domain. Use `--dry-run` before
writing when the destination is uncertain. Remove temporary input files after success or failure.

Report the destination path and whether the entry was added or updated.
