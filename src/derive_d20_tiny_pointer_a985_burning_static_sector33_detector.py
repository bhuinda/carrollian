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
THEOREM_ID = "tiny_pointer_a985_burning_static_sector33_detector"
STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_SECTOR33_DETECTOR_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_SECTOR33_DETECTOR_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_SECTOR33_DETECTOR_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
ALIGNMENT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_public_zero_alignment"
CONSTRUCTED_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_constructed_representative"
)
FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_sector_match"
SECTOR33_DIR = D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support"

EXPECTED_DETECTORS = ["z2_a12_parity", "z4_a42_clock"]


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


def signed_mod(value: int) -> int:
    value %= FIELD_PRIME
    return value if value <= FIELD_PRIME // 2 else value - FIELD_PRIME


def parse_int_list(value: str) -> list[int]:
    return [int(item) for item in json.loads(value)]


def trace_profile_by_generator() -> dict[str, dict[int, dict[str, str]]]:
    rows = read_csv_rows(CONSTRUCTED_DIR / "burning_static_constructed_trace_profile.csv")
    out: dict[str, dict[int, dict[str, str]]] = {}
    for row in rows:
        out.setdefault(row["quotient_generator"], {})[int(row["source_sector"])] = row
    return out


def exact_detector_rows() -> list[dict[str, Any]]:
    rows = read_csv_rows(ALIGNMENT_DIR / "burning_static_constructed_kernel_summary.csv")
    detectors = []
    for row in rows:
        if row["quotient_generator"] not in EXPECTED_DETECTORS:
            continue
        zero_sectors = parse_int_list(row["zero_sectors"])
        detectors.append(
            {
                "quotient_generator": row["quotient_generator"],
                "zero_sector_count": int(row["zero_sector_count"]),
                "zero_sectors": json.dumps(zero_sectors, separators=(",", ":")),
                "nonzero_sector_count": int(row["nonzero_sector_count"]),
                "kernel_is_exact_sector33": row["kernel_is_exact_sector33"] == "True",
            }
        )
    return sorted(detectors, key=lambda item: item["quotient_generator"])


def detector_table(
    traces: dict[str, dict[int, dict[str, str]]],
    detectors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    detector_names = [row["quotient_generator"] for row in detectors]
    sectors = sorted(set.intersection(*(set(traces[name]) for name in detector_names)))
    rows: list[dict[str, Any]] = []
    for sector in sectors:
        first = traces[detector_names[0]][sector]
        z2_trace = int(traces["z2_a12_parity"][sector]["trace_mod_1000003"]) % FIELD_PRIME
        z4_trace = int(traces["z4_a42_clock"][sector]["trace_mod_1000003"]) % FIELD_PRIME
        z2_zero = z2_trace == 0
        z4_zero = z4_trace == 0
        rows.append(
            {
                "source_sector": sector,
                "sector_label": sector,
                "raw_sector": int(first["raw_sector"]),
                "block_dimension": int(first["block_dimension"]),
                "z2_a12_parity_trace_mod": z2_trace,
                "z2_a12_parity_trace_signed": signed_mod(z2_trace),
                "z2_a12_parity_zero": z2_zero,
                "z4_a42_clock_trace_mod": z4_trace,
                "z4_a42_clock_trace_signed": signed_mod(z4_trace),
                "z4_a42_clock_zero": z4_zero,
                "detector_all_zero": z2_zero and z4_zero,
                "detector_any_zero": z2_zero or z4_zero,
            }
        )
    return rows


def build_detector() -> dict[str, Any]:
    alignment_report = load_json(ALIGNMENT_DIR / "report.json")
    constructed_report = load_json(CONSTRUCTED_DIR / "report.json")
    full_match_report = load_json(FULL_MATCH_DIR / "report.json")
    sector33_report = load_json(SECTOR33_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()

    traces = trace_profile_by_generator()
    detector_rows = exact_detector_rows()
    table_rows = detector_table(traces, detector_rows)

    all_zero_sectors = [int(row["source_sector"]) for row in table_rows if row["detector_all_zero"]]
    any_zero_sectors = [int(row["source_sector"]) for row in table_rows if row["detector_any_zero"]]
    sector33_rows = [row for row in table_rows if int(row["source_sector"]) == 33]
    sector33_row = sector33_rows[0] if sector33_rows else {}
    detector_names = [row["quotient_generator"] for row in detector_rows]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generator_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_sector33_detector_generators.csv",
        [
            "quotient_generator",
            "zero_sector_count",
            "zero_sectors",
            "nonzero_sector_count",
            "kernel_is_exact_sector33",
        ],
        detector_rows,
        perennial_maps,
    )
    table_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_sector33_detector_table.csv",
        [
            "source_sector",
            "sector_label",
            "raw_sector",
            "block_dimension",
            "z2_a12_parity_trace_mod",
            "z2_a12_parity_trace_signed",
            "z2_a12_parity_zero",
            "z4_a42_clock_trace_mod",
            "z4_a42_clock_trace_signed",
            "z4_a42_clock_zero",
            "detector_all_zero",
            "detector_any_zero",
        ],
        table_rows,
        perennial_maps,
    )

    checks = {
        "alignment_certified": alignment_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_PUBLIC_ZERO_ALIGNMENT_CERTIFIED"
        and alignment_report.get("all_checks_pass") is True,
        "constructed_representative_certified": constructed_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_CERTIFIED"
        and constructed_report.get("all_checks_pass") is True,
        "full_sector_match_certified": full_match_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_SECTOR_MATCH_CERTIFIED"
        and full_match_report.get("all_checks_pass") is True,
        "sector33_unique_public_zero_certified": sector33_report.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and sector33_report.get("all_checks_pass") is True,
        "detector_generators_are_expected": detector_names == EXPECTED_DETECTORS,
        "detector_generators_have_exact_sector33_kernel": all(
            row["kernel_is_exact_sector33"] and parse_int_list(row["zero_sectors"]) == [33]
            for row in detector_rows
        ),
        "detector_table_has_all_39_source_sectors": len(table_rows) == 39
        and [int(row["source_sector"]) for row in table_rows] == list(range(39)),
        "all_zero_detector_is_unique_sector33": all_zero_sectors == [33],
        "any_zero_detector_is_unique_sector33": any_zero_sectors == [33],
        "sector33_source_to_raw_match_recorded": sector33_row.get("raw_sector") == 19,
        "sector33_block_dimension_is_two": sector33_row.get("block_dimension") == 2,
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            table_perennial_stats["rows_with_perennial_id"]
            == table_perennial_stats["rows_with_direct_sector"]
            == len(table_rows)
            and table_perennial_stats["sector_mismatch_count"] == 0
            and generator_perennial_stats["sector_mismatch_count"] == 0
        ),
    }

    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_sector33_detector.source_drop",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "The constructed Burning/A985 frame-section traces provide a reusable detector for "
            "source sector 33: the selected constructed quotient generators vanish exactly on "
            "source sector 33, so either their individual vanishing or their joint vanishing "
            "selects that sector."
        ),
        "boundary": (
            "This is a repo-native constructed A985-side detector. It does not assert that an "
            "external Burning_static_fields artifact uses the same generator names."
        ),
        "field_prime": FIELD_PRIME,
        "inputs": {
            "public_zero_alignment": {
                "path": rel(ALIGNMENT_DIR / "report.json"),
                "sha256": sha_file(ALIGNMENT_DIR / "report.json"),
            },
            "constructed_representative": {
                "path": rel(CONSTRUCTED_DIR / "report.json"),
                "sha256": sha_file(CONSTRUCTED_DIR / "report.json"),
            },
            "full_sector_match": {
                "path": rel(FULL_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
            },
            "sector33_unique_public_zero": {
                "path": rel(SECTOR33_DIR / "report.json"),
                "sha256": sha_file(SECTOR33_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "detector_generators": detector_names,
            "detected_by_all_zero": all_zero_sectors,
            "detected_by_any_zero": any_zero_sectors,
            "sector33": {
                "source_sector": 33,
                "sector_label": 33,
                "raw_sector": sector33_row.get("raw_sector"),
                "block_dimension": sector33_row.get("block_dimension"),
                "z2_a12_parity_trace_mod": sector33_row.get("z2_a12_parity_trace_mod"),
                "z4_a42_clock_trace_mod": sector33_row.get("z4_a42_clock_trace_mod"),
            },
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "detector_table_rows_resolved": int(table_perennial_stats["rows_with_perennial_id"]),
                "generator_set_columns_added": generator_perennial_stats["added_columns"],
            },
            "tables": {
                "detector_generators": rel(OUT_DIR / "burning_static_sector33_detector_generators.csv"),
                "detector_table": rel(OUT_DIR / "burning_static_sector33_detector_table.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use this sector-33 detector as the acceptance test for any future imported "
            "Burning_static_fields representative rows, then attach accepted rows to the "
            "source-sector matching ledger."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_sector33_detector_manifest.source_drop",
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
    (OUT_DIR / "burning_static_sector33_detector_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    sector33 = report["derived"]["sector33"]
    return (
        "# Burning static sector-33 detector\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        "## Detector\n\n"
        f"- generators: `{report['derived']['detector_generators']}`\n"
        f"- detected by all-zero test: `{report['derived']['detected_by_all_zero']}`\n"
        f"- detected by any-zero test: `{report['derived']['detected_by_any_zero']}`\n"
        f"- source sector 33 raw sector: `{sector33['raw_sector']}`, block dimension: `{sector33['block_dimension']}`\n\n"
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
    generator_rows = read_csv_rows(OUT_DIR / "burning_static_sector33_detector_generators.csv")
    table_rows = read_csv_rows(OUT_DIR / "burning_static_sector33_detector_table.csv")
    all_zero = [int(row["source_sector"]) for row in table_rows if row["detector_all_zero"] == "True"]
    any_zero = [int(row["source_sector"]) for row in table_rows if row["detector_any_zero"] == "True"]
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "generator_rows_count_is_2": len(generator_rows) == 2,
        "generator_rows_are_exact_sector33": all(
            row["kernel_is_exact_sector33"] == "True" and parse_int_list(row["zero_sectors"]) == [33]
            for row in generator_rows
        ),
        "detector_table_has_39_rows": len(table_rows) == 39,
        "detected_all_zero_is_sector33": all_zero == [33],
        "detected_any_zero_is_sector33": any_zero == [33],
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in table_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in table_rows)
            and "zero_sectors_perennial_ids" in generator_rows[0]
        ),
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
        build_detector()
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
