from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
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
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59p3u"
STATUS = "LONG_C59P3U_FORMAL_STRESS_SOURCE_OPERATION_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3F = PROOF_ROOT / "long_c59p3f" / "report.json"
LONG_C59P3F_ASSIGNMENT = PROOF_ROOT / "long_c59p3f" / "assignment.csv"
LONG_OPROM = PROOF_ROOT / "long_oprom" / "report.json"
LONG_OPROM_PROMOTION = PROOF_ROOT / "long_oprom" / "promotion.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3u.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3u.py"

OPCHECK_COLUMNS = [
    "relation_id",
    "visible_index",
    "transition_id",
    "stress_edge_id",
    "rule_code",
    "formal_pushforward_flag",
    "promotion_transition_present_flag",
    "transition_row_present_flag",
    "operation_row_id",
    "operation_row_present_flag",
    "semantic_transition_flag",
    "operation_backed_stress_source_flag",
    "obstruction_code",
]
SOURCE_COLUMNS = [
    "source_row_id",
    "stress_edge_id",
    "assignment_count",
    "direct_assignment_count",
    "reverse_assignment_count",
    "fallback_assignment_count",
    "signed_tension_sum_scaled",
    "abs_tension_sum_scaled",
    "operation_backed_count",
    "semantic_transition_count",
    "formal_source_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

GAP_NAMES = [
    "formal_stress_source_ledger",
    "operation_row_promotion",
    "semantic_transition_flags",
    "physical_selector_axiom",
    "stress_conservation_balance",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "assignment_row_count",
    "promotion_row_count",
    "transition_row_count",
    "joined_assignment_count",
    "source_row_count",
    "direct_assignment_count",
    "reverse_assignment_count",
    "fallback_assignment_count",
    "formal_pushforward_count",
    "operation_row_match_count",
    "semantic_transition_match_count",
    "operation_backed_source_count",
    "source_assignment_total",
    "source_signed_tension_total_scaled",
    "source_abs_tension_total_scaled",
    "source_max_assignment_multiplicity",
    "physical_selector_axiom_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def build_rows() -> dict[str, Any]:
    c59p3f = load_json(LONG_C59P3F)
    oprom = load_json(LONG_OPROM)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    _, assignment_rows_raw = read_csv_rows(LONG_C59P3F_ASSIGNMENT)
    _, promotion_rows_raw = read_csv_rows(LONG_OPROM_PROMOTION)
    _, transition_rows_raw = read_csv_rows(LONG_TRANSITION_CSV)

    promotion_by_relation = {
        int(row["relation_id"]): row for row in promotion_rows_raw
    }
    transition_by_id = {
        int(row["transition_id"]): row for row in transition_rows_raw
    }

    opcheck_rows = []
    source_acc: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            "assignment_count": 0,
            "direct_assignment_count": 0,
            "reverse_assignment_count": 0,
            "fallback_assignment_count": 0,
            "signed_tension_sum_scaled": 0,
            "abs_tension_sum_scaled": 0,
            "operation_backed_count": 0,
            "semantic_transition_count": 0,
        }
    )
    for row in assignment_rows_raw:
        relation_id = int(row["relation_id"])
        transition_id = int(row["transition_id"])
        stress_edge_id = int(row["stress_edge_id"])
        rule_code = int(row["rule_code"])
        promotion = promotion_by_relation.get(relation_id)
        transition = transition_by_id.get(transition_id)
        promotion_present = int(promotion is not None)
        transition_present = int(transition is not None)
        operation_row_id = int(promotion["operation_row_id"]) if promotion else -1
        operation_row_present = (
            int(promotion["operation_row_present_flag"]) if promotion else 0
        )
        semantic_transition = (
            int(promotion["semantic_transition_flag"]) if promotion else 0
        )
        operation_backed = int(
            int(row["formal_pushforward_flag"]) == 1
            and promotion_present == 1
            and transition_present == 1
            and operation_row_present == 1
            and semantic_transition == 1
        )
        opcheck_rows.append(
            {
                "relation_id": relation_id,
                "visible_index": int(row["visible_index"]),
                "transition_id": transition_id,
                "stress_edge_id": stress_edge_id,
                "rule_code": rule_code,
                "formal_pushforward_flag": int(row["formal_pushforward_flag"]),
                "promotion_transition_present_flag": promotion_present,
                "transition_row_present_flag": transition_present,
                "operation_row_id": operation_row_id,
                "operation_row_present_flag": operation_row_present,
                "semantic_transition_flag": semantic_transition,
                "operation_backed_stress_source_flag": operation_backed,
                "obstruction_code": int(operation_backed == 0),
            }
        )
        acc = source_acc[stress_edge_id]
        acc["assignment_count"] += 1
        acc["direct_assignment_count"] += int(rule_code == 0)
        acc["reverse_assignment_count"] += int(rule_code == 1)
        acc["fallback_assignment_count"] += int(rule_code == 2)
        acc["signed_tension_sum_scaled"] += int(row["signed_tension_scaled"])
        acc["abs_tension_sum_scaled"] += int(row["abs_tension_scaled"])
        acc["operation_backed_count"] += operation_backed
        acc["semantic_transition_count"] += semantic_transition

    source_rows = []
    for source_row_id, stress_edge_id in enumerate(sorted(source_acc)):
        acc = source_acc[stress_edge_id]
        source_rows.append(
            {
                "source_row_id": source_row_id,
                "stress_edge_id": stress_edge_id,
                "assignment_count": acc["assignment_count"],
                "direct_assignment_count": acc["direct_assignment_count"],
                "reverse_assignment_count": acc["reverse_assignment_count"],
                "fallback_assignment_count": acc["fallback_assignment_count"],
                "signed_tension_sum_scaled": acc["signed_tension_sum_scaled"],
                "abs_tension_sum_scaled": acc["abs_tension_sum_scaled"],
                "operation_backed_count": acc["operation_backed_count"],
                "semantic_transition_count": acc["semantic_transition_count"],
                "formal_source_flag": 1,
            }
        )

    obs = {
        "input_report_count": 3,
        "input_certified_count": int(certified(c59p3f))
        + int(certified(oprom))
        + int(certified(transition_sem)),
        "assignment_row_count": len(assignment_rows_raw),
        "promotion_row_count": len(promotion_rows_raw),
        "transition_row_count": len(transition_rows_raw),
        "joined_assignment_count": sum(
            row["promotion_transition_present_flag"] for row in opcheck_rows
        ),
        "source_row_count": len(source_rows),
        "direct_assignment_count": sum(
            row["direct_assignment_count"] for row in source_rows
        ),
        "reverse_assignment_count": sum(
            row["reverse_assignment_count"] for row in source_rows
        ),
        "fallback_assignment_count": sum(
            row["fallback_assignment_count"] for row in source_rows
        ),
        "formal_pushforward_count": sum(
            row["formal_pushforward_flag"] for row in opcheck_rows
        ),
        "operation_row_match_count": sum(
            row["operation_row_present_flag"] for row in opcheck_rows
        ),
        "semantic_transition_match_count": sum(
            row["semantic_transition_flag"] for row in opcheck_rows
        ),
        "operation_backed_source_count": sum(
            row["operation_backed_stress_source_flag"] for row in opcheck_rows
        ),
        "source_assignment_total": sum(row["assignment_count"] for row in source_rows),
        "source_signed_tension_total_scaled": sum(
            row["signed_tension_sum_scaled"] for row in source_rows
        ),
        "source_abs_tension_total_scaled": sum(
            row["abs_tension_sum_scaled"] for row in source_rows
        ),
        "source_max_assignment_multiplicity": max(
            row["assignment_count"] for row in source_rows
        ),
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["stress_conservation_balance"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["formal_stress_source_ledger"],
            "gap_code": GAP_CODES["formal_stress_source_ledger"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_row_promotion"],
            "gap_code": GAP_CODES["operation_row_promotion"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_flags"],
            "gap_code": GAP_CODES["semantic_transition_flags"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_conservation_balance"],
            "gap_code": GAP_CODES["stress_conservation_balance"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3f": c59p3f,
        "oprom": oprom,
        "transition_sem": transition_sem,
        "opcheck_rows": opcheck_rows,
        "source_rows": source_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    opcheck_table = table_from_rows(OPCHECK_COLUMNS, rows["opcheck_rows"])
    source_table = table_from_rows(SOURCE_COLUMNS, rows["source_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "assignment_join_total": obs["assignment_row_count"] == 59
        and obs["promotion_row_count"] == 59
        and obs["transition_row_count"] == 642
        and obs["joined_assignment_count"] == 59
        and obs["formal_pushforward_count"] == 59,
        "source_ledger_counts_match": obs["source_row_count"] == 14
        and obs["source_assignment_total"] == 59
        and obs["direct_assignment_count"] == 8
        and obs["reverse_assignment_count"] == 7
        and obs["fallback_assignment_count"] == 44
        and obs["source_max_assignment_multiplicity"] == 10,
        "source_ledger_sums_match": obs["source_signed_tension_total_scaled"]
        == -197809407552
        and obs["source_abs_tension_total_scaled"] == 354128490312,
        "operation_backing_absent": obs["operation_row_match_count"] == 0
        and obs["semantic_transition_match_count"] == 0
        and obs["operation_backed_source_count"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": opcheck_table.shape == (59, len(OPCHECK_COLUMNS))
        and source_table.shape == (14, len(SOURCE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "formal_stress_source_operation_gate",
        "summary": {
            "assignment_row_count": obs["assignment_row_count"],
            "source_row_count": obs["source_row_count"],
            "source_assignment_total": obs["source_assignment_total"],
            "source_signed_tension_total_scaled": obs[
                "source_signed_tension_total_scaled"
            ],
            "source_abs_tension_total_scaled": obs[
                "source_abs_tension_total_scaled"
            ],
            "operation_row_match_count": obs["operation_row_match_count"],
            "semantic_transition_match_count": obs["semantic_transition_match_count"],
            "operation_backed_source_count": obs["operation_backed_source_count"],
            "source_max_assignment_multiplicity": obs[
                "source_max_assignment_multiplicity"
            ],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "opcheck_table_sha256": sha_array(opcheck_table),
        "opcheck_text_sha256": sha_text(csv_text(OPCHECK_COLUMNS, rows["opcheck_rows"])),
        "source_table_sha256": sha_array(source_table),
        "source_text_sha256": sha_text(csv_text(SOURCE_COLUMNS, rows["source_rows"])),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3u = {
        "schema": "long.c59p3u@1",
        "object": "formal_stress_source_operation_gate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3U_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3u.report@1",
        "status": c59p3u["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3u joins the 59 formal stress assignments to the operation "
            "promotion and transition surfaces. The join is total, and it yields "
            "a 14-edge formal stress-source ledger, but zero assigned witnesses "
            "have operation rows or semantic transition flags. The source is "
            "therefore formal rather than operation-backed."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3f assignments, long_oprom promotions, and long_transition_sem rows",
            "witness": "emit per-assignment operation checks, formal source rows, gaps, and observables",
            "coherence": "check total joins, source ledgers, tension sums, and absent operation backing",
            "closure": "certify the formal stress-source operation gate",
            "emit": "write long_c59p3u artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3f": input_entry(
                LONG_C59P3F,
                {
                    "status": rows["c59p3f"].get("status"),
                    "certificate_sha256": rows["c59p3f"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3f_assignment": input_entry(LONG_C59P3F_ASSIGNMENT),
            "long_oprom": input_entry(
                LONG_OPROM,
                {
                    "status": rows["oprom"].get("status"),
                    "certificate_sha256": rows["oprom"].get("certificate_sha256"),
                },
            ),
            "long_oprom_promotion": input_entry(LONG_OPROM_PROMOTION),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3u": relpath(OUT_DIR / "c59p3u.json"),
            "opcheck_csv": relpath(OUT_DIR / "opcheck.csv"),
            "source_csv": relpath(OUT_DIR / "source.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "all 59 formal stress assignments join to promotion and transition rows",
                "the formal assignments induce a 14-edge stress-source ledger",
                "the formal source has signed tension total -197809407552 and absolute total 354128490312",
                "zero assigned witnesses have operation rows or semantic transition flags",
                "zero stress-source rows are operation-backed in the current boundary",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "semantic operation rows for the assigned witnesses",
                "semantic transition flags for the assigned witnesses",
                "a physical selector axiom",
                "stress-source conservation or balance",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Test conservation and balance of the 14-edge formal stress-source "
            "ledger, since operation backing is still absent."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3u.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3u.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3u": c59p3u,
        "opcheck_csv": csv_text(OPCHECK_COLUMNS, rows["opcheck_rows"]),
        "source_csv": csv_text(SOURCE_COLUMNS, rows["source_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "opcheck_table": opcheck_table,
        "source_table": source_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "c59p3u.json", payloads["c59p3u"])
    (OUT_DIR / "opcheck.csv").write_text(payloads["opcheck_csv"], encoding="utf-8")
    (OUT_DIR / "source.csv").write_text(payloads["source_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        opcheck_table=payloads["opcheck_table"],
        source_table=payloads["source_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
    )
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
