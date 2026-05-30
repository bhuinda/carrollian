from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23q import (
        build_components,
        component_mask,
        gf2_rref,
        project_to_components,
        row_mask,
        span_from_basis_masks,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23q import (
        build_components,
        component_mask,
        gf2_rref,
        project_to_components,
        row_mask,
        span_from_basis_masks,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23merge"
STATUS = "SECTOR33_K23_ACTIVE_MERGE_W24_RANK2_SUBCODE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23merge.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23merge.py"
LONG_K23Q_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23q" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_ARTIFACT = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

GROUP_TEXT_HASH = "9948713962c081fcba924bc43802e5a9074e3e0989f984438d3771717addab2c"
TARGET_TEXT_HASH = "b9f469464a16f99c2871fa2539d36984a91b4c5d0fc48eef8f683cc4952b02ea"
IMAGE_TEXT_HASH = "3d77bb52c33a8e4d724b458390c05dd06a549680f35e06ef3f763768b1a4d57f"
OBS_TEXT_HASH = "b3f72c01401ec49bca0e58ec48ee2466d70cf9d0734505ffb7ca83b4d7d0c397"
MATRIX_SHA256 = "e8ff8ee62cc11daf63e6eb9410fc31b3046d471a3a15841bfae944eeaecf1636"

GROUP_COLUMNS = [
    "merge_group_id",
    "component_mask",
    "component_count",
    "input_pattern_xor",
    "target_w24_coordinate",
    "target_pattern",
]
TARGET_COLUMNS = [
    "w24_coordinate",
    "assigned_group_id",
    "output_pattern",
    "coordinate_used_flag",
    "dodecad_flag",
    "octad_flag",
]
IMAGE_COLUMNS = ["word_id", "image_mask", "image_weight", "w24_member_flag"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23q_certified_flag",
    "w24_code_certified_flag",
    "component_count",
    "active_component_count",
    "merge_group_count",
    "nonzero_merge_group_count",
    "zero_merge_group_count",
    "target_used_coordinate_count",
    "image_generator_rank",
    "image_rowspace_word_count",
    "image_w24_member_word_count",
    "image_w24_subcode_flag",
    "dodecad_weight",
    "octad_weight",
    "intersection_weight",
    "sum_weight",
    "full_k23_equality_certified_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_w24_code(artifact: dict[str, Any]) -> set[int]:
    code = {0}
    for generator in artifact["golay_code"]["generator_basis_masks"]:
        mask = int(generator)
        code |= {word ^ mask for word in list(code)}
    return code


def first_dodecad_octad_pair(w24_code: set[int]) -> tuple[int, int]:
    dodecads = sorted(word for word in w24_code if int(word).bit_count() == 12)
    octads = sorted(word for word in w24_code if int(word).bit_count() == 8)
    for dodecad in dodecads:
        for octad in octads:
            if int(dodecad & octad).bit_count() == 4:
                return int(dodecad), int(octad)
    raise AssertionError("no W24 dodecad/octad pair with intersection four")


def coordinates(mask: int) -> list[int]:
    return [index for index in range(24) if (int(mask) >> index) & 1]


def build_pair_collapse() -> dict[str, Any]:
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64)
    support_kernel = (kernel_basis != 0).astype(np.uint8)
    components, _pair_rows = build_components(support_kernel)
    quotient = project_to_components(support_kernel, components)
    quotient_rref, quotient_pivots = gf2_rref(quotient)
    rank = len(quotient_pivots)
    patterns: list[int] = []
    for column in range(quotient.shape[1]):
        pattern = 0
        for row in range(rank):
            if quotient_rref[row, column]:
                pattern |= 1 << row
        patterns.append(pattern)
    pattern_to_components: dict[int, list[int]] = defaultdict(list)
    for component_id, pattern in enumerate(patterns):
        if pattern:
            pattern_to_components[pattern].append(component_id)
    return {
        "support_kernel": support_kernel,
        "components": components,
        "quotient": quotient,
        "quotient_rref": quotient_rref,
        "patterns": patterns,
        "pattern_to_components": {key: sorted(value) for key, value in pattern_to_components.items()},
    }


def build_merge_groups(pattern_to_components: dict[int, list[int]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []

    def add_group(component_ids: list[int], target_pattern: int) -> None:
        input_pattern = 0
        for component_id in component_ids:
            source_pattern = next(pattern for pattern, ids in pattern_to_components.items() if component_id in ids)
            input_pattern ^= int(source_pattern)
        if input_pattern != target_pattern:
            raise AssertionError(f"merge group pattern mismatch: {component_ids}")
        groups.append(
            {
                "component_ids": sorted(component_ids),
                "input_pattern_xor": int(input_pattern),
                "target_pattern": int(target_pattern),
            }
        )

    for component_id in pattern_to_components[1]:
        add_group([component_id], 1)
    for component_id in pattern_to_components[4]:
        add_group([component_id], 4)
    for component_id in pattern_to_components[5]:
        add_group([component_id], 5)
    for component_3, component_6 in zip(pattern_to_components[3], pattern_to_components[6], strict=True):
        add_group([component_3, component_6], 5)
    add_group([pattern_to_components[2][0], pattern_to_components[8][0], pattern_to_components[10][0]], 0)
    return groups


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "component_projection",
        "merge_projection",
        "image_generators",
        "image_words",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23q = load_json(LONG_K23Q_REPORT)
    w24_report = load_json(W24_REPORT)
    w24_artifact = load_json(W24_ARTIFACT)
    w24_code = build_w24_code(w24_artifact)
    dodecad, octad = first_dodecad_octad_pair(w24_code)
    intersection = dodecad & octad
    dodecad_only = dodecad & ~octad
    octad_only = octad & ~dodecad
    pair = build_pair_collapse()
    groups = build_merge_groups(pair["pattern_to_components"])
    pattern_targets = {
        1: coordinates(dodecad_only),
        4: coordinates(octad_only),
        5: coordinates(intersection),
        0: [min(set(range(24)) - set(coordinates(dodecad | octad)))],
    }
    target_queues = {pattern: list(values) for pattern, values in pattern_targets.items()}
    group_rows: list[dict[str, int]] = []
    merge_projection = np.zeros((len(pair["components"]), 24), dtype=np.uint8)
    assigned_by_coordinate = {coordinate: -1 for coordinate in range(24)}
    output_pattern_by_coordinate = {coordinate: 0 for coordinate in range(24)}
    for group_id, group in enumerate(groups):
        target_pattern = int(group["target_pattern"])
        target_coordinate = int(target_queues[target_pattern].pop(0))
        for component_id in group["component_ids"]:
            merge_projection[int(component_id), target_coordinate] ^= 1
        assigned_by_coordinate[target_coordinate] = group_id
        output_pattern_by_coordinate[target_coordinate] = target_pattern
        group_rows.append(
            {
                "merge_group_id": group_id,
                "component_mask": component_mask(group["component_ids"]),
                "component_count": len(group["component_ids"]),
                "input_pattern_xor": int(group["input_pattern_xor"]),
                "target_w24_coordinate": target_coordinate,
                "target_pattern": target_pattern,
            }
        )
    image_generators = (pair["quotient_rref"] @ merge_projection) % 2
    image_masks = [row_mask(row) for row in image_generators]
    image_code = span_from_basis_masks(image_masks)
    image_rows = [
        {
            "word_id": word_id,
            "image_mask": int(word),
            "image_weight": int(word).bit_count(),
            "w24_member_flag": int(int(word) in w24_code),
        }
        for word_id, word in enumerate(sorted(image_code))
    ]
    target_rows = [
        {
            "w24_coordinate": coordinate,
            "assigned_group_id": int(assigned_by_coordinate[coordinate]),
            "output_pattern": int(output_pattern_by_coordinate[coordinate]),
            "coordinate_used_flag": int(assigned_by_coordinate[coordinate] >= 0),
            "dodecad_flag": int((dodecad >> coordinate) & 1),
            "octad_flag": int((octad >> coordinate) & 1),
        }
        for coordinate in range(24)
    ]
    image_rref, image_pivots = gf2_rref(image_generators)
    obs = {
        "long_k23q_certified_flag": int(
            long_k23q.get("status") == "SECTOR33_K23_PAIR_COLLAPSE_24_QUOTIENT_FAMILY_OBSTRUCTED"
            and long_k23q.get("all_checks_pass") is True
        ),
        "w24_code_certified_flag": int(
            w24_report.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
            and w24_report.get("all_checks_pass") is True
        ),
        "component_count": len(pair["components"]),
        "active_component_count": sum(1 for pattern in pair["patterns"] if pattern),
        "merge_group_count": len(group_rows),
        "nonzero_merge_group_count": sum(1 for row in group_rows if row["target_pattern"] != 0),
        "zero_merge_group_count": sum(1 for row in group_rows if row["target_pattern"] == 0),
        "target_used_coordinate_count": sum(1 for row in target_rows if row["coordinate_used_flag"]),
        "image_generator_rank": len(image_pivots),
        "image_rowspace_word_count": len(image_code),
        "image_w24_member_word_count": sum(row["w24_member_flag"] for row in image_rows),
        "image_w24_subcode_flag": int(all(row["w24_member_flag"] for row in image_rows)),
        "dodecad_weight": int(dodecad).bit_count(),
        "octad_weight": int(octad).bit_count(),
        "intersection_weight": int(intersection).bit_count(),
        "sum_weight": int(dodecad ^ octad).bit_count(),
        "full_k23_equality_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "component_projection": pair["quotient"].astype(np.int64),
        "merge_projection": merge_projection.astype(np.int64),
        "image_generators": image_generators.astype(np.int64),
        "image_words": table_from_rows(IMAGE_COLUMNS, image_rows),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23q": long_k23q,
        "w24_report": w24_report,
        "w24_artifact": w24_artifact,
        "group_rows": group_rows,
        "target_rows": target_rows,
        "image_rows": image_rows,
        "obs_rows": obs_rows,
        "group_table": table_from_rows(GROUP_COLUMNS, group_rows),
        "target_table": table_from_rows(TARGET_COLUMNS, target_rows),
        "image_table": table_from_rows(IMAGE_COLUMNS, image_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "dodecad": dodecad,
        "octad": octad,
        "image_masks": image_masks,
        "pattern_counts": {
            str(key): int(value)
            for key, value in sorted(Counter(row["target_pattern"] for row in group_rows).items())
        },
        "group_text_hash": hashlib.sha256(digest_text(GROUP_COLUMNS, group_rows).encode("ascii")).hexdigest(),
        "target_text_hash": hashlib.sha256(digest_text(TARGET_COLUMNS, target_rows).encode("ascii")).hexdigest(),
        "image_text_hash": hashlib.sha256(digest_text(IMAGE_COLUMNS, image_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (obs["long_k23q_certified_flag"], obs["w24_code_certified_flag"]) == (1, 1),
        "merge_shape_is_expected": (
            obs["component_count"],
            obs["active_component_count"],
            obs["merge_group_count"],
            obs["nonzero_merge_group_count"],
            obs["zero_merge_group_count"],
            obs["target_used_coordinate_count"],
        )
        == (37, 21, 17, 16, 1, 17),
        "w24_pair_has_required_intersection": (
            obs["dodecad_weight"],
            obs["octad_weight"],
            obs["intersection_weight"],
            obs["sum_weight"],
        )
        == (12, 8, 4, 12),
        "image_is_rank2_w24_subcode": (
            obs["image_generator_rank"],
            obs["image_rowspace_word_count"],
            obs["image_w24_member_word_count"],
            obs["image_w24_subcode_flag"],
        )
        == (2, 4, 4, 1),
        "global_claims_remain_open": (
            obs["full_k23_equality_certified_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_active_merge_w24_rank2_subcode",
        "summary": obs,
        "dodecad_mask": rows["dodecad"],
        "octad_mask": rows["octad"],
        "image_generator_masks": rows["image_masks"],
        "pattern_counts": rows["pattern_counts"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies one active-merge quotient landing in a rank-2 W24 subcode; it is not a full K23-to-W24 equality proof.",
    }
    seam_payload = {
        "schema": "long.k23merge.seam@1",
        "status": STATUS,
        "claim": "A support-normalized active-merge quotient of the pair-collapsed K23 rowspace maps onto a certified rank-2 W24 subcode generated by a dodecad and an octad with intersection four.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23q": input_entry(
            LONG_K23Q_REPORT,
            {
                "status": rows["long_k23q"].get("status"),
                "certificate_sha256": rows["long_k23q"].get("certificate_sha256"),
            },
        ),
        "long_k23_matrices": input_entry(LONG_K23_MATRICES),
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
        "schema": "long.k23merge.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23merge certifies a concrete active-merge quotient witness from the pair-collapsed K23 surface into a W24 rank-2 subcode.",
        "stage_protocol": {
            "draft": "read long_k23q, K23 matrices, and the certified W24 code",
            "witness": "emit merge groups, target W24 coordinates, image codewords, observables, and matrices",
            "coherence": "check merge counts, dodecad/octad intersection, image rank, and W24 membership for all image words",
            "closure": "certify this rank-2 W24 subcode witness while keeping full K23 equality open",
            "emit": "write long_k23merge artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "group_rows_csv": relpath(OUT_DIR / "group_rows.csv"),
            "target_rows_csv": relpath(OUT_DIR / "target_rows.csv"),
            "image_rows_csv": relpath(OUT_DIR / "image_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23merge_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a deterministic active-component merge of the pair-collapsed K23 quotient",
                "the merge produces 17 used W24 coordinates with output pattern counts 1:8, 4:4, 5:4, 0:1",
                "the selected W24 dodecad has weight 12 and the selected octad has weight 8",
                "their intersection has weight 4 and their sum has weight 12",
                "the quotient image has rank 2 and all 4 image words are in the certified W24 code",
            ],
            "does_not_certify": [
                "a rank-12 W24 image",
                "full K23 rowspace equality with the W24/Euler-punctured syzygy rowspace",
                "basis-independence over all possible integral K23 lattice bases",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Promote the active-merge solver from rank 2 to rank 3 or prove rank 2 is maximal under support-normalized pair-collapse merges.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23merge.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23merge.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "group_csv": csv_text(GROUP_COLUMNS, rows["group_rows"]),
        "target_csv": csv_text(TARGET_COLUMNS, rows["target_rows"]),
        "image_csv": csv_text(IMAGE_COLUMNS, rows["image_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "group_table": rows["group_table"],
        "target_table": rows["target_table"],
        "image_table": rows["image_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "group_text_sha256": rows["group_text_hash"],
            "target_text_sha256": rows["target_text_hash"],
            "image_text_sha256": rows["image_text_hash"],
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
    (OUT_DIR / "group_rows.csv").write_text(payloads["group_csv"], encoding="utf-8")
    (OUT_DIR / "target_rows.csv").write_text(payloads["target_csv"], encoding="utf-8")
    (OUT_DIR / "image_rows.csv").write_text(payloads["image_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        group_table=payloads["group_table"],
        target_table=payloads["target_table"],
        image_table=payloads["image_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23merge_matrices.npz", **payloads["matrix_payload"])
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
