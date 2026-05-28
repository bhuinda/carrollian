from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p18 as p18
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p18 as p18
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p19"
STATUS = "ETA6_P19_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = p18.INDEX_PATH

P5_REPORT = p18.P5_REPORT
P5_TABLES = p18.P5_TABLES
P15_REPORT = p18.P15_REPORT
P17_REPORT = p18.P17_REPORT

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p19.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p19.py"

CELL_WIDTH = 33_554_432
TOP_N = p18.TOP_N
TOP_COLUMNS = [
    "rank",
    "p19_id",
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
OBS_COLUMNS = p18.OBS_COLUMNS
OBS_CODES = p18.OBS_CODES


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    return p18.csv_text(columns, rows)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return p18.table_from_rows(columns, rows)


def build_p19_rows() -> dict[str, Any]:
    previous_cell_width = p18.CELL_WIDTH
    try:
        p18.CELL_WIDTH = CELL_WIDTH
        rows = p18.build_p18_rows()
    finally:
        p18.CELL_WIDTH = previous_cell_width

    top_rows = []
    for row in rows["top_rows"]:
        copied = dict(row)
        copied["p19_id"] = copied.pop("p18_id")
        top_rows.append(copied)
    return {
        "top_rows": top_rows,
        "obs": rows["obs"],
        "obs_rows": rows["obs_rows"],
    }


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p19_id": row["p19_id"],
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
    rows = build_p19_rows()
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
        "expanded_screen_scope_matches": (
            obs["p5_extension_count"],
            obs["triple_count"],
            obs["full_six_count"],
            obs["cell_width"],
            obs["neighbor_cell_count"],
            obs["grid_cell_count"],
        )
        == (144, 487_344, 11_143_364_232, 33_554_432, 81, 114_454),
        "expanded_screen_pair_counts_match": (
            obs["raw_lookup_count"],
            obs["raw_pair_count"],
            obs["outside_raw_pair_count"],
            obs["inside_222_raw_pair_count"],
            obs["outside_unique_low_count"],
        )
        == (722_138_260, 337_311_229, 307_586_410, 29_724_819, 36_308),
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
        "classification": "expanded_grid_outside_222_screen",
        "candidate_construction": (
            "use a 33554432 centered support-difference cell width over all "
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
            "The expanded outside-2+2+2 screen increases raw outside coverage "
            "by more than 11x over p18, but repeats the same p14 outside floor. "
            "No screened outside-class candidate beats p15 or p14, and none "
            "equalizes raw support."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p19 = {
        "schema": "eta6.p19@1",
        "object": "eta6",
        "construction": {
            "source": "all 144 p5 rows outside the p17 2+2+2 class",
            "test": "expanded centered-grid raw triple-pair screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p19.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P19_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "An expanded outside-2+2+2 centered-grid screen checks "
            "307,586,410 outside-class disjoint triple-pairs at cell width "
            "33,554,432. No outside candidate beats p15 or p14, and none "
            "equalizes raw support; the best outside spread remains 1,164,096."
        ),
        "stage_protocol": {
            "draft": "start from the p18 outside-class screen boundary",
            "witness": "expand the centered-grid triple-pair screen and discard 2+2+2 hits",
            "coherence": "compare outside-class rows against p15, p14, p11, p8, p7, p6, and p5 floors",
            "closure": "certify expanded outside-class non-improvement and no screened equalizer",
            "emit": "emit compact p19 artifacts and the next seam",
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
            "p19": relpath(OUT_DIR / "p19.json"),
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
                "expanded centered-grid screen outside the exact p17 2+2+2 class",
                "307586410 outside-class disjoint triple-pairs checked",
                "36308 outside-class unique low sextuples below the p5 floor captured",
                "no screened outside-class candidate beats p15 or p14",
                "no screened outside-class candidate equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all 11143364232 p5 sextuples",
                "all outside-class candidates at every grid scale",
                "that no unscreened unbalanced sextuple beats 492736",
                "a rebuilt carrier after applying the p15 winner as surgery",
            ],
        },
        "next_highest_yield_item": (
            "Start p20 as an exact branch-and-bound over unbalanced class "
            "profiles, using p15 as the incumbent and p19 as the outside-screen "
            "negative control."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p19.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p19.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p19": p19,
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
    write_json(OUT_DIR / "p19.json", payloads["p19"])
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
