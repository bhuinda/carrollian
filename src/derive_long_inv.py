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
    from .derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from .derive_long_thm import (
        BOUNDARY_COLUMNS as LONG_THM_BOUNDARY_COLUMNS,
        OUT_DIR as LONG_THM_DIR,
        STATUS as LONG_THM_STATUS,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from derive_long_thm import (
        BOUNDARY_COLUMNS as LONG_THM_BOUNDARY_COLUMNS,
        OUT_DIR as LONG_THM_DIR,
        STATUS as LONG_THM_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


INVENTORY_ID = "long_inv"
STATUS = "LONG_INV_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / INVENTORY_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_THM_REPORT = LONG_THM_DIR / "report.json"
LONG_THM_BOUNDARY = LONG_THM_DIR / "boundary.csv"
LONG_THM_TABLES = LONG_THM_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_inv.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_inv.py"

FAMILY_TEXT_HASH = "405ac19106d1988cbfebe180ae42d8d354773d674cd1b0d2623d2c4fe5a78724"
RANK_TEXT_HASH = "52c69e722d4e78f6d38e53f436c5ab2d1a060223960a5b00e4b848f49828d9e3"

FAMILY_COLUMNS = [
    "family_id",
    "family_code",
    "source_boundary_code",
    "priority_code",
    "scope_code",
    "theorem_critical_flag",
    "active_goal_required_flag",
    "certified_flag",
    "finite_theorem_exploratory_flag",
    "proof_gap_count",
]
RANK_COLUMNS = [
    "rank_id",
    "family_id",
    "priority_code",
    "blocking_code",
    "next_action_code",
    "depends_on_family_code",
    "emission_order",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "tensor_support_count",
    "source_boundary_count",
    "inventory_family_count",
    "remaining_family_count",
    "certified_family_count",
    "theorem_critical_remaining_count",
    "active_goal_required_remaining_count",
    "finite_theorem_exploratory_remaining_count",
    "high_priority_remaining_count",
    "proof_gap_count",
    "input_long_thm_certified_flag",
    "inventory_bridge_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_int_csv(path: Any) -> list[dict[str, int]]:
    return int_rows(read_csv_rows(path))


def build_rows() -> dict[str, Any]:
    thm_report = load_json(LONG_THM_REPORT)
    thm_boundary_rows = read_int_csv(LONG_THM_BOUNDARY)
    thm_witness = thm_report.get("witness", {})
    finite_theorem = thm_witness.get("finite_theorem", {})
    input_certified = int(
        thm_report.get("status") == LONG_THM_STATUS
        and thm_report.get("all_checks_pass") is True
    )

    remaining_boundary_codes = [row["boundary_code"] for row in thm_boundary_rows]
    family_rows = [
        {
            "family_id": 0,
            "family_code": 0,
            "source_boundary_code": -1,
            "priority_code": 9,
            "scope_code": 0,
            "theorem_critical_flag": 1,
            "active_goal_required_flag": 1,
            "certified_flag": input_certified,
            "finite_theorem_exploratory_flag": 0,
            "proof_gap_count": 0,
        },
        {
            "family_id": 1,
            "family_code": 4,
            "source_boundary_code": 4,
            "priority_code": 0,
            "scope_code": 3,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1,
            "certified_flag": 0,
            "finite_theorem_exploratory_flag": 1,
            "proof_gap_count": 1,
        },
        {
            "family_id": 2,
            "family_code": 0,
            "source_boundary_code": 0,
            "priority_code": 1,
            "scope_code": 0,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1,
            "certified_flag": 0,
            "finite_theorem_exploratory_flag": 1,
            "proof_gap_count": 1,
        },
        {
            "family_id": 3,
            "family_code": 3,
            "source_boundary_code": 3,
            "priority_code": 1,
            "scope_code": 2,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1,
            "certified_flag": 0,
            "finite_theorem_exploratory_flag": 1,
            "proof_gap_count": 1,
        },
        {
            "family_id": 4,
            "family_code": 1,
            "source_boundary_code": 1,
            "priority_code": 2,
            "scope_code": 1,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1,
            "certified_flag": 0,
            "finite_theorem_exploratory_flag": 1,
            "proof_gap_count": 1,
        },
        {
            "family_id": 5,
            "family_code": 2,
            "source_boundary_code": 2,
            "priority_code": 2,
            "scope_code": 1,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1,
            "certified_flag": 0,
            "finite_theorem_exploratory_flag": 1,
            "proof_gap_count": 1,
        },
    ]
    rank_rows = [
        {
            "rank_id": 0,
            "family_id": 1,
            "priority_code": 0,
            "blocking_code": 4,
            "next_action_code": 0,
            "depends_on_family_code": -1,
            "emission_order": 0,
        },
        {
            "rank_id": 1,
            "family_id": 2,
            "priority_code": 1,
            "blocking_code": 0,
            "next_action_code": 1,
            "depends_on_family_code": 4,
            "emission_order": 1,
        },
        {
            "rank_id": 2,
            "family_id": 3,
            "priority_code": 1,
            "blocking_code": 3,
            "next_action_code": 2,
            "depends_on_family_code": 0,
            "emission_order": 2,
        },
        {
            "rank_id": 3,
            "family_id": 4,
            "priority_code": 2,
            "blocking_code": 1,
            "next_action_code": 3,
            "depends_on_family_code": 0,
            "emission_order": 3,
        },
        {
            "rank_id": 4,
            "family_id": 5,
            "priority_code": 2,
            "blocking_code": 2,
            "next_action_code": 4,
            "depends_on_family_code": 1,
            "emission_order": 4,
        },
    ]
    remaining_rows = [row for row in family_rows if row["certified_flag"] == 0]
    obs = {
        "line_point_count": int(finite_theorem.get("line_point_count", 0)),
        "tensor_support_count": int(finite_theorem.get("tensor_support_count", 0)),
        "source_boundary_count": len(thm_boundary_rows),
        "inventory_family_count": len(family_rows),
        "remaining_family_count": len(remaining_rows),
        "certified_family_count": sum(row["certified_flag"] for row in family_rows),
        "theorem_critical_remaining_count": sum(
            row["theorem_critical_flag"] for row in remaining_rows
        ),
        "active_goal_required_remaining_count": sum(
            row["active_goal_required_flag"] for row in remaining_rows
        ),
        "finite_theorem_exploratory_remaining_count": sum(
            row["finite_theorem_exploratory_flag"] for row in remaining_rows
        ),
        "high_priority_remaining_count": sum(
            1 for row in remaining_rows if row["priority_code"] <= 1
        ),
        "proof_gap_count": sum(row["proof_gap_count"] for row in remaining_rows),
        "input_long_thm_certified_flag": input_certified,
        "inventory_bridge_flag": int(
            sorted(remaining_boundary_codes) == [0, 1, 2, 3, 4]
            and len(rank_rows) == len(thm_boundary_rows)
        ),
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
    family_hash = hashlib.sha256(
        digest_text(FAMILY_COLUMNS, family_rows).encode("ascii")
    ).hexdigest()
    rank_hash = hashlib.sha256(
        digest_text(RANK_COLUMNS, rank_rows).encode("ascii")
    ).hexdigest()
    return {
        "family_rows": family_rows,
        "rank_rows": rank_rows,
        "obs_rows": obs_rows,
        "family_table": table_from_rows(FAMILY_COLUMNS, family_rows),
        "rank_table": table_from_rows(RANK_COLUMNS, rank_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "family_hash": family_hash,
        "rank_hash": rank_hash,
        "obs": obs,
        "input_reports": {"long_thm": thm_report},
        "source_boundary_rows": thm_boundary_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    source_boundaries = rows["source_boundary_rows"]
    checks = {
        "input_certified": obs["input_long_thm_certified_flag"] == 1,
        "source_boundary_match": (
            obs["source_boundary_count"] == 5
            and all(row["future_work_flag"] == 1 for row in source_boundaries)
            and all(row["finite_theorem_required_flag"] == 0 for row in source_boundaries)
        ),
        "inventory_split_exact": (
            obs["inventory_family_count"],
            obs["remaining_family_count"],
            obs["certified_family_count"],
            obs["theorem_critical_remaining_count"],
            obs["active_goal_required_remaining_count"],
        )
        == (6, 5, 1, 0, 5),
        "rank_total_order": (
            [row["emission_order"] for row in rows["rank_rows"]] == [0, 1, 2, 3, 4]
            and sorted(row["family_id"] for row in rows["rank_rows"]) == [1, 2, 3, 4, 5]
        ),
        "fingerprints_exact": (
            rows["family_hash"] == FAMILY_TEXT_HASH and rows["rank_hash"] == RANK_TEXT_HASH
        ),
        "goal_not_overclaimed": obs["complete_goal_claim_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["family_table"].shape),
            tuple(rows["rank_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (6, len(FAMILY_COLUMNS)),
            (5, len(RANK_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": INVENTORY_ID,
        "classification": "finite_line_invariant_inventory",
        "input_theorem": {
            "line_point_count": obs["line_point_count"],
            "tensor_support_count": obs["tensor_support_count"],
            "source_boundary_count": obs["source_boundary_count"],
            "input_long_thm_certified_flag": obs["input_long_thm_certified_flag"],
        },
        "inventory": {
            "family_count": obs["inventory_family_count"],
            "remaining_family_count": obs["remaining_family_count"],
            "certified_family_count": obs["certified_family_count"],
            "theorem_critical_remaining_count": obs[
                "theorem_critical_remaining_count"
            ],
            "active_goal_required_remaining_count": obs[
                "active_goal_required_remaining_count"
            ],
            "finite_theorem_exploratory_remaining_count": obs[
                "finite_theorem_exploratory_remaining_count"
            ],
            "high_priority_remaining_count": obs["high_priority_remaining_count"],
            "proof_gap_count": obs["proof_gap_count"],
            "family_text_sha256": rows["family_hash"],
            "family_table_sha256": sha_array(rows["family_table"]),
        },
        "ranking": {
            "rank_row_count": len(rows["rank_rows"]),
            "rank_text_sha256": rows["rank_hash"],
            "rank_table_sha256": sha_array(rows["rank_table"]),
            "next_codes": {
                "0": "long_inv_exhaust",
                "1": "long_assoc",
                "2": "long_h16",
                "3": "long_measure",
                "4": "long_paths",
            },
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    inv_payload = {
        "schema": "long.inv@1",
        "object": "finite_line_invariant_inventory",
        "status": STATUS if all(checks.values()) else "LONG_INV_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.inv.report@1",
        "status": inv_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_inv certifies an inventory split downstream of long_thm: the "
            "finite tensor-lookup theorem is closed, while five broader invariant "
            "families remain open and are ranked by immediate value."
        ),
        "stage_protocol": {
            "draft": "read long_thm theorem status and unresolved boundary rows",
            "witness": "emit invariant-family rows and a total priority order",
            "coherence": "check boundary coverage, rank order, table shapes, and hashes",
            "closure": "certify inventory status without claiming the open families are solved",
            "emit": "write long_inv artifacts and verifier hook",
        },
        "inputs": {
            "long_thm_report": input_entry(
                LONG_THM_REPORT,
                {"status": rows["input_reports"]["long_thm"].get("status")},
            ),
            "long_thm_boundary": input_entry(
                LONG_THM_BOUNDARY,
                {"columns": LONG_THM_BOUNDARY_COLUMNS},
            ),
            "long_thm_tables": input_entry(LONG_THM_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "inv": relpath(OUT_DIR / "inv.json"),
            "family_csv": relpath(OUT_DIR / "family.csv"),
            "rank_csv": relpath(OUT_DIR / "rank.csv"),
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
                "finite theorem closure remains separated from broader invariant discovery",
                "the five open invariant families are not required for the finite theorem",
                "the active discovery path has a concrete priority order",
                "the broader goal is still explicitly open",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic C985 associator composition",
                "a probability measure on the full raw tensor support",
                "all raw product paths in each fiber",
                "a genuine horizon-16 profunctor",
                "exhaustiveness of every invariant of the finite line address space",
            ],
        },
        "next_highest_yield_item": (
            "Build long_pobj: test whether the current finite-line path witnesses "
            "upgrade to a closed path object."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.inv.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.inv.manifest@1",
        "name": INVENTORY_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "inv": inv_payload,
        "family_csv": csv_text(FAMILY_COLUMNS, rows["family_rows"]),
        "rank_csv": csv_text(RANK_COLUMNS, rows["rank_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "family_table": rows["family_table"],
        "rank_table": rows["rank_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "report": report,
        "manifest": manifest,
        "computed_hashes": {
            "family_text_sha256": rows["family_hash"],
            "rank_text_sha256": rows["rank_hash"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != INVENTORY_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": INVENTORY_ID,
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
    write_json(OUT_DIR / "inv.json", payloads["inv"])
    (OUT_DIR / "family.csv").write_text(payloads["family_csv"], encoding="utf-8")
    (OUT_DIR / "rank.csv").write_text(payloads["rank_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        family_table=payloads["family_table"],
        rank_table=payloads["rank_table"],
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
                "computed_hashes": payloads["computed_hashes"],
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
