from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from . import derive_eta6_gap as gap
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p15 as p15
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
    import derive_eta6_p15 as p15
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p16"
STATUS = "ETA6_P16_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P15_REPORT = p15.OUT_DIR / "report.json"
P15_TABLES = p15.OUT_DIR / "tables.npz"
GAP_REPORT = gap.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p16.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p16.py"

TOP_N = 16
FUSED_FACE_MASKS = ((12, 30), (22, 45), (26, 51))
ROW_COLUMNS = [
    "rank",
    "p15_id",
    "mirror_rank",
    "mirror_closed_flag",
    "self_mirror_flag",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
    "p5_f",
    "joint_support_spread",
    "support_equal_flag",
    "eta6_preserved_count",
    "eta6_all_preserved_flag",
    "face12_mask30_count",
    "face22_mask45_count",
    "face26_mask51_count",
    "balanced_222_flag",
    "total_f4_delta",
    "abs_total_f4_delta",
    "per_face_abs_delta_sum",
    "per_face_delta_zero_flag",
    "carrier_neutral_flag",
    "hpol_min_margin",
    "repl_min_margin",
    "carrier_margin_positive_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "top_row_count": 0,
    "component_move_count": 1,
    "mirror_closed_row_count": 2,
    "self_mirror_row_count": 3,
    "mirror_pair_count": 4,
    "eta6_preserved_row_count": 5,
    "eta6_preserved_move_count": 6,
    "global_delta_zero_row_count": 7,
    "per_face_delta_zero_row_count": 8,
    "carrier_neutral_row_count": 9,
    "balanced_222_row_count": 10,
    "winner_rank": 11,
    "winner_p15_id": 12,
    "winner_spread": 13,
    "winner_balanced_222_flag": 14,
    "winner_carrier_neutral_flag": 15,
    "winner_hpol_min_margin": 16,
    "winner_repl_min_margin": 17,
    "winner_margin_positive_flag": 18,
    "p15_screen_min_spread": 19,
    "p15_unique_candidate_count": 20,
    "support_equal_top_row_count": 21,
    "imported_hpol_min_margin": 22,
    "imported_repl_min_margin": 23,
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


def support_vector(row: dict[str, int]) -> tuple[int, int, int, int, int]:
    return (
        row["joint_p0_support"],
        row["joint_p1_support"],
        row["joint_p2_support"],
        row["joint_p3_support"],
        row["joint_p4_support"],
    )


def mirror_support(
    support: tuple[int, int, int, int, int],
) -> tuple[int, int, int, int, int]:
    return (support[1], support[0], support[3], support[2], support[4])


def build_p16_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    p15_tables = np.load(P15_TABLES, allow_pickle=False)
    p5_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    top_rows = rows_from_table(
        np.asarray(p15_tables["top_table"], dtype=np.int64),
        p15.TOP_COLUMNS,
    )[:TOP_N]
    p5_by_id = {row["p5_id"]: row for row in p5_rows}
    support_to_rank = {support_vector(row): row["rank"] for row in top_rows}
    gap_report = load_json(GAP_REPORT)
    hpol_min = int(gap_report["witness"]["hpol"]["min_margin"])
    repl_min = int(gap_report["witness"]["repl"]["min_margin"])
    rows: list[dict[str, int]] = []

    for row in top_rows:
        ids = [row[f"p5_{letter}"] for letter in "abcdef"]
        pieces = [p5_by_id[p5_id] for p5_id in ids]
        counts = Counter((piece["face_id"], piece["label_mask"]) for piece in pieces)
        deltas: defaultdict[tuple[int, int], int] = defaultdict(int)
        for piece in pieces:
            deltas[(piece["face_id"], piece["label_mask"])] += piece["f4_delta"]
        per_face_abs_delta = sum(abs(value) for value in deltas.values())
        total_delta = sum(piece["f4_delta"] for piece in pieces)
        eta6_count = sum(piece["eta6_preserved_flag"] for piece in pieces)
        mirror_rank = support_to_rank.get(mirror_support(support_vector(row)), -1)
        balanced_222 = int(
            all(counts[face_mask] == 2 for face_mask in FUSED_FACE_MASKS)
            and sum(counts.values()) == 6
        )
        per_face_zero = int(per_face_abs_delta == 0)
        carrier_neutral = int(
            eta6_count == 6 and total_delta == 0 and per_face_zero == 1
        )
        rows.append(
            {
                "rank": row["rank"],
                "p15_id": row["p15_id"],
                "mirror_rank": mirror_rank,
                "mirror_closed_flag": int(mirror_rank >= 0),
                "self_mirror_flag": int(mirror_rank == row["rank"]),
                "p5_a": ids[0],
                "p5_b": ids[1],
                "p5_c": ids[2],
                "p5_d": ids[3],
                "p5_e": ids[4],
                "p5_f": ids[5],
                "joint_support_spread": row["joint_support_spread"],
                "support_equal_flag": row["support_equal_flag"],
                "eta6_preserved_count": eta6_count,
                "eta6_all_preserved_flag": int(eta6_count == 6),
                "face12_mask30_count": counts[(12, 30)],
                "face22_mask45_count": counts[(22, 45)],
                "face26_mask51_count": counts[(26, 51)],
                "balanced_222_flag": balanced_222,
                "total_f4_delta": total_delta,
                "abs_total_f4_delta": abs(total_delta),
                "per_face_abs_delta_sum": per_face_abs_delta,
                "per_face_delta_zero_flag": per_face_zero,
                "carrier_neutral_flag": carrier_neutral,
                "hpol_min_margin": hpol_min if carrier_neutral else -1,
                "repl_min_margin": repl_min if carrier_neutral else -1,
                "carrier_margin_positive_flag": int(
                    carrier_neutral and hpol_min > 0 and repl_min > 0
                ),
            }
        )
    return {"rows": rows, "hpol_min": hpol_min, "repl_min": repl_min}


def build_payloads() -> dict[str, Any]:
    p16_rows = build_p16_rows()
    row_table = table_from_rows(ROW_COLUMNS, p16_rows["rows"])
    p5_report = load_json(P5_REPORT)
    p15_report = load_json(P15_REPORT)
    gap_report = load_json(GAP_REPORT)
    winner = p16_rows["rows"][0]
    mirror_pairs = {
        tuple(sorted((row["rank"], row["mirror_rank"])))
        for row in p16_rows["rows"]
        if row["mirror_rank"] >= 0 and row["rank"] != row["mirror_rank"]
    }
    obs = {
        "top_row_count": len(p16_rows["rows"]),
        "component_move_count": sum(row["eta6_preserved_count"] for row in p16_rows["rows"]),
        "mirror_closed_row_count": sum(row["mirror_closed_flag"] for row in p16_rows["rows"]),
        "self_mirror_row_count": sum(row["self_mirror_flag"] for row in p16_rows["rows"]),
        "mirror_pair_count": len(mirror_pairs),
        "eta6_preserved_row_count": sum(row["eta6_all_preserved_flag"] for row in p16_rows["rows"]),
        "eta6_preserved_move_count": sum(row["eta6_preserved_count"] for row in p16_rows["rows"]),
        "global_delta_zero_row_count": sum(
            int(row["abs_total_f4_delta"] == 0) for row in p16_rows["rows"]
        ),
        "per_face_delta_zero_row_count": sum(
            row["per_face_delta_zero_flag"] for row in p16_rows["rows"]
        ),
        "carrier_neutral_row_count": sum(row["carrier_neutral_flag"] for row in p16_rows["rows"]),
        "balanced_222_row_count": sum(row["balanced_222_flag"] for row in p16_rows["rows"]),
        "winner_rank": winner["rank"],
        "winner_p15_id": winner["p15_id"],
        "winner_spread": winner["joint_support_spread"],
        "winner_balanced_222_flag": winner["balanced_222_flag"],
        "winner_carrier_neutral_flag": winner["carrier_neutral_flag"],
        "winner_hpol_min_margin": winner["hpol_min_margin"],
        "winner_repl_min_margin": winner["repl_min_margin"],
        "winner_margin_positive_flag": winner["carrier_margin_positive_flag"],
        "p15_screen_min_spread": int(p15_report["witness"]["grid_min_spread"]),
        "p15_unique_candidate_count": int(p15_report["witness"]["unique_candidate_count"]),
        "support_equal_top_row_count": sum(row["support_equal_flag"] for row in p16_rows["rows"]),
        "imported_hpol_min_margin": p16_rows["hpol_min"],
        "imported_repl_min_margin": p16_rows["repl_min"],
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
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p15_report.get("all_checks_pass") is True
            and gap_report.get("all_checks_pass") is True
        ),
        "top16_packet_shape_matches": (
            obs["top_row_count"],
            obs["component_move_count"],
            tuple(row_table.shape),
            tuple(obs_table.shape),
        )
        == (
            16,
            96,
            (TOP_N, len(ROW_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
        "mirror_packet_is_closed": (
            obs["mirror_closed_row_count"],
            obs["self_mirror_row_count"],
            obs["mirror_pair_count"],
        )
        == (16, 2, 7),
        "winner_is_unique_balanced_hex_neutral_row": (
            obs["balanced_222_row_count"],
            obs["winner_rank"],
            obs["winner_p15_id"],
            obs["winner_spread"],
            obs["winner_balanced_222_flag"],
            obs["winner_carrier_neutral_flag"],
        )
        == (1, 0, 58_834, 492_736, 1, 1),
        "carrier_neutral_counts_match": (
            obs["eta6_preserved_row_count"],
            obs["eta6_preserved_move_count"],
            obs["global_delta_zero_row_count"],
            obs["per_face_delta_zero_row_count"],
            obs["carrier_neutral_row_count"],
            obs["support_equal_top_row_count"],
        )
        == (16, 96, 2, 2, 2, 0),
        "imported_gap_margins_positive_for_neutral_winner": (
            obs["winner_hpol_min_margin"],
            obs["winner_repl_min_margin"],
            obs["winner_margin_positive_flag"],
            obs["imported_hpol_min_margin"],
            obs["imported_repl_min_margin"],
        )
        == (1, 146, 1, 1, 146),
        "p15_input_floor_matches": (
            obs["p15_screen_min_spread"],
            obs["p15_unique_candidate_count"],
        )
        == (492_736, 434_839),
    }
    witness = {
        "classification": "p15_top16_carrier_margin_packet",
        "candidate_construction": (
            "take the p15 top-16 screened sextuples, close them under the "
            "P0/P1 and P2/P3 mirror, and import the eta6_gap hpol/repl margins "
            "only for carrier-neutral rows"
        ),
        "p15_winner": {
            "p15_id": winner["p15_id"],
            "p5_ids": [
                winner["p5_a"],
                winner["p5_b"],
                winner["p5_c"],
                winner["p5_d"],
                winner["p5_e"],
                winner["p5_f"],
            ],
            "spread": winner["joint_support_spread"],
            "balanced_222": winner["balanced_222_flag"],
            "carrier_neutral": winner["carrier_neutral_flag"],
            "hpol_min_margin": winner["hpol_min_margin"],
            "repl_min_margin": winner["repl_min_margin"],
        },
        "mirror_packet": {
            "row_count": obs["top_row_count"],
            "mirror_closed_row_count": obs["mirror_closed_row_count"],
            "self_mirror_row_count": obs["self_mirror_row_count"],
            "mirror_pair_count": obs["mirror_pair_count"],
        },
        "carrier_neutrality": {
            "eta6_preserved_row_count": obs["eta6_preserved_row_count"],
            "global_delta_zero_row_count": obs["global_delta_zero_row_count"],
            "per_face_delta_zero_row_count": obs["per_face_delta_zero_row_count"],
            "carrier_neutral_row_count": obs["carrier_neutral_row_count"],
            "balanced_222_row_count": obs["balanced_222_row_count"],
        },
        "reading": (
            "The p15 winner is the only top-16 row with the full 2+2+2 "
            "face/mask carrier balance, zero total F-delta, and zero per-face "
            "F-delta. Because this is a carrier-neutral symbolic F-screen, the "
            "checked hpol/repl carrier margins remain the imported positive "
            "eta6_gap margins."
        ),
        "row_table_sha256": sha_array(row_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p16 = {
        "schema": "eta6.p16@1",
        "object": "eta6",
        "construction": {
            "source": "p15 top-16 rows plus eta6_gap margins",
            "test": "carrier-neutral margin packet",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p16.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P16_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Within the p15 top-16 symmetry packet, the p15 winner is the unique "
            "full 2+2+2 face/mask carrier-neutral row. Its symbolic F-screen "
            "does not alter the checked carrier row universes, so the imported "
            "eta6_gap margins remain positive: hpol margin 1 and replacement "
            "margin 146."
        ),
        "stage_protocol": {
            "draft": "start from p15 top rows and eta6_gap",
            "witness": "compute mirror partners, face/mask counts, F-delta balance, and imported margins",
            "coherence": "require the top-16 packet to be mirror-closed and the winner to be carrier-neutral",
            "closure": "certify carrier-neutral imported margin positivity for the p15 winner",
            "emit": "emit compact p16 artifacts and the next seam",
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
            "p15_tables": input_entry(P15_TABLES),
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
            "p16": relpath(OUT_DIR / "p16.json"),
            "rows_csv": relpath(OUT_DIR / "rows.csv"),
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
                "p15 top-16 packet is closed under the P0/P1, P2/P3 mirror",
                "p15 winner is the unique full 2+2+2 face/mask carrier-neutral row in that packet",
                "p15 winner has zero total and per-face F-delta over its six moves",
                "imported hpol and replacement carrier margins remain positive for the carrier-neutral p15 winner",
            ],
            "does_not_certify_because_out_of_scope": [
                "a rebuilt geometric carrier after applying the p15 winner as surgery",
                "complete six-move search over all p5 sextuples",
                "carrier neutrality for every unscreened or non-top-16 sextuple",
                "new hpol/replacement row universes beyond eta6_gap",
            ],
        },
        "next_highest_yield_item": (
            "Run p17 as a targeted full-144 companion search around the p15 "
            "winner's 2+2+2 face/mask balance class."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p16.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p16.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p16": p16,
        "rows_csv": csv_text(ROW_COLUMNS, p16_rows["rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, obs_rows),
        "row_table": row_table,
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
    write_json(OUT_DIR / "p16.json", payloads["p16"])
    (OUT_DIR / "rows.csv").write_text(payloads["rows_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        row_table=payloads["row_table"],
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
