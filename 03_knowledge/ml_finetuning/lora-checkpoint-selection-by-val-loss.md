# LoRA微调:用val loss拐点选checkpoint而非直接用最终权重

## 元数据

- 状态：已验证
- 类型：方法
- 领域：ml_finetuning
- 最后更新：2026-07-03
- 标签：LoRA, 过拟合, 模型微调, checkpoint选择

## 用户动作/判断来源

- 本地对Qwen2.5-3B-8bit做LoRA微调(60条数据,200 iters,mlx_lm.lora),观察到val loss在iter50触底(0.668)后持续回升,train loss持续下降至0.033,判断出现过拟合
- 改用训练中途保存的iter100 checkpoint(val loss 0.733)替换最终iter200权重,并通过对比生成结果验证效果未明显下降

## 适用条件

- 小数据集(几十到上百条)做LoRA微调时
- 训练脚本支持定期保存中间checkpoint并计算验证集loss(如mlx_lm.lora的--steps-per-eval/--save-every)

## 核心内容

LoRA微调不要默认使用训练结束时的最终权重。训练时开启周期性验证(val loss),若val loss在训练中途见底后持续回升、而train loss仍在下降,说明出现过拟合,应选用val loss最低点附近的中间checkpoint作为正式使用的adapter,而不是iters跑满后的最终权重。

## 边界与例外

- 数据量较大、正则化充分时过拟合信号不明显,不必生搬硬套
- 仅看loss数值可能不够,还需结合实际生成内容对比(尤其是训练数据未覆盖的话题),参见'LoRA微调效果评估:三层测试法'

## 失效风险

特定于LoRA/小样本微调场景,若换成更大数据集或加入更强正则化,该经验的必要性会降低

## 关联项

- 03_knowledge/ml_finetuning/lora-eval-three-tier-test.md

## 待确认或待验证

- 无
