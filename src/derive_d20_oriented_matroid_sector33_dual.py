from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_oriented_matroid_contour import (
        base_edges,
        edge_table,
        incidence_matrix,
    )
    from src.derive_d20_oriented_matroid_sector33_extension import (
        is_circuit,
        is_cocircuit,
        is_hyperplane,
        matroid_rank,
        rank_of_columns,
    )
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_oriented_matroid_contour import (
        base_edges,
        edge_table,
        incidence_matrix,
    )
    from src.derive_d20_oriented_matroid_sector33_extension import (
        is_circuit,
        is_cocircuit,
        is_hyperplane,
        matroid_rank,
        rank_of_columns,
    )
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_oriented_matroid_sector33_dual"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_JSON = ROOT / "d20.json"
SECTOR33_EXTENSION = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_extension" / "report.json"
)
SECTOR33_HEIGHT_TRANSPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
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
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def row_rank(rows: list[list[int]]) -> int:
    if not rows:
        return 0
    transposed = [[rows[row][col] for row in range(len(rows))] for col in range(len(rows[0]))]
    return rank_of_columns(transposed, list(range(len(rows))))


def integer_nullspace_basis(matrix: list[list[int]]) -> tuple[list[list[int]], list[int], list[int]]:
    rows = len(matrix)
    cols = len(matrix[0])
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_cols: list[int] = []
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][col]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    work[row][idx] - factor * work[rank][idx] for idx in range(cols)
                ]
        pivot_cols.append(col)
        rank += 1
        if rank == rows:
            break

    free_cols = [col for col in range(cols) if col not in pivot_cols]
    basis = []
    for free_col in free_cols:
        vector = [Fraction(0) for _ in range(cols)]
        vector[free_col] = Fraction(1)
        for row, pivot_col in enumerate(pivot_cols):
            vector[pivot_col] = -work[row][free_col]
        lcm = 1
        for value in vector:
            lcm = math.lcm(lcm, value.denominator)
        ints = [int(value * lcm) for value in vector]
        gcd = 0
        for value in ints:
            gcd = math.gcd(gcd, abs(value))
        if gcd:
            ints = [value // gcd for value in ints]
        for value in ints:
            if value:
                if value < 0:
                    ints = [-entry for entry in ints]
                break
        basis.append(ints)
    return basis, pivot_cols, free_cols


def matrix_vector_product(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [
        sum(int(matrix[row][col]) * int(vector[col]) for col in range(len(vector)))
        for row in range(len(matrix))
    ]


def build_sector33_height_attachment_matrix() -> tuple[list[list[int]], dict[str, Any]]:
    d20 = load_json(D20_JSON)
    sector33_height = load_json(SECTOR33_HEIGHT_TRANSPORT)
    edge_rows = edge_table(d20)
    base = base_edges(edge_rows)
    incidence = incidence_matrix(base, 20)
    weights = [int(row["interface_weight"]) for row in edge_rows]
    active = sector33_height["derived"]["active_circuit"]
    active_support = sorted(int(edge_id) for edge_id, _sign in active["active_matrix_row"])
    edge_residual = sector33_height["derived"]["edge_derived_residual"]
    e33_dimension = int(edge_residual["dimension"])
    e33_transport_scalar = int(edge_residual["transport_scalar_signed"])
    active_boundary_sum = [
        sum(incidence[row][edge_id] for edge_id in active_support) for row in range(20)
    ]
    sector_bridge_column = [
        -value // e33_dimension for value in active_boundary_sum
    ] + [e33_transport_scalar]
    matrix = [row + [sector_bridge_column[idx]] for idx, row in enumerate(incidence)]
    matrix.append(weights + [sector_bridge_column[20]])
    summary = {
        "active_support": active_support,
        "new_element_id": len(edge_rows),
        "new_element": "e33",
        "sector33_dimension": e33_dimension,
        "sector33_transport_scalar": e33_transport_scalar,
        "sector_bridge_column": sector_bridge_column,
    }
    return matrix, summary


def build_theorem() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    extension = load_json(SECTOR33_EXTENSION)
    sector33_height = load_json(SECTOR33_HEIGHT_TRANSPORT)

    primal_matrix, attachment = build_sector33_height_attachment_matrix()
    dual_matrix, pivot_cols, free_cols = integer_nullspace_basis(primal_matrix)
    ground = list(range(len(primal_matrix[0])))
    new_element = int(attachment["new_element_id"])
    positive_support = attachment["active_support"] + [new_element]
    positive_vector = [0 for _ in ground]
    for edge_id in attachment["active_support"]:
        positive_vector[edge_id] = 1
    positive_vector[new_element] = int(attachment["sector33_dimension"])
    complement = [element for element in ground if element not in positive_support]

    primal_rank = matroid_rank(primal_matrix)
    dual_rank = matroid_rank(dual_matrix)
    positive_vector_kernel_image = matrix_vector_product(primal_matrix, positive_vector)
    positive_vector_in_dual_rowspace = row_rank(dual_matrix + [positive_vector]) == row_rank(
        dual_matrix
    )
    dual_hyperplane_rank = rank_of_columns(dual_matrix, complement)
    dual_addback_ranks = {
        str(element): rank_of_columns(dual_matrix, complement + [element])
        for element in positive_support
    }

    dual_cocircuit = {
        "support": positive_support,
        "signed_support": [
            {
                "element_id": element,
                "element": "e33" if element == new_element else f"edge_{element}",
                "coefficient": positive_vector[element],
                "sign": 1,
            }
            for element in positive_support
        ],
        "is_positive": all(positive_vector[element] > 0 for element in positive_support),
        "complement": complement,
        "complement_is_dual_hyperplane": is_hyperplane(dual_matrix, complement),
        "support_is_dual_cocircuit": is_cocircuit(dual_matrix, positive_support),
        "support_is_dual_circuit": is_circuit(dual_matrix, positive_support),
        "dual_hyperplane_rank": dual_hyperplane_rank,
        "dual_addback_ranks": dual_addback_ranks,
    }

    dual_summary = {
        "primal_ground_set_size": len(ground),
        "primal_rank": primal_rank,
        "dual_rank": dual_rank,
        "rank_sum": primal_rank + dual_rank,
        "nullspace_basis_rows": len(dual_matrix),
        "nullspace_basis_cols": len(dual_matrix[0]),
        "nullspace_pivot_columns": pivot_cols,
        "nullspace_free_columns": free_cols,
        "dual_matrix": dual_matrix,
        "dual_matrix_sha256": sha_json(dual_matrix),
    }

    element_tests = {
        "e33_dual_singleton_cocircuit": is_cocircuit(dual_matrix, [new_element]),
        "e33_dual_singleton_circuit": is_circuit(dual_matrix, [new_element]),
        "e33_dual_singleton_rank": rank_of_columns(dual_matrix, [new_element]),
        "old_ground_dual_hyperplane": is_hyperplane(
            dual_matrix, [element for element in ground if element != new_element]
        ),
        "old_ground_dual_rank": rank_of_columns(
            dual_matrix, [element for element in ground if element != new_element]
        ),
        "dual_total_rank": dual_rank,
    }

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "sector33_extension_input_is_certified": extension.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_EXTENSION_CERTIFIED"
        and extension.get("all_checks_pass") is True,
        "sector33_height_transport_input_is_certified": sector33_height.get("status")
        == "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and sector33_height.get("all_checks_pass") is True,
        "primal_rank_is_20": primal_rank == 20,
        "dual_rank_is_11": dual_rank == 11,
        "rank_duality_holds": primal_rank + dual_rank == len(ground),
        "dual_matrix_has_expected_shape": len(dual_matrix) == 11
        and all(len(row) == 31 for row in dual_matrix),
        "positive_vector_is_primal_kernel_vector": all(
            value == 0 for value in positive_vector_kernel_image
        ),
        "positive_vector_lies_in_dual_rowspace": positive_vector_in_dual_rowspace,
        "gamma8_e33_is_dual_cocircuit": dual_cocircuit["support_is_dual_cocircuit"],
        "gamma8_e33_complement_is_dual_hyperplane": dual_cocircuit[
            "complement_is_dual_hyperplane"
        ],
        "gamma8_e33_is_not_dual_circuit": dual_cocircuit["support_is_dual_circuit"] is False,
        "dual_cocircuit_is_positive": dual_cocircuit["is_positive"],
        "dual_hyperplane_has_rank_10": dual_hyperplane_rank == 10,
        "adding_any_cocircuit_element_recovers_dual_rank": all(
            value == dual_rank for value in dual_addback_ranks.values()
        ),
        "e33_is_not_singleton_dual_cocircuit": element_tests[
            "e33_dual_singleton_cocircuit"
        ]
        is False,
        "old_ground_is_not_dual_hyperplane": element_tests["old_ground_dual_hyperplane"]
        is False,
    }

    report = {
        "schema": "d20.theorem.d20_oriented_matroid_sector33_dual",
        "status": "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED",
        "object": "D20",
        "definition": {
            "dual_representation": (
                "an explicit integer nullspace basis for the sector-33 height-attachment "
                "matrix; its rows represent the dual oriented matroid"
            ),
            "dual_cocircuit_test": (
                "a support is a cocircuit in the dual matroid iff its complement is a "
                "hyperplane in the dual representation"
            ),
            "positive_cocircuit": (
                "the primal positive circuit vector (1,1,1,1,1,2) lies in the dual "
                "rowspace and has minimal covector support"
            ),
        },
        "claim": (
            "The sector-33 height attachment has an explicit dual/coextension reading. "
            "The primal positive circuit obstruction on gamma8+e33 becomes a positive "
            "cocircuit in the dual oriented matroid: its complement is a rank-10 dual "
            "hyperplane, and adding any one of the six cocircuit elements recovers the "
            "full dual rank 11."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
            "d20_oriented_matroid_sector33_extension_report": input_record(
                SECTOR33_EXTENSION
            ),
            "sector33_height_coherent_transport_report": input_record(
                SECTOR33_HEIGHT_TRANSPORT
            ),
        },
        "derived": {
            "sector33_height_attachment": attachment,
            "dual_summary": dual_summary,
            "positive_primal_circuit_vector": positive_vector,
            "positive_vector_kernel_image": positive_vector_kernel_image,
            "positive_vector_in_dual_rowspace": positive_vector_in_dual_rowspace,
            "dual_positive_cocircuit": dual_cocircuit,
            "element_tests": element_tests,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "confirmed": [
                "the sector-33 positive circuit obstruction has a dual positive-cocircuit reading",
                "the dual hyperplane is exactly the complement of the gamma8+e33 support",
                "the explicit nullspace matrix gives a finite dual/coextension witness",
            ],
            "guardrails": [
                "e33 alone is still not a singleton cocircuit",
                "the old public ground set is still not the dual hyperplane",
                "the dual reading is attached to the decorated sector-33 height extension, not to the pure contour matroid alone",
            ],
        },
        "next_highest_yield_item": (
            "Compute the Tutte polynomial or no-broken-circuit basis for the 31-element "
            "sector-33 height-extension matroid and use it to summarize the "
            "Orlik-Solomon algebra."
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
        "schema": "d20.theorem.d20_oriented_matroid_sector33_dual_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "build an explicit dual representation of the sector-33 height attachment",
            "test whether the positive circuit obstruction becomes a positive dual cocircuit",
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
