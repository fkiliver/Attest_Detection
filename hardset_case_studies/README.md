# HardSet, Case Studies, and Baseline Reproduction Methods

This directory packages five things:

- the active BCB hard-case dataset;
- the source case-study records used to construct and inspect it;
- baseline reproduction methods and adapter scripts;
- the static-model-free Attest execution method;
- the earlier Attest gate selective correction method retained as a historical
  overlay/ablation component.

The package intentionally contains no generated predictions, metric files,
checkpoints, or large external datasets.

## Main Dataset

- Benchmark split: `dataset/bcb_llm_refined_hard_cases/test.txt`
- Pair metadata: `dataset/bcb_llm_refined_hard_cases/pairs.jsonl`
- Source snippets: `dataset/bcb_llm_refined_hard_cases/data.jsonl`
- Compact pair view: `dataset/bcb_llm_refined_hard_cases/pairs_compact.csv`

The root files in `dataset/bcb_llm_refined_hard_cases/` mirror the active
balanced split: 772 pairs, with 386 clone pairs and 386 non-clone pairs. Labels
are the original BCB labels; they were not overwritten by LLM relabeling.

## Directory Layout

| Path | Contents |
|---|---|
| `dataset/bcb_llm_refined_hard_cases/` | Active HardSet dataset plus full refined pool and rejected-audit records. |
| `source_case_studies/all_error_case_studies/` | All 6,550 pooled clone-detector BCB error case-study records and Markdown shards. |
| `provenance/` | Dataset selection policy and counts, without baseline result tables. |
| `baseline_reproduction_methods/` | Reproduced baseline source snapshots and local adapter/run scripts. |
| `attest_exec_method/` | Current Attest execution-evidence method, without router or static base model dependency. |
| `attest_gate_method/` | Earlier DSFM-based selective correction gate implementation and run scripts, retained for ablation/history. |

## Baseline Reproduction Methods

The baseline methods are in `baseline_reproduction_methods/`:

- GraphCodeBERT
- DSFM
- MRT-OAST
- Prism
- HOLMES
- LLM-direct

Only method code and reproduction scripts are included. Outputs such as
predictions, metrics, result CSVs, reports, checkpoints, and large released
datasets are not included in this package.

## Attest Execution Method

The current method is in `attest_exec_method/`. It runs all selected code pairs
through an LLM-assisted executable reconstruction pipeline:

1. infer a shared behavioral contract;
2. complete missing snippet context and lower the pair into executable harnesses;
3. synthesize shared discriminating probes/inputs;
4. execute both sides and compare normalized observable behavior;
5. output clone, non-clone, or undecided with evidence metadata.

This method does not require GraphCodeBERT, DSFM, a dynamic router, or a
selective correction classifier. Those models can still be used as baselines in
paper evaluation, but they are outside the core Attest execution pipeline.

## Attest Gate Method

The earlier gate method is in `attest_gate_method/`. DSFM is used as the base
clone detector; the gate decides whether to keep the DSFM prediction or
selectively override it using evidence-side predictions. It is kept here because
it records the development path and supports ablation/overlay comparisons, but
it is not the final static-model-free pipeline.

## File Formats

`test.txt` uses the standard clone-detection triplet format:

```text
function_id_a function_id_b label
```

`data.jsonl` has one JSON object per function:

```json
{"idx": "function_id", "func": "source code"}
```

`pairs.jsonl` has one JSON object per pair with labels, method names, audit
category, recommended route, summaries, and compact evidence fields.

`llm_case_studies.jsonl` keeps richer case-study records with source excerpts.
Some early generated Chinese explanatory fields have mojibake from the original
runtime encoding; the structured English fields and code excerpts are the fields
used for analysis.

## Dataset Boundary

This is a curated hard-case benchmark mined from several clone detectors'
errors and then filtered by LLM label audit. It is appropriate for stress-testing clone
detectors on verified difficult BCB cases, but it is not the natural-distribution
BCB test set.

## Release Checks

This package was cleaned before release. A strict scan for long `sk-...` API-key
patterns was run after assembly. No key pattern was found.
