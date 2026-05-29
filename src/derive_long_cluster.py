from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
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


THEOREM_ID = "long_cluster"
STATUS = "LONG_CLUSTER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_cluster.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_cluster.py"

CLUSTER_TEXT_HASH = "e4da4f2ec3c0e30298920d47f1e1d27f1d31e5053f67118f7cfbd9baa7875aa7"
SEAM_TEXT_HASH = "2af793a59e0fe9f0053f375a9c323c1ad8e0967b6ca37b755e9988fc791256f0"
OBS_TEXT_HASH = "8448b61dd6557c591b39ef77a8ba7259616e5ec1552f5eb59d3c58c32b6dee98"

FOCUSED_MANIFESTS = {
    "long_anom": PROOF_ROOT / "long_anom" / "manifest.json",
    "long_auto": PROOF_ROOT / "long_auto" / "manifest.json",
    "long_binc": PROOF_ROOT / "long_binc" / "manifest.json",
    "long_c2uf": PROOF_ROOT / "long_c2uf" / "manifest.json",
    "long_h16": PROOF_ROOT / "long_h16" / "manifest.json",
    "long_inv_exhaust": PROOF_ROOT / "long_inv_exhaust" / "manifest.json",
    "long_mat": PROOF_ROOT / "long_mat" / "manifest.json",
    "long_measure": PROOF_ROOT / "long_measure" / "manifest.json",
    "long_orac": PROOF_ROOT / "long_orac" / "manifest.json",
    "long_paths": PROOF_ROOT / "long_paths" / "manifest.json",
    "long_pobj": PROOF_ROOT / "long_pobj" / "manifest.json",
    "long_psec": PROOF_ROOT / "long_psec" / "manifest.json",
}

FOCUSED_REPORTS = {
    name: PROOF_ROOT / name / "report.json"
    for name in [
        "long_anom",
        "long_auto",
        "long_binc",
        "long_c2uf",
        "long_h16",
        "long_inv_exhaust",
        "long_mat",
        "long_measure",
        "long_orac",
        "long_paths",
        "long_pobj",
        "long_psec",
    ]
}

CLUSTERS = [
    (
        0,
        "packet_matrix_bridge",
        [
            "packet",
            "packet239",
            "matrix",
            "mat_2",
            "snf",
            "doublet",
            "restriction",
            "bridge",
            "operator map",
            "kernel dimension",
        ],
    ),
    (
        1,
        "sector_anomaly_ward",
        [
            "anomaly",
            "ward",
            "sector",
            "gamma",
            "clock",
            "counterterm",
            "bms",
            "carroll",
            "flux",
            "c2",
        ],
    ),
    (
        2,
        "automorphic_fourier_string",
        [
            "automorphic",
            "fourier",
            "amplitude",
            "virasoro",
            "loop297",
            "scattering",
            "residue",
            "mode",
            "trace",
            "string",
        ],
    ),
    (
        3,
        "profunctor_path_measure",
        [
            "profunctor",
            "horizon",
            "path",
            "measure",
            "probability",
            "sheaf",
            "martingale",
            "raw",
            "owner",
            "zeta",
            "tensor",
        ],
    ),
    (
        4,
        "c985_coherence",
        [
            "c985",
            "associator",
            "pentagon",
            "zigzag",
            "multifusion",
            "fusion",
            "unit",
            "coherence",
        ],
    ),
    (
        5,
        "quotient_support_orbit",
        [
            "quotient",
            "support",
            "orbit",
            "coorient",
            "terminal",
            "selector",
            "relation",
            "source",
            "line",
            "fiber",
        ],
    ),
    (
        6,
        "exceptional_geometry_bridge",
        [
            "e8",
            "golay",
            "leech",
            "hydrogen",
            "black hole",
            "moonshine",
            "spin",
            "dodecad",
            "sixj",
            "cartan",
            "root",
        ],
    ),
]

CLUSTER_NAMES = {code: name for code, name, _ in CLUSTERS}
CLUSTER_COLUMNS = [
    "cluster_id",
    "report_count",
    "certified_count",
    "consumed_certified_count",
    "unconsumed_certified_count",
    "multi_theme_unconsumed_count",
    "obstruction_count",
    "bridge_gap_count",
    "reopen_flag",
    "top_priority_score",
]
SEAM_COLUMNS = [
    "seam_id",
    "report_code",
    "primary_cluster_code",
    "theme_count",
    "priority_score",
    "obstruction_flag",
    "bridge_gap_flag",
    "proposed_next_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "theorem_report_count",
    "certified_report_count",
    "focused_consumed_report_count",
    "unconsumed_certified_report_count",
    "cluster_count",
    "reopened_cluster_count",
    "seam_candidate_count",
    "multi_theme_unconsumed_count",
    "obstruction_candidate_count",
    "bridge_gap_candidate_count",
    "top_cluster_code",
    "top_seam_report_code",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def normalize_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9_+.-]+", " ", str(value).lower())


def report_text(report_id: str, report: dict[str, Any]) -> str:
    pieces: list[str] = [
        report_id,
        str(report.get("schema", "")),
        str(report.get("status", "")),
        str(report.get("claim", "")),
        str(report.get("theorem", "")),
        str(report.get("theorem_interpretation", "")),
        json.dumps(report.get("closure_boundary", {}), sort_keys=True),
        " ".join(sorted(str(key) for key in report.get("checks", {}).keys())),
    ]
    derived = report.get("derived", {})
    if isinstance(derived, dict):
        pieces.append(" ".join(sorted(str(key) for key in derived.keys())))
        for key in sorted(derived)[:12]:
            value = derived[key]
            if isinstance(value, (dict, list, str, int, float, bool)):
                pieces.append(json.dumps(value, sort_keys=True)[:2000])
    return normalize_text(" ".join(pieces))


def certified(report: dict[str, Any]) -> int:
    status = str(report.get("status", ""))
    return int(
        report.get("all_checks_pass") is True
        and "FAIL" not in status
        and "PROVISIONAL" not in status
    )


def focused_consumed_paths() -> set[str]:
    consumed: set[str] = set()
    for path in FOCUSED_MANIFESTS.values():
        if not path.exists():
            continue
        manifest = load_json(path)
        inputs = manifest.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        for entry in inputs.values():
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                consumed.add(entry["path"])
    return consumed


def score_clusters(text: str) -> dict[int, int]:
    scores: dict[int, int] = {}
    for code, _name, keywords in CLUSTERS:
        score = 0
        for keyword in keywords:
            score += text.count(normalize_text(keyword))
        scores[code] = score
    return scores


def primary_cluster(scores: dict[int, int]) -> int:
    best_score = max(scores.values()) if scores else 0
    if best_score <= 0:
        return 5
    return min(code for code, score in scores.items() if score == best_score)


def proposed_next_code(cluster_code: int) -> int:
    return {
        0: 0,  # packet/matrix bridge operator
        1: 1,  # finite anomaly to automorphic charge correction
        2: 2,  # automorphic Fourier lift
        3: 3,  # profunctor materialization
        4: 4,  # coherence import/export
        5: 5,  # quotient/support refinement
        6: 6,  # exceptional geometry bridge audit
    }[cluster_code]


def inventory_digest(rows: list[dict[str, Any]]) -> str:
    lines = []
    for row in rows:
        lines.append(
            "|".join(
                [
                    str(row["report_code"]),
                    row["path"],
                    str(row["certified_flag"]),
                    str(row["consumed_flag"]),
                    str(row["primary_cluster_code"]),
                    str(row["theme_count"]),
                ]
            )
        )
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def build_rows() -> dict[str, Any]:
    consumed = focused_consumed_paths()
    report_paths = sorted(THEOREM_ROOT.glob("*/report.json"), key=lambda path: relpath(path))
    report_rows: list[dict[str, Any]] = []
    cluster_acc: dict[int, Counter[str]] = {code: Counter() for code, _name, _kw in CLUSTERS}
    source_inventory: list[dict[str, Any]] = []

    for report_code, path in enumerate(report_paths):
        rel = relpath(path)
        report_id = path.parent.name
        report = load_json(path)
        text = report_text(report_id, report)
        scores = score_clusters(text)
        primary = primary_cluster(scores)
        theme_count = sum(1 for value in scores.values() if value > 0)
        cert_flag = certified(report)
        consumed_flag = int(rel in consumed)
        obstruction_flag = int(
            any(
                word in text
                for word in [
                    "obstruction",
                    "missing",
                    "fails",
                    "fail",
                    "gap",
                    "not found",
                    "no certified",
                    "not constructed",
                    "out of scope",
                ]
            )
        )
        bridge_gap_flag = int(
            "bridge" in text
            and any(word in text for word in ["missing", "gap", "obstruction", "no certified"])
        )
        priority = (
            (1000 if cert_flag and not consumed_flag else 0)
            + 100 * theme_count
            + 30 * obstruction_flag
            + 50 * bridge_gap_flag
            + min(99, sum(scores.values()))
        )
        row = {
            "report_code": report_code,
            "path": rel,
            "report_id": report_id,
            "status": str(report.get("status", "")),
            "certificate_sha256": str(report.get("certificate_sha256", "")),
            "certified_flag": cert_flag,
            "consumed_flag": consumed_flag,
            "primary_cluster_code": primary,
            "theme_count": theme_count,
            "obstruction_flag": obstruction_flag,
            "bridge_gap_flag": bridge_gap_flag,
            "priority_score": priority,
            "claim": str(report.get("claim", "")),
            "cluster_scores": scores,
        }
        report_rows.append(row)
        source_inventory.append(
            {
                "report_code": report_code,
                "path": rel,
                "report_id": report_id,
                "status": row["status"],
                "certificate_sha256": row["certificate_sha256"],
                "certified_flag": cert_flag,
                "consumed_flag": consumed_flag,
                "primary_cluster_code": primary,
                "theme_count": theme_count,
                "priority_score": priority,
            }
        )
        acc = cluster_acc[primary]
        acc["report_count"] += 1
        acc["certified_count"] += cert_flag
        acc["consumed_certified_count"] += int(cert_flag and consumed_flag)
        acc["unconsumed_certified_count"] += int(cert_flag and not consumed_flag)
        acc["multi_theme_unconsumed_count"] += int(cert_flag and not consumed_flag and theme_count >= 2)
        acc["obstruction_count"] += int(cert_flag and not consumed_flag and obstruction_flag)
        acc["bridge_gap_count"] += int(cert_flag and not consumed_flag and bridge_gap_flag)
        acc["top_priority_score"] = max(acc["top_priority_score"], priority)

    seam_candidates = [
        row
        for row in report_rows
        if row["certified_flag"]
        and not row["consumed_flag"]
        and row["theme_count"] >= 2
    ]
    seam_candidates.sort(
        key=lambda row: (
            -int(row["priority_score"]),
            int(row["primary_cluster_code"]),
            str(row["path"]),
        )
    )
    seam_rows = [
        {
            "seam_id": index,
            "report_code": int(row["report_code"]),
            "primary_cluster_code": int(row["primary_cluster_code"]),
            "theme_count": int(row["theme_count"]),
            "priority_score": int(row["priority_score"]),
            "obstruction_flag": int(row["obstruction_flag"]),
            "bridge_gap_flag": int(row["bridge_gap_flag"]),
            "proposed_next_code": proposed_next_code(int(row["primary_cluster_code"])),
        }
        for index, row in enumerate(seam_candidates[:32])
    ]
    cluster_rows = []
    for code, _name, _keywords in CLUSTERS:
        acc = cluster_acc[code]
        cluster_rows.append(
            {
                "cluster_id": code,
                "report_count": int(acc["report_count"]),
                "certified_count": int(acc["certified_count"]),
                "consumed_certified_count": int(acc["consumed_certified_count"]),
                "unconsumed_certified_count": int(acc["unconsumed_certified_count"]),
                "multi_theme_unconsumed_count": int(acc["multi_theme_unconsumed_count"]),
                "obstruction_count": int(acc["obstruction_count"]),
                "bridge_gap_count": int(acc["bridge_gap_count"]),
                "reopen_flag": int(acc["multi_theme_unconsumed_count"] > 0),
                "top_priority_score": int(acc["top_priority_score"]),
            }
        )
    top_cluster = max(
        cluster_rows,
        key=lambda row: (
            row["reopen_flag"],
            row["top_priority_score"],
            row["multi_theme_unconsumed_count"],
            -row["cluster_id"],
        ),
    )
    top_seam_code = int(seam_rows[0]["report_code"]) if seam_rows else -1
    obs = {
        "theorem_report_count": len(report_rows),
        "certified_report_count": sum(row["certified_flag"] for row in report_rows),
        "focused_consumed_report_count": sum(
            row["certified_flag"] and row["consumed_flag"] for row in report_rows
        ),
        "unconsumed_certified_report_count": sum(
            row["certified_flag"] and not row["consumed_flag"] for row in report_rows
        ),
        "cluster_count": len(CLUSTERS),
        "reopened_cluster_count": sum(row["reopen_flag"] for row in cluster_rows),
        "seam_candidate_count": len(seam_candidates),
        "multi_theme_unconsumed_count": sum(
            row["certified_flag"] and not row["consumed_flag"] and row["theme_count"] >= 2
            for row in report_rows
        ),
        "obstruction_candidate_count": sum(
            row["certified_flag"] and not row["consumed_flag"] and row["obstruction_flag"]
            for row in report_rows
        ),
        "bridge_gap_candidate_count": sum(
            row["certified_flag"] and not row["consumed_flag"] and row["bridge_gap_flag"]
            for row in report_rows
        ),
        "top_cluster_code": int(top_cluster["cluster_id"]),
        "top_seam_report_code": top_seam_code,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    cluster_table = table_from_rows(CLUSTER_COLUMNS, cluster_rows)
    seam_table = table_from_rows(SEAM_COLUMNS, seam_rows)
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    return {
        "cluster_rows": cluster_rows,
        "seam_rows": seam_rows,
        "obs_rows": obs_rows,
        "cluster_table": cluster_table,
        "seam_table": seam_table,
        "observable_table": obs_table,
        "cluster_text_hash": hashlib.sha256(
            digest_text(CLUSTER_COLUMNS, cluster_rows).encode("ascii")
        ).hexdigest(),
        "seam_text_hash": hashlib.sha256(
            digest_text(SEAM_COLUMNS, seam_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
        "obs": obs,
        "source_inventory": source_inventory,
        "source_inventory_sha256": inventory_digest(source_inventory),
        "top_candidates": [
            {
                "seam_id": index,
                "report_code": int(row["report_code"]),
                "report_id": row["report_id"],
                "path": row["path"],
                "primary_cluster": CLUSTER_NAMES[int(row["primary_cluster_code"])],
                "theme_count": int(row["theme_count"]),
                "priority_score": int(row["priority_score"]),
                "obstruction_flag": int(row["obstruction_flag"]),
                "bridge_gap_flag": int(row["bridge_gap_flag"]),
                "claim": row["claim"],
            }
            for index, row in enumerate(seam_candidates[:12])
        ],
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inventory_nonempty": obs["theorem_report_count"] > 0,
        "certified_reports_seen": obs["certified_report_count"] > 0,
        "focused_consumption_seen": obs["focused_consumed_report_count"] > 0,
        "reopen_candidates_found": (
            obs["unconsumed_certified_report_count"] > 0
            and obs["seam_candidate_count"] > 0
            and obs["reopened_cluster_count"] > 0
        ),
        "cluster_shape_exact": obs["cluster_count"] == len(CLUSTERS),
        "fingerprints_exact": (
            rows["cluster_text_hash"] == CLUSTER_TEXT_HASH
            and rows["seam_text_hash"] == SEAM_TEXT_HASH
            and rows["obs_text_hash"] == OBS_TEXT_HASH
        ),
        "scope_not_overclaimed": obs["complete_goal_claim_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["cluster_table"].shape),
            tuple(rows["seam_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (len(CLUSTERS), len(CLUSTER_COLUMNS)),
            (min(obs["seam_candidate_count"], 32), len(SEAM_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "oracle_reopen_cluster_audit",
        "cluster_code_map": {str(code): name for code, name, _kw in CLUSTERS},
        "proposed_next_code_map": {
            "0": "packet_matrix_bridge_operator_audit",
            "1": "finite_anomaly_to_automorphic_charge_audit",
            "2": "automorphic_fourier_lift_audit",
            "3": "owner_raw_profunctor_materialization_audit",
            "4": "c985_coherence_import_export_audit",
            "5": "quotient_support_refinement_audit",
            "6": "exceptional_geometry_bridge_audit",
        },
        "summary": {
            "theorem_report_count": obs["theorem_report_count"],
            "certified_report_count": obs["certified_report_count"],
            "focused_consumed_report_count": obs["focused_consumed_report_count"],
            "unconsumed_certified_report_count": obs[
                "unconsumed_certified_report_count"
            ],
            "reopened_cluster_count": obs["reopened_cluster_count"],
            "seam_candidate_count": obs["seam_candidate_count"],
            "top_cluster_code": obs["top_cluster_code"],
            "top_seam_report_code": obs["top_seam_report_code"],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "top_candidates": rows["top_candidates"],
        "source_inventory_sha256": rows["source_inventory_sha256"],
        "cluster_text_sha256": rows["cluster_text_hash"],
        "seam_text_sha256": rows["seam_text_hash"],
        "observable_text_sha256": rows["obs_text_hash"],
        "cluster_table_sha256": sha_array(rows["cluster_table"]),
        "seam_table_sha256": sha_array(rows["seam_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    cluster_payload = {
        "schema": "long.cluster@1",
        "object": "oracle_reopen_cluster_audit",
        "status": STATUS if all(checks.values()) else "LONG_CLUSTER_PROVISIONAL",
        "witness": witness,
    }
    inputs: dict[str, Any] = {
        **{
            f"focused_manifest_{name}": input_entry(path)
            for name, path in FOCUSED_MANIFESTS.items()
            if path.exists()
        },
        **{
            f"focused_report_{name}": input_entry(
                path,
                {
                    "status": load_json(path).get("status"),
                    "certificate_sha256": load_json(path).get("certificate_sha256"),
                },
            )
            for name, path in FOCUSED_REPORTS.items()
            if path.exists()
        },
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT)
        if VALIDATOR_SCRIPT.exists()
        else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    for candidate in rows["top_candidates"]:
        inputs[f"top_seam_{candidate['seam_id']}"] = input_entry(
            ROOT / candidate["path"],
            {
                "report_id": candidate["report_id"],
                "primary_cluster": candidate["primary_cluster"],
            },
        )
    report = {
        "schema": "long.cluster.report@1",
        "status": cluster_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_cluster reopens the focused frontier by clustering certified "
            "theorem reports that are not direct inputs to the oracle guardrails. "
            "It is a discovery/routing certificate: it identifies connected seams "
            "for the next focused proof obligations without claiming those seams "
            "are mathematically solved."
        ),
        "stage_protocol": {
            "draft": "read focused oracle manifests and theorem report inventory",
            "witness": "emit cluster rows, seam rows, observable counts, and top candidates",
            "coherence": "check consumption split, cluster table shape, seam candidate existence, hashes, and source inventory digest",
            "closure": "certify a reopen audit without claiming the reopened seams are solved",
            "emit": "write long_cluster artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "cluster": relpath(OUT_DIR / "cluster.json"),
            "cluster_csv": relpath(OUT_DIR / "cluster.csv"),
            "seam_csv": relpath(OUT_DIR / "seam.csv"),
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
                "certified reports outside the current focused oracle inputs are clustered deterministically",
                "multi-theme unconsumed reports are promoted into ranked reopen seam candidates",
                "the frontier-empty claim is now guarded by an explicit reopen audit",
            ],
            "does_not_certify_because_out_of_scope": [
                "that any reopened seam is solved",
                "that keyword clusters are semantic equivalences",
                "broad bundle integration without running the broad certificate gate",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Materialize the top long_cluster seam as a dedicated focused proof "
            "obligation, then feed its decision back into long_orac and "
            "long_frontier."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.cluster.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.cluster.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "cluster": cluster_payload,
        "cluster_csv": csv_text(CLUSTER_COLUMNS, rows["cluster_rows"]),
        "seam_csv": csv_text(SEAM_COLUMNS, rows["seam_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "cluster_table": rows["cluster_table"],
        "seam_table": rows["seam_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "cluster_text_sha256": rows["cluster_text_hash"],
            "seam_text_sha256": rows["seam_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
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
    write_json(OUT_DIR / "cluster.json", payloads["cluster"])
    (OUT_DIR / "cluster.csv").write_text(payloads["cluster_csv"], encoding="utf-8")
    (OUT_DIR / "seam.csv").write_text(payloads["seam_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        cluster_table=payloads["cluster_table"],
        seam_table=payloads["seam_table"],
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
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "top_candidates": report["witness"]["top_candidates"][:5],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
