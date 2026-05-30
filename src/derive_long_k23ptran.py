from __future__ import annotations

import hashlib
import json
from math import gcd
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23ptran"
STATUS = "SECTOR33_K23_PUBLIC_TRANSPORT_POTENTIAL_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23ptran.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23ptran.py"

REPORT_PATHS = {
    "long_k23norm": D20_INVARIANTS / "proof_obligations" / "long_k23norm" / "report.json",
    "long_k23wire": D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "report.json",
    "long_k23wdep": D20_INVARIANTS / "proof_obligations" / "long_k23wdep" / "report.json",
    "long_k23audit": D20_INVARIANTS / "proof_obligations" / "long_k23audit" / "report.json",
    "long_k23vwork": D20_INVARIANTS / "proof_obligations" / "long_k23vwork" / "report.json",
    "long_k23crypt": D20_INVARIANTS / "proof_obligations" / "long_k23crypt" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23norm": "SECTOR33_K23_MLKEM512_NORMALIZATION_CERTIFIED",
    "long_k23wire": "SECTOR33_K23_COMPACT_WIRE_MAP_CERTIFIED",
    "long_k23wdep": "SECTOR33_K23_WIRE_DEPENDENCY_DECISION_CERTIFIED",
    "long_k23audit": "SECTOR33_K23_LOCAL_AUDIT_COST_CERTIFIED",
    "long_k23vwork": "SECTOR33_K23_VERIFIER_WORKLOAD_BINDING_CERTIFIED",
    "long_k23crypt": "SECTOR33_K23_CRYPTOLOGIC_POTENTIAL_FRONTIER_CERTIFIED",
}

PROFILE_TEXT_HASH = "72f3465bd872a7bfb8e4baeb9427f50fdc1e3fc7fe62c6f1c0477dd393c23626"
GATE_TEXT_HASH = "fdd55f4ca853d321cda2c96b0303b2200c01a7af8fc0a0e9c8c4283d0c87bcf0"
OBS_TEXT_HASH = "0c985b38565adb0b90d43ab763af7d06686c90f425a8af7826a630483957bfb6"
MATRIX_SHA256 = "e1dd59f72be325044169e201bcb3a74350becc8cf57aafcdaff78b08912127a3"

PROFILE_COLUMNS = [
    "profile_id",
    "profile_code",
    "source_code",
    "public_transport_axis_flag",
    "shared_table_required_flag",
    "wire_equivalence_required_flag",
    "self_contained_flag",
    "transport_bytes",
    "baseline_public_exchange_bytes",
    "delta_vs_baseline_bytes",
    "improvement_num",
    "improvement_den",
    "objective_improvement_potential_flag",
    "current_public_claim_ready_flag",
    "external_improvement_claim_flag",
]
GATE_COLUMNS = [
    "gate_id",
    "gate_code",
    "profile_id",
    "required_for_public_claim_flag",
    "currently_satisfied_flag",
    "blocking_flag",
    "claim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "profile_row_count",
    "public_transport_profile_count",
    "shared_table_profile_count",
    "self_contained_profile_count",
    "objective_improvement_potential_count",
    "current_public_claim_ready_count",
    "external_improvement_claim_count",
    "baseline_public_exchange_bytes",
    "shared_table_wire_bytes",
    "current_self_contained_bytes",
    "local_audit_total_bytes",
    "digest_surface_total_bytes",
    "shared_delta_vs_baseline_bytes",
    "current_delta_vs_baseline_bytes",
    "shared_improvement_num",
    "shared_improvement_den",
    "current_improvement_num",
    "current_improvement_den",
    "conditional_saved_vs_baseline_bytes",
    "self_contained_penalty_bytes",
    "wire_row_count",
    "wire_row_bytes",
    "wire_total_bytes",
    "table_index_dependency_count",
    "wire_equivalence_claim_count",
    "public_transport_claim_count",
    "external_efficiency_path_demoted_count",
    "local_bytes_per_game_num",
    "local_bytes_per_game_den",
    "gate_row_count",
    "blocking_gate_count",
    "required_gate_count",
    "satisfied_gate_count",
    "claim_gate_count",
    "cryptologic_frontier_flag",
    "ready_for_external_claim_count",
    "public_transport_potential_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["profile_table", "gate_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def reduce_ratio(numerator: int, denominator: int) -> tuple[int, int]:
    divisor = gcd(abs(numerator), abs(denominator))
    return numerator // divisor, denominator // divisor


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORT_PATHS.items()}
    summaries = {name: summary(report) for name, report in reports.items()}
    certified = {name: is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS}

    norm = summaries["long_k23norm"]
    wire = summaries["long_k23wire"]
    wdep = summaries["long_k23wdep"]
    audit = summaries["long_k23audit"]
    vwork = summaries["long_k23vwork"]
    crypt = summaries["long_k23crypt"]

    baseline = int(norm.get("baseline_public_exchange_bytes", -1))
    shared_wire = int(wire.get("wire_total_bytes", -1))
    self_contained = int(wdep.get("current_model_self_contained_bytes", -1))
    local_audit = int(vwork.get("local_audit_total_bytes", -1))
    digest_surface = int(vwork.get("digest_surface_total_bytes", -1))
    shared_delta = shared_wire - baseline
    current_delta = self_contained - baseline
    shared_saved = max(0, baseline - shared_wire)
    current_saved = max(0, baseline - self_contained)
    shared_ratio = reduce_ratio(shared_saved, baseline)
    current_ratio = reduce_ratio(current_saved, baseline)

    profile_rows = [
        {
            "profile_id": 0,
            "profile_code": 0,
            "source_code": 0,
            "public_transport_axis_flag": 1,
            "shared_table_required_flag": 0,
            "wire_equivalence_required_flag": 0,
            "self_contained_flag": 1,
            "transport_bytes": self_contained,
            "baseline_public_exchange_bytes": baseline,
            "delta_vs_baseline_bytes": current_delta,
            "improvement_num": current_ratio[0],
            "improvement_den": current_ratio[1],
            "objective_improvement_potential_flag": 0,
            "current_public_claim_ready_flag": 0,
            "external_improvement_claim_flag": 0,
        },
        {
            "profile_id": 1,
            "profile_code": 1,
            "source_code": 1,
            "public_transport_axis_flag": 1,
            "shared_table_required_flag": 1,
            "wire_equivalence_required_flag": 1,
            "self_contained_flag": 0,
            "transport_bytes": shared_wire,
            "baseline_public_exchange_bytes": baseline,
            "delta_vs_baseline_bytes": shared_delta,
            "improvement_num": shared_ratio[0],
            "improvement_den": shared_ratio[1],
            "objective_improvement_potential_flag": 1,
            "current_public_claim_ready_flag": 0,
            "external_improvement_claim_flag": 0,
        },
        {
            "profile_id": 2,
            "profile_code": 2,
            "source_code": 2,
            "public_transport_axis_flag": 0,
            "shared_table_required_flag": 1,
            "wire_equivalence_required_flag": 0,
            "self_contained_flag": 0,
            "transport_bytes": local_audit,
            "baseline_public_exchange_bytes": baseline,
            "delta_vs_baseline_bytes": local_audit - baseline,
            "improvement_num": shared_ratio[0],
            "improvement_den": shared_ratio[1],
            "objective_improvement_potential_flag": 0,
            "current_public_claim_ready_flag": 0,
            "external_improvement_claim_flag": 0,
        },
    ]
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "profile_id": 1, "required_for_public_claim_flag": 1, "currently_satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "profile_id": 1, "required_for_public_claim_flag": 1, "currently_satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "profile_id": 1, "required_for_public_claim_flag": 1, "currently_satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "profile_id": 1, "required_for_public_claim_flag": 1, "currently_satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "profile_id": 1, "required_for_public_claim_flag": 1, "currently_satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(certified.values()),
        "profile_row_count": len(profile_rows),
        "public_transport_profile_count": sum(row["public_transport_axis_flag"] for row in profile_rows),
        "shared_table_profile_count": sum(row["shared_table_required_flag"] for row in profile_rows),
        "self_contained_profile_count": sum(row["self_contained_flag"] for row in profile_rows),
        "objective_improvement_potential_count": sum(row["objective_improvement_potential_flag"] for row in profile_rows),
        "current_public_claim_ready_count": sum(row["current_public_claim_ready_flag"] for row in profile_rows),
        "external_improvement_claim_count": sum(row["external_improvement_claim_flag"] for row in profile_rows),
        "baseline_public_exchange_bytes": baseline,
        "shared_table_wire_bytes": shared_wire,
        "current_self_contained_bytes": self_contained,
        "local_audit_total_bytes": local_audit,
        "digest_surface_total_bytes": digest_surface,
        "shared_delta_vs_baseline_bytes": shared_delta,
        "current_delta_vs_baseline_bytes": current_delta,
        "shared_improvement_num": shared_ratio[0],
        "shared_improvement_den": shared_ratio[1],
        "current_improvement_num": current_ratio[0],
        "current_improvement_den": current_ratio[1],
        "conditional_saved_vs_baseline_bytes": shared_saved,
        "self_contained_penalty_bytes": max(0, self_contained - baseline),
        "wire_row_count": int(wire.get("wire_row_count", -1)),
        "wire_row_bytes": int(wire.get("wire_row_bytes", -1)),
        "wire_total_bytes": shared_wire,
        "table_index_dependency_count": int(wire.get("table_index_dependency_count", -1)),
        "wire_equivalence_claim_count": int(wire.get("wire_equivalence_claim_count", -1)),
        "public_transport_claim_count": int(vwork.get("public_transport_claim_count", -1)),
        "external_efficiency_path_demoted_count": int(wdep.get("external_efficiency_path_demoted_count", -1)),
        "local_bytes_per_game_num": int(vwork.get("local_bytes_per_game_num", -1)),
        "local_bytes_per_game_den": int(vwork.get("local_bytes_per_game_den", -1)),
        "gate_row_count": len(gate_rows),
        "blocking_gate_count": sum(row["blocking_flag"] for row in gate_rows),
        "required_gate_count": sum(row["required_for_public_claim_flag"] for row in gate_rows),
        "satisfied_gate_count": sum(row["currently_satisfied_flag"] for row in gate_rows),
        "claim_gate_count": sum(row["claim_flag"] for row in gate_rows),
        "cryptologic_frontier_flag": int(crypt.get("cryptologic_frontier_flag", -1)),
        "ready_for_external_claim_count": int(crypt.get("ready_for_external_claim_count", -1)),
        "public_transport_potential_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    profile_table = table_from_rows(PROFILE_COLUMNS, profile_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "profile_table": profile_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "profile_rows": profile_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "profile_table": profile_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "profile_text_hash": hashlib.sha256(digest_text(PROFILE_COLUMNS, profile_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 6,
        "profile_shape_matches": (
            obs["profile_row_count"],
            obs["public_transport_profile_count"],
            obs["shared_table_profile_count"],
            obs["self_contained_profile_count"],
            obs["objective_improvement_potential_count"],
            obs["current_public_claim_ready_count"],
            obs["external_improvement_claim_count"],
        )
        == (3, 2, 2, 1, 1, 0, 0),
        "objective_delta_profile_matches": (
            obs["baseline_public_exchange_bytes"],
            obs["shared_table_wire_bytes"],
            obs["current_self_contained_bytes"],
            obs["shared_delta_vs_baseline_bytes"],
            obs["current_delta_vs_baseline_bytes"],
            obs["shared_improvement_num"],
            obs["shared_improvement_den"],
            obs["current_improvement_num"],
            obs["current_improvement_den"],
            obs["conditional_saved_vs_baseline_bytes"],
            obs["self_contained_penalty_bytes"],
        )
        == (1568, 224, 5376, -1344, 3808, 6, 7, 0, 1, 1344, 3808),
        "wire_dependency_profile_matches": (
            obs["wire_row_count"],
            obs["wire_row_bytes"],
            obs["wire_total_bytes"],
            obs["table_index_dependency_count"],
            obs["wire_equivalence_claim_count"],
            obs["public_transport_claim_count"],
            obs["external_efficiency_path_demoted_count"],
        )
        == (56, 4, 224, 56, 0, 0, 1),
        "local_audit_separation_matches": (
            obs["local_audit_total_bytes"],
            obs["digest_surface_total_bytes"],
            obs["local_bytes_per_game_num"],
            obs["local_bytes_per_game_den"],
        )
        == (224, 5376, 2, 3),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["blocking_gate_count"],
            obs["required_gate_count"],
            obs["satisfied_gate_count"],
            obs["claim_gate_count"],
        )
        == (5, 5, 5, 0, 0),
        "frontier_flags_match": (
            obs["cryptologic_frontier_flag"],
            obs["ready_for_external_claim_count"],
            obs["public_transport_potential_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_public_transport_potential",
        "profile_code_map": {
            "0": "current_self_contained_public_surface",
            "1": "shared_table_public_candidate_surface",
            "2": "local_verifier_audit_surface_not_public_transport",
        },
        "gate_code_map": {
            "0": "public_shared_table_distribution",
            "1": "wire_equivalence_proof",
            "2": "self_contained_public_compression",
            "3": "external_runtime_or_size_benchmark",
            "4": "interop_and_side_channel_profile",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the objective public-transport deltas and the conditional shared-table improvement potential while keeping public improvement claims blocked.",
    }
    seam_payload = {
        "schema": "long.k23ptran.seam@1",
        "status": STATUS,
        "claim": "The K23 public-transport surface has one objective conditional improvement candidate, but no current public improvement claim.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name, path in REPORT_PATHS.items()
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23ptran.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23ptran certifies objective public-transport potential and current blocking gates.",
        "stage_protocol": {
            "draft": "read normalization, wire-map, dependency, audit, workload, and cryptologic-frontier reports",
            "witness": "emit public-transport profiles, claim gates, observables, and numeric tables",
            "coherence": "check public byte deltas, conditional improvement ratio, self-contained penalty, dependency gates, and nonclaims",
            "closure": "certify objective transport potential without converting it into a public improvement claim",
            "emit": "write long_k23ptran artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "profile_rows_csv": relpath(OUT_DIR / "profile_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23ptran_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the current self-contained public surface is 5376 bytes against a 1568-byte baseline, so it is not an improvement",
                "the shared-table candidate surface is 224 bytes against a 1568-byte baseline",
                "the shared-table candidate has conditional byte savings 1344/1568 = 6/7",
                "the shared-table candidate has one objective improvement-potential row",
                "five public-claim gates remain blocking",
            ],
            "does_not_certify": [
                "current public transport improvement",
                "wire-format equivalence",
                "shared-table public distribution",
                "self-contained public compression",
                "external runtime superiority",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Attack the highest-value blocker: construct a public shared-table distribution/equivalence certificate or a self-contained compression certificate.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23ptran.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23ptran.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "profile_csv": csv_text(PROFILE_COLUMNS, rows["profile_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "profile_table": rows["profile_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "profile_text_sha256": rows["profile_text_hash"],
            "gate_text_sha256": rows["gate_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
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
    (OUT_DIR / "profile_rows.csv").write_text(payloads["profile_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        profile_table=payloads["profile_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23ptran_matrices.npz", **payloads["matrix_payload"])
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
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
