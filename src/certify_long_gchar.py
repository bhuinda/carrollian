from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_gchar import (
        CHAR_COLUMNS,
        CLASS_COUNT,
        DECOMP_COLUMNS,
        E_COLUMNS,
        FIELD_PRIME,
        GAMMA_ALG_REPORT,
        GAMMA_ALG_TABLES,
        GAMMA_PERMCHAR_CSV,
        GAMMA_SOURCE_REPORT,
        GAP_CODES,
        GAP_COLUMNS,
        GROUP_ORDER,
        IDEMP_COLUMNS,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_gchar import (
        CHAR_COLUMNS,
        CLASS_COUNT,
        DECOMP_COLUMNS,
        E_COLUMNS,
        FIELD_PRIME,
        GAMMA_ALG_REPORT,
        GAMMA_ALG_TABLES,
        GAMMA_PERMCHAR_CSV,
        GAMMA_SOURCE_REPORT,
        GAP_CODES,
        GAP_COLUMNS,
        GROUP_ORDER,
        IDEMP_COLUMNS,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


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


def validate_long_gchar() -> dict[str, Any]:
    expected = build_payloads()
    gamma_character = load_json(OUT_DIR / "gamma_character.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if gamma_character != expected["gamma_character"]:
        raise AssertionError("long_gchar character JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_gchar cert mismatch")
    for filename, key in {
        "gamma_modular_character_table.csv": "character_csv",
        "primitive_idempotent.csv": "idempotent_csv",
        "six_orbit_permutation_decomposition.csv": "decomposition_csv",
        "balanced_Ei_irrep_decomposition.csv": "e_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_gchar {filename} mismatch")

    for key, expected_array in {
        "char_table": expected["char_table"],
        "idempotent_table": expected["idempotent_table"],
        "decomp_table": expected["decomp_table"],
        "e_table": expected["e_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
        "characters": expected["characters"],
        "idempotents": expected["idempotents"],
        "central_characters": expected["central_characters"],
        "degrees": expected["degrees"],
        "roots": expected["roots"],
        "split_weights": expected["weights"],
        "charpoly": expected["charpoly"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_gchar table mismatch: {key}")

    if report.get("schema") != "long.gchar.report@1":
        raise AssertionError("long_gchar report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_gchar report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_gchar all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_gchar checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gchar report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_gchar report hash mismatch")

    csv_shapes = [
        ("gamma_modular_character_table.csv", CHAR_COLUMNS, CLASS_COUNT),
        ("primitive_idempotent.csv", IDEMP_COLUMNS, CLASS_COUNT),
        ("six_orbit_permutation_decomposition.csv", DECOMP_COLUMNS, 6 * CLASS_COUNT),
        ("balanced_Ei_irrep_decomposition.csv", E_COLUMNS, 8),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_gchar {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "field_prime": FIELD_PRIME,
        "class_count": CLASS_COUNT,
        "root_count": CLASS_COUNT,
        "distinct_root_count": CLASS_COUNT,
        "primitive_idempotent_count": CLASS_COUNT,
        "degree_square_sum": GROUP_ORDER,
        "orthogonality_pass_flag": 1,
        "homomorphism_pass_flag": 1,
        "idempotent_pass_flag": 1,
        "permutation_character_count": 6,
        "permutation_decomposition_row_count": 6 * CLASS_COUNT,
        "permutation_dimension_pass_count": 6,
        "e_module_row_count": 8,
        "e_decomposition_present_count": 0,
        "next_gap_code": 6,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_gchar observable {key} mismatch")

    char_rows = rows_from_table(np.asarray(tables["char_table"]), CHAR_COLUMNS)
    if [row["irrep_id"] for row in char_rows] != list(range(CLASS_COUNT)):
        raise AssertionError("long_gchar irrep ids mismatch")
    degrees = np.asarray(tables["degrees"], dtype=np.int64)
    if int(np.sum(degrees * degrees)) != GROUP_ORDER:
        raise AssertionError("long_gchar degree square sum mismatch")
    if char_rows[0]["degree"] != 1:
        raise AssertionError("long_gchar first degree mismatch")
    if any(char_rows[0][f"char_c{class_id}_mod"] != 1 for class_id in range(CLASS_COUNT)):
        raise AssertionError("long_gchar trivial character row mismatch")

    decomp_rows = rows_from_table(np.asarray(tables["decomp_table"]), DECOMP_COLUMNS)
    for orbit_id in range(6):
        rows_for_orbit = [row for row in decomp_rows if row["orbit_id"] == orbit_id]
        if len(rows_for_orbit) != CLASS_COUNT:
            raise AssertionError("long_gchar orbit decomposition row count mismatch")
        dimension = sum(row["dimension_contribution"] for row in rows_for_orbit)
        expected_dimension = [384, 192, 144, 576, 512, 768][orbit_id]
        if dimension != expected_dimension:
            raise AssertionError("long_gchar orbit dimension reconstruction mismatch")

    e_rows = rows_from_table(np.asarray(tables["e_table"]), E_COLUMNS)
    if [row["e_id"] for row in e_rows] != list(range(8)):
        raise AssertionError("long_gchar E ids mismatch")
    if sum(row["open_flag"] for row in e_rows) != 8:
        raise AssertionError("long_gchar E open vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 1, 1, 0, 0]:
        raise AssertionError("long_gchar gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 0, 1, 0]:
        raise AssertionError("long_gchar gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_gchar manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_gchar manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gchar manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_b3alg": GAMMA_ALG_REPORT,
        "long_b3mod": GAMMA_SOURCE_REPORT,
        "gamma_alg_tables": GAMMA_ALG_TABLES,
        "gamma_permutation_character_csv": GAMMA_PERMCHAR_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_gchar index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gchar index report hash mismatch")

    return {
        "schema": "long.gchar.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_gchar(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
