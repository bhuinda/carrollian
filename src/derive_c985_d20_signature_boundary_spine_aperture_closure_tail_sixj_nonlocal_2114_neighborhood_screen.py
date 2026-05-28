from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen as screen
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen as screen
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = screen.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_NONLOCAL_2114_NEIGHBORHOOD_SCREEN_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

NONLOCAL_SCREEN_REPORT = screen.OUT_DIR / "report.json"
NONLOCAL_SCREEN_CERTIFICATE = (
    screen.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_certificate.json"
)
NONLOCAL_SCREEN_TABLES = (
    screen.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen.py"
)

TARGET_BLOCK = (2, 1, 1, 4)
TARGET_BLOCK_CODE = 2114

PARTNER_COLUMNS = [
    "partner_id",
    "partner_kind",
    "block_code",
    "near_occurrence_count",
    "near_word_count",
    "near_min_distance",
    "occurrence_count",
    "word_count",
    "unrepaired_word_count",
    "rank_min",
    "rank_max",
    "local_touch_flag",
    "base_promoted_flag",
]
INTERVENTION_COLUMNS = [
    "intervention_id",
    "intervention_kind",
    "block_code_a",
    "block_code_b",
    "partner_near_word_count",
    "partner_unrepaired_word_count",
    "state_count",
    "new_state_count",
    "edge_count",
    "new_edge_count",
    "cut_edge_count",
    "old_cut_edge_still_cut_count",
    "old_cut_edge_same_side_count",
    "promoted_cut_edge_count",
    "promoted_only_cut_edge_count",
    "lambda_2_x1e12",
    "cut_conductance_x1e12",
    "conductance_reduction_x1e12",
    "support_changed_flag",
    "selected_best_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "closed_metric_word_count": 0,
    "base_state_count": 1,
    "base_edge_count": 2,
    "base_cut_edge_count": 3,
    "base_cut_conductance_x1e12": 4,
    "target_block_code": 5,
    "target_word_count": 6,
    "near_nonlocal_partner_count": 7,
    "local_partner_count": 8,
    "intervention_count": 9,
    "support_changing_intervention_count": 10,
    "best_block_code_a": 11,
    "best_block_code_b": 12,
    "best_state_count": 13,
    "best_edge_count": 14,
    "best_cut_edge_count": 15,
    "best_old_cut_edge_still_cut_count": 16,
    "best_lambda_2_x1e12": 17,
    "best_cut_conductance_x1e12": 18,
    "best_conductance_reduction_x1e12": 19,
    "max_cut_edge_count": 20,
}


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def block_stats(
    records: dict[tuple[int, ...], dict[str, Any]],
    base_words: set[tuple[int, ...]],
) -> dict[str, Any]:
    occurrence_counts: Counter[tuple[int, int, int, int]] = Counter()
    word_counts: Counter[tuple[int, int, int, int]] = Counter()
    unrepaired_counts: Counter[tuple[int, int, int, int]] = Counter()
    ranks: dict[tuple[int, int, int, int], list[int]] = defaultdict(list)
    near_occurrence_counts: Counter[tuple[int, int, int, int]] = Counter()
    near_word_counts: Counter[tuple[int, int, int, int]] = Counter()
    near_min_distance: dict[tuple[int, int, int, int], int] = {}
    target_word_count = 0

    for word, record in records.items():
        target_ranks = [
            rank for rank, block in record["all_blocks"] if block == TARGET_BLOCK
        ]
        if target_ranks:
            target_word_count += 1
        seen: set[tuple[int, int, int, int]] = set()
        near_seen: set[tuple[int, int, int, int]] = set()
        for rank, block in record["all_blocks"]:
            occurrence_counts[block] += 1
            ranks[block].append(int(rank))
            if block not in seen:
                seen.add(block)
                word_counts[block] += 1
                if word not in base_words:
                    unrepaired_counts[block] += 1
            if not target_ranks or block == TARGET_BLOCK:
                continue
            distance = min(abs(int(rank) - int(target_rank)) for target_rank in target_ranks)
            if distance > 2:
                continue
            near_occurrence_counts[block] += 1
            if block not in near_seen:
                near_seen.add(block)
                near_word_counts[block] += 1
            near_min_distance[block] = min(
                near_min_distance.get(block, 99),
                distance,
            )

    return {
        "occurrence_counts": occurrence_counts,
        "word_counts": word_counts,
        "unrepaired_counts": unrepaired_counts,
        "ranks": ranks,
        "near_occurrence_counts": near_occurrence_counts,
        "near_word_counts": near_word_counts,
        "near_min_distance": near_min_distance,
        "target_word_count": target_word_count,
    }


def build_partner_rows(
    stats: dict[str, Any],
    geometry: dict[str, Any],
) -> tuple[list[dict[str, int]], list[tuple[int, int, int, int]], list[tuple[int, int, int, int]]]:
    local_touch_blocks = set(geometry["touch_counts"])
    base_blocks = set(pair.BASE_BLOCKS)
    word_counts = stats["word_counts"]
    unrepaired_counts = stats["unrepaired_counts"]
    occurrence_counts = stats["occurrence_counts"]
    ranks = stats["ranks"]
    near_occurrence_counts = stats["near_occurrence_counts"]
    near_word_counts = stats["near_word_counts"]
    near_min_distance = stats["near_min_distance"]

    mobile_nonlocal_blocks = [
        block
        for block in word_counts
        if block not in local_touch_blocks
        and block not in base_blocks
        and min(ranks[block]) != max(ranks[block])
        and max(ranks[block]) >= 3
    ]
    near_nonlocal_partners = [
        block for block in near_occurrence_counts if block in mobile_nonlocal_blocks
    ]
    near_nonlocal_partners.sort(
        key=lambda block: (
            near_min_distance[block],
            -near_word_counts[block],
            -unrepaired_counts[block],
            -word_counts[block],
            pair.block_code(block),
        )
    )
    local_partners = sorted(
        [block for block in local_touch_blocks if block not in base_blocks],
        key=lambda block: (-geometry["touch_counts"][block], pair.block_code(block)),
    )

    partner_rows: list[dict[str, int]] = []
    partner_id = 0
    for partner_kind, blocks in ((1, near_nonlocal_partners), (2, local_partners)):
        for block in blocks:
            partner_rows.append(
                {
                    "partner_id": partner_id,
                    "partner_kind": partner_kind,
                    "block_code": pair.block_code(block),
                    "near_occurrence_count": near_occurrence_counts.get(block, 0),
                    "near_word_count": near_word_counts.get(block, 0),
                    "near_min_distance": near_min_distance.get(block, -1),
                    "occurrence_count": occurrence_counts[block],
                    "word_count": word_counts[block],
                    "unrepaired_word_count": unrepaired_counts[block],
                    "rank_min": min(ranks[block]),
                    "rank_max": max(ranks[block]),
                    "local_touch_flag": int(block in local_touch_blocks),
                    "base_promoted_flag": int(block in base_blocks),
                }
            )
            partner_id += 1
    return partner_rows, near_nonlocal_partners, local_partners


def evaluate_intervention(
    intervention_id: int,
    intervention_kind: int,
    blocks: tuple[tuple[int, int, int, int], ...],
    partner_row_by_code: dict[int, dict[str, int]],
    records: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
    base_conductance: int,
) -> dict[str, int]:
    rows_by_word = pair.rows_for_blocks(records, set(pair.BASE_BLOCKS) | set(blocks))
    graph = pair.parent.build_graph(rows_by_word)
    automaton = pair.parent.build_automaton_rows(graph, geometry)
    spectral = automaton["spectral_rows"][0]
    partner_code = pair.block_code(blocks[1]) if len(blocks) == 2 else -1
    partner_row = partner_row_by_code.get(partner_code, {})
    return {
        "intervention_id": intervention_id,
        "intervention_kind": intervention_kind,
        "block_code_a": TARGET_BLOCK_CODE,
        "block_code_b": partner_code,
        "partner_near_word_count": int(partner_row.get("near_word_count", 0)),
        "partner_unrepaired_word_count": int(
            partner_row.get("unrepaired_word_count", 0)
        ),
        "state_count": len(automaton["state_rows"]),
        "new_state_count": len(automaton["state_rows"]) - geometry["state_count"],
        "edge_count": len(automaton["edge_rows"]),
        "new_edge_count": len(automaton["edge_rows"]) - geometry["edge_count"],
        "cut_edge_count": spectral["cut_edge_count"],
        "old_cut_edge_still_cut_count": spectral["old_cut_edge_still_cut_count"],
        "old_cut_edge_same_side_count": spectral["old_cut_edge_same_side_count"],
        "promoted_cut_edge_count": spectral["promoted_cut_edge_count"],
        "promoted_only_cut_edge_count": spectral["promoted_only_cut_edge_count"],
        "lambda_2_x1e12": spectral["lambda_2_x1e12"],
        "cut_conductance_x1e12": spectral["cut_conductance_x1e12"],
        "conductance_reduction_x1e12": base_conductance
        - spectral["cut_conductance_x1e12"],
        "support_changed_flag": int(
            spectral["old_cut_edge_still_cut_count"] < 6
            or spectral["old_cut_edge_same_side_count"] > 0
        ),
        "selected_best_flag": 0,
    }


def build_payload_rows() -> dict[str, Any]:
    nonlocal_report = load_json(NONLOCAL_SCREEN_REPORT)
    nonlocal_certificate = load_json(NONLOCAL_SCREEN_CERTIFICATE)
    geometry = pair.load_second_window_geometry()
    records = pair.precompute_closed_metric_records()
    base_rows = pair.rows_for_blocks(records, set(pair.BASE_BLOCKS))
    stats = block_stats(records, set(base_rows))
    partner_rows, near_nonlocal_partners, local_partners = build_partner_rows(
        stats,
        geometry,
    )
    partner_row_by_code = {row["block_code"]: row for row in partner_rows}
    base_spectral = pair.parent.table_rows(
        np.asarray(
            np.load(pair.SECOND_WINDOW_PROMOTION_TABLES, allow_pickle=False)[
                "spectral_cut_table"
            ],
            dtype=np.int64,
        ),
        pair.parent.SPECTRAL_CUT_COLUMNS,
    )[0]
    base_conductance = base_spectral["cut_conductance_x1e12"]

    interventions: list[tuple[int, tuple[tuple[int, int, int, int], ...]]] = [
        (0, (TARGET_BLOCK,))
    ]
    interventions.extend(
        (1, (TARGET_BLOCK, partner)) for partner in near_nonlocal_partners
    )
    interventions.extend((2, (TARGET_BLOCK, partner)) for partner in local_partners)

    intervention_rows = [
        evaluate_intervention(
            intervention_id,
            intervention_kind,
            blocks,
            partner_row_by_code,
            records,
            geometry,
            base_conductance,
        )
        for intervention_id, (intervention_kind, blocks) in enumerate(interventions)
    ]
    best = min(
        intervention_rows,
        key=lambda row: (
            row["support_changed_flag"],
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["intervention_kind"],
            row["block_code_b"],
        ),
    )
    best["selected_best_flag"] = 1

    observable_values = {
        "closed_metric_word_count": len(records),
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_conductance,
        "target_block_code": TARGET_BLOCK_CODE,
        "target_word_count": stats["target_word_count"],
        "near_nonlocal_partner_count": len(near_nonlocal_partners),
        "local_partner_count": len(local_partners),
        "intervention_count": len(intervention_rows),
        "support_changing_intervention_count": sum(
            row["support_changed_flag"] for row in intervention_rows
        ),
        "best_block_code_a": best["block_code_a"],
        "best_block_code_b": best["block_code_b"],
        "best_state_count": best["state_count"],
        "best_edge_count": best["edge_count"],
        "best_cut_edge_count": best["cut_edge_count"],
        "best_old_cut_edge_still_cut_count": best[
            "old_cut_edge_still_cut_count"
        ],
        "best_lambda_2_x1e12": best["lambda_2_x1e12"],
        "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
        "best_conductance_reduction_x1e12": best[
            "conductance_reduction_x1e12"
        ],
        "max_cut_edge_count": max(row["cut_edge_count"] for row in intervention_rows),
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return {
        "nonlocal_report": nonlocal_report,
        "nonlocal_certificate": nonlocal_certificate,
        "partner_rows": partner_rows,
        "near_nonlocal_partners": near_nonlocal_partners,
        "local_partners": local_partners,
        "intervention_rows": intervention_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    partner_table = table_from_rows(PARTNER_COLUMNS, rows["partner_rows"])
    intervention_table = table_from_rows(
        INTERVENTION_COLUMNS,
        rows["intervention_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = next(row for row in rows["intervention_rows"] if row["selected_best_flag"])
    near_nonlocal_codes = [pair.block_code(block) for block in rows["near_nonlocal_partners"]]
    local_partner_codes = [pair.block_code(block) for block in rows["local_partners"]]

    checks = {
        "nonlocal_screen_report_certified": rows["nonlocal_report"].get("status")
        == screen.STATUS,
        "nonlocal_screen_certificate_certified": rows["nonlocal_certificate"].get(
            "status"
        )
        == screen.STATUS,
        "target_is_nonlocal_2114": observable_values["target_block_code"] == 2114,
        "full_two_hop_and_local_partner_scope_matches": (
            observable_values["target_word_count"],
            observable_values["near_nonlocal_partner_count"],
            observable_values["local_partner_count"],
            observable_values["intervention_count"],
            near_nonlocal_codes,
            local_partner_codes,
        )
        == (
            123,
            14,
            13,
            28,
            [1145, 5211, 1143, 1144, 1211, 1452, 5521, 1431, 4521, 1445, 1521, 4121, 2521, 5221],
            [1451, 4512, 4552, 5125, 1255, 5255, 1252, 2145, 5252, 4511, 4551, 5115, 5511],
        ),
        "no_2114_neighborhood_intervention_changes_old_cut_support": observable_values[
            "support_changing_intervention_count"
        ]
        == 0,
        "best_2114_partner_is_local_5255": (
            observable_values["best_block_code_a"],
            observable_values["best_block_code_b"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_lambda_2_x1e12"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (2114, 5255, 952, 3_058, 6, 6, 1_969_615_000, 2_615_519_000, 1_713_485_000),
        "table_shapes_match_codebooks": (
            tuple(partner_table.shape),
            tuple(intervention_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (27, len(PARTNER_COLUMNS)),
            (28, len(INTERVENTION_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "target_block_code": TARGET_BLOCK_CODE,
        "near_nonlocal_partner_codes": near_nonlocal_codes,
        "local_partner_codes": local_partner_codes,
        "intervention_count": observable_values["intervention_count"],
        "support_changing_intervention_count": observable_values[
            "support_changing_intervention_count"
        ],
        "best_intervention": best,
        "partner_table_sha256": pair.parent.sha_array(partner_table),
        "intervention_table_sha256": pair.parent.sha_array(intervention_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    neighborhood_screen = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen@1",
        "object": "C985->d20",
        "parent": NONLOCAL_SCREEN_REPORT.relative_to(ROOT).as_posix(),
        "search_scope": {
            "target_block_code": TARGET_BLOCK_CODE,
            "target_singleton": True,
            "nonlocal_two_hop_partner_codes": near_nonlocal_codes,
            "mixed_local_partner_codes": local_partner_codes,
            "interventions": "target singleton, target plus every mobile nonlocal two-hop partner, and target plus every non-base local cut-touch partner",
        },
        "summary": {
            "best_block_codes": [best["block_code_a"], best["block_code_b"]],
            "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
            "best_old_cut_edge_still_cut_count": best[
                "old_cut_edge_still_cut_count"
            ],
            "support_changing_intervention_count": observable_values[
                "support_changing_intervention_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_NONLOCAL_2114_NEIGHBORHOOD_SCREEN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The focused 2114 neighborhood screen tests the 2114 singleton, "
            "all 14 mobile nonlocal two-hop partners, and all 13 mixed local "
            "cut-touch partners. The best pair is 2114+5255, which lowers "
            "conductance to 2615519000/1e12 while preserving all six old cut "
            "edges."
        ),
        "stage_protocol": {
            "draft": "start from the certified nonlocal F-symbol candidate screen",
            "witness": "materialize the full two-hop nonlocal neighborhood of 2114 and all mixed local partners",
            "coherence": "rebuild the promoted grammar and fresh spectral cut for every focused intervention",
            "closure": "certify the focused 2114 neighborhood screen and selected non-opening best pair",
            "emit": "emit partner, intervention, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "nonlocal_screen_report": pair.parent.input_entry(
                NONLOCAL_SCREEN_REPORT,
                {
                    "status": rows["nonlocal_report"].get("status"),
                    "certificate_sha256": rows["nonlocal_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "nonlocal_screen_certificate": pair.parent.input_entry(
                NONLOCAL_SCREEN_CERTIFICATE
            ),
            "nonlocal_screen_tables": pair.parent.input_entry(NONLOCAL_SCREEN_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "neighborhood_screen": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen.json"
            ),
            "partner_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_2114_neighborhood_partners.csv"
            ),
            "intervention_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_2114_neighborhood_interventions.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_2114_neighborhood_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "complete target-pair screen for 2114 against mobile nonlocal partners within two trace positions",
                "complete mixed screen for 2114 against every non-base local cut-touch block",
                "fresh spectral-cut comparison for every focused 2114 intervention",
                "2114+5255 is the best focused conductance pair and still preserves old six-edge support",
            ],
            "does_not_certify_because_not_required": [
                "non-target pairs among 2114 neighborhood partners",
                "2114 triples or larger focused nonlocal alphabets",
                "all nonlocal windows beyond the two-hop neighborhood",
                "compiler integration of the screened recoupling rule",
            ],
        },
        "next_highest_yield_item": (
            "Escalate from 2114 pairs to 2114-centered triples using the best "
            "local partner 5255 and the strongest adjacent nonlocal partner "
            "1145, because 2114+5255 is the first focused pair to improve on "
            "the 2114 singleton while still preserving the old six-edge cut."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "2114+5255 is the current best focused nonlocal/local recoupling candidate",
            "the focused 2114 neighborhood still does not remove the old six-edge aperture",
            "the next test should move from 2114 pairs to 2114-centered triples",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified nonlocal F-symbol screen",
            "materialize 2114 two-hop mobile nonlocal partners and local cut-touch partners",
            "test target singleton and target-pair interventions against fresh spectral cuts",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "neighborhood_screen": neighborhood_screen,
        "partner_csv": pair.csv_text(PARTNER_COLUMNS, rows["partner_rows"]),
        "intervention_csv": pair.csv_text(
            INTERVENTION_COLUMNS,
            rows["intervention_rows"],
        ),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "partner_table": partner_table,
        "intervention_table": intervention_table,
        "observable_table": observable_table,
        "certificate": certificate,
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen.json",
        payloads["neighborhood_screen"],
    )
    (OUT_DIR / "sixj_nonlocal_2114_neighborhood_partners.csv").write_text(
        payloads["partner_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_nonlocal_2114_neighborhood_interventions.csv").write_text(
        payloads["intervention_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_nonlocal_2114_neighborhood_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_tables.npz",
        partner_table=payloads["partner_table"],
        intervention_table=payloads["intervention_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_certificate.json",
        payloads["certificate"],
    )
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
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
