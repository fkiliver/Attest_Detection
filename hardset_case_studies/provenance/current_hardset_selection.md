# Current HardSet Selection

Status: `active`

The active dataset is the filtered, original-label HardSet:

- Dataset: `BCB-LLM-Refined-HardCases-balanced`.
- Rows: 772.
- Labels: non-clone=386, clone=386.
- Label policy: original BCB labels unchanged.
- Source benchmark: CodeXGLUE BigCloneBench.
- Source cases: misclassifications pooled from clone detectors.
- Selection: pooled detector error cases filtered by LLM audit consistency with
  BCB labels, confidence >= 0.85, excluding benchmark-preference-bias cases,
  then balanced 1:1.

## Active Files

- `dataset/bcb_llm_refined_hard_cases/test.txt`
- `dataset/bcb_llm_refined_hard_cases/pairs.jsonl`
- `dataset/bcb_llm_refined_hard_cases/data.jsonl`
- `dataset/bcb_llm_refined_hard_cases/summary.json`

## Boundary

This provenance file records only the dataset selection policy and counts. It
does not include baseline result tables, generated predictions, or evaluation
metrics.
