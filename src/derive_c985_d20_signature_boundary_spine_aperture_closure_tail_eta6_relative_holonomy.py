from __future__ import annotations

import json
from itertools import combinations, product
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge as eta6_charge
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge as eta6_charge
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = eta6_charge.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_RELATIVE_HOLONOMY_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

ETA6_REPORT = eta6_charge.OUT_DIR / "report.json"
ETA6_TABLES = (
    eta6_charge.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_tables.npz"
)
ETA6_JSON = (
    eta6_charge.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy.py"
)

EDGE_BASIS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
FACE_BASIS = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
EDGE_CODES = [1, 2, 3, 12, 13, 23]

EDGE_COLUMNS = [
    "edge_basis_id",
    "edge_code",
    "vertex_u",
    "vertex_v",
    "eta6_coeff",
    "holonomy_coeff",
    "relative_boundary_q0",
    "relative_boundary_q1",
    "relative_boundary_q2",
    "absolute_boundary_v0",
    "absolute_boundary_v1",
    "absolute_boundary_v2",
    "absolute_boundary_v3",
]
FACE_COLUMNS = [
    "face_id",
    "face_code",
    "edge_01",
    "edge_02",
    "edge_03",
    "edge_12",
    "edge_13",
    "edge_23",
    "holonomy_face_pairing",
]
OPPOSITE_PAIR_COLUMNS = [
    "opposite_pair_id",
    "edge_code_a",
    "edge_code_b",
    "relative_boundary_q0",
    "relative_boundary_q1",
    "relative_boundary_q2",
    "eta6_pair_coeff",
    "holonomy_pairing",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "edge_count": 0,
    "face_count": 1,
    "relative_boundary_rank": 2,
    "face_boundary_rank": 3,
    "relative_cycle_space_dimension": 4,
    "relative_h1_dimension": 5,
    "relative_cohomology_dimension": 6,
    "eta6_relative_boundary_weight": 7,
    "eta6_absolute_boundary_weight": 8,
    "eta6_in_face_boundary_image_flag": 9,
    "eta6_relative_class_nonzero_flag": 10,
    "holonomy_cocycle_flag": 11,
    "holonomy_coboundary_flag": 12,
    "holonomy_eta6_pairing": 13,
    "opposite_pair_relative_cycle_count": 14,
    "eta6_report_preserved_rows": 15,
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


def rank_gf2(matrix: np.ndarray) -> int:
    reduced = np.asarray(matrix, dtype=np.uint8).copy() % 2
    row_count, column_count = reduced.shape
    rank = 0
    for column in range(column_count):
        pivot = None
        for row in range(rank, row_count):
            if reduced[row, column]:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
        for row in range(row_count):
            if row != rank and reduced[row, column]:
                reduced[row] ^= reduced[rank]
        rank += 1
        if rank == row_count:
            break
    return rank


def in_span_gf2(vector: np.ndarray, columns: np.ndarray) -> bool:
    matrix = np.asarray(columns, dtype=np.uint8) % 2
    augmented = np.column_stack([matrix, np.asarray(vector, dtype=np.uint8) % 2])
    return rank_gf2(augmented) == rank_gf2(matrix)


def quotient_vertex_vector(vertex: int) -> np.ndarray:
    if vertex == 0:
        return np.asarray([1, 0, 0], dtype=np.uint8)
    if vertex == 1:
        return np.asarray([0, 1, 0], dtype=np.uint8)
    if vertex == 2:
        return np.asarray([0, 0, 1], dtype=np.uint8)
    return np.asarray([1, 1, 1], dtype=np.uint8)


def build_relative_boundary_matrix() -> np.ndarray:
    return np.stack(
        [quotient_vertex_vector(u) ^ quotient_vertex_vector(v) for u, v in EDGE_BASIS],
        axis=1,
    )


def build_absolute_boundary_matrix() -> np.ndarray:
    matrix = np.zeros((4, len(EDGE_BASIS)), dtype=np.uint8)
    for edge_id, (u, v) in enumerate(EDGE_BASIS):
        matrix[u, edge_id] = 1
        matrix[v, edge_id] = 1
    return matrix


def build_face_boundary_matrix() -> np.ndarray:
    edge_index = {edge: index for index, edge in enumerate(EDGE_BASIS)}
    matrix = np.zeros((len(EDGE_BASIS), len(FACE_BASIS)), dtype=np.uint8)
    for face_id, face in enumerate(FACE_BASIS):
        for edge in combinations(face, 2):
            matrix[edge_index[tuple(sorted(edge))], face_id] = 1
    return matrix


def kernel_size_gf2(matrix: np.ndarray) -> int:
    return 2 ** (matrix.shape[1] - rank_gf2(matrix))


def build_edge_rows(
    relative_boundary: np.ndarray,
    absolute_boundary: np.ndarray,
    eta_vector: np.ndarray,
    holonomy_vector: np.ndarray,
) -> list[dict[str, int]]:
    rows = []
    for edge_id, (u, v) in enumerate(EDGE_BASIS):
        rows.append(
            {
                "edge_basis_id": edge_id,
                "edge_code": EDGE_CODES[edge_id],
                "vertex_u": u,
                "vertex_v": v,
                "eta6_coeff": int(eta_vector[edge_id]),
                "holonomy_coeff": int(holonomy_vector[edge_id]),
                "relative_boundary_q0": int(relative_boundary[0, edge_id]),
                "relative_boundary_q1": int(relative_boundary[1, edge_id]),
                "relative_boundary_q2": int(relative_boundary[2, edge_id]),
                "absolute_boundary_v0": int(absolute_boundary[0, edge_id]),
                "absolute_boundary_v1": int(absolute_boundary[1, edge_id]),
                "absolute_boundary_v2": int(absolute_boundary[2, edge_id]),
                "absolute_boundary_v3": int(absolute_boundary[3, edge_id]),
            }
        )
    return rows


def build_face_rows(
    face_boundary: np.ndarray,
    holonomy_vector: np.ndarray,
) -> list[dict[str, int]]:
    rows = []
    for face_id, face in enumerate(FACE_BASIS):
        column = face_boundary[:, face_id]
        rows.append(
            {
                "face_id": face_id,
                "face_code": int("".join(str(vertex) for vertex in face)),
                "edge_01": int(column[0]),
                "edge_02": int(column[1]),
                "edge_03": int(column[2]),
                "edge_12": int(column[3]),
                "edge_13": int(column[4]),
                "edge_23": int(column[5]),
                "holonomy_face_pairing": int(np.dot(holonomy_vector, column) % 2),
            }
        )
    return rows


def build_opposite_pair_rows(
    relative_boundary: np.ndarray,
    eta_vector: np.ndarray,
    holonomy_vector: np.ndarray,
) -> list[dict[str, int]]:
    pairs = [(0, 5), (1, 4), (2, 3)]
    rows = []
    for pair_id, (edge_a, edge_b) in enumerate(pairs):
        vector = np.zeros(len(EDGE_BASIS), dtype=np.uint8)
        vector[edge_a] = 1
        vector[edge_b] = 1
        boundary = relative_boundary @ vector % 2
        rows.append(
            {
                "opposite_pair_id": pair_id,
                "edge_code_a": EDGE_CODES[edge_a],
                "edge_code_b": EDGE_CODES[edge_b],
                "relative_boundary_q0": int(boundary[0]),
                "relative_boundary_q1": int(boundary[1]),
                "relative_boundary_q2": int(boundary[2]),
                "eta6_pair_coeff": int(np.dot(eta_vector, vector) % 2),
                "holonomy_pairing": int(np.dot(holonomy_vector, vector) % 2),
            }
        )
    return rows


def eta6_preserved_rows() -> int:
    tables = np.load(ETA6_TABLES, allow_pickle=False)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    observables = {int(row[1]): int(row[2]) for row in observable_table}
    return observables[
        eta6_charge.OBSERVABLE_CODES["preservation_aggregate_row_count"]
    ]


def build_payload_rows() -> dict[str, Any]:
    eta6_report = load_json(ETA6_REPORT)
    eta6_json = load_json(ETA6_JSON)
    relative_boundary = build_relative_boundary_matrix()
    absolute_boundary = build_absolute_boundary_matrix()
    face_boundary = build_face_boundary_matrix()
    eta_vector = np.ones(len(EDGE_BASIS), dtype=np.uint8)
    holonomy_vector = np.asarray([0, 0, 1, 0, 1, 1], dtype=np.uint8)
    relative_eta_boundary = relative_boundary @ eta_vector % 2
    absolute_eta_boundary = absolute_boundary @ eta_vector % 2
    coboundary_matrix = relative_boundary.T
    relative_cycle_dimension = len(EDGE_BASIS) - rank_gf2(relative_boundary)
    relative_h1_dimension = relative_cycle_dimension - rank_gf2(face_boundary)
    cocycle_dimension = len(EDGE_BASIS) - rank_gf2(face_boundary.T)
    relative_cohomology_dimension = cocycle_dimension - rank_gf2(coboundary_matrix)

    observable_values = {
        "edge_count": len(EDGE_BASIS),
        "face_count": len(FACE_BASIS),
        "relative_boundary_rank": rank_gf2(relative_boundary),
        "face_boundary_rank": rank_gf2(face_boundary),
        "relative_cycle_space_dimension": relative_cycle_dimension,
        "relative_h1_dimension": relative_h1_dimension,
        "relative_cohomology_dimension": relative_cohomology_dimension,
        "eta6_relative_boundary_weight": int(relative_eta_boundary.sum()),
        "eta6_absolute_boundary_weight": int(absolute_eta_boundary.sum()),
        "eta6_in_face_boundary_image_flag": int(
            in_span_gf2(eta_vector, face_boundary)
        ),
        "eta6_relative_class_nonzero_flag": int(
            not in_span_gf2(eta_vector, face_boundary)
            and int(relative_eta_boundary.sum()) == 0
        ),
        "holonomy_cocycle_flag": int(
            np.all((face_boundary.T @ holonomy_vector) % 2 == 0)
        ),
        "holonomy_coboundary_flag": int(
            in_span_gf2(holonomy_vector, coboundary_matrix)
        ),
        "holonomy_eta6_pairing": int(np.dot(holonomy_vector, eta_vector) % 2),
        "opposite_pair_relative_cycle_count": 3,
        "eta6_report_preserved_rows": eta6_preserved_rows(),
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
        "eta6_report": eta6_report,
        "eta6_json": eta6_json,
        "relative_boundary": relative_boundary,
        "absolute_boundary": absolute_boundary,
        "face_boundary": face_boundary,
        "eta_vector": eta_vector,
        "holonomy_vector": holonomy_vector,
        "edge_rows": build_edge_rows(
            relative_boundary,
            absolute_boundary,
            eta_vector,
            holonomy_vector,
        ),
        "face_rows": build_face_rows(face_boundary, holonomy_vector),
        "opposite_pair_rows": build_opposite_pair_rows(
            relative_boundary,
            eta_vector,
            holonomy_vector,
        ),
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    face_table = table_from_rows(FACE_COLUMNS, rows["face_rows"])
    opposite_pair_table = table_from_rows(
        OPPOSITE_PAIR_COLUMNS,
        rows["opposite_pair_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]

    checks = {
        "eta6_support_charge_report_certified": rows["eta6_report"].get("status")
        == eta6_charge.STATUS,
        "eta6_json_edge_support_matches_k4": rows["eta6_json"]
        .get("definition", {})
        .get("edge_codes")
        == EDGE_CODES,
        "relative_boundary_complex_has_expected_ranks": (
            observable_values["relative_boundary_rank"],
            observable_values["face_boundary_rank"],
            observable_values["relative_cycle_space_dimension"],
            observable_values["relative_h1_dimension"],
            observable_values["relative_cohomology_dimension"],
        )
        == (2, 3, 4, 1, 1),
        "eta6_is_relative_cycle_not_absolute_cycle": (
            observable_values["eta6_relative_boundary_weight"],
            observable_values["eta6_absolute_boundary_weight"],
        )
        == (0, 4),
        "eta6_relative_class_is_nonzero": (
            observable_values["eta6_in_face_boundary_image_flag"],
            observable_values["eta6_relative_class_nonzero_flag"],
        )
        == (0, 1),
        "holonomy_dual_is_nontrivial_and_detects_eta6": (
            observable_values["holonomy_cocycle_flag"],
            observable_values["holonomy_coboundary_flag"],
            observable_values["holonomy_eta6_pairing"],
        )
        == (1, 0, 1),
        "opposite_edge_pairs_are_relative_cycles": all(
            row["relative_boundary_q0"] == 0
            and row["relative_boundary_q1"] == 0
            and row["relative_boundary_q2"] == 0
            for row in rows["opposite_pair_rows"]
        ),
        "eta6_preservation_link_is_current": observable_values[
            "eta6_report_preserved_rows"
        ]
        == 606,
        "table_shapes_match_codebooks": (
            tuple(edge_table.shape),
            tuple(face_table.shape),
            tuple(opposite_pair_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (6, len(EDGE_COLUMNS)),
            (4, len(FACE_COLUMNS)),
            (3, len(OPPOSITE_PAIR_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "edge_basis_codes": EDGE_CODES,
        "eta6_vector": [int(value) for value in rows["eta_vector"]],
        "holonomy_vector": [int(value) for value in rows["holonomy_vector"]],
        "relative_h1_dimension": observable_values["relative_h1_dimension"],
        "relative_cohomology_dimension": observable_values[
            "relative_cohomology_dimension"
        ],
        "holonomy_eta6_pairing": observable_values["holonomy_eta6_pairing"],
        "eta6_preserved_rows": observable_values["eta6_report_preserved_rows"],
        "edge_table_sha256": pair.parent.sha_array(edge_table),
        "face_table_sha256": pair.parent.sha_array(face_table),
        "opposite_pair_table_sha256": pair.parent.sha_array(opposite_pair_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    holonomy = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy@1",
        "object": "C985->d20",
        "parent": ETA6_REPORT.relative_to(ROOT).as_posix(),
        "relative_complex": {
            "coefficient_field": "F2",
            "c1_edge_basis": EDGE_CODES,
            "c2_face_basis": [12, 13, 23, 123],
            "c0_quotient": "K4 vertices modulo v0+v1+v2+v3",
            "relative_h1_dimension": observable_values["relative_h1_dimension"],
            "relative_cohomology_dimension": observable_values[
                "relative_cohomology_dimension"
            ],
        },
        "eta6_class": {
            "eta6_vector": [int(value) for value in rows["eta_vector"]],
            "relative_boundary_weight": observable_values[
                "eta6_relative_boundary_weight"
            ],
            "absolute_boundary_weight": observable_values[
                "eta6_absolute_boundary_weight"
            ],
            "nonzero_relative_class": bool(
                observable_values["eta6_relative_class_nonzero_flag"]
            ),
        },
        "dual_holonomy": {
            "representative": "star at quotient vertex 3: edges 03,13,23",
            "holonomy_vector": [int(value) for value in rows["holonomy_vector"]],
            "cocycle": bool(observable_values["holonomy_cocycle_flag"]),
            "coboundary": bool(observable_values["holonomy_coboundary_flag"]),
            "eta6_pairing": observable_values["holonomy_eta6_pairing"],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_RELATIVE_HOLONOMY_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6 support charge has a one-dimensional relative homology "
            "and cohomology presentation over F2 after quotienting K4 vertex "
            "boundaries by v0+v1+v2+v3. eta6 is a relative cycle, is not a "
            "face boundary, and is detected by a nontrivial dual holonomy "
            "represented by the vertex-3 star cochain."
        ),
        "stage_protocol": {
            "draft": "start from the certified eta6 support-charge layer",
            "witness": "construct K4 edge, face, relative-boundary, and dual-holonomy matrices",
            "coherence": "compute GF(2) ranks, relative cycle status, face-boundary membership, and dual pairing",
            "closure": "certify eta6 as a nonzero relative class with nontrivial dual holonomy",
            "emit": "emit relative chain tables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "eta6_report": pair.parent.input_entry(
                ETA6_REPORT,
                {
                    "status": rows["eta6_report"].get("status"),
                    "certificate_sha256": rows["eta6_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "eta6_tables": pair.parent.input_entry(ETA6_TABLES),
            "eta6_json": pair.parent.input_entry(ETA6_JSON),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "holonomy": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy.json"
            ),
            "edge_basis_csv": pair.parent.relpath(
                OUT_DIR / "eta6_relative_edge_basis.csv"
            ),
            "face_boundary_csv": pair.parent.relpath(
                OUT_DIR / "eta6_relative_face_boundaries.csv"
            ),
            "opposite_pair_csv": pair.parent.relpath(
                OUT_DIR / "eta6_relative_opposite_pair_cycles.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "eta6_relative_holonomy_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "eta6 is a nonzero relative H1 class over F2 in the K4 quotient model",
                "eta6 is a relative cycle but not an absolute cycle",
                "eta6 is not in the face-boundary image",
                "a nontrivial dual holonomy cochain evaluates to 1 on eta6",
            ],
            "does_not_certify_because_not_required": [
                "integer or real-valued cohomology beyond the F2 support class",
                "Dini torsion or H4 lift coordinates",
                "cyclic/dihedral six-window intervention closure",
                "full rigidity under complete associator geometry",
            ],
        },
        "next_highest_yield_item": (
            "Use the eta6 holonomy class as the base for Dini torsion: compare "
            "conductance descent against the fixed nontrivial holonomy pairing."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "eta6 is a relative cycle only after quotienting the total K4 boundary",
            "eta6 generates a one-dimensional F2 relative support class",
            "the vertex-3 star cochain is a nontrivial holonomy detector for eta6",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified eta6 support-charge report",
            "build K4 edge, face, relative-boundary, and cochain matrices over F2",
            "check eta6 relative-cycle status and non-boundary status",
            "check dual holonomy cocycle, non-coboundary status, and eta6 pairing",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "holonomy": holonomy,
        "edge_basis_csv": pair.csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "face_boundary_csv": pair.csv_text(FACE_COLUMNS, rows["face_rows"]),
        "opposite_pair_csv": pair.csv_text(
            OPPOSITE_PAIR_COLUMNS,
            rows["opposite_pair_rows"],
        ),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "edge_table": edge_table,
        "face_table": face_table,
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
        / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy.json",
        payloads["holonomy"],
    )
    (OUT_DIR / "eta6_relative_edge_basis.csv").write_text(
        payloads["edge_basis_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_relative_face_boundaries.csv").write_text(
        payloads["face_boundary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_relative_opposite_pair_cycles.csv").write_text(
        payloads["opposite_pair_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_relative_holonomy_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_tables.npz",
        edge_table=payloads["edge_table"],
        face_table=payloads["face_table"],
        opposite_pair_table=payloads["opposite_pair_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_certificate.json",
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
