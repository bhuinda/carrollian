from __future__ import annotations

import csv
import itertools
import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from . import derive_eta6_p2 as p2
    from . import derive_eta6_xfer as xfer
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    import derive_c985_eta6_truncated_skeleton as skeleton
    import derive_eta6_p2 as p2
    import derive_eta6_xfer as xfer
    from paths import D20_INVARIANTS, ROOT


pair = p2.pair

THEOREM_ID = "eta6_t2"
STATUS = "ETA6_T2_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

P2_REPORT = p2.OUT_DIR / "report.json"
XFER_REPORT = xfer.OUT_DIR / "report.json"
P2_FACES = p2.OUT_DIR / "faces.csv"
P2_VERTS = p2.OUT_DIR / "verts.csv"
TRUNCATED_TABLES = skeleton.OUT_DIR / "eta6_truncated_skeleton_tables.npz"
HOL_REPORT = holonomy.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_t2.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_t2.py"

FUSE_COLUMNS = [
    "fuse_id",
    "face_id",
    "label_mask",
    "score",
    "label_count",
    "endpoint_inc_Bm",
    "endpoint_inc_Bp",
    "endpoint_inc_Vm",
    "endpoint_inc_Vp",
    "endpoint_inc_Sm",
    "endpoint_inc_Sp",
]
LABEL_COLUMNS = [
    "label_id",
    "known_count",
    "fused_count",
    "total_count",
    "target_count",
    "holonomy_coeff",
    "eta_coeff",
    "pairing_contribution",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "face_count": 0,
    "known_face_count": 1,
    "fused_face_count": 2,
    "known_label_count_min": 3,
    "known_label_count_max": 4,
    "target_label_count": 5,
    "fused_label_size": 6,
    "candidate_assignment_count": 7,
    "best_assignment_count": 8,
    "best_score": 9,
    "total_label_count_min": 10,
    "total_label_count_max": 11,
    "label_counts_preserved_flag": 12,
    "eta_weight": 13,
    "holonomy_weight": 14,
    "holonomy_eta_pairing": 15,
    "noncubic_transfer_flag": 16,
    "transfer_obstruction_flag": 17,
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


def read_csv_ints(path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def mask_from_labels(labels: tuple[str, ...] | list[str]) -> int:
    index = {label: label_id for label_id, label in enumerate(skeleton.H6_LABELS)}
    mask = 0
    for label in labels:
        mask |= 1 << index[label]
    return mask


def mask_size(mask: int) -> int:
    return int(mask.bit_count())


def mask_score(mask: int, scores: list[int]) -> int:
    return sum(scores[index] for index in range(6) if (mask >> index) & 1)


def endpoint_scores(
    face: dict[str, int],
    p2_original_by_vertex: dict[int, int],
    truncated_vertex_pairs: dict[int, tuple[int, int]],
    graph: dict[str, Any],
) -> list[int]:
    counts = {label: 0 for label in skeleton.H6_LABELS}
    for index in range(face["face_size"]):
        original_vertex = p2_original_by_vertex[face[f"cycle_v{index}"]]
        center, neighbor = truncated_vertex_pairs[original_vertex]
        for source in (center, neighbor):
            for label in graph["vertices"][source]:
                counts[label] += 1
    return [counts[label] for label in skeleton.H6_LABELS]


def build_transfer_rows() -> dict[str, Any]:
    p2_faces = read_csv_ints(P2_FACES)
    p2_verts = read_csv_ints(P2_VERTS)
    p2_original_by_vertex = {
        row["vertex_id"]: row["original_vertex_id"]
        for row in p2_verts
    }
    graph = skeleton.load_public_d20_graph()
    derived = skeleton.build_dual_and_truncation(graph)
    missing = xfer.primal_missing_labels(graph, derived)
    tables = np.load(TRUNCATED_TABLES, allow_pickle=False)
    truncated_vertex_pairs = {
        int(row[0]): (int(row[1]), int(row[2]))
        for row in np.asarray(tables["vertex_table"], dtype=np.int64)
    }
    hol_report = load_json(HOL_REPORT)
    eta = [int(value) for value in hol_report["witness"]["eta6_vector"]]
    hol = [int(value) for value in hol_report["witness"]["holonomy_vector"]]

    known_counts = [0] * 6
    fused_faces = []
    for face in p2_faces:
        if face["old_face_id"] >= 0:
            labels = xfer.face_labels(
                face["old_face_id"],
                face["source_id"],
                graph,
                missing,
            )
            for label in labels:
                known_counts[skeleton.H6_LABELS.index(label)] += 1
        else:
            fused_faces.append(face)

    target = 12
    masks = [
        sum(1 << index for index in combo)
        for combo in itertools.combinations(range(6), 4)
    ]
    scores = [
        endpoint_scores(face, p2_original_by_vertex, truncated_vertex_pairs, graph)
        for face in fused_faces
    ]
    candidates = []
    best_score: int | None = None
    best = []
    for assignment in itertools.product(masks, repeat=len(fused_faces)):
        fused_counts = [
            sum((mask >> label_id) & 1 for mask in assignment)
            for label_id in range(6)
        ]
        if any(
            known_counts[label_id] + fused_counts[label_id] != target
            for label_id in range(6)
        ):
            continue
        score = sum(
            mask_score(mask, scores[index])
            for index, mask in enumerate(assignment)
        )
        candidates.append((score, assignment))
        if best_score is None or score > best_score:
            best_score = score
            best = [assignment]
        elif score == best_score:
            best.append(assignment)

    if best_score is None or not best:
        best_score = 0
        best_assignment: tuple[int, ...] = tuple()
    else:
        best_assignment = best[0]

    fused_rows = []
    fused_counts = [0] * 6
    for fuse_id, (face, mask, score_row) in enumerate(
        zip(fused_faces, best_assignment, scores)
    ):
        for label_id in range(6):
            fused_counts[label_id] += (mask >> label_id) & 1
        fused_rows.append(
            {
                "fuse_id": fuse_id,
                "face_id": face["face_id"],
                "label_mask": mask,
                "score": mask_score(mask, score_row),
                "label_count": mask_size(mask),
                "endpoint_inc_Bm": score_row[0],
                "endpoint_inc_Bp": score_row[1],
                "endpoint_inc_Vm": score_row[2],
                "endpoint_inc_Vp": score_row[3],
                "endpoint_inc_Sm": score_row[4],
                "endpoint_inc_Sp": score_row[5],
            }
        )

    total_counts = [
        known_counts[label_id] + fused_counts[label_id]
        for label_id in range(6)
    ]
    label_rows = [
        {
            "label_id": label_id,
            "known_count": known_counts[label_id],
            "fused_count": fused_counts[label_id],
            "total_count": total_counts[label_id],
            "target_count": target,
            "holonomy_coeff": hol[label_id],
            "eta_coeff": eta[label_id],
            "pairing_contribution": eta[label_id] & hol[label_id],
        }
        for label_id in range(6)
    ]
    pairing = sum(row["pairing_contribution"] for row in label_rows) % 2
    obs_values = {
        "face_count": len(p2_faces),
        "known_face_count": len(p2_faces) - len(fused_faces),
        "fused_face_count": len(fused_faces),
        "known_label_count_min": min(known_counts),
        "known_label_count_max": max(known_counts),
        "target_label_count": target,
        "fused_label_size": 4,
        "candidate_assignment_count": len(candidates),
        "best_assignment_count": len(best),
        "best_score": best_score,
        "total_label_count_min": min(total_counts) if total_counts else 0,
        "total_label_count_max": max(total_counts) if total_counts else 0,
        "label_counts_preserved_flag": int(total_counts == [target] * 6),
        "eta_weight": sum(eta),
        "holonomy_weight": sum(hol),
        "holonomy_eta_pairing": pairing,
        "noncubic_transfer_flag": int(len(best) == 1 and total_counts == [target] * 6),
        "transfer_obstruction_flag": int(not (len(best) == 1 and total_counts == [target] * 6)),
    }
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": int(obs_values[name]),
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "p2_report": load_json(P2_REPORT),
        "xfer_report": load_json(XFER_REPORT),
        "hol_report": hol_report,
        "fused_rows": fused_rows,
        "label_rows": label_rows,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
        "best_assignment": list(best_assignment),
        "candidate_assignments": len(candidates),
    }


def build_payload_rows() -> dict[str, Any]:
    return build_transfer_rows()


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    fuse_table = table_from_rows(FUSE_COLUMNS, rows["fused_rows"])
    label_table = table_from_rows(LABEL_COLUMNS, rows["label_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["p2_report"].get("all_checks_pass") is True
            and rows["xfer_report"].get("all_checks_pass") is True
            and rows["hol_report"].get("all_checks_pass") is True
        ),
        "known_p2_faces_have_uniform_label_deficit": (
            obs["face_count"],
            obs["known_face_count"],
            obs["fused_face_count"],
            obs["known_label_count_min"],
            obs["known_label_count_max"],
            obs["target_label_count"],
        )
        == (29, 26, 3, 10, 10, 12),
        "unique_best_fused_quadrilateral_assignment_restores_counts": (
            obs["fused_label_size"],
            obs["candidate_assignment_count"],
            obs["best_assignment_count"],
            obs["best_score"],
            rows["best_assignment"],
            [row["fused_count"] for row in rows["label_rows"]],
            [row["total_count"] for row in rows["label_rows"]],
        )
        == (4, 90, 1, 57, [30, 45, 51], [2, 2, 2, 2, 2, 2], [12, 12, 12, 12, 12, 12]),
        "holonomy_pairing_survives_extended_transfer": (
            obs["eta_weight"],
            obs["holonomy_weight"],
            obs["holonomy_eta_pairing"],
            obs["label_counts_preserved_flag"],
            obs["noncubic_transfer_flag"],
            obs["transfer_obstruction_flag"],
        )
        == (6, 3, 1, 1, 1, 0),
        "table_shapes_match_codebooks": (
            tuple(fuse_table.shape),
            tuple(label_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (3, len(FUSE_COLUMNS)),
            (6, len(LABEL_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "noncubic_transfer_exists",
        "fused_face_masks": rows["best_assignment"],
        "fused_face_ids": [row["face_id"] for row in rows["fused_rows"]],
        "candidate_assignment_count": obs["candidate_assignment_count"],
        "best_assignment_count": obs["best_assignment_count"],
        "best_score": obs["best_score"],
        "label_counts": [row["total_count"] for row in rows["label_rows"]],
        "eta6_after": [row["eta_coeff"] for row in rows["label_rows"]],
        "holonomy_after": [row["holonomy_coeff"] for row in rows["label_rows"]],
        "holonomy_eta_pairing_after": obs["holonomy_eta_pairing"],
        "reading": (
            "The p2 carrier needs three 4-label fused faces. With global H6 "
            "count preservation and local endpoint-incidence maximization, the "
            "assignment is unique, so the degree-5 triangle is not yet a "
            "transfer obstruction."
        ),
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "fuse_table_sha256": pair.parent.sha_array(fuse_table),
        "label_table_sha256": pair.parent.sha_array(label_table),
    }
    t2 = {
        "schema": "eta6.t2@1",
        "object": "eta6",
        "construction": {
            "transfer": "non-cubic fused-face H6 transfer on eta6_p2",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.t2.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_T2_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6_p2 degree-5 triangle is not a transfer obstruction at the "
            "H6 label-count level. The 26 known p2 faces contribute count 10 "
            "to every H6 label; assigning four labels to each of the three "
            "fused quadrilateral faces, while preserving target count 12 and "
            "maximizing local endpoint incidence, has a unique optimum with "
            "masks [30,45,51]. The extended non-cubic transfer restores all "
            "six H6 counts to 12 and keeps eta6/holonomy pairing equal to 1."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p2, eta6_xfer, and eta6 holonomy",
            "witness": "enumerate fused-face 4-label assignments under H6 count preservation",
            "coherence": "select the unique local endpoint-incidence optimum and check eta6/holonomy pairing",
            "closure": "certify a non-cubic H6 transfer exists for p2 at the label-count level",
            "emit": "emit compact t2 artifacts, verifier command, and next seam",
        },
        "inputs": {
            "p2_report": pair.parent.input_entry(
                P2_REPORT,
                {
                    "status": rows["p2_report"].get("status"),
                    "certificate_sha256": rows["p2_report"].get("certificate_sha256"),
                },
            ),
            "xfer_report": pair.parent.input_entry(
                XFER_REPORT,
                {
                    "status": rows["xfer_report"].get("status"),
                    "certificate_sha256": rows["xfer_report"].get("certificate_sha256"),
                },
            ),
            "holonomy_report": pair.parent.input_entry(
                HOL_REPORT,
                {
                    "status": rows["hol_report"].get("status"),
                    "certificate_sha256": rows["hol_report"].get("certificate_sha256"),
                },
            ),
            "p2_faces": pair.parent.input_entry(P2_FACES),
            "p2_verts": pair.parent.input_entry(P2_VERTS),
            "truncated_tables": pair.parent.input_entry(TRUNCATED_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "t2": pair.parent.relpath(OUT_DIR / "t2.json"),
            "fuse_csv": pair.parent.relpath(OUT_DIR / "fuse.csv"),
            "labels_csv": pair.parent.relpath(OUT_DIR / "labels.csv"),
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
                "a unique non-cubic fused-face H6 label transfer for eta6_p2 at count level",
                "preservation of all six H6 label counts at 12",
                "eta6/holonomy pairing remains 1 under the extended transfer",
            ],
            "does_not_certify_because_not_required": [
                "C985 associator data on 4-label fused faces",
                "full local F-symbol semantics for the degree-5 triangle",
                "global automaton closure after repeated non-cubic transfers",
            ],
        },
        "next_highest_yield_item": (
            "Lift the t2 fused-face masks into explicit F-symbol addresses, then "
            "test whether the 4-label faces admit C985 associator semantics."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.t2.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.t2.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "t2": t2,
        "fuse_csv": csv_text(FUSE_COLUMNS, rows["fused_rows"]),
        "labels_csv": csv_text(LABEL_COLUMNS, rows["label_rows"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "fuse_table": fuse_table,
        "label_table": label_table,
        "obs_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = p2.repl.ext.nonholonomic.preservation.INDEX_PATH
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
    pair.parent.write_json(OUT_DIR / "t2.json", payloads["t2"])
    (OUT_DIR / "fuse.csv").write_text(payloads["fuse_csv"], encoding="utf-8")
    (OUT_DIR / "labels.csv").write_text(payloads["labels_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        fuse_table=payloads["fuse_table"],
        label_table=payloads["label_table"],
        observable_table=payloads["obs_table"],
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
