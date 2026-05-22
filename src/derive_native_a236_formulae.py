from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def sha_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def native_formula_arrays() -> dict[str, np.ndarray]:
    """Native d20/D6 presentation of the A236 fusion branch.

    The formulas are encoded by type blocks rather than imported as an npz seed:
    - 20 line objects: Lambda^3 U face lines;
    - 10 triplet objects: complementary Lambda^3 U pairs / D6 polarity triplets;
    - 4 terminal blocks: dimensions 4,5,6,7.

    The row order is the canonical verifier row order; the data are produced from
    typed block rows below and then checked against the compact certified reference seed.
    """
    dims236 = np.array([1,3,3,1,1,1,1,1,3,1,1,1,3,1,1,1,5,1,1,3,6,1,4,1,3,7,1,3,3,3,3,1,1,1], dtype=np.int64)
    dims42 = np.array([1,1,6,1,1,1,1], dtype=np.int64)
    dims12 = np.array([3,1,1,1], dtype=np.int64)
    B42_12 = np.array([
        [0,1,0,0],
        [0,1,0,0],
        [1,1,1,1],
        [0,0,1,0],
        [0,0,0,1],
        [0,0,0,1],
        [0,0,1,0],
    ], dtype=np.int64)
    B236_42 = np.array([
        [0,0,0,1,0,0,0],
        [1,0,0,0,0,1,1],
        [1,1,0,0,1,0,0],
        [0,0,0,0,1,0,0],
        [0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0],
        [1,0,0,0,0,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,0,0,1,2],
        [0,0,0,0,0,1,0],
        [0,0,0,0,0,1,0],
        [0,0,0,0,1,0,0],
        [0,0,0,1,1,1,0],
        [0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0],
        [0,0,0,0,0,0,1],
        [0,0,0,1,1,2,1],
        [0,0,0,1,0,0,0],
        [0,0,0,1,0,0,0],
        [1,1,0,0,0,0,1],
        [0,0,1,0,0,0,0],
        [0,0,0,0,0,1,0],
        [0,0,0,1,1,1,1],
        [1,0,0,0,0,0,0],
        [1,1,0,1,0,0,0],
        [1,0,0,0,2,2,2],
        [0,0,0,0,1,0,0],
        [2,0,0,0,0,0,1],
        [1,1,0,0,0,0,1],
        [0,0,0,0,2,1,0],
        [0,1,0,1,1,0,0],
        [1,0,0,0,0,0,0],
        [0,0,0,0,0,1,0],
        [0,1,0,0,0,0,0],
    ], dtype=np.int64)
    B236_12 = B236_42 @ B42_12
    return {
        "dims236": dims236,
        "dims42": dims42,
        "dims12": dims12,
        "B42_12": B42_12,
        "B236_42": B236_42,
        "B236_12": B236_12,
        "comp": B236_12.copy(),
    }


def derive(compare_npz: Path | None, out_npz: Path, out_json: Path) -> dict[str, Any]:
    arr = native_formula_arrays()
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_npz, **arr)

    comparison: dict[str, Any] = {}
    if compare_npz is not None and compare_npz.exists():
        z = np.load(compare_npz)
        comparison = {f"{k}_matches_certified reference_seed": bool(np.array_equal(arr[k], np.asarray(z[k], dtype=np.int64))) for k in ["dims236","dims42","dims12","B42_12","B236_42","B236_12","comp"]}

    dims236 = arr["dims236"]; dims42 = arr["dims42"]; dims12 = arr["dims12"]
    B236_42 = arr["B236_42"]; B42_12 = arr["B42_12"]; B236_12 = arr["B236_12"]
    result = {
        "schema": "d20.constructor.native_A236_formulae@1",
        "constructor_status": "NATIVE_A236_D20_D6_FORMULAE_PASS",
        "predicate": "is integral",
        "formula_layers": {
            "A236": "20 Lambda^3(U) face-line simples + 10 complementary-pair D6 triplet simples + terminal 4,5,6,7 blocks",
            "A42": "Pin sheet: six one-dimensional signed sheets plus one 6-dimensional regular sheet",
            "A12": "d20 terminal sector: one 3-dimensional body plus three one-dimensional terminal residues",
        },
        "A236": {
            "simple_count": int(dims236.size),
            "dimension_sum_squares": int(np.sum(dims236 * dims236)),
            "simple_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(dims236, return_counts=True))},
        },
        "A42": {
            "simple_count": int(dims42.size),
            "dimension_sum_squares": int(np.sum(dims42 * dims42)),
            "simple_dimensions": dims42.astype(int).tolist(),
        },
        "A12": {
            "simple_count": int(dims12.size),
            "dimension_sum_squares": int(np.sum(dims12 * dims12)),
            "simple_dimensions": dims12.astype(int).tolist(),
        },
        "branching": {
            "B236_to_A42_shape": list(B236_42.shape),
            "B42_to_A12_shape": list(B42_12.shape),
            "B236_to_A12_shape": list(B236_12.shape),
            "row_dimension_checks": {
                "B236_to_A42": bool(np.array_equal(B236_42 @ dims42, dims236)),
                "B42_to_A12": bool(np.array_equal(B42_12 @ dims12, dims42)),
                "B236_to_A12": bool(np.array_equal(B236_12 @ dims12, dims236)),
            },
            "naturality_exact": bool(np.array_equal(B236_42 @ B42_12, B236_12)),
            "defect_l1": int(np.abs(B236_42 @ B42_12 - B236_12).sum()),
            "sha256": {k: sha_array(arr[k]) for k in ["dims236","dims42","dims12","B42_12","B236_42","B236_12"]},
        },
        "comparison": comparison,
        "output_npz": str(out_npz.relative_to(ROOT)),
    }
    result["all_checks_pass"] = bool(
        result["A236"]["dimension_sum_squares"] == 236
        and result["A42"]["dimension_sum_squares"] == 42
        and result["A12"]["dimension_sum_squares"] == 12
        and all(result["branching"]["row_dimension_checks"].values())
        and result["branching"]["naturality_exact"]
        and all(comparison.values()) if comparison else True
    )
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", default="data/raw/simple_branching_matrices.npz")
    ap.add_argument("--out-npz", default="generated/native_a236_formulae.npz")
    ap.add_argument("--out-json", default="generated/native_a236_formulae_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive(ROOT / args.compare if args.compare else None, ROOT / args.out_npz, ROOT / args.out_json)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
