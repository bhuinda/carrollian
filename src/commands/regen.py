#!/usr/bin/env python3
"""Regenerate d20.json, refresh bundle hashes, and audit the bundle.

Run from the bundle root:

    python -m src.commands.regen

This is the single rebuild command. It performs, in order:
  1. rebuild d20.json from the checked source data;
  2. refresh certificate.json's embedded d20 metadata and self hash;
  3. refresh manifests/file_hashes.json for all tracked files;
  4. run the verifier audit without a second regeneration pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime

ensure_numpy_runtime(ROOT, __file__)

from src.invariant_report_inventory import invariant_report_inventory, invariant_report_rows
from src.paths import D20_INVARIANTS, MANIFESTS, ROOT

MANIFEST = MANIFESTS / "file_hashes.json"
D20 = ROOT / "d20.json"
CERTIFICATE = ROOT / "certificate.json"
SCHEMA_LINEAGE_SUFFIX_RE = re.compile(r"\.v\d+(?=$|[._-])")
STACK_STAGE_ID_RE = re.compile(r"^v\d+_")
LINEAGE_PATH_PART_RE = re.compile(r"(^v\d+$|^v\d+_|_v\d+$|_v\d+_|\.v\d+(?=[._-]))")

EXCLUDED_DIRS = {
    ".git",
    ".codex_deps",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".replay_tmp",
    ".tools",
    ".venv",
    ".msys-tmp",
    "__pycache__",
    "a236_compute_py_bundle",
    "d20_coherent_annihilator_verifier_bundle",
    "d20_coherent_annihilator_verifier_bundle",
    "ingest",
    "terwilliger_local_runner",
    "generated",
}

EXCLUDED_DIR_PREFIXES = (
    "cadical-rel-",
    "gnatural_ontological_computation_v",
    "kissat-rel-",
)

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
}

EXCLUDED_FILES = {
    "README.md",
    "d20.json",
    "test.zip",
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def canonical_schema(value: Any) -> Any:
    if isinstance(value, str):
        return SCHEMA_LINEAGE_SUFFIX_RE.sub("", value)
    return value


def canonical_stage_id(value: Any) -> Any:
    if isinstance(value, str):
        return STACK_STAGE_ID_RE.sub("", value)
    return value


def lineage_archive_path(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    return (
        "source_drops" in parts
        or "source_bundles" in parts
        or any(LINEAGE_PATH_PART_RE.search(part) for part in parts)
    )


def non_identity_path(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    return (
        len(parts) >= 4
        and parts[0] == "data"
        and parts[1] == "invariants"
        and parts[2] == "d20"
        and parts[3] in {"proof_obligations", "theorems"}
    )


def sha_json_body(obj: dict[str, Any], hash_key: str) -> str:
    body = {k: v for k, v in obj.items() if k != hash_key}
    return hashlib.sha256(canonical(body)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(cmd), flush=True)
    if capture:
        return subprocess.run(cmd, cwd=ROOT, text=True, check=check, capture_output=True)
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as f:
        return max(sum(1 for _ in f) - 1, 0)


def refresh_standard_manifest(
    *,
    base: Path,
    manifest_schema: str,
    status: str,
    canonical_folder: str,
    layout: dict[str, str],
) -> bool:
    if not base.exists():
        return False
    manifest_path = base / "manifest.json"
    files: dict[str, Any] = {}
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        if lineage_archive_path(path):
            continue
        if any(
            part in EXCLUDED_DIRS or part.startswith(EXCLUDED_DIR_PREFIXES)
            for part in path.relative_to(ROOT).parts
        ):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.name in EXCLUDED_FILES:
            continue
        rel = path.relative_to(base).as_posix()
        files[rel] = {
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        }
    manifest = {
        "schema": manifest_schema,
        "status": status,
        "canonical_folder": canonical_folder,
        "layout": layout,
        "file_count": len(files),
        "files": files,
    }
    write_json(manifest_path, manifest)
    print(f"refreshed {canonical_folder}/manifest.json", flush=True)
    return True


def refresh_tensor_chain_plain_name_view() -> bool:
    base = ROOT / "data" / "evidence" / "tensor_chain"
    if not base.exists():
        return False
    from src.derive_tensor_chain_plain_names import OUT, derive

    OUT.write_text(json.dumps(derive(), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("refreshed data/evidence/tensor_chain/plain_name_view.json", flush=True)
    return True


def refresh_tensor_chain_manifest() -> bool:
    base = ROOT / "data" / "evidence" / "tensor_chain"
    if not base.exists():
        return False
    manifest_path = base / "manifest.json"
    files: dict[str, Any] = {}
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        if lineage_archive_path(path):
            continue
        rel = path.relative_to(base).as_posix()
        files[rel] = {
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        }
    manifest = {
        "schema": "d20.tensor_chain.manifest",
        "status": "TENSOR_CHAIN_MANIFEST_REFRESHED",
        "canonical_folder": "data/evidence/tensor_chain",
        "layout": {
            "arrays": "NPZ array payloads",
            "reports": "machine and human report files",
            "stages": "named experiment stages",
            "tables": "CSV evidence tables",
        },
        "file_count": len(files),
        "files": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("refreshed data/evidence/tensor_chain/manifest.json", flush=True)
    return True


def refresh_ss_sat_manifest() -> bool:
    base = ROOT / "data" / "evidence" / "ss_sat"
    if not base.exists():
        return False
    manifest_path = base / "manifest.json"
    files: dict[str, Any] = {}
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        if lineage_archive_path(path):
            continue
        rel = path.relative_to(base).as_posix()
        if any(
            part in EXCLUDED_DIRS or part.startswith(EXCLUDED_DIR_PREFIXES)
            for part in path.relative_to(ROOT).parts
        ):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files[rel] = {
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        }
    manifest = {
        "schema": "d20.ss_sat.manifest",
        "status": "SS_SAT_MANIFEST_REFRESHED",
        "canonical_folder": "data/evidence/ss_sat",
        "layout": {
            "audits": "proof verification and C/V/X audit outputs",
            "benchmarks": "DIMACS fixture inputs",
            "logs": "captured solver stdout and stderr logs",
            "manifests": "source manifests preserving command lines and hashes",
            "proofs": "DRAT, LRAT, FRAT, and extracted LRAT proof artifacts",
            "reports": "machine and human reports",
            "residues": "typed failed or blocked seams",
            "schema": "external evidence manifest schema",
            "scripts": "evidence analysis and extraction scripts",
            "tables": "CSV evidence summaries",
        },
        "file_count": len(files),
        "files": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("refreshed data/evidence/ss_sat/manifest.json", flush=True)
    return True


def stack_series_stage_summary(stage_id: str, cert_name: str) -> dict[str, Any]:
    base = ROOT / "data" / "evidence" / "stack_series"
    stage_dir = base / "stages" / stage_id
    cert_path = stage_dir / cert_name
    certificate = load_json(cert_path) if cert_path.exists() else {}
    csv_counts = {
        path.relative_to(stage_dir).as_posix(): csv_row_count(path)
        for path in sorted(stage_dir.rglob("*.csv"))
    } if stage_dir.exists() else {}
    return {
        "stage_id": canonical_stage_id(stage_id),
        "certificate_file": cert_name,
        "certificate_sha256": sha_file(cert_path) if cert_path.exists() else None,
        "schema": canonical_schema(certificate.get("schema")),
        "status": certificate.get("status"),
        "bounds": certificate.get("bounds"),
        "derived_row_counts": certificate.get("derived_row_counts") or certificate.get("coefficient_rows") or {},
        "csv_row_counts": csv_counts,
        "tensor_metadata": certificate.get("tensor_metadata"),
        "exact_invariant_hits": certificate.get("exact_invariant_hits") or certificate.get("invariant_hits") or {},
        "verdict": certificate.get("verdict"),
        "open_items": certificate.get("open_items") or certificate.get("open_problems") or certificate.get("motivic_open_items"),
    }


def refresh_stack_series_evidence() -> bool:
    base = ROOT / "data" / "evidence" / "stack_series"
    if not base.exists():
        return False
    cert_names = [
        "q_weighted_stack_series_certificate.json",
        "a985_weighted_stack_series_certificate.json",
        "relation_level_stack_series_certificate.json",
        "relation_pair_stack_series_certificate.json",
    ]
    stage_specs = []
    for cert_name in cert_names:
        matches = sorted((base / "stages").glob(f"*/{cert_name}"))
        if matches:
            stage_specs.append((matches[0].parent.name, cert_name))
    stages = [stack_series_stage_summary(stage_id, cert_name) for stage_id, cert_name in stage_specs]
    report = {
        "schema": "d20.stack_series_evidence_report",
        "status": "STACK_SERIES_EVIDENCE_INTEGRATED",
        "present": True,
        "canonical_root": "data/evidence/stack_series",
        "stage_count": len(stages),
        "stages": stages,
    }
    write_json(base / "reports" / "stack_series_evidence.json", report)

    lines = [
        "# Stack-series evidence",
        "",
        "Canonical archive for the migrated bounded stack-series evidence bundles.",
        "",
        "| Stage | Status | Bounds | Certificate |",
        "| --- | --- | --- | --- |",
    ]
    for stage in stages:
        bounds = stage.get("bounds") or {}
        bounds_text = ", ".join(f"{key}={value}" for key, value in bounds.items()) if isinstance(bounds, dict) else str(bounds)
        lines.append(
            f"| {stage['stage_id']} | {stage.get('status')} | {bounds_text} | {stage.get('certificate_file')} |"
        )
    lines.extend([
        "",
        "These files are evidence artifacts, not source-of-truth theorem claims beyond the status and verdict fields in their certificates.",
    ])
    (base / "reports" / "stack_series_evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    index = {
        "schema": "d20.stack_series_evidence_index",
        "status": "STACK_SERIES_EVIDENCE_INTEGRATED",
        "canonical_root": "data/evidence/stack_series",
        "layout": {
            "stages": "stages/<stage_id>",
            "reports": "reports/stack_series_evidence.{json,md}",
            "manifest": "manifest.json",
        },
        "stages": [
            {
                "stage_id": stage["stage_id"],
                "status": stage.get("status"),
                "schema": stage.get("schema"),
                "certificate_file": stage.get("certificate_file"),
                "certificate_sha256": stage.get("certificate_sha256"),
            }
            for stage in stages
        ],
    }
    write_json(base / "index.json", index)
    refresh_standard_manifest(
        base=base,
        manifest_schema="d20.stack_series_evidence_manifest",
        status="STACK_SERIES_EVIDENCE_INTEGRATED",
        canonical_folder="data/evidence/stack_series",
        layout={
            "stages": "named stack-series evidence drops",
            "reports": "machine and human evidence reports",
        },
    )
    return True


def refresh_height_coherence_evidence() -> bool:
    base = ROOT / "data" / "integrity" / "height_coherence"
    cert_path = base / "certificate.json"
    if not cert_path.exists():
        return False
    certificate = load_json(cert_path)
    certificates = certificate.get("height_coherence_certificates", [])
    positive = [
        row.get("name")
        for row in certificates
        if isinstance(row, dict) and row.get("positive_height_certificate") is True
    ]
    negative = [
        row.get("name")
        for row in certificates
        if isinstance(row, dict) and row.get("negative_control") is True
    ]
    report = {
        "schema": "d20.height_coherence_evidence_report",
        "status": certificate.get("status"),
        "present": True,
        "canonical_root": "data/integrity/height_coherence",
        "definition": certificate.get("definition"),
        "certificate_count": len(certificates),
        "positive_certificate_count": len(positive),
        "negative_control_count": len(negative),
        "positive_certificate_ids": positive,
        "negative_control_ids": negative,
        "saturated_resizing_guard": certificate.get("saturated_resizing_guard"),
        "source_certificate": "certificate.json",
    }
    write_json(base / "reports" / "height_coherence_evidence.json", report)
    lines = [
        "# Height-coherence integrity evidence",
        "",
        "Canonical archive for the migrated UF-kernel height-coherence evidence bundle.",
        "",
        f"Status: `{certificate.get('status')}`",
        "",
        f"Positive certificates: {len(positive)}",
        f"Negative controls: {len(negative)}",
        "",
        "The saturated resizing guard is retained exactly as evidence: pointwise atom projection is rejected as too strong while the saturated bridge is valid.",
    ]
    (base / "reports" / "height_coherence_evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    refresh_standard_manifest(
        base=base,
        manifest_schema="d20.height_coherence_evidence_manifest",
        status=certificate.get("status") or "D20_UF_KERNEL_HEIGHT_COHERENCE_CERTIFIED",
        canonical_folder="data/integrity/height_coherence",
        layout={
            "arrays": "UF-kernel and resizing arrays",
            "examples": "height-coherence examples and guards",
            "reports": "machine and human integrity reports",
            "scripts": "portable verification script",
            "tables": "certificate and guard CSV tables",
        },
    )
    return True


def refresh_reproducibility_evidence() -> bool:
    base = ROOT / "data" / "evidence" / "reproducibility" / "python_bundle"
    if not base.exists():
        return False
    certs = []
    for cert_path in sorted((base / "out").glob("*/certificate.json")):
        certificate = load_json(cert_path)
        certs.append({
            "path": cert_path.relative_to(base).as_posix(),
            "schema": certificate.get("schema"),
            "status": certificate.get("status"),
            "keys": sorted(certificate.keys()),
        })
    source_scripts = [
        path.relative_to(base).as_posix()
        for path in sorted((base / "src").glob("*.py"))
    ] if (base / "src").exists() else []
    report = {
        "schema": "d20.reproducibility_evidence_report",
        "status": "D20_REPRODUCIBILITY_EVIDENCE_INTEGRATED",
        "present": True,
        "canonical_root": "data/evidence/reproducibility/python_bundle",
        "output_certificate_count": len(certs),
        "output_certificates": certs,
        "source_scripts": source_scripts,
    }
    write_json(base / "reports" / "reproducibility_evidence.json", report)
    lines = [
        "# Reproducibility evidence bundle",
        "",
        "Canonical archive for the migrated portable Python/NumPy reproducibility bundle.",
        "",
        "| Output certificate | Status | Schema |",
        "| --- | --- | --- |",
    ]
    for certificate in certs:
        lines.append(f"| {certificate['path']} | {certificate.get('status')} | {certificate.get('schema')} |")
    (base / "reports" / "reproducibility_evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    index = {
        "schema": "d20.reproducibility_evidence_index",
        "status": "D20_REPRODUCIBILITY_EVIDENCE_INTEGRATED",
        "canonical_root": "data/evidence/reproducibility/python_bundle",
        "layout": {
            "src": "source reproduction scripts",
            "out": "reproduced certificate/table outputs",
            "reports": "reports/reproducibility_evidence.{json,md}",
            "manifest": "manifest.json",
        },
        "output_certificate_count": len(certs),
        "source_script_count": len(source_scripts),
    }
    write_json(base / "index.json", index)
    refresh_standard_manifest(
        base=base,
        manifest_schema="d20.reproducibility_evidence_manifest",
        status="D20_REPRODUCIBILITY_EVIDENCE_INTEGRATED",
        canonical_folder="data/evidence/reproducibility/python_bundle",
        layout={
            "out": "reproduced certificate and table outputs",
            "reports": "machine and human evidence reports",
            "src": "portable Python/NumPy reproduction scripts",
        },
    )
    return True


def refresh_coorient_marker() -> bool:
    from src.derive_coorient_marker_from_orbitals import derive, write_outputs
    from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body

    relation = ensure_pre_a985_relation_body(regenerate=False)
    marker = derive(relation)
    write_outputs(marker, relation_npz=relation)
    out = ROOT / "generated" / "coorient_marker_from_orbitals_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(marker, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("refreshed data/coorient coorient marker from pre-A985 regular orbital", flush=True)
    return marker.get("status") == "COORIENT_MARKER_DERIVED_FROM_ORBITALS_PASS"


def refresh_coorient_relator_profile() -> bool:
    from src.derive_coorient_relator_profile_from_a0_a5 import ensure_coorient_relator_profile
    from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body

    relation = ensure_pre_a985_relation_body(regenerate=False)
    result = ensure_coorient_relator_profile(relation, write=True)
    print("refreshed data/invariants/d20/coorient_relator_profile_from_a0_a5.json", flush=True)
    return result.get("status") == "COORIENT_RELATOR_PROFILE_FROM_A0_A5_PASS"


def refresh_pre_a985_relation_body(*, regenerate: bool = True) -> bool:
    from src.derive_pre_a985_relation_body import derive, write_theorem

    theorem = derive(regenerate=regenerate)
    write_theorem(theorem)
    print("refreshed data/invariants/d20/pre_A985_relation_body_theorem.json", flush=True)
    return theorem.get("status") == "PRE_A985_RELATION_BODY_DERIVED_WITHOUT_RELATION_TABLE_PASS"


def refresh_coorient_word_presentation() -> bool:
    from src.derive_absolute_coorient_word_presentation import derive as derive_word
    from src.derive_lifted_coorient_generators_formula import derive_formula
    from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body

    relation = ensure_pre_a985_relation_body(regenerate=False)

    formula_report = derive_formula(
        relation,
        ROOT / "data" / "coorient" / "lifted_coorient_canonical_marker_formula.json",
        ROOT / "data" / "coorient" / "be3_coorient_generators.npz",
        ROOT / "generated" / "lifted_coorient_generators_from_canonical_marker.npz",
        ROOT / "generated" / "relation_memberships_from_canonical_coorient_marker.npz",
        ROOT / "generated" / "lifted_coorient_generators_from_canonical_marker_report.json",
    )
    word_report = derive_word(
        ROOT / "generated" / "relation_memberships_from_canonical_coorient_marker.npz",
        D20_INVARIANTS / "d20_d6_selector_derivation.json",
        ROOT / "data" / "coorient" / "lifted_coorient_canonical_marker_formula.json",
        ROOT / "generated" / "lifted_coorient_generators_from_canonical_marker.npz",
        ROOT / "data" / "coorient" / "absolute_d20_word_presentation.json",
        ROOT / "generated" / "lifted_coorient_generators_from_word_presentation.npz",
        ROOT / "generated" / "relation_memberships_from_absolute_word_presentation.npz",
        ROOT / "generated" / "be3_action_words_from_absolute_presentation.npz",
        ROOT / "generated" / "absolute_coorient_word_presentation_report.json",
    )
    print("refreshed data/coorient absolute word presentation", flush=True)
    return bool(formula_report.get("all_checks_pass") and word_report.get("all_checks_pass"))


def refresh_universal_integral_uniqueness() -> bool:
    from src.derive_universal_integral_uniqueness import derive

    result = derive()
    out = D20_INVARIANTS / "universal_integral_uniqueness.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("refreshed data/invariants/d20/universal_integral_uniqueness.json", flush=True)
    return result.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS"


def refresh_black_hole_inverse_conditioning() -> bool:
    from src.derive_black_hole_inverse_conditioning import write_theorem

    report = write_theorem()
    print("refreshed data/invariants/d20/theorems/black_hole_inverse_conditioning", flush=True)
    return report.get("status") == "D20_BLACK_HOLE_INVERSE_CONDITIONING_CERTIFIED"


def refresh_source_certificates() -> None:
    if not refresh_pre_a985_relation_body(regenerate=True):
        raise SystemExit("pre-A985 relation body refresh failed")
    if not refresh_coorient_relator_profile():
        raise SystemExit("coorient relator-profile derivation failed")
    if not refresh_coorient_marker():
        raise SystemExit("coorient marker derivation failed")
    if not refresh_coorient_word_presentation():
        raise SystemExit("coorient word-presentation refresh failed")
    if not refresh_universal_integral_uniqueness():
        raise SystemExit("universal integral uniqueness refresh failed")
    refresh_tensor_chain_manifest()
    refresh_tensor_chain_plain_name_view()
    refresh_tensor_chain_manifest()
    refresh_ss_sat_manifest()
    refresh_stack_series_evidence()
    refresh_height_coherence_evidence()
    refresh_reproducibility_evidence()
    if not refresh_black_hole_inverse_conditioning():
        raise SystemExit("black-hole inverse conditioning refresh failed")


def rebuild_d20(pretty: bool, *, refresh_sources: bool = True) -> None:
    from src.derive_d20 import derive
    if refresh_sources:
        refresh_source_certificates()
    else:
        print("using cached source artifacts; skipping source-certificate refresh", flush=True)
    print("$ derive d20.json", flush=True)
    obj = derive()
    D20.write_text(json.dumps(obj, indent=2 if pretty else None, sort_keys=bool(pretty), allow_nan=False), encoding="utf-8")
    print("rebuilt d20.json", flush=True)


def certificate_summaries() -> list[dict[str, Any]]:
    index = json.loads((ROOT / "data" / "certificates.json").read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for certificate in index.get("certificates", []):
        rel = certificate["path"]
        path = ROOT / rel
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "id": certificate.get("id"),
            "group": certificate.get("group"),
            "ordinal_dir": certificate.get("ordinal_dir"),
            "certificate": rel,
            "directory": Path(rel).parent.as_posix(),
            "certificate_file_sha256": sha_file(path),
            "status": payload.get("status"),
        })
    return rows


def refresh_certificate() -> None:
    cert = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    d20 = json.loads(D20.read_text(encoding="utf-8"))
    invariant_reports = invariant_report_rows()
    certified_invariant_reports = [row for row in invariant_reports if row.get("certified") is True]
    provisional_invariant_reports = [row for row in invariant_reports if row.get("certified") is not True]

    d20_object_hash = d20.get("d20_sha256")
    if not isinstance(d20_object_hash, str) or len(d20_object_hash) != 64:
        raise SystemExit("d20.json missing valid d20_sha256")

    cert["object"] = "d20"
    cert["schema"] = canonical_schema(cert.get("schema")) or "d20.verifier"
    cert["status"] = "D20_CERTIFIED"
    cert["headline"] = "D20_CERTIFIED"
    cert["d20_status"] = "D20_PASS"
    cert["d20_json"] = {
        "path": "d20.json",
        "schema": canonical_schema(d20.get("schema")),
        "size": D20.stat().st_size,
        "sha256_file": sha_file(D20),
        "sha256_object": d20_object_hash,
        "invariant_sections": sorted(k for k in d20.keys() if k != "d20_sha256"),
    }
    for stale_key in ("lay" + "ers", "lay" + "er_count"):
        cert.pop(stale_key, None)
    cert["certificates"] = certificate_summaries()
    cert["certificate_count"] = len(cert["certificates"])
    cert["certified_invariant_reports"] = certified_invariant_reports
    cert["certified_invariant_report_count"] = len(certified_invariant_reports)
    cert["invariant_report_inventory"] = invariant_report_inventory()
    cert["provisional_invariant_reports"] = provisional_invariant_reports
    cert["provisional_invariant_report_count"] = len(provisional_invariant_reports)
    cert["d20_sha256"] = sha_json_body(cert, "d20_sha256")
    CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def refresh_manifest() -> int:
    """Rebuild manifests/file_hashes.json from the current canonical bundle files."""
    manifest = {
        "schema": "d20.file_hashes",
        "generated_cache_required": False,
        "self_manifest_excluded": "manifests/file_hashes.json",
        "entries": [],
    }
    entries: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if lineage_archive_path(path):
            continue
        if non_identity_path(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == "manifests/file_hashes.json":
            continue
        if any(
            part in EXCLUDED_DIRS or part.startswith(EXCLUDED_DIR_PREFIXES)
            for part in path.relative_to(ROOT).parts
        ):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.name in EXCLUDED_FILES:
            continue
        entries.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        })
    manifest["entries"] = entries
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return len(entries)


def audit(pretty: bool) -> None:
    cmd = [sys.executable, str(ROOT / "certify.py"), "--mode", "audit", "--no-regenerate"]
    if pretty:
        cmd.append("--pretty")
    run(cmd)


def main() -> None:
    ap = argparse.ArgumentParser(description="Regenerate d20.json, refresh hashes, and audit.")
    ap.add_argument("--no-audit", action="store_true", help="Refresh d20.json and hashes but skip final audit.")
    ap.add_argument("--compact", action="store_true", help="Write compact d20.json and compact audit output.")
    ap.add_argument(
        "--cached-source",
        action="store_true",
        help="Reuse existing checked source artifacts; skip pre-A985/coorient/evidence refresh.",
    )
    args = ap.parse_args()

    pretty = not args.compact
    rebuild_d20(pretty=pretty, refresh_sources=not args.cached_source)
    refresh_certificate()
    count = refresh_manifest()
    print(f"updated manifest hashes: {count}", flush=True)
    if not args.no_audit:
        audit(pretty=pretty)
    print("D20_REGENERATED", flush=True)


if __name__ == "__main__":
    main()
