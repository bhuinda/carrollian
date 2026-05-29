from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_spec import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_DIGEST_COLUMNS,
        INDEX_PATH,
        LONG_ABSORB_MATRIX,
        LONG_ABSORB_REPORT,
        LONG_ABSORB_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RESISTANCE_COLUMNS,
        RESISTANCE_DIGEST_COLUMNS,
        SCHUR_COLUMNS,
        SCHUR_DIGEST_COLUMNS,
        SPECTRAL_COLUMNS,
        SPECTRAL_DIGEST_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        edge_fraction_text,
        resistance_fraction_text,
        rows_from_table,
        schur_fraction_text,
        self_hash,
        spectral_fraction_text,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_spec import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_DIGEST_COLUMNS,
        INDEX_PATH,
        LONG_ABSORB_MATRIX,
        LONG_ABSORB_REPORT,
        LONG_ABSORB_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RESISTANCE_COLUMNS,
        RESISTANCE_DIGEST_COLUMNS,
        SCHUR_COLUMNS,
        SCHUR_DIGEST_COLUMNS,
        SPECTRAL_COLUMNS,
        SPECTRAL_DIGEST_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        edge_fraction_text,
        resistance_fraction_text,
        rows_from_table,
        schur_fraction_text,
        self_hash,
        spectral_fraction_text,
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


def digest_rows(table: np.ndarray, columns: list[str]) -> list[list[int]]:
    rows = rows_from_table(table, columns)
    return [[row[column] for column in columns] for row in rows]


def validate_long_spec() -> dict[str, Any]:
    expected = build_payloads()
    spec = load_json(OUT_DIR / "spec.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if spec != expected["spec"]:
        raise AssertionError("long_spec spec JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_spec cert mismatch")
    for filename, key in {
        "schur.csv": "schur_csv",
        "edge.csv": "edge_csv",
        "resistance.csv": "resistance_csv",
        "spectral.csv": "spectral_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_spec {filename} mismatch")

    for key, expected_array in {
        "schur_digest_table": expected["schur_digest_table"],
        "edge_digest_table": expected["edge_digest_table"],
        "resistance_digest_table": expected["resistance_digest_table"],
        "spectral_digest_table": expected["spectral_digest_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_spec table mismatch: {key}")

    if report.get("schema") != "long.spec.report@1":
        raise AssertionError("long_spec report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_spec report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_spec all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_spec checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_spec report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_spec report hash mismatch")

    schur_header, schur_rows = read_csv(OUT_DIR / "schur.csv")
    edge_header, edge_rows = read_csv(OUT_DIR / "edge.csv")
    resistance_header, resistance_rows = read_csv(OUT_DIR / "resistance.csv")
    spectral_header, spectral_rows = read_csv(OUT_DIR / "spectral.csv")
    if schur_header != SCHUR_COLUMNS or len(schur_rows) != 9:
        raise AssertionError("long_spec schur CSV shape mismatch")
    if edge_header != EDGE_COLUMNS or len(edge_rows) != 3:
        raise AssertionError("long_spec edge CSV shape mismatch")
    if resistance_header != RESISTANCE_COLUMNS or len(resistance_rows) != 3:
        raise AssertionError("long_spec resistance CSV shape mismatch")
    if spectral_header != SPECTRAL_COLUMNS or len(spectral_rows) != 4:
        raise AssertionError("long_spec spectral CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "active_component_count": 3,
        "boundary0_count": 1_342,
        "boundary1_count": 864,
        "boundary2_count": 2_378,
        "boundary_total_count": 4_584,
        "schur_entry_count": 9,
        "schur_edge_count": 3,
        "schur_rank_mod_1000000007": 2,
        "schur_rank_mod_1000000009": 2,
        "schur_row_sum_zero_flag": 1,
        "schur_symmetric_flag": 1,
        "schur_cofactor_equal_flag": 1,
        "schur_positive_edge_flag": 1,
        "spectral_invariant_count": 4,
        "trace_num_digits": 258,
        "trace_den_digits": 255,
        "trace_num_mod_1000000007": 338_120_233,
        "trace_den_mod_1000000007": 37_512_555,
        "tree_num_digits": 260,
        "tree_den_digits": 255,
        "tree_num_mod_1000000007": 489_501_615,
        "tree_den_mod_1000000007": 75_025_110,
        "pseudodet_num_digits": 260,
        "pseudodet_den_digits": 255,
        "pseudodet_num_mod_1000000007": 489_501_615,
        "pseudodet_den_mod_1000000007": 25_008_370,
        "discriminant_num_digits": 515,
        "discriminant_den_digits": 510,
        "discriminant_num_mod_1000000007": 403_262_461,
        "discriminant_den_mod_1000000007": 772_777_688,
        "discriminant_positive_flag": 1,
        "discriminant_rational_square_flag": 0,
        "resistance_pair_count": 3,
        "resistance_num_digit_min": 258,
        "resistance_num_digit_max": 258,
        "resistance_den_digit_min": 260,
        "resistance_den_digit_max": 260,
        "long_absorb_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_spec observable {key} mismatch")

    expected_schur_signature = [
        [0, 0, 258, 255, 65_114_317, 75_025_110, 983_636_213, 814_085_260, 1],
        [0, 1, 256, 254, 310_812_724, 253_126_048, 518_584_879, 867_253_560, 0],
        [0, 2, 258, 255, 475_380_363, 75_025_110, 570_326_817, 814_085_260, 0],
        [1, 0, 256, 254, 310_812_724, 253_126_048, 518_584_879, 867_253_560, 0],
        [1, 1, 256, 254, 200_562_526, 253_126_048, 554_218_912, 867_253_560, 1],
        [1, 2, 256, 254, 488_624_757, 253_126_048, 927_196_227, 867_253_560, 0],
        [2, 0, 258, 255, 475_380_363, 75_025_110, 570_326_817, 814_085_260, 0],
        [2, 1, 256, 254, 488_624_757, 253_126_048, 927_196_227, 867_253_560, 0],
        [2, 2, 258, 255, 797_625_560, 75_025_110, 176_963_942, 814_085_260, 1],
    ]
    if digest_rows(np.asarray(tables["schur_digest_table"]), SCHUR_DIGEST_COLUMNS) != expected_schur_signature:
        raise AssertionError("long_spec schur digest fingerprint mismatch")

    if hashlib.sha256(schur_fraction_text(schur_rows).encode("ascii")).hexdigest() != (
        "0f9d997c3b976dce091a82ce44527c4c2b7df14629fe056c98427d570e27d07d"
    ):
        raise AssertionError("long_spec schur hash mismatch")
    if hashlib.sha256(edge_fraction_text(edge_rows).encode("ascii")).hexdigest() != (
        "323b2bcdda4e7771c1c910a2827c5d390adbec86c9e197f7ea937874ec6675cc"
    ):
        raise AssertionError("long_spec edge hash mismatch")
    if hashlib.sha256(
        resistance_fraction_text(resistance_rows).encode("ascii")
    ).hexdigest() != (
        "c91a0b33dc5a2cd6d0ed32d870a2a642972f6dbad2f4c3b2609516563e103de4"
    ):
        raise AssertionError("long_spec resistance hash mismatch")
    if hashlib.sha256(
        spectral_fraction_text(spectral_rows).encode("ascii")
    ).hexdigest() != (
        "9033e3c8a751478502449e29710f132425cbf1aedf99ab3e065a8c7201197633"
    ):
        raise AssertionError("long_spec spectral hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_absorb_report": LONG_ABSORB_REPORT,
        "long_absorb_matrix": LONG_ABSORB_MATRIX,
        "long_absorb_tables": LONG_ABSORB_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.spec.manifest@1":
        raise AssertionError("long_spec manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_spec manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_spec manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_spec missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_spec index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_spec index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.spec.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "schur": witness.get("schur"),
            "spectrum": witness.get("spectrum"),
            "resistance": witness.get("resistance"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_spec(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
