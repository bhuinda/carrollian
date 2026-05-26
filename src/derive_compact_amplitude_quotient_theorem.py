from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "compact_amplitude_quotient"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT = (
    D20_INVARIANTS / "theorems" / "loop297_scattering_amplitude_lift" / "report.json"
)
CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_finite_scattering_table" / "report.json"
)

RESIDUE_RANK = 11
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


def step_is_tube_zero(step: dict[str, Any]) -> bool:
    return (
        int(step["bare_pi33_coefficient_signed"]) == 0
        and int(step["bare_pi33_left_support"]) == 0
        and int(step["bare_pi33_right_support"]) == 0
    )


def packet_is_tube_zero(packet: dict[str, Any]) -> bool:
    return (
        int(packet["bare_pi33_coefficient_signed"]) == 0
        and int(packet["bare_pi33_left_support_sum"]) == 0
        and int(packet["bare_pi33_right_support_sum"]) == 0
        and all(step_is_tube_zero(step) for step in packet["steps"])
    )


def quotient_classes(rows: list[dict[str, Any]], key_name: str) -> list[dict[str, Any]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        groups[str(row[key_name])].append(int(row["generator_cycle_id"]))
    classes = []
    for class_id, key in enumerate(sorted(groups, key=lambda item: (groups[item], item))):
        generator_ids = sorted(groups[key])
        classes.append(
            {
                "class_id": class_id,
                "class_key": key,
                "size": len(generator_ids),
                "generator_cycle_ids": generator_ids,
            }
        )
    return classes


def singleton_partition(classes: list[dict[str, Any]], expected_count: int) -> bool:
    return len(classes) == expected_count and all(row["size"] == 1 for row in classes)


def build_step_atoms(packets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    atoms_by_hash: dict[str, dict[str, Any]] = {}
    for packet in packets:
        generator_id = int(packet["generator_cycle_id"])
        for step in packet["steps"]:
            step_hash = step["step_vector_sha256"]
            atom = atoms_by_hash.setdefault(
                step_hash,
                {
                    "step_vector_sha256": step_hash,
                    "vector_support_values": set(),
                    "vector_coefficient_sum_signed_values": set(),
                    "vector_coefficient_abs_sum_signed_lift_values": set(),
                    "directed_channel_swaps": set(),
                    "edge_ids": set(),
                    "occurrences": [],
                },
            )
            atom["vector_support_values"].add(int(step["vector_support"]))
            atom["vector_coefficient_sum_signed_values"].add(
                int(step["vector_coefficient_sum_signed"])
            )
            atom["vector_coefficient_abs_sum_signed_lift_values"].add(
                int(step["vector_coefficient_abs_sum_signed_lift"])
            )
            atom["directed_channel_swaps"].add(f"{step['removed']}->{step['added']}")
            atom["edge_ids"].add(int(step["edge_id"]))
            atom["occurrences"].append(
                {
                    "generator_cycle_id": generator_id,
                    "step_index": int(step["step_index"]),
                    "edge_id": int(step["edge_id"]),
                    "source_vertex": int(step["source_vertex"]),
                    "target_vertex": int(step["target_vertex"]),
                    "removed": step["removed"],
                    "added": step["added"],
                    "tube_zero": step_is_tube_zero(step),
                }
            )

    atoms = []
    hash_to_atom_id = {}
    for atom_id, step_hash in enumerate(sorted(atoms_by_hash)):
        raw = atoms_by_hash[step_hash]
        occurrence_generator_ids = sorted(
            {int(row["generator_cycle_id"]) for row in raw["occurrences"]}
        )
        support_values = sorted(raw["vector_support_values"])
        coefficient_values = sorted(raw["vector_coefficient_sum_signed_values"])
        coefficient_abs_values = sorted(raw["vector_coefficient_abs_sum_signed_lift_values"])
        atom = {
            "step_atom_id": atom_id,
            "step_vector_sha256": step_hash,
            "occurrence_count": len(raw["occurrences"]),
            "generator_cycle_ids": occurrence_generator_ids,
            "directed_channel_swaps": sorted(raw["directed_channel_swaps"]),
            "edge_ids": sorted(raw["edge_ids"]),
            "vector_support": support_values[0] if len(support_values) == 1 else None,
            "vector_coefficient_sum_signed": (
                coefficient_values[0] if len(coefficient_values) == 1 else None
            ),
            "vector_coefficient_abs_sum_signed_lift": (
                coefficient_abs_values[0] if len(coefficient_abs_values) == 1 else None
            ),
            "consistent_vector_data": (
                len(support_values) == 1
                and len(coefficient_values) == 1
                and len(coefficient_abs_values) == 1
            ),
            "occurrences": sorted(
                raw["occurrences"],
                key=lambda row: (row["generator_cycle_id"], row["step_index"]),
            ),
        }
        hash_to_atom_id[step_hash] = atom_id
        atoms.append(atom)
    return atoms, hash_to_atom_id


def build_generator_rows(
    packets: list[dict[str, Any]],
    hash_to_atom_id: dict[str, int],
    scattering_summaries: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for packet in sorted(packets, key=lambda row: int(row["generator_cycle_id"])):
        generator_id = int(packet["generator_cycle_id"])
        step_hashes = [step["step_vector_sha256"] for step in packet["steps"]]
        step_atom_ids_ordered = [hash_to_atom_id[step_hash] for step_hash in step_hashes]
        step_atom_id_counts = Counter(step_atom_ids_ordered)
        tube_zero_signature = {
            "bare_pi33_coefficient_signed": int(packet["bare_pi33_coefficient_signed"]),
            "bare_pi33_left_support_sum": int(packet["bare_pi33_left_support_sum"]),
            "bare_pi33_right_support_sum": int(packet["bare_pi33_right_support_sum"]),
        }
        profile_key = {
            "length": int(packet["length"]),
            "optical_action": int(packet["optical_action"]),
            "loop_step_support_sum": int(packet["loop_step_support_sum"]),
            "loop_step_coefficient_sum_signed": int(
                packet["loop_step_coefficient_sum_signed"]
            ),
            "loop_step_coefficient_abs_sum_signed_lift": int(
                packet["loop_step_coefficient_abs_sum_signed_lift"]
            ),
        }
        summary = scattering_summaries[generator_id]
        rows.append(
            {
                "generator_cycle_id": generator_id,
                "length": int(packet["length"]),
                "step_count": int(packet["step_count"]),
                "optical_action": int(packet["optical_action"]),
                "loop_step_support_sum": int(packet["loop_step_support_sum"]),
                "loop_step_coefficient_sum_signed": int(
                    packet["loop_step_coefficient_sum_signed"]
                ),
                "loop_step_coefficient_abs_sum_signed_lift": int(
                    packet["loop_step_coefficient_abs_sum_signed_lift"]
                ),
                "tube_zero_signature": tube_zero_signature,
                "tube_zero_signature_sha256": sha_json(tube_zero_signature),
                "support_profile_sha256": sha_json(profile_key),
                "step_hash_multiset_sha256": sha_json(sorted(step_hashes)),
                "ordered_step_chain_sha256": packet["ordered_step_chain_sha256"],
                "generator_amplitude_sha256": packet["generator_amplitude_sha256"],
                "step_atom_ids_ordered": step_atom_ids_ordered,
                "step_atom_multiplicities": [
                    {"step_atom_id": atom_id, "multiplicity": count}
                    for atom_id, count in sorted(step_atom_id_counts.items())
                ],
                "unique_step_atom_count": len(step_atom_id_counts),
                "repeated_step_atom_count": len(step_atom_ids_ordered) - len(step_atom_id_counts),
                "corrected_basis_clock_mod26": int(summary["corrected_basis_clock_mod26"]),
                "hidden_R33_transfer_mod26_histogram": summary[
                    "hidden_R33_transfer_mod26_histogram"
                ],
                "packet_transfer_histogram": summary["packet_transfer_histogram"],
                "preserves_hidden_packet": int(summary["corrected_basis_clock_mod26"]) == 0,
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    lift = load_json(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT)
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    packets = lift["derived"]["generator_amplitude_packets"]
    scattering_summaries = {
        int(row["generator_cycle_id"]): row
        for row in scattering["derived"]["generator_summaries"]
    }

    step_atoms, hash_to_atom_id = build_step_atoms(packets)
    generator_rows = build_generator_rows(packets, hash_to_atom_id, scattering_summaries)
    bare_pi33_classes = quotient_classes(generator_rows, "tube_zero_signature_sha256")
    support_profile_classes = quotient_classes(generator_rows, "support_profile_sha256")
    step_multiset_classes = quotient_classes(generator_rows, "step_hash_multiset_sha256")
    ordered_chain_classes = quotient_classes(generator_rows, "ordered_step_chain_sha256")
    atom_occurrence_histogram = Counter(atom["occurrence_count"] for atom in step_atoms)
    length_histogram = Counter(row["length"] for row in generator_rows)
    gamma8_row = next(
        row for row in generator_rows if row["generator_cycle_id"] == GAMMA8_GENERATOR_ID
    )
    preserving_generators = [
        row["generator_cycle_id"] for row in generator_rows if row["preserves_hidden_packet"]
    ]

    checks = {
        "loop297_scattering_amplitude_lift_is_certified": lift.get("status")
        == "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED"
        and lift.get("all_checks_pass") is True,
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "primitive_generator_packet_count_is_11": len(packets) == RESIDUE_RANK
        and sorted(int(packet["generator_cycle_id"]) for packet in packets)
        == list(range(RESIDUE_RANK)),
        "all_generator_packets_are_tube_pi33_zero": all(packet_is_tube_zero(packet) for packet in packets),
        "step_occurrence_count_matches_generator_lengths": sum(
            len(packet["steps"]) for packet in packets
        )
        == sum(int(packet["length"]) for packet in packets)
        == sum(row["step_count"] for row in generator_rows),
        "used_step_atom_count_is_25": len(step_atoms) == 25,
        "all_step_atoms_have_consistent_vector_data": all(
            atom["consistent_vector_data"] for atom in step_atoms
        ),
        "all_step_atom_occurrences_are_tube_zero": all(
            occurrence["tube_zero"] for atom in step_atoms for occurrence in atom["occurrences"]
        ),
        "bare_pi33_quotient_collapses_all_generators": len(bare_pi33_classes) == 1
        and bare_pi33_classes[0]["size"] == RESIDUE_RANK,
        "support_profile_quotient_separates_generators": singleton_partition(
            support_profile_classes, RESIDUE_RANK
        ),
        "step_hash_multiset_quotient_separates_generators": singleton_partition(
            step_multiset_classes, RESIDUE_RANK
        ),
        "ordered_step_chain_quotient_separates_generators": singleton_partition(
            ordered_chain_classes, RESIDUE_RANK
        ),
        "gamma8_row_matches_certified_cycle8_packet": gamma8_row["length"] == 5
        and gamma8_row["optical_action"] == 374784
        and gamma8_row["loop_step_support_sum"] == 193
        and gamma8_row["loop_step_coefficient_sum_signed"] == 53952
        and gamma8_row["generator_amplitude_sha256"]
        == lift["derived"]["gamma8_generator_amplitude_packet"]["generator_amplitude_sha256"],
        "hidden_packet_preserving_generator_is_exactly_3": preserving_generators == [3],
        "other_ten_generators_flip_hidden_packet": all(
            (
                row["generator_cycle_id"] == 3
                or row["packet_transfer_histogram"]
                == {"kernel_to_odd": 1024, "odd_to_kernel": 1024}
            )
            for row in generator_rows
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        if all_checks_pass
        else "D20_COMPACT_AMPLITUDE_QUOTIENT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.compact_amplitude_quotient",
        "status": status,
        "object": "d20",
        "claim": (
            "The 11 primitive closed-return generator amplitude packets admit a compact quotient. "
            "Modulo the tube-visible Pi_33 functional they collapse to one zero class; retaining the "
            "certified Loop_297 step-vector atoms gives 25 step atoms whose multiset and ordered-chain "
            "quotients separate all 11 primitive generators."
        ),
        "definition": {
            "tube_zero_quotient": (
                "Identify generator packets with the same bare Pi_33 coefficient and left/right tube "
                "supports. In the certified data all 11 packets have the zero signature."
            ),
            "loop_step_atom": (
                "A distinct certified Loop_297 step_vector_sha256 appearing in a primitive generator "
                "amplitude packet, together with its support, signed coefficient sum, directed channel "
                "swap labels, and packet occurrences."
            ),
            "compact_amplitude_quotient": (
                "The quotient ladder from the single tube-zero public class to support-profile, step-hash "
                "multiset, and ordered-chain generator classes."
            ),
        },
        "inputs": {
            "loop297_scattering_amplitude_lift_report": {
                "path": rel(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT),
                "sha256": sha_file(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT),
            },
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
        },
        "derived": {
            "quotient_summary": {
                "primitive_generator_count": len(generator_rows),
                "directed_step_occurrence_count": sum(row["step_count"] for row in generator_rows),
                "used_loop_step_atom_count": len(step_atoms),
                "shared_loop_step_atom_count": sum(
                    1 for atom in step_atoms if atom["occurrence_count"] > 1
                ),
                "isolated_loop_step_atom_count": sum(
                    1 for atom in step_atoms if atom["occurrence_count"] == 1
                ),
                "length_histogram": {
                    str(key): int(length_histogram[key]) for key in sorted(length_histogram)
                },
                "atom_occurrence_histogram": {
                    str(key): int(atom_occurrence_histogram[key])
                    for key in sorted(atom_occurrence_histogram)
                },
                "bare_pi33_quotient_class_count": len(bare_pi33_classes),
                "support_profile_quotient_class_count": len(support_profile_classes),
                "step_hash_multiset_quotient_class_count": len(step_multiset_classes),
                "ordered_step_chain_quotient_class_count": len(ordered_chain_classes),
                "hidden_packet_preserving_generators": preserving_generators,
            },
            "loop_step_atoms": step_atoms,
            "loop_step_atoms_sha256": sha_json(step_atoms),
            "generator_quotient_rows": generator_rows,
            "generator_quotient_rows_sha256": sha_json(generator_rows),
            "quotient_classes": {
                "bare_pi33_tube_zero": bare_pi33_classes,
                "support_profile": support_profile_classes,
                "step_hash_multiset": step_multiset_classes,
                "ordered_step_chain": ordered_chain_classes,
            },
            "gamma8_quotient_row": gamma8_row,
        },
        "interpretation": {
            "what_this_proves": [
                "the public tube-visible amplitude quotient has a single zero class",
                "the non-public compact amplitude alphabet needed by the generator packets has 25 Loop_297 atoms",
                "support profiles, unordered atom multisets, and ordered chains all separate the 11 generators",
                "generator 3 is the unique hidden-packet-preserving amplitude packet in this quotient",
            ],
            "what_this_does_not_prove": (
                "This quotient uses certified Loop_297 step hashes and tube-zero evaluations. It does not "
                "materialize full A985 coordinates or continuum scattering amplitudes."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the reduced amplitude-quotient scattering automaton: label the 2048 residue-mask "
            "transitions by compact generator quotient data and compute its spectral/sector invariants."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.compact_amplitude_quotient_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the Loop_297 scattering amplitude lift and canonical scattering table inputs",
            "verify all 11 primitive generator packets are tube-visible Pi_33 zero",
            "extract the distinct Loop_297 step-vector atoms used by the generator packets",
            "verify the tube-zero quotient collapses all generators to one public class",
            "verify the support-profile, step-hash multiset, and ordered-chain quotients separate all generators",
            "verify gamma_8 and the unique hidden-packet-preserving generator survive in the quotient rows",
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
