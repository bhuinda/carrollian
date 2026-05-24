from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
REPORT_PATH = CVX / "reports" / "quotient_kernel_reflection_certificate.json"

PROJECTION_SECTION = ROOT / "layers" / "tube" / "projection_section.json"
KERNEL_DESCENT = ROOT / "layers" / "tube" / "kernel_descent_audit.json"
DRINFELD_BOUNDARY = ROOT / "layers" / "drinfeld" / "boundary.json"
FULL_LEDGER = CVX / "reports" / "full_no_escape_closure_ledger.json"
X_POLICY = CVX / "reports" / "x_policy_boundary_certificate.json"
T985_EQUIVALENCE = CVX / "reports" / "t985_univalent_equivalence_obligation.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def report_status(path: Path, expected_status: str | None = None) -> dict[str, Any]:
    data = load_json(path)
    status = data.get("status")
    row: dict[str, Any] = {
        "path": rel(path),
        "status": status,
        "sha256": sha256(path),
    }
    if expected_status is not None:
        row["expected_status"] = expected_status
        row["passed"] = status == expected_status
    else:
        row["passed"] = path.exists()
    return row


def build_report() -> dict[str, Any]:
    projection = load_json(PROJECTION_SECTION)
    descent = load_json(KERNEL_DESCENT)
    drinfeld = load_json(DRINFELD_BOUNDARY)
    ledger = load_json(FULL_LEDGER)
    x_policy = load_json(X_POLICY)
    t985 = load_json(T985_EQUIVALENCE)

    projection_dims = projection.get("projection", {})
    section = projection.get("section", {})
    descent_dims = descent.get("dimensions", {})
    drinfeld_projection = drinfeld.get("tube_pair_projection", {})
    exact_ops = descent.get("exact_kernel_descending_operations", [])
    obstructed_ops = descent.get("kernel_obstructed_operations", [])

    quotient_dim = projection_dims.get("closed_loop_quotient_dimension")
    kernel_dim = projection_dims.get("projection_kernel_dimension")
    tube_pair_total = projection_dims.get("tube_pair_basis_total")

    obligations = {
        "projection_surjects_to_public_loop_quotient": {
            "passed": projection_dims.get("projection_surjective") is True
            and quotient_dim == 297,
            "evidence": {
                "projection": "P: TubePair -> Loop_297",
                "closed_loop_quotient_dimension": quotient_dim,
                "tube_pair_basis_total": tube_pair_total,
            },
            "needed": "A certified quotient map from full tube-pair data to the public closed-loop quotient.",
        },
        "kernel_retained_as_hidden_fiber": {
            "passed": kernel_dim == 44224 and descent_dims.get("projection_kernel_dimension") == 44224,
            "evidence": {
                "projection_kernel_dimension": kernel_dim,
                "kernel_descent_dimension": descent_dims.get("projection_kernel_dimension"),
            },
            "needed": "A nonzero retained projection kernel, not an erased or silently collapsed fiber.",
        },
        "canonical_section_is_only_a_chosen_return": {
            "passed": section.get("projection_section_identity") is True
            and section.get("pivot_tube_pair_representatives") == quotient_dim,
            "evidence": {
                "projection_section_identity": section.get("projection_section_identity"),
                "section_pivots": section.get("pivot_tube_pair_representatives"),
                "section_nonzero_coefficients": section.get("section_nonzero_coefficients"),
                "section_hash_root": section.get("section_hash_root"),
            },
            "needed": "A right inverse P*S=I on the quotient, recorded as a chosen representative lift rather than a kernel collapse.",
        },
        "descent_distinguishes_kernel_respecting_from_kernel_obstructed_operations": {
            "passed": descent.get("status") == "TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED"
            and bool(exact_ops)
            and bool(obstructed_ops),
            "evidence": {
                "exact_kernel_descending_operations": exact_ops,
                "kernel_obstructed_operations": obstructed_ops,
                "kernel_descent_test": descent.get("interpretation", {}).get("kernel_descent_test"),
            },
            "needed": "A certified test showing which operations descend through the quotient and which remain section-dependent.",
        },
        "drinfeld_boundary_agrees_with_projection_data": {
            "passed": drinfeld.get("status") == "DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED"
            and drinfeld_projection.get("closed_loop_quotient_dimension") == quotient_dim
            and drinfeld_projection.get("projection_kernel_dimension") == kernel_dim
            and drinfeld_projection.get("section_identity") is True,
            "evidence": {
                "drinfeld_status": drinfeld.get("status"),
                "drinfeld_projection": drinfeld_projection,
            },
            "needed": "Independent boundary-layer agreement on quotient dimension, kernel dimension, and section identity.",
        },
        "public_p_excludes_hidden_x_recovery": {
            "passed": x_policy.get("status") == "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
            "evidence": {
                "x_policy_status": x_policy.get("status"),
                "x_policy_decision": x_policy.get("decision"),
            },
            "needed": "A policy boundary keeping hidden-sector extractor/fiber access outside public-P computation.",
        },
        "global_iff_is_not_inserted": {
            "passed": t985.get("decision", {}).get("may_claim_univalent_p_not_np_iff_t985") is False,
            "evidence": {
                "t985_equivalence_status": t985.get("status"),
                "may_claim_univalent_p_not_np_iff_t985": t985.get("decision", {}).get(
                    "may_claim_univalent_p_not_np_iff_t985"
                ),
            },
            "needed": "The rolewise quotient/kernel certificate must not silently assert the blocked literal equivalence.",
        },
    }

    pass_condition = all(item["passed"] for item in obligations.values())

    return {
        "schema": "d20.integrity.quotient_kernel_reflection.source_drop",
        "status": (
            "QUOTIENT_KERNEL_REFLECTION_CERTIFIED_ROLEWISE"
            if pass_condition
            else "QUOTIENT_KERNEL_REFLECTION_BLOCKED"
        ),
        "claim_level": "rolewise_reflection_not_literal_p_np_equivalence",
        "source_audit": {
            "projection_section": report_status(PROJECTION_SECTION),
            "kernel_descent_audit": report_status(
                KERNEL_DESCENT,
                "TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED",
            ),
            "drinfeld_boundary": report_status(
                DRINFELD_BOUNDARY,
                "DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED",
            ),
            "full_no_escape_closure_ledger": report_status(
                FULL_LEDGER,
                "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED",
            ),
            "x_policy_boundary": report_status(
                X_POLICY,
                "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
            ),
            "t985_univalent_equivalence_obligation": report_status(
                T985_EQUIVALENCE,
                "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING",
            ),
        },
        "bridge_map": {
            "name": "tube_pair_projection",
            "map": "P: TubePair_44521 -> Loop_297",
            "domain_role": "full tube-pair interior/fiber data",
            "codomain_role": "closed-loop public quotient surface",
            "quotient_visible_dimension": quotient_dim,
            "hidden_kernel_dimension": kernel_dim,
            "section": "S: Loop_297 -> TubePair_44521 with P*S=I_297",
        },
        "derivative_reflection": {
            "statement": (
                "Quotient and kernel are complementary first-order readings of the same boundary map: "
                "the quotient records public surface variation, while the kernel records hidden fiber "
                "directions erased by that surface reading."
            ),
            "p_side_role": "public-P/C trace access is quotient-visible boundary dynamics",
            "np_x_side_role": "NP witness/X extractor access is hidden fiber or kernel-sensitive dynamics",
            "reflected_not_identical": True,
            "public_inverse_absent": True,
        },
        "obligations": obligations,
        "decision": {
            "may_claim_quotient_kernel_rolewise_reflection": pass_condition,
            "may_claim_public_quotient_recovers_hidden_kernel": False,
            "may_claim_global_p_not_np_from_this_certificate_alone": False,
            "may_claim_literal_p_not_np_iff_t985": False,
            "reason": (
                "The certified projection has a 297-dimensional quotient, a retained 44,224-dimensional "
                "kernel, a chosen section, and certified kernel-obstructed operations. This supports the "
                "rolewise reflection, not a public inverse or a standalone global separation theorem."
            ),
        },
        "non_claims": [
            "This does not prove a literal P != NP iff T985 equivalence.",
            "This does not make the section canonical evidence that the quotient contains the full kernel.",
            "This does not claim every possible polynomial-time computation has been formalized in a proof assistant.",
            "This does not replace the full no-escape closure ledger or external audit pack.",
        ],
        "next_highest_yield_item": {
            "id": "ball_surface_tensor_bridge_certificate",
            "action": (
                "Promote the ball/surface/raw-tensor dialectical bridge into an adjacent certificate that "
                "names surface, filling, tensor substrate, transport, and residue return roles."
            ),
        },
        "witnessed_against_full_ledger": {
            "full_no_escape_status": ledger.get("status"),
            "may_claim_full_separation_in_repo_model": ledger.get("decision", {}).get(
                "may_claim_full_separation"
            ),
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "QUOTIENT_KERNEL_REFLECTION_CERTIFIED_ROLEWISE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
