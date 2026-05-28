from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p11 as p11
    from . import derive_eta6_p12 as p12
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
    import derive_eta6_p11 as p11
    import derive_eta6_p12 as p12
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p13"
STATUS = "ETA6_P13_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P11_REPORT = p11.OUT_DIR / "report.json"
P11_TABLES = p11.OUT_DIR / "tables.npz"
P12_REPORT = p12.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p13.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p13.py"

TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p13_id",
    "seed_rank",
    "seed_p11_id",
    "extension_p5",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
    "p5_f",
    "face_a",
    "face_b",
    "face_c",
    "face_d",
    "face_e",
    "face_f",
    "mask_a",
    "mask_b",
    "mask_c",
    "mask_d",
    "mask_e",
    "mask_f",
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
    "below_p12_floor_flag",
    "below_p11_floor_flag",
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
    "p11_seed_count": 1,
    "candidate_count": 2,
    "p5_single_floor": 3,
    "p6_pair_floor": 4,
    "p7_triple_floor": 5,
    "p8_quad_floor": 6,
    "p11_quint_floor": 7,
    "p12_seeded_floor": 8,
    "top32_six_min_spread": 9,
    "top32_six_min_below_p12_flag": 10,
    "top32_six_min_below_p11_flag": 11,
    "top32_six_min_below_p8_flag": 12,
    "below_p12_candidate_count": 13,
    "below_p11_candidate_count": 14,
    "below_p8_candidate_count": 15,
    "below_p7_candidate_count": 16,
    "below_p6_candidate_count": 17,
    "below_p5_candidate_count": 18,
    "support_equal_candidate_count": 19,
    "same_face_candidate_count": 20,
    "same_mask_candidate_count": 21,
    "best_p13_id": 22,
    "best_seed_rank": 23,
    "best_seed_p11_id": 24,
    "best_extension_p5": 25,
    "best_p5_a": 26,
    "best_p5_b": 27,
    "best_p5_c": 28,
    "best_p5_d": 29,
    "best_p5_e": 30,
    "best_p5_f": 31,
    "best_same_face_spread": 32,
    "best_same_face_p13_id": 33,
    "best_same_mask_spread": 34,
    "best_same_mask_p13_id": 35,
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
    p13_id: int,
    seed: dict[str, int],
    extension: dict[str, int],
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
    p11_floor: int,
    p12_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    p5_ids = [row["p5_id"] for row in rows]
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p13_id": p13_id,
        "seed_rank": seed["rank"],
        "seed_p11_id": seed["p11_id"],
        "extension_p5": extension["p5_id"],
        "p5_a": p5_ids[0],
        "p5_b": p5_ids[1],
        "p5_c": p5_ids[2],
        "p5_d": p5_ids[3],
        "p5_e": p5_ids[4],
        "p5_f": p5_ids[5],
        "face_a": faces[0],
        "face_b": faces[1],
        "face_c": faces[2],
        "face_d": faces[3],
        "face_e": faces[4],
        "face_f": faces[5],
        "mask_a": masks[0],
        "mask_b": masks[1],
        "mask_c": masks[2],
        "mask_d": masks[3],
        "mask_e": masks[4],
        "mask_f": masks[5],
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
        "below_p12_floor_flag": int(spread < p12_floor),
        "below_p11_floor_flag": int(spread < p11_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p13_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    p11_tables = np.load(P11_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    p11_rows = rows_from_table(
        np.asarray(p11_tables["top_table"], dtype=np.int64),
        p11.TOP_COLUMNS,
    )
    p11_report = load_json(P11_REPORT)
    p12_report = load_json(P12_REPORT)
    row_by_id = {row["p5_id"]: row for row in ext_rows}
    support_by_id = {row["p5_id"]: support(row) for row in ext_rows}
    all_ids = sorted(row_by_id)
    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(p11.P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(p11.P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(p11_report["witness"]["p8_quad_floor"])
    p11_floor = int(p11_report["witness"]["quint_min_spread"])
    p12_floor = int(p12_report["witness"]["seeded_six_min_spread"])

    candidates: dict[tuple[int, ...], tuple[dict[str, int], int]] = {}
    for seed in p11_rows:
        seed_ids = [
            seed["p5_a"],
            seed["p5_b"],
            seed["p5_c"],
            seed["p5_d"],
            seed["p5_e"],
        ]
        for extension_id in all_ids:
            if extension_id in seed_ids:
                continue
            key = tuple(sorted([*seed_ids, extension_id]))
            candidates.setdefault(key, (seed, extension_id))

    top_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    below_p12 = 0
    below_p11 = 0
    below_p8 = 0
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0
    same_face_count = 0
    same_mask_count = 0

    for p13_id, (candidate, (seed, extension_id)) in enumerate(sorted(candidates.items())):
        rows = [row_by_id[p5_id] for p5_id in candidate]
        joint = sum((support_by_id[p5_id] for p5_id in candidate), np.zeros(5, dtype=np.int64))
        row = ranked_row(
            rank=0,
            p13_id=p13_id,
            seed=seed,
            extension=row_by_id[extension_id],
            rows=rows,
            joint=joint,
            p5_floor=p5_floor,
            p6_floor=p6_floor,
            p7_floor=p7_floor,
            p8_floor=p8_floor,
            p11_floor=p11_floor,
            p12_floor=p12_floor,
        )
        spread = row["joint_support_spread"]
        if spread < p12_floor:
            below_p12 += 1
        if spread < p11_floor:
            below_p11 += 1
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
        if row["same_face_flag"] == 1:
            same_face_count += 1
        if row["same_mask_flag"] == 1:
            same_mask_count += 1

        key = (spread, p13_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p13_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p13_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p13_id"],
            )
        ):
            best_same_mask = row
        top_rows.append(row)

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p13 search")
    top_rows = sorted(
        top_rows,
        key=lambda row: (row["joint_support_spread"], row["p13_id"]),
    )[:TOP_N]
    for rank, row in enumerate(top_rows):
        row["rank"] = rank

    obs = {
        "p5_extension_count": len(ext_rows),
        "p11_seed_count": len(p11_rows),
        "candidate_count": len(candidates),
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p11_quint_floor": p11_floor,
        "p12_seeded_floor": p12_floor,
        "top32_six_min_spread": best_any["joint_support_spread"],
        "top32_six_min_below_p12_flag": int(best_any["joint_support_spread"] < p12_floor),
        "top32_six_min_below_p11_flag": int(best_any["joint_support_spread"] < p11_floor),
        "top32_six_min_below_p8_flag": int(best_any["joint_support_spread"] < p8_floor),
        "below_p12_candidate_count": below_p12,
        "below_p11_candidate_count": below_p11,
        "below_p8_candidate_count": below_p8,
        "below_p7_candidate_count": below_p7,
        "below_p6_candidate_count": below_p6,
        "below_p5_candidate_count": below_p5,
        "support_equal_candidate_count": equal,
        "same_face_candidate_count": same_face_count,
        "same_mask_candidate_count": same_mask_count,
        "best_p13_id": best_any["p13_id"],
        "best_seed_rank": best_any["seed_rank"],
        "best_seed_p11_id": best_any["seed_p11_id"],
        "best_extension_p5": best_any["extension_p5"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_p5_e": best_any["p5_e"],
        "best_p5_f": best_any["p5_f"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p13_id": best_same_face["p13_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p13_id": best_same_mask["p13_id"],
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
    }


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p13_id": row["p13_id"],
            "seed_rank": row["seed_rank"],
            "seed_p11_id": row["seed_p11_id"],
            "extension_p5": row["extension_p5"],
            "p5_ids": [
                row["p5_a"],
                row["p5_b"],
                row["p5_c"],
                row["p5_d"],
                row["p5_e"],
                row["p5_f"],
            ],
            "faces": [
                row["face_a"],
                row["face_b"],
                row["face_c"],
                row["face_d"],
                row["face_e"],
                row["face_f"],
            ],
            "masks": [
                row["mask_a"],
                row["mask_b"],
                row["mask_c"],
                row["mask_d"],
                row["mask_e"],
                row["mask_f"],
            ],
            "support": [
                row["joint_p0_support"],
                row["joint_p1_support"],
                row["joint_p2_support"],
                row["joint_p3_support"],
                row["joint_p4_support"],
            ],
            "spread": row["joint_support_spread"],
        }
        for row in rows
    ]


def build_payloads() -> dict[str, Any]:
    rows = build_p13_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p11_report = load_json(P11_REPORT)
    p12_report = load_json(P12_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p11_report.get("all_checks_pass") is True
            and p12_report.get("all_checks_pass") is True
        ),
        "top32_screen_size_matches": (
            obs["p5_extension_count"],
            obs["p11_seed_count"],
            obs["candidate_count"],
        )
        == (144, 32, 4_447),
        "top32_six_improves_p12_but_not_p11": (
            obs["p12_seeded_floor"],
            obs["p11_quint_floor"],
            obs["top32_six_min_spread"],
            obs["top32_six_min_below_p12_flag"],
            obs["top32_six_min_below_p11_flag"],
        )
        == (10_529_536, 1_815_040, 7_982_592, 1, 0),
        "descent_counts_match": (
            obs["below_p12_candidate_count"],
            obs["below_p11_candidate_count"],
            obs["below_p8_candidate_count"],
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (46, 0, 0, 0, 46, 78, 0),
        "same_face_and_mask_counts_match": (
            obs["same_face_candidate_count"],
            obs["same_mask_candidate_count"],
        )
        == (85, 85),
        "best_candidate_matches_expected": (
            obs["best_p13_id"],
            obs["best_seed_rank"],
            obs["best_seed_p11_id"],
            obs["best_extension_p5"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        )
        == (762, 24, 143_959_038, 2, 2, 8, 52, 56, 116, 141),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p13_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p13_id"],
        )
        == (9_602_944, 29, 9_602_944, 29),
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
        "classification": "top32_six_move_frontier_relaxation",
        "candidate_construction": "extend each p11 top-32 quintuple by one additional p5 move",
        "p12_seeded_floor": obs["p12_seeded_floor"],
        "p11_quint_floor": obs["p11_quint_floor"],
        "top32_six_min_spread": obs["top32_six_min_spread"],
        "below_p12_candidate_count": obs["below_p12_candidate_count"],
        "below_p11_candidate_count": obs["below_p11_candidate_count"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p6_candidate_count": obs["below_p6_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "same_face_candidate_count": obs["same_face_candidate_count"],
        "same_mask_candidate_count": obs["same_mask_candidate_count"],
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "reading": (
            "The p11 top-32 six-move frontier relaxes below the p12 seeded "
            "two-row screen but stays above the p11 five-move floor and finds "
            "no support equalizer."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p13 = {
        "schema": "eta6.p13@1",
        "object": "eta6",
        "construction": {
            "source": "p11 top-32 rows",
            "test": "top-32 six-move extension support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p13.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P13_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The p11 top-32 six-move frontier improves on the p12 two-seed "
            "six-move floor, lowering best spread to 7982592, but no candidate "
            "beats the p11 five-move floor and none equalizes raw support."
        ),
        "stage_protocol": {
            "draft": "start from the p11 top-32 quintuples",
            "witness": "extend each top p11 row by every remaining p5 move and deduplicate",
            "coherence": "compare the top-32 six-move frontier against p12, p11, p8, p7, p6, and p5 floors",
            "closure": "certify broader six-move frontier relaxation without support equalization",
            "emit": "emit compact p13 artifacts and the next seam",
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
            "p11_report": input_entry(
                P11_REPORT,
                {
                    "status": p11_report.get("status"),
                    "certificate_sha256": p11_report.get("certificate_sha256"),
                },
            ),
            "p11_tables": input_entry(P11_TABLES),
            "p12_report": input_entry(
                P12_REPORT,
                {
                    "status": p12_report.get("status"),
                    "certificate_sha256": p12_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p13": relpath(OUT_DIR / "p13.json"),
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
                "top-32 p11 six-move frontier over 4447 deduplicated candidates",
                "46 top-32 six-move candidates beat the p12 seeded six-move floor",
                "no top-32 six-move candidate beats the p11 five-move floor",
                "best top-32 six-move support spread is 7982592",
                "no top-32 six-move candidate equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all p5 sextuples",
                "a new post-surgery carrier-level eta6 gap",
                "global closure under repeated non-cubic surgeries",
                "that metric conductance has reached its final asymptote",
            ],
        },
        "next_highest_yield_item": (
            "Run a pair/triple meet-in-the-middle six-move search for sextuples "
            "whose five-subsets hit the p11 top-32 support basin."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p13.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p13.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p13": p13,
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
    write_json(OUT_DIR / "p13.json", payloads["p13"])
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
