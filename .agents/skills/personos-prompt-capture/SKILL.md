---
name: personos-prompt-capture
description: Capture reusable prompts into PersonOS 05_prompts from conversations, working prompt drafts, agent instructions, review rubrics, or tool usage workflows. Use when the user wants to preserve a prompt, prompt pattern, Agent invocation wording, collaboration workflow, code-review prompt, or prompt version with usage results. Inspect existing prompts, avoid duplicates, interview with low effort, show a readable draft, and write only after explicit confirmation.
---

# PersonOS Prompt Capture

Capture one reusable prompt asset at a time into `05_prompts/<category>/<slug>.md`.

Default PersonOS root:
`PERSONOS_ROOT` if set; otherwise use a platform-aware local default:
`D:\workspace\PersonOS` on Windows when that directory exists, else `~/Documents/PersonOS`

Read [references/prompt-schema.md](references/prompt-schema.md) before drafting or writing.

## Boundaries

- The user is always the source subject of a PersonOS prompt record. Record why the user accepted, corrected, or reused the prompt pattern.
- Use this skill for durable prompt text, prompt patterns, invocation wording, Agent collaboration instructions, and review prompts.
- `05_prompts` is not a generic prompt library. Preserve the user's reason for recognizing the prompt as reusable, its validated scenario, and its boundaries.
- Use `personos-knowledge-capture` when the useful artifact is a method or principle, not prompt text.
- Use `personos-organ-capture` when the useful artifact is a judgment rule, rubric, or eval case.
- Use `personos-cases-capture` when the subject is a concrete event or result.
- Never modify `00_profile/` or `04_cases/`.
- Never promote one conversation directly into a stable profile, preference, or anti-pattern.
- Never write before the user explicitly chooses `确认写入`.
- Capture at most one primary prompt asset per invocation.
- Exclude secrets, credentials, `.env` contents, private keys, tokens, unrelated private data, caches, dependency trees, and generated artifacts.
- Every draft must contain `用户动作/判断来源`. If deleting the user's actions and judgments leaves a generic prompt template, rewrite before presenting the draft.

## Workflow

### 1. Locate Existing Context

Inspect current conversation or supplied artifact first. Then inspect a small relevant subset of
`05_prompts/`, especially category README files and likely related prompt entries.

Default categories:

- `agent_prompts`
- `codex_prompts`
- `claude_code_prompts`
- `review_prompts`

Create a new category only after the user confirms it. Otherwise choose the closest existing
category and record boundary uncertainty in the draft.

### 2. Decide New Or Update

Recommend:

- **Update** when an existing prompt is the same asset and the new material changes version, validation, boundaries, or usage notes.
- **New** when the prompt has a distinct task, tool, audience, or output contract.
- **Do not save** when the prompt is one-off, contains private data, or lacks enough reusable structure.

Use exact destination path for updates. Never silently merge ambiguous matches.

### 3. Interview With Low Effort

Ask one question at a time only when a required field or important boundary is unclear.
Prefer concrete options grounded in evidence.

Useful question patterns:

- `这个提示词主要用于 Codex、Claude Code、通用 Agent，还是审查任务？`
- `这个版本是已验证、实验中，还是还待验证？`
- `用户为什么认可这个提示词或用法值得沉淀？`
- `它最重要的输入前提或禁止事项是什么？`

### 4. Present A Readable Draft

Show a concise Chinese draft containing:

- title, status, category, destination
- 用户动作/判断来源
- tool or scenario
- version and change reason
- input requirements
- output format
- success criteria and validation result
- applicable boundary
- prompt body summary or full body if short
- tags and unresolved items
- operation: `新增` or `更新 <path>`

Before showing the draft, check that `source`, `change_reason`, `validation_result`, and
`applicable_boundary` explain why the user accepted the prompt, where it applies, and what
remains unverified.

Then offer exactly: `确认写入`, `修改`, `不保存`.

If the user chooses `修改`, revise and present the readable draft again. If the user chooses
`不保存`, stop without writing.

### 5. Write After Confirmation

Create a temporary JSON object with the confirmed fields. For new entries:

```bash
python3 /Users/zhuanzmima0000/.codex/skills/personos-prompt-capture/scripts/write_prompt.py \
  --input <confirmed-object.json> \
  --root <your PersonOS root>
```

For updates, pass the exact destination:

```bash
python3 /Users/zhuanzmima0000/.codex/skills/personos-prompt-capture/scripts/write_prompt.py \
  --input <confirmed-object.json> \
  --path 05_prompts/<category>/<slug>.md \
  --root <your PersonOS root>
```

If this skill is installed in another Agent, use that Agent's local
`personos-prompt-capture/scripts/write_prompt.py` path instead of assuming the current working
directory is the PersonOS repository.

Use `--allow-new-category` only after the user confirms a new category. Use `--dry-run`
before writing when the destination is uncertain. Remove temporary input files after success
or failure. Report the destination path and whether the prompt was added or updated.
