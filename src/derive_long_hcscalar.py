from __future__ import annotations

import csv
import hashlib
import json
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


THEOREM_ID = "long_hcscalar"
STATUS = "LONG_HCSCALAR_ABSTRACT_COMPLETION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcscalar.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcscalar.py"
LONG_HCSHAPE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcshape" / "report.json"
LONG_HCSHAPE_DOMAIN = D20_INVARIANTS / "proof_obligations" / "long_hcshape" / "domain.csv"
LONG_HCSHAPE_SKELETON = D20_INVARIANTS / "proof_obligations" / "long_hcshape" / "projection_skeleton.npz"
SELECTOR_MARKING = ROOT / "data" / "selectors" / "wu_spinh_6j_marking.json"
INTERTWINE_CERT = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "height_coherent_action_return_intertwining"
    / "height_coherent_action_return_intertwining_certificate.json"
)

SCALAR_TEXT_HASH = "66a33c20342756c68f1b6b599065563750c2600d752253d69b2d81f3ef52fef8"
OBS_TEXT_HASH = "60a6c5d9cfe24b637850e54fd37c9c57620c59a74a6be9e5aba27db4fbcb23e1"
PI_CANDIDATE_SHA256 = "c2acf9003d46a25014307deed107cbbacd05e6a9ca10b31a677034147a384d15"
SCALAR_MATRIX_SHA256 = "dd2120ed84e61ef2585cb3aad4a776b3f92b95793e347c5020ca9343662849b2"

SCALAR_COLUMNS = [
    "scalar_id",
    "target_row",
    "functional_code",
    "source_part_code",
    "h6_index",
    "support_count",
    "domain_id_min",
    "domain_id_max",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "h6_label_count",
    "active_object_count",
    "active_object_0_h6_index",
    "active_object_1_h6_index",
    "source_domain_dimension",
    "target_dimension",
    "skeleton_rank",
    "skeleton_kernel_dimension",
    "residual_domain_dimension",
    "scalar_row_count",
    "scalar_rank_addition",
    "candidate_projection_rank",
    "candidate_kernel_dimension",
    "visible_volume_support_count",
    "active_hidden_support_count",
    "forced_twoform_block_preserved_flag",
    "selector_scalar_coordinate_flag",
    "e33_basis_binding_materialized_flag",
    "r_hc_materialized_flag",
    "full_intertwiner_claim_flag",
    "focused_hcscalar_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

PART_VISIBLE = 0
PART_COPY0_TWOFORM = 1
PART_COPY1_TWOFORM = 2
PART_HIDDEN_PAIR_H6 = 3

FUNCTION_VISIBLE_VOLUME = 0
FUNCTION_ACTIVE_COPY0 = 1
FUNCTION_ACTIVE_COPY1 = 2

TARGET_GLOBAL = 0
TARGET_COPY0_SCALAR = 1
TARGET_COPY1_SCALAR = 17


def read_int_csv(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [{key: int(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def rank_mod(matrix: np.ndarray, prime: int = 1_000_003) -> int:
    work = np.asarray(matrix, dtype=np.int64) % prime
    rows, cols = work.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if int(work[row, col]) % prime:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            work[[rank, pivot]] = work[[pivot, rank]]
        inv = pow(int(work[rank, col]), -1, prime)
        work[rank] = (work[rank] * inv) % prime
        for row in range(rows):
            if row == rank:
                continue
            factor = int(work[row, col]) % prime
            if factor:
                work[row] = (work[row] - factor * work[rank]) % prime
        rank += 1
        if rank == rows:
            break
    return rank


def load_marking() -> tuple[list[str], dict[str, int]]:
    payload = load_json(SELECTOR_MARKING)
    bridge = payload.get("spin12_6j_bridge", {})
    labels = list(bridge.get("H6_labels", []))
    coordinate_map = bridge.get("big_cell_coordinate_map", [])
    scalar_coordinates = [row.get("coordinate") for row in coordinate_map if row.get("type") == "scalar"]
    twoform_count = sum(1 for row in coordinate_map if row.get("type") == "two_form")
    facts = {
        "scalar_coordinate_count": len(scalar_coordinates),
        "scalar_coordinate": int(scalar_coordinates[0]) if scalar_coordinates else -1,
        "twoform_coordinate_count": twoform_count,
        "foam_big_cell_dimension": int(bridge.get("foam_big_cell_dimension", 0)),
    }
    return labels, facts


def scalar_support(domain_rows: list[dict[str, int]], part_code: int, h6_index: int) -> list[int]:
    support: list[int] = []
    for row in domain_rows:
        if row["part_code"] != part_code:
            continue
        if part_code == PART_HIDDEN_PAIR_H6 and row["c"] - 2 != h6_index:
            continue
        support.append(row["domain_id"])
    return support


def build_scalar_rows(domain_rows: list[dict[str, int]], h6_labels: list[str], active_objects: list[str]) -> list[dict[str, int]]:
    active_indices = [h6_labels.index(label) for label in active_objects]
    visible_support = scalar_support(domain_rows, PART_VISIBLE, -1)
    copy0_support = scalar_support(domain_rows, PART_HIDDEN_PAIR_H6, active_indices[0])
    copy1_support = scalar_support(domain_rows, PART_HIDDEN_PAIR_H6, active_indices[1])
    specs = [
        (TARGET_GLOBAL, FUNCTION_VISIBLE_VOLUME, PART_VISIBLE, -1, visible_support),
        (TARGET_COPY0_SCALAR, FUNCTION_ACTIVE_COPY0, PART_HIDDEN_PAIR_H6, active_indices[0], copy0_support),
        (TARGET_COPY1_SCALAR, FUNCTION_ACTIVE_COPY1, PART_HIDDEN_PAIR_H6, active_indices[1], copy1_support),
    ]
    rows = []
    for scalar_id, (target_row, code, part_code, h6_index, support) in enumerate(specs):
        rows.append(
            {
                "scalar_id": scalar_id,
                "target_row": target_row,
                "functional_code": code,
                "source_part_code": part_code,
                "h6_index": h6_index,
                "support_count": len(support),
                "domain_id_min": min(support),
                "domain_id_max": max(support),
            }
        )
    return rows


def build_candidate(skeleton: np.ndarray, scalar_rows: list[dict[str, int]], domain_rows: list[dict[str, int]]) -> tuple[np.ndarray, np.ndarray]:
    candidate = np.asarray(skeleton, dtype=np.int64).copy()
    scalar_matrix = np.zeros((len(scalar_rows), candidate.shape[1]), dtype=np.int64)
    domain_by_id = {row["domain_id"]: row for row in domain_rows}
    for row in scalar_rows:
        for domain_id, domain_row in domain_by_id.items():
            if domain_row["part_code"] != row["source_part_code"]:
                continue
            if row["source_part_code"] == PART_HIDDEN_PAIR_H6 and domain_row["c"] - 2 != row["h6_index"]:
                continue
            candidate[row["target_row"], domain_id] = 1
            scalar_matrix[row["scalar_id"], domain_id] = 1
    return candidate, scalar_matrix


def build_rows() -> dict[str, Any]:
    hcshape = load_json(LONG_HCSHAPE_REPORT)
    intertwine = load_json(INTERTWINE_CERT)
    domain_rows = read_int_csv(LONG_HCSHAPE_DOMAIN)
    h6_labels, marking_facts = load_marking()
    active_objects = list(intertwine.get("facts", {}).get("active_objects", []))
    scalar_rows = build_scalar_rows(domain_rows, h6_labels, active_objects)
    skeleton = np.asarray(np.load(LONG_HCSHAPE_SKELETON, allow_pickle=False)["skeleton"], dtype=np.int64)
    candidate, scalar_matrix = build_candidate(skeleton, scalar_rows, domain_rows)
    skeleton_rank = rank_mod(skeleton)
    candidate_rank = rank_mod(candidate)
    scalar_rank = candidate_rank - skeleton_rank
    obs = {
        "h6_label_count": len(h6_labels),
        "active_object_count": len(active_objects),
        "active_object_0_h6_index": h6_labels.index(active_objects[0]),
        "active_object_1_h6_index": h6_labels.index(active_objects[1]),
        "source_domain_dimension": len(domain_rows),
        "target_dimension": int(candidate.shape[0]),
        "skeleton_rank": skeleton_rank,
        "skeleton_kernel_dimension": int(candidate.shape[1] - skeleton_rank),
        "residual_domain_dimension": sum(row["part_code"] in (PART_VISIBLE, PART_HIDDEN_PAIR_H6) for row in domain_rows),
        "scalar_row_count": len(scalar_rows),
        "scalar_rank_addition": scalar_rank,
        "candidate_projection_rank": candidate_rank,
        "candidate_kernel_dimension": int(candidate.shape[1] - candidate_rank),
        "visible_volume_support_count": scalar_rows[0]["support_count"],
        "active_hidden_support_count": scalar_rows[1]["support_count"] + scalar_rows[2]["support_count"],
        "forced_twoform_block_preserved_flag": int(np.array_equal(candidate[2:17], skeleton[2:17]) and np.array_equal(candidate[18:33], skeleton[18:33])),
        "selector_scalar_coordinate_flag": int(marking_facts["scalar_coordinate_count"] == 1 and marking_facts["scalar_coordinate"] == 0),
        "e33_basis_binding_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "full_intertwiner_claim_flag": 0,
        "focused_hcscalar_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    return {
        "hcshape": hcshape,
        "intertwine": intertwine,
        "domain_rows": domain_rows,
        "h6_labels": h6_labels,
        "active_objects": active_objects,
        "marking_facts": marking_facts,
        "scalar_rows": scalar_rows,
        "obs_rows": obs_rows,
        "scalar_table": table_from_rows(SCALAR_COLUMNS, scalar_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "skeleton": skeleton,
        "candidate": candidate,
        "scalar_matrix": scalar_matrix,
        "obs": obs,
        "scalar_text_hash": hashlib.sha256(digest_text(SCALAR_COLUMNS, scalar_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
        "pi_candidate_sha256": sha_array(candidate),
        "scalar_matrix_sha256": sha_array(scalar_matrix),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_hcshape_input_passes": rows["hcshape"].get("status") == "LONG_HCSHAPE_CERTIFIED" and rows["hcshape"].get("all_checks_pass") is True,
        "target_lock_active_objects_are_source_bound": rows["active_objects"] == ["B+", "S+"],
        "selector_marking_has_six_channel_order": rows["h6_labels"] == ["B-", "B+", "V-", "V+", "S-", "S+"],
        "selector_marking_has_scalar_plus_twoforms": (
            rows["marking_facts"]["scalar_coordinate_count"],
            rows["marking_facts"]["scalar_coordinate"],
            rows["marking_facts"]["twoform_coordinate_count"],
            rows["marking_facts"]["foam_big_cell_dimension"],
        )
        == (1, 0, 15, 16),
        "scalar_rows_have_expected_support": (
            obs["scalar_row_count"],
            obs["visible_volume_support_count"],
            obs["active_hidden_support_count"],
        )
        == (3, 20, 2),
        "scalar_completion_has_required_rank": (
            obs["skeleton_rank"],
            obs["scalar_rank_addition"],
            obs["candidate_projection_rank"],
            obs["candidate_kernel_dimension"],
        )
        == (30, 3, 33, 23),
        "forced_twoform_block_is_preserved": obs["forced_twoform_block_preserved_flag"] == 1,
        "remaining_full_intertwiner_inputs_marked_open": (
            obs["e33_basis_binding_materialized_flag"],
            obs["r_hc_materialized_flag"],
            obs["full_intertwiner_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0),
    }
    scalar_details = [
        {
            "scalar_id": row["scalar_id"],
            "target_row": row["target_row"],
            "functional": ["visible_volume", "active_object_copy0", "active_object_copy1"][row["functional_code"]],
            "h6_label": None if row["h6_index"] < 0 else rows["h6_labels"][row["h6_index"]],
            "support_count": row["support_count"],
            "domain_id_min": row["domain_id_min"],
            "domain_id_max": row["domain_id_max"],
        }
        for row in rows["scalar_rows"]
    ]
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_scalar_completion",
        "summary": obs,
        "h6_labels": rows["h6_labels"],
        "active_objects": rows["active_objects"],
        "scalar_details": scalar_details,
        "pi_candidate_sha256": rows["pi_candidate_sha256"],
        "scalar_matrix_sha256": rows["scalar_matrix_sha256"],
        "boundary": "This is an abstract 33x56 completion on the ordered Lambda3(A2+H6) basis, not yet the e33 relation-support projection table.",
    }
    seam_payload = {
        "schema": "long.hcscalar.seam@1",
        "status": STATUS,
        "claim": "The residual rank-three scalar layer is source-bound by the stored six-channel marking and the active-object list, producing an abstract 33x56 rank-33 projection candidate with kernel 23.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcshape": input_entry(LONG_HCSHAPE_REPORT, {"status": rows["hcshape"].get("status"), "certificate_sha256": rows["hcshape"].get("certificate_sha256")}),
        "domain_csv": input_entry(LONG_HCSHAPE_DOMAIN),
        "skeleton": input_entry(LONG_HCSHAPE_SKELETON),
        "selector_marking": input_entry(SELECTOR_MARKING, {"status": load_json(SELECTOR_MARKING).get("status")}),
        "intertwining_certificate": input_entry(INTERTWINE_CERT, {"status": rows["intertwine"].get("status"), "certificate_sha256": rows["intertwine"].get("certificate_sha256")}),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcscalar.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_hcscalar certifies the sourced abstract scalar completion of long_hcshape: the public visible-volume scalar and the two active-object hidden-pair scalars raise the projection skeleton from rank 30 to rank 33 with kernel 23.",
        "stage_protocol": {
            "draft": "read long_hcshape, the six-channel selector marking, and the target-lock active-object list",
            "witness": "emit scalar rows, observable counts, and the abstract 33x56 projection candidate",
            "coherence": "check source label order, active-object indices, scalar support, rank 33, kernel 23, and preservation of the forced two-form block",
            "closure": "certify the abstract scalar completion without claiming the e33 relation-row projection or R_hc",
            "emit": "write long_hcscalar artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "scalar_rows_csv": relpath(OUT_DIR / "scalar_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "projection_candidate": relpath(OUT_DIR / "projection_candidate.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the stored six-channel order maps active objects B+ and S+ to H6 indices 1 and 5",
                "the three residual scalar rows have supports 20, 1, and 1 on the ordered Lambda3(A2+H6) domain",
                "the scalar rows extend the rank-30 skeleton to an abstract rank-33 projection candidate",
                "the candidate has the required 23-dimensional kernel and preserves the forced two-form block",
            ],
            "does_not_certify": [
                "the actual pi_Foam33 table on the e33 relation-support order",
                "a materialized R_hc generator family",
                "the full matrix intertwining equation",
                "broad bundle integration",
            ],
        },
        "next_highest_yield_item": "Bind the 56 e33 relation-support entries to the ordered Lambda3(A2+H6) domain; then derive R_hc generators and test the matrix identity.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.hcscalar.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {"schema": "long.hcscalar.manifest@1", "name": THEOREM_ID, "status": STATUS, "inputs": inputs, "outputs": report["outputs"], "report_sha256": report["certificate_sha256"]}
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "scalar_csv": csv_text(SCALAR_COLUMNS, rows["scalar_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "scalar_table": rows["scalar_table"],
        "observable_table": rows["observable_table"],
        "candidate": rows["candidate"],
        "scalar_matrix": rows["scalar_matrix"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "scalar_text_sha256": rows["scalar_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "pi_candidate_sha256": rows["pi_candidate_sha256"],
            "scalar_matrix_sha256": rows["scalar_matrix_sha256"],
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
    (OUT_DIR / "scalar_rows.csv").write_text(payloads["scalar_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(OUT_DIR / "tables.npz", scalar_table=payloads["scalar_table"], observable_table=payloads["observable_table"])
    np.savez_compressed(OUT_DIR / "projection_candidate.npz", pi_candidate=payloads["candidate"], scalar_matrix=payloads["scalar_matrix"])
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
