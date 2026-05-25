from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_formal_11_extension_test.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_formal_11_extension_test"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
UNSUPPORTED_STATE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "tube_sandpile_flip_unsupported_state_classification"
    / "report.json"
)
FOURIER_A985_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_a985_sector_character_candidates" / "report.json"
)

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
SCREEN_IDS = ["signed_turn_screen_0", "signed_turn_screen_1", "signed_turn_screen_2"]
SCREEN12_MISSING_STATE = "11"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        schema = index.get("schema", "d20.theorem_registry")
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        schema = "d20.theorem_registry"
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": schema,
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items())}


def phase_bit(phase: int) -> str:
    if int(phase) == 1:
        return "0"
    if int(phase) == -1:
        return "1"
    raise ValueError(f"phase must be +1 or -1, got {phase}")


def candidate_by_id(fourier_a985: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["screen_id"]: row
        for row in fourier_a985["derived"]["candidates"]
    }


def full_object_phase_rows(fourier_a985: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = candidate_by_id(fourier_a985)
    rows = []
    for object_index, label in enumerate(H6_LABELS):
        phases = {
            screen_id: int(candidates[screen_id]["object_phase_assignment"][label])
            for screen_id in SCREEN_IDS
        }
        full_signature = "".join(phase_bit(phases[screen_id]) for screen_id in SCREEN_IDS)
        rows.append(
            {
                "object": object_index,
                "label": label,
                "screen0_phase": phases["signed_turn_screen_0"],
                "screen1_phase": phases["signed_turn_screen_1"],
                "screen2_phase": phases["signed_turn_screen_2"],
                "full_screen_signature": full_signature,
                "screen12_state": full_signature[1:],
            }
        )
    return rows


def scenario_row(
    name: str,
    description: str,
    added_object_labels: int,
    added_local_pre_idempotents: int,
    realizes_nonempty_state11: bool,
    preserves_existing_object_phase_assignments: bool,
    preserves_object_label_count: bool,
    preserves_local_pre_idempotent_total: bool,
    support_is_object_labelled: bool,
    screen0_lift_coverage: list[str],
    fail_reasons: list[str],
) -> dict[str, Any]:
    satisfies_current_constraints = (
        preserves_existing_object_phase_assignments
        and preserves_object_label_count
        and preserves_local_pre_idempotent_total
        and support_is_object_labelled
    )
    return {
        "scenario": name,
        "description": description,
        "added_object_labels": added_object_labels,
        "added_local_pre_idempotents": added_local_pre_idempotents,
        "realizes_nonempty_state11": realizes_nonempty_state11,
        "preserves_existing_object_phase_assignments": preserves_existing_object_phase_assignments,
        "preserves_six_object_label_count": preserves_object_label_count,
        "preserves_109_local_pre_idempotent_total": preserves_local_pre_idempotent_total,
        "support_is_object_labelled": support_is_object_labelled,
        "screen0_lift_coverage": screen0_lift_coverage,
        "satisfies_current_constraints": satisfies_current_constraints,
        "valid_nonempty_extension": satisfies_current_constraints and realizes_nonempty_state11,
        "fail_reasons": fail_reasons,
    }


def formal_extension_scenarios() -> list[dict[str, Any]]:
    return [
        scenario_row(
            name="empty_formal_11_cell",
            description=(
                "Adjoin the missing state as an empty bookkeeping cell."
            ),
            added_object_labels=0,
            added_local_pre_idempotents=0,
            realizes_nonempty_state11=False,
            preserves_existing_object_phase_assignments=True,
            preserves_object_label_count=True,
            preserves_local_pre_idempotent_total=True,
            support_is_object_labelled=True,
            screen0_lift_coverage=[],
            fail_reasons=["empty_cell_has_no_support_and_explains_no_11_transitions"],
        ),
        scenario_row(
            name="relabel_one_existing_piece_as_11",
            description=(
                "Keep the 109-piece total by changing one existing local primitive "
                "piece from its object-derived state to 11."
            ),
            added_object_labels=0,
            added_local_pre_idempotents=0,
            realizes_nonempty_state11=True,
            preserves_existing_object_phase_assignments=False,
            preserves_object_label_count=True,
            preserves_local_pre_idempotent_total=True,
            support_is_object_labelled=True,
            screen0_lift_coverage=[],
            fail_reasons=["changes_the_state_for_an_existing_object_label"],
        ),
        scenario_row(
            name="add_one_unlabelled_11_piece",
            description=(
                "Add one formal state-11 local primitive piece without adding a "
                "signed object label."
            ),
            added_object_labels=0,
            added_local_pre_idempotents=1,
            realizes_nonempty_state11=True,
            preserves_existing_object_phase_assignments=True,
            preserves_object_label_count=True,
            preserves_local_pre_idempotent_total=False,
            support_is_object_labelled=False,
            screen0_lift_coverage=[],
            fail_reasons=[
                "raises_the_109_local_pre_idempotent_total",
                "piece_has_no_signed_object_label",
            ],
        ),
        scenario_row(
            name="add_one_formal_object_011",
            description=(
                "Add one formal object with screen0=0 and screen12=11."
            ),
            added_object_labels=1,
            added_local_pre_idempotents=1,
            realizes_nonempty_state11=True,
            preserves_existing_object_phase_assignments=True,
            preserves_object_label_count=False,
            preserves_local_pre_idempotent_total=False,
            support_is_object_labelled=True,
            screen0_lift_coverage=["011"],
            fail_reasons=[
                "raises_the_six_object_label_count",
                "raises_the_109_local_pre_idempotent_total",
                "covers_only_one_screen0_lift_of_state11",
            ],
        ),
        scenario_row(
            name="add_one_formal_object_111",
            description=(
                "Add one formal object with screen0=1 and screen12=11."
            ),
            added_object_labels=1,
            added_local_pre_idempotents=1,
            realizes_nonempty_state11=True,
            preserves_existing_object_phase_assignments=True,
            preserves_object_label_count=False,
            preserves_local_pre_idempotent_total=False,
            support_is_object_labelled=True,
            screen0_lift_coverage=["111"],
            fail_reasons=[
                "raises_the_six_object_label_count",
                "raises_the_109_local_pre_idempotent_total",
                "covers_only_one_screen0_lift_of_state11",
            ],
        ),
        scenario_row(
            name="add_two_formal_objects_011_111",
            description=(
                "Add two formal objects so both screen0 lifts of screen12=11 are "
                "represented."
            ),
            added_object_labels=2,
            added_local_pre_idempotents=2,
            realizes_nonempty_state11=True,
            preserves_existing_object_phase_assignments=True,
            preserves_object_label_count=False,
            preserves_local_pre_idempotent_total=False,
            support_is_object_labelled=True,
            screen0_lift_coverage=["011", "111"],
            fail_reasons=[
                "raises_the_six_object_label_count",
                "raises_the_109_local_pre_idempotent_total",
            ],
        ),
    ]


def build_theorem() -> dict[str, Any]:
    unsupported = load_json(UNSUPPORTED_STATE_REPORT)
    fourier_a985 = load_json(FOURIER_A985_REPORT)

    object_rows = full_object_phase_rows(fourier_a985)
    full_signature_counts = Counter(row["full_screen_signature"] for row in object_rows)
    screen12_counts = Counter(row["screen12_state"] for row in object_rows)
    object_labels_by_full_signature = {
        signature: [
            row["label"]
            for row in object_rows
            if row["full_screen_signature"] == signature
        ]
        for signature in ["000", "001", "010", "011", "100", "101", "110", "111"]
    }
    object_labels_by_screen12 = {
        state: [
            row["label"]
            for row in object_rows
            if row["screen12_state"] == state
        ]
        for state in ["00", "01", "10", "11"]
    }
    residue_counts = unsupported["derived"]["residue_screen12_counts"]
    support_rows = unsupported["derived"]["sector_support_state_rows"]
    support_counts = {
        row["screen12_state"]: int(row["local_pre_idempotent_count"])
        for row in support_rows
    }
    obstruction = unsupported["derived"]["transition_obstruction_summary"]
    scenarios = formal_extension_scenarios()
    valid_nonempty = [
        row for row in scenarios if row["valid_nonempty_extension"]
    ]
    constraint_preserving = [
        row["scenario"] for row in scenarios if row["satisfies_current_constraints"]
    ]

    checks = {
        "unsupported_state_source_is_certified": unsupported.get("status")
        == "D20_TUBE_SANDPILE_FLIP_UNSUPPORTED_STATE_CLASSIFIED"
        and unsupported.get("all_checks_pass") is True,
        "fourier_a985_sector_source_is_certified": fourier_a985.get("status")
        == "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        and fourier_a985.get("all_checks_pass") is True,
        "six_object_full_signature_counts_match": histogram(full_signature_counts)
        == {"001": 2, "010": 2, "100": 2},
        "six_object_screen12_counts_match": histogram(screen12_counts)
        == {"00": 2, "01": 2, "10": 2},
        "no_object_label_has_011_or_111": object_labels_by_full_signature["011"] == []
        and object_labels_by_full_signature["111"] == [],
        "no_object_label_has_screen12_11": object_labels_by_screen12["11"] == [],
        "residue_has_both_11_screen0_lifts": residue_counts["full_signature_counts"].get("011")
        == 256
        and residue_counts["full_signature_counts"].get("111") == 256,
        "support_has_zero_11_pieces": support_counts == {"00": 30, "01": 35, "10": 44, "11": 0},
        "state11_transition_mass_is_420": int(obstruction["missing_state_pair_count"]) == 420,
        "state11_coset_mass_is_56": int(obstruction["coset_count_using_missing_state"]) == 56,
        "scenario_count_is_6": len(scenarios) == 6,
        "only_empty_scenario_preserves_current_constraints": constraint_preserving == [
            "empty_formal_11_cell"
        ],
        "no_nonempty_scenario_preserves_current_constraints": valid_nonempty == [],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_FORMAL_11_EXTENSION_OBSTRUCTED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_FORMAL_11_EXTENSION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_formal_11_extension_test",
        "status": status,
        "object": "d20",
        "claim": (
            "A nonempty formal support-level realization of screen12=11 is obstructed "
            "by the current finite A985/tube support constraints. The empty cell is "
            "compatible but explains no residue transitions; every nonempty option "
            "requires changing an existing object state, adding an unlabelled piece, "
            "or increasing the six-object/109-piece boundary."
        ),
        "definition": {
            "tested_constraints": (
                "The current support model has six signed object labels and exactly "
                "109 local primitive pieces, each labelled by one of those objects."
            ),
            "formal_11_extension": (
                "A bookkeeping attempt to give the residue-visible screen12=11 state "
                "nonempty support without changing the certified tensor data."
            ),
            "scope_boundary": (
                "This is an obstruction test against current finite support constraints. "
                "It does not construct a new tensor, a new object set, or new sector "
                "idempotents."
            ),
        },
        "inputs": {
            "tube_sandpile_flip_unsupported_state_classification_report": {
                "path": rel(UNSUPPORTED_STATE_REPORT),
                "sha256": sha_file(UNSUPPORTED_STATE_REPORT),
            },
            "fourier_a985_sector_character_candidates_report": {
                "path": rel(FOURIER_A985_REPORT),
                "sha256": sha_file(FOURIER_A985_REPORT),
            },
        },
        "derived": {
            "object_full_phase_rows_sha256": sha_json(object_rows),
            "object_full_phase_rows": object_rows,
            "object_full_signature_counts": histogram(full_signature_counts),
            "object_screen12_counts": histogram(screen12_counts),
            "object_labels_by_full_signature": object_labels_by_full_signature,
            "object_labels_by_screen12": object_labels_by_screen12,
            "residue_state11_screen0_lifts": {
                "011": int(residue_counts["full_signature_counts"]["011"]),
                "111": int(residue_counts["full_signature_counts"]["111"]),
            },
            "state11_transition_obstruction": {
                "missing_state_pair_count": int(obstruction["missing_state_pair_count"]),
                "coset_count_using_missing_state": int(obstruction["coset_count_using_missing_state"]),
                "missing_state_transition_histogram": obstruction[
                    "missing_state_transition_histogram"
                ],
            },
            "formal_extension_scenarios_sha256": sha_json(scenarios),
            "formal_extension_scenarios": scenarios,
            "constraint_preserving_scenarios": constraint_preserving,
            "valid_nonempty_extension_scenarios": valid_nonempty,
        },
        "interpretation": {
            "what_is_certified": (
                "Inside the current finite support model, state 11 cannot be made "
                "nonempty without breaking one of the recorded finite boundaries."
            ),
            "what_remains_open": (
                "A genuine realization would require a new theorem that changes the "
                "object/support model and rechecks the algebraic data, not just a "
                "formal bookkeeping cell."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Either stop the support refinement here as complete for the current "
            "model, or explicitly construct a new extended object/support model and "
            "re-run tensor-level checks."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_formal_11_extension_test_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the unsupported-state classification theorem",
            "compute full screen signatures of the six object labels",
            "verify no object has full signature 011 or 111",
            "enumerate empty, relabel, unlabelled, and formal-object scenarios",
            "verify no nonempty scenario preserves the current support constraints",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
