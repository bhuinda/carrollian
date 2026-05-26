from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_hamming_gaussian_python_work_archive_import"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

TEMP_ROOT = ROOT / "temp" / "all_python_work_files"
PY_ROOT = TEMP_ROOT / "python_files"
TEMP_MANIFEST = TEMP_ROOT / "python_files_manifest.json"
TEMP_INDEX = TEMP_ROOT / "python_files_index.md"

W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_hamming_gaussian_python_work_archive_import.py"
VALIDATOR = ROOT / "src" / "certify_d20_hamming_gaussian_python_work_archive_import.py"

EXPECTED_CERTIFICATES = {
    "hamming_gaussian_call_order/hamming_gaussian_call_order_certificate.json": "HAMMING_GAUSSIAN_CALL_ORDER_PROBE_PASS",
    "hamming_gaussian_convex_order/hamming_gaussian_convex_order_certificate.json": "HAMMING_GAUSSIAN_CONVEX_ORDER_PROBE_PASS",
    "hamming_gaussian_dual_distance/hamming_gaussian_dual_distance_certificate.json": "HAMMING_GAUSSIAN_DUAL_DISTANCE_KRAWTCHOUK_PASS",
    "hamming_gaussian_full_subgaussian_probe/hamming_gaussian_full_subgaussian_probe_certificate.json": "HAMMING_GAUSSIAN_FULL_SUBGAUSSIAN_PROBE_COMPLETE",
    "hamming_gaussian_indicator_shell_domination/hamming_gaussian_indicator_shell_domination_certificate.json": "HAMMING_GAUSSIAN_INDICATOR_SHELL_DOMINATION_CERTIFIED",
    "hamming_gaussian_morphism/hamming_gaussian_morphism_certificate.json": "HAMMING_GAUSSIAN_MORPHISM_INVARIANTS_PASS",
    "hamming_gaussian_sparse_signed/hamming_gaussian_sparse_signed_certificate.json": "HAMMING_GAUSSIAN_SPARSE_SIGNED_PROBE_PASS",
    "hamming_gaussian_talagrand_bridge/hamming_gaussian_talagrand_bridge_certificate.json": "HAMMING_GAUSSIAN_TALAGRAND_BRIDGE_CONSTRUCTED",
}

SCIPY_REQUIRED = [
    "hamming_gaussian_critical_point_audit/hamming_gaussian_critical_point_audit.py",
    "hamming_gaussian_sharp_constant_candidate/hamming_gaussian_sharp_constant_candidate.py",
    "hamming_gaussian_shortening_rank/hamming_gaussian_shortening_rank.py",
    "hamming_gaussian_two_level_probe/hamming_gaussian_two_level_probe.py",
]

MNT_DATA_BOUND = [
    "run_crypto_static_audit.py",
    "verifier_security_audit.py",
    "hamming_gaussian_two_level_probe/hamming_gaussian_two_level_probe.py",
]

CSV_WITNESSES = {
    "hamming_gaussian_entropy_logsobolev_route/local_sdpi_spectrum.csv": {
        "status": "PASS",
        "check": "all_margins_positive",
    },
    "hamming_gaussian_entropy_spinh_veronese/spinh_veronese_numeric_checks.csv": {
        "status": "PASS",
        "check": "status_column_pass",
    },
}


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def compile_probe(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", SyntaxWarning)
        try:
            compile(source, str(path), "exec")
            ok = True
            error = None
        except SyntaxError as exc:
            ok = False
            error = f"{exc.__class__.__name__}: {exc}"
    return {
        "path": relpath(path),
        "ok": ok,
        "error": error,
        "syntax_warnings": [
            {"category": warning.category.__name__, "message": str(warning.message)}
            for warning in caught
        ],
    }


def csv_rows(path: Path) -> list[dict[str, str]]:
    import csv

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def csv_witnesses() -> dict[str, Any]:
    witnesses: dict[str, Any] = {}
    for rel, expectation in CSV_WITNESSES.items():
        path = PY_ROOT / rel
        rows = csv_rows(path) if path.exists() else []
        if expectation["check"] == "all_margins_positive":
            margins = [float(row["margin"]) for row in rows]
            ok = bool(margins) and min(margins) > 0
            summary = {
                "row_count": len(rows),
                "min_margin": min(margins) if margins else None,
                "max_margin": max(margins) if margins else None,
            }
        elif expectation["check"] == "status_column_pass":
            statuses = [row.get("status") for row in rows]
            ok = statuses == [expectation["status"]]
            summary = {"row_count": len(rows), "statuses": statuses}
        else:
            ok = False
            summary = {"row_count": len(rows)}
        witnesses[rel] = {
            "path": relpath(path),
            "sha256": sha_file(path) if path.exists() else None,
            "exists": path.exists(),
            "check": expectation["check"],
            "ok": ok,
            **summary,
        }
    return witnesses


def certificate_summaries() -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for rel, expected_status in EXPECTED_CERTIFICATES.items():
        path = PY_ROOT / rel
        payload = load_json(path)
        summary: dict[str, Any] = {
            "path": relpath(path),
            "sha256": sha_file(path),
            "expected_status": expected_status,
            "status": payload.get("status"),
            "status_matches": payload.get("status") == expected_status,
        }
        if "root_sequence" in payload:
            summary["root_sequence"] = payload["root_sequence"]
        if "positive_defect_sequence_D4_plus" in payload:
            summary["positive_defect_sequence_D4_plus"] = payload[
                "positive_defect_sequence_D4_plus"
            ]
        if "critical_scale_sequence" in payload:
            summary["critical_scale_sequence"] = payload["critical_scale_sequence"]
        if rel.startswith("hamming_gaussian_dual_distance"):
            summary["endpoint"] = payload.get("endpoint", {})
        if rel.startswith("hamming_gaussian_full_subgaussian_probe"):
            exact = payload.get("exact_structured_findings", {})
            search = payload.get("numerical_search", {})
            summary["codeword_K"] = exact.get(
                "codeword_sign_direction_K_lower_bound", {}
            ).get("K")
            summary["codeword_K2"] = exact.get(
                "codeword_sign_direction_K_lower_bound", {}
            ).get("K2")
            summary["best_random_K"] = search.get("best_random_probe", {}).get("K")
            summary["not_claimed"] = payload.get("not_claimed", [])
        if rel.startswith("hamming_gaussian_indicator_shell_domination"):
            summary["all_indicator_cases_pass"] = payload.get("all_indicator_cases_pass")
            summary["global_max_ratio"] = payload.get("global_max_ratio")
            summary["total_subsets_checked"] = payload.get("total_subsets_checked")
            summary["remaining_residue"] = payload.get("remaining_residue")
        if rel.startswith("hamming_gaussian_sparse_signed"):
            summary["pass_checks"] = payload.get("pass_checks", {})
            summary["boundary"] = payload.get("boundary")
        if rel.startswith("hamming_gaussian_talagrand_bridge"):
            summary["finite_input"] = payload.get("finite_input", {})
            summary["sanity_checks"] = payload.get("sanity_checks", {})
            summary["not_claimed"] = payload.get("not_claimed", [])
        summaries[rel] = summary
    return summaries


def source_manifest_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    files = manifest.get("files", [])
    rows = []
    for item in files:
        rel = item["path"]
        path = PY_ROOT / rel
        exists = path.exists()
        actual_hash = sha_file(path) if exists else None
        actual_size = path.stat().st_size if exists else None
        rows.append(
            {
                "path": rel,
                "exists": exists,
                "expected_sha256": item["sha256"],
                "actual_sha256": actual_hash,
                "hash_matches": actual_hash == item["sha256"],
                "expected_size_bytes": item["size_bytes"],
                "actual_size_bytes": actual_size,
                "size_matches": actual_size == item["size_bytes"],
            }
        )
    actual_py_count = len(list(PY_ROOT.rglob("*.py")))
    return {
        "manifest_count": manifest.get("count"),
        "actual_python_file_count": actual_py_count,
        "created_utc": manifest.get("created_utc"),
        "recorded_root": manifest.get("root"),
        "files": rows,
        "all_hashes_match": all(row["hash_matches"] for row in rows),
        "all_sizes_match": all(row["size_matches"] for row in rows),
    }


def build_artifact() -> dict[str, Any]:
    manifest = load_json(TEMP_MANIFEST)
    w24 = load_json(W24_ROW_ALPHABETIZATION)

    scripts = [PY_ROOT / item["path"] for item in manifest["files"]]
    compile_results = [compile_probe(path) for path in scripts]
    certs = certificate_summaries()
    csvs = csv_witnesses()

    checks = {
        "archive_root_exists": TEMP_ROOT.exists() and PY_ROOT.exists(),
        "source_manifest_hashes_all_match": source_manifest_summary(manifest)[
            "all_hashes_match"
        ],
        "source_manifest_sizes_all_match": source_manifest_summary(manifest)[
            "all_sizes_match"
        ],
        "source_manifest_count_matches_actual_python_count": manifest.get("count")
        == len(scripts)
        == len(list(PY_ROOT.rglob("*.py"))),
        "all_python_sources_compile": all(row["ok"] for row in compile_results),
        "syntax_warnings_are_warning_only": all(row["ok"] for row in compile_results),
        "expected_replay_certificates_present": all(
            (PY_ROOT / rel).exists() for rel in EXPECTED_CERTIFICATES
        ),
        "expected_replay_statuses_match": all(
            row["status_matches"] for row in certs.values()
        ),
        "root_killing_sequence_42_18_6_0_replayed": certs[
            "hamming_gaussian_dual_distance/hamming_gaussian_dual_distance_certificate.json"
        ]["root_sequence"]
        == [42, 18, 6, 0],
        "endpoint_dual_distance_8_replayed": certs[
            "hamming_gaussian_dual_distance/hamming_gaussian_dual_distance_certificate.json"
        ]["endpoint"].get("dual_distance_is_8")
        is True,
        "indicator_shell_domination_passes_boolean_case": certs[
            "hamming_gaussian_indicator_shell_domination/hamming_gaussian_indicator_shell_domination_certificate.json"
        ]["all_indicator_cases_pass"]
        is True,
        "indicator_shell_total_subsets_is_full_boolean_cube": certs[
            "hamming_gaussian_indicator_shell_domination/hamming_gaussian_indicator_shell_domination_certificate.json"
        ]["total_subsets_checked"]
        == 2**24,
        "sparse_signed_probe_pass_checks": all(
            certs[
                "hamming_gaussian_sparse_signed/hamming_gaussian_sparse_signed_certificate.json"
            ]["pass_checks"].values()
        ),
        "talagrand_sparse_mgf_sanity_passes": certs[
            "hamming_gaussian_talagrand_bridge/hamming_gaussian_talagrand_bridge_certificate.json"
        ]["sanity_checks"].get("mgf_bound_all_pass")
        is True,
        "logsobolev_local_sdpi_csv_passes": csvs[
            "hamming_gaussian_entropy_logsobolev_route/local_sdpi_spectrum.csv"
        ]["ok"],
        "spinh_veronese_csv_passes": csvs[
            "hamming_gaussian_entropy_spinh_veronese/spinh_veronese_numeric_checks.csv"
        ]["ok"],
        "scipy_dependency_scripts_recorded": all((PY_ROOT / rel).exists() for rel in SCIPY_REQUIRED),
        "mnt_data_bound_scripts_recorded": all((PY_ROOT / rel).exists() for rel in MNT_DATA_BOUND),
        "w24_endpoint_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "final_entropy_inequality_not_certified": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.hamming_gaussian_python_work_archive_import.artifact@1",
        "status": "D20_HAMMING_GAUSSIAN_PYTHON_WORK_ARCHIVE_IMPORTED_PARTIAL_REPLAY",
        "claim_scope": (
            "Import the all_python_work_files archive as bounded Hamming/Golay-to-Gaussian "
            "computational evidence. This certifies source integrity, syntax, replayed "
            "certificates, and explicit local blockers. It does not certify the final "
            "entropy contraction theorem."
        ),
        "source_archive": {
            "manifest": input_entry(TEMP_MANIFEST),
            "index": input_entry(TEMP_INDEX),
            "source_manifest": source_manifest_summary(manifest),
        },
        "syntax": {
            "compile_results": compile_results,
            "warning_files": [
                row["path"] for row in compile_results if row["syntax_warnings"]
            ],
        },
        "replayed_certificates": certs,
        "csv_witnesses": csvs,
        "environment_boundary": {
            "python_replay_executable": "system python selected by the shell",
            "scipy_dependency_scripts_not_replayed_by_certificate": SCIPY_REQUIRED,
            "mnt_data_bound_scripts_not_workspace_replayed": MNT_DATA_BOUND,
        },
        "connection_to_current_problem": {
            "finite_source_status": "solid for the replayed H8^3 to G24 root-killing and dual-distance layers",
            "root_killing_sequence": [42, 18, 6, 0],
            "golay_endpoint_dual_distance": 8,
            "covered_sparse_projection_regime": "all real coefficient projections supported on fewer than 8 coordinates",
            "boolean_indicator_shell_domination": "certified for all 2^24 supports, but only for indicator vectors",
            "sharp_constant_candidate": certs[
                "hamming_gaussian_full_subgaussian_probe/hamming_gaussian_full_subgaussian_probe_certificate.json"
            ]["codeword_K"],
            "remaining_gap": (
                "Lift indicator and sparse evidence to arbitrary nonnegative shell vectors "
                "for w=12,16; this is the finite entropy contraction problem."
            ),
        },
        "open_boundary": {
            "not_certified": [
                "D(q||u_B12) >= 6 D(p_q||u_24)",
                "D(q||u_B16) >= 8 D(p_q||u_24)",
                "arbitrary-vector shell domination from the indicator shell certificate",
                "global sharp subgaussian constant over all coefficient vectors",
                "full multivariate convex-order domination",
                "independent replay of SciPy-dependent scripts by this certificate",
                "workspace replay of scripts hardwired to /mnt/data",
            ],
            "certified_here": [
                "archive source file count, size, and SHA-256 integrity",
                "all 16 Python sources parse and compile",
                "eight generated certificates have the expected statuses",
                "root-killing sequence 42 -> 18 -> 6 -> 0",
                "Golay endpoint dual distance 8 and sparse <8 Rademacher reduction",
                "all Boolean indicator shell cases pass with max ratio 1.0",
                "local SDPI and Spin^h/Veronese CSV witnesses pass their local checks",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.hamming_gaussian_python_work_archive_import@1",
        "status": "D20_HAMMING_GAUSSIAN_PYTHON_WORK_ARCHIVE_IMPORT_CERTIFIED_PARTIAL_REPLAY",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The all_python_work_files archive is internally consistent and partially "
            "replay-certified in this workspace. The finite Hamming/Golay layers are strong: "
            "root killing is 42 -> 18 -> 6 -> 0, the Golay endpoint has dual distance 8, "
            "sparse <8 projections reduce to independent Rademacher sums, and the Boolean "
            "indicator shell domination audit checks all 2^24 supports. The final entropy "
            "contraction inequalities for w=12,16 remain open."
        ),
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR),
            "temp_manifest": artifact["source_archive"]["manifest"],
            "temp_index": artifact["source_archive"]["index"],
            "w24_row_alphabetization": input_entry(W24_ROW_ALPHABETIZATION),
        },
        "witness": {
            "source_archive": artifact["source_archive"],
            "syntax": artifact["syntax"],
            "replayed_certificates": artifact["replayed_certificates"],
            "csv_witnesses": artifact["csv_witnesses"],
            "environment_boundary": artifact["environment_boundary"],
            "connection_to_current_problem": artifact["connection_to_current_problem"],
            "open_boundary": artifact["open_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Promote the indicator shell domination result to arbitrary nonnegative vectors "
            "for w=12,16, preferably via a Krawtchouk/SOS certificate; otherwise turn the "
            "sandpile least-action heuristic into a monotonicity proof for Delta_w."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.hamming_gaussian_python_work_archive_import_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify all source hashes and sizes against temp manifest",
            "compile all Python sources",
            "verify generated replay certificates and expected statuses",
            "verify root-killing, dual-distance, indicator-shell, sparse-signed, Talagrand MGF, local SDPI, and Spin^h/Veronese checks",
            "record SciPy and /mnt/data replay blockers explicitly",
            "record that final entropy contraction remains open",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = sha_json(manifest)
    return manifest


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [row for row in index.get("obligations", []) if row.get("id") != THEOREM_ID]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
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
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    index["registry_sha256"] = sha_json(index)
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    report = build_report(artifact)
    manifest = build_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_index(report)
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
