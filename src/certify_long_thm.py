from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_thm import (
        BOUNDARY_COLUMNS,
        BOUNDARY_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LLNIND_BRIDGE,
        LONG_LLNIND_LAYER,
        LONG_LLNIND_REPORT,
        LONG_LLNIND_SEAM,
        LONG_LLNIND_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PROOF_COLUMNS,
        PROOF_TEXT_HASH,
        STATUS,
        THEOREM_COLUMNS,
        THEOREM_ID,
        THEOREM_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_thm import (
        BOUNDARY_COLUMNS,
        BOUNDARY_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LLNIND_BRIDGE,
        LONG_LLNIND_LAYER,
        LONG_LLNIND_REPORT,
        LONG_LLNIND_SEAM,
        LONG_LLNIND_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PROOF_COLUMNS,
        PROOF_TEXT_HASH,
        STATUS,
        THEOREM_COLUMNS,
        THEOREM_ID,
        THEOREM_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_thm() -> dict[str, Any]:
    expected = build_payloads()
    thm_payload = load_json(OUT_DIR / "thm.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if thm_payload != expected["thm"]:
        raise AssertionError("long_thm thm JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_thm cert mismatch")
    for filename, key in {
        "theorem.csv": "theorem_csv",
        "proof.csv": "proof_csv",
        "boundary.csv": "boundary_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_thm {filename} mismatch")

    for key, expected_array in {
        "theorem_table": expected["theorem_table"],
        "proof_table": expected["proof_table"],
        "boundary_table": expected["boundary_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_thm table mismatch: {key}")

    if report.get("schema") != "long.thm.report@1":
        raise AssertionError("long_thm report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_thm report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_thm all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_thm checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_thm report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_thm report hash mismatch")

    csv_shapes = [
        ("theorem.csv", THEOREM_COLUMNS, 1),
        ("proof.csv", PROOF_COLUMNS, 6),
        ("boundary.csv", BOUNDARY_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_thm {filename} shape mismatch")

    table_shapes = {
        "theorem_table": (1, len(THEOREM_COLUMNS)),
        "proof_table": (6, len(PROOF_COLUMNS)),
        "boundary_table": (5, len(BOUNDARY_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_thm {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "tensor_support_count": 1_414_965,
        "tensor_coeff_sum": 2_537_360,
        "universal_law_count": 306,
        "probability_path_count": 288,
        "finite_gap_check_count": 131_586,
        "finite_gap_nonnegative_count": 131_586,
        "tail_formula_nonnegative_count": 26,
        "certified_layer_count": 8,
        "seam_match_count": 8,
        "proof_item_count": 6,
        "boundary_item_count": 5,
        "resolved_boundary_count": 0,
        "finite_theorem_required_boundary_count": 0,
        "future_work_boundary_count": 5,
        "long_llnind_certified_flag": 1,
        "finite_tensor_lookup_theorem_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_thm observable {key} mismatch")

    if hashlib.sha256(
        digest_text(THEOREM_COLUMNS, csv_rows["theorem.csv"]).encode("ascii")
    ).hexdigest() != THEOREM_TEXT_HASH:
        raise AssertionError("long_thm theorem hash mismatch")
    if hashlib.sha256(
        digest_text(PROOF_COLUMNS, csv_rows["proof.csv"]).encode("ascii")
    ).hexdigest() != PROOF_TEXT_HASH:
        raise AssertionError("long_thm proof hash mismatch")
    if hashlib.sha256(
        digest_text(BOUNDARY_COLUMNS, csv_rows["boundary.csv"]).encode("ascii")
    ).hexdigest() != BOUNDARY_TEXT_HASH:
        raise AssertionError("long_thm boundary hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_llnind_report": LONG_LLNIND_REPORT,
        "long_llnind_layer": LONG_LLNIND_LAYER,
        "long_llnind_seam": LONG_LLNIND_SEAM,
        "long_llnind_bridge": LONG_LLNIND_BRIDGE,
        "long_llnind_tables": LONG_LLNIND_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.thm.manifest@1":
        raise AssertionError("long_thm manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_thm manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_thm manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_thm missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_thm proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_thm proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.thm.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "finite_theorem": witness.get("finite_theorem"),
            "proof_inventory": witness.get("proof_inventory"),
            "remaining_boundaries": witness.get("remaining_boundaries"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_thm(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
