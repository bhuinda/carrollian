from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
        signature_class_ids,
    )
    from .derive_c985_d20_signature_class_nerve import histogram
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
        signature_class_ids,
    )
    from derive_c985_d20_signature_class_nerve import histogram
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_hyperbolic_chart_atlas"
STATUS = "C985_D20_HYPERBOLIC_CHART_ATLAS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

NERVE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_signature_class_nerve"
FILTRATION_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_poincare_landmark_filtration"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"

NERVE_REPORT = NERVE_DIR / "report.json"
NERVE_JSON = NERVE_DIR / "signature_class_nerve.json"
NERVE_TABLES = NERVE_DIR / "signature_class_nerve_tables.npz"
FILTRATION_REPORT = FILTRATION_DIR / "report.json"
FILTRATION_TABLES = FILTRATION_DIR / "filtration_tables.npz"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_hyperbolic_chart_atlas.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_hyperbolic_chart_atlas.py"

TRANSITION_COLUMNS = [
    "source_seed",
    "target_seed",
    "atom_id",
    "source_local_rank",
    "target_local_rank",
    "rank_delta",
    "source_chart_size",
    "target_chart_size",
]

PAIR_COLUMNS = [
    "chart_i",
    "chart_j",
    "intersection_atom_count",
    "intersection_signature_class_count",
    "signature_deficit",
    "intersection_tensor_path_coefficient_mass",
    "rank_displacement_l1",
    "rank_displacement_max",
]


def atom_label(atlas: dict[str, Any], atom_id: int) -> str:
    return "{" + ",".join(atlas["atom_rows"][atom_id]["h6_triple"]) + "}"


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def signature_union_count(atom_ids: set[int], signature_sets: list[set[int]]) -> int:
    if not atom_ids:
        return 0
    return len(set().union(*(signature_sets[atom_id] for atom_id in sorted(atom_ids))))


def exact_atom_covers(chart_atom_incidence: np.ndarray) -> tuple[int, list[tuple[int, ...]]]:
    atom_count = int(chart_atom_incidence.shape[1])
    all_atoms = set(range(atom_count))
    chart_sets = [
        set(int(atom_id) for atom_id in np.flatnonzero(chart_atom_incidence[chart_id]))
        for chart_id in range(int(chart_atom_incidence.shape[0]))
    ]
    for size in range(1, len(chart_sets) + 1):
        covers = [
            combo
            for combo in itertools.combinations(range(len(chart_sets)), size)
            if set().union(*(chart_sets[chart_id] for chart_id in combo)) == all_atoms
        ]
        if covers:
            return size, covers
    raise ValueError("chart family does not cover the atom domain")


def cover_key(
    combo: tuple[int, ...],
    chart_sizes: np.ndarray,
    chart_intersection_signature_counts: np.ndarray,
) -> tuple[int, int, int, tuple[int, ...]]:
    pair_deficits = [
        233 - int(chart_intersection_signature_counts[i, j])
        for i, j in itertools.combinations(combo, 2)
    ]
    max_pair_deficit = max(pair_deficits) if pair_deficits else 0
    return (
        len(combo),
        int(sum(int(chart_sizes[chart_id]) for chart_id in combo)),
        max_pair_deficit,
        combo,
    )


def local_rank_map(chart_atoms: list[int]) -> dict[int, int]:
    return {int(atom_id): rank for rank, atom_id in enumerate(chart_atoms, start=1)}


def build_transition_data(
    selected_chart_ids: tuple[int, ...],
    chart_vertices: list[dict[str, Any]],
    chart_atom_incidence: np.ndarray,
    chart_intersection_signature_counts: np.ndarray,
    chart_intersection_tensor_mass: np.ndarray,
    signature_sets: list[set[int]],
    atlas: dict[str, Any],
) -> dict[str, Any]:
    chart_atoms = {
        int(vertex["seed_atom_id"]): [int(atom_id) for atom_id in vertex["atom_ids"]]
        for vertex in chart_vertices
    }
    chart_sizes = {
        chart_id: len(chart_atoms[chart_id])
        for chart_id in selected_chart_ids
    }
    rank_maps = {
        chart_id: local_rank_map(chart_atoms[chart_id])
        for chart_id in selected_chart_ids
    }

    transition_rows: list[dict[str, Any]] = []
    transition_array_rows: list[list[int]] = []
    pair_rows: list[dict[str, Any]] = []
    pair_array_rows: list[list[int]] = []
    for source_seed, target_seed in itertools.permutations(selected_chart_ids, 2):
        common_atoms = sorted(set(chart_atoms[source_seed]) & set(chart_atoms[target_seed]))
        for atom_id in common_atoms:
            source_rank = rank_maps[source_seed][atom_id]
            target_rank = rank_maps[target_seed][atom_id]
            row = {
                "source_seed": source_seed,
                "target_seed": target_seed,
                "atom_id": atom_id,
                "atom_label": atom_label(atlas, atom_id),
                "source_local_rank": source_rank,
                "target_local_rank": target_rank,
                "rank_delta": target_rank - source_rank,
                "source_chart_size": chart_sizes[source_seed],
                "target_chart_size": chart_sizes[target_seed],
            }
            transition_rows.append(row)
            transition_array_rows.append([int(row[column]) for column in TRANSITION_COLUMNS])

    for chart_i, chart_j in itertools.combinations(selected_chart_ids, 2):
        common_atoms = sorted(set(chart_atoms[chart_i]) & set(chart_atoms[chart_j]))
        deltas = [
            rank_maps[chart_j][atom_id] - rank_maps[chart_i][atom_id]
            for atom_id in common_atoms
        ]
        row = {
            "chart_i": chart_i,
            "chart_j": chart_j,
            "chart_i_label": atom_label(atlas, chart_i),
            "chart_j_label": atom_label(atlas, chart_j),
            "intersection_atom_count": len(common_atoms),
            "intersection_atom_ids": common_atoms,
            "intersection_atom_labels": [atom_label(atlas, atom_id) for atom_id in common_atoms],
            "intersection_signature_class_count": int(
                chart_intersection_signature_counts[chart_i, chart_j]
            ),
            "signature_deficit": 233 - int(chart_intersection_signature_counts[chart_i, chart_j]),
            "intersection_tensor_path_coefficient_mass": int(
                chart_intersection_tensor_mass[chart_i, chart_j]
            ),
            "rank_displacement_l1": int(sum(abs(delta) for delta in deltas)),
            "rank_displacement_max": int(max(abs(delta) for delta in deltas)),
        }
        pair_rows.append(row)
        pair_array_rows.append([int(row[column]) for column in PAIR_COLUMNS])

    triple_atoms = sorted(
        set.intersection(*(set(chart_atoms[chart_id]) for chart_id in selected_chart_ids))
    )
    cycle = list(selected_chart_ids)
    cocycle_rows: list[dict[str, Any]] = []
    cocycle_array_rows: list[list[int]] = []
    for atom_id in triple_atoms:
        delta_0 = rank_maps[cycle[1]][atom_id] - rank_maps[cycle[0]][atom_id]
        delta_1 = rank_maps[cycle[2]][atom_id] - rank_maps[cycle[1]][atom_id]
        delta_2 = rank_maps[cycle[0]][atom_id] - rank_maps[cycle[2]][atom_id]
        row = {
            "atom_id": atom_id,
            "atom_label": atom_label(atlas, atom_id),
            "delta_0_to_1": delta_0,
            "delta_1_to_2": delta_1,
            "delta_2_to_0": delta_2,
            "cycle_sum": delta_0 + delta_1 + delta_2,
        }
        cocycle_rows.append(row)
        cocycle_array_rows.append(
            [atom_id, int(delta_0), int(delta_1), int(delta_2), int(row["cycle_sum"])]
        )

    selected_incidence = np.asarray(
        [chart_atom_incidence[chart_id] for chart_id in selected_chart_ids],
        dtype=np.int8,
    )
    atom_cover_counts = selected_incidence.sum(axis=0).astype(np.int64)
    triple_signature_count = signature_union_count(set(triple_atoms), signature_sets)
    triple_mass = int(
        sum(int(atlas["atom_rows"][atom_id]["tensor_path_coefficient_mass"]) for atom_id in triple_atoms)
    )

    return {
        "transition_rows": transition_rows,
        "transition_array": np.asarray(transition_array_rows, dtype=np.int64),
        "pair_rows": pair_rows,
        "pair_array": np.asarray(pair_array_rows, dtype=np.int64),
        "cocycle_rows": cocycle_rows,
        "cocycle_array": np.asarray(cocycle_array_rows, dtype=np.int64),
        "selected_incidence": selected_incidence,
        "atom_cover_counts": atom_cover_counts,
        "triple_atoms": np.asarray(triple_atoms, dtype=np.int64),
        "triple_signature_count": triple_signature_count,
        "triple_mass": triple_mass,
        "chart_atoms": chart_atoms,
    }


def build_payloads() -> dict[str, Any]:
    nerve_report = load_json(NERVE_REPORT)
    nerve = load_json(NERVE_JSON)
    filtration_report = load_json(FILTRATION_REPORT)
    atlas = load_json(ATLAS_JSON)
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    signature_sets = atom_signature_sets(atlas, relation_records, signature_class_ids(relation_records))
    nerve_tables = np.load(NERVE_TABLES, allow_pickle=False)
    chart_rows = np.asarray(nerve_tables["chart_rows"], dtype=np.int64)
    chart_atom_incidence = np.asarray(nerve_tables["chart_atom_incidence"], dtype=np.int8)
    chart_intersection_signature_counts = np.asarray(
        nerve_tables["chart_intersection_signature_counts"],
        dtype=np.int64,
    )
    chart_intersection_tensor_mass = np.asarray(
        nerve_tables["chart_intersection_tensor_mass"],
        dtype=np.int64,
    )

    chart_sizes = chart_rows[:, 1].astype(np.int64)
    minimum_cover_size, minimum_covers = exact_atom_covers(chart_atom_incidence)
    selected_chart_ids = sorted(
        minimum_covers,
        key=lambda combo: cover_key(combo, chart_sizes, chart_intersection_signature_counts),
    )[0]
    transition_data = build_transition_data(
        selected_chart_ids,
        nerve["chart_vertices"],
        chart_atom_incidence,
        chart_intersection_signature_counts,
        chart_intersection_tensor_mass,
        signature_sets,
        atlas,
    )

    selected_union = sorted(
        set().union(*(set(transition_data["chart_atoms"][chart_id]) for chart_id in selected_chart_ids))
    )
    cover_summaries = [
        {
            "chart_ids": list(combo),
            "chart_labels": [atom_label(atlas, chart_id) for chart_id in combo],
            "chart_size_sum": int(sum(int(chart_sizes[chart_id]) for chart_id in combo)),
            "maximum_pair_signature_deficit": max(
                233 - int(chart_intersection_signature_counts[i, j])
                for i, j in itertools.combinations(combo, 2)
            ),
        }
        for combo in sorted(minimum_covers)
    ]

    atlas_json = {
        "schema": "c985.d20_hyperbolic_chart_atlas@1",
        "object": "d20",
        "atlas_rule": {
            "chart_source": "first-full-coverage Poincare balls from the certified signature-class nerve",
            "selection": "exact minimum set cover of the 20 atom domain; ties use chart-size sum, maximum pair signature deficit, then lexicographic chart ids",
            "transition_map": "on chart overlaps, preserve atom id and record the change of local Poincare-shell rank",
            "cocycle": "around the selected triple overlap, rank-delta transition sums must vanish atomwise",
        },
        "source_nerve_certificate": nerve_report.get("certificate_sha256"),
        "minimum_atom_cover_size": minimum_cover_size,
        "minimum_atom_cover_count": len(minimum_covers),
        "minimum_atom_covers": cover_summaries,
        "selected_chart_ids": list(selected_chart_ids),
        "selected_chart_labels": [atom_label(atlas, chart_id) for chart_id in selected_chart_ids],
        "selected_union_atom_ids": selected_union,
        "selected_union_atom_labels": [atom_label(atlas, atom_id) for atom_id in selected_union],
        "selected_atom_cover_histogram": histogram(
            [int(x) for x in transition_data["atom_cover_counts"].tolist()]
        ),
        "selected_unique_atom_ids": [
            atom_id
            for atom_id, count in enumerate(transition_data["atom_cover_counts"].tolist())
            if int(count) == 1
        ],
        "selected_unique_atom_labels": [
            atom_label(atlas, atom_id)
            for atom_id, count in enumerate(transition_data["atom_cover_counts"].tolist())
            if int(count) == 1
        ],
        "pair_transitions": transition_data["pair_rows"],
        "triple_overlap": {
            "chart_ids": list(selected_chart_ids),
            "atom_count": int(transition_data["triple_atoms"].size),
            "atom_ids": [int(x) for x in transition_data["triple_atoms"].tolist()],
            "atom_labels": [atom_label(atlas, int(x)) for x in transition_data["triple_atoms"].tolist()],
            "signature_class_count": int(transition_data["triple_signature_count"]),
            "tensor_path_coefficient_mass": int(transition_data["triple_mass"]),
        },
        "transition_cocycle": transition_data["cocycle_rows"],
    }

    pair_array = transition_data["pair_array"]
    transition_array = transition_data["transition_array"]
    atom_cover_counts = transition_data["atom_cover_counts"]
    cocycle_array = transition_data["cocycle_array"]
    checks = {
        "signature_class_nerve_report_certified": nerve_report.get("status")
        == "C985_D20_SIGNATURE_CLASS_NERVE_CERTIFIED",
        "landmark_filtration_report_certified": filtration_report.get("status")
        == "C985_D20_POINCARE_LANDMARK_FILTRATION_CERTIFIED",
        "source_chart_count_is_20": int(chart_atom_incidence.shape[0]) == 20,
        "exact_minimum_atom_cover_size_is_3": minimum_cover_size == 3,
        "exact_minimum_atom_cover_count_is_4": len(minimum_covers) == 4,
        "selected_chart_ids_are_0_2_10": list(selected_chart_ids) == [0, 2, 10],
        "selected_chart_size_sum_is_39": int(sum(int(chart_sizes[x]) for x in selected_chart_ids)) == 39,
        "selected_atlas_covers_all_20_atoms": selected_union == list(range(20)),
        "selected_pair_count_is_3": int(pair_array.shape[0]) == 3,
        "selected_pair_min_atom_intersection_is_6": int(pair_array[:, 2].min()) == 6,
        "selected_pair_min_signature_intersection_is_221": int(pair_array[:, 3].min()) == 221,
        "selected_pair_full_signature_intersection_count_is_2": int(np.count_nonzero(pair_array[:, 3] == 233)) == 2,
        "undirected_transition_atom_count_is_25": int(pair_array[:, 2].sum()) == 25,
        "ordered_transition_record_count_is_50": int(transition_array.shape[0]) == 50,
        "triple_overlap_atom_count_is_6": int(transition_data["triple_atoms"].size) == 6,
        "triple_overlap_signature_count_is_221": int(transition_data["triple_signature_count"]) == 221,
        "triple_overlap_mass_is_344576": int(transition_data["triple_mass"]) == 344576,
        "atom_cover_histogram_is_7_7_6": histogram([int(x) for x in atom_cover_counts.tolist()])
        == [
            {"value": 1, "count": 7},
            {"value": 2, "count": 7},
            {"value": 3, "count": 6},
        ],
        "unique_atom_count_is_7": int(np.count_nonzero(atom_cover_counts == 1)) == 7,
        "transition_rank_displacement_l1_sum_is_125": int(pair_array[:, 6].sum()) == 125,
        "transition_rank_displacement_max_is_12": int(pair_array[:, 7].max()) == 12,
        "transition_cocycle_failure_count_is_0": int(np.count_nonzero(cocycle_array[:, 4])) == 0,
    }

    witness = {
        "source_chart_count": 20,
        "minimum_atom_cover_size": minimum_cover_size,
        "minimum_atom_cover_count": len(minimum_covers),
        "selected_chart_ids": list(selected_chart_ids),
        "selected_chart_size_sum": int(sum(int(chart_sizes[x]) for x in selected_chart_ids)),
        "selected_union_atom_count": len(selected_union),
        "selected_pair_count": int(pair_array.shape[0]),
        "selected_pair_atom_intersection_min": int(pair_array[:, 2].min()),
        "selected_pair_signature_intersection_min": int(pair_array[:, 3].min()),
        "selected_pair_full_signature_intersection_count": int(np.count_nonzero(pair_array[:, 3] == 233)),
        "undirected_transition_atom_count": int(pair_array[:, 2].sum()),
        "ordered_transition_record_count": int(transition_array.shape[0]),
        "triple_overlap_atom_ids": [int(x) for x in transition_data["triple_atoms"].tolist()],
        "triple_overlap_signature_count": int(transition_data["triple_signature_count"]),
        "triple_overlap_mass": int(transition_data["triple_mass"]),
        "unique_atom_count": int(np.count_nonzero(atom_cover_counts == 1)),
        "transition_rank_displacement_l1_sum": int(pair_array[:, 6].sum()),
        "transition_rank_displacement_max": int(pair_array[:, 7].max()),
        "transition_cocycle_failure_count": int(np.count_nonzero(cocycle_array[:, 4])),
        "selected_chart_ids_sha256": sha_array(np.asarray(selected_chart_ids, dtype=np.int64)),
        "selected_incidence_sha256": sha_array(transition_data["selected_incidence"]),
        "atom_cover_counts_sha256": sha_array(atom_cover_counts),
        "transition_pair_records_sha256": sha_array(pair_array),
        "ordered_transition_records_sha256": sha_array(transition_array),
        "transition_cocycle_records_sha256": sha_array(cocycle_array),
    }

    certificate = {
        "schema": "c985.d20_hyperbolic_chart_atlas_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_HYPERBOLIC_CHART_ATLAS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "three first-full-coverage Poincare charts suffice to cover all 20 d20 atoms",
            "the canonical minimum atlas is generated by chart seeds [0,2,10]",
            "all selected chart overlaps retain at least six atoms and 221 relation-signature classes",
            "two selected chart overlaps still carry all 233 relation-signature classes",
            "rank-transition maps compose with zero cocycle on the six-atom triple overlap",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_hyperbolic_chart_atlas@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified signature-class nerve admits a canonical three-chart "
            "hyperbolic atlas covering all 20 d20 atoms, with reproducible "
            "rank-transition maps on overlaps and a zero transition cocycle on "
            "the triple overlap."
        ),
        "stage_protocol": {
            "draft": "use the certified signature-class nerve charts as atlas candidates",
            "witness": "solve the exact chart set-cover problem and materialize overlap transition maps",
            "coherence": "check cover minimality, overlap signature floors, rank displacement, and triple-overlap cocycle",
            "closure": "certify a small hyperbolic chart atlas without claiming a packet bridge or categorical enrichment",
            "emit": "emit atlas JSON/CSV/NPZ, certificate, report, and next transition-deepening target",
        },
        "inputs": {
            "signature_class_nerve_report": input_entry(
                NERVE_REPORT,
                {
                    "status": nerve_report.get("status"),
                    "certificate_sha256": nerve_report.get("certificate_sha256"),
                },
            ),
            "signature_class_nerve": input_entry(NERVE_JSON),
            "signature_class_nerve_tables": input_entry(NERVE_TABLES),
            "filtration_report": input_entry(
                FILTRATION_REPORT,
                {
                    "status": filtration_report.get("status"),
                    "certificate_sha256": filtration_report.get("certificate_sha256"),
                },
            ),
            "filtration_tables": input_entry(FILTRATION_TABLES),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "hyperbolic_chart_atlas": relpath(OUT_DIR / "hyperbolic_chart_atlas.json"),
            "atlas_transition_maps_csv": relpath(OUT_DIR / "atlas_transition_maps.csv"),
            "hyperbolic_chart_atlas_tables": relpath(OUT_DIR / "hyperbolic_chart_atlas_tables.npz"),
            "atlas_certificate": relpath(OUT_DIR / "atlas_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exact minimum full-coverage chart cover size and canonical selected cover",
                "selected chart incidence and atom cover counts",
                "all ordered local-rank transition records on selected chart overlaps",
                "selected pair overlap signature/mass/rank-displacement summaries",
                "zero transition cocycle on the selected triple overlap",
            ],
            "does_not_certify_because_not_required": [
                "transition maps between non-selected charts",
                "optimality among non-Poincare or non-full-coverage charts",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the three-chart atlas transition maps to build a transition "
            "groupoid, then compare its cycles with the C985 associator and "
            "pentagon normal-form data."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_hyperbolic_chart_atlas_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified signature-class nerve and filtration tables",
            "solve exact minimum chart cover over the 20 d20 atoms",
            "select the canonical minimum atlas by deterministic tie-break",
            "materialize local-rank transition maps on selected chart overlaps",
            "verify overlap floors and the selected triple-overlap transition cocycle",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "hyperbolic_chart_atlas": atlas_json,
        "atlas_transition_maps_csv": csv_text(TRANSITION_COLUMNS, transition_data["transition_rows"]),
        "selected_chart_ids": np.asarray(selected_chart_ids, dtype=np.int64),
        "selected_incidence": transition_data["selected_incidence"],
        "atom_cover_counts": atom_cover_counts,
        "transition_pair_records": pair_array,
        "ordered_transition_records": transition_array,
        "transition_cocycle_records": cocycle_array,
        "triple_overlap_atom_ids": transition_data["triple_atoms"],
        "atlas_certificate": certificate,
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
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "hyperbolic_chart_atlas.json", payloads["hyperbolic_chart_atlas"])
    (OUT_DIR / "atlas_transition_maps.csv").write_text(
        payloads["atlas_transition_maps_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "hyperbolic_chart_atlas_tables.npz",
        selected_chart_ids=payloads["selected_chart_ids"],
        selected_incidence=payloads["selected_incidence"],
        atom_cover_counts=payloads["atom_cover_counts"],
        transition_pair_records=payloads["transition_pair_records"],
        ordered_transition_records=payloads["ordered_transition_records"],
        transition_cocycle_records=payloads["transition_cocycle_records"],
        triple_overlap_atom_ids=payloads["triple_overlap_atom_ids"],
    )
    write_json(OUT_DIR / "atlas_certificate.json", payloads["atlas_certificate"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "minimum_atom_cover_size": witness["minimum_atom_cover_size"],
                "selected_chart_ids": witness["selected_chart_ids"],
                "selected_pair_signature_intersection_min": witness[
                    "selected_pair_signature_intersection_min"
                ],
                "transition_cocycle_failure_count": witness["transition_cocycle_failure_count"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
