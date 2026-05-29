from __future__ import annotations

import json
import hashlib
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


THEOREM_ID = "long_gr"
STATUS = "LONG_GR_PATHWAY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
CORE_A985 = ROOT / "data" / "core" / "a985.json"
C985_FINAL = PROOF_ROOT / "c985_final_multifusion_certificate" / "report.json"
D20_ATLAS = PROOF_ROOT / "c985_d20_boundary_invariant_atlas" / "report.json"
HYPERBOLIC_GRAPH = PROOF_ROOT / "c985_d20_hyperbolic_boundary_graph" / "report.json"
POINCARE = PROOF_ROOT / "c985_d20_poincare_embedding" / "report.json"
STRESS_GRAPH = PROOF_ROOT / "c985_d20_boundary_neighborhood_stress_graph" / "report.json"
LONG_ANOM = PROOF_ROOT / "long_anom" / "report.json"
LONG_MAT = PROOF_ROOT / "long_mat" / "report.json"
LONG_AUTO = PROOF_ROOT / "long_auto" / "report.json"
LONG_ORAC = PROOF_ROOT / "long_orac" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_gr.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_gr.py"

INPUTS = {
    "core_a985": (CORE_A985, "PASS"),
    "c985_final": (C985_FINAL, "C985_FINITE_SEMISIMPLE_MULTIFUSION_CATEGORY_CERTIFIED"),
    "d20_atlas": (D20_ATLAS, "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED"),
    "hyperbolic_graph": (HYPERBOLIC_GRAPH, "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED"),
    "poincare": (POINCARE, "C985_D20_POINCARE_EMBEDDING_CERTIFIED"),
    "stress_graph": (STRESS_GRAPH, "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"),
    "long_anom": (LONG_ANOM, "LONG_ANOM_CERTIFIED"),
    "long_mat": (LONG_MAT, "LONG_MAT_CERTIFIED"),
    "long_auto": (LONG_AUTO, "LONG_AUTO_CERTIFIED"),
    "long_orac": (LONG_ORAC, "LONG_ORAC_CERTIFIED"),
}

SURFACE_COLUMNS = [
    "surface_id",
    "role_code",
    "input_code",
    "certified_flag",
    "a985_chain_flag",
    "finite_flag",
    "continuum_flag",
    "gr_derivation_flag",
    "open_gap_count",
]
GAP_COLUMNS = [
    "gap_id",
    "obligation_code",
    "required_for_gr_flag",
    "certified_flag",
    "blocked_by_finite_scope_flag",
    "next_flag",
    "dependency_surface_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SURFACE_NAMES = [
    "a985_core_seed",
    "c985_finite_multifusion_category",
    "d20_boundary_atlas",
    "hyperbolic_boundary_graph",
    "poincare_disk_readout",
    "boundary_stress_graph",
    "finite_anomaly_ward_bms_surface",
    "finite_matrix_charge_wall_surface",
    "finite_automorphic_fourier_surface",
    "oracle_status_split",
]
SURFACE_CODES = {name: index for index, name in enumerate(SURFACE_NAMES)}

ROLE_NAMES = [
    "source_seed",
    "finite_category",
    "finite_boundary_geometry",
    "finite_metric_readout",
    "finite_stress_flux_readout",
    "finite_symmetry_anomaly_readout",
    "finite_matrix_dynamics_readout",
    "finite_automorphic_readout",
    "oracle_boundary",
]
ROLE_CODES = {name: index for index, name in enumerate(ROLE_NAMES)}

INPUT_NAMES = list(INPUTS)
INPUT_CODES = {name: index for index, name in enumerate(INPUT_NAMES)}

GAP_NAMES = [
    "smooth_four_dimensional_lorentzian_limit",
    "tensorial_metric_and_connection_from_a985",
    "physical_stress_energy_tensor_from_finite_stress",
    "einstein_tensor_and_bianchi_identity",
    "einstein_field_equation_normalization",
    "geodesic_motion_and_equivalence_principle",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "surface_count",
    "certified_surface_count",
    "a985_chain_surface_count",
    "finite_surface_count",
    "continuum_surface_count",
    "gr_derivation_surface_count",
    "open_gr_gap_count",
    "required_gr_gap_count",
    "certified_gr_gap_count",
    "next_gap_code",
    "pathway_certified_flag",
    "a985_alone_gr_derivation_complete_flag",
    "continuum_gr_claim_flag",
    "physical_stress_energy_certified_flag",
    "long_gate_required_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _status_ok(report: dict[str, Any], expected_status: str, *, core: bool = False) -> int:
    if report.get("status") != expected_status:
        return 0
    if core:
        return 1
    return int(report.get("all_checks_pass") is True)


def _load_inputs() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, (path, _) in INPUTS.items()}


def build_rows() -> dict[str, Any]:
    reports = _load_inputs()
    input_ok = {
        name: _status_ok(report, expected, core=(name == "core_a985"))
        for name, report in reports.items()
        for _, expected in [INPUTS[name]]
    }

    surface_rows: list[dict[str, int]] = [
        {
            "surface_id": SURFACE_CODES["a985_core_seed"],
            "role_code": ROLE_CODES["source_seed"],
            "input_code": INPUT_CODES["core_a985"],
            "certified_flag": input_ok["core_a985"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 0,
        },
        {
            "surface_id": SURFACE_CODES["c985_finite_multifusion_category"],
            "role_code": ROLE_CODES["finite_category"],
            "input_code": INPUT_CODES["c985_final"],
            "certified_flag": input_ok["c985_final"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 0,
        },
        {
            "surface_id": SURFACE_CODES["d20_boundary_atlas"],
            "role_code": ROLE_CODES["finite_boundary_geometry"],
            "input_code": INPUT_CODES["d20_atlas"],
            "certified_flag": input_ok["d20_atlas"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 1,
        },
        {
            "surface_id": SURFACE_CODES["hyperbolic_boundary_graph"],
            "role_code": ROLE_CODES["finite_metric_readout"],
            "input_code": INPUT_CODES["hyperbolic_graph"],
            "certified_flag": input_ok["hyperbolic_graph"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 2,
        },
        {
            "surface_id": SURFACE_CODES["poincare_disk_readout"],
            "role_code": ROLE_CODES["finite_metric_readout"],
            "input_code": INPUT_CODES["poincare"],
            "certified_flag": input_ok["poincare"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 2,
        },
        {
            "surface_id": SURFACE_CODES["boundary_stress_graph"],
            "role_code": ROLE_CODES["finite_stress_flux_readout"],
            "input_code": INPUT_CODES["stress_graph"],
            "certified_flag": input_ok["stress_graph"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 1,
        },
        {
            "surface_id": SURFACE_CODES["finite_anomaly_ward_bms_surface"],
            "role_code": ROLE_CODES["finite_symmetry_anomaly_readout"],
            "input_code": INPUT_CODES["long_anom"],
            "certified_flag": input_ok["long_anom"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 1,
        },
        {
            "surface_id": SURFACE_CODES["finite_matrix_charge_wall_surface"],
            "role_code": ROLE_CODES["finite_matrix_dynamics_readout"],
            "input_code": INPUT_CODES["long_mat"],
            "certified_flag": input_ok["long_mat"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 1,
        },
        {
            "surface_id": SURFACE_CODES["finite_automorphic_fourier_surface"],
            "role_code": ROLE_CODES["finite_automorphic_readout"],
            "input_code": INPUT_CODES["long_auto"],
            "certified_flag": input_ok["long_auto"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 1,
        },
        {
            "surface_id": SURFACE_CODES["oracle_status_split"],
            "role_code": ROLE_CODES["oracle_boundary"],
            "input_code": INPUT_CODES["long_orac"],
            "certified_flag": input_ok["long_orac"],
            "a985_chain_flag": 1,
            "finite_flag": 1,
            "continuum_flag": 0,
            "gr_derivation_flag": 0,
            "open_gap_count": 6,
        },
    ]

    gap_rows: list[dict[str, int]] = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["smooth_four_dimensional_lorentzian_limit"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "blocked_by_finite_scope_flag": 1,
            "next_flag": 1,
            "dependency_surface_code": SURFACE_CODES["poincare_disk_readout"],
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES["tensorial_metric_and_connection_from_a985"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "blocked_by_finite_scope_flag": 1,
            "next_flag": 0,
            "dependency_surface_code": SURFACE_CODES["hyperbolic_boundary_graph"],
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["physical_stress_energy_tensor_from_finite_stress"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "blocked_by_finite_scope_flag": 1,
            "next_flag": 0,
            "dependency_surface_code": SURFACE_CODES["boundary_stress_graph"],
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["einstein_tensor_and_bianchi_identity"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "blocked_by_finite_scope_flag": 1,
            "next_flag": 0,
            "dependency_surface_code": SURFACE_CODES["finite_anomaly_ward_bms_surface"],
        },
        {
            "gap_id": 4,
            "obligation_code": GAP_CODES["einstein_field_equation_normalization"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "blocked_by_finite_scope_flag": 1,
            "next_flag": 0,
            "dependency_surface_code": SURFACE_CODES["finite_matrix_charge_wall_surface"],
        },
        {
            "gap_id": 5,
            "obligation_code": GAP_CODES["geodesic_motion_and_equivalence_principle"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "blocked_by_finite_scope_flag": 1,
            "next_flag": 0,
            "dependency_surface_code": SURFACE_CODES["oracle_status_split"],
        },
    ]

    obs = {
        "input_report_count": len(INPUTS),
        "input_certified_count": sum(input_ok.values()),
        "surface_count": len(surface_rows),
        "certified_surface_count": sum(row["certified_flag"] for row in surface_rows),
        "a985_chain_surface_count": sum(row["a985_chain_flag"] for row in surface_rows),
        "finite_surface_count": sum(row["finite_flag"] for row in surface_rows),
        "continuum_surface_count": sum(row["continuum_flag"] for row in surface_rows),
        "gr_derivation_surface_count": sum(row["gr_derivation_flag"] for row in surface_rows),
        "open_gr_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "required_gr_gap_count": sum(row["required_for_gr_flag"] for row in gap_rows),
        "certified_gr_gap_count": sum(row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES["smooth_four_dimensional_lorentzian_limit"],
        "pathway_certified_flag": 1,
        "a985_alone_gr_derivation_complete_flag": 0,
        "continuum_gr_claim_flag": 0,
        "physical_stress_energy_certified_flag": 0,
        "long_gate_required_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]

    surface_table = table_from_rows(SURFACE_COLUMNS, surface_rows)
    gap_table = table_from_rows(GAP_COLUMNS, gap_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)

    return {
        "reports": reports,
        "input_ok": input_ok,
        "surface_rows": surface_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "surface_table": surface_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "surface_text_hash": sha_text(digest_text(SURFACE_COLUMNS, surface_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"] == obs["input_report_count"],
        "surface_shape_exact": obs["surface_count"] == len(SURFACE_NAMES),
        "gap_shape_exact": obs["open_gr_gap_count"] == len(GAP_NAMES),
        "a985_chain_recorded": obs["a985_chain_surface_count"] == obs["surface_count"],
        "finite_scope_recorded": obs["finite_surface_count"] == obs["surface_count"],
        "continuum_not_claimed": obs["continuum_surface_count"] == 0
        and obs["continuum_gr_claim_flag"] == 0,
        "gr_derivation_not_claimed": obs["gr_derivation_surface_count"] == 0
        and obs["a985_alone_gr_derivation_complete_flag"] == 0,
        "physical_stress_energy_not_claimed": obs["physical_stress_energy_certified_flag"] == 0,
        "next_gap_selected": obs["next_gap_code"] == GAP_CODES["smooth_four_dimensional_lorentzian_limit"],
        "table_shapes_match": rows["surface_table"].shape == (len(SURFACE_NAMES), len(SURFACE_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "a985_to_general_relativity_derivation_pathway",
        "role_code_map": {str(value): key for key, value in ROLE_CODES.items()},
        "input_code_map": {str(value): key for key, value in INPUT_CODES.items()},
        "surface_code_map": {str(value): key for key, value in SURFACE_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "summary": {
            "input_certified_count": obs["input_certified_count"],
            "surface_count": obs["surface_count"],
            "certified_surface_count": obs["certified_surface_count"],
            "open_gr_gap_count": obs["open_gr_gap_count"],
            "next_gap": "smooth_four_dimensional_lorentzian_limit",
            "a985_alone_gr_derivation_complete_flag": obs[
                "a985_alone_gr_derivation_complete_flag"
            ],
            "continuum_gr_claim_flag": obs["continuum_gr_claim_flag"],
            "pathway_certified_flag": obs["pathway_certified_flag"],
        },
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "surface_text_sha256": rows["surface_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    pathway_payload = {
        "schema": "long.gr.pathway@1",
        "object": "a985_to_general_relativity_pathway",
        "status": STATUS if all(checks.values()) else "LONG_GR_PATHWAY_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.gr.report@1",
        "status": pathway_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_gr certifies a pathway, not a derivation: A985-rooted finite "
            "certificate surfaces currently provide the source seed, finite "
            "C985 category, d20 boundary geometry, hyperbolic/Poincare metric "
            "readouts, finite stress/flux/Ward/BMS/anomaly, finite matrix, "
            "finite automorphic/Fourier, and oracle boundary inputs needed to "
            "start a first general-relativity derivation attempt. The required "
            "continuum Lorentzian, tensorial stress-energy, Einstein tensor, "
            "field-equation, and geodesic/equivalence-principle steps remain "
            "explicit open obligations."
        ),
        "stage_protocol": {
            "draft": "read A985, finite C985, d20 metric/stress, anomaly, matrix, automorphic, and oracle reports",
            "witness": "emit certified finite-surface rows and open GR-obligation rows",
            "coherence": "check statuses, row counts, finite/continuum flags, table shapes, and hashes",
            "closure": "certify the A985-to-GR pathway boundary without claiming GR is derived",
            "emit": "write long_gr artifacts and verifier hook",
        },
        "inputs": {
            key: input_entry(
                path,
                {
                    "status": rows["reports"][key].get("status"),
                    "certificate_sha256": rows["reports"][key].get("certificate_sha256"),
                },
            )
            for key, (path, _) in INPUTS.items()
        }
        | {
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "pathway": relpath(OUT_DIR / "pathway.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
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
                "an A985-rooted finite input chain for attempting a first GR derivation",
                "the finite surfaces available today: C985, d20 boundary geometry, hyperbolic/Poincare readouts, stress/flux guardrails, finite Ward/BMS/anomaly, finite matrix, finite automorphic/Fourier, and oracle status split",
                "six explicit open GR bridge obligations, with the smooth four-dimensional Lorentzian limit selected as the next focused seam",
            ],
            "does_not_certify_because_open": [
                "general relativity derived from A985 alone",
                "a smooth four-dimensional Lorentzian manifold or continuum limit",
                "a tensorial metric, Levi-Civita connection, Riemann/Ricci curvature, or Einstein tensor",
                "a physical stress-energy tensor from the finite stress graph",
                "Einstein field equations or their normalization constants",
                "geodesic motion or the equivalence principle from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Build long_lor: certify an A985-rooted Lorentzian continuum-limit "
            "candidate or obstruction from the hyperbolic/Poincare/stress "
            "surfaces before attempting an Einstein-equation certificate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.gr.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.gr.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "pathway": pathway_payload,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
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
    write_json(OUT_DIR / "pathway.json", payloads["pathway"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
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
