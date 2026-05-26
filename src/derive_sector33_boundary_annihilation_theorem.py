from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, DATA, ROOT


THEOREM_ID = "sector33_boundary_annihilation"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"
CORE_A985 = DATA / "core" / "a985.json"
RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"

FIELD_PRIME = 1_000_003
H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]


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


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def vec_entries(vec: np.ndarray) -> list[list[int]]:
    return [[int(i), int(vec[i]) % FIELD_PRIME] for i in np.nonzero(vec % FIELD_PRIME)[0]]


def vec_digest(vec: np.ndarray, include_entries: bool = False) -> dict[str, Any]:
    entries = vec_entries(vec)
    values = [int(value) for _, value in entries]
    digest = {
        "support": len(entries),
        "coefficient_sum": int(sum(values) % FIELD_PRIME),
        "coefficient_sum_signed": signed_mod(int(sum(values))),
        "coefficient_abs_sum_signed_lift": int(sum(abs(signed_mod(value)) for value in values)),
        "sha256": hashlib.sha256(canonical(entries)).hexdigest(),
    }
    if include_entries:
        digest["entries"] = entries
    return digest


def rref_nullspace_mod(matrix: np.ndarray, mod: int) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.int64).copy() % mod
    row_count, col_count = matrix.shape
    rank = 0
    pivots: list[int] = []
    pivot_set: set[int] = set()
    for col in range(col_count):
        rows = np.nonzero(matrix[rank:, col])[0]
        if rows.size == 0:
            continue
        pivot = rank + int(rows[0])
        if pivot != rank:
            matrix[[rank, pivot]] = matrix[[pivot, rank]]
        inv = pow(int(matrix[rank, col]), -1, mod)
        matrix[rank, :] = (matrix[rank, :] * inv) % mod
        indices = np.nonzero(matrix[:, col])[0]
        indices = indices[indices != rank]
        if len(indices):
            values = matrix[indices, col].copy()
            matrix[indices, :] = (matrix[indices, :] - values[:, None] * matrix[rank, :]) % mod
        pivots.append(col)
        pivot_set.add(col)
        rank += 1
        if rank == row_count:
            break

    free = [col for col in range(col_count) if col not in pivot_set]
    basis = np.zeros((col_count, len(free)), dtype=np.int64)
    for idx, free_col in enumerate(free):
        basis[free_col, idx] = 1
    if free:
        for row, pivot_col in enumerate(pivots):
            basis[pivot_col, :] = (-matrix[row, free]) % mod
    return basis


def multiply(triples: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    weights = triples[:, 3] % FIELD_PRIME
    values = (((left[alpha] % FIELD_PRIME) * (right[beta] % FIELD_PRIME)) % FIELD_PRIME * weights) % FIELD_PRIME
    out = np.zeros(left.shape[0], dtype=np.int64)
    np.add.at(out, gamma, values)
    return out % FIELD_PRIME


def regular_trace_coefficients(triples: np.ndarray, relation_count: int) -> np.ndarray:
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    weights = triples[:, 3] % FIELD_PRIME
    trace = np.zeros(relation_count, dtype=np.int64)
    mask = gamma == beta
    np.add.at(trace, alpha[mask], weights[mask])
    return trace % FIELD_PRIME


def local_pre_idempotent(
    core: dict[str, Any],
    triples: np.ndarray,
    block_i: np.ndarray,
    block_j: np.ndarray,
    obj: int,
    local_index: int,
) -> np.ndarray:
    ids = np.where((block_i == obj) & (block_j == obj))[0].astype(np.int64)
    local_index_by_relation = {int(relation): idx for idx, relation in enumerate(ids.tolist())}
    mask = np.isin(triples[:, 0], ids) & np.isin(triples[:, 1], ids) & np.isin(triples[:, 2], ids)
    sub = triples[mask]
    n = int(len(ids))
    tensor = np.zeros((n, n, n), dtype=np.int64)
    for alpha, beta, gamma, value in sub.tolist():
        tensor[
            local_index_by_relation[int(alpha)],
            local_index_by_relation[int(beta)],
            local_index_by_relation[int(gamma)],
        ] = int(value)

    commutator_rows = [(tensor[:, alpha, :] - tensor[alpha, :, :]).T for alpha in range(n)]
    center_basis = rref_nullspace_mod(np.vstack(commutator_rows), FIELD_PRIME)
    stored = core["blocks"][obj]
    coordinates = np.asarray(stored["primitive_idempotent_coordinates"], dtype=np.int64) % FIELD_PRIME
    if center_basis.shape[1] != int(stored["center_dimension"]):
        raise ValueError(f"center dimension mismatch for object {obj}")
    if coordinates.shape != (center_basis.shape[1], center_basis.shape[1]):
        raise ValueError(f"primitive idempotent coordinate shape mismatch for object {obj}")

    local_vec = (center_basis @ coordinates[local_index]) % FIELD_PRIME
    global_vec = np.zeros(int(block_i.shape[0]), dtype=np.int64)
    global_vec[ids] = local_vec
    return global_vec


def sector33_tube_idempotent(
    core: dict[str, Any],
    sector33: dict[str, Any],
    triples: np.ndarray,
    block_i: np.ndarray,
    block_j: np.ndarray,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    pieces = []
    vector = np.zeros(int(block_i.shape[0]), dtype=np.int64)
    for signature in sector33["spectral_signature"]:
        obj = int(signature["object"])
        local_indices = [int(value) for value in signature["local_pre_idempotents"]]
        if len(local_indices) != 1:
            raise ValueError("sector 33 is expected to use one local pre-idempotent per active object")
        local_index = local_indices[0]
        piece = local_pre_idempotent(core, triples, block_i, block_j, obj, local_index)
        vector = (vector + piece) % FIELD_PRIME
        pieces.append(
            {
                "object": obj,
                "label": H6_LABELS[obj],
                "local_pre_idempotent": local_index,
                "support": int(np.count_nonzero(piece)),
                "sha256": vec_digest(piece)["sha256"],
            }
        )
    return vector % FIELD_PRIME, pieces


def build_pair_projections(triples: np.ndarray, block_i: np.ndarray, block_j: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    relation_count = int(block_i.shape[0])
    projections: dict[tuple[int, int], np.ndarray] = {}
    for alpha, beta, gamma, value in triples.tolist():
        removed = int(block_i[int(alpha)])
        added = int(block_j[int(alpha)])
        if removed == added:
            continue
        if (
            int(block_i[int(beta)]) == added
            and int(block_j[int(beta)]) == removed
            and int(block_i[int(gamma)]) == removed
            and int(block_j[int(gamma)]) == removed
        ):
            vec = projections.setdefault((removed, added), np.zeros(relation_count, dtype=np.int64))
            vec[int(gamma)] = (int(vec[int(gamma)]) + int(value)) % FIELD_PRIME
    return projections


def parse_label(label: str) -> list[str]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label {label!r}")
    return [part.strip() for part in body[1:-1].split(",") if part.strip()]


def load_edges() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[int(row["edge_id"])] = row
    return rows


def oriented_edge_vector(
    edge: dict[str, Any],
    source: int,
    target: int,
    projections: dict[tuple[int, int], np.ndarray],
) -> tuple[np.ndarray, int]:
    u = int(edge["u"])
    v = int(edge["v"])
    u_label = parse_label(edge["u_label"])
    v_label = parse_label(edge["v_label"])
    if (u, v) == (source, target):
        removed = list(set(u_label) - set(v_label))[0]
        added = list(set(v_label) - set(u_label))[0]
        sign = 1
    elif (v, u) == (source, target):
        removed = list(set(v_label) - set(u_label))[0]
        added = list(set(u_label) - set(v_label))[0]
        sign = -1
    else:
        raise ValueError(f"edge {edge['edge_id']} does not connect {source}->{target}")
    return projections[(H6_LABELS.index(removed), H6_LABELS.index(added))], sign


def character_evaluation(
    triples: np.ndarray,
    trace_coeff: np.ndarray,
    idempotent: np.ndarray,
    vector: np.ndarray,
    dimension: int,
) -> dict[str, Any]:
    left = multiply(triples, idempotent, vector)
    right = multiply(triples, vector, idempotent)
    trace_value = int((trace_coeff @ left) % FIELD_PRIME)
    coefficient = int((trace_value * pow(int(dimension), -1, FIELD_PRIME)) % FIELD_PRIME)
    return {
        "left_action": vec_digest(left),
        "right_action": vec_digest(right),
        "left_equals_right": bool(np.array_equal(left, right)),
        "regular_trace": trace_value,
        "coefficient_mod_prime": coefficient,
        "coefficient_signed": signed_mod(coefficient),
    }


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
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    boundary_to_loop = load_json(BOUNDARY_TO_LOOP_REPORT)
    full_lift = load_json(FULL_A985_LIFT)
    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]
    relation_npz = np.load(RELATION_NPZ)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    trace_coeff = regular_trace_coefficients(triples, int(block_i.shape[0]))

    sector33_rows = [
        profile
        for profile in full_lift["gluing_and_sector_profiles"]["sector_profiles"]
        if int(profile["sector"]) == 33
    ]
    sector33 = sector33_rows[0] if sector33_rows else {}
    idempotent, idempotent_pieces = sector33_tube_idempotent(core, sector33, triples, block_i, block_j)
    idempotent_square = multiply(triples, idempotent, idempotent)
    identity_relations = full_lift["full_A985_idempotent_validation"]["identity_relations_by_object"]
    identity_coefficients_signed = [signed_mod(int(idempotent[idx])) for idx in identity_relations]
    object_support = [
        int(np.count_nonzero(idempotent[(block_i == obj) & (block_j == obj)]))
        for obj in range(len(H6_LABELS))
    ]

    projections = build_pair_projections(triples, block_i, block_j)
    block_dimension = int(sector33["block_dimension"])
    pair_evaluations = []
    for removed in range(len(H6_LABELS)):
        for added in range(len(H6_LABELS)):
            if removed == added:
                continue
            vector = projections[(removed, added)]
            evaluation = character_evaluation(triples, trace_coeff, idempotent, vector, block_dimension)
            pair_evaluations.append(
                {
                    "removed": H6_LABELS[removed],
                    "added": H6_LABELS[added],
                    "vector": vec_digest(vector),
                    "pi33_tube_character": evaluation,
                }
            )

    cycle = boundary_to_loop["derived"]["cycle8_lift"]["cycle"]
    edges = load_edges()
    unweighted = np.zeros(int(block_i.shape[0]), dtype=np.int64)
    optical_weighted = np.zeros(int(block_i.shape[0]), dtype=np.int64)
    signed_orientation = np.zeros(int(block_i.shape[0]), dtype=np.int64)
    for source, target, edge_id in zip(cycle["vertices"], cycle["vertices"][1:], cycle["edge_ids"]):
        edge = edges[int(edge_id)]
        vector, sign = oriented_edge_vector(edge, int(source), int(target), projections)
        unweighted = (unweighted + vector) % FIELD_PRIME
        optical_weighted = (optical_weighted + int(edge["interface_weight"]) * vector) % FIELD_PRIME
        signed_orientation = (signed_orientation + sign * vector) % FIELD_PRIME

    cycle_variants = {
        "unweighted": {
            "vector": vec_digest(unweighted),
            "pi33_tube_character": character_evaluation(triples, trace_coeff, idempotent, unweighted, block_dimension),
        },
        "optical_weighted": {
            "vector": vec_digest(optical_weighted),
            "pi33_tube_character": character_evaluation(triples, trace_coeff, idempotent, optical_weighted, block_dimension),
        },
        "signed_orientation": {
            "vector": vec_digest(signed_orientation),
            "pi33_tube_character": character_evaluation(triples, trace_coeff, idempotent, signed_orientation, block_dimension),
        },
    }

    checks = {
        "boundary_to_loop_is_certified": boundary_to_loop.get("status") == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary_to_loop.get("all_checks_pass") is True,
        "sector33_profile_exists_once": len(sector33_rows) == 1,
        "sector33_profile_is_public_zero": sector33.get("q42_nonzero_count") == 0
        and sector33.get("q12_nonzero_count") == 0,
        "sector33_uses_two_local_pre_idempotents": sum(
            len(signature["local_pre_idempotents"]) for signature in sector33.get("spectral_signature", [])
        )
        == 2,
        "sector33_tube_idempotent_support_matches_profile": object_support
        == sector33.get("object_loop_coordinate_support"),
        "sector33_tube_idempotent_identity_coefficients_match_profile": identity_coefficients_signed
        == sector33.get("identity_coefficients_signed"),
        "sector33_tube_idempotent_is_idempotent": bool(np.array_equal(idempotent_square, idempotent % FIELD_PRIME)),
        "all_30_directed_pair_lifts_tested": len(pair_evaluations) == 30,
        "pi33_annihilates_all_directed_pair_lifts_left_and_right": all(
            row["pi33_tube_character"]["left_action"]["support"] == 0
            and row["pi33_tube_character"]["right_action"]["support"] == 0
            and row["pi33_tube_character"]["coefficient_mod_prime"] == 0
            and row["pi33_tube_character"]["left_equals_right"] is True
            for row in pair_evaluations
        ),
        "cycle8_unweighted_pi33_coefficient_is_zero": cycle_variants["unweighted"]["pi33_tube_character"][
            "coefficient_mod_prime"
        ]
        == 0,
        "cycle8_optical_weighted_pi33_coefficient_is_zero": cycle_variants["optical_weighted"][
            "pi33_tube_character"
        ]["coefficient_mod_prime"]
        == 0,
        "cycle8_signed_orientation_pi33_coefficient_is_zero": cycle_variants["signed_orientation"][
            "pi33_tube_character"
        ]["coefficient_mod_prime"]
        == 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector33_boundary_annihilation.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The certified bare boundary-to-loop map is annihilated by the tube-visible sector-33 "
            "idempotent. Therefore the scalar Pi_33 tube-character coefficient of gamma_8 is zero "
            "for the unweighted, optical-weighted, and signed structural lifts."
        ),
        "interpretation": (
            "The sector-33 residual attachment is not recovered by the bare closed-loop relation-pair "
            "transport lambda_boundary. A nonzero recovery must use a richer height/coherence/action "
            "transport, not another D20 cycle enumeration or raw rebuild."
        ),
        "definition": {
            "pi33_tube_idempotent": (
                "Sum the two local closed-loop pre-idempotents named by sector 33: B+ local 12 and "
                "S+ local 6, reconstructed from the stored tube-center primitive-idempotent certificate."
            ),
            "pi33_tube_character": "chi_33^tube(x)=Trace_regular(L_{e_33 x}) / dim(Pi_33) over F_1000003.",
            "tested_boundary_lift": "lambda_boundary(r->a)=sum_{alpha:r->a, beta:a->r} alpha beta in Hom(r,r).",
        },
        "inputs": {
            "boundary_to_loop_report": {
                "path": rel(BOUNDARY_TO_LOOP_REPORT),
                "sha256": sha_file(BOUNDARY_TO_LOOP_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
            "core_a985": {
                "path": rel(CORE_A985),
                "sha256": sha_file(CORE_A985),
            },
            "relation_memberships": {
                "path": rel(RELATION_NPZ),
                "sha256": sha_file(RELATION_NPZ),
            },
            "t985_tensor": {
                "path": rel(TENSOR_NPZ),
                "sha256": sha_file(TENSOR_NPZ),
            },
            "d20_edges": {
                "path": rel(D20_EDGES_CSV),
                "sha256": sha_file(D20_EDGES_CSV),
            },
        },
        "derived": {
            "sector33_profile": {
                "sector": sector33.get("sector"),
                "block_dimension": sector33.get("block_dimension"),
                "active_objects": sector33.get("active_objects"),
                "q42_nonzero_count": sector33.get("q42_nonzero_count"),
                "q12_nonzero_count": sector33.get("q12_nonzero_count"),
                "spectral_signature": sector33.get("spectral_signature"),
            },
            "sector33_tube_idempotent": {
                "pieces": idempotent_pieces,
                "vector": vec_digest(idempotent, include_entries=True),
                "object_loop_coordinate_support": object_support,
                "identity_coefficients_signed": identity_coefficients_signed,
                "regular_trace": int((trace_coeff @ idempotent) % FIELD_PRIME),
            },
            "directed_pair_evaluations": pair_evaluations,
            "cycle8": {
                "cycle": cycle,
                "variants": cycle_variants,
            },
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Define and certify a height-coherent or action-return transport that is not the bare "
            "closed-loop relation-pair image, then test whether Pi_33 evaluates nontrivially on that refined lift."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector33_boundary_annihilation_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "reconstruct the sector-33 tube idempotent from stored local pre-idempotents",
            "verify the reconstructed idempotent matches the sector-33 support and identity profile",
            "verify the idempotent law e_33^2=e_33 in A985",
            "evaluate left and right Pi_33 action on all 30 directed object-pair boundary lifts",
            "evaluate unweighted, optical-weighted, and signed gamma_8 structural lifts",
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
