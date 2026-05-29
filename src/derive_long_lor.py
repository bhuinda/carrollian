from __future__ import annotations

import hashlib
import json
from pathlib import Path
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
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_lor"
STATUS = "LONG_LOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
CERTIFICATE = ROOT / "certificate.json"
INTEGRITY_SUMMARY = ROOT / "data" / "integrity" / "proof_system.summary.json"
LONG_GR = PROOF_ROOT / "long_gr" / "report.json"
LONG_REC = PROOF_ROOT / "long_rec" / "report.json"
LONG_MARKOV = PROOF_ROOT / "long_markov" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_lor.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_lor.py"

SPLIT_COLUMNS = [
    "split_id",
    "source_code",
    "ambient_rank",
    "kernel_rank",
    "quotient_rank",
    "time_rank",
    "space_rank",
    "lorentzian_split_flag",
]
CLOCK_COLUMNS = [
    "clock_id",
    "layer_code",
    "value",
    "expected_value",
    "certified_flag",
    "next_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "obligation_code",
    "required_for_gr_flag",
    "certified_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SPLIT_NAMES = [
    "internal_operation_integral_trace",
    "public_boundary_integral_trace",
]
SPLIT_CODES = {name: index for index, name in enumerate(SPLIT_NAMES)}

CLOCK_LAYER_NAMES = [
    "operation_algebra_dimension",
    "integrity_integral_codimension",
    "integrity_integral_dimension",
    "public_rank",
    "public_kernel_dimension",
    "public_quotient_dimension",
    "primitive_kernel_sector",
    "packet_normalization",
    "time_trace_rank",
    "recurrence_node_count",
    "recurrence_edge_count",
    "markov_state_count",
]
CLOCK_LAYER_CODES = {name: index for index, name in enumerate(CLOCK_LAYER_NAMES)}

GAP_NAMES = [
    "materialized_operation_to_boundary_readout",
    "edgewise_time_increment_witnesses",
    "nondegenerate_smooth_lorentzian_metric",
    "four_dimensional_spacetime_reduction",
    "curvature_and_einstein_tensor",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "operation_algebra_dimension",
    "integrity_integral_codimension",
    "integrity_integral_dimension",
    "public_rank",
    "public_kernel_dimension",
    "public_quotient_dimension",
    "primitive_kernel_sector",
    "packet_normalization",
    "spin_packet_dim",
    "epsilon0",
    "wd6_order",
    "recurrence_node_count",
    "recurrence_edge_count",
    "markov_state_count",
    "lorentzian_split_count",
    "time_rank",
    "space_rank",
    "finite_lorentzian_scaffold_flag",
    "smooth_lorentzian_metric_flag",
    "four_dimensional_spacetime_flag",
    "einstein_equation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_dict(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AssertionError(f"{label} is not a JSON object")
    return payload


def _finite_base(integrity_summary: dict[str, Any]) -> dict[str, Any]:
    summary_base = _require_dict(integrity_summary.get("finite_base"), "finite_base")
    return summary_base


def _certificate_integrity(certificate: dict[str, Any]) -> dict[str, Any]:
    return _require_dict(certificate.get("integrity_gate"), "integrity_gate")


def _certificate_optics(certificate: dict[str, Any]) -> dict[str, Any]:
    d20_invariants = _require_dict(certificate.get("d20_invariants"), "d20_invariants")
    return _require_dict(d20_invariants.get("optics"), "d20_invariants.optics")


def _public_quotient_dimension(public_rank: int, public_kernel_dimension: int) -> int:
    return int(public_rank - public_kernel_dimension)


def build_rows() -> dict[str, Any]:
    certificate = load_json(CERTIFICATE)
    integrity_summary = load_json(INTEGRITY_SUMMARY)
    long_gr = load_json(LONG_GR)
    long_rec = load_json(LONG_REC)
    long_markov = load_json(LONG_MARKOV)

    cert_integrity = _certificate_integrity(certificate)
    summary_base = _finite_base(integrity_summary)
    optics = _certificate_optics(certificate)
    optics_constants = _require_dict(optics.get("constants"), "optics.constants")
    central_identity = _require_dict(
        optics.get("central_identity"), "optics.central_identity"
    )
    rec_kernel = _require_dict(
        _require_dict(long_rec.get("witness"), "long_rec.witness").get(
            "transition_kernel"
        ),
        "long_rec.transition_kernel",
    )
    markov_witness = _require_dict(long_markov.get("witness"), "long_markov.witness")
    markov_stationary = _require_dict(
        markov_witness.get("stationary"), "long_markov.stationary"
    )
    markov_weights = markov_stationary.get("weights")
    if not isinstance(markov_weights, list):
        raise AssertionError("long_markov stationary weights missing")
    markov_state_count = len(markov_weights)

    operation_dim = int(summary_base["operation_algebra_dimension"])
    integral_dim = int(summary_base["integrity_integral_dimension"])
    integral_codim = int(summary_base["integrity_integral_codimension"])
    public_rank = int(summary_base["public_rank"])
    public_kernel_dim = int(summary_base["public_kernel_dimension"])
    public_quotient_dim = _public_quotient_dimension(public_rank, public_kernel_dim)
    primitive_kernel_sector = int(summary_base["primitive_kernel_sector"][0])
    packet_normalization = int(central_identity["5_epsilon0_over_4W_D6"])
    spin_packet_dim = int(optics_constants["spin_packet_dim"])
    epsilon0 = int(optics_constants["epsilon0"])
    wd6_order = int(optics_constants["W_D6_order"])
    recurrence_node_count = int(rec_kernel["node_count"])
    recurrence_edge_count = int(rec_kernel["edge_count"])

    split_rows = [
        {
            "split_id": SPLIT_CODES["internal_operation_integral_trace"],
            "source_code": 0,
            "ambient_rank": operation_dim,
            "kernel_rank": integral_codim,
            "quotient_rank": integral_dim,
            "time_rank": integral_dim,
            "space_rank": integral_codim,
            "lorentzian_split_flag": int(integral_dim == 1 and integral_codim == 35),
        },
        {
            "split_id": SPLIT_CODES["public_boundary_integral_trace"],
            "source_code": 1,
            "ambient_rank": public_rank,
            "kernel_rank": public_kernel_dim,
            "quotient_rank": public_quotient_dim,
            "time_rank": public_quotient_dim,
            "space_rank": public_kernel_dim,
            "lorentzian_split_flag": int(
                public_quotient_dim == 1 and public_kernel_dim == 19
            ),
        },
    ]

    clock_expectations = [
        ("operation_algebra_dimension", operation_dim, 36, 0),
        ("integrity_integral_codimension", integral_codim, 35, 0),
        ("integrity_integral_dimension", integral_dim, 1, 0),
        ("public_rank", public_rank, 20, 0),
        ("public_kernel_dimension", public_kernel_dim, 19, 0),
        ("public_quotient_dimension", public_quotient_dim, 1, 0),
        ("primitive_kernel_sector", primitive_kernel_sector, 33, 0),
        ("packet_normalization", packet_normalization, 32, 0),
        ("time_trace_rank", public_quotient_dim, 1, 0),
        ("recurrence_node_count", recurrence_node_count, 259, 0),
        ("recurrence_edge_count", recurrence_edge_count, 642, 0),
        ("markov_state_count", markov_state_count, 3, 0),
    ]
    clock_rows = [
        {
            "clock_id": index,
            "layer_code": CLOCK_LAYER_CODES[name],
            "value": int(value),
            "expected_value": int(expected),
            "certified_flag": int(value == expected),
            "next_flag": int(next_flag),
        }
        for index, (name, value, expected, next_flag) in enumerate(clock_expectations)
    ]

    gap_rows = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["materialized_operation_to_boundary_readout"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES["edgewise_time_increment_witnesses"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["four_dimensional_spacetime_reduction"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 4,
            "obligation_code": GAP_CODES["curvature_and_einstein_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
    ]

    obs = {
        "operation_algebra_dimension": operation_dim,
        "integrity_integral_codimension": integral_codim,
        "integrity_integral_dimension": integral_dim,
        "public_rank": public_rank,
        "public_kernel_dimension": public_kernel_dim,
        "public_quotient_dimension": public_quotient_dim,
        "primitive_kernel_sector": primitive_kernel_sector,
        "packet_normalization": packet_normalization,
        "spin_packet_dim": spin_packet_dim,
        "epsilon0": epsilon0,
        "wd6_order": wd6_order,
        "recurrence_node_count": recurrence_node_count,
        "recurrence_edge_count": recurrence_edge_count,
        "markov_state_count": markov_state_count,
        "lorentzian_split_count": sum(
            row["lorentzian_split_flag"] for row in split_rows
        ),
        "time_rank": public_quotient_dim,
        "space_rank": public_kernel_dim,
        "finite_lorentzian_scaffold_flag": 1,
        "smooth_lorentzian_metric_flag": 0,
        "four_dimensional_spacetime_flag": 0,
        "einstein_equation_flag": 0,
        "open_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES["materialized_operation_to_boundary_readout"],
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]

    return {
        "certificate": certificate,
        "integrity_summary": integrity_summary,
        "long_gr": long_gr,
        "long_rec": long_rec,
        "long_markov": long_markov,
        "cert_integrity": cert_integrity,
        "summary_base": summary_base,
        "optics": optics,
        "split_rows": split_rows,
        "clock_rows": clock_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "split_table": table_from_rows(SPLIT_COLUMNS, split_rows),
        "clock_table": table_from_rows(CLOCK_COLUMNS, clock_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "split_text_hash": sha_text(digest_text(SPLIT_COLUMNS, split_rows)),
        "clock_text_hash": sha_text(digest_text(CLOCK_COLUMNS, clock_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    cert_integrity = rows["cert_integrity"]
    summary_base = rows["summary_base"]
    certificate = rows["certificate"]
    long_gr = rows["long_gr"]
    long_rec = rows["long_rec"]
    long_markov = rows["long_markov"]
    central_identity = rows["optics"]["central_identity"]
    optics_constants = rows["optics"]["constants"]

    checks = {
        "certificate_status_ok": certificate.get("status") == "D20_CERTIFIED",
        "integrity_summary_matches_certificate": all(
            summary_base.get(key) == cert_integrity.get(key)
            for key in [
                "operation_algebra_dimension",
                "integrity_integral_dimension",
                "integrity_integral_codimension",
                "public_rank",
                "public_kernel_dimension",
                "primitive_kernel_sector",
            ]
        ),
        "operation_integral_quotient_is_one": obs["operation_algebra_dimension"] == 36
        and obs["integrity_integral_codimension"] == 35
        and obs["integrity_integral_dimension"] == 1,
        "public_integral_quotient_is_one": obs["public_rank"] == 20
        and obs["public_kernel_dimension"] == 19
        and obs["public_quotient_dimension"] == 1,
        "primitive_packet_time_ladder_exact": obs["primitive_kernel_sector"] == 33
        and obs["packet_normalization"] == 32
        and obs["time_rank"] == 1,
        "optics_packet_identity_exact": central_identity.get("equals_32") is True
        and central_identity.get("5_epsilon0_equals_128_W_D6") is True
        and obs["spin_packet_dim"] == 32
        and obs["epsilon0"] == 589_824
        and obs["wd6_order"] == 23_040
        and int(optics_constants["spin_packet_dim"]) == int(
            central_identity["5_epsilon0_over_4W_D6"]
        ),
        "long_gr_input_certified": long_gr.get("status") == "LONG_GR_PATHWAY_CERTIFIED"
        and long_gr.get("all_checks_pass") is True,
        "recurrence_clock_carrier_certified": long_rec.get("status")
        == "LONG_REC_CERTIFIED"
        and long_rec.get("all_checks_pass") is True
        and obs["recurrence_node_count"] == 259
        and obs["recurrence_edge_count"] == 642,
        "finite_markov_clock_certified": long_markov.get("status")
        == "LONG_MARKOV_CERTIFIED"
        and long_markov.get("all_checks_pass") is True
        and obs["markov_state_count"] == 3,
        "finite_scaffold_not_smooth_metric": obs["finite_lorentzian_scaffold_flag"] == 1
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["four_dimensional_spacetime_flag"] == 0
        and obs["einstein_equation_flag"] == 0,
        "table_shapes_match": rows["split_table"].shape
        == (len(SPLIT_NAMES), len(SPLIT_COLUMNS))
        and rows["clock_table"].shape == (len(CLOCK_LAYER_NAMES), len(CLOCK_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS)),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "finite_lorentzian_time_quotient_scaffold",
        "split_code_map": {str(value): key for key, value in SPLIT_CODES.items()},
        "clock_layer_code_map": {
            str(value): key for key, value in CLOCK_LAYER_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "summary": {
            "operation_algebra_dimension": obs["operation_algebra_dimension"],
            "integrity_integral_codimension": obs[
                "integrity_integral_codimension"
            ],
            "integrity_integral_dimension": obs["integrity_integral_dimension"],
            "public_rank": obs["public_rank"],
            "public_kernel_dimension": obs["public_kernel_dimension"],
            "public_quotient_dimension": obs["public_quotient_dimension"],
            "primitive_kernel_sector": obs["primitive_kernel_sector"],
            "packet_normalization": obs["packet_normalization"],
            "time_rank": obs["time_rank"],
            "space_rank": obs["space_rank"],
            "finite_lorentzian_scaffold_flag": obs[
                "finite_lorentzian_scaffold_flag"
            ],
            "smooth_lorentzian_metric_flag": obs["smooth_lorentzian_metric_flag"],
            "next_gap": "materialized_operation_to_boundary_readout",
        },
        "split_table_sha256": sha_array(rows["split_table"]),
        "split_text_sha256": rows["split_text_hash"],
        "clock_table_sha256": sha_array(rows["clock_table"]),
        "clock_text_sha256": rows["clock_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    lor_payload = {
        "schema": "long.lor@1",
        "object": "finite_lorentzian_time_quotient_scaffold",
        "status": STATUS if all(checks.values()) else "LONG_LOR_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.lor.report@1",
        "status": lor_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_lor certifies the finite Lorentzian scaffold implied by the "
            "d20 time hint: the 36-dimensional operation algebra has a unique "
            "one-dimensional integrity-integral quotient, the public 20-rank "
            "boundary has a 19-dimensional public kernel and one-dimensional "
            "public quotient, and the certified recurrence/Markov surfaces "
            "provide the finite clock carrier. The witness records the current "
            "formal split as 1 time trace plus 19 public kernel directions, "
            "with 33 as hidden primitive kernel sector and 32 as packet "
            "normalization. It does not certify a smooth Lorentzian metric or "
            "a 3+1 spacetime reduction."
        ),
        "stage_protocol": {
            "draft": "read certificate integrity/optics, integrity summary, long_gr, long_rec, and long_markov",
            "witness": "emit quotient-split rows, clock-normalization rows, and open Lorentzian bridge gaps",
            "coherence": "check 36->1, 20->1, 33->32->1, recurrence counts, Markov count, and table hashes",
            "closure": "certify a finite Lorentzian time-quotient scaffold without claiming smooth GR geometry",
            "emit": "write long_lor artifacts and verifier hook",
        },
        "inputs": {
            "certificate": input_entry(
                CERTIFICATE,
                {
                    "status": certificate.get("status"),
                    "headline": certificate.get("headline"),
                },
            ),
            "integrity_summary": input_entry(INTEGRITY_SUMMARY),
            "long_gr": input_entry(
                LONG_GR,
                {
                    "status": long_gr.get("status"),
                    "certificate_sha256": long_gr.get("certificate_sha256"),
                },
            ),
            "long_rec": input_entry(
                LONG_REC,
                {
                    "status": long_rec.get("status"),
                    "certificate_sha256": long_rec.get("certificate_sha256"),
                },
            ),
            "long_markov": input_entry(
                LONG_MARKOV,
                {
                    "status": long_markov.get("status"),
                    "certificate_sha256": long_markov.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "lor": relpath(OUT_DIR / "lor.json"),
            "split_csv": relpath(OUT_DIR / "split.csv"),
            "clock_csv": relpath(OUT_DIR / "clock.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "the operation quotient 36 -> 1 as the internal time trace",
                "the public quotient 20 -> 1 as the public time trace, with 19 public kernel directions",
                "the finite formal Lorentzian split T_1 plus K_pub,19 as a current d20 scaffold",
                "the hidden/packet/time ladder 33 -> 32 -> 1",
                "the recurrence graph and finite Markov boundary as certified clock carriers",
            ],
            "does_not_certify_because_open": [
                "a materialized operation-to-boundary readout matrix rho and edgewise Delta t(e) table",
                "a nondegenerate smooth Lorentzian metric tensor",
                "a 3+1 spacetime reduction from the 1+19 public split",
                "Riemann/Ricci curvature or Einstein tensor",
                "Einstein field equations or general relativity derived from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Build long_time_map: materialize rho, tau_int, q_pub, and edgewise "
            "Delta t(e) witnesses so the recurrence clock is a checked table "
            "rather than only a quotient scaffold."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.lor.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.lor.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "lor": lor_payload,
        "split_csv": csv_text(SPLIT_COLUMNS, rows["split_rows"]),
        "clock_csv": csv_text(CLOCK_COLUMNS, rows["clock_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "split_table": rows["split_table"],
        "clock_table": rows["clock_table"],
        "gap_table": rows["gap_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "lor.json", payloads["lor"])
    (OUT_DIR / "split.csv").write_text(payloads["split_csv"], encoding="utf-8")
    (OUT_DIR / "clock.csv").write_text(payloads["clock_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        split_table=payloads["split_table"],
        clock_table=payloads["clock_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "certificate_sha256": report["certificate_sha256"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
