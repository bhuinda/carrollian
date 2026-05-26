#!/usr/bin/env python3
"""
Full/chunked four-level Terwilliger profile derivation.

Input:
  three_level_terwilliger_profiles.csv

Given a three-level representative (A,B,C), this scans every D subset of C
and records the four-level shell profile

  ( |x∩A|, |x∩B|, |x∩D| )

over all shell words x of weight w in the extended binary Golay code.

This is the actual full-run version of the four-level pilot.

Typical runs:

  # Pilot
  python derive_four_level_terwilliger_profiles_full.py three_level_terwilliger_profiles.csv \
    --shell 12 --max-rest 4 --out out_four_pilot_w12

  # Chunk by profile index
  python derive_four_level_terwilliger_profiles_full.py three_level_terwilliger_profiles.csv \
    --shell 16 --start 0 --stop 250 --out out_four_w16_000_250

  # Full shell, offline
  python derive_four_level_terwilliger_profiles_full.py three_level_terwilliger_profiles.csv \
    --shell 12 --out out_four_w12_full

  # Write local profile vectors as .npz for later positivity/SOS
  python derive_four_level_terwilliger_profiles_full.py three_level_terwilliger_profiles.csv \
    --shell 12 --start 0 --stop 250 --write-vectors --out out_four_w12_000_250

Notes:
  * Full table budget from the current three-level table is 79,552,853 subsets per shell.
  * This script is CPU/RAM heavy for rows with large rest_size. Chunked runs are recommended.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def wt(x: int) -> int:
    return int(x).bit_count()


def bits_to_int(bits) -> int:
    x = 0
    for i, b in enumerate(bits):
        if b:
            x |= 1 << i
    return x


def rm13_h8() -> list[int]:
    pts = list(product([0, 1], repeat=3))
    code = []
    for a in product([0, 1], repeat=3):
        for b in [0, 1]:
            code.append(bits_to_int([(sum(ai * pi for ai, pi in zip(a, p)) + b) % 2 for p in pts]))
    return sorted(set(code))


def direct_sum(codes: list[list[int]], lengths: list[int]) -> list[int]:
    res = [0]
    shift = 0
    for C, L in zip(codes, lengths):
        res = [r | (c << shift) for r in res for c in C]
        shift += L
    return sorted(set(res))


def vector_from_one_based_support(supp: list[int]) -> int:
    x = 0
    for j in supp:
        x |= 1 << (j - 1)
    return x


def type_ii_neighbor(C: list[int], v: int) -> list[int]:
    C0 = [c for c in C if wt(c & v) % 2 == 0]
    return sorted(set(C0 + [c ^ v for c in C0]))


def build_golay() -> list[int]:
    H8 = rm13_h8()
    C = direct_sum([H8, H8, H8], [8, 8, 8])
    for supp in [
        [2, 4, 9, 10, 12, 13, 14, 16, 17, 18, 20, 22],
        [3, 4, 9, 13, 15, 16, 19, 20],
        [2, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23],
    ]:
        C = type_ii_neighbor(C, vector_from_one_based_support(supp))
    return C


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                fields.append(k)
                seen.add(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def popcount_array(width: int) -> np.ndarray:
    return np.array([i.bit_count() for i in range(1 << width)], dtype=np.uint8)


def superset_zeta(values: np.ndarray, width: int) -> np.ndarray:
    values = values.copy()
    for bit in range(width):
        step = 1 << bit
        values = values.reshape(-1, step * 2)
        values[:, :step] += values[:, step: step * 2]
        values = values.reshape(-1)
    return values


def subset_zeta(values: np.ndarray, width: int) -> np.ndarray:
    values = values.copy()
    for bit in range(width):
        step = 1 << bit
        values = values.reshape(-1, step * 2)
        values[:, step: step * 2] += values[:, :step]
        values = values.reshape(-1)
    return values


def positions_from_rest(first_mask: int, second_mask: int) -> list[int]:
    used = first_mask | second_mask
    return [i for i in range(24) if not ((used >> i) & 1)]


def compress_mask(mask: int, positions: list[int]) -> int:
    out = 0
    for small, coord in enumerate(positions):
        if (mask >> coord) & 1:
            out |= 1 << small
    return out


def exact_intersection_components(
    residuals: list[int],
    width: int,
    max_l: int,
    pc: np.ndarray,
) -> list[np.ndarray]:
    """
    For every D subset of a width-set, compute counts of residuals R with |R∩D|=l.

    Uses zeta transforms:
      sup[S] = # residuals R with S subset R,
      then inclusion-exclusion from "contains a chosen m-subset of D" to exact intersections.
    """
    N = 1 << width
    values = np.zeros(N, dtype=np.uint16)
    if residuals:
        np.add.at(values, np.array(residuals, dtype=np.uint32), 1)

    sup = superset_zeta(values, width).astype(np.uint32)

    c_layers: list[np.ndarray] = []
    for m in range(max_l + 1):
        layer = np.zeros(N, dtype=np.uint32)
        layer[pc == m] = sup[pc == m]
        c_layers.append(subset_zeta(layer, width).astype(np.int64))

    exact: list[np.ndarray] = []
    for l in range(max_l + 1):
        total = np.zeros(N, dtype=np.int64)
        for m in range(l, max_l + 1):
            coef = ((-1) ** (m - l)) * math.comb(m, l)
            if coef:
                total += coef * c_layers[m]
        if total.min() < 0:
            raise RuntimeError("negative exact-intersection component: inclusion-exclusion failure")
        exact.append(total.astype(np.uint16))
    return exact


def recover_sizes_from_profile(profile: np.ndarray, shell: int, shell_count: int) -> tuple[int, int, int, int]:
    """Recover color sizes (A,B,D,E) from profile moments."""
    arr = profile.reshape((shell + 1, shell + 1, shell + 1))
    j = np.arange(shell + 1)[:, None, None]
    k = np.arange(shell + 1)[None, :, None]
    l = np.arange(shell + 1)[None, None, :]
    den = shell_count * shell
    n1 = int((24 * int((arr * j).sum())) // den)
    n2 = int((24 * int((arr * k).sum())) // den)
    n3 = int((24 * int((arr * l).sum())) // den)
    n4 = 24 - n1 - n2 - n3
    return n1, n2, n3, n4


def local_four_level_profiles(row: dict[str, Any], shell_words: list[int], pc_cache: dict[int, np.ndarray]) -> tuple[list[dict[str, Any]], np.ndarray | None, dict[str, Any]]:
    shell = int(row["shell"])
    first_mask = int(row["first_representative_mask"])
    second_mask = int(row["second_representative_mask"])
    rest_positions = positions_from_rest(first_mask, second_mask)
    width = len(rest_positions)
    N = 1 << width

    families: dict[tuple[int, int], list[int]] = {}
    used = first_mask | second_mask
    for word in shell_words:
        j = wt(word & first_mask)
        k = wt(word & second_mask)
        residual = compress_mask(word & ~used, rest_positions)
        families.setdefault((j, k), []).append(residual)

    layout: list[tuple[int, int, int]] = []
    arrays: list[np.ndarray] = []

    pc = pc_cache[width]
    for (j, k), residuals in sorted(families.items()):
        max_l = min(shell - j - k, width)
        comps = exact_intersection_components(residuals, width, max_l, pc)
        for l, arr in enumerate(comps):
            layout.append((j, k, l))
            arrays.append(arr)

    if not arrays:
        return [], None, {"width": width, "subsets": N, "layout_components": 0}

    M = np.vstack(arrays).T  # shape: D-subsets x active components
    unique_rows, first_idx, counts = np.unique(M, axis=0, return_index=True, return_counts=True)

    full_len = (shell + 1) ** 3
    profiles = np.zeros((len(unique_rows), full_len), dtype=np.uint16)

    for row_idx, urow in enumerate(unique_rows):
        full = profiles[row_idx]
        for (j, k, l), val in zip(layout, urow):
            full[(j * (shell + 1) + k) * (shell + 1) + l] = val

    entries: list[dict[str, Any]] = []
    shell_count = 2576 if shell == 12 else 759

    for i, full in enumerate(profiles):
        h = hashlib.sha256(full.tobytes()).hexdigest()
        n1, n2, n3, n4 = recover_sizes_from_profile(full.astype(np.int64), shell, shell_count)
        entries.append({
            "shell": shell,
            "source_three_profile_id": int(row["profile_id"]),
            "source_first_size": int(row["first_size"]),
            "source_second_size": int(row["second_size"]),
            "source_rest_size": int(row["rest_size"]),
            "four_profile_sha256": h,
            "local_fiber_count": int(counts[i]),
            "representative_d_mask_compressed": int(first_idx[i]),
            "first_size": n1,
            "second_size": n2,
            "third_size": n3,
            "fourth_size": n4,
        })

    info = {"width": width, "subsets": N, "layout_components": len(layout), "local_unique": len(entries)}
    return entries, profiles, info


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="three_level_terwilliger_profiles.csv")
    ap.add_argument("--shell", type=int, required=True, choices=[12, 16])
    ap.add_argument("--start", type=int, default=0, help="start index after sorting profiles by profile_id")
    ap.add_argument("--stop", type=int, default=None, help="stop index after sorting profiles by profile_id")
    ap.add_argument("--profile-ids", default=None, help="comma-separated profile ids; overrides start/stop if supplied")
    ap.add_argument("--max-rest", type=int, default=None, help="only process rows with rest_size <= this")
    ap.add_argument("--out", required=True)
    ap.add_argument("--write-vectors", action="store_true", help="write local unique profile vectors to compressed npz")
    ap.add_argument("--progress-every", type=int, default=50)
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    sub = df[df.shell == args.shell].sort_values("profile_id").reset_index(drop=True)

    if args.profile_ids:
        ids = {int(x) for x in args.profile_ids.split(",") if x.strip()}
        sub = sub[sub.profile_id.isin(ids)].reset_index(drop=True)
        start, stop = 0, len(sub)
    else:
        start = args.start
        stop = args.stop if args.stop is not None else len(sub)
        sub = sub.iloc[start:stop].reset_index(drop=True)

    if args.max_rest is not None:
        sub = sub[sub.rest_size <= args.max_rest].reset_index(drop=True)

    if len(sub) == 0:
        raise SystemExit("no rows selected")

    C = build_golay()
    shell_words = [c for c in C if wt(c) == args.shell]
    if args.shell == 12 and len(shell_words) != 2576:
        raise RuntimeError("bad G24 shell 12")
    if args.shell == 16 and len(shell_words) != 759:
        raise RuntimeError("bad G24 shell 16")

    pc_cache = {w: popcount_array(w) for w in range(25)}

    all_entries: list[dict[str, Any]] = []
    profile_row_records: list[dict[str, Any]] = []
    vector_blocks: list[np.ndarray] = []
    vector_hashes: list[str] = []

    t0 = time.time()
    total_subsets = 0

    for n, row in enumerate(sub.to_dict(orient="records"), 1):
        entries, profiles, info = local_four_level_profiles(row, shell_words, pc_cache)
        all_entries.extend(entries)
        total_subsets += info["subsets"]

        profile_row_records.append({
            "shell": args.shell,
            "source_three_profile_id": int(row["profile_id"]),
            "rest_size": int(row["rest_size"]),
            "subsets_scanned": info["subsets"],
            "layout_components": info["layout_components"],
            "local_unique_four_profiles": info["local_unique"],
        })

        if args.write_vectors and profiles is not None:
            vector_blocks.append(profiles)
            vector_hashes.extend([e["four_profile_sha256"] for e in entries])

        if args.progress_every and n % args.progress_every == 0:
            print(f"processed {n}/{len(sub)} rows; local entries={len(all_entries)}; elapsed={time.time() - t0:.1f}s")

    # Aggregate hash counts within this chunk.
    agg: dict[tuple[int, str], dict[str, Any]] = {}
    for e in all_entries:
        key = (e["shell"], e["four_profile_sha256"])
        if key not in agg:
            agg[key] = dict(e)
            agg[key]["chunk_fiber_count"] = 0
            # representative source fields kept from first occurrence
        agg[key]["chunk_fiber_count"] += int(e["local_fiber_count"])

    agg_entries = list(agg.values())

    write_csv(out / "four_level_local_profiles.csv", all_entries)
    write_csv(out / "four_level_chunk_profile_hashes.csv", agg_entries)
    write_csv(out / "four_level_source_rows.csv", profile_row_records)

    if args.write_vectors and vector_blocks:
        profiles_all = np.vstack(vector_blocks)
        np.savez_compressed(
            out / "four_level_local_profile_vectors.npz",
            profiles=profiles_all,
            hashes=np.array(vector_hashes, dtype="U64"),
            shell=np.array([args.shell], dtype=np.int16),
        )

    report = {
        "status": "FOUR_LEVEL_CHUNK_COMPLETE",
        "input_csv": str(csv_path),
        "input_csv_sha256": sha256_file(csv_path),
        "shell": args.shell,
        "start": start,
        "stop": stop,
        "profile_ids": args.profile_ids,
        "max_rest": args.max_rest,
        "rows_processed": int(len(sub)),
        "fourth_color_subsets_scanned": int(total_subsets),
        "local_profile_entries": int(len(all_entries)),
        "unique_profile_hashes_in_chunk": int(len(agg_entries)),
        "write_vectors": bool(args.write_vectors),
        "elapsed_seconds": time.time() - t0,
    }
    report["certificate_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    write_json(out / "four_level_chunk_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
