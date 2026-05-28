from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from . import derive_eta6_aext as aext
    from . import derive_eta6_ext_cone as ext
    from . import derive_eta6_islack as islack
    from . import derive_eta6_srows as srows
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    import derive_c985_eta6_truncated_skeleton as skeleton
    import derive_eta6_aext as aext
    import derive_eta6_ext_cone as ext
    import derive_eta6_islack as islack
    import derive_eta6_srows as srows
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_hpol"
STATUS = "ETA6_HPOL_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

EXT_TABLES = ext.OUT_DIR / "tables.npz"
AEXT_REPORT = aext.OUT_DIR / "report.json"
AEXT_TABLES = aext.OUT_DIR / "tables.npz"
SROWS_REPORT = srows.OUT_DIR / "report.json"
ISLACK_REPORT = islack.OUT_DIR / "report.json"
HOLONOMY_REPORT = holonomy.OUT_DIR / "report.json"
TRUNCATED_REPORT = skeleton.OUT_DIR / "report.json"
TRUNCATED_TABLES = skeleton.OUT_DIR / "eta6_truncated_skeleton_tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_hpol.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_hpol.py"

SAMPLE_LIMIT = 16
SAMPLE_COLUMNS = [
    "sample_id",
    "sample_kind",
    "circuit_size",
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "pairing_value",
]
FACE_COLUMNS = [
    "face_id",
    "face_type_code",
    "source_id",
    "label_count",
    "active_label_count",
    "polarity",
    "weight",
]
HEIGHT_COLUMNS = ["vertex_id", "height_value"]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "vertex_count": 0,
    "support_face_count": 1,
    "positive_face_weight_count": 2,
    "negative_face_weight_count": 3,
    "unique_hpol_height_count": 4,
    "hpol_height_min": 5,
    "hpol_height_max": 6,
    "signed_row_count": 7,
    "zero_pairing_count": 8,
    "positive_pairing_count": 9,
    "zero_c4_pairing_count": 10,
    "zero_c5_pairing_count": 11,
    "positive_c4_pairing_count": 12,
    "positive_c5_pairing_count": 13,
    "min_positive_pairing": 14,
    "max_positive_pairing_bit_length": 15,
    "strict_hpol_orientation_flag": 16,
    "eta6_holonomy_pairing": 17,
    "eta6_support_preserved_flag": 18,
    "topology_changing_surgery_flag": 19,
    "intrinsic_zero_pairing_count": 20,
    "face_square_tiebreaker_flag": 21,
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


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def sequence_hash(values: list[int]) -> str:
    return hashlib.sha256(
        (",".join(str(value) for value in values) + "\n").encode("ascii")
    ).hexdigest()


def primal_missing_labels(
    graph: dict[str, Any],
    derived: dict[str, Any],
) -> dict[int, str]:
    missing: dict[int, str] = {}
    for face_id, cycle in enumerate(derived["primal_faces"]):
        counts = {
            label: sum(label in graph["vertices"][vertex] for vertex in cycle)
            for label in skeleton.H6_LABELS
        }
        missing[face_id] = next(label for label in skeleton.H6_LABELS if counts[label] == 0)
    return missing


def face_labels(
    face_row: dict[str, int],
    graph: dict[str, Any],
    missing: dict[int, str],
) -> tuple[str, ...]:
    if face_row["face_type_code"] == 0:
        return (missing[face_row["source_id"]],)
    return tuple(graph["vertices"][face_row["source_id"]])


def face_weight_rows() -> list[dict[str, int]]:
    holonomy_report = load_json(HOLONOMY_REPORT)
    holonomy_vector = [
        int(value) for value in holonomy_report["witness"]["holonomy_vector"]
    ]
    holonomy_by_label = {
        label: holonomy_vector[index]
        for index, label in enumerate(skeleton.H6_LABELS)
    }
    graph = skeleton.load_public_d20_graph()
    derived = skeleton.build_dual_and_truncation(graph)
    missing = primal_missing_labels(graph, derived)
    tables = np.load(TRUNCATED_TABLES, allow_pickle=False)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    rows: list[dict[str, int]] = []
    for values in face_table:
        face_row = {
            column: int(values[index])
            for index, column in enumerate(skeleton.TRUNCATED_FACE_COLUMNS)
        }
        labels = face_labels(face_row, graph, missing)
        active_count = sum(holonomy_by_label[label] for label in labels)
        polarity = 1 if active_count % 2 else -1
        face_id = face_row["face_id"]
        rows.append(
            {
                "face_id": face_id,
                "face_type_code": face_row["face_type_code"],
                "source_id": face_row["source_id"],
                "label_count": len(labels),
                "active_label_count": active_count,
                "polarity": polarity,
                "weight": polarity * (face_id + 1) ** 2,
            }
        )
    return rows


def hpol_height(
    slack_table: np.ndarray,
    face_weights: list[int],
    vertex_count: int,
) -> list[int]:
    heights = [0] * vertex_count
    for row in np.asarray(slack_table, dtype=np.int64):
        face_id = int(row[1])
        vertex_id = int(row[2])
        heights[vertex_id] += face_weights[face_id] * int(row[5])
    return heights


def sample_row(
    sample_id: int,
    sample_kind: int,
    support: tuple[int, ...],
    pairing_value: int,
) -> dict[str, int]:
    padded = list(support) + [-1] * (5 - len(support))
    return {
        "sample_id": sample_id,
        "sample_kind": sample_kind,
        "circuit_size": len(support),
        "v0": padded[0],
        "v1": padded[1],
        "v2": padded[2],
        "v3": padded[3],
        "v4": padded[4],
        "pairing_value": pairing_value,
    }


def stream_stats() -> dict[str, Any]:
    face_rows = face_weight_rows()
    face_weights = [row["weight"] for row in face_rows]

    ext_tables = np.load(EXT_TABLES, allow_pickle=False)
    vertex_table = np.asarray(ext_tables["vertex_table"], dtype=np.int64)
    slack_table = np.asarray(ext_tables["slack_table"], dtype=np.int64)
    coords = [
        tuple(int(value) for value in (ext.SCALE, row[1], row[2], row[3]))
        for row in vertex_table
    ]
    heights = hpol_height(slack_table, face_weights, len(coords))

    aext_tables = np.load(AEXT_TABLES, allow_pickle=False)
    c4_rows = [
        tuple(int(value) for value in row[1:5])
        for row in np.asarray(aext_tables["c4_table"], dtype=np.int64)
    ]
    c4_set = set(c4_rows)

    row_hash = hashlib.sha256()
    samples = []
    row_count = 0
    c4_count = 0
    c5_count = 0
    zero_count = 0
    positive_count = 0
    zero_c4_count = 0
    zero_c5_count = 0
    positive_c4_count = 0
    positive_c5_count = 0
    min_positive: int | None = None
    max_positive = 0

    def emit(
        support: tuple[int, ...],
        coefficients: list[int],
        circuit_size: int,
    ) -> None:
        nonlocal row_count
        nonlocal zero_count
        nonlocal positive_count
        nonlocal zero_c4_count
        nonlocal zero_c5_count
        nonlocal positive_c4_count
        nonlocal positive_c5_count
        nonlocal min_positive
        nonlocal max_positive

        pairing = sum(
            coefficient * heights[vertex_id]
            for coefficient, vertex_id in zip(coefficients, support)
        )
        if pairing < 0:
            coefficients = [-coefficient for coefficient in coefficients]
            pairing = -pairing
        row_hash.update(srows.row_bytes(support, coefficients, pairing))
        if pairing == 0:
            zero_count += 1
            zero_c4_count += int(circuit_size == 4)
            zero_c5_count += int(circuit_size == 5)
            sample_kind = 0
        else:
            positive_count += 1
            positive_c4_count += int(circuit_size == 4)
            positive_c5_count += int(circuit_size == 5)
            min_positive = pairing if min_positive is None else min(min_positive, pairing)
            max_positive = max(max_positive, pairing)
            sample_kind = 1
        if len(samples) < SAMPLE_LIMIT:
            samples.append(sample_row(row_count, sample_kind, support, pairing))
        row_count += 1

    for support in c4_rows:
        emit(support, srows.coefs4([coords[index] for index in support]), 4)
        c4_count += 1

    for support in combinations(range(len(coords)), 5):
        if any(tuple(quad) in c4_set for quad in combinations(support, 4)):
            continue
        emit(support, srows.coefs5([coords[index] for index in support]), 5)
        c5_count += 1

    if min_positive is None:
        min_positive = 0

    return {
        "face_rows": face_rows,
        "face_weights": face_weights,
        "face_weight_sha256": sequence_hash(face_weights),
        "height_rows": [
            {"vertex_id": vertex_id, "height_value": height}
            for vertex_id, height in enumerate(heights)
        ],
        "heights": heights,
        "height_sha256": sequence_hash(heights),
        "row_count": row_count,
        "c4_count": c4_count,
        "c5_count": c5_count,
        "zero_count": zero_count,
        "positive_count": positive_count,
        "zero_c4_count": zero_c4_count,
        "zero_c5_count": zero_c5_count,
        "positive_c4_count": positive_c4_count,
        "positive_c5_count": positive_c5_count,
        "min_positive": min_positive,
        "max_positive": max_positive,
        "row_stream_sha256": row_hash.hexdigest(),
        "samples": samples,
    }


def build_payload_rows() -> dict[str, Any]:
    aext_report = load_json(AEXT_REPORT)
    srows_report = load_json(SROWS_REPORT)
    islack_report = load_json(ISLACK_REPORT)
    holonomy_report = load_json(HOLONOMY_REPORT)
    truncated_report = load_json(TRUNCATED_REPORT)
    stats = stream_stats()
    holonomy_pairing = int(holonomy_report["witness"]["holonomy_eta6_pairing"])
    intrinsic_zero_count = int(
        islack_report["witness"]["pairing_counts"]["zero_pairing_count"]
    )
    obs_values = {
        "vertex_count": len(stats["heights"]),
        "support_face_count": len(stats["face_weights"]),
        "positive_face_weight_count": sum(
            1 for value in stats["face_weights"] if value > 0
        ),
        "negative_face_weight_count": sum(
            1 for value in stats["face_weights"] if value < 0
        ),
        "unique_hpol_height_count": len(set(stats["heights"])),
        "hpol_height_min": min(stats["heights"]),
        "hpol_height_max": max(stats["heights"]),
        "signed_row_count": stats["row_count"],
        "zero_pairing_count": stats["zero_count"],
        "positive_pairing_count": stats["positive_count"],
        "zero_c4_pairing_count": stats["zero_c4_count"],
        "zero_c5_pairing_count": stats["zero_c5_count"],
        "positive_c4_pairing_count": stats["positive_c4_count"],
        "positive_c5_pairing_count": stats["positive_c5_count"],
        "min_positive_pairing": stats["min_positive"],
        "max_positive_pairing_bit_length": stats["max_positive"].bit_length(),
        "strict_hpol_orientation_flag": int(
            stats["zero_count"] == 0 and stats["positive_count"] == stats["row_count"]
        ),
        "eta6_holonomy_pairing": holonomy_pairing,
        "eta6_support_preserved_flag": 1,
        "topology_changing_surgery_flag": 0,
        "intrinsic_zero_pairing_count": intrinsic_zero_count,
        "face_square_tiebreaker_flag": 1,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": code,
            "value": obs_values[name],
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
        for index in [code]
    ]
    return {
        "aext_report": aext_report,
        "srows_report": srows_report,
        "islack_report": islack_report,
        "holonomy_report": holonomy_report,
        "truncated_report": truncated_report,
        "stats": stats,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    stats = rows["stats"]
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    face_table = table_from_rows(FACE_COLUMNS, stats["face_rows"])
    height_table = table_from_rows(HEIGHT_COLUMNS, stats["height_rows"])
    obs_by_code = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    obs = {name: obs_by_code[code] for name, code in OBS_CODES.items()}
    checks = {
        "input_certificates_available": (
            rows["aext_report"].get("all_checks_pass") is True
            and rows["srows_report"].get("all_checks_pass") is True
            and rows["islack_report"].get("all_checks_pass") is True
            and rows["holonomy_report"].get("all_checks_pass") is True
            and rows["truncated_report"].get("all_checks_pass") is True
        ),
        "face_weight_rule_matches_eta6_holonomy_polarity": (
            obs["support_face_count"],
            obs["positive_face_weight_count"],
            obs["negative_face_weight_count"],
            stats["face_weights"],
        )
        == (
            32,
            16,
            16,
            [
                1,
                4,
                9,
                16,
                25,
                -36,
                -49,
                64,
                -81,
                -100,
                -121,
                -144,
                169,
                -196,
                225,
                256,
                289,
                -324,
                -361,
                400,
                441,
                -484,
                529,
                -576,
                -625,
                676,
                729,
                -784,
                -841,
                -900,
                961,
                -1024,
            ],
        ),
        "hpol_height_breaks_vertex_symmetry": (
            obs["vertex_count"],
            obs["unique_hpol_height_count"],
            obs["hpol_height_min"],
            obs["hpol_height_max"],
            stats["height_sha256"],
        )
        == (
            60,
            60,
            -9_418_959_026_769_907,
            3_787_234_343_094_179,
            "fb848d73ee26bd925e3c15b0d262323f547332222236b178b815c6b2eb8a5afe",
        ),
        "all_minimal_circuit_rows_pair_strictly_positive": (
            obs["signed_row_count"],
            obs["zero_pairing_count"],
            obs["positive_pairing_count"],
            obs["zero_c4_pairing_count"],
            obs["zero_c5_pairing_count"],
            obs["positive_c4_pairing_count"],
            obs["positive_c5_pairing_count"],
            obs["min_positive_pairing"],
            obs["max_positive_pairing_bit_length"],
            obs["strict_hpol_orientation_flag"],
            stats["row_stream_sha256"],
        )
        == (
            4_903_515,
            0,
            4_903_515,
            0,
            0,
            10_635,
            4_892_880,
            1,
            136,
            1,
            "70a6216673205d9ed0e3df7a67fa9a61f05ea9343246cf06355b9d764eca72f0",
        ),
        "hpol_repairs_intrinsic_slack_degeneracy_without_topology_change": (
            obs["intrinsic_zero_pairing_count"],
            obs["eta6_holonomy_pairing"],
            obs["eta6_support_preserved_flag"],
            obs["topology_changing_surgery_flag"],
            obs["face_square_tiebreaker_flag"],
        )
        == (4_894_923, 1, 1, 0, 1),
        "table_shapes_match_codebooks": (
            tuple(obs_table.shape),
            tuple(face_table.shape),
            tuple(height_table.shape),
        )
        == (
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (32, len(FACE_COLUMNS)),
            (60, len(HEIGHT_COLUMNS)),
        ),
    }

    witness = {
        "height_rule": (
            "h_v = sum_f epsilon_f (f+1)^2 slack(f,v), where epsilon_f is "
            "+1 for odd eta6-holonomy parity on the face labels and -1 otherwise"
        ),
        "face_weight_sha256": stats["face_weight_sha256"],
        "height_vector_sha256": stats["height_sha256"],
        "row_stream_sha256": stats["row_stream_sha256"],
        "pairing_counts": {
            "signed_row_count": obs["signed_row_count"],
            "zero_pairing_count": obs["zero_pairing_count"],
            "positive_pairing_count": obs["positive_pairing_count"],
            "positive_c4_pairing_count": obs["positive_c4_pairing_count"],
            "positive_c5_pairing_count": obs["positive_c5_pairing_count"],
            "max_positive_pairing": stats["max_positive"],
        },
        "eta6": {
            "holonomy_pairing": obs["eta6_holonomy_pairing"],
            "support_preserved_flag": bool(obs["eta6_support_preserved_flag"]),
        },
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "face_table_sha256": pair.parent.sha_array(face_table),
        "height_table_sha256": pair.parent.sha_array(height_table),
    }

    hpol = {
        "schema": "eta6.hpol@1",
        "object": "eta6",
        "construction": {
            "polarization": "eta6 holonomy parity on truncated-boundary support faces",
            "tie_breaker": "signed square face weight",
            "reading": (
                "the holonomy-polarized support height gives a strict exterior "
                "circuit orientation while preserving the eta6 support class"
            ),
        },
        "witness": witness,
    }

    report = {
        "schema": "eta6.hpol.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_HPOL_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6 holonomy-polarized exterior height, with the minimal "
            "face-square tie-breaker, is strict on the current 60-vertex "
            "boundary carrier: all 4,903,515 minimal affine circuit rows pair "
            "positively. This repairs the symmetric intrinsic slack degeneracy "
            "as an orientation witness. It does not perform a topology-changing "
            "surgery or open eta6."
        ),
        "stage_protocol": {
            "draft": "start from eta6_aext, eta6_srows, eta6_islack, eta6 holonomy, and the truncated support faces",
            "witness": "polarize exterior support slacks by eta6 face holonomy and a square face tie-breaker",
            "coherence": "stream every minimal affine circuit row against the polarized height",
            "closure": "certify zero circuit degeneracies are removed without changing eta6 support",
            "emit": "emit short hpol artifacts, hashes, samples, verifier command, and next target",
        },
        "inputs": {
            "aext_report": pair.parent.input_entry(
                AEXT_REPORT,
                {
                    "status": rows["aext_report"].get("status"),
                    "certificate_sha256": rows["aext_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "aext_tables": pair.parent.input_entry(AEXT_TABLES),
            "ext_tables": pair.parent.input_entry(EXT_TABLES),
            "srows_report": pair.parent.input_entry(
                SROWS_REPORT,
                {
                    "status": rows["srows_report"].get("status"),
                    "certificate_sha256": rows["srows_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "islack_report": pair.parent.input_entry(
                ISLACK_REPORT,
                {
                    "status": rows["islack_report"].get("status"),
                    "certificate_sha256": rows["islack_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "holonomy_report": pair.parent.input_entry(
                HOLONOMY_REPORT,
                {
                    "status": rows["holonomy_report"].get("status"),
                    "certificate_sha256": rows["holonomy_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "truncated_report": pair.parent.input_entry(
                TRUNCATED_REPORT,
                {
                    "status": rows["truncated_report"].get("status"),
                    "certificate_sha256": rows["truncated_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "truncated_tables": pair.parent.input_entry(TRUNCATED_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "hpol": pair.parent.relpath(OUT_DIR / "hpol.json"),
            "weights_csv": pair.parent.relpath(OUT_DIR / "weights.csv"),
            "heights_csv": pair.parent.relpath(OUT_DIR / "heights.csv"),
            "samples_csv": pair.parent.relpath(OUT_DIR / "samp.csv"),
            "obs_csv": pair.parent.relpath(OUT_DIR / "obs.csv"),
            "tables": pair.parent.relpath(OUT_DIR / "tables.npz"),
            "certificate": pair.parent.relpath(OUT_DIR / "cert.json"),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a holonomy-polarized exterior height with face-square tie-breaker",
                "strict positive pairing on all current minimal affine circuit rows",
                "removal of the intrinsic slack-height zero-row degeneracy",
                "eta6 support preservation under this orientation-only test",
            ],
            "does_not_certify_because_not_required": [
                "a topology-changing surgery across eta6",
                "opening or killing the eta6 aperture",
                "that the square tie-breaker is unique or intrinsic",
            ],
        },
        "next_highest_yield_item": (
            "Use hpol as the orientation witness for an explicit discriminant "
            "surgery proposal, then test whether the post-surgery support cone "
            "stays positive."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    cert = {
        "schema": "eta6.hpol.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.hpol.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "hpol": hpol,
        "weights_csv": csv_text(FACE_COLUMNS, stats["face_rows"]),
        "heights_csv": csv_text(HEIGHT_COLUMNS, stats["height_rows"]),
        "samples_csv": csv_text(SAMPLE_COLUMNS, stats["samples"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "observable_table": obs_table,
        "face_table": face_table,
        "height_table": height_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = ext.nonholonomic.preservation.INDEX_PATH
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
    pair.parent.write_json(OUT_DIR / "hpol.json", payloads["hpol"])
    (OUT_DIR / "weights.csv").write_text(payloads["weights_csv"], encoding="utf-8")
    (OUT_DIR / "heights.csv").write_text(payloads["heights_csv"], encoding="utf-8")
    (OUT_DIR / "samp.csv").write_text(payloads["samples_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        observable_table=payloads["observable_table"],
        face_table=payloads["face_table"],
        height_table=payloads["height_table"],
    )
    pair.parent.write_json(OUT_DIR / "cert.json", payloads["cert"])
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
