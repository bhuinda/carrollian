from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23sel import (
        COORD_COLUMNS,
        COORD_TEXT_HASH,
        DERIVE_SCRIPT,
        EULER_HIST_COLUMNS,
        EULER_HIST_TEXT_HASH,
        FULL_HIST_TEXT_HASH,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        HIST_COLUMNS,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        ORTH_COLUMNS,
        ORTH_TEXT_HASH,
        OUT_DIR,
        PUNCTURED_HIST_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        digest_text,
        gf2_rank_masks,
        matrix_payload_hash,
        self_hash,
        build_payloads,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23sel import (
        COORD_COLUMNS,
        COORD_TEXT_HASH,
        DERIVE_SCRIPT,
        EULER_HIST_COLUMNS,
        EULER_HIST_TEXT_HASH,
        FULL_HIST_TEXT_HASH,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        HIST_COLUMNS,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        ORTH_COLUMNS,
        ORTH_TEXT_HASH,
        OUT_DIR,
        PUNCTURED_HIST_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        digest_text,
        gf2_rank_masks,
        matrix_payload_hash,
        self_hash,
        build_payloads,
    )
    from derive_long_raw import rows_from_table


EXPECTED_GENERATORS = [
    4095,
    14040,
    21655,
    37830,
    70429,
    135851,
    266366,
    530021,
    1054124,
    2101745,
    4200242,
    8394059,
]
EXPECTED_FULL_HIST = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
EXPECTED_PUNCTURED_HIST = {0: 1, 7: 253, 8: 506, 11: 1288, 12: 1288, 15: 506, 16: 253, 23: 1}
EXPECTED_EULER_HIST = {
    (0, 0): 1,
    (0, 8): 506,
    (0, 12): 1288,
    (0, 16): 253,
    (1, 7): 253,
    (1, 11): 1288,
    (1, 15): 506,
    (1, 23): 1,
}


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


def validate_long_k23sel() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23sel_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23sel seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23sel cert mismatch")
    for filename, key in {
        "coordinate_rows.csv": "coord_csv",
        "generator_rows.csv": "generator_csv",
        "orthogonality_rows.csv": "orth_csv",
        "weight_histogram.csv": "full_hist_csv",
        "punctured_weight_histogram.csv": "punctured_hist_csv",
        "euler_histogram.csv": "euler_hist_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23sel {filename} mismatch")
    for key, expected_array in {
        "coordinate_table": expected["coord_table"],
        "generator_table": expected["generator_table"],
        "orthogonality_table": expected["orth_table"],
        "weight_histogram_table": expected["full_hist_table"],
        "punctured_weight_histogram_table": expected["punctured_hist_table"],
        "euler_histogram_table": expected["euler_hist_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23sel table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23sel matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23sel.report@1":
        raise AssertionError("long_k23sel report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23sel report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23sel all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23sel checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23sel report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23sel report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("coordinate_rows.csv", COORD_COLUMNS, 24),
        ("generator_rows.csv", GENERATOR_COLUMNS, 12),
        ("orthogonality_rows.csv", ORTH_COLUMNS, 144),
        ("weight_histogram.csv", HIST_COLUMNS, 5),
        ("punctured_weight_histogram.csv", HIST_COLUMNS, 8),
        ("euler_histogram.csv", EULER_HIST_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23sel {filename} shape mismatch")

    assert_locked_hash(
        "coordinate rows",
        hashlib.sha256(digest_text(COORD_COLUMNS, csv_rows["coordinate_rows.csv"]).encode("ascii")).hexdigest(),
        COORD_TEXT_HASH,
    )
    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "orthogonality rows",
        hashlib.sha256(digest_text(ORTH_COLUMNS, csv_rows["orthogonality_rows.csv"]).encode("ascii")).hexdigest(),
        ORTH_TEXT_HASH,
    )
    assert_locked_hash(
        "full histogram rows",
        hashlib.sha256(digest_text(HIST_COLUMNS, csv_rows["weight_histogram.csv"]).encode("ascii")).hexdigest(),
        FULL_HIST_TEXT_HASH,
    )
    assert_locked_hash(
        "punctured histogram rows",
        hashlib.sha256(digest_text(HIST_COLUMNS, csv_rows["punctured_weight_histogram.csv"]).encode("ascii")).hexdigest(),
        PUNCTURED_HIST_TEXT_HASH,
    )
    assert_locked_hash(
        "Euler histogram rows",
        hashlib.sha256(digest_text(EULER_HIST_COLUMNS, csv_rows["euler_histogram.csv"]).encode("ascii")).hexdigest(),
        EULER_HIST_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "generator_masks",
            "generator_matrix",
            "codeword_masks",
            "punctured_codeword_masks",
            "euler_zero_punctured_masks",
            "euler_one_punctured_masks",
            "gram_matrix",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23syz_certified_flag": 1,
        "canonical_frame_certified_flag": 1,
        "row_alphabetization_certified_flag": 1,
        "selector_length": 24,
        "selector_generator_count": 12,
        "selector_rank": 12,
        "selector_word_count": 4096,
        "selector_min_nonzero_weight": 8,
        "selector_weight0_count": 1,
        "selector_weight8_count": 759,
        "selector_weight12_count": 2576,
        "selector_weight16_count": 759,
        "selector_weight24_count": 1,
        "quadratic_zero_word_count": 4096,
        "doubly_even_flag": 1,
        "gram_nonzero_entry_count": 0,
        "self_orthogonal_flag": 1,
        "self_dual_flag": 1,
        "lagrangian_selector_flag": 1,
        "euler_zero_word_count": 2048,
        "euler_one_word_count": 2048,
        "punctured_length": 23,
        "punctured_word_count": 4096,
        "punctured_rank": 12,
        "punctured_min_nonzero_weight": 7,
        "punctured_weight7_count": 253,
        "punctured_weight8_count": 506,
        "punctured_weight11_count": 1288,
        "punctured_weight12_count": 1288,
        "punctured_weight15_count": 506,
        "punctured_weight16_count": 253,
        "punctured_weight23_count": 1,
        "shortened_euler_zero_word_count": 2048,
        "shortened_euler_zero_rank": 11,
        "shortened_euler_zero_min_nonzero_weight": 8,
        "euler_one_coset_word_count": 2048,
        "euler_one_coset_affine_dimension": 11,
        "euler_one_coset_min_weight": 7,
        "external_selector_boundary_flag": 1,
        "intrinsic_selector_proven_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23sel observable {name} mismatch")

    generators = [int(value) for value in np.asarray(matrices["generator_masks"]).tolist()]
    if generators != EXPECTED_GENERATORS:
        raise AssertionError("long_k23sel generator mask mismatch")
    if gf2_rank_masks(generators, 24) != 12:
        raise AssertionError("long_k23sel generator rank mismatch")
    if int(np.count_nonzero(np.asarray(matrices["gram_matrix"]))) != 0:
        raise AssertionError("long_k23sel Gram matrix is not zero")
    full_hist = {
        int(row["weight"]): int(row["word_count"])
        for row in rows_from_table(np.asarray(tables["weight_histogram_table"]), HIST_COLUMNS)
    }
    if full_hist != EXPECTED_FULL_HIST:
        raise AssertionError("long_k23sel full histogram mismatch")
    punctured_hist = {
        int(row["weight"]): int(row["word_count"])
        for row in rows_from_table(np.asarray(tables["punctured_weight_histogram_table"]), HIST_COLUMNS)
    }
    if punctured_hist != EXPECTED_PUNCTURED_HIST:
        raise AssertionError("long_k23sel punctured histogram mismatch")
    euler_hist = {
        (int(row["euler_bit"]), int(row["weight"])): int(row["word_count"])
        for row in rows_from_table(np.asarray(tables["euler_histogram_table"]), EULER_HIST_COLUMNS)
    }
    if euler_hist != EXPECTED_EULER_HIST:
        raise AssertionError("long_k23sel Euler histogram mismatch")
    if len(np.asarray(matrices["codeword_masks"])) != 4096:
        raise AssertionError("long_k23sel codeword count mismatch")
    if len(np.asarray(matrices["punctured_codeword_masks"])) != 4096:
        raise AssertionError("long_k23sel punctured codeword count mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23sel.manifest@1":
        raise AssertionError("long_k23sel manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23sel manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23sel manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23sel index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23sel index report sha mismatch")

    return {
        "schema": "long.k23sel.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23sel(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
