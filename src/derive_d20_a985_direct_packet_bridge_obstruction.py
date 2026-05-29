from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import sys
from collections import Counter
from itertools import groupby
from pathlib import Path
from typing import Any

import numpy as np

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_a985_direct_packet_bridge_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

RELATION_MEMBERSHIPS_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"
HALLOWEEN_NPZ = ROOT / "data" / "raw" / "Halloween.npz"
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE = (
    D20_INVARIANTS / "theorems" / "projective_packet_spectral_charge_table" / "report.json"
)
FULL_EXPOSURE_CANONICAL_LABELLED_FRAME = (
    D20_INVARIANTS / "theorems" / "full_exposure_canonical_labelled_frame" / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)
FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT = (
    D20_INVARIANTS / "theorems" / "fourier_screen0_tube_central_element" / "report.json"
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


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def build_packet_context() -> dict[str, Any]:
    spectral = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE)
    frame = load_json(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    full_packet_ids = sorted(
        int(row["packet_id"]) for row in frame["derived"]["canonical_frame_rows"]
    )
    packet_rows = {
        int(row["packet_id"]): row
        for row in spectral["derived"]["packet_spectral_charge_rows"]
    }
    mode_to_packet = {
        int(mode): packet_id
        for packet_id in full_packet_ids
        for mode in packet_rows[packet_id]["mode_masks"]
    }
    packet_order: list[int] = []
    for component in graph["derived"]["component_rows"]:
        packet_order.extend(int(packet) for packet in component["packet_pair"])
    packet_index = {packet_id: idx for idx, packet_id in enumerate(packet_order)}
    target_full = np.asarray(graph["derived"]["adjacency"]["matrix"], dtype=np.int64)
    target_2i = np.zeros((20, 20), dtype=np.int64)
    target_4s = np.zeros((20, 20), dtype=np.int64)
    for component_id in range(10):
        offset = 2 * component_id
        target_2i[offset, offset] = 2
        target_2i[offset + 1, offset + 1] = 2
        target_4s[offset, offset + 1] = 4
        target_4s[offset + 1, offset] = 4
    return {
        "spectral": spectral,
        "frame": frame,
        "graph": graph,
        "full_packet_ids": full_packet_ids,
        "mode_to_packet": mode_to_packet,
        "packet_order": packet_order,
        "packet_index": packet_index,
        "targets": {
            "2I": target_2i,
            "4S": target_4s,
            "2I+4S": target_full,
        },
    }


def lands_in_block_lift(matrix: np.ndarray) -> tuple[bool, int]:
    off_block_mass = 0
    for component_id in range(10):
        allowed = {2 * component_id, 2 * component_id + 1}
        for row in allowed:
            for col in range(20):
                if col not in allowed:
                    off_block_mass += abs(int(matrix[row, col]))
    return off_block_mass == 0, off_block_mass


def build_direct_relation_probe(context: dict[str, Any]) -> tuple[list[np.ndarray], list[dict[str, Any]]]:
    relation = np.load(RELATION_MEMBERSHIPS_NPZ)
    quotient = np.load(QUOTIENTS_NPZ)
    point_count = int(relation["points"][0])
    offsets = relation["offsets"]
    encoded_pairs = relation["encoded_pairs"]
    mode_to_packet: dict[int, int] = context["mode_to_packet"]
    packet_index: dict[int, int] = context["packet_index"]
    matrices = []
    rows = []
    for relation_id in range(985):
        matrix = np.zeros((20, 20), dtype=np.int64)
        source_hits = 0
        target_hits = 0
        inside_hits = 0
        source_leak = 0
        target_leak = 0
        for encoded in encoded_pairs[int(offsets[relation_id]) : int(offsets[relation_id + 1])]:
            source = int(encoded) // point_count
            target = int(encoded) % point_count
            source_in = source in mode_to_packet
            target_in = target in mode_to_packet
            if source_in:
                source_hits += 1
            if target_in:
                target_hits += 1
            if source_in and target_in:
                inside_hits += 1
                matrix[
                    packet_index[mode_to_packet[source]],
                    packet_index[mode_to_packet[target]],
                ] += 1
            elif source_in:
                source_leak += 1
            elif target_in:
                target_leak += 1
        lands, off_block_mass = lands_in_block_lift(matrix)
        matrices.append(matrix)
        rows.append(
            {
                "relation_id": relation_id,
                "block_i": int(relation["block_i"][relation_id]),
                "block_j": int(relation["block_j"][relation_id]),
                "q42_class": int(quotient["q42_map"][relation_id]),
                "q12_class": int(quotient["q12_map"][relation_id]),
                "source_hits": source_hits,
                "target_hits": target_hits,
                "inside_hits": inside_hits,
                "source_leak": source_leak,
                "target_leak": target_leak,
                "preserves_full_packet_modes_on_source": source_hits > 0
                and source_leak == 0,
                "lands_in_Mat_2_Q_power_10": lands,
                "off_block_mass": off_block_mass,
                "nonzero_packet_entries": int(np.count_nonzero(matrix)),
            }
        )
    return matrices, rows


def target_matches(matrices: list[np.ndarray], targets: dict[str, np.ndarray]) -> dict[str, list[int]]:
    return {
        name: [
            relation_id
            for relation_id, matrix in enumerate(matrices)
            if np.array_equal(matrix, target)
        ]
        for name, target in targets.items()
    }


def quotient_rows(
    matrices: list[np.ndarray],
    relation_rows: list[dict[str, Any]],
    quotient_key: str,
    class_count: int,
    targets: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    quotient = np.load(QUOTIENTS_NPZ)
    map_key = f"{quotient_key}_map"
    rows = []
    for class_id in range(class_count):
        relation_ids = np.where(quotient[map_key] == class_id)[0].tolist()
        matrix = sum((matrices[int(idx)] for idx in relation_ids), np.zeros((20, 20), dtype=np.int64))
        lands, off_block_mass = lands_in_block_lift(matrix)
        target_match = [
            name for name, target in targets.items() if np.array_equal(matrix, target)
        ]
        rows.append(
            {
                "quotient": quotient_key,
                "class_id": class_id,
                "relation_count": len(relation_ids),
                "source_hits": sum(relation_rows[idx]["source_hits"] for idx in relation_ids),
                "inside_hits": sum(relation_rows[idx]["inside_hits"] for idx in relation_ids),
                "source_leak": sum(relation_rows[idx]["source_leak"] for idx in relation_ids),
                "preserves_full_packet_modes_on_source": bool(relation_ids)
                and sum(relation_rows[idx]["source_hits"] for idx in relation_ids) > 0
                and sum(relation_rows[idx]["source_leak"] for idx in relation_ids) == 0,
                "lands_in_Mat_2_Q_power_10": lands,
                "off_block_mass": off_block_mass,
                "nonzero_packet_entries": int(np.count_nonzero(matrix)),
                "target_action_matches": target_match,
                "relation_ids": relation_ids,
            }
        )
    return rows


def first_multiplicativity_violation(matrices: list[np.ndarray]) -> dict[str, Any]:
    triples = np.load(HALLOWEEN_NPZ)["triples"]
    for (left, right), group in groupby(triples, key=lambda row: (int(row[0]), int(row[1]))):
        lhs = matrices[left] @ matrices[right]
        rhs = np.zeros((20, 20), dtype=np.int64)
        terms = []
        for row in group:
            target = int(row[2])
            coefficient = int(row[3])
            rhs += coefficient * matrices[target]
            terms.append([target, coefficient])
        if np.array_equal(lhs, rhs):
            continue
        diff = lhs - rhs
        nonzero = np.argwhere(diff != 0)
        row, col = (int(nonzero[0, 0]), int(nonzero[0, 1]))
        return {
            "left_relation_id": left,
            "right_relation_id": right,
            "rhs_term_count": len(terms),
            "rhs_terms_head": terms[:12],
            "lhs_nonzero_entries": int(np.count_nonzero(lhs)),
            "rhs_nonzero_entries": int(np.count_nonzero(rhs)),
            "diff_nonzero_entries": int(len(nonzero)),
            "diff_l1": int(np.abs(diff).sum()),
            "first_difference": {
                "row": row,
                "col": col,
                "lhs": int(lhs[row, col]),
                "rhs": int(rhs[row, col]),
                "diff": int(diff[row, col]),
            },
        }
    return {}


def build_theorem() -> dict[str, Any]:
    context = build_packet_context()
    tube = load_json(FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT)
    relation_matrices, relation_rows = build_direct_relation_probe(context)
    preserving_rows = [
        row for row in relation_rows if row["preserves_full_packet_modes_on_source"]
    ]
    block_landing_rows = [
        row
        for row in relation_rows
        if row["inside_hits"] and row["lands_in_Mat_2_Q_power_10"]
    ]
    relation_target_matches = target_matches(relation_matrices, context["targets"])
    q42_rows = quotient_rows(relation_matrices, relation_rows, "q42", 42, context["targets"])
    q12_rows = quotient_rows(relation_matrices, relation_rows, "q12", 12, context["targets"])
    quotient_target_matches = {
        "q42": {
            name: [
                row["class_id"]
                for row in q42_rows
                if name in row["target_action_matches"]
            ]
            for name in context["targets"]
        },
        "q12": {
            name: [
                row["class_id"]
                for row in q12_rows
                if name in row["target_action_matches"]
            ]
            for name in context["targets"]
        },
    }
    q42_preserving = [
        row for row in q42_rows if row["preserves_full_packet_modes_on_source"]
    ]
    q12_preserving = [
        row for row in q12_rows if row["preserves_full_packet_modes_on_source"]
    ]
    violation = first_multiplicativity_violation(relation_matrices)
    summary = {
        "label_hypothesis": "mode_mask_equals_raw_point_id",
        "full_exposure_packet_count": len(context["full_packet_ids"]),
        "full_exposure_mode_count": len(context["mode_to_packet"]),
        "raw_relation_count": len(relation_rows),
        "relations_touching_full_packet_modes": sum(
            1 for row in relation_rows if row["source_hits"] > 0
        ),
        "relations_with_inside_hits": sum(1 for row in relation_rows if row["inside_hits"] > 0),
        "relations_preserving_full_packet_modes_on_source": len(preserving_rows),
        "leaking_relation_count": sum(
            1
            for row in relation_rows
            if row["source_hits"] > 0 and row["source_leak"] > 0
        ),
        "zero_source_hit_relation_count": sum(
            1 for row in relation_rows if row["source_hits"] == 0
        ),
        "block_landing_relation_count": len(block_landing_rows),
        "preserving_relation_ids": [row["relation_id"] for row in preserving_rows],
        "tube_identity_relation_ids": tube["derived"]["identity_relations_by_object"],
        "relation_target_action_matches": relation_target_matches,
        "quotient_target_action_matches": quotient_target_matches,
        "q42_preserving_class_ids": [row["class_id"] for row in q42_preserving],
        "q12_preserving_class_ids": [row["class_id"] for row in q12_preserving],
        "direct_compressed_map_is_multiplicative": violation == {},
    }
    checks = {
        "projective_packet_table_is_certified": context["spectral"].get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and context["spectral"].get("all_checks_pass") is True,
        "full_exposure_frame_is_certified": context["frame"].get("status")
        == "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        and context["frame"].get("all_checks_pass") is True,
        "packet_graph_is_certified": context["graph"].get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and context["graph"].get("all_checks_pass") is True,
        "tube_input_is_certified": tube.get("status")
        == "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED"
        and tube.get("all_checks_pass") is True,
        "full_mode_count_is_40": summary["full_exposure_mode_count"] == 40,
        "all_985_relations_touch_full_modes": summary[
            "relations_touching_full_packet_modes"
        ]
        == 985,
        "only_six_relations_preserve_full_modes": summary[
            "relations_preserving_full_packet_modes_on_source"
        ]
        == 6,
        "preserving_relations_are_tube_object_identities": summary[
            "preserving_relation_ids"
        ]
        == summary["tube_identity_relation_ids"],
        "all_nonidentity_relations_leak": summary["leaking_relation_count"] == 979,
        "direct_relation_restrictions_do_not_match_target_actions": all(
            not matches for matches in relation_target_matches.values()
        ),
        "q42_q12_aggregates_do_not_match_target_actions": all(
            not matches
            for quotient_matches in quotient_target_matches.values()
            for matches in quotient_matches.values()
        ),
        "direct_compressed_map_fails_multiplicativity": violation
        == {
            "left_relation_id": 53,
            "right_relation_id": 291,
            "rhs_term_count": 1,
            "rhs_terms_head": [[0, 8]],
            "lhs_nonzero_entries": 6,
            "rhs_nonzero_entries": 8,
            "diff_nonzero_entries": 14,
            "diff_l1": 70,
            "first_difference": {
                "row": 4,
                "col": 6,
                "lhs": 0,
                "rhs": 8,
                "diff": -8,
            },
        },
        "q42_preserving_classes_are_only_identity_singletons": q42_preserving
        == [
            {
                "quotient": "q42",
                "class_id": 2,
                "relation_count": 1,
                "source_hits": 3,
                "inside_hits": 3,
                "source_leak": 0,
                "preserves_full_packet_modes_on_source": True,
                "lands_in_Mat_2_Q_power_10": True,
                "off_block_mass": 0,
                "nonzero_packet_entries": 3,
                "target_action_matches": [],
                "relation_ids": [227],
            },
            {
                "quotient": "q42",
                "class_id": 3,
                "relation_count": 1,
                "source_hits": 8,
                "inside_hits": 8,
                "source_leak": 0,
                "preserves_full_packet_modes_on_source": True,
                "lands_in_Mat_2_Q_power_10": True,
                "off_block_mass": 0,
                "nonzero_packet_entries": 8,
                "target_action_matches": [],
                "relation_ids": [349],
            },
        ],
        "q12_preserving_class_is_identity_pair": q12_preserving
        == [
            {
                "quotient": "q12",
                "class_id": 1,
                "relation_count": 2,
                "source_hits": 11,
                "inside_hits": 11,
                "source_leak": 0,
                "preserves_full_packet_modes_on_source": True,
                "lands_in_Mat_2_Q_power_10": True,
                "off_block_mass": 0,
                "nonzero_packet_entries": 11,
                "target_action_matches": [],
                "relation_ids": [227, 349],
            }
        ],
    }
    report = {
        "schema": "d20.theorem.d20_a985_direct_packet_bridge_obstruction",
        "status": "D20_A985_DIRECT_PACKET_BRIDGE_OBSTRUCTION_CERTIFIED",
        "object": "D20",
        "definition": {
            "direct_label_hypothesis": (
                "Use each full-exposure packet mode mask as the raw point id with the same "
                "integer value, restrict each A985 relation orbital to those 40 raw points, "
                "then aggregate the restricted 40-mode action to the 20 packet basis."
            ),
            "target_actions": [
                "2I",
                "4S",
                "2I+4S",
            ],
            "scope": (
                "This is a no-go for the literal current labels only; it does not rule out "
                "a future nontrivial point-to-mode relabelling or an externally supplied "
                "relation/object/q42/q12-to-packet projection."
            ),
        },
        "claim": (
            "Under the literal current label hypothesis mode_mask == raw point id, the "
            "A985 relation basis does not supply a labelled packet bridge. All 985 "
            "relations touch the 40 full-exposure modes, but 979 leak out of that subspace; "
            "the only six preserving relations are exactly the tube object identity "
            "relations. No direct relation restriction, q42 aggregate, or q12 aggregate "
            "equals the certified packet actions 2I, 4S, or 2I+4S, and the compressed "
            "relation map fails A985 multiplication on relation product 53*291."
        ),
        "inputs": {
            "relation_memberships_npz": input_record(RELATION_MEMBERSHIPS_NPZ),
            "quotients_npz": input_record(QUOTIENTS_NPZ),
            "halloween_npz": input_record(HALLOWEEN_NPZ),
            "projective_packet_spectral_charge_table_report": input_record(
                PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE
            ),
            "full_exposure_canonical_labelled_frame_report": input_record(
                FULL_EXPOSURE_CANONICAL_LABELLED_FRAME
            ),
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
            "fourier_screen0_tube_central_element_report": input_record(
                FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT
            ),
        },
        "derived": {
            "direct_bridge_summary": summary,
            "preserving_relation_rows": preserving_rows,
            "preserving_relation_rows_sha256": sha_json(preserving_rows),
            "q42_preserving_class_rows": q42_preserving,
            "q42_preserving_class_rows_sha256": sha_json(q42_preserving),
            "q12_preserving_class_rows": q12_preserving,
            "q12_preserving_class_rows_sha256": sha_json(q12_preserving),
            "multiplicativity_violation": violation,
            "relation_touch_histogram": {
                "source_hit_histogram": histogram(
                    Counter(row["source_hits"] for row in relation_rows)
                ),
                "inside_hit_histogram": histogram(
                    Counter(row["inside_hits"] for row in relation_rows)
                ),
                "source_leak_zero_count": sum(
                    1 for row in relation_rows if row["source_leak"] == 0
                ),
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "negative_boundary": (
                "The direct raw-point interpretation of packet mode masks is not the missing "
                "A985/tube/q42/q12 bridge."
            ),
            "what_remains_open": (
                "A nontrivial certified point-to-mode relabelling or a separately emitted "
                "relation/object/q42/q12 packet projection could still exist."
            ),
            "next_test_shape": (
                "Any future bridge must provide explicit columns before SNF or A985 "
                "multiplication tests can certify a quotient action."
            ),
        },
        "next_highest_yield_item": (
            "Search for a nontrivial point-to-mode relabelling using the object and q42/q12 "
            "labels; the literal mode-mask/raw-point identification is now certified as a no-go."
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
        "schema": "d20.theorem.d20_a985_direct_packet_bridge_obstruction_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "test the literal current-label A985 relation-to-packet bridge",
            "record the direct relation, q42, and q12 leakage and target-action failures",
            "record a concrete A985 multiplication failure for the compressed direct map",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
