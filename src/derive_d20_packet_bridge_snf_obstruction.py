from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_sandpile_critical_group_theorem import smith_normal_form_diagonal
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_packet_bridge_snf_obstruction.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import smith_normal_form_diagonal
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_packet_bridge_snf_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)
D20_FULL_PACKET_MATRIX_LIFT = (
    D20_INVARIANTS / "theorems" / "d20_full_packet_matrix_lift" / "report.json"
)
D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST = (
    D20_INVARIANTS / "theorems" / "d20_explicit_packet_restriction_map_test" / "report.json"
)


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


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def zero_matrix(size: int) -> list[list[int]]:
    return [[0 for _ in range(size)] for _ in range(size)]


def block_diagonal_from_components(component_rows: list[dict[str, Any]]) -> list[list[int]]:
    size = 2 * len(component_rows)
    out = zero_matrix(size)
    for component_index, row in enumerate(component_rows):
        block = row["block_matrix"]
        offset = 2 * component_index
        for i in range(2):
            for j in range(2):
                out[offset + i][offset + j] = int(block[i][j])
    return out


def matrix_rank_rational(matrix: list[list[int]]) -> int:
    work = [[float(value) for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    col = 0
    while rank < rows and col < cols:
        pivot = None
        for r in range(rank, rows):
            if abs(work[r][col]) > 1e-9:
                pivot = r
                break
        if pivot is None:
            col += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][col]
        work[rank] = [value / scale for value in work[rank]]
        for r in range(rows):
            if r == rank:
                continue
            factor = work[r][col]
            if abs(factor) > 1e-9:
                work[r] = [work[r][c] - factor * work[rank][c] for c in range(cols)]
        rank += 1
        col += 1
    return rank


def prime_factors(values: list[int]) -> list[int]:
    factors: set[int] = set()
    for value in values:
        n = abs(int(value))
        divisor = 2
        while divisor * divisor <= n:
            while n % divisor == 0:
                factors.add(divisor)
                n //= divisor
            divisor += 1
        if n > 1:
            factors.add(n)
    return sorted(factors)


def build_congruence_rows(component_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for component_index, row in enumerate(component_rows):
        pair = [int(value) for value in row["packet_pair"]]
        rows.append(
            {
                "component_id": component_index,
                "packet_pair": pair,
                "block_matrix": row["block_matrix"],
                "local_smith_diagonal": [2, 6],
                "local_cokernel": "Z/2 x Z/6",
                "image_test_for_target_pair_u_v": [
                    "u_minus_v_is_0_mod_2",
                    "u_plus_v_is_0_mod_6",
                ],
            }
        )
    return rows


def build_bridge_tasks(missing_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate": row["candidate"],
            "prior_status": row["status"],
            "snf_status": "packet_obstruction_template_ready_no_raw_columns",
            "source_domain": row["source_domain"],
            "target_domain": row["target_domain"],
            "available_source_keys": row["available_source_keys"],
            "test_once_columns_exist": (
                "for each packet doublet target (u,v), require u-v = 0 mod 2 and u+v = 0 mod 6"
            ),
        }
        for row in missing_rows
    ]


def build_theorem() -> dict[str, Any]:
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    full_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT)
    restriction = load_json(D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST)

    component_rows = graph["derived"]["component_rows"]
    graph_adjacency = graph["derived"]["adjacency"]["matrix"]
    packet_operator = block_diagonal_from_components(component_rows)
    snf = smith_normal_form_diagonal(packet_operator)
    local_snf = smith_normal_form_diagonal([[2, 4], [4, 2]])
    nonunit = [int(value) for value in snf["nonunit_invariant_factors"]]
    determinant_abs = math.prod(nonunit)
    diagonal_multiplicities = {
        str(key): int(value) for key, value in sorted(Counter(nonunit).items())
    }
    congruence_rows = build_congruence_rows(component_rows)
    missing_rows = restriction["derived"]["missing_bridge_inventory"]
    bridge_tasks = build_bridge_tasks(missing_rows)
    obstruction_summary = {
        "packet_operator": "direct_sum_10_copies_of_2I_plus_4S",
        "matrix_shape": [len(packet_operator), len(packet_operator[0])],
        "rank_over_Q": matrix_rank_rational(packet_operator),
        "smith_diagonal_multiplicities": diagonal_multiplicities,
        "nonunit_invariant_factors": nonunit,
        "cokernel": "Z/2^10 x Z/6^10",
        "cokernel_order": determinant_abs,
        "torsion_primes": prime_factors(nonunit),
        "local_block_smith_diagonal": local_snf["diagonal"],
        "local_image_test": "u-v = 0 mod 2 and u+v = 0 mod 6 on each packet doublet",
        "raw_bridge_columns_available": False,
        "raw_bridge_candidate_count": len(bridge_tasks),
    }
    checks = {
        "packet_graph_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "full_packet_matrix_lift_is_certified": full_lift.get("status")
        == "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED"
        and full_lift.get("all_checks_pass") is True,
        "explicit_restriction_test_is_certified": restriction.get("status")
        == "D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_CERTIFIED"
        and restriction.get("all_checks_pass") is True,
        "packet_operator_matches_graph_adjacency": packet_operator == graph_adjacency,
        "ten_uniform_blocks_present": len(component_rows) == 10
        and all(row["block_matrix"] == [[2, 4], [4, 2]] for row in component_rows),
        "local_smith_diagonal_is_2_6": local_snf["diagonal"] == [2, 6]
        and local_snf["off_diagonal_nonzero"] == 0,
        "global_smith_diagonal_is_2_power_10_6_power_10": diagonal_multiplicities
        == {"2": 10, "6": 10},
        "global_smith_form_is_diagonal": snf["off_diagonal_nonzero"] == 0,
        "global_smith_divisibility_chain_valid": snf["divisibility_chain_valid"] is True,
        "operator_has_full_rank": obstruction_summary["rank_over_Q"] == 20,
        "cokernel_order_matches_block_determinant": determinant_abs == 12**10,
        "torsion_primes_are_2_and_3": obstruction_summary["torsion_primes"] == [2, 3],
        "bridge_tasks_match_missing_inventory": [row["candidate"] for row in bridge_tasks]
        == [row["candidate"] for row in missing_rows],
    }
    report = {
        "schema": "d20.theorem.d20_packet_bridge_snf_obstruction",
        "status": "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED",
        "object": "D20",
        "definition": {
            "packet_operator": "the certified full-exposure two-step packet action",
            "integer_bridge_obstruction": (
                "the Smith cokernel of the packet operator; any future raw-label bridge target "
                "must satisfy the block congruence tests before it can be an integral packet image"
            ),
        },
        "claim": (
            "The certified 20-packet operator has exact Smith factors 2^10 and 6^10. "
            "Equivalently, each packet doublet has cokernel Z/2 x Z/6, with image test "
            "u-v = 0 mod 2 and u+v = 0 mod 6. This supplies the integer obstruction "
            "template for the missing A985, tube, and q42/q12 packet bridges, but does not "
            "construct those raw bridges."
        ),
        "inputs": {
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
            "d20_full_packet_matrix_lift_report": input_record(D20_FULL_PACKET_MATRIX_LIFT),
            "d20_explicit_packet_restriction_map_test_report": input_record(
                D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST
            ),
        },
        "derived": {
            "obstruction_summary": obstruction_summary,
            "packet_operator_matrix": packet_operator,
            "packet_operator_matrix_sha256": sha_json(packet_operator),
            "smith_normal_form": {
                "diagonal": snf["diagonal"],
                "diagonal_multiplicities": snf["diagonal_multiplicities"],
                "nonunit_invariant_factors": nonunit,
                "off_diagonal_nonzero": snf["off_diagonal_nonzero"],
                "divisibility_chain_valid": snf["divisibility_chain_valid"],
                "reduction_steps": snf["reduction_steps"],
            },
            "packet_image_congruence_rows": congruence_rows,
            "packet_image_congruence_rows_sha256": sha_json(congruence_rows),
            "raw_bridge_snf_tasks": bridge_tasks,
            "raw_bridge_snf_tasks_sha256": sha_json(bridge_tasks),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "finite_boundary_reading": (
                "The packet action is an integral finite quotient with only 2- and 3-primary "
                "torsion in its cokernel."
            ),
            "denominator_reading": (
                "The plus/minus packet projectors still require denominator 2, while the integral "
                "action itself has Smith factors 2 and 6 per doublet."
            ),
            "not_claimed": (
                "This is not a raw A985 action, not a tube action, and not a theorem about rational "
                "prime distribution."
            ),
        },
        "next_highest_yield_item": (
            "Populate one raw bridge column set, then reduce its packet targets against the block "
            "tests u-v = 0 mod 2 and u+v = 0 mod 6."
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
        "schema": "d20.theorem.d20_packet_bridge_snf_obstruction_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "compute the exact Smith factors of the certified 20-packet operator",
            "turn the missing raw packet bridges into explicit integral congruence tests",
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
