from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
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
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_transition_groupoid"
STATUS = "C985_D20_TRANSITION_GROUPOID_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CHART_ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_hyperbolic_chart_atlas"
ASSOCIATOR_DIR = D20_INVARIANTS / "proof_obligations" / "c985_associator_rebracketing_oracle"
PENTAGON_DIR = D20_INVARIANTS / "proof_obligations" / "c985_pentagon_chain_normal_form"

CHART_ATLAS_REPORT = CHART_ATLAS_DIR / "report.json"
CHART_ATLAS_JSON = CHART_ATLAS_DIR / "hyperbolic_chart_atlas.json"
CHART_ATLAS_TABLES = CHART_ATLAS_DIR / "hyperbolic_chart_atlas_tables.npz"
ASSOCIATOR_REPORT = ASSOCIATOR_DIR / "report.json"
ASSOCIATOR_ORACLE = ASSOCIATOR_DIR / "associator_oracle.json"
ASSOCIATOR_SAMPLES = ASSOCIATOR_DIR / "associator_sample_witnesses.npz"
PENTAGON_REPORT = PENTAGON_DIR / "report.json"
PENTAGON_NORMAL_FORM = PENTAGON_DIR / "pentagon_normal_form.json"
PENTAGON_SAMPLES = PENTAGON_DIR / "pentagon_sample_chains.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_transition_groupoid.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_transition_groupoid.py"

ARROW_COLUMNS = [
    "source_seed",
    "target_seed",
    "atom_id",
    "source_local_rank",
    "target_local_rank",
    "rank_delta",
    "source_chart_size",
    "target_chart_size",
]

INVERSE_COLUMNS = [
    "source_seed",
    "target_seed",
    "atom_id",
    "forward_rank_delta",
    "reverse_rank_delta",
    "defect",
]

COMPOSITION_COLUMNS = [
    "source_seed",
    "middle_seed",
    "target_seed",
    "atom_id",
    "direct_delta",
    "composed_delta",
    "defect",
]

CYCLE_COLUMNS = [
    "start_seed",
    "middle_seed",
    "last_seed",
    "atom_id",
    "cycle_delta_sum",
]


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def transition_lookup(ordered_transition_records: np.ndarray) -> dict[tuple[int, int, int], dict[str, int]]:
    lookup: dict[tuple[int, int, int], dict[str, int]] = {}
    for row in ordered_transition_records:
        record = {
            column: int(row[index])
            for index, column in enumerate(ARROW_COLUMNS)
        }
        key = (record["source_seed"], record["target_seed"], record["atom_id"])
        lookup[key] = record
    return lookup


def build_inverse_records(ordered_transition_records: np.ndarray) -> tuple[list[dict[str, int]], np.ndarray]:
    lookup = transition_lookup(ordered_transition_records)
    rows: list[dict[str, int]] = []
    for row in ordered_transition_records:
        source, target, atom_id, _, _, rank_delta, _, _ = [int(x) for x in row.tolist()]
        reverse = lookup[(target, source, atom_id)]
        record = {
            "source_seed": source,
            "target_seed": target,
            "atom_id": atom_id,
            "forward_rank_delta": rank_delta,
            "reverse_rank_delta": int(reverse["rank_delta"]),
            "defect": rank_delta + int(reverse["rank_delta"]),
        }
        rows.append(record)
    return rows, np.asarray([[row[column] for column in INVERSE_COLUMNS] for row in rows], dtype=np.int64)


def build_composition_records(
    selected_chart_ids: list[int],
    triple_overlap_atom_ids: list[int],
    ordered_transition_records: np.ndarray,
) -> tuple[list[dict[str, int]], np.ndarray]:
    lookup = transition_lookup(ordered_transition_records)
    rows: list[dict[str, int]] = []
    for source, target in itertools.permutations(selected_chart_ids, 2):
        middle_candidates = [chart_id for chart_id in selected_chart_ids if chart_id not in {source, target}]
        middle = middle_candidates[0]
        for atom_id in triple_overlap_atom_ids:
            direct = lookup[(source, target, atom_id)]["rank_delta"]
            composed = (
                lookup[(source, middle, atom_id)]["rank_delta"]
                + lookup[(middle, target, atom_id)]["rank_delta"]
            )
            rows.append(
                {
                    "source_seed": source,
                    "middle_seed": middle,
                    "target_seed": target,
                    "atom_id": atom_id,
                    "direct_delta": int(direct),
                    "composed_delta": int(composed),
                    "defect": int(composed - direct),
                }
            )
    return rows, np.asarray([[row[column] for column in COMPOSITION_COLUMNS] for row in rows], dtype=np.int64)


def build_cycle_records(
    selected_chart_ids: list[int],
    triple_overlap_atom_ids: list[int],
    ordered_transition_records: np.ndarray,
) -> tuple[list[dict[str, int]], np.ndarray]:
    lookup = transition_lookup(ordered_transition_records)
    rows: list[dict[str, int]] = []
    for start, middle, last in itertools.permutations(selected_chart_ids, 3):
        for atom_id in triple_overlap_atom_ids:
            cycle_sum = (
                lookup[(start, middle, atom_id)]["rank_delta"]
                + lookup[(middle, last, atom_id)]["rank_delta"]
                + lookup[(last, start, atom_id)]["rank_delta"]
            )
            rows.append(
                {
                    "start_seed": start,
                    "middle_seed": middle,
                    "last_seed": last,
                    "atom_id": atom_id,
                    "cycle_delta_sum": int(cycle_sum),
                }
            )
    return rows, np.asarray([[row[column] for column in CYCLE_COLUMNS] for row in rows], dtype=np.int64)


def sample_shapes(path: Any) -> dict[str, list[int]]:
    payload = np.load(path, allow_pickle=False)
    return {name: [int(x) for x in payload[name].shape] for name in sorted(payload.files)}


def build_payloads() -> dict[str, Any]:
    chart_report = load_json(CHART_ATLAS_REPORT)
    chart_atlas = load_json(CHART_ATLAS_JSON)
    associator_report = load_json(ASSOCIATOR_REPORT)
    associator_oracle = load_json(ASSOCIATOR_ORACLE)
    pentagon_report = load_json(PENTAGON_REPORT)
    pentagon_normal_form = load_json(PENTAGON_NORMAL_FORM)
    tables = np.load(CHART_ATLAS_TABLES, allow_pickle=False)
    selected_chart_ids = [int(x) for x in np.asarray(tables["selected_chart_ids"], dtype=np.int64)]
    ordered_transition_records = np.asarray(tables["ordered_transition_records"], dtype=np.int64)
    transition_pair_records = np.asarray(tables["transition_pair_records"], dtype=np.int64)
    transition_cocycle_records = np.asarray(tables["transition_cocycle_records"], dtype=np.int64)
    triple_overlap_atom_ids = [int(x) for x in np.asarray(tables["triple_overlap_atom_ids"], dtype=np.int64)]

    inverse_rows, inverse_array = build_inverse_records(ordered_transition_records)
    composition_rows, composition_array = build_composition_records(
        selected_chart_ids,
        triple_overlap_atom_ids,
        ordered_transition_records,
    )
    cycle_rows, cycle_array = build_cycle_records(
        selected_chart_ids,
        triple_overlap_atom_ids,
        ordered_transition_records,
    )

    associator_witness = associator_report.get("witness", {})
    pentagon_witness = pentagon_report.get("witness", {})
    associator_sample_summary = associator_witness.get("sample_summary", {})
    pentagon_sample_summary = pentagon_witness.get("sample_summary", {})
    associator_sample_shapes = sample_shapes(ASSOCIATOR_SAMPLES)
    pentagon_sample_shapes = sample_shapes(PENTAGON_SAMPLES)

    groupoid = {
        "schema": "c985.d20_transition_groupoid@1",
        "object": "d20",
        "groupoid_rule": {
            "objects": "the three canonical hyperbolic atlas chart seeds",
            "arrows": "local-rank transition records on selected chart overlaps, keyed by preserved atom id",
            "inverse_law": "the reverse transition on the same atom has opposite rank delta",
            "composition_law": "on the triple overlap, direct transition equals composition through the third chart",
            "normal_form": "preserved atom id together with terminal chart local rank",
        },
        "source_chart_atlas_certificate": chart_report.get("certificate_sha256"),
        "source_associator_certificate": associator_report.get("certificate_sha256"),
        "source_pentagon_certificate": pentagon_report.get("certificate_sha256"),
        "selected_chart_ids": selected_chart_ids,
        "triple_overlap_atom_ids": triple_overlap_atom_ids,
        "arrow_count": int(ordered_transition_records.shape[0]),
        "inverse_loop_records": inverse_rows,
        "composition_records": composition_rows,
        "cycle_records": cycle_rows,
        "categorical_normal_form_comparison": {
            "transition_groupoid_normal_form": "transition_normal_form(atom_id, terminal_chart, terminal_local_rank)",
            "associator_oracle_status": associator_report.get("status"),
            "associator_oracle_rule": associator_oracle.get("oracle_rule"),
            "associator_sample_rebracketing_count": associator_sample_summary.get("sample_count"),
            "associator_sample_failure_count": associator_sample_summary.get("sample_failure_count"),
            "associator_sample_shapes": associator_sample_shapes,
            "pentagon_status": pentagon_report.get("status"),
            "pentagon_chain_normal_form": pentagon_witness.get("chain_normal_form"),
            "pentagon_exact_length_four_chain_count": pentagon_witness.get("address_counts", {}).get(
                "exact_length_four_chain_count"
            ),
            "pentagon_top_and_bottom_paths_have_same_normal_form": pentagon_report.get("checks", {}).get(
                "top_and_bottom_paths_have_same_normal_form"
            ),
            "pentagon_sample_shapes": pentagon_sample_shapes,
            "comparison_boundary": (
                "the d20 groupoid verifies path-independent local-rank transitions; "
                "the C985 reports independently certify associator and pentagon normal forms"
            ),
        },
    }

    inverse_failures = int(np.count_nonzero(inverse_array[:, 5]))
    composition_failures = int(np.count_nonzero(composition_array[:, 6]))
    cycle_failures = int(np.count_nonzero(cycle_array[:, 4]))
    checks = {
        "chart_atlas_report_certified": chart_report.get("status") == "C985_D20_HYPERBOLIC_CHART_ATLAS_CERTIFIED",
        "associator_oracle_report_certified": associator_report.get("status")
        == "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
        "pentagon_normal_form_report_certified": pentagon_report.get("status")
        == "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
        "selected_chart_ids_are_0_2_10": selected_chart_ids == [0, 2, 10],
        "transition_arrow_count_is_50": int(ordered_transition_records.shape[0]) == 50,
        "transition_pair_count_is_3": int(transition_pair_records.shape[0]) == 3,
        "triple_overlap_atom_count_is_6": len(triple_overlap_atom_ids) == 6,
        "inverse_loop_record_count_is_50": int(inverse_array.shape[0]) == 50,
        "inverse_loop_failures_are_zero": inverse_failures == 0,
        "composition_record_count_is_36": int(composition_array.shape[0]) == 36,
        "composition_failures_are_zero": composition_failures == 0,
        "cycle_record_count_is_36": int(cycle_array.shape[0]) == 36,
        "cycle_holonomy_failures_are_zero": cycle_failures == 0,
        "atlas_cocycle_failures_are_zero": int(np.count_nonzero(transition_cocycle_records[:, 4])) == 0,
        "associator_sample_rebracketing_count_is_1970": associator_sample_summary.get(
            "sample_count"
        )
        == 1970,
        "associator_sample_rebracketing_failures_are_zero": associator_sample_summary.get(
            "sample_failure_count"
        )
        == 0,
        "pentagon_exact_chain_count_matches_final_certificate": pentagon_witness.get(
            "address_counts", {}
        ).get("exact_length_four_chain_count")
        == 16837352591360,
        "pentagon_top_and_bottom_paths_share_normal_form": pentagon_report.get("checks", {}).get(
            "top_and_bottom_paths_have_same_normal_form"
        )
        is True,
        "pentagon_chain_normal_form_is_typed_length_four": pentagon_witness.get("chain_normal_form")
        == "typed_length_four_chain(x0,x1,x2,x3,x4)",
        "groupoid_and_pentagon_both_have_zero_path_defects": composition_failures == 0
        and cycle_failures == 0
        and pentagon_report.get("checks", {}).get("top_and_bottom_paths_have_same_normal_form")
        is True,
    }

    witness = {
        "object_count": len(selected_chart_ids),
        "selected_chart_ids": selected_chart_ids,
        "arrow_count": int(ordered_transition_records.shape[0]),
        "inverse_loop_record_count": int(inverse_array.shape[0]),
        "inverse_loop_failure_count": inverse_failures,
        "composition_record_count": int(composition_array.shape[0]),
        "composition_failure_count": composition_failures,
        "cycle_record_count": int(cycle_array.shape[0]),
        "cycle_holonomy_failure_count": cycle_failures,
        "triple_overlap_atom_ids": triple_overlap_atom_ids,
        "associator_sample_rebracketing_count": associator_sample_summary.get("sample_count"),
        "associator_sample_rebracketing_failures": associator_sample_summary.get("sample_failure_count"),
        "pentagon_exact_length_four_chain_count": pentagon_witness.get("address_counts", {}).get(
            "exact_length_four_chain_count"
        ),
        "pentagon_chain_normal_form": pentagon_witness.get("chain_normal_form"),
        "ordered_transition_records_sha256": sha_array(ordered_transition_records),
        "inverse_loop_records_sha256": sha_array(inverse_array),
        "composition_records_sha256": sha_array(composition_array),
        "cycle_records_sha256": sha_array(cycle_array),
        "associator_samples_sha256": associator_sample_summary.get("chain_sample_sha256"),
        "pentagon_normal_form_sha256": pentagon_witness.get("normal_form_sha256"),
    }

    certificate = {
        "schema": "c985.d20_transition_groupoid_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_TRANSITION_GROUPOID_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the three-chart d20 atlas generates a finite local-rank transition groupoid",
            "all 50 transition arrows have inverse arrows with zero rank defect",
            "all 36 triple-overlap compositions agree with direct transitions",
            "all 36 directed chart cycles have zero rank holonomy",
            "the groupoid path-independence readout is compared against the certified C985 associator and pentagon normal forms",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_transition_groupoid@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The verified three-chart hyperbolic atlas carries a finite transition "
            "groupoid whose local-rank arrows are invertible and path-independent "
            "on the triple overlap, matching the normal-form discipline of the "
            "certified C985 associator and pentagon data at the readout level."
        ),
        "stage_protocol": {
            "draft": "start from the certified three-chart hyperbolic atlas and C985 associator/pentagon reports",
            "witness": "materialize inverse loops, triple-overlap compositions, and directed chart cycles",
            "coherence": "check zero inverse defects, zero composition defects, zero cycle holonomy, and upstream normal-form certificates",
            "closure": "certify the d20 transition groupoid as a readout comparison without re-proving C985 coherence",
            "emit": "emit groupoid JSON/CSV/NPZ, certificate, report, and next cycle-deepening target",
        },
        "inputs": {
            "chart_atlas_report": input_entry(
                CHART_ATLAS_REPORT,
                {
                    "status": chart_report.get("status"),
                    "certificate_sha256": chart_report.get("certificate_sha256"),
                },
            ),
            "chart_atlas": input_entry(CHART_ATLAS_JSON),
            "chart_atlas_tables": input_entry(CHART_ATLAS_TABLES),
            "associator_report": input_entry(
                ASSOCIATOR_REPORT,
                {
                    "status": associator_report.get("status"),
                    "certificate_sha256": associator_report.get("certificate_sha256"),
                },
            ),
            "associator_oracle": input_entry(ASSOCIATOR_ORACLE),
            "associator_samples": input_entry(ASSOCIATOR_SAMPLES),
            "pentagon_report": input_entry(
                PENTAGON_REPORT,
                {
                    "status": pentagon_report.get("status"),
                    "certificate_sha256": pentagon_report.get("certificate_sha256"),
                },
            ),
            "pentagon_normal_form": input_entry(PENTAGON_NORMAL_FORM),
            "pentagon_samples": input_entry(PENTAGON_SAMPLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "transition_groupoid": relpath(OUT_DIR / "transition_groupoid.json"),
            "transition_groupoid_cycles_csv": relpath(OUT_DIR / "transition_groupoid_cycles.csv"),
            "transition_groupoid_tables": relpath(OUT_DIR / "transition_groupoid_tables.npz"),
            "transition_groupoid_certificate": relpath(OUT_DIR / "transition_groupoid_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "finite transition groupoid records for the selected three-chart d20 atlas",
                "inverse-loop zero defects for all ordered transition arrows",
                "triple-overlap direct-vs-composed transition equality",
                "directed chart-cycle zero rank holonomy",
                "readout-level comparison with certified C985 associator and pentagon normal-form metadata",
            ],
            "does_not_certify_because_not_required": [
                "new C985 associator or pentagon coherence beyond the already certified reports",
                "transition groupoids for non-selected chart covers",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the transition groupoid cycles to choose explicit d20 normal-form "
            "words, then compare their atom paths with the certified tensor-sector "
            "geometry signatures."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_transition_groupoid_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified chart atlas and C985 associator/pentagon reports",
            "verify all transition arrows have inverse arrows with opposite rank delta",
            "verify direct-vs-composed transition equality on every triple-overlap atom",
            "verify directed chart-cycle zero holonomy",
            "compare groupoid path independence with C985 associator and pentagon normal-form metadata",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "transition_groupoid": groupoid,
        "transition_groupoid_cycles_csv": csv_text(CYCLE_COLUMNS, cycle_rows),
        "ordered_transition_records": ordered_transition_records,
        "inverse_loop_records": inverse_array,
        "composition_records": composition_array,
        "cycle_records": cycle_array,
        "transition_groupoid_certificate": certificate,
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
    write_json(OUT_DIR / "transition_groupoid.json", payloads["transition_groupoid"])
    (OUT_DIR / "transition_groupoid_cycles.csv").write_text(
        payloads["transition_groupoid_cycles_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "transition_groupoid_tables.npz",
        ordered_transition_records=payloads["ordered_transition_records"],
        inverse_loop_records=payloads["inverse_loop_records"],
        composition_records=payloads["composition_records"],
        cycle_records=payloads["cycle_records"],
    )
    write_json(OUT_DIR / "transition_groupoid_certificate.json", payloads["transition_groupoid_certificate"])
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
                "arrow_count": witness["arrow_count"],
                "composition_failure_count": witness["composition_failure_count"],
                "cycle_holonomy_failure_count": witness["cycle_holonomy_failure_count"],
                "pentagon_chain_normal_form": witness["pentagon_chain_normal_form"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
