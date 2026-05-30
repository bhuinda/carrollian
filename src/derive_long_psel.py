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
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_psel"
STATUS = "LONG_PSEL_CONTRACT_FIRST_FAILURE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_SEL = PROOF_ROOT / "long_sel" / "report.json"
LONG_RIM = PROOF_ROOT / "long_rim" / "report.json"
LONG_RIM_SELECT = PROOF_ROOT / "long_rim_select" / "report.json"
LONG_BINC = PROOF_ROOT / "long_binc" / "report.json"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_DIM4_GATE = PROOF_ROOT / "long_dim4_gate" / "report.json"
LONG_PAX = PROOF_ROOT / "long_pax" / "report.json"
LONG_OPROM = PROOF_ROOT / "long_oprom" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_psel.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_psel.py"

CONTRACT_COLUMNS = [
    "clause_id",
    "clause_code",
    "source_code",
    "required_flag",
    "observed_value",
    "pass_flag",
    "first_failure_flag",
    "downstream_blocked_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

CLAUSE_NAMES = [
    "atom_boundary_domain_present",
    "rim_phase_domain_present",
    "golden_phase_candidate_present",
    "formal_selector_inventory_present",
    "physical_selector_axiom_present",
    "raw_packet_bridge_present",
    "semantic_transition_operation_present",
    "stress_transition_coupling_key_present",
    "dim4_subboundary_selected",
    "gr_source_selector_ready",
]
CLAUSE_CODES = {name: index for index, name in enumerate(CLAUSE_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "contract_clause_count",
    "contract_pass_count",
    "contract_fail_count",
    "first_failure_clause_code",
    "downstream_blocked_clause_count",
    "atom_count",
    "complement_pair_count",
    "rim_phase_count",
    "golden_class_count",
    "golden_unoriented_rim_count",
    "formal_c2_selector_count",
    "physical_selector_axiom_flag",
    "physical_selector_candidate_count",
    "raw_compatible_packet_pair_count",
    "missing_restriction_bridge_count",
    "semantic_transition_operation_flag",
    "stress_transition_shared_key_count",
    "dim4_reduction_certified_flag",
    "certified_dim4_candidate_count",
    "gr_source_selector_ready_flag",
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
    sel = load_json(LONG_SEL)
    rim = load_json(LONG_RIM)
    rim_select = load_json(LONG_RIM_SELECT)
    binc = load_json(LONG_BINC)
    transition = load_json(LONG_TRANSITION_SEM)
    dim4 = load_json(LONG_DIM4_GATE)
    pax = load_json(LONG_PAX)
    oprom = load_json(LONG_OPROM)

    sel_s = summary(sel)
    rim_s = summary(rim)
    rim_select_s = summary(rim_select)
    binc_s = summary(binc)
    transition_s = summary(transition)
    dim4_s = summary(dim4)
    pax_s = summary(pax)
    oprom_s = summary(oprom)

    physical_selector_axiom = int(pax_s["physical_selector_axiom_flag"])
    physical_selector_candidates = int(pax_s["candidate_count"])
    raw_packet_bridge = int(binc_s["raw_compatible_pair_count"])
    semantic_operation = int(oprom_s["operation_promotion_flag"])
    stress_transition_key = int(rim_select_s["stress_transition_shared_key_count"])
    dim4_flag = int(dim4_s["dim4_reduction_certified_flag"])
    gr_ready = int(
        physical_selector_axiom == 1
        and raw_packet_bridge > 0
        and semantic_operation == 1
        and stress_transition_key > 0
        and dim4_flag == 1
    )

    contract_seed = [
        ("atom_boundary_domain_present", 0, 1, int(rim_s["atom_count"] == 20)),
        (
            "rim_phase_domain_present",
            1,
            1,
            int(rim_select_s["rim_phase_count"] == 63),
        ),
        (
            "golden_phase_candidate_present",
            1,
            1,
            int(
                rim_s["golden_defect_class_count"] == 1
                and rim_select_s["golden_unoriented_rims"] == 144
            ),
        ),
        (
            "formal_selector_inventory_present",
            2,
            1,
            int(sel_s["formal_c2_selector_count"] == 8),
        ),
        (
            "physical_selector_axiom_present",
            2,
            1,
            int(physical_selector_axiom == 1 and physical_selector_candidates > 0),
        ),
        (
            "raw_packet_bridge_present",
            3,
            1,
            int(raw_packet_bridge > 0 and int(binc_s["missing_restriction_bridge_count"]) == 0),
        ),
        (
            "semantic_transition_operation_present",
            4,
            1,
            int(semantic_operation == 1),
        ),
        (
            "stress_transition_coupling_key_present",
            1,
            1,
            int(stress_transition_key > 0),
        ),
        ("dim4_subboundary_selected", 5, 1, int(dim4_flag == 1)),
        ("gr_source_selector_ready", 6, 1, gr_ready),
    ]
    first_failure_index = next(
        index for index, (_, _, _, passed) in enumerate(contract_seed) if passed == 0
    )
    contract_rows = []
    for index, (name, source_code, required, passed) in enumerate(contract_seed):
        if name == "physical_selector_axiom_present":
            observed = physical_selector_axiom
        elif name == "raw_packet_bridge_present":
            observed = raw_packet_bridge
        elif name == "semantic_transition_operation_present":
            observed = semantic_operation
        elif name == "stress_transition_coupling_key_present":
            observed = stress_transition_key
        elif name == "dim4_subboundary_selected":
            observed = dim4_flag
        elif name == "gr_source_selector_ready":
            observed = gr_ready
        elif name == "atom_boundary_domain_present":
            observed = int(rim_s["atom_count"])
        elif name == "rim_phase_domain_present":
            observed = int(rim_select_s["rim_phase_count"])
        elif name == "golden_phase_candidate_present":
            observed = int(rim_select_s["golden_unoriented_rims"])
        else:
            observed = int(sel_s["formal_c2_selector_count"])
        contract_rows.append(
            {
                "clause_id": index,
                "clause_code": CLAUSE_CODES[name],
                "source_code": source_code,
                "required_flag": required,
                "observed_value": observed,
                "pass_flag": passed,
                "first_failure_flag": int(index == first_failure_index),
                "downstream_blocked_flag": int(index > first_failure_index),
            }
        )

    obs = {
        "input_report_count": 8,
        "input_certified_count": 8,
        "contract_clause_count": len(contract_rows),
        "contract_pass_count": sum(row["pass_flag"] for row in contract_rows),
        "contract_fail_count": len(contract_rows)
        - sum(row["pass_flag"] for row in contract_rows),
        "first_failure_clause_code": contract_rows[first_failure_index]["clause_code"],
        "downstream_blocked_clause_count": sum(
            row["downstream_blocked_flag"] for row in contract_rows
        ),
        "atom_count": int(rim_s["atom_count"]),
        "complement_pair_count": int(rim_s["complement_pair_count"]),
        "rim_phase_count": int(rim_select_s["rim_phase_count"]),
        "golden_class_count": int(rim_s["golden_defect_class_count"]),
        "golden_unoriented_rim_count": int(rim_select_s["golden_unoriented_rims"]),
        "formal_c2_selector_count": int(sel_s["formal_c2_selector_count"]),
        "physical_selector_axiom_flag": physical_selector_axiom,
        "physical_selector_candidate_count": physical_selector_candidates,
        "raw_compatible_packet_pair_count": raw_packet_bridge,
        "missing_restriction_bridge_count": int(binc_s["missing_restriction_bridge_count"]),
        "semantic_transition_operation_flag": semantic_operation,
        "stress_transition_shared_key_count": stress_transition_key,
        "dim4_reduction_certified_flag": dim4_flag,
        "certified_dim4_candidate_count": int(dim4_s["certified_dim4_candidate_count"]),
        "gr_source_selector_ready_flag": gr_ready,
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
        "sel": sel,
        "rim": rim,
        "rim_select": rim_select,
        "binc": binc,
        "transition": transition,
        "dim4": dim4,
        "pax": pax,
        "oprom": oprom,
        "contract_rows": contract_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    contract_table = table_from_rows(CONTRACT_COLUMNS, rows["contract_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    checks = {
        "input_reports_certified": rows["sel"].get("status")
        == "LONG_SEL_PHYSICAL_SELECTOR_AXIOM_OBSTRUCTION_CERTIFIED"
        and rows["sel"].get("all_checks_pass") is True
        and rows["rim"].get("status") == "LONG_RIM_DEFECT_PHASES_CERTIFIED"
        and rows["rim"].get("all_checks_pass") is True
        and rows["rim_select"].get("status")
        == "LONG_RIM_SELECT_GAUGE_OBSTRUCTION_CERTIFIED"
        and rows["rim_select"].get("all_checks_pass") is True
        and rows["binc"].get("status") == "LONG_BINC_CERTIFIED"
        and rows["binc"].get("all_checks_pass") is True
        and rows["transition"].get("status")
        == "LONG_TRANSITION_SEM_OBSTRUCTION_CERTIFIED"
        and rows["transition"].get("all_checks_pass") is True
        and rows["dim4"].get("status") == "LONG_DIM4_GATE_OBSTRUCTION_CERTIFIED"
        and rows["dim4"].get("all_checks_pass") is True
        and rows["pax"].get("status")
        == "LONG_PAX_PHYSICAL_SELECTOR_CANDIDATE_CERTIFIED"
        and rows["pax"].get("all_checks_pass") is True
        and rows["oprom"].get("status")
        == "LONG_OPROM_GOLDEN_OPERATION_PROMOTION_OBSTRUCTION_CERTIFIED"
        and rows["oprom"].get("all_checks_pass") is True,
        "contract_prefix_passes": obs["atom_count"] == 20
        and obs["rim_phase_count"] == 63
        and obs["golden_class_count"] == 1
        and obs["formal_c2_selector_count"] == 8
        and obs["contract_pass_count"] == 4,
        "first_failure_is_physical_selector_axiom": obs["first_failure_clause_code"]
        == CLAUSE_CODES["physical_selector_axiom_present"]
        and obs["physical_selector_axiom_flag"] == 0
        and obs["physical_selector_candidate_count"] == 1,
        "downstream_failures_preserved": obs["raw_compatible_packet_pair_count"] == 0
        and obs["missing_restriction_bridge_count"] == 3
        and obs["semantic_transition_operation_flag"] == 0
        and obs["stress_transition_shared_key_count"] == 0
        and obs["dim4_reduction_certified_flag"] == 0
        and obs["gr_source_selector_ready_flag"] == 0,
        "table_shapes_match": contract_table.shape
        == (len(CLAUSE_CODES), len(CONTRACT_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "physical_selector_contract_first_failure",
        "summary": {
            "contract_clause_count": obs["contract_clause_count"],
            "contract_pass_count": obs["contract_pass_count"],
            "contract_fail_count": obs["contract_fail_count"],
            "first_failure": "physical_selector_axiom_present",
            "first_failure_clause_code": obs["first_failure_clause_code"],
            "downstream_blocked_clause_count": obs["downstream_blocked_clause_count"],
            "atom_count": obs["atom_count"],
            "rim_phase_count": obs["rim_phase_count"],
            "golden_unoriented_rims": obs["golden_unoriented_rim_count"],
            "formal_c2_selector_count": obs["formal_c2_selector_count"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "physical_selector_candidate_count": obs[
                "physical_selector_candidate_count"
            ],
            "raw_compatible_packet_pair_count": obs[
                "raw_compatible_packet_pair_count"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "stress_transition_shared_key_count": obs[
                "stress_transition_shared_key_count"
            ],
            "dim4_reduction_certified_flag": obs["dim4_reduction_certified_flag"],
            "gr_source_selector_ready_flag": obs["gr_source_selector_ready_flag"],
        },
        "clause_code_map": {str(value): key for key, value in CLAUSE_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "contract_table_sha256": sha_array(contract_table),
        "contract_text_sha256": sha_text(
            csv_text(CONTRACT_COLUMNS, rows["contract_rows"])
        ),
        "observable_table_sha256": sha_array(observable_table),
    }
    psel = {
        "schema": "long.psel@1",
        "object": "physical_selector_contract_first_failure",
        "status": STATUS if all(checks.values()) else "LONG_PSEL_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.psel.report@1",
        "status": psel["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_psel defines the minimal finite physical-selector contract "
            "needed to move from the current atom/rim/packet/transition surfaces "
            "toward a selected physical boundary. The atom domain, rim-phase "
            "domain, golden-phase candidate, formal selector inventory, and one "
            "materialized golden-clock selector candidate are present. The first "
            "failing clause is still acceptance of the physical selector axiom "
            "itself; packet bridge, golden operation promotion, stress-coupling, and "
            "1+3 clauses remain downstream blocked."
        ),
        "stage_protocol": {
            "draft": "read long_sel, long_rim, long_rim_select, long_binc, long_transition_sem, long_dim4_gate, long_pax, and long_oprom",
            "witness": "emit ordered contract clauses and observables",
            "coherence": "check prefix passing clauses, first failure, downstream blocked clauses, input statuses, and table hashes",
            "closure": "certify the first failing physical-selector contract clause",
            "emit": "write long_psel artifacts and verifier hook",
        },
        "inputs": {
            "long_sel": input_entry(
                LONG_SEL,
                {
                    "status": rows["sel"].get("status"),
                    "certificate_sha256": rows["sel"].get("certificate_sha256"),
                },
            ),
            "long_rim": input_entry(
                LONG_RIM,
                {
                    "status": rows["rim"].get("status"),
                    "certificate_sha256": rows["rim"].get("certificate_sha256"),
                },
            ),
            "long_rim_select": input_entry(
                LONG_RIM_SELECT,
                {
                    "status": rows["rim_select"].get("status"),
                    "certificate_sha256": rows["rim_select"].get("certificate_sha256"),
                },
            ),
            "long_binc": input_entry(
                LONG_BINC,
                {
                    "status": rows["binc"].get("status"),
                    "certificate_sha256": rows["binc"].get("certificate_sha256"),
                },
            ),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition"].get("status"),
                    "certificate_sha256": rows["transition"].get("certificate_sha256"),
                },
            ),
            "long_dim4_gate": input_entry(
                LONG_DIM4_GATE,
                {
                    "status": rows["dim4"].get("status"),
                    "certificate_sha256": rows["dim4"].get("certificate_sha256"),
                },
            ),
            "long_pax": input_entry(
                LONG_PAX,
                {
                    "status": rows["pax"].get("status"),
                    "certificate_sha256": rows["pax"].get("certificate_sha256"),
                },
            ),
            "long_oprom": input_entry(
                LONG_OPROM,
                {
                    "status": rows["oprom"].get("status"),
                    "certificate_sha256": rows["oprom"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "psel": relpath(OUT_DIR / "psel.json"),
            "contract_csv": relpath(OUT_DIR / "contract.csv"),
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
                "the finite physical-selector contract has ten ordered clauses",
                "the atom boundary, rim-phase domain, golden candidate, and formal selector inventory clauses pass",
                "one admissible golden-clock selector candidate is materialized by long_pax",
                "the first failing clause is still the unaccepted physical selector axiom",
                "packet bridge, golden operation promotion, stress-coupling, 1+3, and GR-source clauses are downstream blocked",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of a future physical selector axiom",
                "a raw A985-to-packet operator bridge",
                "semantic A985 transition operations",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Decide the materialized long_pax selector candidate: reject it, "
            "accept it as an explicit extra physical axiom, or avoid the extra "
            "axiom by constructing semantic A985 operation rows for the 59 "
            "long_oprom matched golden relation witnesses."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.psel.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.psel.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "psel": psel,
        "contract_csv": csv_text(CONTRACT_COLUMNS, rows["contract_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "contract_table": contract_table,
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
    write_json(OUT_DIR / "psel.json", payloads["psel"])
    (OUT_DIR / "contract.csv").write_text(payloads["contract_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        contract_table=payloads["contract_table"],
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
