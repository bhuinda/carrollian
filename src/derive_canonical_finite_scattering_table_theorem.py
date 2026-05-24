from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "canonical_finite_scattering_table"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS / "theorems" / "hidden_packet_charge_frame_classifier" / "report.json"
)
GLOBAL_COUNTERTERM_LATTICE_REPORT = (
    D20_INVARIANTS / "theorems" / "global_counterterm_lattice" / "report.json"
)
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"

RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
DIRECTED_TRANSITION_COUNT = MASK_COUNT * RESIDUE_RANK
UNDIRECTED_TRANSITION_COUNT = DIRECTED_TRANSITION_COUNT // 2
GAMMA8_MASK = 1 << 8


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


def load_primitive_cycles() -> list[dict[str, Any]]:
    rows = []
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "optical_action": int(row["optical_action"]),
                    "edge_ids": [int(value) for value in row["edge_ids"].split()],
                    "vertices": [int(value) for value in row["vertices"].split()],
                }
            )
    return sorted(rows, key=lambda row: row["cycle_id"])


def signature_entry(packet_row: dict[str, Any]) -> dict[str, Any]:
    signature = packet_row["complete_charge_action_signature"]
    return {
        "mask": int(packet_row["mask"]),
        "hidden_packet": packet_row["hidden_packet"],
        "corrected_R33_mod26": int(packet_row["corrected_R33_mod26"]),
        "height_action": int(packet_row["height_action"]),
        "complete_charge_action_signature": signature,
        "signature_sha256": sha_json(signature),
    }


def packet_transfer(source_packet: str, target_packet: str) -> str:
    return f"{source_packet}_to_{target_packet}"


def build_transition_rows(
    packet_by_mask: dict[int, dict[str, Any]],
    signatures_by_mask: dict[int, dict[str, Any]],
    primitive_cycles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    transition_id = 0
    for source_mask in range(MASK_COUNT):
        source = packet_by_mask[source_mask]
        source_signature = signatures_by_mask[source_mask]
        for generator in primitive_cycles:
            generator_id = int(generator["cycle_id"])
            target_mask = source_mask ^ (1 << generator_id)
            target = packet_by_mask[target_mask]
            target_signature = signatures_by_mask[target_mask]
            source_height = int(source["height_action"])
            target_height = int(target["height_action"])
            source_r33 = int(source["corrected_R33_mod26"])
            target_r33 = int(target["corrected_R33_mod26"])
            rows.append(
                {
                    "transition_id": transition_id,
                    "source_mask": source_mask,
                    "target_mask": target_mask,
                    "generator_cycle_id": generator_id,
                    "toggle": "add" if ((source_mask >> generator_id) & 1) == 0 else "remove",
                    "source_hidden_packet": source["hidden_packet"],
                    "target_hidden_packet": target["hidden_packet"],
                    "packet_transfer": packet_transfer(source["hidden_packet"], target["hidden_packet"]),
                    "incoming_signature_sha256": source_signature["signature_sha256"],
                    "outgoing_signature_sha256": target_signature["signature_sha256"],
                    "source_height_action": source_height,
                    "target_height_action": target_height,
                    "generator_height_action": int(generator["optical_action"]),
                    "height_flux_delta": target_height - source_height,
                    "source_R33_mod26": source_r33,
                    "target_R33_mod26": target_r33,
                    "hidden_R33_transfer_mod26": (target_r33 - source_r33) % 26,
                }
            )
            transition_id += 1
    return rows


def generator_summary_rows(
    transition_rows: list[dict[str, Any]],
    primitive_cycles: list[dict[str, Any]],
    corrected_basis_clock: list[int],
) -> list[dict[str, Any]]:
    rows = []
    by_generator: dict[int, list[dict[str, Any]]] = {
        generator["cycle_id"]: [] for generator in primitive_cycles
    }
    for row in transition_rows:
        by_generator[int(row["generator_cycle_id"])].append(row)
    for generator in primitive_cycles:
        generator_id = int(generator["cycle_id"])
        rows_for_generator = by_generator[generator_id]
        packet_histogram = Counter(row["packet_transfer"] for row in rows_for_generator)
        transfer_histogram = Counter(row["hidden_R33_transfer_mod26"] for row in rows_for_generator)
        height_delta_histogram = Counter(row["height_flux_delta"] for row in rows_for_generator)
        rows.append(
            {
                "generator_cycle_id": generator_id,
                "length": int(generator["length"]),
                "optical_action": int(generator["optical_action"]),
                "corrected_basis_clock_mod26": int(corrected_basis_clock[generator_id]),
                "directed_transition_count": len(rows_for_generator),
                "packet_transfer_histogram": dict(sorted(packet_histogram.items())),
                "hidden_R33_transfer_mod26_histogram": {
                    str(key): int(transfer_histogram[key]) for key in sorted(transfer_histogram)
                },
                "height_flux_delta_histogram": {
                    str(key): int(height_delta_histogram[key])
                    for key in sorted(height_delta_histogram)
                },
            }
        )
    return rows


def reverse_transition_checks(transition_rows: list[dict[str, Any]]) -> bool:
    by_key = {
        (
            int(row["source_mask"]),
            int(row["target_mask"]),
            int(row["generator_cycle_id"]),
        ): row
        for row in transition_rows
    }
    for row in transition_rows:
        reverse = by_key.get(
            (
                int(row["target_mask"]),
                int(row["source_mask"]),
                int(row["generator_cycle_id"]),
            )
        )
        if reverse is None:
            return False
        if int(reverse["height_flux_delta"]) != -int(row["height_flux_delta"]):
            return False
        if int(reverse["hidden_R33_transfer_mod26"]) != int(row["hidden_R33_transfer_mod26"]):
            return False
    return True


def build_theorem() -> dict[str, Any]:
    classifier = load_json(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    global_lattice = load_json(GLOBAL_COUNTERTERM_LATTICE_REPORT)
    primitive_cycles = load_primitive_cycles()

    packet_rows = sorted(
        classifier["derived"]["packet_rows"],
        key=lambda row: int(row["mask"]),
    )
    packet_by_mask = {int(row["mask"]): row for row in packet_rows}
    signature_registry = [signature_entry(row) for row in packet_rows]
    signatures_by_mask = {row["mask"]: row for row in signature_registry}
    corrected_basis_clock = [
        int(value) for value in global_lattice["derived"]["corrected_basis_clock_mod26"]
    ]
    transition_rows = build_transition_rows(packet_by_mask, signatures_by_mask, primitive_cycles)
    generator_summaries = generator_summary_rows(
        transition_rows, primitive_cycles, corrected_basis_clock
    )

    packet_transfer_histogram = Counter(row["packet_transfer"] for row in transition_rows)
    hidden_transfer_histogram = Counter(row["hidden_R33_transfer_mod26"] for row in transition_rows)
    height_delta_histogram = Counter(row["height_flux_delta"] for row in transition_rows)
    toggle_histogram = Counter(row["toggle"] for row in transition_rows)
    gamma8_scattering_star = [
        row for row in transition_rows if int(row["source_mask"]) == GAMMA8_MASK
    ]
    signature_hashes = [row["signature_sha256"] for row in signature_registry]
    expected_height_delta_histogram = Counter()
    for cycle in primitive_cycles:
        action = int(cycle["optical_action"])
        expected_height_delta_histogram[action] += MASK_COUNT // 2
        expected_height_delta_histogram[-action] += MASK_COUNT // 2

    checks = {
        "hidden_packet_charge_frame_classifier_is_certified": classifier.get("status")
        == "D20_HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and classifier.get("all_checks_pass") is True,
        "global_counterterm_lattice_is_certified": global_lattice.get("status")
        == "D20_GLOBAL_COUNTERTERM_LATTICE_CERTIFIED"
        and global_lattice.get("all_checks_pass") is True,
        "primitive_generator_count_is_11": len(primitive_cycles) == RESIDUE_RANK
        and [row["cycle_id"] for row in primitive_cycles] == list(range(RESIDUE_RANK)),
        "signature_registry_separates_all_masks": len(signature_registry) == MASK_COUNT
        and len(set(signature_hashes)) == MASK_COUNT,
        "directed_transition_count_is_2048_times_11": len(transition_rows)
        == DIRECTED_TRANSITION_COUNT,
        "undirected_transition_count_is_11264": len(transition_rows) // 2
        == UNDIRECTED_TRANSITION_COUNT,
        "all_transitions_are_basis_xor_steps": all(
            int(row["target_mask"])
            == (int(row["source_mask"]) ^ (1 << int(row["generator_cycle_id"])))
            for row in transition_rows
        ),
        "every_transition_has_involutive_reverse": reverse_transition_checks(transition_rows),
        "toggle_histogram_is_balanced": dict(toggle_histogram) == {
            "add": UNDIRECTED_TRANSITION_COUNT,
            "remove": UNDIRECTED_TRANSITION_COUNT,
        },
        "hidden_r33_transfer_histogram_matches_corrected_basis": {
            str(key): int(hidden_transfer_histogram[key]) for key in sorted(hidden_transfer_histogram)
        }
        == {"0": 2048, "13": 20480},
        "packet_transfer_histogram_matches_basis_clock": dict(packet_transfer_histogram)
        == {
            "kernel_to_kernel": 1024,
            "kernel_to_odd": 10240,
            "odd_to_kernel": 10240,
            "odd_to_odd": 1024,
        },
        "generator3_is_packet_preserving_and_others_flip": all(
            (
                summary["generator_cycle_id"] == 3
                and summary["packet_transfer_histogram"]
                == {"kernel_to_kernel": 1024, "odd_to_odd": 1024}
            )
            or (
                summary["generator_cycle_id"] != 3
                and summary["packet_transfer_histogram"]
                == {"kernel_to_odd": 1024, "odd_to_kernel": 1024}
            )
            for summary in generator_summaries
        ),
        "height_flux_delta_histogram_matches_generator_actions": {
            str(key): int(height_delta_histogram[key]) for key in sorted(height_delta_histogram)
        }
        == {str(key): int(expected_height_delta_histogram[key]) for key in sorted(expected_height_delta_histogram)},
        "gamma8_scattering_star_has_11_generator_rows": len(gamma8_scattering_star)
        == RESIDUE_RANK
        and sorted(row["generator_cycle_id"] for row in gamma8_scattering_star)
        == list(range(RESIDUE_RANK)),
        "gamma8_self_generator_returns_to_zero_with_negative_height_flux": any(
            row["generator_cycle_id"] == 8
            and row["target_mask"] == 0
            and row["height_flux_delta"] == -374784
            and row["hidden_R33_transfer_mod26"] == 13
            for row in gamma8_scattering_star
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        if all_checks_pass
        else "D20_CANONICAL_FINITE_SCATTERING_TABLE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.canonical_finite_scattering_table",
        "status": status,
        "object": "d20",
        "claim": (
            "The complete hidden-packet classifier determines a canonical finite scattering table on the "
            "11-generator closed-return residue cube. Each directed transition toggles one primitive "
            "closed-return generator and records incoming and outgoing complete packet signatures, signed "
            "height-flux delta, and hidden R33 transfer. Generator 3 preserves the hidden packet; the other "
            "ten generators flip kernel and odd packets."
        ),
        "definition": {
            "finite_scattering_transition": "T_i(mask)=mask xor 2^i for primitive generator i.",
            "incoming_packet_signature": (
                "the complete_charge_action_signature from hidden_packet_charge_frame_classifier at mask"
            ),
            "outgoing_packet_signature": (
                "the complete_charge_action_signature from hidden_packet_charge_frame_classifier at T_i(mask)"
            ),
            "height_flux_delta": "height_action(T_i(mask))-height_action(mask).",
            "hidden_R33_transfer": (
                "corrected_R33_mod26(T_i(mask))-corrected_R33_mod26(mask) modulo 26."
            ),
        },
        "inputs": {
            "hidden_packet_charge_frame_classifier_report": {
                "path": rel(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
            "global_counterterm_lattice_report": {
                "path": rel(GLOBAL_COUNTERTERM_LATTICE_REPORT),
                "sha256": sha_file(GLOBAL_COUNTERTERM_LATTICE_REPORT),
            },
            "primitive_cycles": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
        },
        "derived": {
            "transition_counts": {
                "residue_mask_count": MASK_COUNT,
                "primitive_generator_count": RESIDUE_RANK,
                "directed_transition_count": len(transition_rows),
                "undirected_transition_count": UNDIRECTED_TRANSITION_COUNT,
            },
            "signature_registry": signature_registry,
            "signature_registry_sha256": sha_json(signature_registry),
            "generator_summaries": generator_summaries,
            "packet_transfer_histogram": dict(packet_transfer_histogram),
            "hidden_R33_transfer_mod26_histogram": {
                str(key): int(hidden_transfer_histogram[key])
                for key in sorted(hidden_transfer_histogram)
            },
            "height_flux_delta_histogram": {
                str(key): int(height_delta_histogram[key])
                for key in sorted(height_delta_histogram)
            },
            "toggle_histogram": dict(toggle_histogram),
            "gamma8_scattering_star": gamma8_scattering_star,
            "transition_rows": transition_rows,
            "transition_rows_sha256": sha_json(transition_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "every complete packet signature has a canonical table of primitive-generator exits",
                "the hidden order-two character makes ten generators kernel/odd flippers",
                "the single zero corrected generator preserves kernel and odd packets",
                "height flux is a signed transition quantity and reverses under the involutive reverse edge",
            ],
            "what_this_does_not_prove": (
                "This is a finite residue-cube scattering table. It does not yet assign Loop_297/A985 "
                "transition amplitudes or continuum scattering amplitudes."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Lift the canonical finite scattering rows through the certified boundary-to-Loop_297 map and "
            "attach tube/A985 transition amplitudes to the packet transitions."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.canonical_finite_scattering_table_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify hidden packet classifier and global counterterm inputs",
            "verify signature registry separates all 2048 masks",
            "verify 2048 x 11 directed primitive-generator transitions",
            "verify every transition has an involutive reverse with opposite height flux",
            "verify hidden R33 transfer and packet-transfer histograms",
            "verify generator 3 preserves packets and the other ten generators flip packets",
            "verify gamma_8 scattering star",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
