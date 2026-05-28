from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p6 as p6
    from . import derive_eta6_p7 as p7
    from . import derive_eta6_p8 as p8
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p5 as p5
    import derive_eta6_p6 as p6
    import derive_eta6_p7 as p7
    import derive_eta6_p8 as p8
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p9"
STATUS = "ETA6_P9_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P6_REPORT = p6.OUT_DIR / "report.json"
P7_REPORT = p7.OUT_DIR / "report.json"
P7_TABLES = p7.OUT_DIR / "tables.npz"
P8_REPORT = p8.OUT_DIR / "report.json"
P8_TABLES = p8.OUT_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p9.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p9.py"

TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p9_id",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
    "face_a",
    "face_b",
    "face_c",
    "face_d",
    "face_e",
    "mask_a",
    "mask_b",
    "mask_c",
    "mask_d",
    "mask_e",
    "same_face_flag",
    "same_mask_flag",
    "joint_p0_support",
    "joint_p1_support",
    "joint_p2_support",
    "joint_p3_support",
    "joint_p4_support",
    "joint_support_min",
    "joint_support_max",
    "joint_support_spread",
    "below_p8_floor_flag",
    "below_p7_floor_flag",
    "below_p6_floor_flag",
    "below_p5_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p5_extension_count": 0,
    "p7_top_count": 1,
    "p8_top_count": 2,
    "candidate_count": 3,
    "p5_single_floor": 4,
    "p6_pair_floor": 5,
    "p7_triple_floor": 6,
    "p8_quad_floor": 7,
    "bounded_min_spread": 8,
    "bounded_min_below_p8_flag": 9,
    "below_p8_candidate_count": 10,
    "below_p7_candidate_count": 11,
    "below_p6_candidate_count": 12,
    "below_p5_candidate_count": 13,
    "support_equal_candidate_count": 14,
    "best_p9_id": 15,
    "best_p5_a": 16,
    "best_p5_b": 17,
    "best_p5_c": 18,
    "best_p5_d": 19,
    "best_p5_e": 20,
    "best_face_a": 21,
    "best_face_b": 22,
    "best_face_c": 23,
    "best_face_d": 24,
    "best_face_e": 25,
    "best_same_face_spread": 26,
    "best_same_face_p9_id": 27,
    "best_same_mask_spread": 28,
    "best_same_mask_p9_id": 29,
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


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def frontier_candidates(
    ext_rows: list[dict[str, int]],
    p7_top_rows: list[dict[str, int]],
    p8_top_rows: list[dict[str, int]],
) -> list[tuple[int, int, int, int, int]]:
    ids = [row["p5_id"] for row in ext_rows]
    candidates: set[tuple[int, int, int, int, int]] = set()
    for row in p8_top_rows:
        quad = [row["p5_a"], row["p5_b"], row["p5_c"], row["p5_d"]]
        used = set(quad)
        for extension_id in ids:
            if extension_id not in used:
                candidates.add(tuple(sorted([*quad, extension_id])))
    for row in p7_top_rows:
        triple = [row["p5_a"], row["p5_b"], row["p5_c"]]
        used = set(triple)
        rest = [extension_id for extension_id in ids if extension_id not in used]
        for left, right in itertools.combinations(rest, 2):
            candidates.add(tuple(sorted([*triple, left, right])))
    return sorted(candidates)


def ranked_row(
    *,
    rank: int,
    p9_id: int,
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p9_id": p9_id,
        "p5_a": rows[0]["p5_id"],
        "p5_b": rows[1]["p5_id"],
        "p5_c": rows[2]["p5_id"],
        "p5_d": rows[3]["p5_id"],
        "p5_e": rows[4]["p5_id"],
        "face_a": faces[0],
        "face_b": faces[1],
        "face_c": faces[2],
        "face_d": faces[3],
        "face_e": faces[4],
        "mask_a": masks[0],
        "mask_b": masks[1],
        "mask_c": masks[2],
        "mask_d": masks[3],
        "mask_e": masks[4],
        "same_face_flag": int(len(set(faces)) == 1),
        "same_mask_flag": int(len(set(masks)) == 1),
        "joint_p0_support": int(joint[0]),
        "joint_p1_support": int(joint[1]),
        "joint_p2_support": int(joint[2]),
        "joint_p3_support": int(joint[3]),
        "joint_p4_support": int(joint[4]),
        "joint_support_min": int(joint.min()),
        "joint_support_max": int(joint.max()),
        "joint_support_spread": spread,
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p9_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    p7_tables = np.load(P7_TABLES, allow_pickle=False)
    p8_tables = np.load(P8_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    p7_top_rows = rows_from_table(
        np.asarray(p7_tables["top_table"], dtype=np.int64),
        p7.TOP_COLUMNS,
    )
    p8_top_rows = rows_from_table(
        np.asarray(p8_tables["top_table"], dtype=np.int64),
        p8.TOP_COLUMNS,
    )
    row_by_id = {row["p5_id"]: row for row in ext_rows}
    support_by_id = {
        row["p5_id"]: np.asarray(
            [row[f"p{index}_support"] for index in range(5)],
            dtype=np.int64,
        )
        for row in ext_rows
    }
    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(load_json(P8_REPORT)["witness"]["quad_min_spread"])
    candidates = frontier_candidates(ext_rows, p7_top_rows, p8_top_rows)

    best_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    below_p8 = 0
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0

    for p9_id, candidate in enumerate(candidates):
        rows = [row_by_id[p5_id] for p5_id in candidate]
        joint = sum((support_by_id[p5_id] for p5_id in candidate), np.zeros(5, dtype=np.int64))
        row = ranked_row(
            rank=0,
            p9_id=p9_id,
            rows=rows,
            joint=joint,
            p5_floor=p5_floor,
            p6_floor=p6_floor,
            p7_floor=p7_floor,
            p8_floor=p8_floor,
        )
        spread = row["joint_support_spread"]
        if spread < p8_floor:
            below_p8 += 1
        if spread < p7_floor:
            below_p7 += 1
        if spread < p6_floor:
            below_p6 += 1
        if spread < p5_floor:
            below_p5 += 1
        if spread == 0:
            equal += 1
        key = (spread, p9_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p9_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p9_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p9_id"],
            )
        ):
            best_same_mask = row
        best_rows.append(row)
        best_rows.sort(key=lambda value: (value["joint_support_spread"], value["p9_id"]))
        if len(best_rows) > 512:
            best_rows = best_rows[:64]

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p9 search")
    best_rows = sorted(
        best_rows,
        key=lambda value: (value["joint_support_spread"], value["p9_id"]),
    )[:TOP_N]
    for rank, row in enumerate(best_rows):
        row["rank"] = rank

    obs = {
        "p5_extension_count": len(ext_rows),
        "p7_top_count": len(p7_top_rows),
        "p8_top_count": len(p8_top_rows),
        "candidate_count": len(candidates),
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "bounded_min_spread": best_any["joint_support_spread"],
        "bounded_min_below_p8_flag": int(best_any["joint_support_spread"] < p8_floor),
        "below_p8_candidate_count": below_p8,
        "below_p7_candidate_count": below_p7,
        "below_p6_candidate_count": below_p6,
        "below_p5_candidate_count": below_p5,
        "support_equal_candidate_count": equal,
        "best_p9_id": best_any["p9_id"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_p5_e": best_any["p5_e"],
        "best_face_a": best_any["face_a"],
        "best_face_b": best_any["face_b"],
        "best_face_c": best_any["face_c"],
        "best_face_d": best_any["face_d"],
        "best_face_e": best_any["face_e"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p9_id": best_same_face["p9_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p9_id": best_same_mask["p9_id"],
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
        "top_rows": best_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p9_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p6_report = load_json(P6_REPORT)
    p7_report = load_json(P7_REPORT)
    p8_report = load_json(P8_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p6_report.get("all_checks_pass") is True
            and p7_report.get("all_checks_pass") is True
            and p8_report.get("all_checks_pass") is True
        ),
        "bounded_frontier_size_matches": (
            obs["p5_extension_count"],
            obs["p7_top_count"],
            obs["p8_top_count"],
            obs["candidate_count"],
        )
        == (144, 32, 32, 316_068),
        "bounded_five_move_stalls_above_p8_floor": (
            obs["p8_quad_floor"],
            obs["bounded_min_spread"],
            obs["bounded_min_below_p8_flag"],
            obs["below_p8_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (2_447_744, 5_601_664, 0, 0, 0),
        "descent_counts_match": (
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
        )
        == (0, 88, 128),
        "best_candidate_matches_expected": (
            obs["best_p9_id"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_face_a"],
            obs["best_face_b"],
            obs["best_face_c"],
            obs["best_face_d"],
            obs["best_face_e"],
        )
        == (10_321, 2, 8, 12, 30, 128, 12, 12, 12, 12, 26),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p9_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p9_id"],
        )
        == (5_959_680, 120_075, 5_959_680, 120_075),
        "table_shapes_match_codebooks": (
            tuple(top_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (TOP_N, len(TOP_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "bounded_five_move_frontier_stall",
        "candidate_construction": (
            "deduplicated union of one-step extensions of eta6_p8 top rows "
            "and two-step extensions of eta6_p7 top rows"
        ),
        "p8_quad_floor": obs["p8_quad_floor"],
        "bounded_min_spread": obs["bounded_min_spread"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p7_candidate_count": obs["below_p7_candidate_count"],
        "below_p6_candidate_count": obs["below_p6_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "best_candidates": [
            {
                "rank": row["rank"],
                "p9_id": row["p9_id"],
                "p5_ids": [
                    row["p5_a"],
                    row["p5_b"],
                    row["p5_c"],
                    row["p5_d"],
                    row["p5_e"],
                ],
                "faces": [
                    row["face_a"],
                    row["face_b"],
                    row["face_c"],
                    row["face_d"],
                    row["face_e"],
                ],
                "masks": [
                    row["mask_a"],
                    row["mask_b"],
                    row["mask_c"],
                    row["mask_d"],
                    row["mask_e"],
                ],
                "support": [
                    row["joint_p0_support"],
                    row["joint_p1_support"],
                    row["joint_p2_support"],
                    row["joint_p3_support"],
                    row["joint_p4_support"],
                ],
                "spread": row["joint_support_spread"],
                "same_face": row["same_face_flag"],
                "same_mask": row["same_mask_flag"],
            }
            for row in rows["top_rows"][:16]
        ],
        "reading": (
            "The bounded five-move frontier does not continue the p8 descent; "
            "it stays above the p8 floor and finds no support equalizer."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p9 = {
        "schema": "eta6.p9@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p7 and eta6_p8 top frontiers",
            "test": "bounded five-move eta6-preserving compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p9.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P9_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The bounded five-move frontier around eta6_p7/p8 top rows does not "
            "beat the p8 four-move floor: its best spread is 5601664, with no "
            "support equalizer."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p7 and eta6_p8 compact frontiers",
            "witness": "deduplicate one-step p8-top and two-step p7-top five-move candidates",
            "coherence": "compare bounded five-move spread against p8, p7, p6, and p5 floors",
            "closure": "certify a bounded local stall rather than a global five-move theorem",
            "emit": "emit compact p9 artifacts and the next global-search seam",
        },
        "inputs": {
            "p5_report": input_entry(
                P5_REPORT,
                {
                    "status": p5_report.get("status"),
                    "certificate_sha256": p5_report.get("certificate_sha256"),
                },
            ),
            "p5_tables": input_entry(P5_TABLES),
            "p6_report": input_entry(
                P6_REPORT,
                {
                    "status": p6_report.get("status"),
                    "certificate_sha256": p6_report.get("certificate_sha256"),
                },
            ),
            "p7_report": input_entry(
                P7_REPORT,
                {
                    "status": p7_report.get("status"),
                    "certificate_sha256": p7_report.get("certificate_sha256"),
                },
            ),
            "p7_tables": input_entry(P7_TABLES),
            "p8_report": input_entry(
                P8_REPORT,
                {
                    "status": p8_report.get("status"),
                    "certificate_sha256": p8_report.get("certificate_sha256"),
                },
            ),
            "p8_tables": input_entry(P8_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p9": relpath(OUT_DIR / "p9.json"),
            "top_csv": relpath(OUT_DIR / "top.csv"),
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
                "bounded five-move frontier over 316068 deduplicated candidates",
                "no bounded candidate beats the p8 four-move floor",
                "best bounded five-move spread is 5601664",
                "no bounded five-move candidate equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete five-move search over all p5 quintuple compounds",
                "a global five-move support-spread lower bound",
                "point-level geometric surgery on the p2 carrier",
                "global closure under repeated non-cubic surgeries",
            ],
        },
        "next_highest_yield_item": (
            "Use the p9 stall to prune a targeted full five-move search, starting "
            "from candidates whose four-subsets intersect the p8 best and top rows."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p9.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p9.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p9": p9,
        "top_csv": csv_text(TOP_COLUMNS, rows["top_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "top_table": top_table,
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
    write_json(OUT_DIR / "p9.json", payloads["p9"])
    (OUT_DIR / "top.csv").write_text(payloads["top_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        top_table=payloads["top_table"],
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
