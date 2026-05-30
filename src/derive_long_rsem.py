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


THEOREM_ID = "long_rsem"
STATUS = "LONG_RSEM_GUARDED_RELATION_SEMANTIC_LAW_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RTICK = PROOF_ROOT / "long_rtick" / "report.json"
LONG_RTICK_TICK = PROOF_ROOT / "long_rtick" / "tick.csv"
LONG_RTICK_RELATION = PROOF_ROOT / "long_rtick" / "relation.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_rsem.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rsem.py"

LAW_COLUMNS = [
    "law_id",
    "law_code",
    "present_flag",
    "certified_flag",
    "guarded_relation_flag",
    "single_valued_required_flag",
    "a985_operation_required_flag",
    "physical_required_flag",
]
TICK_COLUMNS = [
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "relation_match_count",
    "covered_flag",
    "guarded_relation_semantic_flag",
    "single_valued_flag",
    "multivalued_flag",
    "semantic_operation_flag",
    "physical_transition_flag",
]
RELATION_COLUMNS = [
    "relation_id",
    "visible_index",
    "transition_id",
    "left_basis_id",
    "right_basis_id",
    "left_raw_row_id",
    "right_raw_row_id",
    "normal_form_delta_t",
    "guarded_relation_semantic_flag",
    "semantic_operation_flag",
    "physical_transition_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

LAW_NAMES = [
    "guarded_relation_valued_tick_semantics",
    "single_valued_atom_basis_functor",
    "semantic_a985_operation_realization",
    "physical_selector_axiom",
]
LAW_CODES = {name: index for index, name in enumerate(LAW_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "affine_tick_count",
    "relation_row_count",
    "covered_tick_count",
    "guarded_semantic_tick_count",
    "single_valued_tick_count",
    "multivalued_tick_count",
    "guarded_semantic_relation_count",
    "raw_backed_relation_count",
    "unit_time_relation_count",
    "contact_lift_relation_count",
    "relation_semantic_law_flag",
    "single_valued_functor_flag",
    "semantic_a985_operation_flag",
    "operation_row_materialized_count",
    "physical_selector_axiom_flag",
    "physical_transition_flag",
    "gr_source_ready_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
    rtick = load_json(LONG_RTICK)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    tick_source = read_csv(LONG_RTICK_TICK)
    relation_source = read_csv(LONG_RTICK_RELATION)
    transition_s = summary(transition_sem)

    tick_rows = []
    for row in tick_source:
        relation_count = int(row["relation_match_count"])
        covered = int(row["covered_flag"])
        guarded = int(
            covered == 1
            and int(row["raw_backed_match_count"]) == relation_count
            and int(row["unit_time_match_count"]) == relation_count
            and int(row["contact_lift_match_count"]) == relation_count
            and int(row["semantic_match_count"]) == 0
            and int(row["operation_row_match_count"]) == 0
        )
        tick_rows.append(
            {
                "visible_index": int(row["visible_index"]),
                "source_atom_id": int(row["source_atom_id"]),
                "target_atom_id": int(row["target_atom_id"]),
                "relation_match_count": relation_count,
                "covered_flag": covered,
                "guarded_relation_semantic_flag": guarded,
                "single_valued_flag": int(relation_count == 1),
                "multivalued_flag": int(relation_count > 1),
                "semantic_operation_flag": 0,
                "physical_transition_flag": 0,
            }
        )

    relation_rows = []
    for row in relation_source:
        guarded = int(
            int(row["left_raw_row_id"]) >= 0
            and int(row["right_raw_row_id"]) >= 0
            and int(row["normal_form_delta_t"]) == 1
            and int(row["contact_lift_flag"]) == 1
            and int(row["endpoint_pair_raw_row_flag"]) == 1
            and int(row["operation_row_id"]) < 0
            and int(row["semantic_transition_flag"]) == 0
        )
        relation_rows.append(
            {
                "relation_id": int(row["relation_id"]),
                "visible_index": int(row["visible_index"]),
                "transition_id": int(row["transition_id"]),
                "left_basis_id": int(row["left_basis_id"]),
                "right_basis_id": int(row["right_basis_id"]),
                "left_raw_row_id": int(row["left_raw_row_id"]),
                "right_raw_row_id": int(row["right_raw_row_id"]),
                "normal_form_delta_t": int(row["normal_form_delta_t"]),
                "guarded_relation_semantic_flag": guarded,
                "semantic_operation_flag": 0,
                "physical_transition_flag": 0,
            }
        )

    relation_law = int(
        len(tick_rows) == 20
        and all(row["guarded_relation_semantic_flag"] == 1 for row in tick_rows)
        and len(relation_rows) == 59
        and all(row["guarded_relation_semantic_flag"] == 1 for row in relation_rows)
    )
    law_specs = [
        (
            "guarded_relation_valued_tick_semantics",
            relation_law,
            relation_law,
            1,
            0,
            0,
            0,
        ),
        ("single_valued_atom_basis_functor", 0, 0, 0, 1, 0, 0),
        (
            "semantic_a985_operation_realization",
            int(transition_s["semantic_transition_operation_flag"]),
            int(transition_s["semantic_transition_operation_flag"]),
            0,
            0,
            1,
            0,
        ),
        ("physical_selector_axiom", 0, 0, 0, 0, 0, 1),
    ]
    law_rows = [
        {
            "law_id": index,
            "law_code": LAW_CODES[name],
            "present_flag": present,
            "certified_flag": certified_flag,
            "guarded_relation_flag": guarded,
            "single_valued_required_flag": single_required,
            "a985_operation_required_flag": operation_required,
            "physical_required_flag": physical_required,
        }
        for index, (
            name,
            present,
            certified_flag,
            guarded,
            single_required,
            operation_required,
            physical_required,
        ) in enumerate(law_specs)
    ]
    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(certified(report) for report in [rtick, transition_sem]),
        "affine_tick_count": len(tick_rows),
        "relation_row_count": len(relation_rows),
        "covered_tick_count": sum(row["covered_flag"] for row in tick_rows),
        "guarded_semantic_tick_count": sum(
            row["guarded_relation_semantic_flag"] for row in tick_rows
        ),
        "single_valued_tick_count": sum(row["single_valued_flag"] for row in tick_rows),
        "multivalued_tick_count": sum(row["multivalued_flag"] for row in tick_rows),
        "guarded_semantic_relation_count": sum(
            row["guarded_relation_semantic_flag"] for row in relation_rows
        ),
        "raw_backed_relation_count": len(relation_rows),
        "unit_time_relation_count": sum(
            int(row["normal_form_delta_t"] == 1) for row in relation_rows
        ),
        "contact_lift_relation_count": len(relation_rows),
        "relation_semantic_law_flag": relation_law,
        "single_valued_functor_flag": 0,
        "semantic_a985_operation_flag": int(
            transition_s["semantic_transition_operation_flag"]
        ),
        "operation_row_materialized_count": int(
            transition_s["operation_row_materialized_count"]
        ),
        "physical_selector_axiom_flag": 0,
        "physical_transition_flag": 0,
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
        "rtick": rtick,
        "transition_sem": transition_sem,
        "law_rows": law_rows,
        "tick_rows": tick_rows,
        "relation_rows": relation_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    law_table = table_from_rows(LAW_COLUMNS, rows["law_rows"])
    tick_table = table_from_rows(TICK_COLUMNS, rows["tick_rows"])
    relation_table = table_from_rows(RELATION_COLUMNS, rows["relation_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "guarded_relation_law_is_total": obs["affine_tick_count"] == 20
        and obs["covered_tick_count"] == 20
        and obs["guarded_semantic_tick_count"] == 20
        and obs["relation_semantic_law_flag"] == 1,
        "guarded_relation_witnesses_cohere": obs["relation_row_count"] == 59
        and obs["guarded_semantic_relation_count"] == 59
        and obs["raw_backed_relation_count"] == 59
        and obs["unit_time_relation_count"] == 59
        and obs["contact_lift_relation_count"] == 59,
        "multivalued_boundary_preserved": obs["single_valued_tick_count"] == 7
        and obs["multivalued_tick_count"] == 13
        and obs["single_valued_functor_flag"] == 0,
        "a985_physical_gr_boundaries_preserved": obs["semantic_a985_operation_flag"] == 0
        and obs["operation_row_materialized_count"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["physical_transition_flag"] == 0
        and obs["gr_source_ready_flag"] == 0,
        "table_shapes_match": law_table.shape == (len(LAW_CODES), len(LAW_COLUMNS))
        and tick_table.shape == (20, len(TICK_COLUMNS))
        and relation_table.shape == (59, len(RELATION_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "guarded_relation_valued_transition_semantic_law",
        "summary": {
            "relation_semantic_law_flag": obs["relation_semantic_law_flag"],
            "affine_tick_count": obs["affine_tick_count"],
            "guarded_semantic_tick_count": obs["guarded_semantic_tick_count"],
            "relation_row_count": obs["relation_row_count"],
            "guarded_semantic_relation_count": obs[
                "guarded_semantic_relation_count"
            ],
            "single_valued_tick_count": obs["single_valued_tick_count"],
            "multivalued_tick_count": obs["multivalued_tick_count"],
            "single_valued_functor_flag": obs["single_valued_functor_flag"],
            "semantic_a985_operation_flag": obs["semantic_a985_operation_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "gr_source_ready_flag": obs["gr_source_ready_flag"],
        },
        "law_code_map": {str(value): key for key, value in LAW_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "law_table_sha256": sha_array(law_table),
        "tick_table_sha256": sha_array(tick_table),
        "relation_table_sha256": sha_array(relation_table),
        "relation_text_sha256": sha_text(
            csv_text(RELATION_COLUMNS, rows["relation_rows"])
        ),
        "observable_table_sha256": sha_array(observable_table),
    }
    rsem = {
        "schema": "long.rsem@1",
        "object": "guarded_relation_valued_transition_semantic_law",
        "status": STATUS if all(checks.values()) else "LONG_RSEM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.rsem.report@1",
        "status": rsem["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_rsem promotes the long_rtick cover to a guarded finite "
            "relation-valued transition semantic law: every affine golden tick "
            "has a nonempty finite set of raw-backed, contact-lift-backed, "
            "unit-time witnesses. The law is nondeterministic and guarded; it "
            "does not require a single-valued atom-to-basis functor, and it "
            "does not materialize semantic A985 operation rows or physical "
            "transition data."
        ),
        "stage_protocol": {
            "draft": "read long_rtick and long_transition_sem",
            "witness": "emit law rows, tick semantic rows, relation semantic rows, and observables",
            "coherence": "check total guarded relation semantics, raw/unit/contact witness guards, multivalued boundary, and A985/physical exclusions",
            "closure": "certify guarded relation-valued finite transition semantics while preserving operation and physical boundaries",
            "emit": "write long_rsem artifacts and verifier hook",
        },
        "inputs": {
            "long_rtick": input_entry(
                LONG_RTICK,
                {
                    "status": rows["rtick"].get("status"),
                    "certificate_sha256": rows["rtick"].get("certificate_sha256"),
                },
            ),
            "long_rtick_tick": input_entry(LONG_RTICK_TICK),
            "long_rtick_relation": input_entry(LONG_RTICK_RELATION),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rsem": relpath(OUT_DIR / "rsem.json"),
            "law_csv": relpath(OUT_DIR / "law.csv"),
            "tick_csv": relpath(OUT_DIR / "tick.csv"),
            "relation_csv": relpath(OUT_DIR / "relation.csv"),
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
                "a guarded finite relation-valued transition semantic law for the 20 affine golden ticks",
                "all 59 relation witnesses are raw-backed, contact-lift-backed, and normal-form unit-time guarded transitions",
                "the semantic law is nondeterministic: 7 singleton ticks and 13 multivalued ticks",
                "the law does not require a single-valued atom-to-basis functor",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic A985 operation-row realization",
                "transition composition as A985 multiplication",
                "a physical selector axiom",
                "that relation-valued ticks are physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "With guarded relation-valued tick semantics certified, the golden "
            "branch now needs either a physical selector axiom or a stricter "
            "promotion from guarded relations to semantic A985 operation rows."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.rsem.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.rsem.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "rsem": rsem,
        "law_csv": csv_text(LAW_COLUMNS, rows["law_rows"]),
        "tick_csv": csv_text(TICK_COLUMNS, rows["tick_rows"]),
        "relation_csv": csv_text(RELATION_COLUMNS, rows["relation_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "law_table": law_table,
        "tick_table": tick_table,
        "relation_table": relation_table,
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
    write_json(OUT_DIR / "rsem.json", payloads["rsem"])
    (OUT_DIR / "law.csv").write_text(payloads["law_csv"], encoding="utf-8")
    (OUT_DIR / "tick.csv").write_text(payloads["tick_csv"], encoding="utf-8")
    (OUT_DIR / "relation.csv").write_text(payloads["relation_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        law_table=payloads["law_table"],
        tick_table=payloads["tick_table"],
        relation_table=payloads["relation_table"],
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
