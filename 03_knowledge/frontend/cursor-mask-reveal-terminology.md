# 前端交互术语：Cursor Mask Reveal

## 元数据

- 状态：已验证
- 类型：术语
- 领域：frontend
- 最后更新：2026-07-05
- 标签：前端交互, 术语, reveal, ink reveal, CSS mask, 动效

## 用户动作/判断来源

- 用户在同一会话中先确认 progressive disclosure 是否为业内常用词，再转向前端 reveal 动效命名。
- 用户追问 ink reveal 的中文是否有固定叫法，并要求区分英文名称与中文描述之间的边界。
- 用户确认英文叫法可直接保留，但需要中文侧更自然的表达与近义词区分。

## 适用条件

- 需要为鼠标揭示、墨迹显影、遮罩显隐类前端动效命名时。
- 需要在设计稿、组件名、方案文档或与 AI 编码工具沟通时使用更准确术语时。
- 需要区分 reveal 效果是临时显现、永久擦除还是扭曲位移时。

## 核心内容

- Cursor Mask Reveal 适用于鼠标移动到哪里，哪里临时显示隐藏层，移开后继续隐藏的稳定透镜式显隐。
- Ink Reveal 更像描述性命名，不是高度标准化术语；中文可用“墨迹揭示动效”或“墨迹显现效果”，不必强行固定成“短暂墨迹揭示”。
- 如果效果更像一团墨迹扫过后露出内容，可用 ink wipe；更像笔刷边缘时用 brush reveal；更像涂抹拖开时用 smudge reveal；更像刮开时用 scratch reveal。
- 术语命名应优先抓交互行为和视觉材质，不要只按中文直译或代码实现命名。

## 边界与例外

- 不要把 ink reveal 当成严格标准术语；它更多是团队沟通和案例搜索的描述性名字。
- 不要把 cursor reveal、mask reveal、scratch reveal 混成一类；它们对应的交互行为不同。
- 中文命名可以服务沟通，但技术实现判断仍应回到 CSS mask、Canvas 2D 或 WebGL 的能力边界。

## 失效风险

低。术语体系本身较稳定，但团队内部中文译法可能继续变化。

## 关联项

- 03_knowledge/frontend/css-mask-vs-webgl-shader-reveal.md

## 待确认或待验证

- 不同设计团队对 ink reveal 的中文译法可能仍会继续分化。
