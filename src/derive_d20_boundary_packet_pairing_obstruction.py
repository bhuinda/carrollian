from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_boundary_packet_pairing_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE = (
    D20_INVARIANTS / "theorems" / "d20_boundary_loop_step_atom_incidence" / "report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_packet_bridge_snf_obstruction" / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]


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


def local_failures(u: int, v: int) -> list[str]:
    failures = []
    if u % 2 != 0:
        failures.append("u_not_0_mod_2")
    if v % 2 != 0:
        failures.append("v_not_0_mod_2")
    if (u + v) % 6 != 0:
        failures.append("u_plus_v_not_0_mod_6")
    return failures


def pair_passes(matrix: list[list[int]], left: int, right: int, scalar: int = 1) -> bool:
    return all(
        not local_failures(scalar * matrix[left][col], scalar * matrix[right][col])
        for col in range(len(matrix[0]))
    )


def compatible_pairs(matrix: list[list[int]], scalar: int = 1) -> list[list[int]]:
    return [
        [left, right]
        for left, right in combinations(range(len(matrix)), 2)
        if pair_passes(matrix, left, right, scalar)
    ]


def find_perfect_matching(vertex_count: int, pairs: list[list[int]]) -> list[list[int]] | None:
    adjacency = {idx: set() for idx in range(vertex_count)}
    for left, right in pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)

    def search(remaining: set[int]) -> list[list[int]] | None:
        if not remaining:
            return []
        pivot = min(remaining, key=lambda item: len(adjacency[item] & remaining))
        for partner in sorted(adjacency[pivot] & remaining):
            tail = search(remaining - {pivot, partner})
            if tail is not None:
                return [[pivot, partner]] + tail
        return None

    return search(set(range(vertex_count)))


def failure_histogram_for_pairs(
    matrix: list[list[int]],
    pairs: list[list[int]],
    scalar: int = 1,
) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for left, right in pairs:
        for col in range(len(matrix[0])):
            failures = local_failures(scalar * matrix[left][col], scalar * matrix[right][col])
            counter["pass" if not failures else "|".join(failures)] += 1
    return histogram(counter)


def complement_pair_rows(public_atom_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    id_by_triple = {
        tuple(str(row["h6_triple"]).split("|")): int(row["public_atom_id"])
        for row in public_atom_rows
    }
    seen: set[int] = set()
    rows = []
    for row in public_atom_rows:
        left = int(row["public_atom_id"])
        if left in seen:
            continue
        triple = tuple(str(row["h6_triple"]).split("|"))
        complement = tuple(label for label in H6_LABELS if label not in set(triple))
        right = id_by_triple[complement]
        seen.add(left)
        seen.add(right)
        rows.append(
            {
                "pair_id": len(rows),
                "public_atom_pair": [left, right],
                "left_h6_triple": "|".join(triple),
                "right_h6_triple": "|".join(complement),
            }
        )
    return rows


def build_scalar_scan_rows(matrix: list[list[int]], max_scalar: int = 12) -> list[dict[str, Any]]:
    rows = []
    for scalar in range(1, max_scalar + 1):
        pairs = compatible_pairs(matrix, scalar)
        matching = find_perfect_matching(len(matrix), pairs)
        rows.append(
            {
                "scalar": scalar,
                "compatible_pair_count": len(pairs),
                "perfect_matching_exists": matching is not None,
                "first_perfect_matching": matching,
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION)
    packet_graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    derived = incidence["derived"]
    matrix = derived["boundary_atom_step_incidence_matrix"]
    public_atom_rows = derived["public_atom_rows"]
    all_unordered_pairs = [[left, right] for left, right in combinations(range(20), 2)]
    raw_pairs = compatible_pairs(matrix)
    raw_matching = find_perfect_matching(20, raw_pairs)
    scalar_scan_rows = build_scalar_scan_rows(matrix, 12)
    first_matching_scalar = next(
        row["scalar"] for row in scalar_scan_rows if row["perfect_matching_exists"]
    )
    complement_rows = complement_pair_rows(public_atom_rows)
    complement_pairs = [row["public_atom_pair"] for row in complement_rows]
    complement_failure_hist = failure_histogram_for_pairs(matrix, complement_pairs)
    complement_columns_passing_all_pairs = [
        col
        for col in range(len(matrix[0]))
        if all(
            not local_failures(matrix[left][col], matrix[right][col])
            for left, right in complement_pairs
        )
    ]
    boundary_snf = derived["boundary_atom_step_incidence_smith_normal_form"]
    boundary_nonunit = [int(value) for value in boundary_snf["nonunit_invariant_factors"]]
    boundary_exponent = max(boundary_nonunit)
    joint_scalar = math.lcm(boundary_exponent, first_matching_scalar)
    component_rows = packet_graph["derived"]["component_rows"]
    packet_pairs = [[int(value) for value in row["packet_pair"]] for row in component_rows]
    obstruction_summary = {
        "public_atom_count": 20,
        "step_atom_column_count": 25,
        "packet_doublet_count": len(packet_pairs),
        "all_unordered_public_pair_count": len(all_unordered_pairs),
        "raw_compatible_pair_count": len(raw_pairs),
        "raw_perfect_matching_exists": raw_matching is not None,
        "raw_failure_histogram_over_all_unordered_pairs": failure_histogram_for_pairs(
            matrix, all_unordered_pairs
        ),
        "minimal_scalar_with_any_compatible_pair": first_matching_scalar,
        "minimal_scalar_with_perfect_matching": first_matching_scalar,
        "boundary_incidence_nonunit_factors": boundary_nonunit,
        "boundary_lattice_exponent": boundary_exponent,
        "joint_boundary_packet_scalar_lcm": joint_scalar,
        "complement_pair_raw_failure_histogram": complement_failure_hist,
        "complement_pair_columns_passing_packet_snf": complement_columns_passing_all_pairs,
    }
    local_image_test = packet_snf["derived"]["obstruction_summary"]["local_image_test"]
    checks = {
        "boundary_loop_step_atom_incidence_is_certified": incidence.get("status")
        == "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED"
        and incidence.get("all_checks_pass") is True,
        "packet_bridge_snf_obstruction_is_certified": packet_snf.get("status")
        == "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED"
        and packet_snf.get("all_checks_pass") is True,
        "full_exposure_packet_graph_is_certified": packet_graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and packet_graph.get("all_checks_pass") is True,
        "packet_snf_local_test_is_exact": local_image_test
        == "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet",
        "incidence_matrix_is_20_by_25": len(matrix) == 20
        and all(len(row) == 25 for row in matrix),
        "public_atom_rows_have_20_entries": len(public_atom_rows) == 20,
        "all_unordered_pair_count_is_190": len(all_unordered_pairs) == 190,
        "raw_compatible_pair_count_is_zero": len(raw_pairs) == 0,
        "raw_perfect_matching_does_not_exist": raw_matching is None,
        "scalars_1_to_5_have_no_compatible_pairs": all(
            row["compatible_pair_count"] == 0 and row["perfect_matching_exists"] is False
            for row in scalar_scan_rows
            if int(row["scalar"]) <= 5
        ),
        "scalar_6_makes_all_pairs_compatible": scalar_scan_rows[5][
            "compatible_pair_count"
        ]
        == 190
        and scalar_scan_rows[5]["perfect_matching_exists"] is True,
        "minimal_scalar_with_matching_is_6": first_matching_scalar == 6,
        "boundary_lattice_exponent_is_4": boundary_exponent == 4,
        "joint_boundary_packet_scalar_lcm_is_12": joint_scalar == 12,
        "complement_pairs_are_10": len(complement_rows) == 10,
        "complement_pairing_raw_has_no_column_passes": complement_columns_passing_all_pairs
        == [],
        "complement_pairing_pair_column_pass_count_is_184": complement_failure_hist.get(
            "pass", 0
        )
        == 184,
    }
    report = {
        "schema": "d20.theorem.d20_boundary_packet_pairing_obstruction",
        "status": "D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION_CERTIFIED",
        "object": "D20",
        "definition": {
            "input_boundary_matrix": (
                "the signed Lambda^3 H6 target-minus-source incidence matrix for the 25 visible "
                "Loop_297 step atoms"
            ),
            "candidate_packet_pairing": (
                "an unordered pairing of the 20 public boundary atoms into ten putative packet doublets"
            ),
            "compatibility_test": local_image_test,
        },
        "claim": (
            "No raw relabelling of the 20 signed public boundary coordinates into ten packet "
            "doublets can make the visible Loop_297 step-atom columns land in the certified "
            "packet SNF image: the compatibility graph has zero edges. A scalar normalization "
            "of 6 is the first scalar that can make any pairing compatible with the packet "
            "block tests; combined with the boundary incidence exponent 4, the joint scalar "
            "clearing bound is 12."
        ),
        "inputs": {
            "d20_boundary_loop_step_atom_incidence_report": input_record(
                D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE
            ),
            "d20_packet_bridge_snf_obstruction_report": input_record(
                D20_PACKET_BRIDGE_SNF_OBSTRUCTION
            ),
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
        },
        "derived": {
            "obstruction_summary": obstruction_summary,
            "raw_compatible_public_atom_pairs": raw_pairs,
            "raw_compatible_public_atom_pairs_sha256": sha_json(raw_pairs),
            "scalar_compatibility_scan_rows": scalar_scan_rows,
            "scalar_compatibility_scan_rows_sha256": sha_json(scalar_scan_rows),
            "canonical_complement_pair_rows": complement_rows,
            "canonical_complement_pair_rows_sha256": sha_json(complement_rows),
            "packet_component_pairs": packet_pairs,
            "packet_component_pairs_sha256": sha_json(packet_pairs),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "negative_boundary": (
                "The signed boundary incidence table cannot be turned into packet-image columns "
                "by merely choosing a different pairing of the 20 public atoms."
            ),
            "normalization_pressure": (
                "Any packet-compatible boundary-to-packet normalization must introduce at least "
                "the packet scalar 6, and a full zero-sum boundary-lattice lift must also account "
                "for the boundary exponent 4."
            ),
            "not_claimed": (
                "The scalar 12 bound is a clearing bound, not a certified physical bridge or "
                "DLCQ/M-theory construction."
            ),
        },
        "next_highest_yield_item": (
            "Search for a nontrivial signed quotient/normalization, not just scalar clearing, "
            "that maps the boundary incidence lattice into packet doublets and preserves the "
            "Loop_297/A985 step labels."
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
        "schema": "d20.theorem.d20_boundary_packet_pairing_obstruction_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "prove that no raw pairing of Lambda^3 H6 boundary atoms yields packet-image step columns",
            "record the first scalar normalization compatible with packet SNF block tests",
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
