from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.a985_perennial_ids import (  # noqa: E402
    load_perennial_sector_maps_if_available,
    write_a985_sector_csv_rows_if_available,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


FIELD_PRIME = 1_000_003
RELATION_COUNT = 985
THEOREM_ID = "tiny_pointer_a985_burning_static_constructed_representative"
STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_REPRESENTATIVE_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
BRIDGE_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_ship_algebraicity_bridge"
CHARACTER_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"

REPRESENTATIVE_ID = "constructed_burning_field_v1"
SOURCE_PREFIX = "CONSTRUCTED_A985_FRAME_SECTION"
REQUIRED_INPUT_COLUMNS = [
    "representative_id",
    "quotient_generator",
    "relation_alpha",
    "coefficient_mod_1000003",
    "source_artifact",
    "source_row",
]
EXPECTED_ORDERS = {
    "z2_a12_parity": 2,
    "z4_a42_clock": 4,
    "z4_a12_frame_clock": 4,
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


def array_digest(array: np.ndarray) -> str:
    normalized = np.asarray(array, dtype=np.int64, order="C")
    h = hashlib.sha256()
    h.update(str(normalized.shape).encode("ascii"))
    h.update(normalized.tobytes())
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


def f2_rank(vectors: list[np.ndarray]) -> int:
    basis: dict[int, int] = {}
    for vector in vectors:
        x = 0
        for bit in (np.asarray(vector, dtype=np.int64) % 2).tolist():
            x = (x << 1) | int(bit)
        while x:
            pivot = x.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = x
                break
            x ^= basis[pivot]
    return len(basis)


def constructed_vectors(
    block_i: np.ndarray,
    block_j: np.ndarray,
    q12_map: np.ndarray,
    q42_map: np.ndarray,
) -> dict[str, np.ndarray]:
    return {
        "z2_a12_parity": (np.asarray(q12_map, dtype=np.int64) % 2).astype(np.int64),
        "z4_a42_clock": (np.asarray(q42_map, dtype=np.int64) % 4).astype(np.int64),
        "z4_a12_frame_clock": (
            np.asarray(q12_map, dtype=np.int64) + np.asarray(block_i, dtype=np.int64) + np.asarray(block_j, dtype=np.int64)
        )
        % 4,
    }


def semantics_payload() -> dict[str, Any]:
    return {
        "schema": "d20.tiny_pointer_a985.burning_static_constructed_representative.semantics@1",
        "term": "Burning_static_fields",
        "plain_language": (
            "A burning-static field is a finite quotient-valued coordinate system on the D20 evidence. "
            "In this A985 package it is represented by three raw orbital vectors whose quotient "
            "orders are Z/2 x Z/4 x Z/4."
        ),
        "a985_interpretation": (
            "The constructed representative is the 2-primary shadow of the certified A985 terminal "
            "frame fields. It is built from q12/q42 quotient readouts and raw source/target object "
            "indices, then evaluated on the 39 source sectors by the canonical character table."
        ),
        "generator_formulas": [
            {
                "quotient_generator": "z2_a12_parity",
                "abstract_order": 2,
                "raw_formula": "q12_map(relation_alpha) mod 2",
            },
            {
                "quotient_generator": "z4_a42_clock",
                "abstract_order": 4,
                "raw_formula": "q42_map(relation_alpha) mod 4",
            },
            {
                "quotient_generator": "z4_a12_frame_clock",
                "abstract_order": 4,
                "raw_formula": "(q12_map(relation_alpha) + source_object + target_object) mod 4",
            },
        ],
        "boundary": (
            "This is a repo-native A985-side construction. It does not assert that an external "
            "Burning_static_fields artifact uses the same generator names or basis."
        ),
    }


def representative_rows(vectors: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for generator, vector in vectors.items():
        for relation_alpha, coefficient in enumerate(vector.tolist()):
            coefficient = int(coefficient) % FIELD_PRIME
            if coefficient == 0:
                continue
            rows.append(
                {
                    "representative_id": REPRESENTATIVE_ID,
                    "quotient_generator": generator,
                    "relation_alpha": relation_alpha,
                    "coefficient_mod_1000003": coefficient,
                    "source_artifact": f"{SOURCE_PREFIX}:{generator}:q12_q42_block_frame",
                    "source_row": relation_alpha,
                }
            )
    return rows


def generator_summary_rows(vectors: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for generator, vector in vectors.items():
        residues = sorted({int(value) for value in vector.tolist()})
        counts = {str(residue): int(np.count_nonzero(vector == residue)) for residue in residues}
        rows.append(
            {
                "representative_id": REPRESENTATIVE_ID,
                "quotient_generator": generator,
                "abstract_order": EXPECTED_ORDERS[generator],
                "nonzero_coordinate_count": int(np.count_nonzero(vector)),
                "residue_values": json.dumps(residues, separators=(",", ":")),
                "residue_counts": json.dumps(counts, sort_keys=True, separators=(",", ":")),
                "coordinate_vector_sha256": array_digest(vector.reshape(1, RELATION_COUNT)),
            }
        )
    return rows


def evaluate_traces(
    vectors: dict[str, np.ndarray],
    character_table: np.ndarray,
    source_sector: np.ndarray,
    raw_sector: np.ndarray,
    block_dimension: np.ndarray,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profile_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    for generator, vector in sorted(vectors.items()):
        traces = (character_table @ (vector % FIELD_PRIME)) % FIELD_PRIME
        support = [
            int(source_sector[idx])
            for idx, value in enumerate(traces.tolist())
            if int(value) % FIELD_PRIME != 0
        ]
        support_raw = [
            int(raw_sector[idx])
            for idx, value in enumerate(traces.tolist())
            if int(value) % FIELD_PRIME != 0
        ]
        for idx, value in enumerate(traces.tolist()):
            trace = int(value) % FIELD_PRIME
            profile_rows.append(
                {
                    "representative_id": REPRESENTATIVE_ID,
                    "quotient_generator": generator,
                    "source_sector": int(source_sector[idx]),
                    "raw_sector": int(raw_sector[idx]),
                    "block_dimension": int(block_dimension[idx]),
                    "trace_mod_1000003": trace,
                    "trace_signed": signed_mod(trace),
                    "sector_in_support": trace != 0,
                }
            )
        support_rows.append(
            {
                "representative_id": REPRESENTATIVE_ID,
                "quotient_generator": generator,
                "trace_nonzero_sector_count": len(support),
                "trace_support_source_sectors": json.dumps(support, separators=(",", ":")),
                "trace_support_raw_sectors": json.dumps(support_raw, separators=(",", ":")),
                "trace_support_block_dimension_sum": int(
                    sum(
                        int(block_dimension[idx])
                        for idx, value in enumerate(traces.tolist())
                        if int(value) % FIELD_PRIME != 0
                    )
                ),
                "trace_vector_sha256": array_digest(traces.reshape(1, traces.shape[0])),
            }
        )
    return profile_rows, support_rows


def build_theorem() -> dict[str, Any]:
    bridge = load_json(BRIDGE_DIR / "report.json")
    character_report = load_json(CHARACTER_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    q = np.load(QUOTIENTS_NPZ)
    t = np.load(TENSOR_NPZ)
    block_i = np.asarray(q["block_i"], dtype=np.int64)
    block_j = np.asarray(q["block_j"], dtype=np.int64)
    q12_map = np.asarray(q["q12_map"], dtype=np.int64)
    q42_map = np.asarray(q["q42_map"], dtype=np.int64)
    reps = np.asarray(t["reps"], dtype=np.int64)
    arrays = np.load(CHARACTER_DIR / "canonical_sector_character_table.npz")
    character_table = np.asarray(arrays["character_table"], dtype=np.int64) % FIELD_PRIME
    source_sector = np.asarray(arrays["source_sector"], dtype=np.int64)
    raw_sector = np.asarray(arrays["raw_sector"], dtype=np.int64)
    block_dimension = np.asarray(arrays["block_dimension"], dtype=np.int64)

    vectors = constructed_vectors(block_i, block_j, q12_map, q42_map)
    rows = representative_rows(vectors)
    summary_rows = generator_summary_rows(vectors)
    profile_rows, support_rows = evaluate_traces(
        vectors,
        character_table,
        source_sector,
        raw_sector,
        block_dimension,
    )
    semantics = semantics_payload()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "burning_static_constructed_semantics.json", semantics)
    write_csv_rows(
        OUT_DIR / "burning_static_constructed_representative_input.csv",
        REQUIRED_INPUT_COLUMNS,
        rows,
    )
    write_csv_rows(
        OUT_DIR / "burning_static_constructed_generator_summary.csv",
        [
            "representative_id",
            "quotient_generator",
            "abstract_order",
            "nonzero_coordinate_count",
            "residue_values",
            "residue_counts",
            "coordinate_vector_sha256",
        ],
        summary_rows,
    )
    profile_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_constructed_trace_profile.csv",
        [
            "representative_id",
            "quotient_generator",
            "source_sector",
            "raw_sector",
            "block_dimension",
            "trace_mod_1000003",
            "trace_signed",
            "sector_in_support",
        ],
        profile_rows,
        perennial_maps,
    )
    support_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_constructed_trace_support_summary.csv",
        [
            "representative_id",
            "quotient_generator",
            "trace_nonzero_sector_count",
            "trace_support_source_sectors",
            "trace_support_raw_sectors",
            "trace_support_block_dimension_sum",
            "trace_vector_sha256",
        ],
        support_rows,
        perennial_maps,
    )

    residue_sets = {name: sorted({int(value) for value in vector.tolist()}) for name, vector in vectors.items()}
    bridge_derived = bridge.get("derived", {})
    burning_static = bridge_derived.get("burning_static_fields", {})
    a985_frame = bridge_derived.get("a985_frame_fields", {})
    checks = {
        "burning_a985_bridge_certified": bridge.get("all_checks_pass") is True,
        "burning_quotient_is_z2_z4_z4": burning_static.get("quotient") == "Z/2 x Z/4^2",
        "a985_two_primary_matches_burning": a985_frame.get("two_primary_component") == "Z/2 x Z/4^2",
        "canonical_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "block_maps_match_relation_reps": np.array_equal(reps[:, 0], block_i)
        and np.array_equal(reps[:, 1], block_j),
        "relation_count_is_985": len(block_i) == RELATION_COUNT == character_table.shape[1],
        "constructed_generator_count_is_3": len(vectors) == 3,
        "constructed_source_artifacts_are_explicit": all(
            str(row["source_artifact"]).startswith(f"{SOURCE_PREFIX}:") for row in rows
        ),
        "z2_generator_uses_only_0_1": residue_sets["z2_a12_parity"] == [0, 1],
        "z4_generators_use_all_0_1_2_3": residue_sets["z4_a42_clock"] == [0, 1, 2, 3]
        and residue_sets["z4_a12_frame_clock"] == [0, 1, 2, 3],
        "mod2_reductions_are_independent": f2_rank(list(vectors.values())) == 3,
        "representative_rows_nonempty": len(rows) > 0,
        "trace_profile_has_3_by_39_rows": len(profile_rows) == 3 * 39,
        "each_generator_has_nonzero_trace_support": all(
            int(row["trace_nonzero_sector_count"]) > 0 for row in support_rows
        ),
        "semantics_file_emitted": (OUT_DIR / "burning_static_constructed_semantics.json").exists(),
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            profile_perennial_stats["rows_with_perennial_id"]
            == profile_perennial_stats["rows_with_direct_sector"]
            == len(profile_rows)
            and profile_perennial_stats["sector_mismatch_count"] == 0
            and support_perennial_stats["sector_mismatch_count"] == 0
        ),
    }

    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_constructed_representative.source_drop",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "A repo-native A985-side Burning_static_fields representative has been constructed as "
            "three raw 985-orbital vectors with quotient shape Z/2 x Z/4^2, and its all-39 "
            "source-sector trace profile has been computed."
        ),
        "boundary": (
            "This constructs the A985 representative from certified q12/q42 frame readouts. It does "
            "not claim an external Burning_static_fields artifact chose the same generator names; "
            "a future imported artifact may differ by a quotient-generator basis change."
        ),
        "field_prime": FIELD_PRIME,
        "inputs": {
            "burning_ship_algebraicity_bridge": {
                "path": rel(BRIDGE_DIR / "report.json"),
                "sha256": sha_file(BRIDGE_DIR / "report.json"),
            },
            "canonical_sector_characters": {
                "path": rel(CHARACTER_DIR / "report.json"),
                "sha256": sha_file(CHARACTER_DIR / "report.json"),
            },
            "canonical_sector_character_table": {
                "path": rel(CHARACTER_DIR / "canonical_sector_character_table.npz"),
                "sha256": sha_file(CHARACTER_DIR / "canonical_sector_character_table.npz"),
            },
            "quotients_npz": {"path": rel(QUOTIENTS_NPZ), "sha256": sha_file(QUOTIENTS_NPZ)},
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "representative_id": REPRESENTATIVE_ID,
            "representative_row_count": len(rows),
            "trace_profile_rows": len(profile_rows),
            "support_summary_rows": len(support_rows),
            "mod2_reduction_rank": f2_rank(list(vectors.values())),
            "residue_sets": residue_sets,
            "abstract_orders": EXPECTED_ORDERS,
            "generator_formulas": semantics["generator_formulas"],
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "trace_profile_rows_resolved": int(profile_perennial_stats["rows_with_perennial_id"]),
                "support_summary_set_columns_added": support_perennial_stats["added_columns"],
            },
            "tables": {
                "semantics": rel(OUT_DIR / "burning_static_constructed_semantics.json"),
                "representative_input": rel(OUT_DIR / "burning_static_constructed_representative_input.csv"),
                "generator_summary": rel(OUT_DIR / "burning_static_constructed_generator_summary.csv"),
                "trace_profile": rel(OUT_DIR / "burning_static_constructed_trace_profile.csv"),
                "trace_support_summary": rel(OUT_DIR / "burning_static_constructed_trace_support_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use this constructed representative as the default Burning field input for public-zero "
            "alignment and sector-33 detection."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_constructed_representative_manifest.source_drop",
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
    (OUT_DIR / "burning_static_constructed_representative_report.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    supports = read_csv_rows(OUT_DIR / "burning_static_constructed_trace_support_summary.csv")
    support_lines = "\n".join(
        f"- `{row['quotient_generator']}`: `{row['trace_nonzero_sector_count']}` sectors, "
        f"dimension sum `{row['trace_support_block_dimension_sum']}`"
        for row in supports
    )
    return (
        "# Burning static constructed representative\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        "## Trace Supports\n\n"
        f"{support_lines}\n\n"
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
    representative_rows_out = read_csv_rows(OUT_DIR / "burning_static_constructed_representative_input.csv")
    profile_rows = read_csv_rows(OUT_DIR / "burning_static_constructed_trace_profile.csv")
    support_rows = read_csv_rows(OUT_DIR / "burning_static_constructed_trace_support_summary.csv")
    summary_rows = read_csv_rows(OUT_DIR / "burning_static_constructed_generator_summary.csv")
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_is_constructed_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "representative_rows_match_report": len(representative_rows_out)
        == int(report.get("derived", {}).get("representative_row_count", -1)),
        "profile_has_117_rows": len(profile_rows) == 117,
        "support_has_3_rows": len(support_rows) == 3,
        "summary_has_3_rows": len(summary_rows) == 3,
        "source_artifacts_are_constructed": all(
            row["source_artifact"].startswith(f"{SOURCE_PREFIX}:") for row in representative_rows_out
        ),
        "semantics_file_exists": (OUT_DIR / "burning_static_constructed_semantics.json").exists(),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in profile_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in profile_rows)
            and "trace_support_source_sectors_perennial_ids" in support_rows[0]
            and "trace_support_raw_sectors_perennial_ids" in support_rows[0]
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
        build_theorem()
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
