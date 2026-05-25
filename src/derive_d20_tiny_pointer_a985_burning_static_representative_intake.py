from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS_CONTRACT_CERTIFIED = (
    "D20_TINY_POINTER_A985_BURNING_STATIC_REPRESENTATIVE_INTAKE_CONTRACT_CERTIFIED"
)
STATUS_NEEDS_REVIEW = "D20_TINY_POINTER_A985_BURNING_STATIC_REPRESENTATIVE_INTAKE_NEEDS_REVIEW"
THEOREM_ID = "tiny_pointer_a985_burning_static_representative_intake"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

BRIDGE_REPORT = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_ship_algebraicity_bridge" / "report.json"
)
CHARACTER_REPORT = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters" / "report.json"
CHARACTER_TABLE = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters" / "canonical_sector_character_table.npz"
)
EVIDENCE_ROOT = ROOT / "data" / "evidence" / "ss_sat"

REQUIRED_SCHEMA = {
    "schema": "d20.tiny_pointer_a985.burning_static_representative_input@1",
    "field_prime": 1_000_003,
    "description": (
        "Raw A985 orbital coordinates for one Burning_static_fields class representative. "
        "Coefficients are interpreted modulo 1000003 against the canonical raw relation order R_alpha."
    ),
    "required_csv_columns": [
        "representative_id",
        "quotient_generator",
        "relation_alpha",
        "coefficient_mod_1000003",
        "source_artifact",
        "source_row",
    ],
    "semantic_requirements": [
        "relation_alpha must be an integer in [0,984]",
        "coefficient_mod_1000003 must be reduced modulo 1000003",
        "at least one nonzero row is required per quotient_generator",
        "expected quotient generators are compatible with Z/2 x Z/4^2",
        "source_artifact must identify the Burning/static field data source, not only the ledger summary",
    ],
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def candidate_file_role(path: Path) -> str | None:
    name = path.name.lower()
    if "burn" in name or "burning" in name:
        return "name_mentions_burning"
    if name in {"all_family_summary.csv", "proof_trace_family_summary.csv", "scheduler_family_summary.csv"}:
        return "referenced_summary_filename"
    if "family_summary" in name:
        return "family_summary_like"
    if "running_ledger.csv" == name:
        return "ledger_summary"
    return None


def scan_files() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(EVIDENCE_ROOT.rglob("*")):
        if not path.is_file():
            continue
        role = candidate_file_role(path)
        if role is None:
            continue
        rows.append(
            {
                "container": "",
                "path": rel(path),
                "artifact_role": role,
                "bytes": path.stat().st_size,
                "sha256": sha_file(path),
            }
        )
    return rows


def scan_zip_entries() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for zip_path in sorted(EVIDENCE_ROOT.rglob("*.zip")):
        try:
            with zipfile.ZipFile(zip_path) as zf:
                for info in zf.infolist():
                    entry_name = Path(info.filename).name.lower()
                    role = None
                    if "burn" in info.filename.lower():
                        role = "zip_entry_mentions_burning"
                    elif entry_name in {
                        "all_family_summary.csv",
                        "proof_trace_family_summary.csv",
                        "scheduler_family_summary.csv",
                    }:
                        role = "zip_referenced_summary_filename"
                    elif "family_summary" in entry_name:
                        role = "zip_family_summary_like"
                    elif entry_name == "running_ledger.csv":
                        role = "zip_ledger_summary"
                    if role is None:
                        continue
                    rows.append(
                        {
                            "container": rel(zip_path),
                            "path": info.filename,
                            "artifact_role": role,
                            "bytes": int(info.file_size),
                            "sha256": "",
                        }
                    )
        except zipfile.BadZipFile:
            rows.append(
                {
                    "container": rel(zip_path),
                    "path": "",
                    "artifact_role": "zip_unreadable",
                    "bytes": 0,
                    "sha256": "",
                }
            )
    return rows


def has_raw_representative(rows: list[dict[str, Any]]) -> bool:
    raw_markers = {
        "burning_static_fields_raw_orbital_coo.csv",
        "burning_static_fields_a985_orbital_coo.csv",
        "burning_static_fields_representative.csv",
        "burning_static_fields_representatives.csv",
    }
    for row in rows:
        name = Path(str(row["path"])).name.lower()
        if name in raw_markers:
            return True
        if "burning_static_fields" in name and ("coo" in name or "representative" in name):
            return True
    return False


def ledger_burning_rows() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ledger in sorted(EVIDENCE_ROOT.rglob("running_ledger.csv")):
        try:
            rows = read_csv_rows(ledger)
        except UnicodeDecodeError:
            continue
        for row in rows:
            if "Burning" in row.get("invariant", "") or "BURNING" in row.get("invariant", ""):
                out.append(
                    {
                        "ledger": rel(ledger),
                        "package": row.get("package", ""),
                        "layer": row.get("layer", ""),
                        "invariant": row.get("invariant", ""),
                        "value": row.get("value", ""),
                        "status": row.get("status", ""),
                        "source": row.get("source", ""),
                    }
                )
    return out


def build_intake() -> dict[str, Any]:
    bridge_report = load_json(BRIDGE_REPORT)
    character_report = load_json(CHARACTER_REPORT)
    artifact_rows = scan_files() + scan_zip_entries()
    burning_rows = ledger_burning_rows()
    raw_representative_present = has_raw_representative(artifact_rows)
    summary_artifact_rows = [
        row for row in artifact_rows if "summary" in row["artifact_role"] or row["artifact_role"].endswith("ledger_summary")
    ]
    zip_rows = [row for row in artifact_rows if row["container"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "burning_static_representative_artifact_audit.csv",
        ["container", "path", "artifact_role", "bytes", "sha256"],
        artifact_rows,
    )
    write_csv_rows(
        OUT_DIR / "burning_static_ledger_rows.csv",
        ["ledger", "package", "layer", "invariant", "value", "status", "source"],
        burning_rows,
    )
    write_csv_rows(
        OUT_DIR / "burning_static_representative_pending_inputs.csv",
        ["input_name", "required", "status", "reason"],
        [
            {
                "input_name": "raw_a985_orbital_representative_coo",
                "required": True,
                "status": "absent",
                "reason": "No local artifact contains Burning_static_fields raw A985 COO coordinates.",
            },
            {
                "input_name": "quotient_generator_labels",
                "required": True,
                "status": "absent",
                "reason": "Ledger gives invariant factors but not generator-to-coordinate rows.",
            },
            {
                "input_name": "canonical_a985_character_table",
                "required": True,
                "status": "present",
                "reason": rel(CHARACTER_TABLE),
            },
        ],
    )
    write_json(OUT_DIR / "burning_static_representative_input_schema.json", REQUIRED_SCHEMA)

    checks = {
        "burning_ship_algebraicity_bridge_certified": bridge_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_SHIP_ALGEBRAICITY_BRIDGE_CERTIFIED"
        and bridge_report.get("all_checks_pass") is True,
        "canonical_a985_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "burning_ledger_rows_found": len(burning_rows) >= 8,
        "summary_artifacts_found": len(summary_artifact_rows) > 0,
        "zip_archives_scanned": len([row for row in zip_rows if row["artifact_role"].startswith("zip")]) > 0,
        "raw_representative_absent": raw_representative_present is False,
        "input_schema_emitted": (OUT_DIR / "burning_static_representative_input_schema.json").exists(),
        "no_raw_projection_emitted_without_source": not (OUT_DIR / "burning_static_raw_a985_projection.csv").exists(),
    }
    all_checks_pass = all(checks.values())
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_representative_intake.source_drop",
        "status": STATUS_CONTRACT_CERTIFIED if all_checks_pass else STATUS_NEEDS_REVIEW,
        "object": "d20",
        "claim": (
            "The local evidence is sufficient for the Burning/A985 finite quotient bridge, but it "
            "does not contain a raw Burning_static_fields representative in the 985-orbital basis. "
            "The required intake schema is now explicit."
        ),
        "boundary": (
            "Do not construct a Burning_static_fields A985 trace profile from only quotient invariant "
            "factors. A representative requires raw orbital coordinates or an explicit generator map."
        ),
        "inputs": {
            "burning_ship_algebraicity_bridge": {"path": rel(BRIDGE_REPORT), "sha256": sha_file(BRIDGE_REPORT)},
            "canonical_sector_characters": {"path": rel(CHARACTER_REPORT), "sha256": sha_file(CHARACTER_REPORT)},
            "canonical_sector_character_table": {"path": rel(CHARACTER_TABLE), "sha256": sha_file(CHARACTER_TABLE)},
            "evidence_root": {"path": rel(EVIDENCE_ROOT)},
        },
        "checks": checks,
        "derived": {
            "artifact_rows_scanned": len(artifact_rows),
            "zip_artifact_rows": len(zip_rows),
            "burning_ledger_rows": len(burning_rows),
            "raw_representative_present": raw_representative_present,
            "required_schema": REQUIRED_SCHEMA["schema"],
            "tables": {
                "artifact_audit": rel(OUT_DIR / "burning_static_representative_artifact_audit.csv"),
                "ledger_rows": rel(OUT_DIR / "burning_static_ledger_rows.csv"),
                "pending_inputs": rel(OUT_DIR / "burning_static_representative_pending_inputs.csv"),
                "input_schema": rel(OUT_DIR / "burning_static_representative_input_schema.json"),
            },
        },
        "next_highest_yield_item": (
            "Supply or derive the Burning_static_fields quotient-generator rows in the emitted input "
            "schema; then the canonical A985 character table can compute the sector support and trace profile."
        ),
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_static_representative_intake_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            **report["derived"]["tables"],
        },
        "validation_tests": list(checks),
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    (OUT_DIR / "burning_static_representative_intake_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Burning Static Representative Intake\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Artifact rows scanned: `{derived['artifact_rows_scanned']}`\n\n"
        f"Burning ledger rows: `{derived['burning_ledger_rows']}`\n\n"
        f"Raw representative present: `{derived['raw_representative_present']}`\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        f"Next: {report['next_highest_yield_item']}\n"
    )


def update_theorem_index(report: dict[str, Any]) -> None:
    index_path = D20_INVARIANTS / "theorems" / "index.json"
    index = load_json(index_path) if index_path.exists() else {"theorems": []}
    theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    theorems.append(
        {
            "id": THEOREM_ID,
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    write_json(index_path, index)


def verify_intake() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    artifact_rows = read_csv_rows(OUT_DIR / "burning_static_representative_artifact_audit.csv")
    ledger_rows = read_csv_rows(OUT_DIR / "burning_static_ledger_rows.csv")
    pending_rows = read_csv_rows(OUT_DIR / "burning_static_representative_pending_inputs.csv")
    schema = load_json(OUT_DIR / "burning_static_representative_input_schema.json")
    checks = {
        "report_status_is_contract_certified": report.get("status") == STATUS_CONTRACT_CERTIFIED,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "artifact_audit_nonempty": len(artifact_rows) > 0,
        "ledger_rows_nonempty": len(ledger_rows) >= 8,
        "pending_rows_include_raw_representative": any(
            row["input_name"] == "raw_a985_orbital_representative_coo" and row["status"] == "absent"
            for row in pending_rows
        ),
        "schema_has_required_columns": schema.get("required_csv_columns") == REQUIRED_SCHEMA["required_csv_columns"],
        "raw_projection_not_emitted": not (OUT_DIR / "burning_static_raw_a985_projection.csv").exists(),
    }
    return {
        "status": "D20_TINY_POINTER_A985_BURNING_STATIC_REPRESENTATIVE_INTAKE_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_BURNING_STATIC_REPRESENTATIVE_INTAKE_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_intake()
    verification = verify_intake()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
