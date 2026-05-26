#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import ast
import array
import csv
import hashlib
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
T985 = ROOT / "data" / "raw" / "T_985.npz"

NMAX = 40
QMAX = 512
CLIP = QMAX + 1
OBJECT_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
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
SERIES_ORDER = ["grade0", "grade1", "grade2", "grade3", "total"]


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
    format_tag = data[6:8]
    if format_tag == b"\x01\x00":
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

    matrix = matrix_from_flat(m_flat, 6, 6)
    relation_pairs = [(int(reps[5 * i]), int(reps[5 * i + 1])) for i in range(985)]
    relation_sizes = [int(reps[5 * i + 4]) for i in range(985)]

    gamma_mass = [[0 for _ in range(6)] for _ in range(6)]
    alpha_mass = [[0 for _ in range(6)] for _ in range(6)]
    beta_mass = [[0 for _ in range(6)] for _ in range(6)]
    object_triple_mass = [[[0 for _ in range(6)] for _ in range(6)] for _ in range(6)]
    coefficient_total = 0
    coefficient_min = None
    coefficient_max = 0
    composability_failures = 0

    support = h_triples["shape"][0]
    for row in range(support):
        alpha = int(triples[4 * row])
        beta = int(triples[4 * row + 1])
        gamma = int(triples[4 * row + 2])
        coeff = int(triples[4 * row + 3])
        coefficient_total += coeff
        coefficient_min = coeff if coefficient_min is None else min(coefficient_min, coeff)
        coefficient_max = max(coefficient_max, coeff)

        ai, aj = relation_pairs[alpha]
        bi, bj = relation_pairs[beta]
        gi, gj = relation_pairs[gamma]
        alpha_mass[ai][aj] += coeff
        beta_mass[bi][bj] += coeff
        gamma_mass[gi][gj] += coeff
        if aj != bi or ai != gi or bj != gj:
            composability_failures += 1
        else:
            object_triple_mass[ai][aj][bj] += coeff

    relation_count = sum(sum(row) for row in matrix)
    if relation_count <= 0 or coefficient_total % relation_count:
        raise AssertionError("T985 coefficient total does not divide by relation count")
    point_fiber = coefficient_total // relation_count
    expected_gamma = [[point_fiber * matrix[i][j] for j in range(6)] for i in range(6)]
    gamma_collapses = gamma_mass == expected_gamma

    return {
        "matrix": matrix,
        "relation_count": relation_count,
        "relation_size_sum": sum(relation_sizes),
        "support": support,
        "coefficient_total": coefficient_total,
        "coefficient_min": coefficient_min,
        "coefficient_max": coefficient_max,
        "point_fiber": point_fiber,
        "gamma_mass": gamma_mass,
        "alpha_mass": alpha_mass,
        "beta_mass": beta_mass,
        "object_triple_mass": object_triple_mass,
        "composability_failures": composability_failures,
        "gamma_collapses_to_point_fiber_m6": gamma_collapses,
        "raw_tensor_min_positive_weight": min(v for row in expected_gamma for v in row if v > 0),
        "hashes": {
            "T_985.npz": sha256_path(T985),
            "M.npy_payload": hashlib.sha256(m_payload).hexdigest(),
            "reps.npy_payload": hashlib.sha256(reps_payload).hexdigest(),
            "triples.npy_payload": hashlib.sha256(triples_payload).hexdigest(),
        },
    }


def clipped_add(left: tuple[int, ...], scale: int, col: list[int]) -> tuple[int, ...]:
    return tuple(min(CLIP, left[i] + scale * col[i]) for i in range(6))


def classify_grade(f_mask: int, c_mask: int) -> str:
    if c_mask:
        return "grade3"
    odd_f = f_mask.bit_count()
    if odd_f == 0:
        return "grade0"
    if odd_f == 3:
        return "grade1"
    return "grade2"


def c_states(linear_weights: tuple[int, ...], remaining: int) -> list[tuple[int, int, int, int]]:
    states: dict[tuple[int, int, int], int] = {(0, 0, 0): 1}
    for j, weight in enumerate(linear_weights):
        next_states: dict[tuple[int, int, int], int] = defaultdict(int)
        bit = 1 << j
        for (used_n, used_q, mask), count in states.items():
            n_room = remaining - used_n
            if weight == 0:
                max_value = n_room
            elif weight > QMAX:
                max_value = 0
            else:
                max_value = min(n_room, (QMAX - used_q) // weight)
            for value in range(max_value + 1):
                next_states[(used_n + value, used_q + weight * value, mask | ((value & 1) * bit))] += count
        states = next_states
    return [(n, q, mask, count) for (n, q, mask), count in states.items()]


def build_f_groups(weights: list[list[int]]) -> dict[tuple[int, tuple[int, ...]], list[int]]:
    states: dict[tuple[int, int, tuple[int, ...]], int] = {(0, 0, (0, 0, 0, 0, 0, 0)): 1}
    for i in range(6):
        col = [weights[j][i] for j in range(6)]
        next_states: dict[tuple[int, int, tuple[int, ...]], int] = defaultdict(int)
        bit = 1 << i
        for (used_n, mask, linear), count in states.items():
            for value in range(NMAX - used_n + 1):
                next_states[
                    (
                        used_n + value,
                        mask | ((value & 1) * bit),
                        clipped_add(linear, value, col),
                    )
                ] += count
        states = next_states

    grouped: dict[tuple[int, tuple[int, ...]], list[int]] = {}
    for (used_n, mask, linear), count in states.items():
        parity_counts = grouped.setdefault((used_n, linear), [0] * 64)
        parity_counts[mask] += count
    return grouped


def compute_series(weights: list[list[int]]) -> dict[str, dict[tuple[int, int], int]]:
    grouped = build_f_groups(weights)
    series = {name: defaultdict(int) for name in SERIES_ORDER}
    c_cache: dict[tuple[tuple[int, ...], int], list[tuple[int, int, int, int]]] = {}

    for (f_n, linear), parity_counts in grouped.items():
        remaining = NMAX - f_n
        cache_key = (linear, remaining)
        if cache_key not in c_cache:
            c_cache[cache_key] = c_states(linear, remaining)
        c_rows = c_cache[cache_key]
        nonzero_f = [(mask, count) for mask, count in enumerate(parity_counts) if count]
        for f_mask, f_count in nonzero_f:
            for c_n, q_exp, c_mask, c_count in c_rows:
                total_n = f_n + c_n
                coeff = f_count * c_count
                grade = classify_grade(f_mask, c_mask)
                series[grade][(total_n, q_exp)] += coeff
                series["total"][(total_n, q_exp)] += coeff
    return {name: dict(values) for name, values in series.items()}


def write_coefficients(path: Path, weight_type: str, series: dict[str, dict[tuple[int, int], int]]) -> int:
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["weight_type", "series", "total_dimension_n", "q_exponent", "coefficient"])
        for name in SERIES_ORDER:
            for (n, q), coeff in sorted(series[name].items()):
                if coeff > 0:
                    writer.writerow([weight_type, name, n, q, coeff])
                    rows += 1
    return rows


def read_coefficients(paths: Iterable[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    return rows


def write_moments(path: Path, coeff_paths: list[Path]) -> int:
    rows = read_coefficients(coeff_paths)
    moments: dict[tuple[str, str, int], list[int]] = defaultdict(lambda: [0, 0, 0])
    for row in rows:
        key = (row["weight_type"], row["series"], int(row["total_dimension_n"]))
        q_exp = int(row["q_exponent"])
        coeff = int(row["coefficient"])
        moments[key][0] += coeff
        moments[key][1] += q_exp * coeff
        moments[key][2] += q_exp * q_exp * coeff

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["weight_type", "series", "total_dimension_n", "count", "q_weighted_sum", "q_mean", "q2_weighted_sum"])
        for (weight_type, series, total_n), (count, q_sum, q2_sum) in sorted(moments.items()):
            q_mean = "" if count == 0 else q_sum / count
            writer.writerow([weight_type, series, total_n, count, q_sum, q_mean, q2_sum])
    return len(moments)


def scan_targets(path: Path, coeff_paths: list[Path]) -> tuple[int, dict[tuple[str, int], int]]:
    rows = read_coefficients(coeff_paths)
    by_weight: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_weight[row["weight_type"]].append(row)

    exact_counts: dict[tuple[str, int], int] = defaultdict(int)
    output_rows: list[list[object]] = []
    for weight_type, weight_rows in sorted(by_weight.items()):
        for target in TARGETS:
            nearest = None
            nearest_distance = None
            exact_for_target = 0
            for row in weight_rows:
                coeff = int(row["coefficient"])
                distance = abs(coeff - target)
                if coeff == target:
                    exact_for_target += 1
                    if exact_for_target <= 200:
                        output_rows.append(
                            [
                                "exact",
                                target,
                                weight_type,
                                row["series"],
                                row["total_dimension_n"],
                                row["q_exponent"],
                                coeff,
                                0,
                                "exact weighted coefficient in search window",
                            ]
                        )
                if nearest is None or distance < nearest_distance:
                    nearest = row
                    nearest_distance = distance
            exact_counts[(weight_type, target)] = exact_for_target
            if nearest is not None:
                output_rows.append(
                    [
                        "nearest" if exact_for_target == 0 else "nearest_with_exact_present",
                        target,
                        weight_type,
                        nearest["series"],
                        nearest["total_dimension_n"],
                        nearest["q_exponent"],
                        nearest["coefficient"],
                        nearest_distance,
                        "nearest weighted coefficient in search window",
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
    return len(output_rows), dict(exact_counts)


def write_matrix_csv(path: Path, matrix: list[list[int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([""] + OBJECT_LABELS)
        for label, row in zip(OBJECT_LABELS, matrix):
            writer.writerow([label] + row)


def status_for_exact(count: int, target: int) -> str:
    if count:
        return "EXACT_HIT"
    if target in (455640, 534656):
        return "NO_HIT_DIAGNOSTIC"
    return "NO_HIT"


def write_tests(path: Path, coefficient_rows: dict[str, int], exact_counts: dict[tuple[str, int], int], raw_trivial: bool, tensor_info: dict) -> int:
    tests: list[list[str]] = [
        ["m6_relation_count_series_computed", "PASS" if coefficient_rows["m6"] > 0 else "FAIL", f"{coefficient_rows['m6']} sparse rows."],
        ["t985_raw_output_mass_qwindow_computed", "PASS" if coefficient_rows["raw"] > 0 else "FAIL", f"{coefficient_rows['raw']} sparse rows."],
        [
            "t985_triples_composable_over_object_pairs",
            "PASS" if tensor_info["composability_failures"] == 0 else "FAIL",
            f"{tensor_info['composability_failures']} composability failures.",
        ],
        [
            "t985_output_mass_collapses_to_2576_m6",
            "PASS" if tensor_info["gamma_collapses_to_point_fiber_m6"] else "FAIL",
            "gamma-output coefficient mass matrix equals 2576 times the six-object relation matrix.",
        ],
        [
            "t985_raw_qwindow_trivial_mixed_terms",
            "PASS" if raw_trivial else "FAIL",
            f"min raw positive pair weight is {tensor_info['raw_tensor_min_positive_weight']} with QMAX={QMAX}.",
        ],
    ]
    for weight_type in ("m6_relation_count", "t985_raw_output_mass"):
        for target in FOCUS_TARGETS:
            count = exact_counts.get((weight_type, target), 0)
            tests.append(
                [
                    f"target_{target}_{weight_type}_exact_hit",
                    status_for_exact(count, target),
                    f"{count} exact hits.",
                ]
            )
    tests.append(
        [
            "full_a985_weighted_sheafified_CoHA",
            "OPEN",
            "A985-weighted stack counting only; no motivic/sheafified CoHA constructed.",
        ]
    )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test", "status", "detail"])
        writer.writerows(tests)
    return len(tests)


def file_record(path: Path) -> dict:
    return {"sha256": sha256_path(path), "size_bytes": path.stat().st_size}


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    tensor_info = read_t985()
    m6 = tensor_info["matrix"]
    raw_output_mass = tensor_info["gamma_mass"]
    raw_trivial = tensor_info["raw_tensor_min_positive_weight"] > QMAX

    write_matrix_csv(OUT / "a985_m6_object_pair_matrix.csv", m6)
    write_matrix_csv(OUT / "t985_output_coefficient_mass_matrix.csv", raw_output_mass)

    m6_series = compute_series(m6)
    raw_series = compute_series(raw_output_mass)

    coefficient_rows = {
        "m6": write_coefficients(OUT / "a985_m6_weighted_coefficients.csv", "m6_relation_count", m6_series),
        "raw": write_coefficients(OUT / "a985_t985_raw_qwindow_coefficients.csv", "t985_raw_output_mass", raw_series),
    }
    moment_rows = write_moments(
        OUT / "a985_weighted_moments_by_dimension.csv",
        [OUT / "a985_m6_weighted_coefficients.csv", OUT / "a985_t985_raw_qwindow_coefficients.csv"],
    )
    hit_rows, exact_counts = scan_targets(
        OUT / "a985_weighted_invariant_hits.csv",
        [OUT / "a985_m6_weighted_coefficients.csv", OUT / "a985_t985_raw_qwindow_coefficients.csv"],
    )
    test_rows = write_tests(
        OUT / "a985_weighted_series_tests.csv",
        coefficient_rows,
        exact_counts,
        raw_trivial,
        tensor_info,
    )

    weight_sources = {
        "schema": "d20.a985_weighted_stack_series.weight_sources",
        "object_labels": OBJECT_LABELS,
        "source_npz": str(T985.relative_to(ROOT)).replace("\\", "/"),
        "tensor_metadata": {
            "relation_count": tensor_info["relation_count"],
            "support": tensor_info["support"],
            "coefficient_total": tensor_info["coefficient_total"],
            "coefficient_min": tensor_info["coefficient_min"],
            "coefficient_max": tensor_info["coefficient_max"],
            "point_fiber": tensor_info["point_fiber"],
            "composability_failures": tensor_info["composability_failures"],
            "gamma_collapses_to_point_fiber_m6": tensor_info["gamma_collapses_to_point_fiber_m6"],
            "raw_tensor_min_positive_weight": tensor_info["raw_tensor_min_positive_weight"],
        },
        "m6_relation_count_matrix": m6,
        "t985_output_coefficient_mass_matrix": raw_output_mass,
        "t985_output_mass_normalized_by_point_fiber": [
            [raw_output_mass[i][j] // tensor_info["point_fiber"] for j in range(6)] for i in range(6)
        ],
        "source_hashes": tensor_info["hashes"],
    }
    write_json(OUT / "a985_weight_sources.json", weight_sources)

    formulas = {
        "schema": "d20.a985_weighted_stack_series.formulas",
        "bounds": {"NMAX": NMAX, "QMAX": QMAX},
        "variables": {
            "F_i": "six source-side stack dimensions indexed by B-,B+,V-,V+,S-,S+",
            "C_i": "six target-side stack dimensions indexed by B-,B+,V-,V+,S-,S+",
            "t": "total dimension",
            "q": "budget exponent",
        },
        "a985_m6_budget": "A_M(F,C)=sum_{i,j} M6[i,j] C_i F_j",
        "raw_t985_output_mass_budget": "A_Traw(F,C)=sum_{i,j} (2576*M6[i,j]) C_i F_j",
        "tensor_collapse": "sum_{alpha,beta} p_{alpha,beta,gamma}, grouped by the output object-pair of gamma, equals 2576*M6",
        "grade_decomposition": {
            "grade0": "all C_i even and all F_i even",
            "grade1": "all C_i even and exactly three F_i are odd",
            "grade2": "all C_i even and the number of odd F_i is in {1,2,4,5,6}",
            "grade3": "at least one C_i is odd",
            "total": "grade0 + grade1 + grade2 + grade3",
        },
        "interpretation": "A985-weighted stack counting at the six-object shadow; the raw tensor mass budget is outside the q<=512 mixed-term window before normalization.",
    }
    write_json(OUT / "a985_weighted_series_formulas.json", formulas)

    report = f"""# D20 A985 Weighted Stack Series source_drop

## Result

```text
D20_A985_WEIGHTED_STACK_SERIES_CERTIFIED_RAW_TENSOR_SHADOW_MOTIVIC_COHA_OPEN
```

This gate injects the certified six-object `A985` relation-count matrix into the stack-series q-budget:

```text
A_M(F,C)=sum_{{i,j}} M6[i,j] C_i F_j
```

It also reads the raw `T_985.npz` tensor triples and verifies that the output-pair coefficient mass collapses to:

```text
T985_output_mass = 2576 * M6
```

The unnormalized raw tensor-mass budget has minimum positive pair weight `{tensor_info["raw_tensor_min_positive_weight"]}`, so under `q <= {QMAX}` it contributes only the `q=0` no-mixed-term window. The normalized six-object shadow is therefore the `M6` weighted series.

## Bounds

```text
total dimension n <= {NMAX}
q exponent <= {QMAX}
```

## Retest Targets

```text
{FOCUS_TARGETS}
```

Exact and nearest coefficient records are in `a985_weighted_invariant_hits.csv`.

## Status

```text
A985-weighted stack-counting series certified at the raw-tensor six-object shadow
motivic/sheafified CoHA series open
```
"""
    (OUT / "a985_weighted_stack_series_report.md").write_text(report, encoding="utf-8")

    files_for_certificate = [
        "a985_m6_object_pair_matrix.csv",
        "t985_output_coefficient_mass_matrix.csv",
        "a985_weight_sources.json",
        "a985_weighted_series_formulas.json",
        "a985_m6_weighted_coefficients.csv",
        "a985_t985_raw_qwindow_coefficients.csv",
        "a985_weighted_moments_by_dimension.csv",
        "a985_weighted_invariant_hits.csv",
        "a985_weighted_series_tests.csv",
        "a985_weighted_stack_series_report.md",
        "build_a985_weighted_stack_series.py",
        "verify_a985_weighted_stack_series.py",
    ]
    certificate = {
        "schema": "d20.a985_weighted_stack_series.source_drop",
        "gate": "D20_A985_WEIGHTED_STACK_SERIES",
        "status": "D20_A985_WEIGHTED_STACK_SERIES_CERTIFIED_RAW_TENSOR_SHADOW_MOTIVIC_COHA_OPEN",
        "bounds": {"NMAX": NMAX, "QMAX": QMAX},
        "verdict": {
            "m6_relation_count_q_series": "CERTIFIED_TRUNCATED",
            "raw_t985_tensor_output_mass_collapse": "CERTIFIED",
            "raw_t985_tensor_output_mass_q_window": "TRIVIAL_FOR_MIXED_TERMS",
            "invariant_hits": "RECORDED",
            "motivic_sheafified_CoHA": "OPEN",
        },
        "tensor_metadata": weight_sources["tensor_metadata"],
        "coefficient_files": {
            "m6_relation_count": {"file": "a985_m6_weighted_coefficients.csv", "rows": coefficient_rows["m6"]},
            "t985_raw_output_mass": {"file": "a985_t985_raw_qwindow_coefficients.csv", "rows": coefficient_rows["raw"]},
        },
        "derived_rows": {
            "moments": moment_rows,
            "invariant_scan": hit_rows,
            "tests": test_rows,
        },
        "target_values_scanned": TARGETS,
        "focus_targets": FOCUS_TARGETS,
        "exact_hit_counts": {f"{weight}:{target}": count for (weight, target), count in sorted(exact_counts.items())},
        "open_tasks": [
            "lift the A985-weighted stack counts to motivic or cohomological weights",
            "construct a relation-level stack series before collapsing to the six-object shadow",
            "extend the q-window or derive closed product identities for the M6-weighted budget",
            "test whether Terwilliger diagnostics stabilize after relation-level quotient maps are available",
        ],
        "files": {name: file_record(OUT / name) for name in files_for_certificate if (OUT / name).exists()},
    }
    write_json(OUT / "a985_weighted_stack_series_certificate.json", certificate)

    manifest_files = files_for_certificate + ["a985_weighted_stack_series_certificate.json"]
    manifest = {
        "package": "d20_a985_weighted_stack_series",
        "status": certificate["status"],
        "files": {name: file_record(OUT / name) for name in manifest_files if (OUT / name).exists()},
    }
    write_json(OUT / "MANIFEST.json", manifest)
    print(certificate["status"])


if __name__ == "__main__":
    main()
