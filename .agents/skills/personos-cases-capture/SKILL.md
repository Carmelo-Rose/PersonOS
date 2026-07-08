---
name: personos-cases-capture
description: Capture, update, or connect one real PersonOS case in 04_cases from a concrete project event, historical project, or supplied artifact. Use when the user wants to record real experience, decisions, successes, failures, project history, follow-up results, or asks to write a confirmed event into PersonOS cases. Inspect related cases, conduct a low-effort option-first interview, show a readable draft, and write only after explicit confirmation.
---

# PersonOS Cases Capture

Capture one verifiable event or one follow-up result at a time. Treat the event and its
evidence as the subject of the interview; do not begin with broad questions about the user's
personality or preferences.

Default PersonOS root:
`PERSONOS_ROOT` if set; otherwise use a platform-aware local default:
`D:\workspace\PersonOS` on Windows when that directory exists, else `~/Documents/PersonOS`

Read [references/case-schemas.md](references/case-schemas.md) before drafting or writing a
case.

## Guardrails

- The user is always the subject of a PersonOS case. Record what the user did,
  why they did it, how they judged or corrected the situation, the result, and
  the reusable lesson. Agents, tools, code, and technical events may appear
  only as background, evidence, or results.
- Before presenting a draft, remove agent and tool names mentally. If the
  user's actions, judgments, and learning are no longer clear, rewrite the
  draft before showing it.
- Write only to `04_cases/`. Never modify `00_profile/`.
- Complete at most one new case or one case update per invocation, then stop.
- Do not write before the user explicitly chooses `确认写入`.
- Never infer uncertain details as facts. Put unresolved details in `待验证项`.
- Use `真实/已验证` only when the important facts and outcome are supported. Otherwise use
  `真实/待验证`.
- Assign one primary case type per event. Do not duplicate one event across case files.
- Update by exact case ID only. Never silently overwrite or merge an ambiguous match.
- Do not expose raw JSON during the confirmation step unless the user asks for it.
- Do not read or cite secrets, credentials, `.env` files, private keys, dependency trees,
  build outputs, caches, or generated artifacts.

## Workflow

### 1. Choose The Capture Mode

Infer the mode from the request when clear. Otherwise offer these concrete paths:

- **Current project**: scan recent project evidence for a new event.
- **Existing case follow-up**: find a known case or unresolved item to update or connect.
- **Historical project**: help reconstruct a past project from a few memorable anchors.

For an existing case follow-up, run:

```bash
python3 ~/.codex/skills/personos-cases-capture/scripts/find_cases.py \
  --root <your PersonOS root> \
  --project "<project name>" --pending
```

Use `--id <case-id>` when the user names an exact case. Search before deciding whether a
follow-up updates an existing case or creates a related new case.

### 2. Find Concrete Candidate Events

Default to scanning the current project. Inspect a small, relevant evidence set:

- `git status`, recent commits, and diffs when available
- project README files, design notes, issue notes, reports, and source entry points
- filenames and modification context that suggest a decision, milestone, failure, or outcome

Exclude at least:

`.env*`, credentials, secrets, keys, tokens, `.git/`, dependency directories, caches,
virtual environments, build outputs, generated files, binaries, and large datasets.

If the current project provides no useful event, scan the default PersonOS project's
`01_projects/` or offer historical project mode.

Offer 2-3 specific event candidates using this format:

`事件｜会记录什么｜为什么值得记录｜预计案例类型`

Briefly explain that choosing an option selects the subject of the interview. Avoid generic
options such as "a recent important decision."

For historical project mode, start with one easy anchor at a time: project name or purpose,
final outcome, or most memorable turning point. Do not require repository evidence; label
user-confirmed memory as evidence and keep uncertain details in `待验证项`.

### 3. Decide Update, Related New Case, Or New Case

Compare the event against related real cases:

- **Update existing** when it resolves a pending item, corrects facts, or supplies the result
  of the same event.
- **Related new case** when a later event has its own decision, success, failure, or reusable
  lesson. Add the existing ID to `关联案例`.
- **New case** when no existing real case covers the event.

State this recommendation before interviewing further. Let the user correct it.

### 4. Interview With Low Effort

After the user chooses an event, ask exactly one question at a time. Prefer a choice tool when
available. Provide 2-3 evidence-grounded likely answers plus a free-form correction path.

Ask only questions needed to distinguish facts, rationale, result, and uncertainty. Good
questions refer to the event:

- "The repository shows the first version stayed file-based. Which reason mattered most?"
- "Which observed result best describes what happened after this choice?"

Do not ask broad questions such as:

- "What do you value when making decisions?"
- "What are your common mistakes?"
- "What is your working style?"

Stop questioning once every required field can be filled or explicitly marked unresolved.

### 5. Classify One Primary Case

Use the routing rules in the schema reference:

- explicit choice among alternatives -> decision
- harmful outcome with a learnable cause -> failure
- beneficial outcome with reusable contributing actions -> success
- meaningful project episode without a stronger classification -> project

When multiple types fit, choose the type containing the most useful new lesson. Mention the
choice in the draft summary.

### 6. Present a Readable Draft

Show a concise Chinese summary with:

- proposed case type and status
- event/date/project
- the user's actions, judgments, corrections, result, and evidence
- the user's reusable lesson
- unresolved items
- operation: `新增`, `更新 <编号>`, or `关联新增（关联 <编号>）`
- destination file

Then offer exactly: `确认写入`, `修改`, `不保存`.

If the user chooses `修改`, revise and present the readable draft again. If the user chooses
`不保存`, stop without writing.

### 7. Write After Confirmation

For a new or related-new case, create a temporary JSON object file containing the confirmed
fields except `编号`. Include `关联案例` for a related-new case. Run:

```bash
python3 ~/.codex/skills/personos-cases-capture/scripts/append_case.py \
  --type <project|decision|failure|success> \
  --input <confirmed-object.json> \
  --root <your PersonOS root>
```

The script validates the full destination JSONL before making an atomic append and generates
the next date-based ID. Report the generated ID and destination. Remove the temporary input
file after the command succeeds or fails.

For an update, create a temporary JSON object containing the complete confirmed replacement
record except `编号`. Run:

```bash
python3 ~/.codex/skills/personos-cases-capture/scripts/update_case.py \
  --id <exact-case-id> \
  --input <confirmed-replacement-object.json> \
  --root <your PersonOS root>
```

Never update with a partial object. Present every changed field and unresolved-item change in
the readable draft before asking for confirmation.

### 8. Suggest, But Do Not Write, Stable Patterns

After writing, inspect existing real cases for closely similar lessons. Only when at least
three real cases support the same pattern, mention a possible preference or anti-pattern
candidate. Do not modify `00_profile/`.
