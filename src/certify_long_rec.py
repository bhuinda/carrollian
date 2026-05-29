from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_rec import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        LONG_BASIS_DIR,
        LONG_BASIS_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_EDGE_COLUMNS,
        WEAK_OWNER_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_rec import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        LONG_BASIS_DIR,
        LONG_BASIS_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_EDGE_COLUMNS,
        WEAK_OWNER_COLUMNS,
        build_payloads,
        self_hash,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_long_rec() -> dict[str, Any]:
    expected = build_payloads()
    rec = load_json(OUT_DIR / "rec.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if rec != expected["rec"]:
        raise AssertionError("long_rec rec JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rec cert mismatch")
    for filename, key in {
        "owner.csv": "owner_csv",
        "edge.csv": "edge_csv",
        "weak_owner.csv": "weak_owner_csv",
        "weak_edge.csv": "weak_edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rec {filename} mismatch")

    for key, expected_array in {
        "owner_table": expected["owner_table"],
        "edge_table": expected["edge_table"],
        "weak_owner_table": expected["weak_owner_table"],
        "weak_edge_table": expected["weak_edge_table"],
        "observable_table": expected["observable_table"],
        "owner_grid": expected["owner_grid"],
        "owner_frontier": expected["owner_frontier"],
        "component_ids": expected["component_ids"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rec table mismatch: {key}")

    if report.get("schema") != "long.rec.report@1":
        raise AssertionError("long_rec report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rec report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rec all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rec checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rec report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rec report hash mismatch")

    owner_header, owner_rows = read_csv(OUT_DIR / "owner.csv")
    edge_header, edge_rows = read_csv(OUT_DIR / "edge.csv")
    weak_owner_header, weak_owner_rows = read_csv(OUT_DIR / "weak_owner.csv")
    weak_edge_header, weak_edge_rows = read_csv(OUT_DIR / "weak_edge.csv")
    if owner_header != OWNER_COLUMNS or len(owner_rows) != 259:
        raise AssertionError("long_rec owner CSV shape mismatch")
    if edge_header != EDGE_COLUMNS or len(edge_rows) != 642:
        raise AssertionError("long_rec edge CSV shape mismatch")
    if weak_owner_header != WEAK_OWNER_COLUMNS or len(weak_owner_rows) != 13:
        raise AssertionError("long_rec weak owner CSV shape mismatch")
    if weak_edge_header != WEAK_EDGE_COLUMNS or len(weak_edge_rows) != 8:
        raise AssertionError("long_rec weak edge CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "basis_count": 259,
        "frontier_cell_count": 970_225,
        "active_owner_count": 259,
        "owner_cell_count_sum": 970_225,
        "owner_cell_count_min": 1,
        "owner_cell_count_max": 197_910,
        "frontier_sum": 404_111_708,
        "frontier_square_sum": 233_520_639_830,
        "frontier_min": 0,
        "frontier_max": 893,
        "transition_node_count": 259,
        "transition_edge_count": 642,
        "transition_component_count": 1,
        "transition_component_max_size": 259,
        "transition_degree_min": 3,
        "transition_degree_max": 13,
        "transition_weighted_degree_min": 3,
        "transition_weighted_degree_max": 1736,
        "source0_boundary_contact_count": 12_707,
        "source1_boundary_contact_count": 5_410,
        "boundary_contact_count": 18_117,
        "directed_boundary_contact_count": 36_234,
        "self_neighbor_contact_count": 1_920_363,
        "owner_lln_var_den": 941_336_550_625,
        "owner_lln_var_num_sum": 837_883_117_934,
        "edge_lln_var_den": 328_225_689,
        "edge_lln_var_num_sum": 321_236_252,
        "weak_owner_class_count": 5,
        "weak_owner_cell_count_max": 718_941,
        "weak_owner_lln_var_num_sum": 361_363_966_216,
        "weak_edge_class_pair_count": 8,
        "weak_edge_lln_var_num_sum": 135_408_656,
        "owner_grid_complete": 1,
        "owner_frontier_regenerates_long_basis": 1,
        "transition_symmetric": 1,
        "transition_row_positive": 1,
        "long_basis_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_rec observable {key} mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_basis_report": LONG_BASIS_REPORT,
        "long_basis_tables": LONG_BASIS_DIR / "tables.npz",
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.rec.manifest@1":
        raise AssertionError("long_rec manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rec manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_rec manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_rec missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rec index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_rec index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.rec.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "line": witness.get("line"),
            "owner_partition": {
                "active_owner_count": witness.get("owner_partition", {}).get(
                    "active_owner_count"
                ),
                "owner_cell_count_min": witness.get("owner_partition", {}).get(
                    "owner_cell_count_min"
                ),
                "owner_cell_count_max": witness.get("owner_partition", {}).get(
                    "owner_cell_count_max"
                ),
            },
            "transition_kernel": witness.get("transition_kernel"),
            "finite_lln": witness.get("finite_lln"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_rec(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
