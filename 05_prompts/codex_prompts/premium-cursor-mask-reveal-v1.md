# Premium Cursor Mask Reveal 完整实现提示词

## 元数据

- 状态：已验证
- 分类：codex_prompts
- 工具或场景：Codex / 前端代码生成工具，用于生成 PremiumCursorMaskReveal.tsx，并作为后续 cursor reveal 动效探索的规格基础
- 版本：v1.1
- 最后更新：2026-06-24
- 标签：前端, 动效, Codex, cursor reveal, CSS mask, Canvas, WebGL, 项目组织

## 用户动作/判断来源

- 用户亲自编写提示词内容，要求发给 Codex 执行。
- 用户明确纠正了之前刮刮乐方向，重新定义正确效果名称和目标。
- 提示词包含完整判断流程、交互目标、视觉目标、两条路线细节、禁止清单、组件结构、素材要求、交互细节、性能监控、验收标准。
- 本次实际用于粒子项目后，CSS Mask 版跑通；随后用户要求复刻 MiMo 风格，并确认最终 demo 效果正是想要的。
- 用户进一步修正项目组织边界：新动效应直接嵌入原粒子项目，而不是每次另起一个页面项目。

## 输入要求

- 当前项目结构、依赖列表、页面实现方式。
- 本机运行环境和浏览器表现。
- 素材图片路径或可替换的背景生成方案。
- 目标交互是固定 lens reveal 还是路径显影 ink reveal。
- 如果参考某个网站，先提供 URL 并允许检查真实 DOM/源码/资源。

## 提示词正文

```text
我现在要做一个高级网页动效：Premium Cursor Mask Reveal。

先不要急着写代码。请先检查当前项目结构、依赖、页面实现方式，并根据本机运行情况判断：
1. 是否适合用 WebGL / Three.js 做 shader mask reveal。
2. 如果 WebGL 会卡，是否应该改用 CSS mask + requestAnimationFrame。
3. 当前页面里哪些代码可能导致卡顿，比如大面积 blur、backdrop-filter、多层 box-shadow、过多 DOM 网格、过高 DPR、复杂 shader。

请先给我一个简短判断：
- 推荐实现路线：CSS Mask / WebGL Shader / Hybrid
- 原因
- 性能风险点
- 预计能否稳定 60fps

然后再开始实现。

我要的效果不是刮刮乐，不是永久擦除，不是大蓝色光圈。
我要的是市面高级网站常见的那种：

鼠标是一个小圆形 mask cursor。
鼠标移动到哪里，哪里临时显示隐藏背景。
鼠标移走后，该区域重新隐藏。
圆形边缘柔和，有高级感。
移动有轻微延迟和惯性。
隐藏层可以比上层稍微有位移，形成“探索隐藏空间”的感觉。

正式效果名称：
Premium Cursor Mask Reveal / Background Revealing Cursor / Mouse Pointer Mask Reveal。

交互目标：
- 默认显示上层 base layer。
- 鼠标附近通过圆形 mask 显示 hidden layer。
- mask 跟随鼠标平滑移动，不要生硬。
- mask 直径默认 180px - 260px，可根据屏幕自适应。
- 鼠标移动越快，mask 可以轻微放大。
- 鼠标停下后 mask 保持在鼠标位置，不要消失。
- 鼠标离开 hero 区域后 mask 逐渐缩小或淡出。
- 不要永久留下痕迹。
- 不要做刮刮乐。

视觉目标：
- 高级、克制、现代、偏 Awwwards / Active Theory / Atelier 风格。
- 不要赛博网格堆满屏幕，不要廉价科技 HUD。
- 画面应该像“表层世界”和“隐藏世界”的对比：
  - 上层：暗色、低对比、压抑、模糊一点、单色化。
  - 下层：更清晰、更亮、更有细节、更有空间感。
- 鼠标小圆区域里能看到隐藏背景的真实差异。
- 圆形边缘要有柔和 feather，不要硬边。
- 圆形外框可以有 1px 细线，轻微透明。
- 可以有非常轻的 grain/noise，但不能卡。
- 可以有轻微 chromatic edge / distortion，但必须克制。

实现优先级：
优先做性能稳定版本，不要为了 shader 牺牲流畅度。

路线 A：CSS Mask 高级版，优先推荐
- 使用两层绝对定位的 full-screen layer。
- baseLayer 在上。
- hiddenLayer 在下，或者 hiddenLayer 通过 mask 显示。
- 使用 CSS mask-image / -webkit-mask-image：
  radial-gradient(circle at var(--x) var(--y), #000 0px, #000 90px, rgba(0,0,0,.65) 120px, transparent 150px)
- 通过 requestAnimationFrame 更新 CSS variables。
- 不要直接用 mousemove 硬更新 DOM。
- 使用 lerp 平滑跟随。
- hiddenLayer 可以根据鼠标做轻微 parallax：
  translate3d(mouseX * -10px, mouseY * -10px, 0)
- baseLayer 可以做极轻微反向 parallax。
- cursor ring 用单独 DOM，transform: translate3d，不要 box-shadow 堆叠。

路线 B：WebGL Shader 版，仅在确认不卡时使用
- 使用 Three.js 单个 full-screen plane。
- 两张纹理 uBaseTexture / uHiddenTexture。
- uMouse 控制 radial mask。
- fragment shader 中 mix(base, hidden, mask)。
- mask 是临时跟随鼠标，不保存轨迹。
- 加非常轻的 UV displacement：
  displacedUv = vUv + dir * wave * 0.006 * mask
- 不要 renderTarget。
- 不要后处理。
- 不要复杂循环。
- renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.25))
- 如果 FPS 低于 50，自动回退 CSS Mask。

必须避免：
- 不要 Scratch Reveal。
- 不要 Canvas 刮刮乐。
- 不要固定中心光圈。
- 不要蓝色大坨发光圆。
- 不要大面积 CSS blur。
- 不要 backdrop-filter。
- 不要多层 box-shadow。
- 不要高频 DOM 网格。
- 不要每帧创建对象。
- 不要每帧创建 texture / material / geometry。
- 不要为了炫技写很重的 shader。

页面结构要求：
新建组件：PremiumCursorMaskReveal.tsx

如果已有旧的 ScratchShaderRevealDemo / ShaderDisplacementRevealDemo，请不要继续使用它们。
首页只展示 PremiumCursorMaskReveal。

组件结构建议：
<section className="premium-reveal">
  <div className="base-layer" />
  <div className="hidden-layer" />
  <div className="content-layer">
    <p className="eyebrow">MOVE TO REVEAL</p>
    <h1>DISCOVER<br />HIDDEN<br />LAYERS</h1>
    <p className="desc">A cursor-driven mask interaction revealing the world beneath.</p>
  </div>
  <div className="cursor-ring" />
</section>

素材要求：
如果没有真实图片，不要用幼稚的大色块。
可以用 CSS 生成两套高级抽象背景：
- baseLayer：暗色渐变 + 低透明纹理 + 大面积阴影层次。
- hiddenLayer：更明亮的冷色渐变 + 山脉/建筑/空间感的抽象图形 + 更清晰的细节。
但最终结构要方便替换成真实图片：
background-image: url('/images/base.jpg')
background-image: url('/images/hidden.jpg')

交互细节：
- 监听 pointermove。
- 记录 targetX / targetY。
- requestAnimationFrame 中 currentX/currentY 逐渐 lerp 到 target。
- CSS variables:
  --mask-x
  --mask-y
  --mask-size
  --parallax-x
  --parallax-y
- 鼠标速度 speed = distance(current, previous)。
- mask size = baseSize + speed * 0.4，限制最大值。
- pointerleave 时 mask scale 到 0 或 opacity 到 0。
- pointerenter 时恢复。

性能监控：
- 页面右下角加一个很小的 FPS 显示，仅开发态可见。
- 如果 FPS 低于 50，自动降低：
  - mask size
  - parallax intensity
  - noise opacity
  - 关闭 distortion
- 保证交互优先流畅。

验收标准：
1. 鼠标移动时，小圆区域能明显看到隐藏背景。
2. 鼠标移走后，原区域重新隐藏。
3. 整体流畅，不明显卡顿。
4. 效果看起来像高级网站的 cursor reveal，而不是刮刮乐、不是手电筒、不是蓝色光圈。
5. 代码结构干净，方便后续替换真实图片。
6. 首页只展示这个新效果，不要保留旧的垃圾 demo。

你问 Codex 的时候，重点让它先回答这句：
基于我当前本机和项目，你建议走 CSS Mask、WebGL Shader，还是 Hybrid？先别写代码，先判断。

它如果还坚持直接 Three.js，你就让它说明为什么不会卡、如何自动降级。

补充边界：如果目标从“鼠标停住保持圆形 lens”变成“MiMo 式鼠标路径短暂显影并自动闭合”，应先实查参考站真实实现，再允许 Canvas 2D destination-out ink stamp 作为路线 C；不要把 Canvas 2D 一概归类成错误的 Scratch Reveal。对于长期做多个动效实验的项目，优先把新效果接入原项目的 route/component 实验台，而不是每次另起项目。
```

## 输出格式

- 先输出简短判断：推荐路线、原因、性能风险、预计 FPS。
- 再输出实现方案与代码改动。
- 实现后输出验证结果：build/lint/browser 检查。
- 如果接入既有实验项目，说明新增 route 和组件路径。

## 成功标准

- 鼠标移动时小圆区域或路径区域能明显看到隐藏背景。
- 鼠标移走后原区域重新隐藏或按目标短暂显影后闭合。
- 整体流畅不明显卡顿。
- 效果像高级网站 cursor reveal，而非刮刮乐、手电筒或蓝色光圈。
- 代码结构干净，方便后续替换真实图片。
- 在多效果项目中能通过 route/component 管理，不强制每次新建项目。

## 验证结果

已验证。CSS Mask 版在 particle-logo-demo 中跑通，Codex 选择路线 A（CSS Mask + rAF），输出 PremiumCursorMaskReveal.tsx、FPS 监控和低帧率降级。随后用户要求复刻 MiMo 首页质感，实查 MiMo Code 页面确认其为 Canvas 2D destination-out transient ink reveal，并在同项目新增 MimoInkReveal route；用户确认“成功了，demo的效果是我想要的”。build/lint 均通过。

## 适用边界

- 适用于需要实现 Premium Cursor Mask Reveal 或相近 cursor reveal 效果的前端项目。
- 适用于 Codex 或类似前端代码生成工具。
- 不适用于真正刮刮乐、永久擦除或需要保存擦除轨迹的业务需求。
- 当目标是固定小圆 lens 且停住保持，优先 CSS Mask；当目标是 MiMo 式划过显影并闭合，优先 Canvas Ink；当目标是 UV 扭曲、Fluid、复杂图像混合，再考虑 WebGL。
- “首页只展示新效果”仅适合一次性交付页面；若用户明确希望长期积累动效实验，应改为同项目 route/component 实验台。

## 变更原因

v1 已在真实项目中验证；本次补充 MiMo 风格 Canvas Ink 路线和同项目实验台组织边界，使提示词不再把所有非 CSS 圆形 mask 都误排除。

## 版本历史

- v1：用户从刮刮乐方向转向正确术语后首次编写完整规格提示词，主要覆盖 CSS Mask 与 WebGL Shader 两条路线。
- v1.1：补充本次验证结果、MiMo Canvas Ink 路线、以及同项目 route/component 实验台的组织边界。

## 待确认或待验证

- WebGL shader 版本尚未在该项目中完成第三阶段实测。
- 如果未来要沉淀专门的 MiMo Ink Reveal prompt，可从 v1.1 中拆出独立提示词。
