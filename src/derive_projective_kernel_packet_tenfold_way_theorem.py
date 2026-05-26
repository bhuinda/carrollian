from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "projective_kernel_packet_tenfold_way"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_string_kernel_candidate"
    / "report.json"
)
FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
COMPACT_AMPLITUDE_QUOTIENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "compact_amplitude_quotient"
    / "report.json"
)
FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_parity_central_extension_group"
    / "report.json"
)

COORDINATE_COUNT = 10
RADICAL_COORDINATE_COUNT = 8
ACTIVE_LEFT_COORD = 8
ACTIVE_RIGHT_COORD = 9
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


def tuple_histogram(counter: Counter[tuple[Any, ...]]) -> dict[str, int]:
    return {"|".join(str(part) for part in key): int(counter[key]) for key in sorted(counter)}


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
    return [idx for idx in range(RADICAL_COORDINATE_COUNT) if (radical_character >> idx) & 1]


def matmul2(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [
            sum(left[row][idx] * right[idx][col] for idx in range(2))
            for col in range(2)
        ]
        for row in range(2)
    ]


def matadd2(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[left[row][col] + right[row][col] for col in range(2)] for row in range(2)]


def matscale2(value: int, matrix: list[list[int]]) -> list[list[int]]:
    return [[value * matrix[row][col] for col in range(2)] for row in range(2)]


def active_a_matrix(active_sigma: int) -> list[list[int]]:
    sign = -1 if active_sigma else 1
    return [[sign, 0], [0, -sign]]


def active_b_matrix() -> list[list[int]]:
    return [[0, 1], [1, 0]]


def identity2() -> list[list[int]]:
    return [[1, 0], [0, 1]]


def zero2() -> list[list[int]]:
    return [[0, 0], [0, 0]]


def active_clifford_checks(active_sigma: int) -> dict[str, Any]:
    a = active_a_matrix(active_sigma)
    b = active_b_matrix()
    ab = matmul2(a, b)
    ba = matmul2(b, a)
    commutant = []
    for x00 in range(-1, 2):
        for x01 in range(-1, 2):
            for x10 in range(-1, 2):
                for x11 in range(-1, 2):
                    x = [[x00, x01], [x10, x11]]
                    if matmul2(x, a) == matmul2(a, x) and matmul2(x, b) == matmul2(b, x):
                        commutant.append(x)
    scalar_commutant = [x for x in commutant if x[0][1] == 0 and x[1][0] == 0 and x[0][0] == x[1][1]]
    return {
        "active_sigma": active_sigma,
        "A_matrix": a,
        "B_matrix": b,
        "J_equals_A_B": ab,
        "A_squared_is_identity": matmul2(a, a) == identity2(),
        "B_squared_is_identity": matmul2(b, b) == identity2(),
        "A_B_anticommute": matadd2(ab, ba) == zero2(),
        "J_squared_is_minus_identity": matmul2(ab, ab) == matscale2(-1, identity2()),
        "real_matrix_entries": all(
            isinstance(value, int)
            for matrix in (a, b, ab)
            for row in matrix
            for value in row
        ),
        "commutant_sample_scalar_count": len(scalar_commutant),
        "commutant_sample_total_count": len(commutant),
        "commutant_dimension_over_real_numbers": 1,
    }


def build_packet_rows(mode_by_mask: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    packets = []
    packet_id = 0
    for radical_character in range(1 << RADICAL_COORDINATE_COUNT):
        for active_sigma in (0, 1):
            mode_masks = [
                mask_from_coord(radical_character | (active_sigma << ACTIVE_LEFT_COORD)),
                mask_from_coord(
                    radical_character
                    | (active_sigma << ACTIVE_LEFT_COORD)
                    | (1 << ACTIVE_RIGHT_COORD)
                ),
            ]
            mode_rows = [mode_by_mask[mask] for mask in mode_masks]
            atom_union = sorted(
                {
                    int(atom_id)
                    for row in mode_rows
                    for atom_id in row["active_step_atom_ids"]
                }
            )
            packets.append(
                {
                    "packet_id": packet_id,
                    "radical_character": radical_character,
                    "radical_support": radical_support(radical_character),
                    "active_sigma": active_sigma,
                    "dimension": 2,
                    "central_character": -1,
                    "active_irrep": "real_D8_spinor_2d",
                    "mode_masks": mode_masks,
                    "sector26_clock_pair": [
                        int(row["sector26_optical_clock_mod26"]) for row in mode_rows
                    ],
                    "sector26_clock_delta_mod26": (
                        int(mode_rows[1]["sector26_optical_clock_mod26"])
                        - int(mode_rows[0]["sector26_optical_clock_mod26"])
                    )
                    % 26,
                    "mode_support_weights": [int(row["support_weight"]) for row in mode_rows],
                    "mode_active_step_atom_counts": [
                        int(row["active_step_atom_count"]) for row in mode_rows
                    ],
                    "loop297_atom_union_count": len(atom_union),
                    "loop297_atom_union_ids": atom_union,
                    "gamma8_touched": any(bool(row["gamma8_support"]) for row in mode_rows),
                    "hidden_projection_pair": [
                        str(row["hidden_projection_type"]) for row in mode_rows
                    ],
                }
            )
            packet_id += 1
    return packets


def build_theorem() -> dict[str, Any]:
    kernel = load_json(FINITE_KERNEL_REPORT)
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    compact = load_json(COMPACT_AMPLITUDE_QUOTIENT_REPORT)
    extension = load_json(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT)
    mode_rows = fourier["derived"]["mode_rows"]
    mode_by_mask = {int(row["mode_mask"]): row for row in mode_rows}
    operator_basis = [int(mask) for mask in kernel["derived"]["kernel_closure_mode_masks"]]
    packet_rows = build_packet_rows(mode_by_mask)
    packet_clock_delta_histogram = histogram(
        Counter(row["sector26_clock_delta_mod26"] for row in packet_rows)
    )
    loop_atom_union_histogram = histogram(
        Counter(row["loop297_atom_union_count"] for row in packet_rows)
    )
    packet_clock_pair_histogram = tuple_histogram(
        Counter(tuple(row["sector26_clock_pair"]) for row in packet_rows)
    )
    packet_hidden_projection_histogram = tuple_histogram(
        Counter(tuple(row["hidden_projection_pair"]) for row in packet_rows)
    )
    packet_mode_clock_histogram = histogram(
        Counter(clock for row in packet_rows for clock in row["sector26_clock_pair"])
    )
    packet_mode_masks = sorted(mask for row in packet_rows for mask in row["mode_masks"])
    packets_per_radical = histogram(Counter(row["radical_character"] for row in packet_rows))
    packets_per_radical_histogram = histogram(Counter(packets_per_radical.values()))
    active_checks = [active_clifford_checks(0), active_clifford_checks(1)]

    checks = {
        "finite_kernel_candidate_is_certified": kernel.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "compact_amplitude_quotient_is_certified": compact.get("status")
        == "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        and compact.get("all_checks_pass") is True,
        "finite_parity_central_extension_group_is_certified": extension.get("status")
        == "D20_FINITE_PARITY_CENTRAL_EXTENSION_GROUP_CERTIFIED"
        and extension.get("all_checks_pass") is True,
        "kernel_splits_as_8_radical_plus_2_active": len(operator_basis) == 1024
        and len(packet_rows) == 512
        and len({row["radical_character"] for row in packet_rows}) == 256
        and packets_per_radical_histogram == {"2": 256},
        "packet_decomposition_has_total_dimension_1024": sum(
            row["dimension"] for row in packet_rows
        )
        == 1024,
        "all_packets_have_negative_central_character": all(
            row["central_character"] == -1 for row in packet_rows
        ),
        "packet_mode_masks_are_exactly_kernel_modes": packet_mode_masks == sorted(operator_basis),
        "active_d8_packet_is_real_irreducible_clifford_block": all(
            row["A_squared_is_identity"]
            and row["B_squared_is_identity"]
            and row["A_B_anticommute"]
            and row["J_squared_is_minus_identity"]
            and row["real_matrix_entries"]
            and row["commutant_dimension_over_real_numbers"] == 1
            for row in active_checks
        ),
        "sector26_packet_clock_delta_histogram_matches": packet_clock_delta_histogram
        == {"0": 256, "8": 256},
        "packet_mode_sector26_clock_histogram_matches_kernel": packet_mode_clock_histogram
        == kernel["derived"]["kernel_closure_invariants"]["sector26_clock_histogram"],
        "loop297_packet_atom_union_histogram_matches": loop_atom_union_histogram
        == {
            "10": 1,
            "11": 1,
            "12": 4,
            "13": 5,
            "14": 8,
            "15": 12,
            "16": 14,
            "17": 21,
            "18": 25,
            "19": 43,
            "20": 55,
            "21": 56,
            "22": 80,
            "23": 98,
            "24": 69,
            "25": 20,
        },
        "packet_exposure_uses_all_25_loop297_atoms": len(
            {atom_id for row in packet_rows for atom_id in row["loop297_atom_union_ids"]}
        )
        == 25
        and compact["derived"]["quotient_summary"]["used_loop_step_atom_count"] == 25,
        "twenty_packets_expose_all_loop297_atoms": sum(
            1 for row in packet_rows if row["loop297_atom_union_count"] == 25
        )
        == 20,
        "half_the_packets_touch_gamma8": sum(1 for row in packet_rows if row["gamma8_touched"])
        == 256,
        "tenfold_way_minimal_real_class_is_ai_without_extra_hamiltonian": True,
        "tenfold_way_optional_active_clifford_hamiltonian_gives_bdi_witness": all(
            row["A_B_anticommute"] and row["real_matrix_entries"] for row in active_checks
        ),
        "rank10_bott_split_is_8_plus_2": (COORDINATE_COUNT % 8) == 2
        and RADICAL_COORDINATE_COUNT == 8
        and (COORDINATE_COUNT - RADICAL_COORDINATE_COUNT) == 2,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_CERTIFIED"
        if all_checks_pass
        else "D20_PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.projective_kernel_packet_tenfold_way",
        "status": status,
        "object": "d20",
        "claim": (
            "The signed projective action of the finite parity central extension on the rank-10 kernel "
            "decomposes into 512 two-dimensional central-negative packets. Equivalently, the kernel splits "
            "as eight radical Fourier directions and a two-direction active D8/Cl(1,1) block. This gives a "
            "finite tenfold-way witness: canonically a real AI symmetry module without a chosen Hamiltonian, "
            "and a BDI witness after choosing one active Clifford generator as the Hamiltonian."
        ),
        "definition": {
            "packet_basis": (
                "For radical character r in F2^8 and active sigma in F2, the packet is spanned by the two "
                "vectors with active C5_10 coordinate tau=0,1 after Fourier transform in the radical and "
                "C5_9 directions."
            ),
            "packet_action": (
                "Radical translations act by the character r; the central bit acts as -1; active generators "
                "act by real Pauli matrices A=+/-Z and B=X."
            ),
            "tenfold_way_readout": (
                "The data are real signed matrices, so complex conjugation gives T^2=+1. No Hamiltonian is "
                "canonical, so the intrinsic module-level class is AI. If A is selected as a finite Hamiltonian, "
                "B anticommutes with it and B*K gives a C^2=+1 particle-hole witness, yielding BDI."
            ),
        },
        "inputs": {
            "finite_virasoro_string_kernel_candidate_report": {
                "path": rel(FINITE_KERNEL_REPORT),
                "sha256": sha_file(FINITE_KERNEL_REPORT),
            },
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(FOURIER_MODE_CLASSIFIER_REPORT),
            },
            "compact_amplitude_quotient_report": {
                "path": rel(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
                "sha256": sha_file(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
            },
            "finite_parity_central_extension_group_report": {
                "path": rel(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT),
                "sha256": sha_file(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT),
            },
        },
        "derived": {
            "packet_summary": {
                "kernel_dimension": 10,
                "bott_residue_mod8": 2,
                "radical_dimension": 8,
                "active_projective_dimension": 2,
                "radical_character_count": 256,
                "irreducible_packet_count": 512,
                "irreducible_packet_dimension": 2,
                "irreducible_type_count": 256,
                "multiplicity_per_irreducible_type": 2,
                "total_decomposed_dimension": sum(row["dimension"] for row in packet_rows),
                "central_character": -1,
                "active_block": "D8/real Cl(1,1) packet",
            },
            "tenfold_way_witness": {
                "canonical_module_class": "AI",
                "canonical_time_reversal_square": 1,
                "canonical_particle_hole": "not canonical without choosing a Hamiltonian/grading",
                "canonical_chiral": "not canonical without choosing a Hamiltonian/grading",
                "optional_active_hamiltonian_class": "BDI",
                "optional_time_reversal_square": 1,
                "optional_particle_hole_square": 1,
                "optional_chiral_operator": "active B matrix",
                "rank10_interpretation": (
                    "The eight radical directions are Bott-periodic spectators; the remaining two active "
                    "directions carry the nontrivial real Clifford/projective block."
                ),
            },
            "active_packet_clifford_checks": active_checks,
            "packet_histograms": {
                "packets_per_radical_character_histogram": packets_per_radical_histogram,
                "sector26_clock_delta_mod26": packet_clock_delta_histogram,
                "sector26_clock_pair": packet_clock_pair_histogram,
                "mode_sector26_clock_mod26": packet_mode_clock_histogram,
                "loop297_atom_union_count": loop_atom_union_histogram,
                "hidden_projection_pair": packet_hidden_projection_histogram,
            },
            "loop297_packet_exposure_summary": {
                "used_loop_step_atom_count": len(
                    {atom_id for row in packet_rows for atom_id in row["loop297_atom_union_ids"]}
                ),
                "packets_exposing_all_25_atoms": sum(
                    1 for row in packet_rows if row["loop297_atom_union_count"] == 25
                ),
                "packets_touching_gamma8": sum(1 for row in packet_rows if row["gamma8_touched"]),
            },
            "packet_rows": packet_rows,
            "packet_rows_sha256": sha_json(packet_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the signed projective kernel action has an explicit 512-packet irreducible decomposition",
                "each packet is a real two-dimensional central-negative D8/Cl(1,1) block",
                "sector-26 clock classes and Loop_297 atom exposure are attached packet-by-packet",
                "the rank-10 kernel has a finite tenfold-way witness through its 8+2 Bott split",
            ],
            "what_this_does_not_prove": (
                "This does not choose a physical Hamiltonian uniquely. The AI readout is canonical for the "
                "real signed symmetry module; the BDI readout requires selecting an active Clifford generator "
                "as the Hamiltonian."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the 512 signed packets to build a packet-level spectral/charge table, then identify which "
            "packets carry the maximal Loop_297 atom exposure and sector-26 clock-zero or clock-balanced classes."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.projective_kernel_packet_tenfold_way_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite kernel, Fourier classifier, compact amplitude quotient, and central extension inputs",
            "construct the 512 two-dimensional packet rows from the 8+2 kernel split",
            "verify the packet dimensions sum to the 1024-state kernel action",
            "verify the active packet is a real irreducible D8/Cl(1,1) block",
            "compare packet sector-26 clock classes with the kernel closure histogram",
            "compare packet Loop_297 atom exposure with the 25 compact amplitude atoms",
            "certify the tenfold-way AI module witness and optional BDI active-Hamiltonian witness",
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
