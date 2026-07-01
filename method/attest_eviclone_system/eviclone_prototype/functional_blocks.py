from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .executor import JavaMethod, parse_method, simple_type


FUNCTIONAL_BLOCK_IR_SCHEMA_VERSION = "eviclone-functional-block-ir/v1"
FUNCTIONAL_BLOCK_PAIR_SCHEMA_VERSION = "eviclone-functional-block-pair/v1"
FUNCTIONAL_BLOCK_HASH_FIELD = "ir_sha256"
FUNCTIONAL_BLOCK_PAIR_HASH_FIELD = "pair_ir_sha256"

MUTATING_METHODS = {
    "add",
    "addAll",
    "append",
    "clear",
    "delete",
    "insert",
    "put",
    "putAll",
    "remove",
    "replace",
    "set",
    "setLength",
    "sort",
}

API_MARKER_PATTERNS = {
    "io": r"\b(File|Path|Files|InputStream|OutputStream|Reader|Writer|PrintWriter|BufferedReader)\b",
    "network": r"\b(URL|URI|URLConnection|HttpURLConnection|Socket|HttpClient)\b",
    "jdbc": r"\b(Connection|DataSource|PreparedStatement|Statement|ResultSet|SQLException)\b",
    "servlet": r"\b(HttpServletRequest|HttpServletResponse|HttpSession|Cookie)\b",
    "gui": r"\b(ActionEvent|ActionListener|JButton|JTextField|JTextArea|JLabel|JPanel|JFrame)\b",
    "time": r"\b(Date|Calendar|Instant|LocalDate|LocalDateTime|System\.currentTimeMillis|new Date)\b",
    "collections": r"\b(List|Set|Map|Collection|Arrays|Collections|Iterator)\b",
}


def extract_functional_block_ir(code: str, *, side: str = "single") -> dict[str, Any]:
    method = parse_method(code)
    body = extract_method_body(code)
    raw_blocks = split_body_into_blocks(body)
    blocks = [
        build_functional_block(index=index, raw=raw, method=method)
        for index, raw in enumerate(raw_blocks)
        if raw.strip()
    ]
    edges = build_block_edges(blocks)
    ir: dict[str, Any] = {
        "schema_version": FUNCTIONAL_BLOCK_IR_SCHEMA_VERSION,
        "side": side,
        "method": method_to_contract(method),
        "extraction_policy": "deterministic_core_logic_statement_blocks/v1",
        "standard_module_sequence": [block["kind"] for block in blocks],
        "blocks": blocks,
        "edges": edges,
        "llm_contract": {
            "allowed_roles": ["block_kind_disambiguation", "missing_context_completion", "probe_synthesis"],
            "clone_decision_allowed": False,
            "raw_source_patch_allowed": False,
            "must_preserve_observed_block_io": True,
        },
        "limitations": [
            "regex-based Java fragment extraction; later stages must verify generated harnesses by compilation and execution",
            "read/write sets are conservative lexical approximations rather than full AST symbol resolution",
        ],
    }
    ir[FUNCTIONAL_BLOCK_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in ir.items() if key != FUNCTIONAL_BLOCK_HASH_FIELD}
    )
    return ir


def extract_pair_functional_block_ir(code_a: str, code_b: str) -> dict[str, Any]:
    ir_a = extract_functional_block_ir(code_a, side="a")
    ir_b = extract_functional_block_ir(code_b, side="b")
    pair_ir: dict[str, Any] = {
        "schema_version": FUNCTIONAL_BLOCK_PAIR_SCHEMA_VERSION,
        "a": ir_a,
        "b": ir_b,
        "module_signature_a": functional_module_signature(ir_a),
        "module_signature_b": functional_module_signature(ir_b),
        "module_signature_equal": functional_module_signature(ir_a) == functional_module_signature(ir_b),
        "llm_contract": {
            "clone_decision_allowed": False,
            "comparison_owner": "programmatic_ir_and_executable_evidence",
            "allowed_llm_roles": ["block_kind_disambiguation", "missing_context_completion", "probe_synthesis"],
        },
    }
    pair_ir[FUNCTIONAL_BLOCK_PAIR_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in pair_ir.items() if key != FUNCTIONAL_BLOCK_PAIR_HASH_FIELD}
    )
    return pair_ir


def verify_functional_block_ir(ir: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if ir.get("schema_version") != FUNCTIONAL_BLOCK_IR_SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    expected = canonical_sha256({key: value for key, value in ir.items() if key != FUNCTIONAL_BLOCK_HASH_FIELD})
    if ir.get(FUNCTIONAL_BLOCK_HASH_FIELD) != expected:
        issues.append("ir_sha256_mismatch")
    if ir.get("llm_contract", {}).get("clone_decision_allowed") is not False:
        issues.append("llm_clone_decision_not_forbidden")
    if ir.get("llm_contract", {}).get("raw_source_patch_allowed") is not False:
        issues.append("llm_raw_source_patch_not_forbidden")
    return {"status": "verified" if not issues else "rejected", "issues": issues}


def verify_pair_functional_block_ir(pair_ir: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if pair_ir.get("schema_version") != FUNCTIONAL_BLOCK_PAIR_SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    expected = canonical_sha256(
        {key: value for key, value in pair_ir.items() if key != FUNCTIONAL_BLOCK_PAIR_HASH_FIELD}
    )
    if pair_ir.get(FUNCTIONAL_BLOCK_PAIR_HASH_FIELD) != expected:
        issues.append("pair_ir_sha256_mismatch")
    for side in ("a", "b"):
        result = verify_functional_block_ir(pair_ir.get(side) or {})
        issues.extend(f"{side}:{issue}" for issue in result["issues"])
    if pair_ir.get("llm_contract", {}).get("clone_decision_allowed") is not False:
        issues.append("pair_llm_clone_decision_not_forbidden")
    return {"status": "verified" if not issues else "rejected", "issues": issues}


def functional_module_signature(ir: dict[str, Any]) -> list[str]:
    return [str(kind) for kind in ir.get("standard_module_sequence") or []]


def extract_method_body(code: str) -> str:
    first = code.find("{")
    if first < 0:
        return ""
    depth = 0
    for index in range(first, len(code)):
        char = code[index]
        if char == "{":
            depth += 1
            if depth == 1:
                body_start = index + 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return code[body_start:index]
    return code[first + 1 :]


def split_body_into_blocks(body: str) -> list[str]:
    body = strip_comments(body)
    blocks: list[str] = []
    buf: list[str] = []
    depth = 0
    in_string = False
    escaped = False
    for char in body:
        buf.append(char)
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
            flush_statement_header(blocks, buf)
        elif char == "}":
            depth = max(0, depth - 1)
            flush_buffer(blocks, buf)
        elif char == ";" and depth == 0:
            flush_buffer(blocks, buf)
    flush_buffer(blocks, buf)
    return [normalize_statement(block) for block in blocks if normalize_statement(block)]


def build_functional_block(*, index: int, raw: str, method: JavaMethod | None) -> dict[str, Any]:
    kind = classify_block(raw)
    block = {
        "block_id": f"B{index:03d}",
        "order": index,
        "kind": kind,
        "standard_module": kind,
        "statement": raw,
        "reads": sorted(read_symbols(raw, method)),
        "writes": sorted(write_symbols(raw)),
        "api_markers": sorted(api_markers(raw)),
        "control_markers": sorted(control_markers(raw)),
        "side_effect_markers": sorted(side_effect_markers(raw)),
    }
    block["block_sha256"] = canonical_sha256(block)
    return block


def classify_block(statement: str) -> str:
    s = statement.strip()
    lower = s.lower()
    if re.match(r"^(for|while|do)\b", s):
        return "collection_iteration" if re.match(r"^for\s*\([^;]+:", s) or re.search(API_MARKER_PATTERNS["collections"], s) else "iteration"
    if re.match(r"^return\b", s):
        return "return_mapping"
    if re.match(r"^(if|else if|switch)\b", s) or "?" in s and ":" in s:
        return "branch_guard"
    if re.match(r"^(try|catch|finally|throw)\b", s):
        return "exception_boundary"
    if any(re.search(pattern, s) for key, pattern in API_MARKER_PATTERNS.items() if key in {"io", "network", "jdbc", "servlet", "gui"}):
        return "environment_interaction"
    if re.search(r"\.(trim|toLowerCase|toUpperCase|split|parseInt|parseLong|parseDouble|valueOf)\s*\(", s):
        return "input_normalization"
    if re.search(r"(\+\+|--|[^=!<>]=[^=])", s) or re.search(r"\.\s*(add|put|set|append|remove|clear)\s*\(", s):
        return "state_update"
    if "stream()" in lower or ".map(" in lower or ".filter(" in lower or ".collect(" in lower:
        return "collection_transform"
    return "pure_computation"


def build_block_edges(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for left, right in zip(blocks, blocks[1:]):
        edges.append(edge(left["block_id"], right["block_id"], "control_order", []))
    for src in blocks:
        writes = set(src.get("writes") or [])
        if not writes:
            continue
        for dst in blocks:
            if dst["order"] <= src["order"]:
                continue
            shared = sorted(writes & set(dst.get("reads") or []))
            if shared:
                edges.append(edge(src["block_id"], dst["block_id"], "data_dependency", shared))
    return edges


def edge(src: str, dst: str, kind: str, variables: list[str]) -> dict[str, Any]:
    payload = {"src": src, "dst": dst, "kind": kind, "variables": variables}
    payload["edge_sha256"] = canonical_sha256(payload)
    return payload


def read_symbols(statement: str, method: JavaMethod | None) -> set[str]:
    symbols = set(re.findall(r"\b[a-zA-Z_]\w*\b", statement))
    keywords = {
        "if",
        "else",
        "for",
        "while",
        "return",
        "new",
        "public",
        "private",
        "protected",
        "static",
        "final",
        "try",
        "catch",
        "throw",
        "throws",
        "null",
        "true",
        "false",
    }
    symbols -= keywords
    if method:
        param_names = {param.name for param in method.params}
        symbols |= param_names & set(statement.split())
    symbols -= write_symbols(statement)
    return {symbol for symbol in symbols if not symbol[:1].isupper()}


def write_symbols(statement: str) -> set[str]:
    writes = set(re.findall(r"\b([a-zA-Z_]\w*)\s*(?:\+\+|--|[+*/%-]?=)", statement))
    for receiver, method_name in re.findall(r"\b([a-zA-Z_]\w*)\s*\.\s*([a-zA-Z_]\w*)\s*\(", statement):
        if method_name in MUTATING_METHODS:
            writes.add(receiver)
    return writes


def api_markers(statement: str) -> set[str]:
    return {name for name, pattern in API_MARKER_PATTERNS.items() if re.search(pattern, statement)}


def control_markers(statement: str) -> set[str]:
    markers = set()
    for marker in ("if", "switch", "for", "while", "try", "catch", "return", "throw"):
        if re.search(rf"\b{marker}\b", statement):
            markers.add(marker)
    return markers


def side_effect_markers(statement: str) -> set[str]:
    markers = set()
    if re.search(r"\.\s*(add|put|set|append|remove|clear|write|delete|executeUpdate)\s*\(", statement):
        markers.add("mutation_or_external_effect")
    if any(name in api_markers(statement) for name in ("io", "network", "jdbc", "servlet", "gui")):
        markers.add("environment_dependent")
    return markers


def method_to_contract(method: JavaMethod | None) -> dict[str, Any] | None:
    if method is None:
        return None
    return {
        "name": method.name,
        "return_type": method.return_type,
        "return_type_simple": simple_type(method.return_type),
        "params": [
            {"name": param.name, "type_name": param.type_name, "type_simple": simple_type(param.type_name)}
            for param in method.params
        ],
        "is_static": method.is_static,
    }


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", text)


def flush_statement_header(blocks: list[str], buf: list[str]) -> None:
    text = "".join(buf).strip()
    if text:
        blocks.append(text)
    buf.clear()


def flush_buffer(blocks: list[str], buf: list[str]) -> None:
    text = "".join(buf).strip()
    if text:
        blocks.append(text)
    buf.clear()


def normalize_statement(statement: str) -> str:
    return re.sub(r"\s+", " ", statement.strip().strip("{}").strip())


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
