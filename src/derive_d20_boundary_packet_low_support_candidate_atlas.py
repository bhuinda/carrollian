from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_boundary_packet_low_support_candidate_atlas"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE = (
    D20_INVARIANTS / "theorems" / "d20_boundary_loop_step_atom_incidence" / "report.json"
)
D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION = (
    D20_INVARIANTS
    / "theorems"
    / "d20_boundary_packet_row_normalization_obstruction"
    / "report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_packet_bridge_snf_obstruction" / "report.json"
)

COEFFICIENT_SET = [-1, 1]
SUPPORT_LIMIT = 2


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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def matrix_rank_rational(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(work)
    col_count = len(work[0]) if row_count else 0
    rank = 0
    col = 0
    while rank < row_count and col < col_count:
        pivot = None
        for row in range(rank, row_count):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            col += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][col]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                work[row][idx] - factor * work[rank][idx] for idx in range(col_count)
            ]
        rank += 1
        col += 1
    return rank


def local_failures(u: int, v: int) -> list[str]:
    failures = []
    if u % 2 != 0:
        failures.append("u_not_0_mod_2")
    if v % 2 != 0:
        failures.append("v_not_0_mod_2")
    if (u + v) % 6 != 0:
        failures.append("u_plus_v_not_0_mod_6")
    return failures


def image_for_support(
    support: list[dict[str, int]], matrix: list[list[int]]
) -> list[int]:
    return [
        sum(row["coefficient"] * matrix[row["public_atom_id"]][col] for row in support)
        for col in range(len(matrix[0]))
    ]


def generate_candidates(matrix: list[list[int]]) -> list[dict[str, Any]]:
    candidates = []
    candidate_id = 0
    for atom_id in range(len(matrix)):
        for coefficient in COEFFICIENT_SET:
            support = [{"public_atom_id": atom_id, "coefficient": coefficient}]
            image = image_for_support(support, matrix)
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "support_size": 1,
                    "coefficient_support": support,
                    "image_vector": image,
                }
            )
            candidate_id += 1
    for left, right in combinations(range(len(matrix)), 2):
        for left_coefficient in COEFFICIENT_SET:
            for right_coefficient in COEFFICIENT_SET:
                support = [
                    {"public_atom_id": left, "coefficient": left_coefficient},
                    {"public_atom_id": right, "coefficient": right_coefficient},
                ]
                image = image_for_support(support, matrix)
                candidates.append(
                    {
                        "candidate_id": candidate_id,
                        "support_size": 2,
                        "coefficient_support": support,
                        "image_vector": image,
                    }
                )
                candidate_id += 1
    return candidates


def enrich_candidate(candidate: dict[str, Any], public_atom_rows: list[dict[str, Any]]) -> dict[str, Any]:
    image = [int(value) for value in candidate["image_vector"]]
    nonzero = [
        {"step_atom_id": idx, "coefficient": value}
        for idx, value in enumerate(image)
        if value != 0
    ]
    support = []
    for item in candidate["coefficient_support"]:
        atom_id = int(item["public_atom_id"])
        support.append(
            {
                "public_atom_id": atom_id,
                "coefficient": int(item["coefficient"]),
                "public_atom_label": public_atom_rows[atom_id]["public_atom_label"],
            }
        )
    return {
        "candidate_id": int(candidate["candidate_id"]),
        "support_size": int(candidate["support_size"]),
        "coefficient_support": support,
        "image_vector": image,
        "image_gcd": math.gcd(*[abs(value) for value in image]) if any(image) else 0,
        "image_is_even": all(value % 2 == 0 for value in image),
        "image_nonzero_count": len(nonzero),
        "image_value_histogram": histogram(Counter(image)),
        "step_atom_support": nonzero,
    }


def compatible_doublet_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for left, right in combinations(candidates, 2):
        left_image = left["image_vector"]
        right_image = right["image_vector"]
        if all(
            not local_failures(left_image[col], right_image[col])
            for col in range(len(left_image))
        ):
            rows.append(
                {
                    "doublet_id": len(rows),
                    "left_candidate_id": left["candidate_id"],
                    "right_candidate_id": right["candidate_id"],
                    "left_support": left["coefficient_support"],
                    "right_support": right["coefficient_support"],
                    "right_is_negative_left": right_image == [-value for value in left_image],
                    "doublet_rank_over_Q": matrix_rank_rational([left_image, right_image]),
                    "passes_packet_snf_image": True,
                }
            )
    return rows


def support_family_rows(even_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[tuple[int, ...], list[int]] = {}
    for row in even_rows:
        family = tuple(
            int(item["public_atom_id"]) for item in row["coefficient_support"]
        )
        by_family.setdefault(family, []).append(int(row["candidate_id"]))
    return [
        {
            "public_atom_support": list(family),
            "candidate_ids": sorted(candidate_ids),
            "signed_candidate_count": len(candidate_ids),
        }
        for family, candidate_ids in sorted(by_family.items())
    ]


def build_theorem() -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE)
    row_norm = load_json(D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    public_atom_rows = incidence["derived"]["public_atom_rows"]
    candidates = generate_candidates(matrix)
    even_rows = [
        enrich_candidate(candidate, public_atom_rows)
        for candidate in candidates
        if all(value % 2 == 0 for value in candidate["image_vector"])
    ]
    support_rows = support_family_rows(even_rows)
    doublet_rows = compatible_doublet_rows(even_rows)
    even_image_rank = matrix_rank_rational([row["image_vector"] for row in even_rows])
    support_hist = histogram(Counter(candidate["support_size"] for candidate in candidates))
    even_support_hist = histogram(Counter(row["support_size"] for row in even_rows))
    summary = {
        "candidate_family": "signed_support_at_most_2_boundary_combinations",
        "coefficient_set": COEFFICIENT_SET,
        "support_limit": SUPPORT_LIMIT,
        "candidate_count": len(candidates),
        "candidate_support_size_histogram": support_hist,
        "even_image_candidate_count": len(even_rows),
        "even_image_support_size_histogram": even_support_hist,
        "even_image_support_family_count": len(support_rows),
        "even_image_support_families": [
            row["public_atom_support"] for row in support_rows
        ],
        "even_image_span_rank_over_Q": even_image_rank,
        "compatible_doublet_count": len(doublet_rows),
        "compatible_doublet_rank_histogram": histogram(
            Counter(row["doublet_rank_over_Q"] for row in doublet_rows)
        ),
        "all_compatible_doublets_are_opposite_rows": all(
            row["right_is_negative_left"] for row in doublet_rows
        ),
        "full_packet_doublet_map_available": False,
    }
    local_image_test = packet_snf["derived"]["obstruction_summary"]["local_image_test"]
    checks = {
        "boundary_loop_step_atom_incidence_is_certified": incidence.get("status")
        == "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED"
        and incidence.get("all_checks_pass") is True,
        "row_normalization_obstruction_is_certified": row_norm.get("status")
        == "D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_CERTIFIED"
        and row_norm.get("all_checks_pass") is True,
        "packet_bridge_snf_obstruction_is_certified": packet_snf.get("status")
        == "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED"
        and packet_snf.get("all_checks_pass") is True,
        "packet_snf_local_test_is_exact": local_image_test
        == "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet",
        "incidence_matrix_is_20_by_25": len(matrix) == 20
        and all(len(row) == 25 for row in matrix),
        "candidate_count_is_800": len(candidates) == 800,
        "candidate_support_histogram_matches": support_hist == {"1": 40, "2": 760},
        "even_image_candidate_count_is_12": len(even_rows) == 12,
        "no_support_1_even_image_candidates": even_support_hist == {"2": 12},
        "even_image_support_families_match": summary["even_image_support_families"]
        == [[0, 11], [6, 17], [14, 15]],
        "even_image_span_rank_is_6": even_image_rank == 6,
        "compatible_doublet_count_is_6": len(doublet_rows) == 6,
        "compatible_doublets_are_rank_one": all(
            row["doublet_rank_over_Q"] == 1 for row in doublet_rows
        ),
        "compatible_doublets_are_only_opposite_rows": summary[
            "all_compatible_doublets_are_opposite_rows"
        ]
        is True,
        "no_full_packet_doublet_map_available": summary[
            "full_packet_doublet_map_available"
        ]
        is False,
    }
    report = {
        "schema": "d20.theorem.d20_boundary_packet_low_support_candidate_atlas",
        "status": "D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_CERTIFIED",
        "object": "D20",
        "definition": {
            "candidate_family": summary["candidate_family"],
            "coefficient_set": COEFFICIENT_SET,
            "support_limit": SUPPORT_LIMIT,
            "packet_snf_image_test": local_image_test,
        },
        "claim": (
            "The first non-diagonal low-support signed boundary combinations that can pass "
            "the packet SNF parity layer are exactly twelve support-2 rows over public atom "
            "families [0,11], [6,17], and [14,15]. They form six packet-compatible doublet "
            "candidates by pairing each row with its negative, but every such doublet has "
            "rank one, so this is a degenerate candidate atlas rather than a full 20-packet "
            "bridge."
        ),
        "inputs": {
            "d20_boundary_loop_step_atom_incidence_report": input_record(
                D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE
            ),
            "d20_boundary_packet_row_normalization_obstruction_report": input_record(
                D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION
            ),
            "d20_packet_bridge_snf_obstruction_report": input_record(
                D20_PACKET_BRIDGE_SNF_OBSTRUCTION
            ),
        },
        "derived": {
            "low_support_summary": summary,
            "even_image_candidate_rows": even_rows,
            "even_image_candidate_rows_sha256": sha_json(even_rows),
            "even_image_support_family_rows": support_rows,
            "even_image_support_family_rows_sha256": sha_json(support_rows),
            "compatible_doublet_candidate_rows": doublet_rows,
            "compatible_doublet_candidate_rows_sha256": sha_json(doublet_rows),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "positive_boundary": (
                "Non-diagonal signed support-2 boundary combinations do exist and can satisfy "
                "the packet SNF image test when paired with their negatives."
            ),
            "degeneracy": (
                "These candidates are rank-one plus/minus doublets and only cover three "
                "support families, so they do not supply the ten independent packet doublets "
                "needed for the full Mat_2(Q)^10 bridge."
            ),
            "not_claimed": (
                "This is not an A985/tube/q42/q12 packet action and not a physical M-theory "
                "or DLCQ lift."
            ),
        },
        "next_highest_yield_item": (
            "Extend the signed-combination search to support 3, then test whether any "
            "packet-compatible doublets have rank two or assemble into more than three "
            "independent support families."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_boundary_packet_low_support_candidate_atlas_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "enumerate signed support-at-most-2 boundary combinations against packet SNF tests",
            "isolate the first non-diagonal candidate atlas and record its rank-one degeneracy",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
