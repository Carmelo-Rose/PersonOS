# 前端高级动效实现路线判断：CSS Mask / Canvas Ink / WebGL Shader

## 元数据

- 状态：已验证
- 类型：架构判断
- 领域：frontend
- 最后更新：2026-06-24
- 标签：前端, 架构判断, CSS mask, Canvas, WebGL, Cursor Reveal, 性能

## 用户动作/判断来源

- 用户明确要求优先做性能稳定版本，不要为了 shader 牺牲流畅度。
- 用户要求 AI 编码工具先判断路线再写代码，不要直接上 Three.js。
- 用户要求实查 MiMo 首页效果的真实实现方式，随后确认 demo 效果正是想要的。
- 本次实查 MiMo Code 页面发现其 reveal 使用 Canvas 2D、destination-out 和短生命周期 stamp，而非 Three.js/GLSL。
- 本地粒子项目中 CSS Mask 版和 MiMo 风格 Canvas Ink 版均实现并通过验证。

## 适用条件

- 实现 Cursor Mask Reveal / Background Revealing Cursor 类效果。
- 需要在前端项目中选择 CSS、Canvas 还是 WebGL 方案。
- 项目需要稳定 60fps，且用户更重视目标效果和可维护性而非技术炫技。
- 需要复刻参考网站的真实交互行为，而不只是复刻术语或截图。

## 核心内容

- 先按目标交互分类，而不是先按技术偏好分类。若效果是“鼠标停住时小圆 lens 保持显示隐藏层，移开后隐藏”，优先 CSS mask + requestAnimationFrame + CSS variables；若效果是“鼠标路径短暂显影，随后自动闭合”，优先 Canvas 2D ink stamp + destination-out；若需要真实图片 UV 扭曲、chromatic edge、fluid distortion 或统一 GPU 后处理，再考虑 WebGL shader。
- CSS Mask 高级版：两层 full-screen layer，hiddenLayer 通过 radial-gradient mask 显示；RAF 更新 --mask-x/--mask-y/--mask-radius；lerp 平滑跟随；hiddenLayer 轻微 parallax；cursor ring 单独 DOM 用 transform，不堆叠 box-shadow。
- Canvas Ink 版：底层是可替换图片或抽象画面，上层 canvas 填充页面底色；鼠标移动时沿路径生成短生命周期 stamp；每帧重绘实色遮罩，再用 globalCompositeOperation='destination-out' 挖出不规则柔边区域；stamp 结束后自然闭合，不永久留下痕迹。
- WebGL Shader 版仅在需求明确时使用：单个 full-screen plane、uBaseTexture/uHiddenTexture、uMouse radial mask、轻量 UV displacement；避免 renderTarget、后处理、复杂循环；限制 renderer.setPixelRatio(Math.min(devicePixelRatio, 1.25))，必要时降级 CSS/Canvas。
- 判断流程：检查当前项目结构、依赖和页面实现方式 → 验证参考站真实 DOM/资源/源码 → 判断目标是 lens reveal 还是 path ink reveal → 给出路线判断 → 再实现并用 build/lint/browser 检查验证。

## 边界与例外

- 不要把所有高级 cursor reveal 都默认解释成 WebGL shader；真实参考站可能用 CSS 或 Canvas。
- 不要把 Canvas 2D 一概等同于刮刮乐。若 stamp 有生命周期并每帧重绘遮罩，它是 transient reveal，不是永久 scratch card。
- CSS mask 对旧浏览器可能有兼容性问题；Canvas ink 在大 DPR 和高 stamp 数下要限制 DPR、MAX_STAMPS 和生命周期。
- WebGL 更适合纹理扭曲和复杂流体，不应为了术语高级而牺牲流畅度和维护成本。

## 失效风险

中。CSS mask、Canvas composite 和 WebGL 技术本身稳定，但浏览器性能、DPR 策略和具体参考站实现会变化；外站源码结论仅代表 2026-06-24 实查结果。

## 关联项

- 03_knowledge/frontend/cursor-mask-reveal-terminology.md
- 03_knowledge/frontend/incremental-effect-building.md
- 05_prompts/codex_prompts/premium-cursor-mask-reveal-v1.md

## 待确认或待验证

- WebGL shader 版本尚未在该项目中作为第三阶段实测。
- 不同浏览器上 CSS mask 与 Canvas composite 的边缘质感和性能仍需按目标设备验证。
