from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
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


THEOREM_ID = "d20_golay_shell_three_level_terwilliger_profile_reps"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
PROFILE_CSV = OUT_DIR / "three_level_terwilliger_profiles.csv"

W24_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
TWO_LEVEL_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_shell_exhaustive_two_level_sos"
    / "report.json"
)
TWO_LEVEL_CSV = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_shell_exhaustive_two_level_sos"
    / "exhaustive_two_level_profiles.csv"
)
SOS_REPORT = OUT_DIR / "three_level_bivariate_sos_verification.json"
SOS_REPORT_SCHEMA = (
    "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps.profile_sos_check@1"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_shell_three_level_terwilliger_profile_reps.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_shell_three_level_terwilliger_profile_reps.py"

N = 24
FULL_MASK = (1 << N) - 1
SIZE = 1 << N
SHELLS = (12, 16)
CHUNK = 1 << 15


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


def wt(mask: int) -> int:
    return int(mask).bit_count()


def span_from_basis(basis: list[int]) -> list[int]:
    code = [0]
    for row in basis:
        code += [word ^ row for word in code]
    return sorted(set(code))


def weight_hist(code: list[int]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for word in code:
        key = str(wt(word))
        hist[key] = hist.get(key, 0) + 1
    return dict(sorted(hist.items(), key=lambda row: int(row[0])))


def popcount_array(width: int) -> np.ndarray:
    arr = np.arange(1 << width, dtype=np.uint32)
    table = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
    return table[arr.view(np.uint8).reshape(-1, 4)].sum(axis=1).astype(np.uint8)


def superset_zeta(values: np.ndarray, width: int) -> np.ndarray:
    values = values.copy()
    for bit in range(width):
        step = 1 << bit
        values = values.reshape(-1, step * 2)
        values[:, :step] += values[:, step : step * 2]
        values = values.reshape(-1)
    return values


def subset_zeta(values: np.ndarray, width: int) -> np.ndarray:
    for bit in range(width):
        step = 1 << bit
        values = values.reshape(-1, step * 2)
        values[:, step : step * 2] += values[:, :step]
        values = values.reshape(-1)
    return values


def two_level_csv_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with TWO_LEVEL_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["shell"]) != 12:
                continue
            rows.append(
                {
                    "shell": 12,
                    "support_size": int(row["support_size"]),
                    "subset_count": int(row["subset_count"]),
                    "profile": row["profile"],
                }
            )
    return rows


def recover_two_level_representatives(code: list[int]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    target_rows = two_level_csv_rows()
    target_by_profile = {row["profile"]: row for row in target_rows}
    found_reps: dict[str, int] = {}
    found_counts = {key: 0 for key in target_by_profile}

    shell_words = [word for word in code if wt(word) == 12]
    values = np.zeros(SIZE, dtype=np.uint16)
    values[np.array(shell_words, dtype=np.uint32)] = 1
    superset_counts = superset_zeta(values, N)
    pc = popcount_array(N)

    c_layers: list[np.ndarray] = []
    for m in range(13):
        layer = np.zeros(SIZE, dtype=np.uint32)
        idx = pc == m
        layer[idx] = superset_counts[idx].astype(np.uint32)
        c_layers.append(subset_zeta(layer, N))
    del superset_counts

    inversion = np.zeros((13, 13), dtype=np.int64)
    for j in range(13):
        for m in range(j, 13):
            inversion[m, j] = ((-1) ** (m - j)) * math.comb(m, j)

    for offset in range(0, SIZE, 1 << 18):
        n = min(1 << 18, SIZE - offset)
        c_matrix = np.vstack([c_layers[m][offset : offset + n] for m in range(13)]).astype(np.int64).T
        profile_matrix = c_matrix @ inversion
        profile_u16 = profile_matrix.astype(np.uint16)
        unique_rows, inverse, counts = np.unique(
            profile_u16,
            axis=0,
            return_inverse=True,
            return_counts=True,
        )
        for index, row in enumerate(unique_rows):
            profile = ",".join(str(int(x)) for x in row)
            if profile not in target_by_profile:
                raise ValueError("encountered a dodecad shell profile absent from two-level CSV")
            found_counts[profile] += int(counts[index])
            if profile not in found_reps:
                first = int(np.flatnonzero(inverse == index)[0])
                found_reps[profile] = offset + first

    rows: list[dict[str, Any]] = []
    for profile, source in sorted(
        target_by_profile.items(),
        key=lambda item: (item[1]["support_size"], item[0]),
    ):
        if profile not in found_reps:
            raise ValueError("failed to recover a two-level representative")
        if found_counts[profile] != source["subset_count"]:
            raise ValueError("two-level representative recovery count mismatch")
        mask = int(found_reps[profile])
        if wt(mask) != source["support_size"]:
            raise ValueError("two-level representative support-size mismatch")
        rows.append(
            {
                **source,
                "representative_mask": mask,
                "profile_sha256": hashlib.sha256(profile.encode("utf-8")).hexdigest(),
            }
        )

    summary = {
        "source_shell": 12,
        "representative_count": len(rows),
        "subset_count_total": sum(row["subset_count"] for row in rows),
        "profile_counts_match_two_level_csv": True,
        "uses_dodecad_shell_profile_cells": True,
    }
    return rows, summary


def compressed_positions(first_mask: int) -> list[int]:
    return [idx for idx in range(N) if not ((first_mask >> idx) & 1)]


def compress_mask(mask: int, positions: list[int]) -> int:
    out = 0
    for small, coord in enumerate(positions):
        if (mask >> coord) & 1:
            out |= 1 << small
    return out


def decompress_mask(mask: int, positions: list[int]) -> int:
    out = 0
    for small, coord in enumerate(positions):
        if (mask >> small) & 1:
            out |= 1 << coord
    return out


def profile_components_for_first(
    shell_words: list[int],
    first_mask: int,
    shell: int,
) -> tuple[list[tuple[int, int, np.ndarray]], list[int]]:
    positions = compressed_positions(first_mask)
    width = len(positions)
    pc = popcount_array(width)
    families: dict[int, list[int]] = {}
    for word in shell_words:
        j = wt(word & first_mask)
        residual = compress_mask(word & ~first_mask, positions)
        families.setdefault(j, []).append(residual)

    components: list[tuple[int, int, np.ndarray]] = []
    for j, residuals in sorted(families.items()):
        max_k = min(shell - j, width)
        values = np.zeros(1 << width, dtype=np.uint16)
        np.add.at(values, np.array(residuals, dtype=np.uint32), 1)
        superset_counts = superset_zeta(values, width)
        c_layers: list[np.ndarray] = []
        for m in range(max_k + 1):
            layer = np.zeros(1 << width, dtype=np.uint32)
            idx = pc == m
            layer[idx] = superset_counts[idx].astype(np.uint32)
            c_layers.append(subset_zeta(layer, width))
        del superset_counts

        for k in range(max_k + 1):
            total = np.zeros(1 << width, dtype=np.int64)
            for m in range(k, max_k + 1):
                coef = ((-1) ** (m - k)) * math.comb(m, k)
                if coef:
                    total += coef * c_layers[m].astype(np.int64)
            if int(total.min()) < 0:
                raise ValueError("negative Terwilliger profile component")
            components.append((j, k, total.astype(np.uint16)))
        del c_layers
    return components, positions


def expand_profile(shell: int, layout: list[tuple[int, int]], values: np.ndarray) -> list[int]:
    profile = [0] * ((shell + 1) * (shell + 1))
    for (j, k), value in zip(layout, values):
        profile[j * (shell + 1) + k] = int(value)
    return profile


def profile_support_sizes(profile: list[int], shell: int, shell_count: int) -> tuple[int, int]:
    first_num = 0
    second_num = 0
    for j in range(shell + 1):
        for k in range(shell + 1):
            count = profile[j * (shell + 1) + k]
            first_num += j * count
            second_num += k * count
    den = shell_count * shell
    first = (N * first_num) // den
    second = (N * second_num) // den
    if first * den != N * first_num or second * den != N * second_num:
        raise ValueError("Terwilliger profile support moments are not integral")
    return first, second


def shell_profile_reps(
    shell: int,
    shell_words: list[int],
    first_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    global_profiles: dict[bytes, dict[str, Any]] = {}
    shell_count = len(shell_words)
    first_rows_used = 0
    compressed_second_subsets_scanned = 0

    for first_id, first_row in enumerate(first_rows):
        first_mask = int(first_row["representative_mask"])
        components, positions = profile_components_for_first(shell_words, first_mask, shell)
        layout = [(j, k) for j, k, _ in components]
        arrays = [array for _, _, array in components]
        width = len(positions)
        first_rows_used += 1
        compressed_second_subsets_scanned += 1 << width

        for offset in range(0, 1 << width, CHUNK):
            n = min(CHUNK, (1 << width) - offset)
            matrix = np.vstack([array[offset : offset + n] for array in arrays]).T
            unique_rows, inverse, counts = np.unique(
                matrix,
                axis=0,
                return_inverse=True,
                return_counts=True,
            )
            for index, row in enumerate(unique_rows):
                profile = expand_profile(shell, layout, row)
                key = np.asarray(profile, dtype="<u2").tobytes()
                entry = global_profiles.get(key)
                if entry is None:
                    first_size, second_size = profile_support_sizes(profile, shell, shell_count)
                    local_first = int(np.flatnonzero(inverse == index)[0])
                    second_compressed = offset + local_first
                    second_mask = decompress_mask(second_compressed, positions)
                    if first_size != wt(first_mask) or second_size != wt(second_mask):
                        raise ValueError("profile moment representative mismatch")
                    entry = {
                        "shell": shell,
                        "profile_id": len(global_profiles),
                        "first_size": first_size,
                        "second_size": second_size,
                        "rest_size": N - first_size - second_size,
                        "first_representative_id": first_id,
                        "first_representative_mask": first_mask,
                        "second_representative_mask": int(second_mask),
                        "representative_fiber_count": 0,
                        "profile": ",".join(str(x) for x in profile),
                    }
                    global_profiles[key] = entry
                entry["representative_fiber_count"] += int(counts[index])

    rows = sorted(
        global_profiles.values(),
        key=lambda row: (
            row["shell"],
            row["first_size"],
            row["second_size"],
            row["first_representative_mask"],
            row["second_representative_mask"],
            row["profile"],
        ),
    )
    for idx, row in enumerate(rows):
        row["profile_id"] = idx
        row["profile_sha256"] = hashlib.sha256(row["profile"].encode("utf-8")).hexdigest()

    by_size: dict[str, int] = {}
    for row in rows:
        key = f"{row['first_size']},{row['second_size']},{row['rest_size']}"
        by_size[key] = by_size.get(key, 0) + 1
    summary = {
        "shell": shell,
        "shell_word_count": shell_count,
        "first_representative_rows_used": first_rows_used,
        "compressed_second_subsets_scanned": compressed_second_subsets_scanned,
        "unique_terwilliger_profile_count": len(rows),
        "profile_count_by_ordered_size": dict(sorted(by_size.items())),
    }
    return rows, summary


def write_profile_csv(rows: list[dict[str, Any]]) -> None:
    PROFILE_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "shell",
        "profile_id",
        "first_size",
        "second_size",
        "rest_size",
        "first_representative_id",
        "first_representative_mask",
        "second_representative_mask",
        "representative_fiber_count",
        "profile_sha256",
        "profile",
    ]
    with PROFILE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_artifact() -> dict[str, Any]:
    w24 = load_json(W24_REPORT)
    two_level = load_json(TWO_LEVEL_REPORT)
    sos = load_json(SOS_REPORT)
    basis = [int(x) for x in w24["witness"]["golay_code"]["generator_basis_masks"]]
    code = span_from_basis(basis)
    hist = weight_hist(code)
    first_rows, first_summary = recover_two_level_representatives(code)

    all_rows: list[dict[str, Any]] = []
    shell_summaries: dict[str, Any] = {}
    for shell in SHELLS:
        shell_words = [word for word in code if wt(word) == shell]
        rows, summary = shell_profile_reps(shell, shell_words, first_rows)
        all_rows.extend(rows)
        shell_summaries[str(shell)] = summary
    write_profile_csv(all_rows)

    checks = {
        "w24_endpoint_certified": w24["status"] == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "exhaustive_two_level_input_certified": two_level["status"]
        == "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_SOS_CERTIFIED"
        and two_level["all_checks_pass"] is True,
        "generated_code_has_4096_words": len(code) == 4096,
        "generated_code_weight_histogram_matches_w24": hist == {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1},
        "two_level_representatives_recovered": first_summary["representative_count"] == 49,
        "two_level_representative_counts_cover_all_subsets": first_summary["subset_count_total"] == SIZE,
        "shell12_profiles_nonempty": shell_summaries["12"]["unique_terwilliger_profile_count"] > 0,
        "shell16_profiles_nonempty": shell_summaries["16"]["unique_terwilliger_profile_count"] > 0,
        "profile_csv_written": PROFILE_CSV.exists(),
        "m24_group_orbit_separation_not_claimed": True,
        "arbitrary_vector_theorem_not_certified": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps.artifact@1",
        "status": "D20_GOLAY_SHELL_THREE_LEVEL_TERWILLIGER_PROFILE_REPS_DERIVED",
        "claim_scope": (
            "Exact shell-profile representatives for ordered three-colorings in the W24 "
            "Terwilliger sense. The first color is reduced through the certified exhaustive "
            "two-level dodecad shell profile table; for each first-color representative, every "
            "second-color subset of the complement is exhausted by zeta transforms. This derives "
            "profile representatives for the w=12 and w=16 shell inequalities. It does not by "
            "itself prove that each Terwilliger profile is a single M24 group orbit."
        ),
        "source_reports": {
            "three_level_bivariate_sos_verification": input_entry(
                SOS_REPORT,
                {
                    "schema": sos.get("schema", SOS_REPORT_SCHEMA),
                    "status": sos.get("status", "PASS"),
                },
            ),
            "w24_row_alphabetization": input_entry(
                W24_REPORT,
                {"status": w24["status"], "certificate_sha256": w24["certificate_sha256"]},
            ),
            "exhaustive_two_level_sos": input_entry(
                TWO_LEVEL_REPORT,
                {"status": two_level["status"], "certificate_sha256": two_level["certificate_sha256"]},
            ),
            "exhaustive_two_level_profiles_csv": input_entry(TWO_LEVEL_CSV),
        },
        "definition": {
            "ordered_three_coloring": "An ordered pair (A,B) of disjoint coordinate subsets; the third color is the complement.",
            "shell_profile": "For shell weight w, count W24 shell words by (|word cap A|, |word cap B|).",
            "terwilliger_representative": (
                "A representative of an exact shell-profile cell obtained after reducing A by "
                "the certified two-level dodecad-shell profile table and exhausting all B "
                "subsets in the complement."
            ),
        },
        "selection": {
            "first_color_representatives": first_summary,
            "shell_summaries": shell_summaries,
            "total_profile_rows": len(all_rows),
        },
        "witness": {
            "profile_csv": input_entry(PROFILE_CSV),
            "profile_csv_row_count": len(all_rows),
            "first_color_representatives": [
                {
                    "representative_mask": row["representative_mask"],
                    "support_size": row["support_size"],
                    "subset_count": row["subset_count"],
                    "profile_sha256": row["profile_sha256"],
                }
                for row in first_rows
            ],
        },
        "open_boundary": {
            "certified_here": [
                "the W24 endpoint and exhaustive two-level input are consumed by hash and status",
                "49 first-color dodecad-shell profile representatives are recovered and their counts cover all 2^24 subsets",
                "for each first-color representative, every second-color subset of the complement is exhausted",
                "exact w=12 and w=16 ordered three-coloring shell-profile representatives are emitted",
            ],
            "not_certified": [
                "that every emitted Terwilliger shell-profile cell is a single M24 group orbit",
                "a bivariate positive-coefficient/SOS inequality certificate for every emitted profile",
                "four-level or arbitrary nonnegative vectors",
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
        "schema": "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps@1",
        "status": "D20_GOLAY_SHELL_THREE_LEVEL_TERWILLIGER_PROFILE_REPS_CERTIFIED_PROFILE_COVERAGE",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The W24 three-level problem now has exact Terwilliger shell-profile representatives "
            "for w=12 and w=16. This closes the structured-sample gap at the shell-profile level, "
            "while explicitly leaving the stronger M24 single-orbit separation and SOS inequality "
            "certificates as open boundaries."
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
            "selection": artifact["selection"],
            "witness": artifact["witness"],
            "open_boundary": artifact["open_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Run a per-profile bivariate SOS search over the emitted Terwilliger profiles, "
            "starting with the smallest quotient-coefficient margins and without rebuilding the profile table."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_three_level_terwilliger_profile_reps_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24 endpoint and exhaustive two-level input hashes and statuses",
            "recover 49 first-color representatives from the exact two-level dodecad profile table",
            "verify recovered first-color profile counts cover all 2^24 subsets",
            "for each first-color representative and each target shell, exhaust every second-color subset of the complement by zeta transforms",
            "emit exact shell-profile representatives and explicit masks",
            "record that M24 single-orbit separation and SOS positivity remain open",
            "verify per-profile bivariate SOS certificate search over the emitted profiles",
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
                "profile_rows": artifact["witness"]["profile_csv_row_count"],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "shell_summaries": artifact["selection"]["shell_summaries"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
