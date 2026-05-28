from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from . import derive_eta6_gap as gap
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p16 as p16
    from . import derive_eta6_p20 as p20
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
    import derive_eta6_p16 as p16
    import derive_eta6_p20 as p20
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p21"
STATUS = "ETA6_P21_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_TABLES = p5.OUT_DIR / "tables.npz"
P16_REPORT = p16.OUT_DIR / "report.json"
P20_REPORT = p20.OUT_DIR / "report.json"
GAP_REPORT = gap.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p21.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p21.py"

BEST_IDS = (1, 47, 57, 79, 110, 128)
GATE_COLUMNS = [
    "gate_id",
    "p5_id",
    "face_id",
    "label_mask",
    "f4_delta",
    "eta6_preserved_flag",
    "p0_support",
    "p1_support",
    "p2_support",
    "p3_support",
    "p4_support",
    "support_spread",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "global_floor": 0,
    "global_at_floor_count": 1,
    "global_below_floor_count": 2,
    "global_equalizer_count": 3,
    "gate_move_count": 4,
    "eta6_preserved_count": 5,
    "balanced_222_flag": 6,
    "total_f4_delta": 7,
    "per_face_abs_delta_sum": 8,
    "carrier_neutral_flag": 9,
    "hpol_min_margin": 10,
    "hpol_min_count": 11,
    "repl_min_margin": 12,
    "checked_margin_positive_flag": 13,
    "rebuilt_carrier_claim_flag": 14,
    "p0_support": 15,
    "p1_support": 16,
    "p2_support": 17,
    "p3_support": 18,
    "p4_support": 19,
    "support_spread": 20,
    "joint_mult_value": 21,
    "best_p5_a": 22,
    "best_p5_b": 23,
    "best_p5_c": 24,
    "best_p5_d": 25,
    "best_p5_e": 26,
    "best_p5_f": 27,
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


def build_p21_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    p5_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    p5_by_id = {row["p5_id"]: row for row in p5_rows}
    pieces = [p5_by_id[p5_id] for p5_id in BEST_IDS]
    p16_report = load_json(P16_REPORT)
    p20_report = load_json(P20_REPORT)
    gap_report = load_json(GAP_REPORT)
    p20_witness = p20_report["witness"]
    gap_witness = gap_report["witness"]

    gate_rows = []
    supports = np.zeros(5, dtype=np.int64)
    counts = Counter()
    deltas: defaultdict[tuple[int, int], int] = defaultdict(int)
    for gate_id, row in enumerate(pieces):
        counts[(row["face_id"], row["label_mask"])] += 1
        deltas[(row["face_id"], row["label_mask"])] += row["f4_delta"]
        for index in range(5):
            supports[index] += row[f"p{index}_support"]
        gate_rows.append(
            {
                "gate_id": gate_id,
                "p5_id": row["p5_id"],
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "f4_delta": row["f4_delta"],
                "eta6_preserved_flag": row["eta6_preserved_flag"],
                "p0_support": row["p0_support"],
                "p1_support": row["p1_support"],
                "p2_support": row["p2_support"],
                "p3_support": row["p3_support"],
                "p4_support": row["p4_support"],
                "support_spread": row["support_spread"],
            }
        )

    total_delta = sum(row["f4_delta"] for row in pieces)
    per_face_abs_delta = sum(abs(value) for value in deltas.values())
    eta6_preserved_count = sum(row["eta6_preserved_flag"] for row in pieces)
    balanced = int(
        counts[(12, 30)] == 2
        and counts[(22, 45)] == 2
        and counts[(26, 51)] == 2
        and sum(counts.values()) == 6
    )
    carrier_neutral = int(
        eta6_preserved_count == 6
        and balanced == 1
        and total_delta == 0
        and per_face_abs_delta == 0
    )
    hpol_margin = int(gap_witness["hpol"]["min_margin"])
    repl_margin = int(gap_witness["repl"]["min_margin"])
    obs = {
        "global_floor": int(p20_witness["global_min_spread"]),
        "global_at_floor_count": int(p20_witness["global_at_min_count"]),
        "global_below_floor_count": int(p20_witness["global_below_min_count"]),
        "global_equalizer_count": int(p20_witness["global_support_equal_count"]),
        "gate_move_count": len(gate_rows),
        "eta6_preserved_count": eta6_preserved_count,
        "balanced_222_flag": balanced,
        "total_f4_delta": total_delta,
        "per_face_abs_delta_sum": per_face_abs_delta,
        "carrier_neutral_flag": carrier_neutral,
        "hpol_min_margin": hpol_margin,
        "hpol_min_count": int(gap_witness["hpol"]["min_margin_count"]),
        "repl_min_margin": repl_margin,
        "checked_margin_positive_flag": int(carrier_neutral and hpol_margin > 0 and repl_margin > 0),
        "rebuilt_carrier_claim_flag": 0,
        "p0_support": int(supports[0]),
        "p1_support": int(supports[1]),
        "p2_support": int(supports[2]),
        "p3_support": int(supports[3]),
        "p4_support": int(supports[4]),
        "support_spread": int(supports.max() - supports.min()),
        "joint_mult_value": sum(row["mult_value"] for row in pieces),
        "best_p5_a": BEST_IDS[0],
        "best_p5_b": BEST_IDS[1],
        "best_p5_c": BEST_IDS[2],
        "best_p5_d": BEST_IDS[3],
        "best_p5_e": BEST_IDS[4],
        "best_p5_f": BEST_IDS[5],
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
        "gate_rows": gate_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "p16_report": p16_report,
        "p20_report": p20_report,
        "gap_report": gap_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p21_rows()
    gate_table = table_from_rows(GATE_COLUMNS, rows["gate_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p16_report = rows["p16_report"]
    p20_report = rows["p20_report"]
    gap_report = rows["gap_report"]
    checks = {
        "input_certificates_available": (
            p16_report.get("all_checks_pass") is True
            and p20_report.get("all_checks_pass") is True
            and gap_report.get("all_checks_pass") is True
        ),
        "exact_floor_gate_matches_p20": (
            obs["global_floor"],
            obs["global_at_floor_count"],
            obs["global_below_floor_count"],
            obs["global_equalizer_count"],
            tuple(p20_report["witness"]["best_p5_ids"]),
        )
        == (492_736, 1, 0, 0, BEST_IDS),
        "gate_component_shape_matches": (
            obs["gate_move_count"],
            obs["eta6_preserved_count"],
            obs["balanced_222_flag"],
            tuple(gate_table.shape),
        )
        == (6, 6, 1, (6, len(GATE_COLUMNS))),
        "gate_neutrality_matches_p16": (
            obs["total_f4_delta"],
            obs["per_face_abs_delta_sum"],
            obs["carrier_neutral_flag"],
            p16_report["witness"]["p15_winner"]["carrier_neutral"],
        )
        == (0, 0, 1, 1),
        "checked_margins_are_positive": (
            obs["hpol_min_margin"],
            obs["hpol_min_count"],
            obs["repl_min_margin"],
            obs["checked_margin_positive_flag"],
        )
        == (1, 2, 146, 1),
        "support_vector_matches_exact_floor": (
            obs["p0_support"],
            obs["p1_support"],
            obs["p2_support"],
            obs["p3_support"],
            obs["p4_support"],
            obs["support_spread"],
        )
        == (1_083_830_080, 1_083_830_080, 1_084_205_056, 1_084_205_056, 1_084_322_816, 492_736),
        "claim_boundary_is_explicit": obs["rebuilt_carrier_claim_flag"] == 0,
        "table_shapes_match_codebooks": tuple(obs_table.shape)
        == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "classification": "exact_floor_surgery_gate",
        "gate_p5_ids": list(BEST_IDS),
        "global_floor": obs["global_floor"],
        "global_at_floor_count": obs["global_at_floor_count"],
        "global_below_floor_count": obs["global_below_floor_count"],
        "global_equalizer_count": obs["global_equalizer_count"],
        "support": [
            obs["p0_support"],
            obs["p1_support"],
            obs["p2_support"],
            obs["p3_support"],
            obs["p4_support"],
        ],
        "carrier": {
            "balanced_222": obs["balanced_222_flag"],
            "eta6_preserved_count": obs["eta6_preserved_count"],
            "total_f4_delta": obs["total_f4_delta"],
            "per_face_abs_delta_sum": obs["per_face_abs_delta_sum"],
            "carrier_neutral": obs["carrier_neutral_flag"],
        },
        "checked_margins": {
            "hpol_min_margin": obs["hpol_min_margin"],
            "hpol_min_count": obs["hpol_min_count"],
            "repl_min_margin": obs["repl_min_margin"],
            "positive": obs["checked_margin_positive_flag"],
            "rebuilt_carrier_claim": obs["rebuilt_carrier_claim_flag"],
        },
        "reading": (
            "The exact six-move floor is now promoted to a surgery gate: it is "
            "globally optimal among p5 sextuples, carrier-neutral in the p16 "
            "sense, and backed by positive checked hpol/repl margins. The "
            "rebuilt post-surgery carrier remains the next seam."
        ),
        "gate_table_sha256": sha_array(gate_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p21 = {
        "schema": "eta6.p21@1",
        "object": "eta6",
        "construction": {
            "source": "p20 exact floor, p16 carrier neutrality, eta6_gap margins",
            "test": "surgery gate readiness packet",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p21.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P21_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The exact p15 floor [1,47,57,79,110,128] is certified as the "
            "current six-move surgery gate: it is the unique global p5 "
            "six-move minimizer at spread 492,736, it is carrier-neutral, and "
            "the checked hpol/replacement margins remain positive at 1 and "
            "146. This is a gate-readiness certificate, not a rebuilt-carrier "
            "certificate."
        ),
        "stage_protocol": {
            "draft": "start from p20, p16, and eta6_gap",
            "witness": "extract the exact floor gate and its six component p5 rows",
            "coherence": "match global optimality, carrier neutrality, and positive checked margins",
            "closure": "certify the exact p15 floor as the current surgery gate",
            "emit": "emit compact p21 artifacts and the rebuilt-carrier seam",
        },
        "inputs": {
            "p5_tables": input_entry(P5_TABLES),
            "p16_report": input_entry(
                P16_REPORT,
                {
                    "status": p16_report.get("status"),
                    "certificate_sha256": p16_report.get("certificate_sha256"),
                },
            ),
            "p20_report": input_entry(
                P20_REPORT,
                {
                    "status": p20_report.get("status"),
                    "certificate_sha256": p20_report.get("certificate_sha256"),
                },
            ),
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
            "p21": relpath(OUT_DIR / "p21.json"),
            "gate_csv": relpath(OUT_DIR / "gate.csv"),
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
                "exact p15 floor promoted to current six-move surgery gate",
                "gate is unique global p5 six-move minimizer at spread 492736",
                "gate is carrier-neutral in the p16 face/mask and F-delta sense",
                "checked hpol and replacement margins remain positive for the neutral gate",
            ],
            "does_not_certify_because_out_of_scope": [
                "post-surgery rebuilt carrier row universe",
                "post-surgery C985 associator or pentagon recomputation",
                "seven-or-more p5 move searches",
                "new hpol/replacement row universes beyond eta6_gap",
            ],
        },
        "next_highest_yield_item": (
            "Start p22 by rebuilding the carrier induced by the p21 surgery gate "
            "and streaming its hpol/replacement margins."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p21.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p21.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p21": p21,
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "gate_table": gate_table,
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
    write_json(OUT_DIR / "p21.json", payloads["p21"])
    (OUT_DIR / "gate.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        gate_table=payloads["gate_table"],
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
