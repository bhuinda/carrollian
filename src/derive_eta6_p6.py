from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
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
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p6"
STATUS = "ETA6_P6_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p6.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p6.py"

PAIR_COLUMNS = [
    "pair_id",
    "p5_a",
    "p5_b",
    "f4_a",
    "f4_b",
    "face_a",
    "face_b",
    "mask_a",
    "mask_b",
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
    "below_single_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
    "eta6_preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p5_extension_count": 0,
    "pair_count": 1,
    "single_floor": 2,
    "pair_min_spread": 3,
    "pair_min_below_single_flag": 4,
    "below_single_pair_count": 5,
    "support_equal_pair_count": 6,
    "best_pair_id": 7,
    "best_pair_p5_a": 8,
    "best_pair_p5_b": 9,
    "best_pair_face_a": 10,
    "best_pair_face_b": 11,
    "best_same_face_spread": 12,
    "best_same_face_pair_id": 13,
    "best_same_mask_spread": 14,
    "best_same_mask_pair_id": 15,
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


def support(row: dict[str, int]) -> list[int]:
    return [row[f"p{index}_support"] for index in range(5)]


def build_p6_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    single_floor = min(row["support_spread"] for row in ext_rows)
    pair_rows = []
    pair_id = 0
    for left, right in itertools.combinations(ext_rows, 2):
        joint = [
            support(left)[index] + support(right)[index]
            for index in range(5)
        ]
        spread = max(joint) - min(joint)
        pair_rows.append(
            {
                "pair_id": pair_id,
                "p5_a": left["p5_id"],
                "p5_b": right["p5_id"],
                "f4_a": left["f4_row_id"],
                "f4_b": right["f4_row_id"],
                "face_a": left["face_id"],
                "face_b": right["face_id"],
                "mask_a": left["label_mask"],
                "mask_b": right["label_mask"],
                "same_face_flag": int(left["face_id"] == right["face_id"]),
                "same_mask_flag": int(left["label_mask"] == right["label_mask"]),
                "joint_p0_support": joint[0],
                "joint_p1_support": joint[1],
                "joint_p2_support": joint[2],
                "joint_p3_support": joint[3],
                "joint_p4_support": joint[4],
                "joint_support_min": min(joint),
                "joint_support_max": max(joint),
                "joint_support_spread": spread,
                "below_single_floor_flag": int(spread < single_floor),
                "support_equal_flag": int(spread == 0),
                "joint_mult_value": left["mult_value"] + right["mult_value"],
                "eta6_preserved_flag": int(
                    left["eta6_preserved_flag"] == 1
                    and right["eta6_preserved_flag"] == 1
                ),
            }
        )
        pair_id += 1

    best_pair = min(pair_rows, key=lambda row: (row["joint_support_spread"], row["pair_id"]))
    same_face_rows = [row for row in pair_rows if row["same_face_flag"] == 1]
    same_mask_rows = [row for row in pair_rows if row["same_mask_flag"] == 1]
    best_same_face = min(
        same_face_rows,
        key=lambda row: (row["joint_support_spread"], row["pair_id"]),
    )
    best_same_mask = min(
        same_mask_rows,
        key=lambda row: (row["joint_support_spread"], row["pair_id"]),
    )
    obs = {
        "p5_extension_count": len(ext_rows),
        "pair_count": len(pair_rows),
        "single_floor": single_floor,
        "pair_min_spread": best_pair["joint_support_spread"],
        "pair_min_below_single_flag": int(best_pair["joint_support_spread"] < single_floor),
        "below_single_pair_count": sum(
            row["below_single_floor_flag"] for row in pair_rows
        ),
        "support_equal_pair_count": sum(row["support_equal_flag"] for row in pair_rows),
        "best_pair_id": best_pair["pair_id"],
        "best_pair_p5_a": best_pair["p5_a"],
        "best_pair_p5_b": best_pair["p5_b"],
        "best_pair_face_a": best_pair["face_a"],
        "best_pair_face_b": best_pair["face_b"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_pair_id": best_same_face["pair_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_pair_id": best_same_mask["pair_id"],
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
    best_rows = sorted(
        pair_rows,
        key=lambda row: (row["joint_support_spread"], row["pair_id"]),
    )[:16]
    return {
        "pair_rows": pair_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "best_rows": best_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p6_rows()
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    checks = {
        "p5_certificate_available": p5_report.get("all_checks_pass") is True,
        "pair_screen_size_matches_144_choose_2": (
            obs["p5_extension_count"],
            obs["pair_count"],
        )
        == (144, 10_296),
        "two_step_compound_beats_single_floor": (
            obs["single_floor"],
            obs["pair_min_spread"],
            obs["pair_min_below_single_flag"],
            obs["below_single_pair_count"],
        )
        == (11_213_312, 10_515_968, 1, 4),
        "no_two_step_support_equalizer_found": obs["support_equal_pair_count"] == 0,
        "best_pair_matches_expected": (
            obs["best_pair_id"],
            obs["best_pair_p5_a"],
            obs["best_pair_p5_b"],
            obs["best_pair_face_a"],
            obs["best_pair_face_b"],
        )
        == (410, 2, 128, 12, 26),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_pair_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_pair_id"],
        )
        == (10_533_376, 1_936, 10_533_376, 1_936),
        "table_shapes_match_codebooks": (
            tuple(pair_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (10_296, len(PAIR_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "two_move_support_spread_descent",
        "single_floor": obs["single_floor"],
        "pair_min_spread": obs["pair_min_spread"],
        "below_single_pair_count": obs["below_single_pair_count"],
        "support_equal_pair_count": obs["support_equal_pair_count"],
        "best_pairs": [
            {
                "pair_id": row["pair_id"],
                "p5_ids": [row["p5_a"], row["p5_b"]],
                "faces": [row["face_a"], row["face_b"]],
                "masks": [row["mask_a"], row["mask_b"]],
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
            for row in rows["best_rows"]
        ],
        "reading": (
            "Pairing p5 support vectors can lower the raw support spread below "
            "the best single pentagon extension, but no two-move compound "
            "equalizes raw support across the five parenthesizations."
        ),
        "pair_table_sha256": sha_array(pair_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p6 = {
        "schema": "eta6.p6@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p5 support vectors",
            "test": "two-move eta6-preserving compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p6.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P6_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A two-move eta6-preserving compound of p5 support vectors lowers "
            "the raw support spread below the best single p5 extension, from "
            "11213312 to 10515968, but no two-move compound equalizes support."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p5 complement-sector pentagon support vectors",
            "witness": "enumerate all unordered two-move compounds",
            "coherence": "compare joint five-parenthesization support spread against the p5 single-move floor",
            "closure": "certify two-move support-spread descent without support equalization",
            "emit": "emit compact p6 artifacts and the next compound search",
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p6": relpath(OUT_DIR / "p6.json"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
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
                "complete two-move screen over all 10296 unordered p5 pairs",
                "4 two-move compounds have lower support spread than the best single p5 extension",
                "best two-move support spread is 10515968",
                "no two-move compound equalizes raw support across the five parenthesizations",
            ],
            "does_not_certify_because_false_or_open": [
                "a raw-support equalizer at two moves",
                "optimality over three or more p5 moves",
                "point-level geometric surgery on the p2 carrier",
                "global closure under repeated non-cubic surgeries",
            ],
        },
        "next_highest_yield_item": (
            "Run the three-move compound screen and check whether support spread "
            "continues descending or hits a positive floor."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p6.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p6.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p6": p6,
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "pair_table": pair_table,
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
    write_json(OUT_DIR / "p6.json", payloads["p6"])
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        pair_table=payloads["pair_table"],
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
