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


THEOREM_ID = "long_krein"
STATUS = "LONG_KREIN_DENOMINATOR_SOURCE_BOUNDARY_PROVISIONAL"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

HANDOFF = ROOT / "docs" / "real.txt"
CHAR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_canonical_sector_characters"
    / "report.json"
)
CHAR_TABLE = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_canonical_sector_characters"
    / "canonical_sector_character_table.csv"
)
TRACE_SUMMARY = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_canonical_sector_characters"
    / "canonical_sector_trace_summary.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_krein.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_krein.py"

SOURCE_COLUMNS = [
    "source_id",
    "source_code",
    "present_flag",
    "certified_flag",
    "required_for_krein_flag",
    "blocks_full_krein_flag",
    "row_count",
    "column_count",
]
TARGET_COLUMNS = [
    "target_id",
    "i",
    "j",
    "k",
    "expected_numerator",
    "expected_denominator",
    "expected_half_integral_flag",
    "computed_flag",
    "verified_flag",
    "blocks_acceptance_flag",
]
CLEARANCE_COLUMNS = [
    "clearance_id",
    "clearance_code",
    "tested_flag",
    "passed_flag",
    "open_flag",
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

SOURCE_NAMES = [
    "handoff_krein_target",
    "canonical_a985_character_table",
    "full_krein_parameter_tensor",
    "idempotent_hadamard_product_witness",
]
SOURCE_CODES = {name: index for index, name in enumerate(SOURCE_NAMES)}

CLEARANCE_NAMES = [
    "double_E5_E6",
    "z2_graded_cover",
    "spinor_state_lift",
    "weak_fusion_category",
    "module_category_realization",
]
CLEARANCE_CODES = {name: index for index, name in enumerate(CLEARANCE_NAMES)}

GAP_NAMES = [
    "canonical_character_table_available",
    "all_krein_parameters_computed",
    "specified_half_rows_verified",
    "denominator_clearance_tests",
    "acceptance_ladder_krein_closure",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "source_row_count",
    "present_source_count",
    "certified_source_count",
    "required_source_count",
    "blocking_source_count",
    "character_sector_count",
    "character_relation_count",
    "character_table_row_count",
    "target_exception_row_count",
    "computed_exception_row_count",
    "verified_exception_row_count",
    "half_integral_exception_row_count",
    "clearance_candidate_count",
    "clearance_tested_count",
    "provisional_flag",
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
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def markdown_report(
    *,
    obs: dict[str, int],
    target_rows: list[dict[str, int]],
    clearance_rows: list[dict[str, int]],
) -> str:
    target_lines = [
        "| i | j | k | expected | computed | verified |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in target_rows:
        target_lines.append(
            "| {i} | {j} | {k} | {num}/{den} | {computed} | {verified} |".format(
                i=row["i"],
                j=row["j"],
                k=row["k"],
                num=row["expected_numerator"],
                den=row["expected_denominator"],
                computed=row["computed_flag"],
                verified=row["verified_flag"],
            )
        )
    clearance_lines = [
        "| candidate | tested | passed | open |",
        "|---|---:|---:|---:|",
    ]
    for row in clearance_rows:
        name = CLEARANCE_NAMES[row["clearance_code"]]
        clearance_lines.append(
            f"| {name} | {row['tested_flag']} | {row['passed_flag']} | {row['open_flag']} |"
        )
    return "\n".join(
        [
            "# Krein Denominator Obstruction Source Boundary",
            "",
            "Status: provisional.",
            "",
            "This report records the next acceptance-ladder target from `docs/real.txt` without upgrading it to a certified Krein computation. The current checked input boundary contains the canonical A985 sector character table, but it does not yet contain a full `q_ij^k` Krein parameter tensor or idempotent Hadamard-product witness.",
            "",
            "## Available Evidence",
            "",
            f"- canonical character sectors: `{obs['character_sector_count']}`",
            f"- canonical relation columns: `{obs['character_relation_count']}`",
            f"- character-table rows: `{obs['character_table_row_count']}`",
            f"- blocking source surfaces still absent: `{obs['blocking_source_count']}`",
            "",
            "## Target Half-Integral Rows",
            "",
            *target_lines,
            "",
            "The four rows above are the handoff target. Their expected denominator obstruction is not certified here because the full Krein parameter table has not been materialized.",
            "",
            "## Clearance Candidates",
            "",
            *clearance_lines,
            "",
            "## Closure Boundary",
            "",
            "Certified here: the source boundary and missing-evidence seam for the Krein denominator task.",
            "",
            "Not certified here: all Krein parameters, the four 135/2 rows, any denominator-clearing double cover, or any acceptance-ladder closure depending on those computations.",
            "",
            "Next highest-yield item: compute the full Krein parameter table from the canonical A985 idempotent/eigenmatrix data, then rerun this report as a certified denominator obstruction or clearance theorem.",
            "",
        ]
    )


def build_rows() -> dict[str, Any]:
    handoff_text = HANDOFF.read_text(encoding="utf-8")
    char_report = load_json(CHAR_REPORT)
    char_header, char_rows = read_csv_rows(CHAR_TABLE)
    trace_header, trace_rows = read_csv_rows(TRACE_SUMMARY)
    character_sector_count = len({int(row["source_sector"]) for row in char_rows})
    character_relation_count = len({int(row["relation_alpha"]) for row in char_rows})

    source_rows = [
        {
            "source_id": SOURCE_CODES["handoff_krein_target"],
            "source_code": SOURCE_CODES["handoff_krein_target"],
            "present_flag": int("q_55" in handoff_text and "135/2" in handoff_text),
            "certified_flag": 0,
            "required_for_krein_flag": 1,
            "blocks_full_krein_flag": 0,
            "row_count": 1,
            "column_count": 0,
        },
        {
            "source_id": SOURCE_CODES["canonical_a985_character_table"],
            "source_code": SOURCE_CODES["canonical_a985_character_table"],
            "present_flag": int(CHAR_TABLE.exists() and TRACE_SUMMARY.exists()),
            "certified_flag": int(certified(char_report)),
            "required_for_krein_flag": 1,
            "blocks_full_krein_flag": 0,
            "row_count": len(char_rows),
            "column_count": len(char_header),
        },
        {
            "source_id": SOURCE_CODES["full_krein_parameter_tensor"],
            "source_code": SOURCE_CODES["full_krein_parameter_tensor"],
            "present_flag": 0,
            "certified_flag": 0,
            "required_for_krein_flag": 1,
            "blocks_full_krein_flag": 1,
            "row_count": 0,
            "column_count": 0,
        },
        {
            "source_id": SOURCE_CODES["idempotent_hadamard_product_witness"],
            "source_code": SOURCE_CODES["idempotent_hadamard_product_witness"],
            "present_flag": 0,
            "certified_flag": 0,
            "required_for_krein_flag": 1,
            "blocks_full_krein_flag": 1,
            "row_count": 0,
            "column_count": 0,
        },
    ]
    target_rows = [
        {
            "target_id": index,
            "i": i,
            "j": j,
            "k": 2,
            "expected_numerator": 135,
            "expected_denominator": 2,
            "expected_half_integral_flag": 1,
            "computed_flag": 0,
            "verified_flag": 0,
            "blocks_acceptance_flag": 1,
        }
        for index, (i, j) in enumerate(((5, 5), (5, 6), (6, 5), (6, 6)))
    ]
    clearance_rows = [
        {
            "clearance_id": CLEARANCE_CODES[name],
            "clearance_code": CLEARANCE_CODES[name],
            "tested_flag": 0,
            "passed_flag": 0,
            "open_flag": 1,
        }
        for name in CLEARANCE_NAMES
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["canonical_character_table_available"],
            "gap_code": GAP_CODES["canonical_character_table_available"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["all_krein_parameters_computed"],
            "gap_code": GAP_CODES["all_krein_parameters_computed"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["specified_half_rows_verified"],
            "gap_code": GAP_CODES["specified_half_rows_verified"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["denominator_clearance_tests"],
            "gap_code": GAP_CODES["denominator_clearance_tests"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["acceptance_ladder_krein_closure"],
            "gap_code": GAP_CODES["acceptance_ladder_krein_closure"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs = {
        "source_row_count": len(source_rows),
        "present_source_count": sum(row["present_flag"] for row in source_rows),
        "certified_source_count": sum(row["certified_flag"] for row in source_rows),
        "required_source_count": sum(
            row["required_for_krein_flag"] for row in source_rows
        ),
        "blocking_source_count": sum(
            row["blocks_full_krein_flag"] for row in source_rows
        ),
        "character_sector_count": character_sector_count,
        "character_relation_count": character_relation_count,
        "character_table_row_count": len(char_rows),
        "target_exception_row_count": len(target_rows),
        "computed_exception_row_count": sum(row["computed_flag"] for row in target_rows),
        "verified_exception_row_count": sum(row["verified_flag"] for row in target_rows),
        "half_integral_exception_row_count": sum(
            row["expected_half_integral_flag"] for row in target_rows
        ),
        "clearance_candidate_count": len(clearance_rows),
        "clearance_tested_count": sum(row["tested_flag"] for row in clearance_rows),
        "provisional_flag": 1,
        "next_gap_code": GAP_CODES["all_krein_parameters_computed"],
    }
    obs_rows = [
        {"observable_id": index, "observable_code": OBS_CODES[name], "value": obs[name]}
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "char_report": char_report,
        "char_header": char_header,
        "char_rows": char_rows,
        "trace_header": trace_header,
        "trace_rows": trace_rows,
        "source_rows": source_rows,
        "target_rows": target_rows,
        "clearance_rows": clearance_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    source_table = table_from_rows(SOURCE_COLUMNS, rows["source_rows"])
    target_table = table_from_rows(TARGET_COLUMNS, rows["target_rows"])
    clearance_table = table_from_rows(CLEARANCE_COLUMNS, rows["clearance_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "handoff_target_present": rows["source_rows"][0]["present_flag"] == 1,
        "canonical_character_input_certified": rows["source_rows"][1][
            "certified_flag"
        ]
        == 1
        and obs["character_sector_count"] == 39
        and obs["character_relation_count"] == 985
        and obs["character_table_row_count"] == 38_415,
        "krein_tensor_not_materialized": obs["blocking_source_count"] == 2
        and obs["computed_exception_row_count"] == 0
        and obs["verified_exception_row_count"] == 0
        and obs["provisional_flag"] == 1,
        "target_rows_recorded_not_verified": obs["target_exception_row_count"] == 4
        and obs["half_integral_exception_row_count"] == 4,
        "clearance_tests_open": obs["clearance_candidate_count"] == 5
        and obs["clearance_tested_count"] == 0,
        "table_shapes_match": source_table.shape == (4, len(SOURCE_COLUMNS))
        and target_table.shape == (4, len(TARGET_COLUMNS))
        and clearance_table.shape == (5, len(CLEARANCE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    md_report = markdown_report(
        obs=obs,
        target_rows=rows["target_rows"],
        clearance_rows=rows["clearance_rows"],
    )
    witness = {
        "name": THEOREM_ID,
        "classification": "krein_denominator_source_boundary",
        "summary": {
            "character_sector_count": obs["character_sector_count"],
            "character_relation_count": obs["character_relation_count"],
            "character_table_row_count": obs["character_table_row_count"],
            "target_exception_row_count": obs["target_exception_row_count"],
            "verified_exception_row_count": obs["verified_exception_row_count"],
            "blocking_source_count": obs["blocking_source_count"],
            "clearance_candidate_count": obs["clearance_candidate_count"],
            "clearance_tested_count": obs["clearance_tested_count"],
            "provisional_flag": obs["provisional_flag"],
        },
        "source_code_map": {str(value): key for key, value in SOURCE_CODES.items()},
        "clearance_code_map": {
            str(value): key for key, value in CLEARANCE_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "source_table_sha256": sha_array(source_table),
        "target_table_sha256": sha_array(target_table),
        "clearance_table_sha256": sha_array(clearance_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "markdown_report_sha256": sha_text(md_report),
    }
    krein = {
        "schema": "long.krein@1",
        "object": "krein_denominator_source_boundary",
        "status": STATUS,
        "witness": witness,
    }
    report = {
        "schema": "long.krein.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_krein records the source boundary for the Krein denominator "
            "obstruction requested by docs/real.txt. The canonical A985 "
            "character table is certified and has shape 39 by 985, but the "
            "full Krein parameter tensor and idempotent Hadamard-product "
            "witness are not materialized in this boundary, so the 135/2 rows "
            "remain provisional targets rather than certified values."
        ),
        "stage_protocol": {
            "draft": "read docs/real.txt and the canonical A985 sector character-table certificate",
            "witness": "emit source-boundary rows, target half-integral rows, clearance candidates, gaps, observables, and the markdown report",
            "coherence": "check character-table shape, target-row recording, absent Krein tensor source, and open clearance tests",
            "closure": "mark the Krein denominator task provisional until q_ij^k is computed from idempotent/eigenmatrix data",
            "emit": "write long_krein artifacts and verifier hook",
        },
        "inputs": {
            "handoff": input_entry(HANDOFF),
            "character_report": input_entry(
                CHAR_REPORT,
                {
                    "status": rows["char_report"].get("status"),
                    "certificate_sha256": rows["char_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "character_table": input_entry(
                CHAR_TABLE,
                {
                    "row_count": len(rows["char_rows"]),
                    "column_count": len(rows["char_header"]),
                },
            ),
            "trace_summary": input_entry(
                TRACE_SUMMARY,
                {
                    "row_count": len(rows["trace_rows"]),
                    "column_count": len(rows["trace_header"]),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "krein": relpath(OUT_DIR / "krein.json"),
            "source_csv": relpath(OUT_DIR / "source.csv"),
            "target_csv": relpath(OUT_DIR / "target.csv"),
            "clearance_csv": relpath(OUT_DIR / "clearance.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "markdown_report": relpath(
                OUT_DIR / "krein_denominator_obstruction_report.md"
            ),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the canonical A985 character table input is certified and has 39 sectors by 985 relations",
                "the four handoff target rows q_55^2, q_56^2, q_65^2, and q_66^2 are recorded as expected 135/2 rows",
                "the current boundary lacks a materialized full Krein parameter tensor",
                "the current boundary lacks the idempotent Hadamard-product witness needed to verify q_ij^k",
            ],
            "does_not_certify_because_provisional": [
                "all Krein parameters",
                "the four 135/2 values as computed facts",
                "doubling E5,E6 as a denominator clearance",
                "a Z2-graded cover, spinor-state lift, weak fusion category, or module-category realization",
                "acceptance-ladder closure at the Krein stage",
            ],
        },
        "next_highest_yield_item": (
            "Compute q_ij^k from the canonical A985 idempotent/eigenmatrix "
            "data and replace this source-boundary report with a certified "
            "Krein denominator obstruction or clearance theorem."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.krein.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.krein.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "krein": krein,
        "source_csv": csv_text(SOURCE_COLUMNS, rows["source_rows"]),
        "target_csv": csv_text(TARGET_COLUMNS, rows["target_rows"]),
        "clearance_csv": csv_text(CLEARANCE_COLUMNS, rows["clearance_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "markdown_report": md_report,
        "source_table": source_table,
        "target_table": target_table,
        "clearance_table": clearance_table,
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
    write_json(OUT_DIR / "krein.json", payloads["krein"])
    (OUT_DIR / "source.csv").write_text(payloads["source_csv"], encoding="utf-8")
    (OUT_DIR / "target.csv").write_text(payloads["target_csv"], encoding="utf-8")
    (OUT_DIR / "clearance.csv").write_text(
        payloads["clearance_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    (OUT_DIR / "krein_denominator_obstruction_report.md").write_text(
        payloads["markdown_report"], encoding="utf-8"
    )
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        source_table=payloads["source_table"],
        target_table=payloads["target_table"],
        clearance_table=payloads["clearance_table"],
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
