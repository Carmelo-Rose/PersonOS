# AILAB 服务机（Windows）部署常驻进程的三个坑

## 元数据

- 状态：已验证
- 类型：最佳实践
- 领域：automation
- 最后更新：2026-07-21
- 标签：Windows部署, PowerShell, 计划任务, 服务机, AILAB

## 用户动作/判断来源

- 2026-07-21 Console 项目部署到 192.168.1.198(AILAB) 时反复调试踩出来的，每条都有实际失败现象、排查过程和修复后的验证

## 适用条件

- 以后要在 AILAB 服务机(或类似安全软件较敏感的 Windows 机器)上用 PowerShell 脚本常驻启动进程时
- 给 Windows 机器写 .ps1 脚本、尤其涉及中文注释时
- 给运行 Python 3.14 或更新版本解释器的机器装依赖时

## 核心内容

- 1) Start-Process -RedirectStandardOutput/-RedirectStandardError 在 AILAB 上会让子进程刚启动就静默退出，零报错零日志，排查耗时很长。改用 Task Scheduler(Register-ScheduledTask)启动同一条命令完全正常。结论：这台机器上要常驻服务，用计划任务，不要用 Start-Process 重定向输出。
- 2) .ps1 文件里中文注释紧挨着反引号续行的多行 cmdlet 调用，经 scp 传到 Windows 后用 powershell -File 执行，偶发把两行合并成一行，导致后面那行变量赋值失效(变量变成 $null，报'无法将参数ArgumentList绑定'之类的错)。怀疑是无 BOM 的 UTF-8 被当 ANSI 代码页解析导致换行丢失。结论：给这类机器用的 .ps1 一律纯 ASCII，cmdlet 调用写单行(别用反引号续行)，中文说明放 .md 文档里不要塞进脚本注释。
- 3) AILAB 上 Python 是 3.14(D:\hyk_sort\python\python.exe，PATH 上唯一解释器，没有 uv)。requirements.txt 精确 pin 版本号(比如 pydantic==2.10.4)会导致 pip 因为没有 cp314 预编译 wheel 而尝试从源码编译，卡住不动(没装 Rust/C 工具链)。结论：给这类新版本 Python 装的依赖用 >= 松约束，不要精确 pin，让 pip 自己挑有 wheel 的版本。

## 边界与例外

- 以上是这一台机器的实测现象，不代表所有 Windows 机器都有同样的安全软件拦截行为；换机器部署时第1条要重新验证，2、3条(纯ASCII脚本、依赖不精确pin)可以直接作为通用习惯保留而不需要重新验证

## 失效风险

如果服务机的安全软件策略变化，或 Python 3.14 的包生态成熟到旧版本也普遍有 wheel 了，第1、3条的具体触发现象可能改变；但'用计划任务而非Start-Process常驻'、'.ps1纯ASCII单行'这两条经验本身通用性强，换机器也大概率适用

## 关联项

- 无

## 待确认或待验证

- 无
