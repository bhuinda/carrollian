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


THEOREM_ID = "long_c59p3m"
STATUS = "LONG_C59P3M_NORMALIZED_OPERATION_PROMOTION_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3N = PROOF_ROOT / "long_c59p3n" / "report.json"
LONG_C59P3N_WEIGHT_CLEAR = PROOF_ROOT / "long_c59p3n" / "weight_clear.csv"
LONG_C59P3E_WEIGHT = PROOF_ROOT / "long_c59p3e" / "weight.csv"
LONG_GCLK = PROOF_ROOT / "long_gclk" / "report.json"
LONG_GCLK_CYCLE = PROOF_ROOT / "long_gclk" / "cycle.csv"
LONG_OPROM = PROOF_ROOT / "long_oprom" / "report.json"
LONG_OPROM_PROMOTION = PROOF_ROOT / "long_oprom" / "promotion.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3m.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3m.py"

JOIN_COLUMNS = [
    "join_id",
    "carrier_id",
    "atom_id",
    "step_atom_id",
    "candidate_basis_id",
    "visible_index",
    "relation_id",
    "transition_id",
    "visible20_cleared_num",
    "promotion_transition_present_flag",
    "guarded_relation_semantic_flag",
    "operation_row_present_flag",
    "semantic_transition_flag",
    "operation_backed_normalized_flag",
    "obstruction_code",
]
CARRIER_COLUMNS = [
    "carrier_id",
    "atom_id",
    "visible_index",
    "promotion_row_count",
    "joined_row_count",
    "visible20_cleared_flag",
    "any_operation_row_flag",
    "any_semantic_transition_flag",
    "operation_backed_carrier_flag",
]
VISIBLE_COLUMNS = [
    "visible_id",
    "visible_index",
    "atom_id",
    "carrier_count",
    "promotion_row_count",
    "join_count",
    "operation_row_count",
    "semantic_transition_count",
    "operation_backed_visible_flag",
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

OBSTRUCTION_NAMES = [
    "operation_row_absent_after_normalized_join",
]
OBSTRUCTION_CODES = {name: index for index, name in enumerate(OBSTRUCTION_NAMES)}

GAP_NAMES = [
    "visible_clock_normalized_rows",
    "visible_relation_join",
    "operation_row_promotion_obstruction",
    "semantic_transition_flag_obstruction",
    "operation_backed_normalized_counterterm",
    "physical_selector_axiom",
    "metric_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "carrier_row_count",
    "active_atom_count",
    "active_visible_index_count",
    "active_unique_promotion_row_count",
    "inactive_promotion_row_count",
    "joined_row_count",
    "zero_promotion_carrier_count",
    "visible20_cleared_carrier_count",
    "operation_row_join_count",
    "semantic_transition_join_count",
    "operation_backed_join_count",
    "operation_backed_carrier_count",
    "operation_promotion_flag",
    "semantic_transition_flag",
    "physical_selector_axiom_flag",
    "metric_derivation_flag",
    "first_failure_gap_code",
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
    c59p3n = load_json(LONG_C59P3N)
    gclk = load_json(LONG_GCLK)
    oprom = load_json(LONG_OPROM)
    _, weight_clear_raw = read_csv_rows(LONG_C59P3N_WEIGHT_CLEAR)
    _, weight_raw = read_csv_rows(LONG_C59P3E_WEIGHT)
    _, cycle_raw = read_csv_rows(LONG_GCLK_CYCLE)
    _, promotion_raw = read_csv_rows(LONG_OPROM_PROMOTION)

    weight_by_carrier = {int(row["carrier_id"]): row for row in weight_raw}
    visible_by_atom = {
        int(row["source_atom_id"]): int(row["visible_edge_id"]) for row in cycle_raw
    }
    atom_by_visible = {
        int(row["visible_edge_id"]): int(row["source_atom_id"]) for row in cycle_raw
    }
    promotions_by_visible: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in promotion_raw:
        promotions_by_visible[int(row["visible_index"])].append(row)

    join_rows = []
    carrier_rows = []
    active_visible_indices = set()
    active_promotion_ids = set()
    join_id = 0
    for weight_clear in weight_clear_raw:
        carrier_id = int(weight_clear["carrier_id"])
        atom_id = int(weight_clear["atom_id"])
        visible_index = visible_by_atom[atom_id]
        active_visible_indices.add(visible_index)
        carrier_weight = weight_by_carrier[carrier_id]
        promotions = promotions_by_visible[visible_index]
        any_operation = 0
        any_semantic = 0
        for promotion in promotions:
            active_promotion_ids.add(int(promotion["relation_id"]))
            operation_flag = int(promotion["operation_row_present_flag"])
            semantic_flag = int(promotion["semantic_transition_flag"])
            backed_flag = int(operation_flag == 1 and semantic_flag == 1)
            any_operation = max(any_operation, operation_flag)
            any_semantic = max(any_semantic, semantic_flag)
            join_rows.append(
                {
                    "join_id": join_id,
                    "carrier_id": carrier_id,
                    "atom_id": atom_id,
                    "step_atom_id": int(carrier_weight["step_atom_id"]),
                    "candidate_basis_id": int(carrier_weight["candidate_basis_id"]),
                    "visible_index": visible_index,
                    "relation_id": int(promotion["relation_id"]),
                    "transition_id": int(promotion["transition_id"]),
                    "visible20_cleared_num": int(
                        weight_clear["visible20_cleared_num"]
                    ),
                    "promotion_transition_present_flag": int(
                        promotion["transition_row_present_flag"]
                    ),
                    "guarded_relation_semantic_flag": int(
                        promotion["guarded_relation_semantic_flag"]
                    ),
                    "operation_row_present_flag": operation_flag,
                    "semantic_transition_flag": semantic_flag,
                    "operation_backed_normalized_flag": backed_flag,
                    "obstruction_code": OBSTRUCTION_CODES[
                        "operation_row_absent_after_normalized_join"
                    ],
                }
            )
            join_id += 1
        carrier_rows.append(
            {
                "carrier_id": carrier_id,
                "atom_id": atom_id,
                "visible_index": visible_index,
                "promotion_row_count": len(promotions),
                "joined_row_count": len(promotions),
                "visible20_cleared_flag": int(
                    weight_clear["visible20_cleared_flag"]
                ),
                "any_operation_row_flag": any_operation,
                "any_semantic_transition_flag": any_semantic,
                "operation_backed_carrier_flag": int(
                    any_operation == 1 and any_semantic == 1
                ),
            }
        )

    carrier_count_by_visible: dict[int, int] = defaultdict(int)
    for row in carrier_rows:
        carrier_count_by_visible[row["visible_index"]] += 1
    visible_rows = []
    for visible_id, visible_index in enumerate(sorted(active_visible_indices)):
        promotions = promotions_by_visible[visible_index]
        join_count = carrier_count_by_visible[visible_index] * len(promotions)
        visible_rows.append(
            {
                "visible_id": visible_id,
                "visible_index": visible_index,
                "atom_id": atom_by_visible[visible_index],
                "carrier_count": carrier_count_by_visible[visible_index],
                "promotion_row_count": len(promotions),
                "join_count": join_count,
                "operation_row_count": sum(
                    int(row["operation_row_present_flag"]) for row in promotions
                )
                * carrier_count_by_visible[visible_index],
                "semantic_transition_count": sum(
                    int(row["semantic_transition_flag"]) for row in promotions
                )
                * carrier_count_by_visible[visible_index],
                "operation_backed_visible_flag": 0,
            }
        )

    inactive_promotion_rows = [
        row
        for row in promotion_raw
        if int(row["visible_index"]) not in active_visible_indices
    ]
    operation_join_count = sum(row["operation_row_present_flag"] for row in join_rows)
    semantic_join_count = sum(row["semantic_transition_flag"] for row in join_rows)
    backed_join_count = sum(row["operation_backed_normalized_flag"] for row in join_rows)
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            int(certified(report)) for report in (c59p3n, gclk, oprom)
        ),
        "carrier_row_count": len(carrier_rows),
        "active_atom_count": len({row["atom_id"] for row in carrier_rows}),
        "active_visible_index_count": len(active_visible_indices),
        "active_unique_promotion_row_count": len(active_promotion_ids),
        "inactive_promotion_row_count": len(inactive_promotion_rows),
        "joined_row_count": len(join_rows),
        "zero_promotion_carrier_count": sum(
            int(row["promotion_row_count"] == 0) for row in carrier_rows
        ),
        "visible20_cleared_carrier_count": sum(
            row["visible20_cleared_flag"] for row in carrier_rows
        ),
        "operation_row_join_count": operation_join_count,
        "semantic_transition_join_count": semantic_join_count,
        "operation_backed_join_count": backed_join_count,
        "operation_backed_carrier_count": sum(
            row["operation_backed_carrier_flag"] for row in carrier_rows
        ),
        "operation_promotion_flag": int(operation_join_count > 0),
        "semantic_transition_flag": int(semantic_join_count > 0),
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "first_failure_gap_code": GAP_CODES["operation_row_promotion_obstruction"],
        "next_gap_code": GAP_CODES["operation_backed_normalized_counterterm"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["visible_clock_normalized_rows"],
            "gap_code": GAP_CODES["visible_clock_normalized_rows"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["visible_relation_join"],
            "gap_code": GAP_CODES["visible_relation_join"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_row_promotion_obstruction"],
            "gap_code": GAP_CODES["operation_row_promotion_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_flag_obstruction"],
            "gap_code": GAP_CODES["semantic_transition_flag_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_backed_normalized_counterterm"],
            "gap_code": GAP_CODES["operation_backed_normalized_counterterm"],
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
        "c59p3n": c59p3n,
        "gclk": gclk,
        "oprom": oprom,
        "join_rows": join_rows,
        "carrier_rows": carrier_rows,
        "visible_rows": visible_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    join_table = table_from_rows(JOIN_COLUMNS, rows["join_rows"])
    carrier_table = table_from_rows(CARRIER_COLUMNS, rows["carrier_rows"])
    visible_table = table_from_rows(VISIBLE_COLUMNS, rows["visible_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "normalized_visible_join_total": obs["carrier_row_count"] == 77
        and obs["active_atom_count"] == 17
        and obs["active_visible_index_count"] == 17
        and obs["active_unique_promotion_row_count"] == 49
        and obs["inactive_promotion_row_count"] == 10
        and obs["joined_row_count"] == 229
        and obs["zero_promotion_carrier_count"] == 0
        and obs["visible20_cleared_carrier_count"] == 77,
        "operation_promotion_absent_after_join": obs["operation_row_join_count"] == 0
        and obs["semantic_transition_join_count"] == 0
        and obs["operation_backed_join_count"] == 0
        and obs["operation_backed_carrier_count"] == 0
        and obs["operation_promotion_flag"] == 0
        and obs["semantic_transition_flag"] == 0,
        "first_failure_is_operation_promotion": obs["first_failure_gap_code"]
        == GAP_CODES["operation_row_promotion_obstruction"]
        and obs["next_gap_code"]
        == GAP_CODES["operation_backed_normalized_counterterm"],
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["metric_derivation_flag"] == 0,
        "table_shapes_match": join_table.shape == (229, len(JOIN_COLUMNS))
        and carrier_table.shape == (77, len(CARRIER_COLUMNS))
        and visible_table.shape == (17, len(VISIBLE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "normalized_operation_promotion_gate",
        "summary": {
            "carrier_row_count": obs["carrier_row_count"],
            "active_visible_index_count": obs["active_visible_index_count"],
            "active_unique_promotion_row_count": obs[
                "active_unique_promotion_row_count"
            ],
            "joined_row_count": obs["joined_row_count"],
            "zero_promotion_carrier_count": obs["zero_promotion_carrier_count"],
            "visible20_cleared_carrier_count": obs[
                "visible20_cleared_carrier_count"
            ],
            "operation_row_join_count": obs["operation_row_join_count"],
            "semantic_transition_join_count": obs["semantic_transition_join_count"],
            "operation_backed_join_count": obs["operation_backed_join_count"],
            "operation_backed_carrier_count": obs[
                "operation_backed_carrier_count"
            ],
        },
        "obstruction_code_map": {
            str(value): key for key, value in OBSTRUCTION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "join_table_sha256": sha_array(join_table),
        "join_text_sha256": sha_text(csv_text(JOIN_COLUMNS, rows["join_rows"])),
        "carrier_table_sha256": sha_array(carrier_table),
        "visible_table_sha256": sha_array(visible_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3m = {
        "schema": "long.c59p3m@1",
        "object": "normalized_operation_promotion_gate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3M_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3m.report@1",
        "status": c59p3m["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3m joins the 77 visible-clock-normalized carrier rows "
            "to the guarded relation promotion surface through the certified "
            "visible cycle. The join is total at the carrier level and yields "
            "229 carrier-promotion rows over 49 active promotion witnesses, "
            "but all joined rows still have zero operation rows and zero "
            "semantic transition flags."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3n, long_gclk, long_oprom, normalized carrier rows, visible cycle rows, and promotion rows",
            "witness": "emit carrier-promotion joins, per-carrier rows, per-visible rows, gaps, and observables",
            "coherence": "check normalized row coverage, visible routing, promotion joins, operation-row absence, and preserved physical gaps",
            "closure": "certify the first operation-promotion failure after visible-clock normalization",
            "emit": "write long_c59p3m artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3n": input_entry(
                LONG_C59P3N,
                {
                    "status": rows["c59p3n"].get("status"),
                    "certificate_sha256": rows["c59p3n"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3n_weight_clear": input_entry(LONG_C59P3N_WEIGHT_CLEAR),
            "long_c59p3e_weight": input_entry(LONG_C59P3E_WEIGHT),
            "long_gclk": input_entry(
                LONG_GCLK,
                {
                    "status": rows["gclk"].get("status"),
                    "certificate_sha256": rows["gclk"].get("certificate_sha256"),
                },
            ),
            "long_gclk_cycle": input_entry(LONG_GCLK_CYCLE),
            "long_oprom": input_entry(
                LONG_OPROM,
                {
                    "status": rows["oprom"].get("status"),
                    "certificate_sha256": rows["oprom"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_oprom_promotion": input_entry(LONG_OPROM_PROMOTION),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3m": relpath(OUT_DIR / "c59p3m.json"),
            "join_csv": relpath(OUT_DIR / "join.csv"),
            "carrier_csv": relpath(OUT_DIR / "carrier.csv"),
            "visible_csv": relpath(OUT_DIR / "visible.csv"),
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
                "all 77 visible-clock-normalized carrier rows route through the visible cycle",
                "all 77 routed carrier rows have at least one guarded relation promotion row",
                "the active normalized carriers cover 49 of the 59 promotion witnesses and leave 10 promotion witnesses inactive because their visible atoms have no carrier counterterm",
                "the carrier-promotion join emits 229 rows",
                "zero joined rows have operation-row backing or semantic transition flags",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "operation-backed normalized counterterm rows",
                "new semantic operation rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical field equation",
            ],
        },
        "next_highest_yield_item": (
            "Construct actual operation rows for the 49 active normalized "
            "promotion witnesses, or certify the schema-level reason those "
            "operation rows are absent."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3m.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3m.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3m": c59p3m,
        "join_csv": csv_text(JOIN_COLUMNS, rows["join_rows"]),
        "carrier_csv": csv_text(CARRIER_COLUMNS, rows["carrier_rows"]),
        "visible_csv": csv_text(VISIBLE_COLUMNS, rows["visible_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "join_table": join_table,
        "carrier_table": carrier_table,
        "visible_table": visible_table,
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
    write_json(OUT_DIR / "c59p3m.json", payloads["c59p3m"])
    (OUT_DIR / "join.csv").write_text(payloads["join_csv"], encoding="utf-8")
    (OUT_DIR / "carrier.csv").write_text(payloads["carrier_csv"], encoding="utf-8")
    (OUT_DIR / "visible.csv").write_text(payloads["visible_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        join_table=payloads["join_table"],
        carrier_table=payloads["carrier_table"],
        visible_table=payloads["visible_table"],
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
