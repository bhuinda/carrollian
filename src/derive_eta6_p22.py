from __future__ import annotations

import csv
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_f4 as f4
    from . import derive_eta6_gap as gap
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p21 as p21
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_f4 as f4
    import derive_eta6_gap as gap
    import derive_eta6_p5 as p5
    import derive_eta6_p21 as p21
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p22"
STATUS = "ETA6_P22_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_TABLES = p5.OUT_DIR / "tables.npz"
F4_REPORT = f4.OUT_DIR / "report.json"
F4_FACE = f4.OUT_DIR / "face.csv"
P21_REPORT = p21.OUT_DIR / "report.json"
GAP_REPORT = gap.OUT_DIR / "report.json"
HPOL_WEIGHTS = ROOT / "data" / "invariants" / "d20" / "proof_obligations" / "eta6_hpol" / "weights.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p22.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p22.py"

PAIR_IDS = ((1, 47), (57, 79), (110, 128))
PAIR_COLUMNS = [
    "pair_id",
    "face_id",
    "label_mask",
    "left_p5_id",
    "right_p5_id",
    "hpol_weight",
    "f4_delta_sum",
    "eta6_preserved_count",
    "mirror_order_flag",
    "p0_support",
    "p1_support",
    "p2_support",
    "p3_support",
    "p4_support",
    "pair_support_spread",
    "pair_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "fused_face_count": 0,
    "gate_pair_count": 1,
    "gate_move_count": 2,
    "eta6_preserved_count": 3,
    "total_f4_delta": 4,
    "per_face_abs_delta_sum": 5,
    "all_pair_delta_zero_flag": 6,
    "all_pair_mirror_flag": 7,
    "carrier_neutral_flag": 8,
    "hpol_weight_sum": 9,
    "p0_support": 10,
    "p1_support": 11,
    "p2_support": 12,
    "p3_support": 13,
    "p4_support": 14,
    "support_spread": 15,
    "p0_p1_equal_flag": 16,
    "p2_p3_equal_flag": 17,
    "p4_excess_over_min": 18,
    "joint_mult_value": 19,
    "global_floor": 20,
    "hpol_min_margin": 21,
    "repl_min_margin": 22,
    "checked_margin_positive_flag": 23,
    "symbolic_carrier_claim_flag": 24,
    "geometric_carrier_claim_flag": 25,
    "best_p5_a": 26,
    "best_p5_b": 27,
    "best_p5_c": 28,
    "best_p5_d": 29,
    "best_p5_e": 30,
    "best_p5_f": 31,
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


def read_weights() -> dict[int, int]:
    with HPOL_WEIGHTS.open("r", encoding="utf-8", newline="") as handle:
        return {int(row["face_id"]): int(row["weight"]) for row in csv.DictReader(handle)}


def read_csv_ints(path: Any) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def mirror_order(left: dict[str, int], right: dict[str, int]) -> bool:
    return (
        left["a"] == right["d"]
        and left["b"] == right["c"]
        and left["c"] == right["b"]
        and left["d"] == right["a"]
        and left["e"] == right["e"]
        and left["omitted_label"] == right["omitted_label"]
    )


def build_p22_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    p5_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    p5_by_id = {row["p5_id"]: row for row in p5_rows}
    weights = read_weights()
    pair_rows = []
    supports = np.zeros(5, dtype=np.int64)
    total_delta = 0
    per_face_abs_delta = 0
    eta6_count = 0
    joint_mult = 0
    for pair_id, (left_id, right_id) in enumerate(PAIR_IDS):
        left = p5_by_id[left_id]
        right = p5_by_id[right_id]
        pair_support = [
            left[f"p{index}_support"] + right[f"p{index}_support"]
            for index in range(5)
        ]
        for index, value in enumerate(pair_support):
            supports[index] += value
        delta = left["f4_delta"] + right["f4_delta"]
        total_delta += delta
        per_face_abs_delta += abs(delta)
        eta6_pair = left["eta6_preserved_flag"] + right["eta6_preserved_flag"]
        eta6_count += eta6_pair
        pair_mult = left["mult_value"] + right["mult_value"]
        joint_mult += pair_mult
        pair_rows.append(
            {
                "pair_id": pair_id,
                "face_id": left["face_id"],
                "label_mask": left["label_mask"],
                "left_p5_id": left_id,
                "right_p5_id": right_id,
                "hpol_weight": weights[left["face_id"]],
                "f4_delta_sum": delta,
                "eta6_preserved_count": eta6_pair,
                "mirror_order_flag": int(mirror_order(left, right)),
                "p0_support": pair_support[0],
                "p1_support": pair_support[1],
                "p2_support": pair_support[2],
                "p3_support": pair_support[3],
                "p4_support": pair_support[4],
                "pair_support_spread": max(pair_support) - min(pair_support),
                "pair_mult_value": pair_mult,
            }
        )

    p21_report = load_json(P21_REPORT)
    gap_report = load_json(GAP_REPORT)
    gate_ids = tuple(p21_report["witness"]["gate_p5_ids"])
    hpol_margin = int(gap_report["witness"]["hpol"]["min_margin"])
    repl_margin = int(gap_report["witness"]["repl"]["min_margin"])
    support_spread = int(supports.max() - supports.min())
    obs = {
        "fused_face_count": len(pair_rows),
        "gate_pair_count": len(pair_rows),
        "gate_move_count": len(gate_ids),
        "eta6_preserved_count": eta6_count,
        "total_f4_delta": total_delta,
        "per_face_abs_delta_sum": per_face_abs_delta,
        "all_pair_delta_zero_flag": int(all(row["f4_delta_sum"] == 0 for row in pair_rows)),
        "all_pair_mirror_flag": int(all(row["mirror_order_flag"] == 1 for row in pair_rows)),
        "carrier_neutral_flag": int(
            eta6_count == 6
            and total_delta == 0
            and per_face_abs_delta == 0
            and all(row["mirror_order_flag"] == 1 for row in pair_rows)
        ),
        "hpol_weight_sum": sum(2 * row["hpol_weight"] for row in pair_rows),
        "p0_support": int(supports[0]),
        "p1_support": int(supports[1]),
        "p2_support": int(supports[2]),
        "p3_support": int(supports[3]),
        "p4_support": int(supports[4]),
        "support_spread": support_spread,
        "p0_p1_equal_flag": int(supports[0] == supports[1]),
        "p2_p3_equal_flag": int(supports[2] == supports[3]),
        "p4_excess_over_min": int(supports[4] - supports.min()),
        "joint_mult_value": joint_mult,
        "global_floor": int(p21_report["witness"]["global_floor"]),
        "hpol_min_margin": hpol_margin,
        "repl_min_margin": repl_margin,
        "checked_margin_positive_flag": int(hpol_margin > 0 and repl_margin > 0),
        "symbolic_carrier_claim_flag": 1,
        "geometric_carrier_claim_flag": 0,
        "best_p5_a": gate_ids[0],
        "best_p5_b": gate_ids[1],
        "best_p5_c": gate_ids[2],
        "best_p5_d": gate_ids[3],
        "best_p5_e": gate_ids[4],
        "best_p5_f": gate_ids[5],
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
        "pair_rows": pair_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "p21_report": p21_report,
        "gap_report": gap_report,
        "f4_report": load_json(F4_REPORT),
        "f4_faces": read_csv_ints(F4_FACE),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p22_rows()
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p21_report = rows["p21_report"]
    gap_report = rows["gap_report"]
    f4_report = rows["f4_report"]
    checks = {
        "input_certificates_available": (
            p21_report.get("all_checks_pass") is True
            and gap_report.get("all_checks_pass") is True
            and f4_report.get("all_checks_pass") is True
        ),
        "symbolic_carrier_matches_f4_faces": (
            [row["face_id"] for row in rows["pair_rows"]],
            [row["label_mask"] for row in rows["pair_rows"]],
            [row["face_id"] for row in rows["f4_faces"]],
            [row["label_mask"] for row in rows["f4_faces"]],
        )
        == ([12, 22, 26], [30, 45, 51], [12, 22, 26], [30, 45, 51]),
        "gate_pairs_are_mirror_neutral": (
            obs["fused_face_count"],
            obs["gate_pair_count"],
            obs["gate_move_count"],
            obs["eta6_preserved_count"],
            obs["total_f4_delta"],
            obs["per_face_abs_delta_sum"],
            obs["all_pair_delta_zero_flag"],
            obs["all_pair_mirror_flag"],
            obs["carrier_neutral_flag"],
        )
        == (3, 3, 6, 6, 0, 0, 1, 1, 1),
        "support_tracks_match_p21_floor": (
            obs["p0_support"],
            obs["p1_support"],
            obs["p2_support"],
            obs["p3_support"],
            obs["p4_support"],
            obs["support_spread"],
            obs["global_floor"],
        )
        == (
            1_083_830_080,
            1_083_830_080,
            1_084_205_056,
            1_084_205_056,
            1_084_322_816,
            492_736,
            492_736,
        ),
        "support_symmetry_and_residual_match": (
            obs["p0_p1_equal_flag"],
            obs["p2_p3_equal_flag"],
            obs["p4_excess_over_min"],
            obs["joint_mult_value"],
        )
        == (1, 1, 492_736, 5_877_006_336),
        "checked_margins_import_positive": (
            obs["hpol_min_margin"],
            obs["repl_min_margin"],
            obs["checked_margin_positive_flag"],
            obs["hpol_weight_sum"],
        )
        == (1, 146, 1, 2_854),
        "claim_boundary_is_explicit": (
            obs["symbolic_carrier_claim_flag"],
            obs["geometric_carrier_claim_flag"],
        )
        == (1, 0),
        "table_shapes_match_codebooks": (
            tuple(pair_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (3, len(PAIR_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "gate_symbolic_carrier",
        "gate_p5_ids": [
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        ],
        "fused_faces": [
            {
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "p5_pair": [row["left_p5_id"], row["right_p5_id"]],
                "support": [
                    row["p0_support"],
                    row["p1_support"],
                    row["p2_support"],
                    row["p3_support"],
                    row["p4_support"],
                ],
                "pair_spread": row["pair_support_spread"],
                "hpol_weight": row["hpol_weight"],
            }
            for row in rows["pair_rows"]
        ],
        "joint_support": [
            obs["p0_support"],
            obs["p1_support"],
            obs["p2_support"],
            obs["p3_support"],
            obs["p4_support"],
        ],
        "support_residual": [
            obs["p0_support"] - min(obs[f"p{index}_support"] for index in range(5)),
            obs["p1_support"] - min(obs[f"p{index}_support"] for index in range(5)),
            obs["p2_support"] - min(obs[f"p{index}_support"] for index in range(5)),
            obs["p3_support"] - min(obs[f"p{index}_support"] for index in range(5)),
            obs["p4_support"] - min(obs[f"p{index}_support"] for index in range(5)),
        ],
        "checked_margins": {
            "hpol_min_margin": obs["hpol_min_margin"],
            "repl_min_margin": obs["repl_min_margin"],
            "positive": obs["checked_margin_positive_flag"],
        },
        "claim_boundary": {
            "symbolic_carrier": obs["symbolic_carrier_claim_flag"],
            "geometric_carrier": obs["geometric_carrier_claim_flag"],
        },
        "reading": (
            "The p21 gate rebuilds a symbolic carrier: three fused faces, each "
            "carried by a mirror pair of p5 moves. The carrier is neutral in "
            "eta6 and F-delta and realizes the exact p20 floor, but this does "
            "not yet supply a new geometric point/face carrier."
        ),
        "pair_table_sha256": sha_array(pair_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p22 = {
        "schema": "eta6.p22@1",
        "object": "eta6",
        "construction": {
            "source": "p21 exact-floor gate plus f4 fused faces",
            "test": "symbolic carrier rebuild",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p22.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P22_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The p21 surgery gate induces an exact symbolic carrier on the "
            "three fused faces (12,30), (22,45), and (26,51). Each face is "
            "represented by a mirror pair of p5 moves with zero F-delta; the "
            "joint carrier realizes the exact global floor 492,736 and keeps "
            "the checked hpol/replacement margins positive. This does not yet "
            "certify a rebuilt geometric point carrier."
        ),
        "stage_protocol": {
            "draft": "start from p21, eta6_gap, and the f4 fused-face carrier",
            "witness": "rebuild the p21 gate as three mirror-paired fused faces",
            "coherence": "check support tracks, mirror neutrality, and imported positive margins",
            "closure": "certify the symbolic carrier induced by the exact surgery gate",
            "emit": "emit compact p22 artifacts and the geometric-carrier seam",
        },
        "inputs": {
            "p5_tables": input_entry(P5_TABLES),
            "f4_report": input_entry(
                F4_REPORT,
                {
                    "status": f4_report.get("status"),
                    "certificate_sha256": f4_report.get("certificate_sha256"),
                },
            ),
            "f4_face": input_entry(F4_FACE),
            "p21_report": input_entry(
                P21_REPORT,
                {
                    "status": p21_report.get("status"),
                    "certificate_sha256": p21_report.get("certificate_sha256"),
                },
            ),
            "gap_report": input_entry(
                GAP_REPORT,
                {
                    "status": gap_report.get("status"),
                    "certificate_sha256": gap_report.get("certificate_sha256"),
                },
            ),
            "hpol_weights": input_entry(HPOL_WEIGHTS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p22": relpath(OUT_DIR / "p22.json"),
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
                "symbolic carrier induced by the p21 exact-floor surgery gate",
                "three fused faces match the f4 carrier masks [30,45,51]",
                "each fused face is a mirror-neutral p5 pair with zero F-delta",
                "joint symbolic carrier realizes the exact p20 floor 492736",
                "checked hpol and replacement margins remain positive",
            ],
            "does_not_certify_because_out_of_scope": [
                "a rebuilt geometric point/face carrier",
                "post-surgery C985 associator or pentagon recomputation",
                "new hpol/replacement row universes beyond eta6_gap",
            ],
        },
        "next_highest_yield_item": (
            "Start p23 by lifting the p22 symbolic carrier to an explicit "
            "geometric point/face carrier, or prove that no such lift is "
            "available from the current data."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p22.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p22.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p22": p22,
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
    write_json(OUT_DIR / "p22.json", payloads["p22"])
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
