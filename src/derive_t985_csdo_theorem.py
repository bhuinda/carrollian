from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, ROOT


DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / "t985_csdo"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"
CERTIFICATE_JSON = ROOT / "certificate.json"
LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def array_digest(a: np.ndarray) -> str:
    c = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(c.dtype).encode())
    h.update(str(c.shape).encode())
    h.update(c.tobytes())
    return h.hexdigest()


def array_bytes_digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_certificate_core() -> dict[str, Any]:
    with CERTIFICATE_JSON.open("r", encoding="utf-8") as f:
        cert = json.load(f)
    return cert["d20_invariants"]["core"]


def aggregate_tensor(triples: np.ndarray, qmap: np.ndarray, classes: int) -> np.ndarray:
    out = np.zeros((classes, classes, classes), dtype=np.int64)
    np.add.at(out, (qmap[triples[:, 0]], qmap[triples[:, 1]], qmap[triples[:, 2]]), triples[:, 3])
    return out


def derive_a42_to_a12(q42: np.ndarray, q12: np.ndarray) -> tuple[list[int | None], bool]:
    result: list[int | None] = []
    ok = True
    for cls in range(42):
        vals = np.unique(q12[q42 == cls])
        if vals.size != 1:
            result.append(None)
            ok = False
        else:
            result.append(int(vals[0]))
    return result, ok


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    core = load_certificate_core()
    expected_a985 = core["A985"]
    expected_a42 = core["Pin(d20)=A42"]
    expected_a12 = core["CY(d20)=A12"]

    tensor = np.load(TENSOR_NPZ)
    quotients = np.load(QUOTIENTS_NPZ)

    triples = np.asarray(tensor["triples"], dtype=np.int64)
    triples_stored = np.asarray(tensor["triples"])
    q42 = np.asarray(quotients["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotients["q12_map"], dtype=np.int64)
    block_i = np.asarray(quotients["block_i"], dtype=np.int64)
    block_j = np.asarray(quotients["block_j"], dtype=np.int64)
    q42_tensor_stored = np.asarray(quotients["q42_tensor"], dtype=np.int64)
    q12_tensor_stored = np.asarray(quotients["q12_tensor"], dtype=np.int64)

    q42_tensor = aggregate_tensor(triples, q42, 42)
    q12_tensor = aggregate_tensor(triples, q12, 12)
    a42_to_a12, a42_to_a12_consistent = derive_a42_to_a12(q42, q12)

    relation_matrix = np.zeros((6, 6), dtype=np.int64)
    np.add.at(relation_matrix, (block_i, block_j), 1)
    coefficient_matrix = np.zeros((6, 6), dtype=np.int64)
    np.add.at(coefficient_matrix, (block_i[triples[:, 0]], block_j[triples[:, 2]]), triples[:, 3])

    checks = {
        "triples_shape": list(triples.shape),
        "triples_shape_matches_certificate": list(triples.shape) == expected_a985["tensor_triples_shape"],
        "triples_coefficient_total": int(triples[:, 3].sum()),
        "triples_coefficient_total_matches_certificate": int(triples[:, 3].sum()) == expected_a985["tensor_coefficient_total"],
        "triples_canonical_sha256": array_digest(triples),
        "triples_canonical_sha256_matches_certificate": array_digest(triples) == expected_a985["tensor_triples_sha256"],
        "triples_storage_sha256": array_bytes_digest(triples_stored),
        "q42_map_shape": list(q42.shape),
        "q42_class_count": int(np.unique(q42).size),
        "q42_map_sha256": array_digest(q42),
        "q42_map_sha256_matches_certificate": array_digest(q42) == expected_a42["map_sha256"],
        "q42_tensor_matches_stored": bool(np.array_equal(q42_tensor, q42_tensor_stored)),
        "q42_tensor_sha256": array_digest(q42_tensor),
        "q42_tensor_sha256_matches_certificate": array_digest(q42_tensor) == expected_a42["tensor_sha256"],
        "q42_tensor_nonzero": int(np.count_nonzero(q42_tensor)),
        "q42_tensor_total": int(q42_tensor.sum()),
        "q12_map_shape": list(q12.shape),
        "q12_class_count": int(np.unique(q12).size),
        "q12_map_sha256": array_digest(q12),
        "q12_map_sha256_matches_certificate": array_digest(q12) == expected_a12["map_sha256"],
        "q12_tensor_matches_stored": bool(np.array_equal(q12_tensor, q12_tensor_stored)),
        "q12_tensor_sha256": array_digest(q12_tensor),
        "q12_tensor_sha256_matches_certificate": array_digest(q12_tensor) == expected_a12["tensor_sha256"],
        "q12_tensor_nonzero": int(np.count_nonzero(q12_tensor)),
        "q12_tensor_total": int(q12_tensor.sum()),
        "a42_to_a12_consistent": bool(a42_to_a12_consistent),
        "a42_to_a12_map_matches_certificate": a42_to_a12 == expected_a12["A42_to_A12_map"],
        "relation_matrix_matches_tensor_header": bool(np.array_equal(relation_matrix, np.asarray(tensor["M"], dtype=np.int64))),
        "relation_matrix_sum": int(relation_matrix.sum()),
    }
    all_checks_pass = all(v for k, v in checks.items() if k.endswith("_matches_certificate") or k.endswith("_matches_stored")) and all(
        [
            checks["triples_shape_matches_certificate"],
            checks["triples_coefficient_total_matches_certificate"],
            checks["a42_to_a12_consistent"],
            checks["relation_matrix_matches_tensor_header"],
        ]
    )

    manifest = {
        "schema": "d20.theorem.t985_csdo_manifest.source_drop",
        "name": "t985_csdo",
        "inputs": {
            "tensor_triples": {"path": rel(TENSOR_NPZ), "array": "triples", "canonical_dtype": "int64"},
            "relation_to_source_object": {"path": rel(QUOTIENTS_NPZ), "array": "block_i", "canonical_dtype": "int64"},
            "relation_to_target_object": {"path": rel(QUOTIENTS_NPZ), "array": "block_j", "canonical_dtype": "int64"},
            "relation_to_A42_map": {"path": rel(QUOTIENTS_NPZ), "array": "q42_map", "canonical_dtype": "int64"},
            "relation_to_A12_map": {"path": rel(QUOTIENTS_NPZ), "array": "q12_map", "canonical_dtype": "int64"},
            "six_object_labels": LABELS,
        },
        "outputs": {
            "report": "data/invariants/d20/theorems/t985_csdo/report.json",
            "manifest": "data/invariants/d20/theorems/t985_csdo/manifest.json",
        },
        "certification_tests": [
            "check tensor triples against the d20 certificate digest",
            "aggregate T985 through q42 and q12 and compare stored quotient tensors",
            "derive the A42 to A12 map from q42 and q12",
            "recover the six-object relation-count matrix from source and target object maps",
        ],
    }

    report = {
        "schema": "d20.theorem.t985_csdo.source_drop",
        "status": "T985_CSDO_THEOREM_INPUTS_CERTIFIED",
        "object": "d20",
        "claim": "The T985 structure-constant table and q42 quotient map are present as theorem-grade inputs and reproduce the certified A42/A12 quotient tensors.",
        "inputs": manifest["inputs"],
        "file_hashes": {
            rel(TENSOR_NPZ): sha_file(TENSOR_NPZ),
            rel(QUOTIENTS_NPZ): sha_file(QUOTIENTS_NPZ),
            rel(CERTIFICATE_JSON): sha_file(CERTIFICATE_JSON),
        },
        "checks": checks,
        "derived": {
            "A42_to_A12_map": a42_to_a12,
            "relation_matrix": relation_matrix.astype(int).tolist(),
            "coefficient_matrix_by_source_target_objects": coefficient_matrix.astype(int).tolist(),
        },
        "all_checks_pass": bool(all_checks_pass),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    registry = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": 1,
        "theorems": [
            {
                "id": "t985_csdo",
                "manifest": "data/invariants/d20/theorems/t985_csdo/manifest.json",
                "report": "data/invariants/d20/theorems/t985_csdo/report.json",
                "status": report["status"],
                "report_sha256": report["certificate_sha256"],
            }
        ],
    }
    registry["registry_sha256"] = sha_json({k: v for k, v in registry.items() if k != "registry_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir.parent / "index.json").write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
