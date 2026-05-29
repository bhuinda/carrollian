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
C985_FINAL_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_final_multifusion_certificate"
    / "report.json"
)
LONG_H16_REPORT = D20_INVARIANTS / "proof_obligations" / "long_h16" / "report.json"
LONG_PATHS_REPORT = D20_INVARIANTS / "proof_obligations" / "long_paths" / "report.json"
LONG_MEASURE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_measure" / "report.json"
LONG_INV_EXHAUST_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "long_inv_exhaust" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_long_inv.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_inv.py"

FAMILY_TEXT_HASH = "942cb23c67bf44224aa534f208847f9c2e5606fb65cf03a75a88dd885e7296af"
RANK_TEXT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

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
    c985_report = load_json(C985_FINAL_REPORT)
    h16_report = load_json(LONG_H16_REPORT)
    paths_report = load_json(LONG_PATHS_REPORT)
    measure_report = load_json(LONG_MEASURE_REPORT)
    inv_exhaust_report = load_json(LONG_INV_EXHAUST_REPORT)
    thm_boundary_rows = read_int_csv(LONG_THM_BOUNDARY)
    thm_witness = thm_report.get("witness", {})
    finite_theorem = thm_witness.get("finite_theorem", {})
    input_certified = int(
        thm_report.get("status") == LONG_THM_STATUS
        and thm_report.get("all_checks_pass") is True
    )
    assoc_retired = int(
        c985_report.get("status")
        == "C985_FINITE_SEMISIMPLE_MULTIFUSION_CATEGORY_CERTIFIED"
        and c985_report.get("all_checks_pass") is True
        and "finite semisimple multi-fusion category status for C985"
        in c985_report.get("closure_boundary", {}).get("certifies", [])
    )
    h16_summary = h16_report.get("witness", {}).get("summary", {})
    h16_retired = int(
        h16_report.get("status") == "LONG_H16_BOUNDARY_CERTIFIED"
        and h16_report.get("all_checks_pass") is True
        and int(h16_summary.get("current_model_obstruction_flag", 0)) == 1
        and int(h16_summary.get("active_h16_frontier_flag", -1)) == 0
        and "the current-model h16 active frontier is closed as an obstruction under the certified artifact constraints"
        in h16_report.get("closure_boundary", {}).get("certifies", [])
    )
    paths_retired = int(
        paths_report.get("status") == "LONG_PATHS_CERTIFIED"
        and paths_report.get("all_checks_pass") is True
        and "all 288 current active-component sum fibers have exact compressed raw product-family counts"
        in paths_report.get("closure_boundary", {}).get("certifies", [])
    )
    measure_summary = measure_report.get("witness", {}).get("summary", {})
    measure_retired = int(
        measure_report.get("status") == "LONG_MEASURE_CERTIFIED"
        and measure_report.get("all_checks_pass") is True
        and int(measure_summary.get("scoped_probability_law_flag", 0)) == 1
        and int(measure_summary.get("full_raw_scope_gap_flag", 0)) == 1
        and int(measure_summary.get("full_raw_measure_certified_flag", -1)) == 0
        and "the full raw-support gap that prevents treating the scoped laws as full raw-support measures in the current ontology"
        in measure_report.get("closure_boundary", {}).get("certifies", [])
    )
    inv_exhaust_summary = inv_exhaust_report.get("witness", {}).get("summary", {})
    inv_exhaust_retired = int(
        inv_exhaust_report.get("status") == "LONG_INV_EXHAUST_CERTIFIED"
        and inv_exhaust_report.get("all_checks_pass") is True
        and int(inv_exhaust_summary.get("current_inventory_exhaustive_flag", 0)) == 1
        and int(inv_exhaust_summary.get("active_frontier_remaining_count", -1)) == 0
        and int(inv_exhaust_summary.get("absolute_exhaustiveness_claim_flag", -1))
        == 0
        and "the current finite-line invariant-family inventory has zero active frontier rows under the focused oracle ontology"
        in inv_exhaust_report.get("closure_boundary", {}).get("certifies", [])
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
            "priority_code": 2,
            "scope_code": 3,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1 - inv_exhaust_retired,
            "certified_flag": inv_exhaust_retired,
            "finite_theorem_exploratory_flag": 1 - inv_exhaust_retired,
            "proof_gap_count": 1 - inv_exhaust_retired,
        },
        {
            "family_id": 2,
            "family_code": 0,
            "source_boundary_code": 0,
            "priority_code": 1,
            "scope_code": 0,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1 - assoc_retired,
            "certified_flag": assoc_retired,
            "finite_theorem_exploratory_flag": 1 - assoc_retired,
            "proof_gap_count": 1 - assoc_retired,
        },
        {
            "family_id": 3,
            "family_code": 3,
            "source_boundary_code": 3,
            "priority_code": 1,
            "scope_code": 2,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1 - h16_retired,
            "certified_flag": h16_retired,
            "finite_theorem_exploratory_flag": 1 - h16_retired,
            "proof_gap_count": 1 - h16_retired,
        },
        {
            "family_id": 4,
            "family_code": 1,
            "source_boundary_code": 1,
            "priority_code": 0,
            "scope_code": 1,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1 - measure_retired,
            "certified_flag": measure_retired,
            "finite_theorem_exploratory_flag": 1 - measure_retired,
            "proof_gap_count": 1 - measure_retired,
        },
        {
            "family_id": 5,
            "family_code": 2,
            "source_boundary_code": 2,
            "priority_code": 9,
            "scope_code": 1,
            "theorem_critical_flag": 0,
            "active_goal_required_flag": 1 - paths_retired,
            "certified_flag": paths_retired,
            "finite_theorem_exploratory_flag": 1 - paths_retired,
            "proof_gap_count": 1 - paths_retired,
        },
    ]
    rank_rows = []
    if not inv_exhaust_retired:
        rank_rows.append(
            {
                "rank_id": 0,
                "family_id": 1,
                "priority_code": 2,
                "blocking_code": 4,
                "next_action_code": 0,
                "depends_on_family_code": -1,
                "emission_order": 0,
            }
        )
    remaining_rows = [row for row in family_rows if row["certified_flag"] == 0]
    remaining_boundary_codes = [
        row["source_boundary_code"]
        for row in remaining_rows
        if row["source_boundary_code"] >= 0
    ]
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
            sorted(remaining_boundary_codes) == []
            and len(rank_rows) == len(remaining_rows)
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
        "rank_table": table_from_rows(RANK_COLUMNS, rank_rows)
        if rank_rows
        else np.zeros((0, len(RANK_COLUMNS)), dtype=np.int64),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "family_hash": family_hash,
        "rank_hash": rank_hash,
        "obs": obs,
        "input_reports": {
            "long_thm": thm_report,
            "c985_final": c985_report,
            "long_h16": h16_report,
            "long_paths": paths_report,
            "long_measure": measure_report,
            "long_inv_exhaust": inv_exhaust_report,
        },
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
        == (6, 0, 6, 0, 0),
        "rank_total_order": rows["rank_rows"] == [],
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
            (0, len(RANK_COLUMNS)),
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
            "next_codes": {},
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
            "finite tensor-lookup theorem is closed, semantic C985 associator debt "
            "has been retired by the passing C985 final oracle, the current "
            "horizon-16 current-model obstruction has been retired by long_h16 "
            "without claiming absolute nonexistence under changed models, "
            "compressed active raw product-path accounting "
            "has been retired by long_paths, scoped active-product measure debt "
            "has been retired by long_measure as a scoped-law/full-gap boundary, "
            "and bounded finite-line inventory exhaustiveness has been retired "
            "by long_inv_exhaust under the focused oracle ontology."
        ),
        "stage_protocol": {
            "draft": "read long_thm theorem status and unresolved boundary rows",
            "witness": "emit invariant-family rows and a total priority order",
            "coherence": "check boundary coverage, rank order, table shapes, and hashes",
            "closure": "certify inventory status without claiming absolute invariant omniscience outside the oracle ontology",
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
            "c985_final_report": input_entry(
                C985_FINAL_REPORT,
                {"status": rows["input_reports"]["c985_final"].get("status")},
            ),
            "long_h16_report": input_entry(
                LONG_H16_REPORT,
                {"status": rows["input_reports"]["long_h16"].get("status")},
            ),
            "long_paths_report": input_entry(
                LONG_PATHS_REPORT,
                {"status": rows["input_reports"]["long_paths"].get("status")},
            ),
            "long_measure_report": input_entry(
                LONG_MEASURE_REPORT,
                {"status": rows["input_reports"]["long_measure"].get("status")},
            ),
            "long_inv_exhaust_report": input_entry(
                LONG_INV_EXHAUST_REPORT,
                {
                    "status": rows["input_reports"]["long_inv_exhaust"].get(
                        "status"
                    )
                },
            ),
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
                "semantic C985 associator debt is retired by the focused C985 final certificate",
                "the current horizon-16 active frontier is retired by the focused current-model obstruction certificate",
                "compressed active raw product-path accounting is retired by long_paths",
                "scoped active-product measure debt is retired by long_measure while full raw-support claims remain separated",
                "bounded finite-line inventory cover is retired by long_inv_exhaust under the focused oracle ontology",
                "there are zero remaining focused inventory-family rows",
                "the broader goal is still explicitly open",
            ],
            "does_not_certify_because_out_of_scope": [
                "materialized raw-address rows for every raw path",
                "absolute nonexistence of a genuine horizon-16 profunctor under changed object/support models",
                "absolute exhaustiveness of every conceivable invariant outside the current oracle ontology",
            ],
        },
        "next_highest_yield_item": (
            "Focused theorem-debt frontier is empty; defer broad integration "
            "gates until the operator permits long gates."
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
