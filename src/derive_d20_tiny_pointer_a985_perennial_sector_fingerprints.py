from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import ast
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


FIELD_PRIME = 1_000_003
THEOREM_ID = "tiny_pointer_a985_perennial_sector_fingerprints"
STATUS = "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_FINGERPRINTS_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_FINGERPRINTS_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_FINGERPRINTS_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
FULL_SECTOR_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_sector_match"
CHARACTER_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters"
CONVENTION_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_source_basis_convention"
BURNING_STATIC_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_constructed_representative"
)
SUPPORT_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_support_full_matrix_unit_orbital_coo"


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


def parse_identity_fingerprint(value: str) -> list[int]:
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list) or not all(isinstance(item, int) for item in parsed):
        raise ValueError(f"invalid identity fingerprint: {value}")
    return parsed


def parse_int_set(value: str) -> set[int]:
    text = value.strip()
    if text == "{}":
        return set()
    if not (text.startswith("{") and text.endswith("}")):
        raise ValueError(f"invalid set literal: {value}")
    body = text[1:-1].strip()
    if not body:
        return set()
    return {int(part.strip()) for part in body.split(",")}


def support_membership_by_sector() -> dict[int, dict[str, list[str]]]:
    memberships: dict[int, dict[str, list[str]]] = {
        sector: {"names": [], "projector_sha256s": []} for sector in range(39)
    }
    for row in read_csv_rows(SUPPORT_COO_DIR / "support_projector_summary.csv"):
        name = row["support_name"]
        if name in {"unit_top_all_39", "zero"}:
            continue
        support = parse_int_set(row["transported_source_support"])
        for sector in support:
            memberships[sector]["names"].append(name)
            memberships[sector]["projector_sha256s"].append(row["projector_sha256"])
    return {
        sector: {
            "names": sorted(values["names"]),
            "projector_sha256s": sorted(values["projector_sha256s"]),
        }
        for sector, values in memberships.items()
    }


def burning_trace_by_sector() -> dict[int, dict[str, dict[str, Any]]]:
    traces: dict[int, dict[str, dict[str, Any]]] = {sector: {} for sector in range(39)}
    for row in read_csv_rows(BURNING_STATIC_DIR / "burning_static_constructed_trace_profile.csv"):
        sector = int(row["source_sector"])
        generator = row["quotient_generator"]
        traces[sector][generator] = {
            "trace_signed": int(row["trace_signed"]),
            "trace_mod_1000003": int(row["trace_mod_1000003"]),
            "sector_in_support": row["sector_in_support"] == "True",
        }
    return traces


def semantic_payload(
    sector_match: dict[str, str],
    character: dict[str, str],
    convention: dict[str, str],
    burning: dict[str, dict[str, Any]],
    support_projector_sha256s: list[str],
) -> dict[str, Any]:
    return {
        "schema": "d20.a985.perennial_sector_fingerprint_payload",
        "object": "d20/A985",
        "field_prime": FIELD_PRIME,
        "block_dimension": int(sector_match["block_dimension"]),
        "six_identity_trace_fingerprint_signed": parse_identity_fingerprint(sector_match["fingerprint"]),
        "canonical_character_row_sha256": character["character_row_sha256"],
        "character_nonzero_values": int(character["nonzero_character_values"]),
        "burning_ship_static_traces": {
            key: burning[key]
            for key in sorted(burning)
        },
        "public_zero_support_projector_sha256_memberships": support_projector_sha256s,
        "matrix_unit_count": int(convention["matrix_unit_count"]),
        "semantic_note": "current source/raw sector labels are intentionally excluded from this payload",
    }


def coordinate_payload(
    semantic_id: str,
    convention: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema": "d20.a985.perennial_sector_coordinate_payload",
        "semantic_perennial_id": semantic_id,
        "field_prime": FIELD_PRIME,
        "repo_basis_convention": "tiny_pointer_a985_source_basis_convention",
        "convention_status": convention["convention_status"],
        "coefficient_source": convention["coefficient_source"],
        "identity_gl_transform": convention["identity_gl_transform"] == "True",
        "matrix_unit_block_sha256": convention["matrix_unit_block_sha256"],
        "repo_convention_residual_gauge_dimension": int(
            convention["repo_convention_residual_gauge_dimension"]
        ),
    }


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sector_match_rows = {
        int(row["source_sector"]): row
        for row in read_csv_rows(FULL_SECTOR_MATCH_DIR / "source_to_raw_sector_full_match.csv")
    }
    character_rows = {
        int(row["source_sector"]): row
        for row in read_csv_rows(CHARACTER_DIR / "canonical_sector_trace_summary.csv")
    }
    convention_rows = {
        int(row["source_sector"]): row
        for row in read_csv_rows(CONVENTION_DIR / "source_matrix_unit_basis_convention_by_sector.csv")
    }
    support_rows = support_membership_by_sector()
    burning_rows = burning_trace_by_sector()

    rows: list[dict[str, Any]] = []
    payloads: list[dict[str, Any]] = []
    for source_sector in sorted(sector_match_rows):
        sector_match = sector_match_rows[source_sector]
        character = character_rows[source_sector]
        convention = convention_rows[source_sector]
        semantic = semantic_payload(
            sector_match,
            character,
            convention,
            burning_rows[source_sector],
            support_rows[source_sector]["projector_sha256s"],
        )
        semantic_sha = sha_json(semantic)
        perennial_id = f"a985pf.{semantic_sha[:24]}"
        coordinate = coordinate_payload(perennial_id, convention)
        coordinate_sha = sha_json(coordinate)
        rows.append(
            {
                "source_sector": source_sector,
                "raw_sector": int(sector_match["raw_sector"]),
                "perennial_id": perennial_id,
                "perennial_payload_sha256": semantic_sha,
                "coordinate_fingerprint_id": f"a985coord.{coordinate_sha[:24]}",
                "coordinate_payload_sha256": coordinate_sha,
                "block_dimension": int(sector_match["block_dimension"]),
                "matrix_unit_count": int(convention["matrix_unit_count"]),
                "six_identity_trace_fingerprint_signed": sector_match["fingerprint"],
                "canonical_character_row_sha256": character["character_row_sha256"],
                "matrix_unit_block_sha256": convention["matrix_unit_block_sha256"],
                "convention_status": convention["convention_status"],
                "burning_ship_trace_signature": json.dumps(
                    {
                        key: burning_rows[source_sector][key]["trace_signed"]
                        for key in sorted(burning_rows[source_sector])
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "public_zero_support_projector_sha256_memberships": "|".join(
                    support_rows[source_sector]["projector_sha256s"]
                ),
                "public_zero_support_name_aliases": "|".join(support_rows[source_sector]["names"]),
            }
        )
        payloads.append(
            {
                "source_sector": source_sector,
                "raw_sector": int(sector_match["raw_sector"]),
                "perennial_id": perennial_id,
                "perennial_payload_sha256": semantic_sha,
                "semantic_payload": semantic,
                "coordinate_fingerprint_id": f"a985coord.{coordinate_sha[:24]}",
                "coordinate_payload_sha256": coordinate_sha,
                "coordinate_payload": coordinate,
            }
        )
    return rows, payloads


def build_theorem() -> dict[str, Any]:
    sector_match_report = load_json(FULL_SECTOR_MATCH_DIR / "report.json")
    character_report = load_json(CHARACTER_DIR / "report.json")
    convention_report = load_json(CONVENTION_DIR / "report.json")
    burning_report = load_json(BURNING_STATIC_DIR / "report.json")
    support_report = load_json(SUPPORT_COO_DIR / "report.json")
    rows, payloads = build_rows()

    perennial_ids = [row["perennial_id"] for row in rows]
    coordinate_ids = [row["coordinate_fingerprint_id"] for row in rows]
    payload_shas = [row["perennial_payload_sha256"] for row in rows]
    coordinate_shas = [row["coordinate_payload_sha256"] for row in rows]
    dimension_histogram = Counter(str(row["block_dimension"]) for row in rows)
    support_membership_histogram = Counter(
        row["public_zero_support_projector_sha256_memberships"]
        if row["public_zero_support_projector_sha256_memberships"]
        else "none"
        for row in rows
    )
    payload_has_no_current_labels = all(
        "source_sector" not in item["semantic_payload"]
        and "raw_sector" not in item["semantic_payload"]
        for item in payloads
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "perennial_sector_fingerprints.csv",
        [
            "source_sector",
            "raw_sector",
            "perennial_id",
            "perennial_payload_sha256",
            "coordinate_fingerprint_id",
            "coordinate_payload_sha256",
            "block_dimension",
            "matrix_unit_count",
            "six_identity_trace_fingerprint_signed",
            "canonical_character_row_sha256",
            "matrix_unit_block_sha256",
            "convention_status",
            "burning_ship_trace_signature",
            "public_zero_support_projector_sha256_memberships",
            "public_zero_support_name_aliases",
        ],
        rows,
    )
    write_json(
        OUT_DIR / "perennial_sector_fingerprint_payloads.json",
        {
            "schema": "d20.a985.perennial_sector_fingerprint_payloads",
            "field_prime": FIELD_PRIME,
            "payloads": payloads,
        },
    )
    write_json(
        OUT_DIR / "perennial_sector_fingerprint_lookup.json",
        {
            "schema": "d20.a985.perennial_sector_fingerprint_lookup",
            "field_prime": FIELD_PRIME,
            "lookup": {
                row["perennial_id"]: {
                    "source_sector": row["source_sector"],
                    "raw_sector": row["raw_sector"],
                    "block_dimension": row["block_dimension"],
                    "coordinate_fingerprint_id": row["coordinate_fingerprint_id"],
                }
                for row in rows
            },
        },
    )

    checks = {
        "full_sector_match_certified": sector_match_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_SECTOR_MATCH_CERTIFIED"
        and sector_match_report.get("all_checks_pass") is True,
        "canonical_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "source_basis_convention_certified": convention_report.get("status")
        == "D20_TINY_POINTER_A985_SOURCE_BASIS_CONVENTION_CERTIFIED"
        and convention_report.get("all_checks_pass") is True,
        "burning_static_representative_certified": burning_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_CERTIFIED"
        and burning_report.get("all_checks_pass") is True,
        "support_full_matrix_unit_coo_certified": support_report.get("status")
        == "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and support_report.get("all_checks_pass") is True,
        "fingerprint_rows_cover_39_sectors": len(rows) == 39,
        "perennial_ids_are_unique": len(set(perennial_ids)) == 39,
        "coordinate_fingerprint_ids_are_unique": len(set(coordinate_ids)) == 39,
        "perennial_payload_hashes_are_unique": len(set(payload_shas)) == 39,
        "coordinate_payload_hashes_are_unique": len(set(coordinate_shas)) == 39,
        "semantic_payloads_exclude_current_labels": payload_has_no_current_labels,
        "matrix_unit_count_is_985": sum(int(row["matrix_unit_count"]) for row in rows) == 985,
        "dimension_histogram_matches_wedderburn_profile": dict(sorted(dimension_histogram.items(), key=lambda kv: int(kv[0])))
        == {
            "1": 7,
            "2": 8,
            "3": 4,
            "4": 8,
            "5": 4,
            "6": 2,
            "8": 1,
            "9": 1,
            "10": 2,
            "11": 1,
            "12": 1,
        },
        "payload_json_emitted": (OUT_DIR / "perennial_sector_fingerprint_payloads.json").exists(),
        "lookup_json_emitted": (OUT_DIR / "perennial_sector_fingerprint_lookup.json").exists(),
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_perennial_sector_fingerprints.source_drop",
        "status": STATUS,
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "All 39 A985 source sectors now have label-independent perennial fingerprints. "
            "The semantic fingerprint payload excludes current source/raw sector labels and combines "
            "the six-identity trace fingerprint, canonical character row hash, Burning Ship static "
            "trace signature, public-zero support projector-hash memberships, and block dimension. A separate "
            "coordinate fingerprint binds the same semantic sector to the repository matrix-unit basis."
        ),
        "boundary": (
            "These are canonical repository identifiers, not a theorem that all future external "
            "presentations must use the same raw relation order. External presentations should be "
            "matched by recomputing the semantic payload or by solving into the repo basis convention."
        ),
        "inputs": {
            "full_sector_match": {
                "path": rel(FULL_SECTOR_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_SECTOR_MATCH_DIR / "report.json"),
            },
            "canonical_sector_characters": {
                "path": rel(CHARACTER_DIR / "report.json"),
                "sha256": sha_file(CHARACTER_DIR / "report.json"),
            },
            "source_basis_convention": {
                "path": rel(CONVENTION_DIR / "report.json"),
                "sha256": sha_file(CONVENTION_DIR / "report.json"),
            },
            "burning_static_constructed_representative": {
                "path": rel(BURNING_STATIC_DIR / "report.json"),
                "sha256": sha_file(BURNING_STATIC_DIR / "report.json"),
            },
            "support_full_matrix_unit_orbital_coo": {
                "path": rel(SUPPORT_COO_DIR / "report.json"),
                "sha256": sha_file(SUPPORT_COO_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "sector_count": len(rows),
            "matrix_unit_count": sum(int(row["matrix_unit_count"]) for row in rows),
            "dimension_histogram": dict(sorted(dimension_histogram.items(), key=lambda kv: int(kv[0]))),
            "support_membership_histogram": dict(sorted(support_membership_histogram.items())),
            "perennial_id_prefix": "a985pf",
            "coordinate_fingerprint_prefix": "a985coord",
            "tables": {
                "fingerprints_csv": rel(OUT_DIR / "perennial_sector_fingerprints.csv"),
                "payloads_json": rel(OUT_DIR / "perennial_sector_fingerprint_payloads.json"),
                "lookup_json": rel(OUT_DIR / "perennial_sector_fingerprint_lookup.json"),
            },
        },
        "next_highest_yield_item": (
            "Use perennial_id as the sector name in new reports, and keep source/raw sector numbers only "
            "as current-coordinate aliases."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_perennial_sector_fingerprints_manifest.source_drop",
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
    (OUT_DIR / "perennial_sector_fingerprints_report.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# A985 perennial sector fingerprints\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        f"Perennial ID prefix: `{derived['perennial_id_prefix']}`\n\n"
        f"Coordinate fingerprint prefix: `{derived['coordinate_fingerprint_prefix']}`\n\n"
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
    rows = read_csv_rows(OUT_DIR / "perennial_sector_fingerprints.csv")
    payloads = load_json(OUT_DIR / "perennial_sector_fingerprint_payloads.json")
    lookup = load_json(OUT_DIR / "perennial_sector_fingerprint_lookup.json")
    perennial_ids = [row["perennial_id"] for row in rows]
    coordinate_ids = [row["coordinate_fingerprint_id"] for row in rows]
    payload_rows = payloads.get("payloads", [])
    recomputed_perennial = [
        sha_json(item["semantic_payload"]) == item["perennial_payload_sha256"]
        and item["perennial_id"] == f"a985pf.{item['perennial_payload_sha256'][:24]}"
        for item in payload_rows
    ]
    recomputed_coordinate = [
        sha_json(item["coordinate_payload"]) == item["coordinate_payload_sha256"]
        and item["coordinate_fingerprint_id"] == f"a985coord.{item['coordinate_payload_sha256'][:24]}"
        for item in payload_rows
    ]
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "fingerprint_rows_cover_39": len(rows) == 39,
        "payload_rows_cover_39": len(payload_rows) == 39,
        "lookup_rows_cover_39": len(lookup.get("lookup", {})) == 39,
        "perennial_ids_unique": len(set(perennial_ids)) == 39,
        "coordinate_ids_unique": len(set(coordinate_ids)) == 39,
        "perennial_ids_match_payload_hashes": all(recomputed_perennial),
        "coordinate_ids_match_payload_hashes": all(recomputed_coordinate),
        "semantic_payloads_exclude_current_labels": all(
            "source_sector" not in item["semantic_payload"]
            and "raw_sector" not in item["semantic_payload"]
            for item in payload_rows
        ),
        "matrix_unit_count_is_985": sum(int(row["matrix_unit_count"]) for row in rows) == 985,
        "report_checks_all_true": all(report.get("checks", {}).values()),
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

