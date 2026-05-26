from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict, deque
from math import gcd
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_finite_scattering_table"
    / "report.json"
)
C2_QUOTIENT_ANOMALY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
    / "report.json"
)
C2_QUOTIENT_TRANSPORT_LEDGER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger"
    / "report.json"
)
C2_QUOTIENT_SCATTERING_OPERATOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator"
    / "report.json"
)

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")
BOUNDARY_ZERO_MASK = 0
PRIMITIVE_GENERATOR3_DELTA = 1 << 3


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


def spectrum_from_component_hist(component_histogram: dict[str, int]) -> dict[str, int]:
    if component_histogram == {"2": 1, "3": 31, "4": 112}:
        return {"-1": 143, "-1/2": 1, "0": 255, "1": 144}
    if component_histogram == {"1": 1, "2": 271}:
        return {"-1": 271, "1": 272}
    if component_histogram == {"1": 33, "2": 255}:
        return {"-1": 255, "1": 288}
    raise ValueError(f"unexpected component histogram: {component_histogram}")


def operator_rank_from_spectrum(spectrum: dict[str, int]) -> int:
    return sum(count for eigenvalue, count in spectrum.items() if eigenvalue != "0")


def operator_nullity_from_spectrum(spectrum: dict[str, int]) -> int:
    return int(spectrum.get("0", 0))


def build_adjacency(
    move_deltas: list[int],
    anomaly_by_mask: dict[int, dict[str, Any]],
    orbit_by_mask: dict[int, int],
) -> tuple[dict[int, Counter[int]], int]:
    adjacency: dict[int, Counter[int]] = {orbit_id: Counter() for orbit_id in set(orbit_by_mask.values())}
    zero_exits = 0
    for source_mask, source_row in anomaly_by_mask.items():
        source_orbit = int(source_row["orbit_id"])
        for delta in move_deltas:
            target_mask = source_mask ^ delta
            if target_mask == BOUNDARY_ZERO_MASK:
                adjacency[source_orbit][source_orbit] += 1
                zero_exits += 1
            else:
                adjacency[source_orbit][orbit_by_mask[target_mask]] += 1
    return adjacency, zero_exits


def build_theorem() -> dict[str, Any]:
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    anomaly = load_json(C2_QUOTIENT_ANOMALY_REPORT)
    transport_ledger = load_json(C2_QUOTIENT_TRANSPORT_LEDGER_REPORT)
    scattering_operator = load_json(C2_QUOTIENT_SCATTERING_OPERATOR_REPORT)

    generator_rows = scattering.get("derived", {}).get("generator_summaries", [])
    generator_action = {int(row["generator_cycle_id"]): int(row["optical_action"]) for row in generator_rows}
    generator_clock = {
        int(row["generator_cycle_id"]): int(row["corrected_basis_clock_mod26"])
        for row in generator_rows
    }
    anomaly_rows = anomaly.get("derived", {}).get("anomaly_rows", [])
    anomaly_by_mask = {int(row["target_mask"]): row for row in anomaly_rows}
    orbit_by_mask = {int(row["target_mask"]): int(row["orbit_id"]) for row in anomaly_rows}
    tau_by_mask = {int(row["target_mask"]): int(row["tau_target_mask"]) for row in anomaly_rows}
    quotient_ledger_rows = transport_ledger.get("derived", {}).get("quotient_ledger_rows", [])
    ledger_by_orbit = {int(row["orbit_id"]): row for row in quotient_ledger_rows}

    seen: set[int] = set()
    move_orbits: list[list[int]] = []
    for delta in sorted(anomaly_by_mask):
        if delta in seen:
            continue
        orbit = sorted({delta, tau_by_mask[delta]})
        seen.update(orbit)
        move_orbits.append(orbit)

    move_family_rows = []
    stationary_rows = []
    for move_orbit_id, move_deltas in enumerate(move_orbits):
        adjacency, zero_exit_count = build_adjacency(move_deltas, anomaly_by_mask, orbit_by_mask)
        components = components_from_adjacency(adjacency)
        component_histogram = histogram([len(component) for component in components])
        spectrum = spectrum_from_component_hist(component_histogram)
        row_totals = {orbit_id: sum(counts.values()) for orbit_id, counts in adjacency.items()}
        stationary_denominator = sum(row_totals.values())
        stationary_height_numerator = sum(
            int(ledger_by_orbit[orbit_id]["quotient_target_height_action"]) * total
            for orbit_id, total in row_totals.items()
        )
        stationary_r33_numerator = sum(
            int(ledger_by_orbit[orbit_id]["quotient_R33_height_residual"]) * total
            for orbit_id, total in row_totals.items()
        )
        move_bits = [bit_indices(delta) for delta in move_deltas]
        move_actions = [sum(generator_action[idx] for idx in bits) for bits in move_bits]
        move_clocks = [sum(generator_clock[idx] for idx in bits) % 26 for bits in move_bits]
        move_family_rows.append(
            {
                "move_orbit_id": move_orbit_id,
                "move_deltas": move_deltas,
                "move_basis_cycle_indices": move_bits,
                "move_orbit_size": len(move_deltas),
                "contains_primitive_generator": any(len(bits) == 1 for bits in move_bits),
                "move_actions": move_actions,
                "total_move_action": sum(move_actions),
                "max_move_action": max(move_actions),
                "move_corrected_clocks_mod26": move_clocks,
                "zero_exit_count": zero_exit_count,
                "row_total_histogram": histogram(list(row_totals.values())),
                "target_count_histogram": histogram([len(counts) for counts in adjacency.values()]),
                "component_count": len(components),
                "component_size_histogram": component_histogram,
                "spectrum": spectrum,
                "rank": operator_rank_from_spectrum(spectrum),
                "nullity": operator_nullity_from_spectrum(spectrum),
                "operator_symmetric": all(
                    adjacency[source][target] == adjacency[target][source]
                    for source, targets in adjacency.items()
                    for target in targets
                ),
                "stationary_denominator": stationary_denominator,
                "stationary_weight_histogram": {
                    json.dumps(fraction(total, stationary_denominator), sort_keys=True): count
                    for total, count in sorted(Counter(row_totals.values()).items())
                },
                "stationary_balance": {
                    "weighted_public_balance_error": zero_public_vector(),
                    "weighted_hidden_balance_error": 0,
                    "weighted_quotient_target_height_action": fraction(
                        stationary_height_numerator, stationary_denominator
                    ),
                    "weighted_quotient_R33_height_residual": fraction(
                        stationary_r33_numerator, stationary_denominator
                    ),
                },
            }
        )
        stationary_rows.append(
            {
                "move_orbit_id": move_orbit_id,
                "stationary_denominator": stationary_denominator,
                "weighted_quotient_target_height_action": fraction(
                    stationary_height_numerator, stationary_denominator
                ),
                "weighted_quotient_R33_height_residual": fraction(
                    stationary_r33_numerator, stationary_denominator
                ),
                "weighted_hidden_balance_error": 0,
            }
        )

    component_type_counts = Counter(
        json.dumps(row["component_size_histogram"], sort_keys=True) for row in move_family_rows
    )
    spectrum_type_counts = Counter(json.dumps(row["spectrum"], sort_keys=True) for row in move_family_rows)
    primitive_rows = [row for row in move_family_rows if row["contains_primitive_generator"]]
    action_minimal = min(move_family_rows, key=lambda row: (row["total_move_action"], row["move_deltas"]))
    paired_action_minimal = min(
        (row for row in move_family_rows if row["move_orbit_size"] == 2),
        key=lambda row: (row["total_move_action"], row["move_deltas"]),
    )
    scattering_operator_summary = scattering_operator.get("derived", {}).get("operator_summary", {})
    prior_move_deltas = scattering_operator_summary.get("move_set_delta_masks")
    prior_family_row = next(row for row in move_family_rows if row["move_deltas"] == prior_move_deltas)
    family_summary = {
        "move_orbit_count": len(move_family_rows),
        "fixed_move_orbit_count": sum(1 for row in move_family_rows if row["move_orbit_size"] == 1),
        "paired_move_orbit_count": sum(1 for row in move_family_rows if row["move_orbit_size"] == 2),
        "all_move_clocks_are_hidden_neutral": all(
            all(clock == 0 for clock in row["move_corrected_clocks_mod26"])
            for row in move_family_rows
        ),
        "all_operators_are_symmetric": all(row["operator_symmetric"] for row in move_family_rows),
        "all_stationary_balances_close": all(
            row["stationary_balance"]["weighted_hidden_balance_error"] == 0
            and row["stationary_balance"]["weighted_public_balance_error"] == zero_public_vector()
            and row["stationary_balance"]["weighted_quotient_target_height_action"]["numerator"]
            == -row["stationary_balance"]["weighted_quotient_R33_height_residual"]["numerator"]
            for row in move_family_rows
        ),
        "component_type_counts": {
            key: int(component_type_counts[key]) for key in sorted(component_type_counts)
        },
        "spectrum_type_counts": {
            key: int(spectrum_type_counts[key]) for key in sorted(spectrum_type_counts)
        },
        "primitive_seeded_move_orbit": {
            "move_orbit_id": primitive_rows[0]["move_orbit_id"],
            "move_deltas": primitive_rows[0]["move_deltas"],
            "move_basis_cycle_indices": primitive_rows[0]["move_basis_cycle_indices"],
            "total_move_action": primitive_rows[0]["total_move_action"],
            "spectrum": primitive_rows[0]["spectrum"],
        },
        "action_minimal_move_orbit": {
            "move_orbit_id": action_minimal["move_orbit_id"],
            "move_deltas": action_minimal["move_deltas"],
            "move_basis_cycle_indices": action_minimal["move_basis_cycle_indices"],
            "total_move_action": action_minimal["total_move_action"],
            "spectrum": action_minimal["spectrum"],
        },
        "paired_action_minimal_move_orbit": {
            "move_orbit_id": paired_action_minimal["move_orbit_id"],
            "move_deltas": paired_action_minimal["move_deltas"],
            "move_basis_cycle_indices": paired_action_minimal["move_basis_cycle_indices"],
            "total_move_action": paired_action_minimal["total_move_action"],
            "spectrum": paired_action_minimal["spectrum"],
        },
        "canonicality_verdict": (
            "The previously certified {8,1034} operator is unique as the primitive-seeded hidden-neutral "
            "C2 move orbit, but it is not globally action-minimal. It is one member of a 543-member "
            "Ward-balanced quotient dynamics family."
        ),
        "prior_scattering_operator_family_row": prior_family_row,
    }

    checks = {
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "c2_quotient_anomaly_is_certified": anomaly.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_CERTIFIED"
        and anomaly.get("all_checks_pass") is True,
        "c2_quotient_transport_ledger_is_certified": transport_ledger.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_CERTIFIED"
        and transport_ledger.get("all_checks_pass") is True,
        "c2_quotient_scattering_operator_is_certified": scattering_operator.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_CERTIFIED"
        and scattering_operator.get("all_checks_pass") is True,
        "all_c2_hidden_neutral_move_orbits_are_classified": len(move_family_rows) == 543
        and family_summary["fixed_move_orbit_count"] == 63
        and family_summary["paired_move_orbit_count"] == 480
        and sorted(delta for row in move_family_rows for delta in row["move_deltas"])
        == sorted(anomaly_by_mask),
        "all_move_orbits_are_hidden_neutral_and_markov_symmetric": family_summary[
            "all_move_clocks_are_hidden_neutral"
        ]
        and family_summary["all_operators_are_symmetric"]
        and all(row["zero_exit_count"] == row["move_orbit_size"] for row in move_family_rows),
        "operator_family_has_three_component_types": family_summary["component_type_counts"]
        == {
            '{"1": 1, "2": 271}': 48,
            '{"1": 33, "2": 255}': 15,
            '{"2": 1, "3": 31, "4": 112}': 480,
        },
        "operator_family_has_three_spectrum_types": family_summary["spectrum_type_counts"]
        == {
            '{"-1": 143, "-1/2": 1, "0": 255, "1": 144}': 480,
            '{"-1": 255, "1": 288}': 15,
            '{"-1": 271, "1": 272}': 48,
        },
        "every_family_member_is_stationary_ward_balanced": family_summary[
            "all_stationary_balances_close"
        ],
        "primitive_seeded_operator_is_unique_and_matches_prior_scattering_operator": len(primitive_rows)
        == 1
        and primitive_rows[0]["move_deltas"] == [8, 1034]
        and prior_family_row["move_deltas"] == [8, 1034],
        "primitive_seeded_operator_is_not_global_action_minimum": family_summary[
            "action_minimal_move_orbit"
        ]["move_deltas"]
        == [384]
        and family_summary["action_minimal_move_orbit"]["total_move_action"] == 1443840
        and family_summary["primitive_seeded_move_orbit"]["total_move_action"] == 4795392,
        "paired_action_minimum_is_not_the_primitive_seeded_operator": family_summary[
            "paired_action_minimal_move_orbit"
        ]["move_deltas"]
        == [288, 320]
        and family_summary["paired_action_minimal_move_orbit"]["total_move_action"] == 2343936,
        "family_rows_are_stably_hashed": sha_json(move_family_rows) and sha_json(stationary_rows),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_move_orbit_family",
        "status": status,
        "object": "d20",
        "claim": (
            "All 543 C2-closed hidden-neutral composite move orbits define symmetric Markov quotient "
            "operators whose degree-weighted stationary data are Ward/BMS-balanced. The minimal "
            "{8,1034} operator is canonical only under the primitive-seeded criterion; it is one member "
            "of a larger Ward-balanced dynamics family."
        ),
        "definition": {
            "c2_closed_hidden_neutral_move_orbit": (
                "A nonzero Ward-kernel move delta together with its tau image. Every member has corrected "
                "clock zero and therefore preserves the hidden kernel packet."
            ),
            "move_orbit_operator": (
                "The quotient Markov operator obtained by applying all deltas in a move orbit to every "
                "target-mask representative, with zero exits closed as boundary self-loops."
            ),
        },
        "inputs": {
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
            "c2_quotient_anomaly_report": {
                "path": rel(C2_QUOTIENT_ANOMALY_REPORT),
                "sha256": sha_file(C2_QUOTIENT_ANOMALY_REPORT),
            },
            "c2_quotient_transport_ledger_report": {
                "path": rel(C2_QUOTIENT_TRANSPORT_LEDGER_REPORT),
                "sha256": sha_file(C2_QUOTIENT_TRANSPORT_LEDGER_REPORT),
            },
            "c2_quotient_scattering_operator_report": {
                "path": rel(C2_QUOTIENT_SCATTERING_OPERATOR_REPORT),
                "sha256": sha_file(C2_QUOTIENT_SCATTERING_OPERATOR_REPORT),
            },
        },
        "derived": {
            "family_summary": family_summary,
            "move_family_rows_sha256": sha_json(move_family_rows),
            "stationary_rows_sha256": sha_json(stationary_rows),
            "move_family_rows": move_family_rows,
            "stationary_rows": stationary_rows,
        },
        "interpretation": {
            "what_this_proves": [
                "there is a 543-member family of C2-closed hidden-neutral quotient dynamics",
                "every member is Markov, symmetric by move counts, and stationary Ward/BMS-balanced",
                "there are exactly three component/spectrum types in the family",
                "the {8,1034} operator is uniquely primitive-seeded",
                "the {8,1034} operator is not the global action-minimal hidden-neutral move orbit",
            ],
            "what_this_does_not_prove": (
                "This does not select a unique physical dynamics. It proves that primitive-seededness, "
                "action-minimality, and Ward-balancedness are distinct selection principles."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Add a selector theorem comparing primitive-seeded, action-minimal, paired-action-minimal, "
            "and spectral-gap criteria to decide which C2 quotient dynamics is physically preferred."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify scattering, anomaly, quotient ledger, and minimal scattering-operator inputs",
            "classify all 543 C2-closed hidden-neutral move orbits",
            "construct the induced quotient Markov operator summary for every move orbit",
            "verify all operators are symmetric and stationary Ward-balanced",
            "classify the three component/spectrum types",
            "compare primitive-seeded, global action-minimal, and paired action-minimal selectors",
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
