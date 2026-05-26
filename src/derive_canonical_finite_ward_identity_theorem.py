from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "canonical_finite_ward_identity"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
)
CANONICAL_FLUX_BALANCE_GAUGE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_flux_balance_gauge" / "report.json"
)
CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_loop_pi33_obstruction" / "report.json"
)

GAMMA8_CYCLE_ID = 8
HEIGHT_ACTION = 374784
PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")


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
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def zero_public_vector() -> dict[str, int]:
    return {component: 0 for component in PUBLIC_COMPONENTS}


def find_cycle8_public_balance(finite_flux: dict[str, Any]) -> dict[str, Any]:
    for row in finite_flux["derived"]["primitive_cycle_balances"]:
        if int(row["cycle_id"]) == GAMMA8_CYCLE_ID:
            return row
    raise ValueError("cycle 8 not found in finite flux balance report")


def sub_public(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    return {component: int(left[component]) - int(right[component]) for component in PUBLIC_COMPONENTS}


def build_theorem() -> dict[str, Any]:
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)
    canonical_gauge = load_json(CANONICAL_FLUX_BALANCE_GAUGE_REPORT)
    canonical_obstruction = load_json(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT)

    cycle8_public = find_cycle8_public_balance(finite_flux)
    q_in = {component: int(cycle8_public["q_in"][component]) for component in PUBLIC_COMPONENTS}
    q_out = {component: int(cycle8_public["q_out"][component]) for component in PUBLIC_COMPONENTS}
    flux = {component: int(cycle8_public["flux_D20"][component]) for component in PUBLIC_COMPONENTS}
    public_exact_gauge_term = sub_public(sub_public(q_out, q_in), flux)

    pi33 = canonical_obstruction["derived"]["pi33_obstruction"]
    bare_terms = {
        key: int(value)
        for key, value in pi33["bare_lambda_coefficients_by_variant"].items()
    }
    bare_pi33_term = int(bare_terms["unweighted"])
    height_corrected_r33_term = int(pi33["height_corrected_coefficient"])
    height_action_term = int(pi33["height_action"])
    scalar_ward_sum = bare_pi33_term + height_corrected_r33_term + height_action_term
    public_scalar_norm = sum(abs(value) for value in public_exact_gauge_term.values())
    total_scalar_balance = public_scalar_norm + scalar_ward_sum
    public_shadow_counts = {
        key: int(value) for key, value in pi33["public_shadow_nonzero_counts"].items()
    }

    checks = {
        "finite_exact_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "canonical_flux_balance_gauge_is_certified": canonical_gauge.get("status")
        == "D20_CANONICAL_FLUX_BALANCE_GAUGE_CERTIFIED"
        and canonical_gauge.get("all_checks_pass") is True,
        "canonical_loop_pi33_obstruction_is_certified": canonical_obstruction.get("status")
        == "D20_CANONICAL_LOOP_PI33_OBSTRUCTION_CERTIFIED"
        and canonical_obstruction.get("all_checks_pass") is True,
        "cycle8_is_canonical_gamma8": int(cycle8_public["cycle_id"]) == GAMMA8_CYCLE_ID
        and cycle8_public["edge_ids"] == [11, 1, 2, 22, 21]
        and canonical_obstruction["derived"]["canonical_boundary_cycle"]["cycle8_edge_ids"]
        == [11, 1, 2, 22, 21],
        "exact_public_flux_gauge_term_is_zero": public_exact_gauge_term == zero_public_vector()
        and q_in == q_out
        and flux == zero_public_vector(),
        "bare_pi33_terms_are_zero": bare_terms
        == {"optical_weighted": 0, "signed_orientation": 0, "unweighted": 0},
        "height_corrected_r33_term_is_negative_height_action": height_corrected_r33_term
        == -HEIGHT_ACTION
        and height_action_term == HEIGHT_ACTION,
        "public_shadows_are_zero": public_shadow_counts == {"q12": 0, "q42": 0},
        "finite_ward_scalar_sum_is_zero": scalar_ward_sum == 0
        and total_scalar_balance == 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CANONICAL_FINITE_WARD_IDENTITY_CERTIFIED"
        if all_checks_pass
        else "D20_CANONICAL_FINITE_WARD_IDENTITY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.canonical_finite_ward_identity",
        "status": status,
        "object": "d20",
        "claim": (
            "In the canonical finite flux-balance gauge, gamma_8 satisfies an explicit finite Ward identity: "
            "the exact public flux gauge term is zero, the bare tube-visible Pi_33 term is zero, and the "
            "height-corrected R33/Pi_33 term is -374784, exactly cancelling the height action +374784."
        ),
        "definition": {
            "public_exact_gauge_term": "Delta Q_public^exact - Flux_D20(gamma_8).",
            "bare_pi33_term": "chi_33^tube(lambda_boundary(gamma_8)).",
            "height_corrected_r33_term": (
                "chi_33^tube(Lambda_hc(gamma_8)), equal to the sector-33/R33 residual."
            ),
            "finite_ward_identity": (
                "|Delta Q_public^exact-Flux_D20|_1 + chi_33(lambda_boundary) + "
                "chi_33(Lambda_hc) + A_h(gamma_8) = 0."
            ),
        },
        "inputs": {
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
            "canonical_flux_balance_gauge_report": {
                "path": rel(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
                "sha256": sha_file(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
            },
            "canonical_loop_pi33_obstruction_report": {
                "path": rel(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT),
                "sha256": sha_file(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT),
            },
        },
        "derived": {
            "cycle": {
                "cycle_id": GAMMA8_CYCLE_ID,
                "edge_ids": cycle8_public["edge_ids"],
                "vertices": cycle8_public["vertices"],
                "canonical_root_vertex": canonical_gauge["derived"]["canonical_marking"][
                    "canonical_root_vertex"
                ],
                "canonical_root_edge": canonical_gauge["derived"]["canonical_marking"][
                    "canonical_root_edge"
                ],
            },
            "public_exact_flux": {
                "q_in": q_in,
                "q_out": q_out,
                "flux_D20": flux,
                "public_exact_gauge_term": public_exact_gauge_term,
                "public_scalar_norm": public_scalar_norm,
            },
            "tube_hidden_terms": {
                "bare_pi33_terms_by_variant": bare_terms,
                "bare_pi33_term_used": bare_pi33_term,
                "height_corrected_r33_term": height_corrected_r33_term,
                "height_action_term": height_action_term,
                "public_shadow_nonzero_counts": public_shadow_counts,
            },
            "ward_identity": {
                "terms": {
                    "public_exact_gauge_scalar": public_scalar_norm,
                    "bare_pi33": bare_pi33_term,
                    "height_corrected_R33": height_corrected_r33_term,
                    "height_action": height_action_term,
                },
                "scalar_sum": scalar_ward_sum,
                "total_scalar_balance": total_scalar_balance,
                "equation": "0 + 0 - 374784 + 374784 = 0",
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the canonical exact public flux term is closed and gauge-fixed",
                "the bare boundary-to-Loop_297 Pi_33 term remains zero",
                "the nonzero physical obstruction is exactly the height-corrected R33/Pi_33 residual",
                "the residual is balanced by the certified finite height action",
            ],
            "what_this_does_not_prove": (
                "This is the gamma_8 finite Ward identity. It does not yet prove the same identity for all "
                "2048 closed-return masks or a continuum Ward identity."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Generalize the canonical Ward identity from gamma_8 to all 2048 closed-return masks using the "
            "global counterterm lattice and all-residue height-coherent transport."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.canonical_finite_ward_identity_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite exact flux balance, canonical gauge, and canonical Loop_297 obstruction inputs",
            "verify the public exact flux gauge term is zero",
            "verify all recorded bare Pi_33 terms are zero",
            "verify the height-corrected R33/Pi_33 term is -374784",
            "verify the finite Ward scalar balance is zero",
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
