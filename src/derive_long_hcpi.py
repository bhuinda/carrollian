from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_hcpi"
STATUS = "LONG_HCPI_INPUT_GAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcpi.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcpi.py"

LONG_HCINV_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcinv" / "report.json"
LONG_HCFOAM_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "report.json"
)
LONG_HCFOAM_MATRICES = (
    D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "r_foam_matrices.npz"
)
EVIDENCE_ROOT = (
    ROOT / "data" / "evidence" / "talagrand_python_handoff" / "work"
)
INTERTWINE_DIR = EVIDENCE_ROOT / "height_coherent_action_return_intertwining"
INTERTWINE_SPEC = INTERTWINE_DIR / "next_intertwining_verifier_spec.json"
INTERTWINE_TARGET = INTERTWINE_DIR / "height_coherent_action_return_intertwining_target.json"
E33_CERT = (
    EVIDENCE_ROOT
    / "e33_full_corrected_transport"
    / "e33_full_corrected_transport_certificate.json"
)
E33_VECTOR = EVIDENCE_ROOT / "e33_full_corrected_transport" / "e33_vector.npz"
ACTION_RETURN_CERT = (
    EVIDENCE_ROOT
    / "all_residue_height_action_return_reconstruction"
    / "all_residue_height_action_return_certificate.json"
)
CORRECTED_VECTORS = (
    EVIDENCE_ROOT
    / "e33_full_corrected_transport"
    / "all_mask_corrected_transport_vectors_dense.npz"
)
TUBE_SECTION = ROOT / "data" / "tube" / "projection_section.json"

REQ_TEXT_HASH = "4fa680da90704f206b6b9aa287e0b4e1e3e3a28c5e9af3392ce449476b3ca600"
OBS_TEXT_HASH = "57d0d6ba5c29bccafda6960fdd5148fa632c5d9ef31e9f46b23450bb6c3ef242"

REQ_COLUMNS = [
    "requirement_id",
    "requirement_code",
    "required_by_spec_flag",
    "materialized_flag",
    "shape_ok_flag",
    "blocked_flag",
    "source_code",
    "target_rows",
    "target_cols",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
REQ_NAMES = [
    "projection_table_pi_foam33",
    "e33_56_support_vector",
    "foam33_target_basis_order",
    "r_hc_generator_family",
    "r_foam_generator_family",
    "all_residue_scalar_height_table",
    "corrected_transport_vectors",
    "tube_projection_section_wrong_shape",
]
REQ_CODES = {name: index for index, name in enumerate(REQ_NAMES)}
OBS_NAMES = [
    "required_input_count",
    "materialized_required_input_count",
    "blocked_required_input_count",
    "pi_foam33_materialized_flag",
    "r_hc_materialized_flag",
    "r_foam_materialized_flag",
    "e33_support",
    "foam33_dimension",
    "r_foam_generator_count",
    "tube_projection_dimension",
    "tube_pair_basis_total",
    "intertwining_package_matrix_file_count",
    "focused_hcpi_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def has_checks_passed(payload: dict[str, Any]) -> bool:
    if payload.get("all_checks_pass") is True:
        return True
    checks = payload.get("checks")
    return isinstance(checks, dict) and all(value not in (False, None, "") for value in checks.values())


def matching_matrix_files(path: Path) -> list[str]:
    patterns = ("*.npy", "*.npz")
    out: list[str] = []
    for pattern in patterns:
        out.extend(relpath(item) for item in sorted(path.glob(pattern)))
    return out


def build_rows() -> dict[str, Any]:
    hcinv = load_json(LONG_HCINV_REPORT)
    hcfoam = load_json(LONG_HCFOAM_REPORT)
    spec = load_json(INTERTWINE_SPEC)
    target = load_json(INTERTWINE_TARGET)
    e33_cert = load_json(E33_CERT)
    action_return = load_json(ACTION_RETURN_CERT)
    tube = load_json(TUBE_SECTION)
    foam_matrices = np.load(LONG_HCFOAM_MATRICES, allow_pickle=False)
    e33_vector = np.load(E33_VECTOR, allow_pickle=False)["e33"]
    corrected = np.load(CORRECTED_VECTORS, allow_pickle=False)["corrected"]

    required_inputs = spec.get("required_inputs", [])
    if not isinstance(required_inputs, list):
        raise AssertionError("intertwining spec required_inputs is not a list")
    required_text = "\n".join(str(value) for value in required_inputs)
    matrix_files = matching_matrix_files(INTERTWINE_DIR)
    r_foam = np.asarray(foam_matrices["r_foam"])
    e33_support = int(np.count_nonzero(e33_vector))
    tube_projection = tube.get("projection", {})
    if not isinstance(tube_projection, dict):
        raise AssertionError("tube projection payload missing")

    req_specs = [
        (
            "projection_table_pi_foam33",
            int("projection_table for pi_Foam33" in required_inputs),
            0,
            0,
            1,
            0,
            33,
            56,
        ),
        (
            "e33_56_support_vector",
            int("e33 56-support vector" in required_inputs),
            int(e33_support == 56),
            int(e33_vector.shape == (985,) and e33_support == 56),
            0,
            1,
            56,
            1,
        ),
        (
            "foam33_target_basis_order",
            int("Foam33 target basis order" in required_inputs),
            int(r_foam.shape[1:] == (33, 33)),
            int(r_foam.shape[1:] == (33, 33)),
            0,
            2,
            33,
            1,
        ),
        (
            "r_hc_generator_family",
            int("height/action-return operator matrices or deterministic rules" in required_inputs),
            0,
            0,
            1,
            3,
            56,
            56,
        ),
        (
            "r_foam_generator_family",
            int("Foam target action-return operator" in required_inputs),
            int(r_foam.shape == (9, 33, 33)),
            int(r_foam.shape == (9, 33, 33)),
            0,
            4,
            33,
            33,
        ),
        (
            "all_residue_scalar_height_table",
            0,
            int(action_return.get("status") == "ALL_RESIDUE_HEIGHT_ACTION_RETURN_RECONSTRUCTED_PASS"),
            int(action_return.get("residue_class_count") == 2048),
            0,
            5,
            2048,
            1,
        ),
        (
            "corrected_transport_vectors",
            0,
            int(corrected.shape == (2048, 985)),
            int(corrected.shape == (2048, 985)),
            0,
            6,
            2048,
            985,
        ),
        (
            "tube_projection_section_wrong_shape",
            0,
            1,
            int(
                tube_projection.get("closed_loop_quotient_dimension") == 297
                and tube_projection.get("tube_pair_basis_total") == 44521
            ),
            1,
            7,
            int(tube_projection.get("closed_loop_quotient_dimension", 0)),
            int(tube_projection.get("tube_pair_basis_total", 0)),
        ),
    ]
    req_rows = [
        {
            "requirement_id": req_id,
            "requirement_code": REQ_CODES[name],
            "required_by_spec_flag": required,
            "materialized_flag": materialized,
            "shape_ok_flag": shape_ok,
            "blocked_flag": blocked,
            "source_code": source_code,
            "target_rows": rows,
            "target_cols": cols,
        }
        for req_id, (
            name,
            required,
            materialized,
            shape_ok,
            blocked,
            source_code,
            rows,
            cols,
        ) in enumerate(req_specs)
    ]
    required_rows = [row for row in req_rows if row["required_by_spec_flag"] == 1]
    obs = {
        "required_input_count": len(required_rows),
        "materialized_required_input_count": sum(
            row["materialized_flag"] for row in required_rows
        ),
        "blocked_required_input_count": sum(row["blocked_flag"] for row in required_rows),
        "pi_foam33_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "r_foam_materialized_flag": int(r_foam.shape == (9, 33, 33)),
        "e33_support": e33_support,
        "foam33_dimension": int(r_foam.shape[1]),
        "r_foam_generator_count": int(r_foam.shape[0]),
        "tube_projection_dimension": int(
            tube_projection["closed_loop_quotient_dimension"]
        ),
        "tube_pair_basis_total": int(tube_projection["tube_pair_basis_total"]),
        "intertwining_package_matrix_file_count": len(matrix_files),
        "focused_hcpi_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": OBS_CODES[name],
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for name in OBS_NAMES
    ]
    return {
        "hcinv": hcinv,
        "hcfoam": hcfoam,
        "spec": spec,
        "target": target,
        "e33_cert": e33_cert,
        "action_return": action_return,
        "tube": tube,
        "required_text": required_text,
        "matrix_files": matrix_files,
        "r_foam": r_foam,
        "e33_vector": e33_vector,
        "corrected": corrected,
        "req_rows": req_rows,
        "obs_rows": obs_rows,
        "req_table": table_from_rows(REQ_COLUMNS, req_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "obs": obs,
        "req_text_hash": hashlib.sha256(
            digest_text(REQ_COLUMNS, req_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_hcinv_input_passes": rows["hcinv"].get("status") == "LONG_HCINV_CERTIFIED"
        and rows["hcinv"].get("all_checks_pass") is True,
        "long_hcfoam_input_passes": rows["hcfoam"].get("status") == "LONG_HCFOAM_CERTIFIED"
        and rows["hcfoam"].get("all_checks_pass") is True,
        "intertwining_spec_names_required_inputs": (
            "projection_table for pi_Foam33" in rows["spec"].get("required_inputs", [])
            and "height/action-return operator matrices or deterministic rules"
            in rows["spec"].get("required_inputs", [])
            and "Foam target action-return operator" in rows["spec"].get("required_inputs", [])
        ),
        "e33_vector_is_materialized": rows["e33_cert"].get("status")
        == "E33_VECTOR_AND_ALL_CORRECTED_TRANSPORTS_CERTIFIED"
        and rows["e33_vector"].shape == (985,)
        and obs["e33_support"] == 56,
        "scalar_and_corrected_transport_exist": rows["action_return"].get("status")
        == "ALL_RESIDUE_HEIGHT_ACTION_RETURN_RECONSTRUCTED_PASS"
        and rows["corrected"].shape == (2048, 985),
        "r_foam_is_materialized": obs["r_foam_materialized_flag"] == 1
        and obs["r_foam_generator_count"] == 9
        and obs["foam33_dimension"] == 33,
        "pi_and_r_hc_remain_missing": (
            obs["pi_foam33_materialized_flag"],
            obs["r_hc_materialized_flag"],
            obs["blocked_required_input_count"],
        )
        == (0, 0, 2),
        "intertwining_package_has_no_matrix_payloads": obs[
            "intertwining_package_matrix_file_count"
        ]
        == 0,
        "tube_projection_is_not_pi_substitute": (
            obs["tube_projection_dimension"],
            obs["tube_pair_basis_total"],
        )
        == (297, 44521),
        "focused_gap_closed_without_goal_claim": (
            obs["focused_hcpi_closed_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_projection_input_gap",
        "summary": obs,
        "required_inputs": rows["spec"].get("required_inputs", []),
        "intertwining_package_matrix_files": rows["matrix_files"],
        "available_inputs": {
            "e33_vector": relpath(E33_VECTOR),
            "corrected_vectors": relpath(CORRECTED_VECTORS),
            "r_foam_matrices": relpath(LONG_HCFOAM_MATRICES),
        },
        "missing_inputs": [
            "projection_table for pi_Foam33",
            "R_hc generator matrices or deterministic rules on the 56-support",
        ],
    }
    seam_payload = {
        "schema": "long.hcpi.seam@1",
        "status": STATUS,
        "claim": (
            "The current height/action-return intertwining stack has e33, "
            "corrected vectors, Foam33 target basis, and R_Foam materialized, "
            "but the pi_Foam33 projection table and R_hc generator family are "
            "not materialized in the declared target package."
        ),
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcinv": input_entry(
            LONG_HCINV_REPORT,
            {
                "status": rows["hcinv"].get("status"),
                "certificate_sha256": rows["hcinv"].get("certificate_sha256"),
            },
        ),
        "long_hcfoam": input_entry(
            LONG_HCFOAM_REPORT,
            {
                "status": rows["hcfoam"].get("status"),
                "certificate_sha256": rows["hcfoam"].get("certificate_sha256"),
            },
        ),
        "r_foam_matrices": input_entry(LONG_HCFOAM_MATRICES),
        "intertwining_spec": input_entry(INTERTWINE_SPEC),
        "intertwining_target": input_entry(INTERTWINE_TARGET),
        "e33_certificate": input_entry(
            E33_CERT,
            {
                "status": rows["e33_cert"].get("status"),
                "certificate_sha256": rows["e33_cert"].get("certificate_sha256"),
            },
        ),
        "e33_vector": input_entry(E33_VECTOR),
        "action_return_certificate": input_entry(
            ACTION_RETURN_CERT,
            {
                "status": rows["action_return"].get("status"),
                "certificate_sha256": rows["action_return"].get("certificate_sha256"),
            },
        ),
        "corrected_vectors": input_entry(CORRECTED_VECTORS),
        "tube_projection_section": input_entry(TUBE_SECTION),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT)
        if VALIDATOR_SCRIPT.exists()
        else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcpi.report@1",
        "status": seam_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_hcpi certifies the remaining input gap for the full "
            "height/action-return intertwiner: R_Foam is now materialized, "
            "while pi_Foam33 and R_hc remain absent from the declared matrix "
            "input surface."
        ),
        "stage_protocol": {
            "draft": "read long_hcinv, long_hcfoam, e33/vector evidence, target spec, and tube projection section",
            "witness": "emit required-input rows and observable counts for materialized versus blocked inputs",
            "coherence": "check e33 support, corrected vectors, R_Foam matrices, target spec requirements, and tube-section shape mismatch",
            "closure": "certify the input gap without claiming the full intertwiner",
            "emit": "write long_hcpi artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "required_inputs_csv": relpath(OUT_DIR / "required_inputs.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "e33 is materialized as a 985-coordinate vector with 56 nonzero support entries",
                "all 2048 corrected transport vectors are present",
                "R_Foam is materialized by long_hcfoam as nine 33x33 matrices",
                "the declared intertwining package has no .npy or .npz matrix payload for pi_Foam33 or R_hc",
                "the existing tube projection section has 297-dimensional quotient shape and is not the required 33x56 pi_Foam33 matrix",
            ],
            "does_not_certify": [
                "a materialized pi_Foam33 projection table",
                "a materialized R_hc generator family",
                "the full pi_Foam33 R_hc equals R_Foam pi_Foam33 identity",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": (
            "Construct the actual 33x56 pi_Foam33 table from the e33 56-support "
            "basis into the checked Foam33 basis, then bind R_hc generators and "
            "run the matrix intertwining verifier."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert_payload = {
        "schema": "long.hcpi.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.hcpi.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "req_csv": csv_text(REQ_COLUMNS, rows["req_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "req_table": rows["req_table"],
        "observable_table": rows["observable_table"],
        "cert": cert_payload,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "req_text_sha256": rows["req_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "required_inputs.csv").write_text(payloads["req_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        required_input_table=payloads["req_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
