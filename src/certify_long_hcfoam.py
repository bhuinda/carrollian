from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcfoam import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        FOAM16_DIM,
        FOAM33_DIM,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
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
    from derive_long_hcfoam import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        FOAM16_DIM,
        FOAM33_DIM,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
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


def signed_monomial(matrix: np.ndarray) -> bool:
    return (
        set(np.unique(matrix)).issubset({-1, 0, 1})
        and bool(np.all(np.count_nonzero(matrix, axis=0) == 1))
        and bool(np.all(np.count_nonzero(matrix, axis=1) == 1))
    )


def validate_long_hcfoam() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "r_foam_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcfoam seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcfoam cert mismatch")
    for filename, key in {
        "foam33_basis.csv": "basis_csv",
        "r_foam_generators.csv": "generator_csv",
        "r_foam_edges.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcfoam {filename} mismatch")
    for key, expected_array in {
        "basis_table": expected["basis_table"],
        "generator_table": expected["generator_table"],
        "edge_table": expected["edge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcfoam table mismatch: {key}")
    for key, expected_array in {
        "foam16": expected["foam16"],
        "r_foam": expected["r_foam"],
    }.items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_hcfoam matrix mismatch: {key}")

    if report.get("schema") != "long.hcfoam.report@1":
        raise AssertionError("long_hcfoam report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcfoam report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcfoam all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcfoam checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcfoam report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcfoam report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("foam33_basis.csv", BASIS_COLUMNS, FOAM33_DIM),
        ("r_foam_generators.csv", GENERATOR_COLUMNS, 9),
        ("r_foam_edges.csv", EDGE_COLUMNS, 9 * FOAM33_DIM),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcfoam {filename} shape mismatch")

    assert_locked_hash(
        "basis",
        hashlib.sha256(
            digest_text(BASIS_COLUMNS, csv_rows["foam33_basis.csv"]).encode("ascii")
        ).hexdigest(),
        BASIS_TEXT_HASH,
    )
    assert_locked_hash(
        "generator",
        hashlib.sha256(
            digest_text(GENERATOR_COLUMNS, csv_rows["r_foam_generators.csv"]).encode(
                "ascii"
            )
        ).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "edge",
        hashlib.sha256(
            digest_text(EDGE_COLUMNS, csv_rows["r_foam_edges.csv"]).encode("ascii")
        ).hexdigest(),
        EDGE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable",
        hashlib.sha256(
            digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
        ).hexdigest(),
        OBS_TEXT_HASH,
    )

    foam16 = np.asarray(matrices["foam16"])
    r_foam = np.asarray(matrices["r_foam"])
    if foam16.shape != (9, FOAM16_DIM, FOAM16_DIM):
        raise AssertionError("Foam16 matrix shape mismatch")
    if r_foam.shape != (9, FOAM33_DIM, FOAM33_DIM):
        raise AssertionError("R_Foam matrix shape mismatch")
    for generator_index in range(9):
        if not signed_monomial(foam16[generator_index]):
            raise AssertionError(
                f"Foam16 generator {generator_index} is not signed monomial"
            )
        if not signed_monomial(r_foam[generator_index]):
            raise AssertionError(
                f"R_Foam generator {generator_index} is not signed monomial"
            )
        if int(r_foam[generator_index, 0, 0]) != 1:
            raise AssertionError(
                f"R_Foam generator {generator_index} does not fix global row"
            )
        if not np.array_equal(
            r_foam[generator_index, 1 : 1 + FOAM16_DIM, 1 : 1 + FOAM16_DIM],
            foam16[generator_index],
        ):
            raise AssertionError(
                f"R_Foam generator {generator_index} first copy mismatch"
            )
        if not np.array_equal(
            r_foam[generator_index, 1 + FOAM16_DIM :, 1 + FOAM16_DIM :],
            foam16[generator_index],
        ):
            raise AssertionError(
                f"R_Foam generator {generator_index} second copy mismatch"
            )

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "field_prime": 1_000_003,
        "foam16_dimension": 16,
        "foam33_dimension": 33,
        "foam16_copy_count": 2,
        "generator_count": 9,
        "foam16_edge_count": 144,
        "foam33_edge_count": 297,
        "foam16_nonzero_count": 144,
        "foam33_nonzero_count": 297,
        "all_foam16_signed_monomial_flag": 1,
        "all_foam16_orthogonal_flag": 1,
        "all_foam33_signed_monomial_flag": 1,
        "all_foam33_orthogonal_flag": 1,
        "all_global_fixed_flag": 1,
        "all_copy_actions_identical_flag": 1,
        "module_basis_rank": 16,
        "projective_action_count": 384,
        "generator_closure_count": 384,
        "r_foam_materialized_flag": 1,
        "pi_foam33_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "focused_hcfoam_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcfoam observable {name} mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_hcinv": expected["report"]["inputs"]["long_hcinv"]["path"],
        "all_four_lifts_report": expected["report"]["inputs"]["all_four_lifts_report"][
            "path"
        ],
        "foam16_basis": expected["report"]["inputs"]["foam16_basis"]["path"],
        "foam16_generator_edges": expected["report"]["inputs"][
            "foam16_generator_edges"
        ]["path"],
        "foam16_module_certification": expected["report"]["inputs"][
            "foam16_module_certification"
        ]["path"],
        "intertwining_target": expected["report"]["inputs"]["intertwining_target"][
            "path"
        ],
        "intertwining_spec": expected["report"]["inputs"]["intertwining_spec"][
            "path"
        ],
    }.items():
        assert_file_hash(inputs.get(label, {}), ROOT / path, label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcfoam.manifest@1":
        raise AssertionError("long_hcfoam manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcfoam manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcfoam manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_hcfoam missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcfoam proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcfoam proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcfoam.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "matrix_hashes": witness.get("matrix_hashes"),
            "operator_boundary": witness.get("operator_boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcfoam(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
