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
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
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
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_normal_form_words"
STATUS = "C985_D20_NORMAL_FORM_WORDS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GROUPOID_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_transition_groupoid"
CHART_ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_hyperbolic_chart_atlas"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"

GROUPOID_REPORT = GROUPOID_DIR / "report.json"
GROUPOID_JSON = GROUPOID_DIR / "transition_groupoid.json"
GROUPOID_TABLES = GROUPOID_DIR / "transition_groupoid_tables.npz"
CHART_ATLAS_REPORT = CHART_ATLAS_DIR / "report.json"
CHART_ATLAS_JSON = CHART_ATLAS_DIR / "hyperbolic_chart_atlas.json"
ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
ATLAS_NPZ = ATLAS_DIR / "d20_boundary_invariant_atlas.npz"
GEOMETRY_REPORT = GEOMETRY_DIR / "report.json"
OBJECT_SECTOR_CUBES = GEOMETRY_DIR / "object_sector_cubes.npz"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_normal_form_words.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_normal_form_words.py"

WORD_COLUMNS = [
    "word_id",
    "start_seed",
    "middle_seed",
    "last_seed",
    "atom_id",
    "start_local_rank",
    "middle_local_rank",
    "last_local_rank",
    "cycle_delta_sum",
    "sector_coverage_count",
    "tensor_path_support",
    "tensor_path_coefficient_mass",
    "internal_signature_class_count",
]

ATOM_COLUMNS = [
    "atom_id",
    "sector_coverage_with_chart_cycle",
    "tensor_path_support_from_cubes",
    "tensor_path_support_from_atlas",
    "tensor_path_coefficient_mass_from_cubes",
    "tensor_path_coefficient_mass_from_atlas",
    "internal_signature_class_count",
    "cycle_word_count",
]


def atom_label(atlas: dict[str, Any], atom_id: int) -> str:
    return "{" + ",".join(atlas["atom_rows"][atom_id]["h6_triple"]) + "}"


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def histogram(values: list[int]) -> list[dict[str, int]]:
    counts: dict[int, int] = {}
    for value in values:
        counts[int(value)] = counts.get(int(value), 0) + 1
    return [
        {"value": int(value), "count": int(count)}
        for value, count in sorted(counts.items())
    ]


def transition_lookup(ordered_transition_records: np.ndarray) -> dict[tuple[int, int, int], dict[str, int]]:
    columns = [
        "source_seed",
        "target_seed",
        "atom_id",
        "source_local_rank",
        "target_local_rank",
        "rank_delta",
        "source_chart_size",
        "target_chart_size",
    ]
    lookup: dict[tuple[int, int, int], dict[str, int]] = {}
    for row in ordered_transition_records:
        record = {
            column: int(row[index])
            for index, column in enumerate(columns)
        }
        lookup[(record["source_seed"], record["target_seed"], record["atom_id"])] = record
    return lookup


def atom_tensor_totals_from_cubes(
    atom: dict[str, Any],
    support_cube: np.ndarray,
    coefficient_cube: np.ndarray,
) -> tuple[int, int]:
    label_to_id = {label: index for index, label in enumerate(OBJECT_LABELS)}
    sector_ids = [label_to_id[label] for label in atom["h6_triple"]]
    paths = itertools.permutations(sector_ids, 3)
    support = 0
    mass = 0
    for path in paths:
        support += int(support_cube[path])
        mass += int(coefficient_cube[path])
    return support, mass


def signature_union_count(atom_ids: set[int], signature_sets: list[set[int]]) -> int:
    if not atom_ids:
        return 0
    return len(set().union(*(signature_sets[atom_id] for atom_id in sorted(atom_ids))))


def build_word_payload(
    atlas: dict[str, Any],
    cycle_records: np.ndarray,
    ordered_transition_records: np.ndarray,
    support_cube: np.ndarray,
    coefficient_cube: np.ndarray,
    signature_sets: list[set[int]],
) -> dict[str, Any]:
    lookup = transition_lookup(ordered_transition_records)
    selected_chart_cycle = [0, 2, 10]
    chart_sector_union: set[str] = set()
    for chart_id in selected_chart_cycle:
        chart_sector_union.update(atlas["atom_rows"][chart_id]["h6_triple"])

    rows: list[dict[str, Any]] = []
    word_array_rows: list[list[int]] = []
    for word_id, cycle in enumerate(cycle_records):
        start_seed, middle_seed, last_seed, atom_id, cycle_delta_sum = [int(x) for x in cycle]
        first = lookup[(start_seed, middle_seed, atom_id)]
        second = lookup[(middle_seed, last_seed, atom_id)]
        third = lookup[(last_seed, start_seed, atom_id)]
        atom = atlas["atom_rows"][atom_id]
        support, mass = atom_tensor_totals_from_cubes(atom, support_cube, coefficient_cube)
        sector_coverage = len(chart_sector_union | set(atom["h6_triple"]))
        row = {
            "word_id": word_id,
            "normal_form_word": (
                f"{start_seed}->{middle_seed}->{last_seed}->{start_seed}"
                f"::atom={atom_id}::nf=({atom_id},{start_seed},{first['source_local_rank']})"
            ),
            "start_seed": start_seed,
            "middle_seed": middle_seed,
            "last_seed": last_seed,
            "atom_id": atom_id,
            "atom_label": atom_label(atlas, atom_id),
            "atom_path": "|".join(atom["h6_triple"]),
            "start_local_rank": int(first["source_local_rank"]),
            "middle_local_rank": int(first["target_local_rank"]),
            "last_local_rank": int(second["target_local_rank"]),
            "return_local_rank": int(third["target_local_rank"]),
            "cycle_delta_sum": cycle_delta_sum,
            "sector_coverage_count": sector_coverage,
            "tensor_path_support": support,
            "tensor_path_coefficient_mass": mass,
            "internal_signature_class_count": int(atom["internal_signature_class_count"]),
        }
        rows.append(row)
        word_array_rows.append([int(row[column]) for column in WORD_COLUMNS])

    unique_atom_ids = sorted(set(int(row["atom_id"]) for row in rows))
    atom_rows: list[dict[str, Any]] = []
    atom_array_rows: list[list[int]] = []
    for atom_id in unique_atom_ids:
        atom = atlas["atom_rows"][atom_id]
        support, mass = atom_tensor_totals_from_cubes(atom, support_cube, coefficient_cube)
        sector_coverage = len(chart_sector_union | set(atom["h6_triple"]))
        row = {
            "atom_id": atom_id,
            "atom_label": atom_label(atlas, atom_id),
            "atom_path": "|".join(atom["h6_triple"]),
            "sector_coverage_with_chart_cycle": sector_coverage,
            "tensor_path_support_from_cubes": support,
            "tensor_path_support_from_atlas": int(atom["tensor_path_support"]),
            "tensor_path_coefficient_mass_from_cubes": mass,
            "tensor_path_coefficient_mass_from_atlas": int(atom["tensor_path_coefficient_mass"]),
            "internal_signature_class_count": int(atom["internal_signature_class_count"]),
            "cycle_word_count": sum(1 for word in rows if int(word["atom_id"]) == atom_id),
        }
        atom_rows.append(row)
        atom_array_rows.append([int(row[column]) for column in ATOM_COLUMNS])

    return {
        "word_rows": rows,
        "word_array": np.asarray(word_array_rows, dtype=np.int64),
        "atom_rows": atom_rows,
        "atom_array": np.asarray(atom_array_rows, dtype=np.int64),
        "chart_sector_union": sorted(chart_sector_union),
        "unique_atom_ids": unique_atom_ids,
        "unique_atom_signature_class_count": signature_union_count(set(unique_atom_ids), signature_sets),
    }


def build_payloads() -> dict[str, Any]:
    groupoid_report = load_json(GROUPOID_REPORT)
    groupoid = load_json(GROUPOID_JSON)
    chart_report = load_json(CHART_ATLAS_REPORT)
    chart_atlas = load_json(CHART_ATLAS_JSON)
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    geometry_report = load_json(GEOMETRY_REPORT)
    groupoid_tables = np.load(GROUPOID_TABLES, allow_pickle=False)
    ordered_transition_records = np.asarray(groupoid_tables["ordered_transition_records"], dtype=np.int64)
    cycle_records = np.asarray(groupoid_tables["cycle_records"], dtype=np.int64)
    geometry = np.load(OBJECT_SECTOR_CUBES, allow_pickle=False)
    support_cube = np.asarray(geometry["support_cube"], dtype=np.int64)
    coefficient_cube = np.asarray(geometry["coefficient_cube"], dtype=np.int64)
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    signature_sets = atom_signature_sets(atlas, relation_records, signature_class_ids(relation_records))
    word_payload = build_word_payload(
        atlas,
        cycle_records,
        ordered_transition_records,
        support_cube,
        coefficient_cube,
        signature_sets,
    )

    word_rows = word_payload["word_rows"]
    word_array = word_payload["word_array"]
    atom_rows = word_payload["atom_rows"]
    atom_array = word_payload["atom_array"]
    word_sector_hist = histogram([int(row["sector_coverage_count"]) for row in word_rows])
    atom_sector_hist = histogram([int(row["sector_coverage_with_chart_cycle"]) for row in atom_rows])
    unique_support_total = int(sum(row["tensor_path_support_from_cubes"] for row in atom_rows))
    unique_mass_total = int(sum(row["tensor_path_coefficient_mass_from_cubes"] for row in atom_rows))
    word_support_total = int(sum(row["tensor_path_support"] for row in word_rows))
    word_mass_total = int(sum(row["tensor_path_coefficient_mass"] for row in word_rows))
    atlas_triple_overlap = chart_atlas.get("triple_overlap", {})
    groupoid_comparison = groupoid.get("categorical_normal_form_comparison", {})

    normal_words = {
        "schema": "c985.d20_normal_form_words@1",
        "object": "d20",
        "word_rule": {
            "source": "directed transition groupoid cycles on the canonical three-chart atlas",
            "normal_form": "cycle word plus preserved atom id and terminal local rank",
            "tensor_sector_comparison": "each word's atom path is evaluated against the certified object-sector support and coefficient cubes",
        },
        "source_transition_groupoid_certificate": groupoid_report.get("certificate_sha256"),
        "source_tensor_geometry_certificate": geometry_report.get("certificate_sha256"),
        "chart_cycle_sector_union": word_payload["chart_sector_union"],
        "normal_form_words": word_rows,
        "unique_cycle_atoms": atom_rows,
        "summary": {
            "word_count": len(word_rows),
            "unique_atom_count": len(atom_rows),
            "word_sector_coverage_histogram": word_sector_hist,
            "unique_atom_sector_coverage_histogram": atom_sector_hist,
            "unique_atom_signature_class_count": word_payload["unique_atom_signature_class_count"],
            "unique_atom_tensor_path_support": unique_support_total,
            "unique_atom_tensor_path_coefficient_mass": unique_mass_total,
            "word_multiplicity_tensor_path_support": word_support_total,
            "word_multiplicity_tensor_path_coefficient_mass": word_mass_total,
            "groupoid_cycle_holonomy_failures": groupoid_report.get("witness", {}).get(
                "cycle_holonomy_failure_count"
            ),
            "pentagon_chain_normal_form": groupoid_comparison.get("pentagon_chain_normal_form"),
        },
    }

    checks = {
        "transition_groupoid_report_certified": groupoid_report.get("status")
        == "C985_D20_TRANSITION_GROUPOID_CERTIFIED",
        "chart_atlas_report_certified": chart_report.get("status")
        == "C985_D20_HYPERBOLIC_CHART_ATLAS_CERTIFIED",
        "boundary_atlas_report_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "tensor_geometry_report_certified": geometry_report.get("status")
        == "C985_TENSOR_GEOMETRY_INVARIANTS_CERTIFIED",
        "cycle_record_count_is_36": int(cycle_records.shape[0]) == 36,
        "normal_form_word_count_is_36": len(word_rows) == 36,
        "unique_cycle_atom_count_is_6": len(atom_rows) == 6,
        "all_cycle_delta_sums_are_zero": bool(np.all(word_array[:, 8] == 0)),
        "each_unique_atom_appears_in_6_words": bool(np.all(atom_array[:, 7] == 6)),
        "word_sector_coverage_histogram_is_24_five_12_six": word_sector_hist
        == [{"value": 5, "count": 24}, {"value": 6, "count": 12}],
        "unique_atom_sector_coverage_histogram_is_4_five_2_six": atom_sector_hist
        == [{"value": 5, "count": 4}, {"value": 6, "count": 2}],
        "object_sector_cube_recomputes_atlas_support": bool(np.all(atom_array[:, 2] == atom_array[:, 3])),
        "object_sector_cube_recomputes_atlas_mass": bool(np.all(atom_array[:, 4] == atom_array[:, 5])),
        "unique_atom_signature_class_count_is_221": word_payload["unique_atom_signature_class_count"] == 221,
        "unique_atom_tensor_path_support_is_216432": unique_support_total == 216432,
        "unique_atom_tensor_path_mass_is_344576": unique_mass_total == 344576,
        "unique_atom_mass_matches_chart_atlas_triple_overlap": unique_mass_total
        == int(atlas_triple_overlap.get("tensor_path_coefficient_mass", -1)),
        "word_multiplicity_mass_is_6_times_unique_mass": word_mass_total == 6 * unique_mass_total,
        "word_multiplicity_support_is_6_times_unique_support": word_support_total == 6 * unique_support_total,
        "groupoid_cycle_holonomy_failures_are_zero": groupoid_report.get("witness", {}).get(
            "cycle_holonomy_failure_count"
        )
        == 0,
        "normal_words_compare_to_pentagon_normal_form": groupoid_comparison.get("pentagon_chain_normal_form")
        == "typed_length_four_chain(x0,x1,x2,x3,x4)",
    }

    witness = {
        "word_count": len(word_rows),
        "unique_atom_count": len(atom_rows),
        "unique_atom_ids": word_payload["unique_atom_ids"],
        "word_sector_coverage_histogram": word_sector_hist,
        "unique_atom_sector_coverage_histogram": atom_sector_hist,
        "unique_atom_signature_class_count": word_payload["unique_atom_signature_class_count"],
        "unique_atom_tensor_path_support": unique_support_total,
        "unique_atom_tensor_path_coefficient_mass": unique_mass_total,
        "word_multiplicity_tensor_path_support": word_support_total,
        "word_multiplicity_tensor_path_coefficient_mass": word_mass_total,
        "groupoid_cycle_holonomy_failure_count": groupoid_report.get("witness", {}).get(
            "cycle_holonomy_failure_count"
        ),
        "pentagon_chain_normal_form": groupoid_comparison.get("pentagon_chain_normal_form"),
        "normal_form_word_table_sha256": sha_array(word_array),
        "normal_form_atom_table_sha256": sha_array(atom_array),
        "cycle_records_sha256": sha_array(cycle_records),
        "object_support_cube_sha256": sha_array(support_cube),
        "object_coefficient_cube_sha256": sha_array(coefficient_cube),
    }

    certificate = {
        "schema": "c985.d20_normal_form_words_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_NORMAL_FORM_WORDS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "transition groupoid cycles give 36 explicit d20 normal-form words",
            "the six cycle atoms are exactly the selected atlas triple-overlap atoms",
            "object-sector cubes reproduce the boundary atlas tensor support and mass for every cycle atom",
            "twelve words recover all six H6 sectors while twenty-four recover five sectors",
            "the word-level path readout remains compatible with the certified pentagon normal-form boundary",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_normal_form_words@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified transition groupoid cycles determine explicit d20 "
            "normal-form words whose atom paths reproduce the certified tensor-sector "
            "support, coefficient mass, and relation-signature coverage on the "
            "six-atom chart triple overlap."
        ),
        "stage_protocol": {
            "draft": "use transition groupoid cycle records and certified tensor-sector geometry cubes",
            "witness": "materialize normal-form word rows and atom-level sector geometry comparisons",
            "coherence": "check zero cycle defects, support/mass agreement with boundary atlas, and sector coverage histograms",
            "closure": "certify d20 word readouts without claiming new C985 pentagon or associator data",
            "emit": "emit normal-form word JSON/CSV/NPZ, certificate, report, and next word-deepening target",
        },
        "inputs": {
            "transition_groupoid_report": input_entry(
                GROUPOID_REPORT,
                {
                    "status": groupoid_report.get("status"),
                    "certificate_sha256": groupoid_report.get("certificate_sha256"),
                },
            ),
            "transition_groupoid": input_entry(GROUPOID_JSON),
            "transition_groupoid_tables": input_entry(GROUPOID_TABLES),
            "chart_atlas_report": input_entry(
                CHART_ATLAS_REPORT,
                {
                    "status": chart_report.get("status"),
                    "certificate_sha256": chart_report.get("certificate_sha256"),
                },
            ),
            "chart_atlas": input_entry(CHART_ATLAS_JSON),
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "boundary_atlas_npz": input_entry(ATLAS_NPZ),
            "tensor_geometry_report": input_entry(
                GEOMETRY_REPORT,
                {
                    "status": geometry_report.get("status"),
                    "certificate_sha256": geometry_report.get("certificate_sha256"),
                },
            ),
            "object_sector_cubes": input_entry(OBJECT_SECTOR_CUBES),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "normal_form_words": relpath(OUT_DIR / "normal_form_words.json"),
            "normal_form_words_csv": relpath(OUT_DIR / "normal_form_words.csv"),
            "normal_form_word_tables": relpath(OUT_DIR / "normal_form_word_tables.npz"),
            "normal_form_words_certificate": relpath(OUT_DIR / "normal_form_words_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "36 explicit d20 normal-form words from transition groupoid cycles",
                "atom-level comparison against certified object-sector support and coefficient cubes",
                "agreement with boundary atlas tensor support and mass for the six cycle atoms",
                "sector-coverage and relation-signature coverage of the word atoms",
                "readout-level compatibility with the certified pentagon normal-form boundary",
            ],
            "does_not_certify_because_not_required": [
                "new C985 associator or pentagon coherence beyond the already certified reports",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the normal-form word atoms to build a six-sector symbolic alphabet, "
            "then certify rewrite rules from word concatenation and tensor-sector "
            "signature preservation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_normal_form_words_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified transition groupoid and tensor geometry readouts",
            "materialize explicit d20 normal-form words from directed chart cycles",
            "recompute each cycle atom tensor support and mass from object-sector cubes",
            "compare recomputed tensor data with the boundary atlas",
            "check sector coverage histograms and compatibility with pentagon normal-form metadata",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "normal_form_words": normal_words,
        "normal_form_words_csv": csv_text(WORD_COLUMNS, word_rows),
        "normal_form_word_table": word_array,
        "normal_form_atom_table": atom_array,
        "normal_form_words_certificate": certificate,
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
    write_json(OUT_DIR / "normal_form_words.json", payloads["normal_form_words"])
    (OUT_DIR / "normal_form_words.csv").write_text(
        payloads["normal_form_words_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "normal_form_word_tables.npz",
        normal_form_word_table=payloads["normal_form_word_table"],
        normal_form_atom_table=payloads["normal_form_atom_table"],
    )
    write_json(OUT_DIR / "normal_form_words_certificate.json", payloads["normal_form_words_certificate"])
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
                "word_count": witness["word_count"],
                "unique_atom_count": witness["unique_atom_count"],
                "unique_atom_signature_class_count": witness["unique_atom_signature_class_count"],
                "unique_atom_tensor_path_coefficient_mass": witness[
                    "unique_atom_tensor_path_coefficient_mass"
                ],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
