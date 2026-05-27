from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        SOURCE_RELATION_NPZ,
        input_entry,
        load_json,
        load_relation_seed,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        SOURCE_RELATION_NPZ,
        input_entry,
        load_json,
        load_relation_seed,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_unit_tensor_laws"
STATUS = "C985_UNIT_TENSOR_LAWS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

REGISTRY_REPORT = REGISTRY_DIR / "report.json"
REGISTRY_SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
REGISTRY_IDENTITIES = REGISTRY_DIR / "identity_orbitals.json"
FUSION_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "report.json"
)
FUSION_TENSOR_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "fusion_tensor_coo.npz"
)
FUSION_BASIS_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "multiplicity_basis_points.npz"
)
FUSION_INDEX_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "multiplicity_basis_index.npz"
)
ASSOCIATOR_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_associator_rebracketing_oracle"
    / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_unit_tensor_laws.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_unit_tensor_laws.py"


def load_fusion_arrays() -> dict[str, np.ndarray]:
    return {
        "triples": np.asarray(
            np.load(FUSION_TENSOR_NPZ, allow_pickle=False)["triples"],
            dtype=np.int64,
        ),
        "basis": np.asarray(
            np.load(FUSION_BASIS_NPZ, allow_pickle=False)["basis_records"],
            dtype=np.int32,
        ),
        "index": np.asarray(
            np.load(FUSION_INDEX_NPZ, allow_pickle=False)["index_records"],
            dtype=np.int64,
        ),
    }


def identity_relations() -> list[int]:
    payload = load_json(REGISTRY_IDENTITIES)
    rows = payload.get("identity_orbitals", [])
    return [
        int(row["identity_relation"])
        for row in sorted(rows, key=lambda item: int(item["object_id"]))
    ]


def key(alpha: int, beta: int, gamma: int) -> int:
    return int(alpha) * 985 * 985 + int(beta) * 985 + int(gamma)


def keyed_rows(rows: np.ndarray) -> np.ndarray:
    return rows[:, 0].astype(np.int64) * 985 * 985 + rows[:, 1].astype(np.int64) * 985 + rows[:, 2].astype(np.int64)


def find_index_row(index: np.ndarray, keys: np.ndarray, alpha: int, beta: int, gamma: int) -> tuple[int, int] | None:
    target = key(alpha, beta, gamma)
    pos = int(np.searchsorted(keys, target))
    if pos >= keys.size or int(keys[pos]) != target:
        return None
    return int(index[pos, 3]), int(index[pos, 4])


def singleton_basis_point(
    basis: np.ndarray,
    index: np.ndarray,
    keys: np.ndarray,
    alpha: int,
    beta: int,
    gamma: int,
) -> int | None:
    row = find_index_row(index, keys, alpha, beta, gamma)
    if row is None:
        return None
    offset, count = row
    if count != 1:
        return None
    return int(basis[offset, 3])


def build_unit_records(
    seed: dict[str, Any],
    source_target: np.ndarray,
    identities: list[int],
    fusion: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, Any]]:
    triples = fusion["triples"]
    basis = fusion["basis"]
    index = fusion["index"]
    tensor_keys = keyed_rows(triples)
    tensor_pair_keys = triples[:, 0].astype(np.int64) * 985 + triples[:, 1].astype(np.int64)
    index_keys = keyed_rows(index)
    if not np.all(tensor_keys[1:] > tensor_keys[:-1]):
        raise AssertionError("fusion tensor keys are not strictly sorted")
    if not np.all(tensor_pair_keys[1:] >= tensor_pair_keys[:-1]):
        raise AssertionError("fusion tensor pair keys are not sorted")
    if not np.all(index_keys[1:] > index_keys[:-1]):
        raise AssertionError("fusion basis index keys are not strictly sorted")

    records = np.empty((985, 7), dtype=np.int32)
    failures: list[dict[str, Any]] = []
    identity_to_object = np.full(985, -1, dtype=np.int16)
    for object_id, identity in enumerate(identities):
        identity_to_object[int(identity)] = object_id
    left_identity_objects = identity_to_object[triples[:, 0].astype(np.int64)]
    right_identity_objects = identity_to_object[triples[:, 1].astype(np.int64)]
    wrong_left = (left_identity_objects >= 0) & (
        left_identity_objects.astype(np.int64) != source_target[triples[:, 1].astype(np.int64), 0]
    )
    wrong_right = (right_identity_objects >= 0) & (
        right_identity_objects.astype(np.int64) != source_target[triples[:, 0].astype(np.int64), 1]
    )
    wrong_unit_nonzero = int(np.count_nonzero(wrong_left) + np.count_nonzero(wrong_right))
    reps = seed["reps"]

    def product_rows(alpha: int, beta: int) -> np.ndarray:
        target = int(alpha) * 985 + int(beta)
        lo = int(np.searchsorted(tensor_pair_keys, target, side="left"))
        hi = int(np.searchsorted(tensor_pair_keys, target, side="right"))
        return triples[lo:hi]

    for alpha in range(985):
        source = int(source_target[alpha, 0])
        target = int(source_target[alpha, 1])
        left_identity = identities[source]
        right_identity = identities[target]
        rep_x = int(reps[alpha, 2])
        rep_y = int(reps[alpha, 3])
        left_rows = product_rows(left_identity, alpha)
        right_rows = product_rows(alpha, right_identity)
        left_coeff = int(left_rows[0, 3]) if left_rows.shape[0] == 1 else 0
        right_coeff = int(right_rows[0, 3]) if right_rows.shape[0] == 1 else 0
        left_gamma = int(left_rows[0, 2]) if left_rows.shape[0] == 1 else -1
        right_gamma = int(right_rows[0, 2]) if right_rows.shape[0] == 1 else -1
        left_basis = singleton_basis_point(basis, index, index_keys, left_identity, alpha, alpha)
        right_basis = singleton_basis_point(basis, index, index_keys, alpha, right_identity, alpha)

        checks = {
            "left_product_is_single_alpha": left_rows.shape[0] == 1 and left_gamma == alpha and left_coeff == 1,
            "right_product_is_single_alpha": right_rows.shape[0] == 1 and right_gamma == alpha and right_coeff == 1,
            "left_basis_is_source_endpoint": left_basis == rep_x,
            "right_basis_is_target_endpoint": right_basis == rep_y,
        }
        if not all(checks.values()):
            failures.append(
                {
                    "alpha": alpha,
                    "checks": checks,
                    "source": source,
                    "target": target,
                    "left_identity": left_identity,
                    "right_identity": right_identity,
                    "left_row_count": int(left_rows.shape[0]),
                    "right_row_count": int(right_rows.shape[0]),
                    "left_gamma": left_gamma,
                    "right_gamma": right_gamma,
                    "left_coeff": left_coeff,
                    "right_coeff": right_coeff,
                    "left_basis": left_basis,
                    "right_basis": right_basis,
                    "representative_pair": [rep_x, rep_y],
                }
            )
        records[alpha] = [
            alpha,
            source,
            target,
            left_identity,
            right_identity,
            -1 if left_basis is None else left_basis,
            -1 if right_basis is None else right_basis,
        ]

    return records, {
        "unit_failure_count": len(failures),
        "first_unit_failures": failures[:8],
        "wrong_unit_nonzero_count": int(wrong_unit_nonzero),
    }


def build_payloads() -> dict[str, Any]:
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    associator_report = load_json(ASSOCIATOR_REPORT)
    seed = load_relation_seed(SOURCE_RELATION_NPZ)
    source_target = np.load(REGISTRY_SOURCE_TARGET, allow_pickle=False)
    identities = identity_relations()
    fusion = load_fusion_arrays()
    records, unit_summary = build_unit_records(seed, source_target, identities, fusion)

    unit_action_table = {
        "schema": "c985.unit_tensor_action_table@1",
        "columns": [
            "alpha",
            "source_object_id",
            "target_object_id",
            "left_identity_relation",
            "right_identity_relation",
            "left_unit_basis_point",
            "right_unit_basis_point",
        ],
        "records_npz": relpath(OUT_DIR / "unit_action_records.npz"),
        "identity_relations": identities,
        "record_count": int(records.shape[0]),
        "records_sha256": sha_array(records),
        "first_32_records": records[:32].astype(int).tolist(),
    }

    checks = {
        "typed_registry_certified": registry_report.get("status")
        == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "fusion_multiplicity_typing_certified": fusion_report.get("status")
        == "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
        "associator_oracle_certified": associator_report.get("status")
        == "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
        "identity_relation_count_is_6": len(identities) == 6,
        "unit_record_count_is_985": int(records.shape[0]) == 985,
        "left_unit_failures_are_zero": unit_summary["unit_failure_count"] == 0,
        "wrong_unit_products_are_zero": unit_summary["wrong_unit_nonzero_count"] == 0,
        "left_unit_basis_points_are_source_endpoints": bool(
            np.array_equal(records[:, 5], seed["reps"][:, 2])
        ),
        "right_unit_basis_points_are_target_endpoints": bool(
            np.array_equal(records[:, 6], seed["reps"][:, 3])
        ),
        "unit_action_records_are_integral": str(records.dtype) == "int32",
    }

    witness = {
        "relation_count": 985,
        "identity_relations": identities,
        "unit_action_records_sha256": sha_array(records),
        "unit_summary": unit_summary,
        "first_16_unit_records": records[:16].astype(int).tolist(),
    }

    unit_certificate = {
        "schema": "c985.unit_tensor_laws_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_UNIT_TENSOR_LAWS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "interpretation": (
            "For every simple X_alpha:i->j, the left unit 1_i and right unit "
            "1_j multiply to X_alpha with coefficient one, with singleton "
            "incidence bases at the representative pair endpoints."
        ),
        "does_not_certify": [
            "unit triangle coherence",
            "pentagon coherence",
            "duality evaluation and coevaluation maps",
            "zig-zag identities",
            "full finite semisimple multi-fusion category status",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.unit_tensor_laws@1",
        "status": unit_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The six identity orbitals act as the decomposable tensor unit on "
            "all 985 typed simple generators at the fusion-multiplicity level."
        ),
        "stage_protocol": {
            "draft": "use the verified identity orbitals and fusion multiplicity bases",
            "witness": "materialize unit_action_records.npz and unit law certificate",
            "coherence": "check left/right unit coefficients and singleton endpoint bases for all 985 simples",
            "closure": "certify tensor unit laws while leaving triangle coherence open",
            "emit": "emit unit tensor law certificate and next triangle/pentagon target",
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
            "identity_orbitals": input_entry(REGISTRY_IDENTITIES),
            "fusion_report": input_entry(
                FUSION_REPORT,
                {
                    "status": fusion_report.get("status"),
                    "certificate_sha256": fusion_report.get("certificate_sha256"),
                },
            ),
            "associator_report": input_entry(
                ASSOCIATOR_REPORT,
                {
                    "status": associator_report.get("status"),
                    "certificate_sha256": associator_report.get("certificate_sha256"),
                },
            ),
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "fusion_tensor": input_entry(FUSION_TENSOR_NPZ),
            "fusion_basis_points": input_entry(FUSION_BASIS_NPZ),
            "fusion_basis_index": input_entry(FUSION_INDEX_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "unit_action_records": relpath(OUT_DIR / "unit_action_records.npz"),
            "unit_action_table": relpath(OUT_DIR / "unit_action_table.json"),
            "unit_certificate": relpath(OUT_DIR / "unit_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "six identity orbitals as decomposable tensor-unit summands",
                "left unit coefficient p_{1_i,alpha}^{alpha}=1 for every alpha:i->j",
                "right unit coefficient p_{alpha,1_j}^{alpha}=1 for every alpha:i->j",
                "wrong-object identity products vanish",
                "left/right unit multiplicity bases are singleton endpoint bases",
            ],
            "does_not_certify": unit_certificate["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Use the associator oracle and singleton unit bases to verify the "
            "unit triangle equations, while continuing the pentagon chain "
            "normalization proof for length-four incidence chains."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.unit_tensor_laws_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "check each left unit product has exactly coefficient one on the same simple",
            "check each right unit product has exactly coefficient one on the same simple",
            "check wrong-object identity products vanish",
            "check left unit basis point is the representative source endpoint",
            "check right unit basis point is the representative target endpoint",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "unit_action_records": records,
        "unit_action_table": unit_action_table,
        "unit_certificate": unit_certificate,
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
    np.savez_compressed(OUT_DIR / "unit_action_records.npz", records=payloads["unit_action_records"])
    write_json(OUT_DIR / "unit_action_table.json", payloads["unit_action_table"])
    write_json(OUT_DIR / "unit_certificate.json", payloads["unit_certificate"])
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
                "unit_record_count": payloads["report"]["witness"]["relation_count"],
                "identity_relations": payloads["report"]["witness"]["identity_relations"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
