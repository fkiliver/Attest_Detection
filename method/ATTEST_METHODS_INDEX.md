# Attest Method Index

This file records the methods packaged in this hard-case artifact release.

## Current Method

### `attest_exec_method`

`attest_exec_method/` is the current paper-facing method. It removes the dynamic
router and static/base-model dependency from the decision path. Every selected
pair is processed by the same execution-evidence pipeline:

- `attest_stage1_comprehend`: infer functional intent and build a shared
  behavioral contract.
- `attest_stage2_make_runnable`: reconstruct missing context and produce
  executable harnesses while preserving the target snippet.
- `attest_stage3_synth_inputs`: synthesize shared probes that exercise normal,
  boundary, and distinguishing behavior.
- `attest_stage4_execute_compare`: execute both sides, normalize outputs, and
  compare observable behavior.
- `attest_eval`: evaluate raw execution coverage, fallback behavior, ablations,
  and metric projections.

This is the method to cite as the main system in the paper.

## Historical / Ablation Method

### `attest_gate_method`

`attest_gate_method/` is the earlier selective correction gate. It assumes an
external base detector such as DSFM and decides whether to keep the base
prediction or use evidence-side correction. It is useful for explaining the
development path and for ablation/overlay analysis, but it is not the current
static-model-free Attest pipeline.

## Baselines

`baseline_reproduction_methods/` contains scripts and source snapshots for
external baselines such as GraphCodeBERT, DSFM, MRT-OAST, Prism, HOLMES, and
LLM-direct. These are not part of Attest; they are evaluation comparators.

## Naming

All packaged methods use the anonymized `attest_...` prefix. The original
development package names and internal experiment names are intentionally not
used as paper-facing method names in this release.
