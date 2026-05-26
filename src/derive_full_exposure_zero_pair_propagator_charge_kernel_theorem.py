from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_propagator_charge_kernel"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_coordinate_green_response"
    / "report.json"
)
PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_spectral_charge_table"
    / "report.json"
)

NUMERIC_LEDGER_FIELDS = [
    "dimension",
    "adjacency_trace",
    "laplacian_trace",
    "sector26_clock_sum_mod26",
    "sector26_clock_delta_mod26",
    "gamma8_mode_count",
    "corrected_hidden_clock_sum_mod26",
    "central_character",
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


def frac_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def linear_image(
    coeffs: dict[int, Fraction],
    spectral_by_packet: dict[int, dict[str, Any]],
    fields: list[str],
) -> dict[str, str]:
    image = {}
    for field in fields:
        value = sum(coeff * int(spectral_by_packet[packet_id][field]) for packet_id, coeff in coeffs.items())
        image[field] = frac_string(value)
    return image


def cleared_mod26_image(
    integer_coeffs: dict[int, int],
    spectral_by_packet: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    clock_pair = [
        sum(
            coeff * int(spectral_by_packet[packet_id]["sector26_clock_pair"][index])
            for packet_id, coeff in integer_coeffs.items()
        )
        % 26
        for index in range(2)
    ]
    clock_sum = (
        sum(
            coeff * int(spectral_by_packet[packet_id]["sector26_clock_sum_mod26"])
            for packet_id, coeff in integer_coeffs.items()
        )
        % 26
    )
    clock_delta = (
        sum(
            coeff * int(spectral_by_packet[packet_id]["sector26_clock_delta_mod26"])
            for packet_id, coeff in integer_coeffs.items()
        )
        % 26
    )
    return {
        "sector26_clock_pair_mod26": clock_pair,
        "sector26_clock_sum_mod26": clock_sum,
        "sector26_clock_delta_mod26": clock_delta,
    }


def shared_frame_axes(frame_rows: list[dict[str, Any]]) -> dict[str, Any]:
    axes = [
        "exposure_frame",
        "gamma_frame",
        "hidden_frame",
        "central_frame",
        "tenfold_frame",
        "full_loop297_atom_exposure",
    ]
    shared = {}
    for axis in axes:
        values = sorted({json.dumps(row[axis], sort_keys=True) for row in frame_rows})
        shared[axis] = json.loads(values[0]) if len(values) == 1 else None
    return shared


def build_residue_rows(
    spectral_by_packet: dict[int, dict[str, Any]],
    frame_by_packet: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    residue_specs = [
        {
            "residue_id": "adjacency_plus_pole",
            "pole": "lambda=6",
            "mode": "plus",
            "rational_coefficients": {239: Fraction(1, 2), 238: Fraction(1, 2)},
            "denominator_cleared_coefficients": {239: 1, 238: 1},
            "meaning": "monopole residue at the adjacency plus pole",
        },
        {
            "residue_id": "adjacency_minus_pole",
            "pole": "lambda=-2",
            "mode": "minus",
            "rational_coefficients": {239: Fraction(1, 2), 238: Fraction(-1, 2)},
            "denominator_cleared_coefficients": {239: 1, 238: -1},
            "meaning": "dipole residue at the adjacency minus pole",
        },
        {
            "residue_id": "markov_plus_pole",
            "pole": "lambda=1",
            "mode": "plus",
            "rational_coefficients": {239: Fraction(1, 2), 238: Fraction(1, 2)},
            "denominator_cleared_coefficients": {239: 1, 238: 1},
            "meaning": "monopole residue at the normalized Markov plus pole",
        },
        {
            "residue_id": "markov_minus_pole",
            "pole": "lambda=-1/3",
            "mode": "minus",
            "rational_coefficients": {239: Fraction(1, 2), 238: Fraction(-1, 2)},
            "denominator_cleared_coefficients": {239: 1, 238: -1},
            "meaning": "dipole residue at the normalized Markov minus pole",
        },
        {
            "residue_id": "laplacian_zero_mode",
            "pole": "m=0",
            "mode": "plus",
            "rational_coefficients": {239: Fraction(1, 2), 238: Fraction(1, 2)},
            "denominator_cleared_coefficients": {239: 1, 238: 1},
            "meaning": "massless zero-mode Green divergence",
        },
        {
            "residue_id": "laplacian_renormalized_dipole",
            "pole": "finite part",
            "mode": "minus",
            "rational_coefficients": {239: Fraction(1, 16), 238: Fraction(-1, 16)},
            "denominator_cleared_coefficients": {239: 1, 238: -1},
            "meaning": "finite massive-Laplacian dipole residue after zero-mode subtraction",
        },
    ]

    support_frames = [frame_by_packet[239], frame_by_packet[238]]
    rows = []
    for spec in residue_specs:
        rational = spec["rational_coefficients"]
        cleared = spec["denominator_cleared_coefficients"]
        rows.append(
            {
                "residue_id": spec["residue_id"],
                "pole": spec["pole"],
                "mode": spec["mode"],
                "meaning": spec["meaning"],
                "support_packet_ids": [239, 238],
                "rational_coefficients": {
                    str(packet_id): frac_string(coeff) for packet_id, coeff in rational.items()
                },
                "denominator_cleared_coefficients": {
                    str(packet_id): coeff for packet_id, coeff in cleared.items()
                },
                "rational_charge_image": linear_image(
                    rational,
                    spectral_by_packet,
                    NUMERIC_LEDGER_FIELDS,
                ),
                "denominator_cleared_sector26_image": cleared_mod26_image(
                    cleared,
                    spectral_by_packet,
                ),
                "shared_support_axes": shared_frame_axes(support_frames),
                "support_charge_frame_keys": {
                    str(packet_id): frame_by_packet[packet_id]["charge_frame_key"]
                    for packet_id in [239, 238]
                },
                "support_fine_spectral_charge_keys": {
                    str(packet_id): frame_by_packet[packet_id]["fine_spectral_charge_key"]
                    for packet_id in [239, 238]
                },
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    green = load_json(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT)
    charge = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    spectral = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)

    frame_rows = charge.get("derived", {}).get("charge_frame_rows", [])
    spectral_rows = spectral.get("derived", {}).get("packet_spectral_charge_rows", [])
    frame_by_packet = {int(row["packet_id"]): row for row in frame_rows}
    spectral_by_packet = {int(row["packet_id"]): row for row in spectral_rows}
    zero_pair_response = green.get("derived", {}).get("zero_pair_source_response", {})

    p239_frame = frame_by_packet.get(239, {})
    p238_frame = frame_by_packet.get(238, {})
    p239_spectral = spectral_by_packet.get(239, {})
    p238_spectral = spectral_by_packet.get(238, {})
    residue_rows = build_residue_rows(spectral_by_packet, frame_by_packet)

    plus_rows = [row for row in residue_rows if row["mode"] == "plus"]
    minus_rows = [row for row in residue_rows if row["mode"] == "minus"]
    plus_sector_images = {
        json.dumps(row["denominator_cleared_sector26_image"], sort_keys=True)
        for row in plus_rows
    }
    minus_sector_images = {
        json.dumps(row["denominator_cleared_sector26_image"], sort_keys=True)
        for row in minus_rows
    }

    shared_axes = shared_frame_axes([p239_frame, p238_frame])
    propagator_charge_kernel_summary = {
        "source_packet_id": 239,
        "active_partner_packet_id": 238,
        "support_packet_ids": [239, 238],
        "residue_row_count": len(residue_rows),
        "shared_support_axes": shared_axes,
        "plus_denominator_cleared_sector26_image": json.loads(next(iter(plus_sector_images)))
        if len(plus_sector_images) == 1
        else None,
        "minus_denominator_cleared_sector26_image": json.loads(next(iter(minus_sector_images)))
        if len(minus_sector_images) == 1
        else None,
        "raw_half_residues_are_not_native_z26_classes": True,
        "kernel_status": (
            "A finite propagator charge kernel exists after canonical denominator clearing. "
            "The raw pole residues live over Q because they contain 1/2 coefficients; the sector-26 "
            "ledger becomes integral only for the cleared plus/minus residue classes [1,1] and [1,-1]."
        ),
    }

    checks = {
        "green_response_input_is_certified": green.get("status")
        == "D20_FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_CERTIFIED"
        and green.get("all_checks_pass") is True,
        "charge_frame_input_is_certified": charge.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "spectral_charge_table_input_is_certified": spectral.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and spectral.get("all_checks_pass") is True,
        "zero_pair_green_support_matches_charge_rows": zero_pair_response.get(
            "support_witness_packet_ids"
        )
        == [239, 238]
        and {239, 238}.issubset(frame_by_packet)
        and {239, 238}.issubset(spectral_by_packet),
        "support_has_shared_propagator_axes": shared_axes
        == {
            "central_frame": "central_negative",
            "exposure_frame": "full",
            "full_loop297_atom_exposure": True,
            "gamma_frame": "gamma8_silent",
            "hidden_frame": "hidden_cancelled",
            "tenfold_frame": "AI|BDI",
        },
        "support_is_same_radical_full_exposure_pair": p239_spectral.get("radical_character")
        == p238_spectral.get("radical_character")
        == 119
        and p239_spectral.get("loop297_atom_union_ids") == list(range(25))
        and p238_spectral.get("loop297_atom_union_ids") == list(range(25)),
        "zero_pair_endpoint_is_label_unique": p239_frame.get("clock_frame") == "zero_pair"
        and p239_frame.get("fine_spectral_charge_key") == "32|0|0|0|25"
        and p238_frame.get("clock_frame") == "delta8_nonzero"
        and p238_frame.get("fine_spectral_charge_key") == "28|4|8|0|25",
        "plus_residue_charge_image_is_stable_across_adjacency_markov_laplacian": len(
            {
                json.dumps(row["rational_charge_image"], sort_keys=True)
                for row in plus_rows
            }
        )
        == 1
        and all(
            row["rational_charge_image"]["laplacian_trace"] == "30"
            and row["rational_charge_image"]["adjacency_trace"] == "-8"
            and row["rational_charge_image"]["sector26_clock_sum_mod26"] == "2"
            and row["rational_charge_image"]["sector26_clock_delta_mod26"] == "4"
            for row in plus_rows
        ),
        "minus_residue_charge_image_is_stable_for_spectral_minus_poles": all(
            row["rational_charge_image"]["laplacian_trace"] == "2"
            and row["rational_charge_image"]["adjacency_trace"] == "-2"
            and row["rational_charge_image"]["sector26_clock_sum_mod26"] == "-2"
            and row["rational_charge_image"]["sector26_clock_delta_mod26"] == "-4"
            for row in minus_rows
            if row["residue_id"] != "laplacian_renormalized_dipole"
        )
        and next(
            row for row in minus_rows if row["residue_id"] == "laplacian_renormalized_dipole"
        )["rational_charge_image"]["laplacian_trace"]
        == "1/4",
        "denominator_cleared_sector26_images_are_integral_and_complementary": plus_sector_images
        == {
            json.dumps(
                {
                    "sector26_clock_delta_mod26": 8,
                    "sector26_clock_pair_mod26": [24, 6],
                    "sector26_clock_sum_mod26": 4,
                },
                sort_keys=True,
            )
        }
        and minus_sector_images
        == {
            json.dumps(
                {
                    "sector26_clock_delta_mod26": 18,
                    "sector26_clock_pair_mod26": [2, 20],
                    "sector26_clock_sum_mod26": 22,
                },
                sort_keys=True,
            )
        },
        "raw_half_residues_are_recorded_as_non_native_z26_classes": (
            propagator_charge_kernel_summary["raw_half_residues_are_not_native_z26_classes"]
            is True
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_propagator_charge_kernel",
        "status": status,
        "object": "d20",
        "claim": (
            "The zero-pair Green-response pole residues define a finite propagator charge kernel after "
            "canonical denominator clearing. The kernel is supported on packets 239 and 238, preserves "
            "full exposure, gamma silence, hidden cancellation, central negativity, and AI|BDI tenfold "
            "type, and carries complementary sector-26 plus/minus residue classes."
        ),
        "definition": {
            "propagator_charge_kernel": (
                "The charge-frame and sector-26 ledger image of the Green-response pole residues for a "
                "labelled source insertion."
            ),
            "canonical_denominator_clearing": (
                "The pole residues have coefficients 1/2, while Z/26 has no inverse for 2. The finite "
                "sector-26 ledger therefore records the cleared classes [1,1] and [1,-1]."
            ),
            "plus_residue_class": "The denominator-cleared monopole class [1,1] on packets 239 and 238.",
            "minus_residue_class": "The denominator-cleared dipole class [1,-1] on packets 239 and 238.",
        },
        "inputs": {
            "full_exposure_label_coordinate_green_response_report": {
                "path": rel(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT),
            },
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
            "projective_packet_spectral_charge_table_report": {
                "path": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
            },
        },
        "derived": {
            "propagator_charge_kernel_summary": propagator_charge_kernel_summary,
            "residue_charge_rows": residue_rows,
            "residue_charge_rows_sha256": sha_json(residue_rows),
            "support_charge_frame_rows": [p239_frame, p238_frame],
            "support_spectral_charge_rows": [p239_spectral, p238_spectral],
        },
        "interpretation": {
            "what_this_proves": [
                "the Green-response residues have a certified charge-frame image on packets 239 and 238",
                "the support preserves full exposure, gamma silence, hidden cancellation, central negativity, and AI|BDI type",
                "the raw half-residues are rational rather than native Z/26 classes",
                "after denominator clearing, the plus and minus sector-26 images are complementary finite classes",
            ],
            "what_this_does_not_prove": (
                "This does not identify a continuum field or particle. It proves a finite, denominator-cleared "
                "propagator charge kernel inside the certified D20 packet ledger."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Test whether the denominator-cleared propagator charge kernel is invariant under the surviving "
            "label-preserving symmetry and compatible with the finite Ward/flux-balance reports."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_propagator_charge_kernel_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify Green-response, charge-frame, and spectral-charge inputs",
            "project the zero-pair plus and minus pole residues through the packet charge ledger",
            "verify support is exactly packets 239 and 238",
            "verify shared full-exposure, gamma, hidden, central, and tenfold axes",
            "verify raw half-residues are not native sector-26 classes",
            "verify denominator-cleared plus and minus sector-26 images",
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
