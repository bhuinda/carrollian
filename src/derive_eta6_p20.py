from __future__ import annotations

import csv
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p17 as p17
    from . import derive_eta6_p19 as p19
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p17 as p17
    import derive_eta6_p19 as p19
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p20"
STATUS = "ETA6_P20_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P17_REPORT = p17.OUT_DIR / "report.json"
P19_REPORT = p19.OUT_DIR / "report.json"
P19_OBS = p19.OUT_DIR / "obs.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p20.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p20.py"

OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "full_six_count": 0,
    "exact_222_count": 1,
    "outside_count": 2,
    "p5_floor": 3,
    "p14_floor": 4,
    "p15_floor": 5,
    "p19_cell_width": 6,
    "capture_margin": 7,
    "capture_applies_flag": 8,
    "inside_min_spread": 9,
    "outside_min_spread": 10,
    "global_min_spread": 11,
    "inside_below_p15_count": 12,
    "inside_at_p15_count": 13,
    "outside_below_p15_count": 14,
    "outside_below_p14_count": 15,
    "global_below_min_count": 16,
    "global_at_min_count": 17,
    "global_support_equal_count": 18,
    "best_p5_a": 19,
    "best_p5_b": 20,
    "best_p5_c": 21,
    "best_p5_d": 22,
    "best_p5_e": 23,
    "best_p5_f": 24,
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


def read_obs(path: Any) -> dict[int, int]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return {
            int(row["observable_code"]): int(row["value"])
            for row in reader
        }


def build_p20_rows() -> dict[str, Any]:
    p17_report = load_json(P17_REPORT)
    p19_report = load_json(P19_REPORT)
    p19_obs = read_obs(P19_OBS)
    p17_witness = p17_report["witness"]
    p19_witness = p19_report["witness"]

    full_six_count = p19_obs[p19.OBS_CODES["full_six_count"]]
    exact_222_count = int(p17_witness["balance_candidate_count"])
    outside_count = full_six_count - exact_222_count
    p5_floor = p19_obs[p19.OBS_CODES["p5_single_floor"]]
    p14_floor = p19_obs[p19.OBS_CODES["p14_basin_six_floor"]]
    p15_floor = p19_obs[p19.OBS_CODES["p15_grid_floor"]]
    cell_width = p19_obs[p19.OBS_CODES["cell_width"]]
    inside_min = int(p17_witness["balance_min_spread"])
    outside_min = int(p19_witness["outside_min_spread"])
    global_min = min(inside_min, outside_min)
    best = p17_witness["best_candidates"][0]

    obs = {
        "full_six_count": full_six_count,
        "exact_222_count": exact_222_count,
        "outside_count": outside_count,
        "p5_floor": p5_floor,
        "p14_floor": p14_floor,
        "p15_floor": p15_floor,
        "p19_cell_width": cell_width,
        "capture_margin": cell_width - p5_floor,
        "capture_applies_flag": int(cell_width > p5_floor > p14_floor > p15_floor > 0),
        "inside_min_spread": inside_min,
        "outside_min_spread": outside_min,
        "global_min_spread": global_min,
        "inside_below_p15_count": int(p17_witness["below_p15_candidate_count"]),
        "inside_at_p15_count": int(p17_witness["at_p15_floor_candidate_count"]),
        "outside_below_p15_count": int(p19_witness["outside_below_p15_unique_count"]),
        "outside_below_p14_count": int(p19_witness["outside_below_p14_unique_count"]),
        "global_below_min_count": int(p17_witness["below_p15_candidate_count"])
        + int(p19_witness["outside_below_p15_unique_count"]),
        "global_at_min_count": int(p17_witness["at_p15_floor_candidate_count"]),
        "global_support_equal_count": int(p17_witness["support_equal_candidate_count"])
        + int(p19_witness["outside_support_equal_unique_count"]),
        "best_p5_a": int(best["p5_ids"][0]),
        "best_p5_b": int(best["p5_ids"][1]),
        "best_p5_c": int(best["p5_ids"][2]),
        "best_p5_d": int(best["p5_ids"][3]),
        "best_p5_e": int(best["p5_ids"][4]),
        "best_p5_f": int(best["p5_ids"][5]),
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
        "obs": obs,
        "obs_rows": obs_rows,
        "p17_report": p17_report,
        "p19_report": p19_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p20_rows()
    obs = rows["obs"]
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    p17_report = rows["p17_report"]
    p19_report = rows["p19_report"]
    p17_witness = p17_report["witness"]
    p19_witness = p19_report["witness"]
    checks = {
        "input_certificates_available": (
            p17_report.get("all_checks_pass") is True
            and p19_report.get("all_checks_pass") is True
            and p17_report.get("status") == "ETA6_P17_CERTIFIED"
            and p19_report.get("status") == "ETA6_P19_CERTIFIED"
        ),
        "partition_count_matches": (
            obs["full_six_count"],
            obs["exact_222_count"],
            obs["outside_count"],
        )
        == (11_143_364_232, 1_435_249_152, 9_708_115_080),
        "capture_lemma_applies": (
            obs["p19_cell_width"],
            obs["p5_floor"],
            obs["p14_floor"],
            obs["p15_floor"],
            obs["capture_margin"],
            obs["capture_applies_flag"],
        )
        == (33_554_432, 11_213_312, 1_164_096, 492_736, 22_341_120, 1),
        "inside_floor_matches": (
            obs["inside_min_spread"],
            obs["inside_below_p15_count"],
            obs["inside_at_p15_count"],
            int(p17_witness["support_equal_candidate_count"]),
        )
        == (492_736, 0, 1, 0),
        "outside_floor_matches": (
            obs["outside_min_spread"],
            obs["outside_below_p15_count"],
            obs["outside_below_p14_count"],
            int(p19_witness["outside_support_equal_unique_count"]),
        )
        == (1_164_096, 0, 0, 0),
        "global_floor_matches": (
            obs["global_min_spread"],
            obs["global_below_min_count"],
            obs["global_at_min_count"],
            obs["global_support_equal_count"],
        )
        == (492_736, 0, 1, 0),
        "best_candidate_matches_expected": (
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        )
        == (1, 47, 57, 79, 110, 128),
        "table_shapes_match_codebooks": tuple(obs_table.shape)
        == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "classification": "global_six_move_floor_by_cell_capture",
        "capture_lemma": (
            "For any 3+3 split, if the six-row support spread is below the "
            "cell width, then the two triple support-difference cells are "
            "complementary up to one cell in each of the four axes. The p19 "
            "neighbor search therefore captures every outside-class sextuple "
            "with spread below the p5 floor."
        ),
        "full_six_count": obs["full_six_count"],
        "exact_222_count": obs["exact_222_count"],
        "outside_count": obs["outside_count"],
        "p19_cell_width": obs["p19_cell_width"],
        "p5_floor": obs["p5_floor"],
        "p15_floor": obs["p15_floor"],
        "inside_min_spread": obs["inside_min_spread"],
        "outside_min_spread": obs["outside_min_spread"],
        "global_min_spread": obs["global_min_spread"],
        "global_below_min_count": obs["global_below_min_count"],
        "global_at_min_count": obs["global_at_min_count"],
        "global_support_equal_count": obs["global_support_equal_count"],
        "best_p5_ids": [
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        ],
        "reading": (
            "The p15 row is the exact six-move support-spread floor across all "
            "p5 sextuples. The balanced class is exact by p17; every outside "
            "candidate capable of beating it would be caught by the p19 cell "
            "screen, whose outside floor is p14 instead."
        ),
        "observable_table_sha256": sha_array(obs_table),
    }
    p20 = {
        "schema": "eta6.p20@1",
        "object": "eta6",
        "construction": {
            "source": "p17 exact 2+2+2 class plus p19 outside-class cell screen",
            "test": "cell-capture proof for the global six-move floor",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p20.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P20_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The p15 winner [1,47,57,79,110,128] is the exact global "
            "six-move support-spread floor over all 11,143,364,232 p5 "
            "sextuples, with spread 492,736. No p5 sextuple has lower spread "
            "and no p5 sextuple equalizes raw support."
        ),
        "stage_protocol": {
            "draft": "partition all sextuples into exact 2+2+2 and outside classes",
            "witness": "use p17 for the exact class and p19 for captured outside low-spread candidates",
            "coherence": "prove the p19 cell width captures every outside candidate below the p5 floor",
            "closure": "combine the two branches into a global six-move floor",
            "emit": "emit compact p20 artifacts and the next seam",
        },
        "inputs": {
            "p17_report": input_entry(
                P17_REPORT,
                {
                    "status": p17_report.get("status"),
                    "certificate_sha256": p17_report.get("certificate_sha256"),
                },
            ),
            "p19_report": input_entry(
                P19_REPORT,
                {
                    "status": p19_report.get("status"),
                    "certificate_sha256": p19_report.get("certificate_sha256"),
                },
            ),
            "p19_obs": input_entry(P19_OBS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p20": relpath(OUT_DIR / "p20.json"),
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
                "exact global six-move support-spread floor over all p5 sextuples",
                "11143364232 p5 sextuples partitioned into exact 2+2+2 and outside classes",
                "p15 winner is the unique global minimizer at spread 492736",
                "no global six-move p5 support equalizer exists",
            ],
            "does_not_certify_because_out_of_scope": [
                "a rebuilt carrier after applying the p15 winner as surgery",
                "seven-or-more p5 move searches",
                "new hpol/replacement row universes beyond eta6_gap",
                "categorical pivotal, spherical, unitary, or braided normalization",
            ],
        },
        "next_highest_yield_item": (
            "Start p21 by applying the p15 exact floor as a surgery move and "
            "recomputing the carrier/gap margins, rather than searching more "
            "six-move p5 combinations."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p20.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p20.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p20": p20,
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
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
    write_json(OUT_DIR / "p20.json", payloads["p20"])
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
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
