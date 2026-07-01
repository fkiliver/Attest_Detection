from __future__ import annotations

import argparse
import binascii
import json
import struct
import zlib
import zipfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("external") / "MRT-OAST"
DEFAULT_REPORT_DIR = Path("eviclone_runs") / "baseline_reproduction"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract MRT-OAST split origindata.z01/.z02/.zip without 7-Zip.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_DIR / "mrt_oast_split_origindata_extraction.json")
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_DIR / "mrt_oast_split_origindata_extraction.md")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = args.repo_root
    output_dir = args.output_dir or root
    parts = [root / "origindata.z01", root / "origindata.z02", root / "origindata.zip"]
    missing_parts = [str(path) for path in parts if not path.exists()]
    if missing_parts:
        summary = {
            "schema_version": "eviclone-mrt-oast-split-origindata-extraction/v1",
            "status": "missing_archive_part",
            "missing_parts": missing_parts,
        }
        write_outputs(summary, args.report_json, args.report_md)
        return 2

    part_sizes = [path.stat().st_size for path in parts]
    segment_offsets = [0, part_sizes[0], part_sizes[0] + part_sizes[1]]
    archive_bytes = b"".join(path.read_bytes() for path in parts)
    rows = []
    status = "extracted"
    with zipfile.ZipFile(root / "origindata.zip") as handle:
        infos = handle.infolist()
        for info in infos:
            row = extract_member(
                archive_bytes=archive_bytes,
                info=info,
                output_dir=output_dir,
                segment_offsets=segment_offsets,
                overwrite=args.overwrite,
            )
            rows.append(row)
            if row["status"] not in {"directory", "extracted", "exists"}:
                status = "partial"

    summary = {
        "schema_version": "eviclone-mrt-oast-split-origindata-extraction/v1",
        "status": status,
        "archive_parts": [{"path": str(path), "size_bytes": path.stat().st_size} for path in parts],
        "output_dir": str(output_dir),
        "members": len(rows),
        "status_counts": count_statuses(rows),
        "files": rows,
        "note": (
            "The MRT-OAST archive is a split zip with a PK\\x07\\x08 marker at the start of .z01. "
            "This extractor uses central-directory metadata from origindata.zip and local headers from the "
            "z01+z02+zip byte stream."
        ),
    }
    write_outputs(summary, args.report_json, args.report_md)
    print(json.dumps({"status": status, "output": str(args.report_json), "report": str(args.report_md)}, sort_keys=True))
    return 0 if status == "extracted" else 2


def extract_member(
    *,
    archive_bytes: bytes,
    info: zipfile.ZipInfo,
    output_dir: Path,
    segment_offsets: list[int],
    overwrite: bool,
) -> dict[str, Any]:
    name = info.filename
    path = output_dir / name
    if name.endswith("/"):
        path.mkdir(parents=True, exist_ok=True)
        return {"path": name, "status": "directory", "size_bytes": 0}
    if path.exists() and not overwrite:
        return {"path": name, "status": "exists", "size_bytes": path.stat().st_size}

    try:
        compressed, resolved_offset = compressed_payload(
            archive_bytes=archive_bytes,
            central_offset=info.header_offset,
            segment_offsets=segment_offsets,
            expected_name=name,
            expected_compressed_size=info.compress_size,
        )
        if info.compress_type == zipfile.ZIP_STORED:
            data = compressed
        elif info.compress_type == zipfile.ZIP_DEFLATED:
            data = zlib.decompress(compressed, -15)
        else:
            return {"path": name, "status": "unsupported_compression", "compression": info.compress_type}
        crc = binascii.crc32(data) & 0xFFFFFFFF
        if crc != info.CRC:
            return {"path": name, "status": "crc_mismatch", "expected_crc": info.CRC, "actual_crc": crc}
        if len(data) != info.file_size:
            return {"path": name, "status": "size_mismatch", "expected_size": info.file_size, "actual_size": len(data)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {"path": name, "status": "extracted", "size_bytes": len(data), "resolved_offset": resolved_offset}
    except Exception as exc:  # pragma: no cover - diagnostic artifact path
        return {"path": name, "status": "failed", "error": repr(exc)}


def compressed_payload(
    *,
    archive_bytes: bytes,
    central_offset: int,
    segment_offsets: list[int],
    expected_name: str,
    expected_compressed_size: int,
) -> tuple[bytes, int]:
    errors: list[str] = []
    for offset in candidate_offsets(central_offset, segment_offsets):
        try:
            return read_payload_at_offset(
                archive_bytes=archive_bytes,
                offset=offset,
                expected_name=expected_name,
                expected_compressed_size=expected_compressed_size,
            )
        except ValueError as exc:
            errors.append(f"{offset}: {exc}")
    raise ValueError("; ".join(errors))


def candidate_offsets(central_offset: int, segment_offsets: list[int]) -> list[int]:
    candidates = [central_offset + segment_offset for segment_offset in segment_offsets]
    return list(dict.fromkeys(offset for offset in candidates if offset >= 0))


def read_payload_at_offset(
    *,
    archive_bytes: bytes,
    offset: int,
    expected_name: str,
    expected_compressed_size: int,
) -> tuple[bytes, int]:
    if archive_bytes[offset : offset + 4] != b"PK\x03\x04":
        raise ValueError(f"missing local header at offset {offset}")
    (
        _sig,
        _ver,
        _flag,
        _comp,
        _mtime,
        _mdate,
        _crc,
        compressed_size,
        _uncompressed_size,
        name_len,
        extra_len,
    ) = struct.unpack_from("<IHHHHHIIIHH", archive_bytes, offset)
    name_start = offset + 30
    name = archive_bytes[name_start : name_start + name_len].decode("utf-8", errors="replace")
    if name != expected_name:
        raise ValueError(f"local header name mismatch: expected {expected_name!r}, got {name!r}")
    data_start = name_start + name_len + extra_len
    if compressed_size == 0 and expected_compressed_size > 0:
        compressed_size = expected_compressed_size
    return archive_bytes[data_start : data_start + compressed_size], offset


def count_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def write_outputs(summary: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(summary), encoding="utf-8")


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# MRT-OAST Split Origindata Extraction",
        "",
        f"Status: `{summary['status']}`",
        "",
        summary.get("note", ""),
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in summary.get("status_counts", {}).items():
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Files", "", "| Path | Status | Size |", "| --- | --- | ---: |"])
    for row in summary.get("files", []):
        lines.append(f"| `{row['path']}` | `{row['status']}` | {row.get('size_bytes', '')} |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
