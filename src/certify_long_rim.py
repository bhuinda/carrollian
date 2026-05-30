from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_rim import (
        ATLAS_CSV,
        ATLAS_REPORT,
        CLASS_COLUMNS,
        HYPERBOLIC_EDGES,
        HYPERBOLIC_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        ORBIT_COLUMNS,
        OUT_DIR,
        RANK_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_rim import (
        ATLAS_CSV,
        ATLAS_REPORT,
        CLASS_COLUMNS,
        HYPERBOLIC_EDGES,
        HYPERBOLIC_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        ORBIT_COLUMNS,
        OUT_DIR,
        RANK_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )


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


def validate_long_rim() -> dict[str, Any]:
    expected = build_payloads()
    rim_classification = load_json(OUT_DIR / "rim_classification.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if rim_classification != expected["rim_classification"]:
        raise AssertionError("long_rim rim_classification JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rim cert mismatch")
    for filename, key in {
        "class.csv": "class_csv",
        "orbit.csv": "orbit_csv",
        "rank.csv": "rank_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rim {filename} mismatch")

    for key, expected_array in {
        "class_table": expected["class_table"],
        "orbit_table": expected["orbit_table"],
        "rank_table": expected["rank_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rim table mismatch: {key}")

    if report.get("schema") != "long.rim.report@1":
        raise AssertionError("long_rim report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rim report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rim all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rim checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rim report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rim report hash mismatch")

    csv_shapes = [
        ("class.csv", CLASS_COLUMNS, 63),
        ("orbit.csv", ORBIT_COLUMNS, 124),
        ("rank.csv", RANK_COLUMNS, len(expected["rank_table"])),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rim {filename} shape mismatch")

    table_shapes = {
        "class_table": (63, len(CLASS_COLUMNS)),
        "orbit_table": (124, 6),
        "rank_table": (len(expected["rank_table"]), len(RANK_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_rim {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "atom_count": 20,
        "johnson_edge_count": 90,
        "johnson_diameter": 3,
        "complement_pair_count": 10,
        "normalized_oriented_rim_count": 177408,
        "normalized_unoriented_rim_count": 88704,
        "s6_automorphism_count": 720,
        "s6_rim_orbit_count": 124,
        "defect_polynomial_class_count": 63,
        "golden_defect_class_count": 1,
        "golden_defect_orbit_count": 1,
        "golden_defect_unoriented_rim_count": 144,
        "golden_defect_oriented_rim_count": 288,
        "golden_defect_canonical_flag": 0,
        "defect_phase_flag": 1,
        "golden_special_phase_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_rim observable {key} mismatch")

    class_rows = rows_from_table(np.asarray(tables["class_table"]), CLASS_COLUMNS)
    orbit_rows = rows_from_table(np.asarray(tables["orbit_table"]), [
        "orbit_id",
        "class_id",
        "orbit_rim_count",
        "rank",
        "nullity",
        "golden_flag",
    ])
    if sum(row["rim_count"] for row in class_rows) != 88704:
        raise AssertionError("long_rim class rim total mismatch")
    if sum(row["orbit_rim_count"] for row in orbit_rows) != 88704:
        raise AssertionError("long_rim orbit rim total mismatch")
    golden_classes = [row for row in class_rows if row["golden_flag"] == 1]
    golden_orbits = [row for row in orbit_rows if row["golden_flag"] == 1]
    if len(golden_classes) != 1 or golden_classes[0]["rank"] != 10:
        raise AssertionError("long_rim golden class mismatch")
    if len(golden_orbits) != 1 or golden_orbits[0]["orbit_rim_count"] != 144:
        raise AssertionError("long_rim golden orbit mismatch")
    if len({row["class_id"] for row in class_rows}) != 63:
        raise AssertionError("long_rim class ids not unique")
    if len({row["orbit_id"] for row in orbit_rows}) != 124:
        raise AssertionError("long_rim orbit ids not unique")

    if manifest != expected["manifest"]:
        raise AssertionError("long_rim manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_rim manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rim manifest report hash mismatch")
    inputs = report.get("inputs", {})
    assert_file_hash(inputs["atlas_report"], ATLAS_REPORT, "atlas_report")
    assert_file_hash(inputs["atlas_csv"], ATLAS_CSV, "atlas_csv")
    assert_file_hash(inputs["hyperbolic_report"], HYPERBOLIC_REPORT, "hyperbolic_report")
    assert_file_hash(inputs["hyperbolic_edges"], HYPERBOLIC_EDGES, "hyperbolic_edges")

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_rim index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rim index report hash mismatch")

    return {
        "schema": "long.rim.verification@1",
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
    print(json.dumps(validate_long_rim(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
