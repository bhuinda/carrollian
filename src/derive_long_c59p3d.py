from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
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


THEOREM_ID = "long_c59p3d"
STATUS = "LONG_C59P3D_COUNTERTERM_SELECTOR_CARRIER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3C = PROOF_ROOT / "long_c59p3c" / "report.json"
LONG_C59P3C_COUNTERTERM = PROOF_ROOT / "long_c59p3c" / "counterterm.csv"
LONG_ABMAP = PROOF_ROOT / "long_abmap" / "report.json"
LONG_ABMAP_DOMAIN = PROOF_ROOT / "long_abmap" / "domain.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3d.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3d.py"

ATOM_COLUMNS = [
    "atom_id",
    "counterterm_scaled",
    "counterterm_support_flag",
    "selector_domain_count",
    "selector_carrier_flag",
    "operation_backed_flag",
]
CARRIER_COLUMNS = [
    "carrier_id",
    "atom_id",
    "step_atom_id",
    "candidate_basis_id",
    "incidence_value",
    "counterterm_scaled",
    "selector_carrier_flag",
    "operation_backed_flag",
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
    "formal_atom_counterterm",
    "selector_carrier_support",
    "exact_selector_weight_distribution",
    "operation_backed_counterterm",
    "physical_selector_axiom",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "atom_count",
    "domain_row_count",
    "counterterm_support_count",
    "selector_supported_counterterm_atom_count",
    "selector_carrier_row_count",
    "min_selector_domain_count_on_support",
    "max_selector_domain_count_on_support",
    "zero_counterterm_atom_count",
    "zero_counterterm_domain_row_count",
    "selector_carrier_flag",
    "exact_selector_weight_distribution_flag",
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
    c59p3c = load_json(LONG_C59P3C)
    abmap = load_json(LONG_ABMAP)
    _, counterterm_rows_raw = read_csv_rows(LONG_C59P3C_COUNTERTERM)
    _, domain_rows_raw = read_csv_rows(LONG_ABMAP_DOMAIN)

    domain_count = Counter(int(row["atom_id"]) for row in domain_rows_raw)
    counterterm_by_atom = {
        int(row["atom_id"]): int(row["counterterm_scaled"])
        for row in counterterm_rows_raw
    }
    support_by_atom = {
        int(row["atom_id"]): int(row["counterterm_support_flag"])
        for row in counterterm_rows_raw
    }
    atom_rows = []
    carrier_rows = []
    for atom_id in range(20):
        support = support_by_atom[atom_id]
        domain_rows = [
            row for row in domain_rows_raw if int(row["atom_id"]) == atom_id
        ]
        selector_carrier = int(support == 0 or len(domain_rows) > 0)
        atom_rows.append(
            {
                "atom_id": atom_id,
                "counterterm_scaled": counterterm_by_atom[atom_id],
                "counterterm_support_flag": support,
                "selector_domain_count": len(domain_rows),
                "selector_carrier_flag": selector_carrier,
                "operation_backed_flag": 0,
            }
        )
        if support:
            for row in domain_rows:
                carrier_rows.append(
                    {
                        "carrier_id": len(carrier_rows),
                        "atom_id": atom_id,
                        "step_atom_id": int(row["step_atom_id"]),
                        "candidate_basis_id": int(row["candidate_basis_id"]),
                        "incidence_value": int(row["incidence_value"]),
                        "counterterm_scaled": counterterm_by_atom[atom_id],
                        "selector_carrier_flag": 1,
                        "operation_backed_flag": 0,
                    }
                )

    support_counts = [
        row["selector_domain_count"]
        for row in atom_rows
        if row["counterterm_support_flag"] == 1
    ]
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59p3c)) + int(certified(abmap)),
        "atom_count": len(atom_rows),
        "domain_row_count": len(domain_rows_raw),
        "counterterm_support_count": sum(
            row["counterterm_support_flag"] for row in atom_rows
        ),
        "selector_supported_counterterm_atom_count": sum(
            int(row["counterterm_support_flag"] == 1 and row["selector_domain_count"] > 0)
            for row in atom_rows
        ),
        "selector_carrier_row_count": len(carrier_rows),
        "min_selector_domain_count_on_support": min(support_counts),
        "max_selector_domain_count_on_support": max(support_counts),
        "zero_counterterm_atom_count": sum(
            int(row["counterterm_support_flag"] == 0) for row in atom_rows
        ),
        "zero_counterterm_domain_row_count": sum(
            row["selector_domain_count"]
            for row in atom_rows
            if row["counterterm_support_flag"] == 0
        ),
        "selector_carrier_flag": int(
            all(
                row["selector_domain_count"] > 0
                for row in atom_rows
                if row["counterterm_support_flag"] == 1
            )
        ),
        "exact_selector_weight_distribution_flag": 0,
        "operation_backed_counterterm_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["exact_selector_weight_distribution"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["formal_atom_counterterm"],
            "gap_code": GAP_CODES["formal_atom_counterterm"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["selector_carrier_support"],
            "gap_code": GAP_CODES["selector_carrier_support"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["exact_selector_weight_distribution"],
            "gap_code": GAP_CODES["exact_selector_weight_distribution"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["operation_backed_counterterm"],
            "gap_code": GAP_CODES["operation_backed_counterterm"],
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
        "c59p3c": c59p3c,
        "abmap": abmap,
        "atom_rows": atom_rows,
        "carrier_rows": carrier_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    atom_table = table_from_rows(ATOM_COLUMNS, rows["atom_rows"])
    carrier_table = table_from_rows(CARRIER_COLUMNS, rows["carrier_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_counts_match": obs["atom_count"] == 20
        and obs["domain_row_count"] == 90
        and obs["counterterm_support_count"] == 17,
        "selector_support_covers_counterterm_atoms": obs[
            "selector_supported_counterterm_atom_count"
        ]
        == 17
        and obs["selector_carrier_row_count"] == 77
        and obs["min_selector_domain_count_on_support"] == 3
        and obs["max_selector_domain_count_on_support"] == 6
        and obs["selector_carrier_flag"] == 1,
        "zero_counterterm_atoms_preserved": obs["zero_counterterm_atom_count"] == 3
        and obs["zero_counterterm_domain_row_count"] == 13,
        "operation_and_physical_boundaries_preserved": obs[
            "exact_selector_weight_distribution_flag"
        ]
        == 0
        and obs["operation_backed_counterterm_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": atom_table.shape == (20, len(ATOM_COLUMNS))
        and carrier_table.shape == (77, len(CARRIER_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "counterterm_selector_carrier",
        "summary": {
            "counterterm_support_count": obs["counterterm_support_count"],
            "selector_supported_counterterm_atom_count": obs[
                "selector_supported_counterterm_atom_count"
            ],
            "selector_carrier_row_count": obs["selector_carrier_row_count"],
            "min_selector_domain_count_on_support": obs[
                "min_selector_domain_count_on_support"
            ],
            "max_selector_domain_count_on_support": obs[
                "max_selector_domain_count_on_support"
            ],
            "selector_carrier_flag": obs["selector_carrier_flag"],
            "exact_selector_weight_distribution_flag": obs[
                "exact_selector_weight_distribution_flag"
            ],
            "operation_backed_counterterm_flag": obs[
                "operation_backed_counterterm_flag"
            ],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "atom_table_sha256": sha_array(atom_table),
        "carrier_table_sha256": sha_array(carrier_table),
        "carrier_text_sha256": sha_text(csv_text(CARRIER_COLUMNS, rows["carrier_rows"])),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3d = {
        "schema": "long.c59p3d@1",
        "object": "counterterm_selector_carrier",
        "status": STATUS if all(checks.values()) else "LONG_C59P3D_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3d.report@1",
        "status": c59p3d["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3d joins the formal atom counterterm to the certified "
            "atom-step selector carrier. All 17 nonzero counterterm atoms have "
            "selector-domain support, giving 77 carrier rows. This certifies "
            "carrier support only, not an exact selector-weight distribution or "
            "operation-backed counterterm realization."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3c counterterm rows and long_abmap atom-step domains",
            "witness": "emit atom support rows, carrier rows, gaps, and observables",
            "coherence": "check all nonzero counterterm atoms have selector-domain carriers and preserve operation/physical gaps",
            "closure": "certify selector-carrier support for the formal atom counterterm",
            "emit": "write long_c59p3d artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3c": input_entry(
                LONG_C59P3C,
                {
                    "status": rows["c59p3c"].get("status"),
                    "certificate_sha256": rows["c59p3c"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3c_counterterm": input_entry(LONG_C59P3C_COUNTERTERM),
            "long_abmap": input_entry(
                LONG_ABMAP,
                {
                    "status": rows["abmap"].get("status"),
                    "certificate_sha256": rows["abmap"].get("certificate_sha256"),
                },
            ),
            "long_abmap_domain": input_entry(LONG_ABMAP_DOMAIN),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3d": relpath(OUT_DIR / "c59p3d.json"),
            "atom_csv": relpath(OUT_DIR / "atom.csv"),
            "carrier_csv": relpath(OUT_DIR / "carrier.csv"),
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
                "all 17 nonzero atom counterterms have certified selector-domain carrier support",
                "the selector carrier contains 77 atom-step rows over the corrected atoms",
                "each corrected atom has between 3 and 6 selector-domain carriers",
                "the three zero-counterterm atoms remain outside the active carrier support",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "an exact selector-weight distribution over the carrier rows",
                "operation-backed counterterm rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Construct an exact selector-weight distribution over the 77 carrier "
            "rows, or certify the divisibility/normalization obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3d.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3d.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3d": c59p3d,
        "atom_csv": csv_text(ATOM_COLUMNS, rows["atom_rows"]),
        "carrier_csv": csv_text(CARRIER_COLUMNS, rows["carrier_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "atom_table": atom_table,
        "carrier_table": carrier_table,
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
    write_json(OUT_DIR / "c59p3d.json", payloads["c59p3d"])
    (OUT_DIR / "atom.csv").write_text(payloads["atom_csv"], encoding="utf-8")
    (OUT_DIR / "carrier.csv").write_text(payloads["carrier_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        atom_table=payloads["atom_table"],
        carrier_table=payloads["carrier_table"],
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
