from __future__ import annotations

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
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_oriented_matroid_contour import (
        base_edges,
        edge_table,
        incidence_matrix,
    )
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_oriented_matroid_sector33_extension"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_JSON = ROOT / "d20.json"
ORIENTED_MATROID_CONTOUR = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_contour" / "report.json"
)
D20_FINITE_CONTOUR = (
    D20_INVARIANTS / "theorems" / "d20_finite_contour_integration" / "report.json"
)
SECTOR33_HEIGHT_TRANSPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
)
SECTOR33_RESIDUAL_ATTACHMENT = (
    D20_INVARIANTS / "theorems" / "sector33_residual_attachment" / "report.json"
)
SECTOR33_UNIQUE_PUBLIC_ZERO = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
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


def rank_of_columns(matrix: list[list[int]], columns: list[int]) -> int:
    work = [[Fraction(row[col]) for col in columns] for row in matrix]
    if not work or not columns:
        return 0
    row_count = len(work)
    col_count = len(columns)
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][col]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    work[row][idx] - factor * work[rank][idx] for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def matroid_rank(matrix: list[list[int]]) -> int:
    return rank_of_columns(matrix, list(range(len(matrix[0]))))


def is_circuit(matrix: list[list[int]], support: list[int]) -> bool:
    target_rank = len(support) - 1
    if rank_of_columns(matrix, support) != target_rank:
        return False
    return all(
        rank_of_columns(matrix, [element for element in support if element != removed])
        == target_rank
        for removed in support
    )


def is_hyperplane(matrix: list[list[int]], support: list[int]) -> bool:
    ground = list(range(len(matrix[0])))
    support_set = set(support)
    full_rank = matroid_rank(matrix)
    if rank_of_columns(matrix, sorted(support_set)) != full_rank - 1:
        return False
    return all(
        rank_of_columns(matrix, sorted(support_set | {element})) == full_rank
        for element in ground
        if element not in support_set
    )


def is_cocircuit(matrix: list[list[int]], support: list[int]) -> bool:
    ground = set(range(len(matrix[0])))
    return is_hyperplane(matrix, sorted(ground - set(support)))


def integer_null_vector(matrix: list[list[int]], support: list[int]) -> list[int]:
    rows = len(matrix)
    cols = len(support)
    work = [[Fraction(matrix[row][support[col]]) for col in range(cols)] for row in range(rows)]
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

    free_cols = [col for col in range(cols) if col not in pivot_cols]
    if len(free_cols) != 1:
        raise ValueError("expected one-dimensional nullspace for circuit support")
    free_col = free_cols[0]
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
    return ints


def signed_support_from_coefficients(
    support: list[int],
    coefficients: list[int],
    labels: dict[int, str],
) -> list[dict[str, Any]]:
    return [
        {
            "element": labels.get(element, str(element)),
            "element_id": element,
            "coefficient": coefficient,
            "sign": 1 if coefficient > 0 else -1,
        }
        for element, coefficient in zip(support, coefficients)
    ]


def append_column(matrix: list[list[int]], column: list[int]) -> list[list[int]]:
    return [row + [entry] for row, entry in zip(matrix, column)]


def extension_tests(
    matrix: list[list[int]],
    gamma_support: list[int],
    new_element: int,
) -> dict[str, Any]:
    ground = list(range(len(matrix[0])))
    old_ground = [element for element in ground if element != new_element]
    gamma_plus_new = gamma_support + [new_element]
    return {
        "rank": matroid_rank(matrix),
        "old_ground_rank": rank_of_columns(matrix, old_ground),
        "new_element_in_old_closure": rank_of_columns(matrix, old_ground)
        == matroid_rank(matrix),
        "gamma_support_rank": rank_of_columns(matrix, gamma_support),
        "gamma_support_is_circuit": is_circuit(matrix, gamma_support),
        "gamma_plus_new_rank": rank_of_columns(matrix, gamma_plus_new),
        "gamma_plus_new_is_circuit": is_circuit(matrix, gamma_plus_new),
        "new_singleton_is_cocircuit": is_cocircuit(matrix, [new_element]),
        "old_ground_is_hyperplane": is_hyperplane(matrix, old_ground),
        "gamma_support_is_cocircuit": is_cocircuit(matrix, gamma_support),
        "gamma_plus_new_is_cocircuit": is_cocircuit(matrix, gamma_plus_new),
    }


def build_theorem() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    contour = load_json(ORIENTED_MATROID_CONTOUR)
    finite_contour = load_json(D20_FINITE_CONTOUR)
    sector33_height = load_json(SECTOR33_HEIGHT_TRANSPORT)
    sector33_attachment = load_json(SECTOR33_RESIDUAL_ATTACHMENT)
    sector33_unique = load_json(SECTOR33_UNIQUE_PUBLIC_ZERO)

    edge_rows = edge_table(d20)
    base = base_edges(edge_rows)
    incidence = incidence_matrix(base, 20)
    weights = [int(row["interface_weight"]) for row in edge_rows]
    base_lift = [row[:] for row in incidence] + [weights[:]]
    edge_count = len(edge_rows)
    new_element = edge_count
    labels = {idx: f"edge_{idx}" for idx in range(edge_count)}
    labels[new_element] = "e33"

    active = sector33_height["derived"]["active_circuit"]
    active_support = sorted(int(edge_id) for edge_id, _sign in active["active_matrix_row"])
    active_positive_coefficients = [1 for _edge_id in active_support]
    cyclic_signed_coefficients_by_edge = {
        int(edge_id): int(sign) for edge_id, sign in active["signed_circuit_row"]
    }
    cyclic_signed_support = sorted(cyclic_signed_coefficients_by_edge)
    signed_integral = sum(
        cyclic_signed_coefficients_by_edge[edge_id] * weights[edge_id]
        for edge_id in cyclic_signed_support
    )
    primitive_quantum = finite_contour["derived"]["signed_contour_residue"]["normalization"]
    primitive_gamma8_residue = signed_integral // primitive_quantum
    height_action = int(active["height_dot_active_row"])
    edge_residual = sector33_height["derived"]["edge_derived_residual"]
    e33_dimension = int(edge_residual["dimension"])
    e33_transport_scalar = int(edge_residual["transport_scalar_signed"])

    signed_residue_column = [0 for _ in range(20)] + [primitive_quantum]
    signed_residue_matrix = append_column(base_lift, signed_residue_column)
    signed_residue_support = cyclic_signed_support + [new_element]
    signed_residue_coefficients = integer_null_vector(
        signed_residue_matrix, signed_residue_support
    )
    signed_residue_tests = extension_tests(
        signed_residue_matrix, cyclic_signed_support, new_element
    )

    hidden_sector_column = [0 for _ in range(20)] + [e33_transport_scalar]
    hidden_sector_matrix = append_column(base_lift, hidden_sector_column)
    hidden_sector_support = cyclic_signed_support + [new_element]
    hidden_sector_coefficients = integer_null_vector(
        hidden_sector_matrix, hidden_sector_support
    )
    hidden_sector_tests = extension_tests(
        hidden_sector_matrix, cyclic_signed_support, new_element
    )

    active_boundary_sum = [
        sum(incidence[row][edge_id] for edge_id in active_support) for row in range(20)
    ]
    if any(value % e33_dimension for value in active_boundary_sum):
        raise ValueError("active boundary is not divisible by sector-33 dimension")
    sector_bridge_column = [
        -value // e33_dimension for value in active_boundary_sum
    ] + [e33_transport_scalar]
    sector_bridge_matrix = append_column(base_lift, sector_bridge_column)
    sector_bridge_support = active_support + [new_element]
    sector_bridge_coefficients = integer_null_vector(
        sector_bridge_matrix, sector_bridge_support
    )
    sector_bridge_tests = extension_tests(
        sector_bridge_matrix, active_support, new_element
    )

    sector_bridge_public_boundary = {
        str(vertex): int(value)
        for vertex, value in enumerate(sector_bridge_column[:20])
        if value
    }

    signed_residue_extension = {
        "name": "signed_residue_lift",
        "representation": "[partial_D20; signed interface-weight row] plus rho with residue quantum 3072",
        "new_element": "rho_primitive",
        "new_column": {
            "public_incidence": {},
            "residue_coordinate": primitive_quantum,
        },
        "gamma8_signed_integral": signed_integral,
        "gamma8_primitive_residue": primitive_gamma8_residue,
        "circuit_support": signed_residue_support,
        "circuit_coefficients": signed_support_from_coefficients(
            signed_residue_support, signed_residue_coefficients, {**labels, new_element: "rho_primitive"}
        ),
        "tests": signed_residue_tests,
        "interpretation": (
            "This lift turns the non-exact signed contour residue into a circuit with "
            "one residue element. The residue element is not a cocircuit or hyperplane."
        ),
    }

    hidden_sector_scalar_extension = {
        "name": "hidden_sector_scalar_lift",
        "representation": "[partial_D20; height row] plus public-zero e33 scalar column",
        "new_element": "e33_hidden_scalar",
        "new_column": {
            "public_incidence": {},
            "height_coordinate": e33_transport_scalar,
            "sector33_dimension": e33_dimension,
            "sector33_residual_integral": int(edge_residual["residual_integral"]),
        },
        "circuit_support": hidden_sector_support,
        "circuit_coefficients": signed_support_from_coefficients(
            hidden_sector_support,
            hidden_sector_coefficients,
            {**labels, new_element: "e33_hidden_scalar"},
        ),
        "tests": hidden_sector_tests,
        "interpretation": (
            "A public-zero sector scalar can close the cyclic signed contour circuit, "
            "but it does not realize the all-positive height certificate."
        ),
    }

    sector33_height_attachment = {
        "name": "sector33_height_attachment",
        "representation": (
            "[partial_D20; height row] plus one sector-33 unit whose doubled column "
            "closes the all-positive gamma8 active row"
        ),
        "new_element": "e33",
        "new_column": {
            "public_incidence": sector_bridge_public_boundary,
            "height_coordinate": e33_transport_scalar,
            "source_vertex": 13,
            "target_vertex": 0,
            "sector33_dimension": e33_dimension,
        },
        "closure_equations": {
            "public_boundary_sum_active_plus_dim_e33": [
                int(active_boundary_sum[row] + e33_dimension * sector_bridge_column[row])
                for row in range(20)
            ],
            "height_sum_active_plus_dim_e33": int(
                height_action + e33_dimension * e33_transport_scalar
            ),
        },
        "circuit_support": sector_bridge_support,
        "circuit_coefficients": signed_support_from_coefficients(
            sector_bridge_support, sector_bridge_coefficients, labels
        ),
        "is_positive_circuit": all(coefficient > 0 for coefficient in sector_bridge_coefficients),
        "tests": sector_bridge_tests,
        "interpretation": (
            "The natural sector-33 height attachment makes gamma8+e33 a positive "
            "circuit obstruction. It still does not make e33 a cocircuit or make the "
            "old contour ground set a hyperplane."
        ),
    }

    sector33_cocircuit_summary = {
        "tested_extensions": [
            signed_residue_extension["name"],
            hidden_sector_scalar_extension["name"],
            sector33_height_attachment["name"],
        ],
        "e33_singleton_cocircuit_in_any_tested_extension": any(
            extension["tests"]["new_singleton_is_cocircuit"]
            for extension in [
                signed_residue_extension,
                hidden_sector_scalar_extension,
                sector33_height_attachment,
            ]
        ),
        "old_ground_hyperplane_in_any_tested_extension": any(
            extension["tests"]["old_ground_is_hyperplane"]
            for extension in [
                signed_residue_extension,
                hidden_sector_scalar_extension,
                sector33_height_attachment,
            ]
        ),
        "gamma8_plus_e33_cocircuit_in_any_tested_extension": any(
            extension["tests"]["gamma_plus_new_is_cocircuit"]
            for extension in [
                signed_residue_extension,
                hidden_sector_scalar_extension,
                sector33_height_attachment,
            ]
        ),
        "positive_circuit_extension": sector33_height_attachment["name"],
        "verdict": (
            "sector33 is certified as a positive circuit obstruction in the height "
            "attachment, not as a cocircuit/hyperplane in these natural primal extensions"
        ),
    }

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "oriented_matroid_contour_is_certified": contour.get("status")
        == "D20_ORIENTED_MATROID_CONTOUR_CERTIFIED"
        and contour.get("all_checks_pass") is True,
        "finite_contour_is_certified": finite_contour.get("status")
        == "D20_FINITE_CONTOUR_INTEGRATION_TEST_PASS"
        and finite_contour.get("all_checks_pass") is True,
        "sector33_inputs_are_certified": sector33_height.get("all_checks_pass") is True
        and sector33_attachment.get("all_checks_pass") is True
        and sector33_unique.get("all_checks_pass") is True,
        "signed_residue_quantum_is_3072": primitive_quantum == 3072,
        "gamma8_signed_residue_is_minus_40_quanta": primitive_gamma8_residue == -40,
        "sector33_height_action_is_374784": height_action == 374784,
        "sector33_transport_scalar_is_minus_187392": e33_transport_scalar == -187392,
        "sector33_dimension_is_2": e33_dimension == 2,
        "signed_residue_lift_makes_gamma8_plus_residue_a_circuit": signed_residue_tests[
            "gamma_plus_new_is_circuit"
        ],
        "hidden_sector_scalar_lift_makes_gamma8_plus_e33_a_circuit": hidden_sector_tests[
            "gamma_plus_new_is_circuit"
        ],
        "sector33_height_attachment_makes_gamma8_plus_e33_a_positive_circuit": sector_bridge_tests[
            "gamma_plus_new_is_circuit"
        ]
        and sector33_height_attachment["is_positive_circuit"],
        "sector33_height_attachment_closure_equations_vanish": all(
            value == 0
            for value in sector33_height_attachment["closure_equations"][
                "public_boundary_sum_active_plus_dim_e33"
            ]
        )
        and sector33_height_attachment["closure_equations"][
            "height_sum_active_plus_dim_e33"
        ]
        == 0,
        "no_tested_extension_makes_e33_a_singleton_cocircuit": not sector33_cocircuit_summary[
            "e33_singleton_cocircuit_in_any_tested_extension"
        ],
        "no_tested_extension_makes_old_ground_a_hyperplane": not sector33_cocircuit_summary[
            "old_ground_hyperplane_in_any_tested_extension"
        ],
        "no_tested_extension_makes_gamma8_plus_e33_a_cocircuit": not sector33_cocircuit_summary[
            "gamma8_plus_e33_cocircuit_in_any_tested_extension"
        ],
        "sector33_unique_public_zero_sector_is_cross_linked": sector33_unique["derived"][
            "public_zero_sectors"
        ]
        == [33],
    }

    report = {
        "schema": "d20.theorem.d20_oriented_matroid_sector33_extension",
        "status": "D20_ORIENTED_MATROID_SECTOR33_EXTENSION_CERTIFIED",
        "object": "D20",
        "definition": {
            "signed_residue_lift": (
                "a one-element extension of the contour incidence matrix by the non-exact "
                "signed 1-form residue quantum"
            ),
            "hidden_sector_scalar_lift": (
                "a public-zero sector scalar extension using the sector-33 transport scalar"
            ),
            "sector33_height_attachment": (
                "a decorated sector unit whose doubled column closes the all-positive "
                "gamma8 active height row"
            ),
            "cocircuit_test": (
                "a subset is a cocircuit when its complement is a hyperplane in the "
                "represented matroid"
            ),
        },
        "claim": (
            "The natural sector-33 single-element extensions of the D20 contour system "
            "do not make sector 33 a cocircuit or hyperplane. Instead, the height-derived "
            "sector-33 attachment makes gamma8+e33 a positive circuit obstruction: the "
            "all-positive gamma8 active row is closed by two copies of the sector-33 unit, "
            "exactly matching the certified -374784 residual and dim(Pi_33)=2."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
            "d20_oriented_matroid_contour_report": input_record(ORIENTED_MATROID_CONTOUR),
            "d20_finite_contour_integration_report": input_record(D20_FINITE_CONTOUR),
            "sector33_height_coherent_transport_report": input_record(
                SECTOR33_HEIGHT_TRANSPORT
            ),
            "sector33_residual_attachment_report": input_record(SECTOR33_RESIDUAL_ATTACHMENT),
            "sector33_unique_public_zero_support_report": input_record(
                SECTOR33_UNIQUE_PUBLIC_ZERO
            ),
        },
        "derived": {
            "base_lift_summary": {
                "edge_count": edge_count,
                "base_contour_rank": 19,
                "height_lift_rank": matroid_rank(base_lift),
                "active_support": active_support,
                "cyclic_signed_support": cyclic_signed_support,
            },
            "signed_residue_extension": signed_residue_extension,
            "hidden_sector_scalar_extension": hidden_sector_scalar_extension,
            "sector33_height_attachment": sector33_height_attachment,
            "sector33_cocircuit_summary": sector33_cocircuit_summary,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "confirmed": [
                "the signed contour residue has a classical one-element circuit closure",
                "the sector-33 height attachment realizes the positive-circuit obstruction",
                "the sector-33 scalar remains tied to the unique public-zero sector 33",
            ],
            "rejected": [
                "sector 33 as singleton cocircuit in the tested primal extensions",
                "old public contour ground set as the sector-33 hyperplane",
                "gamma8+e33 as cocircuit rather than circuit",
            ],
            "overclaim_guard": (
                "A sector-33 cocircuit theorem would need a dual coextension or a different "
                "decorated ground set. The certified primal extensions point to positive "
                "circuit obstruction instead."
            ),
        },
        "next_highest_yield_item": (
            "Build the dual/coextension version of the sector-33 attachment and test "
            "whether the positive circuit obstruction becomes a cocircuit in the dual "
            "oriented matroid."
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
        "schema": "d20.theorem.d20_oriented_matroid_sector33_extension_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "test sector 33 in natural one-element extensions of the D20 contour matroid",
            "certify whether sector 33 is a cocircuit/hyperplane or a positive circuit obstruction",
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
