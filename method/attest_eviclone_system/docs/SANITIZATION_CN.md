# 脱敏与清理说明

## 已移除

- `.env` 和真实 API key；
- 本地绝对路径、用户目录和工作目录名称；
- artifact evaluation、paper readiness、promotion gate 等运行结果；
- `eviclone_runs/` 下的大规模实验输出；
- case-study source data 的外部工作区路径；
- 论文草稿与自动填充稿；
- `external/` 下的第三方模型权重和数据集；
- 大规模评测测试与各类生成结果文件。

## 保留

- 核心源码；
- 最小运行脚本与 Python 依赖闭包；
- 脱敏 README 和架构说明；
- 不含密钥的 `.env.example`；
- 轻量 smoke check。

## 边界

该目录是干净的系统实现包，不是完整 artifact/evaluation bundle。实验结果和论文审计产物应在独立私有实验目录中生成和保存。
