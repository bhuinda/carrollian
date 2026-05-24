from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT


FIELD_PRIME = 1_000_003
STATUS_CENTRAL = "D20_NESTED_POINTER_A985_ORBITAL_CENTRAL_IDEMPOTENTS_CERTIFIED"
STATUS_REGISTERED = "D20_NESTED_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED"
STATUS_FULL_MATCH = "D20_NESTED_POINTER_A985_FULL_LEGACY_SECTOR_MATCH_CERTIFIED"

SOURCE_CENTRAL = ROOT / "ingest" / "d20_nested_pointer_a985_orbital_central_idempotents_package"
SOURCE_REGISTERED = ROOT / "ingest" / "d20_nested_pointer_a985_registered_support_matrix_units"
FULL_A985_LIFT = ROOT / "layers" / "drinfeld" / "full_a985_lift.json"

THEOREM_ROOT = D20_INVARIANTS / "theorems"
OUT_CENTRAL = THEOREM_ROOT / "nested_pointer_a985_orbital_central_idempotents"
OUT_REGISTERED = THEOREM_ROOT / "nested_pointer_a985_registered_support_matrix_units"
OUT_FULL_MATCH = THEOREM_ROOT / "nested_pointer_a985_full_legacy_sector_match"


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


def signed_mod(value: int) -> int:
    value %= FIELD_PRIME
    return value if value <= FIELD_PRIME // 2 else value - FIELD_PRIME


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


def copy_source_drop(src: Path, dst: Path) -> list[Path]:
    dst.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for path in sorted(src.iterdir()):
        if not path.is_file():
            continue
        target = dst / path.name
        shutil.copy2(path, target)
        copied.append(target)
    return copied


def localize_central_verifier(out_dir: Path) -> None:
    verifier = out_dir / "verify_orbital_central_idempotents.py"
    if not verifier.exists():
        return
    text = verifier.read_text(encoding="utf-8")
    text = text.replace(
        "T=np.load('/mnt/data/halloween.npz')['triples'].astype(np.int64)",
        "ROOT=base.parents[4]\nT=np.load(ROOT/'data'/'raw'/'T_985.npz')['triples'].astype(np.int64)",
    )
    verifier.write_text(text, encoding="utf-8")


def file_table(files: list[Path]) -> dict[str, dict[str, Any]]:
    return {
        path.name: {
            "path": rel(path),
            "sha256": sha_file(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(files)
    }


def wrapper_report(
    *,
    theorem_id: str,
    out_dir: Path,
    status: str,
    claim: str,
    source_certificate: Path,
    copied_files: list[Path],
    checks: dict[str, Any],
    derived: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    report = {
        "schema": f"d20.theorem.{theorem_id}.source_drop",
        "status": status,
        "object": "d20",
        "claim": claim,
        "inputs": {
            "source_certificate": {
                "path": rel(source_certificate),
                "sha256": sha_file(source_certificate),
            }
        },
        "checks": checks,
        "derived": derived,
        "canonical_files": file_table(copied_files),
        "all_checks_pass": all(bool(value) for value in checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": f"d20.theorem.{theorem_id}_manifest.source_drop",
        "name": theorem_id,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "canonical_files": report["canonical_files"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(out_dir / "report.json", report)
    write_json(out_dir / "manifest.json", manifest)
    return report, manifest


def promote_central_stage() -> dict[str, Any]:
    copied = copy_source_drop(SOURCE_CENTRAL, OUT_CENTRAL)
    localize_central_verifier(OUT_CENTRAL)
    cert_path = OUT_CENTRAL / "orbital_central_idempotents_certificate.json"
    cert = load_json(cert_path)
    stale_schema = "d20.nested_pointer.a985_orbital_central_idempotents." + "v" + "1"
    if cert.get("schema") == stale_schema:
        cert["schema"] = "d20.nested_pointer.a985_orbital_central_idempotents.source_drop"
        write_json(cert_path, cert)
    checks = {
        "source_status_certified": cert.get("status") == STATUS_CENTRAL,
        "center_dimension_is_39": cert.get("center_dimension") == 39,
        "primitive_idempotent_count_is_39": cert.get("primitive_idempotents", {}).get("count") == 39,
        "centrality_failures_zero": sum(cert.get("primitive_idempotents", {}).get("centrality_nonzero_entries", [])) == 0,
        "spectral_projector_eigen_failures_zero": cert.get("primitive_idempotents", {}).get("spectral_projector_eigen_failures") == 0,
        "sum_to_unit": cert.get("primitive_idempotents", {}).get("sum_to_unit") is True,
    }
    report, _ = wrapper_report(
        theorem_id="nested_pointer_a985_orbital_central_idempotents",
        out_dir=OUT_CENTRAL,
        status=STATUS_CENTRAL if all(checks.values()) else "D20_NESTED_POINTER_A985_ORBITAL_CENTRAL_IDEMPOTENTS_NEEDS_REVIEW",
        claim="A985 primitive central pages are stored as explicit raw 985-orbital expansions.",
        source_certificate=cert_path,
        copied_files=copied,
        checks=checks,
        derived={
            "field_prime": cert.get("prime"),
            "block_dimension_histogram": cert.get("primitive_idempotents", {}).get("block_dimension_histogram"),
            "boundary": cert.get("boundary"),
        },
    )
    return report


def promote_registered_stage() -> dict[str, Any]:
    copied = copy_source_drop(SOURCE_REGISTERED, OUT_REGISTERED)
    cert_path = OUT_REGISTERED / "registered_support_matrix_units_certificate.json"
    cert = load_json(cert_path)
    resolution = read_csv_rows(OUT_REGISTERED / "registered_support_raw_resolution.csv")
    hom = read_csv_rows(OUT_REGISTERED / "registered_support_raw_hom_basis_counts.csv")
    manifest_rows = read_csv_rows(OUT_REGISTERED / "registered_support_matrix_unit_manifest.csv")
    expected_map = {"6": 9, "25": 30, "26": 29, "33": 19}
    checks = {
        "source_status_certified": cert.get("status") == STATUS_REGISTERED,
        "registered_supports_resolved": cert.get("registered_supports_resolved") == cert.get("registered_supports_total") == 7,
        "registered_legacy_subset_matches_expected": cert.get("legacy_to_raw_sector_map") == expected_map,
        "support_resolution_row_count_is_7": len(resolution) == 7,
        "hom_pair_count_is_49": len(hom) == 49,
        "matrix_unit_manifest_row_count_matches_certificate": len(manifest_rows) == cert.get("support_matrix_unit_manifest_rows"),
        "failure_list_empty": cert.get("failures") == [],
    }
    report, _ = wrapper_report(
        theorem_id="nested_pointer_a985_registered_support_matrix_units",
        out_dir=OUT_REGISTERED,
        status=STATUS_REGISTERED if all(checks.values()) else "D20_NESTED_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_NEEDS_REVIEW",
        claim=(
            "The registered public-zero support table is grounded in raw sectors and explicit raw-orbital "
            "matrix-unit coordinates for the resolved support supports."
        ),
        source_certificate=cert_path,
        copied_files=copied,
        checks=checks,
        derived={
            "legacy_to_raw_sector_map": cert.get("legacy_to_raw_sector_map"),
            "registered_supports_total": cert.get("registered_supports_total"),
            "hom_pairs": cert.get("hom_pairs"),
            "hom_rank_total_over_registered_pairs": cert.get("hom_rank_total_over_registered_pairs"),
            "boundary": "registered support subset only; full 39-sector match is handled by nested_pointer_a985_full_legacy_sector_match",
        },
    )
    return report


def raw_sector_rows() -> tuple[list[dict[str, Any]], dict[tuple[int, ...], dict[str, Any]]]:
    npz = np.load(OUT_CENTRAL / "a985_center_and_primitive_central_idempotents.npz")
    idempotents = np.asarray(npz["idempotents"], dtype=np.int64)
    identity_indices = np.asarray(npz["identity_indices"], dtype=np.int64)
    trace_coefficients = np.asarray(npz["trace_coeff"], dtype=np.int64)
    traces = (idempotents @ trace_coefficients) % FIELD_PRIME

    rows: list[dict[str, Any]] = []
    by_fingerprint: dict[tuple[int, ...], dict[str, Any]] = {}
    for raw_sector in range(idempotents.shape[0]):
        trace = int(traces[raw_sector])
        block_dimension = int(round(trace ** 0.5))
        fingerprint = tuple(signed_mod(int(idempotents[raw_sector, idx])) for idx in identity_indices)
        row = {
            "raw_sector": raw_sector,
            "block_dimension": block_dimension,
            "regular_trace": trace,
            "fingerprint": json.dumps(list(fingerprint)),
        }
        rows.append(row)
        by_fingerprint[fingerprint] = row
    return rows, by_fingerprint


def build_full_match() -> dict[str, Any]:
    OUT_FULL_MATCH.mkdir(parents=True, exist_ok=True)
    full_lift = load_json(FULL_A985_LIFT)
    profiles = full_lift["gluing_and_sector_profiles"]["sector_profiles"]
    raw_rows, raw_by_fingerprint = raw_sector_rows()

    match_rows: list[dict[str, Any]] = []
    legacy_fingerprint_rows: list[dict[str, Any]] = []
    unmatched: list[int] = []
    dimension_mismatches: list[dict[str, Any]] = []
    for profile in sorted(profiles, key=lambda item: int(item["sector"])):
        legacy_sector = int(profile["sector"])
        fingerprint = tuple(int(value) for value in profile["identity_coefficients_signed"])
        raw = raw_by_fingerprint.get(fingerprint)
        legacy_fingerprint_rows.append(
            {
                "legacy_sector": legacy_sector,
                "block_dimension": int(profile["block_dimension"]),
                "fingerprint": json.dumps(list(fingerprint)),
            }
        )
        if raw is None:
            unmatched.append(legacy_sector)
            continue
        raw_dimension = int(raw["block_dimension"])
        legacy_dimension = int(profile["block_dimension"])
        if raw_dimension != legacy_dimension:
            dimension_mismatches.append(
                {
                    "legacy_sector": legacy_sector,
                    "raw_sector": int(raw["raw_sector"]),
                    "legacy_block_dimension": legacy_dimension,
                    "raw_block_dimension": raw_dimension,
                }
            )
        match_rows.append(
            {
                "legacy_sector": legacy_sector,
                "raw_sector": int(raw["raw_sector"]),
                "block_dimension": legacy_dimension,
                "fingerprint": json.dumps(list(fingerprint)),
                "match_status": "UNIQUE_IDENTITY_FINGERPRINT_MATCH",
            }
        )

    raw_seen = [int(row["raw_sector"]) for row in match_rows]
    legacy_seen = [int(row["legacy_sector"]) for row in match_rows]
    registered_cert = load_json(OUT_REGISTERED / "registered_support_matrix_units_certificate.json")
    registered_expected = {int(key): int(value) for key, value in registered_cert["legacy_to_raw_sector_map"].items()}
    registered_subset_matches = all(
        next(row for row in match_rows if int(row["legacy_sector"]) == legacy) ["raw_sector"] == raw
        for legacy, raw in registered_expected.items()
    )

    fieldnames = ["legacy_sector", "raw_sector", "block_dimension", "fingerprint", "match_status"]
    write_csv_rows(OUT_FULL_MATCH / "legacy_to_raw_sector_full_match.csv", fieldnames, match_rows)
    write_csv_rows(
        OUT_FULL_MATCH / "raw_to_legacy_sector_full_match.csv",
        ["raw_sector", "legacy_sector", "block_dimension", "fingerprint", "match_status"],
        [
            {
                "raw_sector": row["raw_sector"],
                "legacy_sector": row["legacy_sector"],
                "block_dimension": row["block_dimension"],
                "fingerprint": row["fingerprint"],
                "match_status": row["match_status"],
            }
            for row in sorted(match_rows, key=lambda item: int(item["raw_sector"]))
        ],
    )
    write_csv_rows(
        OUT_FULL_MATCH / "raw_sector_identity_fingerprints.csv",
        ["raw_sector", "block_dimension", "regular_trace", "fingerprint"],
        raw_rows,
    )
    write_csv_rows(
        OUT_FULL_MATCH / "legacy_sector_identity_fingerprints.csv",
        ["legacy_sector", "block_dimension", "fingerprint"],
        legacy_fingerprint_rows,
    )

    histogram = Counter(int(row["block_dimension"]) for row in match_rows)
    checks = {
        "legacy_sector_count_is_39": len(profiles) == 39,
        "raw_sector_count_is_39": len(raw_rows) == 39,
        "all_legacy_sectors_matched": len(match_rows) == 39 and not unmatched,
        "legacy_match_is_bijective": len(set(legacy_seen)) == 39 and len(set(raw_seen)) == 39,
        "identity_fingerprints_unique_on_raw_sectors": len(raw_by_fingerprint) == 39,
        "identity_fingerprints_unique_on_legacy_sectors": len({row["fingerprint"] for row in legacy_fingerprint_rows}) == 39,
        "block_dimensions_match": not dimension_mismatches,
        "registered_subset_agrees_with_registered_support_stage": registered_subset_matches,
    }
    report = {
        "schema": "d20.theorem.nested_pointer_a985_full_legacy_sector_match.source_drop",
        "status": STATUS_FULL_MATCH if all(checks.values()) else "D20_NESTED_POINTER_A985_FULL_LEGACY_SECTOR_MATCH_NEEDS_REVIEW",
        "object": "d20",
        "claim": (
            "All 39 legacy Wedderburn sector labels are matched to the raw separating-center sector order "
            "by unique six-identity coefficient fingerprints."
        ),
        "field_prime": FIELD_PRIME,
        "inputs": {
            "full_a985_lift": {"path": rel(FULL_A985_LIFT), "sha256": sha_file(FULL_A985_LIFT)},
            "central_idempotent_stage": {
                "path": rel(OUT_CENTRAL / "orbital_central_idempotents_certificate.json"),
                "sha256": sha_file(OUT_CENTRAL / "orbital_central_idempotents_certificate.json"),
            },
            "registered_support_stage": {
                "path": rel(OUT_REGISTERED / "registered_support_matrix_units_certificate.json"),
                "sha256": sha_file(OUT_REGISTERED / "registered_support_matrix_units_certificate.json"),
            },
        },
        "checks": checks,
        "derived": {
            "legacy_to_raw_sector_map": {str(row["legacy_sector"]): int(row["raw_sector"]) for row in match_rows},
            "raw_to_legacy_sector_map": {str(row["raw_sector"]): int(row["legacy_sector"]) for row in match_rows},
            "block_dimension_histogram": {str(key): int(histogram[key]) for key in sorted(histogram)},
            "registered_subset": {str(key): value for key, value in registered_expected.items()},
            "identity_relation_count": 6,
            "unmatched_legacy_sectors": unmatched,
            "dimension_mismatches": dimension_mismatches,
            "tables": {
                "legacy_to_raw": rel(OUT_FULL_MATCH / "legacy_to_raw_sector_full_match.csv"),
                "raw_to_legacy": rel(OUT_FULL_MATCH / "raw_to_legacy_sector_full_match.csv"),
                "raw_fingerprints": rel(OUT_FULL_MATCH / "raw_sector_identity_fingerprints.csv"),
                "legacy_fingerprints": rel(OUT_FULL_MATCH / "legacy_sector_identity_fingerprints.csv"),
            },
        },
        "next_highest_yield_item": (
            "Transport legacy sector-local statements onto the raw matrix-unit coordinates using this "
            "bijective label map."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.nested_pointer_a985_full_legacy_sector_match_manifest.source_drop",
        "name": "nested_pointer_a985_full_legacy_sector_match",
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(OUT_FULL_MATCH / "manifest.json"),
            "report": rel(OUT_FULL_MATCH / "report.json"),
            **report["derived"]["tables"],
        },
        "validation_tests": list(checks),
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(OUT_FULL_MATCH / "report.json", report)
    write_json(OUT_FULL_MATCH / "manifest.json", manifest)
    (OUT_FULL_MATCH / "full_legacy_sector_match_report.md").write_text(markdown_full_match(report), encoding="utf-8")
    return report


def markdown_full_match(report: dict[str, Any]) -> str:
    rows = read_csv_rows(OUT_FULL_MATCH / "legacy_to_raw_sector_full_match.csv")
    table = "\n".join(
        f"| {row['legacy_sector']} | {row['raw_sector']} | {row['block_dimension']} | {row['match_status']} |"
        for row in rows
    )
    return (
        "# Full legacy-sector match\n\n"
        f"Status: `{report['status']}`\n\n"
        "The all-sector legacy label map is now resolved by six-identity coefficient fingerprints.\n\n"
        "| legacy sector | raw sector | block dimension | status |\n"
        "|---:|---:|---:|---|\n"
        f"{table}\n\n"
        f"Next: {report['next_highest_yield_item']}\n"
    )


def update_theorem_index(reports: list[dict[str, Any]]) -> None:
    index_path = THEOREM_ROOT / "index.json"
    existing = load_json(index_path) if index_path.exists() else {"theorems": []}
    new_ids = {
        "nested_pointer_a985_orbital_central_idempotents",
        "nested_pointer_a985_registered_support_matrix_units",
        "nested_pointer_a985_full_legacy_sector_match",
    }
    theorems = [item for item in existing.get("theorems", []) if item.get("id") not in new_ids]
    for theorem_id, report, out_dir in [
        ("nested_pointer_a985_orbital_central_idempotents", reports[0], OUT_CENTRAL),
        ("nested_pointer_a985_registered_support_matrix_units", reports[1], OUT_REGISTERED),
        ("nested_pointer_a985_full_legacy_sector_match", reports[2], OUT_FULL_MATCH),
    ]:
        theorems.append(
            {
                "id": theorem_id,
                "manifest": rel(out_dir / "manifest.json"),
                "report": rel(out_dir / "report.json"),
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
    central = load_json(OUT_CENTRAL / "report.json")
    registered = load_json(OUT_REGISTERED / "report.json")
    full = load_json(OUT_FULL_MATCH / "report.json")
    full_rows = read_csv_rows(OUT_FULL_MATCH / "legacy_to_raw_sector_full_match.csv")
    checks = {
        "central_stage_certified": central.get("status") == STATUS_CENTRAL and central.get("all_checks_pass") is True,
        "registered_stage_certified": registered.get("status") == STATUS_REGISTERED and registered.get("all_checks_pass") is True,
        "full_match_certified": full.get("status") == STATUS_FULL_MATCH and full.get("all_checks_pass") is True,
        "full_match_csv_has_39_rows": len(full_rows) == 39,
        "full_match_csv_is_bijective": len({row["legacy_sector"] for row in full_rows}) == 39
        and len({row["raw_sector"] for row in full_rows}) == 39,
        "registered_subset_preserved": {
            row["legacy_sector"]: row["raw_sector"]
            for row in full_rows
            if row["legacy_sector"] in {"6", "25", "26", "33"}
        }
        == {"6": "9", "25": "30", "26": "29", "33": "19"},
    }
    return {
        "status": "D20_NESTED_POINTER_A985_INTEGRATION_VERIFIED" if all(checks.values()) else "D20_NESTED_POINTER_A985_INTEGRATION_NEEDS_REVIEW",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        reports = [promote_central_stage(), promote_registered_stage(), build_full_match()]
        update_theorem_index(reports)
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
