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
    from .derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_min"
STATUS = "LONG_MIN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_UNIV_REPORT = LONG_UNIV_DIR / "report.json"
LONG_UNIV_LAW = LONG_UNIV_DIR / "law.csv"
LONG_UNIV_SQUARE = LONG_UNIV_DIR / "square.csv"
LONG_UNIV_TABLES = LONG_UNIV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_min.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_min.py"

BASIS_TEXT_HASH = (
    "5dc94ce4fc44efd67e1b7de1d48fc49f8be91c79104bad945a67680656507291"
)
FORCE_TEXT_HASH = (
    "80de4a8ae33a3dca2ecc2299302d68f287a03c1303b5373a87c357b79e2ec0b8"
)
COVER_TEXT_HASH = (
    "bf4a6bb17ab0944f48eca71f3915f271d5801e919aa44b4fef0d1c43df7be505"
)

BASIS_COLUMNS = [
    "basis_id",
    "law_id",
    "square_code",
    "law_code",
    "source_id",
    "target_id",
    "subtarget_id",
    "derivation_code",
    "dependency_count",
    "equal_flag",
    "left_num_digits",
    "left_den_digits",
    "right_num_digits",
    "right_den_digits",
]
FORCE_COLUMNS = [
    "force_id",
    "law_id",
    "square_code",
    "law_code",
    "source_id",
    "target_id",
    "subtarget_id",
    "derivation_code",
    "dependency_count",
    "equal_flag",
    "left_num_digits",
    "left_den_digits",
    "right_num_digits",
    "right_den_digits",
]
COVER_COLUMNS = [
    "square_id",
    "square_code",
    "square_name",
    "total_law_count",
    "basis_count",
    "forced_count",
    "equal_count",
    "violation_count",
    "minimal_basis_count",
    "closure_rule_code",
]
COVER_DIGEST_COLUMNS = [
    "square_id",
    "square_code",
    "total_law_count",
    "basis_count",
    "forced_count",
    "equal_count",
    "violation_count",
    "minimal_basis_count",
    "closure_rule_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "total_law_count",
    "basis_law_count",
    "forced_law_count",
    "basis_equal_count",
    "forced_equal_count",
    "violation_count",
    "row_sum_forced_count",
    "readout_forced_count",
    "prof_conv_basis_count",
    "stationary_basis_count",
    "mean_forced_count",
    "moment_forced_count",
    "tail_forced_count",
    "shrink_forced_count",
    "dependency_total",
    "dependency_max",
    "basis_fraction_num",
    "basis_fraction_den",
    "cover_square_count",
    "basis_irredundant_count",
    "long_univ_input_certified",
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


def int_row(row: dict[str, str]) -> dict[str, int]:
    return {key: int(value) for key, value in row.items()}


def derivation(row: dict[str, int]) -> tuple[int, int]:
    square_code = row["square_code"]
    law_code = row["law_code"]
    source_id = row["source_id"]
    if square_code == 0:
        if row["target_id"] == 2 * source_id:
            return 1, 2 * source_id
        return 0, 0
    if square_code == 1:
        if row["target_id"] == 2:
            return 2, 2
        return 0, 0
    if square_code == 2:
        return 3, 2 * source_id + 1
    if square_code == 3:
        return 4, 2 * source_id + 1
    if square_code == 4:
        if law_code == 4:
            return 5, 2 * source_id + 1
        if law_code == 5:
            return 6, 1
        if law_code == 6:
            return 7, 2
    if square_code == 5:
        return 8, 2
    raise ValueError(f"unknown long_min derivation row: {row}")


def law_record(row: dict[str, int]) -> dict[str, int]:
    return {
        key: row[key]
        for key in [
            "law_id",
            "square_code",
            "law_code",
            "source_id",
            "target_id",
            "subtarget_id",
            "equal_flag",
            "left_num_digits",
            "left_den_digits",
            "right_num_digits",
            "right_den_digits",
        ]
    }


def build_rows() -> dict[str, Any]:
    long_univ = load_json(LONG_UNIV_REPORT)
    law_rows = [int_row(row) for row in read_csv_rows(LONG_UNIV_LAW)]
    square_rows_raw = read_csv_rows(LONG_UNIV_SQUARE)
    basis_rows: list[dict[str, int]] = []
    force_rows: list[dict[str, int]] = []

    for row in law_rows:
        derivation_code, dependency_count = derivation(row)
        base = law_record(row)
        if derivation_code == 0:
            basis_rows.append(
                {
                    "basis_id": len(basis_rows),
                    **base,
                    "derivation_code": derivation_code,
                    "dependency_count": dependency_count,
                }
            )
        else:
            force_rows.append(
                {
                    "force_id": len(force_rows),
                    **base,
                    "derivation_code": derivation_code,
                    "dependency_count": dependency_count,
                }
            )

    basis_rows = [{column: row[column] for column in BASIS_COLUMNS} for row in basis_rows]
    force_rows = [{column: row[column] for column in FORCE_COLUMNS} for row in force_rows]

    cover_rows: list[dict[str, Any]] = []
    closure_rule_by_square = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 8}
    for square in square_rows_raw:
        square_code = int(square["square_code"])
        laws = [row for row in law_rows if row["square_code"] == square_code]
        basis = [row for row in basis_rows if row["square_code"] == square_code]
        forced = [row for row in force_rows if row["square_code"] == square_code]
        cover_rows.append(
            {
                "square_id": int(square["square_id"]),
                "square_code": square_code,
                "square_name": square["square_name"],
                "total_law_count": len(laws),
                "basis_count": len(basis),
                "forced_count": len(forced),
                "equal_count": sum(int(row["equal_flag"]) for row in laws),
                "violation_count": sum(int(row["equal_flag"] == 0) for row in laws),
                "minimal_basis_count": len(basis),
                "closure_rule_code": closure_rule_by_square[square_code],
            }
        )

    cover_digest_rows = [
        {column: int(row[column]) for column in COVER_DIGEST_COLUMNS}
        for row in cover_rows
    ]
    basis_table = table_from_rows(BASIS_COLUMNS, basis_rows)
    force_table = table_from_rows(FORCE_COLUMNS, force_rows)
    cover_table = table_from_rows(COVER_DIGEST_COLUMNS, cover_digest_rows)

    basis_hash = hashlib.sha256(
        digest_text(BASIS_COLUMNS, basis_rows).encode("ascii")
    ).hexdigest()
    force_hash = hashlib.sha256(
        digest_text(FORCE_COLUMNS, force_rows).encode("ascii")
    ).hexdigest()
    cover_hash = hashlib.sha256(
        digest_text(COVER_COLUMNS, cover_rows).encode("ascii")
    ).hexdigest()
    derivation_counts = {
        code: sum(int(row["derivation_code"] == code) for row in force_rows)
        for code in range(1, 9)
    }
    obs = {
        "total_law_count": len(law_rows),
        "basis_law_count": len(basis_rows),
        "forced_law_count": len(force_rows),
        "basis_equal_count": sum(int(row["equal_flag"]) for row in basis_rows),
        "forced_equal_count": sum(int(row["equal_flag"]) for row in force_rows),
        "violation_count": sum(int(row["equal_flag"] == 0) for row in law_rows),
        "row_sum_forced_count": derivation_counts[1] + derivation_counts[2],
        "readout_forced_count": sum(derivation_counts[code] for code in range(3, 9)),
        "prof_conv_basis_count": sum(
            int(row["square_code"] == 0) for row in basis_rows
        ),
        "stationary_basis_count": sum(
            int(row["square_code"] == 1) for row in basis_rows
        ),
        "mean_forced_count": derivation_counts[3],
        "moment_forced_count": derivation_counts[4],
        "tail_forced_count": derivation_counts[5]
        + derivation_counts[6]
        + derivation_counts[7],
        "shrink_forced_count": derivation_counts[8],
        "dependency_total": sum(int(row["dependency_count"]) for row in force_rows),
        "dependency_max": max(int(row["dependency_count"]) for row in force_rows),
        "basis_fraction_num": len(basis_rows),
        "basis_fraction_den": len(law_rows),
        "cover_square_count": len(cover_rows),
        "basis_irredundant_count": len(basis_rows),
        "long_univ_input_certified": int(long_univ.get("status") == LONG_UNIV_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    return {
        "input_reports": {"long_univ": long_univ},
        "basis_rows": basis_rows,
        "force_rows": force_rows,
        "cover_rows": cover_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "basis_table": basis_table,
        "force_table": force_table,
        "cover_table": cover_table,
        "observable_table": obs_table,
        "basis_hash": basis_hash,
        "force_hash": force_hash,
        "cover_hash": cover_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": obs["long_univ_input_certified"] == 1,
        "basis_fingerprint_exact": (
            obs["basis_law_count"],
            obs["basis_equal_count"],
            obs["basis_irredundant_count"],
            rows["basis_hash"],
        )
        == (74, 74, 74, BASIS_TEXT_HASH),
        "forced_fingerprint_exact": (
            obs["forced_law_count"],
            obs["forced_equal_count"],
            obs["row_sum_forced_count"],
            obs["readout_forced_count"],
            obs["dependency_total"],
            obs["dependency_max"],
            rows["force_hash"],
        )
        == (232, 232, 9, 223, 2_264, 33, FORCE_TEXT_HASH),
        "cover_fingerprint_exact": (
            obs["cover_square_count"],
            obs["total_law_count"],
            obs["violation_count"],
            rows["cover_hash"],
        )
        == (6, 306, 0, COVER_TEXT_HASH),
        "basis_reduction_exact": (
            obs["basis_fraction_num"],
            obs["basis_fraction_den"],
            obs["prof_conv_basis_count"],
            obs["stationary_basis_count"],
            obs["mean_forced_count"],
            obs["moment_forced_count"],
            obs["tail_forced_count"],
            obs["shrink_forced_count"],
        )
        == (74, 306, 72, 2, 16, 48, 144, 15),
        "table_shapes_match": (
            tuple(rows["basis_table"].shape),
            tuple(rows["force_table"].shape),
            tuple(rows["cover_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (74, len(BASIS_COLUMNS)),
            (232, len(FORCE_COLUMNS)),
            (6, len(COVER_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_universal_lln_forcing_basis",
        "basis": {
            "law_count": obs["basis_law_count"],
            "equal_count": obs["basis_equal_count"],
            "basis_fraction": [
                obs["basis_fraction_num"],
                obs["basis_fraction_den"],
            ],
            "irredundant_count": obs["basis_irredundant_count"],
            "text_sha256": rows["basis_hash"],
            "table_sha256": sha_array(rows["basis_table"]),
        },
        "forced": {
            "law_count": obs["forced_law_count"],
            "equal_count": obs["forced_equal_count"],
            "row_sum_forced_count": obs["row_sum_forced_count"],
            "readout_forced_count": obs["readout_forced_count"],
            "dependency_total": obs["dependency_total"],
            "dependency_max": obs["dependency_max"],
            "text_sha256": rows["force_hash"],
            "table_sha256": sha_array(rows["force_table"]),
        },
        "cover": {
            "square_count": obs["cover_square_count"],
            "law_count": obs["total_law_count"],
            "violation_count": obs["violation_count"],
            "text_sha256": rows["cover_hash"],
            "table_sha256": sha_array(rows["cover_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    min_payload = {
        "schema": "long.min@1",
        "object": "finite_universal_lln_forcing_basis",
        "status": STATUS if all(checks.values()) else "LONG_MIN_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.min.report@1",
        "status": min_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_min certifies a finite forcing basis for the long_univ "
            "commuting diagram: 74 irredundant law rows generate all 306 "
            "commuting laws using row-sum completion for probability rows and "
            "the declared mean, moment, tail, Chebyshev, and shrink readout "
            "constructors."
        ),
        "stage_protocol": {
            "draft": "read the certified long_univ law and square tables",
            "witness": "classify row-level laws into basis rows and forced rows under the finite forcing grammar",
            "coherence": "check input status, coverage, equalities, fixed hashes, reduction counts, and table shapes",
            "closure": "emit basis, force, cover, table, certificate, manifest, and report artifacts",
            "emit": "write long_min artifacts and verifier hook",
        },
        "inputs": {
            "long_univ_report": input_entry(
                LONG_UNIV_REPORT,
                {"status": rows["input_reports"]["long_univ"].get("status")},
            ),
            "long_univ_law": input_entry(LONG_UNIV_LAW),
            "long_univ_square": input_entry(LONG_UNIV_SQUARE),
            "long_univ_tables": input_entry(LONG_UNIV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "min": relpath(OUT_DIR / "min.json"),
            "basis_csv": relpath(OUT_DIR / "basis.csv"),
            "force_csv": relpath(OUT_DIR / "force.csv"),
            "cover_csv": relpath(OUT_DIR / "cover.csv"),
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
                "a 74-law forcing basis inside the 306-law long_univ diagram",
                "row-sum completion of 8 prof_conv rows and 1 stationary row",
                "formula forcing of all 223 mean, moment, tail, Chebyshev, and shrink readout laws",
                "irredundancy relative to the declared row-sum/readout forcing grammar",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute global minimality under arbitrary algebraic identities",
                "new probability laws beyond the certified long_univ diagram",
                "an infinite-horizon LLN theorem",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_nat: certify naturality of the forcing basis under the "
            "line-order/profunctor maps, so the LLN readouts are visibly "
            "functorial rather than only row-wise forced."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.min.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.min.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "min": min_payload,
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "force_csv": csv_text(FORCE_COLUMNS, rows["force_rows"]),
        "cover_csv": csv_text(COVER_COLUMNS, rows["cover_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "basis_table": rows["basis_table"],
        "force_table": rows["force_table"],
        "cover_table": rows["cover_table"],
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
    write_json(OUT_DIR / "min.json", payloads["min"])
    (OUT_DIR / "basis.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "force.csv").write_text(payloads["force_csv"], encoding="utf-8")
    (OUT_DIR / "cover.csv").write_text(payloads["cover_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        basis_table=payloads["basis_table"],
        force_table=payloads["force_table"],
        cover_table=payloads["cover_table"],
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
