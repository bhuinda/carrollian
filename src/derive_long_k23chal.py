from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23cop import (
        LONG_K23CL_MATRICES,
        LONG_K23POLY_FINGERPRINTS,
        LONG_K23POLY_MATRICES,
        LONG_K23POLY_WORDS,
        OPENING_COLUMNS,
        OUT_DIR as LONG_K23COP_DIR,
        PUBLIC_COLUMNS,
    )
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23cop import (
        LONG_K23CL_MATRICES,
        LONG_K23POLY_FINGERPRINTS,
        LONG_K23POLY_MATRICES,
        LONG_K23POLY_WORDS,
        OPENING_COLUMNS,
        OUT_DIR as LONG_K23COP_DIR,
        PUBLIC_COLUMNS,
    )
    from derive_long_k23fam import read_csv_rows
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23chal"
STATUS = "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23chal.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23chal.py"
LONG_K23COP_REPORT = LONG_K23COP_DIR / "report.json"
LONG_K23COP_PUBLIC = LONG_K23COP_DIR / "public_transcript.csv"
LONG_K23COP_OPENINGS = LONG_K23COP_DIR / "opening_rows.csv"

CHALLENGE_TEXT_HASH = "ae4727b1c988ea3bce36b7403f70c56c5994f092662a3ab30ddada5f2b4f6438"
CONTROL_TEXT_HASH = "e04baff863d3a47ff779597480a8ead35093b9a4710cedd79410e07987db25c1"
OBS_TEXT_HASH = "12755e48cf8f4fec2a417f4532ac66993a13efae7d5cfbee943e1ff7c8cdf98c"
MATRIX_SHA256 = "d1c4b2c888dd15a4ea863ebd7ea1ba41c21fd220296ccc9359f2c61d87eaf336"

CHALLENGE_COLUMNS = [
    "challenge_id",
    "transcript_id",
    "class_id",
    "selector_value_mod",
    "member_word_count",
    "selected_opening_id",
    "selected_word_id",
    "residual_class_code",
    "public_digest_sha256",
    "opening_digest_sha256",
    "source_fingerprint",
    "target_fingerprint",
    "residual_tensor_sha256",
    "accept_flag",
]
CONTROL_COLUMNS = [
    "control_id",
    "challenge_id",
    "case_type_code",
    "public_digest_check_flag",
    "opening_digest_check_flag",
    "source_match_flag",
    "target_match_flag",
    "residual_code_match_flag",
    "expected_accept_flag",
    "actual_accept_flag",
]
CHALLENGE_NUMERIC_COLUMNS = [
    "challenge_id",
    "transcript_id",
    "class_id",
    "selector_value_mod",
    "member_word_count",
    "selected_opening_id",
    "selected_word_id",
    "residual_class_code",
    "accept_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cop_certified_flag",
    "public_transcript_count",
    "opening_row_count",
    "challenge_count",
    "control_row_count",
    "accept_control_count",
    "reject_control_count",
    "failed_accept_count",
    "failed_reject_count",
    "selected_clean_challenge_count",
    "selected_defective_challenge_count",
    "selected_opening_unique_count",
    "selected_word_unique_count",
    "public_digest_unique_count",
    "opening_digest_unique_count",
    "selector_nonzero_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def tamper_hash(value: str) -> str:
    replacement = "0" if value[0] != "0" else "1"
    return replacement + value[1:]


def selector_mod(public_digest: str, member_count: int) -> int:
    if member_count <= 0:
        raise AssertionError("member count must be positive")
    return int(public_digest[:16], 16) % member_count


def control_flags(
    *,
    public_digest: str,
    opening_digest: str,
    source_hash: str,
    target_hash: str,
    residual_code: int,
    public_row: dict[str, str],
    opening_row: dict[str, str],
) -> dict[str, int]:
    flags = {
        "public_digest_check_flag": int(public_digest == public_row["public_digest_sha256"]),
        "opening_digest_check_flag": int(opening_digest == opening_row["opening_digest_sha256"]),
        "source_match_flag": int(source_hash == public_row["source_fingerprint"]),
        "target_match_flag": int(target_hash == public_row["target_fingerprint"]),
        "residual_code_match_flag": int(residual_code == int(public_row["residual_class_code"])),
    }
    flags["actual_accept_flag"] = int(all(flags.values()))
    return flags


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["challenge_numeric_table", "control_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23cop = load_json(LONG_K23COP_REPORT)
    public_rows = read_csv_rows(LONG_K23COP_PUBLIC)
    opening_rows = read_csv_rows(LONG_K23COP_OPENINGS)
    openings_by_transcript: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in opening_rows:
        openings_by_transcript[int(row["transcript_id"])].append(row)

    challenge_rows = []
    challenge_numeric_rows = []
    control_rows = []
    control_id = 0
    for challenge_id, public_row in enumerate(public_rows):
        transcript_id = int(public_row["transcript_id"])
        openings = sorted(openings_by_transcript[transcript_id], key=lambda row: int(row["opening_id"]))
        selector = selector_mod(public_row["public_digest_sha256"], len(openings))
        opening = openings[selector]
        accept_flags = control_flags(
            public_digest=public_row["public_digest_sha256"],
            opening_digest=opening["opening_digest_sha256"],
            source_hash=opening["source_matrix_sha256"],
            target_hash=opening["target_matrix_sha256"],
            residual_code=int(public_row["residual_class_code"]),
            public_row=public_row,
            opening_row=opening,
        )
        accept_flag = accept_flags["actual_accept_flag"]
        challenge_row = {
            "challenge_id": challenge_id,
            "transcript_id": transcript_id,
            "class_id": int(public_row["class_id"]),
            "selector_value_mod": selector,
            "member_word_count": int(public_row["member_word_count"]),
            "selected_opening_id": int(opening["opening_id"]),
            "selected_word_id": int(opening["word_id"]),
            "residual_class_code": int(public_row["residual_class_code"]),
            "public_digest_sha256": public_row["public_digest_sha256"],
            "opening_digest_sha256": opening["opening_digest_sha256"],
            "source_fingerprint": public_row["source_fingerprint"],
            "target_fingerprint": public_row["target_fingerprint"],
            "residual_tensor_sha256": opening["residual_tensor_sha256"],
            "accept_flag": accept_flag,
        }
        challenge_rows.append(challenge_row)
        challenge_numeric_rows.append(
            {column: challenge_row[column] for column in CHALLENGE_NUMERIC_COLUMNS}
        )

        cases = [
            (0, public_row["public_digest_sha256"], opening["opening_digest_sha256"], opening["source_matrix_sha256"], opening["target_matrix_sha256"], int(public_row["residual_class_code"]), 1),
            (1, tamper_hash(public_row["public_digest_sha256"]), opening["opening_digest_sha256"], opening["source_matrix_sha256"], opening["target_matrix_sha256"], int(public_row["residual_class_code"]), 0),
            (2, public_row["public_digest_sha256"], tamper_hash(opening["opening_digest_sha256"]), opening["source_matrix_sha256"], opening["target_matrix_sha256"], int(public_row["residual_class_code"]), 0),
            (3, public_row["public_digest_sha256"], opening["opening_digest_sha256"], tamper_hash(opening["source_matrix_sha256"]), opening["target_matrix_sha256"], int(public_row["residual_class_code"]), 0),
            (4, public_row["public_digest_sha256"], opening["opening_digest_sha256"], opening["source_matrix_sha256"], tamper_hash(opening["target_matrix_sha256"]), int(public_row["residual_class_code"]), 0),
            (5, public_row["public_digest_sha256"], opening["opening_digest_sha256"], opening["source_matrix_sha256"], opening["target_matrix_sha256"], int(public_row["residual_class_code"]) + 1, 0),
        ]
        for (
            case_type_code,
            presented_public_digest,
            presented_opening_digest,
            presented_source_hash,
            presented_target_hash,
            presented_residual_code,
            expected_accept,
        ) in cases:
            flags = control_flags(
                public_digest=presented_public_digest,
                opening_digest=presented_opening_digest,
                source_hash=presented_source_hash,
                target_hash=presented_target_hash,
                residual_code=presented_residual_code,
                public_row=public_row,
                opening_row=opening,
            )
            control_rows.append(
                {
                    "control_id": control_id,
                    "challenge_id": challenge_id,
                    "case_type_code": case_type_code,
                    "public_digest_check_flag": flags["public_digest_check_flag"],
                    "opening_digest_check_flag": flags["opening_digest_check_flag"],
                    "source_match_flag": flags["source_match_flag"],
                    "target_match_flag": flags["target_match_flag"],
                    "residual_code_match_flag": flags["residual_code_match_flag"],
                    "expected_accept_flag": expected_accept,
                    "actual_accept_flag": flags["actual_accept_flag"],
                }
            )
            control_id += 1

    obs = {
        "long_k23cop_certified_flag": int(
            long_k23cop.get("status") == "SECTOR33_K23_COMMIT_OPEN_TRANSCRIPT_CERTIFIED"
            and long_k23cop.get("all_checks_pass") is True
        ),
        "public_transcript_count": len(public_rows),
        "opening_row_count": len(opening_rows),
        "challenge_count": len(challenge_rows),
        "control_row_count": len(control_rows),
        "accept_control_count": sum(row["actual_accept_flag"] for row in control_rows),
        "reject_control_count": sum(int(row["actual_accept_flag"] == 0) for row in control_rows),
        "failed_accept_count": sum(
            int(row["expected_accept_flag"] == 1 and row["actual_accept_flag"] == 0)
            for row in control_rows
        ),
        "failed_reject_count": sum(
            int(row["expected_accept_flag"] == 0 and row["actual_accept_flag"] == 1)
            for row in control_rows
        ),
        "selected_clean_challenge_count": sum(row["accept_flag"] for row in challenge_rows if row["residual_class_code"] == 27),
        "selected_defective_challenge_count": sum(int(row["residual_class_code"] != 27) for row in challenge_rows),
        "selected_opening_unique_count": len({row["selected_opening_id"] for row in challenge_rows}),
        "selected_word_unique_count": len({row["selected_word_id"] for row in challenge_rows}),
        "public_digest_unique_count": len({row["public_digest_sha256"] for row in challenge_rows}),
        "opening_digest_unique_count": len({row["opening_digest_sha256"] for row in challenge_rows}),
        "selector_nonzero_count": sum(int(row["selector_value_mod"] != 0) for row in challenge_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    challenge_numeric_table = table_from_rows(CHALLENGE_NUMERIC_COLUMNS, challenge_numeric_rows)
    control_table = table_from_rows(CONTROL_COLUMNS, control_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "challenge_numeric_table": challenge_numeric_table.astype(np.int64),
        "control_table": control_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23cop": long_k23cop,
        "challenge_rows": challenge_rows,
        "control_rows": control_rows,
        "obs_rows": obs_rows,
        "challenge_numeric_table": challenge_numeric_table,
        "control_table": control_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "challenge_text_hash": hashlib.sha256(
            digest_text(CHALLENGE_COLUMNS, challenge_rows).encode("ascii")
        ).hexdigest(),
        "control_text_hash": hashlib.sha256(digest_text(CONTROL_COLUMNS, control_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["long_k23cop_certified_flag"] == 1,
        "challenge_profile_matches": (
            obs["public_transcript_count"],
            obs["opening_row_count"],
            obs["challenge_count"],
            obs["control_row_count"],
        )
        == (56, 91, 56, 336),
        "control_accept_reject_matches": (
            obs["accept_control_count"],
            obs["reject_control_count"],
            obs["failed_accept_count"],
            obs["failed_reject_count"],
        )
        == (56, 280, 0, 0),
        "challenge_selection_profile_matches": (
            obs["selected_clean_challenge_count"],
            obs["selected_defective_challenge_count"],
            obs["selected_opening_unique_count"],
            obs["selected_word_unique_count"],
            obs["public_digest_unique_count"],
        )
        == (1, 55, 56, 56, 56),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_verifier_challenge",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies deterministic challenge selection and accept/reject controls over the bounded commit/open transcript surface.",
    }
    seam_payload = {
        "schema": "long.k23chal.seam@1",
        "status": STATUS,
        "claim": "Every public transcript has one deterministic challenged opening, and the bounded controls reject single-field digest/hash/code tampering.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23cop": input_entry(
            LONG_K23COP_REPORT,
            {
                "status": rows["long_k23cop"].get("status"),
                "certificate_sha256": rows["long_k23cop"].get("certificate_sha256"),
            },
        ),
        "long_k23cop_public": input_entry(LONG_K23COP_PUBLIC),
        "long_k23cop_openings": input_entry(LONG_K23COP_OPENINGS),
        "long_k23poly_words": input_entry(LONG_K23POLY_WORDS),
        "long_k23poly_fingerprints": input_entry(LONG_K23POLY_FINGERPRINTS),
        "long_k23poly_matrices": input_entry(LONG_K23POLY_MATRICES),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23chal.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23chal certifies the K23 verifier-challenge layer.",
        "stage_protocol": {
            "draft": "read long_k23cop public transcripts and openings",
            "witness": "emit deterministic challenge rows, accept/reject control rows, observables, and numeric tables",
            "coherence": "check selector determinism, one challenged opening per public transcript, and reject controls",
            "closure": "certify bounded challenge acceptance while leaving randomness, repetition, and hardness claims open",
            "emit": "write long_k23chal artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "challenge_rows_csv": relpath(OUT_DIR / "challenge_rows.csv"),
            "control_rows_csv": relpath(OUT_DIR / "control_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23chal_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "one deterministic challenge row for each of the 56 public transcripts",
                "challenge selection uses the public digest modulo the transcript member count",
                "56 accepting control rows pass",
                "280 single-field tamper controls reject",
                "selected openings remain public-transcript consistent by digest, source hash, target hash, and residual code",
            ],
            "does_not_certify": [
                "probabilistic soundness under repeated random challenge",
                "hash collision resistance beyond ordinary SHA-256 use",
                "secrecy of repository-visible witness rows",
                "zero knowledge",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Bind the challenge layer back to the finite game surface: define prover moves, verifier moves, payoff labels, and transcript acceptance as a certified game table.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23chal.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23chal.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "challenge_csv": csv_text(CHALLENGE_COLUMNS, rows["challenge_rows"]),
        "control_csv": csv_text(CONTROL_COLUMNS, rows["control_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "challenge_numeric_table": rows["challenge_numeric_table"],
        "control_table": rows["control_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "challenge_text_sha256": rows["challenge_text_hash"],
            "control_text_sha256": rows["control_text_hash"],
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
    (OUT_DIR / "challenge_rows.csv").write_text(payloads["challenge_csv"], encoding="utf-8")
    (OUT_DIR / "control_rows.csv").write_text(payloads["control_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        challenge_numeric_table=payloads["challenge_numeric_table"],
        control_table=payloads["control_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23chal_matrices.npz", **payloads["matrix_payload"])
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
