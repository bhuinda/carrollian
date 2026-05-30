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


THEOREM_ID = "long_c59p3j"
STATUS = "LONG_C59P3J_ENDPOINT_PROJECTOR_DEGENERACY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3H = PROOF_ROOT / "long_c59p3h" / "report.json"
LONG_C59P3G = PROOF_ROOT / "long_c59p3g" / "report.json"
LONG_C59P3G_TRANSITION_SCHEMA = PROOF_ROOT / "long_c59p3g" / "transition_schema.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_TRANSITION_ENDPOINT = PROOF_ROOT / "long_transition_sem" / "endpoint_raw.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3j.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3j.py"

PROJECTOR_NAMES = ["left_endpoint_projector", "right_endpoint_projector"]
PROJECTOR_CODES = {name: index for index, name in enumerate(PROJECTOR_NAMES)}

PROJECTOR_COLUMNS = [
    "projector_id",
    "projector_code",
    "active_transition_count",
    "raw_supported_transition_count",
    "unique_raw_row_count",
    "uses_left_endpoint_flag",
    "uses_right_endpoint_flag",
    "uses_both_endpoint_flag",
    "transition_coupled_flag",
    "semantic_operation_flag",
]
PROJECTOR_ROW_COLUMNS = [
    "row_id",
    "active_transition_id",
    "transition_id",
    "projector_code",
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "raw_row_id",
    "raw_support_flag",
    "uses_left_endpoint_flag",
    "uses_right_endpoint_flag",
    "transition_coupled_flag",
    "operation_promoted_flag",
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
    "active_address_screen_input",
    "endpoint_projector_totality",
    "nondegenerate_transition_coupling_obstruction",
    "semantic_operation_rows_absent",
    "transition_composition_law",
    "physical_selector_axiom",
    "metric_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "active_transition_count",
    "projector_candidate_count",
    "projector_row_count",
    "left_projector_supported_count",
    "right_projector_supported_count",
    "left_projector_unique_raw_row_count",
    "right_projector_unique_raw_row_count",
    "union_projector_unique_raw_row_count",
    "endpoint_projector_totality_flag",
    "transition_coupled_projector_count",
    "operation_promoted_row_count",
    "semantic_operation_flag",
    "transition_composition_law_flag",
    "physical_selector_axiom_flag",
    "metric_derivation_flag",
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


def endpoint_projector_row(
    *,
    row_id: int,
    active_transition_id: int,
    transition: dict[str, str],
    endpoint: dict[str, str],
    projector_name: str,
) -> dict[str, int]:
    uses_left = int(projector_name == "left_endpoint_projector")
    uses_right = int(projector_name == "right_endpoint_projector")
    return {
        "row_id": row_id,
        "active_transition_id": active_transition_id,
        "transition_id": int(transition["transition_id"]),
        "projector_code": PROJECTOR_CODES[projector_name],
        "basis_id": int(endpoint["basis_id"]),
        "source0_addr": int(endpoint["source0_addr"]),
        "source1_addr": int(endpoint["source1_addr"]),
        "target_addr": int(endpoint["target_addr"]),
        "coeff": int(endpoint["coeff"]),
        "raw_row_id": int(endpoint["raw_row_id"]),
        "raw_support_flag": int(endpoint["raw_row_id_flag"]),
        "uses_left_endpoint_flag": uses_left,
        "uses_right_endpoint_flag": uses_right,
        "transition_coupled_flag": int(uses_left == 1 and uses_right == 1),
        "operation_promoted_flag": 0,
    }


def build_rows() -> dict[str, Any]:
    c59p3h = load_json(LONG_C59P3H)
    c59p3g = load_json(LONG_C59P3G)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    _, active_raw = read_csv_rows(LONG_C59P3G_TRANSITION_SCHEMA)
    _, transition_raw = read_csv_rows(LONG_TRANSITION_CSV)
    _, endpoint_raw = read_csv_rows(LONG_TRANSITION_ENDPOINT)

    transition_by_id = {int(row["transition_id"]): row for row in transition_raw}
    endpoint_by_id = {int(row["basis_id"]): row for row in endpoint_raw}
    active_transitions = [
        transition_by_id[int(row["transition_id"])] for row in active_raw
    ]

    projector_row_rows = []
    row_id = 0
    raw_ids_by_projector: dict[str, set[int]] = {
        name: set() for name in PROJECTOR_NAMES
    }
    for active_row, transition in zip(active_raw, active_transitions):
        active_transition_id = int(active_row["active_transition_id"])
        for projector_name, basis_field in [
            ("left_endpoint_projector", "left_basis_id"),
            ("right_endpoint_projector", "right_basis_id"),
        ]:
            endpoint = endpoint_by_id[int(transition[basis_field])]
            projector_row = endpoint_projector_row(
                row_id=row_id,
                active_transition_id=active_transition_id,
                transition=transition,
                endpoint=endpoint,
                projector_name=projector_name,
            )
            if projector_row["raw_support_flag"] == 1:
                raw_ids_by_projector[projector_name].add(projector_row["raw_row_id"])
            projector_row_rows.append(projector_row)
            row_id += 1

    projector_rows = []
    for projector_id, projector_name in enumerate(PROJECTOR_NAMES):
        rows = [
            row
            for row in projector_row_rows
            if row["projector_code"] == PROJECTOR_CODES[projector_name]
        ]
        uses_left = int(projector_name == "left_endpoint_projector")
        uses_right = int(projector_name == "right_endpoint_projector")
        projector_rows.append(
            {
                "projector_id": projector_id,
                "projector_code": PROJECTOR_CODES[projector_name],
                "active_transition_count": len(active_transitions),
                "raw_supported_transition_count": sum(
                    row["raw_support_flag"] for row in rows
                ),
                "unique_raw_row_count": len(raw_ids_by_projector[projector_name]),
                "uses_left_endpoint_flag": uses_left,
                "uses_right_endpoint_flag": uses_right,
                "uses_both_endpoint_flag": int(uses_left == 1 and uses_right == 1),
                "transition_coupled_flag": 0,
                "semantic_operation_flag": 0,
            }
        )

    union_raw_ids = set().union(*raw_ids_by_projector.values())
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            int(certified(report)) for report in (c59p3h, c59p3g, transition_sem)
        ),
        "active_transition_count": len(active_transitions),
        "projector_candidate_count": len(projector_rows),
        "projector_row_count": len(projector_row_rows),
        "left_projector_supported_count": projector_rows[0][
            "raw_supported_transition_count"
        ],
        "right_projector_supported_count": projector_rows[1][
            "raw_supported_transition_count"
        ],
        "left_projector_unique_raw_row_count": projector_rows[0][
            "unique_raw_row_count"
        ],
        "right_projector_unique_raw_row_count": projector_rows[1][
            "unique_raw_row_count"
        ],
        "union_projector_unique_raw_row_count": len(union_raw_ids),
        "endpoint_projector_totality_flag": int(
            all(row["raw_support_flag"] == 1 for row in projector_row_rows)
        ),
        "transition_coupled_projector_count": sum(
            row["transition_coupled_flag"] for row in projector_rows
        ),
        "operation_promoted_row_count": sum(
            row["operation_promoted_flag"] for row in projector_row_rows
        ),
        "semantic_operation_flag": 0,
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": GAP_CODES["transition_composition_law"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["active_address_screen_input"],
            "gap_code": GAP_CODES["active_address_screen_input"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["endpoint_projector_totality"],
            "gap_code": GAP_CODES["endpoint_projector_totality"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["nondegenerate_transition_coupling_obstruction"],
            "gap_code": GAP_CODES["nondegenerate_transition_coupling_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_operation_rows_absent"],
            "gap_code": GAP_CODES["semantic_operation_rows_absent"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["transition_composition_law"],
            "gap_code": GAP_CODES["transition_composition_law"],
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
            "gap_id": GAP_CODES["metric_derivation"],
            "gap_code": GAP_CODES["metric_derivation"],
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
        "c59p3h": c59p3h,
        "c59p3g": c59p3g,
        "transition_sem": transition_sem,
        "projector_rows": projector_rows,
        "projector_row_rows": projector_row_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    projector_table = table_from_rows(PROJECTOR_COLUMNS, rows["projector_rows"])
    projector_row_table = table_from_rows(
        PROJECTOR_ROW_COLUMNS, rows["projector_row_rows"]
    )
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "projector_shape_exact": obs["active_transition_count"] == 29
        and obs["projector_candidate_count"] == 2
        and obs["projector_row_count"] == 58,
        "endpoint_projectors_are_total": obs["left_projector_supported_count"] == 29
        and obs["right_projector_supported_count"] == 29
        and obs["endpoint_projector_totality_flag"] == 1,
        "projector_unique_counts_exact": obs["left_projector_unique_raw_row_count"]
        == 16
        and obs["right_projector_unique_raw_row_count"] == 20
        and obs["union_projector_unique_raw_row_count"] == 24,
        "transition_coupling_obstructed": obs["transition_coupled_projector_count"]
        == 0
        and obs["operation_promoted_row_count"] == 0
        and obs["semantic_operation_flag"] == 0
        and obs["transition_composition_law_flag"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["metric_derivation_flag"] == 0,
        "table_shapes_match": projector_table.shape == (2, len(PROJECTOR_COLUMNS))
        and projector_row_table.shape == (58, len(PROJECTOR_ROW_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "endpoint_projector_degeneracy",
        "summary": {
            "active_transition_count": obs["active_transition_count"],
            "projector_candidate_count": obs["projector_candidate_count"],
            "left_projector_supported_count": obs["left_projector_supported_count"],
            "right_projector_supported_count": obs[
                "right_projector_supported_count"
            ],
            "left_projector_unique_raw_row_count": obs[
                "left_projector_unique_raw_row_count"
            ],
            "right_projector_unique_raw_row_count": obs[
                "right_projector_unique_raw_row_count"
            ],
            "union_projector_unique_raw_row_count": obs[
                "union_projector_unique_raw_row_count"
            ],
            "transition_coupled_projector_count": obs[
                "transition_coupled_projector_count"
            ],
            "operation_promoted_row_count": obs["operation_promoted_row_count"],
        },
        "projector_code_map": {
            str(value): key for key, value in PROJECTOR_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "projector_table_sha256": sha_array(projector_table),
        "projector_row_table_sha256": sha_array(projector_row_table),
        "projector_row_text_sha256": sha_text(
            csv_text(PROJECTOR_ROW_COLUMNS, rows["projector_row_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3j = {
        "schema": "long.c59p3j@1",
        "object": "endpoint_projector_degeneracy",
        "status": STATUS if all(checks.values()) else "LONG_C59P3J_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3j.report@1",
        "status": c59p3j["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3j certifies that same-endpoint projection gives total "
            "raw support for the 29 active transition ids, but only as a "
            "degenerate endpoint readout. The left and right endpoint "
            "projectors each cover all 29 transitions, yet neither uses both "
            "endpoints, so neither is a transition composition law or a "
            "semantic operation promotion."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3h, long_c59p3g, long_transition_sem, active transition rows, transition rows, and endpoint rows",
            "witness": "emit endpoint-projector summary rows, per-transition projector rows, gaps, and observables",
            "coherence": "check total endpoint raw support, unique raw-row counts, absent transition coupling, and preserved operation/physical gaps",
            "closure": "certify endpoint projector totality as degenerate rather than a transition composition law",
            "emit": "write long_c59p3j artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3h": input_entry(
                LONG_C59P3H,
                {
                    "status": rows["c59p3h"].get("status"),
                    "certificate_sha256": rows["c59p3h"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3g": input_entry(
                LONG_C59P3G,
                {
                    "status": rows["c59p3g"].get("status"),
                    "certificate_sha256": rows["c59p3g"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3g_transition_schema": input_entry(
                LONG_C59P3G_TRANSITION_SCHEMA
            ),
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
            "long_transition_endpoint": input_entry(LONG_TRANSITION_ENDPOINT),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3j": relpath(OUT_DIR / "c59p3j.json"),
            "projector_csv": relpath(OUT_DIR / "projector.csv"),
            "projector_row_csv": relpath(OUT_DIR / "projector_row.csv"),
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
                "the left endpoint projector has raw support for all 29 active transitions",
                "the right endpoint projector has raw support for all 29 active transitions",
                "the left projector uses 16 unique raw rows, the right projector uses 20, and their union has 24",
                "zero endpoint projectors use both endpoints",
                "zero endpoint projector rows are promoted to semantic transition operations",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a nondegenerate transition composition law",
                "new semantic operation rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical field equation",
            ],
        },
        "next_highest_yield_item": (
            "Build a nondegenerate composition grammar that uses both endpoints "
            "while preserving total raw support, or certify the next bounded "
            "grammar obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3j.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3j.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3j": c59p3j,
        "projector_csv": csv_text(PROJECTOR_COLUMNS, rows["projector_rows"]),
        "projector_row_csv": csv_text(
            PROJECTOR_ROW_COLUMNS, rows["projector_row_rows"]
        ),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "projector_table": projector_table,
        "projector_row_table": projector_row_table,
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
    write_json(OUT_DIR / "c59p3j.json", payloads["c59p3j"])
    (OUT_DIR / "projector.csv").write_text(
        payloads["projector_csv"], encoding="utf-8"
    )
    (OUT_DIR / "projector_row.csv").write_text(
        payloads["projector_row_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        projector_table=payloads["projector_table"],
        projector_row_table=payloads["projector_row_table"],
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
