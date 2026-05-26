from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_sector_support_pullback.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_sector_support_pullback"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
SECTOR_REFINEMENT_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_sector_refinement" / "report.json"
)
FOURIER_A985_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_a985_sector_character_candidates" / "report.json"
)
SECTOR_UNIQUE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
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


def freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): freeze_json(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [freeze_json(item) for item in value]
    return value


def profile_key(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: freeze_json(row[field]) for field in fields}


def profile_classes(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = profile_key(row, fields)
        key_hash = sha_json(key)
        grouped.setdefault(key_hash, {"profile_key": key, "coset_indices": []})
        grouped[key_hash]["coset_indices"].append(int(row["coset_index"]))

    out = []
    for class_index, (key_hash, item) in enumerate(
        sorted(grouped.items(), key=lambda pair: (pair[1]["coset_indices"][0], pair[0]))
    ):
        coset_indices = sorted(item["coset_indices"])
        out.append(
            {
                "profile_class_index": class_index,
                "profile_key_sha256": key_hash,
                "class_size": len(coset_indices),
                "coset_indices": coset_indices,
                "profile_key": item["profile_key"],
                "contains_cover_span_coset": 0 in coset_indices,
            }
        )
    return out


def phase_bit(phase: int) -> str:
    if int(phase) == 1:
        return "0"
    if int(phase) == -1:
        return "1"
    raise ValueError(f"phase must be +1 or -1, got {phase}")


def state_phases(state: str) -> dict[str, int]:
    return {
        "screen1_phase": 1 if state[0] == "0" else -1,
        "screen2_phase": 1 if state[1] == "0" else -1,
    }


def candidate_by_id(fourier_a985: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["screen_id"]: row
        for row in fourier_a985["derived"]["candidates"]
    }


def object_state(object_index: int, candidates: dict[str, dict[str, Any]]) -> str:
    label = H6_LABELS[int(object_index)]
    return "".join(
        phase_bit(candidates[screen_id]["object_phase_assignment"][label])
        for screen_id in SCREEN_IDS
    )


def sector_support_pullback_rows(
    sector_unique: dict[str, Any],
    fourier_a985: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = candidate_by_id(fourier_a985)
    sector_rows = sorted(
        sector_unique["derived"]["sector_rows"],
        key=lambda row: int(row["sector"]),
    )
    by_state: dict[str, list[dict[str, Any]]] = {state: [] for state in SCREEN12_STATES}
    sector_state_rows = []
    for row in sector_rows:
        piece_rows = []
        state_counter = Counter()
        for obj, local in row["local_pre_idempotent_keys"]:
            state = object_state(int(obj), candidates)
            piece = {
                "sector": int(row["sector"]),
                "object": int(obj),
                "label": H6_LABELS[int(obj)],
                "local_pre_idempotent": int(local),
                "screen12_state": state,
            }
            piece_rows.append(piece)
            by_state[state].append(piece)
            state_counter[state] += 1

        states = sorted(state_counter)
        sector_state_rows.append(
            {
                "sector": int(row["sector"]),
                "public_zero": bool(row["public_zero"]),
                "block_dimension": int(row["block_dimension"]),
                "active_objects": row["active_objects"],
                "local_pre_idempotent_count": len(piece_rows),
                "screen12_state_set": states,
                "homogeneous_screen12_state": states[0] if len(states) == 1 else None,
                "screen12_state_histogram": histogram(state_counter),
                "local_pre_idempotent_state_rows": sorted(
                    piece_rows,
                    key=lambda item: (item["object"], item["local_pre_idempotent"]),
                ),
            }
        )

    state_cell_rows = []
    for state in SCREEN12_STATES:
        touch_ids = sorted({int(piece["sector"]) for piece in by_state[state]})
        homogeneous_ids = sorted(
            int(row["sector"])
            for row in sector_state_rows
            if row["homogeneous_screen12_state"] == state
        )
        public_zero_ids = sorted(
            int(row["sector"])
            for row in sector_state_rows
            if row["public_zero"] and state in row["screen12_state_set"]
        )
        piece_rows = sorted(
            by_state[state],
            key=lambda item: (
                item["sector"],
                item["object"],
                item["local_pre_idempotent"],
            ),
        )
        cell = {
            "screen12_state": state,
            **state_phases(state),
            "local_pre_idempotent_count": len(piece_rows),
            "sector_touch_count": len(touch_ids),
            "homogeneous_sector_count": len(homogeneous_ids),
            "sector_touch_ids": touch_ids,
            "homogeneous_sector_ids": homogeneous_ids,
            "public_zero_sector_ids": public_zero_ids,
            "local_pre_idempotent_rows": piece_rows,
        }
        cell["state_cell_sha256"] = sha_json({k: v for k, v in cell.items() if k != "state_cell_sha256"})
        state_cell_rows.append(cell)

    return sector_state_rows, state_cell_rows


def recode_transition_histogram(
    transition_histogram: dict[str, int],
    supported_states: set[str],
    state_cell_hash: dict[str, str],
) -> tuple[dict[str, int], dict[str, int], int, int]:
    support_admissible = Counter()
    support_admissible_by_hash = Counter()
    missing = Counter()
    support_admissible_pair_count = 0
    missing_pair_count = 0
    for transition, count in sorted(transition_histogram.items()):
        left, right = transition.split("->")
        count = int(count)
        if left in supported_states and right in supported_states:
            support_admissible[transition] += count
            support_admissible_by_hash[
                f"{state_cell_hash[left]}->{state_cell_hash[right]}"
            ] += count
            support_admissible_pair_count += count
        else:
            missing[transition] += count
            missing_pair_count += count
    return (
        histogram(support_admissible),
        histogram(support_admissible_by_hash),
        missing_pair_count,
        support_admissible_pair_count,
    )


def coset_pullback_rows(
    sector_refinement: dict[str, Any],
    state_cell_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    state_cell_hash = {
        row["screen12_state"]: row["state_cell_sha256"]
        for row in state_cell_rows
    }
    supported_states = {
        row["screen12_state"]
        for row in state_cell_rows
        if int(row["local_pre_idempotent_count"]) > 0
    }
    out = []
    for row in sector_refinement["derived"]["coset_screen_refinement_rows"]:
        transition_histogram = {
            str(key): int(value)
            for key, value in row["pair_screen12_transition_histogram"].items()
        }
        support_hist, support_hash_hist, missing_pair_count, support_pair_count = recode_transition_histogram(
            transition_histogram,
            supported_states,
            state_cell_hash,
        )
        missing_hist = {
            key: value
            for key, value in transition_histogram.items()
            if key not in support_hist
        }
        out.append(
            {
                "coset_index": int(row["coset_index"]),
                "grade_flip_pair_count": int(row["grade_flip_pair_count"]),
                "exact_divisor_fiber_count": int(row["exact_divisor_fiber_count"]),
                "pair_sandpile_class_order_histogram": row[
                    "pair_sandpile_class_order_histogram"
                ],
                "fiber_sandpile_class_order_histogram": row[
                    "fiber_sandpile_class_order_histogram"
                ],
                "support_admissible_pair_count": support_pair_count,
                "missing_state_pair_count": missing_pair_count,
                "support_admissible_state_transition_histogram": support_hist,
                "support_admissible_cell_transition_histogram": support_hash_hist,
                "missing_state_transition_histogram": missing_hist,
            }
        )
    return sorted(out, key=lambda row: int(row["coset_index"]))


def transition_obstruction_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    transition_counter = Counter()
    support_transition_counter = Counter()
    missing_transition_counter = Counter()
    endpoint_state_counter = Counter()
    cosets_with_missing = []
    for row in rows:
        missing_pair_count = int(row["missing_state_pair_count"])
        if missing_pair_count:
            cosets_with_missing.append(int(row["coset_index"]))
        for transition, count in row["support_admissible_state_transition_histogram"].items():
            transition_counter[transition] += int(count)
            support_transition_counter[transition] += int(count)
            left, right = transition.split("->")
            endpoint_state_counter[left] += int(count)
            endpoint_state_counter[right] += int(count)
        for transition, count in row["missing_state_transition_histogram"].items():
            transition_counter[transition] += int(count)
            missing_transition_counter[transition] += int(count)
            left, right = transition.split("->")
            endpoint_state_counter[left] += int(count)
            endpoint_state_counter[right] += int(count)
    return {
        "total_pair_count": int(sum(transition_counter.values())),
        "support_admissible_pair_count": int(sum(support_transition_counter.values())),
        "missing_state_pair_count": int(sum(missing_transition_counter.values())),
        "endpoint_state_multiplicity": histogram(endpoint_state_counter),
        "support_admissible_transition_histogram": histogram(support_transition_counter),
        "missing_state_transition_histogram": histogram(missing_transition_counter),
        "coset_count_using_missing_state": len(cosets_with_missing),
        "cosets_using_missing_state": cosets_with_missing,
    }


def build_theorem() -> dict[str, Any]:
    sector_refinement = load_json(SECTOR_REFINEMENT_REPORT)
    fourier_a985 = load_json(FOURIER_A985_REPORT)
    sector_unique = load_json(SECTOR_UNIQUE_REPORT)

    sector_state_rows, state_cell_rows = sector_support_pullback_rows(
        sector_unique,
        fourier_a985,
    )
    pullback_rows = coset_pullback_rows(sector_refinement, state_cell_rows)
    obstruction = transition_obstruction_summary(pullback_rows)

    supported_states = [
        row["screen12_state"]
        for row in state_cell_rows
        if int(row["local_pre_idempotent_count"]) > 0
    ]
    missing_states = [
        row["screen12_state"]
        for row in state_cell_rows
        if int(row["local_pre_idempotent_count"]) == 0
    ]
    combined_order_fields = [
        "grade_flip_pair_count",
        "exact_divisor_fiber_count",
        "pair_sandpile_class_order_histogram",
        "fiber_sandpile_class_order_histogram",
    ]
    support_pullback_fields = combined_order_fields + [
        "support_admissible_cell_transition_histogram"
    ]
    support_pullback_classes = profile_classes(pullback_rows, support_pullback_fields)

    total_missing_pairs = sum(int(row["missing_state_pair_count"]) for row in pullback_rows)
    total_support_pairs = sum(int(row["support_admissible_pair_count"]) for row in pullback_rows)
    total_pairs = total_missing_pairs + total_support_pairs
    checks = {
        "sector_refinement_source_is_certified": sector_refinement.get("status")
        == "D20_TUBE_SANDPILE_FLIP_SECTOR_REFINEMENT_CERTIFIED"
        and sector_refinement.get("all_checks_pass") is True,
        "fourier_a985_sector_source_is_certified": fourier_a985.get("status")
        == "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        and fourier_a985.get("all_checks_pass") is True,
        "sector_unique_source_is_certified": sector_unique.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and sector_unique.get("all_checks_pass") is True,
        "sector_count_is_39": len(sector_state_rows) == 39,
        "local_pre_idempotent_total_is_109": sum(
            int(row["local_pre_idempotent_count"]) for row in state_cell_rows
        )
        == 109,
        "supported_states_are_00_01_10": supported_states == ["00", "01", "10"],
        "missing_state_is_11": missing_states == ["11"],
        "state_cell_piece_counts_match": {
            row["screen12_state"]: int(row["local_pre_idempotent_count"])
            for row in state_cell_rows
        }
        == {"00": 30, "01": 35, "10": 44, "11": 0},
        "state_cell_touch_counts_match": {
            row["screen12_state"]: int(row["sector_touch_count"])
            for row in state_cell_rows
        }
        == {"00": 23, "01": 27, "10": 32, "11": 0},
        "state_cell_homogeneous_counts_match": {
            row["screen12_state"]: int(row["homogeneous_sector_count"])
            for row in state_cell_rows
        }
        == {"00": 0, "01": 4, "10": 5, "11": 0},
        "sector33_is_in_01_cell": any(
            row["screen12_state"] == "01" and row["public_zero_sector_ids"] == [33]
            for row in state_cell_rows
        ),
        "residue_split_uses_missing_11_state": total_missing_pairs > 0
        and "11" in obstruction["endpoint_state_multiplicity"],
        "missing_state_transition_pair_count_is_420": total_missing_pairs == 420,
        "support_admissible_transition_pair_count_is_865": total_support_pairs == 865,
        "total_transition_pair_count_is_1285": total_pairs == 1285,
        "coset_count_using_missing_state_is_56": obstruction["coset_count_using_missing_state"] == 56,
        "support_pullback_profile_class_count_is_64": len(support_pullback_classes) == 64,
        "support_pullback_profile_size_histogram_is_singletons": histogram(
            Counter(row["class_size"] for row in support_pullback_classes)
        )
        == {"1": 64},
        "support_pullback_partition_covers_64_cosets": sorted(
            idx for row in support_pullback_classes for idx in row["coset_indices"]
        )
        == list(range(64)),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_SECTOR_SUPPORT_PULLBACK_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_SECTOR_SUPPORT_PULLBACK_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_sector_support_pullback",
        "status": status,
        "object": "d20",
        "claim": (
            "The 64-way flip-coset screen split has an explicit 39-sector support "
            "pullback after discarding transitions through the unsupported screen12 "
            "state 11. The total four-state pullback is obstructed because no local "
            "primitive sector piece has screen12 state 11, but the support-admissible "
            "transition profile still separates all 64 cosets."
        ),
        "definition": {
            "sector_support_cell": (
                "For each screen1/screen2 bit state, collect the 39-sector idempotent "
                "rows and local primitive pieces whose signed-object phases realize "
                "that state."
            ),
            "support_admissible_transition": (
                "A grade-flip transition is support-admissible when both endpoint "
                "screen12 states have nonempty local primitive sector support."
            ),
            "scope_boundary": (
                "This certifies a finite support pullback of the screen-transition "
                "profile. It does not build a new central idempotent basis or explain "
                "the unsupported 11 residue state inside the present 39-sector support."
            ),
        },
        "inputs": {
            "tube_sandpile_flip_sector_refinement_report": {
                "path": rel(SECTOR_REFINEMENT_REPORT),
                "sha256": sha_file(SECTOR_REFINEMENT_REPORT),
            },
            "fourier_a985_sector_character_candidates_report": {
                "path": rel(FOURIER_A985_REPORT),
                "sha256": sha_file(FOURIER_A985_REPORT),
            },
            "sector33_unique_public_zero_support_report": {
                "path": rel(SECTOR_UNIQUE_REPORT),
                "sha256": sha_file(SECTOR_UNIQUE_REPORT),
            },
        },
        "derived": {
            "supported_screen12_states": supported_states,
            "missing_screen12_states": missing_states,
            "sector_state_rows_sha256": sha_json(sector_state_rows),
            "sector_state_rows": sector_state_rows,
            "state_cell_rows_sha256": sha_json(state_cell_rows),
            "state_cell_rows": state_cell_rows,
            "transition_obstruction_summary": obstruction,
            "coset_support_pullback_rows_sha256": sha_json(pullback_rows),
            "coset_support_pullback_rows": pullback_rows,
            "support_pullback_profile": {
                "fields": support_pullback_fields,
                "class_count": len(support_pullback_classes),
                "class_size_histogram": histogram(
                    Counter(row["class_size"] for row in support_pullback_classes)
                ),
                "class_rows_sha256": sha_json(support_pullback_classes),
                "class_rows": support_pullback_classes,
            },
        },
        "interpretation": {
            "what_is_certified": (
                "The explicit 39-sector support cells for screen12 states 00, 01, "
                "and 10 are enough to recover a singleton 64-coset profile."
            ),
            "what_is_obstructed": (
                "The residue state 11 appears in 420 grade-flip transitions across "
                "56 cosets, but has zero local primitive pieces in the current "
                "39-sector support data."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify the unsupported screen12=11 residue state: either extend the "
            "sector support model or prove it is purely residue-level data."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_sector_support_pullback_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified screen refinement theorem",
            "load explicit 39-sector idempotent support rows",
            "derive screen1/screen2 support cells from local primitive pieces",
            "record the unsupported screen12=11 obstruction",
            "verify the support-admissible transition profile still splits 64 cosets",
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
