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


THEOREM_ID = "long_tri"
STATUS = "LONG_TRI_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
RAW_TENSOR = ROOT / "data" / "raw" / "Halloween.npz"
LONG_KERN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_kern" / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_tri.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_tri.py"

FRONT_COLUMNS = [
    "source_addr",
    "finite_frontier_targets",
    "frontier_min",
    "frontier_max",
    "closure_volume",
    "exact_pair_count",
    "exact_pair_weight",
]
WEAK_COLUMNS = [
    "class_id",
    "class_name",
    "support_count",
    "support_weight",
    "support_square",
    "closure_count",
    "closure_extra",
    "support_indicator_var_num",
    "support_indicator_var_den",
    "closure_indicator_var_num",
    "closure_indicator_var_den",
    "coeff_var_num",
    "coeff_var_den",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "tensor_support_count",
    "tensor_coeff_sum",
    "tensor_coeff_square_sum",
    "domain_word_count",
    "source_pair_support_count",
    "source_pair_empty_count",
    "source_pair_fiber_min",
    "source_pair_fiber_max",
    "frontier_pair_count",
    "frontier_none_count",
    "frontier_min",
    "frontier_max",
    "closure_size",
    "closure_extra",
    "closure_domain_gap",
    "closure_monotone_source0",
    "closure_monotone_source1",
    "closure_target_upward_flag",
    "weak_order_class_count",
    "weak_support_count_sum",
    "weak_support_weight_sum",
    "weak_support_square_sum",
    "weak_closure_count_sum",
    "long_kern_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}
WEAK_CLASSES = [
    "eq_abc",
    "eq_ab_lt_c",
    "eq_ab_gt_c",
    "eq_ac_lt_b",
    "eq_ac_gt_b",
    "eq_bc_lt_a",
    "eq_bc_gt_a",
    "lt_abc",
    "lt_acb",
    "lt_bac",
    "lt_bca",
    "lt_cab",
    "lt_cba",
]
WEAK_CODES = {name: index for index, name in enumerate(WEAK_CLASSES)}


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


def weak_class(a: int, b: int, c: int) -> str:
    if a == b == c:
        return "eq_abc"
    if a == b < c:
        return "eq_ab_lt_c"
    if a == b > c:
        return "eq_ab_gt_c"
    if a == c < b:
        return "eq_ac_lt_b"
    if a == c > b:
        return "eq_ac_gt_b"
    if b == c < a:
        return "eq_bc_lt_a"
    if b == c > a:
        return "eq_bc_gt_a"
    order = sorted(((a, "a"), (b, "b"), (c, "c")))
    return "lt_" + "".join(axis for _, axis in order)


def support_weak_rows(triples: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    counts = np.zeros(len(WEAK_CLASSES), dtype=np.int64)
    weights = np.zeros(len(WEAK_CLASSES), dtype=np.int64)
    squares = np.zeros(len(WEAK_CLASSES), dtype=np.int64)
    for a, b, c, coeff in triples:
        code = WEAK_CODES[weak_class(int(a), int(b), int(c))]
        counts[code] += 1
        weights[code] += int(coeff)
        squares[code] += int(coeff) * int(coeff)
    return counts, weights, squares


def source_pair_profiles(triples: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count = np.zeros((n, n), dtype=np.int32)
    weight = np.zeros((n, n), dtype=np.int64)
    min_output = np.full((n, n), n, dtype=np.int16)
    np.add.at(count, (triples[:, 0], triples[:, 1]), 1)
    np.add.at(weight, (triples[:, 0], triples[:, 1]), triples[:, 3])
    np.minimum.at(min_output, (triples[:, 0], triples[:, 1]), triples[:, 2].astype(np.int16))
    return count, weight, min_output


def frontier_from_min_output(min_output: np.ndarray) -> np.ndarray:
    return np.minimum.accumulate(
        np.minimum.accumulate(min_output[::-1, ::-1], axis=0),
        axis=1,
    )[::-1, ::-1]


def add_range(counts: np.ndarray, label: str, lo: int, hi: int) -> None:
    if hi > lo:
        counts[WEAK_CODES[label]] += hi - lo


def closure_weak_counts(frontier: np.ndarray, n: int) -> np.ndarray:
    counts = np.zeros(len(WEAK_CLASSES), dtype=np.int64)
    for a in range(n):
        for b in range(n):
            m = int(frontier[a, b])
            if m >= n:
                continue
            if a == b:
                add_range(counts, "eq_ab_gt_c", m, min(a, n))
                if m <= a < n:
                    add_range(counts, "eq_abc", a, a + 1)
                add_range(counts, "eq_ab_lt_c", max(m, a + 1), n)
            elif a < b:
                add_range(counts, "lt_cab", m, min(a, n))
                if m <= a < n:
                    add_range(counts, "eq_ac_lt_b", a, a + 1)
                add_range(counts, "lt_acb", max(m, a + 1), min(b, n))
                if m <= b < n:
                    add_range(counts, "eq_bc_gt_a", b, b + 1)
                add_range(counts, "lt_abc", max(m, b + 1), n)
            else:
                add_range(counts, "lt_cba", m, min(b, n))
                if m <= b < n:
                    add_range(counts, "eq_bc_lt_a", b, b + 1)
                add_range(counts, "lt_bca", max(m, b + 1), min(a, n))
                if m <= a < n:
                    add_range(counts, "eq_ac_gt_b", a, a + 1)
                add_range(counts, "lt_bac", max(m, a + 1), n)
    return counts


def build_front_rows(
    frontier: np.ndarray,
    pair_count: np.ndarray,
    pair_weight: np.ndarray,
    n: int,
) -> list[dict[str, int]]:
    finite = frontier < n
    volumes = np.where(finite, n - frontier.astype(np.int64), 0)
    rows: list[dict[str, int]] = []
    for source in range(n):
        finite_row = finite[source]
        front_values = frontier[source, finite_row]
        rows.append(
            {
                "source_addr": source,
                "finite_frontier_targets": int(finite_row.sum()),
                "frontier_min": int(front_values.min()) if front_values.size else n,
                "frontier_max": int(front_values.max()) if front_values.size else n,
                "closure_volume": int(volumes[source].sum()),
                "exact_pair_count": int(np.count_nonzero(pair_count[source])),
                "exact_pair_weight": int(pair_weight[source].sum()),
            }
        )
    return rows


def build_rows() -> dict[str, Any]:
    triples = load_tensor()
    n = line_size(triples)
    pair_count, pair_weight, min_output = source_pair_profiles(triples, n)
    frontier = frontier_from_min_output(min_output)
    finite = frontier < n
    closure_volume = np.where(finite, n - frontier.astype(np.int64), 0)
    support_counts, support_weights, support_squares = support_weak_rows(triples)
    closure_counts = closure_weak_counts(frontier, n)
    domain = n**3
    support_total = int(triples.shape[0])
    coeff_sum = int(triples[:, 3].sum())
    coeff_square_sum = int(np.dot(triples[:, 3], triples[:, 3]))
    weak_rows = []
    for class_id, name in enumerate(WEAK_CLASSES):
        support_count = int(support_counts[class_id])
        support_weight = int(support_weights[class_id])
        support_square = int(support_squares[class_id])
        closure_count = int(closure_counts[class_id])
        weak_rows.append(
            {
                "class_id": class_id,
                "class_name": name,
                "support_count": support_count,
                "support_weight": support_weight,
                "support_square": support_square,
                "closure_count": closure_count,
                "closure_extra": closure_count - support_count,
                "support_indicator_var_num": support_count * (support_total - support_count),
                "support_indicator_var_den": support_total * support_total,
                "closure_indicator_var_num": closure_count * (domain - closure_count),
                "closure_indicator_var_den": domain * domain,
                "coeff_var_num": support_count * support_square - support_weight * support_weight,
                "coeff_var_den": support_count * support_count if support_count else 1,
            }
        )
    long_kern = load_json(LONG_KERN_REPORT)
    pair_nonzero = pair_count[pair_count > 0]
    closure_size = int(closure_volume.sum())
    obs = {
        "line_point_count": n,
        "tensor_support_count": support_total,
        "tensor_coeff_sum": coeff_sum,
        "tensor_coeff_square_sum": coeff_square_sum,
        "domain_word_count": domain,
        "source_pair_support_count": int(np.count_nonzero(pair_count)),
        "source_pair_empty_count": int(pair_count.size - np.count_nonzero(pair_count)),
        "source_pair_fiber_min": int(pair_nonzero.min()),
        "source_pair_fiber_max": int(pair_nonzero.max()),
        "frontier_pair_count": int(finite.sum()),
        "frontier_none_count": int((~finite).sum()),
        "frontier_min": int(frontier[finite].min()),
        "frontier_max": int(frontier[finite].max()),
        "closure_size": closure_size,
        "closure_extra": closure_size - support_total,
        "closure_domain_gap": domain - closure_size,
        "closure_monotone_source0": int(bool(np.all(frontier[1:, :] >= frontier[:-1, :]))),
        "closure_monotone_source1": int(bool(np.all(frontier[:, 1:] >= frontier[:, :-1]))),
        "closure_target_upward_flag": 1,
        "weak_order_class_count": len(WEAK_CLASSES),
        "weak_support_count_sum": int(support_counts.sum()),
        "weak_support_weight_sum": int(support_weights.sum()),
        "weak_support_square_sum": int(support_squares.sum()),
        "weak_closure_count_sum": int(closure_counts.sum()),
        "long_kern_input_certified": int(
            long_kern.get("status") == "LONG_KERN_CERTIFIED"
            and long_kern.get("all_checks_pass") is True
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "triples": triples,
        "pair_count": pair_count,
        "pair_weight": pair_weight,
        "frontier": frontier,
        "front_rows": build_front_rows(frontier, pair_count, pair_weight, n),
        "weak_rows": weak_rows,
        "support_counts": support_counts,
        "support_weights": support_weights,
        "support_squares": support_squares,
        "closure_counts": closure_counts,
        "obs": obs,
        "obs_rows": obs_rows,
        "long_kern": long_kern,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    front_table = table_from_rows(FRONT_COLUMNS, rows["front_rows"])
    weak_numeric_rows = [
        {key: value for key, value in row.items() if key != "class_name"}
        for row in rows["weak_rows"]
    ]
    weak_table = table_from_rows(
        [column for column in WEAK_COLUMNS if column != "class_name"],
        weak_numeric_rows,
    )
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    checks = {
        "long_kern_input_certified": obs["long_kern_input_certified"] == 1,
        "line_size_matches_tensor_addresses": obs["line_point_count"] == 985,
        "raw_tensor_shape": rows["triples"].shape == (1_414_965, 4),
        "raw_tensor_support_unique": len(np.unique((rows["triples"][:, 0] * 985 + rows["triples"][:, 1]) * 985 + rows["triples"][:, 2])) == obs["tensor_support_count"],
        "source_pair_profile_matches_long_kern": (
            obs["source_pair_support_count"],
            obs["source_pair_fiber_min"],
            obs["source_pair_fiber_max"],
        )
        == (198_029, 1, 48),
        "ternary_closure_exact": (
            obs["frontier_pair_count"],
            obs["frontier_none_count"],
            obs["frontier_min"],
            obs["frontier_max"],
            obs["closure_size"],
        )
        == (970_225, 0, 0, 893, 551_559_917),
        "ternary_closure_is_alexandrov": (
            obs["closure_monotone_source0"],
            obs["closure_monotone_source1"],
            obs["closure_target_upward_flag"],
        )
        == (1, 1, 1),
        "weak_classes_partition_support_and_closure": (
            obs["weak_order_class_count"],
            obs["weak_support_count_sum"],
            obs["weak_support_weight_sum"],
            obs["weak_support_square_sum"],
            obs["weak_closure_count_sum"],
        )
        == (
            13,
            obs["tensor_support_count"],
            obs["tensor_coeff_sum"],
            obs["tensor_coeff_square_sum"],
            obs["closure_size"],
        ),
        "table_shapes_match": (
            tuple(front_table.shape),
            tuple(weak_table.shape),
            tuple(obs_table.shape),
            tuple(rows["frontier"].shape),
            tuple(rows["pair_count"].shape),
        )
        == (
            (985, len(FRONT_COLUMNS)),
            (13, len(WEAK_COLUMNS) - 1),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (985, 985),
            (985, 985),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_alexandrov_line_ternary_closure",
        "line": {
            "point_count": obs["line_point_count"],
            "domain_word_count": obs["domain_word_count"],
            "support_count": obs["tensor_support_count"],
        },
        "frontier": {
            "rule": "frontier(i,j)=min c among support triples (a,b,c) with i<=a and j<=b",
            "frontier_pair_count": obs["frontier_pair_count"],
            "frontier_none_count": obs["frontier_none_count"],
            "frontier_min": obs["frontier_min"],
            "frontier_max": obs["frontier_max"],
            "frontier_sha256": sha_array(rows["frontier"]),
        },
        "closure": {
            "rule": "closure contains (i,j,k) iff k>=frontier(i,j)",
            "closure_size": obs["closure_size"],
            "closure_extra": obs["closure_extra"],
            "closure_domain_gap": obs["closure_domain_gap"],
            "source_monotone": [
                bool(obs["closure_monotone_source0"]),
                bool(obs["closure_monotone_source1"]),
            ],
            "target_upward": bool(obs["closure_target_upward_flag"]),
        },
        "weak_order": {
            "class_count": len(WEAK_CLASSES),
            "classes": WEAK_CLASSES,
            "support_counts": rows["support_counts"].astype(int).tolist(),
            "closure_counts": rows["closure_counts"].astype(int).tolist(),
        },
        "finite_lln": {
            "support_class_event": "weak order class of a sampled tensor support row",
            "closure_class_event": "weak order class of a sampled line-domain word restricted to the ternary closure",
            "variance_rule": "for event count m in population N, Var(mean_k)=m*(N-m)/(N^2*k)",
        },
        "source_pair": {
            "support_count": obs["source_pair_support_count"],
            "empty_count": obs["source_pair_empty_count"],
            "fiber_min": obs["source_pair_fiber_min"],
            "fiber_max": obs["source_pair_fiber_max"],
            "pair_count_sha256": sha_array(rows["pair_count"]),
            "pair_weight_sha256": sha_array(rows["pair_weight"]),
        },
        "front_table_sha256": sha_array(front_table),
        "weak_table_sha256": sha_array(weak_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    tri = {
        "schema": "long.tri@1",
        "object": "finite_alexandrov_line_ternary_closure",
        "status": STATUS if all(checks.values()) else "LONG_TRI_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.tri.report@1",
        "status": tri["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_tri certifies the full ternary Alexandrov closure of the "
            "C985 tensor lookup over the finite line, plus weak-order support "
            "classes and exact finite LLN event variances."
        ),
        "stage_protocol": {
            "draft": "reuse long_kern and the raw tensor lookup",
            "witness": "compute source-pair frontiers, ternary closure, and weak-order classes",
            "coherence": "check closure monotonicity, exact volumes, partitions, and source-pair fibers",
            "closure": "derive finite LLN event variances for support and closure classes",
            "emit": "write long_tri artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "long_kern_report": input_entry(
                LONG_KERN_REPORT,
                {"status": rows["long_kern"].get("status")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "tri": relpath(OUT_DIR / "tri.json"),
            "front_csv": relpath(OUT_DIR / "front.csv"),
            "weak_csv": relpath(OUT_DIR / "weak.csv"),
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
                "the exact ternary Alexandrov closure volume of the raw tensor support",
                "the source-pair frontier matrix that determines that closure",
                "the 13 weak-order support classes induced by the finite line",
                "finite LLN event-variance numerators for support and closure weak-order classes",
            ],
            "does_not_certify_because_out_of_scope": [
                "all non-weak-order support classes",
                "recoupling dynamics not visible in the raw tensor lookup support",
                "a minimal generating basis for every possible ternary line profunctor",
                "a semantic infinite limit theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_basis: minimal generators/irreducibles for the line "
            "profunctor closure lattice seen by the tensor lookup."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.tri.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.tri.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "tri": tri,
        "front_csv": csv_text(FRONT_COLUMNS, rows["front_rows"]),
        "weak_csv": csv_text(WEAK_COLUMNS, rows["weak_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "front_table": front_table,
        "weak_table": weak_table,
        "obs_table": obs_table,
        "frontier": rows["frontier"],
        "pair_count": rows["pair_count"],
        "pair_weight": rows["pair_weight"],
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
    write_json(OUT_DIR / "tri.json", payloads["tri"])
    (OUT_DIR / "front.csv").write_text(payloads["front_csv"], encoding="utf-8")
    (OUT_DIR / "weak.csv").write_text(payloads["weak_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        front_table=payloads["front_table"],
        weak_table=payloads["weak_table"],
        observable_table=payloads["obs_table"],
        frontier=payloads["frontier"],
        pair_count=payloads["pair_count"],
        pair_weight=payloads["pair_weight"],
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
