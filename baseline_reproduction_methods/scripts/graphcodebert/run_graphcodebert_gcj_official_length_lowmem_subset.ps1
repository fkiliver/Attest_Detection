param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string]$SourceDataDir = (Join-Path $Root 'eviclone_runs\baseline_reproduction\graphcodebert_dsfm_splits\GCJ'),
    [string]$SubsetDir = (Join-Path $Root 'eviclone_runs\baseline_reproduction\graphcodebert_gcj_official_length_lowmem_subset'),
    [string]$OutputDir = (Join-Path $Root 'eviclone_runs\baseline_reproduction\graphcodebert_gcj_official_length_lowmem_b1_ga16_model'),
    [string]$MetricsPath = (Join-Path $Root 'eviclone_runs\baseline_reproduction\graphcodebert_gcj_official_length_lowmem_b1_ga16_metrics.json'),
    [string]$MetricsReportPath = (Join-Path $Root 'eviclone_runs\baseline_reproduction\graphcodebert_gcj_official_length_lowmem_b1_ga16_metrics.md'),
    [string]$RunLabel = 'GraphCodeBERT GCJ official-length lowmem subset b1 ga16',
    [int]$TrainRows = 512,
    [int]$ValidRows = 256,
    [int]$TestRows = 256,
    [string]$Python = 'python'
)

$ErrorActionPreference = 'Stop'
$SourceDataDir = if ([System.IO.Path]::IsPathRooted($SourceDataDir)) { $SourceDataDir } else { Join-Path $Root $SourceDataDir }
$SubsetDir = if ([System.IO.Path]::IsPathRooted($SubsetDir)) { $SubsetDir } else { Join-Path $Root $SubsetDir }
$OutputDir = if ([System.IO.Path]::IsPathRooted($OutputDir)) { $OutputDir } else { Join-Path $Root $OutputDir }
$MetricsPath = if ([System.IO.Path]::IsPathRooted($MetricsPath)) { $MetricsPath } else { Join-Path $Root $MetricsPath }
$MetricsReportPath = if ([System.IO.Path]::IsPathRooted($MetricsReportPath)) { $MetricsReportPath } else { Join-Path $Root $MetricsReportPath }
$baselineRoot = (Resolve-Path (Join-Path $Root 'eviclone_runs\baseline_reproduction')).Path
$resolvedOutputParent = (Resolve-Path (Split-Path -Parent $OutputDir)).Path
if (-not $resolvedOutputParent.StartsWith($baselineRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write outside baseline_reproduction: $OutputDir"
}

$python = (Get-Command $Python -ErrorAction Stop).Source
$runDir = Join-Path (Resolve-Path (Join-Path $Root '..')).Path 'source_snapshots\GraphCodeBERT\clonedetection'
$logPath = Join-Path $OutputDir 'train_eval_test.log'
$timingPath = Join-Path $OutputDir 'run_timing.json'

New-Item -ItemType Directory -Force -Path $SubsetDir | Out-Null
if (Test-Path -LiteralPath $OutputDir) {
    $resolvedOutput = (Resolve-Path -LiteralPath $OutputDir).Path
    if (-not $resolvedOutput.StartsWith($baselineRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean outside baseline_reproduction: $resolvedOutput"
    }
    Remove-Item -LiteralPath $resolvedOutput -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$ErrorActionPreference = 'Continue'
& $python (Join-Path $Root 'scripts\build_triplet_split_subset.py') `
  --source-dir $SourceDataDir `
  --output-dir $SubsetDir `
  --dataset-name GCJ-official-length-lowmem-subset `
  --train-rows $TrainRows `
  --valid-rows $ValidRows `
  --test-rows $TestRows `
  --seed 20260626 `
  --balanced | Tee-Object -FilePath (Join-Path $OutputDir 'subset_build.log')

$env:TOKENIZERS_PARALLELISM = 'false'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location $runDir

$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $python run.py `
  --train_data_file (Join-Path $SubsetDir 'train.txt') `
  --eval_data_file (Join-Path $SubsetDir 'valid.txt') `
  --test_data_file (Join-Path $SubsetDir 'test.txt') `
  --output_dir $OutputDir `
  --model_name_or_path microsoft/graphcodebert-base `
  --config_name microsoft/graphcodebert-base `
  --tokenizer_name microsoft/graphcodebert-base `
  --do_train --do_eval --do_test `
  --code_length 512 `
  --data_flow_length 128 `
  --train_batch_size 1 `
  --eval_batch_size 1 `
  --gradient_accumulation_steps 16 `
  --learning_rate 2e-5 `
  --epochs 1 `
  --num_workers 0 `
  --seed 42 2>&1 | Tee-Object -FilePath $logPath
$code = $LASTEXITCODE
$sw.Stop()

$timing = @{
    schema_version = 'eviclone-run-timing/v1'
    command = $RunLabel
    exit_code = $code
    elapsed_seconds = [math]::Round($sw.Elapsed.TotalSeconds, 3)
    source_data_dir = $SourceDataDir
    subset_dir = $SubsetDir
    output_dir = $OutputDir
    train_rows = $TrainRows
    valid_rows = $ValidRows
    test_rows = $TestRows
    code_length = 512
    data_flow_length = 128
    train_batch_size = 1
    eval_batch_size = 1
    gradient_accumulation_steps = 16
    effective_train_batch_size = 16
    epochs = 1
    seed = 42
} 
$timing | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $timingPath

if ($code -eq 0) {
    Set-Location $Root
    & $python (Join-Path $Root 'scripts\evaluate_triplet_predictions.py') `
      --gold (Join-Path $SubsetDir 'test.txt') `
      --predictions (Join-Path $OutputDir 'predictions.txt') `
      --output $MetricsPath `
      --report $MetricsReportPath `
      --dataset $RunLabel `
      --method GraphCodeBERT-official-length-lowmem `
      --source 'source_snapshots/GraphCodeBERT/clonedetection/run.py'
    exit $LASTEXITCODE
}

exit $code
