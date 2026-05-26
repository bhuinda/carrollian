from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_golay_shell_three_level_structured_probe"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
PROFILE_CSV = OUT_DIR / "three_level_structured_profiles.csv"

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

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_shell_three_level_structured_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_shell_three_level_structured_probe.py"

N = 24
FULL_MASK = (1 << N) - 1
SHELLS = (12, 16)
BOUND = 20.0
TOL = 1e-8


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


def add_partition(
    partitions: dict[tuple[int, int], set[str]],
    first: int,
    second: int,
    label: str,
) -> None:
    first &= FULL_MASK
    second &= FULL_MASK
    second &= ~first
    partitions.setdefault((first, second), set()).add(label)
    partitions.setdefault((second, first), set()).add(f"swap:{label}")


def structural_masks(w24: dict[str, Any]) -> dict[str, int]:
    witness = w24["witness"]
    containment = witness["containment_witnesses"]
    grid = witness["row_alphabetization"]["grid_row_major"]
    masks: dict[str, int] = {"empty": 0, "full": FULL_MASK}
    for k in range(N + 1):
        masks[f"prefix_{k}"] = (1 << k) - 1 if k else 0
    for row_i, row in enumerate(grid):
        masks[f"mog_row_{row_i}"] = sum(1 << i for i in row)
    for col in range(6):
        masks[f"mog_column_{col}"] = sum(1 << row[col] for row in grid)
    for index, mask in enumerate(containment["row_masks"]):
        masks[f"w24_row_mask_{index}"] = int(mask)
    for index, mask in enumerate(containment["row_pair_masks"]):
        masks[f"w24_row_pair_mask_{index}"] = int(mask)
    for index, mask in enumerate(containment["column_pair_generator_masks"]):
        masks[f"w24_column_pair_codeword_{index}"] = int(mask)
    masks["wu_octad"] = int(containment["wu_octad_mask"])
    return masks


def deterministic_ternary_partitions(count: int = 600) -> list[tuple[int, int, str]]:
    rng = random.Random(20260526)
    rows: list[tuple[int, int, str]] = []
    for i in range(count):
        first = 0
        second = 0
        for bit in range(N):
            color = rng.randrange(3)
            if color == 1:
                first |= 1 << bit
            elif color == 2:
                second |= 1 << bit
        rows.append((first, second, f"deterministic_ternary_{i}"))
    return rows


def selected_partitions(w24: dict[str, Any], code: list[int]) -> dict[tuple[int, int], set[str]]:
    masks = structural_masks(w24)
    partitions: dict[tuple[int, int], set[str]] = {}

    add_partition(partitions, 0, 0, "all_baseline")
    for a in range(N + 1):
        for b in range(a, N + 1):
            first = (1 << a) - 1 if a else 0
            union = (1 << b) - 1 if b else 0
            add_partition(partitions, first, union ^ first, f"prefix_flag_{a}_{b}")

    mask_items = sorted(masks.items())
    for name_a, mask_a in mask_items:
        for name_b, mask_b in mask_items:
            add_partition(partitions, mask_a & ~mask_b, mask_b & ~mask_a, f"struct_symdiff:{name_a}:{name_b}")
            add_partition(partitions, mask_a & mask_b, mask_a & ~mask_b, f"struct_flag:{name_a}:{name_b}")

    splitter_items = [
        (name, mask)
        for name, mask in mask_items
        if name.startswith("mog_")
        or name.startswith("w24_row_pair")
        or name.startswith("w24_column_pair")
        or name == "wu_octad"
    ]
    for word in code:
        word_weight = wt(word)
        if word_weight not in (8, 12, 16, 24):
            continue
        for name, splitter in splitter_items:
            add_partition(
                partitions,
                word & splitter,
                word & ~splitter,
                f"codeword_w{word_weight}_split_by_{name}",
            )
            add_partition(
                partitions,
                word & splitter,
                (~word) & splitter,
                f"splitter_{name}_inside_outside_codeword_w{word_weight}",
            )

    by_weight: dict[int, list[int]] = {8: [], 12: [], 16: [], 24: []}
    for word in code:
        weight = wt(word)
        if weight in by_weight and len(by_weight[weight]) < 80:
            by_weight[weight].append(word)
    for weight_a, words_a in by_weight.items():
        for weight_b, words_b in by_weight.items():
            for a in words_a[:24]:
                for b in words_b[:24]:
                    add_partition(
                        partitions,
                        a & b,
                        a & ~b,
                        f"codeword_pair_flag_w{weight_a}_w{weight_b}",
                    )

    for first, second, label in deterministic_ternary_partitions():
        add_partition(partitions, first, second, label)

    return partitions


def shell_profile(shell_words: np.ndarray, first: int, second: int, shell: int) -> list[int]:
    j = np.bitwise_count(np.bitwise_and(shell_words, np.uint32(first))).astype(np.int16)
    k = np.bitwise_count(np.bitwise_and(shell_words, np.uint32(second))).astype(np.int16)
    flat = j * (shell + 1) + k
    counts = np.bincount(flat, minlength=(shell + 1) * (shell + 1)).astype(np.int64)
    return counts.reshape(shell + 1, shell + 1).ravel().astype(int).tolist()


def profile_support_sizes(profile: list[int], shell: int, shell_count: int) -> tuple[int, int]:
    first_num = 0
    second_num = 0
    for j in range(shell + 1):
        for k in range(shell + 1):
            count = profile[j * (shell + 1) + k]
            first_num += j * count
            second_num += k * count
    den = shell_count * shell
    a_num = N * first_num
    b_num = N * second_num
    if a_num % den or b_num % den:
        raise ValueError("profile support-size moments are not integral")
    return a_num // den, b_num // den


def objective(profile: list[int], shell: int, first_size: int, second_size: int, u: float, v: float) -> float:
    shell_count = sum(profile)
    terms = []
    for j in range(shell + 1):
        for k in range(shell + 1):
            count = profile[j * (shell + 1) + k]
            if count:
                terms.append((j * u + k * v, count))
    m = max(x for x, _ in terms)
    log_num = m + math.log(sum(count * math.exp(x - m) for x, count in terms))
    rest = N - first_size - second_size
    denom = first_size * math.exp(2 * u) + second_size * math.exp(2 * v) + rest
    return log_num - math.log(shell_count) - (shell / 2) * (math.log(denom) - math.log(N))


def gradient(profile: list[int], shell: int, first_size: int, second_size: int, u: float, v: float) -> tuple[float, float]:
    terms = []
    for j in range(shell + 1):
        for k in range(shell + 1):
            count = profile[j * (shell + 1) + k]
            if count:
                terms.append((j * u + k * v, j, k, count))
    m = max(x for x, _, _, _ in terms)
    weights = [count * math.exp(x - m) for x, _, _, count in terms]
    z = sum(weights)
    ej = sum(j * weight for weight, (_, j, _, _) in zip(weights, terms)) / z
    ek = sum(k * weight for weight, (_, _, k, _) in zip(weights, terms)) / z
    rest = N - first_size - second_size
    eu = math.exp(2 * u)
    ev = math.exp(2 * v)
    denom = first_size * eu + second_size * ev + rest
    return (
        ej - shell * first_size * eu / denom,
        ek - shell * second_size * ev / denom,
    )


def hessian_at_equality(profile: list[int], shell: int, first_size: int, second_size: int) -> list[float]:
    shell_count = sum(profile)
    ej = shell * first_size / N
    ek = shell * second_size / N
    ejj = 0.0
    ejk = 0.0
    ekk = 0.0
    for j in range(shell + 1):
        for k in range(shell + 1):
            count = profile[j * (shell + 1) + k]
            p = count / shell_count
            ejj += j * j * p
            ejk += j * k * p
            ekk += k * k * p
    cov_jj = ejj - ej * ej
    cov_jk = ejk - ej * ek
    cov_kk = ekk - ek * ek
    h11 = cov_jj - 2 * shell * first_size * (N - first_size) / (N * N)
    h22 = cov_kk - 2 * shell * second_size * (N - second_size) / (N * N)
    h12 = cov_jk + 2 * shell * first_size * second_size / (N * N)
    trace = h11 + h22
    disc = max((h11 - h22) * (h11 - h22) + 4 * h12 * h12, 0.0)
    root = math.sqrt(disc)
    return [(trace - root) / 2, (trace + root) / 2]


def optimize_profile(profile: list[int], shell: int, first_size: int, second_size: int) -> dict[str, Any]:
    starts = [
        (0.0, 0.0),
        (-8.0, -8.0),
        (-8.0, 0.0),
        (-8.0, 8.0),
        (0.0, -8.0),
        (0.0, 8.0),
        (8.0, -8.0),
        (8.0, 0.0),
        (8.0, 8.0),
        (-16.0, 4.0),
        (4.0, -16.0),
        (16.0, -4.0),
        (-4.0, 16.0),
    ]
    best_f = -1e300
    best = (0.0, 0.0)
    best_grad = (0.0, 0.0)
    for start_u, start_v in starts:
        u = start_u
        v = start_v
        current = objective(profile, shell, first_size, second_size, u, v)
        for _ in range(200):
            gu, gv = gradient(profile, shell, first_size, second_size, u, v)
            norm = math.hypot(gu, gv)
            if norm < 1e-11:
                break
            step = 1.0
            improved = False
            while step > 1e-10:
                nu = max(-BOUND, min(BOUND, u + step * gu))
                nv = max(-BOUND, min(BOUND, v + step * gv))
                candidate = objective(profile, shell, first_size, second_size, nu, nv)
                if candidate >= current + 1e-14:
                    u, v = nu, nv
                    current = candidate
                    improved = True
                    break
                step *= 0.5
            if not improved:
                break
        gu, gv = gradient(profile, shell, first_size, second_size, u, v)
        if current > best_f:
            best_f = current
            best = (u, v)
            best_grad = (gu, gv)

    grid_best = best_f
    grid_best_at = best
    for u in (-BOUND, -12.0, -6.0, 0.0, 6.0, 12.0, BOUND):
        for v in (-BOUND, -12.0, -6.0, 0.0, 6.0, 12.0, BOUND):
            value = objective(profile, shell, first_size, second_size, u, v)
            if value > grid_best:
                grid_best = value
                grid_best_at = (u, v)

    eig = hessian_at_equality(profile, shell, first_size, second_size)
    return {
        "best_F": max(best_f, grid_best),
        "best_u": best[0] if best_f >= grid_best else grid_best_at[0],
        "best_v": best[1] if best_f >= grid_best else grid_best_at[1],
        "best_gradient_norm": math.hypot(*best_grad),
        "hessian_min_eigenvalue_at_equality": min(eig),
        "hessian_max_eigenvalue_at_equality": max(eig),
        "local_hessian_nonpositive": max(eig) <= 1e-9,
    }


def build_profiles(w24: dict[str, Any], code: list[int]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    partitions = selected_partitions(w24, code)
    shell_arrays = {
        shell: np.array([word for word in code if wt(word) == shell], dtype=np.uint32)
        for shell in SHELLS
    }
    profile_map: dict[tuple[int, str], dict[str, Any]] = {}
    for index, ((first, second), labels) in enumerate(sorted(partitions.items())):
        first_size = wt(first)
        second_size = wt(second)
        if first & second:
            raise ValueError("partition levels overlap")
        if first_size + second_size > N:
            raise ValueError("partition levels exceed coordinate set")
        for shell in SHELLS:
            profile = shell_profile(shell_arrays[shell], first, second, shell)
            shell_count = len(shell_arrays[shell])
            moment_first, moment_second = profile_support_sizes(profile, shell, shell_count)
            if (moment_first, moment_second) != (first_size, second_size):
                raise ValueError("profile moments do not match partition sizes")
            key = (shell, ",".join(str(x) for x in profile))
            if key not in profile_map:
                opt = optimize_profile(profile, shell, first_size, second_size)
                profile_map[key] = {
                    "shell": shell,
                    "first_size": first_size,
                    "second_size": second_size,
                    "rest_size": N - first_size - second_size,
                    "profile": key[1],
                    "partition_count": 0,
                    "example_labels": ";".join(sorted(labels)[:8]),
                    **opt,
                }
            profile_map[key]["partition_count"] += 1
    rows = sorted(profile_map.values(), key=lambda row: (row["shell"], -row["best_F"], row["first_size"], row["second_size"], row["profile"]))
    summary = {
        "selected_partition_count": len(partitions),
        "unique_profile_count": len(rows),
        "unique_profile_count_by_shell": {
            str(shell): sum(1 for row in rows if row["shell"] == shell) for shell in SHELLS
        },
        "max_best_F": max(row["best_F"] for row in rows),
        "positive_profile_count": sum(1 for row in rows if row["best_F"] > TOL),
        "local_hessian_positive_count": sum(
            1 for row in rows if row["local_hessian_nonpositive"] is not True
        ),
        "top_profiles": rows[:12],
    }
    return rows, summary


def write_profile_csv(rows: list[dict[str, Any]]) -> None:
    PROFILE_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "shell",
        "first_size",
        "second_size",
        "rest_size",
        "partition_count",
        "best_F",
        "best_u",
        "best_v",
        "best_gradient_norm",
        "hessian_min_eigenvalue_at_equality",
        "hessian_max_eigenvalue_at_equality",
        "local_hessian_nonpositive",
        "example_labels",
        "profile",
    ]
    with PROFILE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_artifact() -> dict[str, Any]:
    w24 = load_json(W24_REPORT)
    two_level = load_json(TWO_LEVEL_REPORT)
    basis = [int(x) for x in w24["witness"]["golay_code"]["generator_basis_masks"]]
    code = span_from_basis(basis)
    hist = weight_hist(code)
    rows, summary = build_profiles(w24, code)
    write_profile_csv(rows)

    checks = {
        "w24_endpoint_certified": w24["status"] == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "exhaustive_two_level_input_certified": two_level["status"]
        == "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_SOS_CERTIFIED"
        and two_level["all_checks_pass"] is True,
        "generated_code_has_4096_words": len(code) == 4096,
        "generated_code_weight_histogram_matches_w24": hist == {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1},
        "selected_partitions_nonempty": summary["selected_partition_count"] > 0,
        "unique_profiles_nonempty": summary["unique_profile_count"] > 0,
        "no_positive_structured_three_level_profile_found": summary["positive_profile_count"] == 0,
        "all_profile_hessians_nonpositive_at_equality": summary["local_hessian_positive_count"] == 0,
        "profile_csv_written": PROFILE_CSV.exists(),
        "full_three_level_exhaustion_not_certified": True,
        "full_arbitrary_vector_theorem_not_certified": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_three_level_structured_probe.artifact@1",
        "status": "D20_GOLAY_SHELL_THREE_LEVEL_STRUCTURED_PROBE_NO_COUNTEREXAMPLE",
        "claim_scope": (
            "Structured three-level probe for the w=12 and w=16 Golay shell domination "
            "inequality. The family includes prefix flags, MOG structural partitions, W24 "
            "codeword support splits, representative codeword-pair flags, and deterministic "
            "random ternary partitions. This is not exhaustive over all 3^24 ordered "
            "three-colorings."
        ),
        "source_reports": {
            "w24_row_alphabetization": input_entry(
                W24_REPORT,
                {"status": w24["status"], "certificate_sha256": w24["certificate_sha256"]},
            ),
            "exhaustive_two_level_sos": input_entry(
                TWO_LEVEL_REPORT,
                {"status": two_level["status"], "certificate_sha256": two_level["certificate_sha256"]},
            ),
        },
        "definition": {
            "three_level_vector": "x_i=exp(u) on A, x_i=exp(v) on B, and x_i=1 off A union B, with A cap B empty.",
            "objective": (
                "F_w(A,B,u,v)=log(sum_{block} exp(u|block cap A|+v|block cap B|))-log(A_w)"
                "-(w/2)log((|A|exp(2u)+|B|exp(2v)+24-|A|-|B|)/24)"
            ),
            "edge_boundary": (
                "The u=0, v=0, u=v, and level-empty faces reduce to the exhaustive two-level "
                "certificate already proved."
            ),
        },
        "selection": {
            "included_families": [
                "all prefix flags A subset A union B",
                "all pairwise structural MOG/W24 mask flags and symmetric differences",
                "all W24 codeword supports split by MOG rows, columns, row-pairs, column-pair codewords, and Wu octad",
                "representative codeword-pair flags by shell weight",
                "deterministic ternary random partitions",
            ],
            **summary,
        },
        "witness": {
            "profile_csv": input_entry(PROFILE_CSV),
            "profile_csv_row_count": len(rows),
            "top_profiles": summary["top_profiles"],
            "max_best_F": summary["max_best_F"],
            "tolerance": TOL,
        },
        "open_boundary": {
            "certified_here": [
                "no positive maximum found in the selected structured three-level profile family",
                "all selected profiles have nonpositive Hessian at the equality point",
                "all one-dimensional faces are covered by the exhaustive two-level certificate",
            ],
            "not_certified": [
                "all 3^24 ordered three-level partitions",
                "a bivariate positive-coefficient/SOS certificate for every three-level profile",
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
        "schema": "d20.proof_obligation.golay_shell_three_level_structured_probe@1",
        "status": "D20_GOLAY_SHELL_THREE_LEVEL_STRUCTURED_PROBE_CERTIFIED_NO_COUNTEREXAMPLE",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The structured three-level probe found no counterexample for w=12 or w=16. "
            "It tested prefix flags, MOG/W24 structural partitions, W24 codeword support "
            "splits, representative codeword-pair flags, and deterministic ternary random "
            "partitions. Every selected profile has nonpositive Hessian at equality and "
            "numerical ascent returned no positive objective. This is a diagnostic bridge "
            "beyond the exhaustive two-level theorem, not a full three-level theorem."
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
            "Derive actual M24/Terwilliger orbit representatives for ordered three-colorings. "
            "That would replace this structured probe with an exhaustive three-level profile "
            "certificate."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_shell_three_level_structured_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24 endpoint and exhaustive two-level input",
            "rebuild W24 from the certified generator basis",
            "construct selected structured three-level partitions",
            "compute exact shell intersection profiles for selected partitions",
            "run deterministic bounded gradient ascent from fixed starts on each unique profile",
            "verify no positive structured three-level maximum is found",
            "verify local Hessian at equality is nonpositive for every selected profile",
            "record that full three-level exhaustion remains open",
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
                "max_best_F": artifact["witness"]["max_best_F"],
                "profiles": artifact["witness"]["profile_csv_row_count"],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "selected_partitions": artifact["selection"]["selected_partition_count"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
