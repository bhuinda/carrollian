from __future__ import annotations

import csv
import hashlib
import json
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


THEOREM_ID = "long_k23grade"
STATUS = "SECTOR33_K23_M23_LINEAR_LIFT_SUPPORT_GRADING_PROFILE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23grade.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23grade.py"
LONG_K23LIN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23lin" / "report.json"
LONG_K23LIN_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23lin" / "k23lin_matrices.npz"
LONG_HCSUPP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "report.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"

LABEL_TEXT_HASH = "94c4f463c5d95db39148387b1562a816aa8d80d7d0628c3cb9121247f889a4c1"
PROFILE_TEXT_HASH = "0584cd4dde23439a7a55c225795b0478807ba79de932684cab327c712ca7ce51"
OBS_TEXT_HASH = "4db058c362d59f792cbe37c2b912f09eff3051cad2407ae3834ed43ce2776a22"
MATRIX_SHA256 = "f2a378bd1c5fe5b388bf890928ab9407f8ab79a2423d86e7237405c1cc8a8684"

FAMILIES = [
    ("block_i", 0),
    ("rep4", 1),
    ("sign", 2),
    ("abs_coeff", 3),
    ("block_rep4", 4),
]
LABEL_COLUMNS = ["family_id", "family_code", "label_value", "support_row_count"]
PROFILE_COLUMNS = [
    "family_id",
    "generator_id",
    "label_count",
    "preserved_flag",
    "bad_group_count",
    "inside_nonzero_count",
    "leak_nonzero_count",
    "operator_nonzero_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23lin_certified_flag",
    "long_hcsupp_certified_flag",
    "support_row_count",
    "generator_count",
    "family_count",
    "label_row_count",
    "profile_row_count",
    "block_i_preserving_generator_count",
    "rep4_preserving_generator_count",
    "sign_preserving_generator_count",
    "abs_coeff_preserving_generator_count",
    "block_rep4_preserving_generator_count",
    "block_i_total_leak_nonzero_count",
    "rep4_total_leak_nonzero_count",
    "sign_total_leak_nonzero_count",
    "abs_coeff_total_leak_nonzero_count",
    "block_rep4_total_leak_nonzero_count",
    "coarse_block_partial_preservation_flag",
    "full_generator_set_preserves_block_i_flag",
    "full_generator_set_preserves_rep4_flag",
    "full_generator_set_preserves_sign_flag",
    "full_generator_set_preserves_abs_coeff_flag",
    "full_generator_set_preserves_block_rep4_flag",
    "height_projection_preservation_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def family_labels(row: dict[str, int]) -> dict[str, int]:
    sign = 1 if int(row["coefficient_signed"]) > 0 else -1
    return {
        "block_i": int(row["block_i"]),
        "rep4": int(row["rep4"]),
        "sign": sign,
        "abs_coeff": abs(int(row["coefficient_signed"])),
        "block_rep4": int(row["block_i"]) * 100 + int(row["rep4"]),
    }


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "support_intertwiners",
        "family_label_matrix",
        "profile_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23lin = load_json(LONG_K23LIN_REPORT)
    long_hcsupp = load_json(LONG_HCSUPP_REPORT)
    support_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    with np.load(LONG_K23LIN_MATRICES, allow_pickle=False) as matrices:
        support_intertwiners = np.asarray(matrices["support_intertwiners"], dtype=np.int64) % PRIME
    label_vectors: dict[str, list[int]] = {
        family_name: [family_labels(row)[family_name] for row in support_rows]
        for family_name, _ in FAMILIES
    }
    label_rows = []
    profile_rows = []
    label_matrix = []
    for family_name, family_id in FAMILIES:
        labels = label_vectors[family_name]
        label_matrix.append(labels)
        values = sorted(set(labels))
        for value in values:
            label_rows.append(
                {
                    "family_id": family_id,
                    "family_code": family_id,
                    "label_value": int(value),
                    "support_row_count": int(labels.count(value)),
                }
            )
        for generator_id in range(support_intertwiners.shape[0]):
            operator = support_intertwiners[generator_id]
            inside_nonzero = 0
            leak_nonzero = 0
            bad_group_count = 0
            for value in values:
                inside = [index for index, label in enumerate(labels) if label == value]
                outside = [index for index, label in enumerate(labels) if label != value]
                inside_count = int(np.count_nonzero(operator[np.ix_(inside, inside)]))
                leak_count = int(np.count_nonzero(operator[np.ix_(inside, outside)]))
                inside_nonzero += inside_count
                leak_nonzero += leak_count
                bad_group_count += int(leak_count > 0)
            profile_rows.append(
                {
                    "family_id": family_id,
                    "generator_id": generator_id,
                    "label_count": len(values),
                    "preserved_flag": int(leak_nonzero == 0),
                    "bad_group_count": bad_group_count,
                    "inside_nonzero_count": inside_nonzero,
                    "leak_nonzero_count": leak_nonzero,
                    "operator_nonzero_count": int(np.count_nonzero(operator)),
                }
            )
    profile_by_family = {
        family_name: [row for row in profile_rows if int(row["family_id"]) == family_id]
        for family_name, family_id in FAMILIES
    }
    obs = {
        "long_k23lin_certified_flag": int(
            long_k23lin.get("status") == "SECTOR33_K23_M23_PRIME_LINEAR_INTERTWINER_CERTIFIED"
            and long_k23lin.get("all_checks_pass") is True
        ),
        "long_hcsupp_certified_flag": int(
            long_hcsupp.get("status") == "LONG_HCSUPP_PROFILE_CERTIFIED"
            and long_hcsupp.get("all_checks_pass") is True
        ),
        "support_row_count": len(support_rows),
        "generator_count": int(support_intertwiners.shape[0]),
        "family_count": len(FAMILIES),
        "label_row_count": len(label_rows),
        "profile_row_count": len(profile_rows),
        "block_i_preserving_generator_count": sum(row["preserved_flag"] for row in profile_by_family["block_i"]),
        "rep4_preserving_generator_count": sum(row["preserved_flag"] for row in profile_by_family["rep4"]),
        "sign_preserving_generator_count": sum(row["preserved_flag"] for row in profile_by_family["sign"]),
        "abs_coeff_preserving_generator_count": sum(row["preserved_flag"] for row in profile_by_family["abs_coeff"]),
        "block_rep4_preserving_generator_count": sum(row["preserved_flag"] for row in profile_by_family["block_rep4"]),
        "block_i_total_leak_nonzero_count": sum(row["leak_nonzero_count"] for row in profile_by_family["block_i"]),
        "rep4_total_leak_nonzero_count": sum(row["leak_nonzero_count"] for row in profile_by_family["rep4"]),
        "sign_total_leak_nonzero_count": sum(row["leak_nonzero_count"] for row in profile_by_family["sign"]),
        "abs_coeff_total_leak_nonzero_count": sum(row["leak_nonzero_count"] for row in profile_by_family["abs_coeff"]),
        "block_rep4_total_leak_nonzero_count": sum(row["leak_nonzero_count"] for row in profile_by_family["block_rep4"]),
        "coarse_block_partial_preservation_flag": int(
            0 < sum(row["preserved_flag"] for row in profile_by_family["block_i"]) < int(support_intertwiners.shape[0])
        ),
        "full_generator_set_preserves_block_i_flag": int(
            sum(row["preserved_flag"] for row in profile_by_family["block_i"]) == int(support_intertwiners.shape[0])
        ),
        "full_generator_set_preserves_rep4_flag": int(
            sum(row["preserved_flag"] for row in profile_by_family["rep4"]) == int(support_intertwiners.shape[0])
        ),
        "full_generator_set_preserves_sign_flag": int(
            sum(row["preserved_flag"] for row in profile_by_family["sign"]) == int(support_intertwiners.shape[0])
        ),
        "full_generator_set_preserves_abs_coeff_flag": int(
            sum(row["preserved_flag"] for row in profile_by_family["abs_coeff"]) == int(support_intertwiners.shape[0])
        ),
        "full_generator_set_preserves_block_rep4_flag": int(
            sum(row["preserved_flag"] for row in profile_by_family["block_rep4"]) == int(support_intertwiners.shape[0])
        ),
        "height_projection_preservation_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "support_intertwiners": support_intertwiners.astype(np.int64),
        "family_label_matrix": np.asarray(label_matrix, dtype=np.int64),
        "profile_table": table_from_rows(PROFILE_COLUMNS, profile_rows),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23lin": long_k23lin,
        "long_hcsupp": long_hcsupp,
        "label_rows": label_rows,
        "profile_rows": profile_rows,
        "obs_rows": obs_rows,
        "label_table": table_from_rows(LABEL_COLUMNS, label_rows),
        "profile_table": table_from_rows(PROFILE_COLUMNS, profile_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "label_text_hash": hashlib.sha256(digest_text(LABEL_COLUMNS, label_rows).encode("ascii")).hexdigest(),
        "profile_text_hash": hashlib.sha256(digest_text(PROFILE_COLUMNS, profile_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23lin_certified_flag"],
            obs["long_hcsupp_certified_flag"],
        )
        == (1, 1),
        "shape_matches": (
            obs["support_row_count"],
            obs["generator_count"],
            obs["family_count"],
            obs["label_row_count"],
            obs["profile_row_count"],
        )
        == (56, 3, 5, 20, 15),
        "preservation_counts_match": (
            obs["block_i_preserving_generator_count"],
            obs["rep4_preserving_generator_count"],
            obs["sign_preserving_generator_count"],
            obs["abs_coeff_preserving_generator_count"],
            obs["block_rep4_preserving_generator_count"],
        )
        == (1, 0, 0, 0, 0),
        "leak_profile_matches": (
            obs["block_i_total_leak_nonzero_count"],
            obs["rep4_total_leak_nonzero_count"],
            obs["sign_total_leak_nonzero_count"],
            obs["abs_coeff_total_leak_nonzero_count"],
            obs["block_rep4_total_leak_nonzero_count"],
        )
        == (8, 329, 263, 118, 337),
        "boundary_flags_match": (
            obs["coarse_block_partial_preservation_flag"],
            obs["full_generator_set_preserves_block_i_flag"],
            obs["full_generator_set_preserves_rep4_flag"],
            obs["full_generator_set_preserves_sign_flag"],
            obs["full_generator_set_preserves_abs_coeff_flag"],
            obs["full_generator_set_preserves_block_rep4_flag"],
            obs["height_projection_preservation_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0, 0, 0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_m23_linear_lift_support_grading_profile",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the support-grading preservation profile of the prime-linear M23 lifts: coarse block preservation is partial, and the finer certified support gradings are not preserved by the full generator set.",
    }
    seam_payload = {
        "schema": "long.k23grade.seam@1",
        "status": STATUS,
        "claim": "The certified prime-linear K23 M23 intertwiners do not preserve the full sector33 support grading; only one generator preserves the coarse block_i split.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23lin": input_entry(
            LONG_K23LIN_REPORT,
            {
                "status": rows["long_k23lin"].get("status"),
                "certificate_sha256": rows["long_k23lin"].get("certificate_sha256"),
            },
        ),
        "long_k23lin_matrices": input_entry(LONG_K23LIN_MATRICES),
        "long_hcsupp": input_entry(
            LONG_HCSUPP_REPORT,
            {
                "status": rows["long_hcsupp"].get("status"),
                "certificate_sha256": rows["long_hcsupp"].get("certificate_sha256"),
            },
        ),
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23grade.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23grade certifies the sector33 support-grading profile of the prime-linear K23 M23 intertwiners.",
        "stage_protocol": {
            "draft": "read long_k23lin support intertwiners and long_hcsupp support rows",
            "witness": "emit support-label rows, generator-by-family leak profiles, observables, and matrices",
            "coherence": "check preservation counts and leakage counts for block_i, rep4, sign, absolute coefficient, and block/rep4 gradings",
            "closure": "certify the grading profile while keeping height-projection preservation open",
            "emit": "write long_k23grade artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "label_rows_csv": relpath(OUT_DIR / "label_rows.csv"),
            "profile_rows_csv": relpath(OUT_DIR / "profile_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23grade_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "one of the three certified support intertwiners preserves the coarse block_i split",
                "the full generator set does not preserve the coarse block_i split",
                "the full generator set does not preserve rep4, sign, absolute coefficient, or combined block/rep4 support grading",
                "the exact leakage counts for each grading family are emitted as finite witnesses",
            ],
            "does_not_certify": [
                "preservation or obstruction for the actual height-coherent projection layer",
                "nonexistence of a different complement choice with better grading behavior",
                "multiplication-structure preservation",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Test the certified prime-linear K23 intertwiners against the height-coherent projection inputs, especially pi_Foam33/R_hc once a materialized projection table is exposed.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23grade.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23grade.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "label_csv": csv_text(LABEL_COLUMNS, rows["label_rows"]),
        "profile_csv": csv_text(PROFILE_COLUMNS, rows["profile_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "label_table": rows["label_table"],
        "profile_table": rows["profile_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "label_text_sha256": rows["label_text_hash"],
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
    (OUT_DIR / "label_rows.csv").write_text(payloads["label_csv"], encoding="utf-8")
    (OUT_DIR / "profile_rows.csv").write_text(payloads["profile_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        label_table=payloads["label_table"],
        profile_table=payloads["profile_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23grade_matrices.npz", **payloads["matrix_payload"])
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
