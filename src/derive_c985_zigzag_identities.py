from __future__ import annotations

import json
from math import gcd
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


THEOREM_ID = "c985_zigzag_identities"
STATUS = "C985_ZIGZAG_IDENTITIES_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

REGISTRY_REPORT = REGISTRY_DIR / "report.json"
REGISTRY_SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
REGISTRY_TRANSPOSE = REGISTRY_DIR / "transpose.npy"
REGISTRY_IDENTITIES = REGISTRY_DIR / "identity_orbitals.json"
FUSION_REPORT = D20_INVARIANTS / "proof_obligations" / "c985_fusion_multiplicity_typing" / "report.json"
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
PAIR_TRANSPORT_NPZ = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_associator_rebracketing_oracle"
    / "pair_transport_section.npz"
)
UNIT_REPORT = D20_INVARIANTS / "proof_obligations" / "c985_unit_tensor_laws" / "report.json"
UNIT_RECORDS_NPZ = D20_INVARIANTS / "proof_obligations" / "c985_unit_tensor_laws" / "unit_action_records.npz"
TRIANGLE_REPORT = D20_INVARIANTS / "proof_obligations" / "c985_unit_triangle_coherence" / "report.json"
DUALITY_REPORT = D20_INVARIANTS / "proof_obligations" / "c985_duality_support" / "report.json"
PENTAGON_REPORT = D20_INVARIANTS / "proof_obligations" / "c985_pentagon_chain_normal_form" / "report.json"
ACTION_NPZ = GENERATED / "be3_action_words_from_absolute_presentation.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_zigzag_identities.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_zigzag_identities.py"


def identity_relations() -> list[int]:
    payload = load_json(REGISTRY_IDENTITIES)
    rows = payload.get("identity_orbitals", [])
    return [
        int(row["identity_relation"])
        for row in sorted(rows, key=lambda item: int(item["object_id"]))
    ]


def key(alpha: int, beta: int, gamma: int) -> int:
    return int(alpha) * 985 * 985 + int(beta) * 985 + int(gamma)


def find_index_row(index: np.ndarray, keys: np.ndarray, alpha: int, beta: int, gamma: int) -> tuple[int, int]:
    target = key(alpha, beta, gamma)
    pos = int(np.searchsorted(keys, target))
    if pos >= keys.size or int(keys[pos]) != target:
        raise AssertionError(f"missing fusion basis row {(alpha, beta, gamma)}")
    return int(index[pos, 3]), int(index[pos, 4])


def normalized_fraction(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        raise ZeroDivisionError("zero denominator")
    if den < 0:
        num = -num
        den = -den
    g = gcd(abs(num), den)
    return num // g, den // g


def solve_two_equations(right_counts: np.ndarray, left_counts: np.ndarray) -> list[tuple[int, int, int]]:
    if np.array_equal(right_counts, left_counts):
        nz = np.nonzero(right_counts)[0]
        if nz.size == 0:
            raise AssertionError("zero zig-zag count row")
        col = int(nz[0])
        num, den = normalized_fraction(1, int(right_counts[col]))
        return [(col, num, den)]
    for first in range(right_counts.size):
        for second in range(first + 1, right_counts.size):
            det = int(right_counts[first] * left_counts[second] - right_counts[second] * left_counts[first])
            if det == 0:
                continue
            n1 = int(left_counts[second] - right_counts[second])
            n2 = int(right_counts[first] - left_counts[first])
            p1 = normalized_fraction(n1, det)
            p2 = normalized_fraction(n2, det)
            return [(first, p1[0], p1[1]), (second, p2[0], p2[1])]
    raise AssertionError("zig-zag linear equations have no two-column solution")


def basis_points(basis: np.ndarray, index: np.ndarray, keys: np.ndarray, alpha: int, beta: int, gamma: int) -> np.ndarray:
    offset, count = find_index_row(index, keys, alpha, beta, gamma)
    return basis[offset : offset + count, 3].astype(np.int64)


def build_zigzag_witness() -> dict[str, Any]:
    seed = load_relation_seed(SOURCE_RELATION_NPZ)
    points = int(seed["points"])
    reps = seed["reps"].astype(np.int64)
    labels = build_label_matrix(seed["encoded_pairs"], seed["offsets"], points)
    source_target = np.asarray(np.load(REGISTRY_SOURCE_TARGET, allow_pickle=False), dtype=np.int64)
    transpose = np.asarray(np.load(REGISTRY_TRANSPOSE, allow_pickle=False), dtype=np.int64)
    identities = np.asarray(identity_relations(), dtype=np.int64)
    basis = np.asarray(
        np.load(FUSION_BASIS_NPZ, allow_pickle=False)["basis_records"],
        dtype=np.int64,
    )
    index = np.asarray(
        np.load(FUSION_INDEX_NPZ, allow_pickle=False)["index_records"],
        dtype=np.int64,
    )
    keys = index[:, 0] * 985 * 985 + index[:, 1] * 985 + index[:, 2]
    action = np.asarray(np.load(ACTION_NPZ, allow_pickle=False)["action_permutations"], dtype=np.int64)
    section = np.asarray(
        np.load(PAIR_TRANSPORT_NPZ, allow_pickle=False)["pair_transport_group_index"],
        dtype=np.int64,
    )
    unit_records = np.asarray(
        np.load(UNIT_RECORDS_NPZ, allow_pickle=False)["records"],
        dtype=np.int64,
    )
    inverse_cache: dict[int, np.ndarray] = {}

    def inverse_perm(group_index: int) -> np.ndarray:
        group_index = int(group_index)
        cached = inverse_cache.get(group_index)
        if cached is not None:
            return cached
        inv = np.empty(points, dtype=np.int64)
        inv[action[group_index]] = np.arange(points, dtype=np.int64)
        inverse_cache[group_index] = inv
        return inv

    def left_to_right(alpha: int, beta: int, delta: int, z0: int, chi: int, epsilon: int, w: int) -> tuple[int, int, int]:
        x = int(reps[epsilon, 2])
        y = int(reps[epsilon, 3])
        left_group = int(section[x * points + int(w)])
        z = int(action[left_group, int(z0)])
        eta = int(labels[z, y])
        right_group = int(section[z * points + y])
        w0 = int(inverse_perm(right_group)[int(w)])
        return eta, w0, z

    def right_to_left(beta: int, chi: int, eta: int, w0: int, alpha: int, epsilon: int, z: int) -> tuple[int, int, int]:
        x = int(reps[epsilon, 2])
        y = int(reps[epsilon, 3])
        right_group = int(section[int(z) * points + y])
        w = int(action[right_group, int(w0)])
        delta = int(labels[x, w])
        left_group = int(section[x * points + w])
        z0 = int(inverse_perm(left_group)[int(z)])
        return delta, z0, w

    coevaluation_rows: list[list[int]] = []
    evaluation_rows: list[list[int]] = []
    count_rows: list[list[int]] = []
    summary_rows = np.empty((985, 8), dtype=np.int32)
    failures: list[dict[str, Any]] = []
    max_denominator = 1

    for alpha in range(985):
        dual = int(transpose[alpha])
        source = int(source_target[alpha, 0])
        target = int(source_target[alpha, 1])
        source_identity = int(identities[source])
        target_identity = int(identities[target])
        coev_points = basis_points(basis, index, keys, alpha, dual, source_identity)
        eval_points = basis_points(basis, index, keys, dual, alpha, target_identity)
        eval_position = {int(point): pos for pos, point in enumerate(eval_points)}
        right_counts = np.zeros(eval_points.size, dtype=np.int64)
        left_counts = np.zeros(eval_points.size, dtype=np.int64)

        x = int(reps[alpha, 2])
        y = int(reps[alpha, 3])
        for point in coev_points:
            eta, eval_point, z = left_to_right(alpha, dual, source_identity, int(point), alpha, alpha, x)
            if eta == target_identity and z == y and eval_point in eval_position:
                right_counts[eval_position[eval_point]] += 1

        dual_x = int(reps[dual, 2])
        dual_right_unit_point = int(unit_records[dual, 6])
        for point in coev_points:
            delta, eval_point, w = right_to_left(alpha, dual, source_identity, int(point), dual, dual, dual_right_unit_point)
            if delta == target_identity and w == dual_x and eval_point in eval_position:
                left_counts[eval_position[eval_point]] += 1

        try:
            solution = solve_two_equations(right_counts, left_counts)
        except AssertionError as exc:
            failures.append(
                {
                    "alpha": alpha,
                    "dual": dual,
                    "reason": str(exc),
                    "coev_dim": int(coev_points.size),
                    "eval_dim": int(eval_points.size),
                    "right_count_sum": int(right_counts.sum()),
                    "left_count_sum": int(left_counts.sum()),
                }
            )
            solution = []

        for point in coev_points:
            coevaluation_rows.append([alpha, int(point), 1, 1])
        for col, numerator, denominator in solution:
            max_denominator = max(max_denominator, int(denominator))
            evaluation_rows.append([alpha, int(eval_points[col]), int(numerator), int(denominator)])
        nonzero_cols = np.nonzero((right_counts != 0) | (left_counts != 0))[0]
        for col in nonzero_cols:
            count_rows.append([alpha, int(eval_points[col]), int(right_counts[col]), int(left_counts[col])])

        right_num = 0
        left_num = 0
        common_den = 1
        for col, numerator, denominator in solution:
            common_den *= int(denominator)
        for col, numerator, denominator in solution:
            factor = common_den // int(denominator)
            right_num += int(right_counts[col]) * int(numerator) * factor
            left_num += int(left_counts[col]) * int(numerator) * factor
        if right_num != common_den or left_num != common_den:
            failures.append(
                {
                    "alpha": alpha,
                    "dual": dual,
                    "reason": "zig-zag scalar is not one",
                    "right_num": right_num,
                    "left_num": left_num,
                    "den": common_den,
                }
            )

        summary_rows[alpha] = [
            alpha,
            dual,
            int(coev_points.size),
            int(eval_points.size),
            int(right_counts.sum()),
            int(left_counts.sum()),
            int(len(solution)),
            int(common_den if solution else 0),
        ]

    coevaluation = np.asarray(coevaluation_rows, dtype=np.int32)
    evaluation = np.asarray(evaluation_rows, dtype=np.int32)
    counts = np.asarray(count_rows, dtype=np.int32)
    return {
        "coevaluation_maps": coevaluation,
        "evaluation_maps": evaluation,
        "zigzag_count_rows": counts,
        "zigzag_summary_rows": summary_rows,
        "summary": {
            "simple_count": 985,
            "zigzag_failure_count": len(failures),
            "first_zigzag_failures": failures[:8],
            "coevaluation_nonzero_terms": int(coevaluation.shape[0]),
            "evaluation_nonzero_terms": int(evaluation.shape[0]),
            "zigzag_count_rows": int(counts.shape[0]),
            "right_zigzag_count_sum": int(summary_rows[:, 4].sum()),
            "left_zigzag_count_sum": int(summary_rows[:, 5].sum()),
            "solution_terms_min": int(summary_rows[:, 6].min()),
            "solution_terms_max": int(summary_rows[:, 6].max()),
            "max_denominator": int(max_denominator),
            "inverse_cache_size": int(len(inverse_cache)),
            "coevaluation_maps_sha256": sha_array(coevaluation),
            "evaluation_maps_sha256": sha_array(evaluation),
            "zigzag_count_rows_sha256": sha_array(counts),
            "zigzag_summary_rows_sha256": sha_array(summary_rows),
            "first_16_summary_rows": summary_rows[:16].astype(int).tolist(),
            "first_16_evaluation_rows": evaluation[:16].astype(int).tolist(),
        },
    }


def build_payloads() -> dict[str, Any]:
    reports = {
        "typed_registry_report": load_json(REGISTRY_REPORT),
        "fusion_report": load_json(FUSION_REPORT),
        "associator_report": load_json(ASSOCIATOR_REPORT),
        "unit_report": load_json(UNIT_REPORT),
        "triangle_report": load_json(TRIANGLE_REPORT),
        "duality_report": load_json(DUALITY_REPORT),
        "pentagon_report": load_json(PENTAGON_REPORT),
    }
    witness = build_zigzag_witness()
    summary = witness["summary"]

    checks = {
        "typed_registry_certified": reports["typed_registry_report"].get("status")
        == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "fusion_multiplicity_typing_certified": reports["fusion_report"].get("status")
        == "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
        "associator_oracle_certified": reports["associator_report"].get("status")
        == "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
        "unit_tensor_laws_certified": reports["unit_report"].get("status")
        == "C985_UNIT_TENSOR_LAWS_CERTIFIED",
        "unit_triangle_coherence_certified": reports["triangle_report"].get("status")
        == "C985_UNIT_TRIANGLE_COHERENCE_CERTIFIED",
        "duality_support_certified": reports["duality_report"].get("status")
        == "C985_DUALITY_SUPPORT_CERTIFIED",
        "pentagon_chain_normal_form_certified": reports["pentagon_report"].get("status")
        == "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
        "all_985_simples_checked": summary["simple_count"] == 985,
        "zigzag_failures_are_zero": summary["zigzag_failure_count"] == 0,
        "coevaluation_terms_match_duality_support_total": summary["coevaluation_nonzero_terms"] == 15456,
        "each_simple_has_evaluation_solution": summary["solution_terms_min"] > 0,
        "right_and_left_zigzag_counts_are_nonzero": summary["right_zigzag_count_sum"] > 0
        and summary["left_zigzag_count_sum"] > 0,
        "evaluation_coefficients_are_integral": summary["max_denominator"] == 1,
    }

    zigzag_certificate = {
        "schema": "c985.zigzag_identities_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_ZIGZAG_IDENTITIES_PROVISIONAL",
        "checks": checks,
        "witness": summary,
        "linear_maps": {
            "coevaluation_maps": relpath(OUT_DIR / "coevaluation_maps.npz"),
            "evaluation_maps": relpath(OUT_DIR / "evaluation_maps.npz"),
            "convention": (
                "Coevaluation has coefficient 1 on every certified coevaluation "
                "basis point. Evaluation coefficients are the recorded integral "
                "solution rows; applying the associator oracle gives scalar 1 "
                "for both zig-zag composites."
            ),
        },
        "does_not_certify": [
            "spherical structure",
            "pivotal structure",
            "unitarity",
            "braiding",
            "full Drinfeld center or modular data",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.zigzag_identities@1",
        "status": zigzag_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The transpose duality data admits explicit C-linear evaluation and "
            "coevaluation maps satisfying both zig-zag identities for all 985 "
            "simple generators."
        ),
        "stage_protocol": {
            "draft": "use certified duality support, unit triangle, and pentagon-normal associator",
            "witness": "materialize evaluation/coevaluation maps and zig-zag count rows",
            "coherence": "solve and verify the two zig-zag scalar equations for every simple",
            "closure": "certify rigidity of the semisimple monoidal C985 skeleton",
            "emit": "emit zig-zag certificate and final C985 multi-fusion checklist target",
        },
        "inputs": {
            "typed_registry_report": input_entry(REGISTRY_REPORT, {"status": reports["typed_registry_report"].get("status")}),
            "fusion_report": input_entry(FUSION_REPORT, {"status": reports["fusion_report"].get("status")}),
            "associator_report": input_entry(ASSOCIATOR_REPORT, {"status": reports["associator_report"].get("status")}),
            "unit_report": input_entry(UNIT_REPORT, {"status": reports["unit_report"].get("status")}),
            "triangle_report": input_entry(TRIANGLE_REPORT, {"status": reports["triangle_report"].get("status")}),
            "duality_report": input_entry(DUALITY_REPORT, {"status": reports["duality_report"].get("status")}),
            "pentagon_report": input_entry(PENTAGON_REPORT, {"status": reports["pentagon_report"].get("status")}),
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "source_target": input_entry(REGISTRY_SOURCE_TARGET),
            "transpose": input_entry(REGISTRY_TRANSPOSE),
            "identity_orbitals": input_entry(REGISTRY_IDENTITIES),
            "fusion_basis_points": input_entry(FUSION_BASIS_NPZ),
            "fusion_basis_index": input_entry(FUSION_INDEX_NPZ),
            "pair_transport_section": input_entry(PAIR_TRANSPORT_NPZ),
            "unit_action_records": input_entry(UNIT_RECORDS_NPZ),
            "be3_action": input_entry(ACTION_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "coevaluation_maps": relpath(OUT_DIR / "coevaluation_maps.npz"),
            "evaluation_maps": relpath(OUT_DIR / "evaluation_maps.npz"),
            "zigzag_counts": relpath(OUT_DIR / "zigzag_counts.npz"),
            "zigzag_certificate": relpath(OUT_DIR / "zigzag_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": summary,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "explicit evaluation maps for all 985 transpose-dual pairs",
                "explicit coevaluation maps for all 985 transpose-dual pairs",
                "both zig-zag identities for every simple generator",
                "rigidity of the certified semisimple monoidal C985 skeleton",
            ],
            "does_not_certify": zigzag_certificate["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Emit the final C985 multi-fusion checklist tying finite "
            "semisimplicity, tensor coherence, decomposable unit, and rigidity "
            "to K0(C985) ~= A985."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.zigzag_identities_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "derive right and left zig-zag count rows from the associator oracle",
            "solve the two zig-zag scalar equations for every simple",
            "materialize coevaluation coefficients",
            "materialize evaluation coefficients",
            "require zigzag_failure_count=0",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "coevaluation_maps": witness["coevaluation_maps"],
        "evaluation_maps": witness["evaluation_maps"],
        "zigzag_count_rows": witness["zigzag_count_rows"],
        "zigzag_summary_rows": witness["zigzag_summary_rows"],
        "zigzag_certificate": zigzag_certificate,
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
    np.savez_compressed(OUT_DIR / "coevaluation_maps.npz", rows=payloads["coevaluation_maps"])
    np.savez_compressed(OUT_DIR / "evaluation_maps.npz", rows=payloads["evaluation_maps"])
    np.savez_compressed(
        OUT_DIR / "zigzag_counts.npz",
        count_rows=payloads["zigzag_count_rows"],
        summary_rows=payloads["zigzag_summary_rows"],
    )
    write_json(OUT_DIR / "zigzag_certificate.json", payloads["zigzag_certificate"])
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
                "zigzag_failures": payloads["report"]["witness"]["zigzag_failure_count"],
                "evaluation_nonzero_terms": payloads["report"]["witness"]["evaluation_nonzero_terms"],
                "coevaluation_nonzero_terms": payloads["report"]["witness"]["coevaluation_nonzero_terms"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
