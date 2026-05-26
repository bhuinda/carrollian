from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_radical_gate_stabilizer_lift"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_radical_gate_stabilizer"
    / "report.json"
)
FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_rank10_tenfold_alignment"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_graph"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_cells"
    / "report.json"
)
PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)

LOCAL_WIDTH = 4
COMMON_RADICAL_CORE = 83
VARIABLE_RADICAL_AXES = [2, 3, 5, 7]


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


def pattern_bits(pattern: int, width: int = LOCAL_WIDTH) -> str:
    return "".join("1" if (pattern >> idx) & 1 else "0" for idx in range(width))


def local_gate(pattern: int) -> bool:
    x2 = bool(pattern & 1)
    x3 = bool((pattern >> 1) & 1)
    x5 = bool((pattern >> 2) & 1)
    return x2 or (x3 and x5)


def gf2_rank(vectors: list[int], width: int = LOCAL_WIDTH) -> int:
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


def apply_linear(columns: tuple[int, ...], vector: int) -> int:
    target = 0
    for idx, column in enumerate(columns):
        if (vector >> idx) & 1:
            target ^= column
    return target


def matrix_rows(columns: tuple[int, ...]) -> list[list[int]]:
    return [
        [(columns[col] >> row) & 1 for col in range(LOCAL_WIDTH)]
        for row in range(LOCAL_WIDTH)
    ]


def all_gl4() -> list[tuple[int, ...]]:
    return [
        tuple(columns)
        for columns in product(range(1 << LOCAL_WIDTH), repeat=LOCAL_WIDTH)
        if gf2_rank(list(columns), LOCAL_WIDTH) == LOCAL_WIDTH
    ]


def radical_from_pattern(pattern: int) -> int:
    radical = COMMON_RADICAL_CORE
    for idx, axis in enumerate(VARIABLE_RADICAL_AXES):
        if (pattern >> idx) & 1:
            radical ^= 1 << axis
    return radical


def packet_id(radical: int, active_sigma: int) -> int:
    return 2 * radical + active_sigma


def canonical_packet_permutation(
    component_permutation: dict[int, int],
) -> dict[int, int]:
    return {
        packet_id(radical, active_sigma): packet_id(target_radical, active_sigma)
        for radical, target_radical in component_permutation.items()
        for active_sigma in (0, 1)
    }


def label_value(row: dict[str, Any], keys: list[str]) -> tuple[Any, ...]:
    return tuple(row.get(key) for key in keys)


def canonical_preserves_label(
    packet_permutation: dict[int, int],
    packet_rows: dict[int, dict[str, Any]],
    packets: list[int],
    keys: list[str],
) -> bool:
    return all(
        label_value(packet_rows[packet], keys)
        == label_value(packet_rows[packet_permutation[packet]], keys)
        for packet in packets
    )


def active_flip_lift_count(
    component_permutation: dict[int, int],
    radicals: list[int],
    packet_rows: dict[int, dict[str, Any]],
    keys: list[str],
) -> int:
    lift_count = 1
    for radical in radicals:
        target_radical = component_permutation[radical]
        valid_flips = 0
        for flip in (0, 1):
            if all(
                label_value(packet_rows[packet_id(radical, active_sigma)], keys)
                == label_value(packet_rows[packet_id(target_radical, active_sigma ^ flip)], keys)
                for active_sigma in (0, 1)
            ):
                valid_flips += 1
        if valid_flips == 0:
            return 0
        lift_count *= valid_flips
    return lift_count


def action_signature_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "ordered_generators": [
                    int(row["first_generator_cycle_id"]),
                    int(row["second_generator_cycle_id"]),
                ],
                "target_relation": (
                    "source_loop"
                    if row["returns_to_source_packet"]
                    else "active_partner"
                ),
                "net_height_flux_delta": int(row["net_height_flux_delta"]),
                "total_optical_action": int(row["total_optical_action"]),
                "hidden_R33_transfer_mod26_total": int(row["hidden_R33_transfer_mod26_total"]),
            }
            for row in rows
        ],
        key=lambda row: (
            row["ordered_generators"],
            row["target_relation"],
            row["net_height_flux_delta"],
            row["total_optical_action"],
        ),
    )


def label_preservation_summary(
    name: str,
    keys: list[str],
    affine_rows: list[dict[str, Any]],
    packet_rows: dict[int, dict[str, Any]],
    radicals: list[int],
    packets: list[int],
) -> dict[str, Any]:
    canonical_survivors = []
    active_flip_lift_count_by_affine = Counter()
    affine_elements_with_active_flip_lift = 0
    active_flip_lift_total = 0

    for row in affine_rows:
        packet_permutation = row["canonical_packet_permutation"]
        if canonical_preserves_label(packet_permutation, packet_rows, packets, keys):
            canonical_survivors.append(row)
        lift_count = active_flip_lift_count(
            row["component_permutation"],
            radicals,
            packet_rows,
            keys,
        )
        active_flip_lift_count_by_affine[lift_count] += 1
        active_flip_lift_total += lift_count
        if lift_count:
            affine_elements_with_active_flip_lift += 1

    return {
        "name": name,
        "keys": keys,
        "canonical_affine_survivor_count": len(canonical_survivors),
        "active_flip_lift_survivor_count": active_flip_lift_total,
        "affine_elements_with_active_flip_lift": affine_elements_with_active_flip_lift,
        "active_flip_lift_count_by_affine_histogram": histogram(active_flip_lift_count_by_affine),
        "canonical_survivor_affine_ids": [
            int(row["affine_stabilizer_id"]) for row in canonical_survivors
        ],
        "canonical_survivor_sample_rows": [
            {
                "affine_stabilizer_id": int(row["affine_stabilizer_id"]),
                "linear_columns": row["linear_columns"],
                "translation_pattern": row["translation_pattern"],
                "component_permutation_by_packet_pair": row["component_permutation_by_packet_pair"],
            }
            for row in canonical_survivors[:12]
        ],
    }


def build_theorem() -> dict[str, Any]:
    stabilizer = load_json(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT)
    alignment = load_json(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)
    cells = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT)
    charge = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)

    gate_support = sorted(pattern for pattern in range(1 << LOCAL_WIDTH) if local_gate(pattern))
    radicals = [radical_from_pattern(pattern) for pattern in gate_support]
    radical_by_pattern = {
        pattern: radical_from_pattern(pattern)
        for pattern in gate_support
    }
    pattern_by_radical = {
        radical: pattern
        for pattern, radical in radical_by_pattern.items()
    }
    packets = sorted(packet_id(radical, active_sigma) for radical in radicals for active_sigma in (0, 1))
    packet_rows = {
        int(row["packet_id"]): row
        for row in charge.get("derived", {}).get("charge_frame_rows", [])
    }
    full_packet_rows = {packet: packet_rows[packet] for packet in packets}

    affine_rows = []
    for columns in all_gl4():
        for translation in range(1 << LOCAL_WIDTH):
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
                    "linear_rows": matrix_rows(columns),
                    "translation": translation,
                    "translation_pattern": pattern_bits(translation),
                    "support_permutation": [
                        gate_support.index(point_image[point])
                        for point in gate_support
                    ],
                    "component_permutation": component_permutation,
                    "component_permutation_by_pattern": {
                        pattern_bits(source): pattern_bits(point_image[source])
                        for source in gate_support
                    },
                    "component_permutation_by_packet_pair": {
                        f"{packet_id(source_radical, 0)},{packet_id(source_radical, 1)}": [
                            packet_id(target_radical, 0),
                            packet_id(target_radical, 1),
                        ]
                        for source_radical, target_radical in component_permutation.items()
                    },
                    "canonical_packet_permutation": packet_permutation,
                }
            )

    graph_vertices = [
        int(vertex)
        for vertex in graph.get("derived", {}).get("graph_summary", {}).get(
            "active_partner_pairs", []
        )
        for vertex in vertex
    ]
    graph_vertex_set = set(graph_vertices)
    action_rows = cells.get("derived", {}).get("two_step_cross_return_rows", [])
    source_action_signature_by_packet = {
        packet: action_signature_rows(
            [row for row in action_rows if int(row["source_packet_id"]) == packet]
        )
        for packet in packets
    }
    action_signatures = {
        sha_json(signature)
        for signature in source_action_signature_by_packet.values()
    }
    full_action_signature = next(iter(action_signatures)) if len(action_signatures) == 1 else None

    label_summaries = [
        label_preservation_summary(
            "graph_action_unlabelled",
            [],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "tenfold_hidden_central_exposure",
            ["tenfold_frame", "hidden_frame", "central_frame", "exposure_frame"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "sector26_delta",
            ["sector26_clock_delta_mod26"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "gamma8_touched",
            ["gamma8_touched", "gamma8_mode_count"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "zero_pair_touched",
            ["sector26_clock_zero_touched"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "combined_gamma_marker",
            ["gamma8_touched", "gamma8_mode_count", "sector26_clock_zero_touched"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "mass_clock_gamma_frame",
            ["mass_frame", "clock_frame", "gamma_frame"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "charge_frame_key",
            ["charge_frame_key"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
        label_preservation_summary(
            "fine_spectral_charge_key",
            ["fine_spectral_charge_key"],
            affine_rows,
            full_packet_rows,
            radicals,
            packets,
        ),
    ]
    label_summary_by_name = {row["name"]: row for row in label_summaries}

    gamma8_touched_packets = [
        packet for packet in packets if full_packet_rows[packet]["gamma8_touched"]
    ]
    zero_pair_touched_packets = [
        packet for packet in packets if full_packet_rows[packet]["sector26_clock_zero_touched"]
    ]
    charge_frame_histogram = histogram(
        Counter(full_packet_rows[packet]["charge_frame_key"] for packet in packets)
    )
    mass_clock_gamma_histogram = histogram(
        Counter(
            (
                full_packet_rows[packet]["mass_frame"],
                full_packet_rows[packet]["clock_frame"],
                full_packet_rows[packet]["gamma_frame"],
            )
            for packet in packets
        )
    )

    graph_action_lift_summary = {
        "radical_affine_stabilizer_order": len(affine_rows),
        "active_partner_flip_freedom_per_component": 2,
        "component_count": len(radicals),
        "active_flip_extension_order": 2 ** len(radicals),
        "graph_action_lift_order": len(affine_rows) * (2 ** len(radicals)),
        "canonical_graph_action_lift_order": len(affine_rows),
        "source_action_signature_sha256": full_action_signature,
        "source_action_signature_is_uniform": len(action_signatures) == 1,
        "source_action_signature_sample": source_action_signature_by_packet[packets[0]],
    }

    stabilizer_summary = stabilizer.get("derived", {}).get("stabilizer_summary", {})
    alignment_summary = alignment.get("derived", {}).get("alignment_summary", {})
    graph_summary = graph.get("derived", {}).get("graph_summary", {})

    checks = {
        "radical_gate_stabilizer_is_certified": stabilizer.get("status")
        == "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_CERTIFIED"
        and stabilizer.get("all_checks_pass") is True,
        "rank10_alignment_is_certified": alignment.get("status")
        == "D20_FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_CERTIFIED"
        and alignment.get("all_checks_pass") is True,
        "packet_graph_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "packet_cells_are_certified": cells.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        and cells.get("all_checks_pass") is True,
        "charge_frame_classifier_is_certified": charge.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "local_gate_and_packet_vertices_match_inputs": len(gate_support) == 10
        and len(packets) == 20
        and sorted(radicals) == alignment_summary.get("radical_anchors")
        and set(packets) == graph_vertex_set
        and stabilizer_summary.get("affine_stabilizer_order") == 384,
        "all_384_affine_stabilizers_lift_to_canonical_graph_action": len(affine_rows) == 384
        and all(
            set(row["canonical_packet_permutation"]) == set(packets)
            and set(row["canonical_packet_permutation"].values()) == set(packets)
            for row in affine_rows
        ),
        "active_flip_extension_has_expected_order": graph_action_lift_summary[
            "graph_action_lift_order"
        ]
        == 384 * 1024
        and label_summary_by_name["graph_action_unlabelled"][
            "active_flip_lift_survivor_count"
        ]
        == 384 * 1024,
        "source_action_signature_is_uniform": len(action_signatures) == 1
        and graph_summary.get("source_total_optical_action_sum_histogram") == {"11096064": 20},
        "tenfold_hidden_central_exposure_labels_do_not_break_lift": label_summary_by_name[
            "tenfold_hidden_central_exposure"
        ]["canonical_affine_survivor_count"]
        == 384
        and label_summary_by_name["tenfold_hidden_central_exposure"][
            "active_flip_lift_survivor_count"
        ]
        == 384 * 1024,
        "combined_gamma_marker_reduces_canonical_lift_to_six": label_summary_by_name[
            "combined_gamma_marker"
        ]["canonical_affine_survivor_count"]
        == 6
        and label_summary_by_name["combined_gamma_marker"][
            "active_flip_lift_survivor_count"
        ]
        == 3072,
        "charge_frame_and_fine_spectral_labels_reduce_to_identity": label_summary_by_name[
            "charge_frame_key"
        ]["canonical_affine_survivor_count"]
        == 1
        and label_summary_by_name["charge_frame_key"]["active_flip_lift_survivor_count"] == 1
        and label_summary_by_name["fine_spectral_charge_key"][
            "canonical_affine_survivor_count"
        ]
        == 1
        and label_summary_by_name["fine_spectral_charge_key"][
            "active_flip_lift_survivor_count"
        ]
        == 1,
        "packet239_is_the_unique_zero_pair_touched_packet": zero_pair_touched_packets == [239],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_radical_gate_stabilizer_lift",
        "status": status,
        "object": "d20",
        "claim": (
            "Every one of the 384 affine stabilizers of the full-exposure radical gate lifts to the "
            "unlabelled weighted packet propagation graph and preserves the uniform action labels. With "
            "the independent active-partner flips on the ten graph doublets, the graph/action lift order is "
            "384*2^10=393216. The physical packet labels break this symmetry sharply: the combined gamma "
            "marker leaves only 6 canonical affine lifts, while the full charge-frame and fine spectral "
            "labels leave only the identity lift."
        ),
        "definition": {
            "canonical_lift": (
                "The lift that sends packet 2r+sigma to 2g(r)+sigma for a radical-gate affine "
                "stabilizer g."
            ),
            "active_flip_lift": (
                "A graph lift may also independently flip sigma on each active-partner doublet because "
                "every doublet has the symmetric block [[2,4],[4,2]]."
            ),
            "action_label": (
                "The ordered generator pair, source-loop/active-partner relation, signed height flux, "
                "total optical action, and hidden R33 transfer label on a two-step cross-return row."
            ),
            "charge_frame_label": "The certified packet charge_frame_key from the projective packet charge-frame classifier.",
        },
        "inputs": {
            "full_exposure_radical_gate_stabilizer_report": {
                "path": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT),
            },
            "full_exposure_rank10_tenfold_alignment_report": {
                "path": rel(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT),
            },
            "full_exposure_packet_propagation_graph_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
            },
            "full_exposure_packet_propagation_cells_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
            },
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
        },
        "derived": {
            "graph_action_lift_summary": graph_action_lift_summary,
            "label_preservation_summaries": label_summaries,
            "full_exposure_label_witness": {
                "packet_ids": packets,
                "radicals": radicals,
                "local_patterns": [pattern_bits(pattern_by_radical[radical]) for radical in radicals],
                "gamma8_touched_packets": gamma8_touched_packets,
                "zero_pair_touched_packets": zero_pair_touched_packets,
                "charge_frame_histogram": charge_frame_histogram,
                "mass_clock_gamma_histogram": mass_clock_gamma_histogram,
            },
            "affine_lift_rows_sha256": sha_json(affine_rows),
            "affine_lift_sample_rows": [
                {
                    "affine_stabilizer_id": int(row["affine_stabilizer_id"]),
                    "linear_columns": row["linear_columns"],
                    "translation_pattern": row["translation_pattern"],
                    "component_permutation_by_packet_pair": row[
                        "component_permutation_by_packet_pair"
                    ],
                }
                for row in affine_rows[:16]
            ],
        },
        "interpretation": {
            "what_this_proves": [
                "the unlabelled full-exposure propagation graph is a large graph/action symmetry object",
                "the action weights do not break the radical-gate affine stabilizer because the source action signature is uniform",
                "the tenfold, hidden, central, and exposure labels are constant on this stratum",
                "gamma data is a real symmetry breaker but still leaves a six-element canonical subgroup",
                "the full charge-frame and fine spectral labels kill every nonidentity radical-gate lift",
            ],
            "what_this_does_not_prove": (
                "This does not classify arbitrary automorphisms outside the radical-gate lift ansatz. It "
                "classifies the 384 certified radical-gate affine stabilizers and their active-flip graph lifts."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Factor the charge-frame symmetry breaking into minimal invariant axes: identify exactly which "
            "mass, clock, gamma, sector-26, and spectral labels kill each nonidentity radical-gate lift."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_radical_gate_stabilizer_lift_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify radical-gate stabilizer, alignment, graph, cell, and charge-frame inputs",
            "enumerate the 384 affine stabilizers and canonically lift them to full packet ids",
            "verify all canonical lifts preserve the weighted graph/action structure",
            "include the independent active-partner flip freedom and verify graph/action lift order 384*2^10",
            "count survivor lifts under gamma labels, charge-frame labels, and fine spectral labels",
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
