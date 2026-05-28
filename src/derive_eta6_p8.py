from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p6 as p6
    from . import derive_eta6_p7 as p7
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
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p8"
STATUS = "ETA6_P8_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P6_REPORT = p6.OUT_DIR / "report.json"
P7_REPORT = p7.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p8.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p8.py"

TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p8_id",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "face_a",
    "face_b",
    "face_c",
    "face_d",
    "mask_a",
    "mask_b",
    "mask_c",
    "mask_d",
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
    "below_p7_floor_flag",
    "below_p6_floor_flag",
    "below_p5_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p5_extension_count": 0,
    "quad_count": 1,
    "p5_single_floor": 2,
    "p6_pair_floor": 3,
    "p7_triple_floor": 4,
    "quad_min_spread": 5,
    "quad_min_below_p7_flag": 6,
    "below_p7_quad_count": 7,
    "below_p6_quad_count": 8,
    "below_p5_quad_count": 9,
    "support_equal_quad_count": 10,
    "best_p8_id": 11,
    "best_p5_a": 12,
    "best_p5_b": 13,
    "best_p5_c": 14,
    "best_p5_d": 15,
    "best_face_a": 16,
    "best_face_b": 17,
    "best_face_c": 18,
    "best_face_d": 19,
    "best_same_face_spread": 20,
    "best_same_face_p8_id": 21,
    "best_same_mask_spread": 22,
    "best_same_mask_p8_id": 23,
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


def support(row: dict[str, int]) -> np.ndarray:
    return np.asarray([row[f"p{index}_support"] for index in range(5)], dtype=np.int64)


def ranked_row(
    *,
    rank: int,
    p8_id: int,
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p8_id": p8_id,
        "p5_a": rows[0]["p5_id"],
        "p5_b": rows[1]["p5_id"],
        "p5_c": rows[2]["p5_id"],
        "p5_d": rows[3]["p5_id"],
        "face_a": faces[0],
        "face_b": faces[1],
        "face_c": faces[2],
        "face_d": faces[3],
        "mask_a": masks[0],
        "mask_b": masks[1],
        "mask_c": masks[2],
        "mask_d": masks[3],
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
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p8_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    supports = np.asarray([support(row) for row in ext_rows], dtype=np.int64)
    faces = np.asarray([row["face_id"] for row in ext_rows], dtype=np.int64)
    masks = np.asarray([row["label_mask"] for row in ext_rows], dtype=np.int64)
    p5_floor = int((supports.max(axis=1) - supports.min(axis=1)).min())
    p6_floor = int(load_json(P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(P7_REPORT)["witness"]["triple_min_spread"])

    best_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0
    p8_id = 0

    for i in range(len(ext_rows) - 3):
        left = supports[i]
        for j in range(i + 1, len(ext_rows) - 2):
            left_mid = left + supports[j]
            for k in range(j + 1, len(ext_rows) - 1):
                base = left_mid + supports[k]
                tail = base + supports[k + 1 :]
                spreads = tail.max(axis=1) - tail.min(axis=1)
                below_p7 += int((spreads < p7_floor).sum())
                below_p6 += int((spreads < p6_floor).sum())
                below_p5 += int((spreads < p5_floor).sum())
                equal += int((spreads == 0).sum())

                candidates: list[int] = []
                min_pos = int(spreads.argmin())
                candidates.append(min_pos)
                if faces[i] == faces[j] == faces[k]:
                    mask = faces[k + 1 :] == faces[i]
                    if bool(mask.any()):
                        masked = np.where(mask, spreads, np.iinfo(np.int64).max)
                        candidates.append(int(masked.argmin()))
                if masks[i] == masks[j] == masks[k]:
                    mask = masks[k + 1 :] == masks[i]
                    if bool(mask.any()):
                        masked = np.where(mask, spreads, np.iinfo(np.int64).max)
                        candidates.append(int(masked.argmin()))

                take = min(40, len(spreads))
                candidates.extend(int(pos) for pos in np.argpartition(spreads, take - 1)[:take])
                for pos in sorted(set(candidates)):
                    p8_candidate = p8_id + pos
                    l = k + 1 + pos
                    row = ranked_row(
                        rank=0,
                        p8_id=p8_candidate,
                        rows=[ext_rows[i], ext_rows[j], ext_rows[k], ext_rows[l]],
                        joint=tail[pos],
                        p5_floor=p5_floor,
                        p6_floor=p6_floor,
                        p7_floor=p7_floor,
                    )
                    key = (row["joint_support_spread"], row["p8_id"])
                    if best_any is None or key < (
                        best_any["joint_support_spread"],
                        best_any["p8_id"],
                    ):
                        best_any = row
                    if row["same_face_flag"] == 1 and (
                        best_same_face is None
                        or key
                        < (
                            best_same_face["joint_support_spread"],
                            best_same_face["p8_id"],
                        )
                    ):
                        best_same_face = row
                    if row["same_mask_flag"] == 1 and (
                        best_same_mask is None
                        or key
                        < (
                            best_same_mask["joint_support_spread"],
                            best_same_mask["p8_id"],
                        )
                    ):
                        best_same_mask = row
                    best_rows.append(row)
                best_rows.sort(key=lambda value: (value["joint_support_spread"], value["p8_id"]))
                if len(best_rows) > 512:
                    best_rows = best_rows[:64]
                p8_id += len(spreads)

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p8 search")
    best_rows = sorted(
        best_rows,
        key=lambda value: (value["joint_support_spread"], value["p8_id"]),
    )[:TOP_N]
    for rank, row in enumerate(best_rows):
        row["rank"] = rank

    obs = {
        "p5_extension_count": len(ext_rows),
        "quad_count": p8_id,
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "quad_min_spread": best_any["joint_support_spread"],
        "quad_min_below_p7_flag": int(best_any["joint_support_spread"] < p7_floor),
        "below_p7_quad_count": below_p7,
        "below_p6_quad_count": below_p6,
        "below_p5_quad_count": below_p5,
        "support_equal_quad_count": equal,
        "best_p8_id": best_any["p8_id"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_face_a": best_any["face_a"],
        "best_face_b": best_any["face_b"],
        "best_face_c": best_any["face_c"],
        "best_face_d": best_any["face_d"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p8_id": best_same_face["p8_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p8_id": best_same_mask["p8_id"],
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
    rows = build_p8_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p6_report = load_json(P6_REPORT)
    p7_report = load_json(P7_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p6_report.get("all_checks_pass") is True
            and p7_report.get("all_checks_pass") is True
        ),
        "quad_screen_size_matches_144_choose_4": (
            obs["p5_extension_count"],
            obs["quad_count"],
        )
        == (144, 17_178_876),
        "four_step_compound_beats_triple_floor": (
            obs["p5_single_floor"],
            obs["p6_pair_floor"],
            obs["p7_triple_floor"],
            obs["quad_min_spread"],
            obs["quad_min_below_p7_flag"],
        )
        == (11_213_312, 10_515_968, 2_601_984, 2_447_744, 1),
        "descent_counts_match": (
            obs["below_p7_quad_count"],
            obs["below_p6_quad_count"],
            obs["below_p5_quad_count"],
            obs["support_equal_quad_count"],
        )
        == (1, 247, 311, 0),
        "best_quad_matches_expected": (
            obs["best_p8_id"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_face_a"],
            obs["best_face_b"],
            obs["best_face_c"],
            obs["best_face_d"],
        )
        == (10_063_403, 28, 36, 58, 66, 12, 12, 22, 22),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p8_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p8_id"],
        )
        == (2_643_328, 3_573_468, 2_643_328, 3_573_468),
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
        "classification": "four_move_support_spread_descent",
        "p5_single_floor": obs["p5_single_floor"],
        "p6_pair_floor": obs["p6_pair_floor"],
        "p7_triple_floor": obs["p7_triple_floor"],
        "quad_min_spread": obs["quad_min_spread"],
        "below_p7_quad_count": obs["below_p7_quad_count"],
        "below_p6_quad_count": obs["below_p6_quad_count"],
        "below_p5_quad_count": obs["below_p5_quad_count"],
        "support_equal_quad_count": obs["support_equal_quad_count"],
        "best_quads": [
            {
                "rank": row["rank"],
                "p8_id": row["p8_id"],
                "p5_ids": [row["p5_a"], row["p5_b"], row["p5_c"], row["p5_d"]],
                "faces": [row["face_a"], row["face_b"], row["face_c"], row["face_d"]],
                "masks": [row["mask_a"], row["mask_b"], row["mask_c"], row["mask_d"]],
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
            "Four-move p5 compounds still lower raw support spread, but the "
            "complete depth-four screen still has no support equalizer."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p8 = {
        "schema": "eta6.p8@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p5 support vectors plus eta6_p7 floor",
            "test": "four-move eta6-preserving compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p8.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P8_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A four-move eta6-preserving compound of p5 support vectors lowers "
            "the raw support spread from the p7 three-move floor 2601984 to "
            "2447744, but no four-move compound equalizes support."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p5 vectors and eta6_p7 triple floor",
            "witness": "enumerate all unordered four-move compounds while retaining compact top rows",
            "coherence": "compare joint support spread against the p5, p6, and p7 floors",
            "closure": "certify four-move support-spread descent without support equalization",
            "emit": "emit compact p8 artifacts and the next compound search",
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p8": relpath(OUT_DIR / "p8.json"),
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
                "complete four-move screen over all 17178876 unordered p5 quadruples",
                "1 four-move compound beats the p7 three-move floor",
                "best four-move support spread is 2447744",
                "no four-move compound equalizes raw support across the five parenthesizations",
            ],
            "does_not_certify_because_false_or_open": [
                "a raw-support equalizer at four moves",
                "optimality over five or more p5 moves",
                "point-level geometric surgery on the p2 carrier",
                "global closure under repeated non-cubic surgeries",
            ],
        },
        "next_highest_yield_item": (
            "Run a bounded five-move screen around the p8 best quadruple and "
            "the p7/p8 top frontier to test whether descent stalls."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p8.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p8.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p8": p8,
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
    write_json(OUT_DIR / "p8.json", payloads["p8"])
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
