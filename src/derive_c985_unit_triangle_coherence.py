from __future__ import annotations

import json
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
        write_json,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "c985_unit_triangle_coherence"
STATUS = "C985_UNIT_TRIANGLE_COHERENCE_CERTIFIED"
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
FUSION_BASIS_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "multiplicity_basis_points.npz"
)
ASSOCIATOR_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_associator_rebracketing_oracle"
    / "report.json"
)
PAIR_TRANSPORT_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_associator_rebracketing_oracle"
    / "pair_transport_section.npz"
)
ACTION_NPZ = GENERATED / "be3_action_words_from_absolute_presentation.npz"
UNIT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_unit_tensor_laws"
    / "report.json"
)
UNIT_RECORDS_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_unit_tensor_laws"
    / "unit_action_records.npz"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_unit_triangle_coherence.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_unit_triangle_coherence.py"


def identity_relations() -> list[int]:
    payload = load_json(REGISTRY_IDENTITIES)
    rows = payload.get("identity_orbitals", [])
    return [
        int(row["identity_relation"])
        for row in sorted(rows, key=lambda item: int(item["object_id"]))
    ]


def load_action() -> np.ndarray:
    return np.asarray(
        np.load(ACTION_NPZ, allow_pickle=False)["action_permutations"],
        dtype=np.int16,
    )


def derive_triangle_witness() -> dict[str, Any]:
    seed = load_relation_seed(SOURCE_RELATION_NPZ)
    points = int(seed["points"])
    labels = build_label_matrix(seed["encoded_pairs"], seed["offsets"], points)
    source_target = np.asarray(np.load(REGISTRY_SOURCE_TARGET, allow_pickle=False), dtype=np.int16)
    identities = np.asarray(identity_relations(), dtype=np.int32)
    basis = np.asarray(
        np.load(FUSION_BASIS_NPZ, allow_pickle=False)["basis_records"],
        dtype=np.int32,
    )
    unit_records = np.asarray(
        np.load(UNIT_RECORDS_NPZ, allow_pickle=False)["records"],
        dtype=np.int32,
    )
    section = np.asarray(
        np.load(PAIR_TRANSPORT_NPZ, allow_pickle=False)["pair_transport_group_index"],
        dtype=np.int16,
    )
    action = load_action()
    reps = seed["reps"]

    alpha = basis[:, 0].astype(np.int64)
    beta = basis[:, 1].astype(np.int64)
    gamma = basis[:, 2].astype(np.int64)
    midpoint = basis[:, 3].astype(np.int64)

    middle_object = source_target[alpha, 1].astype(np.int64)
    gamma_x = reps[gamma, 2].astype(np.int64)
    gamma_y = reps[gamma, 3].astype(np.int64)
    alpha_x = reps[alpha, 2].astype(np.int64)
    alpha_y = reps[alpha, 3].astype(np.int64)
    beta_x = reps[beta, 2].astype(np.int64)
    beta_y = reps[beta, 3].astype(np.int64)
    middle_identity = identities[middle_object].astype(np.int64)

    left_transport = section[gamma_x * points + midpoint].astype(np.int64)
    right_transport = section[midpoint * points + gamma_y].astype(np.int64)
    transport_groups = np.column_stack([left_transport, right_transport]).astype(np.int16)

    middle_objects_match = source_target[alpha, 1] == source_target[beta, 0]
    right_unit_record_matches = unit_records[alpha, 4].astype(np.int64) == middle_identity
    left_unit_record_matches = unit_records[beta, 3].astype(np.int64) == middle_identity
    right_unit_basis_is_alpha_target = unit_records[alpha, 6].astype(np.int64) == alpha_y
    left_unit_basis_is_beta_source = unit_records[beta, 5].astype(np.int64) == beta_x
    basis_is_typed = (labels[gamma_x, midpoint].astype(np.int64) == alpha) & (
        labels[midpoint, gamma_y].astype(np.int64) == beta
    )
    left_transport_valid = (
        (left_transport >= 0)
        & (action[left_transport, alpha_x].astype(np.int64) == gamma_x)
        & (action[left_transport, alpha_y].astype(np.int64) == midpoint)
    )
    right_transport_valid = (
        (right_transport >= 0)
        & (action[right_transport, beta_x].astype(np.int64) == midpoint)
        & (action[right_transport, beta_y].astype(np.int64) == gamma_y)
    )
    triangle_ok = (
        middle_objects_match
        & right_unit_record_matches
        & left_unit_record_matches
        & right_unit_basis_is_alpha_target
        & left_unit_basis_is_beta_source
        & basis_is_typed
        & left_transport_valid
        & right_transport_valid
    )
    failure_indices = np.nonzero(~triangle_ok)[0].astype(np.int64)
    sample_positions = np.unique(
        np.concatenate(
            [
                np.arange(min(32, basis.shape[0]), dtype=np.int64),
                np.linspace(0, basis.shape[0] - 1, num=32, dtype=np.int64),
            ]
        )
    )
    sample_records = np.column_stack(
        [
            sample_positions,
            basis[sample_positions].astype(np.int64),
            middle_identity[sample_positions],
            left_transport[sample_positions],
            right_transport[sample_positions],
        ]
    ).astype(np.int64)

    check_counts = {
        "middle_object_mismatches": int(np.count_nonzero(~middle_objects_match)),
        "right_unit_record_mismatches": int(np.count_nonzero(~right_unit_record_matches)),
        "left_unit_record_mismatches": int(np.count_nonzero(~left_unit_record_matches)),
        "right_unit_basis_mismatches": int(np.count_nonzero(~right_unit_basis_is_alpha_target)),
        "left_unit_basis_mismatches": int(np.count_nonzero(~left_unit_basis_is_beta_source)),
        "basis_typing_mismatches": int(np.count_nonzero(~basis_is_typed)),
        "left_transport_failures": int(np.count_nonzero(~left_transport_valid)),
        "right_transport_failures": int(np.count_nonzero(~right_transport_valid)),
        "triangle_failures": int(failure_indices.size),
    }
    return {
        "transport_groups": transport_groups,
        "failure_indices": failure_indices,
        "sample_records": sample_records,
        "summary": {
            "basis_rows_checked": int(basis.shape[0]),
            "identity_relations": identities.astype(int).tolist(),
            "check_counts": check_counts,
            "transport_groups_sha256": sha_array(transport_groups),
            "failure_indices_sha256": sha_array(failure_indices),
            "sample_records_sha256": sha_array(sample_records),
            "first_failure_indices": failure_indices[:16].astype(int).tolist(),
            "first_16_triangle_samples": sample_records[:16].astype(int).tolist(),
        },
    }


def build_payloads() -> dict[str, Any]:
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    associator_report = load_json(ASSOCIATOR_REPORT)
    unit_report = load_json(UNIT_REPORT)
    witness = derive_triangle_witness()
    summary = witness["summary"]
    check_counts = summary["check_counts"]

    checks = {
        "typed_registry_certified": registry_report.get("status")
        == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "fusion_multiplicity_typing_certified": fusion_report.get("status")
        == "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
        "associator_oracle_certified": associator_report.get("status")
        == "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
        "unit_tensor_laws_certified": unit_report.get("status")
        == "C985_UNIT_TENSOR_LAWS_CERTIFIED",
        "all_fusion_basis_rows_checked": summary["basis_rows_checked"] == 2537360,
        "middle_object_mismatches_are_zero": check_counts["middle_object_mismatches"] == 0,
        "unit_record_mismatches_are_zero": check_counts["right_unit_record_mismatches"] == 0
        and check_counts["left_unit_record_mismatches"] == 0,
        "unit_basis_mismatches_are_zero": check_counts["right_unit_basis_mismatches"] == 0
        and check_counts["left_unit_basis_mismatches"] == 0,
        "basis_typing_mismatches_are_zero": check_counts["basis_typing_mismatches"] == 0,
        "transport_failures_are_zero": check_counts["left_transport_failures"] == 0
        and check_counts["right_transport_failures"] == 0,
        "triangle_failures_are_zero": check_counts["triangle_failures"] == 0,
    }

    triangle_certificate = {
        "schema": "c985.unit_triangle_coherence_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_UNIT_TRIANGLE_COHERENCE_PROVISIONAL",
        "checks": checks,
        "witness": summary,
        "interpretation": (
            "For every nonzero fusion basis row M_{alpha,beta}^{gamma}, the "
            "associator oracle maps the right-unit bracketing "
            "(alpha tensor 1) tensor beta to the left-unit bracketing alpha "
            "tensor (1 tensor beta) through the same midpoint basis vector."
        ),
        "does_not_certify": [
            "pentagon coherence",
            "duality evaluation and coevaluation maps",
            "zig-zag identities",
            "full finite semisimple multi-fusion category status",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.unit_triangle_coherence@1",
        "status": triangle_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The C985 unit triangle equations hold on every certified fusion "
            "multiplicity basis row under the deterministic associator oracle."
        ),
        "stage_protocol": {
            "draft": "use certified unit singleton bases and associator transport",
            "witness": "materialize unit_triangle_witness.npz and triangle certificate",
            "coherence": "check every fusion basis row against the unit triangle normalization",
            "closure": "certify unit triangle coherence while leaving pentagon and rigidity open",
            "emit": "emit triangle certificate and next C985 pentagon target",
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
            "associator_report": input_entry(
                ASSOCIATOR_REPORT,
                {
                    "status": associator_report.get("status"),
                    "certificate_sha256": associator_report.get("certificate_sha256"),
                },
            ),
            "unit_report": input_entry(
                UNIT_REPORT,
                {
                    "status": unit_report.get("status"),
                    "certificate_sha256": unit_report.get("certificate_sha256"),
                },
            ),
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "source_target": input_entry(REGISTRY_SOURCE_TARGET),
            "identity_orbitals": input_entry(REGISTRY_IDENTITIES),
            "fusion_basis_points": input_entry(FUSION_BASIS_NPZ),
            "pair_transport_section": input_entry(PAIR_TRANSPORT_NPZ),
            "be3_action": input_entry(ACTION_NPZ),
            "unit_action_records": input_entry(UNIT_RECORDS_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "unit_triangle_witness": relpath(OUT_DIR / "unit_triangle_witness.npz"),
            "triangle_certificate": relpath(OUT_DIR / "triangle_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": summary,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "unit triangle coherence on every one of the 2,537,360 fusion basis rows",
                "right-unit and left-unit singleton bases agree through the associator oracle",
                "no middle-object, unit-record, basis-typing, or transport failures",
            ],
            "does_not_certify": triangle_certificate["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Verify pentagon coherence by checking that all five associator "
            "paths normalize to the same typed length-four incidence-chain "
            "basis, then build dual evaluation/coevaluation zig-zag checks."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.unit_triangle_coherence_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "check all certified fusion basis rows, not a sample",
            "verify middle object agreement for alpha:i->j and beta:j->k",
            "verify right-unit and left-unit singleton basis records",
            "verify associator transport sends representative endpoints to the triangle midpoint",
            "require triangle_failures=0",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "unit_triangle_witness": {
            "transport_groups": witness["transport_groups"],
            "failure_indices": witness["failure_indices"],
            "sample_records": witness["sample_records"],
        },
        "triangle_certificate": triangle_certificate,
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
        OUT_DIR / "unit_triangle_witness.npz",
        **payloads["unit_triangle_witness"],
    )
    write_json(OUT_DIR / "triangle_certificate.json", payloads["triangle_certificate"])
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
                "basis_rows_checked": payloads["report"]["witness"]["basis_rows_checked"],
                "triangle_failures": payloads["report"]["witness"]["check_counts"]["triangle_failures"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
