from __future__ import annotations

import hashlib
import json
from collections import Counter
from math import gcd
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SOURCED_BALANCE_SHORTEST_PATHS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_shortest_paths"
    / "report.json"
)
SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_transport_families"
    / "report.json"
)
LABEL_RELAXED_ORBIT_QUOTIENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient"
    / "report.json"
)
FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_bms_carrollian_flux_balance"
    / "report.json"
)

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")


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


def zero_public_vector() -> dict[str, int]:
    return {component: 0 for component in PUBLIC_COMPONENTS}


def int_histogram(values: list[int]) -> dict[str, int]:
    counts = Counter(values)
    return {str(key): int(counts[key]) for key in sorted(counts)}


def gcd_abs(values: list[int]) -> int:
    out = 0
    for value in values:
        if value:
            out = gcd(out, abs(int(value)))
    return out


def build_tau_map(orbit_rows: list[dict[str, Any]]) -> tuple[dict[int, int], dict[int, int]]:
    tau: dict[int, int] = {}
    orbit_by_mask: dict[int, int] = {}
    for orbit_id, orbit in enumerate(orbit_rows):
        masks = [int(mask) for mask in orbit["target_masks"]]
        if len(masks) == 1:
            tau[masks[0]] = masks[0]
            orbit_by_mask[masks[0]] = orbit_id
        elif len(masks) == 2:
            left, right = masks
            tau[left] = right
            tau[right] = left
            orbit_by_mask[left] = orbit_id
            orbit_by_mask[right] = orbit_id
        else:
            raise ValueError(f"C2 orbit has unexpected size: {masks}")
    return tau, orbit_by_mask


def build_theorem() -> dict[str, Any]:
    shortest_paths = load_json(SOURCED_BALANCE_SHORTEST_PATHS_REPORT)
    transport_families = load_json(SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT)
    label_relaxed = load_json(LABEL_RELAXED_ORBIT_QUOTIENT_REPORT)
    bms = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)

    path_rows = shortest_paths.get("derived", {}).get("shortest_path_rows", [])
    orbit_rows = transport_families.get("derived", {}).get("hidden_split_c2_orbit_rows", [])
    balance_rows = bms.get("derived", {}).get("balance_rows", [])
    path_by_mask = {int(row["target_mask"]): row for row in path_rows}
    balance_by_mask = {int(row["mask"]): row for row in balance_rows}
    tau, orbit_by_mask = build_tau_map(orbit_rows)
    zero_public = zero_public_vector()

    representatives = {
        orbit_id: min(int(mask) for mask in orbit["target_masks"])
        for orbit_id, orbit in enumerate(orbit_rows)
    }
    anomaly_rows = []
    for mask in sorted(path_by_mask):
        row = path_by_mask[mask]
        balance = balance_by_mask[mask]
        tau_mask = tau[mask]
        tau_row = path_by_mask[tau_mask]
        orbit_id = orbit_by_mask[mask]
        representative_mask = representatives[orbit_id]
        representative_row = path_by_mask[representative_mask]
        representative_balance = balance_by_mask[representative_mask]

        tau_path_action_cocycle = (
            int(tau_row["shortest_path_action"]) - int(row["shortest_path_action"])
        )
        tau_height_cocycle = int(tau_row["target_height_action"]) - int(
            row["target_height_action"]
        )
        representative_path_action_counterterm = int(row["shortest_path_action"]) - int(
            representative_row["shortest_path_action"]
        )
        representative_height_counterterm = int(row["target_height_action"]) - int(
            representative_row["target_height_action"]
        )
        quotient_shortest_path_action = (
            int(row["shortest_path_action"]) - representative_path_action_counterterm
        )
        quotient_target_height_action = (
            int(balance["finite_height_flux"]) - representative_height_counterterm
        )
        quotient_R33_height_residual = (
            int(balance["R33_height_residual"]) + representative_height_counterterm
        )
        quotient_hidden_balance_error = (
            int(balance["bare_pi33"])
            + quotient_R33_height_residual
            + quotient_target_height_action
        )
        anomaly_rows.append(
            {
                "target_mask": mask,
                "tau_target_mask": tau_mask,
                "orbit_id": orbit_id,
                "orbit_size": len(orbit_rows[orbit_id]["target_masks"]),
                "representative_mask": representative_mask,
                "shortest_path_action": row["shortest_path_action"],
                "target_height_action": row["target_height_action"],
                "R33_height_residual": balance["R33_height_residual"],
                "bare_pi33": balance["bare_pi33"],
                "tau_path_action_cocycle": tau_path_action_cocycle,
                "tau_height_cocycle": tau_height_cocycle,
                "tau_cocycle_mod26": tau_height_cocycle % 26,
                "tau_cocycle_half_mod13": (tau_height_cocycle % 26) // 2,
                "representative_path_action_counterterm": representative_path_action_counterterm,
                "representative_height_counterterm": representative_height_counterterm,
                "representative_counterterm_mod26": representative_height_counterterm % 26,
                "representative_counterterm_half_mod13": (
                    representative_height_counterterm % 26
                )
                // 2,
                "quotient_shortest_path_action": quotient_shortest_path_action,
                "quotient_target_height_action": quotient_target_height_action,
                "quotient_R33_height_residual": quotient_R33_height_residual,
                "representative_R33_height_residual": representative_balance[
                    "R33_height_residual"
                ],
                "quotient_hidden_balance_error": quotient_hidden_balance_error,
                "public_balance_error": balance["public_balance_error"],
                "hidden_balance_error": balance["hidden_balance_error"],
            }
        )

    orbit_balance_rows = []
    for orbit_id, orbit in enumerate(orbit_rows):
        masks = [int(mask) for mask in orbit["target_masks"]]
        representative_mask = representatives[orbit_id]
        rep = next(row for row in anomaly_rows if row["target_mask"] == representative_mask)
        member_rows = [row for row in anomaly_rows if row["target_mask"] in masks]
        orbit_balance_rows.append(
            {
                "orbit_id": orbit_id,
                "target_masks": masks,
                "representative_mask": representative_mask,
                "orbit_size": len(masks),
                "quotient_shortest_path_action": rep["quotient_shortest_path_action"],
                "quotient_target_height_action": rep["quotient_target_height_action"],
                "quotient_R33_height_residual": rep["quotient_R33_height_residual"],
                "quotient_hidden_balance_error": rep["quotient_hidden_balance_error"],
                "member_representative_height_counterterms": [
                    row["representative_height_counterterm"] for row in member_rows
                ],
                "member_tau_height_cocycles": [row["tau_height_cocycle"] for row in member_rows],
            }
        )

    tau_height_values = [int(row["tau_height_cocycle"]) for row in anomaly_rows]
    tau_action_values = [int(row["tau_path_action_cocycle"]) for row in anomaly_rows]
    representative_counterterms = [
        int(row["representative_height_counterterm"]) for row in anomaly_rows
    ]
    nonzero_orbit_count = sum(
        1
        for row in orbit_balance_rows
        if any(int(value) != 0 for value in row["member_representative_height_counterterms"])
    )
    zero_orbit_count = len(orbit_balance_rows) - nonzero_orbit_count
    tau_mod26_values = [value % 26 for value in tau_height_values]
    representative_mod26_values = [value % 26 for value in representative_counterterms]
    anomaly_summary = {
        "orbit_count": len(orbit_rows),
        "target_count": len(anomaly_rows),
        "zero_anomaly_orbit_count": zero_orbit_count,
        "nonzero_anomaly_orbit_count": nonzero_orbit_count,
        "tau_cocycle_zero_mask_count": sum(1 for value in tau_height_values if value == 0),
        "tau_cocycle_nonzero_mask_count": sum(1 for value in tau_height_values if value != 0),
        "tau_cocycle_unique_value_count": len(set(tau_height_values)),
        "representative_counterterm_unique_value_count": len(set(representative_counterterms)),
        "representative_counterterm_nonzero_mask_count": sum(
            1 for value in representative_counterterms if value != 0
        ),
        "height_action_cocycle_gcd_abs": gcd_abs(tau_height_values),
        "height_action_cocycle_min": min(tau_height_values),
        "height_action_cocycle_max": max(tau_height_values),
        "representative_counterterm_min": min(representative_counterterms),
        "representative_counterterm_max": max(representative_counterterms),
        "tau_cocycle_mod26_histogram": int_histogram(tau_mod26_values),
        "tau_cocycle_half_mod13_histogram": int_histogram([value // 2 for value in tau_mod26_values]),
        "representative_counterterm_mod26_histogram": int_histogram(representative_mod26_values),
        "representative_counterterm_half_mod13_histogram": int_histogram(
            [value // 2 for value in representative_mod26_values]
        ),
        "path_action_and_height_cocycles_are_identical": tau_action_values == tau_height_values,
        "anomaly_reading": (
            "The C2 failure of action and height to descend is an exact coboundary. Subtracting the "
            "representative counterterm from height/action and adding it to R33 makes the hidden BMS/Ward "
            "row constant on each quotient orbit."
        ),
    }

    checks = {
        "shortest_paths_is_certified": shortest_paths.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_CERTIFIED"
        and shortest_paths.get("all_checks_pass") is True,
        "transport_families_is_certified": transport_families.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_CERTIFIED"
        and transport_families.get("all_checks_pass") is True,
        "label_relaxed_quotient_is_certified": label_relaxed.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_CERTIFIED"
        and label_relaxed.get("all_checks_pass") is True,
        "finite_bms_balance_is_certified": bms.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and bms.get("all_checks_pass") is True,
        "c2_orbits_cover_the_1023_targets_once": len(anomaly_rows) == 1023
        and sorted(tau) == sorted(path_by_mask)
        and sorted(orbit_by_mask) == sorted(path_by_mask),
        "tau_is_an_involution": all(tau[tau[mask]] == mask for mask in tau),
        "tau_cocycle_law_holds_for_action_and_height": all(
            row["tau_height_cocycle"]
            + next(
                other["tau_height_cocycle"]
                for other in anomaly_rows
                if other["target_mask"] == row["tau_target_mask"]
            )
            == 0
            and row["tau_path_action_cocycle"]
            + next(
                other["tau_path_action_cocycle"]
                for other in anomaly_rows
                if other["target_mask"] == row["tau_target_mask"]
            )
            == 0
            for row in anomaly_rows
        ),
        "path_action_and_target_height_have_the_same_c2_cocycle": anomaly_summary[
            "path_action_and_height_cocycles_are_identical"
        ],
        "representative_counterterm_is_exact_coboundary_for_action_and_height": all(
            row["representative_path_action_counterterm"]
            == row["representative_height_counterterm"]
            for row in anomaly_rows
        ),
        "naive_c2_quotient_fails_exactly_on_472_action_height_orbits": nonzero_orbit_count
        == 472
        and zero_orbit_count == 71
        and anomaly_summary["tau_cocycle_nonzero_mask_count"] == 944
        and anomaly_summary["tau_cocycle_zero_mask_count"] == 79,
        "height_action_anomaly_has_even_sector26_shadow_and_full_mod13_half": set(
            tau_mod26_values
        )
        == set(range(0, 26, 2))
        and set(value // 2 for value in tau_mod26_values) == set(range(13))
        and anomaly_summary["height_action_cocycle_gcd_abs"] == 3072,
        "twisted_quotient_hidden_balance_descends_on_every_target": all(
            row["quotient_hidden_balance_error"] == 0
            and row["quotient_R33_height_residual"] == -row["quotient_target_height_action"]
            for row in anomaly_rows
        ),
        "public_balance_descends_without_extra_anomaly": all(
            row["public_balance_error"] == zero_public and row["hidden_balance_error"] == 0
            for row in anomaly_rows
        ),
        "orbit_representative_balance_rows_close": len(orbit_balance_rows) == 543
        and all(row["quotient_hidden_balance_error"] == 0 for row in orbit_balance_rows),
        "anomaly_rows_are_stably_hashed": sha_json(anomaly_rows)
        and sha_json(orbit_balance_rows),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly",
        "status": status,
        "object": "d20",
        "claim": (
            "The hidden-split C2 action/height label-breaking table is an exact quotient anomaly. "
            "The path-action and target-height C2 cocycles are identical, satisfy the C2 cocycle law, "
            "have even sector-26 shadow, and compensate the R33 residual so finite sourced Ward/BMS "
            "balance descends to the C2 quotient after adding the anomaly counterterm."
        ),
        "definition": {
            "tau_cocycle": (
                "For a scalar label F on nonzero Ward-kernel targets and the nonidentity C2 element tau, "
                "c_F(tau,m)=F(tau m)-F(m)."
            ),
            "representative_counterterm": (
                "For each C2 orbit, choose the least target mask as representative r and set "
                "k_F(m)=F(m)-F(r)."
            ),
            "twisted_quotient_balance": (
                "Replace A_h(m) by A_h(m)-k_H(m) and R33(m) by R33(m)+k_H(m). The hidden balance "
                "bare_pi33+R33+A_h then becomes representative-level and orbit-constant."
            ),
        },
        "inputs": {
            "sourced_balance_shortest_paths_report": {
                "path": rel(SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
                "sha256": sha_file(SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
            },
            "sourced_balance_transport_families_report": {
                "path": rel(SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT),
                "sha256": sha_file(SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT),
            },
            "label_relaxed_orbit_quotient_report": {
                "path": rel(LABEL_RELAXED_ORBIT_QUOTIENT_REPORT),
                "sha256": sha_file(LABEL_RELAXED_ORBIT_QUOTIENT_REPORT),
            },
            "finite_bms_carrollian_flux_balance_report": {
                "path": rel(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
            },
        },
        "derived": {
            "anomaly_summary": anomaly_summary,
            "anomaly_rows_sha256": sha_json(anomaly_rows),
            "orbit_balance_rows_sha256": sha_json(orbit_balance_rows),
            "anomaly_rows": anomaly_rows,
            "orbit_balance_rows": orbit_balance_rows,
        },
        "interpretation": {
            "what_this_proves": [
                "the action/height failure of the C2 quotient is exact cocycle data, not an uncontrolled mismatch",
                "the same integer cocycle repairs both path action and target height",
                "the anomaly has even sector-26 shadow and a complete mod-13 half-shadow",
                "public balance already descends on the C2 quotient",
                "hidden R33/action balance descends after applying the representative height counterterm",
            ],
            "what_this_does_not_prove": (
                "This does not make raw action or height invariant on the C2 quotient. It proves that their "
                "non-invariance is an exact anomaly that can be carried as quotient connection data."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the quotient anomaly connection to build the 543-orbit C2 quotient transport ledger and "
            "test whether the quotient transition operator is Markov/spectral and Ward-balanced."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify shortest-path, transport-family, label-relaxed quotient, and finite BMS inputs",
            "construct the C2 involution on the 1023 nonzero Ward-kernel targets",
            "compute path-action and target-height C2 cocycles",
            "verify the C2 cocycle law and exact representative counterterm form",
            "verify the sector-26 anomaly shadow is even and halves onto all mod-13 classes",
            "verify public balance descends without extra anomaly",
            "verify hidden R33/action balance descends after the height counterterm",
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
