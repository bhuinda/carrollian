from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_final_multifusion_certificate import (
        CORE_A985_JSON,
        EXPECTED_STATUSES,
        INDEX_PATH,
        OUT_DIR,
        REPORTS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_final_multifusion_certificate import (
        CORE_A985_JSON,
        EXPECTED_STATUSES,
        INDEX_PATH,
        OUT_DIR,
        REPORTS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_final_multifusion_certificate() -> dict[str, Any]:
    expected = build_payloads()

    theorem_certificate = load_json(OUT_DIR / "theorem_certificate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    index = load_json(INDEX_PATH)

    if theorem_certificate != expected["theorem_certificate"]:
        raise AssertionError("theorem_certificate.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.final_multifusion_certificate@1":
        raise AssertionError("C985 final report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 final multi-fusion certificate is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 final all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 final report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 final report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 final report is not reproducible")

    checks = report.get("checks", {})
    missing = sorted(key for key, passed in checks.items() if passed is not True)
    if missing:
        raise AssertionError(f"C985 final checks are not true: {missing}")

    layer_statuses = theorem_certificate.get("layer_statuses", {})
    for name, status in EXPECTED_STATUSES.items():
        if layer_statuses.get(name) != status:
            raise AssertionError(f"C985 prerequisite status mismatch for {name}")

    witness = report.get("witness", {})
    if witness.get("simple_count") != 985:
        raise AssertionError("C985 final simple count mismatch")
    if witness.get("fusion_tensor_support") != 1414965:
        raise AssertionError("C985 final fusion support mismatch")
    if witness.get("fusion_coefficient_total") != 2537360:
        raise AssertionError("C985 final fusion coefficient total mismatch")
    if witness.get("pentagon_length_four_chain_count") != 16837352591360:
        raise AssertionError("C985 final pentagon chain count mismatch")
    if witness.get("zigzag_simple_count") != 985 or witness.get("zigzag_failure_count") != 0:
        raise AssertionError("C985 final zig-zag witness mismatch")
    certifies = report.get("closure_boundary", {}).get("certifies", [])
    if "finite semisimple multi-fusion category status for C985" not in certifies:
        raise AssertionError("C985 final theorem status is not in closure boundary")

    inputs = report.get("inputs", {})
    for name, path in REPORTS.items():
        assert_file_hash(inputs.get(name, {}), path, f"{name} input")
    assert_file_hash(inputs.get("core_a985", {}), CORE_A985_JSON, "core A985 input")

    if manifest.get("schema") != "c985.proof_obligation.final_multifusion_certificate_manifest@1":
        raise AssertionError("C985 final manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 final manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 final manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 final certificate missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 final index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 final index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.final_multifusion_certificate@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "theorem_status": report.get("status"),
        "simple_count": witness.get("simple_count"),
        "fusion_tensor_support": witness.get("fusion_tensor_support"),
        "pentagon_length_four_chain_count": witness.get("pentagon_length_four_chain_count"),
        "zigzag_failure_count": witness.get("zigzag_failure_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_final_multifusion_certificate()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
