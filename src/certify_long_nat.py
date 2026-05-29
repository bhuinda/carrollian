from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_nat import (
        DEP_COLUMNS,
        DEP_TEXT_HASH,
        DERIVE_SCRIPT,
        FAMILY_COLUMNS,
        FAMILY_TEXT_HASH,
        INDEX_PATH,
        LONG_MIN_BASIS,
        LONG_MIN_FORCE,
        LONG_MIN_REPORT,
        LONG_MIN_TABLES,
        LONG_UNIV_ARROW,
        LONG_UNIV_LAW,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        NAT_COLUMNS,
        NAT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_nat import (
        DEP_COLUMNS,
        DEP_TEXT_HASH,
        DERIVE_SCRIPT,
        FAMILY_COLUMNS,
        FAMILY_TEXT_HASH,
        INDEX_PATH,
        LONG_MIN_BASIS,
        LONG_MIN_FORCE,
        LONG_MIN_REPORT,
        LONG_MIN_TABLES,
        LONG_UNIV_ARROW,
        LONG_UNIV_LAW,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        NAT_COLUMNS,
        NAT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def validate_long_nat() -> dict[str, Any]:
    expected = build_payloads()
    nat_payload = load_json(OUT_DIR / "nat.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if nat_payload != expected["nat"]:
        raise AssertionError("long_nat nat JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_nat cert mismatch")
    for filename, key in {
        "naturality.csv": "naturality_csv",
        "dependency.csv": "dependency_csv",
        "family.csv": "family_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_nat {filename} mismatch")

    for key, expected_array in {
        "nat_table": expected["nat_table"],
        "dependency_table": expected["dependency_table"],
        "family_table": expected["family_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_nat table mismatch: {key}")

    if report.get("schema") != "long.nat.report@1":
        raise AssertionError("long_nat report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_nat report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_nat all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_nat checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_nat report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_nat report hash mismatch")

    csv_shapes = [
        ("naturality.csv", NAT_COLUMNS, 306),
        ("dependency.csv", DEP_COLUMNS, 808),
        ("family.csv", FAMILY_COLUMNS, 6),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_nat {filename} shape mismatch")

    table_shapes = {
        "nat_table": (306, len(NAT_COLUMNS)),
        "dependency_table": (808, len(DEP_COLUMNS)),
        "family_table": (6, len(FAMILY_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_nat {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "law_count": 306,
        "basis_law_count": 74,
        "forced_law_count": 232,
        "family_count": 6,
        "dependency_edge_count": 808,
        "acyclic_dependency_edge_count": 808,
        "bad_dependency_edge_count": 0,
        "profunctor_controlled_law_count": 194,
        "external_input_law_count": 112,
        "basis_profunctor_controlled_count": 74,
        "readout_law_count": 223,
        "row_sum_dependency_edge_count": 74,
        "readout_dependency_edge_count": 734,
        "law_dependency_total": 808,
        "external_dependency_total": 1456,
        "dependency_max": 33,
        "violation_count": 0,
        "long_univ_input_certified": 1,
        "long_min_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_nat observable {key} mismatch")

    if hashlib.sha256(
        digest_text(NAT_COLUMNS, csv_rows["naturality.csv"]).encode("ascii")
    ).hexdigest() != NAT_TEXT_HASH:
        raise AssertionError("long_nat naturality hash mismatch")
    if hashlib.sha256(
        digest_text(DEP_COLUMNS, csv_rows["dependency.csv"]).encode("ascii")
    ).hexdigest() != DEP_TEXT_HASH:
        raise AssertionError("long_nat dependency hash mismatch")
    if hashlib.sha256(
        digest_text(FAMILY_COLUMNS, csv_rows["family.csv"]).encode("ascii")
    ).hexdigest() != FAMILY_TEXT_HASH:
        raise AssertionError("long_nat family hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_univ_report": LONG_UNIV_REPORT,
        "long_univ_law": LONG_UNIV_LAW,
        "long_univ_arrow": LONG_UNIV_ARROW,
        "long_univ_tables": LONG_UNIV_TABLES,
        "long_min_report": LONG_MIN_REPORT,
        "long_min_basis": LONG_MIN_BASIS,
        "long_min_force": LONG_MIN_FORCE,
        "long_min_tables": LONG_MIN_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.nat.manifest@1":
        raise AssertionError("long_nat manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_nat manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_nat manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_nat missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_nat index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_nat index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.nat.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "naturality": witness.get("naturality"),
            "dependency_graph": witness.get("dependency_graph"),
            "families": witness.get("families"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_nat(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
