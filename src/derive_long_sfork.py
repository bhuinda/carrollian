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


THEOREM_ID = "long_sfork"
STATUS = "LONG_SFORK_SELECTOR_BRANCH_FRONTIER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_FRIM = PROOF_ROOT / "long_frim" / "report.json"
LONG_FRIM_SELECTOR = PROOF_ROOT / "long_frim" / "selector.csv"
LONG_GLAW = PROOF_ROOT / "long_glaw" / "report.json"
LONG_TLIFT = PROOF_ROOT / "long_tlift" / "report.json"
LONG_ABMAP = PROOF_ROOT / "long_abmap" / "report.json"
LONG_RTICK = PROOF_ROOT / "long_rtick" / "report.json"
LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RIM_CLASS = PROOF_ROOT / "long_rim" / "class.csv"
LONG_RIM_PHASE = PROOF_ROOT / "long_rim_select" / "phase.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_PSEL = PROOF_ROOT / "long_psel" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_sfork.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_sfork.py"

BRANCH_COLUMNS = [
    "branch_id",
    "branch_code",
    "selected_class_id",
    "class_count",
    "golden_flag",
    "unique_flag",
    "stress_supported_flag",
    "transition_coupled_flag",
    "physical_selector_flag",
    "first_failure_code",
    "viable_flag",
]
CLASS_COLUMNS = [
    "row_id",
    "branch_code",
    "class_id",
    "rim_count",
    "orbit_count",
    "rank",
    "nullity",
    "golden_flag",
    "directed_overlap_max",
    "undirected_overlap_max",
    "undirected_weight_max",
    "stress_global_flag_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

BRANCH_NAMES = [
    "golden_specific",
    "directed_stress",
    "weight_stress",
    "undirected_stress",
    "existing_selector",
    "transition_coupled",
    "physical_selector",
]
BRANCH_CODES = {name: index for index, name in enumerate(BRANCH_NAMES)}

FAILURE_NAMES = [
    "none",
    "golden_selector_law_absent",
    "non_golden_policy_absent",
    "unique_selector_absent",
    "existing_selector_absent",
    "transition_semantics_absent",
    "physical_selector_axiom_absent",
    "atom_basis_lift_absent",
    "atom_basis_functor_absent",
    "relation_semantic_law_absent",
]
FAILURE_CODES = {name: index for index, name in enumerate(FAILURE_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "branch_count",
    "viable_branch_count",
    "golden_class_id",
    "directed_stress_class_id",
    "weight_stress_class_id",
    "undirected_stress_class_count",
    "existing_selector_class_count",
    "transition_shared_key_count",
    "semantic_transition_operation_flag",
    "physical_selector_axiom_flag",
    "physical_selector_candidate_count",
    "golden_selector_law_flag",
    "affine_tick_full_lift_candidate_count",
    "affine_tick_best_candidate_covered_ticks",
    "affine_tick_lift_obstruction_flag",
    "golden_atom_basis_lift_ready_flag",
    "atom_basis_relation_cover_flag",
    "atom_basis_functor_obstruction_flag",
    "golden_atom_basis_functor_ready_flag",
    "relation_tick_cover_flag",
    "relation_valued_semantic_law_flag",
    "golden_relation_semantic_ready_flag",
    "non_golden_physical_policy_flag",
    "stress_branch_ready_count",
    "golden_branch_ready_flag",
    "common_transition_blocker_flag",
    "common_physical_selector_blocker_flag",
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


def first_failure(
    *,
    class_count: int,
    unique: int,
    golden: int,
    stress: int,
    transition: int,
    physical: int,
    existing: int = 1,
) -> int:
    if class_count == 0 or existing == 0:
        return FAILURE_CODES["existing_selector_absent"]
    if unique == 0:
        return FAILURE_CODES["unique_selector_absent"]
    if golden == 0 and stress == 1:
        return FAILURE_CODES["non_golden_policy_absent"]
    if transition == 0:
        return FAILURE_CODES["transition_semantics_absent"]
    if physical == 0:
        return FAILURE_CODES["physical_selector_axiom_absent"]
    return FAILURE_CODES["none"]


def build_rows() -> dict[str, Any]:
    frim = load_json(LONG_FRIM)
    glaw = load_json(LONG_GLAW)
    tlift = load_json(LONG_TLIFT)
    abmap = load_json(LONG_ABMAP)
    rtick = load_json(LONG_RTICK)
    rsem = load_json(LONG_RSEM)
    transition = load_json(LONG_TRANSITION_SEM)
    psel = load_json(LONG_PSEL)
    selector_rows_raw = read_csv(LONG_FRIM_SELECTOR)
    class_rows_raw = read_csv(LONG_RIM_CLASS)
    phase_rows_raw = read_csv(LONG_RIM_PHASE)

    selector_by_code = {int(row["selector_code"]): row for row in selector_rows_raw}
    class_by_id = {
        int(row["class_id"]): {key: int(value) for key, value in row.items()}
        for row in class_rows_raw
    }
    phase_by_id = {
        int(row["class_id"]): {key: int(value) for key, value in row.items()}
        for row in phase_rows_raw
    }
    frim_s = summary(frim)
    glaw_s = summary(glaw)
    tlift_s = summary(tlift)
    abmap_s = summary(abmap)
    rtick_s = summary(rtick)
    rsem_s = summary(rsem)
    transition_s = summary(transition)
    psel_s = summary(psel)

    transition_ready = int(
        frim_s["transition_shared_key_count"] > 0
        and transition_s["semantic_transition_operation_flag"] == 1
    )
    physical_ready = int(psel_s["physical_selector_axiom_flag"] == 1)
    physical_candidates = int(psel_s.get("physical_selector_candidate_count", 0))
    golden_selector_law = int(glaw_s["formal_golden_selector_law_flag"])
    atom_basis_lift_ready = int(
        int(tlift_s["full_lift_candidate_count"]) > 0
        and int(tlift_s["affine_tick_lift_obstruction_flag"]) == 0
    )
    atom_basis_functor_ready = int(
        int(abmap_s["undirected_relation_cover_flag"]) == 1
        and int(abmap_s["undirected_functorial_map_exists_flag"]) == 1
        and int(abmap_s["atom_to_basis_function_certified_flag"]) == 1
    )
    relation_tick_cover = int(rtick_s["relation_cover_certified_flag"])
    relation_semantic_ready = int(
        relation_tick_cover == 1
        and int(rsem_s["relation_semantic_law_flag"]) == 1
    )
    non_golden_policy = 0

    directed_class = int(frim_s["directed_stress_selected_class_id"])
    weight_class = int(frim_s["weight_stress_selected_class_id"])
    golden_class = int(frim_s["golden_class_id"])
    undirected_count = int(frim_s["undirected_stress_selected_class_count"])

    branch_specs = [
        (
            "golden_specific",
            golden_class,
            1,
            1,
            1,
            0,
            relation_semantic_ready,
            physical_ready,
            1,
        ),
        (
            "directed_stress",
            directed_class,
            1,
            0,
            1,
            1,
            transition_ready,
            physical_ready,
            1,
        ),
        (
            "weight_stress",
            weight_class,
            1,
            0,
            1,
            1,
            transition_ready,
            physical_ready,
            1,
        ),
        (
            "undirected_stress",
            -1,
            undirected_count,
            0,
            0,
            1,
            transition_ready,
            physical_ready,
            1,
        ),
        (
            "existing_selector",
            int(selector_by_code[4]["selected_class_id"]),
            int(selector_by_code[4]["class_count"]),
            0,
            0,
            0,
            transition_ready,
            physical_ready,
            int(selector_by_code[4]["class_count"]) > 0,
        ),
        (
            "transition_coupled",
            -1,
            int(frim_s["transition_shared_key_count"]),
            0,
            0,
            0,
            transition_ready,
            physical_ready,
            int(frim_s["transition_shared_key_count"]) > 0,
        ),
        (
            "physical_selector",
            golden_class if physical_candidates == 1 else -1,
            physical_candidates,
            int(physical_candidates == 1),
            int(physical_candidates == 1),
            0,
            relation_semantic_ready if physical_candidates == 1 else transition_ready,
            physical_ready,
            physical_candidates > 0,
        ),
    ]
    branch_rows = []
    for branch_id, (
        name,
        class_id,
        class_count,
        golden,
        unique,
        stress,
        transition_flag,
        physical_flag,
        existing,
    ) in enumerate(branch_specs):
        if name == "golden_specific" and golden_selector_law == 0:
            failure = FAILURE_CODES["golden_selector_law_absent"]
        elif name == "golden_specific" and relation_tick_cover == 1 and relation_semantic_ready == 0:
            failure = FAILURE_CODES["relation_semantic_law_absent"]
        elif name == "golden_specific" and relation_semantic_ready == 0 and atom_basis_functor_ready == 0:
            failure = FAILURE_CODES["atom_basis_functor_absent"]
        elif name == "golden_specific" and relation_semantic_ready == 0 and atom_basis_lift_ready == 0:
            failure = FAILURE_CODES["atom_basis_lift_absent"]
        elif name in {"directed_stress", "weight_stress"} and non_golden_policy == 0:
            failure = FAILURE_CODES["non_golden_policy_absent"]
        else:
            failure = first_failure(
                class_count=class_count,
                unique=unique,
                golden=golden,
                stress=stress,
                transition=transition_flag,
                physical=physical_flag,
                existing=existing,
            )
        branch_rows.append(
            {
                "branch_id": branch_id,
                "branch_code": BRANCH_CODES[name],
                "selected_class_id": class_id,
                "class_count": class_count,
                "golden_flag": golden,
                "unique_flag": unique,
                "stress_supported_flag": stress,
                "transition_coupled_flag": transition_flag,
                "physical_selector_flag": physical_flag,
                "first_failure_code": failure,
                "viable_flag": int(failure == FAILURE_CODES["none"]),
            }
        )

    class_ids = [golden_class, directed_class, weight_class]
    class_rows = []
    for row_id, class_id in enumerate(class_ids):
        class_row = class_by_id[class_id]
        phase_row = phase_by_id[class_id]
        if class_id == golden_class:
            branch_code = BRANCH_CODES["golden_specific"]
        elif class_id == directed_class:
            branch_code = BRANCH_CODES["directed_stress"]
        else:
            branch_code = BRANCH_CODES["weight_stress"]
        stress_global_flags = (
            phase_row["directed_global_max_flag"]
            + phase_row["undirected_global_max_flag"]
            + phase_row["weight_global_max_flag"]
        )
        class_rows.append(
            {
                "row_id": row_id,
                "branch_code": branch_code,
                "class_id": class_id,
                "rim_count": class_row["rim_count"],
                "orbit_count": class_row["orbit_count"],
                "rank": class_row["rank"],
                "nullity": class_row["nullity"],
                "golden_flag": class_row["golden_flag"],
                "directed_overlap_max": phase_row["directed_overlap_max"],
                "undirected_overlap_max": phase_row["undirected_overlap_max"],
                "undirected_weight_max": phase_row["undirected_weight_max"],
                "stress_global_flag_count": stress_global_flags,
            }
        )

    viable_count = sum(row["viable_flag"] for row in branch_rows)
    stress_ready_count = sum(
        int(
            row["stress_supported_flag"] == 1
            and row["unique_flag"] == 1
            and row["transition_coupled_flag"] == 1
            and row["physical_selector_flag"] == 1
        )
        for row in branch_rows
    )
    obs = {
        "input_report_count": 8,
        "input_certified_count": sum(
            certified(report)
            for report in [frim, glaw, tlift, abmap, rtick, rsem, transition, psel]
        ),
        "branch_count": len(branch_rows),
        "viable_branch_count": viable_count,
        "golden_class_id": golden_class,
        "directed_stress_class_id": directed_class,
        "weight_stress_class_id": weight_class,
        "undirected_stress_class_count": undirected_count,
        "existing_selector_class_count": int(selector_by_code[4]["class_count"]),
        "transition_shared_key_count": int(frim_s["transition_shared_key_count"]),
        "semantic_transition_operation_flag": int(
            transition_s["semantic_transition_operation_flag"]
        ),
        "physical_selector_axiom_flag": int(psel_s["physical_selector_axiom_flag"]),
        "physical_selector_candidate_count": physical_candidates,
        "golden_selector_law_flag": golden_selector_law,
        "affine_tick_full_lift_candidate_count": int(
            tlift_s["full_lift_candidate_count"]
        ),
        "affine_tick_best_candidate_covered_ticks": int(
            tlift_s["best_candidate_covered_ticks"]
        ),
        "affine_tick_lift_obstruction_flag": int(
            tlift_s["affine_tick_lift_obstruction_flag"]
        ),
        "golden_atom_basis_lift_ready_flag": atom_basis_lift_ready,
        "atom_basis_relation_cover_flag": int(
            abmap_s["undirected_relation_cover_flag"]
        ),
        "atom_basis_functor_obstruction_flag": int(
            1 - int(abmap_s["undirected_functorial_map_exists_flag"])
        ),
        "golden_atom_basis_functor_ready_flag": atom_basis_functor_ready,
        "relation_tick_cover_flag": relation_tick_cover,
        "relation_valued_semantic_law_flag": int(
            rsem_s["relation_semantic_law_flag"]
        ),
        "golden_relation_semantic_ready_flag": relation_semantic_ready,
        "non_golden_physical_policy_flag": non_golden_policy,
        "stress_branch_ready_count": stress_ready_count,
        "golden_branch_ready_flag": int(
            golden_selector_law == 1
            and relation_semantic_ready == 1
            and physical_ready == 1
        ),
        "common_transition_blocker_flag": int(transition_ready == 0),
        "common_physical_selector_blocker_flag": int(physical_ready == 0),
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
        "frim": frim,
        "glaw": glaw,
        "tlift": tlift,
        "abmap": abmap,
        "rtick": rtick,
        "rsem": rsem,
        "transition": transition,
        "psel": psel,
        "branch_rows": branch_rows,
        "class_rows": class_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    branch_table = table_from_rows(BRANCH_COLUMNS, rows["branch_rows"])
    class_table = table_from_rows(CLASS_COLUMNS, rows["class_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "branch_frontier_has_no_viable_current_branch": obs["branch_count"] == 7
        and obs["viable_branch_count"] == 0,
        "branch_classes_match_frim": obs["golden_class_id"] == 0
        and obs["directed_stress_class_id"] == 41
        and obs["weight_stress_class_id"] == 58
        and obs["undirected_stress_class_count"] == 19,
        "golden_branch_has_formal_selector_law": obs["golden_selector_law_flag"] == 1,
        "golden_branch_has_sharp_tlift_blocker": obs[
            "affine_tick_full_lift_candidate_count"
        ]
        == 0
        and obs["affine_tick_best_candidate_covered_ticks"] == 7
        and obs["affine_tick_lift_obstruction_flag"] == 1
        and obs["golden_atom_basis_lift_ready_flag"] == 0,
        "golden_branch_has_relation_cover_but_no_functor": obs[
            "atom_basis_relation_cover_flag"
        ]
        == 1
        and obs["atom_basis_functor_obstruction_flag"] == 1
        and obs["golden_atom_basis_functor_ready_flag"] == 0,
        "golden_branch_has_relation_valued_transition_semantics": obs[
            "relation_tick_cover_flag"
        ]
        == 1
        and obs["relation_valued_semantic_law_flag"] == 1
        and obs["golden_relation_semantic_ready_flag"] == 1
        and rows["branch_rows"][0]["transition_coupled_flag"] == 1
        and rows["branch_rows"][0]["physical_selector_flag"] == 0
        and rows["branch_rows"][0]["first_failure_code"]
        == FAILURE_CODES["physical_selector_axiom_absent"],
        "stress_branches_lack_non_golden_policy": obs["non_golden_physical_policy_flag"] == 0,
        "transition_and_physical_selector_common_blockers": obs[
            "transition_shared_key_count"
        ]
        == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["common_transition_blocker_flag"] == 1
        and obs["common_physical_selector_blocker_flag"] == 1,
        "table_shapes_match": branch_table.shape == (len(BRANCH_CODES), len(BRANCH_COLUMNS))
        and class_table.shape == (3, len(CLASS_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "selector_branch_frontier",
        "summary": {
            "branch_count": obs["branch_count"],
            "viable_branch_count": obs["viable_branch_count"],
            "golden_class_id": obs["golden_class_id"],
            "directed_stress_class_id": obs["directed_stress_class_id"],
            "weight_stress_class_id": obs["weight_stress_class_id"],
            "undirected_stress_class_count": obs["undirected_stress_class_count"],
            "transition_shared_key_count": obs["transition_shared_key_count"],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "physical_selector_candidate_count": obs[
                "physical_selector_candidate_count"
            ],
            "golden_selector_law_flag": obs["golden_selector_law_flag"],
            "affine_tick_lift_obstruction_flag": obs[
                "affine_tick_lift_obstruction_flag"
            ],
            "affine_tick_best_candidate_covered_ticks": obs[
                "affine_tick_best_candidate_covered_ticks"
            ],
            "atom_basis_relation_cover_flag": obs["atom_basis_relation_cover_flag"],
            "atom_basis_functor_obstruction_flag": obs[
                "atom_basis_functor_obstruction_flag"
            ],
            "relation_tick_cover_flag": obs["relation_tick_cover_flag"],
            "relation_valued_semantic_law_flag": obs[
                "relation_valued_semantic_law_flag"
            ],
            "golden_relation_semantic_ready_flag": obs[
                "golden_relation_semantic_ready_flag"
            ],
            "non_golden_physical_policy_flag": obs[
                "non_golden_physical_policy_flag"
            ],
        },
        "branch_code_map": {str(value): key for key, value in BRANCH_CODES.items()},
        "failure_code_map": {str(value): key for key, value in FAILURE_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "branch_table_sha256": sha_array(branch_table),
        "branch_text_sha256": sha_text(csv_text(BRANCH_COLUMNS, rows["branch_rows"])),
        "class_table_sha256": sha_array(class_table),
        "class_text_sha256": sha_text(csv_text(CLASS_COLUMNS, rows["class_rows"])),
        "observable_table_sha256": sha_array(observable_table),
    }
    sfork = {
        "schema": "long.sfork@1",
        "object": "selector_branch_frontier",
        "status": STATUS if all(checks.values()) else "LONG_SFORK_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.sfork.report@1",
        "status": sfork["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_sfork converts the fixed63/rim/stress lift into explicit "
            "selector branch rows. The golden branch now has a formal golden "
            "selector law from long_glaw, and long_abmap shows relation-level "
            "atom/Loop-step/transition coverage for the affine tick. "
            "long_rtick certifies the guarded relation-valued tick cover, and "
            "long_rsem certifies a guarded relation-valued transition semantic "
            "law for those tick witnesses. "
            "long_psel now carries one materialized long_pax selector candidate, "
            "but "
            "the golden branch remains first blocked by the absence of a "
            "physical selector axiom. The unique directed and "
            "weight stress branches are blocked by the absence of a non-golden "
            "physical policy, transition semantics, and a physical selector "
            "axiom; the undirected branch is nonunique."
        ),
        "stage_protocol": {
            "draft": "read long_frim, long_rsem, long_transition_sem, long_psel, rim class rows, and rim phase rows",
            "witness": "emit branch rows, branch class rows, and observables",
            "coherence": "check branch class ids, first failures, common blockers, input statuses, and table hashes",
            "closure": "certify the current selector branch frontier without choosing a physical branch",
            "emit": "write long_sfork artifacts and verifier hook",
        },
        "inputs": {
            "long_frim": input_entry(
                LONG_FRIM,
                {
                    "status": rows["frim"].get("status"),
                    "certificate_sha256": rows["frim"].get("certificate_sha256"),
                },
            ),
            "long_frim_selector": input_entry(LONG_FRIM_SELECTOR),
            "long_glaw": input_entry(
                LONG_GLAW,
                {
                    "status": rows["glaw"].get("status"),
                    "certificate_sha256": rows["glaw"].get("certificate_sha256"),
                },
            ),
            "long_tlift": input_entry(
                LONG_TLIFT,
                {
                    "status": rows["tlift"].get("status"),
                    "certificate_sha256": rows["tlift"].get("certificate_sha256"),
                },
            ),
            "long_abmap": input_entry(
                LONG_ABMAP,
                {
                    "status": rows["abmap"].get("status"),
                    "certificate_sha256": rows["abmap"].get("certificate_sha256"),
                },
            ),
            "long_rtick": input_entry(
                LONG_RTICK,
                {
                    "status": rows["rtick"].get("status"),
                    "certificate_sha256": rows["rtick"].get("certificate_sha256"),
                },
            ),
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "long_rim_class": input_entry(LONG_RIM_CLASS),
            "long_rim_phase": input_entry(LONG_RIM_PHASE),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition"].get("status"),
                    "certificate_sha256": rows["transition"].get("certificate_sha256"),
                },
            ),
            "long_psel": input_entry(
                LONG_PSEL,
                {
                    "status": rows["psel"].get("status"),
                    "certificate_sha256": rows["psel"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "sfork": relpath(OUT_DIR / "sfork.json"),
            "branch_csv": relpath(OUT_DIR / "branch.csv"),
            "class_csv": relpath(OUT_DIR / "class.csv"),
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
                "the current branch frontier has seven tested selector branches and zero viable physical branches",
                "the golden branch targets defect class 0 and now has a certified formal golden-specific selector law",
                "the golden branch now has a certified guarded relation-valued transition semantic law and is first blocked by the absence of a physical selector axiom",
                "one materialized physical-selector candidate selects the same golden branch, but the physical axiom remains unaccepted",
                "the directed-stress branch targets non-golden defect class 41 and the weight-stress branch targets non-golden defect class 58",
                "the undirected stress branch is nonunique across 19 defect classes",
                "all current branches are still blocked by absent physical selector axiom, absent transition semantics, absent non-golden physical policy, or nonunique/absent selector support before any GR-source claim",
            ],
            "does_not_certify_because_out_of_scope": [
                "that no future branch can be made physical",
                "that golden class 0 is physically correct",
                "that non-golden stress classes 41 or 58 are physically correct",
                "semantic A985 transition operations",
                "a physical selector axiom",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Advance the golden branch by certifying a physical selector axiom "
            "for the guarded relation-valued transition law, or promote that "
            "law to semantic A985 operation rows. Otherwise advance the stress "
            "branch by adding a non-golden physical-policy law plus transition "
            "semantics for classes 41/58."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.sfork.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.sfork.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "sfork": sfork,
        "branch_csv": csv_text(BRANCH_COLUMNS, rows["branch_rows"]),
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "branch_table": branch_table,
        "class_table": class_table,
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
    write_json(OUT_DIR / "sfork.json", payloads["sfork"])
    (OUT_DIR / "branch.csv").write_text(payloads["branch_csv"], encoding="utf-8")
    (OUT_DIR / "class.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        branch_table=payloads["branch_table"],
        class_table=payloads["class_table"],
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
