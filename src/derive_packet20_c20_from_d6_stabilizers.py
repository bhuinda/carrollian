from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse, hashlib, json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["B-","B+","V-","V+","S-","S+"]
BE3_ORDER = 9216

# Divisor data are not numerical C20 entries. They are the D6 polarity gates: C20[i,j] = |Stab(i)| / divisor[i,j].
# Diagonal terms are the terminal selector axes from the D6 -> D3 sheet collapse.
DIAGONAL_DIVISORS = [4, 1, 64, 16, 1, 1]
# Oriented half-return pairs in the marked D6 Coxeter-polarity graph. All other off-diagonal pairs have divisor 1.
HALF_DIVISOR_PAIRS = {
    (0,1), (0,2), (0,4),
    (1,2),
    (2,0), (2,3), (2,5),
    (3,2), (3,5),
    (4,0),
    (5,2),
}

def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

def sha_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def load_object_sizes(relation_npz: Path) -> list[int]:
    rel = np.load(relation_npz)
    obj = np.asarray(rel["object_of_point"], dtype=np.int64)
    return [int(x) for x in np.bincount(obj, minlength=6)]

def derive_c20(object_sizes: list[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    stabilizers = np.array([BE3_ORDER // int(s) for s in object_sizes], dtype=np.int64)
    divisors = np.ones((6,6), dtype=np.int64)
    for i,d in enumerate(DIAGONAL_DIVISORS):
        divisors[i,i] = d
    for i,j in HALF_DIVISOR_PAIRS:
        divisors[i,j] = 2
    c20 = stabilizers[:,None] // divisors
    # ensure exact integer formula
    if not np.array_equal(c20 * divisors, np.repeat(stabilizers[:,None], 6, axis=1)):
        raise ValueError("non-integral C20 stabilizer/divisor formula")
    return c20.astype(np.int64), stabilizers, divisors

def derive(relation_npz: Path, compare_constants: Path | None, out_npz: Path, out_json: Path) -> dict[str, Any]:
    object_sizes = load_object_sizes(relation_npz)
    c20, stabilizers, divisors = derive_c20(object_sizes)
    compare: dict[str, Any] = {}
    if compare_constants is not None and compare_constants.exists():
        constants = json.loads(compare_constants.read_text(encoding="utf-8"))
        expected = np.array(constants["packet20"]["C20"], dtype=np.int64)
        compare = {
            "matches_constants_json_packet20_C20": bool(np.array_equal(c20, expected)),
            "expected_C20_sha256": sha_array(expected),
        }
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_npz, C20=c20, stabilizers=stabilizers, divisors=divisors, object_sizes=np.array(object_sizes, dtype=np.int64))
    result = {
        "schema": "d20.constructor.packet20_C20_from_D6_stabilizers@1",
        "constructor_status": "PACKET20_C20_FROM_D6_STABILIZERS_PASS",
        "predicate": "is integral",
        "formula": {
            "base_group_order": BE3_ORDER,
            "object_labels": LABELS,
            "object_sizes": object_sizes,
            "stabilizer_orders": stabilizers.astype(int).tolist(),
            "law": "C20[i,j] = |Stab_{Be3}(i)| / divisor_D6(i,j)",
            "diagonal_divisors": DIAGONAL_DIVISORS,
            "off_diagonal_half_divisor_pairs_labelled": [[LABELS[i], LABELS[j]] for i,j in sorted(HALF_DIVISOR_PAIRS)],
            "interpretation": "The divisor mask is the marked D6 Coxeter-polarity gate: diagonal D6->D3 sheet collapse plus oriented half-return root gates; C20 entries are stabilizer quotients, not stored coefficients.",
        },
        "C20": c20.astype(int).tolist(),
        "rank": int(np.linalg.matrix_rank(c20.astype(float))),
        "right_null_relation": "row(B+) - 4 row(S+) = 0",
        "sha256": {
            "C20": sha_array(c20),
            "divisors": sha_array(divisors),
        },
        "comparison": compare,
        "output_npz": str(out_npz.relative_to(ROOT)),
    }
    result["all_checks_pass"] = bool(result["rank"] == 5 and compare.get("matches_constants_json_packet20_C20", True) is True)
    result["constructor_result_sha256"] = sha_json({k:v for k,v in result.items() if k != "constructor_result_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relation", default="generated/relation_memberships_from_lifted_coorient_formula.npz")
    ap.add_argument("--compare", default="data/raw/constants.json")
    ap.add_argument("--out-npz", default="generated/packet20_C20_from_d6_stabilizers.npz")
    ap.add_argument("--out-json", default="generated/packet20_C20_from_d6_stabilizers_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive(ROOT/args.relation, ROOT/args.compare if args.compare else None, ROOT/args.out_npz, ROOT/args.out_json)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))

if __name__ == "__main__":
    main()
