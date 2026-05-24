from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, LAYERS, ROOT
from src.derive_sector33_boundary_annihilation_theorem import (
    FIELD_PRIME,
    H6_LABELS,
    multiply,
    regular_trace_coefficients,
    rref_nullspace_mod,
    signed_mod,
    vec_digest,
)
from src.derive_sector33_residual_lift_theorem import quotient_shadow


THEOREM_ID = "sector33_unique_public_zero_carrier"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ALL_RESIDUE_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
FULL_A985_LIFT = LAYERS / "drinfeld" / "full_a985_lift.json"
CORE_A985 = LAYERS / "core" / "a985.json"
RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
QUOTIENT_NPZ = ROOT / "data" / "raw" / "quotients.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def local_idempotent_cache(
    core: dict[str, Any],
    triples: np.ndarray,
    block_i: np.ndarray,
    block_j: np.ndarray,
) -> tuple[dict[tuple[int, int], np.ndarray], dict[int, dict[str, Any]]]:
    cache: dict[tuple[int, int], np.ndarray] = {}
    summaries: dict[int, dict[str, Any]] = {}
    for obj in range(len(H6_LABELS)):
        ids = np.where((block_i == obj) & (block_j == obj))[0].astype(np.int64)
        local_index_by_relation = {int(relation): idx for idx, relation in enumerate(ids.tolist())}
        mask = np.isin(triples[:, 0], ids) & np.isin(triples[:, 1], ids) & np.isin(triples[:, 2], ids)
        sub = triples[mask]
        n = int(len(ids))
        tensor = np.zeros((n, n, n), dtype=np.int64)
        for alpha, beta, gamma, value in sub.tolist():
            tensor[
                local_index_by_relation[int(alpha)],
                local_index_by_relation[int(beta)],
                local_index_by_relation[int(gamma)],
            ] = int(value)

        commutator_rows = [(tensor[:, alpha, :] - tensor[alpha, :, :]).T for alpha in range(n)]
        center_basis = rref_nullspace_mod(np.vstack(commutator_rows), FIELD_PRIME)
        stored = core["blocks"][obj]
        coordinates = np.asarray(stored["primitive_idempotent_coordinates"], dtype=np.int64) % FIELD_PRIME
        expected_dim = int(stored["center_dimension"])
        if center_basis.shape[1] != expected_dim:
            raise ValueError(f"center dimension mismatch for object {obj}")
        if coordinates.shape != (expected_dim, expected_dim):
            raise ValueError(f"primitive idempotent coordinate shape mismatch for object {obj}")

        for local_index in range(expected_dim):
            local_vec = (center_basis @ coordinates[local_index]) % FIELD_PRIME
            global_vec = np.zeros(int(block_i.shape[0]), dtype=np.int64)
            global_vec[ids] = local_vec
            cache[(obj, local_index)] = global_vec
        summaries[obj] = {
            "object": obj,
            "label": H6_LABELS[obj],
            "closed_loop_relation_count": n,
            "center_dimension": expected_dim,
            "primitive_idempotent_count": int(stored["primitive_idempotent_count"]),
            "primitive_idempotent_coordinates_sha256": stored["primitive_idempotent_coordinates_sha256"],
        }
    return cache, summaries


def sector_vector(
    profile: dict[str, Any],
    cache: dict[tuple[int, int], np.ndarray],
    relation_count: int,
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    vector = np.zeros(relation_count, dtype=np.int64)
    keys: list[tuple[int, int]] = []
    for signature in profile["spectral_signature"]:
        obj = int(signature["object"])
        for local_index in signature["local_pre_idempotents"]:
            key = (obj, int(local_index))
            keys.append(key)
            vector = (vector + cache[key]) % FIELD_PRIME
    return vector, keys


def object_loop_support(vec: np.ndarray, block_i: np.ndarray, block_j: np.ndarray) -> list[int]:
    return [
        int(np.count_nonzero(vec[(block_i == obj) & (block_j == obj)]))
        for obj in range(len(H6_LABELS))
    ]


def identity_coefficients_signed(vec: np.ndarray, identity_relations: list[int]) -> list[int]:
    return [signed_mod(int(vec[idx])) for idx in identity_relations]


def active_objects(vec: np.ndarray, block_i: np.ndarray) -> list[str]:
    support = np.nonzero(vec)[0]
    objects = sorted({int(block_i[index]) for index in support})
    return [H6_LABELS[obj] for obj in objects]


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.v1",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    all_residue = load_json(ALL_RESIDUE_TRANSPORT_REPORT)
    full = load_json(FULL_A985_LIFT)
    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]
    relation_npz = np.load(RELATION_NPZ)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    quotients = np.load(QUOTIENT_NPZ)
    q42 = np.asarray(quotients["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotients["q12_map"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    trace_coeff = regular_trace_coefficients(triples, int(block_i.shape[0]))

    profiles = full["gluing_and_sector_profiles"]["sector_profiles"]
    identity_relations = [
        int(value) for value in full["full_A985_idempotent_validation"]["identity_relations_by_object"]
    ]
    cache, local_summaries = local_idempotent_cache(core, triples, block_i, block_j)

    sector_rows = []
    used_keys: list[tuple[int, int]] = []
    idempotent_failures: list[int] = []
    for profile in profiles:
        sector = int(profile["sector"])
        vec, keys = sector_vector(profile, cache, int(block_i.shape[0]))
        used_keys.extend(keys)
        square = multiply(triples, vec, vec)
        is_idempotent = bool(np.array_equal(square, vec % FIELD_PRIME))
        if not is_idempotent:
            idempotent_failures.append(sector)
        q42_shadow = quotient_shadow(vec, q42, 42)
        q12_shadow = quotient_shadow(vec, q12, 12)
        trace_value = int((trace_coeff @ vec) % FIELD_PRIME)
        sector_rows.append(
            {
                "sector": sector,
                "block_dimension": int(profile["block_dimension"]),
                "regular_trace": trace_value,
                "regular_trace_signed": signed_mod(trace_value),
                "expected_regular_trace": int(profile["regular_trace_block_square"]),
                "is_idempotent": is_idempotent,
                "local_pre_idempotent_keys": [[int(obj), int(local)] for obj, local in keys],
                "pre_idempotent_support_size": int(len(keys)),
                "expected_pre_idempotent_support_size": int(profile["pre_idempotent_support_size"]),
                "vector": vec_digest(vec),
                "active_objects": active_objects(vec, block_i),
                "expected_active_objects": profile["active_objects"],
                "object_loop_coordinate_support": object_loop_support(vec, block_i, block_j),
                "expected_object_loop_coordinate_support": profile["object_loop_coordinate_support"],
                "identity_coefficients_signed": identity_coefficients_signed(vec, identity_relations),
                "expected_identity_coefficients_signed": profile["identity_coefficients_signed"],
                "q42_nonzero_count": int(q42_shadow["nonzero_count"]),
                "expected_q42_nonzero_count": int(profile["q42_nonzero_count"]),
                "q12_nonzero_count": int(q12_shadow["nonzero_count"]),
                "expected_q12_nonzero_count": int(profile["q12_nonzero_count"]),
                "public_zero": bool(q42_shadow["nonzero_count"] == 0 and q12_shadow["nonzero_count"] == 0),
                "q42_shadow_sha256": q42_shadow["sha256"],
                "q12_shadow_sha256": q12_shadow["sha256"],
            }
        )

    key_counts = Counter(used_keys)
    duplicate_keys = [
        [int(obj), int(local), int(count)]
        for (obj, local), count in sorted(key_counts.items())
        if count != 1
    ]
    missing_keys = [
        [int(obj), int(local)]
        for obj in range(len(H6_LABELS))
        for local in range(int(core["blocks"][obj]["primitive_idempotent_count"]))
        if (obj, local) not in key_counts
    ]
    public_zero_sectors = [row["sector"] for row in sector_rows if row["public_zero"]]
    profile_public_zero_sectors = [
        int(profile["sector"])
        for profile in profiles
        if int(profile["q42_nonzero_count"]) == 0 and int(profile["q12_nonzero_count"]) == 0
    ]
    nonzero_residual_count = int(all_residue["derived"]["nonzero_residue_class_count"])
    field_zero_nonzero_residual_count = int(all_residue["derived"]["field_zero_nonzero_residual_count"])

    checks = {
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "sector_profile_count_is_39": len(profiles) == 39,
        "local_pre_idempotent_total_is_109": len(cache) == 109,
        "profile_pre_idempotent_total_is_109": len(used_keys) == 109,
        "every_local_pre_idempotent_used_once": not duplicate_keys and not missing_keys,
        "stored_profile_says_all_109_used_once": full["gluing_and_sector_profiles"][
            "all_109_pre_idempotents_used_once"
        ]
        is True,
        "all_sector_idempotents_square_to_self": not idempotent_failures,
        "all_sector_supports_match_profiles": all(
            row["vector"]["support"] == row["expected_pre_idempotent_support_size"]
            or row["vector"]["support"] == sum(row["expected_object_loop_coordinate_support"])
            for row in sector_rows
        ),
        "all_object_loop_supports_match_profiles": all(
            row["object_loop_coordinate_support"] == row["expected_object_loop_coordinate_support"]
            for row in sector_rows
        ),
        "all_identity_coefficients_match_profiles": all(
            row["identity_coefficients_signed"] == row["expected_identity_coefficients_signed"]
            for row in sector_rows
        ),
        "all_q42_shadow_counts_match_profiles": all(
            row["q42_nonzero_count"] == row["expected_q42_nonzero_count"] for row in sector_rows
        ),
        "all_q12_shadow_counts_match_profiles": all(
            row["q12_nonzero_count"] == row["expected_q12_nonzero_count"] for row in sector_rows
        ),
        "all_regular_traces_match_block_squares": all(
            row["regular_trace"] == row["expected_regular_trace"] for row in sector_rows
        ),
        "computed_public_zero_sector_is_only_33": public_zero_sectors == [33],
        "profile_public_zero_sector_is_only_33": profile_public_zero_sectors == [33],
        "nonzero_height_residuals_are_field_nonzero": nonzero_residual_count == 2047
        and field_zero_nonzero_residual_count == 0,
        "sector33_is_unique_single_sector_public_zero_carrier": public_zero_sectors == [33]
        and nonzero_residual_count == 2047
        and field_zero_nonzero_residual_count == 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_CARRIER_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_CARRIER_NEEDS_REVIEW"
    )

    sector33_row = next(row for row in sector_rows if row["sector"] == 33)
    report = {
        "schema": "d20.theorem.sector33_unique_public_zero_carrier.v1",
        "status": status,
        "object": "d20",
        "claim": (
            "Materializing the 39 tube-visible sector idempotents from the 109 local closed-loop "
            "pre-idempotents shows that sector 33 is the unique single-sector idempotent with zero "
            "A42 and A12 public shadow. Since all 2047 nonzero height residuals are nonzero in the "
            "verifier field, any single-sector public-zero height carrier must be Pi_33."
        ),
        "definition": {
            "tube_visible_sector_idempotent": (
                "For each sector profile, sum the local closed-loop pre-idempotents named in its "
                "spectral_signature."
            ),
            "public_zero_carrier": "A sector idempotent e_s with q42(e_s)=0 and q12(e_s)=0.",
            "single_sector_uniqueness": (
                "Among the 39 materialized tube-visible sector idempotents, exactly one has zero public "
                "A42/A12 shadow: e_33."
            ),
        },
        "inputs": {
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_TRANSPORT_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
            "core_a985": {
                "path": rel(CORE_A985),
                "sha256": sha_file(CORE_A985),
            },
            "relation_memberships": {
                "path": rel(RELATION_NPZ),
                "sha256": sha_file(RELATION_NPZ),
            },
            "quotients": {
                "path": rel(QUOTIENT_NPZ),
                "sha256": sha_file(QUOTIENT_NPZ),
            },
            "t985_tensor": {
                "path": rel(TENSOR_NPZ),
                "sha256": sha_file(TENSOR_NPZ),
            },
        },
        "derived": {
            "field_prime": FIELD_PRIME,
            "local_pre_idempotent_summaries": local_summaries,
            "sector_count": len(sector_rows),
            "local_pre_idempotent_keys_used": len(used_keys),
            "duplicate_local_pre_idempotent_keys": duplicate_keys,
            "missing_local_pre_idempotent_keys": missing_keys,
            "public_zero_sectors": public_zero_sectors,
            "profile_public_zero_sectors": profile_public_zero_sectors,
            "nonzero_height_residual_count": nonzero_residual_count,
            "field_zero_nonzero_residual_count": field_zero_nonzero_residual_count,
            "unique_public_zero_carrier": {
                "sector": 33,
                "block_dimension": sector33_row["block_dimension"],
                "vector": sector33_row["vector"],
                "q42_nonzero_count": sector33_row["q42_nonzero_count"],
                "q12_nonzero_count": sector33_row["q12_nonzero_count"],
                "local_pre_idempotent_keys": sector33_row["local_pre_idempotent_keys"],
                "active_objects": sector33_row["active_objects"],
            },
            "sector_rows_sha256": sha_json(sector_rows),
            "sector_rows": sector_rows,
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Test whether any nontrivial linear combination of non-public-zero sector idempotents can have "
            "zero A42/A12 shadow, or prove that the public-zero kernel in the sector-idempotent span is "
            "one-dimensional."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector33_unique_public_zero_carrier_manifest.v1",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "reconstruct all 39 tube-visible sector idempotents from local pre-idempotents",
            "verify the 109 local pre-idempotents are used exactly once across sector profiles",
            "verify each reconstructed sector idempotent is idempotent",
            "verify A42/A12 public shadow counts match the canonical sector profiles",
            "verify sector 33 is the unique single-sector public-zero carrier",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
