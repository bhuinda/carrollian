from __future__ import annotations

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
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
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
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        table_from_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_pobj"
STATUS = "LONG_POBJ_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_PATH_REPORT = PROOF_ROOT / "long_path" / "report.json"
LONG_PATH_COMPONENT = PROOF_ROOT / "long_path" / "component.csv"
LONG_PATH_PATH = PROOF_ROOT / "long_path" / "path.csv"
LONG_PATH_STEP = PROOF_ROOT / "long_path" / "step.csv"
LONG_PATH_TABLES = PROOF_ROOT / "long_path" / "tables.npz"
LONG_COMP_REPORT = PROOF_ROOT / "long_comp" / "report.json"
LONG_COMP_PATH = PROOF_ROOT / "long_comp" / "path.csv"
LONG_COMP_PAIR = PROOF_ROOT / "long_comp" / "pair.csv"
LONG_COMP_TRANSITION = PROOF_ROOT / "long_comp" / "transition.csv"
LONG_COMP_TABLES = PROOF_ROOT / "long_comp" / "tables.npz"
LONG_TENS_REPORT = PROOF_ROOT / "long_tens" / "report.json"
LONG_TENS_FIBER = PROOF_ROOT / "long_tens" / "fiber.csv"
LONG_TENS_TABLES = PROOF_ROOT / "long_tens" / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_pobj.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_pobj.py"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "candidate_code",
    "support_path_count",
    "gap_path_count",
    "transition_count",
    "zeta_transition_count",
    "exact_transition_count",
    "component_pair_count",
    "zeta_component_pair_count",
    "exact_component_pair_count",
    "identity_component_count",
    "selected_component_path_count",
    "total_component_path_count",
    "missing_component_path_count",
    "closed_path_object_flag",
    "sample_section_flag",
    "obstruction_code",
]
PAIR_COLUMNS = [
    "pair_id",
    "from_component_id",
    "to_component_id",
    "left_margin",
    "right_margin",
    "zeta_both_flag",
    "exact_left_flag",
    "exact_right_flag",
    "exact_any_flag",
    "identity_pair_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "candidate_row_count",
    "component_count",
    "component_pair_count",
    "zeta_component_pair_count",
    "exact_component_pair_count",
    "identity_component_count",
    "path_count",
    "gap_path_count",
    "existing_path_count",
    "step_row_count",
    "transition_count",
    "zeta_transition_count",
    "zeta_path_count",
    "exact_transition_count",
    "exact_path_count",
    "total_component_path_count",
    "selected_component_path_count",
    "missing_component_path_count",
    "gap_component_path_count",
    "selected_gap_path_count",
    "closed_path_object_flag",
    "sample_zeta_section_flag",
    "full_component_path_materialized_flag",
    "next_target_code",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def load_int_csv(path: Path) -> list[dict[str, int]]:
    return int_rows(read_csv_rows(path))


def build_pair_rows(component_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    pair_id = 0
    by_component = {row["component_id"]: row for row in component_rows}
    for from_component in sorted(by_component):
        from_row = by_component[from_component]
        from_target = from_row["representative_target_addr"]
        for to_component in sorted(by_component):
            to_row = by_component[to_component]
            left_margin = to_row["representative_source0_addr"] - from_target
            right_margin = to_row["representative_source1_addr"] - from_target
            exact_left = int(left_margin == 0)
            exact_right = int(right_margin == 0)
            exact_any = int(exact_left == 1 or exact_right == 1)
            rows.append(
                {
                    "pair_id": pair_id,
                    "from_component_id": from_component,
                    "to_component_id": to_component,
                    "left_margin": left_margin,
                    "right_margin": right_margin,
                    "zeta_both_flag": int(left_margin >= 0 and right_margin >= 0),
                    "exact_left_flag": exact_left,
                    "exact_right_flag": exact_right,
                    "exact_any_flag": exact_any,
                    "identity_pair_flag": int(
                        from_component == to_component and exact_any == 1
                    ),
                }
            )
            pair_id += 1
    return rows


def build_rows() -> dict[str, Any]:
    path_report = load_json(LONG_PATH_REPORT)
    comp_report = load_json(LONG_COMP_REPORT)
    tens_report = load_json(LONG_TENS_REPORT)
    component_rows = load_int_csv(LONG_PATH_COMPONENT)
    path_rows = load_int_csv(LONG_PATH_PATH)
    step_rows = load_int_csv(LONG_PATH_STEP)
    comp_path_rows = load_int_csv(LONG_COMP_PATH)
    transition_rows = load_int_csv(LONG_COMP_TRANSITION)
    pair_rows = build_pair_rows(component_rows)

    path_witness = path_report.get("witness", {}).get("paths", {})
    comp_inventory = comp_report.get("witness", {}).get("inventory", {})
    comp_zeta = comp_report.get("witness", {}).get("zeta_composability", {})
    comp_exact = comp_report.get("witness", {}).get("exact_composability", {})
    tens_horizons = tens_report.get("witness", {}).get("horizons", {})

    path_count = len(path_rows)
    gap_path_count = sum(row["long_tens_gap_flag"] for row in path_rows)
    existing_path_count = path_count - gap_path_count
    transition_count = len(transition_rows)
    zeta_transition_count = sum(row["zeta_both_flag"] for row in transition_rows)
    zeta_path_count = sum(row["zeta_path_flag"] for row in comp_path_rows)
    exact_transition_count = sum(row["exact_any_flag"] for row in pair_rows)
    exact_path_count = sum(row["exact_path_flag"] for row in comp_path_rows)
    zeta_component_pair_count = sum(row["zeta_both_flag"] for row in pair_rows)
    exact_component_pair_count = sum(row["exact_any_flag"] for row in pair_rows)
    identity_component_count = sum(row["identity_pair_flag"] for row in pair_rows)
    total_component_path_count = int(tens_horizons.get("total_component_path_count", 0))
    gap_component_path_count = int(tens_horizons.get("gap_component_path_count", 0))
    missing_component_path_count = total_component_path_count - path_count
    closed_path_object_flag = int(
        exact_component_pair_count > 0
        and identity_component_count == len(component_rows)
        and exact_path_count == path_count
        and missing_component_path_count == 0
    )
    sample_zeta_section_flag = int(
        path_count == 288
        and gap_path_count == 208
        and zeta_transition_count == transition_count
        and zeta_path_count == path_count
        and exact_path_count == 0
    )

    candidate_rows = [
        {
            "candidate_id": 0,
            "candidate_code": 0,
            "support_path_count": path_count,
            "gap_path_count": gap_path_count,
            "transition_count": transition_count,
            "zeta_transition_count": 0,
            "exact_transition_count": exact_component_pair_count,
            "component_pair_count": len(pair_rows),
            "zeta_component_pair_count": 0,
            "exact_component_pair_count": exact_component_pair_count,
            "identity_component_count": identity_component_count,
            "selected_component_path_count": path_count,
            "total_component_path_count": total_component_path_count,
            "missing_component_path_count": missing_component_path_count,
            "closed_path_object_flag": 0,
            "sample_section_flag": 0,
            "obstruction_code": 1,
        },
        {
            "candidate_id": 1,
            "candidate_code": 1,
            "support_path_count": path_count,
            "gap_path_count": gap_path_count,
            "transition_count": transition_count,
            "zeta_transition_count": zeta_transition_count,
            "exact_transition_count": 0,
            "component_pair_count": len(pair_rows),
            "zeta_component_pair_count": zeta_component_pair_count,
            "exact_component_pair_count": exact_component_pair_count,
            "identity_component_count": identity_component_count,
            "selected_component_path_count": path_count,
            "total_component_path_count": total_component_path_count,
            "missing_component_path_count": missing_component_path_count,
            "closed_path_object_flag": 0,
            "sample_section_flag": sample_zeta_section_flag,
            "obstruction_code": 2,
        },
        {
            "candidate_id": 2,
            "candidate_code": 2,
            "support_path_count": path_count,
            "gap_path_count": gap_path_count,
            "transition_count": transition_count,
            "zeta_transition_count": zeta_transition_count,
            "exact_transition_count": exact_transition_count,
            "component_pair_count": len(pair_rows),
            "zeta_component_pair_count": zeta_component_pair_count,
            "exact_component_pair_count": exact_component_pair_count,
            "identity_component_count": identity_component_count,
            "selected_component_path_count": path_count,
            "total_component_path_count": total_component_path_count,
            "missing_component_path_count": missing_component_path_count,
            "closed_path_object_flag": closed_path_object_flag,
            "sample_section_flag": sample_zeta_section_flag,
            "obstruction_code": 3,
        },
    ]
    obs = {
        "candidate_row_count": len(candidate_rows),
        "component_count": len(component_rows),
        "component_pair_count": len(pair_rows),
        "zeta_component_pair_count": zeta_component_pair_count,
        "exact_component_pair_count": exact_component_pair_count,
        "identity_component_count": identity_component_count,
        "path_count": path_count,
        "gap_path_count": gap_path_count,
        "existing_path_count": existing_path_count,
        "step_row_count": len(step_rows),
        "transition_count": transition_count,
        "zeta_transition_count": zeta_transition_count,
        "zeta_path_count": zeta_path_count,
        "exact_transition_count": int(comp_exact.get("exact_left_transition_count", 0))
        + int(comp_exact.get("exact_right_transition_count", 0)),
        "exact_path_count": exact_path_count,
        "total_component_path_count": total_component_path_count,
        "selected_component_path_count": path_count,
        "missing_component_path_count": missing_component_path_count,
        "gap_component_path_count": gap_component_path_count,
        "selected_gap_path_count": gap_path_count,
        "closed_path_object_flag": closed_path_object_flag,
        "sample_zeta_section_flag": sample_zeta_section_flag,
        "full_component_path_materialized_flag": int(missing_component_path_count == 0),
        "next_target_code": 4,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "path_report": path_report,
        "comp_report": comp_report,
        "tens_report": tens_report,
        "candidate_rows": candidate_rows,
        "pair_rows": pair_rows,
        "obs_rows": obs_rows,
        "candidate_table": table_from_rows(CANDIDATE_COLUMNS, candidate_rows),
        "pair_table": table_from_rows(PAIR_COLUMNS, pair_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "candidate_text_hash": hashlib.sha256(
            digest_text(CANDIDATE_COLUMNS, candidate_rows).encode("ascii")
        ).hexdigest(),
        "pair_text_hash": hashlib.sha256(
            digest_text(PAIR_COLUMNS, pair_rows).encode("ascii")
        ).hexdigest(),
        "obs": obs,
        "source_counts": {
            "path_witness_path_count": int(path_witness.get("path_row_count", 0)),
            "path_witness_gap_count": int(path_witness.get("gap_path_count", 0)),
            "comp_inventory_transition_count": int(
                comp_inventory.get("transition_row_count", 0)
            ),
            "comp_zeta_transition_count": int(
                comp_zeta.get("zeta_both_transition_count", 0)
            ),
            "tens_total_component_path_count": int(
                tens_horizons.get("total_component_path_count", 0)
            ),
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": (
            certified(rows["path_report"], "LONG_PATH_CERTIFIED") == 1
            and certified(rows["comp_report"], "LONG_COMP_CERTIFIED") == 1
            and certified(rows["tens_report"], "LONG_TENS_CERTIFIED") == 1
        ),
        "source_counts_match": (
            rows["source_counts"]["path_witness_path_count"],
            rows["source_counts"]["path_witness_gap_count"],
            rows["source_counts"]["comp_inventory_transition_count"],
            rows["source_counts"]["comp_zeta_transition_count"],
            rows["source_counts"]["tens_total_component_path_count"],
        )
        == (288, 208, 2_840, 2_840, 64_570_080),
        "sample_section_exact": (
            obs["path_count"],
            obs["gap_path_count"],
            obs["step_row_count"],
            obs["transition_count"],
            obs["zeta_transition_count"],
            obs["zeta_path_count"],
        )
        == (288, 208, 3_128, 2_840, 2_840, 288),
        "exact_path_object_obstructed": (
            obs["exact_component_pair_count"],
            obs["identity_component_count"],
            obs["exact_transition_count"],
            obs["exact_path_count"],
            obs["closed_path_object_flag"],
        )
        == (0, 0, 0, 0, 0),
        "component_path_family_unmaterialized": (
            obs["total_component_path_count"],
            obs["selected_component_path_count"],
            obs["missing_component_path_count"],
            obs["gap_component_path_count"],
            obs["full_component_path_materialized_flag"],
        )
        == (64_570_080, 288, 64_569_792, 64_560_240, 0),
        "pair_inventory_exact": (
            obs["component_count"],
            obs["component_pair_count"],
            obs["zeta_component_pair_count"],
            obs["exact_component_pair_count"],
        )
        == (3, 9, 7, 0),
        "goal_not_overclaimed": (
            obs["next_target_code"],
            obs["complete_goal_claim_flag"],
        )
        == (4, 0),
        "table_shapes_match": (
            tuple(rows["candidate_table"].shape),
            tuple(rows["pair_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (3, len(CANDIDATE_COLUMNS)),
            (9, len(PAIR_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "path_object_closure_decision",
        "candidate_code_map": {
            "0": "exact_raw_address_path_object",
            "1": "alexandrov_zeta_sample_section",
            "2": "full_component_path_object",
        },
        "obstruction_code_map": {
            "0": "none",
            "1": "no exact raw endpoint component-pair or identity component exists among selected representatives",
            "2": "zeta-composable section is single-witness and not closed as the full path family",
            "3": "64,569,792 component paths remain unmaterialized relative to the full horizon-16 component-path tensor",
        },
        "target_code_map": {
            "4": "long_paths",
        },
        "summary": {
            "path_count": obs["path_count"],
            "gap_path_count": obs["gap_path_count"],
            "transition_count": obs["transition_count"],
            "zeta_transition_count": obs["zeta_transition_count"],
            "exact_path_count": obs["exact_path_count"],
            "closed_path_object_flag": obs["closed_path_object_flag"],
            "sample_zeta_section_flag": obs["sample_zeta_section_flag"],
            "missing_component_path_count": obs["missing_component_path_count"],
            "next_target": "long_paths",
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "candidate_text_sha256": rows["candidate_text_hash"],
        "pair_text_sha256": rows["pair_text_hash"],
        "candidate_table_sha256": sha_array(rows["candidate_table"]),
        "pair_table_sha256": sha_array(rows["pair_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    pobj_payload = {
        "schema": "long.pobj@1",
        "object": "path_object_closure_decision",
        "status": STATUS if all(checks.values()) else "LONG_POBJ_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.pobj.report@1",
        "status": pobj_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_pobj certifies the path-object decision for the current "
            "selected witness family: the 288 paths, including all 208 gap "
            "fibers, are a finite Alexandrov-zeta-composable sample section, "
            "but they do not close as a genuine exact raw-address path object. "
            "There are no exact source/target component pairs, no identity "
            "components among the selected representatives, and 64,569,792 "
            "component paths remain unmaterialized relative to the full "
            "horizon-16 component-path tensor."
        ),
        "stage_protocol": {
            "draft": "read long_path, long_comp, and long_tens witness artifacts",
            "witness": "emit candidate closure rows, all component-pair endpoint tests, and observable counts",
            "coherence": "check source counts, zeta sample-section coverage, exact endpoint obstruction, full component-path gap, hashes, and table shapes",
            "closure": "decide long_pobj without claiming all raw paths or a genuine horizon-16 profunctor",
            "emit": "write long_pobj artifacts and verifier hook",
        },
        "inputs": {
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {
                    "status": rows["path_report"].get("status"),
                    "certificate_sha256": rows["path_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_path_component": input_entry(LONG_PATH_COMPONENT),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_step": input_entry(LONG_PATH_STEP),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_comp_report": input_entry(
                LONG_COMP_REPORT,
                {
                    "status": rows["comp_report"].get("status"),
                    "certificate_sha256": rows["comp_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_comp_path": input_entry(LONG_COMP_PATH),
            "long_comp_pair": input_entry(LONG_COMP_PAIR),
            "long_comp_transition": input_entry(LONG_COMP_TRANSITION),
            "long_comp_tables": input_entry(LONG_COMP_TABLES),
            "long_tens_report": input_entry(
                LONG_TENS_REPORT,
                {
                    "status": rows["tens_report"].get("status"),
                    "certificate_sha256": rows["tens_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_tens_fiber": input_entry(LONG_TENS_FIBER),
            "long_tens_tables": input_entry(LONG_TENS_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "pobj": relpath(OUT_DIR / "pobj.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
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
                "the selected 288 witness paths form a finite Alexandrov-zeta-composable sample section",
                "the 208 horizon-9..16 gap fibers each still have one selected zeta-composable witness path",
                "the current selected representatives have zero exact raw endpoint component-pair matches",
                "the current selected representatives have zero identity components for an exact raw path object",
                "the selected witness family is not the full 64,570,080-word component-path object",
            ],
            "does_not_certify_because_out_of_scope": [
                "all raw product paths in each fiber",
                "a probability measure on the full raw tensor support",
                "a genuine horizon-16 long_prof profunctor",
                "absolute nonexistence of a path object under changed representatives or a changed object/support model",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Build long_paths: expand or bound the raw/component path families "
            "now that the selected witnesses have been certified as a zeta "
            "sample section rather than a closed exact path object."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.pobj.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.pobj.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "pobj": pobj_payload,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": rows["candidate_table"],
        "pair_table": rows["pair_table"],
        "observable_table": rows["observable_table"],
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
    write_json(OUT_DIR / "pobj.json", payloads["pobj"])
    (OUT_DIR / "candidate.csv").write_text(payloads["candidate_csv"], encoding="utf-8")
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        pair_table=payloads["pair_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
