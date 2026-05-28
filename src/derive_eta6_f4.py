from __future__ import annotations

import itertools
import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from . import derive_eta6_t2 as t2
    from .derive_c985_associator_rebracketing_oracle import (
        OUT_DIR as ASSOC_DIR,
    )
    from .derive_c985_fusion_multiplicity_typing import OUT_DIR as FUSION_DIR
    from .derive_c985_typed_simple_object_registry import (
        OBJECT_LABELS,
        OUT_DIR as REGISTRY_DIR,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_t2 as t2
    from derive_c985_associator_rebracketing_oracle import (
        OUT_DIR as ASSOC_DIR,
    )
    from derive_c985_fusion_multiplicity_typing import OUT_DIR as FUSION_DIR
    from derive_c985_typed_simple_object_registry import (
        OBJECT_LABELS,
        OUT_DIR as REGISTRY_DIR,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_f4"
STATUS = "ETA6_F4_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

T2_REPORT = t2.OUT_DIR / "report.json"
T2_TABLES = t2.OUT_DIR / "tables.npz"
REGISTRY_REPORT = REGISTRY_DIR / "report.json"
SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
FUSION_REPORT = FUSION_DIR / "report.json"
FUSION_TENSOR = FUSION_DIR / "fusion_tensor_coo.npz"
ASSOC_REPORT = ASSOC_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_f4.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_f4.py"

ORDER_COLUMNS = [
    "row_id",
    "fuse_id",
    "face_id",
    "label_mask",
    "order_id",
    "a",
    "b",
    "c",
    "d",
    "left_support",
    "right_support",
    "support_match_flag",
    "left_mult",
    "right_mult",
    "mult_match_flag",
]
FACE_COLUMNS = [
    "fuse_id",
    "face_id",
    "label_mask",
    "label_count",
    "order_count",
    "left_support_sum",
    "right_support_sum",
    "support_sum_match_flag",
    "left_mult_sum",
    "right_mult_sum",
    "mult_sum_match_flag",
    "ordered_support_match_count",
    "ordered_mult_match_count",
    "min_support",
    "max_support",
    "min_mult",
    "max_mult",
]
SAMPLE_COLUMNS = [
    "row_id",
    "fuse_id",
    "order_id",
    "left_alpha",
    "left_beta",
    "left_chi",
    "left_delta",
    "left_epsilon",
    "left_c1",
    "left_c2",
    "right_alpha",
    "right_beta",
    "right_chi",
    "right_eta",
    "right_epsilon",
    "right_c1",
    "right_c2",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "fused_face_count": 0,
    "ordered_quad_count": 1,
    "positive_order_count": 2,
    "ordered_mult_match_count": 3,
    "ordered_support_match_count": 4,
    "face_support_sum_match_count": 5,
    "face_mult_sum_match_count": 6,
    "left_support_total": 7,
    "right_support_total": 8,
    "left_mult_total": 9,
    "right_mult_total": 10,
    "min_order_support": 11,
    "min_order_mult": 12,
    "raw_support_pointwise_obstruction_flag": 13,
    "multiplicity_f_address_flag": 14,
    "sym_support_flag": 15,
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


def mask_labels(mask: int) -> list[int]:
    return [label_id for label_id in range(6) if (int(mask) >> label_id) & 1]


def rel_tables(source_target: np.ndarray) -> tuple[dict[tuple[int, int], list[int]], dict[tuple[int, int], set[int]]]:
    by_pair = {(source, target): [] for source in range(6) for target in range(6)}
    for relation_id, (source, target) in enumerate(source_target):
        by_pair[(int(source), int(target))].append(int(relation_id))
    return by_pair, {key: set(value) for key, value in by_pair.items()}


def fusion_out(triples: np.ndarray) -> dict[tuple[int, int], list[tuple[int, int]]]:
    out: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for alpha, beta, gamma, coeff in triples:
        out[(int(alpha), int(beta))].append((int(gamma), int(coeff)))
    return out


def count_order(
    order: tuple[int, int, int, int],
    by_pair: dict[tuple[int, int], list[int]],
    set_by_pair: dict[tuple[int, int], set[int]],
    out: dict[tuple[int, int], list[tuple[int, int]]],
) -> dict[str, Any]:
    a, b, c, d = order
    ab = by_pair[(a, b)]
    bc = by_pair[(b, c)]
    cd = by_pair[(c, d)]
    ac = set_by_pair[(a, c)]
    ad = set_by_pair[(a, d)]
    bd = set_by_pair[(b, d)]

    left_support = 0
    left_mult = 0
    right_support = 0
    right_mult = 0
    first_left: tuple[int, ...] | None = None
    first_right: tuple[int, ...] | None = None

    for alpha in ab:
        for beta in bc:
            for delta, coeff1 in out.get((alpha, beta), ()):
                if delta not in ac:
                    continue
                for chi in cd:
                    for epsilon, coeff2 in out.get((delta, chi), ()):
                        if epsilon not in ad:
                            continue
                        left_support += 1
                        left_mult += coeff1 * coeff2
                        if first_left is None:
                            first_left = (
                                alpha,
                                beta,
                                chi,
                                delta,
                                epsilon,
                                coeff1,
                                coeff2,
                            )

    for beta in bc:
        for chi in cd:
            for eta, coeff1 in out.get((beta, chi), ()):
                if eta not in bd:
                    continue
                for alpha in ab:
                    for epsilon, coeff2 in out.get((alpha, eta), ()):
                        if epsilon not in ad:
                            continue
                        right_support += 1
                        right_mult += coeff1 * coeff2
                        if first_right is None:
                            first_right = (
                                alpha,
                                beta,
                                chi,
                                eta,
                                epsilon,
                                coeff1,
                                coeff2,
                            )

    if first_left is None or first_right is None:
        raise ValueError(f"empty F-address support for order {order}")
    return {
        "left_support": int(left_support),
        "right_support": int(right_support),
        "left_mult": int(left_mult),
        "right_mult": int(right_mult),
        "first_left": first_left,
        "first_right": first_right,
    }


def build_f4_rows() -> dict[str, Any]:
    t2_tables = np.load(T2_TABLES, allow_pickle=False)
    fuse_table = np.asarray(t2_tables["fuse_table"], dtype=np.int64)
    source_target = np.load(SOURCE_TARGET, allow_pickle=False)
    triples = np.load(FUSION_TENSOR, allow_pickle=False)["triples"]
    by_pair, set_by_pair = rel_tables(source_target)
    out = fusion_out(triples)

    order_rows: list[dict[str, int]] = []
    sample_rows: list[dict[str, int]] = []
    row_id = 0
    for fuse_values in fuse_table:
        fuse = {
            column: int(fuse_values[index])
            for index, column in enumerate(t2.FUSE_COLUMNS)
        }
        labels = mask_labels(fuse["label_mask"])
        for order_id, order in enumerate(itertools.permutations(labels)):
            counts = count_order(order, by_pair, set_by_pair, out)
            left = counts["first_left"]
            right = counts["first_right"]
            order_rows.append(
                {
                    "row_id": row_id,
                    "fuse_id": fuse["fuse_id"],
                    "face_id": fuse["face_id"],
                    "label_mask": fuse["label_mask"],
                    "order_id": order_id,
                    "a": order[0],
                    "b": order[1],
                    "c": order[2],
                    "d": order[3],
                    "left_support": counts["left_support"],
                    "right_support": counts["right_support"],
                    "support_match_flag": int(
                        counts["left_support"] == counts["right_support"]
                    ),
                    "left_mult": counts["left_mult"],
                    "right_mult": counts["right_mult"],
                    "mult_match_flag": int(counts["left_mult"] == counts["right_mult"]),
                }
            )
            sample_rows.append(
                {
                    "row_id": row_id,
                    "fuse_id": fuse["fuse_id"],
                    "order_id": order_id,
                    "left_alpha": left[0],
                    "left_beta": left[1],
                    "left_chi": left[2],
                    "left_delta": left[3],
                    "left_epsilon": left[4],
                    "left_c1": left[5],
                    "left_c2": left[6],
                    "right_alpha": right[0],
                    "right_beta": right[1],
                    "right_chi": right[2],
                    "right_eta": right[3],
                    "right_epsilon": right[4],
                    "right_c1": right[5],
                    "right_c2": right[6],
                }
            )
            row_id += 1

    face_rows = []
    for fuse_id in sorted({row["fuse_id"] for row in order_rows}):
        rows = [row for row in order_rows if row["fuse_id"] == fuse_id]
        left_support_sum = sum(row["left_support"] for row in rows)
        right_support_sum = sum(row["right_support"] for row in rows)
        left_mult_sum = sum(row["left_mult"] for row in rows)
        right_mult_sum = sum(row["right_mult"] for row in rows)
        face_rows.append(
            {
                "fuse_id": fuse_id,
                "face_id": rows[0]["face_id"],
                "label_mask": rows[0]["label_mask"],
                "label_count": len(mask_labels(rows[0]["label_mask"])),
                "order_count": len(rows),
                "left_support_sum": int(left_support_sum),
                "right_support_sum": int(right_support_sum),
                "support_sum_match_flag": int(left_support_sum == right_support_sum),
                "left_mult_sum": int(left_mult_sum),
                "right_mult_sum": int(right_mult_sum),
                "mult_sum_match_flag": int(left_mult_sum == right_mult_sum),
                "ordered_support_match_count": sum(
                    row["support_match_flag"] for row in rows
                ),
                "ordered_mult_match_count": sum(row["mult_match_flag"] for row in rows),
                "min_support": min(
                    min(row["left_support"], row["right_support"]) for row in rows
                ),
                "max_support": max(
                    max(row["left_support"], row["right_support"]) for row in rows
                ),
                "min_mult": min(min(row["left_mult"], row["right_mult"]) for row in rows),
                "max_mult": max(max(row["left_mult"], row["right_mult"]) for row in rows),
            }
        )

    obs = {
        "fused_face_count": len(face_rows),
        "ordered_quad_count": len(order_rows),
        "positive_order_count": sum(
            int(
                row["left_support"] > 0
                and row["right_support"] > 0
                and row["left_mult"] > 0
                and row["right_mult"] > 0
            )
            for row in order_rows
        ),
        "ordered_mult_match_count": sum(row["mult_match_flag"] for row in order_rows),
        "ordered_support_match_count": sum(
            row["support_match_flag"] for row in order_rows
        ),
        "face_support_sum_match_count": sum(
            row["support_sum_match_flag"] for row in face_rows
        ),
        "face_mult_sum_match_count": sum(row["mult_sum_match_flag"] for row in face_rows),
        "left_support_total": sum(row["left_support"] for row in order_rows),
        "right_support_total": sum(row["right_support"] for row in order_rows),
        "left_mult_total": sum(row["left_mult"] for row in order_rows),
        "right_mult_total": sum(row["right_mult"] for row in order_rows),
        "min_order_support": min(
            min(row["left_support"], row["right_support"]) for row in order_rows
        ),
        "min_order_mult": min(
            min(row["left_mult"], row["right_mult"]) for row in order_rows
        ),
        "raw_support_pointwise_obstruction_flag": int(
            all(row["support_match_flag"] == 0 for row in order_rows)
        ),
        "multiplicity_f_address_flag": int(
            all(row["mult_match_flag"] == 1 for row in order_rows)
            and all(row["left_mult"] > 0 and row["right_mult"] > 0 for row in order_rows)
        ),
        "sym_support_flag": int(
            all(row["support_sum_match_flag"] == 1 for row in face_rows)
            and all(row["left_support_sum"] > 0 for row in face_rows)
        ),
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
        "order_rows": order_rows,
        "face_rows": face_rows,
        "sample_rows": sample_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "source_target": source_target,
        "triples": triples,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_f4_rows()
    order_table = table_from_rows(ORDER_COLUMNS, rows["order_rows"])
    face_table = table_from_rows(FACE_COLUMNS, rows["face_rows"])
    sample_table = table_from_rows(SAMPLE_COLUMNS, rows["sample_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]

    t2_report = load_json(T2_REPORT)
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    assoc_report = load_json(ASSOC_REPORT)

    checks = {
        "input_certificates_available": (
            t2_report.get("all_checks_pass") is True
            and registry_report.get("all_checks_pass") is True
            and fusion_report.get("all_checks_pass") is True
            and assoc_report.get("all_checks_pass") is True
        ),
        "fused_masks_match_t2": [
            row["label_mask"] for row in rows["face_rows"]
        ]
        == [30, 45, 51],
        "all_72_ordered_quadruples_positive": (
            obs["fused_face_count"],
            obs["ordered_quad_count"],
            obs["positive_order_count"],
        )
        == (3, 72, 72),
        "multiplicity_balances_orderwise": (
            obs["ordered_mult_match_count"],
            obs["multiplicity_f_address_flag"],
            obs["left_mult_total"],
            obs["right_mult_total"],
        )
        == (72, 1, 213_172_224, 213_172_224),
        "raw_support_is_not_orderwise_balanced": (
            obs["ordered_support_match_count"],
            obs["raw_support_pointwise_obstruction_flag"],
        )
        == (0, 1),
        "support_balances_after_24_order_symmetrization": (
            obs["face_support_sum_match_count"],
            obs["sym_support_flag"],
            obs["left_support_total"],
            obs["right_support_total"],
        )
        == (3, 1, 56_729_616, 56_729_616),
        "minimum_positive_margins_match": (
            obs["min_order_support"],
            obs["min_order_mult"],
        )
        == (59_904, 884_736),
        "table_shapes_match_codebooks": (
            tuple(order_table.shape),
            tuple(face_table.shape),
            tuple(sample_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (72, len(ORDER_COLUMNS)),
            (3, len(FACE_COLUMNS)),
            (72, len(SAMPLE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }

    witness = {
        "classification": "multiplicity_balanced_sym_support",
        "h6_labels": OBJECT_LABELS,
        "fused_face_masks": [row["label_mask"] for row in rows["face_rows"]],
        "fused_face_ids": [row["face_id"] for row in rows["face_rows"]],
        "ordered_quadruples": obs["ordered_quad_count"],
        "left_support_total": obs["left_support_total"],
        "right_support_total": obs["right_support_total"],
        "left_mult_total": obs["left_mult_total"],
        "right_mult_total": obs["right_mult_total"],
        "min_order_support": obs["min_order_support"],
        "min_order_mult": obs["min_order_mult"],
        "ordered_support_match_count": obs["ordered_support_match_count"],
        "ordered_mult_match_count": obs["ordered_mult_match_count"],
        "face_support_sums": [
            {
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "left": row["left_support_sum"],
                "right": row["right_support_sum"],
            }
            for row in rows["face_rows"]
        ],
        "face_mult_sums": [
            {
                "face_id": row["face_id"],
                "label_mask": row["label_mask"],
                "left": row["left_mult_sum"],
                "right": row["right_mult_sum"],
            }
            for row in rows["face_rows"]
        ],
        "reading": (
            "The three eta6_t2 fused 4-label faces have positive C985 "
            "left/right F-address multiplicity on every ordered sector chain. "
            "Multiplicity dimensions match order-by-order; raw support row "
            "counts only balance after summing over the 24 orderings of each "
            "mask."
        ),
        "order_table_sha256": sha_array(order_table),
        "face_table_sha256": sha_array(face_table),
        "sample_table_sha256": sha_array(sample_table),
        "observable_table_sha256": sha_array(obs_table),
    }

    f4 = {
        "schema": "eta6.f4@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_t2 fused masks",
            "test": "C985 typed F-address multiplicity balance on 4-label faces",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.f4.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_F4_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The eta6_t2 4-label fused faces admit C985 associator semantics at "
            "the F-address multiplicity level: every ordered sector quadruple "
            "has positive left/right multiplicity and equal left/right "
            "multiplicity dimension. Raw support-address cardinality is not "
            "balanced order-by-order, but it balances after the 24-order "
            "symmetrization of each fused mask."
        ),
        "stage_protocol": {
            "draft": "start from the short eta6_t2 fused masks [30,45,51]",
            "witness": "count C985 left and right F-addresses for all 72 ordered sector quadruples",
            "coherence": "check multiplicity balance orderwise and raw support balance after mask symmetrization",
            "closure": "certify the exact f4 pass/obstruction split without asserting a pointwise support bijection",
            "emit": "emit compact f4 artifacts and the next C985 seam",
        },
        "inputs": {
            "t2_report": input_entry(
                T2_REPORT,
                {
                    "status": t2_report.get("status"),
                    "certificate_sha256": t2_report.get("certificate_sha256"),
                },
            ),
            "t2_tables": input_entry(T2_TABLES),
            "typed_registry_report": input_entry(
                REGISTRY_REPORT,
                {
                    "status": registry_report.get("status"),
                    "certificate_sha256": registry_report.get("certificate_sha256"),
                },
            ),
            "source_target": input_entry(SOURCE_TARGET),
            "fusion_report": input_entry(
                FUSION_REPORT,
                {
                    "status": fusion_report.get("status"),
                    "certificate_sha256": fusion_report.get("certificate_sha256"),
                },
            ),
            "fusion_tensor": input_entry(FUSION_TENSOR),
            "associator_report": input_entry(
                ASSOC_REPORT,
                {
                    "status": assoc_report.get("status"),
                    "certificate_sha256": assoc_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "f4": relpath(OUT_DIR / "f4.json"),
            "ord_csv": relpath(OUT_DIR / "ord.csv"),
            "face_csv": relpath(OUT_DIR / "face.csv"),
            "samp_csv": relpath(OUT_DIR / "samp.csv"),
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
                "positive C985 F-address multiplicity for all 72 ordered sector quadruples",
                "left/right multiplicity balance for every ordered quadruple",
                "left/right raw support balance after the 24-order symmetrization of each fused mask",
                "an explicit ordered-support obstruction: no ordered quadruple has equal raw support cardinality",
            ],
            "does_not_certify_because_false_or_open": [
                "pointwise raw support-address balance for a fixed ordered quadruple",
                "a numeric 6j scalar or full F-matrix entry",
                "a new C985 simple object corresponding to a 4-label fused face",
                "pentagon action for repeated non-cubic surgeries",
            ],
        },
        "next_highest_yield_item": (
            "Use the f4 multiplicity pass and support obstruction to search for "
            "the shortest pentagon-addressed surgery that preserves eta6 while "
            "moving the raw support imbalance."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.f4.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.f4.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "f4": f4,
        "ord_csv": csv_text(ORDER_COLUMNS, rows["order_rows"]),
        "face_csv": csv_text(FACE_COLUMNS, rows["face_rows"]),
        "samp_csv": csv_text(SAMPLE_COLUMNS, rows["sample_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "order_table": order_table,
        "face_table": face_table,
        "sample_table": sample_table,
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
    write_json(OUT_DIR / "f4.json", payloads["f4"])
    (OUT_DIR / "ord.csv").write_text(payloads["ord_csv"], encoding="utf-8")
    (OUT_DIR / "face.csv").write_text(payloads["face_csv"], encoding="utf-8")
    (OUT_DIR / "samp.csv").write_text(payloads["samp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        order_table=payloads["order_table"],
        face_table=payloads["face_table"],
        sample_table=payloads["sample_table"],
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
