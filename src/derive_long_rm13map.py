from __future__ import annotations

import csv
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .generate_source import build_source_code
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from generate_source import build_source_code
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_rm13map"
STATUS = "RM13_SOURCE_TO_W24_COORDINATE_MAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_rm13map.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rm13map.py"
SOURCE_SCRIPT = ROOT / "src" / "generate_source.py"
LONG_RM13_REPORT = D20_INVARIANTS / "proof_obligations" / "long_rm13" / "report.json"
LONG_K23MERGE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23merge" / "report.json"
LONG_K23MERGE_IMAGE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23merge" / "image_rows.csv"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_ARTIFACT = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

MAP_TEXT_HASH = "8873c3efa9b1b51e8e6987766c0f1e90758032acb66aab482d4d6028dc9aabea"
REPLAY_TEXT_HASH = "6e5af750ce7332d89ae3f050ff012dd1835cf25bd1ec56d267f499450947e3be"
OBS_TEXT_HASH = "0b1d3e9379a1a426151b738af3f114814e8665b2fb7e92354272e8156efbf0f0"
MATRIX_SHA256 = "eefdb044bfd2be2c2267ea2c5930d53dffcb18bdb29e50978dd997e158d9ec69"

MAP_COLUMNS = [
    "source_coord",
    "target_coord",
    "source_singleton_mask",
    "target_singleton_mask",
]
REPLAY_COLUMNS = [
    "word_id",
    "external_mask",
    "external_weight",
    "source_preimage_mask",
    "source_preimage_weight",
    "external_w24_member_flag",
    "source_endpoint_member_flag",
    "remap_matches_external_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_rm13_certified_flag",
    "long_k23merge_certified_flag",
    "external_w24_certified_flag",
    "source_code_size",
    "target_code_size",
    "source_octad_count",
    "target_octad_count",
    "five_subset_lookup_count",
    "fixed_prefix_coordinate_count",
    "search_node_count",
    "coordinate_map_length",
    "coordinate_map_bijective_flag",
    "mapped_source_code_size",
    "mapped_source_target_intersection_count",
    "mapped_source_target_symmetric_difference_count",
    "coordinate_conjugacy_materialized_flag",
    "k23_image_word_count",
    "k23_image_external_member_count",
    "k23_image_source_preimage_member_count",
    "nonzero_k23_image_source_preimage_member_count",
    "k23_image_remap_match_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def vector_mask(vector: tuple[int, ...]) -> int:
    mask = 0
    for index, value in enumerate(vector):
        if int(value):
            mask |= 1 << index
    return mask


def span_from_basis_masks(basis_masks: list[int]) -> set[int]:
    span = {0}
    for mask in basis_masks:
        span |= {word ^ int(mask) for word in list(span)}
    return span


def coordinates(mask: int) -> list[int]:
    return [index for index in range(24) if (int(mask) >> index) & 1]


def map_mask(mask: int, permutation: tuple[int, ...]) -> int:
    out = 0
    for source_coord, target_coord in enumerate(permutation):
        if (int(mask) >> source_coord) & 1:
            out |= 1 << target_coord
    return out


def preimage_mask(mask: int, permutation: tuple[int, ...]) -> int:
    out = 0
    for source_coord, target_coord in enumerate(permutation):
        if (int(mask) >> target_coord) & 1:
            out |= 1 << source_coord
    return out


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_external_w24_code(w24_artifact: dict[str, Any]) -> set[int]:
    return span_from_basis_masks([int(mask) for mask in w24_artifact["golay_code"]["generator_basis_masks"]])


def build_five_octad_lookup(octads: list[int]) -> dict[int, int]:
    lookup: dict[int, int] = {}
    for octad in octads:
        for subset in itertools.combinations(coordinates(octad), 5):
            key = sum(1 << coord for coord in subset)
            previous = lookup.get(key)
            if previous is not None and previous != octad:
                raise ValueError("five-subset octad lookup is not unique")
            lookup[key] = octad
    return lookup


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "permutation_vector",
        "inverse_permutation_vector",
        "replay_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def find_coordinate_map(source_code: set[int], target_code: set[int]) -> tuple[tuple[int, ...], int]:
    source_octads = sorted(mask for mask in source_code if mask.bit_count() == 8)
    target_octads = sorted(mask for mask in target_code if mask.bit_count() == 8)
    source_five = build_five_octad_lookup(source_octads)
    target_five = build_five_octad_lookup(target_octads)
    search_nodes = 0

    def propagate(permutation: list[int], inverse: list[int]) -> tuple[bool, list[tuple[tuple[int, ...], tuple[int, ...]]]]:
        changed = True
        branch_constraints: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        while changed:
            changed = False
            assigned = [coord for coord, image in enumerate(permutation) if image >= 0]
            if len(assigned) < 5:
                return True, []
            branch_constraints = []
            for subset in itertools.combinations(assigned, 5):
                source_key = sum(1 << coord for coord in subset)
                source_octad = source_five[source_key]
                target_key = sum(1 << permutation[coord] for coord in subset)
                target_octad = target_five[target_key]
                target_inside = set(coordinates(target_octad))
                source_remaining: list[int] = []
                for coord in coordinates(source_octad):
                    image = permutation[coord]
                    if image >= 0:
                        if image not in target_inside:
                            return False, []
                    else:
                        source_remaining.append(coord)
                for target_coord in target_inside:
                    source_coord = inverse[target_coord]
                    if source_coord >= 0 and not ((source_octad >> source_coord) & 1):
                        return False, []
                target_remaining = [coord for coord in target_inside if inverse[coord] < 0]
                if len(source_remaining) != len(target_remaining):
                    return False, []
                if len(source_remaining) == 1:
                    source_coord = source_remaining[0]
                    target_coord = target_remaining[0]
                    if permutation[source_coord] >= 0 and permutation[source_coord] != target_coord:
                        return False, []
                    if inverse[target_coord] >= 0 and inverse[target_coord] != source_coord:
                        return False, []
                    permutation[source_coord] = target_coord
                    inverse[target_coord] = source_coord
                    changed = True
                    break
                if len(source_remaining) > 1:
                    branch_constraints.append((tuple(source_remaining), tuple(target_remaining)))
        return True, branch_constraints

    def choose_unassigned(permutation: list[int], inverse: list[int]) -> tuple[int, list[int]]:
        for coord, image in enumerate(permutation):
            if image < 0:
                return coord, [target_coord for target_coord, source_coord in enumerate(inverse) if source_coord < 0]
        return -1, []

    def dfs(permutation: list[int], inverse: list[int]) -> tuple[int, ...] | None:
        nonlocal search_nodes
        search_nodes += 1
        ok, branch_constraints = propagate(permutation, inverse)
        if not ok:
            return None
        if all(image >= 0 for image in permutation):
            candidate = tuple(permutation)
            if {map_mask(mask, candidate) for mask in source_code} == target_code:
                return candidate
            return None
        unique_constraints: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        seen: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
        for source_remaining, target_remaining in branch_constraints:
            key = (source_remaining, target_remaining)
            if key not in seen:
                seen.add(key)
                unique_constraints.append(key)
        if unique_constraints:
            source_remaining, target_remaining = min(
                unique_constraints,
                key=lambda item: (len(item[0]), item[0], item[1]),
            )
            source_coord = source_remaining[0]
            target_candidates = list(target_remaining)
        else:
            source_coord, target_candidates = choose_unassigned(permutation, inverse)
        for target_coord in target_candidates:
            if inverse[target_coord] >= 0:
                continue
            next_permutation = permutation[:]
            next_inverse = inverse[:]
            next_permutation[source_coord] = target_coord
            next_inverse[target_coord] = source_coord
            result = dfs(next_permutation, next_inverse)
            if result is not None:
                return result
        return None

    initial_permutation = [-1] * 24
    initial_inverse = [-1] * 24
    for coord in range(5):
        initial_permutation[coord] = coord
        initial_inverse[coord] = coord
    result = dfs(initial_permutation, initial_inverse)
    if result is None:
        raise ValueError("no coordinate map found")
    return result, search_nodes


def build_rows() -> dict[str, Any]:
    long_rm13 = load_json(LONG_RM13_REPORT)
    long_k23merge = load_json(LONG_K23MERGE_REPORT)
    w24_report = load_json(W24_REPORT)
    w24_artifact = load_json(W24_ARTIFACT)
    source_code = {vector_mask(vector) for vector in build_source_code()["G24"]}
    target_code = build_external_w24_code(w24_artifact)
    source_octads = sorted(mask for mask in source_code if mask.bit_count() == 8)
    target_octads = sorted(mask for mask in target_code if mask.bit_count() == 8)
    permutation, search_nodes = find_coordinate_map(source_code, target_code)
    inverse_permutation = [0] * 24
    for source_coord, target_coord in enumerate(permutation):
        inverse_permutation[target_coord] = source_coord
    mapped_source = {map_mask(mask, permutation) for mask in source_code}
    map_rows = [
        {
            "source_coord": source_coord,
            "target_coord": target_coord,
            "source_singleton_mask": 1 << source_coord,
            "target_singleton_mask": 1 << target_coord,
        }
        for source_coord, target_coord in enumerate(permutation)
    ]
    replay_rows = []
    for raw in read_csv_rows(LONG_K23MERGE_IMAGE_ROWS):
        external_mask = int(raw["image_mask"])
        source_mask = preimage_mask(external_mask, permutation)
        replay_rows.append(
            {
                "word_id": int(raw["word_id"]),
                "external_mask": external_mask,
                "external_weight": external_mask.bit_count(),
                "source_preimage_mask": source_mask,
                "source_preimage_weight": source_mask.bit_count(),
                "external_w24_member_flag": int(external_mask in target_code),
                "source_endpoint_member_flag": int(source_mask in source_code),
                "remap_matches_external_flag": int(map_mask(source_mask, permutation) == external_mask),
            }
        )
    obs = {
        "long_rm13_certified_flag": int(
            long_rm13.get("status") == "RM13_SOURCE_TO_K23_W24_COORDINATE_SEAM_CERTIFIED"
            and long_rm13.get("all_checks_pass") is True
        ),
        "long_k23merge_certified_flag": int(
            long_k23merge.get("status") == "SECTOR33_K23_ACTIVE_MERGE_W24_RANK2_SUBCODE_CERTIFIED"
            and long_k23merge.get("all_checks_pass") is True
        ),
        "external_w24_certified_flag": int(
            w24_report.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
            and w24_report.get("all_checks_pass") is True
        ),
        "source_code_size": len(source_code),
        "target_code_size": len(target_code),
        "source_octad_count": len(source_octads),
        "target_octad_count": len(target_octads),
        "five_subset_lookup_count": len(build_five_octad_lookup(source_octads)),
        "fixed_prefix_coordinate_count": 5,
        "search_node_count": search_nodes,
        "coordinate_map_length": len(permutation),
        "coordinate_map_bijective_flag": int(sorted(permutation) == list(range(24))),
        "mapped_source_code_size": len(mapped_source),
        "mapped_source_target_intersection_count": len(mapped_source & target_code),
        "mapped_source_target_symmetric_difference_count": len(mapped_source ^ target_code),
        "coordinate_conjugacy_materialized_flag": int(mapped_source == target_code),
        "k23_image_word_count": len(replay_rows),
        "k23_image_external_member_count": sum(row["external_w24_member_flag"] for row in replay_rows),
        "k23_image_source_preimage_member_count": sum(row["source_endpoint_member_flag"] for row in replay_rows),
        "nonzero_k23_image_source_preimage_member_count": sum(
            int(row["source_preimage_mask"] != 0 and row["source_endpoint_member_flag"]) for row in replay_rows
        ),
        "k23_image_remap_match_count": sum(row["remap_matches_external_flag"] for row in replay_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    permutation_vector = np.asarray(permutation, dtype=np.int64)
    inverse_permutation_vector = np.asarray(inverse_permutation, dtype=np.int64)
    replay_table = table_from_rows(REPLAY_COLUMNS, replay_rows)
    observable_vector = np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64)
    matrix_payload = {
        "permutation_vector": permutation_vector,
        "inverse_permutation_vector": inverse_permutation_vector,
        "replay_table": replay_table,
        "observable_vector": observable_vector,
    }
    return {
        "long_rm13": long_rm13,
        "long_k23merge": long_k23merge,
        "w24_report": w24_report,
        "w24_artifact": w24_artifact,
        "source_code": source_code,
        "target_code": target_code,
        "map_rows": map_rows,
        "replay_rows": replay_rows,
        "obs_rows": obs_rows,
        "map_table": table_from_rows(MAP_COLUMNS, map_rows),
        "replay_table": replay_table,
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "permutation": permutation,
        "inverse_permutation": tuple(inverse_permutation),
        "map_text_hash": hashlib.sha256(digest_text(MAP_COLUMNS, map_rows).encode("ascii")).hexdigest(),
        "replay_text_hash": hashlib.sha256(digest_text(REPLAY_COLUMNS, replay_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_rm13_certified_flag"],
            obs["long_k23merge_certified_flag"],
            obs["external_w24_certified_flag"],
        )
        == (1, 1, 1),
        "source_and_target_have_golay_size": (
            obs["source_code_size"],
            obs["target_code_size"],
            obs["source_octad_count"],
            obs["target_octad_count"],
        )
        == (4096, 4096, 759, 759),
        "design_extension_search_materialized_map": (
            obs["five_subset_lookup_count"],
            obs["fixed_prefix_coordinate_count"],
            obs["search_node_count"],
            obs["coordinate_map_length"],
            obs["coordinate_map_bijective_flag"],
        )
        == (42504, 5, 77, 24, 1),
        "mapped_source_equals_target": (
            obs["mapped_source_code_size"],
            obs["mapped_source_target_intersection_count"],
            obs["mapped_source_target_symmetric_difference_count"],
            obs["coordinate_conjugacy_materialized_flag"],
        )
        == (4096, 4096, 0, 1),
        "k23_image_replays_to_source_endpoint": (
            obs["k23_image_word_count"],
            obs["k23_image_external_member_count"],
            obs["k23_image_source_preimage_member_count"],
            obs["nonzero_k23_image_source_preimage_member_count"],
            obs["k23_image_remap_match_count"],
        )
        == (4, 4, 4, 3, 4),
        "broader_goal_remains_open": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "rm13_source_to_w24_coordinate_map",
        "summary": obs,
        "permutation": list(rows["permutation"]),
        "inverse_permutation": list(rows["inverse_permutation"]),
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies one explicit coordinate map from the RM(1,3)-built source endpoint to the current W24 row alphabetization and replays the K23 rank-2 image through that map.",
    }
    seam_payload = {
        "schema": "long.rm13map.seam@1",
        "status": STATUS,
        "claim": "The previous RM13 coordinate seam is materialized by an explicit 24-coordinate map, and all four K23 image words replay into the source endpoint under its inverse.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_rm13": input_entry(
            LONG_RM13_REPORT,
            {
                "status": rows["long_rm13"].get("status"),
                "certificate_sha256": rows["long_rm13"].get("certificate_sha256"),
            },
        ),
        "long_k23merge": input_entry(
            LONG_K23MERGE_REPORT,
            {
                "status": rows["long_k23merge"].get("status"),
                "certificate_sha256": rows["long_k23merge"].get("certificate_sha256"),
            },
        ),
        "long_k23merge_image_rows": input_entry(LONG_K23MERGE_IMAGE_ROWS),
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
        "source_constructor": input_entry(SOURCE_SCRIPT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.rm13map.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_rm13map certifies an explicit coordinate map from the RM(1,3)-built source endpoint to the current W24 target and replays the K23 rank-2 image through that map.",
        "stage_protocol": {
            "draft": "read long_rm13, long_k23merge, source constructor, and the certified W24 row alphabetization",
            "witness": "emit coordinate-map rows, K23 replay rows, observables, and permutation matrices",
            "coherence": "check five-subset octad propagation, map bijectivity, full code equality, and replay membership",
            "closure": "certify the coordinate map and K23 replay without claiming full K23/W24 equality or M23 action",
            "emit": "write long_rm13map artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "map_rows_csv": relpath(OUT_DIR / "map_rows.csv"),
            "replay_rows_csv": relpath(OUT_DIR / "replay_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "rm13map_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "one explicit source-coordinate to target-coordinate permutation",
                "the permutation maps all 4096 source endpoint words onto the current W24 target",
                "the inverse permutation maps all four long_k23merge image words into the source endpoint",
                "the three nonzero K23 image words are source-endpoint words after coordinate transport",
            ],
            "does_not_certify": [
                "uniqueness of the coordinate map",
                "a full K23 rowspace equality with W24/Euler-punctured syzygies",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Use the certified coordinate map to lift the K23 rank-2 image into a source-side syzygy frame, then test whether the remaining K23 basis vectors extend to a rank-12 W24 image or hit a certified obstruction.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.rm13map.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.rm13map.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "map_csv": csv_text(MAP_COLUMNS, rows["map_rows"]),
        "replay_csv": csv_text(REPLAY_COLUMNS, rows["replay_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "map_table": rows["map_table"],
        "replay_table": rows["replay_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "map_text_sha256": rows["map_text_hash"],
            "replay_text_sha256": rows["replay_text_hash"],
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
    (OUT_DIR / "map_rows.csv").write_text(payloads["map_csv"], encoding="utf-8")
    (OUT_DIR / "replay_rows.csv").write_text(payloads["replay_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        map_table=payloads["map_table"],
        replay_table=payloads["replay_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "rm13map_matrices.npz", **payloads["matrix_payload"])
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
                "permutation": report["witness"]["permutation"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
