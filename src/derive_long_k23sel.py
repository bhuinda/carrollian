from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23sel"
STATUS = "SECTOR33_K23_CANONICAL_FRAME_GOLAY_SELECTOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23sel.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23sel.py"
LONG_K23SYZ_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23syz" / "report.json"
CANONICAL_FRAME = ROOT / "data" / "geometry" / "canonical_24_syzygy_frame.json"
W24_ROW_ALPHABETIZATION = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

COORD_TEXT_HASH = "7780af0353800bc51bd62c213d4ac814e0a222cfc3980a12f88d87b5eb405f3a"
GENERATOR_TEXT_HASH = "2fe5c482bf618df954dbf9a40a510e1dd26f252ed1b8098a34c8f51e4c6b7b8e"
ORTH_TEXT_HASH = "6d007b5b9763815a4392f838522b09a26e09d7f1a471701a0608ab74381680ed"
FULL_HIST_TEXT_HASH = "a4f8954a92b9b9072acc519b71b515c0f03bc8d0996336805c2c17c99ad73eb8"
PUNCTURED_HIST_TEXT_HASH = "4eb73cdd9c385e27b0484cf52e8fcd86f54b596a76193111534b113e8d407695"
EULER_HIST_TEXT_HASH = "10043994fd9df5c60bfc4734d87e332640b21a13456f98cfba9bc920c612b3f5"
OBS_TEXT_HASH = "0c887439c723fd4445fa237539ae6b5dd7b1008a4338bea191485c17e7602c4c"
MATRIX_SHA256 = "0bb2b2145d5cce3289da300b7d095221f28f2862d62d1c60509222e58d802bbd"

COORD_COLUMNS = [
    "coordinate",
    "canonical_role_code",
    "syzygy_index",
    "mog_row",
    "mog_column",
    "row_f4_value",
    "euler_flag",
    "syzygy_flag",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "mask",
    "weight",
    "euler_bit",
    "punctured_mask",
    "punctured_weight",
    "quadratic_value",
    "self_dot_mod2",
]
ORTH_COLUMNS = ["left_generator_id", "right_generator_id", "dot_mod2"]
HIST_COLUMNS = ["weight", "word_count"]
EULER_HIST_COLUMNS = ["euler_bit", "weight", "word_count"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23syz_certified_flag",
    "canonical_frame_certified_flag",
    "row_alphabetization_certified_flag",
    "selector_length",
    "selector_generator_count",
    "selector_rank",
    "selector_word_count",
    "selector_min_nonzero_weight",
    "selector_weight0_count",
    "selector_weight8_count",
    "selector_weight12_count",
    "selector_weight16_count",
    "selector_weight24_count",
    "quadratic_zero_word_count",
    "doubly_even_flag",
    "gram_nonzero_entry_count",
    "self_orthogonal_flag",
    "self_dual_flag",
    "lagrangian_selector_flag",
    "euler_zero_word_count",
    "euler_one_word_count",
    "punctured_length",
    "punctured_word_count",
    "punctured_rank",
    "punctured_min_nonzero_weight",
    "punctured_weight7_count",
    "punctured_weight8_count",
    "punctured_weight11_count",
    "punctured_weight12_count",
    "punctured_weight15_count",
    "punctured_weight16_count",
    "punctured_weight23_count",
    "shortened_euler_zero_word_count",
    "shortened_euler_zero_rank",
    "shortened_euler_zero_min_nonzero_weight",
    "euler_one_coset_word_count",
    "euler_one_coset_affine_dimension",
    "euler_one_coset_min_weight",
    "external_selector_boundary_flag",
    "intrinsic_selector_proven_flag",
    "m23_module_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def bit_weight(mask: int) -> int:
    return int(mask).bit_count()


def puncture_zero(mask: int) -> int:
    out = 0
    for index in range(1, 24):
        if (int(mask) >> index) & 1:
            out |= 1 << (index - 1)
    return out


def span_masks(generators: list[int]) -> list[int]:
    words = [0]
    for generator in generators:
        words += [word ^ int(generator) for word in words]
    return sorted(set(words))


def gf2_rank_masks(masks: list[int], width: int) -> int:
    basis = [0] * width
    rank = 0
    for mask in masks:
        value = int(mask)
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def mask_to_row(mask: int, width: int) -> list[int]:
    return [int((int(mask) >> index) & 1) for index in range(width)]


def dot_mod2(left: int, right: int) -> int:
    return bit_weight(int(left) & int(right)) % 2


def weight_histogram(words: list[int]) -> dict[int, int]:
    counter = Counter(bit_weight(word) for word in words)
    return {weight: int(counter[weight]) for weight in sorted(counter)}


def min_nonzero_weight(words: list[int]) -> int:
    return min(bit_weight(word) for word in words if int(word) != 0)


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "generator_masks",
        "generator_matrix",
        "codeword_masks",
        "punctured_codeword_masks",
        "euler_zero_punctured_masks",
        "euler_one_punctured_masks",
        "gram_matrix",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23syz = load_json(LONG_K23SYZ_REPORT)
    canonical_frame = load_json(CANONICAL_FRAME)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    frame_meta = canonical_frame.get("canonical_frame", {})
    audit = canonical_frame.get("Golay_binary_audit", {})
    w24_code = w24.get("golay_code", {})
    row_alpha = w24.get("row_alphabetization", {})
    generators = [int(mask) for mask in w24_code.get("generator_basis_masks", [])]
    words = span_masks(generators)
    punctured_words = sorted({puncture_zero(word) for word in words})
    euler_zero_words = sorted({puncture_zero(word) for word in words if (word & 1) == 0})
    euler_one_words = sorted({puncture_zero(word) for word in words if (word & 1) == 1})
    euler_one_base = euler_one_words[0]
    euler_one_diff_words = sorted({word ^ euler_one_base for word in euler_one_words})
    gram = np.asarray([[dot_mod2(left, right) for right in generators] for left in generators], dtype=np.int64)
    full_hist = weight_histogram(words)
    punctured_hist = weight_histogram(punctured_words)
    euler_zero_hist = weight_histogram(euler_zero_words)
    euler_one_hist = weight_histogram(euler_one_words)

    coordinate_labels = {
        int(row.get("coordinate", -1)): row for row in row_alpha.get("coordinate_labels", [])
    }
    coord_rows = []
    for coordinate in range(24):
        label = coordinate_labels.get(coordinate, {})
        coord_rows.append(
            {
                "coordinate": coordinate,
                "canonical_role_code": 0 if coordinate == 0 else 1,
                "syzygy_index": coordinate - 1 if coordinate > 0 else -1,
                "mog_row": int(label.get("mog_row", -1)),
                "mog_column": int(label.get("mog_column", -1)),
                "row_f4_value": int(label.get("row_f4_value", -1)),
                "euler_flag": int(coordinate == 0),
                "syzygy_flag": int(coordinate > 0),
            }
        )
    generator_rows = [
        {
            "generator_id": index,
            "mask": mask,
            "weight": bit_weight(mask),
            "euler_bit": mask & 1,
            "punctured_mask": puncture_zero(mask),
            "punctured_weight": bit_weight(puncture_zero(mask)),
            "quadratic_value": (bit_weight(mask) // 2) % 2,
            "self_dot_mod2": dot_mod2(mask, mask),
        }
        for index, mask in enumerate(generators)
    ]
    orth_rows = [
        {"left_generator_id": left, "right_generator_id": right, "dot_mod2": int(gram[left, right])}
        for left in range(len(generators))
        for right in range(len(generators))
    ]
    full_hist_rows = [{"weight": weight, "word_count": count} for weight, count in full_hist.items()]
    punctured_hist_rows = [{"weight": weight, "word_count": count} for weight, count in punctured_hist.items()]
    euler_hist_rows = (
        [{"euler_bit": 0, "weight": weight, "word_count": count} for weight, count in euler_zero_hist.items()]
        + [{"euler_bit": 1, "weight": weight, "word_count": count} for weight, count in euler_one_hist.items()]
    )
    obs = {
        "long_k23syz_certified_flag": int(
            long_k23syz.get("status") == "SECTOR33_K23_CANONICAL_SYZYGY_FRAME_BINDING_CERTIFIED"
            and long_k23syz.get("all_checks_pass") is True
        ),
        "canonical_frame_certified_flag": int(
            canonical_frame.get("status") == "CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN"
            and int(frame_meta.get("coordinate_count", 0)) == 24
            and int(frame_meta.get("syzygy_dimension", 0)) == 23
            and bool(audit.get("passes_extended_golay_weight_test", True)) is False
        ),
        "row_alphabetization_certified_flag": int(
            w24.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_DERIVED"
            and bool(w24.get("checks", {}).get("rank_is_12", False))
            and bool(w24.get("checks", {}).get("self_dual_by_rank_and_self_orthogonal", False))
            and bool(w24.get("checks", {}).get("doubly_even", False))
        ),
        "selector_length": int(w24_code.get("length", 0)),
        "selector_generator_count": len(generators),
        "selector_rank": gf2_rank_masks(generators, 24),
        "selector_word_count": len(words),
        "selector_min_nonzero_weight": min_nonzero_weight(words),
        "selector_weight0_count": full_hist.get(0, 0),
        "selector_weight8_count": full_hist.get(8, 0),
        "selector_weight12_count": full_hist.get(12, 0),
        "selector_weight16_count": full_hist.get(16, 0),
        "selector_weight24_count": full_hist.get(24, 0),
        "quadratic_zero_word_count": sum(int((bit_weight(word) // 2) % 2 == 0) for word in words),
        "doubly_even_flag": int(all(bit_weight(word) % 4 == 0 for word in words)),
        "gram_nonzero_entry_count": int(np.count_nonzero(gram)),
        "self_orthogonal_flag": int(np.count_nonzero(gram) == 0),
        "self_dual_flag": int(np.count_nonzero(gram) == 0 and gf2_rank_masks(generators, 24) == 12),
        "lagrangian_selector_flag": int(np.count_nonzero(gram) == 0 and gf2_rank_masks(generators, 24) * 2 == 24),
        "euler_zero_word_count": len(euler_zero_words),
        "euler_one_word_count": len(euler_one_words),
        "punctured_length": 23,
        "punctured_word_count": len(punctured_words),
        "punctured_rank": gf2_rank_masks(punctured_words, 23),
        "punctured_min_nonzero_weight": min_nonzero_weight(punctured_words),
        "punctured_weight7_count": punctured_hist.get(7, 0),
        "punctured_weight8_count": punctured_hist.get(8, 0),
        "punctured_weight11_count": punctured_hist.get(11, 0),
        "punctured_weight12_count": punctured_hist.get(12, 0),
        "punctured_weight15_count": punctured_hist.get(15, 0),
        "punctured_weight16_count": punctured_hist.get(16, 0),
        "punctured_weight23_count": punctured_hist.get(23, 0),
        "shortened_euler_zero_word_count": len(euler_zero_words),
        "shortened_euler_zero_rank": gf2_rank_masks(euler_zero_words, 23),
        "shortened_euler_zero_min_nonzero_weight": min_nonzero_weight(euler_zero_words),
        "euler_one_coset_word_count": len(euler_one_words),
        "euler_one_coset_affine_dimension": gf2_rank_masks(euler_one_diff_words, 23),
        "euler_one_coset_min_weight": min(bit_weight(word) for word in euler_one_words),
        "external_selector_boundary_flag": int(w24.get("canonicity_boundary", {}).get("canonical_from_pair_octad_wu_6j_data") is False),
        "intrinsic_selector_proven_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "generator_masks": np.asarray(generators, dtype=np.int64),
        "generator_matrix": np.asarray([mask_to_row(mask, 24) for mask in generators], dtype=np.int64),
        "codeword_masks": np.asarray(words, dtype=np.int64),
        "punctured_codeword_masks": np.asarray(punctured_words, dtype=np.int64),
        "euler_zero_punctured_masks": np.asarray(euler_zero_words, dtype=np.int64),
        "euler_one_punctured_masks": np.asarray(euler_one_words, dtype=np.int64),
        "gram_matrix": gram,
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23syz": long_k23syz,
        "canonical_frame": canonical_frame,
        "w24": w24,
        "coord_rows": coord_rows,
        "generator_rows": generator_rows,
        "orth_rows": orth_rows,
        "full_hist_rows": full_hist_rows,
        "punctured_hist_rows": punctured_hist_rows,
        "euler_hist_rows": euler_hist_rows,
        "obs_rows": obs_rows,
        "coord_table": table_from_rows(COORD_COLUMNS, coord_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "orth_table": table_from_rows(ORTH_COLUMNS, orth_rows),
        "full_hist_table": table_from_rows(HIST_COLUMNS, full_hist_rows),
        "punctured_hist_table": table_from_rows(HIST_COLUMNS, punctured_hist_rows),
        "euler_hist_table": table_from_rows(EULER_HIST_COLUMNS, euler_hist_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "coord_text_hash": hashlib.sha256(digest_text(COORD_COLUMNS, coord_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "orth_text_hash": hashlib.sha256(digest_text(ORTH_COLUMNS, orth_rows).encode("ascii")).hexdigest(),
        "full_hist_text_hash": hashlib.sha256(digest_text(HIST_COLUMNS, full_hist_rows).encode("ascii")).hexdigest(),
        "punctured_hist_text_hash": hashlib.sha256(digest_text(HIST_COLUMNS, punctured_hist_rows).encode("ascii")).hexdigest(),
        "euler_hist_text_hash": hashlib.sha256(digest_text(EULER_HIST_COLUMNS, euler_hist_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23syz_certified_flag"],
            obs["canonical_frame_certified_flag"],
            obs["row_alphabetization_certified_flag"],
        )
        == (1, 1, 1),
        "selector_profile_matches": (
            obs["selector_length"],
            obs["selector_generator_count"],
            obs["selector_rank"],
            obs["selector_word_count"],
            obs["selector_min_nonzero_weight"],
        )
        == (24, 12, 12, 4096, 8),
        "selector_weight_histogram_matches": (
            obs["selector_weight0_count"],
            obs["selector_weight8_count"],
            obs["selector_weight12_count"],
            obs["selector_weight16_count"],
            obs["selector_weight24_count"],
        )
        == (1, 759, 2576, 759, 1),
        "quadratic_isotropic_lagrangian": (
            obs["quadratic_zero_word_count"],
            obs["doubly_even_flag"],
            obs["gram_nonzero_entry_count"],
            obs["self_orthogonal_flag"],
            obs["self_dual_flag"],
            obs["lagrangian_selector_flag"],
        )
        == (4096, 1, 0, 1, 1, 1),
        "punctured_euler_profile_matches": (
            obs["euler_zero_word_count"],
            obs["euler_one_word_count"],
            obs["punctured_length"],
            obs["punctured_word_count"],
            obs["punctured_rank"],
            obs["punctured_min_nonzero_weight"],
            obs["punctured_weight7_count"],
            obs["punctured_weight8_count"],
            obs["punctured_weight11_count"],
            obs["punctured_weight12_count"],
            obs["punctured_weight15_count"],
            obs["punctured_weight16_count"],
            obs["punctured_weight23_count"],
        )
        == (2048, 2048, 23, 4096, 12, 7, 253, 506, 1288, 1288, 506, 253, 1),
        "shortened_and_coset_profiles_match": (
            obs["shortened_euler_zero_word_count"],
            obs["shortened_euler_zero_rank"],
            obs["shortened_euler_zero_min_nonzero_weight"],
            obs["euler_one_coset_word_count"],
            obs["euler_one_coset_affine_dimension"],
            obs["euler_one_coset_min_weight"],
        )
        == (2048, 11, 8, 2048, 11, 7),
        "intrinsic_module_boundary_remains_open": (
            obs["external_selector_boundary_flag"],
            obs["intrinsic_selector_proven_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_canonical_frame_golay_selector",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a selected rank-12 doubly-even self-dual binary selector in the canonical 24-frame; intrinsic selection and M23 action remain open.",
    }
    seam_payload = {
        "schema": "long.k23sel.seam@1",
        "status": STATUS,
        "claim": "The certified W24 row-alphabetized selector is installed as a quadratic/isotropic rank-12 binary selector on the canonical Euler-plus-23-syzygy frame.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23syz": input_entry(
            LONG_K23SYZ_REPORT,
            {
                "status": rows["long_k23syz"].get("status"),
                "certificate_sha256": rows["long_k23syz"].get("certificate_sha256"),
            },
        ),
        "canonical_24_syzygy_frame": input_entry(
            CANONICAL_FRAME,
            {
                "status": rows["canonical_frame"].get("status"),
                "canonical_24_syzygy_frame_sha256": rows["canonical_frame"].get(
                    "canonical_24_syzygy_frame_sha256"
                ),
            },
        ),
        "w24_row_alphabetization": input_entry(
            W24_ROW_ALPHABETIZATION,
            {
                "status": rows["w24"].get("status"),
                "artifact_sha256_excluding_this_field": rows["w24"].get(
                    "artifact_sha256_excluding_this_field"
                ),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23sel.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23sel certifies the selected W24/Golay binary selector on the canonical K23 syzygy frame.",
        "stage_protocol": {
            "draft": "read long_k23syz, the canonical 24 syzygy frame, and the certified W24 row alphabetization",
            "witness": "emit coordinate rows, generator rows, pairwise Gram rows, full/punctured/Euler histograms, observables, and masks",
            "coherence": "check rank, word count, weight histograms, quadratic zero law, Gram zero law, and Euler puncture profiles",
            "closure": "certify the selected binary selector while keeping intrinsic selection and M23 action open",
            "emit": "write long_k23sel artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "coordinate_rows_csv": relpath(OUT_DIR / "coordinate_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "orthogonality_rows_csv": relpath(OUT_DIR / "orthogonality_rows.csv"),
            "weight_histogram_csv": relpath(OUT_DIR / "weight_histogram.csv"),
            "punctured_weight_histogram_csv": relpath(OUT_DIR / "punctured_weight_histogram.csv"),
            "euler_histogram_csv": relpath(OUT_DIR / "euler_histogram.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23sel_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected W24 row-alphabetized binary code has length 24, rank 12, and 4096 words",
                "all selected words are quadratic-zero/doubly-even and the generator Gram matrix is zero",
                "the selected binary subspace is self-dual by rank and self-orthogonality",
                "deleting the Euler coordinate gives the certified length-23 punctured profile",
                "the Euler-zero shortening has rank 11 and minimum nonzero weight 8",
            ],
            "does_not_certify": [
                "that the selector is intrinsic to the naive binary shadow of the canonical frame",
                "an M23 module action on K23",
                "uniqueness of the selected row alphabetization",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Compute the punctured selector stabilizer on the Euler-deleted 23-frame and test whether the induced action is M23-type.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23sel.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23sel.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "coord_csv": csv_text(COORD_COLUMNS, rows["coord_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "orth_csv": csv_text(ORTH_COLUMNS, rows["orth_rows"]),
        "full_hist_csv": csv_text(HIST_COLUMNS, rows["full_hist_rows"]),
        "punctured_hist_csv": csv_text(HIST_COLUMNS, rows["punctured_hist_rows"]),
        "euler_hist_csv": csv_text(EULER_HIST_COLUMNS, rows["euler_hist_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "coord_table": rows["coord_table"],
        "generator_table": rows["generator_table"],
        "orth_table": rows["orth_table"],
        "full_hist_table": rows["full_hist_table"],
        "punctured_hist_table": rows["punctured_hist_table"],
        "euler_hist_table": rows["euler_hist_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "coord_text_sha256": rows["coord_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
            "orth_text_sha256": rows["orth_text_hash"],
            "full_hist_text_sha256": rows["full_hist_text_hash"],
            "punctured_hist_text_sha256": rows["punctured_hist_text_hash"],
            "euler_hist_text_sha256": rows["euler_hist_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
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
    (OUT_DIR / "coordinate_rows.csv").write_text(payloads["coord_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "orthogonality_rows.csv").write_text(payloads["orth_csv"], encoding="utf-8")
    (OUT_DIR / "weight_histogram.csv").write_text(payloads["full_hist_csv"], encoding="utf-8")
    (OUT_DIR / "punctured_weight_histogram.csv").write_text(payloads["punctured_hist_csv"], encoding="utf-8")
    (OUT_DIR / "euler_histogram.csv").write_text(payloads["euler_hist_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        coordinate_table=payloads["coord_table"],
        generator_table=payloads["generator_table"],
        orthogonality_table=payloads["orth_table"],
        weight_histogram_table=payloads["full_hist_table"],
        punctured_weight_histogram_table=payloads["punctured_hist_table"],
        euler_histogram_table=payloads["euler_hist_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23sel_matrices.npz", **payloads["matrix_payload"])
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
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
