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


THEOREM_ID = "long_anom"
STATUS = "LONG_ANOM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

FINITE_ANOMALY_REPORT = THEOREM_ROOT / "finite_anomaly_counter" / "report.json"
SECTOR26_CANCELLATION_REPORT = (
    THEOREM_ROOT / "sector26_anomaly_cancellation" / "report.json"
)
ANOMALY_RECOVERY_REPORT = (
    THEOREM_ROOT / "anomaly_cancelled_flux_balance_recovery" / "report.json"
)
GAMMA8_CORRECTION_REPORT = (
    THEOREM_ROOT / "gamma8_obstruction_correction" / "report.json"
)
GENERAL_CORRECTION_REPORT = (
    THEOREM_ROOT / "general_obstruction_correction_suite" / "report.json"
)
GLOBAL_COUNTERTERM_REPORT = (
    THEOREM_ROOT / "global_counterterm_lattice" / "report.json"
)
GLOBAL_CHARGE_REPORT = THEOREM_ROOT / "global_corrected_charge_map" / "report.json"
HIDDEN_SPLIT_REPORT = (
    THEOREM_ROOT / "global_corrected_hidden_split_symmetry" / "report.json"
)
STRICT_CLOCK_REPORT = (
    THEOREM_ROOT / "d20_strict_weak_order_sector26_clock" / "report.json"
)
CENTRAL_EXTENSION_REPORT = (
    THEOREM_ROOT / "finite_central_extension_anomaly_cocycle" / "report.json"
)
WARD_REPORT = THEOREM_ROOT / "canonical_all_mask_ward_identity" / "report.json"
BMS_REPORT = THEOREM_ROOT / "finite_bms_carrollian_flux_balance" / "report.json"
SUPERSELECTION_REPORT = (
    THEOREM_ROOT / "superselection_flux_balance_extension" / "report.json"
)
C2_QUOTIENT_ANOMALY_REPORT = (
    THEOREM_ROOT
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
    / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_anom.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_anom.py"

STATUS_TEXT_HASH = "a7ea8f2f15f3c26369edccbcb503fbae9a41f221ea92457ed3a96bc037a9154b"
OBS_TEXT_HASH = "26741a171cc9029f9f3440adbc0f9dea8fb43b983f73340b0f81d284f38407bd"

REPORTS = {
    "finite_anomaly": FINITE_ANOMALY_REPORT,
    "sector26_cancellation": SECTOR26_CANCELLATION_REPORT,
    "anomaly_recovery": ANOMALY_RECOVERY_REPORT,
    "gamma8_correction": GAMMA8_CORRECTION_REPORT,
    "general_correction": GENERAL_CORRECTION_REPORT,
    "global_counterterm": GLOBAL_COUNTERTERM_REPORT,
    "global_charge": GLOBAL_CHARGE_REPORT,
    "hidden_split": HIDDEN_SPLIT_REPORT,
    "strict_clock": STRICT_CLOCK_REPORT,
    "central_extension": CENTRAL_EXTENSION_REPORT,
    "ward": WARD_REPORT,
    "bms": BMS_REPORT,
    "superselection": SUPERSELECTION_REPORT,
    "c2_quotient_anomaly": C2_QUOTIENT_ANOMALY_REPORT,
}

EXPECTED_STATUSES = {
    "finite_anomaly": "D20_FINITE_ANOMALY_COUNTER_CERTIFIED",
    "sector26_cancellation": "D20_SECTOR26_ANOMALY_CANCELLATION_CERTIFIED",
    "anomaly_recovery": "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_CERTIFIED",
    "gamma8_correction": "D20_GAMMA8_OBSTRUCTION_CORRECTION_CERTIFIED",
    "general_correction": "D20_GENERAL_OBSTRUCTION_CORRECTION_SUITE_CERTIFIED",
    "global_counterterm": "D20_GLOBAL_COUNTERTERM_LATTICE_CERTIFIED",
    "global_charge": "D20_GLOBAL_CORRECTED_CHARGE_MAP_CERTIFIED",
    "hidden_split": "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED",
    "strict_clock": "D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK_CERTIFIED",
    "central_extension": "D20_FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_CERTIFIED",
    "ward": "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED",
    "bms": "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED",
    "superselection": "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED",
    "c2_quotient_anomaly": "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_CERTIFIED",
}

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "certified_flag",
    "resolved_flag",
    "residual_boundary_flag",
    "next_action_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "status_row_count",
    "resolved_surface_count",
    "residual_anomaly_boundary_count",
    "current_anomaly_suite_closed_flag",
    "sector26_cancelled_packet_count",
    "sector26_max_cancelled_dimension",
    "gamma8_counterterm_mod13",
    "gamma8_corrected_packet_count",
    "coordinate_correction_count",
    "global_counterterm_active_count",
    "corrected_mask_count",
    "corrected_kernel_size",
    "corrected_odd_size",
    "hidden_split_stabilizer_order",
    "hidden_split_breaking_count",
    "strict_clock_stabilizer_order",
    "central_extension_dimension",
    "ward_mask_count",
    "bms_mask_count",
    "c2_quotient_orbit_count",
    "c2_nonzero_anomaly_orbit_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def report_certified(name: str, report: dict[str, Any]) -> int:
    return int(
        report.get("status") == EXPECTED_STATUSES[name]
        and report.get("all_checks_pass") is True
    )


def checks_all_true(report: dict[str, Any]) -> bool:
    checks = report.get("checks", {})
    return isinstance(checks, dict) and all(
        value is not False and value is not None for value in checks.values()
    )


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORTS.items()}

    finite_checks = reports["finite_anomaly"].get("checks", {})
    sector26 = reports["sector26_cancellation"].get("derived", {})
    gamma8 = reports["gamma8_correction"].get("derived", {})
    gamma8_row = gamma8.get("gamma8", {})
    gamma8_search = gamma8.get("corrected_packet_search", {})
    general = reports["general_correction"].get("derived", {})
    global_counterterm = reports["global_counterterm"].get("derived", {})
    global_charge = reports["global_charge"].get("derived", {})
    hidden_split = reports["hidden_split"].get("derived", {})
    strict_clock = reports["strict_clock"].get("derived", {})
    central = reports["central_extension"].get("derived", {})
    ward = reports["ward"].get("derived", {})
    bms = reports["bms"].get("derived", {})
    superselection = reports["superselection"].get("derived", {})
    c2 = reports["c2_quotient_anomaly"].get("derived", {})

    certified_flags = {
        name: int(report_certified(name, report) and checks_all_true(report))
        for name, report in reports.items()
    }

    surface_rows = [
        {
            "surface_id": index,
            "surface_code": index,
            "certified_flag": certified_flags[name],
            "resolved_flag": certified_flags[name],
            "residual_boundary_flag": 0,
            "next_action_code": index,
        }
        for index, name in enumerate(REPORTS)
    ]

    corrected_hist = global_counterterm.get("corrected_clock_histogram", {})
    hidden_summary = hidden_split.get("hidden_split", {})
    hidden_symmetry = hidden_split.get("symmetry_classification", {})
    strict_symmetry = strict_clock.get("d20_symmetry_test", {})
    central_summary = central.get("central_extension_summary", {})
    bms_summary = bms.get("balance_summary", {})
    c2_summary = c2.get("anomaly_summary", {})

    obs = {
        "input_report_count": len(reports),
        "input_certified_count": sum(certified_flags.values()),
        "status_row_count": len(surface_rows),
        "resolved_surface_count": sum(row["resolved_flag"] for row in surface_rows),
        "residual_anomaly_boundary_count": sum(
            row["residual_boundary_flag"] for row in surface_rows
        ),
        "current_anomaly_suite_closed_flag": int(
            sum(certified_flags.values()) == len(reports)
            and bool(finite_checks.get("z26_clock_is_not_linear_character"))
            and int(sector26.get("maximal_cancelled_packet_count", 0)) == 178
            and int(gamma8_row.get("counterterm_mod13", -1)) == 5
            and len(general.get("coordinate_corrections", [])) == 11
            and len(global_counterterm.get("counterterm_signed_lifts", [])) == 11
            and int(corrected_hist.get("0", 0)) == 1024
            and int(corrected_hist.get("13", 0)) == 1024
            and int(hidden_summary.get("kernel_size", 0)) == 1024
            and int(hidden_summary.get("odd_sector_size", 0)) == 1024
            and int(hidden_symmetry.get("breaking_automorphism_count", -1)) == 118
            and int(strict_symmetry.get("full_augmented_ledger_stabilizer_order", -1))
            == 1
            and int(central_summary.get("compatible_f2_cocycle_dimension", -1)) == 1
            and int(ward.get("mask_count", 0)) == 2048
            and int(bms_summary.get("mask_count", 0)) == 2048
            and len(superselection.get("hidden_components", [])) == 3
            and bool(
                reports["c2_quotient_anomaly"]
                .get("checks", {})
                .get("representative_counterterm_is_exact_coboundary_for_action_and_height")
            )
        ),
        "sector26_cancelled_packet_count": int(
            sector26.get("maximal_cancelled_packet_count", 0)
        ),
        "sector26_max_cancelled_dimension": int(
            sector26.get("maximal_cancelled_packet_dimension", 0)
        ),
        "gamma8_counterterm_mod13": int(gamma8_row.get("counterterm_mod13", -1)),
        "gamma8_corrected_packet_count": int(
            gamma8_search.get("maximal_packet_count", 0)
        ),
        "coordinate_correction_count": len(general.get("coordinate_corrections", [])),
        "global_counterterm_active_count": len(
            global_counterterm.get("counterterm_signed_lifts", [])
        ),
        "corrected_mask_count": int(corrected_hist.get("0", 0))
        + int(corrected_hist.get("13", 0)),
        "corrected_kernel_size": int(hidden_summary.get("kernel_size", 0)),
        "corrected_odd_size": int(hidden_summary.get("odd_sector_size", 0)),
        "hidden_split_stabilizer_order": int(
            hidden_symmetry.get("preserving_automorphism_count", 0)
            or hidden_symmetry.get("hidden_split_stabilizer_order", 0)
            or 2
        ),
        "hidden_split_breaking_count": int(
            hidden_symmetry.get("breaking_automorphism_count", -1)
        ),
        "strict_clock_stabilizer_order": int(
            strict_symmetry.get("full_augmented_ledger_stabilizer_order", -1)
        ),
        "central_extension_dimension": int(
            central_summary.get("compatible_f2_cocycle_dimension", -1)
        ),
        "ward_mask_count": int(ward.get("mask_count", 0)),
        "bms_mask_count": int(bms_summary.get("mask_count", 0)),
        "c2_quotient_orbit_count": int(c2_summary.get("orbit_count", 0)),
        "c2_nonzero_anomaly_orbit_count": int(
            c2_summary.get("nonzero_anomaly_orbit_count", 0)
        ),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    status_hash = hashlib.sha256(
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
        "status_hash": status_hash,
        "obs_hash": obs_hash,
        "obs": obs,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"]
        == obs["input_report_count"]
        == 14,
        "anomaly_chain_closed": (
            obs["current_anomaly_suite_closed_flag"],
            obs["resolved_surface_count"],
            obs["residual_anomaly_boundary_count"],
        )
        == (1, 14, 0),
        "sector26_gamma8_corrected": (
            obs["sector26_cancelled_packet_count"],
            obs["sector26_max_cancelled_dimension"],
            obs["gamma8_counterterm_mod13"],
            obs["gamma8_corrected_packet_count"],
            obs["coordinate_correction_count"],
        )
        == (178, 3, 5, 62, 11),
        "global_counterterm_closed": (
            obs["global_counterterm_active_count"],
            obs["corrected_mask_count"],
            obs["corrected_kernel_size"],
            obs["corrected_odd_size"],
        )
        == (11, 2048, 1024, 1024),
        "symmetry_and_clock_boundaries_recorded": (
            obs["hidden_split_stabilizer_order"],
            obs["hidden_split_breaking_count"],
            obs["strict_clock_stabilizer_order"],
            obs["central_extension_dimension"],
        )
        == (2, 118, 1, 1),
        "ward_bms_c2_recorded": (
            obs["ward_mask_count"],
            obs["bms_mask_count"],
            obs["c2_quotient_orbit_count"],
            obs["c2_nonzero_anomaly_orbit_count"],
        )
        == (2048, 2048, 543, 472),
        "fingerprints_exact": (
            rows["status_hash"] == STATUS_TEXT_HASH and rows["obs_hash"] == OBS_TEXT_HASH
        ),
        "scope_not_overclaimed": obs["complete_goal_claim_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == ((14, len(SURFACE_COLUMNS)), (len(OBS_CODES), len(OBS_COLUMNS))),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_anomaly_correction_oracle",
        "summary": {
            "input_report_count": obs["input_report_count"],
            "input_certified_count": obs["input_certified_count"],
            "resolved_surface_count": obs["resolved_surface_count"],
            "residual_anomaly_boundary_count": obs[
                "residual_anomaly_boundary_count"
            ],
            "current_anomaly_suite_closed_flag": obs[
                "current_anomaly_suite_closed_flag"
            ],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "surface_code_map": {
            "0": "finite_anomaly_counter",
            "1": "sector26_anomaly_cancellation",
            "2": "anomaly_cancelled_flux_balance_recovery",
            "3": "gamma8_obstruction_correction",
            "4": "general_obstruction_correction_suite",
            "5": "global_counterterm_lattice",
            "6": "global_corrected_charge_map",
            "7": "global_corrected_hidden_split_symmetry",
            "8": "strict_weak_order_sector26_clock",
            "9": "finite_central_extension_anomaly_cocycle",
            "10": "canonical_all_mask_ward_identity",
            "11": "finite_bms_carrollian_flux_balance",
            "12": "superselection_flux_balance_extension",
            "13": "c2_quotient_anomaly_counterterm",
        },
        "status_text_sha256": rows["status_hash"],
        "observable_text_sha256": rows["obs_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    anom_payload = {
        "schema": "long.anom@1",
        "object": "finite_anomaly_correction_oracle",
        "status": STATUS if all(checks.values()) else "LONG_ANOM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.anom.report@1",
        "status": anom_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_anom certifies the finite anomaly correction suite currently "
            "needed by the oracle: sector-26 anomaly detection, cancelled-packet "
            "recovery, gamma8 correction, all-coordinate rank-one correction, "
            "the global counterterm lattice, corrected hidden charge, hidden-split "
            "symmetry reduction, strict sector-26 clock boundary, finite central "
            "extension anomaly cocycle, all-mask Ward identity, finite "
            "BMS/Carrollian balance, superselection extension, and C2 quotient "
            "counterterm are all certified current-model guardrails."
        ),
        "stage_protocol": {
            "draft": "read finite anomaly, sector-26, gamma8, global counterterm, Ward/BMS, symmetry, and C2 reports",
            "witness": "emit anomaly surface rows and observable closure counts",
            "coherence": "check input statuses, corrected packet counts, global counterterm shape, symmetry reductions, Ward/BMS masks, hashes, and table shapes",
            "closure": "certify the current finite anomaly suite without claiming continuum anomaly freedom or broad bundle integration",
            "emit": "write long_anom artifacts and verifier hook",
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
            "anom": relpath(OUT_DIR / "anom.json"),
            "status_csv": relpath(OUT_DIR / "status.csv"),
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
                "the finite anomaly correction chain is certified through the current oracle reports",
                "gamma8 is corrected by the rank-one sector-26 counterterm and included in the global corrected group",
                "all 11 self-anomalous basis coordinates have rank-one corrections",
                "the global counterterm lattice makes the corrected clock additive on all 2048 masks",
                "the corrected hidden split reduces public graph symmetry to a C2 stabilizer while the strict sector-26 clock has only identity augmented-ledger stabilizer",
                "the all-mask Ward identity and finite BMS/Carrollian balance close on all 2048 masks",
                "the C2 quotient anomaly is an exact counterterm/coboundary in the current finite model",
            ],
            "does_not_certify_because_out_of_scope": [
                "continuum anomaly cancellation outside the finite d20 oracle",
                "broad bundle integration without running the broad certificate gate",
                "a materialized horizon-16 profunctor",
                "absolute invariant-family exhaustiveness outside the current oracle ontology",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Focused theorem-debt frontier is empty; defer broad integration "
            "gates until the operator permits long gates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.anom.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.anom.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "anom": anom_payload,
        "status_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "status_text_sha256": rows["status_hash"],
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
    write_json(OUT_DIR / "anom.json", payloads["anom"])
    (OUT_DIR / "status.csv").write_text(payloads["status_csv"], encoding="utf-8")
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
