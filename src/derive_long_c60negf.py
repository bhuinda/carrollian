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
        sha_array,
        write_json,
    )
    from .derive_long_c60op import (
        OUT_DIR as LONG_C60OP_DIR,
        RESULT_STATUS as C60OP_RESULT_STATUS,
    )
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_c60op import (
        OUT_DIR as LONG_C60OP_DIR,
        RESULT_STATUS as C60OP_RESULT_STATUS,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c60negf"
STATUS = "LONG_C60NEGF_STAGE6_DFT_NEGF_PROTOCOL_CERTIFIED"
RESULT_STATUS = "C60_D20_STAGE6_DFT_NEGF_VALIDATION_PROTOCOL_CONSTRUCTED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_C60OP = LONG_C60OP_DIR / "report.json"
LONG_C60OP_OPCODE = LONG_C60OP_DIR / "opcode.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c60negf.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c60negf.py"

CASE_COLUMNS = [
    "validation_case_id",
    "case_code",
    "opcode_family_code",
    "representative_opcode_id",
    "required_dft_flag",
    "required_negf_flag",
    "control_count",
    "observable_count",
    "physical_result_present_flag",
]
CONTROL_COLUMNS = [
    "control_id",
    "control_code",
    "required_flag",
    "physical_result_present_flag",
]
OBSERVABLE_CLASS_COLUMNS = [
    "observable_class_id",
    "observable_class_code",
    "required_flag",
    "quantitative_result_present_flag",
]
JOB_CARD_COLUMNS = [
    "job_id",
    "validation_case_id",
    "control_code",
    "opcode_family_code",
    "dft_job_flag",
    "negf_job_flag",
    "observable_class_count",
    "protocol_only_flag",
    "physical_result_present_flag",
]
SUCCESS_COLUMNS = [
    "criterion_id",
    "observable_class_code",
    "differential_signature_required_flag",
    "control_separation_required_flag",
    "quantitative_result_present_flag",
]
CLAIM_COLUMNS = [
    "claim_update_id",
    "claim_area_code",
    "formal_dependency_flag",
    "requires_physical_validation_flag",
    "claim_ready_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

FAMILY_NAMES = [
    "SEM_SELECTOR_FLUX_TRANSFER",
    "SEM_ALPHA_FLUX_BALANCE",
    "SEM_STATIC_SELECTOR_ANCHOR",
]
FAMILY_CODES = {name: index for index, name in enumerate(FAMILY_NAMES)}

CASE_NAMES = [
    "static_anchor_symmetry_break",
    "static_anchor_charge_baseline",
    "alpha_flux_pair_partition",
    "alpha_flux_transport_window",
    "alpha_flux_endpoint_reversal",
    "alpha_flux_vibronic_sensitivity",
    "selector_transfer_local_coupling",
    "selector_transfer_charge_gate",
    "selector_transfer_current_gate",
    "selector_transfer_scrambled_alpha",
    "selector_transfer_isomer_mix",
    "mixed_family_discriminant",
    "minimal_protocol_replay",
]
CASE_CODES = {name: index for index, name in enumerate(CASE_NAMES)}

CONTROL_NAMES = [
    "bare_c60",
    "selector_only",
    "alpha_only",
    "endpoint_reversal",
    "scrambled_alpha",
    "nearby_isomer_mix",
]
CONTROL_CODES = {name: index for index, name in enumerate(CONTROL_NAMES)}

OBSERVABLE_CLASS_NAMES = [
    "relaxed_geometry",
    "charge_partition",
    "frontier_orbital_shift",
    "transmission_spectrum",
    "iv_curve",
    "local_current_density",
    "vibronic_sensitivity",
    "functionalization_energy",
]
OBSERVABLE_CLASS_CODES = {
    name: index for index, name in enumerate(OBSERVABLE_CLASS_NAMES)
}

CLAIM_AREA_NAMES = [
    "formal_opcode_assignment",
    "molecular_signature_test",
    "control_discrimination",
    "transport_observable",
    "manufacturability_boundary",
    "device_claim_boundary",
]
CLAIM_AREA_CODES = {name: index for index, name in enumerate(CLAIM_AREA_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "stage5_result_present_flag",
    "semantic_opcode_rows_carried_forward",
    "golden_ticks_carried_forward",
    "c60_transition_edges_carried_forward",
    "stage5_adjacent_composition_failures",
    "minimal_validation_case_count",
    "dft_negf_job_card_count",
    "control_experiment_count",
    "observable_class_count",
    "success_criterion_count",
    "claim_update_count",
    "dft_result_row_count",
    "negf_result_row_count",
    "protocol_only_flag",
    "physical_signature_validated_flag",
    "conductance_validated_flag",
    "manufacturability_validation_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def build_rows() -> dict[str, Any]:
    c60op = load_json(LONG_C60OP)
    c60op_s = summary(c60op)
    case_plan = [
        ("static_anchor_symmetry_break", "SEM_STATIC_SELECTOR_ANCHOR", 57),
        ("static_anchor_charge_baseline", "SEM_STATIC_SELECTOR_ANCHOR", 58),
        ("alpha_flux_pair_partition", "SEM_ALPHA_FLUX_BALANCE", 36),
        ("alpha_flux_transport_window", "SEM_ALPHA_FLUX_BALANCE", 37),
        ("alpha_flux_endpoint_reversal", "SEM_ALPHA_FLUX_BALANCE", 38),
        ("alpha_flux_vibronic_sensitivity", "SEM_ALPHA_FLUX_BALANCE", 39),
        ("selector_transfer_local_coupling", "SEM_SELECTOR_FLUX_TRANSFER", 0),
        ("selector_transfer_charge_gate", "SEM_SELECTOR_FLUX_TRANSFER", 1),
        ("selector_transfer_current_gate", "SEM_SELECTOR_FLUX_TRANSFER", 2),
        ("selector_transfer_scrambled_alpha", "SEM_SELECTOR_FLUX_TRANSFER", 3),
        ("selector_transfer_isomer_mix", "SEM_SELECTOR_FLUX_TRANSFER", 4),
        ("mixed_family_discriminant", "SEM_SELECTOR_FLUX_TRANSFER", 5),
        ("minimal_protocol_replay", "SEM_ALPHA_FLUX_BALANCE", 40),
    ]
    case_rows = [
        {
            "validation_case_id": index,
            "case_code": CASE_CODES[name],
            "opcode_family_code": FAMILY_CODES[family],
            "representative_opcode_id": opcode_id,
            "required_dft_flag": 1,
            "required_negf_flag": 1,
            "control_count": len(CONTROL_CODES),
            "observable_count": len(OBSERVABLE_CLASS_CODES),
            "physical_result_present_flag": 0,
        }
        for index, (name, family, opcode_id) in enumerate(case_plan)
    ]
    control_rows = [
        {
            "control_id": code,
            "control_code": code,
            "required_flag": 1,
            "physical_result_present_flag": 0,
        }
        for _, code in CONTROL_CODES.items()
    ]
    observable_class_rows = [
        {
            "observable_class_id": code,
            "observable_class_code": code,
            "required_flag": 1,
            "quantitative_result_present_flag": 0,
        }
        for _, code in OBSERVABLE_CLASS_CODES.items()
    ]
    job_rows = []
    job_id = 0
    for case in case_rows:
        for control_code in range(len(CONTROL_CODES)):
            job_rows.append(
                {
                    "job_id": job_id,
                    "validation_case_id": case["validation_case_id"],
                    "control_code": control_code,
                    "opcode_family_code": case["opcode_family_code"],
                    "dft_job_flag": 1,
                    "negf_job_flag": 1,
                    "observable_class_count": len(OBSERVABLE_CLASS_CODES),
                    "protocol_only_flag": 1,
                    "physical_result_present_flag": 0,
                }
            )
            job_id += 1
    success_rows = [
        {
            "criterion_id": code,
            "observable_class_code": code,
            "differential_signature_required_flag": 1,
            "control_separation_required_flag": 1,
            "quantitative_result_present_flag": 0,
        }
        for code in range(len(OBSERVABLE_CLASS_CODES))
    ]
    claim_rows = []
    for name, code in CLAIM_AREA_CODES.items():
        physical_required = int(name != "formal_opcode_assignment")
        claim_rows.append(
            {
                "claim_update_id": code,
                "claim_area_code": code,
                "formal_dependency_flag": 1,
                "requires_physical_validation_flag": physical_required,
                "claim_ready_flag": int(physical_required == 0),
            }
        )
    obs = {
        "input_report_count": 1,
        "input_certified_count": int(c60op.get("all_checks_pass") is True),
        "stage5_result_present_flag": int(
            c60op.get("result_status") == C60OP_RESULT_STATUS
        ),
        "semantic_opcode_rows_carried_forward": int(
            c60op_s["semantic_opcode_rows_assigned"]
        ),
        "golden_ticks_carried_forward": int(c60op_s["golden_ticks_covered"]),
        "c60_transition_edges_carried_forward": int(
            c60op_s["c60_transition_edges_used"]
        ),
        "stage5_adjacent_composition_failures": int(
            c60op_s["adjacent_composition_failures"]
        ),
        "minimal_validation_case_count": len(case_rows),
        "dft_negf_job_card_count": len(job_rows),
        "control_experiment_count": len(control_rows),
        "observable_class_count": len(observable_class_rows),
        "success_criterion_count": len(success_rows),
        "claim_update_count": len(claim_rows),
        "dft_result_row_count": 0,
        "negf_result_row_count": 0,
        "protocol_only_flag": 1,
        "physical_signature_validated_flag": 0,
        "conductance_validated_flag": 0,
        "manufacturability_validation_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c60op": c60op,
        "case_rows": case_rows,
        "control_rows": control_rows,
        "observable_class_rows": observable_class_rows,
        "job_rows": job_rows,
        "success_rows": success_rows,
        "claim_rows": claim_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    case_table = table_from_rows(CASE_COLUMNS, rows["case_rows"])
    control_table = table_from_rows(CONTROL_COLUMNS, rows["control_rows"])
    observable_class_table = table_from_rows(
        OBSERVABLE_CLASS_COLUMNS, rows["observable_class_rows"]
    )
    job_card_table = table_from_rows(JOB_CARD_COLUMNS, rows["job_rows"])
    success_table = table_from_rows(SUCCESS_COLUMNS, rows["success_rows"])
    claim_table = table_from_rows(CLAIM_COLUMNS, rows["claim_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "stage5_opcode_certificate_present": obs["input_report_count"]
        == obs["input_certified_count"]
        and obs["stage5_result_present_flag"] == 1,
        "stage5_counts_carried_forward": obs[
            "semantic_opcode_rows_carried_forward"
        ]
        == 59
        and obs["golden_ticks_carried_forward"] == 20
        and obs["c60_transition_edges_carried_forward"] == 30
        and obs["stage5_adjacent_composition_failures"] == 0,
        "validation_matrix_shape_matches": obs["minimal_validation_case_count"]
        == 13
        and obs["dft_negf_job_card_count"] == 78
        and obs["control_experiment_count"] == 6
        and obs["observable_class_count"] == 8
        and obs["success_criterion_count"] == 8,
        "claim_update_matrix_shape_matches": obs[
            "claim_update_count"
        ]
        == 6,
        "all_job_cards_require_dft_and_negf": all(
            row["dft_job_flag"] == 1 and row["negf_job_flag"] == 1
            for row in rows["job_rows"]
        ),
        "protocol_only_boundary_preserved": obs["protocol_only_flag"] == 1
        and obs["dft_result_row_count"] == 0
        and obs["negf_result_row_count"] == 0
        and obs["physical_signature_validated_flag"] == 0
        and obs["conductance_validated_flag"] == 0
        and obs["manufacturability_validation_flag"] == 0,
        "table_shapes_match": case_table.shape == (13, len(CASE_COLUMNS))
        and control_table.shape == (6, len(CONTROL_COLUMNS))
        and observable_class_table.shape
        == (8, len(OBSERVABLE_CLASS_COLUMNS))
        and job_card_table.shape == (78, len(JOB_CARD_COLUMNS))
        and success_table.shape == (8, len(SUCCESS_COLUMNS))
        and claim_table.shape == (6, len(CLAIM_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c60_d20_dft_negf_validation_protocol",
        "result_status": RESULT_STATUS,
        "summary": {
            "semantic_opcode_rows_carried_forward": obs[
                "semantic_opcode_rows_carried_forward"
            ],
            "golden_ticks_carried_forward": obs["golden_ticks_carried_forward"],
            "c60_transition_edges_carried_forward": obs[
                "c60_transition_edges_carried_forward"
            ],
            "stage5_adjacent_composition_failures": obs[
                "stage5_adjacent_composition_failures"
            ],
            "minimal_validation_cases": obs["minimal_validation_case_count"],
            "dft_negf_job_cards": obs["dft_negf_job_card_count"],
            "control_experiments": obs["control_experiment_count"],
            "observable_classes": obs["observable_class_count"],
            "claim_update_count": obs["claim_update_count"],
            "dft_result_row_count": obs["dft_result_row_count"],
            "negf_result_row_count": obs["negf_result_row_count"],
            "physical_signature_validated_flag": obs[
                "physical_signature_validated_flag"
            ],
        },
        "family_code_map": {str(value): key for key, value in FAMILY_CODES.items()},
        "case_code_map": {str(value): key for key, value in CASE_CODES.items()},
        "control_code_map": {
            str(value): key for key, value in CONTROL_CODES.items()
        },
        "observable_class_code_map": {
            str(value): key for key, value in OBSERVABLE_CLASS_CODES.items()
        },
        "claim_area_code_map": {
            str(value): key for key, value in CLAIM_AREA_CODES.items()
        },
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "case_table_sha256": sha_array(case_table),
        "case_text_sha256": sha_text(csv_text(CASE_COLUMNS, rows["case_rows"])),
        "control_table_sha256": sha_array(control_table),
        "observable_class_table_sha256": sha_array(observable_class_table),
        "job_card_table_sha256": sha_array(job_card_table),
        "success_table_sha256": sha_array(success_table),
        "claim_table_sha256": sha_array(claim_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c60negf = {
        "schema": "long.c60negf@1",
        "object": "c60_d20_dft_negf_validation_protocol",
        "status": STATUS if all(checks.values()) else "LONG_C60NEGF_PROVISIONAL",
        "result_status": RESULT_STATUS,
        "witness": witness,
    }
    report = {
        "schema": "long.c60negf.report@1",
        "status": c60negf["status"],
        "result_status": RESULT_STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c60negf converts the Stage 5 formal C60/d20 semantic opcode "
            "assignment into a DFT/NEGF validation protocol. It carries forward "
            "59 opcode rows, 20 golden ticks, 30 C60 transition edges, and zero "
            "Stage 5 composition failures, then emits 13 validation cases, 78 "
            "job cards, 6 controls, 8 observable classes, and success criteria. "
            "It contains no physical simulation result rows."
        ),
        "stage_protocol": {
            "draft": "read long_c60op C60 opcode-assignment certificate",
            "witness": "emit validation cases, controls, observable classes, job cards, success criteria, and observables",
            "coherence": "check carried Stage 5 counts, 13x6 job matrix, 8 observable classes, and zero physical-result rows",
            "closure": "certify the Stage 6 DFT/NEGF validation protocol as a protocol only",
            "emit": "write long_c60negf artifacts and verifier hook",
        },
        "inputs": {
            "long_c60op": input_entry(
                LONG_C60OP,
                {
                    "status": rows["c60op"].get("status"),
                    "certificate_sha256": rows["c60op"].get(
                        "certificate_sha256"
                    ),
                    "result_status": rows["c60op"].get("result_status"),
                },
            ),
            "long_c60op_opcode": input_entry(LONG_C60OP_OPCODE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c60negf": relpath(OUT_DIR / "c60negf.json"),
            "case_csv": relpath(OUT_DIR / "case.csv"),
            "control_csv": relpath(OUT_DIR / "control.csv"),
            "observable_class_csv": relpath(OUT_DIR / "observable_class.csv"),
            "job_card_csv": relpath(OUT_DIR / "job_card.csv"),
            "success_csv": relpath(OUT_DIR / "success.csv"),
            "claim_csv": relpath(OUT_DIR / "claim.csv"),
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
                "the Stage 6 validation protocol carries forward 59 Stage 5 C60 opcode rows",
                "the protocol contains 13 validation cases and 78 DFT/NEGF job cards",
                "the protocol includes 6 controls and 8 observable classes",
                "the protocol includes a 6-row claim update matrix",
                "all job cards require both DFT and NEGF evaluation",
                "zero DFT result rows and zero NEGF result rows are present in this certificate",
            ],
            "does_not_certify_because_out_of_scope": [
                "physical conductance signatures",
                "switching speed, decoherence, thermal stability, or manufacturability",
                "DFT convergence or NEGF transmission values",
                "experimental synthesis feasibility",
                "a physical selector axiom",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Run or import signed DFT/NEGF result tables for the 78 protocol job "
            "cards, then certify whether the three opcode families produce "
            "separable molecular signatures against the six controls."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c60negf.cert@1",
        "status": report["status"],
        "result_status": RESULT_STATUS,
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c60negf.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "result_status": RESULT_STATUS,
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c60negf": c60negf,
        "case_csv": csv_text(CASE_COLUMNS, rows["case_rows"]),
        "control_csv": csv_text(CONTROL_COLUMNS, rows["control_rows"]),
        "observable_class_csv": csv_text(
            OBSERVABLE_CLASS_COLUMNS, rows["observable_class_rows"]
        ),
        "job_card_csv": csv_text(JOB_CARD_COLUMNS, rows["job_rows"]),
        "success_csv": csv_text(SUCCESS_COLUMNS, rows["success_rows"]),
        "claim_csv": csv_text(CLAIM_COLUMNS, rows["claim_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "case_table": case_table,
        "control_table": control_table,
        "observable_class_table": observable_class_table,
        "job_card_table": job_card_table,
        "success_table": success_table,
        "claim_table": claim_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "c60negf.json", payloads["c60negf"])
    (OUT_DIR / "case.csv").write_text(payloads["case_csv"], encoding="utf-8")
    (OUT_DIR / "control.csv").write_text(
        payloads["control_csv"], encoding="utf-8"
    )
    (OUT_DIR / "observable_class.csv").write_text(
        payloads["observable_class_csv"], encoding="utf-8"
    )
    (OUT_DIR / "job_card.csv").write_text(
        payloads["job_card_csv"], encoding="utf-8"
    )
    (OUT_DIR / "success.csv").write_text(
        payloads["success_csv"], encoding="utf-8"
    )
    (OUT_DIR / "claim.csv").write_text(payloads["claim_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        case_table=payloads["case_table"],
        control_table=payloads["control_table"],
        observable_class_table=payloads["observable_class_table"],
        job_card_table=payloads["job_card_table"],
        success_table=payloads["success_table"],
        claim_table=payloads["claim_table"],
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
                "result_status": report["result_status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
