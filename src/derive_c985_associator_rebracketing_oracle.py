from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        SOURCE_RELATION_NPZ,
        build_label_matrix,
        input_entry,
        load_json,
        load_relation_seed,
        self_hash,
        sha_array,
        sha_file,
        write_json,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        SOURCE_RELATION_NPZ,
        build_label_matrix,
        input_entry,
        load_json,
        load_relation_seed,
        self_hash,
        sha_array,
        sha_file,
        write_json,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "c985_associator_rebracketing_oracle"
STATUS = "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

ACTION_NPZ = GENERATED / "be3_action_words_from_absolute_presentation.npz"
REGISTRY_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_typed_simple_object_registry"
    / "report.json"
)
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
FUSION_TENSOR_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_fusion_multiplicity_typing"
    / "fusion_tensor_coo.npz"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_associator_rebracketing_oracle.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_associator_rebracketing_oracle.py"


def load_action() -> np.ndarray:
    z = np.load(ACTION_NPZ, allow_pickle=False)
    return np.asarray(z["action_permutations"], dtype=np.int16)


def load_fusion_arrays() -> dict[str, np.ndarray]:
    return {
        "basis": np.asarray(
            np.load(FUSION_BASIS_NPZ, allow_pickle=False)["basis_records"],
            dtype=np.int32,
        ),
        "index": np.asarray(
            np.load(FUSION_INDEX_NPZ, allow_pickle=False)["index_records"],
            dtype=np.int64,
        ),
        "triples": np.asarray(
            np.load(FUSION_TENSOR_NPZ, allow_pickle=False)["triples"],
            dtype=np.int64,
        ),
    }


def build_transport_section(seed: dict[str, Any], action: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    encoded = seed["encoded_pairs"]
    offsets = seed["offsets"]
    reps = seed["reps"]
    points = int(seed["points"])
    relation_count = offsets.size - 1
    section = np.full(points * points, -1, dtype=np.int16)

    orbit_mismatches: list[int] = []
    stabilizer_min = None
    stabilizer_max = 0
    section_rows = []
    for relation_id in range(relation_count):
        rep_x = int(reps[relation_id, 2])
        rep_y = int(reps[relation_id, 3])
        codes = action[:, rep_x].astype(np.int64) * points + action[:, rep_y].astype(np.int64)
        order = np.argsort(codes, kind="stable")
        sorted_codes = codes[order]
        first = np.empty(sorted_codes.shape, dtype=np.bool_)
        first[0] = True
        first[1:] = sorted_codes[1:] != sorted_codes[:-1]
        unique_codes = sorted_codes[first]
        group_indices = order[first].astype(np.int16)

        supplied = np.sort(encoded[int(offsets[relation_id]) : int(offsets[relation_id + 1])])
        if not np.array_equal(unique_codes, supplied):
            orbit_mismatches.append(relation_id)
        section[unique_codes] = group_indices

        stabilizer = int(action.shape[0] // unique_codes.size)
        stabilizer_min = stabilizer if stabilizer_min is None else min(stabilizer_min, stabilizer)
        stabilizer_max = max(stabilizer_max, stabilizer)
        if relation_id < 16:
            section_rows.append(
                {
                    "relation": relation_id,
                    "representative_pair": [rep_x, rep_y],
                    "orbit_size": int(unique_codes.size),
                    "stabilizer_order": stabilizer,
                    "first_transport_group_indices": group_indices[:8].astype(int).tolist(),
                }
            )

    return section, {
        "orbit_mismatch_count": len(orbit_mismatches),
        "first_orbit_mismatches": orbit_mismatches[:16],
        "transport_section_unfilled_pairs": int(np.count_nonzero(section < 0)),
        "stabilizer_order_min": int(stabilizer_min or 0),
        "stabilizer_order_max": int(stabilizer_max),
        "first_16_transport_section_rows": section_rows,
    }


def verify_transport_section(seed: dict[str, Any], action: np.ndarray, section: np.ndarray) -> dict[str, Any]:
    encoded = seed["encoded_pairs"]
    offsets = seed["offsets"]
    reps = seed["reps"]
    points = int(seed["points"])
    relation_count = offsets.size - 1
    failures: list[int] = []
    checked_pairs = 0
    for relation_id in range(relation_count):
        lo = int(offsets[relation_id])
        hi = int(offsets[relation_id + 1])
        segment = encoded[lo:hi]
        groups = section[segment].astype(np.int64)
        xs = segment // points
        ys = segment % points
        rep_x = int(reps[relation_id, 2])
        rep_y = int(reps[relation_id, 3])
        ok = bool(
            np.all(groups >= 0)
            and np.array_equal(action[groups, rep_x].astype(np.int64), xs)
            and np.array_equal(action[groups, rep_y].astype(np.int64), ys)
        )
        checked_pairs += int(segment.size)
        if not ok:
            failures.append(relation_id)
            if len(failures) >= 16:
                break
    return {
        "checked_ordered_pairs": checked_pairs,
        "transport_failures": len(failures),
        "first_transport_failure_relations": failures,
    }


def index_key(alpha: int, beta: int, gamma: int, relation_count: int) -> int:
    return int(alpha) * relation_count * relation_count + int(beta) * relation_count + int(gamma)


def index_lookup(index: np.ndarray, keys: np.ndarray, alpha: int, beta: int, gamma: int) -> tuple[int, int]:
    key = index_key(alpha, beta, gamma, 985)
    pos = int(np.searchsorted(keys, key))
    if pos >= keys.size or int(keys[pos]) != key:
        raise AssertionError(f"missing fusion basis index row {(alpha, beta, gamma)}")
    return int(index[pos, 3]), int(index[pos, 4])


def basis_contains(
    basis: np.ndarray,
    index: np.ndarray,
    keys: np.ndarray,
    alpha: int,
    beta: int,
    gamma: int,
    point: int,
) -> bool:
    offset, count = index_lookup(index, keys, alpha, beta, gamma)
    points = basis[offset : offset + count, 3]
    pos = int(np.searchsorted(points, point))
    return pos < points.size and int(points[pos]) == int(point)


def inverse_point_image(action_row: np.ndarray) -> np.ndarray:
    inv = np.empty(action_row.shape[0], dtype=np.int16)
    inv[action_row.astype(np.int64)] = np.arange(action_row.shape[0], dtype=np.int16)
    return inv


def first_last_rows_by_column(index: np.ndarray, column: int, relation_count: int) -> tuple[np.ndarray, np.ndarray]:
    first = np.full(relation_count, -1, dtype=np.int64)
    last = np.full(relation_count, -1, dtype=np.int64)
    for row_id, value in enumerate(index[:, column].astype(np.int64)):
        if first[value] < 0:
            first[value] = row_id
        last[value] = row_id
    return first, last


def build_associator_samples(
    seed: dict[str, Any],
    action: np.ndarray,
    section: np.ndarray,
    labels: np.ndarray,
    fusion: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    basis = fusion["basis"]
    index = fusion["index"]
    keys = (
        index[:, 0].astype(np.int64) * 985 * 985
        + index[:, 1].astype(np.int64) * 985
        + index[:, 2].astype(np.int64)
    )
    if not np.all(keys[1:] > keys[:-1]):
        raise AssertionError("fusion basis index keys are not strictly sorted")

    first_by_output, last_by_output = first_last_rows_by_column(index, 2, 985)
    first_by_first, last_by_first = first_last_rows_by_column(index, 0, 985)
    reps = seed["reps"]
    points = int(seed["points"])

    left_records: list[list[int]] = []
    chain_records: list[list[int]] = []
    right_records: list[list[int]] = []
    transport_groups: list[list[int]] = []
    failures: list[dict[str, Any]] = []

    for delta in range(985):
        if first_by_output[delta] < 0 or first_by_first[delta] < 0:
            continue
        row_pairs = [
            (int(first_by_output[delta]), int(first_by_first[delta]), "first"),
            (int(last_by_output[delta]), int(last_by_first[delta]), "last"),
        ]
        for inner_row_id, outer_row_id, mode in row_pairs:
            inner = index[inner_row_id]
            outer = index[outer_row_id]
            alpha, beta, inner_delta = [int(x) for x in inner[:3]]
            outer_delta, chi, epsilon = [int(x) for x in outer[:3]]
            if inner_delta != delta or outer_delta != delta:
                failures.append({"delta": delta, "mode": mode, "reason": "delta mismatch"})
                continue
            inner_offset = int(inner[3])
            inner_count = int(inner[4])
            outer_offset = int(outer[3])
            outer_count = int(outer[4])
            inner_basis_row = inner_offset if mode == "first" else inner_offset + inner_count - 1
            outer_basis_row = outer_offset if mode == "first" else outer_offset + outer_count - 1
            z0 = int(basis[inner_basis_row, 3])
            w = int(basis[outer_basis_row, 3])
            x = int(reps[epsilon, 2])
            y = int(reps[epsilon, 3])
            pair_xw = x * points + w
            group_left = int(section[pair_xw])
            z = int(action[group_left, z0])
            eta = int(labels[z, y])
            pair_zy = z * points + y
            group_right = int(section[pair_zy])
            inv_right = inverse_point_image(action[group_right])
            w0 = int(inv_right[w])
            eta_x = int(reps[eta, 2])
            eta_y = int(reps[eta, 3])

            checks = {
                "outer_basis_typed": int(labels[x, w]) == delta and int(labels[w, y]) == chi,
                "chain_typed": int(labels[x, z]) == alpha
                and int(labels[z, w]) == beta
                and int(labels[w, y]) == chi
                and int(labels[x, y]) == epsilon,
                "right_transport_typed": int(action[group_right, eta_x]) == z
                and int(action[group_right, eta_y]) == y,
                "right_inner_basis_exists": basis_contains(basis, index, keys, beta, chi, eta, w0),
                "right_outer_basis_exists": basis_contains(basis, index, keys, alpha, eta, epsilon, z),
            }
            if not all(checks.values()):
                failures.append(
                    {
                        "delta": delta,
                        "mode": mode,
                        "reason": "sample map failed",
                        "checks": checks,
                    }
                )
                continue
            left_records.append([alpha, beta, delta, z0, chi, epsilon, w])
            chain_records.append([x, z, w, y])
            right_records.append([beta, chi, eta, w0, alpha, epsilon, z])
            transport_groups.append([group_left, group_right])

    samples = {
        "left_records": np.asarray(left_records, dtype=np.int32),
        "chain_records": np.asarray(chain_records, dtype=np.int32),
        "right_records": np.asarray(right_records, dtype=np.int32),
        "transport_groups": np.asarray(transport_groups, dtype=np.int16),
    }
    summary = {
        "sample_count": int(samples["left_records"].shape[0]),
        "sample_failure_count": len(failures),
        "first_sample_failures": failures[:8],
        "sample_delta_modes": "first and last available left-bracketing rows for every intermediate delta",
        "sample_unique_chain_count": int(np.unique(samples["chain_records"], axis=0).shape[0])
        if samples["chain_records"].size
        else 0,
        "left_sample_sha256": sha_array(samples["left_records"]),
        "chain_sample_sha256": sha_array(samples["chain_records"]),
        "right_sample_sha256": sha_array(samples["right_records"]),
        "transport_group_sample_sha256": sha_array(samples["transport_groups"]),
        "first_16_left_samples": samples["left_records"][:16].astype(int).tolist(),
        "first_16_chain_samples": samples["chain_records"][:16].astype(int).tolist(),
        "first_16_right_samples": samples["right_records"][:16].astype(int).tolist(),
    }
    return samples, summary


def associator_address_counts(triples: np.ndarray) -> dict[str, Any]:
    relation_count = 985
    support_in = np.bincount(triples[:, 2], minlength=relation_count).astype(np.int64)
    support_first = np.bincount(triples[:, 0], minlength=relation_count).astype(np.int64)
    support_second = np.bincount(triples[:, 1], minlength=relation_count).astype(np.int64)
    weight_in = np.bincount(triples[:, 2], weights=triples[:, 3], minlength=relation_count).astype(np.int64)
    weight_first = np.bincount(triples[:, 0], weights=triples[:, 3], minlength=relation_count).astype(np.int64)
    weight_second = np.bincount(triples[:, 1], weights=triples[:, 3], minlength=relation_count).astype(np.int64)
    return {
        "left_support_address_rows": int(np.sum(support_in * support_first)),
        "right_support_address_rows": int(np.sum(support_in * support_second)),
        "left_multiplicity_basis_vectors": int(np.sum(weight_in * weight_first)),
        "right_multiplicity_basis_vectors": int(np.sum(weight_in * weight_second)),
        "multiplicity_basis_vectors": int(triples[:, 3].sum()),
        "support_in_sha256": sha_array(support_in),
        "support_first_sha256": sha_array(support_first),
        "support_second_sha256": sha_array(support_second),
        "weight_in_sha256": sha_array(weight_in),
        "weight_first_sha256": sha_array(weight_first),
        "weight_second_sha256": sha_array(weight_second),
    }


def build_payloads() -> dict[str, Any]:
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    seed = load_relation_seed(SOURCE_RELATION_NPZ)
    action = load_action()
    labels = build_label_matrix(seed["encoded_pairs"], seed["offsets"], int(seed["points"]))
    fusion = load_fusion_arrays()
    section, section_summary = build_transport_section(seed, action)
    section_verification = verify_transport_section(seed, action, section)
    samples, sample_summary = build_associator_samples(seed, action, section, labels, fusion)
    address_counts = associator_address_counts(fusion["triples"])

    oracle = {
        "schema": "c985.associator_rebracketing_oracle@1",
        "basis_model": {
            "left_record_columns": [
                "alpha",
                "beta",
                "delta",
                "inner_point_z0",
                "chi",
                "epsilon",
                "outer_point_w",
            ],
            "chain_record_columns": ["x", "z", "w", "y"],
            "right_record_columns": [
                "beta",
                "chi",
                "eta",
                "inner_point_w0",
                "alpha",
                "epsilon",
                "outer_point_z",
            ],
            "transport_section": relpath(OUT_DIR / "pair_transport_section.npz"),
            "sample_witnesses": relpath(OUT_DIR / "associator_sample_witnesses.npz"),
        },
        "left_to_chain_algorithm": [
            "for epsilon choose its representative pair (x,y)",
            "outer left basis row gives w with (x,w) in R_delta and (w,y) in R_chi",
            "pair_transport_section[x,y,w] chooses the least group element sending rep(delta) to (x,w)",
            "transport the inner basis point z0 by that group element to obtain z",
            "the chain is (x,z,w,y)",
        ],
        "chain_to_right_algorithm": [
            "set eta to the relation label of (z,y)",
            "pair_transport_section chooses the least group element sending rep(eta) to (z,y)",
            "pull w back by the inverse point permutation to obtain w0",
            "use w0 as the M_{beta,chi}^{eta} basis point and z as the M_{alpha,eta}^{epsilon} basis point",
        ],
        "address_counts": address_counts,
    }

    checks = {
        "typed_registry_certified": registry_report.get("status")
        == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "fusion_multiplicity_typing_certified": fusion_report.get("status")
        == "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
        "action_shape_is_9216_by_2576": tuple(action.shape) == (9216, 2576),
        "transport_section_covers_all_ordered_pairs": section_summary["transport_section_unfilled_pairs"] == 0,
        "transport_orbits_match_all_985_relations": section_summary["orbit_mismatch_count"] == 0,
        "transport_sends_representatives_to_every_ordered_pair": section_verification["transport_failures"] == 0
        and section_verification["checked_ordered_pairs"] == int(seed["points"]) * int(seed["points"]),
        "left_and_right_support_address_counts_match": address_counts["left_support_address_rows"]
        == address_counts["right_support_address_rows"],
        "left_and_right_multiplicity_basis_counts_match": address_counts["left_multiplicity_basis_vectors"]
        == address_counts["right_multiplicity_basis_vectors"],
        "known_full_left_support_address_rows_match": address_counts["left_support_address_rows"]
        == 2367375223,
        "known_full_associator_basis_vectors_match": address_counts["left_multiplicity_basis_vectors"]
        == 6536239360,
        "sample_rebracketing_failures_are_zero": sample_summary["sample_failure_count"] == 0,
        "sample_rebracketing_count_is_1970": sample_summary["sample_count"] == 1970,
    }

    witness = {
        "relation_count": 985,
        "points": int(seed["points"]),
        "group_order": int(seed["group_order"]),
        "transport_section_sha256": sha_array(section),
        "action_sha256": sha_array(action),
        "address_counts": address_counts,
        "transport_section_summary": section_summary,
        "transport_section_verification": section_verification,
        "sample_summary": sample_summary,
    }

    associator_certificate = {
        "schema": "c985.associator_rebracketing_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_ASSOCIATOR_REBRACKETING_ORACLE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "interpretation": (
            "The certificate supplies a deterministic transport section from each "
            "orbital representative pair to every ordered pair in its relation, "
            "then defines left/right associator basis rebracketing through the "
            "same length-three incidence chain (x,z,w,y)."
        ),
        "does_not_certify": [
            "pentagon coherence",
            "unit triangle coherence",
            "duality evaluation and coevaluation maps",
            "zig-zag identities",
            "full finite semisimple multi-fusion category status",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.associator_rebracketing_oracle@1",
        "status": associator_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The C985 associator basis rebracketing is given by a deterministic "
            "transport-section oracle identifying both bracketings with typed "
            "length-three incidence chains."
        ),
        "stage_protocol": {
            "draft": "use the verified typed registry, fusion multiplicity bases, and recovered Be3 action",
            "witness": "materialize pair_transport_section.npz, associator oracle metadata, and concrete sample rebracketings",
            "coherence": "check full transport-section coverage, exact left/right basis counts, and sampled left-to-right chain maps",
            "closure": "certify the associator rebracketing oracle while leaving pentagon, units, and rigidity open",
            "emit": "emit associator oracle certificate and next C985 pentagon target",
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
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "be3_action": input_entry(ACTION_NPZ),
            "fusion_basis_points": input_entry(FUSION_BASIS_NPZ),
            "fusion_basis_index": input_entry(FUSION_INDEX_NPZ),
            "fusion_tensor": input_entry(FUSION_TENSOR_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "pair_transport_section": relpath(OUT_DIR / "pair_transport_section.npz"),
            "associator_sample_witnesses": relpath(OUT_DIR / "associator_sample_witnesses.npz"),
            "associator_oracle": relpath(OUT_DIR / "associator_oracle.json"),
            "associator_certificate": relpath(OUT_DIR / "associator_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "least-group-element transport section for every ordered pair in every C985 orbital",
                "deterministic left-bracketing to length-three-chain map",
                "deterministic length-three-chain to right-bracketing map",
                "exact equality of left and right associator basis vector counts",
                "sampled concrete F-symbol permutation rows across every intermediate delta",
            ],
            "does_not_certify": associator_certificate["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Use this associator oracle to verify pentagon coherence by checking "
            "that all five rebracketing paths induce the same deterministic "
            "length-four incidence-chain reindexing."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.associator_rebracketing_oracle_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "build a least-group-index transport section for every ordered pair",
            "verify the recovered action orbit of every representative pair equals the stored orbital segment",
            "verify the section sends representative pairs to every ordered pair in its relation",
            "compute exact left and right associator address-space sizes from the certified fusion tensor",
            "sample first/last left-bracketing rows for every intermediate delta and map them through length-three chains",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "pair_transport_section": section,
        "associator_sample_witnesses": samples,
        "associator_oracle": oracle,
        "associator_certificate": associator_certificate,
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
        OUT_DIR / "pair_transport_section.npz",
        pair_transport_group_index=payloads["pair_transport_section"],
    )
    np.savez_compressed(
        OUT_DIR / "associator_sample_witnesses.npz",
        **payloads["associator_sample_witnesses"],
    )
    write_json(OUT_DIR / "associator_oracle.json", payloads["associator_oracle"])
    write_json(OUT_DIR / "associator_certificate.json", payloads["associator_certificate"])
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
                "left_associator_basis_vectors": payloads["report"]["witness"]["address_counts"][
                    "left_multiplicity_basis_vectors"
                ],
                "right_associator_basis_vectors": payloads["report"]["witness"]["address_counts"][
                    "right_multiplicity_basis_vectors"
                ],
                "sample_count": payloads["report"]["witness"]["sample_summary"]["sample_count"],
                "transport_section_sha256": payloads["report"]["witness"]["transport_section_sha256"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
