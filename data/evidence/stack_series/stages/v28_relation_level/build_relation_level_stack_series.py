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
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
T985 = ROOT / "data" / "raw" / "T_985.npz"

NMAX = 40
QMAX = 512
STATUS = "D20_A985_RELATION_LEVEL_STACK_SERIES_CERTIFIED_RAW_TENSOR_MOTIVIC_COHA_OPEN"
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
OBJECT_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
BUDGET_ORDER = [
    "tensor_coefficient_value",
    "relation_orbit_size",
    "left_relation_coefficient_mass",
    "right_relation_coefficient_mass",
    "output_relation_coefficient_mass",
    "left_relation_support",
    "right_relation_support",
    "output_relation_support",
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
    if descr == "<i4":
        arr = array.array("i")
    elif descr == "<i8":
        arr = array.array("q")
    else:
        raise ValueError(f"unsupported dtype for {name}: {descr}")
    arr.frombytes(payload)
    return header, arr, payload


def matrix_from_flat(flat: array.array, rows: int, cols: int) -> list[list[int]]:
    return [[int(flat[r * cols + c]) for c in range(cols)] for r in range(rows)]


def counter_rows(counter: Counter[int]) -> list[dict[str, int]]:
    return [{"weight": int(weight), "multiplicity": int(counter[weight])} for weight in sorted(counter)]


def read_t985() -> dict:
    with zipfile.ZipFile(T985) as npz:
        h_m, m_flat, m_payload = load_npy_member(npz, "M.npy")
        h_reps, reps, reps_payload = load_npy_member(npz, "reps.npy")
        h_triples, triples, triples_payload = load_npy_member(npz, "triples.npy")

    if h_m["shape"] != (6, 6):
        raise AssertionError(f"unexpected M shape: {h_m['shape']}")
    if h_reps["shape"] != (985, 5):
        raise AssertionError(f"unexpected reps shape: {h_reps['shape']}")
    if len(h_triples["shape"]) != 2 or h_triples["shape"][1] != 4:
        raise AssertionError(f"unexpected triples shape: {h_triples['shape']}")

    relation_count = h_reps["shape"][0]
    support = h_triples["shape"][0]
    m6 = matrix_from_flat(m_flat, 6, 6)
    relation_source = [int(reps[5 * i]) for i in range(relation_count)]
    relation_target = [int(reps[5 * i + 1]) for i in range(relation_count)]
    relation_orbit_sizes = [int(reps[5 * i + 4]) for i in range(relation_count)]

    coefficient_values: Counter[int] = Counter()
    left_mass = [0] * relation_count
    right_mass = [0] * relation_count
    output_mass = [0] * relation_count
    left_support = [0] * relation_count
    right_support = [0] * relation_count
    output_support = [0] * relation_count
    object_path_support: Counter[tuple[int, int, int]] = Counter()
    object_path_mass: Counter[tuple[int, int, int]] = Counter()
    coefficient_total = 0
    coefficient_min = None
    coefficient_max = 0
    composability_failures = 0

    for row in range(support):
        alpha = int(triples[4 * row])
        beta = int(triples[4 * row + 1])
        gamma = int(triples[4 * row + 2])
        coeff = int(triples[4 * row + 3])
        coefficient_values[coeff] += 1
        coefficient_total += coeff
        coefficient_min = coeff if coefficient_min is None else min(coefficient_min, coeff)
        coefficient_max = max(coefficient_max, coeff)

        left_mass[alpha] += coeff
        right_mass[beta] += coeff
        output_mass[gamma] += coeff
        left_support[alpha] += 1
        right_support[beta] += 1
        output_support[gamma] += 1

        ai, aj = relation_source[alpha], relation_target[alpha]
        bi, bj = relation_source[beta], relation_target[beta]
        gi, gj = relation_source[gamma], relation_target[gamma]
        if aj != bi or ai != gi or bj != gj:
            composability_failures += 1
        else:
            object_path_support[(ai, aj, bj)] += 1
            object_path_mass[(ai, aj, bj)] += coeff

    output_counter = Counter(output_mass)
    output_uniform = len(output_counter) == 1
    point_fiber = next(iter(output_counter)) if output_uniform else None
    expected_output_total = point_fiber * relation_count if point_fiber is not None else None

    budgets: dict[str, Counter[int]] = {
        "tensor_coefficient_value": coefficient_values,
        "relation_orbit_size": Counter(relation_orbit_sizes),
        "left_relation_coefficient_mass": Counter(left_mass),
        "right_relation_coefficient_mass": Counter(right_mass),
        "output_relation_coefficient_mass": output_counter,
        "left_relation_support": Counter(left_support),
        "right_relation_support": Counter(right_support),
        "output_relation_support": Counter(output_support),
    }

    return {
        "m6": m6,
        "relation_source": relation_source,
        "relation_target": relation_target,
        "relation_orbit_sizes": relation_orbit_sizes,
        "budgets": budgets,
        "object_path_support": object_path_support,
        "object_path_mass": object_path_mass,
        "metadata": {
            "relation_count": relation_count,
            "support": support,
            "coefficient_total": coefficient_total,
            "coefficient_min": coefficient_min,
            "coefficient_max": coefficient_max,
            "composability_failures": composability_failures,
            "output_relation_mass_uniform": output_uniform,
            "output_relation_mass_value": point_fiber,
            "expected_output_total": expected_output_total,
        },
        "hashes": {
            "T_985.npz": sha256_path(T985),
            "M.npy_payload": hashlib.sha256(m_payload).hexdigest(),
            "reps.npy_payload": hashlib.sha256(reps_payload).hexdigest(),
            "triples.npy_payload": hashlib.sha256(triples_payload).hexdigest(),
        },
    }


def symmetric_stack_series(distribution: Counter[int]) -> dict[tuple[int, int], int]:
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for weight in sorted(distribution):
        multiplicity = int(distribution[weight])
        if weight > QMAX:
            continue
        next_states: dict[tuple[int, int], int] = defaultdict(int)
        max_k = min(NMAX, QMAX // weight)
        choices = [comb(multiplicity + k - 1, k) for k in range(max_k + 1)]
        for (used_n, used_q), count in states.items():
            for k, choice_count in enumerate(choices):
                next_n = used_n + k
                next_q = used_q + weight * k
                if next_n <= NMAX and next_q <= QMAX:
                    next_states[(next_n, next_q)] += count * choice_count
        states = next_states
    return dict(states)


def write_weight_distribution(path: Path, tensor_info: dict) -> int:
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["budget", "weight", "multiplicity", "within_q_window"])
        for budget in BUDGET_ORDER:
            for weight, multiplicity in sorted(tensor_info["budgets"][budget].items()):
                writer.writerow([budget, weight, multiplicity, weight <= QMAX])
                rows += 1
    return rows


def write_object_path_summary(path: Path, object_path_support: Counter, object_path_mass: Counter) -> int:
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_object", "middle_object", "target_object", "support", "coefficient_mass"])
        for key in sorted(object_path_support):
            i, j, k = key
            writer.writerow([OBJECT_LABELS[i], OBJECT_LABELS[j], OBJECT_LABELS[k], object_path_support[key], object_path_mass[key]])
            rows += 1
    return rows


def write_coefficients(path: Path, series_by_budget: dict[str, dict[tuple[int, int], int]]) -> int:
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["weight_type", "series", "total_dimension_n", "q_exponent", "coefficient"])
        for budget in BUDGET_ORDER:
            for (n, q), coefficient in sorted(series_by_budget[budget].items()):
                if coefficient > 0:
                    writer.writerow([budget, "symmetric_stack", n, q, coefficient])
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
            writer.writerow([weight_type, series, n, count, "" if count == 0 else q_sum / count, q2_sum])
    return len(moments)


def write_invariant_hits(path: Path, coefficient_path: Path) -> tuple[int, dict[tuple[str, int], int]]:
    rows = read_coefficients(coefficient_path)
    by_budget: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_budget[row["weight_type"]].append(row)

    output_rows: list[list[object]] = []
    exact_counts: dict[tuple[str, int], int] = {}
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
                        output_rows.append(
                            [
                                "exact",
                                target,
                                budget,
                                row["series"],
                                row["total_dimension_n"],
                                row["q_exponent"],
                                coefficient,
                                0,
                                "exact relation-level weighted coefficient in search window",
                            ]
                        )
                if nearest is None or distance < nearest_distance:
                    nearest = row
                    nearest_distance = distance
            exact_counts[(budget, target)] = exact
            if nearest is not None:
                output_rows.append(
                    [
                        "nearest" if exact == 0 else "nearest_with_exact_present",
                        target,
                        budget,
                        nearest["series"],
                        nearest["total_dimension_n"],
                        nearest["q_exponent"],
                        nearest["coefficient"],
                        nearest_distance,
                        "nearest relation-level weighted coefficient in search window",
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
        writer.writerows(output_rows)
    return len(output_rows), exact_counts


def focus_status(exact_count: int, target: int) -> str:
    if exact_count:
        return "EXACT_HIT"
    if target in (455640, 534656):
        return "NO_HIT_DIAGNOSTIC"
    return "NO_HIT"


def write_tests(path: Path, tensor_info: dict, coefficient_rows: int, exact_counts: dict[tuple[str, int], int]) -> int:
    metadata = tensor_info["metadata"]
    tests: list[list[str]] = [
        ["relation_level_series_computed", "PASS" if coefficient_rows > 0 else "FAIL", f"{coefficient_rows} sparse rows."],
        [
            "t985_triples_composable_over_relation_object_pairs",
            "PASS" if metadata["composability_failures"] == 0 else "FAIL",
            f"{metadata['composability_failures']} composability failures.",
        ],
        [
            "output_relation_mass_uniform",
            "PASS" if metadata["output_relation_mass_uniform"] else "FAIL",
            f"output relation mass value {metadata['output_relation_mass_value']}.",
        ],
        [
            "raw_tensor_metadata",
            "PASS"
            if metadata["relation_count"] == 985 and metadata["support"] == 1414965 and metadata["coefficient_total"] == 2537360
            else "FAIL",
            f"relations={metadata['relation_count']}; support={metadata['support']}; coefficient_total={metadata['coefficient_total']}.",
        ],
    ]
    for budget in BUDGET_ORDER:
        for target in FOCUS_TARGETS:
            exact = exact_counts.get((budget, target), 0)
            tests.append([f"target_{target}_{budget}_exact_hit", focus_status(exact, target), f"{exact} exact hits."])
    tests.append(
        [
            "full_relation_pair_bilinear_stack",
            "OPEN",
            "This gate uses relation/tensor symmetric-product budgets; it does not yet enumerate a 985x985 relation-pair bilinear stack.",
        ]
    )
    tests.append(
        [
            "full_a985_relation_level_sheafified_CoHA",
            "OPEN",
            "Raw relation-level stack counting only; no motivic/sheafified CoHA constructed.",
        ]
    )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test", "status", "detail"])
        writer.writerows(tests)
    return len(tests)


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def file_record(path: Path) -> dict:
    return {"sha256": sha256_path(path), "size_bytes": path.stat().st_size}


def distribution_summary(tensor_info: dict) -> dict:
    out = {}
    for budget in BUDGET_ORDER:
        dist = tensor_info["budgets"][budget]
        out[budget] = {
            "distinct_weights": len(dist),
            "min_weight": min(dist),
            "max_weight": max(dist),
            "classes_total": sum(dist.values()),
            "classes_in_q_window": sum(m for weight, m in dist.items() if weight <= QMAX),
            "distribution": counter_rows(dist),
        }
    return out


def main() -> None:
    tensor_info = read_t985()
    series_by_budget = {budget: symmetric_stack_series(tensor_info["budgets"][budget]) for budget in BUDGET_ORDER}

    distribution_rows = write_weight_distribution(OUT / "relation_level_weight_distributions.csv", tensor_info)
    path_rows = write_object_path_summary(
        OUT / "relation_level_object_path_summary.csv",
        tensor_info["object_path_support"],
        tensor_info["object_path_mass"],
    )
    coefficient_rows = write_coefficients(OUT / "relation_level_weighted_coefficients.csv", series_by_budget)
    moment_rows = write_moments(OUT / "relation_level_weighted_moments_by_dimension.csv", OUT / "relation_level_weighted_coefficients.csv")
    hit_rows, exact_counts = write_invariant_hits(
        OUT / "relation_level_invariant_hits.csv",
        OUT / "relation_level_weighted_coefficients.csv",
    )
    test_rows = write_tests(OUT / "relation_level_series_tests.csv", tensor_info, coefficient_rows, exact_counts)

    formulas = {
        "schema": "d20.a985_relation_level_stack_series.v28.formulas",
        "bounds": {"NMAX": NMAX, "QMAX": QMAX},
        "series_formula": "Z_B(t,q)=prod_w (1 - t q^w)^(-m_B(w)), truncated to n<=40 and q<=512",
        "coefficient_law": "[t^n q^Q] prod_w sum_{k>=0} binomial(m_B(w)+k-1,k) t^k q^{kw}",
        "budgets": {
            "tensor_coefficient_value": "one class per nonzero T985 triple, weighted by p_{alpha,beta,gamma}",
            "relation_orbit_size": "one class per A985 relation, weighted by representative relation orbit size",
            "left_relation_coefficient_mass": "one class per relation alpha, weighted by sum_{beta,gamma} p_{alpha,beta,gamma}",
            "right_relation_coefficient_mass": "one class per relation beta, weighted by sum_{alpha,gamma} p_{alpha,beta,gamma}",
            "output_relation_coefficient_mass": "one class per relation gamma, weighted by sum_{alpha,beta} p_{alpha,beta,gamma}",
            "left_relation_support": "one class per relation alpha, weighted by number of nonzero tensor rows with that alpha",
            "right_relation_support": "one class per relation beta, weighted by number of nonzero tensor rows with that beta",
            "output_relation_support": "one class per relation gamma, weighted by number of nonzero tensor rows with that gamma",
        },
        "seam": "This is relation/tensor symmetric-product stack counting, not the full 985x985 relation-pair bilinear stack and not a motivic/sheafified CoHA.",
    }
    write_json(OUT / "relation_level_series_formulas.json", formulas)

    source_summary = {
        "schema": "d20.a985_relation_level_stack_series.v28.sources",
        "object_labels": OBJECT_LABELS,
        "source_npz": str(T985.relative_to(ROOT)).replace("\\", "/"),
        "source_hashes": tensor_info["hashes"],
        "tensor_metadata": tensor_info["metadata"],
        "m6_relation_count_matrix": tensor_info["m6"],
        "distribution_summary": distribution_summary(tensor_info),
    }
    write_json(OUT / "relation_level_weight_sources.json", source_summary)

    report = f"""# D20 A985 Relation-Level Stack Series v28

## Result

```text
{STATUS}
```

This gate keeps the raw `A985` relation/tensor data before the six-object collapse. It reads `data/raw/T_985.npz`, verifies the `985` relation classes and `{tensor_info["metadata"]["support"]}` nonzero tensor triples, and computes truncated symmetric-product stack series for relation-level budgets.

## Budgets

```text
Z_B(t,q)=prod_w (1 - t q^w)^(-m_B(w)), n <= {NMAX}, q <= {QMAX}
```

The budgets are tensor coefficient values, relation orbit sizes, left/right/output coefficient masses, and left/right/output support counts.

## Retest

The focus targets are:

```text
{FOCUS_TARGETS}
```

No focus target appears as an exact coefficient in the raw relation-level budgets. The nearest rows are recorded in `relation_level_invariant_hits.csv`.

## Seam

This is not yet the full `985 x 985` relation-pair bilinear stack and not a motivic/sheafified CoHA. It is the certified raw relation/tensor symmetric-product gate.
"""
    (OUT / "relation_level_stack_series_report.md").write_text(report, encoding="utf-8")

    files_for_certificate = [
        "relation_level_weight_distributions.csv",
        "relation_level_object_path_summary.csv",
        "relation_level_weighted_coefficients.csv",
        "relation_level_weighted_moments_by_dimension.csv",
        "relation_level_invariant_hits.csv",
        "relation_level_series_tests.csv",
        "relation_level_series_formulas.json",
        "relation_level_weight_sources.json",
        "relation_level_stack_series_report.md",
        "build_relation_level_stack_series.py",
        "verify_relation_level_stack_series.py",
    ]
    certificate = {
        "schema": "d20.a985_relation_level_stack_series.v28",
        "gate": "D20_A985_RELATION_LEVEL_STACK_SERIES",
        "status": STATUS,
        "bounds": {"NMAX": NMAX, "QMAX": QMAX},
        "verdict": {
            "raw_t985_tensor_loaded": "CERTIFIED",
            "relation_level_symmetric_stack_series": "CERTIFIED_TRUNCATED",
            "invariant_hits": "RECORDED",
            "full_985x985_relation_pair_bilinear_stack": "OPEN",
            "motivic_sheafified_CoHA": "OPEN",
        },
        "tensor_metadata": tensor_info["metadata"],
        "derived_rows": {
            "weight_distributions": distribution_rows,
            "object_path_summary": path_rows,
            "coefficients": coefficient_rows,
            "moments": moment_rows,
            "invariant_scan": hit_rows,
            "tests": test_rows,
        },
        "target_values_scanned": TARGETS,
        "focus_targets": FOCUS_TARGETS,
        "exact_hit_counts": {f"{budget}:{target}": count for (budget, target), count in sorted(exact_counts.items())},
        "open_tasks": [
            "build the full 985x985 relation-pair bilinear stack budget from p_{alpha,beta,gamma}",
            "add quotient maps q42(alpha) and q12(I) to test CSDO/Terwilliger stabilization before object collapse",
            "lift relation-level counts to motivic or cohomological weights",
        ],
        "files": {name: file_record(OUT / name) for name in files_for_certificate if (OUT / name).exists()},
    }
    write_json(OUT / "relation_level_stack_series_certificate.json", certificate)

    manifest_files = files_for_certificate + ["relation_level_stack_series_certificate.json"]
    manifest = {
        "package": "d20_a985_relation_level_stack_series_v28",
        "status": STATUS,
        "files": {name: file_record(OUT / name) for name in manifest_files if (OUT / name).exists()},
    }
    write_json(OUT / "MANIFEST.json", manifest)
    print(STATUS)


if __name__ == "__main__":
    main()
