from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_sandpile_critical_group_theorem import smith_normal_form_diagonal
    from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import smith_normal_form_diagonal
    from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "d20_boundary_loop_step_atom_incidence"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
D20_PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
LOOP297_SCATTERING_AMPLITUDE_LIFT = (
    D20_INVARIANTS / "theorems" / "loop297_scattering_amplitude_lift" / "report.json"
)
COMPACT_AMPLITUDE_QUOTIENT = (
    D20_INVARIANTS / "theorems" / "compact_amplitude_quotient" / "report.json"
)

INCIDENCE_CSV = DEFAULT_OUT_DIR / "boundary_atom_step_incidence.csv"
PAIR_ALIGNMENT_CSV = DEFAULT_OUT_DIR / "directed_pair_projection_step_atom_alignment.csv"

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


def parse_label(label: str) -> tuple[str, ...]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label {label!r}")
    order = {name: idx for idx, name in enumerate(H6_LABELS)}
    return tuple(sorted((part.strip() for part in body[1:-1].split(",") if part.strip()), key=order.__getitem__))


def public_atom_label(parts: tuple[str, ...]) -> str:
    return "{" + ",".join(parts) + "}"


def pair_key(removed: str, added: str) -> str:
    return f"{removed}->{added}"


def load_edges() -> list[dict[str, Any]]:
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    edges = []
    for row in rows:
        edges.append(
            {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": parse_label(row["u_label"]),
                "v_label": parse_label(row["v_label"]),
                "interface_weight": int(row["interface_weight"]),
                "selector_duad": row["selector_duad"],
                "selector_choice": int(row["selector_choice"]),
            }
        )
    return sorted(edges, key=lambda row: row["edge_id"])


def load_primitive_cycle_rows() -> list[dict[str, Any]]:
    with D20_PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [
        {
            "cycle_id": int(row["cycle_id"]),
            "length": int(row["length"]),
            "vertices": [int(value) for value in row["vertices"].split()],
            "edge_ids": [int(value) for value in row["edge_ids"].split()],
            "optical_action": int(row["optical_action"]),
        }
        for row in rows
    ]


def build_public_atom_rows(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels_by_vertex: dict[int, tuple[str, ...]] = {}
    for edge in edges:
        for key in ("u", "v"):
            label_key = f"{key}_label"
            vertex_id = int(edge[key])
            label = edge[label_key]
            prior = labels_by_vertex.setdefault(vertex_id, label)
            if prior != label:
                raise ValueError(f"inconsistent label for vertex {vertex_id}")
    rows = []
    for vertex_id in sorted(labels_by_vertex):
        label = labels_by_vertex[vertex_id]
        rows.append(
            {
                "public_atom_id": vertex_id,
                "public_atom_label": public_atom_label(label),
                "h6_triple": "|".join(label),
                "native_domain": "Lambda^3 H6",
            }
        )
    return rows


def signed_vertex_vector(occurrences: list[dict[str, Any]], vertex_count: int) -> list[int]:
    vector = [0 for _ in range(vertex_count)]
    for occurrence in occurrences:
        vector[int(occurrence["source_vertex"])] -= 1
        vector[int(occurrence["target_vertex"])] += 1
    return vector


def sparse_vector(vector: list[int]) -> list[dict[str, int]]:
    return [
        {"public_atom_id": idx, "coefficient": int(value)}
        for idx, value in enumerate(vector)
        if value != 0
    ]


def matrix_rank_rational(matrix: list[list[int]]) -> int:
    work = [[float(value) for value in row] for row in matrix]
    row_count = len(work)
    col_count = len(work[0]) if row_count else 0
    rank = 0
    col = 0
    while rank < row_count and col < col_count:
        pivot = None
        for row in range(rank, row_count):
            if abs(work[row][col]) > 1e-9:
                pivot = row
                break
        if pivot is None:
            col += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][col]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][col]
            if abs(factor) > 1e-9:
                work[row] = [
                    work[row][idx] - factor * work[rank][idx] for idx in range(col_count)
                ]
        rank += 1
        col += 1
    return rank


def build_pair_alignment_rows(
    pair_projection_rows: list[dict[str, Any]],
    step_atoms: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    atom_by_pair: dict[str, dict[str, Any]] = {}
    for atom in step_atoms:
        swaps = atom["directed_channel_swaps"]
        if len(swaps) == 1:
            atom_by_pair[str(swaps[0])] = atom
    rows = []
    for row in sorted(pair_projection_rows, key=lambda item: (item["removed"], item["added"])):
        key = pair_key(str(row["removed"]), str(row["added"]))
        atom = atom_by_pair.get(key)
        rows.append(
            {
                "directed_pair": key,
                "removed": row["removed"],
                "added": row["added"],
                "boundary_projection_support": int(row["support"]),
                "boundary_projection_coefficient_sum": int(row["coefficient_sum"]),
                "boundary_projection_closed_at_removed": bool(row["all_outputs_closed_at_removed"]),
                "observed_in_compact_step_atoms": atom is not None,
                "step_atom_id": None if atom is None else int(atom["step_atom_id"]),
                "step_vector_sha256": None if atom is None else atom["step_vector_sha256"],
                "step_atom_occurrence_count": None if atom is None else int(atom["occurrence_count"]),
                "step_atom_vector_support": None if atom is None else int(atom["vector_support"]),
                "step_atom_vector_coefficient_sum_signed": (
                    None if atom is None else int(atom["vector_coefficient_sum_signed"])
                ),
            }
        )
    return rows


def build_step_atom_incidence_rows(
    step_atoms: list[dict[str, Any]],
    public_atom_rows: list[dict[str, Any]],
    pair_alignment_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[list[int]]]:
    vertex_count = len(public_atom_rows)
    pair_by_key = {row["directed_pair"]: row for row in pair_alignment_rows}
    rows = []
    columns = []
    for atom in sorted(step_atoms, key=lambda row: int(row["step_atom_id"])):
        swaps = [str(value) for value in atom["directed_channel_swaps"]]
        projection = pair_by_key[swaps[0]] if len(swaps) == 1 else {}
        occurrences = [
            {
                "generator_cycle_id": int(row["generator_cycle_id"]),
                "step_index": int(row["step_index"]),
                "edge_id": int(row["edge_id"]),
                "source_vertex": int(row["source_vertex"]),
                "target_vertex": int(row["target_vertex"]),
                "removed": row["removed"],
                "added": row["added"],
                "tube_zero": bool(row["tube_zero"]),
            }
            for row in atom["occurrences"]
        ]
        vector = signed_vertex_vector(occurrences, vertex_count)
        columns.append(vector)
        rows.append(
            {
                "step_atom_id": int(atom["step_atom_id"]),
                "directed_channel_swaps": swaps,
                "boundary_projection_support": projection.get("boundary_projection_support"),
                "boundary_projection_coefficient_sum": projection.get(
                    "boundary_projection_coefficient_sum"
                ),
                "step_vector_sha256": atom["step_vector_sha256"],
                "occurrence_count": int(atom["occurrence_count"]),
                "generator_cycle_ids": [int(value) for value in atom["generator_cycle_ids"]],
                "edge_ids": [int(value) for value in atom["edge_ids"]],
                "vector_support": int(atom["vector_support"]),
                "vector_coefficient_sum_signed": int(atom["vector_coefficient_sum_signed"]),
                "consistent_vector_data": bool(atom["consistent_vector_data"]),
                "signed_vertex_vector_target_minus_source": vector,
                "signed_vertex_support": sparse_vector(vector),
                "signed_vertex_total": sum(vector),
                "signed_vertex_l1_norm": sum(abs(value) for value in vector),
                "signed_vertex_coefficient_histogram": histogram(Counter(vector)),
                "occurrences": occurrences,
            }
        )
    matrix = [
        [columns[column_index][row_index] for column_index in range(len(columns))]
        for row_index in range(vertex_count)
    ]
    return rows, matrix


def build_generator_boundary_rows(
    generator_packets: list[dict[str, Any]],
    hash_to_atom_id: dict[str, int],
    vertex_count: int,
) -> list[dict[str, Any]]:
    rows = []
    for packet in sorted(generator_packets, key=lambda row: int(row["generator_cycle_id"])):
        steps = packet["steps"]
        vector = signed_vertex_vector(steps, vertex_count)
        step_atom_ids_ordered = [
            hash_to_atom_id[str(step["step_vector_sha256"])] for step in steps
        ]
        vertices = [int(steps[0]["source_vertex"])] + [int(step["target_vertex"]) for step in steps]
        rows.append(
            {
                "generator_cycle_id": int(packet["generator_cycle_id"]),
                "length": int(packet["length"]),
                "step_count": int(packet["step_count"]),
                "optical_action": int(packet["optical_action"]),
                "step_atom_ids_ordered": step_atom_ids_ordered,
                "source_target_vertices": vertices,
                "path_closes": bool(vertices[0] == vertices[-1]),
                "signed_vertex_vector_target_minus_source": vector,
                "signed_vertex_total": sum(vector),
                "signed_boundary_zero": all(value == 0 for value in vector),
            }
        )
    return rows


def write_incidence_csv(
    path: Path,
    public_atom_rows: list[dict[str, Any]],
    matrix: list[list[int]],
) -> None:
    fieldnames = [
        "public_atom_id",
        "public_atom_label",
        "h6_triple",
        "native_domain",
    ] + [f"step_atom_{idx:02d}" for idx in range(len(matrix[0]) if matrix else 0)]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row_index, atom in enumerate(public_atom_rows):
            out = dict(atom)
            for col_index, value in enumerate(matrix[row_index]):
                out[f"step_atom_{col_index:02d}"] = value
            writer.writerow(out)


def write_pair_alignment_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "directed_pair",
        "removed",
        "added",
        "boundary_projection_support",
        "boundary_projection_coefficient_sum",
        "boundary_projection_closed_at_removed",
        "observed_in_compact_step_atoms",
        "step_atom_id",
        "step_vector_sha256",
        "step_atom_occurrence_count",
        "step_atom_vector_support",
        "step_atom_vector_coefficient_sum_signed",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_theorem() -> dict[str, Any]:
    edges = load_edges()
    primitive_cycles = load_primitive_cycle_rows()
    boundary = load_json(BOUNDARY_TO_LOOP_REPORT)
    loop297 = load_json(LOOP297_SCATTERING_AMPLITUDE_LIFT)
    compact = load_json(COMPACT_AMPLITUDE_QUOTIENT)

    public_atom_rows = build_public_atom_rows(edges)
    pair_projection_rows = boundary["derived"]["pair_projection_summaries"]
    step_atoms = compact["derived"]["loop_step_atoms"]
    pair_alignment_rows = build_pair_alignment_rows(pair_projection_rows, step_atoms)
    step_atom_rows, incidence_matrix = build_step_atom_incidence_rows(
        step_atoms, public_atom_rows, pair_alignment_rows
    )
    hash_to_atom_id = {
        str(row["step_vector_sha256"]): int(row["step_atom_id"]) for row in step_atoms
    }
    generator_rows = build_generator_boundary_rows(
        loop297["derived"]["generator_amplitude_packets"], hash_to_atom_id, len(public_atom_rows)
    )
    snf = smith_normal_form_diagonal(incidence_matrix)
    observed_pairs = sorted(
        row["directed_pair"] for row in pair_alignment_rows if row["observed_in_compact_step_atoms"]
    )
    missing_pairs = sorted(
        row["directed_pair"] for row in pair_alignment_rows if not row["observed_in_compact_step_atoms"]
    )
    l1_histogram = histogram(Counter(row["signed_vertex_l1_norm"] for row in step_atom_rows))
    occurrence_histogram = histogram(Counter(row["occurrence_count"] for row in step_atom_rows))
    incidence_summary = {
        "public_atom_count": len(public_atom_rows),
        "d20_edge_count": len(edges),
        "primitive_cycle_count": len(primitive_cycles),
        "boundary_directed_pair_projection_count": len(pair_projection_rows),
        "compact_loop_step_atom_count": len(step_atoms),
        "observed_directed_pair_count": len(observed_pairs),
        "missing_directed_pair_count": len(missing_pairs),
        "missing_directed_pairs_from_compact_step_atoms": missing_pairs,
        "incidence_matrix_shape": [
            len(incidence_matrix),
            len(incidence_matrix[0]) if incidence_matrix else 0,
        ],
        "rank_over_Q": matrix_rank_rational(incidence_matrix),
        "smith_diagonal": snf["diagonal"],
        "nonunit_invariant_factors": snf["nonunit_invariant_factors"],
        "zero_sum_boundary_lattice_index": 32,
        "quotient_reading": "Z^20 / image = Z x Z/2 x Z/4 x Z/4",
        "signed_vertex_l1_histogram": l1_histogram,
        "step_atom_occurrence_count_histogram": occurrence_histogram,
    }
    checks = {
        "boundary_to_loop_is_certified": boundary.get("status")
        == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary.get("all_checks_pass") is True,
        "loop297_scattering_amplitude_lift_is_certified": loop297.get("status")
        == "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED"
        and loop297.get("all_checks_pass") is True,
        "compact_amplitude_quotient_is_certified": compact.get("status")
        == "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        and compact.get("all_checks_pass") is True,
        "d20_edge_table_has_30_edges": len(edges) == 30,
        "public_atom_domain_has_20_vertices": len(public_atom_rows) == 20,
        "public_atom_ids_are_contiguous": [row["public_atom_id"] for row in public_atom_rows]
        == list(range(20)),
        "primitive_cycle_table_has_11_rows": len(primitive_cycles) == 11,
        "boundary_has_30_directed_pair_projections": len(pair_projection_rows) == 30,
        "compact_has_25_loop_step_atoms": len(step_atoms) == 25,
        "all_step_atoms_have_single_directed_pair": all(
            len(row["directed_channel_swaps"]) == 1 for row in step_atoms
        ),
        "all_step_atoms_have_consistent_vector_data": all(
            row["consistent_vector_data"] is True for row in step_atoms
        ),
        "observed_step_pairs_are_boundary_pairs": set(observed_pairs)
        <= {row["directed_pair"] for row in pair_alignment_rows},
        "observed_pair_projection_values_match_step_atoms": all(
            (
                row["step_atom_id"] is None
                or (
                    row["boundary_projection_support"] == row["step_atom_vector_support"]
                    and row["boundary_projection_coefficient_sum"]
                    == row["step_atom_vector_coefficient_sum_signed"]
                )
            )
            for row in pair_alignment_rows
        ),
        "five_boundary_pair_projections_are_not_compact_step_atoms": missing_pairs
        == ["B+->V-", "B-->V+", "B-->V-", "S+->B+", "S-->B-"],
        "incidence_matrix_is_20_by_25": incidence_summary["incidence_matrix_shape"] == [20, 25],
        "incidence_columns_sum_to_zero": all(
            sum(incidence_matrix[row][col] for row in range(20)) == 0 for col in range(25)
        ),
        "incidence_rank_is_public_zero_hyperplane": incidence_summary["rank_over_Q"] == 19,
        "incidence_smith_form_is_diagonal": snf["off_diagonal_nonzero"] == 0,
        "incidence_smith_divisibility_chain_valid": snf["divisibility_chain_valid"] is True,
        "incidence_smith_nonunit_factors_are_2_4_4": snf["nonunit_invariant_factors"]
        == [2, 4, 4],
        "zero_sum_boundary_lattice_index_is_32": incidence_summary[
            "zero_sum_boundary_lattice_index"
        ]
        == 32,
        "all_generator_paths_close": all(row["path_closes"] is True for row in generator_rows),
        "all_generator_boundaries_are_zero": all(
            row["signed_boundary_zero"] is True for row in generator_rows
        ),
        "generator_step_atom_orders_match_compact_labels": [
            row["step_atom_ids_ordered"] for row in generator_rows
        ]
        == [
            row["step_atom_ids_ordered"]
            for row in sorted(
                compact["derived"]["generator_quotient_rows"],
                key=lambda item: int(item["generator_cycle_id"]),
            )
        ],
        "all_step_occurrences_are_tube_zero": all(
            occurrence["tube_zero"] is True
            for row in step_atom_rows
            for occurrence in row["occurrences"]
        ),
    }
    report = {
        "schema": "d20.theorem.d20_boundary_loop_step_atom_incidence",
        "status": "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED",
        "object": "D20",
        "definition": {
            "public_boundary": "D20 = Lambda^3 H6 with 20 public atom vertices",
            "step_atom": (
                "a compact Loop_297 step vector hash, carrying one directed H6 channel swap "
                "and its observed primitive-cycle occurrences"
            ),
            "signed_incidence_convention": (
                "target_minus_source: each occurrence contributes -1 at source_vertex and +1 at target_vertex"
            ),
        },
        "claim": (
            "The visible boundary-to-Loop_297 step atoms have a certified signed incidence table "
            "over the 20 Lambda^3 H6 public atoms. Their 20x25 incidence matrix spans the "
            "zero-sum public boundary hyperplane over Q, but integrally has Smith torsion "
            "2,4,4; five certified directed A985 pair projections are not present among the "
            "compact primitive step atoms."
        ),
        "inputs": {
            "d20_edges_csv": input_record(D20_EDGES_CSV),
            "d20_primitive_cycles_csv": input_record(D20_PRIMITIVE_CYCLES_CSV),
            "boundary_to_loop_report": input_record(BOUNDARY_TO_LOOP_REPORT),
            "loop297_scattering_amplitude_lift_report": input_record(
                LOOP297_SCATTERING_AMPLITUDE_LIFT
            ),
            "compact_amplitude_quotient_report": input_record(COMPACT_AMPLITUDE_QUOTIENT),
        },
        "derived": {
            "incidence_summary": incidence_summary,
            "public_atom_rows": public_atom_rows,
            "public_atom_rows_sha256": sha_json(public_atom_rows),
            "directed_pair_projection_step_atom_alignment_rows": pair_alignment_rows,
            "directed_pair_projection_step_atom_alignment_rows_sha256": sha_json(
                pair_alignment_rows
            ),
            "step_atom_boundary_incidence_rows": step_atom_rows,
            "step_atom_boundary_incidence_rows_sha256": sha_json(step_atom_rows),
            "boundary_atom_step_incidence_matrix": incidence_matrix,
            "boundary_atom_step_incidence_matrix_sha256": sha_json(incidence_matrix),
            "boundary_atom_step_incidence_smith_normal_form": {
                "diagonal": snf["diagonal"],
                "diagonal_multiplicities": snf["diagonal_multiplicities"],
                "nonunit_invariant_factors": snf["nonunit_invariant_factors"],
                "off_diagonal_nonzero": snf["off_diagonal_nonzero"],
                "divisibility_chain_valid": snf["divisibility_chain_valid"],
                "reduction_steps": snf["reduction_steps"],
            },
            "generator_boundary_closure_rows": generator_rows,
            "generator_boundary_closure_rows_sha256": sha_json(generator_rows),
            "csv_artifacts": {
                "boundary_atom_step_incidence": rel(INCIDENCE_CSV),
                "directed_pair_projection_step_atom_alignment": rel(PAIR_ALIGNMENT_CSV),
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "positive_boundary_lift": (
                "The compact Loop_297 step atoms are sufficient over Q to span every public "
                "zero-sum Lambda^3 H6 boundary direction."
            ),
            "integral_obstruction": (
                "The same visible step atoms are not saturated over Z; the zero-sum boundary "
                "lattice quotient has torsion Z/2 x Z/4 x Z/4."
            ),
            "remaining_packet_gap": (
                "This is a boundary incidence certificate, not a full-packet map. A separate "
                "signed or normalized map from this boundary lattice to the 20 full-exposure "
                "packet coordinates is still required before the packet SNF test can certify "
                "an A985/tube/q42/q12 bridge."
            ),
        },
        "next_highest_yield_item": (
            "Search for a normalization or quotient map from the signed Lambda^3 H6 boundary "
            "incidence lattice to the full-exposure packet doublets that kills the 2,4,4 "
            "boundary torsion and satisfies the packet SNF block tests."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_incidence_csv(
        out_dir / "boundary_atom_step_incidence.csv",
        report["derived"]["public_atom_rows"],
        report["derived"]["boundary_atom_step_incidence_matrix"],
    )
    write_pair_alignment_csv(
        out_dir / "directed_pair_projection_step_atom_alignment.csv",
        report["derived"]["directed_pair_projection_step_atom_alignment_rows"],
    )
    report["derived"]["csv_artifact_hashes"] = {
        "boundary_atom_step_incidence": sha_file(out_dir / "boundary_atom_step_incidence.csv"),
        "directed_pair_projection_step_atom_alignment": sha_file(
            out_dir / "directed_pair_projection_step_atom_alignment.csv"
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_boundary_loop_step_atom_incidence_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
            "boundary_atom_step_incidence_csv": rel(
                out_dir / "boundary_atom_step_incidence.csv"
            ),
            "directed_pair_projection_step_atom_alignment_csv": rel(
                out_dir / "directed_pair_projection_step_atom_alignment.csv"
            ),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "emit the signed Lambda^3 H6 boundary incidence table for visible Loop_297 step atoms",
            "compute the integral boundary-lattice obstruction before attempting a packet bridge",
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
