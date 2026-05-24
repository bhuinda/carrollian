from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "hidden_packet_charge_frame_classifier"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_bms_carrollian_flux_balance" / "report.json"
)
CANONICAL_FLUX_BALANCE_GAUGE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_flux_balance_gauge" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
RESIDUE_SPECTRUM_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")
RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
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


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def active_edge_ids(incidence_vector_mod2: str) -> list[int]:
    return [idx for idx, bit in enumerate(incidence_vector_mod2) if bit == "1"]


def charge_tuple(charges: dict[int, dict[str, int]], vertex: int) -> tuple[int, ...]:
    return tuple(charges[vertex][component] for component in PUBLIC_COMPONENTS)


def load_residue_rows() -> dict[int, dict[str, Any]]:
    rows = {}
    with RESIDUE_SPECTRUM_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mask = int(row["mask"])
            rows[mask] = {
                "mask": mask,
                "basis_cycle_ids": [
                    int(value) for value in row["basis_cycle_ids"].split() if value
                ],
                "residue_edge_weight": int(row["residue_edge_weight"]),
                "total_basis_length": int(row["total_basis_length"]),
                "total_optical_action": int(row["total_optical_action"]),
                "incidence_vector_mod2": row["incidence_vector_mod2"],
            }
    return rows


def load_edge_rows(charges: dict[int, dict[str, int]]) -> list[dict[str, Any]]:
    rows = []
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            edge = {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "interface_weight": int(row["interface_weight"]),
            }
            u = edge["u"]
            v = edge["v"]
            sign = 1 if charge_tuple(charges, u) < charge_tuple(charges, v) else -1
            diff = {
                component: charges[v][component] - charges[u][component]
                for component in PUBLIC_COMPONENTS
            }
            edge["canonical_sign_uv"] = sign
            edge["root_incident"] = 1 if 0 in {u, v} else 0
            edge["root_edge"] = 1 if edge["edge_id"] == 2 else 0
            edge["flux_l1"] = sum(abs(value) for value in diff.values())
            edge["flux_abs"] = {
                component: abs(diff[component]) for component in PUBLIC_COMPONENTS
            }
            edge["flux_signed"] = {
                component: sign * diff[component] for component in PUBLIC_COMPONENTS
            }
            rows.append(edge)
    return sorted(rows, key=lambda row: row["edge_id"])


def class_summary(
    rows: list[dict[str, Any]],
    signature_name: str,
    signature_fields: list[str],
) -> dict[str, Any]:
    classes: dict[str, list[int]] = defaultdict(list)
    by_packet = Counter()
    for row in rows:
        signature = {field: row[field] for field in signature_fields}
        key = sha_json(signature)
        classes[key].append(row["mask"])
    for key, masks in classes.items():
        packet = next(row["hidden_packet"] for row in rows if row["mask"] == masks[0])
        by_packet[packet] += 1
    size_histogram = Counter(len(masks) for masks in classes.values())
    non_singletons = [
        {
            "class_sha256": key,
            "size": len(masks),
            "sample_masks": masks[:12],
        }
        for key, masks in classes.items()
        if len(masks) > 1
    ]
    non_singletons = sorted(
        non_singletons,
        key=lambda item: (-item["size"], item["class_sha256"]),
    )
    return {
        "signature": signature_name,
        "signature_fields": signature_fields,
        "class_count": len(classes),
        "classes_by_hidden_packet": dict(sorted(by_packet.items())),
        "class_size_histogram": {
            str(size): int(count) for size, count in sorted(size_histogram.items())
        },
        "max_class_size": max(size_histogram),
        "non_singleton_class_count": sum(1 for masks in classes.values() if len(masks) > 1),
        "sample_non_singletons": non_singletons[:24],
        "class_map_sha256": sha_json({key: sorted(masks) for key, masks in sorted(classes.items())}),
    }


def histogram_by_packet(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for packet in ("kernel", "odd"):
        histogram = Counter(row[field] for row in rows if row["hidden_packet"] == packet)
        output[packet] = {str(key): int(histogram[key]) for key in sorted(histogram)}
    return output


def build_packet_rows(
    balance_rows: list[dict[str, Any]],
    residue_rows: dict[int, dict[str, Any]],
    transport_rows: dict[int, dict[str, Any]],
    edge_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for balance in sorted(balance_rows, key=lambda row: int(row["mask"])):
        mask = int(balance["mask"])
        residue = residue_rows[mask]
        transport = transport_rows[mask]
        active_edges = active_edge_ids(residue["incidence_vector_mod2"])
        edges = [edge_rows[edge_id] for edge_id in active_edges]
        public_flux_abs_sums = {
            component: sum(edge["flux_abs"][component] for edge in edges)
            for component in PUBLIC_COMPONENTS
        }
        public_flux_signed_sums = {
            component: sum(edge["flux_signed"][component] for edge in edges)
            for component in PUBLIC_COMPONENTS
        }
        row = {
            "mask": mask,
            "hidden_packet": balance["hidden_packet"],
            "corrected_R33_mod26": int(balance["corrected_R33_mod26"]),
            "basis_cycle_indices": balance["basis_cycle_indices"],
            "basis_cycle_count": len(balance["basis_cycle_indices"]),
            "edge_support_count": len(active_edges),
            "active_edge_ids": active_edges,
            "root_edge_active": sum(edge["root_edge"] for edge in edges),
            "root_incident_edge_count": sum(edge["root_incident"] for edge in edges),
            "canonical_forward_edge_count": sum(
                1 for edge in edges if edge["canonical_sign_uv"] == 1
            ),
            "canonical_backward_edge_count": sum(
                1 for edge in edges if edge["canonical_sign_uv"] == -1
            ),
            "canonical_orientation_signed_sum": sum(edge["canonical_sign_uv"] for edge in edges),
            "public_flux_l1_support": sum(edge["flux_l1"] for edge in edges),
            "public_flux_abs_sums": public_flux_abs_sums,
            "public_flux_signed_sums": public_flux_signed_sums,
            "edge_mod2_height_action": int(transport["edge_mod2_height_action"]),
            "height_action": int(balance["finite_height_flux"]),
            "height_gap_from_mod2_support": int(transport["edge_mod2_height_gap"]),
            "total_basis_length": int(residue["total_basis_length"]),
            "incidence_vector_mod2": residue["incidence_vector_mod2"],
        }
        row["coarse_signature"] = {
            key: row[key]
            for key in (
                "hidden_packet",
                "basis_cycle_count",
                "edge_support_count",
                "root_edge_active",
                "root_incident_edge_count",
                "canonical_forward_edge_count",
                "canonical_backward_edge_count",
            )
        }
        row["refined_charge_frame_signature"] = {
            **row["coarse_signature"],
            "public_flux_abs_sums": public_flux_abs_sums,
            "public_flux_signed_sums": public_flux_signed_sums,
        }
        row["complete_charge_action_signature"] = {
            **row["refined_charge_frame_signature"],
            "height_action": row["height_action"],
            "edge_mod2_height_action": row["edge_mod2_height_action"],
        }
        rows.append(row)
    return rows


def build_theorem() -> dict[str, Any]:
    finite_bms = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)
    canonical_gauge = load_json(CANONICAL_FLUX_BALANCE_GAUGE_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)

    charges = {
        int(vertex): {component: int(values[component]) for component in PUBLIC_COMPONENTS}
        for vertex, values in canonical_gauge["derived"]["exact_flux_gauge"][
            "root_zero_potential"
        ].items()
    }
    residue_rows = load_residue_rows()
    edge_rows = load_edge_rows(charges)
    transport_rows = {
        int(row["mask"]): row for row in all_residue["derived"]["transport_rows"]
    }
    balance_rows = finite_bms["derived"]["balance_rows"]
    packet_rows = build_packet_rows(balance_rows, residue_rows, transport_rows, edge_rows)

    coarse_fields = [
        "hidden_packet",
        "basis_cycle_count",
        "edge_support_count",
        "root_edge_active",
        "root_incident_edge_count",
        "canonical_forward_edge_count",
        "canonical_backward_edge_count",
    ]
    refined_fields = coarse_fields + ["public_flux_abs_sums", "public_flux_signed_sums"]
    complete_fields = refined_fields + ["height_action", "edge_mod2_height_action"]

    hidden_packet_histogram = Counter(row["hidden_packet"] for row in packet_rows)
    root_edge_by_packet = histogram_by_packet(packet_rows, "root_edge_active")
    root_incident_by_packet = histogram_by_packet(packet_rows, "root_incident_edge_count")
    basis_count_by_packet = histogram_by_packet(packet_rows, "basis_cycle_count")
    edge_count_by_packet = histogram_by_packet(packet_rows, "edge_support_count")
    orientation_sum_by_packet = histogram_by_packet(packet_rows, "canonical_orientation_signed_sum")
    coarse_summary = class_summary(packet_rows, "coarse_charge_frame", coarse_fields)
    refined_summary = class_summary(packet_rows, "refined_charge_frame", refined_fields)
    complete_summary = class_summary(packet_rows, "complete_charge_action", complete_fields)
    gamma8_row = packet_rows[GAMMA8_MASK]

    checks = {
        "finite_bms_carrollian_flux_balance_is_certified": finite_bms.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and finite_bms.get("all_checks_pass") is True,
        "canonical_flux_balance_gauge_is_certified": canonical_gauge.get("status")
        == "D20_CANONICAL_FLUX_BALANCE_GAUGE_CERTIFIED"
        and canonical_gauge.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "all_2048_packet_rows_are_present": len(packet_rows) == MASK_COUNT
        and [row["mask"] for row in packet_rows] == list(range(MASK_COUNT)),
        "residue_spectrum_matches_packet_rows": sorted(residue_rows) == list(range(MASK_COUNT))
        and all(len(row["incidence_vector_mod2"]) == 30 for row in residue_rows.values()),
        "active_edge_counts_match_residue_and_transport": all(
            row["edge_support_count"] == residue_rows[row["mask"]]["residue_edge_weight"]
            and row["edge_support_count"] == int(transport_rows[row["mask"]]["active_edge_count"])
            for row in packet_rows
        ),
        "height_actions_match_residue_transport_and_balance": all(
            row["height_action"] == residue_rows[row["mask"]]["total_optical_action"]
            and row["height_action"] == int(transport_rows[row["mask"]]["height_action"])
            for row in packet_rows
        ),
        "hidden_packets_split_evenly": dict(hidden_packet_histogram)
        == {"kernel": 1024, "odd": 1024},
        "root_edge_activity_is_balanced_inside_each_packet": root_edge_by_packet
        == {"kernel": {"0": 512, "1": 512}, "odd": {"0": 512, "1": 512}},
        "root_incidence_profile_is_identical_inside_each_packet": root_incident_by_packet
        == {"kernel": {"0": 256, "2": 768}, "odd": {"0": 256, "2": 768}},
        "coarse_charge_frame_classifier_has_942_classes": coarse_summary["class_count"] == 942
        and coarse_summary["classes_by_hidden_packet"] == {"kernel": 472, "odd": 470},
        "refined_charge_frame_classifier_has_2032_classes": refined_summary["class_count"]
        == 2032
        and refined_summary["class_size_histogram"] == {"1": 2016, "2": 16},
        "complete_charge_action_classifier_separates_all_masks": complete_summary["class_count"]
        == MASK_COUNT
        and complete_summary["class_size_histogram"] == {"1": MASK_COUNT},
        "gamma8_packet_invariants_match_balance_witness": gamma8_row["mask"] == GAMMA8_MASK
        and gamma8_row["hidden_packet"] == "odd"
        and gamma8_row["basis_cycle_indices"] == [8]
        and gamma8_row["edge_support_count"] == 5
        and gamma8_row["root_edge_active"] == 1
        and gamma8_row["root_incident_edge_count"] == 2
        and gamma8_row["canonical_forward_edge_count"] == 4
        and gamma8_row["canonical_backward_edge_count"] == 1
        and gamma8_row["height_action"] == 374784,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        if all_checks_pass
        else "D20_HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.hidden_packet_charge_frame_classifier",
        "status": status,
        "object": "d20",
        "claim": (
            "The finite BMS/Carrollian hidden packets admit a canonical charge-frame classifier. The "
            "1024 kernel and 1024 odd masks have identical root-edge and root-incidence balances, but "
            "their active edge supports split into 942 coarse charge-frame classes. Adding public "
            "charge-flux moments refines this to 2032 classes with only 16 doubletons; adding the finite "
            "height/action pair separates all 2048 masks."
        ),
        "definition": {
            "hidden_packet": "kernel when corrected_R33_mod26=0, odd when corrected_R33_mod26=13.",
            "coarse_charge_frame_signature": (
                "hidden packet, basis-cycle count, active edge count, canonical root-edge activity, "
                "root incidence, and canonical forward/backward edge counts."
            ),
            "refined_charge_frame_signature": (
                "the coarse signature plus absolute and canonical-signed public flux moment sums in the "
                "root-fixed (M,J,P,Phi) frame."
            ),
            "complete_charge_action_signature": (
                "the refined charge-frame signature plus height_action and edge_mod2_height_action."
            ),
        },
        "inputs": {
            "finite_bms_carrollian_flux_balance_report": {
                "path": rel(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
            },
            "canonical_flux_balance_gauge_report": {
                "path": rel(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
                "sha256": sha_file(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "residue_spectrum": {
                "path": rel(RESIDUE_SPECTRUM_CSV),
                "sha256": sha_file(RESIDUE_SPECTRUM_CSV),
            },
            "d20_edge_table": {"path": rel(D20_EDGES_CSV), "sha256": sha_file(D20_EDGES_CSV)},
        },
        "derived": {
            "public_charge_frame": {
                "components": list(PUBLIC_COMPONENTS),
                "canonical_root_vertex": canonical_gauge["derived"]["canonical_marking"][
                    "canonical_root_vertex"
                ],
                "canonical_root_edge": canonical_gauge["derived"]["canonical_marking"][
                    "canonical_root_edge"
                ],
            },
            "packet_histograms": {
                "hidden_packet": dict(hidden_packet_histogram),
                "basis_cycle_count_by_packet": basis_count_by_packet,
                "edge_support_count_by_packet": edge_count_by_packet,
                "root_edge_active_by_packet": root_edge_by_packet,
                "root_incident_edge_count_by_packet": root_incident_by_packet,
                "canonical_orientation_signed_sum_by_packet": orientation_sum_by_packet,
            },
            "classifiers": {
                "coarse_charge_frame": coarse_summary,
                "refined_charge_frame": refined_summary,
                "complete_charge_action": complete_summary,
            },
            "gamma8_row": gamma8_row,
            "packet_rows": packet_rows,
            "packet_rows_sha256": sha_json(packet_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the hidden kernel/odd split is not detected by root-edge or root-incidence parity alone",
                "canonical public charge-frame moments almost separate the closed-return packets",
                "the finite height/action pair completes the invariant classifier",
                "gamma_8 is located as an odd one-basis, five-edge, root-edge-active packet",
            ],
            "what_this_does_not_prove": (
                "This is a finite packet classifier. It does not identify these packet classes with "
                "continuum BMS representations or asymptotic field modes without an additional recovery map."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Turn the complete packet classifier into a canonical finite scattering table: incoming "
            "packet signature, outgoing packet signature, height flux, and hidden R33 transfer."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.hidden_packet_charge_frame_classifier_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite BMS/Carrollian balance, canonical gauge, and all-residue height transport inputs",
            "verify all 2048 packet rows are present and agree with the residue spectrum",
            "verify active edge counts and height actions agree across reports",
            "verify root-edge and root-incidence packet histograms",
            "verify coarse, refined, and complete classifier class counts",
            "verify gamma_8 packet invariants",
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
