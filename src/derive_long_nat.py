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
    from .derive_long_min import OUT_DIR as LONG_MIN_DIR, STATUS as LONG_MIN_STATUS
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
    from derive_long_min import OUT_DIR as LONG_MIN_DIR, STATUS as LONG_MIN_STATUS
    from derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_nat"
STATUS = "LONG_NAT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_UNIV_REPORT = LONG_UNIV_DIR / "report.json"
LONG_UNIV_LAW = LONG_UNIV_DIR / "law.csv"
LONG_UNIV_ARROW = LONG_UNIV_DIR / "arrow.csv"
LONG_UNIV_TABLES = LONG_UNIV_DIR / "tables.npz"
LONG_MIN_REPORT = LONG_MIN_DIR / "report.json"
LONG_MIN_BASIS = LONG_MIN_DIR / "basis.csv"
LONG_MIN_FORCE = LONG_MIN_DIR / "force.csv"
LONG_MIN_TABLES = LONG_MIN_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_nat.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_nat.py"

NAT_TEXT_HASH = "4d48141025b54eed39674bc63a835278eead64505c119423b0efd2469f0cefe3"
DEP_TEXT_HASH = "2f8952ca7fef0e7bb0c37a16473e3a1a3df228ce400d9fe1fa5bbc8bb858554b"
FAMILY_TEXT_HASH = "a6b19741389053949b2705d6be06513aaf2e754ac34f21ea6d1badb7b9da1dac"

NAT_COLUMNS = [
    "nat_id",
    "law_id",
    "square_code",
    "law_code",
    "source_id",
    "target_id",
    "subtarget_id",
    "family_code",
    "carrier_arrow_code",
    "readout_arrow_code",
    "comparison_arrow_code",
    "stage_code",
    "basis_flag",
    "forced_flag",
    "profunctor_control_flag",
    "external_input_flag",
    "dependency_count",
    "law_dependency_count",
    "external_dependency_count",
    "equal_flag",
]
DEP_COLUMNS = [
    "edge_id",
    "from_law_id",
    "to_law_id",
    "dependency_kind_code",
    "source_id",
    "target_id",
    "weight_code",
]
FAMILY_COLUMNS = [
    "family_id",
    "family_code",
    "law_count",
    "basis_count",
    "forced_count",
    "profunctor_controlled_count",
    "external_input_count",
    "dependency_edge_count",
    "violation_count",
    "carrier_arrow_code",
    "readout_arrow_code",
    "comparison_arrow_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "law_count",
    "basis_law_count",
    "forced_law_count",
    "family_count",
    "dependency_edge_count",
    "acyclic_dependency_edge_count",
    "bad_dependency_edge_count",
    "profunctor_controlled_law_count",
    "external_input_law_count",
    "basis_profunctor_controlled_count",
    "readout_law_count",
    "row_sum_dependency_edge_count",
    "readout_dependency_edge_count",
    "law_dependency_total",
    "external_dependency_total",
    "dependency_max",
    "violation_count",
    "long_univ_input_certified",
    "long_min_input_certified",
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


def map_meta(row: dict[str, int]) -> tuple[int, int, int, int, int, int]:
    square_code = row["square_code"]
    law_code = row["law_code"]
    source_id = row["source_id"]
    if square_code == 0:
        return 4, -1, 5, 0, 1, 0
    if square_code == 1:
        return 2, -1, 5, 1, 1, 0
    if square_code == 2:
        return 5, 6, -1, 2, int(source_id <= 8), int(source_id > 8)
    if square_code == 3:
        return 5, 7, -1, 2, int(source_id <= 8), int(source_id > 8)
    if square_code == 4:
        return 5, 8, -1, {4: 2, 5: 3, 6: 4}[law_code], int(source_id <= 8), int(source_id > 8)
    if square_code == 5:
        return 7, 9, -1, 5, int(source_id <= 8), int(source_id > 8)
    raise ValueError(f"unknown long_nat naturality row: {row}")


def dependency_spec(
    row: dict[str, int],
    *,
    basis_ids: set[int],
    by_key: dict[tuple[int, int, int, int, int], int],
    by_square_source: dict[tuple[int, int], list[dict[str, int]]],
) -> tuple[list[tuple[int, int, int, int, int]], int]:
    square_code = row["square_code"]
    law_code = row["law_code"]
    source_id = row["source_id"]
    target_id = row["target_id"]
    dependencies: list[tuple[int, int, int, int, int]] = []
    external_dependency_count = 0

    if square_code == 0 and row["law_id"] not in basis_ids:
        for dep in by_square_source[(0, source_id)]:
            if dep["law_id"] != row["law_id"]:
                dependencies.append((dep["law_id"], 1, source_id, dep["target_id"], 1))
    elif square_code == 1 and row["law_id"] not in basis_ids:
        for dep in by_square_source[(1, source_id)]:
            if dep["law_id"] != row["law_id"]:
                dependencies.append((dep["law_id"], 1, source_id, dep["target_id"], 1))
    elif square_code == 2:
        if source_id <= 8:
            for dep in by_square_source[(0, source_id)]:
                dependencies.append((dep["law_id"], 2, source_id, dep["target_id"], dep["target_id"]))
        else:
            external_dependency_count = 2 * source_id + 1
    elif square_code == 3:
        if source_id <= 8:
            for dep in by_square_source[(0, source_id)]:
                dependencies.append((dep["law_id"], 3, source_id, dep["target_id"], dep["target_id"]))
        else:
            external_dependency_count = 2 * source_id + 1
    elif square_code == 4 and law_code == 4:
        if source_id <= 8:
            for dep in by_square_source[(0, source_id)]:
                dependencies.append((dep["law_id"], 4, source_id, dep["target_id"], dep["target_id"]))
        else:
            external_dependency_count = 2 * source_id + 1
    elif square_code == 4 and law_code == 5:
        dependencies.append((by_key[(3, 3, source_id, 2, -1)], 5, source_id, target_id, 1))
    elif square_code == 4 and law_code == 6:
        dependencies.append((by_key[(4, 4, source_id, target_id, 0)], 6, source_id, target_id, 1))
        dependencies.append((by_key[(4, 5, source_id, target_id, 1)], 7, source_id, target_id, 1))
    elif square_code == 5:
        dependencies.append((by_key[(3, 3, source_id - 1, 2, -1)], 8, source_id, 0, 1))
        dependencies.append((by_key[(3, 3, source_id, 2, -1)], 9, source_id, 0, 1))

    return dependencies, external_dependency_count


def build_rows() -> dict[str, Any]:
    long_univ = load_json(LONG_UNIV_REPORT)
    long_min = load_json(LONG_MIN_REPORT)
    law_rows = [int_row(row) for row in read_csv_rows(LONG_UNIV_LAW)]
    basis_ids = {int(row["law_id"]) for row in read_csv_rows(LONG_MIN_BASIS)}

    by_key = {
        (
            row["square_code"],
            row["law_code"],
            row["source_id"],
            row["target_id"],
            row["subtarget_id"],
        ): row["law_id"]
        for row in law_rows
    }
    by_square_source: dict[tuple[int, int], list[dict[str, int]]] = {}
    for row in law_rows:
        by_square_source.setdefault((row["square_code"], row["source_id"]), []).append(row)

    nat_rows: list[dict[str, int]] = []
    dependency_rows: list[dict[str, int]] = []
    for row in law_rows:
        carrier_arrow_code, readout_arrow_code, comparison_arrow_code, stage_code, profunctor_control_flag, external_input_flag = map_meta(row)
        dependencies, external_dependency_count = dependency_spec(
            row,
            basis_ids=basis_ids,
            by_key=by_key,
            by_square_source=by_square_source,
        )
        nat_rows.append(
            {
                "nat_id": len(nat_rows),
                "law_id": row["law_id"],
                "square_code": row["square_code"],
                "law_code": row["law_code"],
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "subtarget_id": row["subtarget_id"],
                "family_code": row["square_code"],
                "carrier_arrow_code": carrier_arrow_code,
                "readout_arrow_code": readout_arrow_code,
                "comparison_arrow_code": comparison_arrow_code,
                "stage_code": stage_code,
                "basis_flag": int(row["law_id"] in basis_ids),
                "forced_flag": int(row["law_id"] not in basis_ids),
                "profunctor_control_flag": profunctor_control_flag,
                "external_input_flag": external_input_flag,
                "dependency_count": len(dependencies) + external_dependency_count,
                "law_dependency_count": len(dependencies),
                "external_dependency_count": external_dependency_count,
                "equal_flag": row["equal_flag"],
            }
        )
        for from_law_id, dependency_kind_code, source_id, target_id, weight_code in dependencies:
            dependency_rows.append(
                {
                    "edge_id": len(dependency_rows),
                    "from_law_id": from_law_id,
                    "to_law_id": row["law_id"],
                    "dependency_kind_code": dependency_kind_code,
                    "source_id": source_id,
                    "target_id": target_id,
                    "weight_code": weight_code,
                }
            )

    law_family = {row["law_id"]: row["family_code"] for row in nat_rows}
    family_rows: list[dict[str, int]] = []
    for family_code in range(6):
        rows = [row for row in nat_rows if row["family_code"] == family_code]
        deps = [
            row
            for row in dependency_rows
            if law_family[row["to_law_id"]] == family_code
        ]
        family_rows.append(
            {
                "family_id": family_code,
                "family_code": family_code,
                "law_count": len(rows),
                "basis_count": sum(int(row["basis_flag"]) for row in rows),
                "forced_count": sum(int(row["forced_flag"]) for row in rows),
                "profunctor_controlled_count": sum(
                    int(row["profunctor_control_flag"]) for row in rows
                ),
                "external_input_count": sum(int(row["external_input_flag"]) for row in rows),
                "dependency_edge_count": len(deps),
                "violation_count": sum(int(row["equal_flag"] == 0) for row in rows),
                "carrier_arrow_code": rows[0]["carrier_arrow_code"],
                "readout_arrow_code": rows[0]["readout_arrow_code"],
                "comparison_arrow_code": rows[0]["comparison_arrow_code"],
            }
        )

    nat_hash = hashlib.sha256(
        digest_text(NAT_COLUMNS, nat_rows).encode("ascii")
    ).hexdigest()
    dependency_hash = hashlib.sha256(
        digest_text(DEP_COLUMNS, dependency_rows).encode("ascii")
    ).hexdigest()
    family_hash = hashlib.sha256(
        digest_text(FAMILY_COLUMNS, family_rows).encode("ascii")
    ).hexdigest()

    obs = {
        "law_count": len(nat_rows),
        "basis_law_count": sum(int(row["basis_flag"]) for row in nat_rows),
        "forced_law_count": sum(int(row["forced_flag"]) for row in nat_rows),
        "family_count": len(family_rows),
        "dependency_edge_count": len(dependency_rows),
        "acyclic_dependency_edge_count": sum(
            int(row["from_law_id"] < row["to_law_id"]) for row in dependency_rows
        ),
        "bad_dependency_edge_count": sum(
            int(row["from_law_id"] >= row["to_law_id"]) for row in dependency_rows
        ),
        "profunctor_controlled_law_count": sum(
            int(row["profunctor_control_flag"]) for row in nat_rows
        ),
        "external_input_law_count": sum(int(row["external_input_flag"]) for row in nat_rows),
        "basis_profunctor_controlled_count": sum(
            int(row["basis_flag"] and row["profunctor_control_flag"]) for row in nat_rows
        ),
        "readout_law_count": sum(int(row["square_code"] in {2, 3, 4, 5}) for row in nat_rows),
        "row_sum_dependency_edge_count": sum(
            int(row["dependency_kind_code"] == 1) for row in dependency_rows
        ),
        "readout_dependency_edge_count": sum(
            int(row["dependency_kind_code"] != 1) for row in dependency_rows
        ),
        "law_dependency_total": sum(int(row["law_dependency_count"]) for row in nat_rows),
        "external_dependency_total": sum(
            int(row["external_dependency_count"]) for row in nat_rows
        ),
        "dependency_max": max(int(row["dependency_count"]) for row in nat_rows),
        "violation_count": sum(int(row["equal_flag"] == 0) for row in nat_rows),
        "long_univ_input_certified": int(long_univ.get("status") == LONG_UNIV_STATUS),
        "long_min_input_certified": int(long_min.get("status") == LONG_MIN_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]

    return {
        "input_reports": {"long_univ": long_univ, "long_min": long_min},
        "nat_rows": nat_rows,
        "dependency_rows": dependency_rows,
        "family_rows": family_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "nat_table": table_from_rows(NAT_COLUMNS, nat_rows),
        "dependency_table": table_from_rows(DEP_COLUMNS, dependency_rows),
        "family_table": table_from_rows(FAMILY_COLUMNS, family_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "nat_hash": nat_hash,
        "dependency_hash": dependency_hash,
        "family_hash": family_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": (
            obs["long_univ_input_certified"],
            obs["long_min_input_certified"],
        )
        == (1, 1),
        "naturality_fingerprint_exact": (
            obs["law_count"],
            obs["basis_law_count"],
            obs["forced_law_count"],
            obs["profunctor_controlled_law_count"],
            obs["external_input_law_count"],
            rows["nat_hash"],
        )
        == (306, 74, 232, 194, 112, NAT_TEXT_HASH),
        "dependency_graph_fingerprint_exact": (
            obs["dependency_edge_count"],
            obs["acyclic_dependency_edge_count"],
            obs["bad_dependency_edge_count"],
            obs["law_dependency_total"],
            obs["external_dependency_total"],
            obs["dependency_max"],
            rows["dependency_hash"],
        )
        == (808, 808, 0, 808, 1456, 33, DEP_TEXT_HASH),
        "family_fingerprint_exact": (
            obs["family_count"],
            obs["violation_count"],
            obs["row_sum_dependency_edge_count"],
            obs["readout_dependency_edge_count"],
            rows["family_hash"],
        )
        == (6, 0, 74, 734, FAMILY_TEXT_HASH),
        "table_shapes_match": (
            tuple(rows["nat_table"].shape),
            tuple(rows["dependency_table"].shape),
            tuple(rows["family_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (306, len(NAT_COLUMNS)),
            (808, len(DEP_COLUMNS)),
            (6, len(FAMILY_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_universal_lln_naturality_dependency_graph",
        "naturality": {
            "law_count": obs["law_count"],
            "basis_law_count": obs["basis_law_count"],
            "forced_law_count": obs["forced_law_count"],
            "profunctor_controlled_law_count": obs["profunctor_controlled_law_count"],
            "external_input_law_count": obs["external_input_law_count"],
            "text_sha256": rows["nat_hash"],
            "table_sha256": sha_array(rows["nat_table"]),
        },
        "dependency_graph": {
            "edge_count": obs["dependency_edge_count"],
            "acyclic_edge_count": obs["acyclic_dependency_edge_count"],
            "bad_edge_count": obs["bad_dependency_edge_count"],
            "law_dependency_total": obs["law_dependency_total"],
            "external_dependency_total": obs["external_dependency_total"],
            "dependency_max": obs["dependency_max"],
            "text_sha256": rows["dependency_hash"],
            "table_sha256": sha_array(rows["dependency_table"]),
        },
        "families": {
            "family_count": obs["family_count"],
            "row_sum_dependency_edge_count": obs["row_sum_dependency_edge_count"],
            "readout_dependency_edge_count": obs["readout_dependency_edge_count"],
            "violation_count": obs["violation_count"],
            "text_sha256": rows["family_hash"],
            "table_sha256": sha_array(rows["family_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    nat_payload = {
        "schema": "long.nat@1",
        "object": "finite_universal_lln_naturality_dependency_graph",
        "status": STATUS if all(checks.values()) else "LONG_NAT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.nat.report@1",
        "status": nat_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_nat certifies the finite naturality dependency graph for "
            "the long_univ laws relative to the long_min forcing basis: 306 "
            "laws are assigned to six naturality families, 808 internal "
            "dependency edges are acyclic, 194 laws remain inside the "
            "horizon-8 profunctor-controlled sector, and 112 laws are marked "
            "as horizon-extension readouts requiring convolution input beyond "
            "that profunctor overlap."
        ),
        "stage_protocol": {
            "draft": "read the certified long_univ laws and long_min forcing basis",
            "witness": "build law-family rows and explicit internal dependency edges",
            "coherence": "check input status, coverage, acyclicity, control-boundary counts, fixed hashes, and table shapes",
            "closure": "emit naturality, dependency, family, table, certificate, manifest, and report artifacts",
            "emit": "write long_nat artifacts and verifier hook",
        },
        "inputs": {
            "long_univ_report": input_entry(
                LONG_UNIV_REPORT,
                {"status": rows["input_reports"]["long_univ"].get("status")},
            ),
            "long_univ_law": input_entry(LONG_UNIV_LAW),
            "long_univ_arrow": input_entry(LONG_UNIV_ARROW),
            "long_univ_tables": input_entry(LONG_UNIV_TABLES),
            "long_min_report": input_entry(
                LONG_MIN_REPORT,
                {"status": rows["input_reports"]["long_min"].get("status")},
            ),
            "long_min_basis": input_entry(LONG_MIN_BASIS),
            "long_min_force": input_entry(LONG_MIN_FORCE),
            "long_min_tables": input_entry(LONG_MIN_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "nat": relpath(OUT_DIR / "nat.json"),
            "naturality_csv": relpath(OUT_DIR / "naturality.csv"),
            "dependency_csv": relpath(OUT_DIR / "dependency.csv"),
            "family_csv": relpath(OUT_DIR / "family.csv"),
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
                "law-to-family naturality assignment for every long_univ law",
                "explicit acyclic internal dependency graph from long_min basis and row-sum/readout laws",
                "the 194-law profunctor-controlled sector through horizon 8",
                "the 112-law horizon-extension boundary that uses long_conv input beyond profunctor overlap",
            ],
            "does_not_certify_because_out_of_scope": [
                "profunctor naturality beyond the certified horizon-8 overlap",
                "absolute minimality of the dependency graph under arbitrary algebraic rewrites",
                "an infinite-horizon LLN theorem",
                "all possible line-order maps not represented in the certified artifacts",
            ],
        },
        "next_highest_yield_item": (
            "Build long_hlim: certify whether the 112 horizon-extension laws "
            "stabilize under the same dependency grammar as the profunctor-"
            "controlled sector, or expose the exact finite obstruction to "
            "extending profunctor control past horizon eight."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.nat.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.nat.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "nat": nat_payload,
        "naturality_csv": csv_text(NAT_COLUMNS, rows["nat_rows"]),
        "dependency_csv": csv_text(DEP_COLUMNS, rows["dependency_rows"]),
        "family_csv": csv_text(FAMILY_COLUMNS, rows["family_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "nat_table": rows["nat_table"],
        "dependency_table": rows["dependency_table"],
        "family_table": rows["family_table"],
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
    write_json(OUT_DIR / "nat.json", payloads["nat"])
    (OUT_DIR / "naturality.csv").write_text(payloads["naturality_csv"], encoding="utf-8")
    (OUT_DIR / "dependency.csv").write_text(payloads["dependency_csv"], encoding="utf-8")
    (OUT_DIR / "family.csv").write_text(payloads["family_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        nat_table=payloads["nat_table"],
        dependency_table=payloads["dependency_table"],
        family_table=payloads["family_table"],
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
