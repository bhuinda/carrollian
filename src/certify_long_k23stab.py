from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23stab import (
        BASE_STABILIZER_COLUMNS,
        BASE_STABILIZER_TEXT_HASH,
        BLOCK_COLUMNS,
        BLOCK_TEXT_HASH,
        DERIVE_SCRIPT,
        EXPECTED_BASE4_STABILIZER_COUNT,
        GENERATOR_COLUMNS,
        GENERATOR_PERMS,
        GENERATOR_TEXT_HASH,
        M23_ORDER,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SCHREIER_COLUMNS,
        SCHREIER_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        apply_perm_to_mask,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23stab import (
        BASE_STABILIZER_COLUMNS,
        BASE_STABILIZER_TEXT_HASH,
        BLOCK_COLUMNS,
        BLOCK_TEXT_HASH,
        DERIVE_SCRIPT,
        EXPECTED_BASE4_STABILIZER_COUNT,
        GENERATOR_COLUMNS,
        GENERATOR_PERMS,
        GENERATOR_TEXT_HASH,
        M23_ORDER,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SCHREIER_COLUMNS,
        SCHREIER_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        apply_perm_to_mask,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_SCHREIER_ORBITS = [23, 22, 21, 20, 16, 3]
EXPECTED_SCHREIER_STAB_GENS = [61, 1093, 959, 47, 2, 0]


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def assert_locked_hash(label: str, actual: str, expected: str) -> None:
    if not expected:
        raise AssertionError(f"{label} witness hash is not locked")
    if actual != expected:
        raise AssertionError(f"{label} witness hash mismatch")


def validate_long_k23stab() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23stab_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23stab seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23stab cert mismatch")
    for filename, key in {
        "block_rows.csv": "block_csv",
        "generator_rows.csv": "generator_csv",
        "schreier_rows.csv": "schreier_csv",
        "base_stabilizer_rows.csv": "base_stabilizer_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23stab {filename} mismatch")
    for key, expected_array in {
        "block_table": expected["block_table"],
        "generator_table": expected["generator_table"],
        "schreier_table": expected["schreier_table"],
        "base_stabilizer_table": expected["base_stabilizer_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23stab table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23stab matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23stab.report@1":
        raise AssertionError("long_k23stab report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23stab report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23stab all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23stab checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23stab report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23stab report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("block_rows.csv", BLOCK_COLUMNS, 253),
        ("generator_rows.csv", GENERATOR_COLUMNS, 3),
        ("schreier_rows.csv", SCHREIER_COLUMNS, 6),
        ("base_stabilizer_rows.csv", BASE_STABILIZER_COLUMNS, EXPECTED_BASE4_STABILIZER_COUNT),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23stab {filename} shape mismatch")

    assert_locked_hash(
        "block rows",
        hashlib.sha256(digest_text(BLOCK_COLUMNS, csv_rows["block_rows.csv"]).encode("ascii")).hexdigest(),
        BLOCK_TEXT_HASH,
    )
    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "Schreier rows",
        hashlib.sha256(digest_text(SCHREIER_COLUMNS, csv_rows["schreier_rows.csv"]).encode("ascii")).hexdigest(),
        SCHREIER_TEXT_HASH,
    )
    assert_locked_hash(
        "base stabilizer rows",
        hashlib.sha256(
            digest_text(BASE_STABILIZER_COLUMNS, csv_rows["base_stabilizer_rows.csv"]).encode("ascii")
        ).hexdigest(),
        BASE_STABILIZER_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "block_masks",
            "generator_permutations",
            "base4_stabilizer_permutations",
            "schreier_level_table",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23sel_certified_flag": 1,
        "point_count": 23,
        "block_count": 253,
        "block_size": 7,
        "weight7_block_count": 253,
        "four_subset_count": 8855,
        "four_subset_expected_count": 8855,
        "unique_block_per_4_subset_flag": 1,
        "generator_count": 3,
        "generator_preserve_count": 3,
        "generated_group_order": M23_ORDER,
        "expected_m23_order": M23_ORDER,
        "group_order_matches_m23_flag": 1,
        "schreier_level_count": 6,
        "schreier_terminal_stabilizer_generator_count": 0,
        "base_ordered_4_tuple_count": 212520,
        "base4_pointwise_stabilizer_count": 48,
        "base4_pointwise_stabilizer_expected_count": 48,
        "automorphism_upper_bound": M23_ORDER,
        "upper_bound_matches_generated_order_flag": 1,
        "full_design_automorphism_group_certified_flag": 1,
        "m23_type_action_certified_flag": 1,
        "support_action_on_k23_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23stab observable {name} mismatch")

    generator_perms = np.asarray(matrices["generator_permutations"], dtype=np.int64)
    if generator_perms.tolist() != GENERATOR_PERMS:
        raise AssertionError("long_k23stab generator permutations mismatch")
    block_set = {int(value) for value in np.asarray(matrices["block_masks"]).tolist()}
    for perm in [tuple(int(value) for value in row) for row in generator_perms.tolist()]:
        image_blocks = {apply_perm_to_mask(perm, block) for block in block_set}
        if image_blocks != block_set:
            raise AssertionError("long_k23stab generator does not preserve blocks")
    schreier_rows = rows_from_table(np.asarray(tables["schreier_table"]), SCHREIER_COLUMNS)
    if [row["orbit_size"] for row in schreier_rows] != EXPECTED_SCHREIER_ORBITS:
        raise AssertionError("long_k23stab Schreier orbit list mismatch")
    if [row["schreier_generator_count"] for row in schreier_rows] != EXPECTED_SCHREIER_STAB_GENS:
        raise AssertionError("long_k23stab Schreier stabilizer generator list mismatch")
    if int(np.prod(np.asarray(matrices["schreier_level_table"])[:, 2])) != M23_ORDER:
        raise AssertionError("long_k23stab Schreier order product mismatch")
    if np.asarray(matrices["base4_stabilizer_permutations"]).shape != (48, 23):
        raise AssertionError("long_k23stab base stabilizer matrix shape mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23stab.manifest@1":
        raise AssertionError("long_k23stab manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23stab manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23stab manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23stab index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23stab index report sha mismatch")

    return {
        "schema": "long.k23stab.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23stab(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
