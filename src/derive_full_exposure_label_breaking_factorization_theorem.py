from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

from src.derive_full_exposure_radical_gate_stabilizer_lift_theorem import (
    active_flip_lift_count,
    all_gl4,
    apply_linear,
    canonical_packet_permutation,
    canonical_preserves_label,
    local_gate,
    packet_id,
    pattern_bits,
    radical_from_pattern,
)
from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_label_breaking_factorization"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_radical_gate_stabilizer_lift"
    / "report.json"
)
PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)

AXIS_FAMILIES: dict[str, list[str]] = {
    "mass": ["mass_frame"],
    "clock": ["clock_frame"],
    "gamma": ["gamma_frame", "gamma8_touched", "gamma8_mode_count"],
    "sector26": [
        "sector26_clock_sum_mod26",
        "sector26_clock_delta_mod26",
        "sector26_clock_zero_pair",
        "sector26_clock_zero_touched",
    ],
    "spectral": ["adjacency_trace", "laplacian_trace"],
}

ATOMIC_LABELS: dict[str, list[str]] = {
    "mass_frame": ["mass_frame"],
    "clock_frame": ["clock_frame"],
    "gamma_frame": ["gamma_frame"],
    "gamma8_marker": ["gamma8_touched", "gamma8_mode_count"],
    "sector26_sum": ["sector26_clock_sum_mod26"],
    "sector26_delta": ["sector26_clock_delta_mod26"],
    "sector26_zero_pair": ["sector26_clock_zero_pair"],
    "sector26_zero_touched": ["sector26_clock_zero_touched"],
    "spectral_trace": ["adjacency_trace", "laplacian_trace"],
    "fine_spectral": ["fine_spectral_charge_key"],
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def keys_for(names: tuple[str, ...] | list[str], registry: dict[str, list[str]]) -> list[str]:
    keys: list[str] = []
    for name in names:
        keys.extend(registry[name])
    return keys


def label_value(row: dict[str, Any], keys: list[str]) -> tuple[Any, ...]:
    return tuple(row.get(key) for key in keys)


def build_affine_rows() -> tuple[list[int], list[int], list[int], list[dict[str, Any]]]:
    gate_support = sorted(pattern for pattern in range(16) if local_gate(pattern))
    radicals = [radical_from_pattern(pattern) for pattern in gate_support]
    packets = sorted(packet_id(radical, active_sigma) for radical in radicals for active_sigma in (0, 1))
    radical_by_pattern = {pattern: radical_from_pattern(pattern) for pattern in gate_support}
    affine_rows = []
    for columns in all_gl4():
        for translation in range(16):
            point_image = {
                point: apply_linear(columns, point) ^ translation
                for point in gate_support
            }
            if sorted(point_image.values()) != gate_support:
                continue
            component_permutation = {
                radical_by_pattern[source_pattern]: radical_by_pattern[target_pattern]
                for source_pattern, target_pattern in point_image.items()
            }
            packet_permutation = canonical_packet_permutation(component_permutation)
            affine_rows.append(
                {
                    "affine_stabilizer_id": len(affine_rows),
                    "linear_columns": list(columns),
                    "translation": translation,
                    "translation_pattern": pattern_bits(translation),
                    "component_permutation": component_permutation,
                    "component_permutation_by_pattern": {
                        pattern_bits(source): pattern_bits(point_image[source])
                        for source in gate_support
                    },
                    "canonical_packet_permutation": packet_permutation,
                }
            )
    return gate_support, radicals, packets, affine_rows


def label_summary(
    name: str,
    keys: list[str],
    affine_rows: list[dict[str, Any]],
    packet_rows: dict[int, dict[str, Any]],
    packets: list[int],
    radicals: list[int],
    identity_affine_id: int,
) -> dict[str, Any]:
    survivor_ids = [
        int(row["affine_stabilizer_id"])
        for row in affine_rows
        if canonical_preserves_label(row["canonical_packet_permutation"], packet_rows, packets, keys)
    ]
    active_lift_counts = [
        active_flip_lift_count(row["component_permutation"], radicals, packet_rows, keys)
        for row in affine_rows
    ]
    nonidentity_survivors = [
        affine_id for affine_id in survivor_ids if affine_id != identity_affine_id
    ]
    return {
        "name": name,
        "keys": keys,
        "canonical_affine_survivor_count": len(survivor_ids),
        "canonical_affine_survivor_ids": survivor_ids,
        "surviving_nonidentity_ids": nonidentity_survivors,
        "killed_nonidentity_count": len(affine_rows) - 1 - len(nonidentity_survivors),
        "active_flip_lift_survivor_count": sum(active_lift_counts),
        "active_flip_lift_count_by_affine_histogram": histogram(Counter(active_lift_counts)),
    }


def combination_rows(
    registry: dict[str, list[str]],
    affine_rows: list[dict[str, Any]],
    packet_rows: dict[int, dict[str, Any]],
    packets: list[int],
    radicals: list[int],
    identity_affine_id: int,
) -> list[dict[str, Any]]:
    names = list(registry)
    rows = []
    for size in range(1, len(names) + 1):
        for combo in combinations(names, size):
            rows.append(
                label_summary(
                    "+".join(combo),
                    keys_for(combo, registry),
                    affine_rows,
                    packet_rows,
                    packets,
                    radicals,
                    identity_affine_id,
                )
                | {"axis_names": list(combo)}
            )
    return rows


def inclusion_minimal_identity_sets(rows: list[dict[str, Any]]) -> list[list[str]]:
    identity_sets = [
        tuple(row["axis_names"])
        for row in rows
        if row["canonical_affine_survivor_count"] == 1
    ]
    minimal = []
    for item in sorted(identity_sets, key=lambda value: (len(value), value)):
        item_set = set(item)
        if not any(set(existing).issubset(item_set) for existing in minimal):
            minimal.append(item)
    return [list(item) for item in minimal]


def build_theorem() -> dict[str, Any]:
    lift = load_json(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT)
    charge = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    gate_support, radicals, packets, affine_rows = build_affine_rows()
    packet_rows = {
        int(row["packet_id"]): row
        for row in charge.get("derived", {}).get("charge_frame_rows", [])
        if int(row["packet_id"]) in set(packets)
    }
    identity_affine_ids = [
        int(row["affine_stabilizer_id"])
        for row in affine_rows
        if all(row["canonical_packet_permutation"][packet] == packet for packet in packets)
    ]
    identity_affine_id = identity_affine_ids[0] if len(identity_affine_ids) == 1 else -1

    axis_rows = [
        label_summary(
            name,
            keys,
            affine_rows,
            packet_rows,
            packets,
            radicals,
            identity_affine_id,
        )
        for name, keys in AXIS_FAMILIES.items()
    ]
    atomic_rows = [
        label_summary(
            name,
            keys,
            affine_rows,
            packet_rows,
            packets,
            radicals,
            identity_affine_id,
        )
        for name, keys in ATOMIC_LABELS.items()
    ]
    axis_combo_rows = combination_rows(
        AXIS_FAMILIES,
        affine_rows,
        packet_rows,
        packets,
        radicals,
        identity_affine_id,
    )
    atomic_combo_rows = combination_rows(
        ATOMIC_LABELS,
        affine_rows,
        packet_rows,
        packets,
        radicals,
        identity_affine_id,
    )

    axis_summary_by_name = {row["name"]: row for row in axis_rows}
    atomic_summary_by_name = {row["name"]: row for row in atomic_rows}
    minimal_axis_identity_sets = inclusion_minimal_identity_sets(axis_combo_rows)
    minimal_atomic_identity_sets = inclusion_minimal_identity_sets(atomic_combo_rows)

    nonidentity_breaker_rows = []
    for row in affine_rows:
        affine_id = int(row["affine_stabilizer_id"])
        if affine_id == identity_affine_id:
            continue
        killed_by_axis = [
            name
            for name, keys in AXIS_FAMILIES.items()
            if not canonical_preserves_label(row["canonical_packet_permutation"], packet_rows, packets, keys)
        ]
        killed_by_atomic = [
            name
            for name, keys in ATOMIC_LABELS.items()
            if not canonical_preserves_label(row["canonical_packet_permutation"], packet_rows, packets, keys)
        ]
        nonidentity_breaker_rows.append(
            {
                "affine_stabilizer_id": affine_id,
                "linear_columns": row["linear_columns"],
                "translation_pattern": row["translation_pattern"],
                "killed_by_axis_families": killed_by_axis,
                "preserved_axis_families": [
                    name for name in AXIS_FAMILIES if name not in killed_by_axis
                ],
                "killed_by_atomic_labels": killed_by_atomic,
                "preserved_atomic_labels": [
                    name for name in ATOMIC_LABELS if name not in killed_by_atomic
                ],
            }
        )

    cumulative_chain = []
    accumulated_names: list[str] = []
    prior_survivors = {int(row["affine_stabilizer_id"]) for row in affine_rows}
    for name in ["mass", "clock", "gamma", "sector26", "spectral"]:
        accumulated_names.append(name)
        keys = keys_for(accumulated_names, AXIS_FAMILIES)
        survivors = {
            int(row["affine_stabilizer_id"])
            for row in affine_rows
            if canonical_preserves_label(row["canonical_packet_permutation"], packet_rows, packets, keys)
        }
        cumulative_chain.append(
            {
                "axis_added": name,
                "axis_prefix": list(accumulated_names),
                "canonical_affine_survivor_count": len(survivors),
                "survivor_ids": sorted(survivors),
                "killed_at_this_step_count": len(prior_survivors - survivors),
                "killed_at_this_step_ids": sorted(prior_survivors - survivors)[:64],
            }
        )
        prior_survivors = survivors

    breaker_summary = {
        "identity_affine_id": identity_affine_id,
        "canonical_affine_lift_count": len(affine_rows),
        "nonidentity_affine_lift_count": len(affine_rows) - 1,
        "axis_family_survivor_counts": {
            row["name"]: row["canonical_affine_survivor_count"]
            for row in axis_rows
        },
        "axis_family_active_flip_lift_counts": {
            row["name"]: row["active_flip_lift_survivor_count"]
            for row in axis_rows
        },
        "atomic_label_survivor_counts": {
            row["name"]: row["canonical_affine_survivor_count"]
            for row in atomic_rows
        },
        "atomic_label_active_flip_lift_counts": {
            row["name"]: row["active_flip_lift_survivor_count"]
            for row in atomic_rows
        },
        "axis_kill_incidence": {
            row["name"]: row["killed_nonidentity_count"]
            for row in axis_rows
        },
        "atomic_kill_incidence": {
            row["name"]: row["killed_nonidentity_count"]
            for row in atomic_rows
        },
        "minimal_axis_identity_sets": minimal_axis_identity_sets,
        "minimal_atomic_identity_sets": minimal_atomic_identity_sets,
    }

    checks = {
        "stabilizer_lift_is_certified": lift.get("status")
        == "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_CERTIFIED"
        and lift.get("all_checks_pass") is True,
        "charge_frame_classifier_is_certified": charge.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "affine_lift_rows_match_lift_theorem": len(affine_rows) == 384
        and identity_affine_ids == [0]
        and lift.get("derived", {}).get("graph_action_lift_summary", {}).get(
            "canonical_graph_action_lift_order"
        )
        == 384,
        "axis_family_counts_match_expected_factorization": (
            breaker_summary["axis_family_survivor_counts"]
            == {
                "mass": 2,
                "clock": 48,
                "gamma": 24,
                "sector26": 1,
                "spectral": 2,
            }
        ),
        "active_flip_counts_match_expected_factorization": (
            breaker_summary["axis_family_active_flip_lift_counts"]
            == {
                "mass": 64,
                "clock": 48,
                "gamma": 24576,
                "sector26": 1,
                "spectral": 2,
            }
        ),
        "atomic_counts_identify_true_single_label_breakers": (
            atomic_summary_by_name["sector26_sum"]["canonical_affine_survivor_count"] == 1
            and atomic_summary_by_name["fine_spectral"]["canonical_affine_survivor_count"] == 1
            and atomic_summary_by_name["sector26_delta"]["canonical_affine_survivor_count"] == 384
        ),
        "minimal_axis_identity_sets_are_exact": minimal_axis_identity_sets
        == [["sector26"], ["clock", "spectral"], ["mass", "clock"]],
        "minimal_atomic_identity_sets_are_exact": minimal_atomic_identity_sets
        == [
            ["fine_spectral"],
            ["sector26_sum"],
            ["clock_frame", "spectral_trace"],
            ["mass_frame", "clock_frame"],
            ["mass_frame", "sector26_zero_pair"],
            ["mass_frame", "sector26_zero_touched"],
            ["sector26_zero_pair", "spectral_trace"],
            ["sector26_zero_touched", "spectral_trace"],
        ],
        "every_nonidentity_lift_is_killed_by_some_atomic_label": all(
            row["killed_by_atomic_labels"] for row in nonidentity_breaker_rows
        )
        and len(nonidentity_breaker_rows) == 383,
        "mass_then_clock_cumulative_chain_reaches_identity": cumulative_chain[0][
            "canonical_affine_survivor_count"
        ]
        == 2
        and cumulative_chain[1]["canonical_affine_survivor_count"] == 1,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_label_breaking_factorization",
        "status": status,
        "object": "d20",
        "claim": (
            "The charge-frame rigidity of the full-exposure stabilizer lift factors into explicit "
            "label axes. Mass alone leaves two canonical affine lifts; clock alone leaves 48; gamma "
            "alone leaves 24; spectral trace alone leaves two; the full sector-26 clock family leaves "
            "only identity. At atomic resolution, sector26_clock_sum_mod26 and fine_spectral_charge_key "
            "each individually kill every nonidentity radical-gate lift, while sector26_clock_delta_mod26 "
            "kills none."
        ),
        "definition": {
            "axis_family": "A named group of packet labels: mass, clock, gamma, sector26, or spectral.",
            "atomic_label": "A single irreducible label or small inseparable label pair inside an axis family.",
            "killed_lift": "A canonical affine packet lift that fails to preserve a label on all 20 full-exposure packets.",
            "minimal_identity_set": "A label-axis subset whose survivor set is identity and no proper subset already has identity survivor set.",
        },
        "inputs": {
            "full_exposure_radical_gate_stabilizer_lift_report": {
                "path": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
            },
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
        },
        "derived": {
            "breaker_summary": breaker_summary,
            "axis_family_rows": axis_rows,
            "atomic_label_rows": atomic_rows,
            "axis_combination_rows": axis_combo_rows,
            "atomic_combination_identity_rows": [
                row for row in atomic_combo_rows if row["canonical_affine_survivor_count"] == 1
            ],
            "cumulative_axis_chain_mass_clock_gamma_sector26_spectral": cumulative_chain,
            "nonidentity_breaker_rows": nonidentity_breaker_rows,
            "nonidentity_breaker_rows_sha256": sha_json(nonidentity_breaker_rows),
            "full_exposure_packet_label_rows": [
                {
                    "packet_id": packet,
                    "local_pattern": pattern_bits(gate_support[radicals.index(packet // 2)]),
                    "mass_frame": packet_rows[packet]["mass_frame"],
                    "clock_frame": packet_rows[packet]["clock_frame"],
                    "gamma_frame": packet_rows[packet]["gamma_frame"],
                    "sector26_clock_sum_mod26": packet_rows[packet]["sector26_clock_sum_mod26"],
                    "sector26_clock_delta_mod26": packet_rows[packet]["sector26_clock_delta_mod26"],
                    "sector26_clock_zero_pair": packet_rows[packet]["sector26_clock_zero_pair"],
                    "sector26_clock_zero_touched": packet_rows[packet]["sector26_clock_zero_touched"],
                    "adjacency_trace": packet_rows[packet]["adjacency_trace"],
                    "laplacian_trace": packet_rows[packet]["laplacian_trace"],
                    "fine_spectral_charge_key": packet_rows[packet]["fine_spectral_charge_key"],
                }
                for packet in packets
            ],
        },
        "interpretation": {
            "what_this_proves": [
                "the labelled full-exposure screen is rigid because sector-26 sum and fine spectral labels are complete separators on the 384 canonical lifts",
                "mass and spectral trace have the same coarse strength, each leaving one nonidentity affine ambiguity",
                "clock is weaker alone but pairs with mass or spectral trace to force identity",
                "gamma is a real but incomplete breaker at this factorization level",
                "sector26 delta is not a breaker on canonical lifts; the sector-26 sum is the decisive sector-26 invariant",
            ],
            "what_this_does_not_prove": (
                "This only factors the already-certified radical-gate lift ansatz. It does not classify "
                "automorphisms unrelated to the 384 affine gate stabilizers."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the minimal label breakers to define a canonical labelled D20 full-exposure coordinate "
            "frame and test whether packet 239 is selected by an intrinsic fixed-point rule rather than by "
            "external naming."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_label_breaking_factorization_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify stabilizer-lift and charge-frame classifier inputs",
            "recompute all 384 canonical radical-gate lifts",
            "count survivor sets for mass, clock, gamma, sector-26, and spectral axis families",
            "compute inclusion-minimal identity-generating axis and atomic-label subsets",
            "emit a per-nonidentity-lift table of labels that break each lift",
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
