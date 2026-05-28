from __future__ import annotations

import json
import math
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index as dini
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator as transfer
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index as dini
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator as transfer
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = dini.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_H4_PRECURSOR_LIFT_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

DINI_REPORT = dini.OUT_DIR / "report.json"
DINI_TABLES = (
    dini.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_tables.npz"
)
TRANSFER_REPORT = transfer.OUT_DIR / "report.json"
TRANSFER_CENTERS = (
    transfer.OUT_DIR / "aperture_closure_tail_second_window_transfer_centers.csv"
)
TRANSFER_TABLES = (
    transfer.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift.py"
)

H4_COLUMNS = [
    "stage_id",
    "stage_code",
    "coordinate_source_code",
    "poincare_available_flag",
    "symbolic_chart_flag",
    "x_x1e12",
    "y_x1e12",
    "poincare_radius_x1e12",
    "r_holonomy_x1e12",
    "h_conductance_x1e12",
    "h_drop_from_base_x1e12",
    "inside_unit_disk_flag",
    "h4_metric_certified_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "coordinate_count": 0,
    "poincare_available_count": 1,
    "symbolic_precursor_count": 2,
    "inside_unit_disk_count": 3,
    "h4_metric_certified_count": 4,
    "r_fixed_nonzero_count": 5,
    "h_strict_descent_flag": 6,
    "base_x_x1e12": 7,
    "base_y_x1e12": 8,
    "base_radius_x1e12": 9,
    "final_h_conductance_x1e12": 10,
    "base_to_final_h_drop_x1e12": 11,
    "symbolic_chart_max_radius_x1e12": 12,
}

SCALE = 1_000_000_000_000
R_HOLONOMY_X1E12 = SCALE


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def symbolic_xy(stage_id: int, conductance_x1e12: int) -> tuple[int, int]:
    x = -300_000_000_000 + stage_id * 150_000_000_000
    y = conductance_x1e12 * 100
    return x, y


def radius_x1e12(x: int, y: int) -> int:
    return math.isqrt(x * x + y * y)


def build_h4_rows(
    dini_report: dict[str, Any],
    transfer_report: dict[str, Any],
    chain_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    mass_center = transfer_report["witness"]["mass_center"]
    rows = []
    base_conductance = chain_rows[0]["cut_conductance_x1e12"]
    for row in chain_rows:
        stage_id = row["stage_id"]
        if stage_id == 0:
            x = int(mass_center["center_x_x1e12"])
            y = int(mass_center["center_y_x1e12"])
            radius = int(mass_center["center_radius_x1e12"])
            source_code = 0
            poincare_available = 1
            symbolic = 0
        else:
            x, y = symbolic_xy(stage_id, row["cut_conductance_x1e12"])
            radius = radius_x1e12(x, y)
            source_code = 1
            poincare_available = 0
            symbolic = 1
        rows.append(
            {
                "stage_id": stage_id,
                "stage_code": row["stage_code"],
                "coordinate_source_code": source_code,
                "poincare_available_flag": poincare_available,
                "symbolic_chart_flag": symbolic,
                "x_x1e12": x,
                "y_x1e12": y,
                "poincare_radius_x1e12": radius,
                "r_holonomy_x1e12": row["eta6_holonomy_pairing"]
                * R_HOLONOMY_X1E12,
                "h_conductance_x1e12": row["cut_conductance_x1e12"],
                "h_drop_from_base_x1e12": base_conductance
                - row["cut_conductance_x1e12"],
                "inside_unit_disk_flag": int(radius < SCALE),
                "h4_metric_certified_flag": 0,
            }
        )
    if dini_report["witness"]["holonomy_pairing_chain"] != [1, 1, 1, 1, 1]:
        raise ValueError("Dini holonomy chain is not fixed at 1")
    return rows


def build_observable_rows(
    h4_rows: list[dict[str, int]],
) -> tuple[list[dict[str, int]], dict[str, int]]:
    heights = [row["h_conductance_x1e12"] for row in h4_rows]
    symbolic_radii = [
        row["poincare_radius_x1e12"]
        for row in h4_rows
        if row["symbolic_chart_flag"] == 1
    ]
    observable_values = {
        "coordinate_count": len(h4_rows),
        "poincare_available_count": sum(
            row["poincare_available_flag"] for row in h4_rows
        ),
        "symbolic_precursor_count": sum(row["symbolic_chart_flag"] for row in h4_rows),
        "inside_unit_disk_count": sum(row["inside_unit_disk_flag"] for row in h4_rows),
        "h4_metric_certified_count": sum(
            row["h4_metric_certified_flag"] for row in h4_rows
        ),
        "r_fixed_nonzero_count": sum(
            row["r_holonomy_x1e12"] == R_HOLONOMY_X1E12 for row in h4_rows
        ),
        "h_strict_descent_flag": int(
            all(left > right for left, right in zip(heights, heights[1:]))
        ),
        "base_x_x1e12": h4_rows[0]["x_x1e12"],
        "base_y_x1e12": h4_rows[0]["y_x1e12"],
        "base_radius_x1e12": h4_rows[0]["poincare_radius_x1e12"],
        "final_h_conductance_x1e12": heights[-1],
        "base_to_final_h_drop_x1e12": heights[0] - heights[-1],
        "symbolic_chart_max_radius_x1e12": max(symbolic_radii),
    }
    rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return rows, observable_values


def build_payload_rows() -> dict[str, Any]:
    dini_report = load_json(DINI_REPORT)
    transfer_report = load_json(TRANSFER_REPORT)
    tables = np.load(DINI_TABLES, allow_pickle=False)
    chain_rows = table_rows(
        np.asarray(tables["chain_table"], dtype=np.int64),
        dini.CHAIN_COLUMNS,
    )
    h4_rows = build_h4_rows(dini_report, transfer_report, chain_rows)
    observable_rows, observable_values = build_observable_rows(h4_rows)
    return {
        "dini_report": dini_report,
        "transfer_report": transfer_report,
        "chain_rows": chain_rows,
        "h4_rows": h4_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    h4_table = table_from_rows(H4_COLUMNS, rows["h4_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    heights = [row["h_conductance_x1e12"] for row in rows["h4_rows"]]

    checks = {
        "dini_torsion_report_certified": rows["dini_report"].get("status")
        == dini.STATUS,
        "second_window_transfer_report_certified": rows["transfer_report"].get(
            "status"
        )
        == transfer.STATUS,
        "h4_precursor_coordinate_scope_is_expected": (
            observable_values["coordinate_count"],
            observable_values["poincare_available_count"],
            observable_values["symbolic_precursor_count"],
            observable_values["h4_metric_certified_count"],
        )
        == (5, 1, 4, 0),
        "base_coordinate_reuses_certified_poincare_mass_center": (
            observable_values["base_x_x1e12"],
            observable_values["base_y_x1e12"],
            observable_values["base_radius_x1e12"],
        )
        == (67_572_661_820, 4_522_140_858, 67_723_810_000),
        "all_precursor_coordinates_stay_inside_unit_disk": observable_values[
            "inside_unit_disk_count"
        ]
        == 5
        and observable_values["symbolic_chart_max_radius_x1e12"] < SCALE,
        "residual_coordinate_is_fixed_nonzero_eta6_holonomy": observable_values[
            "r_fixed_nonzero_count"
        ]
        == 5,
        "height_coordinate_matches_dini_conductance_descent": (
            heights,
            observable_values["h_strict_descent_flag"],
            observable_values["base_to_final_h_drop_x1e12"],
        )
        == (
            [
                4_329_004_000,
                3_649_635_000,
                2_645_503_000,
                2_615_519_000,
                2_610_966_000,
            ],
            1,
            1_718_038_000,
        ),
        "table_shapes_match_codebooks": (
            tuple(h4_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (5, len(H4_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "coordinate_count": observable_values["coordinate_count"],
        "poincare_available_count": observable_values["poincare_available_count"],
        "symbolic_precursor_count": observable_values["symbolic_precursor_count"],
        "h4_metric_certified_count": observable_values["h4_metric_certified_count"],
        "height_chain_x1e12": heights,
        "residual_chain_x1e12": [
            row["r_holonomy_x1e12"] for row in rows["h4_rows"]
        ],
        "base_poincare_center": {
            "x_x1e12": rows["h4_rows"][0]["x_x1e12"],
            "y_x1e12": rows["h4_rows"][0]["y_x1e12"],
            "radius_x1e12": rows["h4_rows"][0]["poincare_radius_x1e12"],
        },
        "h4_table_sha256": pair.parent.sha_array(h4_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    h4 = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift@1",
        "object": "C985->d20",
        "coordinate_reading": {
            "x_y": (
                "stage 0 uses the certified second-window transfer Poincare "
                "mass center; stages 1-4 use a deterministic symbolic "
                "precursor chart until per-intervention Poincare centers exist"
            ),
            "r": "eta6 holonomy pairing scaled by 1e12",
            "h": "cut conductance scaled by 1e12",
            "metric_status": "precursor only; h4_metric_certified_flag is 0",
        },
        "coordinates": [
            {
                "stage_id": row["stage_id"],
                "coordinate_source_code": row["coordinate_source_code"],
                "poincare_available": bool(row["poincare_available_flag"]),
                "x_x1e12": row["x_x1e12"],
                "y_x1e12": row["y_x1e12"],
                "r_holonomy_x1e12": row["r_holonomy_x1e12"],
                "h_conductance_x1e12": row["h_conductance_x1e12"],
            }
            for row in rows["h4_rows"]
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_H4_PRECURSOR_LIFT_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The Dini torsion chain now has a finite four-coordinate precursor "
            "table. Stage 0 reuses the certified second-window Poincare transfer "
            "mass center, stages 1-4 are explicitly symbolic precursor chart "
            "points, r is the fixed eta6 holonomy coordinate, and h is the "
            "strictly descending conductance coordinate. This does not certify "
            "a literal H4 metric embedding."
        ),
        "stage_protocol": {
            "draft": "start from the certified eta6 Dini torsion chain",
            "witness": "attach x,y,r,h coordinates with explicit source flags",
            "coherence": "check base Poincare center, fixed residual coordinate, and strict height descent",
            "closure": "certify the H4 precursor table while leaving metric embedding unclaimed",
            "emit": "emit H4 precursor coordinate table, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "dini_report": pair.parent.input_entry(
                DINI_REPORT,
                {
                    "status": rows["dini_report"].get("status"),
                    "certificate_sha256": rows["dini_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "dini_tables": pair.parent.input_entry(DINI_TABLES),
            "second_window_transfer_report": pair.parent.input_entry(
                TRANSFER_REPORT,
                {
                    "status": rows["transfer_report"].get("status"),
                    "certificate_sha256": rows["transfer_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "second_window_transfer_centers": pair.parent.input_entry(
                TRANSFER_CENTERS
            ),
            "second_window_transfer_tables": pair.parent.input_entry(
                TRANSFER_TABLES
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "h4_precursor": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift.json"
            ),
            "coordinates_csv": pair.parent.relpath(
                OUT_DIR / "eta6_h4_precursor_coordinates.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "eta6_h4_precursor_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a five-stage (x,y,r,h) precursor table for the Dini torsion chain",
                "reuse of the certified second-window Poincare transfer mass center at stage 0",
                "fixed nonzero eta6 holonomy residual coordinate through the chain",
                "strict conductance height descent through the chain",
            ],
            "does_not_certify_because_not_required": [
                "per-intervention Poincare centers for stages 1-4",
                "an H4 metric tensor or distance law",
                "curvature or torsion from a smooth embedding",
                "positive lower asymptote of the conductance relaxation curve",
            ],
        },
        "next_highest_yield_item": (
            "Replace the symbolic H4 precursor coordinates for stages 1-4 with "
            "fresh per-intervention Poincare centers, then test whether the "
            "conductance height descent has a positive lower asymptote at fixed "
            "eta6 holonomy."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the Dini chain has a reproducible four-coordinate precursor",
            "the residual and height coordinates are already certified data",
            "the missing piece for an H4 metric certificate is per-intervention Poincare geometry",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified Dini torsion and second-window transfer reports",
            "attach x,y,r,h coordinates to every Dini-chain stage",
            "check Poincare availability/source flags and inside-disk status",
            "check fixed eta6 residual and descending conductance height",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "h4_precursor": h4,
        "coordinates_csv": pair.csv_text(H4_COLUMNS, rows["h4_rows"]),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "h4_table": h4_table,
        "observable_table": observable_table,
        "certificate": certificate,
        "report": report,
        "manifest": manifest,
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift.json",
        payloads["h4_precursor"],
    )
    (OUT_DIR / "eta6_h4_precursor_coordinates.csv").write_text(
        payloads["coordinates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_h4_precursor_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_tables.npz",
        h4_table=payloads["h4_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_certificate.json",
        payloads["certificate"],
    )
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
