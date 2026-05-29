from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_ctor import (
        DERIVE_SCRIPT,
        FORMULA_JSON,
        HASH_COLUMNS,
        INDEX_PATH,
        LONG_ORAC_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_QUOTIENTS,
        RAW_RELATIONS,
        RAW_TENSOR,
        STATUS,
        STRICT_QUOTIENTS,
        STRICT_RELATIONS,
        STRICT_TENSOR,
        SURFACE_CODE_MAP,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        npz_array_entry,
        quotient_arrays,
        relation_arrays,
        self_hash,
        tensor_arrays,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_ctor import (
        DERIVE_SCRIPT,
        FORMULA_JSON,
        HASH_COLUMNS,
        INDEX_PATH,
        LONG_ORAC_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_QUOTIENTS,
        RAW_RELATIONS,
        RAW_TENSOR,
        STATUS,
        STRICT_QUOTIENTS,
        STRICT_RELATIONS,
        STRICT_TENSOR,
        SURFACE_CODE_MAP,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        npz_array_entry,
        quotient_arrays,
        relation_arrays,
        self_hash,
        tensor_arrays,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def assert_npz_array_entry(
    entry: dict[str, Any],
    expected_path: Path,
    arrays: dict[str, np.ndarray],
    label: str,
) -> None:
    expected = npz_array_entry(expected_path, arrays)
    if entry != expected:
        raise AssertionError(f"{label} array entry mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_ctor() -> dict[str, Any]:
    expected = build_payloads()
    ctor_payload = load_json(OUT_DIR / "ctor.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if ctor_payload != expected["ctor"]:
        raise AssertionError("long_ctor ctor JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_ctor cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "hash.csv": "hash_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_ctor {filename} mismatch")

    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_ctor table mismatch: {key}")

    if report.get("schema") != "long.ctor.report@1":
        raise AssertionError("long_ctor report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_ctor report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_ctor all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_ctor checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ctor report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_ctor report hash mismatch")

    csv_shapes = [
        ("surface.csv", SURFACE_COLUMNS, len(SURFACE_CODE_MAP)),
        ("hash.csv", HASH_COLUMNS, 23),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_ctor {filename} shape mismatch")

    table_shapes = {
        "surface_table": (len(SURFACE_CODE_MAP), len(SURFACE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_ctor {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "surface_row_count": 12,
        "hash_row_count": 23,
        "strict_scratch_passed_flag": 1,
        "full_scratch_object_constructor_flag": 1,
        "constructs_from_supplied_raw_seeds_flag": 0,
        "seed_boundary_file_count": 0,
        "completed_full_scratch_step_count": 21,
        "missing_full_scratch_step_count": 0,
        "remaining_boundary_count": 0,
        "points": 2576,
        "relations": 985,
        "ordered_pair_partition_size": 6_635_776,
        "object_count": 6,
        "tensor_support": 1_414_965,
        "tensor_coefficient_total": 2_537_360,
        "stored_raw_triples_order_matches_generated_flag": 0,
        "canonical_tensor_multiset_matches_flag": 1,
        "raw_tensor_reps_match_generated_reps_flag": 0,
        "relation_partition_matches_flag": 1,
        "terminal_q42_map_matches_flag": 1,
        "terminal_q12_map_matches_flag": 1,
        "terminal_q42_tensor_matches_flag": 1,
        "terminal_q12_tensor_matches_flag": 1,
        "long_orac_certified_flag": 1,
        "oracle_input_report_count": 31,
        "oracle_resolved_surface_count": 29,
        "oracle_open_boundary_count": 22,
        "coorient_formula_seed_integer_count": 12,
        "coorient_full_generator_integer_count": 7728,
        "coorient_generator_compression_ratio_x1000": 644000,
        "cache_disposable_as_semantic_input_flag": 1,
        "exact_npz_byte_reproduction_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_ctor observable {key} mismatch")
    if obs.get(OBS_CODES["raw_cache_file_bytes"], 0) <= 0:
        raise AssertionError("long_ctor raw cache size missing")
    if obs.get(OBS_CODES["raw_array_uncompressed_bytes"], 0) <= 0:
        raise AssertionError("long_ctor raw array byte count missing")

    surface_rows = rows_from_table(np.asarray(tables["surface_table"]), SURFACE_COLUMNS)
    if any(row["certified_flag"] != 1 for row in surface_rows):
        raise AssertionError("long_ctor uncertified surface row")
    if surface_rows[5]["remaining_boundary_count"] != 1:
        raise AssertionError("long_ctor tensor cache boundary count mismatch")
    if surface_rows[11]["remaining_boundary_count"] != 22:
        raise AssertionError("long_ctor oracle open boundary count mismatch")

    hash_header, hash_rows = read_csv(OUT_DIR / "hash.csv")
    if hash_header != HASH_COLUMNS:
        raise AssertionError("long_ctor hash header mismatch")
    mismatch_codes = {
        int(row["hash_code"])
        for row in hash_rows
        if int(row["matches_reference_flag"]) == 0
    }
    if mismatch_codes != {0, 6}:
        raise AssertionError(f"long_ctor unexpected hash mismatch codes: {mismatch_codes}")

    inputs = report.get("inputs", {})
    for key, path in {
        "raw_tensor": RAW_TENSOR,
        "raw_relations": RAW_RELATIONS,
        "raw_quotients": RAW_QUOTIENTS,
        "coorient_formula": FORMULA_JSON,
        "long_orac_report": LONG_ORAC_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)
    assert_npz_array_entry(
        inputs.get("strict_tensor", {}),
        STRICT_TENSOR,
        tensor_arrays(STRICT_TENSOR),
        "strict_tensor",
    )
    assert_npz_array_entry(
        inputs.get("strict_relations", {}),
        STRICT_RELATIONS,
        relation_arrays(STRICT_RELATIONS),
        "strict_relations",
    )
    assert_npz_array_entry(
        inputs.get("strict_quotients", {}),
        STRICT_QUOTIENTS,
        quotient_arrays(STRICT_QUOTIENTS),
        "strict_quotients",
    )

    if manifest.get("schema") != "long.ctor.manifest@1":
        raise AssertionError("long_ctor manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ctor manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_ctor manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_ctor missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ctor proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_ctor proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.ctor.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "surface_code_map": witness.get("surface_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_ctor(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
