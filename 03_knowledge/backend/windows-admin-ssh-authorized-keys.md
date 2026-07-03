# Windows管理员账号配置SSH免密登录的关键点

## 元数据

- 状态：已验证
- 类型：方法
- 领域：backend
- 最后更新：2026-06-30
- 标签：SSH, Windows, OpenSSH, 远程运维

## 用户动作/判断来源

- 用户委托服务机上的远程Agent执行 icacls/authorized_keys 相关命令，经两轮权限调整后 Mac 到该 Windows 管理员账号的免密SSH才连接成功

## 适用条件

- 需要从 Mac/Linux 免密 SSH 登录一台 Windows 机器上属于 Administrators 组的账号时

## 核心内容

- Windows OpenSSH 对管理员账号有特殊处理：公钥必须写入 C:\ProgramData\ssh\administrators_authorized_keys，写到用户目录下的 ~/.ssh/authorized_keys 对管理员账号无效。
- administrators_authorized_keys 文件权限要求严格：需用 icacls 去除继承并仅授予 SYSTEM 和 BUILTIN\Administrators 完全控制权，否则 sshd 会在认证阶段之前就直接断开连接（表现为 Connection closed by remote host，而不是提示密码/密钥错误）。
- 用户主目录下的 .ssh 目录及其 authorized_keys 同样需要去继承、仅保留当前用户的完全控制权，否则也会被拒绝。
- 排查连接失败时用 ssh -v 观察到类似 kex_exchange_identification: Connection closed 这种在密钥协商前就断开的情况，基本可判定是文件权限问题而非公钥内容错误，应优先检查 icacls 权限而不是重新生成密钥。

## 边界与例外

- 仅适用于 Windows OpenSSH Server（Win10/11自带或安装的OpenSSH）；非管理员的普通账号仍按标准 ~/.ssh/authorized_keys 路径 + 用户目录权限即可，不需要 administrators_authorized_keys

## 失效风险

依赖 Windows OpenSSH 当前版本对管理员账号的实现细节，未来微软更新该组件行为可能变化

## 关联项

- 无

## 待确认或待验证

- 无
