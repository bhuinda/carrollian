from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
D20 = ROOT / "data" / "invariants" / "d20"
REPORT_PATH = CVX / "reports" / "t985_univalent_equivalence_obligation.json"

T985_CSDO = D20 / "theorems" / "t985_csdo" / "report.json"
PRE_A985 = D20 / "pre_A985_relation_body_theorem.json"
FULL_LEDGER = CVX / "reports" / "full_no_escape_closure_ledger.json"
FORALL_THEOREM = CVX / "reports" / "forall_yes_no_preservation_theorem.json"
CERTIFIED_POINTER = (
    D20
    / "theorems"
    / "certified_pointer_a985_matrix_unit_dereference"
    / "report.json"
)
SUPPORT_RESTRICTED_TABLES = (
    D20
    / "theorems"
    / "tiny_pointer_a985_support_restricted_multiplication_tables"
    / "report.json"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def report_status(path: Path, expected_status: str) -> dict[str, Any]:
    data = load_json(path)
    status = data.get("status")
    return {
        "path": rel(path),
        "status": status,
        "expected_status": expected_status,
        "passed": status == expected_status,
    }


def formal_proof_files() -> list[str]:
    suffixes = {".lean", ".agda", ".v", ".coq", ".idr"}
    ignored_parts = {".git", ".venv", ".replay_tmp", "generated"}
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        files.append(rel(path))
    return sorted(files)


def build_report() -> dict[str, Any]:
    t985 = load_json(T985_CSDO)
    ledger = load_json(FULL_LEDGER)
    certified_pointer = load_json(CERTIFIED_POINTER)
    support_tables = load_json(SUPPORT_RESTRICTED_TABLES)
    proof_files = formal_proof_files()

    t985_certified = t985.get("status") == "T985_CSDO_THEOREM_INPUTS_CERTIFIED"
    repo_forward_closed = ledger.get("decision", {}).get("may_claim_full_separation") is True
    uf_formal_layer_present = bool(proof_files)

    obligations = {
        "p_not_np_as_univalent_hprop_defined": {
            "passed": False,
            "evidence": None,
            "needed": "A proof-assistant or HoTT/UF definition of the proposition P != NP as an hProp.",
        },
        "t985_as_univalent_hprop_defined": {
            "passed": False,
            "evidence": {
                "t985_certificate_status": t985.get("status"),
                "raw_tensor_hash": t985.get("file_hashes", {}).get("data/raw/T_985.npz"),
            },
            "needed": (
                "A formal hProp such as T985Certified, not just a finite tensor file and JSON certificate."
            ),
        },
        "forward_map_t985_to_p_not_np": {
            "passed": repo_forward_closed,
            "evidence": {
                "scope": "repo-local T985/CVX model, not standalone UF",
                "ledger_status": ledger.get("status"),
            },
            "needed": "For UF equivalence, recast the repo-local implication as a formal map T985Certified -> PneqNP.",
        },
        "backward_map_p_not_np_to_t985": {
            "passed": False,
            "evidence": None,
            "needed": (
                "A theorem showing any proof or truth of P != NP forces this T985 object, or an equivalent "
                "T985Certified hProp. The repo has no necessity or uniqueness theorem of that kind."
            ),
        },
        "tiny_pointer_dereference_certified": {
            "passed": certified_pointer.get("status")
            == "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_CERTIFIED",
            "evidence": {
                "certified_pointer_status": certified_pointer.get("status"),
                "claim": certified_pointer.get("claim"),
                "finite_defect_count": certified_pointer.get("derived", {}).get("finite_defect_count"),
                "open_boundary_count": certified_pointer.get("derived", {}).get("open_boundary_count"),
            },
            "needed": "A certified tiny-pointer dereference layer into A985 matrix-unit coordinates.",
        },
        "tiny_pointer_is_conditional_on_a985_t985": {
            "passed": support_tables.get("inputs", {}).get("t985_tensor", {}).get("path")
            == "data/raw/T_985.npz",
            "evidence": {
                "pointer_native_support": certified_pointer.get("source", {}).get("native_support"),
                "address_space_support": certified_pointer.get("address_space", {}).get("support"),
                "address_space_basis_size": certified_pointer.get("address_space", {}).get("basis_size"),
                "support_tables_t985_input": support_tables.get("inputs", {}).get("t985_tensor"),
            },
            "needed": (
                "For a backward map, the tiny pointer would need to construct T985Certified from PneqNP, "
                "not dereference coordinates using A985/T985-backed inputs."
            ),
        },
        "tiny_pointer_supplies_backward_map": {
            "passed": False,
            "evidence": {
                "why_not": (
                    "The tiny pointer certifies a dereference from legacy/public support labels into raw "
                    "A985 orbital matrix-unit coordinates. Its own support-restricted multiplication layer "
                    "reads data/raw/T_985.npz. That is an internal address/reconstruction certificate, not "
                    "a necessity theorem PneqNP -> T985Certified."
                )
            },
            "needed": (
                "A proof that any hProp proof of P != NP determines the tiny pointer and thereby determines "
                "T985Certified, without assuming A985/T985 as an input surface."
            ),
        },
        "univalence_turns_equivalence_into_path": {
            "passed": False,
            "evidence": {
                "reason": (
                    "Univalence can identify equivalent types, and for hProps a path is equivalent to logical "
                    "equivalence, but it does not supply the two implication maps."
                )
            },
            "needed": "First prove both hProp maps; only then can univalence/propositional extensionality package them.",
        },
        "formal_uf_proof_artifact_present": {
            "passed": uf_formal_layer_present,
            "evidence": {"formal_files": proof_files},
            "needed": "A Lean/Coq/Agda/HoTT artifact carrying the definitions and maps.",
        },
    }

    backward_missing = obligations["backward_map_p_not_np_to_t985"]["passed"] is False
    pass_condition = all(item["passed"] for item in obligations.values())

    return {
        "schema": "d20.integrity.t985_univalent_equivalence_obligation.source_drop",
        "status": (
            "T985_UNIVALENT_EQUIVALENCE_CERTIFIED"
            if pass_condition
            else "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING"
        ),
        "claim_level": "equivalence_obligation_not_proved",
        "source_audit": {
            "t985_csdo": report_status(T985_CSDO, "T985_CSDO_THEOREM_INPUTS_CERTIFIED"),
            "pre_a985_relation_body": report_status(
                PRE_A985,
                "PRE_A985_RELATION_BODY_DERIVED_WITHOUT_RELATION_TABLE_PASS",
            ),
            "forall_yes_no_preservation_theorem": report_status(
                FORALL_THEOREM,
                "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
            ),
            "full_no_escape_closure_ledger": report_status(
                FULL_LEDGER,
                "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED",
            ),
            "certified_pointer_a985_matrix_unit_dereference": report_status(
                CERTIFIED_POINTER,
                "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_CERTIFIED",
            ),
            "tiny_pointer_a985_support_restricted_multiplication_tables": report_status(
                SUPPORT_RESTRICTED_TABLES,
                "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_CERTIFIED",
            ),
        },
        "univalent_form": {
            "candidate_proposition_left": "PneqNP : hProp",
            "candidate_proposition_right": "T985Certified : hProp",
            "target_statement": "PneqNP <-> T985Certified, equivalently PneqNP = T985Certified for hProps under univalence/propositional extensionality.",
            "required_maps": [
                "T985Certified -> PneqNP",
                "PneqNP -> T985Certified",
            ],
        },
        "obligations": obligations,
        "decision": {
            "may_claim_t985_sufficient_for_repo_model_full_separation": t985_certified and repo_forward_closed,
            "may_claim_univalent_p_not_np_iff_t985": pass_condition,
            "may_claim_p_not_np_implies_t985": False,
            "may_claim_t985_necessary_for_any_p_not_np_proof": False,
            "reason": (
                "The repo has a replayed T985-backed route to the model-scoped separation claim, but no "
                "formal hProp definitions and no backward map from P != NP to T985Certified."
            ),
        },
        "non_claims": [
            "This does not refute the repo-local T985/CVX separation chain.",
            "This does not prove T985 is unnecessary.",
            "This does not prove P != NP iff T985.",
            "Univalence alone does not create the missing backward implication.",
        ],
        "blocker": {
            "id": "p_not_np_to_t985_backward_map",
            "active": backward_missing,
            "description": (
                "To prove logical equivalence, construct a formal map from the proposition P != NP to "
                "T985Certified. The tiny-pointer layer helps inside A985/T985, but currently assumes that "
                "address space rather than deriving it from P != NP."
            ),
        },
        "next_highest_yield_item": {
            "id": "formalize_hprops_and_backward_map_or_drop_iff",
            "action": "Define PneqNP and T985Certified as hProps in a proof assistant, then either prove the backward map or record the claim as one-way sufficiency.",
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
