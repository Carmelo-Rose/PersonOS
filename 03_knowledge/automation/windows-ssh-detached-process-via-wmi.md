# Windows上SSH会话结束会杀掉会话内启动的子进程，用WMI(Win32_Process.Create)可以让长耗时任务真正脱离会话独立存活

## 元数据

- 状态：已验证
- 类型：工具用法
- 领域：automation
- 最后更新：2026-07-21
- 标签：Windows, SSH, 进程管理, WMI, PowerShell

## 用户动作/判断来源

- workbench项目smart-erase切段方案验证：实测多次通过SSH+PowerShell Start-Process启动的长耗时任务，在发起它的SSH会话结束后进程被回收（即使用-PassThru/-NoNewWindow等参数也一样）；改用PowerShell的Invoke-CimMethod -ClassName Win32_Process -MethodName Create启动后，进程在原SSH会话早已结束的情况下仍能被后续独立的SSH调用查到、持续运行完成

## 适用条件

- 需要通过SSH在远程Windows机器上启动一个耗时超过单次命令/工具调用超时上限的任务，且希望任务在启动它的SSH连接断开后继续跑
- 需要用多次独立的短SSH调用分批查看一个长任务的进度，而不是让一次SSH调用长时间挂起等待

## 核心内容

在Windows上通过SSH执行的PowerShell命令（包括用Start-Process、&等方式启动的子进程），当发起它们的SSH会话结束时，子进程会被一并终止，即使表面上看起来'已经用Start-Process分离了'。要让一个长耗时任务真正独立于SSH会话存活，需要经由一个不属于该会话Job Object的父进程来创建它——实测可行的办法：用PowerShell的`Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=...}`（底层走WMI）来启动，这样创建出的进程树完全独立于发起SSH会话，之后可以用任意数量的、彼此独立的短SSH调用去查看它的状态（PID、CPU时间、输出日志文件等），不需要保持一个SSH连接一直开着。注意Win32_Process.Create不支持标准输出/错误重定向，若需要捕获输出，让它启动的目标脚本自己在内部用Start-Process的-RedirectStandardOutput/-RedirectStandardError重定向到日志文件，再从文件里读取。

## 边界与例外

- 只在这台具体机器（Windows 10 + 公司内部OpenSSH配置）上验证过，不同SSH Server实现/配置可能有不同的会话生命周期管理策略
- Win32_Process.Create本身不能设置工作目录之外的很多进程属性，复杂场景可能需要额外处理

## 失效风险

具体现象（SSH会话内子进程被一并回收）推测和Windows OpenSSH Server把会话子进程纳入同一个Job Object、以kill-on-close语义清理有关，未来OpenSSH Server版本或配置变化可能改变这一行为，需要重新验证。

## 关联项

- 03_knowledge/automation/powershell-argumentlist-quoting-gotcha.md

## 待确认或待验证

- 无
