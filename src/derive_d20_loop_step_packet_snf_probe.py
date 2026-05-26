from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_loop_step_packet_snf_probe.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_loop_step_packet_snf_probe"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
LOOP297_SCATTERING_AMPLITUDE_LIFT = (
    D20_INVARIANTS / "theorems" / "loop297_scattering_amplitude_lift" / "report.json"
)
AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE = (
    D20_INVARIANTS / "theorems" / "projective_packet_spectral_charge_table" / "report.json"
)
FULL_EXPOSURE_CANONICAL_LABELLED_FRAME = (
    D20_INVARIANTS / "theorems" / "full_exposure_canonical_labelled_frame" / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_packet_bridge_snf_obstruction" / "report.json"
)

EXPECTED_STATUSES = {
    "boundary_to_loop_report": "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED",
    "loop297_scattering_amplitude_lift_report": "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED",
    "amplitude_quotient_fourier_mode_classifier_report": (
        "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
    ),
    "projective_packet_spectral_charge_table_report": (
        "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
    ),
    "full_exposure_canonical_labelled_frame_report": (
        "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
    ),
    "full_exposure_packet_propagation_graph_report": (
        "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED"
    ),
}


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


def pair_histogram(counter: Counter[tuple[int, int]]) -> dict[str, int]:
    return {f"{key[0]}|{key[1]}": int(counter[key]) for key in sorted(counter)}


def packet_pairs(component_rows: list[dict[str, Any]]) -> list[list[int]]:
    return [[int(packet_id) for packet_id in row["packet_pair"]] for row in component_rows]


def snf_failed_tests(u: int, v: int) -> list[str]:
    failed = []
    if u % 2 != 0:
        failed.append("u_not_0_mod_2")
    if v % 2 != 0:
        failed.append("v_not_0_mod_2")
    if (u + v) % 6 != 0:
        failed.append("u_plus_v_not_0_mod_6")
    return failed


def build_packet_mode_incidence_rows(
    pairs: list[list[int]],
    spectral_by_packet: dict[int, dict[str, Any]],
    mode_atoms_by_mask: dict[int, set[int]],
    step_atom_ids: list[int],
) -> list[dict[str, Any]]:
    rows = []
    for component_id, pair in enumerate(pairs):
        for component_position, packet_id in enumerate(pair):
            packet = spectral_by_packet[packet_id]
            mode_masks = [int(mask) for mask in packet["mode_masks"]]
            incidence_counts = [
                sum(1 for mask in mode_masks if atom_id in mode_atoms_by_mask[mask])
                for atom_id in step_atom_ids
            ]
            rows.append(
                {
                    "component_id": component_id,
                    "component_position": component_position,
                    "packet_id": packet_id,
                    "mode_masks": mode_masks,
                    "mode_active_step_atom_counts": [
                        len(mode_atoms_by_mask[mask]) for mask in mode_masks
                    ],
                    "loop297_atom_union_count": int(packet["loop297_atom_union_count"]),
                    "step_atom_incidence_counts": incidence_counts,
                    "step_atom_incidence_count_histogram": histogram(Counter(incidence_counts)),
                }
            )
    return rows


def build_step_atom_column_rows(
    pairs: list[list[int]],
    packet_rows: list[dict[str, Any]],
    step_atom_ids: list[int],
) -> list[dict[str, Any]]:
    row_by_packet = {int(row["packet_id"]): row for row in packet_rows}
    column_rows = []
    for atom_index, atom_id in enumerate(step_atom_ids):
        target_vector = []
        component_pair_values = []
        failed_component_rows = []
        value_histogram: Counter[int] = Counter()
        reason_histogram: Counter[str] = Counter()
        for component_id, pair in enumerate(pairs):
            u = int(row_by_packet[pair[0]]["step_atom_incidence_counts"][atom_index])
            v = int(row_by_packet[pair[1]]["step_atom_incidence_counts"][atom_index])
            target_vector.extend([u, v])
            value_histogram.update([u, v])
            failed = snf_failed_tests(u, v)
            reason_key = "pass" if not failed else "|".join(failed)
            reason_histogram[reason_key] += 1
            component_pair_values.append([u, v])
            if failed:
                failed_component_rows.append(
                    {
                        "component_id": component_id,
                        "packet_pair": pair,
                        "target_pair": [u, v],
                        "failed_tests": failed,
                    }
                )
        column_rows.append(
            {
                "loop297_step_atom_id": atom_id,
                "target_vector_component_order": target_vector,
                "component_pair_values": component_pair_values,
                "value_histogram": histogram(value_histogram),
                "failure_reason_histogram": histogram(reason_histogram),
                "failed_component_count": len(failed_component_rows),
                "passes_packet_snf_image": len(failed_component_rows) == 0,
                "first_failed_component": failed_component_rows[0],
            }
        )
    return column_rows


def build_theorem() -> dict[str, Any]:
    boundary = load_json(BOUNDARY_TO_LOOP_REPORT)
    loop297 = load_json(LOOP297_SCATTERING_AMPLITUDE_LIFT)
    fourier = load_json(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER)
    spectral = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE)
    frame = load_json(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION)

    component_rows = graph["derived"]["component_rows"]
    pairs = packet_pairs(component_rows)
    component_packet_ids = [packet_id for pair in pairs for packet_id in pair]
    frame_packet_ids = [
        int(row["packet_id"]) for row in frame["derived"]["canonical_frame_rows"]
    ]
    spectral_by_packet = {
        int(row["packet_id"]): row
        for row in spectral["derived"]["packet_spectral_charge_rows"]
        if int(row["packet_id"]) in set(component_packet_ids)
    }
    mode_atoms_by_mask = {
        int(row["mode_mask"]): set(int(atom_id) for atom_id in row["active_step_atom_ids"])
        for row in fourier["derived"]["mode_rows"]
    }
    step_atom_ids = sorted(
        {
            atom_id
            for packet_id in component_packet_ids
            for mask in spectral_by_packet[packet_id]["mode_masks"]
            for atom_id in mode_atoms_by_mask[int(mask)]
        }
    )
    packet_rows = build_packet_mode_incidence_rows(
        pairs, spectral_by_packet, mode_atoms_by_mask, step_atom_ids
    )
    column_rows = build_step_atom_column_rows(pairs, packet_rows, step_atom_ids)

    pair_value_counter: Counter[tuple[int, int]] = Counter()
    failure_reason_counter: Counter[str] = Counter()
    failed_blocks_per_column_counter: Counter[int] = Counter()
    for column in column_rows:
        failed_blocks_per_column_counter[int(column["failed_component_count"])] += 1
        for pair_value in column["component_pair_values"]:
            pair_value_counter[(int(pair_value[0]), int(pair_value[1]))] += 1
        for reason, count in column["failure_reason_histogram"].items():
            failure_reason_counter[str(reason)] += int(count)

    passing_columns = [
        int(row["loop297_step_atom_id"])
        for row in column_rows
        if bool(row["passes_packet_snf_image"])
    ]
    failing_columns = [
        int(row["loop297_step_atom_id"])
        for row in column_rows
        if not bool(row["passes_packet_snf_image"])
    ]
    probe_summary = {
        "visible_candidate": "Loop_297_step_atom_mode_incidence_count_columns",
        "candidate_semantics": (
            "for each step atom and full-exposure packet, count how many of the "
            "packet's two mode masks contain that atom"
        ),
        "full_exposure_packet_count": len(component_packet_ids),
        "component_count": len(pairs),
        "loop297_step_atom_count": len(step_atom_ids),
        "step_atom_ids": step_atom_ids,
        "tested_column_count": len(column_rows),
        "columns_passing_packet_snf_image": passing_columns,
        "columns_failing_packet_snf_image": failing_columns,
        "failed_blocks_per_column_histogram": histogram(failed_blocks_per_column_counter),
        "component_pair_value_histogram": pair_histogram(pair_value_counter),
        "failure_reason_histogram": histogram(failure_reason_counter),
        "natural_column_outcome": "all_visible_loop_step_columns_fail_packet_snf_image",
    }

    local_image_test = snf["derived"]["obstruction_summary"]["local_image_test"]
    checks = {
        "boundary_to_loop_is_certified": boundary.get("status")
        == EXPECTED_STATUSES["boundary_to_loop_report"]
        and boundary.get("all_checks_pass") is True,
        "loop297_scattering_amplitude_lift_is_certified": loop297.get("status")
        == EXPECTED_STATUSES["loop297_scattering_amplitude_lift_report"]
        and loop297.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == EXPECTED_STATUSES["amplitude_quotient_fourier_mode_classifier_report"]
        and fourier.get("all_checks_pass") is True,
        "spectral_charge_table_is_certified": spectral.get("status")
        == EXPECTED_STATUSES["projective_packet_spectral_charge_table_report"]
        and spectral.get("all_checks_pass") is True,
        "full_exposure_frame_is_certified": frame.get("status")
        == EXPECTED_STATUSES["full_exposure_canonical_labelled_frame_report"]
        and frame.get("all_checks_pass") is True,
        "packet_propagation_graph_is_certified": graph.get("status")
        == EXPECTED_STATUSES["full_exposure_packet_propagation_graph_report"]
        and graph.get("all_checks_pass") is True,
        "packet_snf_obstruction_is_certified": snf.get("status")
        == EXPECTED_STATUSES["d20_packet_bridge_snf_obstruction_report"]
        and snf.get("all_checks_pass") is True,
        "component_count_is_10": len(pairs) == 10,
        "component_pairs_cover_frame_packets": sorted(component_packet_ids)
        == sorted(frame_packet_ids),
        "component_pairs_have_uniform_packet_block": all(
            row["block_matrix"] == [[2, 4], [4, 2]] for row in component_rows
        ),
        "full_packet_spectral_rows_exist": sorted(spectral_by_packet) == sorted(component_packet_ids),
        "all_full_packets_have_two_modes": all(
            len(spectral_by_packet[packet_id]["mode_masks"]) == 2
            for packet_id in component_packet_ids
        ),
        "all_full_packets_have_full_loop297_atom_union": all(
            int(spectral_by_packet[packet_id]["loop297_atom_union_count"]) == 25
            and spectral_by_packet[packet_id]["loop297_atom_union_ids"] == list(range(25))
            for packet_id in component_packet_ids
        ),
        "mode_classifier_contains_all_full_packet_modes": all(
            int(mask) in mode_atoms_by_mask
            for packet_id in component_packet_ids
            for mask in spectral_by_packet[packet_id]["mode_masks"]
        ),
        "loop_step_atom_ids_are_0_to_24": step_atom_ids == list(range(25)),
        "mode_incidence_counts_are_one_or_two": all(
            count in (1, 2)
            for row in packet_rows
            for count in row["step_atom_incidence_counts"]
        ),
        "no_packet_atom_incidence_zero": all(
            count > 0 for row in packet_rows for count in row["step_atom_incidence_counts"]
        ),
        "step_atom_column_count_is_25": len(column_rows) == 25,
        "column_vectors_are_20_dimensional": all(
            len(row["target_vector_component_order"]) == 20 for row in column_rows
        ),
        "snf_local_image_test_is_exact_original_basis_test": local_image_test
        == "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet",
        "no_visible_loop_step_column_passes_packet_snf": passing_columns == [],
        "every_visible_loop_step_column_fails_every_component": all(
            int(row["failed_component_count"]) == len(pairs) for row in column_rows
        ),
        "component_pair_value_histogram_matches_visible_incidence": probe_summary[
            "component_pair_value_histogram"
        ]
        == {"1|1": 2, "1|2": 12, "2|2": 236},
        "failure_reason_histogram_matches_snf_tests": probe_summary[
            "failure_reason_histogram"
        ]
        == {
            "u_not_0_mod_2|u_plus_v_not_0_mod_6": 12,
            "u_not_0_mod_2|v_not_0_mod_2|u_plus_v_not_0_mod_6": 2,
            "u_plus_v_not_0_mod_6": 236,
        },
    }

    report = {
        "schema": "d20.theorem.d20_loop_step_packet_snf_probe",
        "status": "D20_LOOP_STEP_PACKET_SNF_PROBE_CERTIFIED",
        "object": "D20",
        "definition": {
            "visible_loop_surface": (
                "the certified boundary-to-Loop_297 and Fourier-mode active_step_atom_ids surface"
            ),
            "candidate_columns": (
                "Loop_297 step-atom support-count columns into the 20 full-exposure packet "
                "coordinates, ordered by the certified full-exposure packet propagation graph"
            ),
            "packet_snf_image_test": local_image_test,
        },
        "claim": (
            "The currently visible Loop_297 step-atom incidence surface does not supply a raw "
            "integer bridge into the certified 20-packet matrix image: all 25 natural "
            "step-atom support-count columns fail the exact packet SNF image test on every "
            "active-partner doublet."
        ),
        "inputs": {
            "boundary_to_loop_report": input_record(BOUNDARY_TO_LOOP_REPORT),
            "loop297_scattering_amplitude_lift_report": input_record(
                LOOP297_SCATTERING_AMPLITUDE_LIFT
            ),
            "amplitude_quotient_fourier_mode_classifier_report": input_record(
                AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER
            ),
            "projective_packet_spectral_charge_table_report": input_record(
                PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE
            ),
            "full_exposure_canonical_labelled_frame_report": input_record(
                FULL_EXPOSURE_CANONICAL_LABELLED_FRAME
            ),
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
            "d20_packet_bridge_snf_obstruction_report": input_record(
                D20_PACKET_BRIDGE_SNF_OBSTRUCTION
            ),
        },
        "derived": {
            "probe_summary": probe_summary,
            "component_packet_pairs": pairs,
            "packet_mode_incidence_rows": packet_rows,
            "packet_mode_incidence_rows_sha256": sha_json(packet_rows),
            "step_atom_column_rows": column_rows,
            "step_atom_column_rows_sha256": sha_json(column_rows),
            "step_atom_target_vectors_sha256": sha_json(
                [row["target_vector_component_order"] for row in column_rows]
            ),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "boundary_pressure": (
                "The public boundary-to-loop certificates reach Loop_297 step atoms and packet "
                "modes, but the support-count incidence visible there is not already a packet "
                "operator image."
            ),
            "what_is_ruled_out": (
                "A raw packet bridge cannot be just the naive active_step_atom support-count "
                "map from Loop_297 step atoms to full-exposure packets."
            ),
            "not_ruled_out": (
                "A labelled A985, tube, or q42/q12 bridge with certified multiplicities, signs, "
                "cancellations, or quotient normalization is still open."
            ),
        },
        "next_highest_yield_item": (
            "Emit a certified Lambda^3 H6/A985 atom-to-support incidence table with signed "
            "multiplicities, then rerun the same packet SNF image test on those raw columns."
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
        "schema": "d20.theorem.d20_loop_step_packet_snf_probe_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "test the visible Loop_297 step-atom packet incidence against the packet SNF obstruction",
            "separate the certified loop/mode boundary from the still-missing raw packet bridges",
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
