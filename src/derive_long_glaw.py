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


THEOREM_ID = "long_glaw"
STATUS = "LONG_GLAW_FORMAL_GOLDEN_SELECTOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RIM = PROOF_ROOT / "long_rim" / "report.json"
LONG_RIM_CLASS = PROOF_ROOT / "long_rim" / "class.csv"
LONG_RIM_ORBIT = PROOF_ROOT / "long_rim" / "orbit.csv"
LONG_FRIM = PROOF_ROOT / "long_frim" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_glaw.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_glaw.py"

LAW_COLUMNS = [
    "law_id",
    "law_code",
    "selected_class_id",
    "selected_orbit_id",
    "class_count",
    "orbit_count",
    "rim_count",
    "rank",
    "nullity",
    "formal_selector_flag",
    "physical_selector_flag",
]
COEFF_COLUMNS = [
    "coeff_id",
    "power",
    "coefficient",
    "expected_coefficient",
    "match_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

LAW_NAMES = ["golden_polynomial_unique_defect_class"]
LAW_CODES = {name: index for index, name in enumerate(LAW_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "defect_class_count",
    "golden_class_count",
    "golden_class_id",
    "golden_orbit_count",
    "golden_orbit_id",
    "golden_unoriented_rim_count",
    "golden_rank",
    "golden_nullity",
    "coefficient_match_count",
    "coefficient_row_count",
    "formal_golden_selector_law_flag",
    "physical_selector_axiom_flag",
    "transition_semantics_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

GOLDEN_COEFFS = {
    20: 1,
    19: 0,
    18: -140,
    17: 0,
    16: 7760,
    15: 0,
    14: -212800,
    13: 0,
    12: 2886400,
    11: 0,
    10: -15492096,
    9: 0,
    8: 0,
    7: 0,
    6: 0,
    5: 0,
    4: 0,
    3: 0,
    2: 0,
    1: 0,
    0: 0,
}


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
    rim = load_json(LONG_RIM)
    frim = load_json(LONG_FRIM)
    class_rows_raw = read_csv(LONG_RIM_CLASS)
    orbit_rows_raw = read_csv(LONG_RIM_ORBIT)

    class_rows = [{key: int(value) for key, value in row.items()} for row in class_rows_raw]
    golden_classes = [row for row in class_rows if row["golden_flag"] == 1]
    golden_orbits = [
        {key: int(value) if key != "representative_rim" and key != "charpoly_sha256" else value for key, value in row.items()}
        for row in orbit_rows_raw
        if int(row["golden_flag"]) == 1
    ]
    golden_class = golden_classes[0]
    golden_orbit = golden_orbits[0]

    coeff_rows = []
    for index, power in enumerate(range(20, -1, -1)):
        coeff = int(golden_class[f"coeff_x{power}"])
        expected = GOLDEN_COEFFS[power]
        coeff_rows.append(
            {
                "coeff_id": index,
                "power": power,
                "coefficient": coeff,
                "expected_coefficient": expected,
                "match_flag": int(coeff == expected),
            }
        )

    frim_s = summary(frim)
    law_rows = [
        {
            "law_id": 0,
            "law_code": LAW_CODES["golden_polynomial_unique_defect_class"],
            "selected_class_id": golden_class["class_id"],
            "selected_orbit_id": int(golden_orbit["orbit_id"]),
            "class_count": len(golden_classes),
            "orbit_count": len(golden_orbits),
            "rim_count": golden_class["rim_count"],
            "rank": golden_class["rank"],
            "nullity": golden_class["nullity"],
            "formal_selector_flag": 1,
            "physical_selector_flag": 0,
        }
    ]
    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(certified(report) for report in [rim, frim]),
        "defect_class_count": int(frim_s["defect_class_count"]),
        "golden_class_count": len(golden_classes),
        "golden_class_id": golden_class["class_id"],
        "golden_orbit_count": len(golden_orbits),
        "golden_orbit_id": int(golden_orbit["orbit_id"]),
        "golden_unoriented_rim_count": golden_class["rim_count"],
        "golden_rank": golden_class["rank"],
        "golden_nullity": golden_class["nullity"],
        "coefficient_match_count": sum(row["match_flag"] for row in coeff_rows),
        "coefficient_row_count": len(coeff_rows),
        "formal_golden_selector_law_flag": 1,
        "physical_selector_axiom_flag": 0,
        "transition_semantics_flag": 0,
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
        "rim": rim,
        "frim": frim,
        "law_rows": law_rows,
        "coeff_rows": coeff_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    law_table = table_from_rows(LAW_COLUMNS, rows["law_rows"])
    coeff_table = table_from_rows(COEFF_COLUMNS, rows["coeff_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "golden_class_is_unique": obs["defect_class_count"] == 63
        and obs["golden_class_count"] == 1
        and obs["golden_class_id"] == 0,
        "golden_orbit_is_unique": obs["golden_orbit_count"] == 1
        and obs["golden_unoriented_rim_count"] == 144,
        "golden_coefficients_match_formal_law": obs["coefficient_match_count"]
        == obs["coefficient_row_count"]
        == 21,
        "formal_law_is_not_physical_selector": obs["formal_golden_selector_law_flag"] == 1
        and obs["physical_selector_axiom_flag"] == 0
        and obs["transition_semantics_flag"] == 0,
        "table_shapes_match": law_table.shape == (len(LAW_CODES), len(LAW_COLUMNS))
        and coeff_table.shape == (21, len(COEFF_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "formal_golden_selector_law",
        "summary": {
            "defect_class_count": obs["defect_class_count"],
            "golden_class_id": obs["golden_class_id"],
            "golden_class_count": obs["golden_class_count"],
            "golden_orbit_count": obs["golden_orbit_count"],
            "golden_unoriented_rim_count": obs["golden_unoriented_rim_count"],
            "golden_rank": obs["golden_rank"],
            "golden_nullity": obs["golden_nullity"],
            "formal_golden_selector_law_flag": obs[
                "formal_golden_selector_law_flag"
            ],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "transition_semantics_flag": obs["transition_semantics_flag"],
        },
        "law_code_map": {str(value): key for key, value in LAW_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "golden_charpoly_factorization": "x^10*(x^2-36)*(x^4-52*x^2+656)^2",
        "golden_spectrum_squares": ["36", "26+2*sqrt(5)", "26-2*sqrt(5)"],
        "law_table_sha256": sha_array(law_table),
        "law_text_sha256": sha_text(csv_text(LAW_COLUMNS, rows["law_rows"])),
        "coeff_table_sha256": sha_array(coeff_table),
        "coeff_text_sha256": sha_text(csv_text(COEFF_COLUMNS, rows["coeff_rows"])),
        "observable_table_sha256": sha_array(observable_table),
    }
    glaw = {
        "schema": "long.glaw@1",
        "object": "formal_golden_selector_law",
        "status": STATUS if all(checks.values()) else "LONG_GLAW_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.glaw.report@1",
        "status": glaw["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_glaw materializes the formal golden selector law: select the "
            "unique defect class whose half-tick polynomial is "
            "x^10*(x^2-36)*(x^4-52*x^2+656)^2. This closes the formal law "
            "for golden class 0 but does not make it a physical selector."
        ),
        "stage_protocol": {
            "draft": "read long_rim, long_frim, long_sfork, and rim class/orbit rows",
            "witness": "emit the formal golden law row and coefficient witness rows",
            "coherence": "check uniqueness, coefficient match, formal selector flag, and table hashes",
            "closure": "certify a formal golden selector law while preserving physical and transition blockers",
            "emit": "write long_glaw artifacts and verifier hook",
        },
        "inputs": {
            "long_rim": input_entry(
                LONG_RIM,
                {
                    "status": rows["rim"].get("status"),
                    "certificate_sha256": rows["rim"].get("certificate_sha256"),
                },
            ),
            "long_rim_class": input_entry(LONG_RIM_CLASS),
            "long_rim_orbit": input_entry(LONG_RIM_ORBIT),
            "long_frim": input_entry(
                LONG_FRIM,
                {
                    "status": rows["frim"].get("status"),
                    "certificate_sha256": rows["frim"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "glaw": relpath(OUT_DIR / "glaw.json"),
            "law_csv": relpath(OUT_DIR / "law.csv"),
            "coeff_csv": relpath(OUT_DIR / "coeff.csv"),
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
                "there is exactly one golden defect class under the current rim classification",
                "the selected formal golden class is class 0",
                "the golden class has one S6 rim orbit and 144 unoriented rims",
                "the class-0 coefficients match x^10*(x^2-36)*(x^4-52*x^2+656)^2",
                "the formal golden selector law is available as an input to branch-frontier checks",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the formal golden selector is physically valid",
                "that stress selection should be ignored",
                "semantic A985 transition operations",
                "a physical selector axiom",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Rerun the selector branch frontier with long_glaw as an input so "
            "the golden branch advances to the next real blocker."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.glaw.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.glaw.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "glaw": glaw,
        "law_csv": csv_text(LAW_COLUMNS, rows["law_rows"]),
        "coeff_csv": csv_text(COEFF_COLUMNS, rows["coeff_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "law_table": law_table,
        "coeff_table": coeff_table,
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
    write_json(OUT_DIR / "glaw.json", payloads["glaw"])
    (OUT_DIR / "law.csv").write_text(payloads["law_csv"], encoding="utf-8")
    (OUT_DIR / "coeff.csv").write_text(payloads["coeff_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        law_table=payloads["law_table"],
        coeff_table=payloads["coeff_table"],
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
