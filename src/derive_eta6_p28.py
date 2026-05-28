from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p25 as p25
    from . import derive_eta6_p26 as p26
    from . import derive_eta6_p27 as p27
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p25 as p25
    import derive_eta6_p26 as p26
    import derive_eta6_p27 as p27
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p28"
STATUS = "ETA6_P28_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p25.OUT_DIR / "report.json"
P25_TABLES = p25.OUT_DIR / "tables.npz"
P26_REPORT = p26.OUT_DIR / "report.json"
P27_REPORT = p27.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p28.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p28.py"

TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p28_id",
    "p25_a",
    "p25_b",
    "p25_c",
    "p24_a",
    "p24_b",
    "p24_c",
    "lift_a",
    "lift_b",
    "lift_c",
    "face_a",
    "face_b",
    "face_c",
    "mask_a",
    "mask_b",
    "mask_c",
    "same_lift_flag",
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
    "below_p27_floor_flag",
    "below_p25_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p25_extension_count": 0,
    "triple_count": 1,
    "p25_single_floor": 2,
    "p27_pair_floor": 3,
    "triple_min_spread": 4,
    "triple_min_below_p27_flag": 5,
    "below_p27_triple_count": 6,
    "below_p25_triple_count": 7,
    "support_equal_triple_count": 8,
    "best_p28_id": 9,
    "best_p25_a": 10,
    "best_p25_b": 11,
    "best_p25_c": 12,
    "best_face_a": 13,
    "best_face_b": 14,
    "best_face_c": 15,
    "best_same_face_spread": 16,
    "best_same_face_p28_id": 17,
    "best_same_mask_spread": 18,
    "best_same_mask_p28_id": 19,
    "p26_horizon_component_count": 20,
    "p26_checked_positive_row_total": 21,
    "p26_min_component_margin": 22,
    "compound_horizon_margin": 23,
    "compound_horizon_strict_flag": 24,
    "p26_margin_preserved_flag": 25,
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


def ranked_row(
    *,
    rank: int,
    p28_id: int,
    left: dict[str, int],
    mid: dict[str, int],
    right: dict[str, int],
    joint: list[int],
    p25_floor: int,
    p27_floor: int,
) -> dict[str, int]:
    spread = max(joint) - min(joint)
    return {
        "rank": rank,
        "p28_id": p28_id,
        "p25_a": left["p25_id"],
        "p25_b": mid["p25_id"],
        "p25_c": right["p25_id"],
        "p24_a": left["p24_row_id"],
        "p24_b": mid["p24_row_id"],
        "p24_c": right["p24_row_id"],
        "lift_a": left["lift_id"],
        "lift_b": mid["lift_id"],
        "lift_c": right["lift_id"],
        "face_a": left["face_id"],
        "face_b": mid["face_id"],
        "face_c": right["face_id"],
        "mask_a": left["label_mask"],
        "mask_b": mid["label_mask"],
        "mask_c": right["label_mask"],
        "same_lift_flag": int(
            left["lift_id"] == mid["lift_id"] == right["lift_id"]
        ),
        "same_face_flag": int(
            left["face_id"] == mid["face_id"] == right["face_id"]
        ),
        "same_mask_flag": int(
            left["label_mask"] == mid["label_mask"] == right["label_mask"]
        ),
        "joint_p0_support": joint[0],
        "joint_p1_support": joint[1],
        "joint_p2_support": joint[2],
        "joint_p3_support": joint[3],
        "joint_p4_support": joint[4],
        "joint_support_min": min(joint),
        "joint_support_max": max(joint),
        "joint_support_spread": spread,
        "below_p27_floor_flag": int(spread < p27_floor),
        "below_p25_floor_flag": int(spread < p25_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": (
            left["mult_value"] + mid["mult_value"] + right["mult_value"]
        ),
    }


def build_p28_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    p25_floor = min(row["support_spread"] for row in ext_rows)
    p27_report = load_json(P27_REPORT)
    p27_floor = int(p27_report["witness"]["pair_min_spread"])

    best_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    below_p27 = 0
    below_p25 = 0
    equal = 0
    p28_id = 0

    for i in range(len(ext_rows) - 2):
        left = ext_rows[i]
        left_support = support(left)
        for j in range(i + 1, len(ext_rows) - 1):
            mid = ext_rows[j]
            mid_support = support(mid)
            base = [
                left_support[index] + mid_support[index]
                for index in range(5)
            ]
            for k in range(j + 1, len(ext_rows)):
                right = ext_rows[k]
                right_support = support(right)
                joint = [
                    base[index] + right_support[index]
                    for index in range(5)
                ]
                row = ranked_row(
                    rank=0,
                    p28_id=p28_id,
                    left=left,
                    mid=mid,
                    right=right,
                    joint=joint,
                    p25_floor=p25_floor,
                    p27_floor=p27_floor,
                )
                spread = row["joint_support_spread"]
                if spread < p27_floor:
                    below_p27 += 1
                if spread < p25_floor:
                    below_p25 += 1
                if spread == 0:
                    equal += 1
                key = (spread, p28_id)
                if best_any is None or key < (
                    best_any["joint_support_spread"],
                    best_any["p28_id"],
                ):
                    best_any = row
                if row["same_face_flag"] == 1 and (
                    best_same_face is None
                    or key
                    < (
                        best_same_face["joint_support_spread"],
                        best_same_face["p28_id"],
                    )
                ):
                    best_same_face = row
                if row["same_mask_flag"] == 1 and (
                    best_same_mask is None
                    or key
                    < (
                        best_same_mask["joint_support_spread"],
                        best_same_mask["p28_id"],
                    )
                ):
                    best_same_mask = row
                best_rows.append(row)
                best_rows.sort(
                    key=lambda value: (
                        value["joint_support_spread"],
                        value["p28_id"],
                    )
                )
                if len(best_rows) > TOP_N:
                    best_rows.pop()
                p28_id += 1

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p28 search")
    top_rows = []
    for rank, row in enumerate(best_rows):
        top_row = dict(row)
        top_row["rank"] = rank
        top_rows.append(top_row)

    p26_report = load_json(P26_REPORT)
    p26_boundary = p26_report["witness"]["claim_boundary"]
    p26_min_margin = min(
        component["margin"] for component in p26_report["witness"]["components"]
    )
    obs = {
        "p25_extension_count": len(ext_rows),
        "triple_count": p28_id,
        "p25_single_floor": p25_floor,
        "p27_pair_floor": p27_floor,
        "triple_min_spread": best_any["joint_support_spread"],
        "triple_min_below_p27_flag": int(best_any["joint_support_spread"] < p27_floor),
        "below_p27_triple_count": below_p27,
        "below_p25_triple_count": below_p25,
        "support_equal_triple_count": equal,
        "best_p28_id": best_any["p28_id"],
        "best_p25_a": best_any["p25_a"],
        "best_p25_b": best_any["p25_b"],
        "best_p25_c": best_any["p25_c"],
        "best_face_a": best_any["face_a"],
        "best_face_b": best_any["face_b"],
        "best_face_c": best_any["face_c"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p28_id": best_same_face["p28_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p28_id": best_same_mask["p28_id"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best_any["joint_support_spread"]),
        "compound_horizon_strict_flag": int(
            p26_min_margin > 0
            and best_any["joint_support_spread"] > 0
            and equal == 0
        ),
        "p26_margin_preserved_flag": int(
            p26_boundary["support_equalizer_absent"] == 1
            and p26_boundary["universal_completion_claim"] == 0
        ),
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
        "top_rows": top_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "p26_report": p26_report,
        "p27_report": p27_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p28_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p25_report = load_json(P25_REPORT)
    p26_report = rows["p26_report"]
    p27_report = rows["p27_report"]
    checks = {
        "input_certificates_available": (
            p25_report.get("all_checks_pass") is True
            and p26_report.get("all_checks_pass") is True
            and p27_report.get("all_checks_pass") is True
        ),
        "triple_screen_size_matches_144_choose_3": (
            obs["p25_extension_count"],
            obs["triple_count"],
        )
        == (144, 487_344),
        "three_step_compound_beats_p27_floor": (
            obs["p25_single_floor"],
            obs["p27_pair_floor"],
            obs["triple_min_spread"],
            obs["triple_min_below_p27_flag"],
        )
        == (11_213_312, 10_515_968, 2_601_984, 1),
        "descent_counts_match": (
            obs["below_p27_triple_count"],
            obs["below_p25_triple_count"],
            obs["support_equal_triple_count"],
        )
        == (24, 34, 0),
        "best_triple_matches_expected": (
            obs["best_p28_id"],
            obs["best_p25_a"],
            obs["best_p25_b"],
            obs["best_p25_c"],
            obs["best_face_a"],
            obs["best_face_b"],
            obs["best_face_c"],
        )
        == (130_707, 14, 24, 32, 12, 12, 12),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p28_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p28_id"],
        )
        == (2_601_984, 130_707, 2_601_984, 130_707),
        "p26_horizon_margins_remain_strict": (
            obs["p26_horizon_component_count"],
            obs["p26_checked_positive_row_total"],
            obs["p26_min_component_margin"],
            obs["compound_horizon_margin"],
            obs["compound_horizon_strict_flag"],
            obs["p26_margin_preserved_flag"],
        )
        == (4, 7_735_158, 1, 1, 1, 1),
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
        "classification": "lifted_three_move_support_spread_descent",
        "p25_single_floor": obs["p25_single_floor"],
        "p27_pair_floor": obs["p27_pair_floor"],
        "triple_min_spread": obs["triple_min_spread"],
        "below_p27_triple_count": obs["below_p27_triple_count"],
        "below_p25_triple_count": obs["below_p25_triple_count"],
        "support_equal_triple_count": obs["support_equal_triple_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "best_triples": [
            {
                "rank": row["rank"],
                "p28_id": row["p28_id"],
                "p25_ids": [row["p25_a"], row["p25_b"], row["p25_c"]],
                "p24_rows": [row["p24_a"], row["p24_b"], row["p24_c"]],
                "lifts": [row["lift_a"], row["lift_b"], row["lift_c"]],
                "faces": [row["face_a"], row["face_b"], row["face_c"]],
                "masks": [row["mask_a"], row["mask_b"], row["mask_c"]],
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
        "horizon_reading": (
            "Three lifted p25 moves sharply lower the pentagon support-spread "
            "floor from 10515968 to 2601984, but every checked triple remains "
            "strictly positive and none equalizes raw support."
        ),
        "claim_boundary": {
            "complete_triple_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_triple_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p28 = {
        "schema": "eta6.p28@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p25 support vectors plus eta6_p27 floor",
            "test": "complete three-move lifted compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p28.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P28_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A complete three-move screen over the 144 eta6_p25 lifted pentagon "
            "extensions lowers the support-spread floor from the p27 two-move "
            "floor 10515968 to 2601984. Twenty-four triples beat the p27 floor, "
            "and no triple equalizes raw support. The p26 finite-horizon "
            "margins remain strict on the checked packet."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p25 vectors, eta6_p27 pair floor, and eta6_p26 margins",
            "witness": "enumerate all unordered three-move lifted compounds while retaining compact top rows",
            "coherence": "compare joint support spread against p25 and p27 and preserve p26 positive margins",
            "closure": "certify three-move lifted spread descent without raw-support equalization",
            "emit": "emit compact p28 artifacts and the next compound-depth seam",
        },
        "inputs": {
            "p25_report": input_entry(
                P25_REPORT,
                {
                    "status": p25_report.get("status"),
                    "certificate_sha256": p25_report.get("certificate_sha256"),
                },
            ),
            "p25_tables": input_entry(P25_TABLES),
            "p26_report": input_entry(
                P26_REPORT,
                {
                    "status": p26_report.get("status"),
                    "certificate_sha256": p26_report.get("certificate_sha256"),
                },
            ),
            "p27_report": input_entry(
                P27_REPORT,
                {
                    "status": p27_report.get("status"),
                    "certificate_sha256": p27_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p28": relpath(OUT_DIR / "p28.json"),
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
                "complete three-move screen over all 487344 unordered p25 triples",
                "24 three-move compounds lower the p27 two-move floor",
                "best lifted three-move support spread is 2601984",
                "no three-move compound equalizes raw support",
                "p26 finite-horizon margins remain positive on the checked packet",
            ],
            "does_not_certify_because_false_or_open": [
                "a raw-support equalizer at three moves",
                "optimality over four or more p25 moves",
                "new simple-object semantics for the lifted carrier",
                "that eta6 is uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "Start p29 by running the four-move lifted compound screen using "
            "meet-in-the-middle sums to test whether the p28 floor persists."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p28.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p28.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p28": p28,
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
    write_json(OUT_DIR / "p28.json", payloads["p28"])
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
