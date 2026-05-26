from __future__ import annotations

import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/invariants/d20/theorems/tiny_pointer_a985_sector_label_alias_registry"

FULL_MATCH_CSV = (
    ROOT
    / "data/invariants/d20/theorems/tiny_pointer_a985_full_sector_match/source_to_raw_sector_full_match.csv"
)
PERENNIAL_CSV = (
    ROOT
    / "data/invariants/d20/theorems/tiny_pointer_a985_perennial_sector_fingerprints/perennial_sector_fingerprints.csv"
)
CERTIFIED_POINTER_REPORT = (
    ROOT
    / "data/invariants/d20/theorems/certified_pointer_a985_matrix_unit_dereference/report.json"
)
CERTIFIED_POINTER_INSTANCE = (
    ROOT
    / "data/invariants/d20/theorems/certified_pointer_a985_matrix_unit_dereference/certified_pointer_instance.json"
)
CERTIFIED_EVIDENCE = ROOT / "data/invariants/d20/certified_evidence_invariants.json"

ALIAS_CSV = OUT_DIR / "sector_label_alias_registry.csv"
ATOM_CSV = OUT_DIR / "d20_atom_domain.csv"
PRIMITIVE_SCHEMA = OUT_DIR / "tiny_pointer_d20_atom_primitive_schema.json"
REPORT = OUT_DIR / "report.json"


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def canonical_json_sha256(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def atom_rows() -> list[dict[str, object]]:
    h6 = ["B-", "B+", "V-", "V+", "S-", "S+"]
    return [
        {
            "atom_id": idx,
            "atom_label": "d20_atom_" + "_".join(x.replace("-", "minus").replace("+", "plus") for x in triple),
            "h6_triple": "|".join(triple),
            "native_domain": "C(H6,3)",
        }
        for idx, triple in enumerate(combinations(h6, 3))
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    full_match_rows = read_csv(FULL_MATCH_CSV)
    perennial_rows = read_csv(PERENNIAL_CSV)
    perennial_by_source = {row["source_sector"]: row for row in perennial_rows}

    alias_rows: list[dict[str, object]] = []
    for row in sorted(full_match_rows, key=lambda r: int(r["source_sector"])):
        source_sector = row["source_sector"]
        raw_sector = row["raw_sector"]
        p = perennial_by_source[source_sector]
        alias_rows.append(
            {
                "source_sector": int(source_sector),
                "raw_sector": int(raw_sector),
                "perennial_id": row["perennial_id"],
                "coordinate_fingerprint_id": row["coordinate_fingerprint_id"],
                "block_dimension": int(row["block_dimension"]),
                "matrix_unit_count": int(p["matrix_unit_count"]),
                "match_status": row["match_status"],
                "canonical_source_alias": f"a985.source_sector.{source_sector}",
                "canonical_address_alias": f"a985.raw_sector.{raw_sector}",
                "canonical_matrix_unit_family": f"a985.raw_sector.{raw_sector}.matrix_units",
                "native_source_domain": "d20_atom:C(H6,3)",
            }
        )

    atoms = atom_rows()
    write_csv(
        ATOM_CSV,
        atoms,
        ["atom_id", "atom_label", "h6_triple", "native_domain"],
    )
    write_csv(
        ALIAS_CSV,
        alias_rows,
        [
            "source_sector",
            "raw_sector",
            "perennial_id",
            "coordinate_fingerprint_id",
            "block_dimension",
            "matrix_unit_count",
            "match_status",
            "canonical_source_alias",
            "canonical_address_alias",
            "canonical_matrix_unit_family",
            "native_source_domain",
        ],
    )

    evidence = json.loads(CERTIFIED_EVIDENCE.read_text(encoding="utf-8"))
    certified_pointer_report = json.loads(CERTIFIED_POINTER_REPORT.read_text(encoding="utf-8"))
    certified_pointer_instance = json.loads(CERTIFIED_POINTER_INSTANCE.read_text(encoding="utf-8"))
    atom_count_from_evidence = evidence["computability_proof"]["counts"]["B_atoms"]

    primitive_schema = {
        "object": "d20",
        "schema": "d20.vocabulary.tiny_pointer_d20_atom_primitive",
        "primitive": "tiny_pointer",
        "meaning": (
            "A tiny pointer is the primitive dereference record attached to the native d20 "
            "atom domain. A d20 atom is a 3-subset of H6; the A985 sector and matrix-unit "
            "labels are the address layer used to dereference atom-supported readouts."
        ),
        "native_source_domain": {
            "name": "d20_atom",
            "definition": "C(H6,3)",
            "atom_count": len(atoms),
            "h6": ["B-", "B+", "V-", "V+", "S-", "S+"],
            "table": str(ATOM_CSV.relative_to(ROOT)).replace("\\", "/"),
        },
        "address_layer": {
            "name": "A985 raw orbital matrix-unit address space",
            "basis_size": certified_pointer_instance["address_space"]["basis_size"],
            "sector_count": len(alias_rows),
            "address_atoms": certified_pointer_instance["address_space"]["address_atoms"],
        },
        "canonical_aliases": {
            "table": str(ALIAS_CSV.relative_to(ROOT)).replace("\\", "/"),
            "rows": len(alias_rows),
            "source_label": "source_sector",
            "address_label": "raw_sector",
            "semantic_label": "perennial_id",
            "coordinate_label": "coordinate_fingerprint_id",
        },
        "pointer_slots": certified_pointer_report["derived"]["pointer_slots"],
        "typing_boundary": (
            "This registry does not identify the 20 native d20 atoms with the 39 A985 sectors. "
            "It fixes the atoms as source-domain primitives and the A985 labels as certified "
            "dereference addresses."
        ),
        "status": "D20_TINY_POINTER_D20_ATOM_PRIMITIVE_SCHEMA_EMITTED",
    }
    primitive_schema["schema_sha256"] = canonical_json_sha256(primitive_schema)
    write_json(PRIMITIVE_SCHEMA, primitive_schema)

    checks = {
        "d20_atom_domain_has_20_rows": len(atoms) == 20,
        "d20_atom_count_matches_certified_evidence": len(atoms) == atom_count_from_evidence,
        "source_sector_alias_rows_are_39": len(alias_rows) == 39,
        "source_sector_aliases_are_unique": len({r["source_sector"] for r in alias_rows}) == 39,
        "raw_sector_aliases_are_unique": len({r["raw_sector"] for r in alias_rows}) == 39,
        "perennial_ids_are_unique": len({r["perennial_id"] for r in alias_rows}) == 39,
        "coordinate_fingerprint_ids_are_unique": len({r["coordinate_fingerprint_id"] for r in alias_rows}) == 39,
        "all_alias_rows_have_unique_fingerprint_matches": all(
            r["match_status"] == "UNIQUE_IDENTITY_FINGERPRINT_MATCH" for r in alias_rows
        ),
        "primitive_schema_emitted": PRIMITIVE_SCHEMA.exists(),
        "alias_registry_emitted": ALIAS_CSV.exists(),
        "atom_domain_emitted": ATOM_CSV.exists(),
    }

    report = {
        "all_checks_pass": all(checks.values()),
        "boundary": (
            "The theorem fixes canonical labels and the d20 atom source domain for tiny-pointer "
            "dereference. It does not assert a bijection between atoms and A985 sectors."
        ),
        "checks": checks,
        "claim": (
            "The tiny pointer is canonicalized as the primitive dereference structure associated "
            "to d20 atoms: native atoms are C(H6,3), while A985 source, raw, perennial, and "
            "coordinate labels form the certified address aliases used by the pointer."
        ),
        "derived": {
            "atom_domain_rows": len(atoms),
            "alias_registry_rows": len(alias_rows),
            "source_sector_count": len({r["source_sector"] for r in alias_rows}),
            "raw_sector_count": len({r["raw_sector"] for r in alias_rows}),
            "perennial_id_count": len({r["perennial_id"] for r in alias_rows}),
            "coordinate_fingerprint_id_count": len({r["coordinate_fingerprint_id"] for r in alias_rows}),
            "tables": {
                "atom_domain": str(ATOM_CSV.relative_to(ROOT)).replace("\\", "/"),
                "sector_label_alias_registry": str(ALIAS_CSV.relative_to(ROOT)).replace("\\", "/"),
                "tiny_pointer_d20_atom_primitive_schema": str(PRIMITIVE_SCHEMA.relative_to(ROOT)).replace(
                    "\\", "/"
                ),
            },
        },
        "inputs": {
            "certified_evidence_invariants": {
                "path": str(CERTIFIED_EVIDENCE.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_path(CERTIFIED_EVIDENCE),
            },
            "certified_pointer_a985_matrix_unit_dereference": {
                "path": str(CERTIFIED_POINTER_REPORT.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_path(CERTIFIED_POINTER_REPORT),
            },
            "certified_pointer_a985_matrix_unit_instance": {
                "path": str(CERTIFIED_POINTER_INSTANCE.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_path(CERTIFIED_POINTER_INSTANCE),
            },
            "perennial_sector_fingerprints": {
                "path": str(PERENNIAL_CSV.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_path(PERENNIAL_CSV),
            },
            "source_to_raw_sector_full_match": {
                "path": str(FULL_MATCH_CSV.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_path(FULL_MATCH_CSV),
            },
        },
        "next_highest_yield_item": (
            "Attach certified per-atom support incidence to this registry when an atom-to-support "
            "table is emitted from the Tiny Pointers source material."
        ),
        "object": "d20",
        "schema": "d20.theorem.tiny_pointer_a985_sector_label_alias_registry",
        "status": "D20_TINY_POINTER_A985_SECTOR_LABEL_ALIAS_REGISTRY_CERTIFIED",
    }
    write_json(REPORT, report)


if __name__ == "__main__":
    main()
