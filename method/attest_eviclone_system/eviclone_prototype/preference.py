from __future__ import annotations

import json
import math
import re
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .alignment import clamp01, code_marker_set, extract_hash_algorithms, feature_tokens, jaccard
from .dataset import ClonePair
from .evidence import VERDICT_TO_LABEL, append_reason


MODEL_SCHEMA = "eviclone-annotation-preference/v1"


def load_preference_model(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_preference_model(model: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def train_preference_model(
    cards: list[dict[str, Any]],
    *,
    pair_map: dict[int, ClonePair] | None = None,
    epochs: int = 80,
    learning_rate: float = 0.18,
    l2: float = 0.0008,
    target_l2: float = 0.004,
    target_min_examples: int = 5,
    adapter_strength: float = 1.0,
    preference_gate: float = 1.0,
    prototype_weight: float = 0.0,
    prototype_k: int = 9,
    prototype_min_similarity: float = 0.02,
    profile_prior_weight: float = 0.0,
    reference_mode: str = "decision",
    threshold: float = 0.5,
) -> dict[str, Any]:
    pair_map = pair_map or {}
    target_counts = Counter(str((card.get("target") or {}).get("name") or "") for card in cards)
    examples: list[dict[str, Any]] = []
    label_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    target_label_counts: dict[str, Counter[str]] = {}

    for card in cards:
        pair_id = int(card.get("pair_id", 0) or 0)
        target = str((card.get("target") or {}).get("name") or "")
        target_key = target if target_counts[target] >= int(target_min_examples) else "__rare__"
        label = int((card.get("gold") or {}).get("label", 0))
        tokens = sorted(preference_tokens(card, pair_map.get(pair_id), reference_mode=reference_mode))
        if not tokens:
            continue
        label_counts[str(label)] += 1
        token_counts.update(tokens)
        target_label_counts.setdefault(target_key, Counter())[str(label)] += 1
        examples.append(
            {
                "pair_id": pair_id,
                "target": target,
                "target_key": target_key,
                "gold_label": label,
                "tokens": tokens,
            }
        )

    weights = train_preference_weights(
        examples,
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
        target_l2=target_l2,
    )
    return {
        "schema_version": MODEL_SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "threshold": clamp01(threshold),
        "adapter_strength": max(0.0, float(adapter_strength)),
        "preference_gate": clamp01(preference_gate),
        "prototype_weight": clamp01(prototype_weight),
        "prototype_k": max(1, int(prototype_k)),
        "prototype_min_similarity": max(0.0, float(prototype_min_similarity)),
        "profile_prior_weight": clamp01(profile_prior_weight),
        "reference_mode": reference_mode if reference_mode in {"decision", "score", "semantic"} else "decision",
        "target_min_examples": max(1, int(target_min_examples)),
        "training": {
            "epochs": max(1, int(epochs)),
            "learning_rate": float(learning_rate),
            "l2": float(l2),
            "target_l2": float(target_l2),
        },
        "bias": round(weights["bias"], 6),
        "global_token_weights": weights["global_token_weights"],
        "target_bias": weights["target_bias"],
        "target_token_weights": weights["target_token_weights"],
        "label_counts": dict(label_counts),
        "target_counts": dict(target_counts),
        "target_label_counts": {target: dict(counts) for target, counts in target_label_counts.items()},
        "token_counts": dict(token_counts),
        "examples": examples,
        "summary": {
            "examples": len(examples),
            "targets": len(target_counts),
            "features": len(token_counts),
        },
    }


def train_preference_weights(
    examples: list[dict[str, Any]],
    *,
    epochs: int,
    learning_rate: float,
    l2: float,
    target_l2: float,
) -> dict[str, Any]:
    global_weights: dict[str, float] = {}
    target_weights: dict[str, dict[str, float]] = {}
    target_bias: dict[str, float] = {}
    bias = 0.0
    if not examples:
        return {
            "bias": 0.0,
            "global_token_weights": {},
            "target_bias": {},
            "target_token_weights": {},
        }

    for _ in range(max(1, int(epochs))):
        for example in examples:
            tokens = list(example.get("tokens") or [])
            if not tokens:
                continue
            target = str(example.get("target_key") or "__rare__")
            scale = 1.0 / math.sqrt(len(tokens))
            local_weights = target_weights.setdefault(target, {})
            target_value = 1.0 if int(example.get("gold_label", 0)) == 1 else 0.0
            z = (
                bias
                + sum(global_weights.get(token, 0.0) for token in tokens) * scale
                + target_bias.get(target, 0.0)
                + sum(local_weights.get(token, 0.0) for token in tokens) * scale
            )
            z = max(-12.0, min(12.0, z))
            pred = sigmoid(z)
            error = target_value - pred

            bias += learning_rate * (error - l2 * bias)
            target_bias[target] = target_bias.get(target, 0.0) + learning_rate * (
                error - target_l2 * target_bias.get(target, 0.0)
            )
            global_decay = 1.0 - learning_rate * l2
            target_decay = 1.0 - learning_rate * target_l2
            for token in tokens:
                global_weights[token] = global_weights.get(token, 0.0) * global_decay + learning_rate * error * scale
                local_weights[token] = local_weights.get(token, 0.0) * target_decay + learning_rate * error * scale

    return {
        "bias": bias,
        "global_token_weights": compact_weights(global_weights),
        "target_bias": {target: round(value, 6) for target, value in target_bias.items() if abs(value) >= 0.0001},
        "target_token_weights": {
            target: compact_weights(weights)
            for target, weights in target_weights.items()
            if compact_weights(weights)
        },
    }


def compact_weights(weights: dict[str, float]) -> dict[str, float]:
    return {token: round(value, 6) for token, value in weights.items() if abs(value) >= 0.0001}


def tune_preference_model(
    cards: list[dict[str, Any]],
    model: dict[str, Any],
    *,
    pair_map: dict[int, ClonePair] | None = None,
    threshold_grid: list[float] | None = None,
    adapter_grid: list[float] | None = None,
    gate_grid: list[float] | None = None,
    prototype_grid: list[float] | None = None,
    profile_prior_grid: list[float] | None = None,
    metric: str = "f1",
) -> dict[str, Any]:
    pair_map = pair_map or {}
    threshold_grid = threshold_grid or [round(step / 20, 2) for step in range(0, 21)]
    adapter_grid = adapter_grid or [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    gate_grid = gate_grid or [0.0, 0.25, 0.5, 0.75, 1.0]
    prototype_grid = prototype_grid or [float(model.get("prototype_weight", 0.0))]
    profile_prior_grid = profile_prior_grid or [float(model.get("profile_prior_weight", 0.0))]
    metric = metric if metric in {"f1", "accuracy", "precision", "recall"} else "f1"
    components = [
        (
            card,
            preference_components(
                card,
                model,
                pair=pair_map.get(int(card.get("pair_id", 0) or 0)),
            ),
        )
        for card in cards
    ]

    candidates: list[dict[str, Any]] = []
    for adapter_strength in adapter_grid:
        for preference_gate in gate_grid:
            for prototype_weight in prototype_grid:
                for profile_prior_weight in profile_prior_grid:
                    scored_cards = [
                        (
                            card,
                            preference_score_from_components(
                                item,
                                adapter_strength=float(adapter_strength),
                                preference_gate=float(preference_gate),
                                prototype_weight=float(prototype_weight),
                                profile_prior_weight=float(profile_prior_weight),
                            ),
                        )
                        for card, item in components
                    ]
                    for threshold in threshold_grid:
                        summary = evaluate_scored_cards(scored_cards, threshold=float(threshold))
                        candidates.append(
                            {
                                "threshold": clamp01(threshold),
                                "adapter_strength": max(0.0, float(adapter_strength)),
                                "preference_gate": clamp01(preference_gate),
                                "prototype_weight": clamp01(prototype_weight),
                                "profile_prior_weight": clamp01(profile_prior_weight),
                                "metrics": summary,
                            }
                        )

    def rank(candidate: dict[str, Any]) -> tuple[float, float, float, float, float]:
        summary = candidate["metrics"]
        return (
            float(summary.get(metric, 0.0)),
            float(summary.get("accuracy", 0.0)),
            float(summary.get("precision", 0.0)),
            float(summary.get("recall", 0.0)),
            -abs(float(candidate["threshold"]) - 0.5),
        )

    candidates.sort(key=rank, reverse=True)
    tuned = deepcopy(model)
    best = candidates[0] if candidates else {}
    if best:
        tuned["threshold"] = best["threshold"]
        tuned["adapter_strength"] = best["adapter_strength"]
        tuned["preference_gate"] = best["preference_gate"]
        tuned["prototype_weight"] = best.get("prototype_weight", float(model.get("prototype_weight", 0.0)))
        tuned["profile_prior_weight"] = best.get(
            "profile_prior_weight",
            float(model.get("profile_prior_weight", 0.0)),
        )
    tuned["tuning"] = {
        "metric": metric,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validation_cards": len(cards),
        "candidate_count": len(candidates),
        "best": best,
        "top_candidates": candidates[:10],
    }
    return tuned


def tune_preference_target_thresholds(
    cards: list[dict[str, Any]],
    model: dict[str, Any],
    *,
    pair_map: dict[int, ClonePair] | None = None,
    threshold_grid: list[float] | None = None,
    metric: str = "f1",
    passes: int = 3,
) -> dict[str, Any]:
    pair_map = pair_map or {}
    threshold_grid = threshold_grid or [round(step / 20, 2) for step in range(0, 21)]
    metric = metric if metric in {"f1", "accuracy", "precision", "recall"} else "f1"
    tuned = deepcopy(model)
    tuned.pop("target_thresholds", None)
    scored_cards = [
        (
            card,
            score_preference_card(
                card,
                tuned,
                pair=pair_map.get(int(card.get("pair_id", 0) or 0)),
            )["score"],
        )
        for card in cards
    ]
    targets = sorted({str((card.get("target") or {}).get("name") or "") for card in cards})
    base_threshold = float(tuned.get("threshold", 0.5))
    tuned["target_thresholds"] = {target: base_threshold for target in targets if target}
    history: list[dict[str, Any]] = []

    def rank(summary: dict[str, Any]) -> tuple[float, float, float, float]:
        return (
            float(summary.get(metric, 0.0)),
            float(summary.get("accuracy", 0.0)),
            float(summary.get("precision", 0.0)),
            float(summary.get("recall", 0.0)),
        )

    best_summary = evaluate_scored_cards_with_model(scored_cards, tuned)
    for _ in range(max(1, int(passes))):
        changed = False
        for target in targets:
            if not target:
                continue
            current = float(tuned["target_thresholds"].get(target, base_threshold))
            local_best = (rank(best_summary), current, best_summary)
            for threshold in threshold_grid:
                candidate = deepcopy(tuned)
                candidate["target_thresholds"][target] = clamp01(threshold)
                summary = evaluate_scored_cards_with_model(scored_cards, candidate)
                candidate_rank = rank(summary)
                if candidate_rank > local_best[0]:
                    local_best = (candidate_rank, clamp01(threshold), summary)
            if local_best[1] != current:
                tuned["target_thresholds"][target] = local_best[1]
                best_summary = local_best[2]
                changed = True
                history.append({"target": target, "threshold": local_best[1], "metrics": best_summary})
        if not changed:
            break

    tuned["target_tuning"] = {
        "metric": metric,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validation_cards": len(cards),
        "targets": len(targets),
        "best_metrics": evaluate_scored_cards_with_model(scored_cards, tuned),
        "history": history,
    }
    return tuned


def apply_preference_model(
    card: dict[str, Any],
    model: dict[str, Any],
    *,
    pair: ClonePair | None = None,
) -> dict[str, Any]:
    scored = score_preference_card(card, model, pair=pair)
    pred = 1 if scored["score"] >= preference_threshold_for_card(card, model) else 0
    confidence = scored["score"] if pred == 1 else 1.0 - scored["score"]
    updated = dict(card)
    input_decision = dict(card.get("decision") or {})
    updated["preference_input_decision"] = input_decision
    updated["annotation_preference"] = scored
    updated["policy"] = "annotation-preference"
    verdict = "benchmark_supported_clone" if pred == 1 else "benchmark_supported_non_clone"
    updated["decision"] = {
        "verdict": verdict,
        "pred_label": pred,
        "confidence": round(confidence, 4),
        "rationale": append_reason(
            str(input_decision.get("rationale", "")),
            (
                "Annotation Preference Space predicts label "
                f"{pred} with score={scored['score']:.4f}; "
                f"preference={scored['preference_score']:.4f}, "
                f"reference={scored['reference_score']:.4f} ({scored['reference_source']}), "
                f"semantic={scored['semantic_score']:.4f}."
            ),
        ),
        "observations": list(input_decision.get("observations") or []),
        "risk_flags": list(input_decision.get("risk_flags") or []) + ["annotation_preference_override"],
        "recommended_next_step": "inspect_preference_components",
    }
    return updated


def score_preference_card(
    card: dict[str, Any],
    model: dict[str, Any],
    *,
    pair: ClonePair | None = None,
) -> dict[str, Any]:
    components = preference_components(card, model, pair=pair)
    score = preference_score_from_components(
        components,
        adapter_strength=float(model.get("adapter_strength", 1.0)),
        preference_gate=float(model.get("preference_gate", 1.0)),
        prototype_weight=float(model.get("prototype_weight", 0.0)),
        profile_prior_weight=float(model.get("profile_prior_weight", 0.0)),
    )
    return {
        "score": round(score, 6),
        "threshold": preference_threshold_for_card(card, model),
        "preference_score": round(components["preference_score"], 6),
        "prototype_score": round(components["prototype_score"], 6),
        "prototype_weight": float(model.get("prototype_weight", 0.0)),
        "profile_prior_score": round(components["profile_prior_score"], 6),
        "profile_prior_weight": float(model.get("profile_prior_weight", 0.0)),
        "reference_score": round(components["reference_score"], 6),
        "reference_source": components["reference_source"],
        "semantic_score": round(components["semantic_score"], 6),
        "global_score": round(sigmoid(components["global_logit"]), 6),
        "target_adapter_score": round(sigmoid(components["target_logit"]), 6),
        "global_logit": round(components["global_logit"], 6),
        "target_logit": round(components["target_logit"], 6),
        "adapter_strength": float(model.get("adapter_strength", 1.0)),
        "preference_gate": float(model.get("preference_gate", 1.0)),
        "target_key": components["target_key"],
        "feature_count": components["feature_count"],
        "nearest_preference_examples": components["prototype_neighbors"],
    }


def preference_components(
    card: dict[str, Any],
    model: dict[str, Any],
    *,
    pair: ClonePair | None = None,
) -> dict[str, Any]:
    reference_mode = str(model.get("reference_mode", "decision"))
    tokens = preference_tokens(card, pair, reference_mode=reference_mode)
    target = str((card.get("target") or {}).get("name") or "")
    target_counts = model.get("target_counts") or {}
    target_key = target if int(target_counts.get(target, 0) or 0) >= int(model.get("target_min_examples", 1)) else "__rare__"
    scale = 1.0 / math.sqrt(len(tokens)) if tokens else 1.0
    global_weights = model.get("global_token_weights") or {}
    target_weights = (model.get("target_token_weights") or {}).get(target_key, {})
    global_logit = float(model.get("bias", 0.0)) + sum(float(global_weights.get(token, 0.0)) for token in tokens) * scale
    target_logit = float((model.get("target_bias") or {}).get(target_key, 0.0)) + sum(
        float(target_weights.get(token, 0.0)) for token in tokens
    ) * scale
    adapter_strength = float(model.get("adapter_strength", 1.0))
    preference_logit = global_logit + adapter_strength * target_logit
    semantic = semantic_score(card)
    ref_score, ref_source = reference_score(card, semantic, mode=reference_mode)
    prototype_score, prototype_neighbors = preference_prototype_score(tokens, target_key, model)
    return {
        "tokens": tokens,
        "target_key": target_key,
        "global_logit": global_logit,
        "target_logit": target_logit,
        "preference_score": sigmoid(preference_logit),
        "prototype_score": prototype_score,
        "prototype_neighbors": prototype_neighbors,
        "profile_prior_score": target_profile_prior(card, pair),
        "reference_score": ref_score,
        "reference_source": ref_source,
        "semantic_score": semantic,
        "feature_count": len(tokens),
    }


def preference_score_from_components(
    components: dict[str, Any],
    *,
    adapter_strength: float,
    preference_gate: float,
    prototype_weight: float = 0.0,
    profile_prior_weight: float = 0.0,
) -> float:
    preference_logit = float(components["global_logit"]) + max(0.0, float(adapter_strength)) * float(
        components["target_logit"]
    )
    logistic_score = sigmoid(preference_logit)
    prototype_score = float(components.get("prototype_score", logistic_score))
    prototype = clamp01(prototype_weight)
    preference_score = (1.0 - prototype) * logistic_score + prototype * prototype_score
    gate = clamp01(preference_gate)
    reference = float(components.get("reference_score", components["semantic_score"]))
    base = gate * preference_score + (1.0 - gate) * reference
    profile = clamp01(profile_prior_weight)
    prior = float(components.get("profile_prior_score", 0.5))
    return profile * prior + (1.0 - profile) * base


def evaluate_preference_model(
    cards: list[dict[str, Any]],
    model: dict[str, Any],
    *,
    pair_map: dict[int, ClonePair] | None = None,
) -> dict[str, Any]:
    pair_map = pair_map or {}
    counts = {"evaluated": 0, "abstained": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for card in cards:
        pair_id = int(card.get("pair_id", 0) or 0)
        score = score_preference_card(card, model, pair=pair_map.get(pair_id))["score"]
        pred = 1 if score >= preference_threshold_for_card(card, model) else 0
        gold = int((card.get("gold") or {}).get("label", 0))
        counts["evaluated"] += 1
        if pred == 1 and gold == 1:
            counts["tp"] += 1
        elif pred == 0 and gold == 0:
            counts["tn"] += 1
        elif pred == 1 and gold == 0:
            counts["fp"] += 1
        elif pred == 0 and gold == 1:
            counts["fn"] += 1
    return preference_metrics(counts)


def evaluate_scored_cards(scored_cards: list[tuple[dict[str, Any], float]], *, threshold: float) -> dict[str, Any]:
    counts = {"evaluated": 0, "abstained": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for card, score in scored_cards:
        pred = 1 if score >= threshold else 0
        gold = int((card.get("gold") or {}).get("label", 0))
        counts["evaluated"] += 1
        if pred == 1 and gold == 1:
            counts["tp"] += 1
        elif pred == 0 and gold == 0:
            counts["tn"] += 1
        elif pred == 1 and gold == 0:
            counts["fp"] += 1
        elif pred == 0 and gold == 1:
            counts["fn"] += 1
    return preference_metrics(counts)


def evaluate_scored_cards_with_model(
    scored_cards: list[tuple[dict[str, Any], float]],
    model: dict[str, Any],
) -> dict[str, Any]:
    counts = {"evaluated": 0, "abstained": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for card, score in scored_cards:
        pred = 1 if score >= preference_threshold_for_card(card, model) else 0
        gold = int((card.get("gold") or {}).get("label", 0))
        counts["evaluated"] += 1
        if pred == 1 and gold == 1:
            counts["tp"] += 1
        elif pred == 0 and gold == 0:
            counts["tn"] += 1
        elif pred == 1 and gold == 0:
            counts["fp"] += 1
        elif pred == 0 and gold == 1:
            counts["fn"] += 1
    return preference_metrics(counts)


def preference_threshold_for_card(card: dict[str, Any], model: dict[str, Any]) -> float:
    target = str((card.get("target") or {}).get("name") or "")
    thresholds = model.get("target_thresholds") or {}
    if isinstance(thresholds, dict) and target in thresholds:
        item = thresholds.get(target)
        if isinstance(item, dict):
            item = item.get("threshold")
        try:
            return clamp01(float(item))
        except (TypeError, ValueError):
            pass
    return clamp01(float(model.get("threshold", 0.5)))


def preference_metrics(counts: dict[str, int]) -> dict[str, Any]:
    evaluated = counts["evaluated"]
    tp = counts["tp"]
    tn = counts["tn"]
    fp = counts["fp"]
    fn = counts["fn"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / evaluated if evaluated else 0.0
    return {
        **counts,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def preference_tokens(
    card: dict[str, Any],
    pair: ClonePair | None = None,
    *,
    reference_mode: str = "decision",
) -> set[str]:
    tokens = set(feature_tokens(card, pair))
    target = str((card.get("target") or {}).get("name") or "")
    add_token(tokens, "aps_target", target)

    llm = card.get("llm_evidence") or {}
    decision = card.get("decision") or {}
    semantic_label = semantic_label_from_llm(llm)
    bcb_label = bcb_label_from_llm(llm)
    decision_label = decision.get("pred_label")
    if semantic_label in (0, 1):
        add_token(tokens, "aps_semantic_label", semantic_label)
    if bcb_label in (0, 1):
        add_token(tokens, "aps_llm_bcb_label", bcb_label)
    if semantic_label in (0, 1) and bcb_label in (0, 1):
        add_token(tokens, "aps_semantic_bcb_relation", f"{semantic_label}_to_{bcb_label}")
    if decision_label in (0, 1) and bcb_label in (0, 1):
        add_token(tokens, "aps_decision_bcb_relation", f"{decision_label}_to_{bcb_label}")

    add_reference_tokens(tokens, card, reference_mode=reference_mode)

    shared = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
    if isinstance(shared, dict):
        add_token(tokens, "aps_slice_exists", shared.get("exists"))
        add_token(tokens, "aps_slice_alignment", shared.get("bcb_target_alignment"))
        add_text_axis_tokens(tokens, "aps_slice_text", str(shared.get("description", "")))

    wrapper_differences = llm.get("wrapper_differences", []) if isinstance(llm, dict) else []
    semantic_risks = llm.get("semantic_risk_flags", []) if isinstance(llm, dict) else []
    for item in wrapper_differences:
        add_text_axis_tokens(tokens, "aps_wrapper_axis", str(item))
    for item in semantic_risks:
        add_text_axis_tokens(tokens, "aps_risk_axis", str(item))
    for item in decision.get("risk_flags", []) or []:
        add_text_axis_tokens(tokens, "aps_decision_axis", str(item))

    if pair:
        add_pair_shape_tokens(tokens, pair)
        add_target_invariance_tokens(tokens, target, pair)
    return tokens


def add_pair_shape_tokens(tokens: set[str], pair: ClonePair) -> None:
    len_a = max(1, len(pair.code_a))
    len_b = max(1, len(pair.code_b))
    ratio = max(len_a, len_b) / max(1, min(len_a, len_b))
    if ratio >= 5:
        bucket = "very_asymmetric"
    elif ratio >= 2:
        bucket = "asymmetric"
    else:
        bucket = "balanced"
    add_token(tokens, "aps_code_length_ratio", bucket)
    method_a = len(re.findall(r"\b[a-zA-Z_$][\w$]*\s*\(", pair.code_a))
    method_b = len(re.findall(r"\b[a-zA-Z_$][\w$]*\s*\(", pair.code_b))
    if method_a <= 2 and method_b <= 2:
        add_token(tokens, "aps_call_density", "small")
    elif method_a >= 12 or method_b >= 12:
        add_token(tokens, "aps_call_density", "large_wrapper")
    else:
        add_token(tokens, "aps_call_density", "medium")


def add_target_invariance_tokens(tokens: set[str], target: str, pair: ClonePair) -> None:
    target_key = normalize_piece(target)
    low_a = pair.code_a.lower()
    low_b = pair.code_b.lower()
    if "secure_hash" in target_key or "hash" in target_key:
        add_hash_invariance_tokens(tokens, pair.code_a, pair.code_b)
    if "execute_update" in target_key or "rollback" in target_key or "transaction" in target_key:
        add_transaction_invariance_tokens(tokens, low_a, low_b)
    if "copy_file" in target_key or "download_from_web" in target_key:
        add_io_preference_tokens(tokens, target_key, low_a, low_b)


def add_hash_invariance_tokens(tokens: set[str], code_a: str, code_b: str) -> None:
    hash_a = extract_hash_algorithms(code_a)
    hash_b = extract_hash_algorithms(code_b)
    for algorithm in sorted(hash_a):
        add_token(tokens, "aps_hash_algorithm_a", algorithm)
    for algorithm in sorted(hash_b):
        add_token(tokens, "aps_hash_algorithm_b", algorithm)
    if hash_a and hash_b and not (hash_a & hash_b):
        add_token(tokens, "aps_target_invariant", "hash_algorithm_mismatch")
        add_token(tokens, "aps_hash_algorithm_pair", f"{'+'.join(sorted(hash_a))}|{'+'.join(sorted(hash_b))}")
    elif hash_a & hash_b:
        add_token(tokens, "aps_target_invariant", "hash_algorithm_overlap")

    output_a = hash_output_shape(code_a)
    output_b = hash_output_shape(code_b)
    add_token(tokens, "aps_hash_output_a", output_a)
    add_token(tokens, "aps_hash_output_b", output_b)
    if output_a != "unknown" and output_b != "unknown" and output_a != output_b:
        add_token(tokens, "aps_target_invariant", "hash_output_shape_mismatch")
        add_token(tokens, "aps_hash_output_pair", f"{output_a}|{output_b}")


def hash_output_shape(code: str) -> str:
    low = code.lower()
    signature = low.split("{", 1)[0]
    if "base64" in low:
        return "base64_text"
    if "byte[]" in signature or "byte []" in signature or re.search(r"\bbyte\s*\[\s*\]\s+\w+\s*\(", signature):
        return "raw_bytes"
    if "tostring(16)" in low or "integer.tostring" in low or "stringbuffer" in low or "stringbuilder" in low:
        return "hex_text"
    if "return " in low and ".digest(" in low and "string" not in signature:
        return "raw_bytes"
    if "string" in signature and ("digest" in low or "message_digest" in low or "messagedigest" in low):
        return "text"
    return "unknown"


def add_transaction_invariance_tokens(tokens: set[str], low_a: str, low_b: str) -> None:
    ops_a = sql_operation_set(low_a)
    ops_b = sql_operation_set(low_b)
    for op in sorted(ops_a):
        add_token(tokens, "aps_transaction_op_a", op)
    for op in sorted(ops_b):
        add_token(tokens, "aps_transaction_op_b", op)
    if ops_a and ops_b and not (ops_a & ops_b):
        add_token(tokens, "aps_target_invariant", "transaction_operation_mismatch")
        add_token(tokens, "aps_transaction_op_pair", f"{'+'.join(sorted(ops_a))}|{'+'.join(sorted(ops_b))}")
    elif ops_a & ops_b:
        add_token(tokens, "aps_target_invariant", "transaction_operation_overlap")

    control_a = transaction_control_set(low_a)
    control_b = transaction_control_set(low_b)
    if control_a or control_b:
        add_token(tokens, "aps_transaction_control_a", "+".join(sorted(control_a)) or "none")
        add_token(tokens, "aps_transaction_control_b", "+".join(sorted(control_b)) or "none")
    if control_a and control_b and control_a != control_b:
        add_token(tokens, "aps_target_invariant", "transaction_control_mismatch")


def sql_operation_set(low: str) -> set[str]:
    ops: set[str] = set()
    for op in ["select", "insert", "update", "delete"]:
        if re.search(rf"\b{op}\b", low):
            ops.add(op)
    if "executeupdate" in low and not ops:
        ops.add("execute_update_unknown")
    return ops


def transaction_control_set(low: str) -> set[str]:
    controls: set[str] = set()
    if "rollback" in low:
        controls.add("rollback")
    if "commit" in low:
        controls.add("commit")
    if "setautocommit(false)" in low.replace(" ", ""):
        controls.add("manual_commit")
    return controls


def add_io_preference_tokens(tokens: set[str], target_key: str, low_a: str, low_b: str) -> None:
    profile_a = io_profile(low_a)
    profile_b = io_profile(low_b)
    for item in sorted(profile_a):
        add_token(tokens, "aps_io_profile_a", item)
    for item in sorted(profile_b):
        add_token(tokens, "aps_io_profile_b", item)
    shared = profile_a & profile_b
    for item in sorted(shared):
        add_token(tokens, "aps_io_profile_shared", item)
    if profile_a and profile_b and not shared:
        add_token(tokens, "aps_io_profile_relation", "disjoint")
    elif shared:
        add_token(tokens, "aps_io_profile_relation", "overlap")
    elif profile_a or profile_b:
        add_token(tokens, "aps_io_profile_relation", "one_sided")
    if "copy_file" in target_key and ({"archive", "dearchive"} & (profile_a | profile_b)):
        add_token(tokens, "aps_broad_target_preference", "copy_file_archive_family")
    if "download_from_web" in target_key and "remote_read" in (profile_a | profile_b):
        add_token(tokens, "aps_broad_target_preference", "download_remote_read_family")


def io_profile(low: str) -> set[str]:
    profile: set[str] = set()
    markers = code_marker_set(low)
    if "fileinputstream" in markers or "inputstream" in low or "reader" in low:
        profile.add("read")
    if "fileoutputstream" in markers or "outputstream" in low or "writer" in low or "printwriter" in low:
        profile.add("write")
    if {"fileinputstream", "fileoutputstream"} <= markers or "ioutils.copy" in markers or "files.copy" in markers:
        profile.add("plain_copy")
    if "zipinputstream" in markers or "getnextentry" in low or "unzip" in low:
        profile.add("dearchive")
    if "zipoutputstream" in markers or "jaroutputstream" in markers or "taroutputstream" in low or "gzipoutputstream" in low:
        profile.add("archive")
    if "url(" in markers or "http" in markers or "httpclient" in low or "openstream" in low:
        profile.add("remote_read")
    if "stringbuffer" in low or "stringbuilder" in low or re.search(r"\b\w+\s*=\s*\w+\s*\+", low):
        profile.add("materialize_text")
    return profile


def target_profile_prior(card: dict[str, Any], pair: ClonePair | None) -> float:
    if pair is None:
        return 0.5
    target = normalize_piece(str((card.get("target") or {}).get("name") or ""))
    low_a = pair.code_a.lower()
    low_b = pair.code_b.lower()
    if "secure_hash" in target or "hash" in target:
        return hash_profile_prior(pair.code_a, pair.code_b)
    if "execute_update" in target or "rollback" in target or "transaction" in target:
        return transaction_profile_prior(low_a, low_b)
    if "copy_file" in target:
        return copy_profile_prior(low_a, low_b)
    if "download_from_web" in target:
        return download_profile_prior(low_a, low_b)
    return 0.5


def hash_profile_prior(code_a: str, code_b: str) -> float:
    hash_a = extract_hash_algorithms(code_a)
    hash_b = extract_hash_algorithms(code_b)
    output_a = hash_output_shape(code_a)
    output_b = hash_output_shape(code_b)
    score = 0.5
    if hash_a and hash_b:
        score = 0.78 if hash_a & hash_b else 0.12
    if output_a != "unknown" and output_b != "unknown" and output_a != output_b:
        score = min(score, 0.25)
    return score


def transaction_profile_prior(low_a: str, low_b: str) -> float:
    ops_a = sql_operation_set(low_a)
    ops_b = sql_operation_set(low_b)
    controls_a = transaction_control_set(low_a)
    controls_b = transaction_control_set(low_b)
    score = 0.5
    if ops_a and ops_b:
        score = 0.72 if ops_a & ops_b else 0.25
    if controls_a and controls_b and controls_a != controls_b:
        score = min(score, 0.42)
    if "rollback" in controls_a and "rollback" in controls_b:
        score = max(score, 0.68)
    return score


def copy_profile_prior(low_a: str, low_b: str) -> float:
    profile_a = io_profile(low_a)
    profile_b = io_profile(low_b)
    shared = profile_a & profile_b
    if "plain_copy" in shared:
        return 0.82
    if {"archive", "dearchive"} & (profile_a | profile_b):
        if {"read", "write"} <= (profile_a | profile_b):
            return 0.68
        return 0.6
    if {"read", "write"} <= profile_a and {"read", "write"} <= profile_b:
        return 0.62
    if profile_a and profile_b and not shared:
        return 0.35
    if profile_a or profile_b:
        return 0.3
    return 0.5


def download_profile_prior(low_a: str, low_b: str) -> float:
    profile_a = io_profile(low_a)
    profile_b = io_profile(low_b)
    if "remote_read" in profile_a and "remote_read" in profile_b:
        return 0.78
    if "remote_read" in (profile_a | profile_b) and ("read" in (profile_a | profile_b) or "materialize_text" in (profile_a | profile_b)):
        return 0.58
    return 0.45


def add_reference_tokens(tokens: set[str], card: dict[str, Any], *, reference_mode: str = "decision") -> None:
    semantic = semantic_score(card)
    reference, source = reference_score(card, semantic, mode=reference_mode)
    add_token(tokens, "aps_reference_source", source)
    add_token(tokens, "aps_reference_score", score_bucket(reference))

    alignment = card.get("bcb_alignment") or {}
    if not isinstance(alignment, dict) or not alignment:
        return
    add_token(tokens, "aps_alignment_score", score_bucket(alignment.get("score")))
    add_token(tokens, "aps_alignment_nb_score", score_bucket(alignment.get("naive_bayes_score")))
    add_token(tokens, "aps_alignment_knn_score", score_bucket(alignment.get("knn_score")))
    add_token(tokens, "aps_alignment_linear_score", score_bucket(alignment.get("linear_score")))
    add_token(tokens, "aps_alignment_memory_score", score_bucket(alignment.get("hard_memory_score")))
    add_token(tokens, "aps_alignment_memory_coverage", bool(alignment.get("hard_memory_coverage")))

    decision = card.get("decision") or {}
    semantic_decision = card.get("semantic_decision") or {}
    semantic_label = semantic_decision.get("pred_label") if isinstance(semantic_decision, dict) else None
    alignment_label = decision.get("pred_label") if isinstance(decision, dict) else None
    if semantic_label in (0, 1) and alignment_label in (0, 1):
        add_token(tokens, "aps_alignment_semantic_relation", f"{semantic_label}_to_{alignment_label}")

    for neighbor in alignment.get("top_neighbors", []) or []:
        if not isinstance(neighbor, dict):
            continue
        add_token(tokens, "aps_alignment_neighbor_label", neighbor.get("gold_label"))
        add_token(tokens, "aps_alignment_neighbor_hard_pos", bool(neighbor.get("hard_positive")))
        add_token(tokens, "aps_alignment_neighbor_hard_neg", bool(neighbor.get("hard_negative")))
    for neighbor in alignment.get("hard_memory_neighbors", []) or []:
        if not isinstance(neighbor, dict):
            continue
        add_token(tokens, "aps_alignment_memory_label", neighbor.get("gold_label"))
        add_token(tokens, "aps_alignment_memory_case", neighbor.get("case_type"))


def semantic_score(card: dict[str, Any]) -> float:
    llm = card.get("llm_evidence") or {}
    label = semantic_label_from_llm(llm)
    confidence = llm.get("semantic_confidence") if isinstance(llm, dict) else None
    if label not in (0, 1):
        decision = card.get("decision") or {}
        label = decision.get("pred_label")
        confidence = decision.get("confidence")
    try:
        conf = max(0.0, min(float(confidence), 1.0))
    except (TypeError, ValueError):
        conf = 0.5
    if label == 1:
        return max(conf, 0.5)
    if label == 0:
        return min(1.0 - conf, 0.5)
    return 0.5


def reference_score(
    card: dict[str, Any],
    fallback_semantic: float | None = None,
    *,
    mode: str = "decision",
) -> tuple[float, str]:
    alignment = card.get("bcb_alignment") or {}
    if mode == "semantic":
        semantic = semantic_score(card) if fallback_semantic is None else fallback_semantic
        return clamp01(float(semantic)), "semantic"
    if isinstance(alignment, dict) and alignment:
        decision = card.get("decision") or {}
        if mode == "decision" and isinstance(decision, dict) and decision.get("pred_label") in (0, 1):
            return decision_probability(decision), "bcb_alignment_decision"
        if "score" in alignment:
            try:
                return clamp01(float(alignment.get("score"))), "bcb_alignment_score"
            except (TypeError, ValueError):
                pass
    semantic = semantic_score(card) if fallback_semantic is None else fallback_semantic
    return clamp01(float(semantic)), "semantic"


def decision_probability(decision: dict[str, Any]) -> float:
    label = decision.get("pred_label")
    try:
        confidence = clamp01(float(decision.get("confidence", 0.5)))
    except (TypeError, ValueError):
        confidence = 0.5
    if label == 1:
        return 0.5 + 0.5 * confidence
    if label == 0:
        return 0.5 - 0.5 * confidence
    return 0.5


def score_bucket(value: Any) -> str:
    try:
        score = clamp01(float(value))
    except (TypeError, ValueError):
        return "missing"
    if score >= 0.9:
        return "very_high"
    if score >= 0.75:
        return "high"
    if score >= 0.6:
        return "mid_high"
    if score >= 0.4:
        return "middle"
    if score >= 0.25:
        return "mid_low"
    if score >= 0.1:
        return "low"
    return "very_low"


def semantic_label_from_llm(llm: dict[str, Any]) -> int | None:
    if not isinstance(llm, dict):
        return None
    return VERDICT_TO_LABEL.get(str(llm.get("semantic_verdict") or ""))


def bcb_label_from_llm(llm: dict[str, Any]) -> int | None:
    if not isinstance(llm, dict):
        return None
    return VERDICT_TO_LABEL.get(str(llm.get("bcb_gold_verdict") or ""))


def nearest_preference_examples(tokens: set[str], target_key: str, model: dict[str, Any]) -> list[dict[str, Any]]:
    _, neighbors = preference_prototype_score(tokens, target_key, model)
    return neighbors


def preference_prototype_score(
    tokens: set[str],
    target_key: str,
    model: dict[str, Any],
) -> tuple[float, list[dict[str, Any]]]:
    examples = model.get("examples") or []
    if not examples:
        return label_prior(model), []
    min_similarity = max(0.0, float(model.get("prototype_min_similarity", 0.02)))
    k = max(1, int(model.get("prototype_k", 9)))
    scored: list[tuple[float, dict[str, Any]]] = []
    for example in examples:
        example_tokens = set(example.get("tokens") or [])
        sim = jaccard(tokens, example_tokens)
        if target_key and example.get("target_key") == target_key:
            sim += 0.15
        if sim >= min_similarity:
            scored.append((sim, example))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:k]
    if not top:
        return label_prior(model), []
    weight_sum = sum(max(0.0001, sim) for sim, _ in top)
    pos_weight = sum(max(0.0001, sim) for sim, ex in top if int(ex.get("gold_label", 0)) == 1)
    neighbors = [
        {
            "pair_id": ex.get("pair_id"),
            "gold_label": ex.get("gold_label"),
            "similarity": round(sim, 4),
        }
        for sim, ex in top[:5]
    ]
    return pos_weight / weight_sum, neighbors


def label_prior(model: dict[str, Any]) -> float:
    labels = model.get("label_counts") or {}
    pos = int(labels.get("1", 0) or 0)
    neg = int(labels.get("0", 0) or 0)
    return pos / (pos + neg) if pos + neg else 0.5


def add_text_axis_tokens(tokens: set[str], prefix: str, text: str) -> None:
    lowered = text.lower()
    axes = {
        "wrapper": ["wrapper", "嵌入", "包装", "context", "上下文"],
        "partial": ["partial", "slice", "片段", "局部"],
        "one_sided": ["only one side", "单侧", "缺失", "missing"],
        "algorithm": ["algorithm", "md5", "sha", "算法", "摘要", "哈希"],
        "io_shape": ["inputstream", "outputstream", "stream", "reader", "writer", "流"],
        "source_sink": ["file", "url", "http", "classpath", "resource", "文件", "远程", "本地"],
        "transform": ["transform", "parse", "decode", "encode", "转换", "解析", "过滤"],
        "test_or_gui": ["test", "assert", "gui", "listener", "测试", "界面"],
        "transaction": ["transaction", "rollback", "commit", "事务", "回滚"],
    }
    for axis, markers in axes.items():
        if any(marker in lowered or marker in text for marker in markers):
            add_token(tokens, prefix, axis)


def add_token(tokens: set[str], prefix: str, value: Any) -> None:
    if value is None:
        return
    text = normalize_piece(str(value))
    if text:
        tokens.add(f"{prefix}:{text}")


def normalize_piece(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_\-.:]+", "_", value)
    return value.strip("_")[:80]


def sigmoid(value: float) -> float:
    value = max(-12.0, min(12.0, value))
    return 1.0 / (1.0 + math.exp(-value))
