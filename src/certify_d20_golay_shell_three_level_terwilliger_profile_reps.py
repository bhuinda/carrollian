from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_golay_shell_three_level_terwilliger_profile_reps import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        PROFILE_CSV,
        THEOREM_ID,
        build_manifest,
        build_report,
    )
    from .derive_d20_golay_shell_three_level_structured_probe import BOUND, TOL, optimize_profile
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_golay_shell_three_level_terwilliger_profile_reps import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        PROFILE_CSV,
        THEOREM_ID,
        build_manifest,
        build_report,
    )
    from derive_d20_golay_shell_three_level_structured_probe import (
        BOUND,
        TOL,
        optimize_profile,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()
PROFILE_CSV_REL = PROFILE_CSV.relative_to(ROOT).as_posix()
SOS_REPORT_PATH = OUT_DIR / "three_level_bivariate_sos_verification.json"
SOS_REPORT_REL = SOS_REPORT_PATH.relative_to(ROOT).as_posix()
SOS_CHECK_SCHEMA = "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps.profile_sos_check@1"

EXPECTED_CHECKS = {
    "w24_endpoint_certified",
    "exhaustive_two_level_input_certified",
    "generated_code_has_4096_words",
    "generated_code_weight_histogram_matches_w24",
    "two_level_representatives_recovered",
    "two_level_representative_counts_cover_all_subsets",
    "shell12_profiles_nonempty",
    "shell16_profiles_nonempty",
    "profile_csv_written",
    "m24_group_orbit_separation_not_claimed",
    "arbitrary_vector_theorem_not_certified",
}


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} file hash mismatch")


def _read_profile_csv() -> list[dict[str, str]]:
    with PROFILE_CSV.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _parse_profile(profile: str, shell: int) -> list[int]:
    values = [int(x) for x in profile.split(",") if x != ""]
    expected = (shell + 1) ** 2
    if len(values) != expected:
        raise AssertionError(f"Terwilliger profile length is not {(shell + 1)}x{(shell + 1)}")
    return values


def _write_json(path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def verify_bivariate_sos_over_profiles(
    *,
    max_profiles: int | None = None,
    include_top_failures: int = 25,
    verbose: bool = False,
) -> dict[str, Any]:
    rows = _read_profile_csv()
    if max_profiles is not None and max_profiles > 0:
        rows = rows[:max_profiles]
    if not rows:
        raise AssertionError("Terwilliger profile CSV is empty")
    if "profile" not in rows[0]:
        raise AssertionError("Terwilliger profile CSV is missing profile column")

    positive_profiles: list[dict[str, Any]] = []
    max_best_f = -10.0
    max_best_profile: dict[str, Any] | None = None
    max_grad_norm = 0.0
    max_grad_profile: dict[str, Any] | None = None

    for index, row in enumerate(rows):
        shell = int(row["shell"])
        if shell not in (12, 16):
            raise AssertionError(f"Terwilliger profile shell unexpected: {shell}")
        first_size = int(row["first_size"])
        second_size = int(row["second_size"])
        rest_size = int(row["rest_size"])
        if first_size + second_size + rest_size != 24:
            raise AssertionError(f"Terwilliger profile size bookkeeping mismatch at row {index}")

        profile = _parse_profile(row["profile"], shell)
        witness = optimize_profile(profile, shell, first_size, second_size)
        best_f = float(witness["best_F"])
        grad_norm = float(witness["best_gradient_norm"])
        max_best_f = max(max_best_f, best_f)
        if grad_norm > max_grad_norm:
            max_grad_norm = grad_norm
            max_grad_profile = {
                "row": index,
                "shell": shell,
                "first_size": first_size,
                "second_size": second_size,
                "best_F": best_f,
                "best_u": witness["best_u"],
                "best_v": witness["best_v"],
                "best_gradient_norm": grad_norm,
                "hessian_nonpositive": witness["local_hessian_nonpositive"],
            }
        if best_f > TOL or witness["local_hessian_nonpositive"] is not True:
            positive_profiles.append(
                {
                    "row": index,
                    "shell": shell,
                    "first_size": first_size,
                    "second_size": second_size,
                    "best_F": best_f,
                    "best_u": witness["best_u"],
                    "best_v": witness["best_v"],
                    "best_gradient_norm": grad_norm,
                    "hessian_min_eigenvalue_at_equality": witness[
                        "hessian_min_eigenvalue_at_equality"
                    ],
                    "hessian_max_eigenvalue_at_equality": witness[
                        "hessian_max_eigenvalue_at_equality"
                    ],
                }
            )
            if best_f > max_best_f:
                max_best_profile = positive_profiles[-1]
        if verbose and best_f > TOL:
            print(f"row {index}: shell={shell} best_F={best_f:.3e}")

    positive_profiles.sort(key=lambda row: row["best_F"], reverse=True)
    summary = {
        "schema": SOS_CHECK_SCHEMA,
        "name": THEOREM_ID,
        "schema_version": "1",
        "status": "PASS" if not positive_profiles else "FAIL",
        "profile_count": len(rows),
        "checked_profile_count": len(rows),
        "optimization_tolerance": float(TOL),
        "optimization_bound": float(BOUND),
        "positive_profile_count": len(positive_profiles),
        "max_best_F": max_best_f,
        "max_gradient_norm": max_grad_norm,
        "max_gradient_witness": max_grad_profile,
        "violations": positive_profiles[:include_top_failures],
    }
    _write_json(SOS_REPORT_PATH, summary)
    return summary


def _profile_support_sizes(profile: list[int], shell: int, shell_count: int) -> tuple[int, int]:
    first_num = 0
    second_num = 0
    for j in range(shell + 1):
        for k in range(shell + 1):
            count = profile[j * (shell + 1) + k]
            first_num += j * count
            second_num += k * count
    den = shell_count * shell
    if (24 * first_num) % den or (24 * second_num) % den:
        raise AssertionError("profile support moments are not integral")
    return (24 * first_num) // den, (24 * second_num) // den


def _wt(mask: int) -> int:
    return int(mask).bit_count()


def validate_d20_golay_shell_three_level_terwilliger_profile_reps() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps.artifact@1":
        raise AssertionError("Terwilliger profile artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_SHELL_THREE_LEVEL_TERWILLIGER_PROFILE_REPS_DERIVED":
        raise AssertionError("Terwilliger profile artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Terwilliger profile artifact self hash mismatch")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Terwilliger profile checks mismatch")

    selection = artifact.get("selection", {})
    first = selection.get("first_color_representatives", {})
    if first.get("representative_count") != 49:
        raise AssertionError("Terwilliger first-color representative count mismatch")
    if first.get("subset_count_total") != 1 << 24:
        raise AssertionError("Terwilliger first-color representatives do not cover all subsets")

    shell_summaries = selection.get("shell_summaries", {})
    if set(shell_summaries) != {"12", "16"}:
        raise AssertionError("Terwilliger shell summary keys mismatch")
    expected_shell_counts = {"12": 2576, "16": 759}
    for shell, shell_count in expected_shell_counts.items():
        summary = shell_summaries.get(shell, {})
        if summary.get("shell_word_count") != shell_count:
            raise AssertionError(f"Terwilliger shell {shell} word count mismatch")
        if summary.get("first_representative_rows_used") != 49:
            raise AssertionError(f"Terwilliger shell {shell} first representative coverage mismatch")
        if summary.get("compressed_second_subsets_scanned") != 34217663:
            raise AssertionError(f"Terwilliger shell {shell} second-subset scan count mismatch")
        if summary.get("unique_terwilliger_profile_count", 0) <= 0:
            raise AssertionError(f"Terwilliger shell {shell} profile count is empty")

    witness = artifact.get("witness", {})
    _check_input_file(witness.get("profile_csv", {}), PROFILE_CSV_REL, "profile CSV")
    csv_rows = _read_profile_csv()
    if len(csv_rows) != witness.get("profile_csv_row_count"):
        raise AssertionError("Terwilliger profile CSV row count mismatch")
    if len(csv_rows) != selection.get("total_profile_rows"):
        raise AssertionError("Terwilliger total profile row mismatch")

    seen: set[tuple[int, str]] = set()
    rows_by_shell = {"12": 0, "16": 0}
    for row in csv_rows:
        shell = int(row["shell"])
        shell_key = str(shell)
        if shell_key not in rows_by_shell:
            raise AssertionError("Terwilliger CSV unexpected shell")
        rows_by_shell[shell_key] += 1
        profile = [int(x) for x in row["profile"].split(",") if x != ""]
        if len(profile) != (shell + 1) * (shell + 1):
            raise AssertionError("Terwilliger CSV profile length mismatch")
        shell_count = expected_shell_counts[shell_key]
        if sum(profile) != shell_count:
            raise AssertionError("Terwilliger CSV profile shell-count mismatch")
        first_size, second_size = _profile_support_sizes(profile, shell, shell_count)
        if first_size != int(row["first_size"]):
            raise AssertionError("Terwilliger CSV first-size moment mismatch")
        if second_size != int(row["second_size"]):
            raise AssertionError("Terwilliger CSV second-size moment mismatch")
        if first_size + second_size + int(row["rest_size"]) != 24:
            raise AssertionError("Terwilliger CSV ordered size mismatch")
        first_mask = int(row["first_representative_mask"])
        second_mask = int(row["second_representative_mask"])
        if first_mask & second_mask:
            raise AssertionError("Terwilliger representative masks are not disjoint")
        if _wt(first_mask) != first_size or _wt(second_mask) != second_size:
            raise AssertionError("Terwilliger representative mask weights mismatch")
        key = (shell, row["profile"])
        if key in seen:
            raise AssertionError("Terwilliger duplicate shell profile row")
        seen.add(key)

    for shell, count in rows_by_shell.items():
        if count != shell_summaries[shell].get("unique_terwilliger_profile_count"):
            raise AssertionError(f"Terwilliger shell {shell} CSV count mismatch")

    if report.get("schema") != "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps@1":
        raise AssertionError("Terwilliger profile report schema mismatch")
    if report.get("status") != "D20_GOLAY_SHELL_THREE_LEVEL_TERWILLIGER_PROFILE_REPS_CERTIFIED_PROFILE_COVERAGE":
        raise AssertionError("Terwilliger profile report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Terwilliger profile report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("Terwilliger profile report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Terwilliger profile report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Terwilliger profile report is not reproducible from artifact")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_golay_shell_three_level_terwilliger_profile_reps.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_golay_shell_three_level_terwilliger_profile_reps.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps_manifest@1":
        raise AssertionError("Terwilliger profile manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Terwilliger profile manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Terwilliger profile manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Terwilliger profile manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Terwilliger profile manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Terwilliger profile registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Terwilliger profile registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Terwilliger profile registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-bivariate-sos",
        action="store_true",
        help="Verify a per-profile bivariate SOS-style ascent certificate over existing CSV rows.",
    )
    parser.add_argument(
        "--max-profiles",
        type=int,
        default=0,
        help="Limit bivariate SOS verification to the first N rows (for quick spot-checks).",
    )
    parser.add_argument(
        "--show-top-failures",
        type=int,
        default=25,
        help="Number of highest-Best-F violating rows to include in output.",
    )
    parser.add_argument("--quiet", action="store_true", help="Output machine-readable JSON only.")
    args = parser.parse_args()

    if args.verify_bivariate_sos:
        result = verify_bivariate_sos_over_profiles(
            max_profiles=args.max_profiles if args.max_profiles > 0 else None,
            include_top_failures=max(0, args.show_top_failures),
        )
        if not args.quiet:
            print(json.dumps(result, sort_keys=True, indent=2))
        if result["status"] != "PASS":
            raise SystemExit(1)
        raise SystemExit(0)

    validate_d20_golay_shell_three_level_terwilliger_profile_reps()
    if not args.quiet:
        print("D20 Golay shell three-level Terwilliger profile reps validated")
