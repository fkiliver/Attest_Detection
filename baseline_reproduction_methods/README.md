# Baseline Reproduction Methods

This directory contains method source snapshots and local adapter/run scripts
used to reproduce baseline methods on BCB, OJClone, GCJ, and the HardSet
dataset.

It intentionally excludes:

- generated predictions;
- metric/result files;
- diagnostic reports;
- checkpoints and pretrained model weights;
- large released datasets and compressed archives;
- logs and wrong-case output folders;
- API keys.

## Layout

| Path | Contents |
|---|---|
| `scripts/graphcodebert/` | Local GraphCodeBERT wrappers and dataset adapters. |
| `scripts/dsfm/` | DSFM dataset/adaptation/export scripts. |
| `scripts/mrt_oast/` | MRT-OAST extraction and run adapters. |
| `scripts/prism/` | Prism dataset, array, compile, and run adapters. |
| `scripts/holmes/` | HOLMES source-graph and dataset adapters plus runner scripts. |
| `scripts/llm_direct/` | LLM-direct input preparation, execution, and output-retention helpers. |
| `source_snapshots/GraphCodeBERT/` | Official GraphCodeBERT clone-detection source snapshot, excluding bundled result/data files. |
| `source_snapshots/DSFM/` | DSFM source snapshot, excluding datasets and pretrained weights. |
| `source_snapshots/MRT-OAST/` | MRT-OAST source snapshot, excluding origin data, result CSVs, and wrong-case outputs. |
| `source_snapshots/Prism/` | Prism source snapshot, excluding Python bytecode caches. |
| `source_snapshots/HOLMES/` | HOLMES model source snapshot, excluding large Drive data archives. |

## Notes

Some scripts preserve absolute paths from the local reproduction workspace. When
rerunning elsewhere, update path constants or command-line arguments to point to
the local dataset, external source snapshot, and output directories.

LLM-direct scripts require the caller to provide an API key through the runtime
environment or command-line configuration. No key is stored in this package.

This directory is a method-reproduction bundle, not an evaluation-output bundle.
