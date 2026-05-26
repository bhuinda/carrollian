from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_golay_shell_two_level_lift_probe"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

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
DIRECT_ATTEMPT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_entropy_direct_attempt_import"
    / "report.json"
)
INDICATOR_CSV = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "hamming_gaussian_indicator_shell_domination"
    / "indicator_shell_domination_by_support_size.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_shell_two_level_lift_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_shell_two_level_lift_probe.py"

N = 24
FULL_MASK = (1 << N) - 1
SHELLS = (12, 16)
GRID_STEPS = 1600
T_BOUND = 40.0
TOL = 1e-10


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


def read_indicator_masks() -> dict[int, set[int]]:
    masks: dict[int, set[int]] = {12: set(), 16: set()}
    if not INDICATOR_CSV.exists():
        return masks
    with INDICATOR_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            shell = int(row["shell_weight"])
            if shell in masks:
                masks[shell].add(int(row["example_support_mask"]))
    return masks


def deterministic_random_masks(count_per_size: int = 12) -> set[int]:
    rng = random.Random(20260526)
    masks: set[int] = set()
    for k in range(N + 1):
        for _ in range(count_per_size):
            coords = rng.sample(range(N), k)
            mask = 0
            for i in coords:
                mask |= 1 << i
            masks.add(mask)
    return masks


def selected_split_masks(w24: dict[str, Any], code: list[int]) -> dict[int, dict[int, set[str]]]:
    witness = w24["witness"]
    containment = witness["containment_witnesses"]
    row_alphabet = witness["row_alphabetization"]["grid_row_major"]
    by_mask: dict[int, set[str]] = {}

    def add(mask: int, label: str) -> None:
        mask &= FULL_MASK
        by_mask.setdefault(mask, set()).add(label)
        by_mask.setdefault(FULL_MASK ^ mask, set()).add(f"complement:{label}")

    add(0, "empty")
    add(FULL_MASK, "full")
    for k in range(N + 1):
        add((1 << k) - 1 if k else 0, f"prefix_k{k}")
    for i in range(N):
        add(1 << i, f"singleton_{i}")
    for row_i, row in enumerate(row_alphabet):
        mask = sum(1 << i for i in row)
        add(mask, f"mog_row_{row_i}")
    for col in range(6):
        mask = sum(1 << row[col] for row in row_alphabet)
        add(mask, f"mog_column_{col}")
    for mask in containment["row_masks"]:
        add(int(mask), "w24_row_mask")
    for mask in containment["row_pair_masks"]:
        add(int(mask), "w24_row_pair_mask")
    for mask in containment["column_pair_generator_masks"]:
        add(int(mask), "w24_column_pair_codeword")

    for word in code:
        weight = wt(word)
        if weight in (8, 12, 16, 24):
            add(word, f"w24_shell_support_w{weight}")

    for shell, masks in read_indicator_masks().items():
        for mask in masks:
            add(mask, f"indicator_worst_shell_{shell}")

    for mask in deterministic_random_masks():
        add(mask, "deterministic_random")

    return {mask: {0: labels} for mask, labels in by_mask.items()}


def shell_profile(shell_words: list[int], mask: int, shell_weight: int) -> list[int]:
    counts = [0] * (shell_weight + 1)
    for word in shell_words:
        counts[wt(word & mask)] += 1
    return counts


def log_sum_exp_terms(counts: list[int], t: float) -> float:
    terms = [(j * t, count) for j, count in enumerate(counts) if count]
    m = max(value for value, _ in terms)
    return m + math.log(sum(count * math.exp(value - m) for value, count in terms))


def two_level_f(counts: list[int], k: int, shell_weight: int, t: float) -> float:
    total = sum(counts)
    if total == 0:
        return float("-inf")
    if k == 0 or k == N:
        return 0.0
    denom = k * math.exp(2.0 * t) + (N - k)
    return (
        log_sum_exp_terms(counts, t)
        - math.log(total)
        - (shell_weight / 2.0) * (math.log(denom) - math.log(N))
    )


def two_level_derivative(counts: list[int], k: int, shell_weight: int, t: float) -> float:
    if k == 0 or k == N:
        return 0.0
    terms = [(j * t, j, count) for j, count in enumerate(counts) if count]
    m = max(value for value, _, _ in terms)
    weights = [count * math.exp(value - m) for value, _, count in terms]
    z = sum(weights)
    expected_j = sum(j * weight for weight, (_, j, _) in zip(weights, terms)) / z
    e2 = math.exp(2.0 * t)
    expected_under_l2 = shell_weight * k * e2 / (k * e2 + (N - k))
    return expected_j - expected_under_l2


def bisection_root(counts: list[int], k: int, shell_weight: int, lo: float, hi: float) -> float:
    flo = two_level_derivative(counts, k, shell_weight, lo)
    for _ in range(80):
        mid = (lo + hi) / 2.0
        fmid = two_level_derivative(counts, k, shell_weight, mid)
        if abs(fmid) < 1e-14:
            return mid
        if flo * fmid <= 0:
            hi = mid
        else:
            lo = mid
            flo = fmid
    return (lo + hi) / 2.0


def optimize_two_level(counts: list[int], k: int, shell_weight: int) -> dict[str, Any]:
    if k == 0 or k == N:
        return {
            "max_F": 0.0,
            "arg_t": 0.0,
            "root_count": 1,
            "endpoint_left_F": 0.0,
            "endpoint_right_F": 0.0,
        }
    grid = [-T_BOUND + (2 * T_BOUND) * i / GRID_STEPS for i in range(GRID_STEPS + 1)]
    roots = [-T_BOUND, 0.0, T_BOUND]
    prev_t = grid[0]
    prev_d = two_level_derivative(counts, k, shell_weight, prev_t)
    for t in grid[1:]:
        deriv = two_level_derivative(counts, k, shell_weight, t)
        if deriv == 0.0:
            roots.append(t)
        elif prev_d * deriv < 0:
            roots.append(bisection_root(counts, k, shell_weight, prev_t, t))
        prev_t = t
        prev_d = deriv
    roots = sorted(set(round(root, 13) for root in roots))
    values = [(two_level_f(counts, k, shell_weight, root), root) for root in roots]
    max_f, arg_t = max(values, key=lambda row: row[0])
    return {
        "max_F": max_f,
        "arg_t": arg_t,
        "root_count": len(roots),
        "endpoint_left_F": two_level_f(counts, k, shell_weight, -T_BOUND),
        "endpoint_right_F": two_level_f(counts, k, shell_weight, T_BOUND),
    }


def profile_key(counts: list[int]) -> str:
    return ",".join(str(x) for x in counts)


def build_rows(w24: dict[str, Any], code: list[int]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    split_labels = selected_split_masks(w24, code)
    shell_words = {shell: [word for word in code if wt(word) == shell] for shell in SHELLS}
    rows: list[dict[str, Any]] = []
    unique_profiles: dict[str, dict[str, Any]] = {}
    for mask, label_payload in sorted(split_labels.items()):
        labels = sorted(label_payload[0])
        k = wt(mask)
        for shell in SHELLS:
            counts = shell_profile(shell_words[shell], mask, shell)
            opt = optimize_two_level(counts, k, shell)
            key = f"w{shell}:k{k}:{profile_key(counts)}"
            unique_profiles.setdefault(
                key,
                {
                    "shell": shell,
                    "support_size": k,
                    "counts": counts,
                    "seen_count": 0,
                    "max_F": opt["max_F"],
                    "arg_t": opt["arg_t"],
                },
            )
            unique_profiles[key]["seen_count"] += 1
            rows.append(
                {
                    "shell": shell,
                    "support_mask": mask,
                    "support_size": k,
                    "labels": ";".join(labels[:8]),
                    "label_count": len(labels),
                    "profile": profile_key(counts),
                    "max_F": opt["max_F"],
                    "arg_t": opt["arg_t"],
                    "root_count": opt["root_count"],
                    "endpoint_left_F": opt["endpoint_left_F"],
                    "endpoint_right_F": opt["endpoint_right_F"],
                    "exceeds_tolerance": opt["max_F"] > TOL,
                }
            )
    profile_summary = {
        "unique_profile_count": len(unique_profiles),
        "by_shell": {
            str(shell): sum(1 for profile in unique_profiles.values() if profile["shell"] == shell)
            for shell in SHELLS
        },
    }
    return rows, profile_summary


def write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_artifact() -> dict[str, Any]:
    w24 = load_json(W24_REPORT)
    archive = load_json(ARCHIVE_REPORT)
    direct = load_json(DIRECT_ATTEMPT_REPORT)
    basis = [int(x) for x in w24["witness"]["golay_code"]["generator_basis_masks"]]
    code = span_from_basis(basis)
    hist = weight_hist(code)
    rows, profile_summary = build_rows(w24, code)
    rows_sorted = sorted(rows, key=lambda row: row["max_F"], reverse=True)
    top_rows = rows_sorted[:20]
    max_f = float(rows_sorted[0]["max_F"])
    max_excess = max_f - TOL
    csv_path = OUT_DIR / "two_level_lift_profiles.csv"
    write_csv_rows(csv_path, rows_sorted)

    checks = {
        "w24_endpoint_certified": w24["status"] == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "archive_indicator_shell_input_certified": archive["status"]
        == "D20_HAMMING_GAUSSIAN_PYTHON_WORK_ARCHIVE_IMPORT_CERTIFIED_PARTIAL_REPLAY"
        and archive["checks"]["indicator_shell_domination_passes_boolean_case"] is True,
        "direct_entropy_attempt_import_certified": direct["status"]
        == "D20_GOLAY_ENTROPY_DIRECT_ATTEMPT_IMPORT_CERTIFIED"
        and direct["all_checks_pass"] is True,
        "generated_code_has_4096_words": len(code) == 4096,
        "generated_code_weight_histogram_matches_w24": hist == {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1},
        "two_level_rows_nonempty": len(rows) > 0,
        "all_selected_two_level_maxima_within_tolerance": max_f <= TOL,
        "all_selected_endpoint_limits_within_tolerance": all(
            row["endpoint_left_F"] <= TOL and row["endpoint_right_F"] <= TOL for row in rows
        ),
        "equality_orbit_seen_at_t_zero": any(abs(row["max_F"]) <= TOL and abs(row["arg_t"]) <= 1e-11 for row in rows),
        "final_arbitrary_vector_theorem_not_certified": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_two_level_lift_probe.artifact@1",
        "status": "D20_GOLAY_SHELL_TWO_LEVEL_LIFT_PROBE_NO_COUNTEREXAMPLE",
        "claim_scope": (
            "Two-level nonnegative lift probe for the Golay shell entropy domination "
            "inequality. This certifies selected split masks, including all W24 shell supports, "
            "canonical MOG masks, indicator-worst masks, and deterministic random masks. It is "
            "not a proof over all subsets or arbitrary nonnegative vectors."
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
            "direct_entropy_attempt": input_entry(
                DIRECT_ATTEMPT_REPORT,
                {"status": direct["status"], "certificate_sha256": direct["certificate_sha256"]},
            ),
            "indicator_shell_csv": input_entry(INDICATOR_CSV),
        },
        "definition": {
            "two_level_vector": "x_i=exp(t) on S and x_i=1 off S",
            "objective": (
                "F_w(S,t)=log(sum_B exp(t*|B cap S|))-log(A_w)"
                "-(w/2)log((|S|exp(2t)+24-|S|)/24)"
            ),
            "target": "F_w(S,t)<=0 for w in {12,16}.",
            "optimization": (
                "For each selected profile, derivative sign changes on [-40,40] are bracketed "
                "on a 1600-step grid and refined by bisection; endpoints approximate the "
                "two Boolean face limits."
            ),
        },
        "selection": {
            "split_mask_count": len({row["support_mask"] for row in rows}),
            "two_level_row_count": len(rows),
            "shells": list(SHELLS),
            "included_families": [
                "empty and full support",
                "all prefixes and complements",
                "all singletons and complements",
                "MOG rows and columns",
                "certified W24 row, row-pair, and column-pair masks",
                "all W24 shell supports of weights 8,12,16,24 and complements",
                "indicator-shell worst masks from the exhaustive Boolean certificate",
                "deterministic random masks stratified by support size",
            ],
            "unique_profiles": profile_summary,
        },
        "witness": {
            "max_F": max_f,
            "max_excess_over_tolerance": max_excess,
            "tolerance": TOL,
            "top_rows": top_rows,
            "csv": input_entry(csv_path),
        },
        "open_boundary": {
            "certified_here": [
                "no two-level counterexample on the selected split-mask family",
                "all W24 shell-support splits of weights 8,12,16,24 are included",
                "the Boolean endpoint limits for those selected splits stay within tolerance",
            ],
            "not_certified": [
                "all possible split masks up to M24 orbit",
                "arbitrary nonnegative vectors with three or more distinct values",
                "the final w=12 entropy contraction theorem",
                "the final w=16 entropy contraction theorem",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_two_level_lift_probe@1",
        "status": "D20_GOLAY_SHELL_TWO_LEVEL_LIFT_PROBE_CERTIFIED_NO_COUNTEREXAMPLE",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The selected two-level lift from Boolean indicator faces toward arbitrary "
            "nonnegative shell weights produced no counterexample for w=12 or w=16. The tested "
            "family includes all W24 shell supports, canonical MOG masks, indicator-worst masks, "
            "and deterministic random split masks. This narrows the entropy gap but does not "
            "prove the arbitrary-vector shell domination theorem."
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
            "Replace selected split masks by an exhaustive M24 subset-orbit/Terwilliger "
            "reduction, then certify every two-level profile before attacking three-level or "
            "full Krawtchouk/SOS domination."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_two_level_lift_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24 endpoint and handoff archive/direct-attempt inputs",
            "rebuild the W24 code from the certified generator basis",
            "construct selected two-level split masks",
            "optimize the w=12 and w=16 two-level shell objectives over t",
            "verify no selected two-level maximum exceeds tolerance",
            "record that the arbitrary-vector theorem remains open",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "two_level_csv": relpath(OUT_DIR / "two_level_lift_profiles.csv"),
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
                "max_F": artifact["witness"]["max_F"],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "split_mask_count": artifact["selection"]["split_mask_count"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
