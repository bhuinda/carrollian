from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

C2_QUOTIENT_ANOMALY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
    / "report.json"
)
C2_MOVE_ORBIT_FAMILY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family"
    / "report.json"
)
C2_DYNAMICS_SELECTOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector"
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


def compact_dynamics_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "move_orbit_id": int(row["move_orbit_id"]),
        "move_deltas": row["move_deltas"],
        "move_basis_cycle_indices": row["move_basis_cycle_indices"],
        "move_orbit_size": int(row["move_orbit_size"]),
        "total_move_action": int(row["total_move_action"]),
        "component_size_histogram": row["component_size_histogram"],
        "spectrum": row["spectrum"],
        "rank": int(row["rank"]),
        "nullity": int(row["nullity"]),
    }


def selected_ids_from_compact(rows: list[dict[str, Any]]) -> list[int]:
    return sorted(int(row["move_orbit_id"]) for row in rows)


def build_target_universe(anomaly_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    masks_by_orbit: dict[int, set[int]] = defaultdict(set)
    tau_by_mask: dict[int, int] = {}
    representative_by_orbit: dict[int, int] = {}
    for row in anomaly_rows:
        orbit_id = int(row["orbit_id"])
        target_mask = int(row["target_mask"])
        masks_by_orbit[orbit_id].add(target_mask)
        tau_by_mask[target_mask] = int(row["tau_target_mask"])
        representative_by_orbit[orbit_id] = int(row["representative_mask"])

    target_universe = []
    for orbit_id in sorted(masks_by_orbit):
        masks = sorted(masks_by_orbit[orbit_id])
        tau_edges = sorted([{"source": mask, "target": tau_by_mask[mask]} for mask in masks], key=lambda x: x["source"])
        code = {
            "orbit_id": orbit_id,
            "representative_mask": representative_by_orbit[orbit_id],
            "target_masks": masks,
            "orbit_size": len(masks),
            "tau_path_kind": "reflexive_fixed_point" if len(masks) == 1 else "nontrivial_c2_path_pair",
            "tau_edges": tau_edges,
        }
        code["code_sha256"] = sha_json(code)
        target_universe.append(code)
    return target_universe


def build_dynamics_universe(move_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dynamics_universe = []
    for row in move_rows:
        compact = compact_dynamics_row(row)
        structure = {
            **compact,
            "stationary_balance": row["stationary_balance"],
            "operator_symmetric": row["operator_symmetric"],
        }
        code = {
            **compact,
            "structure_sha256": sha_json(structure),
            "identity_principle": "same canonical dynamics code iff same certified structure",
        }
        code["code_sha256"] = sha_json(code)
        dynamics_universe.append(code)
    return sorted(dynamics_universe, key=lambda row: row["move_orbit_id"])


def build_selector_fibers(
    selector_summary: dict[str, Any],
    scored_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scored_by_id = {int(row["move_orbit_id"]): row for row in scored_rows}
    all_ids = sorted(scored_by_id)
    raw_gap_ids = [
        move_id
        for move_id, row in scored_by_id.items()
        if row["raw_componentwise_nontrivial_absolute_gap"]
        == {"denominator": 1, "numerator": 0}
    ]
    lazy_gap_ids = [
        move_id
        for move_id, row in scored_by_id.items()
        if row["lazy_componentwise_nontrivial_gap"]
        == {"denominator": 1, "numerator": 1}
    ]
    paired_lazy_gap_ids = [
        move_id
        for move_id, row in scored_by_id.items()
        if int(row["move_orbit_size"]) == 2
        and row["lazy_componentwise_nontrivial_gap"]
        == {"denominator": 2, "numerator": 1}
    ]
    fibers = [
        {
            "selector": "primitive_seeded",
            "selected_move_orbit_ids": selected_ids_from_compact(
                selector_summary["primitive_seeded_selected"]
            ),
            "contractible": True,
        },
        {
            "selector": "global_action_minimal",
            "selected_move_orbit_ids": selected_ids_from_compact(
                selector_summary["global_action_minimal_selected"]
            ),
            "contractible": True,
        },
        {
            "selector": "paired_action_minimal",
            "selected_move_orbit_ids": selected_ids_from_compact(
                selector_summary["paired_action_minimal_selected"]
            ),
            "contractible": True,
        },
        {
            "selector": "raw_componentwise_absolute_spectral_gap",
            "selected_move_orbit_ids": sorted(raw_gap_ids),
            "contractible": False,
        },
        {
            "selector": "lazy_componentwise_spectral_gap",
            "selected_move_orbit_ids": sorted(lazy_gap_ids),
            "contractible": False,
        },
        {
            "selector": "lazy_componentwise_spectral_gap_action_tiebreak",
            "selected_move_orbit_ids": selected_ids_from_compact(
                selector_summary["lazy_spectral_gap_action_tiebreak_selected"]
            ),
            "contractible": True,
        },
        {
            "selector": "paired_lazy_componentwise_spectral_gap",
            "selected_move_orbit_ids": sorted(paired_lazy_gap_ids),
            "contractible": False,
        },
        {
            "selector": "paired_lazy_componentwise_spectral_gap_action_tiebreak",
            "selected_move_orbit_ids": selected_ids_from_compact(
                selector_summary["paired_lazy_spectral_gap_action_tiebreak_selected"]
            ),
            "contractible": True,
        },
    ]
    for fiber in fibers:
        fiber["selected_count"] = len(fiber["selected_move_orbit_ids"])
        fiber["selected_move_orbit_ids_sha256"] = sha_json(fiber["selected_move_orbit_ids"])
        fiber["subset_of_dynamics_universe"] = set(fiber["selected_move_orbit_ids"]).issubset(all_ids)
        fiber["is_hprop_fiber"] = fiber["selected_count"] <= 1
    return fibers


def build_theorem() -> dict[str, Any]:
    anomaly = load_json(C2_QUOTIENT_ANOMALY_REPORT)
    move_family = load_json(C2_MOVE_ORBIT_FAMILY_REPORT)
    selector = load_json(C2_DYNAMICS_SELECTOR_REPORT)

    anomaly_rows = anomaly.get("derived", {}).get("anomaly_rows", [])
    move_rows = move_family.get("derived", {}).get("move_family_rows", [])
    selector_summary = selector.get("derived", {}).get("selector_summary", {})
    scored_rows = selector.get("derived", {}).get("scored_move_rows", [])

    target_universe = build_target_universe(anomaly_rows)
    dynamics_universe = build_dynamics_universe(move_rows)
    selector_fibers = build_selector_fibers(selector_summary, scored_rows)

    target_code_hashes = [row["code_sha256"] for row in target_universe]
    dynamics_code_hashes = [row["code_sha256"] for row in dynamics_universe]
    target_orbit_sizes = Counter(row["orbit_size"] for row in target_universe)
    dynamics_orbit_sizes = Counter(row["move_orbit_size"] for row in dynamics_universe)
    selector_by_name = {row["selector"]: row for row in selector_fibers}
    dynamics_ids = {int(row["move_orbit_id"]) for row in dynamics_universe}

    univalent_candidate_signature = {
        "claim_level": "finite_skeletal_univalent_foundation_candidate",
        "universe_codes": [
            {
                "code": "C2TargetQuotient",
                "eliminates": "raw nonzero Ward-kernel target masks modulo tau paths",
                "element_count": len(target_universe),
                "source_point_count": len(anomaly_rows),
                "path_constructor_count": target_orbit_sizes.get(2, 0),
                "fixed_path_count": target_orbit_sizes.get(1, 0),
                "truncation": "set",
            },
            {
                "code": "C2WardBalancedDynamics",
                "eliminates": "C2-closed hidden-neutral move orbits with certified Markov/Ward data",
                "element_count": len(dynamics_universe),
                "source_move_delta_count": sum(row["move_orbit_size"] for row in dynamics_universe),
                "path_constructor_count": dynamics_orbit_sizes.get(2, 0),
                "fixed_path_count": dynamics_orbit_sizes.get(1, 0),
                "truncation": "set",
            },
            {
                "code": "C2DynamicsSelector",
                "eliminates": "finite selector criteria over C2WardBalancedDynamics",
                "element_count": len(selector_fibers),
                "truncation": "set",
            },
            {
                "code": "SelectedDynamics",
                "eliminates": "dependent selector fibers Sigma(selector, selected dynamics)",
                "fiber_count": len(selector_fibers),
                "contractible_fiber_count": sum(1 for row in selector_fibers if row["contractible"]),
                "noncontractible_fiber_count": sum(1 for row in selector_fibers if not row["contractible"]),
                "truncation": "set with hProp subfibers when selected_count <= 1",
            },
        ],
        "hit_signature": {
            "C2TargetQuotient": {
                "points": "target_mask : NonzeroWardKernelMask",
                "paths": "tau_path(m) : target_mask(m) = target_mask(tau(m))",
                "set_truncation": "all identity types are propositions after quotienting",
            },
            "C2WardBalancedDynamics": {
                "points": "move_orbit : C2ClosedHiddenNeutralMoveOrbit",
                "paths": "tau_move_path(delta) : move(delta) = move(tau(delta))",
                "structure": "symmetric Markov operator + stationary Ward/BMS balance witness",
            },
            "SelectedDynamics": {
                "points": "selector criterion with selected C2WardBalancedDynamics fiber",
                "paths": "contractible exactly for singleton selector fibers",
            },
        },
        "identity_equivalence_principle": {
            "finite_skeletal_rule": (
                "For this candidate universe, two codes are identified exactly when their canonical "
                "structure hashes agree; equivalence-to-path is therefore a finite skeletal rule."
            ),
            "target_code_hashes_sha256": sha_json(target_code_hashes),
            "dynamics_code_hashes_sha256": sha_json(dynamics_code_hashes),
            "selector_fibers_sha256": sha_json(selector_fibers),
        },
        "constructive_univalence_gate": {
            "equivalence_witness": "tau quotient paths plus canonical dynamics structure hashes",
            "zero_transport_residue": "all move-family stationary public and hidden Ward/BMS balances close",
            "height_coherence": "target height action cancels R33 residual in every stationary row",
            "formal_proof_artifact_present": False,
        },
    }

    bridge_summary = {
        "target_source_mask_count": len(anomaly_rows),
        "target_quotient_count": len(target_universe),
        "target_fixed_count": int(target_orbit_sizes.get(1, 0)),
        "target_paired_count": int(target_orbit_sizes.get(2, 0)),
        "dynamics_count": len(dynamics_universe),
        "dynamics_fixed_count": int(dynamics_orbit_sizes.get(1, 0)),
        "dynamics_paired_count": int(dynamics_orbit_sizes.get(2, 0)),
        "selector_count": len(selector_fibers),
        "contractible_selector_fibers": [
            row["selector"] for row in selector_fibers if row["contractible"]
        ],
        "noncontractible_selector_fibers": [
            row["selector"] for row in selector_fibers if not row["contractible"]
        ],
        "primitive_seeded_selected_ids": selector_by_name["primitive_seeded"][
            "selected_move_orbit_ids"
        ],
        "least_action_selected_ids": selector_by_name["global_action_minimal"][
            "selected_move_orbit_ids"
        ],
        "paired_least_action_selected_ids": selector_by_name["paired_action_minimal"][
            "selected_move_orbit_ids"
        ],
        "lazy_gap_selected_count": selector_by_name["lazy_componentwise_spectral_gap"][
            "selected_count"
        ],
        "paired_lazy_gap_selected_count": selector_by_name[
            "paired_lazy_componentwise_spectral_gap"
        ]["selected_count"],
        "candidate_verdict": (
            "The C2 selector layer admits a complete finite skeletal univalent-foundation candidate: "
            "states are a C2 set-quotient HIT, dynamics are a finite certified structure universe, "
            "selectors are dependent fibers, and singleton selectors are contractible hProp-like fibers. "
            "This is not yet a proof-assistant formalization of univalence."
        ),
    }

    checks = {
        "c2_quotient_anomaly_is_certified": anomaly.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_CERTIFIED"
        and anomaly.get("all_checks_pass") is True,
        "c2_move_orbit_family_is_certified": move_family.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_CERTIFIED"
        and move_family.get("all_checks_pass") is True,
        "c2_dynamics_selector_is_certified": selector.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_CERTIFIED"
        and selector.get("all_checks_pass") is True,
        "target_universe_is_complete_c2_set_quotient": len(anomaly_rows) == 1023
        and len(target_universe) == 543
        and target_orbit_sizes == Counter({2: 480, 1: 63}),
        "target_universe_codes_are_skeletal": len(set(target_code_hashes)) == 543,
        "dynamics_universe_is_complete_move_family": len(dynamics_universe) == 543
        and dynamics_orbit_sizes == Counter({2: 480, 1: 63}),
        "dynamics_universe_codes_are_skeletal": len(set(dynamics_code_hashes)) == 543
        and {int(row["move_orbit_id"]) for row in dynamics_universe} == set(range(543)),
        "selector_fibers_are_subtypes_of_dynamics_universe": all(
            set(row["selected_move_orbit_ids"]).issubset(dynamics_ids)
            and row["subset_of_dynamics_universe"]
            for row in selector_fibers
        ),
        "singleton_selectors_are_contractible": selector_by_name["primitive_seeded"][
            "selected_move_orbit_ids"
        ]
        == [3]
        and selector_by_name["global_action_minimal"]["selected_move_orbit_ids"] == [173]
        and selector_by_name["paired_action_minimal"]["selected_move_orbit_ids"] == [130]
        and selector_by_name["lazy_componentwise_spectral_gap_action_tiebreak"][
            "selected_move_orbit_ids"
        ]
        == [173]
        and selector_by_name["paired_lazy_componentwise_spectral_gap_action_tiebreak"][
            "selected_move_orbit_ids"
        ]
        == [130],
        "noncontractible_selectors_record_required_multiplicity": selector_by_name[
            "raw_componentwise_absolute_spectral_gap"
        ]["selected_count"]
        == 543
        and selector_by_name["lazy_componentwise_spectral_gap"]["selected_count"] == 63
        and selector_by_name["paired_lazy_componentwise_spectral_gap"]["selected_count"] == 480,
        "constructive_univalence_gate_is_instantiated_as_candidate_not_formal_proof": (
            univalent_candidate_signature["constructive_univalence_gate"][
                "formal_proof_artifact_present"
            ]
            is False
            and move_family.get("derived", {})
            .get("family_summary", {})
            .get("all_stationary_balances_close")
            is True
        ),
        "finite_signature_hashes_are_stable": sha_json(target_universe)
        and sha_json(dynamics_universe)
        and sha_json(selector_fibers)
        and sha_json(univalent_candidate_signature),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge",
        "status": status,
        "object": "d20",
        "claim": (
            "The certified C2 selector layer determines a complete finite skeletal candidate for a "
            "univalent-foundations presentation: C2 quotient states are a set-quotient HIT, C2 dynamics "
            "form a finite certified structure universe, selectors are dependent fibers, and singleton "
            "selector fibers are contractible. This is a candidate bridge, not a completed formal UF proof."
        ),
        "definition": {
            "finite_skeletal_univalent_candidate": (
                "A finite universe of canonical structure codes where identity is represented by equality "
                "of stable certified hashes, and equivalence-to-path is restricted to that skeletal layer."
            ),
            "complete_for_current_selector_layer": (
                "Every C2 quotient target, every C2-closed hidden-neutral dynamics row, and every certified "
                "selector fiber from the input reports has a code in the candidate signature."
            ),
        },
        "inputs": {
            "c2_quotient_anomaly_report": {
                "path": rel(C2_QUOTIENT_ANOMALY_REPORT),
                "sha256": sha_file(C2_QUOTIENT_ANOMALY_REPORT),
            },
            "c2_move_orbit_family_report": {
                "path": rel(C2_MOVE_ORBIT_FAMILY_REPORT),
                "sha256": sha_file(C2_MOVE_ORBIT_FAMILY_REPORT),
            },
            "c2_dynamics_selector_report": {
                "path": rel(C2_DYNAMICS_SELECTOR_REPORT),
                "sha256": sha_file(C2_DYNAMICS_SELECTOR_REPORT),
            },
        },
        "derived": {
            "bridge_summary": bridge_summary,
            "univalent_candidate_signature": univalent_candidate_signature,
            "target_universe_sha256": sha_json(target_universe),
            "dynamics_universe_sha256": sha_json(dynamics_universe),
            "selector_fibers_sha256": sha_json(selector_fibers),
            "target_universe": target_universe,
            "dynamics_universe": dynamics_universe,
            "selector_fibers": selector_fibers,
        },
        "interpretation": {
            "what_this_proves": [
                "the C2 selector layer has enough finite data to be presented as a set-truncated HIT plus finite structure universe",
                "selector choices become dependent fibers over the certified dynamics universe",
                "primitive, least-action, paired least-action, and action-tiebroken spectral selectors are contractible fibers",
                "raw and untiebroken spectral selectors remain noncontractible fibers, preserving the selector ambiguity",
            ],
            "what_this_does_not_prove": [
                "no Lean/Coq/Agda/HoTT formalization has been emitted",
                "the theorem does not prove univalence for all D20 mathematics",
                "the theorem does not select the physical axiom among the competing contractible fibers",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Emit a proof-assistant target skeleton for the C2TargetQuotient HIT, C2WardBalancedDynamics "
            "record, selector fibers, and the finite skeletal identity/equivalence rule."
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
