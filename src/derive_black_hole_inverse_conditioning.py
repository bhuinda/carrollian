from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "black_hole_inverse_conditioning"
STATUS_PASS = "D20_BLACK_HOLE_INVERSE_CONDITIONING_CERTIFIED"
STATUS_REVIEW = "D20_BLACK_HOLE_INVERSE_CONDITIONING_NEEDS_REVIEW"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
CERTIFIED_EVIDENCE = D20_INVARIANTS / "certified_evidence_invariants.json"


def canonical(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


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


def certified_evidence_base_payload(source: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(source))
    pole_packet = (
        payload.get("black_hole_certified_simulator", {})
        .get("pole_packet", {})
    )
    if isinstance(pole_packet, dict):
        pole_packet.pop("conditioning_certificate", None)
    return payload


def certified_evidence_base_sha256(source: dict[str, Any]) -> str:
    return sha_json(certified_evidence_base_payload(source))


def forward_state(state: np.ndarray) -> np.ndarray:
    M, a, Q = (float(x) for x in state)
    discriminant = M * M - a * a - Q * Q
    if discriminant <= 0:
        raise ValueError("state is not subextremal")
    sqrt_disc = math.sqrt(discriminant)
    r_plus = M + sqrt_disc
    r_minus = M - sqrt_disc
    R = r_plus * r_plus + a * a
    T = (r_plus - r_minus) / (4.0 * math.pi * R)
    return np.array(
        [
            math.log(R),
            math.log(T),
            a / R,
            Q * r_plus / R,
        ],
        dtype=np.float64,
    )


def inverse_pole(pole: np.ndarray) -> np.ndarray:
    log_R, log_T, omega, phi = (float(x) for x in pole)
    R = math.exp(log_R)
    T = math.exp(log_T)
    a = omega * R
    radial_square = R - a * a
    if radial_square <= 0:
        raise ValueError("pole packet has no real r_plus")
    r_plus = math.sqrt(radial_square)
    Q = phi * R / r_plus
    delta = 4.0 * math.pi * T * R
    half_delta = delta / 2.0
    M_radial = r_plus - half_delta
    constraint_square = a * a + Q * Q + half_delta * half_delta
    if constraint_square <= 0:
        raise ValueError("pole packet has no real mass constraint")
    M_constraint = math.sqrt(constraint_square)
    M = (M_radial + M_constraint) / 2.0
    return np.array([M, a, Q], dtype=np.float64)


def state_from_polar(M: float, rho: float, theta: float) -> np.ndarray:
    radius = rho * M
    return np.array(
        [M, radius * math.cos(theta), radius * math.sin(theta)], dtype=np.float64
    )


def central_difference(
    value: np.ndarray,
    column: int,
    func: Any,
    h0: float,
    *,
    min_h: float = 1e-13,
) -> np.ndarray:
    h = h0
    while h >= min_h:
        plus = value.copy()
        minus = value.copy()
        plus[column] += h
        minus[column] -= h
        try:
            fp = func(plus)
            fm = func(minus)
        except (ValueError, OverflowError):
            h *= 0.1
            continue
        if np.all(np.isfinite(fp)) and np.all(np.isfinite(fm)):
            return (fp - fm) / (2.0 * h)
        h *= 0.1
    raise ValueError("could not compute stable finite difference")


def inverse_jacobian(pole: np.ndarray) -> np.ndarray:
    cols = [
        central_difference(pole, i, inverse_pole, 1e-7, min_h=1e-14)
        for i in range(4)
    ]
    return np.column_stack(cols)


def forward_jacobian(state: np.ndarray) -> np.ndarray:
    cols = []
    for i in range(3):
        h0 = max(abs(float(state[i])), 1.0) * 1e-6
        cols.append(central_difference(state, i, forward_state, h0, min_h=1e-14))
    return np.column_stack(cols)


def singular_summary(matrix: np.ndarray) -> dict[str, Any]:
    s = np.linalg.svd(matrix, compute_uv=False)
    smallest = float(s[-1])
    largest = float(s[0])
    return {
        "operator_norm": largest,
        "smallest_singular_value": smallest,
        "condition_number": float(largest / smallest) if smallest > 0 else math.inf,
    }


def case_metrics(case_id: str, family: str, state: np.ndarray) -> dict[str, Any]:
    pole = forward_state(state)
    recovered = inverse_pole(pole)
    repole = forward_state(recovered)
    state_error = np.abs(recovered - state)
    pole_residual = repole - pole
    inv_summary = singular_summary(inverse_jacobian(pole))
    fwd_summary = singular_summary(forward_jacobian(state))
    discriminant = float(state[0] * state[0] - state[1] * state[1] - state[2] * state[2])
    extremality_ratio = float(math.sqrt(state[1] * state[1] + state[2] * state[2]) / state[0])
    return {
        "case_id": case_id,
        "family": family,
        "state": {
            "M": float(state[0]),
            "a": float(state[1]),
            "Q": float(state[2]),
            "discriminant": discriminant,
            "extremality_ratio": extremality_ratio,
        },
        "pole": {
            "log_R": float(pole[0]),
            "log_T": float(pole[1]),
            "omega_H": float(pole[2]),
            "phi_H": float(pole[3]),
        },
        "roundtrip": {
            "max_abs_state_error": float(np.max(state_error)),
            "pole_residual_norm": float(np.linalg.norm(pole_residual)),
            "M_abs_error": float(state_error[0]),
            "a_abs_error": float(state_error[1]),
            "Q_abs_error": float(state_error[2]),
        },
        "inverse_jacobian": inv_summary,
        "forward_jacobian": fwd_summary,
    }


def summarize_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    def max_by(path: tuple[str, ...]) -> tuple[float, dict[str, Any]]:
        best_value = -math.inf
        best_case: dict[str, Any] = {}
        for case in cases:
            value: Any = case
            for key in path:
                value = value[key]
            value = float(value)
            if value > best_value:
                best_value = value
                best_case = case
        return best_value, best_case

    max_state_error, state_case = max_by(("roundtrip", "max_abs_state_error"))
    max_pole_residual, pole_case = max_by(("roundtrip", "pole_residual_norm"))
    max_inv_norm, inv_case = max_by(("inverse_jacobian", "operator_norm"))
    max_inv_cond, inv_cond_case = max_by(("inverse_jacobian", "condition_number"))
    max_fwd_cond, fwd_cond_case = max_by(("forward_jacobian", "condition_number"))
    return {
        "sample_count": len(cases),
        "max_abs_state_error": max_state_error,
        "max_abs_state_error_case": state_case.get("case_id"),
        "max_pole_residual_norm": max_pole_residual,
        "max_pole_residual_case": pole_case.get("case_id"),
        "inverse_operator_norm_max": max_inv_norm,
        "inverse_operator_norm_case": inv_case.get("case_id"),
        "inverse_condition_number_max": max_inv_cond,
        "inverse_condition_number_case": inv_cond_case.get("case_id"),
        "forward_condition_number_max": max_fwd_cond,
        "forward_condition_number_case": fwd_cond_case.get("case_id"),
    }


def build_samples() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = np.random.default_rng(20260524)
    interior: list[dict[str, Any]] = []
    for i in range(64):
        M = float(rng.uniform(0.8, 2.4))
        rho = float(rng.uniform(0.02, 0.75))
        theta = float(rng.uniform(0.08, 1.35))
        interior.append(case_metrics(f"interior_{i:03d}", "interior", state_from_polar(M, rho, theta)))

    near_extremal: list[dict[str, Any]] = []
    gaps = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10]
    thetas = [0.2, 0.9, 1.25]
    masses = [1.0, 1.4]
    for M in masses:
        for theta in thetas:
            for gap in gaps:
                rho = 1.0 - gap
                case_id = f"near_M{M:g}_theta{theta:g}_gap{gap:.0e}"
                near_extremal.append(
                    case_metrics(case_id, "near_extremal", state_from_polar(M, rho, theta))
                )
    return interior, near_extremal


def noise_projection_cases(
    anchors: list[dict[str, Any]], *, samples_per_anchor: int = 6
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(20260525)
    levels = [1e-12, 1e-10, 1e-8, 1e-6]
    rows: list[dict[str, Any]] = []
    for anchor_index, anchor in enumerate(anchors):
        state = np.array(
            [anchor["state"]["M"], anchor["state"]["a"], anchor["state"]["Q"]],
            dtype=np.float64,
        )
        pole = forward_state(state)
        for level in levels:
            for sample_index in range(samples_per_anchor):
                direction = rng.normal(size=4)
                direction /= np.linalg.norm(direction)
                noise = direction * level
                noisy_pole = pole + noise
                recovered = inverse_pole(noisy_pole)
                state_delta = recovered - state
                try:
                    projected_pole = forward_state(recovered)
                    projection_residual = projected_pole - noisy_pole
                    projection_valid = True
                    projection_residual_norm: float | None = float(
                        np.linalg.norm(projection_residual)
                    )
                    projection_residual_over_noise: float | None = float(
                        np.linalg.norm(projection_residual) / np.linalg.norm(noise)
                    )
                except ValueError:
                    projection_valid = False
                    projection_residual_norm = None
                    projection_residual_over_noise = None
                rows.append(
                    {
                        "anchor_case_id": anchor["case_id"],
                        "anchor_family": anchor["family"],
                        "level": level,
                        "sample_index": sample_index,
                        "noise_norm": float(np.linalg.norm(noise)),
                        "state_delta_norm": float(np.linalg.norm(state_delta)),
                        "projection_valid": projection_valid,
                        "projection_residual_norm": projection_residual_norm,
                        "amplification": float(np.linalg.norm(state_delta) / np.linalg.norm(noise)),
                        "projection_residual_over_noise": projection_residual_over_noise,
                    }
                )
    return rows


def summarize_noise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_level: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = f"{row['level']:.0e}"
        group = by_level.setdefault(
            key,
            {
                "sample_count": 0,
                "invalid_projection_count": 0,
                "max_amplification": 0.0,
                "max_projection_residual_norm": 0.0,
                "max_projection_residual_over_noise": 0.0,
            },
        )
        group["sample_count"] += 1
        group["invalid_projection_count"] += int(row["projection_valid"] is False)
        group["max_amplification"] = max(group["max_amplification"], row["amplification"])
        if row["projection_residual_norm"] is not None:
            group["max_projection_residual_norm"] = max(
                group["max_projection_residual_norm"], row["projection_residual_norm"]
            )
        if row["projection_residual_over_noise"] is not None:
            group["max_projection_residual_over_noise"] = max(
                group["max_projection_residual_over_noise"],
                row["projection_residual_over_noise"],
            )
    valid_rows = [row for row in rows if row["projection_residual_norm"] is not None]
    return {
        "sample_count": len(rows),
        "invalid_projection_count": sum(1 for row in rows if row["projection_valid"] is False),
        "max_amplification": max(row["amplification"] for row in rows),
        "max_projection_residual_norm": max(
            (row["projection_residual_norm"] for row in valid_rows), default=0.0
        ),
        "max_projection_residual_over_noise": max(
            (row["projection_residual_over_noise"] for row in valid_rows), default=0.0
        ),
        "by_level": by_level,
    }


def finite_tree(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    return True


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


def build_theorem() -> dict[str, Any]:
    source = load_json(CERTIFIED_EVIDENCE)
    bh = source["black_hole_certified_simulator"]
    interior_cases, near_cases = build_samples()
    interior_summary = summarize_cases(interior_cases)
    near_summary = summarize_cases(near_cases)
    anchors = interior_cases[:4] + near_cases[-6:]
    noise_rows = noise_projection_cases(anchors)
    noise_summary = summarize_noise(noise_rows)

    checks = {
        "source_inverse_precision_is_certified": bh["checks"].get("exact_inverse_precision_ok") is True,
        "interior_roundtrip_machine_precision": interior_summary["max_abs_state_error"] < 1e-12,
        "near_extremal_roundtrip_bounded": near_summary["max_abs_state_error"] < 1e-7,
        "near_extremal_conditioning_detected": near_summary["forward_condition_number_max"]
        > interior_summary["forward_condition_number_max"] * 1000.0,
        "noise_projection_detects_inconsistent_poles": noise_summary[
            "max_projection_residual_over_noise"
        ]
        > 0.01
        or noise_summary["invalid_projection_count"] > 0,
    }
    report_body = {
        "schema": "d20.black_hole.inverse_conditioning",
        "status": STATUS_PASS if all(checks.values()) else STATUS_REVIEW,
        "object": "d20",
        "claim": (
            "The Kerr-Newman pole packet y=(log R, log T, omega_H, phi_H) is a "
            "machine-precision inverse coordinate witness for ordinary subextremal states, "
            "and its repair residual is exploitable as a conditioning and inconsistent-pole detector."
        ),
        "definition": {
            "forward": "x=(M,a,Q) -> y=(log(r_+^2+a^2), log T, a/R, Q r_+/R)",
            "inverse": "R=exp(y0), T=exp(y1), a=omega R, r_+=sqrt(R-a^2), Q=phi R/r_+, M repaired from radial and constraint equations",
            "projection_residual": "||forward(inverse(y_noisy))-y_noisy||_2",
            "scope": "double-precision conditioning certificate for the certified simulator, not a numerical-relativity PDE theorem",
        },
        "input_witness": {
            "path": rel(CERTIFIED_EVIDENCE),
            "base_payload_sha256_without_conditioning_certificate": certified_evidence_base_sha256(source),
            "black_hole_status": bh.get("status"),
            "source_exact_inverse_audit": bh.get("pole_packet", {}).get("exact_inverse_audit"),
        },
        "sample_design": {
            "rng_seeds": {
                "interior": 20260524,
                "noise_projection": 20260525,
            },
            "interior_samples": len(interior_cases),
            "near_extremal_samples": len(near_cases),
            "noise_projection_samples": len(noise_rows),
            "near_extremal_gaps": ["1e-2", "1e-4", "1e-6", "1e-8", "1e-10"],
            "noise_levels": ["1e-12", "1e-10", "1e-8", "1e-6"],
        },
        "derived": {
            "interior": interior_summary,
            "near_extremal": near_summary,
            "near_over_interior_inverse_operator_norm_ratio": (
                near_summary["inverse_operator_norm_max"]
                / interior_summary["inverse_operator_norm_max"]
            ),
            "near_over_interior_forward_condition_ratio": (
                near_summary["forward_condition_number_max"]
                / interior_summary["forward_condition_number_max"]
            ),
            "noise_projection": noise_summary,
            "worst_cases": {
                "interior_by_inverse_norm": max(
                    interior_cases,
                    key=lambda case: case["inverse_jacobian"]["operator_norm"],
                ),
                "near_extremal_by_inverse_norm": max(
                    near_cases,
                    key=lambda case: case["inverse_jacobian"]["operator_norm"],
                ),
                "noise_by_projection_residual": max(
                    noise_rows,
                    key=lambda row: row["projection_residual_norm"] or 0.0,
                ),
            },
        },
        "checks": checks,
        "all_checks_pass": False,
        "exploitability": [
            "coordinate witness: reconstruct (M,a,Q) directly from y without an optimizer",
            "roundtrip gate: reject or quarantine pole packets with residual above tolerance",
            "conditioning alarm: near-extremal states show much larger inverse sensitivity",
            "repair map: noisy four-coordinate packets project back to the three-parameter Kerr-Newman surface",
        ],
        "non_claims": [
            "does not identify the simulator with a physical black-hole PDE solver",
            "does not remove near-extremal conditioning risk",
            "does not prove a theorem about arbitrary external coordinates",
        ],
        "next_highest_yield_item": (
            "Use the projection residual as a score in generated pole-packet searches and record "
            "which perturbation directions are tangent versus normal to the Kerr-Newman surface."
        ),
    }
    checks["all_values_finite"] = finite_tree(report_body)
    report_body["all_checks_pass"] = all(checks.values())
    report_body["status"] = STATUS_PASS if report_body["all_checks_pass"] else STATUS_REVIEW
    report_body["certificate_sha256"] = sha_json(
        {k: v for k, v in report_body.items() if k != "certificate_sha256"}
    )
    return report_body


def certified_pointer(report: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    report_path = out_dir / "report.json"
    return {
        "path": rel(report_path),
        "sha256": sha_file(report_path),
        "status": report["status"],
        "sample_count": report["sample_design"]["interior_samples"]
        + report["sample_design"]["near_extremal_samples"]
        + report["sample_design"]["noise_projection_samples"],
        "interior_max_abs_state_error": report["derived"]["interior"]["max_abs_state_error"],
        "near_extremal_max_abs_state_error": report["derived"]["near_extremal"][
            "max_abs_state_error"
        ],
        "near_over_interior_inverse_operator_norm_ratio": report["derived"][
            "near_over_interior_inverse_operator_norm_ratio"
        ],
        "near_over_interior_forward_condition_ratio": report["derived"][
            "near_over_interior_forward_condition_ratio"
        ],
        "noise_projection_residual_over_noise_max": report["derived"]["noise_projection"][
            "max_projection_residual_over_noise"
        ],
        "use": "roundtrip and projection-residual gate for pole-packet integrity",
    }


def refresh_certified_evidence_pointer(report: dict[str, Any], out_dir: Path) -> None:
    source = load_json(CERTIFIED_EVIDENCE)
    pole_packet = source.setdefault("black_hole_certified_simulator", {}).setdefault(
        "pole_packet", {}
    )
    pole_packet["conditioning_certificate"] = certified_pointer(report, out_dir)
    CERTIFIED_EVIDENCE.write_text(
        json.dumps(source, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR, *, update_certified: bool = True) -> dict[str, Any]:
    report = build_theorem()
    source = load_json(CERTIFIED_EVIDENCE)
    manifest = {
        "schema": "d20.black_hole.inverse_conditioning_manifest",
        "name": THEOREM_ID,
        "inputs": {
            "certified_evidence_invariants": {
                "path": rel(CERTIFIED_EVIDENCE),
                "base_payload_sha256_without_conditioning_certificate": certified_evidence_base_sha256(source),
            }
        },
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "round-trip exact interior subextremal states through y=(log R, log T, omega_H, phi_H)",
            "stress the same inverse near the subextremal boundary",
            "inject inconsistent pole-packet noise and measure projection residuals",
            "record inverse and forward finite-difference conditioning",
        ],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    if update_certified:
        refresh_certified_evidence_pointer(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
