from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from math import comb
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


THEOREM_ID = "long_k23q"
STATUS = "SECTOR33_K23_PAIR_COLLAPSE_24_QUOTIENT_FAMILY_OBSTRUCTED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23q.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23q.py"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
LONG_K23BIN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23bin" / "report.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_ARTIFACT = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

COMPONENT_TEXT_HASH = "656b9aadcf2a99baf658c4eae8847515cff6ec22ae418bb3819d2a7d219c5212"
PAIR_TEXT_HASH = "f1fcad407186144602bce9edb6652aa79d383b8398c2b15217e0665aab6d6214"
CANDIDATE_TEXT_HASH = "01a257d35b534b8a6fe33588e5d738b94e2e9793d4343e7f8827bb6ed388db5d"
WEIGHT_TEXT_HASH = "c771d56e09a9f5febef1ce1d3f7295cfc6015537fb631819554d21ee185e8efa"
OBS_TEXT_HASH = "3a52db2d45ea0ab8859822153c6285fa894248801f30995ef82ca83ca7feacf4"
MATRIX_SHA256 = "42c58cff42ca6d3aeadd004d572ad95bd18331a47e5eb6c9359bae791093ce1d"

COMPONENT_COLUMNS = [
    "component_id",
    "source_count",
    "source_mask",
    "quotient_active_flag",
    "pad_eligible_flag",
]
PAIR_COLUMNS = [
    "pair_row_id",
    "basis_row_id",
    "source_a",
    "source_b",
    "component_id",
    "collapsed_flag",
]
CANDIDATE_COLUMNS = [
    "candidate_id",
    "pad_component_mask",
    "pad_component_count",
    "quotient_length",
    "active_component_count",
    "quotient_rank",
    "min_nonzero_weight",
    "forbidden_weight_class_count",
    "forbidden_word_count",
    "w24_subcode_possible_flag",
]
WEIGHT_COLUMNS = ["weight", "rowspace_word_count", "w24_allowed_weight_flag", "forbidden_weight_flag"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "long_k23bin_certified_flag",
    "w24_code_certified_flag",
    "support_input_row_count",
    "support_normalized_rank",
    "two_support_relation_count",
    "quotient_component_count",
    "component_size_1_count",
    "component_size_2_count",
    "component_size_4_count",
    "active_component_count",
    "pad_eligible_component_count",
    "candidate_family_count",
    "quotient_length",
    "quotient_rank",
    "rowspace_word_count",
    "min_nonzero_weight",
    "forbidden_weight_class_count",
    "forbidden_word_count",
    "coordinate_permutation_obstruction_flag",
    "candidate_w24_subcode_count",
    "pair_collapse_family_closed_flag",
    "non_pair_quotient_open_flag",
    "k23_equality_certified_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def gf2_rref(matrix: np.ndarray) -> tuple[np.ndarray, list[int]]:
    work = np.asarray(matrix, dtype=np.uint8).copy() % 2
    row_count, column_count = work.shape
    pivots: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        candidates = np.flatnonzero(work[pivot_row:, column])
        if candidates.size == 0:
            continue
        source_row = pivot_row + int(candidates[0])
        if source_row != pivot_row:
            work[[pivot_row, source_row]] = work[[source_row, pivot_row]]
        for row in range(row_count):
            if row != pivot_row and work[row, column]:
                work[row] ^= work[pivot_row]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return work, pivots


def row_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row, dtype=np.uint8).tolist()):
        if int(value) & 1:
            mask |= 1 << index
    return mask


def span_from_basis_masks(basis_masks: list[int]) -> set[int]:
    span = {0}
    for mask in basis_masks:
        span |= {word ^ mask for word in list(span)}
    return span


def component_mask(values: list[int]) -> int:
    mask = 0
    for value in values:
        mask |= 1 << int(value)
    return mask


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "support_normalized_kernel",
        "component_projection",
        "component_activity",
        "quotient_rref",
        "rowspace_weight_histogram",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_components(support_kernel: np.ndarray) -> tuple[list[list[int]], list[dict[str, int]]]:
    parent = list(range(support_kernel.shape[1]))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a: int, b: int) -> None:
        root_a = find(a)
        root_b = find(b)
        if root_a != root_b:
            parent[root_b] = root_a

    pair_rows: list[dict[str, int]] = []
    pair_row_id = 0
    for basis_row_id, row in enumerate(support_kernel):
        sources = np.flatnonzero(row).astype(int).tolist()
        if len(sources) == 2:
            union(sources[0], sources[1])
            pair_rows.append(
                {
                    "pair_row_id": pair_row_id,
                    "basis_row_id": basis_row_id,
                    "source_a": sources[0],
                    "source_b": sources[1],
                    "component_id": -1,
                    "collapsed_flag": 1,
                }
            )
            pair_row_id += 1
    raw_components: dict[int, list[int]] = defaultdict(list)
    for source in range(support_kernel.shape[1]):
        raw_components[find(source)].append(source)
    components = sorted(raw_components.values(), key=lambda row: (row[0], len(row)))
    component_id_by_source = {source: component_id for component_id, comp in enumerate(components) for source in comp}
    for row in pair_rows:
        row["component_id"] = component_id_by_source[row["source_a"]]
    return components, pair_rows


def project_to_components(support_kernel: np.ndarray, components: list[list[int]]) -> np.ndarray:
    component_id_by_source = {source: component_id for component_id, comp in enumerate(components) for source in comp}
    projected = np.zeros((support_kernel.shape[0], len(components)), dtype=np.uint8)
    for row_id, row in enumerate(support_kernel):
        for source in np.flatnonzero(row):
            projected[row_id, component_id_by_source[int(source)]] ^= 1
    return projected


def build_rows() -> dict[str, Any]:
    long_k23 = load_json(LONG_K23_REPORT)
    long_k23bin = load_json(LONG_K23BIN_REPORT)
    w24_report = load_json(W24_REPORT)
    w24_artifact = load_json(W24_ARTIFACT)
    support_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64)

    support_kernel = (kernel_basis != 0).astype(np.uint8)
    support_rref, support_pivots = gf2_rref(support_kernel)
    components, pair_rows = build_components(support_kernel)
    quotient = project_to_components(support_kernel, components)
    quotient_rref, quotient_pivots = gf2_rref(quotient)
    quotient_rank = len(quotient_pivots)
    quotient_basis_masks = [row_mask(quotient_rref[row_index]) for row_index in range(quotient_rank)]
    rowspace = span_from_basis_masks(quotient_basis_masks)
    rowspace_weight_hist = Counter(int(word).bit_count() for word in rowspace)
    allowed_weights = {int(weight) for weight, count in w24_artifact["golay_code"]["weight_histogram"].items() if int(count) > 0}
    forbidden_weight_classes = sorted(
        weight for weight, count in rowspace_weight_hist.items() if int(count) > 0 and weight not in allowed_weights
    )
    forbidden_word_count = sum(int(rowspace_weight_hist[weight]) for weight in forbidden_weight_classes)
    component_activity = quotient.sum(axis=0).astype(np.int64)
    active_components = [index for index, value in enumerate(component_activity.tolist()) if int(value) > 0]
    pad_components = [index for index, value in enumerate(component_activity.tolist()) if int(value) == 0]
    component_size_hist = Counter(len(component) for component in components)
    nonzero_weights = sorted(weight for weight, count in rowspace_weight_hist.items() if weight and count)
    min_nonzero_weight = nonzero_weights[0] if nonzero_weights else 0
    quotient_length = 24
    pad_count = quotient_length - len(active_components)
    candidate_rows = [
        {
            "candidate_id": candidate_id,
            "pad_component_mask": component_mask(list(pad_choice)),
            "pad_component_count": pad_count,
            "quotient_length": quotient_length,
            "active_component_count": len(active_components),
            "quotient_rank": quotient_rank,
            "min_nonzero_weight": min_nonzero_weight,
            "forbidden_weight_class_count": len(forbidden_weight_classes),
            "forbidden_word_count": forbidden_word_count,
            "w24_subcode_possible_flag": 0,
        }
        for candidate_id, pad_choice in enumerate(itertools.combinations(pad_components, pad_count))
    ]
    component_rows = [
        {
            "component_id": component_id,
            "source_count": len(component),
            "source_mask": component_mask(component),
            "quotient_active_flag": int(component_id in active_components),
            "pad_eligible_flag": int(component_id in pad_components),
        }
        for component_id, component in enumerate(components)
    ]
    weight_rows = [
        {
            "weight": weight,
            "rowspace_word_count": int(rowspace_weight_hist.get(weight, 0)),
            "w24_allowed_weight_flag": int(weight in allowed_weights),
            "forbidden_weight_flag": int(rowspace_weight_hist.get(weight, 0) > 0 and weight not in allowed_weights),
        }
        for weight in range(quotient_length + 1)
    ]
    candidate_family_count = comb(len(pad_components), pad_count)
    obs = {
        "long_k23_certified_flag": int(
            long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
            and long_k23.get("all_checks_pass") is True
        ),
        "long_k23bin_certified_flag": int(
            long_k23bin.get("status") == "SECTOR33_K23_BINARY_ROWSPACE_PROFILE_CERTIFIED"
            and long_k23bin.get("all_checks_pass") is True
        ),
        "w24_code_certified_flag": int(
            w24_report.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
            and w24_report.get("all_checks_pass") is True
        ),
        "support_input_row_count": len(support_rows),
        "support_normalized_rank": len(support_pivots),
        "two_support_relation_count": len(pair_rows),
        "quotient_component_count": len(components),
        "component_size_1_count": int(component_size_hist.get(1, 0)),
        "component_size_2_count": int(component_size_hist.get(2, 0)),
        "component_size_4_count": int(component_size_hist.get(4, 0)),
        "active_component_count": len(active_components),
        "pad_eligible_component_count": len(pad_components),
        "candidate_family_count": candidate_family_count,
        "quotient_length": quotient_length,
        "quotient_rank": quotient_rank,
        "rowspace_word_count": len(rowspace),
        "min_nonzero_weight": min_nonzero_weight,
        "forbidden_weight_class_count": len(forbidden_weight_classes),
        "forbidden_word_count": forbidden_word_count,
        "coordinate_permutation_obstruction_flag": int(forbidden_word_count > 0),
        "candidate_w24_subcode_count": sum(row["w24_subcode_possible_flag"] for row in candidate_rows),
        "pair_collapse_family_closed_flag": int(candidate_family_count == len(candidate_rows) and forbidden_word_count > 0),
        "non_pair_quotient_open_flag": 1,
        "k23_equality_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "support_normalized_kernel": support_kernel.astype(np.int64),
        "component_projection": quotient.astype(np.int64),
        "component_activity": component_activity.astype(np.int64),
        "quotient_rref": quotient_rref.astype(np.int64),
        "rowspace_weight_histogram": np.asarray([int(rowspace_weight_hist.get(weight, 0)) for weight in range(25)], dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23": long_k23,
        "long_k23bin": long_k23bin,
        "w24_report": w24_report,
        "w24_artifact": w24_artifact,
        "component_rows": component_rows,
        "pair_rows": pair_rows,
        "candidate_rows": candidate_rows,
        "weight_rows": weight_rows,
        "obs_rows": obs_rows,
        "component_table": table_from_rows(COMPONENT_COLUMNS, component_rows),
        "pair_table": table_from_rows(PAIR_COLUMNS, pair_rows),
        "candidate_table": table_from_rows(CANDIDATE_COLUMNS, candidate_rows),
        "weight_table": table_from_rows(WEIGHT_COLUMNS, weight_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "active_components": active_components,
        "pad_components": pad_components,
        "forbidden_weight_classes": forbidden_weight_classes,
        "component_text_hash": hashlib.sha256(digest_text(COMPONENT_COLUMNS, component_rows).encode("ascii")).hexdigest(),
        "pair_text_hash": hashlib.sha256(digest_text(PAIR_COLUMNS, pair_rows).encode("ascii")).hexdigest(),
        "candidate_text_hash": hashlib.sha256(digest_text(CANDIDATE_COLUMNS, candidate_rows).encode("ascii")).hexdigest(),
        "weight_text_hash": hashlib.sha256(digest_text(WEIGHT_COLUMNS, weight_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23_certified_flag"],
            obs["long_k23bin_certified_flag"],
            obs["w24_code_certified_flag"],
        )
        == (1, 1, 1),
        "support_normalized_pair_collapse_shape": (
            obs["support_normalized_rank"],
            obs["two_support_relation_count"],
            obs["quotient_component_count"],
            obs["component_size_1_count"],
            obs["component_size_2_count"],
            obs["component_size_4_count"],
        )
        == (23, 19, 37, 26, 7, 4),
        "twenty_four_quotient_family_count": (
            obs["active_component_count"],
            obs["pad_eligible_component_count"],
            obs["candidate_family_count"],
            obs["quotient_length"],
        )
        == (21, 16, 560, 24),
        "quotient_rowspace_weight_obstruction": (
            obs["quotient_rank"],
            obs["rowspace_word_count"],
            obs["min_nonzero_weight"],
            obs["forbidden_weight_class_count"],
            obs["forbidden_word_count"],
            obs["coordinate_permutation_obstruction_flag"],
        )
        == (4, 16, 2, 5, 12, 1),
        "all_pair_collapse_candidates_fail": (
            obs["candidate_w24_subcode_count"],
            obs["pair_collapse_family_closed_flag"],
            obs["non_pair_quotient_open_flag"],
            obs["k23_equality_certified_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 1, 1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_pair_collapse_24_quotient_family",
        "summary": obs,
        "active_components": rows["active_components"],
        "pad_components": rows["pad_components"],
        "forbidden_weight_classes": rows["forbidden_weight_classes"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the support-normalized pair-collapse 24-coordinate completion family only; more general linear quotients remain open.",
    }
    seam_payload = {
        "schema": "long.k23q.seam@1",
        "status": STATUS,
        "claim": "After support-normalizing K23 and collapsing the 19 two-support relations, all 560 length-24 completions of the 21 active quotient coordinates have forbidden W24 weights.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23": input_entry(
            LONG_K23_REPORT,
            {
                "status": rows["long_k23"].get("status"),
                "certificate_sha256": rows["long_k23"].get("certificate_sha256"),
            },
        ),
        "long_k23bin": input_entry(
            LONG_K23BIN_REPORT,
            {
                "status": rows["long_k23bin"].get("status"),
                "certificate_sha256": rows["long_k23bin"].get("certificate_sha256"),
            },
        ),
        "long_k23_matrices": input_entry(LONG_K23_MATRICES),
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "w24_hexacode_row_alphabetization": input_entry(
            W24_REPORT,
            {
                "status": rows["w24_report"].get("status"),
                "certificate_sha256": rows["w24_report"].get("certificate_sha256"),
            },
        ),
        "w24_artifact": input_entry(
            W24_ARTIFACT,
            {
                "status": rows["w24_artifact"].get("status"),
                "artifact_sha256_excluding_this_field": rows["w24_artifact"].get(
                    "artifact_sha256_excluding_this_field"
                ),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23q.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23q certifies a bounded non-coordinate 56-to-24 quotient family and obstructs it by W24 weight invariants.",
        "stage_protocol": {
            "draft": "read long_k23, long_k23bin, K23 kernel matrices, sector33 support rows, and W24 weights",
            "witness": "emit pair-collapse rows, quotient components, all 560 padded 24-coordinate completions, weight rows, observables, and matrices",
            "coherence": "check support-normalized rank, two-support collapse components, 21 active plus 16 pad-eligible components, and W24 forbidden weights",
            "closure": "certify the pair-collapse quotient family obstruction while keeping general linear quotients open",
            "emit": "write long_k23q artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "component_rows_csv": relpath(OUT_DIR / "component_rows.csv"),
            "pair_rows_csv": relpath(OUT_DIR / "pair_rows.csv"),
            "candidate_rows_csv": relpath(OUT_DIR / "candidate_rows.csv"),
            "weight_rows_csv": relpath(OUT_DIR / "weight_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23q_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "support-normalized K23 still has rank 23",
                "19 two-support K23 relations generate a canonical pair-collapse quotient with 37 components",
                "the quotient has 21 active components and 16 inactive pad-eligible components",
                "all 560 ways to pad the active quotient to length 24 share rank 4 and forbidden W24 weights",
                "the pair-collapse 24-coordinate quotient family has zero W24-subcode candidates",
            ],
            "does_not_certify": [
                "absence of a more general linear quotient from 56 support coordinates to W24",
                "basis-independence over all possible integral K23 lattice bases",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Move from pair-collapse quotients to a constrained linear solver over the 32 active K23 columns, enforcing W24 allowed weights before any exact basis comparison.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23q.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23q.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "weight_csv": csv_text(WEIGHT_COLUMNS, rows["weight_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "component_table": rows["component_table"],
        "pair_table": rows["pair_table"],
        "candidate_table": rows["candidate_table"],
        "weight_table": rows["weight_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "component_text_sha256": rows["component_text_hash"],
            "pair_text_sha256": rows["pair_text_hash"],
            "candidate_text_sha256": rows["candidate_text_hash"],
            "weight_text_sha256": rows["weight_text_hash"],
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
    (OUT_DIR / "component_rows.csv").write_text(payloads["component_csv"], encoding="utf-8")
    (OUT_DIR / "pair_rows.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "candidate_rows.csv").write_text(payloads["candidate_csv"], encoding="utf-8")
    (OUT_DIR / "weight_rows.csv").write_text(payloads["weight_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        component_table=payloads["component_table"],
        pair_table=payloads["pair_table"],
        candidate_table=payloads["candidate_table"],
        weight_table=payloads["weight_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23q_matrices.npz", **payloads["matrix_payload"])
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
