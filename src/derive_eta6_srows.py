from __future__ import annotations

import hashlib
import json
from itertools import combinations
from math import gcd
from typing import Any

import numpy as np

try:
    from . import derive_eta6_aext as aext
    from . import derive_eta6_ext_cone as ext
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_aext as aext
    import derive_eta6_ext_cone as ext
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_srows"
STATUS = "ETA6_SROWS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

AEXT_REPORT = aext.OUT_DIR / "report.json"
AEXT_TABLES = aext.OUT_DIR / "tables.npz"
EXT_TABLES = ext.OUT_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_srows.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_srows.py"

SAMPLE_LIMIT = 24
SAMPLE_COLUMNS = [
    "sample_id",
    "circuit_size",
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "c0",
    "c1",
    "c2",
    "c3",
    "c4",
    "height_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "signed_row_count": 0,
    "signed_c4_row_count": 1,
    "signed_c5_row_count": 2,
    "positive_height_row_count": 3,
    "zero_height_row_count": 4,
    "min_height_value_bit_length": 5,
    "max_height_value_bit_length": 6,
    "max_abs_coefficient_bit_length": 7,
    "positive_coefficient_count": 8,
    "negative_coefficient_count": 9,
    "height_vector_dimension": 10,
    "height_min_value": 11,
    "height_max_value": 12,
    "full_signed_circuit_gordan_flag": 13,
    "intrinsic_surgery_orientation_flag": 14,
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


def height_vector(count: int) -> list[int]:
    return [
        (index + 1) ** 3
        + 17 * (index + 1) ** 2
        + 31 * (index + 1)
        + 7
        for index in range(count)
    ]


def det3(a: tuple[int, int, int], b: tuple[int, int, int], c: tuple[int, int, int]) -> int:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def det4_cols(cols: list[tuple[int, int, int, int]]) -> int:
    p0 = cols[0][1:]
    a = (
        cols[1][1] - p0[0],
        cols[1][2] - p0[1],
        cols[1][3] - p0[2],
    )
    b = (
        cols[2][1] - p0[0],
        cols[2][2] - p0[1],
        cols[2][3] - p0[2],
    )
    c = (
        cols[3][1] - p0[0],
        cols[3][2] - p0[1],
        cols[3][3] - p0[2],
    )
    return cols[0][0] * det3(a, b, c)


def gcd_list(values: list[int]) -> int:
    result = 0
    for value in values:
        result = gcd(result, abs(value))
    return result


def normalize(coefficients: list[int]) -> list[int]:
    divisor = gcd_list(coefficients)
    normalized = [value // divisor for value in coefficients]
    first = next(value for value in normalized if value)
    if first < 0:
        normalized = [-value for value in normalized]
    return normalized


def coefs5(cols: list[tuple[int, int, int, int]]) -> list[int]:
    coefficients = []
    for index in range(5):
        subcols = [cols[subindex] for subindex in range(5) if subindex != index]
        value = det4_cols(subcols)
        if index % 2:
            value = -value
        coefficients.append(value)
    return normalize(coefficients)


def det3_matrix(rows: list[list[int]], indices: list[int]) -> int:
    a = (rows[0][indices[0]], rows[0][indices[1]], rows[0][indices[2]])
    b = (rows[1][indices[0]], rows[1][indices[1]], rows[1][indices[2]])
    c = (rows[2][indices[0]], rows[2][indices[1]], rows[2][indices[2]])
    return det3(a, b, c)


def coefs4(cols: list[tuple[int, int, int, int]]) -> list[int]:
    rows = [[cols[column][row] for column in range(4)] for row in range(4)]
    for removed_row in range(4):
        subrows = [rows[row] for row in range(4) if row != removed_row]
        coefficients = []
        for column in range(4):
            indices = [index for index in range(4) if index != column]
            value = det3_matrix(subrows, indices)
            if (removed_row + column) % 2:
                value = -value
            coefficients.append(value)
        if any(coefficients):
            return normalize(coefficients)
    raise ValueError("zero affine circuit coefficients")


def row_bytes(
    support: tuple[int, ...],
    coefficients: list[int],
    height_value: int,
) -> bytes:
    return (
        ",".join(str(vertex_id) for vertex_id in support)
        + "|"
        + ",".join(str(coefficient) for coefficient in coefficients)
        + "|"
        + str(height_value)
        + "\n"
    ).encode("ascii")


def support_bytes(support: tuple[int, ...]) -> bytes:
    return (",".join(str(vertex_id) for vertex_id in support) + "\n").encode("ascii")


def sample_row(
    sample_id: int,
    support: tuple[int, ...],
    coefficients: list[int],
    height_value: int,
) -> dict[str, Any]:
    padded_vertices = list(support) + [-1] * (5 - len(support))
    padded_coefficients = coefficients + [0] * (5 - len(coefficients))
    row: dict[str, Any] = {
        "sample_id": sample_id,
        "circuit_size": len(support),
        "height_value": height_value,
    }
    for index, vertex_id in enumerate(padded_vertices):
        row[f"v{index}"] = vertex_id
    for index, coefficient in enumerate(padded_coefficients):
        row[f"c{index}"] = coefficient
    return row


def signed_row_stats() -> dict[str, Any]:
    ext_tables = np.load(EXT_TABLES, allow_pickle=False)
    vertex_table = np.asarray(ext_tables["vertex_table"], dtype=np.int64)
    coords = [
        tuple(int(value) for value in (ext.SCALE, row[1], row[2], row[3]))
        for row in vertex_table
    ]
    heights = height_vector(len(coords))

    aext_tables = np.load(AEXT_TABLES, allow_pickle=False)
    c4_rows = [
        tuple(int(value) for value in row[1:5])
        for row in np.asarray(aext_tables["c4_table"], dtype=np.int64)
    ]
    c4_set = set(c4_rows)

    row_hash = hashlib.sha256()
    support_hash = hashlib.sha256()
    height_hash = hashlib.sha256(
        (",".join(str(value) for value in heights) + "\n").encode("ascii")
    ).hexdigest()

    samples = []
    row_count = 0
    c4_count = 0
    c5_count = 0
    zero_height_count = 0
    positive_height_count = 0
    min_height_value: int | None = None
    max_height_value = 0
    max_abs_coefficient = 0
    positive_coefficient_count = 0
    negative_coefficient_count = 0

    def emit_row(support: tuple[int, ...], coefficients: list[int]) -> None:
        nonlocal row_count
        nonlocal zero_height_count
        nonlocal positive_height_count
        nonlocal min_height_value
        nonlocal max_height_value
        nonlocal max_abs_coefficient
        nonlocal positive_coefficient_count
        nonlocal negative_coefficient_count

        height_value = sum(
            coefficient * heights[vertex_id]
            for coefficient, vertex_id in zip(coefficients, support)
        )
        if height_value < 0:
            coefficients = [-coefficient for coefficient in coefficients]
            height_value = -height_value
        if height_value == 0:
            zero_height_count += 1
        else:
            positive_height_count += 1

        row_hash.update(row_bytes(support, coefficients, height_value))
        support_hash.update(support_bytes(support))
        min_height_value = (
            height_value
            if min_height_value is None
            else min(min_height_value, height_value)
        )
        max_height_value = max(max_height_value, height_value)
        max_abs_coefficient = max(
            max_abs_coefficient,
            max(abs(coefficient) for coefficient in coefficients),
        )
        positive_coefficient_count += sum(1 for coefficient in coefficients if coefficient > 0)
        negative_coefficient_count += sum(1 for coefficient in coefficients if coefficient < 0)
        if len(samples) < SAMPLE_LIMIT:
            samples.append(
                sample_row(row_count, support, coefficients, height_value)
            )
        row_count += 1

    for support in c4_rows:
        emit_row(support, coefs4([coords[index] for index in support]))
        c4_count += 1

    for support in combinations(range(len(coords)), 5):
        if any(tuple(quad) in c4_set for quad in combinations(support, 4)):
            continue
        emit_row(support, coefs5([coords[index] for index in support]))
        c5_count += 1

    if min_height_value is None:
        raise ValueError("no signed rows were emitted")

    return {
        "height_vector": heights,
        "row_count": row_count,
        "c4_count": c4_count,
        "c5_count": c5_count,
        "zero_height_count": zero_height_count,
        "positive_height_count": positive_height_count,
        "min_height_value": min_height_value,
        "max_height_value": max_height_value,
        "max_abs_coefficient": max_abs_coefficient,
        "positive_coefficient_count": positive_coefficient_count,
        "negative_coefficient_count": negative_coefficient_count,
        "row_stream_sha256": row_hash.hexdigest(),
        "support_stream_sha256": support_hash.hexdigest(),
        "height_vector_sha256": height_hash,
        "samples": samples,
    }


def build_payload_rows() -> dict[str, Any]:
    aext_report = load_json(AEXT_REPORT)
    stats = signed_row_stats()
    obs_values = {
        "signed_row_count": stats["row_count"],
        "signed_c4_row_count": stats["c4_count"],
        "signed_c5_row_count": stats["c5_count"],
        "positive_height_row_count": stats["positive_height_count"],
        "zero_height_row_count": stats["zero_height_count"],
        "min_height_value_bit_length": int(stats["min_height_value"]).bit_length(),
        "max_height_value_bit_length": int(stats["max_height_value"]).bit_length(),
        "max_abs_coefficient_bit_length": int(
            stats["max_abs_coefficient"]
        ).bit_length(),
        "positive_coefficient_count": stats["positive_coefficient_count"],
        "negative_coefficient_count": stats["negative_coefficient_count"],
        "height_vector_dimension": len(stats["height_vector"]),
        "height_min_value": min(stats["height_vector"]),
        "height_max_value": max(stats["height_vector"]),
        "full_signed_circuit_gordan_flag": int(stats["zero_height_count"] == 0),
        "intrinsic_surgery_orientation_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": row_id,
            "observable_code": code,
            "value": int(obs_values[key]),
            "scale_code": 0,
        }
        for row_id, (key, code) in enumerate(OBS_CODES.items())
    ]
    return {
        "aext_report": aext_report,
        "stats": stats,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    stats = rows["stats"]
    obs = rows["obs_values"]

    checks = {
        "aext_input_is_certified": rows["aext_report"].get("status") == aext.STATUS,
        "all_minimal_circuits_are_oriented": (
            obs["signed_row_count"],
            obs["signed_c4_row_count"],
            obs["signed_c5_row_count"],
        )
        == (4_903_515, 10_635, 4_892_880),
        "height_orientation_is_strict": (
            obs["positive_height_row_count"],
            obs["zero_height_row_count"],
            obs["min_height_value_bit_length"],
            obs["max_height_value_bit_length"],
            obs["max_abs_coefficient_bit_length"],
            obs["full_signed_circuit_gordan_flag"],
        )
        == (4_903_515, 0, 8, 141, 123, 1),
        "stream_hashes_match_reference": (
            stats["row_stream_sha256"],
            stats["support_stream_sha256"],
            stats["height_vector_sha256"],
        )
        == (
            "2d4f17d00b4e1408d408e275eabd2c7095641b0544ece528729d86b83c238e84",
            "16a3ba24aef7c4b02f306601dd45438ccda18f0257a125a3cc98acd4e523639e",
            "3287f972a5b170b1b98212122fc9c71076b80af61ebe55a9ada1027e68190399",
        ),
        "closure_boundary_is_not_overclaimed": obs[
            "intrinsic_surgery_orientation_flag"
        ]
        == 0,
        "table_shapes_match_codebooks": tuple(obs_table.shape)
        == (len(OBS_CODES), len(OBS_COLUMNS)),
    }

    witness = {
        "height_rule": "h_i = (i+1)^3 + 17(i+1)^2 + 31(i+1) + 7",
        "height_vector_sha256": stats["height_vector_sha256"],
        "row_stream_sha256": stats["row_stream_sha256"],
        "support_stream_sha256": stats["support_stream_sha256"],
        "signed_rows": {
            "row_count": stats["row_count"],
            "size4_count": stats["c4_count"],
            "size5_count": stats["c5_count"],
            "positive_height_row_count": stats["positive_height_count"],
            "zero_height_row_count": stats["zero_height_count"],
            "min_height_value": stats["min_height_value"],
            "max_height_value": stats["max_height_value"],
            "max_abs_coefficient": stats["max_abs_coefficient"],
            "positive_coefficient_count": stats["positive_coefficient_count"],
            "negative_coefficient_count": stats["negative_coefficient_count"],
        },
        "observable_table_sha256": pair.parent.sha_array(obs_table),
    }

    srows = {
        "schema": "eta6.srows@1",
        "object": "eta6",
        "construction": {
            "circuit_matrix": "height-oriented primitive affine dependence rows for every minimal circuit",
            "orientation": "choose the sign of each primitive row so its dot product with h is positive",
            "gordan_vector": "the deterministic 60-coordinate height vector h",
        },
        "witness": witness,
    }

    report = {
        "schema": "eta6.srows.report@1",
        "status": STATUS
        if all(checks.values())
        else "ETA6_SROWS_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "All 4,903,515 minimal affine circuits of the rounded eta6 "
            "60-vertex carrier now have deterministic signed height rows. Each "
            "primitive circuit row is oriented so its pairing with the fixed "
            "height vector h_i=(i+1)^3+17(i+1)^2+31(i+1)+7 is strictly "
            "positive; the minimum pairing is 146. By Gordan's alternative, "
            "this height-oriented full circuit matrix has no nonzero "
            "nonnegative dependence annihilating it. The intrinsic exterior "
            "surgery orientation remains a separate gate."
        ),
        "stage_protocol": {
            "draft": "start from eta6_aext circuit census",
            "witness": "stream primitive signed rows for every size-4 and size-5 minimal affine circuit",
            "coherence": "check every row pairs strictly positively with the deterministic height vector",
            "closure": "apply Gordan to the height-oriented full circuit matrix",
            "emit": "emit stream hashes, samples, observables, cert, report, verifier command, and next target",
        },
        "inputs": {
            "aext_report": pair.parent.input_entry(
                AEXT_REPORT,
                {
                    "status": rows["aext_report"].get("status"),
                    "certificate_sha256": rows["aext_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "aext_tables": pair.parent.input_entry(AEXT_TABLES),
            "ext_tables": pair.parent.input_entry(EXT_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "srows": pair.parent.relpath(OUT_DIR / "srows.json"),
            "samples_csv": pair.parent.relpath(OUT_DIR / "samp.csv"),
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
                "all 4,903,515 minimal affine circuits have deterministic signed rows",
                "the fixed height vector pairs strictly positively with every signed row",
                "Gordan-dual infeasibility for the height-oriented full circuit matrix",
            ],
            "does_not_certify_because_not_required": [
                "that this chosen height orientation is the intrinsic surgery orientation",
                "a surgery move crossing the eta6 aperture stratum",
            ],
        },
        "next_highest_yield_item": (
            "Replace the chosen height orientation with an intrinsic exterior "
            "surgery orientation and test whether it preserves eta6."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    cert = {
        "schema": "eta6.srows.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.srows.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "srows": srows,
        "samples_csv": csv_text(SAMPLE_COLUMNS, rows["stats"]["samples"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "observable_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = ext.nonholonomic.preservation.INDEX_PATH
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
    pair.parent.write_json(OUT_DIR / "srows.json", payloads["srows"])
    (OUT_DIR / "samp.csv").write_text(payloads["samples_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        observable_table=payloads["observable_table"],
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
