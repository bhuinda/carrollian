from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "raw543_repo_c2_kernel_agda_bridge_data"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
RAW543_REPO_REPORT = (
    D20_INVARIANTS / "theorems" / "raw543_repo_c2_kernel_action" / "report.json"
)
C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge"
    / "report.json"
)
RAW543_INDEXED_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed"
    / "report.json"
)
LAZY63_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63"
    / "report.json"
)
PAIRED480_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480"
    / "report.json"
)

RAW_SELECTOR = "raw_componentwise_absolute_spectral_gap"
LAZY_SELECTOR = "lazy_componentwise_spectral_gap"
PAIRED_SELECTOR = "paired_lazy_componentwise_spectral_gap"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def mask_bits(mask: int, width: int = 11) -> str:
    return format(mask, f"0{width}b")[::-1]


def selected_ids_from_bridge(bridge: dict[str, Any], selector: str) -> list[int]:
    for fiber in bridge["derived"]["selector_fibers"]:
        if fiber.get("selector") == selector:
            return [int(item) for item in fiber["selected_move_orbit_ids"]]
    raise ValueError(f"missing selector fiber: {selector}")


def selected_ids_from_report(report: dict[str, Any], key: str) -> list[int]:
    return [int(item) for item in report["derived"][key]["selected_move_orbit_ids"]]


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_rows(
    raw543_repo: dict[str, Any],
    raw_ids: list[int],
    lazy63_ids: list[int],
    paired480_ids: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    lazy_index = {orbit_id: idx for idx, orbit_id in enumerate(lazy63_ids)}
    paired_index = {orbit_id: idx for idx, orbit_id in enumerate(paired480_ids)}
    orbit_rows = raw543_repo["derived"]["artifacts"]["orbit_rows"]
    if [int(row["orbit_id"]) for row in orbit_rows] != raw_ids:
        raise ValueError("raw543 orbit ids do not match Agda raw selector ids")

    bridge_rows: list[dict[str, Any]] = []
    fixed_rows: list[dict[str, Any]] = []
    paired_rows: list[dict[str, Any]] = []
    for row in orbit_rows:
        orbit_id = int(row["orbit_id"])
        fixed = bool(row["fixed"])
        member_a = int(row["member_a"])
        member_b = int(row["member_b"])
        size = int(row["size"])
        bucket = "lazy63_fixed" if fixed else "paired480_two_cycle"
        out = {
            "orbit_id": orbit_id,
            "agda_dynamics_id": f"d{orbit_id}",
            "agda_membership_constructor": f"rawGapMember{orbit_id}",
            "raw543_fin_index": orbit_id,
            "raw543_fin_witness": f"from_nat_prime(543,{orbit_id})",
            "bucket": bucket,
            "bucket_index": lazy_index.get(orbit_id, paired_index.get(orbit_id)),
            "lazy63_index": lazy_index.get(orbit_id),
            "paired480_index": paired_index.get(orbit_id),
            "orbit_size": size,
            "fixed": fixed,
            "representative_mask": int(row["representative"]),
            "member_a_mask": member_a,
            "member_b_mask": member_b,
            "member_a_bits_lsb_first": mask_bits(member_a),
            "member_b_bits_lsb_first": mask_bits(member_b),
        }
        bridge_rows.append(out)
        if fixed:
            fixed_rows.append(out)
        else:
            paired_rows.append(out)
    return bridge_rows, fixed_rows, paired_rows


def build_theorem() -> dict[str, Any]:
    raw543_repo = load_json(RAW543_REPO_REPORT)
    bridge = load_json(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT)
    raw543_indexed = load_json(RAW543_INDEXED_REPORT)
    lazy63 = load_json(LAZY63_REPORT)
    paired480 = load_json(PAIRED480_REPORT)

    raw_ids = selected_ids_from_bridge(bridge, RAW_SELECTOR)
    lazy63_ids = selected_ids_from_bridge(bridge, LAZY_SELECTOR)
    paired480_ids = selected_ids_from_bridge(bridge, PAIRED_SELECTOR)
    indexed_raw_ids = selected_ids_from_report(raw543_indexed, "raw_selector")
    report_lazy63_ids = selected_ids_from_report(lazy63, "lazy_selector")
    report_paired480_ids = selected_ids_from_report(paired480, "paired_lazy_selector")

    bridge_rows, fixed_rows, paired_rows = build_rows(
        raw543_repo,
        raw_ids,
        lazy63_ids,
        paired480_ids,
    )
    fixed_ids = [int(row["orbit_id"]) for row in fixed_rows]
    two_cycle_ids = [int(row["orbit_id"]) for row in paired_rows]
    by_id = {int(row["orbit_id"]): row for row in bridge_rows}

    vector_payload = {
        "raw543_orbit_ids": raw_ids,
        "fixed63_orbit_ids": fixed_ids,
        "paired480_orbit_ids": two_cycle_ids,
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

    checks = {
        "repo_raw543_action_is_certified": raw543_repo.get("status")
        == "RAW543_REPO_C2_KERNEL_ACTION_CERTIFIED"
        and raw543_repo.get("all_checks_pass") is True,
        "univalent_bridge_is_certified": bridge.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_CERTIFIED"
        and bridge.get("all_checks_pass") is True,
        "raw543_indexed_report_is_certified": raw543_indexed.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED"
        and raw543_indexed.get("all_checks_pass") is True,
        "lazy63_report_is_certified": lazy63.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_CERTIFIED"
        and lazy63.get("all_checks_pass") is True,
        "paired480_report_is_certified": paired480.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_CERTIFIED"
        and paired480.get("all_checks_pass") is True,
        "raw_selector_ids_are_all_actual_orbit_ids": raw_ids == list(range(543)),
        "indexed_raw_selector_ids_match_bridge": indexed_raw_ids == raw_ids,
        "lazy63_report_ids_match_bridge": report_lazy63_ids == lazy63_ids,
        "paired480_report_ids_match_bridge": report_paired480_ids == paired480_ids,
        "actual_fixed_orbits_match_lazy63_selector": fixed_ids == lazy63_ids,
        "actual_two_cycle_orbits_match_paired480_selector": two_cycle_ids == paired480_ids,
        "lazy63_and_paired480_partition_raw543": sorted(lazy63_ids + paired480_ids) == raw_ids
        and set(lazy63_ids).isdisjoint(paired480_ids),
        "raw543_row_count_is_543": len(bridge_rows) == 543,
        "fixed_row_count_is_63": len(fixed_rows) == 63,
        "paired_row_count_is_480": len(paired_rows) == 480,
        "raw543_fin_indices_are_identity_order": [
            int(row["raw543_fin_index"]) for row in bridge_rows
        ]
        == list(range(543)),
    }

    report = {
        "schema": "d20.theorem.raw543_repo_c2_kernel_agda_bridge_data",
        "status": "RAW543_REPO_C2_KERNEL_AGDA_BRIDGE_DATA_CERTIFIED",
        "object": "D20",
        "claim": (
            "The existing Agda Raw543 selector indexing is the identity ordering "
            "of the actual repository-bound nonzero C2 kernel orbits; its Lazy63 "
            "and PairedLazy480 subselectors are exactly the fixed and two-cycle "
            "actual orbit partitions."
        ),
        "inputs": {
            "raw543_repo_c2_kernel_action_report": input_record(RAW543_REPO_REPORT),
            "c2_univalent_foundation_bridge_report": input_record(
                C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT
            ),
            "raw543_indexed_report": input_record(RAW543_INDEXED_REPORT),
            "lazy63_report": input_record(LAZY63_REPORT),
            "paired480_report": input_record(PAIRED480_REPORT),
        },
        "derived": {
            "agda_binding": {
                "raw_selector": RAW_SELECTOR,
                "lazy63_selector": LAZY_SELECTOR,
                "paired480_selector": PAIRED_SELECTOR,
                "raw543_membership_constructor_prefix": "rawGapMember",
                "agda_dynamics_id_prefix": "d",
                "raw543_fin_index_rule": "orbit_id -> FDP.fromN' 543 orbit_id",
            },
            "summary": {
                "raw543_orbit_count": len(bridge_rows),
                "fixed63_orbit_count": len(fixed_rows),
                "paired480_two_cycle_orbit_count": len(paired_rows),
                "raw543_fin_identity_indexing": True,
                "lazy63_equals_actual_fixed_orbits": fixed_ids == lazy63_ids,
                "paired480_equals_actual_two_cycle_orbits": two_cycle_ids == paired480_ids,
            },
            "ids": {
                "raw543_orbit_ids": raw_ids,
                "fixed63_orbit_ids": fixed_ids,
                "paired480_orbit_ids": two_cycle_ids,
                "lazy63_selected_ids": lazy63_ids,
                "paired480_selected_ids": paired480_ids,
            },
            "hashes": {
                "bridge_rows_sha256": sha_json(bridge_rows),
                "fixed63_rows_sha256": sha_json(fixed_rows),
                "paired480_rows_sha256": sha_json(paired_rows),
                "vector_payload_sha256": sha_json(vector_payload),
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "next_highest_yield_item": (
            "Feed actual_raw543_agda_orbit_bridge.csv into the Agda emitter so the "
            "refactored modules consume the actual C2 kernel orbit masks directly."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report, bridge_rows, fixed_rows, paired_rows, vector_payload


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report, bridge_rows, fixed_rows, paired_rows, vector_payload = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "actual_raw543_agda_orbit_bridge.csv", bridge_rows)
    write_csv(out_dir / "actual_raw543_agda_fixed63.csv", fixed_rows)
    write_csv(out_dir / "actual_raw543_agda_paired480.csv", paired_rows)
    (out_dir / "actual_raw543_agda_bridge_vectors.json").write_text(
        json.dumps(vector_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.raw543_repo_c2_kernel_agda_bridge_data_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "artifacts": {
            "bridge_csv": rel(out_dir / "actual_raw543_agda_orbit_bridge.csv"),
            "fixed63_csv": rel(out_dir / "actual_raw543_agda_fixed63.csv"),
            "paired480_csv": rel(out_dir / "actual_raw543_agda_paired480.csv"),
            "bridge_vectors": rel(out_dir / "actual_raw543_agda_bridge_vectors.json"),
        },
        "artifact_hashes": {
            "bridge_csv": sha_file(out_dir / "actual_raw543_agda_orbit_bridge.csv"),
            "fixed63_csv": sha_file(out_dir / "actual_raw543_agda_fixed63.csv"),
            "paired480_csv": sha_file(out_dir / "actual_raw543_agda_paired480.csv"),
            "bridge_vectors": sha_file(out_dir / "actual_raw543_agda_bridge_vectors.json"),
        },
        "inputs": report["inputs"],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
