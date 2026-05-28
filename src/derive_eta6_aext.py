from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_eta6_ext_cone as ext
    from . import derive_eta6_gordan as gordan
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_ext_cone as ext
    import derive_eta6_gordan as gordan
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_aext"
STATUS = "ETA6_AEXT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

EXT_REPORT = ext.OUT_DIR / "report.json"
EXT_TABLES = ext.OUT_DIR / "tables.npz"
GORDAN_REPORT = gordan.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_aext.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_aext.py"

C4_ZERO_EPS = 1e-10
COLLINEAR_EPS = 1e-10

AEXT_COLUMNS = [
    "aext_row_id",
    "face_id",
    "vertex_id",
    "face_type_code",
    "face_size",
    "slack_x1e12",
    "test_h_x1e12",
    "test_value_x1e12",
    "positive_flag",
]
C4_COLUMNS = ["circuit_id", "v0", "v1", "v2", "v3"]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "aext_row_count": 0,
    "aext_positive_row_count": 1,
    "aext_zero_row_count": 2,
    "aext_test_vector_dimension": 3,
    "aext_test_h_x1e12": 4,
    "aext_min_test_value_x1e12": 5,
    "aext_max_test_value_x1e12": 6,
    "aext_gordan_no_nonzero_y_flag": 7,
    "collinear_triple_count": 8,
    "minimal_c4_count": 9,
    "minimal_c5_count": 10,
    "minimal_affine_circuit_count": 11,
    "max_c4_det_abs_x1e15": 12,
    "min_non_c4_det_abs_x1e12": 13,
    "circuit_census_gap_flag": 14,
    "full_circuit_gordan_flag": 15,
    "surgery_certificate_flag": 16,
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


def circuit_key(vertices: tuple[int, ...]) -> bytes:
    return (",".join(str(vertex_id) for vertex_id in vertices) + "\n").encode("ascii")


def det4_abs(matrix: np.ndarray, vertices: tuple[int, int, int, int]) -> float:
    return abs(float(np.linalg.det(matrix[list(vertices)])))


def triple_area(points: np.ndarray, vertices: tuple[int, int, int]) -> float:
    left, middle, right = points[list(vertices)]
    return float(np.linalg.norm(np.cross(middle - left, right - left)))


def build_aext_rows(slack_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    return [
        {
            "aext_row_id": row_id,
            "face_id": row["face_id"],
            "vertex_id": row["vertex_id"],
            "face_type_code": row["face_type_code"],
            "face_size": row["face_size"],
            "slack_x1e12": row["slack_x1e12"],
            "test_h_x1e12": ext.SCALE,
            "test_value_x1e12": row["slack_x1e12"],
            "positive_flag": int(row["slack_x1e12"] > 0),
        }
        for row_id, row in enumerate(slack_rows)
    ]


def build_circuit_census(vertex_table: np.ndarray) -> dict[str, Any]:
    points = vertex_table[:, 1:4].astype(np.float64) / float(ext.SCALE)
    homogeneous = np.column_stack([np.ones(len(points)), points])

    collinear_count = 0
    min_non_collinear_area = float("inf")
    for triple in combinations(range(len(points)), 3):
        area = triple_area(points, triple)
        if area < COLLINEAR_EPS:
            collinear_count += 1
        else:
            min_non_collinear_area = min(min_non_collinear_area, area)

    c4_rows = []
    c4_set: set[tuple[int, int, int, int]] = set()
    c4_hash = hashlib.sha256()
    max_c4_det_abs = 0.0
    min_non_c4_det_abs = float("inf")
    for circuit_id, quad in enumerate(combinations(range(len(points)), 4)):
        det_abs = det4_abs(homogeneous, quad)
        if det_abs < C4_ZERO_EPS:
            c4_set.add(quad)
            c4_hash.update(circuit_key(quad))
            c4_rows.append(
                {
                    "circuit_id": len(c4_rows),
                    "v0": quad[0],
                    "v1": quad[1],
                    "v2": quad[2],
                    "v3": quad[3],
                }
            )
            max_c4_det_abs = max(max_c4_det_abs, det_abs)
        else:
            min_non_c4_det_abs = min(min_non_c4_det_abs, det_abs)

    c5_count = 0
    c5_hash = hashlib.sha256()
    for five in combinations(range(len(points)), 5):
        if all(tuple(quad) not in c4_set for quad in combinations(five, 4)):
            c5_count += 1
            c5_hash.update(circuit_key(five))

    return {
        "collinear_count": collinear_count,
        "min_non_collinear_area": min_non_collinear_area,
        "c4_rows": c4_rows,
        "c4_set": c4_set,
        "c4_hash": c4_hash.hexdigest(),
        "c5_count": c5_count,
        "c5_hash": c5_hash.hexdigest(),
        "max_c4_det_abs": max_c4_det_abs,
        "min_non_c4_det_abs": min_non_c4_det_abs,
    }


def build_payload_rows() -> dict[str, Any]:
    ext_report = load_json(EXT_REPORT)
    gordan_report = load_json(GORDAN_REPORT)
    tables = np.load(EXT_TABLES, allow_pickle=False)
    vertex_table = np.asarray(tables["vertex_table"], dtype=np.int64)
    slack_rows = table_rows(
        np.asarray(tables["slack_table"], dtype=np.int64),
        ext.SLACK_COLUMNS,
    )
    aext_rows = build_aext_rows(slack_rows)
    circuit_census = build_circuit_census(vertex_table)
    test_values = [row["test_value_x1e12"] for row in aext_rows]
    obs_values = {
        "aext_row_count": len(aext_rows),
        "aext_positive_row_count": sum(row["positive_flag"] for row in aext_rows),
        "aext_zero_row_count": sum(row["test_value_x1e12"] == 0 for row in aext_rows),
        "aext_test_vector_dimension": 1,
        "aext_test_h_x1e12": ext.SCALE,
        "aext_min_test_value_x1e12": min(test_values),
        "aext_max_test_value_x1e12": max(test_values),
        "aext_gordan_no_nonzero_y_flag": int(all(value > 0 for value in test_values)),
        "collinear_triple_count": circuit_census["collinear_count"],
        "minimal_c4_count": len(circuit_census["c4_rows"]),
        "minimal_c5_count": circuit_census["c5_count"],
        "minimal_affine_circuit_count": len(circuit_census["c4_rows"])
        + circuit_census["c5_count"],
        "max_c4_det_abs_x1e15": int(round(circuit_census["max_c4_det_abs"] * 1e15)),
        "min_non_c4_det_abs_x1e12": int(
            round(circuit_census["min_non_c4_det_abs"] * 1e12)
        ),
        "circuit_census_gap_flag": int(
            circuit_census["max_c4_det_abs"] < C4_ZERO_EPS
            and circuit_census["min_non_c4_det_abs"] > 1e-3
            and circuit_census["collinear_count"] == 0
        ),
        "full_circuit_gordan_flag": 0,
        "surgery_certificate_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": row_id,
            "observable_code": code,
            "value": int(obs_values[key]),
            "scale_code": 0,
        }
        for row_id, (key, code) in enumerate(OBS_CODES.items())
    ]
    return {
        "ext_report": ext_report,
        "gordan_report": gordan_report,
        "aext_rows": aext_rows,
        "circuit_census": circuit_census,
        "obs_rows": obs_rows,
        "obs_values": obs_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    aext_table = table_from_rows(AEXT_COLUMNS, rows["aext_rows"])
    c4_table = table_from_rows(C4_COLUMNS, rows["circuit_census"]["c4_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs_values"]

    checks = {
        "input_reports_are_certified": (
            rows["ext_report"].get("status"),
            rows["gordan_report"].get("status"),
        )
        == (ext.STATUS, gordan.STATUS),
        "aext_exterior_cell_matrix_is_explicit": (
            obs["aext_row_count"],
            obs["aext_positive_row_count"],
            obs["aext_zero_row_count"],
            obs["aext_test_vector_dimension"],
            obs["aext_test_h_x1e12"],
            obs["aext_min_test_value_x1e12"],
            obs["aext_max_test_value_x1e12"],
        )
        == (1_740, 1_740, 0, 1, ext.SCALE, 350_487_408_079, 3_103_251_249_022),
        "aext_gordan_dual_is_certified": obs["aext_gordan_no_nonzero_y_flag"] == 1,
        "minimal_affine_circuit_census_is_complete_for_rounded_model": (
            obs["collinear_triple_count"],
            obs["minimal_c4_count"],
            obs["minimal_c5_count"],
            obs["minimal_affine_circuit_count"],
            obs["circuit_census_gap_flag"],
        )
        == (0, 10_635, 4_892_880, 4_903_515, 1),
        "closure_boundary_is_not_overclaimed": (
            obs["full_circuit_gordan_flag"],
            obs["surgery_certificate_flag"],
        )
        == (0, 0),
        "table_shapes_match_codebooks": (
            tuple(aext_table.shape),
            tuple(c4_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (1_740, len(AEXT_COLUMNS)),
            (10_635, len(C4_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }

    witness = {
        "aext_matrix": {
            "row_count": obs["aext_row_count"],
            "positive_row_count": obs["aext_positive_row_count"],
            "zero_row_count": obs["aext_zero_row_count"],
            "test_h_x1e12": obs["aext_test_h_x1e12"],
            "min_test_value_x1e12": obs["aext_min_test_value_x1e12"],
            "max_test_value_x1e12": obs["aext_max_test_value_x1e12"],
        },
        "minimal_affine_circuits": {
            "collinear_triple_count": obs["collinear_triple_count"],
            "size4_count": obs["minimal_c4_count"],
            "size5_count": obs["minimal_c5_count"],
            "total_count": obs["minimal_affine_circuit_count"],
            "max_size4_det_abs_x1e15": obs["max_c4_det_abs_x1e15"],
            "min_non_size4_det_abs_x1e12": obs["min_non_c4_det_abs_x1e12"],
            "size4_stream_sha256": rows["circuit_census"]["c4_hash"],
            "size5_stream_sha256": rows["circuit_census"]["c5_hash"],
        },
        "aext_table_sha256": pair.parent.sha_array(aext_table),
        "c4_table_sha256": pair.parent.sha_array(c4_table),
        "observable_table_sha256": pair.parent.sha_array(obs_table),
    }

    aext = {
        "schema": "eta6.aext@1",
        "object": "eta6",
        "construction": {
            "aext_matrix": "expanded exterior-cell support matrix with one row per face/non-face support slack",
            "gordan_vector": "h = [1]",
            "circuit_census": (
                "minimal affine circuits in the rounded 60-vertex coordinate "
                "model: coplanar 4-circuits plus 5-subsets containing no "
                "coplanar 4-subset"
            ),
        },
        "witness": witness,
    }

    report = {
        "schema": "eta6.aext.report@1",
        "status": STATUS
        if all(checks.values())
        else "ETA6_AEXT_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6 exterior layer now has an explicit expanded exterior-cell "
            "matrix A_ext with 1,740 support rows. The one-dimensional height "
            "witness h=1 evaluates every row strictly positive, so Gordan's "
            "alternative rules out a nonzero nonnegative dependence for this "
            "expanded exterior-cell matrix. The same run also enumerates the "
            "minimal affine-circuit census of the rounded 60-vertex carrier: "
            "10,635 coplanar 4-circuits and 4,892,880 generic 5-circuits. The "
            "full signed circuit-row Gordan test and surgery continuation are "
            "kept as open next layers."
        ),
        "stage_protocol": {
            "draft": "start from eta6_ext_cone slacks and eta6_gordan",
            "witness": "expand all 1,740 exterior face/non-face cells and enumerate minimal affine circuits",
            "coherence": "check strict A_ext positivity and determinant gap for the circuit census",
            "closure": "apply Gordan to the expanded exterior-cell matrix only",
            "emit": "emit compact rows, hashes, observables, cert, report, verifier command, and next target",
        },
        "inputs": {
            "ext_report": pair.parent.input_entry(
                EXT_REPORT,
                {
                    "status": rows["ext_report"].get("status"),
                    "certificate_sha256": rows["ext_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "ext_tables": pair.parent.input_entry(EXT_TABLES),
            "gordan_report": pair.parent.input_entry(
                GORDAN_REPORT,
                {
                    "status": rows["gordan_report"].get("status"),
                    "certificate_sha256": rows["gordan_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "aext": pair.parent.relpath(OUT_DIR / "aext.json"),
            "aext_csv": pair.parent.relpath(OUT_DIR / "aext.csv"),
            "c4_csv": pair.parent.relpath(OUT_DIR / "c4.csv"),
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
                "the expanded 1,740-row exterior-cell support matrix A_ext is explicit",
                "h=1 is strictly positive on every expanded exterior-cell row",
                "Gordan-dual infeasibility for nonzero nonnegative dependences on this expanded exterior-cell matrix",
                "a compact full census count and stream hash for minimal affine circuits of the rounded 60-vertex carrier",
            ],
            "does_not_certify_because_not_required": [
                "signed height rows for all 4,903,515 minimal affine circuits",
                "Gordan infeasibility for the full signed affine-circuit matrix",
                "a surgery move crossing the eta6 aperture stratum",
            ],
        },
        "next_highest_yield_item": (
            "Orient the 4,903,515 minimal affine circuits into signed height rows "
            "and run the Gordan alternative on that full circuit matrix."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    cert = {
        "schema": "eta6.aext.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.aext.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "aext": aext,
        "aext_csv": pair.csv_text(AEXT_COLUMNS, rows["aext_rows"]),
        "c4_csv": pair.csv_text(C4_COLUMNS, rows["circuit_census"]["c4_rows"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "aext_table": aext_table,
        "c4_table": c4_table,
        "observable_table": obs_table,
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
    pair.parent.write_json(OUT_DIR / "aext.json", payloads["aext"])
    (OUT_DIR / "aext.csv").write_text(payloads["aext_csv"], encoding="utf-8")
    (OUT_DIR / "c4.csv").write_text(payloads["c4_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        aext_table=payloads["aext_table"],
        c4_table=payloads["c4_table"],
        observable_table=payloads["observable_table"],
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
