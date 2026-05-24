from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "nonexact_optical_residue"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
RESIDUE_SPECTRUM_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"
MINIMAL_SPECTRUM_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_minimal.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"


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


def split_ids(value: str) -> list[int]:
    return [int(part) for part in value.split()] if value else []


def load_residue_spectrum(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            action = int(row["total_optical_action"])
            rows.append(
                {
                    "mask": int(row["mask"]),
                    "basis_cycle_ids": split_ids(row["basis_cycle_ids"]),
                    "residue_edge_weight": int(row["residue_edge_weight"]),
                    "total_basis_length": int(row["total_basis_length"]),
                    "total_optical_action": action,
                    "total_connection_log_action": row["total_connection_log_action"],
                    "total_entropy_proxy": row["total_entropy_proxy"],
                    "incidence_vector_mod2": row["incidence_vector_mod2"].strip(),
                    "forced_res_A985_optical": -action,
                    "forced_nonzero_residual": action != 0,
                }
            )
    return rows


def load_primitive_cycles() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            action = int(row["optical_action"])
            rows.append(
                {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "edge_ids": split_ids(row["edge_ids"]),
                    "optical_action": action,
                    "entropy_proxy_A_over_4WD6": row["entropy_proxy_A_over_4WD6"],
                    "forced_res_A985_optical": -action,
                    "forced_nonzero_residual": action != 0,
                }
            )
    return rows


def class_digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "mask": row["mask"],
        "basis_cycle_ids": row["basis_cycle_ids"],
        "residue_edge_weight": row["residue_edge_weight"],
        "total_basis_length": row["total_basis_length"],
        "total_optical_action": row["total_optical_action"],
        "forced_res_A985_optical": row["forced_res_A985_optical"],
        "incidence_vector_mod2": row["incidence_vector_mod2"],
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
    residue_rows = load_residue_spectrum(RESIDUE_SPECTRUM_CSV)
    minimal_rows = load_residue_spectrum(MINIMAL_SPECTRUM_CSV)
    primitive_cycles = load_primitive_cycles()

    cycle_rank = 11
    masks = sorted(row["mask"] for row in residue_rows)
    zero_rows = [row for row in residue_rows if row["mask"] == 0]
    nonzero_rows = [row for row in residue_rows if row["mask"] != 0]
    forced_rows = [row for row in nonzero_rows if row["forced_nonzero_residual"]]
    sorted_forced = sorted(
        forced_rows,
        key=lambda row: (
            row["total_optical_action"],
            row["residue_edge_weight"],
            row["total_basis_length"],
            row["mask"],
        ),
    )
    sorted_minimal_nonzero = sorted(
        [row for row in minimal_rows if row["mask"] != 0],
        key=lambda row: (
            row["total_optical_action"],
            row["residue_edge_weight"],
            row["total_basis_length"],
            row["mask"],
        ),
    )
    first_forced = sorted_forced[0] if sorted_forced else None
    first_minimal = sorted_minimal_nonzero[0] if sorted_minimal_nonzero else None
    primitive_witness = min(primitive_cycles, key=lambda row: (row["optical_action"], row["cycle_id"]))

    checks = {
        "residue_spectrum_exists": RESIDUE_SPECTRUM_CSV.exists(),
        "minimal_spectrum_exists": MINIMAL_SPECTRUM_CSV.exists(),
        "primitive_cycle_table_exists": PRIMITIVE_CYCLES_CSV.exists(),
        "residue_class_count_is_2_power_11": len(residue_rows) == 2**cycle_rank,
        "residue_masks_are_complete": masks == list(range(2**cycle_rank)),
        "zero_class_unique": len(zero_rows) == 1,
        "zero_class_has_zero_optical_action": len(zero_rows) == 1 and zero_rows[0]["total_optical_action"] == 0,
        "zero_class_has_zero_forced_residual": len(zero_rows) == 1 and zero_rows[0]["forced_res_A985_optical"] == 0,
        "all_nonzero_classes_have_positive_optical_action": all(row["total_optical_action"] > 0 for row in nonzero_rows),
        "all_nonzero_classes_force_nonzero_residual": len(forced_rows) == len(nonzero_rows),
        "forced_nonzero_count_is_2047": len(forced_rows) == 2**cycle_rank - 1,
        "primitive_cycles_have_positive_optical_action": all(row["optical_action"] > 0 for row in primitive_cycles),
        "optical_flux_is_not_exact": bool(primitive_cycles) and primitive_witness["optical_action"] > 0,
        "first_forced_class_is_mask_256": first_forced is not None and first_forced["mask"] == 256,
        "first_forced_action_is_374784": first_forced is not None and first_forced["total_optical_action"] == 374784,
        "minimal_spectrum_agrees_on_first_forced_class": (
            first_forced is not None
            and first_minimal is not None
            and first_forced["mask"] == first_minimal["mask"]
            and first_forced["total_optical_action"] == first_minimal["total_optical_action"]
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_NONEXACT_OPTICAL_RESIDUE_CERTIFIED"
        if all_checks_pass
        else "D20_NONEXACT_OPTICAL_RESIDUE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.nonexact_optical_residue.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The positive optical action on closed D20 returns is a non-exact flux. "
            "In the scalar closed-return balance, every nonzero residue class forces "
            "a nonzero A985 residual equal to minus its optical action."
        ),
        "inputs": {
            "residue_spectrum": {
                "path": rel(RESIDUE_SPECTRUM_CSV),
                "sha256": sha_file(RESIDUE_SPECTRUM_CSV),
            },
            "minimal_residue_spectrum": {
                "path": rel(MINIMAL_SPECTRUM_CSV),
                "sha256": sha_file(MINIMAL_SPECTRUM_CSV),
            },
            "primitive_cycle_table": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
        },
        "definitions": {
            "nonexact_optical_flux": "Flux_D20^opt(gamma) := A_opt(gamma), the positive optical action recorded for the closed return.",
            "closed_return_balance": "0 = Flux_D20^opt(gamma) + Res_A985^opt(gamma)",
            "forced_residual": "Res_A985^opt(gamma) := -A_opt(gamma)",
            "exactness_obstruction": (
                "A scalar edge flux is exact only if every closed cycle has zero integral. "
                "The primitive H-cycle table contains positive closed optical actions, so optical action is not exact."
            ),
        },
        "derived": {
            "cycle_rank": cycle_rank,
            "residue_class_count": len(residue_rows),
            "zero_residue_class": class_digest(zero_rows[0]) if zero_rows else None,
            "forced_nonzero_residual_count": len(forced_rows),
            "first_forced_nonzero_residual": class_digest(first_forced) if first_forced else None,
            "first_forced_nonzero_residuals_by_optical_action": [
                class_digest(row) for row in sorted_forced[:12]
            ],
            "primitive_exactness_witness": primitive_witness,
            "primitive_cycle_residuals": [
                {
                    "cycle_id": row["cycle_id"],
                    "length": row["length"],
                    "optical_action": row["optical_action"],
                    "forced_res_A985_optical": row["forced_res_A985_optical"],
                    "forced_nonzero_residual": row["forced_nonzero_residual"],
                }
                for row in sorted(primitive_cycles, key=lambda row: (row["optical_action"], row["cycle_id"]))
            ],
        },
        "checks": checks,
        "theorem": {
            "statement": (
                "For the 2048 certified D20 mod-2 closed-return classes, the zero class is the only class "
                "with zero optical action. Every nonzero class has positive optical action, hence the scalar "
                "balance law forces Res_A985^opt(gamma)=-A_opt(gamma) != 0."
            ),
            "first_obstruction": (
                "The first forced nonzero residual is mask 256, basis cycle [8], with optical action 374784 "
                "and forced residual -374784."
            ),
            "scope": (
                "This isolates the non-exact optical/action sector. It does not identify the internal A985 "
                "carrier of the residual beyond the scalar balance obligation."
            ),
            "not_claimed": [
                "the hidden A985 residual carrier has been decomposed into relation-algebra sectors",
                "continuum BMS balance has been recovered",
                "positive optical action can be gauged away",
            ],
        },
        "next_highest_yield_item": (
            "Resolve the forced scalar residuals into A985 sector data by pairing the first obstructing "
            "cycles with the sector-33/tube-visible integrity witnesses."
        ),
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.nonexact_optical_residue_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the 2048-class closed-return residue ledger is complete",
            "verify the zero class has zero optical action and zero forced residual",
            "verify every nonzero residue class has positive optical action",
            "isolate the first forced nonzero residual class by optical action",
            "certify that optical action is non-exact because a primitive closed cycle has positive action",
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
