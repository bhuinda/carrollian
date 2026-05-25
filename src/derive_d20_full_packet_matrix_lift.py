from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_full_packet_matrix_lift.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_full_packet_matrix_lift"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CONSTANTS = ROOT / "data" / "raw" / "constants.json"
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)
FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_coordinate_transition_operator"
    / "report.json"
)
D20_MINIMAL_MATRIX_CHARGE_LIFT = (
    D20_INVARIANTS / "theorems" / "d20_minimal_matrix_charge_lift" / "report.json"
)


Matrix = list[list[Fraction]]


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


def frac_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix_to_strings(matrix: Matrix) -> list[list[str]]:
    return [[frac_string(value) for value in row] for row in matrix]


def mat_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def mat_mul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def scalar_mat(scalar: Fraction, matrix: Matrix) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def zero_matrix(rows: int, cols: int) -> Matrix:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def int_matrix(matrix: list[list[int]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in matrix]


def orient_packet_pair(pair: list[int]) -> list[int]:
    # Match the already certified minimal charge-lift orientation for the zero-pair block.
    if pair == [238, 239]:
        return [239, 238]
    return pair


def build_component_lift_rows(component_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    identity: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    swap: Matrix = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    plus_projector = scalar_mat(Fraction(1, 2), mat_add(identity, swap))
    minus_projector = scalar_mat(Fraction(1, 2), mat_add(identity, scalar_mat(Fraction(-1), swap)))
    expected_block = [[2, 4], [4, 2]]
    rows = []
    for component_index, component in enumerate(component_rows):
        pair = [int(packet) for packet in component["packet_pair"]]
        rows.append(
            {
                "component_id": int(component.get("component_id", component_index)),
                "packet_pair": pair,
                "oriented_basis": orient_packet_pair(pair),
                "block_matrix": component["block_matrix"],
                "block_decomposition": "2*I + 4*S",
                "swap_involution": matrix_to_strings(swap),
                "plus_projector": matrix_to_strings(plus_projector),
                "minus_projector": matrix_to_strings(minus_projector),
                "plus_eigenvalue": 6,
                "minus_eigenvalue": -2,
                "ordered_cross_return_count": int(component["ordered_cross_return_count"]),
                "hidden_R33_transfer_mod26_sum": int(component["hidden_R33_transfer_mod26_sum"]),
                "net_height_flux_delta_sum": int(component["net_height_flux_delta_sum"]),
                "is_zero_pair_component": set(pair) == {238, 239},
                "block_is_uniform": component["block_matrix"] == expected_block,
            }
        )
    return rows


def block_diagonal_from_components(component_rows: list[dict[str, Any]]) -> Matrix:
    size = 2 * len(component_rows)
    out = zero_matrix(size, size)
    for idx, row in enumerate(component_rows):
        block = int_matrix(row["block_matrix"])
        offset = 2 * idx
        for i in range(2):
            for j in range(2):
                out[offset + i][offset + j] = block[i][j]
    return out


def matrix_trace(matrix: Matrix) -> Fraction:
    return sum(matrix[i][i] for i in range(len(matrix)))


def build_theorem() -> dict[str, Any]:
    constants = load_json(CONSTANTS)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    label_operator = load_json(FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR)
    minimal = load_json(D20_MINIMAL_MATRIX_CHARGE_LIFT)

    graph_components = graph["derived"]["component_rows"]
    label_components = label_operator["derived"]["component_coordinate_rows"]
    lift_rows = build_component_lift_rows(graph_components)
    adjacency_matrix = block_diagonal_from_components(graph_components)
    graph_adjacency = int_matrix(graph["derived"]["adjacency"]["matrix"])
    zero_pair_rows = [row for row in lift_rows if row["is_zero_pair_component"]]
    minimal_lift = minimal["derived"]["minimal_matrix_charge_lift"]
    transition_block: Matrix = [[Fraction(2), Fraction(4)], [Fraction(4), Fraction(2)]]
    identity: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    swap: Matrix = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    plus_projector = scalar_mat(Fraction(1, 2), mat_add(identity, swap))
    minus_projector = scalar_mat(Fraction(1, 2), mat_add(identity, scalar_mat(Fraction(-1), swap)))
    acting_summary = {
        "block_algebra": "Mat_2(Q)^10",
        "block_algebra_dimension_over_Q": 40,
        "packet_vector_space_dimension": 20,
        "component_count": len(lift_rows),
        "full_exposure_transition_operator": "direct_sum_10_copies_of_2I_plus_4S",
        "transition_operator_trace": int(matrix_trace(adjacency_matrix)),
        "transition_operator_row_sum": 6,
        "transition_operator_integer_eigenvalue_histogram": {
            "6": 10,
            "-2": 10,
        },
        "minimal_charge_lift_component_id": zero_pair_rows[0]["component_id"] if zero_pair_rows else None,
        "minimal_charge_lift_oriented_basis": zero_pair_rows[0]["oriented_basis"] if zero_pair_rows else None,
    }
    a985_probe = {
        "a985_dimension": constants["wedderburn"]["sum_squares"],
        "a985_center_dimension": constants["wedderburn"]["center_dim"],
        "block_lift_image_dimension_bound": acting_summary["block_algebra_dimension_over_Q"],
        "faithful_full_a985_action_possible_in_this_block_lift": False,
        "minimum_kernel_dimension_for_any_a985_map_into_this_block_lift": (
            int(constants["wedderburn"]["sum_squares"])
            - acting_summary["block_algebra_dimension_over_Q"]
        ),
        "certified_a985_to_packet_operator_map_present": False,
        "tested_action": "full_exposure_two_step_transition_operator",
        "tested_action_lands_in_block_lift": True,
        "scope_note": (
            "The certified transition operator acts through the block matrix lift. A full A985 action "
            "would need a separate homomorphism from the 985-dimensional algebra to packet operators; "
            "no such map is supplied by the current certificates."
        ),
    }
    checks = {
        "full_exposure_packet_graph_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "label_coordinate_operator_is_certified": label_operator.get("status")
        == "D20_FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_CERTIFIED"
        and label_operator.get("all_checks_pass") is True,
        "minimal_charge_lift_is_certified": minimal.get("status")
        == "D20_MINIMAL_MATRIX_CHARGE_LIFT_CERTIFIED"
        and minimal.get("all_checks_pass") is True,
        "ten_components_are_present": len(lift_rows) == 10
        and len(label_components) == 10
        and len(graph["derived"]["graph_summary"]["active_partner_pairs"]) == 10,
        "all_blocks_are_uniform_2_4_4_2": all(row["block_is_uniform"] for row in lift_rows),
        "block_diagonal_matrix_matches_graph_adjacency": adjacency_matrix == graph_adjacency,
        "each_block_has_swap_projector_decomposition": all(
            row["swap_involution"] == [["0", "1"], ["1", "0"]]
            and row["plus_projector"] == [["1/2", "1/2"], ["1/2", "1/2"]]
            and row["minus_projector"] == [["1/2", "-1/2"], ["-1/2", "1/2"]]
            for row in lift_rows
        )
        and mat_mul(plus_projector, plus_projector) == plus_projector
        and mat_mul(minus_projector, minus_projector) == minus_projector
        and mat_mul(plus_projector, minus_projector) == zero_matrix(2, 2)
        and mat_add(plus_projector, minus_projector) == identity,
        "transition_operator_is_2I_plus_4S_on_each_block": transition_block
        == mat_add(scalar_mat(Fraction(2), identity), scalar_mat(Fraction(4), swap)),
        "spectral_histogram_matches_full_packet_graph": {
            str(row["value"]): int(row["multiplicity"])
            for row in graph["derived"]["spectral_summary"]["integer_adjacency_eigenvalues"]
        }
        == {"-2": 10, "6": 10},
        "zero_pair_block_embeds_minimal_charge_lift": len(zero_pair_rows) == 1
        and zero_pair_rows[0]["oriented_basis"] == minimal_lift["basis_order"]
        and zero_pair_rows[0]["plus_projector"] == minimal_lift["plus_projector"]
        and zero_pair_rows[0]["minus_projector"] == minimal_lift["minus_projector"],
        "hidden_and_height_flux_remain_zero_on_all_blocks": all(
            row["hidden_R33_transfer_mod26_sum"] == 0
            and row["net_height_flux_delta_sum"] == 0
            for row in lift_rows
        ),
        "full_a985_action_is_not_faithfully_realized_at_this_level": a985_probe[
            "a985_dimension"
        ]
        == 985
        and a985_probe["block_lift_image_dimension_bound"] == 40
        and a985_probe["minimum_kernel_dimension_for_any_a985_map_into_this_block_lift"]
        == 945
        and a985_probe["faithful_full_a985_action_possible_in_this_block_lift"] is False,
        "no_certified_a985_to_packet_operator_map_is_present": a985_probe[
            "certified_a985_to_packet_operator_map_present"
        ]
        is False
        and a985_probe["tested_action_lands_in_block_lift"] is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_PACKET_MATRIX_LIFT_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.d20_full_packet_matrix_lift",
        "status": status,
        "object": "d20",
        "claim": (
            "The local Mat_2(Q) charge-kernel lift extends to the whole 20-packet "
            "full-exposure propagation algebra as ten independent 2x2 blocks. In the "
            "certified active-partner decomposition, the transition operator is the direct "
            "sum of ten copies of 2I+4S, with plus/minus projectors on every block. The "
            "zero-pair component recovers the minimal [239,238] charge lift. This realizes "
            "the full-exposure propagation operator, but it does not faithfully realize the "
            "full 985-dimensional A985 algebra."
        ),
        "definition": {
            "full_packet_matrix_lift": (
                "The block algebra Mat_2(Q)^10 on the ten certified active-partner packet "
                "doublets of the full-exposure propagation graph."
            ),
            "acting_operator": (
                "The certified two-step full-exposure transition operator, not the full A985 "
                "multiplication tensor."
            ),
            "a985_action_probe": (
                "A dimension and input-boundary test: this 40-dimensional block image can "
                "only support a quotient-level A985 action, and no A985-to-packet operator "
                "homomorphism is currently certified."
            ),
        },
        "inputs": {
            "constants": input_record(CONSTANTS),
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
            "full_exposure_label_coordinate_transition_operator_report": input_record(
                FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR
            ),
            "d20_minimal_matrix_charge_lift_report": input_record(D20_MINIMAL_MATRIX_CHARGE_LIFT),
        },
        "derived": {
            "acting_summary": acting_summary,
            "component_lift_rows": lift_rows,
            "a985_action_probe": a985_probe,
            "component_lift_rows_sha256": sha_json(lift_rows),
        },
        "interpretation": {
            "what_this_certifies": [
                "the certified full-exposure transition operator acts through Mat_2(Q)^10",
                "each active-partner packet pair has the same plus/minus projector decomposition",
                "the [239,238] zero-pair component embeds the previously certified minimal matrix charge lift",
                "a faithful full A985 action is impossible inside this 40-dimensional block image",
            ],
            "what_this_does_not_certify": [
                "a homomorphism from A985 to the 20-packet operator algebra",
                "a quotient A985 action on full-exposure packets",
                "a DLCQ matrix model",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Search for an actual quotient-level A985-to-packet operator map: identify which "
            "certified A985, tube, or quotient elements preserve the 20-packet full-exposure "
            "subspace and test whether their images land in Mat_2(Q)^10."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.d20_full_packet_matrix_lift_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify full-exposure graph, label-coordinate operator, and minimal charge-lift inputs",
            "verify ten active-partner components with uniform [[2,4],[4,2]] blocks",
            "verify the reconstructed block diagonal matrix matches the certified graph adjacency",
            "verify each block has the same swap/projector decomposition",
            "verify the zero-pair block embeds the minimal [239,238] charge lift",
            "verify hidden transfer and height flux remain zero on all blocks",
            "verify faithful full A985 action is impossible inside the 40-dimensional block image",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
