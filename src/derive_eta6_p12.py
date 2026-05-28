from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_gap as gap
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p11 as p11
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_gap as gap
    import derive_eta6_p5 as p5
    import derive_eta6_p11 as p11
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p12"
STATUS = "ETA6_P12_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P11_REPORT = p11.OUT_DIR / "report.json"
P11_TABLES = p11.OUT_DIR / "tables.npz"
GAP_REPORT = gap.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p12.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p12.py"

TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p12_id",
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
    "seeded_six_min_spread": 8,
    "seeded_six_min_below_p11_flag": 9,
    "seeded_six_min_below_p8_flag": 10,
    "below_p11_candidate_count": 11,
    "below_p8_candidate_count": 12,
    "below_p7_candidate_count": 13,
    "below_p6_candidate_count": 14,
    "below_p5_candidate_count": 15,
    "support_equal_candidate_count": 16,
    "best_p12_id": 17,
    "best_seed_rank": 18,
    "best_seed_p11_id": 19,
    "best_extension_p5": 20,
    "best_p5_a": 21,
    "best_p5_b": 22,
    "best_p5_c": 23,
    "best_p5_d": 24,
    "best_p5_e": 25,
    "best_p5_f": 26,
    "best_same_face_spread": 27,
    "best_same_face_p12_id": 28,
    "best_same_mask_spread": 29,
    "best_same_mask_p12_id": 30,
    "gap_hpol_min_margin": 31,
    "gap_hpol_row_count": 32,
    "gap_repl_min_margin": 33,
    "gap_repl_row_count": 34,
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
    p12_id: int,
    seed: dict[str, int],
    extension: dict[str, int],
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
    p11_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    p5_ids = [row["p5_id"] for row in rows]
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p12_id": p12_id,
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
        "below_p11_floor_flag": int(spread < p11_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p12_rows() -> dict[str, Any]:
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
    gap_report = load_json(GAP_REPORT)
    p8_floor = int(p11_report["witness"]["p8_quad_floor"])
    p11_floor = int(p11_report["witness"]["quint_min_spread"])
    seeds = [row for row in p11_rows if row["joint_support_spread"] < p8_floor]
    row_by_id = {row["p5_id"]: row for row in ext_rows}
    support_by_id = {row["p5_id"]: support(row) for row in ext_rows}
    all_ids = sorted(row_by_id)
    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(p11.P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(p11.P7_REPORT)["witness"]["triple_min_spread"])

    candidates: dict[tuple[int, ...], tuple[dict[str, int], int]] = {}
    for seed in seeds:
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
    below_p11 = 0
    below_p8 = 0
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0

    for p12_id, (candidate, (seed, extension_id)) in enumerate(sorted(candidates.items())):
        rows = [row_by_id[p5_id] for p5_id in candidate]
        joint = sum((support_by_id[p5_id] for p5_id in candidate), np.zeros(5, dtype=np.int64))
        row = ranked_row(
            rank=0,
            p12_id=p12_id,
            seed=seed,
            extension=row_by_id[extension_id],
            rows=rows,
            joint=joint,
            p5_floor=p5_floor,
            p6_floor=p6_floor,
            p7_floor=p7_floor,
            p8_floor=p8_floor,
            p11_floor=p11_floor,
        )
        spread = row["joint_support_spread"]
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
        key = (spread, p12_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p12_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p12_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p12_id"],
            )
        ):
            best_same_mask = row
        top_rows.append(row)

    if best_any is None:
        raise ValueError("empty p12 search")
    if best_same_face is None:
        best_same_face = best_any
    if best_same_mask is None:
        best_same_mask = best_any
    top_rows = sorted(
        top_rows,
        key=lambda row: (row["joint_support_spread"], row["p12_id"]),
    )[:TOP_N]
    for rank, row in enumerate(top_rows):
        row["rank"] = rank

    gap_hpol = gap_report["witness"]["hpol"]
    gap_repl = gap_report["witness"]["repl"]
    obs = {
        "p5_extension_count": len(ext_rows),
        "p11_seed_count": len(seeds),
        "candidate_count": len(candidates),
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p11_quint_floor": p11_floor,
        "seeded_six_min_spread": best_any["joint_support_spread"],
        "seeded_six_min_below_p11_flag": int(best_any["joint_support_spread"] < p11_floor),
        "seeded_six_min_below_p8_flag": int(best_any["joint_support_spread"] < p8_floor),
        "below_p11_candidate_count": below_p11,
        "below_p8_candidate_count": below_p8,
        "below_p7_candidate_count": below_p7,
        "below_p6_candidate_count": below_p6,
        "below_p5_candidate_count": below_p5,
        "support_equal_candidate_count": equal,
        "best_p12_id": best_any["p12_id"],
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
        "best_same_face_p12_id": best_same_face["p12_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p12_id": best_same_mask["p12_id"],
        "gap_hpol_min_margin": int(gap_hpol["min_margin"]),
        "gap_hpol_row_count": int(gap_hpol["row_count"]),
        "gap_repl_min_margin": int(gap_repl["min_margin"]),
        "gap_repl_row_count": int(gap_repl["row_count"]),
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
            "p12_id": row["p12_id"],
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
    rows = build_p12_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p11_report = load_json(P11_REPORT)
    gap_report = load_json(GAP_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p11_report.get("all_checks_pass") is True
            and gap_report.get("all_checks_pass") is True
        ),
        "seeded_screen_size_matches": (
            obs["p5_extension_count"],
            obs["p11_seed_count"],
            obs["candidate_count"],
        )
        == (144, 2, 278),
        "seeded_six_stalls_above_p11": (
            obs["p11_quint_floor"],
            obs["seeded_six_min_spread"],
            obs["seeded_six_min_below_p11_flag"],
            obs["seeded_six_min_below_p8_flag"],
        )
        == (1_815_040, 10_529_536, 0, 0),
        "descent_counts_match": (
            obs["below_p11_candidate_count"],
            obs["below_p8_candidate_count"],
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (0, 0, 0, 0, 2, 0),
        "best_candidate_matches_expected": (
            obs["best_p12_id"],
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
        == (31, 0, 67_415_100, 32, 1, 8, 32, 41, 52, 54),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p12_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p12_id"],
        )
        == (10_529_536, 31, 10_529_536, 31),
        "carrier_gap_import_matches_eta6_gap": (
            obs["gap_hpol_min_margin"],
            obs["gap_hpol_row_count"],
            obs["gap_repl_min_margin"],
            obs["gap_repl_row_count"],
        )
        == (1, 4_903_515, 146, 2_831_367),
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
        "classification": "seeded_six_move_extension_stall",
        "candidate_construction": (
            "extend the two p11 quintuples below the p8 floor by one additional p5 move"
        ),
        "p11_quint_floor": obs["p11_quint_floor"],
        "seeded_six_min_spread": obs["seeded_six_min_spread"],
        "below_p11_candidate_count": obs["below_p11_candidate_count"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "carrier_gap_import": {
            "hpol_min_margin": obs["gap_hpol_min_margin"],
            "hpol_row_count": obs["gap_hpol_row_count"],
            "repl_min_margin": obs["gap_repl_min_margin"],
            "repl_row_count": obs["gap_repl_row_count"],
            "reading": (
                "The current carrier-level eta6 gap remains imported from eta6_gap; "
                "p12 does not construct a new post-surgery carrier."
            ),
        },
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "reading": (
            "The direct six-move extensions of the two p8-beating p11 rows do not "
            "continue the descent. The current carrier gap certificate is still "
            "positive, but no new carrier surgery gap is claimed here."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p12 = {
        "schema": "eta6.p12@1",
        "object": "eta6",
        "construction": {
            "source": "two p11 rows below the p8 floor plus eta6_gap carrier margin",
            "test": "seeded six-move extension support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p12.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P12_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The seeded six-move extension screen around the two p11 rows below "
            "the p8 floor does not continue the p11 descent: best spread is "
            "10529536, with no support equalizer. The current eta6 carrier gap "
            "is imported from eta6_gap with hpol margin 1 and replacement margin 146."
        ),
        "stage_protocol": {
            "draft": "start from the two p11 quintuples below the p8 floor",
            "witness": "extend each seed by every remaining p5 move and deduplicate",
            "coherence": "compare seeded six-move spread against p11, p8, p7, p6, and p5 floors",
            "closure": "certify seeded six-move stall plus imported carrier gap",
            "emit": "emit compact p12 artifacts and the next seam",
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
            "gap_report": input_entry(
                GAP_REPORT,
                {
                    "status": gap_report.get("status"),
                    "certificate_sha256": gap_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p12": relpath(OUT_DIR / "p12.json"),
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
                "seeded six-move extension screen over 278 deduplicated candidates",
                "no seeded six-move candidate beats the p11 five-move floor",
                "best seeded six-move support spread is 10529536",
                "no seeded six-move candidate equalizes raw support",
                "current eta6 carrier gap certificate is still positive via eta6_gap",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all p5 sextuples",
                "a new post-surgery carrier-level eta6 gap",
                "global closure under repeated non-cubic surgeries",
                "that metric conductance has reached its final asymptote",
            ],
        },
        "next_highest_yield_item": (
            "Run a broader six-move meet-in-the-middle screen around the p11 "
            "top-32 rows, then only build a new carrier if a support-level "
            "candidate beats p11."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p12.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p12.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p12": p12,
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
    write_json(OUT_DIR / "p12.json", payloads["p12"])
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
