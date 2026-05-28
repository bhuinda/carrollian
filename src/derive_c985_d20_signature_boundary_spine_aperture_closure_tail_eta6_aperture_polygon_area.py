from __future__ import annotations

import json
import math
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen as graham
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion as promotion
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen as graham
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion as promotion
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_APERTURE_POLYGON_AREA_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GRAHAM_REPORT = graham.OUT_DIR / "report.json"
GRAHAM_TABLES = (
    graham.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_tables.npz"
)
PROMOTION_REPORT = promotion.OUT_DIR / "report.json"
PROMOTION_TABLES = (
    promotion.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area.py"
)

SCALE = 1_000_000_000_000
GRAHAM_AREA_X1E12 = graham.GRAHAM_AREA_NUM_X1E6 * 1_000_000
REGULAR_AREA_X1E12 = graham.REGULAR_AREA_NUM_X1E6 * 1_000_000
GRAHAM_AREA_TOLERANCE_X1E12 = 5_000_000_000

POINT_COLUMNS = [
    "point_id",
    "cut_edge_id",
    "source_state_id",
    "target_state_id",
    "midpoint_x2_x1e12",
    "midpoint_y2_x1e12",
    "polygon_order",
    "convex_hull_flag",
    "convex_hull_order",
]
METRIC_COLUMNS = [
    "metric_id",
    "cut_edge_count",
    "unique_midpoint_count",
    "convex_hull_vertex_count",
    "diameter_left_cut_edge_id",
    "diameter_right_cut_edge_id",
    "diameter_sq_x1e12",
    "polygon_area_x1e12",
    "diameter_normalized_area_x1e12",
    "regular_area_x1e12",
    "graham_area_x1e12",
    "area_over_regular_ratio_x1e12",
    "area_over_graham_ratio_x1e12",
    "regular_area_abs_error_x1e12",
    "graham_area_abs_error_x1e12",
    "convex_hexagon_flag",
    "graham_area_match_flag",
    "area_certificate_available_flag",
    "truncated_icosahedral_skeleton_certified_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "cut_edge_count": 0,
    "unique_midpoint_count": 1,
    "convex_hull_vertex_count": 2,
    "diameter_sq_x1e12": 3,
    "polygon_area_x1e12": 4,
    "diameter_normalized_area_x1e12": 5,
    "regular_area_x1e12": 6,
    "graham_area_x1e12": 7,
    "area_over_regular_ratio_x1e12": 8,
    "area_over_graham_ratio_x1e12": 9,
    "regular_area_abs_error_x1e12": 10,
    "graham_area_abs_error_x1e12": 11,
    "convex_hexagon_flag": 12,
    "graham_area_match_flag": 13,
    "area_certificate_available_flag": 14,
    "truncated_icosahedral_skeleton_certified_flag": 15,
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


def csv_text(headers: list[str], rows: list[dict[str, int]]) -> str:
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row[header]) for header in headers))
    return "\n".join(lines) + "\n"


def cross(
    origin: tuple[int, int],
    left: tuple[int, int],
    right: tuple[int, int],
) -> int:
    return (left[0] - origin[0]) * (right[1] - origin[1]) - (
        left[1] - origin[1]
    ) * (right[0] - origin[0])


def convex_hull(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    ordered = sorted(set(points))
    if len(ordered) <= 1:
        return ordered
    lower: list[tuple[int, int]] = []
    for point in ordered:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[int, int]] = []
    for point in reversed(ordered):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def twice_polygon_area(points: list[tuple[int, int]]) -> int:
    total = 0
    for (left_x, left_y), (right_x, right_y) in zip(points, points[1:] + points[:1]):
        total += left_x * right_y - left_y * right_x
    return abs(total)


def build_point_rows(
    edge_rows: list[dict[str, int]],
    poincare_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    poincare_by_state = {
        row["automaton_state_id"]: row
        for row in poincare_rows
    }
    cut_edges = [
        row
        for row in edge_rows
        if row["new_spectral_cut_edge_flag"] == 1
    ]
    points = []
    for point_id, edge in enumerate(
        sorted(cut_edges, key=lambda row: row["automaton_edge_id"])
    ):
        source = poincare_by_state[edge["source_state_id"]]
        target = poincare_by_state[edge["target_state_id"]]
        points.append(
            {
                "point_id": point_id,
                "cut_edge_id": edge["automaton_edge_id"],
                "source_state_id": edge["source_state_id"],
                "target_state_id": edge["target_state_id"],
                "midpoint_x2_x1e12": (
                    source["poincare_x_x1e12"] + target["poincare_x_x1e12"]
                ),
                "midpoint_y2_x1e12": (
                    source["poincare_y_x1e12"] + target["poincare_y_x1e12"]
                ),
                "polygon_order": -1,
                "convex_hull_flag": 0,
                "convex_hull_order": -1,
            }
        )

    sum_x = sum(row["midpoint_x2_x1e12"] for row in points)
    sum_y = sum(row["midpoint_y2_x1e12"] for row in points)
    count = len(points)
    angle_ordered = sorted(
        points,
        key=lambda row: (
            math.atan2(
                count * row["midpoint_y2_x1e12"] - sum_y,
                count * row["midpoint_x2_x1e12"] - sum_x,
            ),
            row["cut_edge_id"],
        ),
    )
    for order, row in enumerate(angle_ordered):
        row["polygon_order"] = order

    hull = convex_hull(
        [
            (row["midpoint_x2_x1e12"], row["midpoint_y2_x1e12"])
            for row in points
        ]
    )
    hull_order = {point: order for order, point in enumerate(hull)}
    for row in points:
        point = (row["midpoint_x2_x1e12"], row["midpoint_y2_x1e12"])
        if point in hull_order:
            row["convex_hull_flag"] = 1
            row["convex_hull_order"] = hull_order[point]
    return points


def build_metric_row(point_rows: list[dict[str, int]]) -> dict[str, int]:
    ordered_points = [
        (row["midpoint_x2_x1e12"], row["midpoint_y2_x1e12"])
        for row in sorted(point_rows, key=lambda row: row["polygon_order"])
    ]
    all_points = [
        (row["midpoint_x2_x1e12"], row["midpoint_y2_x1e12"])
        for row in point_rows
    ]
    hull = convex_hull(all_points)
    diameter_pair = max(
        (
            (
                (left["midpoint_x2_x1e12"] - right["midpoint_x2_x1e12"]) ** 2
                + (left["midpoint_y2_x1e12"] - right["midpoint_y2_x1e12"]) ** 2,
                left["cut_edge_id"],
                right["cut_edge_id"],
            )
            for left, right in combinations(point_rows, 2)
        ),
        key=lambda item: (item[0], -item[1], -item[2]),
    )
    twice_area_x4e24 = twice_polygon_area(ordered_points)
    diameter_sq_x4e24 = diameter_pair[0]
    polygon_area_x1e12 = twice_area_x4e24 // (8 * SCALE)
    diameter_sq_x1e12 = diameter_sq_x4e24 // (4 * SCALE)
    normalized_area_x1e12 = (
        twice_area_x4e24 * SCALE
    ) // (2 * diameter_sq_x4e24)
    area_over_regular_ratio_x1e12 = (
        normalized_area_x1e12 * SCALE
    ) // REGULAR_AREA_X1E12
    area_over_graham_ratio_x1e12 = (
        normalized_area_x1e12 * SCALE
    ) // GRAHAM_AREA_X1E12
    regular_error = abs(normalized_area_x1e12 - REGULAR_AREA_X1E12)
    graham_error = abs(normalized_area_x1e12 - GRAHAM_AREA_X1E12)
    convex_hexagon_flag = int(
        len(point_rows) == 6
        and len(set(all_points)) == 6
        and len(hull) == 6
        and twice_area_x4e24 > 0
    )
    graham_match_flag = int(graham_error <= GRAHAM_AREA_TOLERANCE_X1E12)
    return {
        "metric_id": 0,
        "cut_edge_count": len(point_rows),
        "unique_midpoint_count": len(set(all_points)),
        "convex_hull_vertex_count": len(hull),
        "diameter_left_cut_edge_id": diameter_pair[1],
        "diameter_right_cut_edge_id": diameter_pair[2],
        "diameter_sq_x1e12": diameter_sq_x1e12,
        "polygon_area_x1e12": polygon_area_x1e12,
        "diameter_normalized_area_x1e12": normalized_area_x1e12,
        "regular_area_x1e12": REGULAR_AREA_X1E12,
        "graham_area_x1e12": GRAHAM_AREA_X1E12,
        "area_over_regular_ratio_x1e12": area_over_regular_ratio_x1e12,
        "area_over_graham_ratio_x1e12": area_over_graham_ratio_x1e12,
        "regular_area_abs_error_x1e12": regular_error,
        "graham_area_abs_error_x1e12": graham_error,
        "convex_hexagon_flag": convex_hexagon_flag,
        "graham_area_match_flag": graham_match_flag,
        "area_certificate_available_flag": 1,
        "truncated_icosahedral_skeleton_certified_flag": 0,
    }


def build_payload_rows() -> dict[str, Any]:
    graham_report = load_json(GRAHAM_REPORT)
    promotion_report = load_json(PROMOTION_REPORT)
    tables = np.load(PROMOTION_TABLES, allow_pickle=False)
    edge_rows = table_rows(
        np.asarray(tables["edge_table"], dtype=np.int64),
        promotion.EDGE_COLUMNS,
    )
    poincare_rows = table_rows(
        np.asarray(tables["poincare_table"], dtype=np.int64),
        promotion.POINCARE_COLUMNS,
    )
    spectral_rows = table_rows(
        np.asarray(tables["spectral_cut_table"], dtype=np.int64),
        promotion.SPECTRAL_CUT_COLUMNS,
    )
    point_rows = build_point_rows(edge_rows, poincare_rows)
    metric_rows = [build_metric_row(point_rows)]
    metric = metric_rows[0]
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(metric[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return {
        "graham_report": graham_report,
        "promotion_report": promotion_report,
        "spectral_row": spectral_rows[0],
        "point_rows": point_rows,
        "metric_rows": metric_rows,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    point_table = table_from_rows(POINT_COLUMNS, rows["point_rows"])
    metric_table = table_from_rows(METRIC_COLUMNS, rows["metric_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    metric = rows["metric_rows"][0]
    spectral = rows["spectral_row"]
    ordered_points = sorted(rows["point_rows"], key=lambda row: row["polygon_order"])
    hull_points = sorted(
        (row for row in rows["point_rows"] if row["convex_hull_flag"] == 1),
        key=lambda row: row["convex_hull_order"],
    )

    checks = {
        "parent_reports_certified": (
            rows["promotion_report"].get("status"),
            rows["graham_report"].get("status"),
        )
        == (promotion.STATUS, graham.STATUS),
        "six_cut_edges_match_second_window_spectral_witness": (
            metric["cut_edge_count"],
            spectral["cut_edge_count"],
            spectral["old_cut_edge_still_cut_count"],
        )
        == (6, 6, 6),
        "cut_edge_midpoints_are_distinct_but_not_a_convex_hexagon": (
            metric["unique_midpoint_count"],
            metric["convex_hull_vertex_count"],
            metric["convex_hexagon_flag"],
        )
        == (6, 3, 0),
        "diameter_normalized_area_is_reproducible": (
            metric["diameter_sq_x1e12"],
            metric["polygon_area_x1e12"],
            metric["diameter_normalized_area_x1e12"],
        )
        == (10_540_354_657, 1_742_768_258, 165_342_468_540),
        "midpoint_projection_is_not_the_graham_lift": (
            metric["area_over_regular_ratio_x1e12"],
            metric["area_over_graham_ratio_x1e12"],
            metric["regular_area_abs_error_x1e12"],
            metric["graham_area_abs_error_x1e12"],
            metric["graham_area_match_flag"],
        )
        == (
            254_561_403_962,
            244_958_700_378,
            484_176_531_460,
            509_638_531_460,
            0,
        ),
        "truncated_icosahedral_skeleton_is_not_certified_here": metric[
            "truncated_icosahedral_skeleton_certified_flag"
        ]
        == 0,
        "table_shapes_match_codebooks": (
            tuple(point_table.shape),
            tuple(metric_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (6, len(POINT_COLUMNS)),
            (1, len(METRIC_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "cut_edge_ids": [row["cut_edge_id"] for row in rows["point_rows"]],
        "polygon_ordered_cut_edge_ids": [
            row["cut_edge_id"] for row in ordered_points
        ],
        "convex_hull_cut_edge_ids": [row["cut_edge_id"] for row in hull_points],
        "metric": metric,
        "raw_integer_geometry": {
            "twice_area_x4e24": twice_polygon_area(
                [
                    (row["midpoint_x2_x1e12"], row["midpoint_y2_x1e12"])
                    for row in ordered_points
                ]
            ),
            "diameter_sq_x4e24": max(
                (
                    (left["midpoint_x2_x1e12"] - right["midpoint_x2_x1e12"]) ** 2
                    + (left["midpoint_y2_x1e12"] - right["midpoint_y2_x1e12"])
                    ** 2
                )
                for left, right in combinations(rows["point_rows"], 2)
            ),
        },
        "point_table_sha256": sha_array(point_table),
        "metric_table_sha256": sha_array(metric_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    aperture_polygon = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area@1",
        "object": "C985->d20",
        "source": "second-window promotion spectral cut-edge midpoints in the certified Poincare coordinate table",
        "graham_reference": {
            "area_graham_approx_x1e12": GRAHAM_AREA_X1E12,
            "area_regular_diameter_one_hexagon_approx_x1e12": REGULAR_AREA_X1E12,
            "area_tolerance_x1e12": GRAHAM_AREA_TOLERANCE_X1E12,
        },
        "midpoint_geometry": {
            "points": rows["point_rows"],
            "polygon_ordered_cut_edge_ids": witness["polygon_ordered_cut_edge_ids"],
            "convex_hull_cut_edge_ids": witness["convex_hull_cut_edge_ids"],
            "metric": metric,
        },
        "steinitz_context": {
            "truncated_icosahedral_graph_vertices": 60,
            "truncated_icosahedral_graph_edges": 90,
            "current_certificate_realizes_that_skeleton": False,
            "reason": "this certificate measures the six cut-edge midpoint polygon, not a 60/90 polyhedral skeleton",
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_APERTURE_POLYGON_AREA_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The promoted six-edge cut has a reproducible midpoint-projection "
            "area witness. Its six midpoint samples are distinct, but their "
            "convex hull has only three vertices; this says the Graham-like "
            "hexagonal throat is not visible in the raw midpoint projection. "
            "After diameter normalization the projected area is 0.165342468540, "
            "so the geometry has to be read one lift higher rather than from "
            "cut-edge midpoints alone."
        ),
        "stage_protocol": {
            "draft": "start from the certified second-window promotion cut and Graham throat screen",
            "witness": "build the six cut-edge midpoint samples in Poincare coordinates",
            "coherence": "sort the samples cyclically, compute hull size, diameter, and normalized area",
            "closure": "certify the midpoint polygon area as a projection witness pointing to the lifted boundary skeleton",
            "emit": "emit midpoint, metric, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "graham_throat_report": input_entry(
                GRAHAM_REPORT,
                {
                    "status": rows["graham_report"].get("status"),
                    "certificate_sha256": rows["graham_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "graham_throat_tables": input_entry(GRAHAM_TABLES),
            "second_window_promotion_report": input_entry(
                PROMOTION_REPORT,
                {
                    "status": rows["promotion_report"].get("status"),
                    "certificate_sha256": rows["promotion_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "second_window_promotion_tables": input_entry(PROMOTION_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "aperture_polygon": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area.json"
            ),
            "midpoints_csv": relpath(OUT_DIR / "eta6_aperture_polygon_midpoints.csv"),
            "metrics_csv": relpath(OUT_DIR / "eta6_aperture_polygon_metrics.csv"),
            "observables_csv": relpath(
                OUT_DIR / "eta6_aperture_polygon_observables.csv"
            ),
            "tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_tables.npz"
            ),
            "certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the six promoted cut-edge midpoint samples are reproducible from certified Poincare data",
                "the midpoint projection has six distinct samples but a triangular convex hull",
                "the diameter-normalized midpoint projection is far below both the regular and Graham diameter-one hexagon references",
                "the midpoint projection therefore cannot be the full Graham-like lifted aperture witness",
            ],
            "does_not_certify_because_not_required": [
                "a six-vertex convex aperture polygon from endpoint, face, or barycentric geometry",
                "a 60-vertex/90-edge truncated-icosahedral polyhedral skeleton",
                "Graham-ratio convergence for any non-midpoint aperture construction",
                "an H4 metric tensor or curvature/torsion area law",
            ],
        },
        "next_highest_yield_item": (
            "Lift the readout to the public-boundary dual and test whether the "
            "60/90 truncated-icosahedral graph is the Steinitz-compatible "
            "boundary skeleton carrying the Graham-like throat geometry."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the Graham analogy survives as a lifted target geometry, not as the raw cut-edge midpoint projection",
            "the six-edge eta6 support is still the invariant source of the readout",
            "the next geometric aperture test needs the lifted public-boundary skeleton rather than edge midpoints",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified Graham throat and second-window promotion reports",
            "filter the six promoted spectral cut edges",
            "compute midpoint samples from certified Poincare coordinates",
            "check cyclic order, convex hull count, diameter, area, and Graham mismatch",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "aperture_polygon": aperture_polygon,
        "midpoints_csv": csv_text(POINT_COLUMNS, rows["point_rows"]),
        "metrics_csv": csv_text(METRIC_COLUMNS, rows["metric_rows"]),
        "observables_csv": csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "point_table": point_table,
        "metric_table": metric_table,
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
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area.json",
        payloads["aperture_polygon"],
    )
    (OUT_DIR / "eta6_aperture_polygon_midpoints.csv").write_text(
        payloads["midpoints_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_aperture_polygon_metrics.csv").write_text(
        payloads["metrics_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_aperture_polygon_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_tables.npz",
        point_table=payloads["point_table"],
        metric_table=payloads["metric_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_certificate.json",
        payloads["certificate"],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
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
