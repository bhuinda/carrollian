#!/usr/bin/env python3
from __future__ import annotations

import ast
import array
import csv
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
T985 = ROOT / "data" / "raw" / "T_985.npz"
QUOTIENTS = ROOT / "data" / "raw" / "quotients.npz"

NMAX = 40
QMAX = 512
STATUS = "D20_A985_RELATION_PAIR_QUOTIENT_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN"
TARGETS = [
    32,
    39,
    91,
    243,
    455,
    2275,
    4095,
    6825,
    6912,
    14560,
    455640,
    531441,
    534656,
    1414965,
    2537360,
]
FOCUS_TARGETS = [39, 243, 455640, 534656]
BUDGET_ORDER = [
    "full_pair_coefficient_mass",
    "full_pair_output_support",
    "q42_pair_coefficient_mass",
    "q42_pair_row_support",
    "q42_pair_output_classes",
    "q42_tensor_coefficient_mass",
    "q12_pair_coefficient_mass",
    "q12_pair_row_support",
    "q12_pair_output_classes",
    "q12_tensor_coefficient_mass",
]


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_npy_member(npz: zipfile.ZipFile, name: str) -> tuple[dict, array.array, bytes]:
    data = npz.read(name)
    if data[:6] != b"\x93NUMPY":
        raise ValueError(f"{name} is not an npy member")
    version = data[6:8]
    if version == b"\x01\x00":
        header_len = int.from_bytes(data[8:10], "little")
        offset = 10
    else:
        header_len = int.from_bytes(data[8:12], "little")
        offset = 12
    header = ast.literal_eval(data[offset : offset + header_len].decode("latin1"))
    payload = data[offset + header_len :]
    descr = header["descr"]
    if descr == "<i2":
        arr = array.array("h")
    elif descr == "<i4":
        arr = array.array("i")
    elif descr == "<i8":
        arr = array.array("q")
    else:
        raise ValueError(f"unsupported dtype for {name}: {descr}")
    arr.frombytes(payload)
    return header, arr, payload


def digest_int_sequence(values: list[int], item_bytes: int) -> str:
    signed = True
    h = hashlib.sha256()
    for value in values:
        h.update(int(value).to_bytes(item_bytes, "little", signed=signed))
    return h.hexdigest()


def quotient_tensor_index(nclasses: int, i: int, j: int, k: int) -> int:
    return (i * nclasses + j) * nclasses + k


def distribution_record(distribution: Counter[int]) -> dict:
    return {
        "distinct_weights": len(distribution),
        "min_weight": min(distribution),
        "max_weight": max(distribution),
        "cell_count": sum(distribution.values()),
        "zero_cells": distribution.get(0, 0),
        "cells_in_q_window": sum(m for weight, m in distribution.items() if weight <= QMAX),
        "positive_cells": sum(m for weight, m in distribution.items() if weight > 0),
        "positive_cells_in_q_window": sum(m for weight, m in distribution.items() if 0 < weight <= QMAX),
        "distribution": [{"weight": int(weight), "multiplicity": int(distribution[weight])} for weight in sorted(distribution)],
    }


def compute() -> dict:
    with zipfile.ZipFile(T985) as zt, zipfile.ZipFile(QUOTIENTS) as zq:
        h_triples, triples, triples_payload = load_npy_member(zt, "triples.npy")
        h_q42, q42, q42_payload = load_npy_member(zq, "q42_map.npy")
        h_q12, q12, q12_payload = load_npy_member(zq, "q12_map.npy")
        h_q42t, q42_tensor_supplied, q42_tensor_payload = load_npy_member(zq, "q42_tensor.npy")
        h_q12t, q12_tensor_supplied, q12_tensor_payload = load_npy_member(zq, "q12_tensor.npy")

    if h_triples["shape"] != (1414965, 4):
        raise AssertionError(f"unexpected triples shape: {h_triples['shape']}")
    if h_q42["shape"] != (985,) or h_q12["shape"] != (985,):
        raise AssertionError("unexpected quotient map shape")
    if h_q42t["shape"] != (42, 42, 42) or h_q12t["shape"] != (12, 12, 12):
        raise AssertionError("unexpected quotient tensor shape")

    pair_mass: dict[tuple[int, int], int] = defaultdict(int)
    pair_support: dict[tuple[int, int], int] = defaultdict(int)
    q42_pair_mass = [[0] * 42 for _ in range(42)]
    q42_pair_rows = [[0] * 42 for _ in range(42)]
    q42_pair_outputs = [[set() for _ in range(42)] for __ in range(42)]
    q42_tensor = [0] * (42 * 42 * 42)
    q12_pair_mass = [[0] * 12 for _ in range(12)]
    q12_pair_rows = [[0] * 12 for _ in range(12)]
    q12_pair_outputs = [[set() for _ in range(12)] for __ in range(12)]
    q12_tensor = [0] * (12 * 12 * 12)
    coefficient_total = 0
    coefficient_min = None
    coefficient_max = 0

    support = h_triples["shape"][0]
    for row in range(support):
        alpha = int(triples[4 * row])
        beta = int(triples[4 * row + 1])
        gamma = int(triples[4 * row + 2])
        coeff = int(triples[4 * row + 3])
        coefficient_total += coeff
        coefficient_min = coeff if coefficient_min is None else min(coefficient_min, coeff)
        coefficient_max = max(coefficient_max, coeff)

        pair_mass[(alpha, beta)] += coeff
        pair_support[(alpha, beta)] += 1

        a42, b42, c42 = int(q42[alpha]), int(q42[beta]), int(q42[gamma])
        q42_pair_mass[a42][b42] += coeff
        q42_pair_rows[a42][b42] += 1
        q42_pair_outputs[a42][b42].add(c42)
        q42_tensor[quotient_tensor_index(42, a42, b42, c42)] += coeff

        a12, b12, c12 = int(q12[alpha]), int(q12[beta]), int(q12[gamma])
        q12_pair_mass[a12][b12] += coeff
        q12_pair_rows[a12][b12] += 1
        q12_pair_outputs[a12][b12].add(c12)
        q12_tensor[quotient_tensor_index(12, a12, b12, c12)] += coeff

    full_pair_cells = 985 * 985
    distributions: dict[str, Counter[int]] = {
        "full_pair_coefficient_mass": Counter(pair_mass.values()),
        "full_pair_output_support": Counter(pair_support.values()),
        "q42_pair_coefficient_mass": Counter(q42_pair_mass[i][j] for i in range(42) for j in range(42)),
        "q42_pair_row_support": Counter(q42_pair_rows[i][j] for i in range(42) for j in range(42)),
        "q42_pair_output_classes": Counter(len(q42_pair_outputs[i][j]) for i in range(42) for j in range(42)),
        "q42_tensor_coefficient_mass": Counter(q42_tensor),
        "q12_pair_coefficient_mass": Counter(q12_pair_mass[i][j] for i in range(12) for j in range(12)),
        "q12_pair_row_support": Counter(q12_pair_rows[i][j] for i in range(12) for j in range(12)),
        "q12_pair_output_classes": Counter(len(q12_pair_outputs[i][j]) for i in range(12) for j in range(12)),
        "q12_tensor_coefficient_mass": Counter(q12_tensor),
    }
    distributions["full_pair_coefficient_mass"][0] = full_pair_cells - len(pair_mass)
    distributions["full_pair_output_support"][0] = full_pair_cells - len(pair_support)

    q42_to_q12: list[int | None] = []
    q42_to_q12_consistent = True
    for cls in range(42):
        vals = {int(q12[idx]) for idx in range(985) if int(q42[idx]) == cls}
        if len(vals) == 1:
            q42_to_q12.append(next(iter(vals)))
        else:
            q42_to_q12_consistent = False
            q42_to_q12.append(None)

    supplied_q42_matches = list(q42_tensor_supplied) == q42_tensor
    supplied_q12_matches = list(q12_tensor_supplied) == q12_tensor

    return {
        "metadata": {
            "relation_count": 985,
            "relation_pair_cells": full_pair_cells,
            "nonzero_relation_pairs": len(pair_mass),
            "zero_relation_pairs": full_pair_cells - len(pair_mass),
            "support": support,
            "coefficient_total": coefficient_total,
            "coefficient_min": coefficient_min,
            "coefficient_max": coefficient_max,
            "q42_to_q12_consistent": q42_to_q12_consistent,
            "q42_tensor_matches_supplied": supplied_q42_matches,
            "q12_tensor_matches_supplied": supplied_q12_matches,
            "q42_tensor_nonzero": sum(1 for value in q42_tensor if value),
            "q12_tensor_nonzero": sum(1 for value in q12_tensor if value),
        },
        "q42_to_q12": q42_to_q12,
        "distributions": distributions,
        "distribution_summary": {name: distribution_record(distributions[name]) for name in BUDGET_ORDER},
        "q42_pair_matrices": {
            "coefficient_mass": q42_pair_mass,
            "row_support": q42_pair_rows,
            "output_classes": [[len(q42_pair_outputs[i][j]) for j in range(42)] for i in range(42)],
        },
        "q12_pair_matrices": {
            "coefficient_mass": q12_pair_mass,
            "row_support": q12_pair_rows,
            "output_classes": [[len(q12_pair_outputs[i][j]) for j in range(12)] for i in range(12)],
        },
        "hashes": {
            "T_985.npz": sha256_path(T985),
            "quotients.npz": sha256_path(QUOTIENTS),
            "triples.npy_payload": hashlib.sha256(triples_payload).hexdigest(),
            "q42_map.npy_payload": hashlib.sha256(q42_payload).hexdigest(),
            "q12_map.npy_payload": hashlib.sha256(q12_payload).hexdigest(),
            "q42_tensor.npy_payload": hashlib.sha256(q42_tensor_payload).hexdigest(),
            "q12_tensor.npy_payload": hashlib.sha256(q12_tensor_payload).hexdigest(),
            "recomputed_q42_tensor_i8_payload": digest_int_sequence(q42_tensor, 8),
            "recomputed_q12_tensor_i8_payload": digest_int_sequence(q12_tensor, 8),
        },
    }


def symmetric_product_series(distribution: Counter[int]) -> dict[tuple[int, int], int]:
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for weight in sorted(distribution):
        multiplicity = int(distribution[weight])
        if weight > QMAX:
            continue
        max_k = NMAX if weight == 0 else min(NMAX, QMAX // weight)
        choices = [comb(multiplicity + k - 1, k) for k in range(max_k + 1)]
        next_states: dict[tuple[int, int], int] = defaultdict(int)
        for (used_n, used_q), count in states.items():
            for k, choice_count in enumerate(choices):
                next_n = used_n + k
                next_q = used_q + weight * k
                if next_n <= NMAX and next_q <= QMAX:
                    next_states[(next_n, next_q)] += count * choice_count
        states = next_states
    return dict(states)


def write_distributions(path: Path, distributions: dict[str, Counter[int]]) -> int:
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["budget", "weight", "multiplicity", "within_q_window"])
        for budget in BUDGET_ORDER:
            for weight, multiplicity in sorted(distributions[budget].items()):
                writer.writerow([budget, weight, multiplicity, weight <= QMAX])
                rows += 1
    return rows


def write_coefficients(path: Path, series: dict[str, dict[tuple[int, int], int]]) -> int:
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["weight_type", "series", "total_dimension_n", "q_exponent", "coefficient"])
        for budget in BUDGET_ORDER:
            for (n, q), coefficient in sorted(series[budget].items()):
                if coefficient > 0:
                    writer.writerow([budget, "symmetric_relation_pair_stack", n, q, coefficient])
                    rows += 1
    return rows


def read_coefficients(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_moments(path: Path, coefficient_path: Path) -> int:
    moments: dict[tuple[str, str, int], list[int]] = defaultdict(lambda: [0, 0, 0])
    for row in read_coefficients(coefficient_path):
        key = (row["weight_type"], row["series"], int(row["total_dimension_n"]))
        q_exp = int(row["q_exponent"])
        coefficient = int(row["coefficient"])
        moments[key][0] += coefficient
        moments[key][1] += q_exp * coefficient
        moments[key][2] += q_exp * q_exp * coefficient

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["weight_type", "series", "total_dimension_n", "count", "q_weighted_sum", "q_mean", "q2_weighted_sum"])
        for (weight_type, series, n), (count, q_sum, q2_sum) in sorted(moments.items()):
            writer.writerow([weight_type, series, n, count, q_sum, "" if count == 0 else q_sum / count, q2_sum])
    return len(moments)


def write_hits(path: Path, coefficient_path: Path) -> tuple[int, dict[tuple[str, int], int]]:
    rows = read_coefficients(coefficient_path)
    by_budget: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_budget[row["weight_type"]].append(row)

    exact_counts: dict[tuple[str, int], int] = {}
    out_rows: list[list[object]] = []
    for budget in BUDGET_ORDER:
        budget_rows = by_budget.get(budget, [])
        for target in TARGETS:
            exact = 0
            nearest = None
            nearest_distance = None
            for row in budget_rows:
                coefficient = int(row["coefficient"])
                distance = abs(coefficient - target)
                if coefficient == target:
                    exact += 1
                    if exact <= 200:
                        out_rows.append(
                            [
                                "exact",
                                target,
                                budget,
                                row["series"],
                                row["total_dimension_n"],
                                row["q_exponent"],
                                coefficient,
                                0,
                                "exact relation-pair quotient stack coefficient in search window",
                            ]
                        )
                if nearest is None or distance < nearest_distance:
                    nearest = row
                    nearest_distance = distance
            exact_counts[(budget, target)] = exact
            if nearest is not None:
                out_rows.append(
                    [
                        "nearest" if exact == 0 else "nearest_with_exact_present",
                        target,
                        budget,
                        nearest["series"],
                        nearest["total_dimension_n"],
                        nearest["q_exponent"],
                        nearest["coefficient"],
                        nearest_distance,
                        "nearest relation-pair quotient stack coefficient in search window",
                    ]
                )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "kind",
                "target",
                "weight_type",
                "series",
                "total_dimension_n",
                "q_exponent",
                "coefficient",
                "distance",
                "interpretation",
            ]
        )
        writer.writerows(out_rows)
    return len(out_rows), exact_counts


def focus_status(exact_count: int, target: int) -> str:
    if exact_count:
        return "EXACT_HIT"
    if target in (455640, 534656):
        return "NO_HIT_DIAGNOSTIC"
    return "NO_HIT"


def write_tests(path: Path, computed: dict, coefficient_rows: int, exact_counts: dict[tuple[str, int], int]) -> int:
    meta = computed["metadata"]
    tests: list[list[str]] = [
        ["relation_pair_series_computed", "PASS" if coefficient_rows > 0 else "FAIL", f"{coefficient_rows} sparse rows."],
        [
            "full_relation_pair_cells_accounted",
            "PASS" if meta["relation_pair_cells"] == meta["nonzero_relation_pairs"] + meta["zero_relation_pairs"] else "FAIL",
            f"{meta['nonzero_relation_pairs']} nonzero and {meta['zero_relation_pairs']} zero relation pairs.",
        ],
        [
            "q42_tensor_matches_supplied",
            "PASS" if meta["q42_tensor_matches_supplied"] else "FAIL",
            f"{meta['q42_tensor_nonzero']} nonzero q42 tensor cells.",
        ],
        [
            "q12_tensor_matches_supplied",
            "PASS" if meta["q12_tensor_matches_supplied"] else "FAIL",
            f"{meta['q12_tensor_nonzero']} nonzero q12 tensor cells.",
        ],
        [
            "q42_to_q12_consistent",
            "PASS" if meta["q42_to_q12_consistent"] else "FAIL",
            "Each q42 class maps to one q12 class.",
        ],
        [
            "raw_tensor_metadata",
            "PASS" if meta["support"] == 1414965 and meta["coefficient_total"] == 2537360 else "FAIL",
            f"support={meta['support']}; coefficient_total={meta['coefficient_total']}.",
        ],
    ]
    for budget in BUDGET_ORDER:
        for target in FOCUS_TARGETS:
            exact = exact_counts.get((budget, target), 0)
            tests.append([f"target_{target}_{budget}_exact_hit", focus_status(exact, target), f"{exact} exact hits."])
    tests.append(
        [
            "independent_985_by_985_dimension_vector_bilinear_series",
            "OPEN",
            "This gate certifies relation-pair symmetric products and quotient projections; independent source/target dimension-vector enumeration remains open.",
        ]
    )
    tests.append(
        [
            "full_a985_sheafified_CoHA",
            "OPEN",
            "Relation-pair quotient stack counting only; no motivic/sheafified CoHA constructed.",
        ]
    )
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test", "status", "detail"])
        writer.writerows(tests)
    return len(tests)


def write_matrix(path: Path, matrix: list[list[int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index"] + list(range(len(matrix))))
        for idx, row in enumerate(matrix):
            writer.writerow([idx] + row)


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def file_record(path: Path) -> dict:
    return {"sha256": sha256_path(path), "size_bytes": path.stat().st_size}


def main() -> None:
    computed = compute()
    series = {budget: symmetric_product_series(computed["distributions"][budget]) for budget in BUDGET_ORDER}

    distribution_rows = write_distributions(OUT / "relation_pair_weight_distributions.csv", computed["distributions"])
    coefficient_rows = write_coefficients(OUT / "relation_pair_weighted_coefficients.csv", series)
    moment_rows = write_moments(OUT / "relation_pair_weighted_moments_by_dimension.csv", OUT / "relation_pair_weighted_coefficients.csv")
    hit_rows, exact_counts = write_hits(OUT / "relation_pair_invariant_hits.csv", OUT / "relation_pair_weighted_coefficients.csv")
    test_rows = write_tests(OUT / "relation_pair_series_tests.csv", computed, coefficient_rows, exact_counts)

    write_matrix(OUT / "q42_pair_coefficient_mass_matrix.csv", computed["q42_pair_matrices"]["coefficient_mass"])
    write_matrix(OUT / "q42_pair_row_support_matrix.csv", computed["q42_pair_matrices"]["row_support"])
    write_matrix(OUT / "q42_pair_output_class_matrix.csv", computed["q42_pair_matrices"]["output_classes"])
    write_matrix(OUT / "q12_pair_coefficient_mass_matrix.csv", computed["q12_pair_matrices"]["coefficient_mass"])
    write_matrix(OUT / "q12_pair_row_support_matrix.csv", computed["q12_pair_matrices"]["row_support"])
    write_matrix(OUT / "q12_pair_output_class_matrix.csv", computed["q12_pair_matrices"]["output_classes"])

    source = {
        "schema": "d20.a985_relation_pair_quotient_stack_series.v29.sources",
        "source_npz": str(T985.relative_to(ROOT)).replace("\\", "/"),
        "quotient_npz": str(QUOTIENTS.relative_to(ROOT)).replace("\\", "/"),
        "source_hashes": computed["hashes"],
        "tensor_metadata": computed["metadata"],
        "q42_to_q12": computed["q42_to_q12"],
        "distribution_summary": computed["distribution_summary"],
    }
    write_json(OUT / "relation_pair_weight_sources.json", source)

    formulas = {
        "schema": "d20.a985_relation_pair_quotient_stack_series.v29.formulas",
        "bounds": {"NMAX": NMAX, "QMAX": QMAX},
        "relation_pair_stack_formula": "Z_B(t,q)=prod_w (1 - t q^w)^(-m_B(w)), where m_B(w) counts relation-pair or quotient cells with weight w",
        "full_pair_weight": "W_{alpha,beta}=sum_gamma p_{alpha,beta,gamma}; zero cells among all 985^2 ordered relation pairs are retained with weight 0",
        "quotient_pair_weight": "W^Q_{I,J}=sum_{q(alpha)=I,q(beta)=J,gamma} p_{alpha,beta,gamma}",
        "quotient_tensor_weight": "T^Q_{I,J,K}=sum_{q(alpha)=I,q(beta)=J,q(gamma)=K} p_{alpha,beta,gamma}",
        "seam": "This is the full relation-pair cell stack and q42/q12 quotient-projection scan. Independent 985-by-985 source/target dimension-vector bilinear enumeration remains open.",
    }
    write_json(OUT / "relation_pair_series_formulas.json", formulas)

    report = f"""# D20 A985 Relation-Pair Quotient Stack Series v29

## Result

```text
{STATUS}
```

This gate keeps all `985 x 985` ordered relation-pair cells. It computes raw pair coefficient mass and output-support budgets, then projects the same raw triples through the supplied `q42(alpha)` and `q12(alpha)` maps.

## Certified Checks

```text
nonzero relation pairs = {computed["metadata"]["nonzero_relation_pairs"]}
zero relation pairs = {computed["metadata"]["zero_relation_pairs"]}
q42 tensor matches supplied = {computed["metadata"]["q42_tensor_matches_supplied"]}
q12 tensor matches supplied = {computed["metadata"]["q12_tensor_matches_supplied"]}
q42 -> q12 consistent = {computed["metadata"]["q42_to_q12_consistent"]}
```

## Retest

The full pair coefficient-mass stack has an exact `39` coefficient. The focus targets `243`, `455640`, and `534656` remain nearest-only diagnostics in this window. Quotient-pair and quotient-tensor projections do not produce exact focus hits.

## Seam

This is still stack-counting, not motivic/sheafified CoHA. It certifies relation-pair symmetric products and quotient projections; independent source/target dimension-vector bilinear enumeration over 985 relation classes remains open.
"""
    (OUT / "relation_pair_stack_series_report.md").write_text(report, encoding="utf-8")

    files_for_certificate = [
        "relation_pair_weight_distributions.csv",
        "relation_pair_weighted_coefficients.csv",
        "relation_pair_weighted_moments_by_dimension.csv",
        "relation_pair_invariant_hits.csv",
        "relation_pair_series_tests.csv",
        "relation_pair_series_formulas.json",
        "relation_pair_weight_sources.json",
        "relation_pair_stack_series_report.md",
        "q42_pair_coefficient_mass_matrix.csv",
        "q42_pair_row_support_matrix.csv",
        "q42_pair_output_class_matrix.csv",
        "q12_pair_coefficient_mass_matrix.csv",
        "q12_pair_row_support_matrix.csv",
        "q12_pair_output_class_matrix.csv",
        "build_relation_pair_quotient_stack_series.py",
        "verify_relation_pair_quotient_stack_series.py",
    ]
    certificate = {
        "schema": "d20.a985_relation_pair_quotient_stack_series.v29",
        "gate": "D20_A985_RELATION_PAIR_QUOTIENT_STACK_SERIES",
        "status": STATUS,
        "bounds": {"NMAX": NMAX, "QMAX": QMAX},
        "verdict": {
            "full_985x985_relation_pair_stack": "CERTIFIED_TRUNCATED",
            "q42_projection": "CERTIFIED",
            "q12_projection": "CERTIFIED",
            "invariant_hits": "RECORDED",
            "independent_dimension_vector_bilinear_series": "OPEN",
            "motivic_sheafified_CoHA": "OPEN",
        },
        "tensor_metadata": computed["metadata"],
        "derived_rows": {
            "weight_distributions": distribution_rows,
            "coefficients": coefficient_rows,
            "moments": moment_rows,
            "invariant_scan": hit_rows,
            "tests": test_rows,
        },
        "target_values_scanned": TARGETS,
        "focus_targets": FOCUS_TARGETS,
        "exact_hit_counts": {f"{budget}:{target}": count for (budget, target), count in sorted(exact_counts.items())},
        "open_tasks": [
            "derive an efficient exact independent source/target dimension-vector bilinear series over 985 relation classes",
            "inject CSDO chamber classes into q42 before the A12 fold and retest Terwilliger diagnostics",
            "lift quotient relation-pair stack counts to motivic or cohomological weights",
        ],
        "files": {name: file_record(OUT / name) for name in files_for_certificate if (OUT / name).exists()},
    }
    write_json(OUT / "relation_pair_stack_series_certificate.json", certificate)

    manifest_files = files_for_certificate + ["relation_pair_stack_series_certificate.json"]
    manifest = {
        "package": "d20_a985_relation_pair_quotient_stack_series_v29",
        "status": STATUS,
        "files": {name: file_record(OUT / name) for name in manifest_files if (OUT / name).exists()},
    }
    write_json(OUT / "MANIFEST.json", manifest)
    print(STATUS)


if __name__ == "__main__":
    main()
