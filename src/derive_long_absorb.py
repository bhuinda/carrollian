from __future__ import annotations

import hashlib
import json
from collections import deque
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_flow import (
        EDGE_COLUMNS as FLOW_EDGE_COLUMNS,
        OUT_DIR as LONG_FLOW_DIR,
        STATUS as LONG_FLOW_STATUS,
    )
    from .derive_long_lap import OUT_DIR as LONG_LAP_DIR
    from .derive_long_rec import (
        EDGE_COLUMNS as REC_EDGE_COLUMNS,
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_flow import (
        EDGE_COLUMNS as FLOW_EDGE_COLUMNS,
        OUT_DIR as LONG_FLOW_DIR,
        STATUS as LONG_FLOW_STATUS,
    )
    from derive_long_lap import OUT_DIR as LONG_LAP_DIR
    from derive_long_rec import (
        EDGE_COLUMNS as REC_EDGE_COLUMNS,
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_absorb"
STATUS = "LONG_ABSORB_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_FLOW_REPORT = LONG_FLOW_DIR / "report.json"
LONG_FLOW_TABLES = LONG_FLOW_DIR / "tables.npz"
LONG_LAP_TABLES = LONG_LAP_DIR / "tables.npz"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_absorb.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_absorb.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

MATRIX_COLUMNS = [
    "source_component_id",
    "absorbing_component_id",
    "flow_num",
    "flow_den",
    "flow_num_digits",
    "flow_den_digits",
    "flow_num_mod_1000000007",
    "flow_den_mod_1000000007",
    "flow_num_mod_1000000009",
    "flow_den_mod_1000000009",
    "flow_sha256",
    "diagonal_flag",
]
MATRIX_DIGEST_COLUMNS = [
    "source_component_id",
    "absorbing_component_id",
    "flow_num_digits",
    "flow_den_digits",
    "flow_num_mod_1000000007",
    "flow_den_mod_1000000007",
    "flow_num_mod_1000000009",
    "flow_den_mod_1000000009",
    "diagonal_flag",
]
OWNER_COLUMNS = [
    "inactive_basis_id",
    "shell_id",
    "weak_class_code",
    "active_boundary_count",
    "inactive_boundary_count",
    "weighted_degree",
    "dominant_component_id",
    "prob0_num_mod_1000000007",
    "prob0_den_mod_1000000007",
    "prob0_num_mod_1000000009",
    "prob0_den_mod_1000000009",
    "prob1_num_mod_1000000007",
    "prob1_den_mod_1000000007",
    "prob1_num_mod_1000000009",
    "prob1_den_mod_1000000009",
    "prob2_num_mod_1000000007",
    "prob2_den_mod_1000000007",
    "prob2_num_mod_1000000009",
    "prob2_den_mod_1000000009",
]
SHELL_COLUMNS = [
    "shell_id",
    "owner_count",
    "basis_sum",
    "basis_square_sum",
    "active_boundary_count",
    "inactive_boundary_count",
    "dominant0_count",
    "dominant1_count",
    "dominant2_count",
    "prob0_sum_num_mod_1000000007",
    "prob0_sum_den_mod_1000000007",
    "prob0_sum_num_mod_1000000009",
    "prob0_sum_den_mod_1000000009",
    "prob1_sum_num_mod_1000000007",
    "prob1_sum_den_mod_1000000007",
    "prob1_sum_num_mod_1000000009",
    "prob1_sum_den_mod_1000000009",
    "prob2_sum_num_mod_1000000007",
    "prob2_sum_den_mod_1000000007",
    "prob2_sum_num_mod_1000000009",
    "prob2_sum_den_mod_1000000009",
    "active_weighted_prob0_num_mod_1000000007",
    "active_weighted_prob0_den_mod_1000000007",
    "active_weighted_prob0_num_mod_1000000009",
    "active_weighted_prob0_den_mod_1000000009",
    "active_weighted_prob1_num_mod_1000000007",
    "active_weighted_prob1_den_mod_1000000007",
    "active_weighted_prob1_num_mod_1000000009",
    "active_weighted_prob1_den_mod_1000000009",
    "active_weighted_prob2_num_mod_1000000007",
    "active_weighted_prob2_den_mod_1000000007",
    "active_weighted_prob2_num_mod_1000000009",
    "active_weighted_prob2_den_mod_1000000009",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "full_owner_count",
    "active_owner_count",
    "inactive_owner_count",
    "active_component_count",
    "inactive_dirichlet_rank",
    "dirichlet_det_digit_count",
    "dirichlet_det_mod_1000000007",
    "dirichlet_det_mod_1000000009",
    "dirichlet_det_positive_flag",
    "absorption_matrix_entry_count",
    "transfer_total_boundary_count",
    "transfer_source0_boundary_count",
    "transfer_source1_boundary_count",
    "transfer_source2_boundary_count",
    "transfer_symmetry_flag",
    "transfer_row_sum_match_flag",
    "transfer_col_sum_match_flag",
    "probability_row_sum_violation_count",
    "inactive_shell_count",
    "inactive_shell_max_distance",
    "inactive_weighted_degree_sum",
    "inactive_active_boundary_sum",
    "inactive_internal_boundary_sum",
    "dominant0_owner_count",
    "dominant1_owner_count",
    "dominant2_owner_count",
    "shell1_dominant0_owner_count",
    "shell1_dominant1_owner_count",
    "shell1_dominant2_owner_count",
    "diagonal_return_num_digits",
    "diagonal_return_den_digits",
    "diagonal_return_num_mod_1000000007",
    "diagonal_return_den_mod_1000000007",
    "offdiagonal_transfer_num_digits",
    "offdiagonal_transfer_den_digits",
    "offdiagonal_transfer_num_mod_1000000007",
    "offdiagonal_transfer_den_mod_1000000007",
    "long_flow_input_certified",
    "long_rec_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def fraction_record(value: Fraction) -> dict[str, int | str]:
    text = f"{value.numerator}/{value.denominator}"
    return {
        "num": value.numerator,
        "den": value.denominator,
        "num_digits": len(str(abs(value.numerator))),
        "den_digits": len(str(value.denominator)),
        "num_mod_1000000007": value.numerator % MOD_PRIMES[0],
        "den_mod_1000000007": value.denominator % MOD_PRIMES[0],
        "num_mod_1000000009": value.numerator % MOD_PRIMES[1],
        "den_mod_1000000009": value.denominator % MOD_PRIMES[1],
        "sha256": hashlib.sha256(text.encode("ascii")).hexdigest(),
    }


def fraction_mods(value: Fraction) -> list[int]:
    return [
        value.numerator % MOD_PRIMES[0],
        value.denominator % MOD_PRIMES[0],
        value.numerator % MOD_PRIMES[1],
        value.denominator % MOD_PRIMES[1],
    ]


def dominant_component(values: list[Fraction]) -> int:
    return max(range(len(values)), key=lambda index: (values[index], -index))


def matrix_fraction_text(matrix_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['source_component_id']},{row['absorbing_component_id']},"
        f"{row['flow_num']},{row['flow_den']}\n"
        for row in matrix_rows
    )


def owner_digest_text(owner_rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in OWNER_COLUMNS) + "\n"
        for row in owner_rows
    )


def shell_digest_text(shell_rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in SHELL_COLUMNS) + "\n"
        for row in shell_rows
    )


def bareiss_solve(
    matrix: list[list[int]],
    rhs: list[list[int]],
) -> tuple[list[list[Fraction]], int]:
    n = len(matrix)
    m = len(rhs[0])
    aug = [matrix[index][:] + rhs[index][:] for index in range(n)]
    sign = 1
    previous = 1
    for col in range(n - 1):
        if aug[col][col] == 0:
            swap = next(
                (row for row in range(col + 1, n) if aug[row][col] != 0),
                None,
            )
            if swap is None:
                raise ValueError("singular Dirichlet matrix")
            aug[col], aug[swap] = aug[swap], aug[col]
            sign = -sign
        pivot = aug[col][col]
        pivot_row = aug[col]
        for row_index in range(col + 1, n):
            multiplier = aug[row_index][col]
            row = aug[row_index]
            for entry_index in range(col + 1, n + m):
                row[entry_index] = (
                    row[entry_index] * pivot
                    - multiplier * pivot_row[entry_index]
                ) // previous
            row[col] = 0
        previous = pivot

    determinant = sign * aug[n - 1][n - 1]
    solution = [[Fraction(0) for _ in range(m)] for _ in range(n)]
    for row_index in range(n - 1, -1, -1):
        row = aug[row_index]
        for rhs_index in range(m):
            total = Fraction(row[n + rhs_index])
            for col in range(row_index + 1, n):
                if row[col]:
                    total -= row[col] * solution[col][rhs_index]
            solution[row_index][rhs_index] = total / Fraction(row[row_index])
    return solution, determinant


def bfs_distances(
    owner_ids: list[int],
    active_owners: set[int],
    rec_edge_rows: list[dict[str, int]],
) -> dict[int, int]:
    adjacency = {owner: set() for owner in owner_ids}
    for row in rec_edge_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        adjacency[left].add(right)
        adjacency[right].add(left)
    distances = {owner: 0 for owner in active_owners}
    queue: deque[int] = deque(sorted(active_owners))
    while queue:
        owner = queue.popleft()
        for nxt in sorted(adjacency[owner]):
            if nxt in distances:
                continue
            distances[nxt] = distances[owner] + 1
            queue.append(nxt)
    return distances


def build_absorption_system() -> dict[str, Any]:
    long_flow = load_json(LONG_FLOW_REPORT)
    long_rec = load_json(LONG_REC_REPORT)
    flow_tables = np.load(LONG_FLOW_TABLES, allow_pickle=False)
    lap_tables = np.load(LONG_LAP_TABLES, allow_pickle=False)
    rec_tables = np.load(LONG_REC_TABLES, allow_pickle=False)

    rec_owner_rows = rows_from_table(
        np.asarray(rec_tables["owner_table"]),
        REC_OWNER_COLUMNS,
    )
    rec_edge_rows = rows_from_table(
        np.asarray(rec_tables["edge_table"]),
        REC_EDGE_COLUMNS,
    )
    flow_edge_rows = rows_from_table(
        np.asarray(flow_tables["edge_table"]),
        FLOW_EDGE_COLUMNS,
    )
    active_owners = [int(value) for value in np.asarray(lap_tables["active_owner_ids"])]
    active_set = set(active_owners)
    component_ids = [int(value) for value in np.asarray(lap_tables["component_ids"])]
    component_by_active = dict(zip(active_owners, component_ids))
    component_count = max(component_ids) + 1
    owner_by_basis = {row["basis_id"]: row for row in rec_owner_rows}
    owner_ids = sorted(owner_by_basis)
    inactive_owners = [owner for owner in owner_ids if owner not in active_set]
    inactive_rank = {owner: rank for rank, owner in enumerate(inactive_owners)}
    n = len(inactive_owners)

    matrix = [[0 for _ in range(n)] for _ in range(n)]
    rhs = [[0 for _ in range(component_count)] for _ in range(n)]
    active_boundary = [0 for _ in range(n)]
    inactive_boundary = [0 for _ in range(n)]
    for row in rec_edge_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        weight = int(row["boundary_count"])
        left_active = left in active_set
        right_active = right in active_set
        if not left_active and not right_active:
            left_index = inactive_rank[left]
            right_index = inactive_rank[right]
            matrix[left_index][left_index] += weight
            matrix[right_index][right_index] += weight
            matrix[left_index][right_index] -= weight
            matrix[right_index][left_index] -= weight
            inactive_boundary[left_index] += weight
            inactive_boundary[right_index] += weight
        elif left_active and not right_active:
            index = inactive_rank[right]
            matrix[index][index] += weight
            rhs[index][component_by_active[left]] += weight
            active_boundary[index] += weight
        elif right_active and not left_active:
            index = inactive_rank[left]
            matrix[index][index] += weight
            rhs[index][component_by_active[right]] += weight
            active_boundary[index] += weight

    probabilities, determinant = bareiss_solve(matrix, rhs)
    distances = bfs_distances(owner_ids, active_set, rec_edge_rows)
    transfer = [
        [Fraction(0) for _ in range(component_count)]
        for _ in range(component_count)
    ]
    for row in flow_edge_rows:
        source = int(row["component_id"])
        inactive = int(row["inactive_basis_id"])
        weight = int(row["boundary_count"])
        probability_row = probabilities[inactive_rank[inactive]]
        for target in range(component_count):
            transfer[source][target] += weight * probability_row[target]

    return {
        "long_flow": long_flow,
        "long_rec": long_rec,
        "rec_owner_rows": rec_owner_rows,
        "inactive_owners": inactive_owners,
        "owner_by_basis": owner_by_basis,
        "active_owners": active_owners,
        "component_count": component_count,
        "matrix": matrix,
        "rhs": rhs,
        "probabilities": probabilities,
        "determinant": determinant,
        "active_boundary": active_boundary,
        "inactive_boundary": inactive_boundary,
        "distances": distances,
        "transfer": transfer,
    }


def build_rows() -> dict[str, Any]:
    system = build_absorption_system()
    inactive_owners = system["inactive_owners"]
    owner_by_basis = system["owner_by_basis"]
    probabilities = system["probabilities"]
    active_boundary = system["active_boundary"]
    inactive_boundary = system["inactive_boundary"]
    distances = system["distances"]
    transfer = system["transfer"]
    determinant = int(system["determinant"])

    matrix_rows: list[dict[str, Any]] = []
    matrix_digest_rows: list[dict[str, int]] = []
    for source in range(system["component_count"]):
        for target in range(system["component_count"]):
            value = transfer[source][target]
            record = fraction_record(value)
            matrix_row = {
                "source_component_id": source,
                "absorbing_component_id": target,
                "flow_num": record["num"],
                "flow_den": record["den"],
                "flow_num_digits": record["num_digits"],
                "flow_den_digits": record["den_digits"],
                "flow_num_mod_1000000007": record["num_mod_1000000007"],
                "flow_den_mod_1000000007": record["den_mod_1000000007"],
                "flow_num_mod_1000000009": record["num_mod_1000000009"],
                "flow_den_mod_1000000009": record["den_mod_1000000009"],
                "flow_sha256": record["sha256"],
                "diagonal_flag": int(source == target),
            }
            matrix_rows.append(matrix_row)
            matrix_digest_rows.append(
                {
                    column: int(matrix_row[column])
                    for column in MATRIX_DIGEST_COLUMNS
                }
            )

    owner_rows: list[dict[str, int]] = []
    for owner in inactive_owners:
        rank = inactive_owners.index(owner)
        probs = probabilities[rank]
        row = {
            "inactive_basis_id": owner,
            "shell_id": int(distances[owner]),
            "weak_class_code": int(owner_by_basis[owner]["weak_class_code"]),
            "active_boundary_count": int(active_boundary[rank]),
            "inactive_boundary_count": int(inactive_boundary[rank]),
            "weighted_degree": int(owner_by_basis[owner]["weighted_degree"]),
            "dominant_component_id": dominant_component(probs),
        }
        for component_id, value in enumerate(probs):
            mods = fraction_mods(value)
            for suffix, mod_value in zip(
                [
                    "num_mod_1000000007",
                    "den_mod_1000000007",
                    "num_mod_1000000009",
                    "den_mod_1000000009",
                ],
                mods,
            ):
                row[f"prob{component_id}_{suffix}"] = mod_value
        owner_rows.append(row)

    shell_rows: list[dict[str, int]] = []
    inactive_shells = sorted({int(distances[owner]) for owner in inactive_owners})
    for shell_id in inactive_shells:
        shell_owners = [
            owner for owner in inactive_owners if int(distances[owner]) == shell_id
        ]
        shell_probs = [
            sum(probabilities[inactive_owners.index(owner)][component_id] for owner in shell_owners)
            for component_id in range(system["component_count"])
        ]
        weighted_shell_probs = [
            sum(
                active_boundary[inactive_owners.index(owner)]
                * probabilities[inactive_owners.index(owner)][component_id]
                for owner in shell_owners
            )
            for component_id in range(system["component_count"])
        ]
        shell_row = {
            "shell_id": shell_id,
            "owner_count": len(shell_owners),
            "basis_sum": sum(shell_owners),
            "basis_square_sum": sum(owner * owner for owner in shell_owners),
            "active_boundary_count": sum(
                active_boundary[inactive_owners.index(owner)]
                for owner in shell_owners
            ),
            "inactive_boundary_count": sum(
                inactive_boundary[inactive_owners.index(owner)]
                for owner in shell_owners
            ),
            "dominant0_count": sum(
                1
                for owner in shell_owners
                if dominant_component(probabilities[inactive_owners.index(owner)]) == 0
            ),
            "dominant1_count": sum(
                1
                for owner in shell_owners
                if dominant_component(probabilities[inactive_owners.index(owner)]) == 1
            ),
            "dominant2_count": sum(
                1
                for owner in shell_owners
                if dominant_component(probabilities[inactive_owners.index(owner)]) == 2
            ),
        }
        for component_id, value in enumerate(shell_probs):
            mods = fraction_mods(value)
            shell_row[f"prob{component_id}_sum_num_mod_1000000007"] = mods[0]
            shell_row[f"prob{component_id}_sum_den_mod_1000000007"] = mods[1]
            shell_row[f"prob{component_id}_sum_num_mod_1000000009"] = mods[2]
            shell_row[f"prob{component_id}_sum_den_mod_1000000009"] = mods[3]
        for component_id, value in enumerate(weighted_shell_probs):
            mods = fraction_mods(value)
            shell_row[
                f"active_weighted_prob{component_id}_num_mod_1000000007"
            ] = mods[0]
            shell_row[
                f"active_weighted_prob{component_id}_den_mod_1000000007"
            ] = mods[1]
            shell_row[
                f"active_weighted_prob{component_id}_num_mod_1000000009"
            ] = mods[2]
            shell_row[
                f"active_weighted_prob{component_id}_den_mod_1000000009"
            ] = mods[3]
        shell_rows.append(shell_row)

    diagonal_return = sum(transfer[index][index] for index in range(system["component_count"]))
    offdiagonal_transfer = sum(
        transfer[source][target]
        for source in range(system["component_count"])
        for target in range(system["component_count"])
        if source != target
    )
    diagonal_record = fraction_record(diagonal_return)
    offdiagonal_record = fraction_record(offdiagonal_transfer)
    source_boundaries = [sum(row[target] for target in range(system["component_count"])) for row in transfer]
    target_boundaries = [sum(transfer[source][target] for source in range(system["component_count"])) for target in range(system["component_count"])]
    row_sum_violations = sum(1 for row in probabilities if sum(row) != 1)
    dominant_counts = [
        sum(1 for row in owner_rows if row["dominant_component_id"] == component_id)
        for component_id in range(system["component_count"])
    ]
    shell1_rows = [row for row in owner_rows if row["shell_id"] == 1]
    shell1_dominant_counts = [
        sum(1 for row in shell1_rows if row["dominant_component_id"] == component_id)
        for component_id in range(system["component_count"])
    ]
    obs = {
        "line_point_count": 985,
        "full_owner_count": len(system["rec_owner_rows"]),
        "active_owner_count": len(system["active_owners"]),
        "inactive_owner_count": len(inactive_owners),
        "active_component_count": system["component_count"],
        "inactive_dirichlet_rank": len(inactive_owners),
        "dirichlet_det_digit_count": len(str(abs(determinant))),
        "dirichlet_det_mod_1000000007": determinant % MOD_PRIMES[0],
        "dirichlet_det_mod_1000000009": determinant % MOD_PRIMES[1],
        "dirichlet_det_positive_flag": int(determinant > 0),
        "absorption_matrix_entry_count": len(matrix_rows),
        "transfer_total_boundary_count": int(sum(source_boundaries)),
        "transfer_source0_boundary_count": int(source_boundaries[0]),
        "transfer_source1_boundary_count": int(source_boundaries[1]),
        "transfer_source2_boundary_count": int(source_boundaries[2]),
        "transfer_symmetry_flag": int(
            all(
                transfer[source][target] == transfer[target][source]
                for source in range(system["component_count"])
                for target in range(system["component_count"])
            )
        ),
        "transfer_row_sum_match_flag": int(source_boundaries == [1342, 864, 2378]),
        "transfer_col_sum_match_flag": int(target_boundaries == [1342, 864, 2378]),
        "probability_row_sum_violation_count": row_sum_violations,
        "inactive_shell_count": len(inactive_shells),
        "inactive_shell_max_distance": max(inactive_shells),
        "inactive_weighted_degree_sum": sum(
            int(row["weighted_degree"]) for row in owner_rows
        ),
        "inactive_active_boundary_sum": sum(active_boundary),
        "inactive_internal_boundary_sum": sum(inactive_boundary),
        "dominant0_owner_count": dominant_counts[0],
        "dominant1_owner_count": dominant_counts[1],
        "dominant2_owner_count": dominant_counts[2],
        "shell1_dominant0_owner_count": shell1_dominant_counts[0],
        "shell1_dominant1_owner_count": shell1_dominant_counts[1],
        "shell1_dominant2_owner_count": shell1_dominant_counts[2],
        "diagonal_return_num_digits": int(diagonal_record["num_digits"]),
        "diagonal_return_den_digits": int(diagonal_record["den_digits"]),
        "diagonal_return_num_mod_1000000007": int(
            diagonal_record["num_mod_1000000007"]
        ),
        "diagonal_return_den_mod_1000000007": int(
            diagonal_record["den_mod_1000000007"]
        ),
        "offdiagonal_transfer_num_digits": int(offdiagonal_record["num_digits"]),
        "offdiagonal_transfer_den_digits": int(offdiagonal_record["den_digits"]),
        "offdiagonal_transfer_num_mod_1000000007": int(
            offdiagonal_record["num_mod_1000000007"]
        ),
        "offdiagonal_transfer_den_mod_1000000007": int(
            offdiagonal_record["den_mod_1000000007"]
        ),
        "long_flow_input_certified": int(
            system["long_flow"].get("status") == LONG_FLOW_STATUS
        ),
        "long_rec_input_certified": int(
            system["long_rec"].get("status") == LONG_REC_STATUS
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        **system,
        "matrix_rows": matrix_rows,
        "matrix_digest_rows": matrix_digest_rows,
        "owner_rows": owner_rows,
        "shell_rows": shell_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "determinant_record": {
            "digits": len(str(abs(determinant))),
            "mod_1000000007": determinant % MOD_PRIMES[0],
            "mod_1000000009": determinant % MOD_PRIMES[1],
            "sha256": hashlib.sha256(str(determinant).encode("ascii")).hexdigest(),
        },
        "diagonal_return": diagonal_record,
        "offdiagonal_transfer": offdiagonal_record,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    matrix_digest_table = table_from_rows(
        MATRIX_DIGEST_COLUMNS,
        rows["matrix_digest_rows"],
    )
    owner_table = table_from_rows(OWNER_COLUMNS, rows["owner_rows"])
    shell_table = table_from_rows(SHELL_COLUMNS, rows["shell_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    matrix_hash = hashlib.sha256(
        matrix_fraction_text(rows["matrix_rows"]).encode("ascii")
    ).hexdigest()
    owner_hash = hashlib.sha256(
        owner_digest_text(rows["owner_rows"]).encode("ascii")
    ).hexdigest()
    shell_hash = hashlib.sha256(
        shell_digest_text(rows["shell_rows"]).encode("ascii")
    ).hexdigest()
    matrix_mod_signature = [
        (
            row["source_component_id"],
            row["absorbing_component_id"],
            row["flow_num_digits"],
            row["flow_den_digits"],
            row["flow_num_mod_1000000007"],
            row["flow_den_mod_1000000007"],
            row["flow_num_mod_1000000009"],
            row["flow_den_mod_1000000009"],
            row["diagonal_flag"],
        )
        for row in rows["matrix_digest_rows"]
    ]
    checks = {
        "inputs_certified": (
            obs["long_flow_input_certified"],
            obs["long_rec_input_certified"],
        )
        == (1, 1),
        "dirichlet_determinant_exact": (
            obs["inactive_dirichlet_rank"],
            obs["dirichlet_det_digit_count"],
            obs["dirichlet_det_mod_1000000007"],
            obs["dirichlet_det_mod_1000000009"],
            obs["dirichlet_det_positive_flag"],
            rows["determinant_record"]["sha256"],
        )
        == (
            208,
            270,
            328_173_059,
            543_927_589,
            1,
            "63e315795445a97c6998b510ff4b0dbdafdf389f20fccb6b6ae8e735c20b8a7e",
        ),
        "transfer_conservation_exact": (
            obs["transfer_total_boundary_count"],
            obs["transfer_source0_boundary_count"],
            obs["transfer_source1_boundary_count"],
            obs["transfer_source2_boundary_count"],
            obs["transfer_symmetry_flag"],
            obs["transfer_row_sum_match_flag"],
            obs["transfer_col_sum_match_flag"],
            obs["probability_row_sum_violation_count"],
        )
        == (4_584, 1_342, 864, 2_378, 1, 1, 1, 0),
        "matrix_mod_signature_exact": matrix_mod_signature
        == [
            (0, 0, 258, 255, 618_582_603, 75_025_110, 518_772_888, 814_085_260, 1),
            (0, 1, 256, 254, 689_187_283, 253_126_048, 481_415_130, 867_253_560, 0),
            (0, 2, 258, 255, 524_619_644, 75_025_110, 429_673_192, 814_085_260, 0),
            (1, 0, 256, 254, 689_187_283, 253_126_048, 481_415_130, 867_253_560, 0),
            (1, 1, 257, 254, 500_341_420, 253_126_048, 752_850_196, 867_253_560, 1),
            (1, 2, 256, 254, 511_375_250, 253_126_048, 72_803_782, 867_253_560, 0),
            (2, 0, 258, 255, 524_619_644, 75_025_110, 429_673_192, 814_085_260, 0),
            (2, 1, 256, 254, 511_375_250, 253_126_048, 72_803_782, 867_253_560, 0),
            (2, 2, 259, 255, 612_084_781, 75_025_110, 717_766_923, 814_085_260, 1),
        ],
        "diagonal_offdiagonal_exact": (
            obs["diagonal_return_num_digits"],
            obs["diagonal_return_den_digits"],
            obs["diagonal_return_num_mod_1000000007"],
            obs["diagonal_return_den_mod_1000000007"],
            obs["offdiagonal_transfer_num_digits"],
            obs["offdiagonal_transfer_den_digits"],
            obs["offdiagonal_transfer_num_mod_1000000007"],
            obs["offdiagonal_transfer_den_mod_1000000007"],
            rows["diagonal_return"]["sha256"],
            rows["offdiagonal_transfer"]["sha256"],
        )
        == (
            259,
            255,
            619_430_690,
            37_512_555,
            258,
            255,
            338_120_233,
            37_512_555,
            "ca8da1e1c9b5d70d70c63f86ef9da5e71bac2e48e550405f195e33f365bc1332",
            "aeecacdc00b81f37cb0ea08a895059647dbbdbd10af3219b14b7285da89e6411",
        ),
        "inactive_owner_shell_exact": (
            obs["inactive_shell_count"],
            obs["inactive_shell_max_distance"],
            obs["inactive_weighted_degree_sum"],
            obs["inactive_active_boundary_sum"],
            obs["inactive_internal_boundary_sum"],
            obs["dominant0_owner_count"],
            obs["dominant1_owner_count"],
            obs["dominant2_owner_count"],
            obs["shell1_dominant0_owner_count"],
            obs["shell1_dominant1_owner_count"],
            obs["shell1_dominant2_owner_count"],
        )
        == (7, 7, 20_392, 4_584, 15_808, 86, 2, 120, 27, 2, 23),
        "digest_hashes_exact": (
            matrix_hash,
            owner_hash,
            shell_hash,
        )
        == (
            "7dde8dfc5c2306b4a5f55b3176ab7e19c2fba7457f2da2ac3cfa00d625cc973b",
            "ea8e86de6b25fa8c775ff22e45c508ad41a41085f4414844b8ff978498c08bdb",
            "99b44a0e967e9ffdc1166568e824c695f4a8ea45c21e8d41a18955da4c7c48f1",
        ),
        "table_shapes_match": (
            tuple(matrix_digest_table.shape),
            tuple(owner_table.shape),
            tuple(shell_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (9, len(MATRIX_DIGEST_COLUMNS)),
            (208, len(OWNER_COLUMNS)),
            (7, len(SHELL_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "long_rec_inactive_absorbing_dirichlet_kernel",
        "scope": {
            "interior": "208 inactive long_rec owners",
            "absorbing_boundary": "three long_lap active owner components",
            "operator": "weighted Dirichlet Laplacian on inactive owners",
        },
        "dirichlet": {
            "rank": obs["inactive_dirichlet_rank"],
            "determinant": rows["determinant_record"],
            "probability_row_sum_violations": obs[
                "probability_row_sum_violation_count"
            ],
        },
        "transfer": {
            "total_boundary": obs["transfer_total_boundary_count"],
            "source_boundaries": [
                int(obs["transfer_source0_boundary_count"]),
                int(obs["transfer_source1_boundary_count"]),
                int(obs["transfer_source2_boundary_count"]),
            ],
            "symmetric": bool(obs["transfer_symmetry_flag"]),
            "row_sums_match": bool(obs["transfer_row_sum_match_flag"]),
            "col_sums_match": bool(obs["transfer_col_sum_match_flag"]),
            "matrix_fraction_text_sha256": matrix_hash,
            "matrix_digest_table_sha256": sha_array(matrix_digest_table),
            "diagonal_return": rows["diagonal_return"],
            "offdiagonal_transfer": rows["offdiagonal_transfer"],
        },
        "inactive_owners": {
            "owner_count": obs["inactive_owner_count"],
            "dominant_counts": [
                obs["dominant0_owner_count"],
                obs["dominant1_owner_count"],
                obs["dominant2_owner_count"],
            ],
            "shell1_dominant_counts": [
                obs["shell1_dominant0_owner_count"],
                obs["shell1_dominant1_owner_count"],
                obs["shell1_dominant2_owner_count"],
            ],
            "owner_digest_sha256": owner_hash,
            "owner_table_sha256": sha_array(owner_table),
        },
        "shells": {
            "shell_count": obs["inactive_shell_count"],
            "max_distance": obs["inactive_shell_max_distance"],
            "shell_digest_sha256": shell_hash,
            "shell_table_sha256": sha_array(shell_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    absorb = {
        "schema": "long.absorb@1",
        "object": "long_rec_inactive_absorbing_dirichlet_kernel",
        "status": STATUS if all(checks.values()) else "LONG_ABSORB_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.absorb.report@1",
        "status": absorb["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_absorb certifies the exact absorbing Dirichlet kernel obtained "
            "by collapsing the three long_lap active components as boundary "
            "terminals inside the full long_rec owner graph. The inactive "
            "208-owner Laplacian is nonsingular, all absorption rows sum to one, "
            "and the 3x3 leakage transfer matrix is symmetric with conserved "
            "row and column boundary totals 1342, 864, and 2378."
        ),
        "stage_protocol": {
            "draft": "collapse active long_lap components to three absorbing terminals",
            "witness": "solve the inactive weighted Dirichlet Laplacian exactly over Q",
            "coherence": "check determinant, transfer matrix, conservation, dominance, shell, and digest fingerprints",
            "closure": "emit exact transfer matrix, owner/shell digests, tables, certificate, manifest, and report",
            "emit": "write long_absorb artifacts and verifier hook",
        },
        "inputs": {
            "long_flow_report": input_entry(
                LONG_FLOW_REPORT,
                {"status": rows["long_flow"].get("status")},
            ),
            "long_flow_tables": input_entry(LONG_FLOW_TABLES),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
            "long_rec_report": input_entry(
                LONG_REC_REPORT,
                {"status": rows["long_rec"].get("status")},
            ),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "absorb": relpath(OUT_DIR / "absorb.json"),
            "matrix_csv": relpath(OUT_DIR / "matrix.csv"),
            "owner_csv": relpath(OUT_DIR / "owner.csv"),
            "shell_csv": relpath(OUT_DIR / "shell.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the inactive long_rec Dirichlet Laplacian is nonsingular",
                "each inactive owner has exact absorption probabilities summing to one",
                "the shell-1 leakage induces a symmetric conserved 3x3 component transfer matrix",
                "the inactive shell dominance profile out to distance seven",
            ],
            "does_not_certify_because_out_of_scope": [
                "support-changing recouplings outside long_rec",
                "continuous-time diffusion or asymptotic stochastic limits",
                "a universal eta6 horizon theorem",
                "higher-order tensor repairs beyond the owner transition kernel",
            ],
        },
        "next_highest_yield_item": (
            "Build long_spec: certify the reduced three-terminal Dirichlet/Schur "
            "operator and its finite spectral fingerprints, using long_absorb's "
            "symmetric transfer matrix as the boundary kernel."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.absorb.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.absorb.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "absorb": absorb,
        "matrix_csv": csv_text(MATRIX_COLUMNS, rows["matrix_rows"]),
        "owner_csv": csv_text(OWNER_COLUMNS, rows["owner_rows"]),
        "shell_csv": csv_text(SHELL_COLUMNS, rows["shell_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "matrix_digest_table": matrix_digest_table,
        "owner_table": owner_table,
        "shell_table": shell_table,
        "observable_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "absorb.json", payloads["absorb"])
    (OUT_DIR / "matrix.csv").write_text(payloads["matrix_csv"], encoding="utf-8")
    (OUT_DIR / "owner.csv").write_text(payloads["owner_csv"], encoding="utf-8")
    (OUT_DIR / "shell.csv").write_text(payloads["shell_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        matrix_digest_table=payloads["matrix_digest_table"],
        owner_table=payloads["owner_table"],
        shell_table=payloads["shell_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
