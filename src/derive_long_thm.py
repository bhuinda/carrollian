from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_llnind import (
        BRIDGE_COLUMNS as LONG_LLNIND_BRIDGE_COLUMNS,
        LAYER_COLUMNS as LONG_LLNIND_LAYER_COLUMNS,
        OUT_DIR as LONG_LLNIND_DIR,
        SEAM_COLUMNS as LONG_LLNIND_SEAM_COLUMNS,
        STATUS as LONG_LLNIND_STATUS,
    )
    from .derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_llnind import (
        BRIDGE_COLUMNS as LONG_LLNIND_BRIDGE_COLUMNS,
        LAYER_COLUMNS as LONG_LLNIND_LAYER_COLUMNS,
        OUT_DIR as LONG_LLNIND_DIR,
        SEAM_COLUMNS as LONG_LLNIND_SEAM_COLUMNS,
        STATUS as LONG_LLNIND_STATUS,
    )
    from derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_thm"
STATUS = "LONG_THM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_LLNIND_REPORT = LONG_LLNIND_DIR / "report.json"
LONG_LLNIND_LAYER = LONG_LLNIND_DIR / "layer.csv"
LONG_LLNIND_SEAM = LONG_LLNIND_DIR / "seam.csv"
LONG_LLNIND_BRIDGE = LONG_LLNIND_DIR / "bridge.csv"
LONG_LLNIND_TABLES = LONG_LLNIND_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_thm.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_thm.py"

THEOREM_TEXT_HASH = "2bc6c7b25152ad8d6d022dc703f4f155c1463a316a62ac321c345b79cd88f4ac"
PROOF_TEXT_HASH = "092a3c117a1b410c75091a1451399f7baa72969c738fd6bf38e1ef85bb128d04"
BOUNDARY_TEXT_HASH = "e0ea1cc4a3beb8dfbffba464f21af99bc88050380a5521416bb8c91ded827c2c"

THEOREM_COLUMNS = [
    "theorem_id",
    "theorem_code",
    "line_point_count",
    "tensor_support_count",
    "universal_law_count",
    "support_gap_check_count",
    "support_gap_nonnegative_count",
    "proof_item_count",
    "boundary_item_count",
    "finite_tensor_lookup_theorem_flag",
]
PROOF_COLUMNS = [
    "proof_id",
    "proof_code",
    "source_layer_code",
    "primary_count",
    "secondary_count",
    "tertiary_count",
    "certified_flag",
]
BOUNDARY_COLUMNS = [
    "boundary_id",
    "boundary_code",
    "scope_code",
    "resolved_flag",
    "finite_theorem_required_flag",
    "future_work_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "tensor_support_count",
    "tensor_coeff_sum",
    "universal_law_count",
    "probability_path_count",
    "finite_gap_check_count",
    "finite_gap_nonnegative_count",
    "tail_formula_nonnegative_count",
    "certified_layer_count",
    "seam_match_count",
    "proof_item_count",
    "boundary_item_count",
    "resolved_boundary_count",
    "finite_theorem_required_boundary_count",
    "future_work_boundary_count",
    "long_llnind_certified_flag",
    "finite_tensor_lookup_theorem_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_int_csv(path: Any) -> list[dict[str, int]]:
    return int_rows(read_csv_rows(path))


def build_rows() -> dict[str, Any]:
    llnind_report = load_json(LONG_LLNIND_REPORT)
    layer_rows = read_int_csv(LONG_LLNIND_LAYER)
    seam_rows = read_int_csv(LONG_LLNIND_SEAM)
    bridge_rows = read_int_csv(LONG_LLNIND_BRIDGE)
    bridge = bridge_rows[0]

    certified_layer_count = sum(row["certified_flag"] for row in layer_rows)
    seam_match_count = sum(row["seam_match_flag"] for row in seam_rows)
    llnind_certified = int(
        llnind_report.get("status") == LONG_LLNIND_STATUS
        and llnind_report.get("all_checks_pass") is True
    )
    proof_rows = [
        {
            "proof_id": 0,
            "proof_code": 0,
            "source_layer_code": 0,
            "primary_count": bridge["line_point_count"],
            "secondary_count": bridge["tensor_support_count"],
            "tertiary_count": bridge["tensor_coeff_sum"],
            "certified_flag": 1,
        },
        {
            "proof_id": 1,
            "proof_code": 1,
            "source_layer_code": 1,
            "primary_count": bridge["profunctor_object_count"],
            "secondary_count": bridge["profunctor_count"],
            "tertiary_count": bridge["universal_node_count"],
            "certified_flag": 1,
        },
        {
            "proof_id": 2,
            "proof_code": 2,
            "source_layer_code": 2,
            "primary_count": bridge["universal_law_count"],
            "secondary_count": bridge["forcing_basis_count"],
            "tertiary_count": bridge["naturality_law_count"],
            "certified_flag": 1,
        },
        {
            "proof_id": 3,
            "proof_code": 3,
            "source_layer_code": 5,
            "primary_count": bridge["probability_path_count"],
            "secondary_count": bridge["variance_shrink_count"],
            "tertiary_count": bridge["raw_path_count"],
            "certified_flag": 1,
        },
        {
            "proof_id": 4,
            "proof_code": 4,
            "source_layer_code": 7,
            "primary_count": bridge["finite_gap_check_count"],
            "secondary_count": bridge["finite_gap_nonnegative_count"],
            "tertiary_count": bridge["tail_formula_nonnegative_count"],
            "certified_flag": 1,
        },
        {
            "proof_id": 5,
            "proof_code": 5,
            "source_layer_code": -1,
            "primary_count": certified_layer_count,
            "secondary_count": seam_match_count,
            "tertiary_count": bridge["theorem_bridge_flag"],
            "certified_flag": llnind_certified,
        },
    ]
    boundary_rows = [
        {
            "boundary_id": 0,
            "boundary_code": 0,
            "scope_code": 0,
            "resolved_flag": 0,
            "finite_theorem_required_flag": 0,
            "future_work_flag": 1,
        },
        {
            "boundary_id": 1,
            "boundary_code": 1,
            "scope_code": 1,
            "resolved_flag": 0,
            "finite_theorem_required_flag": 0,
            "future_work_flag": 1,
        },
        {
            "boundary_id": 2,
            "boundary_code": 2,
            "scope_code": 1,
            "resolved_flag": 0,
            "finite_theorem_required_flag": 0,
            "future_work_flag": 1,
        },
        {
            "boundary_id": 3,
            "boundary_code": 3,
            "scope_code": 2,
            "resolved_flag": 0,
            "finite_theorem_required_flag": 0,
            "future_work_flag": 1,
        },
        {
            "boundary_id": 4,
            "boundary_code": 4,
            "scope_code": 3,
            "resolved_flag": 0,
            "finite_theorem_required_flag": 0,
            "future_work_flag": 1,
        },
    ]
    finite_theorem_flag = int(
        llnind_certified
        and certified_layer_count == 8
        and seam_match_count == 8
        and bridge["theorem_bridge_flag"] == 1
        and bridge["finite_gap_check_count"] == bridge["finite_gap_nonnegative_count"]
        and sum(row["certified_flag"] for row in proof_rows) == len(proof_rows)
        and sum(row["finite_theorem_required_flag"] for row in boundary_rows) == 0
    )
    theorem_rows = [
        {
            "theorem_id": 0,
            "theorem_code": 0,
            "line_point_count": bridge["line_point_count"],
            "tensor_support_count": bridge["tensor_support_count"],
            "universal_law_count": bridge["universal_law_count"],
            "support_gap_check_count": bridge["finite_gap_check_count"],
            "support_gap_nonnegative_count": bridge["finite_gap_nonnegative_count"],
            "proof_item_count": len(proof_rows),
            "boundary_item_count": len(boundary_rows),
            "finite_tensor_lookup_theorem_flag": finite_theorem_flag,
        }
    ]
    obs = {
        "line_point_count": bridge["line_point_count"],
        "tensor_support_count": bridge["tensor_support_count"],
        "tensor_coeff_sum": bridge["tensor_coeff_sum"],
        "universal_law_count": bridge["universal_law_count"],
        "probability_path_count": bridge["probability_path_count"],
        "finite_gap_check_count": bridge["finite_gap_check_count"],
        "finite_gap_nonnegative_count": bridge["finite_gap_nonnegative_count"],
        "tail_formula_nonnegative_count": bridge["tail_formula_nonnegative_count"],
        "certified_layer_count": certified_layer_count,
        "seam_match_count": seam_match_count,
        "proof_item_count": len(proof_rows),
        "boundary_item_count": len(boundary_rows),
        "resolved_boundary_count": sum(row["resolved_flag"] for row in boundary_rows),
        "finite_theorem_required_boundary_count": sum(
            row["finite_theorem_required_flag"] for row in boundary_rows
        ),
        "future_work_boundary_count": sum(row["future_work_flag"] for row in boundary_rows),
        "long_llnind_certified_flag": llnind_certified,
        "finite_tensor_lookup_theorem_flag": finite_theorem_flag,
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
    theorem_hash = hashlib.sha256(
        digest_text(THEOREM_COLUMNS, theorem_rows).encode("ascii")
    ).hexdigest()
    proof_hash = hashlib.sha256(
        digest_text(PROOF_COLUMNS, proof_rows).encode("ascii")
    ).hexdigest()
    boundary_hash = hashlib.sha256(
        digest_text(BOUNDARY_COLUMNS, boundary_rows).encode("ascii")
    ).hexdigest()
    return {
        "theorem_rows": theorem_rows,
        "proof_rows": proof_rows,
        "boundary_rows": boundary_rows,
        "obs_rows": obs_rows,
        "theorem_table": table_from_rows(THEOREM_COLUMNS, theorem_rows),
        "proof_table": table_from_rows(PROOF_COLUMNS, proof_rows),
        "boundary_table": table_from_rows(BOUNDARY_COLUMNS, boundary_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "theorem_hash": theorem_hash,
        "proof_hash": proof_hash,
        "boundary_hash": boundary_hash,
        "obs": obs,
        "input_reports": {"long_llnind": llnind_report},
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": obs["long_llnind_certified_flag"] == 1,
        "theorem_fingerprint_exact": (
            obs["line_point_count"],
            obs["tensor_support_count"],
            obs["universal_law_count"],
            obs["finite_gap_check_count"],
            obs["finite_gap_nonnegative_count"],
            rows["theorem_hash"],
        )
        == (
            985,
            1_414_965,
            306,
            131_586,
            131_586,
            THEOREM_TEXT_HASH,
        ),
        "proof_fingerprint_exact": (
            obs["proof_item_count"],
            obs["certified_layer_count"],
            obs["seam_match_count"],
            obs["finite_tensor_lookup_theorem_flag"],
            rows["proof_hash"],
        )
        == (6, 8, 8, 1, PROOF_TEXT_HASH),
        "boundary_fingerprint_exact": (
            obs["boundary_item_count"],
            obs["resolved_boundary_count"],
            obs["finite_theorem_required_boundary_count"],
            obs["future_work_boundary_count"],
            rows["boundary_hash"],
        )
        == (5, 0, 0, 5, BOUNDARY_TEXT_HASH),
        "goal_not_overclaimed": obs["complete_goal_claim_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["theorem_table"].shape),
            tuple(rows["proof_table"].shape),
            tuple(rows["boundary_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (1, len(THEOREM_COLUMNS)),
            (6, len(PROOF_COLUMNS)),
            (5, len(BOUNDARY_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_tensor_lookup_lln_theorem_status",
        "finite_theorem": {
            "line_point_count": obs["line_point_count"],
            "tensor_support_count": obs["tensor_support_count"],
            "tensor_coeff_sum": obs["tensor_coeff_sum"],
            "universal_law_count": obs["universal_law_count"],
            "probability_path_count": obs["probability_path_count"],
            "finite_gap_check_count": obs["finite_gap_check_count"],
            "finite_gap_nonnegative_count": obs["finite_gap_nonnegative_count"],
            "tail_formula_nonnegative_count": obs["tail_formula_nonnegative_count"],
            "theorem_text_sha256": rows["theorem_hash"],
            "theorem_table_sha256": sha_array(rows["theorem_table"]),
        },
        "proof_inventory": {
            "proof_item_count": obs["proof_item_count"],
            "certified_layer_count": obs["certified_layer_count"],
            "seam_match_count": obs["seam_match_count"],
            "proof_text_sha256": rows["proof_hash"],
            "proof_table_sha256": sha_array(rows["proof_table"]),
        },
        "remaining_boundaries": {
            "boundary_item_count": obs["boundary_item_count"],
            "resolved_boundary_count": obs["resolved_boundary_count"],
            "finite_theorem_required_boundary_count": obs[
                "finite_theorem_required_boundary_count"
            ],
            "future_work_boundary_count": obs["future_work_boundary_count"],
            "boundary_text_sha256": rows["boundary_hash"],
            "boundary_table_sha256": sha_array(rows["boundary_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    thm_payload = {
        "schema": "long.thm@1",
        "object": "finite_tensor_lookup_lln_theorem_status",
        "status": STATUS if all(checks.values()) else "LONG_THM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.thm.report@1",
        "status": thm_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_thm certifies the finite tensor-lookup LLN theorem status: "
            "the 985-address line, tensor lookup, finite profunctor diagram, "
            "raw product-path witnesses, probability curve, and global support-gap "
            "induction form one verified finite theorem bridge. It also records "
            "the remaining non-theorem boundaries without claiming they are solved."
        ),
        "stage_protocol": {
            "draft": "read the certified theorem bridge and its layer/seam evidence",
            "witness": "emit proved theorem rows and unresolved boundary rows",
            "coherence": "check theorem counts, proof inventory, boundary separation, hashes, and shapes",
            "closure": "certify finite tensor-lookup LLN status without overclaiming unresolved boundaries",
            "emit": "write long_thm artifacts and verifier hook",
        },
        "inputs": {
            "long_llnind_report": input_entry(
                LONG_LLNIND_REPORT,
                {"status": rows["input_reports"]["long_llnind"].get("status")},
            ),
            "long_llnind_layer": input_entry(
                LONG_LLNIND_LAYER,
                {"columns": LONG_LLNIND_LAYER_COLUMNS},
            ),
            "long_llnind_seam": input_entry(
                LONG_LLNIND_SEAM,
                {"columns": LONG_LLNIND_SEAM_COLUMNS},
            ),
            "long_llnind_bridge": input_entry(
                LONG_LLNIND_BRIDGE,
                {"columns": LONG_LLNIND_BRIDGE_COLUMNS},
            ),
            "long_llnind_tables": input_entry(LONG_LLNIND_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "thm": relpath(OUT_DIR / "thm.json"),
            "theorem_csv": relpath(OUT_DIR / "theorem.csv"),
            "proof_csv": relpath(OUT_DIR / "proof.csv"),
            "boundary_csv": relpath(OUT_DIR / "boundary.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "finite tensor-lookup LLN theorem status for the certified 985-address line bridge",
                "separation of proved finite theorem content from unresolved semantic/full-measure boundaries",
                "nonnegative global support-gap induction as part of the finite theorem bridge",
                "explicit non-completion of the broader open-ended invariant discovery objective",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic C985 associator composition",
                "a probability measure on the full raw tensor support",
                "all raw product paths in each fiber",
                "a genuine horizon-16 profunctor",
                "all possible invariants of the line address space",
            ],
        },
        "next_highest_yield_item": (
            "Build long_inv: inventory the remaining invariant families and rank "
            "which ones are theorem-critical versus exploratory."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.thm.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.thm.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "thm": thm_payload,
        "theorem_csv": csv_text(THEOREM_COLUMNS, rows["theorem_rows"]),
        "proof_csv": csv_text(PROOF_COLUMNS, rows["proof_rows"]),
        "boundary_csv": csv_text(BOUNDARY_COLUMNS, rows["boundary_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "theorem_table": rows["theorem_table"],
        "proof_table": rows["proof_table"],
        "boundary_table": rows["boundary_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "report": report,
        "manifest": manifest,
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
    write_json(OUT_DIR / "thm.json", payloads["thm"])
    (OUT_DIR / "theorem.csv").write_text(payloads["theorem_csv"], encoding="utf-8")
    (OUT_DIR / "proof.csv").write_text(payloads["proof_csv"], encoding="utf-8")
    (OUT_DIR / "boundary.csv").write_text(payloads["boundary_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        theorem_table=payloads["theorem_table"],
        proof_table=payloads["proof_table"],
        boundary_table=payloads["boundary_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
