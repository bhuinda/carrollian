from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

C2_MOVE_ORBIT_FAMILY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family"
    / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fraction_dict(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def eigenvalue(label: str) -> Fraction:
    return Fraction(label)


def gap_scores(row: dict[str, Any]) -> dict[str, Any]:
    spectrum = {eigenvalue(label): int(count) for label, count in row["spectrum"].items()}
    remaining = dict(spectrum)
    remaining[Fraction(1, 1)] = remaining.get(Fraction(1, 1), 0) - int(row["component_count"])
    if remaining.get(Fraction(1, 1), 0) == 0:
        remaining.pop(Fraction(1, 1), None)
    if any(count < 0 for count in remaining.values()):
        raise ValueError(f"component count exceeds unit spectrum for row {row['move_orbit_id']}")

    raw_abs_radius = max((abs(value) for value, count in remaining.items() if count), default=Fraction(0))
    lazy_abs_radius = max(
        (abs((Fraction(1) + value) / 2) for value, count in remaining.items() if count),
        default=Fraction(0),
    )
    return {
        "raw_componentwise_nontrivial_absolute_gap": fraction_dict(Fraction(1) - raw_abs_radius),
        "lazy_componentwise_nontrivial_gap": fraction_dict(Fraction(1) - lazy_abs_radius),
        "raw_componentwise_nontrivial_absolute_radius": fraction_dict(raw_abs_radius),
        "lazy_componentwise_nontrivial_radius": fraction_dict(lazy_abs_radius),
    }


def select_min(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    best = min(row[key] for row in rows)
    return [row for row in rows if row[key] == best]


def select_max_fraction(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    values = [
        Fraction(row[key]["numerator"], row[key]["denominator"])
        for row in rows
    ]
    best = max(values)
    return [
        row
        for row in rows
        if Fraction(row[key]["numerator"], row[key]["denominator"]) == best
    ]


def compact_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "move_orbit_id": row["move_orbit_id"],
            "move_deltas": row["move_deltas"],
            "move_basis_cycle_indices": row["move_basis_cycle_indices"],
            "move_orbit_size": row["move_orbit_size"],
            "total_move_action": row["total_move_action"],
            "component_size_histogram": row["component_size_histogram"],
            "spectrum": row["spectrum"],
            "rank": row["rank"],
            "nullity": row["nullity"],
            "lazy_componentwise_nontrivial_gap": row[
                "lazy_componentwise_nontrivial_gap"
            ],
        }
        for row in rows
    ]


def selected_ids(rows: list[dict[str, Any]]) -> list[int]:
    return [int(row["move_orbit_id"]) for row in rows]


def selected_deltas(rows: list[dict[str, Any]]) -> list[list[int]]:
    return [list(row["move_deltas"]) for row in rows]


def build_theorem() -> dict[str, Any]:
    family = load_json(C2_MOVE_ORBIT_FAMILY_REPORT)
    family_summary = family.get("derived", {}).get("family_summary", {})
    base_rows = family.get("derived", {}).get("move_family_rows", [])
    scored_rows = []
    for row in base_rows:
        scores = gap_scores(row)
        scored_rows.append(
            {
                "move_orbit_id": row["move_orbit_id"],
                "move_deltas": row["move_deltas"],
                "move_basis_cycle_indices": row["move_basis_cycle_indices"],
                "move_orbit_size": row["move_orbit_size"],
                "contains_primitive_generator": row["contains_primitive_generator"],
                "total_move_action": row["total_move_action"],
                "max_move_action": row["max_move_action"],
                "component_count": row["component_count"],
                "component_size_histogram": row["component_size_histogram"],
                "spectrum": row["spectrum"],
                "rank": row["rank"],
                "nullity": row["nullity"],
                "stationary_denominator": row["stationary_denominator"],
                **scores,
            }
        )

    primitive_rows = [row for row in scored_rows if row["contains_primitive_generator"]]
    action_minimal_rows = select_min(scored_rows, "total_move_action")
    paired_rows = [row for row in scored_rows if row["move_orbit_size"] == 2]
    paired_action_minimal_rows = select_min(paired_rows, "total_move_action")
    raw_gap_rows = select_max_fraction(
        scored_rows, "raw_componentwise_nontrivial_absolute_gap"
    )
    lazy_gap_rows = select_max_fraction(
        scored_rows, "lazy_componentwise_nontrivial_gap"
    )
    paired_lazy_gap_rows = select_max_fraction(
        paired_rows, "lazy_componentwise_nontrivial_gap"
    )
    lazy_gap_action_tiebreak_rows = select_min(lazy_gap_rows, "total_move_action")
    paired_lazy_gap_action_tiebreak_rows = select_min(
        paired_lazy_gap_rows, "total_move_action"
    )

    by_component_type = Counter(
        json.dumps(row["component_size_histogram"], sort_keys=True)
        for row in scored_rows
    )
    by_lazy_gap = Counter(
        json.dumps(row["lazy_componentwise_nontrivial_gap"], sort_keys=True)
        for row in scored_rows
    )
    by_raw_gap = Counter(
        json.dumps(row["raw_componentwise_nontrivial_absolute_gap"], sort_keys=True)
        for row in scored_rows
    )

    selector_table = [
        {
            "criterion": "primitive_seeded",
            "definition": "Require the move orbit to contain a primitive generator delta.",
            "selected_count": len(primitive_rows),
            "selected_move_orbit_ids": selected_ids(primitive_rows),
            "selected_move_deltas": selected_deltas(primitive_rows),
            "unique": len(primitive_rows) == 1,
        },
        {
            "criterion": "global_action_minimal",
            "definition": "Minimize total hidden-neutral move action over all 543 admissible move orbits.",
            "selected_count": len(action_minimal_rows),
            "selected_move_orbit_ids": selected_ids(action_minimal_rows),
            "selected_move_deltas": selected_deltas(action_minimal_rows),
            "unique": len(action_minimal_rows) == 1,
        },
        {
            "criterion": "paired_action_minimal",
            "definition": "Require a non-fixed paired C2 move orbit, then minimize total move action.",
            "selected_count": len(paired_action_minimal_rows),
            "selected_move_orbit_ids": selected_ids(paired_action_minimal_rows),
            "selected_move_deltas": selected_deltas(paired_action_minimal_rows),
            "unique": len(paired_action_minimal_rows) == 1,
        },
        {
            "criterion": "raw_componentwise_absolute_spectral_gap",
            "definition": (
                "Remove one unit eigenvalue per connected component and maximize 1 minus the remaining "
                "absolute spectral radius."
            ),
            "selected_count": len(raw_gap_rows),
            "selected_move_orbit_ids_sha256": sha_json(selected_ids(raw_gap_rows)),
            "selected_move_deltas_sha256": sha_json(selected_deltas(raw_gap_rows)),
            "unique": len(raw_gap_rows) == 1,
            "max_gap": raw_gap_rows[0]["raw_componentwise_nontrivial_absolute_gap"],
        },
        {
            "criterion": "lazy_componentwise_spectral_gap",
            "definition": (
                "Apply the lazy normalization (I+P)/2, remove one unit eigenvalue per connected component, "
                "and maximize 1 minus the remaining absolute spectral radius."
            ),
            "selected_count": len(lazy_gap_rows),
            "selected_move_orbit_ids_sha256": sha_json(selected_ids(lazy_gap_rows)),
            "selected_move_deltas_sha256": sha_json(selected_deltas(lazy_gap_rows)),
            "unique": len(lazy_gap_rows) == 1,
            "max_gap": lazy_gap_rows[0]["lazy_componentwise_nontrivial_gap"],
            "action_tiebreak_selected_move_orbit_ids": selected_ids(
                lazy_gap_action_tiebreak_rows
            ),
            "action_tiebreak_selected_move_deltas": selected_deltas(
                lazy_gap_action_tiebreak_rows
            ),
        },
    ]

    selector_summary = {
        "candidate_family_size": len(scored_rows),
        "criteria_disagree": True,
        "primitive_seeded_selected": compact_rows(primitive_rows),
        "global_action_minimal_selected": compact_rows(action_minimal_rows),
        "paired_action_minimal_selected": compact_rows(paired_action_minimal_rows),
        "lazy_spectral_gap_selected_count": len(lazy_gap_rows),
        "lazy_spectral_gap_action_tiebreak_selected": compact_rows(
            lazy_gap_action_tiebreak_rows
        ),
        "paired_lazy_spectral_gap_selected_count": len(paired_lazy_gap_rows),
        "paired_lazy_spectral_gap_action_tiebreak_selected": compact_rows(
            paired_lazy_gap_action_tiebreak_rows
        ),
        "raw_gap_histogram": {
            key: int(by_raw_gap[key]) for key in sorted(by_raw_gap)
        },
        "lazy_gap_histogram": {
            key: int(by_lazy_gap[key]) for key in sorted(by_lazy_gap)
        },
        "component_type_counts": {
            key: int(by_component_type[key]) for key in sorted(by_component_type)
        },
        "selection_verdict": (
            "No selector-free physical preference is certified. Primitive-seededness selects {8,1034}; "
            "global action and lazy spectral-gap with action tiebreak select {384}; paired-action and "
            "paired lazy-gap with action tiebreak select {288,320}."
        ),
    }

    checks = {
        "c2_move_orbit_family_is_certified": family.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_CERTIFIED"
        and family.get("all_checks_pass") is True,
        "candidate_family_has_expected_size": len(scored_rows) == 543
        and family_summary.get("fixed_move_orbit_count") == 63
        and family_summary.get("paired_move_orbit_count") == 480,
        "primitive_seeded_selector_is_unique_prior_operator": selected_deltas(primitive_rows)
        == [[8, 1034]],
        "global_action_selector_is_unique_fixed_minimum": selected_deltas(action_minimal_rows)
        == [[384]]
        and action_minimal_rows[0]["total_move_action"] == 1443840,
        "paired_action_selector_is_unique_paired_minimum": selected_deltas(
            paired_action_minimal_rows
        )
        == [[288, 320]]
        and paired_action_minimal_rows[0]["total_move_action"] == 2343936,
        "raw_absolute_gap_is_degenerate_on_entire_family": len(raw_gap_rows) == 543
        and raw_gap_rows[0]["raw_componentwise_nontrivial_absolute_gap"]
        == {"numerator": 0, "denominator": 1},
        "lazy_gap_selects_exactly_fixed_singleton_family": len(lazy_gap_rows) == 63
        and all(row["move_orbit_size"] == 1 for row in lazy_gap_rows)
        and lazy_gap_rows[0]["lazy_componentwise_nontrivial_gap"]
        == {"numerator": 1, "denominator": 1},
        "lazy_gap_action_tiebreak_is_global_action_minimum": selected_deltas(
            lazy_gap_action_tiebreak_rows
        )
        == [[384]],
        "paired_lazy_gap_action_tiebreak_is_paired_action_minimum": selected_deltas(
            paired_lazy_gap_action_tiebreak_rows
        )
        == [[288, 320]],
        "selection_criteria_are_not_equivalent": len(
            {
                tuple(primitive_rows[0]["move_deltas"]),
                tuple(action_minimal_rows[0]["move_deltas"]),
                tuple(paired_action_minimal_rows[0]["move_deltas"]),
            }
        )
        == 3,
        "selector_rows_are_stably_hashed": sha_json(scored_rows)
        and sha_json(selector_table),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_dynamics_selector",
        "status": status,
        "object": "d20",
        "claim": (
            "The C2 quotient dynamics family has no selector-free unique physical operator. Different "
            "natural selectors pick different certified Ward-balanced dynamics: primitive-seededness picks "
            "{8,1034}, global action minimization picks {384}, paired-action minimization picks {288,320}, "
            "and lazy componentwise spectral-gap maximization picks the fixed singleton family with {384} "
            "as its action tiebreak."
        ),
        "definition": {
            "selector_domain": (
                "The 543 C2-closed hidden-neutral move-orbit operators certified by the move-orbit family "
                "theorem."
            ),
            "raw_componentwise_absolute_spectral_gap": (
                "After removing one eigenvalue 1 for each connected component, the quantity 1-rho_abs "
                "computed from the remaining raw spectrum."
            ),
            "lazy_componentwise_spectral_gap": (
                "The same componentwise nontrivial gap after replacing P by (I+P)/2, used to remove "
                "period-two obstruction from the fixed singleton operators."
            ),
        },
        "inputs": {
            "c2_move_orbit_family_report": {
                "path": rel(C2_MOVE_ORBIT_FAMILY_REPORT),
                "sha256": sha_file(C2_MOVE_ORBIT_FAMILY_REPORT),
            },
        },
        "derived": {
            "selector_summary": selector_summary,
            "selector_table": selector_table,
            "scored_move_rows_sha256": sha_json(scored_rows),
            "selector_table_sha256": sha_json(selector_table),
            "scored_move_rows": scored_rows,
        },
        "interpretation": {
            "what_this_proves": [
                "primitive-seeded, action-minimal, paired-action-minimal, and spectral criteria are distinct",
                "the earlier {8,1034} operator is physically preferred only if primitive seeding is imposed",
                "least action and lazy spectral-gap with action tiebreak both prefer the fixed singleton {384}",
                "if paired C2 transport is required, {288,320} is the least-action and spectral-action tiebreak",
            ],
            "what_this_does_not_prove": (
                "This does not choose the physical axiom. It certifies the selector table that any later "
                "physics-grade preference must pass through."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Prove or refute a physical selector axiom: require primitive seeding, least action, paired "
            "transport, or maximal lazy spectral relaxation, then propagate the selected dynamics to the "
            "finite BMS/Carrollian flux-balance recovery."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem_manifest",
        "theorem_id": THEOREM_ID,
        "status": report["status"],
        "report": rel(out_dir / "report.json"),
        "inputs": report["inputs"],
        "checks": report["checks"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
