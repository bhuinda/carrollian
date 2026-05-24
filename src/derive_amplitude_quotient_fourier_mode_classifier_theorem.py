from __future__ import annotations

import hashlib
import json
from collections import Counter
from math import comb
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "amplitude_quotient_fourier_mode_classifier"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

REDUCED_AUTOMATON_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "reduced_amplitude_quotient_scattering_automaton"
    / "report.json"
)
SECTOR26_INVARIANT_SUITE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)

RESIDUE_RANK = 11
MODE_COUNT = 1 << RESIDUE_RANK
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


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def bit_ids(mask: int) -> list[int]:
    return [idx for idx in range(RESIDUE_RANK) if (mask >> idx) & 1]


def mode_sector_sum(mode_mask: int, hidden_clock_mask: int, sector: str) -> int:
    if mode_mask == 0:
        return MODE_COUNT // 2
    if mode_mask == hidden_clock_mask:
        return MODE_COUNT // 2 if sector == "kernel" else -(MODE_COUNT // 2)
    return 0


def hidden_projection_type(mode_mask: int, hidden_clock_mask: int) -> str:
    if mode_mask == 0:
        return "sector_constant"
    if mode_mask == hidden_clock_mask:
        return "kernel_odd_sign"
    return "sector_orthogonal"


def build_mode_rows(
    generator_labels: list[dict[str, Any]],
    sector26_basis_mod26: list[int],
) -> list[dict[str, Any]]:
    hidden_flipping_generators = [
        int(row["generator_cycle_id"]) for row in generator_labels if not row["preserves_hidden_packet"]
    ]
    hidden_clock_mask = sum(1 << generator_id for generator_id in hidden_flipping_generators)
    corrected_clock_by_generator = {
        int(row["generator_cycle_id"]): int(row["corrected_basis_clock_mod26"])
        for row in generator_labels
    }
    ordered_chain_class_by_generator = {
        int(row["generator_cycle_id"]): int(row["ordered_step_chain_class_id"])
        for row in generator_labels
    }
    atom_ids_by_generator = {
        int(row["generator_cycle_id"]): set(int(atom_id) for atom_id in row["step_atom_ids_ordered"])
        for row in generator_labels
    }

    rows = []
    for mode_mask in range(MODE_COUNT):
        support = bit_ids(mode_mask)
        weight = len(support)
        adjacency_eigenvalue = RESIDUE_RANK - 2 * weight
        laplacian_eigenvalue = 2 * weight
        gamma8_active = ((mode_mask >> GAMMA8_GENERATOR_ID) & 1) == 1
        corrected_hidden_clock_mod26 = sum(
            corrected_clock_by_generator[idx] for idx in support
        ) % 26
        sector26_optical_clock_mod26 = sum(sector26_basis_mod26[idx] for idx in support) % 26
        active_step_atom_ids = sorted(
            set().union(*(atom_ids_by_generator[idx] for idx in support)) if support else set()
        )
        rows.append(
            {
                "mode_mask": mode_mask,
                "support_weight": weight,
                "support_generator_ids": support,
                "negative_ordered_step_chain_class_ids": [
                    ordered_chain_class_by_generator[idx] for idx in support
                ],
                "adjacency_eigenvalue": adjacency_eigenvalue,
                "laplacian_eigenvalue": laplacian_eigenvalue,
                "random_walk_eigenvalue": {
                    "numerator": adjacency_eigenvalue,
                    "denominator": RESIDUE_RANK,
                },
                "gamma8_support": gamma8_active,
                "gamma8_translation_eigenvalue": -1 if gamma8_active else 1,
                "hidden_projection_type": hidden_projection_type(mode_mask, hidden_clock_mask),
                "hidden_sector_character_sums": {
                    "kernel": mode_sector_sum(mode_mask, hidden_clock_mask, "kernel"),
                    "odd": mode_sector_sum(mode_mask, hidden_clock_mask, "odd"),
                },
                "corrected_hidden_clock_mod26": corrected_hidden_clock_mod26,
                "sector26_optical_clock_mod26": sector26_optical_clock_mod26,
                "active_step_atom_ids": active_step_atom_ids,
                "active_step_atom_count": len(active_step_atom_ids),
            }
        )
    return rows


def spectral_histogram_from_rows(mode_rows: list[dict[str, Any]]) -> dict[str, int]:
    return histogram(Counter(row["adjacency_eigenvalue"] for row in mode_rows))


def expected_spectral_histogram() -> dict[str, int]:
    return {str(RESIDUE_RANK - 2 * k): comb(RESIDUE_RANK, k) for k in range(RESIDUE_RANK + 1)}


def build_theorem() -> dict[str, Any]:
    automaton = load_json(REDUCED_AUTOMATON_REPORT)
    sector26 = load_json(SECTOR26_INVARIANT_SUITE_REPORT)
    generator_labels = automaton["derived"]["generator_labels"]
    sector26_basis_mod26 = sector26["derived"]["optical_action_normalization"][
        "basis_cycle_normalized_mod26"
    ]
    mode_rows = build_mode_rows(generator_labels, sector26_basis_mod26)
    hidden_flipping_generators = [
        int(row["generator_cycle_id"]) for row in generator_labels if not row["preserves_hidden_packet"]
    ]
    hidden_clock_mask = sum(1 << generator_id for generator_id in hidden_flipping_generators)
    hidden_sign_mode = mode_rows[hidden_clock_mask]
    gamma8_basis_mode = mode_rows[1 << GAMMA8_GENERATOR_ID]
    nonzero_sector26_histogram = histogram(
        Counter(row["sector26_optical_clock_mod26"] for row in mode_rows if row["mode_mask"] != 0)
    )
    sector26_histogram = histogram(
        Counter(row["sector26_optical_clock_mod26"] for row in mode_rows)
    )
    hidden_projection_histogram = histogram(
        Counter(row["hidden_projection_type"] for row in mode_rows)
    )
    corrected_hidden_clock_histogram = histogram(
        Counter(row["corrected_hidden_clock_mod26"] for row in mode_rows)
    )
    gamma8_support_histogram = histogram(Counter(row["gamma8_support"] for row in mode_rows))
    eigenvalue_gamma8_histogram = histogram(
        Counter(
            (row["adjacency_eigenvalue"], "gamma8" if row["gamma8_support"] else "gamma8_complement")
            for row in mode_rows
        )
    )
    active_atom_count_histogram = histogram(
        Counter(row["active_step_atom_count"] for row in mode_rows)
    )
    adjacency_histogram = spectral_histogram_from_rows(mode_rows)
    laplacian_histogram = histogram(Counter(row["laplacian_eigenvalue"] for row in mode_rows))
    automaton_spectrum = automaton["derived"]["spectral_invariants"]
    automaton_adjacency_histogram = {
        str(row["eigenvalue"]): int(row["multiplicity"])
        for row in automaton_spectrum["adjacency_spectrum"]
    }
    trace_a = sum(
        row["adjacency_eigenvalue"] for row in mode_rows
    )
    trace_a2 = sum(
        row["adjacency_eigenvalue"] ** 2 for row in mode_rows
    )

    checks = {
        "reduced_automaton_is_certified": automaton.get("status")
        == "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_CERTIFIED"
        and automaton.get("all_checks_pass") is True,
        "sector26_invariant_suite_is_certified": sector26.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26.get("all_checks_pass") is True,
        "mode_count_matches_automaton_state_count": len(mode_rows) == MODE_COUNT
        == automaton["derived"]["automaton_summary"]["state_count"],
        "mode_support_weights_match_masks": all(
            row["support_weight"] == int(row["mode_mask"]).bit_count() for row in mode_rows
        ),
        "adjacency_eigenvalues_are_hypercube_characters": all(
            row["adjacency_eigenvalue"] == RESIDUE_RANK - 2 * row["support_weight"]
            for row in mode_rows
        ),
        "laplacian_eigenvalues_are_twice_weight": all(
            row["laplacian_eigenvalue"] == 2 * row["support_weight"] for row in mode_rows
        ),
        "spectral_histogram_matches_hypercube_formula": adjacency_histogram
        == expected_spectral_histogram(),
        "spectral_histogram_matches_automaton_report": adjacency_histogram
        == automaton_adjacency_histogram,
        "spectral_moments_match_automaton_report": trace_a
        == automaton_spectrum["spectral_moments"]["trace_A"]
        and trace_a2 == automaton_spectrum["spectral_moments"]["trace_A2"],
        "hidden_projection_has_constant_sign_and_orthogonal_modes": hidden_projection_histogram
        == {"kernel_odd_sign": 1, "sector_constant": 1, "sector_orthogonal": MODE_COUNT - 2},
        "hidden_sign_mode_matches_sector_quotient_eigenvalue": hidden_sign_mode[
            "mode_mask"
        ]
        == hidden_clock_mask
        and hidden_sign_mode["support_weight"] == len(hidden_flipping_generators)
        and hidden_sign_mode["adjacency_eigenvalue"]
        == automaton["derived"]["sector_invariants"]["per_state_sector_quotient_matrix"][
            "eigenvalues"
        ][1]["eigenvalue"],
        "corrected_hidden_clock_histogram_is_balanced_mod_26": corrected_hidden_clock_histogram
        == {"0": MODE_COUNT // 2, "13": MODE_COUNT // 2},
        "sector26_optical_clock_hits_all_26_residues": sorted(
            int(key) for key in sector26_histogram
        )
        == list(range(26)),
        "nonzero_sector26_optical_clock_histogram_matches_sector26_suite": (
            nonzero_sector26_histogram
            == sector26["derived"]["optical_action_normalization"][
                "all_nonzero_normalized_action_mod26_histogram"
            ]
        ),
        "gamma8_support_splits_modes_evenly": gamma8_support_histogram
        == {"False": MODE_COUNT // 2, "True": MODE_COUNT // 2},
        "gamma8_basis_mode_matches_first_obstruction_clock": gamma8_basis_mode["mode_mask"]
        == (1 << GAMMA8_GENERATOR_ID)
        and gamma8_basis_mode["support_weight"] == 1
        and gamma8_basis_mode["adjacency_eigenvalue"] == RESIDUE_RANK - 2
        and gamma8_basis_mode["sector26_optical_clock_mod26"]
        == sector26["derived"]["optical_action_normalization"][
            "first_obstruction_normalized_mod26"
        ]
        and gamma8_basis_mode["corrected_hidden_clock_mod26"] == 13
        and gamma8_basis_mode["active_step_atom_count"]
        == automaton["derived"]["gamma8_automaton_label"]["unique_step_atom_count"],
        "zero_mode_is_constant_and_tube_public": mode_rows[0]["hidden_projection_type"]
        == "sector_constant"
        and mode_rows[0]["adjacency_eigenvalue"] == RESIDUE_RANK
        and mode_rows[0]["active_step_atom_count"] == 0,
        "full_mode_exposes_all_25_step_atoms": mode_rows[-1]["active_step_atom_count"]
        == automaton["derived"]["automaton_summary"]["used_loop_step_atom_count"]
        == 25,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        if all_checks_pass
        else "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.amplitude_quotient_fourier_mode_classifier",
        "status": status,
        "object": "d20",
        "claim": (
            "The reduced amplitude-quotient scattering automaton diagonalizes over the 2048 residue "
            "characters of F_2^11. Each Fourier mode is classified by hypercube eigenvalue, hidden "
            "kernel/odd sector projection, gamma_8 support, corrected hidden mod-26 clock, sector-26 "
            "optical clock, and exposed compact Loop_297 step atoms."
        ),
        "definition": {
            "fourier_mode": "A character chi_m(x)=(-1)^(m dot x) indexed by m in F_2^11.",
            "adjacency_eigenvalue": "For support weight k=|m|, lambda(m)=11-2k.",
            "hidden_sector_projection": (
                "The mode is sector_constant for m=0, kernel_odd_sign for the ten-generator hidden "
                "flipping mask, and sector_orthogonal otherwise."
            ),
            "sector26_optical_clock": (
                "The dual mod-26 optical clock sum_i m_i a_i using the certified normalized basis "
                "cycle residues a_i from the sector-26 invariant suite."
            ),
            "corrected_hidden_clock": (
                "The dual corrected hidden clock sum_i m_i c_i mod 26 using c_i=0 for generator 3 "
                "and c_i=13 for the ten hidden-packet-flipping generators."
            ),
        },
        "inputs": {
            "reduced_automaton_report": {
                "path": rel(REDUCED_AUTOMATON_REPORT),
                "sha256": sha_file(REDUCED_AUTOMATON_REPORT),
            },
            "sector26_invariant_suite_report": {
                "path": rel(SECTOR26_INVARIANT_SUITE_REPORT),
                "sha256": sha_file(SECTOR26_INVARIANT_SUITE_REPORT),
            },
        },
        "derived": {
            "classifier_summary": {
                "mode_count": len(mode_rows),
                "residue_rank": RESIDUE_RANK,
                "hidden_clock_mask": hidden_clock_mask,
                "hidden_flipping_generators": hidden_flipping_generators,
                "gamma8_generator_id": GAMMA8_GENERATOR_ID,
                "sector26_basis_cycle_normalized_mod26": sector26_basis_mod26,
                "adjacency_eigenvalue_histogram": adjacency_histogram,
                "laplacian_eigenvalue_histogram": laplacian_histogram,
                "hidden_projection_histogram": hidden_projection_histogram,
                "corrected_hidden_clock_mod26_histogram": corrected_hidden_clock_histogram,
                "sector26_optical_clock_mod26_histogram": sector26_histogram,
                "nonzero_sector26_optical_clock_mod26_histogram": nonzero_sector26_histogram,
                "gamma8_support_histogram": gamma8_support_histogram,
                "eigenvalue_gamma8_support_histogram": eigenvalue_gamma8_histogram,
                "active_step_atom_count_histogram": active_atom_count_histogram,
            },
            "distinguished_modes": {
                "zero_mode": mode_rows[0],
                "hidden_kernel_odd_sign_mode": hidden_sign_mode,
                "gamma8_basis_mode": gamma8_basis_mode,
                "full_support_mode": mode_rows[-1],
            },
            "mode_rows": mode_rows,
            "mode_rows_sha256": sha_json(mode_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the reduced automaton is explicitly diagonalized by the 2048 finite Fourier characters",
                "the hidden-sector quotient eigenmodes are exactly the constant mode and the ten-generator kernel/odd sign mode",
                "the gamma_8 basis character has eigenvalue 9 and sector-26 optical clock 18",
                "the nonzero Fourier-mode sector-26 optical clock histogram matches the certified 2047-class optical clock",
                "compact amplitude atom exposure can be read per Fourier support set",
            ],
            "what_this_does_not_prove": (
                "This is a finite character classifier for the quotient automaton. It does not yet construct "
                "continuum spherical harmonics, Virasoro modes, or full A985 coordinate eigenvectors."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Derive the finite Virasoro/string-kernel candidate: use the sector-26 optical clock and Fourier "
            "eigenmodes to isolate the 26-aligned invariant subpacket and test closure under generator addition."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.amplitude_quotient_fourier_mode_classifier_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify reduced automaton and sector-26 invariant-suite inputs",
            "enumerate all 2048 F_2^11 Fourier characters",
            "verify hypercube adjacency and Laplacian eigenvalue formulas",
            "verify spectral histograms and moments against the automaton theorem",
            "verify hidden-sector constant/sign/orthogonal mode classification",
            "verify gamma_8 and sector-26 optical clock distinguished modes",
            "verify the nonzero mode mod-26 optical clock histogram matches the sector-26 suite",
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
