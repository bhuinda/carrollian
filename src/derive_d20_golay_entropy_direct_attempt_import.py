from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_golay_entropy_direct_attempt_import"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

HANDOFF_ROOT = ROOT / "data" / "evidence" / "talagrand_python_handoff"
HANDOFF_MANIFEST = HANDOFF_ROOT / "manifest.json"
DIRECT_ATTEMPT_DIR = HANDOFF_ROOT / "work" / "golay_entropy_direct_attempt"
DIRECT_ATTEMPT_CERTIFICATE = DIRECT_ATTEMPT_DIR / "golay_entropy_direct_attempt_certificate.json"
DIRECT_ATTEMPT_REPORT = DIRECT_ATTEMPT_DIR / "golay_entropy_direct_attempt_report.md"

W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
GOLAY_HAMMING_PROBE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_hamming_correspondence_probe"
    / "report.json"
)
MIXED_DUAD_PRUNE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_mixed_duad_quotient_orthogonality_prune"
    / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_entropy_direct_attempt_import.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_entropy_direct_attempt_import.py"

CSV_FILES = [
    "direct_attempt_summary.csv",
    "structured_pattern_search.csv",
    "lbfgs_multistart_search.csv",
    "kkt_sandpile_iteration_trace.csv",
    "sandpile_like_gradient_balancing.csv",
]
EXPECTED_STATUS = "DIRECT_VARIATIONAL_AND_SANDPILE_ATTEMPT_COMPLETE_NO_COUNTEREXAMPLE"


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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def handoff_file_hashes(manifest: dict[str, Any], names: list[str]) -> dict[str, Any]:
    files = manifest.get("files", {})
    rows: dict[str, Any] = {}
    for name in names:
        key = f"work/golay_entropy_direct_attempt/{name}"
        item = files.get(key)
        path = DIRECT_ATTEMPT_DIR / name
        expected = item.get("sha256") if isinstance(item, dict) else None
        rows[name] = {
            "path": relpath(path),
            "declared_in_handoff_manifest": isinstance(item, dict),
            "expected_sha256": expected,
            "actual_sha256": sha_file(path),
            "matches": expected == sha_file(path),
        }
    return rows


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def rows_from_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def numeric_column(rows: list[dict[str, str]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        try:
            values.append(float(row[key]))
        except (KeyError, TypeError, ValueError):
            pass
    return values


def csv_summary(path: Path) -> dict[str, Any]:
    rows = rows_from_csv(path)
    fields = list(rows[0]) if rows else []
    summary: dict[str, Any] = {
        "path": relpath(path),
        "row_count": len(rows),
        "fields": fields,
        "sha256": sha_file(path),
    }
    for field in fields:
        values = numeric_column(rows, field)
        if values:
            summary.setdefault("numeric_ranges", {})[field] = {
                "min": min(values),
                "max": max(values),
            }
    if "exceeds_zero" in fields:
        summary["exceeds_zero_true_count"] = sum(row.get("exceeds_zero") == "True" for row in rows)
    return summary


def shell_rows_from_summary_csv() -> list[dict[str, Any]]:
    rows = rows_from_csv(DIRECT_ATTEMPT_DIR / "direct_attempt_summary.csv")
    converted = []
    for row in rows:
        converted.append(
            {
                "shell": int(row["shell"]),
                "blocks": int(row["blocks"]),
                "best_pattern_F": float(row["best_pattern_F"]),
                "best_pattern_label": row["best_pattern_label"],
                "best_multistart_F": float(row["best_multistart_F"]),
                "best_multistart_start": int(row["best_multistart_start"]),
                "best_kkt_F": float(row["best_kkt_F"]),
                "best_kkt_start": int(row["best_kkt_start"]),
                "any_counterexample_found": row["any_counterexample_found"] == "True",
            }
        )
    return converted


def max_observed_f(csv_summaries: dict[str, Any]) -> float:
    values = []
    for summary in csv_summaries.values():
        f_range = summary.get("numeric_ranges", {}).get("F")
        if f_range:
            values.append(float(f_range["max"]))
    return max(values)


def build_artifact() -> dict[str, Any]:
    handoff_manifest = load_json(HANDOFF_MANIFEST)
    certificate = load_json(DIRECT_ATTEMPT_CERTIFICATE)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    golay_probe = load_json(GOLAY_HAMMING_PROBE)
    mixed = load_json(MIXED_DUAD_PRUNE)

    report_text = DIRECT_ATTEMPT_REPORT.read_text(encoding="utf-8")
    manifest_names = CSV_FILES + [
        "golay_entropy_direct_attempt_certificate.json",
        "golay_entropy_direct_attempt_report.md",
    ]
    manifest_hashes = handoff_file_hashes(handoff_manifest, manifest_names)
    cert_without_hash = dict(certificate)
    claimed_cert_hash = cert_without_hash.pop("certificate_sha256", None)
    repo_canonical_cert_hash = sha_json(cert_without_hash)
    csv_summaries = {
        name: csv_summary(DIRECT_ATTEMPT_DIR / name)
        for name in CSV_FILES
    }
    summary_csv_rows = shell_rows_from_summary_csv()
    certificate_summary = certificate["summary"]
    w24_hist = {
        str(weight): int(count)
        for weight, count in w24["witness"]["golay_code"]["weight_histogram"].items()
    }
    cert_hist = {str(weight): int(count) for weight, count in certificate["weight_enumerator"].items()}
    observed_max_f = max_observed_f(csv_summaries)

    checks = {
        "handoff_manifest_declares_direct_attempt_files": all(
            row["declared_in_handoff_manifest"] for row in manifest_hashes.values()
        ),
        "handoff_manifest_file_hashes_all_match": all(row["matches"] for row in manifest_hashes.values()),
        "direct_certificate_status_matches_expected": certificate["status"] == EXPECTED_STATUS,
        "handoff_report_records_no_counterexample_status": EXPECTED_STATUS in report_text,
        "certificate_summary_has_shells_12_and_16": [row["shell"] for row in certificate_summary] == [12, 16],
        "summary_csv_matches_certificate_summary": summary_csv_rows == certificate_summary,
        "no_counterexample_recorded_for_each_shell": all(
            row["any_counterexample_found"] is False for row in certificate_summary
        ),
        "all_csv_exceeds_zero_counts_are_zero": all(
            summary.get("exceeds_zero_true_count", 0) == 0 for summary in csv_summaries.values()
        ),
        "max_observed_F_within_roundoff": observed_max_f <= 3e-15,
        "w24_endpoint_is_certified": w24["status"] == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "w24_weight_enumerator_matches_direct_attempt": w24_hist == cert_hist,
        "dodecad_and_weight16_shell_sizes_match": w24_hist.get("12") == 2576
        and w24_hist.get("16") == 759,
        "golay_hamming_probe_records_morphism_open": golay_probe["candidate_morphism"][
            "morphism_status"
        ]
        == "OPEN_NOT_CONSTRUCTED",
        "sector33_w24_local_matching_still_open": mixed["checks"]["explicit_morphism_remains_open"] is True
        and mixed["checks"]["no_mixed_assignment_is_self_orthogonal"] is True,
        "handoff_internal_certificate_hash_not_used_as_repo_self_hash": claimed_cert_hash
        != repo_canonical_cert_hash,
        "final_entropy_inequality_not_certified": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_entropy_direct_attempt_import.artifact@1",
        "status": "D20_GOLAY_ENTROPY_DIRECT_ATTEMPT_IMPORTED_NO_COUNTEREXAMPLE",
        "claim_scope": (
            "Import the handoff Golay entropy direct-attempt artifact as bounded computational "
            "evidence tied to the certified W24/Golay endpoint. This is not a proof of the "
            "w=12,16 entropy contraction inequalities."
        ),
        "source_reports": {
            "handoff_manifest": input_entry(
                HANDOFF_MANIFEST,
                {"direct_attempt_file_count": len(manifest_names)},
            ),
            "direct_certificate": input_entry(
                DIRECT_ATTEMPT_CERTIFICATE,
                {
                    "recorded_certificate_sha256": certificate["certificate_sha256"],
                    "status": certificate["status"],
                },
            ),
            "direct_report": input_entry(DIRECT_ATTEMPT_REPORT),
            "w24_row_alphabetization": input_entry(
                W24_ROW_ALPHABETIZATION,
                {
                    "certificate_sha256": w24["certificate_sha256"],
                    "status": w24["status"],
                },
            ),
            "golay_hamming_probe": input_entry(
                GOLAY_HAMMING_PROBE,
                {
                    "certificate_sha256": golay_probe["certificate_sha256"],
                    "status": golay_probe["status"],
                },
            ),
            "mixed_duad_prune": input_entry(
                MIXED_DUAD_PRUNE,
                {
                    "certificate_sha256": mixed["certificate_sha256"],
                    "status": mixed["status"],
                },
            ),
        },
        "handoff_integrity": {
            "manifest_file_hashes": manifest_hashes,
            "recorded_certificate_sha256": claimed_cert_hash,
            "repo_canonical_certificate_hash_excluding_field": repo_canonical_cert_hash,
            "recorded_certificate_hash_matches_repo_canonical_hash": claimed_cert_hash
            == repo_canonical_cert_hash,
            "certificate_file_sha256": sha_file(DIRECT_ATTEMPT_CERTIFICATE),
        },
        "direct_attempt": {
            "status": certificate["status"],
            "timestamp_utc": certificate["timestamp_utc"],
            "weight_enumerator": cert_hist,
            "summary": certificate_summary,
            "csv_summaries": csv_summaries,
            "max_observed_F": observed_max_f,
        },
        "connection_to_current_problem": {
            "w24_endpoint": {
                "status": w24["status"],
                "rank": w24["witness"]["golay_code"]["rank"],
                "weight_histogram": w24_hist,
                "dodecad_count": w24["witness"]["golay_code"]["dodecad_count"],
            },
            "sector33_to_w24_map_status": golay_probe["candidate_morphism"]["morphism_status"],
            "mixed_local_duad_matching_status": mixed["status"],
            "interpretation": (
                "The entropy attempt attaches downstream to the certified W24 shell once a "
                "sector33-to-W24 map exists. It does not construct that map and does not close "
                "the entropy inequality."
            ),
        },
        "open_boundary": {
            "not_certified": [
                "D(q||u_B12) >= 6 D(p_q||u_24)",
                "D(q||u_B16) >= 8 D(p_q||u_24)",
                "a sandpile least-action proof of entropy monotonicity",
                "a Krawtchouk/SOS certificate",
                "an independent full replay from source-only inputs",
                "a sector33-to-W24 morphism",
            ],
            "certified_here": [
                "handoff artifact file integrity against its manifest",
                "no counterexample recorded in the supplied direct search traces",
                "the supplied W24 weight enumerator matches the certified repo W24/Golay endpoint",
                "the direct entropy attempt is downstream of, not a substitute for, the open sector33-to-W24 map",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_entropy_direct_attempt_import@1",
        "status": "D20_GOLAY_ENTROPY_DIRECT_ATTEMPT_IMPORT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The handoff Golay entropy direct attempt is imported as bounded computational evidence: "
            "its manifest hashes match, its supplied traces record no counterexample for the "
            "w=12 and w=16 shell objectives, and its weight enumerator matches the certified "
            "W24/Golay endpoint. It does not prove the entropy contraction inequalities and it "
            "does not construct the still-open sector33-to-W24 map."
        ),
        "definition": {
            "entropy_target": (
                "For w=12,16, prove Delta_w(q)=D(q||u_Bw)-(w/2)D(p_q||u_24) >= 0; "
                "the direct attempt numerically maximizes the equivalent log-shell objective F_w."
            ),
            "import_boundary": (
                "The handoff certificate is treated as an external computational artifact. The repo "
                "certificate verifies file integrity and trace summaries, but does not treat the "
                "handoff certificate_sha256 as a repo self hash."
            ),
        },
        "closure_boundary": {
            "certifies": artifact["open_boundary"]["certified_here"],
            "does_not_certify": artifact["open_boundary"]["not_certified"],
        },
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
            **artifact["source_reports"],
        },
        "witness": {
            "handoff_integrity": artifact["handoff_integrity"],
            "direct_attempt": artifact["direct_attempt"],
            "connection_to_current_problem": artifact["connection_to_current_problem"],
            "open_boundary": artifact["open_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Turn the no-counterexample data into a real finite certificate: either a "
            "Krawtchouk/SOS certificate for the w=12,16 shell objective, or a sandpile "
            "least-action monotonicity proof for Delta_w."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_entropy_direct_attempt_import_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify handoff manifest file hashes",
            "verify direct-attempt status and no-counterexample summary",
            "verify CSV traces record no exceeds_zero counterexample",
            "verify observed F maxima are within numerical roundoff of zero",
            "verify W24 endpoint weight enumerator matches the direct-attempt enumerator",
            "record that the entropy inequality and sector33-to-W24 map remain open",
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
                "max_observed_F": artifact["direct_attempt"]["max_observed_F"],
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
