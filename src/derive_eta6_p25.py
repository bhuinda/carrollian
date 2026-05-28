from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p24 as p24
    from .derive_c985_fusion_multiplicity_typing import OUT_DIR as FUSION_DIR
    from .derive_c985_pentagon_chain_normal_form import OUT_DIR as PENTAGON_DIR
    from .derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p5 as p5
    import derive_eta6_p24 as p24
    from derive_c985_fusion_multiplicity_typing import OUT_DIR as FUSION_DIR
    from derive_c985_pentagon_chain_normal_form import OUT_DIR as PENTAGON_DIR
    from derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p25"
STATUS = "ETA6_P25_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P24_REPORT = p24.OUT_DIR / "report.json"
P24_TABLES = p24.OUT_DIR / "tables.npz"
REGISTRY_REPORT = REGISTRY_DIR / "report.json"
SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
FUSION_REPORT = FUSION_DIR / "report.json"
FUSION_TENSOR = FUSION_DIR / "fusion_tensor_coo.npz"
PENTAGON_REPORT = PENTAGON_DIR / "report.json"
PENTAGON_HELPER_SCRIPT = p5.DERIVE_SCRIPT

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p25.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p25.py"

EXT_COLUMNS = [
    "p25_id",
    "p24_row_id",
    "lift_id",
    "face_id",
    "label_mask",
    "order_id",
    "a",
    "b",
    "c",
    "d",
    "e",
    "omitted_label",
    "p24_delta",
    "p0_support",
    "p1_support",
    "p2_support",
    "p3_support",
    "p4_support",
    "p0_mult",
    "p1_mult",
    "p2_mult",
    "p3_mult",
    "p4_mult",
    "support_min",
    "support_max",
    "support_spread",
    "support_unique_count",
    "support_equal_flag",
    "mult_value",
    "mult_spread",
    "mult_unique_count",
    "mult_equal_flag",
    "eta6_preserved_flag",
]
FACE_COLUMNS = [
    "lift_id",
    "face_id",
    "label_mask",
    "extension_count",
    "mult_equal_count",
    "support_equal_count",
    "min_support_spread",
    "max_support_spread",
    "support_spread_sum",
    "min_mult_value",
    "max_mult_value",
    "best_p25_id",
    "best_p24_row_id",
    "best_extension_label",
    "p0_support_total",
    "p1_support_total",
    "p2_support_total",
    "p3_support_total",
    "p4_support_total",
    "p0_mult_total",
    "p1_mult_total",
    "p2_mult_total",
    "p3_mult_total",
    "p4_mult_total",
    "lift_support_row_count",
    "lift_positive_support_count",
    "lift_min_slack_x1e12",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "lift_face_count": 0,
    "p24_order_count": 1,
    "p25_extension_count": 2,
    "complement_extensions_per_order": 3,
    "mult_equal_extension_count": 4,
    "support_equal_extension_count": 5,
    "support_unique_five_count": 6,
    "eta6_preserved_extension_count": 7,
    "min_support_spread": 8,
    "max_support_spread": 9,
    "min_spread_count": 10,
    "max_spread_count": 11,
    "total_mult_p0": 12,
    "total_mult_p1": 13,
    "total_mult_p2": 14,
    "total_mult_p3": 15,
    "total_mult_p4": 16,
    "total_support_p0": 17,
    "total_support_p1": 18,
    "total_support_p2": 19,
    "total_support_p3": 20,
    "total_support_p4": 21,
    "p25_multiplicity_flag": 22,
    "p25_raw_support_obstruction_flag": 23,
    "lift_support_row_count": 24,
    "lift_support_positive_count": 25,
    "lift_min_slack_x1e12": 26,
    "p24_lifted_f_address_flag": 27,
    "new_pentagon_recompute_flag": 28,
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


def build_p25_rows() -> dict[str, Any]:
    p24_tables = np.load(P24_TABLES, allow_pickle=False)
    order_rows = rows_from_table(
        np.asarray(p24_tables["order_table"], dtype=np.int64),
        p24.ORDER_COLUMNS,
    )
    lifted_faces = rows_from_table(
        np.asarray(p24_tables["face_table"], dtype=np.int64),
        p24.FACE_COLUMNS,
    )
    face_by_lift = {row["lift_id"]: row for row in lifted_faces}
    source_target = np.load(SOURCE_TARGET, allow_pickle=False)
    triples = np.load(FUSION_TENSOR, allow_pickle=False)["triples"]
    compose = p5.build_composer(source_target, triples)

    ext_rows: list[dict[str, int]] = []
    p25_id = 0
    for row in order_rows:
        label_mask = row["label_mask"]
        complement = [
            label_id for label_id in range(6) if not ((label_mask >> label_id) & 1)
        ]
        p24_delta = row["left_support"] - row["right_support"]
        for extension_label in complement:
            omitted_label = next(
                label_id
                for label_id in range(6)
                if label_id != extension_label and not ((label_mask >> label_id) & 1)
            )
            counts = p5.pentagon_counts(
                (
                    row["a"],
                    row["b"],
                    row["c"],
                    row["d"],
                    extension_label,
                ),
                compose,
            )
            support = [count[0] for count in counts]
            mult = [count[1] for count in counts]
            ext_rows.append(
                {
                    "p25_id": p25_id,
                    "p24_row_id": row["row_id"],
                    "lift_id": row["lift_id"],
                    "face_id": row["face_id"],
                    "label_mask": label_mask,
                    "order_id": row["order_id"],
                    "a": row["a"],
                    "b": row["b"],
                    "c": row["c"],
                    "d": row["d"],
                    "e": extension_label,
                    "omitted_label": omitted_label,
                    "p24_delta": p24_delta,
                    "p0_support": support[0],
                    "p1_support": support[1],
                    "p2_support": support[2],
                    "p3_support": support[3],
                    "p4_support": support[4],
                    "p0_mult": mult[0],
                    "p1_mult": mult[1],
                    "p2_mult": mult[2],
                    "p3_mult": mult[3],
                    "p4_mult": mult[4],
                    "support_min": min(support),
                    "support_max": max(support),
                    "support_spread": max(support) - min(support),
                    "support_unique_count": len(set(support)),
                    "support_equal_flag": int(len(set(support)) == 1),
                    "mult_value": mult[0],
                    "mult_spread": max(mult) - min(mult),
                    "mult_unique_count": len(set(mult)),
                    "mult_equal_flag": int(len(set(mult)) == 1),
                    "eta6_preserved_flag": int(extension_label in complement),
                }
            )
            p25_id += 1

    face_rows = []
    for lift_id in sorted({row["lift_id"] for row in ext_rows}):
        rows = [row for row in ext_rows if row["lift_id"] == lift_id]
        face = face_by_lift[lift_id]
        best = min(rows, key=lambda row: (row["support_spread"], row["p25_id"]))
        face_rows.append(
            {
                "lift_id": lift_id,
                "face_id": rows[0]["face_id"],
                "label_mask": rows[0]["label_mask"],
                "extension_count": len(rows),
                "mult_equal_count": sum(row["mult_equal_flag"] for row in rows),
                "support_equal_count": sum(row["support_equal_flag"] for row in rows),
                "min_support_spread": min(row["support_spread"] for row in rows),
                "max_support_spread": max(row["support_spread"] for row in rows),
                "support_spread_sum": sum(row["support_spread"] for row in rows),
                "min_mult_value": min(row["mult_value"] for row in rows),
                "max_mult_value": max(row["mult_value"] for row in rows),
                "best_p25_id": best["p25_id"],
                "best_p24_row_id": best["p24_row_id"],
                "best_extension_label": best["e"],
                "p0_support_total": sum(row["p0_support"] for row in rows),
                "p1_support_total": sum(row["p1_support"] for row in rows),
                "p2_support_total": sum(row["p2_support"] for row in rows),
                "p3_support_total": sum(row["p3_support"] for row in rows),
                "p4_support_total": sum(row["p4_support"] for row in rows),
                "p0_mult_total": sum(row["p0_mult"] for row in rows),
                "p1_mult_total": sum(row["p1_mult"] for row in rows),
                "p2_mult_total": sum(row["p2_mult"] for row in rows),
                "p3_mult_total": sum(row["p3_mult"] for row in rows),
                "p4_mult_total": sum(row["p4_mult"] for row in rows),
                "lift_support_row_count": face["support_row_count"],
                "lift_positive_support_count": face["positive_support_count"],
                "lift_min_slack_x1e12": face["min_slack_x1e12"],
            }
        )

    min_spread = min(row["support_spread"] for row in ext_rows)
    max_spread = max(row["support_spread"] for row in ext_rows)
    p24_report = load_json(P24_REPORT)
    obs = {
        "lift_face_count": len(face_rows),
        "p24_order_count": len(order_rows),
        "p25_extension_count": len(ext_rows),
        "complement_extensions_per_order": len(ext_rows) // len(order_rows),
        "mult_equal_extension_count": sum(row["mult_equal_flag"] for row in ext_rows),
        "support_equal_extension_count": sum(row["support_equal_flag"] for row in ext_rows),
        "support_unique_five_count": sum(
            int(row["support_unique_count"] == 5) for row in ext_rows
        ),
        "eta6_preserved_extension_count": sum(
            row["eta6_preserved_flag"] for row in ext_rows
        ),
        "min_support_spread": min_spread,
        "max_support_spread": max_spread,
        "min_spread_count": sum(
            int(row["support_spread"] == min_spread) for row in ext_rows
        ),
        "max_spread_count": sum(
            int(row["support_spread"] == max_spread) for row in ext_rows
        ),
        "total_mult_p0": sum(row["p0_mult"] for row in ext_rows),
        "total_mult_p1": sum(row["p1_mult"] for row in ext_rows),
        "total_mult_p2": sum(row["p2_mult"] for row in ext_rows),
        "total_mult_p3": sum(row["p3_mult"] for row in ext_rows),
        "total_mult_p4": sum(row["p4_mult"] for row in ext_rows),
        "total_support_p0": sum(row["p0_support"] for row in ext_rows),
        "total_support_p1": sum(row["p1_support"] for row in ext_rows),
        "total_support_p2": sum(row["p2_support"] for row in ext_rows),
        "total_support_p3": sum(row["p3_support"] for row in ext_rows),
        "total_support_p4": sum(row["p4_support"] for row in ext_rows),
        "p25_multiplicity_flag": int(
            all(row["mult_equal_flag"] == 1 for row in ext_rows)
        ),
        "p25_raw_support_obstruction_flag": int(
            all(row["support_equal_flag"] == 0 for row in ext_rows)
            and all(row["support_unique_count"] == 5 for row in ext_rows)
        ),
        "lift_support_row_count": sum(row["lift_support_row_count"] for row in face_rows),
        "lift_support_positive_count": sum(
            row["lift_positive_support_count"] for row in face_rows
        ),
        "lift_min_slack_x1e12": min(row["lift_min_slack_x1e12"] for row in face_rows),
        "p24_lifted_f_address_flag": int(
            p24_report["witness"]["classification"]
            == "lifted_geometric_f_address_recompute"
        ),
        "new_pentagon_recompute_flag": 1,
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
        "ext_rows": ext_rows,
        "face_rows": face_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "p24_report": p24_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p25_rows()
    ext_table = table_from_rows(EXT_COLUMNS, rows["ext_rows"])
    face_table = table_from_rows(FACE_COLUMNS, rows["face_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]

    p24_report = rows["p24_report"]
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    pentagon_report = load_json(PENTAGON_REPORT)

    total_mults = [
        obs["total_mult_p0"],
        obs["total_mult_p1"],
        obs["total_mult_p2"],
        obs["total_mult_p3"],
        obs["total_mult_p4"],
    ]
    total_supports = [
        obs["total_support_p0"],
        obs["total_support_p1"],
        obs["total_support_p2"],
        obs["total_support_p3"],
        obs["total_support_p4"],
    ]
    checks = {
        "input_certificates_available": (
            p24_report.get("all_checks_pass") is True
            and registry_report.get("all_checks_pass") is True
            and fusion_report.get("all_checks_pass") is True
            and pentagon_report.get("all_checks_pass") is True
        ),
        "screen_size_is_144_lifted_extensions": (
            obs["lift_face_count"],
            obs["p24_order_count"],
            obs["p25_extension_count"],
            obs["complement_extensions_per_order"],
        )
        == (3, 72, 144, 2),
        "eta6_mask_is_preserved": (
            obs["eta6_preserved_extension_count"],
            obs["p25_extension_count"],
        )
        == (144, 144),
        "multiplicity_matches_all_five_parenthesizations": (
            obs["mult_equal_extension_count"],
            obs["p25_multiplicity_flag"],
            total_mults,
        )
        == (
            144,
            1,
            [145_542_610_944] * 5,
        ),
        "raw_support_never_matches_all_five_parenthesizations": (
            obs["support_equal_extension_count"],
            obs["support_unique_five_count"],
            obs["p25_raw_support_obstruction_flag"],
        )
        == (0, 144, 1),
        "support_totals_show_pentagon_support_imbalance": total_supports
        == [
            23_211_650_672,
            23_211_650_672,
            26_519_023_584,
            26_519_023_584,
            29_718_149_184,
        ],
        "support_spread_extrema_match": (
            obs["min_support_spread"],
            obs["min_spread_count"],
            obs["max_support_spread"],
            obs["max_spread_count"],
        )
        == (11_213_312, 2, 633_114_624, 2),
        "lifted_margin_is_imported_and_positive": (
            obs["lift_support_row_count"],
            obs["lift_support_positive_count"],
            obs["lift_min_slack_x1e12"],
        )
        == (132, 132, 363_262_450_397),
        "claim_boundary_is_explicit": (
            obs["p24_lifted_f_address_flag"],
            obs["new_pentagon_recompute_flag"],
        )
        == (1, 1),
        "table_shapes_match_codebooks": (
            tuple(ext_table.shape),
            tuple(face_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (144, len(EXT_COLUMNS)),
            (3, len(FACE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }

    best_rows = sorted(
        rows["ext_rows"],
        key=lambda row: (row["support_spread"], row["p25_id"]),
    )[:8]
    witness = {
        "classification": "lifted_face_pentagon_recompute",
        "parenthesizations": p5.PARENTHESIZATIONS,
        "lifted_face_count": obs["lift_face_count"],
        "p24_order_count": obs["p24_order_count"],
        "p25_extension_count": obs["p25_extension_count"],
        "total_multiplicity_by_parenthesization": total_mults,
        "total_support_by_parenthesization": total_supports,
        "min_support_spread": obs["min_support_spread"],
        "max_support_spread": obs["max_support_spread"],
        "min_spread_count": obs["min_spread_count"],
        "max_spread_count": obs["max_spread_count"],
        "lifted_margin": {
            "support_rows": obs["lift_support_row_count"],
            "positive_support_rows": obs["lift_support_positive_count"],
            "min_slack_x1e12": obs["lift_min_slack_x1e12"],
        },
        "claim_boundary": {
            "p24_lifted_f_address_recompute": obs["p24_lifted_f_address_flag"],
            "new_pentagon_recompute": obs["new_pentagon_recompute_flag"],
            "raw_support_equalizer_found": obs["support_equal_extension_count"],
        },
        "best_extensions": [
            {
                "p25_id": row["p25_id"],
                "p24_row_id": row["p24_row_id"],
                "lift_id": row["lift_id"],
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "order": [row["a"], row["b"], row["c"], row["d"], row["e"]],
                "p24_delta": row["p24_delta"],
                "support_spread": row["support_spread"],
                "support": [
                    row["p0_support"],
                    row["p1_support"],
                    row["p2_support"],
                    row["p3_support"],
                    row["p4_support"],
                ],
                "mult_value": row["mult_value"],
            }
            for row in best_rows
        ],
        "face_summaries": [
            {
                "lift_id": row["lift_id"],
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "extension_count": row["extension_count"],
                "min_support_spread": row["min_support_spread"],
                "max_support_spread": row["max_support_spread"],
                "best_p25_id": row["best_p25_id"],
                "support_totals": [
                    row["p0_support_total"],
                    row["p1_support_total"],
                    row["p2_support_total"],
                    row["p3_support_total"],
                    row["p4_support_total"],
                ],
                "mult_totals": [
                    row["p0_mult_total"],
                    row["p1_mult_total"],
                    row["p2_mult_total"],
                    row["p3_mult_total"],
                    row["p4_mult_total"],
                ],
            }
            for row in rows["face_rows"]
        ],
        "reading": (
            "The p24 lifted geometric F-address packet survives the pentagon "
            "window at multiplicity level. Raw support cardinality still "
            "fails to equalize on every complement-sector extension."
        ),
        "ext_table_sha256": sha_array(ext_table),
        "face_table_sha256": sha_array(face_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p25 = {
        "schema": "eta6.p25@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p24 lifted geometric F-address rows",
            "test": "lifted-face pentagon recomputation",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p25.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P25_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6_p24 lifted geometric F-address packet passes the "
            "pentagon extension screen at multiplicity level. For all 144 "
            "complement-sector extensions, all five parenthesizations have "
            "equal multiplicity. Raw support equality fails for every "
            "extension, and the least support spread is 11213312."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p24 lifted-face ordered quadruples and certified C985 pentagon normal form",
            "witness": "append each complementary H6 sector and count all five parenthesization address spaces",
            "coherence": "check multiplicity equality, support inequality, and lifted positive margin import",
            "closure": "certify lifted-face pentagon multiplicity coherence with explicit raw-support obstruction",
            "emit": "emit compact p25 artifacts and the next horizon-margin target",
        },
        "inputs": {
            "p24_report": input_entry(
                P24_REPORT,
                {
                    "status": p24_report.get("status"),
                    "certificate_sha256": p24_report.get("certificate_sha256"),
                },
            ),
            "p24_tables": input_entry(P24_TABLES),
            "typed_registry_report": input_entry(
                REGISTRY_REPORT,
                {
                    "status": registry_report.get("status"),
                    "certificate_sha256": registry_report.get("certificate_sha256"),
                },
            ),
            "source_target": input_entry(SOURCE_TARGET),
            "fusion_report": input_entry(
                FUSION_REPORT,
                {
                    "status": fusion_report.get("status"),
                    "certificate_sha256": fusion_report.get("certificate_sha256"),
                },
            ),
            "fusion_tensor": input_entry(FUSION_TENSOR),
            "pentagon_report": input_entry(
                PENTAGON_REPORT,
                {
                    "status": pentagon_report.get("status"),
                    "certificate_sha256": pentagon_report.get("certificate_sha256"),
                },
            ),
            "pentagon_helper_script": input_entry(PENTAGON_HELPER_SCRIPT),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p25": relpath(OUT_DIR / "p25.json"),
            "ext_csv": relpath(OUT_DIR / "ext.csv"),
            "face_csv": relpath(OUT_DIR / "face.csv"),
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
                "pentagon recomputation on the p24 lifted geometric F-address rows",
                "all 144 complement-sector lifted pentagon extensions preserve eta6 masks",
                "multiplicity equality across all five pentagon parenthesizations for every extension",
                "raw support equality fails for every extension",
                "the least lifted raw support spread in the pentagon screen is 11213312",
            ],
            "does_not_certify_because_false_or_open": [
                "a raw-support pentagon equalizer on the lifted carrier",
                "new simple-object semantics for the lifted geometric carrier",
                "global automaton closure after repeated geometric lifts",
                "pivotal, spherical, braided, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Start p26 by combining the eta6_gap Gordan margin, the p24 "
            "lifted-face slack, and the p25 pentagon spread floor into a "
            "single finite-horizon margin certificate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p25.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p25.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p25": p25,
        "ext_csv": csv_text(EXT_COLUMNS, rows["ext_rows"]),
        "face_csv": csv_text(FACE_COLUMNS, rows["face_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "ext_table": ext_table,
        "face_table": face_table,
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
    write_json(OUT_DIR / "p25.json", payloads["p25"])
    (OUT_DIR / "ext.csv").write_text(payloads["ext_csv"], encoding="utf-8")
    (OUT_DIR / "face.csv").write_text(payloads["face_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        ext_table=payloads["ext_table"],
        face_table=payloads["face_table"],
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
