from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_eta6_hpol as hpol
    from . import derive_eta6_repl as repl
    from . import derive_eta6_srows as srows
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_hpol as hpol
    import derive_eta6_repl as repl
    import derive_eta6_srows as srows
    from paths import D20_INVARIANTS, ROOT


pair = hpol.pair

THEOREM_ID = "eta6_gap"
STATUS = "ETA6_GAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

HPOL_REPORT = hpol.OUT_DIR / "report.json"
REPL_REPORT = repl.OUT_DIR / "report.json"
REPL_TABLES = repl.OUT_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_gap.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_gap.py"

SAMPLE_LIMIT = 16
EXPECTED_HPOL_MIN_COUNT = 2

MARG_COLUMNS = [
    "carrier_id",
    "carrier_code",
    "row_count",
    "zero_count",
    "positive_count",
    "min_margin",
    "min_count",
    "strict_flag",
]
SAMPLE_COLUMNS = [
    "sample_id",
    "row_id",
    "circuit_size",
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "margin_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "hpol_row_count": 0,
    "hpol_zero_count": 1,
    "hpol_positive_count": 2,
    "hpol_min_margin": 3,
    "hpol_min_count": 4,
    "hpol_min_c4_count": 5,
    "hpol_min_c5_count": 6,
    "hpol_max_margin_bit_length": 7,
    "hpol_row_hash_match_flag": 8,
    "hpol_gap_positive_flag": 9,
    "no_positive_annihilator_flag": 10,
    "repl_row_count": 11,
    "repl_zero_count": 12,
    "repl_positive_count": 13,
    "repl_min_margin": 14,
    "repl_gap_positive_flag": 15,
    "repl_row_hash_match_flag": 16,
    "checked_carrier_count": 17,
    "universal_completion_claim_flag": 18,
    "current_replacement_stability_flag": 19,
}


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def sample_row(
    sample_id: int,
    row_id: int,
    support: tuple[int, ...],
    margin: int,
) -> dict[str, int]:
    padded = list(support) + [-1] * (5 - len(support))
    return {
        "sample_id": sample_id,
        "row_id": row_id,
        "circuit_size": len(support),
        "v0": padded[0],
        "v1": padded[1],
        "v2": padded[2],
        "v3": padded[3],
        "v4": padded[4],
        "margin_value": margin,
    }


def hpol_margin_stats() -> dict[str, Any]:
    face_rows = hpol.face_weight_rows()
    face_weights = [row["weight"] for row in face_rows]

    ext_tables = np.load(hpol.EXT_TABLES, allow_pickle=False)
    vertex_table = np.asarray(ext_tables["vertex_table"], dtype=np.int64)
    slack_table = np.asarray(ext_tables["slack_table"], dtype=np.int64)
    coords = [
        tuple(int(value) for value in (hpol.ext.SCALE, row[1], row[2], row[3]))
        for row in vertex_table
    ]
    heights = hpol.hpol_height(slack_table, face_weights, len(coords))

    aext_tables = np.load(hpol.AEXT_TABLES, allow_pickle=False)
    c4_rows = [
        tuple(int(value) for value in row[1:5])
        for row in np.asarray(aext_tables["c4_table"], dtype=np.int64)
    ]
    c4_set = set(c4_rows)

    row_hash = hashlib.sha256()
    row_count = 0
    zero_count = 0
    positive_count = 0
    min_margin: int | None = None
    min_count = 0
    min_c4_count = 0
    min_c5_count = 0
    max_margin = 0
    samples: list[dict[str, int]] = []

    def emit(
        support: tuple[int, ...],
        coefficients: list[int],
        circuit_size: int,
    ) -> None:
        nonlocal row_count
        nonlocal zero_count
        nonlocal positive_count
        nonlocal min_margin
        nonlocal min_count
        nonlocal min_c4_count
        nonlocal min_c5_count
        nonlocal max_margin
        nonlocal samples

        margin = sum(
            coefficient * heights[vertex_id]
            for coefficient, vertex_id in zip(coefficients, support)
        )
        if margin < 0:
            coefficients = [-coefficient for coefficient in coefficients]
            margin = -margin
        row_hash.update(srows.row_bytes(support, coefficients, margin))
        if margin == 0:
            zero_count += 1
        else:
            positive_count += 1
            max_margin = max(max_margin, margin)
            if min_margin is None or margin < min_margin:
                min_margin = margin
                min_count = 1
                min_c4_count = int(circuit_size == 4)
                min_c5_count = int(circuit_size == 5)
                samples = [sample_row(0, row_count, support, margin)]
            elif margin == min_margin:
                min_count += 1
                min_c4_count += int(circuit_size == 4)
                min_c5_count += int(circuit_size == 5)
                if len(samples) < SAMPLE_LIMIT:
                    samples.append(
                        sample_row(len(samples), row_count, support, margin)
                    )
        row_count += 1

    for support in c4_rows:
        emit(support, srows.coefs4([coords[index] for index in support]), 4)

    c5_count = 0
    for support in combinations(range(len(coords)), 5):
        if any(tuple(quad) in c4_set for quad in combinations(support, 4)):
            continue
        emit(support, srows.coefs5([coords[index] for index in support]), 5)
        c5_count += 1

    if min_margin is None:
        min_margin = 0

    return {
        "row_count": row_count,
        "c4_count": len(c4_rows),
        "c5_count": c5_count,
        "zero_count": zero_count,
        "positive_count": positive_count,
        "min_margin": min_margin,
        "min_count": min_count,
        "min_c4_count": min_c4_count,
        "min_c5_count": min_c5_count,
        "max_margin": max_margin,
        "row_stream_sha256": row_hash.hexdigest(),
        "samples": samples,
    }


def repl_obs_values() -> dict[str, int]:
    tables = np.load(REPL_TABLES, allow_pickle=False)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    obs_by_code = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, repl.OBS_COLUMNS)
    }
    return {name: int(obs_by_code[code]) for name, code in repl.OBS_CODES.items()}


def build_payload_rows() -> dict[str, Any]:
    hpol_report = load_json(HPOL_REPORT)
    repl_report = load_json(REPL_REPORT)
    hstats = hpol_margin_stats()
    robs = repl_obs_values()
    hpol_hash_match = int(
        hstats["row_stream_sha256"]
        == hpol_report.get("witness", {}).get("row_stream_sha256")
    )
    repl_hash_match = int(
        repl_report.get("witness", {})
        .get("circuits", {})
        .get("row_stream_sha256")
        == "58a495540af510f0ef52e8d730ffbf58d42c07725971dff463364f67d79e118c"
    )
    obs_values = {
        "hpol_row_count": hstats["row_count"],
        "hpol_zero_count": hstats["zero_count"],
        "hpol_positive_count": hstats["positive_count"],
        "hpol_min_margin": hstats["min_margin"],
        "hpol_min_count": hstats["min_count"],
        "hpol_min_c4_count": hstats["min_c4_count"],
        "hpol_min_c5_count": hstats["min_c5_count"],
        "hpol_max_margin_bit_length": hstats["max_margin"].bit_length(),
        "hpol_row_hash_match_flag": hpol_hash_match,
        "hpol_gap_positive_flag": int(hstats["min_margin"] > 0),
        "no_positive_annihilator_flag": int(
            hstats["zero_count"] == 0 and hstats["min_margin"] > 0
        ),
        "repl_row_count": robs["signed_row_count"],
        "repl_zero_count": robs["zero_pairing_count"],
        "repl_positive_count": robs["positive_pairing_count"],
        "repl_min_margin": robs["min_positive_pairing"],
        "repl_gap_positive_flag": int(robs["min_positive_pairing"] > 0),
        "repl_row_hash_match_flag": repl_hash_match,
        "checked_carrier_count": 2,
        "universal_completion_claim_flag": 0,
        "current_replacement_stability_flag": int(
            hstats["min_margin"] > 0 and robs["min_positive_pairing"] > 0
        ),
    }
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": int(obs_values[name]),
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    marg_rows = [
        {
            "carrier_id": 0,
            "carrier_code": 0,
            "row_count": hstats["row_count"],
            "zero_count": hstats["zero_count"],
            "positive_count": hstats["positive_count"],
            "min_margin": hstats["min_margin"],
            "min_count": hstats["min_count"],
            "strict_flag": int(hstats["zero_count"] == 0),
        },
        {
            "carrier_id": 1,
            "carrier_code": 1,
            "row_count": robs["signed_row_count"],
            "zero_count": robs["zero_pairing_count"],
            "positive_count": robs["positive_pairing_count"],
            "min_margin": robs["min_positive_pairing"],
            "min_count": -1,
            "strict_flag": int(robs["zero_pairing_count"] == 0),
        },
    ]
    return {
        "hpol_report": hpol_report,
        "repl_report": repl_report,
        "hstats": hstats,
        "robs": robs,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
        "marg_rows": marg_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    marg_table = table_from_rows(MARG_COLUMNS, rows["marg_rows"])
    sample_table = table_from_rows(SAMPLE_COLUMNS, rows["hstats"]["samples"])
    obs = rows["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["hpol_report"].get("all_checks_pass") is True
            and rows["repl_report"].get("all_checks_pass") is True
        ),
        "hpol_margin_stream_matches_certified_universe": (
            obs["hpol_row_count"],
            obs["hpol_zero_count"],
            obs["hpol_positive_count"],
            obs["hpol_min_margin"],
            obs["hpol_max_margin_bit_length"],
            obs["hpol_row_hash_match_flag"],
            rows["hstats"]["row_stream_sha256"],
        )
        == (
            4_903_515,
            0,
            4_903_515,
            1,
            136,
            1,
            "70a6216673205d9ed0e3df7a67fa9a61f05ea9343246cf06355b9d764eca72f0",
        ),
        "hpol_min_margin_count_is_exact_stream_count": (
            obs["hpol_min_count"] == EXPECTED_HPOL_MIN_COUNT
            and obs["hpol_min_count"]
            == obs["hpol_min_c4_count"] + obs["hpol_min_c5_count"]
            and tuple(sample_table.shape)
            == (min(SAMPLE_LIMIT, EXPECTED_HPOL_MIN_COUNT), len(SAMPLE_COLUMNS))
        ),
        "strict_positive_functional_blocks_positive_annihilator": (
            obs["hpol_gap_positive_flag"],
            obs["no_positive_annihilator_flag"],
        )
        == (1, 1),
        "replacement_gap_imported_from_certified_carrier": (
            obs["repl_row_count"],
            obs["repl_zero_count"],
            obs["repl_positive_count"],
            obs["repl_min_margin"],
            obs["repl_row_hash_match_flag"],
        )
        == (2_831_367, 0, 2_831_367, 146, 1),
        "claim_boundary_is_explicit": (
            obs["checked_carrier_count"],
            obs["current_replacement_stability_flag"],
            obs["universal_completion_claim_flag"],
        )
        == (2, 1, 0),
        "table_shapes_match_codebooks": (
            tuple(obs_table.shape),
            tuple(marg_table.shape),
            tuple(sample_table.shape),
        )
        == (
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (2, len(MARG_COLUMNS)),
            (min(SAMPLE_LIMIT, EXPECTED_HPOL_MIN_COUNT), len(SAMPLE_COLUMNS)),
        ),
    }
    witness = {
        "hpol": {
            "row_count": obs["hpol_row_count"],
            "zero_count": obs["hpol_zero_count"],
            "positive_count": obs["hpol_positive_count"],
            "min_margin": obs["hpol_min_margin"],
            "min_margin_count": obs["hpol_min_count"],
            "min_c4_count": obs["hpol_min_c4_count"],
            "min_c5_count": obs["hpol_min_c5_count"],
            "max_margin": rows["hstats"]["max_margin"],
            "row_stream_sha256": rows["hstats"]["row_stream_sha256"],
        },
        "repl": {
            "row_count": obs["repl_row_count"],
            "zero_count": obs["repl_zero_count"],
            "positive_count": obs["repl_positive_count"],
            "min_margin": obs["repl_min_margin"],
            "row_stream_sha256": rows["repl_report"]
            .get("witness", {})
            .get("circuits", {})
            .get("row_stream_sha256"),
        },
        "gordan_reading": (
            "If every signed row r has r(h) >= m > 0, then no nonzero "
            "nonnegative combination of the rows can annihilate: evaluating "
            "the combination on h gives a strictly positive number."
        ),
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "margin_table_sha256": pair.parent.sha_array(marg_table),
        "sample_table_sha256": pair.parent.sha_array(sample_table),
    }
    gap = {
        "schema": "eta6.gap@1",
        "object": "eta6",
        "construction": {
            "name": "gap",
            "reading": (
                "the holonomy-polarized height is a strict positive functional "
                "on the full current signed-row universe"
            ),
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.gap.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_GAP_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The current eta6 row universe has an exact positive integer gap: "
            "all 4,903,515 hpol-oriented rows pair with margin at least 1, "
            "and the minimum is attained by the streamed witnesses recorded "
            "in samp.csv. By the same Gordan-dual evaluation test, this rules "
            "out a nonzero positive annihilating dependence for the current "
            "signed-row matrix. The already-certified face-31 replacement "
            "carrier also has a positive imported margin, 146. This certifies "
            "gap protection on the checked carriers, not every future "
            "completion."
        ),
        "stage_protocol": {
            "draft": "start from eta6_hpol and eta6_repl",
            "witness": "stream every hpol signed row and count exact minimum-margin hits",
            "coherence": "compare hpol stream hash and imported replacement gap",
            "closure": "certify positive Gordan functional for the current row universe",
            "emit": "emit compact gap artifacts, verifier command, and next seam",
        },
        "inputs": {
            "hpol_report": pair.parent.input_entry(
                HPOL_REPORT,
                {
                    "status": rows["hpol_report"].get("status"),
                    "certificate_sha256": rows["hpol_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "repl_report": pair.parent.input_entry(
                REPL_REPORT,
                {
                    "status": rows["repl_report"].get("status"),
                    "certificate_sha256": rows["repl_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "repl_tables": pair.parent.input_entry(REPL_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "gap": pair.parent.relpath(OUT_DIR / "gap.json"),
            "marg_csv": pair.parent.relpath(OUT_DIR / "marg.csv"),
            "samp_csv": pair.parent.relpath(OUT_DIR / "samp.csv"),
            "obs_csv": pair.parent.relpath(OUT_DIR / "obs.csv"),
            "tables": pair.parent.relpath(OUT_DIR / "tables.npz"),
            "certificate": pair.parent.relpath(OUT_DIR / "cert.json"),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exact current hpol margin m = 1",
                "exact count of current hpol rows attaining the minimum margin",
                "Gordan-dual exclusion of positive annihilating dependence for the current signed-row matrix",
                "positive imported gap on the already-certified face-31 replacement carrier",
            ],
            "does_not_certify_because_not_required": [
                "all future replacement completions",
                "C985 associator closure on a modified carrier",
                "that eta6 is globally uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "Build the multi-face patch for the second hit and test whether its "
            "row universe also has a positive eta6 gap."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.gap.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.gap.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "gap": gap,
        "marg_csv": csv_text(MARG_COLUMNS, rows["marg_rows"]),
        "samp_csv": csv_text(SAMPLE_COLUMNS, rows["hstats"]["samples"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "marg_table": marg_table,
        "sample_table": sample_table,
        "obs_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = hpol.ext.nonholonomic.preservation.INDEX_PATH
    if index_path.exists():
        index_payload = load_json(index_path)
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(index_path, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(OUT_DIR / "gap.json", payloads["gap"])
    (OUT_DIR / "marg.csv").write_text(payloads["marg_csv"], encoding="utf-8")
    (OUT_DIR / "samp.csv").write_text(payloads["samp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        margin_table=payloads["marg_table"],
        sample_table=payloads["sample_table"],
        observable_table=payloads["obs_table"],
    )
    pair.parent.write_json(OUT_DIR / "cert.json", payloads["cert"])
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
