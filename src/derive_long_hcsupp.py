from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
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


THEOREM_ID = "long_hcsupp"
STATUS = "LONG_HCSUPP_PROFILE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcsupp.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcsupp.py"
E33_ENTRIES = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "e33_full_corrected_transport"
    / "e33_vector_entries.csv"
)
E33_CERT = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "e33_full_corrected_transport"
    / "e33_full_corrected_transport_certificate.json"
)
RELATION_MEMBERSHIPS = ROOT / "data" / "raw" / "relation_memberships.npz"
SECTOR33_UNIQUE = D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
LONG_HCSCALAR_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcscalar" / "report.json"
LONG_HCSHAPE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcshape" / "report.json"

SUPPORT_TEXT_HASH = "17ace265fa58aa0f60ea57c58d7a3778936f86b687b58752b4a5b42376e6f698"
PROFILE_TEXT_HASH = "986a6a5523055d6915a6a87130c0a3aeac041eebb58562dd4ff39754f3a4d4fc"
OBS_TEXT_HASH = "6993eec5d1e783ad9db623a6fc101ef27cadf8db636a1fb28a71e7f9f25edf2e"
SUPPORT_TABLE_SHA256 = "c42256881fb73135503585c7f0d4187e2f63d6a37d9d238e4db00cb360884140"

SUPPORT_COLUMNS = [
    "row_id",
    "relation_id",
    "coefficient_mod",
    "coefficient_signed",
    "block_i",
    "block_j",
    "rep0",
    "rep1",
    "rep2",
    "rep3",
    "rep4",
    "rep2_object",
    "rep3_object",
]
PROFILE_COLUMNS = [
    "profile_id",
    "block_i",
    "block_j",
    "support_count",
    "positive_count",
    "negative_count",
    "signed_sum",
    "abs_sum",
    "distinct_coefficient_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "e33_support",
    "e33_positive_count",
    "e33_negative_count",
    "e33_signed_sum",
    "raw_block_profile_count",
    "bplus_block_support",
    "splus_block_support",
    "sector33_profile_support",
    "sector33_public_zero_flag",
    "sector33_q42_nonzero_count",
    "sector33_q12_nonzero_count",
    "sector33_pre_idempotent_support_size",
    "sector33_bplus_local_pre_idempotent",
    "sector33_splus_local_pre_idempotent",
    "e33_reconstruction_bplus_candidate",
    "e33_reconstruction_splus_candidate",
    "abstract_domain_dimension",
    "abstract_visible_count",
    "abstract_twoform_count",
    "abstract_hidden_pair_count",
    "abstract_candidate_rank",
    "abstract_candidate_kernel_dimension",
    "relation_support_table_materialized_flag",
    "relation_to_lambda3_binding_materialized_flag",
    "block_counts_match_abstract_partition_flag",
    "count_only_binding_possible_flag",
    "focused_hcsupp_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def read_e33_rows() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with E33_ENTRIES.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def joined_support_rows() -> list[dict[str, int]]:
    e33_rows = read_e33_rows()
    membership = np.load(RELATION_MEMBERSHIPS, allow_pickle=False)
    block_i = np.asarray(membership["block_i"], dtype=np.int64)
    block_j = np.asarray(membership["block_j"], dtype=np.int64)
    reps = np.asarray(membership["reps"], dtype=np.int64)
    object_of_point = np.asarray(membership["object_of_point"], dtype=np.int64)
    rows: list[dict[str, int]] = []
    for row_id, row in enumerate(e33_rows):
        relation_id = row["relation_id"]
        rep = reps[relation_id]
        rows.append(
            {
                "row_id": row_id,
                "relation_id": relation_id,
                "coefficient_mod": row["coefficient_mod"],
                "coefficient_signed": row["coefficient_signed"],
                "block_i": int(block_i[relation_id]),
                "block_j": int(block_j[relation_id]),
                "rep0": int(rep[0]),
                "rep1": int(rep[1]),
                "rep2": int(rep[2]),
                "rep3": int(rep[3]),
                "rep4": int(rep[4]),
                "rep2_object": int(object_of_point[int(rep[2])]),
                "rep3_object": int(object_of_point[int(rep[3])]),
            }
        )
    return rows


def profile_rows(support_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    groups: dict[tuple[int, int], list[dict[str, int]]] = defaultdict(list)
    for row in support_rows:
        groups[(row["block_i"], row["block_j"])].append(row)
    rows: list[dict[str, int]] = []
    for profile_id, key in enumerate(sorted(groups)):
        entries = groups[key]
        coeffs = [row["coefficient_signed"] for row in entries]
        rows.append(
            {
                "profile_id": profile_id,
                "block_i": key[0],
                "block_j": key[1],
                "support_count": len(entries),
                "positive_count": sum(value > 0 for value in coeffs),
                "negative_count": sum(value < 0 for value in coeffs),
                "signed_sum": sum(coeffs),
                "abs_sum": sum(abs(value) for value in coeffs),
                "distinct_coefficient_count": len(set(coeffs)),
            }
        )
    return rows


def sector33_profile(unique_report: dict[str, Any]) -> dict[str, Any]:
    rows = unique_report.get("derived", {}).get("sector_rows", [])
    for row in rows:
        if row.get("sector") == 33:
            return row
    raise ValueError("sector 33 profile not found")


def build_rows() -> dict[str, Any]:
    e33_cert = load_json(E33_CERT)
    unique_report = load_json(SECTOR33_UNIQUE)
    hcscalar = load_json(LONG_HCSCALAR_REPORT)
    hcshape = load_json(LONG_HCSHAPE_REPORT)
    support_rows = joined_support_rows()
    profiles = profile_rows(support_rows)
    profile_by_block = {(row["block_i"], row["block_j"]): row for row in profiles}
    sector33 = sector33_profile(unique_report)
    local_keys = sector33.get("local_pre_idempotent_keys", [])
    summary = hcshape.get("witness", {}).get("summary", {})
    scalar_summary = hcscalar.get("witness", {}).get("summary", {})
    abstract_counts = sorted(
        [
            int(summary.get("visible_triple_count", -1)),
            int(summary.get("copy0_twoform_count", -1)) + int(summary.get("copy1_twoform_count", -1)),
            int(summary.get("hidden_pair_h6_count", -1)),
        ]
    )
    relation_counts = sorted(row["support_count"] for row in profiles)
    obs = {
        "e33_support": len(support_rows),
        "e33_positive_count": sum(row["coefficient_signed"] > 0 for row in support_rows),
        "e33_negative_count": sum(row["coefficient_signed"] < 0 for row in support_rows),
        "e33_signed_sum": sum(row["coefficient_signed"] for row in support_rows),
        "raw_block_profile_count": len(profiles),
        "bplus_block_support": profile_by_block[(1, 1)]["support_count"],
        "splus_block_support": profile_by_block[(5, 5)]["support_count"],
        "sector33_profile_support": int(sector33.get("vector", {}).get("support", -1)),
        "sector33_public_zero_flag": int(bool(sector33.get("public_zero"))),
        "sector33_q42_nonzero_count": int(sector33.get("q42_nonzero_count", -1)),
        "sector33_q12_nonzero_count": int(sector33.get("q12_nonzero_count", -1)),
        "sector33_pre_idempotent_support_size": int(sector33.get("pre_idempotent_support_size", -1)),
        "sector33_bplus_local_pre_idempotent": int(local_keys[0][1]),
        "sector33_splus_local_pre_idempotent": int(local_keys[1][1]),
        "e33_reconstruction_bplus_candidate": int(e33_cert.get("e33", {}).get("B_plus_local_candidate", -1)),
        "e33_reconstruction_splus_candidate": int(e33_cert.get("e33", {}).get("S_plus_local_candidate", -1)),
        "abstract_domain_dimension": int(summary.get("lambda3_a8_dimension", -1)),
        "abstract_visible_count": int(summary.get("visible_triple_count", -1)),
        "abstract_twoform_count": int(summary.get("copy0_twoform_count", -1)) + int(summary.get("copy1_twoform_count", -1)),
        "abstract_hidden_pair_count": int(summary.get("hidden_pair_h6_count", -1)),
        "abstract_candidate_rank": int(scalar_summary.get("candidate_projection_rank", -1)),
        "abstract_candidate_kernel_dimension": int(scalar_summary.get("candidate_kernel_dimension", -1)),
        "relation_support_table_materialized_flag": 1,
        "relation_to_lambda3_binding_materialized_flag": 0,
        "block_counts_match_abstract_partition_flag": int(relation_counts == abstract_counts),
        "count_only_binding_possible_flag": int(relation_counts == abstract_counts),
        "focused_hcsupp_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    return {
        "e33_cert": e33_cert,
        "unique_report": unique_report,
        "hcscalar": hcscalar,
        "hcshape": hcshape,
        "sector33": sector33,
        "support_rows": support_rows,
        "profile_rows": profiles,
        "obs_rows": obs_rows,
        "support_table": table_from_rows(SUPPORT_COLUMNS, support_rows),
        "profile_table": table_from_rows(PROFILE_COLUMNS, profiles),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "obs": obs,
        "coefficient_counter": {
            str(key): value
            for key, value in sorted(Counter(row["coefficient_signed"] for row in support_rows).items())
        },
        "support_text_hash": hashlib.sha256(digest_text(SUPPORT_COLUMNS, support_rows).encode("ascii")).hexdigest(),
        "profile_text_hash": hashlib.sha256(digest_text(PROFILE_COLUMNS, profiles).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
        "support_table_sha256": sha_array(table_from_rows(SUPPORT_COLUMNS, support_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    sector33 = rows["sector33"]
    checks = {
        "e33_input_is_certified": rows["e33_cert"].get("status") == "E33_VECTOR_AND_ALL_CORRECTED_TRANSPORTS_CERTIFIED",
        "unique_sector33_input_is_certified": rows["unique_report"].get("status") == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED" and rows["unique_report"].get("all_checks_pass") is True,
        "abstract_scalar_input_passes": rows["hcscalar"].get("status") == "LONG_HCSCALAR_ABSTRACT_COMPLETION_CERTIFIED" and rows["hcscalar"].get("all_checks_pass") is True,
        "support_join_has_expected_size_and_sign_split": (
            obs["e33_support"],
            obs["e33_positive_count"],
            obs["e33_negative_count"],
            obs["e33_signed_sum"],
        )
        == (56, 28, 28, 0),
        "support_rows_are_active_closed_loop_blocks": (
            obs["raw_block_profile_count"],
            obs["bplus_block_support"],
            obs["splus_block_support"],
        )
        == (2, 12, 44),
        "support_profile_matches_sector33": (
            sector33.get("active_objects"),
            sector33.get("object_loop_coordinate_support"),
            obs["sector33_profile_support"],
            obs["sector33_q42_nonzero_count"],
            obs["sector33_q12_nonzero_count"],
        )
        == (["B+", "S+"], [0, 12, 0, 0, 0, 44], 56, 0, 0),
        "abstract_candidate_remains_rank33_kernel23": (
            obs["abstract_domain_dimension"],
            obs["abstract_candidate_rank"],
            obs["abstract_candidate_kernel_dimension"],
        )
        == (56, 33, 23),
        "count_only_binding_is_rejected": (
            obs["abstract_visible_count"],
            obs["abstract_twoform_count"],
            obs["abstract_hidden_pair_count"],
            obs["block_counts_match_abstract_partition_flag"],
            obs["count_only_binding_possible_flag"],
            obs["relation_to_lambda3_binding_materialized_flag"],
        )
        == (20, 30, 6, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_relation_support_profile",
        "summary": obs,
        "sector33_local_pre_idempotent_keys": sector33.get("local_pre_idempotent_keys"),
        "coefficient_counter": rows["coefficient_counter"],
        "support_table_sha256": rows["support_table_sha256"],
        "boundary": "This certifies the relation-row support profile of e33, not a relation-row to Lambda3(A2+H6) basis binding.",
    }
    seam_payload = {
        "schema": "long.hcsupp.seam@1",
        "status": STATUS,
        "claim": "The e33 relation support is source-bound as a two-block closed-loop profile, 12 rows on B+ and 44 rows on S+, matching the unique public-zero sector profile and not matching the abstract 20+30+6 projection partition by counts alone.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "e33_entries": input_entry(E33_ENTRIES),
        "e33_certificate": input_entry(E33_CERT, {"status": rows["e33_cert"].get("status"), "certificate_sha256": rows["e33_cert"].get("certificate_sha256")}),
        "relation_memberships": input_entry(RELATION_MEMBERSHIPS),
        "sector33_unique_public_zero": input_entry(SECTOR33_UNIQUE, {"status": rows["unique_report"].get("status"), "certificate_sha256": rows["unique_report"].get("certificate_sha256")}),
        "long_hcscalar": input_entry(LONG_HCSCALAR_REPORT, {"status": rows["hcscalar"].get("status"), "certificate_sha256": rows["hcscalar"].get("certificate_sha256")}),
        "long_hcshape": input_entry(LONG_HCSHAPE_REPORT, {"status": rows["hcshape"].get("status"), "certificate_sha256": rows["hcshape"].get("certificate_sha256")}),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcsupp.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_hcsupp certifies the current source-bound e33 relation-support profile and marks the relation-row to Lambda3(A2+H6) basis binding as still open.",
        "stage_protocol": {
            "draft": "read e33 vector rows, raw relation memberships, sector33 public-zero profile, and long_hcscalar",
            "witness": "emit joined 56-row support table, two-block profile table, and observable counts",
            "coherence": "check support count, sign split, raw closed-loop blocks, sector33 object-loop profile, and abstract partition mismatch",
            "closure": "certify the support profile without claiming a pi_Foam33 relation-row binding",
            "emit": "write long_hcsupp artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "support_rows_csv": relpath(OUT_DIR / "support_rows.csv"),
            "profile_csv": relpath(OUT_DIR / "profile.csv"),
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
                "the materialized e33 support has 56 relation rows with 28 positive and 28 negative signed entries",
                "all support rows lie in the active closed-loop blocks B+->B+ and S+->S+",
                "the raw block profile is 12 B+ rows and 44 S+ rows, matching the sector33 object-loop support profile",
                "the abstract 20+30+6 Lambda3(A2+H6) partition cannot by itself be identified with the raw 12+44 relation profile",
            ],
            "does_not_certify": [
                "the relation-row to Lambda3(A2+H6) basis binding",
                "the actual pi_Foam33 relation-support projection table",
                "a materialized R_hc generator family",
                "the full matrix intertwining equation",
            ],
        },
        "next_highest_yield_item": "Reconstruct or expose the local center-basis expansion for the sector33 B+ and S+ pre-idempotents, then use it to bind the 56 relation rows to the abstract Lambda3(A2+H6) basis.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.hcsupp.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {"schema": "long.hcsupp.manifest@1", "name": THEOREM_ID, "status": STATUS, "inputs": inputs, "outputs": report["outputs"], "report_sha256": report["certificate_sha256"]}
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "support_csv": csv_text(SUPPORT_COLUMNS, rows["support_rows"]),
        "profile_csv": csv_text(PROFILE_COLUMNS, rows["profile_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "support_table": rows["support_table"],
        "profile_table": rows["profile_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "support_text_sha256": rows["support_text_hash"],
            "profile_text_sha256": rows["profile_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "support_table_sha256": rows["support_table_sha256"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [row for row in index_payload.get("obligations", []) if isinstance(row, dict) and row.get("id") != THEOREM_ID]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append({"id": THEOREM_ID, "manifest": relpath(OUT_DIR / "manifest.json"), "report": relpath(OUT_DIR / "report.json"), "report_sha256": report["certificate_sha256"], "status": report["status"]})
    obligations.sort(key=lambda row: str(row["id"]))
    index = {"schema": schema, "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT", "obligation_count": len(obligations), "obligations": obligations}
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "support_rows.csv").write_text(payloads["support_csv"], encoding="utf-8")
    (OUT_DIR / "profile.csv").write_text(payloads["profile_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(OUT_DIR / "tables.npz", support_table=payloads["support_table"], profile_table=payloads["profile_table"], observable_table=payloads["observable_table"])
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
