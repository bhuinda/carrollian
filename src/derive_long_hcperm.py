from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
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


FIELD_PRIME = 1_000_003
THEOREM_ID = "long_hcperm"
STATUS = "LONG_HCPERM_SIGNED_COLUMN_LIFT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcperm.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcperm.py"
LONG_HCGRADE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "report.json"
LONG_HCGRADE_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "center_grade_projection.npz"
LONG_HCFOAM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "report.json"
LONG_HCFOAM_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "r_foam_matrices.npz"
LONG_C2UF_REPORT = D20_INVARIANTS / "proof_obligations" / "long_c2uf" / "report.json"

COMBO_TEXT_HASH = "f709248481ff88cff40096519ca78aa3501603d61b6ff47e52e44c7cc6165e73"
GENERATOR_TEXT_HASH = "c46c684609a336761814e01509bd843814fb5cf59c6af2d8e5a0de8bd2156526"
OBS_TEXT_HASH = "27930a75ef0ce9d99cb97a28eba3961dca72f2ab2c20699e65b1cb92961c9508"
MATRIX_SHA256 = "e74819a705e391514670322abefdec6896a658a1379601d8ebdb8227bdc2982b"

COMBO_COLUMNS = [
    "combo_id",
    "feature_id_0",
    "feature_id_1",
    "feature_id_2",
    "feature_id_3",
    "feature_id_4",
    "projection_rank",
    "kernel_dimension",
    "unique_exact_column_count",
    "unique_projective_column_count",
    "duplicate_projective_class_count",
    "total_hit_count",
    "total_miss_count",
    "total_multi_count",
    "perfect_generator_count",
    "worst_generator_miss_count",
    "best_flag",
    "selected_hcgrade_flag",
]
GENERATOR_COLUMNS = [
    "row_id",
    "combo_id",
    "generator_id",
    "hit_count",
    "miss_count",
    "multi_target_count",
    "distinct_target_count",
    "perfect_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "support_dimension",
    "target_dimension",
    "generator_count",
    "feature_row_count",
    "rank33_combo_count",
    "perfect_combo_count",
    "selected_combo_id",
    "selected_total_hit_count",
    "selected_total_miss_count",
    "selected_perfect_generator_count",
    "best_combo_id",
    "best_total_hit_count",
    "best_total_miss_count",
    "best_perfect_generator_count",
    "best_worst_generator_miss_count",
    "signed_column_lift_obstruction_flag",
    "sourced_c2_surface_present_flag",
    "nonmonomial_lift_still_open_flag",
    "alternate_feature_family_still_open_flag",
    "full_intertwiner_claim_flag",
    "focused_hcperm_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

SELECTED_HCGRADE_FEATURES = (2, 3, 4, 7, 10)


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def rank_mod(matrix: np.ndarray, prime: int = FIELD_PRIME) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, cols = work.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if int(work[row, col]) % prime:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            work[[rank, pivot]] = work[[pivot, rank]]
        inv = pow(int(work[rank, col]), -1, prime)
        work[rank] = (work[rank] * inv) % prime
        for row in range(rows):
            if row == rank:
                continue
            factor = int(work[row, col]) % prime
            if factor:
                work[row] = (work[row] - factor * work[rank]) % prime
        rank += 1
        if rank == rows:
            break
    return rank


def column_class_stats(projection: np.ndarray) -> tuple[int, int, int]:
    exact: dict[tuple[int, ...], list[int]] = {}
    projective: dict[tuple[int, ...], list[int]] = {}
    for column in range(projection.shape[1]):
        key = tuple((projection[:, column] % FIELD_PRIME).tolist())
        neg = tuple((-projection[:, column] % FIELD_PRIME).tolist())
        exact.setdefault(key, []).append(column)
        projective.setdefault(min(key, neg), []).append(column)
    duplicate_projective = sum(1 for values in projective.values() if len(values) > 1)
    return len(exact), len(projective), duplicate_projective


def signed_column_lift_stats(projection: np.ndarray, r_foam: np.ndarray) -> tuple[list[dict[str, int]], dict[str, int]]:
    column_lookup: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    for column in range(projection.shape[1]):
        key = tuple((projection[:, column] % FIELD_PRIME).tolist())
        neg = tuple((-projection[:, column] % FIELD_PRIME).tolist())
        column_lookup.setdefault(key, []).append((column, 1))
        column_lookup.setdefault(neg, []).append((column, -1))

    generator_rows: list[dict[str, int]] = []
    total_hit = 0
    total_miss = 0
    total_multi = 0
    perfect_count = 0
    worst_miss = 0
    for generator_id, matrix in enumerate(r_foam):
        hit_count = 0
        miss_count = 0
        multi_count = 0
        target_columns: set[int] = set()
        for column in range(projection.shape[1]):
            transformed = tuple(((matrix @ projection[:, column]) % FIELD_PRIME).tolist())
            candidates = column_lookup.get(transformed, [])
            if candidates:
                hit_count += 1
                target_columns.update(candidate[0] for candidate in candidates)
                if len(candidates) > 1:
                    multi_count += 1
            else:
                miss_count += 1
        perfect = int(miss_count == 0)
        perfect_count += perfect
        worst_miss = max(worst_miss, miss_count)
        total_hit += hit_count
        total_miss += miss_count
        total_multi += multi_count
        generator_rows.append(
            {
                "generator_id": generator_id,
                "hit_count": hit_count,
                "miss_count": miss_count,
                "multi_target_count": multi_count,
                "distinct_target_count": len(target_columns),
                "perfect_flag": perfect,
            }
        )
    summary = {
        "total_hit_count": total_hit,
        "total_miss_count": total_miss,
        "total_multi_count": total_multi,
        "perfect_generator_count": perfect_count,
        "worst_generator_miss_count": worst_miss,
    }
    return generator_rows, summary


def combo_sort_key(row: dict[str, int]) -> tuple[int, int, int, int]:
    return (
        row["total_miss_count"],
        -row["perfect_generator_count"],
        row["worst_generator_miss_count"],
        row["total_multi_count"],
    )


def build_rows() -> dict[str, Any]:
    hcgrade = load_json(LONG_HCGRADE_REPORT)
    hcfoam = load_json(LONG_HCFOAM_REPORT)
    c2uf = load_json(LONG_C2UF_REPORT)
    grade_npz = np.load(LONG_HCGRADE_MATRICES, allow_pickle=False)
    foam_npz = np.load(LONG_HCFOAM_MATRICES, allow_pickle=False)
    center = np.asarray(grade_npz["center_matrix"], dtype=np.int64) % FIELD_PRIME
    feature_matrix = np.asarray(grade_npz["feature_matrix"], dtype=np.int64) % FIELD_PRIME
    selected_projection = np.asarray(grade_npz["projection_matrix"], dtype=np.int64) % FIELD_PRIME
    r_foam = np.asarray(foam_npz["r_foam"], dtype=np.int64) % FIELD_PRIME

    combo_rows: list[dict[str, int]] = []
    generator_rows: list[dict[str, int]] = []
    projections: list[np.ndarray] = []
    selected_combo_id = -1
    row_id = 0
    for combo in itertools.combinations(range(feature_matrix.shape[0]), 5):
        projection = np.vstack([center, feature_matrix[list(combo)]]) % FIELD_PRIME
        projection_rank = rank_mod(projection)
        if projection_rank != 33:
            continue
        combo_id = len(combo_rows)
        exact_count, projective_count, duplicate_count = column_class_stats(projection)
        per_generator, summary = signed_column_lift_stats(projection, r_foam)
        combo_tuple = tuple(int(value) for value in combo)
        if combo_tuple == SELECTED_HCGRADE_FEATURES:
            selected_combo_id = combo_id
        combo_rows.append(
            {
                "combo_id": combo_id,
                "feature_id_0": combo_tuple[0],
                "feature_id_1": combo_tuple[1],
                "feature_id_2": combo_tuple[2],
                "feature_id_3": combo_tuple[3],
                "feature_id_4": combo_tuple[4],
                "projection_rank": projection_rank,
                "kernel_dimension": int(projection.shape[1] - projection_rank),
                "unique_exact_column_count": exact_count,
                "unique_projective_column_count": projective_count,
                "duplicate_projective_class_count": duplicate_count,
                "total_hit_count": summary["total_hit_count"],
                "total_miss_count": summary["total_miss_count"],
                "total_multi_count": summary["total_multi_count"],
                "perfect_generator_count": summary["perfect_generator_count"],
                "worst_generator_miss_count": summary["worst_generator_miss_count"],
                "best_flag": 0,
                "selected_hcgrade_flag": int(combo_tuple == SELECTED_HCGRADE_FEATURES),
            }
        )
        for per_row in per_generator:
            generator_rows.append({"row_id": row_id, "combo_id": combo_id, **per_row})
            row_id += 1
        projections.append(projection)

    if selected_combo_id < 0:
        raise AssertionError("selected long_hcgrade combo not found")
    best_combo = min(combo_rows, key=combo_sort_key)
    best_combo_id = best_combo["combo_id"]
    combo_rows[best_combo_id]["best_flag"] = 1
    selected_combo = combo_rows[selected_combo_id]

    obs = {
        "support_dimension": int(center.shape[1]),
        "target_dimension": int(r_foam.shape[1]),
        "generator_count": int(r_foam.shape[0]),
        "feature_row_count": int(feature_matrix.shape[0]),
        "rank33_combo_count": int(len(combo_rows)),
        "perfect_combo_count": int(sum(row["perfect_generator_count"] == r_foam.shape[0] for row in combo_rows)),
        "selected_combo_id": int(selected_combo_id),
        "selected_total_hit_count": int(selected_combo["total_hit_count"]),
        "selected_total_miss_count": int(selected_combo["total_miss_count"]),
        "selected_perfect_generator_count": int(selected_combo["perfect_generator_count"]),
        "best_combo_id": int(best_combo_id),
        "best_total_hit_count": int(best_combo["total_hit_count"]),
        "best_total_miss_count": int(best_combo["total_miss_count"]),
        "best_perfect_generator_count": int(best_combo["perfect_generator_count"]),
        "best_worst_generator_miss_count": int(best_combo["worst_generator_miss_count"]),
        "signed_column_lift_obstruction_flag": int(best_combo["perfect_generator_count"] != r_foam.shape[0]),
        "sourced_c2_surface_present_flag": int(c2uf.get("status") == "LONG_C2UF_CERTIFIED" and c2uf.get("all_checks_pass") is True),
        "nonmonomial_lift_still_open_flag": 1,
        "alternate_feature_family_still_open_flag": 1,
        "full_intertwiner_claim_flag": 0,
        "focused_hcperm_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "selected_projection": selected_projection,
        "best_projection": projections[best_combo_id],
        "r_foam": r_foam,
    }
    matrix_sha = hashlib.sha256(
        b"".join(np.ascontiguousarray(matrix_payload[key]).tobytes() for key in matrix_payload)
    ).hexdigest()
    return {
        "hcgrade": hcgrade,
        "hcfoam": hcfoam,
        "c2uf": c2uf,
        "combo_rows": combo_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "combo_table": table_from_rows(COMBO_COLUMNS, combo_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_sha,
        "obs": obs,
        "combo_text_hash": hashlib.sha256(digest_text(COMBO_COLUMNS, combo_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_hcgrade_input_passes": rows["hcgrade"].get("status") == "LONG_HCGRADE_CENTER_GRADE_RANK_CERTIFIED"
        and rows["hcgrade"].get("all_checks_pass") is True,
        "long_hcfoam_input_passes": rows["hcfoam"].get("status") == "LONG_HCFOAM_CERTIFIED"
        and rows["hcfoam"].get("all_checks_pass") is True,
        "long_c2uf_input_passes": rows["c2uf"].get("status") == "LONG_C2UF_CERTIFIED"
        and rows["c2uf"].get("all_checks_pass") is True,
        "rank33_family_has_expected_size": obs["rank33_combo_count"] == 256,
        "selected_combo_matches_prior_hcgrade": (
            obs["selected_combo_id"],
            obs["selected_total_hit_count"],
            obs["selected_total_miss_count"],
            obs["selected_perfect_generator_count"],
        )
        == (0, 92, 412, 0),
        "best_combo_is_still_obstructed": (
            obs["best_combo_id"],
            obs["best_total_hit_count"],
            obs["best_total_miss_count"],
            obs["best_perfect_generator_count"],
            obs["best_worst_generator_miss_count"],
        )
        == (251, 190, 314, 0, 50),
        "no_signed_column_lift_in_declared_family": (
            obs["perfect_combo_count"],
            obs["signed_column_lift_obstruction_flag"],
        )
        == (0, 1),
        "open_boundaries_preserved": (
            obs["nonmonomial_lift_still_open_flag"],
            obs["alternate_feature_family_still_open_flag"],
            obs["full_intertwiner_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_signed_column_lift_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This rejects signed row-basis permutation lifts inside the declared center-grade family; it does not reject nonmonomial lifts or different feature families.",
    }
    seam_payload = {
        "schema": "long.hcperm.seam@1",
        "status": STATUS,
        "claim": "No rank-33 completion in the declared 24-row center-grade feature family is closed under the nine target signed-column actions.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcgrade": input_entry(
            LONG_HCGRADE_REPORT,
            {
                "status": rows["hcgrade"].get("status"),
                "certificate_sha256": rows["hcgrade"].get("certificate_sha256"),
            },
        ),
        "long_hcfoam": input_entry(
            LONG_HCFOAM_REPORT,
            {
                "status": rows["hcfoam"].get("status"),
                "certificate_sha256": rows["hcfoam"].get("certificate_sha256"),
            },
        ),
        "long_c2uf": input_entry(
            LONG_C2UF_REPORT,
            {
                "status": rows["c2uf"].get("status"),
                "certificate_sha256": rows["c2uf"].get("certificate_sha256"),
            },
        ),
        "hcgrade_matrices": input_entry(LONG_HCGRADE_MATRICES),
        "hcfoam_matrices": input_entry(LONG_HCFOAM_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcperm.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_hcperm certifies an obstruction: the current center-grade projection family cannot be the final support action through a signed row-basis permutation lift of the target action.",
        "stage_protocol": {
            "draft": "read long_hcgrade, long_hcfoam, long_c2uf, the 33x56 projection family data, and the target action matrices",
            "witness": "emit all 256 rank-33 completion rows and per-generator signed-column lift statistics",
            "coherence": "check rank-33 family size, selected-completion statistics, best-completion statistics, and open nonmonomial boundaries",
            "closure": "certify only the signed column-lift obstruction inside the declared feature family",
            "emit": "write long_hcperm artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "combo_rows_csv": relpath(OUT_DIR / "combo_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "lift_obstruction_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all 256 rank-33 completions in the declared center-grade feature family were tested",
                "zero completions admit a signed row-basis permutation lift for all nine target generators",
                "the selected long_hcgrade completion has 412 misses across 504 generator-column tests",
                "the best completion still has 314 misses across 504 generator-column tests",
            ],
            "does_not_certify": [
                "nonexistence of a nonmonomial 56x56 source-side operator family",
                "nonexistence of a valid projection outside the declared center-grade feature family",
                "the accepted Lambda3(A2+H6) row binding",
                "the full matrix intertwining equation",
            ],
        },
        "next_highest_yield_item": "Drop the signed-permutation lift assumption and solve the linear source-side operator equation against the rank-33 projection candidate while preserving the 23-dimensional kernel.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.hcperm.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.hcperm.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "combo_csv": csv_text(COMBO_COLUMNS, rows["combo_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "combo_table": rows["combo_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "combo_text_sha256": rows["combo_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
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
    (OUT_DIR / "combo_rows.csv").write_text(payloads["combo_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        combo_table=payloads["combo_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "lift_obstruction_matrices.npz", **payloads["matrix_payload"])
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
