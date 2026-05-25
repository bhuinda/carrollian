from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_rank10_tenfold_alignment"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_graph"
    / "report.json"
)
PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_kernel_packet_tenfold_way"
    / "report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_spectral_charge_table"
    / "report.json"
)

RADICAL_COORDINATE_COUNT = 8
ACTIVE_LEFT_COORD = 8
ACTIVE_RIGHT_COORD = 9
KERNEL_COORDINATE_COUNT = 10
KERNEL_SIMPLE_SOURCE_BITS = [0, 1, 2, 3, 4, 6, 7, 8]


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


def bit_ids(mask: int, width: int) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def gf2_rank(vectors: list[int], width: int) -> int:
    basis = [0] * width
    rank = 0
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot] == 0:
                basis[pivot] = value
                rank += 1
                break
            value ^= basis[pivot]
    return rank


def mask_from_coord(coord: int) -> int:
    mask = 0
    for coord_idx, source_bit in enumerate(KERNEL_SIMPLE_SOURCE_BITS):
        if (coord >> coord_idx) & 1:
            mask ^= 1 << source_bit
    if (coord >> ACTIVE_LEFT_COORD) & 1:
        mask ^= (1 << 5) | (1 << 9)
    if (coord >> ACTIVE_RIGHT_COORD) & 1:
        mask ^= (1 << 5) | (1 << 10)
    return mask


def radical_support(radical_character: int) -> list[int]:
    return bit_ids(radical_character, RADICAL_COORDINATE_COUNT)


def radical_gate(radical_character: int) -> bool:
    x2 = bool((radical_character >> 2) & 1)
    x3 = bool((radical_character >> 3) & 1)
    x5 = bool((radical_character >> 5) & 1)
    return x2 or (x3 and x5)


def variable_pattern(radical_character: int, axes: list[int]) -> str:
    return "".join("1" if (radical_character >> axis) & 1 else "0" for axis in axes)


def pattern_bits(pattern: int, width: int) -> str:
    return "".join("1" if (pattern >> idx) & 1 else "0" for idx in range(width))


def build_theorem() -> dict[str, Any]:
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)
    tenfold = load_json(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT)
    spectral = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)

    graph_derived = graph.get("derived", {})
    graph_summary = graph_derived.get("graph_summary", {})
    component_rows = graph_derived.get("component_rows", [])
    tenfold_derived = tenfold.get("derived", {})
    packet_summary = tenfold_derived.get("packet_summary", {})
    tenfold_witness = tenfold_derived.get("tenfold_way_witness", {})
    packet_by_id = {
        int(row["packet_id"]): row
        for row in tenfold_derived.get("packet_rows", [])
    }
    spectral_by_id = {
        int(row["packet_id"]): row
        for row in spectral.get("derived", {}).get("packet_spectral_charge_rows", [])
    }

    component_alignment_rows = []
    radical_anchors = []
    mode_coords = []
    mode_masks = []
    for component in component_rows:
        left, right = [int(packet_id) for packet_id in component["packet_pair"]]
        left_packet = packet_by_id[left]
        right_packet = packet_by_id[right]
        radical = int(left_packet["radical_character"])
        radical_anchors.append(radical)
        component_mode_coords = []
        component_mode_masks = []
        for packet_id in (left, right):
            packet = packet_by_id[packet_id]
            active_sigma = int(packet["active_sigma"])
            for active_tau in (0, 1):
                coord = radical | (active_sigma << ACTIVE_LEFT_COORD) | (
                    active_tau << ACTIVE_RIGHT_COORD
                )
                component_mode_coords.append(coord)
                component_mode_masks.append(mask_from_coord(coord))
        mode_coords.extend(component_mode_coords)
        mode_masks.extend(component_mode_masks)
        component_alignment_rows.append(
            {
                "packet_pair": [left, right],
                "radical_character": radical,
                "radical_binary": format(radical, "08b"),
                "radical_support": radical_support(radical),
                "relative_variable_pattern_2357": variable_pattern(radical, [2, 3, 5, 7]),
                "active_sigma_values": [
                    int(left_packet["active_sigma"]),
                    int(right_packet["active_sigma"]),
                ],
                "active_tau_values_per_packet": [0, 1],
                "kernel_coordinate_plane": sorted(component_mode_coords),
                "mode_masks_from_coordinate_plane": sorted(component_mode_masks),
                "packet_mode_masks": sorted(
                    [int(mask) for mask in left_packet["mode_masks"]]
                    + [int(mask) for mask in right_packet["mode_masks"]]
                ),
                "graph_block_matrix": component["block_matrix"],
                "gamma8_touched_pair": [
                    bool(spectral_by_id[left]["gamma8_touched"]),
                    bool(spectral_by_id[right]["gamma8_touched"]),
                ],
                "tenfold_canonical_classes": sorted(
                    {
                        spectral_by_id[left]["tenfold_canonical_class"],
                        spectral_by_id[right]["tenfold_canonical_class"],
                    }
                ),
                "optional_active_hamiltonian_classes": sorted(
                    {
                        spectral_by_id[left]["tenfold_optional_active_hamiltonian_class"],
                        spectral_by_id[right]["tenfold_optional_active_hamiltonian_class"],
                    }
                ),
            }
        )

    radical_anchors = sorted(radical_anchors)
    common_core = (1 << RADICAL_COORDINATE_COUNT) - 1
    for radical in radical_anchors:
        common_core &= radical
    radical_relative_vectors = [radical ^ common_core for radical in radical_anchors]
    all_radical_variation = 0
    for value in radical_relative_vectors:
        all_radical_variation |= value
    variable_radical_axes = bit_ids(all_radical_variation, RADICAL_COORDINATE_COUNT)
    fixed_one_radical_axes = bit_ids(common_core, RADICAL_COORDINATE_COUNT)
    fixed_zero_radical_axes = [
        axis
        for axis in range(RADICAL_COORDINATE_COUNT)
        if axis not in fixed_one_radical_axes and axis not in variable_radical_axes
    ]

    expected_radicals = sorted(
        common_core
        | sum(
            (1 << axis)
            for idx, axis in enumerate(variable_radical_axes)
            if (pattern >> idx) & 1
        )
        for pattern in range(1 << len(variable_radical_axes))
        if radical_gate(
            common_core
            | sum(
                (1 << axis)
                for idx, axis in enumerate(variable_radical_axes)
                if (pattern >> idx) & 1
            )
        )
    )
    excluded_variable_patterns = [
        pattern_bits(pattern, len(variable_radical_axes))
        for pattern in range(1 << len(variable_radical_axes))
        if not radical_gate(
            common_core
            | sum((1 << axis) for idx, axis in enumerate(variable_radical_axes) if (pattern >> idx) & 1)
        )
    ]

    active_axis_vectors = [1 << ACTIVE_LEFT_COORD, 1 << ACTIVE_RIGHT_COORD]
    affine_direction_vectors = radical_relative_vectors + active_axis_vectors
    affine_direction_rank = gf2_rank(affine_direction_vectors, KERNEL_COORDINATE_COUNT)
    linear_span_rank = gf2_rank(mode_coords, KERNEL_COORDINATE_COUNT)
    radical_affine_rank = gf2_rank(radical_relative_vectors, RADICAL_COORDINATE_COUNT)
    radical_linear_rank = gf2_rank(radical_anchors, RADICAL_COORDINATE_COUNT)
    packet_pairs_from_radicals = [[2 * radical, 2 * radical + 1] for radical in radical_anchors]
    all_packet_mode_masks_match = all(
        row["mode_masks_from_coordinate_plane"] == row["packet_mode_masks"]
        for row in component_alignment_rows
    )

    alignment_summary = {
        "kernel_dimension": int(packet_summary.get("kernel_dimension", 0)),
        "component_count": len(component_rows),
        "component_count_matches_kernel_dimension": len(component_rows)
        == int(packet_summary.get("kernel_dimension", -1)),
        "radical_anchor_count": len(radical_anchors),
        "radical_anchors": radical_anchors,
        "radical_anchor_binary": [format(radical, "08b") for radical in radical_anchors],
        "common_radical_core": common_core,
        "common_radical_core_binary": format(common_core, "08b"),
        "fixed_one_radical_axes": fixed_one_radical_axes,
        "fixed_zero_radical_axes": fixed_zero_radical_axes,
        "variable_radical_axes": variable_radical_axes,
        "free_active_axes": [ACTIVE_LEFT_COORD, ACTIVE_RIGHT_COORD],
        "radical_affine_direction_rank": radical_affine_rank,
        "radical_linear_span_rank": radical_linear_rank,
        "full_mode_affine_direction_rank": affine_direction_rank,
        "full_mode_linear_span_rank": linear_span_rank,
        "canonical_rank10_axis_basis": False,
        "basis_failure_reason": (
            "The ten graph components match the kernel dimension numerically, but their coordinate "
            "directions span only four radical axes plus the two active axes."
        ),
    }
    boolean_gate_witness = {
        "fixed_equations": {
            "radical_axes_equal_one": fixed_one_radical_axes,
            "radical_axes_equal_zero": fixed_zero_radical_axes,
        },
        "variable_radical_axes": variable_radical_axes,
        "condition": "x2 or (x3 and x5)",
        "support_radical_count": len(radical_anchors),
        "expected_radicals_from_gate": expected_radicals,
        "excluded_variable_patterns_2357": excluded_variable_patterns,
        "is_affine_subspace": False,
        "not_affine_reason": "The radical support has 10 points; an affine F2-subspace would have power-of-two size.",
    }
    tenfold_alignment = {
        "kernel_split": "8 radical spectator axes plus 2 active Cl(1,1) axes",
        "canonical_module_class": tenfold_witness.get("canonical_module_class"),
        "optional_active_hamiltonian_class": tenfold_witness.get(
            "optional_active_hamiltonian_class"
        ),
        "active_axes_are_free_in_every_component": True,
        "graph_operator_axis": "active_sigma",
        "packet_internal_axis": "active_tau",
        "moving_radical_axis_count": len(variable_radical_axes),
        "fixed_radical_axis_count": len(fixed_one_radical_axes) + len(fixed_zero_radical_axes),
    }

    checks = {
        "full_exposure_packet_propagation_graph_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "projective_kernel_packet_tenfold_way_is_certified": tenfold.get("status")
        == "D20_PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_CERTIFIED"
        and tenfold.get("all_checks_pass") is True,
        "projective_packet_spectral_charge_table_is_certified": spectral.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and spectral.get("all_checks_pass") is True,
        "component_count_matches_rank10_kernel_dimension": alignment_summary[
            "component_count_matches_kernel_dimension"
        ]
        is True
        and alignment_summary["component_count"] == 10,
        "doublets_are_active_partner_planes": packet_pairs_from_radicals
        == graph_summary.get("active_partner_pairs")
        and all(row["active_sigma_values"] == [0, 1] for row in component_alignment_rows),
        "active_plane_mode_masks_match_packet_model": all_packet_mode_masks_match,
        "radical_core_and_variable_axes_are_certified": common_core == 83
        and fixed_one_radical_axes == [0, 1, 4, 6]
        and fixed_zero_radical_axes == []
        and variable_radical_axes == [2, 3, 5, 7],
        "full_exposure_boolean_gate_matches_radical_support": radical_anchors
        == expected_radicals
        and len(radical_anchors) == 10
        and excluded_variable_patterns == ["0000", "0100", "0010", "0001", "0101", "0011"],
        "component_support_is_not_rank10_basis": alignment_summary[
            "canonical_rank10_axis_basis"
        ]
        is False
        and radical_affine_rank == 4
        and affine_direction_rank == 6
        and linear_span_rank == 7,
        "tenfold_active_block_is_preserved": tenfold_alignment["canonical_module_class"]
        == "AI"
        and tenfold_alignment["optional_active_hamiltonian_class"] == "BDI"
        and tenfold_alignment["active_axes_are_free_in_every_component"] is True,
        "packet239_alignment_is_238_239_with_radical119": any(
            row["packet_pair"] == [238, 239]
            and row["radical_character"] == 119
            and row["relative_variable_pattern_2357"] == "1010"
            for row in component_alignment_rows
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_rank10_tenfold_alignment",
        "status": status,
        "object": "d20",
        "claim": (
            "The ten full-exposure propagation doublets match the rank-10 kernel dimension by count, "
            "but they do not form a canonical ten-axis basis. Each doublet is an active two-packet plane "
            "over a fixed radical character. The ten radical anchors have common core 83, vary only on "
            "radical axes 2, 3, 5, and 7, and satisfy the nonlinear support gate x2 or (x3 and x5). "
            "Thus the full-exposure graph is a ten-component tenfold-facing screen, not the full rank-10 "
            "coordinate cube."
        ),
        "definition": {
            "component_anchor": "The shared radical character r for an active-partner packet pair [2r,2r+1].",
            "active_plane": "The four kernel coordinates r + sigma*e8 + tau*e9 for sigma,tau in F2.",
            "rank10_basis_test": "Whether the component coordinate directions span all ten kernel axes.",
            "tenfold_alignment": "Compatibility with the certified 8 radical plus 2 active Cl(1,1) split.",
        },
        "inputs": {
            "full_exposure_packet_propagation_graph_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
            },
            "projective_kernel_packet_tenfold_way_report": {
                "path": rel(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT),
                "sha256": sha_file(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT),
            },
            "projective_packet_spectral_charge_table_report": {
                "path": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
            },
        },
        "derived": {
            "alignment_summary": alignment_summary,
            "boolean_gate_witness": boolean_gate_witness,
            "tenfold_alignment": tenfold_alignment,
            "component_alignment_rows": component_alignment_rows,
            "histograms": {
                "radical_support_size": histogram(
                    Counter(len(radical_support(radical)) for radical in radical_anchors)
                ),
                "gamma8_touched_pair": histogram(
                    Counter(
                        tuple(row["gamma8_touched_pair"]) for row in component_alignment_rows
                    )
                ),
                "relative_variable_pattern_2357": histogram(
                    Counter(
                        row["relative_variable_pattern_2357"]
                        for row in component_alignment_rows
                    )
                ),
            },
            "component_alignment_rows_sha256": sha_json(component_alignment_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the ten graph components are active planes in the certified 8+2 kernel coordinate split",
                "the component count equals the rank-10 kernel dimension only as a count, not as a basis",
                "full exposure is cut out by a fixed radical core plus a nonlinear four-axis radical gate",
                "packet 239 is the active-sigma half of the radical-119 component [238,239]",
            ],
            "what_this_does_not_prove": (
                "This does not identify the ten full-exposure doublets with the ten coordinate axes. "
                "It certifies the opposite: the moving support has rank 6 in the 10-coordinate kernel."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify the automorphism/stabilizer of the full-exposure radical gate with fixed core "
            "83 and condition x2 or (x3 and x5)."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_rank10_tenfold_alignment_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify graph, tenfold packet, and packet spectral inputs",
            "map each graph doublet to its radical anchor and active sigma/tau coordinate plane",
            "verify packet mode masks agree with the rank-10 coordinate model",
            "compute common radical core, moving radical axes, affine direction rank, and linear span rank",
            "verify the nonlinear full-exposure radical gate and the non-basis result",
            "verify AI/BDI tenfold labels remain aligned with the active Cl(1,1) block",
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
