from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, ROOT
from src.derive_sector33_boundary_annihilation_theorem import (
    FIELD_PRIME,
    multiply,
    regular_trace_coefficients,
    signed_mod,
    vec_digest,
)


THEOREM_ID = "sector33_residual_lift"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
ANNIHILATION_REPORT = D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
SECTOR_ATTACHMENT_REPORT = D20_INVARIANTS / "theorems" / "sector33_residual_attachment" / "report.json"
NONEXACT_REPORT = D20_INVARIANTS / "theorems" / "nonexact_optical_residue" / "report.json"
RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
QUOTIENT_NPZ = ROOT / "data" / "raw" / "quotients.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"


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


def vector_from_entries(entries: list[list[int]], relation_count: int) -> np.ndarray:
    vec = np.zeros(relation_count, dtype=np.int64)
    for index, value in entries:
        vec[int(index)] = int(value) % FIELD_PRIME
    return vec


def quotient_shadow(vec: np.ndarray, qmap: np.ndarray, size: int) -> dict[str, Any]:
    out = np.zeros(size, dtype=np.int64)
    np.add.at(out, qmap.astype(np.int64), vec % FIELD_PRIME)
    out %= FIELD_PRIME
    entries = [[int(i), int(out[i])] for i in np.nonzero(out)[0]]
    return {
        "nonzero_count": len(entries),
        "sha256": hashlib.sha256(canonical(entries)).hexdigest(),
        "entries": entries,
    }


def character_evaluation(
    triples: np.ndarray,
    trace_coeff: np.ndarray,
    idempotent: np.ndarray,
    vector: np.ndarray,
    dimension: int,
) -> dict[str, Any]:
    action = multiply(triples, idempotent, vector)
    trace_value = int((trace_coeff @ action) % FIELD_PRIME)
    coefficient = int((trace_value * pow(int(dimension), -1, FIELD_PRIME)) % FIELD_PRIME)
    return {
        "action": vec_digest(action),
        "regular_trace": trace_value,
        "coefficient_mod_prime": coefficient,
        "coefficient_signed": signed_mod(coefficient),
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
        index = json.loads(index_path.read_text(encoding="utf-8"))
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
    boundary = load_json(BOUNDARY_TO_LOOP_REPORT)
    annihilation = load_json(ANNIHILATION_REPORT)
    attachment = load_json(SECTOR_ATTACHMENT_REPORT)
    nonexact = load_json(NONEXACT_REPORT)

    relation_count = int(np.load(RELATION_NPZ)["block_i"].shape[0])
    quotients = np.load(QUOTIENT_NPZ)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    trace_coeff = regular_trace_coefficients(triples, relation_count)

    e33_entries = annihilation["derived"]["sector33_tube_idempotent"]["vector"]["entries"]
    e33 = vector_from_entries(e33_entries, relation_count)
    lambda_entries = boundary["derived"]["cycle8_lift"]["vector"]["entries"]
    lambda_gamma8 = vector_from_entries(lambda_entries, relation_count)

    sector_interface = attachment["derived"]["sector_attachment"]
    residual_mod = int(sector_interface["residual_mod_prime"])
    residual_signed = int(sector_interface["residual_integral"])
    dimension = int(annihilation["derived"]["sector33_profile"]["block_dimension"])
    inverse_dimension = pow(dimension, -1, FIELD_PRIME)
    residual_scalar = (residual_mod * inverse_dimension) % FIELD_PRIME
    residual_lift = (residual_scalar * e33) % FIELD_PRIME
    corrected_lift = (lambda_gamma8 + residual_lift) % FIELD_PRIME

    chi_e33 = character_evaluation(triples, trace_coeff, e33, e33, dimension)
    chi_lambda = character_evaluation(triples, trace_coeff, e33, lambda_gamma8, dimension)
    chi_residual = character_evaluation(triples, trace_coeff, e33, residual_lift, dimension)
    chi_corrected = character_evaluation(triples, trace_coeff, e33, corrected_lift, dimension)

    q42_shadow = quotient_shadow(residual_lift, np.asarray(quotients["q42_map"], dtype=np.int64), 42)
    q12_shadow = quotient_shadow(residual_lift, np.asarray(quotients["q12_map"], dtype=np.int64), 12)

    checks = {
        "boundary_to_loop_is_certified": boundary.get("status") == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary.get("all_checks_pass") is True,
        "sector33_annihilation_is_certified": annihilation.get("status")
        == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True,
        "sector33_attachment_is_certified": attachment.get("status")
        == "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED"
        and attachment.get("all_checks_pass") is True,
        "nonexact_residual_matches_cycle8": nonexact["derived"]["first_forced_nonzero_residual"][
            "basis_cycle_ids"
        ]
        == [8]
        and int(nonexact["derived"]["first_forced_nonzero_residual"]["forced_res_A985_optical"])
        == residual_signed,
        "bare_lambda_pi33_coefficient_is_zero": chi_lambda["coefficient_mod_prime"] == 0,
        "chi33_of_e33_equals_sector_dimension": chi_e33["coefficient_mod_prime"] == dimension,
        "residual_scalar_is_dimension_normalized": (residual_scalar * dimension) % FIELD_PRIME == residual_mod,
        "residual_lift_pi33_coefficient_is_residual": chi_residual["coefficient_mod_prime"] == residual_mod
        and chi_residual["coefficient_signed"] == residual_signed,
        "corrected_lift_pi33_coefficient_is_residual": chi_corrected["coefficient_mod_prime"] == residual_mod
        and chi_corrected["coefficient_signed"] == residual_signed,
        "residual_lift_has_zero_q42_shadow": q42_shadow["nonzero_count"] == 0,
        "residual_lift_has_zero_q12_shadow": q12_shadow["nonzero_count"] == 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR33_RESIDUAL_LIFT_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR33_RESIDUAL_LIFT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector33_residual_lift.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The bare structural lift lambda_boundary(gamma_8) has zero Pi_33 tube coefficient, but the "
            "dimension-normalized hidden lift (Res_A985^opt(gamma_8)/dim(Pi_33)) e_33 has Pi_33 coefficient "
            "equal to the certified residual -374784 and has zero A42/A12 public shadow."
        ),
        "definition": {
            "residual_lift": "rho_33(gamma_8) = (Res_A985^opt(gamma_8) / dim(Pi_33)) e_33 in Loop_297.",
            "corrected_lift": "Lambda_33(gamma_8) = lambda_boundary(gamma_8) + rho_33(gamma_8).",
            "normalization": "chi_33^tube(e_33)=dim(Pi_33), so chi_33^tube(rho_33)=Res_A985^opt.",
        },
        "inputs": {
            "boundary_to_loop_report": {
                "path": rel(BOUNDARY_TO_LOOP_REPORT),
                "sha256": sha_file(BOUNDARY_TO_LOOP_REPORT),
            },
            "sector33_boundary_annihilation_report": {
                "path": rel(ANNIHILATION_REPORT),
                "sha256": sha_file(ANNIHILATION_REPORT),
            },
            "sector33_residual_attachment_report": {
                "path": rel(SECTOR_ATTACHMENT_REPORT),
                "sha256": sha_file(SECTOR_ATTACHMENT_REPORT),
            },
            "nonexact_optical_residue_report": {
                "path": rel(NONEXACT_REPORT),
                "sha256": sha_file(NONEXACT_REPORT),
            },
            "relation_memberships": {
                "path": rel(RELATION_NPZ),
                "sha256": sha_file(RELATION_NPZ),
            },
            "quotients": {
                "path": rel(QUOTIENT_NPZ),
                "sha256": sha_file(QUOTIENT_NPZ),
            },
            "t985_tensor": {
                "path": rel(TENSOR_NPZ),
                "sha256": sha_file(TENSOR_NPZ),
            },
        },
        "derived": {
            "cycle_id": 8,
            "sector": 33,
            "field_prime": FIELD_PRIME,
            "residual": {
                "integral": residual_signed,
                "mod_prime": residual_mod,
                "dimension": dimension,
                "inverse_dimension": inverse_dimension,
                "residual_lift_scalar": residual_scalar,
                "residual_lift_scalar_signed": signed_mod(residual_scalar),
            },
            "vectors": {
                "lambda_boundary_gamma8": vec_digest(lambda_gamma8),
                "e33": vec_digest(e33),
                "residual_lift": vec_digest(residual_lift),
                "corrected_lift": vec_digest(corrected_lift),
            },
            "pi33_tube_character": {
                "e33": chi_e33,
                "lambda_boundary_gamma8": chi_lambda,
                "residual_lift": chi_residual,
                "corrected_lift": chi_corrected,
            },
            "public_shadows": {
                "residual_lift_q42": q42_shadow,
                "residual_lift_q12": q12_shadow,
            },
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Replace this normalized residual injection with an intrinsic height-coherent transport rule "
            "that derives rho_33(gamma) from edge/circuit data rather than inserting the certified residual scalar."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector33_residual_lift_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the bare lambda_boundary gamma_8 lift has zero Pi_33 coefficient",
            "verify chi_33(e_33)=dim(Pi_33)",
            "normalize the certified optical residual by dim(Pi_33)",
            "verify the residual lift has Pi_33 coefficient -374784",
            "verify the residual lift has zero A42 and A12 shadows",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
