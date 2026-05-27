from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_typed_simple_object_registry"
STATUS = "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

SOURCE_RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
CORE_A985_JSON = ROOT / "data" / "core" / "a985.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_typed_simple_object_registry.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_typed_simple_object_registry.py"

OBJECT_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return sha_json(tmp)


def load_relation_seed(path: Path = SOURCE_RELATION_NPZ) -> dict[str, Any]:
    z = np.load(path, allow_pickle=False)
    return {
        "encoded_pairs": np.asarray(z["encoded_pairs"], dtype=np.int64),
        "offsets": np.asarray(z["offsets"], dtype=np.int64),
        "object_of_point": np.asarray(z["object_of_point"], dtype=np.int16),
        "reps": np.asarray(z["reps"], dtype=np.int32),
        "block_i": np.asarray(z["block_i"], dtype=np.int16),
        "block_j": np.asarray(z["block_j"], dtype=np.int16),
        "points": int(np.asarray(z["points"]).reshape(-1)[0]),
        "group_order": int(np.asarray(z["group_order"]).reshape(-1)[0]),
    }


def build_label_matrix(encoded_pairs: np.ndarray, offsets: np.ndarray, points: int) -> np.ndarray:
    relation_count = offsets.size - 1
    labels = np.full(points * points, -1, dtype=np.int32)
    for relation_id in range(relation_count):
        lo = int(offsets[relation_id])
        hi = int(offsets[relation_id + 1])
        labels[encoded_pairs[lo:hi]] = relation_id
    if np.any(labels < 0):
        raise ValueError("relation membership table does not cover every ordered pair")
    return labels.reshape(points, points)


def relation_count_matrix(source_target: np.ndarray) -> np.ndarray:
    matrix = np.zeros((len(OBJECT_LABELS), len(OBJECT_LABELS)), dtype=np.int64)
    for source, target in source_target:
        matrix[int(source), int(target)] += 1
    return matrix


def derive_transpose_and_identities(seed: dict[str, Any]) -> tuple[np.ndarray, list[dict[str, Any]]]:
    encoded_pairs = seed["encoded_pairs"]
    offsets = seed["offsets"]
    object_of_point = seed["object_of_point"]
    reps = seed["reps"]
    block_i = seed["block_i"]
    block_j = seed["block_j"]
    points = int(seed["points"])
    relation_count = offsets.size - 1
    labels = build_label_matrix(encoded_pairs, offsets, points)

    transpose = np.empty(relation_count, dtype=np.int32)
    for relation_id in range(relation_count):
        rep_x = int(reps[relation_id, 2])
        rep_y = int(reps[relation_id, 3])
        transpose[relation_id] = int(labels[rep_y, rep_x])

    identities: list[dict[str, Any]] = []
    point_ids = np.arange(points, dtype=np.int64)
    for object_id, label in enumerate(OBJECT_LABELS):
        points_in_object = point_ids[object_of_point == object_id]
        diagonal_labels = labels[points_in_object, points_in_object]
        unique = np.unique(diagonal_labels)
        if unique.size != 1:
            raise ValueError(f"object {object_id} has {unique.size} diagonal identity relations")
        relation_id = int(unique[0])
        identities.append(
            {
                "object_id": object_id,
                "object_label": label,
                "identity_relation": relation_id,
                "source_object_id": int(block_i[relation_id]),
                "target_object_id": int(block_j[relation_id]),
                "diagonal_point_count": int(points_in_object.size),
            }
        )
    return transpose, identities


def typed_segments_ok(seed: dict[str, Any]) -> bool:
    encoded_pairs = seed["encoded_pairs"]
    offsets = seed["offsets"]
    object_of_point = seed["object_of_point"]
    block_i = seed["block_i"]
    block_j = seed["block_j"]
    points = int(seed["points"])
    for relation_id in range(offsets.size - 1):
        lo = int(offsets[relation_id])
        hi = int(offsets[relation_id + 1])
        segment = encoded_pairs[lo:hi]
        xs = segment // points
        ys = segment % points
        if not np.all(object_of_point[xs] == block_i[relation_id]):
            return False
        if not np.all(object_of_point[ys] == block_j[relation_id]):
            return False
    return True


def build_payloads() -> dict[str, Any]:
    seed = load_relation_seed()
    core = load_json(CORE_A985_JSON)
    relations_block = core.get("blocks", {}).get("relations", {})
    finite_block = core.get("blocks", {}).get("finite_algebra", {})
    tube_blocks = core.get("blocks", {}).get("tube_algebra_lift", {}).get("blocks", [])

    relation_count = int(seed["offsets"].size - 1)
    source_target = np.column_stack([seed["block_i"], seed["block_j"]]).astype(np.int16)
    transpose, identity_orbitals = derive_transpose_and_identities(seed)
    matrix = relation_count_matrix(source_target)
    object_sizes = np.bincount(seed["object_of_point"], minlength=len(OBJECT_LABELS)).astype(np.int64)
    relation_sizes = (seed["offsets"][1:] - seed["offsets"][:-1]).astype(np.int64)

    expected_identity_relations = [
        int(block.get("identity_relation"))
        for block in sorted(tube_blocks, key=lambda row: int(row.get("object", -1)))
        if isinstance(block, dict) and "identity_relation" in block
    ]
    actual_identity_relations = [row["identity_relation"] for row in identity_orbitals]

    objects = {
        "schema": "c985.typed_simple_object_registry.objects@1",
        "object_count": len(OBJECT_LABELS),
        "objects": [
            {
                "object_id": object_id,
                "label": label,
                "point_count": int(object_sizes[object_id]),
                "outgoing_relation_count": int(matrix[object_id, :].sum()),
                "incoming_relation_count": int(matrix[:, object_id].sum()),
                "identity_relation": actual_identity_relations[object_id],
            }
            for object_id, label in enumerate(OBJECT_LABELS)
        ],
        "object_pair_relation_matrix": matrix.astype(int).tolist(),
    }

    orbitals = {
        "schema": "c985.typed_simple_object_registry.orbitals@1",
        "relation_count": relation_count,
        "orbitals": [
            {
                "relation_id": relation_id,
                "source_object_id": int(source_target[relation_id, 0]),
                "source_object_label": OBJECT_LABELS[int(source_target[relation_id, 0])],
                "target_object_id": int(source_target[relation_id, 1]),
                "target_object_label": OBJECT_LABELS[int(source_target[relation_id, 1])],
                "representative_pair": [
                    int(seed["reps"][relation_id, 2]),
                    int(seed["reps"][relation_id, 3]),
                ],
                "relation_size": int(relation_sizes[relation_id]),
                "transpose_relation": int(transpose[relation_id]),
            }
            for relation_id in range(relation_count)
        ],
    }

    semisimple = {
        "schema": "c985.semisimple_category_certificate@1",
        "status": "C985_SEMISIMPLE_SKELETON_CERTIFIED_MONOIDAL_COHERENCE_OPEN",
        "simple_count": relation_count,
        "object_count": len(OBJECT_LABELS),
        "hom_rule": "Hom(X_alpha, X_beta) is C if alpha == beta and 0 otherwise.",
        "finite_direct_sums_by_construction": True,
        "idempotents_split_by_skeletal_semisimple_construction": True,
        "source_target_matrix": matrix.astype(int).tolist(),
        "does_not_certify": [
            "associator/F-symbols",
            "pentagon coherence",
            "unit triangle coherence",
            "duality evaluation and coevaluation maps",
            "zig-zag identities",
            "full finite semisimple multi-fusion category status",
        ],
    }

    checks = {
        "source_relation_npz_exists": SOURCE_RELATION_NPZ.exists(),
        "core_a985_certificate_exists": CORE_A985_JSON.exists(),
        "point_count_is_2576": int(seed["points"]) == 2576,
        "group_order_is_9216": int(seed["group_order"]) == 9216,
        "relation_count_is_985": relation_count == 985,
        "ordered_pair_partition_covers_points_squared": int(seed["encoded_pairs"].size)
        == int(seed["points"]) * int(seed["points"]),
        "offset_count_is_relation_count_plus_one": int(seed["offsets"].size) == relation_count + 1,
        "object_count_is_6": int(object_sizes.size) == 6,
        "object_sizes_match_core": object_sizes.astype(int).tolist()
        == [int(x) for x in relations_block.get("object_sizes", [])],
        "relation_count_matrix_matches_core_relations": matrix.astype(int).tolist()
        == relations_block.get("relation_count_matrix"),
        "relation_count_matrix_matches_finite_algebra": matrix.astype(int).tolist()
        == finite_block.get("object_pair_relation_matrix"),
        "relation_count_matrix_sums_to_985": int(matrix.sum()) == 985,
        "segments_are_source_target_typed": typed_segments_ok(seed),
        "transpose_is_involution": bool(np.array_equal(transpose[transpose], np.arange(relation_count))),
        "transpose_flips_source_target": bool(
            np.array_equal(source_target[transpose, 0], source_target[:, 1])
            and np.array_equal(source_target[transpose, 1], source_target[:, 0])
        ),
        "identity_relation_count_is_6": len(actual_identity_relations) == 6,
        "identity_relations_match_closed_loop_units": actual_identity_relations
        == expected_identity_relations,
        "semisimple_skeleton_declares_coherence_open": "associator/F-symbols"
        in semisimple["does_not_certify"],
    }

    witness = {
        "points": int(seed["points"]),
        "group_order": int(seed["group_order"]),
        "relation_count": relation_count,
        "object_labels": OBJECT_LABELS,
        "object_sizes": object_sizes.astype(int).tolist(),
        "object_pair_relation_matrix": matrix.astype(int).tolist(),
        "identity_relations": actual_identity_relations,
        "relation_size_min": int(relation_sizes.min()),
        "relation_size_max": int(relation_sizes.max()),
        "relation_size_total": int(relation_sizes.sum()),
        "source_target_sha256": sha_array(source_target),
        "transpose_sha256": sha_array(transpose),
        "object_of_point_sha256": sha_array(seed["object_of_point"]),
    }

    report = {
        "schema": "c985.proof_obligation.typed_simple_object_registry@1",
        "status": STATUS if all(checks.values()) else "C985_TYPED_SIMPLE_OBJECT_REGISTRY_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The 985 A985 relations are typed as simple C985 generators over the six H6 "
            "object sectors, with source/target registry, transpose involution, and six "
            "identity orbitals certified from the relation-membership table."
        ),
        "stage_protocol": {
            "draft": "derive the C985 simple-object typing from the existing A985 relation membership table",
            "witness": "materialize objects, orbitals, source_target.npy, transpose.npy, identity orbitals, and semisimple skeleton certificate",
            "coherence": "check typed segments, matrix counts, transpose involution, identity orbitals, and formal semisimplicity boundary",
            "closure": "certify the typed registry while leaving monoidal coherence open",
            "emit": "emit the first C985 proof-obligation artifacts and next target",
        },
        "inputs": {
            "relation_memberships": input_entry(SOURCE_RELATION_NPZ),
            "core_a985": input_entry(
                CORE_A985_JSON,
                {
                    "status": core.get("status"),
                    "certificate_sha256": core.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "objects": relpath(OUT_DIR / "objects.json"),
            "orbitals": relpath(OUT_DIR / "orbitals.json"),
            "source_target": relpath(OUT_DIR / "source_target.npy"),
            "transpose": relpath(OUT_DIR / "transpose.npy"),
            "identity_orbitals": relpath(OUT_DIR / "identity_orbitals.json"),
            "semisimple_category_certificate": relpath(OUT_DIR / "semisimple_category_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "typed simple-object registry for 985 C985 simple generators",
                "six H6 object sectors and their identity orbitals",
                "orbital transpose involution as the expected dual-object map",
                "formal semisimple skeletal C-linear category before tensor coherence",
            ],
            "does_not_certify": semisimple["does_not_certify"],
        },
        "next_highest_yield_item": (
            "Construct the fusion multiplicity spaces from incidence-chain bases and "
            "verify that their dimensions match the A985 tensor coefficients with "
            "source/target typing failures equal to zero."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.typed_simple_object_registry_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "derive s,t:{1,...,985}->H6 from relation_memberships.npz block_i/block_j",
            "check object-pair relation counts against data/core/a985.json",
            "check every relation segment is contained in the declared source/target object product",
            "derive transpose.npy from reversed representative pairs and check involution",
            "derive six identity orbitals from diagonal pairs and check against closed-loop unit relations",
            "record formal semisimple skeletal category while keeping monoidal coherence open",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "objects": objects,
        "orbitals": orbitals,
        "source_target": source_target,
        "transpose": transpose,
        "identity_orbitals": {
            "schema": "c985.typed_simple_object_registry.identity_orbitals@1",
            "identity_orbitals": identity_orbitals,
        },
        "semisimple_category_certificate": semisimple,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
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
    write_json(OUT_DIR / "objects.json", payloads["objects"])
    write_json(OUT_DIR / "orbitals.json", payloads["orbitals"])
    np.save(OUT_DIR / "source_target.npy", payloads["source_target"])
    np.save(OUT_DIR / "transpose.npy", payloads["transpose"])
    write_json(OUT_DIR / "identity_orbitals.json", payloads["identity_orbitals"])
    write_json(
        OUT_DIR / "semisimple_category_certificate.json",
        payloads["semisimple_category_certificate"],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "relation_count": payloads["report"]["witness"]["relation_count"],
                "identity_relations": payloads["report"]["witness"]["identity_relations"],
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
