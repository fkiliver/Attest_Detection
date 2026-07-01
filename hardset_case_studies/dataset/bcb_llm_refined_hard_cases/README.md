# BCB LLM-Refined Hard Cases

## Construction

- Source benchmark: CodeXGLUE BigCloneBench.
- Source cases: misclassifications pooled from clone detectors and audited by LLM.
- Selection: `agrees_with_bcb == true`, `confidence >= 0.85`, LLM
  `bcb_style_clone` matches the BCB label, and at least one pooled detector
  predicts the pair wrong.
- Default exclusion: `benchmark_preference_bias` cases are kept in the rejected
  audit file, not in the refined set.
- Root `data.jsonl`, `test.txt`, and `pairs.jsonl` are copies of the balanced
  split for direct benchmark use.

## Counts

- Full refined pool: 2,973 pairs, 526 functions, labels `0=2,587`, `1=386`.
- Balanced benchmark: 772 pairs, 370 functions, labels `0=386`, `1=386`.
- Rejected/audited cases: 3,577.

## Files

- `data.jsonl`: source snippets for the active balanced split.
- `test.txt`: active balanced pair labels.
- `pairs.jsonl`: active balanced pair metadata.
- `pairs_compact.csv`: compact spreadsheet-style view of active pairs.
- `llm_case_studies.jsonl`: richer active case-study records with source
  excerpts.
- `summary.json`: dataset construction counts and selection metadata.
- `rejected_cases.jsonl`: audited records excluded by the selection policy.
- `balanced/`: explicit copy of the active 772-pair split.
- `full/`: 2,973-pair refined candidate pool before balancing.

This directory intentionally excludes generated baseline predictions, metric
files, and result reports.

## Reporting Boundary

This is a curated hard-case benchmark mined from several clone detectors'
errors and then filtered by LLM label audit. It is appropriate for stress-testing clone
detectors on verified difficult BCB cases, but it should not be reported as the
natural-distribution BCB test set.
