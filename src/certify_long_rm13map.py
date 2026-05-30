from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_rm13map import (
        DERIVE_SCRIPT,
        MAP_COLUMNS,
        MAP_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REPLAY_COLUMNS,
        REPLAY_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_rm13map import (
        DERIVE_SCRIPT,
        MAP_COLUMNS,
        MAP_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REPLAY_COLUMNS,
        REPLAY_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )


EXPECTED_PERMUTATION = [
    0,
    1,
    2,
    3,
    4,
    11,
    23,
    17,
    5,
    16,
    8,
    7,
    10,
    22,
    18,
    21,
    9,
    6,
    15,
    19,
    20,
    12,
    13,
    14,
]
EXPECTED_REPLAY_PREIMAGES = {0, 204095, 14945289, 15143222}


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


def validate_long_rm13map() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index_payload = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "rm13map_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_rm13map seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rm13map cert mismatch")
    for filename, key in {
        "map_rows.csv": "map_csv",
        "replay_rows.csv": "replay_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rm13map {filename} mismatch")
    for key, expected_array in {
        "map_table": expected["map_table"],
        "replay_table": expected["replay_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rm13map table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_rm13map matrix payload mismatch: {key}")

    if report.get("schema") != "long.rm13map.report@1":
        raise AssertionError("long_rm13map report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rm13map report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rm13map all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rm13map checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rm13map report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rm13map report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("map_rows.csv", MAP_COLUMNS, 24),
        ("replay_rows.csv", REPLAY_COLUMNS, 4),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rm13map {filename} shape mismatch")

    assert_locked_hash(
        "map rows",
        hashlib.sha256(digest_text(MAP_COLUMNS, csv_rows["map_rows.csv"]).encode("ascii")).hexdigest(),
        MAP_TEXT_HASH,
    )
    assert_locked_hash(
        "replay rows",
        hashlib.sha256(digest_text(REPLAY_COLUMNS, csv_rows["replay_rows.csv"]).encode("ascii")).hexdigest(),
        REPLAY_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "permutation_vector",
            "inverse_permutation_vector",
            "replay_table",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_rm13_certified_flag": 1,
        "long_k23merge_certified_flag": 1,
        "external_w24_certified_flag": 1,
        "source_code_size": 4096,
        "target_code_size": 4096,
        "source_octad_count": 759,
        "target_octad_count": 759,
        "five_subset_lookup_count": 42504,
        "fixed_prefix_coordinate_count": 5,
        "search_node_count": 77,
        "coordinate_map_length": 24,
        "coordinate_map_bijective_flag": 1,
        "mapped_source_code_size": 4096,
        "mapped_source_target_intersection_count": 4096,
        "mapped_source_target_symmetric_difference_count": 0,
        "coordinate_conjugacy_materialized_flag": 1,
        "k23_image_word_count": 4,
        "k23_image_external_member_count": 4,
        "k23_image_source_preimage_member_count": 4,
        "nonzero_k23_image_source_preimage_member_count": 3,
        "k23_image_remap_match_count": 4,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_rm13map observable {name} mismatch")

    permutation = [int(value) for value in np.asarray(matrices["permutation_vector"]).tolist()]
    if permutation != EXPECTED_PERMUTATION:
        raise AssertionError("long_rm13map permutation mismatch")
    inverse = [int(value) for value in np.asarray(matrices["inverse_permutation_vector"]).tolist()]
    if sorted(inverse) != list(range(24)):
        raise AssertionError("long_rm13map inverse permutation not bijective")
    for source_coord, target_coord in enumerate(permutation):
        if inverse[target_coord] != source_coord:
            raise AssertionError("long_rm13map inverse permutation mismatch")

    replay_rows = rows_from_table(np.asarray(tables["replay_table"]), REPLAY_COLUMNS)
    preimages = {int(row["source_preimage_mask"]) for row in replay_rows}
    if preimages != EXPECTED_REPLAY_PREIMAGES:
        raise AssertionError("long_rm13map replay preimage set mismatch")
    if any(int(row["source_endpoint_member_flag"]) != 1 for row in replay_rows):
        raise AssertionError("long_rm13map source replay membership mismatch")
    if any(int(row["remap_matches_external_flag"]) != 1 for row in replay_rows):
        raise AssertionError("long_rm13map replay remap mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.rm13map.manifest@1":
        raise AssertionError("long_rm13map manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rm13map manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_rm13map manifest self hash mismatch")
    matching = [
        row
        for row in index_payload.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_rm13map index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rm13map index report sha mismatch")

    return {
        "schema": "long.rm13map.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "permutation": report.get("witness", {}).get("permutation", []),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_rm13map(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
