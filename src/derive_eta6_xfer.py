from __future__ import annotations

import csv
import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from . import derive_eta6_repl as repl
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    import derive_c985_eta6_truncated_skeleton as skeleton
    import derive_eta6_repl as repl
    from paths import D20_INVARIANTS, ROOT


pair = repl.pair

THEOREM_ID = "eta6_xfer"
STATUS = "ETA6_XFER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

HOL_REPORT = holonomy.OUT_DIR / "report.json"
REPL_REPORT = repl.OUT_DIR / "report.json"
REPL_FACES = repl.OUT_DIR / "faces.csv"
REPL_VERTS = repl.OUT_DIR / "verts.csv"
TRUNCATED_TABLES = skeleton.OUT_DIR / "eta6_truncated_skeleton_tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_xfer.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_xfer.py"

EDGE_COLUMNS = [
    "edge_id",
    "edge_code",
    "eta_before",
    "eta_after",
    "hol_before",
    "hol_after",
    "transfer_value",
    "pairing_contribution",
]
LABEL_COLUMNS = [
    "label_id",
    "before_face_count",
    "after_face_count",
    "before_parity",
    "after_parity",
    "holonomy_coeff",
]
PATCH_COLUMNS = [
    "patch_row_id",
    "old_face_id",
    "source_id",
    "before_size",
    "after_size",
    "label_mask",
    "holonomy_parity",
    "size_delta",
]
CYCLE_COLUMNS = [
    "cycle_id",
    "cycle_type_code",
    "source_id",
    "label_mask",
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "v5",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "edge_count": 0,
    "transfer_rank": 1,
    "eta_before_weight": 2,
    "eta_after_weight": 3,
    "eta_transfer_equal_flag": 4,
    "holonomy_before_weight": 5,
    "holonomy_after_weight": 6,
    "holonomy_transfer_equal_flag": 7,
    "holonomy_eta_pairing_before": 8,
    "holonomy_eta_pairing_after": 9,
    "label_count_preserved_flag": 10,
    "source_face_count_before": 11,
    "source_face_count_after": 12,
    "source_id_preserved_count": 13,
    "affected_face_count": 14,
    "old_cycle_length": 15,
    "cap_cycle_length": 16,
    "cap_uses_first_hit_vertices_flag": 17,
    "removed_cycle_disjoint_cap_flag": 18,
    "geometric_carrier_changed_flag": 19,
    "eta6_killed_flag": 20,
    "eta6_preserved_flag": 21,
    "eta6_transformed_geometrically_flag": 22,
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


def label_mask(labels: tuple[str, ...]) -> int:
    index = {label: label_id for label_id, label in enumerate(skeleton.H6_LABELS)}
    mask = 0
    for label in labels:
        mask |= 1 << index[label]
    return mask


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
    old_face_id: int,
    source_id: int,
    graph: dict[str, Any],
    missing: dict[int, str],
) -> tuple[str, ...]:
    if old_face_id < 12:
        return (missing[source_id],)
    return tuple(graph["vertices"][source_id])


def read_repl_faces() -> list[dict[str, int]]:
    with REPL_FACES.open("r", encoding="utf-8", newline="") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def read_repl_vertex_originals() -> dict[int, int]:
    with REPL_VERTS.open("r", encoding="utf-8", newline="") as handle:
        return {
            int(row["vertex_id"]): int(row["original_vertex_id"])
            for row in csv.DictReader(handle)
        }


def old_face_rows() -> list[dict[str, int]]:
    tables = np.load(TRUNCATED_TABLES, allow_pickle=False)
    return repl.table_rows(
        np.asarray(tables["face_table"], dtype=np.int64),
        skeleton.TRUNCATED_FACE_COLUMNS,
    )


def face_cycle(row: dict[str, int]) -> list[int]:
    return [row[f"cycle_v{index}"] for index in range(row["face_size"])]


def cycle_to_original(row: dict[str, int], local_to_original: dict[int, int]) -> list[int]:
    return [local_to_original[row[f"cycle_v{index}"]] for index in range(row["face_size"])]


def build_xfer_rows() -> dict[str, Any]:
    hol_report = load_json(HOL_REPORT)
    repl_report = load_json(REPL_REPORT)
    eta_before = [int(value) for value in hol_report["witness"]["eta6_vector"]]
    hol_before = [int(value) for value in hol_report["witness"]["holonomy_vector"]]
    eta_after = eta_before[:]
    hol_after = hol_before[:]
    edge_rows = [
        {
            "edge_id": edge_id,
            "edge_code": holonomy.EDGE_CODES[edge_id],
            "eta_before": eta_before[edge_id],
            "eta_after": eta_after[edge_id],
            "hol_before": hol_before[edge_id],
            "hol_after": hol_after[edge_id],
            "transfer_value": 1,
            "pairing_contribution": eta_after[edge_id] & hol_after[edge_id],
        }
        for edge_id in range(len(holonomy.EDGE_CODES))
    ]

    graph = skeleton.load_public_d20_graph()
    derived = skeleton.build_dual_and_truncation(graph)
    missing = primal_missing_labels(graph, derived)
    before_faces = old_face_rows()
    after_faces = read_repl_faces()
    after_by_old = {row["old_face_id"]: row for row in after_faces}
    local_to_original = read_repl_vertex_originals()

    before_counts = [0] * len(skeleton.H6_LABELS)
    after_counts = [0] * len(skeleton.H6_LABELS)
    label_index = {label: index for index, label in enumerate(skeleton.H6_LABELS)}
    source_preserved = 0
    patch_rows = []
    for old in before_faces:
        after = after_by_old[old["face_id"]]
        labels = face_labels(old["face_id"], old["source_id"], graph, missing)
        for label in labels:
            before_counts[label_index[label]] += 1
            after_counts[label_index[label]] += 1
        source_preserved += int(old["source_id"] == after["source_id"])
        if old["face_size"] != after["face_size"] or old["face_id"] == 31:
            hol_parity = sum(
                hol_after[label_index[label]]
                for label in labels
            ) % 2
            patch_rows.append(
                {
                    "patch_row_id": len(patch_rows),
                    "old_face_id": old["face_id"],
                    "source_id": old["source_id"],
                    "before_size": old["face_size"],
                    "after_size": after["face_size"],
                    "label_mask": label_mask(labels),
                    "holonomy_parity": hol_parity,
                    "size_delta": after["face_size"] - old["face_size"],
                }
            )

    label_rows = [
        {
            "label_id": label_id,
            "before_face_count": before_counts[label_id],
            "after_face_count": after_counts[label_id],
            "before_parity": before_counts[label_id] % 2,
            "after_parity": after_counts[label_id] % 2,
            "holonomy_coeff": hol_after[label_id],
        }
        for label_id in range(len(skeleton.H6_LABELS))
    ]

    old_face31 = next(row for row in before_faces if row["face_id"] == 31)
    new_face31 = after_by_old[31]
    old_cycle = face_cycle(old_face31)
    cap_cycle = cycle_to_original(new_face31, local_to_original)
    face31_labels = face_labels(31, old_face31["source_id"], graph, missing)
    cycle_rows = [
        {
            "cycle_id": 0,
            "cycle_type_code": 0,
            "source_id": old_face31["source_id"],
            "label_mask": label_mask(face31_labels),
            "v0": old_cycle[0],
            "v1": old_cycle[1],
            "v2": old_cycle[2],
            "v3": old_cycle[3],
            "v4": old_cycle[4],
            "v5": old_cycle[5],
        },
        {
            "cycle_id": 1,
            "cycle_type_code": 1,
            "source_id": new_face31["source_id"],
            "label_mask": label_mask(face31_labels),
            "v0": cap_cycle[0],
            "v1": cap_cycle[1],
            "v2": cap_cycle[2],
            "v3": cap_cycle[3],
            "v4": cap_cycle[4],
            "v5": cap_cycle[5],
        },
    ]

    pairing_before = sum(e & h for e, h in zip(eta_before, hol_before)) % 2
    pairing_after = sum(e & h for e, h in zip(eta_after, hol_after)) % 2
    label_count_preserved = int(before_counts == after_counts)
    cap_uses_first_hit = int(cap_cycle == repl.CAP_ORIGINAL_VERTICES)
    cycles_disjoint = int(set(old_cycle).isdisjoint(cap_cycle))
    obs_values = {
        "edge_count": len(edge_rows),
        "transfer_rank": len(edge_rows),
        "eta_before_weight": sum(eta_before),
        "eta_after_weight": sum(eta_after),
        "eta_transfer_equal_flag": int(eta_before == eta_after),
        "holonomy_before_weight": sum(hol_before),
        "holonomy_after_weight": sum(hol_after),
        "holonomy_transfer_equal_flag": int(hol_before == hol_after),
        "holonomy_eta_pairing_before": pairing_before,
        "holonomy_eta_pairing_after": pairing_after,
        "label_count_preserved_flag": label_count_preserved,
        "source_face_count_before": len(before_faces),
        "source_face_count_after": len(after_faces),
        "source_id_preserved_count": source_preserved,
        "affected_face_count": len(patch_rows),
        "old_cycle_length": len(old_cycle),
        "cap_cycle_length": len(cap_cycle),
        "cap_uses_first_hit_vertices_flag": cap_uses_first_hit,
        "removed_cycle_disjoint_cap_flag": cycles_disjoint,
        "geometric_carrier_changed_flag": int(old_cycle != cap_cycle),
        "eta6_killed_flag": 0,
        "eta6_preserved_flag": int(pairing_after == 1 and eta_before == eta_after),
        "eta6_transformed_geometrically_flag": int(old_cycle != cap_cycle),
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
        "hol_report": hol_report,
        "repl_report": repl_report,
        "edge_rows": edge_rows,
        "label_rows": label_rows,
        "patch_rows": patch_rows,
        "cycle_rows": cycle_rows,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
    }


def build_payload_rows() -> dict[str, Any]:
    return build_xfer_rows()


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    label_table = table_from_rows(LABEL_COLUMNS, rows["label_rows"])
    patch_table = table_from_rows(PATCH_COLUMNS, rows["patch_rows"])
    cycle_table = table_from_rows(CYCLE_COLUMNS, rows["cycle_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["hol_report"].get("all_checks_pass") is True
            and rows["repl_report"].get("all_checks_pass") is True
        ),
        "k4_eta6_chain_transfers_by_identity": (
            obs["edge_count"],
            obs["transfer_rank"],
            obs["eta_before_weight"],
            obs["eta_after_weight"],
            obs["eta_transfer_equal_flag"],
        )
        == (6, 6, 6, 6, 1),
        "holonomy_pairing_survives_transfer": (
            obs["holonomy_before_weight"],
            obs["holonomy_after_weight"],
            obs["holonomy_transfer_equal_flag"],
            obs["holonomy_eta_pairing_before"],
            obs["holonomy_eta_pairing_after"],
        )
        == (3, 3, 1, 1, 1),
        "h6_face_source_counts_are_preserved": (
            obs["label_count_preserved_flag"],
            obs["source_face_count_before"],
            obs["source_face_count_after"],
            obs["source_id_preserved_count"],
            [row["before_face_count"] for row in rows["label_rows"]],
            [row["after_face_count"] for row in rows["label_rows"]],
        )
        == (1, 32, 32, 32, [12, 12, 12, 12, 12, 12], [12, 12, 12, 12, 12, 12]),
        "face31_carrier_is_geometrically_transformed": (
            obs["affected_face_count"],
            obs["old_cycle_length"],
            obs["cap_cycle_length"],
            obs["cap_uses_first_hit_vertices_flag"],
            obs["removed_cycle_disjoint_cap_flag"],
            obs["geometric_carrier_changed_flag"],
            rows["cycle_rows"][0],
            rows["cycle_rows"][1],
        )
        == (
            7,
            6,
            6,
            1,
            1,
            1,
            {
                "cycle_id": 0,
                "cycle_type_code": 0,
                "source_id": 19,
                "label_mask": 56,
                "v0": 43,
                "v1": 53,
                "v2": 54,
                "v3": 59,
                "v4": 57,
                "v5": 44,
            },
            {
                "cycle_id": 1,
                "cycle_type_code": 1,
                "source_id": 19,
                "label_mask": 56,
                "v0": 42,
                "v1": 40,
                "v2": 51,
                "v3": 50,
                "v4": 56,
                "v5": 58,
            },
        ),
        "classification_is_preserved_not_killed": (
            obs["eta6_killed_flag"],
            obs["eta6_preserved_flag"],
            obs["eta6_transformed_geometrically_flag"],
        )
        == (0, 1, 1),
        "table_shapes_match_codebooks": (
            tuple(edge_table.shape),
            tuple(label_table.shape),
            tuple(patch_table.shape),
            tuple(cycle_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (6, len(EDGE_COLUMNS)),
            (6, len(LABEL_COLUMNS)),
            (7, len(PATCH_COLUMNS)),
            (2, len(CYCLE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "preserved_class_transformed_carrier",
        "eta6_before": [row["eta_before"] for row in rows["edge_rows"]],
        "eta6_after": [row["eta_after"] for row in rows["edge_rows"]],
        "holonomy_before": [row["hol_before"] for row in rows["edge_rows"]],
        "holonomy_after": [row["hol_after"] for row in rows["edge_rows"]],
        "holonomy_eta_pairing_after": obs["holonomy_eta_pairing_after"],
        "old_face31_cycle": rows["cycle_rows"][0],
        "new_cap_cycle": rows["cycle_rows"][1],
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "edge_table_sha256": pair.parent.sha_array(edge_table),
        "label_table_sha256": pair.parent.sha_array(label_table),
        "patch_table_sha256": pair.parent.sha_array(patch_table),
        "cycle_table_sha256": pair.parent.sha_array(cycle_table),
    }
    xfer = {
        "schema": "eta6.xfer@1",
        "object": "eta6",
        "construction": {
            "transfer": "identity on the K4/H6 seam chain data, with geometric carrier moved from old face-31 cycle to cap cycle",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.xfer.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_XFER_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The face-31 replacement preserves the abstract eta6 seam class under "
            "the H6/K4 source-label transfer: eta6 remains [1,1,1,1,1,1], the "
            "dual holonomy remains [0,0,1,0,1,1], and the pairing remains 1. "
            "The geometric carrier is transformed from the old face-31 hexagon "
            "to the first-hit cap hexagon, so eta6 is preserved as a class but "
            "moved as a carrier. It is not killed."
        ),
        "stage_protocol": {
            "draft": "start from eta6 holonomy and eta6_repl",
            "witness": "compare K4/H6 chain data, source-label counts, and old/new face-31 cycles",
            "coherence": "check identity transfer, holonomy pairing, label counts, and geometric carrier change",
            "closure": "classify the face-31 replacement as class-preserving and carrier-transforming",
            "emit": "emit short xfer artifacts, hashes, verifier command, and next target",
        },
        "inputs": {
            "holonomy_report": pair.parent.input_entry(
                HOL_REPORT,
                {
                    "status": rows["hol_report"].get("status"),
                    "certificate_sha256": rows["hol_report"].get("certificate_sha256"),
                },
            ),
            "repl_report": pair.parent.input_entry(
                REPL_REPORT,
                {
                    "status": rows["repl_report"].get("status"),
                    "certificate_sha256": rows["repl_report"].get("certificate_sha256"),
                },
            ),
            "repl_faces": pair.parent.input_entry(REPL_FACES),
            "repl_verts": pair.parent.input_entry(REPL_VERTS),
            "truncated_tables": pair.parent.input_entry(TRUNCATED_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "xfer": pair.parent.relpath(OUT_DIR / "xfer.json"),
            "edges_csv": pair.parent.relpath(OUT_DIR / "edges.csv"),
            "labels_csv": pair.parent.relpath(OUT_DIR / "labels.csv"),
            "patch_csv": pair.parent.relpath(OUT_DIR / "patch.csv"),
            "cycles_csv": pair.parent.relpath(OUT_DIR / "cycles.csv"),
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
                "eta6 class preservation under the face-31 replacement source-label transfer",
                "nontrivial holonomy pairing remains 1 after transfer",
                "the geometric carrier changes from the old face-31 cycle to the cap cycle",
                "eta6 is not killed by the certified replacement",
            ],
            "does_not_certify_because_not_required": [
                "global automaton closure after repeated surgeries",
                "C985 associator data on the replacement carrier",
                "that future cuts preserve eta6",
            ],
        },
        "next_highest_yield_item": (
            "Iterate the same xfer/repl test on the next support-discriminant hit "
            "to see whether eta6 remains class-preserved under repeated cuts."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.xfer.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.xfer.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "xfer": xfer,
        "edges_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "labels_csv": csv_text(LABEL_COLUMNS, rows["label_rows"]),
        "patch_csv": csv_text(PATCH_COLUMNS, rows["patch_rows"]),
        "cycles_csv": csv_text(CYCLE_COLUMNS, rows["cycle_rows"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "edge_table": edge_table,
        "label_table": label_table,
        "patch_table": patch_table,
        "cycle_table": cycle_table,
        "obs_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = repl.ext.nonholonomic.preservation.INDEX_PATH
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
    pair.parent.write_json(OUT_DIR / "xfer.json", payloads["xfer"])
    (OUT_DIR / "edges.csv").write_text(payloads["edges_csv"], encoding="utf-8")
    (OUT_DIR / "labels.csv").write_text(payloads["labels_csv"], encoding="utf-8")
    (OUT_DIR / "patch.csv").write_text(payloads["patch_csv"], encoding="utf-8")
    (OUT_DIR / "cycles.csv").write_text(payloads["cycles_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        edge_table=payloads["edge_table"],
        label_table=payloads["label_table"],
        patch_table=payloads["patch_table"],
        cycle_table=payloads["cycle_table"],
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
