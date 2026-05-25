from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.paths import D20_INVARIANTS, DATA


THEOREM_ID = "readout_stack_scope"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CORE_A985 = DATA / "core" / "a985.json"
DERIVED_INVARIANT_REPORTS = D20_INVARIANTS / "derived_invariant_reports.json"
PUBLIC_SHADOW_KERNEL_REPORT = D20_INVARIANTS / "theorems" / "sector_public_shadow_kernel" / "report.json"
IDEMPOTENT_ADMISSIBILITY_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_idempotent_support_admissibility" / "report.json"
)
SECTOR33_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
SUPERSELECTION_REPORT = D20_INVARIANTS / "theorems" / "superselection_flux_balance_extension" / "report.json"
TUBE_PROJECTION_SECTION = DATA / "tube" / "projection_section.json"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


def report_status(path: Path, expected_status: str, all_checks: bool = True) -> dict[str, Any]:
    data = load_json(path)
    passed = data.get("status") == expected_status
    if all_checks:
        passed = passed and data.get("all_checks_pass") is True
    return {
        "path": rel(path),
        "sha256": sha_file(path),
        "status": data.get("status"),
        "expected_status": expected_status,
        "all_checks_pass": data.get("all_checks_pass"),
        "passed": passed,
    }


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
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    core = load_json(CORE_A985)
    derived_reports_text = DERIVED_INVARIANT_REPORTS.read_text(encoding="utf-8")
    public_shadow = load_json(PUBLIC_SHADOW_KERNEL_REPORT)
    idempotent = load_json(IDEMPOTENT_ADMISSIBILITY_REPORT)
    height = load_json(SECTOR33_HEIGHT_TRANSPORT_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    superselection = load_json(SUPERSELECTION_REPORT)
    tube_section = load_json(TUBE_PROJECTION_SECTION)

    quotient_block = core["blocks"]["quotients"]
    terminal_quotients_close = (
        quotient_block.get("q42_classes") == 42
        and quotient_block.get("q12_classes") == 12
        and quotient_block.get("q42_to_q12_consistent") is True
    )
    a236_not_ordinary_quotient = (
        "A236 layer cannot be obtained as an ordinary semisimple central projection/quotient"
        in derived_reports_text
        and "extra representation/fusion functor data" in derived_reports_text
    )
    public_kernel_not_one_dimensional = (
        public_shadow.get("all_checks_pass") is True
        and public_shadow["derived"].get("rank_mod_prime") == 12
        and public_shadow["derived"].get("kernel_dimension") == 27
    )
    idempotent_public_zero_not_unique = (
        idempotent.get("all_checks_pass") is True
        and idempotent["derived"].get("boolean_public_zero_solution_count_including_zero") == 6
    )
    height_transport_derives_residual = (
        height.get("all_checks_pass") is True
        and height["checks"].get("derived_residual_matches_sector_attachment") is True
        and height["checks"].get("corrected_transport_pi33_coefficient_is_edge_derived_residual") is True
    )
    all_residue_transport_global = (
        all_residue.get("all_checks_pass") is True
        and all_residue["checks"].get("basis_active_circuit_matrix_is_height_coherent") is True
        and all_residue["checks"].get("edge_mod2_incidence_is_not_globally_height_coherent") is True
    )
    tube_section_retains_kernel = (
        tube_section["section"].get("projection_section_identity") is True
        and tube_section["projection"].get("projection_kernel_dimension", 0) > 0
    )
    superselection_extends_hidden_fiber = superselection.get("status") == (
        "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED"
    )

    checks = {
        "terminal_quotient_readouts_close": terminal_quotients_close,
        "a236_is_not_ordinary_a985_quotient": a236_not_ordinary_quotient,
        "tube_projection_retains_nontrivial_kernel": tube_section_retains_kernel,
        "public_shadow_kernel_is_not_one_dimensional": public_kernel_not_one_dimensional,
        "public_zero_idempotent_supports_are_not_unique": idempotent_public_zero_not_unique,
        "height_transport_derives_gamma8_residual_from_circuit": height_transport_derives_residual,
        "all_residue_transport_is_height_coherent_but_edge_mod2_is_not": all_residue_transport_global,
        "superselection_extension_tracks_nonprimitive_public_zero_supports": superselection_extends_hidden_fiber,
    }

    report = {
        "schema": "d20.theorem.readout_stack_scope",
        "status": "D20_READOUT_TRANSPORT_STACK_SCOPE_CERTIFIED" if all(checks.values()) else "D20_READOUT_TRANSPORT_STACK_SCOPE_BLOCKED",
        "object": "d20",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The d20 finite interface is not correctly described as a strict quotient tower. "
            "A42 and A12 are terminal quotient readouts of A985, while A236 is native branching/fusion "
            "data and the hidden sector invariants require tube sections, public-shadow kernels, "
            "superselection supports, and height-coherent action-return transport."
        ),
        "definition": {
            "recommended_name": "readout/transport stack",
            "strict_quotient_tower": (
                "A chain in which each level is obtained only as an ordinary algebra quotient of the "
                "previous level."
            ),
            "weakened_stack": (
                "A typed family of functorial readouts, quotient shadows, retained kernels, "
                "sector supports, and intrinsic transports over the same d20 object."
            ),
            "terminal_quotient_readouts": "A985 -> A42 -> A12 closes as stored quotient maps and tensors.",
            "native_branching_readout": "A236 is representation/fusion branching data, not an ordinary A985 central quotient.",
            "intrinsic_transport": height["definition"]["transport"],
        },
        "source_audit": {
            "core_a985": {
                "path": rel(CORE_A985),
                "sha256": sha_file(CORE_A985),
                "q42_classes": quotient_block.get("q42_classes"),
                "q12_classes": quotient_block.get("q12_classes"),
                "q42_to_q12_consistent": quotient_block.get("q42_to_q12_consistent"),
            },
            "derived_invariant_reports": {
                "path": rel(DERIVED_INVARIANT_REPORTS),
                "sha256": sha_file(DERIVED_INVARIANT_REPORTS),
                "contains_a236_obstruction": a236_not_ordinary_quotient,
            },
            "sector_public_shadow_kernel": report_status(
                PUBLIC_SHADOW_KERNEL_REPORT,
                "D20_SECTOR_PUBLIC_SHADOW_KERNEL_CERTIFIED",
            ),
            "sector_idempotent_support_admissibility": report_status(
                IDEMPOTENT_ADMISSIBILITY_REPORT,
                "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED",
            ),
            "sector33_height_coherent_transport": report_status(
                SECTOR33_HEIGHT_TRANSPORT_REPORT,
                "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
            ),
            "sector33_all_residue_height_transport": report_status(
                ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT,
                "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
            ),
            "superselection_flux_balance_extension": report_status(
                SUPERSELECTION_REPORT,
                "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED",
            ),
            "tube_projection_section": {
                "path": rel(TUBE_PROJECTION_SECTION),
                "sha256": sha_file(TUBE_PROJECTION_SECTION),
                "schema": tube_section.get("schema"),
                "projection_section_identity": tube_section["section"].get("projection_section_identity"),
                "projection_kernel_dimension": tube_section["projection"].get("projection_kernel_dimension"),
                "passed": tube_section_retains_kernel,
            },
        },
        "readout_stack": {
            "bulk": {
                "object": "A985",
                "role": "finite generated multiplication body",
                "ordinary_quotient_parent": None,
            },
            "native_a236": {
                "object": "A236",
                "role": "native representation/fusion branching readout",
                "ordinary_quotient_of_A985": False,
            },
            "terminal_quotients": [
                {
                    "object": "A42",
                    "role": "terminal quotient readout",
                    "ordinary_quotient_of_A985": True,
                },
                {
                    "object": "A12",
                    "role": "terminal quotient readout",
                    "ordinary_quotient_of_A42": True,
                },
            ],
            "retained_kernel_data": {
                "closed_loop_quotient_dimension": tube_section["projection"].get(
                    "closed_loop_quotient_dimension"
                ),
                "projection_kernel_dimension": tube_section["projection"].get("projection_kernel_dimension"),
            },
            "public_zero_kernel": {
                "rank_mod_prime": public_shadow["derived"].get("rank_mod_prime"),
                "kernel_dimension": public_shadow["derived"].get("kernel_dimension"),
                "coordinate_axis_public_zero_sectors": public_shadow["derived"].get(
                    "coordinate_axis_public_zero_sectors"
                ),
            },
            "idempotent_admissibility": {
                "boolean_public_zero_solution_count_including_zero": idempotent["derived"].get(
                    "boolean_public_zero_solution_count_including_zero"
                ),
                "interpretation": idempotent.get("interpretation"),
            },
            "height_action_return_transport": {
                "formula": height["definition"]["transport"],
                "gamma8_height_action": height["derived"]["edge_derived_residual"]["height_action"],
                "gamma8_residual_integral": height["derived"]["edge_derived_residual"]["residual_integral"],
                "gamma8_transport_scalar": height["derived"]["edge_derived_residual"]["transport_scalar"],
                "height_transport_vector_sha256": height["derived"]["vectors"]["height_transport"]["sha256"],
                "corrected_transport_vector_sha256": height["derived"]["vectors"]["corrected_transport"]["sha256"],
                "q42_nonzero_count": height["derived"]["public_shadows"]["height_transport_q42"][
                    "nonzero_count"
                ],
                "q12_nonzero_count": height["derived"]["public_shadows"]["height_transport_q12"][
                    "nonzero_count"
                ],
            },
            "superselection_extension": superselection.get("interpretation"),
        },
        "checks": checks,
        "decision": {
            "may_claim_strict_quotient_tower": False,
            "may_claim_terminal_quotient_readouts": terminal_quotients_close,
            "may_claim_weakened_readout_transport_stack": all(checks.values()),
            "reason": (
                "The ordinary quotient statement holds only for the terminal A42/A12 readouts. "
                "A236, kernel retention, public-zero supports, and height-coherent transports carry "
                "additional invariant data outside a strict quotient-only chain."
            ),
        },
        "non_claims": [
            "This does not rewrite the current generated core layer wording; it scopes and supersedes it until the next canonical rebuild.",
            "This does not claim that every public-zero kernel vector is physically admissible.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": (
            "Propagate the readout/transport-stack terminology through the canonical generated artifacts "
            "during the next targeted rebuild, after formatting/layout decisions are fixed."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_outputs(report: dict[str, Any], out_dir: Path = DEFAULT_OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    manifest_path = out_dir / "manifest.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "schema": "d20.theorem.readout_stack_scope.manifest",
        "status": "D20_READOUT_TRANSPORT_STACK_SCOPE_MANIFEST",
        "object": "d20",
        "theorem_id": THEOREM_ID,
        "report": rel(report_path),
        "report_sha256": report["certificate_sha256"],
        "inputs": {
            "core_a985": {"path": rel(CORE_A985), "sha256": sha_file(CORE_A985)},
            "derived_invariant_reports": {
                "path": rel(DERIVED_INVARIANT_REPORTS),
                "sha256": sha_file(DERIVED_INVARIANT_REPORTS),
            },
            "public_shadow_kernel_report": {
                "path": rel(PUBLIC_SHADOW_KERNEL_REPORT),
                "sha256": sha_file(PUBLIC_SHADOW_KERNEL_REPORT),
            },
            "idempotent_admissibility_report": {
                "path": rel(IDEMPOTENT_ADMISSIBILITY_REPORT),
                "sha256": sha_file(IDEMPOTENT_ADMISSIBILITY_REPORT),
            },
            "sector33_height_transport_report": {
                "path": rel(SECTOR33_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(SECTOR33_HEIGHT_TRANSPORT_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "superselection_flux_balance_extension_report": {
                "path": rel(SUPERSELECTION_REPORT),
                "sha256": sha_file(SUPERSELECTION_REPORT),
            },
            "tube_projection_section": {
                "path": rel(TUBE_PROJECTION_SECTION),
                "sha256": sha_file(TUBE_PROJECTION_SECTION),
            },
        },
        "verification_steps": [
            "verify terminal A42/A12 quotient readouts close",
            "verify A236 is not asserted as an ordinary A985 quotient",
            "verify public-zero and idempotent support reports require admissibility constraints",
            "verify rho_33(gamma_8) is derived by height-coherent action-return transport",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)


def main() -> int:
    report = build_theorem()
    write_outputs(report)
    print(report["status"])
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
