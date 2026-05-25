from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import src.derive_d20_oriented_matroid_tutte_os as tutte_os
    from src.derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
        matrix_vector_product,
    )
    from src.derive_d20_oriented_matroid_sector33_extension import (
        is_circuit,
        matroid_rank,
        rank_of_columns,
    )
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import src.derive_d20_oriented_matroid_tutte_os as tutte_os
    from src.derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
        matrix_vector_product,
    )
    from src.derive_d20_oriented_matroid_sector33_extension import (
        is_circuit,
        matroid_rank,
        rank_of_columns,
    )
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_oriented_matroid_prime_lift_audit"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
AUDIT_PRIMES = [1_000_003, 1_000_033, 1_000_037, 1_000_039, 1_000_081]

D20_JSON = ROOT / "d20.json"
SECTOR33_EXTENSION = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_extension" / "report.json"
)
SECTOR33_DUAL = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
TUTTE_OS = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_tutte_os" / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    limit = math.isqrt(value)
    divisor = 3
    while divisor <= limit:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def compute_prime_tutte(matrix: list[list[int]], prime: int) -> dict[str, Any]:
    original_prime = tutte_os.FIELD_PRIME
    try:
        tutte_os.FIELD_PRIME = prime
        mod_matrix = tutte_os.reduce_matrix(matrix)
        initial_state, rank = tutte_os.canonical_state(mod_matrix, len(mod_matrix[0]))
        polynomial, cache_stats = tutte_os.tutte_polynomial(initial_state)
        terms = tutte_os.polynomial_terms(polynomial)
        specializations = {
            "T_1_1_basis_count": tutte_os.evaluate_tutte(polynomial, 1, 1),
            "T_2_2_all_subsets": tutte_os.evaluate_tutte(polynomial, 2, 2),
        }
        return {
            "field_prime": prime,
            "is_prime": is_prime(prime),
            "rank": rank,
            "ground_set_size": len(mod_matrix[0]),
            "term_count": len(terms),
            "polynomial_sha256": sha_json(terms),
            "cache_stats": cache_stats,
            "specializations": specializations,
        }
    finally:
        tutte_os.FIELD_PRIME = original_prime


def exact_rational_audit(matrix: list[list[int]], attachment: dict[str, Any]) -> dict[str, Any]:
    ground = list(range(len(matrix[0])))
    new_element = int(attachment["new_element_id"])
    support = attachment["active_support"] + [new_element]
    positive_vector = [0 for _ in ground]
    for edge_id in attachment["active_support"]:
        positive_vector[edge_id] = 1
    positive_vector[new_element] = int(attachment["sector33_dimension"])
    kernel_image = matrix_vector_product(matrix, positive_vector)
    support_rank = rank_of_columns(matrix, support)
    deletion_ranks = {
        str(element): rank_of_columns(matrix, [item for item in support if item != element])
        for element in support
    }
    coefficient_gcd = 0
    for value in positive_vector:
        coefficient_gcd = math.gcd(coefficient_gcd, abs(value))
    return {
        "ground_set_size": len(ground),
        "matrix_rank_over_q": matroid_rank(matrix),
        "positive_circuit_support": support,
        "positive_circuit_coefficients": [positive_vector[element] for element in support],
        "positive_circuit_coefficient_gcd": coefficient_gcd,
        "positive_circuit_kernel_image": kernel_image,
        "positive_support_rank_over_q": support_rank,
        "positive_support_deletion_ranks_over_q": deletion_ranks,
        "positive_support_is_exact_q_circuit": is_circuit(matrix, support),
    }


def build_theorem() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    extension = load_json(SECTOR33_EXTENSION)
    dual = load_json(SECTOR33_DUAL)
    tutte_report = load_json(TUTTE_OS)

    matrix, attachment = build_sector33_height_attachment_matrix()
    baseline_hash = tutte_report["derived"]["tutte_polynomial"]["polynomial_sha256"]
    baseline_basis_count = tutte_report["derived"]["tutte_polynomial"]["specializations"][
        "T_1_1_basis_count"
    ]
    prime_records = [compute_prime_tutte(matrix, prime) for prime in AUDIT_PRIMES]
    rational = exact_rational_audit(matrix, attachment)
    stable_hashes = sorted({record["polynomial_sha256"] for record in prime_records})
    stable_basis_counts = sorted(
        {record["specializations"]["T_1_1_basis_count"] for record in prime_records}
    )

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "sector33_extension_input_is_certified": extension.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_EXTENSION_CERTIFIED"
        and extension.get("all_checks_pass") is True,
        "sector33_dual_input_is_certified": dual.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual.get("all_checks_pass") is True,
        "tutte_os_input_is_certified": tutte_report.get("status")
        == "D20_ORIENTED_MATROID_TUTTE_OS_CERTIFIED"
        and tutte_report.get("all_checks_pass") is True,
        "all_audit_primes_are_prime": all(record["is_prime"] for record in prime_records),
        "all_audit_primes_have_rank_20": all(record["rank"] == 20 for record in prime_records),
        "all_audit_primes_have_ground_31": all(
            record["ground_set_size"] == 31 for record in prime_records
        ),
        "all_audit_primes_have_93_terms": all(
            record["term_count"] == 93 for record in prime_records
        ),
        "all_audit_primes_match_baseline_tutte_hash": stable_hashes == [baseline_hash],
        "all_audit_primes_match_baseline_basis_count": stable_basis_counts
        == [baseline_basis_count],
        "all_audit_primes_pass_all_subsets_specialization": all(
            record["specializations"]["T_2_2_all_subsets"] == 2 ** 31
            for record in prime_records
        ),
        "exact_q_rank_is_20": rational["matrix_rank_over_q"] == 20,
        "distinguished_support_is_exact_q_circuit": rational[
            "positive_support_is_exact_q_circuit"
        ],
        "distinguished_q_circuit_has_zero_image": all(
            value == 0 for value in rational["positive_circuit_kernel_image"]
        ),
        "distinguished_q_circuit_is_primitive": rational[
            "positive_circuit_coefficient_gcd"
        ]
        == 1,
    }

    report = {
        "schema": "d20.theorem.d20_oriented_matroid_prime_lift_audit",
        "status": "D20_ORIENTED_MATROID_PRIME_LIFT_AUDIT_CERTIFIED",
        "object": "D20",
        "definition": {
            "audit_scope": (
                "multi-prime stability of the sector-33 height-attachment Tutte "
                "polynomial, plus exact rational checks for rank and the distinguished "
                "gamma8+e33 circuit"
            ),
            "non_claim": (
                "this audit does not prove that every rational and modular circuit "
                "support agrees; that remains the promotion gate"
            ),
        },
        "claim": (
            "The sector-33 Tutte/OS package is stable across five large prime-field "
            "reductions, all with rank 20, 93 Tutte terms, the same polynomial hash, "
            "and the same basis count. The underlying integer matrix has exact "
            "rational rank 20, and the gamma8+e33 positive circuit is an exact "
            "primitive rational circuit. This is a certified lift audit, not a full "
            "rational promotion."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
            "d20_oriented_matroid_sector33_extension_report": input_record(
                SECTOR33_EXTENSION
            ),
            "d20_oriented_matroid_sector33_dual_report": input_record(SECTOR33_DUAL),
            "d20_oriented_matroid_tutte_os_report": input_record(TUTTE_OS),
        },
        "derived": {
            "audit_primes": AUDIT_PRIMES,
            "baseline": {
                "field_prime": tutte_report["derived"]["field_matroid"]["field_prime"],
                "tutte_polynomial_sha256": baseline_hash,
                "basis_count": baseline_basis_count,
                "report_sha256": tutte_report["certificate_sha256"],
            },
            "prime_field_records": prime_records,
            "prime_stability_summary": {
                "stable_tutte_hashes": stable_hashes,
                "stable_basis_counts": stable_basis_counts,
                "all_primes_match_baseline": stable_hashes == [baseline_hash]
                and stable_basis_counts == [baseline_basis_count],
            },
            "exact_rational_audit": rational,
            "promotion_boundary": {
                "full_rational_promotion_certified": False,
                "remaining_gate": (
                    "certify that every modular circuit support is an exact rational "
                    "circuit, or replay deletion-contraction with exact rational "
                    "rank-preservation witnesses"
                ),
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "confirmed": [
                "the finite-field Tutte polynomial is stable across the audited primes",
                "the sector-33 height attachment has exact rational rank 20",
                "the distinguished gamma8+e33 positive circuit is exact over Q",
            ],
            "guardrails": [
                "multi-prime stability is evidence, not an exhaustive rational matroid equality proof",
                "the OS/NBC summary remains formally certified over the audited prime fields",
                "the rational promotion gate is explicit and not marked complete",
            ],
        },
        "next_highest_yield_item": (
            "Build the exact circuit-support promotion certificate: enumerate or "
            "otherwise certify that every modular circuit support in the sector-33 "
            "height attachment is also a rational circuit."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_oriented_matroid_prime_lift_audit_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "audit multi-prime stability of the sector-33 Tutte/OS package",
            "record exact rational rank and distinguished circuit checks",
            "keep the remaining rational-promotion gate explicit",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])
    print(report["derived"]["prime_stability_summary"]["stable_tutte_hashes"][0])


if __name__ == "__main__":
    main()
