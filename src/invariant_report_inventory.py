from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REPORT_ROOTS = (
    ("theorem", ROOT / "data" / "invariants" / "d20" / "theorems"),
    ("proof_obligation", ROOT / "data" / "invariants" / "d20" / "proof_obligations"),
)

CERTIFIED_STATUS_MARKERS = (
    "_CERTIFIED",
    "_PASS",
    "_CLASSIFIED",
    "_REGISTERED",
    "_EVALUATED",
    "_OBSTRUCTED",
)
PROVISIONAL_STATUS_MARKERS = (
    "_NEEDS_REVIEW",
    "_SOURCE_ABSENT",
    "_READY_INPUT_ABSENT",
)
DEMOTED_STATUS_MARKERS = (
    "_DEMOTED",
)


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def status_is_certified(status: Any) -> bool:
    if not isinstance(status, str):
        return False
    if any(status.endswith(marker) for marker in DEMOTED_STATUS_MARKERS):
        return False
    if any(status.endswith(marker) for marker in PROVISIONAL_STATUS_MARKERS):
        return False
    return any(status.endswith(marker) for marker in CERTIFIED_STATUS_MARKERS)


def status_is_demoted(status: Any) -> bool:
    return isinstance(status, str) and any(status.endswith(marker) for marker in DEMOTED_STATUS_MARKERS)


def status_classification(status: Any) -> str:
    if status_is_certified(status):
        return "certified"
    if status_is_demoted(status):
        return "demoted"
    return "provisional"


def invariant_report_rows(*, root: Path = ROOT) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for kind, report_root in REPORT_ROOTS:
        scan_root = root / report_root.relative_to(ROOT)
        if not scan_root.is_dir():
            continue
        for directory in sorted(path for path in scan_root.iterdir() if path.is_dir()):
            report_path = directory / "report.json"
            if not report_path.exists():
                continue
            payload = load_json(report_path)
            rel = report_path.relative_to(root).as_posix()
            status = payload.get("status")
            classification = status_classification(status)
            row: dict[str, Any] = {
                "id": directory.name,
                "kind": kind,
                "path": rel,
                "status": status,
                "certified": classification == "certified",
                "classification": classification,
                "schema": payload.get("schema"),
                "report_file_sha256": sha_file(report_path),
            }
            certificate_sha256 = payload.get("certificate_sha256")
            if isinstance(certificate_sha256, str):
                row["certificate_sha256"] = certificate_sha256
            all_checks_pass = payload.get("all_checks_pass")
            if isinstance(all_checks_pass, bool):
                row["all_checks_pass"] = all_checks_pass
            rows.append(row)
    return rows


def invariant_report_inventory(*, root: Path = ROOT) -> dict[str, Any]:
    rows = invariant_report_rows(root=root)
    certified = [row for row in rows if row.get("classification") == "certified"]
    provisional = [row for row in rows if row.get("classification") == "provisional"]
    demoted = [row for row in rows if row.get("classification") == "demoted"]
    return {
        "schema": "d20.certified_invariant_report_inventory",
        "status": "D20_CERTIFIED_INVARIANT_REPORT_INVENTORY_BUILT",
        "automation": "scan data/invariants/d20/{theorems,proof_obligations}/*/report.json during certificate refresh; certified/provisional/demoted classification is derived from status markers",
        "scan_roots": [
            "data/invariants/d20/theorems",
            "data/invariants/d20/proof_obligations",
        ],
        "report_count": len(rows),
        "certified_report_count": len(certified),
        "provisional_report_count": len(provisional),
        "demoted_report_count": len(demoted),
        "certified_status_markers": list(CERTIFIED_STATUS_MARKERS),
        "provisional_status_markers": list(PROVISIONAL_STATUS_MARKERS),
        "demoted_status_markers": list(DEMOTED_STATUS_MARKERS),
    }
