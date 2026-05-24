from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
SS_SAT = ROOT / "data" / "evidence" / "ss_sat"
D20 = ROOT / "data" / "invariants" / "d20"
HCYCLE = ROOT / "data" / "invariants" / "hcycle"

REPORT_PATH = CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json"
ALL_RESIDUE_TRANSPORT = D20 / "theorems" / "sector33_all_residue_height_transport" / "report.json"
X_TARGET = CVX / "reports" / "x_extractor_target_certificate.json"
UNIFORM_INVESTIGATION = CVX / "reports" / "uniform_cnf_to_e33_family_encoding_investigation.json"
PRIMITIVE_CYCLES = HCYCLE / "subscript_Hcycle_primitive_cycles.csv"
SOLVER_RUNS = SS_SAT / "tables" / "solver_run_summary.csv"
SCALED_SOLVER_RUNS = SS_SAT / "tables" / "scaled_solver_run_summary.csv"

FIELD_PRIME = 1_000_003

CANARY_FORMULAS = {
    "canary_sat_unit": {
        "source_kind": "generated_truth_diversity_canary",
        "text": "p cnf 1 1\n1 0\n",
    },
    "canary_sat_binary_choice": {
        "source_kind": "generated_truth_diversity_canary",
        "text": "p cnf 2 2\n1 2 0\n-1 2 0\n",
    },
    "canary_unsat_unit_pair": {
        "source_kind": "generated_truth_diversity_canary",
        "text": "p cnf 1 2\n1 0\n-1 0\n",
    },
    "canary_unsat_two_var_box": {
        "source_kind": "generated_truth_diversity_canary",
        "text": "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def signed_mod(value: int) -> int:
    residue = value % FIELD_PRIME
    if residue > FIELD_PRIME // 2:
        return residue - FIELD_PRIME
    return residue


def parse_dimacs_text(text: str, source_id: str) -> dict[str, Any]:
    variables: int | None = None
    declared_clauses: int | None = None
    tokens: list[int] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError(f"{source_id}: unsupported DIMACS header {line!r}")
            variables = int(parts[2])
            declared_clauses = int(parts[3])
            continue
        tokens.extend(int(part) for part in line.split())

    clauses: list[list[int]] = []
    current: list[int] = []
    for token in tokens:
        if token == 0:
            clauses.append(current)
            current = []
        else:
            current.append(token)
    if current:
        raise ValueError(f"{source_id}: unterminated DIMACS clause")
    if variables is None or declared_clauses is None:
        raise ValueError(f"{source_id}: missing DIMACS header")
    if declared_clauses != len(clauses):
        raise ValueError(f"{source_id}: declared {declared_clauses} clauses, parsed {len(clauses)}")

    return {
        "source_id": source_id,
        "variables": variables,
        "declared_clauses": declared_clauses,
        "clauses": clauses,
    }


def normalize_clause(clause: list[int]) -> list[int]:
    return sorted(set(clause), key=lambda item: (abs(item), item < 0))


def canonical_formula(parsed: dict[str, Any]) -> dict[str, Any]:
    clauses = sorted(normalize_clause(clause) for clause in parsed["clauses"])
    return {
        "variables": parsed["variables"],
        "clauses": clauses,
    }


def formula_features(parsed: dict[str, Any]) -> dict[str, Any]:
    canonical = canonical_formula(parsed)
    clauses = canonical["clauses"]
    flat = [literal for clause in clauses for literal in clause]
    widths = [len(clause) for clause in clauses]
    variables_seen = sorted({abs(literal) for literal in flat})
    positive = sum(1 for literal in flat if literal > 0)
    negative = sum(1 for literal in flat if literal < 0)
    tautological = sum(1 for clause in clauses if any(-literal in clause for literal in clause))
    horn = sum(1 for clause in clauses if sum(1 for literal in clause if literal > 0) <= 1)

    return {
        "variables": parsed["variables"],
        "clauses": len(clauses),
        "total_literals": len(flat),
        "positive_literals": positive,
        "negative_literals": negative,
        "unit_clauses": sum(1 for width in widths if width == 1),
        "binary_clauses": sum(1 for width in widths if width == 2),
        "ternary_clauses": sum(1 for width in widths if width == 3),
        "wide_clauses": sum(1 for width in widths if width >= 4),
        "max_clause_width": max(widths, default=0),
        "literal_abs_sum": sum(abs(literal) for literal in flat),
        "signed_literal_sum": sum(flat),
        "distinct_variables_seen": len(variables_seen),
        "tautological_clauses": tautological,
        "horn_clauses": horn,
    }


def compile_mask(parsed: dict[str, Any]) -> dict[str, Any]:
    canonical = canonical_formula(parsed)
    features = formula_features(parsed)
    digest = sha_json(canonical)
    digest_int = int(digest[:16], 16)

    bit_sources = [
        ("variables_parity", features["variables"]),
        ("clauses_parity", features["clauses"]),
        ("total_literals_parity", features["total_literals"]),
        ("negative_literals_parity", features["negative_literals"]),
        ("positive_literals_parity", features["positive_literals"]),
        ("unit_clauses_parity", features["unit_clauses"]),
        ("binary_clauses_parity", features["binary_clauses"]),
        ("ternary_clauses_parity", features["ternary_clauses"]),
        ("wide_clauses_parity", features["wide_clauses"]),
        ("literal_abs_sum_parity", features["literal_abs_sum"] + features["tautological_clauses"]),
        ("canonical_sha256_low_bit", digest_int),
    ]
    bits = [
        {
            "basis_cycle_id": index,
            "source": source,
            "value": int(value),
            "bit": int(value) & 1,
        }
        for index, (source, value) in enumerate(bit_sources)
    ]
    mask = sum(bit["bit"] << bit["basis_cycle_id"] for bit in bits)
    forced_nonzero_bit: int | None = None
    if mask == 0 and (features["clauses"] > 0 or features["total_literals"] > 0):
        forced_nonzero_bit = (
            features["variables"] + 3 * features["clauses"] + 5 * features["total_literals"]
        ) % len(bits)
        mask = 1 << forced_nonzero_bit

    return {
        "compiler_id": "public_cnf_parity_hash_to_d20_basis_mask_v0",
        "compiler_kind": "finite_public_fingerprint_candidate_not_semantic_reduction",
        "canonical_formula_sha256": digest,
        "features": features,
        "bit_sources": bits,
        "forced_nonzero_bit": forced_nonzero_bit,
        "mask": mask,
        "basis_cycle_ids": [index for index in range(11) if (mask >> index) & 1],
    }


def brute_force_truth(parsed: dict[str, Any], max_variables: int = 16) -> str | None:
    variables = parsed["variables"]
    if variables > max_variables:
        return None
    clauses = parsed["clauses"]
    for values in itertools.product([False, True], repeat=variables):
        assignment = {index + 1: value for index, value in enumerate(values)}
        if all(any((literal > 0) == assignment.get(abs(literal), False) for literal in clause) for clause in clauses):
            return "SAT"
    return "UNSAT"


def solver_truth_map() -> dict[str, str]:
    status_by_benchmark: dict[str, Counter[str]] = defaultdict(Counter)
    for row in read_csv(SOLVER_RUNS) + read_csv(SCALED_SOLVER_RUNS):
        status_by_benchmark[row["benchmark"]][row["status"]] += 1
    truth: dict[str, str] = {}
    for benchmark, counts in status_by_benchmark.items():
        if counts.get("SAT", 0) > 0:
            truth[benchmark] = "SAT"
        elif counts.get("UNSAT", 0) > 0:
            truth[benchmark] = "UNSAT"
    return truth


def load_primitive_cycles() -> dict[int, dict[str, Any]]:
    cycles: dict[int, dict[str, Any]] = {}
    for row in read_csv(PRIMITIVE_CYCLES):
        cycle_id = int(row["cycle_id"])
        cycles[cycle_id] = {
            "cycle_id": cycle_id,
            "length": int(row["length"]),
            "optical_action": int(row["optical_action"]),
            "vertices": [int(item) for item in row["vertices"].split()],
            "edge_ids": [int(item) for item in row["edge_ids"].split()],
            "turn_addresses": row["turn_addresses"].split(),
        }
    return cycles


def transport_table() -> dict[int, dict[str, Any]]:
    all_residue = load_json(ALL_RESIDUE_TRANSPORT)
    return {int(row["mask"]): row for row in all_residue["derived"]["transport_rows"]}


def source_formulas() -> list[dict[str, Any]]:
    formulas: list[dict[str, Any]] = []
    for path in sorted((SS_SAT / "benchmarks").glob("*.cnf"), key=lambda item: item.name):
        formulas.append(
            {
                "source_id": path.name,
                "source_kind": "canonical_ss_sat_fixture",
                "path": rel(path),
                "text": path.read_text(encoding="utf-8"),
            }
        )
    for path in sorted((SS_SAT / "benchmarks" / "scaled").glob("*.cnf"), key=lambda item: item.name):
        formulas.append(
            {
                "source_id": f"scaled/{path.name}",
                "source_kind": "canonical_ss_sat_scaled_fixture",
                "path": rel(path),
                "text": path.read_text(encoding="utf-8"),
            }
        )
    for source_id, item in CANARY_FORMULAS.items():
        formulas.append(
            {
                "source_id": source_id,
                "source_kind": item["source_kind"],
                "path": None,
                "text": item["text"],
            }
        )
    return formulas


def annotate_compilation(
    formula: dict[str, Any],
    truth_by_source: dict[str, str],
    cycles: dict[int, dict[str, Any]],
    transports: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    parsed = parse_dimacs_text(formula["text"], formula["source_id"])
    compiled = compile_mask(parsed)
    mask = compiled["mask"]
    row = transports[mask]
    basis_cycles = [cycles[index] for index in compiled["basis_cycle_ids"]]
    basis_height_action = sum(cycle["optical_action"] for cycle in basis_cycles)
    brute_force = brute_force_truth(parsed)
    known_truth = truth_by_source.get(formula["source_id"]) or brute_force
    target_predicate = row["residual_integral"] != 0

    return {
        "source_id": formula["source_id"],
        "source_kind": formula["source_kind"],
        "path": formula.get("path"),
        "known_truth": known_truth,
        "truth_source": "solver_logs" if formula["source_id"] in truth_by_source else "bounded_bruteforce_canary",
        "bruteforce_truth_if_bounded": brute_force,
        "compiler_output": compiled,
        "closed_return_circuit": {
            "kind": "formal_sum_of_d20_primitive_closed_cycles",
            "basis_cycle_ids": compiled["basis_cycle_ids"],
            "basis_cycle_count": len(compiled["basis_cycle_ids"]),
            "total_primitive_edge_steps": sum(cycle["length"] for cycle in basis_cycles),
            "height_action_from_basis_cycles": basis_height_action,
            "height_action_matches_transport_row": basis_height_action == row["height_action"],
            "primitive_cycles": basis_cycles,
        },
        "rho33_transport_from_emitted_circuit": {
            "support_sector": row["support_sector"],
            "height_action": row["height_action"],
            "residual_integral": row["residual_integral"],
            "residual_mod_prime": row["residual_mod_prime"],
            "transport_scalar": row["transport_scalar"],
            "transport_scalar_signed": row["transport_scalar_signed"],
            "pi33_coefficient_mod_prime": row["pi33_coefficient_mod_prime"],
            "target_predicate_nonzero_e33_residual": target_predicate,
            "formula": "rho_33(phi) = -(A_h(C(phi))/dim(Pi_33)) e_33, using the emitted D20 basis-cycle mask C(phi).",
        },
        "sat_preservation_probe": {
            "target_predicate": target_predicate,
            "matches_sat_truth": None if known_truth is None else target_predicate == (known_truth == "SAT"),
        },
    }


def preservation_summary(compiled_rows: list[dict[str, Any]]) -> dict[str, Any]:
    known = [row for row in compiled_rows if row["known_truth"] in {"SAT", "UNSAT"}]
    sat_rows = [row for row in known if row["known_truth"] == "SAT"]
    unsat_rows = [row for row in known if row["known_truth"] == "UNSAT"]
    mismatches = [
        {
            "source_id": row["source_id"],
            "known_truth": row["known_truth"],
            "mask": row["compiler_output"]["mask"],
            "target_predicate": row["sat_preservation_probe"]["target_predicate"],
        }
        for row in known
        if row["sat_preservation_probe"]["matches_sat_truth"] is False
    ]
    false_positives = [row for row in mismatches if row["known_truth"] == "UNSAT" and row["target_predicate"] is True]
    false_negatives = [row for row in mismatches if row["known_truth"] == "SAT" and row["target_predicate"] is False]
    return {
        "known_truth_instances": len(known),
        "sat_instances": len(sat_rows),
        "unsat_instances": len(unsat_rows),
        "truth_diverse": bool(sat_rows and unsat_rows),
        "target_predicate": "nonzero sector-33 height residual after public CNF fingerprint compilation",
        "passed": bool(known) and not mismatches and bool(sat_rows and unsat_rows),
        "mismatch_count": len(mismatches),
        "false_positive_unsat_as_target_yes_count": len(false_positives),
        "false_negative_sat_as_target_no_count": len(false_negatives),
        "mismatches": mismatches[:20],
    }


def report_status(path: Path, expected_status: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": rel(path),
        "status": data.get("status"),
        "expected_status": expected_status,
        "passed": data.get("status") == expected_status,
    }


def build_report() -> dict[str, Any]:
    cycles = load_primitive_cycles()
    transports = transport_table()
    truth_by_source = solver_truth_map()
    compiled_rows = [
        annotate_compilation(formula, truth_by_source, cycles, transports) for formula in source_formulas()
    ]
    preservation = preservation_summary(compiled_rows)
    all_masks = [row["compiler_output"]["mask"] for row in compiled_rows]
    all_height_matches = all(
        row["closed_return_circuit"]["height_action_matches_transport_row"] for row in compiled_rows
    )
    all_rows_have_transport = all(
        0 <= row["compiler_output"]["mask"] <= 2047
        and row["rho33_transport_from_emitted_circuit"]["support_sector"] == 33
        for row in compiled_rows
    )
    nonzero_mask_rows = [row for row in compiled_rows if row["compiler_output"]["mask"] != 0]

    return {
        "schema": "d20.integrity.formula_to_boundary_cycle_family_candidate.source_drop",
        "status": "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
        "claim_level": "public_compiler_candidate_not_sat_reduction",
        "source_audit": {
            "uniform_cnf_to_e33_family_encoding_investigation": report_status(
                UNIFORM_INVESTIGATION,
                "UNIFORM_CNF_TO_E33_ENCODING_INVESTIGATION_BLOCKED",
            ),
            "sector33_all_residue_height_transport": report_status(
                ALL_RESIDUE_TRANSPORT,
                "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
            ),
            "x_extractor_target": report_status(
                X_TARGET,
                "X_EXTRACTOR_TARGET_AND_INTRINSIC_TRANSPORT_CERTIFIED_POLYNOMIAL_LOWER_BOUND_OPEN",
            ),
        },
        "compiler": {
            "id": "public_cnf_parity_hash_to_d20_basis_mask_v0",
            "input_surface": "DIMACS CNF text only",
            "output_surface": "11-bit D20 primitive basis-cycle activation mask plus finite sector-33 transport annotation",
            "algorithm": [
                "parse DIMACS CNF",
                "canonicalize clauses by sorted unique literals and sorted clause rows",
                "compute public parity/hash feature bits",
                "emit an 11-bit D20 basis-cycle mask",
                "look up the certified finite sector-33 all-residue transport row for that mask",
            ],
            "public_only": True,
            "does_not_read_solver_outcome": True,
            "does_not_read_hidden_e33_to_choose_mask": True,
            "polynomial_time_bound": "O(input_bytes + literal_count + 11)",
            "output_size_bound": "at most 11 primitive D20 cycles plus one certified finite transport row",
            "finite_codomain_size": 2048,
            "finite_codomain_warning": (
                "This finite 2048-mask compiler cannot be a SAT-complete reduction for unbounded CNF "
                "without a parameterized target-family extension."
            ),
        },
        "compiled_instance_summary": {
            "instance_count": len(compiled_rows),
            "canonical_fixture_count": sum(
                1 for row in compiled_rows if row["source_kind"] == "canonical_ss_sat_fixture"
            ),
            "scaled_fixture_count": sum(
                1 for row in compiled_rows if row["source_kind"] == "canonical_ss_sat_scaled_fixture"
            ),
            "generated_truth_diversity_canary_count": sum(
                1 for row in compiled_rows if row["source_kind"] == "generated_truth_diversity_canary"
            ),
            "unique_mask_count": len(set(all_masks)),
            "mask_histogram": dict(sorted(Counter(all_masks).items())),
            "all_masks_in_2048_residue_table": all_rows_have_transport,
            "all_height_actions_recomputed_from_emitted_basis_cycles": all_height_matches,
            "nonzero_e33_residual_count": len(nonzero_mask_rows),
        },
        "compiled_instances": compiled_rows,
        "sat_preservation_probe": preservation,
        "construction_checks": {
            "compiler_total_on_test_surface": len(compiled_rows) == len(source_formulas()),
            "compiler_public_only": True,
            "compiler_polynomial_output_bound": True,
            "rho33_transport_recomputed_from_emitted_circuit_data": all_height_matches and all_rows_have_transport,
            "truth_diverse_probe_surface_present": preservation["truth_diverse"],
            "sat_yes_no_preservation_on_probe_surface": preservation["passed"],
        },
        "decision": {
            "may_claim_public_formula_to_boundary_cycle_compiler_candidate": True,
            "may_claim_polynomial_output_bound_for_candidate": True,
            "may_claim_rho33_recomputed_from_emitted_circuit_data": all_height_matches and all_rows_have_transport,
            "may_claim_sat_yes_no_preservation": preservation["passed"],
            "may_claim_uniform_cnf_to_e33_family_encoding": False,
            "may_claim_sat_complete_hidden_e33_family": False,
            "may_claim_p_not_np": False,
            "reason": (
                "A deterministic public CNF-to-D20-mask compiler candidate now exists and recomputes "
                "sector-33 transport from emitted circuit data. It is a finite public fingerprint and "
                "fails the truth-diverse SAT-preservation probe, so it is not a SAT reduction."
            ),
        },
        "non_claims": [
            "This is not a SAT-complete reduction.",
            "This finite 2048-mask target cannot carry an unbounded asymptotic separation by itself.",
            "The nonzero e33 residual predicate is not equivalent to CNF satisfiability on the probe surface.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": "cnf_to_parameterized_e33_packet_compiler",
            "action": (
                "Implement the public DIMACS-to-E(phi) packet compiler and replay checker that emits "
                "clause-local circuit data and validates SAT/UNSAT canaries against the schema."
            ),
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
