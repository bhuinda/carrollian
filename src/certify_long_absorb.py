from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_absorb import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_FLOW_REPORT,
        LONG_FLOW_TABLES,
        LONG_LAP_TABLES,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        MATRIX_COLUMNS,
        MATRIX_DIGEST_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        SHELL_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        matrix_fraction_text,
        owner_digest_text,
        rows_from_table,
        self_hash,
        shell_digest_text,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_absorb import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_FLOW_REPORT,
        LONG_FLOW_TABLES,
        LONG_LAP_TABLES,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        MATRIX_COLUMNS,
        MATRIX_DIGEST_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        SHELL_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        matrix_fraction_text,
        owner_digest_text,
        rows_from_table,
        self_hash,
        shell_digest_text,
    )


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


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def validate_long_absorb() -> dict[str, Any]:
    expected = build_payloads()
    absorb = load_json(OUT_DIR / "absorb.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if absorb != expected["absorb"]:
        raise AssertionError("long_absorb absorb JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_absorb cert mismatch")
    for filename, key in {
        "matrix.csv": "matrix_csv",
        "owner.csv": "owner_csv",
        "shell.csv": "shell_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_absorb {filename} mismatch")

    for key, expected_array in {
        "matrix_digest_table": expected["matrix_digest_table"],
        "owner_table": expected["owner_table"],
        "shell_table": expected["shell_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_absorb table mismatch: {key}")

    if report.get("schema") != "long.absorb.report@1":
        raise AssertionError("long_absorb report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_absorb report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_absorb all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_absorb checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_absorb report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_absorb report hash mismatch")

    matrix_header, matrix_rows = read_csv(OUT_DIR / "matrix.csv")
    owner_header, owner_rows = read_csv(OUT_DIR / "owner.csv")
    shell_header, shell_rows = read_csv(OUT_DIR / "shell.csv")
    if matrix_header != MATRIX_COLUMNS or len(matrix_rows) != 9:
        raise AssertionError("long_absorb matrix CSV shape mismatch")
    if owner_header != OWNER_COLUMNS or len(owner_rows) != 208:
        raise AssertionError("long_absorb owner CSV shape mismatch")
    if shell_header != SHELL_COLUMNS or len(shell_rows) != 7:
        raise AssertionError("long_absorb shell CSV shape mismatch")
    if np.asarray(tables["matrix_digest_table"]).shape != (
        9,
        len(MATRIX_DIGEST_COLUMNS),
    ):
        raise AssertionError("long_absorb matrix digest table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "full_owner_count": 259,
        "active_owner_count": 51,
        "inactive_owner_count": 208,
        "active_component_count": 3,
        "inactive_dirichlet_rank": 208,
        "dirichlet_det_digit_count": 270,
        "dirichlet_det_mod_1000000007": 328_173_059,
        "dirichlet_det_mod_1000000009": 543_927_589,
        "dirichlet_det_positive_flag": 1,
        "absorption_matrix_entry_count": 9,
        "transfer_total_boundary_count": 4_584,
        "transfer_source0_boundary_count": 1_342,
        "transfer_source1_boundary_count": 864,
        "transfer_source2_boundary_count": 2_378,
        "transfer_symmetry_flag": 1,
        "transfer_row_sum_match_flag": 1,
        "transfer_col_sum_match_flag": 1,
        "probability_row_sum_violation_count": 0,
        "inactive_shell_count": 7,
        "inactive_shell_max_distance": 7,
        "inactive_weighted_degree_sum": 20_392,
        "inactive_active_boundary_sum": 4_584,
        "inactive_internal_boundary_sum": 15_808,
        "dominant0_owner_count": 86,
        "dominant1_owner_count": 2,
        "dominant2_owner_count": 120,
        "shell1_dominant0_owner_count": 27,
        "shell1_dominant1_owner_count": 2,
        "shell1_dominant2_owner_count": 23,
        "diagonal_return_num_digits": 259,
        "diagonal_return_den_digits": 255,
        "diagonal_return_num_mod_1000000007": 619_430_690,
        "diagonal_return_den_mod_1000000007": 37_512_555,
        "offdiagonal_transfer_num_digits": 258,
        "offdiagonal_transfer_den_digits": 255,
        "offdiagonal_transfer_num_mod_1000000007": 338_120_233,
        "offdiagonal_transfer_den_mod_1000000007": 37_512_555,
        "long_flow_input_certified": 1,
        "long_rec_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_absorb observable {key} mismatch")

    matrix_digest_rows = rows_from_table(
        np.asarray(tables["matrix_digest_table"]),
        MATRIX_DIGEST_COLUMNS,
    )
    expected_matrix_digest = [
        [0, 0, 258, 255, 618_582_603, 75_025_110, 518_772_888, 814_085_260, 1],
        [0, 1, 256, 254, 689_187_283, 253_126_048, 481_415_130, 867_253_560, 0],
        [0, 2, 258, 255, 524_619_644, 75_025_110, 429_673_192, 814_085_260, 0],
        [1, 0, 256, 254, 689_187_283, 253_126_048, 481_415_130, 867_253_560, 0],
        [1, 1, 257, 254, 500_341_420, 253_126_048, 752_850_196, 867_253_560, 1],
        [1, 2, 256, 254, 511_375_250, 253_126_048, 72_803_782, 867_253_560, 0],
        [2, 0, 258, 255, 524_619_644, 75_025_110, 429_673_192, 814_085_260, 0],
        [2, 1, 256, 254, 511_375_250, 253_126_048, 72_803_782, 867_253_560, 0],
        [2, 2, 259, 255, 612_084_781, 75_025_110, 717_766_923, 814_085_260, 1],
    ]
    if [
        [row[column] for column in MATRIX_DIGEST_COLUMNS]
        for row in matrix_digest_rows
    ] != expected_matrix_digest:
        raise AssertionError("long_absorb matrix digest fingerprint mismatch")

    matrix_text_rows = [
        {
            "source_component_id": row["source_component_id"],
            "absorbing_component_id": row["absorbing_component_id"],
            "flow_num": row["flow_num"],
            "flow_den": row["flow_den"],
        }
        for row in matrix_rows
    ]
    matrix_text_hash = hashlib.sha256(
        matrix_fraction_text(matrix_text_rows).encode("ascii")
    ).hexdigest()
    if matrix_text_hash != "7dde8dfc5c2306b4a5f55b3176ab7e19c2fba7457f2da2ac3cfa00d625cc973b":
        raise AssertionError("long_absorb matrix text hash mismatch")
    owner_table_rows = rows_from_table(np.asarray(tables["owner_table"]), OWNER_COLUMNS)
    shell_table_rows = rows_from_table(np.asarray(tables["shell_table"]), SHELL_COLUMNS)
    if hashlib.sha256(owner_digest_text(owner_table_rows).encode("ascii")).hexdigest() != (
        "ea8e86de6b25fa8c775ff22e45c508ad41a41085f4414844b8ff978498c08bdb"
    ):
        raise AssertionError("long_absorb owner digest hash mismatch")
    if hashlib.sha256(shell_digest_text(shell_table_rows).encode("ascii")).hexdigest() != (
        "99b44a0e967e9ffdc1166568e824c695f4a8ea45c21e8d41a18955da4c7c48f1"
    ):
        raise AssertionError("long_absorb shell digest hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_flow_report": LONG_FLOW_REPORT,
        "long_flow_tables": LONG_FLOW_TABLES,
        "long_lap_tables": LONG_LAP_TABLES,
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_tables": LONG_REC_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.absorb.manifest@1":
        raise AssertionError("long_absorb manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_absorb manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_absorb manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_absorb missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_absorb index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_absorb index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.absorb.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "dirichlet": witness.get("dirichlet"),
            "transfer": witness.get("transfer"),
            "inactive_owners": witness.get("inactive_owners"),
            "shells": witness.get("shells"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_absorb(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
