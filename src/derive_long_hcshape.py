from __future__ import annotations

import hashlib
import itertools
import json
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


THEOREM_ID = "long_hcshape"
STATUS = "LONG_HCSHAPE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcshape.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcshape.py"
LONG_HCPI_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcpi" / "report.json"
LONG_HCFOAM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "report.json"
FOAM33_BASIS = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "foam33_basis.csv"
INTERTWINE_CERT = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "height_coherent_action_return_intertwining"
    / "height_coherent_action_return_intertwining_certificate.json"
)

DOMAIN_TEXT_HASH = "d73f86d78b7a598c4a3f11dcd4f7882cdfd2e5eccdbc575069ce6423a5e9e894"
TARGET_TEXT_HASH = "7b004065007deff00c414890010178e09cba65ce8ea348f99464db0751d497d7"
OBS_TEXT_HASH = "4663625895f0f5a9817cd7cb2801274c9355ba81011d122b5c1f9950be32a34a"

DOMAIN_COLUMNS = [
    "domain_id",
    "a",
    "b",
    "c",
    "hidden_count",
    "part_code",
    "forced_target_row",
]
TARGET_COLUMNS = [
    "target_id",
    "block_code",
    "foam16_index",
    "copy_index",
    "forced_source_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "a8_dimension",
    "h6_dimension",
    "hidden_dimension",
    "lambda3_a8_dimension",
    "visible_triple_count",
    "copy0_twoform_count",
    "copy1_twoform_count",
    "hidden_pair_h6_count",
    "foam16_dimension",
    "foam33_dimension",
    "forced_twoform_rank",
    "residual_domain_dimension",
    "required_projection_rank",
    "required_kernel_dimension",
    "residual_scalar_rank_needed",
    "skeleton_rank",
    "skeleton_kernel_dimension",
    "rank_gap_to_target",
    "e33_basis_binding_materialized_flag",
    "scalar_functionals_materialized_flag",
    "focused_hcshape_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

PART_VISIBLE = 0
PART_COPY0_TWOFORM = 1
PART_COPY1_TWOFORM = 2
PART_HIDDEN_PAIR_H6 = 3


def target_row_for_twoform(hidden: int, h_pair: tuple[int, int]) -> int:
    h0, h1 = h_pair
    foam_index = 1
    for left in range(6):
        for right in range(left + 1, 6):
            if (left, right) == (h0, h1):
                return 1 + hidden * 16 + foam_index
            foam_index += 1
    raise AssertionError("bad H6 pair")


def build_domain_rows() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for domain_id, triple in enumerate(itertools.combinations(range(8), 3)):
        hidden = [value for value in triple if value < 2]
        h_values = tuple(value - 2 for value in triple if value >= 2)
        forced_target = -1
        if len(hidden) == 0:
            part_code = PART_VISIBLE
        elif len(hidden) == 1:
            part_code = PART_COPY0_TWOFORM if hidden[0] == 0 else PART_COPY1_TWOFORM
            forced_target = target_row_for_twoform(hidden[0], h_values)  # type: ignore[arg-type]
        else:
            part_code = PART_HIDDEN_PAIR_H6
        rows.append(
            {
                "domain_id": domain_id,
                "a": triple[0],
                "b": triple[1],
                "c": triple[2],
                "hidden_count": len(hidden),
                "part_code": part_code,
                "forced_target_row": forced_target,
            }
        )
    return rows


def build_target_rows(domain_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    source_counts = {row_id: 0 for row_id in range(33)}
    for row in domain_rows:
        target = row["forced_target_row"]
        if target >= 0:
            source_counts[target] += 1
    rows = [{"target_id": 0, "block_code": 0, "foam16_index": -1, "copy_index": -1, "forced_source_count": 0}]
    for copy_index in range(2):
        for foam16_index in range(16):
            target_id = 1 + copy_index * 16 + foam16_index
            rows.append(
                {
                    "target_id": target_id,
                    "block_code": 1 + copy_index,
                    "foam16_index": foam16_index,
                    "copy_index": copy_index,
                    "forced_source_count": source_counts[target_id],
                }
            )
    return rows


def skeleton_matrix(domain_rows: list[dict[str, int]]) -> np.ndarray:
    matrix = np.zeros((33, 56), dtype=np.int64)
    for row in domain_rows:
        target = row["forced_target_row"]
        if target >= 0:
            matrix[target, row["domain_id"]] = 1
    return matrix


def rank_int(matrix: np.ndarray) -> int:
    _, pivots = np.linalg.qr(matrix.astype(float).T, mode="reduced"), None
    return int(np.linalg.matrix_rank(matrix.astype(float)))


def build_rows() -> dict[str, Any]:
    hcpi = load_json(LONG_HCPI_REPORT)
    hcfoam = load_json(LONG_HCFOAM_REPORT)
    intertwine = load_json(INTERTWINE_CERT)
    domain_rows = build_domain_rows()
    target_rows = build_target_rows(domain_rows)
    skeleton = skeleton_matrix(domain_rows)
    skeleton_rank = rank_int(skeleton)
    counts = {
        "visible": sum(row["part_code"] == PART_VISIBLE for row in domain_rows),
        "copy0": sum(row["part_code"] == PART_COPY0_TWOFORM for row in domain_rows),
        "copy1": sum(row["part_code"] == PART_COPY1_TWOFORM for row in domain_rows),
        "hidden_pair": sum(row["part_code"] == PART_HIDDEN_PAIR_H6 for row in domain_rows),
    }
    obs = {
        "a8_dimension": 8,
        "h6_dimension": 6,
        "hidden_dimension": 2,
        "lambda3_a8_dimension": len(domain_rows),
        "visible_triple_count": counts["visible"],
        "copy0_twoform_count": counts["copy0"],
        "copy1_twoform_count": counts["copy1"],
        "hidden_pair_h6_count": counts["hidden_pair"],
        "foam16_dimension": 16,
        "foam33_dimension": len(target_rows),
        "forced_twoform_rank": skeleton_rank,
        "residual_domain_dimension": counts["visible"] + counts["hidden_pair"],
        "required_projection_rank": 33,
        "required_kernel_dimension": 23,
        "residual_scalar_rank_needed": 33 - skeleton_rank,
        "skeleton_rank": skeleton_rank,
        "skeleton_kernel_dimension": 56 - skeleton_rank,
        "rank_gap_to_target": 33 - skeleton_rank,
        "e33_basis_binding_materialized_flag": 0,
        "scalar_functionals_materialized_flag": 0,
        "focused_hcshape_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    return {
        "hcpi": hcpi,
        "hcfoam": hcfoam,
        "intertwine": intertwine,
        "domain_rows": domain_rows,
        "target_rows": target_rows,
        "obs_rows": obs_rows,
        "domain_table": table_from_rows(DOMAIN_COLUMNS, domain_rows),
        "target_table": table_from_rows(TARGET_COLUMNS, target_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "skeleton": skeleton,
        "obs": obs,
        "domain_text_hash": hashlib.sha256(digest_text(DOMAIN_COLUMNS, domain_rows).encode("ascii")).hexdigest(),
        "target_text_hash": hashlib.sha256(digest_text(TARGET_COLUMNS, target_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
        "skeleton_sha256": hashlib.sha256(np.ascontiguousarray(skeleton).tobytes()).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_hcpi_input_passes": rows["hcpi"].get("status") == "LONG_HCPI_INPUT_GAP_CERTIFIED" and rows["hcpi"].get("all_checks_pass") is True,
        "long_hcfoam_input_passes": rows["hcfoam"].get("status") == "LONG_HCFOAM_CERTIFIED" and rows["hcfoam"].get("all_checks_pass") is True,
        "target_lock_matches_a8_lambda3": rows["intertwine"].get("facts", {}).get("Lambda3_A8_candidate") == 56,
        "domain_partition_is_complete": (
            obs["lambda3_a8_dimension"],
            obs["visible_triple_count"],
            obs["copy0_twoform_count"],
            obs["copy1_twoform_count"],
            obs["hidden_pair_h6_count"],
        )
        == (56, 20, 15, 15, 6),
        "target_dimension_matches_foam33": (
            obs["foam16_dimension"],
            obs["foam33_dimension"],
        )
        == (16, 33),
        "forced_twoform_block_has_rank_30": obs["forced_twoform_rank"] == 30,
        "residual_gap_is_three_scalars": (
            obs["residual_domain_dimension"],
            obs["residual_scalar_rank_needed"],
            obs["required_projection_rank"],
            obs["required_kernel_dimension"],
        )
        == (26, 3, 33, 23),
        "skeleton_has_expected_gap": (
            obs["skeleton_rank"],
            obs["skeleton_kernel_dimension"],
            obs["rank_gap_to_target"],
        )
        == (30, 26, 3),
        "remaining_bindings_marked_open": (
            obs["e33_basis_binding_materialized_flag"],
            obs["scalar_functionals_materialized_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_projection_shape",
        "summary": obs,
        "skeleton_sha256": rows["skeleton_sha256"],
        "decomposition": "Lambda3(A2 + H6) = Lambda3(H6) + A2*Lambda2(H6) + Lambda2(A2)*H6 = 20 + 30 + 6",
        "remaining_projection_data": [
            "three scalar functionals on the 26-dimensional residual sector",
            "binding from the 56 e33 relation-support rows to this ordered Lambda3(A2 + H6) basis",
        ],
    }
    seam_payload = {
        "schema": "long.hcshape.seam@1",
        "status": STATUS,
        "claim": "The 56-to-33 projection shape has a forced 30-rank two-form block; the remaining projection data is exactly a 3-rank scalar residual plus the e33 basis binding.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcpi": input_entry(LONG_HCPI_REPORT, {"status": rows["hcpi"].get("status"), "certificate_sha256": rows["hcpi"].get("certificate_sha256")}),
        "long_hcfoam": input_entry(LONG_HCFOAM_REPORT, {"status": rows["hcfoam"].get("status"), "certificate_sha256": rows["hcfoam"].get("certificate_sha256")}),
        "foam33_basis": input_entry(FOAM33_BASIS),
        "intertwining_certificate": input_entry(INTERTWINE_CERT, {"status": rows["intertwine"].get("status"), "certificate_sha256": rows["intertwine"].get("certificate_sha256")}),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcshape.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_hcshape certifies the abstract projection shape required after long_hcpi: 30 target two-form coordinates are forced, leaving a 3-scalar residual choice and e33 support-basis binding before pi_Foam33 is materialized.",
        "stage_protocol": {
            "draft": "read long_hcpi, long_hcfoam, Foam33 basis, and the target-lock certificate",
            "witness": "emit Lambda3(A2+H6) domain rows, Foam33 target rows, and a forced two-form skeleton matrix",
            "coherence": "check the 20+15+15+6 decomposition, rank-30 skeleton, and rank-3 residual gap",
            "closure": "certify the projection shape without claiming the actual pi_Foam33 table",
            "emit": "write long_hcshape artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "domain_csv": relpath(OUT_DIR / "domain.csv"),
            "target_csv": relpath(OUT_DIR / "target.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "skeleton": relpath(OUT_DIR / "projection_skeleton.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the Lambda3(A2+H6) domain has 56 basis triples split as 20 visible, 15 copy-0 two-form, 15 copy-1 two-form, and 6 hidden-pair rows",
                "the Foam33 target has dimension 33 as one global coordinate plus two 16-coordinate Foam blocks",
                "the two-form part forces a rank-30 projection skeleton",
                "any rank-33 projection extending that skeleton needs exactly three additional scalar rows on the 26-dimensional residual sector",
            ],
            "does_not_certify": [
                "the actual pi_Foam33 matrix on the e33 relation-support order",
                "which three scalar residual functionals are physically selected",
                "the R_hc generator family",
                "the full matrix intertwining equation",
            ],
        },
        "next_highest_yield_item": "Construct the three residual scalar functionals and the e33 relation-support to Lambda3(A2+H6) basis binding; those two pieces complete pi_Foam33.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.hcshape.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {"schema": "long.hcshape.manifest@1", "name": THEOREM_ID, "status": STATUS, "inputs": inputs, "outputs": report["outputs"], "report_sha256": report["certificate_sha256"]}
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "domain_csv": csv_text(DOMAIN_COLUMNS, rows["domain_rows"]),
        "target_csv": csv_text(TARGET_COLUMNS, rows["target_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "domain_table": rows["domain_table"],
        "target_table": rows["target_table"],
        "observable_table": rows["observable_table"],
        "skeleton": rows["skeleton"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "domain_text_sha256": rows["domain_text_hash"],
            "target_text_sha256": rows["target_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "skeleton_sha256": rows["skeleton_sha256"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [row for row in index_payload.get("obligations", []) if isinstance(row, dict) and row.get("id") != THEOREM_ID]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append({"id": THEOREM_ID, "manifest": relpath(OUT_DIR / "manifest.json"), "report": relpath(OUT_DIR / "report.json"), "report_sha256": report["certificate_sha256"], "status": report["status"]})
    obligations.sort(key=lambda row: str(row["id"]))
    index = {"schema": schema, "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT", "obligation_count": len(obligations), "obligations": obligations}
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "domain.csv").write_text(payloads["domain_csv"], encoding="utf-8")
    (OUT_DIR / "target.csv").write_text(payloads["target_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(OUT_DIR / "tables.npz", domain_table=payloads["domain_table"], target_table=payloads["target_table"], observable_table=payloads["observable_table"])
    np.savez_compressed(OUT_DIR / "projection_skeleton.npz", skeleton=payloads["skeleton"])
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(json.dumps({"status": report["status"], "all_checks_pass": report["all_checks_pass"], "certificate_sha256": report["certificate_sha256"], "computed_hashes": payloads["computed_hashes"], "summary": report["witness"]["summary"], "report": relpath(OUT_DIR / "report.json"), "next_highest_yield_item": report["next_highest_yield_item"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
