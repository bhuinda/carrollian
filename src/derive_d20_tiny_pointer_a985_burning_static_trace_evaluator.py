from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
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
THEOREM_ID = "tiny_pointer_a985_burning_static_trace_evaluator"
STATUS_CONTRACT_CERTIFIED = (
    "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_CONTRACT_CERTIFIED"
)
STATUS_NEEDS_REVIEW = "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_NEEDS_REVIEW"
STATUS_PROFILE_CERTIFIED = "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_PROFILE_CERTIFIED"
STATUS_DESIGNED_PROFILE_CERTIFIED = (
    "D20_TINY_POINTER_A985_BURNING_STATIC_DESIGNED_TRACE_PROFILE_CERTIFIED"
)
STATUS_CONSTRUCTED_PROFILE_CERTIFIED = (
    "D20_TINY_POINTER_A985_BURNING_STATIC_CONSTRUCTED_TRACE_PROFILE_CERTIFIED"
)

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
INTAKE_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_static_representative_intake"
CHARACTER_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters"
DEFAULT_INPUT = INTAKE_DIR / "burning_static_representative_input.csv"

REQUIRED_COLUMNS = [
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


def load_character_data() -> dict[str, np.ndarray]:
    arrays = np.load(CHARACTER_DIR / "canonical_sector_character_table.npz")
    return {
        "character_table": np.asarray(arrays["character_table"], dtype=np.int64) % FIELD_PRIME,
        "source_sector": np.asarray(arrays["source_sector"], dtype=np.int64),
        "raw_sector": np.asarray(arrays["raw_sector"], dtype=np.int64),
        "block_dimension": np.asarray(arrays["block_dimension"], dtype=np.int64),
        "identity_indices": np.asarray(arrays["identity_indices"], dtype=np.int64),
    }


def input_path_from_args(path_text: str | None) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else ROOT / path
    return DEFAULT_INPUT if DEFAULT_INPUT.exists() else None


def validate_input_schema(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        rows = list(reader)
    return rows, missing


def parse_input_rows(
    input_path: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[tuple[str, str], np.ndarray],
    dict[tuple[str, str], dict[str, int]],
    dict[str, Any],
]:
    rows, missing_columns = validate_input_schema(input_path)
    vectors: dict[tuple[str, str], np.ndarray] = {}
    stats: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {
            "row_count": 0,
            "nonzero_rows": 0,
            "relation_alpha_failures": 0,
            "coefficient_failures": 0,
            "blank_source_artifact_rows": 0,
            "ledger_only_source_rows": 0,
        }
    )
    row_errors = 0
    for row in rows:
        representative_id = row.get("representative_id", "").strip()
        quotient_generator = row.get("quotient_generator", "").strip()
        key = (representative_id, quotient_generator)
        if key not in vectors:
            vectors[key] = np.zeros(RELATION_COUNT, dtype=np.int64)
        stats[key]["row_count"] += 1

        try:
            relation_alpha = int(row.get("relation_alpha", ""))
        except ValueError:
            stats[key]["relation_alpha_failures"] += 1
            row_errors += 1
            continue
        if relation_alpha < 0 or relation_alpha >= RELATION_COUNT:
            stats[key]["relation_alpha_failures"] += 1
            row_errors += 1
            continue

        try:
            coefficient = int(row.get("coefficient_mod_1000003", ""))
        except ValueError:
            stats[key]["coefficient_failures"] += 1
            row_errors += 1
            continue
        if coefficient < 0 or coefficient >= FIELD_PRIME:
            stats[key]["coefficient_failures"] += 1
            row_errors += 1
            continue

        source_artifact = row.get("source_artifact", "").strip()
        if not source_artifact:
            stats[key]["blank_source_artifact_rows"] += 1
        if "running_ledger" in source_artifact.lower():
            stats[key]["ledger_only_source_rows"] += 1
        if coefficient:
            stats[key]["nonzero_rows"] += 1
        vectors[key][relation_alpha] = (vectors[key][relation_alpha] + coefficient) % FIELD_PRIME

    validation_rows: list[dict[str, Any]] = []
    for key in sorted(stats):
        representative_id, quotient_generator = key
        item = stats[key]
        status = (
            "VALID"
            if missing_columns == []
            and item["row_count"] > 0
            and item["nonzero_rows"] > 0
            and item["relation_alpha_failures"] == 0
            and item["coefficient_failures"] == 0
            and item["blank_source_artifact_rows"] == 0
            and item["ledger_only_source_rows"] == 0
            else "INVALID"
        )
        validation_rows.append(
            {
                "representative_id": representative_id,
                "quotient_generator": quotient_generator,
                **item,
                "status": status,
            }
        )
    input_summary = {
        "missing_columns": missing_columns,
        "row_count": len(rows),
        "group_count": len(stats),
        "row_errors": row_errors,
        "valid_group_count": sum(1 for row in validation_rows if row["status"] == "VALID"),
    }
    return validation_rows, vectors, stats, input_summary


def identity_selftest(character_data: dict[str, np.ndarray]) -> tuple[list[dict[str, Any]], bool]:
    character_table = character_data["character_table"]
    source_sector = character_data["source_sector"]
    raw_sector = character_data["raw_sector"]
    block_dimension = character_data["block_dimension"]
    identity_indices = character_data["identity_indices"]

    identity_vector = np.zeros(RELATION_COUNT, dtype=np.int64)
    identity_vector[identity_indices] = 1
    traces = (character_table @ identity_vector) % FIELD_PRIME
    rows: list[dict[str, Any]] = []
    for idx, trace in enumerate(traces.tolist()):
        expected = int(block_dimension[idx])
        observed = int(trace)
        rows.append(
            {
                "source_sector": int(source_sector[idx]),
                "raw_sector": int(raw_sector[idx]),
                "block_dimension": expected,
                "identity_trace_mod_1000003": observed,
                "identity_trace_signed": signed_mod(observed),
                "status": "PASS" if observed == expected else "FAIL",
            }
        )
    return rows, all(row["status"] == "PASS" for row in rows)


def evaluate_vectors(
    character_data: dict[str, np.ndarray],
    vectors: dict[tuple[str, str], np.ndarray],
    valid_keys: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    character_table = character_data["character_table"]
    source_sector = character_data["source_sector"]
    raw_sector = character_data["raw_sector"]
    block_dimension = character_data["block_dimension"]

    profile_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for key in sorted(vectors):
        if key not in valid_keys:
            continue
        representative_id, quotient_generator = key
        vector = vectors[key]
        traces = (character_table @ vector) % FIELD_PRIME
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
        support_dimension_sum = sum(
            int(block_dimension[idx])
            for idx, value in enumerate(traces.tolist())
            if int(value) % FIELD_PRIME != 0
        )
        for idx, value in enumerate(traces.tolist()):
            trace = int(value) % FIELD_PRIME
            profile_rows.append(
                {
                    "representative_id": representative_id,
                    "quotient_generator": quotient_generator,
                    "source_sector": int(source_sector[idx]),
                    "raw_sector": int(raw_sector[idx]),
                    "block_dimension": int(block_dimension[idx]),
                    "trace_mod_1000003": trace,
                    "trace_signed": signed_mod(trace),
                    "sector_in_support": trace != 0,
                }
            )
        summary_rows.append(
            {
                "representative_id": representative_id,
                "quotient_generator": quotient_generator,
                "coefficient_nonzero_count": int(np.count_nonzero(vector)),
                "trace_nonzero_sector_count": len(support),
                "trace_support_source_sectors": json.dumps(support, separators=(",", ":")),
                "trace_support_raw_sectors": json.dumps(support_raw, separators=(",", ":")),
                "trace_support_block_dimension_sum": int(support_dimension_sum),
                "coefficient_vector_sha256": array_digest(vector.reshape(1, RELATION_COUNT)),
                "trace_vector_sha256": array_digest(traces.reshape(1, traces.shape[0])),
            }
        )
    return profile_rows, summary_rows


def output_contract(input_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "d20.tiny_pointer_a985.burning_static_trace_evaluator_contract@1",
        "field_prime": FIELD_PRIME,
        "input_schema": input_schema.get("schema"),
        "required_csv_columns": REQUIRED_COLUMNS,
        "linear_rule": (
            "For each representative/generator vector v=sum_alpha c_alpha R_alpha, "
            "the source-sector trace is tr_s(v)=sum_alpha c_alpha chi_s(R_alpha) modulo 1000003."
        ),
        "character_table": rel(CHARACTER_DIR / "canonical_sector_character_table.npz"),
        "output_profile_columns": [
            "representative_id",
            "quotient_generator",
            "source_sector",
            "raw_sector",
            "block_dimension",
            "trace_mod_1000003",
            "trace_signed",
            "sector_in_support",
        ],
    }


def build_trace_evaluator(input_path: Path | None) -> dict[str, Any]:
    intake_report = load_json(INTAKE_DIR / "report.json")
    input_schema = load_json(INTAKE_DIR / "burning_static_representative_input_schema.json")
    character_report = load_json(CHARACTER_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    character_data = load_character_data()
    selftest_rows, selftest_pass = identity_selftest(character_data)
    contract = output_contract(input_schema)

    input_present = input_path is not None and input_path.exists()
    validation_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    input_summary: dict[str, Any] = {
        "missing_columns": REQUIRED_COLUMNS,
        "row_count": 0,
        "group_count": 0,
        "row_errors": 0,
        "valid_group_count": 0,
    }

    if input_present and input_path is not None:
        validation_rows, vectors, _stats, input_summary = parse_input_rows(input_path)
        valid_keys = {
            (str(row["representative_id"]), str(row["quotient_generator"]))
            for row in validation_rows
            if row["status"] == "VALID"
        }
        profile_rows, summary_rows = evaluate_vectors(character_data, vectors, valid_keys)

    input_source_kind = "absent"
    if input_present and input_path is not None:
        input_rows = read_csv_rows(input_path)
        source_artifacts = [row.get("source_artifact", "") for row in input_rows]
        input_source_kind = (
            "constructed_a985_frame_section"
            if source_artifacts
            and all(source.startswith("CONSTRUCTED_A985_FRAME_SECTION:") for source in source_artifacts)
            else (
            "designed_frame_section"
            if source_artifacts
            and all(source.startswith("DESIGNED_FRAME_SECTION:") for source in source_artifacts)
            else "external_or_mixed"
            )
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "burning_static_trace_evaluator_contract.json", contract)
    selftest_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_trace_evaluator_identity_selftest.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "identity_trace_mod_1000003",
            "identity_trace_signed",
            "status",
        ],
        selftest_rows,
        perennial_maps,
    )
    write_csv_rows(
        OUT_DIR / "burning_static_trace_input_validation.csv",
        [
            "representative_id",
            "quotient_generator",
            "row_count",
            "nonzero_rows",
            "relation_alpha_failures",
            "coefficient_failures",
            "blank_source_artifact_rows",
            "ledger_only_source_rows",
            "status",
        ],
        validation_rows,
    )
    profile_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_trace_profile.csv",
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
    summary_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "burning_static_trace_support_summary.csv",
        [
            "representative_id",
            "quotient_generator",
            "coefficient_nonzero_count",
            "trace_nonzero_sector_count",
            "trace_support_source_sectors",
            "trace_support_raw_sectors",
            "trace_support_block_dimension_sum",
            "coefficient_vector_sha256",
            "trace_vector_sha256",
        ],
        summary_rows,
        perennial_maps,
    )

    schema_columns_match = input_schema.get("required_csv_columns") == REQUIRED_COLUMNS
    character_shape = list(character_data["character_table"].shape)
    checks = {
        "burning_intake_report_passed": intake_report.get("all_checks_pass") is True,
        "canonical_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "character_table_shape_is_39_by_985": character_shape == [39, 985],
        "input_schema_matches_required_columns": schema_columns_match,
        "identity_selftest_passed": selftest_pass,
        "contract_emitted": (OUT_DIR / "burning_static_trace_evaluator_contract.json").exists(),
        "no_profile_rows_without_input": input_present or len(profile_rows) == 0,
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            selftest_perennial_stats["rows_with_perennial_id"]
            == selftest_perennial_stats["rows_with_direct_sector"]
            == len(selftest_rows)
            and profile_perennial_stats["rows_with_perennial_id"]
            == profile_perennial_stats["rows_with_direct_sector"]
            == len(profile_rows)
            and selftest_perennial_stats["sector_mismatch_count"] == 0
            and profile_perennial_stats["sector_mismatch_count"] == 0
            and summary_perennial_stats["sector_mismatch_count"] == 0
        ),
    }
    if input_present:
        checks.update(
            {
                "input_columns_present": input_summary["missing_columns"] == [],
                "input_rows_nonempty": input_summary["row_count"] > 0,
                "all_input_groups_valid": input_summary["group_count"] == input_summary["valid_group_count"]
                and input_summary["group_count"] > 0,
                "profile_has_39_rows_per_valid_group": len(profile_rows)
                == 39 * int(input_summary["valid_group_count"]),
                "summary_has_one_row_per_valid_group": len(summary_rows)
                == int(input_summary["valid_group_count"]),
            }
        )
    else:
        checks.update(
            {
                "input_absent_recorded": True,
                "input_validation_rows_empty": len(validation_rows) == 0,
                "support_summary_rows_empty": len(summary_rows) == 0,
            }
        )

    all_checks_pass = all(checks.values())
    if input_present and all_checks_pass:
        status = (
            STATUS_CONSTRUCTED_PROFILE_CERTIFIED
            if input_source_kind == "constructed_a985_frame_section"
            else (
            STATUS_DESIGNED_PROFILE_CERTIFIED
            if input_source_kind == "designed_frame_section"
            else STATUS_PROFILE_CERTIFIED
            )
        )
    elif all_checks_pass:
        status = STATUS_CONTRACT_CERTIFIED
    else:
        status = STATUS_NEEDS_REVIEW
    claim = (
        "The Burning_static_fields representative-to-sector trace evaluator is ready: supplied raw "
        "985-orbital coordinates will be mapped through the canonical A985 character table into all "
        "39 source-sector traces."
    )
    if input_present and input_source_kind == "constructed_a985_frame_section":
        claim = (
            "The constructed A985-side Burning_static_fields representatives are mapped through "
            "the canonical A985 character table into all 39 source-sector traces."
        )
    elif input_present and input_source_kind == "designed_frame_section":
        claim = (
            "The designed A985 frame-section representatives are mapped through the canonical A985 "
            "character table into all 39 source-sector traces."
        )
    elif input_present:
        claim = (
            "The supplied Burning_static_fields raw 985-orbital representatives are mapped through "
            "the canonical A985 character table into all 39 source-sector traces."
        )

    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_trace_evaluator.source_drop",
        "status": status,
        "object": "d20",
        "claim": claim,
        "boundary": (
            "The contract-certified status means no Burning_static_fields raw representative was present; "
            "only the evaluator contract and identity selftest are certified. It is not a Burning support profile."
        )
        if not input_present
        else (
            "Trace rows certify the repo-native constructed A985-side Burning coordinates. They do "
            "not assert that any external artifact uses the same generator names."
            if input_source_kind == "constructed_a985_frame_section"
            else (
                "Trace rows certify the designed input coordinates, not that the external "
                "Burning_static_fields generator map chooses this section."
                if input_source_kind == "designed_frame_section"
                else "Trace rows certify the supplied input coordinates, not any stronger quotient-generator uniqueness claim."
            )
        ),
        "field_prime": FIELD_PRIME,
        "inputs": {
            "burning_static_representative_intake": {
                "path": rel(INTAKE_DIR / "report.json"),
                "sha256": sha_file(INTAKE_DIR / "report.json"),
                "status": intake_report.get("status"),
            },
            "representative_input": (
                {"path": rel(input_path), "sha256": sha_file(input_path)}
                if input_present and input_path is not None
                else {"path": rel(DEFAULT_INPUT), "present": False}
            ),
            "canonical_sector_characters": {
                "path": rel(CHARACTER_DIR / "report.json"),
                "sha256": sha_file(CHARACTER_DIR / "report.json"),
                "status": character_report.get("status"),
            },
            "canonical_sector_character_table": {
                "path": rel(CHARACTER_DIR / "canonical_sector_character_table.npz"),
                "sha256": sha_file(CHARACTER_DIR / "canonical_sector_character_table.npz"),
            },
        },
        "checks": checks,
        "derived": {
            "character_table_shape": character_shape,
            "identity_selftest_rows": len(selftest_rows),
            "input_present": input_present,
            "input_source_kind": input_source_kind,
            "input_summary": input_summary,
            "profile_rows": len(profile_rows),
            "support_summary_rows": len(summary_rows),
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "identity_selftest_rows_resolved": int(selftest_perennial_stats["rows_with_perennial_id"]),
                "profile_rows_resolved": int(profile_perennial_stats["rows_with_perennial_id"]),
                "support_summary_set_columns_added": summary_perennial_stats["added_columns"],
            },
            "tables": {
                "contract": rel(OUT_DIR / "burning_static_trace_evaluator_contract.json"),
                "identity_selftest": rel(OUT_DIR / "burning_static_trace_evaluator_identity_selftest.csv"),
                "input_validation": rel(OUT_DIR / "burning_static_trace_input_validation.csv"),
                "trace_profile": rel(OUT_DIR / "burning_static_trace_profile.csv"),
                "support_summary": rel(OUT_DIR / "burning_static_trace_support_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use this constructed trace profile for public-zero alignment and sector-33 detection."
            if input_source_kind == "constructed_a985_frame_section"
            else (
            "Compare any future imported Burning_static_fields generator rows against the designed "
            "frame-section trace profile."
            if input_source_kind == "designed_frame_section"
            else (
                "Place the raw Burning_static_fields representative CSV at "
                f"{rel(DEFAULT_INPUT)} using the emitted schema, then rerun this evaluator to certify the "
                "39-sector trace support."
            )
            )
        ),
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_trace_evaluator_manifest.source_drop",
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
    (OUT_DIR / "burning_static_trace_evaluator_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Burning static trace evaluator\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        "## Derived\n\n"
        f"- input present: `{derived['input_present']}`\n"
        f"- identity selftest rows: `{derived['identity_selftest_rows']}`\n"
        f"- profile rows: `{derived['profile_rows']}`\n"
        f"- support summary rows: `{derived['support_summary_rows']}`\n\n"
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
    selftest_rows = read_csv_rows(OUT_DIR / "burning_static_trace_evaluator_identity_selftest.csv")
    validation_rows = read_csv_rows(OUT_DIR / "burning_static_trace_input_validation.csv")
    profile_rows = read_csv_rows(OUT_DIR / "burning_static_trace_profile.csv")
    summary_rows = read_csv_rows(OUT_DIR / "burning_static_trace_support_summary.csv")
    input_present = bool(report.get("derived", {}).get("input_present"))
    valid_group_count = int(report.get("derived", {}).get("input_summary", {}).get("valid_group_count", 0))
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_checks_pass": report.get("all_checks_pass") is True,
        "status_is_expected": report.get("status")
        in {
            STATUS_CONTRACT_CERTIFIED,
            STATUS_PROFILE_CERTIFIED,
            STATUS_DESIGNED_PROFILE_CERTIFIED,
            STATUS_CONSTRUCTED_PROFILE_CERTIFIED,
        },
        "contract_exists": (OUT_DIR / "burning_static_trace_evaluator_contract.json").exists(),
        "identity_selftest_has_39_pass_rows": len(selftest_rows) == 39
        and all(row["status"] == "PASS" for row in selftest_rows),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in selftest_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in selftest_rows)
            and all(row.get("perennial_id", "").startswith("a985pf.") for row in profile_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in profile_rows)
            and (not summary_rows or "trace_support_source_sectors_perennial_ids" in summary_rows[0])
            and (not summary_rows or "trace_support_raw_sectors_perennial_ids" in summary_rows[0])
        ),
    }
    if input_present:
        checks.update(
            {
                "validation_rows_match_valid_group_count": sum(1 for row in validation_rows if row["status"] == "VALID")
                == valid_group_count,
                "profile_rows_match_valid_groups": len(profile_rows) == 39 * valid_group_count,
                "summary_rows_match_valid_groups": len(summary_rows) == valid_group_count,
                "status_certifies_profile": report.get("status")
                in {
                    STATUS_PROFILE_CERTIFIED,
                    STATUS_DESIGNED_PROFILE_CERTIFIED,
                    STATUS_CONSTRUCTED_PROFILE_CERTIFIED,
                },
            }
        )
    else:
        checks.update(
            {
                "status_certifies_absent_input_contract": report.get("status") == STATUS_CONTRACT_CERTIFIED,
                "validation_rows_empty_without_input": len(validation_rows) == 0,
                "profile_rows_empty_without_input": len(profile_rows) == 0,
                "summary_rows_empty_without_input": len(summary_rows) == 0,
            }
        )
    return {
        "status": "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Optional Burning_static_fields raw representative CSV.")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if not args.verify_only:
        input_path = input_path_from_args(args.input)
        build_trace_evaluator(input_path)
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
