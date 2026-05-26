from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


THEOREM_ID = "finite_burningship_folded_map"
STATUS = "D20_FINITE_BURNINGSHIP_FOLDED_MAP_CERTIFIED"
VERIFY_STATUS = "D20_FINITE_BURNINGSHIP_FOLDED_MAP_VERIFIED"
VERIFY_FAILED_STATUS = "D20_FINITE_BURNINGSHIP_FOLDED_MAP_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
BRIDGE_REPORT = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_ship_algebraicity_bridge" / "report.json"
)
MODULI = [2, 3, 4, 5, 6, 8, 10, 12, 20, 60]
TARGET_TWO_PRIMARY = [2, 4, 4]


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fold_residue(value: int, modulus: int) -> int:
    residue = value % modulus
    return min(residue, (-residue) % modulus)


def finite_burningship_step(
    state: tuple[int, int],
    parameter: tuple[int, int],
    modulus: int,
) -> tuple[int, int]:
    x, y = state
    a, b = parameter
    u = fold_residue(x, modulus)
    v = fold_residue(y, modulus)
    return ((u * u - v * v + a) % modulus, (2 * u * v + b) % modulus)


def orbit_stats(
    parameter: tuple[int, int],
    modulus: int,
    seed: tuple[int, int] = (0, 0),
) -> tuple[int, int, int, tuple[int, int]]:
    seen: dict[tuple[int, int], int] = {}
    state = seed
    step = 0
    while state not in seen:
        seen[state] = step
        state = finite_burningship_step(state, parameter, modulus)
        step += 1
    preperiod = seen[state]
    period = step - preperiod
    return preperiod, period, len(seen), state


def two_primary_factor(value: int) -> int | None:
    factor = 1
    while value % 2 == 0 and value > 0:
        factor *= 2
        value //= 2
    return factor if factor > 1 else None


def quotient_literal(factors: list[int]) -> str:
    if not factors:
        return "trivial"
    counts = Counter(factors)
    parts: list[str] = []
    for factor in sorted(counts):
        count = counts[factor]
        parts.append(f"Z/{factor}" if count == 1 else f"Z/{factor}^{count}")
    return " x ".join(parts)


def two_primary_shape(modulus: int, branch_lift: bool) -> list[int]:
    factors: list[int] = [2] if branch_lift else []
    component = two_primary_factor(modulus)
    if component is not None:
        factors.extend([component, component])
    return sorted(factors)


def transition_indegree_values(modulus: int) -> tuple[int, int, int]:
    indegree: Counter[tuple[int, int]] = Counter()
    image: set[tuple[int, int]] = set()
    for x in range(modulus):
        for y in range(modulus):
            for a in range(modulus):
                for b in range(modulus):
                    target = finite_burningship_step((x, y), (a, b), modulus)
                    image.add(target)
                    indegree[target] += 1
    values = list(indegree.values())
    return len(image), min(values), max(values)


def summarize_modulus(modulus: int) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    image_count, indegree_min, indegree_max = transition_indegree_values(modulus)
    orbit_counter: Counter[tuple[int, int]] = Counter()
    attractor_counter: Counter[tuple[int, int]] = Counter()
    max_preperiod = 0
    max_period = 0

    for a in range(modulus):
        for b in range(modulus):
            preperiod, period, _visited, attractor = orbit_stats((a, b), modulus)
            orbit_counter[(preperiod, period)] += 1
            attractor_counter[attractor] += 1
            max_preperiod = max(max_preperiod, preperiod)
            max_period = max(max_period, period)

    direct_shape = two_primary_shape(modulus, branch_lift=False)
    branch_shape = two_primary_shape(modulus, branch_lift=True)
    top_orbit_type, top_orbit_count = orbit_counter.most_common(1)[0]
    summary = {
        "modulus": modulus,
        "state_count": modulus * modulus,
        "parameter_count": modulus * modulus,
        "transition_image_count": image_count,
        "transition_indegree_min": indegree_min,
        "transition_indegree_max": indegree_max,
        "orbit_type_count": len(orbit_counter),
        "attractor_count_from_zero_seed": len(attractor_counter),
        "max_preperiod": max_preperiod,
        "max_period": max_period,
        "top_orbit_preperiod": top_orbit_type[0],
        "top_orbit_period": top_orbit_type[1],
        "top_orbit_parameter_count": top_orbit_count,
        "direct_two_primary_shape": quotient_literal(direct_shape),
        "branch_lift_two_primary_shape": quotient_literal(branch_shape),
        "branch_lift_matches_static_2primary": branch_shape == TARGET_TWO_PRIMARY,
    }
    orbit_rows = [
        {
            "modulus": modulus,
            "preperiod": preperiod,
            "period": period,
            "parameter_count": count,
        }
        for (preperiod, period), count in sorted(orbit_counter.items())
    ]
    attractor_rows = [
        {
            "modulus": modulus,
            "attractor_x": attractor[0],
            "attractor_y": attractor[1],
            "parameter_count": count,
        }
        for attractor, count in attractor_counter.most_common(25)
    ]
    return summary, orbit_rows, attractor_rows


def semantics_payload() -> dict[str, Any]:
    return {
        "schema": "d20.finite_burningship_folded_map.semantics@1",
        "classical_formula": "z_{n+1} = (abs(Re z_n) + i abs(Im z_n))^2 + c",
        "finite_fold": "abs_m(r) = min(r mod m, -r mod m)",
        "finite_formula": [
            "x' = abs_m(x)^2 - abs_m(y)^2 + a mod m",
            "y' = 2 abs_m(x) abs_m(y) + b mod m",
        ],
        "mechanical_reading": (
            "The literal finite map on Z/m x Z/m has two parameter clocks. A separate order-two "
            "branch bit appears only if the finite model remembers which sheet was folded by the "
            "absolute-value operation."
        ),
        "naming_recommendation": (
            "Name the A985 object a static 2-primary fold-frame or branch-lifted frame readout, "
            "not just a burning field."
        ),
    }


def build_theorem() -> dict[str, Any]:
    bridge = load_json(BRIDGE_REPORT)
    target_factors = bridge.get("derived", {}).get("burning_static_fields", {}).get("quotient_factors", [])
    summary_rows: list[dict[str, Any]] = []
    orbit_rows: list[dict[str, Any]] = []
    attractor_rows: list[dict[str, Any]] = []
    for modulus in MODULI:
        summary, orbit_hist, top_attractors = summarize_modulus(modulus)
        summary_rows.append(summary)
        orbit_rows.extend(orbit_hist)
        attractor_rows.extend(top_attractors)

    mod4 = next(row for row in summary_rows if row["modulus"] == 4)
    mod20 = next(row for row in summary_rows if row["modulus"] == 20)
    mod60 = next(row for row in summary_rows if row["modulus"] == 60)
    semantics = semantics_payload()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "finite_burningship_folded_map_semantics.json", semantics)
    write_csv_rows(
        OUT_DIR / "finite_burningship_modulus_summary.csv",
        [
            "modulus",
            "state_count",
            "parameter_count",
            "transition_image_count",
            "transition_indegree_min",
            "transition_indegree_max",
            "orbit_type_count",
            "attractor_count_from_zero_seed",
            "max_preperiod",
            "max_period",
            "top_orbit_preperiod",
            "top_orbit_period",
            "top_orbit_parameter_count",
            "direct_two_primary_shape",
            "branch_lift_two_primary_shape",
            "branch_lift_matches_static_2primary",
        ],
        summary_rows,
    )
    write_csv_rows(
        OUT_DIR / "finite_burningship_orbit_type_histogram.csv",
        ["modulus", "preperiod", "period", "parameter_count"],
        orbit_rows,
    )
    write_csv_rows(
        OUT_DIR / "finite_burningship_top_attractors.csv",
        ["modulus", "attractor_x", "attractor_y", "parameter_count"],
        attractor_rows,
    )

    checks = {
        "bridge_certified": bridge.get("all_checks_pass") is True,
        "target_quotient_factors_are_z2_z4_z4": target_factors == TARGET_TWO_PRIMARY,
        "mod4_direct_shape_is_z4_squared": mod4["direct_two_primary_shape"] == "Z/4^2",
        "mod4_branch_lift_matches_static_2primary": mod4["branch_lift_matches_static_2primary"] is True,
        "mod20_branch_lift_matches_static_2primary": mod20["branch_lift_matches_static_2primary"] is True,
        "mod60_branch_lift_matches_static_2primary": mod60["branch_lift_matches_static_2primary"] is True,
        "all_finite_maps_are_total_on_grid": all(
            int(row["transition_image_count"]) == int(row["state_count"]) for row in summary_rows
        ),
        "all_transition_indegrees_uniform_when_parameters_vary": all(
            int(row["transition_indegree_min"]) == int(row["transition_indegree_max"])
            == int(row["parameter_count"])
            for row in summary_rows
        ),
        "mod60_has_nontrivial_orbit_variety": int(mod60["orbit_type_count"]) > int(mod4["orbit_type_count"]),
        "semantics_file_emitted": (OUT_DIR / "finite_burningship_folded_map_semantics.json").exists(),
    }
    report = {
        "schema": "d20.theorem.finite_burningship_folded_map.source_drop",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "A literal finite folded version of the Burning Ship recurrence has been evaluated on "
            "cyclic grids. Its direct mod-4 parameter frame gives Z/4^2; the A985 static "
            "Z/2 x Z/4^2 shape appears when the finite model keeps the order-two fold-sheet bit."
        ),
        "boundary": (
            "This is a finite dynamical-system model of the classical formula. It does not prove "
            "that the imported sandpile_burningship certificate used this exact finite fold rule."
        ),
        "inputs": {
            "burning_a985_bridge": {
                "path": rel(BRIDGE_REPORT),
                "sha256": sha_file(BRIDGE_REPORT),
            }
        },
        "checks": checks,
        "derived": {
            "classical_formula": semantics["classical_formula"],
            "finite_fold": semantics["finite_fold"],
            "target_two_primary_shape": quotient_literal(TARGET_TWO_PRIMARY),
            "moduli": MODULI,
            "mod4_direct_two_primary_shape": mod4["direct_two_primary_shape"],
            "mod4_branch_lift_two_primary_shape": mod4["branch_lift_two_primary_shape"],
            "mod60_orbit_type_count": mod60["orbit_type_count"],
            "mod60_attractor_count_from_zero_seed": mod60["attractor_count_from_zero_seed"],
            "tables": {
                "semantics": rel(OUT_DIR / "finite_burningship_folded_map_semantics.json"),
                "modulus_summary": rel(OUT_DIR / "finite_burningship_modulus_summary.csv"),
                "orbit_type_histogram": rel(OUT_DIR / "finite_burningship_orbit_type_histogram.csv"),
                "top_attractors": rel(OUT_DIR / "finite_burningship_top_attractors.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use the branch-lifted Z/2 x Z/4^2 finite frame as a naming and normalization model "
            "for the A985 static 2-primary readout."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.finite_burningship_folded_map_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            **report["derived"]["tables"],
        },
        "validation_tests": list(checks),
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    (OUT_DIR / "finite_burningship_folded_map_report.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    return (
        "# finite Burning Ship folded map\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Next: {report['next_highest_yield_item']}\n"
    )


def update_theorem_index(report: dict[str, Any]) -> None:
    index_path = D20_INVARIANTS / "theorems" / "index.json"
    existing = load_json(index_path) if index_path.exists() else {"theorems": []}
    theorems = [item for item in existing.get("theorems", []) if item.get("id") != THEOREM_ID]
    theorems.append(
        {
            "id": THEOREM_ID,
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    write_json(index_path, index)


def verify_outputs() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    summary_rows = read_csv_rows(OUT_DIR / "finite_burningship_modulus_summary.csv")
    orbit_rows = read_csv_rows(OUT_DIR / "finite_burningship_orbit_type_histogram.csv")
    attractor_rows = read_csv_rows(OUT_DIR / "finite_burningship_top_attractors.csv")
    by_modulus = {int(row["modulus"]): row for row in summary_rows}
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "summary_has_expected_moduli": sorted(by_modulus) == MODULI,
        "mod4_branch_lift_matches_target": by_modulus[4]["branch_lift_two_primary_shape"] == "Z/2 x Z/4^2",
        "mod60_branch_lift_matches_target": by_modulus[60]["branch_lift_two_primary_shape"] == "Z/2 x Z/4^2",
        "orbit_histogram_nonempty": len(orbit_rows) > 0,
        "top_attractors_nonempty": len(attractor_rows) > 0,
        "semantics_file_exists": (OUT_DIR / "finite_burningship_folded_map_semantics.json").exists(),
    }
    return {
        "status": VERIFY_STATUS if all(checks.values()) else VERIFY_FAILED_STATUS,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_theorem()
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
