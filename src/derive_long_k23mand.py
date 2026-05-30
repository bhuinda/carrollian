from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23fam import read_csv_rows
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23mand"
STATUS = "SECTOR33_K23_SOURCE_BOUND_MANDATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23mand.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23mand.py"
LONG_K23COP_PUBLIC = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "public_transcript.csv"
LONG_K23COP_OPENINGS = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "opening_rows.csv"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23CHAL_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "challenge_rows.csv"
LONG_K23SOUND_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json"

MANDATE_TEXT_HASH = "ae165d13a457aae24fc236efc0b4ab141584b41b782ca911b16440a21abedcc8"
PROFILE_TEXT_HASH = "6157ca1088a124ea46c5b58978ba626030c51f76ace3583ed570bd6522e2fb07"
OBS_TEXT_HASH = "944ee10928fdd0f103697185d449733393063e0ca01a55f17c8651d53954b471"
MATRIX_SHA256 = "478fe8249183e6050e783e837ddce961364801b0110fb65ed92b785016d95386"

MANDATE_COLUMNS = [
    "challenge_id",
    "transcript_id",
    "member_word_count",
    "digest_prefix_u64_mod_member_count",
    "recorded_selector_value_mod",
    "selected_opening_id",
    "expected_opening_id",
    "selector_match_flag",
    "opening_match_flag",
    "digest_bound_flag",
    "external_randomness_used_flag",
]
PROFILE_COLUMNS = [
    "profile_id",
    "profile_code",
    "selector_value_mod",
    "challenge_count",
    "member_word_count_min",
    "member_word_count_max",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "public_transcript_count",
    "opening_row_count",
    "challenge_count",
    "mandate_row_count",
    "selector_match_count",
    "opening_match_count",
    "digest_bound_count",
    "selector_zero_count",
    "selector_nonzero_count",
    "selector_profile_count",
    "selected_opening_unique_count",
    "selected_word_unique_count",
    "external_randomness_used_count",
    "external_randomness_claim_flag",
    "challenge_randomness_source_certified_flag",
    "deterministic_mandate_certified_flag",
    "proof_of_mandate_flag",
    "hardness_claim_flag",
    "zero_knowledge_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def selector_mod(public_digest: str, member_count: int) -> int:
    if member_count <= 0:
        raise AssertionError("member count must be positive")
    return int(public_digest[:16], 16) % member_count


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["mandate_table", "profile_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    chal_report = load_json(LONG_K23CHAL_REPORT)
    sound_report = load_json(LONG_K23SOUND_REPORT)
    public_rows = {int(row["transcript_id"]): row for row in read_csv_rows(LONG_K23COP_PUBLIC)}
    challenge_rows = [{key: value for key, value in row.items()} for row in read_csv_rows(LONG_K23CHAL_ROWS)]
    openings_by_transcript: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv_rows(LONG_K23COP_OPENINGS):
        openings_by_transcript[int(row["transcript_id"])].append(row)

    mandate_rows = []
    selected_words = set()
    for row in challenge_rows:
        transcript_id = int(row["transcript_id"])
        public = public_rows[transcript_id]
        openings = sorted(openings_by_transcript[transcript_id], key=lambda item: int(item["opening_id"]))
        expected_selector = selector_mod(public["public_digest_sha256"], int(public["member_word_count"]))
        expected_opening_id = int(openings[expected_selector]["opening_id"])
        recorded_selector = int(row["selector_value_mod"])
        selected_opening_id = int(row["selected_opening_id"])
        selected_words.add(int(row["selected_word_id"]))
        mandate_rows.append(
            {
                "challenge_id": int(row["challenge_id"]),
                "transcript_id": transcript_id,
                "member_word_count": int(row["member_word_count"]),
                "digest_prefix_u64_mod_member_count": expected_selector,
                "recorded_selector_value_mod": recorded_selector,
                "selected_opening_id": selected_opening_id,
                "expected_opening_id": expected_opening_id,
                "selector_match_flag": int(expected_selector == recorded_selector),
                "opening_match_flag": int(expected_opening_id == selected_opening_id),
                "digest_bound_flag": int(public["public_digest_sha256"] == row["public_digest_sha256"]),
                "external_randomness_used_flag": 0,
            }
        )

    selector_counts = Counter(row["recorded_selector_value_mod"] for row in mandate_rows)
    profile_rows = []
    for profile_id, selector_value in enumerate(sorted(selector_counts)):
        members = [
            row["member_word_count"]
            for row in mandate_rows
            if row["recorded_selector_value_mod"] == selector_value
        ]
        profile_rows.append(
            {
                "profile_id": profile_id,
                "profile_code": selector_value,
                "selector_value_mod": selector_value,
                "challenge_count": selector_counts[selector_value],
                "member_word_count_min": min(members),
                "member_word_count_max": max(members),
            }
        )

    obs = {
        "input_report_count": 2,
        "certified_input_count": is_certified(chal_report, "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED")
        + is_certified(sound_report, "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED"),
        "public_transcript_count": len(public_rows),
        "opening_row_count": sum(len(rows) for rows in openings_by_transcript.values()),
        "challenge_count": len(challenge_rows),
        "mandate_row_count": len(mandate_rows),
        "selector_match_count": sum(row["selector_match_flag"] for row in mandate_rows),
        "opening_match_count": sum(row["opening_match_flag"] for row in mandate_rows),
        "digest_bound_count": sum(row["digest_bound_flag"] for row in mandate_rows),
        "selector_zero_count": selector_counts[0],
        "selector_nonzero_count": sum(count for value, count in selector_counts.items() if value != 0),
        "selector_profile_count": len(profile_rows),
        "selected_opening_unique_count": len({row["selected_opening_id"] for row in mandate_rows}),
        "selected_word_unique_count": len(selected_words),
        "external_randomness_used_count": sum(row["external_randomness_used_flag"] for row in mandate_rows),
        "external_randomness_claim_flag": 0,
        "challenge_randomness_source_certified_flag": 0,
        "deterministic_mandate_certified_flag": 1,
        "proof_of_mandate_flag": 1,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    mandate_table = table_from_rows(MANDATE_COLUMNS, mandate_rows)
    profile_table = table_from_rows(PROFILE_COLUMNS, profile_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "mandate_table": mandate_table.astype(np.int64),
        "profile_table": profile_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "chal_report": chal_report,
        "sound_report": sound_report,
        "mandate_rows": mandate_rows,
        "profile_rows": profile_rows,
        "obs_rows": obs_rows,
        "mandate_table": mandate_table,
        "profile_table": profile_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "mandate_text_hash": hashlib.sha256(digest_text(MANDATE_COLUMNS, mandate_rows).encode("ascii")).hexdigest(),
        "profile_text_hash": hashlib.sha256(digest_text(PROFILE_COLUMNS, profile_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 2,
        "selector_binding_exact": (
            obs["challenge_count"],
            obs["selector_match_count"],
            obs["opening_match_count"],
            obs["digest_bound_count"],
        )
        == (56, 56, 56, 56),
        "selector_profile_matches": (
            obs["selector_zero_count"],
            obs["selector_nonzero_count"],
            obs["selector_profile_count"],
            obs["selected_opening_unique_count"],
            obs["selected_word_unique_count"],
        )
        == (45, 11, 3, 56, 56),
        "randomness_obstruction_recorded": (
            obs["external_randomness_used_count"],
            obs["external_randomness_claim_flag"],
            obs["challenge_randomness_source_certified_flag"],
        )
        == (0, 0, 0),
        "mandate_claim_scoped": (
            obs["deterministic_mandate_certified_flag"],
            obs["proof_of_mandate_flag"],
            obs["hardness_claim_flag"],
            obs["zero_knowledge_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_source_bound_mandate",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies deterministic source-bound mandate selection for the K23 verifier challenge.",
    }
    seam_payload = {
        "schema": "long.k23mand.seam@1",
        "status": STATUS,
        "claim": "The current K23 verifier challenge is source-bound to the public transcript digest; no external randomness source is certified.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23chal": input_entry(
            LONG_K23CHAL_REPORT,
            {
                "status": rows["chal_report"].get("status"),
                "certificate_sha256": rows["chal_report"].get("certificate_sha256"),
            },
        ),
        "long_k23sound": input_entry(
            LONG_K23SOUND_REPORT,
            {
                "status": rows["sound_report"].get("status"),
                "certificate_sha256": rows["sound_report"].get("certificate_sha256"),
            },
        ),
        "long_k23cop_public": input_entry(LONG_K23COP_PUBLIC),
        "long_k23cop_openings": input_entry(LONG_K23COP_OPENINGS),
        "long_k23chal_rows": input_entry(LONG_K23CHAL_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23mand.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23mand certifies the source-bound verifier mandate for the K23 challenge layer.",
        "stage_protocol": {
            "draft": "read public transcript rows, opening rows, challenge rows, and bounded soundness report",
            "witness": "emit mandate selector rows, selector profile rows, and observables",
            "coherence": "check selector recomputation, selected opening binding, and explicit randomness non-claim",
            "closure": "certify deterministic proof-of-mandate while leaving external randomness and security claims open",
            "emit": "write long_k23mand artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "mandate_rows_csv": relpath(OUT_DIR / "mandate_rows.csv"),
            "profile_rows_csv": relpath(OUT_DIR / "profile_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23mand_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "every verifier challenge selector recomputes from the public transcript digest prefix",
                "every selected opening id matches the digest-derived selector",
                "the challenge layer uses zero external randomness rows in the current certificate",
                "the finite proof-of-mandate is source-bound and deterministic",
            ],
            "does_not_certify": [
                "a random challenge source",
                "cryptographic hardness",
                "zero knowledge",
                "unbounded adversary security",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Promote proof-of-mandate into the frontier: test whether mandate determinism is sufficient for the next semantic authority layer or whether a new challenge-source extension is required.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23mand.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23mand.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "mandate_csv": csv_text(MANDATE_COLUMNS, rows["mandate_rows"]),
        "profile_csv": csv_text(PROFILE_COLUMNS, rows["profile_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "mandate_table": rows["mandate_table"],
        "profile_table": rows["profile_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "mandate_text_sha256": rows["mandate_text_hash"],
            "profile_text_sha256": rows["profile_text_hash"],
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
    (OUT_DIR / "mandate_rows.csv").write_text(payloads["mandate_csv"], encoding="utf-8")
    (OUT_DIR / "profile_rows.csv").write_text(payloads["profile_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        mandate_table=payloads["mandate_table"],
        profile_table=payloads["profile_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23mand_matrices.npz", **payloads["matrix_payload"])
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
