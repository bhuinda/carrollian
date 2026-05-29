from __future__ import annotations

import hashlib
import json
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


THEOREM_ID = "long_h16"
STATUS = "LONG_H16_BOUNDARY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

REPORTS = {
    "long_tens": PROOF_ROOT / "long_tens" / "report.json",
    "long_lift": PROOF_ROOT / "long_lift" / "report.json",
    "long_raw": PROOF_ROOT / "long_raw" / "report.json",
    "long_path": PROOF_ROOT / "long_path" / "report.json",
    "long_measure": PROOF_ROOT / "long_measure" / "report.json",
    "long_comp": PROOF_ROOT / "long_comp" / "report.json",
    "long_all": PROOF_ROOT / "long_all" / "report.json",
    "long_linf": PROOF_ROOT / "long_linf" / "report.json",
    "long_ind": PROOF_ROOT / "long_ind" / "report.json",
    "long_suppind": PROOF_ROOT / "long_suppind" / "report.json",
    "long_recind": PROOF_ROOT / "long_recind" / "report.json",
    "long_formind": PROOF_ROOT / "long_formind" / "report.json",
    "long_domind": PROOF_ROOT / "long_domind" / "report.json",
    "long_gapind": PROOF_ROOT / "long_gapind" / "report.json",
}

DERIVE_SCRIPT = ROOT / "src" / "derive_long_h16.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_h16.py"

SURFACE_TEXT_HASH = "53ecdb5f1687f30ee304b5d1d76fb2925713248e9af1fd6626ac28dd9ed33bc5"
OBS_TEXT_HASH = "73dbe44638b170fcef9065a73055043cec4230fa898b37acb2899e9b91acf9d6"

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "input_certified_flag",
    "resolved_flag",
    "open_boundary_flag",
    "materialized_flag",
    "positive_witness_flag",
    "next_action_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "surface_row_count",
    "resolved_surface_count",
    "open_boundary_count",
    "h16_sum_state_count",
    "h16_gap_sum_state_count",
    "component_path_total",
    "active_owner_count",
    "owner_cell_count",
    "raw_tensor_support_count",
    "raw_tensor_coeff_sum",
    "raw_support_lift_positive_count",
    "raw_coeff_lift_positive_count",
    "sample_path_count",
    "sample_gap_path_count",
    "exact_composable_path_count",
    "zeta_composable_path_count",
    "scoped_measure_law_flag",
    "full_raw_measure_certified_flag",
    "full_raw_scope_gap_flag",
    "full_raw_oriented_sheaf_flag",
    "full_raw_positive_zeta_sheaf_flag",
    "reverse_section_count",
    "global_gap_check_count",
    "global_gap_nonnegative_count",
    "materialized_h16_profunctor_flag",
    "current_model_obstruction_flag",
    "active_h16_frontier_flag",
    "boundary_decision_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(report: dict[str, Any]) -> int:
    status = str(report.get("status", ""))
    return int(
        report.get("all_checks_pass") is True
        and "FAIL" not in status
        and "PROVISIONAL" not in status
    )


def load_reports() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, path in REPORTS.items()}


def build_rows() -> dict[str, Any]:
    reports = load_reports()
    tens = reports["long_tens"]["witness"]
    lift = reports["long_lift"]["witness"]
    raw = reports["long_raw"]["witness"]
    path = reports["long_path"]["witness"]
    measure = reports["long_measure"]["witness"]
    comp = reports["long_comp"]["witness"]
    all_raw = reports["long_all"]["witness"]
    gapind = reports["long_gapind"]["witness"]["gap_induction"]

    input_certified_count = sum(certified(report) for report in reports.values())
    induction_names = [
        "long_linf",
        "long_ind",
        "long_suppind",
        "long_recind",
        "long_formind",
        "long_domind",
        "long_gapind",
    ]
    induction_ok = int(all(certified(reports[name]) for name in induction_names))
    h16_profunctor_materialized = int(
        tens["current_representation"]["current_horizon16_sum_profunctor_flag"] == 1
        or lift["current_representation"]["current_materialized_owner_path_flag"] == 1
        or lift["current_representation"]["current_materialized_owner_cell_path_flag"] == 1
        or lift["current_representation"]["current_raw_line_address_lift_flag"] == 1
        or raw["current_representation"]["current_materialized_raw_path_flag"] == 1
        or path["current_representation"]["current_composable_raw_address_path_flag"] == 1
    )
    raw_backed_compressed = int(
        raw["current_representation"]["current_compressed_raw_lift_flag"] == 1
        and raw["current_representation"]["current_markov_only_quotient_flag"] == 0
        and raw["fibers"]["raw_support_lift_positive_count"] == 288
        and raw["fibers"]["raw_coeff_lift_positive_count"] == 288
    )
    sample_path_ok = int(
        path["current_representation"]["current_explicit_raw_product_path_flag"] == 1
        and path["current_representation"]["current_single_witness_per_fiber_flag"] == 1
        and path["paths"]["path_row_count"] == 288
        and path["paths"]["gap_witness_count"] == 208
    )
    comp_ok = int(
        comp["current_representation"]["current_alexandrov_zeta_composable_path_flag"]
        == 1
        and comp["current_representation"]["current_exact_source_target_composable_path_flag"]
        == 0
        and comp["zeta_composability"]["zeta_path_count"] == 288
        and comp["exact_composability"]["exact_path_count"] == 0
    )
    all_raw_ok = int(
        all_raw["current_representation"]["current_oriented_full_raw_sheaf_flag"] == 1
        and all_raw["current_representation"]["current_positive_zeta_full_raw_sheaf_flag"]
        == 0
        and all_raw["lln_moments"]["raw_section_count"] == 1_414_965
    )
    gapind_ok = int(
        induction_ok
        and gapind["finite_gap_check_count"]
        == gapind["finite_gap_nonnegative_count"]
        == 131_586
    )
    measure_summary = measure["summary"]
    measure_ok = int(
        certified(reports["long_measure"]) == 1
        and measure_summary["scoped_probability_law_flag"] == 1
        and measure_summary["full_raw_measure_certified_flag"] == 0
        and measure_summary["full_raw_scope_gap_flag"] == 1
    )
    current_model_obstruction = int(
        h16_profunctor_materialized == 0
        and raw_backed_compressed == 1
        and sample_path_ok == 1
        and comp_ok == 1
        and measure_ok == 1
        and all_raw_ok == 1
    )

    surface_rows = [
        {
            "surface_id": 0,
            "surface_code": 0,
            "input_certified_flag": certified(reports["long_tens"]),
            "resolved_flag": certified(reports["long_tens"]),
            "open_boundary_flag": 1,
            "materialized_flag": int(
                tens["current_representation"]["current_horizon16_sum_profunctor_flag"]
            ),
            "positive_witness_flag": int(tens["horizons"]["fiber_total_matches_paths_flag"]),
            "next_action_code": 0,
        },
        {
            "surface_id": 1,
            "surface_code": 1,
            "input_certified_flag": certified(reports["long_lift"]),
            "resolved_flag": certified(reports["long_lift"]),
            "open_boundary_flag": 1,
            "materialized_flag": int(
                lift["current_representation"]["current_materialized_owner_cell_path_flag"]
            ),
            "positive_witness_flag": int(
                lift["fibers"]["owner_cell_lift_positive_count"] == 288
            ),
            "next_action_code": 1,
        },
        {
            "surface_id": 2,
            "surface_code": 2,
            "input_certified_flag": certified(reports["long_raw"]),
            "resolved_flag": raw_backed_compressed,
            "open_boundary_flag": 1,
            "materialized_flag": int(
                raw["current_representation"]["current_materialized_raw_path_flag"]
            ),
            "positive_witness_flag": raw_backed_compressed,
            "next_action_code": 2,
        },
        {
            "surface_id": 3,
            "surface_code": 3,
            "input_certified_flag": certified(reports["long_path"]),
            "resolved_flag": sample_path_ok,
            "open_boundary_flag": 1,
            "materialized_flag": int(
                path["current_representation"]["current_explicit_raw_product_path_flag"]
            ),
            "positive_witness_flag": sample_path_ok,
            "next_action_code": 3,
        },
        {
            "surface_id": 4,
            "surface_code": 4,
            "input_certified_flag": certified(reports["long_comp"]),
            "resolved_flag": comp_ok,
            "open_boundary_flag": 1,
            "materialized_flag": int(
                comp["current_representation"]["current_alexandrov_zeta_composable_path_flag"]
            ),
            "positive_witness_flag": comp_ok,
            "next_action_code": 4,
        },
        {
            "surface_id": 5,
            "surface_code": 5,
            "input_certified_flag": certified(reports["long_all"]),
            "resolved_flag": all_raw_ok,
            "open_boundary_flag": 1,
            "materialized_flag": int(
                all_raw["current_representation"]["current_oriented_full_raw_sheaf_flag"]
            ),
            "positive_witness_flag": all_raw_ok,
            "next_action_code": 5,
        },
        {
            "surface_id": 6,
            "surface_code": 6,
            "input_certified_flag": induction_ok,
            "resolved_flag": gapind_ok,
            "open_boundary_flag": 0,
            "materialized_flag": 1,
            "positive_witness_flag": gapind_ok,
            "next_action_code": 6,
        },
        {
            "surface_id": 7,
            "surface_code": 7,
            "input_certified_flag": input_certified_count == len(reports),
            "resolved_flag": int(
                raw_backed_compressed == 1
                and sample_path_ok == 1
                and comp_ok == 1
                and h16_profunctor_materialized == 0
            ),
            "open_boundary_flag": 1,
            "materialized_flag": h16_profunctor_materialized,
            "positive_witness_flag": 0,
            "next_action_code": 7,
        },
        {
            "surface_id": 8,
            "surface_code": 8,
            "input_certified_flag": certified(reports["long_measure"]),
            "resolved_flag": measure_ok,
            "open_boundary_flag": 0,
            "materialized_flag": 0,
            "positive_witness_flag": measure_ok,
            "next_action_code": 8,
        },
    ]
    obs = {
        "input_report_count": len(reports),
        "input_certified_count": input_certified_count,
        "surface_row_count": len(surface_rows),
        "resolved_surface_count": sum(row["resolved_flag"] for row in surface_rows),
        "open_boundary_count": sum(row["open_boundary_flag"] for row in surface_rows),
        "h16_sum_state_count": int(tens["horizons"]["total_sum_state_count"]),
        "h16_gap_sum_state_count": int(tens["fibers"]["gap_sum_state_count"]),
        "component_path_total": int(tens["horizons"]["total_component_path_count"]),
        "active_owner_count": int(lift["components"]["active_owner_total"]),
        "owner_cell_count": int(lift["components"]["owner_cell_total"]),
        "raw_tensor_support_count": int(raw["raw_owner_assignment"]["raw_tensor_support_count"]),
        "raw_tensor_coeff_sum": int(raw["raw_owner_assignment"]["raw_tensor_coeff_sum"]),
        "raw_support_lift_positive_count": int(
            raw["fibers"]["raw_support_lift_positive_count"]
        ),
        "raw_coeff_lift_positive_count": int(
            raw["fibers"]["raw_coeff_lift_positive_count"]
        ),
        "sample_path_count": int(path["paths"]["path_row_count"]),
        "sample_gap_path_count": int(path["paths"]["gap_path_count"]),
        "exact_composable_path_count": int(comp["exact_composability"]["exact_path_count"]),
        "zeta_composable_path_count": int(comp["zeta_composability"]["zeta_path_count"]),
        "scoped_measure_law_flag": int(measure_summary["scoped_probability_law_flag"]),
        "full_raw_measure_certified_flag": int(
            measure_summary["full_raw_measure_certified_flag"]
        ),
        "full_raw_scope_gap_flag": int(measure_summary["full_raw_scope_gap_flag"]),
        "full_raw_oriented_sheaf_flag": int(
            all_raw["current_representation"]["current_oriented_full_raw_sheaf_flag"]
        ),
        "full_raw_positive_zeta_sheaf_flag": int(
            all_raw["current_representation"]["current_positive_zeta_full_raw_sheaf_flag"]
        ),
        "reverse_section_count": int(all_raw["orientation_split"]["reverse_section_count"]),
        "global_gap_check_count": int(gapind["finite_gap_check_count"]),
        "global_gap_nonnegative_count": int(gapind["finite_gap_nonnegative_count"]),
        "materialized_h16_profunctor_flag": h16_profunctor_materialized,
        "current_model_obstruction_flag": current_model_obstruction,
        "active_h16_frontier_flag": 1 - current_model_obstruction,
        "boundary_decision_code": 3,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    surface_hash = hashlib.sha256(
        digest_text(SURFACE_COLUMNS, surface_rows).encode("ascii")
    ).hexdigest()
    obs_hash = hashlib.sha256(
        digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
    ).hexdigest()
    return {
        "reports": reports,
        "surface_rows": surface_rows,
        "obs_rows": obs_rows,
        "surface_table": table_from_rows(SURFACE_COLUMNS, surface_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "surface_hash": surface_hash,
        "obs_hash": obs_hash,
        "obs": obs,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"] == obs["input_report_count"] == 14,
        "h16_quotient_exact": (
            obs["h16_sum_state_count"],
            obs["h16_gap_sum_state_count"],
            obs["component_path_total"],
        )
        == (288, 208, 64_570_080),
        "raw_lift_exact": (
            obs["active_owner_count"],
            obs["owner_cell_count"],
            obs["raw_tensor_support_count"],
            obs["raw_tensor_coeff_sum"],
            obs["raw_support_lift_positive_count"],
            obs["raw_coeff_lift_positive_count"],
        )
        == (51, 749_239, 1_414_965, 2_537_360, 288, 288),
        "sample_composability_boundary_exact": (
            obs["sample_path_count"],
            obs["sample_gap_path_count"],
            obs["exact_composable_path_count"],
            obs["zeta_composable_path_count"],
        )
        == (288, 208, 0, 288),
        "scoped_measure_boundary_exact": (
            obs["scoped_measure_law_flag"],
            obs["full_raw_measure_certified_flag"],
            obs["full_raw_scope_gap_flag"],
        )
        == (1, 0, 1),
        "full_raw_sheaf_boundary_exact": (
            obs["full_raw_oriented_sheaf_flag"],
            obs["full_raw_positive_zeta_sheaf_flag"],
            obs["reverse_section_count"],
        )
        == (1, 0, 937_376),
        "global_gap_induction_exact": (
            obs["global_gap_check_count"],
            obs["global_gap_nonnegative_count"],
        )
        == (131_586, 131_586),
        "h16_profunctor_boundary_exact": (
            obs["materialized_h16_profunctor_flag"],
            obs["current_model_obstruction_flag"],
            obs["active_h16_frontier_flag"],
            obs["boundary_decision_code"],
            obs["resolved_surface_count"],
            obs["open_boundary_count"],
        )
        == (0, 1, 0, 3, 9, 7),
        "fingerprints_exact": (
            rows["surface_hash"] == SURFACE_TEXT_HASH
            and rows["obs_hash"] == OBS_TEXT_HASH
        ),
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == ((9, len(SURFACE_COLUMNS)), (len(OBS_CODES), len(OBS_COLUMNS))),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "horizon16_profunctor_boundary",
        "summary": {
            "input_report_count": obs["input_report_count"],
            "input_certified_count": obs["input_certified_count"],
            "resolved_surface_count": obs["resolved_surface_count"],
            "open_boundary_count": obs["open_boundary_count"],
            "materialized_h16_profunctor_flag": obs[
                "materialized_h16_profunctor_flag"
            ],
            "current_model_obstruction_flag": obs["current_model_obstruction_flag"],
            "active_h16_frontier_flag": obs["active_h16_frontier_flag"],
            "boundary_decision_code": obs["boundary_decision_code"],
        },
        "surface_code_map": {
            "0": "horizon16_sum_quotient",
            "1": "owner_component_lift",
            "2": "raw_owner_support_lift",
            "3": "single_raw_product_path_witness",
            "4": "alexandrov_zeta_sample_composability",
            "5": "full_raw_oriented_interval_sheaf",
            "6": "global_symbolic_gap_induction",
            "7": "genuine_horizon16_profunctor_boundary",
            "8": "scoped_active_product_measure_boundary",
        },
        "next_action_code_map": {
            "0": "do not equate the sum quotient with a profunctor without a materialized path object",
            "1": "materialize owner-cell paths before claiming an owner-level profunctor",
            "2": "materialize raw address paths before claiming raw-line horizon-16 profunctoriality",
            "3": "upgrade single witnesses to exhaustive raw path families if long_paths is targeted",
            "4": "exact source/target composability remains absent; keep claims at zeta-composable sample level",
            "5": "orientation is required for the full raw sheaf; positive-zeta full sheaf is obstructed",
            "6": "symbolic gap induction is certified and can be used as the finite-line support oracle",
            "7": "current artifacts do not materialize a genuine horizon-16 profunctor",
            "8": "use the scoped active-product measure boundary without upgrading it to full raw-support measure",
        },
        "horizon16": {
            "sum_state_count": obs["h16_sum_state_count"],
            "gap_sum_state_count": obs["h16_gap_sum_state_count"],
            "component_path_total": obs["component_path_total"],
            "raw_support_count": obs["raw_tensor_support_count"],
            "raw_coeff_sum": obs["raw_tensor_coeff_sum"],
            "sample_path_count": obs["sample_path_count"],
            "zeta_composable_path_count": obs["zeta_composable_path_count"],
            "exact_composable_path_count": obs["exact_composable_path_count"],
            "current_model_obstruction_flag": obs["current_model_obstruction_flag"],
        },
        "surface_text_sha256": rows["surface_hash"],
        "observable_text_sha256": rows["obs_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    h16_payload = {
        "schema": "long.h16@1",
        "object": "horizon16_profunctor_boundary",
        "status": STATUS if all(checks.values()) else "LONG_H16_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.h16.report@1",
        "status": h16_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_h16 certifies the current horizon-16 profunctor boundary and "
            "current-model obstruction: "
            "the extension is raw-backed and has one explicit raw product-path "
            "witness for every sum-state fiber, with Alexandrov-zeta sample "
            "composability, scoped active-product measure laws, and global "
            "support-gap induction, while the current artifact boundary has no "
            "materialized owner-path, raw-address-path, exact-composable sample "
            "path, or genuine long_prof horizon-16 profunctor."
        ),
        "stage_protocol": {
            "draft": "read horizon-16 quotient, lift, raw, path, composability, full sheaf, and induction reports",
            "witness": "emit horizon-16 status rows and observable counts",
            "coherence": "check statuses, counts, representation flags, hashes, and table shapes",
            "closure": "certify the current h16 boundary and current-model obstruction without claiming absolute nonexistence",
            "emit": "write long_h16 artifacts and verifier hook",
        },
        "inputs": {
            **{
                name: input_entry(
                    path,
                    {
                        "status": rows["reports"][name].get("status"),
                        "certificate_sha256": rows["reports"][name].get(
                            "certificate_sha256"
                        ),
                    },
                )
                for name, path in REPORTS.items()
            },
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "h16": relpath(OUT_DIR / "h16.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
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
                "horizon-16 is raw-backed at the compressed owner/support quotient",
                "one explicit raw product-path witness exists for every horizon-16 sum-state fiber",
                "the sample witnesses are Alexandrov-zeta composable but not exact source/target composable",
                "the scoped active-product measure boundary preserves the full raw-support gap",
                "the full raw tensor support has an oriented interval sheaf, not a positive-zeta sheaf",
                "global support-gap induction is available as the finite-line support oracle",
                "no materialized genuine long_prof horizon-16 profunctor exists in the current artifact boundary",
                "the current-model h16 active frontier is closed as an obstruction under the certified artifact constraints",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence under a changed object/support model",
                "all raw product paths in each fiber",
                "a materialized owner-cell or raw-address horizon-16 path object",
                "a probability measure on the full raw tensor support independent of the current active-product boundary",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_inv_exhaust: prove or bound the invariant-family "
            "inventory cover for the finite-line address space."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.h16.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.h16.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "h16": h16_payload,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "surface_text_sha256": rows["surface_hash"],
            "obs_text_sha256": rows["obs_hash"],
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
    write_json(OUT_DIR / "h16.json", payloads["h16"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
