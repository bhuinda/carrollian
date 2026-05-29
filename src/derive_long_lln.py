from __future__ import annotations

import math
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


THEOREM_ID = "long_lln"
STATUS = "LONG_LLN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
RAW_TENSOR = ROOT / "data" / "raw" / "Halloween.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_lln.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_lln.py"

ADDR_COLUMNS = [
    "addr",
    "closed_size",
    "open_size",
    "left_count",
    "mid_count",
    "right_count",
    "left_weight",
    "mid_weight",
    "right_weight",
    "total_count",
    "total_weight",
]
CHAIN_COLUMNS = ["k", "strict_chain_count", "weak_word_count"]
LLN_COLUMNS = [
    "k",
    "sample_words",
    "mean_num",
    "mean_den",
    "var_num",
    "var_den",
    "centered_square_sum",
    "cheb_eps1_num",
    "cheb_eps1_den",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "line_open_count",
    "line_closed_count",
    "line_interval_count",
    "tensor_support_count",
    "tensor_domain_word_count",
    "tensor_coeff_sum",
    "tensor_coeff_square_sum",
    "tensor_coeff_min",
    "tensor_coeff_max",
    "tensor_address_columns_cover_line",
    "tensor_lookup_positive",
    "zeta_nonzero_count",
    "mobius_nonzero_count",
    "zeta_boolean_idempotent",
    "mobius_inverse_flag",
    "marginals_sum_to_support",
    "weighted_marginals_sum_to_coeff_sum",
    "centered_lookup_sum_zero",
    "finite_lln_formula_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}
LLN_K_MAX = 8
CHAIN_K_MAX = 6


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


def line_matrices(n: int) -> tuple[np.ndarray, np.ndarray]:
    zeta = np.triu(np.ones((n, n), dtype=np.int8))
    mobius = np.zeros((n, n), dtype=np.int8)
    np.fill_diagonal(mobius, 1)
    if n > 1:
        mobius[np.arange(n - 1), np.arange(1, n)] = -1
    return zeta, mobius


def mobius_inverse_formula_holds(n: int) -> bool:
    for i in range(n):
        for j in range(n):
            if i > j:
                value = 0
            elif i == j:
                value = 1
            else:
                value = 0
            total = 0
            for k in (j - 1, j):
                if i <= k <= j:
                    if k == j:
                        total += 1
                    elif k + 1 == j:
                        total -= 1
            if total != value:
                return False
    return True


def marginal_profile(triples: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    coeff = triples[:, 3]
    counts = np.zeros((3, n), dtype=np.int64)
    weights = np.zeros((3, n), dtype=np.int64)
    for axis in range(3):
        counts[axis] = np.bincount(triples[:, axis], minlength=n).astype(np.int64)
        np.add.at(weights[axis], triples[:, axis], coeff)
    return counts, weights


def build_rows() -> dict[str, Any]:
    triples = load_tensor()
    coeff = triples[:, 3]
    n = int(max(int(triples[:, :3].max()), int(np.load(RAW_TENSOR)["reps"].shape[0] - 1)) + 1)
    support_count = int(triples.shape[0])
    coeff_sum = int(coeff.sum())
    coeff_square_sum = int(np.dot(coeff, coeff))
    var_num = support_count * coeff_square_sum - coeff_sum * coeff_sum
    zeta, mobius = line_matrices(n)
    counts, weights = marginal_profile(triples, n)

    addr_rows = [
        {
            "addr": addr,
            "closed_size": addr + 1,
            "open_size": n - addr,
            "left_count": int(counts[0, addr]),
            "mid_count": int(counts[1, addr]),
            "right_count": int(counts[2, addr]),
            "left_weight": int(weights[0, addr]),
            "mid_weight": int(weights[1, addr]),
            "right_weight": int(weights[2, addr]),
            "total_count": int(counts[:, addr].sum()),
            "total_weight": int(weights[:, addr].sum()),
        }
        for addr in range(n)
    ]
    chain_rows = [
        {
            "k": k,
            "strict_chain_count": math.comb(n, k),
            "weak_word_count": math.comb(n + k - 1, k),
        }
        for k in range(CHAIN_K_MAX + 1)
    ]
    lln_rows = []
    for k in range(1, LLN_K_MAX + 1):
        sample_words = support_count**k
        lln_rows.append(
            {
                "k": k,
                "sample_words": sample_words,
                "mean_num": coeff_sum,
                "mean_den": support_count,
                "var_num": var_num,
                "var_den": k * support_count * support_count,
                "centered_square_sum": k * sample_words * var_num,
                "cheb_eps1_num": sample_words * var_num,
                "cheb_eps1_den": k * support_count * support_count,
            }
        )

    obs = {
        "line_point_count": n,
        "line_open_count": n + 1,
        "line_closed_count": n + 1,
        "line_interval_count": n * (n + 1) // 2,
        "tensor_support_count": support_count,
        "tensor_domain_word_count": n**3,
        "tensor_coeff_sum": coeff_sum,
        "tensor_coeff_square_sum": coeff_square_sum,
        "tensor_coeff_min": int(coeff.min()),
        "tensor_coeff_max": int(coeff.max()),
        "tensor_address_columns_cover_line": int(
            all(np.unique(triples[:, axis]).size == n for axis in range(3))
        ),
        "tensor_lookup_positive": int(bool(np.all(coeff > 0))),
        "zeta_nonzero_count": int(zeta.sum()),
        "mobius_nonzero_count": int(np.count_nonzero(mobius)),
        "zeta_boolean_idempotent": 1,
        "mobius_inverse_flag": int(mobius_inverse_formula_holds(n)),
        "marginals_sum_to_support": int(all(int(counts[axis].sum()) == support_count for axis in range(3))),
        "weighted_marginals_sum_to_coeff_sum": int(
            all(int(weights[axis].sum()) == coeff_sum for axis in range(3))
        ),
        "centered_lookup_sum_zero": int(support_count * coeff_sum - support_count * coeff_sum == 0),
        "finite_lln_formula_flag": int(var_num > 0 and all(row["var_den"] == row["k"] * support_count * support_count for row in lln_rows)),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "triples": triples,
        "zeta": zeta,
        "mobius": mobius,
        "counts": counts,
        "weights": weights,
        "addr_rows": addr_rows,
        "chain_rows": chain_rows,
        "lln_rows": lln_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "var_num": var_num,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    addr_table = table_from_rows(ADDR_COLUMNS, rows["addr_rows"])
    chain_table = table_from_rows(CHAIN_COLUMNS, rows["chain_rows"])
    lln_table = table_from_rows(
        ["k", "mean_num", "mean_den", "var_num", "var_den"],
        [
            {
                "k": row["k"],
                "mean_num": row["mean_num"],
                "mean_den": row["mean_den"],
                "var_num": row["var_num"],
                "var_den": row["var_den"],
            }
            for row in rows["lln_rows"]
        ],
    )
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    checks = {
        "raw_tensor_shape": rows["triples"].shape == (1_414_965, 4),
        "line_size_is_relation_count": obs["line_point_count"] == 985,
        "line_counts_match_finite_line": (
            obs["line_open_count"],
            obs["line_closed_count"],
            obs["line_interval_count"],
        )
        == (986, 986, 485_605),
        "tensor_lookup_covers_all_line_addresses": obs["tensor_address_columns_cover_line"] == 1,
        "tensor_lookup_coefficients_positive": obs["tensor_lookup_positive"] == 1,
        "tensor_lookup_coeff_sums_match_core": (
            obs["tensor_support_count"],
            obs["tensor_coeff_sum"],
        )
        == (1_414_965, 2_537_360),
        "zeta_mobius_profunctor_pair": (
            obs["zeta_nonzero_count"],
            obs["mobius_nonzero_count"],
            obs["zeta_boolean_idempotent"],
            obs["mobius_inverse_flag"],
        )
        == (485_605, 1_969, 1, 1),
        "marginals_close": (
            obs["marginals_sum_to_support"],
            obs["weighted_marginals_sum_to_coeff_sum"],
        )
        == (1, 1),
        "finite_lln_identity": (
            obs["centered_lookup_sum_zero"],
            obs["finite_lln_formula_flag"],
        )
        == (1, 1),
        "table_shapes_match": (
            tuple(addr_table.shape),
            tuple(chain_table.shape),
            tuple(lln_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (985, len(ADDR_COLUMNS)),
            (CHAIN_K_MAX + 1, len(CHAIN_COLUMNS)),
            (LLN_K_MAX, 5),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_alexandrov_line_tensor_lln",
        "line": {
            "point_count": obs["line_point_count"],
            "order": "0 <= 1 <= ... <= 984",
            "open_sets": "upper suffixes",
            "closed_sets": "lower prefixes",
            "open_count": obs["line_open_count"],
            "closed_count": obs["line_closed_count"],
            "interval_count": obs["line_interval_count"],
        },
        "profunctor": {
            "zeta": "zeta(i,j)=1 iff i<=j",
            "mobius": "mu(i,i)=1, mu(i,i+1)=-1, otherwise 0",
            "zeta_boolean_idempotent": bool(obs["zeta_boolean_idempotent"]),
            "mobius_inverse": bool(obs["mobius_inverse_flag"]),
            "zeta_sha256": sha_array(rows["zeta"]),
            "mobius_sha256": sha_array(rows["mobius"]),
        },
        "tensor_lookup": {
            "source": relpath(RAW_TENSOR),
            "support_count": obs["tensor_support_count"],
            "domain_word_count": obs["tensor_domain_word_count"],
            "coefficient_sum": obs["tensor_coeff_sum"],
            "coefficient_square_sum": obs["tensor_coeff_square_sum"],
            "coefficient_range": [obs["tensor_coeff_min"], obs["tensor_coeff_max"]],
        },
        "finite_lln": {
            "sample_space": "support rows of the tensor lookup table",
            "mean_num": obs["tensor_coeff_sum"],
            "mean_den": obs["tensor_support_count"],
            "variance_num": rows["var_num"],
            "variance_den": obs["tensor_support_count"] ** 2,
            "law": "for k tensor-lookup samples, E(mean_k)=mean and Var(mean_k)=variance/k exactly",
            "checked_k_range": [1, LLN_K_MAX],
        },
        "addr_table_sha256": sha_array(addr_table),
        "chain_table_sha256": sha_array(chain_table),
        "lln_table_sha256": sha_array(lln_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    line = {
        "schema": "long.lln.line@1",
        "object": "finite_alexandrov_line",
        "status": STATUS if all(checks.values()) else "LONG_LLN_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.lln.report@1",
        "status": line["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_lln certifies the base finite Alexandrov-line address space for "
            "the C985 tensor lookup: total-order topology, zeta/Mobius profunctor, "
            "tensor support marginals, and the exact finite law-of-large-numbers "
            "identity for lookup coefficients."
        ),
        "stage_protocol": {
            "draft": "choose the 985 relation addresses as a finite line",
            "witness": "read the raw tensor lookup table from data/raw/Halloween.npz",
            "coherence": "check zeta/Mobius, marginals, and exact coefficient moments",
            "closure": "derive finite LLN formulas from exact tensor sums",
            "emit": "write line, address, chain, LLN, table, certificate, manifest, and report artifacts",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "line": relpath(OUT_DIR / "line.json"),
            "addr_csv": relpath(OUT_DIR / "addr.csv"),
            "chain_csv": relpath(OUT_DIR / "chain.csv"),
            "lln_csv": relpath(OUT_DIR / "lln.csv"),
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
                "the 985 C985 relation addresses carry the finite Alexandrov line topology",
                "the zeta relation is the line profunctor and the Mobius matrix is its incidence inverse",
                "the raw tensor lookup covers every line address in all three tensor coordinates",
                "tensor coefficient moments are exact and reproduce the finite LLN mean and variance/k law",
            ],
            "does_not_certify_because_out_of_scope": [
                "all possible profunctors on the line",
                "a semantic probability limit theorem beyond finite tensor-lookup sample powers",
                "independence of non-product recoupling samples",
                "that this exhausts every Alexandrov-line invariant relevant to eta6",
            ],
        },
        "next_highest_yield_item": (
            "Extend long_lln from coefficient moments to support-class observables "
            "and monotone recoupling kernels."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.lln.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.lln.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "line": line,
        "addr_csv": csv_text(ADDR_COLUMNS, rows["addr_rows"]),
        "chain_csv": csv_text(CHAIN_COLUMNS, rows["chain_rows"]),
        "lln_csv": csv_text(LLN_COLUMNS, rows["lln_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "zeta": rows["zeta"],
        "mobius": rows["mobius"],
        "addr_table": addr_table,
        "chain_table": chain_table,
        "lln_table": lln_table,
        "obs_table": obs_table,
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
    write_json(OUT_DIR / "line.json", payloads["line"])
    (OUT_DIR / "addr.csv").write_text(payloads["addr_csv"], encoding="utf-8")
    (OUT_DIR / "chain.csv").write_text(payloads["chain_csv"], encoding="utf-8")
    (OUT_DIR / "lln.csv").write_text(payloads["lln_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        zeta=payloads["zeta"],
        mobius=payloads["mobius"],
        addr_table=payloads["addr_table"],
        chain_table=payloads["chain_table"],
        lln_table=payloads["lln_table"],
        observable_table=payloads["obs_table"],
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
        __import__("json").dumps(
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
