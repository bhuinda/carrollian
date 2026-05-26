from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


THEOREM_ID = "tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors"
STATUS = "D20_TINY_POINTER_A985_BURNING_SHIP_FOLD_FRAME_NORMALIZATION_ANCHORS_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_BURNING_SHIP_FOLD_FRAME_NORMALIZATION_ANCHORS_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_BURNING_SHIP_FOLD_FRAME_NORMALIZATION_ANCHORS_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
FINITE_DIR = D20_INVARIANTS / "theorems" / "finite_burningship_folded_map"
CONSTRUCTED_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_constructed_representative"
)
TRACE_EVALUATOR_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_trace_evaluator"
ALIGNMENT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_public_zero_alignment"
DETECTOR_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_sector33_detector"

ANCHOR_ORDER = ["z2_a12_parity", "z4_a42_clock", "z4_a12_frame_clock"]
ANCHOR_DEFINITIONS = {
    "z2_a12_parity": {
        "normalization_anchor": "fold_sheet_bit",
        "finite_burning_ship_role": "order-two sheet bit retained by the finite absolute-value fold",
        "finite_quotient_factor": "Z/2",
        "a985_raw_formula": "q12_map(relation_alpha) mod 2",
        "normalization_use": "fixes the branch orientation of the static 2-primary frame",
    },
    "z4_a42_clock": {
        "normalization_anchor": "primary_mod4_clock",
        "finite_burning_ship_role": "first direct mod-4 parameter clock of the finite Burning Ship frame",
        "finite_quotient_factor": "Z/4",
        "a985_raw_formula": "q42_map(relation_alpha) mod 4",
        "normalization_use": "fixes the first Z/4 clock and is an exact source-sector-33 detector",
    },
    "z4_a12_frame_clock": {
        "normalization_anchor": "framed_mod4_clock",
        "finite_burning_ship_role": "second direct mod-4 clock after adding the A985 source/target frame",
        "finite_quotient_factor": "Z/4",
        "a985_raw_formula": "(q12_map(relation_alpha) + source_object + target_object) mod 4",
        "normalization_use": "fixes the companion Z/4 frame clock; it vanishes on sector 33 but has one extra zero sector",
    },
}


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


def parse_json_list(value: str) -> list[int]:
    return [int(item) for item in json.loads(value)]


def rows_by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def build_anchor_rows() -> list[dict[str, Any]]:
    generator_rows = rows_by_key(
        read_csv_rows(CONSTRUCTED_DIR / "burning_static_constructed_generator_summary.csv"),
        "quotient_generator",
    )
    kernel_rows = rows_by_key(
        read_csv_rows(ALIGNMENT_DIR / "burning_static_constructed_kernel_summary.csv"),
        "quotient_generator",
    )
    detector_rows = rows_by_key(
        read_csv_rows(DETECTOR_DIR / "burning_static_sector33_detector_generators.csv"),
        "quotient_generator",
    )
    rows: list[dict[str, Any]] = []
    for generator in ANCHOR_ORDER:
        definition = ANCHOR_DEFINITIONS[generator]
        summary = generator_rows[generator]
        kernel = kernel_rows[generator]
        detector = detector_rows.get(generator)
        exact_detector = detector is not None and detector["kernel_is_exact_sector33"] == "True"
        zero_sectors = parse_json_list(kernel["zero_sectors"])
        rows.append(
            {
                "normalization_anchor": definition["normalization_anchor"],
                "quotient_generator": generator,
                "abstract_order": int(summary["abstract_order"]),
                "finite_quotient_factor": definition["finite_quotient_factor"],
                "finite_burning_ship_role": definition["finite_burning_ship_role"],
                "a985_raw_formula": definition["a985_raw_formula"],
                "residue_values": summary["residue_values"],
                "nonzero_coordinate_count": int(summary["nonzero_coordinate_count"]),
                "coordinate_vector_sha256": summary["coordinate_vector_sha256"],
                "zero_sectors": json.dumps(zero_sectors, separators=(",", ":")),
                "kernel_is_exact_sector33": exact_detector,
                "normalization_use": definition["normalization_use"],
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    finite_report = load_json(FINITE_DIR / "report.json")
    constructed_report = load_json(CONSTRUCTED_DIR / "report.json")
    trace_report = load_json(TRACE_EVALUATOR_DIR / "report.json")
    alignment_report = load_json(ALIGNMENT_DIR / "report.json")
    detector_report = load_json(DETECTOR_DIR / "report.json")
    finite_summary = rows_by_key(read_csv_rows(FINITE_DIR / "finite_burningship_modulus_summary.csv"), "modulus")
    anchor_rows = build_anchor_rows()

    order_profile = [int(row["abstract_order"]) for row in anchor_rows]
    exact_detector_generators = [
        row["quotient_generator"] for row in anchor_rows if row["kernel_is_exact_sector33"] is True
    ]
    zero_sector_profile = {row["quotient_generator"]: parse_json_list(row["zero_sectors"]) for row in anchor_rows}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "burning_ship_fold_frame_normalization_anchors.csv",
        [
            "normalization_anchor",
            "quotient_generator",
            "abstract_order",
            "finite_quotient_factor",
            "finite_burning_ship_role",
            "a985_raw_formula",
            "residue_values",
            "nonzero_coordinate_count",
            "coordinate_vector_sha256",
            "zero_sectors",
            "kernel_is_exact_sector33",
            "normalization_use",
        ],
        anchor_rows,
    )
    convention = {
        "schema": "d20.tiny_pointer_a985.burning_ship_fold_frame_normalization_convention@1",
        "name": "Burning Ship branch-lifted static fold-frame",
        "quotient_shape": "Z/2 x Z/4^2",
        "anchor_order": ANCHOR_ORDER,
        "rule": (
            "Use the finite Burning Ship branch-lift convention: the retained fold-sheet bit fixes "
            "the Z/2 generator, and the two mod-4 frame clocks fix the two Z/4 generators."
        ),
        "boundary": (
            "This fixes the static 2-primary frame convention. It is not a full GL_d matrix-unit "
            "basis choice for every open Wedderburn block."
        ),
    }
    write_json(OUT_DIR / "burning_ship_fold_frame_normalization_convention.json", convention)

    mod4 = finite_summary["4"]
    mod20 = finite_summary["20"]
    mod60 = finite_summary["60"]
    checks = {
        "finite_burning_ship_folded_map_certified": finite_report.get("status")
        == "D20_FINITE_BURNINGSHIP_FOLDED_MAP_CERTIFIED"
        and finite_report.get("all_checks_pass") is True,
        "constructed_static_representative_certified": constructed_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_CERTIFIED"
        and constructed_report.get("all_checks_pass") is True,
        "trace_evaluator_ready_or_profile_certified": trace_report.get("status")
        in {
            "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_READY_INPUT_ABSENT",
            "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_PROFILE_CERTIFIED",
            "D20_TINY_POINTER_A985_BURNING_STATIC_DESIGNED_TRACE_PROFILE_CERTIFIED",
            "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_TRACE_PROFILE_CERTIFIED",
        }
        and trace_report.get("all_checks_pass") is True,
        "public_zero_alignment_certified": alignment_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_PUBLIC_ZERO_ALIGNMENT_CERTIFIED"
        and alignment_report.get("all_checks_pass") is True,
        "sector33_detector_certified": detector_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_SECTOR33_DETECTOR_CERTIFIED"
        and detector_report.get("all_checks_pass") is True,
        "mod4_direct_shape_is_z4_squared": mod4["direct_two_primary_shape"] == "Z/4^2",
        "mod4_branch_lift_shape_matches_static": mod4["branch_lift_two_primary_shape"] == "Z/2 x Z/4^2",
        "mod20_branch_lift_shape_matches_static": mod20["branch_lift_two_primary_shape"] == "Z/2 x Z/4^2",
        "mod60_branch_lift_shape_matches_static": mod60["branch_lift_two_primary_shape"] == "Z/2 x Z/4^2",
        "anchor_order_profile_is_2_4_4": order_profile == [2, 4, 4],
        "exact_sector33_detector_generators_are_fold_sheet_and_primary_clock": exact_detector_generators
        == ["z2_a12_parity", "z4_a42_clock"],
        "all_anchor_rows_vanish_on_sector33": all(33 in sectors for sectors in zero_sector_profile.values()),
        "framed_clock_records_extra_zero_sector20": zero_sector_profile["z4_a12_frame_clock"] == [20, 33],
        "anchor_rows_count_is_3": len(anchor_rows) == 3,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors.source_drop",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "The A985 static 2-primary frame is normalized by the finite Burning Ship branch-lift "
            "convention: fold-sheet bit, primary mod-4 clock, and framed mod-4 clock map to the "
            "three constructed raw-orbital generators."
        ),
        "boundary": (
            "These anchors normalize the static Z/2 x Z/4^2 frame. They do not remove the separate "
            "sector-local GL_d matrix-unit basis ambiguity for all open blocks."
        ),
        "inputs": {
            "finite_burning_ship_folded_map": {
                "path": rel(FINITE_DIR / "report.json"),
                "sha256": sha_file(FINITE_DIR / "report.json"),
            },
            "constructed_static_representative": {
                "path": rel(CONSTRUCTED_DIR / "report.json"),
                "sha256": sha_file(CONSTRUCTED_DIR / "report.json"),
            },
            "constructed_trace_evaluator": {
                "path": rel(TRACE_EVALUATOR_DIR / "report.json"),
                "sha256": sha_file(TRACE_EVALUATOR_DIR / "report.json"),
            },
            "public_zero_alignment": {
                "path": rel(ALIGNMENT_DIR / "report.json"),
                "sha256": sha_file(ALIGNMENT_DIR / "report.json"),
            },
            "sector33_detector": {
                "path": rel(DETECTOR_DIR / "report.json"),
                "sha256": sha_file(DETECTOR_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "anchor_order": ANCHOR_ORDER,
            "order_profile": order_profile,
            "exact_sector33_detector_generators": exact_detector_generators,
            "zero_sector_profile": zero_sector_profile,
            "normalization_convention": "Burning Ship branch-lifted static fold-frame",
            "tables": {
                "anchors": rel(OUT_DIR / "burning_ship_fold_frame_normalization_anchors.csv"),
                "convention": rel(OUT_DIR / "burning_ship_fold_frame_normalization_convention.json"),
            },
        },
        "next_highest_yield_item": (
            "Thread this fold-frame convention into the sector-local normalization ledger as the "
            "static 2-primary anchor, while keeping the remaining GL_d block-basis obligations explicit."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors_manifest.source_drop",
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
    (OUT_DIR / "burning_ship_fold_frame_normalization_anchors_report.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    return (
        "# Burning Ship fold-frame normalization anchors\n\n"
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
    anchor_rows = read_csv_rows(OUT_DIR / "burning_ship_fold_frame_normalization_anchors.csv")
    convention = load_json(OUT_DIR / "burning_ship_fold_frame_normalization_convention.json")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "anchor_rows_count_is_3": len(anchor_rows) == 3,
        "anchor_order_is_expected": [row["quotient_generator"] for row in anchor_rows] == ANCHOR_ORDER,
        "order_profile_is_2_4_4": [int(row["abstract_order"]) for row in anchor_rows] == [2, 4, 4],
        "exact_detector_rows_are_expected": [
            row["quotient_generator"] for row in anchor_rows if row["kernel_is_exact_sector33"] == "True"
        ]
        == ["z2_a12_parity", "z4_a42_clock"],
        "convention_names_burning_ship": "Burning Ship" in convention.get("name", ""),
        "convention_file_exists": (OUT_DIR / "burning_ship_fold_frame_normalization_convention.json").exists(),
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
