from __future__ import annotations

import csv
import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/report.json"
MANIFEST_REL = "data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/manifest.json"
RAW543_REPO_REL = "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/report.json"
BRIDGE_REL = (
    "data/invariants/d20/theorems/"
    "full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge/report.json"
)
RAW543_INDEXED_REL = (
    "data/invariants/d20/theorems/"
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed/report.json"
)
LAZY63_REL = (
    "data/invariants/d20/theorems/"
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63/report.json"
)
PAIRED480_REL = (
    "data/invariants/d20/theorems/"
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480/report.json"
)
EXPECTED_STATUS = "RAW543_REPO_C2_KERNEL_AGDA_BRIDGE_DATA_CERTIFIED"
RAW_SELECTOR = "raw_componentwise_absolute_spectral_gap"
LAZY_SELECTOR = "lazy_componentwise_spectral_gap"
PAIRED_SELECTOR = "paired_lazy_componentwise_spectral_gap"


def _load_report() -> dict[str, Any]:
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    cached = cached_core_block("raw543_repo_c2_kernel_agda_bridge_data")
    if cached is not None:
        return cached
    raise FileNotFoundError("missing raw543 Agda bridge data certificate")


def _load_json_rel(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _mask_bits(mask: int, width: int = 11) -> str:
    return format(mask, f"0{width}b")[::-1]


def _selected_ids_from_bridge(bridge: dict[str, Any], selector: str) -> list[int]:
    for fiber in bridge["derived"]["selector_fibers"]:
        if fiber.get("selector") == selector:
            return [int(item) for item in fiber["selected_move_orbit_ids"]]
    raise AssertionError(f"raw543 Agda bridge missing selector fiber: {selector}")


def _selected_ids_from_report(report: dict[str, Any], key: str) -> list[int]:
    return [int(item) for item in report["derived"][key]["selected_move_orbit_ids"]]


def _expected_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    raw543_repo = _load_json_rel(RAW543_REPO_REL)
    bridge = _load_json_rel(BRIDGE_REL)
    raw_ids = _selected_ids_from_bridge(bridge, RAW_SELECTOR)
    lazy63_ids = _selected_ids_from_bridge(bridge, LAZY_SELECTOR)
    paired480_ids = _selected_ids_from_bridge(bridge, PAIRED_SELECTOR)
    lazy_index = {orbit_id: idx for idx, orbit_id in enumerate(lazy63_ids)}
    paired_index = {orbit_id: idx for idx, orbit_id in enumerate(paired480_ids)}
    orbit_rows = raw543_repo["derived"]["artifacts"]["orbit_rows"]
    if [int(row["orbit_id"]) for row in orbit_rows] != raw_ids:
        raise AssertionError("raw543 Agda bridge orbit id ordering mismatch")

    rows: list[dict[str, Any]] = []
    fixed_rows: list[dict[str, Any]] = []
    paired_rows: list[dict[str, Any]] = []
    for row in orbit_rows:
        orbit_id = int(row["orbit_id"])
        fixed = bool(row["fixed"])
        member_a = int(row["member_a"])
        member_b = int(row["member_b"])
        out = {
            "orbit_id": orbit_id,
            "agda_dynamics_id": f"d{orbit_id}",
            "agda_membership_constructor": f"rawGapMember{orbit_id}",
            "raw543_fin_index": orbit_id,
            "raw543_fin_witness": f"from_nat_prime(543,{orbit_id})",
            "bucket": "lazy63_fixed" if fixed else "paired480_two_cycle",
            "bucket_index": lazy_index.get(orbit_id, paired_index.get(orbit_id)),
            "lazy63_index": lazy_index.get(orbit_id),
            "paired480_index": paired_index.get(orbit_id),
            "orbit_size": int(row["size"]),
            "fixed": fixed,
            "representative_mask": int(row["representative"]),
            "member_a_mask": member_a,
            "member_b_mask": member_b,
            "member_a_bits_lsb_first": _mask_bits(member_a),
            "member_b_bits_lsb_first": _mask_bits(member_b),
        }
        rows.append(out)
        if fixed:
            fixed_rows.append(out)
        else:
            paired_rows.append(out)

    by_id = {int(row["orbit_id"]): row for row in rows}
    vectors = {
        "raw543_orbit_ids": raw_ids,
        "fixed63_orbit_ids": [int(row["orbit_id"]) for row in fixed_rows],
        "paired480_orbit_ids": [int(row["orbit_id"]) for row in paired_rows],
        "lazy63_selected_ids": lazy63_ids,
        "paired480_selected_ids": paired480_ids,
        "agda_raw543_fin_indices": {
            str(orbit_id): int(by_id[orbit_id]["raw543_fin_index"]) for orbit_id in raw_ids
        },
        "actual_orbit_masks": {
            str(orbit_id): {
                "member_a": int(by_id[orbit_id]["member_a_mask"]),
                "member_b": int(by_id[orbit_id]["member_b_mask"]),
                "fixed": bool(by_id[orbit_id]["fixed"]),
            }
            for orbit_id in raw_ids
        },
    }
    return rows, fixed_rows, paired_rows, vectors


def _read_bridge_csv(rel_path: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with (ROOT / rel_path).open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            parsed = {
                "orbit_id": int(row["orbit_id"]),
                "agda_dynamics_id": row["agda_dynamics_id"],
                "agda_membership_constructor": row["agda_membership_constructor"],
                "raw543_fin_index": int(row["raw543_fin_index"]),
                "raw543_fin_witness": row["raw543_fin_witness"],
                "bucket": row["bucket"],
                "bucket_index": int(row["bucket_index"]),
                "lazy63_index": int(row["lazy63_index"]) if row["lazy63_index"] else None,
                "paired480_index": int(row["paired480_index"]) if row["paired480_index"] else None,
                "orbit_size": int(row["orbit_size"]),
                "fixed": row["fixed"] == "True",
                "representative_mask": int(row["representative_mask"]),
                "member_a_mask": int(row["member_a_mask"]),
                "member_b_mask": int(row["member_b_mask"]),
                "member_a_bits_lsb_first": row["member_a_bits_lsb_first"],
                "member_b_bits_lsb_first": row["member_b_bits_lsb_first"],
            }
            out.append(parsed)
    return out


def _validate_input(path_key: str, expected_rel: str, report: dict[str, Any]) -> None:
    row = report.get("inputs", {}).get(path_key, {})
    if row.get("path") != expected_rel:
        raise AssertionError(f"raw543 Agda bridge input path mismatch: {path_key}")
    if h_file(ROOT / expected_rel) != row.get("sha256"):
        raise AssertionError(f"raw543 Agda bridge input hash mismatch: {path_key}")


def validate_raw543_repo_c2_kernel_agda_bridge_data() -> Dict[str, Any]:
    rec = _load_report()
    if rec.get("status") != EXPECTED_STATUS:
        raise AssertionError("raw543 Agda bridge status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("raw543 Agda bridge checks did not pass")

    _validate_input("raw543_repo_c2_kernel_action_report", RAW543_REPO_REL, rec)
    _validate_input("c2_univalent_foundation_bridge_report", BRIDGE_REL, rec)
    _validate_input("raw543_indexed_report", RAW543_INDEXED_REL, rec)
    _validate_input("lazy63_report", LAZY63_REL, rec)
    _validate_input("paired480_report", PAIRED480_REL, rec)

    raw543_repo = _load_json_rel(RAW543_REPO_REL)
    bridge = _load_json_rel(BRIDGE_REL)
    raw543_indexed = _load_json_rel(RAW543_INDEXED_REL)
    lazy63 = _load_json_rel(LAZY63_REL)
    paired480 = _load_json_rel(PAIRED480_REL)
    if raw543_repo.get("status") != "RAW543_REPO_C2_KERNEL_ACTION_CERTIFIED":
        raise AssertionError("raw543 Agda bridge source action status mismatch")
    if bridge.get("status") != "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_CERTIFIED":
        raise AssertionError("raw543 Agda bridge univalent report status mismatch")
    if raw543_indexed.get("status") != "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED":
        raise AssertionError("raw543 Agda bridge indexed report status mismatch")
    if lazy63.get("status") != "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_CERTIFIED":
        raise AssertionError("raw543 Agda bridge lazy63 report status mismatch")
    if paired480.get("status") != "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_CERTIFIED":
        raise AssertionError("raw543 Agda bridge paired480 report status mismatch")

    expected_rows, expected_fixed, expected_paired, expected_vectors = _expected_rows()
    manifest = _load_json_rel(MANIFEST_REL)
    artifacts = manifest.get("artifacts", {})
    expected_artifacts = {
        "bridge_csv": "data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/actual_raw543_agda_orbit_bridge.csv",
        "fixed63_csv": "data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/actual_raw543_agda_fixed63.csv",
        "paired480_csv": "data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/actual_raw543_agda_paired480.csv",
        "bridge_vectors": "data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/actual_raw543_agda_bridge_vectors.json",
    }
    if artifacts != expected_artifacts:
        raise AssertionError("raw543 Agda bridge manifest artifact path mismatch")

    actual_rows = _read_bridge_csv(expected_artifacts["bridge_csv"])
    actual_fixed = _read_bridge_csv(expected_artifacts["fixed63_csv"])
    actual_paired = _read_bridge_csv(expected_artifacts["paired480_csv"])
    actual_vectors = _load_json_rel(expected_artifacts["bridge_vectors"])
    if actual_rows != expected_rows:
        raise AssertionError("raw543 Agda bridge rows mismatch")
    if actual_fixed != expected_fixed:
        raise AssertionError("raw543 Agda bridge fixed63 rows mismatch")
    if actual_paired != expected_paired:
        raise AssertionError("raw543 Agda bridge paired480 rows mismatch")
    if actual_vectors != expected_vectors:
        raise AssertionError("raw543 Agda bridge vector payload mismatch")

    derived = rec.get("derived", {})
    ids = derived.get("ids", {})
    if ids.get("raw543_orbit_ids") != list(range(543)):
        raise AssertionError("raw543 Agda bridge raw ids mismatch")
    if ids.get("fixed63_orbit_ids") != ids.get("lazy63_selected_ids"):
        raise AssertionError("raw543 Agda bridge fixed/lazy ids mismatch")
    if ids.get("paired480_orbit_ids") != ids.get("paired480_selected_ids"):
        raise AssertionError("raw543 Agda bridge paired ids mismatch")
    summary = derived.get("summary", {})
    if summary.get("raw543_orbit_count") != 543:
        raise AssertionError("raw543 Agda bridge raw count mismatch")
    if summary.get("fixed63_orbit_count") != 63:
        raise AssertionError("raw543 Agda bridge fixed count mismatch")
    if summary.get("paired480_two_cycle_orbit_count") != 480:
        raise AssertionError("raw543 Agda bridge paired count mismatch")

    hashes = derived.get("hashes", {})
    if hashes.get("bridge_rows_sha256") != h_json(expected_rows):
        raise AssertionError("raw543 Agda bridge row hash mismatch")
    if hashes.get("fixed63_rows_sha256") != h_json(expected_fixed):
        raise AssertionError("raw543 Agda bridge fixed hash mismatch")
    if hashes.get("paired480_rows_sha256") != h_json(expected_paired):
        raise AssertionError("raw543 Agda bridge paired hash mismatch")
    if hashes.get("vector_payload_sha256") != h_json(expected_vectors):
        raise AssertionError("raw543 Agda bridge vector hash mismatch")

    for key, rel_path in expected_artifacts.items():
        if h_file(ROOT / rel_path) != manifest.get("artifact_hashes", {}).get(key):
            raise AssertionError(f"raw543 Agda bridge artifact hash mismatch: {key}")
    if manifest.get("report_sha256") != rec.get("certificate_sha256"):
        raise AssertionError("raw543 Agda bridge manifest report hash mismatch")
    tmp_manifest = dict(manifest)
    tmp_manifest.pop("manifest_sha256", None)
    if h_json(tmp_manifest) != manifest.get("manifest_sha256"):
        raise AssertionError("raw543 Agda bridge manifest self hash mismatch")

    checks = rec.get("checks", {})
    for key, value in checks.items():
        if value is not True:
            raise AssertionError(f"raw543 Agda bridge check failed: {key}")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != rec.get("certificate_sha256"):
        raise AssertionError("raw543 Agda bridge self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_raw543_repo_c2_kernel_agda_bridge_data()
    print(rec["status"])
    print(rec["certificate_sha256"])
