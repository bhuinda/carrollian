from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen as barycenter
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture as nonholonomic
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen as barycenter
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture as nonholonomic
    import derive_c985_eta6_truncated_skeleton as skeleton
    from paths import D20_INVARIANTS, ROOT


pair = nonholonomic.pair

THEOREM_ID = "eta6_ext_cone"
STATUS = "ETA6_EXT_CONE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TRUNCATED_DIR = D20_INVARIANTS / "proof_obligations" / "c985_eta6_truncated_skeleton"
TRUNCATED_REPORT = TRUNCATED_DIR / "report.json"
TRUNCATED_TABLES = TRUNCATED_DIR / "eta6_truncated_skeleton_tables.npz"
NONHOLONOMIC_REPORT = nonholonomic.OUT_DIR / "report.json"
NONHOLONOMIC_TABLES = (
    nonholonomic.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_eta6_ext_cone.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_eta6_ext_cone.py"
)

SCALE = 1_000_000_000_000

VERTEX_COLUMNS = [
    "vertex_id",
    "x_x1e12",
    "y_x1e12",
    "z_x1e12",
]
FACE_SUPPORT_COLUMNS = [
    "face_id",
    "face_type_code",
    "face_size",
    "normal_x_x1e12",
    "normal_y_x1e12",
    "normal_z_x1e12",
    "offset_x1e12",
    "nonface_vertex_count",
    "min_slack_x1e12",
    "max_slack_x1e12",
    "positive_slack_count",
    "zero_slack_count",
]
SLACK_COLUMNS = [
    "slack_row_id",
    "face_id",
    "vertex_id",
    "face_type_code",
    "face_size",
    "slack_x1e12",
    "positive_flag",
    "discriminant_equal_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "coordinate_vertex_count": 0,
    "face_count": 1,
    "pentagon_face_count": 2,
    "hexagon_face_count": 3,
    "support_inequality_count": 4,
    "positive_slack_count": 5,
    "zero_slack_count": 6,
    "min_slack_x1e12": 7,
    "max_slack_x1e12": 8,
    "positive_support_cone_flag": 9,
    "current_discriminant_intersection_flag": 10,
    "support_matrix_available_flag": 11,
    "affine_circuit_gordan_certificate_available_flag": 12,
    "nonholonomic_prior_exterior_matrix_available_flag": 13,
    "nonholonomic_prior_positive_proxy_flag": 14,
    "surgery_certificate_available_flag": 15,
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


def build_truncated_coordinates(
    vertex_rows: list[dict[str, int]],
) -> dict[int, np.ndarray]:
    graph = skeleton.load_public_d20_graph()
    derived = skeleton.build_dual_and_truncation(graph)
    standard = barycenter.standard_icosahedron()
    iso = barycenter.dual_icosahedron_isomorphism(derived["dual_edge_pairs"])
    dual_coords = {
        dual_id: standard["coords"][target_id]
        for dual_id, target_id in enumerate(iso)
    }
    return {
        row["vertex_id"]: (
            2.0 * dual_coords[row["center_dual_vertex_id"]]
            + dual_coords[row["neighbor_dual_vertex_id"]]
        )
        / 3.0
        for row in vertex_rows
    }


def scaled(value: float) -> int:
    return int(round(float(value) * SCALE))


def face_cycle(row: dict[str, int]) -> list[int]:
    return [row[f"cycle_v{index}"] for index in range(row["face_size"])]


def oriented_face_support(
    cycle: list[int],
    coords: dict[int, np.ndarray],
    origin: np.ndarray,
) -> tuple[np.ndarray, float]:
    points = np.asarray([coords[vertex_id] for vertex_id in cycle], dtype=np.float64)
    center = np.mean(points, axis=0)
    normal = np.zeros(3, dtype=np.float64)
    for index, point in enumerate(points):
        normal += np.cross(point - center, points[(index + 1) % len(points)] - center)
    norm = float(np.linalg.norm(normal))
    if norm == 0.0:
        raise ValueError(f"degenerate face cycle {cycle}")
    normal = normal / norm
    if float(np.dot(normal, center - origin)) < 0.0:
        normal = -normal
    offset = float(np.dot(normal, center))
    return normal, offset


def build_support_rows(
    face_rows: list[dict[str, int]],
    coords: dict[int, np.ndarray],
) -> dict[str, Any]:
    origin = np.mean(np.asarray(list(coords.values()), dtype=np.float64), axis=0)
    face_support_rows = []
    slack_rows = []
    slack_row_id = 0
    for face in face_rows:
        cycle = face_cycle(face)
        cycle_set = set(cycle)
        normal, offset = oriented_face_support(cycle, coords, origin)
        face_slacks = []
        for vertex_id in sorted(coords):
            if vertex_id in cycle_set:
                continue
            slack = offset - float(np.dot(normal, coords[vertex_id]))
            slack_x1e12 = scaled(slack)
            face_slacks.append(slack_x1e12)
            slack_rows.append(
                {
                    "slack_row_id": slack_row_id,
                    "face_id": face["face_id"],
                    "vertex_id": vertex_id,
                    "face_type_code": face["face_type_code"],
                    "face_size": face["face_size"],
                    "slack_x1e12": slack_x1e12,
                    "positive_flag": int(slack_x1e12 > 0),
                    "discriminant_equal_flag": int(slack_x1e12 == 0),
                }
            )
            slack_row_id += 1
        face_support_rows.append(
            {
                "face_id": face["face_id"],
                "face_type_code": face["face_type_code"],
                "face_size": face["face_size"],
                "normal_x_x1e12": scaled(normal[0]),
                "normal_y_x1e12": scaled(normal[1]),
                "normal_z_x1e12": scaled(normal[2]),
                "offset_x1e12": scaled(offset),
                "nonface_vertex_count": len(face_slacks),
                "min_slack_x1e12": min(face_slacks),
                "max_slack_x1e12": max(face_slacks),
                "positive_slack_count": sum(value > 0 for value in face_slacks),
                "zero_slack_count": sum(value == 0 for value in face_slacks),
            }
        )
    return {
        "face_support_rows": face_support_rows,
        "slack_rows": slack_rows,
    }


def build_payload_rows() -> dict[str, Any]:
    truncated_report = load_json(TRUNCATED_REPORT)
    nonholonomic_report = load_json(NONHOLONOMIC_REPORT)
    truncated_tables = np.load(TRUNCATED_TABLES, allow_pickle=False)
    vertex_rows = table_rows(
        np.asarray(truncated_tables["vertex_table"], dtype=np.int64),
        skeleton.TRUNCATED_VERTEX_COLUMNS,
    )
    face_rows = table_rows(
        np.asarray(truncated_tables["face_table"], dtype=np.int64),
        skeleton.TRUNCATED_FACE_COLUMNS,
    )
    coords = build_truncated_coordinates(vertex_rows)
    coordinate_rows = [
        {
            "vertex_id": vertex_id,
            "x_x1e12": scaled(coord[0]),
            "y_x1e12": scaled(coord[1]),
            "z_x1e12": scaled(coord[2]),
        }
        for vertex_id, coord in sorted(coords.items())
    ]
    support = build_support_rows(face_rows, coords)
    slack_values = [row["slack_x1e12"] for row in support["slack_rows"]]
    nonholonomic_witness = nonholonomic_report["witness"]["open_seams"]
    observable_values = {
        "coordinate_vertex_count": len(coordinate_rows),
        "face_count": len(face_rows),
        "pentagon_face_count": sum(row["face_type_code"] == 0 for row in face_rows),
        "hexagon_face_count": sum(row["face_type_code"] == 1 for row in face_rows),
        "support_inequality_count": len(support["slack_rows"]),
        "positive_slack_count": sum(value > 0 for value in slack_values),
        "zero_slack_count": sum(value == 0 for value in slack_values),
        "min_slack_x1e12": min(slack_values),
        "max_slack_x1e12": max(slack_values),
        "positive_support_cone_flag": int(all(value > 0 for value in slack_values)),
        "current_discriminant_intersection_flag": int(
            any(value == 0 for value in slack_values)
        ),
        "support_matrix_available_flag": 1,
        "affine_circuit_gordan_certificate_available_flag": 0,
        "nonholonomic_prior_exterior_matrix_available_flag": int(
            nonholonomic_witness["exterior_circuit_matrix_available"]
        ),
        "nonholonomic_prior_positive_proxy_flag": int(
            nonholonomic_witness["positive_cone_is_conductance_height_proxy"]
        ),
        "surgery_certificate_available_flag": int(
            nonholonomic_witness["surgery_certificate_available"]
        ),
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
        "truncated_report": truncated_report,
        "nonholonomic_report": nonholonomic_report,
        "coordinate_rows": coordinate_rows,
        "face_support_rows": support["face_support_rows"],
        "slack_rows": support["slack_rows"],
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    vertex_table = table_from_rows(VERTEX_COLUMNS, rows["coordinate_rows"])
    face_support_table = table_from_rows(
        FACE_SUPPORT_COLUMNS,
        rows["face_support_rows"],
    )
    slack_table = table_from_rows(SLACK_COLUMNS, rows["slack_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]

    checks = {
        "input_reports_are_certified": (
            rows["truncated_report"].get("status"),
            rows["nonholonomic_report"].get("status"),
        )
        == (skeleton.STATUS, nonholonomic.STATUS),
        "lifted_boundary_coordinate_scope_matches_60_90_32": (
            observable_values["coordinate_vertex_count"],
            observable_values["face_count"],
            observable_values["pentagon_face_count"],
            observable_values["hexagon_face_count"],
        )
        == (60, 32, 12, 20),
        "support_slack_matrix_is_strictly_positive": (
            observable_values["support_inequality_count"],
            observable_values["positive_slack_count"],
            observable_values["zero_slack_count"],
            observable_values["positive_support_cone_flag"],
            observable_values["current_discriminant_intersection_flag"],
            observable_values["min_slack_x1e12"],
        )
        == (1_740, 1_740, 0, 1, 0, 350_487_408_079),
        "max_slack_matches_convex_truncated_coordinate_witness": observable_values[
            "max_slack_x1e12"
        ]
        == 3_103_251_249_022,
        "nonholonomic_open_seam_is_refined_but_not_closed": (
            observable_values["support_matrix_available_flag"],
            observable_values["affine_circuit_gordan_certificate_available_flag"],
            observable_values["nonholonomic_prior_exterior_matrix_available_flag"],
            observable_values["nonholonomic_prior_positive_proxy_flag"],
            observable_values["surgery_certificate_available_flag"],
        )
        == (1, 0, 0, 1, 0),
        "table_shapes_match_codebooks": (
            tuple(vertex_table.shape),
            tuple(face_support_table.shape),
            tuple(slack_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (60, len(VERTEX_COLUMNS)),
            (32, len(FACE_SUPPORT_COLUMNS)),
            (1_740, len(SLACK_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "coordinate_model": (
            "standard icosahedron coordinates pulled back through the "
            "certified dual graph and truncated at one-third edge positions"
        ),
        "support_slack_matrix": {
            "row_count": observable_values["support_inequality_count"],
            "positive_row_count": observable_values["positive_slack_count"],
            "zero_row_count": observable_values["zero_slack_count"],
            "min_slack_x1e12": observable_values["min_slack_x1e12"],
            "max_slack_x1e12": observable_values["max_slack_x1e12"],
        },
        "boundary_face_split": {
            "pentagons": observable_values["pentagon_face_count"],
            "hexagons": observable_values["hexagon_face_count"],
        },
        "open_seams": {
            "support_matrix_available": True,
            "affine_circuit_gordan_certificate_available": False,
            "surgery_certificate_available": False,
        },
        "vertex_table_sha256": pair.parent.sha_array(vertex_table),
        "face_support_table_sha256": pair.parent.sha_array(face_support_table),
        "slack_table_sha256": pair.parent.sha_array(slack_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    support_cone = {
        "schema": "eta6.ext_cone@1",
        "object": "C985->d20",
        "construction": {
            "carrier": "certified lifted 60/90/32 truncated boundary skeleton",
            "coordinate_model": witness["coordinate_model"],
            "support_matrix": (
                "one support inequality for each face/non-face vertex pair: "
                "b_f - <n_f, x_v> > 0"
            ),
            "discriminant": "union of support hyperplanes where any support slack equals zero",
        },
        "witness": witness,
    }

    report = {
        "schema": "eta6.ext_cone.report@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_EXTERIOR_SUPPORT_CONE_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The lifted 60/90/32 boundary carrier admits a concrete convex "
            "exterior support-slack matrix. Across all 1,740 face/non-face "
            "support inequalities, every slack is strictly positive; the "
            "minimum slack is 350487408079/1e12. Thus the current lifted "
            "carrier is inside a certified support-positive cone and does not "
            "intersect the support discriminant. This refines the prior "
            "conductance-height proxy, while the full affine-circuit/Gordan "
            "certificate and surgery continuation remain open seams."
        ),
        "stage_protocol": {
            "draft": "start from the certified lifted truncated skeleton and nonholonomic aperture report",
            "witness": "realize the 60 vertices using standard icosahedral coordinates and build face support planes",
            "coherence": "check every non-face vertex has positive slack against every face support plane",
            "closure": "certify a support-positive cone and explicit support discriminant equation",
            "emit": "emit vertex, face-support, slack, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "truncated_skeleton_report": pair.parent.input_entry(
                TRUNCATED_REPORT,
                {
                    "status": rows["truncated_report"].get("status"),
                    "certificate_sha256": rows["truncated_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "truncated_skeleton_tables": pair.parent.input_entry(TRUNCATED_TABLES),
            "nonholonomic_aperture_report": pair.parent.input_entry(
                NONHOLONOMIC_REPORT,
                {
                    "status": rows["nonholonomic_report"].get("status"),
                    "certificate_sha256": rows["nonholonomic_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "nonholonomic_aperture_tables": pair.parent.input_entry(
                NONHOLONOMIC_TABLES
            ),
            "coordinate_helper_script": pair.parent.input_entry(
                barycenter.DERIVE_SCRIPT
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "support_cone": pair.parent.relpath(
                OUT_DIR / "ext_cone.json"
            ),
            "vertices_csv": pair.parent.relpath(
                OUT_DIR / "vertices.csv"
            ),
            "faces_csv": pair.parent.relpath(
                OUT_DIR / "faces.csv"
            ),
            "slacks_csv": pair.parent.relpath(
                OUT_DIR / "slacks.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "obs.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR / "tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR / "cert.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a concrete 60-vertex coordinate realization for the lifted truncated boundary carrier",
                "a support-slack exterior matrix with 1,740 strictly positive face/non-face inequalities",
                "the current lifted carrier avoids the support discriminant where any support slack is zero",
                "the conductance-height proxy has been refined to a convex support-positive cone witness",
            ],
            "does_not_certify_because_not_required": [
                "the full affine-dependency exterior circuit matrix A_ext from all exterior cells",
                "Gordan-dual infeasibility of positive affine dependences",
                "a surgery move crossing the eta6 aperture stratum",
                "commutator or bracket closure of the complete F-symbol distribution",
            ],
        },
        "next_highest_yield_item": (
            "Upgrade the support-slack matrix to the full affine-circuit "
            "A_ext/Gordan certificate: enumerate minimal exterior affine "
            "circuits and certify no nonzero y >= 0 solves A_ext^T y = 0."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "eta6.ext_cone.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the lifted 60/90 carrier has a concrete strict convex support witness",
            "the support discriminant is explicit as slack equals zero and is avoided by the current realization",
            "the next missing layer is the full affine-circuit/Gordan dual certificate",
        ],
    }

    manifest = {
        "schema": "eta6.ext_cone.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified truncated skeleton and nonholonomic aperture reports",
            "build deterministic truncated-icosahedral coordinates from the dual icosahedron",
            "compute support planes for all 32 faces",
            "evaluate all 1,740 face/non-face support slacks",
            "check strict positivity and zero support-discriminant intersection",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "support_cone": support_cone,
        "vertices_csv": pair.csv_text(VERTEX_COLUMNS, rows["coordinate_rows"]),
        "faces_csv": pair.csv_text(
            FACE_SUPPORT_COLUMNS,
            rows["face_support_rows"],
        ),
        "slacks_csv": pair.csv_text(SLACK_COLUMNS, rows["slack_rows"]),
        "observables_csv": pair.csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "vertex_table": vertex_table,
        "face_support_table": face_support_table,
        "slack_table": slack_table,
        "observable_table": observable_table,
        "certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = nonholonomic.preservation.INDEX_PATH
    if index_path.exists():
        index_payload = load_json(index_path)
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
    pair.parent.write_json(index_path, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(
        OUT_DIR / "ext_cone.json",
        payloads["support_cone"],
    )
    (OUT_DIR / "vertices.csv").write_text(
        payloads["vertices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "faces.csv").write_text(
        payloads["faces_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "slacks.csv").write_text(
        payloads["slacks_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "obs.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        vertex_table=payloads["vertex_table"],
        face_support_table=payloads["face_support_table"],
        slack_table=payloads["slack_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR / "cert.json",
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
