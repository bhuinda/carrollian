from __future__ import annotations

import itertools
import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p11 as p11
    from . import derive_eta6_p15 as p15
    from . import derive_eta6_p17 as p17
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
    import derive_eta6_p15 as p15
    import derive_eta6_p17 as p17
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p18"
STATUS = "ETA6_P18_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P6_REPORT = p11.P6_REPORT
P7_REPORT = p11.P7_REPORT
P8_REPORT = p11.P8_REPORT
P11_REPORT = p11.OUT_DIR / "report.json"
P14_REPORT = p15.P14_REPORT
P15_REPORT = p15.OUT_DIR / "report.json"
P17_REPORT = p17.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p18.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p18.py"

CELL_WIDTH = 16_777_216
OFFSETS = list(itertools.product([-1, 0, 1], repeat=4))
CLASS_MAP = {(12, 30): 0, (22, 45): 1, (26, 51): 2}
TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p18_id",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
    "p5_f",
    "joint_p0_support",
    "joint_p1_support",
    "joint_p2_support",
    "joint_p3_support",
    "joint_p4_support",
    "joint_support_min",
    "joint_support_max",
    "joint_support_spread",
    "below_p15_floor_flag",
    "below_p14_floor_flag",
    "below_p11_floor_flag",
    "below_p8_floor_flag",
    "below_p7_floor_flag",
    "below_p6_floor_flag",
    "below_p5_floor_flag",
    "support_equal_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p5_extension_count": 0,
    "triple_count": 1,
    "full_six_count": 2,
    "cell_width": 3,
    "neighbor_cell_count": 4,
    "grid_cell_count": 5,
    "raw_lookup_count": 6,
    "raw_pair_count": 7,
    "outside_raw_pair_count": 8,
    "inside_222_raw_pair_count": 9,
    "outside_unique_low_count": 10,
    "p5_single_floor": 11,
    "p6_pair_floor": 12,
    "p7_triple_floor": 13,
    "p8_quad_floor": 14,
    "p11_quint_floor": 15,
    "p14_basin_six_floor": 16,
    "p15_grid_floor": 17,
    "outside_min_spread": 18,
    "outside_min_below_p15_flag": 19,
    "outside_min_below_p14_flag": 20,
    "outside_below_p15_raw_count": 21,
    "outside_below_p14_raw_count": 22,
    "outside_below_p11_raw_count": 23,
    "outside_below_p8_raw_count": 24,
    "outside_below_p7_raw_count": 25,
    "outside_below_p6_raw_count": 26,
    "outside_below_p5_raw_count": 27,
    "outside_support_equal_raw_count": 28,
    "outside_below_p15_unique_count": 29,
    "outside_below_p14_unique_count": 30,
    "outside_below_p11_unique_count": 31,
    "outside_below_p8_unique_count": 32,
    "outside_below_p7_unique_count": 33,
    "outside_below_p6_unique_count": 34,
    "outside_below_p5_unique_count": 35,
    "outside_support_equal_unique_count": 36,
    "best_p5_a": 37,
    "best_p5_b": 38,
    "best_p5_c": 39,
    "best_p5_d": 40,
    "best_p5_e": 41,
    "best_p5_f": 42,
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


def top_row(
    *,
    rank: int,
    p18_id: int,
    combo: tuple[int, ...],
    ids: np.ndarray,
    joint: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
    p11_floor: int,
    p14_floor: int,
    p15_floor: int,
) -> dict[str, int]:
    p5_ids = [int(ids[index]) for index in combo]
    spread = int(joint.max() - joint.min())
    return {
        "rank": rank,
        "p18_id": p18_id,
        "p5_a": p5_ids[0],
        "p5_b": p5_ids[1],
        "p5_c": p5_ids[2],
        "p5_d": p5_ids[3],
        "p5_e": p5_ids[4],
        "p5_f": p5_ids[5],
        "joint_p0_support": int(joint[0]),
        "joint_p1_support": int(joint[1]),
        "joint_p2_support": int(joint[2]),
        "joint_p3_support": int(joint[3]),
        "joint_p4_support": int(joint[4]),
        "joint_support_min": int(joint.min()),
        "joint_support_max": int(joint.max()),
        "joint_support_spread": spread,
        "below_p15_floor_flag": int(spread < p15_floor),
        "below_p14_floor_flag": int(spread < p14_floor),
        "below_p11_floor_flag": int(spread < p11_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
    }


def build_p18_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    supports = np.asarray(
        [
            [row[f"p{index}_support"] for index in range(5)]
            for row in ext_rows
        ],
        dtype=np.int64,
    )
    ids = np.asarray([row["p5_id"] for row in ext_rows], dtype=np.int64)
    classes = np.asarray(
        [CLASS_MAP[(row["face_id"], row["label_mask"])] for row in ext_rows],
        dtype=np.int8,
    )
    triples = np.asarray(
        list(itertools.combinations(range(len(ext_rows)), 3)),
        dtype=np.int16,
    )
    triple_supports = (
        supports[triples[:, 0]]
        + supports[triples[:, 1]]
        + supports[triples[:, 2]]
    )
    triple_classes = np.zeros((len(triples), 3), dtype=np.int8)
    row_indexes = np.arange(len(triples))
    for index in range(3):
        triple_classes[row_indexes, classes[triples[:, index]]] += 1
    diffs = triple_supports[:, 1:] - triple_supports[:, [0]]
    grid: defaultdict[tuple[int, int, int, int], list[int]] = defaultdict(list)
    quantized = np.floor_divide(diffs, CELL_WIDTH).astype(np.int32)
    for index, key in enumerate(map(tuple, quantized)):
        grid[key].append(index)

    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(load_json(P8_REPORT)["witness"]["quad_min_spread"])
    p11_floor = int(load_json(P11_REPORT)["witness"]["quint_min_spread"])
    p14_floor = int(load_json(P14_REPORT)["witness"]["basin_six_min_spread"])
    p15_floor = int(load_json(P15_REPORT)["witness"]["grid_min_spread"])

    raw_lookup = 0
    raw_pair = 0
    outside_raw = 0
    inside_222_raw = 0
    below_raw = {name: 0 for name in ("p15", "p14", "p11", "p8", "p7", "p6", "p5")}
    equal_raw = 0
    low: dict[tuple[int, ...], tuple[int, np.ndarray]] = {}

    floors = {
        "p15": p15_floor,
        "p14": p14_floor,
        "p11": p11_floor,
        "p8": p8_floor,
        "p7": p7_floor,
        "p6": p6_floor,
        "p5": p5_floor,
    }
    for anchor_index in range(len(triples)):
        target = tuple(
            np.floor_divide(-diffs[anchor_index], CELL_WIDTH).astype(np.int32)
        )
        raw_hits: list[int] = []
        for offset in OFFSETS:
            raw_hits.extend(
                grid.get(
                    tuple(target[axis] + offset[axis] for axis in range(4)),
                    (),
                )
            )
        if not raw_hits:
            continue
        hit_indexes = np.asarray(raw_hits, dtype=np.int32)
        raw_lookup += len(raw_hits)
        anchor = triples[anchor_index]
        hit_triples = triples[hit_indexes]
        disjoint = hit_indexes > anchor_index
        disjoint &= (
            (hit_triples[:, 0] != anchor[0])
            & (hit_triples[:, 1] != anchor[0])
            & (hit_triples[:, 2] != anchor[0])
        )
        disjoint &= (
            (hit_triples[:, 0] != anchor[1])
            & (hit_triples[:, 1] != anchor[1])
            & (hit_triples[:, 2] != anchor[1])
        )
        disjoint &= (
            (hit_triples[:, 0] != anchor[2])
            & (hit_triples[:, 1] != anchor[2])
            & (hit_triples[:, 2] != anchor[2])
        )
        hit_indexes = hit_indexes[disjoint]
        if len(hit_indexes) == 0:
            continue
        raw_pair += len(hit_indexes)
        counts = triple_classes[anchor_index] + triple_classes[hit_indexes]
        inside_222 = (
            (counts[:, 0] == 2)
            & (counts[:, 1] == 2)
            & (counts[:, 2] == 2)
        )
        inside_222_raw += int(inside_222.sum())
        outside_mask = ~inside_222
        outside_raw += int(outside_mask.sum())
        if not bool(outside_mask.any()):
            continue
        hit_indexes = hit_indexes[outside_mask]
        sums = triple_supports[anchor_index] + triple_supports[hit_indexes]
        spreads = sums.max(axis=1) - sums.min(axis=1)
        for name, floor in floors.items():
            below_raw[name] += int((spreads < floor).sum())
        equal_raw += int((spreads == 0).sum())
        for local_index in np.flatnonzero(spreads < p5_floor):
            hit_index = int(hit_indexes[local_index])
            combo = tuple(
                sorted(
                    [
                        *map(int, triples[anchor_index]),
                        *map(int, triples[hit_index]),
                    ]
                )
            )
            low[combo] = (int(spreads[local_index]), sums[local_index])

    unique_below = {name: 0 for name in floors}
    unique_equal = 0
    low_rows = []
    for p18_id, (combo, (spread, joint)) in enumerate(sorted(low.items())):
        for name, floor in floors.items():
            if spread < floor:
                unique_below[name] += 1
        if spread == 0:
            unique_equal += 1
        low_rows.append(
            top_row(
                rank=0,
                p18_id=p18_id,
                combo=combo,
                ids=ids,
                joint=joint,
                p5_floor=p5_floor,
                p6_floor=p6_floor,
                p7_floor=p7_floor,
                p8_floor=p8_floor,
                p11_floor=p11_floor,
                p14_floor=p14_floor,
                p15_floor=p15_floor,
            )
        )
    top_rows = sorted(
        low_rows,
        key=lambda row: (row["joint_support_spread"], row["p18_id"]),
    )[:TOP_N]
    for rank, row in enumerate(top_rows):
        row["rank"] = rank
    best = top_rows[0]
    obs = {
        "p5_extension_count": len(ext_rows),
        "triple_count": len(triples),
        "full_six_count": 11_143_364_232,
        "cell_width": CELL_WIDTH,
        "neighbor_cell_count": len(OFFSETS),
        "grid_cell_count": len(grid),
        "raw_lookup_count": raw_lookup,
        "raw_pair_count": raw_pair,
        "outside_raw_pair_count": outside_raw,
        "inside_222_raw_pair_count": inside_222_raw,
        "outside_unique_low_count": len(low),
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p11_quint_floor": p11_floor,
        "p14_basin_six_floor": p14_floor,
        "p15_grid_floor": p15_floor,
        "outside_min_spread": best["joint_support_spread"],
        "outside_min_below_p15_flag": best["below_p15_floor_flag"],
        "outside_min_below_p14_flag": best["below_p14_floor_flag"],
        "outside_below_p15_raw_count": below_raw["p15"],
        "outside_below_p14_raw_count": below_raw["p14"],
        "outside_below_p11_raw_count": below_raw["p11"],
        "outside_below_p8_raw_count": below_raw["p8"],
        "outside_below_p7_raw_count": below_raw["p7"],
        "outside_below_p6_raw_count": below_raw["p6"],
        "outside_below_p5_raw_count": below_raw["p5"],
        "outside_support_equal_raw_count": equal_raw,
        "outside_below_p15_unique_count": unique_below["p15"],
        "outside_below_p14_unique_count": unique_below["p14"],
        "outside_below_p11_unique_count": unique_below["p11"],
        "outside_below_p8_unique_count": unique_below["p8"],
        "outside_below_p7_unique_count": unique_below["p7"],
        "outside_below_p6_unique_count": unique_below["p6"],
        "outside_below_p5_unique_count": unique_below["p5"],
        "outside_support_equal_unique_count": unique_equal,
        "best_p5_a": best["p5_a"],
        "best_p5_b": best["p5_b"],
        "best_p5_c": best["p5_c"],
        "best_p5_d": best["p5_d"],
        "best_p5_e": best["p5_e"],
        "best_p5_f": best["p5_f"],
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
    return {"top_rows": top_rows, "obs": obs, "obs_rows": obs_rows}


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p18_id": row["p18_id"],
            "p5_ids": [
                row["p5_a"],
                row["p5_b"],
                row["p5_c"],
                row["p5_d"],
                row["p5_e"],
                row["p5_f"],
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
    rows = build_p18_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p15_report = load_json(P15_REPORT)
    p17_report = load_json(P17_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p15_report.get("all_checks_pass") is True
            and p17_report.get("all_checks_pass") is True
        ),
        "wide_screen_scope_matches": (
            obs["p5_extension_count"],
            obs["triple_count"],
            obs["full_six_count"],
            obs["cell_width"],
            obs["neighbor_cell_count"],
            obs["grid_cell_count"],
        )
        == (144, 487_344, 11_143_364_232, 16_777_216, 81, 300_178),
        "wide_screen_pair_counts_match": (
            obs["raw_lookup_count"],
            obs["raw_pair_count"],
            obs["outside_raw_pair_count"],
            obs["inside_222_raw_pair_count"],
            obs["outside_unique_low_count"],
        )
        == (61_647_945, 28_758_081, 26_546_089, 2_211_992, 36_308),
        "outside_floor_does_not_beat_p15_or_p14": (
            obs["p15_grid_floor"],
            obs["p14_basin_six_floor"],
            obs["outside_min_spread"],
            obs["outside_min_below_p15_flag"],
            obs["outside_min_below_p14_flag"],
        )
        == (492_736, 1_164_096, 1_164_096, 0, 0),
        "outside_raw_counts_match": (
            obs["outside_below_p15_raw_count"],
            obs["outside_below_p14_raw_count"],
            obs["outside_below_p11_raw_count"],
            obs["outside_below_p8_raw_count"],
            obs["outside_below_p7_raw_count"],
            obs["outside_below_p6_raw_count"],
            obs["outside_below_p5_raw_count"],
            obs["outside_support_equal_raw_count"],
        )
        == (0, 0, 240, 980, 1_160, 283_070, 363_080, 0),
        "outside_unique_counts_match": (
            obs["outside_below_p15_unique_count"],
            obs["outside_below_p14_unique_count"],
            obs["outside_below_p11_unique_count"],
            obs["outside_below_p8_unique_count"],
            obs["outside_below_p7_unique_count"],
            obs["outside_below_p6_unique_count"],
            obs["outside_below_p5_unique_count"],
            obs["outside_support_equal_unique_count"],
        )
        == (0, 0, 24, 98, 116, 28_307, 36_308, 0),
        "best_candidate_matches_expected": (
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        )
        == (6, 12, 19, 29, 94, 96),
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
        "classification": "wide_grid_outside_222_screen",
        "candidate_construction": (
            "use a 16777216 centered support-difference cell width over all "
            "p5 triples, then discard raw triple-pairs in the exact 2+2+2 "
            "face/mask class exhausted by p17"
        ),
        "cell_width": obs["cell_width"],
        "raw_pair_count": obs["raw_pair_count"],
        "outside_raw_pair_count": obs["outside_raw_pair_count"],
        "inside_222_raw_pair_count": obs["inside_222_raw_pair_count"],
        "outside_unique_low_count": obs["outside_unique_low_count"],
        "outside_min_spread": obs["outside_min_spread"],
        "outside_below_p15_unique_count": obs["outside_below_p15_unique_count"],
        "outside_below_p14_unique_count": obs["outside_below_p14_unique_count"],
        "outside_support_equal_unique_count": obs["outside_support_equal_unique_count"],
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "reading": (
            "The wider outside-2+2+2 screen finds no candidate below the p15 "
            "floor and no support equalizer. Its best outside-class candidate "
            "is the p14 basin winner at spread 1164096."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p18 = {
        "schema": "eta6.p18@1",
        "object": "eta6",
        "construction": {
            "source": "all 144 p5 rows outside the p17 2+2+2 class",
            "test": "wide centered-grid raw triple-pair screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p18.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P18_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A wider outside-2+2+2 centered-grid screen checks 26,546,089 "
            "outside-class disjoint triple-pairs at cell width 16,777,216. "
            "No outside candidate beats p15 or p14, and none equalizes raw "
            "support; the best outside spread is 1,164,096."
        ),
        "stage_protocol": {
            "draft": "start from the p17 exhausted 2+2+2 class boundary",
            "witness": "screen wider centered-grid triple-pairs and discard 2+2+2 hits",
            "coherence": "compare outside-class rows against p15, p14, p11, p8, p7, p6, and p5 floors",
            "closure": "certify bounded outside-class non-improvement and no screened equalizer",
            "emit": "emit compact p18 artifacts and the next seam",
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
            "p15_report": input_entry(
                P15_REPORT,
                {
                    "status": p15_report.get("status"),
                    "certificate_sha256": p15_report.get("certificate_sha256"),
                },
            ),
            "p17_report": input_entry(
                P17_REPORT,
                {
                    "status": p17_report.get("status"),
                    "certificate_sha256": p17_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p18": relpath(OUT_DIR / "p18.json"),
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
                "wide centered-grid screen outside the exact p17 2+2+2 class",
                "26546089 outside-class disjoint triple-pairs checked",
                "36308 outside-class unique low sextuples below the p5 floor captured",
                "no screened outside-class candidate beats p15 or p14",
                "no screened outside-class candidate equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all 11143364232 p5 sextuples",
                "all outside-class candidates at wider or different grid scales",
                "that no unscreened unbalanced sextuple beats 492736",
                "a rebuilt carrier after applying the p15 winner as surgery",
            ],
        },
        "next_highest_yield_item": (
            "Run p19 as the 33554432 outside-2+2+2 screen or start an exact "
            "branch-and-bound over unbalanced class profiles."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p18.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p18.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p18": p18,
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
    write_json(OUT_DIR / "p18.json", payloads["p18"])
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
