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
    from .derive_long_kern import PAIR_AXES, pair_matrix, monotone_closure
    from .derive_long_tri import (
        WEAK_CLASSES,
        WEAK_CODES,
        frontier_from_min_output,
        line_size,
        load_tensor,
        source_pair_profiles,
        weak_class,
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
    from derive_long_kern import PAIR_AXES, pair_matrix, monotone_closure
    from derive_long_tri import (
        WEAK_CLASSES,
        WEAK_CODES,
        frontier_from_min_output,
        line_size,
        load_tensor,
        source_pair_profiles,
        weak_class,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_basis"
STATUS = "LONG_BASIS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
RAW_TENSOR = ROOT / "data" / "raw" / "Halloween.npz"
LONG_KERN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_kern" / "report.json"
LONG_TRI_REPORT = D20_INVARIANTS / "proof_obligations" / "long_tri" / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_basis.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_basis.py"

TRI_BASIS_COLUMNS = [
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "weak_class_code",
    "source_pair_id",
    "closure_volume",
    "source0_margin",
    "source1_margin",
]
PAIR_BASIS_COLUMNS = [
    "pair",
    "source_axis",
    "target_axis",
    "basis_id",
    "source_addr",
    "target_addr",
    "fiber_count",
    "fiber_weight",
    "closure_area",
    "next_source_gap",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "tensor_support_count",
    "tensor_coeff_sum",
    "tensor_coeff_square_sum",
    "domain_word_count",
    "tri_basis_count",
    "tri_basis_weight_sum",
    "tri_basis_square_sum",
    "tri_basis_source0_min",
    "tri_basis_source0_max",
    "tri_basis_source1_min",
    "tri_basis_source1_max",
    "tri_basis_target_min",
    "tri_basis_target_max",
    "tri_basis_output_support_count",
    "tri_basis_output_max_multiplicity",
    "tri_basis_regenerates_frontier",
    "tri_basis_irredundant_flag",
    "tri_frontier_pair_count",
    "tri_frontier_min",
    "tri_frontier_max",
    "tri_closure_size",
    "pair_basis_total",
    "pair_basis_01_count",
    "pair_basis_02_count",
    "pair_basis_12_count",
    "pair_basis_regenerates_pair_closures",
    "pair_basis_irredundant_flag",
    "long_tri_input_certified",
    "long_kern_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def closure_size(frontier: np.ndarray, n: int) -> int:
    finite = frontier < n
    return int(np.where(finite, n - frontier.astype(np.int64), 0).sum())


def frontier_from_basis(tri_basis: np.ndarray, n: int) -> np.ndarray:
    min_output = np.full((n, n), n, dtype=np.int16)
    np.minimum.at(
        min_output,
        (tri_basis[:, 0], tri_basis[:, 1]),
        tri_basis[:, 2].astype(np.int16),
    )
    return frontier_from_min_output(min_output)


def tri_basis_rows(
    triples: np.ndarray,
    min_output: np.ndarray,
    frontier: np.ndarray,
    n: int,
) -> tuple[list[dict[str, int]], np.ndarray]:
    next0 = np.full((n, n), n, dtype=np.int16)
    next1 = np.full((n, n), n, dtype=np.int16)
    next0[:-1, :] = frontier[1:, :]
    next1[:, :-1] = frontier[:, 1:]
    basis_pair = min_output < np.minimum(next0, next1)
    basis_mask = (
        triples[:, 2].astype(np.int16) == min_output[triples[:, 0], triples[:, 1]]
    ) & basis_pair[triples[:, 0], triples[:, 1]]
    basis = triples[basis_mask]
    order = np.lexsort((basis[:, 2], basis[:, 1], basis[:, 0]))
    basis = basis[order]
    rows: list[dict[str, int]] = []
    for basis_id, (a_raw, b_raw, c_raw, coeff_raw) in enumerate(basis):
        a = int(a_raw)
        b = int(b_raw)
        c = int(c_raw)
        coeff = int(coeff_raw)
        source0_next = int(frontier[a + 1, b]) if a + 1 < n else n
        source1_next = int(frontier[a, b + 1]) if b + 1 < n else n
        rows.append(
            {
                "basis_id": basis_id,
                "source0_addr": a,
                "source1_addr": b,
                "target_addr": c,
                "coeff": coeff,
                "weak_class_code": WEAK_CODES[weak_class(a, b, c)],
                "source_pair_id": a * n + b,
                "closure_volume": (a + 1) * (b + 1) * (n - c),
                "source0_margin": source0_next - c,
                "source1_margin": source1_next - c,
            }
        )
    return rows, basis


def pair_closure_from_basis(rows: list[dict[str, int]], n: int) -> np.ndarray:
    diff = np.zeros((n + 1, n + 1), dtype=np.int32)
    if rows:
        sources = np.asarray([row["source_addr"] for row in rows], dtype=np.int64)
        targets = np.asarray([row["target_addr"] for row in rows], dtype=np.int64)
        np.add.at(diff, (np.zeros_like(sources), targets), 1)
        np.add.at(diff, (sources + 1, targets), -1)
        np.add.at(diff, (np.zeros_like(sources), np.full_like(targets, n)), -1)
        np.add.at(diff, (sources + 1, np.full_like(targets, n)), 1)
    return diff.cumsum(axis=0).cumsum(axis=1)[:n, :n] > 0


def pair_basis_rows_for_projection(
    triples: np.ndarray,
    n: int,
    pair_code: int,
    source_axis: int,
    target_axis: int,
) -> tuple[list[dict[str, int]], np.ndarray, np.ndarray]:
    count, weight = pair_matrix(triples, n, source_axis, target_axis)
    support = count > 0
    rows, cols = np.nonzero(support)
    row_min = np.full(n, n, dtype=np.int16)
    np.minimum.at(row_min, rows, cols.astype(np.int16))
    suffix_min = np.minimum.accumulate(row_min[::-1])[::-1]
    basis_rows: list[dict[str, int]] = []
    for source, target in zip(rows.tolist(), cols.tolist()):
        next_min = int(suffix_min[source + 1]) if source + 1 < n else n
        if target != int(row_min[source]) or target >= next_min:
            continue
        basis_rows.append(
            {
                "pair": pair_code,
                "source_axis": source_axis,
                "target_axis": target_axis,
                "basis_id": len(basis_rows),
                "source_addr": int(source),
                "target_addr": int(target),
                "fiber_count": int(count[source, target]),
                "fiber_weight": int(weight[source, target]),
                "closure_area": (int(source) + 1) * (n - int(target)),
                "next_source_gap": next_min - int(target),
            }
        )
    return basis_rows, monotone_closure(support), pair_closure_from_basis(basis_rows, n)


def pair_basis_rows(
    triples: np.ndarray,
    n: int,
) -> tuple[list[dict[str, int]], np.ndarray, np.ndarray]:
    all_rows: list[dict[str, int]] = []
    full_closures = np.zeros((len(PAIR_AXES), n, n), dtype=np.bool_)
    basis_closures = np.zeros((len(PAIR_AXES), n, n), dtype=np.bool_)
    for pair_code, (source_axis, target_axis) in enumerate(PAIR_AXES):
        rows, full_closure, basis_closure = pair_basis_rows_for_projection(
            triples,
            n,
            pair_code,
            source_axis,
            target_axis,
        )
        all_rows.extend(rows)
        full_closures[pair_code] = full_closure
        basis_closures[pair_code] = basis_closure
    return all_rows, full_closures, basis_closures


def build_rows() -> dict[str, Any]:
    triples = load_tensor()
    n = line_size(triples)
    pair_count, pair_weight, min_output = source_pair_profiles(triples, n)
    frontier = frontier_from_min_output(min_output)
    tri_rows, tri_basis = tri_basis_rows(triples, min_output, frontier, n)
    basis_frontier = frontier_from_basis(tri_basis, n)
    pair_rows, full_pair_closures, basis_pair_closures = pair_basis_rows(triples, n)
    long_tri = load_json(LONG_TRI_REPORT)
    long_kern = load_json(LONG_KERN_REPORT)
    tri_table = table_from_rows(TRI_BASIS_COLUMNS, tri_rows)
    pair_table = table_from_rows(PAIR_BASIS_COLUMNS, pair_rows)
    output_counts = np.bincount(tri_basis[:, 2].astype(np.int64), minlength=n)
    pair_count_by_code = np.bincount(
        np.asarray([row["pair"] for row in pair_rows], dtype=np.int64),
        minlength=len(PAIR_AXES),
    )
    finite = frontier < n
    obs = {
        "line_point_count": n,
        "tensor_support_count": int(triples.shape[0]),
        "tensor_coeff_sum": int(triples[:, 3].sum()),
        "tensor_coeff_square_sum": int(np.dot(triples[:, 3], triples[:, 3])),
        "domain_word_count": n**3,
        "tri_basis_count": int(tri_basis.shape[0]),
        "tri_basis_weight_sum": int(tri_basis[:, 3].sum()),
        "tri_basis_square_sum": int(np.dot(tri_basis[:, 3], tri_basis[:, 3])),
        "tri_basis_source0_min": int(tri_basis[:, 0].min()),
        "tri_basis_source0_max": int(tri_basis[:, 0].max()),
        "tri_basis_source1_min": int(tri_basis[:, 1].min()),
        "tri_basis_source1_max": int(tri_basis[:, 1].max()),
        "tri_basis_target_min": int(tri_basis[:, 2].min()),
        "tri_basis_target_max": int(tri_basis[:, 2].max()),
        "tri_basis_output_support_count": int(np.count_nonzero(output_counts)),
        "tri_basis_output_max_multiplicity": int(output_counts.max()),
        "tri_basis_regenerates_frontier": int(np.array_equal(frontier, basis_frontier)),
        "tri_basis_irredundant_flag": int(
            all(row["source0_margin"] > 0 and row["source1_margin"] > 0 for row in tri_rows)
        ),
        "tri_frontier_pair_count": int(finite.sum()),
        "tri_frontier_min": int(frontier[finite].min()),
        "tri_frontier_max": int(frontier[finite].max()),
        "tri_closure_size": closure_size(frontier, n),
        "pair_basis_total": int(len(pair_rows)),
        "pair_basis_01_count": int(pair_count_by_code[0]),
        "pair_basis_02_count": int(pair_count_by_code[1]),
        "pair_basis_12_count": int(pair_count_by_code[2]),
        "pair_basis_regenerates_pair_closures": int(
            np.array_equal(full_pair_closures, basis_pair_closures)
        ),
        "pair_basis_irredundant_flag": int(
            all(row["next_source_gap"] > 0 for row in pair_rows)
        ),
        "long_tri_input_certified": int(
            long_tri.get("status") == "LONG_TRI_CERTIFIED"
            and long_tri.get("all_checks_pass") is True
        ),
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
        "tri_basis": tri_basis,
        "tri_rows": tri_rows,
        "pair_rows": pair_rows,
        "tri_table": tri_table,
        "pair_table": pair_table,
        "basis_frontier": basis_frontier,
        "full_pair_closures": full_pair_closures,
        "basis_pair_closures": basis_pair_closures,
        "output_counts": output_counts,
        "obs": obs,
        "obs_rows": obs_rows,
        "long_tri": long_tri,
        "long_kern": long_kern,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    tri_weak_counts = np.bincount(
        rows["tri_table"][:, TRI_BASIS_COLUMNS.index("weak_class_code")],
        minlength=len(WEAK_CLASSES),
    )
    checks = {
        "long_tri_input_certified": obs["long_tri_input_certified"] == 1,
        "long_kern_input_certified": obs["long_kern_input_certified"] == 1,
        "line_size_matches_tensor_addresses": obs["line_point_count"] == 985,
        "raw_tensor_shape": rows["triples"].shape == (1_414_965, 4),
        "tri_basis_is_irredundant": obs["tri_basis_irredundant_flag"] == 1,
        "tri_basis_regenerates_full_frontier": obs["tri_basis_regenerates_frontier"] == 1,
        "tri_basis_exact_fingerprint": (
            obs["tri_basis_count"],
            obs["tri_basis_weight_sum"],
            obs["tri_basis_square_sum"],
            obs["tri_basis_source0_min"],
            obs["tri_basis_source0_max"],
            obs["tri_basis_source1_min"],
            obs["tri_basis_source1_max"],
            obs["tri_basis_target_min"],
            obs["tri_basis_target_max"],
            obs["tri_basis_output_support_count"],
            obs["tri_basis_output_max_multiplicity"],
        )
        == (259, 596, 5366, 118, 984, 714, 984, 0, 893, 164, 5),
        "tri_closure_matches_long_tri": (
            obs["tri_frontier_pair_count"],
            obs["tri_frontier_min"],
            obs["tri_frontier_max"],
            obs["tri_closure_size"],
        )
        == (970_225, 0, 893, 551_559_917),
        "pair_basis_is_irredundant": obs["pair_basis_irredundant_flag"] == 1,
        "pair_basis_regenerates_pair_closures": (
            obs["pair_basis_regenerates_pair_closures"],
            obs["pair_basis_total"],
            obs["pair_basis_01_count"],
            obs["pair_basis_02_count"],
            obs["pair_basis_12_count"],
        )
        == (1, 18, 6, 6, 6),
        "table_shapes_match": (
            tuple(rows["tri_table"].shape),
            tuple(rows["pair_table"].shape),
            tuple(obs_table.shape),
            tuple(rows["basis_frontier"].shape),
            tuple(rows["basis_pair_closures"].shape),
        )
        == (
            (259, len(TRI_BASIS_COLUMNS)),
            (18, len(PAIR_BASIS_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (985, 985),
            (3, 985, 985),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_alexandrov_line_closure_basis",
        "line": {
            "point_count": obs["line_point_count"],
            "domain_word_count": obs["domain_word_count"],
            "tensor_support_count": obs["tensor_support_count"],
        },
        "ternary_basis": {
            "rule": "keep support triples not dominated by any larger source pair with an equal-or-lower target",
            "basis_count": obs["tri_basis_count"],
            "basis_weight_sum": obs["tri_basis_weight_sum"],
            "basis_square_sum": obs["tri_basis_square_sum"],
            "source0_range": [obs["tri_basis_source0_min"], obs["tri_basis_source0_max"]],
            "source1_range": [obs["tri_basis_source1_min"], obs["tri_basis_source1_max"]],
            "target_range": [obs["tri_basis_target_min"], obs["tri_basis_target_max"]],
            "output_support_count": obs["tri_basis_output_support_count"],
            "output_max_multiplicity": obs["tri_basis_output_max_multiplicity"],
            "weak_classes": WEAK_CLASSES,
            "weak_class_counts": tri_weak_counts.astype(int).tolist(),
            "regenerates_frontier": bool(obs["tri_basis_regenerates_frontier"]),
            "irredundant": bool(obs["tri_basis_irredundant_flag"]),
            "tri_basis_table_sha256": sha_array(rows["tri_table"]),
            "basis_frontier_sha256": sha_array(rows["basis_frontier"]),
        },
        "pair_basis": {
            "rule": "keep observed pair points not dominated by a higher source with a lower-or-equal target",
            "basis_total": obs["pair_basis_total"],
            "basis_counts": [
                obs["pair_basis_01_count"],
                obs["pair_basis_02_count"],
                obs["pair_basis_12_count"],
            ],
            "regenerates_pair_closures": bool(obs["pair_basis_regenerates_pair_closures"]),
            "irredundant": bool(obs["pair_basis_irredundant_flag"]),
            "pair_basis_table_sha256": sha_array(rows["pair_table"]),
            "basis_pair_closures_sha256": sha_array(rows["basis_pair_closures"]),
        },
        "closure": {
            "frontier_pair_count": obs["tri_frontier_pair_count"],
            "frontier_min": obs["tri_frontier_min"],
            "frontier_max": obs["tri_frontier_max"],
            "closure_size": obs["tri_closure_size"],
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    basis = {
        "schema": "long.basis@1",
        "object": "finite_alexandrov_line_closure_basis",
        "status": STATUS if all(checks.values()) else "LONG_BASIS_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.basis.report@1",
        "status": basis["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_basis certifies that the tensor lookup's pair and ternary "
            "Alexandrov closures are generated by small irredundant support "
            "antichains: 18 pair generators and 259 ternary generators."
        ),
        "stage_protocol": {
            "draft": "reuse long_kern, long_tri, and the raw tensor lookup",
            "witness": "extract nondominated pair and ternary support generators",
            "coherence": "regenerate pair closures and the ternary frontier from the basis",
            "closure": "check irredundancy, exact fingerprints, and closure volumes",
            "emit": "write long_basis artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "long_kern_report": input_entry(
                LONG_KERN_REPORT,
                {"status": rows["long_kern"].get("status")},
            ),
            "long_tri_report": input_entry(
                LONG_TRI_REPORT,
                {"status": rows["long_tri"].get("status")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "basis": relpath(OUT_DIR / "basis.json"),
            "tri_basis_csv": relpath(OUT_DIR / "tri_basis.csv"),
            "pair_basis_csv": relpath(OUT_DIR / "pair_basis.csv"),
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
                "the minimal nondominated ternary support antichain that regenerates the long_tri frontier",
                "the minimal nondominated pair support antichains that regenerate the long_kern pair closures",
                "exact generator fingerprints for count, weights, address ranges, and output multiplicities",
                "that the huge closure can be read from the finite basis rather than enumerated as raw bulk",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic recoupling moves beyond the raw tensor lookup order",
                "a basis for all possible monotone profunctors on the 985-point line",
                "an infinite or asymptotic LLN theorem",
                "C985 associator closure data not present in the tensor lookup support",
            ],
        },
        "next_highest_yield_item": (
            "Build long_rec: recoupling/transition kernels on the long_basis "
            "antichain, then test which basis moves preserve eta6."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.basis.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.basis.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "basis": basis,
        "tri_basis_csv": csv_text(TRI_BASIS_COLUMNS, rows["tri_rows"]),
        "pair_basis_csv": csv_text(PAIR_BASIS_COLUMNS, rows["pair_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tri_basis_table": rows["tri_table"],
        "pair_basis_table": rows["pair_table"],
        "obs_table": obs_table,
        "basis_frontier": rows["basis_frontier"],
        "basis_pair_closures": rows["basis_pair_closures"],
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
    write_json(OUT_DIR / "basis.json", payloads["basis"])
    (OUT_DIR / "tri_basis.csv").write_text(payloads["tri_basis_csv"], encoding="utf-8")
    (OUT_DIR / "pair_basis.csv").write_text(payloads["pair_basis_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tri_basis_table=payloads["tri_basis_table"],
        pair_basis_table=payloads["pair_basis_table"],
        observable_table=payloads["obs_table"],
        basis_frontier=payloads["basis_frontier"],
        basis_pair_closures=payloads["basis_pair_closures"],
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
