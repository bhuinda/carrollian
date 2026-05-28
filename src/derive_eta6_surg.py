from __future__ import annotations

import csv
import json
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from . import derive_eta6_ext_cone as ext
    from . import derive_eta6_hpol as hpol
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_ext_cone as ext
    import derive_eta6_hpol as hpol
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_surg"
STATUS = "ETA6_SURG_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

EXT_REPORT = ext.OUT_DIR / "report.json"
EXT_TABLES = ext.OUT_DIR / "tables.npz"
HPOL_REPORT = hpol.OUT_DIR / "report.json"
HPOL_WEIGHTS = hpol.OUT_DIR / "weights.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_surg.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_surg.py"

OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "support_row_count": 0,
    "negative_ray_row_count": 1,
    "first_hit_row_count": 2,
    "survivor_row_count": 3,
    "first_tau_numerator": 4,
    "first_tau_denominator": 5,
    "next_tau_numerator": 6,
    "next_tau_denominator": 7,
    "post_tau_numerator": 8,
    "post_tau_denominator": 9,
    "nonpositive_survivor_count": 10,
    "positive_survivor_count": 11,
    "min_survivor_slack_numerator": 12,
    "min_survivor_slack_denominator": 13,
    "removed_negative_post_count": 14,
    "support_cone_positive_after_cut_flag": 15,
    "topology_replacement_certified_flag": 16,
    "eta6_opened_flag": 17,
}
CRIT_COLUMNS = [
    "rank",
    "slack_row_id",
    "face_id",
    "vertex_id",
    "face_type_code",
    "face_size",
    "slack_x1e12",
    "face_weight",
    "tau_num",
    "tau_den",
]
DROP_COLUMNS = [
    "drop_id",
    "slack_row_id",
    "face_id",
    "vertex_id",
    "slack_x1e12",
    "face_weight",
    "post_slack_num",
    "post_slack_den",
]
SURVIVOR_COLUMNS = [
    "sample_id",
    "slack_row_id",
    "face_id",
    "vertex_id",
    "slack_x1e12",
    "face_weight",
    "post_slack_num",
    "post_slack_den",
]
SAMPLE_LIMIT = 16


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


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


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def face_weights() -> dict[int, int]:
    with HPOL_WEIGHTS.open("r", encoding="utf-8", newline="") as handle:
        return {
            int(row["face_id"]): int(row["weight"])
            for row in csv.DictReader(handle)
        }


def frac_parts(value: Fraction) -> tuple[int, int]:
    return int(value.numerator), int(value.denominator)


def build_surg_rows() -> dict[str, Any]:
    weights = face_weights()
    tables = np.load(EXT_TABLES, allow_pickle=False)
    slack_table = np.asarray(tables["slack_table"], dtype=np.int64)
    critical = []
    for row in slack_table:
        slack_row_id = int(row[0])
        face_id = int(row[1])
        vertex_id = int(row[2])
        face_type_code = int(row[3])
        face_size = int(row[4])
        slack = int(row[5])
        weight = weights[face_id]
        if weight < 0:
            critical.append(
                (
                    Fraction(slack, -weight),
                    slack_row_id,
                    face_id,
                    vertex_id,
                    face_type_code,
                    face_size,
                    slack,
                    weight,
                )
            )
    critical.sort()
    first_tau = critical[0][0]
    first_hits = [row for row in critical if row[0] == first_tau]
    next_tau = next(row[0] for row in critical if row[0] > first_tau)
    post_tau = (first_tau + next_tau) / 2
    first_hit_ids = {row[1] for row in first_hits}

    critical_rows = []
    for rank, row in enumerate(critical):
        tau_num, tau_den = frac_parts(row[0])
        critical_rows.append(
            {
                "rank": rank,
                "slack_row_id": row[1],
                "face_id": row[2],
                "vertex_id": row[3],
                "face_type_code": row[4],
                "face_size": row[5],
                "slack_x1e12": row[6],
                "face_weight": row[7],
                "tau_num": tau_num,
                "tau_den": tau_den,
            }
        )

    drop_rows = []
    survivor_samples = []
    removed_negative_post_count = 0
    nonpositive_survivor_count = 0
    positive_survivor_count = 0
    min_survivor: Fraction | None = None
    min_survivor_row: dict[str, int] | None = None
    for row in slack_table:
        slack_row_id = int(row[0])
        face_id = int(row[1])
        vertex_id = int(row[2])
        slack = int(row[5])
        weight = weights[face_id]
        post_slack = Fraction(slack, 1) + post_tau * weight
        post_num, post_den = frac_parts(post_slack)
        if slack_row_id in first_hit_ids:
            if post_slack < 0:
                removed_negative_post_count += 1
            drop_rows.append(
                {
                    "drop_id": len(drop_rows),
                    "slack_row_id": slack_row_id,
                    "face_id": face_id,
                    "vertex_id": vertex_id,
                    "slack_x1e12": slack,
                    "face_weight": weight,
                    "post_slack_num": post_num,
                    "post_slack_den": post_den,
                }
            )
            continue
        if post_slack <= 0:
            nonpositive_survivor_count += 1
        else:
            positive_survivor_count += 1
        if min_survivor is None or post_slack < min_survivor:
            min_survivor = post_slack
            min_survivor_row = {
                "slack_row_id": slack_row_id,
                "face_id": face_id,
                "vertex_id": vertex_id,
                "slack_x1e12": slack,
                "face_weight": weight,
                "post_slack_num": post_num,
                "post_slack_den": post_den,
            }
        if len(survivor_samples) < SAMPLE_LIMIT:
            survivor_samples.append(
                {
                    "sample_id": len(survivor_samples),
                    "slack_row_id": slack_row_id,
                    "face_id": face_id,
                    "vertex_id": vertex_id,
                    "slack_x1e12": slack,
                    "face_weight": weight,
                    "post_slack_num": post_num,
                    "post_slack_den": post_den,
                }
            )
    if min_survivor is None or min_survivor_row is None:
        raise ValueError("no survivor support rows")

    first_num, first_den = frac_parts(first_tau)
    next_num, next_den = frac_parts(next_tau)
    post_num, post_den = frac_parts(post_tau)
    min_num, min_den = frac_parts(min_survivor)
    obs_values = {
        "support_row_count": int(slack_table.shape[0]),
        "negative_ray_row_count": len(critical_rows),
        "first_hit_row_count": len(drop_rows),
        "survivor_row_count": int(slack_table.shape[0]) - len(drop_rows),
        "first_tau_numerator": first_num,
        "first_tau_denominator": first_den,
        "next_tau_numerator": next_num,
        "next_tau_denominator": next_den,
        "post_tau_numerator": post_num,
        "post_tau_denominator": post_den,
        "nonpositive_survivor_count": nonpositive_survivor_count,
        "positive_survivor_count": positive_survivor_count,
        "min_survivor_slack_numerator": min_num,
        "min_survivor_slack_denominator": min_den,
        "removed_negative_post_count": removed_negative_post_count,
        "support_cone_positive_after_cut_flag": int(nonpositive_survivor_count == 0),
        "topology_replacement_certified_flag": 0,
        "eta6_opened_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": obs_values[name],
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "critical_rows": critical_rows,
        "drop_rows": drop_rows,
        "survivor_samples": survivor_samples,
        "obs_rows": obs_rows,
        "obs_values": obs_values,
        "first_tau": first_tau,
        "next_tau": next_tau,
        "post_tau": post_tau,
        "min_survivor": min_survivor,
        "min_survivor_row": min_survivor_row,
    }


def build_payload_rows() -> dict[str, Any]:
    return {
        "ext_report": load_json(EXT_REPORT),
        "hpol_report": load_json(HPOL_REPORT),
        "surg": build_surg_rows(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    surg = rows["surg"]
    obs_table = table_from_rows(OBS_COLUMNS, surg["obs_rows"])
    crit_table = table_from_rows(CRIT_COLUMNS, surg["critical_rows"])
    drop_table = table_from_rows(DROP_COLUMNS, surg["drop_rows"])
    sample_table = table_from_rows(SURVIVOR_COLUMNS, surg["survivor_samples"])
    obs = surg["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["ext_report"].get("all_checks_pass") is True
            and rows["hpol_report"].get("all_checks_pass") is True
        ),
        "hpol_ray_first_discriminant_hit_is_exact": (
            obs["support_row_count"],
            obs["negative_ray_row_count"],
            obs["first_hit_row_count"],
            obs["first_tau_numerator"],
            obs["first_tau_denominator"],
            [row["slack_row_id"] for row in surg["drop_rows"]],
        )
        == (
            1_740,
            870,
            6,
            96_225_044_865,
            256,
            [1726, 1728, 1734, 1735, 1738, 1739],
        ),
        "post_cut_time_is_between_first_and_second_hits": (
            obs["next_tau_numerator"],
            obs["next_tau_denominator"],
            obs["post_tau_numerator"],
            obs["post_tau_denominator"],
            surg["first_tau"] < surg["post_tau"] < surg["next_tau"],
        )
        == (
            6_415_002_991,
            15,
            3_085_616_438_671,
            7_680,
            True,
        ),
        "surviving_support_cone_stays_positive": (
            obs["survivor_row_count"],
            obs["nonpositive_survivor_count"],
            obs["positive_survivor_count"],
            obs["min_survivor_slack_numerator"],
            obs["min_survivor_slack_denominator"],
            obs["support_cone_positive_after_cut_flag"],
            surg["min_survivor_row"],
        )
        == (
            1_734,
            0,
            1_734,
            2_982_976_390_815,
            128,
            1,
            {
                "slack_row_id": 1619,
                "face_id": 29,
                "vertex_id": 41,
                "slack_x1e12": 384_900_179_460,
                "face_weight": -900,
                "post_slack_num": 2_982_976_390_815,
                "post_slack_den": 128,
            },
        ),
        "removed_rows_are_the_only_post_cut_violations": (
            obs["removed_negative_post_count"],
            obs["topology_replacement_certified_flag"],
            obs["eta6_opened_flag"],
        )
        == (6, 0, 0),
        "table_shapes_match_codebooks": (
            tuple(obs_table.shape),
            tuple(crit_table.shape),
            tuple(drop_table.shape),
            tuple(sample_table.shape),
        )
        == (
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (870, len(CRIT_COLUMNS)),
            (6, len(DROP_COLUMNS)),
            (SAMPLE_LIMIT, len(SURVIVOR_COLUMNS)),
        ),
    }
    witness = {
        "ray_rule": "support slack s(f,v,t) = s(f,v) + t * hpol_face_weight(f)",
        "first_tau": {
            "numerator": obs["first_tau_numerator"],
            "denominator": obs["first_tau_denominator"],
        },
        "post_tau": {
            "numerator": obs["post_tau_numerator"],
            "denominator": obs["post_tau_denominator"],
        },
        "first_hit_slack_row_ids": [row["slack_row_id"] for row in surg["drop_rows"]],
        "first_hit_face_id": 31,
        "first_hit_vertices": [row["vertex_id"] for row in surg["drop_rows"]],
        "survivor_rows": obs["survivor_row_count"],
        "nonpositive_survivor_count": obs["nonpositive_survivor_count"],
        "min_survivor_slack": {
            "numerator": obs["min_survivor_slack_numerator"],
            "denominator": obs["min_survivor_slack_denominator"],
        },
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "critical_table_sha256": pair.parent.sha_array(crit_table),
        "drop_table_sha256": pair.parent.sha_array(drop_table),
        "sample_table_sha256": pair.parent.sha_array(sample_table),
    }
    surg_json = {
        "schema": "eta6.surg@1",
        "object": "eta6",
        "construction": {
            "proposal": "delete the first-hit support row orbit along the hpol face-offset ray",
            "post_cut_test": "evaluate every surviving support inequality at the midpoint before the second hit",
            "reading": "the first cut has a positive survivor cone, but no replacement complex is certified yet",
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.surg.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_SURG_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The hpol face-offset ray reaches its first support discriminant at "
            "six rows on face 31. Deleting those first-hit rows as a proposed "
            "cut gives an explicit post-cut support test: at the midpoint before "
            "the second hit, all 1,734 survivor support inequalities are still "
            "strictly positive. This certifies a positive survivor cone for the "
            "proposal, not a completed topology replacement or eta6 opening."
        ),
        "stage_protocol": {
            "draft": "start from eta6_ext_cone and eta6_hpol",
            "witness": "follow the hpol support-face offset ray to the first support discriminant",
            "coherence": "delete first-hit rows and evaluate every survivor at the post-cut midpoint",
            "closure": "certify strict positivity of the survivor support cone",
            "emit": "emit short surg artifacts, hashes, verifier command, and next target",
        },
        "inputs": {
            "ext_report": pair.parent.input_entry(
                EXT_REPORT,
                {
                    "status": rows["ext_report"].get("status"),
                    "certificate_sha256": rows["ext_report"].get("certificate_sha256"),
                },
            ),
            "ext_tables": pair.parent.input_entry(EXT_TABLES),
            "hpol_report": pair.parent.input_entry(
                HPOL_REPORT,
                {
                    "status": rows["hpol_report"].get("status"),
                    "certificate_sha256": rows["hpol_report"].get("certificate_sha256"),
                },
            ),
            "hpol_weights": pair.parent.input_entry(HPOL_WEIGHTS),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "surg": pair.parent.relpath(OUT_DIR / "surg.json"),
            "crit_csv": pair.parent.relpath(OUT_DIR / "crit.csv"),
            "drop_csv": pair.parent.relpath(OUT_DIR / "drop.csv"),
            "samp_csv": pair.parent.relpath(OUT_DIR / "samp.csv"),
            "obs_csv": pair.parent.relpath(OUT_DIR / "obs.csv"),
            "tables": pair.parent.relpath(OUT_DIR / "tables.npz"),
            "certificate": pair.parent.relpath(OUT_DIR / "cert.json"),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the first exact support-discriminant hit along the hpol face-offset ray",
                "the six first-hit support rows proposed for deletion",
                "strict positivity of every surviving support inequality just past the cut",
            ],
            "does_not_certify_because_not_required": [
                "a full replacement boundary complex after the cut",
                "a topology-changing surgery across eta6",
                "opening or killing eta6",
            ],
        },
        "next_highest_yield_item": (
            "Build the replacement cell complex for the six-row face-31 cut, "
            "then rerun the support-cone and affine-circuit checks on that new complex."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.surg.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.surg.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "surg": surg_json,
        "crit_csv": csv_text(CRIT_COLUMNS, surg["critical_rows"]),
        "drop_csv": csv_text(DROP_COLUMNS, surg["drop_rows"]),
        "samp_csv": csv_text(SURVIVOR_COLUMNS, surg["survivor_samples"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, surg["obs_rows"]),
        "obs_table": obs_table,
        "crit_table": crit_table,
        "drop_table": drop_table,
        "sample_table": sample_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = ext.nonholonomic.preservation.INDEX_PATH
    if index_path.exists():
        index_payload = load_json(index_path)
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(index_path, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(OUT_DIR / "surg.json", payloads["surg"])
    (OUT_DIR / "crit.csv").write_text(payloads["crit_csv"], encoding="utf-8")
    (OUT_DIR / "drop.csv").write_text(payloads["drop_csv"], encoding="utf-8")
    (OUT_DIR / "samp.csv").write_text(payloads["samp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        observable_table=payloads["obs_table"],
        critical_table=payloads["crit_table"],
        drop_table=payloads["drop_table"],
        sample_table=payloads["sample_table"],
    )
    pair.parent.write_json(OUT_DIR / "cert.json", payloads["cert"])
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
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
