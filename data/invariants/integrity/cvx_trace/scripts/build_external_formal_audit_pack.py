from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "external_formal_audit_pack.json"

CORE_REPORTS: dict[str, tuple[Path, str]] = {
    "assignment_bearing_e33_target_family_obligation": (
        CVX / "reports" / "assignment_bearing_e33_target_family_obligation.json",
        "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED",
    ),
    "cnf_to_parameterized_e33_packet_compiler": (
        CVX / "reports" / "cnf_to_parameterized_e33_packet_compiler_certificate.json",
        "CNF_TO_PARAMETERIZED_E33_PACKET_COMPILER_BUILT_REPLAY_CHECKED_FOR_CANARIES_REDUCTION_OPEN",
    ),
    "encoded_family_bridge": (
        CVX / "reports" / "encoded_family_bridge_certificate.json",
        "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
    ),
    "encoded_family_sat_frontier": (
        CVX / "reports" / "encoded_family_sat_frontier_certificate.json",
        "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED",
    ),
    "encoded_family_scope": (
        CVX / "reports" / "encoded_family_scope_certificate.json",
        "ENCODED_FAMILY_SCOPE_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
    ),
    "forall_yes_no_preservation_theorem": (
        CVX / "reports" / "forall_yes_no_preservation_theorem.json",
        "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
    ),
    "formula_to_boundary_cycle_family_candidate": (
        CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json",
        "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
    ),
    "full_no_escape_closure_ledger": (
        CVX / "reports" / "full_no_escape_closure_ledger.json",
        "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED",
    ),
    "parameterized_e33_target_schema": (
        CVX / "reports" / "parameterized_e33_target_schema_certificate.json",
        "PARAMETERIZED_E33_TARGET_SCHEMA_DEFINED_REDUCTION_OPEN",
    ),
    "uniform_cnf_to_e33_family_encoding_investigation": (
        CVX / "reports" / "uniform_cnf_to_e33_family_encoding_investigation.json",
        "UNIFORM_CNF_TO_E33_ENCODING_CERTIFIED_BY_PARAMETERIZED_ASSIGNMENT_TARGET",
    ),
    "universal_pure_c_no_escape": (
        CVX / "reports" / "universal_pure_c_no_escape_report.json",
        "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
    ),
    "universal_trace_compiler": (
        CVX / "reports" / "universal_trace_compiler_report.json",
        "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
    ),
    "universal_trace_typing": (
        CVX / "reports" / "universal_trace_typing_report.json",
        "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
    ),
    "universal_v_wall_crossing_accounting": (
        CVX / "reports" / "universal_v_wall_crossing_accounting_report.json",
        "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS",
    ),
    "universal_x_extractor_isolation": (
        CVX / "reports" / "universal_x_extractor_isolation_report.json",
        "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
    ),
    "x_extractor_frontier": (
        CVX / "reports" / "x_extractor_frontier_certificate.json",
        "X_EXTRACTOR_FRONTIER_EXPLICIT_POLYNOMIAL_FAMILY_EXTRACTOR_PROMOTED",
    ),
    "x_extractor_target": (
        CVX / "reports" / "x_extractor_target_certificate.json",
        "X_EXTRACTOR_TARGET_AND_INTRINSIC_TRANSPORT_CERTIFIED_POLYNOMIAL_LOWER_BOUND_OPEN",
    ),
    "x_policy_boundary": (
        CVX / "reports" / "x_policy_boundary_certificate.json",
        "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
    ),
    "quotient_kernel_reflection": (
        CVX / "reports" / "quotient_kernel_reflection_certificate.json",
        "QUOTIENT_KERNEL_REFLECTION_CERTIFIED_ROLEWISE",
    ),
    "p_not_np_model_scoped_theorem": (
        CVX / "reports" / "p_not_np_model_scoped_theorem.json",
        "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED",
    ),
    "t985_univalent_equivalence_obligation": (
        CVX / "reports" / "t985_univalent_equivalence_obligation.json",
        "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING",
    ),
}

CHECKLIST = BASE / "p_vs_np_bridge_checklist.json"
CVX_INDEX = CVX / "index.json"
DATA_INDEX = ROOT / "data" / "index.json"
TRACE_VALIDATION_REPORT = CVX / "reports" / "cadical_lrat_contradiction_4_validation.json"
LAYER_INPUTS = [
    ROOT / "layers" / "tube" / "projection_section.json",
    ROOT / "layers" / "tube" / "kernel_descent_audit.json",
    ROOT / "layers" / "drinfeld" / "boundary.json",
]

REPLAY_COMMANDS = [
    (
        "finite_target_fence",
        "python data/invariants/integrity/cvx_trace/scripts/build_formula_to_boundary_cycle_family_candidate.py",
        "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
    ),
    (
        "assignment_target_obligation",
        "python data/invariants/integrity/cvx_trace/scripts/build_assignment_bearing_e33_target_family_obligation.py",
        "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED",
    ),
    (
        "parameterized_target_schema",
        "python data/invariants/integrity/cvx_trace/scripts/build_parameterized_e33_target_schema_certificate.py",
        "PARAMETERIZED_E33_TARGET_SCHEMA_DEFINED_REDUCTION_OPEN",
    ),
    (
        "public_packet_compiler",
        "python data/invariants/integrity/cvx_trace/scripts/build_cnf_to_parameterized_e33_packet_compiler_certificate.py",
        "CNF_TO_PARAMETERIZED_E33_PACKET_COMPILER_BUILT_REPLAY_CHECKED_FOR_CANARIES_REDUCTION_OPEN",
    ),
    (
        "forall_yes_no_theorem",
        "python data/invariants/integrity/cvx_trace/scripts/build_forall_yes_no_preservation_theorem.py",
        "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
    ),
    (
        "x_policy_boundary",
        "python data/invariants/integrity/cvx_trace/scripts/build_x_policy_boundary_certificate.py",
        "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
    ),
    (
        "encoded_family_bridge",
        "python data/invariants/integrity/cvx_trace/scripts/build_encoded_family_bridge_certificate.py",
        "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
    ),
    (
        "encoded_family_scope",
        "python data/invariants/integrity/cvx_trace/scripts/build_encoded_family_scope_certificate.py",
        "ENCODED_FAMILY_SCOPE_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
    ),
    (
        "encoded_family_sat_frontier",
        "python data/invariants/integrity/cvx_trace/scripts/build_encoded_family_sat_frontier_certificate.py",
        "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED",
    ),
    (
        "uniform_cnf_to_e33_encoding",
        "python data/invariants/integrity/cvx_trace/scripts/build_uniform_cnf_to_e33_family_encoding_investigation.py",
        "UNIFORM_CNF_TO_E33_ENCODING_CERTIFIED_BY_PARAMETERIZED_ASSIGNMENT_TARGET",
    ),
    (
        "full_no_escape_closure_ledger",
        "python data/invariants/integrity/cvx_trace/scripts/build_full_no_escape_closure_ledger.py",
        "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED",
    ),
    (
        "t985_univalent_equivalence_obligation",
        "python data/invariants/integrity/cvx_trace/scripts/build_t985_univalent_equivalence_obligation.py",
        "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING",
    ),
    (
        "quotient_kernel_reflection",
        "python data/invariants/integrity/cvx_trace/scripts/build_quotient_kernel_reflection_certificate.py",
        "QUOTIENT_KERNEL_REFLECTION_CERTIFIED_ROLEWISE",
    ),
    (
        "p_not_np_model_scoped_theorem",
        "python data/invariants/integrity/cvx_trace/scripts/build_p_not_np_model_scoped_theorem.py",
        "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED",
    ),
    (
        "external_formal_audit_pack",
        "python data/invariants/integrity/cvx_trace/scripts/build_external_formal_audit_pack.py",
        "EXTERNAL_FORMAL_AUDIT_PACK_READY",
    ),
    (
        "cvx_trace_schema_validation",
        "python data/invariants/integrity/cvx_trace/scripts/validate_cvx_trace.py",
        "CVX_TRACE_SCHEMA_VALIDATION_PASS",
    ),
]


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


def report_status(path: Path, expected_status: str) -> dict[str, Any]:
    data = load_json(path)
    status = data.get("status")
    return {
        "path": rel(path),
        "status": status,
        "expected_status": expected_status,
        "passed": status == expected_status,
        "sha256": sha256(path),
    }


def script_path_from_command(command: str) -> Path:
    parts = command.split()
    if len(parts) < 2 or parts[0] != "python":
        raise ValueError(f"unsupported replay command shape: {command}")
    return ROOT / parts[1]


def replay_plan() -> list[dict[str, Any]]:
    rows = []
    for step, command, expected_stdout in REPLAY_COMMANDS:
        script = script_path_from_command(command)
        rows.append(
            {
                "step": step,
                "command": command,
                "expected_stdout": expected_stdout,
                "script": rel(script),
                "script_exists": script.exists(),
                "script_sha256": sha256(script) if script.exists() else None,
            }
        )
    return rows


def hash_manifest(paths: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        rows.append(
            {
                "path": rel(path),
                "exists": path.exists(),
                "sha256": sha256(path) if path.exists() else None,
            }
        )
    return rows


def source_audit() -> dict[str, Any]:
    audit = {key: report_status(path, expected) for key, (path, expected) in CORE_REPORTS.items()}
    audit["bridge_checklist"] = report_status(CHECKLIST, "P_VS_NP_BRIDGE_CHECKLIST_FORMALIZED")
    audit["cvx_trace_validation"] = report_status(TRACE_VALIDATION_REPORT, "CVX_TRACE_SCHEMA_VALIDATION_PASS")
    return audit


def build_report() -> dict[str, Any]:
    audit = source_audit()
    replay = replay_plan()
    ledger = load_json(CORE_REPORTS["full_no_escape_closure_ledger"][0])
    checklist = load_json(CHECKLIST)
    cvx_index = load_json(CVX_INDEX)
    data_index = load_json(DATA_INDEX)
    integrity_required = data_index.get("domains", {}).get("integrity_ladders", {}).get("required_files", [])

    required_artifacts = [
        path
        for path, _expected in CORE_REPORTS.values()
    ] + [
        CHECKLIST,
        CVX_INDEX,
        DATA_INDEX,
        CVX / "schemas" / "parameterized_e33_target.schema.json",
        CVX / "schemas" / "cvx_trace.schema.json",
        CVX / "reports" / "p_not_np_model_scoped_theorem.md",
    ] + LAYER_INPUTS
    manifest = hash_manifest(required_artifacts)

    index_registered = (
        cvx_index.get("external_formal_audit_pack") == "reports/external_formal_audit_pack.json"
        and cvx_index.get("external_formal_audit_pack_builder")
        == "scripts/build_external_formal_audit_pack.py"
        and "cvx_trace/reports/external_formal_audit_pack.json" in integrity_required
        and "cvx_trace/scripts/build_external_formal_audit_pack.py" in integrity_required
    )

    all_sources_pass = all(item["passed"] for item in audit.values())
    all_replay_scripts_present = all(item["script_exists"] for item in replay)
    all_manifest_files_present = all(item["exists"] for item in manifest)
    ledger_closed = ledger.get("decision", {}).get("may_claim_full_separation") is True
    checklist_points_to_review = checklist.get("next_highest_yield_item", {}).get("id") in {
        "external_formal_audit_pack",
        "independent_external_replay",
        "proof_assistant_formalization_or_external_reviewer",
    }
    pass_condition = (
        all_sources_pass
        and all_replay_scripts_present
        and all_manifest_files_present
        and ledger_closed
        and index_registered
        and checklist_points_to_review
    )

    return {
        "schema": "d20.integrity.external_formal_audit_pack.source_drop",
        "status": "EXTERNAL_FORMAL_AUDIT_PACK_READY" if pass_condition else "EXTERNAL_FORMAL_AUDIT_PACK_INCOMPLETE",
        "claim_level": "external_audit_material_packaged_not_externally_validated",
        "purpose": (
            "Freeze the repo-local proof ledger, theorem certificates, and minimal replay commands "
            "for independent external formal audit."
        ),
        "source_audit": audit,
        "artifact_hash_manifest": manifest,
        "minimal_replay_plan": {
            "run_from": rel(ROOT),
            "does_not_require_full_rebuild": True,
            "commands": replay,
        },
        "claim_boundary": {
            "repo_model": "Claims are scoped to the repository's stated C/V/X interface model and certificate semantics.",
            "finite_target_boundary": (
                "The fixed 2048-mask D20 target remains fenced as a finite lookup testbed; "
                "SAT-completeness is carried by the parameterized assignment-witness E(phi) target."
            ),
            "external_status": "This pack is prepared for external audit; it is not itself independent external validation.",
            "non_claims": [
                "This does not claim a proof-assistant formalization has been completed.",
                "This does not claim peer review or independent clean-room replay has already occurred.",
                "This does not make the finite D20 mask fingerprint SAT-preserving.",
            ],
        },
        "registration": {
            "cvx_index_registered": cvx_index.get("external_formal_audit_pack")
            == "reports/external_formal_audit_pack.json",
            "cvx_index_builder_registered": cvx_index.get("external_formal_audit_pack_builder")
            == "scripts/build_external_formal_audit_pack.py",
            "data_index_report_registered": "cvx_trace/reports/external_formal_audit_pack.json"
            in integrity_required,
            "data_index_builder_registered": "cvx_trace/scripts/build_external_formal_audit_pack.py"
            in integrity_required,
            "registered": index_registered,
        },
        "decision": {
            "may_claim_audit_pack_ready": pass_condition,
            "may_claim_external_validation_completed": False,
            "may_claim_full_separation_in_repo_model": ledger_closed,
            "reason": (
                "All audit-pack source reports, artifact hashes, replay commands, and registry entries are present."
                if pass_condition
                else "One or more source reports, replay commands, artifact hashes, or registry entries are missing."
            ),
        },
        "next_highest_yield_item": {
            "id": "independent_external_replay",
            "action": "Run the minimal replay plan in a clean checkout and compare the emitted report hashes.",
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_audit_pack_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
