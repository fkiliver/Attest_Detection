# Attest Gate Selective Correction Method

This directory contains the method code for using DSFM as the base clone
detector and applying a selective correction gate only when evidence indicates
that the base prediction is risky.

No trained checkpoint, generated prediction file, metric table, or experiment
result is included here.

## Method Boundary

The method has four stages:

1. DSFM produces the base clone/non-clone prediction for each pair.
2. DSFM predictions are normalized into a triplet format:

   ```text
   function_id_a function_id_b label [confidence] [margin]
   ```

3. Evidence cards provide optional semantic/dynamic/context evidence for the
   same function-id pairs.
4. The selective gate decides whether to keep the DSFM prediction or override it
   with the evidence-side prediction.

The gate is not a clone classifier by itself. It is a correction policy over an
existing DSFM prediction stream.

## Included Files

| Path | Role |
|---|---|
| `attest_gate/selective_gate.py` | Core gate feature extraction, heuristic scoring, learned logistic gate, evaluation, and threshold tuning. |
| `attest_gate/config.py` | Default DSFM base-model paths and runtime constants. |
| `attest_gate/dynamic_router.py` | Minimal compatibility shim used by the DSFM prediction normalizer. |
| `scripts/run_dsfm_export_predictions.py` | Export per-pair DSFM predictions from a DSFM checkpoint and processed DSFM split. |
| `scripts/prepare_dsfm_base_predictions.py` | Normalize DSFM/CSV/JSONL/triplet prediction files into the base prediction format. |
| `scripts/apply_selective_correction_gate.py` | Apply a heuristic selective gate to DSFM predictions and evidence cards. |
| `scripts/evaluate_selective_correction_gate.py` | Evaluate/tune the heuristic gate when gold labels are available. |
| `scripts/train_selective_correction_gate.py` | Train a lightweight learned logistic gate from evidence cards. |
| `scripts/tune_selective_gate_projection.py` | Tune a threshold by projected full-test precision/recall/F1. |
| `scripts/project_selective_gate_full_test.py` | Project correction deltas from error/guard rows onto a full-test baseline. |
| `scripts/check_selective_gate_deployment.py` | Check row consistency and basic readiness for a generated gate output. |
| `examples/heuristic_policy_example.json` | Minimal example policy file. |

## Required Inputs

- DSFM repository/source and checkpoint if using
  `run_dsfm_export_predictions.py`.
- A dataset split in DSFM processed format, or an already exported DSFM
  prediction file.
- Evidence cards in JSONL format. Each card should contain:
  - function ids;
  - an evidence-side decision label;
  - optional confidence, dynamic evidence, context-completion status, and local
    feature summaries.
- Gold labels are required only for evaluation, training, or threshold tuning.

## Basic Commands

Export DSFM predictions:

```powershell
python -B scripts\run_dsfm_export_predictions.py `
  --dsfm-repo ..\baseline_reproduction_methods\source_snapshots\DSFM `
  --data-dir <processed_dsfm_dataset> `
  --checkpoint <DSFM_checkpoint.pt> `
  --pair-map <test_pair_id_map.txt> `
  --output runs\dsfm_base_predictions.txt
```

Normalize an existing prediction file:

```powershell
python -B scripts\prepare_dsfm_base_predictions.py `
  --input <raw_dsfm_predictions.jsonl_or_csv_or_txt> `
  --output runs\dsfm_base_predictions.txt
```

Tune a heuristic gate when gold labels are available:

```powershell
python -B scripts\evaluate_selective_correction_gate.py `
  --cards <evidence_cards.jsonl> `
  --actual <gold_test.txt> `
  --predictions runs\dsfm_base_predictions.txt `
  --grid-start 0.0 `
  --grid-stop 1.6 `
  --grid-step 0.01 `
  --output runs\gate_eval.json `
  --csv runs\gate_rows.csv
```

Apply a fixed policy without gold labels:

```powershell
python -B scripts\apply_selective_correction_gate.py `
  --predictions runs\dsfm_base_predictions.txt `
  --cards <evidence_cards.jsonl> `
  --policy-file examples\heuristic_policy_example.json `
  --output-predictions runs\attest_gate_predictions.txt `
  --output-summary runs\attest_gate_summary.json
```

Train a learned gate:

```powershell
python -B scripts\train_selective_correction_gate.py `
  --train-cards <train_cards.jsonl> `
  --calibration-cards <calibration_cards.jsonl> `
  --actual <gold_test.txt> `
  --predictions runs\dsfm_base_predictions.txt `
  --output-model runs\learned_gate_model.json `
  --output-summary runs\learned_gate_summary.json
```

## Policy Semantics

The default heuristic gate computes an override score from:

- evidence-side confidence;
- DSFM/evidence disagreement;
- dynamic execution status;
- context-completion status;
- whether executable evidence agrees with the evidence-side prediction;
- retained source/context fidelity;
- framework or missing-context risk flags;
- optional BCB-style LLM alignment flags.

An override is allowed only when the DSFM prediction and evidence-side
prediction disagree and the score exceeds the selected threshold.

## Output Boundary

Outputs generated by these scripts should be written outside this method
directory, for example under a local `runs/` directory. Keep generated
predictions, metrics, trained models, and summaries out of the release package
unless they are intentionally being published as separate result artifacts.
