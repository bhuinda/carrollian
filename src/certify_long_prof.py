from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_prof import (
        COMPOSE_COLUMNS,
        COMPOSE_DIGEST_COLUMNS,
        COMPOSE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_ABSORB_MATRIX,
        LONG_ABSORB_REPORT,
        LONG_ABSORB_TABLES,
        LONG_DEV_DISTRIBUTION,
        LONG_DEV_REPORT,
        LONG_DEV_TABLES,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBJECT_COLUMNS,
        OBJECT_DIGEST_COLUMNS,
        OBJECT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COMPONENT_COLUMNS,
        OWNER_COMPONENT_DIGEST_COLUMNS,
        OWNER_COMPONENT_TEXT_HASH,
        PROFUNCTOR_COLUMNS,
        PROFUNCTOR_DIGEST_COLUMNS,
        PROFUNCTOR_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        compose_text,
        object_text,
        owner_component_text,
        profunctor_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_prof import (
        COMPOSE_COLUMNS,
        COMPOSE_DIGEST_COLUMNS,
        COMPOSE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_ABSORB_MATRIX,
        LONG_ABSORB_REPORT,
        LONG_ABSORB_TABLES,
        LONG_DEV_DISTRIBUTION,
        LONG_DEV_REPORT,
        LONG_DEV_TABLES,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBJECT_COLUMNS,
        OBJECT_DIGEST_COLUMNS,
        OBJECT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COMPONENT_COLUMNS,
        OWNER_COMPONENT_DIGEST_COLUMNS,
        OWNER_COMPONENT_TEXT_HASH,
        PROFUNCTOR_COLUMNS,
        PROFUNCTOR_DIGEST_COLUMNS,
        PROFUNCTOR_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        compose_text,
        object_text,
        owner_component_text,
        profunctor_text,
        rows_from_table,
        self_hash,
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_prof() -> dict[str, Any]:
    expected = build_payloads()
    prof = load_json(OUT_DIR / "prof.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if prof != expected["prof"]:
        raise AssertionError("long_prof prof JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_prof cert mismatch")
    for filename, key in {
        "object.csv": "object_csv",
        "profunctor.csv": "profunctor_csv",
        "owner_component.csv": "owner_component_csv",
        "compose.csv": "compose_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_prof {filename} mismatch")

    for key, expected_array in {
        "object_table": expected["object_table"],
        "profunctor_table": expected["profunctor_table"],
        "owner_component_table": expected["owner_component_table"],
        "compose_table": expected["compose_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_prof table mismatch: {key}")

    if report.get("schema") != "long.prof.report@1":
        raise AssertionError("long_prof report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_prof report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_prof all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_prof checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_prof report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_prof report hash mismatch")

    csv_shapes = [
        ("object.csv", OBJECT_COLUMNS, 9),
        ("profunctor.csv", PROFUNCTOR_COLUMNS, 8),
        ("owner_component.csv", OWNER_COMPONENT_COLUMNS, 777),
        ("compose.csv", COMPOSE_COLUMNS, 92),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_prof {filename} shape mismatch")

    table_shapes = {
        "object_table": (9, len(OBJECT_DIGEST_COLUMNS)),
        "profunctor_table": (8, len(PROFUNCTOR_DIGEST_COLUMNS)),
        "owner_component_table": (777, len(OWNER_COMPONENT_DIGEST_COLUMNS)),
        "compose_table": (92, len(COMPOSE_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_prof {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "object_count": 9,
        "profunctor_count": 8,
        "line_point_count": 985,
        "line_pair_count": 970_225,
        "owner_count": 259,
        "weak_class_count": 13,
        "active_owner_count": 51,
        "inactive_owner_count": 208,
        "boundary_component_count": 3,
        "boundary_total_count": 4_584,
        "deviation_distribution_row_count": 80,
        "owner_component_row_count": 777,
        "owner_component_positive_count": 675,
        "owner_component_row_sum_violation_count": 0,
        "owner_component_active_positive_count": 51,
        "owner_component_inactive_positive_count": 624,
        "owner_component_dominant0_count": 119,
        "owner_component_dominant1_count": 3,
        "owner_component_dominant2_count": 137,
        "component0_active_owner_count": 33,
        "component1_active_owner_count": 1,
        "component2_active_owner_count": 17,
        "owner_component_num_digit_max": 255,
        "owner_component_den_digit_max": 256,
        "compose_law_count": 92,
        "compose_equal_count": 92,
        "compose_violation_count": 0,
        "composition_left_num_digit_max": 1_819,
        "composition_left_den_digit_max": 1_820,
        "long_rec_input_certified": 1,
        "long_lap_input_certified": 1,
        "long_absorb_input_certified": 1,
        "long_markov_input_certified": 1,
        "long_dev_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_prof observable {key} mismatch")

    if hashlib.sha256(object_text(csv_rows["object.csv"]).encode("ascii")).hexdigest() != OBJECT_TEXT_HASH:
        raise AssertionError("long_prof object hash mismatch")
    if hashlib.sha256(
        profunctor_text(csv_rows["profunctor.csv"]).encode("ascii")
    ).hexdigest() != PROFUNCTOR_TEXT_HASH:
        raise AssertionError("long_prof profunctor hash mismatch")
    if hashlib.sha256(
        owner_component_text(csv_rows["owner_component.csv"]).encode("ascii")
    ).hexdigest() != OWNER_COMPONENT_TEXT_HASH:
        raise AssertionError("long_prof owner_component hash mismatch")
    if hashlib.sha256(compose_text(csv_rows["compose.csv"]).encode("ascii")).hexdigest() != COMPOSE_TEXT_HASH:
        raise AssertionError("long_prof compose hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_tables": LONG_REC_TABLES,
        "long_lap_report": LONG_LAP_REPORT,
        "long_lap_tables": LONG_LAP_TABLES,
        "long_absorb_report": LONG_ABSORB_REPORT,
        "long_absorb_tables": LONG_ABSORB_TABLES,
        "long_absorb_matrix": LONG_ABSORB_MATRIX,
        "long_markov_report": LONG_MARKOV_REPORT,
        "long_markov_kernel": LONG_MARKOV_KERNEL,
        "long_markov_stationary": LONG_MARKOV_STATIONARY,
        "long_dev_report": LONG_DEV_REPORT,
        "long_dev_distribution": LONG_DEV_DISTRIBUTION,
        "long_dev_tables": LONG_DEV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.prof.manifest@1":
        raise AssertionError("long_prof manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_prof manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_prof manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_prof missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_prof index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_prof index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.prof.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "objects": witness.get("objects"),
            "profunctors": witness.get("profunctors"),
            "owner_component": witness.get("owner_component"),
            "composition": witness.get("composition"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_prof(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
