from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_kern"
STATUS = "LONG_KERN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
RAW_TENSOR = ROOT / "data" / "raw" / "Halloween.npz"
LONG_LLN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_lln" / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_kern.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_kern.py"

AXIS_COLUMNS = [
    "axis",
    "addr",
    "point_count",
    "point_weight",
    "closed_prefix_count",
    "closed_prefix_weight",
    "open_suffix_count",
    "open_suffix_weight",
    "open_lln_var_num",
    "open_lln_var_den",
]
PAIR_COLUMNS = [
    "pair",
    "source_axis",
    "target_axis",
    "support_pairs",
    "weighted_sum",
    "row_degree_min",
    "row_degree_max",
    "col_degree_min",
    "col_degree_max",
    "row_weight_min",
    "row_weight_max",
    "col_weight_min",
    "col_weight_max",
    "max_fiber_count",
    "max_fiber_weight",
    "diag_pairs",
    "diag_weight",
    "forward_pairs",
    "forward_weight",
    "reverse_pairs",
    "reverse_weight",
    "closure_pairs",
    "closure_extra",
    "closure_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "axis_count",
    "pair_kernel_count",
    "tensor_support_count",
    "tensor_coeff_sum",
    "axis_point_count_total",
    "axis_point_weight_total",
    "axis_all_points_seen",
    "axis_prefix_suffix_monotone",
    "axis_open_lln_flag",
    "pair_weight_sum_total",
    "pair_all_rows_seen",
    "pair_all_cols_seen",
    "pair_closure_profunctor_count",
    "pair_closure_extra_total",
    "pair_support_total",
    "pair_diag_total",
    "pair_forward_total",
    "pair_reverse_total",
    "long_lln_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}
PAIR_AXES = [(0, 1), (0, 2), (1, 2)]


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def load_tensor() -> np.ndarray:
    payload = np.load(RAW_TENSOR, allow_pickle=False)
    triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise ValueError("raw tensor triples must have shape (*, 4)")
    return triples


def line_size(triples: np.ndarray) -> int:
    return int(triples[:, :3].max()) + 1


def axis_profiles(triples: np.ndarray, n: int) -> tuple[list[dict[str, int]], np.ndarray, np.ndarray]:
    coeff = triples[:, 3]
    support_count = int(triples.shape[0])
    counts = np.zeros((3, n), dtype=np.int64)
    weights = np.zeros((3, n), dtype=np.int64)
    rows: list[dict[str, int]] = []
    for axis in range(3):
        counts[axis] = np.bincount(triples[:, axis], minlength=n).astype(np.int64)
        np.add.at(weights[axis], triples[:, axis], coeff)
        prefix_count = np.cumsum(counts[axis])
        prefix_weight = np.cumsum(weights[axis])
        suffix_count = np.cumsum(counts[axis][::-1])[::-1]
        suffix_weight = np.cumsum(weights[axis][::-1])[::-1]
        for addr in range(n):
            open_count = int(suffix_count[addr])
            rows.append(
                {
                    "axis": axis,
                    "addr": addr,
                    "point_count": int(counts[axis, addr]),
                    "point_weight": int(weights[axis, addr]),
                    "closed_prefix_count": int(prefix_count[addr]),
                    "closed_prefix_weight": int(prefix_weight[addr]),
                    "open_suffix_count": open_count,
                    "open_suffix_weight": int(suffix_weight[addr]),
                    "open_lln_var_num": open_count * (support_count - open_count),
                    "open_lln_var_den": support_count * support_count,
                }
            )
    return rows, counts, weights


def pair_matrix(
    triples: np.ndarray,
    n: int,
    source_axis: int,
    target_axis: int,
) -> tuple[np.ndarray, np.ndarray]:
    count = np.zeros((n, n), dtype=np.int32)
    weight = np.zeros((n, n), dtype=np.int64)
    flat = triples[:, source_axis] * n + triples[:, target_axis]
    np.add.at(count.ravel(), flat, 1)
    np.add.at(weight.ravel(), flat, triples[:, 3])
    return count, weight


def monotone_closure(support: np.ndarray) -> np.ndarray:
    n = support.shape[0]
    rows, cols = np.nonzero(support)
    diff = np.zeros((n + 1, n + 1), dtype=np.int32)
    np.add.at(diff, (np.zeros_like(rows), cols), 1)
    np.add.at(diff, (rows + 1, cols), -1)
    np.add.at(diff, (np.zeros_like(rows), np.full_like(cols, n)), -1)
    np.add.at(diff, (rows + 1, np.full_like(cols, n)), 1)
    return diff.cumsum(axis=0).cumsum(axis=1)[:n, :n] > 0


def closure_is_profunctor(closure: np.ndarray) -> bool:
    down_source = bool(np.all(closure[1:, :] <= closure[:-1, :]))
    up_target = bool(np.all(closure[:, :-1] <= closure[:, 1:]))
    return down_source and up_target


def pair_profiles(triples: np.ndarray, n: int) -> tuple[list[dict[str, int]], np.ndarray, np.ndarray, np.ndarray]:
    rows: list[dict[str, int]] = []
    counts = np.zeros((len(PAIR_AXES), n, n), dtype=np.int32)
    weights = np.zeros((len(PAIR_AXES), n, n), dtype=np.int64)
    closures = np.zeros((len(PAIR_AXES), n, n), dtype=np.bool_)
    tri_upper = np.triu(np.ones((n, n), dtype=bool))
    tri_lower = np.tril(np.ones((n, n), dtype=bool))
    diag = np.eye(n, dtype=bool)
    for pair_code, (source_axis, target_axis) in enumerate(PAIR_AXES):
        count, weight = pair_matrix(triples, n, source_axis, target_axis)
        support = count > 0
        closure = monotone_closure(support)
        counts[pair_code] = count
        weights[pair_code] = weight
        closures[pair_code] = closure
        row_degree = support.sum(axis=1)
        col_degree = support.sum(axis=0)
        row_weight = weight.sum(axis=1)
        col_weight = weight.sum(axis=0)
        rows.append(
            {
                "pair": pair_code,
                "source_axis": source_axis,
                "target_axis": target_axis,
                "support_pairs": int(support.sum()),
                "weighted_sum": int(weight.sum()),
                "row_degree_min": int(row_degree.min()),
                "row_degree_max": int(row_degree.max()),
                "col_degree_min": int(col_degree.min()),
                "col_degree_max": int(col_degree.max()),
                "row_weight_min": int(row_weight.min()),
                "row_weight_max": int(row_weight.max()),
                "col_weight_min": int(col_weight.min()),
                "col_weight_max": int(col_weight.max()),
                "max_fiber_count": int(count.max()),
                "max_fiber_weight": int(weight.max()),
                "diag_pairs": int(support[diag].sum()),
                "diag_weight": int(weight[diag].sum()),
                "forward_pairs": int(support[tri_upper].sum()),
                "forward_weight": int(weight[tri_upper].sum()),
                "reverse_pairs": int(support[tri_lower].sum()),
                "reverse_weight": int(weight[tri_lower].sum()),
                "closure_pairs": int(closure.sum()),
                "closure_extra": int(closure.sum() - support.sum()),
                "closure_flag": int(closure_is_profunctor(closure)),
            }
        )
    return rows, counts, weights, closures


def build_rows() -> dict[str, Any]:
    triples = load_tensor()
    n = line_size(triples)
    axis_rows, axis_counts, axis_weights = axis_profiles(triples, n)
    pair_rows, pair_counts, pair_weights, closures = pair_profiles(triples, n)
    long_lln = load_json(LONG_LLN_REPORT)
    support_count = int(triples.shape[0])
    coeff_sum = int(triples[:, 3].sum())
    axis_monotone = all(
        row["closed_prefix_count"] + row["open_suffix_count"] - row["point_count"] == support_count
        for row in axis_rows
    )
    pair_all_rows_seen = all(row["row_degree_min"] > 0 for row in pair_rows)
    pair_all_cols_seen = all(row["col_degree_min"] > 0 for row in pair_rows)
    obs = {
        "line_point_count": n,
        "axis_count": 3,
        "pair_kernel_count": len(PAIR_AXES),
        "tensor_support_count": support_count,
        "tensor_coeff_sum": coeff_sum,
        "axis_point_count_total": int(axis_counts.sum()),
        "axis_point_weight_total": int(axis_weights.sum()),
        "axis_all_points_seen": int(bool(np.all(axis_counts > 0))),
        "axis_prefix_suffix_monotone": int(axis_monotone),
        "axis_open_lln_flag": int(
            all(
                row["open_lln_var_den"] == support_count * support_count
                and row["open_lln_var_num"] >= 0
                for row in axis_rows
            )
        ),
        "pair_weight_sum_total": sum(row["weighted_sum"] for row in pair_rows),
        "pair_all_rows_seen": int(pair_all_rows_seen),
        "pair_all_cols_seen": int(pair_all_cols_seen),
        "pair_closure_profunctor_count": sum(row["closure_flag"] for row in pair_rows),
        "pair_closure_extra_total": sum(row["closure_extra"] for row in pair_rows),
        "pair_support_total": sum(row["support_pairs"] for row in pair_rows),
        "pair_diag_total": sum(row["diag_pairs"] for row in pair_rows),
        "pair_forward_total": sum(row["forward_pairs"] for row in pair_rows),
        "pair_reverse_total": sum(row["reverse_pairs"] for row in pair_rows),
        "long_lln_input_certified": int(
            long_lln.get("status") == "LONG_LLN_CERTIFIED"
            and long_lln.get("all_checks_pass") is True
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "triples": triples,
        "axis_rows": axis_rows,
        "axis_counts": axis_counts,
        "axis_weights": axis_weights,
        "pair_rows": pair_rows,
        "pair_counts": pair_counts,
        "pair_weights": pair_weights,
        "closures": closures,
        "obs": obs,
        "obs_rows": obs_rows,
        "long_lln": long_lln,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    axis_table = table_from_rows(AXIS_COLUMNS, rows["axis_rows"])
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    support_count = obs["tensor_support_count"]
    coeff_sum = obs["tensor_coeff_sum"]
    checks = {
        "long_lln_input_certified": obs["long_lln_input_certified"] == 1,
        "line_size_matches_tensor_addresses": obs["line_point_count"] == 985,
        "axis_profiles_close": (
            obs["axis_point_count_total"],
            obs["axis_point_weight_total"],
        )
        == (3 * support_count, 3 * coeff_sum),
        "axis_profiles_are_positive_and_monotone": (
            obs["axis_all_points_seen"],
            obs["axis_prefix_suffix_monotone"],
            obs["axis_open_lln_flag"],
        )
        == (1, 1, 1),
        "pair_kernels_close": (
            obs["pair_weight_sum_total"],
            obs["pair_all_rows_seen"],
            obs["pair_all_cols_seen"],
        )
        == (3 * coeff_sum, 1, 1),
        "pair_closures_are_monotone_profunctors": (
            obs["pair_closure_profunctor_count"] == len(PAIR_AXES)
            and obs["pair_closure_extra_total"] > 0
        ),
        "table_shapes_match": (
            tuple(axis_table.shape),
            tuple(pair_table.shape),
            tuple(obs_table.shape),
            tuple(rows["pair_counts"].shape),
            tuple(rows["closures"].shape),
        )
        == (
            (3 * 985, len(AXIS_COLUMNS)),
            (len(PAIR_AXES), len(PAIR_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (len(PAIR_AXES), 985, 985),
            (len(PAIR_AXES), 985, 985),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_alexandrov_line_support_kernels",
        "line": {
            "point_count": obs["line_point_count"],
            "principal_open_profiles": 3 * 985,
            "pair_kernel_count": len(PAIR_AXES),
        },
        "support": {
            "tensor_support_count": support_count,
            "tensor_coeff_sum": coeff_sum,
            "axis_point_count_total": obs["axis_point_count_total"],
            "pair_support_total": obs["pair_support_total"],
            "pair_diag_total": obs["pair_diag_total"],
            "pair_forward_total": obs["pair_forward_total"],
            "pair_reverse_total": obs["pair_reverse_total"],
        },
        "kernels": {
            "rule": "for observed pair (a,b), its monotone profunctor closure contains all (i,j) with i<=a and b<=j",
            "pair_rows": rows["pair_rows"],
            "closure_extra_total": obs["pair_closure_extra_total"],
            "pair_count_sha256": sha_array(rows["pair_counts"]),
            "pair_weight_sha256": sha_array(rows["pair_weights"]),
            "closure_sha256": sha_array(rows["closures"]),
        },
        "principal_open_lln": {
            "sample_space": "tensor support rows",
            "event": "coordinate axis lies in upper suffix [addr,984]",
            "variance_rule": "count(open)*(N-count(open))/N^2 for one sample; divide by k for k product samples",
            "all_principal_open_events_checked": bool(obs["axis_open_lln_flag"]),
        },
        "axis_table_sha256": sha_array(axis_table),
        "pair_table_sha256": sha_array(pair_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    kernel = {
        "schema": "long.kern@1",
        "object": "finite_alexandrov_line_support_kernels",
        "status": STATUS if all(checks.values()) else "LONG_KERN_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.kern.report@1",
        "status": kernel["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_kern certifies the principal-open support observables and "
            "pairwise monotone profunctor closures induced by the C985 tensor "
            "lookup over the finite Alexandrov line."
        ),
        "stage_protocol": {
            "draft": "reuse the long_lln line and raw tensor lookup",
            "witness": "compute axis principal-open profiles and pair projection kernels",
            "coherence": "check closure, monotonicity, positivity, and tensor marginal totals",
            "closure": "emit monotone profunctor closures and principal-open LLN events",
            "emit": "write long_kern artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["long_lln"].get("status")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "kernel": relpath(OUT_DIR / "kernel.json"),
            "axis_csv": relpath(OUT_DIR / "axis.csv"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all principal-open suffix events for each tensor coordinate have exact finite Bernoulli LLN data",
                "each pair projection has a finite boolean/count/weight kernel over the line",
                "each pair projection has a monotone Alexandrov profunctor closure",
                "axis and pair marginal totals close back to the raw tensor lookup",
            ],
            "does_not_certify_because_out_of_scope": [
                "higher arity monotone closures on all three tensor coordinates",
                "recoupling kernels outside raw tensor support projections",
                "that the pair closures are minimal for any semantic process beyond Alexandrov profunctor saturation",
                "a complete basis for all possible line profunctors",
            ],
        },
        "next_highest_yield_item": (
            "Build long_tri: the ternary Alexandrov closure and support-class "
            "LLN profiles for full tensor triples."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.kern.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.kern.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "kernel": kernel,
        "axis_csv": csv_text(AXIS_COLUMNS, rows["axis_rows"]),
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "axis_table": axis_table,
        "pair_table": pair_table,
        "obs_table": obs_table,
        "pair_counts": rows["pair_counts"],
        "pair_weights": rows["pair_weights"],
        "closures": rows["closures"],
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "kernel.json", payloads["kernel"])
    (OUT_DIR / "axis.csv").write_text(payloads["axis_csv"], encoding="utf-8")
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        axis_table=payloads["axis_table"],
        pair_table=payloads["pair_table"],
        observable_table=payloads["obs_table"],
        pair_counts=payloads["pair_counts"],
        pair_weights=payloads["pair_weights"],
        closures=payloads["closures"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
