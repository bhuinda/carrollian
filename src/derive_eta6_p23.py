from __future__ import annotations

import csv
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p2 as p2
    from . import derive_eta6_p22 as p22
    from . import derive_eta6_t2 as t2
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p2 as p2
    import derive_eta6_p22 as p22
    import derive_eta6_t2 as t2
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p23"
STATUS = "ETA6_P23_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P2_REPORT = p2.OUT_DIR / "report.json"
P2_FACES = p2.OUT_DIR / "faces.csv"
P2_VERTS = p2.OUT_DIR / "verts.csv"
P2_SUPP = p2.OUT_DIR / "supp.csv"
T2_REPORT = t2.OUT_DIR / "report.json"
T2_FUSE = t2.OUT_DIR / "fuse.csv"
P22_REPORT = p22.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p23.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p23.py"

LIFT_FACE_IDS = (12, 22, 26)
HIT_VERTICES = (40, 46, 47)
FACE_COLUMNS = [
    "lift_id",
    "face_id",
    "label_mask",
    "kind_code",
    "face_size",
    "hit_vertex_a",
    "hit_vertex_b",
    "anchor_vertex_a",
    "anchor_vertex_b",
    "cycle_v0",
    "cycle_v1",
    "cycle_v2",
    "cycle_v3",
    "orig_v0",
    "orig_v1",
    "orig_v2",
    "orig_v3",
    "support_row_count",
    "positive_support_count",
    "min_slack_x1e12",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "lift_face_count": 0,
    "quadrilateral_face_count": 1,
    "fused_kind_count": 2,
    "unique_vertex_count": 3,
    "hit_vertex_count": 4,
    "support_row_count": 5,
    "support_positive_count": 6,
    "support_zero_count": 7,
    "min_slack_x1e12": 8,
    "max_slack_x1e12": 9,
    "p2_positive_support_flag": 10,
    "p22_symbolic_carrier_flag": 11,
    "geometric_lift_flag": 12,
    "new_c985_recompute_flag": 13,
    "face12_label_mask": 14,
    "face22_label_mask": 15,
    "face26_label_mask": 16,
}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def read_csv_ints(path: Any) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def face_cycle(row: dict[str, int]) -> list[int]:
    return [row[f"cycle_v{index}"] for index in range(row["face_size"])]


def build_p23_rows() -> dict[str, Any]:
    faces = read_csv_ints(P2_FACES)
    verts = {row["vertex_id"]: row for row in read_csv_ints(P2_VERTS)}
    supp = read_csv_ints(P2_SUPP)
    fuse_rows = read_csv_ints(T2_FUSE)
    fuse_by_face = {row["face_id"]: row for row in fuse_rows}
    support_by_face: dict[int, list[dict[str, int]]] = {}
    for row in supp:
        support_by_face.setdefault(row["face_id"], []).append(row)

    face_rows = []
    unique_vertices: set[int] = set()
    support_values = []
    for lift_id, face_id in enumerate(LIFT_FACE_IDS):
        face = faces[face_id]
        cycle = face_cycle(face)
        unique_vertices.update(cycle)
        hit = [vertex for vertex in cycle if vertex in HIT_VERTICES]
        anchors = [vertex for vertex in cycle if vertex not in HIT_VERTICES]
        face_support = support_by_face[face_id]
        support_values.extend(row["slack_x1e12"] for row in face_support)
        originals = [verts[vertex]["original_vertex_id"] for vertex in cycle]
        face_rows.append(
            {
                "lift_id": lift_id,
                "face_id": face_id,
                "label_mask": fuse_by_face[face_id]["label_mask"],
                "kind_code": face["kind_code"],
                "face_size": face["face_size"],
                "hit_vertex_a": hit[0],
                "hit_vertex_b": hit[1],
                "anchor_vertex_a": anchors[0],
                "anchor_vertex_b": anchors[1],
                "cycle_v0": cycle[0],
                "cycle_v1": cycle[1],
                "cycle_v2": cycle[2],
                "cycle_v3": cycle[3],
                "orig_v0": originals[0],
                "orig_v1": originals[1],
                "orig_v2": originals[2],
                "orig_v3": originals[3],
                "support_row_count": len(face_support),
                "positive_support_count": sum(
                    row["positive_flag"] for row in face_support
                ),
                "min_slack_x1e12": min(row["slack_x1e12"] for row in face_support),
            }
        )

    p2_report = load_json(P2_REPORT)
    p22_report = load_json(P22_REPORT)
    obs = {
        "lift_face_count": len(face_rows),
        "quadrilateral_face_count": sum(row["face_size"] == 4 for row in face_rows),
        "fused_kind_count": sum(row["kind_code"] == 2 for row in face_rows),
        "unique_vertex_count": len(unique_vertices),
        "hit_vertex_count": len(set(unique_vertices) & set(HIT_VERTICES)),
        "support_row_count": len(support_values),
        "support_positive_count": sum(value > 0 for value in support_values),
        "support_zero_count": sum(value == 0 for value in support_values),
        "min_slack_x1e12": min(support_values),
        "max_slack_x1e12": max(support_values),
        "p2_positive_support_flag": int(
            p2_report["witness"]["support"]["support_rows"] > 0
            and p2_report["all_checks_pass"] is True
        ),
        "p22_symbolic_carrier_flag": int(
            p22_report["witness"]["claim_boundary"]["symbolic_carrier"] == 1
        ),
        "geometric_lift_flag": 1,
        "new_c985_recompute_flag": 0,
        "face12_label_mask": face_rows[0]["label_mask"],
        "face22_label_mask": face_rows[1]["label_mask"],
        "face26_label_mask": face_rows[2]["label_mask"],
    }
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": int(obs[name]),
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "face_rows": face_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "p2_report": p2_report,
        "t2_report": load_json(T2_REPORT),
        "p22_report": p22_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p23_rows()
    face_table = table_from_rows(FACE_COLUMNS, rows["face_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p2_report = rows["p2_report"]
    t2_report = rows["t2_report"]
    p22_report = rows["p22_report"]
    checks = {
        "input_certificates_available": (
            p2_report.get("all_checks_pass") is True
            and t2_report.get("all_checks_pass") is True
            and p22_report.get("all_checks_pass") is True
        ),
        "p22_faces_lift_to_p2_fused_quads": (
            [row["face_id"] for row in rows["face_rows"]],
            [row["label_mask"] for row in rows["face_rows"]],
            obs["quadrilateral_face_count"],
            obs["fused_kind_count"],
        )
        == ([12, 22, 26], [30, 45, 51], 3, 3),
        "lift_vertices_match_hit_triangle_attachment": (
            obs["unique_vertex_count"],
            obs["hit_vertex_count"],
            [row["hit_vertex_a"] for row in rows["face_rows"]],
            [row["hit_vertex_b"] for row in rows["face_rows"]],
        )
        == (9, 3, [47, 46, 40], [46, 40, 47]),
        "lift_support_rows_are_positive": (
            obs["support_row_count"],
            obs["support_positive_count"],
            obs["support_zero_count"],
            obs["min_slack_x1e12"],
            obs["max_slack_x1e12"],
        )
        == (132, 132, 0, 363_262_450_397, 2_602_092_146_127),
        "carrier_boundaries_are_explicit": (
            obs["p2_positive_support_flag"],
            obs["p22_symbolic_carrier_flag"],
            obs["geometric_lift_flag"],
            obs["new_c985_recompute_flag"],
        )
        == (1, 1, 1, 0),
        "table_shapes_match_codebooks": (
            tuple(face_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (3, len(FACE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "symbolic_to_geometric_face_lift",
        "lift_faces": [
            {
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "cycle": [
                    row["cycle_v0"],
                    row["cycle_v1"],
                    row["cycle_v2"],
                    row["cycle_v3"],
                ],
                "original_vertices": [
                    row["orig_v0"],
                    row["orig_v1"],
                    row["orig_v2"],
                    row["orig_v3"],
                ],
                "min_slack_x1e12": row["min_slack_x1e12"],
            }
            for row in rows["face_rows"]
        ],
        "support": {
            "support_rows": obs["support_row_count"],
            "positive_support_rows": obs["support_positive_count"],
            "min_slack_x1e12": obs["min_slack_x1e12"],
            "max_slack_x1e12": obs["max_slack_x1e12"],
        },
        "claim_boundary": {
            "geometric_face_lift": obs["geometric_lift_flag"],
            "new_c985_recompute": obs["new_c985_recompute_flag"],
        },
        "reading": (
            "The p22 symbolic carrier has an explicit p2 geometric face lift: "
            "its three fused masks are precisely the three fused quadrilateral "
            "faces attached to the hit triangle. Their support rows are all "
            "strictly positive. C985 associator data has not yet been recomputed "
            "on this lifted geometric carrier."
        ),
        "face_table_sha256": sha_array(face_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p23 = {
        "schema": "eta6.p23@1",
        "object": "eta6",
        "construction": {
            "source": "p22 symbolic carrier plus p2 geometric carrier",
            "test": "symbolic-to-geometric fused-face lift",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p23.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P23_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The p22 symbolic carrier lifts to the existing p2 geometric "
            "carrier: faces 12, 22, and 26 are fused quadrilateral faces with "
            "masks 30, 45, and 51, and their 132 support rows are strictly "
            "positive. This certifies the geometric face lift, not a new C985 "
            "associator/pentagon recomputation on the lifted carrier."
        ),
        "stage_protocol": {
            "draft": "start from p22, p2, and t2",
            "witness": "match p22 fused masks to p2 fused quadrilateral faces",
            "coherence": "check hit-triangle attachment and strict support positivity",
            "closure": "certify the symbolic-to-geometric face lift",
            "emit": "emit compact p23 artifacts and the next C985 seam",
        },
        "inputs": {
            "p2_report": input_entry(
                P2_REPORT,
                {
                    "status": p2_report.get("status"),
                    "certificate_sha256": p2_report.get("certificate_sha256"),
                },
            ),
            "p2_faces": input_entry(P2_FACES),
            "p2_verts": input_entry(P2_VERTS),
            "p2_supp": input_entry(P2_SUPP),
            "t2_report": input_entry(
                T2_REPORT,
                {
                    "status": t2_report.get("status"),
                    "certificate_sha256": t2_report.get("certificate_sha256"),
                },
            ),
            "t2_fuse": input_entry(T2_FUSE),
            "p22_report": input_entry(
                P22_REPORT,
                {
                    "status": p22_report.get("status"),
                    "certificate_sha256": p22_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p23": relpath(OUT_DIR / "p23.json"),
            "faces_csv": relpath(OUT_DIR / "faces.csv"),
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
                "p22 symbolic carrier lifts to p2 fused quadrilateral faces",
                "lifted faces carry masks [30,45,51]",
                "lifted faces attach to the p2 hit triangle",
                "all support rows on the lifted faces are strictly positive",
            ],
            "does_not_certify_because_out_of_scope": [
                "new C985 associator data on the lifted geometric carrier",
                "new pentagon recomputation after the p21/p22 gate",
                "global automaton closure after repeated geometric lifts",
            ],
        },
        "next_highest_yield_item": (
            "Start p24 by recomputing C985 F-address/associator semantics on "
            "the p23 lifted geometric carrier."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p23.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p23.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p23": p23,
        "faces_csv": csv_text(FACE_COLUMNS, rows["face_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "face_table": face_table,
        "obs_table": obs_table,
        "cert": cert,
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
    write_json(OUT_DIR / "p23.json", payloads["p23"])
    (OUT_DIR / "faces.csv").write_text(payloads["faces_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        face_table=payloads["face_table"],
        observable_table=payloads["obs_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
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
