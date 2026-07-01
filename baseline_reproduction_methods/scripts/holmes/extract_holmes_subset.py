from __future__ import annotations

import argparse
import json
import re
import tarfile
from pathlib import Path


DATA_RE = re.compile(r"^(?P<prefix>[^/]+)/(train|val|test)/processed/data_(?P<idx>\d+)\.pt$")
RAW_RE = re.compile(r"^[^/]+/(train|val|test)/raw/[^/]+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract a HOLMES processed-data subset from a released tarball.")
    parser.add_argument("--tar", type=Path, required=True)
    parser.add_argument("--prefix", required=True, help="Archive prefix such as bcbEU or gcjEU.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int, required=True, help="Maximum processed data_*.pt files per split; 0 means full split.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    extracted: dict[str, int] = {"raw": 0, "processed": 0}
    split_counts = {"train": 0, "val": 0, "test": 0}
    output_root = args.output_dir.resolve()
    with tarfile.open(args.tar, "r:gz") as archive:
        for member in archive:
            name = member.name.replace("\\", "/")
            if not name.startswith(f"{args.prefix}/"):
                continue
            should_extract = False
            data_match = DATA_RE.match(name)
            if data_match and data_match.group("prefix") == args.prefix:
                idx = int(data_match.group("idx"))
                should_extract = args.limit <= 0 or idx < args.limit
                if should_extract:
                    split_counts[name.split("/")[1]] += 1
                    extracted["processed"] += 1
            elif RAW_RE.match(name):
                should_extract = True
                extracted["raw"] += 1
            elif member.isdir():
                should_extract = True
            if not should_extract:
                continue
            target = (args.output_dir / name).resolve()
            if not str(target).startswith(str(output_root)):
                raise RuntimeError(f"Refusing unsafe archive member: {name}")
            archive.extract(member, path=args.output_dir)
    manifest = {
        "schema_version": "eviclone-holmes-subset-extract/v1",
        "tar": str(args.tar),
        "prefix": args.prefix,
        "output_dir": str(args.output_dir),
        "limit": args.limit,
        "extracted": extracted,
        "split_counts": split_counts,
    }
    manifest_path = args.output_dir / f"{args.prefix}_subset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), **manifest}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
