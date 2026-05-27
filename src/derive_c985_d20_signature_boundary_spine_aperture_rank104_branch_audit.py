from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        REWRITE_COMPLEX_EDGES,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        OUT_DIR as CLOSED_REPAIR_DIR,
        STATUS as CLOSED_REPAIR_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        OUT_DIR as EDIT_REPAIR_DIR,
        STATUS as EDIT_REPAIR_STATUS,
        WORD_COLUMNS as EDIT_REPAIR_WORD_COLUMNS,
        canonical_insertions,
        row_word as edit_repair_word,
        target_match_indices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        TRACE_CLASS_COLUMNS,
        OUT_DIR as TRACE_QUOTIENT_DIR,
        STATUS as TRACE_QUOTIENT_STATUS,
        bounded_atoms,
        bounded_carriers,
        bounded_edges,
        bounded_word,
        levenshtein,
        padded,
        read_csv_ints,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        REWRITE_COMPLEX_EDGES,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        OUT_DIR as CLOSED_REPAIR_DIR,
        STATUS as CLOSED_REPAIR_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        OUT_DIR as EDIT_REPAIR_DIR,
        STATUS as EDIT_REPAIR_STATUS,
        WORD_COLUMNS as EDIT_REPAIR_WORD_COLUMNS,
        canonical_insertions,
        row_word as edit_repair_word,
        target_match_indices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        TRACE_CLASS_COLUMNS,
        OUT_DIR as TRACE_QUOTIENT_DIR,
        STATUS as TRACE_QUOTIENT_STATUS,
        bounded_atoms,
        bounded_carriers,
        bounded_edges,
        bounded_word,
        levenshtein,
        padded,
        read_csv_ints,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_rank104_branch_audit"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_RANK104_BRANCH_AUDIT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TRACE_QUOTIENT_REPORT = TRACE_QUOTIENT_DIR / "report.json"
TRACE_QUOTIENT_JSON = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient.json"
)
TRACE_QUOTIENT_CLASSES = TRACE_QUOTIENT_DIR / "aperture_overhead3_trace_classes.csv"
TRACE_QUOTIENT_TABLES = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables.npz"
)
TRACE_QUOTIENT_CERTIFICATE = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate.json"
)

EDIT_REPAIR_REPORT = EDIT_REPAIR_DIR / "report.json"
EDIT_REPAIR_CANDIDATES = EDIT_REPAIR_DIR / "aperture_overhead2_edit_repair_candidates.csv"
EDIT_REPAIR_TABLES = (
    EDIT_REPAIR_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair_tables.npz"
)
EDIT_REPAIR_CERTIFICATE = (
    EDIT_REPAIR_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair_certificate.json"
)

CLOSED_REPAIR_REPORT = CLOSED_REPAIR_DIR / "report.json"
CLOSED_REPAIR_CERTIFICATE = (
    CLOSED_REPAIR_DIR
    / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit.py"
)

MAX_WORD_LENGTH = 7
MAX_PATH_LENGTH = 7
RANK104_TRACE = (48, 42, 27, 31, 50, 44)
RANK104_TARGET_WORD = (2, 1, 3, 4, 5, 2, 5)

SYMBOL_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
PATH_CARRIER_COLUMNS = [f"carrier_{index}_id" for index in range(MAX_PATH_LENGTH + 1)]
PATH_EDGE_COLUMNS = [f"cell_edge_{index}_id" for index in range(MAX_PATH_LENGTH)]
PATH_ATOM_COLUMNS = [f"selected_atom_{index}_id" for index in range(MAX_PATH_LENGTH)]

WORD_AUDIT_COLUMNS = [
    "word_audit_id",
    "word_length",
    *SYMBOL_COLUMNS,
    "bounded_candidate_count",
    "bounded_rank_min",
    "bounded_rank_max",
    "target0_levenshtein_distance",
    "target1_levenshtein_distance",
    "target0_subsequence_flag",
    "target1_subsequence_flag",
    "target0_inserted_symbol_count",
    "target1_inserted_symbol_count",
    "edit_repair_candidate_flag",
    "edit_repair_candidate_id",
    "edit_repair_target_word_id",
    "edit_repair_edit_distance",
    "edit_repair_weak_repair_flag",
    "edit_repair_strong_repair_flag",
    "edit_repair_target_consumed_before_node44_flag",
    "edit_repair_rooted_carrier_path_count",
    "closed_repair_class_match_flag",
]

TARGET_PATH_COLUMNS = [
    "target_path_id",
    "bounded_candidate_id",
    "bounded_rank_order",
    "walk_length",
    *PATH_CARRIER_COLUMNS,
    *PATH_EDGE_COLUMNS,
    *PATH_ATOM_COLUMNS,
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "rank104_candidate_count": 0,
    "rank104_distinct_word_count": 1,
    "rank104_target_language_word_count": 2,
    "rank104_target_language_candidate_count": 3,
    "rank104_non_target_candidate_count": 4,
    "rank104_weak_repair_word_count": 5,
    "rank104_strong_repair_word_count": 6,
    "rank104_closed_repair_class_match_count": 7,
    "target0_two_insertion_weak_closed_candidate_count": 8,
    "target1_target_language_word_count": 9,
    "rank104_rank_min": 10,
    "rank104_rank_max": 11,
}


def edit_repair_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def inserted_symbol_count(word: tuple[int, ...], target: tuple[int, ...]) -> int:
    return len(word) - len(target) if target_match_indices(word, target) else -1


def closed_repair_words(closed_report: dict[str, Any]) -> set[tuple[int, ...]]:
    repair_classes = closed_report.get("witness", {}).get("repair_classes", {})
    return {
        tuple(int(value) for value in row.get("symbol_word", []))
        for row in repair_classes.values()
        if isinstance(row, dict)
    }


def build_payloads() -> dict[str, Any]:
    quotient_report = load_json(TRACE_QUOTIENT_REPORT)
    quotient_json = load_json(TRACE_QUOTIENT_JSON)
    quotient_certificate = load_json(TRACE_QUOTIENT_CERTIFICATE)
    edit_report = load_json(EDIT_REPAIR_REPORT)
    edit_certificate = load_json(EDIT_REPAIR_CERTIFICATE)
    closed_report = load_json(CLOSED_REPAIR_REPORT)
    closed_certificate = load_json(CLOSED_REPAIR_CERTIFICATE)

    quotient_tables = np.load(TRACE_QUOTIENT_TABLES, allow_pickle=False)
    edit_tables = np.load(EDIT_REPAIR_TABLES, allow_pickle=False)
    bounded_tables = np.load(BOUNDED_BACKTRACK_TABLES, allow_pickle=False)
    trace_class_table = np.asarray(quotient_tables["trace_class_table"], dtype=np.int64)
    edit_candidate_table = np.asarray(edit_tables["candidate_table"], dtype=np.int64)
    bounded_candidate_table = np.asarray(
        bounded_tables["candidate_table"],
        dtype=np.int64,
    )

    bounded_rows = read_csv_ints(BOUNDED_BACKTRACK_CANDIDATES)
    edit_rows = edit_repair_rows(EDIT_REPAIR_CANDIDATES)
    edit_by_word = {edit_repair_word(row): row for row in edit_rows}
    prior_closed_words = closed_repair_words(closed_report)

    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }

    rank104_rows = []
    for row in bounded_rows:
        if int(row["trace_detour_overhead"]) != 3:
            continue
        _raw, trace_nodes, _signatures, _metrics = build_trace(
            bounded_word(row),
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        if tuple(trace_nodes) == RANK104_TRACE:
            rank104_rows.append(row)
    rank104_rows = sorted(rank104_rows, key=lambda row: int(row["rank_order"]))

    rows_by_word: dict[tuple[int, ...], list[dict[str, int]]] = {}
    for row in rank104_rows:
        rows_by_word.setdefault(bounded_word(row), []).append(row)

    word_rows: list[dict[str, int]] = []
    for word_audit_id, word in enumerate(sorted(rows_by_word)):
        rows = rows_by_word[word]
        ranks = [int(row["rank_order"]) for row in rows]
        target0 = tuple(int(value) for value in LOWER_OVERHEAD_TAIL_WORDS[0])
        target1 = tuple(int(value) for value in LOWER_OVERHEAD_TAIL_WORDS[1])
        target0_indices = target_match_indices(word, target0)
        target1_indices = target_match_indices(word, target1)
        edit_row = edit_by_word.get(word)
        word_rows.append(
            {
                "word_audit_id": word_audit_id,
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        SYMBOL_COLUMNS,
                        padded(word, MAX_WORD_LENGTH),
                    )
                },
                "bounded_candidate_count": len(rows),
                "bounded_rank_min": min(ranks),
                "bounded_rank_max": max(ranks),
                "target0_levenshtein_distance": levenshtein(word, target0),
                "target1_levenshtein_distance": levenshtein(word, target1),
                "target0_subsequence_flag": int(bool(target0_indices)),
                "target1_subsequence_flag": int(bool(target1_indices)),
                "target0_inserted_symbol_count": inserted_symbol_count(word, target0),
                "target1_inserted_symbol_count": inserted_symbol_count(word, target1),
                "edit_repair_candidate_flag": int(edit_row is not None),
                "edit_repair_candidate_id": int(edit_row["candidate_id"])
                if edit_row
                else -1,
                "edit_repair_target_word_id": int(edit_row["target_word_id"])
                if edit_row
                else -1,
                "edit_repair_edit_distance": int(edit_row["edit_distance"])
                if edit_row
                else -1,
                "edit_repair_weak_repair_flag": int(edit_row["weak_repair_flag"])
                if edit_row
                else 0,
                "edit_repair_strong_repair_flag": int(edit_row["strong_repair_flag"])
                if edit_row
                else 0,
                "edit_repair_target_consumed_before_node44_flag": int(
                    edit_row["target_consumed_before_node44_flag"]
                )
                if edit_row
                else 0,
                "edit_repair_rooted_carrier_path_count": int(
                    edit_row["rooted_carrier_path_count"]
                )
                if edit_row
                else -1,
                "closed_repair_class_match_flag": int(word in prior_closed_words),
            }
        )

    target_path_rows = []
    for row in rows_by_word.get(RANK104_TARGET_WORD, []):
        target_path_rows.append(
            {
                "target_path_id": len(target_path_rows),
                "bounded_candidate_id": int(row["walk_candidate_id"]),
                "bounded_rank_order": int(row["rank_order"]),
                "walk_length": int(row["walk_length"]),
                **{
                    column: value
                    for column, value in zip(
                        PATH_CARRIER_COLUMNS,
                        padded(bounded_carriers(row), MAX_PATH_LENGTH + 1),
                    )
                },
                **{
                    column: value
                    for column, value in zip(
                        PATH_EDGE_COLUMNS,
                        padded(bounded_edges(row), MAX_PATH_LENGTH),
                    )
                },
                **{
                    column: value
                    for column, value in zip(
                        PATH_ATOM_COLUMNS,
                        padded(bounded_atoms(row), MAX_PATH_LENGTH),
                    )
                },
            }
        )

    word_table = table_from_rows(WORD_AUDIT_COLUMNS, word_rows)
    target_path_table = table_from_rows(TARGET_PATH_COLUMNS, target_path_rows)
    target_language_rows = [
        row for row in word_rows if row["target0_subsequence_flag"] or row["target1_subsequence_flag"]
    ]
    observable_values = {
        "rank104_candidate_count": len(rank104_rows),
        "rank104_distinct_word_count": len(rows_by_word),
        "rank104_target_language_word_count": len(target_language_rows),
        "rank104_target_language_candidate_count": sum(
            row["bounded_candidate_count"] for row in target_language_rows
        ),
        "rank104_non_target_candidate_count": len(rank104_rows)
        - sum(row["bounded_candidate_count"] for row in target_language_rows),
        "rank104_weak_repair_word_count": sum(
            row["edit_repair_weak_repair_flag"] for row in word_rows
        ),
        "rank104_strong_repair_word_count": sum(
            row["edit_repair_strong_repair_flag"] for row in word_rows
        ),
        "rank104_closed_repair_class_match_count": sum(
            row["closed_repair_class_match_flag"] for row in word_rows
        ),
        "target0_two_insertion_weak_closed_candidate_count": len(target_path_rows),
        "target1_target_language_word_count": sum(
            row["target1_subsequence_flag"] for row in word_rows
        ),
        "rank104_rank_min": min(int(row["rank_order"]) for row in rank104_rows),
        "rank104_rank_max": max(int(row["rank_order"]) for row in rank104_rows),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    word_counts = Counter(bounded_word(row) for row in rank104_rows)
    target_word_row = next(row for row in word_rows if row["edit_repair_candidate_flag"])
    checks = {
        "trace_quotient_report_certified": quotient_report.get("status")
        == TRACE_QUOTIENT_STATUS,
        "trace_quotient_certificate_certified": quotient_certificate.get("status")
        == TRACE_QUOTIENT_STATUS,
        "trace_quotient_schema_available": quotient_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1",
        "edit_repair_report_certified": edit_report.get("status") == EDIT_REPAIR_STATUS,
        "edit_repair_certificate_certified": edit_certificate.get("status")
        == EDIT_REPAIR_STATUS,
        "closed_repair_report_certified": closed_report.get("status")
        == CLOSED_REPAIR_STATUS,
        "closed_repair_certificate_certified": closed_certificate.get("status")
        == CLOSED_REPAIR_STATUS,
        "trace_class_table_shape_is_7_by_codebook": tuple(trace_class_table.shape)
        == (7, len(TRACE_CLASS_COLUMNS)),
        "edit_candidate_table_shape_is_596_by_codebook": tuple(
            edit_candidate_table.shape
        )[0]
        == 596,
        "bounded_candidate_table_shape_is_1287": tuple(bounded_candidate_table.shape)[0]
        == 1287,
        "rank104_candidate_count_is_18": observable_values[
            "rank104_candidate_count"
        ]
        == 18,
        "rank104_rank_interval_is_104_to_121": observable_values["rank104_rank_min"]
        == 104
        and observable_values["rank104_rank_max"] == 121,
        "rank104_distinct_word_split_matches": word_counts
        == Counter(
            {
                (2, 1, 3, 4, 5, 2): 2,
                (2, 1, 3, 4, 5, 2, 2): 12,
                (2, 1, 3, 4, 5, 2, 5): 4,
            }
        ),
        "only_one_rank104_word_is_in_target_language": observable_values[
            "rank104_target_language_word_count"
        ]
        == 1
        and tuple(
            target_word_row[column]
            for column in SYMBOL_COLUMNS
            if target_word_row[column] >= 0
        )
        == RANK104_TARGET_WORD,
        "target_word_is_two_insertion_weak_target0": target_word_row[
            "edit_repair_target_word_id"
        ]
        == 0
        and target_word_row["edit_repair_edit_distance"] == 2
        and target_word_row["edit_repair_weak_repair_flag"] == 1,
        "target_word_is_not_strong": target_word_row[
            "edit_repair_strong_repair_flag"
        ]
        == 0
        and target_word_row["edit_repair_target_consumed_before_node44_flag"] == 0,
        "rank104_has_four_target_language_bounded_paths": observable_values[
            "target0_two_insertion_weak_closed_candidate_count"
        ]
        == 4,
        "rank104_has_no_target1_language_word": observable_values[
            "target1_target_language_word_count"
        ]
        == 0,
        "rank104_not_in_closed_repair_classes": observable_values[
            "rank104_closed_repair_class_match_count"
        ]
        == 0,
        "word_audit_table_shape_matches_codebook": tuple(word_table.shape)
        == (3, len(WORD_AUDIT_COLUMNS)),
        "target_path_table_shape_matches_codebook": tuple(target_path_table.shape)
        == (4, len(TARGET_PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "rank104_trace": list(RANK104_TRACE),
        "word_counts": {" ".join(map(str, key)): value for key, value in word_counts.items()},
        "target_language_word": list(RANK104_TARGET_WORD),
        "target_language_insertions": [
            list(row) for row in canonical_insertions(
                RANK104_TARGET_WORD,
                tuple(LOWER_OVERHEAD_TAIL_WORDS[0]),
            )
        ],
        "target_language_bounded_candidate_ids": [
            row["bounded_candidate_id"] for row in target_path_rows
        ],
        "target_language_bounded_ranks": [
            row["bounded_rank_order"] for row in target_path_rows
        ],
        "target_word_edit_repair_candidate_id": target_word_row[
            "edit_repair_candidate_id"
        ],
        "word_audit_table_sha256": sha_array(word_table),
        "target_path_table_sha256": sha_array(target_path_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    audit = {
        "schema": "c985.d20_signature_boundary_spine_aperture_rank104_branch_audit@1",
        "object": "d20",
        "audit_rule": {
            "trace_class": "48->42->27->31->50->44, rank interval 104..121 in the overhead-3 quotient",
            "target_language": "the two abstract overhead-2 target words from the symbol-state obstruction layer",
            "repair_scope": "the certified insertion-only edit-repair table through two inserted contacts",
        },
        "summary": {
            "candidate_count": observable_values["rank104_candidate_count"],
            "distinct_word_count": observable_values["rank104_distinct_word_count"],
            "target_language_word": list(RANK104_TARGET_WORD),
            "target_language_bounded_candidate_count": observable_values[
                "target0_two_insertion_weak_closed_candidate_count"
            ],
            "classification": "nonminimal weak target0 repair; not strong and not a prior closed-repair class",
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_rank104_branch_audit_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_RANK104_BRANCH_AUDIT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the rank-104 overhead-3 trace class has 18 bounded first-return candidates and three selected-symbol words",
            "four candidates use x2,x1,x3,x4,x5,x2,x5, which is a two-insertion weak repair of target0 x2,x1,x4,x2,x5",
            "that target-compatible word is not strong because node44 is reached before the final target x5 is consumed",
            "the remaining 14 rank-104 candidates do not contain either overhead-2 target word as a subsequence",
            "the branch is absent from the prior closed-repair classes because it is a nonminimal weak repair, not a new minimal or strong target repair",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_branch_audit@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The rank-104 nonbaseline valley-37 class is not a new minimal "
            "closed repair family. Its target-language part is a two-insertion "
            "weak target0 repair with four closed first-return witnesses, but "
            "node44 is reached before the final target x5 is consumed."
        ),
        "stage_protocol": {
            "draft": "isolate the rank-104 trace class from bounded overhead-3 candidates",
            "witness": "compare its selected-symbol words against the two overhead-2 targets and edit-repair table",
            "coherence": "separate non-target words from the two-insertion weak target0 repair word",
            "closure": "certify why the branch was absent from minimal closed-repair classes",
            "emit": "emit rank-104 branch audit JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "trace_quotient_report": input_entry(
                TRACE_QUOTIENT_REPORT,
                {
                    "status": quotient_report.get("status"),
                    "certificate_sha256": quotient_report.get("certificate_sha256"),
                },
            ),
            "trace_quotient_json": input_entry(TRACE_QUOTIENT_JSON),
            "trace_quotient_classes": input_entry(TRACE_QUOTIENT_CLASSES),
            "trace_quotient_tables": input_entry(TRACE_QUOTIENT_TABLES),
            "trace_quotient_certificate": input_entry(TRACE_QUOTIENT_CERTIFICATE),
            "bounded_backtrack_candidates": input_entry(BOUNDED_BACKTRACK_CANDIDATES),
            "bounded_backtrack_tables": input_entry(BOUNDED_BACKTRACK_TABLES),
            "edit_repair_report": input_entry(
                EDIT_REPAIR_REPORT,
                {
                    "status": edit_report.get("status"),
                    "certificate_sha256": edit_report.get("certificate_sha256"),
                },
            ),
            "edit_repair_candidates": input_entry(EDIT_REPAIR_CANDIDATES),
            "edit_repair_tables": input_entry(EDIT_REPAIR_TABLES),
            "edit_repair_certificate": input_entry(EDIT_REPAIR_CERTIFICATE),
            "closed_repair_report": input_entry(
                CLOSED_REPAIR_REPORT,
                {
                    "status": closed_report.get("status"),
                    "certificate_sha256": closed_report.get("certificate_sha256"),
                },
            ),
            "closed_repair_certificate": input_entry(CLOSED_REPAIR_CERTIFICATE),
            "symbolic_associativity_csv": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_rank104_branch_audit": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit.json"
            ),
            "aperture_rank104_word_audit_csv": relpath(
                OUT_DIR / "aperture_rank104_word_audit.csv"
            ),
            "aperture_rank104_target_paths_csv": relpath(
                OUT_DIR / "aperture_rank104_target_paths.csv"
            ),
            "aperture_rank104_observables_csv": relpath(
                OUT_DIR / "aperture_rank104_observables.csv"
            ),
            "signature_boundary_spine_aperture_rank104_branch_audit_tables": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit_tables.npz"
            ),
            "signature_boundary_spine_aperture_rank104_branch_audit_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_rank104_branch_audit_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected-symbol word split of the rank-104 trace class",
                "which rank-104 words lie in the overhead-2 target language",
                "that x2,x1,x3,x4,x5,x2,x5 is a two-insertion weak target0 repair with four bounded closed witnesses",
                "that the word is not a strong repair and is not one of the prior closed-repair classes",
            ],
            "does_not_certify_because_not_required": [
                "all nonminimal weak repairs outside rank-104",
                "repairs using substitutions or deletions",
                "post-node44 promotion of the weak target0 word to a strong repair",
                "walks longer than the bounded search",
            ],
        },
        "next_highest_yield_item": (
            "Enumerate all nonminimal weak closed repairs across the seven "
            "overhead-3 trace classes and compute the minimal post-node44 "
            "promotion needed to make each target-consumed/strong."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_branch_audit_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified overhead-3 trace quotient, edit-repair, and closed-repair artifacts",
            "isolate bounded first-return candidates in the rank-104 trace class",
            "compare each distinct selected-symbol word against both abstract overhead-2 targets",
            "cross-link target-language words to the certified edit-repair table",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_rank104_branch_audit": audit,
        "aperture_rank104_word_audit_csv": csv_text(WORD_AUDIT_COLUMNS, word_rows),
        "aperture_rank104_target_paths_csv": csv_text(
            TARGET_PATH_COLUMNS,
            target_path_rows,
        ),
        "aperture_rank104_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "word_audit_table": word_table,
        "target_path_table": target_path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_rank104_branch_audit_certificate": certificate,
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
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit.json",
        payloads["signature_boundary_spine_aperture_rank104_branch_audit"],
    )
    (OUT_DIR / "aperture_rank104_word_audit.csv").write_text(
        payloads["aperture_rank104_word_audit_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_rank104_target_paths.csv").write_text(
        payloads["aperture_rank104_target_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_rank104_observables.csv").write_text(
        payloads["aperture_rank104_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit_tables.npz",
        word_audit_table=payloads["word_audit_table"],
        target_path_table=payloads["target_path_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_branch_audit_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_rank104_branch_audit_certificate"
        ],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "rank104_trace": witness["rank104_trace"],
                "target_language_word": witness["target_language_word"],
                "target_language_bounded_candidate_ids": witness[
                    "target_language_bounded_candidate_ids"
                ],
                "next_highest_yield_item": payloads["report"][
                    "next_highest_yield_item"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
