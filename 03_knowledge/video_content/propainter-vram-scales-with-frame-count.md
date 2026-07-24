# ProPainter官方推理脚本的显存占用主要由帧数决定，不是分辨率

## 元数据

- 状态：已验证
- 类型：架构判断
- 领域：video_content
- 最后更新：2026-07-21
- 标签：ProPainter, 显存优化, 视频推理, WDDM

## 用户动作/判断来源

- workbench项目smart-erase长视频显存假死排查：读ProPainter官方inference_propainter.py源码定位根因，并用同一素材做前后对比复现验证

## 适用条件

- 用ProPainter（或类似把整段视频frames/masks/光流当作一个整体张量处理的视频修复/补绘模型）处理较长或高帧率视频时
- 在显存有限的GPU（尤其Windows WDDM驱动而非TCC/Linux）上跑视频推理任务，怀疑'跑得慢/卡住'是不是显存不够时

## 核心内容

ProPainter官方推理脚本把整段视频的frames/flow_masks/masks_dilated等张量在一开始就整体搬上显存，--subvideo_length参数只切分中间计算阶段（光流补全、图像传播），不切分这几个常驻张量。因此显存占用近似与总帧数线性相关，跟单帧分辨率反而关系没那么大——实测把长边分辨率从1280降到960，显存占用几乎不变；而713帧比同分辨率下353帧的差距，才是显存从'能跑'到'假死'的真正分界。在显存逼近上限时，Windows WDDM驱动（非TCC）的典型表现是GPU利用率显示100%但进度长时间冻结（假死），而不是干净地报CUDA OOM错误，容易被误判为'还在算，只是慢'。

## 边界与例外

- 这是2080Ti 22G + WDDM驱动 + 这一版ProPainter代码下的实测结论，没有在其他显卡/驱动模式/ProPainter版本上验证过是否同样成立
- 230~240帧左右的安全阈值是基于两个数据点（353帧勉强跑完、713帧假死）在一个特定分辨率（约540×960）下定的经验值，换更大分辨率可能需要重新校准

## 失效风险

特指ProPainter官方inference_propainter.py这一版本的实现细节（frames/flow_masks/masks_dilated在开始就整体.to(device)，--subvideo_length只切分中间计算阶段、每阶段结束又torch.cat拼回全长张量）；如果上游改了实现方式（做成真正流式），这条经验会过时。

## 关联项

- 无

## 待确认或待验证

- 无
