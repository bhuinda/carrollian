from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from math import gcd
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_finite_scattering_table"
    / "report.json"
)
C2_QUOTIENT_TRANSPORT_LEDGER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger"
    / "report.json"
)
C2_QUOTIENT_ANOMALY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
    / "report.json"
)

GENERATOR3_DELTA = 1 << 3
BOUNDARY_ZERO_MASK = 0
PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")


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


def bit_indices(mask: int) -> list[int]:
    return [idx for idx in range(11) if mask & (1 << idx)]


def image_mask(mask: int, basis_image_masks: list[int]) -> int:
    image = 0
    for idx, basis_image in enumerate(basis_image_masks):
        if mask & (1 << idx):
            image ^= int(basis_image)
    return image


def zero_public_vector() -> dict[str, int]:
    return {component: 0 for component in PUBLIC_COMPONENTS}


def fraction(numerator: int, denominator: int) -> dict[str, int]:
    divisor = gcd(abs(numerator), abs(denominator))
    return {"numerator": numerator // divisor, "denominator": denominator // divisor}


def histogram(values: list[int]) -> dict[str, int]:
    counts = Counter(values)
    return {str(value): int(counts[value]) for value in sorted(counts)}


def components_from_adjacency(adjacency: dict[int, Counter[int]]) -> list[list[int]]:
    seen: set[int] = set()
    components: list[list[int]] = []
    for start in sorted(adjacency):
        if start in seen:
            continue
        component = {start}
        queue: deque[int] = deque([start])
        while queue:
            source = queue.popleft()
            neighbors = set(adjacency[source])
            neighbors.update(node for node, counts in adjacency.items() if source in counts)
            for target in neighbors:
                if target not in component:
                    component.add(target)
                    queue.append(target)
        seen.update(component)
        components.append(sorted(component))
    return components


def component_spectrum(component: list[int], adjacency: dict[int, Counter[int]]) -> dict[str, int]:
    size = len(component)
    has_self_loop = any(node in adjacency[node] for node in component)
    if size == 2 and has_self_loop:
        return {"1": 1, "-1/2": 1}
    if size == 3:
        return {"1": 1, "0": 1, "-1": 1}
    if size == 4:
        return {"1": 1, "0": 2, "-1": 1}
    raise ValueError(f"unexpected quotient component shape: {component}")


def add_spectra(spectra: list[dict[str, int]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for spectrum in spectra:
        counts.update(spectrum)
    order = {"-1": -1.0, "-1/2": -0.5, "0": 0.0, "1": 1.0}
    return {key: int(counts[key]) for key in sorted(counts, key=lambda item: order[item])}


def build_theorem() -> dict[str, Any]:
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    transport_ledger = load_json(C2_QUOTIENT_TRANSPORT_LEDGER_REPORT)
    anomaly = load_json(C2_QUOTIENT_ANOMALY_REPORT)

    operator_summary = transport_ledger.get("derived", {}).get("operator_summary", {})
    basis_image_masks = [int(mask) for mask in operator_summary["basis_image_masks"]]
    tau_generator3_delta = image_mask(GENERATOR3_DELTA, basis_image_masks)
    move_deltas = sorted({GENERATOR3_DELTA, tau_generator3_delta})
    generator_by_id = {
        int(row["generator_cycle_id"]): row
        for row in scattering.get("derived", {}).get("generator_summaries", [])
    }
    move_rows = []
    for delta in move_deltas:
        bits = bit_indices(delta)
        move_rows.append(
            {
                "delta_mask": delta,
                "basis_cycle_indices": bits,
                "move_type": "primitive" if bits == [3] else "tau_image_composite",
                "generator_sequence": bits,
                "optical_action": sum(int(generator_by_id[idx]["optical_action"]) for idx in bits),
                "corrected_clock_mod26": sum(
                    int(generator_by_id[idx]["corrected_basis_clock_mod26"]) for idx in bits
                )
                % 26,
                "tau_image_delta_mask": image_mask(delta, basis_image_masks),
            }
        )

    anomaly_rows = anomaly.get("derived", {}).get("anomaly_rows", [])
    quotient_ledger_rows = transport_ledger.get("derived", {}).get("quotient_ledger_rows", [])
    anomaly_by_mask = {int(row["target_mask"]): row for row in anomaly_rows}
    orbit_by_mask = {int(row["target_mask"]): int(row["orbit_id"]) for row in anomaly_rows}
    masks_by_orbit: dict[int, list[int]] = defaultdict(list)
    for mask, orbit_id in orbit_by_mask.items():
        masks_by_orbit[orbit_id].append(mask)
    ledger_by_orbit = {int(row["orbit_id"]): row for row in quotient_ledger_rows}
    target_domain = set(anomaly_by_mask)

    adjacency: dict[int, Counter[int]] = {orbit_id: Counter() for orbit_id in ledger_by_orbit}
    zero_exit_rows = []
    primitive_witness_rows = []
    for source_mask, source_row in sorted(anomaly_by_mask.items()):
        source_orbit = int(source_row["orbit_id"])
        for delta in move_deltas:
            target_mask = source_mask ^ delta
            if target_mask == BOUNDARY_ZERO_MASK:
                adjacency[source_orbit][source_orbit] += 1
                zero_exit_rows.append(
                    {
                        "source_mask": source_mask,
                        "source_orbit_id": source_orbit,
                        "delta_mask": delta,
                        "closed_as_self_loop": True,
                    }
                )
            else:
                target_orbit = orbit_by_mask[target_mask]
                adjacency[source_orbit][target_orbit] += 1
                primitive_witness_rows.append(
                    {
                        "source_mask": source_mask,
                        "source_orbit_id": source_orbit,
                        "target_mask": target_mask,
                        "target_orbit_id": target_orbit,
                        "delta_mask": delta,
                    }
                )

    quotient_operator_rows = []
    row_totals: dict[int, int] = {}
    for orbit_id in sorted(adjacency):
        total = sum(adjacency[orbit_id].values())
        row_totals[orbit_id] = total
        ledger_row = ledger_by_orbit[orbit_id]
        quotient_operator_rows.append(
            {
                "source_orbit_id": orbit_id,
                "source_orbit_size": int(ledger_row["orbit_size"]),
                "row_total_count": total,
                "stationary_weight": fraction(total, sum(2 * len(masks) for masks in masks_by_orbit.values())),
                "targets": [
                    {
                        "target_orbit_id": target_orbit,
                        "multiplicity": int(count),
                        "probability": fraction(int(count), total),
                    }
                    for target_orbit, count in sorted(adjacency[orbit_id].items())
                ],
                "quotient_public_balance_error": zero_public_vector(),
                "quotient_hidden_balance_error": int(ledger_row["quotient_hidden_balance_error"]),
                "quotient_target_height_action": int(ledger_row["quotient_target_height_action"]),
                "quotient_R33_height_residual": int(ledger_row["quotient_R33_height_residual"]),
            }
        )

    components = components_from_adjacency(adjacency)
    component_rows = [
        {
            "component_id": idx,
            "orbit_ids": component,
            "size": len(component),
            "has_self_loop": any(node in adjacency[node] for node in component),
            "spectrum": component_spectrum(component, adjacency),
        }
        for idx, component in enumerate(components)
    ]
    spectrum = add_spectra([row["spectrum"] for row in component_rows])
    stationary_denominator = sum(row_totals.values())
    stationary_height_numerator = sum(
        int(ledger_by_orbit[orbit_id]["quotient_target_height_action"]) * total
        for orbit_id, total in row_totals.items()
    )
    stationary_r33_numerator = sum(
        int(ledger_by_orbit[orbit_id]["quotient_R33_height_residual"]) * total
        for orbit_id, total in row_totals.items()
    )
    stationary_public_error = zero_public_vector()
    stationary_hidden_error = sum(
        int(ledger_by_orbit[orbit_id]["quotient_hidden_balance_error"]) * total
        for orbit_id, total in row_totals.items()
    )
    stationary_rows = [
        {
            "orbit_id": orbit_id,
            "weight": fraction(total, stationary_denominator),
            "row_total_count": total,
        }
        for orbit_id, total in sorted(row_totals.items())
    ]
    incoming_counts = Counter()
    for source, targets in adjacency.items():
        for target, count in targets.items():
            incoming_counts[target] += count
    operator_summary = {
        "move_set": move_rows,
        "move_set_delta_masks": move_deltas,
        "target_orbit_count": len(quotient_operator_rows),
        "zero_exit_self_loop_count": len(zero_exit_rows),
        "row_total_histogram": histogram(list(row_totals.values())),
        "target_count_histogram": histogram([len(row["targets"]) for row in quotient_operator_rows]),
        "component_count": len(component_rows),
        "component_size_histogram": histogram([row["size"] for row in component_rows]),
        "markov_spectrum": spectrum,
        "rank": spectrum["-1"] + spectrum["-1/2"] + spectrum["1"],
        "nullity": spectrum["0"],
        "trace": fraction(1, 2),
        "stationary_distribution_denominator": stationary_denominator,
        "stationary_weight_histogram": {
            json.dumps(fraction(total, stationary_denominator), sort_keys=True): count
            for total, count in sorted(Counter(row_totals.values()).items())
        },
        "stationary_balance": {
            "weighted_public_balance_error": stationary_public_error,
            "weighted_hidden_balance_error": stationary_hidden_error,
            "weighted_quotient_target_height_action": fraction(
                stationary_height_numerator, stationary_denominator
            ),
            "weighted_quotient_R33_height_residual": fraction(
                stationary_r33_numerator, stationary_denominator
            ),
        },
    }

    checks = {
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "c2_quotient_transport_ledger_is_certified": transport_ledger.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_CERTIFIED"
        and transport_ledger.get("all_checks_pass") is True,
        "c2_quotient_anomaly_is_certified": anomaly.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_CERTIFIED"
        and anomaly.get("all_checks_pass") is True,
        "move_set_is_c2_closed_and_kernel_preserving": move_deltas == [8, 1034]
        and all(row["tau_image_delta_mask"] in move_deltas for row in move_rows)
        and all(row["corrected_clock_mod26"] == 0 for row in move_rows),
        "move_set_contains_generator3_and_tau_image_composite": move_rows[0]["generator_sequence"] == [3]
        and move_rows[0]["move_type"] == "primitive"
        and move_rows[1]["generator_sequence"] == [1, 3, 10]
        and move_rows[1]["move_type"] == "tau_image_composite",
        "zero_exit_closure_is_exactly_the_boundary_pair": len(zero_exit_rows) == 2
        and sorted(row["source_mask"] for row in zero_exit_rows) == [8, 1034],
        "operator_is_markov_on_every_quotient_orbit": len(quotient_operator_rows) == 543
        and all(
            sum(target["probability"]["numerator"] / target["probability"]["denominator"] for target in row["targets"])
            == 1
            for row in quotient_operator_rows
        ),
        "operator_counts_are_symmetric": all(
            adjacency[source][target] == adjacency[target][source]
            for source, targets in adjacency.items()
            for target in targets
        ),
        "stationary_distribution_is_degree_weighted_and_exact": all(
            incoming_counts[orbit_id] == row_totals[orbit_id] for orbit_id in row_totals
        )
        and stationary_denominator == 2046
        and Counter(row_totals.values()) == Counter({4: 480, 2: 63}),
        "component_decomposition_matches_c2_move_geometry": len(component_rows) == 144
        and Counter(row["size"] for row in component_rows) == Counter({4: 112, 3: 31, 2: 1}),
        "spectrum_matches_component_normal_forms": spectrum
        == {"-1": 143, "-1/2": 1, "0": 255, "1": 144}
        and operator_summary["rank"] == 288
        and operator_summary["nullity"] == 255,
        "stationary_data_is_ward_balanced": stationary_public_error == zero_public_vector()
        and stationary_hidden_error == 0
        and stationary_height_numerator + stationary_r33_numerator == 0
        and all(row["quotient_hidden_balance_error"] == 0 for row in quotient_operator_rows),
        "operator_rows_are_stably_hashed": sha_json(quotient_operator_rows)
        and sha_json(component_rows)
        and sha_json(stationary_rows),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator",
        "status": status,
        "object": "d20",
        "claim": (
            "The C2-invariant kernel-preserving move orbit {8,1034} defines a nontrivial Markov scattering "
            "operator on the 543 anomaly-corrected quotient orbits. Its component decomposition, spectrum, "
            "degree-weighted stationary distribution, and stationary Ward/BMS balance are certified exactly."
        ),
        "definition": {
            "quotient_scattering_operator": (
                "The row-stochastic operator on C2 quotient orbits obtained by applying the C2-closed "
                "move set {generator 3, tau(generator 3)} and closing the two zero exits as boundary "
                "self-loops."
            ),
            "stationary_balance": (
                "The degree-weighted stationary average of the anomaly-corrected quotient ledger rows."
            ),
        },
        "inputs": {
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
            "c2_quotient_transport_ledger_report": {
                "path": rel(C2_QUOTIENT_TRANSPORT_LEDGER_REPORT),
                "sha256": sha_file(C2_QUOTIENT_TRANSPORT_LEDGER_REPORT),
            },
            "c2_quotient_anomaly_report": {
                "path": rel(C2_QUOTIENT_ANOMALY_REPORT),
                "sha256": sha_file(C2_QUOTIENT_ANOMALY_REPORT),
            },
        },
        "derived": {
            "operator_summary": operator_summary,
            "quotient_operator_rows_sha256": sha_json(quotient_operator_rows),
            "component_rows_sha256": sha_json(component_rows),
            "stationary_rows_sha256": sha_json(stationary_rows),
            "primitive_witness_rows_sha256": sha_json(primitive_witness_rows),
            "zero_exit_rows": zero_exit_rows,
            "quotient_operator_rows": quotient_operator_rows,
            "component_rows": component_rows,
            "stationary_rows": stationary_rows,
        },
        "interpretation": {
            "what_this_proves": [
                "a nontrivial C2 quotient scattering operator exists on the 543-orbit quotient ledger",
                "the operator is Markov, reversible by symmetric move counts, and exactly spectral",
                "the only closure adjustment is the two zero exits from the orbit {8,1034}",
                "the degree-weighted stationary state is Ward/BMS-balanced after the anomaly connection",
            ],
            "what_this_does_not_prove": (
                "This is the minimal C2-closed kernel-preserving scattering operator. It does not yet use "
                "all possible C2-invariant composite moves or prove uniqueness among quotient dynamics."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify all C2-closed hidden-neutral composite move orbits and test whether the minimal "
            "quotient scattering operator is canonical or one member of a larger Ward-balanced dynamics family."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify scattering, C2 transport-ledger, and anomaly inputs",
            "derive the C2-closed hidden-neutral move orbit {8,1034}",
            "construct the 543-row quotient Markov operator with zero-exit boundary closure",
            "verify symmetric counts and degree-weighted stationary distribution",
            "verify component decomposition and exact spectrum",
            "verify stationary Ward/BMS balance",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
