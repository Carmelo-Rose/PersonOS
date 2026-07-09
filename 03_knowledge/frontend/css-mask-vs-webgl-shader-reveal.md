# 前端高级动效实现路线判断：CSS Mask / Canvas Ink / WebGL Shader

## 元数据

- 状态：已验证
- 类型：架构判断
- 领域：frontend
- 最后更新：2026-07-05
- 标签：前端, 架构判断, CSS mask, Canvas, WebGL, reveal, 性能

## 用户动作/判断来源

- 用户基于此前 grain 项目继续追问 reveal 动效的实现分类，要求把项目中的效果落到更准确的技术名词上。
- 用户明确询问其项目中的实现应归到 mask reveal 还是 canvas ink reveal。
- 同一会话中，用户要求补充一组可用于继续学习的前端视觉交互关键词。

## 适用条件

- 需要判断 reveal 效果该用 CSS mask、Canvas 2D 还是 WebGL 时。
- 需要把动效命名、交互形态和技术实现绑定起来时。
- 需要为后续学习路线建立从术语到技术栈的映射时。

## 核心内容

- 固定跟随鼠标、鼠标停住后显现区域仍保留在当前位置的稳定透镜式 reveal，优先归类为 mask reveal，并优先考虑 CSS mask 实现。
- 短暂出现、会自动消散、像墨迹或涂抹一样把内容短时擦出来的 reveal，优先归类为 canvas ink reveal，典型实现是 Canvas 2D + globalCompositeOperation='destination-out' + 短生命周期 stamps。
- 只有当效果核心是图片 UV 扭曲、液态位移、色散边缘或统一 GPU 后处理时，才进入 distortion reveal / shader effect / WebGL 的路线。
- 学习与实现都应先按交互分类，再选技术；不要从 Three.js 或 shader 可用性反推效果定义。

## 边界与例外

- 不要把所有高级 reveal 一律归到 WebGL shader；很多真实案例只需 CSS mask 或 Canvas 2D。
- 不要因为中文叫“墨迹”就直接上 shader；如果本质是短命擦除层，Canvas 2D 往往更合适。
- 术语与实现需要双向校验：命名帮助检索案例，但实现路线仍要受目标交互、性能预算和设备约束支配。

## 失效风险

中。技术边界稳定，但具体参考站点与浏览器性能表现会随时间变化。

## 关联项

- 03_knowledge/frontend/cursor-mask-reveal-terminology.md

## 待确认或待验证

- 若后续要覆盖更复杂的图片位移或液态折射场景，还需要单独补充 shader 路线的验证案例。
