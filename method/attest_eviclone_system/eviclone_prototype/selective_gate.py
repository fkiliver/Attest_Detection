from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PairKey = tuple[str, str]


@dataclass(frozen=True)
class BaselineRow:
    function_id_a: str
    function_id_b: str
    gold: int
    prediction: int


LEARNED_FEATURE_NAMES = [
    "bias",
    "ours_confidence",
    "ours_pred_is_positive",
    "gcb_pred_is_positive",
    "dynamic_executed",
    "dynamic_compile_failed",
    "dynamic_context_compile_success_no_probe",
    "dynamic_context_compile_failed",
    "dynamic_execution_failed",
    "dynamic_timeout",
    "dynamic_agrees_with_ours",
    "dynamic_conflicts_with_ours",
    "context_completed",
    "context_not_recoverable",
    "context_rejected",
    "context_failed",
    "context_level_high",
    "context_changed_original_logic",
    "identifier_similarity",
    "shared_family_count",
    "risk_count",
    "llm_risk_count",
    "heuristic_override_score",
    "heuristic_score_ge_131",
    "heuristic_score_ge_144",
    "probe_result_available",
    "probe_result_same",
    "probe_result_different",
    "probe_compile_only_result",
    "context_source_artifact_retained",
    "context_source_hash_recorded",
    "context_source_artifact_path_recorded",
    "context_high_fidelity_retained_source",
    "framework_or_missing_context_risk",
    "llm_bcb_alignment_positive",
    "llm_bcb_alignment_negative",
]


@dataclass(frozen=True)
class LearnedGateModel:
    feature_names: list[str]
    weights: list[float]
    threshold: float

    def score(self, features: dict[str, Any]) -> float:
        vector = learned_feature_vector(features)
        z = sum(weight * value for weight, value in zip(self.weights, vector))
        return sigmoid(z)

    def should_override(self, features: dict[str, Any]) -> bool:
        if not features.get("gcb_ours_disagree"):
            return False
        return self.score(features) >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_type": "linear_logistic_selective_gate",
            "feature_names": self.feature_names,
            "weights": self.weights,
            "threshold": self.threshold,
        }

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "LearnedGateModel":
        return cls(
            feature_names=list(obj["feature_names"]),
            weights=[float(x) for x in obj["weights"]],
            threshold=float(obj["threshold"]),
        )


def pair_key(function_id_a: str, function_id_b: str) -> PairKey:
    return str(function_id_a), str(function_id_b)


def card_pair_key(card: dict[str, Any]) -> PairKey:
    ids = card.get("function_ids") or {}
    return pair_key(str(ids.get("a", "")), str(ids.get("b", "")))


def load_baseline_rows(actual_path: Path, predictions_path: Path) -> dict[PairKey, BaselineRow]:
    actual_rows = read_triplet_file(actual_path)
    pred_rows = read_triplet_file(predictions_path)
    if len(actual_rows) != len(pred_rows):
        raise ValueError(f"actual/prediction row count mismatch: {len(actual_rows)} != {len(pred_rows)}")

    result: dict[PairKey, BaselineRow] = {}
    for idx, (actual, pred) in enumerate(zip(actual_rows, pred_rows), start=1):
        if actual[0] != pred[0] or actual[1] != pred[1]:
            raise ValueError(f"pair mismatch at row {idx}: actual={actual[:2]} prediction={pred[:2]}")
        result[pair_key(actual[0], actual[1])] = BaselineRow(
            function_id_a=actual[0],
            function_id_b=actual[1],
            gold=int(actual[2]),
            prediction=int(pred[2]),
        )
    return result


def read_triplet_file(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) < 3:
                raise ValueError(f"expected at least 3 columns at {path}:{line_no}, got {len(parts)}")
            rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def load_cards(path: Path) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                cards.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid card JSON at {path}:{line_no}: {exc}") from exc
    return cards


def card_features(card: dict[str, Any], baseline: BaselineRow | None = None) -> dict[str, Any]:
    decision = card.get("decision") or {}
    dynamic = card.get("dynamic_evidence") or {}
    local = card.get("local_evidence") or {}
    llm = card.get("llm_evidence") or {}
    parsed = dynamic.get("execution", {}).get("parsed") if isinstance(dynamic.get("execution"), dict) else None
    context = dynamic.get("llm_context_completion") if isinstance(dynamic, dict) else None
    context_payload = context.get("payload") if isinstance(context, dict) else None
    preservation = context_payload.get("semantic_preservation") if isinstance(context_payload, dict) else None
    artifact = context.get("source_artifact") if isinstance(context, dict) and isinstance(context.get("source_artifact"), dict) else {}
    payload_source_sha = context_payload.get("java_source_sha256") if isinstance(context_payload, dict) else None

    ours_pred = coerce_label(decision.get("pred_label"))
    gcb_pred = baseline.prediction if baseline else None
    gold = baseline.gold if baseline else coerce_label((card.get("gold") or {}).get("label"))
    dynamic_pred = None
    if dynamic.get("status") == "executed" and isinstance(parsed, dict) and parsed.get("same") in (True, False):
        dynamic_pred = 1 if parsed.get("same") is True else 0

    risk_flags = list(decision.get("risk_flags") or [])
    llm_risks = list(llm.get("semantic_risk_flags") or []) if isinstance(llm, dict) else []
    preservation_risks = list(preservation.get("risk_flags") or []) if isinstance(preservation, dict) else []
    shared_families = list(local.get("shared_feature_families") or []) if isinstance(local, dict) else []
    context_status = context.get("status") if isinstance(context, dict) else "none"
    context_level = ""
    changed_original_logic = False
    if isinstance(preservation, dict):
        context_level = str(preservation.get("level") or "")
        changed = preservation.get("changed_original_logic")
        changed_original_logic = changed is True or str(changed).strip().lower() in {"true", "yes", "1"}
    parsed_status = str(parsed.get("status") or "") if isinstance(parsed, dict) else ""
    artifact_retained = artifact.get("retained") is True
    artifact_path_recorded = bool(artifact.get("path"))
    artifact_sha_recorded = bool(artifact.get("sha256"))
    context_source_hash_recorded = artifact_sha_recorded or bool(payload_source_sha)
    risk_text = " ".join(str(item).lower() for item in risk_flags + llm_risks + preservation_risks)
    framework_or_missing_context_risk = any(
        marker in risk_text
        for marker in [
            "framework",
            "missing_context",
            "missing field",
            "missing_field",
            "stub",
            "servlet",
            "swing",
            "gui",
            "database",
            "jdbc",
            "db",
        ]
    )
    bcb_gold_verdict = str(llm.get("bcb_gold_verdict") or "") if isinstance(llm, dict) else ""

    return {
        "pair_id": card.get("pair_id"),
        "gold": gold,
        "gcb_pred": gcb_pred,
        "ours_pred": ours_pred,
        "ours_confidence": safe_float(decision.get("confidence"), 0.0),
        "ours_verdict": str(decision.get("verdict") or ""),
        "gcb_ours_disagree": ours_pred in (0, 1) and gcb_pred in (0, 1) and ours_pred != gcb_pred,
        "dynamic_status": str(dynamic.get("status") or "not_run"),
        "dynamic_pred": dynamic_pred,
        "dynamic_agrees_with_ours": dynamic_pred in (0, 1) and dynamic_pred == ours_pred,
        "dynamic_conflicts_with_ours": dynamic_pred in (0, 1) and ours_pred in (0, 1) and dynamic_pred != ours_pred,
        "context_status": str(context_status or "none"),
        "context_level": context_level,
        "context_changed_original_logic": changed_original_logic,
        "probe_result_available": dynamic_pred in (0, 1),
        "probe_result_same": dynamic_pred == 1,
        "probe_result_different": dynamic_pred == 0,
        "probe_parsed_status": parsed_status,
        "context_source_artifact_retained": artifact_retained,
        "context_source_hash_recorded": context_source_hash_recorded,
        "context_source_artifact_path_recorded": artifact_path_recorded,
        "context_high_fidelity_retained_source": (
            str(context_status or "") == "completed"
            and str(context_level or "").lower() == "high"
            and not changed_original_logic
            and artifact_retained
            and context_source_hash_recorded
        ),
        "framework_or_missing_context_risk": framework_or_missing_context_risk,
        "llm_bcb_alignment_positive": bcb_gold_verdict in {"behaviorally_supported_clone", "likely_clone"},
        "llm_bcb_alignment_negative": bcb_gold_verdict in {"likely_non_clone", "non_clone_supported"},
        "llm_status": str(llm.get("status") or "success") if isinstance(llm, dict) else "not_run",
        "identifier_similarity": safe_float(local.get("identifier_similarity"), 0.0) if isinstance(local, dict) else 0.0,
        "shared_family_count": len(shared_families),
        "risk_count": len(risk_flags),
        "llm_risk_count": len(llm_risks),
    }


def default_override_score(features: dict[str, Any]) -> float:
    ours_pred = features.get("ours_pred")
    gcb_pred = features.get("gcb_pred")
    if ours_pred not in (0, 1) or gcb_pred not in (0, 1):
        return -math.inf
    if ours_pred == gcb_pred:
        return -math.inf
    if features.get("ours_verdict") in {"context_insufficient", "unknown"}:
        return -math.inf
    if features.get("llm_status") == "failed":
        return -math.inf

    score = safe_float(features.get("ours_confidence"), 0.0)
    dynamic_status = str(features.get("dynamic_status") or "")
    context_status = str(features.get("context_status") or "")

    score += {
        "executed": 0.18,
        "llm_context_compile_success_no_probe": -0.02,
        "compile_failed": -0.08,
        "llm_context_compile_failed": -0.10,
        "llm_context_execution_failed": -0.12,
        "timeout": -0.18,
    }.get(dynamic_status, -0.05)

    score += {
        "completed": 0.04,
        "not_recoverable": -0.04,
        "rejected": -0.08,
        "failed": -0.18,
        "none": -0.04,
    }.get(context_status, -0.04)

    if features.get("dynamic_agrees_with_ours"):
        score += 0.25
    if features.get("dynamic_conflicts_with_ours"):
        score -= 0.45
    if str(features.get("context_level") or "").lower() == "high":
        score += 0.03
    if features.get("context_changed_original_logic"):
        score -= 0.35

    score += min(int(features.get("shared_family_count") or 0), 3) * 0.025
    score += min(safe_float(features.get("identifier_similarity"), 0.0), 0.4) * 0.10
    score -= min(int(features.get("risk_count") or 0), 8) * 0.015
    score -= min(int(features.get("llm_risk_count") or 0), 8) * 0.010
    return round(score, 6)


def evaluate_gate(
    cards: Iterable[dict[str, Any]],
    baseline_rows: dict[PairKey, BaselineRow],
    *,
    threshold: float,
) -> dict[str, Any]:
    counters = Counter()
    by_dynamic = Counter()
    by_context = Counter()
    rows: list[dict[str, Any]] = []
    for card in cards:
        key = card_pair_key(card)
        baseline = baseline_rows.get(key)
        if baseline is None:
            counters["missing_baseline"] += 1
            continue
        features = card_features(card, baseline)
        score = default_override_score(features)
        override = bool(features.get("gcb_ours_disagree")) and score >= threshold
        gcb_pred = int(features["gcb_pred"])
        ours_pred = features.get("ours_pred")
        gold = int(features["gold"])
        final_pred = int(ours_pred) if override and ours_pred in (0, 1) else gcb_pred

        baseline_correct = gcb_pred == gold
        ours_correct = ours_pred == gold if ours_pred in (0, 1) else False
        final_correct = final_pred == gold
        counters["total"] += 1
        counters["baseline_correct"] += int(baseline_correct)
        counters["ours_full_correct"] += int(ours_correct)
        counters["gate_correct"] += int(final_correct)
        counters["override"] += int(override)
        counters["keep"] += int(not override)
        counters["candidate_disagreement"] += int(bool(features.get("gcb_ours_disagree")))
        if override:
            by_dynamic[str(features.get("dynamic_status"))] += 1
            by_context[str(features.get("context_status"))] += 1
            if ours_correct and not baseline_correct:
                counters["benefit"] += 1
            elif baseline_correct and not ours_correct:
                counters["harm"] += 1
            else:
                counters["neutral_override"] += 1
        rows.append(
            {
                "pair_id": features.get("pair_id"),
                "function_id_a": key[0],
                "function_id_b": key[1],
                "gold": gold,
                "gcb_pred": gcb_pred,
                "ours_pred": ours_pred,
                "score": score,
                "override": override,
                "final_pred": final_pred,
                "baseline_correct": baseline_correct,
                "ours_correct": ours_correct,
                "final_correct": final_correct,
                "dynamic_status": features.get("dynamic_status"),
                "context_status": features.get("context_status"),
                "ours_confidence": features.get("ours_confidence"),
                "ours_verdict": features.get("ours_verdict"),
            }
        )
    total = counters["total"]
    benefit = counters["benefit"]
    harm = counters["harm"]
    override_count = counters["override"]
    result = {
        "threshold": threshold,
        "total": total,
        "missing_baseline": counters["missing_baseline"],
        "baseline_correct": counters["baseline_correct"],
        "ours_full_correct": counters["ours_full_correct"],
        "gate_correct": counters["gate_correct"],
        "baseline_accuracy": ratio(counters["baseline_correct"], total),
        "ours_full_accuracy": ratio(counters["ours_full_correct"], total),
        "gate_accuracy": ratio(counters["gate_correct"], total),
        "candidate_disagreement": counters["candidate_disagreement"],
        "override_count": override_count,
        "override_rate": ratio(override_count, total),
        "benefit": benefit,
        "harm": harm,
        "neutral_override": counters["neutral_override"],
        "net_gain": benefit - harm,
        "override_precision": ratio(benefit, benefit + harm),
        "override_by_dynamic_status": dict(by_dynamic.most_common()),
        "override_by_context_status": dict(by_context.most_common()),
        "rows": rows,
    }
    return result


def evaluate_learned_gate(
    cards: Iterable[dict[str, Any]],
    baseline_rows: dict[PairKey, BaselineRow],
    model: LearnedGateModel,
) -> dict[str, Any]:
    counters = Counter()
    rows: list[dict[str, Any]] = []
    for card in cards:
        key = card_pair_key(card)
        baseline = baseline_rows.get(key)
        if baseline is None:
            counters["missing_baseline"] += 1
            continue
        features = card_features(card, baseline)
        score = model.score(features)
        override = model.should_override(features)
        gcb_pred = int(features["gcb_pred"])
        ours_pred = features.get("ours_pred")
        gold = int(features["gold"])
        final_pred = int(ours_pred) if override and ours_pred in (0, 1) else gcb_pred

        baseline_correct = gcb_pred == gold
        ours_correct = ours_pred == gold if ours_pred in (0, 1) else False
        final_correct = final_pred == gold
        counters["total"] += 1
        counters["baseline_correct"] += int(baseline_correct)
        counters["ours_full_correct"] += int(ours_correct)
        counters["gate_correct"] += int(final_correct)
        counters["override"] += int(override)
        counters["keep"] += int(not override)
        counters["candidate_disagreement"] += int(bool(features.get("gcb_ours_disagree")))
        if override:
            if ours_correct and not baseline_correct:
                counters["benefit"] += 1
            elif baseline_correct and not ours_correct:
                counters["harm"] += 1
            else:
                counters["neutral_override"] += 1
        rows.append(
            {
                "pair_id": features.get("pair_id"),
                "function_id_a": key[0],
                "function_id_b": key[1],
                "gold": gold,
                "gcb_pred": gcb_pred,
                "ours_pred": ours_pred,
                "score": round(score, 6),
                "override": override,
                "final_pred": final_pred,
                "baseline_correct": baseline_correct,
                "ours_correct": ours_correct,
                "final_correct": final_correct,
                "dynamic_status": features.get("dynamic_status"),
                "context_status": features.get("context_status"),
                "ours_confidence": features.get("ours_confidence"),
                "ours_verdict": features.get("ours_verdict"),
            }
        )
    return gate_result_from_counters(counters, model.threshold, rows)


def gate_result_from_counters(counters: Counter, threshold: float, rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = counters["total"]
    benefit = counters["benefit"]
    harm = counters["harm"]
    override_count = counters["override"]
    return {
        "threshold": threshold,
        "total": total,
        "missing_baseline": counters["missing_baseline"],
        "baseline_correct": counters["baseline_correct"],
        "ours_full_correct": counters["ours_full_correct"],
        "gate_correct": counters["gate_correct"],
        "baseline_accuracy": ratio(counters["baseline_correct"], total),
        "ours_full_accuracy": ratio(counters["ours_full_correct"], total),
        "gate_accuracy": ratio(counters["gate_correct"], total),
        "candidate_disagreement": counters["candidate_disagreement"],
        "override_count": override_count,
        "override_rate": ratio(override_count, total),
        "benefit": benefit,
        "harm": harm,
        "neutral_override": counters["neutral_override"],
        "net_gain": benefit - harm,
        "override_precision": ratio(benefit, benefit + harm),
        "rows": rows,
    }


def tune_threshold(
    cards: list[dict[str, Any]],
    baseline_rows: dict[PairKey, BaselineRow],
    *,
    thresholds: Iterable[float],
    min_override_precision: float = 0.0,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    candidates: list[dict[str, Any]] = []
    for threshold in thresholds:
        result = evaluate_gate(cards, baseline_rows, threshold=threshold)
        compact = {k: v for k, v in result.items() if k != "rows"}
        candidates.append(compact)
        if result["override_count"] and result["override_precision"] < min_override_precision:
            continue
        if best is None or gate_sort_key(result) > gate_sort_key(best):
            best = result
    if best is None:
        best = evaluate_gate(cards, baseline_rows, threshold=math.inf)
    return {
        "best": best,
        "grid": candidates,
    }


def train_learned_gate(
    cards: list[dict[str, Any]],
    baseline_rows: dict[PairKey, BaselineRow],
    *,
    epochs: int = 300,
    learning_rate: float = 0.08,
    l2: float = 0.001,
    threshold_candidates: Iterable[float] | None = None,
    min_override_precision: float = 0.0,
) -> dict[str, Any]:
    examples = training_examples(cards, baseline_rows)
    if not examples:
        raise ValueError("no disagreement examples available for gate training")
    positives = sum(label for _, label in examples)
    negatives = len(examples) - positives
    pos_weight = len(examples) / (2 * positives) if positives else 1.0
    neg_weight = len(examples) / (2 * negatives) if negatives else 1.0

    weights = [0.0 for _ in LEARNED_FEATURE_NAMES]
    for _ in range(max(1, epochs)):
        grad = [0.0 for _ in weights]
        for vector, label in examples:
            pred = sigmoid(sum(w * x for w, x in zip(weights, vector)))
            sample_weight = pos_weight if label == 1 else neg_weight
            error = (pred - label) * sample_weight
            for idx, value in enumerate(vector):
                grad[idx] += error * value
        n = float(len(examples))
        for idx in range(len(weights)):
            regularizer = l2 * weights[idx] if idx != 0 else 0.0
            weights[idx] -= learning_rate * ((grad[idx] / n) + regularizer)

    raw_model = LearnedGateModel(feature_names=list(LEARNED_FEATURE_NAMES), weights=weights, threshold=0.5)
    thresholds = list(threshold_candidates or [i / 100 for i in range(0, 101)])
    best: dict[str, Any] | None = None
    grid: list[dict[str, Any]] = []
    for threshold in thresholds:
        model = LearnedGateModel(feature_names=list(LEARNED_FEATURE_NAMES), weights=weights, threshold=threshold)
        result = evaluate_learned_gate(cards, baseline_rows, model)
        compact = {k: v for k, v in result.items() if k != "rows"}
        grid.append(compact)
        if result["override_count"] and result["override_precision"] < min_override_precision:
            continue
        if best is None or gate_sort_key(result) > gate_sort_key(best):
            best = result
    if best is None:
        best = evaluate_learned_gate(cards, baseline_rows, raw_model)
    model = LearnedGateModel(feature_names=list(LEARNED_FEATURE_NAMES), weights=weights, threshold=float(best["threshold"]))
    return {
        "model": model,
        "training_examples": len(examples),
        "positive_examples": positives,
        "negative_examples": negatives,
        "best": best,
        "grid": grid,
    }


def tune_learned_gate_threshold(
    model: LearnedGateModel,
    cards: list[dict[str, Any]],
    baseline_rows: dict[PairKey, BaselineRow],
    *,
    threshold_candidates: Iterable[float] | None = None,
    min_override_precision: float = 0.0,
) -> dict[str, Any]:
    thresholds = list(threshold_candidates or [i / 100 for i in range(0, 101)])
    best: dict[str, Any] | None = None
    grid: list[dict[str, Any]] = []
    for threshold in thresholds:
        candidate = LearnedGateModel(model.feature_names, model.weights, threshold)
        result = evaluate_learned_gate(cards, baseline_rows, candidate)
        compact = {k: v for k, v in result.items() if k != "rows"}
        grid.append(compact)
        if result["override_count"] and result["override_precision"] < min_override_precision:
            continue
        if best is None or gate_sort_key(result) > gate_sort_key(best):
            best = result
    if best is None:
        best = evaluate_learned_gate(cards, baseline_rows, LearnedGateModel(model.feature_names, model.weights, math.inf))
    tuned_model = LearnedGateModel(model.feature_names, model.weights, float(best["threshold"]))
    return {
        "model": tuned_model,
        "best": best,
        "grid": grid,
    }


def training_examples(cards: list[dict[str, Any]], baseline_rows: dict[PairKey, BaselineRow]) -> list[tuple[list[float], int]]:
    examples: list[tuple[list[float], int]] = []
    for card in cards:
        baseline = baseline_rows.get(card_pair_key(card))
        if baseline is None:
            continue
        features = card_features(card, baseline)
        if not features.get("gcb_ours_disagree"):
            continue
        ours_pred = features.get("ours_pred")
        if ours_pred not in (0, 1):
            continue
        gold = int(features["gold"])
        gcb_pred = int(features["gcb_pred"])
        label = 1 if ours_pred == gold and gcb_pred != gold else 0
        examples.append((learned_feature_vector(features), label))
    return examples


def learned_feature_vector(features: dict[str, Any]) -> list[float]:
    dynamic = str(features.get("dynamic_status") or "")
    context = str(features.get("context_status") or "")
    level = str(features.get("context_level") or "").lower()
    parsed_status = str(features.get("probe_parsed_status") or "").lower()
    heuristic_score = default_override_score(features)
    if not math.isfinite(heuristic_score):
        heuristic_score = -1.0
    heuristic_score = max(-0.5, min(float(heuristic_score), 1.6))
    return [
        1.0,
        safe_float(features.get("ours_confidence"), 0.0),
        1.0 if features.get("ours_pred") == 1 else 0.0,
        1.0 if features.get("gcb_pred") == 1 else 0.0,
        1.0 if dynamic == "executed" else 0.0,
        1.0 if dynamic == "compile_failed" else 0.0,
        1.0 if dynamic == "llm_context_compile_success_no_probe" else 0.0,
        1.0 if dynamic == "llm_context_compile_failed" else 0.0,
        1.0 if dynamic in {"execution_failed", "llm_context_execution_failed"} else 0.0,
        1.0 if dynamic == "timeout" else 0.0,
        1.0 if features.get("dynamic_agrees_with_ours") else 0.0,
        1.0 if features.get("dynamic_conflicts_with_ours") else 0.0,
        1.0 if context == "completed" else 0.0,
        1.0 if context == "not_recoverable" else 0.0,
        1.0 if context == "rejected" else 0.0,
        1.0 if context == "failed" else 0.0,
        1.0 if level == "high" else 0.0,
        1.0 if features.get("context_changed_original_logic") else 0.0,
        min(safe_float(features.get("identifier_similarity"), 0.0), 1.0),
        min(float(features.get("shared_family_count") or 0), 5.0) / 5.0,
        min(float(features.get("risk_count") or 0), 10.0) / 10.0,
        min(float(features.get("llm_risk_count") or 0), 10.0) / 10.0,
        heuristic_score / 1.6,
        1.0 if heuristic_score >= 1.31 else 0.0,
        1.0 if heuristic_score >= 1.44 else 0.0,
        1.0 if features.get("probe_result_available") else 0.0,
        1.0 if features.get("probe_result_same") else 0.0,
        1.0 if features.get("probe_result_different") else 0.0,
        1.0 if parsed_status == "compile_only" or dynamic == "llm_context_compile_success_no_probe" else 0.0,
        1.0 if features.get("context_source_artifact_retained") else 0.0,
        1.0 if features.get("context_source_hash_recorded") else 0.0,
        1.0 if features.get("context_source_artifact_path_recorded") else 0.0,
        1.0 if features.get("context_high_fidelity_retained_source") else 0.0,
        1.0 if features.get("framework_or_missing_context_risk") else 0.0,
        1.0 if features.get("llm_bcb_alignment_positive") else 0.0,
        1.0 if features.get("llm_bcb_alignment_negative") else 0.0,
    ]


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def gate_sort_key(result: dict[str, Any]) -> tuple[Any, ...]:
    return (
        result.get("net_gain", 0),
        result.get("gate_correct", 0),
        result.get("override_precision", 0.0),
        -result.get("override_count", 0),
    )


def ratio(num: int | float, den: int | float) -> float:
    return round(float(num) / float(den), 6) if den else 0.0


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def coerce_label(value: Any) -> int | None:
    if value in (0, 1):
        return int(value)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed in (0, 1) else None


def threshold_grid(start: float = 0.0, stop: float = 1.5, step: float = 0.01) -> list[float]:
    result: list[float] = []
    current = start
    while current <= stop + 1e-9:
        result.append(round(current, 6))
        current += step
    return result
