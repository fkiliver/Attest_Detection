from __future__ import annotations

import json
import math
import re
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .dataset import ClonePair
from .evidence import append_reason


MODEL_SCHEMA = "eviclone-bcb-alignment/v1"
DECISION_MODES = {"replace", "selective", "fill-abstain"}


def load_alignment_model(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_alignment_model(model: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def train_alignment_model(
    cards: list[dict[str, Any]],
    *,
    pair_map: dict[int, ClonePair] | None = None,
    k: int = 11,
    threshold: float = 0.5,
    positive_threshold: float | None = None,
    negative_threshold: float | None = None,
    nb_weight: float = 0.35,
    linear_weight: float = 0.5,
    linear_epochs: int = 40,
    memory_k: int = 7,
    memory_weight: float = 0.0,
    memory_min_similarity: float = 0.2,
    decision_mode: str = "replace",
) -> dict[str, Any]:
    examples: list[dict[str, Any]] = []
    pos_counts: Counter[str] = Counter()
    neg_counts: Counter[str] = Counter()
    label_counts = Counter()
    token_document_counts: Counter[str] = Counter()
    pair_map = pair_map or {}

    for card in cards:
        label = int(card.get("gold", {}).get("label", 0))
        tokens = sorted(feature_tokens(card, pair_map.get(int(card.get("pair_id", 0)))))
        if not tokens:
            continue
        label_counts[str(label)] += 1
        token_document_counts.update(tokens)
        if label == 1:
            pos_counts.update(tokens)
        else:
            neg_counts.update(tokens)
        examples.append(
            {
                "pair_id": int(card.get("pair_id", 0)),
                "gold_label": label,
                "target": card.get("target", {}).get("name") or "",
                "functionality_id": str(card.get("target", {}).get("functionality_id", "")),
                "semantic_pred_label": semantic_pred_label(card),
                "hard_positive": label == 1 and semantic_pred_label(card) != 1,
                "hard_negative": label == 0 and semantic_pred_label(card) == 1,
                "tokens": tokens,
            }
        )

    linear_weights, linear_bias = train_linear_weights(examples, epochs=linear_epochs)
    hard_memory_examples = build_hard_memory_examples(examples)
    return {
        "schema_version": MODEL_SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "k": max(1, int(k)),
        "memory_k": max(1, int(memory_k)),
        "memory_weight": max(0.0, min(float(memory_weight), 1.0)),
        "memory_min_similarity": max(0.0, float(memory_min_similarity)),
        "threshold": max(0.0, min(float(threshold), 1.0)),
        "positive_threshold": max(0.0, min(float(positive_threshold if positive_threshold is not None else threshold), 1.0)),
        "negative_threshold": max(0.0, min(float(negative_threshold if negative_threshold is not None else threshold), 1.0)),
        "nb_weight": max(0.0, min(float(nb_weight), 1.0)),
        "linear_weight": max(0.0, min(float(linear_weight), 1.0)),
        "linear_bias": round(linear_bias, 6),
        "linear_token_weights": linear_weights,
        "linear_epochs": max(1, int(linear_epochs)),
        "decision_mode": decision_mode if decision_mode in DECISION_MODES else "replace",
        "label_counts": dict(label_counts),
        "token_document_counts": dict(token_document_counts),
        "positive_token_counts": dict(pos_counts),
        "negative_token_counts": dict(neg_counts),
        "examples": examples,
        "hard_memory_examples": hard_memory_examples,
        "summary": {
            "examples": len(examples),
            "hard_positives": sum(1 for item in examples if item["hard_positive"]),
            "hard_negatives": sum(1 for item in examples if item["hard_negative"]),
            "hard_memory_examples": len(hard_memory_examples),
        },
    }


def apply_bcb_alignment(
    card: dict[str, Any],
    model: dict[str, Any],
    *,
    pair: ClonePair | None = None,
) -> dict[str, Any]:
    scored = score_card(card, model, pair=pair)
    pred_label = alignment_pred_label(card, model, scored["score"])
    confidence = scored["score"] if pred_label == 1 else 1.0 - scored["score"]

    updated = dict(card)
    semantic_decision = dict(card.get("decision", {}))
    updated["semantic_decision"] = semantic_decision
    updated["bcb_alignment"] = scored
    updated["policy"] = "bcb-alignment"

    verdict = "benchmark_supported_clone" if pred_label == 1 else "benchmark_supported_non_clone"
    rationale = append_reason(
        str(semantic_decision.get("rationale", "")),
        (
            "BCB-alignment layer predicts label "
            f"{pred_label} with score={scored['score']:.4f}; semantic decision is preserved separately."
        ),
    )
    updated["decision"] = {
        "verdict": verdict,
        "pred_label": pred_label,
        "confidence": round(confidence, 4),
        "rationale": rationale,
        "observations": list(semantic_decision.get("observations") or []),
        "risk_flags": list(semantic_decision.get("risk_flags") or []) + ["bcb_alignment_override"],
        "recommended_next_step": "inspect_semantic_decision" if pred_label != semantic_pred_label(card) else "human_audit_optional",
    }
    return updated


def alignment_pred_label(card: dict[str, Any], model: dict[str, Any], score: float) -> int:
    mode = str(model.get("decision_mode", "replace"))
    threshold, positive_threshold, negative_threshold = thresholds_for_card(card, model)
    if mode == "fill-abstain":
        semantic = semantic_pred_label(card)
        if semantic is not None:
            return semantic
        return 1 if score >= positive_threshold else 0
    if mode != "selective":
        return 1 if score >= threshold else 0
    semantic = semantic_pred_label(card)
    if semantic is None:
        return 1 if score >= positive_threshold else 0
    if semantic == 0 and score >= positive_threshold:
        return 1
    if semantic == 1 and score <= negative_threshold:
        return 0
    return semantic


def thresholds_for_card(card: dict[str, Any], model: dict[str, Any]) -> tuple[float, float, float]:
    threshold = float(model.get("threshold", 0.5))
    positive_threshold = float(model.get("positive_threshold", threshold))
    negative_threshold = float(model.get("negative_threshold", threshold))
    target = str((card.get("target") or {}).get("name") or "")
    target_thresholds = model.get("target_thresholds") or {}
    item = target_thresholds.get(target) if isinstance(target_thresholds, dict) else None
    if isinstance(item, dict):
        threshold = float(item.get("threshold", item.get("positive_threshold", threshold)))
        positive_threshold = float(item.get("positive_threshold", positive_threshold))
        negative_threshold = float(item.get("negative_threshold", negative_threshold))
    return threshold, positive_threshold, negative_threshold


def evaluate_alignment_model(
    cards: list[dict[str, Any]],
    model: dict[str, Any],
    *,
    pair_map: dict[int, ClonePair] | None = None,
) -> dict[str, Any]:
    pair_map = pair_map or {}
    counts = {
        "evaluated": 0,
        "abstained": 0,
        "tp": 0,
        "tn": 0,
        "fp": 0,
        "fn": 0,
    }
    for card in cards:
        pair_id = int(card.get("pair_id", 0) or 0)
        score = score_card(card, model, pair=pair_map.get(pair_id))["score"]
        pred = alignment_pred_label(card, model, score)
        gold = int(card.get("gold", {}).get("label", 0))
        counts["evaluated"] += 1
        if pred == 1 and gold == 1:
            counts["tp"] += 1
        elif pred == 0 and gold == 0:
            counts["tn"] += 1
        elif pred == 1 and gold == 0:
            counts["fp"] += 1
        elif pred == 0 and gold == 1:
            counts["fn"] += 1
    return alignment_metrics(counts)


def tune_alignment_thresholds(
    cards: list[dict[str, Any]],
    model: dict[str, Any],
    *,
    pair_map: dict[int, ClonePair] | None = None,
    positive_thresholds: list[float] | None = None,
    negative_thresholds: list[float] | None = None,
    nb_weights: list[float] | None = None,
    linear_weights: list[float] | None = None,
    memory_weights: list[float] | None = None,
    decision_modes: list[str] | None = None,
    metric: str = "f1",
) -> dict[str, Any]:
    pair_map = pair_map or {}
    positive_thresholds = positive_thresholds or default_threshold_grid()
    negative_thresholds = negative_thresholds or default_threshold_grid()
    nb_weights = nb_weights or [float(model.get("nb_weight", 0.35))]
    linear_weights = linear_weights or [float(model.get("linear_weight", 0.0))]
    memory_weights = memory_weights or [float(model.get("memory_weight", 0.0))]
    decision_modes = decision_modes or ["selective"]
    decision_modes = [mode for mode in decision_modes if mode in DECISION_MODES]
    if not decision_modes:
        decision_modes = ["selective"]
    metric = metric if metric in {"f1", "accuracy", "precision", "recall"} else "f1"

    candidates: list[dict[str, Any]] = []
    components = [
        (
            card,
            score_components(
                card,
                model,
                pair=pair_map.get(int(card.get("pair_id", 0) or 0)),
            ),
        )
        for card in cards
    ]
    for linear_weight in linear_weights:
        for nb_weight in nb_weights:
            for memory_weight in memory_weights:
                weighted_model = deepcopy(model)
                weighted_model["nb_weight"] = clamp01(nb_weight)
                weighted_model["linear_weight"] = clamp01(linear_weight)
                weighted_model["memory_weight"] = clamp01(memory_weight)
                scored_cards = [
                    (card, score_value_from_components(item, weighted_model))
                    for card, item in components
                ]
                for decision_mode in decision_modes:
                    mode_negative_thresholds = (
                        negative_thresholds if decision_mode == "selective" else [model.get("negative_threshold", 0.5)]
                    )
                    for positive_threshold in positive_thresholds:
                        for negative_threshold in mode_negative_thresholds:
                            candidate = deepcopy(weighted_model)
                            candidate["decision_mode"] = decision_mode
                            candidate["threshold"] = clamp01(positive_threshold)
                            candidate["positive_threshold"] = clamp01(positive_threshold)
                            candidate["negative_threshold"] = clamp01(float(negative_threshold))
                            summary = evaluate_scored_cards(scored_cards, candidate)
                            candidates.append(
                                {
                                    "decision_mode": candidate["decision_mode"],
                                    "positive_threshold": candidate["positive_threshold"],
                                    "negative_threshold": candidate["negative_threshold"],
                                    "nb_weight": candidate["nb_weight"],
                                    "linear_weight": candidate["linear_weight"],
                                    "memory_weight": candidate["memory_weight"],
                                    "metrics": summary,
                                }
                            )

    if not candidates:
        tuned = deepcopy(model)
        tuned["tuning"] = {"metric": metric, "candidate_count": 0, "best": {}}
        return tuned

    def rank(candidate: dict[str, Any]) -> tuple[float, float, float, float, float]:
        summary = candidate["metrics"]
        return (
            float(summary.get(metric, 0.0)),
            float(summary.get("accuracy", 0.0)),
            float(summary.get("precision", 0.0)),
            float(summary.get("recall", 0.0)),
            -abs(float(candidate["positive_threshold"]) - float(candidate["negative_threshold"])),
        )

    candidates.sort(key=rank, reverse=True)
    best = candidates[0]
    tuned = deepcopy(model)
    tuned["decision_mode"] = best["decision_mode"]
    tuned["threshold"] = best["positive_threshold"]
    tuned["positive_threshold"] = best["positive_threshold"]
    tuned["negative_threshold"] = best["negative_threshold"]
    tuned["nb_weight"] = best["nb_weight"]
    tuned["linear_weight"] = best["linear_weight"]
    tuned["memory_weight"] = best["memory_weight"]
    tuned["tuning"] = {
        "metric": metric,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validation_cards": len(cards),
        "candidate_count": len(candidates),
        "best": best,
        "top_candidates": candidates[:10],
    }
    return tuned


def tune_target_thresholds(
    cards: list[dict[str, Any]],
    model: dict[str, Any],
    *,
    pair_map: dict[int, ClonePair] | None = None,
    threshold_grid: list[float] | None = None,
    metric: str = "f1",
    passes: int = 3,
) -> dict[str, Any]:
    pair_map = pair_map or {}
    threshold_grid = threshold_grid or default_threshold_grid()
    metric = metric if metric in {"f1", "accuracy", "precision", "recall"} else "f1"
    tuned = deepcopy(model)
    tuned.pop("target_thresholds", None)
    scored_cards = [
        (
            card,
            score_card(
                card,
                tuned,
                pair=pair_map.get(int(card.get("pair_id", 0) or 0)),
            )["score"],
        )
        for card in cards
    ]
    targets = sorted({str((card.get("target") or {}).get("name") or "") for card in cards})
    base_positive = float(tuned.get("positive_threshold", tuned.get("threshold", 0.5)))
    base_negative = float(tuned.get("negative_threshold", tuned.get("threshold", 0.5)))
    target_thresholds = {
        target: {
            "threshold": base_positive,
            "positive_threshold": base_positive,
            "negative_threshold": base_negative,
        }
        for target in targets
        if target
    }
    tuned["target_thresholds"] = deepcopy(target_thresholds)
    history: list[dict[str, Any]] = []

    def rank(summary: dict[str, Any]) -> tuple[float, float, float, float]:
        return (
            float(summary.get(metric, 0.0)),
            float(summary.get("accuracy", 0.0)),
            float(summary.get("precision", 0.0)),
            float(summary.get("recall", 0.0)),
        )

    best_summary = evaluate_scored_cards(scored_cards, tuned)
    for _ in range(max(1, int(passes))):
        changed = False
        for target in targets:
            if not target:
                continue
            current = deepcopy(tuned["target_thresholds"][target])
            local_best = (rank(best_summary), current, best_summary)
            for positive_threshold in threshold_grid:
                for negative_threshold in threshold_grid:
                    candidate = deepcopy(tuned)
                    candidate["target_thresholds"][target] = {
                        "threshold": clamp01(positive_threshold),
                        "positive_threshold": clamp01(positive_threshold),
                        "negative_threshold": clamp01(negative_threshold),
                    }
                    summary = evaluate_scored_cards(scored_cards, candidate)
                    candidate_rank = rank(summary)
                    if candidate_rank > local_best[0]:
                        local_best = (candidate_rank, candidate["target_thresholds"][target], summary)
            if local_best[1] != current:
                tuned["target_thresholds"][target] = local_best[1]
                best_summary = local_best[2]
                changed = True
                history.append({"target": target, "thresholds": local_best[1], "metrics": best_summary})
        if not changed:
            break

    tuned["target_tuning"] = {
        "metric": metric,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validation_cards": len(cards),
        "targets": len(targets),
        "best_metrics": evaluate_scored_cards(scored_cards, tuned),
        "history": history,
    }
    return tuned


def evaluate_scored_cards(
    scored_cards: list[tuple[dict[str, Any], float]],
    model: dict[str, Any],
) -> dict[str, Any]:
    counts = {
        "evaluated": 0,
        "abstained": 0,
        "tp": 0,
        "tn": 0,
        "fp": 0,
        "fn": 0,
    }
    for card, score in scored_cards:
        pred = alignment_pred_label(card, model, score)
        gold = int(card.get("gold", {}).get("label", 0))
        counts["evaluated"] += 1
        if pred == 1 and gold == 1:
            counts["tp"] += 1
        elif pred == 0 and gold == 0:
            counts["tn"] += 1
        elif pred == 1 and gold == 0:
            counts["fp"] += 1
        elif pred == 0 and gold == 1:
            counts["fn"] += 1
    return alignment_metrics(counts)


def alignment_metrics(counts: dict[str, int]) -> dict[str, Any]:
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


def default_threshold_grid() -> list[float]:
    return [round(step / 20, 2) for step in range(0, 21)]


def clamp01(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def score_card(card: dict[str, Any], model: dict[str, Any], *, pair: ClonePair | None = None) -> dict[str, Any]:
    components = score_components(card, model, pair=pair)
    score = score_value_from_components(components, model)
    return {
        "score": round(score, 6),
        "threshold": float(model.get("threshold", 0.5)),
        "naive_bayes_score": round(components["naive_bayes_score"], 6),
        "knn_score": round(components["knn_score"], 6),
        "linear_score": round(components["linear_score"], 6),
        "hard_memory_score": round(components["hard_memory_score"], 6),
        "hard_memory_coverage": bool(components["hard_memory_coverage"]),
        "semantic_pred_label": semantic_pred_label(card),
        "feature_count": components["feature_count"],
        "top_neighbors": components["top_neighbors"],
        "hard_memory_neighbors": components["hard_memory_neighbors"],
    }


def score_components(card: dict[str, Any], model: dict[str, Any], *, pair: ClonePair | None = None) -> dict[str, Any]:
    tokens = feature_tokens(card, pair)
    nb = naive_bayes_score(tokens, model)
    knn, neighbors = knn_score(tokens, card, model)
    linear = linear_score(tokens, model)
    memory, memory_neighbors, memory_coverage = hard_memory_score(tokens, card, model)
    return {
        "naive_bayes_score": nb,
        "knn_score": knn,
        "linear_score": linear,
        "hard_memory_score": memory,
        "hard_memory_coverage": memory_coverage,
        "feature_count": len(tokens),
        "top_neighbors": neighbors,
        "hard_memory_neighbors": memory_neighbors,
    }


def score_value_from_components(components: dict[str, Any], model: dict[str, Any]) -> float:
    nb_weight = clamp01(float(model.get("nb_weight", 0.35)))
    linear_weight = clamp01(float(model.get("linear_weight", 0.0)))
    memory_weight = clamp01(float(model.get("memory_weight", 0.0)))
    nb_knn = nb_weight * float(components["naive_bayes_score"]) + (1.0 - nb_weight) * float(components["knn_score"])
    base = linear_weight * float(components["linear_score"]) + (1.0 - linear_weight) * nb_knn
    if not components.get("hard_memory_coverage"):
        return base
    return memory_weight * float(components["hard_memory_score"]) + (1.0 - memory_weight) * base


def naive_bayes_score(tokens: set[str], model: dict[str, Any]) -> float:
    labels = model.get("label_counts", {})
    pos_docs = int(labels.get("1", 0))
    neg_docs = int(labels.get("0", 0))
    if pos_docs + neg_docs == 0:
        return 0.5
    pos_counts = Counter(model.get("positive_token_counts", {}))
    neg_counts = Counter(model.get("negative_token_counts", {}))
    vocab = set(pos_counts) | set(neg_counts) | set(tokens)
    alpha = 1.0
    pos_total = sum(pos_counts.values()) + alpha * len(vocab)
    neg_total = sum(neg_counts.values()) + alpha * len(vocab)
    log_odds = math.log((pos_docs + alpha) / (neg_docs + alpha))
    for token in tokens:
        log_odds += math.log((pos_counts[token] + alpha) / pos_total)
        log_odds -= math.log((neg_counts[token] + alpha) / neg_total)
    log_odds = max(-8.0, min(8.0, log_odds / max(1.0, math.sqrt(len(tokens)))))
    return 1.0 / (1.0 + math.exp(-log_odds))


def train_linear_weights(
    examples: list[dict[str, Any]],
    *,
    epochs: int = 40,
    learning_rate: float = 0.25,
    l2: float = 0.0005,
) -> tuple[dict[str, float], float]:
    weights: dict[str, float] = {}
    bias = 0.0
    if not examples:
        return {}, 0.0
    for _ in range(max(1, int(epochs))):
        for example in examples:
            tokens = list(example.get("tokens") or [])
            if not tokens:
                continue
            scale = 1.0 / math.sqrt(len(tokens))
            target = 1.0 if int(example.get("gold_label", 0)) == 1 else 0.0
            z = bias + sum(weights.get(token, 0.0) for token in tokens) * scale
            z = max(-12.0, min(12.0, z))
            pred = 1.0 / (1.0 + math.exp(-z))
            error = target - pred
            bias += learning_rate * error
            decay = 1.0 - learning_rate * l2
            for token in tokens:
                weights[token] = weights.get(token, 0.0) * decay + learning_rate * error * scale
    return {token: round(value, 6) for token, value in weights.items() if abs(value) >= 0.0001}, bias


def linear_score(tokens: set[str], model: dict[str, Any]) -> float:
    weights = model.get("linear_token_weights") or {}
    if not weights or not tokens:
        return 0.5
    scale = 1.0 / math.sqrt(len(tokens))
    z = float(model.get("linear_bias", 0.0)) + sum(float(weights.get(token, 0.0)) for token in tokens) * scale
    z = max(-12.0, min(12.0, z))
    return 1.0 / (1.0 + math.exp(-z))


def build_hard_memory_examples(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    memory: list[dict[str, Any]] = []
    for example in examples:
        label = int(example.get("gold_label", 0))
        semantic = example.get("semantic_pred_label")
        case_type = ""
        if label == 1 and semantic != 1:
            case_type = "hard_positive"
        elif label == 0 and semantic == 1:
            case_type = "hard_negative"
        elif label == 0 and semantic is None:
            case_type = "abstained_negative"
        if not case_type:
            continue
        memory.append(
            {
                "pair_id": example.get("pair_id"),
                "gold_label": label,
                "target": example.get("target", ""),
                "functionality_id": str(example.get("functionality_id", "")),
                "semantic_pred_label": semantic,
                "case_type": case_type,
                "tokens": example.get("tokens") or [],
            }
        )
    return memory


def hard_memory_score(
    tokens: set[str],
    card: dict[str, Any],
    model: dict[str, Any],
) -> tuple[float, list[dict[str, Any]], bool]:
    examples = model.get("hard_memory_examples") or []
    if not examples:
        return 0.5, [], False
    k = max(1, int(model.get("memory_k", 7)))
    min_similarity = max(0.0, float(model.get("memory_min_similarity", 0.2)))
    scored: list[tuple[float, dict[str, Any]]] = []
    for example in examples:
        sim = memory_similarity(tokens, card, example)
        if sim >= min_similarity:
            scored.append((sim, example))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:k]
    if not top:
        return 0.5, [], False
    weight_sum = sum(max(0.0001, sim) for sim, _ in top)
    pos_weight = sum(max(0.0001, sim) for sim, ex in top if int(ex.get("gold_label", 0)) == 1)
    neighbors = [
        {
            "pair_id": ex.get("pair_id"),
            "gold_label": ex.get("gold_label"),
            "case_type": ex.get("case_type"),
            "similarity": round(sim, 4),
        }
        for sim, ex in top[:5]
    ]
    return pos_weight / weight_sum, neighbors, True


def memory_similarity(tokens: set[str], card: dict[str, Any], example: dict[str, Any]) -> float:
    example_tokens = set(example.get("tokens") or [])
    if not tokens or not example_tokens:
        return 0.0
    target = card.get("target", {}) or {}
    target_name = str(target.get("name") or "")
    fid = str(target.get("functionality_id") or "")
    sim = jaccard(tokens, example_tokens)
    if target_name and target_name == example.get("target"):
        sim += 0.25
    if fid and fid == str(example.get("functionality_id", "")):
        sim += 0.25
    if semantic_pred_label(card) == example.get("semantic_pred_label"):
        sim += 0.1
    exact_overlap = len({token for token in tokens & example_tokens if "_exact:" in token})
    if exact_overlap:
        sim += min(0.25, exact_overlap * 0.05)
    relation_overlap = len({token for token in tokens & example_tokens if token.startswith(("copy_relation:", "hash_algorithm_relation:", "hash_algorithm_pair:"))})
    if relation_overlap:
        sim += min(0.2, relation_overlap * 0.1)
    return sim


def knn_score(tokens: set[str], card: dict[str, Any], model: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    k = max(1, int(model.get("k", 11)))
    target = card.get("target", {}) or {}
    target_name = str(target.get("name") or "")
    fid = str(target.get("functionality_id") or "")
    scored: list[tuple[float, dict[str, Any]]] = []
    for example in model.get("examples", []):
        example_tokens = set(example.get("tokens") or [])
        if not example_tokens:
            continue
        sim = jaccard(tokens, example_tokens)
        if target_name and target_name == example.get("target"):
            sim += 0.2
        if fid and fid == str(example.get("functionality_id", "")):
            sim += 0.2
        if semantic_pred_label(card) == example.get("semantic_pred_label"):
            sim += 0.05
        scored.append((sim, example))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:k]
    if not top or top[0][0] <= 0:
        labels = model.get("label_counts", {})
        pos = int(labels.get("1", 0))
        neg = int(labels.get("0", 0))
        fallback = pos / (pos + neg) if pos + neg else 0.5
        return fallback, []
    weight_sum = sum(max(0.0001, sim) for sim, _ in top)
    pos_weight = sum(max(0.0001, sim) for sim, ex in top if int(ex.get("gold_label", 0)) == 1)
    neighbors = [
        {
            "pair_id": ex.get("pair_id"),
            "gold_label": ex.get("gold_label"),
            "similarity": round(sim, 4),
            "hard_positive": bool(ex.get("hard_positive")),
            "hard_negative": bool(ex.get("hard_negative")),
        }
        for sim, ex in top[:5]
    ]
    return pos_weight / weight_sum, neighbors


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def feature_tokens(card: dict[str, Any], pair: ClonePair | None = None) -> set[str]:
    tokens: set[str] = set()
    target = card.get("target", {}) or {}
    add_token(tokens, "target_name", target.get("name"))
    add_token(tokens, "functionality_id", target.get("functionality_id"))

    local = card.get("local_evidence", {}) or {}
    add_token(tokens, "target_family", local.get("target_family"))
    for family in local.get("shared_feature_families", []) or []:
        add_token(tokens, "shared_family", family)
    for flag in local.get("risk_flags", []) or []:
        add_token(tokens, "local_risk_exact", flag)
        add_text_tokens(tokens, "local_risk", str(flag))

    decision = card.get("decision", {}) or {}
    add_token(tokens, "semantic_verdict", decision.get("verdict"))
    add_token(tokens, "semantic_pred", decision.get("pred_label"))
    add_token(tokens, "semantic_confidence", confidence_bucket(decision.get("confidence")))
    for flag in decision.get("risk_flags", []) or []:
        add_token(tokens, "decision_risk_exact", flag)
        add_text_tokens(tokens, "decision_risk", str(flag))

    dynamic = card.get("dynamic_evidence", {}) or {}
    add_token(tokens, "dynamic_status", dynamic.get("status") or "not_run")
    parsed = (dynamic.get("execution") or {}).get("parsed") if isinstance(dynamic.get("execution"), dict) else None
    if isinstance(parsed, dict):
        add_token(tokens, "dynamic_same", parsed.get("same"))

    llm = card.get("llm_evidence", {}) or {}
    if llm:
        add_token(tokens, "llm_verdict", llm.get("verdict"))
        add_token(tokens, "llm_pred", llm.get("pred_label"))
        add_token(tokens, "llm_semantic_verdict", llm.get("semantic_verdict"))
        add_token(tokens, "llm_bcb_gold_verdict", llm.get("bcb_gold_verdict"))
        add_token(tokens, "llm_bcb_gold_confidence", confidence_bucket(llm.get("bcb_gold_confidence")))
        shared = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
        if isinstance(shared, dict):
            add_token(tokens, "slice_exists", shared.get("exists"))
            add_token(tokens, "slice_alignment", shared.get("bcb_target_alignment"))
            add_text_tokens(tokens, "slice_desc", str(shared.get("description", "")))
        for flag in llm.get("semantic_risk_flags", []) or []:
            add_token(tokens, "llm_risk_exact", flag)
            add_text_tokens(tokens, "llm_risk", str(flag))
        for item in llm.get("wrapper_differences", []) or []:
            add_text_tokens(tokens, "wrapper", str(item))

    if pair:
        add_code_tokens(tokens, pair.code_a, "a")
        add_code_tokens(tokens, pair.code_b, "b")
        add_code_relation_tokens(tokens, pair.code_a, pair.code_b)
    return tokens


def add_code_tokens(tokens: set[str], code: str, side: str) -> None:
    value = code.lower()
    signature = value.split("{", 1)[0]
    for marker in [
        "fileinputstream",
        "fileoutputstream",
        "ioutils.copy",
        "fileutils.copyfile",
        "files.copy",
        "transferfrom",
        "transferto",
        "zipinputstream",
        "zipoutputstream",
        "jaroutputstream",
        "messageDigest".lower(),
        "md5",
        "sha-1",
        "sha-256",
        "sha-512",
        "http",
        "url(",
        "socket",
        "servlet",
        "jpopupmenu",
        "actionlistener",
        "upload",
        "download",
        "screenshot",
        "backup",
        "copyfile",
        "inputstream",
        "outputstream",
        "stringwriter",
        "bytearrayoutputstream",
    ]:
        if marker in value:
            add_token(tokens, f"code_{side}", marker)
    for name in re.findall(r"\b([a-zA-Z_$][\w$]*)\s*\(", signature):
        add_token(tokens, f"method_{side}", name)


def add_code_relation_tokens(tokens: set[str], code_a: str, code_b: str) -> None:
    markers_a = code_marker_set(code_a)
    markers_b = code_marker_set(code_b)
    for marker in sorted(markers_a & markers_b):
        add_token(tokens, "both_code_marker", marker)
    for marker in sorted((markers_a ^ markers_b) & IMPORTANT_ASYMMETRIC_MARKERS):
        add_token(tokens, "one_side_code_marker", marker)

    hash_a = extract_hash_algorithms(code_a)
    hash_b = extract_hash_algorithms(code_b)
    for algo in sorted(hash_a & hash_b):
        add_token(tokens, "hash_algorithm_relation", f"same_{algo}")
    if hash_a and hash_b and not (hash_a & hash_b):
        add_token(tokens, "hash_algorithm_relation", "mismatch")
        add_token(tokens, "hash_algorithm_pair", f"{'+'.join(sorted(hash_a))}|{'+'.join(sorted(hash_b))}")

    low_a = code_a.lower()
    low_b = code_b.lower()
    if has_filtered_stream_copy(low_a, low_b):
        add_token(tokens, "copy_relation", "filtered_stream_vs_file_copy")
    if has_download_vs_plain_copy(low_a, low_b):
        add_token(tokens, "copy_relation", "download_or_remote_vs_plain_copy")


IMPORTANT_ASYMMETRIC_MARKERS = {
    "fileinputstream",
    "fileoutputstream",
    "ioutils.copy",
    "fileutils.copyfile",
    "files.copy",
    "transferfrom",
    "transferto",
    "zipinputstream",
    "zipoutputstream",
    "jaroutputstream",
    "http",
    "url(",
    "socket",
    "servlet",
    "jpopupmenu",
    "upload",
    "download",
    "bytearrayoutputstream",
}


def code_marker_set(code: str) -> set[str]:
    value = code.lower()
    return {marker for marker in IMPORTANT_ASYMMETRIC_MARKERS if marker in value}


def extract_hash_algorithms(code: str) -> set[str]:
    value = code.lower()
    algorithms: set[str] = set()
    if "md5" in value:
        algorithms.add("md5")
    if "sha-1" in value or "sha1" in value:
        algorithms.add("sha1")
    if "sha-256" in value or "sha256" in value:
        algorithms.add("sha256")
    if "sha-512" in value or "sha512" in value:
        algorithms.add("sha512")
    return algorithms


def has_filtered_stream_copy(low_a: str, low_b: str) -> bool:
    left_filtered = "bytefilter" in low_a or "filter" in low_a
    right_filtered = "bytefilter" in low_b or "filter" in low_b
    left_plain_file = "fileinputstream" in low_a and "fileoutputstream" in low_a
    right_plain_file = "fileinputstream" in low_b and "fileoutputstream" in low_b
    return (left_filtered and right_plain_file) or (right_filtered and left_plain_file)


def has_download_vs_plain_copy(low_a: str, low_b: str) -> bool:
    left_remote = "url(" in low_a or "http" in low_a or "download" in low_a
    right_remote = "url(" in low_b or "http" in low_b or "download" in low_b
    left_plain_file = "fileinputstream" in low_a and "fileoutputstream" in low_a
    right_plain_file = "fileinputstream" in low_b and "fileoutputstream" in low_b
    return (left_remote and right_plain_file and not right_remote) or (right_remote and left_plain_file and not left_remote)


def add_token(tokens: set[str], prefix: str, value: Any) -> None:
    if value is None:
        return
    text = normalize_piece(str(value))
    if text:
        tokens.add(f"{prefix}:{text}")


def add_text_tokens(tokens: set[str], prefix: str, value: str) -> None:
    text = value.lower()
    for keyword in [
        "only one side",
        "boundary_guard",
        "copy",
        "download",
        "upload",
        "stream",
        "file",
        "zip",
        "jar",
        "hash",
        "md5",
        "sha",
        "test",
        "gui",
        "wrapper",
        "fragment",
        "missing",
        "socket",
        "http",
        "resource",
        "classpath",
        "backup",
        "archive",
        "serialize",
        "transform",
        "parse",
        "semantic",
    ]:
        if keyword in text:
            add_token(tokens, prefix, keyword)
    for word in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", text):
        if len(word) <= 32:
            add_token(tokens, prefix, word)


def normalize_piece(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_\-.:]+", "_", value)
    return value.strip("_")[:80]


def confidence_bucket(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if number < 0.34:
        return "low"
    if number < 0.67:
        return "mid"
    return "high"


def semantic_pred_label(card: dict[str, Any]) -> int | None:
    pred = (card.get("decision") or {}).get("pred_label")
    return int(pred) if pred in (0, 1) else None


def mine_hard_cases(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for card in cards:
        gold = int(card.get("gold", {}).get("label", 0))
        pred = semantic_pred_label(card)
        case_type = ""
        if gold == 1 and pred != 1:
            case_type = "hard_positive"
        elif gold == 0 and pred == 1:
            case_type = "hard_negative"
        elif pred is None:
            case_type = "abstained"
        if not case_type:
            continue
        result.append(
            {
                "case_type": case_type,
                "pair_id": card.get("pair_id"),
                "gold_label": gold,
                "semantic_pred_label": pred,
                "target": card.get("target", {}),
                "decision": card.get("decision", {}),
                "llm_evidence": card.get("llm_evidence"),
                "dynamic_evidence": card.get("dynamic_evidence"),
            }
        )
    return result
