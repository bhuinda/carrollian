from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p25 as p25
    from . import derive_eta6_p26 as p26
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
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p27"
STATUS = "ETA6_P27_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p25.OUT_DIR / "report.json"
P25_TABLES = p25.OUT_DIR / "tables.npz"
P26_REPORT = p26.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p27.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p27.py"

PAIR_COLUMNS = [
    "pair_id",
    "p25_a",
    "p25_b",
    "p24_a",
    "p24_b",
    "lift_a",
    "lift_b",
    "face_a",
    "face_b",
    "mask_a",
    "mask_b",
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
    "below_p25_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
    "eta6_preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p25_extension_count": 0,
    "pair_count": 1,
    "p25_single_floor": 2,
    "pair_min_spread": 3,
    "pair_min_below_single_flag": 4,
    "below_single_pair_count": 5,
    "support_equal_pair_count": 6,
    "best_pair_id": 7,
    "best_pair_p25_a": 8,
    "best_pair_p25_b": 9,
    "best_pair_face_a": 10,
    "best_pair_face_b": 11,
    "best_same_face_spread": 12,
    "best_same_face_pair_id": 13,
    "best_same_mask_spread": 14,
    "best_same_mask_pair_id": 15,
    "p26_horizon_component_count": 16,
    "p26_checked_positive_row_total": 17,
    "p26_min_component_margin": 18,
    "compound_horizon_margin": 19,
    "compound_horizon_strict_flag": 20,
    "p26_margin_preserved_flag": 21,
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


def build_p27_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    single_floor = min(row["support_spread"] for row in ext_rows)
    pair_rows: list[dict[str, int]] = []
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
                "p25_a": left["p25_id"],
                "p25_b": right["p25_id"],
                "p24_a": left["p24_row_id"],
                "p24_b": right["p24_row_id"],
                "lift_a": left["lift_id"],
                "lift_b": right["lift_id"],
                "face_a": left["face_id"],
                "face_b": right["face_id"],
                "mask_a": left["label_mask"],
                "mask_b": right["label_mask"],
                "same_lift_flag": int(left["lift_id"] == right["lift_id"]),
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
                "below_p25_floor_flag": int(spread < single_floor),
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
    p26_report = load_json(P26_REPORT)
    p26_boundary = p26_report["witness"]["claim_boundary"]
    p26_min_margin = min(
        component["margin"] for component in p26_report["witness"]["components"]
    )
    obs = {
        "p25_extension_count": len(ext_rows),
        "pair_count": len(pair_rows),
        "p25_single_floor": single_floor,
        "pair_min_spread": best_pair["joint_support_spread"],
        "pair_min_below_single_flag": int(
            best_pair["joint_support_spread"] < single_floor
        ),
        "below_single_pair_count": sum(
            row["below_p25_floor_flag"] for row in pair_rows
        ),
        "support_equal_pair_count": sum(row["support_equal_flag"] for row in pair_rows),
        "best_pair_id": best_pair["pair_id"],
        "best_pair_p25_a": best_pair["p25_a"],
        "best_pair_p25_b": best_pair["p25_b"],
        "best_pair_face_a": best_pair["face_a"],
        "best_pair_face_b": best_pair["face_b"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_pair_id": best_same_face["pair_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_pair_id": best_same_mask["pair_id"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best_pair["joint_support_spread"]),
        "compound_horizon_strict_flag": int(
            p26_min_margin > 0
            and best_pair["joint_support_spread"] > 0
            and sum(row["support_equal_flag"] for row in pair_rows) == 0
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
    best_rows = sorted(
        pair_rows,
        key=lambda row: (row["joint_support_spread"], row["pair_id"]),
    )[:16]
    return {
        "pair_rows": pair_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "best_rows": best_rows,
        "p26_report": p26_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p27_rows()
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p25_report = load_json(P25_REPORT)
    p26_report = rows["p26_report"]
    checks = {
        "input_certificates_available": (
            p25_report.get("all_checks_pass") is True
            and p26_report.get("all_checks_pass") is True
        ),
        "pair_screen_size_matches_144_choose_2": (
            obs["p25_extension_count"],
            obs["pair_count"],
        )
        == (144, 10_296),
        "two_step_compound_beats_p25_floor": (
            obs["p25_single_floor"],
            obs["pair_min_spread"],
            obs["pair_min_below_single_flag"],
            obs["below_single_pair_count"],
        )
        == (11_213_312, 10_515_968, 1, 4),
        "no_two_step_support_equalizer_found": obs["support_equal_pair_count"] == 0,
        "best_pair_matches_expected": (
            obs["best_pair_id"],
            obs["best_pair_p25_a"],
            obs["best_pair_p25_b"],
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
            tuple(pair_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (10_296, len(PAIR_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "lifted_two_move_support_spread_descent",
        "p25_single_floor": obs["p25_single_floor"],
        "pair_min_spread": obs["pair_min_spread"],
        "below_single_pair_count": obs["below_single_pair_count"],
        "support_equal_pair_count": obs["support_equal_pair_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "best_pairs": [
            {
                "pair_id": row["pair_id"],
                "p25_ids": [row["p25_a"], row["p25_b"]],
                "p24_rows": [row["p24_a"], row["p24_b"]],
                "lifts": [row["lift_a"], row["lift_b"]],
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
        "horizon_reading": (
            "Two lifted p25 moves can lower the pentagon support-spread floor "
            "from 11213312 to 10515968, but every checked pair remains "
            "strictly positive and none equalizes raw support."
        ),
        "claim_boundary": {
            "complete_pair_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_pair_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "pair_table_sha256": sha_array(pair_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p27 = {
        "schema": "eta6.p27@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p25 lifted pentagon support vectors",
            "test": "complete two-move lifted compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p27.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P27_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A complete two-move screen over the 144 eta6_p25 lifted pentagon "
            "extensions lowers the support-spread floor from 11213312 to "
            "10515968. Exactly four pairs beat the p25 single-extension floor, "
            "and no pair equalizes raw support. The p26 finite-horizon margins "
            "remain strict on the checked packet."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p25 lifted pentagon support vectors and eta6_p26 margins",
            "witness": "enumerate all unordered two-move lifted compounds",
            "coherence": "compare joint support spread against p25 and preserve p26 positive margins",
            "closure": "certify two-move lifted spread descent without raw-support equalization",
            "emit": "emit compact p27 artifacts and the next compound-depth seam",
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p27": relpath(OUT_DIR / "p27.json"),
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
                "complete two-move screen over all 10296 unordered p25 pairs",
                "4 two-move compounds lower the p25 support-spread floor",
                "best lifted two-move support spread is 10515968",
                "no two-move compound equalizes raw support",
                "p26 finite-horizon margins remain positive on the checked packet",
            ],
            "does_not_certify_because_false_or_open": [
                "a raw-support equalizer at two moves",
                "optimality over three or more p25 moves",
                "new simple-object semantics for the lifted carrier",
                "that eta6 is uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "Start p28 by running the three-move lifted compound screen over "
            "p25 support vectors and checking whether the p27 floor continues "
            "to descend while remaining positive."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p27.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p27.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p27": p27,
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
    write_json(OUT_DIR / "p27.json", payloads["p27"])
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
