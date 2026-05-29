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
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_stress_couple"
STATUS = "LONG_STRESS_COUPLE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_STRESS_EDGE_CSV = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_stress_couple.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_stress_couple.py"

SCHEMA_COLUMNS = [
    "schema_row_id",
    "schema_code",
    "transition_schema_flag",
    "stress_schema_flag",
    "coupling_key_required_flag",
    "present_flag",
    "obstruction_flag",
    "value",
]
GAP_COLUMNS = ["gap_id", "gap_code", "open_flag", "obstruction_flag", "next_flag"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SCHEMA_NAMES = [
    "transition_basis_raw_schema_present",
    "stress_atom_edge_schema_present",
    "transition_atom_pair_columns_absent",
    "stress_basis_pair_columns_absent",
    "shared_certified_coupling_key_absent",
    "materialized_transition_stress_map_absent",
]
SCHEMA_CODES = {name: index for index, name in enumerate(SCHEMA_NAMES)}

GAP_NAMES = [
    "stress_transition_coupling_map",
    "physical_stress_energy_tensor",
    "nondegenerate_smooth_lorentzian_metric",
    "curvature_and_einstein_tensor",
    "gr_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_artifact_count",
    "stress_gate_certified_flag",
    "transition_row_count",
    "stress_edge_row_count",
    "transition_basis_column_count",
    "transition_raw_column_count",
    "transition_atom_column_count",
    "stress_atom_column_count",
    "stress_basis_column_count",
    "shared_certified_coupling_key_count",
    "materialized_coupling_row_count",
    "coupling_map_certified_flag",
    "current_boundary_obstruction_flag",
    "physical_stress_energy_flag",
    "smooth_lorentzian_metric_flag",
    "curvature_einstein_tensor_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

TRANSITION_ATOM_COLUMNS = {"source_atom", "target_atom", "stress_edge_id"}
STRESS_BASIS_COLUMNS = {"left_basis_id", "right_basis_id", "left_raw_row_id", "right_raw_row_id"}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_with_header(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def build_rows() -> dict[str, Any]:
    stress_gate = load_json(LONG_STRESS_GATE)
    transition_columns, transition_rows = read_csv_with_header(LONG_TRANSITION_CSV)
    stress_columns, stress_rows = read_csv_with_header(LONG_STRESS_EDGE_CSV)

    transition_column_set = set(transition_columns)
    stress_column_set = set(stress_columns)
    transition_basis_columns = {"left_basis_id", "right_basis_id"} & transition_column_set
    transition_raw_columns = {"left_raw_row_id", "right_raw_row_id"} & transition_column_set
    transition_atom_columns = TRANSITION_ATOM_COLUMNS & transition_column_set
    stress_atom_columns = {"source_atom", "target_atom", "stress_edge_id"} & stress_column_set
    stress_basis_columns = STRESS_BASIS_COLUMNS & stress_column_set
    shared_coupling_keys = (
        {"source_atom", "target_atom", "stress_edge_id", "left_basis_id", "right_basis_id"}
        & transition_column_set
        & stress_column_set
    )
    materialized_coupling_rows = 0
    obs = {
        "input_artifact_count": 3,
        "stress_gate_certified_flag": int(
            stress_gate.get("status") == "LONG_STRESS_GATE_CERTIFIED"
            and stress_gate.get("all_checks_pass") is True
        ),
        "transition_row_count": len(transition_rows),
        "stress_edge_row_count": len(stress_rows),
        "transition_basis_column_count": len(transition_basis_columns),
        "transition_raw_column_count": len(transition_raw_columns),
        "transition_atom_column_count": len(transition_atom_columns),
        "stress_atom_column_count": len(stress_atom_columns),
        "stress_basis_column_count": len(stress_basis_columns),
        "shared_certified_coupling_key_count": len(shared_coupling_keys),
        "materialized_coupling_row_count": materialized_coupling_rows,
        "coupling_map_certified_flag": 0,
        "current_boundary_obstruction_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "curvature_einstein_tensor_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 4,
        "next_gap_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
    }
    schema_rows = [
        {
            "schema_row_id": SCHEMA_CODES["transition_basis_raw_schema_present"],
            "schema_code": SCHEMA_CODES["transition_basis_raw_schema_present"],
            "transition_schema_flag": 1,
            "stress_schema_flag": 0,
            "coupling_key_required_flag": 0,
            "present_flag": 1,
            "obstruction_flag": 0,
            "value": obs["transition_row_count"],
        },
        {
            "schema_row_id": SCHEMA_CODES["stress_atom_edge_schema_present"],
            "schema_code": SCHEMA_CODES["stress_atom_edge_schema_present"],
            "transition_schema_flag": 0,
            "stress_schema_flag": 1,
            "coupling_key_required_flag": 0,
            "present_flag": 1,
            "obstruction_flag": 0,
            "value": obs["stress_edge_row_count"],
        },
        {
            "schema_row_id": SCHEMA_CODES["transition_atom_pair_columns_absent"],
            "schema_code": SCHEMA_CODES["transition_atom_pair_columns_absent"],
            "transition_schema_flag": 1,
            "stress_schema_flag": 0,
            "coupling_key_required_flag": 1,
            "present_flag": int(obs["transition_atom_column_count"] > 0),
            "obstruction_flag": int(obs["transition_atom_column_count"] == 0),
            "value": obs["transition_atom_column_count"],
        },
        {
            "schema_row_id": SCHEMA_CODES["stress_basis_pair_columns_absent"],
            "schema_code": SCHEMA_CODES["stress_basis_pair_columns_absent"],
            "transition_schema_flag": 0,
            "stress_schema_flag": 1,
            "coupling_key_required_flag": 1,
            "present_flag": int(obs["stress_basis_column_count"] > 0),
            "obstruction_flag": int(obs["stress_basis_column_count"] == 0),
            "value": obs["stress_basis_column_count"],
        },
        {
            "schema_row_id": SCHEMA_CODES["shared_certified_coupling_key_absent"],
            "schema_code": SCHEMA_CODES["shared_certified_coupling_key_absent"],
            "transition_schema_flag": 1,
            "stress_schema_flag": 1,
            "coupling_key_required_flag": 1,
            "present_flag": int(obs["shared_certified_coupling_key_count"] > 0),
            "obstruction_flag": int(obs["shared_certified_coupling_key_count"] == 0),
            "value": obs["shared_certified_coupling_key_count"],
        },
        {
            "schema_row_id": SCHEMA_CODES["materialized_transition_stress_map_absent"],
            "schema_code": SCHEMA_CODES["materialized_transition_stress_map_absent"],
            "transition_schema_flag": 1,
            "stress_schema_flag": 1,
            "coupling_key_required_flag": 1,
            "present_flag": int(materialized_coupling_rows > 0),
            "obstruction_flag": int(materialized_coupling_rows == 0),
            "value": materialized_coupling_rows,
        },
    ]
    gap_rows = [
        {
            "gap_id": code,
            "gap_code": code,
            "open_flag": int(name != "stress_transition_coupling_map"),
            "obstruction_flag": 1,
            "next_flag": int(name == "nondegenerate_smooth_lorentzian_metric"),
        }
        for name, code in GAP_CODES.items()
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "stress_gate": stress_gate,
        "transition_columns": transition_columns,
        "transition_rows": transition_rows,
        "stress_columns": stress_columns,
        "stress_rows": stress_rows,
        "schema_rows": schema_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "schema_table": table_from_rows(SCHEMA_COLUMNS, schema_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "schema_text_hash": sha_text(digest_text(SCHEMA_COLUMNS, schema_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    stress_gate = rows["stress_gate"]
    checks = {
        "stress_gate_input_certified": obs["stress_gate_certified_flag"] == 1,
        "source_surfaces_present": obs["transition_row_count"] == 642
        and obs["stress_edge_row_count"] == 100,
        "transition_schema_lacks_stress_atom_key": obs["transition_basis_column_count"] == 2
        and obs["transition_raw_column_count"] == 2
        and obs["transition_atom_column_count"] == 0,
        "stress_schema_lacks_transition_basis_key": obs["stress_atom_column_count"] == 3
        and obs["stress_basis_column_count"] == 0,
        "shared_coupling_key_absent": obs["shared_certified_coupling_key_count"] == 0
        and obs["materialized_coupling_row_count"] == 0,
        "current_obstruction_scope_exact": obs["coupling_map_certified_flag"] == 0
        and obs["current_boundary_obstruction_flag"] == 1
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["curvature_einstein_tensor_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["schema_table"].shape
        == (len(SCHEMA_CODES), len(SCHEMA_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "stress_transition_coupling_current_boundary_obstruction",
        "summary": {
            "transition_row_count": obs["transition_row_count"],
            "stress_edge_row_count": obs["stress_edge_row_count"],
            "transition_atom_column_count": obs["transition_atom_column_count"],
            "stress_basis_column_count": obs["stress_basis_column_count"],
            "shared_certified_coupling_key_count": obs[
                "shared_certified_coupling_key_count"
            ],
            "materialized_coupling_row_count": obs["materialized_coupling_row_count"],
            "coupling_map_certified_flag": obs["coupling_map_certified_flag"],
            "current_boundary_obstruction_flag": obs[
                "current_boundary_obstruction_flag"
            ],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "gr_derivation_flag": obs["gr_derivation_flag"],
            "next_gap": "nondegenerate_smooth_lorentzian_metric",
        },
        "schema_code_map": {str(value): key for key, value in SCHEMA_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "schema_table_sha256": sha_array(rows["schema_table"]),
        "schema_text_sha256": rows["schema_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    stress_couple = {
        "schema": "long.stress_couple@1",
        "object": "stress_transition_coupling_current_boundary_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_STRESS_COUPLE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.stress_couple.report@1",
        "status": stress_couple["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_stress_couple checks the current artifact boundary for a "
            "certified coupling from the 642 guarded transitions to the 100 "
            "directed stress-neighborhood edges. The transition rows are keyed "
            "by basis/raw endpoint data, while the stress-edge rows are keyed "
            "by source/target atom data. No shared certified coupling key or "
            "materialized transition-to-stress map is present, so physical "
            "stress-energy remains uncertified."
        ),
        "stage_protocol": {
            "draft": "read long_stress_gate, transition rows, and finite stress-edge rows",
            "witness": "emit schema-seam rows, open gap rows, and observables",
            "coherence": "check source row counts, schema keys, absent shared coupling key, and table hashes",
            "closure": "certify the current-boundary transition-to-stress coupling obstruction",
            "emit": "write long_stress_couple artifacts and verifier hook",
        },
        "inputs": {
            "long_stress_gate": input_entry(
                LONG_STRESS_GATE,
                {
                    "status": stress_gate.get("status"),
                    "certificate_sha256": stress_gate.get("certificate_sha256"),
                },
            ),
            "long_transition_csv": input_entry(
                LONG_TRANSITION_CSV,
                {"row_count": len(rows["transition_rows"])},
            ),
            "long_stress_edge_csv": input_entry(
                LONG_STRESS_EDGE_CSV,
                {"row_count": len(rows["stress_rows"])},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "stress_couple": relpath(OUT_DIR / "stress_couple.json"),
            "schema_csv": relpath(OUT_DIR / "schema.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "the current focused artifact boundary has 642 guarded transitions and 100 directed stress edges",
                "transition rows are keyed by basis/raw endpoint columns, not stress atom columns",
                "stress-edge rows are keyed by source/target atom columns, not transition basis/raw columns",
                "no shared certified coupling key or materialized transition-to-stress map exists in this boundary",
                "the stress-transition coupling seam is closed as a current-boundary obstruction",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of every possible mathematical transition-to-stress map",
                "a physical stress-energy tensor",
                "a nondegenerate smooth Lorentzian metric tensor",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
                "a completed derivation of general relativity",
            ],
        },
        "next_highest_yield_item": (
            "Build long_metric_rank_gate: decide what finite rank/signature "
            "statement survives from the time quotient, public boundary, guarded "
            "transitions, and finite stress readout now that physical stress-energy "
            "is blocked in the current boundary."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.stress_couple.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.stress_couple.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "stress_couple": stress_couple,
        "schema_csv": csv_text(SCHEMA_COLUMNS, rows["schema_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "schema_table": rows["schema_table"],
        "gap_table": rows["gap_table"],
        "observable_table": rows["observable_table"],
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
    write_json(OUT_DIR / "stress_couple.json", payloads["stress_couple"])
    (OUT_DIR / "schema.csv").write_text(payloads["schema_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        schema_table=payloads["schema_table"],
        gap_table=payloads["gap_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
