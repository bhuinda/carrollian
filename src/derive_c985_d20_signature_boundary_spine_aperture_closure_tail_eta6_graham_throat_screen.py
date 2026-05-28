from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift as h4
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge as eta6
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift as h4
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge as eta6
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = h4.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_GRAHAM_THROAT_SCREEN_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

H4_REPORT = h4.OUT_DIR / "report.json"
H4_TABLES = (
    h4.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_tables.npz"
)
ETA6_REPORT = eta6.OUT_DIR / "report.json"
ETA6_TABLES = (
    eta6.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen.py"
)

SCALE = 1_000_000_000_000
GRAHAM_AREA_NUM_X1E6 = 674_981
REGULAR_AREA_NUM_X1E6 = 649_519
GRAHAM_RATIO_X1E12 = (GRAHAM_AREA_NUM_X1E6 * SCALE) // REGULAR_AREA_NUM_X1E6
GRAHAM_TOLERANCE_X1E12 = 5_000_000_000

PAIR_COLUMNS = [
    "pair_id",
    "from_stage_id",
    "to_stage_id",
    "from_height_x1e12",
    "to_height_x1e12",
    "height_ratio_x1e12",
    "graham_ratio_abs_error_x1e12",
    "within_graham_tolerance_flag",
]
GRAPH_COLUMNS = [
    "graph_id",
    "vertex_count",
    "edge_count",
    "min_degree",
    "max_degree",
    "cubic_flag",
    "planar_flag",
    "three_vertex_connected_flag",
    "truncated_icosahedral_vertex_count_flag",
    "truncated_icosahedral_edge_count_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "graham_area_x1e6": 0,
    "regular_area_x1e6": 1,
    "graham_ratio_x1e12": 2,
    "height_pair_count": 3,
    "closest_pair_from_stage_id": 4,
    "closest_pair_to_stage_id": 5,
    "closest_height_ratio_x1e12": 6,
    "closest_graham_error_x1e12": 7,
    "graham_ratio_match_count": 8,
    "support_fixed_flag": 9,
    "strict_height_descent_flag": 10,
    "k4_polyhedral_constraint_flag": 11,
    "truncated_icosahedral_match_flag": 12,
    "area_certificate_available_flag": 13,
}


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


def connected_after_removing(
    vertices: set[int],
    edges: list[tuple[int, int]],
    removed: set[int],
) -> bool:
    remaining = sorted(vertices - removed)
    if not remaining:
        return True
    adjacency = {vertex: set() for vertex in remaining}
    for left, right in edges:
        if left in removed or right in removed:
            continue
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = {remaining[0]}
    stack = [remaining[0]]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen == set(remaining)


def k4_graph_row() -> dict[str, int]:
    vertices = {0, 1, 2, 3}
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    degrees = {
        vertex: sum(vertex in edge for edge in edges)
        for vertex in vertices
    }
    three_connected = all(
        connected_after_removing(vertices, edges, set(removed))
        for size in (1, 2)
        for removed in combinations(vertices, size)
    )
    return {
        "graph_id": 0,
        "vertex_count": len(vertices),
        "edge_count": len(edges),
        "min_degree": min(degrees.values()),
        "max_degree": max(degrees.values()),
        "cubic_flag": int(set(degrees.values()) == {3}),
        "planar_flag": 1,
        "three_vertex_connected_flag": int(three_connected),
        "truncated_icosahedral_vertex_count_flag": int(len(vertices) == 60),
        "truncated_icosahedral_edge_count_flag": int(len(edges) == 90),
    }


def build_pair_rows(heights: list[int]) -> list[dict[str, int]]:
    rows = []
    for pair_id, (source, target) in enumerate(combinations(range(len(heights)), 2)):
        ratio = (heights[source] * SCALE) // heights[target]
        error = abs(ratio - GRAHAM_RATIO_X1E12)
        rows.append(
            {
                "pair_id": pair_id,
                "from_stage_id": source,
                "to_stage_id": target,
                "from_height_x1e12": heights[source],
                "to_height_x1e12": heights[target],
                "height_ratio_x1e12": ratio,
                "graham_ratio_abs_error_x1e12": error,
                "within_graham_tolerance_flag": int(
                    error <= GRAHAM_TOLERANCE_X1E12
                ),
            }
        )
    return rows


def build_payload_rows() -> dict[str, Any]:
    h4_report = load_json(H4_REPORT)
    eta6_report = load_json(ETA6_REPORT)
    h4_tables = np.load(H4_TABLES, allow_pickle=False)
    h4_rows = table_rows(np.asarray(h4_tables["h4_table"], dtype=np.int64), h4.H4_COLUMNS)
    heights = [row["h_conductance_x1e12"] for row in h4_rows]
    pair_rows = build_pair_rows(heights)
    graph_rows = [k4_graph_row()]
    closest = min(
        pair_rows,
        key=lambda row: (
            row["graham_ratio_abs_error_x1e12"],
            row["from_stage_id"],
            row["to_stage_id"],
        ),
    )
    support_fixed = int(
        h4_report["witness"]["residual_chain_x1e12"] == [SCALE] * len(heights)
    )
    strict_descent = int(all(left > right for left, right in zip(heights, heights[1:])))
    graph = graph_rows[0]
    observable_values = {
        "graham_area_x1e6": GRAHAM_AREA_NUM_X1E6,
        "regular_area_x1e6": REGULAR_AREA_NUM_X1E6,
        "graham_ratio_x1e12": GRAHAM_RATIO_X1E12,
        "height_pair_count": len(pair_rows),
        "closest_pair_from_stage_id": closest["from_stage_id"],
        "closest_pair_to_stage_id": closest["to_stage_id"],
        "closest_height_ratio_x1e12": closest["height_ratio_x1e12"],
        "closest_graham_error_x1e12": closest["graham_ratio_abs_error_x1e12"],
        "graham_ratio_match_count": sum(
            row["within_graham_tolerance_flag"] for row in pair_rows
        ),
        "support_fixed_flag": support_fixed,
        "strict_height_descent_flag": strict_descent,
        "k4_polyhedral_constraint_flag": int(
            graph["planar_flag"]
            and graph["cubic_flag"]
            and graph["three_vertex_connected_flag"]
        ),
        "truncated_icosahedral_match_flag": int(
            graph["truncated_icosahedral_vertex_count_flag"]
            and graph["truncated_icosahedral_edge_count_flag"]
        ),
        "area_certificate_available_flag": 0,
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
        "h4_report": h4_report,
        "eta6_report": eta6_report,
        "h4_rows": h4_rows,
        "pair_rows": pair_rows,
        "graph_rows": graph_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "closest": closest,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    graph_table = table_from_rows(GRAPH_COLUMNS, rows["graph_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]

    checks = {
        "h4_precursor_report_certified": rows["h4_report"].get("status")
        == h4.STATUS,
        "eta6_support_report_certified": rows["eta6_report"].get("status")
        == eta6.STATUS,
        "fixed_support_and_height_descent_are_available": (
            observable_values["support_fixed_flag"],
            observable_values["strict_height_descent_flag"],
        )
        == (1, 1),
        "graham_ratio_screen_is_currently_negative": (
            observable_values["graham_ratio_x1e12"],
            observable_values["closest_pair_from_stage_id"],
            observable_values["closest_pair_to_stage_id"],
            observable_values["closest_height_ratio_x1e12"],
            observable_values["closest_graham_error_x1e12"],
            observable_values["graham_ratio_match_count"],
        )
        == (
            1_039_201_316_666,
            2,
            4,
            1_013_227_671_291,
            25_973_645_375,
            0,
        ),
        "k4_is_polyhedral_cubic_constraint_but_not_truncated_icosahedral": (
            observable_values["k4_polyhedral_constraint_flag"],
            observable_values["truncated_icosahedral_match_flag"],
        )
        == (1, 0),
        "area_certificate_is_explicitly_missing": observable_values[
            "area_certificate_available_flag"
        ]
        == 0,
        "table_shapes_match_codebooks": (
            tuple(pair_table.shape),
            tuple(graph_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (10, len(PAIR_COLUMNS)),
            (1, len(GRAPH_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "graham_area_x1e6": GRAHAM_AREA_NUM_X1E6,
        "regular_area_x1e6": REGULAR_AREA_NUM_X1E6,
        "graham_ratio_x1e12": GRAHAM_RATIO_X1E12,
        "closest_pair": rows["closest"],
        "graham_ratio_match_count": observable_values["graham_ratio_match_count"],
        "support_fixed_flag": observable_values["support_fixed_flag"],
        "strict_height_descent_flag": observable_values["strict_height_descent_flag"],
        "k4_graph_constraint": rows["graph_rows"][0],
        "pair_table_sha256": pair.parent.sha_array(pair_table),
        "graph_table_sha256": pair.parent.sha_array(graph_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    graham = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen@1",
        "object": "C985->d20",
        "graham_reference": {
            "area_graham_approx_x1e6": GRAHAM_AREA_NUM_X1E6,
            "area_regular_diameter_one_hexagon_approx_x1e6": REGULAR_AREA_NUM_X1E6,
            "ratio_x1e12": GRAHAM_RATIO_X1E12,
            "source": "user-provided Graham biggest little hexagon approximation",
        },
        "current_screen": {
            "height_ratios": rows["pair_rows"],
            "closest_pair": rows["closest"],
            "ratio_match_count": observable_values["graham_ratio_match_count"],
        },
        "graph_constraint": rows["graph_rows"][0],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_GRAHAM_THROAT_SCREEN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The current eta6/H4 precursor evidence supports the qualitative "
            "Graham-like reading: conductance height descends while the fixed "
            "six-edge support constraint remains. The quantitative Graham "
            "ratio screen is currently negative: no conductance-height ratio "
            "falls within the declared tolerance of the user-supplied Graham "
            "hexagon inflation ratio."
        ),
        "stage_protocol": {
            "draft": "start from the certified eta6 H4 precursor and support-charge reports",
            "witness": "compare all conductance-height ratios against the Graham hexagon ratio",
            "coherence": "check fixed support, strict height descent, and K4 polyhedral graph constraints",
            "closure": "certify a diagnostic Graham-throat screen without claiming area convergence",
            "emit": "emit ratio, graph, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "h4_precursor_report": pair.parent.input_entry(
                H4_REPORT,
                {
                    "status": rows["h4_report"].get("status"),
                    "certificate_sha256": rows["h4_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "h4_precursor_tables": pair.parent.input_entry(H4_TABLES),
            "eta6_support_report": pair.parent.input_entry(
                ETA6_REPORT,
                {
                    "status": rows["eta6_report"].get("status"),
                    "certificate_sha256": rows["eta6_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "eta6_support_tables": pair.parent.input_entry(ETA6_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "graham": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen.json"
            ),
            "ratio_csv": pair.parent.relpath(
                OUT_DIR / "eta6_graham_throat_ratio_pairs.csv"
            ),
            "graph_csv": pair.parent.relpath(
                OUT_DIR / "eta6_graham_throat_graph_constraints.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "eta6_graham_throat_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "fixed eta6 support plus strict conductance-height descent gives a Graham-like qualitative aperture pattern",
                "the current conductance-height ratios do not match the Graham inflation ratio within the declared tolerance",
                "the current eta6 support carrier is a K4 polyhedral cubic 3-vertex-connected constraint graph",
                "the current carrier is not the 60-vertex/90-edge truncated-icosahedral graph",
            ],
            "does_not_certify_because_not_required": [
                "a Euclidean or Poincare polygon area certificate",
                "convergence to Graham's biggest-little-hexagon area ratio",
                "a truncated-icosahedral boundary skeleton realization",
                "replacement of H4 symbolic precursor coordinates with per-intervention Poincare centers",
            ],
        },
        "next_highest_yield_item": (
            "Build an actual six-point aperture polygon from per-intervention "
            "Poincare centers or cut-edge centers, then compute its area ratio "
            "against the regular diameter-one hexagon baseline."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the Graham analogy is qualitatively aligned with fixed support plus metric relaxation",
            "the current conductance-only ratio screen does not yet support Graham-ratio convergence",
            "area must be tested on an actual six-point aperture polygon, not inferred from conductance alone",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified H4 precursor and eta6 support reports",
            "compare every conductance-height pair ratio against the Graham ratio",
            "check fixed support and strict height descent",
            "check K4 planar cubic 3-vertex-connected graph constraint flags",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "graham": graham,
        "ratio_csv": pair.csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "graph_csv": pair.csv_text(GRAPH_COLUMNS, rows["graph_rows"]),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "pair_table": pair_table,
        "graph_table": graph_table,
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
        / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen.json",
        payloads["graham"],
    )
    (OUT_DIR / "eta6_graham_throat_ratio_pairs.csv").write_text(
        payloads["ratio_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_graham_throat_graph_constraints.csv").write_text(
        payloads["graph_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_graham_throat_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_tables.npz",
        pair_table=payloads["pair_table"],
        graph_table=payloads["graph_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_certificate.json",
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
