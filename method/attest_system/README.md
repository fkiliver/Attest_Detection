# Attest

**Semantic (Type-4) code-clone detection via constructed behavioral evidence.**

Existing semantic-clone detectors judge code by its *static form* (e.g.
representation-learning models), by *compiling low-quality completions and then
matching statically*, or by *asking an LLM directly* (unreliable). Attest instead
constructs **real behavioral evidence**: a single LLM backbone drives a four-stage
pipeline that *executes* both fragments on a shared input set and compares their
observable behavior.

```
 code_A ┐                              ┌─ run A ─┐
        ├▶ ① comprehend ─▶ ② make ────┤         ├─▶ ④ execute & compare ─▶ Clone /
 code_B ┘   + unified       runnable   └─ run B ─┘     (normalize + LLM diff)   Non-Clone /
            contract        + ③ shared inputs                                   Undecided
```

1. **Comprehend** — label each fragment's function and define one *unified test
   contract* `⟨σ, O, F⟩`: the calling interface `σ`, what output to observe `O`,
   and the shape of an input case `F`. If the two fragments plainly compute
   different functions, exit early as Non-Clone.
2. **Make runnable** — the LLM completes each fragment into a runnable harness
   conforming to the contract, adding missing declarations/dependencies and an
   I/O adapter. The original fragment is embedded verbatim; the LLM fills only
   named holes and cannot edit the harness machinery. A compile-repair loop feeds
   diagnostics back to the LLM up to a fixed budget.
3. **Synthesize inputs** — one shared, intent-covering input batch (normal values
   plus empty, large, boundary, and non-ASCII cases), handed to both sides so the
   two output sequences are comparable position by position.
4. **Execute & compare** — run both under a deterministic sandbox, normalize
   harmless differences (float precision, collection order, whitespace, exception
   type), let the LLM adjudicate any *residual* difference as real-vs-cosmetic,
   then decide by pass-rate ≥ θ. If a fragment cannot be made runnable (or no
   behavioral evidence can be produced), the pipeline **falls back to a direct LLM
   judgment** and flags the outcome (`extra['fallback'] == 'llm_direct'`) so
   executed and fallback verdicts can be reported separately. Set
   `decision.llm_fallback_on_exec_fail = False` to instead abstain (`Undecided`)
   — useful for measuring the execution pipeline's raw coverage.

## Prerequisites

| Need | Why | Check |
|------|-----|-------|
| Python 3.11+ | orchestrator | `python --version` |
| JDK 21 (`javac`, `java`) | Java execution | `javac -version` |
| Docker | **required** for C/C++ (no host gcc); optional hardening for Java | `docker --version` |

Configure the LLM backend by copying `.env.example` to `.env` (git-ignored) and
filling in your key:

```
LLM_API_KEY=your-api-key-here
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Quick start

```bash
# verify the LLM endpoint (one live API call)
python -m attest.smoke_llm

# run the offline unit suite (executor, JSON protocol, normalizer, metrics)
pytest

# run the live end-to-end gate (real API + JDK)
pytest -m live tests/test_gate_e2e.py

# detect a single pair
python -m attest.pipeline --pair A.java B.java [--label 1] [--docker]

# evaluate a dataset: full pipeline vs the LLM-direct baseline
python -m attest.eval.run_eval --dataset bcb --limit 20 --methods full direct

# ablations: no-exec (text similarity instead of behavior), no-label, no-diff
python -m attest.eval.run_eval --dataset ojclone --limit 10 --methods full no-exec
```

## Layout

```
attest/              orchestrator package
  config.py            central knobs: LLM endpoint, thresholds, sandbox caps
  llm.py               OpenAI-compatible client with on-disk response cache
  schemas.py           typed contract / pair / verdict data model
  pipeline.py          end-to-end driver for a single pair
  stage1_comprehend.py comprehension + unified contract
  stage2_make_runnable.py  executable reconstruction (+ repair_loop.py, harness_fill.py)
  stage3_synth_inputs.py   shared input synthesis
  stage4_execute_compare.py  execution, normalization, verdict
  normalize.py         deterministic, model-free difference normalization
  depgate.py           external-dependency gate (guards against stubbed clones)
  executors/           sandboxed Java / C++ runners (subprocess + optional Docker)
  datasets/            benchmark loaders
  eval/                metrics, baselines, ablations, dataset runner
harness_support/     hand-written JSON libs + harness templates (java/, cpp/) — the LLM never edits these
tests/               pytest: JSON round-trip, protocol, executor smoke, end-to-end gate
```

## Configuration

All tunable knobs live in `attest/config.py` and can be overridden via `.env` or
environment variables:

- **Decision** — `pass_rate_theta` (agreement threshold θ), repair budgets,
  float tolerances, the `llm_fallback_on_exec_fail` and `external_dependency_gate`
  toggles.
- **Execution** — per-case and whole-harness timeouts, JVM heap/GC caps, Docker
  image/memory/CPU/pids limits (`config.with_docker(True)`).
- **Ablations** — `no_label`, `no_diff_explainer`, `no_execution`
  (`config.with_ablation(...)`), each disabling one sub-component so its
  contribution can be measured.

## Notes

- **Sandboxing.** Each run executes in an isolated temporary scratch directory
  with a wall-clock timeout, process-tree kill, heap/CPU caps, and no stdin.
  Docker runs (and all C/C++ runs) add `--network none`, a read-only root, and
  resource limits.
- **Reproducibility.** LLM decoding is deterministic (`temperature=0`) and
  responses are cached on disk under `.llm_cache/`, so re-runs of the pipeline
  are stable.
- This is a research artifact accompanying an anonymous submission and is
  released for review and reproduction.
