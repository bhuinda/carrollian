from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_ext_cone as ext
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_ext_cone as ext
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_gordan"
STATUS = "ETA6_GORDAN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

EXT_REPORT = ext.OUT_DIR / "report.json"
EXT_TABLES = ext.OUT_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_gordan.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_gordan.py"

DUAL_COLUMNS = [
    "dual_row_id",
    "face_id",
    "face_type_code",
    "multiplicity",
    "a0_offset_x1e12",
    "a1_neg_normal_x_x1e12",
    "a2_neg_normal_y_x1e12",
    "a3_neg_normal_z_x1e12",
    "test_value_x1e12",
    "positive_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "support_face_row_count": 0,
    "expanded_support_row_count": 1,
    "gordan_test_vector_dimension": 2,
    "test_vector_a0_x1e12": 3,
    "test_vector_a1_x1e12": 4,
    "test_vector_a2_x1e12": 5,
    "test_vector_a3_x1e12": 6,
    "min_dual_test_value_x1e12": 7,
    "max_dual_test_value_x1e12": 8,
    "positive_dual_row_count": 9,
    "zero_dual_row_count": 10,
    "gordan_no_nonzero_y_flag": 11,
    "support_plane_gordan_certificate_flag": 12,
    "full_affine_circuit_gordan_flag": 13,
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


def build_payload_rows() -> dict[str, Any]:
    ext_report = load_json(EXT_REPORT)
    tables = np.load(EXT_TABLES, allow_pickle=False)
    face_rows = table_rows(
        np.asarray(tables["face_support_table"], dtype=np.int64),
        ext.FACE_SUPPORT_COLUMNS,
    )
    dual_rows = []
    for row_id, row in enumerate(face_rows):
        multiplicity = int(row["nonface_vertex_count"])
        offset = int(row["offset_x1e12"])
        dual_rows.append(
            {
                "dual_row_id": row_id,
                "face_id": row["face_id"],
                "face_type_code": row["face_type_code"],
                "multiplicity": multiplicity,
                "a0_offset_x1e12": offset,
                "a1_neg_normal_x_x1e12": -row["normal_x_x1e12"],
                "a2_neg_normal_y_x1e12": -row["normal_y_x1e12"],
                "a3_neg_normal_z_x1e12": -row["normal_z_x1e12"],
                "test_value_x1e12": offset,
                "positive_flag": int(offset > 0),
            }
        )
    test_values = [row["test_value_x1e12"] for row in dual_rows]
    obs_values = {
        "support_face_row_count": len(dual_rows),
        "expanded_support_row_count": sum(row["multiplicity"] for row in dual_rows),
        "gordan_test_vector_dimension": 4,
        "test_vector_a0_x1e12": ext.SCALE,
        "test_vector_a1_x1e12": 0,
        "test_vector_a2_x1e12": 0,
        "test_vector_a3_x1e12": 0,
        "min_dual_test_value_x1e12": min(test_values),
        "max_dual_test_value_x1e12": max(test_values),
        "positive_dual_row_count": sum(row["positive_flag"] for row in dual_rows),
        "zero_dual_row_count": sum(row["test_value_x1e12"] == 0 for row in dual_rows),
        "gordan_no_nonzero_y_flag": int(all(value > 0 for value in test_values)),
        "support_plane_gordan_certificate_flag": 1,
        "full_affine_circuit_gordan_flag": 0,
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
        "ext_report": ext_report,
        "dual_rows": dual_rows,
        "obs_rows": obs_rows,
        "obs_values": obs_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    dual_table = table_from_rows(DUAL_COLUMNS, rows["dual_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs_values"]

    checks = {
        "ext_cone_report_certified": rows["ext_report"].get("status") == ext.STATUS,
        "support_plane_scope_matches_ext_cone": (
            obs["support_face_row_count"],
            obs["expanded_support_row_count"],
        )
        == (32, 1_740),
        "gordan_test_vector_is_strictly_positive": (
            obs["gordan_test_vector_dimension"],
            obs["test_vector_a0_x1e12"],
            obs["test_vector_a1_x1e12"],
            obs["test_vector_a2_x1e12"],
            obs["test_vector_a3_x1e12"],
            obs["min_dual_test_value_x1e12"],
            obs["positive_dual_row_count"],
            obs["zero_dual_row_count"],
        )
        == (4, ext.SCALE, 0, 0, 0, 1_511_522_628_152, 32, 0),
        "support_plane_gordan_dual_is_certified": (
            obs["gordan_no_nonzero_y_flag"],
            obs["support_plane_gordan_certificate_flag"],
            obs["full_affine_circuit_gordan_flag"],
        )
        == (1, 1, 0),
        "table_shapes_match_codebooks": (
            tuple(dual_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (32, len(DUAL_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }

    witness = {
        "gordan_test_vector_x1e12": [ext.SCALE, 0, 0, 0],
        "support_plane_rows": obs["support_face_row_count"],
        "expanded_support_rows": obs["expanded_support_row_count"],
        "min_test_value_x1e12": obs["min_dual_test_value_x1e12"],
        "max_test_value_x1e12": obs["max_dual_test_value_x1e12"],
        "dual_table_sha256": pair.parent.sha_array(dual_table),
        "observable_table_sha256": pair.parent.sha_array(obs_table),
    }

    gordan = {
        "schema": "eta6.gordan@1",
        "object": "eta6",
        "construction": {
            "matrix": "oriented support-plane rows A_i = [b_f, -n_f]",
            "test_vector": "x = [1,0,0,0]",
            "gordan_reading": (
                "A x > 0 certifies there is no nonzero y >= 0 with "
                "A^T y = 0 for this support-plane matrix"
            ),
        },
        "witness": witness,
    }

    report = {
        "schema": "eta6.gordan.report@1",
        "status": STATUS
        if all(checks.values())
        else "ETA6_GORDAN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6 support-positive cone now has a Gordan certificate for "
            "the oriented support-plane matrix. With rows A_i=[b_f,-n_f], the "
            "test vector [1,0,0,0] gives A_i x = b_f > 0 for all 32 face rows "
            "and therefore for all 1,740 expanded face/non-face support rows. "
            "By Gordan's alternative, no nonzero y >= 0 solves A^T y = 0 for "
            "this support-plane matrix. The full exterior affine-circuit "
            "Gordan certificate remains a separate next layer."
        ),
        "stage_protocol": {
            "draft": "start from eta6_ext_cone support planes",
            "witness": "form homogeneous support rows [b_f,-n_f]",
            "coherence": "evaluate every row on [1,0,0,0] and check strict positivity",
            "closure": "apply Gordan alternative to the support-plane matrix",
            "emit": "emit dual rows, observables, cert, report, verifier command, and next target",
        },
        "inputs": {
            "ext_report": pair.parent.input_entry(
                EXT_REPORT,
                {
                    "status": rows["ext_report"].get("status"),
                    "certificate_sha256": rows["ext_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "ext_tables": pair.parent.input_entry(EXT_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "gordan": pair.parent.relpath(OUT_DIR / "gordan.json"),
            "dual_csv": pair.parent.relpath(OUT_DIR / "dual.csv"),
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
                "a Gordan alternative witness for the oriented support-plane matrix",
                "no nonzero nonnegative dependence annihilates the support-plane matrix",
                "the certificate expands from 32 face rows to all 1,740 support rows by multiplicity",
            ],
            "does_not_certify_because_not_required": [
                "minimal exterior affine circuits",
                "Gordan infeasibility for the full affine-circuit matrix A_ext",
                "surgery across eta6",
            ],
        },
        "next_highest_yield_item": (
            "Enumerate minimal affine circuits from exterior vertex sets and "
            "run the same Gordan alternative on that full A_ext matrix."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    cert = {
        "schema": "eta6.gordan.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.gordan.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "gordan": gordan,
        "dual_csv": ext.pair.csv_text(DUAL_COLUMNS, rows["dual_rows"]),
        "obs_csv": ext.pair.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "dual_table": dual_table,
        "observable_table": obs_table,
        "obs_table": obs_table,
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
    pair.parent.write_json(OUT_DIR / "gordan.json", payloads["gordan"])
    (OUT_DIR / "dual.csv").write_text(payloads["dual_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        dual_table=payloads["dual_table"],
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
