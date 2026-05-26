from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS, DATA
except ImportError:  # Supports `python src/derive_d20_fourier_a985_sector_character_candidates.py`.
    from derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from paths import D20_INVARIANTS, DATA


THEOREM_ID = "fourier_a985_sector_character_candidates"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FOURIER_RESIDUE_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_residue_screen" / "report.json"
)
SECTOR_UNIQUE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
)
SECTOR_ADMISSIBILITY_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_idempotent_support_admissibility" / "report.json"
)
FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
EXPECTED_HOMOGENEOUS_COUNTS = {
    "signed_turn_screen_0": {"homogeneous": 16, "mixed": 23},
    "signed_turn_screen_1": {"homogeneous": 12, "mixed": 27},
    "signed_turn_screen_2": {"homogeneous": 16, "mixed": 23},
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


def phase_assignment(screen: dict[str, Any]) -> dict[str, int]:
    phases = {label: 1 for label in screen["source_positive_phase_labels"]}
    phases.update({label: -1 for label in screen["source_negative_phase_labels"]})
    return {label: phases[label] for label in H6_LABELS}


def local_phase_counts(phases: dict[str, int], local_summaries: dict[str, Any]) -> dict[str, int]:
    counts = {"+1": 0, "-1": 0}
    for obj_key, summary in local_summaries.items():
        label = summary["label"]
        key = "+1" if phases[label] == 1 else "-1"
        counts[key] += int(summary["primitive_idempotent_count"])
    return counts


def sector_evaluation_rows(
    phases: dict[str, int],
    sector_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for row in sector_rows:
        active_objects = list(row["active_objects"])
        object_phases = {label: phases[label] for label in active_objects}
        values = sorted(set(object_phases.values()))
        homogeneous = len(values) <= 1
        scalar = values[0] if homogeneous and values else None
        primitive_piece_rows = []
        for obj, local in row["local_pre_idempotent_keys"]:
            label = H6_LABELS[int(obj)]
            primitive_piece_rows.append(
                {
                    "object": int(obj),
                    "label": label,
                    "local_pre_idempotent": int(local),
                    "phase": phases[label],
                }
            )
        rows.append(
            {
                "sector": int(row["sector"]),
                "block_dimension": int(row["block_dimension"]),
                "active_objects": active_objects,
                "object_phases": object_phases,
                "primitive_piece_phases": primitive_piece_rows,
                "homogeneous_on_sector": homogeneous,
                "sector_scalar": scalar,
                "public_zero": bool(row["public_zero"]),
            }
        )
    return rows


def public_zero_support_evaluations(
    sector_rows: list[dict[str, Any]],
    sector_evaluations: list[dict[str, Any]],
    support_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_sector = {int(row["sector"]): row for row in sector_evaluations}
    dimension_by_sector = {int(row["sector"]): int(row["block_dimension"]) for row in sector_rows}
    out = []
    for support in support_rows:
        sectors = [int(value) for value in support["sector_support"]]
        scalars = [
            by_sector[sector]["sector_scalar"]
            for sector in sectors
            if by_sector[sector]["homogeneous_on_sector"]
        ]
        all_sectors_homogeneous = all(by_sector[sector]["homogeneous_on_sector"] for sector in sectors)
        scalar_values = sorted(set(scalars))
        scalar_on_support = (
            all_sectors_homogeneous and len(scalar_values) == 1
            if sectors
            else True
        )
        out.append(
            {
                "sector_support": sectors,
                "sector_count": int(support["sector_count"]),
                "regular_trace": int(support["regular_trace"]),
                "dimension_sum": int(support["dimension_sum"]),
                "sector_dimensions": [dimension_by_sector[sector] for sector in sectors],
                "public_zero": bool(support["public_zero"]),
                "boundary_null": bool(support["boundary_null"]),
                "scalar_on_support": scalar_on_support,
                "support_scalar": scalar_values[0] if scalar_on_support and scalar_values else (0 if not sectors else None),
                "all_member_sectors_homogeneous": all_sectors_homogeneous,
                "member_sector_scalars": [
                    {
                        "sector": sector,
                        "homogeneous_on_sector": by_sector[sector]["homogeneous_on_sector"],
                        "sector_scalar": by_sector[sector]["sector_scalar"],
                    }
                    for sector in sectors
                ],
            }
        )
    return out


def screen_candidate_record(
    screen: dict[str, Any],
    sector_rows: list[dict[str, Any]],
    support_rows: list[dict[str, Any]],
    local_summaries: dict[str, Any],
) -> dict[str, Any]:
    phases = phase_assignment(screen)
    sector_evaluations = sector_evaluation_rows(phases, sector_rows)
    homogeneous = [row for row in sector_evaluations if row["homogeneous_on_sector"]]
    mixed = [row for row in sector_evaluations if not row["homogeneous_on_sector"]]
    scalar_histogram = Counter(str(row["sector_scalar"]) for row in homogeneous)
    public_zero_evaluations = public_zero_support_evaluations(
        sector_rows,
        sector_evaluations,
        support_rows,
    )
    nonzero_public_zero = [
        row for row in public_zero_evaluations if row["public_zero"] and row["sector_count"] > 0
    ]
    pi33 = next(row for row in sector_evaluations if row["sector"] == 33)
    return {
        "screen_id": screen["screen_id"],
        "defect_cycle_ids": screen["defect_cycle_ids"],
        "defect_vector_mask": screen["defect_vector_mask"],
        "object_phase_assignment": phases,
        "local_primitive_phase_counts": local_phase_counts(phases, local_summaries),
        "local_phase_operator_involution": all(value in {-1, 1} for value in phases.values()),
        "homogeneous_sector_count": len(homogeneous),
        "mixed_sector_count": len(mixed),
        "homogeneous_sector_scalars": {key: int(value) for key, value in sorted(scalar_histogram.items())},
        "descends_to_all_39_sector_scalars": len(mixed) == 0,
        "pi33_sector_scalar": pi33["sector_scalar"],
        "pi33_homogeneous": pi33["homogeneous_on_sector"],
        "all_nonzero_public_zero_supports_scalar": all(
            row["scalar_on_support"] for row in nonzero_public_zero
        ),
        "public_zero_support_evaluations": public_zero_evaluations,
        "sector_evaluations_sha256": hashlib.sha256(canonical(sector_evaluations)).hexdigest(),
        "sector_evaluations": sector_evaluations,
    }


def build_theorem() -> dict[str, Any]:
    fourier = load_json(FOURIER_RESIDUE_REPORT)
    sector_unique = load_json(SECTOR_UNIQUE_REPORT)
    admissibility = load_json(SECTOR_ADMISSIBILITY_REPORT)
    full = load_json(FULL_A985_LIFT)

    screens = fourier["derived"]["screens"]
    sector_rows = sorted(
        sector_unique["derived"]["sector_rows"],
        key=lambda row: int(row["sector"]),
    )
    local_summaries = sector_unique["derived"]["local_pre_idempotent_summaries"]
    support_rows = sorted(
        admissibility["derived"]["candidate_rows"],
        key=lambda row: (int(row["sector_count"]), row["sector_support"]),
    )
    candidates = [
        screen_candidate_record(screen, sector_rows, support_rows, local_summaries)
        for screen in screens
    ]
    expected_counts_match = all(
        {
            "homogeneous": int(candidate["homogeneous_sector_count"]),
            "mixed": int(candidate["mixed_sector_count"]),
        }
        == EXPECTED_HOMOGENEOUS_COUNTS[candidate["screen_id"]]
        for candidate in candidates
    )
    public_zero_scalar_profile = {
        candidate["screen_id"]: bool(candidate["all_nonzero_public_zero_supports_scalar"])
        for candidate in candidates
    }
    pi33_scalars = {
        candidate["screen_id"]: int(candidate["pi33_sector_scalar"])
        for candidate in candidates
    }
    local_totals = [
        sum(candidate["local_primitive_phase_counts"].values()) for candidate in candidates
    ]

    checks = {
        "fourier_residue_screen_is_certified": fourier.get("status")
        == "D20_FOURIER_RESIDUE_SCREEN_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "sector33_unique_public_zero_support_is_certified": sector_unique.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and sector_unique.get("all_checks_pass") is True,
        "sector_idempotent_support_admissibility_is_classified": admissibility.get("status")
        == "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED"
        and admissibility.get("all_checks_pass") is True,
        "full_a985_lift_is_certified": full.get("status") == "DRINFELD_FULL_A985_LIFT_CERTIFIED",
        "sector_profile_count_is_39": len(sector_rows) == 39
        and len(full["gluing_and_sector_profiles"]["sector_profiles"]) == 39,
        "screen_count_is_3": len(candidates) == 3,
        "each_screen_labels_all_six_objects": all(
            sorted(candidate["object_phase_assignment"]) == sorted(H6_LABELS)
            for candidate in candidates
        ),
        "each_screen_local_phase_operator_is_involution": all(
            candidate["local_phase_operator_involution"] for candidate in candidates
        ),
        "each_screen_touches_all_109_local_primitive_pieces": local_totals == [109, 109, 109],
        "homogeneous_mixed_sector_counts_match": expected_counts_match,
        "no_screen_descends_to_all_39_sector_scalars": all(
            not candidate["descends_to_all_39_sector_scalars"] for candidate in candidates
        ),
        "pi33_is_scalar_for_all_three_candidates": pi33_scalars
        == {
            "signed_turn_screen_0": 1,
            "signed_turn_screen_1": 1,
            "signed_turn_screen_2": -1,
        },
        "only_first_screen_is_scalar_on_all_nonzero_public_zero_supports": public_zero_scalar_profile
        == {
            "signed_turn_screen_0": True,
            "signed_turn_screen_1": False,
            "signed_turn_screen_2": False,
        },
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        if all_checks_pass
        else "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_NEED_REVIEW"
    )

    report = {
        "schema": "d20.theorem.fourier_a985_sector_character_candidates",
        "status": status,
        "object": "d20",
        "claim": (
            "The three finite Fourier residue screens define signed-object involutions on the "
            "109 local closed-loop primitive pieces, but none descends to a scalar character on "
            "all 39 materialized A985/tube sector idempotents. The first screen is scalar on all "
            "certified nonzero public-zero idempotent supports; the second and third are not."
        ),
        "definition": {
            "signed_object_phase_candidate": (
                "Use the signed-turn phase assignment on B-, B+, V-, V+, S-, S+ as a diagonal "
                "phase on local primitive closed-loop pieces by object label."
            ),
            "sector_character_test": (
                "A candidate descends to a scalar on a sector idempotent exactly when all local "
                "primitive pieces in that sector carry the same phase."
            ),
            "scope_boundary": (
                "This evaluates candidate sector characters against certified A985/tube sector "
                "profiles. It does not construct a new central idempotent basis or a full Fourier "
                "transform on A985 modules."
            ),
        },
        "inputs": {
            "fourier_residue_screen_report": {
                "path": rel(FOURIER_RESIDUE_REPORT),
                "sha256": sha_file(FOURIER_RESIDUE_REPORT),
            },
            "sector33_unique_public_zero_support_report": {
                "path": rel(SECTOR_UNIQUE_REPORT),
                "sha256": sha_file(SECTOR_UNIQUE_REPORT),
            },
            "sector_idempotent_support_admissibility_report": {
                "path": rel(SECTOR_ADMISSIBILITY_REPORT),
                "sha256": sha_file(SECTOR_ADMISSIBILITY_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
        },
        "derived": {
            "h6_labels": H6_LABELS,
            "sector_count": len(sector_rows),
            "local_primitive_piece_count": 109,
            "public_zero_support_count_including_zero": len(
                [row for row in support_rows if row["public_zero"]]
            ),
            "nonzero_public_zero_supports": [
                row["sector_support"]
                for row in support_rows
                if row["public_zero"] and int(row["sector_count"]) > 0
            ],
            "candidate_count": len(candidates),
            "public_zero_scalar_profile": public_zero_scalar_profile,
            "pi33_scalars": pi33_scalars,
            "candidate_records_sha256": hashlib.sha256(canonical(candidates)).hexdigest(),
            "candidates": candidates,
        },
        "interpretation": {
            "what_is_certified": (
                "The signed-turn residue screens can be tested directly on the materialized "
                "A985/tube sector profiles, and the obstruction to a global sector character is "
                "the mixed object phase inside some sector idempotents."
            ),
            "what_this_does_not_prove": (
                "This does not produce an A985 Fourier basis. It proves a candidate evaluation "
                "and records which signed-object screens fail or survive the scalar sector test."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Refine the surviving public-zero-compatible screen into an actual tube central element "
            "by projecting it through the local primitive-idempotent coordinates and checking "
            "multiplication against the 297-dimensional closed-loop algebra."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.fourier_a985_sector_character_candidates_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the finite Fourier residue screen is certified",
            "verify the materialized A985/tube sector-idempotent profile is certified",
            "evaluate each signed-object phase candidate on the 109 local primitive pieces",
            "test whether each candidate is scalar on each of the 39 sector idempotents",
            "test public-zero idempotent supports for scalar compatibility",
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
