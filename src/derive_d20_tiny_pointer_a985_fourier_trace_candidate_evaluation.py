from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.derive_d20_tiny_pointer_a985_block_matrix_units import FIELD_PRIME, RELATION_COUNT, array_digest  # noqa: E402
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_fourier_trace_candidate_evaluation"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FOURIER_CANDIDATES_DIR = D20_INVARIANTS / "theorems" / "fourier_a985_sector_character_candidates"
CHARACTER_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters"


EXPECTED_COUNTS = {
    "signed_turn_screen_0": {"homogeneous": 16, "mixed": 23},
    "signed_turn_screen_1": {"homogeneous": 12, "mixed": 27},
    "signed_turn_screen_2": {"homogeneous": 16, "mixed": 23},
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


def candidate_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(candidate["screen_id"]): candidate
        for candidate in report.get("derived", {}).get("candidates", [])
    }


def sector_eval_map(candidate: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(row["sector"]): row for row in candidate["sector_evaluations"]}


def scalar_trace_vector(
    sector_indices: list[int],
    scalars_by_sector: dict[int, int],
    table_by_sector: dict[int, np.ndarray],
) -> np.ndarray:
    out = np.zeros(RELATION_COUNT, dtype=np.int64)
    for sector in sector_indices:
        out = (out + int(scalars_by_sector[sector]) * table_by_sector[sector]) % FIELD_PRIME
    return out % FIELD_PRIME


def support_key(values: list[int]) -> str:
    return "{" + ",".join(str(int(value)) for value in sorted(values)) + "}"


def build_evaluation() -> dict[str, Any]:
    fourier_report = load_json(FOURIER_CANDIDATES_DIR / "report.json")
    character_report = load_json(CHARACTER_DIR / "report.json")
    arrays = np.load(CHARACTER_DIR / "canonical_sector_character_table.npz")
    character_table = np.asarray(arrays["character_table"], dtype=np.int64) % FIELD_PRIME
    source_sectors = np.asarray(arrays["source_sector"], dtype=np.int64)
    block_dimensions = np.asarray(arrays["block_dimension"], dtype=np.int64)
    identity_indices = np.asarray(arrays["identity_indices"], dtype=np.int64)
    table_by_sector = {
        int(sector): character_table[idx, :]
        for idx, sector in enumerate(source_sectors.tolist())
    }
    dimension_by_sector = {
        int(sector): int(block_dimensions[idx])
        for idx, sector in enumerate(source_sectors.tolist())
    }
    candidates = candidate_by_id(fourier_report)

    summary_rows: list[dict[str, Any]] = []
    relation_trace_rows: list[dict[str, Any]] = []
    public_zero_rows: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []

    identity_trace_failures: list[str] = []
    pi33_trace_failures: list[str] = []
    support_trace_failures: list[str] = []
    expected_count_failures: list[str] = []

    for screen_id in sorted(candidates):
        candidate = candidates[screen_id]
        sector_map = sector_eval_map(candidate)
        homogeneous = sorted(
            sector for sector, row in sector_map.items() if bool(row["homogeneous_on_sector"])
        )
        mixed = sorted(
            sector for sector, row in sector_map.items() if not bool(row["homogeneous_on_sector"])
        )
        scalars = {
            sector: int(sector_map[sector]["sector_scalar"])
            for sector in homogeneous
        }
        trace_vector = scalar_trace_vector(homogeneous, scalars, table_by_sector)
        identity_trace = int(np.sum(trace_vector[identity_indices]) % FIELD_PRIME)
        expected_identity_trace = sum(
            int(scalars[sector]) * int(dimension_by_sector[sector])
            for sector in homogeneous
        ) % FIELD_PRIME
        if identity_trace != expected_identity_trace:
            identity_trace_failures.append(screen_id)

        expected = EXPECTED_COUNTS.get(screen_id)
        if expected != {"homogeneous": len(homogeneous), "mixed": len(mixed)}:
            expected_count_failures.append(screen_id)

        pi33_scalar = int(candidate["pi33_sector_scalar"])
        pi33_vector = (pi33_scalar * table_by_sector[33]) % FIELD_PRIME
        pi33_identity_trace = int(np.sum(pi33_vector[identity_indices]) % FIELD_PRIME)
        if pi33_identity_trace != (pi33_scalar * dimension_by_sector[33]) % FIELD_PRIME:
            pi33_trace_failures.append(screen_id)

        for relation_alpha, value in enumerate(trace_vector.tolist()):
            relation_trace_rows.append(
                {
                    "screen_id": screen_id,
                    "trace_domain": "homogeneous_sectors",
                    "relation_alpha": relation_alpha,
                    "trace_mod_1000003": int(value),
                    "trace_signed": signed_mod(int(value)),
                }
            )

        support_records: list[dict[str, Any]] = []
        for support in candidate["public_zero_support_evaluations"]:
            sectors = [int(value) for value in support["sector_support"]]
            scalar_on_support = bool(support["scalar_on_support"])
            support_scalar = support["support_scalar"]
            support_trace_defined = scalar_on_support and support_scalar is not None
            support_identity_trace = None
            expected_support_identity_trace = None
            support_trace_sha256 = None
            nonzero_support_trace_values = None
            if support_trace_defined:
                scalar = int(support_scalar)
                support_vector = scalar_trace_vector(
                    sectors,
                    {sector: scalar for sector in sectors},
                    table_by_sector,
                )
                support_identity_trace = int(np.sum(support_vector[identity_indices]) % FIELD_PRIME)
                expected_support_identity_trace = (
                    scalar * sum(dimension_by_sector[sector] for sector in sectors)
                ) % FIELD_PRIME
                support_trace_sha256 = array_digest(support_vector.reshape(1, RELATION_COUNT))
                nonzero_support_trace_values = int(np.count_nonzero(support_vector))
                if support_identity_trace != expected_support_identity_trace:
                    support_trace_failures.append(f"{screen_id}:{support_key(sectors)}")
            public_zero_rows.append(
                {
                    "screen_id": screen_id,
                    "sector_support": support_key(sectors),
                    "sector_count": int(support["sector_count"]),
                    "dimension_sum": int(support["dimension_sum"]),
                    "public_zero": bool(support["public_zero"]),
                    "scalar_on_support": scalar_on_support,
                    "support_scalar": "" if support_scalar is None else support_scalar,
                    "canonical_trace_defined": support_trace_defined,
                    "identity_trace_mod_1000003": "" if support_identity_trace is None else support_identity_trace,
                    "expected_identity_trace_mod_1000003": ""
                    if expected_support_identity_trace is None
                    else expected_support_identity_trace,
                    "nonzero_trace_values": "" if nonzero_support_trace_values is None else nonzero_support_trace_values,
                    "trace_sha256": "" if support_trace_sha256 is None else support_trace_sha256,
                }
            )
            support_records.append(
                {
                    "sector_support": sectors,
                    "scalar_on_support": scalar_on_support,
                    "canonical_trace_defined": support_trace_defined,
                    "support_scalar": support_scalar,
                    "identity_trace_mod_1000003": support_identity_trace,
                    "expected_identity_trace_mod_1000003": expected_support_identity_trace,
                    "trace_sha256": support_trace_sha256,
                }
            )

        summary = {
            "screen_id": screen_id,
            "homogeneous_sector_count": len(homogeneous),
            "mixed_sector_count": len(mixed),
            "homogeneous_dimension_sum": sum(dimension_by_sector[sector] for sector in homogeneous),
            "mixed_dimension_sum": sum(dimension_by_sector[sector] for sector in mixed),
            "full_a985_trace_defined": len(mixed) == 0,
            "homogeneous_identity_trace_mod_1000003": identity_trace,
            "expected_homogeneous_identity_trace_mod_1000003": expected_identity_trace,
            "pi33_scalar": pi33_scalar,
            "pi33_identity_trace_mod_1000003": pi33_identity_trace,
            "nonzero_homogeneous_trace_values": int(np.count_nonzero(trace_vector)),
            "homogeneous_trace_sha256": array_digest(trace_vector.reshape(1, RELATION_COUNT)),
            "mixed_sectors": json.dumps(mixed, separators=(",", ":")),
            "homogeneous_sectors": json.dumps(homogeneous, separators=(",", ":")),
        }
        summary_rows.append(summary)
        candidate_records.append(
            {
                **summary,
                "homogeneous_trace_row_sha256": summary["homogeneous_trace_sha256"],
                "public_zero_support_records": support_records,
            }
        )

    public_zero_profile = {
        row["screen_id"]: bool(candidates[row["screen_id"]]["all_nonzero_public_zero_supports_scalar"])
        for row in summary_rows
    }
    full_trace_profile = {
        row["screen_id"]: bool(row["full_a985_trace_defined"])
        for row in summary_rows
    }
    pi33_scalars = {
        row["screen_id"]: int(row["pi33_scalar"])
        for row in summary_rows
    }
    relation_trace_row_count = len(relation_trace_rows)
    public_zero_trace_defined_rows = [
        row for row in public_zero_rows if row["public_zero"] is True and row["canonical_trace_defined"] is True
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "fourier_trace_candidate_summary.csv",
        [
            "screen_id",
            "homogeneous_sector_count",
            "mixed_sector_count",
            "homogeneous_dimension_sum",
            "mixed_dimension_sum",
            "full_a985_trace_defined",
            "homogeneous_identity_trace_mod_1000003",
            "expected_homogeneous_identity_trace_mod_1000003",
            "pi33_scalar",
            "pi33_identity_trace_mod_1000003",
            "nonzero_homogeneous_trace_values",
            "homogeneous_trace_sha256",
            "mixed_sectors",
            "homogeneous_sectors",
        ],
        summary_rows,
    )
    write_csv_rows(
        OUT_DIR / "fourier_trace_candidate_relation_traces.csv",
        [
            "screen_id",
            "trace_domain",
            "relation_alpha",
            "trace_mod_1000003",
            "trace_signed",
        ],
        relation_trace_rows,
    )
    write_csv_rows(
        OUT_DIR / "fourier_trace_public_zero_support_summary.csv",
        [
            "screen_id",
            "sector_support",
            "sector_count",
            "dimension_sum",
            "public_zero",
            "scalar_on_support",
            "support_scalar",
            "canonical_trace_defined",
            "identity_trace_mod_1000003",
            "expected_identity_trace_mod_1000003",
            "nonzero_trace_values",
            "trace_sha256",
        ],
        public_zero_rows,
    )

    checks = {
        "fourier_candidate_report_certified": fourier_report.get("status")
        == "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        and fourier_report.get("all_checks_pass") is True,
        "canonical_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "character_table_shape_is_39_by_985": character_table.shape == (39, RELATION_COUNT),
        "candidate_count_is_3": len(summary_rows) == 3,
        "relation_trace_rows_are_3_by_985": relation_trace_row_count == 3 * RELATION_COUNT,
        "homogeneous_mixed_counts_match_prior_profile": expected_count_failures == [],
        "homogeneous_identity_traces_match_character_table": identity_trace_failures == [],
        "pi33_identity_traces_match_character_table": pi33_trace_failures == [],
        "public_zero_identity_traces_match_character_table": support_trace_failures == [],
        "no_candidate_has_full_a985_trace": full_trace_profile
        == {
            "signed_turn_screen_0": False,
            "signed_turn_screen_1": False,
            "signed_turn_screen_2": False,
        },
        "public_zero_scalar_profile_preserved": public_zero_profile
        == {
            "signed_turn_screen_0": True,
            "signed_turn_screen_1": False,
            "signed_turn_screen_2": False,
        },
        "pi33_scalar_profile_preserved": pi33_scalars
        == {
            "signed_turn_screen_0": 1,
            "signed_turn_screen_1": 1,
            "signed_turn_screen_2": -1,
        },
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_fourier_trace_candidate_evaluation.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The Fourier residue candidates have now been evaluated against the canonical A985 block "
            "character table. Each candidate gets a raw-relation trace vector on its homogeneous "
            "sector domain; none extends to a full all-39-sector scalar A985 trace because each has "
            "mixed sectors."
        ),
        "inputs": {
            "fourier_a985_sector_character_candidates": {
                "path": rel(FOURIER_CANDIDATES_DIR / "report.json"),
                "sha256": sha_file(FOURIER_CANDIDATES_DIR / "report.json"),
            },
            "canonical_sector_characters": {
                "path": rel(CHARACTER_DIR / "report.json"),
                "sha256": sha_file(CHARACTER_DIR / "report.json"),
            },
            "canonical_sector_character_table": {
                "path": rel(CHARACTER_DIR / "canonical_sector_character_table.npz"),
                "sha256": sha_file(CHARACTER_DIR / "canonical_sector_character_table.npz"),
            },
        },
        "checks": checks,
        "derived": {
            "candidate_count": len(summary_rows),
            "relation_trace_rows": relation_trace_row_count,
            "public_zero_support_rows": len(public_zero_rows),
            "public_zero_trace_defined_rows": len(public_zero_trace_defined_rows),
            "full_trace_profile": full_trace_profile,
            "public_zero_scalar_profile": public_zero_profile,
            "pi33_scalars": pi33_scalars,
            "identity_trace_failures": identity_trace_failures,
            "pi33_trace_failures": pi33_trace_failures,
            "support_trace_failures": support_trace_failures,
            "candidate_records_sha256": hashlib.sha256(canonical(candidate_records)).hexdigest(),
            "candidate_records": candidate_records,
            "tables": {
                "candidate_summary": rel(OUT_DIR / "fourier_trace_candidate_summary.csv"),
                "candidate_relation_traces": rel(OUT_DIR / "fourier_trace_candidate_relation_traces.csv"),
                "public_zero_support_summary": rel(OUT_DIR / "fourier_trace_public_zero_support_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "For the surviving public-zero-compatible screen, construct the supported trace vector "
            "as an explicit central element candidate and compare it against multiplication in the "
            "closed-loop/tube layer."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_fourier_trace_candidate_evaluation_manifest.source_drop",
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
    (OUT_DIR / "fourier_trace_candidate_evaluation_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Fourier Trace Candidate Evaluation\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Relation trace rows: `{derived['relation_trace_rows']}`\n\n"
        f"Full trace profile: `{derived['full_trace_profile']}`\n\n"
        f"Public-zero scalar profile: `{derived['public_zero_scalar_profile']}`\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Next: {report['next_highest_yield_item']}\n"
    )


def update_theorem_index(report: dict[str, Any]) -> None:
    index_path = D20_INVARIANTS / "theorems" / "index.json"
    index = load_json(index_path) if index_path.exists() else {"theorems": []}
    theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
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


def verify_theorem() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    summary_rows = read_csv_rows(OUT_DIR / "fourier_trace_candidate_summary.csv")
    relation_rows = read_csv_rows(OUT_DIR / "fourier_trace_candidate_relation_traces.csv")
    public_zero_rows = read_csv_rows(OUT_DIR / "fourier_trace_public_zero_support_summary.csv")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "summary_has_3_rows": len(summary_rows) == 3,
        "relation_trace_rows_are_2955": len(relation_rows) == 3 * RELATION_COUNT,
        "public_zero_rows_are_18": len(public_zero_rows) == 18,
        "no_summary_full_trace_defined": all(row["full_a985_trace_defined"] == "False" for row in summary_rows),
        "identity_trace_columns_match": all(
            row["homogeneous_identity_trace_mod_1000003"]
            == row["expected_homogeneous_identity_trace_mod_1000003"]
            for row in summary_rows
        ),
        "public_zero_defined_identity_columns_match": all(
            row["canonical_trace_defined"] != "True"
            or row["identity_trace_mod_1000003"] == row["expected_identity_trace_mod_1000003"]
            for row in public_zero_rows
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_evaluation()
    verification = verify_theorem()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
