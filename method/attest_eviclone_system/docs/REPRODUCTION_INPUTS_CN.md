# 复现实验输入要求

本包不携带评测数据。若要重新运行完整实验，请准备以下输入：

1. `graphcodebert_full_test_errors_eviclone.jsonl`
2. `probe_synthesis_candidates.jsonl`
3. `probe_synthesis_plan.json`
4. source-retention queue files
5. retained source cards，或配置在线 LLM 重新生成
6. Java/Javac
7. OpenAI-compatible API key

建议将这些数据放在包外的私有 `runs/` 或 `data/` 目录中，不要提交到公开仓库。
