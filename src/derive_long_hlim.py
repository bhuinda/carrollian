from __future__ import annotations

import csv
import hashlib
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from .derive_long_nat import OUT_DIR as LONG_NAT_DIR, STATUS as LONG_NAT_STATUS
    from .derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from derive_long_nat import OUT_DIR as LONG_NAT_DIR, STATUS as LONG_NAT_STATUS
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_hlim"
STATUS = "LONG_HLIM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_NAT_REPORT = LONG_NAT_DIR / "report.json"
LONG_NAT_NATURALITY = LONG_NAT_DIR / "naturality.csv"
LONG_NAT_DEPENDENCY = LONG_NAT_DIR / "dependency.csv"
LONG_NAT_TABLES = LONG_NAT_DIR / "tables.npz"
LONG_CONV_REPORT = LONG_CONV_DIR / "report.json"
LONG_CONV_MARGINAL = LONG_CONV_DIR / "marginal.csv"
LONG_CONV_CONVOLUTION = LONG_CONV_DIR / "convolution.csv"
LONG_CONV_TABLES = LONG_CONV_DIR / "tables.npz"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_OBJECT = LONG_PROF_DIR / "object.csv"
LONG_PROF_PROFUNCTOR = LONG_PROF_DIR / "profunctor.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_hlim.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hlim.py"

HORIZON_TEXT_HASH = "749d98cef39ae66c3cc0c53d0787179f1e1acbf08b51a7c7f9130ea14b54f863"
OBSTRUCTION_TEXT_HASH = "d5bf2d7040ee64bec34a3cef364e4cfd0f96cba94ca331a754ef0e932b9a92fb"
PROPAGATION_TEXT_HASH = "cc80252c1ba39ac5d8bbd43fd36f62e4d5dcbd5cc2a84af3c03b367da8e1abe1"
SPLIT_TEXT_HASH = "f293a153f634d635487df6755bad1dd88a2050600ca8c04e88a94ecf9f4b4252"

HORIZON_COLUMNS = [
    "horizon_id",
    "sample_count",
    "marginal_row_count",
    "prof_match_row_count",
    "prof_missing_row_count",
    "split_pair_count",
    "split_equal_row_count",
    "external_law_count",
    "external_seed_law_count",
    "external_propagated_law_count",
    "external_dependency_count",
    "extension_flag",
    "split_stabilized_flag",
    "prof_obstructed_flag",
]
OBSTRUCTION_COLUMNS = [
    "obstruction_id",
    "sample_count",
    "sum_value",
    "marginal_row_id",
    "prof_match_flag",
    "positive_flag",
    "split_pair_count",
    "extension_flag",
]
PROPAGATION_COLUMNS = [
    "propagation_id",
    "law_id",
    "square_code",
    "law_code",
    "source_id",
    "target_id",
    "subtarget_id",
    "external_seed_flag",
    "internal_propagation_flag",
    "split_pair_count",
    "direct_missing_row_count",
    "ultimate_missing_row_count",
    "dependency_count",
    "law_dependency_count",
    "external_dependency_count",
    "equal_flag",
]
SPLIT_COLUMNS = [
    "split_horizon_id",
    "sample_count",
    "split_pair_count",
    "split_row_count",
    "split_equal_count",
    "split_violation_count",
    "extension_flag",
    "cover_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "horizon_count",
    "extension_horizon_count",
    "marginal_row_count",
    "prof_match_row_count",
    "prof_missing_row_count",
    "split_pair_count",
    "extension_split_pair_count",
    "split_equal_row_count",
    "extension_split_equal_row_count",
    "split_violation_count",
    "external_law_count",
    "external_seed_law_count",
    "external_propagated_law_count",
    "external_dependency_total",
    "ultimate_missing_dependency_total",
    "obstruction_row_count",
    "split_stabilized_extension_count",
    "prof_obstructed_extension_count",
    "prof_source_horizon",
    "prof_target_rows",
    "conv_state_horizon",
    "conv_split_horizon",
    "long_nat_input_certified",
    "long_conv_input_certified",
    "long_prof_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def digest_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    return "".join(",".join(str(row[column]) for column in columns) + "\n" for row in rows)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def int_rows(rows: list[dict[str, str]]) -> list[dict[str, int]]:
    return [{key: int(value) for key, value in row.items()} for row in rows]


def ultimate_missing_row_count(row: dict[str, int]) -> int:
    sample_count = row["source_id"]
    square_code = row["square_code"]
    if square_code in {2, 3, 4}:
        return 2 * sample_count + 1
    if square_code == 5:
        previous = 2 * (sample_count - 1) + 1 if sample_count - 1 > 8 else 0
        return 2 * sample_count + 1 + previous
    return row["external_dependency_count"]


def build_rows() -> dict[str, Any]:
    long_nat = load_json(LONG_NAT_REPORT)
    long_conv = load_json(LONG_CONV_REPORT)
    long_prof = load_json(LONG_PROF_REPORT)
    nat_rows = int_rows(read_csv_rows(LONG_NAT_NATURALITY))
    marginal_rows_raw = read_csv_rows(LONG_CONV_MARGINAL)
    convolution_rows = int_rows(read_csv_rows(LONG_CONV_CONVOLUTION))
    profunctor_rows = read_csv_rows(LONG_PROF_PROFUNCTOR)

    path_sum = next(
        row for row in profunctor_rows if row["profunctor_name"] == "path_sum_distribution"
    )
    prof_source_horizon = int(path_sum["source_count"])
    prof_target_rows = int(path_sum["target_count"])
    conv_horizon = long_conv["witness"]["horizon"]
    conv_state_horizon = int(conv_horizon["state_horizon"])
    conv_split_horizon = int(conv_horizon["split_horizon"])

    horizon_rows: list[dict[str, int]] = []
    split_rows: list[dict[str, int]] = []
    obstruction_rows: list[dict[str, int]] = []

    for sample_count in range(1, conv_state_horizon + 1):
        marginal_rows = [
            (index, row)
            for index, row in enumerate(marginal_rows_raw)
            if int(row["sample_count"]) == sample_count
        ]
        split_conv_rows = [
            row for row in convolution_rows if row["total_horizon"] == sample_count
        ]
        split_pairs = {
            (row["left_horizon"], row["right_horizon"]) for row in split_conv_rows
        }
        split_equal_count = sum(int(row["equal_flag"]) for row in split_conv_rows)
        split_violation_count = len(split_conv_rows) - split_equal_count
        external_nat_rows = [
            row
            for row in nat_rows
            if row["source_id"] == sample_count and row["external_input_flag"] == 1
        ]
        external_seed_rows = [
            row for row in external_nat_rows if row["external_dependency_count"] > 0
        ]
        extension_flag = int(sample_count > prof_source_horizon)
        prof_missing_count = sum(
            int(int(row["prof_match_flag"]) == -1) for _index, row in marginal_rows
        )
        prof_match_count = sum(
            int(int(row["prof_match_flag"]) == 1) for _index, row in marginal_rows
        )
        split_stabilized_flag = int(
            (sample_count == 1 and not split_conv_rows)
            or (bool(split_conv_rows) and split_violation_count == 0)
        )
        horizon_rows.append(
            {
                "horizon_id": sample_count - 1,
                "sample_count": sample_count,
                "marginal_row_count": len(marginal_rows),
                "prof_match_row_count": prof_match_count,
                "prof_missing_row_count": prof_missing_count,
                "split_pair_count": len(split_pairs),
                "split_equal_row_count": split_equal_count,
                "external_law_count": len(external_nat_rows),
                "external_seed_law_count": len(external_seed_rows),
                "external_propagated_law_count": len(external_nat_rows)
                - len(external_seed_rows),
                "external_dependency_count": sum(
                    int(row["external_dependency_count"]) for row in external_nat_rows
                ),
                "extension_flag": extension_flag,
                "split_stabilized_flag": split_stabilized_flag,
                "prof_obstructed_flag": int(
                    extension_flag and prof_missing_count == len(marginal_rows)
                ),
            }
        )
        split_rows.append(
            {
                "split_horizon_id": sample_count - 1,
                "sample_count": sample_count,
                "split_pair_count": len(split_pairs),
                "split_row_count": len(split_conv_rows),
                "split_equal_count": split_equal_count,
                "split_violation_count": split_violation_count,
                "extension_flag": extension_flag,
                "cover_flag": split_stabilized_flag,
            }
        )
        if extension_flag:
            for marginal_row_id, row in marginal_rows:
                obstruction_rows.append(
                    {
                        "obstruction_id": len(obstruction_rows),
                        "sample_count": sample_count,
                        "sum_value": int(row["sum_value"]),
                        "marginal_row_id": marginal_row_id,
                        "prof_match_flag": int(row["prof_match_flag"]),
                        "positive_flag": int(row["positive_flag"]),
                        "split_pair_count": len(split_pairs),
                        "extension_flag": 1,
                    }
                )

    split_pair_by_horizon = {
        row["sample_count"]: row["split_pair_count"] for row in horizon_rows
    }
    propagation_rows: list[dict[str, int]] = []
    for row in [row for row in nat_rows if row["external_input_flag"] == 1]:
        propagation_rows.append(
            {
                "propagation_id": len(propagation_rows),
                "law_id": row["law_id"],
                "square_code": row["square_code"],
                "law_code": row["law_code"],
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "subtarget_id": row["subtarget_id"],
                "external_seed_flag": int(row["external_dependency_count"] > 0),
                "internal_propagation_flag": int(row["external_dependency_count"] == 0),
                "split_pair_count": split_pair_by_horizon[row["source_id"]],
                "direct_missing_row_count": row["external_dependency_count"],
                "ultimate_missing_row_count": ultimate_missing_row_count(row),
                "dependency_count": row["dependency_count"],
                "law_dependency_count": row["law_dependency_count"],
                "external_dependency_count": row["external_dependency_count"],
                "equal_flag": row["equal_flag"],
            }
        )

    horizon_hash = hashlib.sha256(
        digest_text(HORIZON_COLUMNS, horizon_rows).encode("ascii")
    ).hexdigest()
    obstruction_hash = hashlib.sha256(
        digest_text(OBSTRUCTION_COLUMNS, obstruction_rows).encode("ascii")
    ).hexdigest()
    propagation_hash = hashlib.sha256(
        digest_text(PROPAGATION_COLUMNS, propagation_rows).encode("ascii")
    ).hexdigest()
    split_hash = hashlib.sha256(
        digest_text(SPLIT_COLUMNS, split_rows).encode("ascii")
    ).hexdigest()

    obs = {
        "horizon_count": len(horizon_rows),
        "extension_horizon_count": sum(int(row["extension_flag"]) for row in horizon_rows),
        "marginal_row_count": sum(int(row["marginal_row_count"]) for row in horizon_rows),
        "prof_match_row_count": sum(
            int(row["prof_match_row_count"]) for row in horizon_rows
        ),
        "prof_missing_row_count": sum(
            int(row["prof_missing_row_count"]) for row in horizon_rows
        ),
        "split_pair_count": sum(int(row["split_pair_count"]) for row in horizon_rows),
        "extension_split_pair_count": sum(
            int(row["split_pair_count"]) for row in horizon_rows if row["extension_flag"]
        ),
        "split_equal_row_count": sum(
            int(row["split_equal_row_count"]) for row in horizon_rows
        ),
        "extension_split_equal_row_count": sum(
            int(row["split_equal_row_count"])
            for row in horizon_rows
            if row["extension_flag"]
        ),
        "split_violation_count": sum(
            int(row["split_violation_count"]) for row in split_rows
        ),
        "external_law_count": sum(int(row["external_law_count"]) for row in horizon_rows),
        "external_seed_law_count": sum(
            int(row["external_seed_law_count"]) for row in horizon_rows
        ),
        "external_propagated_law_count": sum(
            int(row["external_propagated_law_count"]) for row in horizon_rows
        ),
        "external_dependency_total": sum(
            int(row["external_dependency_count"]) for row in horizon_rows
        ),
        "ultimate_missing_dependency_total": sum(
            int(row["ultimate_missing_row_count"]) for row in propagation_rows
        ),
        "obstruction_row_count": len(obstruction_rows),
        "split_stabilized_extension_count": sum(
            int(row["split_stabilized_flag"] and row["extension_flag"])
            for row in horizon_rows
        ),
        "prof_obstructed_extension_count": sum(
            int(row["prof_obstructed_flag"]) for row in horizon_rows
        ),
        "prof_source_horizon": prof_source_horizon,
        "prof_target_rows": prof_target_rows,
        "conv_state_horizon": conv_state_horizon,
        "conv_split_horizon": conv_split_horizon,
        "long_nat_input_certified": int(long_nat.get("status") == LONG_NAT_STATUS),
        "long_conv_input_certified": int(long_conv.get("status") == LONG_CONV_STATUS),
        "long_prof_input_certified": int(long_prof.get("status") == LONG_PROF_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]

    return {
        "input_reports": {
            "long_nat": long_nat,
            "long_conv": long_conv,
            "long_prof": long_prof,
        },
        "horizon_rows": horizon_rows,
        "obstruction_rows": obstruction_rows,
        "propagation_rows": propagation_rows,
        "split_rows": split_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "horizon_table": table_from_rows(HORIZON_COLUMNS, horizon_rows),
        "obstruction_table": table_from_rows(OBSTRUCTION_COLUMNS, obstruction_rows),
        "propagation_table": table_from_rows(PROPAGATION_COLUMNS, propagation_rows),
        "split_table": table_from_rows(SPLIT_COLUMNS, split_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "horizon_hash": horizon_hash,
        "obstruction_hash": obstruction_hash,
        "propagation_hash": propagation_hash,
        "split_hash": split_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": (
            obs["long_nat_input_certified"],
            obs["long_conv_input_certified"],
            obs["long_prof_input_certified"],
        )
        == (1, 1, 1),
        "horizon_fingerprint_exact": (
            obs["horizon_count"],
            obs["extension_horizon_count"],
            obs["marginal_row_count"],
            obs["prof_match_row_count"],
            obs["prof_missing_row_count"],
            obs["split_stabilized_extension_count"],
            rows["horizon_hash"],
        )
        == (16, 8, 288, 80, 208, 8, HORIZON_TEXT_HASH),
        "split_stabilization_exact": (
            obs["split_pair_count"],
            obs["extension_split_pair_count"],
            obs["split_equal_row_count"],
            obs["extension_split_equal_row_count"],
            obs["split_violation_count"],
            rows["split_hash"],
        )
        == (64, 36, 3648, 2556, 0, SPLIT_TEXT_HASH),
        "profunctor_obstruction_exact": (
            obs["obstruction_row_count"],
            obs["prof_obstructed_extension_count"],
            obs["prof_source_horizon"],
            obs["prof_target_rows"],
            obs["conv_state_horizon"],
            obs["conv_split_horizon"],
            rows["obstruction_hash"],
        )
        == (208, 8, 8, 80, 16, 8, OBSTRUCTION_TEXT_HASH),
        "propagation_fingerprint_exact": (
            obs["external_law_count"],
            obs["external_seed_law_count"],
            obs["external_propagated_law_count"],
            obs["external_dependency_total"],
            obs["ultimate_missing_dependency_total"],
            rows["propagation_hash"],
        )
        == (112, 56, 56, 1456, 3087, PROPAGATION_TEXT_HASH),
        "table_shapes_match": (
            tuple(rows["horizon_table"].shape),
            tuple(rows["obstruction_table"].shape),
            tuple(rows["propagation_table"].shape),
            tuple(rows["split_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (16, len(HORIZON_COLUMNS)),
            (208, len(OBSTRUCTION_COLUMNS)),
            (112, len(PROPAGATION_COLUMNS)),
            (16, len(SPLIT_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_horizon_limit_obstruction",
        "horizon": {
            "horizon_count": obs["horizon_count"],
            "extension_horizon_count": obs["extension_horizon_count"],
            "marginal_row_count": obs["marginal_row_count"],
            "prof_match_row_count": obs["prof_match_row_count"],
            "prof_missing_row_count": obs["prof_missing_row_count"],
            "text_sha256": rows["horizon_hash"],
            "table_sha256": sha_array(rows["horizon_table"]),
        },
        "split_stabilization": {
            "split_pair_count": obs["split_pair_count"],
            "extension_split_pair_count": obs["extension_split_pair_count"],
            "split_equal_row_count": obs["split_equal_row_count"],
            "extension_split_equal_row_count": obs["extension_split_equal_row_count"],
            "split_violation_count": obs["split_violation_count"],
            "text_sha256": rows["split_hash"],
            "table_sha256": sha_array(rows["split_table"]),
        },
        "profunctor_obstruction": {
            "obstruction_row_count": obs["obstruction_row_count"],
            "prof_obstructed_extension_count": obs["prof_obstructed_extension_count"],
            "prof_source_horizon": obs["prof_source_horizon"],
            "prof_target_rows": obs["prof_target_rows"],
            "conv_state_horizon": obs["conv_state_horizon"],
            "conv_split_horizon": obs["conv_split_horizon"],
            "text_sha256": rows["obstruction_hash"],
            "table_sha256": sha_array(rows["obstruction_table"]),
        },
        "propagation": {
            "external_law_count": obs["external_law_count"],
            "external_seed_law_count": obs["external_seed_law_count"],
            "external_propagated_law_count": obs["external_propagated_law_count"],
            "external_dependency_total": obs["external_dependency_total"],
            "ultimate_missing_dependency_total": obs[
                "ultimate_missing_dependency_total"
            ],
            "text_sha256": rows["propagation_hash"],
            "table_sha256": sha_array(rows["propagation_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    hlim_payload = {
        "schema": "long.hlim@1",
        "object": "finite_horizon_limit_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_HLIM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.hlim.report@1",
        "status": hlim_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_hlim certifies that horizons 9 through 16 are already "
            "finite split-convolution stable, but not profunctor-controlled "
            "by the certified horizon-8 path-sum profunctor: exactly 208 "
            "marginal rows have no profunctor comparison row, and those rows "
            "generate the 112-law horizon-extension boundary in long_nat."
        ),
        "stage_protocol": {
            "draft": "read long_nat, long_conv, and long_prof horizon/profunctor artifacts",
            "witness": "separate split-stable extension horizons from missing profunctor comparison rows",
            "coherence": "check input status, horizon counts, split equalities, obstruction rows, propagation rows, hashes, and shapes",
            "closure": "emit horizon, obstruction, propagation, split, table, certificate, manifest, and report artifacts",
            "emit": "write long_hlim artifacts and verifier hook",
        },
        "inputs": {
            "long_nat_report": input_entry(
                LONG_NAT_REPORT,
                {"status": rows["input_reports"]["long_nat"].get("status")},
            ),
            "long_nat_naturality": input_entry(LONG_NAT_NATURALITY),
            "long_nat_dependency": input_entry(LONG_NAT_DEPENDENCY),
            "long_nat_tables": input_entry(LONG_NAT_TABLES),
            "long_conv_report": input_entry(
                LONG_CONV_REPORT,
                {"status": rows["input_reports"]["long_conv"].get("status")},
            ),
            "long_conv_marginal": input_entry(LONG_CONV_MARGINAL),
            "long_conv_convolution": input_entry(LONG_CONV_CONVOLUTION),
            "long_conv_tables": input_entry(LONG_CONV_TABLES),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_object": input_entry(LONG_PROF_OBJECT),
            "long_prof_profunctor": input_entry(LONG_PROF_PROFUNCTOR),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "hlim": relpath(OUT_DIR / "hlim.json"),
            "horizon_csv": relpath(OUT_DIR / "horizon.csv"),
            "obstruction_csv": relpath(OUT_DIR / "obstruction.csv"),
            "propagation_csv": relpath(OUT_DIR / "propagation.csv"),
            "split_csv": relpath(OUT_DIR / "split.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "horizons 9-16 are covered by exact split-convolution identities using horizons at most 8",
                "the profunctor-controlled public path-sum comparison stops at horizon 8",
                "exactly 208 extension marginal rows are missing profunctor comparison rows",
                "the 112 long_nat horizon-extension laws are generated by those missing rows plus internal readout propagation",
            ],
            "does_not_certify_because_out_of_scope": [
                "a new profunctor object extending path_sum_distribution to horizon 16",
                "profunctor naturality beyond the certified horizon-8 object",
                "an infinite-horizon LLN theorem",
                "optimality of the horizon-16 cutoff",
            ],
        },
        "next_highest_yield_item": (
            "Build long_ext: construct the minimal formal profunctor extension "
            "that would add the 208 missing comparison rows, then check whether "
            "it is a genuine tensor-lookup object or only a convolution shadow."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.hlim.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.hlim.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "hlim": hlim_payload,
        "horizon_csv": csv_text(HORIZON_COLUMNS, rows["horizon_rows"]),
        "obstruction_csv": csv_text(OBSTRUCTION_COLUMNS, rows["obstruction_rows"]),
        "propagation_csv": csv_text(PROPAGATION_COLUMNS, rows["propagation_rows"]),
        "split_csv": csv_text(SPLIT_COLUMNS, rows["split_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "horizon_table": rows["horizon_table"],
        "obstruction_table": rows["obstruction_table"],
        "propagation_table": rows["propagation_table"],
        "split_table": rows["split_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "hlim.json", payloads["hlim"])
    (OUT_DIR / "horizon.csv").write_text(payloads["horizon_csv"], encoding="utf-8")
    (OUT_DIR / "obstruction.csv").write_text(
        payloads["obstruction_csv"], encoding="utf-8"
    )
    (OUT_DIR / "propagation.csv").write_text(
        payloads["propagation_csv"], encoding="utf-8"
    )
    (OUT_DIR / "split.csv").write_text(payloads["split_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        horizon_table=payloads["horizon_table"],
        obstruction_table=payloads["obstruction_table"],
        propagation_table=payloads["propagation_table"],
        split_table=payloads["split_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
