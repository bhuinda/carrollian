from __future__ import annotations

import csv
import hashlib
import json
import math
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


THEOREM_ID = "long_c59p3e"
STATUS = "LONG_C59P3E_EXACT_SELECTOR_WEIGHT_DISTRIBUTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3D = PROOF_ROOT / "long_c59p3d" / "report.json"
LONG_C59P3D_ATOM = PROOF_ROOT / "long_c59p3d" / "atom.csv"
LONG_C59P3D_CARRIER = PROOF_ROOT / "long_c59p3d" / "carrier.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3e.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3e.py"

WEIGHT_COLUMNS = [
    "carrier_id",
    "atom_id",
    "step_atom_id",
    "candidate_basis_id",
    "incidence_value",
    "selector_domain_count",
    "counterterm_scaled",
    "weight_num",
    "weight_den",
    "common_den_weight_num",
    "row_integral_flag",
    "exact_weight_flag",
    "operation_backed_flag",
]
ATOM_SUM_COLUMNS = [
    "atom_id",
    "counterterm_scaled",
    "selector_domain_count",
    "weight_row_count",
    "sum_num",
    "sum_den",
    "sum_equals_counterterm_flag",
    "all_rows_integral_flag",
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
    "selector_carrier_support",
    "exact_rational_selector_distribution",
    "integral_selector_weight_distribution",
    "operation_backed_counterterm",
    "physical_selector_axiom",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "active_atom_count",
    "carrier_row_count",
    "exact_weight_row_count",
    "atom_sum_pass_count",
    "common_denominator",
    "integral_weight_row_count",
    "nonintegral_weight_row_count",
    "integral_atom_count",
    "nonintegral_atom_count",
    "integral_distribution_flag",
    "exact_rational_distribution_flag",
    "common_den_weight_num_abs_total",
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


def lcm(values: list[int]) -> int:
    out = 1
    for value in values:
        out = out * value // math.gcd(out, value)
    return out


def build_rows() -> dict[str, Any]:
    c59p3d = load_json(LONG_C59P3D)
    _, atom_rows_raw = read_csv_rows(LONG_C59P3D_ATOM)
    _, carrier_rows_raw = read_csv_rows(LONG_C59P3D_CARRIER)

    active_atoms = [
        row for row in atom_rows_raw if int(row["counterterm_support_flag"]) == 1
    ]
    active_atom_ids = {int(row["atom_id"]) for row in active_atoms}
    domain_count_by_atom = {
        int(row["atom_id"]): int(row["selector_domain_count"])
        for row in atom_rows_raw
    }
    weight_denominators = []
    raw_weight_rows = []
    for row in carrier_rows_raw:
        atom_id = int(row["atom_id"])
        if atom_id not in active_atom_ids:
            continue
        counterterm = int(row["counterterm_scaled"])
        domain_count = domain_count_by_atom[atom_id]
        divisor = math.gcd(abs(counterterm), domain_count)
        weight_num = counterterm // divisor
        weight_den = domain_count // divisor
        weight_denominators.append(weight_den)
        raw_weight_rows.append((row, domain_count, weight_num, weight_den))

    common_denominator = lcm(weight_denominators)
    weight_rows = []
    for row, domain_count, weight_num, weight_den in raw_weight_rows:
        weight_rows.append(
            {
                "carrier_id": int(row["carrier_id"]),
                "atom_id": int(row["atom_id"]),
                "step_atom_id": int(row["step_atom_id"]),
                "candidate_basis_id": int(row["candidate_basis_id"]),
                "incidence_value": int(row["incidence_value"]),
                "selector_domain_count": domain_count,
                "counterterm_scaled": int(row["counterterm_scaled"]),
                "weight_num": weight_num,
                "weight_den": weight_den,
                "common_den_weight_num": weight_num
                * (common_denominator // weight_den),
                "row_integral_flag": int(weight_den == 1),
                "exact_weight_flag": 1,
                "operation_backed_flag": 0,
            }
        )

    rows_by_atom: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in weight_rows:
        rows_by_atom[row["atom_id"]].append(row)
    atom_sum_rows = []
    for atom_row in active_atoms:
        atom_id = int(atom_row["atom_id"])
        counterterm = int(atom_row["counterterm_scaled"])
        domain_count = int(atom_row["selector_domain_count"])
        rows = rows_by_atom[atom_id]
        common_atom_den = lcm([row["weight_den"] for row in rows])
        sum_num = sum(
            row["weight_num"] * (common_atom_den // row["weight_den"])
            for row in rows
        )
        atom_sum_rows.append(
            {
                "atom_id": atom_id,
                "counterterm_scaled": counterterm,
                "selector_domain_count": domain_count,
                "weight_row_count": len(rows),
                "sum_num": sum_num,
                "sum_den": common_atom_den,
                "sum_equals_counterterm_flag": int(
                    sum_num == counterterm * common_atom_den
                ),
                "all_rows_integral_flag": int(
                    all(row["row_integral_flag"] == 1 for row in rows)
                ),
            }
        )

    obs = {
        "input_report_count": 1,
        "input_certified_count": int(certified(c59p3d)),
        "active_atom_count": len(active_atoms),
        "carrier_row_count": len(weight_rows),
        "exact_weight_row_count": sum(row["exact_weight_flag"] for row in weight_rows),
        "atom_sum_pass_count": sum(
            row["sum_equals_counterterm_flag"] for row in atom_sum_rows
        ),
        "common_denominator": common_denominator,
        "integral_weight_row_count": sum(row["row_integral_flag"] for row in weight_rows),
        "nonintegral_weight_row_count": sum(
            int(row["row_integral_flag"] == 0) for row in weight_rows
        ),
        "integral_atom_count": sum(
            row["all_rows_integral_flag"] for row in atom_sum_rows
        ),
        "nonintegral_atom_count": sum(
            int(row["all_rows_integral_flag"] == 0) for row in atom_sum_rows
        ),
        "integral_distribution_flag": int(
            all(row["row_integral_flag"] == 1 for row in weight_rows)
        ),
        "exact_rational_distribution_flag": int(
            all(row["sum_equals_counterterm_flag"] == 1 for row in atom_sum_rows)
        ),
        "common_den_weight_num_abs_total": sum(
            abs(row["common_den_weight_num"]) for row in weight_rows
        ),
        "operation_backed_counterterm_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["operation_backed_counterterm"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["selector_carrier_support"],
            "gap_code": GAP_CODES["selector_carrier_support"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["exact_rational_selector_distribution"],
            "gap_code": GAP_CODES["exact_rational_selector_distribution"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["integral_selector_weight_distribution"],
            "gap_code": GAP_CODES["integral_selector_weight_distribution"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
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
        "c59p3d": c59p3d,
        "weight_rows": weight_rows,
        "atom_sum_rows": atom_sum_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    weight_table = table_from_rows(WEIGHT_COLUMNS, rows["weight_rows"])
    atom_sum_table = table_from_rows(ATOM_SUM_COLUMNS, rows["atom_sum_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_report_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "exact_distribution_covers_carrier": obs["active_atom_count"] == 17
        and obs["carrier_row_count"] == 77
        and obs["exact_weight_row_count"] == 77
        and obs["atom_sum_pass_count"] == 17
        and obs["exact_rational_distribution_flag"] == 1,
        "normalization_denominator_exact": obs["common_denominator"] == 20
        and obs["common_den_weight_num_abs_total"] == 13159253255760,
        "integer_distribution_obstructed": obs["integral_weight_row_count"] == 30
        and obs["nonintegral_weight_row_count"] == 47
        and obs["integral_atom_count"] == 7
        and obs["nonintegral_atom_count"] == 10
        and obs["integral_distribution_flag"] == 0,
        "operation_and_physical_boundaries_preserved": obs[
            "operation_backed_counterterm_flag"
        ]
        == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": weight_table.shape == (77, len(WEIGHT_COLUMNS))
        and atom_sum_table.shape == (17, len(ATOM_SUM_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "exact_selector_weight_distribution",
        "summary": {
            "active_atom_count": obs["active_atom_count"],
            "carrier_row_count": obs["carrier_row_count"],
            "exact_rational_distribution_flag": obs[
                "exact_rational_distribution_flag"
            ],
            "common_denominator": obs["common_denominator"],
            "integral_weight_row_count": obs["integral_weight_row_count"],
            "nonintegral_weight_row_count": obs["nonintegral_weight_row_count"],
            "integral_atom_count": obs["integral_atom_count"],
            "nonintegral_atom_count": obs["nonintegral_atom_count"],
            "integral_distribution_flag": obs["integral_distribution_flag"],
            "operation_backed_counterterm_flag": obs[
                "operation_backed_counterterm_flag"
            ],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "weight_table_sha256": sha_array(weight_table),
        "weight_text_sha256": sha_text(csv_text(WEIGHT_COLUMNS, rows["weight_rows"])),
        "atom_sum_table_sha256": sha_array(atom_sum_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3e = {
        "schema": "long.c59p3e@1",
        "object": "exact_selector_weight_distribution",
        "status": STATUS if all(checks.values()) else "LONG_C59P3E_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3e.report@1",
        "status": c59p3e["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3e distributes the formal atom counterterm exactly over "
            "the 77 selector-carrier rows. The distribution is exact over "
            "rational weights with common denominator 20, but not integral: "
            "47 rows across 10 atoms require non-unit denominators."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3d atom and carrier rows",
            "witness": "emit per-carrier rational weights, per-atom exact sum rows, gaps, and observables",
            "coherence": "check exact per-atom sums, common denominator, integer divisibility obstruction, and preserved operation/physical gaps",
            "closure": "certify exact rational selector-weight distribution and integral obstruction",
            "emit": "write long_c59p3e artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3d": input_entry(
                LONG_C59P3D,
                {
                    "status": rows["c59p3d"].get("status"),
                    "certificate_sha256": rows["c59p3d"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3d_atom": input_entry(LONG_C59P3D_ATOM),
            "long_c59p3d_carrier": input_entry(LONG_C59P3D_CARRIER),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3e": relpath(OUT_DIR / "c59p3e.json"),
            "weight_csv": relpath(OUT_DIR / "weight.csv"),
            "atom_sum_csv": relpath(OUT_DIR / "atom_sum.csv"),
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
                "an exact rational selector-weight distribution exists over all 77 carrier rows",
                "each of the 17 active atoms sums exactly to its formal counterterm",
                "the common denominator of the reduced carrier weights is 20",
                "an integral row-weight distribution is obstructed for the equal-carrier normalization",
                "47 carrier rows across 10 atoms require non-unit denominators",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "an integral selector-weight distribution under this normalization",
                "operation-backed counterterm rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Attempt to clear the denominator-20 rational distribution through a "
            "certified packet/clock normalization, or prove that the denominator "
            "cannot be absorbed by the current packet scale."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3e.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3e.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3e": c59p3e,
        "weight_csv": csv_text(WEIGHT_COLUMNS, rows["weight_rows"]),
        "atom_sum_csv": csv_text(ATOM_SUM_COLUMNS, rows["atom_sum_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "weight_table": weight_table,
        "atom_sum_table": atom_sum_table,
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
    write_json(OUT_DIR / "c59p3e.json", payloads["c59p3e"])
    (OUT_DIR / "weight.csv").write_text(payloads["weight_csv"], encoding="utf-8")
    (OUT_DIR / "atom_sum.csv").write_text(
        payloads["atom_sum_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        weight_table=payloads["weight_table"],
        atom_sum_table=payloads["atom_sum_table"],
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
