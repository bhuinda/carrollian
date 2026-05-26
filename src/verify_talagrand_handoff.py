from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ID = "talagrand_python_handoff"
EVIDENCE_DIR = ROOT / "data" / "evidence" / EVIDENCE_ID
MANIFEST_PATH = EVIDENCE_DIR / "manifest.json"
SOURCE_MANIFEST = EVIDENCE_DIR / "MANIFEST.csv"
STATUS_LEDGER = EVIDENCE_DIR / "STATUS_LEDGER.json"
RUN_ORDER = EVIDENCE_DIR / "RUN_ORDER.md"
README = EVIDENCE_DIR / "README_HANDOFF.md"
WORK_DIR = EVIDENCE_DIR / "work"
EXPECTED_STATUS = "HANDOFF_BUNDLE_BUILT; FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED"
EXPECTED_FINAL_BOUNDARY = "FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED"
EXPECTED_OPEN_TARGET = "Exclude the multilevel KKT obstruction system with dF>0"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode(
        "utf-8"
    )


def sha_json(obj: dict[str, Any], hash_key: str) -> str:
    body = {key: value for key, value in obj.items() if key != hash_key}
    return hashlib.sha256(canonical(body)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel(path)} is not a JSON object")
    return payload


def manifest_csv_rows() -> list[dict[str, Any]]:
    with SOURCE_MANIFEST.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "path": row["path"],
                "archive_path": row["archive_path"],
                "size_bytes": int(row["size_bytes"]),
                "sha256": row["sha256"],
            }
        )
    return out


def file_entries() -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted(EVIDENCE_DIR.rglob("*")):
        if not path.is_file() or path == MANIFEST_PATH:
            continue
        item_rel = path.relative_to(EVIDENCE_DIR).as_posix()
        entries[item_rel] = {
            "path": rel(path),
            "sha256": sha_file(path),
            "size_bytes": path.stat().st_size,
        }
    return entries


def run_order_steps() -> list[str]:
    steps: list[str] = []
    for line in RUN_ORDER.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit() or ". `" not in stripped:
            continue
        steps.append(stripped.split("`", 2)[1])
    return steps


def source_manifest_check(source_rows: list[dict[str, Any]], files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    checked: list[dict[str, Any]] = []
    missing: list[str] = []
    for row in source_rows:
        source_path = "work/" + row["path"]
        entry = files.get(source_path)
        if entry is None:
            missing.append(source_path)
            checked.append(
                {
                    "path": source_path,
                    "exists": False,
                    "sha256_matches": False,
                    "size_matches": False,
                }
            )
            continue
        checked.append(
            {
                "path": source_path,
                "exists": True,
                "expected_sha256": row["sha256"],
                "actual_sha256": entry["sha256"],
                "sha256_matches": entry["sha256"] == row["sha256"],
                "expected_size_bytes": row["size_bytes"],
                "actual_size_bytes": entry["size_bytes"],
                "size_matches": entry["size_bytes"] == row["size_bytes"],
            }
        )
    source_paths = {"work/" + row["path"] for row in source_rows}
    work_paths = {path for path in files if path.startswith("work/")}
    extra = sorted(work_paths - source_paths)
    return {
        "declared_file_count": len(source_rows),
        "actual_work_file_count": len(work_paths),
        "checked_files": checked,
        "missing_declared_files": missing,
        "extra_work_files": extra,
        "all_declared_files_present": not missing,
        "all_declared_hashes_match": all(item["sha256_matches"] for item in checked),
        "all_declared_sizes_match": all(item["size_matches"] for item in checked),
    }


def build_manifest() -> dict[str, Any]:
    source_rows = manifest_csv_rows()
    status_ledger = load_json(STATUS_LEDGER)
    files = file_entries()
    steps = run_order_steps()
    extension_counts = Counter(Path(path).suffix.lower() or "<none>" for path in files)
    top_level_counts = Counter(path.split("/", 1)[0] for path in files)
    source_check = source_manifest_check(source_rows, files)
    zip_files = sorted(path for path in files if path.lower().endswith(".zip"))
    checks = {
        "root_readme_present": README.exists(),
        "run_order_present": RUN_ORDER.exists(),
        "source_manifest_present": SOURCE_MANIFEST.exists(),
        "status_ledger_present": STATUS_LEDGER.exists(),
        "work_directory_present": WORK_DIR.exists(),
        "source_manifest_declared_files_present": source_check["all_declared_files_present"],
        "source_manifest_hashes_match": source_check["all_declared_hashes_match"],
        "source_manifest_sizes_match": source_check["all_declared_sizes_match"],
        "source_manifest_covers_work_tree": source_check["actual_work_file_count"]
        == source_check["declared_file_count"]
        and not source_check["extra_work_files"],
        "status_ledger_declares_final_proof_not_claimed": status_ledger.get("global_status") == EXPECTED_STATUS,
        "status_ledger_declares_remaining_open_target": EXPECTED_OPEN_TARGET
        in str(status_ledger.get("remaining_open_target", "")),
        "readme_declares_final_proof_not_claimed": EXPECTED_FINAL_BOUNDARY in README.read_text(encoding="utf-8"),
        "run_order_declares_main_chain": len(steps) == 12,
        "nested_zip_files_absent": not zip_files,
    }
    manifest: dict[str, Any] = {
        "schema": "d20.evidence.talagrand_python_handoff.manifest@1",
        "id": EVIDENCE_ID,
        "status": "TALAGRAND_PYTHON_HANDOFF_IMPORTED_WITH_OPEN_GLOBAL_TARGET",
        "canonical_root": rel(EVIDENCE_DIR),
        "source_handoff": "ingress/talagrand_python_handoff",
        "bundle_scope": status_ledger.get("bundle_scope"),
        "created_utc": status_ledger.get("created_utc"),
        "global_status": status_ledger.get("global_status"),
        "claim_boundary": {
            "final_global_talagrand_proof_claimed": False,
            "remaining_open_target": status_ledger.get("remaining_open_target"),
            "handoff_note": status_ledger.get("handoff_note"),
        },
        "main_chain": status_ledger.get("main_chain", []),
        "exactly_closed": status_ledger.get("exactly_closed", []),
        "review_order": steps,
        "file_count": len(files),
        "work_file_count": source_check["actual_work_file_count"],
        "source_manifest_file_count": source_check["declared_file_count"],
        "extension_counts": dict(sorted(extension_counts.items())),
        "top_level_counts": dict(sorted(top_level_counts.items())),
        "source_manifest_check": source_check,
        "zip_files": zip_files,
        "checks": checks,
        "files": files,
    }
    manifest["manifest_sha256"] = sha_json(manifest, "manifest_sha256")
    return manifest


def write_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return manifest


def load_manifest() -> dict[str, Any]:
    return load_json(MANIFEST_PATH)


def validate_manifest() -> dict[str, Any]:
    expected = build_manifest()
    actual = load_manifest()
    checks = {
        "manifest_exists": MANIFEST_PATH.exists(),
        "manifest_matches_current_bundle": actual == expected,
        "manifest_hash_matches_payload": actual.get("manifest_sha256") == sha_json(actual, "manifest_sha256"),
        "all_bundle_checks_pass": all(actual.get("checks", {}).values()),
        "final_global_proof_not_claimed": actual.get("claim_boundary", {}).get("final_global_talagrand_proof_claimed")
        is False,
    }
    return {
        "schema": "d20.verification.talagrand_python_handoff@1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "evidence_root": rel(EVIDENCE_DIR),
        "manifest": rel(MANIFEST_PATH),
        "manifest_sha256": actual.get("manifest_sha256"),
        "file_count": actual.get("file_count"),
        "work_file_count": actual.get("work_file_count"),
        "global_status": actual.get("global_status"),
        "remaining_open_target": actual.get("claim_boundary", {}).get("remaining_open_target"),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the Talagrand Python handoff evidence bundle.")
    parser.add_argument("--write", action="store_true", help="Regenerate data/evidence/talagrand_python_handoff/manifest.json.")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if args.write:
        result = write_manifest()
    else:
        result = validate_manifest()
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True, allow_nan=False))
    if not args.write and result.get("status") != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
