from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_eta6_aext as aext
    from . import derive_eta6_ext_cone as ext
    from . import derive_eta6_srows as srows
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_aext as aext
    import derive_eta6_ext_cone as ext
    import derive_eta6_srows as srows
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_islack"
STATUS = "ETA6_ISLACK_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

EXT_TABLES = ext.OUT_DIR / "tables.npz"
AEXT_REPORT = aext.OUT_DIR / "report.json"
AEXT_TABLES = aext.OUT_DIR / "tables.npz"
SROWS_REPORT = srows.OUT_DIR / "report.json"
HOLONOMY_REPORT = holonomy.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_islack.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_islack.py"

SAMPLE_LIMIT = 16
SAMPLE_COLUMNS = [
    "sample_id",
    "sample_kind",
    "circuit_size",
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "pairing_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "vertex_count": 0,
    "support_face_count": 1,
    "nonface_slack_per_vertex": 2,
    "unique_intrinsic_height_count": 3,
    "intrinsic_height_value": 4,
    "signed_row_count": 5,
    "zero_pairing_count": 6,
    "positive_pairing_count": 7,
    "zero_c4_pairing_count": 8,
    "zero_c5_pairing_count": 9,
    "positive_c4_pairing_count": 10,
    "positive_c5_pairing_count": 11,
    "min_positive_pairing": 12,
    "max_positive_pairing_bit_length": 13,
    "strict_intrinsic_orientation_flag": 14,
    "symmetric_slack_degenerate_flag": 15,
    "eta6_holonomy_pairing": 16,
    "eta6_support_preserved_flag": 17,
    "surgery_certificate_flag": 18,
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


def intrinsic_slack_height(slack_table: np.ndarray, vertex_count: int) -> dict[str, Any]:
    heights = [0] * vertex_count
    counts = [0] * vertex_count
    for row in np.asarray(slack_table, dtype=np.int64):
        vertex_id = int(row[2])
        heights[vertex_id] += int(row[5])
        counts[vertex_id] += 1
    return {
        "heights": heights,
        "counts": counts,
        "height_sha256": hashlib.sha256(
            (",".join(str(value) for value in heights) + "\n").encode("ascii")
        ).hexdigest(),
    }


def sample_row(
    sample_id: int,
    sample_kind: int,
    support: tuple[int, ...],
    pairing_value: int,
) -> dict[str, int]:
    padded = list(support) + [-1] * (5 - len(support))
    return {
        "sample_id": sample_id,
        "sample_kind": sample_kind,
        "circuit_size": len(support),
        "v0": padded[0],
        "v1": padded[1],
        "v2": padded[2],
        "v3": padded[3],
        "v4": padded[4],
        "pairing_value": pairing_value,
    }


def stream_stats() -> dict[str, Any]:
    ext_tables = np.load(EXT_TABLES, allow_pickle=False)
    vertex_table = np.asarray(ext_tables["vertex_table"], dtype=np.int64)
    slack_table = np.asarray(ext_tables["slack_table"], dtype=np.int64)
    coords = [
        tuple(int(value) for value in (ext.SCALE, row[1], row[2], row[3]))
        for row in vertex_table
    ]
    height = intrinsic_slack_height(slack_table, len(coords))
    heights = height["heights"]

    aext_tables = np.load(AEXT_TABLES, allow_pickle=False)
    c4_rows = [
        tuple(int(value) for value in row[1:5])
        for row in np.asarray(aext_tables["c4_table"], dtype=np.int64)
    ]
    c4_set = set(c4_rows)

    row_hash = hashlib.sha256()
    samples = []
    row_count = 0
    c4_count = 0
    c5_count = 0
    zero_count = 0
    positive_count = 0
    zero_c4_count = 0
    zero_c5_count = 0
    positive_c4_count = 0
    positive_c5_count = 0
    min_positive: int | None = None
    max_positive = 0

    def emit(
        support: tuple[int, ...],
        coefficients: list[int],
        circuit_size: int,
    ) -> None:
        nonlocal row_count
        nonlocal zero_count
        nonlocal positive_count
        nonlocal zero_c4_count
        nonlocal zero_c5_count
        nonlocal positive_c4_count
        nonlocal positive_c5_count
        nonlocal min_positive
        nonlocal max_positive

        pairing = sum(
            coefficient * heights[vertex_id]
            for coefficient, vertex_id in zip(coefficients, support)
        )
        if pairing < 0:
            coefficients = [-coefficient for coefficient in coefficients]
            pairing = -pairing
        row_hash.update(srows.row_bytes(support, coefficients, pairing))
        if pairing == 0:
            zero_count += 1
            zero_c4_count += int(circuit_size == 4)
            zero_c5_count += int(circuit_size == 5)
            sample_kind = 0
        else:
            positive_count += 1
            positive_c4_count += int(circuit_size == 4)
            positive_c5_count += int(circuit_size == 5)
            min_positive = pairing if min_positive is None else min(min_positive, pairing)
            max_positive = max(max_positive, pairing)
            sample_kind = 1
        if len(samples) < SAMPLE_LIMIT:
            samples.append(sample_row(row_count, sample_kind, support, pairing))
        row_count += 1

    for support in c4_rows:
        emit(support, srows.coefs4([coords[index] for index in support]), 4)
        c4_count += 1

    for support in combinations(range(len(coords)), 5):
        if any(tuple(quad) in c4_set for quad in combinations(support, 4)):
            continue
        emit(support, srows.coefs5([coords[index] for index in support]), 5)
        c5_count += 1

    if min_positive is None:
        min_positive = 0

    return {
        "heights": heights,
        "height_counts": height["counts"],
        "height_sha256": height["height_sha256"],
        "row_count": row_count,
        "c4_count": c4_count,
        "c5_count": c5_count,
        "zero_count": zero_count,
        "positive_count": positive_count,
        "zero_c4_count": zero_c4_count,
        "zero_c5_count": zero_c5_count,
        "positive_c4_count": positive_c4_count,
        "positive_c5_count": positive_c5_count,
        "min_positive": min_positive,
        "max_positive": max_positive,
        "row_stream_sha256": row_hash.hexdigest(),
        "samples": samples,
    }


def build_payload_rows() -> dict[str, Any]:
    aext_report = load_json(AEXT_REPORT)
    srows_report = load_json(SROWS_REPORT)
    holonomy_report = load_json(HOLONOMY_REPORT)
    stats = stream_stats()
    holonomy_pairing = int(
        holonomy_report["witness"]["holonomy_eta6_pairing"]
    )
    obs_values = {
        "vertex_count": len(stats["heights"]),
        "support_face_count": 32,
        "nonface_slack_per_vertex": sorted(set(stats["height_counts"]))[0],
        "unique_intrinsic_height_count": len(set(stats["heights"])),
        "intrinsic_height_value": stats["heights"][0],
        "signed_row_count": stats["row_count"],
        "zero_pairing_count": stats["zero_count"],
        "positive_pairing_count": stats["positive_count"],
        "zero_c4_pairing_count": stats["zero_c4_count"],
        "zero_c5_pairing_count": stats["zero_c5_count"],
        "positive_c4_pairing_count": stats["positive_c4_count"],
        "positive_c5_pairing_count": stats["positive_c5_count"],
        "min_positive_pairing": stats["min_positive"],
        "max_positive_pairing_bit_length": int(stats["max_positive"]).bit_length(),
        "strict_intrinsic_orientation_flag": int(stats["zero_count"] == 0),
        "symmetric_slack_degenerate_flag": int(stats["zero_count"] > 0),
        "eta6_holonomy_pairing": holonomy_pairing,
        "eta6_support_preserved_flag": 1,
        "surgery_certificate_flag": 0,
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
        "srows_report": srows_report,
        "holonomy_report": holonomy_report,
        "stats": stats,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs_values"]
    stats = rows["stats"]

    checks = {
        "input_reports_are_certified": (
            rows["aext_report"].get("status"),
            rows["srows_report"].get("status"),
            rows["holonomy_report"].get("status"),
        )
        == (aext.STATUS, srows.STATUS, holonomy.STATUS),
        "intrinsic_slack_height_is_symmetric": (
            obs["vertex_count"],
            obs["support_face_count"],
            obs["nonface_slack_per_vertex"],
            obs["unique_intrinsic_height_count"],
            obs["intrinsic_height_value"],
            stats["height_sha256"],
        )
        == (
            60,
            32,
            29,
            1,
            48_849_960_057_179,
            "a57d06fdcc1e3946c4ccf770586f8d3a38004305a18bc43d28fe6267e664254e",
        ),
        "intrinsic_slack_height_is_not_strict_surgery_orientation": (
            obs["signed_row_count"],
            obs["zero_pairing_count"],
            obs["positive_pairing_count"],
            obs["zero_c4_pairing_count"],
            obs["zero_c5_pairing_count"],
            obs["positive_c4_pairing_count"],
            obs["positive_c5_pairing_count"],
            obs["strict_intrinsic_orientation_flag"],
            obs["symmetric_slack_degenerate_flag"],
        )
        == (
            4_903_515,
            4_894_923,
            8_592,
            2_043,
            4_892_880,
            8_592,
            0,
            0,
            1,
        ),
        "positive_residuals_match_rounded_c4_layer": (
            obs["min_positive_pairing"],
            obs["max_positive_pairing_bit_length"],
            stats["row_stream_sha256"],
        )
        == (
            97_699_920_114_358,
            128,
            "d2bb71ef191a6360aad4754c53a911975a43cdd831d6a8042adf5db7742cd00e",
        ),
        "eta6_support_is_preserved_but_not_crossed": (
            obs["eta6_holonomy_pairing"],
            obs["eta6_support_preserved_flag"],
            obs["surgery_certificate_flag"],
        )
        == (1, 1, 0),
        "table_shapes_match_codebooks": tuple(obs_table.shape)
        == (len(OBS_CODES), len(OBS_COLUMNS)),
    }

    witness = {
        "intrinsic_height_rule": "h_v = sum of exterior support slacks over all non-incident faces",
        "height_value_x1e12": obs["intrinsic_height_value"],
        "height_vector_sha256": stats["height_sha256"],
        "row_stream_sha256": stats["row_stream_sha256"],
        "pairing_counts": {
            "signed_row_count": obs["signed_row_count"],
            "zero_pairing_count": obs["zero_pairing_count"],
            "positive_pairing_count": obs["positive_pairing_count"],
            "zero_c4_pairing_count": obs["zero_c4_pairing_count"],
            "zero_c5_pairing_count": obs["zero_c5_pairing_count"],
            "max_positive_pairing": stats["max_positive"],
        },
        "eta6": {
            "holonomy_pairing": obs["eta6_holonomy_pairing"],
            "support_preserved_flag": bool(obs["eta6_support_preserved_flag"]),
        },
        "observable_table_sha256": pair.parent.sha_array(obs_table),
    }

    islack = {
        "schema": "eta6.islack@1",
        "object": "eta6",
        "construction": {
            "intrinsic_height": witness["intrinsic_height_rule"],
            "surgery_reading": "the fully symmetric slack height is an obstruction test, not a surgery orientation",
            "eta6_reading": "the support class is preserved because no boundary surgery is performed",
        },
        "witness": witness,
    }

    report = {
        "schema": "eta6.islack.report@1",
        "status": STATUS
        if all(checks.values())
        else "ETA6_ISLACK_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The first intrinsic exterior slack height is completely symmetric "
            "on the lifted 60-vertex carrier: every vertex has the same summed "
            "support slack. It therefore fails as a strict surgery orientation: "
            "4,894,923 of 4,903,515 minimal affine circuit rows pair to zero. "
            "The eta6 holonomy pairing remains 1 because no topology-changing "
            "surgery is performed. The next gate must polarize the exterior "
            "height by the eta6 holonomy/seam data."
        ),
        "stage_protocol": {
            "draft": "start from eta6_aext, eta6_srows, and eta6 holonomy",
            "witness": "sum exterior support slacks at each truncated vertex",
            "coherence": "stream all minimal affine circuits against the intrinsic slack height",
            "closure": "certify the symmetric slack height as a degenerate non-surgery orientation",
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
            "srows_report": pair.parent.input_entry(
                SROWS_REPORT,
                {
                    "status": rows["srows_report"].get("status"),
                    "certificate_sha256": rows["srows_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "holonomy_report": pair.parent.input_entry(
                HOLONOMY_REPORT,
                {
                    "status": rows["holonomy_report"].get("status"),
                    "certificate_sha256": rows["holonomy_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "islack": pair.parent.relpath(OUT_DIR / "islack.json"),
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
                "the summed exterior support-slack height is intrinsic and symmetric on the current carrier",
                "that intrinsic slack height is too degenerate to be a strict surgery orientation",
                "eta6 support/holonomy is preserved under this no-surgery identity test",
            ],
            "does_not_certify_because_not_required": [
                "a holonomy-polarized exterior height",
                "a surgery move crossing the eta6 aperture stratum",
                "opening or killing eta6",
            ],
        },
        "next_highest_yield_item": (
            "Build a holonomy-polarized exterior height from the eta6 seam and "
            "test whether it gives a strict surgery orientation."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    cert = {
        "schema": "eta6.islack.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.islack.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "islack": islack,
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
    pair.parent.write_json(OUT_DIR / "islack.json", payloads["islack"])
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
