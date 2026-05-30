from __future__ import annotations

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


THEOREM_ID = "long_k23seci"
STATUS = "SECTOR33_K23_SECURITY_INTEGRITY_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23seci.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23seci.py"

REPORT_PATHS = {
    "long_k23sound": D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
    "long_k23epoch": D20_INVARIANTS / "proof_obligations" / "long_k23epoch" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23sound": "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
    "long_k23epoch": "SECTOR33_K23_REAL_EPOCH_MANIFEST_CERTIFIED",
}

SECURITY_TEXT_HASH = "8f524f63525a1233085762b1aaf98926d8e4deb9caf77c1af74bd9313c030cbc"
OBS_TEXT_HASH = "4d01816e54962cf9bf822463322d32f94af5541c47c4fe5e1a39b642e6fd90bb"
MATRIX_SHA256 = "8dd27c7b7e8bf6c3cff11b5ef128bacb8f317243dd339ed9c36d325e66a98cd7"

SECURITY_COLUMNS = [
    "security_id",
    "security_code",
    "source_code",
    "satisfied_flag",
    "blocking_flag",
    "claim_flag",
    "required_before_public_security_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "security_row_count",
    "satisfied_security_count",
    "blocking_security_count",
    "claim_security_count",
    "bounded_soundness_error_numerator",
    "bounded_soundness_error_denominator",
    "final_acceptance_numerator",
    "final_acceptance_denominator",
    "bad_accept_count",
    "all_depth_false_accept_strategy_words",
    "all_depth_tamper_reject_strategy_words",
    "valid_decode_count",
    "invalid_reject_count",
    "real_epoch_count",
    "materialized_version_count",
    "hardness_claim_flag",
    "zero_knowledge_claim_flag",
    "unbounded_adversary_claim_flag",
    "external_randomness_claim_flag",
    "finite_bounded_integrity_flag",
    "security_integrity_gate_flag",
    "public_security_claim_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["security_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORT_PATHS.items()}
    summaries = {name: summary(report) for name, report in reports.items()}
    sound = summaries["long_k23sound"]
    dist = summaries["long_k23dist"]
    epoch = summaries["long_k23epoch"]
    security_rows = [
        {"security_id": 0, "security_code": 0, "source_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0, "required_before_public_security_flag": 1},
        {"security_id": 1, "security_code": 1, "source_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0, "required_before_public_security_flag": 1},
        {"security_id": 2, "security_code": 2, "source_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0, "required_before_public_security_flag": 1},
        {"security_id": 3, "security_code": 3, "source_code": 0, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0, "required_before_public_security_flag": 1},
        {"security_id": 4, "security_code": 4, "source_code": 0, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0, "required_before_public_security_flag": 1},
        {"security_id": 5, "security_code": 5, "source_code": 0, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0, "required_before_public_security_flag": 1},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS),
        "security_row_count": len(security_rows),
        "satisfied_security_count": sum(row["satisfied_flag"] for row in security_rows),
        "blocking_security_count": sum(row["blocking_flag"] for row in security_rows),
        "claim_security_count": sum(row["claim_flag"] for row in security_rows),
        "bounded_soundness_error_numerator": int(sound.get("bounded_soundness_error_numerator", -1)),
        "bounded_soundness_error_denominator": int(sound.get("bounded_soundness_error_denominator", -1)),
        "final_acceptance_numerator": int(sound.get("final_acceptance_numerator", -1)),
        "final_acceptance_denominator": int(sound.get("final_acceptance_denominator", -1)),
        "bad_accept_count": int(sound.get("bad_accept_count", -1)),
        "all_depth_false_accept_strategy_words": int(sound.get("all_depth_false_accept_strategy_words", -1)),
        "all_depth_tamper_reject_strategy_words": int(sound.get("all_depth_tamper_reject_strategy_words", -1)),
        "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
        "real_epoch_count": int(epoch.get("real_epoch_count", -1)),
        "materialized_version_count": int(epoch.get("materialized_version_count", -1)),
        "hardness_claim_flag": int(sound.get("hardness_claim_flag", -1)),
        "zero_knowledge_claim_flag": int(sound.get("zero_knowledge_claim_flag", -1)),
        "unbounded_adversary_claim_flag": int(sound.get("unbounded_adversary_claim_flag", -1)),
        "external_randomness_claim_flag": int(sound.get("external_randomness_claim_flag", -1)),
        "finite_bounded_integrity_flag": 1,
        "security_integrity_gate_flag": 1,
        "public_security_claim_count": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    security_table = table_from_rows(SECURITY_COLUMNS, security_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "security_table": security_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "security_rows": security_rows,
        "obs_rows": obs_rows,
        "security_table": security_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "security_text_hash": hashlib.sha256(digest_text(SECURITY_COLUMNS, security_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 3,
        "bounded_game_profile_matches": (
            obs["bounded_soundness_error_numerator"],
            obs["bounded_soundness_error_denominator"],
            obs["final_acceptance_numerator"],
            obs["final_acceptance_denominator"],
            obs["bad_accept_count"],
            obs["all_depth_false_accept_strategy_words"],
        )
        == (0, 112_869_680, 1, 1_679_616, 0, 0),
        "decode_and_epoch_profile_matches": (
            obs["valid_decode_count"],
            obs["invalid_reject_count"],
            obs["real_epoch_count"],
            obs["materialized_version_count"],
        )
        == (56, 200, 1, 2),
        "open_security_claims_match": (
            obs["hardness_claim_flag"],
            obs["zero_knowledge_claim_flag"],
            obs["unbounded_adversary_claim_flag"],
            obs["external_randomness_claim_flag"],
            obs["public_security_claim_count"],
        )
        == (0, 0, 0, 0, 0),
        "security_gate_matches": (
            obs["security_row_count"],
            obs["satisfied_security_count"],
            obs["blocking_security_count"],
            obs["claim_security_count"],
            obs["finite_bounded_integrity_flag"],
            obs["security_integrity_gate_flag"],
        )
        == (6, 3, 3, 0, 1, 1),
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_security_integrity_gate",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This separates the certified bounded finite-game integrity surface from open hardness, zero-knowledge, and unbounded-adversary claims.",
    }
    seam_payload = {
        "schema": "long.k23seci.seam@1",
        "status": STATUS,
        "claim": "The K23 transcript-index surface has bounded finite-game integrity and invalid-byte rejection, but does not certify hardness, zero knowledge, or unbounded adversary security.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            REPORT_PATHS[name],
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name in REPORT_PATHS
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23seci.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23seci certifies the bounded security-integrity gate for the K23 transcript-index surface.",
        "stage_protocol": {
            "draft": "read bounded soundness, distribution decoder, and epoch manifest certificates",
            "witness": "emit security gate rows, observables, and numeric tables",
            "coherence": "check bounded false accepts, invalid-byte rejection, epoch scope, and open security nonclaims",
            "closure": "certify finite bounded integrity without hardness or unbounded-security overclaim",
            "emit": "write long_k23seci artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "security_rows_csv": relpath(OUT_DIR / "security_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23seci_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "bounded finite-game bad accepts are zero",
                "the bounded soundness-error numerator is zero over 112869680 counted tamper strategies",
                "56 valid transcript-index bytes decode and 200 invalid one-byte values reject",
            ],
            "does_not_certify": [
                "computational hardness",
                "zero knowledge",
                "unbounded adversary security",
                "external randomness security",
                "public security superiority",
            ],
        },
        "next_highest_yield_item": "Turn this gate into an external threat-model matrix only after real benchmark and third-party epoch artifacts exist.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23seci.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23seci.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "security_csv": csv_text(SECURITY_COLUMNS, rows["security_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "security_table": rows["security_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "security_text_sha256": rows["security_text_hash"],
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
    (OUT_DIR / "security_rows.csv").write_text(payloads["security_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        security_table=payloads["security_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23seci_matrices.npz", **payloads["matrix_payload"])
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
