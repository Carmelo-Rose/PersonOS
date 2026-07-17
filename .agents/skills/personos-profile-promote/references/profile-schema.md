# PersonOS Profile Promote Manifest Schema

`write_profile.py --input <file>` takes a **JSON array**. Each item has a `kind`. A NEW trait
(`anti_pattern` / `preference_row`) must carry `source_cases` with at least `--min-support`
distinct real case 编号 (default 2, prefer 3); the writer rejects under-supported traits. Review
date is filled by the script.

## kind: anti_pattern  → new section in 00_profile/anti_patterns.md

Inserted before the `## 待补充清单` list. Rejects a duplicate heading.

```json
{
  "kind": "anti_pattern",
  "title": "凭感觉判断根因，不先最小实测",
  "applicable_scenario": "排查性能/卡死/数据异常/环境问题时",
  "typical_manifestation": "见长时间无响应就断定“卡死”，凭经验下网络/配置结论",
  "why_harmful": "误判方向、返工；把可量化问题当玄学",
  "early_signal": "还没跑 curl/dry-run/日志锚点就已经有结论",
  "alternative": "先用最小实测或量化拿到确定数据，再下结论",
  "exceptions": "已有充分同类经验、验证成本极低的显而易见问题",
  "source_cases": ["failure_20260703_001", "decision_20260704_001"]
}
```

## kind: preference_row  → new row in the 决策偏好 table of 00_profile/preference.md

Columns: 场景 / 偏好 / 优先级 / 原因 / 可接受例外. Case ids are auto-appended to 原因 if not
already present. Rejects a duplicate 场景.

```json
{
  "kind": "preference_row",
  "title": "电商自动化偏好风控闭环",
  "scenario": "电商自动化 / 采集面临平台风控",
  "preference": "优先做发现-暂停-留证-人工恢复闭环，不自动绕过验证",
  "priority": "高（域限定：电商自动化）",
  "reason": "自动绕过推高封号风险；进程退出≠业务成功",
  "exception": "官方开放 API / 已授权数据源",
  "source_cases": ["success_20260716_001", "decision_20260704_001"]
}
```

## kind: strengthen  → add new source cases to an EXISTING anti-pattern

Appends to that section's `- 来源案例：` line and refreshes 最后复核日期. Use this instead of a
duplicate when the trait already exists. Idempotent (already-present ids skipped).

```json
{
  "kind": "strengthen",
  "heading": "反模式名称：把模糊指令丢给弱模型 / 子代理",
  "add_source_cases": ["decision_20260619_001"]
}
```

## Notes

- `strengthen` in v1 targets anti-pattern sections only (clean `来源案例` line). To strengthen a
  preference row or ability-map row, propose the edit as text and apply it by hand.
- `person_profile.md` (identity, goals, stage) and `ability_map.md` new rows are NOT written by the
  script — propose them as text for the user to apply.
- Prefer `--min-support 3` and cross-project evidence for a durable trait; use 2 only when the two
  cases are strong and from different projects.
