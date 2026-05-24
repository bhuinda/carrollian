from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


MAP_ID = "boundary_to_loop"
DEFAULT_OUT_DIR = D20_INVARIANTS / "boundary_to_loop"
EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
FIELD_PRIME = 1_000_003


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


def parse_label(label: str) -> tuple[str, ...]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label {label!r}")
    order = {name: i for i, name in enumerate(H6_LABELS)}
    return tuple(sorted((part.strip() for part in body[1:-1].split(",") if part.strip()), key=order.__getitem__))


def label_text(parts: tuple[str, ...]) -> str:
    return "{" + ",".join(parts) + "}"


def load_edges() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            u_label = parse_label(row["u_label"])
            v_label = parse_label(row["v_label"])
            removed_uv = sorted(set(u_label) - set(v_label), key=H6_LABELS.index)
            added_uv = sorted(set(v_label) - set(u_label), key=H6_LABELS.index)
            if len(removed_uv) != 1 or len(added_uv) != 1:
                raise ValueError(f"bad D20 edge labels for edge {row['edge_id']}")
            rows.append(
                {
                    "edge_id": int(row["edge_id"]),
                    "u": int(row["u"]),
                    "v": int(row["v"]),
                    "u_label": label_text(u_label),
                    "v_label": label_text(v_label),
                    "shared_duad": row["shared_duad"],
                    "swapped_pair": row["swapped_pair"],
                    "interface_weight": int(row["interface_weight"]),
                    "selector_duad_index": int(row["selector_duad_index"]),
                    "selector_duad": row["selector_duad"],
                    "selector_choice": int(row["selector_choice"]),
                    "u_to_v": {
                        "removed": removed_uv[0],
                        "added": added_uv[0],
                    },
                    "v_to_u": {
                        "removed": added_uv[0],
                        "added": removed_uv[0],
                    },
                }
            )
    return sorted(rows, key=lambda row: row["edge_id"])


def load_cycle(cycle_id: int) -> dict[str, Any]:
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["cycle_id"]) == cycle_id:
                return {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "vertices": [int(part) for part in row["vertices"].split()],
                    "edge_ids": [int(part) for part in row["edge_ids"].split()],
                    "optical_action": int(row["optical_action"]),
                    "vertex_labels": row["vertex_labels"],
                }
    raise ValueError(f"cycle {cycle_id} not found")


def relation_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rel_npz = np.load(RELATION_NPZ)
    tensor_npz = np.load(TENSOR_NPZ)
    return (
        np.asarray(rel_npz["block_i"], dtype=np.int64),
        np.asarray(rel_npz["block_j"], dtype=np.int64),
        np.asarray(tensor_npz["triples"], dtype=np.int64),
    )


def build_pair_projection(block_i: np.ndarray, block_j: np.ndarray, triples: np.ndarray) -> dict[tuple[int, int], dict[int, int]]:
    """Sum all r->a->r relation-pair projections into closed loops at r."""
    projections: dict[tuple[int, int], dict[int, int]] = {}
    for alpha, beta, gamma, coeff in triples.tolist():
        alpha = int(alpha)
        beta = int(beta)
        gamma = int(gamma)
        coeff = int(coeff)
        r = int(block_i[alpha])
        a = int(block_j[alpha])
        if r == a:
            continue
        if int(block_i[beta]) != a or int(block_j[beta]) != r:
            continue
        if int(block_i[gamma]) != r or int(block_j[gamma]) != r:
            continue
        vec = projections.setdefault((r, a), {})
        vec[gamma] = vec.get(gamma, 0) + coeff
    return projections


def vec_digest(vec: dict[int, int]) -> dict[str, Any]:
    entries = [[int(k), int(v)] for k, v in sorted(vec.items()) if v]
    values = [abs(v) for _, v in entries]
    mod_entries = [[k, v % FIELD_PRIME] for k, v in entries if v % FIELD_PRIME]
    return {
        "support": len(entries),
        "coefficient_sum": int(sum(v for _, v in entries)),
        "coefficient_abs_sum": int(sum(values)),
        "coefficient_min": int(min((v for _, v in entries), default=0)),
        "coefficient_max": int(max((v for _, v in entries), default=0)),
        "mod_prime_support": len(mod_entries),
        "mod_prime_sum": int(sum(v for _, v in entries) % FIELD_PRIME),
        "sha256": hashlib.sha256(canonical(entries)).hexdigest(),
        "mod_prime_sha256": hashlib.sha256(canonical(mod_entries)).hexdigest(),
        "entries": entries,
    }


def add_vec(target: dict[int, int], source: dict[int, int], scale: int = 1) -> None:
    for key, value in source.items():
        new_value = target.get(key, 0) + scale * int(value)
        if new_value:
            target[key] = new_value
        elif key in target:
            del target[key]


def object_summary(vec: dict[int, int], block_i: np.ndarray) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for rel_id, coeff in vec.items():
        label = H6_LABELS[int(block_i[int(rel_id)])]
        item = out.setdefault(label, {"support": 0, "coefficient_sum": 0, "mod_prime_sum": 0})
        item["support"] += 1
        item["coefficient_sum"] += int(coeff)
        item["mod_prime_sum"] = (item["mod_prime_sum"] + int(coeff)) % FIELD_PRIME
    return out


def build_report() -> dict[str, Any]:
    edges = load_edges()
    edge_by_id = {row["edge_id"]: row for row in edges}
    edge_by_vertices = {tuple(sorted((row["u"], row["v"]))): row for row in edges}
    block_i, block_j, triples = relation_data()
    projections = build_pair_projection(block_i, block_j, triples)

    pair_checks = []
    for r in range(6):
        for a in range(6):
            if r == a:
                continue
            vec = projections.get((r, a), {})
            pair_checks.append(
                {
                    "removed": H6_LABELS[r],
                    "added": H6_LABELS[a],
                    "support": len(vec),
                    "coefficient_sum": int(sum(vec.values())),
                    "all_outputs_closed_at_removed": all(
                        int(block_i[g]) == r and int(block_j[g]) == r for g in vec
                    ),
                }
            )

    oriented_edge_rows = []
    for row in edges:
        for direction, source, target, info in (
            ("u_to_v", row["u"], row["v"], row["u_to_v"]),
            ("v_to_u", row["v"], row["u"], row["v_to_u"]),
        ):
            r = H6_LABELS.index(info["removed"])
            a = H6_LABELS.index(info["added"])
            vec = projections[(r, a)]
            digest = vec_digest(vec)
            oriented_edge_rows.append(
                {
                    "edge_id": row["edge_id"],
                    "direction": direction,
                    "source_vertex": source,
                    "target_vertex": target,
                    "removed": info["removed"],
                    "added": info["added"],
                    "loop_base_object": info["removed"],
                    "support": digest["support"],
                    "coefficient_sum": digest["coefficient_sum"],
                    "coefficient_abs_sum": digest["coefficient_abs_sum"],
                    "mod_prime_sum": digest["mod_prime_sum"],
                    "vector_sha256": digest["sha256"],
                    "mod_prime_vector_sha256": digest["mod_prime_sha256"],
                    "entries": digest["entries"],
                }
            )

    cycle8 = load_cycle(8)
    cycle_vec: dict[int, int] = {}
    cycle_steps = []
    for source, target, edge_id in zip(cycle8["vertices"], cycle8["vertices"][1:], cycle8["edge_ids"]):
        edge = edge_by_id[edge_id]
        if (edge["u"], edge["v"]) == (source, target):
            info = edge["u_to_v"]
            direction = "u_to_v"
        elif (edge["v"], edge["u"]) == (source, target):
            info = edge["v_to_u"]
            direction = "v_to_u"
        else:
            raise ValueError(f"cycle 8 edge orientation mismatch for edge {edge_id}")
        r = H6_LABELS.index(info["removed"])
        a = H6_LABELS.index(info["added"])
        vec = projections[(r, a)]
        add_vec(cycle_vec, vec)
        cycle_steps.append(
            {
                "edge_id": edge_id,
                "source_vertex": source,
                "target_vertex": target,
                "direction": direction,
                "removed": info["removed"],
                "added": info["added"],
                "loop_base_object": info["removed"],
                "step_vector_sha256": vec_digest(vec)["sha256"],
            }
        )

    cycle_digest = vec_digest(cycle_vec)
    checks = {
        "edge_table_exists": EDGE_CSV.exists(),
        "primitive_cycle_table_exists": PRIMITIVE_CYCLES_CSV.exists(),
        "relation_npz_exists": RELATION_NPZ.exists(),
        "tensor_npz_exists": TENSOR_NPZ.exists(),
        "d20_edge_count_is_30": len(edges) == 30,
        "oriented_edge_count_is_60": len(oriented_edge_rows) == 60,
        "all_30_directed_object_pair_projections_exist": len(projections) == 30,
        "all_pair_projection_outputs_closed_at_removed": all(row["all_outputs_closed_at_removed"] for row in pair_checks),
        "all_pair_projection_vectors_nonzero": all(row["support"] > 0 and row["coefficient_sum"] > 0 for row in pair_checks),
        "cycle8_is_expected_first_obstruction": cycle8["edge_ids"] == [11, 1, 2, 22, 21]
        and cycle8["optical_action"] == 374784,
        "cycle8_lift_is_nonzero": cycle_digest["support"] > 0 and cycle_digest["coefficient_sum"] > 0,
        "cycle8_lift_has_mod_prime_nonzero": cycle_digest["mod_prime_support"] > 0
        and cycle_digest["mod_prime_sum"] != 0,
        "cycle8_lift_has_sector33_base_overlap": any(
            key in object_summary(cycle_vec, block_i) for key in ("B+", "S+")
        ),
        "edge_vertices_are_unique": len(edge_by_vertices) == 30,
    }
    all_checks_pass = all(checks.values())
    status = "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED" if all_checks_pass else "D20_BOUNDARY_TO_LOOP_MAP_NEEDS_REVIEW"

    report = {
        "schema": "d20.boundary_to_loop_map.v1",
        "status": status,
        "object": "d20",
        "definition": {
            "lambda_boundary": (
                "For an oriented D20 edge U->V, let r be the unique channel removed from U and "
                "a the unique channel added in V. lambda_boundary(U->V) is the sum, over all A985 "
                "relations alpha:r->a and beta:a->r, of the closed-loop product alpha*beta in Hom(r,r)."
            ),
            "codomain": "Loop_297 = direct sum_i Hom(i,i) closed-loop relation basis",
            "field_prime_for_reductions": FIELD_PRIME,
        },
        "inputs": {
            "d20_edges": {"path": rel(EDGE_CSV), "sha256": sha_file(EDGE_CSV)},
            "primitive_cycles": {"path": rel(PRIMITIVE_CYCLES_CSV), "sha256": sha_file(PRIMITIVE_CYCLES_CSV)},
            "relation_memberships": {"path": rel(RELATION_NPZ), "sha256": sha_file(RELATION_NPZ)},
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "derived": {
            "directed_object_pair_projection_count": len(projections),
            "pair_projection_summaries": pair_checks,
            "oriented_edge_count": len(oriented_edge_rows),
            "cycle8_lift": {
                "cycle": cycle8,
                "steps": cycle_steps,
                "vector": cycle_digest,
                "object_summary": object_summary(cycle_vec, block_i),
            },
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Materialize or deterministically recompute the Pi_33 character/idempotent functional, then evaluate it "
            "on the certified cycle8 Loop_297 vector."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_outputs(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_report()
    manifest = {
        "schema": "d20.boundary_to_loop_map_manifest.v1",
        "name": MAP_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "validation_tests": [
            "construct all 30 directed object-pair A985 tube projections",
            "construct both orientations for all 30 D20 edges",
            "verify every lift lands in the closed-loop relation basis at the removed object",
            "verify the cycle-8 lift is nonzero over integers and modulo F_1000003",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    report = write_outputs()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
