#!/usr/bin/env python3
"""Merge four-level Terwilliger chunk outputs.

Usage:
  python merge_four_level_chunks.py out_four_w12_*/four_level_chunk_profile_hashes.csv \
    --out merged_w12
"""

from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="four_level_chunk_profile_hashes.csv files")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    frames = []
    for f in args.files:
        frames.append(pd.read_csv(f))
    df = pd.concat(frames, ignore_index=True)

    group_cols = ["shell", "four_profile_sha256"]
    first_cols = [
        "first_size", "second_size", "third_size", "fourth_size",
        "source_three_profile_id", "representative_d_mask_compressed",
    ]

    grouped = df.groupby(group_cols, as_index=False).agg(
        global_fiber_count=("chunk_fiber_count", "sum"),
        occurrences=("chunk_fiber_count", "count"),
        **{c: (c, "first") for c in first_cols if c in df.columns}
    )

    merged_path = out / "four_level_global_profile_hashes.csv"
    grouped.to_csv(merged_path, index=False)

    report = {
        "status": "FOUR_LEVEL_CHUNKS_MERGED",
        "input_files": [str(x) for x in args.files],
        "input_file_sha256": {str(x): sha256_file(Path(x)) for x in args.files},
        "raw_rows": int(len(df)),
        "unique_profile_hashes": int(len(grouped)),
        "merged_csv": str(merged_path),
        "merged_csv_sha256": sha256_file(merged_path),
    }
    report["certificate_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (out / "four_level_merge_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
