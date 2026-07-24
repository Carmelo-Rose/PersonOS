# PowerShell给Windows子进程传递含中文路径/内嵌引号JSON参数的正确方式

## 元数据

- 状态：已验证
- 类型：工具用法
- 领域：automation
- 最后更新：2026-07-21
- 标签：PowerShell, Windows, 命令行参数, 转义

## 用户动作/判断来源

- workbench项目smart-erase复现测试：多次尝试PowerShell Start-Process -ArgumentList传数组/ProcessStartInfo.ArgumentList，均失败或产生错误结果，最终定位到可靠做法

## 适用条件

- 需要在Windows/PowerShell里给一个子进程（如python.exe）传递包含空格、中文字符、或内嵌双引号（比如一段JSON字符串）的命令行参数

## 核心内容

踩过的坑：1) `Start-Process -ArgumentList` 传字符串数组时，会被简单地用空格拼接成一行，不会给包含空格的元素自动加引号，导致含空格路径/JSON被从中间断开、当成多个参数；2) 手动给每个数组元素预先包一层转义引号，又会被再拼接逻辑重新处理，产生双重转义/损坏；3) 想用更底层的`System.Diagnostics.ProcessStartInfo.ArgumentList`（.NET原生的参数列表集合，理论上不需要手工拼引号）在某些机器/.NET版本上是null，调用`.Add()`只会抛出非终止性错误（脚本不会中断，但参数没加成功），导致进程用0个参数悄悄启动或秒退，很容易被忽略。唯一稳妥可靠的办法：手工拼出一个和Python `subprocess.list2cmdline()`风格一致的**单个转义字符串**（形如 `--input "path with space" --params "{\"k\": v}"`，内部的双引号用反斜杠转义），整体作为**一个字符串**（不是数组）传给`-ArgumentList`，不要再对它做任何额外的包裹或转义。

## 边界与例外

- 仅针对Windows/PowerShell 5.1 + .NET Framework这一组合验证过
- 如果参数本身还包含反斜杠或其他特殊字符，需要额外核对转义规则是否仍然正确

## 失效风险

PowerShell/.NET不同版本对ArgumentList的支持程度不同（本次踩坑的机器上ProcessStartInfo.ArgumentList返回null、属性不可用），换机器/换PowerShell版本时结论可能不完全适用，建议先验证。

## 关联项

- 03_knowledge/automation/windows-ssh-detached-process-via-wmi.md

## 待确认或待验证

- 无
