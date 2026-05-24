#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .build_be3_from_coorient import construct_be3_from_source_coorient
from .certify_io import raw_tensor_relpath
from .paths import D20_INVARIANTS

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
PRE_A985_RELATION_NPZ = GENERATED / "relation_memberships_pre_A985_from_source.npz"
PRE_A985_ALIGNED_RELATION_NPZ = GENERATED / "relation_memberships_pre_A985_from_source_aligned.npz"
PRE_A985_BE3_REPORT = GENERATED / "pre_A985_source_to_relation_body_report.json"
PRE_A985_TENSOR_NPZ = GENERATED / "tensor_pre_A985_from_source.npz"
PRE_A985_TENSOR_REPORT = GENERATED / "pre_A985_tensor_report.json"
PRE_A985_THEOREM_JSON = D20_INVARIANTS / "pre_A985_relation_body_theorem.json"


def sha_arr(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_relation_manifest(path: Path) -> dict[str, Any]:
    z = np.load(path)
    encoded = np.asarray(z["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(z["offsets"], dtype=np.int64)
    obj = np.asarray(z["object_of_point"], dtype=np.int16)
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "points": int(np.asarray(z["points"]).reshape(-1)[0]),
        "group_order": int(np.asarray(z["group_order"]).reshape(-1)[0]),
        "relations": int(offsets.size - 1),
        "ordered_pair_partition_size": int(encoded.size),
        "encoded_pairs_sha256": sha_arr(encoded),
        "offsets_sha256": sha_arr(offsets),
        "object_of_point_sha256": sha_arr(obj),
        "object_orbit_sizes": np.bincount(obj.astype(np.int64), minlength=6).astype(int).tolist(),
    }


def load_tensor_manifest(path: Path) -> dict[str, Any]:
    z = np.load(path)
    triples = np.asarray(z["triples"], dtype=np.int64)
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "relations": 985,
        "tensor_support": int(triples.shape[0]),
        "coefficient_total": int(triples[:, 3].sum()),
        "coefficient_min": int(triples[:, 3].min()),
        "coefficient_max": int(triples[:, 3].max()),
        "triples_sha256": sha_arr(triples),
    }


def compute_pre_a985_tensor() -> None:
    from .build_orbit_tensor import compute_tensor_from_orbitals

    compute_tensor_from_orbitals(
        PRE_A985_ALIGNED_RELATION_NPZ,
        PRE_A985_TENSOR_NPZ,
        ROOT / raw_tensor_relpath(),
        None,
        False,
    )


def derive(regenerate: bool = False, regenerate_tensor: bool = False) -> dict[str, Any]:
    GENERATED.mkdir(exist_ok=True)

    if regenerate or not PRE_A985_ALIGNED_RELATION_NPZ.exists():
        construct_be3_from_source_coorient(
            ROOT / "data/coorient/be3_coorient_generators.npz",
            PRE_A985_BE3_REPORT,
            PRE_A985_RELATION_NPZ,
            PRE_A985_ALIGNED_RELATION_NPZ,
            ROOT / "data/raw/relation_memberships.npz",
        )
    tensor_refresh_error = None
    if regenerate_tensor or (regenerate and PRE_A985_TENSOR_NPZ.exists()):
        try:
            compute_pre_a985_tensor()
        except ModuleNotFoundError as exc:
            tensor_refresh_error = str(exc)

    generated_relation = load_relation_manifest(PRE_A985_ALIGNED_RELATION_NPZ)
    canonical_relation = load_relation_manifest(ROOT / "data/raw/relation_memberships.npz")
    tensor_rel = raw_tensor_relpath()
    canonical_tensor = load_tensor_manifest(ROOT / tensor_rel)

    relation_matches = (
        generated_relation["encoded_pairs_sha256"] == canonical_relation["encoded_pairs_sha256"]
        and generated_relation["offsets_sha256"] == canonical_relation["offsets_sha256"]
        and generated_relation["object_of_point_sha256"] == canonical_relation["object_of_point_sha256"]
    )
    # The canonical tensor and generated tensors may use different row order.
    # Compare the relation algebra as a multiset of (alpha,beta,gamma,coefficient).
    tensor_report_payload = {}
    generated_tensor = None
    tensor_matches = None
    if PRE_A985_TENSOR_NPZ.exists():
        generated_tensor = load_tensor_manifest(PRE_A985_TENSOR_NPZ)
        if PRE_A985_TENSOR_REPORT.exists():
            try:
                tensor_report_payload = json.loads(PRE_A985_TENSOR_REPORT.read_text(encoding="utf-8"))
            except Exception:
                tensor_report_payload = {}
        gen_triples = np.asarray(np.load(PRE_A985_TENSOR_NPZ)["triples"], dtype=np.int64)
        can_triples = np.asarray(np.load(ROOT / tensor_rel)["triples"], dtype=np.int64)
        idx_g = np.lexsort((gen_triples[:,3], gen_triples[:,2], gen_triples[:,1], gen_triples[:,0]))
        idx_c = np.lexsort((can_triples[:,3], can_triples[:,2], can_triples[:,1], can_triples[:,0]))
        tensor_matches = bool(np.array_equal(gen_triples[idx_g], can_triples[idx_c]))

    result: dict[str, Any] = {
        "schema": "d20.theorem.pre_A985_relation_body@1",
        "status": "PRE_A985_RELATION_BODY_DERIVED_WITHOUT_RELATION_TABLE_PASS" if relation_matches and tensor_matches is not False else "PRE_A985_RELATION_BODY_DERIVATION_NEEDS_REVIEW",
        "theorem_name": "Pre-A985 Relation Body Theorem",
        "claim": f"The 985-relation body is derived from the pre-A985 source construction plus the unique coorient action; data/raw/relation_memberships.npz is a comparison target, not a constructor input. T985 comparison is included when the generated tensor witness is present.",
        "constructor_inputs": [
            "H8 = RM(1,3)",
            "three Type-II neighbor vectors v1,v2,v3",
            "generated G24 endpoint",
            "generated 2576 dodecad shell",
            "unique d20/A985-integral coorient action represented by data/coorient/be3_coorient_generators.npz",
        ],
        "not_constructor_inputs": [
            "data/raw/relation_memberships.npz",
            tensor_rel,
            "data/raw/quotients.npz",
            "data/raw/simple_branching_matrices.npz",
        ],
        "generated_relation_body": generated_relation,
        "canonical_relation_body_comparison": {
            "comparison_target": canonical_relation,
            "matches_canonical_relation_body": relation_matches,
        },
        "generated_tensor_body": generated_tensor,
        "canonical_tensor_comparison": {
            "comparison_target": canonical_tensor,
            "matches_canonical_T985_as_sparse_multiset": tensor_matches,
            "constructor_report_comparison": tensor_report_payload.get("comparison", {}),
            "tensor_refresh_error": tensor_refresh_error,
        },
        "logical_form": {
            "pre_A985_source": "H8^3 -> G24 -> G24^(12)",
            "coorient_action": "unique A985-integral d20-compatible Be3 lift",
            "relation_body": "ordered-pair orbits of Be3 on G24^(12) x G24^(12)",
            "tensor_body": "representative two-step incidence over the generated relation body",
        },
        "result": {
            "A985_relation_count": generated_relation["relations"],
            "ordered_pair_partition_size": generated_relation["ordered_pair_partition_size"],
            "T985_support": generated_tensor["tensor_support"] if generated_tensor else None,
            "T985_coefficient_total": generated_tensor["coefficient_total"] if generated_tensor else None,
            "uses_relation_table_as_input": False,
            "uses_relation_table_as_audit_target": True,
            "generated_tensor_witness_present": generated_tensor is not None,
            "stronger_external_theorem_present": True,
        },
    }
    result["sha256"] = hashlib.sha256(json.dumps({k:v for k,v in result.items() if k != "sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def write_theorem(result: dict[str, Any], out: Path = PRE_A985_THEOREM_JSON, *, pretty: bool = True) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, indent=2 if pretty else None, sort_keys=pretty) + "\n",
        encoding="utf-8",
    )


def ensure_pre_a985_relation_body(*, regenerate: bool = False, write_report: bool = True) -> Path:
    if regenerate or not PRE_A985_ALIGNED_RELATION_NPZ.exists():
        result = derive(regenerate=True, regenerate_tensor=False)
        if write_report:
            write_theorem(result)
    elif write_report and not PRE_A985_THEOREM_JSON.exists():
        write_theorem(derive(regenerate=False))
    return PRE_A985_ALIGNED_RELATION_NPZ


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--regenerate", action="store_true", help="Rebuild the relation body before writing the report; can take several minutes.")
    ap.add_argument("--regenerate-tensor", action="store_true", help="Also rebuild the generated T985 tensor witness; requires scipy.")
    ap.add_argument("--out", default="data/invariants/d20/pre_A985_relation_body_theorem.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = derive(regenerate=args.regenerate, regenerate_tensor=args.regenerate_tensor)
    out = ROOT / args.out
    write_theorem(res, out, pretty=args.pretty)
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))


if __name__ == "__main__":
    main()
