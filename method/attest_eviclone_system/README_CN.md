# attest_eviclone_system

这是 EviClone 的脱敏源码整理版，面向方法展示、代码审查和后续复现实验接入。

本目录刻意不包含：

- configured LLM 或其他服务的真实 API key；
- 本机绝对路径、用户名、运行日志；
- GraphCodeBERT/BCB 大规模评测结果；
- 860/6550 样本原始数据、case-study 明细、probe 执行结果；
- 论文草稿、artifact suite 结果、manifest/report 审计产物；
- 第三方模型权重和数据集压缩包。

## 核心系统链路

```text
Selective Gate
  -> LLM Context Completion
  -> Retained Source Sidecar
  -> Functional Block / Module Lowering
  -> Probe Synthesis and Execution
  -> Metric Aggregation
  -> Evidence Contract
```

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `eviclone_prototype/` | 核心原型代码 |
| `scripts/` | 最小运行入口及其依赖脚本 |
| `docs/` | 架构、脱敏边界和复现实验接入说明 |
| `.env.example` | 本地环境变量示例，不包含真实密钥 |
| `RUN_SMOKE.ps1` | 轻量源码检查，不依赖评测数据 |

## 轻量检查

```powershell
.\RUN_SMOKE.ps1
```

该检查只做 Python 语法编译和关键模块导入，不运行大规模评测。

## 在线 LLM 配置

复制 `.env.example` 为 `.env`，填入自己的本地密钥。`.env` 已被 local ignore rules 忽略。

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
  }
}
```

## 数据接入

该脱敏版不自带评测数据。要复现实验，需要另行提供：

- BCB/GraphCodeBERT 错例输入；
- probe synthesis candidates；
- source-retention queue；
- retained source cards 或在线 LLM 生成权限；
- Java/Javac 执行环境。
