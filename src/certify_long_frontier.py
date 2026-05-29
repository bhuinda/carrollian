from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_frontier import (
        CARD_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_ANOM_REPORT,
        LONG_AUTO_REPORT,
        LONG_CLUSTER_REPORT,
        LONG_INV_REPORT,
        LONG_INV_EXHAUST_REPORT,
        LONG_MAT_REPORT,
        LONG_ORAC_OBS,
        LONG_ORAC_REPORT,
        LONG_ORAC_TABLES,
        LONG_MEASURE_REPORT,
        LONG_PATHS_REPORT,
        LONG_POBJ_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_frontier import (
        CARD_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_ANOM_REPORT,
        LONG_AUTO_REPORT,
        LONG_CLUSTER_REPORT,
        LONG_INV_REPORT,
        LONG_INV_EXHAUST_REPORT,
        LONG_MAT_REPORT,
        LONG_ORAC_OBS,
        LONG_ORAC_REPORT,
        LONG_ORAC_TABLES,
        LONG_MEASURE_REPORT,
        LONG_PATHS_REPORT,
        LONG_POBJ_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
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


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_frontier() -> dict[str, Any]:
    expected = build_payloads()
    frontier_payload = load_json(OUT_DIR / "frontier.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if frontier_payload != expected["frontier"]:
        raise AssertionError("long_frontier frontier JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_frontier cert mismatch")
    for filename, key in {
        "cards.csv": "cards_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_frontier {filename} mismatch")

    for key, expected_array in {
        "card_table": expected["card_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_frontier table mismatch: {key}")

    if report.get("schema") != "long.frontier.report@1":
        raise AssertionError("long_frontier report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_frontier report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_frontier all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_frontier checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_frontier report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_frontier report hash mismatch")

    csv_shapes = [
        ("cards.csv", CARD_COLUMNS, 13),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_frontier {filename} shape mismatch")

    table_shapes = {
        "card_table": (13, len(CARD_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_frontier {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "card_count": 13,
        "guardrail_closed_count": 12,
        "frontier_open_count": 1,
        "next_card_count": 1,
        "oracle_input_count": 31,
        "oracle_certified_input_count": 31,
        "oracle_resolved_surface_count": 29,
        "oracle_open_boundary_count": 22,
        "oracle_inventory_update_needed_flag": 0,
        "matrix_guardrail_closed_flag": 1,
        "sector11_guardrail_closed_flag": 1,
        "c2_guardrail_closed_flag": 1,
        "anomaly_guardrail_closed_flag": 1,
        "automorphic_guardrail_closed_flag": 1,
        "matrix_boundary_guardrail_closed_flag": 1,
        "cluster_reopened_count": 6,
        "cluster_seam_candidate_count": 94,
        "cluster_top_cluster_code": 5,
        "path_object_decided_flag": 1,
        "path_object_closed_flag": 0,
        "raw_product_family_decided_flag": 1,
        "measure_boundary_decided_flag": 1,
        "scoped_measure_law_flag": 1,
        "raw_product_family_materialized_flag": 0,
        "h16_materialized_profunctor_flag": 0,
        "h16_current_model_obstruction_flag": 1,
        "raw_paths_exhaustive_flag": 0,
        "full_raw_measure_certified_flag": 0,
        "highest_yield_target_code": 12,
        "highest_token_reduction_code": 4,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_frontier observable {key} mismatch")

    card_rows = rows_from_table(np.asarray(tables["card_table"]), CARD_COLUMNS)
    open_targets = [
        row["target_code"]
        for row in sorted(
            [row for row in card_rows if row["status_code"] == 1],
            key=lambda row: row["rank_code"],
        )
    ]
    if open_targets != [12]:
        raise AssertionError("long_frontier open target order mismatch")
    next_rows = [row for row in card_rows if row["next_flag"] == 1]
    if len(next_rows) != 1 or next_rows[0]["target_code"] != 12:
        raise AssertionError("long_frontier next target mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_orac_report": LONG_ORAC_REPORT,
        "long_orac_obs": LONG_ORAC_OBS,
        "long_orac_tables": LONG_ORAC_TABLES,
        "long_inv_report": LONG_INV_REPORT,
        "long_pobj_report": LONG_POBJ_REPORT,
        "long_paths_report": LONG_PATHS_REPORT,
        "long_measure_report": LONG_MEASURE_REPORT,
        "long_inv_exhaust_report": LONG_INV_EXHAUST_REPORT,
        "long_anom_report": LONG_ANOM_REPORT,
        "long_auto_report": LONG_AUTO_REPORT,
        "long_mat_report": LONG_MAT_REPORT,
        "long_cluster_report": LONG_CLUSTER_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.frontier.manifest@1":
        raise AssertionError("long_frontier manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_frontier manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_frontier manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_frontier missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_frontier proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_frontier proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.frontier.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "target_code_map": witness.get("target_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_frontier(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
