from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_hcfoam"
STATUS = "LONG_HCFOAM_CERTIFIED"
FIELD_PRIME = 1_000_003
FOAM16_DIM = 16
FOAM33_DIM = 33
FOAM16_COPY_COUNT = 2

OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
TENSOR_CHAIN = ROOT / "data" / "evidence" / "tensor_chain" / "stages"
ALL_FOUR = TENSOR_CHAIN / "all_four_lifts"
INTERTWINE_DIR = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "height_coherent_action_return_intertwining"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcfoam.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcfoam.py"
LONG_HCINV_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcinv" / "report.json"
ALL_FOUR_REPORT = ALL_FOUR / "all_four_lifts_report.json"
FOAM16_BASIS_CSV = ALL_FOUR / "faithful_foam16_module_basis.csv"
FOAM16_EDGES_CSV = ALL_FOUR / "faithful_foam16_generator_action_edges.csv"
FOAM16_CERT_CSV = ALL_FOUR / "faithful_foam16_module_certification.csv"
INTERTWINE_TARGET = INTERTWINE_DIR / "height_coherent_action_return_intertwining_target.json"
INTERTWINE_SPEC = INTERTWINE_DIR / "next_intertwining_verifier_spec.json"

BASIS_TEXT_HASH = "89675097622280bea2eba1a17a59182b0644ea2d5e5480f0f80bdd3c9efd8eb9"
GENERATOR_TEXT_HASH = "db8f4d508f6e3ff9f3863e386a5216474a830285f138af8b435413aa9615e5b7"
EDGE_TEXT_HASH = "0875d36ad3a350ab670f33cc7836ed5f79490df4f4286816c96a175a20196780"
OBS_TEXT_HASH = "981d3749405526075b07091d140432c4a57c1e9f3f7fc6daf4b9f5ee702114f0"

BASIS_COLUMNS = [
    "basis_id",
    "block_code",
    "foam16_index",
    "copy_index",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "source_row_count",
    "target_row_count",
    "foam16_signed_monomial_flag",
    "foam33_signed_monomial_flag",
    "foam33_global_fixed_flag",
    "copy_action_identical_flag",
    "trace_signed",
]
EDGE_COLUMNS = [
    "edge_id",
    "generator_id",
    "source_basis_id",
    "target_basis_id",
    "sign",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "field_prime",
    "foam16_dimension",
    "foam33_dimension",
    "foam16_copy_count",
    "generator_count",
    "foam16_edge_count",
    "foam33_edge_count",
    "foam16_nonzero_count",
    "foam33_nonzero_count",
    "all_foam16_signed_monomial_flag",
    "all_foam16_orthogonal_flag",
    "all_foam33_signed_monomial_flag",
    "all_foam33_orthogonal_flag",
    "all_global_fixed_flag",
    "all_copy_actions_identical_flag",
    "module_basis_rank",
    "projective_action_count",
    "generator_closure_count",
    "r_foam_materialized_flag",
    "pi_foam33_materialized_flag",
    "r_hc_materialized_flag",
    "focused_hcfoam_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_cert_csv(path: Path) -> dict[str, str]:
    _header, rows = read_csv_rows(path)
    return {row["diagnostic"]: row["value"] for row in rows}


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def signed_monomial(matrix: np.ndarray) -> bool:
    nonzero_per_col = np.count_nonzero(matrix, axis=0)
    nonzero_per_row = np.count_nonzero(matrix, axis=1)
    values_ok = set(np.unique(matrix)).issubset({-1, 0, 1})
    return (
        values_ok
        and bool(np.all(nonzero_per_col == 1))
        and bool(np.all(nonzero_per_row == 1))
    )


def orthogonal_signed(matrix: np.ndarray) -> bool:
    return bool(np.array_equal(matrix.T @ matrix, np.eye(matrix.shape[0], dtype=int)))


def build_foam16_generators() -> tuple[np.ndarray, list[str], list[dict[str, str]]]:
    header, rows = read_csv_rows(FOAM16_EDGES_CSV)
    expected = [
        "generator_index",
        "generator",
        "source_index",
        "source_label",
        "target_index",
        "target_label",
        "sign",
    ]
    if header != expected:
        raise AssertionError("Foam16 generator edge schema mismatch")
    generator_ids = sorted({int(row["generator_index"]) for row in rows})
    if generator_ids != list(range(len(generator_ids))):
        raise AssertionError("Foam16 generator ids are not contiguous")
    matrices = np.zeros((len(generator_ids), FOAM16_DIM, FOAM16_DIM), dtype=np.int64)
    names: list[str] = []
    for generator_id in generator_ids:
        generator_rows = [
            row for row in rows if int(row["generator_index"]) == generator_id
        ]
        if len(generator_rows) != FOAM16_DIM:
            raise AssertionError("Foam16 generator row count mismatch")
        names.append(generator_rows[0]["generator"])
        seen_sources: set[int] = set()
        seen_targets: set[int] = set()
        for row in generator_rows:
            source = int(row["source_index"])
            target = int(row["target_index"])
            sign = int(row["sign"])
            if sign not in {-1, 1}:
                raise AssertionError("Foam16 generator sign mismatch")
            matrices[generator_id, target, source] = sign
            seen_sources.add(source)
            seen_targets.add(target)
        if seen_sources != set(range(FOAM16_DIM)):
            raise AssertionError("Foam16 source basis coverage mismatch")
        if seen_targets != set(range(FOAM16_DIM)):
            raise AssertionError("Foam16 target basis coverage mismatch")
    return matrices, names, rows


def build_r_foam(foam16: np.ndarray) -> np.ndarray:
    r_foam = np.zeros((foam16.shape[0], FOAM33_DIM, FOAM33_DIM), dtype=np.int64)
    for generator_id, matrix in enumerate(foam16):
        r_foam[generator_id, 0, 0] = 1
        for source in range(FOAM16_DIM):
            for target in range(FOAM16_DIM):
                sign = int(matrix[target, source])
                if not sign:
                    continue
                r_foam[generator_id, 1 + target, 1 + source] = sign
                r_foam[
                    generator_id,
                    1 + FOAM16_DIM + target,
                    1 + FOAM16_DIM + source,
                ] = sign
    return r_foam


def build_rows() -> dict[str, Any]:
    long_hcinv = load_json(LONG_HCINV_REPORT)
    all_four_report = load_json(ALL_FOUR_REPORT)
    target = load_json(INTERTWINE_TARGET)
    spec = load_json(INTERTWINE_SPEC)
    basis_header, basis_input_rows = read_csv_rows(FOAM16_BASIS_CSV)
    cert = read_cert_csv(FOAM16_CERT_CSV)
    foam16, generator_names, foam16_edge_rows = build_foam16_generators()
    r_foam = build_r_foam(foam16)

    if basis_header != ["label_index", "foam_basis", "degree"]:
        raise AssertionError("Foam16 basis schema mismatch")
    if len(basis_input_rows) != FOAM16_DIM:
        raise AssertionError("Foam16 basis row count mismatch")
    if [int(row["label_index"]) for row in basis_input_rows] != list(
        range(FOAM16_DIM)
    ):
        raise AssertionError("Foam16 basis order mismatch")

    basis_rows = [{"basis_id": 0, "block_code": 0, "foam16_index": -1, "copy_index": -1}]
    for copy_index in range(FOAM16_COPY_COUNT):
        for foam16_index in range(FOAM16_DIM):
            basis_rows.append(
                {
                    "basis_id": 1 + copy_index * FOAM16_DIM + foam16_index,
                    "block_code": 1 + copy_index,
                    "foam16_index": foam16_index,
                    "copy_index": copy_index,
                }
            )

    generator_rows: list[dict[str, int]] = []
    edge_rows: list[dict[str, int]] = []
    edge_id = 0
    for generator_id in range(foam16.shape[0]):
        matrix = foam16[generator_id]
        target_matrix = r_foam[generator_id]
        copy_a = target_matrix[1 : 1 + FOAM16_DIM, 1 : 1 + FOAM16_DIM]
        copy_b = target_matrix[1 + FOAM16_DIM :, 1 + FOAM16_DIM :]
        generator_rows.append(
            {
                "generator_id": generator_id,
                "source_row_count": FOAM16_DIM,
                "target_row_count": FOAM33_DIM,
                "foam16_signed_monomial_flag": int(signed_monomial(matrix)),
                "foam33_signed_monomial_flag": int(signed_monomial(target_matrix)),
                "foam33_global_fixed_flag": int(target_matrix[0, 0] == 1),
                "copy_action_identical_flag": int(
                    np.array_equal(copy_a, matrix) and np.array_equal(copy_b, matrix)
                ),
                "trace_signed": int(np.trace(target_matrix)),
            }
        )
        for source in range(FOAM33_DIM):
            nonzero = np.nonzero(target_matrix[:, source])[0]
            if len(nonzero) != 1:
                raise AssertionError("R_Foam column is not monomial")
            target_basis = int(nonzero[0])
            edge_rows.append(
                {
                    "edge_id": edge_id,
                    "generator_id": generator_id,
                    "source_basis_id": source,
                    "target_basis_id": target_basis,
                    "sign": int(target_matrix[target_basis, source]),
                }
            )
            edge_id += 1

    all_foam16_signed = all(signed_monomial(matrix) for matrix in foam16)
    all_foam16_orthogonal = all(orthogonal_signed(matrix) for matrix in foam16)
    all_foam33_signed = all(signed_monomial(matrix) for matrix in r_foam)
    all_foam33_orthogonal = all(orthogonal_signed(matrix) for matrix in r_foam)
    all_global_fixed = all(int(matrix[0, 0]) == 1 for matrix in r_foam)
    all_copy_actions_identical = all(
        np.array_equal(matrix[1 : 1 + FOAM16_DIM, 1 : 1 + FOAM16_DIM], foam16[index])
        and np.array_equal(
            matrix[1 + FOAM16_DIM :, 1 + FOAM16_DIM :], foam16[index]
        )
        for index, matrix in enumerate(r_foam)
    )

    obs = {
        "field_prime": FIELD_PRIME,
        "foam16_dimension": FOAM16_DIM,
        "foam33_dimension": FOAM33_DIM,
        "foam16_copy_count": FOAM16_COPY_COUNT,
        "generator_count": int(foam16.shape[0]),
        "foam16_edge_count": len(foam16_edge_rows),
        "foam33_edge_count": len(edge_rows),
        "foam16_nonzero_count": int(np.count_nonzero(foam16)),
        "foam33_nonzero_count": int(np.count_nonzero(r_foam)),
        "all_foam16_signed_monomial_flag": int(all_foam16_signed),
        "all_foam16_orthogonal_flag": int(all_foam16_orthogonal),
        "all_foam33_signed_monomial_flag": int(all_foam33_signed),
        "all_foam33_orthogonal_flag": int(all_foam33_orthogonal),
        "all_global_fixed_flag": int(all_global_fixed),
        "all_copy_actions_identical_flag": int(all_copy_actions_identical),
        "module_basis_rank": int(cert["basis_rank"]),
        "projective_action_count": int(cert["distinct_projective_actions_on_Foam16"]),
        "generator_closure_count": int(
            cert["closure_generated_by_listed_generators_on_Foam16"]
        ),
        "r_foam_materialized_flag": 1,
        "pi_foam33_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "focused_hcfoam_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": OBS_CODES[name],
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for name in OBS_NAMES
    ]

    basis_table = table_from_rows(BASIS_COLUMNS, basis_rows)
    generator_table = table_from_rows(GENERATOR_COLUMNS, generator_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    return {
        "long_hcinv": long_hcinv,
        "all_four_report": all_four_report,
        "target": target,
        "spec": spec,
        "cert": cert,
        "generator_names": generator_names,
        "foam16": foam16,
        "r_foam": r_foam,
        "basis_rows": basis_rows,
        "generator_rows": generator_rows,
        "edge_rows": edge_rows,
        "obs_rows": obs_rows,
        "basis_table": basis_table,
        "generator_table": generator_table,
        "edge_table": edge_table,
        "observable_table": obs_table,
        "obs": obs,
        "basis_text_hash": hashlib.sha256(
            digest_text(BASIS_COLUMNS, basis_rows).encode("ascii")
        ).hexdigest(),
        "generator_text_hash": hashlib.sha256(
            digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")
        ).hexdigest(),
        "edge_text_hash": hashlib.sha256(
            digest_text(EDGE_COLUMNS, edge_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
        "foam16_matrix_sha256": sha_array(foam16),
        "r_foam_matrix_sha256": sha_array(r_foam),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    long_hcinv = rows["long_hcinv"]
    all_four_report = rows["all_four_report"]
    target = rows["target"]
    spec = rows["spec"]
    cert = rows["cert"]
    checks = {
        "long_hcinv_input_passes": long_hcinv.get("all_checks_pass") is True
        and long_hcinv.get("status") == "LONG_HCINV_CERTIFIED",
        "intertwining_spec_requires_r_foam": "Foam target action-return operator"
        in spec.get("required_inputs", []),
        "target_shape_is_one_plus_two_foam16": target.get("minimal_operator_shape", {})
        .get("R_Foam", "")
        .startswith("induced operator on 1_glob"),
        "foam16_module_input_certified": (
            cert.get("basis_rank"),
            cert.get("all_signed_fano_G_signed_monomial"),
            cert.get("all_signed_fano_G_orthogonal"),
        )
        == ("16", "True", "True"),
        "all_four_lifts_constructs_foam_module": all_four_report.get("tasks", {})
        .get("2_canonical_16_label_foam_module", {})
        .get("canonical_foam_module_rank")
        == 16,
        "r_foam_shape_and_counts": (
            obs["generator_count"],
            obs["foam33_dimension"],
            obs["foam33_edge_count"],
            obs["foam33_nonzero_count"],
        )
        == (9, 33, 297, 297),
        "foam16_shape_and_counts": (
            obs["foam16_dimension"],
            obs["foam16_edge_count"],
            obs["foam16_nonzero_count"],
        )
        == (16, 144, 144),
        "signed_monomial_and_orthogonal": (
            obs["all_foam16_signed_monomial_flag"],
            obs["all_foam16_orthogonal_flag"],
            obs["all_foam33_signed_monomial_flag"],
            obs["all_foam33_orthogonal_flag"],
        )
        == (1, 1, 1, 1),
        "foam33_block_structure": (
            obs["all_global_fixed_flag"],
            obs["all_copy_actions_identical_flag"],
            obs["module_basis_rank"],
            obs["projective_action_count"],
            obs["generator_closure_count"],
        )
        == (1, 1, 16, 384, 384),
        "remaining_intertwiner_inputs_marked_open": (
            obs["r_foam_materialized_flag"],
            obs["pi_foam33_materialized_flag"],
            obs["r_hc_materialized_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0, 0),
        "tables_have_expected_shapes": (
            tuple(rows["basis_table"].shape),
            tuple(rows["generator_table"].shape),
            tuple(rows["edge_table"].shape),
            tuple(rows["observable_table"].shape),
            tuple(rows["foam16"].shape),
            tuple(rows["r_foam"].shape),
        )
        == (
            (FOAM33_DIM, len(BASIS_COLUMNS)),
            (9, len(GENERATOR_COLUMNS)),
            (297, len(EDGE_COLUMNS)),
            (len(OBS_NAMES), len(OBS_COLUMNS)),
            (9, FOAM16_DIM, FOAM16_DIM),
            (9, FOAM33_DIM, FOAM33_DIM),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "foam_target_action_return_operator_family",
        "summary": obs,
        "generator_names": rows["generator_names"],
        "matrix_hashes": {
            "foam16_matrix_sha256": rows["foam16_matrix_sha256"],
            "r_foam_matrix_sha256": rows["r_foam_matrix_sha256"],
        },
        "operator_boundary": {
            "r_foam_materialized": True,
            "pi_foam33_materialized": False,
            "r_hc_materialized": False,
            "full_intertwiner_verified": False,
        },
    }
    seam_payload = {
        "schema": "long.hcfoam.seam@1",
        "status": STATUS,
        "claim": (
            "The Foam target side of the height/action-return intertwining target "
            "is materialized as nine 33x33 signed-monomial R_Foam generator "
            "matrices on 1_glob plus two Foam16 copies."
        ),
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcinv": input_entry(
            LONG_HCINV_REPORT,
            {
                "status": long_hcinv.get("status"),
                "certificate_sha256": long_hcinv.get("certificate_sha256"),
            },
        ),
        "all_four_lifts_report": input_entry(
            ALL_FOUR_REPORT, {"status": all_four_report.get("status")}
        ),
        "foam16_basis": input_entry(FOAM16_BASIS_CSV),
        "foam16_generator_edges": input_entry(FOAM16_EDGES_CSV),
        "foam16_module_certification": input_entry(FOAM16_CERT_CSV),
        "intertwining_target": input_entry(INTERTWINE_TARGET),
        "intertwining_spec": input_entry(INTERTWINE_SPEC),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT)
        if VALIDATOR_SCRIPT.exists()
        else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcfoam.report@1",
        "status": seam_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_hcfoam turns the Foam target operator requested by the "
            "height/action-return intertwining spec into concrete checked "
            "33x33 matrices. It deliberately leaves pi_Foam33 and R_hc open."
        ),
        "stage_protocol": {
            "draft": "read long_hcinv, the Foam16 module basis/action edges, the module certification, and the intertwining target spec",
            "witness": "emit Foam33 basis rows, R_Foam generator summaries, signed action edges, and matrix hashes",
            "coherence": "check signed-monomial, orthogonality, block structure, counts, and open remaining inputs",
            "closure": "certify only the R_Foam target-side matrix family",
            "emit": "write long_hcfoam artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "basis_csv": relpath(OUT_DIR / "foam33_basis.csv"),
            "generator_csv": relpath(OUT_DIR / "r_foam_generators.csv"),
            "edge_csv": relpath(OUT_DIR / "r_foam_edges.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "r_foam_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the Foam16 generator edge table materializes nine signed-monomial 16x16 operators",
                "the target action is lifted to nine 33x33 signed-monomial R_Foam operators on 1_glob plus two Foam16 copies",
                "the global coordinate is fixed by every R_Foam generator",
                "the two Foam16 copies carry identical generator actions",
                "the R_Foam matrices are ready as verifier input for the height/action-return intertwining test",
            ],
            "does_not_certify": [
                "a materialized pi_Foam33 projection matrix",
                "a materialized R_hc source-side matrix family",
                "the full pi_Foam33 R_hc equals R_Foam pi_Foam33 identity",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": (
            "Materialize pi_Foam33 as the 33x56 support projection, then bind "
            "R_hc on the e33 56-support and run the existing matrix verifier "
            "against the checked R_Foam family."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert_payload = {
        "schema": "long.hcfoam.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.hcfoam.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "basis_table": rows["basis_table"],
        "generator_table": rows["generator_table"],
        "edge_table": rows["edge_table"],
        "observable_table": rows["observable_table"],
        "foam16": rows["foam16"],
        "r_foam": rows["r_foam"],
        "cert": cert_payload,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "basis_text_sha256": rows["basis_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
            "edge_text_sha256": rows["edge_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "foam16_matrix_sha256": rows["foam16_matrix_sha256"],
            "r_foam_matrix_sha256": rows["r_foam_matrix_sha256"],
        },
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
    (OUT_DIR / "foam33_basis.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "r_foam_generators.csv").write_text(
        payloads["generator_csv"], encoding="utf-8"
    )
    (OUT_DIR / "r_foam_edges.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        basis_table=payloads["basis_table"],
        generator_table=payloads["generator_table"],
        edge_table=payloads["edge_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(
        OUT_DIR / "r_foam_matrices.npz",
        foam16=payloads["foam16"],
        r_foam=payloads["r_foam"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
