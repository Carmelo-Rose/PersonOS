# workbench 视觉模型配置有两个独立字段：图片反推(VISION_MODEL) 与视频分析(MONO_VIDEO_MODEL) 互不同步

## 元数据

- 状态：已验证
- 类型：架构判断
- 领域：video_content
- 最后更新：2026-07-22
- 标签：workbench, video_content, 配置, UX陷阱

## 用户动作/判断来源

- 用户在设置页只改了'图片 / 视频反推（视觉理解）'分组下的模型字段，以为这一处已经覆盖图片和视频两种场景
- 排查视频分析任务失败时发现 sqlite 里 MONO_VIDEO_MODEL 仍是修改前的旧值，跟已经改对的 VISION_MODEL 不一致
- 读取 src/lib/mono/service.ts 确认视频分析代码只在 MONO_VIDEO_MODEL 未显式设置时才会回退使用 VISION_MODEL

## 适用条件

- 在 workbench 设置页修改视觉/视频相关模型配置时
- 排查'改了模型配置但某个功能还是报旧错误'类问题时，优先直接查 sqlite 里对应 key 的当前值，而不是相信 UI 分组标题的措辞

## 核心内容

workbench 设置页的'图片 / 视频反推（视觉理解）'分组只对应 VISION_MODEL/VISION_BASE_URL/VISION_API_KEY，只影响图片反推（image_to_prompt）。视频分析走的是另一组完全独立的字段 MONO_VIDEO_MODEL/MONO_VIDEO_ANALYZE_URL/MONO_VIDEO_API_KEY，界面上单独分组显示为'视频分析服务（Mono）'。代码里视频分析只有在 MONO_VIDEO_MODEL 这几个字段完全没有被显式设置过（sqlite 里没有覆盖值）时，才会回退使用 VISION_* 的值；一旦 MONO_VIDEO_MODEL 曾经被写过任何值（哪怕是错的），就不会再回退，必须单独改对它才生效。

## 边界与例外

- 只描述了 workbench 这一个代码库当前的具体实现，不是通用规律；不同代码库/产品的字段命名和回退逻辑可能完全不同

## 失效风险

如果后续把这两个配置字段在代码或 UI 上合并/重构，这条知识会过期，需要重新核实。

## 关联项

- 无

## 待确认或待验证

- 无
