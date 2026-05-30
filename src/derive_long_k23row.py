from __future__ import annotations

import csv
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


THEOREM_ID = "long_k23row"
STATUS = "SECTOR33_K23_SELECTED_W24_ROWSPACE_SUBCODE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23row.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23row.py"
LONG_K23OCT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23oct" / "report.json"
LONG_K23OCT_PLACEMENT = D20_INVARIANTS / "proof_obligations" / "long_k23oct" / "placement_rows.csv"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
DELETE_CONTRACT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_marked_delete_contract_shadow_probe"
    / "report.json"
)
SECTOR33_DUAL_REPORT = D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"

ROW_TEXT_HASH = "8be0b9b2acdb508112400adade62ee9610fd86be4da3385f25f6e60ce256d6ee"
WORD_TEXT_HASH = "936e01dd41b91bb61a4785f80a51040ffd1e935f9e5fb221ffe1f3985b88d3d6"
OBS_TEXT_HASH = "7b4e573e035929f7755846cc3e32cf7fc91b356eb5feb0d3aa529893ac1598e8"
MATRIX_SHA256 = "ff35a600c5399852e6bf06aedba7f2b0380660ba4088abca44fc8ad479a4cdab"

ROW_COLUMNS = [
    "row_id",
    "source_row_mask",
    "source_original_edge_mask",
    "source_support_count",
    "mapped_w24_mask",
    "mapped_weight",
    "in_w24_code_flag",
    "matches_target_octad_flag",
]
WORD_COLUMNS = [
    "word_id",
    "span_selector_mask",
    "mapped_w24_mask",
    "mapped_weight",
    "in_w24_code_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23oct_certified_flag",
    "w24_code_certified_flag",
    "sector33_dual_certified_flag",
    "delete_contract_input_certified_flag",
    "selected_record_id",
    "selected_extra_removed",
    "selected_effective_contract_count",
    "selected_remaining_column_count",
    "selected_source_rank",
    "mapped_basis_row_count",
    "mapped_nonzero_mask",
    "mapped_nonzero_weight",
    "target_octad_mask",
    "mapped_basis_in_w24_flag",
    "rowspace_word_count",
    "rowspace_rank",
    "rowspace_all_words_in_w24_flag",
    "rowspace_subcode_certified_flag",
    "rowspace_equals_w24_flag",
    "k23_equality_certified_flag",
    "full_morphism_certified_flag",
    "m23_module_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    return hashlib.sha256(
        b"".join(
            np.ascontiguousarray(payload[key]).tobytes()
            for key in ["source_row_matrix", "mapped_basis_vectors", "mapped_word_masks"]
        )
    ).hexdigest()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def span_masks(gens: list[int]) -> set[int]:
    out = {0}
    for gen in gens:
        out |= {word ^ gen for word in list(out)}
    return out


def rref_mod2(rows: list[list[int]], ncols: int) -> tuple[list[list[int]], list[int]]:
    work = [[int(value) & 1 for value in row] for row in rows]
    rank = 0
    pivots: list[int] = []
    for col in range(ncols):
        pivot = None
        for row in range(rank, len(work)):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for row in range(len(work)):
            if row != rank and work[row][col]:
                work[row] = [left ^ right for left, right in zip(work[row], work[rank])]
        pivots.append(col)
        rank += 1
        if rank == len(work):
            break
    return [row for row in work if any(row)], pivots


def delete_column(rows: list[list[int]], columns: list[int], original_element: int) -> tuple[list[list[int]], list[int]]:
    idx = columns.index(original_element)
    next_rows = [[value for col, value in enumerate(row) if col != idx] for row in rows]
    next_columns = [value for col, value in enumerate(columns) if col != idx]
    reduced, _pivots = rref_mod2(next_rows, len(next_columns))
    return reduced, next_columns


def contract_column(
    rows: list[list[int]],
    columns: list[int],
    original_element: int,
) -> tuple[list[list[int]], list[int], bool]:
    idx = columns.index(original_element)
    pivot = None
    for row, values in enumerate(rows):
        if values[idx]:
            pivot = row
            break
    if pivot is None:
        next_rows, next_columns = delete_column(rows, columns, original_element)
        return next_rows, next_columns, False
    work = [list(row) for row in rows]
    for row in range(len(work)):
        if row != pivot and work[row][idx]:
            work[row] = [left ^ right for left, right in zip(work[row], work[pivot])]
    contracted = [
        [value for col, value in enumerate(values) if col != idx]
        for row_idx, values in enumerate(work)
        if row_idx != pivot
    ]
    next_columns = [value for col, value in enumerate(columns) if col != idx]
    reduced, _pivots = rref_mod2(contracted, len(next_columns))
    return reduced, next_columns, True


def apply_minor(
    matrix: list[list[int]],
    removed: list[int],
    contracted: set[int],
) -> tuple[list[list[int]], list[int], int]:
    columns = list(range(len(matrix[0])))
    rows, _pivots = rref_mod2(matrix, len(columns))
    effective_contracts = 0
    for original in sorted(removed):
        if original in contracted:
            rows, columns, contracted_nonloop = contract_column(rows, columns, original)
            if contracted_nonloop:
                effective_contracts += 1
        else:
            rows, columns = delete_column(rows, columns, original)
    return rows, columns, effective_contracts


def row_mask(row: list[int]) -> int:
    mask = 0
    for idx, value in enumerate(row):
        if value:
            mask |= 1 << idx
    return mask


def original_edge_mask(row: list[int], columns: list[int]) -> int:
    mask = 0
    for idx, value in enumerate(row):
        if value:
            mask |= 1 << int(columns[idx])
    return mask


def vector_from_mask(mask: int, width: int) -> list[int]:
    return [(mask >> idx) & 1 for idx in range(width)]


def selected_record(records: list[dict[str, Any]], record_id: int = 0) -> dict[str, Any]:
    if len(records) <= record_id:
        raise AssertionError("selected compatible record is missing")
    return records[record_id]


def build_rows() -> dict[str, Any]:
    long_k23oct = load_json(LONG_K23OCT_REPORT)
    w24 = load_json(W24_REPORT)
    delete_contract = load_json(DELETE_CONTRACT_REPORT)
    sector33_dual = load_json(SECTOR33_DUAL_REPORT)
    placement_rows_raw = read_csv_rows(LONG_K23OCT_PLACEMENT)
    placement = {int(row["source_edge_id"]): int(row["w24_coordinate"]) for row in placement_rows_raw}
    target_octad_mask = int(long_k23oct["witness"]["target_w24_octad_mask"])

    records = delete_contract["witness"]["delete_contract_shadow_analysis"]["shadow_summaries"]["dual_rowspace_shadow"]["compatible_records"]
    record = selected_record(records, 0)
    removed = sorted(int(value) for value in record["contracted_original_elements"] + record["deleted_original_elements"])
    contracted = {int(value) for value in record["contracted_original_elements"]}
    dual_matrix = [[int(value) & 1 for value in row] for row in sector33_dual["derived"]["dual_summary"]["dual_matrix"]]
    source_rows, remaining_columns, effective_contracts = apply_minor(dual_matrix, removed, contracted)
    source_rank = len(source_rows)
    w24_span = span_masks([int(mask) for mask in w24["witness"]["golay_code"]["generator_basis_masks"]])

    row_records: list[dict[str, int]] = []
    mapped_basis_masks: list[int] = []
    mapped_basis_vectors: list[list[int]] = []
    for row_id, row in enumerate(source_rows):
        mapped_mask = 0
        for idx, value in enumerate(row):
            if value:
                mapped_mask ^= 1 << placement[int(remaining_columns[idx])]
        mapped_basis_masks.append(mapped_mask)
        mapped_basis_vectors.append(vector_from_mask(mapped_mask, 24))
        row_records.append(
            {
                "row_id": row_id,
                "source_row_mask": row_mask(row),
                "source_original_edge_mask": original_edge_mask(row, remaining_columns),
                "source_support_count": int(sum(row)),
                "mapped_w24_mask": int(mapped_mask),
                "mapped_weight": int(mapped_mask.bit_count()),
                "in_w24_code_flag": int(mapped_mask in w24_span),
                "matches_target_octad_flag": int(mapped_mask == target_octad_mask),
            }
        )

    word_records: list[dict[str, int]] = []
    for word_id, selector in enumerate(range(1 << len(mapped_basis_masks))):
        mapped_mask = 0
        for basis_id, basis_mask in enumerate(mapped_basis_masks):
            if (selector >> basis_id) & 1:
                mapped_mask ^= basis_mask
        word_records.append(
            {
                "word_id": word_id,
                "span_selector_mask": selector,
                "mapped_w24_mask": int(mapped_mask),
                "mapped_weight": int(mapped_mask.bit_count()),
                "in_w24_code_flag": int(mapped_mask in w24_span),
            }
        )

    all_words_in_w24 = all(row["in_w24_code_flag"] == 1 for row in word_records)
    obs = {
        "long_k23oct_certified_flag": int(long_k23oct.get("status") == "SECTOR33_K23_TYPED_W24_OCTAD_PLACEMENT_CERTIFIED" and long_k23oct.get("all_checks_pass") is True),
        "w24_code_certified_flag": int(w24.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED" and w24.get("all_checks_pass") is True),
        "sector33_dual_certified_flag": int(sector33_dual.get("status") == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED" and sector33_dual.get("all_checks_pass") is True),
        "delete_contract_input_certified_flag": int(delete_contract.get("status") == "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_CERTIFIED" and delete_contract.get("all_checks_pass") is True),
        "selected_record_id": 0,
        "selected_extra_removed": int(record["extra_removed"]),
        "selected_effective_contract_count": int(effective_contracts),
        "selected_remaining_column_count": len(remaining_columns),
        "selected_source_rank": source_rank,
        "mapped_basis_row_count": len(mapped_basis_masks),
        "mapped_nonzero_mask": int(mapped_basis_masks[0]) if mapped_basis_masks else 0,
        "mapped_nonzero_weight": int(mapped_basis_masks[0].bit_count()) if mapped_basis_masks else 0,
        "target_octad_mask": target_octad_mask,
        "mapped_basis_in_w24_flag": int(all(row["in_w24_code_flag"] == 1 for row in row_records)),
        "rowspace_word_count": len(word_records),
        "rowspace_rank": len(mapped_basis_masks),
        "rowspace_all_words_in_w24_flag": int(all_words_in_w24),
        "rowspace_subcode_certified_flag": int(all_words_in_w24 and source_rank == len(mapped_basis_masks)),
        "rowspace_equals_w24_flag": 0,
        "k23_equality_certified_flag": 0,
        "full_morphism_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "source_row_matrix": np.asarray(source_rows, dtype=np.int64),
        "mapped_basis_vectors": np.asarray(mapped_basis_vectors, dtype=np.int64),
        "mapped_word_masks": np.asarray([row["mapped_w24_mask"] for row in word_records], dtype=np.int64),
    }
    return {
        "long_k23oct": long_k23oct,
        "w24": w24,
        "delete_contract": delete_contract,
        "sector33_dual": sector33_dual,
        "row_records": row_records,
        "word_records": word_records,
        "obs_rows": obs_rows,
        "row_table": table_from_rows(ROW_COLUMNS, row_records),
        "word_table": table_from_rows(WORD_COLUMNS, word_records),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "remaining_columns": remaining_columns,
        "row_text_hash": hashlib.sha256(digest_text(ROW_COLUMNS, row_records).encode("ascii")).hexdigest(),
        "word_text_hash": hashlib.sha256(digest_text(WORD_COLUMNS, word_records).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_k23oct_input_passes": obs["long_k23oct_certified_flag"] == 1,
        "w24_code_input_passes": obs["w24_code_certified_flag"] == 1,
        "sector33_dual_input_passes": obs["sector33_dual_certified_flag"] == 1,
        "delete_contract_input_passes": obs["delete_contract_input_certified_flag"] == 1,
        "selected_minor_reconstructs_rank_one_rowspace": (
            obs["selected_record_id"],
            obs["selected_extra_removed"],
            obs["selected_effective_contract_count"],
            obs["selected_remaining_column_count"],
            obs["selected_source_rank"],
        )
        == (0, 5, 3, 24, 1),
        "mapped_basis_is_target_w24_octad": (
            obs["mapped_basis_row_count"],
            obs["mapped_nonzero_mask"],
            obs["mapped_nonzero_weight"],
            obs["target_octad_mask"],
            obs["mapped_basis_in_w24_flag"],
        )
        == (1, obs["target_octad_mask"], 8, obs["target_octad_mask"], 1),
        "entire_selected_rowspace_is_w24_subcode": (
            obs["rowspace_word_count"],
            obs["rowspace_rank"],
            obs["rowspace_all_words_in_w24_flag"],
            obs["rowspace_subcode_certified_flag"],
        )
        == (2, 1, 1, 1),
        "higher_binding_claims_remain_open": (
            obs["rowspace_equals_w24_flag"],
            obs["k23_equality_certified_flag"],
            obs["full_morphism_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_selected_w24_rowspace_subcode",
        "summary": obs,
        "remaining_columns": rows["remaining_columns"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the selected rank-one sector33 shadow rowspace maps into the certified W24 code under the long_k23oct placement, but not that it equals the full W24 code or K23 syzygy rowspace.",
    }
    seam_payload = {
        "schema": "long.k23row.seam@1",
        "status": STATUS,
        "claim": "The selected 24-column sector33 delete/contract shadow rowspace maps to a rank-one W24 subcode generated by the certified target octad.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23oct": input_entry(
            LONG_K23OCT_REPORT,
            {
                "status": rows["long_k23oct"].get("status"),
                "certificate_sha256": rows["long_k23oct"].get("certificate_sha256"),
            },
        ),
        "long_k23oct_placement": input_entry(LONG_K23OCT_PLACEMENT),
        "w24_hexacode_row_alphabetization": input_entry(
            W24_REPORT,
            {
                "status": rows["w24"].get("status"),
                "certificate_sha256": rows["w24"].get("certificate_sha256"),
            },
        ),
        "sector33_w24_marked_delete_contract_shadow_probe": input_entry(
            DELETE_CONTRACT_REPORT,
            {
                "status": rows["delete_contract"].get("status"),
                "certificate_sha256": rows["delete_contract"].get("certificate_sha256"),
            },
        ),
        "sector33_dual": input_entry(
            SECTOR33_DUAL_REPORT,
            {
                "status": rows["sector33_dual"].get("status"),
                "certificate_sha256": rows["sector33_dual"].get("certificate_sha256"),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23row.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23row certifies the selected sector33 rank-one shadow as a W24 subcode under the long_k23oct coordinate placement.",
        "stage_protocol": {
            "draft": "read long_k23oct, the selected delete/contract shadow, the dual sector33 matrix, and the certified W24 code",
            "witness": "emit reconstructed source rowspace rows, mapped W24 rowspace words, observables, and matrix payloads",
            "coherence": "check minor reconstruction, mapping to the target W24 octad, and full rowspace containment in W24",
            "closure": "certify selected rowspace containment without claiming full K23 or W24 equality",
            "emit": "write long_k23row artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "rowspace_rows_csv": relpath(OUT_DIR / "rowspace_rows.csv"),
            "rowspace_words_csv": relpath(OUT_DIR / "rowspace_words.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23row_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected delete/contract shadow record reconstructs as a rank-one rowspace on 24 columns",
                "the nonzero row maps under long_k23oct placement to the certified target W24 octad",
                "both words in the selected rank-one rowspace are contained in the certified W24 code",
                "the selected sector33 shadow is therefore a W24 subcode under this placement",
            ],
            "does_not_certify": [
                "that the selected rank-one rowspace equals the full W24 code",
                "a full sector33-to-W24 rowspace morphism for all sector33 rows",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Lift from the selected rank-one rowspace to a higher-rank 24-column sector33-to-W24 rowspace morphism, or prove that this selected shadow is the maximal rowspace available under the current delete/contract route.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23row.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23row.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "row_csv": csv_text(ROW_COLUMNS, rows["row_records"]),
        "word_csv": csv_text(WORD_COLUMNS, rows["word_records"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "row_table": rows["row_table"],
        "word_table": rows["word_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "row_text_sha256": rows["row_text_hash"],
            "word_text_sha256": rows["word_text_hash"],
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
    (OUT_DIR / "rowspace_rows.csv").write_text(payloads["row_csv"], encoding="utf-8")
    (OUT_DIR / "rowspace_words.csv").write_text(payloads["word_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        row_table=payloads["row_table"],
        word_table=payloads["word_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23row_matrices.npz", **payloads["matrix_payload"])
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
