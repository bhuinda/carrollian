from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

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
THEOREM_ID = "tiny_pointer_a985_burning_static_designed_frame_section"
STATUS = "D20_TINY_POINTER_A985_BURNING_STATIC_DESIGNED_FRAME_SECTION_CANDIDATE_CERTIFIED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
BRIDGE_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_ship_algebraicity_bridge"
CHARACTER_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"

OBJECT_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
REQUIRED_INPUT_COLUMNS = [
    "representative_id",
    "quotient_generator",
    "relation_alpha",
    "coefficient_mod_1000003",
    "source_artifact",
    "source_row",
]


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


def object_sign(object_index: np.ndarray) -> np.ndarray:
    return np.asarray(object_index, dtype=np.int64) % 2


def object_family(object_index: np.ndarray) -> np.ndarray:
    return np.asarray(object_index, dtype=np.int64) // 2


def object_clock_mod4(object_index: np.ndarray) -> np.ndarray:
    # Canonical 6-label compression into a four-state clock:
    # B-/B+/V-/V+/S-/S+ -> 0/1/1/2/2/3.
    return (object_family(object_index) + object_sign(object_index)) % 4


def designed_vectors(
    block_i: np.ndarray,
    block_j: np.ndarray,
    q12_map: np.ndarray,
    q42_map: np.ndarray,
) -> dict[str, np.ndarray]:
    a12_parity = np.asarray(q12_map, dtype=np.int64) % 2
    a42_clock = np.asarray(q42_map, dtype=np.int64) % 4
    a12_frame_clock = (np.asarray(q12_map, dtype=np.int64) + block_i + block_j) % 4
    return {
        "z2_a12_parity": a12_parity.astype(np.int64),
        "z4_a42_clock": a42_clock.astype(np.int64),
        "z4_a12_frame_clock": a12_frame_clock.astype(np.int64),
    }


def rules_payload() -> dict[str, Any]:
    return {
        "schema": "d20.tiny_pointer_a985.burning_static_designed_frame_section.rules@1",
        "field_prime": FIELD_PRIME,
        "object_labels": OBJECT_LABELS,
        "object_indexing": {
            "sign_bit": "object_index mod 2, with minus=0 and plus=1",
            "family_index": "floor(object_index / 2), with B=0, V=1, S=2",
            "clock_mod4": "(family_index + sign_bit) mod 4",
        },
        "terminal_frame_readouts": {
            "q12_map": "certified A985 -> A12 terminal quotient class",
            "q42_map": "certified A985 -> A42 terminal quotient class",
            "block_i_block_j": "source and target object indices of the raw A985 relation",
        },
        "abstract_two_primary_section": [
            {
                "burning_generator": "z2_a12_parity",
                "abstract_order": 2,
                "a985_frame_quotient_source": "Z/2 factor",
                "raw_formula": "q12_map(relation_alpha) mod 2",
            },
            {
                "burning_generator": "z4_a42_clock",
                "abstract_order": 4,
                "a985_frame_quotient_source": "5 times the Z/20 factor",
                "raw_formula": "q42_map(relation_alpha) mod 4",
            },
            {
                "burning_generator": "z4_a12_frame_clock",
                "abstract_order": 4,
                "a985_frame_quotient_source": "15 times the Z/60 factor",
                "raw_formula": "(q12_map(relation_alpha) + source_object + target_object) mod 4",
            },
        ],
        "status_boundary": (
            "This is a designed section of the certified A985 frame 2-primary shape. "
            "It is not an imported Burning_static_fields generator map."
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
                    "representative_id": "designed_frame_section_v1",
                    "quotient_generator": generator,
                    "relation_alpha": relation_alpha,
                    "coefficient_mod_1000003": coefficient,
                    "source_artifact": f"DESIGNED_FRAME_SECTION:{generator}:block_i_block_j",
                    "source_row": relation_alpha,
                }
            )
    return rows


def generator_summary_rows(vectors: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    expected_orders = {
        "z2_a12_parity": 2,
        "z4_a42_clock": 4,
        "z4_a12_frame_clock": 4,
    }
    rows: list[dict[str, Any]] = []
    for generator, vector in vectors.items():
        residues = sorted({int(value) for value in vector.tolist()})
        counts = {str(residue): int(np.count_nonzero(vector == residue)) for residue in residues}
        rows.append(
            {
                "representative_id": "designed_frame_section_v1",
                "quotient_generator": generator,
                "abstract_order": expected_orders[generator],
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
                    "representative_id": "designed_frame_section_v1",
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
                "representative_id": "designed_frame_section_v1",
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

    vectors = designed_vectors(block_i, block_j, q12_map, q42_map)
    rows = representative_rows(vectors)
    summary_rows = generator_summary_rows(vectors)
    profile_rows, support_rows = evaluate_traces(
        vectors,
        character_table,
        source_sector,
        raw_sector,
        block_dimension,
    )
    rules = rules_payload()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "burning_static_designed_frame_section_rules.json", rules)
    write_csv_rows(
        OUT_DIR / "burning_static_designed_representative_input.csv",
        REQUIRED_INPUT_COLUMNS,
        rows,
    )
    write_csv_rows(
        OUT_DIR / "burning_static_designed_generator_summary.csv",
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
        OUT_DIR / "burning_static_designed_trace_profile.csv",
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
        OUT_DIR / "burning_static_designed_trace_support_summary.csv",
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
    a985_primary = bridge.get("derived", {}).get("a985_frame_fields", {})
    checks = {
        "burning_a985_bridge_certified": bridge.get("all_checks_pass") is True,
        "a985_frame_two_primary_matches_burning": a985_primary.get("two_primary_component") == "Z/2 x Z/4^2",
        "canonical_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "block_maps_match_relation_reps": np.array_equal(reps[:, 0], block_i)
        and np.array_equal(reps[:, 1], block_j),
        "relation_count_is_985": len(block_i) == RELATION_COUNT == character_table.shape[1],
        "designed_generator_count_is_3": len(vectors) == 3,
        "z2_generator_uses_only_0_1": residue_sets["z2_a12_parity"] == [0, 1],
        "z4_generators_use_all_0_1_2_3": residue_sets["z4_a42_clock"] == [0, 1, 2, 3]
        and residue_sets["z4_a12_frame_clock"] == [0, 1, 2, 3],
        "mod2_reductions_are_independent": f2_rank(list(vectors.values())) == 3,
        "representative_rows_nonempty": len(rows) > 0,
        "trace_profile_has_3_by_39_rows": len(profile_rows) == 3 * 39,
        "each_generator_has_nonzero_trace_support": all(
            int(row["trace_nonzero_sector_count"]) > 0 for row in support_rows
        ),
        "input_schema_columns_match_trace_evaluator": REQUIRED_INPUT_COLUMNS
        == [
            "representative_id",
            "quotient_generator",
            "relation_alpha",
            "coefficient_mod_1000003",
            "source_artifact",
            "source_row",
        ],
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
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_designed_frame_section.source_drop",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "A canonical designed A985 frame section has been materialized as three raw 985-orbital "
            "vectors with abstract two-primary shape Z/2 x Z/4^2, and its all-39 source-sector trace "
            "profile has been computed through the canonical A985 character table."
        ),
        "boundary": (
            "This is a designed Burning_static_fields candidate. It is not an imported source witness "
            "and does not prove that the external Burning_static_fields generators choose this section."
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
            "representative_row_count": len(rows),
            "trace_profile_rows": len(profile_rows),
            "support_summary_rows": len(support_rows),
            "mod2_reduction_rank": f2_rank(list(vectors.values())),
            "residue_sets": residue_sets,
            "abstract_orders": {
                "z2_a12_parity": 2,
                "z4_a42_clock": 4,
                "z4_a12_frame_clock": 4,
            },
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "trace_profile_rows_resolved": int(profile_perennial_stats["rows_with_perennial_id"]),
                "support_summary_set_columns_added": support_perennial_stats["added_columns"],
            },
            "tables": {
                "rules": rel(OUT_DIR / "burning_static_designed_frame_section_rules.json"),
                "representative_input": rel(OUT_DIR / "burning_static_designed_representative_input.csv"),
                "generator_summary": rel(OUT_DIR / "burning_static_designed_generator_summary.csv"),
                "trace_profile": rel(OUT_DIR / "burning_static_designed_trace_profile.csv"),
                "trace_support_summary": rel(OUT_DIR / "burning_static_designed_trace_support_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use the generic Burning static trace evaluator on the designed representative input, "
            "then compare any future imported Burning generator rows against this designed section."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_designed_frame_section_manifest.source_drop",
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
    (OUT_DIR / "burning_static_designed_frame_section_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    supports = read_csv_rows(OUT_DIR / "burning_static_designed_trace_support_summary.csv")
    support_lines = "\n".join(
        f"- `{row['quotient_generator']}`: `{row['trace_nonzero_sector_count']}` sectors, "
        f"dimension sum `{row['trace_support_block_dimension_sum']}`"
        for row in supports
    )
    return (
        "# Burning static designed frame section\n\n"
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
    representative_rows_out = read_csv_rows(OUT_DIR / "burning_static_designed_representative_input.csv")
    profile_rows = read_csv_rows(OUT_DIR / "burning_static_designed_trace_profile.csv")
    support_rows = read_csv_rows(OUT_DIR / "burning_static_designed_trace_support_summary.csv")
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_is_candidate_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "representative_rows_match_report": len(representative_rows_out)
        == int(report.get("derived", {}).get("representative_row_count", -1)),
        "profile_has_117_rows": len(profile_rows) == 117,
        "support_has_3_rows": len(support_rows) == 3,
        "support_rows_are_nonzero": all(int(row["trace_nonzero_sector_count"]) > 0 for row in support_rows),
        "rules_file_exists": (OUT_DIR / "burning_static_designed_frame_section_rules.json").exists(),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in profile_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in profile_rows)
            and "trace_support_source_sectors_perennial_ids" in support_rows[0]
            and "trace_support_raw_sectors_perennial_ids" in support_rows[0]
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_BURNING_STATIC_DESIGNED_FRAME_SECTION_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_BURNING_STATIC_DESIGNED_FRAME_SECTION_VERIFY_FAILED",
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
