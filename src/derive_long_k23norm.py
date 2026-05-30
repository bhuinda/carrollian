from __future__ import annotations

import csv
import hashlib
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23norm"
STATUS = "SECTOR33_K23_MLKEM512_NORMALIZATION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23norm.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23norm.py"
LONG_K23BENCH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23bench" / "report.json"
LONG_K23BENCH_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23bench" / "bench_rows.csv"

PARAM_TEXT_HASH = "8ee43297fdf8085a5f172ece324efeab9b14e773f0237066f2d05048504ccd05"
NORM_TEXT_HASH = "55430c9b245ee8b534378f692476d3c4cbefa2b14f46b36b8b22617571197270"
EQUATION_TEXT_HASH = "45fd5506e75387337f7ceedf21b01141c2f8b117eec51ec70ec0d3cf225aef22"
LIMIT_TEXT_HASH = "c6d5f33b69b8a0e62786e580098e240a1b4b9e1f82aa962f5a99ba705d5ed22a"
OBS_TEXT_HASH = "f45ca6cdd425e0c132b798e6fe17217ee513b07694fd54d57d3360b59c0d2610"
MATRIX_SHA256 = "f107beed4032acfa0cedb9b0e11e9ebfc98f56230e1b1786886c61ec95a25283"

PARAM_COLUMNS = [
    "parameter_id",
    "spec_code",
    "parameter_set_code",
    "n_value",
    "q_value",
    "k_value",
    "eta1_value",
    "eta2_value",
    "du_value",
    "dv_value",
    "required_rbg_strength_bits",
    "encapsulation_key_bytes",
    "decapsulation_key_bytes",
    "ciphertext_bytes",
    "shared_secret_bytes",
    "official_source_flag",
]
NORM_COLUMNS = [
    "normalization_id",
    "candidate_id",
    "potential_code",
    "baseline_spec_code",
    "parameter_set_code",
    "internal_operation_count",
    "internal_transcript_rows",
    "internal_verification_path_count",
    "digest_bytes",
    "public_digest_columns",
    "opening_digest_columns",
    "internal_public_digest_bytes",
    "internal_opening_digest_bytes",
    "baseline_public_exchange_bytes",
    "baseline_total_material_bytes",
    "external_numeric_baseline_flag",
    "comparison_equation_flag",
    "improvement_claim_flag",
]
EQUATION_COLUMNS = [
    "equation_id",
    "equation_code",
    "left_value",
    "right_value",
    "equality_flag",
    "improvement_claim_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "open_flag",
    "required_before_improvement_claim_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "selected_candidate_id",
    "selected_potential_code",
    "selected_baseline_spec_code",
    "bench_candidate_count",
    "parameter_row_count",
    "official_parameter_source_count",
    "parameter_set_code",
    "required_rbg_strength_bits",
    "encapsulation_key_bytes",
    "decapsulation_key_bytes",
    "ciphertext_bytes",
    "shared_secret_bytes",
    "baseline_public_exchange_bytes",
    "baseline_total_material_bytes",
    "digest_bytes",
    "public_digest_columns",
    "opening_digest_columns",
    "internal_operation_count",
    "internal_transcript_rows",
    "internal_verification_path_count",
    "internal_public_digest_bytes",
    "internal_opening_digest_bytes",
    "comparison_delta_public_bytes",
    "public_ratio_numerator",
    "public_ratio_denominator",
    "equation_row_count",
    "equation_pass_count",
    "external_numeric_baseline_count",
    "improvement_claim_count",
    "limit_row_count",
    "open_limit_count",
    "overclaim_count",
    "normalization_surface_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["param_table", "norm_table", "equation_table", "limit_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def reduce_ratio(numerator: int, denominator: int) -> tuple[int, int]:
    from math import gcd

    divisor = gcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def build_rows() -> dict[str, Any]:
    bench_report = load_json(LONG_K23BENCH_REPORT)
    bench_summary = summary(bench_report)
    bench_rows = read_csv_rows(LONG_K23BENCH_ROWS)
    selected = next(row for row in bench_rows if int(row["candidate_id"]) == 3)

    digest_bytes = 32
    public_digest_columns = 3
    opening_digest_columns = 4
    internal_operation_count = int(selected["internal_operation_count"])
    internal_transcript_rows = int(selected["transcript_size_rows"])
    internal_verification_path_count = int(selected["verification_path_count"])
    internal_public_digest_bytes = internal_transcript_rows * public_digest_columns * digest_bytes
    internal_opening_digest_bytes = internal_verification_path_count * opening_digest_columns * digest_bytes

    encapsulation_key_bytes = 800
    decapsulation_key_bytes = 1632
    ciphertext_bytes = 768
    shared_secret_bytes = 32
    baseline_public_exchange_bytes = encapsulation_key_bytes + ciphertext_bytes
    baseline_total_material_bytes = (
        encapsulation_key_bytes
        + decapsulation_key_bytes
        + ciphertext_bytes
        + shared_secret_bytes
    )
    comparison_delta_public_bytes = internal_public_digest_bytes - baseline_public_exchange_bytes
    ratio_num, ratio_den = reduce_ratio(internal_public_digest_bytes, baseline_public_exchange_bytes)

    param_rows = [
        {
            "parameter_id": 0,
            "spec_code": 0,
            "parameter_set_code": 512,
            "n_value": 256,
            "q_value": 3329,
            "k_value": 2,
            "eta1_value": 3,
            "eta2_value": 2,
            "du_value": 10,
            "dv_value": 4,
            "required_rbg_strength_bits": 128,
            "encapsulation_key_bytes": encapsulation_key_bytes,
            "decapsulation_key_bytes": decapsulation_key_bytes,
            "ciphertext_bytes": ciphertext_bytes,
            "shared_secret_bytes": shared_secret_bytes,
            "official_source_flag": 1,
        }
    ]
    norm_rows = [
        {
            "normalization_id": 0,
            "candidate_id": int(selected["candidate_id"]),
            "potential_code": int(selected["potential_code"]),
            "baseline_spec_code": int(selected["baseline_spec_code"]),
            "parameter_set_code": 512,
            "internal_operation_count": internal_operation_count,
            "internal_transcript_rows": internal_transcript_rows,
            "internal_verification_path_count": internal_verification_path_count,
            "digest_bytes": digest_bytes,
            "public_digest_columns": public_digest_columns,
            "opening_digest_columns": opening_digest_columns,
            "internal_public_digest_bytes": internal_public_digest_bytes,
            "internal_opening_digest_bytes": internal_opening_digest_bytes,
            "baseline_public_exchange_bytes": baseline_public_exchange_bytes,
            "baseline_total_material_bytes": baseline_total_material_bytes,
            "external_numeric_baseline_flag": 1,
            "comparison_equation_flag": 1,
            "improvement_claim_flag": 0,
        }
    ]
    equation_rows = [
        {"equation_id": 0, "equation_code": 0, "left_value": internal_public_digest_bytes, "right_value": 56 * 3 * 32, "equality_flag": 1, "improvement_claim_flag": 0},
        {"equation_id": 1, "equation_code": 1, "left_value": internal_opening_digest_bytes, "right_value": 56 * 4 * 32, "equality_flag": 1, "improvement_claim_flag": 0},
        {"equation_id": 2, "equation_code": 2, "left_value": baseline_public_exchange_bytes, "right_value": 800 + 768, "equality_flag": 1, "improvement_claim_flag": 0},
        {"equation_id": 3, "equation_code": 3, "left_value": baseline_total_material_bytes, "right_value": 800 + 1632 + 768 + 32, "equality_flag": 1, "improvement_claim_flag": 0},
        {"equation_id": 4, "equation_code": 4, "left_value": comparison_delta_public_bytes, "right_value": internal_public_digest_bytes - baseline_public_exchange_bytes, "equality_flag": 1, "improvement_claim_flag": 0},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 3, "limit_code": 3, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 4, "limit_code": 4, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": 1,
        "certified_input_count": is_certified(bench_report, "SECTOR33_K23_BENCHMARK_SURFACE_CERTIFIED"),
        "selected_candidate_id": int(selected["candidate_id"]),
        "selected_potential_code": int(selected["potential_code"]),
        "selected_baseline_spec_code": int(selected["baseline_spec_code"]),
        "bench_candidate_count": int(bench_summary.get("candidate_row_count", -1)),
        "parameter_row_count": len(param_rows),
        "official_parameter_source_count": sum(row["official_source_flag"] for row in param_rows),
        "parameter_set_code": 512,
        "required_rbg_strength_bits": 128,
        "encapsulation_key_bytes": encapsulation_key_bytes,
        "decapsulation_key_bytes": decapsulation_key_bytes,
        "ciphertext_bytes": ciphertext_bytes,
        "shared_secret_bytes": shared_secret_bytes,
        "baseline_public_exchange_bytes": baseline_public_exchange_bytes,
        "baseline_total_material_bytes": baseline_total_material_bytes,
        "digest_bytes": digest_bytes,
        "public_digest_columns": public_digest_columns,
        "opening_digest_columns": opening_digest_columns,
        "internal_operation_count": internal_operation_count,
        "internal_transcript_rows": internal_transcript_rows,
        "internal_verification_path_count": internal_verification_path_count,
        "internal_public_digest_bytes": internal_public_digest_bytes,
        "internal_opening_digest_bytes": internal_opening_digest_bytes,
        "comparison_delta_public_bytes": comparison_delta_public_bytes,
        "public_ratio_numerator": ratio_num,
        "public_ratio_denominator": ratio_den,
        "equation_row_count": len(equation_rows),
        "equation_pass_count": sum(row["equality_flag"] for row in equation_rows),
        "external_numeric_baseline_count": sum(row["external_numeric_baseline_flag"] for row in norm_rows),
        "improvement_claim_count": sum(row["improvement_claim_flag"] for row in norm_rows) + sum(row["improvement_claim_flag"] for row in equation_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "normalization_surface_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    param_table = table_from_rows(PARAM_COLUMNS, param_rows)
    norm_table = table_from_rows(NORM_COLUMNS, norm_rows)
    equation_table = table_from_rows(EQUATION_COLUMNS, equation_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "param_table": param_table.astype(np.int64),
        "norm_table": norm_table.astype(np.int64),
        "equation_table": equation_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "bench_report": bench_report,
        "param_rows": param_rows,
        "norm_rows": norm_rows,
        "equation_rows": equation_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "param_table": param_table,
        "norm_table": norm_table,
        "equation_table": equation_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "param_text_hash": hashlib.sha256(digest_text(PARAM_COLUMNS, param_rows).encode("ascii")).hexdigest(),
        "norm_text_hash": hashlib.sha256(digest_text(NORM_COLUMNS, norm_rows).encode("ascii")).hexdigest(),
        "equation_text_hash": hashlib.sha256(digest_text(EQUATION_COLUMNS, equation_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_pass": obs["certified_input_count"] == 1,
        "selected_candidate_matches": (
            obs["selected_candidate_id"],
            obs["selected_potential_code"],
            obs["selected_baseline_spec_code"],
            obs["bench_candidate_count"],
        )
        == (3, 3, 0, 6),
        "parameter_profile_matches": (
            obs["parameter_set_code"],
            obs["required_rbg_strength_bits"],
            obs["encapsulation_key_bytes"],
            obs["decapsulation_key_bytes"],
            obs["ciphertext_bytes"],
            obs["shared_secret_bytes"],
            obs["official_parameter_source_count"],
        )
        == (512, 128, 800, 1632, 768, 32, 1),
        "byte_equations_match": (
            obs["baseline_public_exchange_bytes"],
            obs["baseline_total_material_bytes"],
            obs["internal_public_digest_bytes"],
            obs["internal_opening_digest_bytes"],
            obs["comparison_delta_public_bytes"],
            obs["public_ratio_numerator"],
            obs["public_ratio_denominator"],
            obs["equation_row_count"],
            obs["equation_pass_count"],
        )
        == (1568, 3232, 5376, 7168, 3808, 24, 7, 5, 5),
        "claim_boundary_matches": (
            obs["external_numeric_baseline_count"],
            obs["improvement_claim_count"],
            obs["normalization_surface_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 1, 0),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["overclaim_count"],
        )
        == (5, 5, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_mlkem512_one_candidate_normalization",
        "selected_candidate": "authority_decision_table_candidate",
        "parameter_set": "ML-KEM-512",
        "external_source_url": "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf",
        "equation_code_map": {
            "0": "internal_public_digest_bytes",
            "1": "internal_opening_digest_bytes",
            "2": "baseline_public_exchange_bytes",
            "3": "baseline_total_material_bytes",
            "4": "public_digest_minus_baseline_public_exchange_bytes",
        },
        "limit_code_map": {
            "0": "wire_format_mapping",
            "1": "operation_model_equivalence",
            "2": "implementation_timing_or_memory_measurement",
            "3": "security_reduction",
            "4": "interoperability_or_compliance",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This normalizes one K23 benchmark candidate against ML-KEM-512 byte-size constants and equations without asserting an improvement.",
    }
    seam_payload = {
        "schema": "long.k23norm.seam@1",
        "status": STATUS,
        "claim": "One K23 benchmark candidate is normalized against ML-KEM-512 byte-size constants with explicit equations and no improvement claim.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23bench": input_entry(
            LONG_K23BENCH_REPORT,
            {
                "status": rows["bench_report"].get("status"),
                "certificate_sha256": rows["bench_report"].get("certificate_sha256"),
            },
        ),
        "long_k23bench_rows": input_entry(LONG_K23BENCH_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23norm.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23norm certifies one-candidate ML-KEM-512 normalization for the K23 benchmark surface.",
        "stage_protocol": {
            "draft": "read long_k23bench and select the FIPS 203 baseline candidate row",
            "witness": "emit parameter constants, normalization row, equation rows, open-limit rows, observables, and numeric tables",
            "coherence": "check selected candidate, byte constants, equations, ratio, and claim boundary",
            "closure": "certify one concrete normalization row without asserting improvement, compliance, or deployment readiness",
            "emit": "write long_k23norm artifacts and verifier hook",
        },
        "inputs": inputs,
        "external_sources": {
            "source_kind": "official_nist_fips_203_pdf",
            "url": "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf",
            "used_facts": [
                "ML-KEM-512 parameter row: n=256, q=3329, k=2, eta1=3, eta2=2, du=10, dv=4, required RBG strength 128 bits",
                "ML-KEM-512 byte row: encapsulation key 800, decapsulation key 1632, ciphertext 768, shared secret 32",
            ],
        },
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "parameter_rows_csv": relpath(OUT_DIR / "parameter_rows.csv"),
            "normalization_rows_csv": relpath(OUT_DIR / "normalization_rows.csv"),
            "equation_rows_csv": relpath(OUT_DIR / "equation_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23norm_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "candidate 3 from long_k23bench is selected for FIPS 203 ML-KEM-512 normalization",
                "ML-KEM-512 parameter and byte constants are materialized as one local row",
                "internal digest-row byte equations and public-exchange byte equations are explicit",
                "one external numeric baseline is materialized",
                "improvement, compliance, runtime, and deployment claims remain false",
            ],
            "does_not_certify": [
                "speed or size improvement",
                "security superiority",
                "wire-format equivalence",
                "operation-model equivalence",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Use the normalization row to define a candidate-specific wire-format map or demote the candidate if no compact public transcript encoding exists.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23norm.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23norm.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "param_csv": csv_text(PARAM_COLUMNS, rows["param_rows"]),
        "norm_csv": csv_text(NORM_COLUMNS, rows["norm_rows"]),
        "equation_csv": csv_text(EQUATION_COLUMNS, rows["equation_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "param_table": rows["param_table"],
        "norm_table": rows["norm_table"],
        "equation_table": rows["equation_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "param_text_sha256": rows["param_text_hash"],
            "norm_text_sha256": rows["norm_text_hash"],
            "equation_text_sha256": rows["equation_text_hash"],
            "limit_text_sha256": rows["limit_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
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
    (OUT_DIR / "parameter_rows.csv").write_text(payloads["param_csv"], encoding="utf-8")
    (OUT_DIR / "normalization_rows.csv").write_text(payloads["norm_csv"], encoding="utf-8")
    (OUT_DIR / "equation_rows.csv").write_text(payloads["equation_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        param_table=payloads["param_table"],
        norm_table=payloads["norm_table"],
        equation_table=payloads["equation_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23norm_matrices.npz", **payloads["matrix_payload"])
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
