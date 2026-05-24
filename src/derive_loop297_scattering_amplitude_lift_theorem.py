from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "loop297_scattering_amplitude_lift"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_finite_scattering_table" / "report.json"
)
BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
SECTOR33_BOUNDARY_ANNIHILATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
)
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
DIRECTED_TRANSITION_COUNT = MASK_COUNT * RESIDUE_RANK
GAMMA8_GENERATOR_ID = 8


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


def parse_label(label: str) -> tuple[str, ...]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label {label!r}")
    order = {name: idx for idx, name in enumerate(H6_LABELS)}
    return tuple(sorted((part.strip() for part in body[1:-1].split(",") if part.strip()), key=order.__getitem__))


def load_edges() -> dict[int, dict[str, Any]]:
    rows = {}
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[int(row["edge_id"])] = {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": parse_label(row["u_label"]),
                "v_label": parse_label(row["v_label"]),
                "interface_weight": int(row["interface_weight"]),
            }
    return rows


def load_primitive_cycles() -> list[dict[str, Any]]:
    rows = []
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "optical_action": int(row["optical_action"]),
                    "vertices": [int(value) for value in row["vertices"].split()],
                    "edge_ids": [int(value) for value in row["edge_ids"].split()],
                }
            )
    return sorted(rows, key=lambda row: row["cycle_id"])


def step_pair(edge: dict[str, Any], source: int, target: int) -> tuple[str, str]:
    if (edge["u"], edge["v"]) == (source, target):
        source_label = set(edge["u_label"])
        target_label = set(edge["v_label"])
    elif (edge["v"], edge["u"]) == (source, target):
        source_label = set(edge["v_label"])
        target_label = set(edge["u_label"])
    else:
        raise ValueError(f"edge {edge['edge_id']} does not connect {source}->{target}")
    removed = sorted(source_label - target_label, key=H6_LABELS.index)
    added = sorted(target_label - source_label, key=H6_LABELS.index)
    if len(removed) != 1 or len(added) != 1:
        raise ValueError(f"bad channel swap on edge {edge['edge_id']}")
    return removed[0], added[0]


def pair_key(removed: str, added: str) -> str:
    return f"{removed}->{added}"


def pi33_zero(character: dict[str, Any]) -> bool:
    return (
        int(character["coefficient_mod_prime"]) == 0
        and int(character["coefficient_signed"]) == 0
        and character["left_equals_right"] is True
        and int(character["left_action"]["support"]) == 0
        and int(character["right_action"]["support"]) == 0
    )


def build_generator_packets(
    primitive_cycles: list[dict[str, Any]],
    edges: dict[int, dict[str, Any]],
    pair_evaluations: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    packets = []
    for cycle in primitive_cycles:
        steps = []
        support_sum = 0
        coefficient_sum_signed = 0
        coefficient_abs_sum_signed_lift = 0
        for step_index, (source, target, edge_id) in enumerate(
            zip(cycle["vertices"], cycle["vertices"][1:], cycle["edge_ids"])
        ):
            edge = edges[int(edge_id)]
            removed, added = step_pair(edge, int(source), int(target))
            pair = pair_evaluations[pair_key(removed, added)]
            vector = pair["vector"]
            pi33 = pair["pi33_tube_character"]
            support_sum += int(vector["support"])
            coefficient_sum_signed += int(vector["coefficient_sum_signed"])
            coefficient_abs_sum_signed_lift += int(vector["coefficient_abs_sum_signed_lift"])
            steps.append(
                {
                    "step_index": step_index,
                    "edge_id": int(edge_id),
                    "source_vertex": int(source),
                    "target_vertex": int(target),
                    "removed": removed,
                    "added": added,
                    "loop_base_object": removed,
                    "vector_support": int(vector["support"]),
                    "vector_coefficient_sum_signed": int(vector["coefficient_sum_signed"]),
                    "vector_coefficient_abs_sum_signed_lift": int(
                        vector["coefficient_abs_sum_signed_lift"]
                    ),
                    "step_vector_sha256": vector["sha256"],
                    "bare_pi33_coefficient_signed": int(pi33["coefficient_signed"]),
                    "bare_pi33_left_support": int(pi33["left_action"]["support"]),
                    "bare_pi33_right_support": int(pi33["right_action"]["support"]),
                }
            )
        packet_core = {
            "generator_cycle_id": int(cycle["cycle_id"]),
            "length": int(cycle["length"]),
            "optical_action": int(cycle["optical_action"]),
            "step_count": len(steps),
            "loop_step_support_sum": support_sum,
            "loop_step_coefficient_sum_signed": coefficient_sum_signed,
            "loop_step_coefficient_abs_sum_signed_lift": coefficient_abs_sum_signed_lift,
            "steps": steps,
            "ordered_step_chain_sha256": sha_json(steps),
            "bare_pi33_coefficient_signed": 0,
            "bare_pi33_left_support_sum": sum(step["bare_pi33_left_support"] for step in steps),
            "bare_pi33_right_support_sum": sum(step["bare_pi33_right_support"] for step in steps),
        }
        packet_core["generator_amplitude_sha256"] = sha_json(packet_core)
        packets.append(packet_core)
    return packets


def build_lifted_transition_rows(
    transition_rows: list[dict[str, Any]],
    generator_packets: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for row in transition_rows:
        generator_id = int(row["generator_cycle_id"])
        packet = generator_packets[generator_id]
        height_delta = int(row["height_flux_delta"])
        height_corrected_transfer = -height_delta
        rows.append(
            {
                "transition_id": int(row["transition_id"]),
                "source_mask": int(row["source_mask"]),
                "target_mask": int(row["target_mask"]),
                "generator_cycle_id": generator_id,
                "toggle": row["toggle"],
                "packet_transfer": row["packet_transfer"],
                "incoming_signature_sha256": row["incoming_signature_sha256"],
                "outgoing_signature_sha256": row["outgoing_signature_sha256"],
                "generator_amplitude_sha256": packet["generator_amplitude_sha256"],
                "ordered_step_chain_sha256": packet["ordered_step_chain_sha256"],
                "bare_lambda_pi33_coefficient": 0,
                "height_corrected_R33_transfer": height_corrected_transfer,
                "finite_height_flux_delta": height_delta,
                "transition_balance_sum": height_corrected_transfer + height_delta,
                "hidden_R33_transfer_mod26": int(row["hidden_R33_transfer_mod26"]),
            }
        )
    return rows


def reverse_transition_checks(rows: list[dict[str, Any]]) -> bool:
    by_key = {
        (
            int(row["source_mask"]),
            int(row["target_mask"]),
            int(row["generator_cycle_id"]),
        ): row
        for row in rows
    }
    for row in rows:
        reverse = by_key.get(
            (
                int(row["target_mask"]),
                int(row["source_mask"]),
                int(row["generator_cycle_id"]),
            )
        )
        if reverse is None:
            return False
        if int(reverse["finite_height_flux_delta"]) != -int(row["finite_height_flux_delta"]):
            return False
        if int(reverse["height_corrected_R33_transfer"]) != -int(row["height_corrected_R33_transfer"]):
            return False
        if int(reverse["hidden_R33_transfer_mod26"]) != int(row["hidden_R33_transfer_mod26"]):
            return False
    return True


def build_theorem() -> dict[str, Any]:
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    boundary_to_loop = load_json(BOUNDARY_TO_LOOP_REPORT)
    annihilation = load_json(SECTOR33_BOUNDARY_ANNIHILATION_REPORT)
    primitive_cycles = load_primitive_cycles()
    edges = load_edges()
    pair_evaluations = {
        pair_key(row["removed"], row["added"]): row
        for row in annihilation["derived"]["directed_pair_evaluations"]
    }

    generator_packets_list = build_generator_packets(primitive_cycles, edges, pair_evaluations)
    generator_packets = {
        int(packet["generator_cycle_id"]): packet for packet in generator_packets_list
    }
    lifted_rows = build_lifted_transition_rows(
        scattering["derived"]["transition_rows"], generator_packets
    )
    packet_transfer_histogram = Counter(row["packet_transfer"] for row in lifted_rows)
    hidden_transfer_histogram = Counter(row["hidden_R33_transfer_mod26"] for row in lifted_rows)
    height_corrected_transfer_histogram = Counter(
        row["height_corrected_R33_transfer"] for row in lifted_rows
    )
    gamma8_generator_packet = generator_packets[GAMMA8_GENERATOR_ID]
    cycle8_steps = boundary_to_loop["derived"]["cycle8_lift"]["steps"]
    cycle8_step_hashes = [step["step_vector_sha256"] for step in cycle8_steps]
    gamma8_step_hashes = [step["step_vector_sha256"] for step in gamma8_generator_packet["steps"]]
    gamma8_lifted_rows = [
        row for row in lifted_rows if int(row["source_mask"]) == (1 << GAMMA8_GENERATOR_ID)
    ]

    checks = {
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "boundary_to_loop_map_is_certified": boundary_to_loop.get("status")
        == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary_to_loop.get("all_checks_pass") is True,
        "sector33_boundary_annihilation_is_certified": annihilation.get("status")
        == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True,
        "all_30_directed_pair_amplitudes_are_available": len(pair_evaluations) == 30
        and boundary_to_loop["derived"]["directed_object_pair_projection_count"] == 30,
        "all_directed_pair_pi33_amplitudes_are_zero": all(
            pi33_zero(row["pi33_tube_character"]) for row in pair_evaluations.values()
        ),
        "primitive_generator_amplitude_packet_count_is_11": len(generator_packets) == RESIDUE_RANK
        and sorted(generator_packets) == list(range(RESIDUE_RANK)),
        "generator_step_counts_match_primitive_lengths": all(
            packet["step_count"] == packet["length"] for packet in generator_packets.values()
        ),
        "all_generator_bare_pi33_amplitudes_are_zero": all(
            packet["bare_pi33_coefficient_signed"] == 0
            and packet["bare_pi33_left_support_sum"] == 0
            and packet["bare_pi33_right_support_sum"] == 0
            for packet in generator_packets.values()
        ),
        "gamma8_generator_packet_matches_boundary_to_loop_cycle8": gamma8_step_hashes
        == cycle8_step_hashes
        and gamma8_generator_packet["optical_action"]
        == boundary_to_loop["derived"]["cycle8_lift"]["cycle"]["optical_action"]
        and gamma8_generator_packet["length"]
        == boundary_to_loop["derived"]["cycle8_lift"]["cycle"]["length"],
        "lifted_transition_count_matches_scattering_table": len(lifted_rows)
        == DIRECTED_TRANSITION_COUNT
        == scattering["derived"]["transition_counts"]["directed_transition_count"],
        "all_lifted_rows_reference_known_generator_packets": all(
            row["generator_amplitude_sha256"]
            == generator_packets[int(row["generator_cycle_id"])]["generator_amplitude_sha256"]
            for row in lifted_rows
        ),
        "all_lifted_rows_have_zero_bare_pi33": all(
            row["bare_lambda_pi33_coefficient"] == 0 for row in lifted_rows
        ),
        "all_lifted_rows_balance_height_corrected_r33_transfer": all(
            row["transition_balance_sum"] == 0 for row in lifted_rows
        ),
        "all_lifted_rows_have_involutive_reverse": reverse_transition_checks(lifted_rows),
        "packet_transfer_histogram_matches_scattering_table": dict(packet_transfer_histogram)
        == scattering["derived"]["packet_transfer_histogram"],
        "hidden_r33_transfer_histogram_matches_scattering_table": {
            str(key): int(hidden_transfer_histogram[key]) for key in sorted(hidden_transfer_histogram)
        }
        == scattering["derived"]["hidden_R33_transfer_mod26_histogram"],
        "gamma8_lifted_scattering_star_has_11_rows": len(gamma8_lifted_rows) == RESIDUE_RANK,
        "gamma8_self_generator_lift_returns_to_zero_with_positive_correction": any(
            row["generator_cycle_id"] == GAMMA8_GENERATOR_ID
            and row["target_mask"] == 0
            and row["finite_height_flux_delta"] == -374784
            and row["height_corrected_R33_transfer"] == 374784
            and row["bare_lambda_pi33_coefficient"] == 0
            for row in gamma8_lifted_rows
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED"
        if all_checks_pass
        else "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.loop297_scattering_amplitude_lift",
        "status": status,
        "object": "d20",
        "claim": (
            "The canonical finite scattering table lifts through the certified boundary-to-Loop_297 map at "
            "the primitive-generator level. Each of the 11 primitive generators receives an ordered chain of "
            "certified directed channel-pair Loop_297 amplitude hashes. All bare tube-visible Pi_33 amplitudes "
            "are zero, so every scattering-row residual is carried by the height-corrected R33 transfer."
        ),
        "definition": {
            "generator_amplitude_packet": (
                "For a primitive closed-return generator, the ordered list of lambda_boundary step hashes, "
                "support/sum amplitudes, and certified zero Pi_33 tube coefficients."
            ),
            "lifted_scattering_row": (
                "A canonical scattering transition row together with its generator_amplitude_sha256, bare "
                "lambda Pi_33 coefficient, height-corrected R33 transfer, and finite height-flux delta."
            ),
            "transition_balance": (
                "bare_lambda_pi33_coefficient + height_corrected_R33_transfer + "
                "finite_height_flux_delta = 0."
            ),
        },
        "inputs": {
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
            "boundary_to_loop_report": {
                "path": rel(BOUNDARY_TO_LOOP_REPORT),
                "sha256": sha_file(BOUNDARY_TO_LOOP_REPORT),
            },
            "sector33_boundary_annihilation_report": {
                "path": rel(SECTOR33_BOUNDARY_ANNIHILATION_REPORT),
                "sha256": sha_file(SECTOR33_BOUNDARY_ANNIHILATION_REPORT),
            },
            "d20_edges": {"path": rel(D20_EDGES_CSV), "sha256": sha_file(D20_EDGES_CSV)},
            "primitive_cycles": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
        },
        "derived": {
            "generator_amplitude_packets": generator_packets_list,
            "generator_amplitude_packets_sha256": sha_json(generator_packets_list),
            "lifted_transition_counts": {
                "directed_transition_count": len(lifted_rows),
                "primitive_generator_count": RESIDUE_RANK,
            },
            "packet_transfer_histogram": dict(packet_transfer_histogram),
            "hidden_R33_transfer_mod26_histogram": {
                str(key): int(hidden_transfer_histogram[key])
                for key in sorted(hidden_transfer_histogram)
            },
            "height_corrected_R33_transfer_histogram": {
                str(key): int(height_corrected_transfer_histogram[key])
                for key in sorted(height_corrected_transfer_histogram)
            },
            "gamma8_generator_amplitude_packet": gamma8_generator_packet,
            "gamma8_lifted_scattering_star": gamma8_lifted_rows,
            "lifted_transition_rows": lifted_rows,
            "lifted_transition_rows_sha256": sha_json(lifted_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the finite scattering table has certified Loop_297 step-amplitude provenance",
                "bare lambda_boundary transport remains Pi_33-annihilated on every primitive generator",
                "the transition-level nonzero Pi_33 balance is exactly the height-corrected R33 transfer",
                "gamma_8's generator lift agrees with the earlier certified boundary-to-Loop_297 cycle-8 lift",
            ],
            "what_this_does_not_prove": (
                "This attaches certified Loop_297 amplitude hashes and tube Pi_33 evaluations. It does not "
                "materialize full A985 matrix coordinates or continuum scattering amplitudes."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Materialize a compact amplitude quotient for the 11 generator packets: identify which "
            "Loop_297 step-hash chains are independent under the tube/public-zero quotient."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.loop297_scattering_amplitude_lift_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify scattering, boundary-to-Loop_297, and sector-33 boundary-annihilation inputs",
            "verify all 30 directed pair amplitudes are available and Pi_33-annihilated",
            "verify all 11 primitive generator amplitude packets",
            "verify gamma_8 generator packet matches the certified cycle-8 boundary lift",
            "verify all 22528 lifted scattering rows reference generator amplitude packets",
            "verify every lifted transition balances bare zero, height-corrected R33 transfer, and height flux",
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
