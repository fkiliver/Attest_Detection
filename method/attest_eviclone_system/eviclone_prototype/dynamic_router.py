from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .config import DEFAULT_BASE_MODEL
from .dataset import ClonePair
from .executor import parse_method, supported_probe
from .evidence import VERDICT_TO_LABEL, append_reason, safe_float


PairKey = tuple[str, str]


ROUTE_DECISION_SCHEMA_VERSION = "eviclone-dynamic-route-decision/v1"
LEARNED_ROUTE_MODEL_SCHEMA_VERSION = "eviclone-learned-dynamic-route-model/v1"
LEARNED_ROUTE_SCORE_CERTIFICATE_SCHEMA_VERSION = "eviclone-learned-route-score-certificate/v1"
BASE_MODEL_PASSTHROUGH_CERTIFICATE_SCHEMA_VERSION = "eviclone-base-model-passthrough-certificate/v1"
ROUTE_INPUT_BOUNDARY = "pre_execution_static_features_and_base_prediction_only"
ROUTE_TRAINING_TARGET = "run_dynamic_when_base_prediction_is_wrong"
ROUTE_COMPONENT_ROLE = "dynamic_evidence_router"
ROUTE_DECISION_KIND = "evidence_acquisition"
ROUTE_DYNAMIC_ACTION = "acquire_dynamic_evidence_then_programmatic_fusion"
ROUTE_PASSTHROUGH_ACTION = "base_model_passthrough"
DEFAULT_BASE_MODEL_SOURCE = DEFAULT_BASE_MODEL
ROUTE_ALLOWED_POLICIES = {
    "expected_dynamic_evidence_utility/v1",
    "learned_expected_dynamic_evidence_utility/v1",
}
ROUTE_FAILURE_BOUNDARY_AXES = [
    "base_model_uncertainty",
    "static_evidence_conflict",
    "semantic_gap",
    "context_dependency",
    "source_fragmentation",
    "probe_feasibility",
    "base_model_safe_region",
]
ROUTE_REASON_FAILURE_BOUNDARY_MAP = {
    "baseline_prediction_missing": "base_model_uncertainty",
    "low_base_model_margin": "base_model_uncertainty",
    "low_base_model_confidence": "base_model_uncertainty",
    "static_evidence_disagrees_with_base_model": "static_evidence_conflict",
    "local_static_evidence_inconclusive": "static_evidence_conflict",
    "target_functionality_static_asymmetry": "semantic_gap",
    "no_shared_static_feature_family": "semantic_gap",
    "low_identifier_overlap_needs_semantic_evidence": "semantic_gap",
    "unsupported_target_family_requires_evidence": "semantic_gap",
    "framework_or_environment_context_needed": "context_dependency",
    "method_fragment_or_parse_risk": "source_fragmentation",
    "deterministic_probe_available": "probe_feasibility",
    "no_builtin_probe_available": "probe_feasibility",
    "high_margin_base_model_region": "base_model_safe_region",
    "low_expected_dynamic_utility": "base_model_safe_region",
    "learned_dynamic_route_score_ge_threshold": "probe_feasibility",
    "learned_dynamic_route_score_below_threshold": "base_model_safe_region",
}
ROUTE_FORBIDDEN_TOP_LEVEL_KEYS = {
    "gold",
    "gold_label",
    "true_label",
    "ground_truth",
    "base_wrong",
    "final_label",
    "final_decision",
    "clone_label",
    "is_clone",
    "benchmark_label",
    "bcb_gold_verdict",
}
ROUTE_FORBIDDEN_FEATURE_KEYS = {
    "gold",
    "gold_label",
    "true_label",
    "ground_truth",
    "base_wrong",
    "final_label",
    "final_decision",
    "clone_label",
    "is_clone",
    "benchmark_label",
    "bcb_gold_verdict",
    "decision",
}


CONTEXT_DEPENDENCY_MARKERS = [
    "HttpServlet",
    "ServletRequest",
    "ServletResponse",
    "HttpSession",
    "JFrame",
    "JPanel",
    "JButton",
    "ActionEvent",
    "Connection",
    "PreparedStatement",
    "ResultSet",
    "DataSource",
    "EntityManager",
    "SessionFactory",
    "JdbcTemplate",
    "ApplicationContext",
    "RequestMapping",
    "Autowired",
]


TRUNCATION_MARKERS = [
    "/* ...",
    "... */",
    "// ...",
    "TODO",
]


@dataclass(frozen=True)
class BaseModelPrediction:
    label: int | None
    confidence: float | None = None
    margin: float | None = None
    source: str = DEFAULT_BASE_MODEL_SOURCE

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "confidence": self.confidence,
            "margin": self.margin,
            "source": self.source,
        }


@dataclass(frozen=True)
class DynamicRouteDecision:
    run_dynamic: bool
    score: float
    threshold: float
    tier: str
    reasons: list[str]
    features: dict[str, Any]
    base_prediction: BaseModelPrediction | None = None
    route_model_certificate: dict[str, Any] | None = None
    route_score_certificate: dict[str, Any] | None = None
    policy: str = "expected_dynamic_evidence_utility/v1"

    def to_dict(self) -> dict[str, Any]:
        failure_boundary = route_failure_boundary(self.features, self.reasons)
        payload = {
            "policy": self.policy,
            "run_dynamic": self.run_dynamic,
            "score": self.score,
            "threshold": self.threshold,
            "tier": self.tier,
            "reasons": self.reasons,
            "failure_boundary": failure_boundary,
            "features": self.features,
            "base_prediction": self.base_prediction.to_dict() if self.base_prediction else None,
        }
        if self.route_model_certificate:
            payload["route_model_certificate"] = dict(self.route_model_certificate)
        if self.route_score_certificate:
            payload["route_score_certificate"] = dict(self.route_score_certificate)
        payload["route_decision_certificate"] = build_route_decision_certificate(payload)
        return payload


LEARNED_ROUTE_FEATURE_NAMES = [
    "bias",
    "base_pred_is_positive",
    "base_margin",
    "base_uncertainty",
    "local_pred_is_positive",
    "local_unknown",
    "local_disagrees_with_base",
    "target_unsupported",
    "target_asymmetric",
    "shared_family_count",
    "no_shared_family",
    "identifier_similarity",
    "low_identifier_overlap",
    "high_identifier_overlap",
    "risk_count",
    "method_a_parsed",
    "method_b_parsed",
    "source_fragment_risk",
    "builtin_probe_supported",
    "context_dependency_risk",
    "context_dependency_count",
]


@dataclass(frozen=True)
class LearnedDynamicRouteModel:
    feature_names: list[str]
    weights: list[float]
    threshold: float
    policy: str = "learned_expected_dynamic_evidence_utility/v1"

    def score(self, features: dict[str, Any]) -> float:
        vector = dynamic_route_feature_vector(features)
        return sigmoid(sum(weight * value for weight, value in zip(self.weights, vector)))

    def should_run_dynamic(self, features: dict[str, Any]) -> bool:
        if features.get("base_label") not in (0, 1):
            return True
        return self.score(features) >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "model_type": "linear_logistic_dynamic_route_gate",
            "feature_names": self.feature_names,
            "weights": self.weights,
            "threshold": self.threshold,
            "policy": self.policy,
            "training_target": ROUTE_TRAINING_TARGET,
            "input_boundary": ROUTE_INPUT_BOUNDARY,
            "allowed_output": "run_dynamic_only",
            "final_decision_allowed": False,
            "gold_visible_at_inference": False,
        }
        payload["model_certificate"] = build_learned_route_model_certificate(payload)
        return payload

    def model_certificate(self) -> dict[str, Any]:
        return build_learned_route_model_certificate(self.to_dict())

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "LearnedDynamicRouteModel":
        feature_names = list(obj.get("feature_names") or LEARNED_ROUTE_FEATURE_NAMES)
        return cls(
            feature_names=feature_names,
            weights=[float(x) for x in obj["weights"]],
            threshold=float(obj["threshold"]),
            policy=str(obj.get("policy") or "learned_expected_dynamic_evidence_utility/v1"),
        )


def build_route_decision_certificate(route: dict[str, Any]) -> dict[str, Any]:
    payload = canonical_route_decision_payload(route)
    errors = validate_route_decision_payload(payload)
    certificate: dict[str, Any] = {
        "schema_version": ROUTE_DECISION_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "component_role": ROUTE_COMPONENT_ROLE,
        "decision_kind": ROUTE_DECISION_KIND,
        "input_boundary": ROUTE_INPUT_BOUNDARY,
        "training_target": ROUTE_TRAINING_TARGET,
        "allowed_output": "run_dynamic_only",
        "clone_label_output_allowed": False,
        "final_decision_allowed": False,
        "passthrough_action": ROUTE_PASSTHROUGH_ACTION,
        "dynamic_action": ROUTE_DYNAMIC_ACTION,
        "gold_visible": False,
        "policy": payload.get("policy"),
        "run_dynamic": payload.get("run_dynamic"),
        "score": payload.get("score"),
        "threshold": payload.get("threshold"),
        "feature_schema": list(LEARNED_ROUTE_FEATURE_NAMES),
        "failure_boundary_axes": list((payload.get("failure_boundary") or {}).get("axes") or []),
        "failure_boundary_primary_axis": (payload.get("failure_boundary") or {}).get("primary_axis"),
        "decision_sha256": canonical_json_sha256(payload),
        "validation_errors": errors,
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def verify_route_decision_certificate(route: dict[str, Any]) -> tuple[bool, list[str]]:
    forbidden_raw_paths = sorted(find_forbidden_route_payload_keys(route))
    if forbidden_raw_paths:
        return False, [
            "dynamic_route_certificate_untrusted:dynamic route contains forbidden decision keys: "
            + ",".join(forbidden_raw_paths[:8])
        ]
    expected = build_route_decision_certificate(route)
    if expected.get("status") != "verified":
        errors = expected.get("validation_errors") if isinstance(expected.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"dynamic_route_certificate_untrusted:{suffix}"]
    embedded = route.get("route_decision_certificate") if isinstance(route.get("route_decision_certificate"), dict) else {}
    if not embedded:
        return False, ["dynamic_route_certificate_missing"]
    if embedded.get("schema_version") != ROUTE_DECISION_SCHEMA_VERSION:
        return False, ["dynamic_route_certificate_schema_mismatch"]
    if embedded.get("component_role") != ROUTE_COMPONENT_ROLE:
        return False, ["dynamic_route_certificate_component_role_mismatch"]
    if embedded.get("decision_kind") != ROUTE_DECISION_KIND:
        return False, ["dynamic_route_certificate_decision_kind_mismatch"]
    if embedded.get("allowed_output") != "run_dynamic_only":
        return False, ["dynamic_route_certificate_allowed_output_mismatch"]
    if embedded.get("clone_label_output_allowed") is not False:
        return False, ["dynamic_route_certificate_allows_clone_label_output"]
    if embedded.get("final_decision_allowed") is not False:
        return False, ["dynamic_route_certificate_allows_final_decision"]
    if embedded.get("passthrough_action") != ROUTE_PASSTHROUGH_ACTION:
        return False, ["dynamic_route_certificate_passthrough_action_mismatch"]
    if embedded.get("dynamic_action") != ROUTE_DYNAMIC_ACTION:
        return False, ["dynamic_route_certificate_dynamic_action_mismatch"]
    actual_sha = canonical_json_sha256({key: value for key, value in embedded.items() if key != "certificate_sha256"})
    if embedded.get("certificate_sha256") != actual_sha:
        return False, ["dynamic_route_certificate_sha_mismatch"]
    if embedded.get("certificate_sha256") != expected.get("certificate_sha256"):
        return False, ["dynamic_route_certificate_recomputed_sha_mismatch"]
    return True, ["dynamic_route_certificate_verified"]


def canonical_route_decision_payload(route: dict[str, Any]) -> dict[str, Any]:
    features = route.get("features") if isinstance(route.get("features"), dict) else {}
    reasons = [str(reason) for reason in route.get("reasons") or []]
    failure_boundary = (
        route.get("failure_boundary")
        if isinstance(route.get("failure_boundary"), dict)
        else route_failure_boundary(features, reasons)
    )
    payload = {
        "policy": route.get("policy"),
        "run_dynamic": route.get("run_dynamic"),
        "score": route.get("score"),
        "threshold": route.get("threshold"),
        "tier": route.get("tier"),
        "reasons": reasons,
        "failure_boundary": failure_boundary,
        "features": features,
        "base_prediction": route.get("base_prediction") if isinstance(route.get("base_prediction"), dict) else None,
    }
    if isinstance(route.get("route_model_certificate"), dict):
        payload["route_model_certificate"] = route.get("route_model_certificate")
    if isinstance(route.get("route_score_certificate"), dict):
        payload["route_score_certificate"] = route.get("route_score_certificate")
    return payload


def validate_route_decision_payload(route: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    forbidden_top = sorted(key for key in route if normalize_route_key(str(key)) in ROUTE_FORBIDDEN_TOP_LEVEL_KEY_SET)
    if forbidden_top:
        errors.append("dynamic route contains forbidden decision keys: " + ",".join(forbidden_top))

    policy = str(route.get("policy") or "")
    if policy not in ROUTE_ALLOWED_POLICIES:
        errors.append("dynamic route policy is invalid")
    run_dynamic = route.get("run_dynamic")
    if run_dynamic not in (True, False):
        errors.append("dynamic route run_dynamic must be boolean")
    score = route_float(route.get("score"))
    threshold = route_float(route.get("threshold"))
    if score is None or not 0.0 <= score <= 1.0:
        errors.append("dynamic route score must be within [0,1]")
    if threshold is None or not 0.0 <= threshold <= 1.0:
        errors.append("dynamic route threshold must be within [0,1]")
    if score is not None and threshold is not None:
        expected_tier = route_tier(score, threshold)
        if route.get("tier") != expected_tier:
            errors.append("dynamic route tier does not match score/threshold")
    reasons = route.get("reasons")
    if not isinstance(reasons, list) or not reasons or any(not isinstance(item, str) for item in reasons):
        errors.append("dynamic route reasons must be a non-empty list of strings")
    failure_boundary = route.get("failure_boundary") if isinstance(route.get("failure_boundary"), dict) else {}
    if failure_boundary:
        axes = failure_boundary.get("axes")
        primary_axis = failure_boundary.get("primary_axis")
        if not isinstance(axes, list) or any(axis not in ROUTE_FAILURE_BOUNDARY_AXES for axis in axes):
            errors.append("dynamic route failure boundary axes are invalid")
        if primary_axis not in ROUTE_FAILURE_BOUNDARY_AXES:
            errors.append("dynamic route failure boundary primary_axis is invalid")
        if isinstance(reasons, list):
            expected_boundary = route_failure_boundary(
                route.get("features") if isinstance(route.get("features"), dict) else {},
                [str(reason) for reason in reasons],
            )
            if failure_boundary != expected_boundary:
                errors.append("dynamic route failure boundary does not match features and reasons")
    features = route.get("features")
    if not isinstance(features, dict):
        errors.append("dynamic route features must be an object")
    else:
        forbidden_features = sorted(find_forbidden_route_feature_keys(features))
        if forbidden_features:
            errors.append("dynamic route features contain forbidden decision keys: " + ",".join(forbidden_features[:8]))
        expected_vector_size = len(LEARNED_ROUTE_FEATURE_NAMES)
        if len(dynamic_route_feature_vector(features)) != expected_vector_size:
            errors.append("dynamic route feature vector size mismatch")

    base = route.get("base_prediction") if isinstance(route.get("base_prediction"), dict) else None
    base_label = coerce_label(base.get("label")) if base else None
    if run_dynamic is False and base_label not in (0, 1):
        errors.append("dynamic route pass-through requires a binary base prediction")
    if run_dynamic in (True, False) and score is not None and threshold is not None and base_label in (0, 1):
        expected_run_dynamic = score >= threshold
        if bool(run_dynamic) != expected_run_dynamic:
            errors.append("dynamic route run_dynamic does not match score threshold")
    model_certificate = route.get("route_model_certificate") if isinstance(route.get("route_model_certificate"), dict) else {}
    if policy == "learned_expected_dynamic_evidence_utility/v1":
        ok, reasons = verify_learned_route_model_certificate(model_certificate)
        if not ok:
            errors.append("learned dynamic route model certificate invalid: " + "|".join(reasons[:3]))
        else:
            if model_certificate.get("policy") != policy:
                errors.append("learned dynamic route model certificate policy mismatch")
            if threshold is not None and route_float(model_certificate.get("threshold")) != threshold:
                errors.append("learned dynamic route model certificate threshold mismatch")
        score_ok, score_reasons = verify_learned_route_score_certificate(route)
        if not score_ok:
            errors.append("learned dynamic route score certificate invalid: " + "|".join(score_reasons[:3]))
    elif model_certificate:
        errors.append("heuristic dynamic route must not carry a learned model certificate")
    elif isinstance(route.get("route_score_certificate"), dict):
        errors.append("heuristic dynamic route must not carry a learned score certificate")
    return errors


def build_learned_route_model_certificate(model: dict[str, Any]) -> dict[str, Any]:
    payload = canonical_learned_route_model_payload(model)
    errors = validate_learned_route_model_payload(payload)
    certificate: dict[str, Any] = {
        "schema_version": LEARNED_ROUTE_MODEL_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "model_type": payload.get("model_type"),
        "policy": payload.get("policy"),
        "training_target": payload.get("training_target"),
        "input_boundary": payload.get("input_boundary"),
        "allowed_output": payload.get("allowed_output"),
        "final_decision_allowed": payload.get("final_decision_allowed"),
        "gold_visible_at_inference": payload.get("gold_visible_at_inference"),
        "feature_schema": list(payload.get("feature_names") or []),
        "feature_schema_sha256": canonical_json_sha256(list(payload.get("feature_names") or [])),
        "weights_sha256": canonical_json_sha256(list(payload.get("weights") or [])),
        "threshold": payload.get("threshold"),
        "model_sha256": canonical_json_sha256(payload),
        "validation_errors": errors,
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def verify_learned_route_model_certificate(certificate: dict[str, Any]) -> tuple[bool, list[str]]:
    if not isinstance(certificate, dict) or not certificate:
        return False, ["learned_route_model_certificate_missing"]
    if certificate.get("schema_version") != LEARNED_ROUTE_MODEL_SCHEMA_VERSION:
        return False, ["learned_route_model_certificate_schema_mismatch"]
    expected_sha = canonical_json_sha256({key: value for key, value in certificate.items() if key != "certificate_sha256"})
    if certificate.get("certificate_sha256") != expected_sha:
        return False, ["learned_route_model_certificate_sha_mismatch"]
    if certificate.get("status") != "verified":
        return False, ["learned_route_model_certificate_unverified"]
    if certificate.get("training_target") != ROUTE_TRAINING_TARGET:
        return False, ["learned_route_model_certificate_training_target_mismatch"]
    if certificate.get("input_boundary") != ROUTE_INPUT_BOUNDARY:
        return False, ["learned_route_model_certificate_input_boundary_mismatch"]
    if certificate.get("allowed_output") != "run_dynamic_only":
        return False, ["learned_route_model_certificate_allowed_output_mismatch"]
    if certificate.get("final_decision_allowed") is not False:
        return False, ["learned_route_model_certificate_allows_final_decision"]
    if certificate.get("gold_visible_at_inference") is not False:
        return False, ["learned_route_model_certificate_allows_gold_inference"]
    if certificate.get("feature_schema") != LEARNED_ROUTE_FEATURE_NAMES:
        return False, ["learned_route_model_certificate_feature_schema_mismatch"]
    if certificate.get("feature_schema_sha256") != canonical_json_sha256(LEARNED_ROUTE_FEATURE_NAMES):
        return False, ["learned_route_model_certificate_feature_schema_sha_mismatch"]
    threshold = route_float(certificate.get("threshold"))
    if threshold is None or not 0.0 <= threshold <= 1.0:
        return False, ["learned_route_model_certificate_threshold_invalid"]
    for hash_field in ["weights_sha256", "model_sha256"]:
        value = str(certificate.get(hash_field) or "")
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value.lower()):
            return False, [f"learned_route_model_certificate_{hash_field}_invalid"]
    return True, ["learned_route_model_certificate_verified"]


def verify_learned_route_model_artifact(model: dict[str, Any]) -> tuple[bool, list[str]]:
    if not isinstance(model, dict) or not model:
        return False, ["learned_route_model_artifact_missing"]
    embedded = model.get("model_certificate") if isinstance(model.get("model_certificate"), dict) else {}
    if not embedded:
        return False, ["learned_route_model_certificate_missing"]
    ok, reasons = verify_learned_route_model_certificate(embedded)
    if not ok:
        return False, reasons
    expected = build_learned_route_model_certificate(model)
    if embedded.get("certificate_sha256") != expected.get("certificate_sha256"):
        return False, ["learned_route_model_certificate_recomputed_sha_mismatch"]
    if embedded.get("model_sha256") != expected.get("model_sha256"):
        return False, ["learned_route_model_certificate_model_sha_mismatch"]
    if embedded.get("weights_sha256") != expected.get("weights_sha256"):
        return False, ["learned_route_model_certificate_weights_sha_mismatch"]
    return True, ["learned_route_model_artifact_verified"]


def build_learned_route_score_certificate(
    *,
    model: LearnedDynamicRouteModel,
    features: dict[str, Any],
    score: float,
    threshold: float,
    run_dynamic: bool,
) -> dict[str, Any]:
    model_payload = model.to_dict()
    model_certificate = model_payload["model_certificate"]
    feature_vector = dynamic_route_feature_vector(features)
    weights = [float(weight) for weight in model.weights]
    raw_recomputed_score = round(sigmoid(sum(weight * value for weight, value in zip(weights, feature_vector))), 6)
    baseline_missing_override = features.get("base_label") not in (0, 1)
    recomputed_score = round(max(raw_recomputed_score, threshold), 6) if baseline_missing_override else raw_recomputed_score
    expected_run_dynamic = True if baseline_missing_override else recomputed_score >= threshold
    payload = {
        "schema_version": LEARNED_ROUTE_SCORE_CERTIFICATE_SCHEMA_VERSION,
        "policy": model.policy,
        "training_target": ROUTE_TRAINING_TARGET,
        "input_boundary": ROUTE_INPUT_BOUNDARY,
        "allowed_output": "run_dynamic_only",
        "final_decision_allowed": False,
        "gold_visible_at_inference": False,
        "feature_names": list(model.feature_names),
        "feature_vector": feature_vector,
        "feature_vector_sha256": canonical_json_sha256(feature_vector),
        "weights": weights,
        "weights_sha256": canonical_json_sha256(weights),
        "model_sha256": model_certificate.get("model_sha256"),
        "model_certificate_sha256": model_certificate.get("certificate_sha256"),
        "threshold": threshold,
        "score": round(float(score), 6),
        "raw_recomputed_score": raw_recomputed_score,
        "recomputed_score": recomputed_score,
        "baseline_missing_override": baseline_missing_override,
        "run_dynamic": bool(run_dynamic),
        "expected_run_dynamic": bool(expected_run_dynamic),
    }
    errors = validate_learned_route_score_payload(payload)
    certificate = dict(payload)
    certificate["status"] = "verified" if not errors else "rejected"
    certificate["validation_errors"] = errors
    certificate["score_certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "score_certificate_sha256"}
    )
    return certificate


def verify_learned_route_score_certificate(route: dict[str, Any]) -> tuple[bool, list[str]]:
    certificate = route.get("route_score_certificate") if isinstance(route.get("route_score_certificate"), dict) else {}
    if not certificate:
        return False, ["learned_route_score_certificate_missing"]
    if certificate.get("schema_version") != LEARNED_ROUTE_SCORE_CERTIFICATE_SCHEMA_VERSION:
        return False, ["learned_route_score_certificate_schema_mismatch"]
    actual_sha = canonical_json_sha256({key: value for key, value in certificate.items() if key != "score_certificate_sha256"})
    if certificate.get("score_certificate_sha256") != actual_sha:
        return False, ["learned_route_score_certificate_sha_mismatch"]
    if certificate.get("status") != "verified":
        return False, ["learned_route_score_certificate_unverified"]
    payload_errors = validate_learned_route_score_payload(certificate)
    if payload_errors:
        return False, ["learned_route_score_certificate_invalid:" + "|".join(payload_errors[:3])]

    features = route.get("features") if isinstance(route.get("features"), dict) else {}
    feature_vector = dynamic_route_feature_vector(features)
    if certificate.get("feature_vector") != feature_vector:
        return False, ["learned_route_score_certificate_feature_vector_mismatch"]
    if certificate.get("feature_vector_sha256") != canonical_json_sha256(feature_vector):
        return False, ["learned_route_score_certificate_feature_vector_sha_mismatch"]

    try:
        weights = [float(weight) for weight in certificate.get("weights") or []]
    except (TypeError, ValueError):
        return False, ["learned_route_score_certificate_weights_invalid"]
    raw_recomputed_score = round(sigmoid(sum(weight * value for weight, value in zip(weights, feature_vector))), 6)
    baseline_missing_override = features.get("base_label") not in (0, 1)
    recomputed_score = round(max(raw_recomputed_score, route_float(certificate.get("threshold")) or 0.0), 6) if baseline_missing_override else raw_recomputed_score
    if route_float(certificate.get("raw_recomputed_score")) != raw_recomputed_score:
        return False, ["learned_route_score_certificate_raw_recomputed_score_mismatch"]
    if bool(certificate.get("baseline_missing_override")) != bool(baseline_missing_override):
        return False, ["learned_route_score_certificate_baseline_missing_override_mismatch"]
    if route_float(certificate.get("recomputed_score")) != recomputed_score:
        return False, ["learned_route_score_certificate_recomputed_score_mismatch"]
    route_score = route_float(route.get("score"))
    if route_score is None or round(route_score, 6) != recomputed_score:
        return False, ["learned_route_score_certificate_route_score_mismatch"]
    if route_float(certificate.get("score")) != round(route_score, 6):
        return False, ["learned_route_score_certificate_score_mismatch"]

    route_threshold = route_float(route.get("threshold"))
    if route_threshold is None or route_float(certificate.get("threshold")) != route_threshold:
        return False, ["learned_route_score_certificate_threshold_mismatch"]
    expected_run_dynamic = True if baseline_missing_override else recomputed_score >= route_threshold
    if bool(certificate.get("expected_run_dynamic")) != bool(expected_run_dynamic):
        return False, ["learned_route_score_certificate_expected_run_dynamic_mismatch"]
    if bool(certificate.get("run_dynamic")) != bool(route.get("run_dynamic")):
        return False, ["learned_route_score_certificate_run_dynamic_mismatch"]
    if bool(route.get("run_dynamic")) != bool(expected_run_dynamic):
        return False, ["learned_route_score_certificate_route_run_dynamic_mismatch"]

    model_certificate = route.get("route_model_certificate") if isinstance(route.get("route_model_certificate"), dict) else {}
    if model_certificate:
        if certificate.get("model_sha256") != model_certificate.get("model_sha256"):
            return False, ["learned_route_score_certificate_model_sha_mismatch"]
        if certificate.get("weights_sha256") != model_certificate.get("weights_sha256"):
            return False, ["learned_route_score_certificate_weights_sha_mismatch"]
        if certificate.get("model_certificate_sha256") != model_certificate.get("certificate_sha256"):
            return False, ["learned_route_score_certificate_model_certificate_sha_mismatch"]
    model_payload = {
        "model_type": "linear_logistic_dynamic_route_gate",
        "feature_names": list(certificate.get("feature_names") or []),
        "weights": weights,
        "threshold": route_threshold,
        "policy": certificate.get("policy"),
        "training_target": certificate.get("training_target"),
        "input_boundary": certificate.get("input_boundary"),
        "allowed_output": certificate.get("allowed_output"),
        "final_decision_allowed": certificate.get("final_decision_allowed"),
        "gold_visible_at_inference": certificate.get("gold_visible_at_inference"),
    }
    if certificate.get("model_sha256") != canonical_json_sha256(canonical_learned_route_model_payload(model_payload)):
        return False, ["learned_route_score_certificate_model_payload_sha_mismatch"]
    return True, ["learned_route_score_certificate_verified"]


def validate_learned_route_score_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("policy") != "learned_expected_dynamic_evidence_utility/v1":
        errors.append("learned route score policy is invalid")
    if payload.get("training_target") != ROUTE_TRAINING_TARGET:
        errors.append("learned route score training_target is invalid")
    if payload.get("input_boundary") != ROUTE_INPUT_BOUNDARY:
        errors.append("learned route score input_boundary is invalid")
    if payload.get("allowed_output") != "run_dynamic_only":
        errors.append("learned route score allowed_output is invalid")
    if payload.get("final_decision_allowed") is not False:
        errors.append("learned route score must not allow final decisions")
    if payload.get("gold_visible_at_inference") is not False:
        errors.append("learned route score must not see gold at inference")
    if payload.get("feature_names") != LEARNED_ROUTE_FEATURE_NAMES:
        errors.append("learned route score feature schema mismatch")
    feature_vector = payload.get("feature_vector") if isinstance(payload.get("feature_vector"), list) else []
    weights = payload.get("weights") if isinstance(payload.get("weights"), list) else []
    try:
        numeric_weights = [float(weight) for weight in weights]
    except (TypeError, ValueError):
        numeric_weights = []
        errors.append("learned route score weights must be numeric")
    if len(feature_vector) != len(LEARNED_ROUTE_FEATURE_NAMES):
        errors.append("learned route score feature vector length mismatch")
    if len(weights) != len(LEARNED_ROUTE_FEATURE_NAMES):
        errors.append("learned route score weights length mismatch")
    if payload.get("feature_vector_sha256") != canonical_json_sha256(feature_vector):
        errors.append("learned route score feature vector sha mismatch")
    if payload.get("weights_sha256") != canonical_json_sha256(numeric_weights):
        errors.append("learned route score weights sha mismatch")
    threshold = route_float(payload.get("threshold"))
    score = route_float(payload.get("score"))
    raw_recomputed = route_float(payload.get("raw_recomputed_score"))
    recomputed = route_float(payload.get("recomputed_score"))
    if threshold is None or not 0.0 <= threshold <= 1.0:
        errors.append("learned route score threshold must be within [0,1]")
    if score is None or not 0.0 <= score <= 1.0:
        errors.append("learned route score must be within [0,1]")
    if raw_recomputed is None or not 0.0 <= raw_recomputed <= 1.0:
        errors.append("learned route raw recomputed score must be within [0,1]")
    if recomputed is None or not 0.0 <= recomputed <= 1.0:
        errors.append("learned route recomputed score must be within [0,1]")
    if score is not None and recomputed is not None and round(score, 6) != round(recomputed, 6):
        errors.append("learned route score must equal recomputed score")
    for hash_field in ["model_sha256", "model_certificate_sha256"]:
        value = str(payload.get(hash_field) or "")
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value.lower()):
            errors.append(f"learned route score {hash_field} is invalid")
    return errors


def canonical_learned_route_model_payload(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_type": model.get("model_type"),
        "feature_names": list(model.get("feature_names") or []),
        "weights": [float(weight) for weight in model.get("weights") or []],
        "threshold": route_float(model.get("threshold")),
        "policy": model.get("policy"),
        "training_target": model.get("training_target"),
        "input_boundary": model.get("input_boundary"),
        "allowed_output": model.get("allowed_output"),
        "final_decision_allowed": model.get("final_decision_allowed"),
        "gold_visible_at_inference": model.get("gold_visible_at_inference"),
    }


def validate_learned_route_model_payload(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if model.get("model_type") != "linear_logistic_dynamic_route_gate":
        errors.append("learned route model_type is invalid")
    if model.get("policy") != "learned_expected_dynamic_evidence_utility/v1":
        errors.append("learned route model policy is invalid")
    if model.get("training_target") != ROUTE_TRAINING_TARGET:
        errors.append("learned route model training_target is invalid")
    if model.get("input_boundary") != ROUTE_INPUT_BOUNDARY:
        errors.append("learned route model input_boundary is invalid")
    if model.get("allowed_output") != "run_dynamic_only":
        errors.append("learned route model allowed_output is invalid")
    if model.get("final_decision_allowed") is not False:
        errors.append("learned route model must not allow final decisions")
    if model.get("gold_visible_at_inference") is not False:
        errors.append("learned route model must not see gold at inference")
    if model.get("feature_names") != LEARNED_ROUTE_FEATURE_NAMES:
        errors.append("learned route model feature schema mismatch")
    weights = model.get("weights") if isinstance(model.get("weights"), list) else []
    if len(weights) != len(LEARNED_ROUTE_FEATURE_NAMES):
        errors.append("learned route model weights length mismatch")
    threshold = route_float(model.get("threshold"))
    if threshold is None or not 0.0 <= threshold <= 1.0:
        errors.append("learned route model threshold must be within [0,1]")
    forbidden = sorted(find_forbidden_route_feature_keys(model))
    if forbidden:
        errors.append("learned route model contains forbidden decision keys: " + ",".join(forbidden[:8]))
    return errors


def find_forbidden_route_payload_keys(value: Any, *, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).strip()
            child_path = f"{prefix}.{key_text}" if prefix else key_text
            if normalize_route_key(key_text) in ROUTE_FORBIDDEN_PAYLOAD_KEY_SET:
                found.add(child_path)
            found.update(find_forbidden_route_payload_keys(child, prefix=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            found.update(find_forbidden_route_payload_keys(child, prefix=child_path))
    return found


def find_forbidden_route_feature_keys(value: Any, *, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).strip()
            lowered = normalize_route_key(key_text)
            child_path = f"{prefix}.{key_text}" if prefix else key_text
            if lowered in ROUTE_FORBIDDEN_FEATURE_KEY_SET:
                found.add(child_path)
            found.update(find_forbidden_route_feature_keys(child, prefix=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.update(find_forbidden_route_feature_keys(child, prefix=f"{prefix}[{index}]"))
    return found


def normalize_route_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


ROUTE_FORBIDDEN_TOP_LEVEL_KEY_SET = {normalize_route_key(key) for key in ROUTE_FORBIDDEN_TOP_LEVEL_KEYS}
ROUTE_FORBIDDEN_FEATURE_KEY_SET = {normalize_route_key(key) for key in ROUTE_FORBIDDEN_FEATURE_KEYS}
ROUTE_FORBIDDEN_PAYLOAD_KEY_SET = ROUTE_FORBIDDEN_TOP_LEVEL_KEY_SET | ROUTE_FORBIDDEN_FEATURE_KEY_SET


def route_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def pair_key(function_id_a: str, function_id_b: str) -> PairKey:
    return str(function_id_a), str(function_id_b)


def card_pair_key(card: dict[str, Any]) -> PairKey:
    ids = card.get("function_ids") or {}
    return pair_key(str(ids.get("a", "")), str(ids.get("b", "")))


def route_dynamic_execution(
    pair: ClonePair,
    card: dict[str, Any],
    *,
    base_prediction: BaseModelPrediction | None = None,
    threshold: float = 0.5,
    mode: str = "execute",
    model: LearnedDynamicRouteModel | None = None,
) -> DynamicRouteDecision:
    """Estimate whether dynamic evidence is worth acquiring for this pair.

    This router is intentionally not a clone classifier. It predicts the expected
    utility of entering the expensive executable-evidence branch. Samples routed
    out should keep the base model prediction unchanged.
    """
    features = dynamic_route_features(pair, card, base_prediction=base_prediction, mode=mode)
    if model is None:
        score, reasons = dynamic_route_score(features)
        active_threshold = threshold
        policy = "expected_dynamic_evidence_utility/v1"
        route_model_certificate = None
        route_score_certificate = None
    else:
        score = model.score(features)
        active_threshold = model.threshold
        policy = model.policy
        reasons = []
        route_model_certificate = model.model_certificate()
        route_score_certificate = None

    baseline_missing = base_prediction is None or base_prediction.label not in (0, 1)
    if baseline_missing:
        run_dynamic = True
        score = max(score, active_threshold)
    else:
        score = round(score, 6)
        run_dynamic = score >= active_threshold

    score = round(score, 6)
    if model is not None:
        reasons = learned_route_reasons(features, score, active_threshold)
    if baseline_missing:
        reasons = ["baseline_prediction_missing"] + [reason for reason in reasons if reason != "baseline_prediction_missing"]
    if model is not None:
        route_score_certificate = build_learned_route_score_certificate(
            model=model,
            features=features,
            score=score,
            threshold=active_threshold,
            run_dynamic=run_dynamic,
        )
    return DynamicRouteDecision(
        run_dynamic=run_dynamic,
        score=score,
        threshold=active_threshold,
        tier=route_tier(score, active_threshold),
        reasons=reasons,
        features=features,
        base_prediction=base_prediction,
        route_model_certificate=route_model_certificate,
        route_score_certificate=route_score_certificate,
        policy=policy,
    )


def dynamic_route_features(
    pair: ClonePair,
    card: dict[str, Any],
    *,
    base_prediction: BaseModelPrediction | None = None,
    mode: str = "execute",
) -> dict[str, Any]:
    local = card.get("local_evidence") or {}
    decision = card.get("decision") or {}
    risk_flags = [str(item) for item in local.get("risk_flags") or []]
    local_pred = decision.get("pred_label")
    if local_pred not in (0, 1):
        local_pred = None
    base_label = base_prediction.label if base_prediction else None
    base_confidence = base_prediction.confidence if base_prediction else None
    base_margin = base_prediction.margin if base_prediction else None
    if base_margin is None and base_confidence is not None:
        base_margin = abs(float(base_confidence) - 0.5) * 2.0

    method_a = parse_method(pair.code_a)
    method_b = parse_method(pair.code_b)
    builtin_probe_supported = False
    if method_a is not None and method_b is not None and mode == "execute":
        _family, probe = supported_probe(pair, method_a, method_b)
        builtin_probe_supported = bool(probe)

    code_text = f"{pair.code_a}\n{pair.code_b}"
    context_markers = sorted(
        {marker for marker in CONTEXT_DEPENDENCY_MARKERS if re.search(rf"\b{re.escape(marker)}\b", code_text)}
    )
    target_family = str(local.get("target_family") or "unknown")
    shared_families = list(local.get("shared_feature_families") or [])
    identifier_similarity = safe_float(local.get("identifier_similarity"), 0.0)
    target_asymmetric = any("only one side" in item.lower() for item in risk_flags)
    no_shared_family = any("no shared high-level feature family" in item.lower() for item in risk_flags)
    target_unsupported = target_family == "unknown"
    local_unknown = local_pred is None
    local_disagrees_with_base = local_pred in (0, 1) and base_label in (0, 1) and int(local_pred) != int(base_label)
    source_fragment_risk = method_a is None or method_b is None or has_truncation_marker(code_text)

    return {
        "base_label": base_label,
        "base_confidence": base_confidence,
        "base_margin": base_margin,
        "base_uncertainty": 1.0 - clamp01(base_margin) if base_margin is not None else 0.35,
        "local_pred": local_pred,
        "local_unknown": local_unknown,
        "local_disagrees_with_base": local_disagrees_with_base,
        "target_family": target_family,
        "target_unsupported": target_unsupported,
        "target_asymmetric": target_asymmetric,
        "shared_family_count": len(shared_families),
        "no_shared_family": no_shared_family,
        "identifier_similarity": identifier_similarity,
        "low_identifier_overlap": identifier_similarity < 0.05,
        "high_identifier_overlap": identifier_similarity >= 0.35,
        "risk_count": len(risk_flags),
        "risk_flags": risk_flags,
        "method_a_parsed": method_a is not None,
        "method_b_parsed": method_b is not None,
        "source_fragment_risk": source_fragment_risk,
        "builtin_probe_supported": builtin_probe_supported,
        "context_dependency_markers": context_markers,
        "context_dependency_count": len(context_markers),
        "context_dependency_risk": bool(context_markers),
        "mode": mode,
    }


def dynamic_route_score(features: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    def add(delta: float, reason: str) -> None:
        nonlocal score
        score += delta
        if reason not in reasons:
            reasons.append(reason)

    base_margin = features.get("base_margin")
    base_confidence = features.get("base_confidence")
    if features.get("base_label") not in (0, 1):
        add(0.30, "baseline_prediction_missing")
    elif base_margin is not None and safe_float(base_margin, 0.0) < 0.25:
        add(0.24, "low_base_model_margin")
    elif base_confidence is not None and 0.42 <= safe_float(base_confidence, 0.5) <= 0.58:
        add(0.18, "low_base_model_confidence")

    if features.get("local_disagrees_with_base"):
        add(0.26, "static_evidence_disagrees_with_base_model")
    if features.get("local_unknown"):
        add(0.12, "local_static_evidence_inconclusive")
    if features.get("target_asymmetric"):
        add(0.24, "target_functionality_static_asymmetry")
    if features.get("no_shared_family"):
        add(0.11, "no_shared_static_feature_family")
    if features.get("low_identifier_overlap"):
        add(0.08, "low_identifier_overlap_needs_semantic_evidence")
    if features.get("target_unsupported"):
        add(0.08, "unsupported_target_family_requires_evidence")
    if features.get("source_fragment_risk"):
        add(0.18, "method_fragment_or_parse_risk")
    if features.get("context_dependency_risk"):
        add(min(0.24, 0.08 + 0.04 * int(features.get("context_dependency_count") or 0)), "framework_or_environment_context_needed")
    if features.get("builtin_probe_supported"):
        add(0.18, "deterministic_probe_available")
    elif not features.get("context_dependency_risk"):
        add(-0.05, "no_builtin_probe_available")

    if (
        features.get("base_label") in (0, 1)
        and safe_float(features.get("base_margin"), 0.0) >= 0.70
        and not features.get("local_disagrees_with_base")
        and not features.get("target_asymmetric")
        and not features.get("context_dependency_risk")
        and not features.get("source_fragment_risk")
        and not features.get("no_shared_family")
    ):
        add(-0.25, "high_margin_base_model_region")

    return max(0.0, min(1.0, score)), reasons or ["low_expected_dynamic_utility"]


def learned_route_reasons(features: dict[str, Any], score: float, threshold: float) -> list[str]:
    _heuristic_score, heuristic_reasons = dynamic_route_score(features)
    reasons = ["learned_dynamic_route_score_ge_threshold"] if score >= threshold else ["learned_dynamic_route_score_below_threshold"]
    for reason in heuristic_reasons:
        if reason not in reasons:
            reasons.append(reason)
    return reasons


def route_failure_boundary(features: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    """Summarize why a sample is inside or outside the dynamic-evidence region."""
    axis_counts: Counter[str] = Counter()
    reason_axes: dict[str, str] = {}
    for reason in reasons:
        axis = ROUTE_REASON_FAILURE_BOUNDARY_MAP.get(str(reason), "semantic_gap")
        axis_counts[axis] += 1
        reason_axes[str(reason)] = axis
    if features.get("context_dependency_risk"):
        axis_counts["context_dependency"] += 1
    if features.get("source_fragment_risk"):
        axis_counts["source_fragmentation"] += 1
    if features.get("local_disagrees_with_base") or features.get("local_unknown"):
        axis_counts["static_evidence_conflict"] += 1
    if features.get("builtin_probe_supported"):
        axis_counts["probe_feasibility"] += 1
    if not axis_counts:
        axis_counts["base_model_safe_region"] += 1
    axes = [axis for axis in ROUTE_FAILURE_BOUNDARY_AXES if axis_counts.get(axis, 0) > 0]
    primary_axis = max(axes, key=lambda axis: (axis_counts[axis], -ROUTE_FAILURE_BOUNDARY_AXES.index(axis)))
    return {
        "schema_version": "eviclone-dynamic-route-failure-boundary/v1",
        "role": "static_model_failure_boundary_modeling",
        "primary_axis": primary_axis,
        "axes": axes,
        "axis_counts": {axis: axis_counts[axis] for axis in axes},
        "reason_axes": reason_axes,
        "context_dependency_markers": list(features.get("context_dependency_markers") or []),
        "source_fragment_risk": bool(features.get("source_fragment_risk")),
        "builtin_probe_supported": bool(features.get("builtin_probe_supported")),
    }


def dynamic_route_feature_vector(features: dict[str, Any]) -> list[float]:
    return [
        1.0,
        1.0 if features.get("base_label") == 1 else 0.0,
        clamp01(features.get("base_margin")),
        clamp01(features.get("base_uncertainty")),
        1.0 if features.get("local_pred") == 1 else 0.0,
        1.0 if features.get("local_unknown") else 0.0,
        1.0 if features.get("local_disagrees_with_base") else 0.0,
        1.0 if features.get("target_unsupported") else 0.0,
        1.0 if features.get("target_asymmetric") else 0.0,
        min(float(features.get("shared_family_count") or 0), 5.0) / 5.0,
        1.0 if features.get("no_shared_family") else 0.0,
        clamp01(features.get("identifier_similarity")),
        1.0 if features.get("low_identifier_overlap") else 0.0,
        1.0 if features.get("high_identifier_overlap") else 0.0,
        min(float(features.get("risk_count") or 0), 10.0) / 10.0,
        1.0 if features.get("method_a_parsed") else 0.0,
        1.0 if features.get("method_b_parsed") else 0.0,
        1.0 if features.get("source_fragment_risk") else 0.0,
        1.0 if features.get("builtin_probe_supported") else 0.0,
        1.0 if features.get("context_dependency_risk") else 0.0,
        min(float(features.get("context_dependency_count") or 0), 5.0) / 5.0,
    ]


def train_learned_dynamic_route(
    pairs: Iterable[ClonePair],
    cards: Iterable[dict[str, Any]],
    baseline_rows: dict[PairKey, Any],
    *,
    epochs: int = 300,
    learning_rate: float = 0.08,
    l2: float = 0.001,
    threshold_candidates: Iterable[float] | None = None,
    min_base_error_recall: float = 0.0,
    mode: str = "execute",
) -> dict[str, Any]:
    examples = dynamic_route_training_examples(pairs, cards, baseline_rows, mode=mode)
    if not examples:
        raise ValueError("no dynamic route training examples available")
    positives = sum(label for _, label in examples)
    negatives = len(examples) - positives
    pos_weight = len(examples) / (2 * positives) if positives else 1.0
    neg_weight = len(examples) / (2 * negatives) if negatives else 1.0

    weights = [0.0 for _ in LEARNED_ROUTE_FEATURE_NAMES]
    for _ in range(max(1, epochs)):
        grad = [0.0 for _ in weights]
        for vector, label in examples:
            pred = sigmoid(sum(weight * value for weight, value in zip(weights, vector)))
            sample_weight = pos_weight if label == 1 else neg_weight
            error = (pred - label) * sample_weight
            for idx, value in enumerate(vector):
                grad[idx] += error * value
        n = float(len(examples))
        for idx in range(len(weights)):
            regularizer = l2 * weights[idx] if idx != 0 else 0.0
            weights[idx] -= learning_rate * ((grad[idx] / n) + regularizer)

    thresholds = list(threshold_candidates or [i / 100 for i in range(0, 101)])
    best: dict[str, Any] | None = None
    grid: list[dict[str, Any]] = []
    for threshold in thresholds:
        model = LearnedDynamicRouteModel(list(LEARNED_ROUTE_FEATURE_NAMES), weights, float(threshold))
        result = evaluate_dynamic_route_gate(pairs, cards, baseline_rows, model=model, mode=mode)
        compact = {k: v for k, v in result.items() if k != "rows"}
        grid.append(compact)
        if result["base_error_count"] and result["base_error_recall"] < min_base_error_recall:
            continue
        if best is None or dynamic_route_sort_key(result) > dynamic_route_sort_key(best):
            best = result
    if best is None:
        fallback = LearnedDynamicRouteModel(list(LEARNED_ROUTE_FEATURE_NAMES), weights, 0.0)
        best = evaluate_dynamic_route_gate(pairs, cards, baseline_rows, model=fallback, mode=mode)
    model = LearnedDynamicRouteModel(list(LEARNED_ROUTE_FEATURE_NAMES), weights, float(best["threshold"]))
    return {
        "model": model,
        "training_examples": len(examples),
        "positive_examples": positives,
        "negative_examples": negatives,
        "best": best,
        "grid": grid,
        "training_target": "run_dynamic_when_base_prediction_is_wrong",
    }


def dynamic_route_training_examples(
    pairs: Iterable[ClonePair],
    cards: Iterable[dict[str, Any]],
    baseline_rows: dict[PairKey, Any],
    *,
    mode: str = "execute",
) -> list[tuple[list[float], int]]:
    card_by_pair = {card_pair_key(card): card for card in cards}
    examples: list[tuple[list[float], int]] = []
    for pair in pairs:
        key = pair_key(pair.function_id_a, pair.function_id_b)
        baseline = baseline_rows.get(key)
        card = card_by_pair.get(key)
        if baseline is None or card is None:
            continue
        base_label = coerce_label(getattr(baseline, "prediction", None))
        gold = coerce_label(getattr(baseline, "gold", None))
        if base_label not in (0, 1) or gold not in (0, 1):
            continue
        base_prediction = BaseModelPrediction(
            label=base_label,
            confidence=coerce_optional_float(getattr(baseline, "confidence", None)),
            margin=coerce_optional_float(getattr(baseline, "margin", None)),
            source=str(getattr(baseline, "source", DEFAULT_BASE_MODEL_SOURCE)),
        )
        features = dynamic_route_features(pair, card, base_prediction=base_prediction, mode=mode)
        label = 1 if base_label != gold else 0
        examples.append((dynamic_route_feature_vector(features), label))
    return examples


def evaluate_dynamic_route_gate(
    pairs: Iterable[ClonePair],
    cards: Iterable[dict[str, Any]],
    baseline_rows: dict[PairKey, Any],
    *,
    model: LearnedDynamicRouteModel | None = None,
    threshold: float = 0.5,
    mode: str = "execute",
) -> dict[str, Any]:
    card_by_pair = {card_pair_key(card): card for card in cards}
    counters = Counter()
    rows: list[dict[str, Any]] = []
    for pair in pairs:
        key = pair_key(pair.function_id_a, pair.function_id_b)
        baseline = baseline_rows.get(key)
        card = card_by_pair.get(key)
        if baseline is None:
            counters["missing_baseline"] += 1
            continue
        if card is None:
            counters["missing_card"] += 1
            continue
        base_label = coerce_label(getattr(baseline, "prediction", None))
        gold = coerce_label(getattr(baseline, "gold", None))
        if base_label not in (0, 1) or gold not in (0, 1):
            counters["invalid_label"] += 1
            continue
        base_prediction = BaseModelPrediction(
            label=base_label,
            confidence=coerce_optional_float(getattr(baseline, "confidence", None)),
            margin=coerce_optional_float(getattr(baseline, "margin", None)),
            source=str(getattr(baseline, "source", DEFAULT_BASE_MODEL_SOURCE)),
        )
        route = route_dynamic_execution(
            pair,
            card,
            base_prediction=base_prediction,
            threshold=threshold,
            mode=mode,
            model=model,
        )
        base_wrong = base_label != gold
        run_dynamic = route.run_dynamic
        failure_boundary = route_failure_boundary(route.features, route.reasons)
        counters["total"] += 1
        counters["base_error"] += int(base_wrong)
        counters["base_correct"] += int(not base_wrong)
        counters["route_to_dynamic"] += int(run_dynamic)
        counters["pass_through"] += int(not run_dynamic)
        counters["routed_base_errors"] += int(run_dynamic and base_wrong)
        counters["unnecessary_dynamic"] += int(run_dynamic and not base_wrong)
        counters["missed_base_errors"] += int((not run_dynamic) and base_wrong)
        counters["pass_through_correct"] += int((not run_dynamic) and not base_wrong)
        rows.append(
            {
                "pair_id": pair.pair_id,
                "function_id_a": key[0],
                "function_id_b": key[1],
                "gold": gold,
                "base_pred": base_label,
                "base_wrong": base_wrong,
                "run_dynamic": run_dynamic,
                "score": route.score,
                "threshold": route.threshold,
                "tier": route.tier,
                "reasons": route.reasons,
                "failure_boundary_primary_axis": failure_boundary["primary_axis"],
                "failure_boundary_axes": failure_boundary["axes"],
            }
        )
    total = counters["total"]
    route_count = counters["route_to_dynamic"]
    pass_count = counters["pass_through"]
    base_error_count = counters["base_error"]
    result = {
        "threshold": model.threshold if model is not None else threshold,
        "policy": model.policy if model is not None else "expected_dynamic_evidence_utility/v1",
        "total": total,
        "missing_baseline": counters["missing_baseline"],
        "missing_card": counters["missing_card"],
        "invalid_label": counters["invalid_label"],
        "base_error_count": base_error_count,
        "base_correct_count": counters["base_correct"],
        "route_to_dynamic": route_count,
        "pass_through": pass_count,
        "execution_reduction": ratio(pass_count, total),
        "route_rate": ratio(route_count, total),
        "routed_base_errors": counters["routed_base_errors"],
        "unnecessary_dynamic": counters["unnecessary_dynamic"],
        "missed_base_errors": counters["missed_base_errors"],
        "pass_through_correct": counters["pass_through_correct"],
        "route_precision": ratio(counters["routed_base_errors"], route_count),
        "base_error_recall": ratio(counters["routed_base_errors"], base_error_count),
        "pass_through_safety": ratio(counters["pass_through_correct"], pass_count),
        "oracle_dynamic_budget_accuracy_upper_bound": ratio(counters["base_correct"] + counters["routed_base_errors"], total),
        "rows": rows,
    }
    return result


def dynamic_route_sort_key(result: dict[str, Any]) -> tuple[Any, ...]:
    return (
        result.get("base_error_recall", 0.0),
        result.get("route_precision", 0.0),
        result.get("oracle_dynamic_budget_accuracy_upper_bound", 0.0),
        result.get("execution_reduction", 0.0),
        -result.get("route_to_dynamic", 0),
    )


def build_base_model_passthrough_certificate(
    *,
    route: dict[str, Any],
    decision: dict[str, Any],
    base_prediction: dict[str, Any],
) -> dict[str, Any]:
    payload = canonical_base_model_passthrough_payload(
        route=route,
        decision=decision,
        base_prediction=base_prediction,
    )
    errors = validate_base_model_passthrough_payload(payload)
    certificate: dict[str, Any] = {
        "schema_version": BASE_MODEL_PASSTHROUGH_CERTIFICATE_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "policy": "routed_base_model_passthrough/v1",
        "final_source": "base_model_passthrough",
        "final_label": payload.get("final_label"),
        "base_prediction": payload.get("base_prediction"),
        "route_run_dynamic": payload.get("route_run_dynamic"),
        "route_policy": payload.get("route_policy"),
        "route_decision_certificate_sha256": payload.get("route_decision_certificate_sha256"),
        "dynamic_evidence_allowed": False,
        "executable_fusion_allowed": False,
        "llm_final_decision_allowed": False,
        "validation_errors": errors,
    }
    certificate["passthrough_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "passthrough_sha256"}
    )
    return certificate


def verify_base_model_passthrough_certificate(card: dict[str, Any]) -> tuple[bool, list[str]]:
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    base_prediction = card.get("base_model_prediction") if isinstance(card.get("base_model_prediction"), dict) else {}
    embedded = card.get("base_model_passthrough") if isinstance(card.get("base_model_passthrough"), dict) else {}
    if not embedded:
        return False, ["base_model_passthrough_certificate_missing"]
    expected = build_base_model_passthrough_certificate(
        route=route,
        decision=decision,
        base_prediction=base_prediction,
    )
    if expected.get("status") != "verified":
        errors = expected.get("validation_errors") if isinstance(expected.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"base_model_passthrough_certificate_untrusted:{suffix}"]
    if embedded.get("schema_version") != BASE_MODEL_PASSTHROUGH_CERTIFICATE_SCHEMA_VERSION:
        return False, ["base_model_passthrough_certificate_schema_mismatch"]
    actual_sha = canonical_json_sha256({key: value for key, value in embedded.items() if key != "passthrough_sha256"})
    if embedded.get("passthrough_sha256") != actual_sha:
        return False, ["base_model_passthrough_certificate_sha_mismatch"]
    if embedded.get("passthrough_sha256") != expected.get("passthrough_sha256"):
        return False, ["base_model_passthrough_certificate_recomputed_sha_mismatch"]
    return True, ["base_model_passthrough_certificate_verified"]


def canonical_base_model_passthrough_payload(
    *,
    route: dict[str, Any],
    decision: dict[str, Any],
    base_prediction: dict[str, Any],
) -> dict[str, Any]:
    route_certificate = route.get("route_decision_certificate") if isinstance(route.get("route_decision_certificate"), dict) else {}
    return {
        "route_run_dynamic": route.get("run_dynamic"),
        "route_policy": route.get("policy"),
        "route_decision_certificate_sha256": route_certificate.get("certificate_sha256"),
        "base_prediction": {
            "label": coerce_label(base_prediction.get("label")),
            "confidence": coerce_optional_float(base_prediction.get("confidence")),
            "margin": coerce_optional_float(base_prediction.get("margin")),
            "source": base_prediction.get("source"),
        },
        "final_label": coerce_label(decision.get("pred_label")),
        "recommended_next_step": decision.get("recommended_next_step"),
    }


def validate_base_model_passthrough_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("route_run_dynamic") is not False:
        errors.append("base passthrough requires route_run_dynamic=false")
    route_sha = str(payload.get("route_decision_certificate_sha256") or "")
    if len(route_sha) != 64 or any(char not in "0123456789abcdef" for char in route_sha.lower()):
        errors.append("base passthrough requires a route decision certificate sha")
    base = payload.get("base_prediction") if isinstance(payload.get("base_prediction"), dict) else {}
    base_label = coerce_label(base.get("label"))
    final_label = coerce_label(payload.get("final_label"))
    if base_label not in (0, 1):
        errors.append("base passthrough requires a binary base label")
    if final_label not in (0, 1):
        errors.append("base passthrough requires a binary final label")
    if base_label in (0, 1) and final_label in (0, 1) and base_label != final_label:
        errors.append("base passthrough final label differs from base label")
    if payload.get("recommended_next_step") != "accept_base_model_prediction":
        errors.append("base passthrough final decision must recommend accepting the base prediction")
    return errors


def apply_base_model_passthrough(card: dict[str, Any], route: DynamicRouteDecision) -> dict[str, Any]:
    if route.base_prediction is None or route.base_prediction.label not in (0, 1):
        return attach_dynamic_route(card, route)
    updated = attach_dynamic_route(card, route)
    label = int(route.base_prediction.label)
    verdict = "likely_clone" if label == 1 else "likely_non_clone"
    confidence = route.base_prediction.confidence
    if confidence is None:
        confidence = 0.5 + 0.5 * clamp01(route.base_prediction.margin) if route.base_prediction.margin is not None else 0.5
    decision = dict(updated.get("decision") or {})
    risk_flags = list(decision.get("risk_flags") or [])
    if "dynamic_router_base_model_passthrough" not in risk_flags:
        risk_flags.append("dynamic_router_base_model_passthrough")
    legacy_source = str(route.base_prediction.source or "").lower()
    if legacy_source in {"codebert", "graphcodebert"} and "dynamic_router_codebert_passthrough" not in risk_flags:
        risk_flags.append("dynamic_router_codebert_passthrough")
    base_source = str(route.base_prediction.source or DEFAULT_BASE_MODEL_SOURCE)
    decision.update(
        {
            "verdict": verdict,
            "pred_label": VERDICT_TO_LABEL[verdict],
            "confidence": round(clamp01(confidence), 4),
            "rationale": append_reason(
                str(decision.get("rationale") or ""),
                f"Dynamic router estimated low executable-evidence utility; final output keeps the base {base_source} prediction.",
            ),
            "risk_flags": risk_flags,
            "recommended_next_step": "accept_base_model_prediction",
        }
    )
    updated["decision"] = decision
    updated["base_model_prediction"] = route.base_prediction.to_dict()
    updated["base_model_passthrough"] = build_base_model_passthrough_certificate(
        route=updated["dynamic_route"],
        decision=decision,
        base_prediction=updated["base_model_prediction"],
    )
    return updated


def apply_codebert_passthrough(card: dict[str, Any], route: DynamicRouteDecision) -> dict[str, Any]:
    """Backward-compatible name for historical CodeBERT/GraphCodeBERT experiments."""
    return apply_base_model_passthrough(card, route)


def attach_dynamic_route(card: dict[str, Any], route: DynamicRouteDecision) -> dict[str, Any]:
    updated = dict(card)
    updated["dynamic_route"] = route.to_dict()
    return updated


def route_tier(score: float, threshold: float) -> str:
    if score >= threshold + 0.20:
        return "high_expected_dynamic_value"
    if score >= threshold:
        return "route_to_dynamic"
    if score <= max(0.0, threshold - 0.25):
        return "base_model_region"
    return "borderline_base_model_region"


def load_base_predictions(path: Path, *, source: str = DEFAULT_BASE_MODEL_SOURCE) -> dict[PairKey, BaseModelPrediction]:
    result: dict[PairKey, BaseModelPrediction] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) < 3:
                raise ValueError(f"expected at least 3 columns at {path}:{line_no}, got {len(parts)}")
            label = coerce_label(parts[2])
            confidence = coerce_optional_float(parts[3]) if len(parts) >= 4 else None
            margin = coerce_optional_float(parts[4]) if len(parts) >= 5 else None
            result[pair_key(parts[0], parts[1])] = BaseModelPrediction(
                label=label,
                confidence=confidence,
                margin=margin,
                source=source,
            )
    return result


def load_learned_dynamic_route_model(path: Path) -> LearnedDynamicRouteModel:
    import json

    obj = json.loads(path.read_text(encoding="utf-8"))
    ok, reasons = verify_learned_route_model_artifact(obj)
    if not ok:
        reason = reasons[0] if reasons else "learned_route_model_artifact_untrusted"
        raise ValueError(f"learned dynamic route model artifact failed certificate verification: {reason}")
    return LearnedDynamicRouteModel.from_dict(obj)


def base_prediction_for_pair(pair: ClonePair, mapping: dict[PairKey, BaseModelPrediction] | None = None) -> BaseModelPrediction | None:
    if mapping:
        mapped = mapping.get(pair_key(pair.function_id_a, pair.function_id_b))
        if mapped is not None:
            return mapped
    raw = pair.raw or {}
    for key in [
        "dsfm_prediction",
        "dsfm_label",
        "dsfm_pred",
        "base_prediction",
        "prediction",
        "graphcodebert_prediction",
        "codebert_prediction",
    ]:
        if key in raw:
            label = coerce_label(raw.get(key))
            if label in (0, 1):
                source = str(raw.get("base_model") or raw.get("model") or DEFAULT_BASE_MODEL_SOURCE)
                return BaseModelPrediction(
                    label=label,
                    confidence=coerce_optional_float(
                        first_present(raw, ["dsfm_confidence", "base_confidence", "graphcodebert_confidence", "codebert_confidence"])
                    ),
                    margin=coerce_optional_float(
                        first_present(raw, ["dsfm_margin", "base_margin", "graphcodebert_margin", "codebert_margin"])
                    ),
                    source=source,
                )
    return None


def first_present(mapping: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return None


def has_truncation_marker(text: str) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in TRUNCATION_MARKERS)


def coerce_label(value: Any) -> int | None:
    if value in (0, 1):
        return int(value)
    text = str(value).strip()
    if text in {"0", "1"}:
        return int(text)
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    if math.isclose(number, 0.0):
        return 0
    if math.isclose(number, 1.0):
        return 1
    return None


def coerce_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp01(value: Any) -> float:
    return max(0.0, min(1.0, safe_float(value, 0.0)))


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def ratio(num: int | float, den: int | float) -> float:
    return round(float(num) / float(den), 6) if den else 0.0
