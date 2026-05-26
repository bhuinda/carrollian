from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "projective_packet_spectral_charge_table"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_kernel_packet_tenfold_way"
    / "report.json"
)


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


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def tuple_histogram(counter: Counter[tuple[Any, ...]]) -> dict[str, int]:
    return {"|".join(str(part) for part in key): int(counter[key]) for key in sorted(counter)}


def mode_pair(packet: dict[str, Any], mode_by_mask: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    return [mode_by_mask[int(mask)] for mask in packet["mode_masks"]]


def packet_charge_row(packet: dict[str, Any], mode_by_mask: dict[int, dict[str, Any]]) -> dict[str, Any]:
    modes = mode_pair(packet, mode_by_mask)
    adjacency_pair = [int(row["adjacency_eigenvalue"]) for row in modes]
    laplacian_pair = [int(row["laplacian_eigenvalue"]) for row in modes]
    hidden_clock_pair = [int(row["corrected_hidden_clock_mod26"]) for row in modes]
    gamma8_mode_count = sum(1 for row in modes if bool(row["gamma8_support"]))
    sector26_clock_pair = [int(value) for value in packet["sector26_clock_pair"]]
    sector26_sum = sum(sector26_clock_pair) % 26
    sector26_delta = int(packet["sector26_clock_delta_mod26"])
    loop_atom_count = int(packet["loop297_atom_union_count"])
    laplacian_trace = sum(laplacian_pair)
    adjacency_trace = sum(adjacency_pair)
    coarse_class = [
        laplacian_trace,
        sector26_delta,
        gamma8_mode_count,
        loop_atom_count,
    ]
    fine_class = [
        laplacian_trace,
        sector26_sum,
        sector26_delta,
        gamma8_mode_count,
        loop_atom_count,
    ]
    return {
        "packet_id": int(packet["packet_id"]),
        "radical_character": int(packet["radical_character"]),
        "active_sigma": int(packet["active_sigma"]),
        "dimension": int(packet["dimension"]),
        "central_character": int(packet["central_character"]),
        "tenfold_canonical_class": "AI",
        "tenfold_optional_active_hamiltonian_class": "BDI",
        "mode_masks": [int(mask) for mask in packet["mode_masks"]],
        "adjacency_eigenvalue_pair": adjacency_pair,
        "adjacency_trace": adjacency_trace,
        "laplacian_eigenvalue_pair": laplacian_pair,
        "laplacian_trace": laplacian_trace,
        "sector26_clock_pair": sector26_clock_pair,
        "sector26_clock_sum_mod26": sector26_sum,
        "sector26_clock_delta_mod26": sector26_delta,
        "sector26_clock_balanced": sector26_delta == 0,
        "sector26_clock_zero_touched": 0 in sector26_clock_pair,
        "sector26_clock_zero_pair": sector26_clock_pair == [0, 0],
        "corrected_hidden_clock_pair": hidden_clock_pair,
        "corrected_hidden_clock_sum_mod26": sum(hidden_clock_pair) % 26,
        "gamma8_mode_count": gamma8_mode_count,
        "gamma8_touched": bool(packet["gamma8_touched"]),
        "loop297_atom_union_count": loop_atom_count,
        "loop297_atom_union_ids": [int(atom_id) for atom_id in packet["loop297_atom_union_ids"]],
        "full_loop297_atom_exposure": loop_atom_count == 25,
        "mode_support_weights": [int(row["support_weight"]) for row in modes],
        "mode_active_step_atom_counts": [
            int(row["active_step_atom_count"]) for row in modes
        ],
        "hidden_projection_pair": [str(row["hidden_projection_type"]) for row in modes],
        "coarse_spectral_charge_key": "|".join(str(value) for value in coarse_class),
        "fine_spectral_charge_key": "|".join(str(value) for value in fine_class),
    }


def build_theorem() -> dict[str, Any]:
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    packets = load_json(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT)
    mode_rows = fourier["derived"]["mode_rows"]
    mode_by_mask = {int(row["mode_mask"]): row for row in mode_rows}
    packet_rows = packets["derived"]["packet_rows"]
    table = [packet_charge_row(row, mode_by_mask) for row in packet_rows]

    laplacian_trace_histogram = histogram(Counter(row["laplacian_trace"] for row in table))
    adjacency_trace_histogram = histogram(Counter(row["adjacency_trace"] for row in table))
    sector26_clock_sum_histogram = histogram(
        Counter(row["sector26_clock_sum_mod26"] for row in table)
    )
    sector26_clock_delta_histogram = histogram(
        Counter(row["sector26_clock_delta_mod26"] for row in table)
    )
    hidden_clock_pair_histogram = tuple_histogram(
        Counter(tuple(row["corrected_hidden_clock_pair"]) for row in table)
    )
    hidden_clock_sum_histogram = histogram(
        Counter(row["corrected_hidden_clock_sum_mod26"] for row in table)
    )
    gamma8_mode_count_histogram = histogram(Counter(row["gamma8_mode_count"] for row in table))
    loop_atom_union_histogram = histogram(
        Counter(row["loop297_atom_union_count"] for row in table)
    )
    central_character_histogram = histogram(Counter(row["central_character"] for row in table))
    tenfold_class_histogram = histogram(Counter(row["tenfold_canonical_class"] for row in table))
    optional_tenfold_class_histogram = histogram(
        Counter(row["tenfold_optional_active_hamiltonian_class"] for row in table)
    )
    coarse_charge_class_histogram = histogram(
        Counter(row["coarse_spectral_charge_key"] for row in table)
    )
    fine_charge_class_histogram = histogram(
        Counter(row["fine_spectral_charge_key"] for row in table)
    )

    full_loop_packets = [row for row in table if row["full_loop297_atom_exposure"]]
    clock_zero_packets = [row for row in table if row["sector26_clock_zero_touched"]]
    balanced_packets = [row for row in table if row["sector26_clock_balanced"]]
    distinguished = {
        "full_loop297_atom_exposure_packet_ids": [
            row["packet_id"] for row in full_loop_packets
        ],
        "clock_zero_touched_packet_ids": [row["packet_id"] for row in clock_zero_packets],
        "full_loop297_and_clock_zero_packet_ids": [
            row["packet_id"]
            for row in full_loop_packets
            if row["sector26_clock_zero_touched"]
        ],
        "full_loop297_and_clock_balanced_packet_ids": [
            row["packet_id"]
            for row in full_loop_packets
            if row["sector26_clock_balanced"]
        ],
        "full_loop297_and_gamma8_packet_ids": [
            row["packet_id"] for row in full_loop_packets if row["gamma8_touched"]
        ],
        "lowest_laplacian_trace_packet_ids": [
            row["packet_id"] for row in table if row["laplacian_trace"] == 4
        ],
        "highest_laplacian_trace_packet_ids": [
            row["packet_id"] for row in table if row["laplacian_trace"] == 40
        ],
    }

    checks = {
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "projective_kernel_packet_tenfold_way_is_certified": packets.get("status")
        == "D20_PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_CERTIFIED"
        and packets.get("all_checks_pass") is True,
        "packet_table_has_512_rows_and_total_dimension_1024": len(table) == 512
        and sum(row["dimension"] for row in table) == 1024,
        "packet_table_mode_masks_are_unique_and_cover_kernel": len(
            {mask for row in table for mask in row["mode_masks"]}
        )
        == 1024,
        "central_character_is_negative_on_all_packets": central_character_histogram == {"-1": 512},
        "tenfold_labels_are_ai_and_optional_bdi_on_all_packets": tenfold_class_histogram
        == {"AI": 512}
        and optional_tenfold_class_histogram == {"BDI": 512},
        "laplacian_trace_histogram_matches_packet_spectrum": laplacian_trace_histogram
        == {
            "4": 1,
            "8": 9,
            "12": 36,
            "16": 84,
            "20": 126,
            "24": 126,
            "28": 84,
            "32": 36,
            "36": 9,
            "40": 1,
        },
        "adjacency_trace_histogram_matches_packet_spectrum": adjacency_trace_histogram
        == {
            "-18": 1,
            "-14": 9,
            "-10": 36,
            "-6": 84,
            "-2": 126,
            "2": 126,
            "6": 84,
            "10": 36,
            "14": 9,
            "18": 1,
        },
        "sector26_clock_delta_splits_evenly": sector26_clock_delta_histogram
        == {"0": 256, "8": 256},
        "sector26_clock_sum_histogram_matches": sector26_clock_sum_histogram
        == {
            "0": 41,
            "2": 39,
            "4": 42,
            "6": 40,
            "8": 40,
            "10": 42,
            "12": 39,
            "14": 41,
            "16": 39,
            "18": 36,
            "20": 38,
            "22": 36,
            "24": 39,
        },
        "hidden_clock_cancels_packetwise": hidden_clock_sum_histogram == {"0": 512}
        and hidden_clock_pair_histogram == {"0|0": 256, "13|13": 256},
        "gamma8_mode_count_splits_evenly": gamma8_mode_count_histogram == {"0": 256, "2": 256},
        "loop297_atom_union_histogram_matches": loop_atom_union_histogram
        == {
            "10": 1,
            "11": 1,
            "12": 4,
            "13": 5,
            "14": 8,
            "15": 12,
            "16": 14,
            "17": 21,
            "18": 25,
            "19": 43,
            "20": 55,
            "21": 56,
            "22": 80,
            "23": 98,
            "24": 69,
            "25": 20,
        },
        "distinguished_full_loop_packets_match": distinguished[
            "full_loop297_atom_exposure_packet_ids"
        ]
        == [
            174,
            175,
            190,
            191,
            238,
            239,
            246,
            247,
            254,
            255,
            430,
            431,
            446,
            447,
            494,
            495,
            502,
            503,
            510,
            511,
        ],
        "unique_full_loop_clock_zero_packet_is_239": distinguished[
            "full_loop297_and_clock_zero_packet_ids"
        ]
        == [239],
        "full_loop_balanced_and_gamma8_counts_are_10_each": len(
            distinguished["full_loop297_and_clock_balanced_packet_ids"]
        )
        == 10
        and len(distinguished["full_loop297_and_gamma8_packet_ids"]) == 10,
        "clock_zero_touched_packet_count_is_62": len(
            distinguished["clock_zero_touched_packet_ids"]
        )
        == 62,
        "balanced_packet_count_is_256": len(balanced_packets) == 256,
        "spectral_charge_class_counts_are_certified": len(coarse_charge_class_histogram) == 138
        and max(coarse_charge_class_histogram.values()) == 19
        and len(fine_charge_class_histogram) == 440
        and max(fine_charge_class_histogram.values()) == 3,
        "extreme_spectral_packets_are_endpoints": distinguished[
            "lowest_laplacian_trace_packet_ids"
        ]
        == [0]
        and distinguished["highest_laplacian_trace_packet_ids"] == [511],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        if all_checks_pass
        else "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.projective_packet_spectral_charge_table",
        "status": status,
        "object": "d20",
        "claim": (
            "The 512 signed projective kernel packets carry a certified packet-level spectral/charge table. "
            "Each row records the two Fourier modes, spectral traces, sector-26 clocks, hidden-clock "
            "cancellation, gamma8 incidence, Loop_297 atom exposure, central character, and finite tenfold "
            "labels. The table identifies the maximal Loop_297 exposure packets, the unique full-exposure "
            "sector-26 clock-zero packet, and the endpoint spectral packets."
        ),
        "definition": {
            "packet_spectral_charge_row": (
                "A packet row is the two-mode central-negative packet with adjacency/laplacian traces, "
                "sector-26 sum and delta, corrected-hidden-clock sum, gamma8 count, and Loop_297 atom union."
            ),
            "coarse_spectral_charge_key": (
                "(laplacian_trace, sector26_delta, gamma8_mode_count, loop297_atom_union_count)."
            ),
            "fine_spectral_charge_key": (
                "(laplacian_trace, sector26_sum, sector26_delta, gamma8_mode_count, loop297_atom_union_count)."
            ),
        },
        "inputs": {
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(FOURIER_MODE_CLASSIFIER_REPORT),
            },
            "projective_kernel_packet_tenfold_way_report": {
                "path": rel(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT),
                "sha256": sha_file(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT),
            },
        },
        "derived": {
            "spectral_charge_summary": {
                "packet_count": len(table),
                "total_dimension": sum(row["dimension"] for row in table),
                "central_character_histogram": central_character_histogram,
                "tenfold_canonical_class_histogram": tenfold_class_histogram,
                "tenfold_optional_active_hamiltonian_class_histogram": (
                    optional_tenfold_class_histogram
                ),
                "coarse_spectral_charge_class_count": len(coarse_charge_class_histogram),
                "coarse_spectral_charge_max_multiplicity": max(
                    coarse_charge_class_histogram.values()
                ),
                "fine_spectral_charge_class_count": len(fine_charge_class_histogram),
                "fine_spectral_charge_max_multiplicity": max(
                    fine_charge_class_histogram.values()
                ),
                "full_loop297_atom_exposure_packet_count": len(full_loop_packets),
                "clock_zero_touched_packet_count": len(clock_zero_packets),
                "balanced_packet_count": len(balanced_packets),
            },
            "histograms": {
                "laplacian_trace": laplacian_trace_histogram,
                "adjacency_trace": adjacency_trace_histogram,
                "sector26_clock_sum_mod26": sector26_clock_sum_histogram,
                "sector26_clock_delta_mod26": sector26_clock_delta_histogram,
                "corrected_hidden_clock_pair": hidden_clock_pair_histogram,
                "corrected_hidden_clock_sum_mod26": hidden_clock_sum_histogram,
                "gamma8_mode_count": gamma8_mode_count_histogram,
                "loop297_atom_union_count": loop_atom_union_histogram,
                "coarse_spectral_charge_class": coarse_charge_class_histogram,
                "fine_spectral_charge_class": fine_charge_class_histogram,
            },
            "distinguished_packet_sets": distinguished,
            "packet_spectral_charge_rows": table,
            "packet_spectral_charge_rows_sha256": sha_json(table),
        },
        "interpretation": {
            "what_this_proves": [
                "the signed packets now have a stable spectral/charge ledger",
                "sector-26 clock balance splits the packets exactly in half",
                "hidden clock cancels inside every packet",
                "only one full Loop_297 exposure packet is also sector-26 clock-zero",
                "the extreme spectral packets are packet 0 and packet 511",
            ],
            "what_this_does_not_prove": (
                "This does not yet assign physical mass/angular-momentum names to the packet charges. It "
                "certifies the finite table that such a naming must respect."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Promote the packet spectral/charge rows into a finite charge-frame classifier: name the "
            "mass/clock/exposure/gamma8 axes and isolate the unique full-exposure clock-zero packet."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.projective_packet_spectral_charge_table_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify Fourier classifier and projective packet decomposition inputs",
            "construct 512 packet spectral/charge rows",
            "verify packet dimensions and mode coverage",
            "verify spectral trace, sector-26 clock, hidden-clock, gamma8, and Loop_297 histograms",
            "identify maximal Loop_297 exposure, clock-zero, balanced, and endpoint spectral packet sets",
            "classify coarse and fine spectral/charge key multiplicities",
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
