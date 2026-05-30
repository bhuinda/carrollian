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


THEOREM_ID = "long_c59kt"
STATUS = "LONG_C59KT_KERNEL_TIME_SEAM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59ST = PROOF_ROOT / "long_c59st" / "report.json"
LONG_C59ST_KERNEL = PROOF_ROOT / "long_c59st" / "kernel.csv"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_TIME_MAP_MATRIX = PROOF_ROOT / "long_time_map" / "matrix.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59kt.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59kt.py"

KERNEL_TIME_COLUMNS = [
    "atom_id",
    "kernel_value",
    "q_pub_value",
    "time_product",
    "kernel_support_flag",
    "q_pub_support_flag",
    "support_intersection_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "certified_flag",
    "obstruction_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

DECISION_NAMES = [
    "tensor_kernel_available",
    "public_time_trace_available",
    "kernel_annihilated_by_q_pub",
    "kernel_support_disjoint_from_time_support",
    "kernel_time_trace_identified",
    "finite_gauge_null_stress_mode",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "tensor_kernel_time_test",
    "q_pub_annihilation",
    "finite_gauge_null_stress_mode",
    "stress_quotient_by_null_mode",
    "four_dimensional_metric_reduction",
    "physical_stress_energy_lift",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "public_rank",
    "time_rank",
    "kernel_support_count",
    "q_pub_support_count",
    "support_intersection_count",
    "q_pub_dot_kernel",
    "public_kernel_membership_flag",
    "time_trace_nonzero_flag",
    "kernel_time_identification_flag",
    "finite_gauge_null_stress_mode_flag",
    "stress_quotient_needed_flag",
    "four_dimensional_metric_flag",
    "physical_stress_energy_flag",
    "smooth_metric_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def q_pub_vector(matrix_rows: list[dict[str, int]], public_rank: int) -> list[int]:
    q_pub = [0] * public_rank
    for row in matrix_rows:
        if row["matrix_code"] == 1:
            q_pub[row["column_index"]] = row["value"]
    return q_pub


def build_rows() -> dict[str, Any]:
    c59st = load_json(LONG_C59ST)
    time_map = load_json(LONG_TIME_MAP)
    kernel_rows_source = read_csv_int(LONG_C59ST_KERNEL)
    matrix_rows = read_csv_int(LONG_TIME_MAP_MATRIX)
    time_summary = time_map["witness"]["summary"]
    public_rank = int(time_summary["public_rank"])
    time_rank = int(time_summary["public_quotient_dimension"])
    q_pub = q_pub_vector(matrix_rows, public_rank)
    kernel = [
        row["kernel_value"]
        for row in sorted(kernel_rows_source, key=lambda row: row["atom_id"])
    ]

    kernel_time_rows = []
    for atom, kernel_value in enumerate(kernel):
        q_value = q_pub[atom]
        kernel_time_rows.append(
            {
                "atom_id": atom,
                "kernel_value": kernel_value,
                "q_pub_value": q_value,
                "time_product": kernel_value * q_value,
                "kernel_support_flag": int(kernel_value != 0),
                "q_pub_support_flag": int(q_value != 0),
                "support_intersection_flag": int(kernel_value != 0 and q_value != 0),
            }
        )

    q_pub_dot_kernel = sum(row["time_product"] for row in kernel_time_rows)
    kernel_support_count = sum(row["kernel_support_flag"] for row in kernel_time_rows)
    q_pub_support_count = sum(row["q_pub_support_flag"] for row in kernel_time_rows)
    support_intersection_count = sum(
        row["support_intersection_flag"] for row in kernel_time_rows
    )
    public_kernel_membership_flag = int(q_pub_dot_kernel == 0)
    time_trace_nonzero_flag = int(q_pub_dot_kernel != 0)
    kernel_time_identification_flag = int(
        public_kernel_membership_flag == 0 and support_intersection_count > 0
    )
    finite_gauge_null_stress_mode_flag = int(
        public_kernel_membership_flag == 1
        and kernel_support_count > 0
        and kernel_time_identification_flag == 0
    )
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59st)) + int(certified(time_map)),
        "public_rank": public_rank,
        "time_rank": time_rank,
        "kernel_support_count": kernel_support_count,
        "q_pub_support_count": q_pub_support_count,
        "support_intersection_count": support_intersection_count,
        "q_pub_dot_kernel": q_pub_dot_kernel,
        "public_kernel_membership_flag": public_kernel_membership_flag,
        "time_trace_nonzero_flag": time_trace_nonzero_flag,
        "kernel_time_identification_flag": kernel_time_identification_flag,
        "finite_gauge_null_stress_mode_flag": finite_gauge_null_stress_mode_flag,
        "stress_quotient_needed_flag": 1,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["stress_quotient_by_null_mode"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["tensor_kernel_available"],
            "decision_code": DECISION_CODES["tensor_kernel_available"],
            "value": kernel_support_count,
            "certified_flag": int(kernel_support_count > 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["public_time_trace_available"],
            "decision_code": DECISION_CODES["public_time_trace_available"],
            "value": q_pub_support_count,
            "certified_flag": int(q_pub_support_count > 0 and time_rank == 1),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["kernel_annihilated_by_q_pub"],
            "decision_code": DECISION_CODES["kernel_annihilated_by_q_pub"],
            "value": public_kernel_membership_flag,
            "certified_flag": public_kernel_membership_flag,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["kernel_support_disjoint_from_time_support"],
            "decision_code": DECISION_CODES[
                "kernel_support_disjoint_from_time_support"
            ],
            "value": support_intersection_count,
            "certified_flag": int(support_intersection_count == 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["kernel_time_trace_identified"],
            "decision_code": DECISION_CODES["kernel_time_trace_identified"],
            "value": kernel_time_identification_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["finite_gauge_null_stress_mode"],
            "decision_code": DECISION_CODES["finite_gauge_null_stress_mode"],
            "value": finite_gauge_null_stress_mode_flag,
            "certified_flag": finite_gauge_null_stress_mode_flag,
            "obstruction_flag": 0,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["tensor_kernel_time_test"],
            "gap_code": GAP_CODES["tensor_kernel_time_test"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["q_pub_annihilation"],
            "gap_code": GAP_CODES["q_pub_annihilation"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["finite_gauge_null_stress_mode"],
            "gap_code": GAP_CODES["finite_gauge_null_stress_mode"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_quotient_by_null_mode"],
            "gap_code": GAP_CODES["stress_quotient_by_null_mode"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["four_dimensional_metric_reduction"],
            "gap_code": GAP_CODES["four_dimensional_metric_reduction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_stress_energy_lift"],
            "gap_code": GAP_CODES["physical_stress_energy_lift"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59st": c59st,
        "time_map": time_map,
        "kernel_time_rows": kernel_time_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "q_pub": q_pub,
        "kernel": kernel,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    kernel_time_table = table_from_rows(
        KERNEL_TIME_COLUMNS, rows["kernel_time_rows"]
    )
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    q_pub_table = np.asarray([rows["q_pub"]], dtype=np.int64)
    kernel_table = np.asarray([rows["kernel"]], dtype=np.int64)
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "kernel_and_time_trace_available": obs["public_rank"] == 20
        and obs["time_rank"] == 1
        and obs["kernel_support_count"] == 2
        and obs["q_pub_support_count"] == 1,
        "q_pub_annihilation_exact": obs["q_pub_dot_kernel"] == 0
        and obs["public_kernel_membership_flag"] == 1,
        "time_identification_obstructed": obs["time_trace_nonzero_flag"] == 0
        and obs["support_intersection_count"] == 0
        and obs["kernel_time_identification_flag"] == 0,
        "gauge_null_mode_certified": obs["finite_gauge_null_stress_mode_flag"] == 1
        and obs["stress_quotient_needed_flag"] == 1,
        "metric_physical_boundaries_preserved": obs["four_dimensional_metric_flag"]
        == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": kernel_time_table.shape
        == (20, len(KERNEL_TIME_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS))
        and q_pub_table.shape == (1, 20)
        and kernel_table.shape == (1, 20),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_kernel_time_seam",
        "summary": {
            "public_rank": obs["public_rank"],
            "time_rank": obs["time_rank"],
            "kernel_support_count": obs["kernel_support_count"],
            "q_pub_support_count": obs["q_pub_support_count"],
            "support_intersection_count": obs["support_intersection_count"],
            "q_pub_dot_kernel": obs["q_pub_dot_kernel"],
            "public_kernel_membership_flag": obs["public_kernel_membership_flag"],
            "kernel_time_identification_flag": obs[
                "kernel_time_identification_flag"
            ],
            "finite_gauge_null_stress_mode_flag": obs[
                "finite_gauge_null_stress_mode_flag"
            ],
            "stress_quotient_needed_flag": obs["stress_quotient_needed_flag"],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "kernel_time_table_sha256": sha_array(kernel_time_table),
        "kernel_time_text_sha256": sha_text(
            csv_text(KERNEL_TIME_COLUMNS, rows["kernel_time_rows"])
        ),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "q_pub_table_sha256": sha_array(q_pub_table),
        "kernel_table_sha256": sha_array(kernel_table),
    }
    c59kt = {
        "schema": "long.c59kt@1",
        "object": "c59x_kernel_time_seam",
        "status": STATUS if all(checks.values()) else "LONG_C59KT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59kt.report@1",
        "status": c59kt["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59kt compares the one-dimensional kernel of the finite "
            "symmetric stress candidate with q_pub from the certified time map. "
            "The kernel is annihilated by q_pub, so it lies in the public kernel "
            "rather than realizing the public time trace."
        ),
        "stage_protocol": {
            "draft": "read long_c59st kernel vector and long_time_map q_pub",
            "witness": "emit per-atom kernel/time products, decisions, gaps, and observables",
            "coherence": "check q_pub dot kernel, support intersection, public-kernel membership, and open metric boundaries",
            "closure": "certify the stress null direction as a public-kernel gauge-null mode",
            "emit": "write long_c59kt artifacts and verifier hook",
        },
        "inputs": {
            "long_c59st": input_entry(
                LONG_C59ST,
                {
                    "status": rows["c59st"].get("status"),
                    "certificate_sha256": rows["c59st"].get("certificate_sha256"),
                },
            ),
            "long_c59st_kernel": input_entry(LONG_C59ST_KERNEL),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": rows["time_map"].get("status"),
                    "certificate_sha256": rows["time_map"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_time_map_matrix": input_entry(LONG_TIME_MAP_MATRIX),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59kt": relpath(OUT_DIR / "c59kt.json"),
            "kernel_time_csv": relpath(OUT_DIR / "kernel_time.csv"),
            "decision_csv": relpath(OUT_DIR / "decision.csv"),
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
                "the tensor kernel vector has zero public time component",
                "the tensor kernel lies in the certified public kernel of q_pub",
                "the tensor null direction is a finite gauge-null stress mode under the current time map",
                "the stress-kernel count match is not a canonical time-trace identification",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "identification of the tensor kernel with the public time trace",
                "a quotient stress tensor after removing the gauge-null mode",
                "a four-dimensional metric reduction",
                "a smooth Lorentzian metric",
                "a physical stress-energy tensor",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Quotient the finite stress candidate by the certified gauge-null "
            "mode and retest the resulting 19-dimensional form against the "
            "public-kernel boundary."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59kt.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59kt.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59kt": c59kt,
        "kernel_time_csv": csv_text(
            KERNEL_TIME_COLUMNS, rows["kernel_time_rows"]
        ),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "kernel_time_table": kernel_time_table,
        "decision_table": decision_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "q_pub_table": q_pub_table,
        "kernel_table": kernel_table,
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
    write_json(OUT_DIR / "c59kt.json", payloads["c59kt"])
    (OUT_DIR / "kernel_time.csv").write_text(
        payloads["kernel_time_csv"], encoding="utf-8"
    )
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        kernel_time_table=payloads["kernel_time_table"],
        decision_table=payloads["decision_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
        q_pub_table=payloads["q_pub_table"],
        kernel_table=payloads["kernel_table"],
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
