from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "projective_packet_charge_frame_classifier"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_spectral_charge_table"
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


def mass_frame(row: dict[str, Any]) -> str:
    trace = int(row["laplacian_trace"])
    if trace == 4:
        return "mass_floor"
    if trace <= 12:
        return "low"
    if trace <= 28:
        return "middle"
    if trace < 40:
        return "high"
    return "mass_ceiling"


def clock_frame(row: dict[str, Any]) -> str:
    if row["sector26_clock_zero_pair"]:
        return "zero_pair"
    if row["sector26_clock_zero_touched"]:
        return "zero_touched"
    if row["sector26_clock_balanced"]:
        return "balanced_nonzero"
    return "delta8_nonzero"


def exposure_frame(row: dict[str, Any]) -> str:
    count = int(row["loop297_atom_union_count"])
    if count == 25:
        return "full"
    if count >= 22:
        return "high"
    if count >= 17:
        return "mid"
    return "low"


def gamma_frame(row: dict[str, Any]) -> str:
    return "gamma8" if row["gamma8_touched"] else "gamma8_silent"


def hidden_frame(row: dict[str, Any]) -> str:
    return "hidden_cancelled" if int(row["corrected_hidden_clock_sum_mod26"]) == 0 else "hidden_open"


def central_frame(row: dict[str, Any]) -> str:
    return "central_negative" if int(row["central_character"]) == -1 else "central_other"


def tenfold_frame(row: dict[str, Any]) -> str:
    return f"{row['tenfold_canonical_class']}|{row['tenfold_optional_active_hamiltonian_class']}"


def build_charge_frame_rows(packet_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in packet_rows:
        frame = {
            "packet_id": int(row["packet_id"]),
            "mass_frame": mass_frame(row),
            "clock_frame": clock_frame(row),
            "exposure_frame": exposure_frame(row),
            "gamma_frame": gamma_frame(row),
            "hidden_frame": hidden_frame(row),
            "central_frame": central_frame(row),
            "tenfold_frame": tenfold_frame(row),
            "laplacian_trace": int(row["laplacian_trace"]),
            "adjacency_trace": int(row["adjacency_trace"]),
            "sector26_clock_pair": [int(value) for value in row["sector26_clock_pair"]],
            "sector26_clock_sum_mod26": int(row["sector26_clock_sum_mod26"]),
            "sector26_clock_delta_mod26": int(row["sector26_clock_delta_mod26"]),
            "loop297_atom_union_count": int(row["loop297_atom_union_count"]),
            "gamma8_mode_count": int(row["gamma8_mode_count"]),
            "full_loop297_atom_exposure": bool(row["full_loop297_atom_exposure"]),
            "sector26_clock_zero_pair": bool(row["sector26_clock_zero_pair"]),
            "sector26_clock_zero_touched": bool(row["sector26_clock_zero_touched"]),
            "sector26_clock_balanced": bool(row["sector26_clock_balanced"]),
            "gamma8_touched": bool(row["gamma8_touched"]),
            "fine_spectral_charge_key": row["fine_spectral_charge_key"],
        }
        frame["charge_frame_key"] = "|".join(
            [
                frame["mass_frame"],
                frame["clock_frame"],
                frame["exposure_frame"],
                frame["gamma_frame"],
                frame["hidden_frame"],
                frame["central_frame"],
                frame["tenfold_frame"],
            ]
        )
        rows.append(frame)
    return rows


def build_theorem() -> dict[str, Any]:
    table_report = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
    packet_rows = table_report["derived"]["packet_spectral_charge_rows"]
    frame_rows = build_charge_frame_rows(packet_rows)
    by_packet_id = {row["packet_id"]: row for row in frame_rows}
    p239 = by_packet_id[239]

    mass_histogram = histogram(Counter(row["mass_frame"] for row in frame_rows))
    clock_histogram = histogram(Counter(row["clock_frame"] for row in frame_rows))
    exposure_histogram = histogram(Counter(row["exposure_frame"] for row in frame_rows))
    gamma_histogram = histogram(Counter(row["gamma_frame"] for row in frame_rows))
    hidden_histogram = histogram(Counter(row["hidden_frame"] for row in frame_rows))
    central_histogram = histogram(Counter(row["central_frame"] for row in frame_rows))
    tenfold_histogram = histogram(Counter(row["tenfold_frame"] for row in frame_rows))
    charge_frame_histogram = histogram(Counter(row["charge_frame_key"] for row in frame_rows))
    axis_quad_histogram = tuple_histogram(
        Counter(
            (
                row["mass_frame"],
                row["clock_frame"],
                row["exposure_frame"],
                row["gamma_frame"],
            )
            for row in frame_rows
        )
    )
    distinguished_sets = {
        "distinguished_packet_id": 239,
        "full_exposure_clock_zero_packet_ids": [
            row["packet_id"]
            for row in frame_rows
            if row["full_loop297_atom_exposure"] and row["sector26_clock_zero_touched"]
        ],
        "full_exposure_clock_zero_pair_packet_ids": [
            row["packet_id"]
            for row in frame_rows
            if row["full_loop297_atom_exposure"] and row["sector26_clock_zero_pair"]
        ],
        "full_exposure_clock_zero_gamma_silent_packet_ids": [
            row["packet_id"]
            for row in frame_rows
            if row["full_loop297_atom_exposure"]
            and row["sector26_clock_zero_touched"]
            and not row["gamma8_touched"]
        ],
        "same_frame_as_packet239_packet_ids": [
            row["packet_id"]
            for row in frame_rows
            if row["charge_frame_key"] == p239["charge_frame_key"]
        ],
        "same_fine_spectral_charge_as_packet239_packet_ids": [
            row["packet_id"]
            for row in frame_rows
            if row["fine_spectral_charge_key"] == p239["fine_spectral_charge_key"]
        ],
    }

    checks = {
        "projective_packet_spectral_charge_table_is_certified": table_report.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and table_report.get("all_checks_pass") is True,
        "charge_frame_has_512_rows": len(frame_rows) == 512,
        "charge_frame_axes_are_named": set(frame_rows[0])
        >= {
            "mass_frame",
            "clock_frame",
            "exposure_frame",
            "gamma_frame",
            "hidden_frame",
            "central_frame",
            "tenfold_frame",
            "charge_frame_key",
        },
        "mass_axis_histogram_matches": mass_histogram
        == {
            "high": 45,
            "low": 45,
            "mass_ceiling": 1,
            "mass_floor": 1,
            "middle": 420,
        },
        "clock_axis_histogram_matches": clock_histogram
        == {
            "balanced_nonzero": 235,
            "delta8_nonzero": 215,
            "zero_pair": 21,
            "zero_touched": 41,
        },
        "exposure_axis_histogram_matches": exposure_histogram
        == {"full": 20, "high": 247, "low": 45, "mid": 200},
        "gamma_axis_splits_evenly": gamma_histogram == {"gamma8": 256, "gamma8_silent": 256},
        "hidden_axis_is_cancelled_everywhere": hidden_histogram == {"hidden_cancelled": 512},
        "central_axis_is_negative_everywhere": central_histogram == {"central_negative": 512},
        "tenfold_axis_is_ai_bdi_everywhere": tenfold_histogram == {"AI|BDI": 512},
        "charge_frame_key_count_is_47": len(charge_frame_histogram) == 47
        and max(charge_frame_histogram.values()) == 56,
        "axis_quad_key_count_is_47": len(axis_quad_histogram) == 47
        and max(axis_quad_histogram.values()) == 56,
        "packet239_has_distinguished_charge_frame": p239["mass_frame"] == "high"
        and p239["clock_frame"] == "zero_pair"
        and p239["exposure_frame"] == "full"
        and p239["gamma_frame"] == "gamma8_silent"
        and p239["hidden_frame"] == "hidden_cancelled"
        and p239["central_frame"] == "central_negative"
        and p239["tenfold_frame"] == "AI|BDI",
        "packet239_is_unique_full_exposure_clock_zero_packet": distinguished_sets[
            "full_exposure_clock_zero_packet_ids"
        ]
        == [239]
        and distinguished_sets["full_exposure_clock_zero_pair_packet_ids"] == [239],
        "packet239_is_unique_in_charge_frame_and_fine_key": distinguished_sets[
            "same_frame_as_packet239_packet_ids"
        ]
        == [239]
        and distinguished_sets["same_fine_spectral_charge_as_packet239_packet_ids"] == [239],
        "packet239_charge_values_match": p239["laplacian_trace"] == 32
        and p239["adjacency_trace"] == -10
        and p239["sector26_clock_pair"] == [0, 0]
        and p239["sector26_clock_sum_mod26"] == 0
        and p239["sector26_clock_delta_mod26"] == 0
        and p239["loop297_atom_union_count"] == 25
        and p239["gamma8_mode_count"] == 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        if all_checks_pass
        else "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.projective_packet_charge_frame_classifier",
        "status": status,
        "object": "d20",
        "claim": (
            "The projective packet spectral/charge table admits a finite charge-frame classifier with named "
            "mass, clock, exposure, gamma8, hidden, central, and tenfold axes. The classifier has 47 occupied "
            "charge-frame classes and isolates packet 239 as the unique full Loop_297 exposure, sector-26 "
            "clock-zero packet."
        ),
        "definition": {
            "mass_frame": "Coarse spectral band from packet laplacian trace.",
            "clock_frame": "sector-26 class: zero_pair, zero_touched, balanced_nonzero, or delta8_nonzero.",
            "exposure_frame": "Loop_297 atom exposure tier: low, mid, high, or full.",
            "gamma_frame": "gamma8 or gamma8_silent according to packet gamma8 incidence.",
            "hidden_frame": "hidden_cancelled when corrected hidden clock sum is zero.",
            "central_frame": "central_negative when the projective central character is -1.",
            "tenfold_frame": "canonical AI plus optional active-Hamiltonian BDI witness.",
        },
        "inputs": {
            "projective_packet_spectral_charge_table_report": {
                "path": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
            },
        },
        "derived": {
            "classifier_summary": {
                "packet_count": len(frame_rows),
                "charge_frame_class_count": len(charge_frame_histogram),
                "charge_frame_max_multiplicity": max(charge_frame_histogram.values()),
                "distinguished_packet_id": 239,
                "distinguished_packet_charge_frame_key": p239["charge_frame_key"],
                "distinguished_packet_fine_spectral_charge_key": p239[
                    "fine_spectral_charge_key"
                ],
            },
            "axis_histograms": {
                "mass_frame": mass_histogram,
                "clock_frame": clock_histogram,
                "exposure_frame": exposure_histogram,
                "gamma_frame": gamma_histogram,
                "hidden_frame": hidden_histogram,
                "central_frame": central_histogram,
                "tenfold_frame": tenfold_histogram,
                "charge_frame_key": charge_frame_histogram,
                "mass_clock_exposure_gamma_key": axis_quad_histogram,
            },
            "distinguished_packet_sets": distinguished_sets,
            "distinguished_packet_239": p239,
            "charge_frame_rows": frame_rows,
            "charge_frame_rows_sha256": sha_json(frame_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the packet spectral/charge table has named classifier axes",
                "the finite charge-frame classifier has 47 occupied classes",
                "packet 239 is unique by both its named charge-frame key and its fine spectral/charge key",
                "packet 239 is the unique full Loop_297 exposure packet with sector-26 clock zero",
            ],
            "what_this_does_not_prove": (
                "This does not yet identify packet 239 with a physical vacuum or ground state. It certifies "
                "the finite invariant signature that any such interpretation must preserve."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Test packet 239 as the finite vacuum/seed candidate: compute its stabilizer inside the signed "
            "projective kernel action and compare it with the full-exposure packet stabilizers."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.projective_packet_charge_frame_classifier_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify projective packet spectral/charge table input",
            "construct named mass, clock, exposure, gamma8, hidden, central, and tenfold axes",
            "verify all axis histograms and occupied charge-frame class count",
            "verify packet 239 charge-frame values",
            "verify packet 239 is the unique full-exposure sector-26 clock-zero packet",
            "verify packet 239 is unique by charge-frame key and fine spectral/charge key",
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
