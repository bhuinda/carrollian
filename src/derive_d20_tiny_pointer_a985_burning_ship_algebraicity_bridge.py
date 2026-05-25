from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_BURNING_SHIP_ALGEBRAICITY_BRIDGE_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_burning_ship_algebraicity_bridge"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

LEDGER = ROOT / "data" / "evidence" / "ss_sat" / "source_drops" / "external_evidence_gate" / "running_ledger.csv"
CANONICAL_CHARACTERS = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_characters" / "report.json"
FOURIER_TRACE_EVAL = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_fourier_trace_candidate_evaluation" / "report.json"
)


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


def find_row(rows: list[dict[str, str]], *, layer: str, invariant: str) -> dict[str, str] | None:
    for row in rows:
        if row["layer"] == layer and row["invariant"] == invariant:
            return row
    return None


def required_row(rows: list[dict[str, str]], *, layer: str, invariant: str) -> dict[str, str]:
    row = find_row(rows, layer=layer, invariant=invariant)
    if row is None:
        raise ValueError(f"missing ledger row {layer}:{invariant}")
    return row


def parse_quotient(text: str) -> list[int]:
    text = text.strip()
    if text.lower() == "trivial":
        return []
    factors: list[int] = []
    for part in text.split(" x "):
        match = re.fullmatch(r"Z/(\d+)(?:\^(\d+))?", part.strip())
        if match is None:
            raise ValueError(f"unsupported quotient factor: {part!r}")
        modulus = int(match.group(1))
        count = int(match.group(2) or "1")
        factors.extend([modulus] * count)
    return factors


def quotient_order(factors: list[int]) -> int:
    out = 1
    for value in factors:
        out *= int(value)
    return out


def primary_component(factors: list[int], prime: int) -> list[int]:
    components: list[int] = []
    for value in factors:
        power = 1
        remaining = int(value)
        while remaining % prime == 0:
            power *= prime
            remaining //= prime
        if power > 1:
            components.append(power)
    return sorted(components)


def quotient_literal(factors: list[int]) -> str:
    if not factors:
        return "trivial"
    counts: dict[int, int] = {}
    for factor in factors:
        counts[factor] = counts.get(factor, 0) + 1
    parts = []
    for factor in sorted(counts):
        count = counts[factor]
        parts.append(f"Z/{factor}" if count == 1 else f"Z/{factor}^{count}")
    return " x ".join(parts)


def selected_evidence_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    wanted = [
        ("base", "D20 critical group"),
        ("base", "critical group order"),
        ("family", "Burning_static_fields_quotient"),
        ("family", "Burning_static_fields_image_size"),
        ("proof_trace", "Burning_static_fields_quotient"),
        ("proof_trace", "Burning_static_fields_image_size"),
        ("scheduler_family", "BURNING_STATIC_FIELDS_quotient"),
        ("scheduler_family", "BURNING_STATIC_FIELDS_image_size"),
        ("family", "A985_frame_fields_quotient"),
        ("family", "A985_frame_fields_image_size"),
        ("hybrid", "ECA_pattern_basis + Burning_static_fields"),
        ("hybrid", "BOOLEAN_TRACE_UNION + Burning_weighted_analytic"),
        ("hybrid", "BOOLEAN_TRACE_UNION + Burning_static_all"),
        ("prior", "sandpile_burningship"),
    ]
    out: list[dict[str, Any]] = []
    for layer, invariant in wanted:
        row = find_row(rows, layer=layer, invariant=invariant)
        if row is None:
            continue
        out.append(
            {
                "package": row["package"],
                "layer": row["layer"],
                "invariant": row["invariant"],
                "value": row["value"],
                "status": row["status"],
                "source": row["source"],
            }
        )
    return out


def build_bridge() -> dict[str, Any]:
    ledger_rows = read_csv_rows(LEDGER)
    character_report = load_json(CANONICAL_CHARACTERS)
    fourier_trace_report = load_json(FOURIER_TRACE_EVAL)

    critical_order_row = required_row(ledger_rows, layer="base", invariant="critical group order")
    burning_quotient_row = required_row(ledger_rows, layer="family", invariant="Burning_static_fields_quotient")
    burning_image_row = required_row(ledger_rows, layer="family", invariant="Burning_static_fields_image_size")
    burning_proof_quotient_row = required_row(
        ledger_rows,
        layer="proof_trace",
        invariant="Burning_static_fields_quotient",
    )
    burning_proof_image_row = required_row(
        ledger_rows,
        layer="proof_trace",
        invariant="Burning_static_fields_image_size",
    )
    burning_scheduler_quotient_row = required_row(
        ledger_rows,
        layer="scheduler_family",
        invariant="BURNING_STATIC_FIELDS_quotient",
    )
    burning_scheduler_image_row = required_row(
        ledger_rows,
        layer="scheduler_family",
        invariant="BURNING_STATIC_FIELDS_image_size",
    )
    a985_quotient_row = required_row(ledger_rows, layer="family", invariant="A985_frame_fields_quotient")
    a985_image_row = required_row(ledger_rows, layer="family", invariant="A985_frame_fields_image_size")
    prior_burning_row = required_row(ledger_rows, layer="prior", invariant="sandpile_burningship")
    hybrid_eca_burning = required_row(ledger_rows, layer="hybrid", invariant="ECA_pattern_basis + Burning_static_fields")
    hybrid_boolean_weighted = required_row(
        ledger_rows,
        layer="hybrid",
        invariant="BOOLEAN_TRACE_UNION + Burning_weighted_analytic",
    )
    hybrid_boolean_static = required_row(
        ledger_rows,
        layer="hybrid",
        invariant="BOOLEAN_TRACE_UNION + Burning_static_all",
    )

    critical_order = int(critical_order_row["value"])
    burning_factors = parse_quotient(burning_quotient_row["value"])
    a985_factors = parse_quotient(a985_quotient_row["value"])
    burning_order = quotient_order(burning_factors)
    a985_order = quotient_order(a985_factors)
    burning_two_primary = primary_component(burning_factors, 2)
    a985_two_primary = primary_component(a985_factors, 2)
    burning_image_size = int(burning_image_row["value"])
    a985_image_size = int(a985_image_row["value"])

    evidence = selected_evidence_rows(ledger_rows)
    primary_rows = [
        {
            "observable": "Burning_static_fields",
            "quotient": burning_quotient_row["value"],
            "quotient_order": burning_order,
            "two_primary_component": quotient_literal(burning_two_primary),
            "two_primary_order": quotient_order(burning_two_primary),
            "odd_primary_cofactor": burning_order // quotient_order(burning_two_primary),
        },
        {
            "observable": "A985_frame_fields",
            "quotient": a985_quotient_row["value"],
            "quotient_order": a985_order,
            "two_primary_component": quotient_literal(a985_two_primary),
            "two_primary_order": quotient_order(a985_two_primary),
            "odd_primary_cofactor": a985_order // quotient_order(a985_two_primary),
        },
    ]
    bridge_rows = [
        {
            "bridge_check": "burning_quotient_order",
            "left_value": burning_quotient_row["value"],
            "right_value": burning_order,
            "interpretation": "Burning static fields expose a 2-primary quotient of order 32.",
        },
        {
            "bridge_check": "a985_two_primary_component",
            "left_value": a985_quotient_row["value"],
            "right_value": quotient_literal(a985_two_primary),
            "interpretation": "The A985 frame quotient has the same 2-primary invariant factors.",
        },
        {
            "bridge_check": "critical_group_index_burning",
            "left_value": critical_order,
            "right_value": burning_image_size,
            "interpretation": "D20 critical group order divided by Burning quotient order matches the certified image size.",
        },
        {
            "bridge_check": "critical_group_index_a985_frame",
            "left_value": critical_order,
            "right_value": a985_image_size,
            "interpretation": "D20 critical group order divided by A985 frame quotient order matches the certified image size.",
        },
        {
            "bridge_check": "trace_detector_available",
            "left_value": character_report["status"],
            "right_value": fourier_trace_report["status"],
            "interpretation": "A985 sector characters and Fourier trace candidates are available to test any explicit Burning-to-A985 vector.",
        },
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "burning_a985_bridge_evidence_rows.csv",
        ["package", "layer", "invariant", "value", "status", "source"],
        evidence,
    )
    write_csv_rows(
        OUT_DIR / "burning_a985_primary_decomposition.csv",
        [
            "observable",
            "quotient",
            "quotient_order",
            "two_primary_component",
            "two_primary_order",
            "odd_primary_cofactor",
        ],
        primary_rows,
    )
    write_csv_rows(
        OUT_DIR / "burning_a985_bridge_checks.csv",
        ["bridge_check", "left_value", "right_value", "interpretation"],
        bridge_rows,
    )

    checks = {
        "ledger_has_burning_family_quotient": burning_quotient_row["value"] == "Z/2 x Z/4^2",
        "ledger_has_burning_family_image_size": burning_image_size == 162000,
        "ledger_has_burning_proof_trace_repeat": burning_proof_quotient_row["value"] == burning_quotient_row["value"]
        and int(burning_proof_image_row["value"]) == burning_image_size,
        "ledger_has_burning_scheduler_repeat": burning_scheduler_quotient_row["value"] == burning_quotient_row["value"]
        and int(burning_scheduler_image_row["value"]) == burning_image_size,
        "prior_burningship_certificate_imported": prior_burning_row["value"]
        == "D20_SANDPILE_BURNINGSHIP_STATIC_ACTION_CERTIFIED"
        and prior_burning_row["status"] == "IMPORTED_CERTIFICATE_HASHED",
        "ledger_has_a985_frame_quotient": a985_quotient_row["value"] == "Z/2 x Z/20 x Z/60",
        "ledger_has_a985_frame_image_size": a985_image_size == 2160,
        "critical_group_order_is_5184000": critical_order == 5_184_000,
        "burning_quotient_order_is_32": burning_order == 32,
        "a985_frame_quotient_order_is_2400": a985_order == 2400,
        "burning_image_size_matches_critical_group_index": critical_order // burning_order == burning_image_size,
        "a985_image_size_matches_critical_group_index": critical_order // a985_order == a985_image_size,
        "burning_equals_a985_two_primary_component": burning_two_primary == a985_two_primary == [2, 4, 4],
        "hybrid_burning_rows_collapse_trivially": hybrid_eca_burning["value"] == "trivial"
        and hybrid_boolean_weighted["value"] == "trivial"
        and hybrid_boolean_static["value"] == "trivial",
        "canonical_a985_sector_characters_certified": character_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        and character_report.get("all_checks_pass") is True,
        "fourier_trace_candidate_evaluation_certified": fourier_trace_report.get("status")
        == "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_CERTIFIED"
        and fourier_trace_report.get("all_checks_pass") is True,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_ship_algebraicity_bridge.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_BURNING_SHIP_ALGEBRAICITY_BRIDGE_NEEDS_REVIEW",
        "object": "d20",
        "claim": (
            "The certified Burning Ship/static-field algebraicity is the 2-primary shadow of the "
            "A985 frame-field quotient: Burning_static_fields has quotient Z/2 x Z/4^2, and "
            "A985_frame_fields has quotient Z/2 x Z/20 x Z/60 whose 2-primary component is also "
            "Z/2 x Z/4^2."
        ),
        "boundary": (
            "This theorem certifies the finite quotient bridge and the availability of canonical "
            "A985 trace detectors. It does not yet provide a raw 985-orbital Burning_static_fields "
            "vector or class representative."
        ),
        "inputs": {
            "external_evidence_gate_ledger": {"path": rel(LEDGER), "sha256": sha_file(LEDGER)},
            "canonical_sector_characters": {
                "path": rel(CANONICAL_CHARACTERS),
                "sha256": sha_file(CANONICAL_CHARACTERS),
            },
            "fourier_trace_candidate_evaluation": {
                "path": rel(FOURIER_TRACE_EVAL),
                "sha256": sha_file(FOURIER_TRACE_EVAL),
            },
        },
        "checks": checks,
        "derived": {
            "critical_group_order": critical_order,
            "burning_static_fields": {
                "quotient": burning_quotient_row["value"],
                "quotient_factors": burning_factors,
                "quotient_order": burning_order,
                "image_size": burning_image_size,
                "two_primary_component": quotient_literal(burning_two_primary),
            },
            "a985_frame_fields": {
                "quotient": a985_quotient_row["value"],
                "quotient_factors": a985_factors,
                "quotient_order": a985_order,
                "image_size": a985_image_size,
                "two_primary_component": quotient_literal(a985_two_primary),
                "odd_primary_cofactor": a985_order // quotient_order(a985_two_primary),
            },
            "bridge": {
                "same_two_primary_component": burning_two_primary == a985_two_primary,
                "shared_two_primary_component": quotient_literal(burning_two_primary),
                "shared_two_primary_order": quotient_order(burning_two_primary),
                "a985_odd_cofactor_beyond_burning": a985_order // burning_order,
            },
            "tables": {
                "evidence_rows": rel(OUT_DIR / "burning_a985_bridge_evidence_rows.csv"),
                "primary_decomposition": rel(OUT_DIR / "burning_a985_primary_decomposition.csv"),
                "bridge_checks": rel(OUT_DIR / "burning_a985_bridge_checks.csv"),
            },
        },
        "next_highest_yield_item": (
            "Materialize a Burning_static_fields representative in the raw A985 orbital basis, then "
            "apply the canonical 39-sector character table to locate its sector support and trace profile."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_burning_ship_algebraicity_bridge_manifest.source_drop",
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
    (OUT_DIR / "burning_ship_algebraicity_bridge_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    bridge = derived["bridge"]
    return (
        "# Burning Ship Algebraicity Bridge\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Shared 2-primary component: `{bridge['shared_two_primary_component']}`\n\n"
        f"A985 odd cofactor beyond Burning: `{bridge['a985_odd_cofactor_beyond_burning']}`\n\n"
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


def verify_bridge() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    evidence_rows = read_csv_rows(OUT_DIR / "burning_a985_bridge_evidence_rows.csv")
    primary_rows = read_csv_rows(OUT_DIR / "burning_a985_primary_decomposition.csv")
    bridge_rows = read_csv_rows(OUT_DIR / "burning_a985_bridge_checks.csv")
    primary_by_observable = {row["observable"]: row for row in primary_rows}
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "evidence_rows_include_burning_and_a985": len(evidence_rows) >= 10,
        "primary_rows_have_two_observables": sorted(primary_by_observable) == [
            "A985_frame_fields",
            "Burning_static_fields",
        ],
        "burning_two_primary_is_z2_z4_z4": primary_by_observable["Burning_static_fields"]["two_primary_component"]
        == "Z/2 x Z/4^2",
        "a985_two_primary_is_z2_z4_z4": primary_by_observable["A985_frame_fields"]["two_primary_component"]
        == "Z/2 x Z/4^2",
        "bridge_check_rows_present": len(bridge_rows) == 5,
        "shared_two_primary_reported": report.get("derived", {}).get("bridge", {}).get("shared_two_primary_component")
        == "Z/2 x Z/4^2",
    }
    return {
        "status": "D20_TINY_POINTER_A985_BURNING_SHIP_ALGEBRAICITY_BRIDGE_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_BURNING_SHIP_ALGEBRAICITY_BRIDGE_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_bridge()
    verification = verify_bridge()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
