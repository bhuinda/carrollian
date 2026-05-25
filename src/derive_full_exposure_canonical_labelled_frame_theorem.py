from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.derive_full_exposure_radical_gate_stabilizer_lift_theorem import (
    pattern_bits,
)
from src.derive_full_exposure_label_breaking_factorization_theorem import (
    build_affine_rows,
)
from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_canonical_labelled_frame"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_breaking_factorization"
    / "report.json"
)
FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_radical_gate_stabilizer_lift"
    / "report.json"
)
PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)

CANONICAL_FRAME_FIELDS = [
    "full_loop297_atom_exposure",
    "mass_frame",
    "clock_frame",
    "gamma_frame",
    "sector26_clock_sum_mod26",
    "sector26_clock_delta_mod26",
    "sector26_clock_zero_pair",
    "sector26_clock_zero_touched",
    "fine_spectral_charge_key",
]
PACKET239_SELECTION_FIELDS = [
    "full_loop297_atom_exposure",
    "sector26_clock_pair",
    "sector26_clock_sum_mod26",
    "sector26_clock_delta_mod26",
    "sector26_clock_zero_pair",
    "sector26_clock_zero_touched",
]


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


def histogram(values: list[Any]) -> dict[str, int]:
    counter = Counter(values)
    return {str(key): int(counter[key]) for key in sorted(counter)}


def frame_key(row: dict[str, Any]) -> list[Any]:
    return [row.get(field) for field in CANONICAL_FRAME_FIELDS]


def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    zero_pair_rank = 0 if row["sector26_clock_zero_pair"] and row["sector26_clock_zero_touched"] else 1
    gamma_rank = 1 if row["gamma8_touched"] else 0
    return (
        zero_pair_rank,
        gamma_rank,
        int(row["sector26_clock_sum_mod26"]),
        int(row["sector26_clock_delta_mod26"]),
        row["fine_spectral_charge_key"],
    )


def packet239_selector(row: dict[str, Any]) -> bool:
    return (
        row.get("full_loop297_atom_exposure") is True
        and row.get("sector26_clock_pair") == [0, 0]
        and row.get("sector26_clock_sum_mod26") == 0
        and row.get("sector26_clock_delta_mod26") == 0
        and row.get("sector26_clock_zero_pair") is True
        and row.get("sector26_clock_zero_touched") is True
    )


def build_frame_rows(
    packets: list[int],
    radicals: list[int],
    gate_support: list[int],
    charge_rows: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    pattern_by_radical = {
        radical: gate_support[index]
        for index, radical in enumerate(radicals)
    }
    rows = []
    for packet in packets:
        row = charge_rows[packet]
        radical = packet // 2
        rows.append(
            {
                "packet_id": packet,
                "radical": radical,
                "active_sigma": packet % 2,
                "local_pattern": pattern_bits(pattern_by_radical[radical]),
                "canonical_frame_key": frame_key(row),
                "selection_signature": {
                    field: row[field]
                    for field in PACKET239_SELECTION_FIELDS
                },
                "mass_frame": row["mass_frame"],
                "clock_frame": row["clock_frame"],
                "gamma_frame": row["gamma_frame"],
                "full_loop297_atom_exposure": row["full_loop297_atom_exposure"],
                "sector26_clock_pair": row["sector26_clock_pair"],
                "sector26_clock_sum_mod26": row["sector26_clock_sum_mod26"],
                "sector26_clock_delta_mod26": row["sector26_clock_delta_mod26"],
                "sector26_clock_zero_pair": row["sector26_clock_zero_pair"],
                "sector26_clock_zero_touched": row["sector26_clock_zero_touched"],
                "gamma8_touched": row["gamma8_touched"],
                "gamma8_mode_count": row["gamma8_mode_count"],
                "adjacency_trace": row["adjacency_trace"],
                "laplacian_trace": row["laplacian_trace"],
                "fine_spectral_charge_key": row["fine_spectral_charge_key"],
                "charge_frame_key": row["charge_frame_key"],
            }
        )
    ordered = sorted(rows, key=sort_key)
    return [
        {
            "frame_index": index,
            **row,
        }
        for index, row in enumerate(ordered)
    ]


def build_theorem() -> dict[str, Any]:
    factorization = load_json(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT)
    lift = load_json(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT)
    charge = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)

    gate_support, radicals, packets, affine_rows = build_affine_rows()
    charge_rows = {
        int(row["packet_id"]): row
        for row in charge.get("derived", {}).get("charge_frame_rows", [])
        if int(row["packet_id"]) in set(packets)
    }
    frame_rows = build_frame_rows(packets, radicals, gate_support, charge_rows)
    frame_key_rows = [row["canonical_frame_key"] for row in frame_rows]
    frame_key_hashes = [sha_json(row) for row in frame_key_rows]

    selected_rows = [row for row in frame_rows if packet239_selector(row)]
    selected_packet_ids = [int(row["packet_id"]) for row in selected_rows]
    selected_frame_indices = [int(row["frame_index"]) for row in selected_rows]
    selected_row = selected_rows[0] if len(selected_rows) == 1 else None

    breaker_summary = factorization.get("derived", {}).get("breaker_summary", {})
    minimal_axis_sets = breaker_summary.get("minimal_axis_identity_sets", [])
    minimal_atomic_sets = breaker_summary.get("minimal_atomic_identity_sets", [])
    lift_checks = lift.get("checks", {})

    canonical_frame_summary = {
        "packet_count": len(frame_rows),
        "canonical_affine_lift_count": len(affine_rows),
        "frame_field_count": len(CANONICAL_FRAME_FIELDS),
        "frame_key_count": len(set(frame_key_hashes)),
        "fine_spectral_key_count": len(
            {row["fine_spectral_charge_key"] for row in frame_rows}
        ),
        "charge_frame_key_count": len({row["charge_frame_key"] for row in frame_rows}),
        "sector26_sum_histogram": histogram(
            [row["sector26_clock_sum_mod26"] for row in frame_rows]
        ),
        "clock_frame_histogram": histogram([row["clock_frame"] for row in frame_rows]),
        "gamma_frame_histogram": histogram([row["gamma_frame"] for row in frame_rows]),
        "selected_packet_ids_by_zero_pair_fixed_rule": selected_packet_ids,
    }
    packet239_selection = {
        "selection_rule": "full_exposure_sector26_zero_pair_fixed_point",
        "selection_rule_fields": PACKET239_SELECTION_FIELDS,
        "uses_external_packet_id": False,
        "selected_packet_ids": selected_packet_ids,
        "selected_frame_indices": selected_frame_indices,
        "selected_signature": selected_row["selection_signature"] if selected_row else None,
        "selected_fine_spectral_charge_key": (
            selected_row["fine_spectral_charge_key"] if selected_row else None
        ),
        "selected_charge_frame_key": selected_row["charge_frame_key"] if selected_row else None,
    }

    checks = {
        "label_breaking_factorization_is_certified": factorization.get("status")
        == "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_CERTIFIED"
        and factorization.get("all_checks_pass") is True,
        "radical_gate_stabilizer_lift_is_certified": lift.get("status")
        == "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_CERTIFIED"
        and lift.get("all_checks_pass") is True,
        "charge_frame_classifier_is_certified": charge.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "full_exposure_frame_has_20_packets": len(frame_rows) == 20
        and sorted(row["packet_id"] for row in frame_rows) == packets
        and all(row["full_loop297_atom_exposure"] is True for row in frame_rows),
        "canonical_frame_key_is_injective": len(set(frame_key_hashes)) == 20,
        "fine_spectral_key_is_injective_on_full_exposure_frame": (
            canonical_frame_summary["fine_spectral_key_count"] == 20
        ),
        "minimal_breaker_frame_has_identity_stabilizer": (
            ["sector26"] in minimal_axis_sets
            and ["fine_spectral"] in minimal_atomic_sets
            and ["sector26_sum"] in minimal_atomic_sets
            and factorization.get("checks", {}).get(
                "atomic_counts_identify_true_single_label_breakers"
            )
            is True
        ),
        "lift_theorem_already_locates_zero_pair_touched_packet": lift_checks.get(
            "packet239_is_the_unique_zero_pair_touched_packet"
        )
        is True,
        "zero_pair_rule_selects_packet239_intrinsically": selected_packet_ids == [239],
        "selection_rule_is_id_free": "packet_id" not in PACKET239_SELECTION_FIELDS
        and packet239_selection["uses_external_packet_id"] is False,
        "selected_packet_has_expected_intrinsic_signature": selected_row is not None
        and selected_row["selection_signature"]
        == {
            "full_loop297_atom_exposure": True,
            "sector26_clock_pair": [0, 0],
            "sector26_clock_sum_mod26": 0,
            "sector26_clock_delta_mod26": 0,
            "sector26_clock_zero_pair": True,
            "sector26_clock_zero_touched": True,
        }
        and selected_row["fine_spectral_charge_key"] == "32|0|0|0|25"
        and selected_row["charge_frame_key"]
        == "high|zero_pair|full|gamma8_silent|hidden_cancelled|central_negative|AI|BDI",
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_canonical_labelled_frame",
        "status": status,
        "object": "d20",
        "claim": (
            "The 20 full-exposure packets admit a canonical labelled coordinate frame built from the "
            "minimal label breakers. The frame key is injective, the factorization theorem supplies "
            "identity rigidity through sector-26 sum and fine spectral labels, and packet 239 is recovered "
            "without using its external id as the unique full-exposure sector-26 zero-pair fixed point."
        ),
        "definition": {
            "canonical_labelled_frame": (
                "The 20 full-exposure packets sorted and keyed by intrinsic charge-frame fields: full "
                "Loop_297 exposure, mass, clock, gamma, sector-26 clock data, and fine spectral charge."
            ),
            "zero_pair_fixed_point": (
                "A full-exposure packet whose sector-26 clock pair is [0,0], hence sum 0, delta 0, "
                "zero-pair true, and zero-touched true."
            ),
            "id_free_selection": (
                "A selection predicate whose input fields exclude packet_id and frame_index."
            ),
        },
        "inputs": {
            "full_exposure_label_breaking_factorization_report": {
                "path": rel(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT),
            },
            "full_exposure_radical_gate_stabilizer_lift_report": {
                "path": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
            },
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
        },
        "derived": {
            "canonical_frame_summary": canonical_frame_summary,
            "canonical_frame_fields": CANONICAL_FRAME_FIELDS,
            "packet239_selection": packet239_selection,
            "minimal_identity_breakers": {
                "coarse_axis_sets": minimal_axis_sets,
                "atomic_label_sets": minimal_atomic_sets,
                "identity_rigid_atomic_singletons": [
                    ["sector26_sum"],
                    ["fine_spectral"],
                ],
            },
            "canonical_frame_rows": frame_rows,
            "canonical_frame_rows_sha256": sha_json(frame_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the labelled full-exposure packet frame is intrinsic and injective on the 20-packet stratum",
                "sector-26 sum and fine spectral labels each independently kill the nonidentity radical-gate lifts",
                "packet 239 is recoverable as the unique sector-26 zero-pair fixed point in that frame",
            ],
            "what_this_does_not_prove": (
                "This does not overturn the stabilizer theorem: packet 239 is not proven to be a unique "
                "symmetry-fixed vacuum. It is an intrinsic labelled-frame coordinate selected by the "
                "certified sector-26 clock condition."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Push the canonical labelled full-exposure frame through the two-step scattering table and "
            "express the transition operator in intrinsic label coordinates rather than packet ids."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_canonical_labelled_frame_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the label-breaking factorization, stabilizer-lift, and charge-frame inputs",
            "rebuild the 20 full-exposure packet list from the radical-gate support",
            "construct the intrinsic canonical labelled frame and verify its frame key is injective",
            "verify sector-26 sum and fine spectral labels are identity-rigid minimal breakers",
            "select packet 239 by an id-free sector-26 zero-pair fixed-point predicate",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
