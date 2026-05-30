from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23act"
STATUS = "SECTOR33_K23_M23_SUPPORT_BINDING_ROW_ACTION_OBSTRUCTED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23act.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23act.py"
LONG_K23SYZ_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23syz" / "report.json"
LONG_K23SYZ_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23syz" / "k23syz_matrices.npz"
LONG_K23STAB_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23stab" / "report.json"
LONG_K23STAB_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23stab" / "k23stab_matrices.npz"

GENERATOR_TEXT_HASH = "4e760a94edc41f6aab0e28133cc7d955c7a3fea91177f7b0fc0168cddb5654fc"
MISMATCH_TEXT_HASH = "33111eff08d81531ffbbfa56390569f5bd8892a82878353f86091a9cf8218542"
OBS_TEXT_HASH = "151fc09318069d959a3727c4bec3ddd8df5932e3548c9ad2ec24fc5a365727c5"
MATRIX_SHA256 = "60bd4f53e724accc3e2c9f6358948c3683af9ad59cd95b502e2204ff80a15a87"

GENERATOR_COLUMNS = [
    "generator_id",
    "generator_order",
    "plain_row_multiset_preserved_flag",
    "signed_row_multiset_preserved_flag",
    "pm_signed_row_multiset_preserved_flag",
    "support_row_multiset_preserved_flag",
    "exact_row_intersection_count",
    "exact_active_row_intersection_count",
    "support_row_intersection_count",
    "support_active_row_intersection_count",
    "missing_exact_row_count",
    "missing_support_row_count",
]
MISMATCH_COLUMNS = [
    "mismatch_id",
    "generator_id",
    "source_support_row_id",
    "transformed_support_mask",
    "transformed_nonzero_count",
    "transformed_signed_l1",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23syz_certified_flag",
    "long_k23stab_certified_flag",
    "prime_field",
    "support_row_count",
    "frame_coordinate_count",
    "active_support_row_count",
    "inactive_support_row_count",
    "generator_count",
    "plain_preserving_generator_count",
    "signed_preserving_generator_count",
    "pm_signed_preserving_generator_count",
    "support_preserving_generator_count",
    "total_exact_row_intersection_count",
    "total_exact_active_row_intersection_count",
    "total_support_row_intersection_count",
    "total_support_active_row_intersection_count",
    "total_missing_exact_row_count",
    "total_missing_support_row_count",
    "row_permutation_lift_exists_for_all_generators_flag",
    "row_sign_lift_exists_for_all_generators_flag",
    "support_pattern_lift_exists_for_all_generators_flag",
    "m23_design_action_certified_flag",
    "support_binding_row_action_obstructed_flag",
    "general_prime_linear_lift_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def signed_value(value: int) -> int:
    value = int(value) % PRIME
    if value > PRIME // 2:
        return value - PRIME
    return value


def row_support_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row).tolist()):
        if int(value) % PRIME != 0:
            mask |= 1 << index
    return mask


def row_tuple(row: np.ndarray) -> tuple[int, ...]:
    return tuple(int(value) % PRIME for value in np.asarray(row).tolist())


def signed_row_tuple(row: np.ndarray) -> tuple[int, ...]:
    return tuple(signed_value(int(value)) for value in np.asarray(row).tolist())


def pm_signed_tuple(row: np.ndarray) -> tuple[int, ...]:
    signed = signed_row_tuple(row)
    neg = tuple(-value for value in signed)
    return min(signed, neg)


def multiset_intersection_count(left: list[tuple[int, ...]] | list[int], right: list[tuple[int, ...]] | list[int]) -> int:
    left_counter = Counter(left)
    right_counter = Counter(right)
    return sum(min(left_counter[key], right_counter[key]) for key in left_counter.keys() & right_counter.keys())


def perm_order(perm: list[int]) -> int:
    seen = [False] * len(perm)
    order = 1
    for start in range(len(perm)):
        if seen[start]:
            continue
        length = 0
        point = start
        while not seen[point]:
            seen[point] = True
            point = int(perm[point])
            length += 1
        if length:
            order = int(np.lcm(order, length))
    return order


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "frame_lift_mod",
        "generator_permutations",
        "action_column_permutations",
        "transformed_frame_lifts",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23syz = load_json(LONG_K23SYZ_REPORT)
    long_k23stab = load_json(LONG_K23STAB_REPORT)
    with np.load(LONG_K23SYZ_MATRICES, allow_pickle=False) as matrices:
        frame_lift_mod = np.asarray(matrices["frame_lift_mod"], dtype=np.int64) % PRIME
        frame_lift_signed = np.asarray(matrices["frame_lift_signed"], dtype=np.int64)
    with np.load(LONG_K23STAB_MATRICES, allow_pickle=False) as matrices:
        generator_permutations = np.asarray(matrices["generator_permutations"], dtype=np.int64)
    original_plain_rows = [row_tuple(row) for row in frame_lift_mod]
    original_signed_rows = [signed_row_tuple(row) for row in frame_lift_mod]
    original_pm_rows = [pm_signed_tuple(row) for row in frame_lift_mod]
    original_support_rows = [row_support_mask(row) for row in frame_lift_mod]
    active_row_count = sum(int(mask != 0) for mask in original_support_rows)
    inactive_row_count = len(original_support_rows) - active_row_count
    generator_rows = []
    mismatch_rows = []
    transformed_lifts = []
    action_column_permutations = []
    mismatch_id = 0
    for generator_id, perm_array in enumerate(generator_permutations.tolist()):
        perm = [int(value) for value in perm_array]
        columns = [0] + [1 + perm[index] for index in range(23)]
        action_column_permutations.append(columns)
        transformed = frame_lift_mod[:, columns]
        transformed_lifts.append(transformed.astype(np.int64))
        transformed_plain_rows = [row_tuple(row) for row in transformed]
        transformed_signed_rows = [signed_row_tuple(row) for row in transformed]
        transformed_pm_rows = [pm_signed_tuple(row) for row in transformed]
        transformed_support_rows = [row_support_mask(row) for row in transformed]
        exact_intersection = multiset_intersection_count(original_plain_rows, transformed_plain_rows)
        support_intersection = multiset_intersection_count(original_support_rows, transformed_support_rows)
        exact_active_intersection = exact_intersection - inactive_row_count
        support_active_intersection = support_intersection - inactive_row_count
        missing_exact = len(original_plain_rows) - exact_intersection
        missing_support = len(original_support_rows) - support_intersection
        row = {
            "generator_id": generator_id,
            "generator_order": perm_order(perm),
            "plain_row_multiset_preserved_flag": int(Counter(original_plain_rows) == Counter(transformed_plain_rows)),
            "signed_row_multiset_preserved_flag": int(Counter(original_signed_rows) == Counter(transformed_signed_rows)),
            "pm_signed_row_multiset_preserved_flag": int(Counter(original_pm_rows) == Counter(transformed_pm_rows)),
            "support_row_multiset_preserved_flag": int(Counter(original_support_rows) == Counter(transformed_support_rows)),
            "exact_row_intersection_count": exact_intersection,
            "exact_active_row_intersection_count": exact_active_intersection,
            "support_row_intersection_count": support_intersection,
            "support_active_row_intersection_count": support_active_intersection,
            "missing_exact_row_count": missing_exact,
            "missing_support_row_count": missing_support,
        }
        generator_rows.append(row)
        original_counter = Counter(original_plain_rows)
        for source_row_id, transformed_row in enumerate(transformed):
            key = row_tuple(transformed_row)
            if original_counter[key] > 0:
                original_counter[key] -= 1
                continue
            signed_row = signed_row_tuple(transformed_row)
            mismatch_rows.append(
                {
                    "mismatch_id": mismatch_id,
                    "generator_id": generator_id,
                    "source_support_row_id": source_row_id,
                    "transformed_support_mask": row_support_mask(transformed_row),
                    "transformed_nonzero_count": int(np.count_nonzero(transformed_row)),
                    "transformed_signed_l1": sum(abs(value) for value in signed_row),
                }
            )
            mismatch_id += 1
    obs = {
        "long_k23syz_certified_flag": int(
            long_k23syz.get("status") == "SECTOR33_K23_CANONICAL_SYZYGY_FRAME_BINDING_CERTIFIED"
            and long_k23syz.get("all_checks_pass") is True
        ),
        "long_k23stab_certified_flag": int(
            long_k23stab.get("status") == "SECTOR33_K23_PUNCTURED_SELECTOR_M23_STABILIZER_CERTIFIED"
            and long_k23stab.get("all_checks_pass") is True
        ),
        "prime_field": PRIME,
        "support_row_count": frame_lift_mod.shape[0],
        "frame_coordinate_count": frame_lift_mod.shape[1],
        "active_support_row_count": active_row_count,
        "inactive_support_row_count": inactive_row_count,
        "generator_count": len(generator_rows),
        "plain_preserving_generator_count": sum(row["plain_row_multiset_preserved_flag"] for row in generator_rows),
        "signed_preserving_generator_count": sum(row["signed_row_multiset_preserved_flag"] for row in generator_rows),
        "pm_signed_preserving_generator_count": sum(row["pm_signed_row_multiset_preserved_flag"] for row in generator_rows),
        "support_preserving_generator_count": sum(row["support_row_multiset_preserved_flag"] for row in generator_rows),
        "total_exact_row_intersection_count": sum(row["exact_row_intersection_count"] for row in generator_rows),
        "total_exact_active_row_intersection_count": sum(row["exact_active_row_intersection_count"] for row in generator_rows),
        "total_support_row_intersection_count": sum(row["support_row_intersection_count"] for row in generator_rows),
        "total_support_active_row_intersection_count": sum(row["support_active_row_intersection_count"] for row in generator_rows),
        "total_missing_exact_row_count": sum(row["missing_exact_row_count"] for row in generator_rows),
        "total_missing_support_row_count": sum(row["missing_support_row_count"] for row in generator_rows),
        "row_permutation_lift_exists_for_all_generators_flag": int(
            all(row["plain_row_multiset_preserved_flag"] for row in generator_rows)
        ),
        "row_sign_lift_exists_for_all_generators_flag": int(
            all(row["pm_signed_row_multiset_preserved_flag"] for row in generator_rows)
        ),
        "support_pattern_lift_exists_for_all_generators_flag": int(
            all(row["support_row_multiset_preserved_flag"] for row in generator_rows)
        ),
        "m23_design_action_certified_flag": int(
            long_k23stab.get("witness", {}).get("summary", {}).get("m23_type_action_certified_flag", 0)
        ),
        "support_binding_row_action_obstructed_flag": int(
            sum(row["plain_row_multiset_preserved_flag"] for row in generator_rows) == 0
            and sum(row["pm_signed_row_multiset_preserved_flag"] for row in generator_rows) == 0
            and sum(row["support_row_multiset_preserved_flag"] for row in generator_rows) == 0
        ),
        "general_prime_linear_lift_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "frame_lift_mod": frame_lift_mod.astype(np.int64),
        "generator_permutations": generator_permutations.astype(np.int64),
        "action_column_permutations": np.asarray(action_column_permutations, dtype=np.int64),
        "transformed_frame_lifts": np.asarray(transformed_lifts, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23syz": long_k23syz,
        "long_k23stab": long_k23stab,
        "generator_rows": generator_rows,
        "mismatch_rows": mismatch_rows,
        "obs_rows": obs_rows,
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "mismatch_table": table_from_rows(MISMATCH_COLUMNS, mismatch_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "mismatch_text_hash": hashlib.sha256(digest_text(MISMATCH_COLUMNS, mismatch_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23syz_certified_flag"],
            obs["long_k23stab_certified_flag"],
            obs["m23_design_action_certified_flag"],
        )
        == (1, 1, 1),
        "support_lift_shape_matches": (
            obs["prime_field"],
            obs["support_row_count"],
            obs["frame_coordinate_count"],
            obs["active_support_row_count"],
            obs["inactive_support_row_count"],
            obs["generator_count"],
        )
        == (PRIME, 56, 24, 23, 33, 3),
        "no_row_permutation_lift_for_generators": (
            obs["plain_preserving_generator_count"],
            obs["signed_preserving_generator_count"],
            obs["pm_signed_preserving_generator_count"],
            obs["support_preserving_generator_count"],
        )
        == (0, 0, 0, 0),
        "intersection_profile_matches": (
            obs["total_exact_row_intersection_count"],
            obs["total_exact_active_row_intersection_count"],
            obs["total_support_row_intersection_count"],
            obs["total_support_active_row_intersection_count"],
            obs["total_missing_exact_row_count"],
            obs["total_missing_support_row_count"],
        )
        == (120, 21, 120, 21, 48, 48),
        "obstruction_boundary": (
            obs["row_permutation_lift_exists_for_all_generators_flag"],
            obs["row_sign_lift_exists_for_all_generators_flag"],
            obs["support_pattern_lift_exists_for_all_generators_flag"],
            obs["support_binding_row_action_obstructed_flag"],
            obs["general_prime_linear_lift_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_m23_support_binding_row_action_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the current 56-row K23 support binding is not preserved by the three certified M23 design generators as a row-permutation, signed-row, or support-pattern action; a general prime-linear lift remains open.",
    }
    seam_payload = {
        "schema": "long.k23act.seam@1",
        "status": STATUS,
        "claim": "The certified M23-order punctured selector action does not lift to the current signed 56-support binding by row permutation, row sign, or support-pattern permutation for the three design generators.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23syz": input_entry(
            LONG_K23SYZ_REPORT,
            {
                "status": rows["long_k23syz"].get("status"),
                "certificate_sha256": rows["long_k23syz"].get("certificate_sha256"),
            },
        ),
        "long_k23syz_matrices": input_entry(LONG_K23SYZ_MATRICES),
        "long_k23stab": input_entry(
            LONG_K23STAB_REPORT,
            {
                "status": rows["long_k23stab"].get("status"),
                "certificate_sha256": rows["long_k23stab"].get("certificate_sha256"),
            },
        ),
        "long_k23stab_matrices": input_entry(LONG_K23STAB_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23act.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23act certifies the row-action obstruction between the M23 punctured selector action and the current K23 56-support binding.",
        "stage_protocol": {
            "draft": "read long_k23syz support-frame lift and long_k23stab generator permutations",
            "witness": "emit generator lift rows, transformed-row mismatch rows, observables, and transformed matrices",
            "coherence": "check row-multiset, signed-row, sign-normalized, and support-pattern preservation counts",
            "closure": "certify the row-action obstruction while keeping general prime-linear lifting open",
            "emit": "write long_k23act artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "generator_lift_rows_csv": relpath(OUT_DIR / "generator_lift_rows.csv"),
            "mismatch_rows_csv": relpath(OUT_DIR / "mismatch_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23act_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the three certified M23 design generators do not preserve the current 56-row frame lift as a row multiset",
                "the same generators do not preserve it after signed-row normalization by plus/minus sign",
                "the same generators do not preserve the row support-pattern multiset",
                "the current support binding therefore has a row-action obstruction against the certified M23 design action",
            ],
            "does_not_certify": [
                "nonexistence of a general prime-field linear lift",
                "nonexistence of a changed support binding with M23 equivariance",
                "intrinsic recovery of the selector from the naive binary shadow",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Solve the general prime-linear intertwiner equation for the three certified M23 generators against the K23 basis/support lift, or emit the corresponding linear obstruction.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23act.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23act.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "mismatch_csv": csv_text(MISMATCH_COLUMNS, rows["mismatch_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "generator_table": rows["generator_table"],
        "mismatch_table": rows["mismatch_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "generator_text_sha256": rows["generator_text_hash"],
            "mismatch_text_sha256": rows["mismatch_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "generator_lift_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "mismatch_rows.csv").write_text(payloads["mismatch_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        generator_table=payloads["generator_table"],
        mismatch_table=payloads["mismatch_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23act_matrices.npz", **payloads["matrix_payload"])
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
