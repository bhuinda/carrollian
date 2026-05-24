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
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime

ensure_numpy_runtime(ROOT, __file__)

from src.paths import MANIFESTS, ROOT

MANIFEST = MANIFESTS / "file_hashes.json"
D20 = ROOT / "d20.json"
CERTIFICATE = ROOT / "certificate.json"

EXCLUDED_DIRS = {
    ".git",
    ".codex_deps",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tools",
    ".venv",
    ".msys-tmp",
    "__pycache__",
    "a236_compute_py_bundle",
    "d20_coherent_annihilator_verifier_bundle",
    "d20_coherent_annihilator_verifier_bundle_v3",
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
    "test.zip",
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json_body(obj: dict[str, Any], hash_key: str) -> str:
    body = {k: v for k, v in obj.items() if k != hash_key}
    return hashlib.sha256(canonical(body)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(cmd), flush=True)
    if capture:
        return subprocess.run(cmd, cwd=ROOT, text=True, check=check, capture_output=True)
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def refresh_tensor_chain_plain_name_view() -> bool:
    base = ROOT / "data" / "evidence" / "tensor_chain"
    if not base.exists():
        return False
    from src.derive_tensor_chain_plain_names import OUT, derive

    OUT.write_text(json.dumps(derive(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        rel = path.relative_to(base).as_posix()
        files[rel] = {
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        }
    manifest = {
        "schema": "d20.tensor_chain.manifest.v2",
        "status": "TENSOR_CHAIN_MANIFEST_REFRESHED",
        "canonical_folder": "data/evidence/tensor_chain",
        "layout": {
            "arrays": "NPZ array payloads",
            "reports": "machine and human report files",
            "stages": "versioned and named experiment stages",
            "tables": "CSV evidence tables",
        },
        "file_count": len(files),
        "files": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        rel = path.relative_to(base).as_posix()
        if rel.startswith("source_archives/legacy_roots/"):
            continue
        files[rel] = {
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        }
    manifest = {
        "schema": "d20.ss_sat.manifest.v1",
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
            "scripts": "versioned evidence analysis and extraction scripts",
            "source_archives": "zip evidence bundles plus local-only archived staging roots",
            "source_versions": "versioned provenance copied from consolidated gnatural drops",
            "tables": "CSV evidence summaries",
        },
        "file_count": len(files),
        "files": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("refreshed data/evidence/ss_sat/manifest.json", flush=True)
    return True


def refresh_coorient_marker() -> bool:
    from src.derive_coorient_marker_from_orbitals import derive, write_outputs
    from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body

    relation = ensure_pre_a985_relation_body(regenerate=False)
    marker = derive(relation)
    write_outputs(marker, relation_npz=relation)
    out = ROOT / "generated" / "coorient_marker_from_orbitals_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("refreshed data/coorient coorient marker from pre-A985 regular orbital", flush=True)
    return marker.get("status") == "COORIENT_MARKER_DERIVED_FROM_ORBITALS_PASS"


def refresh_coorient_relator_profile() -> bool:
    from src.derive_coorient_relator_profile_from_a0_a5 import ensure_coorient_relator_profile
    from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body

    relation = ensure_pre_a985_relation_body(regenerate=False)
    result = ensure_coorient_relator_profile(relation, write=True)
    print("refreshed data/d20/coorient_relator_profile_from_a0_a5.json", flush=True)
    return result.get("status") == "COORIENT_RELATOR_PROFILE_FROM_A0_A5_PASS"


def refresh_pre_a985_relation_body(*, regenerate: bool = True) -> bool:
    from src.derive_pre_a985_relation_body import derive, write_theorem

    theorem = derive(regenerate=regenerate)
    write_theorem(theorem)
    print("refreshed data/d20/pre_A985_relation_body_theorem.json", flush=True)
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
        ROOT / "data" / "d20" / "d20_d6_selector_derivation.json",
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
    out = ROOT / "data" / "d20" / "universal_integral_uniqueness.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("refreshed data/d20/universal_integral_uniqueness.json", flush=True)
    return result.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS"


def rebuild_d20(pretty: bool) -> None:
    from src.derive_d20 import derive
    if not refresh_pre_a985_relation_body(regenerate=True):
        raise SystemExit("pre-A985 relation body refresh failed")
    if not refresh_coorient_relator_profile():
        raise SystemExit("coorient relator-profile derivation failed")
    if not refresh_coorient_marker():
        raise SystemExit("coorient marker derivation failed")
    if not refresh_coorient_word_presentation():
        raise SystemExit("coorient word-presentation refresh failed")
    if not refresh_coorient_relator_profile():
        raise SystemExit("coorient relator-profile derivation failed")
    if not refresh_coorient_marker():
        raise SystemExit("coorient marker derivation failed")
    if not refresh_pre_a985_relation_body(regenerate=True):
        raise SystemExit("pre-A985 relation body refresh failed")
    if not refresh_coorient_relator_profile():
        raise SystemExit("coorient relator-profile derivation failed")
    if not refresh_coorient_marker():
        raise SystemExit("coorient marker derivation failed")
    if not refresh_universal_integral_uniqueness():
        raise SystemExit("universal integral uniqueness refresh failed")
    refresh_tensor_chain_manifest()
    refresh_tensor_chain_plain_name_view()
    refresh_tensor_chain_manifest()
    refresh_ss_sat_manifest()
    print("$ derive d20.json", flush=True)
    obj = derive()
    D20.write_text(json.dumps(obj, indent=2 if pretty else None, sort_keys=bool(pretty)), encoding="utf-8")
    print("rebuilt d20.json", flush=True)


def layer_certificate_summaries() -> list[dict[str, Any]]:
    index = json.loads((ROOT / "layers" / "index.json").read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for layer in index.get("layers", []):
        rel = layer["path"]
        path = ROOT / rel
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "id": layer.get("id"),
            "group": layer.get("group"),
            "legacy_dir": layer.get("legacy_dir"),
            "legacy_path": layer.get("legacy_path"),
            "certificate": rel,
            "directory": Path(rel).parent.as_posix(),
            "certificate_file_sha256": sha_file(path),
            "status": payload.get("status"),
        })
    return rows


def refresh_certificate() -> None:
    cert = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    d20 = json.loads(D20.read_text(encoding="utf-8"))

    d20_object_hash = d20.get("d20_sha256")
    if not isinstance(d20_object_hash, str) or len(d20_object_hash) != 64:
        raise SystemExit("d20.json missing valid d20_sha256")

    cert["object"] = "d20"
    cert["status"] = "D20_CERTIFIED"
    cert["headline"] = "D20_CERTIFIED"
    cert["d20_status"] = "D20_PASS"
    cert["d20_json"] = {
        "path": "d20.json",
        "schema": d20.get("schema"),
        "size": D20.stat().st_size,
        "sha256_file": sha_file(D20),
        "sha256_object": d20_object_hash,
        "invariant_sections": sorted(k for k in d20.keys() if k != "d20_sha256"),
    }
    cert["layers"] = layer_certificate_summaries()
    cert["layer_count"] = len(cert["layers"])
    cert["d20_sha256"] = sha_json_body(cert, "d20_sha256")
    CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refresh_manifest() -> int:
    """Rebuild manifests/file_hashes.json from the current canonical bundle files."""
    manifest = {
        "schema": "d20.file_hashes.v2",
        "generated_cache_required": False,
        "self_manifest_excluded": "manifests/file_hashes.json",
        "entries": [],
    }
    entries: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
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
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    args = ap.parse_args()

    pretty = not args.compact
    rebuild_d20(pretty=pretty)
    refresh_certificate()
    count = refresh_manifest()
    print(f"updated manifest hashes: {count}", flush=True)
    if not args.no_audit:
        audit(pretty=pretty)
    print("D20_REGENERATED", flush=True)


if __name__ == "__main__":
    main()
