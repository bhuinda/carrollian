from __future__ import annotations

import csv
import gc
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_golay_shell_exhaustive_two_level_sos"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
PROFILE_CSV = OUT_DIR / "exhaustive_two_level_profiles.csv"

W24_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
ARCHIVE_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_hamming_gaussian_python_work_archive_import"
    / "report.json"
)
SELECTED_TWO_LEVEL_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_shell_two_level_lift_probe"
    / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_shell_exhaustive_two_level_sos.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_shell_exhaustive_two_level_sos.py"

N = 24
SIZE = 1 << N
SHELLS = (12, 16)
CHUNK = 1 << 18


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


def span_from_basis(basis: list[int]) -> list[int]:
    code = [0]
    for row in basis:
        code += [word ^ row for word in code]
    return sorted(set(code))


def wt(mask: int) -> int:
    return int(mask).bit_count()


def weight_hist(code: list[int]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for word in code:
        key = str(wt(word))
        hist[key] = hist.get(key, 0) + 1
    return dict(sorted(hist.items(), key=lambda row: int(row[0])))


def popcount_array() -> np.ndarray:
    arr = np.arange(SIZE, dtype=np.uint32)
    table = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
    return table[arr.view(np.uint8).reshape(-1, 4)].sum(axis=1).astype(np.uint8)


def superset_zeta_shell(shell_words: list[int]) -> np.ndarray:
    values = np.zeros(SIZE, dtype=np.uint16)
    values[np.array(shell_words, dtype=np.uint32)] = 1
    for bit in range(N):
        step = 1 << bit
        values = values.reshape(-1, step * 2)
        values[:, :step] += values[:, step : step * 2]
        values = values.reshape(-1)
    return values


def subset_zeta(values: np.ndarray) -> np.ndarray:
    for bit in range(N):
        step = 1 << bit
        values = values.reshape(-1, step * 2)
        values[:, step : step * 2] += values[:, :step]
        values = values.reshape(-1)
    return values


def quotient_by_x_minus_one(poly: list[int]) -> tuple[list[int], int]:
    if len(poly) <= 1:
        return [], poly[0] if poly else 0
    quotient = [0] * (len(poly) - 1)
    quotient[-1] = poly[-1]
    for i in range(len(quotient) - 2, -1, -1):
        quotient[i] = poly[i + 1] + quotient[i + 1]
    remainder = poly[0] + quotient[0]
    return quotient, remainder


def gap_polynomial_coeffs(profile: list[int], support_size: int, shell: int, shell_count: int) -> list[int]:
    half = shell // 2
    coeffs = [0] * (shell + 1)
    for a in range(half + 1):
        degree = 2 * a
        coeffs[degree] += (
            shell_count
            * math.comb(half, a)
            * (support_size**a)
            * ((N - support_size) ** (half - a))
        )
    scale = N**half
    for j, count in enumerate(profile):
        coeffs[j] -= scale * int(count)
    return coeffs


def support_size_from_profile(profile: list[int], shell: int, shell_count: int) -> int:
    numerator = N * sum(j * int(count) for j, count in enumerate(profile))
    denominator = shell_count * shell
    if numerator % denominator != 0:
        raise ValueError("profile does not determine an integral support size")
    return numerator // denominator


def certify_profile(profile: list[int], shell: int, shell_count: int) -> dict[str, Any]:
    support_size = support_size_from_profile(profile, shell, shell_count)
    gap = gap_polynomial_coeffs(profile, support_size, shell, shell_count)
    q1, rem1 = quotient_by_x_minus_one(gap)
    quotient, rem2 = quotient_by_x_minus_one(q1)
    if rem1 != 0 or rem2 != 0:
        raise ValueError("gap polynomial is not divisible by (r-1)^2")
    return {
        "support_size": support_size,
        "gap_coefficients": gap,
        "positive_quotient_coefficients": quotient,
        "first_division_remainder": rem1,
        "second_division_remainder": rem2,
        "min_positive_quotient_coefficient": min(quotient) if quotient else 0,
        "positive_quotient_nonnegative": all(coef >= 0 for coef in quotient),
        "quotient_zero_coefficient_count": sum(1 for coef in quotient if coef == 0),
    }


def exact_profiles_for_shell(
    shell: int,
    code: list[int],
    pc: np.ndarray,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    shell_words = [word for word in code if wt(word) == shell]
    shell_count = len(shell_words)
    superset_counts = superset_zeta_shell(shell_words)
    c_layers: list[np.ndarray] = []
    transform_maxima: list[int] = []
    for m in range(shell + 1):
        values = np.zeros(SIZE, dtype=np.uint32)
        idx = pc == m
        values[idx] = superset_counts[idx].astype(np.uint32)
        values = subset_zeta(values)
        transform_maxima.append(int(values.max()))
        c_layers.append(values)

    binomial_inversion = np.zeros((shell + 1, shell + 1), dtype=np.int64)
    for j in range(shell + 1):
        for m in range(j, shell + 1):
            binomial_inversion[m, j] = ((-1) ** (m - j)) * math.comb(m, j)

    profiles: dict[bytes, dict[str, Any]] = {}
    malformed_chunks = 0
    min_profile_entry = 0
    max_profile_sum = 0
    for offset in range(0, SIZE, CHUNK):
        n = min(CHUNK, SIZE - offset)
        c_matrix = np.vstack(
            [c_layers[m][offset : offset + n] for m in range(shell + 1)]
        ).astype(np.int64).T
        profile_matrix = c_matrix @ binomial_inversion
        if int(profile_matrix.min()) < 0:
            malformed_chunks += 1
            min_profile_entry = min(min_profile_entry, int(profile_matrix.min()))
        sums = profile_matrix.sum(axis=1)
        max_profile_sum = max(max_profile_sum, int(sums.max()))
        profile_u16 = profile_matrix.astype(np.uint16)
        unique_rows, inverse, counts = np.unique(
            profile_u16,
            axis=0,
            return_inverse=True,
            return_counts=True,
        )
        support_sizes = pc[offset : offset + n]
        for index, row in enumerate(unique_rows):
            key = row.tobytes()
            if key not in profiles:
                profiles[key] = {
                    "profile": row.astype(int).tolist(),
                    "subset_count": 0,
                    "support_sizes": set(),
                }
            profiles[key]["subset_count"] += int(counts[index])
            profiles[key]["support_sizes"].update(
                int(k) for k in np.unique(support_sizes[inverse == index])
            )
    del c_layers
    gc.collect()

    rows: list[dict[str, Any]] = []
    min_quotient_coefficient = None
    for profile_payload in profiles.values():
        profile = profile_payload["profile"]
        cert = certify_profile(profile, shell, shell_count)
        support_size = cert["support_size"]
        support_sizes_seen = sorted(profile_payload["support_sizes"])
        if support_sizes_seen != [support_size]:
            raise ValueError("profile support-size witness mismatch")
        min_quotient_coefficient = (
            cert["min_positive_quotient_coefficient"]
            if min_quotient_coefficient is None
            else min(min_quotient_coefficient, cert["min_positive_quotient_coefficient"])
        )
        rows.append(
            {
                "shell": shell,
                "support_size": support_size,
                "subset_count": profile_payload["subset_count"],
                "profile": ",".join(str(x) for x in profile),
                "gap_coefficients": ",".join(str(x) for x in cert["gap_coefficients"]),
                "positive_quotient_coefficients": ",".join(
                    str(x) for x in cert["positive_quotient_coefficients"]
                ),
                "min_positive_quotient_coefficient": cert[
                    "min_positive_quotient_coefficient"
                ],
                "quotient_zero_coefficient_count": cert["quotient_zero_coefficient_count"],
                "positive_quotient_nonnegative": cert["positive_quotient_nonnegative"],
                "first_division_remainder": cert["first_division_remainder"],
                "second_division_remainder": cert["second_division_remainder"],
            }
        )
    rows.sort(key=lambda row: (row["shell"], row["support_size"], row["profile"]))
    summary = {
        "shell": shell,
        "shell_count": shell_count,
        "unique_profile_count": len(rows),
        "subset_count_total": sum(int(row["subset_count"]) for row in rows),
        "all_subsets_covered": sum(int(row["subset_count"]) for row in rows) == SIZE,
        "malformed_chunks": malformed_chunks,
        "min_profile_entry": min_profile_entry,
        "max_profile_sum": max_profile_sum,
        "min_positive_quotient_coefficient": min_quotient_coefficient,
        "all_positive_quotients_nonnegative": all(
            row["positive_quotient_nonnegative"] is True for row in rows
        ),
        "all_gap_polynomials_have_double_root_at_one": all(
            row["first_division_remainder"] == 0 and row["second_division_remainder"] == 0
            for row in rows
        ),
        "transform_maxima": transform_maxima,
    }
    return rows, summary


def write_profile_csv(rows: list[dict[str, Any]]) -> None:
    PROFILE_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "shell",
        "support_size",
        "subset_count",
        "profile",
        "gap_coefficients",
        "positive_quotient_coefficients",
        "min_positive_quotient_coefficient",
        "quotient_zero_coefficient_count",
        "positive_quotient_nonnegative",
        "first_division_remainder",
        "second_division_remainder",
    ]
    with PROFILE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_artifact() -> dict[str, Any]:
    w24 = load_json(W24_REPORT)
    archive = load_json(ARCHIVE_REPORT)
    selected = load_json(SELECTED_TWO_LEVEL_REPORT)
    basis = [int(x) for x in w24["witness"]["golay_code"]["generator_basis_masks"]]
    code = span_from_basis(basis)
    hist = weight_hist(code)
    pc = popcount_array()

    all_rows: list[dict[str, Any]] = []
    shell_summaries: dict[str, Any] = {}
    for shell in SHELLS:
        rows, summary = exact_profiles_for_shell(shell, code, pc)
        all_rows.extend(rows)
        shell_summaries[str(shell)] = summary
    write_profile_csv(all_rows)

    checks = {
        "w24_endpoint_certified": w24["status"] == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "archive_two_level_precursor_certified": archive["status"]
        == "D20_HAMMING_GAUSSIAN_PYTHON_WORK_ARCHIVE_IMPORT_CERTIFIED_PARTIAL_REPLAY",
        "selected_two_level_precursor_certified": selected["status"]
        == "D20_GOLAY_SHELL_TWO_LEVEL_LIFT_PROBE_CERTIFIED_NO_COUNTEREXAMPLE"
        and selected["all_checks_pass"] is True,
        "generated_code_has_4096_words": len(code) == 4096,
        "generated_code_weight_histogram_matches_w24": hist == {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1},
        "both_shells_have_49_profiles": all(
            shell_summaries[str(shell)]["unique_profile_count"] == 49 for shell in SHELLS
        ),
        "both_shells_cover_all_subsets": all(
            shell_summaries[str(shell)]["all_subsets_covered"] is True for shell in SHELLS
        ),
        "all_profile_entries_well_formed": all(
            shell_summaries[str(shell)]["malformed_chunks"] == 0
            and shell_summaries[str(shell)]["min_profile_entry"] == 0
            for shell in SHELLS
        ),
        "all_profile_sums_match_shell_sizes": shell_summaries["12"]["max_profile_sum"] == 2576
        and shell_summaries["16"]["max_profile_sum"] == 759,
        "all_gap_polynomials_have_positive_coefficient_quotients": all(
            shell_summaries[str(shell)]["all_positive_quotients_nonnegative"] is True
            for shell in SHELLS
        ),
        "all_gap_polynomials_have_double_equality_root": all(
            shell_summaries[str(shell)]["all_gap_polynomials_have_double_root_at_one"] is True
            for shell in SHELLS
        ),
        "profile_csv_written": PROFILE_CSV.exists(),
        "full_arbitrary_vector_theorem_not_certified": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_exhaustive_two_level_sos.artifact@1",
        "status": "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_POSITIVE_QUOTIENT_CERTIFIED",
        "claim_scope": (
            "Exact exhaustive certificate for all two-level nonnegative shell vectors over "
            "all 2^24 coordinate subsets, for the w=12 and w=16 Golay shells. This proves "
            "the two-level case of the shell domination inequality, but not the full "
            "arbitrary-vector case."
        ),
        "source_reports": {
            "w24_row_alphabetization": input_entry(
                W24_REPORT,
                {"status": w24["status"], "certificate_sha256": w24["certificate_sha256"]},
            ),
            "python_work_archive": input_entry(
                ARCHIVE_REPORT,
                {"status": archive["status"], "certificate_sha256": archive["certificate_sha256"]},
            ),
            "selected_two_level_probe": input_entry(
                SELECTED_TWO_LEVEL_REPORT,
                {"status": selected["status"], "certificate_sha256": selected["certificate_sha256"]},
            ),
        },
        "definition": {
            "two_level_vector": "x_i=r on S and x_i=1 off S, with r>=0.",
            "integer_gap_polynomial": (
                "Q_{w,S}(r)=A_w(1)(|S|r^2+24-|S|)^(w/2)"
                "-24^(w/2) sum_j n_j(S) r^j"
            ),
            "profile": "n_j(S)=#{B in G24_w : |B cap S|=j}",
            "certificate_rule": (
                "For every exact profile, Q_{w,S}(r)=(r-1)^2 R_{w,S}(r), and all "
                "coefficients of R_{w,S} are nonnegative integers. Thus Q_{w,S}(r)>=0 "
                "for every r>=0."
            ),
            "transform_method": (
                "Superset zeta gives A(T)=#{B in G24_w:T subset B}; subset zeta on "
                "fixed |T| layers gives binomial moments c_m(S)=sum_{T subset S,|T|=m}A(T); "
                "binomial inversion recovers every n_j(S)."
            ),
        },
        "witness": {
            "length": N,
            "subset_count_per_shell": SIZE,
            "shells": shell_summaries,
            "profile_csv": input_entry(PROFILE_CSV),
            "profile_csv_row_count": len(all_rows),
            "sample_profiles": all_rows[:10],
        },
        "open_boundary": {
            "certified_here": [
                "all two-level vectors x_i=r on S and x_i=1 off S for every S subset {1,...,24}",
                "w=12 shell domination in the two-level case",
                "w=16 shell domination in the two-level case",
                "exact positive-coefficient quotient certificates for all 98 shell/profile cases",
            ],
            "not_certified": [
                "three-level or higher nonnegative vectors",
                "arbitrary nonnegative vectors in R^24",
                "the full w=12 entropy contraction theorem",
                "the full w=16 entropy contraction theorem",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_exhaustive_two_level_sos@1",
        "status": "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_SOS_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The two-level case of the Golay shell domination inequality is certified "
            "exhaustively for w=12 and w=16. For every subset S of the 24 coordinates, the "
            "exact intersection profile is reduced to one of 49 profiles per shell, and the "
            "integer gap polynomial factors as (r-1)^2 times a polynomial with nonnegative "
            "integer coefficients. This proves the two-level lift case; the arbitrary-vector "
            "entropy contraction remains open."
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
            **artifact["source_reports"],
        },
        "witness": {
            "definition": artifact["definition"],
            "witness": artifact["witness"],
            "open_boundary": artifact["open_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Attempt the three-level analogue. If the same positive-quotient pattern survives "
            "for all three-block MOG/Terwilliger profiles, promote it toward a full "
            "Krawtchouk/SOS certificate for arbitrary nonnegative vectors."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_exhaustive_two_level_sos_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "rebuild W24 from the certified generator basis",
            "recover exact shell/subset intersection profiles for all 2^24 subsets by zeta transforms",
            "verify each shell has 49 exact profiles covering all subsets",
            "build exact integer gap polynomials for w=12 and w=16",
            "divide every gap polynomial by (r-1)^2",
            "verify every quotient has nonnegative integer coefficients",
            "record that arbitrary vectors with three or more levels remain open",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "profile_csv": relpath(PROFILE_CSV),
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
                "profiles": artifact["witness"]["profile_csv_row_count"],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "unique_profiles_by_shell": {
                    shell: artifact["witness"]["shells"][shell]["unique_profile_count"]
                    for shell in artifact["witness"]["shells"]
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
