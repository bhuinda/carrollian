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
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_duality_support"
STATUS = "C985_DUALITY_SUPPORT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

REGISTRY_REPORT = REGISTRY_DIR / "report.json"
REGISTRY_SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
REGISTRY_TRANSPOSE = REGISTRY_DIR / "transpose.npy"
REGISTRY_IDENTITIES = REGISTRY_DIR / "identity_orbitals.json"
FUSION_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "report.json"
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
TRIANGLE_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_unit_triangle_coherence"
    / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_duality_support.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_duality_support.py"


def identity_relations() -> list[int]:
    payload = load_json(REGISTRY_IDENTITIES)
    rows = payload.get("identity_orbitals", [])
    return [
        int(row["identity_relation"])
        for row in sorted(rows, key=lambda item: int(item["object_id"]))
    ]


def key(alpha: int, beta: int, gamma: int) -> int:
    return int(alpha) * 985 * 985 + int(beta) * 985 + int(gamma)


def find_index_row(index: np.ndarray, keys: np.ndarray, alpha: int, beta: int, gamma: int) -> tuple[int, int] | None:
    target = key(alpha, beta, gamma)
    pos = int(np.searchsorted(keys, target))
    if pos >= keys.size or int(keys[pos]) != target:
        return None
    return int(index[pos, 3]), int(index[pos, 4])


def build_duality_records() -> tuple[np.ndarray, dict[str, Any]]:
    source_target = np.asarray(np.load(REGISTRY_SOURCE_TARGET, allow_pickle=False), dtype=np.int16)
    transpose = np.asarray(np.load(REGISTRY_TRANSPOSE, allow_pickle=False), dtype=np.int32)
    identities = np.asarray(identity_relations(), dtype=np.int32)
    basis = np.asarray(
        np.load(FUSION_BASIS_NPZ, allow_pickle=False)["basis_records"],
        dtype=np.int32,
    )
    index = np.asarray(
        np.load(FUSION_INDEX_NPZ, allow_pickle=False)["index_records"],
        dtype=np.int64,
    )
    keys = (
        index[:, 0].astype(np.int64) * 985 * 985
        + index[:, 1].astype(np.int64) * 985
        + index[:, 2].astype(np.int64)
    )
    if not np.all(keys[1:] > keys[:-1]):
        raise AssertionError("fusion basis index keys are not strictly sorted")

    records = np.empty((985, 10), dtype=np.int32)
    failures: list[dict[str, Any]] = []
    for alpha in range(985):
        dual = int(transpose[alpha])
        source = int(source_target[alpha, 0])
        target = int(source_target[alpha, 1])
        eval_identity = int(identities[target])
        coeval_identity = int(identities[source])
        eval_row = find_index_row(index, keys, dual, alpha, eval_identity)
        coeval_row = find_index_row(index, keys, alpha, dual, coeval_identity)
        eval_dim = 0 if eval_row is None else eval_row[1]
        coeval_dim = 0 if coeval_row is None else coeval_row[1]
        eval_first = -1 if eval_row is None else int(basis[eval_row[0], 3])
        coeval_first = -1 if coeval_row is None else int(basis[coeval_row[0], 3])
        checks = {
            "dual_source_target_flipped": int(source_target[dual, 0]) == target
            and int(source_target[dual, 1]) == source,
            "eval_space_nonzero": eval_dim > 0,
            "coeval_space_nonzero": coeval_dim > 0,
        }
        if not all(checks.values()):
            failures.append(
                {
                    "alpha": alpha,
                    "dual": dual,
                    "source": source,
                    "target": target,
                    "checks": checks,
                    "eval_dim": eval_dim,
                    "coeval_dim": coeval_dim,
                }
            )
        records[alpha] = [
            alpha,
            dual,
            source,
            target,
            eval_identity,
            coeval_identity,
            eval_dim,
            coeval_dim,
            eval_first,
            coeval_first,
        ]

    return records, {
        "duality_failure_count": len(failures),
        "first_duality_failures": failures[:8],
        "eval_dim_min": int(records[:, 6].min()),
        "eval_dim_max": int(records[:, 6].max()),
        "coeval_dim_min": int(records[:, 7].min()),
        "coeval_dim_max": int(records[:, 7].max()),
        "eval_dim_total": int(records[:, 6].sum()),
        "coeval_dim_total": int(records[:, 7].sum()),
    }


def build_payloads() -> dict[str, Any]:
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    triangle_report = load_json(TRIANGLE_REPORT)
    source_target = np.asarray(np.load(REGISTRY_SOURCE_TARGET, allow_pickle=False), dtype=np.int16)
    transpose = np.asarray(np.load(REGISTRY_TRANSPOSE, allow_pickle=False), dtype=np.int32)
    identities = identity_relations()
    records, duality_summary = build_duality_records()

    duality_table = {
        "schema": "c985.duality_support_records@1",
        "columns": [
            "alpha",
            "transpose_dual",
            "source_object_id",
            "target_object_id",
            "evaluation_identity_relation",
            "coevaluation_identity_relation",
            "evaluation_basis_dimension",
            "coevaluation_basis_dimension",
            "first_evaluation_basis_point",
            "first_coevaluation_basis_point",
        ],
        "records_npz": relpath(OUT_DIR / "duality_support_records.npz"),
        "record_count": int(records.shape[0]),
        "records_sha256": sha_array(records),
        "first_32_records": records[:32].astype(int).tolist(),
    }

    checks = {
        "typed_registry_certified": registry_report.get("status")
        == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "fusion_multiplicity_typing_certified": fusion_report.get("status")
        == "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
        "unit_triangle_coherence_certified": triangle_report.get("status")
        == "C985_UNIT_TRIANGLE_COHERENCE_CERTIFIED",
        "duality_record_count_is_985": int(records.shape[0]) == 985,
        "transpose_is_involution": bool(np.array_equal(transpose[transpose], np.arange(985))),
        "transpose_flips_all_source_targets": bool(
            np.array_equal(source_target[transpose, 0], source_target[:, 1])
            and np.array_equal(source_target[transpose, 1], source_target[:, 0])
        ),
        "identity_orbitals_are_self_dual": bool(np.array_equal(transpose[np.asarray(identities)], np.asarray(identities))),
        "evaluation_spaces_are_nonzero": int(records[:, 6].min()) > 0,
        "coevaluation_spaces_are_nonzero": int(records[:, 7].min()) > 0,
        "duality_failures_are_zero": duality_summary["duality_failure_count"] == 0,
    }

    witness = {
        "relation_count": 985,
        "identity_relations": identities,
        "duality_records_sha256": sha_array(records),
        "duality_summary": duality_summary,
        "first_16_duality_records": records[:16].astype(int).tolist(),
    }

    duality_certificate = {
        "schema": "c985.duality_support_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_DUALITY_SUPPORT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "interpretation": (
            "Transpose gives a source/target-flipped candidate dual for every "
            "simple, and the evaluation and coevaluation target identity "
            "multiplicity spaces are finite and nonzero."
        ),
        "does_not_certify": [
            "specific evaluation and coevaluation linear combinations",
            "zig-zag identities",
            "full rigidity",
            "full finite semisimple multi-fusion category status",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.duality_support@1",
        "status": duality_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The transpose involution supplies a typed dual candidate for each "
            "C985 simple, with nonzero evaluation and coevaluation multiplicity "
            "spaces against the six identity orbitals."
        ),
        "stage_protocol": {
            "draft": "use certified transpose, identity orbitals, and fusion multiplicity bases",
            "witness": "materialize duality_support_records.npz and duality support certificate",
            "coherence": "check source/target flip and nonzero eval/coeval spaces for all 985 simples",
            "closure": "certify duality support while leaving zig-zag identities open",
            "emit": "emit duality support certificate and next C985 zig-zag target",
        },
        "inputs": {
            "typed_registry_report": input_entry(
                REGISTRY_REPORT,
                {
                    "status": registry_report.get("status"),
                    "certificate_sha256": registry_report.get("certificate_sha256"),
                },
            ),
            "fusion_report": input_entry(
                FUSION_REPORT,
                {
                    "status": fusion_report.get("status"),
                    "certificate_sha256": fusion_report.get("certificate_sha256"),
                },
            ),
            "triangle_report": input_entry(
                TRIANGLE_REPORT,
                {
                    "status": triangle_report.get("status"),
                    "certificate_sha256": triangle_report.get("certificate_sha256"),
                },
            ),
            "source_target": input_entry(REGISTRY_SOURCE_TARGET),
            "transpose": input_entry(REGISTRY_TRANSPOSE),
            "identity_orbitals": input_entry(REGISTRY_IDENTITIES),
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "fusion_basis_points": input_entry(FUSION_BASIS_NPZ),
            "fusion_basis_index": input_entry(FUSION_INDEX_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "duality_support_records": relpath(OUT_DIR / "duality_support_records.npz"),
            "duality_support_table": relpath(OUT_DIR / "duality_support_table.json"),
            "duality_certificate": relpath(OUT_DIR / "duality_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "transpose dual candidate for every C985 simple",
                "source/target flip and transpose involution",
                "nonzero evaluation multiplicity space X_alpha^vee tensor X_alpha -> 1_target",
                "nonzero coevaluation multiplicity space 1_source -> X_alpha tensor X_alpha^vee",
            ],
            "does_not_certify": duality_certificate["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Choose explicit evaluation/coevaluation vectors in these nonzero "
            "multiplicity spaces and verify the two zig-zag identities using "
            "the associator oracle."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.duality_support_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "check transpose is an involution and flips source/target",
            "check identity orbitals are self-dual",
            "check every evaluation multiplicity space is nonzero",
            "check every coevaluation multiplicity space is nonzero",
            "record basis dimensions and first basis points for all 985 simples",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "duality_support_records": records,
        "duality_support_table": duality_table,
        "duality_certificate": duality_certificate,
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
    np.savez_compressed(
        OUT_DIR / "duality_support_records.npz",
        records=payloads["duality_support_records"],
    )
    write_json(OUT_DIR / "duality_support_table.json", payloads["duality_support_table"])
    write_json(OUT_DIR / "duality_certificate.json", payloads["duality_certificate"])
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
                "eval_dim_min": payloads["report"]["witness"]["duality_summary"]["eval_dim_min"],
                "coeval_dim_min": payloads["report"]["witness"]["duality_summary"]["coeval_dim_min"],
                "duality_failures": payloads["report"]["witness"]["duality_summary"]["duality_failure_count"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
