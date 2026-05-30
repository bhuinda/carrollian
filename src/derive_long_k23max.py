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


THEOREM_ID = "long_k23max"
STATUS = "SECTOR33_K23_DELETE_CONTRACT_ROUTE_MAX_RANK1_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23max.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23max.py"
LONG_K23ROW_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23row" / "report.json"
LONG_K23OCT_OCTAD = D20_INVARIANTS / "proof_obligations" / "long_k23oct" / "octad_rows.csv"
DELETE_CONTRACT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_marked_delete_contract_shadow_probe"
    / "report.json"
)

CLASS_TEXT_HASH = "6532e26e51f38a1801ed42ee67371b20729720164bfa4fa8149fcaf39e704215"
SUPPORT_TEXT_HASH = "8fc42151e31d807d3092ac28784b881bc0c4dbd4dcc0802fb45351f6a26e151f"
OBS_TEXT_HASH = "e275a083e16b9bdb5618576887b538520f545ef5eb3550ac56977a1914221d46"
MATRIX_SHA256 = "b1c5321a50653504580effecce3afd3f1f4fe9c7a2ed383204e288804f43208d"

CLASS_COLUMNS = [
    "class_id",
    "route_side_code",
    "class_kind_code",
    "candidate_count",
    "compatible_count",
    "compatible_rank",
    "unique_support_count",
    "mapped_w24_mask",
    "max_rank_in_class",
    "higher_rank_flag",
]
SUPPORT_COLUMNS = [
    "support_row_id",
    "source_edge_id",
    "w24_coordinate",
    "h6_column_id",
    "mog_row",
    "f4_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23row_certified_flag",
    "delete_contract_input_certified_flag",
    "delete_contract_candidate_count",
    "primal_candidate_count",
    "primal_compatible_count",
    "dual_candidate_count",
    "dual_compatible_count",
    "dual_rank0_compatible_count",
    "dual_rank1_compatible_count",
    "dual_rank_ge2_compatible_count",
    "unique_nonzero_support_count",
    "unique_nonzero_support_weight",
    "unique_nonzero_support_case_count",
    "mapped_w24_mask",
    "mapped_w24_weight",
    "mapped_w24_subcode_flag",
    "current_route_max_compatible_rank",
    "current_route_higher_rank_possible_flag",
    "current_route_maximal_rank1_closed_flag",
    "outside_delete_contract_route_open_flag",
    "k23_equality_certified_flag",
    "m23_module_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    return hashlib.sha256(
        b"".join(
            np.ascontiguousarray(payload[key]).tobytes()
            for key in ["class_matrix", "support_matrix", "observable_vector"]
        )
    ).hexdigest()


def int_dict_get(payload: dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(payload.get(key, default))
    except (TypeError, ValueError):
        return default


def build_rows() -> dict[str, Any]:
    long_k23row = load_json(LONG_K23ROW_REPORT)
    delete_contract = load_json(DELETE_CONTRACT_REPORT)
    octad_rows_raw = read_csv_rows(LONG_K23OCT_OCTAD)
    analysis = delete_contract["witness"]["delete_contract_shadow_analysis"]
    primal = analysis["shadow_summaries"]["primal_orthogonal_shadow"]
    dual = analysis["shadow_summaries"]["dual_rowspace_shadow"]
    rank_hist = {str(key): int(value) for key, value in dual.get("golay_weight_compatible_rank_histogram", {}).items()}
    unique_supports = dual.get("unique_nonzero_supports", [])
    support_weight = int(unique_supports[0]["support_weight"]) if unique_supports else 0
    support_case_count = int(unique_supports[0]["case_count"]) if unique_supports else 0
    mapped_w24_mask = int(long_k23row["witness"]["summary"]["mapped_nonzero_mask"])
    mapped_w24_weight = int(long_k23row["witness"]["summary"]["mapped_nonzero_weight"])
    class_rows = [
        {
            "class_id": 0,
            "route_side_code": 0,
            "class_kind_code": 0,
            "candidate_count": int(primal["candidate_count"]),
            "compatible_count": int(primal["golay_weight_compatible_case_count"]),
            "compatible_rank": -1,
            "unique_support_count": 0,
            "mapped_w24_mask": 0,
            "max_rank_in_class": -1,
            "higher_rank_flag": 0,
        },
        {
            "class_id": 1,
            "route_side_code": 1,
            "class_kind_code": 1,
            "candidate_count": rank_hist.get("0", 0),
            "compatible_count": rank_hist.get("0", 0),
            "compatible_rank": 0,
            "unique_support_count": 0,
            "mapped_w24_mask": 0,
            "max_rank_in_class": 0,
            "higher_rank_flag": 0,
        },
        {
            "class_id": 2,
            "route_side_code": 1,
            "class_kind_code": 2,
            "candidate_count": rank_hist.get("1", 0),
            "compatible_count": rank_hist.get("1", 0),
            "compatible_rank": 1,
            "unique_support_count": len(unique_supports),
            "mapped_w24_mask": mapped_w24_mask,
            "max_rank_in_class": 1,
            "higher_rank_flag": 0,
        },
    ]
    support_rows = [
        {
            "support_row_id": int(row["octad_row_id"]),
            "source_edge_id": int(row["source_edge_id"]),
            "w24_coordinate": int(row["w24_coordinate"]),
            "h6_column_id": int(row["h6_column_id"]),
            "mog_row": int(row["mog_row"]),
            "f4_value": int(row["f4_value"]),
        }
        for row in octad_rows_raw
    ]
    rank_ge2 = sum(count for rank, count in rank_hist.items() if int(rank) >= 2)
    obs = {
        "long_k23row_certified_flag": int(long_k23row.get("status") == "SECTOR33_K23_SELECTED_W24_ROWSPACE_SUBCODE_CERTIFIED" and long_k23row.get("all_checks_pass") is True),
        "delete_contract_input_certified_flag": int(delete_contract.get("status") == "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_CERTIFIED" and delete_contract.get("all_checks_pass") is True),
        "delete_contract_candidate_count": int(analysis["candidate_count"]),
        "primal_candidate_count": int(primal["candidate_count"]),
        "primal_compatible_count": int(primal["golay_weight_compatible_case_count"]),
        "dual_candidate_count": int(dual["candidate_count"]),
        "dual_compatible_count": int(dual["golay_weight_compatible_case_count"]),
        "dual_rank0_compatible_count": rank_hist.get("0", 0),
        "dual_rank1_compatible_count": rank_hist.get("1", 0),
        "dual_rank_ge2_compatible_count": rank_ge2,
        "unique_nonzero_support_count": len(unique_supports),
        "unique_nonzero_support_weight": support_weight,
        "unique_nonzero_support_case_count": support_case_count,
        "mapped_w24_mask": mapped_w24_mask,
        "mapped_w24_weight": mapped_w24_weight,
        "mapped_w24_subcode_flag": int(long_k23row["witness"]["summary"]["rowspace_subcode_certified_flag"]),
        "current_route_max_compatible_rank": 1 if rank_hist.get("1", 0) else 0,
        "current_route_higher_rank_possible_flag": int(rank_ge2 > 0),
        "current_route_maximal_rank1_closed_flag": int(rank_ge2 == 0 and int(primal["golay_weight_compatible_case_count"]) == 0 and rank_hist.get("1", 0) == support_case_count),
        "outside_delete_contract_route_open_flag": 1,
        "k23_equality_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "class_matrix": table_from_rows(CLASS_COLUMNS, class_rows),
        "support_matrix": table_from_rows(SUPPORT_COLUMNS, support_rows),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23row": long_k23row,
        "delete_contract": delete_contract,
        "class_rows": class_rows,
        "support_rows": support_rows,
        "obs_rows": obs_rows,
        "class_table": matrix_payload["class_matrix"],
        "support_table": matrix_payload["support_matrix"],
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "class_text_hash": hashlib.sha256(digest_text(CLASS_COLUMNS, class_rows).encode("ascii")).hexdigest(),
        "support_text_hash": hashlib.sha256(digest_text(SUPPORT_COLUMNS, support_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_k23row_input_passes": obs["long_k23row_certified_flag"] == 1,
        "delete_contract_input_passes": obs["delete_contract_input_certified_flag"] == 1,
        "candidate_family_count_is_6400": (
            obs["delete_contract_candidate_count"],
            obs["primal_candidate_count"],
            obs["dual_candidate_count"],
        )
        == (6400, 3200, 3200),
        "primal_side_has_no_compatible_shadow": obs["primal_compatible_count"] == 0,
        "dual_compatible_rank_histogram_is_55_plus_15": (
            obs["dual_compatible_count"],
            obs["dual_rank0_compatible_count"],
            obs["dual_rank1_compatible_count"],
            obs["dual_rank_ge2_compatible_count"],
        )
        == (70, 55, 15, 0),
        "only_nonzero_support_is_mapped_w24_subcode": (
            obs["unique_nonzero_support_count"],
            obs["unique_nonzero_support_weight"],
            obs["unique_nonzero_support_case_count"],
            obs["mapped_w24_weight"],
            obs["mapped_w24_subcode_flag"],
        )
        == (1, 8, 15, 8, 1),
        "current_route_is_max_rank_one": (
            obs["current_route_max_compatible_rank"],
            obs["current_route_higher_rank_possible_flag"],
            obs["current_route_maximal_rank1_closed_flag"],
        )
        == (1, 0, 1),
        "global_claims_remain_open": (
            obs["outside_delete_contract_route_open_flag"],
            obs["k23_equality_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_delete_contract_route_max_rank1",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This closes the current cocircuit-plus-one delete/contract W24 shadow route at maximal compatible rank one; it does not rule out non-edge, quotient, or full 56-to-W24 binding routes.",
    }
    seam_payload = {
        "schema": "long.k23max.seam@1",
        "status": STATUS,
        "claim": "Under the current cocircuit-plus-one delete/contract route, the only nonzero W24-compatible sector33 shadow is the rank-one octad subcode already certified by long_k23row.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23row": input_entry(
            LONG_K23ROW_REPORT,
            {
                "status": rows["long_k23row"].get("status"),
                "certificate_sha256": rows["long_k23row"].get("certificate_sha256"),
            },
        ),
        "long_k23oct_octad": input_entry(LONG_K23OCT_OCTAD),
        "sector33_w24_marked_delete_contract_shadow_probe": input_entry(
            DELETE_CONTRACT_REPORT,
            {
                "status": rows["delete_contract"].get("status"),
                "certificate_sha256": rows["delete_contract"].get("certificate_sha256"),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23max.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23max certifies that the current sector33 delete/contract shadow route cannot produce a W24-compatible rowspace above rank one.",
        "stage_protocol": {
            "draft": "read long_k23row and the full delete/contract shadow probe",
            "witness": "emit route-class rows, support-placement rows, observables, and matrix payloads",
            "coherence": "check 6400 candidates, primal obstruction, dual 55+15 rank split, unique nonzero support, and open outside-route flags",
            "closure": "certify maximal rank-one closure for this route only",
            "emit": "write long_k23max artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "class_rows_csv": relpath(OUT_DIR / "class_rows.csv"),
            "support_rows_csv": relpath(OUT_DIR / "support_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23max_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the current delete/contract shadow family has 6400 tested candidates",
                "the primal side has zero W24-compatible shadows",
                "the dual side has 55 rank-zero compatible shadows and 15 rank-one compatible shadows",
                "there are zero rank-two-or-higher W24-compatible shadows in this route",
                "the only nonzero compatible support is the long_k23row W24 octad subcode",
            ],
            "does_not_certify": [
                "absence of a sector33-to-W24 morphism outside the current delete/contract route",
                "a full 56-to-W24 syzygy basis-binding map",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Leave the exhausted delete/contract route and test a general quotient or non-edge 56-to-W24 binding family with rank and W24 containment as hard gates.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23max.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23max.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "support_csv": csv_text(SUPPORT_COLUMNS, rows["support_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "class_table": rows["class_table"],
        "support_table": rows["support_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "class_text_sha256": rows["class_text_hash"],
            "support_text_sha256": rows["support_text_hash"],
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
    (OUT_DIR / "class_rows.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "support_rows.csv").write_text(payloads["support_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        class_table=payloads["class_table"],
        support_table=payloads["support_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23max_matrices.npz", **payloads["matrix_payload"])
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
