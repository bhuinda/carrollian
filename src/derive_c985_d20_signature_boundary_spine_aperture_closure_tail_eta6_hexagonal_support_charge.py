from __future__ import annotations

import csv
import json
from collections import Counter
from io import StringIO
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame as frame
    from . import derive_c985_sixj_conductance as preservation
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame as frame
    import derive_c985_sixj_conductance as preservation
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = preservation.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_HEXAGONAL_SUPPORT_CHARGE_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SIXJ_FRAME_REPORT = frame.OUT_DIR / "report.json"
SIXJ_FRAME_CUT_EDGES = frame.OUT_DIR / "sixj_bottleneck_cut_edges.csv"
SIXJ_FRAME_TABLES = (
    frame.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_tables.npz"
)
PRESERVATION_REPORT = preservation.OUT_DIR / "report.json"
PRESERVATION_TABLES = (
    preservation.OUT_DIR
    / "sixj_conductance_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge.py"
)

EDGE_COLUMNS = [
    "edge_row_id",
    "frame_edge_id",
    "transfer_edge_id",
    "abstract_u",
    "abstract_v",
    "source_state_id",
    "target_state_id",
    "source_side_code",
    "target_side_code",
    "undirected_stationary_flux_x1e12",
    "transfer_boundary_source_count",
    "transfer_boundary_target_count",
]
ABSTRACT_VERTEX_COLUMNS = [
    "abstract_vertex_id",
    "degree",
    "degree_mod2",
    "boundary_mod2_flag",
]
OPPOSITE_PAIR_COLUMNS = [
    "opposite_pair_id",
    "frame_edge_id_a",
    "frame_edge_id_b",
    "abstract_edge_code_a",
    "abstract_edge_code_b",
    "vertex_cover_count",
    "perfect_matching_flag",
    "flux_sum_x1e12",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "eta6_edge_count": 0,
    "eta6_nonzero_flag": 1,
    "uniform_flux_flag": 2,
    "per_edge_flux_x1e12": 3,
    "total_flux_x1e12": 4,
    "transfer_boundary_vertex_count": 5,
    "transfer_cycle_flag": 6,
    "abstract_vertex_count": 7,
    "abstract_edge_count": 8,
    "abstract_mod2_boundary_weight": 9,
    "abstract_cycle_flag": 10,
    "opposite_pair_count": 11,
    "perfect_matching_pair_count": 12,
    "relative_cut_charge_flag": 13,
    "preservation_aggregate_row_count": 14,
    "preservation_decreasing_row_count": 15,
    "preservation_support_changing_row_count": 16,
}


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def load_csv_rows(path) -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(path.read_text(encoding="utf-8"))))


def edge_code(u: int, v: int) -> int:
    return int(f"{min(u, v)}{max(u, v)}")


def parse_edge_row(row_id: int, row: dict[str, str]) -> dict[str, int]:
    abstract = row["abstract_tetra_edge"]
    u = int(abstract[0])
    v = int(abstract[1])
    return {
        "edge_row_id": row_id,
        "frame_edge_id": int(row["frame_edge_id"]),
        "transfer_edge_id": int(row["transfer_edge_id"]),
        "abstract_u": u,
        "abstract_v": v,
        "source_state_id": int(row["source_state_id"]),
        "target_state_id": int(row["target_state_id"]),
        "source_side_code": int(row["source_side_code"]),
        "target_side_code": int(row["target_side_code"]),
        "undirected_stationary_flux_x1e12": int(
            row["undirected_stationary_flux_x1e12"]
        ),
        "transfer_boundary_source_count": 1,
        "transfer_boundary_target_count": 1,
    }


def build_abstract_vertex_rows(edge_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    degrees: Counter[int] = Counter()
    for row in edge_rows:
        degrees[row["abstract_u"]] += 1
        degrees[row["abstract_v"]] += 1
    return [
        {
            "abstract_vertex_id": vertex,
            "degree": degrees[vertex],
            "degree_mod2": degrees[vertex] % 2,
            "boundary_mod2_flag": int(degrees[vertex] % 2 != 0),
        }
        for vertex in range(4)
    ]


def build_opposite_pair_rows(edge_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    by_code = {
        edge_code(row["abstract_u"], row["abstract_v"]): row for row in edge_rows
    }
    pairs = [(1, 23), (2, 13), (3, 12)]
    rows = []
    for pair_id, (code_a, code_b) in enumerate(pairs):
        row_a = by_code[code_a]
        row_b = by_code[code_b]
        vertices = {
            row_a["abstract_u"],
            row_a["abstract_v"],
            row_b["abstract_u"],
            row_b["abstract_v"],
        }
        rows.append(
            {
                "opposite_pair_id": pair_id,
                "frame_edge_id_a": row_a["frame_edge_id"],
                "frame_edge_id_b": row_b["frame_edge_id"],
                "abstract_edge_code_a": code_a,
                "abstract_edge_code_b": code_b,
                "vertex_cover_count": len(vertices),
                "perfect_matching_flag": int(len(vertices) == 4),
                "flux_sum_x1e12": row_a["undirected_stationary_flux_x1e12"]
                + row_b["undirected_stationary_flux_x1e12"],
            }
        )
    return rows


def preservation_observables() -> dict[int, int]:
    tables = np.load(PRESERVATION_TABLES, allow_pickle=False)
    return {
        int(row[1]): int(row[2])
        for row in np.asarray(tables["observable_table"], dtype=np.int64)
    }


def build_payload_rows() -> dict[str, Any]:
    frame_report = load_json(SIXJ_FRAME_REPORT)
    preservation_report = load_json(PRESERVATION_REPORT)
    edge_rows = [
        parse_edge_row(row_id, row)
        for row_id, row in enumerate(load_csv_rows(SIXJ_FRAME_CUT_EDGES))
    ]
    abstract_vertex_rows = build_abstract_vertex_rows(edge_rows)
    opposite_pair_rows = build_opposite_pair_rows(edge_rows)
    transfer_boundary_vertices = {
        row["source_state_id"] for row in edge_rows
    } | {row["target_state_id"] for row in edge_rows}
    flux_values = {row["undirected_stationary_flux_x1e12"] for row in edge_rows}
    preservation_values = preservation_observables()

    observable_values = {
        "eta6_edge_count": len(edge_rows),
        "eta6_nonzero_flag": int(len(edge_rows) > 0),
        "uniform_flux_flag": int(len(flux_values) == 1),
        "per_edge_flux_x1e12": next(iter(flux_values)),
        "total_flux_x1e12": sum(
            row["undirected_stationary_flux_x1e12"] for row in edge_rows
        ),
        "transfer_boundary_vertex_count": len(transfer_boundary_vertices),
        "transfer_cycle_flag": int(len(transfer_boundary_vertices) == 0),
        "abstract_vertex_count": len(abstract_vertex_rows),
        "abstract_edge_count": len(edge_rows),
        "abstract_mod2_boundary_weight": sum(
            row["boundary_mod2_flag"] for row in abstract_vertex_rows
        ),
        "abstract_cycle_flag": int(
            sum(row["boundary_mod2_flag"] for row in abstract_vertex_rows) == 0
        ),
        "opposite_pair_count": len(opposite_pair_rows),
        "perfect_matching_pair_count": sum(
            row["perfect_matching_flag"] for row in opposite_pair_rows
        ),
        "relative_cut_charge_flag": int(
            all(row["source_side_code"] == 1 for row in edge_rows)
            and all(row["target_side_code"] == -1 for row in edge_rows)
            and len(edge_rows) == 6
        ),
        "preservation_aggregate_row_count": preservation_values[
            preservation.OBSERVABLE_CODES["aggregate_row_count"]
        ],
        "preservation_decreasing_row_count": preservation_values[
            preservation.OBSERVABLE_CODES["conductance_decreasing_row_count"]
        ],
        "preservation_support_changing_row_count": preservation_values[
            preservation.OBSERVABLE_CODES["support_changing_row_count"]
        ],
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return {
        "frame_report": frame_report,
        "preservation_report": preservation_report,
        "edge_rows": edge_rows,
        "abstract_vertex_rows": abstract_vertex_rows,
        "opposite_pair_rows": opposite_pair_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    abstract_vertex_table = table_from_rows(
        ABSTRACT_VERTEX_COLUMNS,
        rows["abstract_vertex_rows"],
    )
    opposite_pair_table = table_from_rows(
        OPPOSITE_PAIR_COLUMNS,
        rows["opposite_pair_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]

    edge_set = {
        edge_code(row["abstract_u"], row["abstract_v"]) for row in rows["edge_rows"]
    }
    checks = {
        "sixj_frame_report_certified": rows["frame_report"].get("status")
        == frame.STATUS,
        "conductance_preservation_report_certified": rows[
            "preservation_report"
        ].get("status")
        == preservation.STATUS,
        "eta6_is_nonzero_uniform_six_edge_support": (
            observable_values["eta6_edge_count"],
            observable_values["eta6_nonzero_flag"],
            observable_values["uniform_flux_flag"],
            observable_values["per_edge_flux_x1e12"],
            observable_values["total_flux_x1e12"],
        )
        == (6, 1, 1, 170_677_590, 1_024_065_540),
        "eta6_is_complete_k4_edge_support": (
            edge_set,
            [row["degree"] for row in rows["abstract_vertex_rows"]],
        )
        == ({1, 2, 3, 12, 13, 23}, [3, 3, 3, 3]),
        "eta6_is_not_raw_transfer_or_k4_cycle": (
            observable_values["transfer_boundary_vertex_count"],
            observable_values["transfer_cycle_flag"],
            observable_values["abstract_mod2_boundary_weight"],
            observable_values["abstract_cycle_flag"],
        )
        == (12, 0, 4, 0),
        "eta6_has_three_opposite_edge_matchings": (
            observable_values["opposite_pair_count"],
            observable_values["perfect_matching_pair_count"],
        )
        == (3, 3),
        "eta6_is_preserved_relative_cut_charge": (
            observable_values["relative_cut_charge_flag"],
            observable_values["preservation_aggregate_row_count"],
            observable_values["preservation_decreasing_row_count"],
            observable_values["preservation_support_changing_row_count"],
        )
        == (1, 606, 153, 0),
        "table_shapes_match_codebooks": (
            tuple(edge_table.shape),
            tuple(abstract_vertex_table.shape),
            tuple(opposite_pair_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (6, len(EDGE_COLUMNS)),
            (4, len(ABSTRACT_VERTEX_COLUMNS)),
            (3, len(OPPOSITE_PAIR_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "eta6_edge_codes": sorted(edge_set),
        "abstract_vertex_degrees": [
            row["degree"] for row in rows["abstract_vertex_rows"]
        ],
        "transfer_boundary_vertex_count": observable_values[
            "transfer_boundary_vertex_count"
        ],
        "abstract_mod2_boundary_weight": observable_values[
            "abstract_mod2_boundary_weight"
        ],
        "opposite_pair_count": observable_values["opposite_pair_count"],
        "preserved_under_certified_fsymbol_rows": observable_values[
            "preservation_aggregate_row_count"
        ],
        "preserved_under_conductance_decreasing_rows": observable_values[
            "preservation_decreasing_row_count"
        ],
        "edge_table_sha256": pair.parent.sha_array(edge_table),
        "abstract_vertex_table_sha256": pair.parent.sha_array(abstract_vertex_table),
        "opposite_pair_table_sha256": pair.parent.sha_array(opposite_pair_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    eta6 = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge@1",
        "object": "C985->d20",
        "parent": PRESERVATION_REPORT.relative_to(ROOT).as_posix(),
        "definition": {
            "eta6": "the six old spectral-cut transfer edges from the certified 6j bottleneck frame",
            "edge_codes": sorted(edge_set),
            "reading": (
                "eta6 is a nonzero relative cut/support charge with complete "
                "K4 edge support; it is not a raw graph-cycle under either "
                "transfer-state incidence or abstract K4 mod-2 incidence"
            ),
        },
        "summary": {
            "eta6_edge_count": observable_values["eta6_edge_count"],
            "relative_cut_charge_flag": observable_values["relative_cut_charge_flag"],
            "abstract_cycle_flag": observable_values["abstract_cycle_flag"],
            "transfer_cycle_flag": observable_values["transfer_cycle_flag"],
            "preservation_decreasing_row_count": observable_values[
                "preservation_decreasing_row_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_HEXAGONAL_SUPPORT_CHARGE_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "eta6 is the nonzero six-edge relative cut/support charge carried "
            "by the certified 6j bottleneck. Direct incidence checks show it "
            "is not an ordinary graph cycle: the transfer-state boundary has "
            "12 endpoints and the abstract K4 mod-2 boundary has weight 4. "
            "The preserved object is therefore the hexagonal support charge, "
            "not a naive 1-cycle."
        ),
        "stage_protocol": {
            "draft": "start from the certified six-edge 6j bottleneck frame and conductance-preservation aggregate",
            "witness": "materialize eta6 as six transfer cut edges with abstract K4 addresses",
            "coherence": "compute transfer incidence, K4 vertex incidence, opposite-edge matching split, and preservation linkage",
            "closure": "certify eta6 as a nonzero preserved relative support charge and reject the naive cycle model",
            "emit": "emit eta6 support, incidence, opposite-pair, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "sixj_frame_report": pair.parent.input_entry(
                SIXJ_FRAME_REPORT,
                {
                    "status": rows["frame_report"].get("status"),
                    "certificate_sha256": rows["frame_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "sixj_frame_cut_edges": pair.parent.input_entry(SIXJ_FRAME_CUT_EDGES),
            "sixj_frame_tables": pair.parent.input_entry(SIXJ_FRAME_TABLES),
            "conductance_preservation_report": pair.parent.input_entry(
                PRESERVATION_REPORT,
                {
                    "status": rows["preservation_report"].get("status"),
                    "certificate_sha256": rows["preservation_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "conductance_preservation_tables": pair.parent.input_entry(
                PRESERVATION_TABLES
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "eta6": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge.json"
            ),
            "edge_csv": pair.parent.relpath(OUT_DIR / "eta6_cut_edges.csv"),
            "abstract_vertex_csv": pair.parent.relpath(
                OUT_DIR / "eta6_abstract_vertex_incidence.csv"
            ),
            "opposite_pair_csv": pair.parent.relpath(
                OUT_DIR / "eta6_opposite_edge_pairs.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "eta6_hexagonal_support_charge_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "eta6 is a nonzero six-edge support charge",
                "eta6 has complete K4 edge support with three opposite-edge matchings",
                "eta6 is preserved under all currently certified F-symbol/6j rows and every conductance-decreasing row",
                "eta6 is not a raw transfer-state or abstract K4 graph cycle",
            ],
            "does_not_certify_because_not_required": [
                "a relative cohomology group presentation for eta6",
                "Dini torsion or H4 lift coordinates",
                "cyclic/dihedral six-window intervention closure",
                "full rigidity under the complete associator geometry",
            ],
        },
        "next_highest_yield_item": (
            "Compute the relative holonomy/cohomology presentation for eta6, "
            "because the direct incidence test shows the preserved object is "
            "a cut/support charge rather than an ordinary 1-cycle."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "eta6 is nonzero and preserved in the current bounded F-symbol evidence",
            "eta6 is K4-complete but not a naive graph cycle",
            "the next invariant should be relative holonomy/cohomology, not another local repair graph",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified six-edge 6j bottleneck frame",
            "load certified conductance-decreasing preservation aggregate",
            "compute transfer and abstract K4 incidence of eta6",
            "check nonzero support charge, opposite-pair split, and non-cycle status",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "eta6": eta6,
        "edge_csv": pair.csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "abstract_vertex_csv": pair.csv_text(
            ABSTRACT_VERTEX_COLUMNS,
            rows["abstract_vertex_rows"],
        ),
        "opposite_pair_csv": pair.csv_text(
            OPPOSITE_PAIR_COLUMNS,
            rows["opposite_pair_rows"],
        ),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "edge_table": edge_table,
        "abstract_vertex_table": abstract_vertex_table,
        "opposite_pair_table": opposite_pair_table,
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
        / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge.json",
        payloads["eta6"],
    )
    (OUT_DIR / "eta6_cut_edges.csv").write_text(
        payloads["edge_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_abstract_vertex_incidence.csv").write_text(
        payloads["abstract_vertex_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_opposite_edge_pairs.csv").write_text(
        payloads["opposite_pair_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_hexagonal_support_charge_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_tables.npz",
        edge_table=payloads["edge_table"],
        abstract_vertex_table=payloads["abstract_vertex_table"],
        opposite_pair_table=payloads["opposite_pair_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_certificate.json",
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
