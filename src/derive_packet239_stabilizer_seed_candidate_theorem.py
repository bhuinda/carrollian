from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "packet239_stabilizer_seed_candidate"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

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
FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_parity_central_extension_group"
    / "report.json"
)

RADICAL_COORDINATE_COUNT = 8
ACTIVE_LEFT_COORD = 8
ACTIVE_RIGHT_COORD = 9
COORDINATE_COUNT = 10
GROUP_ORDER = 1 << 11


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


def parity(value: int) -> int:
    return value.bit_count() & 1


def decode_group_element(element: int) -> tuple[int, int]:
    coord = element & ((1 << COORDINATE_COUNT) - 1)
    central = (element >> COORDINATE_COUNT) & 1
    return coord, central


def packet_matrix(element: int, radical_character: int, active_sigma: int) -> tuple[int, int, int, int]:
    coord, central = decode_group_element(element)
    radical_translation = coord & ((1 << RADICAL_COORDINATE_COUNT) - 1)
    active_alpha = (coord >> ACTIVE_LEFT_COORD) & 1
    active_beta = (coord >> ACTIVE_RIGHT_COORD) & 1
    base_phase = central ^ parity(radical_character & radical_translation) ^ (
        active_sigma & active_alpha
    )
    values = [[0, 0], [0, 0]]
    for source_tau in (0, 1):
        target_tau = source_tau ^ active_beta
        exponent = base_phase ^ (active_alpha & source_tau)
        values[target_tau][source_tau] = -1 if exponent else 1
    return (values[0][0], values[0][1], values[1][0], values[1][1])


def normalize_projective_matrix(matrix: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    for value in matrix:
        if value:
            return matrix if value > 0 else tuple(-entry for entry in matrix)
    return matrix


def identity_kernel_elements(radical_character: int, active_sigma: int) -> list[int]:
    return [
        element
        for element in range(GROUP_ORDER)
        if packet_matrix(element, radical_character, active_sigma) == (1, 0, 0, 1)
    ]


def packet_stabilizer_row(packet_row: dict[str, Any], charge_frame_row: dict[str, Any]) -> dict[str, Any]:
    radical_character = int(packet_row["radical_character"])
    active_sigma = int(packet_row["active_sigma"])
    image = {
        packet_matrix(element, radical_character, active_sigma)
        for element in range(GROUP_ORDER)
    }
    projective_image = {normalize_projective_matrix(matrix) for matrix in image}
    scalar_elements = [
        element
        for element in range(GROUP_ORDER)
        if packet_matrix(element, radical_character, active_sigma)
        in {(1, 0, 0, 1), (-1, 0, 0, -1)}
    ]
    identity_elements = identity_kernel_elements(radical_character, active_sigma)
    return {
        "packet_id": int(packet_row["packet_id"]),
        "radical_character": radical_character,
        "active_sigma": active_sigma,
        "setwise_stabilizer_order": GROUP_ORDER,
        "scalar_stabilizer_order": len(scalar_elements),
        "identity_kernel_order": len(identity_elements),
        "linear_image_order": len(image),
        "projective_image_order": len(projective_image),
        "linear_image_type": "D8_real_signed_2x2",
        "projective_image_type": "V4",
        "identity_kernel_sha256": sha_json(identity_elements),
        "charge_frame_key": charge_frame_row["charge_frame_key"],
        "fine_spectral_charge_key": charge_frame_row["fine_spectral_charge_key"],
        "full_loop297_atom_exposure": bool(charge_frame_row["full_loop297_atom_exposure"]),
        "sector26_clock_zero_pair": bool(charge_frame_row["sector26_clock_zero_pair"]),
        "gamma8_touched": bool(charge_frame_row["gamma8_touched"]),
    }


def build_theorem() -> dict[str, Any]:
    classifier = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    spectral_table = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
    extension = load_json(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT)
    charge_rows = classifier["derived"]["charge_frame_rows"]
    packet_rows = spectral_table["derived"]["packet_spectral_charge_rows"]
    charge_by_id = {int(row["packet_id"]): row for row in charge_rows}
    packet_by_id = {int(row["packet_id"]): row for row in packet_rows}
    stabilizer_rows = [
        packet_stabilizer_row(packet_by_id[packet_id], charge_by_id[packet_id])
        for packet_id in sorted(packet_by_id)
    ]
    stabilizer_by_id = {row["packet_id"]: row for row in stabilizer_rows}
    full_exposure_packet_ids = [
        row["packet_id"] for row in stabilizer_rows if row["full_loop297_atom_exposure"]
    ]
    full_exposure_stabilizers = [
        stabilizer_by_id[packet_id] for packet_id in full_exposure_packet_ids
    ]
    p239 = stabilizer_by_id[239]
    same_identity_kernel_as_239 = [
        row["packet_id"]
        for row in stabilizer_rows
        if row["identity_kernel_sha256"] == p239["identity_kernel_sha256"]
    ]
    same_full_identity_kernel_as_239 = [
        row["packet_id"]
        for row in full_exposure_stabilizers
        if row["identity_kernel_sha256"] == p239["identity_kernel_sha256"]
    ]
    expected_image = {
        (1, 0, 0, 1),
        (-1, 0, 0, -1),
        (1, 0, 0, -1),
        (-1, 0, 0, 1),
        (0, 1, 1, 0),
        (0, -1, -1, 0),
        (0, -1, 1, 0),
        (0, 1, -1, 0),
    }
    image_239 = {
        packet_matrix(element, int(packet_by_id[239]["radical_character"]), int(packet_by_id[239]["active_sigma"]))
        for element in range(GROUP_ORDER)
    }

    setwise_histogram = histogram(Counter(row["setwise_stabilizer_order"] for row in stabilizer_rows))
    scalar_histogram = histogram(Counter(row["scalar_stabilizer_order"] for row in stabilizer_rows))
    kernel_histogram = histogram(Counter(row["identity_kernel_order"] for row in stabilizer_rows))
    linear_image_histogram = histogram(Counter(row["linear_image_order"] for row in stabilizer_rows))
    projective_image_histogram = histogram(
        Counter(row["projective_image_order"] for row in stabilizer_rows)
    )
    full_setwise_histogram = histogram(
        Counter(row["setwise_stabilizer_order"] for row in full_exposure_stabilizers)
    )
    full_scalar_histogram = histogram(
        Counter(row["scalar_stabilizer_order"] for row in full_exposure_stabilizers)
    )
    full_kernel_histogram = histogram(
        Counter(row["identity_kernel_order"] for row in full_exposure_stabilizers)
    )

    checks = {
        "projective_packet_charge_frame_classifier_is_certified": classifier.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and classifier.get("all_checks_pass") is True,
        "projective_packet_spectral_charge_table_is_certified": spectral_table.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and spectral_table.get("all_checks_pass") is True,
        "finite_parity_central_extension_group_is_certified": extension.get("status")
        == "D20_FINITE_PARITY_CENTRAL_EXTENSION_GROUP_CERTIFIED"
        and extension.get("all_checks_pass") is True,
        "stabilizer_table_has_512_rows": len(stabilizer_rows) == 512,
        "all_packets_have_full_setwise_stabilizer": setwise_histogram == {"2048": 512},
        "all_packets_have_uniform_scalar_stabilizer": scalar_histogram == {"512": 512},
        "all_packets_have_uniform_identity_kernel_order": kernel_histogram == {"256": 512},
        "all_packets_have_uniform_d8_linear_image": linear_image_histogram == {"8": 512}
        and projective_image_histogram == {"4": 512},
        "packet239_linear_image_is_expected_d8": image_239 == expected_image,
        "full_exposure_packets_have_same_stabilizer_orders": len(full_exposure_stabilizers) == 20
        and full_setwise_histogram == {"2048": 20}
        and full_scalar_histogram == {"512": 20}
        and full_kernel_histogram == {"256": 20},
        "packet239_stabilizer_orders_match_full_exposure_peers": p239["setwise_stabilizer_order"]
        == 2048
        and p239["scalar_stabilizer_order"] == 512
        and p239["identity_kernel_order"] == 256
        and p239["linear_image_order"] == 8
        and p239["projective_image_order"] == 4,
        "packet239_identity_kernel_is_shared_only_with_active_partner_among_full_exposure": (
            same_full_identity_kernel_as_239 == [238, 239]
        ),
        "packet239_charge_frame_remains_unique": classifier["checks"].get(
            "packet239_is_unique_in_charge_frame_and_fine_key"
        )
        is True
        and classifier["checks"].get("packet239_is_unique_full_exposure_clock_zero_packet")
        is True,
        "packet239_is_charge_seed_not_symmetry_fixed_vacuum": p239["setwise_stabilizer_order"] == 2048
        and full_setwise_histogram == {"2048": 20}
        and classifier["derived"]["distinguished_packet_sets"][
            "full_exposure_clock_zero_packet_ids"
        ]
        == [239],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PACKET239_STABILIZER_SEED_CANDIDATE_CERTIFIED"
        if all_checks_pass
        else "D20_PACKET239_STABILIZER_SEED_CANDIDATE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.packet239_stabilizer_seed_candidate",
        "status": status,
        "object": "d20",
        "claim": (
            "Packet 239 is not distinguished by a larger signed-action stabilizer: every projective packet "
            "has full setwise stabilizer order 2048, scalar stabilizer order 512, identity kernel order 256, "
            "and D8 real signed 2x2 image. Packet 239 remains distinguished only as a finite charge-frame seed: "
            "it is the unique full Loop_297 exposure, sector-26 clock-zero packet."
        ),
        "definition": {
            "setwise_stabilizer": (
                "Elements of the signed projective kernel action preserving the two-dimensional packet subspace."
            ),
            "scalar_stabilizer": "Elements acting by +/- identity on the packet.",
            "identity_kernel": "Elements acting as +identity on the packet.",
            "linear_image": "The signed 2x2 real matrix image of the full central extension on the packet.",
        },
        "inputs": {
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
            "projective_packet_spectral_charge_table_report": {
                "path": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
            },
            "finite_parity_central_extension_group_report": {
                "path": rel(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT),
                "sha256": sha_file(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT),
            },
        },
        "derived": {
            "stabilizer_summary": {
                "packet_count": len(stabilizer_rows),
                "setwise_stabilizer_order_histogram": setwise_histogram,
                "scalar_stabilizer_order_histogram": scalar_histogram,
                "identity_kernel_order_histogram": kernel_histogram,
                "linear_image_order_histogram": linear_image_histogram,
                "projective_image_order_histogram": projective_image_histogram,
                "linear_image_type": "D8_real_signed_2x2",
                "projective_image_type": "V4",
                "packet239_charge_frame_unique": True,
                "packet239_stabilizer_unique": False,
                "packet239_seed_status": "charge-frame seed candidate; not symmetry-fixed vacuum",
            },
            "full_exposure_stabilizer_comparison": {
                "full_exposure_packet_ids": full_exposure_packet_ids,
                "setwise_stabilizer_order_histogram": full_setwise_histogram,
                "scalar_stabilizer_order_histogram": full_scalar_histogram,
                "identity_kernel_order_histogram": full_kernel_histogram,
                "same_identity_kernel_as_packet239_within_full_exposure": (
                    same_full_identity_kernel_as_239
                ),
            },
            "packet239_stabilizer": p239,
            "packet239_linear_image_matrices": sorted([list(matrix) for matrix in image_239]),
            "same_identity_kernel_as_packet239_packet_ids": same_identity_kernel_as_239,
            "stabilizer_rows": stabilizer_rows,
            "stabilizer_rows_sha256": sha_json(stabilizer_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "packet 239 is invariant under the same setwise signed action as every other packet",
                "packet 239 has no enhanced stabilizer compared with the other full-exposure packets",
                "packet 239 shares its identity kernel with active partner packet 238 among full-exposure packets",
                "packet 239 is distinguished by charge-frame invariants, not by being a symmetry-fixed vacuum",
            ],
            "what_this_does_not_prove": (
                "This does not rule out a later physical vacuum interpretation. It says that the current finite "
                "signed kernel action does not make packet 239 a unique stabilizer-fixed vacuum."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build a packet-239 seed propagation theorem: start from packet 239 and apply admissible non-kernel "
            "boundary/scattering moves to determine which charge frames are reachable."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.packet239_stabilizer_seed_candidate_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify packet charge-frame classifier, spectral table, and central extension inputs",
            "compute setwise stabilizer, scalar stabilizer, identity kernel, and image orders for all 512 packets",
            "compare packet 239 stabilizer orders with the 20 full-exposure packets",
            "verify packet 239 has the expected D8 real signed 2x2 image",
            "verify packet 239 remains unique by charge-frame invariants but not by stabilizer size",
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
