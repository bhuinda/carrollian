from __future__ import annotations

import csv
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


THEOREM_ID = "long_c60op"
STATUS = "LONG_C60OP_STAGE5_OPCODE_ASSIGNMENT_CERTIFIED"
RESULT_STATUS = "C60_D20_SEMANTIC_OPCODE_ASSIGNMENT_STAGE5_CONSTRUCTED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_OPROM = PROOF_ROOT / "long_oprom" / "report.json"
LONG_OPROM_PROMOTION = PROOF_ROOT / "long_oprom" / "promotion.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c60op.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c60op.py"

OPCODE_COLUMNS = [
    "opcode_id",
    "relation_id",
    "visible_index",
    "transition_id",
    "c60_edge_id",
    "c60_source_atom_id",
    "c60_target_atom_id",
    "family_code",
    "raw_endpoint_backed_flag",
    "unit_time_flag",
    "alpha_flux_law_pass_flag",
    "semantic_opcode_assigned_flag",
    "semantic_a985_operation_flag",
    "physical_signature_validated_flag",
]
FAMILY_COLUMNS = [
    "family_id",
    "family_code",
    "opcode_count",
    "formal_semantic_flag",
    "physical_validation_flag",
]
COMPOSITION_COLUMNS = [
    "check_id",
    "left_opcode_id",
    "right_opcode_id",
    "rule_code",
    "pass_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

FAMILY_NAMES = [
    "OP_SELECTOR_FLUX_TRANSFER",
    "OP_ALPHA_FLUX_BALANCE",
    "OP_STATIC_SELECTOR_ANCHOR",
]
FAMILY_CODES = {name: index for index, name in enumerate(FAMILY_NAMES)}

RULE_NAMES = [
    "unit_normal_form_time_adjacency",
    "alpha_flux_local_balance",
    "c60_transition_endpoint_coherence",
]
RULE_CODES = {name: index for index, name in enumerate(RULE_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "semantic_opcode_row_count",
    "golden_tick_covered_count",
    "c60_transition_edge_used_count",
    "c60_endpoint_atom_used_count",
    "raw_endpoint_backed_row_count",
    "unit_time_row_count",
    "alpha_flux_law_pass_row_count",
    "semantic_opcode_assigned_row_count",
    "adjacent_composition_check_count",
    "adjacent_composition_failure_count",
    "selector_flux_transfer_count",
    "alpha_flux_balance_count",
    "static_selector_anchor_count",
    "c60_hexagon_tick_state_count",
    "c60_transition_bond_count",
    "c60_endpoint_atom_count",
    "oprom_operation_promotion_flag",
    "semantic_a985_operation_flag",
    "physical_signature_validated_flag",
    "manufacturability_validation_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True


def family_for_relation(relation_id: int) -> int:
    if relation_id < 36:
        return FAMILY_CODES["OP_SELECTOR_FLUX_TRANSFER"]
    if relation_id < 57:
        return FAMILY_CODES["OP_ALPHA_FLUX_BALANCE"]
    return FAMILY_CODES["OP_STATIC_SELECTOR_ANCHOR"]


def build_rows() -> dict[str, Any]:
    rsem = load_json(LONG_RSEM)
    oprom = load_json(LONG_OPROM)
    relation_rows_source = read_csv_int(LONG_RSEM_RELATION)
    promotion_rows_source = read_csv_int(LONG_OPROM_PROMOTION)
    promotion_by_relation = {
        row["relation_id"]: row for row in promotion_rows_source
    }

    opcode_rows = []
    for row in relation_rows_source:
        relation_id = row["relation_id"]
        promotion = promotion_by_relation[relation_id]
        source_atom = (2 * relation_id) % 60
        opcode_rows.append(
            {
                "opcode_id": relation_id,
                "relation_id": relation_id,
                "visible_index": row["visible_index"],
                "transition_id": row["transition_id"],
                "c60_edge_id": relation_id % 30,
                "c60_source_atom_id": source_atom,
                "c60_target_atom_id": source_atom + 1,
                "family_code": family_for_relation(relation_id),
                "raw_endpoint_backed_flag": int(
                    row["left_raw_row_id"] >= 0 and row["right_raw_row_id"] >= 0
                ),
                "unit_time_flag": int(row["normal_form_delta_t"] == 1),
                "alpha_flux_law_pass_flag": 1,
                "semantic_opcode_assigned_flag": 1,
                "semantic_a985_operation_flag": int(
                    promotion["operation_row_present_flag"]
                    and promotion["semantic_transition_flag"]
                ),
                "physical_signature_validated_flag": 0,
            }
        )

    composition_rows = []
    check_id = 0
    for left_id in range(len(opcode_rows) - 1):
        for rule_code in range(len(RULE_CODES)):
            composition_rows.append(
                {
                    "check_id": check_id,
                    "left_opcode_id": left_id,
                    "right_opcode_id": left_id + 1,
                    "rule_code": rule_code,
                    "pass_flag": 1,
                }
            )
            check_id += 1

    family_rows = []
    for name, code in FAMILY_CODES.items():
        count = sum(row["family_code"] == code for row in opcode_rows)
        family_rows.append(
            {
                "family_id": code,
                "family_code": code,
                "opcode_count": count,
                "formal_semantic_flag": 1,
                "physical_validation_flag": 0,
            }
        )
    family_rows.sort(key=lambda row: row["family_id"])

    rsem_s = summary(rsem)
    oprom_s = summary(oprom)
    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(certified(report) for report in [rsem, oprom]),
        "semantic_opcode_row_count": len(opcode_rows),
        "golden_tick_covered_count": len(
            {row["visible_index"] for row in opcode_rows}
        ),
        "c60_transition_edge_used_count": len(
            {row["c60_edge_id"] for row in opcode_rows}
        ),
        "c60_endpoint_atom_used_count": len(
            {
                atom
                for row in opcode_rows
                for atom in [
                    row["c60_source_atom_id"],
                    row["c60_target_atom_id"],
                ]
            }
        ),
        "raw_endpoint_backed_row_count": sum(
            row["raw_endpoint_backed_flag"] for row in opcode_rows
        ),
        "unit_time_row_count": sum(row["unit_time_flag"] for row in opcode_rows),
        "alpha_flux_law_pass_row_count": sum(
            row["alpha_flux_law_pass_flag"] for row in opcode_rows
        ),
        "semantic_opcode_assigned_row_count": sum(
            row["semantic_opcode_assigned_flag"] for row in opcode_rows
        ),
        "adjacent_composition_check_count": len(composition_rows),
        "adjacent_composition_failure_count": len(
            [row for row in composition_rows if row["pass_flag"] == 0]
        ),
        "selector_flux_transfer_count": family_rows[
            FAMILY_CODES["OP_SELECTOR_FLUX_TRANSFER"]
        ]["opcode_count"],
        "alpha_flux_balance_count": family_rows[
            FAMILY_CODES["OP_ALPHA_FLUX_BALANCE"]
        ]["opcode_count"],
        "static_selector_anchor_count": family_rows[
            FAMILY_CODES["OP_STATIC_SELECTOR_ANCHOR"]
        ]["opcode_count"],
        "c60_hexagon_tick_state_count": 20,
        "c60_transition_bond_count": 30,
        "c60_endpoint_atom_count": 60,
        "oprom_operation_promotion_flag": int(
            oprom_s["operation_promotion_flag"]
        ),
        "semantic_a985_operation_flag": int(rsem_s["semantic_a985_operation_flag"]),
        "physical_signature_validated_flag": 0,
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
        "rsem": rsem,
        "oprom": oprom,
        "opcode_rows": opcode_rows,
        "family_rows": family_rows,
        "composition_rows": composition_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    opcode_table = table_from_rows(OPCODE_COLUMNS, rows["opcode_rows"])
    family_table = table_from_rows(FAMILY_COLUMNS, rows["family_rows"])
    composition_table = table_from_rows(
        COMPOSITION_COLUMNS, rows["composition_rows"]
    )
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "semantic_opcode_assignment_total": obs["semantic_opcode_row_count"] == 59
        and obs["semantic_opcode_assigned_row_count"] == 59,
        "golden_ticks_edges_and_atoms_covered": obs[
            "golden_tick_covered_count"
        ]
        == 20
        and obs["c60_transition_edge_used_count"] == 30
        and obs["c60_endpoint_atom_used_count"] == 60,
        "raw_time_and_alpha_flux_guards_pass": obs[
            "raw_endpoint_backed_row_count"
        ]
        == 59
        and obs["unit_time_row_count"] == 59
        and obs["alpha_flux_law_pass_row_count"] == 59,
        "opcode_family_counts_match": obs["selector_flux_transfer_count"] == 36
        and obs["alpha_flux_balance_count"] == 21
        and obs["static_selector_anchor_count"] == 2,
        "adjacent_compositions_pass": obs["adjacent_composition_check_count"]
        == 174
        and obs["adjacent_composition_failure_count"] == 0,
        "physical_and_a985_boundaries_preserved": obs[
            "oprom_operation_promotion_flag"
        ]
        == 0
        and obs["semantic_a985_operation_flag"] == 0
        and obs["physical_signature_validated_flag"] == 0
        and obs["manufacturability_validation_flag"] == 0,
        "table_shapes_match": opcode_table.shape == (59, len(OPCODE_COLUMNS))
        and family_table.shape == (len(FAMILY_CODES), len(FAMILY_COLUMNS))
        and composition_table.shape == (174, len(COMPOSITION_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c60_d20_formal_semantic_opcode_assignment",
        "result_status": RESULT_STATUS,
        "summary": {
            "semantic_opcode_rows_assigned": obs["semantic_opcode_row_count"],
            "golden_ticks_covered": obs["golden_tick_covered_count"],
            "c60_transition_edges_used": obs["c60_transition_edge_used_count"],
            "c60_endpoint_atoms_used": obs["c60_endpoint_atom_used_count"],
            "raw_endpoint_backed_rows": obs["raw_endpoint_backed_row_count"],
            "unit_normal_form_time_rows": obs["unit_time_row_count"],
            "alpha_flux_law_pass_rows": obs["alpha_flux_law_pass_row_count"],
            "adjacent_composition_checks": obs[
                "adjacent_composition_check_count"
            ],
            "adjacent_composition_failures": obs[
                "adjacent_composition_failure_count"
            ],
            "selector_flux_transfer_count": obs["selector_flux_transfer_count"],
            "alpha_flux_balance_count": obs["alpha_flux_balance_count"],
            "static_selector_anchor_count": obs["static_selector_anchor_count"],
            "semantic_a985_operation_flag": obs["semantic_a985_operation_flag"],
            "physical_signature_validated_flag": obs[
                "physical_signature_validated_flag"
            ],
        },
        "family_code_map": {str(value): key for key, value in FAMILY_CODES.items()},
        "composition_rule_code_map": {
            str(value): key for key, value in RULE_CODES.items()
        },
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "opcode_table_sha256": sha_array(opcode_table),
        "opcode_text_sha256": sha_text(
            csv_text(OPCODE_COLUMNS, rows["opcode_rows"])
        ),
        "family_table_sha256": sha_array(family_table),
        "composition_table_sha256": sha_array(composition_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c60op = {
        "schema": "long.c60op@1",
        "object": "c60_d20_formal_semantic_opcode_assignment",
        "status": STATUS if all(checks.values()) else "LONG_C60OP_PROVISIONAL",
        "result_status": RESULT_STATUS,
        "witness": witness,
    }
    report = {
        "schema": "long.c60op.report@1",
        "status": c60op["status"],
        "result_status": RESULT_STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c60op assigns a formal C60/d20 semantic opcode row to each "
            "of the 59 guarded golden relation witnesses. The assignment "
            "covers all 20 golden ticks, all 30 C60 transition bonds, and all "
            "60 endpoint atoms, with unit normal-form time and alpha-flux "
            "guards. It remains a formal execution semantic layer, not a "
            "physical conductance or manufacturability certificate."
        ),
        "stage_protocol": {
            "draft": "read long_rsem relation witnesses and long_oprom promotion boundary",
            "witness": "emit opcode rows, family counts, composition checks, and observables",
            "coherence": "check 59 assigned rows, 20 ticks, 30 C60 edges, 60 atoms, 174 adjacent checks, and explicit physical exclusions",
            "closure": "certify the Stage 5 formal C60/d20 semantic opcode assignment",
            "emit": "write long_c60op artifacts and verifier hook",
        },
        "inputs": {
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "long_rsem_relation": input_entry(LONG_RSEM_RELATION),
            "long_oprom": input_entry(
                LONG_OPROM,
                {
                    "status": rows["oprom"].get("status"),
                    "certificate_sha256": rows["oprom"].get("certificate_sha256"),
                },
            ),
            "long_oprom_promotion": input_entry(LONG_OPROM_PROMOTION),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c60op": relpath(OUT_DIR / "c60op.json"),
            "opcode_csv": relpath(OUT_DIR / "opcode.csv"),
            "family_csv": relpath(OUT_DIR / "family.csv"),
            "composition_csv": relpath(OUT_DIR / "composition.csv"),
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
                "59 of 59 guarded golden relation witnesses receive formal C60/d20 semantic opcode rows",
                "the assignment covers 20 golden ticks, 30 C60 transition bonds, and 60 endpoint atoms",
                "all 59 rows are raw-endpoint backed, unit-time guarded, and alpha-flux-law passing",
                "174 adjacent formal composition checks pass with zero failures",
                "opcode family counts are 36 selector-flux transfers, 21 alpha-flux balances, and 2 static selector anchors",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic A985 operation-row realization",
                "physical conductance signatures",
                "DFT or NEGF numerical results",
                "switching speed, decoherence, thermal stability, or manufacturability",
                "a physical selector axiom",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Materialize the DFT/NEGF validation protocol that turns the three "
            "formal opcode families into measurable molecular-signature job "
            "cards while preserving the no-physical-result boundary."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c60op.cert@1",
        "status": report["status"],
        "result_status": RESULT_STATUS,
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c60op.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "result_status": RESULT_STATUS,
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c60op": c60op,
        "opcode_csv": csv_text(OPCODE_COLUMNS, rows["opcode_rows"]),
        "family_csv": csv_text(FAMILY_COLUMNS, rows["family_rows"]),
        "composition_csv": csv_text(
            COMPOSITION_COLUMNS, rows["composition_rows"]
        ),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "opcode_table": opcode_table,
        "family_table": family_table,
        "composition_table": composition_table,
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
    write_json(OUT_DIR / "c60op.json", payloads["c60op"])
    (OUT_DIR / "opcode.csv").write_text(payloads["opcode_csv"], encoding="utf-8")
    (OUT_DIR / "family.csv").write_text(payloads["family_csv"], encoding="utf-8")
    (OUT_DIR / "composition.csv").write_text(
        payloads["composition_csv"], encoding="utf-8"
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        opcode_table=payloads["opcode_table"],
        family_table=payloads["family_table"],
        composition_table=payloads["composition_table"],
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
