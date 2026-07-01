# Attest Execution Method

This directory contains the static-model-free Attest pipeline used for hard-case
semantic clone validation. The method constructs behavioral evidence rather than
accepting a representation-model prediction, a lexical similarity score, or a
direct LLM vote as the final decision.

The packaged method name is intentionally anonymized as `attest_exec_method`.

## Pipeline

```text
code A, code B
  -> attest_stage1_comprehend: infer each fragment's function and a shared I/O contract
  -> attest_stage2_make_runnable: complete missing context and build executable harnesses
  -> attest_stage3_synth_inputs: generate shared discriminating inputs
  -> attest_stage4_execute_compare: execute both sides, normalize outputs, compare behavior
  -> attest_fallback_or_abstain: return clone / non-clone / undecided with evidence tags
```

The system is designed for incomplete benchmark snippets: missing imports, class
fields, helper methods, framework context, Servlet/GUI/DB environment, and other
surrounding state are reconstructed as a support layer. The original snippet is
kept as the target logic; the LLM is used to fill context and adapters, not to
rewrite the target behavior.

## Implemented Components

| Component | Files | Role |
|---|---|---|
| `attest_pipeline` | `attest/pipeline.py` | End-to-end orchestration and evidence emission. |
| `attest_stage1_comprehend` | `attest/stage1_comprehend.py`, `attest/prompts.py` | Functional understanding and unified contract construction. |
| `attest_stage2_make_runnable` | `attest/stage2_make_runnable.py`, `attest/repair_loop.py`, `attest/harness_fill.py` | Context completion, harness filling, compile/runtime repair. |
| `attest_stage3_synth_inputs` | `attest/stage3_synth_inputs.py` | Shared probe/input generation. |
| `attest_stage4_execute_compare` | `attest/stage4_execute_compare.py`, `attest/normalize.py` | Execution, output normalization, residual-difference adjudication. |
| `attest_executor_java` | `attest/executors/java_exec.py`, `harness_support/java/` | Java harness compilation and execution. |
| `attest_executor_cpp` | `attest/executors/cpp_exec.py`, `harness_support/cpp/` | C/C++ harness execution through Docker. |
| `attest_dependency_gate` | `attest/depgate.py` | Guard against decisions that only reflect external dependency stubs. |
| `attest_eval` | `attest/eval/` | Dataset evaluation, ablation, metrics, and overlay accounting utilities. |

## Prerequisites

| Need | Why | Check |
|---|---|---|
| Python 3.11+ | Pipeline orchestration and tests. | `python --version` |
| JDK 21 or compatible `javac`/`java` | Java execution. | `javac -version` |
| Docker | Required for C/C++ execution; optional hardening for Java. | `docker --version` |
| OpenAI-compatible LLM endpoint | Context completion, contract construction, input synthesis. | `python -m attest.smoke_llm` |

Configure the LLM backend by copying `.env.example` to `.env` and filling in a
local key. The release package intentionally contains no API key or generated
LLM cache.

## Quick Start

```bash
cd method/attest_exec_method
python -m pip install -r requirements.txt

# Offline tests: normalization, schema, metrics, and executor smoke tests.
pytest -q

# Optional live endpoint check.
python -m attest.smoke_llm

# Run one pair.
python -m attest.pipeline --pair A.java B.java --label 1

# Evaluate a dataset subset.
python -m attest.eval.run_eval --dataset bcb --limit 20 --methods full direct
```

## What Is Not in This Method

This directory does not include the selective correction gate, the dynamic
router, DSFM/GraphCodeBERT base predictions, or a static clone model. Those
components are kept separately as baselines or historical overlay experiments in
the release root. The final method here runs the execution-evidence pipeline for
the target pair and reports `undecided` when behavioral evidence is insufficient
and fallback is disabled.

## Reproducibility Notes

- Decoding is deterministic by default (`temperature=0`).
- Intermediate artifacts are written under the configured run directory.
- LLM cache, execution workdirs, and API keys are excluded from the release.
- Unit tests are included so reviewers can verify the artifact without live LLM
  calls; live end-to-end tests require a configured endpoint.
