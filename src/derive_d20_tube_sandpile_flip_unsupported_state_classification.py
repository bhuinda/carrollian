from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_unsupported_state_classification.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_unsupported_state_classification"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
SUPPORT_PULLBACK_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_sector_support_pullback" / "report.json"
)
FOURIER_RESIDUE_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_residue_screen" / "report.json"
)
FOURIER_A985_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_a985_sector_character_candidates" / "report.json"
)

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
SCREEN_IDS = ["signed_turn_screen_1", "signed_turn_screen_2"]
SCREEN12_STATES = ["00", "01", "10", "11"]


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


def object_phase_rows(fourier_a985: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = candidate_by_id(fourier_a985)
    rows = []
    for object_index, label in enumerate(H6_LABELS):
        screen1_phase = int(candidates[SCREEN_IDS[0]]["object_phase_assignment"][label])
        screen2_phase = int(candidates[SCREEN_IDS[1]]["object_phase_assignment"][label])
        state = phase_bit(screen1_phase) + phase_bit(screen2_phase)
        rows.append(
            {
                "object": object_index,
                "label": label,
                "screen1_phase": screen1_phase,
                "screen2_phase": screen2_phase,
                "screen12_state": state,
            }
        )
    return rows


def residue_screen12_counts(fourier_residue: dict[str, Any]) -> dict[str, Any]:
    full_counts = {
        str(key): int(value)
        for key, value in fourier_residue["derived"]["combined_screen"][
            "cell_counts_by_signature"
        ].items()
    }
    screen12_counts = Counter()
    screen0_by_screen12: dict[str, Counter[str]] = defaultdict(Counter)
    for signature, count in sorted(full_counts.items()):
        screen0 = signature[0]
        screen12 = signature[1:]
        screen12_counts[screen12] += int(count)
        screen0_by_screen12[screen12][screen0] += int(count)
    return {
        "full_signature_counts": dict(sorted(full_counts.items())),
        "screen12_counts": histogram(screen12_counts),
        "screen0_split_by_screen12": {
            key: histogram(value)
            for key, value in sorted(screen0_by_screen12.items())
        },
    }


def state_support_rows(support_pullback: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in support_pullback["derived"]["state_cell_rows"]:
        label_counts = Counter(
            piece["label"] for piece in row["local_pre_idempotent_rows"]
        )
        rows.append(
            {
                "screen12_state": row["screen12_state"],
                "screen1_phase": int(row["screen1_phase"]),
                "screen2_phase": int(row["screen2_phase"]),
                "local_pre_idempotent_count": int(row["local_pre_idempotent_count"]),
                "sector_touch_count": int(row["sector_touch_count"]),
                "homogeneous_sector_count": int(row["homogeneous_sector_count"]),
                "object_label_counts": histogram(label_counts),
                "sector_touch_ids": row["sector_touch_ids"],
                "homogeneous_sector_ids": row["homogeneous_sector_ids"],
                "public_zero_sector_ids": row["public_zero_sector_ids"],
                "state_cell_sha256": row["state_cell_sha256"],
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    support_pullback = load_json(SUPPORT_PULLBACK_REPORT)
    fourier_residue = load_json(FOURIER_RESIDUE_REPORT)
    fourier_a985 = load_json(FOURIER_A985_REPORT)

    object_rows = object_phase_rows(fourier_a985)
    object_state_counts = Counter(row["screen12_state"] for row in object_rows)
    object_labels_by_state = {
        state: [
            row["label"]
            for row in object_rows
            if row["screen12_state"] == state
        ]
        for state in SCREEN12_STATES
    }
    residue_counts = residue_screen12_counts(fourier_residue)
    support_rows = state_support_rows(support_pullback)
    support_counts = {
        row["screen12_state"]: int(row["local_pre_idempotent_count"])
        for row in support_rows
    }
    support_touch_counts = {
        row["screen12_state"]: int(row["sector_touch_count"])
        for row in support_rows
    }
    obstruction = support_pullback["derived"]["transition_obstruction_summary"]
    supported_object_states = [
        state for state in SCREEN12_STATES if object_state_counts[state] > 0
    ]
    supported_sector_states = support_pullback["derived"]["supported_screen12_states"]
    missing_object_states = [
        state for state in SCREEN12_STATES if object_state_counts[state] == 0
    ]
    missing_sector_states = support_pullback["derived"]["missing_screen12_states"]

    classification = {
        "unsupported_state": "11",
        "classification": "residue_visible_but_outside_current_object_phase_image",
        "reason": (
            "The residue screen12 map has all four states, but the six signed "
            "object labels realize only 00, 01, and 10. Since the 39-sector "
            "support rows are assembled from local primitive pieces labelled by "
            "those six objects, state 11 has no local primitive sector support "
            "inside the current model."
        ),
        "minimum_extension_needed": (
            "Any support-level realization of state 11 would require at least one "
            "new primitive piece or object-phase label with screen1_phase=-1 and "
            "screen2_phase=-1, or a different non-support construction."
        ),
    }

    checks = {
        "support_pullback_source_is_certified": support_pullback.get("status")
        == "D20_TUBE_SANDPILE_FLIP_SECTOR_SUPPORT_PULLBACK_CERTIFIED"
        and support_pullback.get("all_checks_pass") is True,
        "fourier_residue_source_is_certified": fourier_residue.get("status")
        == "D20_FOURIER_RESIDUE_SCREEN_CERTIFIED"
        and fourier_residue.get("all_checks_pass") is True,
        "fourier_a985_sector_source_is_certified": fourier_a985.get("status")
        == "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        and fourier_a985.get("all_checks_pass") is True,
        "object_state_counts_match": histogram(object_state_counts)
        == {"00": 2, "01": 2, "10": 2},
        "object_state_11_is_absent": object_labels_by_state["11"] == [],
        "support_state_counts_match": support_counts
        == {"00": 30, "01": 35, "10": 44, "11": 0},
        "support_touch_counts_match": support_touch_counts
        == {"00": 23, "01": 27, "10": 32, "11": 0},
        "residue_screen12_has_four_equal_cells": residue_counts["screen12_counts"]
        == {"00": 512, "01": 512, "10": 512, "11": 512},
        "residue_screen0_splits_each_screen12_cell_256_256": all(
            split == {"0": 256, "1": 256}
            for split in residue_counts["screen0_split_by_screen12"].values()
        ),
        "supported_object_states_match_sector_states": supported_object_states
        == supported_sector_states
        == ["00", "01", "10"],
        "missing_object_states_match_sector_states": missing_object_states
        == missing_sector_states
        == ["11"],
        "unsupported_state_has_residue_mass": int(
            residue_counts["screen12_counts"]["11"]
        )
        == 512,
        "unsupported_state_has_transition_mass": int(
            obstruction["missing_state_pair_count"]
        )
        == 420,
        "unsupported_state_hits_56_cosets": int(
            obstruction["coset_count_using_missing_state"]
        )
        == 56,
        "support_admissible_profile_still_splits_64_cosets": int(
            support_pullback["derived"]["support_pullback_profile"]["class_count"]
        )
        == 64
        and support_pullback["derived"]["support_pullback_profile"]["class_size_histogram"]
        == {"1": 64},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_UNSUPPORTED_STATE_CLASSIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_UNSUPPORTED_STATE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_unsupported_state_classification",
        "status": status,
        "object": "d20",
        "claim": (
            "The unsupported screen12=11 state is residue-visible but outside the "
            "current A985/tube six-object phase image. The full residue cube has "
            "512 masks in screen12=11, and grade-flip data uses that state, but "
            "no signed object label or local primitive sector piece realizes it."
        ),
        "definition": {
            "screen12_state": (
                "The two-bit value formed from signed_turn_screen_1 and "
                "signed_turn_screen_2, using 0 for phase +1 and 1 for phase -1."
            ),
            "object_phase_image": (
                "The set of screen12 states realized by the six object labels "
                "B-, B+, V-, V+, S-, S+ in the certified A985/tube phase tests."
            ),
            "classification_boundary": (
                "The classification is relative to the current support-level "
                "A985/tube model. It does not prove that no larger or different "
                "construction can realize the missing state."
            ),
        },
        "inputs": {
            "tube_sandpile_flip_sector_support_pullback_report": {
                "path": rel(SUPPORT_PULLBACK_REPORT),
                "sha256": sha_file(SUPPORT_PULLBACK_REPORT),
            },
            "fourier_residue_screen_report": {
                "path": rel(FOURIER_RESIDUE_REPORT),
                "sha256": sha_file(FOURIER_RESIDUE_REPORT),
            },
            "fourier_a985_sector_character_candidates_report": {
                "path": rel(FOURIER_A985_REPORT),
                "sha256": sha_file(FOURIER_A985_REPORT),
            },
        },
        "derived": {
            "classification": classification,
            "object_phase_rows_sha256": sha_json(object_rows),
            "object_phase_rows": object_rows,
            "object_state_counts": histogram(object_state_counts),
            "object_labels_by_state": object_labels_by_state,
            "residue_screen12_counts": residue_counts,
            "sector_support_state_rows_sha256": sha_json(support_rows),
            "sector_support_state_rows": support_rows,
            "transition_obstruction_summary": obstruction,
            "support_pullback_profile_summary": {
                key: value
                for key, value in support_pullback["derived"]["support_pullback_profile"].items()
                if key != "class_rows"
            },
        },
        "interpretation": {
            "what_is_certified": (
                "State 11 is not lost in the residue calculation; it is absent "
                "from the object-labelled support side before sector aggregation."
            ),
            "what_remains_open": (
                "Whether state 11 should be modeled by extending the support data "
                "or treated as purely residue-level data remains a separate theorem."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Test whether adding a formal screen12=11 support cell preserves the "
            "finite algebra checks or immediately violates existing object-phase "
            "constraints."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_unsupported_state_classification_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified sector-support pullback theorem",
            "compare screen12 states realized by the residue cube",
            "compare screen12 states realized by the six object phase labels",
            "verify state 11 has residue mass but no local primitive support",
            "record the finite extension boundary for state 11",
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
