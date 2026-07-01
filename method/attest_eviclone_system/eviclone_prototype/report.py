from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context_completion import CONTEXT_EXPERT_CONTRACT, CONTEXT_OUTPUT_KIND
from .dynamic_router import (
    ROUTE_FAILURE_BOUNDARY_AXES,
    ROUTE_TRAINING_TARGET,
    route_failure_boundary,
    verify_base_model_passthrough_certificate,
    verify_learned_route_model_certificate,
    verify_learned_route_score_certificate,
    verify_route_decision_certificate,
)
from .evidence import metrics
from .executor import (
    PROBE_ADEQUACY_HASH_FIELD,
    SOURCE_ARTIFACT_SCHEMA_VERSION,
    SOURCE_ARTIFACT_HASH_FIELD,
    build_probe_adequacy_certificate,
    build_probe_adequacy_certificate_hash,
    build_runtime_fixture_hash,
    build_source_artifact_hash,
    RUNTIME_FIXTURE_HASH_FIELD,
    RUNTIME_FIXTURE_SPECS,
)
from .executable_fusion import (
    verify_context_added_context_artifact,
    verify_context_probe_execution_path_artifact,
    verify_context_source_safety_artifact,
    verify_executed_source_matches_artifact,
    verify_context_payload_schema_certificate,
    verify_llm_expert_invocation_output,
    verify_llm_input_firewall,
    verify_llm_model_config,
    verify_probe_payload_schema_certificate,
    verify_probe_source_binding_artifact,
    verify_source_artifact,
)
from .pipeline_trace import (
    COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION,
    FINAL_DECISION_BINDING_SCHEMA_VERSION,
    build_final_decision_binding,
    canonical_sha256,
)
from .probe_synthesis import PROBE_EXPERT_CONTRACT, PROBE_OUTPUT_KIND


def load_cards(path: Path) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                cards.append(json.loads(line))
    return cards


def summarize_cards(cards: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = Counter(card.get("decision", {}).get("verdict", "unknown") for card in cards)
    targets = Counter(card.get("target", {}).get("name") or "unknown" for card in cards)
    dynamic_status = Counter(
        dynamic_status_of(card)
        for card in cards
    )
    llm_status = Counter(
        "success" if card.get("llm_evidence") and card.get("llm_evidence", {}).get("status") != "failed"
        else ("failed" if card.get("llm_evidence") else "not_run")
        for card in cards
    )
    llm_errors = Counter(llm_error_bucket(card) for card in cards if llm_error_bucket(card))
    llm_success = llm_status.get("success", 0)
    llm_failed = llm_status.get("failed", 0)
    dynamic_route_accounting = summarize_dynamic_route_accounting(cards)
    architecture_accounting = summarize_architecture_contract_accounting(cards)
    llm_expert_accounting = summarize_llm_expert_contract_accounting(cards)
    runtime_fixture_accounting = summarize_runtime_fixture_accounting(cards)
    fusion_accounting = summarize_fusion_decision_accounting(cards)
    executable_integrity_accounting = summarize_executable_evidence_integrity_accounting(cards)
    return {
        "schema_version": "eviclone-run-summary/v1",
        "status": "completed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_cards": len(cards),
        "metrics_against_bcb_gold": metrics(cards),
        "verdict_counts": dict(verdicts.most_common()),
        "target_counts": dict(targets.most_common()),
        "dynamic_status_counts": dict(dynamic_status.most_common()),
        "llm_status_counts": dict(llm_status.most_common()),
        "llm_health": {
            "success": llm_success,
            "failed": llm_failed,
            "not_run": llm_status.get("not_run", 0),
            "success_rate": round(llm_success / len(cards), 6) if cards else 0.0,
            "failure_rate": round(llm_failed / len(cards), 6) if cards else 0.0,
        },
        "llm_error_counts": dict(llm_errors.most_common(20)),
        "dynamic_route_accounting": dynamic_route_accounting,
        "architecture_contract_accounting": architecture_accounting,
        "llm_expert_contract_accounting": llm_expert_accounting,
        "runtime_fixture_accounting": runtime_fixture_accounting,
        "fusion_decision_accounting": fusion_accounting,
        "executable_evidence_integrity_accounting": executable_integrity_accounting,
    }


def write_report(cards: list[dict[str, Any]], path: Path, *, title: str = "EviClone Run Report") -> dict[str, Any]:
    summary = summarize_cards(cards)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Sample Cards",
        "",
    ]
    for card in cards[:10]:
        decision = card.get("decision", {})
        lines.extend(
            [
                f"### Pair {card.get('pair_id')}",
                "",
                f"- Target: {card.get('target', {}).get('name')}",
                f"- Gold: {card.get('gold', {}).get('label')} ({card.get('gold', {}).get('source')})",
                f"- Verdict: {decision.get('verdict')} / pred={decision.get('pred_label')} / confidence={decision.get('confidence')}",
                f"- Dynamic: {dynamic_status_of(card)}",
                f"- Rationale: {decision.get('rationale', '')}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return summary


def dynamic_status_of(card: dict[str, Any]) -> str:
    dynamic = card.get("dynamic_evidence")
    if not isinstance(dynamic, dict):
        return "not_run"
    return str(dynamic.get("status") or "not_run")


def summarize_dynamic_route_accounting(cards: list[dict[str, Any]]) -> dict[str, Any]:
    policies: Counter[str] = Counter()
    tiers: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    failure_boundary_primary_axes: Counter[str] = Counter()
    failure_boundary_axes: Counter[str] = Counter()
    failure_boundary_axis_totals: dict[str, Counter[str]] = {
        axis: Counter() for axis in ROUTE_FAILURE_BOUNDARY_AXES
    }
    certificate_reasons: Counter[str] = Counter()
    totals = Counter()
    for card in cards:
        route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
        if not route:
            continue
        totals["route_cards"] += 1
        policies[str(route.get("policy") or "missing")] += 1
        tiers[str(route.get("tier") or "missing")] += 1
        route_reasons = route.get("reasons") if isinstance(route.get("reasons"), list) else []
        for reason in route_reasons:
            reasons[str(reason)] += 1
        failure_boundary = (
            route.get("failure_boundary")
            if isinstance(route.get("failure_boundary"), dict)
            else route_failure_boundary(
                route.get("features") if isinstance(route.get("features"), dict) else {},
                [str(reason) for reason in route_reasons],
            )
        )
        primary_axis = str(failure_boundary.get("primary_axis") or "unknown")
        if primary_axis not in failure_boundary_axis_totals:
            failure_boundary_axis_totals[primary_axis] = Counter()
        failure_boundary_primary_axes[primary_axis] += 1
        for axis in failure_boundary.get("axes") or []:
            failure_boundary_axes[str(axis)] += 1

        if route.get("policy") == "learned_expected_dynamic_evidence_utility/v1" or isinstance(
            route.get("route_model_certificate"), dict
        ):
            totals["learned_route_cards"] += 1
            model_certificate = (
                route.get("route_model_certificate")
                if isinstance(route.get("route_model_certificate"), dict)
                else {}
            )
            score_certificate = (
                route.get("route_score_certificate")
                if isinstance(route.get("route_score_certificate"), dict)
                else {}
            )
            if not model_certificate:
                totals["missing_learned_route_model_certificate"] += 1
            else:
                model_ok, model_reasons = verify_learned_route_model_certificate(model_certificate)
                if model_ok:
                    totals["verified_learned_route_model_certificate"] += 1
                else:
                    totals["unverified_learned_route_model_certificate"] += 1
                for reason in model_reasons:
                    certificate_reasons[f"learned_model:{reason}"] += 1
            if not score_certificate:
                totals["missing_learned_route_score_certificate"] += 1
            else:
                score_ok, score_reasons = verify_learned_route_score_certificate(route)
                if score_ok:
                    totals["verified_learned_route_score_certificate"] += 1
                else:
                    totals["unverified_learned_route_score_certificate"] += 1
                for reason in score_reasons:
                    certificate_reasons[f"learned_score:{reason}"] += 1
        else:
            totals["heuristic_route_cards"] += 1

        certificate = route.get("route_decision_certificate") if isinstance(route.get("route_decision_certificate"), dict) else {}
        if not certificate:
            totals["missing_route_decision_certificate"] += 1
        else:
            ok, verify_reasons = verify_route_decision_certificate(route)
            if ok:
                totals["verified_route_decision_certificate"] += 1
            else:
                totals["unverified_route_decision_certificate"] += 1
            for reason in verify_reasons:
                certificate_reasons[str(reason)] += 1

        run_dynamic = route.get("run_dynamic")
        if run_dynamic is True:
            totals["route_to_dynamic"] += 1
            failure_boundary_axis_totals[primary_axis]["route_to_dynamic"] += 1
        elif run_dynamic is False:
            totals["pass_through"] += 1
            failure_boundary_axis_totals[primary_axis]["pass_through"] += 1
            passthrough = card.get("base_model_passthrough") if isinstance(card.get("base_model_passthrough"), dict) else {}
            if not passthrough:
                totals["missing_base_model_passthrough_certificate"] += 1
                certificate_reasons["base_passthrough:missing"] += 1
            else:
                passthrough_ok, passthrough_reasons = verify_base_model_passthrough_certificate(card)
                if passthrough_ok:
                    totals["verified_base_model_passthrough_certificate"] += 1
                else:
                    totals["unverified_base_model_passthrough_certificate"] += 1
                for reason in passthrough_reasons:
                    certificate_reasons[f"base_passthrough:{reason}"] += 1
        else:
            totals["invalid_route_decision"] += 1
            continue

        base_label = base_prediction_label_of(card)
        gold_label = binary_label(card.get("gold", {}).get("label") if isinstance(card.get("gold"), dict) else None)
        if base_label not in (0, 1) or gold_label not in (0, 1):
            totals["missing_base_or_gold_for_route_eval"] += 1
            continue

        totals["base_prediction_cards"] += 1
        base_wrong = base_label != gold_label
        failure_boundary_axis_totals[primary_axis]["base_prediction_cards"] += 1
        failure_boundary_axis_totals[primary_axis]["base_error_count"] += int(base_wrong)
        failure_boundary_axis_totals[primary_axis]["base_correct_count"] += int(not base_wrong)
        totals["base_error_count"] += int(base_wrong)
        totals["base_correct_count"] += int(not base_wrong)
        if run_dynamic and base_wrong:
            totals["routed_base_errors"] += 1
            failure_boundary_axis_totals[primary_axis]["routed_base_errors"] += 1
        elif run_dynamic and not base_wrong:
            totals["unnecessary_dynamic"] += 1
            failure_boundary_axis_totals[primary_axis]["unnecessary_dynamic"] += 1
        elif not run_dynamic and base_wrong:
            totals["missed_base_errors"] += 1
            failure_boundary_axis_totals[primary_axis]["missed_base_errors"] += 1
        elif not run_dynamic and not base_wrong:
            totals["pass_through_correct"] += 1
            failure_boundary_axis_totals[primary_axis]["pass_through_correct"] += 1

    route_cards = totals["route_cards"]
    route_to_dynamic = totals["route_to_dynamic"]
    pass_through = totals["pass_through"]
    base_eval_cards = totals["base_prediction_cards"]
    labeled_route_to_dynamic = totals["routed_base_errors"] + totals["unnecessary_dynamic"]
    labeled_pass_through = totals["missed_base_errors"] + totals["pass_through_correct"]
    return {
        "system_role": "selective_dynamic_evidence_router",
        "training_target": ROUTE_TRAINING_TARGET,
        "allowed_output": "run_dynamic_only",
        "base_passthrough_semantics": "cards not routed to dynamic execution keep the base model prediction",
        "route_cards": route_cards,
        "route_to_dynamic": route_to_dynamic,
        "pass_through": pass_through,
        "invalid_route_decision": totals["invalid_route_decision"],
        "learned_route_cards": totals["learned_route_cards"],
        "heuristic_route_cards": totals["heuristic_route_cards"],
        "verified_learned_route_model_certificate": totals["verified_learned_route_model_certificate"],
        "missing_learned_route_model_certificate": totals["missing_learned_route_model_certificate"],
        "unverified_learned_route_model_certificate": totals["unverified_learned_route_model_certificate"],
        "verified_learned_route_score_certificate": totals["verified_learned_route_score_certificate"],
        "missing_learned_route_score_certificate": totals["missing_learned_route_score_certificate"],
        "unverified_learned_route_score_certificate": totals["unverified_learned_route_score_certificate"],
        "missing_route_decision_certificate": totals["missing_route_decision_certificate"],
        "verified_route_decision_certificate": totals["verified_route_decision_certificate"],
        "unverified_route_decision_certificate": totals["unverified_route_decision_certificate"],
        "verified_base_model_passthrough_certificate": totals["verified_base_model_passthrough_certificate"],
        "missing_base_model_passthrough_certificate": totals["missing_base_model_passthrough_certificate"],
        "unverified_base_model_passthrough_certificate": totals["unverified_base_model_passthrough_certificate"],
        "base_prediction_cards": base_eval_cards,
        "missing_base_or_gold_for_route_eval": totals["missing_base_or_gold_for_route_eval"],
        "base_error_count": totals["base_error_count"],
        "base_correct_count": totals["base_correct_count"],
        "routed_base_errors": totals["routed_base_errors"],
        "unnecessary_dynamic": totals["unnecessary_dynamic"],
        "missed_base_errors": totals["missed_base_errors"],
        "pass_through_correct": totals["pass_through_correct"],
        "route_rate": ratio(route_to_dynamic, route_cards),
        "execution_reduction": ratio(pass_through, route_cards),
        "route_precision": ratio(totals["routed_base_errors"], labeled_route_to_dynamic),
        "base_error_recall": ratio(totals["routed_base_errors"], totals["base_error_count"]),
        "pass_through_safety": ratio(totals["pass_through_correct"], labeled_pass_through),
        "oracle_dynamic_budget_accuracy_upper_bound": ratio(
            totals["base_correct_count"] + totals["routed_base_errors"],
            base_eval_cards,
        ),
        "policy_counts": dict(policies.most_common()),
        "tier_counts": dict(tiers.most_common()),
        "route_reason_counts": dict(reasons.most_common(20)),
        "failure_boundary_role": "static_model_failure_boundary_modeling",
        "failure_boundary_primary_axis_counts": dict(failure_boundary_primary_axes.most_common()),
        "failure_boundary_axis_counts": dict(failure_boundary_axes.most_common()),
        "failure_boundary_metrics_by_primary_axis": failure_boundary_metrics_by_axis(failure_boundary_axis_totals),
        "certificate_reason_counts": dict(certificate_reasons.most_common(20)),
    }


def failure_boundary_metrics_by_axis(axis_totals: dict[str, Counter[str]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for axis, counts in axis_totals.items():
        total = counts["route_to_dynamic"] + counts["pass_through"]
        labeled_route_to_dynamic = counts["routed_base_errors"] + counts["unnecessary_dynamic"]
        labeled_pass_through = counts["missed_base_errors"] + counts["pass_through_correct"]
        if not total and not counts["base_prediction_cards"]:
            continue
        result[axis] = {
            "route_cards": total,
            "base_prediction_cards": counts["base_prediction_cards"],
            "route_to_dynamic": counts["route_to_dynamic"],
            "pass_through": counts["pass_through"],
            "base_error_count": counts["base_error_count"],
            "base_correct_count": counts["base_correct_count"],
            "routed_base_errors": counts["routed_base_errors"],
            "unnecessary_dynamic": counts["unnecessary_dynamic"],
            "missed_base_errors": counts["missed_base_errors"],
            "pass_through_correct": counts["pass_through_correct"],
            "route_rate": ratio(counts["route_to_dynamic"], total),
            "route_precision": ratio(counts["routed_base_errors"], labeled_route_to_dynamic),
            "base_error_recall": ratio(counts["routed_base_errors"], counts["base_error_count"]),
            "pass_through_safety": ratio(counts["pass_through_correct"], labeled_pass_through),
        }
    return result


def base_prediction_label_of(card: dict[str, Any]) -> int | None:
    base = card.get("base_model_prediction") if isinstance(card.get("base_model_prediction"), dict) else {}
    label = binary_label(base.get("label") if base else None)
    if label in (0, 1):
        return label
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    route_base = route.get("base_prediction") if isinstance(route.get("base_prediction"), dict) else {}
    label = binary_label(route_base.get("label") if route_base else None)
    if label in (0, 1):
        return label
    passthrough = card.get("base_model_passthrough") if isinstance(card.get("base_model_passthrough"), dict) else {}
    passthrough_base = passthrough.get("base_prediction") if isinstance(passthrough.get("base_prediction"), dict) else {}
    return binary_label(passthrough_base.get("label") if passthrough_base else None)


def binary_label(value: Any) -> int | None:
    if value in (0, 1):
        return int(value)
    if isinstance(value, str) and value.strip() in {"0", "1"}:
        return int(value.strip())
    return None


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def summarize_architecture_contract_accounting(cards: list[dict[str, Any]]) -> dict[str, Any]:
    policies: Counter[str] = Counter()
    decision_authorities: Counter[str] = Counter()
    final_component_sets: Counter[str] = Counter()
    deployable_final_source_sets: Counter[str] = Counter()
    final_permission_components: Counter[str] = Counter()
    bounded_expert_components: Counter[str] = Counter()
    component_roles: Counter[str] = Counter()
    totals = Counter()

    for card in cards:
        route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
        if route:
            totals["routed_cards"] += 1
        contract = card.get("pipeline_contract") if isinstance(card.get("pipeline_contract"), dict) else {}
        if not contract:
            if route:
                totals["missing_pipeline_contract"] += 1
            continue
        totals["pipeline_contract_cards"] += 1
        card_clean = True
        if contract.get("programmatic_fusion_required") is True:
            totals["programmatic_fusion_required_cards"] += 1
        if contract.get("llm_final_decision_allowed") is not False and route:
            totals["pipeline_contract_llm_final_decision_allowed_violations"] += 1
        deployable_sources = [
            str(item)
            for item in contract.get("deployable_final_sources") or []
        ]
        if route:
            deployable_final_source_sets["|".join(deployable_sources) if deployable_sources else "none"] += 1
            if "no_reliable_final_label" in deployable_sources:
                card_clean = False
                totals["deployable_final_sources_include_no_reliable_label"] += 1
        binding = (
            contract.get("final_decision_binding")
            if isinstance(contract.get("final_decision_binding"), dict)
            else {}
        )
        if route:
            if not binding:
                card_clean = False
                totals["missing_final_decision_binding"] += 1
            else:
                totals["final_decision_binding_present"] += 1
                binding_clean = True
                if binding.get("schema_version") == FINAL_DECISION_BINDING_SCHEMA_VERSION:
                    totals["final_decision_binding_schema_valid"] += 1
                else:
                    binding_clean = False
                    totals["final_decision_binding_schema_invalid"] += 1
                expected_binding_sha = canonical_sha256(
                    {key: value for key, value in binding.items() if key != "binding_sha256"}
                )
                if binding.get("binding_sha256") == expected_binding_sha:
                    totals["final_decision_binding_self_hash_verified"] += 1
                else:
                    binding_clean = False
                    totals["final_decision_binding_self_hash_unverified"] += 1
                if binding == build_final_decision_binding(card):
                    totals["final_decision_binding_recomputed_verified"] += 1
                else:
                    binding_clean = False
                    totals["final_decision_binding_recomputed_mismatch"] += 1
                if binding_clean:
                    totals["final_decision_binding_verified"] += 1
                else:
                    card_clean = False

        interaction = (
            contract.get("component_interaction_contract")
            if isinstance(contract.get("component_interaction_contract"), dict)
            else {}
        )
        if not interaction:
            if route:
                totals["missing_component_interaction_contract"] += 1
            continue
        totals["component_interaction_contract_cards"] += 1
        policies[str(interaction.get("policy") or "missing")] += 1
        decision_authorities[str(interaction.get("decision_authority") or "missing")] += 1

        if interaction.get("schema_version") == COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION:
            totals["component_interaction_schema_valid"] += 1
        else:
            card_clean = False
            totals["component_interaction_schema_invalid"] += 1

        expected_sha = canonical_sha256(
            {key: value for key, value in interaction.items() if key != "interaction_contract_sha256"}
        )
        if interaction.get("interaction_contract_sha256") == expected_sha:
            totals["component_interaction_self_hash_verified"] += 1
        else:
            card_clean = False
            totals["component_interaction_self_hash_unverified"] += 1

        if route and interaction.get("llm_clone_label_output_allowed") is not False:
            card_clean = False
            totals["llm_clone_label_output_allowed_violations"] += 1
        if route and interaction.get("llm_final_decision_output_allowed") is not False:
            card_clean = False
            totals["llm_final_decision_output_allowed_violations"] += 1

        final_components = [
            str(item)
            for item in interaction.get("final_decision_components") or []
        ]
        final_component_sets["|".join(final_components) if final_components else "none"] += 1
        expected_final_components = ["base_model_passthrough"] if route.get("run_dynamic") is False else ["executable_fusion"] if route else []
        if route and final_components == expected_final_components:
            totals["final_decision_components_match_route"] += 1
        elif route:
            card_clean = False
            totals["final_decision_components_mismatch_route"] += 1

        bounded_components = [
            str(item)
            for item in interaction.get("bounded_expert_components") or []
        ]
        expected_bounded_components = [] if route.get("run_dynamic") is False else [
            "llm_context_completion",
            "llm_probe_synthesis",
        ] if route else []
        if route and bounded_components == expected_bounded_components:
            totals["bounded_expert_components_match_route"] += 1
        elif route:
            card_clean = False
            totals["bounded_expert_components_mismatch_route"] += 1
        allowed_bounded = set(expected_bounded_components)

        for component in interaction.get("components") or []:
            if not isinstance(component, dict):
                card_clean = False
                totals["malformed_component_permission"] += 1
                continue
            name = str(component.get("component") or "missing")
            role = str(component.get("role") or "missing")
            component_roles[f"{name}:{role}"] += 1
            if component.get("may_emit_final_decision") is True:
                final_permission_components[name] += 1
            if component.get("may_emit_bounded_expert_artifact") is True:
                bounded_expert_components[name] += 1
            if name.startswith("llm_") and component.get("may_emit_final_decision") is not False:
                card_clean = False
                totals["llm_component_final_decision_permission_violations"] += 1
            if name.startswith("llm_") and component.get("may_emit_bounded_expert_artifact") is True:
                totals["llm_bounded_expert_artifact_components"] += 1
            if route and component.get("may_emit_bounded_expert_artifact") is True and name not in allowed_bounded:
                card_clean = False
                totals["unauthorized_bounded_expert_artifact_permission_violations"] += 1
        if card_clean:
            totals["clean_component_interaction_contract_cards"] += 1

    interaction_cards = totals["component_interaction_contract_cards"]
    clean_cards = totals["clean_component_interaction_contract_cards"]
    return {
        "system_role": "programmatic_component_interaction_contract",
        "contract_schema_version": COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION,
        "routed_cards": totals["routed_cards"],
        "pipeline_contract_cards": totals["pipeline_contract_cards"],
        "missing_pipeline_contract": totals["missing_pipeline_contract"],
        "component_interaction_contract_cards": interaction_cards,
        "missing_component_interaction_contract": totals["missing_component_interaction_contract"],
        "component_interaction_schema_valid": totals["component_interaction_schema_valid"],
        "component_interaction_schema_invalid": totals["component_interaction_schema_invalid"],
        "component_interaction_self_hash_verified": totals["component_interaction_self_hash_verified"],
        "component_interaction_self_hash_unverified": totals["component_interaction_self_hash_unverified"],
        "programmatic_fusion_required_cards": totals["programmatic_fusion_required_cards"],
        "final_decision_binding_present": totals["final_decision_binding_present"],
        "missing_final_decision_binding": totals["missing_final_decision_binding"],
        "final_decision_binding_verified": totals["final_decision_binding_verified"],
        "final_decision_binding_schema_valid": totals["final_decision_binding_schema_valid"],
        "final_decision_binding_schema_invalid": totals["final_decision_binding_schema_invalid"],
        "final_decision_binding_self_hash_verified": totals["final_decision_binding_self_hash_verified"],
        "final_decision_binding_self_hash_unverified": totals["final_decision_binding_self_hash_unverified"],
        "final_decision_binding_recomputed_verified": totals["final_decision_binding_recomputed_verified"],
        "final_decision_binding_recomputed_mismatch": totals["final_decision_binding_recomputed_mismatch"],
        "pipeline_contract_llm_final_decision_allowed_violations": totals[
            "pipeline_contract_llm_final_decision_allowed_violations"
        ],
        "deployable_final_sources_include_no_reliable_label": totals[
            "deployable_final_sources_include_no_reliable_label"
        ],
        "llm_clone_label_output_allowed_violations": totals["llm_clone_label_output_allowed_violations"],
        "llm_final_decision_output_allowed_violations": totals["llm_final_decision_output_allowed_violations"],
        "llm_component_final_decision_permission_violations": totals[
            "llm_component_final_decision_permission_violations"
        ],
        "llm_bounded_expert_artifact_components": totals["llm_bounded_expert_artifact_components"],
        "final_decision_components_match_route": totals["final_decision_components_match_route"],
        "final_decision_components_mismatch_route": totals["final_decision_components_mismatch_route"],
        "bounded_expert_components_match_route": totals["bounded_expert_components_match_route"],
        "bounded_expert_components_mismatch_route": totals["bounded_expert_components_mismatch_route"],
        "unauthorized_bounded_expert_artifact_permission_violations": totals[
            "unauthorized_bounded_expert_artifact_permission_violations"
        ],
        "malformed_component_permission": totals["malformed_component_permission"],
        "clean_component_interaction_contract_cards": clean_cards,
        "clean_component_interaction_contract_rate": ratio(clean_cards, interaction_cards),
        "policy_counts": dict(policies.most_common()),
        "decision_authority_counts": dict(decision_authorities.most_common()),
        "final_decision_component_set_counts": dict(final_component_sets.most_common()),
        "deployable_final_source_set_counts": dict(deployable_final_source_sets.most_common()),
        "final_permission_component_counts": dict(final_permission_components.most_common()),
        "bounded_expert_component_counts": dict(bounded_expert_components.most_common()),
        "component_role_counts": dict(component_roles.most_common(30)),
    }


def summarize_llm_expert_contract_accounting(cards: list[dict[str, Any]]) -> dict[str, Any]:
    components: Counter[str] = Counter()
    expert_statuses: Counter[str] = Counter()
    invocation_roles: Counter[str] = Counter()
    invocation_contracts: Counter[str] = Counter()
    invocation_output_kinds: Counter[str] = Counter()
    schema_component_roles: Counter[str] = Counter()
    schema_output_kinds: Counter[str] = Counter()
    verification_reasons: Counter[str] = Counter()
    totals = Counter()

    for card in cards:
        dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
        if not dynamic:
            continue
        for spec in llm_expert_component_specs(dynamic):
            component = spec["component"]
            expert = spec["expert"]
            if not isinstance(expert, dict) or not expert:
                continue
            payload = expert.get("payload") if isinstance(expert.get("payload"), dict) else {}
            invocation = expert.get("expert_invocation") if isinstance(expert.get("expert_invocation"), dict) else {}
            schema = payload.get(spec["schema_key"]) if isinstance(payload.get(spec["schema_key"]), dict) else {}
            free_text_violation_seen = False

            totals["expert_outputs"] += 1
            components[component] += 1
            expert_statuses[str(expert.get("status") or "missing")] += 1
            if expert.get("status") == "completed":
                totals["completed_expert_outputs"] += 1
            elif expert.get("status") == "rejected":
                totals["rejected_expert_outputs"] += 1
            elif expert.get("status") == "failed":
                totals["failed_expert_outputs"] += 1

            if schema:
                totals["payload_schema_present"] += 1
                schema_component_roles[str(schema.get("component_role") or "missing")] += 1
                schema_output_kinds[str(schema.get("output_kind") or "missing")] += 1
                if schema.get("clone_label_output_allowed") is not False:
                    totals["clone_label_output_allowed_violations"] += 1
                if schema.get("final_decision_allowed") is not False:
                    totals["final_decision_allowed_violations"] += 1
            else:
                totals["payload_schema_missing"] += 1

            schema_ok, schema_reasons = spec["schema_verifier"](payload)
            if schema_ok:
                totals["payload_schema_verified"] += 1
            else:
                totals["payload_schema_unverified"] += 1
            for reason in schema_reasons:
                verification_reasons[f"{component}:{reason}"] += 1
                if "contains forbidden decision token" in str(reason):
                    free_text_violation_seen = True
                    verification_reasons[f"{component}:free_text_decision_language_violation"] += 1

            if invocation:
                totals["expert_invocation_present"] += 1
                invocation_roles[str(invocation.get("expert_role") or "missing")] += 1
                invocation_contracts[str(invocation.get("expert_contract") or "missing")] += 1
                invocation_output_kinds[str(invocation.get("output_kind") or "missing")] += 1
                if invocation.get("validation_passed") is True:
                    totals["expert_invocation_validation_passed"] += 1
                else:
                    totals["expert_invocation_validation_failed"] += 1
                for error in invocation.get("validation_errors") or []:
                    if "contains forbidden decision token" in str(error):
                        free_text_violation_seen = True
                        verification_reasons[f"{component}:free_text_decision_language_violation"] += 1
            else:
                totals["expert_invocation_missing"] += 1

            invocation_ok, invocation_reasons = verify_llm_expert_invocation_output(
                invocation,
                issue_prefix=component,
                expected_role=spec["invocation_role"],
                expected_contract=spec["contract"],
                expected_output_kind=spec["output_kind"],
                expected_output_sha=payload.get(spec["output_sha_key"]),
            )
            if invocation_ok:
                totals["expert_invocation_verified"] += 1
            else:
                totals["expert_invocation_unverified"] += 1
            for reason in invocation_reasons:
                verification_reasons[reason] += 1

            firewall_ok, firewall_reasons = verify_llm_input_firewall(invocation, issue_prefix=component)
            if firewall_ok:
                totals["input_firewall_verified"] += 1
            else:
                totals["input_firewall_unverified"] += 1
            for reason in firewall_reasons:
                verification_reasons[reason] += 1

            model_ok, model_reasons = verify_llm_model_config(invocation, issue_prefix=component)
            if model_ok:
                totals["model_config_verified"] += 1
            else:
                totals["model_config_unverified"] += 1
            for reason in model_reasons:
                verification_reasons[reason] += 1
            if free_text_violation_seen:
                totals["free_text_decision_language_violations"] += 1

    expert_outputs = totals["expert_outputs"]
    return {
        "system_role": "llm_context_and_probe_experts_only",
        "llm_final_decision_allowed": False,
        "allowed_decision_authority": "none",
        "programmatic_fusion_required": True,
        "expert_outputs": expert_outputs,
        "completed_expert_outputs": totals["completed_expert_outputs"],
        "rejected_expert_outputs": totals["rejected_expert_outputs"],
        "failed_expert_outputs": totals["failed_expert_outputs"],
        "payload_schema_present": totals["payload_schema_present"],
        "payload_schema_missing": totals["payload_schema_missing"],
        "payload_schema_verified": totals["payload_schema_verified"],
        "payload_schema_unverified": totals["payload_schema_unverified"],
        "expert_invocation_present": totals["expert_invocation_present"],
        "expert_invocation_missing": totals["expert_invocation_missing"],
        "expert_invocation_verified": totals["expert_invocation_verified"],
        "expert_invocation_unverified": totals["expert_invocation_unverified"],
        "expert_invocation_validation_passed": totals["expert_invocation_validation_passed"],
        "expert_invocation_validation_failed": totals["expert_invocation_validation_failed"],
        "input_firewall_verified": totals["input_firewall_verified"],
        "input_firewall_unverified": totals["input_firewall_unverified"],
        "model_config_verified": totals["model_config_verified"],
        "model_config_unverified": totals["model_config_unverified"],
        "clone_label_output_allowed_violations": totals["clone_label_output_allowed_violations"],
        "final_decision_allowed_violations": totals["final_decision_allowed_violations"],
        "free_text_decision_language_violations": totals["free_text_decision_language_violations"],
        "guarded_expert_output_rate": ratio(
            min(
                totals["payload_schema_verified"],
                totals["expert_invocation_verified"],
                totals["input_firewall_verified"],
            ),
            expert_outputs,
        ),
        "component_counts": dict(components.most_common()),
        "expert_status_counts": dict(expert_statuses.most_common()),
        "invocation_role_counts": dict(invocation_roles.most_common()),
        "invocation_contract_counts": dict(invocation_contracts.most_common()),
        "invocation_output_kind_counts": dict(invocation_output_kinds.most_common()),
        "schema_component_role_counts": dict(schema_component_roles.most_common()),
        "schema_output_kind_counts": dict(schema_output_kinds.most_common()),
        "verification_reason_counts": dict(verification_reasons.most_common(30)),
    }


def llm_expert_component_specs(dynamic: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "component": "context_completion",
            "expert": dynamic.get("llm_context_completion") if isinstance(dynamic.get("llm_context_completion"), dict) else {},
            "schema_key": "context_payload_schema",
            "schema_verifier": verify_context_payload_schema_certificate,
            "invocation_role": "context_completion",
            "contract": CONTEXT_EXPERT_CONTRACT,
            "output_kind": CONTEXT_OUTPUT_KIND,
            "output_sha_key": "java_source_sha256",
        },
        {
            "component": "probe_synthesis",
            "expert": dynamic.get("llm_probe_synthesis") if isinstance(dynamic.get("llm_probe_synthesis"), dict) else {},
            "schema_key": "probe_payload_schema",
            "schema_verifier": verify_probe_payload_schema_certificate,
            "invocation_role": "probe_synthesis",
            "contract": PROBE_EXPERT_CONTRACT,
            "output_kind": PROBE_OUTPUT_KIND,
            "output_sha_key": "probe_body_sha256",
        },
    ]


def summarize_runtime_fixture_accounting(cards: list[dict[str, Any]]) -> dict[str, Any]:
    fixture_counts: Counter[str] = Counter()
    fixture_family_counts: Counter[str] = Counter()
    framework_contract_counts: Counter[str] = Counter()
    verification_reasons: Counter[str] = Counter()
    totals = Counter()

    for card in cards:
        dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
        if not dynamic:
            continue
        totals["dynamic_cards"] += 1
        certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
        if certificate:
            totals["java_execution_certificate_cards"] += 1
        certificate_fixtures = (
            certificate.get("runtime_fixtures")
            if isinstance(certificate.get("runtime_fixtures"), dict)
            else {}
        )
        sandbox = (
            certificate.get("execution_sandbox")
            if isinstance(certificate.get("execution_sandbox"), dict)
            else {}
        )
        meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
        mock_ids = {str(item) for item in meta.get("framework_mocks") or [] if str(item)}
        contracts = {
            str(item.get("mock_id") or ""): item
            for item in meta.get("framework_mock_contracts") or []
            if isinstance(item, dict)
        }
        card_uses_fixture = False
        card_clean = True

        for fixture_id, spec in RUNTIME_FIXTURE_SPECS.items():
            top_fixture = dynamic.get(fixture_id) if isinstance(dynamic.get(fixture_id), dict) else {}
            certificate_fixture = (
                certificate_fixtures.get(fixture_id)
                if isinstance(certificate_fixtures.get(fixture_id), dict)
                else {}
            )
            sandbox_fixture = sandbox.get(fixture_id) if isinstance(sandbox.get(fixture_id), dict) else {}
            fixture_used = bool(top_fixture or certificate_fixture or sandbox_fixture or fixture_id in mock_ids)
            if not fixture_used:
                continue

            card_uses_fixture = True
            totals["fixture_bindings"] += 1
            fixture_counts[fixture_id] += 1
            fixture_family_counts[str(spec.get("family") or "unknown")] += 1
            contract = contracts.get(fixture_id) if isinstance(contracts.get(fixture_id), dict) else {}
            if contract:
                totals["framework_contract_bound"] += 1
                framework_contract_counts[str(contract.get("family") or "unknown")] += 1
            else:
                card_clean = False
                totals["framework_contract_missing"] += 1
                verification_reasons[f"{fixture_id}:framework_contract_missing"] += 1

            for label, fixture in [
                ("top_level", top_fixture),
                ("certificate", certificate_fixture),
                ("sandbox", sandbox_fixture),
            ]:
                if fixture:
                    totals[f"{label}_manifest_present"] += 1
                else:
                    card_clean = False
                    totals[f"{label}_manifest_missing"] += 1
                    verification_reasons[f"{fixture_id}:{label}_manifest_missing"] += 1

            reference_fixture = top_fixture or certificate_fixture or sandbox_fixture
            if reference_fixture.get("schema_version") == spec.get("schema_version"):
                totals["fixture_schema_verified"] += 1
            else:
                card_clean = False
                totals["fixture_schema_unverified"] += 1
                verification_reasons[f"{fixture_id}:schema_mismatch"] += 1

            fixture_hash = reference_fixture.get(RUNTIME_FIXTURE_HASH_FIELD)
            if fixture_hash and fixture_hash == build_runtime_fixture_hash(reference_fixture):
                totals["fixture_hash_verified"] += 1
            elif fixture_hash:
                card_clean = False
                totals["fixture_hash_mismatch"] += 1
                verification_reasons[f"{fixture_id}:sha_mismatch"] += 1
            else:
                card_clean = False
                totals["fixture_hash_missing"] += 1
                verification_reasons[f"{fixture_id}:sha_missing"] += 1

            if reference_fixture.get("deterministic") is True:
                totals["deterministic_fixture_manifests"] += 1
            else:
                card_clean = False
                totals["nondeterministic_fixture_manifests"] += 1
                verification_reasons[f"{fixture_id}:not_deterministic"] += 1
            if reference_fixture.get("no_external_services") is True:
                totals["no_external_service_fixture_manifests"] += 1
            else:
                card_clean = False
                totals["external_service_fixture_manifests"] += 1
                verification_reasons[f"{fixture_id}:external_services_allowed"] += 1

            if top_fixture and certificate_fixture and top_fixture == certificate_fixture:
                totals["top_level_certificate_match"] += 1
            elif top_fixture and certificate_fixture:
                card_clean = False
                totals["top_level_certificate_mismatch"] += 1
                verification_reasons[f"{fixture_id}:certificate_mismatch"] += 1

            if certificate_fixture and sandbox_fixture and certificate_fixture == sandbox_fixture:
                totals["certificate_sandbox_match"] += 1
            elif certificate_fixture and sandbox_fixture:
                card_clean = False
                totals["certificate_sandbox_mismatch"] += 1
                verification_reasons[f"{fixture_id}:sandbox_mismatch"] += 1

        if card_uses_fixture:
            totals["cards_with_runtime_fixtures"] += 1
            if card_clean:
                totals["clean_runtime_fixture_cards"] += 1

    fixture_bindings = totals["fixture_bindings"]
    cards_with_fixtures = totals["cards_with_runtime_fixtures"]
    return {
        "system_role": "programmatic_runtime_context_fixture_accounting",
        "purpose": "audit deterministic environment and framework context completion used by executable evidence",
        "dynamic_cards": totals["dynamic_cards"],
        "java_execution_certificate_cards": totals["java_execution_certificate_cards"],
        "cards_with_runtime_fixtures": cards_with_fixtures,
        "fixture_bindings": fixture_bindings,
        "clean_runtime_fixture_cards": totals["clean_runtime_fixture_cards"],
        "clean_runtime_fixture_card_rate": ratio(totals["clean_runtime_fixture_cards"], cards_with_fixtures),
        "top_level_manifest_present": totals["top_level_manifest_present"],
        "top_level_manifest_missing": totals["top_level_manifest_missing"],
        "certificate_manifest_present": totals["certificate_manifest_present"],
        "certificate_manifest_missing": totals["certificate_manifest_missing"],
        "sandbox_manifest_present": totals["sandbox_manifest_present"],
        "sandbox_manifest_missing": totals["sandbox_manifest_missing"],
        "framework_contract_bound": totals["framework_contract_bound"],
        "framework_contract_missing": totals["framework_contract_missing"],
        "fixture_schema_verified": totals["fixture_schema_verified"],
        "fixture_schema_unverified": totals["fixture_schema_unverified"],
        "fixture_hash_verified": totals["fixture_hash_verified"],
        "fixture_hash_missing": totals["fixture_hash_missing"],
        "fixture_hash_mismatch": totals["fixture_hash_mismatch"],
        "deterministic_fixture_manifests": totals["deterministic_fixture_manifests"],
        "nondeterministic_fixture_manifests": totals["nondeterministic_fixture_manifests"],
        "no_external_service_fixture_manifests": totals["no_external_service_fixture_manifests"],
        "external_service_fixture_manifests": totals["external_service_fixture_manifests"],
        "top_level_certificate_match": totals["top_level_certificate_match"],
        "top_level_certificate_mismatch": totals["top_level_certificate_mismatch"],
        "certificate_sandbox_match": totals["certificate_sandbox_match"],
        "certificate_sandbox_mismatch": totals["certificate_sandbox_mismatch"],
        "fixture_schema_coverage": ratio(totals["fixture_schema_verified"], fixture_bindings),
        "fixture_hash_coverage": ratio(totals["fixture_hash_verified"], fixture_bindings),
        "certificate_binding_coverage": ratio(totals["top_level_certificate_match"], fixture_bindings),
        "sandbox_binding_coverage": ratio(totals["certificate_sandbox_match"], fixture_bindings),
        "fixture_counts": dict(fixture_counts.most_common()),
        "fixture_family_counts": dict(fixture_family_counts.most_common()),
        "framework_contract_family_counts": dict(framework_contract_counts.most_common()),
        "verification_reason_counts": dict(verification_reasons.most_common(30)),
    }


def summarize_executable_evidence_integrity_accounting(cards: list[dict[str, Any]]) -> dict[str, Any]:
    components: Counter[str] = Counter()
    preservation_statuses: Counter[str] = Counter()
    adequacy_tiers: Counter[str] = Counter()
    verification_reasons: Counter[str] = Counter()
    totals = Counter()

    for card in cards:
        dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
        if not dynamic:
            continue
        totals["dynamic_cards"] += 1
        certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
        meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}

        for component, expert_key, expected_sha_key in [
            ("context_completion", "llm_context_completion", "java_source_sha256"),
            ("probe_synthesis", "llm_probe_synthesis", "probe_body_sha256"),
        ]:
            expert = dynamic.get(expert_key) if isinstance(dynamic.get(expert_key), dict) else {}
            payload = expert.get("payload") if isinstance(expert.get("payload"), dict) else {}
            if component == "context_completion" and expert.get("status") == "rejected":
                if payload.get("java_source_sha256"):
                    totals["diagnostic_source_artifacts_expected"] += 1
                diagnostic_artifact = (
                    expert.get("diagnostic_source_artifact")
                    if isinstance(expert.get("diagnostic_source_artifact"), dict)
                    else {}
                )
                if diagnostic_artifact:
                    totals["diagnostic_source_artifact_present"] += 1
                    ok, diagnostic_reasons = verify_quarantined_diagnostic_source_artifact(
                        diagnostic_artifact,
                        expected_sha=payload.get("java_source_sha256"),
                    )
                    if ok:
                        totals["diagnostic_source_artifact_verified"] += 1
                    else:
                        totals["diagnostic_source_artifact_unverified"] += 1
                    for reason in diagnostic_reasons:
                        verification_reasons[f"{component}:diagnostic_{reason}"] += 1
            if expert.get("status") != "completed":
                continue
            artifact = expert.get("source_artifact") if isinstance(expert.get("source_artifact"), dict) else {}
            totals["completed_expert_source_artifacts_required"] += 1
            components[component] += 1
            if not artifact:
                totals["source_artifact_missing"] += 1
                verification_reasons[f"{component}:source_artifact_missing"] += 1
                continue

            totals["source_artifact_present"] += 1
            expected_sha = payload.get(expected_sha_key) if component == "context_completion" else None
            artifact_ok, artifact_reasons = verify_source_artifact(artifact, expected_sha=expected_sha)
            if artifact_ok:
                totals["source_artifact_verified"] += 1
            else:
                totals["source_artifact_unverified"] += 1
            for reason in artifact_reasons:
                verification_reasons[f"{component}:{reason}"] += 1

            if artifact.get("retained") is True:
                totals["source_artifact_retained"] += 1
            else:
                totals["source_artifact_not_retained"] += 1
                verification_reasons[f"{component}:source_artifact_not_retained"] += 1
            if artifact.get(SOURCE_ARTIFACT_HASH_FIELD):
                totals["source_artifact_certificate_present"] += 1
            else:
                totals["source_artifact_certificate_missing"] += 1

            preservation = artifact.get("source_preservation") if isinstance(artifact.get("source_preservation"), dict) else {}
            preservation_ok = source_preservation_certificate_is_strong(artifact)
            if preservation:
                totals["source_preservation_present"] += 1
                preservation_statuses[str(preservation.get("status") or "missing")] += 1
            else:
                totals["source_preservation_missing"] += 1
                preservation_statuses["missing"] += 1
            if preservation_ok:
                totals["source_preservation_verified"] += 1
            else:
                totals["source_preservation_unverified"] += 1
                verification_reasons[f"{component}:source_preservation_unverified"] += 1

            if artifact_ok:
                source_match_ok, source_match_reasons = verify_executed_source_matches_artifact(
                    dynamic,
                    artifact,
                    issue_prefix=component,
                )
                if source_match_ok:
                    totals["executed_source_matches_artifact"] += 1
                else:
                    totals["executed_source_mismatch"] += 1
                for reason in source_match_reasons:
                    verification_reasons[f"{component}:{reason}"] += 1

            if component == "context_completion":
                for label, ok_reasons in [
                    ("context_source_safety", verify_context_source_safety_artifact(artifact)),
                    ("context_added_context", verify_context_added_context_artifact(artifact, payload)),
                    ("context_probe_execution_path", verify_context_probe_execution_path_artifact(artifact, payload)),
                ]:
                    ok, reasons = ok_reasons
                    if ok:
                        totals[f"{label}_verified"] += 1
                    else:
                        totals[f"{label}_unverified"] += 1
                    for reason in reasons:
                        verification_reasons[f"{component}:{reason}"] += 1
            else:
                binding_ok, binding_reasons = verify_probe_source_binding_artifact(artifact, payload)
                if binding_ok:
                    totals["probe_source_binding_verified"] += 1
                else:
                    totals["probe_source_binding_unverified"] += 1
                for reason in binding_reasons:
                    verification_reasons[f"{component}:{reason}"] += 1

        probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
        if not probe_contract:
            continue
        totals["probe_adequacy_required_cards"] += 1
        probe_section = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
        adequacy = (
            probe_section.get("probe_adequacy_certificate")
            if isinstance(probe_section.get("probe_adequacy_certificate"), dict)
            else {}
        )
        if not adequacy:
            totals["probe_adequacy_missing"] += 1
            verification_reasons["probe_adequacy:missing"] += 1
            continue
        totals["probe_adequacy_present"] += 1
        adequacy_tiers[str(adequacy.get("adequacy_tier") or "missing")] += 1
        expected = build_probe_adequacy_certificate(probe_contract)
        adequacy_hash = adequacy.get(PROBE_ADEQUACY_HASH_FIELD)
        verified = (
            adequacy.get("status") == "verified"
            and adequacy_hash == build_probe_adequacy_certificate_hash(adequacy)
            and probe_section.get("probe_adequacy_sha256") == adequacy_hash
            and bool(expected)
            and adequacy == expected
        )
        if verified:
            totals["probe_adequacy_verified"] += 1
        else:
            totals["probe_adequacy_unverified"] += 1
            verification_reasons["probe_adequacy:unverified_or_recomputed_mismatch"] += 1

    required_artifacts = totals["completed_expert_source_artifacts_required"]
    adequacy_required = totals["probe_adequacy_required_cards"]
    return {
        "system_role": "programmatic_executable_evidence_integrity_accounting",
        "purpose": "audit retained source sidecars, source preservation, probe bindings, and probe adequacy certificates",
        "dynamic_cards": totals["dynamic_cards"],
        "completed_expert_source_artifacts_required": required_artifacts,
        "source_artifact_present": totals["source_artifact_present"],
        "source_artifact_missing": totals["source_artifact_missing"],
        "source_artifact_verified": totals["source_artifact_verified"],
        "source_artifact_unverified": totals["source_artifact_unverified"],
        "source_artifact_retained": totals["source_artifact_retained"],
        "source_artifact_not_retained": totals["source_artifact_not_retained"],
        "source_artifact_certificate_present": totals["source_artifact_certificate_present"],
        "source_artifact_certificate_missing": totals["source_artifact_certificate_missing"],
        "diagnostic_source_artifacts_expected": totals["diagnostic_source_artifacts_expected"],
        "diagnostic_source_artifact_present": totals["diagnostic_source_artifact_present"],
        "diagnostic_source_artifact_verified": totals["diagnostic_source_artifact_verified"],
        "diagnostic_source_artifact_unverified": totals["diagnostic_source_artifact_unverified"],
        "source_preservation_present": totals["source_preservation_present"],
        "source_preservation_missing": totals["source_preservation_missing"],
        "source_preservation_verified": totals["source_preservation_verified"],
        "source_preservation_unverified": totals["source_preservation_unverified"],
        "executed_source_matches_artifact": totals["executed_source_matches_artifact"],
        "executed_source_mismatch": totals["executed_source_mismatch"],
        "context_source_safety_verified": totals["context_source_safety_verified"],
        "context_source_safety_unverified": totals["context_source_safety_unverified"],
        "context_added_context_verified": totals["context_added_context_verified"],
        "context_added_context_unverified": totals["context_added_context_unverified"],
        "context_probe_execution_path_verified": totals["context_probe_execution_path_verified"],
        "context_probe_execution_path_unverified": totals["context_probe_execution_path_unverified"],
        "probe_source_binding_verified": totals["probe_source_binding_verified"],
        "probe_source_binding_unverified": totals["probe_source_binding_unverified"],
        "probe_adequacy_required_cards": adequacy_required,
        "probe_adequacy_present": totals["probe_adequacy_present"],
        "probe_adequacy_missing": totals["probe_adequacy_missing"],
        "probe_adequacy_verified": totals["probe_adequacy_verified"],
        "probe_adequacy_unverified": totals["probe_adequacy_unverified"],
        "source_artifact_verification_rate": ratio(totals["source_artifact_verified"], required_artifacts),
        "source_preservation_verification_rate": ratio(totals["source_preservation_verified"], required_artifacts),
        "probe_adequacy_verification_rate": ratio(totals["probe_adequacy_verified"], adequacy_required),
        "component_counts": dict(components.most_common()),
        "source_preservation_status_counts": dict(preservation_statuses.most_common()),
        "probe_adequacy_tier_counts": dict(adequacy_tiers.most_common()),
        "verification_reason_counts": dict(verification_reasons.most_common(30)),
    }


def verify_quarantined_diagnostic_source_artifact(
    artifact: dict[str, Any],
    *,
    expected_sha: Any = None,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not artifact:
        return False, ["source_artifact_missing"]
    if artifact.get("schema_version") != SOURCE_ARTIFACT_SCHEMA_VERSION:
        return False, ["source_artifact_schema_mismatch"]
    if artifact.get("retained") is not False:
        return False, ["source_artifact_not_marked_unretained"]
    if artifact.get("quarantined") is not True:
        return False, ["source_artifact_not_quarantined"]
    artifact_certificate_sha = artifact.get(SOURCE_ARTIFACT_HASH_FIELD)
    if artifact_certificate_sha != build_source_artifact_hash(artifact):
        return False, ["source_artifact_certificate_sha_mismatch"]
    reasons.append("source_artifact_certificate_sha_verified")
    source_path = Path(str(artifact.get("path") or ""))
    if not source_path.exists() or not source_path.is_file():
        return False, reasons + ["source_artifact_file_missing"]
    bytes_data = source_path.read_bytes()
    actual_sha = hashlib.sha256(bytes_data).hexdigest()
    artifact_sha = str(artifact.get("sha256") or "")
    if artifact_sha != actual_sha:
        return False, reasons + ["source_artifact_sha_mismatch"]
    expected_text = str(expected_sha or "")
    if expected_text and expected_text != actual_sha:
        return False, reasons + ["context_payload_source_sha_mismatch"]
    try:
        if int(artifact.get("bytes")) != len(bytes_data):
            return False, reasons + ["source_artifact_byte_count_mismatch"]
    except (TypeError, ValueError):
        return False, reasons + ["source_artifact_byte_count_invalid"]
    reasons.append("source_artifact_verified")
    return True, reasons


def source_preservation_certificate_is_strong(artifact: dict[str, Any]) -> bool:
    preservation = artifact.get("source_preservation") if isinstance(artifact.get("source_preservation"), dict) else {}
    if not preservation:
        return False
    if preservation.get("schema_version") != "eviclone-source-preservation/v1":
        return False
    expected_sha = canonical_sha256({key: value for key, value in preservation.items() if key != "certificate_sha256"})
    if preservation.get("certificate_sha256") != expected_sha:
        return False
    if preservation.get("source_sha256") != artifact.get("sha256"):
        return False
    if preservation.get("status") not in {"exact", "normalized", "identifier_supported"}:
        return False
    for side in ["snippet_a", "snippet_b"]:
        snippet = preservation.get(side) if isinstance(preservation.get(side), dict) else {}
        if snippet.get("nonempty") is not True:
            return False
        retained = (
            snippet.get("exact_present") is True
            or snippet.get("normalized_present") is True
            or (
                isinstance(snippet.get("identifier_retention"), dict)
                and snippet["identifier_retention"].get("status") == "sufficient"
            )
        )
        if not retained:
            return False
    return True


def summarize_fusion_decision_accounting(cards: list[dict[str, Any]]) -> dict[str, Any]:
    final_sources: Counter[str] = Counter()
    totals = Counter()
    for card in cards:
        fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
        if not fusion:
            continue
        totals["fusion_cards"] += 1
        final_source = str(fusion.get("final_source") or "missing")
        final_sources[final_source] += 1
        dependencies = fusion.get("trust_dependencies") if isinstance(fusion.get("trust_dependencies"), dict) else {}
        case_summary = dependencies.get("case_summary") if isinstance(dependencies.get("case_summary"), dict) else {}
        if case_summary:
            totals["case_summary_present"] += 1
            if int(case_summary.get("mismatch_count") or 0) > 0:
                totals["case_summary_mismatch_cards"] += 1
            if int(case_summary.get("boundary_mismatch_count") or 0) > 0:
                totals["case_summary_boundary_mismatch_cards"] += 1
            if int(case_summary.get("non_boundary_mismatch_count") or 0) > 0:
                totals["case_summary_non_boundary_mismatch_cards"] += 1
            if case_summary.get("boundary_only_divergence") is True:
                totals["boundary_only_divergence_cards"] += 1
                if final_source == "base_model_passthrough_after_untrusted_dynamic":
                    totals["boundary_only_base_passthrough_cards"] += 1
        reasons = [str(reason) for reason in fusion.get("reasons") or []]
        if "boundary_only_divergence_not_decisive_for_override" in reasons:
            totals["boundary_only_not_decisive_for_override"] += 1
        accounting = (
            fusion.get("decision_accounting")
            if isinstance(fusion.get("decision_accounting"), dict)
            else {}
        )
        if not accounting:
            totals["missing_decision_accounting"] += 1
            continue
        totals["accounted_cards"] += 1
        for key in [
            "dynamic_override_eligible",
            "override_applied",
            "confirmation_applied",
            "trusted_without_base_applied",
            "base_passthrough_applied",
            "no_reliable_label",
        ]:
            totals[key] += int(accounting.get(key) is True)
    accounted = totals["accounted_cards"]
    return {
        "fusion_cards": totals["fusion_cards"],
        "accounted_cards": accounted,
        "missing_decision_accounting": totals["missing_decision_accounting"],
        "final_source_counts": dict(final_sources.most_common()),
        "dynamic_override_eligible": totals["dynamic_override_eligible"],
        "override_applied": totals["override_applied"],
        "confirmation_applied": totals["confirmation_applied"],
        "trusted_without_base_applied": totals["trusted_without_base_applied"],
        "base_passthrough_applied": totals["base_passthrough_applied"],
        "no_reliable_label": totals["no_reliable_label"],
        "case_summary_present": totals["case_summary_present"],
        "case_summary_mismatch_cards": totals["case_summary_mismatch_cards"],
        "case_summary_boundary_mismatch_cards": totals["case_summary_boundary_mismatch_cards"],
        "case_summary_non_boundary_mismatch_cards": totals["case_summary_non_boundary_mismatch_cards"],
        "boundary_only_divergence_cards": totals["boundary_only_divergence_cards"],
        "boundary_only_base_passthrough_cards": totals["boundary_only_base_passthrough_cards"],
        "boundary_only_not_decisive_for_override": totals["boundary_only_not_decisive_for_override"],
        "override_rate_among_accounted": round(totals["override_applied"] / accounted, 6) if accounted else 0.0,
        "passthrough_rate_among_accounted": round(totals["base_passthrough_applied"] / accounted, 6) if accounted else 0.0,
    }


def llm_error_bucket(card: dict[str, Any]) -> str:
    llm = card.get("llm_evidence")
    if not isinstance(llm, dict) or llm.get("status") != "failed":
        return ""
    error = str(llm.get("error") or "").strip()
    if not error:
        return "failed_without_error"
    if "HTTP 402" in error or "Insufficient Balance" in error:
        return "HTTP 402: Insufficient Balance"
    if "HTTP 429" in error or "rate limit" in error.lower():
        return "HTTP 429: rate limit"
    if "missing API key" in error:
        return "missing API key"
    return error[:160]
