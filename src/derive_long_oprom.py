from __future__ import annotations

import csv
import hashlib
import json
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


THEOREM_ID = "long_oprom"
STATUS = "LONG_OPROM_GOLDEN_OPERATION_PROMOTION_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_oprom.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_oprom.py"

PROMOTION_COLUMNS = [
    "relation_id",
    "visible_index",
    "transition_id",
    "transition_row_present_flag",
    "guarded_relation_semantic_flag",
    "operation_row_id",
    "operation_row_present_flag",
    "semantic_transition_flag",
    "operation_promotion_flag",
    "obstruction_code",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "present_flag",
    "required_for_promotion_flag",
    "obstruction_flag",
    "row_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

GAP_NAMES = [
    "guarded_relation_witnesses_present",
    "contact_lift_transition_rows_present",
    "semantic_operation_rows_absent",
    "transition_composition_law_absent",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBSTRUCTION_NAMES = [
    "matched_contact_lift_has_no_a985_operation_row",
]
OBSTRUCTION_CODES = {name: index for index, name in enumerate(OBSTRUCTION_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "golden_relation_row_count",
    "transition_row_count",
    "matched_transition_row_count",
    "guarded_relation_row_count",
    "operation_row_match_count",
    "semantic_transition_match_count",
    "promotion_success_count",
    "promotion_blocked_count",
    "operation_promotion_flag",
    "semantic_a985_operation_flag",
    "transition_composition_law_flag",
    "physical_selector_axiom_flag",
    "gr_source_ready_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def build_rows() -> dict[str, Any]:
    rsem = load_json(LONG_RSEM)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    rsem_s = summary(rsem)
    transition_s = summary(transition_sem)
    relation_rows_source = read_csv_int(LONG_RSEM_RELATION)
    transition_rows_source = read_csv_int(LONG_TRANSITION_CSV)
    transition_by_id = {row["transition_id"]: row for row in transition_rows_source}

    promotion_rows = []
    for row in relation_rows_source:
        transition = transition_by_id.get(row["transition_id"])
        transition_present = int(transition is not None)
        operation_row_id = -1 if transition is None else int(transition["operation_row_id"])
        semantic_flag = 0 if transition is None else int(transition["semantic_transition_flag"])
        operation_present = int(operation_row_id >= 0)
        promoted = int(
            transition_present == 1
            and int(row["guarded_relation_semantic_flag"]) == 1
            and operation_present == 1
            and semantic_flag == 1
        )
        promotion_rows.append(
            {
                "relation_id": row["relation_id"],
                "visible_index": row["visible_index"],
                "transition_id": row["transition_id"],
                "transition_row_present_flag": transition_present,
                "guarded_relation_semantic_flag": row[
                    "guarded_relation_semantic_flag"
                ],
                "operation_row_id": operation_row_id,
                "operation_row_present_flag": operation_present,
                "semantic_transition_flag": semantic_flag,
                "operation_promotion_flag": promoted,
                "obstruction_code": OBSTRUCTION_CODES[
                    "matched_contact_lift_has_no_a985_operation_row"
                ],
            }
        )

    promotion_success = sum(row["operation_promotion_flag"] for row in promotion_rows)
    operation_matches = sum(row["operation_row_present_flag"] for row in promotion_rows)
    semantic_matches = sum(row["semantic_transition_flag"] for row in promotion_rows)
    promotion_flag = int(
        len(promotion_rows) == 59
        and promotion_success == 59
        and operation_matches == 59
        and semantic_matches == 59
    )
    gap_rows = [
        {
            "gap_id": 0,
            "gap_code": GAP_CODES["guarded_relation_witnesses_present"],
            "present_flag": int(int(rsem_s["relation_semantic_law_flag"]) == 1),
            "required_for_promotion_flag": 1,
            "obstruction_flag": 0,
            "row_count": len(relation_rows_source),
        },
        {
            "gap_id": 1,
            "gap_code": GAP_CODES["contact_lift_transition_rows_present"],
            "present_flag": int(
                sum(row["transition_row_present_flag"] for row in promotion_rows)
                == len(promotion_rows)
            ),
            "required_for_promotion_flag": 1,
            "obstruction_flag": 0,
            "row_count": sum(
                row["transition_row_present_flag"] for row in promotion_rows
            ),
        },
        {
            "gap_id": 2,
            "gap_code": GAP_CODES["semantic_operation_rows_absent"],
            "present_flag": int(operation_matches > 0),
            "required_for_promotion_flag": 1,
            "obstruction_flag": int(operation_matches == 0),
            "row_count": operation_matches,
        },
        {
            "gap_id": 3,
            "gap_code": GAP_CODES["transition_composition_law_absent"],
            "present_flag": 0,
            "required_for_promotion_flag": 1,
            "obstruction_flag": 1,
            "row_count": 0,
        },
    ]
    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(
            certified(report) for report in [rsem, transition_sem]
        ),
        "golden_relation_row_count": len(promotion_rows),
        "transition_row_count": len(transition_rows_source),
        "matched_transition_row_count": sum(
            row["transition_row_present_flag"] for row in promotion_rows
        ),
        "guarded_relation_row_count": sum(
            row["guarded_relation_semantic_flag"] for row in promotion_rows
        ),
        "operation_row_match_count": operation_matches,
        "semantic_transition_match_count": semantic_matches,
        "promotion_success_count": promotion_success,
        "promotion_blocked_count": len(promotion_rows) - promotion_success,
        "operation_promotion_flag": promotion_flag,
        "semantic_a985_operation_flag": int(
            transition_s["semantic_transition_operation_flag"]
        ),
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "gr_source_ready_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "rsem": rsem,
        "transition_sem": transition_sem,
        "promotion_rows": promotion_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    promotion_table = table_from_rows(PROMOTION_COLUMNS, rows["promotion_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "guarded_relations_match_contact_lift_transitions": obs[
            "golden_relation_row_count"
        ]
        == 59
        and obs["matched_transition_row_count"] == 59
        and obs["guarded_relation_row_count"] == 59,
        "operation_rows_absent_for_all_golden_relations": obs[
            "operation_row_match_count"
        ]
        == 0
        and obs["semantic_transition_match_count"] == 0
        and obs["promotion_success_count"] == 0
        and obs["promotion_blocked_count"] == 59
        and obs["operation_promotion_flag"] == 0,
        "downstream_physical_gr_boundaries_preserved": obs[
            "semantic_a985_operation_flag"
        ]
        == 0
        and obs["transition_composition_law_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["gr_source_ready_flag"] == 0,
        "table_shapes_match": promotion_table.shape
        == (59, len(PROMOTION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "golden_guarded_relation_operation_promotion_gate",
        "summary": {
            "golden_relation_row_count": obs["golden_relation_row_count"],
            "matched_transition_row_count": obs["matched_transition_row_count"],
            "guarded_relation_row_count": obs["guarded_relation_row_count"],
            "operation_row_match_count": obs["operation_row_match_count"],
            "semantic_transition_match_count": obs[
                "semantic_transition_match_count"
            ],
            "promotion_success_count": obs["promotion_success_count"],
            "promotion_blocked_count": obs["promotion_blocked_count"],
            "operation_promotion_flag": obs["operation_promotion_flag"],
            "semantic_a985_operation_flag": obs["semantic_a985_operation_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "gr_source_ready_flag": obs["gr_source_ready_flag"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "obstruction_code_map": {
            str(value): key for key, value in OBSTRUCTION_CODES.items()
        },
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "promotion_table_sha256": sha_array(promotion_table),
        "promotion_text_sha256": sha_text(
            csv_text(PROMOTION_COLUMNS, rows["promotion_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "gap_text_sha256": sha_text(csv_text(GAP_COLUMNS, rows["gap_rows"])),
        "observable_table_sha256": sha_array(observable_table),
    }
    oprom = {
        "schema": "long.oprom@1",
        "object": "golden_guarded_relation_operation_promotion_gate",
        "status": STATUS if all(checks.values()) else "LONG_OPROM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.oprom.report@1",
        "status": oprom["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_oprom tests whether the 59 guarded relation-valued golden "
            "tick witnesses can be promoted to semantic A985 operation rows "
            "under the current transition surface. Each guarded relation "
            "matches a contact-lift transition row, but none has an operation "
            "row or semantic transition flag. The golden relation law therefore "
            "remains a guarded transition law, not an A985 operation law."
        ),
        "stage_protocol": {
            "draft": "read long_rsem relation rows and long_transition_sem transition rows",
            "witness": "emit matched promotion rows, gap rows, and observables",
            "coherence": "check 59 guarded relation witnesses, transition-row matches, absent operation rows, and preserved physical boundary",
            "closure": "certify the current operation-promotion obstruction for the golden guarded relation law",
            "emit": "write long_oprom artifacts and verifier hook",
        },
        "inputs": {
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "long_rsem_relation": input_entry(LONG_RSEM_RELATION),
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
            "oprom": relpath(OUT_DIR / "oprom.json"),
            "promotion_csv": relpath(OUT_DIR / "promotion.csv"),
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
                "all 59 golden guarded relation witnesses match contact-lift transition rows",
                "zero of those 59 matched transitions has a semantic A985 operation row",
                "zero of those 59 matched transitions has semantic_transition_flag=1",
                "the golden guarded relation law is not promoted to semantic A985 operations in the current artifact boundary",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute impossibility of future operation-row promotion",
                "a transition composition law from contact lifts to A985 multiplication",
                "a physical selector axiom",
                "that relation-valued ticks are physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Construct actual A985 operation rows for the 59 matched golden "
            "relation witnesses, or certify a stronger no-go theorem showing "
            "why contact-lift transitions cannot be promoted under the current "
            "A985 operation schema."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.oprom.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.oprom.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "oprom": oprom,
        "promotion_csv": csv_text(PROMOTION_COLUMNS, rows["promotion_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "promotion_table": promotion_table,
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
    write_json(OUT_DIR / "oprom.json", payloads["oprom"])
    (OUT_DIR / "promotion.csv").write_text(
        payloads["promotion_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        promotion_table=payloads["promotion_table"],
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
