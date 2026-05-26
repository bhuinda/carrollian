from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, deque
from itertools import combinations
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "finite_virasoro_string_kernel_candidate"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
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


def gf2_rank(vectors: list[int]) -> int:
    basis = [0] * RESIDUE_RANK
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


def gf2_basis(vectors: list[int]) -> list[int]:
    basis: list[int] = []
    for vector in vectors:
        value = vector
        for item in basis:
            value = min(value, value ^ item)
        if value:
            basis.append(value)
            basis.sort(reverse=True)
    return basis


def gf2_span(vectors: list[int]) -> set[int]:
    span = {0}
    for item in gf2_basis(vectors):
        span |= {value ^ item for value in list(span)}
    return span


def orthogonal_masks(vectors: list[int]) -> list[int]:
    return [
        mask
        for mask in range(MODE_COUNT)
        if all(((mask & vector).bit_count() % 2) == 0 for vector in vectors)
    ]


def component_sizes(states: set[int], generator_masks: list[int]) -> list[int]:
    seen: set[int] = set()
    sizes = []
    for state in sorted(states):
        if state in seen:
            continue
        queue: deque[int] = deque([state])
        seen.add(state)
        size = 0
        while queue:
            current = queue.popleft()
            size += 1
            for generator in generator_masks:
                target = current ^ generator
                if target in states and target not in seen:
                    seen.add(target)
                    queue.append(target)
        sizes.append(size)
    return sorted(sizes)


def kernel_spectrum(representatives: list[int], generator_masks: list[int]) -> dict[str, int]:
    return histogram(
        Counter(
            sum(1 if ((representative & generator).bit_count() % 2) == 0 else -1 for generator in generator_masks)
            for representative in representatives
        )
    )


def mode_digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode_mask": int(row["mode_mask"]),
        "support_weight": int(row["support_weight"]),
        "support_generator_ids": row["support_generator_ids"],
        "adjacency_eigenvalue": int(row["adjacency_eigenvalue"]),
        "laplacian_eigenvalue": int(row["laplacian_eigenvalue"]),
        "gamma8_support": bool(row["gamma8_support"]),
        "hidden_projection_type": row["hidden_projection_type"],
        "corrected_hidden_clock_mod26": int(row["corrected_hidden_clock_mod26"]),
        "sector26_optical_clock_mod26": int(row["sector26_optical_clock_mod26"]),
        "active_step_atom_count": int(row["active_step_atom_count"]),
    }


def closure_pair_stats(seed_modes: list[int], mode_rows_by_mask: dict[int, dict[str, Any]]) -> dict[str, Any]:
    closed = 0
    escaped = 0
    escaped_clock_histogram: Counter[int] = Counter()
    for idx, left in enumerate(seed_modes):
        for right in seed_modes[idx:]:
            target = left ^ right
            clock = int(mode_rows_by_mask[target]["sector26_optical_clock_mod26"])
            if clock == 0:
                closed += 1
            else:
                escaped += 1
                escaped_clock_histogram[clock] += 1
    return {
        "unordered_pair_count": len(seed_modes) * (len(seed_modes) + 1) // 2,
        "closed_pair_count": closed,
        "escaped_pair_count": escaped,
        "escaped_clock_histogram": histogram(escaped_clock_histogram),
    }


def quotient_representatives(orthogonal_mask: int) -> list[int]:
    seen: set[int] = set()
    representatives = []
    for mode in range(MODE_COUNT):
        if mode in seen:
            continue
        partner = mode ^ orthogonal_mask
        representatives.append(min(mode, partner))
        seen.add(mode)
        seen.add(partner)
    return representatives


def build_theorem() -> dict[str, Any]:
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    mode_rows = fourier["derived"]["mode_rows"]
    mode_rows_by_mask = {int(row["mode_mask"]): row for row in mode_rows}
    seed_modes = [
        int(row["mode_mask"])
        for row in mode_rows
        if int(row["sector26_optical_clock_mod26"]) == 0
    ]
    nonzero_seed_modes = [mode for mode in seed_modes if mode != 0]
    seed_span = gf2_span(seed_modes)
    seed_orthogonal = orthogonal_masks(seed_modes)
    parity_mask = next(mask for mask in seed_orthogonal if mask != 0)
    parity_generators = bit_ids(parity_mask)
    closure_modes = sorted(seed_span)
    complement_modes = sorted(set(range(MODE_COUNT)) - seed_span)
    preserving_generators = [
        generator_id
        for generator_id in range(RESIDUE_RANK)
        if ((parity_mask >> generator_id) & 1) == 0
    ]
    crossing_generators = [
        generator_id
        for generator_id in range(RESIDUE_RANK)
        if ((parity_mask >> generator_id) & 1) == 1
    ]
    primitive_preserving_masks = [1 << generator_id for generator_id in preserving_generators]
    primitive_crossing_masks = [1 << generator_id for generator_id in crossing_generators]
    paired_cross_return_generators = [
        {
            "generator_pair": [left, right],
            "composite_mask": (1 << left) ^ (1 << right),
            "support_generator_ids": [left, right],
        }
        for left, right in combinations(crossing_generators, 2)
    ]
    paired_cross_return_masks = [
        int(row["composite_mask"]) for row in paired_cross_return_generators
    ]
    internal_generator_masks = primitive_preserving_masks + paired_cross_return_masks
    primitive_component_sizes = component_sizes(seed_span, primitive_preserving_masks)
    composite_component_sizes = component_sizes(seed_span, internal_generator_masks)
    representatives = quotient_representatives(parity_mask)
    spectrum = kernel_spectrum(representatives, internal_generator_masks)
    spectrum_counter = Counter({int(key): value for key, value in spectrum.items()})
    gamma8_mode_mask = 1 << GAMMA8_GENERATOR_ID
    hidden_sign_mode_mask = fourier["derived"]["classifier_summary"]["hidden_clock_mask"]
    seed_pair_stats = closure_pair_stats(seed_modes, mode_rows_by_mask)
    internal_transition_count = len(seed_span) * len(primitive_preserving_masks)
    crossing_transition_count = len(seed_span) * len(primitive_crossing_masks)
    composite_transition_count = len(seed_span) * len(paired_cross_return_masks)

    closure_summary = {
        "kernel_closure_rank": gf2_rank(closure_modes),
        "kernel_closure_mode_count": len(closure_modes),
        "defining_parity_mask": parity_mask,
        "defining_parity_generators": parity_generators,
        "defining_equation": "m_5 + m_9 + m_10 = 0 mod 2",
        "seed_zero_clock_mode_count": len(seed_modes),
        "seed_zero_clock_nonzero_mode_count": len(nonzero_seed_modes),
        "complement_mode_count": len(complement_modes),
        "preserving_primitive_generators": preserving_generators,
        "crossing_primitive_generators": crossing_generators,
        "paired_cross_return_generators": paired_cross_return_generators,
        "primitive_preserving_generator_rank": gf2_rank(primitive_preserving_masks),
        "paired_cross_return_generator_rank": gf2_rank(paired_cross_return_masks),
        "full_internal_generator_rank": gf2_rank(internal_generator_masks),
        "primitive_preserving_component_histogram": histogram(Counter(primitive_component_sizes)),
        "primitive_plus_composite_component_histogram": histogram(Counter(composite_component_sizes)),
    }
    closure_invariants = {
        "sector26_clock_histogram": histogram(
            Counter(
                int(mode_rows_by_mask[mode]["sector26_optical_clock_mod26"])
                for mode in closure_modes
            )
        ),
        "support_weight_histogram": histogram(
            Counter(int(mode_rows_by_mask[mode]["support_weight"]) for mode in closure_modes)
        ),
        "adjacency_eigenvalue_histogram": histogram(
            Counter(
                int(mode_rows_by_mask[mode]["adjacency_eigenvalue"])
                for mode in closure_modes
            )
        ),
        "gamma8_support_histogram": histogram(
            Counter(bool(mode_rows_by_mask[mode]["gamma8_support"]) for mode in closure_modes)
        ),
        "hidden_projection_histogram": histogram(
            Counter(mode_rows_by_mask[mode]["hidden_projection_type"] for mode in closure_modes)
        ),
        "corrected_hidden_clock_mod26_histogram": histogram(
            Counter(
                int(mode_rows_by_mask[mode]["corrected_hidden_clock_mod26"])
                for mode in closure_modes
            )
        ),
    }
    complement_invariants = {
        "sector26_clock_histogram": histogram(
            Counter(
                int(mode_rows_by_mask[mode]["sector26_optical_clock_mod26"])
                for mode in complement_modes
            )
        ),
        "hidden_projection_histogram": histogram(
            Counter(mode_rows_by_mask[mode]["hidden_projection_type"] for mode in complement_modes)
        ),
    }
    kernel_graph = {
        "primitive_internal_directed_transition_count": internal_transition_count,
        "primitive_crossing_directed_transition_count": crossing_transition_count,
        "paired_cross_return_directed_transition_count": composite_transition_count,
        "candidate_internal_generator_count": len(internal_generator_masks),
        "candidate_internal_directed_transition_count": len(seed_span) * len(internal_generator_masks),
        "candidate_internal_undirected_transition_count": len(seed_span)
        * len(internal_generator_masks)
        // 2,
        "candidate_internal_spectrum": spectrum,
        "candidate_internal_spectral_moments": {
            "dimension": sum(spectrum_counter.values()),
            "trace_A": sum(eigenvalue * multiplicity for eigenvalue, multiplicity in spectrum_counter.items()),
            "trace_A2": sum(
                (eigenvalue ** 2) * multiplicity
                for eigenvalue, multiplicity in spectrum_counter.items()
            ),
            "spectral_radius": max(spectrum_counter),
        },
    }

    checks = {
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "seed_zero_clock_fiber_has_83_modes": len(seed_modes) == 83
        and len(nonzero_seed_modes) == 82,
        "seed_zero_clock_fiber_is_not_additively_closed": seed_pair_stats[
            "escaped_pair_count"
        ]
        == 2847
        and seed_pair_stats["closed_pair_count"] == 639,
        "minimal_kernel_closure_has_rank_10_and_1024_modes": closure_summary[
            "kernel_closure_rank"
        ]
        == 10
        and closure_summary["kernel_closure_mode_count"] == 1024,
        "kernel_closure_is_defined_by_5_9_10_parity": parity_mask == 1568
        and parity_generators == [5, 9, 10],
        "kernel_closure_contains_seed_zero_clock_fiber": set(seed_modes).issubset(seed_span),
        "kernel_closure_contains_gamma8_but_not_hidden_sign_mode": gamma8_mode_mask in seed_span
        and hidden_sign_mode_mask not in seed_span,
        "kernel_closure_has_even_sector26_clock_residues_only": sorted(
            int(key) for key in closure_invariants["sector26_clock_histogram"]
        )
        == list(range(0, 26, 2)),
        "kernel_complement_has_odd_sector26_clock_residues_only": sorted(
            int(key) for key in complement_invariants["sector26_clock_histogram"]
        )
        == list(range(1, 26, 2)),
        "primitive_generators_split_as_8_preserving_3_crossing": preserving_generators
        == [0, 1, 2, 3, 4, 6, 7, 8]
        and crossing_generators == [5, 9, 10],
        "primitive_preserving_graph_has_four_256_components": closure_summary[
            "primitive_preserving_component_histogram"
        ]
        == {"256": 4},
        "paired_cross_return_composites_connect_kernel": closure_summary[
            "paired_cross_return_generator_rank"
        ]
        == 2
        and closure_summary["full_internal_generator_rank"] == 10
        and closure_summary["primitive_plus_composite_component_histogram"] == {"1024": 1},
        "kernel_graph_has_degree_11_and_expected_edge_counts": kernel_graph[
            "candidate_internal_generator_count"
        ]
        == 11
        and kernel_graph["candidate_internal_directed_transition_count"] == 11264
        and kernel_graph["candidate_internal_undirected_transition_count"] == 5632,
        "kernel_graph_spectrum_has_expected_dimension_and_moments": kernel_graph[
            "candidate_internal_spectral_moments"
        ]["dimension"]
        == 1024
        and kernel_graph["candidate_internal_spectral_moments"]["trace_A"] == 0
        and kernel_graph["candidate_internal_spectral_moments"]["trace_A2"] == 11264,
        "kernel_closure_keeps_constant_but_excludes_hidden_sign_projection": closure_invariants[
            "hidden_projection_histogram"
        ]
        == {"sector_constant": 1, "sector_orthogonal": 1023},
        "gamma8_support_splits_kernel_evenly": closure_invariants["gamma8_support_histogram"]
        == {"False": 512, "True": 512},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        if all_checks_pass
        else "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.finite_virasoro_string_kernel_candidate",
        "status": status,
        "object": "d20",
        "claim": (
            "The sector-26 optical clock on the finite Fourier mode classifier has a distinguished "
            "clock-zero seed fiber of 83 modes. That seed is not additively closed, but its minimal "
            "F_2-linear closure is a certified rank-10 finite string-kernel candidate: the hyperplane "
            "m_5 + m_9 + m_10 = 0. Eight primitive generators preserve this kernel, while the three "
            "crossing primitive generators close only through paired cross-return composites."
        ),
        "definition": {
            "clock_zero_seed": "The Fourier modes with sector26_optical_clock_mod26 = 0.",
            "finite_string_kernel_candidate": (
                "The minimal F_2-linear span of the clock-zero seed fiber, equivalently the hyperplane "
                "m_5 + m_9 + m_10 = 0 mod 2."
            ),
            "primitive_preserving_generator": (
                "A primitive generator e_i whose addition preserves the candidate hyperplane."
            ),
            "paired_cross_return_composite": (
                "A two-generator move e_i + e_j formed from crossing generators. These are the minimal "
                "closed-return composites needed to connect the candidate kernel internally."
            ),
        },
        "inputs": {
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(FOURIER_MODE_CLASSIFIER_REPORT),
            }
        },
        "derived": {
            "closure_summary": closure_summary,
            "seed_pair_closure_test": seed_pair_stats,
            "kernel_closure_invariants": closure_invariants,
            "kernel_complement_invariants": complement_invariants,
            "kernel_internal_graph": kernel_graph,
            "distinguished_membership": {
                "zero_mode": mode_digest(mode_rows_by_mask[0]),
                "gamma8_basis_mode": mode_digest(mode_rows_by_mask[gamma8_mode_mask]),
                "hidden_kernel_odd_sign_mode": mode_digest(
                    mode_rows_by_mask[hidden_sign_mode_mask]
                ),
                "gamma8_in_kernel_closure": gamma8_mode_mask in seed_span,
                "hidden_sign_mode_in_kernel_closure": hidden_sign_mode_mask in seed_span,
            },
            "clock_zero_seed_modes": [mode_digest(mode_rows_by_mask[mode]) for mode in seed_modes],
            "kernel_closure_mode_masks": closure_modes,
            "kernel_closure_mode_masks_sha256": sha_json(closure_modes),
        },
        "interpretation": {
            "what_this_proves": [
                "the finite sector-26 clock-zero fiber is a certified 83-mode seed, not an additive subspace",
                "the minimal additive closure of that seed is a rank-10 hyperplane with 1024 Fourier modes",
                "gamma_8 lies inside the finite string-kernel candidate, while the hidden kernel/odd sign mode lies outside it",
                "eight primitive moves preserve the kernel and three primitive moves cross it",
                "paired cross-return composites from the three crossing moves are exactly what connect the kernel internally",
            ],
            "what_this_does_not_prove": (
                "This is a finite Virasoro/string-kernel candidate. It does not construct continuum Virasoro "
                "operators, prove BRST cohomology, or identify a physical bosonic string spectrum."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the finite Virasoro generator algebra on the rank-10 kernel: multiply primitive-preserving "
            "moves and paired cross-return composites, then test commutators/relations against the sector-26 clock."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.finite_virasoro_string_kernel_candidate_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the amplitude-quotient Fourier mode classifier input",
            "isolate the sector-26 clock-zero seed fiber",
            "test additive closure of the raw seed fiber",
            "compute the minimal F_2-linear closure and its defining parity equation",
            "classify primitive preserving and crossing generators",
            "verify paired cross-return composites connect the rank-10 kernel",
            "verify gamma_8, hidden-sector, sector-26, and spectral invariants of the candidate kernel",
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
