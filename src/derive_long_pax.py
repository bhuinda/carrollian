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


THEOREM_ID = "long_pax"
STATUS = "LONG_PAX_PHYSICAL_SELECTOR_CANDIDATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_GLAW = PROOF_ROOT / "long_glaw" / "report.json"
LONG_GCLK = PROOF_ROOT / "long_gclk" / "report.json"
LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_pax.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_pax.py"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "candidate_code",
    "selected_class_id",
    "selected_branch_code",
    "formal_golden_law_flag",
    "affine_clock_flag",
    "guarded_relation_semantic_flag",
    "candidate_admissible_flag",
    "axiom_accepted_flag",
    "physical_selector_axiom_flag",
]
CLAUSE_COLUMNS = [
    "clause_id",
    "clause_code",
    "required_flag",
    "observed_value",
    "pass_flag",
    "acceptance_required_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

CANDIDATE_NAMES = ["golden_guarded_affine_clock_selector"]
CANDIDATE_CODES = {name: index for index, name in enumerate(CANDIDATE_NAMES)}

CLAUSE_NAMES = [
    "formal_golden_selector_law",
    "affine_clock_order10",
    "guarded_relation_semantic_law",
    "candidate_axiom_materialized",
    "candidate_axiom_accepted",
]
CLAUSE_CODES = {name: index for index, name in enumerate(CLAUSE_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "candidate_count",
    "selected_class_id",
    "selected_branch_code",
    "formal_golden_selector_law_flag",
    "affine_clock_order",
    "affine_clock_flag",
    "relation_semantic_law_flag",
    "guarded_semantic_tick_count",
    "guarded_semantic_relation_count",
    "candidate_admissible_flag",
    "axiom_accepted_flag",
    "physical_selector_axiom_flag",
    "semantic_a985_operation_flag",
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
    glaw = load_json(LONG_GLAW)
    gclk = load_json(LONG_GCLK)
    rsem = load_json(LONG_RSEM)

    glaw_s = summary(glaw)
    gclk_s = summary(gclk)
    rsem_s = summary(rsem)

    selected_class_id = int(glaw_s["golden_class_id"])
    selected_branch_code = 0
    formal_law = int(glaw_s["formal_golden_selector_law_flag"])
    affine_clock_order = int(gclk_s["affine_clock_order"])
    affine_clock = int(
        affine_clock_order == 10
        and int(gclk_s["affine_tenth_tick_identity_count"]) == 20
        and int(gclk_s["affine_fifth_tick_complement_count"]) == 20
    )
    relation_semantic = int(rsem_s["relation_semantic_law_flag"])
    guarded_ticks = int(rsem_s["guarded_semantic_tick_count"])
    guarded_relations = int(rsem_s["guarded_semantic_relation_count"])
    candidate = int(
        selected_class_id == 0
        and selected_branch_code == 0
        and formal_law == 1
        and affine_clock == 1
        and relation_semantic == 1
        and guarded_ticks == 20
        and guarded_relations == 59
    )
    accepted = 0
    physical_axiom = 0

    candidate_rows = [
        {
            "candidate_id": 0,
            "candidate_code": CANDIDATE_CODES[
                "golden_guarded_affine_clock_selector"
            ],
            "selected_class_id": selected_class_id,
            "selected_branch_code": selected_branch_code,
            "formal_golden_law_flag": formal_law,
            "affine_clock_flag": affine_clock,
            "guarded_relation_semantic_flag": relation_semantic,
            "candidate_admissible_flag": candidate,
            "axiom_accepted_flag": accepted,
            "physical_selector_axiom_flag": physical_axiom,
        }
    ]
    clause_specs = [
        ("formal_golden_selector_law", formal_law, 0),
        ("affine_clock_order10", affine_clock, 0),
        ("guarded_relation_semantic_law", relation_semantic, 0),
        ("candidate_axiom_materialized", candidate, 0),
        ("candidate_axiom_accepted", accepted, 1),
    ]
    clause_rows = [
        {
            "clause_id": index,
            "clause_code": CLAUSE_CODES[name],
            "required_flag": 1,
            "observed_value": observed,
            "pass_flag": observed,
            "acceptance_required_flag": acceptance_required,
        }
        for index, (name, observed, acceptance_required) in enumerate(clause_specs)
    ]
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            certified(report) for report in [glaw, gclk, rsem]
        ),
        "candidate_count": candidate,
        "selected_class_id": selected_class_id,
        "selected_branch_code": selected_branch_code,
        "formal_golden_selector_law_flag": formal_law,
        "affine_clock_order": affine_clock_order,
        "affine_clock_flag": affine_clock,
        "relation_semantic_law_flag": relation_semantic,
        "guarded_semantic_tick_count": guarded_ticks,
        "guarded_semantic_relation_count": guarded_relations,
        "candidate_admissible_flag": candidate,
        "axiom_accepted_flag": accepted,
        "physical_selector_axiom_flag": physical_axiom,
        "semantic_a985_operation_flag": int(rsem_s["semantic_a985_operation_flag"]),
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
        "glaw": glaw,
        "gclk": gclk,
        "rsem": rsem,
        "candidate_rows": candidate_rows,
        "clause_rows": clause_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    clause_table = table_from_rows(CLAUSE_COLUMNS, rows["clause_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "candidate_inputs_cohere": obs["selected_class_id"] == 0
        and obs["selected_branch_code"] == 0
        and obs["formal_golden_selector_law_flag"] == 1
        and obs["affine_clock_flag"] == 1
        and obs["relation_semantic_law_flag"] == 1,
        "candidate_materialized_without_physical_acceptance": obs[
            "candidate_admissible_flag"
        ]
        == 1,
        "acceptance_and_physical_boundaries_preserved": obs["axiom_accepted_flag"]
        == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["semantic_a985_operation_flag"] == 0
        and obs["gr_source_ready_flag"] == 0,
        "table_shapes_match": candidate_table.shape
        == (len(CANDIDATE_CODES), len(CANDIDATE_COLUMNS))
        and clause_table.shape == (len(CLAUSE_CODES), len(CLAUSE_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "physical_selector_axiom_candidate",
        "summary": {
            "candidate_count": obs["candidate_count"],
            "selected_class_id": obs["selected_class_id"],
            "selected_branch_code": obs["selected_branch_code"],
            "formal_golden_selector_law_flag": obs[
                "formal_golden_selector_law_flag"
            ],
            "affine_clock_order": obs["affine_clock_order"],
            "relation_semantic_law_flag": obs["relation_semantic_law_flag"],
            "guarded_semantic_tick_count": obs["guarded_semantic_tick_count"],
            "guarded_semantic_relation_count": obs[
                "guarded_semantic_relation_count"
            ],
            "candidate_admissible_flag": obs["candidate_admissible_flag"],
            "axiom_accepted_flag": obs["axiom_accepted_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "semantic_a985_operation_flag": obs["semantic_a985_operation_flag"],
            "gr_source_ready_flag": obs["gr_source_ready_flag"],
        },
        "candidate_code_map": {
            str(value): key for key, value in CANDIDATE_CODES.items()
        },
        "clause_code_map": {str(value): key for key, value in CLAUSE_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "candidate_text_sha256": sha_text(
            csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"])
        ),
        "clause_table_sha256": sha_array(clause_table),
        "clause_text_sha256": sha_text(csv_text(CLAUSE_COLUMNS, rows["clause_rows"])),
        "observable_table_sha256": sha_array(observable_table),
    }
    pax = {
        "schema": "long.pax@1",
        "object": "physical_selector_axiom_candidate",
        "status": STATUS if all(checks.values()) else "LONG_PAX_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.pax.report@1",
        "status": pax["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_pax materializes the finite golden-clock physical-selector "
            "candidate over the certified formal golden law, affine C10 clock, "
            "and guarded relation-valued transition semantics. It certifies "
            "candidate admissibility only: the candidate is not accepted as a "
            "physical selector axiom, and no semantic A985 operation row, "
            "1+3 Lorentzian boundary, stress-energy tensor, or GR source claim "
            "is promoted."
        ),
        "stage_protocol": {
            "draft": "read long_glaw, long_gclk, and long_rsem",
            "witness": "emit selector-candidate row, candidate clauses, and observables",
            "coherence": "check golden class, affine clock, guarded semantics, candidate materialization, and preserved physical boundary",
            "closure": "certify an admissible finite selector candidate without accepting the physical axiom",
            "emit": "write long_pax artifacts and verifier hook",
        },
        "inputs": {
            "long_glaw": input_entry(
                LONG_GLAW,
                {
                    "status": rows["glaw"].get("status"),
                    "certificate_sha256": rows["glaw"].get("certificate_sha256"),
                },
            ),
            "long_gclk": input_entry(
                LONG_GCLK,
                {
                    "status": rows["gclk"].get("status"),
                    "certificate_sha256": rows["gclk"].get("certificate_sha256"),
                },
            ),
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "pax": relpath(OUT_DIR / "pax.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "clause_csv": relpath(OUT_DIR / "clause.csv"),
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
                "one admissible finite golden-clock selector candidate exists in the current certified boundary",
                "the candidate selects golden defect class 0 and selector branch 0",
                "the candidate is supported by the formal golden law, affine order-10 clock, and guarded relation-valued transition semantics",
                "the candidate is upstream of physical-selector acceptance and can be consumed by the selector contract",
                "the physical selector axiom remains unaccepted in this certificate",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the candidate is physically true",
                "a physical selector axiom accepted from A985 alone",
                "semantic A985 transition-operation realization",
                "that relation-valued ticks are physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Decide whether to reject the materialized selector candidate, "
            "accept it as an explicit extra physical axiom, or avoid the extra "
            "axiom by promoting the guarded relation law to semantic A985 "
            "operation rows."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.pax.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.pax.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "pax": pax,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "clause_csv": csv_text(CLAUSE_COLUMNS, rows["clause_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "clause_table": clause_table,
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
    write_json(OUT_DIR / "pax.json", payloads["pax"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "clause.csv").write_text(payloads["clause_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        clause_table=payloads["clause_table"],
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
