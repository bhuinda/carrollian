from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_sixj_tetra_closure as closure
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_sixj_tetra_closure as closure
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = closure.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_NONLOCAL_FSYMBOL_CANDIDATE_SCREEN_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TETRAHEDRAL_CLOSURE_REPORT = closure.OUT_DIR / "report.json"
TETRAHEDRAL_CLOSURE_CERTIFICATE = (
    closure.OUT_DIR
    / "sixj_tetra_closure_certificate.json"
)
TETRAHEDRAL_CLOSURE_TABLES = (
    closure.OUT_DIR
    / "sixj_tetra_closure_tables.npz"
)
ASSOCIATOR_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "c985_associator_rebracketing_oracle" / "report.json"
)
PENTAGON_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "c985_pentagon_chain_normal_form" / "report.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen.py"
)

SCREEN_BLOCK_COUNT = 6

CANDIDATE_COLUMNS = [
    "candidate_id",
    "block_code",
    "occurrence_count",
    "word_count",
    "unrepaired_word_count",
    "native_repair_word_count",
    "skip_repair_word_count",
    "left_radius2_word_count",
    "right_radius2_word_count",
    "rank_min",
    "rank_max",
    "mobile_flag",
    "local_touch_flag",
    "base_promoted_flag",
    "selected_screen_flag",
    "score",
]
INTERVENTION_COLUMNS = [
    "intervention_id",
    "intervention_size",
    "block_code_a",
    "block_code_b",
    "candidate_unrepaired_word_count",
    "candidate_word_count",
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
    "local_touch_block_count": 5,
    "nonlocal_block_count": 6,
    "mobile_nonlocal_block_count": 7,
    "screen_block_count": 8,
    "screen_intervention_count": 9,
    "support_changing_intervention_count": 10,
    "best_intervention_size": 11,
    "best_block_code_a": 12,
    "best_block_code_b": 13,
    "best_state_count": 14,
    "best_edge_count": 15,
    "best_cut_edge_count": 16,
    "best_old_cut_edge_still_cut_count": 17,
    "best_lambda_2_x1e12": 18,
    "best_cut_conductance_x1e12": 19,
    "best_conductance_reduction_x1e12": 20,
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


def block_tuple_from_code(code: int) -> tuple[int, int, int, int]:
    return tuple(int(digit) for digit in f"{int(code):04d}")


def build_candidate_stats(
    records: dict[tuple[int, ...], dict[str, Any]],
    base_rows: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
) -> tuple[list[dict[str, int]], list[tuple[int, int, int, int]]]:
    local_touch_blocks = set(geometry["touch_counts"])
    base_blocks = set(pair.BASE_BLOCKS)
    base_words = set(base_rows)
    occurrence_counts: Counter[tuple[int, int, int, int]] = Counter()
    word_counts: Counter[tuple[int, int, int, int]] = Counter()
    unrepaired_word_counts: Counter[tuple[int, int, int, int]] = Counter()
    native_repair_word_counts: Counter[tuple[int, int, int, int]] = Counter()
    skip_repair_word_counts: Counter[tuple[int, int, int, int]] = Counter()
    left_radius2_word_counts: Counter[tuple[int, int, int, int]] = Counter()
    right_radius2_word_counts: Counter[tuple[int, int, int, int]] = Counter()
    ranks: dict[tuple[int, int, int, int], list[int]] = defaultdict(list)

    for word, record in records.items():
        seen: set[tuple[int, int, int, int]] = set()
        for rank, block in record["all_blocks"]:
            occurrence_counts[block] += 1
            ranks[block].append(int(rank))
            if block in seen:
                continue
            seen.add(block)
            word_counts[block] += 1
            if word not in base_words:
                unrepaired_word_counts[block] += 1
            if record["native_repair"]:
                native_repair_word_counts[block] += 1
            if record["skip_derived_repair"]:
                skip_repair_word_counts[block] += 1
            if record["left_edit_radius"] <= 2:
                left_radius2_word_counts[block] += 1
            if record["right_edit_radius"] <= 2:
                right_radius2_word_counts[block] += 1

    nonlocal_blocks = [
        block
        for block in word_counts
        if block not in local_touch_blocks and block not in base_blocks
    ]
    mobile_blocks = [
        block
        for block in nonlocal_blocks
        if min(ranks[block]) != max(ranks[block]) and max(ranks[block]) >= 3
    ]
    mobile_blocks.sort(
        key=lambda block: (
            -unrepaired_word_counts[block],
            -word_counts[block],
            -occurrence_counts[block],
            pair.block_code(block),
        )
    )
    selected_blocks = mobile_blocks[:SCREEN_BLOCK_COUNT]

    rows = []
    for candidate_id, block in enumerate(
        sorted(
            nonlocal_blocks,
            key=lambda item: (
                -int(item in selected_blocks),
                -int(item in mobile_blocks),
                -unrepaired_word_counts[item],
                -word_counts[item],
                -occurrence_counts[item],
                pair.block_code(item),
            ),
        )
    ):
        rank_min = min(ranks[block])
        rank_max = max(ranks[block])
        mobile_flag = int(block in mobile_blocks)
        score = (
            int(mobile_flag) * 10_000_000_000
            + unrepaired_word_counts[block] * 1_000_000
            + word_counts[block] * 1_000
            + occurrence_counts[block]
        )
        rows.append(
            {
                "candidate_id": candidate_id,
                "block_code": pair.block_code(block),
                "occurrence_count": occurrence_counts[block],
                "word_count": word_counts[block],
                "unrepaired_word_count": unrepaired_word_counts[block],
                "native_repair_word_count": native_repair_word_counts[block],
                "skip_repair_word_count": skip_repair_word_counts[block],
                "left_radius2_word_count": left_radius2_word_counts[block],
                "right_radius2_word_count": right_radius2_word_counts[block],
                "rank_min": rank_min,
                "rank_max": rank_max,
                "mobile_flag": mobile_flag,
                "local_touch_flag": int(block in local_touch_blocks),
                "base_promoted_flag": int(block in base_blocks),
                "selected_screen_flag": int(block in selected_blocks),
                "score": score,
            }
        )
    return rows, selected_blocks


def evaluate_intervention(
    intervention_id: int,
    blocks: tuple[tuple[int, int, int, int], ...],
    records: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
    base_conductance: int,
    candidate_row_by_code: dict[int, dict[str, int]],
) -> dict[str, int]:
    rows_by_word = pair.rows_for_blocks(records, set(pair.BASE_BLOCKS) | set(blocks))
    graph = pair.parent.build_graph(rows_by_word)
    automaton = pair.parent.build_automaton_rows(graph, geometry)
    spectral = automaton["spectral_rows"][0]
    block_codes = [pair.block_code(block) for block in blocks]
    candidate_unrepaired = sum(
        candidate_row_by_code[code]["unrepaired_word_count"] for code in block_codes
    )
    candidate_words = sum(candidate_row_by_code[code]["word_count"] for code in block_codes)
    block_b = block_codes[1] if len(block_codes) == 2 else -1
    return {
        "intervention_id": intervention_id,
        "intervention_size": len(blocks),
        "block_code_a": block_codes[0],
        "block_code_b": block_b,
        "candidate_unrepaired_word_count": candidate_unrepaired,
        "candidate_word_count": candidate_words,
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
    closure_report = load_json(TETRAHEDRAL_CLOSURE_REPORT)
    closure_certificate = load_json(TETRAHEDRAL_CLOSURE_CERTIFICATE)
    associator_report = load_json(ASSOCIATOR_REPORT)
    pentagon_report = load_json(PENTAGON_REPORT)
    geometry = pair.load_second_window_geometry()
    records = pair.precompute_closed_metric_records()
    base_rows = pair.rows_for_blocks(records, set(pair.BASE_BLOCKS))
    base_spectral = pair.parent.table_rows(
        np.asarray(
            np.load(pair.SECOND_WINDOW_PROMOTION_TABLES, allow_pickle=False)[
                "spectral_cut_table"
            ],
            dtype=np.int64,
        ),
        pair.parent.SPECTRAL_CUT_COLUMNS,
    )[0]

    candidate_rows, selected_blocks = build_candidate_stats(records, base_rows, geometry)
    candidate_row_by_code = {row["block_code"]: row for row in candidate_rows}

    interventions = [(block,) for block in selected_blocks]
    interventions.extend(tuple(blocks) for blocks in combinations(selected_blocks, 2))
    intervention_rows = [
        evaluate_intervention(
            intervention_id,
            blocks,
            records,
            geometry,
            base_spectral["cut_conductance_x1e12"],
            candidate_row_by_code,
        )
        for intervention_id, blocks in enumerate(interventions)
    ]
    best = min(
        intervention_rows,
        key=lambda row: (
            row["support_changed_flag"],
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["intervention_size"],
            row["block_code_a"],
            row["block_code_b"],
        ),
    )
    best["selected_best_flag"] = 1

    observable_values = {
        "closed_metric_word_count": len(records),
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_spectral["cut_conductance_x1e12"],
        "local_touch_block_count": len(geometry["touch_counts"]),
        "nonlocal_block_count": len(candidate_rows),
        "mobile_nonlocal_block_count": sum(row["mobile_flag"] for row in candidate_rows),
        "screen_block_count": len(selected_blocks),
        "screen_intervention_count": len(intervention_rows),
        "support_changing_intervention_count": sum(
            row["support_changed_flag"] for row in intervention_rows
        ),
        "best_intervention_size": best["intervention_size"],
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
        "closure_report": closure_report,
        "closure_certificate": closure_certificate,
        "associator_report": associator_report,
        "pentagon_report": pentagon_report,
        "candidate_rows": candidate_rows,
        "selected_blocks": selected_blocks,
        "intervention_rows": intervention_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    intervention_table = table_from_rows(
        INTERVENTION_COLUMNS,
        rows["intervention_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = next(row for row in rows["intervention_rows"] if row["selected_best_flag"])
    selected_codes = [pair.block_code(block) for block in rows["selected_blocks"]]

    checks = {
        "tetrahedral_closure_report_certified": rows["closure_report"].get("status")
        == closure.STATUS,
        "tetrahedral_closure_certificate_certified": rows["closure_certificate"].get(
            "status"
        )
        == closure.STATUS,
        "associator_oracle_certified": rows["associator_report"].get("status")
        == "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
        "pentagon_normal_form_certified": rows["pentagon_report"].get("status")
        == "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
        "candidate_scope_is_outside_cut_touch_alphabet": (
            observable_values["local_touch_block_count"],
            observable_values["nonlocal_block_count"],
            selected_codes,
        )
        == (15, 171, [1452, 4521, 2114, 1145, 5214, 5521]),
        "screen_tests_top_six_singletons_and_pairs": (
            observable_values["screen_block_count"],
            observable_values["screen_intervention_count"],
        )
        == (6, 21),
        "no_screened_nonlocal_intervention_changes_old_cut_support": observable_values[
            "support_changing_intervention_count"
        ]
        == 0,
        "best_screened_candidate_is_nonlocal_2114": (
            observable_values["best_intervention_size"],
            observable_values["best_block_code_a"],
            observable_values["best_block_code_b"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (1, 2114, -1, 945, 3_045, 6, 6, 2_645_503_000, 1_683_501_000),
        "table_shapes_match_codebooks": (
            tuple(candidate_table.shape),
            tuple(intervention_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (171, len(CANDIDATE_COLUMNS)),
            (21, len(INTERVENTION_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "selected_nonlocal_block_codes": selected_codes,
        "mobile_nonlocal_block_count": observable_values[
            "mobile_nonlocal_block_count"
        ],
        "screen_intervention_count": observable_values["screen_intervention_count"],
        "support_changing_intervention_count": observable_values[
            "support_changing_intervention_count"
        ],
        "best_intervention": best,
        "candidate_table_sha256": pair.parent.sha_array(candidate_table),
        "intervention_table_sha256": pair.parent.sha_array(intervention_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    screen = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen@1",
        "object": "C985->d20",
        "parent": TETRAHEDRAL_CLOSURE_REPORT.relative_to(ROOT).as_posix(),
        "global_coherence_inputs": {
            "associator_report": ASSOCIATOR_REPORT.relative_to(ROOT).as_posix(),
            "pentagon_report": PENTAGON_REPORT.relative_to(ROOT).as_posix(),
        },
        "search_scope": {
            "excluded_local_touch_blocks": sorted(
                pair.block_code(block) for block in pair.load_second_window_geometry()["touch_counts"]
            ),
            "selected_nonlocal_block_codes": selected_codes,
            "screen": "top six mobile nonlocal blocks by unrepaired-word coverage, tested as singletons and unordered pairs",
        },
        "summary": {
            "best_nonlocal_block_code": best["block_code_a"],
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
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_NONLOCAL_FSYMBOL_CANDIDATE_SCREEN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "After the K4-local touch alphabet is exhausted, the strongest "
            "mobile nonlocal F-symbol screen selects blocks "
            "1452,4521,2114,1145,5214,5521. Testing those as singleton and "
            "pair promotions finds 2114 as the best conductance drop, but no "
            "screened intervention moves the old six-edge aperture."
        ),
        "stage_protocol": {
            "draft": "start from the certified full tetrahedral K4-local obstruction",
            "witness": "rank nonlocal four-symbol windows outside all current cut-touch blocks",
            "coherence": "bind the screen to certified associator and pentagon normal-form reports",
            "closure": "test the selected nonlocal singleton/pair promotions against fresh spectral cuts",
            "emit": "emit candidate, intervention, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "tetrahedral_closure_report": pair.parent.input_entry(
                TETRAHEDRAL_CLOSURE_REPORT,
                {
                    "status": rows["closure_report"].get("status"),
                    "certificate_sha256": rows["closure_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "tetrahedral_closure_certificate": pair.parent.input_entry(
                TETRAHEDRAL_CLOSURE_CERTIFICATE
            ),
            "tetrahedral_closure_tables": pair.parent.input_entry(
                TETRAHEDRAL_CLOSURE_TABLES
            ),
            "associator_report": pair.parent.input_entry(
                ASSOCIATOR_REPORT,
                {
                    "status": rows["associator_report"].get("status"),
                    "certificate_sha256": rows["associator_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "pentagon_report": pair.parent.input_entry(
                PENTAGON_REPORT,
                {
                    "status": rows["pentagon_report"].get("status"),
                    "certificate_sha256": rows["pentagon_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "nonlocal_screen": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen.json"
            ),
            "candidate_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_fsymbol_candidates.csv"
            ),
            "intervention_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_fsymbol_screen_interventions.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_fsymbol_screen_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "nonlocal candidate atlas outside all current six-edge cut-touch blocks",
                "top-six mobile nonlocal F-symbol window screen by unrepaired-word coverage",
                "fresh spectral-cut test for screened singleton and pair promotions",
                "2114 is the strongest screened nonlocal conductance candidate and still preserves old six-edge support",
            ],
            "does_not_certify_because_not_required": [
                "all nonlocal singleton or pair promotions",
                "nonlocal triples or larger nonlocal closure alphabets",
                "a complete numerical C985 F-symbol table",
                "compiler integration of the screened recoupling rule",
            ],
        },
        "next_highest_yield_item": (
            "Escalate the nonlocal screen around 2114: test its focused "
            "two-hop neighborhood and mixed local/nonlocal pairs, because 2114 "
            "is the first screened candidate that beats all local conductance "
            "drops while preserving the six old cut edges."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the first nonlocal screen leaves the exhausted K4 touch alphabet",
            "2114 is the current best F-symbol-window conductance candidate",
            "screened nonlocal singleton/pair moves still do not remove the old six-edge aperture",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified tetrahedral closure obstruction",
            "load certified associator oracle and pentagon normal form",
            "rank nonlocal mobile four-symbol windows outside all cut-touch blocks",
            "test selected nonlocal singleton and pair promotions against fresh spectral cuts",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "nonlocal_screen": screen,
        "candidate_csv": pair.csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "intervention_csv": pair.csv_text(
            INTERVENTION_COLUMNS,
            rows["intervention_rows"],
        ),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "candidate_table": candidate_table,
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
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen.json",
        payloads["nonlocal_screen"],
    )
    (OUT_DIR / "sixj_nonlocal_fsymbol_candidates.csv").write_text(
        payloads["candidate_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_nonlocal_fsymbol_screen_interventions.csv").write_text(
        payloads["intervention_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_nonlocal_fsymbol_screen_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_tables.npz",
        candidate_table=payloads["candidate_table"],
        intervention_table=payloads["intervention_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_certificate.json",
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
