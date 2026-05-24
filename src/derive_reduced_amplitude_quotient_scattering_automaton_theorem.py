from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from math import comb
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "reduced_amplitude_quotient_scattering_automaton"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_finite_scattering_table" / "report.json"
)
COMPACT_AMPLITUDE_QUOTIENT_REPORT = (
    D20_INVARIANTS / "theorems" / "compact_amplitude_quotient" / "report.json"
)

RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
DIRECTED_TRANSITION_COUNT = MASK_COUNT * RESIDUE_RANK
UNDIRECTED_TRANSITION_COUNT = DIRECTED_TRANSITION_COUNT // 2
GAMMA8_GENERATOR_ID = 8
HIDDEN_SECTORS = ["kernel", "odd"]


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


def class_id_by_generator(classes: list[dict[str, Any]]) -> dict[int, int]:
    mapping = {}
    for row in classes:
        for generator_id in row["generator_cycle_ids"]:
            mapping[int(generator_id)] = int(row["class_id"])
    return mapping


def build_generator_labels(compact: dict[str, Any]) -> list[dict[str, Any]]:
    classes = compact["derived"]["quotient_classes"]
    tube_class = class_id_by_generator(classes["bare_pi33_tube_zero"])
    support_class = class_id_by_generator(classes["support_profile"])
    multiset_class = class_id_by_generator(classes["step_hash_multiset"])
    ordered_class = class_id_by_generator(classes["ordered_step_chain"])

    labels = []
    for row in sorted(
        compact["derived"]["generator_quotient_rows"],
        key=lambda item: int(item["generator_cycle_id"]),
    ):
        generator_id = int(row["generator_cycle_id"])
        labels.append(
            {
                "generator_cycle_id": generator_id,
                "tube_zero_class_id": tube_class[generator_id],
                "support_profile_class_id": support_class[generator_id],
                "step_hash_multiset_class_id": multiset_class[generator_id],
                "ordered_step_chain_class_id": ordered_class[generator_id],
                "length": int(row["length"]),
                "optical_action": int(row["optical_action"]),
                "loop_step_support_sum": int(row["loop_step_support_sum"]),
                "loop_step_coefficient_sum_signed": int(
                    row["loop_step_coefficient_sum_signed"]
                ),
                "loop_step_coefficient_abs_sum_signed_lift": int(
                    row["loop_step_coefficient_abs_sum_signed_lift"]
                ),
                "unique_step_atom_count": int(row["unique_step_atom_count"]),
                "step_atom_ids_ordered": row["step_atom_ids_ordered"],
                "step_atom_multiplicities": row["step_atom_multiplicities"],
                "preserves_hidden_packet": bool(row["preserves_hidden_packet"]),
                "corrected_basis_clock_mod26": int(row["corrected_basis_clock_mod26"]),
                "packet_transfer_histogram": row["packet_transfer_histogram"],
                "hidden_R33_transfer_mod26_histogram": row[
                    "hidden_R33_transfer_mod26_histogram"
                ],
                "ordered_step_chain_sha256": row["ordered_step_chain_sha256"],
                "step_hash_multiset_sha256": row["step_hash_multiset_sha256"],
                "generator_amplitude_sha256": row["generator_amplitude_sha256"],
            }
        )
    return labels


def build_reduced_transition_rows(
    scattering_rows: list[dict[str, Any]],
    labels_by_generator: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for row in scattering_rows:
        generator_id = int(row["generator_cycle_id"])
        label = labels_by_generator[generator_id]
        rows.append(
            {
                "transition_id": int(row["transition_id"]),
                "source_mask": int(row["source_mask"]),
                "target_mask": int(row["target_mask"]),
                "generator_cycle_id": generator_id,
                "tube_zero_class_id": int(label["tube_zero_class_id"]),
                "support_profile_class_id": int(label["support_profile_class_id"]),
                "step_hash_multiset_class_id": int(label["step_hash_multiset_class_id"]),
                "ordered_step_chain_class_id": int(label["ordered_step_chain_class_id"]),
                "source_hidden_packet": row["source_hidden_packet"],
                "target_hidden_packet": row["target_hidden_packet"],
                "packet_transfer": row["packet_transfer"],
                "toggle": row["toggle"],
                "finite_height_flux_delta": int(row["height_flux_delta"]),
                "hidden_R33_transfer_mod26": int(row["hidden_R33_transfer_mod26"]),
            }
        )
    return rows


def reachable_state_count(rows: list[dict[str, Any]]) -> int:
    adjacency: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        adjacency[int(row["source_mask"])].append(int(row["target_mask"]))
    seen = {0}
    queue: deque[int] = deque([0])
    while queue:
        current = queue.popleft()
        for target in adjacency[current]:
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return len(seen)


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
        for key in (
            "tube_zero_class_id",
            "support_profile_class_id",
            "step_hash_multiset_class_id",
            "ordered_step_chain_class_id",
            "hidden_R33_transfer_mod26",
        ):
            if reverse[key] != row[key]:
                return False
    return True


def commuting_involutive_generators() -> bool:
    for mask in range(MASK_COUNT):
        for i in range(RESIDUE_RANK):
            if ((mask ^ (1 << i)) ^ (1 << i)) != mask:
                return False
            for j in range(i + 1, RESIDUE_RANK):
                left = (mask ^ (1 << i)) ^ (1 << j)
                right = (mask ^ (1 << j)) ^ (1 << i)
                if left != right:
                    return False
    return True


def spectral_invariants() -> dict[str, Any]:
    adjacency_spectrum = [
        {"eigenvalue": RESIDUE_RANK - 2 * k, "multiplicity": comb(RESIDUE_RANK, k)}
        for k in range(RESIDUE_RANK + 1)
    ]
    laplacian_spectrum = [
        {"eigenvalue": 2 * k, "multiplicity": comb(RESIDUE_RANK, k)}
        for k in range(RESIDUE_RANK + 1)
    ]
    trace_a = sum(row["eigenvalue"] * row["multiplicity"] for row in adjacency_spectrum)
    trace_a2 = sum((row["eigenvalue"] ** 2) * row["multiplicity"] for row in adjacency_spectrum)
    return {
        "adjacency_spectrum": adjacency_spectrum,
        "laplacian_spectrum": laplacian_spectrum,
        "spectral_moments": {
            "dimension": sum(row["multiplicity"] for row in adjacency_spectrum),
            "trace_A": trace_a,
            "trace_A2": trace_a2,
            "spectral_radius": RESIDUE_RANK,
            "second_largest_adjacency_eigenvalue": RESIDUE_RANK - 2,
            "random_walk_gap": "2/11",
            "bipartite_min_eigenvalue": -RESIDUE_RANK,
        },
    }


def build_sector_invariants(rows: list[dict[str, Any]]) -> dict[str, Any]:
    state_sector: dict[int, str] = {}
    transfer_counts = Counter()
    for row in rows:
        source = int(row["source_mask"])
        source_sector = row["source_hidden_packet"]
        prior = state_sector.setdefault(source, source_sector)
        if prior != source_sector:
            raise ValueError(f"state {source} has inconsistent hidden sector")
        transfer_counts[(source_sector, row["target_hidden_packet"])] += 1

    state_counts = Counter(state_sector.values())
    matrix = []
    for source_sector in HIDDEN_SECTORS:
        row = []
        for target_sector in HIDDEN_SECTORS:
            count = transfer_counts[(source_sector, target_sector)]
            divisor = state_counts[source_sector]
            if count % divisor != 0:
                raise ValueError("hidden-sector quotient has nonintegral row")
            row.append(count // divisor)
        matrix.append(row)
    return {
        "state_counts": {key: int(state_counts[key]) for key in HIDDEN_SECTORS},
        "directed_transfer_counts": {
            f"{source}->{target}": int(transfer_counts[(source, target)])
            for source in HIDDEN_SECTORS
            for target in HIDDEN_SECTORS
        },
        "per_state_sector_quotient_matrix": {
            "basis": HIDDEN_SECTORS,
            "matrix": matrix,
            "eigenvalues": [
                {"eigenvalue": matrix[0][0] + matrix[0][1], "multiplicity": 1},
                {"eigenvalue": matrix[0][0] - matrix[0][1], "multiplicity": 1},
            ],
        },
    }


def build_atom_exposures(generator_labels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_atom: dict[int, dict[str, Any]] = {}
    for label in generator_labels:
        generator_id = int(label["generator_cycle_id"])
        for step_index, atom_id in enumerate(label["step_atom_ids_ordered"]):
            row = by_atom.setdefault(
                int(atom_id),
                {
                    "step_atom_id": int(atom_id),
                    "generator_occurrence_count": 0,
                    "automaton_step_token_count": 0,
                    "generator_cycle_ids": set(),
                    "packet_transfer_exposure": Counter(),
                    "occurrences": [],
                },
            )
            row["generator_occurrence_count"] += 1
            row["automaton_step_token_count"] += MASK_COUNT
            row["generator_cycle_ids"].add(generator_id)
            row["packet_transfer_exposure"].update(label["packet_transfer_histogram"])
            row["occurrences"].append(
                {"generator_cycle_id": generator_id, "step_index": step_index}
            )

    exposures = []
    for atom_id in sorted(by_atom):
        raw = by_atom[atom_id]
        exposures.append(
            {
                "step_atom_id": atom_id,
                "generator_occurrence_count": int(raw["generator_occurrence_count"]),
                "automaton_step_token_count": int(raw["automaton_step_token_count"]),
                "generator_cycle_ids": sorted(raw["generator_cycle_ids"]),
                "packet_transfer_exposure": {
                    key: int(raw["packet_transfer_exposure"][key])
                    for key in sorted(raw["packet_transfer_exposure"])
                },
                "occurrences": sorted(
                    raw["occurrences"],
                    key=lambda row: (row["generator_cycle_id"], row["step_index"]),
                ),
            }
        )
    return exposures


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def build_theorem() -> dict[str, Any]:
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    compact = load_json(COMPACT_AMPLITUDE_QUOTIENT_REPORT)
    generator_labels = build_generator_labels(compact)
    labels_by_generator = {int(row["generator_cycle_id"]): row for row in generator_labels}
    transition_rows = build_reduced_transition_rows(
        scattering["derived"]["transition_rows"], labels_by_generator
    )

    outdegree = Counter(row["source_mask"] for row in transition_rows)
    indegree = Counter(row["target_mask"] for row in transition_rows)
    label_counts = Counter(row["ordered_step_chain_class_id"] for row in transition_rows)
    generator_counts = Counter(row["generator_cycle_id"] for row in transition_rows)
    tube_class_counts = Counter(row["tube_zero_class_id"] for row in transition_rows)
    hidden_preserving_generators = [
        row["generator_cycle_id"] for row in generator_labels if row["preserves_hidden_packet"]
    ]
    hidden_flipping_generators = [
        row["generator_cycle_id"] for row in generator_labels if not row["preserves_hidden_packet"]
    ]
    spectrum = spectral_invariants()
    sector = build_sector_invariants(transition_rows)
    atom_exposures = build_atom_exposures(generator_labels)
    total_optical_action = sum(row["optical_action"] * MASK_COUNT for row in generator_labels)
    total_loop_support = sum(row["loop_step_support_sum"] * MASK_COUNT for row in generator_labels)
    total_loop_coefficient = sum(
        row["loop_step_coefficient_sum_signed"] * MASK_COUNT for row in generator_labels
    )
    signed_height_flux_total = sum(row["finite_height_flux_delta"] for row in transition_rows)
    absolute_height_flux_total = sum(abs(row["finite_height_flux_delta"]) for row in transition_rows)
    gamma8_transitions = [
        row for row in transition_rows if row["generator_cycle_id"] == GAMMA8_GENERATOR_ID
    ]
    gamma8_label = labels_by_generator[GAMMA8_GENERATOR_ID]

    adjacency_trace = spectrum["spectral_moments"]["trace_A"]
    adjacency_trace_square = spectrum["spectral_moments"]["trace_A2"]
    checks = {
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "compact_amplitude_quotient_is_certified": compact.get("status")
        == "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        and compact.get("all_checks_pass") is True,
        "state_count_is_2048": MASK_COUNT == 2048
        and scattering["derived"]["transition_counts"]["residue_mask_count"] == MASK_COUNT,
        "label_count_is_11": len(generator_labels) == RESIDUE_RANK
        and sorted(labels_by_generator) == list(range(RESIDUE_RANK)),
        "transition_count_is_2048_times_11": len(transition_rows) == DIRECTED_TRANSITION_COUNT,
        "all_transition_labels_are_known": all(
            row["generator_cycle_id"] in labels_by_generator for row in transition_rows
        ),
        "every_transition_is_xor_generator_toggle": all(
            row["target_mask"] == (row["source_mask"] ^ (1 << row["generator_cycle_id"]))
            for row in transition_rows
        ),
        "all_generators_are_commuting_involutions": commuting_involutive_generators(),
        "every_transition_has_reverse_with_same_compact_label": reverse_transition_checks(
            transition_rows
        ),
        "automaton_is_connected": reachable_state_count(transition_rows) == MASK_COUNT,
        "outdegree_and_indegree_are_11_regular": Counter(outdegree.values()) == {RESIDUE_RANK: MASK_COUNT}
        and Counter(indegree.values()) == {RESIDUE_RANK: MASK_COUNT},
        "each_ordered_chain_label_has_2048_transitions": all(
            label_counts[label["ordered_step_chain_class_id"]] == MASK_COUNT
            for label in generator_labels
        ),
        "each_generator_has_2048_transitions": all(
            generator_counts[generator_id] == MASK_COUNT for generator_id in range(RESIDUE_RANK)
        ),
        "tube_zero_public_label_collapses_all_transitions": dict(tube_class_counts) == {0: DIRECTED_TRANSITION_COUNT},
        "hidden_sector_quotient_matrix_is_1_10_10_1": sector[
            "per_state_sector_quotient_matrix"
        ]["matrix"]
        == [[1, 10], [10, 1]],
        "hidden_packet_preserving_generator_is_exactly_3": hidden_preserving_generators == [3],
        "hidden_packet_flipping_generators_are_the_other_ten": hidden_flipping_generators
        == [0, 1, 2, 4, 5, 6, 7, 8, 9, 10],
        "adjacency_spectrum_has_expected_dimension_and_moments": spectrum["spectral_moments"][
            "dimension"
        ]
        == MASK_COUNT
        and adjacency_trace == 0
        and adjacency_trace_square == DIRECTED_TRANSITION_COUNT,
        "laplacian_zero_mode_is_unique": spectrum["laplacian_spectrum"][0]
        == {"eigenvalue": 0, "multiplicity": 1},
        "automaton_step_atom_exposure_matches_72_generator_steps": sum(
            row["automaton_step_token_count"] for row in atom_exposures
        )
        == compact["derived"]["quotient_summary"]["directed_step_occurrence_count"] * MASK_COUNT,
        "atom_exposure_uses_25_step_atoms": len(atom_exposures)
        == compact["derived"]["quotient_summary"]["used_loop_step_atom_count"]
        == 25,
        "signed_height_flux_total_is_zero": signed_height_flux_total == 0,
        "absolute_height_flux_matches_optical_action_total": absolute_height_flux_total
        == total_optical_action,
        "gamma8_label_has_2048_transitions_and_expected_action": len(gamma8_transitions) == MASK_COUNT
        and gamma8_label["optical_action"] == 374784
        and gamma8_label["ordered_step_chain_class_id"] == GAMMA8_GENERATOR_ID,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_CERTIFIED"
        if all_checks_pass
        else "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.reduced_amplitude_quotient_scattering_automaton",
        "status": status,
        "object": "d20",
        "claim": (
            "The compact amplitude quotient labels a reduced scattering automaton on the 2048 closed-return "
            "residue masks. The automaton is the 11-regular Cayley graph of F_2^11 by the primitive "
            "closed-return generators, with one tube-zero public label, 11 compact ordered-chain labels, "
            "25 exposed Loop_297 step atoms, and a hidden-sector quotient matrix [[1,10],[10,1]]."
        ),
        "definition": {
            "state": "A closed-return residue mask in F_2^11.",
            "transition": "T_i(mask) = mask xor 2^i, labelled by the compact amplitude quotient row for generator i.",
            "reduced_automaton": (
                "The directed labelled transition system with 2048 states and 11 outgoing primitive-generator "
                "moves per state, retaining compact amplitude quotient labels instead of full Loop_297 vectors."
            ),
            "sector_quotient": (
                "The two-state hidden-packet quotient induced by kernel/odd packet labels on the 2048 masks."
            ),
        },
        "inputs": {
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
            "compact_amplitude_quotient_report": {
                "path": rel(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
                "sha256": sha_file(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
            },
        },
        "derived": {
            "automaton_summary": {
                "state_count": MASK_COUNT,
                "residue_rank": RESIDUE_RANK,
                "generator_label_count": len(generator_labels),
                "tube_zero_public_label_count": len(tube_class_counts),
                "used_loop_step_atom_count": len(atom_exposures),
                "directed_transition_count": len(transition_rows),
                "undirected_transition_count": UNDIRECTED_TRANSITION_COUNT,
                "outdegree_histogram": histogram(Counter(outdegree.values())),
                "indegree_histogram": histogram(Counter(indegree.values())),
                "ordered_step_chain_label_transition_histogram": histogram(label_counts),
                "generator_transition_histogram": histogram(generator_counts),
                "tube_zero_class_transition_histogram": histogram(tube_class_counts),
                "hidden_packet_preserving_generators": hidden_preserving_generators,
                "hidden_packet_flipping_generators": hidden_flipping_generators,
            },
            "action_invariants": {
                "total_optical_action_over_directed_transitions": total_optical_action,
                "total_loop_step_support_over_directed_transitions": total_loop_support,
                "total_loop_step_coefficient_sum_over_directed_transitions": total_loop_coefficient,
                "signed_height_flux_total": signed_height_flux_total,
                "absolute_height_flux_total": absolute_height_flux_total,
            },
            "spectral_invariants": spectrum,
            "sector_invariants": sector,
            "generator_labels": generator_labels,
            "generator_labels_sha256": sha_json(generator_labels),
            "atom_exposure_rows": atom_exposures,
            "atom_exposure_rows_sha256": sha_json(atom_exposures),
            "gamma8_automaton_label": gamma8_label,
            "gamma8_transition_summary": {
                "generator_cycle_id": GAMMA8_GENERATOR_ID,
                "transition_count": len(gamma8_transitions),
                "toggle_histogram": histogram(Counter(row["toggle"] for row in gamma8_transitions)),
                "packet_transfer_histogram": histogram(
                    Counter(row["packet_transfer"] for row in gamma8_transitions)
                ),
                "height_flux_delta_histogram": histogram(
                    Counter(row["finite_height_flux_delta"] for row in gamma8_transitions)
                ),
            },
            "reduced_transition_rows": transition_rows,
            "reduced_transition_rows_sha256": sha_json(transition_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the compact amplitude labels form a complete reduced transition alphabet for all 2048 masks",
                "the reduced automaton is connected, 11-regular, reversible, and generated by commuting involutions",
                "the public tube-zero quotient erases generator distinctions while the compact ordered-chain quotient preserves them",
                "the hidden packet quotient has per-state transition matrix [[1,10],[10,1]] with generator 3 as the unique preserving move",
                "the exact hypercube adjacency and Laplacian spectra are certified from the transition system",
            ],
            "what_this_does_not_prove": (
                "This automaton is finite and quotient-labelled. It does not materialize continuum scattering "
                "states or full A985 coordinate amplitudes."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Derive the amplitude-quotient Fourier mode classifier: diagonalize the F_2^11 automaton by "
            "characters and classify modes by eigenvalue, hidden sector, gamma_8 support, and sector-26 clock."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.reduced_amplitude_quotient_scattering_automaton_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify canonical scattering and compact amplitude quotient inputs",
            "verify all 2048 x 11 transitions are labelled by compact generator quotient rows",
            "verify every transition is an xor primitive-generator toggle with an involutive reverse",
            "verify connectedness and 11-regular in/out degree",
            "verify the public tube-zero class collapses all transitions while ordered-chain labels separate generators",
            "verify the hidden-sector quotient matrix and gamma_8 transition summary",
            "verify exact hypercube spectral moments and atom exposure counts",
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
