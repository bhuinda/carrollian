from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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
    from .derive_long_lln import STATUS as LONG_LLN_STATUS
    from .derive_long_path import (
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        OUT_DIR as LONG_PATH_DIR,
        STATUS as LONG_PATH_STATUS,
    )
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_lln import STATUS as LONG_LLN_STATUS
    from derive_long_path import (
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        OUT_DIR as LONG_PATH_DIR,
        STATUS as LONG_PATH_STATUS,
    )
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_comp"
STATUS = "LONG_COMP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_PATH_REPORT = LONG_PATH_DIR / "report.json"
LONG_PATH_COMPONENT = LONG_PATH_DIR / "component.csv"
LONG_PATH_PATH = LONG_PATH_DIR / "path.csv"
LONG_PATH_STEP = LONG_PATH_DIR / "step.csv"
LONG_PATH_TABLES = LONG_PATH_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_comp.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_comp.py"

PAIR_TEXT_HASH = (
    "77d97eb5c31a576f4e85661fff2ad19ed39e6fbe914f55efe9d20ad05008d0e5"
)
PATH_TEXT_HASH = (
    "82c34f7eb3d2c4165933c64c868eb5fd0e49684f47caf92e8ebd834c31874ab7"
)
TRANSITION_TEXT_HASH = (
    "c9637711b0bf9c3fb596027a6fd6cd25f679bcef675deb4fc3455f9e295e1e26"
)

PAIR_COLUMNS = [
    "pair_id",
    "from_component_id",
    "to_component_id",
    "transition_count",
    "left_margin_min",
    "left_margin_max",
    "right_margin_min",
    "right_margin_max",
    "zeta_both_count",
    "exact_source_match_count",
]
PATH_COLUMNS = [
    "path_id",
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "step_count",
    "transition_count",
    "zeta_left_transition_count",
    "zeta_right_transition_count",
    "zeta_both_transition_count",
    "exact_left_transition_count",
    "exact_right_transition_count",
    "zeta_path_flag",
    "exact_path_flag",
    "long_tens_gap_flag",
    "gap_zeta_witness_flag",
]
TRANSITION_COLUMNS = [
    "transition_id",
    "path_id",
    "fiber_row_id",
    "from_step_index",
    "to_step_index",
    "from_component_id",
    "to_component_id",
    "from_raw_row_id",
    "to_raw_row_id",
    "from_target_addr",
    "to_source0_addr",
    "to_source1_addr",
    "left_margin",
    "right_margin",
    "zeta_left_flag",
    "zeta_right_flag",
    "zeta_both_flag",
    "exact_left_flag",
    "exact_right_flag",
    "long_tens_gap_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "pair_row_count",
    "path_row_count",
    "step_row_count",
    "transition_row_count",
    "one_step_path_count",
    "gap_path_count",
    "existing_path_count",
    "gap_transition_count",
    "existing_transition_count",
    "zeta_left_transition_count",
    "zeta_right_transition_count",
    "zeta_both_transition_count",
    "zeta_path_count",
    "gap_zeta_path_count",
    "existing_zeta_path_count",
    "exact_left_transition_count",
    "exact_right_transition_count",
    "exact_path_count",
    "left_margin_min",
    "left_margin_max",
    "right_margin_min",
    "right_margin_max",
    "current_alexandrov_zeta_composable_path_flag",
    "current_exact_source_target_composable_path_flag",
    "current_c985_semantic_composable_path_flag",
    "current_lln_product_sample_independence_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def transitions_for_path(steps: list[dict[str, int]]) -> list[tuple[dict[str, int], dict[str, int]]]:
    ordered = sorted(steps, key=lambda row: row["step_index"])
    return list(zip(ordered, ordered[1:]))


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_path": load_json(LONG_PATH_REPORT),
    }
    path_input_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    step_input_rows = int_rows(read_csv_rows(LONG_PATH_STEP))
    path_by_id = {row["path_id"]: row for row in path_input_rows}
    steps_by_path: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in step_input_rows:
        steps_by_path[row["path_id"]].append(row)

    transition_rows: list[dict[str, int]] = []
    path_rows: list[dict[str, int]] = []
    transition_id = 0
    for path_id in sorted(path_by_id):
        path = path_by_id[path_id]
        steps = steps_by_path[path_id]
        local_transitions = []
        for left, right in transitions_for_path(steps):
            left_margin = right["source0_addr"] - left["target_addr"]
            right_margin = right["source1_addr"] - left["target_addr"]
            zeta_left = int(left_margin >= 0)
            zeta_right = int(right_margin >= 0)
            exact_left = int(left["target_addr"] == right["source0_addr"])
            exact_right = int(left["target_addr"] == right["source1_addr"])
            row = {
                "transition_id": transition_id,
                "path_id": path_id,
                "fiber_row_id": path["fiber_row_id"],
                "from_step_index": left["step_index"],
                "to_step_index": right["step_index"],
                "from_component_id": left["component_id"],
                "to_component_id": right["component_id"],
                "from_raw_row_id": left["raw_row_id"],
                "to_raw_row_id": right["raw_row_id"],
                "from_target_addr": left["target_addr"],
                "to_source0_addr": right["source0_addr"],
                "to_source1_addr": right["source1_addr"],
                "left_margin": left_margin,
                "right_margin": right_margin,
                "zeta_left_flag": zeta_left,
                "zeta_right_flag": zeta_right,
                "zeta_both_flag": int(zeta_left and zeta_right),
                "exact_left_flag": exact_left,
                "exact_right_flag": exact_right,
                "long_tens_gap_flag": path["long_tens_gap_flag"],
            }
            transition_rows.append(row)
            local_transitions.append(row)
            transition_id += 1
        transition_count = len(local_transitions)
        zeta_left_count = sum(row["zeta_left_flag"] for row in local_transitions)
        zeta_right_count = sum(row["zeta_right_flag"] for row in local_transitions)
        zeta_both_count = sum(row["zeta_both_flag"] for row in local_transitions)
        exact_left_count = sum(row["exact_left_flag"] for row in local_transitions)
        exact_right_count = sum(row["exact_right_flag"] for row in local_transitions)
        zeta_path = int(zeta_both_count == transition_count)
        exact_path = int(
            transition_count > 0
            and (exact_left_count + exact_right_count) == transition_count
        )
        path_rows.append(
            {
                "path_id": path_id,
                "fiber_row_id": path["fiber_row_id"],
                "sample_count": path["sample_count"],
                "sum_value": path["sum_value"],
                "step_count": path["step_count"],
                "transition_count": transition_count,
                "zeta_left_transition_count": zeta_left_count,
                "zeta_right_transition_count": zeta_right_count,
                "zeta_both_transition_count": zeta_both_count,
                "exact_left_transition_count": exact_left_count,
                "exact_right_transition_count": exact_right_count,
                "zeta_path_flag": zeta_path,
                "exact_path_flag": exact_path,
                "long_tens_gap_flag": path["long_tens_gap_flag"],
                "gap_zeta_witness_flag": int(
                    path["long_tens_gap_flag"] == 1 and zeta_path == 1
                ),
            }
        )

    pair_rows: list[dict[str, int]] = []
    grouped: dict[tuple[int, int], list[dict[str, int]]] = defaultdict(list)
    for row in transition_rows:
        grouped[(row["from_component_id"], row["to_component_id"])].append(row)
    for pair_id, ((from_component, to_component), rows) in enumerate(
        sorted(grouped.items())
    ):
        pair_rows.append(
            {
                "pair_id": pair_id,
                "from_component_id": from_component,
                "to_component_id": to_component,
                "transition_count": len(rows),
                "left_margin_min": min(row["left_margin"] for row in rows),
                "left_margin_max": max(row["left_margin"] for row in rows),
                "right_margin_min": min(row["right_margin"] for row in rows),
                "right_margin_max": max(row["right_margin"] for row in rows),
                "zeta_both_count": sum(row["zeta_both_flag"] for row in rows),
                "exact_source_match_count": sum(
                    int(row["exact_left_flag"] or row["exact_right_flag"])
                    for row in rows
                ),
            }
        )

    obs = {
        "pair_row_count": len(pair_rows),
        "path_row_count": len(path_rows),
        "step_row_count": len(step_input_rows),
        "transition_row_count": len(transition_rows),
        "one_step_path_count": sum(
            int(row["transition_count"] == 0) for row in path_rows
        ),
        "gap_path_count": sum(row["long_tens_gap_flag"] for row in path_rows),
        "existing_path_count": sum(1 - row["long_tens_gap_flag"] for row in path_rows),
        "gap_transition_count": sum(
            row["long_tens_gap_flag"] for row in transition_rows
        ),
        "existing_transition_count": sum(
            1 - row["long_tens_gap_flag"] for row in transition_rows
        ),
        "zeta_left_transition_count": sum(
            row["zeta_left_flag"] for row in transition_rows
        ),
        "zeta_right_transition_count": sum(
            row["zeta_right_flag"] for row in transition_rows
        ),
        "zeta_both_transition_count": sum(
            row["zeta_both_flag"] for row in transition_rows
        ),
        "zeta_path_count": sum(row["zeta_path_flag"] for row in path_rows),
        "gap_zeta_path_count": sum(row["gap_zeta_witness_flag"] for row in path_rows),
        "existing_zeta_path_count": sum(
            int(row["long_tens_gap_flag"] == 0 and row["zeta_path_flag"] == 1)
            for row in path_rows
        ),
        "exact_left_transition_count": sum(
            row["exact_left_flag"] for row in transition_rows
        ),
        "exact_right_transition_count": sum(
            row["exact_right_flag"] for row in transition_rows
        ),
        "exact_path_count": sum(row["exact_path_flag"] for row in path_rows),
        "left_margin_min": min(row["left_margin"] for row in transition_rows),
        "left_margin_max": max(row["left_margin"] for row in transition_rows),
        "right_margin_min": min(row["right_margin"] for row in transition_rows),
        "right_margin_max": max(row["right_margin"] for row in transition_rows),
        "current_alexandrov_zeta_composable_path_flag": 1,
        "current_exact_source_target_composable_path_flag": 0,
        "current_c985_semantic_composable_path_flag": 0,
        "current_lln_product_sample_independence_flag": 1,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    pair_hash = hashlib.sha256(
        digest_text(PAIR_COLUMNS, pair_rows).encode("ascii")
    ).hexdigest()
    path_hash = hashlib.sha256(
        digest_text(PATH_COLUMNS, path_rows).encode("ascii")
    ).hexdigest()
    transition_hash = hashlib.sha256(
        digest_text(TRANSITION_COLUMNS, transition_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "pair_rows": pair_rows,
        "path_rows": path_rows,
        "transition_rows": transition_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "pair_table": table_from_rows(PAIR_COLUMNS, pair_rows),
        "path_table": table_from_rows(PATH_COLUMNS, path_rows),
        "transition_table": table_from_rows(TRANSITION_COLUMNS, transition_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "pair_hash": pair_hash,
        "path_hash": path_hash,
        "transition_hash": transition_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_lln"].get("status"),
            input_reports["long_path"].get("status"),
        )
        == (LONG_LLN_STATUS, LONG_PATH_STATUS),
        "transition_inventory_exact": (
            obs["pair_row_count"],
            obs["path_row_count"],
            obs["step_row_count"],
            obs["transition_row_count"],
            obs["one_step_path_count"],
            obs["gap_path_count"],
            obs["existing_path_count"],
            obs["gap_transition_count"],
            obs["existing_transition_count"],
        )
        == (5, 288, 3128, 2840, 3, 208, 80, 2476, 364),
        "alexandrov_zeta_composability_exact": (
            obs["zeta_left_transition_count"],
            obs["zeta_right_transition_count"],
            obs["zeta_both_transition_count"],
            obs["zeta_path_count"],
            obs["gap_zeta_path_count"],
            obs["existing_zeta_path_count"],
            obs["left_margin_min"],
            obs["right_margin_min"],
            obs["left_margin_max"],
            obs["right_margin_max"],
            rows["pair_hash"],
            rows["path_hash"],
            rows["transition_hash"],
        )
        == (
            2840,
            2840,
            2840,
            288,
            208,
            80,
            8,
            152,
            171,
            708,
            PAIR_TEXT_HASH,
            PATH_TEXT_HASH,
            TRANSITION_TEXT_HASH,
        ),
        "exact_source_target_not_present": (
            obs["exact_left_transition_count"],
            obs["exact_right_transition_count"],
            obs["exact_path_count"],
        )
        == (0, 0, 0),
        "current_representation_exact": (
            obs["current_alexandrov_zeta_composable_path_flag"],
            obs["current_exact_source_target_composable_path_flag"],
            obs["current_c985_semantic_composable_path_flag"],
            obs["current_lln_product_sample_independence_flag"],
        )
        == (1, 0, 0, 1),
        "table_shapes_match": (
            tuple(rows["pair_table"].shape),
            tuple(rows["path_table"].shape),
            tuple(rows["transition_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (5, len(PAIR_COLUMNS)),
            (288, len(PATH_COLUMNS)),
            (2840, len(TRANSITION_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "alexandrov_zeta_composable_sample_paths",
        "zeta_rule": "for adjacent raw lookup rows r_i -> r_{i+1}, require target_i <= source0_{i+1} and target_i <= source1_{i+1}",
        "inventory": {
            "pair_row_count": obs["pair_row_count"],
            "path_row_count": obs["path_row_count"],
            "step_row_count": obs["step_row_count"],
            "transition_row_count": obs["transition_row_count"],
            "one_step_path_count": obs["one_step_path_count"],
            "gap_path_count": obs["gap_path_count"],
            "existing_path_count": obs["existing_path_count"],
            "gap_transition_count": obs["gap_transition_count"],
            "existing_transition_count": obs["existing_transition_count"],
        },
        "zeta_composability": {
            "zeta_left_transition_count": obs["zeta_left_transition_count"],
            "zeta_right_transition_count": obs["zeta_right_transition_count"],
            "zeta_both_transition_count": obs["zeta_both_transition_count"],
            "zeta_path_count": obs["zeta_path_count"],
            "gap_zeta_path_count": obs["gap_zeta_path_count"],
            "existing_zeta_path_count": obs["existing_zeta_path_count"],
            "left_margin_range": [obs["left_margin_min"], obs["left_margin_max"]],
            "right_margin_range": [obs["right_margin_min"], obs["right_margin_max"]],
            "pair_table_sha256": sha_array(rows["pair_table"]),
            "pair_text_sha256": rows["pair_hash"],
            "path_table_sha256": sha_array(rows["path_table"]),
            "path_text_sha256": rows["path_hash"],
            "transition_table_sha256": sha_array(rows["transition_table"]),
            "transition_text_sha256": rows["transition_hash"],
        },
        "exact_composability": {
            "exact_left_transition_count": obs["exact_left_transition_count"],
            "exact_right_transition_count": obs["exact_right_transition_count"],
            "exact_path_count": obs["exact_path_count"],
        },
        "current_representation": {
            "current_alexandrov_zeta_composable_path_flag": obs[
                "current_alexandrov_zeta_composable_path_flag"
            ],
            "current_exact_source_target_composable_path_flag": obs[
                "current_exact_source_target_composable_path_flag"
            ],
            "current_c985_semantic_composable_path_flag": obs[
                "current_c985_semantic_composable_path_flag"
            ],
            "current_lln_product_sample_independence_flag": obs[
                "current_lln_product_sample_independence_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    comp_payload = {
        "schema": "long.comp@1",
        "object": "alexandrov_zeta_composable_sample_paths",
        "status": STATUS if all(checks.values()) else "LONG_COMP_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.comp.report@1",
        "status": comp_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_comp certifies that the explicit long_path raw product "
            "witnesses are composable in the Alexandrov-line zeta profunctor: "
            "for every adjacent pair of raw lookup rows, the previous target "
            "address is below both source addresses of the next row. This "
            "supplies a finite profunctorial path structure for the LLN sample "
            "witnesses, while exact source/target equality and semantic C985 "
            "composition remain unclaimed."
        ),
        "stage_protocol": {
            "draft": "read long_path step-expanded witnesses and long_lln zeta rule",
            "witness": "test target_i <= source0_{i+1} and target_i <= source1_{i+1} on every adjacent raw-row transition",
            "coherence": "check transition inventory, zeta margins, exact-composition absence, hashes, statuses, and table shapes",
            "closure": "emit Alexandrov-zeta composability without claiming exact C985 composability",
            "emit": "write long_comp artifacts and verifier hook",
        },
        "inputs": {
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": rows["input_reports"]["long_path"].get("status")},
            ),
            "long_path_component": input_entry(LONG_PATH_COMPONENT),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_step": input_entry(LONG_PATH_STEP),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "comp": relpath(OUT_DIR / "comp.json"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "path_csv": relpath(OUT_DIR / "path.csv"),
            "transition_csv": relpath(OUT_DIR / "transition.csv"),
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
                "all adjacent transitions in all 288 long_path witnesses are zeta-composable over the finite Alexandrov line",
                "all 208 gap-fiber witnesses are zeta-composable over the finite Alexandrov line",
                "the minimum zeta margins are positive: 8 on source0 and 152 on source1",
                "exact source/target equality is absent from these witnesses",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic C985 associator composition",
                "a genuine long_prof horizon-16 profunctor",
                "all possible raw product paths in each fiber",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_sheaf: turn the zeta-composable sample paths into an "
            "Alexandrov open/closed support sheaf and test restriction/gluing "
            "for LLN observables."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.comp.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.comp.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "comp": comp_payload,
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "path_csv": csv_text(PATH_COLUMNS, rows["path_rows"]),
        "transition_csv": csv_text(TRANSITION_COLUMNS, rows["transition_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "pair_table": rows["pair_table"],
        "path_table": rows["path_table"],
        "transition_table": rows["transition_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "report": report,
        "manifest": manifest,
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
    write_json(OUT_DIR / "comp.json", payloads["comp"])
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "path.csv").write_text(payloads["path_csv"], encoding="utf-8")
    (OUT_DIR / "transition.csv").write_text(
        payloads["transition_csv"], encoding="utf-8"
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        pair_table=payloads["pair_table"],
        path_table=payloads["path_table"],
        transition_table=payloads["transition_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
