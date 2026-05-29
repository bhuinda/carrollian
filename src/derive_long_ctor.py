from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import h_file, raw_tensor_relpath
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from certify_io import h_file, raw_tensor_relpath
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


THEOREM_ID = "long_ctor"
STATUS = "LONG_CTOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_ORAC_REPORT = PROOF_ROOT / "long_orac" / "report.json"

RAW_TENSOR = ROOT / raw_tensor_relpath()
RAW_RELATIONS = ROOT / "data" / "raw" / "relation_memberships.npz"
RAW_QUOTIENTS = ROOT / "data" / "raw" / "quotients.npz"
STRICT_TENSOR = ROOT / "generated" / "strict_scratch_tensor_from_pre_a985.npz"
STRICT_RELATIONS = (
    ROOT / "generated" / "relation_memberships_pre_A985_from_source_aligned.npz"
)
STRICT_QUOTIENTS = (
    ROOT / "generated" / "strict_scratch_terminal_quotients_from_dihedral_formula.npz"
)
FORMULA_JSON = ROOT / "data" / "coorient" / "lifted_coorient_canonical_marker_formula.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_ctor.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_ctor.py"

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "certified_flag",
    "constructor_input_flag",
    "audit_target_flag",
    "exact_replay_flag",
    "remaining_boundary_count",
]
HASH_COLUMNS = [
    "hash_id",
    "hash_code",
    "artifact",
    "sha256",
    "matches_reference_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "surface_row_count",
    "hash_row_count",
    "strict_scratch_passed_flag",
    "full_scratch_object_constructor_flag",
    "constructs_from_supplied_raw_seeds_flag",
    "seed_boundary_file_count",
    "audit_target_file_count",
    "completed_full_scratch_step_count",
    "missing_full_scratch_step_count",
    "remaining_boundary_count",
    "points",
    "relations",
    "ordered_pair_partition_size",
    "object_count",
    "tensor_support",
    "tensor_coefficient_total",
    "raw_cache_file_bytes",
    "raw_array_uncompressed_bytes",
    "stored_raw_triples_order_matches_generated_flag",
    "canonical_tensor_multiset_matches_flag",
    "raw_tensor_reps_match_generated_reps_flag",
    "relation_partition_matches_flag",
    "terminal_q42_map_matches_flag",
    "terminal_q12_map_matches_flag",
    "terminal_q42_tensor_matches_flag",
    "terminal_q12_tensor_matches_flag",
    "long_orac_certified_flag",
    "oracle_input_report_count",
    "oracle_resolved_surface_count",
    "oracle_open_boundary_count",
    "coorient_formula_seed_integer_count",
    "coorient_full_generator_integer_count",
    "coorient_generator_compression_ratio_x1000",
    "cache_disposable_as_semantic_input_flag",
    "exact_npz_byte_reproduction_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

SURFACE_CODE_MAP = {
    "0": "strict_scratch_constructor",
    "1": "source_to_relation_body",
    "2": "coorient_formula_generators",
    "3": "absolute_word_presentation",
    "4": "relation_partition",
    "5": "a985_tensor_canonical_multiset",
    "6": "terminal_q42_q12_oracle",
    "7": "center_idempotents",
    "8": "native_a236_formulae",
    "9": "a236_branching_boundary",
    "10": "a236_profunctor",
    "11": "long_orac_status_split",
}
HASH_CODE_MAP = {
    "0": "raw_stored_triples",
    "1": "raw_canonical_sorted_triples",
    "2": "strict_canonical_sorted_triples",
    "3": "raw_object_pair_matrix",
    "4": "strict_object_pair_matrix",
    "5": "raw_reps",
    "6": "strict_reps",
    "7": "raw_relation_encoded_pairs",
    "8": "strict_relation_encoded_pairs",
    "9": "raw_relation_offsets",
    "10": "strict_relation_offsets",
    "11": "raw_relation_object_of_point",
    "12": "strict_relation_object_of_point",
    "13": "raw_q42_map",
    "14": "strict_q42_map",
    "15": "raw_q12_map",
    "16": "strict_q12_map",
    "17": "raw_q42_tensor",
    "18": "strict_q42_tensor",
    "19": "raw_q12_tensor",
    "20": "strict_q12_tensor",
    "21": "strict_constructor_result",
    "22": "long_orac_certificate",
}


def sorted_triples_sha(path: Path) -> str:
    z = np.load(path, allow_pickle=False)
    triples = np.asarray(z["triples"], dtype=np.int32)
    order = np.lexsort((triples[:, 3], triples[:, 2], triples[:, 1], triples[:, 0]))
    return sha_array(triples[order])


def tensor_arrays(path: Path) -> dict[str, np.ndarray]:
    z = np.load(path, allow_pickle=False)
    return {
        "triples": np.asarray(z["triples"], dtype=np.int32),
        "M": np.asarray(z["M"], dtype=np.int64),
        "reps": np.asarray(z["reps"], dtype=np.int32),
    }


def relation_arrays(path: Path) -> dict[str, np.ndarray]:
    z = np.load(path, allow_pickle=False)
    return {
        "encoded_pairs": np.asarray(z["encoded_pairs"], dtype=np.int64),
        "offsets": np.asarray(z["offsets"], dtype=np.int64),
        "object_of_point": np.asarray(z["object_of_point"], dtype=np.int16),
        "block_i": np.asarray(z["block_i"], dtype=np.int16),
        "block_j": np.asarray(z["block_j"], dtype=np.int16),
    }


def quotient_arrays(path: Path) -> dict[str, np.ndarray]:
    z = np.load(path, allow_pickle=False)
    return {
        "q42_map": np.asarray(z["q42_map"], dtype=np.int16),
        "q12_map": np.asarray(z["q12_map"], dtype=np.int16),
        "q42_tensor": np.asarray(z["q42_tensor"], dtype=np.int64),
        "q12_tensor": np.asarray(z["q12_tensor"], dtype=np.int64),
    }


def raw_uncompressed_bytes() -> int:
    raw = tensor_arrays(RAW_TENSOR)
    return int(sum(array.nbytes for array in raw.values()))


def npz_array_entry(path: Path, arrays: dict[str, np.ndarray]) -> dict[str, Any]:
    return {
        "path": relpath(path),
        "array_sha256": {name: sha_array(array) for name, array in arrays.items()},
    }


def load_constructor_witness() -> dict[str, Any]:
    from src.commands.construct import construct_from_generated_strict_scratch_pipeline

    return construct_from_generated_strict_scratch_pipeline()


def build_rows() -> dict[str, Any]:
    witness = load_constructor_witness()
    long_orac = load_json(LONG_ORAC_REPORT)
    raw_tensor = tensor_arrays(RAW_TENSOR)
    strict_tensor = tensor_arrays(STRICT_TENSOR)
    raw_relation = relation_arrays(RAW_RELATIONS)
    strict_relation = relation_arrays(STRICT_RELATIONS)
    raw_quotient = quotient_arrays(RAW_QUOTIENTS)
    strict_quotient = quotient_arrays(STRICT_QUOTIENTS)

    raw_sorted_sha = sorted_triples_sha(RAW_TENSOR)
    strict_sorted_sha = sorted_triples_sha(STRICT_TENSOR)
    stored_raw_triples_sha = sha_array(raw_tensor["triples"])
    stored_strict_triples_sha = sha_array(strict_tensor["triples"])
    relation_matches = all(
        np.array_equal(raw_relation[name], strict_relation[name])
        for name in ["encoded_pairs", "offsets", "object_of_point", "block_i", "block_j"]
    )
    q42_map_matches = np.array_equal(raw_quotient["q42_map"], strict_quotient["q42_map"])
    q12_map_matches = np.array_equal(raw_quotient["q12_map"], strict_quotient["q12_map"])
    q42_tensor_matches = np.array_equal(
        raw_quotient["q42_tensor"], strict_quotient["q42_tensor"]
    )
    q12_tensor_matches = np.array_equal(
        raw_quotient["q12_tensor"], strict_quotient["q12_tensor"]
    )
    long_orac_witness = long_orac.get("witness", {})
    long_orac_summary = long_orac_witness.get("summary", {})
    formula = witness.get("coorient", {})
    generator_report = load_json(ROOT / "generated" / "strict_scratch_lifted_coorient_generators_report.json")
    formula_info = generator_report.get("formula", {})

    surfaces = [
        {
            "surface_id": 0,
            "surface_code": 0,
            "certified_flag": int(
                witness.get("constructor_status")
                == "GENERATED_STRICT_SCRATCH_CONSTRUCTOR_PASS"
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": int(witness.get("strict_scratch_passed") is True),
            "remaining_boundary_count": len(witness.get("remaining_boundary", [])),
        },
        {
            "surface_id": 1,
            "surface_code": 1,
            "certified_flag": int(
                witness.get("checks", {}).get("pre_A985_relation_body_pass") is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 2,
            "surface_code": 2,
            "certified_flag": int(
                witness.get("checks", {}).get("formula_generators_pass") is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 3,
            "surface_code": 3,
            "certified_flag": int(
                witness.get("checks", {}).get("absolute_word_presentation_pass") is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 4,
            "surface_code": 4,
            "certified_flag": int(relation_matches),
            "constructor_input_flag": 0,
            "audit_target_flag": 1,
            "exact_replay_flag": int(relation_matches),
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 5,
            "surface_code": 5,
            "certified_flag": int(raw_sorted_sha == strict_sorted_sha),
            "constructor_input_flag": 0,
            "audit_target_flag": 1,
            "exact_replay_flag": int(raw_sorted_sha == strict_sorted_sha),
            "remaining_boundary_count": 1,
        },
        {
            "surface_id": 6,
            "surface_code": 6,
            "certified_flag": int(
                q42_map_matches
                and q12_map_matches
                and q42_tensor_matches
                and q12_tensor_matches
            ),
            "constructor_input_flag": 0,
            "audit_target_flag": 1,
            "exact_replay_flag": int(
                q42_map_matches
                and q12_map_matches
                and q42_tensor_matches
                and q12_tensor_matches
            ),
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 7,
            "surface_code": 7,
            "certified_flag": int(
                witness.get("checks", {}).get("center_idempotents_pass") is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 8,
            "surface_code": 8,
            "certified_flag": int(
                witness.get("checks", {}).get("native_a236_formulae_pass") is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": 0,
        },
        {
            "surface_id": 9,
            "surface_code": 9,
            "certified_flag": int(
                witness.get("checks", {}).get("a236_generated_branching_boundary_pass")
                is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": len(
                witness.get("readouts", {}).get(
                    "a236_generated_branching_remaining_boundary", []
                )
                or []
            ),
        },
        {
            "surface_id": 10,
            "surface_code": 10,
            "certified_flag": int(
                witness.get("checks", {}).get("a236_profunctor_from_tube_cache_pass")
                is True
            ),
            "constructor_input_flag": 1,
            "audit_target_flag": 0,
            "exact_replay_flag": 1,
            "remaining_boundary_count": len(
                witness.get("readouts", {}).get("a236_profunctor_remaining_boundary", [])
                or []
            ),
        },
        {
            "surface_id": 11,
            "surface_code": 11,
            "certified_flag": int(
                long_orac.get("status") == "LONG_ORAC_CERTIFIED"
                and long_orac.get("all_checks_pass") is True
            ),
            "constructor_input_flag": 0,
            "audit_target_flag": 1,
            "exact_replay_flag": int(
                long_orac.get("status") == "LONG_ORAC_CERTIFIED"
                and long_orac.get("all_checks_pass") is True
            ),
            "remaining_boundary_count": int(
                long_orac_summary.get("open_boundary_count", 0)
            ),
        },
    ]

    hash_items = [
        ("raw tensor stored triples", 0, stored_raw_triples_sha, 0),
        ("raw tensor canonical sorted triples", 1, raw_sorted_sha, 1),
        ("strict tensor canonical sorted triples", 2, strict_sorted_sha, int(raw_sorted_sha == strict_sorted_sha)),
        ("raw tensor object-pair matrix", 3, sha_array(raw_tensor["M"]), 1),
        ("strict tensor object-pair matrix", 4, sha_array(strict_tensor["M"]), int(np.array_equal(raw_tensor["M"], strict_tensor["M"]))),
        ("raw tensor reps", 5, sha_array(raw_tensor["reps"]), 1),
        ("strict tensor reps", 6, sha_array(strict_tensor["reps"]), int(np.array_equal(raw_tensor["reps"], strict_tensor["reps"]))),
        ("raw relation encoded pairs", 7, sha_array(raw_relation["encoded_pairs"]), 1),
        ("strict relation encoded pairs", 8, sha_array(strict_relation["encoded_pairs"]), int(np.array_equal(raw_relation["encoded_pairs"], strict_relation["encoded_pairs"]))),
        ("raw relation offsets", 9, sha_array(raw_relation["offsets"]), 1),
        ("strict relation offsets", 10, sha_array(strict_relation["offsets"]), int(np.array_equal(raw_relation["offsets"], strict_relation["offsets"]))),
        ("raw relation object_of_point", 11, sha_array(raw_relation["object_of_point"]), 1),
        ("strict relation object_of_point", 12, sha_array(strict_relation["object_of_point"]), int(np.array_equal(raw_relation["object_of_point"], strict_relation["object_of_point"]))),
        ("raw q42 map", 13, sha_array(raw_quotient["q42_map"]), 1),
        ("strict q42 map", 14, sha_array(strict_quotient["q42_map"]), int(q42_map_matches)),
        ("raw q12 map", 15, sha_array(raw_quotient["q12_map"]), 1),
        ("strict q12 map", 16, sha_array(strict_quotient["q12_map"]), int(q12_map_matches)),
        ("raw q42 tensor", 17, sha_array(raw_quotient["q42_tensor"]), 1),
        ("strict q42 tensor", 18, sha_array(strict_quotient["q42_tensor"]), int(q42_tensor_matches)),
        ("raw q12 tensor", 19, sha_array(raw_quotient["q12_tensor"]), 1),
        ("strict q12 tensor", 20, sha_array(strict_quotient["q12_tensor"]), int(q12_tensor_matches)),
        ("strict constructor result", 21, witness.get("constructor_result_sha256", ""), 1),
        ("long_orac certificate", 22, long_orac.get("certificate_sha256", ""), 1),
    ]
    hash_rows = [
        {
            "hash_id": index,
            "hash_code": code,
            "artifact": artifact,
            "sha256": digest,
            "matches_reference_flag": match,
        }
        for index, (artifact, code, digest, match) in enumerate(hash_items)
    ]

    obs = {
        "surface_row_count": len(surfaces),
        "hash_row_count": len(hash_rows),
        "strict_scratch_passed_flag": int(witness.get("strict_scratch_passed") is True),
        "full_scratch_object_constructor_flag": int(
            witness.get("full_scratch_object_constructor") is True
        ),
        "constructs_from_supplied_raw_seeds_flag": int(
            witness.get("constructs_from_supplied_raw_seeds") is True
        ),
        "seed_boundary_file_count": len(witness.get("seed_boundary", [])),
        "audit_target_file_count": len(witness.get("audit_targets_not_constructor_inputs", [])),
        "completed_full_scratch_step_count": len(
            witness.get("completed_full_scratch_steps", [])
        ),
        "missing_full_scratch_step_count": len(
            witness.get("missing_full_scratch_steps", [])
        ),
        "remaining_boundary_count": len(witness.get("remaining_boundary", [])),
        "points": int(witness.get("finite_object", {}).get("points", 0)),
        "relations": int(witness.get("finite_object", {}).get("relations", 0)),
        "ordered_pair_partition_size": int(
            witness.get("finite_object", {}).get("ordered_pair_partition_size", 0)
        ),
        "object_count": len(witness.get("finite_object", {}).get("object_sizes", [])),
        "tensor_support": int(
            witness.get("tensor", {}).get("report", {}).get("tensor_support", 0)
        ),
        "tensor_coefficient_total": int(
            witness.get("tensor", {}).get("report", {}).get("coefficient_total", 0)
        ),
        "raw_cache_file_bytes": RAW_TENSOR.stat().st_size,
        "raw_array_uncompressed_bytes": raw_uncompressed_bytes(),
        "stored_raw_triples_order_matches_generated_flag": int(
            stored_raw_triples_sha == stored_strict_triples_sha
        ),
        "canonical_tensor_multiset_matches_flag": int(raw_sorted_sha == strict_sorted_sha),
        "raw_tensor_reps_match_generated_reps_flag": int(
            np.array_equal(raw_tensor["reps"], strict_tensor["reps"])
        ),
        "relation_partition_matches_flag": int(relation_matches),
        "terminal_q42_map_matches_flag": int(q42_map_matches),
        "terminal_q12_map_matches_flag": int(q12_map_matches),
        "terminal_q42_tensor_matches_flag": int(q42_tensor_matches),
        "terminal_q12_tensor_matches_flag": int(q12_tensor_matches),
        "long_orac_certified_flag": int(
            long_orac.get("status") == "LONG_ORAC_CERTIFIED"
            and long_orac.get("all_checks_pass") is True
        ),
        "oracle_input_report_count": int(long_orac_summary.get("input_report_count", 0)),
        "oracle_resolved_surface_count": int(
            long_orac_summary.get("resolved_surface_count", 0)
        ),
        "oracle_open_boundary_count": int(
            long_orac_summary.get("open_boundary_count", 0)
        ),
        "coorient_formula_seed_integer_count": int(
            formula_info.get("seed_size_integers", 0)
        ),
        "coorient_full_generator_integer_count": int(
            formula_info.get("full_seed_size_integers", 0)
        ),
        "coorient_generator_compression_ratio_x1000": int(
            round(float(formula_info.get("compression_ratio", 0.0)) * 1000)
        ),
        "cache_disposable_as_semantic_input_flag": int(
            witness.get("constructs_from_supplied_raw_seeds") is False
            and raw_sorted_sha == strict_sorted_sha
            and q42_map_matches
            and q12_map_matches
            and q42_tensor_matches
            and q12_tensor_matches
        ),
        "exact_npz_byte_reproduction_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "witness": witness,
        "long_orac": long_orac,
        "surface_rows": surfaces,
        "hash_rows": hash_rows,
        "obs_rows": obs_rows,
        "obs": obs,
        "surface_table": table_from_rows(SURFACE_COLUMNS, surfaces),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    witness = rows["witness"]
    long_orac = rows["long_orac"]
    checks = {
        "strict_constructor_passes": (
            obs["strict_scratch_passed_flag"],
            obs["full_scratch_object_constructor_flag"],
            obs["constructs_from_supplied_raw_seeds_flag"],
            obs["seed_boundary_file_count"],
            obs["missing_full_scratch_step_count"],
            obs["remaining_boundary_count"],
        )
        == (1, 1, 0, 0, 0, 0),
        "finite_object_shape_matches": (
            obs["points"],
            obs["relations"],
            obs["ordered_pair_partition_size"],
            obs["object_count"],
        )
        == (2576, 985, 6_635_776, 6),
        "tensor_replay_matches": (
            obs["tensor_support"],
            obs["tensor_coefficient_total"],
            obs["canonical_tensor_multiset_matches_flag"],
        )
        == (1_414_965, 2_537_360, 1),
        "cache_boundary_not_overclaimed": (
            obs["stored_raw_triples_order_matches_generated_flag"],
            obs["raw_tensor_reps_match_generated_reps_flag"],
            obs["exact_npz_byte_reproduction_claim_flag"],
        )
        == (0, 0, 0),
        "relation_partition_replay_matches": obs["relation_partition_matches_flag"] == 1,
        "terminal_oracle_replay_matches": (
            obs["terminal_q42_map_matches_flag"],
            obs["terminal_q12_map_matches_flag"],
            obs["terminal_q42_tensor_matches_flag"],
            obs["terminal_q12_tensor_matches_flag"],
        )
        == (1, 1, 1, 1),
        "oracle_certificate_is_current": (
            obs["long_orac_certified_flag"],
            obs["oracle_input_report_count"],
            obs["oracle_resolved_surface_count"],
            obs["oracle_open_boundary_count"],
        )
        == (1, 31, 29, 22),
        "formula_compression_recorded": (
            obs["coorient_formula_seed_integer_count"],
            obs["coorient_full_generator_integer_count"],
            obs["coorient_generator_compression_ratio_x1000"],
        )
        == (12, 7728, 644000),
        "cache_demoted_to_audit_target": (
            obs["cache_disposable_as_semantic_input_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
        "surface_rows_all_certified": all(
            row["certified_flag"] == 1 for row in rows["surface_rows"]
        ),
        "hash_references_cover_expected_mismatches": (
            [row["matches_reference_flag"] for row in rows["hash_rows"] if row["hash_code"] in (0, 6)]
            == [0, 0]
            and all(
                row["matches_reference_flag"] == 1
                for row in rows["hash_rows"]
                if row["hash_code"] not in (0, 6)
            )
        ),
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (len(SURFACE_CODE_MAP), len(SURFACE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    ctor_payload = {
        "schema": "long.ctor@1",
        "object": "strict_scratch_tensor_oracle_constructor",
        "status": STATUS if all(checks.values()) else "LONG_CTOR_PROVISIONAL",
        "witness": {
            "name": THEOREM_ID,
            "classification": "strict_scratch_tensor_oracle_constructor",
            "summary": {
                "strict_scratch_passed": bool(obs["strict_scratch_passed_flag"]),
                "constructs_from_supplied_raw_seeds": bool(
                    obs["constructs_from_supplied_raw_seeds_flag"]
                ),
                "tensor_support": obs["tensor_support"],
                "tensor_coefficient_total": obs["tensor_coefficient_total"],
                "canonical_tensor_multiset_matches": bool(
                    obs["canonical_tensor_multiset_matches_flag"]
                ),
                "terminal_oracle_matches": bool(
                    obs["terminal_q42_map_matches_flag"]
                    and obs["terminal_q12_map_matches_flag"]
                    and obs["terminal_q42_tensor_matches_flag"]
                    and obs["terminal_q12_tensor_matches_flag"]
                ),
                "long_orac_certified": bool(obs["long_orac_certified_flag"]),
                "exact_npz_byte_reproduction_claim": False,
            },
            "surface_code_map": SURFACE_CODE_MAP,
            "hash_code_map": HASH_CODE_MAP,
            "surface_table_sha256": sha_array(rows["surface_table"]),
            "observable_table_sha256": sha_array(rows["observable_table"]),
            "strict_constructor_result_sha256": witness.get(
                "constructor_result_sha256"
            ),
            "long_orac_certificate_sha256": long_orac.get("certificate_sha256"),
        },
    }
    report = {
        "schema": "long.ctor.report@1",
        "status": ctor_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_ctor certifies that the generated strict-scratch constructor "
            "recreates the A985 multiplication tensor as a canonical sparse "
            "multiset and recreates the terminal q42/q12 oracle surfaces exactly, "
            "while keeping Halloween.npz as an audit target rather than a "
            "semantic constructor input. It also records that the current "
            "long_orac oracle status split remains certified on top of that "
            "surface."
        ),
        "stage_protocol": {
            "draft": "read the strict-scratch constructor, raw tensor, generated tensor, relation partition, terminal quotient, and long_orac artifacts",
            "witness": "emit constructor surface rows, artifact hashes, exact equality flags, cache-size counts, and formula compression counts",
            "coherence": "check strict constructor status, finite object shape, canonical tensor equality, terminal oracle equality, long_orac status, table shapes, and cache-boundary flags",
            "closure": "certify algorithmic tensor/oracle replay without claiming byte-for-byte npz reproduction or final goal closure",
            "emit": "write long_ctor artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "raw_relations": input_entry(RAW_RELATIONS),
            "raw_quotients": input_entry(RAW_QUOTIENTS),
            "strict_tensor": npz_array_entry(STRICT_TENSOR, tensor_arrays(STRICT_TENSOR)),
            "strict_relations": npz_array_entry(
                STRICT_RELATIONS, relation_arrays(STRICT_RELATIONS)
            ),
            "strict_quotients": npz_array_entry(
                STRICT_QUOTIENTS, quotient_arrays(STRICT_QUOTIENTS)
            ),
            "coorient_formula": input_entry(FORMULA_JSON),
            "long_orac_report": input_entry(
                LONG_ORAC_REPORT,
                {
                    "status": long_orac.get("status"),
                    "certificate_sha256": long_orac.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "ctor": relpath(OUT_DIR / "ctor.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
            "hash_csv": relpath(OUT_DIR / "hash.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": ctor_payload["witness"],
        "checks": checks,
        "observables": obs,
        "closure_boundary": {
            "certifies": [
                "the strict-scratch constructor passes with zero supplied raw seed boundary",
                "the 2576-point, 985-relation ordered-pair partition is reconstructed",
                "the A985 tensor support is 1,414,965 and coefficient mass is 2,537,360",
                "the generated tensor equals Halloween.npz after canonical sparse-row sorting",
                "the generated q42/q12 maps and q42/q12 tensors match the raw oracle files exactly",
                "the current long_orac status split is certified over the same tensor/oracle surface",
                "Halloween.npz is demoted to audit/cache role for this constructor surface",
            ],
            "does_not_certify_because_out_of_scope": [
                "byte-for-byte reproduction of the Halloween.npz zip container",
                "preservation of the stored raw triples row order",
                "preservation of the raw representative-row choices in the reps array",
                "a probability measure on the full raw tensor support beyond long_measure scope",
                "full raw-path materialization beyond the compressed active-product path surface",
                "completion of any external or absolute infinite theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Use long_ctor as the constructor guardrail, then target the remaining "
            "raw cache boundary only if exact npz byte reproduction is operationally "
            "needed; otherwise move to broad bundle integration."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.ctor.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": ctor_payload["witness"],
    }
    manifest = {
        "schema": "long.ctor.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "ctor": ctor_payload,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "hash_csv": hash_csv_text(rows["hash_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
    }


def hash_csv_text(rows: list[dict[str, Any]]) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=HASH_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "ctor.json", payloads["ctor"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "hash.csv").write_text(payloads["hash_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
