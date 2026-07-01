from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.config import DEFAULT_API_KEY_ENV, DEFAULT_BASE_URL, DEFAULT_MODEL, LLMConfig  # noqa: E402
from eviclone_prototype.dataset import ClonePair, load_pairs  # noqa: E402
from eviclone_prototype.executor import parse_probe_output, proc_info  # noqa: E402
from eviclone_prototype.llm import ChatClient  # noqa: E402
from eviclone_prototype.probe_synthesis import synthesize_probe_with_llm  # noqa: E402
from scripts.build_probe_execution_readiness_audit import (  # noqa: E402
    DEFAULT_SOURCE_CARDS,
    card_context_completion,
    card_context_source_artifact,
    candidate_pair_key,
    load_candidates,
    materialize_candidate_source_artifact,
    source_file_check,
)
from scripts.build_probe_synthesis_plan import DEFAULT_CANDIDATES, DEFAULT_RUN_DIR, sorted_counter  # noqa: E402

DEFAULT_DATASET = DEFAULT_RUN_DIR / "probe_source_retention_rerun_queue" / "pairs.jsonl"
DEFAULT_OUTPUT = DEFAULT_RUN_DIR / "probe_synthesis_execution_results.jsonl"
DEFAULT_SUMMARY = DEFAULT_RUN_DIR / "probe_synthesis_execution.summary.json"
DEFAULT_REPORT = DEFAULT_RUN_DIR / "probe_synthesis_execution.md"
DEFAULT_SOURCE_DIR = DEFAULT_RUN_DIR / "probe_synthesis_execution_sources"

MAIN_RE = re.compile(r"public\s+static\s+void\s+main\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\{", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute probe-synthesis candidates against retained EviProbe.java sidecars.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--source-cards", type=Path, default=DEFAULT_SOURCE_CARDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--timeout-sec", type=int, default=8)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--include-review", action="store_true")
    parser.add_argument("--with-llm-probe", action="store_true")
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--api-key", type=str, default="")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--resume", action="store_true", help="reuse existing result rows and append only missing candidates")
    args = parser.parse_args()

    result = run_probe_synthesis_execution(
        dataset=args.dataset,
        candidates_jsonl=args.candidates,
        source_cards_jsonl=args.source_cards,
        output_jsonl=args.output,
        summary_path=args.summary,
        report_path=args.report,
        source_dir=args.source_dir,
        limit=args.limit,
        offset=args.offset,
        timeout_sec=args.timeout_sec,
        workers=args.workers,
        include_review=args.include_review,
        with_llm_probe=args.with_llm_probe,
        llm_retries=args.llm_retries,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        api_key=args.api_key,
        temperature=args.temperature,
        keep_work=args.keep_work,
        resume=args.resume,
    )
    print(json.dumps({"status": result["status"], "summary": str(args.summary.resolve())}, ensure_ascii=False))
    return 0 if result["status"] in {"completed", "completed_with_warnings", "no_candidates"} else 2


def run_probe_synthesis_execution(
    *,
    dataset: Path,
    candidates_jsonl: Path,
    source_cards_jsonl: Path,
    output_jsonl: Path,
    summary_path: Path,
    report_path: Path,
    source_dir: Path,
    limit: int = 0,
    offset: int = 0,
    timeout_sec: int = 8,
    workers: int = 1,
    include_review: bool = False,
    with_llm_probe: bool = False,
    llm_retries: int = 1,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    api_key: str = "",
    temperature: float = 0.0,
    keep_work: bool = False,
    resume: bool = False,
) -> dict[str, Any]:
    pairs = {pair_key(pair.function_id_a, pair.function_id_b): pair for pair in load_pairs(dataset)}
    cards = load_cards_by_pair(source_cards_jsonl)
    candidates = [
        materialize_candidate_source_artifact(candidate, cards)
        for candidate in load_candidates(candidates_jsonl)
    ]
    if offset:
        candidates = candidates[offset:]
    if limit:
        candidates = candidates[:limit]
    client = make_probe_client(
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        api_key=api_key,
        temperature=temperature,
    ) if with_llm_probe else None

    selected_keys = {candidate_pair_key(candidate) for candidate in candidates}
    existing_records = load_existing_execution_records(output_jsonl, selected_keys) if resume else {}

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    pending = [candidate for candidate in candidates if candidate_pair_key(candidate) not in existing_records]
    mode = "a" if existing_records and output_jsonl.exists() else "w"
    with output_jsonl.open(mode, encoding="utf-8", newline="\n") as handle:
        for candidate in candidates:
            key = candidate_pair_key(candidate)
            if key in existing_records:
                records.append(existing_records[key])
        if max(1, int(workers or 1)) == 1:
            for candidate in pending:
                record = execute_candidate_probe_for_maps(
                    candidate,
                    pairs=pairs,
                    cards=cards,
                    source_dir=source_dir,
                    timeout_sec=timeout_sec,
                    include_review=include_review,
                    client=client,
                    llm_retries=llm_retries,
                    keep_work=keep_work,
                )
                records.append(record)
                write_record(handle, record)
        else:
            with ThreadPoolExecutor(max_workers=max(1, int(workers or 1))) as executor:
                futures = [
                    executor.submit(
                        execute_candidate_probe_for_maps,
                        candidate,
                        pairs=pairs,
                        cards=cards,
                        source_dir=source_dir,
                        timeout_sec=timeout_sec,
                        include_review=include_review,
                        client=client,
                        llm_retries=llm_retries,
                        keep_work=keep_work,
                    )
                    for candidate in pending
                ]
                for future in as_completed(futures):
                    record = future.result()
                    records.append(record)
                    write_record(handle, record)

    summary = summarize_probe_records(
        records,
        dataset=dataset,
        candidates_jsonl=candidates_jsonl,
        source_cards_jsonl=source_cards_jsonl,
        output_jsonl=output_jsonl,
        source_dir=source_dir,
        include_review=include_review,
        with_llm_probe=with_llm_probe,
        resume=resume,
        existing_records_reused=sum(1 for candidate in candidates if candidate_pair_key(candidate) in existing_records),
        workers=max(1, int(workers or 1)),
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(report_path, summary)
    return summary


def execute_candidate_probe(
    *,
    candidate: dict[str, Any],
    pair: ClonePair | None,
    source_card: dict[str, Any] | None,
    source_dir: Path,
    timeout_sec: int,
    include_review: bool,
    client: ChatClient | None,
    llm_retries: int,
    keep_work: bool,
) -> dict[str, Any]:
    base = base_record(candidate, pair)
    if pair is None:
        return {**base, "status": "dataset_pair_missing"}
    artifact = candidate_source_artifact(candidate)
    file_check = source_file_check(
        artifact,
        expected_sha=(candidate.get("context_completion") or {}).get("java_source_sha256"),
        allow_expected_drift=candidate.get("source_artifact_origin") == "source_retention_cards",
    )
    base["source_file_check"] = file_check
    if file_check.get("status") != "verified":
        return {**base, "status": "source_not_ready"}
    source_path = Path(str(file_check["path"]))
    source = source_path.read_text(encoding="utf-8", errors="replace")
    helper_completion = complete_probe_helpers(source)
    source = str(helper_completion.get("source") or source)
    base["probe_helper_completion"] = {
        key: value for key, value in helper_completion.items() if key != "source"
    }
    if not required_probe_helpers_present(source):
        return {**base, "status": "required_helpers_missing"}

    probe_generation = generate_probe_body(
        candidate=candidate,
        pair=pair,
        source=source,
        source_card=source_card,
        include_review=include_review,
        client=client,
        llm_retries=llm_retries,
    )
    base["probe_generation"] = {key: value for key, value in probe_generation.items() if key != "probe_body"}
    probe_body = str(probe_generation.get("probe_body") or "")
    if not probe_body:
        return {**base, "status": "probe_not_generated"}

    probe_source = replace_main_body(source, probe_body)
    if probe_source == source:
        return {**base, "status": "main_replacement_failed"}
    sidecar = write_probe_source(
        probe_source,
        source_dir,
        pair_id=pair.pair_id,
        case_id=int_or_none(candidate.get("case_id")) or 0,
        probe_origin=str(probe_generation.get("origin") or "unknown"),
    )
    execution = compile_and_run_probe_source(
        probe_source,
        timeout_sec=timeout_sec,
        keep_work=keep_work,
    )
    parsed = execution.get("execution", {}).get("parsed") if isinstance(execution.get("execution"), dict) else None
    dynamic_label = 1 if isinstance(parsed, dict) and parsed.get("same") is True else 0 if isinstance(parsed, dict) and parsed.get("same") is False else None
    return {
        **base,
        "status": execution_status(execution),
        "probe_source_artifact": sidecar,
        "compile": execution.get("compile"),
        "execution": execution.get("execution"),
        "dynamic_label": dynamic_label,
        "benefit": is_benefit(base.get("baseline_label"), base.get("gold"), dynamic_label),
        "harm": is_harm(base.get("baseline_label"), base.get("gold"), dynamic_label),
    }


def execute_candidate_probe_for_maps(
    candidate: dict[str, Any],
    *,
    pairs: dict[tuple[str, str], ClonePair],
    cards: dict[tuple[str, str], dict[str, Any]],
    source_dir: Path,
    timeout_sec: int,
    include_review: bool,
    client: ChatClient | None,
    llm_retries: int,
    keep_work: bool,
) -> dict[str, Any]:
    key = candidate_pair_key(candidate)
    return execute_candidate_probe(
        candidate=candidate,
        pair=pairs.get(key),
        source_card=cards.get(key),
        source_dir=source_dir,
        timeout_sec=timeout_sec,
        include_review=include_review,
        client=client,
        llm_retries=llm_retries,
        keep_work=keep_work,
    )


def write_record(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    handle.flush()


def generate_probe_body(
    *,
    candidate: dict[str, Any],
    pair: ClonePair,
    source: str,
    source_card: dict[str, Any] | None,
    include_review: bool,
    client: ChatClient | None,
    llm_retries: int,
) -> dict[str, Any]:
    route = str(candidate.get("generation_route") or "")
    if route == "deterministic_template" or (include_review and route == "deterministic_template_with_review"):
        body = deterministic_probe_body(candidate)
        if body:
            return {
                "origin": "deterministic_template",
                "route": route,
                "probe_body_sha256": sha256_text(body),
                "probe_body": body,
                "review_required": route == "deterministic_template_with_review",
            }
    if client is None:
        return {
            "origin": "not_generated",
            "route": route,
            "reason": "deterministic template unsupported and --with-llm-probe disabled",
            "probe_body": "",
        }
    dynamic = source_card.get("dynamic_evidence") if isinstance(source_card, dict) and isinstance(source_card.get("dynamic_evidence"), dict) else {}
    completion = synthesize_probe_with_llm(
        pair,
        generated_source=source,
        compile_info=dynamic.get("compile") if isinstance(dynamic.get("compile"), dict) else {},
        meta=dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {},
        client=client,
        retries=llm_retries,
    )
    probe_body = str(completion.get("probe_body") or "")
    return {
        "origin": "llm_probe_synthesis",
        "route": route,
        "status": completion.get("status"),
        "error": completion.get("error"),
        "payload": completion.get("payload"),
        "expert_invocation": completion.get("expert_invocation"),
        "probe_body_sha256": sha256_text(probe_body) if probe_body else None,
        "probe_body": probe_body,
    }


def deterministic_probe_body(candidate: dict[str, Any]) -> str:
    mode = str(candidate.get("probe_mode") or "")
    method_a = candidate.get("method_a") if isinstance(candidate.get("method_a"), dict) else {}
    method_b = candidate.get("method_b") if isinstance(candidate.get("method_b"), dict) else {}
    if mode == "llm_probe_contract":
        return ""
    if not method_a.get("name") or not method_b.get("name"):
        return ""
    if mode == "return_value_probe" and (is_void(method_a) or is_void(method_b)):
        return ""
    if not params_supported(method_a) or not params_supported(method_b):
        return ""
    case_count = 3 if mode in {"return_value_probe", "exception_probe"} else 1
    lines = [
        "StringBuilder outA = new StringBuilder();",
        "StringBuilder outB = new StringBuilder();",
    ]
    for index in range(case_count):
        lines.extend(side_invocation_block("A", index, method_a, mode))
        lines.extend(side_invocation_block("B", index, method_b, mode))
    lines.extend(
        [
            "String finalA = outA.toString();",
            "String finalB = outB.toString();",
            "printResult(finalA.equals(finalB), finalA, finalB);",
        ]
    )
    return "\n".join(lines)


def side_invocation_block(side: str, index: int, method: dict[str, Any], mode: str) -> list[str]:
    lower = side.lower()
    root = f"root{side}{index}"
    src = f"src{side}{index}"
    out = f"outPath{side}{index}"
    obs = f"obsOut{side}{index}"
    writer = f"obsWriter{side}{index}"
    lines = [
        f'java.nio.file.Path {root} = work.resolve("{side}{index}");',
        f"java.nio.file.Files.createDirectories({root});",
        f"java.nio.file.Path {src} = {root}.resolve(\"input.txt\");",
        f"java.nio.file.Path {out} = {root}.resolve(\"output.txt\");",
        f'java.nio.file.Files.write({src}, ("alpha\\nbeta\\ncase{index}\\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));',
        f"java.io.ByteArrayOutputStream {obs} = new java.io.ByteArrayOutputStream();",
        f"java.io.StringWriter {writer} = new java.io.StringWriter();",
        "try {",
    ]
    args = [
        argument_expr(param, side=side, index=index, mode=mode)
        for param in method.get("params") or []
        if isinstance(param, dict)
    ]
    call = f"new Snippet{side}().{method.get('name')}({', '.join(args)})"
    if is_void(method):
        lines.append(f"    {call};")
        lines.append(f'    Object ret{side}{index} = "void";')
    else:
        lines.append(f"    Object ret{side}{index} = {call};")
    lines.append(f"    {writer}.flush();")
    lines.append(f'    out{side}.append("case{index}:return=").append(normalizeValue(ret{side}{index}));')
    lines.append(f'    out{side}.append("|stream=").append(b64({obs}.toByteArray()));')
    lines.append(f'    out{side}.append("|writer=").append({writer}.toString());')
    lines.append(f'    out{side}.append("|file_exists=").append(java.nio.file.Files.exists({out}));')
    lines.append(f"    if (java.nio.file.Files.exists({out})) out{side}.append(\"|file=\").append(b64(java.nio.file.Files.readAllBytes({out})));")
    lines.append(f'    out{side}.append("\\n");')
    lines.append("} catch (Throwable t) {")
    lines.append(f'    out{side}.append("case{index}:EX=").append(t.getClass().getName()).append(":").append(String.valueOf(t.getMessage())).append("\\n");')
    lines.append("}")
    return lines


def argument_expr(param: dict[str, Any], *, side: str, index: int, mode: str) -> str:
    type_name = str(param.get("type") or "")
    name = str(param.get("name") or "").lower()
    key = simple_type_key(type_name)
    src = f"src{side}{index}"
    out = f"outPath{side}{index}"
    root = f"root{side}{index}"
    obs = f"obsOut{side}{index}"
    writer = f"obsWriter{side}{index}"
    if key == "string":
        if "encoding" in name or "charset" in name:
            return '"UTF-8"'
        if any(token in name for token in ["url", "uri", "page", "link"]):
            return f"{src}.toUri().toURL().toString()"
        if any(token in name for token in ["out", "dest", "target", "output"]):
            return f"{out}.toString()"
        if any(token in name for token in ["dir", "folder"]):
            return f"{root}.toString()"
        if any(token in name for token in ["file", "path", "src", "source", "input"]):
            return f"{src}.toString()"
        return f'"alpha{index}"'
    if key in {"int", "integer"}:
        return str([0, 1, -1][index % 3])
    if key in {"long"}:
        return str([0, 1, -1][index % 3]) + "L"
    if key in {"double"}:
        return ["0.0d", "1.5d", "-1.0d"][index % 3]
    if key in {"float"}:
        return ["0.0f", "1.5f", "-1.0f"][index % 3]
    if key in {"boolean"}:
        return "true" if index % 2 == 0 else "false"
    if key == "file":
        return f"{src}.toFile()"
    if key == "path":
        return src
    if key == "url":
        return f"{src}.toUri().toURL()"
    if key == "uri":
        return f"{src}.toUri()"
    if key == "inputstream":
        return f"new java.io.ByteArrayInputStream((\"alpha\\nbeta\\ncase{index}\\n\").getBytes(java.nio.charset.StandardCharsets.UTF_8))"
    if key == "outputstream":
        return obs
    if key == "reader":
        return f"new java.io.StringReader(\"alpha\\nbeta\\ncase{index}\\n\")"
    if key == "writer":
        return writer
    if key in {"list", "collection", "iterable"}:
        return 'new java.util.ArrayList<String>(java.util.Arrays.asList("alpha", "beta"))'
    if key == "arraylist":
        return 'new java.util.ArrayList<String>(java.util.Arrays.asList("alpha", "beta"))'
    if key == "set":
        return 'new java.util.LinkedHashSet<String>(java.util.Arrays.asList("alpha", "beta"))'
    if key == "hashset":
        return 'new java.util.HashSet<String>(java.util.Arrays.asList("alpha", "beta"))'
    if key == "map":
        return 'new java.util.LinkedHashMap<String, String>() {{ put("alpha", "beta"); put("case", "case' + str(index) + '"); }}'
    if key == "hashmap":
        return 'new java.util.HashMap<String, String>() {{ put("alpha", "beta"); put("case", "case' + str(index) + '"); }}'
    if key == "properties":
        return 'new java.util.Properties() {{ setProperty("alpha", "beta"); setProperty("case", "case' + str(index) + '"); }}'
    if key == "bufferedreader":
        return f"new java.io.BufferedReader(new java.io.StringReader(\"alpha\\nbeta\\ncase{index}\\n\"))"
    if key == "bufferedwriter":
        return f"new java.io.BufferedWriter({writer})"
    if key == "printwriter":
        return f"new java.io.PrintWriter({writer})"
    if key.endswith("[]"):
        if key in {"byte[]"}:
            return f"(\"alpha\\nbeta\\ncase{index}\\n\").getBytes(java.nio.charset.StandardCharsets.UTF_8)"
        if key in {"char[]"}:
            return f"\"alpha\\nbeta\\ncase{index}\\n\".toCharArray()"
        if key in {"int[]", "integer[]"}:
            return "new int[] {1, 2, 3}"
        if key in {"long[]"}:
            return "new long[] {1L, 2L, 3L}"
        if key in {"boolean[]"}:
            return "new boolean[] {true, false}"
        return 'new String[] {"alpha", "beta"}'
    return "null"


def params_supported(method: dict[str, Any]) -> bool:
    return all(argument_supported(param) for param in method.get("params") or [] if isinstance(param, dict))


def argument_supported(param: dict[str, Any]) -> bool:
    key = simple_type_key(str(param.get("type") or ""))
    return key in {
        "string",
        "int",
        "integer",
        "long",
        "double",
        "float",
        "boolean",
        "file",
        "path",
        "url",
        "uri",
        "inputstream",
        "outputstream",
        "reader",
        "writer",
        "bufferedreader",
        "bufferedwriter",
        "printwriter",
        "list",
        "arraylist",
        "collection",
        "iterable",
        "set",
        "hashset",
        "map",
        "hashmap",
        "properties",
        "byte[]",
        "char[]",
        "string[]",
        "int[]",
        "integer[]",
        "long[]",
        "boolean[]",
    }


def simple_type_key(type_name: str) -> str:
    text = re.sub(r"\bfinal\b", "", type_name or "")
    text = re.sub(r"<.*>", "", text)
    text = text.replace("...", "[]").strip()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text.replace(" ", "").lower()


def is_void(method: dict[str, Any]) -> bool:
    return simple_type_key(str(method.get("return_type") or "")) == "void"


def required_probe_helpers_present(source: str) -> bool:
    return all(helper_method_defined(source, name) for name in ("printResult", "normalizeValue", "b64"))


def complete_probe_helpers(source: str) -> dict[str, Any]:
    inserted: list[str] = []
    helper_blocks: list[str] = []
    if not helper_method_defined(source, "printResult"):
        inserted.append("printResult")
        helper_blocks.append(
            """
    public static void printResult(boolean same, String outA, String outB) {
        System.out.println("EVICLONE_RESULT {\\\"status\\\":\\\"executed\\\",\\\"same\\\":"
                + same + ",\\\"out_a\\\":\\\"" + jsonEscape(outA)
                + "\\\",\\\"out_b\\\":\\\"" + jsonEscape(outB) + "\\\"}");
    }
"""
        )
    if not helper_method_defined(source, "normalizeValue"):
        inserted.append("normalizeValue")
        helper_blocks.append(
            """
    public static String normalizeValue(Object value) {
        if (value == null) return "null";
        Class<?> type = value.getClass();
        if (!type.isArray()) return String.valueOf(value);
        if (value instanceof byte[]) return b64((byte[]) value);
        if (value instanceof int[]) return java.util.Arrays.toString((int[]) value);
        if (value instanceof long[]) return java.util.Arrays.toString((long[]) value);
        if (value instanceof double[]) return java.util.Arrays.toString((double[]) value);
        if (value instanceof float[]) return java.util.Arrays.toString((float[]) value);
        if (value instanceof boolean[]) return java.util.Arrays.toString((boolean[]) value);
        if (value instanceof char[]) return new String((char[]) value);
        return java.util.Arrays.deepToString((Object[]) value);
    }
"""
        )
    if not helper_method_defined(source, "b64"):
        inserted.append("b64")
        helper_blocks.append(
            """
    public static String b64(byte[] bytes) {
        byte[] safe = bytes == null ? new byte[0] : bytes;
        return java.util.Base64.getEncoder().encodeToString(safe);
    }
"""
        )
    if not helper_method_defined(source, "jsonEscape") and ("printResult" in inserted):
        inserted.append("jsonEscape")
        helper_blocks.append(
            r"""
    public static String jsonEscape(String value) {
        String text = value == null ? "" : value;
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            switch (ch) {
                case '\\': out.append("\\\\"); break;
                case '"': out.append("\\\""); break;
                case '\n': out.append("\\n"); break;
                case '\r': out.append("\\r"); break;
                case '\t': out.append("\\t"); break;
                default:
                    if (ch < 0x20) out.append(String.format("\\u%04x", (int) ch));
                    else out.append(ch);
            }
        }
        return out.toString();
    }
"""
        )
    if not helper_blocks:
        return {"status": "already_present", "inserted_helpers": [], "source": source}
    completed = insert_helpers_into_eviprobe(source, "\n".join(helper_blocks))
    if completed == source:
        return {"status": "insertion_failed", "inserted_helpers": inserted, "source": source}
    return {
        "status": "inserted",
        "inserted_helpers": inserted,
        "source_sha256": sha256_text(completed),
        "source": completed,
    }


def helper_method_defined(source: str, name: str) -> bool:
    return re.search(
        rf"\b(?:public|private|protected)?\s*(?:static\s+)?[A-Za-z_$][\w$<>\[\].?,\s]*\s+{re.escape(name)}\s*\(",
        source or "",
    ) is not None


def insert_helpers_into_eviprobe(source: str, helpers: str) -> str:
    text = source or ""
    class_match = re.search(r"\bpublic\s+class\s+EviProbe\b[^{]*\{", text)
    if not class_match:
        return text
    depth = 0
    for index in range(class_match.end() - 1, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:index] + "\n" + helpers.rstrip() + "\n" + text[index:]
    return text


def replace_main_body(source: str, probe_body: str) -> str:
    match = MAIN_RE.search(source or "")
    if not match:
        return source
    brace_index = match.end() - 1
    depth = 0
    for index in range(brace_index, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                main_body = "\n".join(
                    [
                        'java.nio.file.Path work = java.nio.file.Paths.get(args.length > 0 ? args[0] : ".").toAbsolutePath();',
                        "java.nio.file.Files.createDirectories(work);",
                        probe_body,
                    ]
                )
                replacement = "{\n" + indent(main_body, 8) + "\n    }"
                return source[:brace_index] + replacement + source[index + 1 :]
    return source


def compile_and_run_probe_source(source: str, *, timeout_sec: int, keep_work: bool) -> dict[str, Any]:
    if not shutil.which("javac") or not shutil.which("java"):
        return {"status": "toolchain_missing", "compile": {}, "execution": {}}
    work_root = allocate_probe_work_root()
    try:
        source_path = work_root / "EviProbe.java"
        source_path.write_text(source, encoding="utf-8", newline="\n")
        compile_proc = subprocess.run(
            ["javac", "-encoding", "UTF-8", source_path.name],
            cwd=str(work_root),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        compile_info = proc_info(compile_proc)
        if compile_proc.returncode != 0:
            return {"status": "compile_failed", "compile": compile_info, "execution": {}, "work_root": str(work_root.resolve())}
        probe_work = work_root / "work"
        run_proc = subprocess.run(
            ["java", "-cp", ".", "EviProbe", str(probe_work.resolve())],
            cwd=str(work_root),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=minimal_java_env(),
            check=False,
        )
        execution = proc_info(run_proc)
        execution["parsed"] = parse_probe_output(run_proc.stdout)
        return {
            "status": "executed" if run_proc.returncode == 0 and isinstance(execution["parsed"], dict) else "execution_failed",
            "compile": compile_info,
            "execution": execution,
            "work_root": str(work_root.resolve()),
        }
    except subprocess.TimeoutExpired as exc:
        return {"status": "timeout", "compile": {}, "execution": {"timeout": True, "cmd": exc.cmd}, "work_root": str(work_root.resolve())}
    finally:
        if not keep_work:
            shutil.rmtree(work_root, ignore_errors=True)


def allocate_probe_work_root() -> Path:
    parents = []
    if os.environ.get("EVICLONE_TMP_DIR"):
        parents.append(Path(os.environ["EVICLONE_TMP_DIR"]))
    parents.extend([Path("eviclone_runs") / "tmp", Path("tmp") / "eviclone_runs"])
    last_error: Exception | None = None
    for parent in parents:
        try:
            parent.mkdir(parents=True, exist_ok=True)
            work_root = parent / f"probe_exec_{uuid.uuid4().hex[:8]}"
            work_root.mkdir(parents=True, exist_ok=False)
            return work_root
        except PermissionError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise PermissionError("no writable probe temp directory")


def write_probe_source(source: str, source_dir: Path, *, pair_id: int, case_id: int, probe_origin: str) -> dict[str, Any]:
    digest = sha256_text(source)
    safe_origin = re.sub(r"[^A-Za-z0-9_.-]+", "_", probe_origin or "probe")
    path = source_dir / f"case_{case_id}_pair_{pair_id}_{safe_origin}_{digest[:16]}_EviProbe.java"
    path.write_text(source, encoding="utf-8", newline="\n")
    return {
        "retained": True,
        "path": str(path.resolve()),
        "sha256": digest,
        "bytes": path.stat().st_size,
        "probe_origin": probe_origin,
    }


def execution_status(execution: dict[str, Any]) -> str:
    status = str(execution.get("status") or "")
    parsed = execution.get("execution", {}).get("parsed") if isinstance(execution.get("execution"), dict) else None
    if status == "executed" and isinstance(parsed, dict) and parsed.get("status") == "executed":
        return "executed"
    if status == "executed":
        return "invalid_probe_output"
    return status or "failed"


def base_record(candidate: dict[str, Any], pair: ClonePair | None) -> dict[str, Any]:
    baseline = coerce_label((candidate.get("graphcodebert_prediction") if candidate else None))
    if baseline is None and pair is not None:
        raw = pair.raw if isinstance(pair.raw, dict) else {}
        baseline = coerce_label(raw.get("graphcodebert_prediction"))
    return {
        "schema_version": "eviclone-probe-synthesis-execution-result/v1",
        "case_id": int_or_none(candidate.get("case_id")),
        "pair": list(candidate_pair_key(candidate)),
        "pair_id": pair.pair_id if pair else None,
        "gold": pair.label if pair else coerce_label(candidate.get("gold")),
        "baseline_label": baseline,
        "probe_mode": candidate.get("probe_mode"),
        "generation_route": candidate.get("generation_route"),
        "risk_tier": candidate.get("risk_tier"),
        "candidate_correct": candidate.get("candidate_correct"),
    }


def candidate_source_artifact(candidate: dict[str, Any]) -> dict[str, Any]:
    context = candidate.get("context_completion") if isinstance(candidate.get("context_completion"), dict) else {}
    return context.get("source_artifact") if isinstance(context.get("source_artifact"), dict) else {}


def load_cards_by_pair(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    result = {}
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(card, dict):
                ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
                key = pair_key(str(ids.get("a") or ""), str(ids.get("b") or ""))
                if key != ("", ""):
                    result[key] = card
    return result


def summarize_probe_records(
    records: list[dict[str, Any]],
    *,
    dataset: Path,
    candidates_jsonl: Path,
    source_cards_jsonl: Path,
    output_jsonl: Path,
    source_dir: Path,
    include_review: bool,
    with_llm_probe: bool,
    resume: bool = False,
    existing_records_reused: int = 0,
    workers: int = 1,
) -> dict[str, Any]:
    statuses = Counter(str(row.get("status") or "unknown") for row in records)
    routes = Counter(str(row.get("generation_route") or "unknown") for row in records)
    modes = Counter(str(row.get("probe_mode") or "unknown") for row in records)
    origins = Counter(str((row.get("probe_generation") or {}).get("origin") or "none") for row in records)
    actual_with_llm_probe = with_llm_probe or origins.get("llm_probe_synthesis", 0) > 0
    benefits = sum(1 for row in records if row.get("benefit") is True)
    harms = sum(1 for row in records if row.get("harm") is True)
    executed = statuses.get("executed", 0)
    summary = {
        "schema_version": "eviclone-probe-synthesis-execution-summary/v1",
        "status": "no_candidates" if not records else "completed_with_warnings" if harms else "completed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "dataset": str(dataset.resolve()),
            "candidates_jsonl": str(candidates_jsonl.resolve()),
            "source_cards_jsonl": str(source_cards_jsonl.resolve()),
        },
        "outputs": {
            "results": str(output_jsonl.resolve()),
            "source_dir": str(source_dir.resolve()),
        },
        "configuration": {
            "include_review": include_review,
            "with_llm_probe": actual_with_llm_probe,
            "requested_with_llm_probe": with_llm_probe,
            "resume": resume,
            "workers": workers,
        },
        "summary": {
            "candidate_count": len(records),
            "existing_records_reused": existing_records_reused,
            "new_records_executed": max(0, len(records) - existing_records_reused),
            "executed": executed,
            "compiled_or_executed": executed + statuses.get("invalid_probe_output", 0),
            "benefit": benefits,
            "harm": harms,
            "net_gain": benefits - harms,
            "dynamic_label_available": sum(1 for row in records if row.get("dynamic_label") in (0, 1)),
            "source_not_ready": statuses.get("source_not_ready", 0),
            "probe_not_generated": statuses.get("probe_not_generated", 0),
            "compile_failed": statuses.get("compile_failed", 0),
            "execution_failed": statuses.get("execution_failed", 0),
            "timeout": statuses.get("timeout", 0),
        },
        "status_counts": sorted_counter(statuses),
        "generation_route_counts": sorted_counter(routes),
        "probe_mode_counts": sorted_counter(modes),
        "probe_origin_counts": sorted_counter(origins),
    }
    return summary


def load_existing_execution_records(path: Path, selected_keys: set[tuple[str, str]]) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    records: dict[tuple[str, str], dict[str, Any]] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            key = execution_record_pair_key(row)
            if key in selected_keys and key != ("", ""):
                records[key] = row
    return records


def execution_record_pair_key(row: dict[str, Any]) -> tuple[str, str]:
    pair = row.get("pair")
    if isinstance(pair, list) and len(pair) >= 2:
        return pair_key(str(pair[0]), str(pair[1]))
    if isinstance(pair, dict):
        left = pair.get("function_id_a") or pair.get("a") or pair.get("left")
        right = pair.get("function_id_b") or pair.get("b") or pair.get("right")
        return pair_key(str(left or ""), str(right or ""))
    return ("", "")


def write_report(path: Path, summary: dict[str, Any]) -> None:
    s = summary["summary"]
    lines = [
        "# Probe Synthesis Execution",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| candidate_count | {s['candidate_count']} |",
        f"| executed | {s['executed']} |",
        f"| dynamic_label_available | {s['dynamic_label_available']} |",
        f"| benefit | {s['benefit']} |",
        f"| harm | {s['harm']} |",
        f"| net_gain | {s['net_gain']} |",
        f"| source_not_ready | {s['source_not_ready']} |",
        f"| probe_not_generated | {s['probe_not_generated']} |",
        f"| compile_failed | {s['compile_failed']} |",
        f"| execution_failed | {s['execution_failed']} |",
        f"| timeout | {s['timeout']} |",
        "",
        "## Status Counts",
        "",
        "| status | count |",
        "| --- | ---: |",
    ]
    for key, value in summary["status_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Probe Origins", "", "| origin | count |", "| --- | ---: |"])
    for key, value in summary["probe_origin_counts"].items():
        lines.append(f"| {key} | {value} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def make_probe_client(
    *,
    model: str,
    base_url: str,
    api_key_env: str,
    api_key: str,
    temperature: float,
) -> ChatClient:
    config = LLMConfig(
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        temperature=temperature,
    )
    return ChatClient(config=config, api_key=config.resolve_api_key(api_key))


def pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((str(a), str(b)))) if a and b else ("", "")


def coerce_label(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed in (0, 1) else None


def is_benefit(base_label: Any, gold: Any, dynamic_label: Any) -> bool:
    return base_label in (0, 1) and gold in (0, 1) and dynamic_label in (0, 1) and base_label != gold and dynamic_label == gold


def is_harm(base_label: Any, gold: Any, dynamic_label: Any) -> bool:
    return base_label in (0, 1) and gold in (0, 1) and dynamic_label in (0, 1) and base_label == gold and dynamic_label != gold


def minimal_java_env() -> dict[str, str]:
    keep = {"PATH", "Path", "PATHEXT", "SystemRoot", "WINDIR", "ComSpec", "TEMP", "TMP", "JAVA_HOME", "JDK_HOME"}
    env = {key: value for key, value in os.environ.items() if key in keep}
    if not any(key.lower() == "path" for key in env):
        env["PATH"] = os.defpath
    return env


def indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in (text or "").strip().splitlines())


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
