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

from src.a985_perennial_ids import (  # noqa: E402
    load_perennial_sector_maps_if_available,
    write_a985_sector_csv_rows_if_available,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


FIELD_PRIME = 1_000_003
THEOREM_ID = "tiny_pointer_a985_burning_static_public_zero_alignment"
STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_PUBLIC_ZERO_ALIGNMENT_CERTIFIED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
CONSTRUCTED_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_constructed_representative"
)
TRACE_EVALUATOR_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_trace_evaluator"
PUBLIC_ZERO_DIR = D20_INVARIANTS / "theorems" / "sector_idempotent_support_admissibility"
SECTOR33_DIR = D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support"
FOURIER_TRACE_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_fourier_trace_candidate_evaluation"


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


def signed_mod(value: int) -> int:
    value %= FIELD_PRIME
    return value if value <= FIELD_PRIME // 2 else value - FIELD_PRIME


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


def support_key(sectors: list[int]) -> str:
    return "{" + ",".join(str(int(value)) for value in sorted(sectors)) + "}"


def parse_support_key(value: str) -> list[int]:
    value = value.strip()
    if value in {"", "{}"}:
        return []
    return [int(part) for part in value.strip("{}").split(",") if part]


def trace_map(rows: list[dict[str, str]]) -> dict[str, dict[int, int]]:
    out: dict[str, dict[int, int]] = {}
    for row in rows:
        generator = row["quotient_generator"]
        out.setdefault(generator, {})[int(row["source_sector"])] = int(row["trace_mod_1000003"]) % FIELD_PRIME
    return out


def public_zero_supports(report: dict[str, Any]) -> list[dict[str, Any]]:
    supports = []
    for row in report["derived"]["candidate_rows"]:
        if not bool(row["public_zero"]):
            continue
        sectors = [int(value) for value in row["sector_support"]]
        supports.append(
            {
                "sector_support": sectors,
                "sector_key": support_key(sectors),
                "sector_count": int(row["sector_count"]),
                "dimension_sum": int(row["dimension_sum"]),
                "regular_trace": int(row["regular_trace"]),
                "contains_sector33": bool(row["contains_sector33"]),
                "height_support_exact_for_certified_transport": bool(
                    row["height_support_exact_for_certified_transport"]
                ),
                "inclusion_minimal_nonzero": bool(row["inclusion_minimal_nonzero"]),
                "boundary_null": bool(row["boundary_null"]),
            }
        )
    return sorted(supports, key=lambda item: (len(item["sector_support"]), item["sector_support"]))


def generator_kernel_rows(traces: dict[str, dict[int, int]], public_zero: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public_zero_nonempty = [row for row in public_zero if row["sector_support"]]
    out: list[dict[str, Any]] = []
    for generator, by_sector in sorted(traces.items()):
        zero_sectors = sorted(sector for sector, trace in by_sector.items() if trace == 0)
        nonzero_sectors = sorted(sector for sector, trace in by_sector.items() if trace != 0)
        exact_public_zero_hits = [
            row["sector_key"]
            for row in public_zero_nonempty
            if sorted(row["sector_support"]) == zero_sectors
        ]
        contained_public_zero_hits = [
            row["sector_key"]
            for row in public_zero_nonempty
            if set(row["sector_support"]).issubset(set(zero_sectors))
        ]
        out.append(
            {
                "quotient_generator": generator,
                "zero_sector_count": len(zero_sectors),
                "zero_sectors": json.dumps(zero_sectors, separators=(",", ":")),
                "nonzero_sector_count": len(nonzero_sectors),
                "contains_sector33_in_kernel": 33 in zero_sectors,
                "kernel_is_exact_sector33": zero_sectors == [33],
                "kernel_extra_non_public_zero_sectors": json.dumps(
                    [sector for sector in zero_sectors if sector != 33],
                    separators=(",", ":"),
                ),
                "kernel_equals_public_zero_supports": json.dumps(exact_public_zero_hits, separators=(",", ":")),
                "public_zero_supports_contained_in_kernel": json.dumps(contained_public_zero_hits, separators=(",", ":")),
            }
        )
    return out


def support_alignment_rows(
    traces: dict[str, dict[int, int]],
    public_zero: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for generator, by_sector in sorted(traces.items()):
        for support in public_zero:
            sectors = support["sector_support"]
            sector_traces = [by_sector[sector] for sector in sectors]
            zero_members = [sector for sector, trace in zip(sectors, sector_traces) if trace == 0]
            nonzero_members = [sector for sector, trace in zip(sectors, sector_traces) if trace != 0]
            trace_sum = sum(sector_traces) % FIELD_PRIME
            rows.append(
                {
                    "quotient_generator": generator,
                    "sector_support": support["sector_key"],
                    "sector_count": support["sector_count"],
                    "dimension_sum": support["dimension_sum"],
                    "regular_trace": support["regular_trace"],
                    "contains_sector33": support["contains_sector33"],
                    "height_support_exact_for_certified_transport": support[
                        "height_support_exact_for_certified_transport"
                    ],
                    "inclusion_minimal_nonzero": support["inclusion_minimal_nonzero"],
                    "boundary_null": support["boundary_null"],
                    "zero_member_sectors": json.dumps(zero_members, separators=(",", ":")),
                    "nonzero_member_sectors": json.dumps(nonzero_members, separators=(",", ":")),
                    "support_all_members_zero": len(sectors) > 0 and len(nonzero_members) == 0,
                    "support_has_nonzero_member": len(nonzero_members) > 0,
                    "trace_sum_mod_1000003": trace_sum,
                    "trace_sum_signed": signed_mod(trace_sum),
                }
            )
    return rows


def fourier_overlap_rows(
    traces: dict[str, dict[int, int]],
    fourier_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    public_zero_rows = [
        row for row in fourier_rows if row["public_zero"] == "True" and row["sector_support"] != "{}"
    ]
    rows: list[dict[str, Any]] = []
    for generator, by_sector in sorted(traces.items()):
        kernel = {sector for sector, trace in by_sector.items() if trace == 0}
        for row in public_zero_rows:
            sectors = parse_support_key(row["sector_support"])
            rows.append(
                {
                    "quotient_generator": generator,
                    "screen_id": row["screen_id"],
                    "sector_support": row["sector_support"],
                    "fourier_scalar_on_support": row["scalar_on_support"],
                    "fourier_support_scalar": row["support_scalar"],
                    "fourier_canonical_trace_defined": row["canonical_trace_defined"],
                    "constructed_kernel_contains_support": set(sectors).issubset(kernel),
                    "constructed_kernel_intersection": json.dumps(
                        sorted(set(sectors) & kernel),
                        separators=(",", ":"),
                    ),
                }
            )
    return rows


def build_alignment() -> dict[str, Any]:
    constructed_report = load_json(CONSTRUCTED_DIR / "report.json")
    evaluator_report = load_json(TRACE_EVALUATOR_DIR / "report.json")
    public_report = load_json(PUBLIC_ZERO_DIR / "report.json")
    sector33_report = load_json(SECTOR33_DIR / "report.json")
    fourier_report = load_json(FOURIER_TRACE_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()

    trace_rows = read_csv_rows(CONSTRUCTED_DIR / "burning_static_constructed_trace_profile.csv")
    traces = trace_map(trace_rows)
    public_zero = public_zero_supports(public_report)
    kernel_rows = generator_kernel_rows(traces, public_zero)
    alignment_rows = support_alignment_rows(traces, public_zero)
    fourier_rows = fourier_overlap_rows(
        traces,
        read_csv_rows(FOURIER_TRACE_DIR / "fourier_trace_public_zero_support_summary.csv"),
    )

    exact_sector33_generators = [
        row["quotient_generator"] for row in kernel_rows if row["kernel_is_exact_sector33"] is True
    ]
    generators_vanishing_on_sector33 = [
        row["quotient_generator"] for row in kernel_rows if row["contains_sector33_in_kernel"] is True
    ]
    nonempty_public_zero = [row for row in public_zero if row["sector_support"]]
    exact_height_support = [
        row["sector_key"]
        for row in nonempty_public_zero
        if row["height_support_exact_for_certified_transport"]
    ]
    minimal_without_sector33 = [
        row["sector_key"]
        for row in nonempty_public_zero
        if row["inclusion_minimal_nonzero"] and not row["contains_sector33"]
    ]
    exact_sector33_alignment = [
        row
        for row in alignment_rows
        if row["quotient_generator"] in exact_sector33_generators
        and row["sector_support"] in minimal_without_sector33
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kernel_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_constructed_kernel_summary.csv",
        [
            "quotient_generator",
            "zero_sector_count",
            "zero_sectors",
            "nonzero_sector_count",
            "contains_sector33_in_kernel",
            "kernel_is_exact_sector33",
            "kernel_extra_non_public_zero_sectors",
            "kernel_equals_public_zero_supports",
            "public_zero_supports_contained_in_kernel",
        ],
        kernel_rows,
        perennial_maps,
    )
    alignment_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_public_zero_support_alignment.csv",
        [
            "quotient_generator",
            "sector_support",
            "sector_count",
            "dimension_sum",
            "regular_trace",
            "contains_sector33",
            "height_support_exact_for_certified_transport",
            "inclusion_minimal_nonzero",
            "boundary_null",
            "zero_member_sectors",
            "nonzero_member_sectors",
            "support_all_members_zero",
            "support_has_nonzero_member",
            "trace_sum_mod_1000003",
            "trace_sum_signed",
        ],
        alignment_rows,
        perennial_maps,
    )
    fourier_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_fourier_public_zero_overlap.csv",
        [
            "quotient_generator",
            "screen_id",
            "sector_support",
            "fourier_scalar_on_support",
            "fourier_support_scalar",
            "fourier_canonical_trace_defined",
            "constructed_kernel_contains_support",
            "constructed_kernel_intersection",
        ],
        fourier_rows,
        perennial_maps,
    )

    checks = {
        "constructed_representative_certified": constructed_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_CERTIFIED"
        and constructed_report.get("all_checks_pass") is True,
        "trace_evaluator_ready_or_profile_certified": evaluator_report.get("status")
        in {
            "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_READY_INPUT_ABSENT",
            "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_PROFILE_CERTIFIED",
            "D20_TINY_POINTER_A985_BURNING_STATIC_DESIGNED_TRACE_PROFILE_CERTIFIED",
            "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_TRACE_PROFILE_CERTIFIED",
        }
        and evaluator_report.get("all_checks_pass") is True,
        "public_zero_supports_certified": public_report.get("status")
        == "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED"
        and public_report.get("all_checks_pass") is True,
        "sector33_unique_public_zero_certified": sector33_report.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and sector33_report.get("all_checks_pass") is True,
        "fourier_trace_candidate_evaluation_certified": fourier_report.get("status")
        == "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_CERTIFIED"
        and fourier_report.get("all_checks_pass") is True,
        "public_zero_support_count_is_6_including_zero": len(public_zero) == 6,
        "height_exact_public_zero_support_is_33": exact_height_support == ["{33}"],
        "all_constructed_generators_vanish_on_sector33": sorted(generators_vanishing_on_sector33)
        == sorted(traces),
        "at_least_two_generators_have_exact_sector33_kernel": len(exact_sector33_generators) >= 2,
        "exact_sector33_generators_detect_minimal_public_zero_without_sector33": all(
            row["support_has_nonzero_member"] is True for row in exact_sector33_alignment
        ),
        "kernel_summary_has_three_rows": len(kernel_rows) == 3,
        "alignment_rows_are_3_by_6": len(alignment_rows) == 18,
        "perennial_set_keys_emitted_when_available": perennial_maps is None
        or (
            kernel_perennial_stats["sector_mismatch_count"] == 0
            and alignment_perennial_stats["sector_mismatch_count"] == 0
            and fourier_perennial_stats["sector_mismatch_count"] == 0
            and "zero_sectors_perennial_ids" in kernel_perennial_stats["added_columns"]
            and "sector_support_perennial_ids" in alignment_perennial_stats["added_columns"]
            and "constructed_kernel_intersection_perennial_ids" in fourier_perennial_stats["added_columns"]
        ),
    }

    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_public_zero_alignment.source_drop",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "The constructed Burning/A985 frame-section traces align with the certified public-zero "
            "sector structure: all three constructed generators vanish on sector 33, and two have "
            "kernel exactly {33}, the unique primitive public-zero and height-exact support."
        ),
        "boundary": (
            "This compares the repo-native constructed A985-side Burning trace profile to "
            "certified public-zero sector supports. It does not assert that an external artifact "
            "uses the same generator names."
        ),
        "field_prime": FIELD_PRIME,
        "inputs": {
            "constructed_representative": {
                "path": rel(CONSTRUCTED_DIR / "report.json"),
                "sha256": sha_file(CONSTRUCTED_DIR / "report.json"),
            },
            "constructed_trace_evaluator": {
                "path": rel(TRACE_EVALUATOR_DIR / "report.json"),
                "sha256": sha_file(TRACE_EVALUATOR_DIR / "report.json"),
            },
            "public_zero_supports": {
                "path": rel(PUBLIC_ZERO_DIR / "report.json"),
                "sha256": sha_file(PUBLIC_ZERO_DIR / "report.json"),
            },
            "sector33_unique_public_zero": {
                "path": rel(SECTOR33_DIR / "report.json"),
                "sha256": sha_file(SECTOR33_DIR / "report.json"),
            },
            "fourier_trace_candidate_evaluation": {
                "path": rel(FOURIER_TRACE_DIR / "report.json"),
                "sha256": sha_file(FOURIER_TRACE_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "constructed_generators": sorted(traces),
            "generators_vanishing_on_sector33": generators_vanishing_on_sector33,
            "exact_sector33_kernel_generators": exact_sector33_generators,
            "height_exact_public_zero_supports": exact_height_support,
            "minimal_public_zero_supports_without_sector33": minimal_without_sector33,
            "public_zero_support_count": len(public_zero),
            "tables": {
                "kernel_summary": rel(OUT_DIR / "burning_static_constructed_kernel_summary.csv"),
                "public_zero_alignment": rel(OUT_DIR / "burning_static_public_zero_support_alignment.csv"),
                "fourier_public_zero_overlap": rel(OUT_DIR / "burning_static_fourier_public_zero_overlap.csv"),
            },
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "kernel_set_columns_added": kernel_perennial_stats["added_columns"],
                "alignment_set_columns_added": alignment_perennial_stats["added_columns"],
                "fourier_set_columns_added": fourier_perennial_stats["added_columns"],
            },
        },
        "next_highest_yield_item": (
            "Promote the exact-{33} constructed generators into a sector-33 detector theorem, then "
            "compare future imported Burning_static_fields rows against that detector."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_public_zero_alignment_manifest.source_drop",
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
    (OUT_DIR / "burning_static_public_zero_alignment_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    kernels = read_csv_rows(OUT_DIR / "burning_static_constructed_kernel_summary.csv")
    kernel_lines = "\n".join(
        f"- `{row['quotient_generator']}` kernel: `{row['zero_sectors']}`"
        for row in kernels
    )
    return (
        "# Burning static public-zero alignment\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        "## Kernels\n\n"
        f"{kernel_lines}\n\n"
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
    kernel_rows = read_csv_rows(OUT_DIR / "burning_static_constructed_kernel_summary.csv")
    alignment_rows = read_csv_rows(OUT_DIR / "burning_static_public_zero_support_alignment.csv")
    fourier_rows = read_csv_rows(OUT_DIR / "burning_static_fourier_public_zero_overlap.csv")
    exact_kernel_rows = [row for row in kernel_rows if row["kernel_is_exact_sector33"] == "True"]
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    kernel_fields = set(kernel_rows[0]) if kernel_rows else set()
    alignment_fields = set(alignment_rows[0]) if alignment_rows else set()
    fourier_fields = set(fourier_rows[0]) if fourier_rows else set()
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "kernel_rows_count_is_3": len(kernel_rows) == 3,
        "alignment_rows_count_is_18": len(alignment_rows) == 18,
        "fourier_overlap_rows_nonempty": len(fourier_rows) > 0,
        "at_least_two_exact_sector33_kernel_rows": len(exact_kernel_rows) >= 2,
        "all_kernel_rows_include_sector33": all(row["contains_sector33_in_kernel"] == "True" for row in kernel_rows),
        "perennial_set_keys_present_when_available": not perennial_available
        or (
            "zero_sectors_perennial_ids" in kernel_fields
            and "sector_support_perennial_ids" in alignment_fields
            and "zero_member_sectors_perennial_ids" in alignment_fields
            and "nonzero_member_sectors_perennial_ids" in alignment_fields
            and "sector_support_perennial_ids" in fourier_fields
            and "constructed_kernel_intersection_perennial_ids" in fourier_fields
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_BURNING_STATIC_PUBLIC_ZERO_ALIGNMENT_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_BURNING_STATIC_PUBLIC_ZERO_ALIGNMENT_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_alignment()
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
