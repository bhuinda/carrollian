from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_llnind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LAYER_COLUMNS,
        LAYER_TEXT_HASH,
        LONG_GAPIND_BRIDGE,
        LONG_GAPIND_REGIME,
        LONG_GAPIND_REPORT,
        LONG_GAPIND_TABLES,
        LONG_LLN_ADDR,
        LONG_LLN_LLN,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_MIN_BASIS,
        LONG_MIN_COVER,
        LONG_MIN_REPORT,
        LONG_MIN_TABLES,
        LONG_NAT_DEPENDENCY,
        LONG_NAT_NATURALITY,
        LONG_NAT_REPORT,
        LONG_NAT_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        LONG_PROF_COMPOSE,
        LONG_PROF_OBJECT,
        LONG_PROF_PROFUNCTOR,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_RAW_FIBER,
        LONG_RAW_OWNER,
        LONG_RAW_REPORT,
        LONG_RAW_TABLES,
        LONG_UNIV_ARROW,
        LONG_UNIV_LAW,
        LONG_UNIV_NODE,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SEAM_COLUMNS,
        SEAM_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_llnind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LAYER_COLUMNS,
        LAYER_TEXT_HASH,
        LONG_GAPIND_BRIDGE,
        LONG_GAPIND_REGIME,
        LONG_GAPIND_REPORT,
        LONG_GAPIND_TABLES,
        LONG_LLN_ADDR,
        LONG_LLN_LLN,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_MIN_BASIS,
        LONG_MIN_COVER,
        LONG_MIN_REPORT,
        LONG_MIN_TABLES,
        LONG_NAT_DEPENDENCY,
        LONG_NAT_NATURALITY,
        LONG_NAT_REPORT,
        LONG_NAT_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        LONG_PROF_COMPOSE,
        LONG_PROF_OBJECT,
        LONG_PROF_PROFUNCTOR,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_RAW_FIBER,
        LONG_RAW_OWNER,
        LONG_RAW_REPORT,
        LONG_RAW_TABLES,
        LONG_UNIV_ARROW,
        LONG_UNIV_LAW,
        LONG_UNIV_NODE,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SEAM_COLUMNS,
        SEAM_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def validate_long_llnind() -> dict[str, Any]:
    expected = build_payloads()
    llnind_payload = load_json(OUT_DIR / "llnind.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if llnind_payload != expected["llnind"]:
        raise AssertionError("long_llnind llnind JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_llnind cert mismatch")
    for filename, key in {
        "layer.csv": "layer_csv",
        "seam.csv": "seam_csv",
        "bridge.csv": "bridge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_llnind {filename} mismatch")

    for key, expected_array in {
        "layer_table": expected["layer_table"],
        "seam_table": expected["seam_table"],
        "bridge_table": expected["bridge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_llnind table mismatch: {key}")

    if report.get("schema") != "long.llnind.report@1":
        raise AssertionError("long_llnind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_llnind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_llnind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_llnind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_llnind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_llnind report hash mismatch")

    csv_shapes = [
        ("layer.csv", LAYER_COLUMNS, 8),
        ("seam.csv", SEAM_COLUMNS, 8),
        ("bridge.csv", BRIDGE_COLUMNS, 1),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_llnind {filename} shape mismatch")

    table_shapes = {
        "layer_table": (8, len(LAYER_COLUMNS)),
        "seam_table": (8, len(SEAM_COLUMNS)),
        "bridge_table": (1, len(BRIDGE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_llnind {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "tensor_support_count": 1_414_965,
        "tensor_coeff_sum": 2_537_360,
        "checked_k_start": 1,
        "checked_k_end": 8,
        "profunctor_object_count": 9,
        "profunctor_count": 8,
        "profunctor_law_count": 92,
        "universal_node_count": 15,
        "universal_arrow_count": 10,
        "universal_law_count": 306,
        "forcing_basis_count": 74,
        "forced_law_count": 232,
        "naturality_law_count": 306,
        "profunctor_controlled_law_count": 194,
        "external_input_law_count": 112,
        "naturality_dependency_edge_count": 808,
        "probability_path_count": 288,
        "probability_sample_max": 16,
        "variance_shrink_count": 16,
        "raw_tensor_support_count": 1_414_965,
        "raw_coeff_sum": 2_537_360,
        "raw_path_count": 288,
        "gap_path_count": 208,
        "path_step_count": 3_128,
        "gap_regime_count": 4,
        "finite_gap_check_count": 131_586,
        "finite_gap_nonnegative_count": 131_586,
        "tail_formula_nonnegative_count": 26,
        "input_certified_count": 9,
        "seam_match_count": 8,
        "current_llnind_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_llnind observable {key} mismatch")

    if hashlib.sha256(
        digest_text(LAYER_COLUMNS, csv_rows["layer.csv"]).encode("ascii")
    ).hexdigest() != LAYER_TEXT_HASH:
        raise AssertionError("long_llnind layer hash mismatch")
    if hashlib.sha256(
        digest_text(SEAM_COLUMNS, csv_rows["seam.csv"]).encode("ascii")
    ).hexdigest() != SEAM_TEXT_HASH:
        raise AssertionError("long_llnind seam hash mismatch")
    if hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, csv_rows["bridge.csv"]).encode("ascii")
    ).hexdigest() != BRIDGE_TEXT_HASH:
        raise AssertionError("long_llnind bridge hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lln_report": LONG_LLN_REPORT,
        "long_lln_addr": LONG_LLN_ADDR,
        "long_lln_lln": LONG_LLN_LLN,
        "long_lln_tables": LONG_LLN_TABLES,
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_object": LONG_PROF_OBJECT,
        "long_prof_profunctor": LONG_PROF_PROFUNCTOR,
        "long_prof_compose": LONG_PROF_COMPOSE,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_univ_report": LONG_UNIV_REPORT,
        "long_univ_node": LONG_UNIV_NODE,
        "long_univ_arrow": LONG_UNIV_ARROW,
        "long_univ_law": LONG_UNIV_LAW,
        "long_univ_tables": LONG_UNIV_TABLES,
        "long_min_report": LONG_MIN_REPORT,
        "long_min_basis": LONG_MIN_BASIS,
        "long_min_cover": LONG_MIN_COVER,
        "long_min_tables": LONG_MIN_TABLES,
        "long_nat_report": LONG_NAT_REPORT,
        "long_nat_naturality": LONG_NAT_NATURALITY,
        "long_nat_dependency": LONG_NAT_DEPENDENCY,
        "long_nat_tables": LONG_NAT_TABLES,
        "long_prob_report": LONG_PROB_REPORT,
        "long_prob_dist": LONG_PROB_DIST,
        "long_prob_moment": LONG_PROB_MOMENT,
        "long_prob_tables": LONG_PROB_TABLES,
        "long_raw_report": LONG_RAW_REPORT,
        "long_raw_owner": LONG_RAW_OWNER,
        "long_raw_fiber": LONG_RAW_FIBER,
        "long_raw_tables": LONG_RAW_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_step": LONG_PATH_STEP,
        "long_path_tables": LONG_PATH_TABLES,
        "long_gapind_report": LONG_GAPIND_REPORT,
        "long_gapind_regime": LONG_GAPIND_REGIME,
        "long_gapind_bridge": LONG_GAPIND_BRIDGE,
        "long_gapind_tables": LONG_GAPIND_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.llnind.manifest@1":
        raise AssertionError("long_llnind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_llnind manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_llnind manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_llnind missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_llnind proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_llnind proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.llnind.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "layers": witness.get("layers"),
            "seams": witness.get("seams"),
            "theorem_bridge": witness.get("theorem_bridge"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_llnind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
