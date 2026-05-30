from __future__ import annotations

import csv
import hashlib
import json
from itertools import combinations, permutations
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


THEOREM_ID = "long_frim"
STATUS = "LONG_FRIM_F63_RIM_STRESS_LIFT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_F63 = PROOF_ROOT / "long_f63" / "report.json"
LONG_F63_ATOM = PROOF_ROOT / "long_f63" / "atom.csv"
LONG_RIM = PROOF_ROOT / "long_rim" / "report.json"
LONG_RIM_ORBIT = PROOF_ROOT / "long_rim" / "orbit.csv"
LONG_RIM_SELECT = PROOF_ROOT / "long_rim_select" / "report.json"
LONG_RIM_PHASE = PROOF_ROOT / "long_rim_select" / "phase.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_PSEL = PROOF_ROOT / "long_psel" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_frim.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_frim.py"

SPINE_COLUMNS = ["row_id", "structure_code", "value", "pass_flag"]
SELECTOR_COLUMNS = [
    "selector_id",
    "selector_code",
    "class_count",
    "selected_class_id",
    "golden_flag",
    "unique_flag",
    "stress_flag",
    "transition_coupled_flag",
    "physical_selector_flag",
    "obstruction_flag",
]
RIM_COLUMNS = [
    "rim_check_id",
    "orbit_id",
    "class_id",
    "golden_flag",
    "edge_fail_count",
    "complement_fail_count",
    "pass_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

STRUCTURE_NAMES = [
    "grade_three_atom_count",
    "xor_weight_two_pair_count",
    "xor_weight_four_pair_count",
    "xor_weight_six_pair_count",
    "complement_pair_count",
    "s6_coordinate_permutation_count",
    "s6_preserves_grade_three_count",
    "s6_preserves_johnson_count",
    "s6_preserves_complement_count",
    "rim_representative_count",
    "rim_edge_fail_count",
    "rim_complement_fail_count",
]
STRUCTURE_CODES = {name: index for index, name in enumerate(STRUCTURE_NAMES)}

SELECTOR_NAMES = [
    "golden_phase",
    "directed_stress_max",
    "undirected_stress_max",
    "weight_stress_max",
    "existing_phase_selector",
    "transition_coupled_selector",
    "physical_selector",
]
SELECTOR_CODES = {name: index for index, name in enumerate(SELECTOR_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "atom_count",
    "johnson_pair_count",
    "nonedge_pair_count",
    "complement_pair_count",
    "s6_coordinate_permutation_count",
    "s6_preserves_grade_three_count",
    "s6_preserves_johnson_count",
    "s6_preserves_complement_count",
    "rim_orbit_count",
    "rim_edge_fail_count",
    "rim_complement_fail_count",
    "defect_class_count",
    "golden_class_id",
    "directed_stress_selected_class_id",
    "undirected_stress_selected_class_count",
    "weight_stress_selected_class_id",
    "golden_selected_by_stress_flag",
    "stress_unique_selector_count",
    "stress_selector_count",
    "transition_shared_key_count",
    "semantic_transition_operation_flag",
    "physical_selector_axiom_flag",
    "physical_selector_candidate_count",
    "coordinate_spine_rim_lift_flag",
    "physical_rim_selector_flag",
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


def permute_mask(mask: int, perm: tuple[int, ...]) -> int:
    out = 0
    for source, target in enumerate(perm):
        if (mask >> source) & 1:
            out |= 1 << target
    return out


def build_rows() -> dict[str, Any]:
    f63 = load_json(LONG_F63)
    rim = load_json(LONG_RIM)
    rim_select = load_json(LONG_RIM_SELECT)
    transition = load_json(LONG_TRANSITION_SEM)
    psel = load_json(LONG_PSEL)
    atom_rows_raw = read_csv(LONG_F63_ATOM)
    orbit_rows_raw = read_csv(LONG_RIM_ORBIT)
    phase_rows_raw = read_csv(LONG_RIM_PHASE)

    atom_coord = {
        int(row["atom_id"]): int(row["coordinate_mask"]) for row in atom_rows_raw
    }
    coord_atoms = set(atom_coord.values())
    pair_counts = {2: 0, 4: 0, 6: 0}
    for left, right in combinations(sorted(atom_coord), 2):
        weight = (atom_coord[left] ^ atom_coord[right]).bit_count()
        pair_counts[weight] += 1

    s6_total = 0
    s6_grade = 0
    s6_johnson = 0
    s6_complement = 0
    johnson_pairs = {
        frozenset((left, right))
        for left, right in combinations(sorted(atom_coord), 2)
        if (atom_coord[left] ^ atom_coord[right]).bit_count() == 2
    }
    complement_pairs = {
        frozenset((left, right))
        for left, right in combinations(sorted(atom_coord), 2)
        if (atom_coord[left] ^ atom_coord[right]).bit_count() == 6
    }
    coord_to_atom = {coord: atom for atom, coord in atom_coord.items()}
    for perm in permutations(range(6)):
        s6_total += 1
        mapped_coords = {permute_mask(coord, perm) for coord in coord_atoms}
        if mapped_coords == coord_atoms:
            s6_grade += 1
        mapped_atom = {
            atom: coord_to_atom[permute_mask(coord, perm)]
            for atom, coord in atom_coord.items()
        }
        mapped_johnson = {
            frozenset((mapped_atom[left], mapped_atom[right]))
            for left, right in (tuple(pair) for pair in johnson_pairs)
        }
        if mapped_johnson == johnson_pairs:
            s6_johnson += 1
        mapped_complement = {
            frozenset((mapped_atom[left], mapped_atom[right]))
            for left, right in (tuple(pair) for pair in complement_pairs)
        }
        if mapped_complement == complement_pairs:
            s6_complement += 1

    rim_rows = []
    rim_edge_fail_total = 0
    rim_complement_fail_total = 0
    for check_id, row in enumerate(orbit_rows_raw):
        rim_atoms = [int(value) for value in row["representative_rim"].split("|")]
        edge_fail = 0
        complement_fail = 0
        for index, atom in enumerate(rim_atoms):
            right = rim_atoms[(index + 1) % len(rim_atoms)]
            if (atom_coord[atom] ^ atom_coord[right]).bit_count() != 2:
                edge_fail += 1
        for index in range(10):
            if (atom_coord[rim_atoms[index]] ^ atom_coord[rim_atoms[index + 10]]).bit_count() != 6:
                complement_fail += 1
        rim_edge_fail_total += edge_fail
        rim_complement_fail_total += complement_fail
        rim_rows.append(
            {
                "rim_check_id": check_id,
                "orbit_id": int(row["orbit_id"]),
                "class_id": int(row["class_id"]),
                "golden_flag": int(row["golden_flag"]),
                "edge_fail_count": edge_fail,
                "complement_fail_count": complement_fail,
                "pass_flag": int(edge_fail == 0 and complement_fail == 0),
            }
        )

    phase_rows = [
        {key: int(value) for key, value in row.items()} for row in phase_rows_raw
    ]
    golden_classes = [row["class_id"] for row in phase_rows if row["golden_flag"]]
    directed_classes = [
        row["class_id"] for row in phase_rows if row["directed_global_max_flag"]
    ]
    undirected_classes = [
        row["class_id"] for row in phase_rows if row["undirected_global_max_flag"]
    ]
    weight_classes = [
        row["class_id"] for row in phase_rows if row["weight_global_max_flag"]
    ]
    existing_classes = [
        row["class_id"] for row in phase_rows if row["existing_selector_flag"]
    ]
    transition_s = summary(transition)
    rim_select_s = summary(rim_select)
    psel_s = summary(psel)

    golden_selected_by_stress = int(
        any(class_id in golden_classes for class_id in directed_classes)
        or any(class_id in golden_classes for class_id in undirected_classes)
        or any(class_id in golden_classes for class_id in weight_classes)
    )
    stress_unique_count = int(len(directed_classes) == 1) + int(len(weight_classes) == 1)
    transition_shared = int(rim_select_s["stress_transition_shared_key_count"])
    semantic_transition = int(transition_s["semantic_transition_operation_flag"])
    physical_axiom = int(psel_s["physical_selector_axiom_flag"])
    physical_candidates = int(psel_s.get("physical_selector_candidate_count", 0))

    selector_rows = [
        {
            "selector_id": 0,
            "selector_code": SELECTOR_CODES["golden_phase"],
            "class_count": len(golden_classes),
            "selected_class_id": golden_classes[0] if len(golden_classes) == 1 else -1,
            "golden_flag": 1,
            "unique_flag": int(len(golden_classes) == 1),
            "stress_flag": 0,
            "transition_coupled_flag": 0,
            "physical_selector_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "selector_id": 1,
            "selector_code": SELECTOR_CODES["directed_stress_max"],
            "class_count": len(directed_classes),
            "selected_class_id": directed_classes[0] if len(directed_classes) == 1 else -1,
            "golden_flag": int(any(item in golden_classes for item in directed_classes)),
            "unique_flag": int(len(directed_classes) == 1),
            "stress_flag": 1,
            "transition_coupled_flag": int(transition_shared > 0 and semantic_transition == 1),
            "physical_selector_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "selector_id": 2,
            "selector_code": SELECTOR_CODES["undirected_stress_max"],
            "class_count": len(undirected_classes),
            "selected_class_id": undirected_classes[0] if len(undirected_classes) == 1 else -1,
            "golden_flag": int(any(item in golden_classes for item in undirected_classes)),
            "unique_flag": int(len(undirected_classes) == 1),
            "stress_flag": 1,
            "transition_coupled_flag": int(transition_shared > 0 and semantic_transition == 1),
            "physical_selector_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "selector_id": 3,
            "selector_code": SELECTOR_CODES["weight_stress_max"],
            "class_count": len(weight_classes),
            "selected_class_id": weight_classes[0] if len(weight_classes) == 1 else -1,
            "golden_flag": int(any(item in golden_classes for item in weight_classes)),
            "unique_flag": int(len(weight_classes) == 1),
            "stress_flag": 1,
            "transition_coupled_flag": int(transition_shared > 0 and semantic_transition == 1),
            "physical_selector_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "selector_id": 4,
            "selector_code": SELECTOR_CODES["existing_phase_selector"],
            "class_count": len(existing_classes),
            "selected_class_id": existing_classes[0] if len(existing_classes) == 1 else -1,
            "golden_flag": int(any(item in golden_classes for item in existing_classes)),
            "unique_flag": int(len(existing_classes) == 1),
            "stress_flag": 0,
            "transition_coupled_flag": 0,
            "physical_selector_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "selector_id": 5,
            "selector_code": SELECTOR_CODES["transition_coupled_selector"],
            "class_count": transition_shared,
            "selected_class_id": -1,
            "golden_flag": 0,
            "unique_flag": 0,
            "stress_flag": 0,
            "transition_coupled_flag": int(transition_shared > 0 and semantic_transition == 1),
            "physical_selector_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "selector_id": 6,
            "selector_code": SELECTOR_CODES["physical_selector"],
            "class_count": physical_candidates,
            "selected_class_id": -1,
            "golden_flag": 0,
            "unique_flag": 0,
            "stress_flag": 0,
            "transition_coupled_flag": 0,
            "physical_selector_flag": physical_axiom,
            "obstruction_flag": 1,
        },
    ]

    structure_values = {
        "grade_three_atom_count": len(atom_coord),
        "xor_weight_two_pair_count": pair_counts[2],
        "xor_weight_four_pair_count": pair_counts[4],
        "xor_weight_six_pair_count": pair_counts[6],
        "complement_pair_count": len(complement_pairs),
        "s6_coordinate_permutation_count": s6_total,
        "s6_preserves_grade_three_count": s6_grade,
        "s6_preserves_johnson_count": s6_johnson,
        "s6_preserves_complement_count": s6_complement,
        "rim_representative_count": len(rim_rows),
        "rim_edge_fail_count": rim_edge_fail_total,
        "rim_complement_fail_count": rim_complement_fail_total,
    }
    structure_expected = {
        "grade_three_atom_count": 20,
        "xor_weight_two_pair_count": 90,
        "xor_weight_four_pair_count": 90,
        "xor_weight_six_pair_count": 10,
        "complement_pair_count": 10,
        "s6_coordinate_permutation_count": 720,
        "s6_preserves_grade_three_count": 720,
        "s6_preserves_johnson_count": 720,
        "s6_preserves_complement_count": 720,
        "rim_representative_count": 124,
        "rim_edge_fail_count": 0,
        "rim_complement_fail_count": 0,
    }
    spine_rows = [
        {
            "row_id": index,
            "structure_code": STRUCTURE_CODES[name],
            "value": structure_values[name],
            "pass_flag": int(structure_values[name] == structure_expected[name]),
        }
        for index, name in enumerate(STRUCTURE_NAMES)
    ]

    physical_rim_selector = int(
        physical_axiom == 1
        and transition_shared > 0
        and semantic_transition == 1
        and golden_selected_by_stress == 1
    )
    obs = {
        "input_report_count": 5,
        "input_certified_count": sum(
            certified(report) for report in [f63, rim, rim_select, transition, psel]
        ),
        "atom_count": len(atom_coord),
        "johnson_pair_count": pair_counts[2],
        "nonedge_pair_count": pair_counts[4],
        "complement_pair_count": pair_counts[6],
        "s6_coordinate_permutation_count": s6_total,
        "s6_preserves_grade_three_count": s6_grade,
        "s6_preserves_johnson_count": s6_johnson,
        "s6_preserves_complement_count": s6_complement,
        "rim_orbit_count": len(rim_rows),
        "rim_edge_fail_count": rim_edge_fail_total,
        "rim_complement_fail_count": rim_complement_fail_total,
        "defect_class_count": len(phase_rows),
        "golden_class_id": golden_classes[0],
        "directed_stress_selected_class_id": directed_classes[0]
        if len(directed_classes) == 1
        else -1,
        "undirected_stress_selected_class_count": len(undirected_classes),
        "weight_stress_selected_class_id": weight_classes[0] if len(weight_classes) == 1 else -1,
        "golden_selected_by_stress_flag": golden_selected_by_stress,
        "stress_unique_selector_count": stress_unique_count,
        "stress_selector_count": 3,
        "transition_shared_key_count": transition_shared,
        "semantic_transition_operation_flag": semantic_transition,
        "physical_selector_axiom_flag": physical_axiom,
        "physical_selector_candidate_count": physical_candidates,
        "coordinate_spine_rim_lift_flag": int(
            rim_edge_fail_total == 0 and rim_complement_fail_total == 0
        ),
        "physical_rim_selector_flag": physical_rim_selector,
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
        "f63": f63,
        "rim": rim,
        "rim_select": rim_select,
        "transition": transition,
        "psel": psel,
        "spine_rows": spine_rows,
        "selector_rows": selector_rows,
        "rim_rows": rim_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "directed_classes": directed_classes,
        "undirected_classes": undirected_classes,
        "weight_classes": weight_classes,
        "golden_classes": golden_classes,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    spine_table = table_from_rows(SPINE_COLUMNS, rows["spine_rows"])
    selector_table = table_from_rows(SELECTOR_COLUMNS, rows["selector_rows"])
    rim_table = table_from_rows(RIM_COLUMNS, rows["rim_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "f63_spine_reproduces_johnson_geometry": obs["atom_count"] == 20
        and obs["johnson_pair_count"] == 90
        and obs["nonedge_pair_count"] == 90
        and obs["complement_pair_count"] == 10,
        "s6_coordinate_permutations_preserve_spine_geometry": obs[
            "s6_coordinate_permutation_count"
        ]
        == 720
        and obs["s6_preserves_grade_three_count"] == 720
        and obs["s6_preserves_johnson_count"] == 720
        and obs["s6_preserves_complement_count"] == 720,
        "rim_representatives_lift_to_f63_c20_cycles": obs["rim_orbit_count"] == 124
        and obs["rim_edge_fail_count"] == 0
        and obs["rim_complement_fail_count"] == 0
        and obs["coordinate_spine_rim_lift_flag"] == 1,
        "stress_phase_selectors_are_non_golden": obs["golden_class_id"] == 0
        and obs["directed_stress_selected_class_id"] == 41
        and obs["weight_stress_selected_class_id"] == 58
        and obs["golden_selected_by_stress_flag"] == 0,
        "undirected_stress_selector_is_nonunique": obs[
            "undirected_stress_selected_class_count"
        ]
        == 19,
        "transition_and_physical_selector_still_blocked": obs["transition_shared_key_count"] == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["physical_rim_selector_flag"] == 0,
        "table_shapes_match": spine_table.shape == (len(STRUCTURE_CODES), len(SPINE_COLUMNS))
        and selector_table.shape == (len(SELECTOR_CODES), len(SELECTOR_COLUMNS))
        and rim_table.shape == (124, len(RIM_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "f63_rim_stress_lift_obstruction",
        "summary": {
            "atom_count": obs["atom_count"],
            "johnson_pair_count": obs["johnson_pair_count"],
            "complement_pair_count": obs["complement_pair_count"],
            "s6_coordinate_permutation_count": obs["s6_coordinate_permutation_count"],
            "rim_orbit_count": obs["rim_orbit_count"],
            "defect_class_count": obs["defect_class_count"],
            "golden_class_id": obs["golden_class_id"],
            "directed_stress_selected_class_id": obs[
                "directed_stress_selected_class_id"
            ],
            "undirected_stress_selected_class_count": obs[
                "undirected_stress_selected_class_count"
            ],
            "weight_stress_selected_class_id": obs["weight_stress_selected_class_id"],
            "golden_selected_by_stress_flag": obs["golden_selected_by_stress_flag"],
            "transition_shared_key_count": obs["transition_shared_key_count"],
            "semantic_transition_operation_flag": obs["semantic_transition_operation_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "physical_rim_selector_flag": obs["physical_rim_selector_flag"],
        },
        "structure_code_map": {
            str(value): key for key, value in STRUCTURE_CODES.items()
        },
        "selector_code_map": {str(value): key for key, value in SELECTOR_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "directed_stress_classes": rows["directed_classes"],
        "undirected_stress_classes": rows["undirected_classes"],
        "weight_stress_classes": rows["weight_classes"],
        "golden_classes": rows["golden_classes"],
        "spine_table_sha256": sha_array(spine_table),
        "spine_text_sha256": sha_text(csv_text(SPINE_COLUMNS, rows["spine_rows"])),
        "selector_table_sha256": sha_array(selector_table),
        "selector_text_sha256": sha_text(
            csv_text(SELECTOR_COLUMNS, rows["selector_rows"])
        ),
        "rim_table_sha256": sha_array(rim_table),
        "rim_text_sha256": sha_text(csv_text(RIM_COLUMNS, rows["rim_rows"])),
        "observable_table_sha256": sha_array(observable_table),
    }
    frim = {
        "schema": "long.frim@1",
        "object": "f63_rim_stress_lift_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_FRIM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.frim.report@1",
        "status": frim["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_frim lifts the rim and stress-selection question onto the "
            "certified fixed63 F2^6 exterior spine. The spine canonically "
            "reproduces J(6,3), complement pairs, and all representative C20 "
            "rim cycles. Stress-overlap maxima define finite phase candidates, "
            "but they are non-golden or nonunique and remain uncoupled from "
            "semantic transition data."
        ),
        "stage_protocol": {
            "draft": "read long_f63, long_rim, long_rim_select, long_transition_sem, and long_psel",
            "witness": "emit spine invariants, rim representative checks, selector candidates, and observables",
            "coherence": "check F2^6 Johnson geometry, S6 preservation, C20 rim lift, stress selector classes, transition obstruction, and table hashes",
            "closure": "certify the F2^6 rim lift and the current stress/transition selector obstruction",
            "emit": "write long_frim artifacts and verifier hook",
        },
        "inputs": {
            "long_f63": input_entry(
                LONG_F63,
                {
                    "status": rows["f63"].get("status"),
                    "certificate_sha256": rows["f63"].get("certificate_sha256"),
                },
            ),
            "long_f63_atom": input_entry(LONG_F63_ATOM),
            "long_rim": input_entry(
                LONG_RIM,
                {
                    "status": rows["rim"].get("status"),
                    "certificate_sha256": rows["rim"].get("certificate_sha256"),
                },
            ),
            "long_rim_orbit": input_entry(LONG_RIM_ORBIT),
            "long_rim_select": input_entry(
                LONG_RIM_SELECT,
                {
                    "status": rows["rim_select"].get("status"),
                    "certificate_sha256": rows["rim_select"].get("certificate_sha256"),
                },
            ),
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
            "frim": relpath(OUT_DIR / "frim.json"),
            "spine_csv": relpath(OUT_DIR / "spine.csv"),
            "selector_csv": relpath(OUT_DIR / "selector.csv"),
            "rim_csv": relpath(OUT_DIR / "rim.csv"),
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
                "the fixed63 grade-three spine reproduces the 20-atom J(6,3) geometry with 90 Johnson pairs and 10 complement pairs",
                "all 720 coordinate permutations preserve the grade-three atom set, Johnson edges, and complement pairs",
                "all 124 representative complement-antipodal C20 rim orbits lift to valid cycles in the fixed63 exterior spine",
                "directed and weight stress-overlap maxima select non-golden defect classes 41 and 58 respectively",
                "the undirected stress-overlap maximum is nonunique across 19 defect classes",
                "no stress-selected rim phase is currently coupled to semantic transition operations or a physical selector axiom",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the deterministic F2^6 basis is the unique physical H6 basis",
                "that the golden rim phase is physically required",
                "that a non-golden stress-selected phase is physically valid",
                "semantic A985 transition operations",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Decide the stress selector branch: either promote the non-golden "
            "directed/weight stress classes into a new physical rim candidate "
            "with transition semantics, or add a golden-specific selector law "
            "that is independent of the current stress maxima."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.frim.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.frim.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "frim": frim,
        "spine_csv": csv_text(SPINE_COLUMNS, rows["spine_rows"]),
        "selector_csv": csv_text(SELECTOR_COLUMNS, rows["selector_rows"]),
        "rim_csv": csv_text(RIM_COLUMNS, rows["rim_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "spine_table": spine_table,
        "selector_table": selector_table,
        "rim_table": rim_table,
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
    write_json(OUT_DIR / "frim.json", payloads["frim"])
    (OUT_DIR / "spine.csv").write_text(payloads["spine_csv"], encoding="utf-8")
    (OUT_DIR / "selector.csv").write_text(payloads["selector_csv"], encoding="utf-8")
    (OUT_DIR / "rim.csv").write_text(payloads["rim_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        spine_table=payloads["spine_table"],
        selector_table=payloads["selector_table"],
        rim_table=payloads["rim_table"],
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
