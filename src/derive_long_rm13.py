from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .generate_source import (
        TYPE_II_NEIGHBOR_ALPHA,
        TYPE_II_NEIGHBOR_BETA,
        TYPE_II_NEIGHBOR_GAMMA,
        make_C0,
        make_H8,
        neighbor,
        vec_from_one_based,
        weight_enumerator,
        wt,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from generate_source import (
        TYPE_II_NEIGHBOR_ALPHA,
        TYPE_II_NEIGHBOR_BETA,
        TYPE_II_NEIGHBOR_GAMMA,
        make_C0,
        make_H8,
        neighbor,
        vec_from_one_based,
        weight_enumerator,
        wt,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_rm13"
STATUS = "RM13_SOURCE_TO_K23_W24_COORDINATE_SEAM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_rm13.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rm13.py"
GENERATE_SOURCE_SCRIPT = ROOT / "src" / "generate_source.py"
LONG_K23MERGE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23merge" / "report.json"
LONG_K23MERGE_IMAGE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23merge" / "image_rows.csv"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_ARTIFACT = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

STAGE_TEXT_HASH = "93a09671ce74326006f1b8d963e719a986e05161e22d06b80ba024ad732b6853"
IMAGE_TEXT_HASH = "0bead6a533d67b397b9cb7fff06326d4da78be0dce63e12e9bb87171e2db7aee"
OBS_TEXT_HASH = "91eead8dcb4fcc9dcd2a0450fbb26566675b2fd9ccd5e96438702d0a6400b250"
MATRIX_SHA256 = "79d3d55ff224cf2f645a86c8b4e776100d2acc4aee09f6211db41919db581290"

STAGE_COLUMNS = [
    "stage_id",
    "stage_code",
    "code_size",
    "root_weight4_count",
    "min_nonzero_weight",
    "external_w24_intersection_count",
    "weight0_count",
    "weight4_count",
    "weight8_count",
    "weight12_count",
    "weight16_count",
    "weight20_count",
    "weight24_count",
]
IMAGE_COLUMNS = [
    "word_id",
    "image_mask",
    "image_weight",
    "external_w24_member_flag",
    "source_C0_member_flag",
    "source_alpha_member_flag",
    "source_beta_member_flag",
    "source_gamma_member_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23merge_certified_flag",
    "external_w24_certified_flag",
    "h8_size",
    "h8_dimension",
    "h8_weight4_count",
    "c0_size",
    "c0_root_weight4_count",
    "alpha_root_weight4_count",
    "beta_root_weight4_count",
    "gamma_root_weight4_count",
    "source_endpoint_min_nonzero_weight",
    "source_endpoint_external_w24_same_enumerator_flag",
    "source_endpoint_external_w24_identity_equal_flag",
    "source_endpoint_external_w24_intersection_count",
    "source_endpoint_external_w24_symmetric_difference_count",
    "k23merge_image_word_count",
    "k23merge_image_external_w24_member_count",
    "k23merge_image_source_C0_member_count",
    "k23merge_image_source_endpoint_member_count",
    "nonzero_k23merge_image_source_endpoint_member_count",
    "coordinate_conjugacy_materialized_flag",
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


def build_source_stages() -> list[tuple[str, list[tuple[int, ...]]]]:
    h8 = make_H8()
    code = make_C0(h8)
    stages = [("C0", code)]
    for name, support in [
        ("alpha", TYPE_II_NEIGHBOR_ALPHA),
        ("beta", TYPE_II_NEIGHBOR_BETA),
        ("gamma", TYPE_II_NEIGHBOR_GAMMA),
    ]:
        code = neighbor(code, vec_from_one_based(support))
        stages.append((name, code))
    return stages


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_external_w24_code(w24_artifact: dict[str, Any]) -> set[int]:
    return span_from_basis_masks([int(mask) for mask in w24_artifact["golay_code"]["generator_basis_masks"]])


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["stage_table", "image_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23merge = load_json(LONG_K23MERGE_REPORT)
    w24_report = load_json(W24_REPORT)
    w24_artifact = load_json(W24_ARTIFACT)
    external_w24 = build_external_w24_code(w24_artifact)
    h8 = make_H8()
    stages = build_source_stages()
    stage_sets = {name: {vector_mask(vector) for vector in code} for name, code in stages}
    source_endpoint = stage_sets["gamma"]
    stage_rows = []
    for stage_id, (name, code) in enumerate(stages):
        enum = weight_enumerator(code)
        nonzero_weights = [weight for weight, count in enum.items() if weight and count]
        stage_rows.append(
            {
                "stage_id": stage_id,
                "stage_code": stage_id,
                "code_size": len(code),
                "root_weight4_count": int(enum.get(4, 0)),
                "min_nonzero_weight": min(nonzero_weights) if nonzero_weights else 0,
                "external_w24_intersection_count": len(stage_sets[name] & external_w24),
                "weight0_count": int(enum.get(0, 0)),
                "weight4_count": int(enum.get(4, 0)),
                "weight8_count": int(enum.get(8, 0)),
                "weight12_count": int(enum.get(12, 0)),
                "weight16_count": int(enum.get(16, 0)),
                "weight20_count": int(enum.get(20, 0)),
                "weight24_count": int(enum.get(24, 0)),
            }
        )
    image_rows_raw = read_csv_rows(LONG_K23MERGE_IMAGE_ROWS)
    image_rows = []
    for raw in image_rows_raw:
        mask = int(raw["image_mask"])
        image_rows.append(
            {
                "word_id": int(raw["word_id"]),
                "image_mask": mask,
                "image_weight": int(raw["image_weight"]),
                "external_w24_member_flag": int(mask in external_w24),
                "source_C0_member_flag": int(mask in stage_sets["C0"]),
                "source_alpha_member_flag": int(mask in stage_sets["alpha"]),
                "source_beta_member_flag": int(mask in stage_sets["beta"]),
                "source_gamma_member_flag": int(mask in source_endpoint),
            }
        )
    source_endpoint_same_enum = Counter(mask.bit_count() for mask in source_endpoint) == Counter(
        mask.bit_count() for mask in external_w24
    )
    source_endpoint_intersection = len(source_endpoint & external_w24)
    obs = {
        "long_k23merge_certified_flag": int(
            long_k23merge.get("status") == "SECTOR33_K23_ACTIVE_MERGE_W24_RANK2_SUBCODE_CERTIFIED"
            and long_k23merge.get("all_checks_pass") is True
        ),
        "external_w24_certified_flag": int(
            w24_report.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
            and w24_report.get("all_checks_pass") is True
        ),
        "h8_size": len(h8),
        "h8_dimension": 4,
        "h8_weight4_count": int(weight_enumerator(h8).get(4, 0)),
        "c0_size": len(stages[0][1]),
        "c0_root_weight4_count": int(stage_rows[0]["root_weight4_count"]),
        "alpha_root_weight4_count": int(stage_rows[1]["root_weight4_count"]),
        "beta_root_weight4_count": int(stage_rows[2]["root_weight4_count"]),
        "gamma_root_weight4_count": int(stage_rows[3]["root_weight4_count"]),
        "source_endpoint_min_nonzero_weight": int(stage_rows[3]["min_nonzero_weight"]),
        "source_endpoint_external_w24_same_enumerator_flag": int(source_endpoint_same_enum),
        "source_endpoint_external_w24_identity_equal_flag": int(source_endpoint == external_w24),
        "source_endpoint_external_w24_intersection_count": source_endpoint_intersection,
        "source_endpoint_external_w24_symmetric_difference_count": len(source_endpoint ^ external_w24),
        "k23merge_image_word_count": len(image_rows),
        "k23merge_image_external_w24_member_count": sum(row["external_w24_member_flag"] for row in image_rows),
        "k23merge_image_source_C0_member_count": sum(row["source_C0_member_flag"] for row in image_rows),
        "k23merge_image_source_endpoint_member_count": sum(row["source_gamma_member_flag"] for row in image_rows),
        "nonzero_k23merge_image_source_endpoint_member_count": sum(
            int(row["image_mask"] != 0 and row["source_gamma_member_flag"]) for row in image_rows
        ),
        "coordinate_conjugacy_materialized_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "stage_table": table_from_rows(STAGE_COLUMNS, stage_rows),
        "image_table": table_from_rows(IMAGE_COLUMNS, image_rows),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23merge": long_k23merge,
        "w24_report": w24_report,
        "w24_artifact": w24_artifact,
        "stage_rows": stage_rows,
        "image_rows": image_rows,
        "obs_rows": obs_rows,
        "stage_table": matrix_payload["stage_table"],
        "image_table": matrix_payload["image_table"],
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "stage_text_hash": hashlib.sha256(digest_text(STAGE_COLUMNS, stage_rows).encode("ascii")).hexdigest(),
        "image_text_hash": hashlib.sha256(digest_text(IMAGE_COLUMNS, image_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (obs["long_k23merge_certified_flag"], obs["external_w24_certified_flag"]) == (1, 1),
        "rm13_source_shape_matches": (
            obs["h8_size"],
            obs["h8_dimension"],
            obs["h8_weight4_count"],
            obs["c0_size"],
        )
        == (16, 4, 14, 4096),
        "neighbor_root_sequence_matches": (
            obs["c0_root_weight4_count"],
            obs["alpha_root_weight4_count"],
            obs["beta_root_weight4_count"],
            obs["gamma_root_weight4_count"],
            obs["source_endpoint_min_nonzero_weight"],
        )
        == (42, 18, 6, 0, 8),
        "external_w24_same_enumerator_but_not_identity_order": (
            obs["source_endpoint_external_w24_same_enumerator_flag"],
            obs["source_endpoint_external_w24_identity_equal_flag"],
            obs["source_endpoint_external_w24_intersection_count"],
            obs["source_endpoint_external_w24_symmetric_difference_count"],
        )
        == (1, 0, 4, 8184),
        "k23merge_image_is_external_not_source_order": (
            obs["k23merge_image_word_count"],
            obs["k23merge_image_external_w24_member_count"],
            obs["k23merge_image_source_C0_member_count"],
            obs["k23merge_image_source_endpoint_member_count"],
            obs["nonzero_k23merge_image_source_endpoint_member_count"],
        )
        == (4, 4, 2, 1, 0),
        "coordinate_conjugacy_remains_open": (
            obs["coordinate_conjugacy_materialized_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "rm13_source_to_k23_w24_coordinate_seam",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the RM(1,3) source chain and the coordinate-order seam against the current W24 target used by K23; it does not materialize a conjugacy between the two W24 coordinate systems.",
    }
    seam_payload = {
        "schema": "long.rm13.seam@1",
        "status": STATUS,
        "claim": "The original RM(1,3) source chain is certified upstream, but the K23 rank-2 W24 image is expressed in the current external W24 row alphabetization, not in the source constructor's G24 coordinate order.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
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
        "source_constructor": input_entry(GENERATE_SOURCE_SCRIPT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.rm13.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_rm13 certifies that RM(1,3) is the upstream H8 source and records the open coordinate seam between the source G24 endpoint and the current W24 target used by K23.",
        "stage_protocol": {
            "draft": "read source constructor, long_k23merge, and the certified W24 row alphabetization",
            "witness": "emit source-stage rows, K23 image membership rows, observables, and matrices",
            "coherence": "check H8 shape, root-killing sequence, endpoint enumerator match, identity-order mismatch, and K23 image membership",
            "closure": "certify the source/target coordinate seam without claiming a materialized conjugacy",
            "emit": "write long_rm13 artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "stage_rows_csv": relpath(OUT_DIR / "stage_rows.csv"),
            "image_rows_csv": relpath(OUT_DIR / "image_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "rm13_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "H8 is the RM(1,3) [8,4] source with 14 weight-four words",
                "C0=H8^3 has 42 weight-four roots",
                "the Type-II neighbor root sequence is 42 -> 18 -> 6 -> 0",
                "the source endpoint and current W24 target have the same Golay weight enumerator but are not equal in identity coordinate order",
                "the nonzero long_k23merge image words are current-W24 words but are not source-endpoint words in identity coordinate order",
            ],
            "does_not_certify": [
                "a coordinate conjugacy between the source G24 endpoint and the current W24 row alphabetization",
                "a direct RM(1,3) subcode inside the current W24 target",
                "full K23 rowspace equality with the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Materialize a coordinate conjugacy between the source-constructor G24 endpoint and the current W24 row alphabetization, then replay the K23 rank-2 image through that conjugacy.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.rm13.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.rm13.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "stage_csv": csv_text(STAGE_COLUMNS, rows["stage_rows"]),
        "image_csv": csv_text(IMAGE_COLUMNS, rows["image_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "stage_table": rows["stage_table"],
        "image_table": rows["image_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "stage_text_sha256": rows["stage_text_hash"],
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
    (OUT_DIR / "stage_rows.csv").write_text(payloads["stage_csv"], encoding="utf-8")
    (OUT_DIR / "image_rows.csv").write_text(payloads["image_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        stage_table=payloads["stage_table"],
        image_table=payloads["image_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "rm13_matrices.npz", **payloads["matrix_payload"])
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
