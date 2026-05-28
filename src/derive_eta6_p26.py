from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_gap as gap
    from . import derive_eta6_p24 as p24
    from . import derive_eta6_p25 as p25
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_gap as gap
    import derive_eta6_p24 as p24
    import derive_eta6_p25 as p25
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p26"
STATUS = "ETA6_P26_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

GAP_REPORT = gap.OUT_DIR / "report.json"
P24_REPORT = p24.OUT_DIR / "report.json"
P24_TABLES = p24.OUT_DIR / "tables.npz"
P25_REPORT = p25.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p26.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p26.py"

MARGIN_COLUMNS = [
    "component_id",
    "component_code",
    "margin_value",
    "row_count",
    "positive_count",
    "zero_count",
    "strict_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "component_count": 0,
    "hpol_row_count": 1,
    "hpol_min_margin": 2,
    "hpol_min_count": 3,
    "hpol_no_positive_annihilator_flag": 4,
    "repl_row_count": 5,
    "repl_min_margin": 6,
    "p24_lift_row_count": 7,
    "p24_lift_positive_count": 8,
    "p24_lift_min_slack_x1e12": 9,
    "p25_extension_count": 10,
    "p25_support_equal_count": 11,
    "p25_min_support_spread": 12,
    "p25_max_support_spread": 13,
    "p25_mult_equal_count": 14,
    "checked_positive_row_total": 15,
    "min_component_margin": 16,
    "all_components_strict_flag": 17,
    "support_equalizer_absent_flag": 18,
    "universal_completion_claim_flag": 19,
}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def p24_lift_stats() -> dict[str, int]:
    tables = np.load(P24_TABLES, allow_pickle=False)
    face_rows = table_rows(
        np.asarray(tables["face_table"], dtype=np.int64),
        p24.FACE_COLUMNS,
    )
    return {
        "row_count": sum(row["support_row_count"] for row in face_rows),
        "positive_count": sum(row["positive_support_count"] for row in face_rows),
        "zero_count": sum(
            row["support_row_count"] - row["positive_support_count"]
            for row in face_rows
        ),
        "min_slack_x1e12": min(row["min_slack_x1e12"] for row in face_rows),
    }


def build_payload_rows() -> dict[str, Any]:
    gap_report = load_json(GAP_REPORT)
    p24_report = load_json(P24_REPORT)
    p25_report = load_json(P25_REPORT)
    hpol = gap_report["witness"]["hpol"]
    repl = gap_report["witness"]["repl"]
    lift = p24_lift_stats()
    p25_witness = p25_report["witness"]
    p25_boundary = p25_witness["claim_boundary"]

    margin_rows = [
        {
            "component_id": 0,
            "component_code": 0,
            "margin_value": hpol["min_margin"],
            "row_count": hpol["row_count"],
            "positive_count": hpol["positive_count"],
            "zero_count": hpol["zero_count"],
            "strict_flag": int(hpol["min_margin"] > 0 and hpol["zero_count"] == 0),
        },
        {
            "component_id": 1,
            "component_code": 1,
            "margin_value": repl["min_margin"],
            "row_count": repl["row_count"],
            "positive_count": repl["positive_count"],
            "zero_count": repl["zero_count"],
            "strict_flag": int(repl["min_margin"] > 0 and repl["zero_count"] == 0),
        },
        {
            "component_id": 2,
            "component_code": 2,
            "margin_value": lift["min_slack_x1e12"],
            "row_count": lift["row_count"],
            "positive_count": lift["positive_count"],
            "zero_count": lift["zero_count"],
            "strict_flag": int(
                lift["min_slack_x1e12"] > 0 and lift["zero_count"] == 0
            ),
        },
        {
            "component_id": 3,
            "component_code": 3,
            "margin_value": p25_witness["min_support_spread"],
            "row_count": p25_witness["p25_extension_count"],
            "positive_count": p25_witness["p25_extension_count"]
            - p25_boundary["raw_support_equalizer_found"],
            "zero_count": p25_boundary["raw_support_equalizer_found"],
            "strict_flag": int(
                p25_witness["min_support_spread"] > 0
                and p25_boundary["raw_support_equalizer_found"] == 0
            ),
        },
    ]
    obs = {
        "component_count": len(margin_rows),
        "hpol_row_count": hpol["row_count"],
        "hpol_min_margin": hpol["min_margin"],
        "hpol_min_count": hpol["min_margin_count"],
        "hpol_no_positive_annihilator_flag": int(
            hpol["min_margin"] > 0 and hpol["zero_count"] == 0
        ),
        "repl_row_count": repl["row_count"],
        "repl_min_margin": repl["min_margin"],
        "p24_lift_row_count": lift["row_count"],
        "p24_lift_positive_count": lift["positive_count"],
        "p24_lift_min_slack_x1e12": lift["min_slack_x1e12"],
        "p25_extension_count": p25_witness["p25_extension_count"],
        "p25_support_equal_count": p25_boundary["raw_support_equalizer_found"],
        "p25_min_support_spread": p25_witness["min_support_spread"],
        "p25_max_support_spread": p25_witness["max_support_spread"],
        "p25_mult_equal_count": p25_witness["p25_extension_count"],
        "checked_positive_row_total": sum(row["positive_count"] for row in margin_rows),
        "min_component_margin": min(row["margin_value"] for row in margin_rows),
        "all_components_strict_flag": int(
            all(row["strict_flag"] == 1 for row in margin_rows)
        ),
        "support_equalizer_absent_flag": int(
            p25_boundary["raw_support_equalizer_found"] == 0
        ),
        "universal_completion_claim_flag": 0,
    }
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
        "margin_rows": margin_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "gap_report": gap_report,
        "p24_report": p24_report,
        "p25_report": p25_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    margin_table = table_from_rows(MARGIN_COLUMNS, rows["margin_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    gap_report = rows["gap_report"]
    p24_report = rows["p24_report"]
    p25_report = rows["p25_report"]
    checks = {
        "input_certificates_available": (
            gap_report.get("all_checks_pass") is True
            and p24_report.get("all_checks_pass") is True
            and p25_report.get("all_checks_pass") is True
        ),
        "gordan_margin_exact": (
            obs["hpol_row_count"],
            obs["hpol_min_margin"],
            obs["hpol_min_count"],
            obs["hpol_no_positive_annihilator_flag"],
        )
        == (4_903_515, 1, 2, 1),
        "replacement_margin_positive": (
            obs["repl_row_count"],
            obs["repl_min_margin"],
        )
        == (2_831_367, 146),
        "lifted_face_slack_positive": (
            obs["p24_lift_row_count"],
            obs["p24_lift_positive_count"],
            obs["p24_lift_min_slack_x1e12"],
        )
        == (132, 132, 363_262_450_397),
        "pentagon_spread_floor_positive": (
            obs["p25_extension_count"],
            obs["p25_support_equal_count"],
            obs["p25_min_support_spread"],
            obs["p25_max_support_spread"],
            obs["p25_mult_equal_count"],
        )
        == (144, 0, 11_213_312, 633_114_624, 144),
        "horizon_packet_is_strict_on_checked_components": (
            obs["component_count"],
            obs["checked_positive_row_total"],
            obs["min_component_margin"],
            obs["all_components_strict_flag"],
            obs["support_equalizer_absent_flag"],
            obs["universal_completion_claim_flag"],
        )
        == (4, 7_735_158, 1, 1, 1, 0),
        "table_shapes_match_codebooks": (
            tuple(margin_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (4, len(MARGIN_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "finite_horizon_margin_packet",
        "components": [
            {
                "name": "current hpol Gordan margin",
                "margin": obs["hpol_min_margin"],
                "row_count": obs["hpol_row_count"],
                "reading": "strict positive Gordan functional blocks positive annihilator for the current hpol signed-row matrix",
            },
            {
                "name": "replacement carrier margin",
                "margin": obs["repl_min_margin"],
                "row_count": obs["repl_row_count"],
                "reading": "already-certified face-31 replacement carrier remains positive",
            },
            {
                "name": "p24 lifted-face slack",
                "margin": obs["p24_lift_min_slack_x1e12"],
                "row_count": obs["p24_lift_row_count"],
                "reading": "the p23-to-p24 lifted geometric faces keep all support rows strictly positive",
            },
            {
                "name": "p25 pentagon support-spread floor",
                "margin": obs["p25_min_support_spread"],
                "row_count": obs["p25_extension_count"],
                "reading": "lifted pentagon extensions have no raw-support equalizer",
            },
        ],
        "horizon_reading": (
            "Across the checked eta6 packet, support-changing collapse is "
            "blocked by explicit positive integer floors: hpol Gordan margin "
            "1, replacement margin 146, lifted-face slack 363262450397, and "
            "pentagon support-spread floor 11213312."
        ),
        "claim_boundary": {
            "checked_component_count": obs["component_count"],
            "checked_positive_row_total": obs["checked_positive_row_total"],
            "support_equalizer_absent": obs["support_equalizer_absent_flag"],
            "universal_completion_claim": obs["universal_completion_claim_flag"],
        },
        "margin_table_sha256": sha_array(margin_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p26 = {
        "schema": "eta6.p26@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_gap + eta6_p24 + eta6_p25",
            "test": "finite-horizon margin aggregation",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p26.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P26_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The current checked eta6 packet has a strict finite-horizon "
            "margin profile. The hpol Gordan margin is m=1 over 4,903,515 "
            "rows; the replacement carrier margin is 146; the p24 lifted-face "
            "slack is 363262450397 over 132 rows; and the p25 lifted pentagon "
            "support-spread floor is 11213312 over 144 extensions. This "
            "certifies gap protection on the checked packet, not every future "
            "completion."
        ),
        "stage_protocol": {
            "draft": "start from eta6_gap, eta6_p24, and eta6_p25 certified reports",
            "witness": "extract the strict positive floors and checked row counts",
            "coherence": "verify all components are positive and no universal completion claim is made",
            "closure": "certify the finite-horizon margin packet for the checked eta6 stack",
            "emit": "emit compact p26 artifacts and the next recomputation seam",
        },
        "inputs": {
            "gap_report": input_entry(
                GAP_REPORT,
                {
                    "status": gap_report.get("status"),
                    "certificate_sha256": gap_report.get("certificate_sha256"),
                },
            ),
            "p24_report": input_entry(
                P24_REPORT,
                {
                    "status": p24_report.get("status"),
                    "certificate_sha256": p24_report.get("certificate_sha256"),
                },
            ),
            "p24_tables": input_entry(P24_TABLES),
            "p25_report": input_entry(
                P25_REPORT,
                {
                    "status": p25_report.get("status"),
                    "certificate_sha256": p25_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p26": relpath(OUT_DIR / "p26.json"),
            "marg_csv": relpath(OUT_DIR / "marg.csv"),
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
                "current hpol Gordan margin m = 1",
                "positive imported replacement margin 146",
                "positive p24 lifted-face slack 363262450397",
                "positive p25 lifted pentagon support-spread floor 11213312",
                "no p25 raw-support equalizer in the checked lifted pentagon screen",
            ],
            "does_not_certify_because_out_of_scope": [
                "all future replacement completions",
                "new simple-object semantics for the lifted carrier",
                "global automaton closure after repeated geometric lifts",
                "that eta6 is uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "Start p27 by testing whether any p25 best-extension compound "
            "can lower the lifted pentagon support-spread floor without "
            "breaking the p26 finite-horizon margins."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p26.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p26.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p26": p26,
        "marg_csv": csv_text(MARGIN_COLUMNS, rows["margin_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "margin_table": margin_table,
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
    write_json(OUT_DIR / "p26.json", payloads["p26"])
    (OUT_DIR / "marg.csv").write_text(payloads["marg_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        margin_table=payloads["margin_table"],
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
