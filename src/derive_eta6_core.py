from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_core"
STATUS = "ETA6_CORE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

GAP_REPORT = D20_INVARIANTS / "proof_obligations" / "eta6_gap" / "report.json"
P20_REPORT = D20_INVARIANTS / "proof_obligations" / "eta6_p20" / "report.json"
P21_REPORT = D20_INVARIANTS / "proof_obligations" / "eta6_p21" / "report.json"
P26_REPORT = D20_INVARIANTS / "proof_obligations" / "eta6_p26" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_core.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_core.py"

SPINE_COLUMNS = [
    "rank",
    "report_code",
    "role_code",
    "certified_flag",
    "primary_margin",
    "primary_floor",
    "row_count",
    "raw_count",
    "support_equalizer_count",
    "min_count",
    "universal_claim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_NAMES = [
    "spine_report_count",
    "certified_spine_count",
    "input_certificates_ok",
    "hpol_margin",
    "hpol_row_count",
    "hpol_min_count",
    "hpol_zero_count",
    "gordan_no_positive_annihilator_flag",
    "replacement_margin",
    "replacement_row_count",
    "global_six_floor",
    "global_six_count",
    "global_at_floor_count",
    "global_below_floor_count",
    "global_support_equal_count",
    "gate_floor",
    "gate_carrier_neutral",
    "gate_eta6_preserved_count",
    "gate_rebuilt_claim",
    "packet_component_count",
    "packet_positive_row_total",
    "packet_min_margin",
    "packet_support_equalizer_absent",
    "best_ids_agree_flag",
    "bounded_horizon_flag",
    "universal_completion_claim",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}
REPORT_CODES = {
    "gap": 0,
    "p20": 1,
    "p21": 2,
    "p26": 3,
}
ROLE_CODES = {
    "gap": 0,
    "floor": 1,
    "gate": 2,
    "packet": 3,
}
BEST_IDS = [1, 47, 57, 79, 110, 128]


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def cert_flag(report: dict[str, Any]) -> int:
    return int(report.get("all_checks_pass") is True)


def min_component_margin(p26_witness: dict[str, Any]) -> int:
    return min(int(row["margin"]) for row in p26_witness["components"])


def p25_floor_from_p26(p26_witness: dict[str, Any]) -> int:
    for row in p26_witness["components"]:
        if row.get("name") == "p25 pentagon support-spread floor":
            return int(row["margin"])
    raise ValueError("p26 p25 floor component missing")


def build_rows() -> dict[str, Any]:
    reports = {
        "gap": load_json(GAP_REPORT),
        "p20": load_json(P20_REPORT),
        "p21": load_json(P21_REPORT),
        "p26": load_json(P26_REPORT),
    }
    gap_w = reports["gap"]["witness"]
    p20_w = reports["p20"]["witness"]
    p21_w = reports["p21"]["witness"]
    p26_w = reports["p26"]["witness"]
    p26_boundary = p26_w["claim_boundary"]

    hpol = gap_w["hpol"]
    repl = gap_w["repl"]
    p26_min_margin = min_component_margin(p26_w)
    p25_floor = p25_floor_from_p26(p26_w)
    best_ids_agree = int(
        p20_w["best_p5_ids"] == BEST_IDS
        and p21_w["gate_p5_ids"] == BEST_IDS
    )
    input_ok = int(all(cert_flag(report) for report in reports.values()))
    universal_claim = int(p26_boundary["universal_completion_claim"])

    obs = {
        "spine_report_count": len(reports),
        "certified_spine_count": sum(cert_flag(report) for report in reports.values()),
        "input_certificates_ok": input_ok,
        "hpol_margin": hpol["min_margin"],
        "hpol_row_count": hpol["row_count"],
        "hpol_min_count": hpol["min_margin_count"],
        "hpol_zero_count": hpol["zero_count"],
        "gordan_no_positive_annihilator_flag": int(
            hpol["min_margin"] > 0 and hpol["zero_count"] == 0
        ),
        "replacement_margin": repl["min_margin"],
        "replacement_row_count": repl["row_count"],
        "global_six_floor": p20_w["global_min_spread"],
        "global_six_count": p20_w["full_six_count"],
        "global_at_floor_count": p20_w["global_at_min_count"],
        "global_below_floor_count": p20_w["global_below_min_count"],
        "global_support_equal_count": p20_w["global_support_equal_count"],
        "gate_floor": p21_w["global_floor"],
        "gate_carrier_neutral": p21_w["carrier"]["carrier_neutral"],
        "gate_eta6_preserved_count": p21_w["carrier"]["eta6_preserved_count"],
        "gate_rebuilt_claim": p21_w["checked_margins"]["rebuilt_carrier_claim"],
        "packet_component_count": p26_boundary["checked_component_count"],
        "packet_positive_row_total": p26_boundary["checked_positive_row_total"],
        "packet_min_margin": p26_min_margin,
        "packet_support_equalizer_absent": p26_boundary["support_equalizer_absent"],
        "best_ids_agree_flag": best_ids_agree,
        "bounded_horizon_flag": 0,
        "universal_completion_claim": universal_claim,
    }
    obs["bounded_horizon_flag"] = int(
        input_ok == 1
        and obs["gordan_no_positive_annihilator_flag"] == 1
        and obs["global_six_floor"] == 492_736
        and obs["global_below_floor_count"] == 0
        and obs["global_support_equal_count"] == 0
        and obs["gate_carrier_neutral"] == 1
        and obs["gate_eta6_preserved_count"] == 6
        and obs["gate_rebuilt_claim"] == 0
        and obs["packet_min_margin"] == 1
        and obs["packet_support_equalizer_absent"] == 1
        and obs["best_ids_agree_flag"] == 1
        and obs["universal_completion_claim"] == 0
    )

    spine_rows = [
        {
            "rank": 0,
            "report_code": REPORT_CODES["gap"],
            "role_code": ROLE_CODES["gap"],
            "certified_flag": cert_flag(reports["gap"]),
            "primary_margin": hpol["min_margin"],
            "primary_floor": 0,
            "row_count": hpol["row_count"],
            "raw_count": 0,
            "support_equalizer_count": hpol["zero_count"],
            "min_count": hpol["min_margin_count"],
            "universal_claim_flag": 0,
        },
        {
            "rank": 1,
            "report_code": REPORT_CODES["p20"],
            "role_code": ROLE_CODES["floor"],
            "certified_flag": cert_flag(reports["p20"]),
            "primary_margin": 0,
            "primary_floor": p20_w["global_min_spread"],
            "row_count": p20_w["full_six_count"],
            "raw_count": p20_w["full_six_count"],
            "support_equalizer_count": p20_w["global_support_equal_count"],
            "min_count": p20_w["global_at_min_count"],
            "universal_claim_flag": 0,
        },
        {
            "rank": 2,
            "report_code": REPORT_CODES["p21"],
            "role_code": ROLE_CODES["gate"],
            "certified_flag": cert_flag(reports["p21"]),
            "primary_margin": p21_w["checked_margins"]["hpol_min_margin"],
            "primary_floor": p21_w["global_floor"],
            "row_count": p21_w["carrier"]["eta6_preserved_count"],
            "raw_count": p21_w["carrier"]["eta6_preserved_count"],
            "support_equalizer_count": p21_w["global_equalizer_count"],
            "min_count": p21_w["global_at_floor_count"],
            "universal_claim_flag": p21_w["checked_margins"]["rebuilt_carrier_claim"],
        },
        {
            "rank": 3,
            "report_code": REPORT_CODES["p26"],
            "role_code": ROLE_CODES["packet"],
            "certified_flag": cert_flag(reports["p26"]),
            "primary_margin": p26_min_margin,
            "primary_floor": p25_floor,
            "row_count": p26_boundary["checked_positive_row_total"],
            "raw_count": p26_boundary["checked_component_count"],
            "support_equalizer_count": 1 - p26_boundary["support_equalizer_absent"],
            "min_count": p26_boundary["checked_component_count"],
            "universal_claim_flag": p26_boundary["universal_completion_claim"],
        },
    ]
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": int(obs[name]),
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "reports": reports,
        "obs": obs,
        "obs_rows": obs_rows,
        "spine_rows": spine_rows,
        "best_ids": BEST_IDS,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    spine_table = table_from_rows(SPINE_COLUMNS, rows["spine_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    reports = rows["reports"]
    obs = rows["obs"]
    checks = {
        "input_certificates_available": obs["input_certificates_ok"] == 1,
        "gordan_gap_strict": (
            obs["hpol_row_count"],
            obs["hpol_margin"],
            obs["hpol_min_count"],
            obs["hpol_zero_count"],
            obs["gordan_no_positive_annihilator_flag"],
            obs["replacement_row_count"],
            obs["replacement_margin"],
        )
        == (4_903_515, 1, 2, 0, 1, 2_831_367, 146),
        "global_six_floor_exact": (
            obs["global_six_floor"],
            obs["global_six_count"],
            obs["global_at_floor_count"],
            obs["global_below_floor_count"],
            obs["global_support_equal_count"],
        )
        == (492_736, 11_143_364_232, 1, 0, 0),
        "gate_is_carrier_neutral": (
            obs["gate_floor"],
            obs["gate_carrier_neutral"],
            obs["gate_eta6_preserved_count"],
            obs["gate_rebuilt_claim"],
        )
        == (492_736, 1, 6, 0),
        "finite_margin_packet_strict": (
            obs["packet_component_count"],
            obs["packet_positive_row_total"],
            obs["packet_min_margin"],
            obs["packet_support_equalizer_absent"],
        )
        == (4, 7_735_158, 1, 1),
        "spine_consensus_matches": obs["best_ids_agree_flag"] == 1,
        "bounded_not_universal": (
            obs["bounded_horizon_flag"],
            obs["universal_completion_claim"],
        )
        == (1, 0),
        "table_shapes_match_codebooks": (
            tuple(spine_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (len(REPORT_CODES), len(SPINE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "eta6_core",
        "reading": (
            "eta6 behaves as a bounded finite horizon in the checked packet: "
            "there is a strict Gordan gap, an exact global six-move floor, a "
            "carrier-neutral gate, and a strict margin packet."
        ),
        "core_claim": "bounded_horizon",
        "best_p5_ids": rows["best_ids"],
        "gordan_gap": {
            "hpol_margin": obs["hpol_margin"],
            "hpol_rows": obs["hpol_row_count"],
            "replacement_margin": obs["replacement_margin"],
            "replacement_rows": obs["replacement_row_count"],
        },
        "six_floor": {
            "floor": obs["global_six_floor"],
            "full_six_count": obs["global_six_count"],
            "at_floor_count": obs["global_at_floor_count"],
            "below_floor_count": obs["global_below_floor_count"],
            "support_equalizer_count": obs["global_support_equal_count"],
        },
        "gate": {
            "floor": obs["gate_floor"],
            "carrier_neutral": obs["gate_carrier_neutral"],
            "eta6_preserved_count": obs["gate_eta6_preserved_count"],
            "rebuilt_carrier_claim": obs["gate_rebuilt_claim"],
        },
        "margin_packet": {
            "component_count": obs["packet_component_count"],
            "checked_positive_row_total": obs["packet_positive_row_total"],
            "min_margin": obs["packet_min_margin"],
            "support_equalizer_absent": obs["packet_support_equalizer_absent"],
        },
        "claim_boundary": {
            "checked_spine_reports": obs["spine_report_count"],
            "checked_positive_row_total": obs["packet_positive_row_total"],
            "checked_global_six_count": obs["global_six_count"],
            "bounded_horizon_flag": obs["bounded_horizon_flag"],
            "universal_completion_claim": obs["universal_completion_claim"],
        },
        "spine_table_sha256": sha_array(spine_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    core = {
        "schema": "eta6.core@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_gap + eta6_p20 + eta6_p21 + eta6_p26",
            "test": "compact structural horizon spine",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.core.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_CORE_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "eta6_core is the compact structural certificate for the current "
            "eta6 spine. It certifies bounded horizon behavior across the "
            "checked row universes and admissible p/F support screens: positive "
            "gap, exact six-move floor, neutral gate, strict margin packet, and "
            "no checked support equalizer. It is not a universal completion theorem."
        ),
        "stage_protocol": {
            "draft": "select the compact eta6 evidence spine",
            "witness": "read fixed integers from certified reports",
            "coherence": "require the floor and gate layers to agree on the same best p5 ids",
            "closure": "emit a bounded horizon certificate with explicit scope",
            "emit": "write eta6_core artifacts and verifier hook",
        },
        "inputs": {
            "gap_report": input_entry(GAP_REPORT, {"status": reports["gap"].get("status")}),
            "p20_report": input_entry(P20_REPORT, {"status": reports["p20"].get("status")}),
            "p21_report": input_entry(P21_REPORT, {"status": reports["p21"].get("status")}),
            "p26_report": input_entry(P26_REPORT, {"status": reports["p26"].get("status")}),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "core": relpath(OUT_DIR / "core.json"),
            "spine_csv": relpath(OUT_DIR / "spine.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "eta6 hpol rows have margin at least 1 in the checked gap universe",
                "no positive annihilating dependence exists for the checked hpol signed-row matrix",
                "the exact p5 six-move floor is 492736 over 11143364232 sextuples",
                "the floor gate preserves all six eta6 carrier entries and is carrier-neutral",
                "the p26 packet has strict positive margins across four checked components",
            ],
            "does_not_certify_because_out_of_scope": [
                "all future carrier completions",
                "every possible F-symbol intervention outside the checked admissible screens",
                "a semantic proof of global C985 associator closure on a rebuilt carrier",
                "that eta6 is uncrossable outside these finite row and branch universes",
            ],
        },
        "next_highest_yield_item": (
            "Keep eta6_p40 as a stress appendix; next certify a non-pNN "
            "recoupling class if a new obstruction family is needed."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.core.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.core.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "core": core,
        "spine_csv": csv_text(SPINE_COLUMNS, rows["spine_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "spine_table": spine_table,
        "obs_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "core.json", payloads["core"])
    (OUT_DIR / "spine.csv").write_text(payloads["spine_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        spine_table=payloads["spine_table"],
        observable_table=payloads["obs_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
