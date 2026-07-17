# .agents/skills — PersonOS 采集 skills 的唯一源

本目录是 PersonOS 各 capture skill（cases / knowledge / organ / prompt / session）的
**唯一真源 (source of truth)**。所有对 skill 的修改都只在这里改。

## 有两处部署副本，不要直接改

| 位置 | 用途 | 谁在读 |
| --- | --- | --- |
| `.agents/skills/<name>/`（本目录） | **源，只改这里** | 维护者 |
| `~/.codex/skills/<name>/` | Codex 运行副本（SKILL.md 里 run 路径指向这里） | Codex |
| `<repo>/<name>.skill.zip` | 可分发包，供 Claude Cowork 导入 | Cowork |

直接改 `~/.codex/skills/` 或 `.skill.zip` 会在下次同步时被覆盖，改动丢失。

## 维护规则：改完 skill 必须同步

改动本目录任何 skill 后，运行：

```bash
bash tools/sync_skills.sh            # 推送到 ~/.codex/skills + 重打包全部 .skill.zip
bash tools/sync_skills.sh --dry-run  # 先预览差异
```

然后到 Claude Cowork 的 设置 › Capabilities 重新导入更新后的 `.skill.zip`（脚本代替不了这步）。

**macOS 提醒**：从「终端」运行，且终端需具备「完全磁盘访问权限」，否则访问
`~/Documents` / `~/.codex` 会被 TCC 拦截。

## 字段/schema 变更连带项

若改动涉及 `04_cases` 等写入的数据结构（如决策生命周期字段 `决策状态`/`取代`/`被取代`），
记得同时更新：`<skill>/references/*schema*.md`、`<skill>/SKILL.md` 的访谈与写入说明，以及
对应数据目录的 `README.md`（如 `04_cases/README.md` 的字段规范）。
