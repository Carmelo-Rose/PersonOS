---
name: personos-session-capture
description: Capture the current conversation or working session into PersonOS in one pass. Use when the user says "记录这次", wants to capture the current session, asks to 沉淀到 PersonOS, or wants one-call routing across cases, knowledge, prompts, organs, and profile candidates. Extract all meaningful capture objects, run deduplication, draft each to schema granularity, present one unified candidate board, take a single confirmation, then write the confirmed items deterministically by dispatching a frozen manifest to the specialist write scripts. Never write directly, never write before confirmation, and never batch-write items the user did not select.
---

# PersonOS Session Capture

The single front door for recording the current session into PersonOS. It turns one session
into a cross-group candidate board, takes a single confirmation, then writes the confirmed
items deterministically — each frozen item is dispatched to a specialist write script, so the
model never re-derives content at write time. That determinism is what prevents capture drift.

Default PersonOS root:
`/Users/zhuanzmima0000/Documents/PersonOS`

## Two Capture Paths

- **Batch (default for "记录这次")**: extract all candidates, dedup, draft to schema
  granularity, show one unified board, take one confirmation, freeze a manifest, and apply it
  with `apply_manifest.py`. Writes go straight through the specialist scripts. Use this whenever
  the user wants to record the current session.
- **Interactive deep capture**: for a single object that needs an interview, reconstruction, or
  careful new-versus-update reasoning, invoke the specialist skill directly
  (`personos-cases-capture`, `personos-knowledge-capture`, `personos-prompt-capture`,
  `personos-organ-capture`). Those skills are unchanged and own the deep single-object flow.

## Core Rule

The user is always the subject. Capture what the user tried to achieve, did, noticed, judged,
decided, rejected, corrected, approved, and learned. Agents, tools, code, and technical events
may appear only as background, evidence, or results.

## Guardrails

- Never write to PersonOS directly. All writes go through the specialist scripts via
  `apply_manifest.py`, and only after explicit confirmation.
- One confirmation gate by default: the candidate board is the confirmation. After the user
  confirms, items that did not materially change are written without asking again.
- Re-confirm only items that **materially change** after schema drafting. Material change means:
  target group/type/destination/title/core content changes; one item splits into several or
  several merge into one; a dedup hit now requires update/merge/overwrite of an existing record;
  a conflict, missing evidence, privacy/sensitive content, or a status drop from verified to
  unverified appears; or a schema field would require a judgment the user has not confirmed.
- Exclude secrets, credentials, private keys, tokens, `.env` contents, dependency trees, caches,
  generated artifacts, and unrelated private data.
- `00_profile` is candidate-only. Never write a profile entry from a session; one session is
  evidence, not proof of a stable trait.
- Before drafting any item, mentally remove agent and tool names. If the user's action,
  judgment, and lesson are no longer clear, rewrite the draft or drop the candidate.
- Do not force a capture from a session with no meaningful user action, reusable knowledge,
  prompt asset, judgment rule, or profile signal.

## Workflow

### 1. Inspect The Session

Review the conversation and any supplied artifact. Identify every concrete moment where the
user set or changed a goal, selected/rejected/corrected an option, imposed a quality/safety/
approval boundary, supplied missing context, approved/stopped/redirected/verified work, or
produced a reusable method, prompt, rule, or long-term signal. Note observed results and
unresolved questions.

### 2. Extract And Route All Candidates

List every meaningful capture object — not just one — and assign each a target group:

- **`04_cases`** (`decision` / `failure` / `success` / `project`): concrete user events,
  decisions, failures, successes, project episodes, follow-up results.
- **`03_knowledge`**: reusable methods, principles, tool usage, terminology, architecture
  judgment, best practices.
- **`05_prompts`**: durable prompt assets, invocation wording, collaboration workflows, input
  requirements, output formats, tested prompt versions.
- **`02_organs`**: stable judgment rules, rubrics, classifiers, calibration/eval/boundary cases.
- **`00_profile`** (candidate only): possible stable preferences, anti-patterns, ability
  boundaries, or background facts. Never written here.

When a concrete event and a reusable principle both exist, default to a `04_cases` event unless
the user explicitly wants the principle, prompt, or rule itself saved.

### 3. Deduplicate — Decide New Versus Update Deterministically

Before drafting, search existing records so new-versus-update is grounded, not guessed. Run the
matching read-only finder per candidate:

```bash
python3 ~/.codex/skills/personos-cases-capture/scripts/find_cases.py --root <ROOT> --project "<name>"
python3 ~/.codex/skills/personos-knowledge-capture/scripts/find_knowledge.py --root <ROOT> --query "<keywords>"
python3 ~/.codex/skills/personos-prompt-capture/scripts/find_prompts.py --root <ROOT> --query "<keywords>"
python3 ~/.codex/skills/personos-organ-capture/scripts/find_organs.py --root <ROOT> --query "<keywords>"
```

For each candidate record the operation (`新增` or `更新 <id/path/heading>`), the target, and a
one-line dedupe result. When a likely match exists, default to update and name the exact target.

### 4. Draft Each Candidate To Schema Granularity

Read the matching schema reference before drafting each candidate, then fill that specialist's
required fields:

- `personos-cases-capture/references/case-schemas.md`
- `personos-knowledge-capture/references/knowledge-schema.md`
- `personos-prompt-capture/references/prompt-schema.md`
- `personos-organ-capture/references/organ-schema.md`

Keep the user as the subject. Put every uncertainty in `待验证项` / `unresolved`; never invent a
fact, motive, result, or lesson the user did not state or demonstrate. For a new `03_knowledge`
or `05_prompts` item, choose a stable English `slug` now and carry it in the payload; do not rely
on auto-slugify, because a Chinese title falls back to a date-based filename.

### 5. Present The Unified Candidate Board

Show one concise Chinese board, one row per candidate, at draft-preview granularity:

```text
类型 | 拟定标题 | 目标组 + 目标文件/ID | 操作(新增 / 更新<目标>) + 依据 | 一行内容预览 | 关键证据 | 未决项 | 查重结果
```

For `03_knowledge` and `05_prompts`, show the final destination path including the slug — not just
the title — so the user confirms what actually lands on disk.

End the board with: `确认后，未发生实质变化的条目将直接写入；发生实质变化的条目会单独再确认。`
List any `00_profile` candidates separately, marked `仅候选，不写入`.

### 6. Take One Confirmation

Ask which items to `写入` / `暂缓` / `修改`. Accept a single batch reply such as
`写入 1、3，暂缓 2`. On `修改`, revise that row and re-show the board. Do not write anything
until the user confirms.

### 7. Freeze The Manifest

For confirmed items only, build a frozen manifest JSON in a temporary file, matching the shape
`apply_manifest.py` expects. Do not change any payload after the user confirmed it.

```json
{
  "schema_version": "1",
  "root": "/Users/zhuanzmima0000/Documents/PersonOS",
  "items": [
    {
      "id": "item-1",
      "group": "cases",
      "operation": "create",
      "case_type": "decision",
      "title": "…",
      "evidence": ["…"],
      "dedupe_result": "无匹配",
      "payload": { "状态": "真实/待验证", "发生日期": "…", "项目": "…", "...": "schema 字段" }
    },
    {
      "id": "item-2",
      "group": "knowledge",
      "operation": "update",
      "path": "03_knowledge/ai_agent/<slug>.md",
      "payload": { "title": "…", "status": "已验证", "...": "schema 字段" }
    }
  ]
}
```

Routing fields by group: cases create needs `case_type`; cases update needs `target_id`;
knowledge/prompt update needs `path`; new domain/category/organ needs `allow_new_domain` /
`allow_new_category` / `allow_new_organ`. Organ new-versus-update is decided by whether the
payload contains `heading`. A new `03_knowledge` / `05_prompts` payload should include an explicit
`slug` so the destination filename matches what the board showed.

### 8. Apply Deterministically

Run once. Optionally pass `--dry-run` first to preflight every item; all four groups support it.

```bash
python3 ~/.codex/skills/personos-session-capture/scripts/apply_manifest.py \
  --manifest <frozen-manifest.json> \
  --root /Users/zhuanzmima0000/Documents/PersonOS
```

If this skill is installed in another agent, use that agent's local
`personos-session-capture/scripts/apply_manifest.py` path. Remove the temporary manifest file
after the command finishes.

### 9. Report And Escalate

Report each item's result (operation, generated id, or destination) from the `apply_manifest.py`
output. Hand a single item to its specialist skill (interactive path) instead of forcing the
batch write when the script rejected it (schema, duplicate, missing path, ambiguous id), when
the item materially changed during drafting, or when it needs an interview or reconstruction.
Re-run only the remaining items if needed.

Stop when every confirmed item is written or handed off and the user has nothing else to save.

## Output Boundary

This skill handles intake, routing, deduplication, the candidate board, the single confirmation,
and deterministic dispatch. It never writes PersonOS files itself; all writes go through the
specialist scripts via `apply_manifest.py` after explicit confirmation. `00_profile` is never
written from a session.
