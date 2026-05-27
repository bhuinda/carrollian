from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        SOURCE_RELATION_NPZ,
        build_label_matrix,
        input_entry,
        load_json,
        load_relation_seed,
        self_hash,
        sha_array,
        sha_file,
        sha_json,
        write_json,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        SOURCE_RELATION_NPZ,
        build_label_matrix,
        input_entry,
        load_json,
        load_relation_seed,
        self_hash,
        sha_array,
        sha_file,
        sha_json,
        write_json,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "c985_fusion_multiplicity_typing"
STATUS = "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

SOURCE_TENSOR_NPZ = GENERATED / "tensor_from_source_coorient.npz"
REGISTRY_REPORT = REGISTRY_DIR / "report.json"
REGISTRY_SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_fusion_multiplicity_typing.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_fusion_multiplicity_typing.py"


def load_source_tensor() -> dict[str, np.ndarray]:
    z = np.load(SOURCE_TENSOR_NPZ, allow_pickle=False)
    triples = np.asarray(z["triples"], dtype=np.int32)
    return {
        "triples": triples,
        "M": np.asarray(z["M"], dtype=np.int64),
        "reps": np.asarray(z["reps"], dtype=np.int32),
    }


def derive_basis_and_tensor() -> dict[str, np.ndarray]:
    seed = load_relation_seed(SOURCE_RELATION_NPZ)
    points = int(seed["points"])
    relation_count = int(seed["offsets"].size - 1)
    labels = build_label_matrix(seed["encoded_pairs"], seed["offsets"], points)
    reps = seed["reps"]

    total_basis = relation_count * points
    basis = np.empty((total_basis, 4), dtype=np.int32)
    cursor = 0
    z_points = np.arange(points, dtype=np.int32)
    for gamma in range(relation_count):
        x = int(reps[gamma, 2])
        y = int(reps[gamma, 3])
        alpha = labels[x, :].astype(np.int32, copy=False)
        beta = labels[:, y].astype(np.int32, copy=False)
        span = slice(cursor, cursor + points)
        basis[span, 0] = alpha
        basis[span, 1] = beta
        basis[span, 2] = gamma
        basis[span, 3] = z_points
        cursor += points
    order = np.lexsort((basis[:, 3], basis[:, 2], basis[:, 1], basis[:, 0]))
    basis = basis[order]

    keys = (
        basis[:, 0].astype(np.int64) * relation_count * relation_count
        + basis[:, 1].astype(np.int64) * relation_count
        + basis[:, 2].astype(np.int64)
    )
    unique_keys, starts, counts = np.unique(keys, return_index=True, return_counts=True)
    alpha = (unique_keys // (relation_count * relation_count)).astype(np.int32)
    beta = ((unique_keys // relation_count) % relation_count).astype(np.int32)
    gamma = (unique_keys % relation_count).astype(np.int32)
    triples = np.column_stack([alpha, beta, gamma, counts.astype(np.int32)]).astype(np.int32)
    index = np.column_stack([alpha, beta, gamma, starts.astype(np.int64), counts.astype(np.int64)]).astype(
        np.int64
    )
    return {
        "basis": basis,
        "triples": triples,
        "index": index,
    }


def typing_failure_count(triples: np.ndarray, source_target: np.ndarray) -> int:
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    ok = (
        (source_target[alpha, 0] == source_target[gamma, 0])
        & (source_target[alpha, 1] == source_target[beta, 0])
        & (source_target[beta, 1] == source_target[gamma, 1])
    )
    return int((~ok).sum())


def relation_pair_matrix(source_target: np.ndarray) -> np.ndarray:
    matrix = np.zeros((6, 6), dtype=np.int64)
    for source, target in source_target:
        matrix[int(source), int(target)] += 1
    return matrix


def build_payloads() -> dict[str, Any]:
    registry_report = load_json(REGISTRY_REPORT)
    source_target = np.load(REGISTRY_SOURCE_TARGET, allow_pickle=False)
    source_tensor = load_source_tensor()
    derived = derive_basis_and_tensor()

    triples = derived["triples"]
    basis = derived["basis"]
    index = derived["index"]
    source_triples = source_tensor["triples"]
    source_order = np.lexsort((source_triples[:, 2], source_triples[:, 1], source_triples[:, 0]))
    source_triples = source_triples[source_order]
    matrix = relation_pair_matrix(source_target)
    typing_failures = typing_failure_count(triples, source_target)

    checks = {
        "typed_registry_certified": registry_report.get("status")
        == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "source_tensor_exists": SOURCE_TENSOR_NPZ.exists(),
        "source_tensor_support_is_1414965": int(source_triples.shape[0]) == 1414965,
        "derived_tensor_support_is_1414965": int(triples.shape[0]) == 1414965,
        "derived_tensor_matches_source_tensor": bool(np.array_equal(triples, source_triples)),
        "basis_row_count_matches_coefficient_total": int(basis.shape[0]) == 2537360,
        "basis_index_row_count_matches_tensor_support": int(index.shape[0]) == int(triples.shape[0]),
        "basis_index_counts_sum_to_basis_rows": int(index[:, 4].sum()) == int(basis.shape[0]),
        "all_fusion_coefficients_positive_on_support": bool(np.all(triples[:, 3] > 0)),
        "all_fusion_coefficients_integral": str(triples.dtype) == "int32",
        "fusion_typing_failure_count_is_zero": typing_failures == 0,
        "source_tensor_matrix_matches_registry": source_tensor["M"].astype(int).tolist()
        == matrix.astype(int).tolist(),
        "source_target_shape_is_985_by_2": tuple(source_target.shape) == (985, 2),
    }

    witness = {
        "relation_count": 985,
        "tensor_support": int(triples.shape[0]),
        "coefficient_total": int(triples[:, 3].sum()),
        "coefficient_min": int(triples[:, 3].min()),
        "coefficient_max": int(triples[:, 3].max()),
        "basis_row_count": int(basis.shape[0]),
        "typing_failure_count": typing_failures,
        "fusion_tensor_sha256": sha_array(triples),
        "multiplicity_basis_points_sha256": sha_array(basis),
        "multiplicity_basis_index_sha256": sha_array(index),
        "object_pair_relation_matrix": matrix.astype(int).tolist(),
        "first_16_tensor_rows": triples[:16].astype(int).tolist(),
        "first_16_basis_rows": basis[:16].astype(int).tolist(),
        "first_16_index_rows": index[:16].astype(int).tolist(),
    }

    multiplicity_basis_index_json = {
        "schema": "c985.fusion_multiplicity_basis_index@1",
        "basis_encoding": {
            "multiplicity_basis_points_npz": relpath(OUT_DIR / "multiplicity_basis_points.npz"),
            "basis_records_columns": ["alpha", "beta", "gamma", "intermediate_point_z"],
            "multiplicity_basis_index_npz": relpath(OUT_DIR / "multiplicity_basis_index.npz"),
            "index_records_columns": ["alpha", "beta", "gamma", "basis_offset", "basis_count"],
            "basis_order": "lexicographic alpha,beta,gamma,intermediate_point_z",
        },
        "basis_row_count": int(basis.shape[0]),
        "index_row_count": int(index.shape[0]),
        "basis_sha256": sha_array(basis),
        "index_sha256": sha_array(index),
        "sample_index_rows": index[:32].astype(int).tolist(),
    }

    fusion_typing_certificate = {
        "schema": "c985.fusion_typing_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_FUSION_MULTIPLICITY_TYPING_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "interpretation": (
            "Each nonzero tensor coefficient p_{alpha,beta}^{gamma} is realized by "
            "the finite basis of intermediate points z with (x,z) in R_alpha, "
            "(z,y) in R_beta, and (x,y) in R_gamma for the selected representative "
            "pair of R_gamma."
        ),
        "does_not_certify": [
            "associator/F-symbol bijections between bracketings",
            "pentagon coherence",
            "unit triangle coherence",
            "duality evaluation and coevaluation maps",
            "zig-zag identities",
            "full finite semisimple multi-fusion category status",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.fusion_multiplicity_typing@1",
        "status": fusion_typing_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The C985 tensor product multiplicities are certified as nonnegative typed "
            "finite incidence-basis dimensions matching the A985 sparse tensor."
        ),
        "stage_protocol": {
            "draft": "use the verified typed registry and the source/coorient A985 tensor",
            "witness": "materialize fusion_tensor_coo.npz plus multiplicity basis and index archives",
            "coherence": "check coefficient positivity, basis dimensions, source/target typing, and equality with the A985 tensor",
            "closure": "certify the decategorified fusion multiplicity layer while leaving associator and higher coherence open",
            "emit": "emit fusion typing certificate and next C985 coherence target",
        },
        "inputs": {
            "typed_registry_report": input_entry(
                REGISTRY_REPORT,
                {
                    "status": registry_report.get("status"),
                    "certificate_sha256": registry_report.get("certificate_sha256"),
                },
            ),
            "source_target": input_entry(REGISTRY_SOURCE_TARGET),
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "source_tensor": input_entry(SOURCE_TENSOR_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "fusion_tensor_coo": relpath(OUT_DIR / "fusion_tensor_coo.npz"),
            "multiplicity_basis_points": relpath(OUT_DIR / "multiplicity_basis_points.npz"),
            "multiplicity_basis_index_npz": relpath(OUT_DIR / "multiplicity_basis_index.npz"),
            "multiplicity_basis_index": relpath(OUT_DIR / "multiplicity_basis_index.json"),
            "fusion_typing_certificate": relpath(OUT_DIR / "fusion_typing_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "nonnegative integral fusion coefficients on the 985 typed simple generators",
                "zero source/target typing failures for all nonzero products",
                "finite multiplicity bases indexed by intermediate incidence points",
                "agreement of the derived fusion tensor with the existing A985 tensor",
            ],
            "does_not_certify": fusion_typing_certificate["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Construct associator/F-symbol bijections by identifying the two bracketings "
            "of length-three incidence chains and hash the deterministic reindexing maps."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.fusion_multiplicity_typing_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "rebuild multiplicity bases from relation representative pairs and intermediate points",
            "derive sparse fusion tensor coefficients from basis counts",
            "compare derived tensor with generated/tensor_from_source_coorient.npz",
            "verify every nonzero coefficient is source/target typed",
            "verify index counts sum to the multiplicity basis archive row count",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "fusion_tensor_coo": triples,
        "multiplicity_basis_points": basis,
        "multiplicity_basis_index_array": index,
        "multiplicity_basis_index": multiplicity_basis_index_json,
        "fusion_typing_certificate": fusion_typing_certificate,
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
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT_DIR / "fusion_tensor_coo.npz", triples=payloads["fusion_tensor_coo"])
    np.savez_compressed(
        OUT_DIR / "multiplicity_basis_points.npz",
        basis_records=payloads["multiplicity_basis_points"],
    )
    np.savez_compressed(
        OUT_DIR / "multiplicity_basis_index.npz",
        index_records=payloads["multiplicity_basis_index_array"],
    )
    write_json(OUT_DIR / "multiplicity_basis_index.json", payloads["multiplicity_basis_index"])
    write_json(OUT_DIR / "fusion_typing_certificate.json", payloads["fusion_typing_certificate"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "tensor_support": payloads["report"]["witness"]["tensor_support"],
                "basis_row_count": payloads["report"]["witness"]["basis_row_count"],
                "typing_failure_count": payloads["report"]["witness"]["typing_failure_count"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
