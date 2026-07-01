# 系统架构

## 1. Selective Gate

决定一个样本是否需要进入动态执行链路。低风险样本可保留基础模型结果，高风险或边界不清样本进入后续证据链。

## 2. LLM Context Completion

LLM 只负责补全方法片段缺失的 imports、类字段、框架上下文、Servlet/GUI/DB 环境等。LLM 不直接给 clone/non-clone 最终结论。

## 3. Retained Source Sidecar

将补全后的源码、上下文解释、风险标记和 probe 所需结构保存为 sidecar，供后续 verifier 和执行器审计。

## 4. Functional Block / Module Lowering

抽取核心运行逻辑，转换成更标准的可执行模块，而不是在原始代码上盲目打补丁。

## 5. Probe Synthesis and Execution

生成能区分功能行为的 probe，执行后收集返回值、文件/流/HTTP/异常等证据。

## 6. Metric Aggregation

把动态证据映射为 benefit、harm、net gain 等指标。该整理版保留计算逻辑，不携带历史评测结果。

## 7. Evidence Contract

通过 schema、source preservation、side-effect safety、probe path 和 manifest-like contract 限制证据可用性。
