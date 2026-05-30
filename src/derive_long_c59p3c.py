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


THEOREM_ID = "long_c59p3c"
STATUS = "LONG_C59P3C_FORMAL_LOCAL_COUNTERTERM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3W = PROOF_ROOT / "long_c59p3w" / "report.json"
LONG_C59P3W_BALANCE = PROOF_ROOT / "long_c59p3w" / "balance.csv"
LONG_C59P3W_EDGE = PROOF_ROOT / "long_c59p3w" / "edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3c.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3c.py"

COUNTERTERM_COLUMNS = [
    "atom_id",
    "pre_net_divergence_scaled",
    "counterterm_scaled",
    "post_net_divergence_scaled",
    "counterterm_support_flag",
    "pre_local_balance_flag",
    "post_local_balance_flag",
    "minimal_support_required_flag",
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
    "formal_local_counterterm",
    "corrected_local_balance",
    "operation_backed_counterterm",
    "physical_selector_axiom",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "atom_count",
    "edge_row_count",
    "pre_unbalanced_atom_count",
    "counterterm_support_count",
    "counterterm_sum_scaled",
    "counterterm_abs_total_scaled",
    "counterterm_max_abs_scaled",
    "post_unbalanced_atom_count",
    "post_global_divergence_sum_scaled",
    "minimal_support_flag",
    "formal_counterterm_flag",
    "operation_backed_counterterm_flag",
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
    c59p3w = load_json(LONG_C59P3W)
    _, balance_rows_raw = read_csv_rows(LONG_C59P3W_BALANCE)
    _, edge_rows_raw = read_csv_rows(LONG_C59P3W_EDGE)

    counterterm_rows = []
    for row in balance_rows_raw:
        net = int(row["net_divergence_scaled"])
        counterterm = -net
        post = net + counterterm
        support = int(counterterm != 0)
        counterterm_rows.append(
            {
                "atom_id": int(row["atom_id"]),
                "pre_net_divergence_scaled": net,
                "counterterm_scaled": counterterm,
                "post_net_divergence_scaled": post,
                "counterterm_support_flag": support,
                "pre_local_balance_flag": int(row["local_balance_flag"]),
                "post_local_balance_flag": int(post == 0),
                "minimal_support_required_flag": support,
            }
        )

    obs = {
        "input_report_count": 1,
        "input_certified_count": int(certified(c59p3w)),
        "atom_count": len(counterterm_rows),
        "edge_row_count": len(edge_rows_raw),
        "pre_unbalanced_atom_count": sum(
            int(row["pre_local_balance_flag"] == 0) for row in counterterm_rows
        ),
        "counterterm_support_count": sum(
            row["counterterm_support_flag"] for row in counterterm_rows
        ),
        "counterterm_sum_scaled": sum(
            row["counterterm_scaled"] for row in counterterm_rows
        ),
        "counterterm_abs_total_scaled": sum(
            abs(row["counterterm_scaled"]) for row in counterterm_rows
        ),
        "counterterm_max_abs_scaled": max(
            abs(row["counterterm_scaled"]) for row in counterterm_rows
        ),
        "post_unbalanced_atom_count": sum(
            int(row["post_local_balance_flag"] == 0) for row in counterterm_rows
        ),
        "post_global_divergence_sum_scaled": sum(
            row["post_net_divergence_scaled"] for row in counterterm_rows
        ),
        "minimal_support_flag": int(
            all(
                row["minimal_support_required_flag"]
                == int(row["pre_net_divergence_scaled"] != 0)
                for row in counterterm_rows
            )
        ),
        "formal_counterterm_flag": 1,
        "operation_backed_counterterm_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["operation_backed_counterterm"],
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
            "gap_id": GAP_CODES["formal_local_counterterm"],
            "gap_code": GAP_CODES["formal_local_counterterm"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["corrected_local_balance"],
            "gap_code": GAP_CODES["corrected_local_balance"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_backed_counterterm"],
            "gap_code": GAP_CODES["operation_backed_counterterm"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
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
        "c59p3w": c59p3w,
        "counterterm_rows": counterterm_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    counterterm_table = table_from_rows(
        COUNTERTERM_COLUMNS, rows["counterterm_rows"]
    )
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_report_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_boundary_matches": obs["atom_count"] == 20
        and obs["edge_row_count"] == 14
        and obs["pre_unbalanced_atom_count"] == 17,
        "counterterm_is_minimal_support": obs["counterterm_support_count"] == 17
        and obs["minimal_support_flag"] == 1,
        "counterterm_sums_match": obs["counterterm_sum_scaled"] == 0
        and obs["counterterm_abs_total_scaled"] == 657962662788
        and obs["counterterm_max_abs_scaled"] == 180000000000,
        "corrected_balance_holds": obs["post_unbalanced_atom_count"] == 0
        and obs["post_global_divergence_sum_scaled"] == 0,
        "operation_and_physical_boundaries_preserved": obs[
            "formal_counterterm_flag"
        ]
        == 1
        and obs["operation_backed_counterterm_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": counterterm_table.shape
        == (20, len(COUNTERTERM_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "formal_local_counterterm",
        "summary": {
            "atom_count": obs["atom_count"],
            "pre_unbalanced_atom_count": obs["pre_unbalanced_atom_count"],
            "counterterm_support_count": obs["counterterm_support_count"],
            "counterterm_sum_scaled": obs["counterterm_sum_scaled"],
            "counterterm_abs_total_scaled": obs["counterterm_abs_total_scaled"],
            "counterterm_max_abs_scaled": obs["counterterm_max_abs_scaled"],
            "post_unbalanced_atom_count": obs["post_unbalanced_atom_count"],
            "formal_counterterm_flag": obs["formal_counterterm_flag"],
            "operation_backed_counterterm_flag": obs[
                "operation_backed_counterterm_flag"
            ],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "counterterm_table_sha256": sha_array(counterterm_table),
        "counterterm_text_sha256": sha_text(
            csv_text(COUNTERTERM_COLUMNS, rows["counterterm_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3c = {
        "schema": "long.c59p3c@1",
        "object": "formal_local_counterterm",
        "status": STATUS if all(checks.values()) else "LONG_C59P3C_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3c.report@1",
        "status": c59p3c["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3c constructs the minimal formal atom counterterm for the "
            "17 nonzero local stress-source divergences. The correction is the "
            "negative of each local residue, has zero total sum, and makes all "
            "20 corrected local balances vanish. It is formal only and is not "
            "operation-backed in the current boundary."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3w balance rows and source edge rows",
            "witness": "emit atom counterterm rows, gaps, and observables",
            "coherence": "check minimal support, zero total counterterm, corrected local balance, and preserved operation/physical boundaries",
            "closure": "certify the formal local counterterm surface",
            "emit": "write long_c59p3c artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3w": input_entry(
                LONG_C59P3W,
                {
                    "status": rows["c59p3w"].get("status"),
                    "certificate_sha256": rows["c59p3w"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3w_balance": input_entry(LONG_C59P3W_BALANCE),
            "long_c59p3w_edge": input_entry(LONG_C59P3W_EDGE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3c": relpath(OUT_DIR / "c59p3c.json"),
            "counterterm_csv": relpath(OUT_DIR / "counterterm.csv"),
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
                "a formal atom counterterm exists for every nonzero local stress-source residue",
                "the counterterm support has minimal size 17",
                "the counterterm total sum is zero",
                "the corrected local divergence is zero at all 20 atoms",
                "the formal correction preserves the global zero-divergence ledger",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "operation-backed counterterm rows",
                "semantic transition flags for the counterterm",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Attempt to lift the formal atom counterterm into operation-backed "
            "or selector-backed rows; otherwise keep it as a certified formal "
            "local-balance correction only."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3c.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3c.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3c": c59p3c,
        "counterterm_csv": csv_text(COUNTERTERM_COLUMNS, rows["counterterm_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "counterterm_table": counterterm_table,
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
    write_json(OUT_DIR / "c59p3c.json", payloads["c59p3c"])
    (OUT_DIR / "counterterm.csv").write_text(
        payloads["counterterm_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        counterterm_table=payloads["counterterm_table"],
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
