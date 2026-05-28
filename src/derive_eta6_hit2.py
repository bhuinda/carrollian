from __future__ import annotations

import csv
import json
from collections import Counter
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from . import derive_eta6_repl as repl
    from . import derive_eta6_xfer as xfer
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_eta6_truncated_skeleton as skeleton
    import derive_eta6_repl as repl
    import derive_eta6_xfer as xfer
    from paths import D20_INVARIANTS, ROOT


pair = repl.pair

THEOREM_ID = "eta6_hit2"
STATUS = "ETA6_HIT2_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REPL_REPORT = repl.OUT_DIR / "report.json"
XFER_REPORT = xfer.OUT_DIR / "report.json"
REPL_FACES = repl.OUT_DIR / "faces.csv"
REPL_VERTS = repl.OUT_DIR / "verts.csv"
REPL_SUPP = repl.OUT_DIR / "supp.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_hit2.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_hit2.py"

HIT_COLUMNS = [
    "hit_id",
    "support_row_id",
    "face_id",
    "local_vertex_id",
    "original_vertex_id",
    "slack_x1e12",
    "face_weight",
    "tau_num",
    "tau_den",
]
COLLAPSE_COLUMNS = [
    "row_id",
    "face_id",
    "old_face_id",
    "before_size",
    "after_size",
    "collapse_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "support_row_count": 0,
    "negative_ray_row_count": 1,
    "first_hit_row_count": 2,
    "first_hit_face_id": 3,
    "first_tau_numerator": 4,
    "first_tau_denominator": 5,
    "next_tau_numerator": 6,
    "next_tau_denominator": 7,
    "post_tau_numerator": 8,
    "post_tau_denominator": 9,
    "survivor_row_count": 10,
    "positive_survivor_count": 11,
    "nonpositive_survivor_count": 12,
    "min_survivor_slack_numerator": 13,
    "min_survivor_slack_denominator": 14,
    "removed_negative_post_count": 15,
    "support_cone_positive_after_hit_cut_flag": 16,
    "naive_removed_vertex_count": 17,
    "naive_cap_vertex_count": 18,
    "collapsed_face_count": 19,
    "collapsed_to_vertex_count": 20,
    "collapsed_to_edge_count": 21,
    "min_naive_face_size": 22,
    "edge_incidence_bad_edge_count": 23,
    "simple_replacement_valid_flag": 24,
    "three_edge_collapse_flag": 25,
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


def frac_parts(value: Fraction) -> tuple[int, int]:
    return int(value.numerator), int(value.denominator)


def read_csv_ints(path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def face_cycle(face: dict[str, int]) -> list[int]:
    return [face[f"cycle_v{index}"] for index in range(face["face_size"])]


def face_weights(faces: list[dict[str, int]]) -> dict[int, int]:
    graph = skeleton.load_public_d20_graph()
    derived = skeleton.build_dual_and_truncation(graph)
    missing = xfer.primal_missing_labels(graph, derived)
    holonomy_by_label = {
        label: int(value)
        for label, value in zip(skeleton.H6_LABELS, [0, 0, 1, 0, 1, 1])
    }
    weights = {}
    for face in faces:
        labels = xfer.face_labels(
            face["old_face_id"],
            face["source_id"],
            graph,
            missing,
        )
        active = sum(holonomy_by_label[label] for label in labels)
        polarity = 1 if active % 2 else -1
        weights[face["face_id"]] = polarity * (face["face_id"] + 1) ** 2
    return weights


def build_hit_rows() -> dict[str, Any]:
    faces = read_csv_ints(REPL_FACES)
    verts = read_csv_ints(REPL_VERTS)
    support_rows = read_csv_ints(REPL_SUPP)
    original_by_local = {
        row["vertex_id"]: row["original_vertex_id"]
        for row in verts
    }
    weights = face_weights(faces)
    critical = []
    for row in support_rows:
        weight = weights[row["face_id"]]
        if weight < 0:
            critical.append(
                (
                    Fraction(row["slack_x1e12"], -weight),
                    row["support_row_id"],
                    row["face_id"],
                    row["vertex_id"],
                    row["slack_x1e12"],
                    weight,
                )
            )
    critical.sort()
    first_tau = critical[0][0]
    first_hits = [row for row in critical if row[0] == first_tau]
    next_tau = next(row[0] for row in critical if row[0] > first_tau)
    post_tau = (first_tau + next_tau) / 2
    hit_ids = {row[1] for row in first_hits}
    hit_rows = []
    for hit_id, row in enumerate(first_hits):
        tau_num, tau_den = frac_parts(row[0])
        hit_rows.append(
            {
                "hit_id": hit_id,
                "support_row_id": row[1],
                "face_id": row[2],
                "local_vertex_id": row[3],
                "original_vertex_id": original_by_local[row[3]],
                "slack_x1e12": row[4],
                "face_weight": row[5],
                "tau_num": tau_num,
                "tau_den": tau_den,
            }
        )

    nonpositive_survivor_count = 0
    positive_survivor_count = 0
    removed_negative_post_count = 0
    min_survivor: Fraction | None = None
    for row in support_rows:
        weight = weights[row["face_id"]]
        value = Fraction(row["slack_x1e12"]) + post_tau * weight
        if row["support_row_id"] in hit_ids:
            if value < 0:
                removed_negative_post_count += 1
            continue
        if value <= 0:
            nonpositive_survivor_count += 1
        else:
            positive_survivor_count += 1
        if min_survivor is None or value < min_survivor:
            min_survivor = value
    if min_survivor is None:
        raise ValueError("no survivor rows")

    face31 = next(face for face in faces if face["face_id"] == 31)
    removed = set(face_cycle(face31))
    cap = [row["local_vertex_id"] for row in hit_rows]
    collapse_rows = []
    edge_counter: Counter[tuple[int, int]] = Counter()
    for face in faces:
        cycle = face_cycle(face)
        if face["face_id"] == 31:
            after_cycle = cap
        elif removed & set(cycle):
            after_cycle = [vertex for vertex in cycle if vertex not in removed]
        else:
            after_cycle = cycle
        if len(after_cycle) >= 1:
            for left, right in zip(after_cycle, after_cycle[1:] + after_cycle[:1]):
                edge_counter[tuple(sorted((left, right)))] += 1
        if len(after_cycle) < 3:
            collapse_rows.append(
                {
                    "row_id": len(collapse_rows),
                    "face_id": face["face_id"],
                    "old_face_id": face["old_face_id"],
                    "before_size": face["face_size"],
                    "after_size": len(after_cycle),
                    "collapse_code": len(after_cycle),
                }
            )
    bad_edge_count = sum(1 for count in edge_counter.values() if count != 2)
    first_num, first_den = frac_parts(first_tau)
    next_num, next_den = frac_parts(next_tau)
    post_num, post_den = frac_parts(post_tau)
    min_num, min_den = frac_parts(min_survivor)
    obs_values = {
        "support_row_count": len(support_rows),
        "negative_ray_row_count": len(critical),
        "first_hit_row_count": len(hit_rows),
        "first_hit_face_id": hit_rows[0]["face_id"],
        "first_tau_numerator": first_num,
        "first_tau_denominator": first_den,
        "next_tau_numerator": next_num,
        "next_tau_denominator": next_den,
        "post_tau_numerator": post_num,
        "post_tau_denominator": post_den,
        "survivor_row_count": len(support_rows) - len(hit_rows),
        "positive_survivor_count": positive_survivor_count,
        "nonpositive_survivor_count": nonpositive_survivor_count,
        "min_survivor_slack_numerator": min_num,
        "min_survivor_slack_denominator": min_den,
        "removed_negative_post_count": removed_negative_post_count,
        "support_cone_positive_after_hit_cut_flag": int(nonpositive_survivor_count == 0),
        "naive_removed_vertex_count": len(removed),
        "naive_cap_vertex_count": len(cap),
        "collapsed_face_count": len(collapse_rows),
        "collapsed_to_vertex_count": sum(row["after_size"] == 1 for row in collapse_rows),
        "collapsed_to_edge_count": sum(row["after_size"] == 2 for row in collapse_rows),
        "min_naive_face_size": min(row["after_size"] for row in collapse_rows),
        "edge_incidence_bad_edge_count": bad_edge_count,
        "simple_replacement_valid_flag": int(not collapse_rows and bad_edge_count == 0),
        "three_edge_collapse_flag": int(len(hit_rows) == 3 and len(collapse_rows) == 6),
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
        "hit_rows": hit_rows,
        "collapse_rows": collapse_rows,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
    }


def build_payload_rows() -> dict[str, Any]:
    return {
        "repl_report": load_json(REPL_REPORT),
        "xfer_report": load_json(XFER_REPORT),
        "hit": build_hit_rows(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    hit = rows["hit"]
    hit_table = table_from_rows(HIT_COLUMNS, hit["hit_rows"])
    collapse_table = table_from_rows(COLLAPSE_COLUMNS, hit["collapse_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, hit["obs_rows"])
    obs = hit["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["repl_report"].get("all_checks_pass") is True
            and rows["xfer_report"].get("all_checks_pass") is True
        ),
        "second_hit_is_exact_face31_three_vertex_hit": (
            obs["support_row_count"],
            obs["negative_ray_row_count"],
            obs["first_hit_row_count"],
            obs["first_hit_face_id"],
            obs["first_tau_numerator"],
            obs["first_tau_denominator"],
            [row["support_row_id"] for row in hit["hit_rows"]],
            [row["local_vertex_id"] for row in hit["hit_rows"]],
            [row["original_vertex_id"] for row in hit["hit_rows"]],
        )
        == (
            1_560,
            782,
            3,
            31,
            118_940_696_591,
            512,
            [1552, 1558, 1559],
            [41, 50, 51],
            [41, 52, 55],
        ),
        "post_hit_survivor_cone_stays_positive": (
            obs["next_tau_numerator"],
            obs["next_tau_denominator"],
            obs["post_tau_numerator"],
            obs["post_tau_denominator"],
            obs["survivor_row_count"],
            obs["positive_survivor_count"],
            obs["nonpositive_survivor_count"],
            obs["min_survivor_slack_numerator"],
            obs["min_survivor_slack_denominator"],
            obs["removed_negative_post_count"],
            obs["support_cone_positive_after_hit_cut_flag"],
        )
        == (
            96_225_044_865,
            256,
            311_390_786_321,
            1_024,
            1_557,
            1_557,
            0,
            73_509_393_139,
            1,
            3,
            1,
        ),
        "naive_second_replacement_collapses_neighbor_faces": (
            obs["naive_removed_vertex_count"],
            obs["naive_cap_vertex_count"],
            obs["collapsed_face_count"],
            obs["collapsed_to_vertex_count"],
            obs["collapsed_to_edge_count"],
            obs["min_naive_face_size"],
            obs["edge_incidence_bad_edge_count"],
            obs["simple_replacement_valid_flag"],
            obs["three_edge_collapse_flag"],
        )
        == (6, 3, 6, 3, 3, 1, 15, 0, 1),
        "collapsed_faces_are_expected_neighbors": [
            row["face_id"] for row in hit["collapse_rows"]
        ]
        == [8, 10, 11, 25, 29, 30],
        "table_shapes_match_codebooks": (
            tuple(hit_table.shape),
            tuple(collapse_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (3, len(HIT_COLUMNS)),
            (6, len(COLLAPSE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "three_edge_collapse_obstruction",
        "hit_original_vertices": [row["original_vertex_id"] for row in hit["hit_rows"]],
        "hit_local_vertices": [row["local_vertex_id"] for row in hit["hit_rows"]],
        "first_tau": {
            "numerator": obs["first_tau_numerator"],
            "denominator": obs["first_tau_denominator"],
        },
        "post_tau": {
            "numerator": obs["post_tau_numerator"],
            "denominator": obs["post_tau_denominator"],
        },
        "collapsed_neighbor_faces": [row["face_id"] for row in hit["collapse_rows"]],
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "hit_table_sha256": pair.parent.sha_array(hit_table),
        "collapse_table_sha256": pair.parent.sha_array(collapse_table),
    }
    hit2 = {
        "schema": "eta6.hit2@1",
        "object": "eta6",
        "construction": {
            "next_hit": "second support-discriminant hit on the eta6_repl carrier",
            "classification": witness["classification"],
            "reading": "the survivor cone remains positive, but the naive second cap collapses neighbor faces",
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.hit2.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_HIT2_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The next support-discriminant hit after eta6_repl is again on face "
            "31, but it is a three-vertex hit at original vertices 41,52,55. "
            "Deleting just those hit support rows leaves all 1,557 survivor "
            "support inequalities positive. However, applying the previous "
            "simple cap rule would collapse six neighboring faces, so the next "
            "step is a three-edge collapse problem, not another same-type cap."
        ),
        "stage_protocol": {
            "draft": "start from eta6_repl and eta6_xfer",
            "witness": "compute the next hpol support-discriminant hit on the replacement carrier",
            "coherence": "check survivor positivity and simulate the naive cap replacement",
            "closure": "certify the second hit as a three-edge collapse obstruction",
            "emit": "emit short hit2 artifacts, hashes, verifier command, and next target",
        },
        "inputs": {
            "repl_report": pair.parent.input_entry(
                REPL_REPORT,
                {
                    "status": rows["repl_report"].get("status"),
                    "certificate_sha256": rows["repl_report"].get("certificate_sha256"),
                },
            ),
            "xfer_report": pair.parent.input_entry(
                XFER_REPORT,
                {
                    "status": rows["xfer_report"].get("status"),
                    "certificate_sha256": rows["xfer_report"].get("certificate_sha256"),
                },
            ),
            "repl_faces": pair.parent.input_entry(REPL_FACES),
            "repl_verts": pair.parent.input_entry(REPL_VERTS),
            "repl_supp": pair.parent.input_entry(REPL_SUPP),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "hit2": pair.parent.relpath(OUT_DIR / "hit2.json"),
            "hits_csv": pair.parent.relpath(OUT_DIR / "hits.csv"),
            "collapse_csv": pair.parent.relpath(OUT_DIR / "collapse.csv"),
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
                "the exact second support-discriminant hit on eta6_repl",
                "positive survivor cone after deleting only the three hit support rows",
                "failure of the previous simple cap rule by neighboring-face collapse",
            ],
            "does_not_certify_because_not_required": [
                "a valid replacement complex for the second hit",
                "eta6 transfer through the unresolved three-edge collapse",
                "global automaton closure after repeated surgeries",
            ],
        },
        "next_highest_yield_item": (
            "Build a multi-face patch for the three-edge collapse at original "
            "vertices 41,52,55, then test support positivity and eta6 transfer."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.hit2.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.hit2.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "hit2": hit2,
        "hits_csv": csv_text(HIT_COLUMNS, hit["hit_rows"]),
        "collapse_csv": csv_text(COLLAPSE_COLUMNS, hit["collapse_rows"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, hit["obs_rows"]),
        "hit_table": hit_table,
        "collapse_table": collapse_table,
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
    pair.parent.write_json(OUT_DIR / "hit2.json", payloads["hit2"])
    (OUT_DIR / "hits.csv").write_text(payloads["hits_csv"], encoding="utf-8")
    (OUT_DIR / "collapse.csv").write_text(payloads["collapse_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        hit_table=payloads["hit_table"],
        collapse_table=payloads["collapse_table"],
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
